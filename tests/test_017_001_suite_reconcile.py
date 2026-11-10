"""017-001 T3 RED: oraculo contable del agregador y de la condicion de entrada.

Derivado del contrato aprobado ``docs/specs/017-001-suite-performance/
spec.md`` §4.4 (PC-6, INV-5/INV-6) operacionalizado por
``docs/specs/017-001-suite-performance/t3-aggregator-contract.md``. No lee
implementacion: ejerce la CLI fija como caja negra sobre intentos
sinteticos en directorios temporales descartables con profile.json y
attempt.json bien formados (forma publicada por T1/T2):

    python3 scripts/cdad-suite.py reconcile --attempt <dir> --out <dir> [--register <path>]
    python3 scripts/cdad-suite.py entry-check --attempts <mapping.json> --out <dir> [--register <path>]

Cubre los ocho casos contables del contrato operativo mas los codigos de
salida (0 reconciliacion producida, 1 entrada no satisfecha, 2 entrada
inutilizable) y la escritura de los documentos markdown.

Trazabilidad: todos protegen PC-6 (conciliacion reproducible desde
evidencia cruda, sin doble conteo, con residual y diagnostico) con
INV-5 (un intervalo contribuye una sola vez) e INV-6 (ausencia no es
cero; incompleto no es base valida) donde se indica.

Forma de profile.json/attempt.json usada (campos del contrato §Entrada):
profile con schema_version, status, diagnosis, pytest_argv,
pytest_wall_s, phases [{nodeid, when, duration_s, outcome}], operations
[{operation, interval_id, parent_id, nodeid, phase, owner_scope,
started, finished, termination[, branch, duration_s]}], operation_scope
{path}, capture_errors, operation_errors; attempt con started_at,
finished_at, commit, dirty, rc, selection, pytest_summary.

Forma esperada de la salida (conceptos del contrato; los nombres de
clave JSON aceptan los alias documentados en los helpers porque el
contrato fija conceptos, no claves): reconciliation.json con S_test,
preparacion atribuida y resto por test, bloque de compartidas, residuos
de corrida y exterior con signo y resolucion, diagnosticos como codigos
nombrados; entry.json con satisfied, checks nombrados y motivos;
reconciliation.md / entry.md no vacios.

Sin umbrales temporales como oraculo: solo igualdades contables con
tolerancia 1e-3 s (la declarada por el contrato) y signos; nunca techos
ni bound==deadline.

Hoy cada test falla por AssertionError de promesa ausente (rc esperado
0/1 y obtenido 2 por subcomando inexistente), nunca por ImportError ni
error de coleccion.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

CLI = Path(__file__).resolve().parents[1] / "scripts" / "cdad-suite.py"

TOL = 1e-3


# --------------------------------------------------------------------------
# Constructores de evidencia sintetica
# --------------------------------------------------------------------------

def phase_row(nodeid, when, duration_s, outcome="passed"):
    return {"nodeid": nodeid, "when": when, "duration_s": duration_s,
            "outcome": outcome}


def op_row(operation, interval_id, parent_id, nodeid, phase, owner_scope,
           started, finished, termination="ok", branch="cold"):
    return {"operation": operation, "interval_id": interval_id,
            "parent_id": parent_id, "nodeid": nodeid, "phase": phase,
            "owner_scope": owner_scope, "branch": branch,
            "started": started, "finished": finished,
            "duration_s": finished - started, "termination": termination}


def write_attempt(attempt_dir, *, phases, operations, status="complete",
                  diagnosis="", pytest_wall_s=5.0, started_at=1000.0,
                  finished_at=1008.0, commit="a" * 40, dirty=False, rc=0,
                  selection=None, operation_scope=None):
    attempt_dir = Path(attempt_dir)
    attempt_dir.mkdir(parents=True, exist_ok=True)
    if selection is None:
        nodeids = sorted({p["nodeid"] for p in phases})
        selection = nodeids
    profile = {
        "schema_version": 1,
        "status": status,
        "diagnosis": diagnosis,
        "pytest_argv": ["pytest"] + list(selection),
        "pytest_wall_s": pytest_wall_s,
        "phases": list(phases),
        "operations": list(operations),
        "operation_scope": operation_scope if operation_scope is not None else {},
        "capture_errors": [],
        "operation_errors": [],
    }
    attempt = {
        "started_at": started_at,
        "finished_at": finished_at,
        "commit": commit,
        "dirty": dirty,
        "rc": rc,
        "state": "finished",
        "selection": list(selection),
        "pytest_summary": {"passed": len(selection)},
    }
    (attempt_dir / "profile.json").write_text(json.dumps(profile, indent=2),
                                              encoding="utf-8")
    (attempt_dir / "attempt.json").write_text(json.dumps(attempt, indent=2),
                                              encoding="utf-8")
    return attempt_dir


def write_register(path, *, selections, expected_counts, calibrated=True,
                   with_decision_rule=True):
    """Registro sintetico minimo con la forma del contrato (cobertura §)."""
    families = [{
        "family": "synthetic-committed-preparation",
        "selection": "C-SYNTH",
        "state": "comprometida",
        "classification": "preparacion",
        "context": "test-call",
        "operations": [
            {"id": op_id, "expected": expected}
            for op_id, expected in expected_counts.items()
        ],
    }]
    scope = {
        "schema_version": 1,
        "status": "calibrated" if calibrated else "draft",
        "calibrated": calibrated,
        "feature_id": "017-001-suite-performance",
        "selections": selections,
        "families": families,
        "volume_observations": {
            "synthetic-volume": {
                "unknown_component": (
                    {"decision_rule": "retain-in-remainder"}
                    if with_decision_rule else {}
                ),
            },
        },
    }
    path = Path(path)
    path.write_text(json.dumps(scope, indent=2), encoding="utf-8")
    return path


def run_reconcile(attempt_dir, out_dir, register=None, timeout=60):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(CLI), "reconcile",
           "--attempt", str(attempt_dir), "--out", str(out_dir)]
    if register is not None:
        cmd += ["--register", str(register)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def run_entry(mapping, out_dir, register=None, timeout=60):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(CLI), "entry-check",
           "--attempts", str(mapping), "--out", str(out_dir)]
    if register is not None:
        cmd += ["--register", str(register)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def read_json(path):
    path = Path(path)
    assert path.is_file(), (
        "017-001 T3: falta el documento esperado %s; sin el la promesa "
        "contable no es recuperable" % path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def assert_markdown(out_dir, name):
    doc = Path(out_dir) / name
    assert doc.is_file(), (
        "017-001 T3: falta el documento %s; el responsable no puede leer "
        "la conciliacion/entrada sin el markdown" % name)
    text = doc.read_text(encoding="utf-8")
    assert text.strip(), (
        "017-001 T3: el documento %s esta vacio; un markdown vacio no "
        "acredita nada" % name)
    return text


# --------------------------------------------------------------------------
# Lectura tolerante a alias de clave (el contrato fija conceptos, no claves)
# --------------------------------------------------------------------------

def _test_rows(payload):
    if isinstance(payload.get("tests"), list):
        return payload["tests"]
    if isinstance(payload.get("by_test"), dict):
        return [{"nodeid": k, **v} for k, v in payload["by_test"].items()]
    return []


def find_test(payload, nodeid):
    for row in _test_rows(payload):
        if row.get("nodeid") == nodeid:
            return row
    raise AssertionError(
        "017-001 T3: reconciliation.json no trae el test %s; sin su fila "
        "no hay S_test que contrastar: %r" % (nodeid, payload))


def num(row, *aliases):
    for key in aliases:
        if key in row and isinstance(row[key], (int, float)):
            return float(row[key])
    raise AssertionError(
        "017-001 T3: la fila %r no trae ninguno de los campos %r; sin la "
        "cifra no hay conciliacion verificable" % (row, aliases))


def s_test_of(row):
    return num(row, "S_test", "s_test")


def attributed_of(row):
    return num(row, "preparation_s", "attributed", "preparation",
                "attributed_s")


def remainder_of(row):
    return num(row, "remainder_s", "remainder", "resto")


def run_block(payload):
    run = payload.get("run")
    assert isinstance(run, dict), (
        "017-001 T3: reconciliation.json no trae bloque de corrida con "
        "residuos; sin el no hay conciliacion con el tiempo exterior: %r"
        % payload)
    return run


def diagnostics_of(payload):
    diag = payload.get("diagnostics", payload.get("diagnosticos", []))
    assert isinstance(diag, list), (
        "017-001 T3: los diagnosticos no son una lista: %r" % diag)
    codes = set()
    for item in diag:
        if isinstance(item, str):
            codes.add(item)
        elif isinstance(item, dict):
            for key in ("code", "codigo", "diagnostic"):
                if key in item:
                    codes.add(str(item[key]))
    return codes


# Caso 1 — S_test/atribuido/resto. PC-6, INV-5.
def test_reconcile_two_tests_reports_s_test_attributed_and_remainder(tmp_path):
    """Sin este test, el usuario recibe una conciliacion que no desglosa
    S_test en preparacion medida y resto, y no puede localizar el costo."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node_a = "test_sample.py::test_a"
    node_b = "test_sample.py::test_b"
    phases = [
        phase_row(node_a, "setup", 0.1),
        phase_row(node_a, "call", 1.0),
        phase_row(node_a, "teardown", 0.2),
        phase_row(node_b, "call", 2.0),
    ]
    operations = [
        op_row("prep.op", "op-a1", None, node_a, "call", "test", 10.0, 10.5),
        op_row("prep.op", "op-b1", None, node_b, "call", "test", 20.0, 20.25),
    ]
    attempt = write_attempt(tmp_path / "attempt", phases=phases,
                            operations=operations, pytest_wall_s=5.0,
                            started_at=1000.0, finished_at=1008.0)
    out = tmp_path / "out"
    rc, _, err = run_reconcile(attempt, out)
    assert rc == 0, (
        "017-001 T3 caso 1 (PC-6): reconcile debe salir 0 con intento "
        "completo; salio %r: %s" % (rc, err.decode("utf-8", "replace")))
    payload = read_json(out / "reconciliation.json")
    row_a = find_test(payload, node_a)
    assert abs(s_test_of(row_a) - 1.3) <= TOL, (
        "017-001 T3 caso 1: S_test de test_a debe ser 1.3 (0.1+1.0+0.2), "
        "fue %r" % row_a)
    assert abs(attributed_of(row_a) - 0.5) <= TOL, (
        "017-001 T3 caso 1: atribuido de test_a debe ser 0.5, fue %r" % row_a)
    assert abs(remainder_of(row_a) - 0.8) <= TOL, (
        "017-001 T3 caso 1: resto de test_a debe ser 0.8 con signo "
        "explicito, fue %r" % row_a)
    row_b = find_test(payload, node_b)
    assert abs(s_test_of(row_b) - 2.0) <= TOL, (
        "017-001 T3 caso 1: S_test de test_b debe ser 2.0, fue %r" % row_b)
    assert abs(attributed_of(row_b) - 0.25) <= TOL, (
        "017-001 T3 caso 1: atribuido de test_b debe ser 0.25, fue %r" % row_b)
    assert abs(remainder_of(row_b) - 1.75) <= TOL, (
        "017-001 T3 caso 1: resto de test_b debe ser 1.75, fue %r" % row_b)
    text = assert_markdown(out, "reconciliation.md")
    assert "test_a" in text and "test_b" in text, (
        "017-001 T3 caso 1: reconciliation.md no nombra los tests conciliados")


