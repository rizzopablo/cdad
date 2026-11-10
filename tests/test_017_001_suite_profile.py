"""017-001 T1 RED: XML y fases de `close` sin cambiar el cierre (spec §§4.2–4.3).

Oráculo: contrato aprobado `docs/specs/017-001-suite-performance/spec.md`
§§4.2–4.3 (PC-1 parte resultados/fases, PC-2), no la implementación: `close`
se usa como caja negra por CLI sobre repos sintéticos, con los patrones de
repos sintéticos y CLIs grabadoras de `tests/test_008_002_suite_evidence.py`
y `tests/test_008_005_ci_gate.py` (conftest grabadora que cuenta hijos
pytest). Ninguna aserción importa el producto.

Sin umbrales temporales como oráculo (spec §4.2; convención 11): las
duraciones solo se comprueban por presencia, tipo y monotonía gruesa
(>= 0); nunca igualdad exacta, techos ni bound==deadline.
"""

import hashlib
import json
from pathlib import Path
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

import pytest


CLI = Path(__file__).resolve().parents[1] / "scripts" / "cdad-suite.py"

SKIP_REASON = "intentional opt-in skip"

SENTINEL_CONFTEST = '''\
import os

_sentinel = os.environ.get("SUITE_PROFILE_PYTEST_SENTINEL")
if _sentinel:
    with open(_sentinel, "a", encoding="utf-8") as _handle:
        _handle.write("pytest-child\\n")
'''

SAMPLE = (
    "import time\n"
    "import pytest\n"
    "def test_pass(): pass\n"
    "def test_fail(): assert False, 'profile deliberate failure'\n"
    "@pytest.mark.skip(reason='intentional opt-in skip')\n"
    "def test_skip(): pass\n"
    "def test_wait(): time.sleep(60)\n"
    "def test_extra(): pass\n"
)

PHASE_WHEN = {"setup", "call", "teardown"}
PHASE_OUTCOMES = {"passed", "failed", "skipped"}


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    assert CLI.is_file(), "017-001 R1-R5: el CLI canonico scripts/cdad-suite.py no existe"
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.invalid"],
                   check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    (tmp_path / "conftest.py").write_text(SENTINEL_CONFTEST, encoding="utf-8")
    (tmp_path / "test_sample.py").write_text(SAMPLE, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "conftest.py", "test_sample.py"],
                   check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "fixture"], check=True)
    (tmp_path / "evidence").mkdir()
    monkeypatch.setenv("SUITE_PROFILE_PYTEST_SENTINEL", str(tmp_path / "pytest-children.log"))
    return tmp_path


def start_close(workspace, selection, label):
    nodeids = workspace / (label + ".txt")
    nodeids.write_text("\n".join("test_sample.py::" + name for name in selection) + "\n",
                       encoding="utf-8")
    return subprocess.Popen(
        [sys.executable, str(CLI), "close", "--evidence-root", str(workspace / "evidence"),
         "--nodeids", str(nodeids)],
        cwd=workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
    )


def run_close(workspace, selection, label, timeout=180):
    process = start_close(workspace, selection, label)
    out, err = process.communicate(timeout=timeout)
    return process.returncode, out, err


def attempts(workspace):
    return sorted(p for p in (workspace / "evidence").iterdir() if p.is_dir())


def only_attempt(workspace):
    found = attempts(workspace)
    assert len(found) == 1, (
        "017-001: un close debe reservar exactamente un intento; hay %d" % len(found))
    return found[0]


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def attempt_data(attempt):
    path = attempt / "attempt.json"
    assert path.is_file(), "017-001: el intento no dejo attempt.json"
    return json.loads(path.read_text(encoding="utf-8"))


def profile_data(attempt):
    path = attempt / "profile.json"
    assert path.is_file(), (
        "017-001 T1 (PC-1 parte resultados/fases): el intento no conserva profile.json; "
        "sin este artefacto el responsable no puede recuperar fases ni argv medido")
    return json.loads(path.read_text(encoding="utf-8"))


def xml_cases(attempt):
    path = attempt / "pytest.xml"
    assert path.is_file(), (
        "017-001 T1 (PC-1 parte resultados/fases): el intento no conserva pytest.xml; "
        "sin este artefacto el responsable no puede contrastar nodeids con resultados")
    return list(ET.parse(str(path)).getroot().iter("testcase"))


