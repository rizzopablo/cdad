"""017-001 T2 RED (corrección D1/D2): marcas de operaciones y diagnóstico de captura (spec §4.2).

Oráculo derivado del contrato aprobado ``docs/specs/017-001-suite-performance/
spec.md`` §4.2 (PC-1 parte operaciones, INV-1/INV-2/INV-6/INV-8) y del esquema de
``performance/operation-scope.json`` (mechanism explicit-synchronous-markers),
con el formato de ``profile.json`` ya publicado por T1. No lee
implementación: ``close`` se usa como caja negra por CLI sobre repos
sintéticos (patrón de ``test_017_001_suite_profile.py``) y la costura bajo
prueba vive en ``tests/suite_operation_markers.py``. Ninguna aserción importa
``scripts/cdad_suite_observer.py`` ni su API interna.

Corrección D1 (camino de integración real y satisfacible): los cierres que
exigen operaciones corren sobre un hijo sintético que emite marcas con el
helper (copiado al workspace sintético); un hijo que nunca importa el helper
ni adjunta un sumidero no puede producir operaciones por construcción y su
oráculo sería insatisfacible. P3 conserva un cierre de control que solo
acredita la viabilidad del camino (rc intacto y forma de operations), sin
exigir presencia ni ausencia: la neutralidad es propiedad del helper y se
verifica en proceso.

Corrección D2-rev (tras green-T2-blocked.md, spec §4.4): la captura
faltante solo exige incomplete cuando el alcance aplicado declara un
recorrido comprometido cuya seleccion incluye el nodeid ejecutado y el
perfil capturo cero operaciones (status incomplete con diagnosis no
vacía; la lista puede estar vacía). Un recorrido no ejercitado se
distingue de un fallo de captura: con el alcance por defecto y una
seleccion que no ejercita ningun recorrido comprometido, el perfil queda
complete (protecciones T1 conservadas). Para que (A) sea comprobable sin
acoplarse a señales del arnes, el oraculo construye en su workspace un
alcance sintetico explicito que declara el nodeid sintetico como parte
de un recorrido comprometido y lo pasa por el argumento declarado
--operation-scope (nuevo, con default al registro del repositorio del
CLI). El contraste con marcas capturadas y alcance satisfecho queda
complete sin diagnosis.

Sin umbrales temporales como oráculo (spec §4.2; convención 11): solo
presencia, identidad y diagnóstico; nunca techos ni igualdades de duración.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.suite_operation_markers import (
    attach,
    detach,
    is_active,
    observed,
    operation,
    use_context,
)

CLI = Path(__file__).resolve().parents[1] / "scripts" / "cdad-suite.py"
SCOPE_PATH = (Path(__file__).resolve().parents[1] / "docs" / "specs"
              / "017-001-suite-performance" / "performance"
              / "operation-scope.json")
HELPER_SRC = Path(__file__).resolve().parent / "suite_operation_markers.py"

SAMPLE = (
    "def test_pass(): pass\n"
)

# Hijo que emite marcas con el helper (D1): el helper se copia al workspace
# sintético para que el hijo lo importe como módulo local; el observador del
# hijo (implementer) puede así conectar su sumidero sobre la misma copia.
EMITTING_SAMPLE = (
    "from suite_operation_markers import operation\n"
    "def test_pass():\n"
    "    with operation(\"u4.lookup\", branch=\"cold\"):\n"
    "        with operation(\"u4.copy\", branch=\"cold\"):\n"
    "            assert True\n"
    "        with operation(\"u4.initial-generate\", branch=\"cold\"):\n"
    "            assert True\n"
)

# Hijo que emite una marca y falla dentro de ella (P2): la excepción
# contractual debe propagarse (rc != 0) y el intervalo debe quedar capturado.
FAILING_SAMPLE = (
    "from suite_operation_markers import operation\n"
    "def test_boom():\n"
    "    with operation(\"recovery.initial-prepare\", branch=\"cold\"):\n"
    "        assert False, 'boom-contractual'\n"
)

# Hijo que usa el helper sin observador (P3): el cuerpo se ejecuta intacto y
# no se adjunta ningún sumidero en el hijo; el cierre solo acredita que el
# camino de integración es viable (colección limpia, rc intacto).
NEUTRAL_SAMPLE = (
    "from suite_operation_markers import operation\n"
    "def test_pass():\n"
    "    with operation(\"u1.lookup\", branch=\"cold\"):\n"
    "        assert 40 + 2 == 42\n"
)

BEGIN_KEYS = {"event", "operation", "interval_id", "parent_id", "process_id",
              "nodeid", "phase", "owner_scope", "branch"}


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    assert CLI.is_file(), "017-001 T2: el CLI canonico scripts/cdad-suite.py no existe"
    assert SCOPE_PATH.is_file(), "017-001 T2: falta performance/operation-scope.json"
    detach()
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.invalid"],
                   check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    (tmp_path / "test_sample.py").write_text(SAMPLE, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "test_sample.py"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "fixture"], check=True)
    (tmp_path / "evidence").mkdir()
    yield tmp_path
    detach()


def install_helper(workspace):
    """Copia el helper al workspace sintético (D1): sin esta copia el hijo no
    puede importar las marcas y el camino de integración es insatisfacible."""
    assert HELPER_SRC.is_file(), (
        "017-001 T2: falta tests/suite_operation_markers.py en el checkout; "
        "sin el helper no hay marcas que el hijo pueda emitir")
    shutil.copy(HELPER_SRC, workspace / "suite_operation_markers.py")


def write_sample(workspace, text):
    (workspace / "test_sample.py").write_text(text, encoding="utf-8")


def run_close(workspace, selection, label, timeout=180, operation_scope=None):
    nodeids = workspace / (label + ".txt")
    nodeids.write_text("\n".join("test_sample.py::" + name for name in selection) + "\n",
                       encoding="utf-8")
    cmd = [sys.executable, str(CLI), "close", "--evidence-root", str(workspace / "evidence"),
           "--nodeids", str(nodeids)]
    if operation_scope is not None:
        # Alcance sintetico explicito (nuevo, con default al registro del
        # repositorio del CLI): sin este argumento el oraculo no puede
        # distinguir recorrido no ejercitado de fallo de captura (spec §4.4).
        cmd += ["--operation-scope", str(operation_scope)]
    process = subprocess.Popen(
        cmd,
        cwd=workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(timeout=timeout)
    return process.returncode, out, err


def write_synthetic_scope(workspace, nodeids, label="synthetic-scope"):
    """Alcance sintetico explicito: declara el nodeid sintetico como parte
    de un recorrido comprometido (spec §4.4: solo un recorrido ejercitado
    que debia emitir puede exigir incomplete ante captura cero)."""
    path = workspace / (label + ".json")
    scope = {
        "schema_version": 1,
        "status": "synthetic",
        "feature_id": "017-001-suite-performance",
        "mechanisms": {
            "explicit-synchronous-markers": {
                "transport": "dedicated-logging-channel",
                "fields": ["operation", "interval_id", "parent_id",
                           "process_id", "nodeid", "phase", "owner_scope",
                           "branch"],
            }
        },
        "selections": {
            "C-SYNTH": {
                "existing": False,
                "proposed_verifier": True,
                "fresh_process": True,
                "nodeids": list(nodeids),
            }
        },
        "families": [
            {
                "family": "synthetic-committed-preparation",
                "selection": "C-SYNTH",
                "state": "comprometida",
                "classification": "preparacion",
                "context": "test-call",
                "operations": [
                    {"id": "synthetic.prepare", "expected": 1}
                ],
            }
        ],
    }
    path.write_text(json.dumps(scope, indent=2), encoding="utf-8")
    return path


def attempts(workspace):
    return sorted(p for p in (workspace / "evidence").iterdir() if p.is_dir())


def only_attempt(workspace):
    found = attempts(workspace)
    assert len(found) == 1, (
        "017-001 T2: un close debe reservar exactamente un intento; hay %d" % len(found))
    return found[0]


def profile_data(attempt):
    path = attempt / "profile.json"
    assert path.is_file(), (
        "017-001 T2 (PC-1 parte operaciones): el intento no conserva profile.json; "
        "sin este artefacto el responsable no puede recuperar operaciones ni "
        "diagnóstico de captura")
    return json.loads(path.read_text(encoding="utf-8"))


def scope_data():
    return json.loads(SCOPE_PATH.read_text(encoding="utf-8"))


def scope_requires_operations(scope):
    mechanisms = scope.get("mechanisms", {})
    marker = mechanisms.get("explicit-synchronous-markers", {})
    assert marker.get("transport") == "dedicated-logging-channel", (
        "017-001 T2: el alcance no fija el canal dedicado de marcas")
    assert "operation" in marker.get("fields", []), (
        "017-001 T2: el alcance no exige el campo operation")
    committed = [f.get("family") for f in scope.get("families", [])
                 if f.get("state", "comprometida") == "comprometida"]
    assert committed, (
        "017-001 T2: el alcance no compromete ninguna familia de operaciones")
    return committed


def check_begin_contract(record):
    assert BEGIN_KEYS <= record.keys(), (
        "017-001 T2: evento sin identidad completa: %r" % record)
    assert record["event"] in {"begin", "end"}, (
        "017-001 T2: evento fuera de begin/end: %r" % record)
    assert record["process_id"] == os.getpid(), (
        "017-001 T2: process_id no es el proceso que emitió: %r" % record)
    assert isinstance(record["interval_id"], str) and record["interval_id"], (
        "017-001 T2: interval_id vacío: %r" % record)


# P1 — con observador, los eventos llegan con identidad, contexto de test o
# compartido y anidamiento padre-hijo. PC-1 (parte operaciones), INV-1, INV-8.
def test_active_observer_captures_intervals_with_identity_context_and_nesting(workspace):
    """Sin este test, el usuario calibra sobre intervalos sin identidad, sin
    contexto o sin anidamiento y atribuye preparación a quien no la causó."""
    with observed() as seen:
        assert is_active()
        with use_context(nodeid="test_sample.py::test_pass", phase="call",
                         owner_scope="test"):
            with operation("u4.lookup", branch="cold") as parent:
                with operation("u4.copy", branch="cold") as child:
                    assert child != parent
                with operation("u4.initial-generate", branch="cold"):
                    pass
        with use_context(nodeid=None, phase="setup", owner_scope="shared"):
            with operation("isolation.seed", branch="session"):
                pass
    begins = [r for r in seen if r["event"] == "begin"]
    ends = [r for r in seen if r["event"] == "end"]
    assert len(begins) == 4 and len(ends) == 4, (
        "017-001 T2 P1: con observador deben llegar 4 comienzos y 4 fines: %r" % seen)
    for record in seen:
        check_begin_contract(record)
    ids = [r["interval_id"] for r in begins]
    assert len(set(ids)) == 4, (
        "017-001 T2 P1: los intervalos no tienen identidad única: %r" % ids)
    by_op = {r["operation"]: r for r in begins}
    assert by_op["u4.copy"]["parent_id"] == by_op["u4.lookup"]["interval_id"], (
        "017-001 T2 P1: u4.copy no cuelga de u4.lookup: %r" % by_op)
    assert by_op["u4.lookup"]["parent_id"] is None, (
        "017-001 T2 P1: la raíz no tiene padre nulo: %r" % by_op["u4.lookup"])
    assert by_op["u4.lookup"]["nodeid"] == "test_sample.py::test_pass", (
        "017-001 T2 P1: se perdió el contexto de test: %r" % by_op["u4.lookup"])
    assert by_op["isolation.seed"]["owner_scope"] == "shared", (
        "017-001 T2 P1: la preparación compartida quedó adjudicada a un test: %r"
        % by_op["isolation.seed"])
    assert by_op["u4.lookup"]["branch"] == "cold", (
        "017-001 T2 P1: se perdió la rama fría: %r" % by_op["u4.lookup"])
    assert {r["termination"] for r in ends} == {"ok"}, (
        "017-001 T2 P1: el cierre limpio no terminó como ok: %r" % ends)

    # Integración (D1): el hijo emite marcas con el helper copiado; solo
    # entonces el perfil puede traer operations tras la implementación.
    install_helper(workspace)
    write_sample(workspace, EMITTING_SAMPLE)
    rc, _, _ = run_close(workspace, ["test_pass"], "ops-active")
    assert rc == 0, (
        "017-001 T2 P1: el hijo que emite marcas debe cerrar con rc 0; si no, "
        "se rompió el resultado contractual antes del oráculo")
    profile = profile_data(only_attempt(workspace))
    operations = profile.get("operations")
    assert isinstance(operations, list) and operations, (
        "017-001 T2 P1: el perfil no trae operaciones observadas; sin "
        "intervalos con identidad no hay calibración de preparación en call")
    scope_ref = (profile.get("operation_scope") or profile.get("operation_scope_ref")
                 or profile.get("scope_ref") or profile.get("scope"))
    assert scope_ref, (
        "017-001 T2 P1: el perfil no referencia el alcance de operaciones aplicado")


# P2 — la salida excepcional cierra el intervalo con terminación de error y
# propaga la excepción. PC-1 (parte operaciones), INV-2.
def test_exceptional_exit_closes_interval_with_error_termination(workspace):
    """Sin este test, una excepción deja un intervalo abierto que la
    atribución cuenta como tiempo válido o traga el fallo contractual."""
    with observed() as seen:
        with pytest.raises(ValueError, match="boom-contractual"):
            with operation("recovery.initial-prepare", branch="cold") as interval:
                raise ValueError("boom-contractual")
        assert interval
    assert len(seen) == 2, (
        "017-001 T2 P2: la salida excepcional debe emitir begin+end: %r" % seen)
    begin, end = seen
    check_begin_contract(begin)
    assert end["event"] == "end" and end["interval_id"] == begin["interval_id"], (
        "017-001 T2 P2: el fin no cierra el intervalo abierto: %r" % seen)
    assert end["termination"] == "error", (
        "017-001 T2 P2: el cierre por excepción no quedó como error: %r" % end)

    marker = ValueError("boom-contractual")
    try:
        with observed():
            with operation("recovery.initial-prepare"):
                raise marker
    except ValueError as caught:
        assert caught is marker, (
            "017-001 T2 P2: la marca sustituyó la excepción contractual")
    else:  # pragma: no cover
        raise AssertionError("017-001 T2 P2: la excepción contractual no se propagó")

    # Integración (D1): el hijo emite la marca y falla dentro de ella; el rc
    # contractual debe conservarse y el perfil debe traer la operación.
    install_helper(workspace)
    write_sample(workspace, FAILING_SAMPLE)
    rc, _, _ = run_close(workspace, ["test_boom"], "ops-exception")
    assert rc != 0, (
        "017-001 T2 P2: el hijo que falla dentro de la marca debe cerrar con "
        "rc != 0; si queda rc 0, el cierre tragó el fallo contractual")
    profile = profile_data(only_attempt(workspace))
    operations = profile.get("operations")
    assert isinstance(operations, list) and operations, (
        "017-001 T2 P2: el perfil no trae operaciones; sin captura no se puede "
        "exigir el cierre por excepción del intervalo")


# P3 — sin observador, el helper no altera resultados ni deja evidencia.
# PC-1 (parte operaciones), INV-2.
def test_without_observer_helper_is_neutral_and_leaves_no_evidence(workspace, tmp_path):
    """Sin este test, la instrumentación puede cambiar el resultado de un test
    o sembrar evidencia fantasma cuando nadie la pidió."""
    assert not is_active()
    with observed() as probe:
        pass
    assert probe == []
    sentinel = tmp_path / "no-evidence-dir"
    with operation("u1.lookup", branch="cold") as interval:
        assert interval
        result = 40 + 2
    assert result == 42, (
        "017-001 T2 P3: la marca alteró el cómputo del cuerpo")
    assert not sentinel.exists(), (
        "017-001 T2 P3: la marca creó evidencia sin observador")
    with pytest.raises(ValueError, match="boom-neutro"):
        with operation("u1.lookup"):
            raise ValueError("boom-neutro")

    # Control de integración (D1): el hijo usa el helper sin observador
    # propio; el cierre acredita que el camino es viable (colección limpia,
    # rc intacto, forma de operations) sin exigir presencia ni ausencia: tras
    # GREEN el observador de sesión captura lo emitido y antes no hay nada
    # que capturar, así que ambas direcciones serían insatisfacibles aquí.
    install_helper(workspace)
    write_sample(workspace, NEUTRAL_SAMPLE)
    rc, _, _ = run_close(workspace, ["test_pass"], "ops-neutral")
    assert rc == 0, (
        "017-001 T2 P3: el hijo que usa el helper sin observador debe cerrar "
        "con rc 0; si no, el camino de integración (copia + import) está roto, "
        "no la promesa")
    profile = profile_data(only_attempt(workspace))
    operations = profile.get("operations")
    assert isinstance(operations, list), (
        "017-001 T2 P3: profile.json no conserva la forma de operations como "
        "lista; sin esa forma no hay contraste que acredite la neutralidad")


# P4 — la captura faltante sobre un recorrido comprometido ejercitado se
# diagnostica como medición incompleta (spec §4.4): el alcance aplicado
# declara un recorrido comprometido cuya seleccion incluye el nodeid
# ejecutado y el perfil capturo cero operaciones → status incomplete con
# diagnosis no vacia. Un recorrido no ejercitado se distingue de un fallo
# de captura: con el alcance por defecto del repositorio y una seleccion
# que no ejercita ningun recorrido comprometido, el perfil queda complete
# (protecciones T1 conservadas). El contraste con marcas capturadas queda
# complete sin diagnosis.
# PC-1 (parte operaciones), INV-6, INV-8.
def test_missing_markers_capture_is_diagnosed_as_incomplete_measurement(workspace):
    """Sin este test, el usuario consume una medición sin operaciones sobre
    un recorrido comprometido ejercitado como si fuera completa y entra a
    la base sobre captura rota; y sin el alcance sintetico explicito, el
    oraculo no distingue recorrido no ejercitado de fallo de captura."""
    synthetic_nodeids = ["test_sample.py::test_pass"]
    synthetic_scope = write_synthetic_scope(workspace, synthetic_nodeids)

    scope = json.loads(synthetic_scope.read_text(encoding="utf-8"))
    committed = scope_requires_operations(scope)
    assert "synthetic-committed-preparation" in committed, (
        "017-001 T2 P4: el alcance sintetico debe declarar un recorrido "
        "comprometido que incluya el nodeid ejecutado: %r" % committed)
    selected = scope["selections"]["C-SYNTH"]["nodeids"]
    assert synthetic_nodeids[0] in selected, (
        "017-001 T2 P4: el alcance sintetico debe incluir el nodeid "
        "ejecutado como parte del recorrido comprometido: %r" % selected)

    # (A) Captura faltante sobre recorrido ejercitado: el hijo no emite
    # ninguna marca y el alcance aplicado (sintetico, via --operation-scope)
    # declara ese nodeid dentro de un recorrido comprometido → status
    # incomplete con diagnosis no vacía; la lista puede estar vacía.
    rc, _, _ = run_close(workspace, ["test_pass"], "ops-missing",
                         operation_scope=synthetic_scope)
    assert rc == 0, (
        "017-001 T2 P4: la selección limpia debe cerrar con rc 0; si no, se "
        "rompió el resultado contractual antes del oráculo")
    missing_attempt = only_attempt(workspace)
    profile = profile_data(missing_attempt)
    assert profile.get("status") == "incomplete", (
        "017-001 T2 P4: el alcance aplicado declara el recorrido "
        "comprometido %r sobre el nodeid ejecutado y el perfil capturó "
        "cero operaciones; la medición queda incomplete hasta recalibrar, "
        "nunca complete" % sorted(committed))
    assert isinstance(profile.get("diagnosis"), str) and profile["diagnosis"].strip(), (
        "017-001 T2 P4: la medición incomplete quedó sin diagnosis accionable; "
        "no distingue la falla de captura del resultado de pytest")
    operations = profile.get("operations")
    assert isinstance(operations, list), (
        "017-001 T2 P4: profile.json no conserva la forma de operations como "
        "lista aunque esté vacía")

    # (B) Contraste: el mismo hijo emitiendo marcas produce operations no
    # vacias y complete (mismo alcance sintetico, misma seleccion).
    install_helper(workspace)
    write_sample(workspace, EMITTING_SAMPLE)
    rc, _, _ = run_close(workspace, ["test_pass"], "ops-present",
                         operation_scope=synthetic_scope)
    assert rc == 0, (
        "017-001 T2 P4: el hijo que emite marcas debe cerrar con rc 0; si no, "
        "se rompió el resultado contractual antes del contraste")
    found = attempts(workspace)
    assert len(found) == 2, (
        "017-001 T2 P4: dos close deben reservar exactamente dos intentos; hay %d"
        % len(found))
    present_attempt = next(p for p in found if p != missing_attempt)
    contrast = profile_data(present_attempt)
    contrast_ops = contrast.get("operations")
    assert isinstance(contrast_ops, list) and contrast_ops, (
        "017-001 T2 P4: el hijo emitió marcas y el perfil no trae operaciones; "
        "sin intervalos no hay contraste complete que acreditar")
    assert contrast.get("status") == "complete", (
        "017-001 T2 P4: con marcas capturadas y alcance satisfecho la medición "
        "debe quedar complete, no %r" % contrast.get("status"))
    assert not contrast.get("diagnosis"), (
        "017-001 T2 P4: una medición completa no debe traer diagnóstico pendiente")


def write_synthetic_op_scope(workspace, executed_nodeids, label="synthetic-op-scope",
                             selection_name="C-OP-SYNTH", selection_nodeids=None,
                             include_family_selection=False,
                             include_op_selection=True):
    """Alcance sintetico con seleccion a nivel de operacion (hallazgo 2 del
    review-T2): la familia omite ``selection`` y la operacion declara la
    seleccion aplicable. ``selection_nodeids=None`` usa los nodeids
    ejecutados (recorrido ejercitado); otra lista modela una seleccion que
    no incluye el nodeid ejecutado (contraste: recorrido no ejercitado)."""
    if selection_nodeids is None:
        selection_nodeids = list(executed_nodeids)
    path = workspace / (label + ".json")
    family = {
        "family": "synthetic-op-selection",
        "state": "comprometida",
        "classification": "preparacion",
        "context": "test-call",
        "operations": [
            {"id": "synthetic.op-prepare", "expected": 1}
        ],
    }
    if include_family_selection:
        family["selection"] = selection_name
    if include_op_selection:
        family["operations"][0]["selection"] = selection_name
    scope = {
        "schema_version": 1,
        "status": "synthetic",
        "feature_id": "017-001-suite-performance",
        "mechanisms": {
            "explicit-synchronous-markers": {
                "transport": "dedicated-logging-channel",
                "fields": ["operation", "interval_id", "parent_id",
                           "process_id", "nodeid", "phase", "owner_scope",
                           "branch"],
            }
        },
        "selections": {
            selection_name: {
                "existing": False,
                "proposed_verifier": True,
                "fresh_process": True,
                "nodeids": list(selection_nodeids),
            }
        },
        "families": [family],
    }
    path.write_text(json.dumps(scope, indent=2), encoding="utf-8")
    return path


# P5 — la seleccion declarada a nivel de operacion tambien ejercita el
# recorrido comprometido (review-T2 hallazgo 2, spec §4.2 + §4.4): una
# familia sin seleccion cuya operacion declara una seleccion que incluye
# el nodeid ejecutado, con cero operaciones capturadas, queda status
# incomplete con diagnosis no vacia. El contraste se conserva: si la
# operacion no declara seleccion o la seleccion no incluye el nodeid
# ejecutado, el perfil sigue complete (protecciones T1 conservadas).
# PC-1 (parte operaciones), INV-6, INV-8.
def test_operation_level_selection_is_diagnosed_as_incomplete_measurement(workspace):
    """Sin este test, el usuario consume una medicion sin operaciones sobre
    un recorrido comprometido ejercitado solo por seleccion de operacion
    (familia u3-disposable-product sin seleccion, operacion
    u3.contract-staging con selection C-U3) como si fuera completa y entra
    a la base sobre captura rota confundida con medicion valida."""
    synthetic_nodeids = ["test_sample.py::test_pass"]
    op_scope = write_synthetic_op_scope(workspace, synthetic_nodeids)

    scope = json.loads(op_scope.read_text(encoding="utf-8"))
    committed = scope_requires_operations(scope)
    assert "synthetic-op-selection" in committed, (
        "017-001 T2 P5: el alcance sintetico debe declarar la familia "
        "comprometida: %r" % committed)
    family = scope["families"][0]
    assert "selection" not in family, (
        "017-001 T2 P5: la familia debe omitir la seleccion para ejercitar "
        "la regla de operacion: %r" % family)
    assert family["operations"][0].get("selection") == "C-OP-SYNTH", (
        "017-001 T2 P5: la operacion debe declarar la seleccion aplicable: "
        "%r" % family["operations"][0])
    selected = scope["selections"]["C-OP-SYNTH"]["nodeids"]
    assert synthetic_nodeids[0] in selected, (
        "017-001 T2 P5: la seleccion de operacion debe incluir el nodeid "
        "ejecutado: %r" % selected)

    # (A) Captura faltante sobre recorrido ejercitado por seleccion de
    # operacion: el hijo no emite ninguna marca → status incomplete con
    # diagnosis no vacia; la lista puede estar vacia.
    before = set(attempts(workspace))
    rc, _, _ = run_close(workspace, ["test_pass"], "ops-op-missing",
                         operation_scope=op_scope)
    assert rc == 0, (
        "017-001 T2 P5: la seleccion limpia debe cerrar con rc 0; si no, se "
        "rompio el resultado contractual antes del oraculo")
    missing = set(attempts(workspace)) - before
    assert len(missing) == 1, (
        "017-001 T2 P5: un close debe reservar exactamente un intento nuevo")
    profile = profile_data(missing.pop())
    assert profile.get("status") == "incomplete", (
        "017-001 T2 P5: el alcance aplicado declara la operacion "
        "synthetic.op-prepare con seleccion C-OP-SYNTH sobre el nodeid "
        "ejecutado y el perfil capturo cero operaciones; la medicion queda "
        "incomplete hasta recalibrar, nunca complete")
    assert isinstance(profile.get("diagnosis"), str) and profile["diagnosis"].strip(), (
        "017-001 T2 P5: la medicion incomplete quedo sin diagnosis accionable; "
        "no distingue la falla de captura del resultado de pytest")
    operations = profile.get("operations")
    assert isinstance(operations, list), (
        "017-001 T2 P5: profile.json no conserva la forma de operations como "
        "lista aunque este vacia")

    # (B) Contraste: la operacion no declara seleccion (familia sin
    # seleccion, operacion sin seleccion) → recorrido no ejercitado, el
    # perfil sigue complete.
    no_selection_scope = write_synthetic_op_scope(
        workspace, synthetic_nodeids, label="synthetic-op-noselection",
        include_op_selection=False)
    no_selection = json.loads(no_selection_scope.read_text(encoding="utf-8"))
    assert "selection" not in no_selection["families"][0], (
        "017-001 T2 P5: el contraste sin seleccion no debe declarar "
        "seleccion de familia")
    assert "selection" not in no_selection["families"][0]["operations"][0], (
        "017-001 T2 P5: el contraste sin seleccion no debe declarar "
        "seleccion de operacion")
    before = set(attempts(workspace))
    rc, _, _ = run_close(workspace, ["test_pass"], "ops-op-noselection",
                         operation_scope=no_selection_scope)
    assert rc == 0, (
        "017-001 T2 P5: el contraste sin seleccion debe cerrar con rc 0")
    fresh = set(attempts(workspace)) - before
    assert len(fresh) == 1, (
        "017-001 T2 P5: un close debe reservar exactamente un intento nuevo")
    contrast = profile_data(fresh.pop())
    assert contrast.get("status") == "complete", (
        "017-001 T2 P5: sin seleccion aplicable no hay recorrido ejercitado; "
        "el perfil debe seguir complete, no %r" % contrast.get("status"))

    # (C) Contraste: la seleccion de operacion no incluye el nodeid
    # ejecutado → recorrido no ejercitado, el perfil sigue complete.
    other_scope = write_synthetic_op_scope(
        workspace, synthetic_nodeids, label="synthetic-op-other",
        selection_name="C-OP-OTHER",
        selection_nodeids=["test_sample.py::test_other"])
    other = json.loads(other_scope.read_text(encoding="utf-8"))
    assert synthetic_nodeids[0] not in other["selections"]["C-OP-OTHER"]["nodeids"], (
        "017-001 T2 P5: el contraste debe declarar una seleccion que no "
        "incluye el nodeid ejecutado")
    before = set(attempts(workspace))
    rc, _, _ = run_close(workspace, ["test_pass"], "ops-op-other",
                         operation_scope=other_scope)
    assert rc == 0, (
        "017-001 T2 P5: el contraste con seleccion ajena debe cerrar con rc 0")
    fresh = set(attempts(workspace)) - before
    assert len(fresh) == 1, (
        "017-001 T2 P5: un close debe reservar exactamente un intento nuevo")
    other_profile = profile_data(fresh.pop())
    assert other_profile.get("status") == "complete", (
        "017-001 T2 P5: con seleccion de operacion que no incluye el nodeid "
        "ejecutado no hay recorrido ejercitado; el perfil debe seguir "
        "complete, no %r" % other_profile.get("status"))


# Hijo ambiguo (P6): el mismo helper vive en la raíz del workspace (copia
# bare que el observador importa primero) Y bajo tests/ como paquete; el
# test del hijo importa tests.suite_operation_markers. Con tests/ en
# sys.path y tests como paquete coexisten dos instancias del helper y el
# sumidero queda conectado en la que nadie usa → operations vacías hasta
# el fix, aunque el hijo emita marcas reales.
AMBIGUOUS_SAMPLE = (
    "from tests.suite_operation_markers import operation\n"
    "def test_amb():\n"
    "    with operation(\"u4.lookup\", branch=\"cold\"):\n"
    "        with operation(\"u4.copy\", branch=\"cold\"):\n"
    "            assert True\n"
)

# Hijo ambiguo sin marcas (P6 contraste): mismo layout, cuerpo limpio.
AMBIGUOUS_PLAIN = (
    "def test_amb(): pass\n"
)


def install_ambiguous_layout(workspace):
    """Reproduce la ambigüedad dual-instancia (P6): helper en la raíz del
    workspace Y bajo tests/ como paquete. Sin ambas copias el hijo no
    puede importar tests.suite_operation_markers y el oráculo no ejercita
    el defecto (sería D1 insatisfacible, no esta promesa)."""
    install_helper(workspace)
    pkg = workspace / "tests"
    pkg.mkdir(exist_ok=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    assert HELPER_SRC.is_file(), (
        "017-001 T2 P6: falta tests/suite_operation_markers.py en el checkout; "
        "sin el helper no hay ambigüedad que reproducir")
    shutil.copy(HELPER_SRC, pkg / "suite_operation_markers.py")


def run_close_nodeids(workspace, nodeids, label, timeout=180,
                      operation_scope=None):
    """Variante de run_close con nodeids completos (P6): la selección vive
    bajo tests/ como paquete, no en la raíz. run_close queda intacto."""
    nodeids_path = workspace / (label + ".txt")
    nodeids_path.write_text("\n".join(nodeids) + "\n", encoding="utf-8")
    cmd = [sys.executable, str(CLI), "close", "--evidence-root", str(workspace / "evidence"),
           "--nodeids", str(nodeids_path)]
    if operation_scope is not None:
        cmd += ["--operation-scope", str(operation_scope)]
    process = subprocess.Popen(
        cmd,
        cwd=workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(timeout=timeout)
    return process.returncode, out, err


# P6 — el layout ambiguo (helper bare en raíz + tests/ paquete, hijo que
# importa tests.suite_operation_markers) captura operaciones en el perfil:
# una sola instancia compartida entre observador e hijo, sin sumidero en
# la copia que nadie usa. El contraste sin marcas sigue diagnosticando
# incomplete con diagnosis (spec §4.4).
# PC-1 (parte operaciones), INV-1, INV-6, INV-8.
def test_ambiguous_helper_import_still_captures_operations(workspace):
    """Sin este test, el usuario consume un perfil con phases pero
    operations vacías sobre un recorrido que sí emitió marcas —la pérdida
    ocurre por la doble instancia, no por marcas ausentes— y entra a la
    base sobre captura rota confundida con medición incompleta genuina;
    ningún contraste distingue entonces marcas perdidas de marcas nunca
    emitidas."""
    nodeid = "tests/test_ambiguous.py::test_amb"
    synthetic_scope = write_synthetic_scope(
        workspace, [nodeid], label="synthetic-ambiguous-scope")

    scope = json.loads(synthetic_scope.read_text(encoding="utf-8"))
    committed = scope_requires_operations(scope)
    assert "synthetic-committed-preparation" in committed, (
        "017-001 T2 P6: el alcance sintetico debe declarar un recorrido "
        "comprometido que incluya el nodeid ejecutado: %r" % committed)
    selected = scope["selections"]["C-SYNTH"]["nodeids"]
    assert nodeid in selected, (
        "017-001 T2 P6: el alcance sintetico debe incluir el nodeid "
        "ejecutado como parte del recorrido comprometido: %r" % selected)

    install_ambiguous_layout(workspace)
    (workspace / "tests" / "test_ambiguous.py").write_text(
        AMBIGUOUS_SAMPLE, encoding="utf-8")

    # (A) El hijo emite marcas vía tests.suite_operation_markers: el perfil
    # debe traer operations no vacías (una sola instancia compartida).
    before = set(attempts(workspace))
    rc, _, _ = run_close_nodeids(
        workspace, [nodeid], "ops-ambiguous", operation_scope=synthetic_scope)
    assert rc == 0, (
        "017-001 T2 P6: el hijo ambiguo debe cerrar con rc 0; si no, se "
        "rompió la colección o el import (tests como paquete) antes del "
        "oráculo, no la promesa")
    fresh = set(attempts(workspace)) - before
    assert len(fresh) == 1, (
        "017-001 T2 P6: un close debe reservar exactamente un intento nuevo")
    profile = profile_data(fresh.pop())
    operations = profile.get("operations")
    assert isinstance(operations, list) and operations, (
        "017-001 T2 P6: el perfil no trae operaciones aunque el hijo emitió "
        "marcas vía tests.suite_operation_markers; el sumidero quedó en la "
        "instancia que nadie usa (ambigüedad bare vs paquete)")
    assert profile.get("status") == "complete", (
        "017-001 T2 P6: con marcas capturadas y alcance satisfecho la medición "
        "debe quedar complete, no %r" % profile.get("status"))
    assert not profile.get("diagnosis"), (
        "017-001 T2 P6: una medición completa no debe traer diagnóstico pendiente")

    # (B) Contraste: el mismo layout sin marcas (cuerpo limpio) sigue
    # diagnosticando incomplete con diagnosis sobre el recorrido ejercitado.
    (workspace / "tests" / "test_ambiguous.py").write_text(
        AMBIGUOUS_PLAIN, encoding="utf-8")
    before = set(attempts(workspace))
    rc, _, _ = run_close_nodeids(
        workspace, [nodeid], "ops-ambiguous-plain",
        operation_scope=synthetic_scope)
    assert rc == 0, (
        "017-001 T2 P6: la selección limpia debe cerrar con rc 0; si no, se "
        "rompió el resultado contractual antes del contraste")
    fresh = set(attempts(workspace)) - before
    assert len(fresh) == 1, (
        "017-001 T2 P6: un close debe reservar exactamente un intento nuevo")
    contrast = profile_data(fresh.pop())
    assert contrast.get("status") == "incomplete", (
        "017-001 T2 P6: sin marcas sobre el recorrido comprometido ejercitado "
        "la medición queda incomplete hasta recalibrar, nunca complete")
    assert isinstance(contrast.get("diagnosis"), str) and contrast["diagnosis"].strip(), (
        "017-001 T2 P6: la medición incomplete quedó sin diagnosis accionable; "
        "no distingue la falla de captura del resultado de pytest")
    contrast_ops = contrast.get("operations")
    assert isinstance(contrast_ops, list), (
        "017-001 T2 P6: profile.json no conserva la forma de operations como "
        "lista aunque esté vacía")


# ---------------------------------------------------------------------------
# C-P-cold / C-P-present — verificadores de calibración de
# portable-product-staging (review-T2-002, hallazgo 1 bloqueante; spec §4.2;
# PC-1 parte operaciones, INV-1/INV-3/INV-8).
#
# El registro compromete product.lookup/copy/generate con ramas C-P-cold
# (fría: lookup cold + copy + generate anidados, luego cached) y C-P-present
# (checkout-manifest sin copy/generate, luego cached), pero calibration.md
# reconoce que ninguna selección las ejercitó: la rama fría queda no
# ejercitada porque el checkout examinado ya trae manifiesto. Sin estos dos
# verificadores, quien consuma el registro encuentra operaciones
# comprometidas sin evidencia focal de sus ramas, límites y anidamiento, y
# la base no puede acreditarse sobre el costo de staging de producto.
#
# Honestidad RED (paquete red-012): NO hay comportamiento nuevo —
# tests/product_staging.py ya implementa las tres ramas. Estos verificadores
# pasan de entrada: son verificadores VERDES de calibración, no RED. La
# protección que aportan (antes ausente) es la evidencia focal de ramas,
# anidamiento, árbol devuelto y no-mutación del checkout real sobre una
# fuente descartable real con `make staging` real.
#
# La fuente descartable excluye .git/cachés/build/.cdad: .cdad guarda la
# evidencia viva y el mapeo (§D) exige que quede fuera de los orígenes
# copiados; `make staging` no la necesita (verificado: genera el manifiesto
# en una copia mínima en ~0.3s). build se excluye en C-P-cold para lograr la
# ausencia de manifiesto, y en C-P-present se repone solo el manifiesto real
# (bytes copiados del checkout, procedencia registrada). Nunca se escribe en
# el checkout real: se contrasta por bytes del manifiesto antes/después.
# ---------------------------------------------------------------------------

def _disposable_product_source(tmp_path, label, with_manifest):
    """Copia descartable real del repo bajo tmp_path.

    Devuelve (source, provenance). Con with_manifest=False la copia queda
    SIN build/staging/manifest.json (rama fría); con True se repone el
    manifiesto real con procedencia registrada (rama checkout-manifest).
    """
    real_root = Path(__file__).resolve().parents[1]
    dest = tmp_path / label
    shutil.copytree(
        real_root,
        dest,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            ".git", ".pytest_cache", "__pycache__", "build", ".cdad", ".cdad-execution"),
    )
    provenance = {"source_root": str(real_root), "disposable": str(dest)}
    if with_manifest:
        real_manifest = real_root / "build" / "staging" / "manifest.json"
        assert real_manifest.is_file(), (
            "017-001 C-P-present: el checkout real debe traer el manifiesto "
            "para copiar su procedencia a la fuente descartable")
        target = dest / "build" / "staging" / "manifest.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(real_manifest, target)
        provenance["manifest_source"] = str(real_manifest)
        provenance["manifest_bytes"] = target.stat().st_size
    else:
        assert not (dest / "build" / "staging" / "manifest.json").exists(), (
            "017-001 C-P-cold: la fuente descartable debe quedar SIN "
            "manifiesto de staging")
    return dest, provenance


# C-P-cold — rama fría real + reutilización. PC-1 (parte operaciones),
# INV-1 (identidad/anidamiento), INV-3 (nada se escribe en el checkout),
# INV-8 (evidencia focal previa de un intervalo comprometido).
def test_product_root_cold_then_reuse(tmp_path):
    """Sin este test, la rama fría de product_root (copy+generate reales)
    sigue comprometida sin haberse ejercitado jamás: el usuario entraría a
    la base atribuyendo un costo de staging jamás medido ni anidado."""
    from tests import product_staging

    real_root = Path(__file__).resolve().parents[1]
    real_manifest = real_root / "build" / "staging" / "manifest.json"
    assert real_manifest.is_file(), (
        "017-001 C-P-cold: precondición para contrastar no-mutación: el "
        "checkout real debe traer build/staging/manifest.json")
    before_bytes = real_manifest.read_bytes()

    source, _provenance = _disposable_product_source(
        tmp_path, "disposable-cold", with_manifest=False)

    saved_repo_root = product_staging.REPO_ROOT
    saved_cached = product_staging._product_root
    product_staging.REPO_ROOT = source
    product_staging._product_root = None
    try:
        with observed() as seen:
            first = product_staging.product_root()
            second = product_staging.product_root()
    finally:
        product_staging.REPO_ROOT = saved_repo_root
        product_staging._product_root = saved_cached

    for record in seen:
        check_begin_contract(record)
    begins = [r for r in seen if r["event"] == "begin"]
    ends = [r for r in seen if r["event"] == "end"]
    lookups = [r for r in begins if r["operation"] == "product.lookup"]
    copies = [r for r in begins if r["operation"] == "product.copy"]
    generates = [r for r in begins if r["operation"] == "product.generate"]
    assert [r["branch"] for r in lookups] == ["cold", "cached"], (
        "017-001 C-P-cold: dos lookups esperados (cold + cached): %r"
        % [(r["operation"], r["branch"]) for r in begins])
    assert len(copies) == 1 and copies[0]["branch"] == "cold", (
        "017-001 C-P-cold: una copia fría esperada: %r" % begins)
    assert len(generates) == 1 and generates[0]["branch"] == "cold", (
        "017-001 C-P-cold: una generación fría esperada: %r" % begins)
    assert copies[0]["parent_id"] == lookups[0]["interval_id"], (
        "017-001 C-P-cold: product.copy no cuelga del lookup frío: %r"
        % begins)
    assert generates[0]["parent_id"] == lookups[0]["interval_id"], (
        "017-001 C-P-cold: product.generate no cuelga del lookup frío: %r"
        % begins)
    assert lookups[1]["parent_id"] is None, (
        "017-001 C-P-cold: el lookup cached debe ser raíz: %r" % lookups[1])
    assert {r["termination"] for r in ends} == {"ok"}, (
        "017-001 C-P-cold: todo cierre limpio termina ok: %r" % ends)
    assert len(begins) == len(ends) == 4, (
        "017-001 C-P-cold: 4 comienzos y 4 fines esperados: %r" % seen)

    assert first == second, (
        "017-001 C-P-cold: la reutilización debe devolver la misma raíz")
    assert first != source and first != real_root, (
        "017-001 C-P-cold: la rama fría genera en una copia propia, no en "
        "la fuente ni en el checkout: %r" % str(first))
    generated = first / "build" / "staging" / "manifest.json"
    assert generated.is_file(), (
        "017-001 C-P-cold: `make staging` real no generó el manifiesto en "
        "la copia de producto: %r" % str(first))
    json.loads(generated.read_text(encoding="utf-8"))
    assert not (source / "build" / "staging" / "manifest.json").exists(), (
        "017-001 C-P-cold: la generación escribió en la fuente descartable "
        "en vez de en la copia de producto")
    assert real_manifest.read_bytes() == before_bytes, (
        "017-001 C-P-cold: el checkout real fue tocado (INV-3)")


# C-P-present — manifiesto existente + reutilización. PC-1 (parte
# operaciones), INV-1, INV-3, INV-8.
def test_product_root_existing_manifest_then_reuse(tmp_path):
    """Sin este test, la rama checkout-manifest (presencia reutilizada sin
    copy/generate) sigue comprometida sin haberse ejercitado jamás: el
    usuario no distingue presencia reutilizada de rama fría y puede pagar
    una generación que el registro declara innecesaria."""
    from tests import product_staging

    real_root = Path(__file__).resolve().parents[1]
    real_manifest = real_root / "build" / "staging" / "manifest.json"
    assert real_manifest.is_file(), (
        "017-001 C-P-present: precondición: el checkout real debe traer "
        "build/staging/manifest.json")
    before_bytes = real_manifest.read_bytes()

    source, provenance = _disposable_product_source(
        tmp_path, "disposable-present", with_manifest=True)
    assert (source / "build" / "staging" / "manifest.json").read_bytes() == \
        before_bytes, (
            "017-001 C-P-present: la fuente descartable debe portar el "
            "manifiesto real con procedencia %r" % provenance)

    saved_repo_root = product_staging.REPO_ROOT
    saved_cached = product_staging._product_root
    product_staging.REPO_ROOT = source
    product_staging._product_root = None
    try:
        with observed() as seen:
            first = product_staging.product_root()
            second = product_staging.product_root()
    finally:
        product_staging.REPO_ROOT = saved_repo_root
        product_staging._product_root = saved_cached

    for record in seen:
        check_begin_contract(record)
    begins = [r for r in seen if r["event"] == "begin"]
    ends = [r for r in seen if r["event"] == "end"]
    lookups = [r for r in begins if r["operation"] == "product.lookup"]
    assert [r["branch"] for r in lookups] == ["checkout-manifest", "cached"], (
        "017-001 C-P-present: dos lookups esperados (checkout-manifest + "
        "cached): %r" % [(r["operation"], r["branch"]) for r in begins])
    assert not [r for r in begins if r["operation"] == "product.copy"], (
        "017-001 C-P-present: con manifiesto no debe haber copia: %r"
        % begins)
    assert not [r for r in begins if r["operation"] == "product.generate"], (
        "017-001 C-P-present: con manifiesto no debe haber generación: %r"
        % begins)
    assert {r["termination"] for r in ends} == {"ok"}, (
        "017-001 C-P-present: todo cierre limpio termina ok: %r" % ends)
    assert len(begins) == len(ends) == 2, (
        "017-001 C-P-present: 2 comienzos y 2 fines esperados: %r" % seen)

    assert first == second == source, (
        "017-001 C-P-present: con manifiesto la raíz se reutiliza por "
        "presencia: %r" % str(first))
    assert real_manifest.read_bytes() == before_bytes, (
        "017-001 C-P-present: el checkout real fue tocado (INV-3)")


# P7 — sumideros simultáneos (spec §4.2; PC-1 parte operaciones, INV-1,
# INV-8): el observador del close y el observed() del verificador coexisten.
# attach agrega sin desplazar, detach retira el propio o el último, is_active
# indica si hay alguno, observed agrega el suyo y lo retira al salir, y todos
# los sumideros reciben los eventos.
def test_concurrent_sinks_coexist_and_both_receive_events():
    """Sin este test, el observed() del verificador desplaza con attach() el
    sumidero único del observador del close: la corrida C-P por close no
    captura product.lookup aunque el hijo emitió las marcas y el perfil queda
    sin operaciones."""
    assert not is_active()
    close_sink = []
    attach(close_sink)
    try:
        assert is_active()
        with observed() as test_sink:
            assert is_active()
            with operation("product.lookup", branch="cold"):
                pass
        assert is_active(), (
            "017-001 T2 P7: al salir observed() debe seguir activo el sumidero "
            "del close; si no, observed() desplazó al observador")
        assert len(test_sink) == 2, (
            "017-001 T2 P7: el sumidero del test debe recibir begin+end: %r"
            % test_sink)
        assert len(close_sink) == 2, (
            "017-001 T2 P7: el sumidero del close quedó desplazado por el del "
            "test y no recibió las marcas: %r" % close_sink)
        test_begin, test_end = test_sink
        close_begin, close_end = close_sink
        assert test_begin["event"] == "begin" and test_end["event"] == "end", (
            "017-001 T2 P7: el sumidero del test no recibió begin+end: %r"
            % test_sink)
        assert close_begin == test_begin and close_end == test_end, (
            "017-001 T2 P7: ambos sumideros deben recibir los mismos eventos: "
            "%r vs %r" % (close_sink, test_sink))
        check_begin_contract(test_begin)
        detach(close_sink)
        assert not is_active(), (
            "017-001 T2 P7: detach(sumidero) debe retirar ese sumidero")
        attach(close_sink)
        attach(test_sink)
        detach()
        assert is_active(), (
            "017-001 T2 P7: detach() debe retirar solo el último sumidero")
        detach()
        assert not is_active(), (
            "017-001 T2 P7: sin sumideros no hay observador activo")
    finally:
        while is_active():
            detach()
    assert not is_active()
