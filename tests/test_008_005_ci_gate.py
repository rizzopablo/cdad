"""008-005 PC-1..PC-8: el gate de CI como caja negra por CLI.

Cada test construye un repo sintético con CLIs grabadoras en `scripts/`
(mismo patrón que `tests/test_008_002_suite_evidence.py`) y ejecuta el
entrypoint versionado tal como lo haría un usuario: `--base`, `--repo-root`
y `--evidence-root`. Se observan argv, orden, evidencia, resumen y código de
salida; ninguna aserción importa el producto.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest


CLI = Path(__file__).resolve().parents[1] / "scripts" / "cdad-ci-gate.py"

STEP_ORDER = ["validate-state", "surface", "doctrine", "odoo", "close"]

LONG_SKIP_REASON = (
    "motivo completo de skip (008-005 PC-3/D3: COLUMNS no truncó el motivo "
    "publicado por pytest) "
    + "variable-de-entorno-completa-0123456789 " * 40
)[:678]
assert len(LONG_SKIP_REASON) == 678, "fixture: el motivo largo debe tener 678"

PYTEST_RED_STDOUT = """\
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-8.3.5, pluggy-1.5.0
rootdir: /tmp/synthetic
collected 5 items

test_alpha.py::test_alpha FAILED                                          [ 20%]
test_beta.py::test_beta PASSED                                            [ 40%]
test_gamma.py::test_gamma FAILED                                          [ 60%]
test_delta.py::test_delta SKIPPED (flow opt-in deshabilitado)             [ 80%]
test_epsilon.py::test_epsilon PASSED                                      [100%]

=================================== FAILURES ===================================
________________________________ test_alpha __________________________________

    def test_alpha():
>       assert False, "alpha-boom"
E       AssertionError: alpha-boom
E       assert False

test_alpha.py:3: AssertionError
________________________________ test_gamma __________________________________

    def test_gamma():
>       raise ValueError("gamma-boom")
E       ValueError: gamma-boom

test_gamma.py:2: ValueError
=========================== short test summary info ============================
FAILED test_alpha.py::test_alpha - AssertionError: alpha-boom
FAILED test_gamma.py::test_gamma - ValueError: gamma-boom
======================= 1 passed, 2 failed, 3 skipped in 0.10s =================
"""


# PC-3/F5: un ERROR de colección no lleva `::` ni aparece en el bloque de
# FAILURES; el contrato exige nombrarlo con la ruta como nodeid, con
# `reason: null` y referencia a stdout.log (el motivo no se inventa).
PYTEST_COLLECTION_ERROR_STDOUT = """\
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-8.3.5, pluggy-1.5.0
rootdir: /tmp/synthetic
collected 0 items / 1 error

==================================== ERRORS ====================================
___________________ ERROR collecting tests/test_broken.py ____________________
ImportError while importing test module '/tmp/synthetic/tests/test_broken.py'.
Hint: make sure your test modules/packages have valid Python names.
tests/test_broken.py:1: in <module>
    import missing_dep