# C1+R1 — XML y fases corresponden a lo realmente emitido; ausente ≠ cero.
# PC-1 (parte resultados/fases), INV-1, INV-6. Check 1 del plan T1.
def test_close_emits_xml_and_phases_matching_emitted_selection(workspace):
    """Sin este test, el usuario recibe XML/perfil que nombran otros tests o
    inventan fases de duración cero y calibra sobre ficción."""
    selection = ["test_pass", "test_fail", "test_skip"]
    rc, _, _ = run_close(workspace, selection, "r1")
    assert rc != 0, "017-001 R1: la seleccion con test_fail debe cerrar con rc != 0"
    attempt = only_attempt(workspace)

    cases = xml_cases(attempt)
    names = {case.get("name") for case in cases}
    assert {"test_pass", "test_fail", "test_skip"} <= names, (
        "017-001 R1: pytest.xml no cubre los nodeids realmente emitidos: %r" % sorted(names))
    for unselected in ("test_extra", "test_wait"):
        assert unselected not in names, (
            "017-001 R1: pytest.xml nombra un test no seleccionado (%s)" % unselected)
    by_name = {case.get("name"): case for case in cases}
    assert by_name["test_fail"].find("failure") is not None or \
        by_name["test_fail"].find("error") is not None, (
        "017-001 R1: pytest.xml no registra el fallo de test_fail")
    skipped = by_name["test_skip"].find("skipped")
    assert skipped is not None and SKIP_REASON in (skipped.get("message") or ""), (
        "017-001 R1: pytest.xml no conserva el motivo completo del skip")

    profile = profile_data(attempt)
    phases = profile.get("phases")
    assert isinstance(phases, list) and phases, (
        "017-001 R1: profile.json no trae fases emitidas")
    selected = {"test_sample.py::" + name for name in selection}
    seen = set()
    for row in phases:
        assert {"nodeid", "when", "duration_s", "outcome"} <= row.keys(), (
            "017-001 R1: fila de fase sin identidad completa: %r" % row)
        assert row["nodeid"] in selected, (
            "017-001 R1: fase de un nodeid no emitido (%s): ausente debe seguir ausente, "
            "no aparecer como fila inventada" % row["nodeid"])
        assert row["when"] in PHASE_WHEN, (
            "017-001 R1: fase con when fuera de setup/call/teardown: %r" % row["when"])
        assert isinstance(row["duration_s"], (int, float)) and row["duration_s"] >= 0, (
            "017-001 R1: duration_s no es una duracion observada >= 0: %r" % row)
        assert row["outcome"] in PHASE_OUTCOMES, (
            "017-001 R1: outcome fuera de passed/failed/skipped: %r" % row)
        seen.add((row["nodeid"], row["when"]))
    for nodeid in selected:
        assert any(n == nodeid for n, _ in seen), (
            "017-001 R1: el nodeid emitido %s no tiene fases registradas" % nodeid)
    for ghost in ("test_sample.py::test_extra", "test_sample.py::test_wait"):
        assert not any(n == ghost for n, _ in seen), (
            "017-001 R1: fase no ejecutada (%s) presente como fila: una ausencia no es "
            "una duracion cero" % ghost)
        assert not any(n == ghost and d == 0 for n, d in
                       ((r["nodeid"], r["duration_s"]) for r in phases)), (
            "017-001 R1: fase ausente suplantada por duration_s == 0 para %s" % ghost)


# C2+R2 — argv y artefactos recuperables desde el intento reservado;
# sucesivos no sobrescriben lo nuevo. PC-1 (parte), PC-2 (reserva), INV-1.
def test_attempt_preserves_argv_and_new_artifacts_across_attempts(workspace):
    """Sin este test, el usuario pierde el XML/perfil del primer intento o no
    puede reconstruir el comando medido."""
    assert run_close(workspace, ["test_pass"], "first")[0] == 0
    first, = attempts(workspace)
    before = hashes(first)
    assert run_close(workspace, ["test_skip"], "second")[0] == 0
    after = attempts(workspace)
    assert len(after) == 2 and first in after, (
        "017-001 R2: dos close sucesivos deben dejar dos intentos reservados")
    assert hashes(first) == before, (
        "017-001 R2: el segundo intento sobrescribio evidencia del primero")

    for attempt, selected in ((after[0], "test_pass"), (after[1], "test_skip")):
        profile = profile_data(attempt)
        argv = profile.get("pytest_argv")
        assert isinstance(argv, list) and argv, (
            "017-001 R2: profile.json no conserva el argv efectivo del hijo")
        assert "test_sample" in " ".join(str(token) for token in argv), (
            "017-001 R2: pytest_argv no refleja la seleccion medida: %r" % argv)
        xml_cases(attempt)
        record = (attempt / "attempt.json").read_text(encoding="utf-8")
        assert "pytest.xml" in record and "profile.json" in record, (
            "017-001 R2: el intento no referencia sus artefactos nuevos; no son "
            "recuperables desde el intento reservado")