# Caso 2 — anidamiento padre-hijo sin doble conteo. PC-6, INV-5.
def test_reconcile_nested_child_is_breakdown_not_additional_cost(tmp_path):
    """Sin este test, el agregador puede sumar el hijo dentro del padre y
    presentar una preparacion mayor que S_test (doble conteo)."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node = "test_sample.py::test_nested"
    phases = [phase_row(node, "call", 2.0)]
    operations = [
        op_row("parent.op", "p1", None, node, "call", "test", 0.0, 1.0),
        op_row("child.op", "c1", "p1", node, "call", "test", 0.2, 0.7),
    ]
    attempt = write_attempt(tmp_path / "attempt", phases=phases,
                            operations=operations)
    out = tmp_path / "out"
    rc, _, err = run_reconcile(attempt, out)
    assert rc == 0, (
        "017-001 T3 caso 2 (PC-6/INV-5): reconcile debe salir 0; salio %r: "
        "%s" % (rc, err.decode("utf-8", "replace")))
    payload = read_json(out / "reconciliation.json")
    row = find_test(payload, node)
    assert abs(attributed_of(row) - 1.0) <= TOL, (
        "017-001 T3 caso 2: el hijo incluido en el padre es desglose, no "
        "costo adicional: atribuido debe ser 1.0 (union), no 1.5; fue %r"
        % row)
    assert abs(remainder_of(row) - 1.0) <= TOL, (
        "017-001 T3 caso 2: resto debe ser 1.0 (2.0-1.0), fue %r" % row)
    assert_markdown(out, "reconciliation.md")


# Caso 3 — solapamiento parcial como union. PC-6, INV-5.
def test_reconcile_partial_overlap_counts_union_not_sum(tmp_path):
    """Sin este test, dos operaciones hermanas solapadas se suman dos veces
    en la interseccion y la preparacion supera el tiempo real."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node = "test_sample.py::test_overlap"
    phases = [phase_row(node, "call", 3.0)]
    operations = [
        op_row("sib.a", "a1", None, node, "call", "test", 0.0, 0.6),
        op_row("sib.b", "b1", None, node, "call", "test", 0.4, 1.0),
    ]
    attempt = write_attempt(tmp_path / "attempt", phases=phases,
                            operations=operations)
    out = tmp_path / "out"
    rc, _, err = run_reconcile(attempt, out)
    assert rc == 0, (
        "017-001 T3 caso 3 (PC-6/INV-5): reconcile debe salir 0; salio %r: "
        "%s" % (rc, err.decode("utf-8", "replace")))
    payload = read_json(out / "reconciliation.json")
    row = find_test(payload, node)
    assert abs(attributed_of(row) - 1.0) <= TOL, (
        "017-001 T3 caso 3: el solapamiento parcial es union (1.0), no suma "
        "(1.2); fue %r" % row)
    assert_markdown(out, "reconciliation.md")


