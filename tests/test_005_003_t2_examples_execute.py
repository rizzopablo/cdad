#!/usr/bin/env python3
"""005-003 T2 RED — interfaz operativa + disposición de versión + evidencia
mecánica + arranque con la vista primero (PD-3, PD-4, PD-5, PD-11;
INV-1, INV-3, INV-9).

Contract:
- docs/specs/005-003-orientation-reduction/spec.md §2.3 (interfaz operativa y
  asset canónico de ejemplos ejecutables), §2.4 (disposición de versión y del
  medidor), §2.5 (evidencia mecánica fiable), §2.9 (arranque y reentrada con la
  vista primero), §3 PD-3/PD-4/PD-5/PD-11, §4 INV-1/INV-3/INV-9.
- docs/specs/005-003-orientation-reduction/plan.md §3 (ficha T2) y §4 (T2).

Superficie observable bajo prueba (proyectos sintéticos en tempdirs; caja
negra: SOLO subprocess sobre los CLIs del árbol; la implementación NUNCA se
importa ni se lee al escribir este test):

    python3 <skill-dir>/scripts/cdad_packet.py status --project-root <ABS>
    python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root <ABS> \\
        --record-dispatch <packet-id> --attempt-id <id> --input <attempt.json>
    python3 <skill-dir>/scripts/cdad_continuity.py begin --project-root <ABS> \\
        --execution-context <exec.json> --update <UPDATE.json>

Los ejemplos mínimos viven en el ASSET CANÓNICO declarado por la spec
(`skills/cdad-cycle/assets/orientation-examples.json`): el test los LOCALIZA
por su ruta declarada y los EJECUTA, nunca por prosa de Markdown. Los oráculos
documentales (PD-4/PD-5/PD-11) leen la referencia/procedimiento por su ruta
declarada en tiempo de ejecución; la spec fija qué afirman.

El asset aún NO existe y las referencias aún no declaran el contrato de T2: por
eso cada test falla en la ASERCIÓN sobre el contrato observable (asset / rc /
diagnóstico / documento), nunca en un error de E/S no capturado, ImportError,
SyntaxError ni error de setup. Los fixtures son autocontenidos (tempdirs
armados por el test; sin datos de demo, sin la base real de sesiones, sin rutas
de este host) y el HOME del subproceso SIEMPRE es un tempdir vacío.

Mapeo test → postcondición/borde:
  test_pd3_asset_declares_minimum_examples
      -> PD-3 (asset canónico con `examples[]`; cada elemento declara
         id/kind/target + input|command; conjunto mínimo: attempt.json,
         UPDATE de continuidad, invocación de la vista `status`)
  test_pd3_dispatch_record_example_executes
      -> PD-3 (el ejemplo del registro de despacho se EJECUTA, rc=0)
  test_pd3_continuity_update_example_executes
      -> PD-3 (el UPDATE de continuidad se EJECUTA, rc=0)
  test_pd3_status_invocation_example_executes
      -> PD-3 (la invocación válida de la vista `status` se EJECUTA, rc=0)
  test_pd3_invalid_example_fails_naming_the_field
      -> PD-3 borde (un ejemplo inválido falla con el diagnóstico que NOMBRA
         el campo: `runtime` ausente en el attempt.json)
  test_pd5_reference_declares_real_rc_capture_and_repro
      -> PD-5 (el patrón de captura vive en `orientation.md` —`PIPESTATUS[0]`,
         no `$?`, sin tubería que enmascare— y una invocación que falla,
         capturada con el patrón, reporta el rc REAL ≠ 0 y el error accionable
         nombra la causa y la recuperación)
  test_pd4_reference_distinguishes_absence_from_incoherence
      -> PD-4 (reusa el `cdad-version-check.py` instalado; UNKNOWN /
         NO-PROJECT-AGENTS = ausencia ≠ DRIFT = incoherencia)
  test_pd4_absent_meter_declared_as_absence_not_drift
      -> PD-4 borde («medidor no instalado» se declara ausencia, no DRIFT)
  test_pd11_start_procedure_names_status_view_as_orientation_action
      -> PD-11 (i) el procedimiento nombra la vista `status` como acción de
         orientación
  test_pd11_start_procedure_declares_expand_only_on_concrete_need
      -> PD-11 (ii) declara la regla de ampliar solo ante una necesidad
         concreta (un bloqueo o una duda que afecte al siguiente despacho)
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import (
    build_project,
    read_state,
    tree_snapshot,
    write_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"

# Rutas DECLARADAS por la spec (el test localiza por ellas, nunca por prosa).
ASSET = SKILL_DIR / "assets" / "orientation-examples.json"
ORIENTATION = SKILL_DIR / "references" / "orientation.md"
PROJECT_START = SKILL_DIR / "references" / "project-start.md"

# CLIs del árbol (versión correspondiente), invocados como subproceso.
PACKET_CLI = SKILL_DIR / "scripts" / "cdad_packet.py"
CONTINUITY_CLI = SKILL_DIR / "scripts" / "cdad_continuity.py"

CLI_TIMEOUT_S = 60

# §2.3: campos EXACTOS del archivo de entrada del registro de despacho.
DISPATCH_KEYS = (
    "runtime",
    "model_configured",
    "model_reported",
    "session",
    "started_at",
    "provenance",
)
# §2.3: el UPDATE de continuidad exige estas cuatro de CONTENIDO; `budget` es
# opcional y el CLI exige además las claves de idempotencia (`packet_id`,
# `attempt`). La spec fija el contenido mínimo, no un conjunto exclusivo.
CONTINUITY_REQUIRED = ("goal", "decisions", "uncertainties", "next_action")
CONTINUITY_ALLOWED = set(CONTINUITY_REQUIRED) | {"budget", "packet_id", "attempt"}


# ---------------------------------------------------------------- helpers


def _load_text(path: Path) -> str:
    """Documento declarado por su ruta; ausente es estado conductual, no E/S."""
    assert path.is_file(), (
        f"documento requerido no existe (ruta declarada): {path}"
    )
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> object:
    """Asset JSON declarado; ausente/inválido es AssertionError de contrato."""
    assert path.is_file(), (
        "PD-3 violada: el asset canónico de ejemplos no existe en su ruta "
        f"declarada: {path}"
    )
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"PD-3 violada: el asset de ejemplos no es JSON válido ({path}): "
            f"{raw[:200]!r}"
        ) from exc


def _as_obj(value: object):
    """El contenido de un ejemplo como objeto: dict, o texto JSON parseado."""
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _tokens(command: object) -> list[str] | None:
    if isinstance(command, list) and command:
        return [str(t) for t in command]
    if isinstance(command, str) and command.strip():
        return shlex.split(command)
    return None


def _examples(asset: object) -> list[dict]:
    """Los `examples[]` del asset, con su forma mínima declarada (§2.3)."""
    assert isinstance(asset, dict), (
        f"PD-3 violada: el asset de ejemplos no es un objeto JSON: {asset!r}"
    )
    examples = asset.get("examples")
    assert isinstance(examples, list) and examples, (
        "PD-3 violada: el asset no declara un array `examples[]` no vacío: "
        f"{asset!r}"
    )
    for ex in examples:
        assert isinstance(ex, dict), (
            f"PD-3 violada: elemento de `examples[]` no es un objeto: {ex!r}"
        )
        for key in ("id", "kind", "target"):
            assert isinstance(ex.get(key), str) and ex.get(key).strip(), (
                "PD-3 violada: un ejemplo no declara `id`/`kind`/`target` "
                f"(§2.3): {ex!r}"
            )
        assert ("input" in ex) or ("command" in ex), (
            "PD-3 violada: un ejemplo no declara su `input` ni su `command` "
            f"(§2.3): {ex!r}"
        )
    return examples


def _is_status_example(ex: dict) -> bool:
    tokens = _tokens(ex.get("command"))
    if not tokens:
        return False
    return any(t == "status" for t in tokens) and any(
        "cdad_packet" in t for t in tokens
    )


def _is_dispatch_example(ex: dict) -> bool:
    obj = _as_obj(ex.get("input"))
    return isinstance(obj, dict) and set(DISPATCH_KEYS) <= set(obj)


def _is_continuity_example(ex: dict) -> bool:
    obj = _as_obj(ex.get("input"))
    return isinstance(obj, dict) and set(CONTINUITY_REQUIRED) <= set(obj)


def _require(examples: list[dict], predicate, label: str, why: str) -> dict:
    found = next((ex for ex in examples if predicate(ex)), None)
    assert found is not None, (
        f"PD-3 violada: el asset canónico no incluye el ejemplo mínimo "
        f"exigido — {label} ({why})"
    )
    return found


def _rel_target(target: object, default: str) -> str:
    if isinstance(target, str):
        t = target.strip()
        if t.endswith(".json") and not t.startswith("/") and " " not in t:
            return t
    return default


def _exec_context() -> dict:
    """Execution context mínimo para ejecutar el ejemplo de continuidad."""
    return {
        "schema_version": 1,
        "execution_id": "exec-t2-red-001",
        "runtime": "opencode",
        "hitl_delegation": {
            "authority_ref": "docs/epics/epic-fixture/execution.md",
            "expires_on": "2099-12-31",
        },
    }


class _Project:
    """Proyecto sintético autocontenido en un tempdir, con HOME aislado."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        build_project(self.root)

    def env(self) -> dict:
        env = dict(os.environ)
        env["HOME"] = str(self.home)  # NUNCA el HOME real
        return env

    def run(self, argv: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            argv,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT if cwd is None else cwd),
            env=self.env(),
            stdin=subprocess.DEVNULL,
            timeout=CLI_TIMEOUT_S,
        )

    def write_json(self, rel: str, doc: object) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(doc, str):
            path.write_text(doc, encoding="utf-8")
        else:
            path.write_text(
                json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        return path

    def prepare(self) -> None:
        proc = self.run(
            [
                sys.executable, str(PACKET_CLI), "prepare",
                "--project-root", str(self.root),
                "--role", "test-writer", "--substage", "red",
                "--objective", "005-003 T2 fixture",
            ]
        )
        assert proc.returncode == 0, (
            "fixture: `prepare` del proyecto sintético debe tener éxito; "
            f"rc={proc.returncode}; stderr={proc.stderr.strip()!r}"
        )

    def packet_id(self) -> str:
        pid = (read_state(self.root).get("active_packet") or {}).get("id")
        assert pid, "fixture: no hay paquete activo tras `prepare`"
        return pid

    def snapshot(self) -> dict:
        return tree_snapshot(self.root)


@pytest.fixture
def project(tmp_path: Path) -> _Project:
    return _Project(tmp_path)


def _run_dispatch(project: _Project, ex: dict) -> subprocess.CompletedProcess:
    """Ejecuta el ejemplo del registro de despacho contra el CLI del árbol."""
    project.prepare()
    target = _rel_target(ex.get("target"), "docs/attempt.json")
    input_path = project.write_json(target, ex["input"])
    attempt = ex.get("attempt_id") or "t2-red-a1"
    return project.run(
        [
            sys.executable, str(PACKET_CLI), "prepare",
            "--project-root", str(project.root),
            "--record-dispatch", project.packet_id(),
            "--attempt-id", str(attempt),
            "--input", str(input_path),
        ]
    )


def _run_continuity(project: _Project, ex: dict) -> subprocess.CompletedProcess:
    """Ejecuta el UPDATE de continuidad del asset contra el CLI del árbol."""
    exec_ctx = project.write_json(".cdad/fixtures/exec.json", _exec_context())
    target = _rel_target(ex.get("target"), "docs/update.json")
    update_path = project.write_json(target, ex["input"])
    return project.run(
        [
            sys.executable, str(CONTINUITY_CLI), "begin",
            "--project-root", str(project.root),
            "--execution-context", str(exec_ctx),
            "--update", str(update_path),
        ]
    )


def _substitute_status_command(tokens: list[str], root: Path) -> list[str]:
    """Resuelve los marcadores declarados de la invocación de la vista."""
    out: list[str] = []
    for i, tok in enumerate(tokens):
        if i == 0 and tok in {"python", "python3"}:
            out.append(sys.executable)
            continue
        tok = tok.replace("<skill-dir>", str(SKILL_DIR))
        tok = tok.replace("<ABS>", str(root))
        tok = tok.replace("{project_root}", str(root))
        tok = tok.replace("<PROJECT_ROOT>", str(root))
        tok = tok.replace("<project-root>", str(root))
        out.append(tok)
    if "--project-root" not in out:
        out += ["--project-root", str(root)]
    return out


def _run_status(project: _Project, ex: dict) -> subprocess.CompletedProcess:
    """Ejecuta la invocación de la vista declarada por el asset."""
    tokens = _tokens(ex.get("command"))
    assert tokens, (
        "PD-3 violada: el ejemplo de la vista `status` no declara su "
        f"`command` (invocación válida, §2.3): {ex!r}"
    )
    argv = _substitute_status_command(tokens, project.root)
    return project.run(argv)


def _window_around(text: str, pattern: re.Pattern, radius: int = 4):
    """Ventanas de líneas alrededor de cada coincidencia (para co-ocurrencia)."""
    lines = text.splitlines()
    windows = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            lo, hi = max(0, i - radius), min(len(lines), i + radius + 1)
            windows.append("\n".join(lines[lo:hi]))
    return windows


# ---------------------------------------------------------------- PD-3


def test_pd3_asset_declares_minimum_examples() -> None:
    """PD-3: los ejemplos viven en el asset canónico declarado por la spec y su
    conjunto mínimo (attempt.json, UPDATE de continuidad, invocación de la
    vista `status`) está presente; se localizan por el asset, nunca por prosa.

    Enmienda de oráculo (test-writer): la spec §2.3 fija el CONTENIDO MÍNIMO
    del `UPDATE` (las cuatro claves de contenido; `budget` opcional), NO un
    conjunto exclusivo de claves. El CLI de continuidad exige además las claves
    de idempotencia `packet_id` (string no vacío) y `attempt` (int) de nivel
    superior y falla cerrado sin ellas, así que las claves permitidas se acotan
    al contenido mínimo + `budget` + esas dos claves del CLI; exigir exclusividad
    a `{goal, decisions, uncertainties, next_action, budget}` contradecía al CLI
    y era insatisfacible a la vez que
    `test_pd3_continuity_update_example_executes`."""
    asset = _load_json(ASSET)
    examples = _examples(asset)

    dispatch = _require(
        examples, _is_dispatch_example,
        "archivo de entrada del registro de despacho",
        "docs/attempt.json con runtime, model_configured, model_reported, "
        "session, started_at + provenance",
    )
    continuity = _require(
        examples, _is_continuity_example,
        "UPDATE de continuidad",
        "goal/decisions/uncertainties/next_action (+ budget opcional)",
    )
    _require(
        examples, _is_status_example,
        "invocación válida de la vista `status`",
        "cdad_packet.py status --project-root <ABS>",
    )

    # §2.3: «campos exactos» del attempt.json.
    dispatch_obj = _as_obj(dispatch["input"])
    assert set(dispatch_obj) == set(DISPATCH_KEYS), (
        "PD-3 violada: el ejemplo del registro de despacho no declara los "
        f"campos EXACTOS exigidos (§2.3): {sorted(dispatch_obj)} != "
        f"{sorted(DISPATCH_KEYS)}"
    )
    # §2.3: el UPDATE exige las cuatro claves de CONTENIDO; `budget` es
    # opcional y el CLI exige además la idempotencia (`packet_id`, `attempt`).
    cont_obj = _as_obj(continuity["input"])
    assert set(CONTINUITY_REQUIRED) <= set(cont_obj), (
        "PD-3 violada: el UPDATE de continuidad no declara "
        f"goal/decisions/uncertainties/next_action: {sorted(cont_obj)}"
    )
    assert set(cont_obj) <= CONTINUITY_ALLOWED, (
        "PD-3 violada: el UPDATE de continuidad declara claves fuera del "
        "contrato (§2.3: contenido mínimo + `budget` opcional + las claves de "
        f"idempotencia exigidas por el CLI): "
        f"{sorted(set(cont_obj) - CONTINUITY_ALLOWED)}"
    )


def test_pd3_dispatch_record_example_executes(project: _Project) -> None:
    """PD-3: el ejemplo del registro de despacho se EJECUTA contra la versión
    correspondiente (el CLI del árbol) y tiene éxito (rc=0)."""
    examples = _examples(_load_json(ASSET))
    dispatch = _require(
        examples, _is_dispatch_example,
        "archivo de entrada del registro de despacho", "docs/attempt.json",
    )
    proc = _run_dispatch(project, dispatch)
    assert proc.returncode == 0, (
        "PD-3 violada: el ejemplo del registro de despacho no se ejecuta "
        f"contra el CLI del árbol (rc={proc.returncode}); "
        f"stderr={proc.stderr.strip()!r}"
    )
    assert "Traceback" not in proc.stderr, (
        "PD-3 violada: la ejecución del ejemplo terminó con traceback: "
        f"{proc.stderr.strip()!r}"
    )


def test_pd3_continuity_update_example_executes(project: _Project) -> None:
    """PD-3: el UPDATE de continuidad se EJECUTA contra la versión
    correspondiente (el CLI del árbol) y tiene éxito (rc=0)."""
    examples = _examples(_load_json(ASSET))
    continuity = _require(
        examples, _is_continuity_example,
        "UPDATE de continuidad", "goal/decisions/uncertainties/next_action",
    )
    proc = _run_continuity(project, continuity)
    assert proc.returncode == 0, (
        "PD-3 violada: el UPDATE de continuidad no se ejecuta contra el CLI "
        f"del árbol (rc={proc.returncode}); stderr={proc.stderr.strip()!r}"
    )
    assert "Traceback" not in proc.stderr, (
        "PD-3 violada: la ejecución del UPDATE terminó con traceback: "
        f"{proc.stderr.strip()!r}"
    )


def test_pd3_status_invocation_example_executes(project: _Project) -> None:
    """PD-3: la invocación válida de la vista `status` se EJECUTA contra la
    versión correspondiente y emite su documento (rc=0)."""
    examples = _examples(_load_json(ASSET))
    status_ex = _require(
        examples, _is_status_example,
        "invocación válida de la vista `status`",
        "cdad_packet.py status --project-root <ABS>",
    )
    proc = _run_status(project, status_ex)
    assert proc.returncode == 0, (
        "PD-3 violada: la invocación de la vista del asset no se ejecuta "
        f"contra el CLI del árbol (rc={proc.returncode}); "
        f"stderr={proc.stderr.strip()!r}"
    )
    assert proc.stdout.strip(), (
        "PD-3 violada: la invocación de la vista no emitió su documento: "
        f"stderr={proc.stderr.strip()!r}"
    )
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "PD-3 violada: la invocación de la vista no emitió un documento "
            f"JSON válido: {proc.stdout[:200]!r}"
        ) from exc
    assert isinstance(doc, dict), (
        f"PD-3 violada: el documento de la vista no es un objeto JSON: {doc!r}"
    )