# C3+R3 — conservación de fallos/skips/interrupciones con instrumentación.
# PC-2, INV-6. Check 3 del plan T1 (faceta nueva sobre la protección existente).
def test_profile_preserves_failures_skips_and_interruptions_without_substituting_rc(workspace):
    """Sin este test, la instrumentación puede enmascarar un fallo, un skip o
    una interrupción, o blanquear un rojo contractual con un supuesto éxito."""
    rc, _, _ = run_close(workspace, ["test_fail"], "fails")
    assert rc != 0
    attempt = only_attempt(workspace)
    data = attempt_data(attempt)
    assert data["rc"] == rc, (
        "017-001 R3: el intento no propaga el rc contractual del fallo")
    assert any((case.get("name") == "test_fail")
               and (case.find("failure") is not None or case.find("error") is not None)
               for case in xml_cases(attempt)), (
        "017-001 R3: pytest.xml no nombra el fallo con la instrumentación activa")
    profile_data(attempt)

    rc, _, _ = run_close(workspace, ["test_skip"], "skips")
    assert rc == 0
    attempts_now = attempts(workspace)
    assert len(attempts_now) == 2
    skip_attempt = attempts_now[1]
    summary = attempt_data(skip_attempt).get("pytest_summary", {})
    assert any("test_skip" in skip.get("nodeid", "")
               and SKIP_REASON in skip.get("reason", "")
               for skip in summary.get("skips", [])), (
        "017-001 R3: el resumen no conserva el motivo completo del skip")
    assert any((case.get("name") == "test_skip") and (case.find("skipped") is not None)
               for case in xml_cases(skip_attempt)), (
        "017-001 R3: pytest.xml no registra el skip con la instrumentación activa")
    profile_data(skip_attempt)

    process = start_close(workspace, ["test_wait"], "interrupted")
    try:
        deadline = time.monotonic() + 20
        evidence = None
        while time.monotonic() < deadline:
            found = [p for p in attempts(workspace) if (p / "attempt.json").is_file()]
            if len(found) == 3:
                evidence = found[2]
                break
            assert process.poll() is None, "close salio antes de registrar el intento en curso"
            time.sleep(0.05)
        assert evidence is not None, "close no registro el intento en curso"
        import os as _os
        _os.killpg(process.pid, signal.SIGKILL)
        process.communicate(timeout=60)
        data = json.loads((evidence / "attempt.json").read_text(encoding="utf-8"))
        assert data["state"] in {"running", "interrupted"}, (
            "017-001 R3: el intento interrumpido no quedo como running/interrupted: %r"
            % data["state"])
        assert data["rc"] is None or data["rc"] != 0, (
            "017-001 R3: la interrupcion quedo registrada como exito")
        profile_path = evidence / "profile.json"
        if profile_path.is_file():
            payload = json.loads(profile_path.read_text(encoding="utf-8"))
            assert payload.get("status") == "incomplete", (
                "017-001 R3: un perfil parcial de un intento interrumpido no puede "
                "presentarse como medicion completa")
    finally:
        if process.poll() is None:
            import os as _os
            _os.killpg(process.pid, signal.SIGKILL)
            process.communicate()


# C4+R4 — el diagnóstico distingue medición incompleta de resultado
# contractual; solo-fases no acredita base. PC-1 (parte), INV-6.
def test_incomplete_measurement_is_diagnosed_not_presented_as_contract(workspace):
    """Sin este test, el usuario confunde fases parciales con medición válida
    y consume la base sobre evidencia rota."""
    rc, _, _ = run_close(workspace, ["test_pass", "test_skip"], "clean")
    assert rc == 0
    attempt = only_attempt(workspace)
    profile = profile_data(attempt)
    assert profile.get("status") in {"complete", "incomplete"}, (
        "017-001 R4: profile.json no declara status complete/incomplete")
    assert "diagnosis" in profile, (
        "017-001 R4: profile.json no trae diagnosis para la medicion incompleta")
    if profile["status"] == "complete":
        assert not profile.get("diagnosis"), (
            "017-001 R4: una medicion completa no debe traer diagnostico pendiente")
    assert attempt_data(attempt)["rc"] == rc, (
        "017-001 R4: el perfil sustituyo el rc contractual de pytest")
    assert profile.get("status") == "complete", (
        "017-001 R4: una seleccion limpia sin interrupciones debe medir complete; "
        "si falta captura, la base queda bloqueada hasta recalibrar")

    process = start_close(workspace, ["test_wait"], "broken")
    try:
        deadline = time.monotonic() + 20
        evidence = None
        while time.monotonic() < deadline:
            found = [p for p in attempts(workspace) if (p / "attempt.json").is_file()]
            if len(found) == 2:
                evidence = found[1]
                break
            assert process.poll() is None, "close salio antes de registrar el intento en curso"
            time.sleep(0.05)
        assert evidence is not None, "close no registro el intento en curso"
        import os as _os
        _os.killpg(process.pid, signal.SIGKILL)
        process.communicate(timeout=60)
        data = json.loads((evidence / "attempt.json").read_text(encoding="utf-8"))
        assert data["rc"] is None or data["rc"] != 0, (
            "017-001 R4: la interrupcion quedo registrada como exito contractual")
        profile_path = evidence / "profile.json"
        assert (not profile_path.is_file()) or (
            json.loads(profile_path.read_text(encoding="utf-8")).get("status")
            == "incomplete"), (
            "017-001 R4: la medicion interrumpida debe quedar ausente o diagnosticada "
            "como incomplete, nunca como resultado contractual valido")
        if profile_path.is_file():
            payload = json.loads(profile_path.read_text(encoding="utf-8"))
            assert payload.get("diagnosis"), (
                "017-001 R4: una medicion incomplete sin diagnosis no distingue la "
                "falla de captura del resultado de pytest")
    finally:
        if process.poll() is None:
            import os as _os
            _os.killpg(process.pid, signal.SIGKILL)
            process.communicate()