E   ModuleNotFoundError: No module named 'missing_dep'
=========================== short test summary info ============================
ERROR tests/test_broken.py - ModuleNotFoundError: No module named 'missing_dep'
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.05s ===============================
"""


# --------------------------------------------------------------- grabadoras


SENTINEL_CONFTEST = '''\
import os

_sentinel = os.environ.get("CI_GATE_TEST_PYTEST_SENTINEL")
if _sentinel:
    with open(_sentinel, "a", encoding="utf-8") as _handle:
        _handle.write("pytest-imported-repo-conftest\\n")
'''


PACKET_RECORDER = '''\
#!/usr/bin/env python3
import json
import os
import sys

argv = sys.argv[1:]
log = os.environ.get("CI_GATE_TEST_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"tool": "packet", "argv": argv}) + "\\n")

if argv[:1] == ["validate-state"]:
    sys.stdout.write(
        "VALID: execution=fake feature=fake model_policy=ordinary\\n")
    sys.exit(0)
if argv[:2] == ["validate-policy", "--classify"] and len(argv) >= 3:
    path = argv[2]
    if path == "README.md" or path.startswith("docs/"):
        kind = "documentation"
    else:
        kind = "unclassified"
    sys.stdout.write(path + "\\t" + kind + "\\n")
    sys.exit(0)
sys.stderr.write("fake cdad_packet: argv no soportado: " + repr(argv) + "\\n")
sys.exit(64)
'''


SUITE_RECORDER = '''\
#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

argv = sys.argv[1:]
log = os.environ.get("CI_GATE_TEST_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"tool": "suite", "argv": argv}) + "\\n")


def _value(name):
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
    return None


scenario = json.loads(
    Path(os.environ["CI_GATE_TEST_SCENARIO"]).read_text(encoding="utf-8"))

if argv[:1] == ["surface"]:
    spec = scenario.get("surface", {})
    rc = int(spec.get("rc", 0))
    if rc != 0:
        sys.stderr.write(spec.get("message", "surface: seleccion vacia\\n"))
        sys.exit(rc)
    sys.stdout.write(json.dumps({"base": _value("--base"), "all": False,
                                 "nodeids": spec.get("nodeids", [])}) + "\\n")
    sys.exit(0)

if argv[:1] == ["close"]:
    spec = scenario.get("close", {})
    root = Path(_value("--evidence-root"))
    root.mkdir(parents=True, exist_ok=True)
    for index, payload in enumerate(spec.get("attempts", []), 1):
        directory = root / ("attempt-%02d-%d-fake" % (index, os.getpid()))
        directory.mkdir(parents=True, exist_ok=True)
        stdout_log = directory / "stdout.log"
        stderr_log = directory / "stderr.log"
        stdout_log.write_text(payload.pop("_stdout", ""), encoding="utf-8")
        stderr_log.write_text("", encoding="utf-8")
        record = dict(payload)
        record.setdefault("schema_version", 1)
        record.setdefault("selection", {"kind": "all", "value": "all",
                                        "nodeids": []})
        record.setdefault("artifacts", {"stdout": str(stdout_log),
                                        "stderr": str(stderr_log)})
        (directory / "attempt.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\\n",
            encoding="utf-8")
    sys.exit(int(spec.get("rc", 0)))

sys.stderr.write("fake cdad-suite: argv no soportado: " + repr(argv) + "\\n")
sys.exit(64)
'''


DOCTRINE_RECORDER = '''\
#!/usr/bin/env python3
import json
import os
import sys

log = os.environ.get("CI_GATE_TEST_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"tool": "doctrine", "argv": sys.argv[1:]})
                     + "\\n")
sys.stdout.write("doctrina: OK (fake)\\n")
sys.exit(0)
'''


ODOO_RECORDER = '''\
#!/usr/bin/env bash
if [ -n "$CI_GATE_TEST_LOG" ]; then
  printf '{"tool": "odoo", "argv": []}\\n' >> "$CI_GATE_TEST_LOG"
fi
echo "68 asserts, 0 fallos (fake)"
exit 0
'''


# ------------------------------------------------------------------ helpers


def _write(path, text, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True)


def make_repo(tmp_path):
    """Repo sintético versionado con las CLIs grabadoras ya comprometidas."""
    repo = tmp_path / "repo"
    control = tmp_path / "control"
    repo.mkdir(parents=True)
    control.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    _write(repo / "conftest.py", SENTINEL_CONFTEST)
    _write(repo / "scripts" / "cdad_packet.py", PACKET_RECORDER, True)
    _write(repo / "scripts" / "cdad-suite.py", SUITE_RECORDER, True)
    _write(repo / "scripts" / "cdad-doctrine-check.py", DOCTRINE_RECORDER, True)
    _write(repo / "tests" / "validate-odoo-specialization.sh", ODOO_RECORDER,
           True)
    _write(repo / "app" / "module.py", "VALUE = 1\n")
    _write(repo / "docs" / "guia.md", "# guia\n")
    _write(repo / "README.md", "# demo\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    return {
        "root": tmp_path,
        "repo": repo,
        "control": control,
        "evidence": tmp_path / "evidence",
        "base": _git(repo, "rev-parse", "HEAD").stdout.strip(),
    }


def commit_change(fixture, relative, text):
    path = fixture["repo"] / relative
    _write(path, text)
    _git(fixture["repo"], "add", relative)
    _git(fixture["repo"], "commit", "-qm", "cambio: " + relative)
    return _git(fixture["repo"], "rev-parse", "HEAD").stdout.strip()


def try_head(fixture):
    return _git(fixture["repo"], "rev-parse", "HEAD").stdout.strip()


def attempt(fixture, *, commit="head", dirty=0, state="finished", rc=0,
            verified=True, passed=3, failed=0, skipped=0, errors=0,
            skips=None, canary_delta=0, stdout=""):
    if commit == "head":
        commit = try_head(fixture)
    return {
        "state": state,
        "command": "close --all",
        "commit": commit,
        "dirty": dirty,
        "started_at": "2026-10-28T00:00:00+00:00",
        "finished_at": ("2026-10-28T00:00:10+00:00"
                        if state == "finished" else None),
        "rc": rc if state == "finished" else None,
        "pytest_summary": {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "xfailed": 0,
            "xpassed": 0,
            "verified": verified,
            "skips": list(skips or []),
        },
        "canary": {"scope": "HOME", "before": 5, "after": 5 + canary_delta,
                   "delta_lines": canary_delta},
        "_stdout": stdout,
    }


def healthy(fixture, **overrides):
    return {
        "surface": {"rc": 0, "nodeids": ["test_sample.py::test_ok"]},
        "close": {"rc": 0, "attempts": [attempt(fixture, **overrides)]},
    }


def write_scenario(fixture, scenario):
    (fixture["control"] / "scenario.json").write_text(
        json.dumps(scenario), encoding="utf-8")


def gate_env(fixture, env_extra=None):
    env = dict(os.environ)
    env["CI_GATE_TEST_LOG"] = str(fixture["control"] / "calls.jsonl")
    env["CI_GATE_TEST_SCENARIO"] = str(fixture["control"] / "scenario.json")
    env["CI_GATE_TEST_PYTEST_SENTINEL"] = str(
        fixture["control"] / "pytest-sentinel.log")
    if env_extra:
        env.update(env_extra)
    return env


def run_gate_argv(fixture, argv, *, env_extra=None):
    """Invoca el entrypoint con argv explícito (necesario para los casos de
    error de uso: sin `--base`, `--repo-root` inutilizable)."""
    assert CLI.is_file(), (
        "008-005: el entrypoint versionado scripts/cdad-ci-gate.py no "
        "existe; sin él ninguna de las promesas del gate (PC-1..PC-8) es "
        "verificable por el usuario")
    return subprocess.run(
        [sys.executable, str(CLI), *argv], cwd=str(fixture["repo"]),
        env=gate_env(fixture, env_extra), capture_output=True, text=True,
        timeout=180)


def run_gate(fixture, *, base=None, env_extra=None):
    argv = [
        "--base", fixture["base"] if base is None else base,
        "--repo-root", str(fixture["repo"]),
        "--evidence-root", str(fixture["evidence"]),
    ]
    return run_gate_argv(fixture, argv, env_extra=env_extra)


def calls(fixture):
    path = fixture["control"] / "calls.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def step_names(fixture):
    names = []
    for record in calls(fixture):
        tool, argv = record["tool"], record["argv"]
        if tool == "packet" and argv[:1] == ["validate-state"]:
            names.append("validate-state")
        elif tool == "packet" and argv[:1] == ["validate-policy"]:
            continue
        elif tool == "suite" and argv[:1] == ["surface"]:
            names.append("surface")
        elif tool == "suite" and argv[:1] == ["close"]:
            names.append("close")
        elif tool == "doctrine":
            names.append("doctrine")
        elif tool == "odoo":
            names.append("odoo")
        else:
            names.append("?" + tool + ":" + " ".join(argv))
    return names


def step_calls(fixture, tool, subcommand):
    return [record for record in calls(fixture)
            if record["tool"] == tool and record["argv"][:1] == [subcommand]]


def run_roots(fixture):
    evidence = fixture["evidence"]
    if not evidence.is_dir():
        return []
    return sorted(path for path in evidence.iterdir()
                  if path.is_dir() and path.name.startswith("gate-"))


def only_root(fixture):
    roots = run_roots(fixture)
    assert len(roots) == 1, (
        f"PC-7: la corrida debe dejar exactamente una raíz de evidencia "
        f"bajo la base; encontradas: {[p.name for p in roots]}")
    return roots[0]


def gate_json(run_root):
    path = run_root / "gate.json"
    assert path.is_file(), (
        f"008-005: la corrida no dejó gate.json en {run_root.name} "
        f"(PC-7: toda corrida deja gate.json)")
    return json.loads(path.read_text(encoding="utf-8"))


def report_text(run_root):
    path = run_root / "suite-report.md"
    assert path.is_file(), (
        f"008-005: la corrida no dejó suite-report.md en {run_root.name} "
        f"(D10/PC-3: el resumen humano es parte del veredicto)")
    return path.read_text(encoding="utf-8")


def cause_tokens(data):
    return [str(cause).split(":", 1)[0].strip() for cause in data["causes"]]


def sentinel_absent(fixture):
    path = fixture["control"] / "pytest-sentinel.log"
    assert not path.is_file(), (
        "PC-1/PC-3: el gate ejecutó pytest fuera de `close --all` "
        f"(el conftest del repo sintético se importó): {path.read_text()!r}")


def snapshot(root, *, skip_git=False):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes())
            .hexdigest()
            for path in root.rglob("*")
            if path.is_file()
            and not (skip_git and ".git" in path.relative_to(root).parts)}


def product_change(fixture):
    return commit_change(fixture, "app/module.py", "VALUE = 2\n")


# ------------------------------------------------------------------- PC-1


def test_pc1_un_comando_orden_fijo_y_una_sola_corrida_de_pytest(tmp_path):
    """PC-1: sin este test, el usuario paga dos suites por push y no puede
    saber si el veredicto salió del orden declarado."""
    fixture = make_repo(tmp_path)
    product_change(fixture)
    write_scenario(fixture, healthy(fixture))

    result = run_gate(fixture)

    assert result.returncode == 0, (
        f"PC-1: la corrida sana del gate salió {result.returncode}: "
        f"{result.stdout}{result.stderr}")
    assert step_names(fixture) == STEP_ORDER, (
        "PC-1: el gate no ejecutó los pasos aplicables en el orden "
        f"declarado y una sola vez: {step_names(fixture)}")
    surface = step_calls(fixture, "suite", "surface")
    assert len(surface) == 1
    assert "--collect-only" in surface[0]["argv"], (
        "PC-1: el paso de superficie no usó --collect-only: "
        f"{surface[0]['argv']}")
    assert "--base" in surface[0]["argv"]
    close = step_calls(fixture, "suite", "close")
    assert len(close) == 1
    assert "--all" in close[0]["argv"], (
        f"PC-1/INV-4: `close` no corrió la suite completa: {close[0]['argv']}")
    data = gate_json(only_root(fixture))
    assert [gate["name"] for gate in data["gates"]] == [
        "validate-state", "surface", "doctrine", "odoo-specialization",
        "close"], (
        f"PC-1: gates[] no refleja el orden declarado: {data['gates']}")
    assert all(gate["applicable"] is True for gate in data["gates"])
    sentinel_absent(fixture)


# ------------------------------------------------------------------- PC-2


ATTRIBUTION_CASES = [
    ("verde-atribuible", "verde-atribuible", 0, None),
    ("commit-nulo", "commit-nulo", 1, "commit-null"),
    ("dirty-no-cero", "dirty-no-cero", 1, "dirty-no-cero"),
    ("intento-no-finished", "intento-no-finished", 1, "attempt-no-finished"),
    ("summary-no-verified", "summary-no-verified", 1, "summary-unverified"),
    ("cero-intentos", "cero-intentos", 1, "sin-intento"),
    ("intentos-multiples", "intentos-multiples", 1, "intentos-multiples"),
    ("close-rc", "close-rc", 1, "close-rc"),
]


def attribution_scenario(fixture, condition):
    if condition == "verde-atribuible":
        return healthy(fixture)
    if condition == "commit-nulo":
        return healthy(fixture, commit=None)
    if condition == "dirty-no-cero":
        scenario = healthy(fixture)
        # El intento declara árbol limpio; el árbol real tiene un archivo
        # versionado modificado (AC-2: el gate mide el árbol, no confía).
        _write(fixture["repo"] / "app" / "module.py", "VALUE = 99\n")
        return scenario
    if condition == "intento-no-finished":
        return healthy(fixture, state="running")
    if condition == "summary-no-verified":
        return healthy(fixture, verified=False)
    if condition == "cero-intentos":
        return {"surface": {"rc": 0}, "close": {"rc": 0, "attempts": []}}
    if condition == "intentos-multiples":
        return {
            "surface": {"rc": 0},
            "close": {"rc": 0, "attempts": [attempt(fixture),
                                            attempt(fixture)]},
        }
    if condition == "close-rc":
        return {
            "surface": {"rc": 0},
            "close": {"rc": 1, "attempts": [attempt(fixture, rc=1,
                                                    failed=1)]},
        }
    raise AssertionError("condición desconocida: " + condition)


@pytest.mark.parametrize("condition,expected_rc,cause", [
    (case[1], case[2], case[3]) for case in ATTRIBUTION_CASES
], ids=[case[0] for case in ATTRIBUTION_CASES])
def test_pc2_atribucion_fail_closed(tmp_path, condition, expected_rc, cause):
    """PC-2: sin este test, el usuario puede recibir un verde no atribuible
    (commit nulo, árbol sucio, intento incompleto o resumen no verificable)
    como si el commit bajo prueba hubiera pasado."""
    fixture = make_repo(tmp_path)
    product_change(fixture)
    write_scenario(fixture, attribution_scenario(fixture, condition))

    result = run_gate(fixture)

    data = gate_json(only_root(fixture))
    if cause is None:
        assert result.returncode == 0, (
            f"PC-2: un intento finished/verified/rc 0/commit/dirty 0 debe "
            f"salir 0; salió {result.returncode}: {result.stderr}")
        assert data["verdict"] == "green"
        attribution = data["attribution"]
        assert attribution["attributable"] is True
        assert attribution["attempts"] == 1
        assert attribution["attempt_state"] == "finished"
        assert attribution["summary_verified"] is True
        assert attribution["dirty"] == 0
        assert attribution["commit"]
        assert attribution.get("causes") == [], (
            f"PC-2/PC-7 (F3): attribution no reproduce el esquema 1: "
            f"`attribution.causes` debe estar presente y vacío en verde; "
            f"got {attribution.get('causes')!r}")
        assert data["causes"] == []
        return

    assert result.returncode == 1, (
        f"PC-2 [{condition}]: un verde no atribuible debe salir != 0 "
        f"(1 = rojo); salió {result.returncode}: {result.stderr}")
    assert data["verdict"] == "red"
    tokens = cause_tokens(data)
    assert cause in tokens, (
        f"PC-2 [{condition}]: el veredicto no nombra la causa {cause!r}: "
        f"{data['causes']}")
    assert data["attribution"]["attributable"] is False
    if condition == "dirty-no-cero":
        assert data["dirty"] != 0, (
            "PC-2/AC-2: el gate declaró árbol limpio con un archivo "
            "versionado modificado")
    if condition == "cero-intentos":
        assert data["attempt"] is None
    if condition == "intentos-multiples":
        assert data["attribution"]["attempts"] == 2


# ------------------------------------------------------------------- PC-3


def test_pc3_rojo_nombra_fallos_y_skips_completos_sin_repetir_suite(tmp_path):
    """PC-3: sin este test, quien lee el reporte no sabe qué contrato se
    rompió, un skip largo se lee truncado y el rojo cuesta una segunda
    suite para explicarse."""
    fixture = make_repo(tmp_path)
    product_change(fixture)
    skips = [
        {"nodeid": "test_delta.py::test_delta",
         "reason": "flow opt-in deshabilitado"},
        {"nodeid": "test_zeta.py::test_zeta",
         "reason": "requiere acceso a red: la suite no sale a la red en CI"},
        {"nodeid": "test_eta.py::test_eta", "reason": LONG_SKIP_REASON},
    ]
    write_scenario(fixture, {
        "surface": {"rc": 0},
        "close": {
            "rc": 1,
            "attempts": [attempt(
                fixture, rc=1, passed=1, failed=2, skipped=3, skips=skips,
                stdout=PYTEST_RED_STDOUT)],
        },
    })

    result = run_gate(fixture)

    assert result.returncode == 1, (
        f"PC-3: un rojo de suite debe salir 1; salió {result.returncode}")
    run_root = only_root(fixture)
    data = gate_json(run_root)
    assert data["verdict"] == "red"
    report = report_text(run_root)

    failures = {item["nodeid"]: item for item in data["pytest"]["failures"]}
    assert set(failures) == {"test_alpha.py::test_alpha",
                             "test_gamma.py::test_gamma"}, (
        f"PC-3: gate.json no nombra cada nodeid fallido: {failures}")
    for nodeid, marker in (("test_alpha.py::test_alpha", "alpha-boom"),
                           ("test_gamma.py::test_gamma", "gamma-boom")):
        assert nodeid in report, (
            f"PC-3: suite-report.md no nombra el nodeid fallido {nodeid}")
        reason = failures[nodeid].get("reason")
        if reason is None:
            assert "stdout.log" in report, (
                "PC-3: motivo no atribuible sin declarar la referencia a "
                "stdout.log")
        else:
            assert marker in reason, (
                f"PC-3: el motivo de {nodeid} no corresponde al fallo: "
                f"{reason!r}")

    reported = {item["nodeid"]: item["reason"]
                for item in data["pytest"]["skips"]}
    for skip in skips:
        assert reported.get(skip["nodeid"]) == skip["reason"], (
            f"PC-3: el skip {skip['nodeid']} no conserva su motivo "
            f"completo: {reported.get(skip['nodeid'])!r}")
        assert skip["reason"] in report, (
            f"PC-3: suite-report.md no lleva el motivo completo de "
            f"{skip['nodeid']}")
    assert LONG_SKIP_REASON in report
    assert len(step_calls(fixture, "suite", "close")) == 1, (
        "PC-3: el gate volvió a ejecutar pytest después del rojo")
    sentinel_absent(fixture)


def test_pc3_error_de_coleccion_se_nombra_y_referencia_stdout_log(tmp_path):
    """PC-3/F5: sin este test, un ERROR de colección (sin `::`) queda sin
    nombrar en el veredicto y el lector no tiene ni ruta ni log al que ir,
    aunque el contrato exige nombrarlo con su ruta y declarar el motivo
    como no atribuible."""
    fixture = make_repo(tmp_path)
    product_change(fixture)
    write_scenario(fixture, {
        "surface": {"rc": 0},
        "close": {
            "rc": 1,
            "attempts": [attempt(
                fixture, rc=1, passed=0, failed=0, skipped=0, errors=1,
                stdout=PYTEST_COLLECTION_ERROR_STDOUT)],
        },
    })

    result = run_gate(fixture)

    assert result.returncode == 1, (
        f"PC-3: un error de colección es rojo (1); salió "
        f"{result.returncode}: {result.stderr}")
    run_root = only_root(fixture)
    data = gate_json(run_root)
    report = report_text(run_root)
    assert data["verdict"] == "red"
    failures = {item["nodeid"]: item for item in data["pytest"]["failures"]}
    error_node = "tests/test_broken.py"
    assert error_node in failures, (
        f"PC-3/F5: el ERROR de colección no se nombra con la ruta como "
        f"nodeid (sin `::`): {sorted(failures)}")
    assert failures[error_node].get("reason") is None, (
        f"PC-3/F5: un ERROR de colección no es atribuible al bloque de "
        f"fallos de pytest; el motivo no se inventa: "
        f"{failures[error_node].get('reason')!r}")
    assert error_node in report, (
        f"PC-3/F5: suite-report.md no nombra la ruta del error de "
        f"colección {error_node}")
    assert "stdout.log" in report, (
        "PC-3/F5: el reporte no declara la referencia a stdout.log para el "
        "error no atribuible")
    assert data["pytest"]["errors"] == 1, (
        f"PC-3/F5: el error de colección (fallo no atribuible) no cuenta "
        f"como error: {data['pytest']}")
    assert len(step_calls(fixture, "suite", "close")) == 1, (
        "PC-3: el gate volvió a ejecutar pytest para explicar el error")
    sentinel_absent(fixture)


# ------------------------------------------------------------------- PC-4


@pytest.mark.parametrize("relative,text", [
    ("docs/nota.md", "# nota\n"),
    ("README.md", "# demo v2\n"),
], ids=["docs-only", "readme-only"])
def test_pc4_cambio_solo_documentacion_no_ejecuta_superficie(
        tmp_path, relative, text):
    """PC-4: sin este test, un cambio de documentación se bloquea por un
    mapeo de superficie que no puede aplicar."""
    fixture = make_repo(tmp_path)
    commit_change(fixture, relative, text)
    write_scenario(fixture, healthy(fixture))

    result = run_gate(fixture)

    assert result.returncode == 0, (
        f"PC-4: un diff sólo documentación no debe hacer fallar el gate; "
        f"salió {result.returncode}: {result.stdout}{result.stderr}")
    assert step_names(fixture) == ["validate-state", "doctrine", "odoo",
                                  "close"], (
        "PC-4: el paso de superficie se ejecutó sobre un cambio sólo "
        f"documentación: {step_names(fixture)}")
    data = gate_json(only_root(fixture))
    assert data["change"]["kind"] == "solo-documentacion", (
        f"PC-4: change.kind no clasifica el diff como documentación: "
        f"{data['change']}")
    surface_gate = [gate for gate in data["gates"]
                    if gate["name"] == "surface"]
    assert len(surface_gate) == 1
    assert surface_gate[0]["applicable"] is False, (
        "PC-4: el paso de superficie no se declaró no aplica")
    assert surface_gate[0]["rc"] in (0, None), (
        "PC-4: un paso no aplicable no puede declarar un rc de fallo")
    assert str(surface_gate[0]["detail"]).strip(), (
        "PC-4: no se registró el motivo de la no aplicabilidad")


def test_pc4_cambio_de_producto_sin_superficie_es_rojo_y_nombra_ruta(
        tmp_path):
    """PC-4: sin este test, un cambio de producto con el mapa de superficie
    desactualizado pasa como verde."""
    fixture = make_repo(tmp_path)
    product_change(fixture)
    write_scenario(fixture, {
        "surface": {
            "rc": 1,
            "message": ("surface: cambio sin superficie clasificada: "
                        "app/module.py\n"),
        },
        "close": {"rc": 0, "attempts": [attempt(fixture)]},
    })

    result = run_gate(fixture)

    assert result.returncode == 1, (
        f"PC-4: un cambio de producto sin superficie debe ser rojo; salió "
        f"{result.returncode}")
    run_root = only_root(fixture)
    data = gate_json(run_root)
    assert data["verdict"] == "red"
    assert "surface-rc" in cause_tokens(data), (
        f"PC-4: el veredicto no nombra la causa de superficie: "
        f"{data['causes']}")
    assert data["change"]["kind"] == "codigo"
    assert "app/module.py" in json.dumps(data, ensure_ascii=False), (
        "PC-4: el veredicto no nombra la ruta que produjo el rojo de "
        "superficie")
    assert "app/module.py" in report_text(run_root)
    assert len(step_calls(fixture, "suite", "close")) == 1, (
        "PC-4/D1: un rojo barato no suprime la corrida de la suite")


# ------------------------------------------------------------------- PC-5


NETWORK_SHIM = """\
#!/bin/sh
if [ -n "$CI_GATE_TEST_VIOLATIONS" ]; then
  printf '%s %s\\n' "$0" "$*" >> "$CI_GATE_TEST_VIOLATIONS"