def test_pd3_invalid_example_fails_naming_the_field(project: _Project) -> None:
    """PD-3 borde: un ejemplo inválido (attempt.json sin `runtime`) falla con el
    diagnóstico que NOMBRA el campo ausente."""
    examples = _examples(_load_json(ASSET))
    dispatch = _require(
        examples, _is_dispatch_example,
        "archivo de entrada del registro de despacho", "docs/attempt.json",
    )
    invalid = {k: v for k, v in _as_obj(dispatch["input"]).items() if k != "runtime"}
    assert "runtime" not in invalid

    project.prepare()
    input_path = project.write_json("docs/attempt-invalid.json", invalid)
    proc = project.run(
        [
            sys.executable, str(PACKET_CLI), "prepare",
            "--project-root", str(project.root),
            "--record-dispatch", project.packet_id(),
            "--attempt-id", "t2-red-invalid",
            "--input", str(input_path),
        ]
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        "PD-3 violada: un ejemplo inválido (attempt.json sin `runtime`) fue "
        f"aceptado (rc={proc.returncode})"
    )
    assert "Traceback" not in proc.stderr, (
        f"PD-3 violada: el fallo del ejemplo inválido es un traceback: {out!r}"
    )
    assert re.search(r"\bruntime\b", out), (
        "PD-3 violada: el diagnóstico del ejemplo inválido no NOMBRA el campo "
        f"ausente (`runtime`): {out.strip()!r}"
    )