# C5+R5 — el close instrumentado invoca una sola corrida pytest y registra su
# pared. PC-2 (§4.3 sin 2º pytest), INV-7. A nivel gate se reutiliza el PC-1
# existente de test_008_005_ci_gate.py sin duplicarlo.
def test_instrumented_close_runs_single_pytest_and_records_wall_argv(
        workspace, monkeypatch):
    """Sin este test, el gate puede pagar dos suites o acreditar una ruta
    distinta de la medida."""
    monkeypatch.setenv("PYTEST_ADDOPTS", "-k test_nothing_matches_this --tb=no")
    rc, _, _ = run_close(workspace, ["test_pass", "test_skip"], "single")
    attempt = only_attempt(workspace)
    profile = profile_data(attempt)
    argv = profile.get("pytest_argv")
    assert isinstance(argv, list) and argv, (
        "017-001 R5: profile.json no conserva el argv efectivo del hijo pytest")
    wall = profile.get("pytest_wall_s")
    assert isinstance(wall, (int, float)) and wall >= 0, (
        "017-001 R5: profile.json no registra la pared del hijo como numero >= 0 "
        "(consistencia, no techo: sin igualdad exacta)")
    assert rc == 0, (
        "017-001 R5: PYTEST_ADDOPTS heredado altero la seleccion: la instrumentacion "
        "debe neutralizarlo segun §4.3 y correr lo seleccionado")
    summary = attempt_data(attempt).get("pytest_summary", {})
    assert (summary.get("passed"), summary.get("skipped")) == (1, 1), (
        "017-001 R5: con ADDOPTS hostil no corrio exactamente la seleccion: %r" % summary)
    sentinel = workspace / "pytest-children.log"
    assert sentinel.is_file(), (
        "017-001 R5: el hijo pytest no importo el conftest del repo sintetico; no se "
        "puede atribuir la corrida a una sola invocacion")
    assert sentinel.read_text(encoding="utf-8").splitlines() == ["pytest-child"], (
        "017-001 R5: el close instrumentado no ejecuto exactamente un hijo pytest")


# H1 (review-T1 §1) — una captura parcial no puede declararse completa.
# spec §§4.2-4.3, PC-2, INV-6. Trazada al hallazgo 1 y a PC-1 (parte)/PC-2.
def test_partial_phase_capture_is_incomplete_with_intact_rc(workspace):
    """Sin este test, el usuario consume un perfil incompleto creyendo que las
    fases y resultados estan integros (contrario a §4.3 e INV-6)."""
    shadow = (
        '"""Shadow roto: solo registra setup, pierde call/teardown."""\n'
        "import json, os, time\n"
        "_phases = []\n"
        "_start = None\n"
        "def pytest_sessionstart(session):\n"
        "    global _start\n"
        "    _start = time.monotonic()\n"
        "def pytest_runtest_logreport(report):\n"
        '    if report.when == "setup":\n'
        "        if report.passed:\n"
        '            outcome = \"passed\"\n'
        "        elif report.failed:\n"
        '            outcome = \"failed\"\n'
        "        else:\n"
        '            outcome = \"skipped\"\n'
        "        _phases.append({\"nodeid\": report.nodeid, \"when\": report.when, "
        "\"duration_s\": float(getattr(report, \"duration\", 0.0)), "
        "\"outcome\": outcome})\n"
        "def pytest_sessionfinish(session, exitstatus):\n"
        '    sink = os.environ.get(\"CDAD_SUITE_PHASE_SINK\")\n'
        "    if not sink:\n"
        "        return\n"
        "    payload = {\"schema_version\": 1, "
        "\"elapsed_s\": (time.monotonic() - _start) if _start else 0.1, "
        "\"pytest_exitstatus\": exitstatus, \"phases\": _phases}\n"
        '    with open(sink, \"w\", encoding=\"utf-8\") as _f:\n'
        "        json.dump(payload, _f)\n"
    )
    (workspace / "cdad_suite_observer.py").write_text(shadow, encoding="utf-8")
    rc, _, _ = run_close(workspace, ["test_pass"], "partial")
    assert rc == 0, (
        "017-001 H1: el hijo con test_pass debe cerrar con rc 0; si no, la induccion "
        "externa rompio el resultado contractual en vez de solo la captura")
    attempt = only_attempt(workspace)
    names = {case.get("name") for case in xml_cases(attempt)}
    assert "test_pass" in names, (
        "017-001 H1: pytest.xml no muestra que el hijo corrio test_pass; sin hijo "
        "corrido no hay inconsistencia XML/fases que exigir")
    profile = profile_data(attempt)
    phases = profile.get("phases") or []
    nodeid = "test_sample.py::test_pass"
    assert any(r.get("nodeid") == nodeid and r.get("when") == "setup" for r in phases), (
        "017-001 H1: la perdida inducida no dejo ni el setup; el medio externo no "
        "reprodujo la captura parcial (setup-si, call-no)")
    assert not any(r.get("nodeid") == nodeid and r.get("when") == "call" for r in phases), (
        "017-001 H1: el shadow no indujo la perdida de call; no se puede exigir el "
        "diagnostico de captura parcial sin perdida real")
    assert profile.get("status") == "incomplete", (
        "017-001 H1: una captura parcial (setup sin call, XML completo) se declaro "
        "%r; debe ser incomplete" % profile.get("status"))
    assert isinstance(profile.get("diagnosis"), str) and profile["diagnosis"].strip(), (
        "017-001 H1: la medicion incompleta quedo sin diagnosis accionable; no "
        "distingue la falla de captura del resultado de pytest")
    assert attempt_data(attempt)["rc"] == rc, (
        "017-001 H1: el diagnostico de captura incompleta altero el rc contractual")


