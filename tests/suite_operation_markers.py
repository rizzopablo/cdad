"""017-001 T2: costura neutra de marcas de operaciones (spec §4.2, mapping §2).

Propuesta de interfaz nueva, no descripción de una API existente. El helper
emite eventos síncronos de comienzo y fin por un canal de logging dedicado;
el observador (implementer, fuera de tests/) toma tiempos monotónicos y
agrega identidad de intervalo, contexto y anidamiento.

Sin observador activo no escribe evidencia ni modifica la ejecución: el
cuerpo se ejecuta intacto y las excepciones se propagan; la salida
excepcional cierra el intervalo mediante ``finally`` con terminación de
error.

Pueden coexistir varios sumideros simultáneos (por ejemplo, el observador
del close y el ``observed()`` de un verificador): ``attach`` agrega sin
desplazar, ``detach`` retira el propio o el último, ``is_active`` indica si
hay alguno, ``observed`` agrega el suyo y lo retira al salir, y todos los
sumideros reciben los mismos eventos.

Campos por evento (mapping §2 + mechanism explicit-synchronous-markers):
operation, interval_id, parent_id, process_id, nodeid, phase, owner_scope,
branch, event (begin/end) y termination (solo end: ok/error). El reloj
pertenece al observador; el helper no mide duraciones.

Sin umbrales temporales como oráculo (spec §4.2; convención 11).
"""

import contextvars
import itertools
import logging
import os
import uuid
from contextlib import contextmanager

CHANNEL = "cdad.suite.operations"

logger = logging.getLogger(CHANNEL)

_counter = itertools.count(1)

_sinks: list = []

_current_interval: contextvars.ContextVar = contextvars.ContextVar(
    "suite_operation_interval", default=None)
_current_nodeid: contextvars.ContextVar = contextvars.ContextVar(
    "suite_operation_nodeid", default=None)
_current_phase: contextvars.ContextVar = contextvars.ContextVar(
    "suite_operation_phase", default=None)
_current_owner_scope: contextvars.ContextVar = contextvars.ContextVar(
    "suite_operation_owner_scope", default=None)


def is_active() -> bool:
    """Hay al menos un observador activo recibiendo eventos."""
    return bool(_sinks)


def attach(sink: list) -> None:
    """Conecta un sumidero de eventos (el observador). Solo tests/.

    Agrega sin desplazar a los ya conectados; el mismo sumidero no se
    duplica.
    """
    if not any(current is sink for current in _sinks):
        _sinks.append(sink)


def detach(sink: list | None = None) -> None:
    """Desconecta un observador.

    Con el sumidero propio lo retira a él; sin argumento retira el último.
    Sin sumideros no hace nada: las marcas vuelven a ser neutras.
    """
    if sink is None:
        if _sinks:
            _sinks.pop()
        return
    _sinks[:] = [current for current in _sinks if current is not sink]


@contextmanager
def observed(sink=None):
    """Activa un observador en memoria y lo entrega; al salir lo retira.

    Agrega su sumidero sin desplazar a los ya conectados y al salir retira
    solo el propio.
    """
    if sink is None:
        sink = []
    attach(sink)
    try:
        yield sink
    finally:
        detach(sink)


@contextmanager
def use_context(*, nodeid=None, phase=None, owner_scope=None):
    """Fija el contexto ambiente (test o compartido) para las marcas."""
    tokens = (
        _current_nodeid.set(nodeid),
        _current_phase.set(phase),
        _current_owner_scope.set(owner_scope),
    )
    try:
        yield
    finally:
        _current_nodeid.reset(tokens[0])
        _current_phase.reset(tokens[1])
        _current_owner_scope.reset(tokens[2])


def _new_interval_id() -> str:
    # Identidad intento-proceso-ocurrencia: el intento lo agrega el
    # observador; aquí proceso + ocurrencia + salto único.
    return "%d-%d-%s" % (os.getpid(), next(_counter), uuid.uuid4().hex[:8])


@contextmanager
def operation(operation_id, *, nodeid=None, phase=None,
              owner_scope=None, branch=None):
    """Rodea una operación con marcas de comienzo y fin.

    Sin observador activo el cuerpo se ejecuta sin emitir nada. Con
    observador se emiten dos eventos (begin/end) con identidad de
    intervalo, padre, proceso, contexto, rama y terminación. La salida
    excepcional cierra el intervalo con termination="error" y propaga
    la excepción sin sustituirla.
    """
    interval_id = _new_interval_id()
    parent_id = _current_interval.get()
    resolved = {
        "nodeid": nodeid if nodeid is not None else _current_nodeid.get(),
        "phase": phase if phase is not None else _current_phase.get(),
        "owner_scope": (owner_scope if owner_scope is not None
                        else _current_owner_scope.get()),
    }
    if not is_active():
        token = _current_interval.set(interval_id)
        try:
            yield interval_id
        finally:
            _current_interval.reset(token)
        return
    begin = {
        "event": "begin",
        "operation": operation_id,
        "interval_id": interval_id,
        "parent_id": parent_id,
        "process_id": os.getpid(),
        "nodeid": resolved["nodeid"],
        "phase": resolved["phase"],
        "owner_scope": resolved["owner_scope"],
        "branch": branch,
    }
    for target in list(_sinks):
        target.append(begin)
    logger.debug("suite-operation-begin %r", begin)
    token = _current_interval.set(interval_id)
    try:
        yield interval_id
    except BaseException:
        end = dict(begin, event="end", termination="error")
        for target in list(_sinks):
            target.append(end)
        logger.debug("suite-operation-end %r", end)
        raise
    else:
        end = dict(begin, event="end", termination="ok")
        for target in list(_sinks):
            target.append(end)
        logger.debug("suite-operation-end %r", end)
    finally:
        _current_interval.reset(token)