# ---------------------------------------------------------------- PD-5


def test_pd5_reference_declares_real_rc_capture_and_repro(project: _Project) -> None:
    """PD-5: el patrón de captura del `rc` vive en la referencia operativa
    (`orientation.md`) y captura el rc REAL del CLI (no el de la tubería:
    `PIPESTATUS[0]`, no `$?`); una invocación que falla, capturada con el
    patrón, reporta el rc real ≠ 0 (no un 0 enmascarado) y el error accionable
    nombra la causa y el camino de recuperación."""
    text = _load_text(ORIENTATION)

    # El patrón declarado existe y captura el rc del CLI real.
    assert re.search(r"\bPIPESTATUS\b", text), (
        "PD-5 violada: `orientation.md` no declara el patrón de captura del rc "
        "real (`PIPESTATUS[0]`, no `$?`)"
    )
    assert re.search(r"PIPESTATUS\s*\[\s*0\s*\]", text), (
        "PD-5 violada: `orientation.md` no declara `PIPESTATUS[0]` como la "
        "fuente del rc real (el de la tubería lo sustituye)"
    )
    assert re.search(r"(?i)pipefail|tuber[ií]a|pipe\b|head|tail", text), (
        "PD-5 violada: `orientation.md` no declara el riesgo de enmascarar el "
        "rc con una tubería (`set -o pipefail` / head / tail)"
    )

    # §2.5: salida acotada para el contexto, evidencia completa por referencia.
    bounded_re = re.compile(r"(?i)--max-bytes|acotad\w*|bounded|truncat\w*")
    evidence_windows = _window_around(text, re.compile(r"(?i)evidencia|evidence"))
    assert any(
        bounded_re.search(w) and re.search(r"(?i)referencia|reference", w)
        for w in evidence_windows
    ), (
        "PD-5 violada: `orientation.md` no declara la salida acotada con la "
        "evidencia completa disponible por referencia (§2.5)"
    )

    # Reproducción observable: el rc capturado es el del CLI real, no el 0 de
    # la tubería; el error nombra la causa y la recuperación. La invocación que
    # falla usa una raíz INEXISTENTE: bajo la resolución unificada de 005-011
    # (fila 11, PD-2/PD-3) una raíz relativa ya NO falla, así que el fixture de
    # fallo de PD-5 se corrige (el oráculo de captura del rc se conserva).
    missing = project.base / "missing-root"
    assert not missing.exists(), "fixture: la raíz inexistente no debe existir"
    direct = project.run(
        [sys.executable, str(PACKET_CLI), "validate-state",
         "--project-root", str(missing)],
        cwd=project.root,
    )
    assert direct.returncode != 0, (
        "fixture: se esperaba una invocación que falla (raíz inexistente); "
        f"rc={direct.returncode}"
    )

    script = (
        f"{shlex.quote(sys.executable)} {shlex.quote(str(PACKET_CLI))} "
        f"validate-state --project-root {shlex.quote(str(missing))} | head -c 200\n"
        "printf '\\nRC_PIPE=%s RC_REAL=%s\\n' \"$?\" \"${PIPESTATUS[0]}\"\n"
    )
    piped = subprocess.run(
        ["bash", "-c", script],
        cwd=str(project.root),
        capture_output=True,
        text=True,
        env=project.env(),
        stdin=subprocess.DEVNULL,
        timeout=CLI_TIMEOUT_S,
    )
    out = piped.stdout + piped.stderr
    match = re.search(r"RC_PIPE=(\d+)\s+RC_REAL=(\d+)", out)
    assert match, (
        "fixture: no se pudo leer el rc capturado según el patrón declarado: "
        f"{out!r}"
    )
    rc_pipe, rc_real = int(match.group(1)), int(match.group(2))
    assert rc_real == direct.returncode, (
        "PD-5 violada: el rc capturado con el patrón no es el del CLI real "
        f"({rc_real} != {direct.returncode})"
    )
    assert rc_real != 0, (
        "PD-5 violada: el patrón reportó un rc enmascarado (0) en vez del rc "
        f"real de la invocación que falla: {out!r}"
    )
    assert rc_pipe == 0, (
        "fixture: la tubería debía enmascarar el rc (`$?` = 0); "
        f"RC_PIPE={rc_pipe}"
    )

    # Error accionable: formato `ERROR: …` y recuperación legítima.
    assert re.search(r"ERROR:", out), (
        "PD-5 violada: el error no usa el formato accionable `ERROR: …`: "
        f"{out.strip()!r}"
    )
    assert re.search(r"(?i)existing directory", out), (
        "PD-5 violada: el error accionable no nombra el camino de recuperación "
        f"(la raíz debe ser un directorio existente): {out.strip()!r}"
    )

    # §2.5: el error accionable no habilita atajos — la referencia declara las
    # prohibiciones (no ampliar alcances, fabricar aprobaciones ni borrar
    # registros).
    prohibitions = {
        "no ampliar alcances": re.compile(
            r"(?i)(no|nunca|never|not)[^.\n]{0,50}ampli\w*"
        ),
        "no fabricar aprobaciones": re.compile(
            r"(?i)(no|nunca|never|not)[^.\n]{0,50}fabric\w*"
        ),
        "no borrar registros": re.compile(
            r"(?i)(no|nunca|never|not)[^.\n]{0,50}(borrar|borres|delete)"
        ),
    }
    declared = [label for label, rx in prohibitions.items() if rx.search(text)]
    assert len(declared) >= 2, (
        "PD-5 violada: `orientation.md` no declara las prohibiciones del error "
        "accionable (§2.5: no ampliar alcances, fabricar aprobaciones ni "
        f"borrar registros); declaradas: {declared}"
    )