# H2 (review-T1 §2) — un fallo al escribir el perfil no sustituye el resultado.
# spec §4.3, PC-2, INV-6. Trazada al hallazgo 2.
def test_profile_write_failure_preserves_pytest_rc(workspace):
    """Sin este test, un fallo de medicion cambia el resultado observable de
    close y oculta el rc real (contrario a §4.3 y PC-2)."""
    sample = workspace / "test_sample.py"
    sample.write_text(
        sample.read_text(encoding="utf-8")
        + "\ndef test_h2_slow():\n    import time\n    time.sleep(2)\n",
        encoding="utf-8")
    nodeids = workspace / "block.txt"
    nodeids.write_text("test_sample.py::test_h2_slow\n", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, str(CLI), "close", "--evidence-root", str(workspace / "evidence"),
         "--nodeids", str(nodeids)],
        cwd=workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        deadline = time.monotonic() + 20
        target = None
        while time.monotonic() < deadline:
            found = [p for p in attempts(workspace) if p.is_dir()]
            if found:
                target = found[0]
                break
            assert process.poll() is None, "close salio antes de reservar el intento"
            time.sleep(0.05)
        assert target is not None, "close no reservo el intento en curso"
        time.sleep(0.3)
        blocker = target / "profile.json"
        if not blocker.exists():
            blocker.mkdir()
        out, err = process.communicate(timeout=60)
        rc = process.returncode
        err_text = err.decode("utf-8", "replace")
        assert rc == 0, (
            "017-001 H2: el fallo de escritura de profile.json sustituyo el rc del "
            "hijo (rc=%r); debe conservar el rc contractual 0" % rc)
        data = attempt_data(target)
        assert data["state"] == "finished", (
            "017-001 H2: el intento quedo como %r tras el fallo de medicion; debe "
            "cerrar finished con el rc del hijo" % data["state"])
        assert data["rc"] == 0, (
            "017-001 H2: el intento no conserva el rc 0 del hijo tras el fallo de "
            "medicion (rc=%r)" % data["rc"])
        assert "Traceback" not in err_text, (
            "017-001 H2: el fallo de medicion propago una excepcion sin diagnostico "
            "contractual; debe manejarse con rc intacto y fallo diagnosticado")
        haystack = (target / "attempt.json").read_text(encoding="utf-8") + out.decode(
            "utf-8", "replace") + err_text
        assert "profile" in haystack.lower() or "medici" in haystack.lower(), (
            "017-001 H2: el fallo de escritura del perfil quedo sin diagnostico "
            "recuperable")
        profile_path = target / "profile.json"
        assert not (profile_path.is_file() and json.loads(
            profile_path.read_text(encoding="utf-8")).get("status") == "complete"), (
            "017-001 H2: con la escritura bloqueada no puede haber un perfil "
            "complete que sustituya la ausencia explicita")
    finally:
        if process.poll() is None:
            import os as _os
            _os.killpg(process.pid, signal.SIGKILL)
            process.communicate()


