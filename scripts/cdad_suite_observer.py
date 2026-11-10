"""Observador de fases y operaciones para el `close` de ``scripts/cdad-suite.py`` (017-001 T1+T2).

Plugin pytest minimo, cargado solo por el hijo que `close` invoca mediante
``-p cdad_suite_observer``: registra cada informe de fase realmente emitido
(``setup``/``call``/``teardown``) con su nodeid, duracion observada y
resultado, y vuelca los registros a JSON al final de la sesion.

En T2 ademas conecta su sumidero a la costura
``tests/suite_operation_markers.py`` (modulo importable
``suite_operation_markers``): cuando el hijo puede importarla, cada marca de
comienzo y fin queda recolectada con su operacion, identidad de intervalo,
padre, proceso, contexto de test o compartido, rama y terminacion, mas los
tiempos monotonicos tomados por este observador (el helper no mide
duraciones). Sin el sumidero del `close` (``CDAD_SUITE_PHASE_SINK`` ausente)
el plugin no registra nada: cargarlo fuera de un `close` instrumentado es
inocuo, y sin la costura importable las marcas del hijo siguen neutras.

Solo observa: no altera seleccion, resultado, orden ni ejecucion. Si la
captura falla, lo declara por stderr y deja el sumidero ausente o parcial;
`close` diagnostica entonces la medicion como incompleta sin sustituir el rc
contractual. Una fase no emitida nunca aparece: ausente sigue siendo ausente,
no una fila de duracion cero.
"""

from __future__ import annotations

import json
import os
import sys
import time
from contextlib import nullcontext

try:
    import pytest
except ImportError:  # pragma: no cover: el plugin solo carga bajo pytest
    pytest = None

# Sumidero que `close` fija en el entorno del hijo. Sin el, el plugin no
# registra nada: cargarlo fuera de un `close` instrumentado es inocuo.
SINK_ENV = "CDAD_SUITE_PHASE_SINK"

_STARTED_AT = time.monotonic()
_PHASES: list = []
# Errores de captura del propio observador (p. ej. un informe que no se pudo
# serializar). Se conservan en el volcado para que `close` declare la
# medicion incompleta en vez de presentar una captura parcial como completa
# (017-001 review-T1 H1, INV-6). Medir nunca rompe la corrida medida.
_CAPTURE_ERRORS: list = []

# Costura de marcas (017-001 T2): se resuelve de forma perezosa porque al
# inicio de la sesion el directorio del hijo puede no estar todavia en
# sys.path; tras la coleccion si lo esta. Sin ella, las marcas del hijo
# siguen neutras y solo se conservan fases. En el repo coexisten la copia
# bare (``suite_operation_markers``) y la calificada
# (``tests.suite_operation_markers``) como instancias distintas en
# sys.modules: el sumidero se adjunta a TODAS para que ninguna marca se
# pierda por la ambiguedad (017-001 T2 P6).
_markers_module = None
_markers_modules: list = []
_ops_sink = None
# Intervalos sin su par begin/end, eventos duplicados o fallos al conectar el
# sumidero: `close` los convierte en medicion incompleta diagnosticada.
_OP_ERRORS: list = []


def _discover_markers() -> list:
    """Todas las instancias importables del helper, sin duplicar objetos."""
    found: list = []
    for name in ("suite_operation_markers", "tests.suite_operation_markers"):
        try:
            __import__(name)
        except ImportError:
            continue
        mod = sys.modules.get(name)
        if mod is None:
            continue
        if any(existing is mod for existing in found):
            continue
        found.append(mod)
    return found


def _ensure_markers():
    """Primera instancia importable, o ``None`` (compatibilidad)."""
    global _markers_module
    if _markers_module is not None:
        return _markers_module
    found = _discover_markers()
    if not found:
        return None
    _markers_module = found[0]
    return _markers_module


class _TimedSink(list):
    """Sumidero que estampa el reloj monotonico en cada evento recibido."""

    def __init__(self):
        super().__init__()
        self.times: list = []

    def append(self, record):
        self.times.append(time.monotonic())
        super().append(record)


def _ensure_ops_attached() -> bool:
    """Conecta el sumidero a TODAS las instancias si hay medicion en curso.

    Usa un unico sumidero compartido: cada marca emitida por cualquier
    instancia cae una vez en la misma lista. Reintenta en cada fase porque
    una instancia puede volverse importable tras la coleccion; las ya
    conectadas no se reconectan.
    """
    global _ops_sink, _markers_module, _markers_modules
    if not os.environ.get(SINK_ENV):
        return False
    if _ops_sink is None:
        _ops_sink = _TimedSink()
    found = _discover_markers()
    if not found:
        return False
    if _markers_module is None:
        _markers_module = found[0]
    attached_any = bool(_markers_modules)
    for markers in found:
        if any(existing is markers for existing in _markers_modules):
            continue
        try:
            markers.attach(_ops_sink)
        except Exception as exc:  # medir nunca rompe la corrida medida
            _OP_ERRORS.append(
                f"no se pudo conectar el sumidero de operaciones: {exc}")
            print(f"cdad_suite_observer: {_OP_ERRORS[-1]}", file=sys.stderr)
            continue
        _markers_modules.append(markers)
        attached_any = True
    if not attached_any:
        return False
    return True