# ---------------------------------------------------------------- PD-4


def test_pd4_reference_distinguishes_absence_from_incoherence() -> None:
    """PD-4: el verdicto reusa el `cdad-version-check.py` instalado y la
    referencia distingue AUSENCIA (`UNKNOWN`/`NO-PROJECT-AGENTS`) de
    INCOHERENCIA (`DRIFT`); borde: sin marcador → ausencia, versiones
    divergentes → DRIFT."""
    text = _load_text(ORIENTATION)

    assert re.search(r"cdad-version-check\.py", text), (
        "PD-4 violada: la referencia no reusa el medidor de versión instalado "
        "(`cdad-version-check.py`)"
    )
    for verdict in ("UNKNOWN", "NO-PROJECT-AGENTS", "DRIFT"):
        assert re.search(re.escape(verdict), text), (
            f"PD-4 violada: la referencia no nombra el verdicto {verdict} (§2.4)"
        )

    absence_re = re.compile(r"(?i)ausencia|absence|no verificado|not verified")
    absence_windows = _window_around(
        text, re.compile(r"UNKNOWN|NO-PROJECT-AGENTS")
    )
    assert any(absence_re.search(w) for w in absence_windows), (
        "PD-4 violada: `UNKNOWN`/`NO-PROJECT-AGENTS` no se declaran como "
        "AUSENCIA (versión no verificada)"
    )

    incoherence_re = re.compile(r"(?i)incoherencia|incoherence")
    drift_windows = _window_around(text, re.compile(r"\bDRIFT\b"))
    assert any(incoherence_re.search(w) for w in drift_windows), (
        "PD-4 violada: `DRIFT` no se declara como INCOHERENCIA (distinta de "
        "la ausencia)"
    )