# review-T1-002 (rama skip) — un teardown perdido de un test omitido no puede
# declararse completo; el skip limpio sin call sigue completo.
# spec §§4.2-4.3, PC-2, INV-6. Trazada al hallazgo de review-T1-002.
def test_skipped_teardown_loss_is_incomplete_while_clean_skip_stays_complete(workspace):
    """Sin este test, el usuario consume una medicion parcial de un test omitido
    (setup skipped sin su teardown emitido) creyendola integra (contrario a
    §§4.2-4.3 e INV-6); sin el contrapeso, una correccion futura podria marcar
    todo skip como incompleto y bloquear la base sobre skips limpios."""
    # (b) Contrapeso primero: skip limpio sin call debe quedar complete.
    rc, _, _ = run_close(workspace, ["test_skip"], "skip-clean")
    assert rc == 0, (
        "017-001 skip-rama (b): la seleccion solo con test_skip debe cerrar con "
        "rc 0; si no, el hijo rompio el resultado contractual antes del oraculo")
    clean_attempts = attempts(workspace)
    assert len(clean_attempts) == 1, (
        "017-001 skip-rama (b): un close debe reservar exactamente un intento")
    clean_attempt = clean_attempts[0]
    clean_names = {case.get("name") for case in xml_cases(clean_attempt)}
    assert "test_skip" in clean_names, (
        "017-001 skip-rama (b): pytest.xml no muestra que el hijo corrio "
        "test_skip; sin hijo corrido no hay caso limpio que exigir")
    clean_profile = profile_data(clean_attempt)
    clean_phases = clean_profile.get("phases") or []
    skip_nodeid = "test_sample.py::test_skip"
    assert any(r.get("nodeid") == skip_nodeid and r.get("when") == "setup"
               for r in clean_phases), (
        "017-001 skip-rama (b): el skip limpio no dejo su setup; sin fases "
        "emitidas no hay contrapeso que conservar")
    assert any(r.get("nodeid") == skip_nodeid and r.get("when") == "teardown"
               for r in clean_phases), (
        "017-001 skip-rama (b): el skip limpio sin call no dejo su teardown "
        "emitido; sin ese teardown no hay caso limpio que exigir")
    assert clean_profile.get("status") == "complete", (
        "017-001 skip-rama (b): un skip limpio sin call (setup skipped + "
        "teardown emitido) se declaro %r; debe quedar complete"
        % clean_profile.get("status"))
    assert not clean_profile.get("diagnosis"), (
        "017-001 skip-rama (b): una medicion completa no debe traer "
        "diagnostico pendiente")
    assert attempt_data(clean_attempt)["rc"] == rc, (
        "017-001 skip-rama (b): el perfil altero el rc contractual del skip")

    # (a) Rama pendiente: sombra externa que conserva setup skipped y descarta
    # el teardown emitido; exige incomplete con diagnosis y rc intacto.
    shadow = (
        '"""Shadow roto: solo registra setup, pierde call/teardown."""\n'
        "import json, os, time\n"
        "_phases = []\n"
        "_start = None\n"
        "def pytest_sessionstart(session):\n"
        "    global _start\n"
        "    _start = time.monotonic()\n"
        "def pytest_runtest_logreport(report):\n"
        '    if report.when == "setup":\n'
        "        if report.passed:\n"
        '            outcome = "passed"\n'
        "        elif report.failed:\n"
        '            outcome = "failed"\n'
        "        else:\n"
        '            outcome = "skipped"\n'
        "        _phases.append({\"nodeid\": report.nodeid, \"when\": report.when, "
        "\"duration_s\": float(getattr(report, \"duration\", 0.0)), "
        "\"outcome\": outcome})\n"
        "def pytest_sessionfinish(session, exitstatus):\n"
        '    sink = os.environ.get("CDAD_SUITE_PHASE_SINK")\n'
        "    if not sink:\n"
        "        return\n"
        "    payload = {\"schema_version\": 1, "
        "\"elapsed_s\": (time.monotonic() - _start) if _start else 0.1, "
        "\"pytest_exitstatus\": exitstatus, \"phases\": _phases}\n"
        '    with open(sink, "w", encoding="utf-8") as _f:\n'
        "        json.dump(payload, _f)\n"
    )
    (workspace / "cdad_suite_observer.py").write_text(shadow, encoding="utf-8")
    rc, _, _ = run_close(workspace, ["test_skip"], "skip-partial")
    assert rc == 0, (
        "017-001 skip-rama (a): el hijo con test_skip debe cerrar con rc 0; si "
        "no, la induccion externa rompio el resultado contractual en vez de "
        "solo la captura")
    attempt = next(p for p in attempts(workspace) if p != clean_attempt)
    names = {case.get("name") for case in xml_cases(attempt)}
    assert "test_skip" in names, (
        "017-001 skip-rama (a): pytest.xml no muestra que el hijo corrio "
        "test_skip; sin hijo corrido no hay inconsistencia XML/fases que exigir")
    profile = profile_data(attempt)
    phases = profile.get("phases") or []
    assert any(r.get("nodeid") == skip_nodeid and r.get("when") == "setup"
               for r in phases), (
        "017-001 skip-rama (a): la perdida inducida no dejo ni el setup "
        "skipped; el medio externo no reprodujo la captura parcial "
        "(setup-si, teardown-no)")
    assert not any(r.get("nodeid") == skip_nodeid and r.get("when") == "teardown"
                   for r in phases), (
        "017-001 skip-rama (a): el shadow no indujo la perdida del teardown; "
        "no se puede exigir el diagnostico de captura parcial sin perdida real")
    assert profile.get("status") == "incomplete", (
        "017-001 skip-rama (a): una captura parcial de omitido (setup skipped "
        "sin su teardown emitido, XML completo) se declaro %r; debe ser "
        "incomplete" % profile.get("status"))
    assert isinstance(profile.get("diagnosis"), str) and profile["diagnosis"].strip(), (
        "017-001 skip-rama (a): la medicion incompleta quedo sin diagnosis "
        "accionable; no distingue la falla de captura del resultado de pytest")
    assert attempt_data(attempt)["rc"] == rc, (
        "017-001 skip-rama (a): el diagnostico de captura incompleta altero el "
        "rc contractual")
# H3 (review-T1 §3) — una interrupcion manejada conserva argv y tiempo.
# spec §§4.2-4.3, PC-2. Trazada al hallazgo 3 (SIGINT, no SIGKILL).
def test_handled_sigint_preserves_argv_and_wall(workspace):
    """Sin este test, el perfil de un intento interrumpido no permite
    reconstruir que comando se midio ni el tiempo transcurrido."""
    process = start_close(workspace, ["test_wait"], "handled")
    try:
        deadline = time.monotonic() + 20
        evidence = None
        while time.monotonic() < deadline:
            found = [p for p in attempts(workspace) if (p / "attempt.json").is_file()]
            if found:
                evidence = found[0]
                break
            assert process.poll() is None, "close salio antes de registrar el intento en curso"
            time.sleep(0.05)
        assert evidence is not None, "close no registro el intento en curso"
        time.sleep(1.0)
        import os as _os
        _os.killpg(process.pid, signal.SIGINT)
        _, _ = process.communicate(timeout=60)
        rc = process.returncode
        assert rc != 0, (
            "017-001 H3: la interrupcion manejada quedo con rc 0; debe ser no exitosa")
        data = json.loads((evidence / "attempt.json").read_text(encoding="utf-8"))
        assert data["state"] == "interrupted", (
            "017-001 H3: el intento interrumpido por SIGINT quedo como %r; debe ser "
            "interrupted" % data["state"])
        assert data["rc"] is None or data["rc"] != 0, (
            "017-001 H3: la interrupcion quedo registrada como exito")
        profile_path = evidence / "profile.json"
        assert profile_path.is_file(), (
            "017-001 H3: el intento interrumpido no dejo profile.json con argv y pared")
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
        assert payload.get("status") == "incomplete", (
            "017-001 H3: el perfil interrumpido se presento como %r; debe ser "
            "incomplete" % payload.get("status"))
        argv = payload.get("pytest_argv")
        assert isinstance(argv, list) and argv, (
            "017-001 H3: el perfil interrumpido perdio el argv efectivo del hijo "
            "(%r); debe conservarlo aunque hubo SIGINT" % argv)
        assert "test_wait" in " ".join(str(token) for token in argv), (
            "017-001 H3: pytest_argv no refleja la seleccion medida: %r" % argv)
        wall = payload.get("pytest_wall_s")
        assert isinstance(wall, (int, float)) and wall >= 0, (
            "017-001 H3: el perfil interrumpido perdio el tiempo del hijo (%r); debe "
            "recuperar la pared aunque hubo SIGINT" % wall)
    finally:
        if process.poll() is None:
            import os as _os
            _os.killpg(process.pid, signal.SIGKILL)
            process.communicate()