def _phase_context(nodeid, phase):
    """Contexto ambiente para las marcas emitidas durante una fase de test.

    Lo fija en TODAS las instancias conectadas: cada instancia guarda sus
    ContextVars propias y el hijo puede emitir por cualquiera de ellas.
    """
    from contextlib import ExitStack
    modules = list(_markers_modules)
    if not modules and _markers_module is not None:
        modules = [_markers_module]
    if not modules or _ops_sink is None:
        return nullcontext()
    stack = ExitStack()
    entered = False
    for markers in modules:
        try:
            stack.enter_context(markers.use_context(
                nodeid=nodeid, phase=phase, owner_scope="test"))
            entered = True
        except Exception:  # idem: medir no cambia la ejecucion medida
            continue
    if not entered:
        stack.close()
        return nullcontext()
    return stack


if pytest is not None:  # pragma: no branch

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(item):
        _ensure_ops_attached()
        with _phase_context(getattr(item, "nodeid", None), "setup"):
            yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(item):
        _ensure_ops_attached()
        with _phase_context(getattr(item, "nodeid", None), "call"):
            yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(item):
        _ensure_ops_attached()
        with _phase_context(getattr(item, "nodeid", None), "teardown"):
            yield


def pytest_sessionstart(session):
    """Intenta conectar el sumidero; si la costura aun no importa, los hooks
    de fase lo reintentan tras la coleccion."""
    _ensure_ops_attached()


def pytest_runtest_logreport(report):
    """Conserva cada fase realmente emitida, tal como pytest la informa."""
    if not os.environ.get(SINK_ENV):
        return
    try:
        _PHASES.append({
            "nodeid": str(report.nodeid),
            "when": str(report.when),
            "duration_s": float(report.duration),
            "outcome": str(report.outcome),
        })
    except Exception as exc:  # la medicion nunca rompe la corrida medida
        _CAPTURE_ERRORS.append(str(exc))
        print(f"cdad_suite_observer: no se pudo registrar una fase: {exc}",
              file=sys.stderr)


def _build_operations() -> list:
    """Empareja begin/end por intervalo con duraciones monotonicas.

    El anidamiento lo fija el helper (``parent_id``); aqui solo se conserva:
    el tiempo inclusivo de un padre no se suma con sus hijos, cada intervalo
    aporta su propia pared begin/end. Un intervalo sin su par no es una
    operacion: queda como error de captura para que `close` diagnostique la
    medicion incompleta en vez de presentar una captura parcial como valida.
    """
    events = list(_ops_sink) if _ops_sink is not None else []
    stamps = list(_ops_sink.times) if _ops_sink is not None else []
    slots: dict = {}
    order: list = []
    seen: set = set()
    for event, stamp in zip(events, stamps):
        if not isinstance(event, dict):
            _OP_ERRORS.append(
                f"evento de operacion no dict: {type(event).__name__}")
            continue
        try:
            fingerprint = json.dumps(event, sort_keys=True, default=str)
        except Exception:
            fingerprint = repr(event)
        if fingerprint in seen:
            # Misma marca llegada por dos canales (bare + paquete
            # comparten un unico sumidero o el hijo emite por ambas
            # instancias): se conserva una sola vez, sin error.
            continue
        seen.add(fingerprint)
        interval = event.get("interval_id")
        kind = event.get("event")
        slot = slots.get(interval)
        if slot is None:
            slot = {}
            slots[interval] = slot
            order.append(interval)
        if kind == "begin" and "begin" not in slot:
            slot["begin"] = (event, stamp)
        elif kind == "end" and "end" not in slot:
            slot["end"] = (event, stamp)
        else:
            _OP_ERRORS.append(
                f"evento duplicado o desconocido para intervalo {interval!r}: "
                f"{kind!r}")
    operations = []
    for interval in order:
        slot = slots[interval]
        if "begin" not in slot or "end" not in slot:
            _OP_ERRORS.append(f"intervalo sin par begin/end: {interval!r}")
            continue
        (begin, started), (end, finished) = slot["begin"], slot["end"]
        if finished < started:  # el reloj es monotonico; no forzar causalidad
            finished = started
        operations.append({
            "operation": begin.get("operation"),
            "interval_id": begin.get("interval_id"),
            "parent_id": begin.get("parent_id"),
            "process_id": begin.get("process_id"),
            "nodeid": begin.get("nodeid"),
            "phase": begin.get("phase"),
            "owner_scope": begin.get("owner_scope"),
            "branch": begin.get("branch"),
            "started": started,
            "finished": finished,
            "duration_s": finished - started,
            "termination": end.get("termination"),
        })
    return operations


def pytest_sessionfinish(session, exitstatus):
    """Vuelca las fases y operaciones observadas; el volcado es atomico o no
    ocurre. El sumidero de marcas se retira siempre para no fugar estado."""
    global _ops_sink, _markers_modules
    sink = os.environ.get(SINK_ENV)
    operations = _build_operations()
    modules = list(_markers_modules)
    if not modules and _markers_module is not None:
        modules = [_markers_module]
    if modules and _ops_sink is not None:
        for markers in modules:
            try:
                markers.detach()
            except Exception as exc:  # idem: medir no cambia lo medido
                _OP_ERRORS.append(f"no se pudo retirar el sumidero: {exc}")
    _markers_modules = []
    _ops_sink = None
    if not sink:
        return
    payload = {
        "schema_version": 1,
        "pytest_exitstatus": exitstatus,
        "elapsed_s": time.monotonic() - _STARTED_AT,
        "phases": _PHASES,
        "capture_errors": list(_CAPTURE_ERRORS),
        "operations": operations,
        "operation_errors": list(_OP_ERRORS),
    }
    try:
        temporary = sink + ".tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        os.replace(temporary, sink)
    except Exception as exc:  # idem: medir no cambia el resultado medido
        print(f"cdad_suite_observer: no se pudo volcar {sink}: {exc}",
              file=sys.stderr)