# Caso 4 — operacion compartida separada. PC-6.
def test_reconcile_shared_operation_stays_separate(tmp_path):
    """Sin este test, la preparacion compartida se adjudica al primer test
    y su S_test queda inflado con costo ajeno."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node = "test_sample.py::test_owned"
    phases = [phase_row(node, "call", 1.0)]
    operations = [
        op_row("own.op", "o1", None, node, "call", "test", 5.0, 5.5),
        op_row("shared.op", "s1", None, None, "setup", "shared", 0.0, 2.0),
    ]
    attempt = write_attempt(tmp_path / "attempt", phases=phases,
                            operations=operations)
    out = tmp_path / "out"
    rc, _, err = run_reconcile(attempt, out)
    assert rc == 0, (
        "017-001 T3 caso 4 (PC-6): reconcile debe salir 0; salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    payload = read_json(out / "reconciliation.json")
    row = find_test(payload, node)
    assert abs(s_test_of(row) - 1.0) <= TOL, (
        "017-001 T3 caso 4: S_test no debe incluir lo compartido; fue %r" % row)
    assert abs(attributed_of(row) - 0.5) <= TOL, (
        "017-001 T3 caso 4: atribuido debe ser solo lo propio (0.5); fue %r"
        % row)
    raw = json.loads((out / "reconciliation.json").read_text(encoding="utf-8"))
    blob = json.dumps(raw)
    assert "shared" in blob, (
        "017-001 T3 caso 4: lo compartido debe informarse en bloque propio, "
        "no desaparecer")
    assert_markdown(out, "reconciliation.md")


# Caso 5 — residuos de corrida y exterior con signo y resolucion. PC-6, INV-6.
def test_reconcile_run_and_exterior_residuals_keep_sign_and_resolution(tmp_path):
    """Sin este test, el usuario no ve cuanto tiempo queda fuera de las
    fases y del hijo pytest, o un residuo negativo se fuerza a cero."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node_a = "test_sample.py::test_a"
    node_b = "test_sample.py::test_b"
    phases = [phase_row(node_a, "call", 1.3), phase_row(node_b, "call", 2.0)]
    operations = [op_row("prep.op", "o1", None, node_a, "call", "test",
                         10.0, 10.5)]
    # Suma S_test = 3.3; T_pytest = 5.0 -> R_pytest = 1.7;
    # T_exterior = 8.0 -> R_exterior = 3.0.
    attempt = write_attempt(tmp_path / "attempt", phases=phases,
                            operations=operations, pytest_wall_s=5.0,
                            started_at=1000.0, finished_at=1008.0)
    out = tmp_path / "out"
    rc, _, err = run_reconcile(attempt, out)
    assert rc == 0, (
        "017-001 T3 caso 5 (PC-6): reconcile debe salir 0; salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    payload = read_json(out / "reconciliation.json")
    run = run_block(payload)
    blob = json.dumps(run)
    assert "R_pytest" in blob or "r_pytest" in blob.lower() or "residual" in blob.lower(), (
        "017-001 T3 caso 5: falta el residuo de corrida con signo explicito: "
        "%r" % run)
    assert "R_exterior" in blob or "r_exterior" in blob.lower() or "exterior" in blob.lower(), (
        "017-001 T3 caso 5: falta el residuo exterior con signo explicito: "
        "%r" % run)
    assert "resol" in json.dumps(payload).lower() or "resolution" in blob.lower(), (
        "017-001 T3 caso 5: falta la resolucion declarada de los relojes; "
        "sin ella el residuo no es interpretable")
    values = [v for v in run.values() if isinstance(v, (int, float))]
    assert any(v > 0 for v in values), (
        "017-001 T3 caso 5: los residuos positivos deben conservar su signo; "
        "fueron %r" % run)
    text = assert_markdown(out, "reconciliation.md")
    assert "residual" in text.lower() or "R_" in text, (
        "017-001 T3 caso 5: reconciliation.md no muestra los residuos")


# Caso 6 — status incomplete: reconciliacion producida, entrada bloqueada.
# PC-6, INV-6.
def test_incomplete_status_still_reconciles_but_blocks_entry(tmp_path):
    """Sin este test, una medicion incompleta o bien bloquea la
    conciliacion (se pierde el diagnostico) o bien deja entrar a la base
    sobre captura rota."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node = "test_sample.py::test_inc"
    phases = [phase_row(node, "call", 1.0)]
    attempt = write_attempt(
        tmp_path / "attempt", phases=phases, operations=[],
        status="incomplete", diagnosis="missing expected intervals",
        pytest_wall_s=2.0, started_at=1000.0, finished_at=1003.0)
    out_rec = tmp_path / "out-rec"
    rc, _, err = run_reconcile(attempt, out_rec)
    assert rc == 0, (
        "017-001 T3 caso 6 (PC-6/INV-6): con status incomplete la "
        "reconciliacion igual se produce (rc 0); salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    assert_markdown(out_rec, "reconciliation.md")
    payload = read_json(out_rec / "reconciliation.json")
    assert "incomplete" in json.dumps(payload).lower(), (
        "017-001 T3 caso 6: la reconciliacion debe reflejar el estado "
        "incomplete del perfil")

    register = write_register(
        tmp_path / "register.json",
        selections={"C-SYNTH": {"existing": True, "fresh_process": True,
                                "nodeids": [node]}},
        expected_counts={})
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps({"C-SYNTH": str(attempt)}),
                            encoding="utf-8")
    out_entry = tmp_path / "out-entry"
    rc, _, err = run_entry(mapping_path, out_entry, register=register)
    assert rc == 1, (
        "017-001 T3 caso 6: con intento incomplete la entrada queda "
        "bloqueada (rc 1); salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    entry = read_json(out_entry / "entry.json")
    assert entry.get("satisfied") is False, (
        "017-001 T3 caso 6: entry.satisfied debe ser false con intento "
        "incomplete: %r" % entry)
    blob = json.dumps(entry).lower()
    assert "profile-incomplete" in blob or "incomplete" in blob, (
        "017-001 T3 caso 6: la entrada bloqueada debe enumerar el "
        "diagnostico del perfil: %r" % entry)
    assert_markdown(out_entry, "entry.md")


# Caso 7 — conteo faltante contra registro bloquea la entrada. PC-6.
def test_missing_count_vs_register_blocks_entry(tmp_path):
    """Sin este test, la base puede consumirse aunque falten operaciones
    comprometidas respecto del registro (conteo esperado > observado)."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node = "test_sample.py::test_cov"
    phases = [phase_row(node, "call", 1.0)]
    operations = [op_row("synthetic.prepare", "m1", None, node, "call",
                         "test", 1.0, 1.5)]
    attempt = write_attempt(tmp_path / "attempt", phases=phases,
                            operations=operations)
    register = write_register(
        tmp_path / "register.json",
        selections={"C-SYNTH": {"existing": True, "fresh_process": True,
                                "nodeids": [node]}},
        expected_counts={"synthetic.prepare": 2})
    out_rec = tmp_path / "out-rec"
    rc, _, err = run_reconcile(attempt, out_rec, register=register)
    assert rc == 0, (
        "017-001 T3 caso 7 (PC-6): reconcile se produce aunque haya "
        "faltante (rc 0); salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    payload = read_json(out_rec / "reconciliation.json")
    assert "missing-operation-vs-register" in diagnostics_of(payload), (
        "017-001 T3 caso 7: la reconciliacion debe diagnosticar "
        "missing-operation-vs-register (esperada 2, observada 1): %r"
        % payload)
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps({"C-SYNTH": str(attempt)}),
                            encoding="utf-8")
    out_entry = tmp_path / "out-entry"
    rc, _, err = run_entry(mapping_path, out_entry, register=register)
    assert rc == 1, (
        "017-001 T3 caso 7: con faltante contra registro la entrada queda "
        "bloqueada (rc 1); salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    entry = read_json(out_entry / "entry.json")
    assert entry.get("satisfied") is False, (
        "017-001 T3 caso 7: entry.satisfied debe ser false con faltante: %r"
        % entry)
    assert "missing-operation-vs-register" in json.dumps(entry), (
        "017-001 T3 caso 7: entry.json debe enumerar "
        "missing-operation-vs-register: %r" % entry)
    assert_markdown(out_entry, "entry.md")


# Caso 8 — determinismo byte a byte. PC-6, INV-1.
def test_reconcile_is_byte_for_byte_deterministic(tmp_path):
    """Sin este test, dos reconciliaciones de la misma entrada pueden
    diferir (orden no fijado) y la evidencia deja de ser reproducible."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node_b = "test_sample.py::test_b"
    node_a = "test_sample.py::test_a"
    phases = [phase_row(node_b, "call", 2.0), phase_row(node_a, "call", 1.0)]
    operations = [
        op_row("prep.op", "o2", None, node_b, "call", "test", 20.0, 20.5),
        op_row("prep.op", "o1", None, node_a, "call", "test", 10.0, 10.5),
    ]
    attempt = write_attempt(tmp_path / "attempt", phases=phases,
                            operations=operations)
    out1, out2 = tmp_path / "out1", tmp_path / "out2"
    rc1, _, err1 = run_reconcile(attempt, out1)
    assert rc1 == 0, (
        "017-001 T3 caso 8 (PC-6/INV-1): primera reconciliacion debe salir "
        "0; salio %r: %s" % (rc1, err1.decode("utf-8", "replace")))
    rc2, _, err2 = run_reconcile(attempt, out2)
    assert rc2 == 0, (
        "017-001 T3 caso 8: segunda reconciliacion debe salir 0; salio %r: "
        "%s" % (rc2, err2.decode("utf-8", "replace")))
    first = (out1 / "reconciliation.json").read_bytes()
    second = (out2 / "reconciliation.json").read_bytes()
    assert first == second, (
        "017-001 T3 caso 8: misma entrada debe dar el mismo "
        "reconciliation.json byte a byte (tests por costo descendente, "
        "empates por nodeid)")
    assert_markdown(out1, "reconciliation.md")


# Codigo 2 — entrada inutilizable con motivo por stderr. PC-6, INV-6.
def test_unusable_inputs_return_2_with_stderr_reason(tmp_path):
    """Sin este test, una entrada rota (sin profile/attempt, JSON invalido
    o mapa incompleto) podria pasar como rc 0/1 silencioso en vez de
    informar su motivo con el codigo 2."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    empty = tmp_path / "empty-attempt"
    empty.mkdir()
    out = tmp_path / "out"
    rc, _, err = run_reconcile(empty, out)
    assert rc == 2, (
        "017-001 T3 codigo 2 (PC-6/INV-6): sin profile.json/attempt.json "
        "reconcile debe salir 2; salio %r" % rc)
    err_text = err.decode("utf-8", "replace").lower()
    assert "profile.json" in err_text or "attempt.json" in err_text, (
        "017-001 T3 codigo 2: el motivo del 2 debe informarse por stderr "
        "nombrando el artefacto faltante; fue %r" % err_text)

    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps({"C-SYNTH": str(tmp_path / "no-existe")}),
                            encoding="utf-8")
    register = write_register(
        tmp_path / "register.json",
        selections={"C-SYNTH": {"existing": True, "fresh_process": True,
                                "nodeids": ["test_sample.py::test_x"]}},
        expected_counts={})
    out_entry = tmp_path / "out-entry"
    rc, _, err = run_entry(mapping_path, out_entry, register=register)
    assert rc == 2, (
        "017-001 T3 codigo 2: con mapa hacia ruta inexistente entry-check "
        "debe salir 2; salio %r" % rc)
    err_text = err.decode("utf-8", "replace")
    assert err_text.strip(), (
        "017-001 T3 codigo 2: el motivo del 2 debe informarse por stderr, "
        "no en silencio")


# Hallazgo bloqueante review-T3 — entry-check vincula clave con seleccion
# declarada y registro. PC-1 (calibracion acredita la seleccion que el
# intento declara; §4.4), PC-6 (entrada reproducible).
def test_entry_check_binds_map_key_to_declared_selection_and_register(tmp_path):
    """Sin este test, el usuario puede iniciar la base con un mapa que asocia
    la clave C-R a un intento cuya seleccion declarada es otra, acreditando
    una calibracion para una seleccion que el intento no declara."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node_ok = "test_sample.py::test_ok"
    node_wrong = "test_other.py::test_wrong"
    attempt_ok = write_attempt(
        tmp_path / "attempt-ok", phases=[phase_row(node_ok, "call", 1.0)],
        operations=[], pytest_wall_s=2.0, started_at=1000.0,
        finished_at=1003.0, selection=[node_ok])
    register = write_register(
        tmp_path / "register.json",
        selections={"C-R": {"existing": True, "fresh_process": True,
                            "nodeids": [node_ok]}},
        expected_counts={})
    mapping_ok = tmp_path / "mapping-ok.json"
    mapping_ok.write_text(json.dumps({"C-R": str(attempt_ok)}),
                          encoding="utf-8")
    out_ok = tmp_path / "out-ok"
    rc, _, err = run_entry(mapping_ok, out_ok, register=register)
    assert rc == 0, (
        "017-001 T3 bloqueante (PC-1): la asociacion correcta C-R -> intento "
        "que declara %r debe seguir saliendo 0; salio %r: %s"
        % (node_ok, rc, err.decode("utf-8", "replace")))
    entry_ok = read_json(out_ok / "entry.json")
    assert entry_ok.get("satisfied") is True, (
        "017-001 T3 bloqueante: la asociacion correcta debe dejar "
        "entry.satisfied=true: %r" % entry_ok)
    assert_markdown(out_ok, "entry.md")

    attempt_bad = write_attempt(
        tmp_path / "attempt-bad",
        phases=[phase_row(node_wrong, "call", 1.0)], operations=[],
        pytest_wall_s=2.0, started_at=1000.0, finished_at=1003.0,
        selection=[node_wrong])
    mapping_bad = tmp_path / "mapping-bad.json"
    mapping_bad.write_text(json.dumps({"C-R": str(attempt_bad)}),
                           encoding="utf-8")
    out_bad = tmp_path / "out-bad"
    rc, _, err = run_entry(mapping_bad, out_bad, register=register)
    assert rc == 1, (
        "017-001 T3 bloqueante (PC-1): un mapa que asocia la clave C-R a un "
        "intento cuya seleccion declarada es %r (registro espera %r) debe "
        "salir 1; salio %r: %s"
        % (node_wrong, node_ok, rc, err.decode("utf-8", "replace")))
    entry = read_json(out_bad / "entry.json")
    assert entry.get("satisfied") is False, (
        "017-001 T3 bloqueante: con seleccion declarada discrepante "
        "entry.satisfied debe ser false: %r" % entry)
    blob = json.dumps(entry).lower()
    assert "c-r" in blob, (
        "017-001 T3 bloqueante: el motivo debe nombrar la clave discrepante "
        "C-R: %r" % entry)
    assert ("selection" in blob or "test_wrong" in blob
            or "nodeid" in blob or "discrep" in blob
            or "mismatch" in blob or "declar" in blob), (
        "017-001 T3 bloqueante: el motivo debe nombrar la discrepancia entre "
        "la seleccion declarada por el intento y la esperada: %r" % entry)
    assert_markdown(out_bad, "entry.md")


# Hallazgo bloqueante review-T3-002 — seleccion ausente o irresoluble
# como fallo nombrado de selection-coverage. PC-1 (la calibracion acredita
# la seleccion que el intento declara; §4.4 + t3-aggregator-contract
# entry-check §selection-coverage), INV-6 (omision no equivale a pase).
def test_entry_check_missing_or_unresolvable_selection_fails_selection_coverage(tmp_path):
    """Sin este test, el usuario puede iniciar la base con un mapa correcto
    cuya seleccion declarada falta en attempt.json (o es un escalar
    irresoluble) y entry-check la acepta en silencio como cobertura valida,
    acreditando una entrada sin el dato que vincula clave con seleccion."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node_ok = "test_sample.py::test_ok"
    register = write_register(
        tmp_path / "register.json",
        selections={"C-R": {"existing": True, "fresh_process": True,
                            "nodeids": [node_ok]}},
        expected_counts={})

    def selection_coverage_check(entry):
        checks = entry.get("checks", [])
        for item in checks:
            if isinstance(item, dict) and item.get("name") == "selection-coverage":
                return item
        raise AssertionError(
            "017-001 T3 bloqueante review-T3-002 (PC-1/INV-6): entry.json no "
            "trae el check nombrado selection-coverage: %r" % entry)

    def assert_selection_coverage_names_key(entry, key="C-R"):
        check = selection_coverage_check(entry)
        assert check.get("passed") is False, (
            "017-001 T3 bloqueante review-T3-002 (PC-1/INV-6): con seleccion "
            "ausente o irresoluble el check selection-coverage debe quedar "
            "falso: %r" % entry)
        blob = json.dumps(check).lower()
        assert key.lower() in blob, (
            "017-001 T3 bloqueante review-T3-002: el motivo de "
            "selection-coverage debe nombrar la clave afectada %s: %r"
            % (key, entry))

    # Contraste positivo: intento completo con seleccion declarada correcta.
    attempt_ok = write_attempt(
        tmp_path / "attempt-ok", phases=[phase_row(node_ok, "call", 1.0)],
        operations=[], pytest_wall_s=2.0, started_at=1000.0,
        finished_at=1003.0, selection=[node_ok])
    mapping_ok = tmp_path / "mapping-ok.json"
    mapping_ok.write_text(json.dumps({"C-R": str(attempt_ok)}),
                          encoding="utf-8")
    out_ok = tmp_path / "out-ok"
    rc, _, err = run_entry(mapping_ok, out_ok, register=register)
    assert rc == 0, (
        "017-001 T3 bloqueante review-T3-002 (PC-1): el contraste con el "
        "intento completo que declara %r debe seguir saliendo 0; salio %r: %s"
        % (node_ok, rc, err.decode("utf-8", "replace")))
    entry_ok = read_json(out_ok / "entry.json")
    assert entry_ok.get("satisfied") is True, (
        "017-001 T3 bloqueante review-T3-002: el intento completo debe dejar "
        "entry.satisfied=true: %r" % entry_ok)
    assert_markdown(out_ok, "entry.md")

    # Caso 1: copia sintetica en temporal descartable cuyo attempt.json NO
    # trae el campo selection (la evidencia real nunca se modifica).
    attempt_miss = write_attempt(
        tmp_path / "attempt-miss", phases=[phase_row(node_ok, "call", 1.0)],
        operations=[], pytest_wall_s=2.0, started_at=1000.0,
        finished_at=1003.0, selection=[node_ok])
    miss_doc = attempt_miss / "attempt.json"
    miss_payload = json.loads(miss_doc.read_text(encoding="utf-8"))
    assert "selection" in miss_payload, (
        "017-001 T3 bloqueante review-T3-002: la copia sintetica debe partir "
        "del intento completo con selection para luego ausentarla")
    del miss_payload["selection"]
    miss_doc.write_text(json.dumps(miss_payload, indent=2), encoding="utf-8")
    mapping_miss = tmp_path / "mapping-miss.json"
    mapping_miss.write_text(json.dumps({"C-R": str(attempt_miss)}),
                            encoding="utf-8")
    out_miss = tmp_path / "out-miss"
    rc, _, err = run_entry(mapping_miss, out_miss, register=register)
    assert rc == 1, (
        "017-001 T3 bloqueante review-T3-002 (PC-1/INV-6): con attempt.json "
        "sin campo selection la entrada debe quedar bloqueada (rc 1); "
        "salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    entry_miss = read_json(out_miss / "entry.json")
    assert entry_miss.get("satisfied") is False, (
        "017-001 T3 bloqueante review-T3-002: con seleccion ausente "
        "entry.satisfied debe ser false: %r" % entry_miss)
    assert "selection-coverage" in json.dumps(entry_miss), (
        "017-001 T3 bloqueante review-T3-002: la entrada bloqueada debe "
        "enumerar el check selection-coverage: %r" % entry_miss)
    assert_selection_coverage_names_key(entry_miss, "C-R")
    assert_markdown(out_miss, "entry.md")

    # Caso 2: selection como escalar irresoluble (no lista de nodeids).
    attempt_scalar = write_attempt(
        tmp_path / "attempt-scalar", phases=[phase_row(node_ok, "call", 1.0)],
        operations=[], pytest_wall_s=2.0, started_at=1000.0,
        finished_at=1003.0, selection=[node_ok])
    scalar_doc = attempt_scalar / "attempt.json"
    scalar_payload = json.loads(scalar_doc.read_text(encoding="utf-8"))
    scalar_payload["selection"] = 999
    scalar_doc.write_text(json.dumps(scalar_payload, indent=2),
                          encoding="utf-8")
    mapping_scalar = tmp_path / "mapping-scalar.json"
    mapping_scalar.write_text(json.dumps({"C-R": str(attempt_scalar)}),
                              encoding="utf-8")
    out_scalar = tmp_path / "out-scalar"
    rc, _, err = run_entry(mapping_scalar, out_scalar, register=register)
    assert rc == 1, (
        "017-001 T3 bloqueante review-T3-002 (PC-1/INV-6): con selection como "
        "escalar irresoluble la entrada debe quedar bloqueada (rc 1); "
        "salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    entry_scalar = read_json(out_scalar / "entry.json")
    assert entry_scalar.get("satisfied") is False, (
        "017-001 T3 bloqueante review-T3-002: con seleccion irresoluble "
        "entry.satisfied debe ser false: %r" % entry_scalar)
    assert "selection-coverage" in json.dumps(entry_scalar), (
        "017-001 T3 bloqueante review-T3-002: la entrada bloqueada debe "
        "enumerar el check selection-coverage: %r" % entry_scalar)
    assert_selection_coverage_names_key(entry_scalar, "C-R")
    assert_markdown(out_scalar, "entry.md")


# Hallazgo opcional review-T3 — residuo exterior contra resolucion de 1 s.
# PC-6 (residual con alcance, signo y diagnostico honesto), INV-6.
def test_reconcile_exterior_residual_uses_declared_one_second_resolution(tmp_path):
    """Sin este test, el usuario ve como anomalia una diferencia de -0.5 s que
    el propio reloj exterior (resolucion declarada 1 s) no permite resolver."""
    assert CLI.is_file(), "017-001 T3: falta el CLI canonico scripts/cdad-suite.py"
    node = "test_sample.py::test_a"
    # R_exterior = T_exterior - T_pytest; T_pytest = 5.0 en ambos casos y
    # R_pytest = +4.0 (positivo), de modo que un residual-sign solo puede
    # venir del exterior.
    attempt_half = write_attempt(
        tmp_path / "attempt-half", phases=[phase_row(node, "call", 1.0)],
        operations=[], pytest_wall_s=5.0, started_at=1000.0,
        finished_at=1004.5)
    out_half = tmp_path / "out-half"
    rc, _, err = run_reconcile(attempt_half, out_half)
    assert rc == 0, (
        "017-001 T3 opcional (PC-6): reconcile con R_exterior=-0.5 s debe "
        "producirse (rc 0); salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    payload_half = read_json(out_half / "reconciliation.json")
    assert "residual-sign" not in diagnostics_of(payload_half), (
        "017-001 T3 opcional: un R_exterior de -0.5 s esta dentro de la "
        "resolucion declarada de 1 s y no debe diagnosticarse como "
        "residual-sign: %r" % payload_half)
    assert_markdown(out_half, "reconciliation.md")

    attempt_over = write_attempt(
        tmp_path / "attempt-over", phases=[phase_row(node, "call", 1.0)],
        operations=[], pytest_wall_s=5.0, started_at=1000.0,
        finished_at=1003.5)
    out_over = tmp_path / "out-over"
    rc, _, err = run_reconcile(attempt_over, out_over)
    assert rc == 0, (
        "017-001 T3 opcional (PC-6): reconcile con R_exterior=-1.5 s debe "
        "producirse (rc 0); salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    payload_over = read_json(out_over / "reconciliation.json")
    assert "residual-sign" in diagnostics_of(payload_over), (
        "017-001 T3 opcional: un R_exterior de -1.5 s supera la resolucion "
        "declarada de 1 s y si debe diagnosticarse como residual-sign: %r"
        % payload_over)
    assert_markdown(out_over, "reconciliation.md")


# --------------------------------------------------------------------------
# T4 — contraste de alcance de la corrida base (seleccion completa). PC-5
# (el informe contrasta captura y alcance comprometido en la base:
# distingue un recorrido no ejercitado de un fallo de captura, spec
# §4.4) con PC-6 (conciliacion reproducible con diagnostico) e INV-6
# (ausencia no es cero; incompleto no es base valida).
#
# Ni los doce tests anteriores ni el contrato operativo de T3 cubren este
# contraste: T3 compara conteos `expected` contra lo observado y deja la
# cobertura como "unavailable"/"available" sin distinguir seleccion
# completa; el registro real ya declara por operacion
# `expected_in_full_run` (true/false) y `expected_in_full_run_reason`
# (performance/operation-scope.json), pero reconcile lo ignora hoy.
# --------------------------------------------------------------------------

def _write_full_run_attempt(attempt_dir, *, phases, operations, nodeids,
                            pytest_wall_s=5.0, started_at=1000.0,
                            finished_at=1008.0):
    """Intento sintetico de seleccion completa: attempt.json con
    selection.kind == "all" (la seleccion que la base declara)."""
    attempt_dir = write_attempt(
        attempt_dir, phases=phases, operations=operations,
        selection=list(nodeids), pytest_wall_s=pytest_wall_s,
        started_at=started_at, finished_at=finished_at)
    doc = Path(attempt_dir) / "attempt.json"
    payload = json.loads(doc.read_text(encoding="utf-8"))
    payload["selection"] = {"kind": "all", "nodeids": list(nodeids)}
    doc.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return Path(attempt_dir)


def _write_full_run_register(path, *, nodeids, declared):
    """Registro sintetico minimo con la forma del registro real
    (performance/operation-scope.json): por operacion,
    expected_in_full_run (true/false) y expected_in_full_run_reason.
    declared: {op_id: (expected_in_full_run, reason)}."""
    families = [{
        "family": "synthetic-full-run-scope",
        "selection": "FULL",
        "state": "comprometida",
        "classification": "preparacion",
        "context": "test-call",
        "operations": [
            {"id": op_id, "expected_in_full_run": flag,
             "expected_in_full_run_reason": reason}
            for op_id, (flag, reason) in declared.items()
        ],
    }]
    scope = {
        "schema_version": 1,
        "status": "calibrated",
        "calibrated": True,
        "feature_id": "017-001-suite-performance",
        "selections": {"FULL": {"existing": True, "fresh_process": True,
                                "nodeids": list(nodeids)}},
        "families": families,
        "volume_observations": {
            "synthetic-volume": {
                "unknown_component": {
                    "decision_rule": "retain-in-remainder"},
            },
        },
    }
    path = Path(path)
    path.write_text(json.dumps(scope, indent=2), encoding="utf-8")
    return path


def _full_coverage(payload):
    register = payload.get("register")
    assert isinstance(register, dict), (
        "017-001 T4 (PC-5): reconciliation.json no trae bloque de registro; "
        "sin el no hay contraste entre alcance declarado y observado: %r"
        % payload)
    for key in ("coverage", "cobertura", "alcance"):
        coverage = register.get(key)
        if isinstance(coverage, dict):
            return coverage
    raise AssertionError(
        "017-001 T4 (PC-5): el bloque de registro no trae cobertura contra "
        "el registro; sin ella la base no contrasta alcance: %r" % register)


def _full_coverage_status(coverage):
    for key in ("status", "estado"):
        value = coverage.get(key)
        if isinstance(value, str):
            return value
    raise AssertionError(
        "017-001 T4 (PC-5): la cobertura no trae estado; sin el no se sabe "
        "si el contraste es de seleccion completa: %r" % coverage)


_UNEXERCISED_HINTS = ("unexerc", "not_exerc", "not-exerc", "no_ejerc",
                      "sin_ejerc", "sin-ejerc", "absent", "ausente",
                      "pending", "skipped", "omit")


def _coverage_names_as_unexercised(coverage, op_id):
    """True si la cobertura informa op_id como no ejercitada (recorrido
    declarado pero sin observaciones), bajo una clave que indica
    no-ejercicio. El contrato fija el concepto, no la clave."""
    found = False

    def visit(node, hinted):
        nonlocal found
        if isinstance(node, dict):
            for key, value in node.items():
                key_hint = any(h in str(key).lower()
                               for h in _UNEXERCISED_HINTS)
                visit(value, hinted or key_hint)
        elif isinstance(node, list):
            for item in node:
                visit(item, hinted)
        elif isinstance(node, str):
            if hinted and node == op_id:
                found = True

    visit(coverage, False)
    return found


def test_full_selection_scope_contrast_distinguishes_unexercised_from_missing(tmp_path):
    """Sin este test, el usuario recibe en la corrida base (seleccion
    completa) una cobertura que no distingue un recorrido no ejercitado de
    un fallo de captura: una operacion comprometida ausente pasa en
    silencio y la base puede consumirse sobre captura rota (PC-5/PC-6,
    INV-6, spec §4.4)."""
    assert CLI.is_file(), "017-001 T4: falta el CLI canonico scripts/cdad-suite.py"
    node = "test_sample.py::test_full_scope"

    # Caso A — declarada expected_in_full_run=false, cero observaciones:
    # se informa como no ejercitada, sin diagnostico de faltante.
    attempt_a = _write_full_run_attempt(
        tmp_path / "attempt-a", phases=[phase_row(node, "call", 1.0)],
        operations=[], nodeids=[node])
    register_a = _write_full_run_register(
        tmp_path / "register-a.json", nodeids=[node],
        declared={"synthetic.cold-copy": (
            False, "synthetic-cold-branch-not-taken-in-base")})
    out_a = tmp_path / "out-a"
    rc, _, err = run_reconcile(attempt_a, out_a, register=register_a)
    assert rc == 0, (
        "017-001 T4 caso A (PC-5): reconcile de seleccion completa se "
        "produce (rc 0); salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    payload_a = read_json(out_a / "reconciliation.json")
    coverage_a = _full_coverage(payload_a)
    assert _full_coverage_status(coverage_a) == "all-selection", (
        "017-001 T4 caso A (PC-5): con seleccion completa el contraste de "
        "alcance de la base debe informar coverage.status 'all-selection'; "
        "fue %r (contraste de alcance no disponible)" % (coverage_a,))
    assert "missing-operation-vs-register" not in diagnostics_of(payload_a), (
        "017-001 T4 caso A (PC-5/INV-6): lo declarado "
        "expected_in_full_run=false y no observado no es un faltante: %r"
        % payload_a)
    assert _coverage_names_as_unexercised(coverage_a, "synthetic.cold-copy"), (
        "017-001 T4 caso A (PC-5/INV-6): la operacion declarada "
        "expected_in_full_run=false con cero observaciones debe informarse "
        "como no ejercitada: %r" % (coverage_a,))
    assert_markdown(out_a, "reconciliation.md")

    # Caso B — declarada expected_in_full_run=true, cero observaciones:
    # missing-operation-vs-register y medicion incompleta/bloqueada.
    attempt_b = _write_full_run_attempt(
        tmp_path / "attempt-b", phases=[phase_row(node, "call", 1.0)],
        operations=[], nodeids=[node])
    register_b = _write_full_run_register(
        tmp_path / "register-b.json", nodeids=[node],
        declared={"synthetic.committed-prep": (
            True, "synthetic-committed-preparation")})
    out_b = tmp_path / "out-b"
    rc, _, err = run_reconcile(attempt_b, out_b, register=register_b)
    assert rc == 0, (
        "017-001 T4 caso B (PC-5): reconcile de seleccion completa se "
        "produce aunque haya faltante (rc 0); salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    payload_b = read_json(out_b / "reconciliation.json")
    coverage_b = _full_coverage(payload_b)
    assert _full_coverage_status(coverage_b) == "all-selection", (
        "017-001 T4 caso B (PC-5): con seleccion completa el contraste de "
        "alcance de la base debe informar coverage.status 'all-selection'; "
        "fue %r (contraste de alcance no disponible)" % (coverage_b,))
    assert "missing-operation-vs-register" in diagnostics_of(payload_b), (
        "017-001 T4 caso B (PC-5/INV-6): la operacion declarada "
        "expected_in_full_run=true con cero observaciones debe "
        "diagnosticar missing-operation-vs-register: %r" % payload_b)
    assert "synthetic.committed-prep" in json.dumps(payload_b), (
        "017-001 T4 caso B: el diagnostico debe nombrar la operacion "
        "ausente synthetic.committed-prep: %r" % payload_b)
    blob_b = json.dumps(payload_b).lower()
    assert ("incomplete" in blob_b or "blocked" in blob_b
            or "bloque" in blob_b), (
        "017-001 T4 caso B (INV-6): si falta un intervalo que debia "
        "emitirse, la medicion queda incompleta/bloqueada, no completa: %r"
        % payload_b)
    assert_markdown(out_b, "reconciliation.md")

    # Caso C — observada no declarada, y declarada false pero observada.
    attempt_c = _write_full_run_attempt(
        tmp_path / "attempt-c", phases=[phase_row(node, "call", 1.0)],
        operations=[
            op_row("synthetic.cold-seen", "c1", None, node, "call", "test",
                   10.0, 10.5),
            op_row("synthetic.ghost-op", "g1", None, node, "call", "test",
                   11.0, 11.25),
        ], nodeids=[node])
    register_c = _write_full_run_register(
        tmp_path / "register-c.json", nodeids=[node],
        declared={"synthetic.cold-seen": (
            False, "synthetic-cold-branch-taken-in-this-run")})
    out_c = tmp_path / "out-c"
    rc, _, err = run_reconcile(attempt_c, out_c, register=register_c)
    assert rc == 0, (
        "017-001 T4 caso C (PC-5): reconcile de seleccion completa se "
        "produce (rc 0); salio %r: %s"
        % (rc, err.decode("utf-8", "replace")))
    payload_c = read_json(out_c / "reconciliation.json")
    coverage_c = _full_coverage(payload_c)
    assert _full_coverage_status(coverage_c) == "all-selection", (
        "017-001 T4 caso C (PC-5): con seleccion completa el contraste de "
        "alcance de la base debe informar coverage.status 'all-selection'; "
        "fue %r (contraste de alcance no disponible)" % (coverage_c,))
    codes_c = diagnostics_of(payload_c)
    assert "operation-without-register-entry" in codes_c, (
        "017-001 T4 caso C (PC-5): la operacion observada que el registro no "
        "declara debe diagnosticar operation-without-register-entry: %r"
        % payload_c)
    assert "synthetic.ghost-op" in json.dumps(payload_c), (
        "017-001 T4 caso C: el diagnostico debe nombrar la operacion no "
        "declarada synthetic.ghost-op: %r" % payload_c)
    assert "missing-operation-vs-register" not in codes_c, (
        "017-001 T4 caso C (PC-5/INV-6): lo declarado "
        "expected_in_full_run=false pero observado no es un faltante: %r"
        % payload_c)
    raw_c = payload_c.get("diagnostics", payload_c.get("diagnosticos", []))
    assert not any("synthetic.cold-seen" in json.dumps(item)
                   for item in raw_c), (
        "017-001 T4 caso C (PC-5): la operacion declarada false pero "
        "observada no produce diagnostico: %r" % payload_c)
    assert_markdown(out_c, "reconciliation.md")


# --------------------------------------------------------------------------
# T4 — identidad contable a nivel de corrida del agregador (review-T4
# hallazgo 2, reencuadrado). PC-6 (conciliacion reproducible desde la
# evidencia cruda, con residual y diagnostico) con INV-5 (un intervalo
# contribuye una sola vez) y spec §4.4 (para la corrida: T_pytest,
# R_pytest = T_pytest - suma(S_test); los identificados dentro de los
# residuos se desglosan sin volver a sumarlos; el informe declara
# resolucion y redondeo).
#
# Ninguno de los trece tests anteriores cubre el triple a nivel de
# corrida: el caso 1 usa valores amigos de 1 decimal (1.3/2.0), el caso 5
# exige presencia de residuos con signo pero no los totales de
# preparacion y resto ni su identidad con sum_S_test, y el resto de
# casos cubre anidamiento, solapamiento, compartidas, residuos,
# entrada y determinismo. Con 2034 tests reales la suma de los valores
# por test redondeados a 3 decimales difiere del total en 0.309 s, de
# modo que la identidad no se puede reconstruir con las cifras
# publicadas.
# --------------------------------------------------------------------------

def test_run_level_accounting_identity_with_rounding_bound(tmp_path):
    """Sin este test, el usuario recibe una conciliacion cuya corrida no
    publica totales de preparacion y resto a 3 decimales calculados desde
    los valores sin redondear, y ningun documento declara la cota de
    redondeo al sumar valores por test publicados: con 200 tests de
    0.1234 s la suma publicada por test (200x0.123) difiere del total en
    0.08 s —en la base real, 0.309 s con 2034 tests— y un redondeo
    silencioso pasa por conciliacion valida (PC-6/INV-5, spec §4.4)."""
    assert CLI.is_file(), "017-001 T4: falta el CLI canonico scripts/cdad-suite.py"

    def run_total(run, aliases, canonical):
        for key in aliases:
            if key in run and isinstance(run[key], (int, float)):
                return float(run[key])
        raise AssertionError(
            "017-001 T4 hallazgo-2 (PC-6): el bloque run no publica %s "
            "(aceptados %r); sin esos totales la identidad contable no se "
            "puede reconstruir con las cifras publicadas: %r"
            % (canonical, aliases, run))

    # Intento sintetico de varios cientos de tests con milesimas
    # significativas: cada S_test = 0.1234, cada preparacion = 0.0234,
    # cada resto = 0.1000. Sumas sin redondear: total 24.68,
    # preparacion 4.68, resto 20.0; T_pytest = 30.0 -> R_pytest = 5.32.
    n_tests = 200
    dur = 0.1234
    prep = 0.0234
    phases = [phase_row("test_sample.py::test_%04d" % i, "call", dur)
              for i in range(n_tests)]
    operations = []
    start = 100.0
    for i in range(n_tests):
        nodeid = "test_sample.py::test_%04d" % i
        operations.append(op_row("prep.op", "op-%d" % i, None, nodeid,
                                 "call", "test", start, start + prep))
        start += 1.0
    attempt = write_attempt(tmp_path / "attempt", phases=phases,
                            operations=operations, pytest_wall_s=30.0,
                            started_at=1000.0, finished_at=1040.0)
    out = tmp_path / "out"
    rc, _, err = run_reconcile(attempt, out)
    assert rc == 0, (
        "017-001 T4 hallazgo-2 (PC-6): reconcile debe salir 0 con intento "
        "completo; salio %r: %s" % (rc, err.decode("utf-8", "replace")))
    payload = read_json(out / "reconciliation.json")
    run = run_block(payload)

    run_sum = run_total(run, ("sum_S_test", "sum_s_test"), "sum_S_test")
    run_prep = run_total(
        run, ("preparation_s", "preparation", "attributed_s", "attributed",
              "preparation_total_s"), "preparation_s")
    run_rem = run_total(
        run, ("remainder_s", "remainder", "resto"), "remainder_s")

    exp_sum = round(n_tests * dur, 3)
    exp_prep = round(n_tests * prep, 3)
    exp_rem = round(n_tests * (dur - prep), 3)
    assert abs(run_sum - exp_sum) <= 1e-9, (
        "017-001 T4 hallazgo-2 (PC-6): sum_S_test debe calcularse desde los "
        "valores sin redondear (200x0.1234 -> 24.68 a 3 decimales), fue %r"
        % run)
    assert abs(run_prep - exp_prep) <= 1e-9, (
        "017-001 T4 hallazgo-2 (PC-6): preparation_s debe calcularse desde "
        "los valores sin redondear (200x0.0234 -> 4.68 a 3 decimales), "
        "fue %r" % run)
    assert abs(run_rem - exp_rem) <= 1e-9, (
        "017-001 T4 hallazgo-2 (PC-6): remainder_s debe calcularse desde "
        "los valores sin redondear (200x0.1000 -> 20.0 a 3 decimales), "
        "fue %r" % run)
    for value, name in ((run_sum, "sum_S_test"), (run_prep, "preparation_s"),
                        (run_rem, "remainder_s")):
        assert abs(value * 1000 - round(value * 1000)) <= 1e-6, (
            "017-001 T4 hallazgo-2 (PC-6): %s debe publicarse a 3 decimales "
            "(multiplo de 0.001), fue %r" % (name, run))
    assert abs((run_prep + run_rem) - run_sum) <= TOL, (
        "017-001 T4 hallazgo-2 (PC-6/INV-5): preparation_s + remainder_s "
        "debe igualar sum_S_test con tolerancia 1e-3; fue %r" % run)
    r_pytest = run_total(
        run, ("R_pytest", "r_pytest", "residual_pytest",
              "residuo_corrida"), "R_pytest")
    t_pytest = run_total(
        run, ("T_pytest", "t_pytest", "pytest_wall_s",
              "pytest_total_s"), "T_pytest")
    assert abs((run_sum + r_pytest) - t_pytest) <= TOL, (
        "017-001 T4 hallazgo-2 (PC-6): sum_S_test + R_pytest debe igualar "
        "T_pytest con tolerancia 1e-3; fue %r" % run)

    text = assert_markdown(out, "reconciliation.md")
    blob = (json.dumps(payload) + "\n" + text).lower()
    has_round = "round" in blob or "redond" in blob
    has_bound = ("cota" in blob or "bound" in blob or "toler" in blob)
    assert has_round and has_bound, (
        "017-001 T4 hallazgo-2 (PC-6): el documento debe declarar la cota "
        "de redondeo al sumar valores por test publicados (redondeo/cota); "
        "sin ella la deriva de 0.08 s en este sintetico (0.309 s en la base "
        "real) es indistinguible de una discrepancia contable")