# Matriz T1-003 (review-T1-003, con review-T1-002) — integridad de fases según
# el resultado de setup: la exención de call vale solo cuando setup no pasó
# (skipped/failed, que no ejecutan call); con setup pasado, call es esperable
# y toda fase esperable debe estar presente. Medio externo: sombra del
# observador que descarta una fase concreta (patrón de H1/skip-rama
# reutilizado desde los tests autorizados, no desde implementación).
# spec §§4.2–4.3, PC-2, INV-6.
MATRIX_SCENARIOS = {
    "setup-skip": {
        "test": "test_matrix_setup_skip",
        "code": (
            "@pytest.mark.skip(reason='intentional opt-in skip')\n"
            "def test_matrix_setup_skip():\n"
            "    pass\n"
        ),
        "rc": 0,
        "xml": "skipped",
        "drop": "teardown",
    },
    "call-skip": {
        "test": "test_matrix_call_skip",
        "code": (
            "def test_matrix_call_skip():\n"
            "    import pytest\n"
            "    pytest.skip('intentional opt-in skip')\n"
        ),
        "rc": 0,
        "xml": "skipped",
        "drop": "call",
    },
    "teardown-skip": {
        "test": "test_matrix_teardown_skip",
        "code": (
            "@pytest.fixture\n"
            "def _matrix_teardown_skipper():\n"
            "    yield\n"
            "    pytest.skip('intentional opt-in skip')\n"
            "def test_matrix_teardown_skip(_matrix_teardown_skipper):\n"
            "    pass\n"
        ),
        "rc": 0,
        "xml": "skipped",
        "drop": "teardown",
    },
    "setup-failed": {
        "test": "test_matrix_setup_failed",
        "code": (
            "@pytest.fixture\n"
            "def _matrix_failing_setup():\n"
            "    assert False, 'profile deliberate setup failure'\n"
            "    yield\n"
            "def test_matrix_setup_failed(_matrix_failing_setup):\n"
            "    pass\n"
        ),
        "rc": "nonzero",
        "xml": "failed",
        "drop": "teardown",
    },
}

MATRIX_SHADOW = (
    '"""Shadow: registra toda fase salvo la WHEN descartada (perdida externa)."""\n'
    "import json, os, time\n"
    "_phases = []\n"
    "_start = None\n"
    "def pytest_sessionstart(session):\n"
    "    global _start\n"
    "    _start = time.monotonic()\n"
    "def pytest_runtest_logreport(report):\n"
    '    if report.when == "@@DROP@@":\n'
    "        return\n"
    "    if report.passed:\n"
    '        outcome = "passed"\n'
    "    elif report.failed:\n"
    '        outcome = "failed"\n'
    "    else:\n"
    '        outcome = "skipped"\n'
    "    _phases.append({\"nodeid\": report.nodeid, \"when\": report.when, "
    "\"duration_s\": float(getattr(report, \"duration\", 0.0)), "
    "\"outcome\": outcome})\n"
    "def pytest_sessionfinish(session, exitstatus):\n"
    '    sink = os.environ.get("CDAD_SUITE_PHASE_SINK")\n'
    "    if not sink:\n"
    "        return\n"
    "    payload = {\"schema_version\": 1, "
    "\"elapsed_s\": (time.monotonic() - _start) if _start else 0.1, "
    "\"pytest_exitstatus\": exitstatus, \"phases\": _phases}\n"
    '    with open(sink, "w", encoding="utf-8") as _f:\n'
    "        json.dump(payload, _f)\n"
)

MATRIX_PARAMS = []
MATRIX_IDS = []
for _origin, _cfg in MATRIX_SCENARIOS.items():
    MATRIX_PARAMS.append((_origin, None))
    MATRIX_IDS.append(_origin + "-clean")
    MATRIX_PARAMS.append((_origin, _cfg["drop"]))
    MATRIX_IDS.append(_origin + "-drop-" + _cfg["drop"])