def test_pd4_absent_meter_declared_as_absence_not_drift() -> None:
    """PD-4 borde: el caso «medidor no instalado» se declara AUSENCIA, no
    `DRIFT` (la ausencia del medidor no es incoherencia)."""
    text = _load_text(ORIENTATION)

    meter_re = re.compile(r"(?i)medidor|meter")
    absent_re = re.compile(r"(?i)no instalad|not installed|ausente|absent")
    absence_re = re.compile(r"(?i)ausencia|absence")
    negation_re = re.compile(r"(?i)\bno\b|\bnunca\b|\bnever\b|\bnot\b|distinta|≠")

    absent_windows = [
        w for w in _window_around(text, meter_re) if absent_re.search(w)
    ]
    assert absent_windows, (
        "PD-4 violada: la referencia no declara el caso «medidor no instalado» "
        "(§2.4)"
    )
    assert any(absence_re.search(w) for w in absent_windows), (
        "PD-4 violada: el caso «medidor no instalado» no se declara como "
        "AUSENCIA"
    )
    for window in absent_windows:
        if re.search(r"\bDRIFT\b", window):
            assert negation_re.search(window), (
                "PD-4 violada: la referencia presenta el medidor ausente como "
                f"`DRIFT` (debe ser ausencia, no incoherencia): {window!r}"
            )