fi
exit 127
"""

GIT_SHIM = """\
#!/usr/bin/env bash
case "$1" in
  push|fetch|pull|clone)
    if [ -n "$CI_GATE_TEST_VIOLATIONS" ]; then
      printf 'git %%s\\n' "$*" >> "$CI_GATE_TEST_VIOLATIONS"
    fi
    exit 1
    ;;
  tag)
    if [ -n "$CI_GATE_TEST_VIOLATIONS" ]; then
      printf 'git %%s\\n' "$*" >> "$CI_GATE_TEST_VIOLATIONS"
    fi
    ;;
esac
exec %s "$@"
"""


def test_pc5_hermetico_sin_home_sin_red_y_sin_escrituras_fuera(tmp_path):
    """PC-5: sin este test, el gate puede depender del HOME del operador,
    salir a la red o escribir fuera de su raíz de evidencia."""
    fixture = make_repo(tmp_path)
    product_change(fixture)
    write_scenario(fixture, healthy(fixture))

    home = tmp_path / "empty-home"
    home.mkdir()
    shims = tmp_path / "shims"
    shims.mkdir()
    violations = fixture["control"] / "violations.log"
    real_git = shutil.which("git")
    assert real_git, "fixture: git no está disponible"
    for name in ("curl", "wget", "nc", "ssh", "scp", "ftp"):
        _write(shims / name, NETWORK_SHIM, True)
    _write(shims / "git", GIT_SHIM % real_git, True)

    # El índice interno de git no es objeto de PC-5 (sólo el árbol de
    # trabajo y su estado visible); el estado sí se compara por `status`.
    repo_before = snapshot(fixture["repo"], skip_git=True)
    home_before = snapshot(home)
    tree_before = snapshot(tmp_path, skip_git=True)
    status_before = _git(fixture["repo"], "status", "--porcelain").stdout

    result = run_gate(fixture, env_extra={
        "HOME": str(home),
        "XDG_CONFIG_HOME": "",
        "XDG_DATA_HOME": "",
        "XDG_STATE_HOME": "",
        "XDG_CACHE_HOME": "",
        "PATH": str(shims) + os.pathsep + os.environ.get("PATH", ""),
        "CI_GATE_TEST_VIOLATIONS": str(violations),
    })

    assert result.returncode == 0, (
        f"PC-5: el gate no completó con HOME vacío y PATH sin red: "
        f"{result.returncode}\n{result.stdout}{result.stderr}")
    tree_after = snapshot(tmp_path, skip_git=True)
    new_paths = {path for path in tree_after if path not in tree_before}
    foreign = {path for path in new_paths
               if not (path.startswith("evidence/")
                       or path == "control/calls.jsonl")}
    assert not foreign, (
        f"PC-5/INV-2: el gate escribió fuera de la raíz de la corrida: "
        f"{sorted(foreign)}")
    assert snapshot(fixture["repo"], skip_git=True) == repo_before, (
        "PC-5/INV-2: el gate modificó el árbol de trabajo")
    assert snapshot(home) == home_before, (
        "PC-5: el gate escribió en el HOME del operador")
    assert _git(fixture["repo"], "status", "--porcelain").stdout == \
        status_before
    assert not violations.is_file() or not violations.read_text().strip(), (
        f"PC-5/INV-3: el gate intentó publicar o salir a la red: "
        f"{violations.read_text() if violations.is_file() else ''}")
    data = gate_json(only_root(fixture))
    assert data["verdict"] == "green"


# ------------------------------------------------------------------- PC-7


def test_pc7_dos_corridas_dos_raices_y_gate_json_aun_fallando(tmp_path):
    """PC-7: sin este test, el dueño pierde la evidencia de un push pasado
    o no puede auditar una corrida que falló antes de cerrar."""
    fixture = make_repo(tmp_path)
    product_change(fixture)
    write_scenario(fixture, healthy(fixture))

    first = run_gate(fixture)
    assert first.returncode == 0, first.stderr
    first_root = only_root(fixture)
    first_hashes = snapshot(first_root)
    assert (first_root / "gate.json").is_file()
    assert (first_root / "suite-report.md").is_file()

    second = run_gate(fixture)
    assert second.returncode == 0, second.stderr
    roots = run_roots(fixture)
    assert len(roots) == 2, (
        f"PC-7: dos corridas deben dejar dos raíces: {[p.name for p in roots]}")
    assert snapshot(first_root) == first_hashes, (
        "PC-7: la segunda corrida pisó la evidencia de la primera")
    for run_root in roots:
        data = gate_json(run_root)
        assert data["schema_version"] == 1
        attempts = [path for path in run_root.iterdir()
                    if path.is_dir() and path.name.startswith("attempt-")]
        assert len(attempts) == 1, (
            f"PC-7: la raíz {run_root.name} no tiene exactamente un "
            f"intento: {[p.name for p in attempts]}")

    broken = run_gate(fixture, base="0" * 40)
    assert broken.returncode != 0, (
        "PC-7: una base inválida debe producir una salida distinta de cero")
    third = set(run_roots(fixture)) - set(roots)
    assert len(third) == 1, (
        "PC-7: la corrida fallida tampoco dejó su raíz de evidencia")
    data = gate_json(third.pop())
    assert data["verdict"] == "red"
    assert data["causes"], (
        "PC-7: la corrida que falla antes de close no dejó la causa")
    # F3/F4: la precondición fallida se nombra, no se inventa clasificación.
    assert "base-invalida" in cause_tokens(data), (
        f"PC-7/F3: la base inválida no se declara con la causa "
        f"`base-invalida` del vocabulario cerrado: {data['causes']}")
    assert data["change"]["kind"] == "desconocido", (
        f"PC-7/F3: con base inválida el cambio no puede clasificarse: "
        f"change.kind debe ser 'desconocido', no {data['change']!r}")
    always = ["validate-state", "doctrine", "odoo-specialization", "close"]
    gates = {gate["name"]: gate for gate in data["gates"]}
    assert set(gates) == set(always), (
        f"PC-7/F4: gates[] debe registrar exactamente los cuatro pasos "
        f"«siempre» cuando la precondición falla (la superficie no aplica y "
        f"no se registra): {sorted(gates)}")
    for name in always:
        assert gates[name]["applicable"] is False, (
            f"PC-7/F4: el paso {name} debe declararse no aplicable cuando "
            f"la precondición falla: {gates[name]!r}")
        assert gates[name]["rc"] is None, (
            f"PC-7/F4: un paso no aplicable no puede publicar rc: "
            f"{gates[name]!r}")
        assert str(gates[name]["detail"]).strip(), (
            f"PC-7/F4: el paso {name} no nombra la precondición que lo "
            f"hizo no aplicable: {gates[name]!r}")


# ------------------------------------------------------------------- PC-8


def test_pc8_canario_y_carga_visibles_y_no_decisorios(tmp_path):
    """PC-8: sin este test, la interferencia con el HOME real o la carga del
    runner pueden convertir un verde de suite en rojo, o quedar invisibles."""
    fixture = make_repo(tmp_path)
    product_change(fixture)

    write_scenario(fixture, healthy(fixture, canary_delta=0))
    first = run_gate(fixture)
    assert first.returncode == 0, first.stderr
    write_scenario(fixture, healthy(fixture, canary_delta=450))
    second = run_gate(fixture)
    assert second.returncode == 0, (
        f"PC-8/INV-5: un delta de canario cambió el código de salida: "
        f"{second.returncode}")

    roots = run_roots(fixture)
    assert len(roots) == 2
    by_delta = {}
    for run_root in roots:
        data = gate_json(run_root)
        assert data["verdict"] == "green"
        assert isinstance(data["loadavg"], list)
        assert len(data["loadavg"]) == 3
        assert all(isinstance(value, (int, float))
                   for value in data["loadavg"])
        by_delta[data["canary"]["delta_lines"]] = (run_root, data)
    assert set(by_delta) == {0, 450}, (
        f"PC-8: el delta del canario no quedó en gate.json: "
        f"{sorted(by_delta)}")
    report = report_text(by_delta[450][0])
    assert "450" in report, (
        "PC-8: el resumen humano no muestra el delta del canario")
    assert re.search(r"canary|canario", report, re.IGNORECASE), (
        "PC-8: el resumen humano no nombra el canario")
    assert re.search(r"load|carga", report, re.IGNORECASE), (
        "PC-8: el resumen humano no muestra la carga")


# ------------------------------------------- error de uso (exit 2, D6/F8)


def test_exit2_sin_base_es_error_de_uso_y_no_abre_raiz(tmp_path):
    """D6/F8: sin este test, el usuario puede correr el gate sin `--base` y
    recibir un veredicto sobre una base inventada (o pagar una raíz de
    evidencia por un error de uso)."""
    fixture = make_repo(tmp_path)
    product_change(fixture)
    write_scenario(fixture, healthy(fixture))

    result = run_gate_argv(fixture, [
        "--repo-root", str(fixture["repo"]),
        "--evidence-root", str(fixture["evidence"]),
    ])

    assert result.returncode == 2, (
        f"D6/F8: sin `--base` el gate debe salir 2 (error de uso), no "
        f"{result.returncode}: {result.stdout}{result.stderr}")
    diagnostic = (result.stderr or "") + (result.stdout or "")
    assert "base" in diagnostic.lower(), (
        f"D6/F8: el error de uso no nombra la falta de `--base`: "
        f"{diagnostic!r}")
    assert run_roots(fixture) == [], (
        f"F8/PC-7: un error de uso no abre raíz de evidencia nueva: "
        f"{[path.name for path in run_roots(fixture)]}")
    assert step_names(fixture) == [], (
        f"D6: el gate ejecutó pasos sin `--base`: {step_names(fixture)}")


def test_exit2_repo_root_archivo_es_error_de_uso(tmp_path):
    """D6/F8: sin este test, un `--repo-root` que no es un directorio puede
    terminar en un fallo interno (rc 1) o, peor, en una corrida sobre un
    árbol que no existe."""
    fixture = make_repo(tmp_path)
    product_change(fixture)
    write_scenario(fixture, healthy(fixture))
    not_a_dir = fixture["repo"] / "README.md"
    assert not_a_dir.is_file()

    result = run_gate_argv(fixture, [
        "--base", fixture["base"],
        "--repo-root", str(not_a_dir),
        "--evidence-root", str(fixture["evidence"]),
    ])

    assert result.returncode == 2, (
        f"F8: `--repo-root` apuntando a un archivo es error de uso (2), no "
        f"{result.returncode}: {result.stdout}{result.stderr}")
    diagnostic = (result.stderr or "") + (result.stdout or "")
    assert diagnostic.strip(), (
        "F8: el error de uso de `--repo-root` no deja diagnóstico")