@pytest.mark.parametrize("origin,drop_when", MATRIX_PARAMS, ids=MATRIX_IDS)
def test_matrix_phase_loss_is_incomplete_while_clean_stays_complete(
        workspace, origin, drop_when):
    """Sin este test, el usuario consume una medición parcial (una fase
    emitida perdida según el origen del skip/fallo) creyéndola íntegra; sin
    el contrapeso limpio, una corrección futura podría marcar skips/fallos
    limpios como incompletos y bloquear la base (spec §§4.2–4.3, PC-2,
    INV-6; review-T1-003 sobre review-T1-002)."""
    cfg = MATRIX_SCENARIOS[origin]
    name = cfg["test"]
    nodeid = "test_sample.py::" + name
    sample = workspace / "test_sample.py"
    sample.write_text(sample.read_text(encoding="utf-8") + "\n" + cfg["code"],
                      encoding="utf-8")
    tag = "clean" if drop_when is None else "drop-" + drop_when
    if drop_when is not None:
        (workspace / "cdad_suite_observer.py").write_text(
            MATRIX_SHADOW.replace("@@DROP@@", drop_when), encoding="utf-8")
    rc, _, _ = run_close(workspace, [name], "matrix-%s-%s" % (origin, tag))
    if cfg["rc"] == "nonzero":
        assert rc != 0, (
            "017-001 matriz %s (%s): el hijo con fallo de setup debe cerrar "
            "con rc != 0; si no, la escena rompio el resultado contractual "
            "antes del oraculo" % (origin, tag))
    else:
        assert rc == 0, (
            "017-001 matriz %s (%s): el hijo debe cerrar con rc 0; si no, la "
            "escena rompio el resultado contractual en vez de solo la "
            "captura" % (origin, tag))
    attempt = only_attempt(workspace)
    cases = {case.get("name"): case for case in xml_cases(attempt)}
    assert name in cases, (
        "017-001 matriz %s (%s): pytest.xml no muestra que el hijo corrio %s; "
        "sin hijo corrido no hay caso que exigir" % (origin, tag, name))
    case = cases[name]
    if cfg["xml"] == "skipped":
        assert case.find("skipped") is not None and SKIP_REASON in (
            (case.find("skipped").get("message") or "")), (
            "017-001 matriz %s (%s): pytest.xml no conserva el skip de %s con "
            "su motivo" % (origin, tag, name))
    else:
        assert case.find("failure") is not None or case.find("error") is not None, (
            "017-001 matriz %s (%s): pytest.xml no registra el fallo de setup "
            "de %s" % (origin, tag, name))
    profile = profile_data(attempt)
    phases = [row for row in (profile.get("phases") or [])
              if row.get("nodeid") == nodeid]
    if drop_when is None:
        assert any(row.get("when") == "setup" for row in phases), (
            "017-001 matriz %s (clean): el caso limpio no dejo su setup; sin "
            "fases emitidas no hay contrapeso que conservar" % origin)
        assert any(row.get("when") == "teardown" for row in phases), (
            "017-001 matriz %s (clean): el caso limpio no dejo su teardown "
            "emitido; sin ese teardown no hay caso limpio que exigir" % origin)
        if origin == "setup-skip":
            assert any(row.get("when") == "setup" and row.get("outcome") == "skipped"
                       for row in phases), (
                "017-001 matriz setup-skip (clean): el setup del omitido no "
                "quedo como skipped: %r" % phases)
        if origin == "call-skip":
            assert all(row.get("outcome") == "passed"
                       for row in phases if row.get("when") == "setup"), (
                "017-001 matriz call-skip (clean): el setup previo al skip en "
                "call no quedo como passed: %r" % phases)
            assert any(row.get("when") == "call" and row.get("outcome") == "skipped"
                       for row in phases), (
                "017-001 matriz call-skip (clean): el skip dentro de call no "
                "dejo su fase call como skipped: %r" % phases)
        if origin == "setup-failed":
            assert any(row.get("when") == "setup" and row.get("outcome") == "failed"
                       for row in phases), (
                "017-001 matriz setup-failed (clean): el setup no quedo como "
                "failed: %r" % phases)
        assert profile.get("status") == "complete", (
            "017-001 matriz %s (clean): un caso limpio se declaro %r; debe "
            "quedar complete" % (origin, profile.get("status")))
        assert not profile.get("diagnosis"), (
            "017-001 matriz %s (clean): una medicion completa no debe traer "
            "diagnostico pendiente" % origin)
    else:
        assert any(row.get("when") == "setup" for row in phases), (
            "017-001 matriz %s (%s): la perdida inducida no dejo ni el setup; "
            "el medio externo no reprodujo la captura parcial" % (origin, tag))
        assert not any(row.get("when") == drop_when for row in phases), (
            "017-001 matriz %s (%s): el shadow no indujo la perdida de %s; no "
            "se puede exigir el diagnostico sin perdida real"
            % (origin, tag, drop_when))
        if origin == "call-skip":
            assert any(row.get("when") == "setup" and row.get("outcome") == "passed"
                       for row in phases), (
                "017-001 matriz call-skip (%s): sin el setup passed no hay "
                "prueba de que call era esperable" % tag)
            assert any(row.get("when") == "teardown" for row in phases), (
                "017-001 matriz call-skip (%s): la perdida debe ser solo de "
                "call; sin teardown no hay captura parcial que exigir" % tag)
        assert profile.get("status") == "incomplete", (
            "017-001 matriz %s (%s): una captura parcial (fase %s emitida y "
            "perdida, resto presente, XML completo) se declaro %r; debe ser "
            "incomplete" % (origin, tag, drop_when, profile.get("status")))
        assert isinstance(profile.get("diagnosis"), str) and profile["diagnosis"].strip(), (
            "017-001 matriz %s (%s): la medicion incompleta quedo sin "
            "diagnosis accionable" % (origin, tag))
    assert attempt_data(attempt)["rc"] == rc, (
        "017-001 matriz %s (%s): el perfil altero el rc contractual" % (origin, tag))