# ---------------------------------------------------------------- PD-11


def test_pd11_start_procedure_names_status_view_as_orientation_action() -> None:
    """PD-11 (i): el procedimiento canónico de arranque y reentrada nombra la
    vista `status` como acción de orientación. Oráculo DOCUMENTAL: lee el
    documento por su ruta declarada y NO afirma la propiedad «primero» (esa la
    observa la aceptación en T5)."""
    text = _load_text(PROJECT_START)

    status_re = re.compile(r"\bstatus\b")
    view_re = re.compile(
        r"(?i)cdad_packet|orientation\.md|--project-root|vista compacta|"
        r"compact view|vista de estado"
    )
    windows = _window_around(text, status_re, radius=4)
    assert any(view_re.search(w) for w in windows), (
        "PD-11 violada: el procedimiento de arranque no nombra la vista "
        "`status` como acción de orientación (no aparece `status` junto a su "
        "CLI/referencia)"
    )


def test_pd11_start_procedure_declares_expand_only_on_concrete_need() -> None:
    """PD-11 (ii): el procedimiento declara la regla de ampliar solo ante una
    necesidad concreta (un bloqueo o una duda que afecte al siguiente
    despacho). Oráculo DOCUMENTAL sobre la ruta declarada."""
    text = _load_text(PROJECT_START)

    expand_re = re.compile(r"(?i)ampli\w*|expand\w*|widen")
    need_re = re.compile(
        r"(?i)necesidad concreta|concrete need|bloqueo|blocker|duda|doubt|"
        r"motivo|reason"
    )
    windows = _window_around(text, expand_re, radius=4)
    assert windows, (
        "PD-11 violada: el procedimiento no declara la regla de ampliación "
        "(no menciona ampliar/expandir)"
    )
    assert any(need_re.search(w) for w in windows), (
        "PD-11 violada: el procedimiento no declara que se amplía solo ante "
        "una necesidad concreta (un bloqueo o una duda que afecte al siguiente "
        "despacho)"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
