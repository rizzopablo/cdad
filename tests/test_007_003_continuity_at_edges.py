#!/usr/bin/env python3
"""RED 007-003 — continuidad verificable en los bordes del recorrido.

Contract (aprobada 2026-10-24):
- `docs/specs/007-003-continuity-at-edges/spec.md` §2.1 (identidad y
  comprobación previa: `verify-begin`), §2.2 (integración en los bordes
  ejecutables: transporte nativo y externo, registro canónico), §2.3
  (cierre común de recepción: `checkpoint-receipt`, enlace histórico `prev`,
  identidad/unicidad del cierre y origen de `attempt`), §2.4 (recuperación de
  interrupciones), §2.5 (evidencia con aplicabilidad explícita), §2.6
  (proyección y compatibilidad), §3 (INV-1..INV-10) y §4 (PC-01..PC-06 con
  los nombres estables de cada test).
- Insumos de contexto: `docs/specs/007-003-continuity-at-edges/discovery.md`
  y `review-001.md` (los tres BLOCKING que la spec resuelve).

Superficie observable bajo prueba (CAJA NEGRA: SOLO subproceso sobre los CLI
del repo; ningún módulo de implementación se importa ni se lee):

    python3 skills/cdad-cycle/scripts/cdad_continuity.py verify-begin \\
        --project-root ROOT --execution-context EXEC.json \\
        --packet PACKET_ID --attempt N [--json]
    python3 skills/cdad-cycle/scripts/cdad_continuity.py checkpoint-receipt \\
        --project-root ROOT --execution-context EXEC.json \\
        --packet PACKET_ID --attempt N --receipt RECEIPT.json [--json]
    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare \\
        --project-root ROOT --record-dispatch PACKET_ID \\
        --attempt-id ID --input OBS.json --continuity-attempt N
    python3 skills/cdad-cycle/scripts/cdad_dispatch.py dispatch|record \\
        --project-root ROOT --packet PACKET_ID --runtime RT \\
        [--attempt-id ID] --continuity-attempt N
    python3 skills/cdad-cycle/scripts/cdad_delegate.py \\
        --project-root ROOT --packet PACKET_ID --destination DEST \\
        --exec-config CFG.json --continuity-attempt N
    python3 skills/cdad-cycle/scripts/cdad_result.py receive \\
        --project-root ROOT --execution-context EXEC.json \\
        --packet PACKET.md --request REQUEST.json --descriptor RESULT.json \\
        --continuity-attempt N [--late]
    python3 skills/cdad-cycle/scripts/cdad_result.py validate-receipt \\
        --project-root ROOT --receipt RECEIPT.json \\
        [--close-continuity --continuity-attempt N]

Y, como control/observación del almacenamiento existente:
`cdad_continuity.py begin|checkpoint|resume` y `cdad_packet.py
register-transition`.

Fixture: proyecto descartable en un tempdir (política, contrato, autoridad y
state de `tests/test_004_002_t2_bootstrap.build_project`), con el `HOME` y el
`XDG_CONFIG_HOME` del subproceso en tempdirs VACÍOS (nunca el HOME real,
nunca este repo). La capa previa de despacho se produce por el camino
legítimo del CLI (`prepare` → `begin` → `prepare --record-dispatch`) en los
tests de PC-02; para aislar la RECEPCIÓN/CIERRE, el fixture reconstruye el
estado posterior al despacho con la forma REAL del registro I8 de 006-005 y
el binding `dispatched` (nunca inventa un recibo, un cuerpo ni un cierre).
Las variantes que el productor no emite (cuerpos legados, cuerpos huérfanos,
cabezas incoherentes, recibos copiados) se construyen en el fixture a partir
de un artefacto REAL del productor. Los ids son sintéticos y anónimos. El
transporte externo se observa con un módulo de runtime de FIXTURE (no
producto) colocado junto a una copia descartable del skill: el módulo registra
cada invocación en un JSONL y sólo imprime su sobre cuando se lo ejecuta como
proceso; así «no se lanzó el worker» es un hecho observable, no una
inferencia.

Mapeo test → postcondición (spec §4):

  test_transport_requires_current_matching_begin
      -> PC-01: sin `begin` vigente (ausente, checkpoint posterior, cuerpo
         alterado, `record` histórico ausente, cabeza de otro intento,
         ejecución/paquete/contexto discordantes, autoridad expirada o flag
         ausente) el transporte externo se rechaza ANTES de lanzar el worker;
         con prueba válida continúa el transporte existente.
  test_native_dispatch_and_registration_require_begin
      -> PC-02: los cuerpos canónicos del orquestador y su derivado declaran
         la comprobación inmediatamente antes de la herramienta nativa; el
         registro canónico (`prepare --record-dispatch`) y el verbo nativo
         `record` rechazan un intento nuevo sin la prueba, sin publicar
         estado, observación ni staging; un replay byte-idéntico de un
         registro durable conserva su idempotencia.
  test_receive_closes_continuity_idempotently
      -> PC-03: la recepción ordinaria deja recibo durable + checkpoint, sin
         tocar `semantic_status=pending`; repetirla no agrega enlaces ni
         repite efectos; sin `--continuity-attempt` falla cerrado sin
         escribir; un `N` discordante se rechaza salvo cierre idéntico
         demostrable; `receive --late` conserva las mismas reglas (intento
         ausente, discordante sin cierre, cierre idéntico con cabeza de otro
         intento y ejecución cerrada).
  test_external_durable_receipt_uses_common_continuity_close
      -> PC-04: un recibo durable externo converge al MISMO cierre común sin
         staged ni nueva recepción; repetir la validación con cierre no
         altera la cadena; recibo ilegible e identidad ajena se rechazan.
  test_interrupted_receipt_or_transition_recovers_only_missing_checkpoint
      -> PC-05: interrupciones después del recibo y después de la transición
         se recuperan cerrando únicamente continuidad; recibo y transición
         permanecen idénticos; cabeza adelantada se rechaza sin rebobinar;
         con varios eslabones posteriores el cierre se localiza por
         encadenamiento; un cuerpo huérfano no cuenta como cierre ni
         antecedente; un cuerpo legado sin `prev` es historia no demostrable.
  test_repair_preserves_history_and_invalidates_evidence_explicitly
      -> PC-06: replay del cierre (inmediato, tras varios checkpoints y con
         cabeza de otro intento) devuelve la identidad original sin alterar
         archivos; misma clave con contenido distinto se rechaza; rutas
         equivalentes son la misma; otro `attempt` es otro cierre; `begin` y
         `checkpoint` idénticos conservan bytes/digest/secuencia, `begin`
         divergente rechaza y `checkpoint` divergente agrega un enlace;
         alterar `prev` sin digest o publicar cabeza/cuerpo incoherentes se
         rechaza sin reparación; la reparación conserva el antecedente,
         proyecta la evidencia invalidada con motivo y no la rehabilita por
         igualdad, cambio de hash ni reanclaje; los cuerpos antiguos siguen
         leyéndose.

RED hoy (HEAD f557e26, medido con esta misma fixture):
- `verify-begin` y `checkpoint-receipt` NO existen (`invalid choice`) y
  `--continuity-attempt` NO existe en `prepare`/`dispatch`/`record`/
  `receive`/`validate-receipt`/`cdad_delegate.py` (`unrecognized arguments`):
  cada caso falla en la ASERCIÓN de superficie declarada, nunca por
  ImportError, SyntaxError, JSONDecodeError ni error de fixture.
- El cuerpo de `begin`/`checkpoint` no declara `prev` (§2.3.1) y la proyección
  de `resume` no emite `changes`/`evidence` (§2.5/§2.6): los casos de cadena
  demostrable y de evidencia fallan en su aserción de contrato.
- El transporte externo arranca el worker sin `begin` vigente y el registro
  canónico acepta un intento nuevo sin prueba: las variantes de rechazo
  fallan en `rc≠0`/`worker no lanzado`, con el mensaje de contrato.
- En PC-04/PC-05/PC-06 la capa previa de recepción usa el camino legítimo
  (`receive --continuity-attempt N`); hoy ese flag no existe, así que esos
  tests fallan primero en la superficie de `receive` y, una vez exista,
  recorren sus aserciones propias de cierre/recuperación/evidencia (el orden
  de la spec: el cierre ocurre DESPUÉS de publicar o reconocer el recibo).
- Los casos marcados GUARD (idempotencia de `begin`/`checkpoint`, split-brain
  del `begin` divergente, replay durable del registro, `resume` de solo
  lectura) ya se cumplen hoy y se conservan para que la extensión no los
  relaje; no se les inventa un oráculo nuevo.

Límite declarado (spec §2.2 y §7): la comprobación documental del wiring
nativo se asevera sobre `sources/roles/orchestrator.md` y su derivado
`agents/cdad-orchestrator.md`; NO se presenta como interceptación empírica de
una herramienta del runtime.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from test_004_002_t2_bootstrap import build_project

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
PACKET_CLI = SKILL_DIR / "scripts" / "cdad_packet.py"
CONTINUITY_CLI = SKILL_DIR / "scripts" / "cdad_continuity.py"
RESULT_CLI = SKILL_DIR / "scripts" / "cdad_result.py"
DISPATCH_CLI = SKILL_DIR / "scripts" / "cdad_dispatch.py"
DELEGATE_CLI = SKILL_DIR / "scripts" / "cdad_delegate.py"
ORCHESTRATOR_SOURCE = REPO_ROOT / "sources" / "roles" / "orchestrator.md"
ORCHESTRATOR_DERIVED = REPO_ROOT / "agents" / "cdad-orchestrator.md"

ROLE = "test-writer"
SUBSTAGE = "red"
OBJECTIVE = "007-003 continuidad en los bordes (fixture demo-700)"
APPROVER = "Demo Approver"
AUTHORITY_REF = "docs/epics/epic-004-single-source-planning/execution.md"
CLOSURE_REL = "docs/closures/demo-700-closure.md"
STATE_REL = "docs/.cdad-state.json"
RECEIPT_NAME = "receipt.json"
CLI_TIMEOUT_S = 120

FIXTURE_RUNTIME = "demo700fix"
FIXTURE_ATTEMPT_ID = "attempt-demo-700-001"
FIXTURE_SESSION = "ses-demo-700-0001"

# §2.1/§2.3: el entero de continuidad NO es el `--attempt-id` textual.
TEXTUAL_ATTEMPT = "1"

# §2.3.1: vocabulario del enlace histórico.
PREV_KEY = "prev"
RECEIPT_CHECKPOINT_KEY = "receipt_checkpoint"
# §2.5: vocabulario cerrado de la aplicabilidad.
EVIDENCE_STATUSES = {"vigente", "invalidada"}

# Señales de que la superficie declarada todavía no existe (RED por CLI
# ausente): un «rechazo» observado así es un error de uso, no el
# comportamiento bajo prueba.
SURFACE_TOKENS = (
    "unrecognized arguments",
    "invalid choice",
    "no such option",
    "unknown command",
)

# Condición de continuidad: el diagnóstico del rechazo debe nombrarla.
CONTINUITY_PATTERN = re.compile(
    r"(?i)continu|begin|intent|attempt|receipt|recibo|cadena|chain|"
    r"identit|execution|ejecuci|packet|paquete|autoridad|authority")
# §2.3.1: diagnósticos de integridad/enlace histórico.
CHAIN_PATTERN = re.compile(
    r"(?i)prev|legacy|legado|historia|history|demostr|digest|hash|"
    r"integridad|integrity|incoher|chain|cadena")

# El módulo de runtime del FIXTURE (NO producto): registra su invocación y
# sólo imprime el sobre cuando se lo ejecuta como proceso.
FIXTURE_MODULE_SOURCE = '''#!/usr/bin/env python3
"""FIXTURE runtime module of tests/test_007_003_continuity_at_edges.py.

NOT product. Declared behavior:
- appends every invocation to `fixture-calls.jsonl` (argv + cwd);
- `--capabilities` answers the five declared keys;
- `--observe` answers `null` (no durable store in the fixture);
- otherwise writes a byte-exact final text next to itself and prints the
  declared envelope only when executed as a process (never contaminates an
  in-process invocation);
- exits 0 without touching the project.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "fixture-calls.jsonl"
FINAL = HERE / "fixture-final.md"
CAPABILITIES = {
    "native_observation": True,
    "external_transport": True,
    "session_correlation": False,
    "version": "demo700fix 1.0",
    "reason": None,
}


def _log(entry):
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True, default=str) + "\\n")


def _direct():
    return Path(sys.argv[0] or "").resolve().name == Path(__file__).name


ARGV = list(sys.argv[1:])
_log({"argv": ARGV, "cwd": os.getcwd()})

if "--capabilities" in ARGV:
    if _direct():
        sys.stdout.write(json.dumps(CAPABILITIES, sort_keys=True) + "\\n")
        sys.stdout.flush()
    sys.exit(0)

if "--observe" in ARGV:
    if _direct():
        sys.stdout.write("null\\n")
        sys.stdout.flush()
    sys.exit(0)

FINAL.write_text("# fixture final text (007-003)\\n", encoding="utf-8")
envelope = {
    "attempt": "attempt-fixture-007-003",
    "session": "ses-fixture-007-003",
    "termination": "completed",
    "delivery_ref": str(FINAL),
    "diagnosis": None,
}
if _direct():
    sys.stdout.write(json.dumps(envelope, sort_keys=True) + "\\n")
    sys.stdout.flush()
sys.exit(0)
'''


# ---------------------------------------------------------------- helpers


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_body_bytes(doc: dict) -> bytes:
    """Serialización canónica del cuerpo (la que usa el productor existente)."""
    return json.dumps(
        doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8")


def output(proc: subprocess.CompletedProcess) -> str:
    return (proc.stdout or "") + (proc.stderr or "")


def tail(text: str, lines: int = 30) -> str:
    return "\n".join((text or "").strip().splitlines()[-lines:])


def assert_surface(proc: subprocess.CompletedProcess, label: str,
                   surface: str) -> None:
    """Un rechazo sólo es evidencia del contrato si la superficie declarada
    existe. Un `invalid choice`/`unrecognized arguments` es RED por CLI
    ausente, no el comportamiento bajo prueba."""
    text = output(proc)
    for token in SURFACE_TOKENS:
        assert token not in text, (
            f"{label}: la superficie declarada no existe todavía ({surface}); "
            f"la salida es un error de uso del argparse, no el rechazo bajo "
            f"prueba:\n{tail(text)}")


def assert_rc0(proc: subprocess.CompletedProcess, label: str,
               what: str) -> None:
    assert proc.returncode == 0, (
        f"{label}: {what} debe completar (rc=0); rc={proc.returncode}:\n"
        f"{tail(output(proc))}")


def assert_rejected(proc: subprocess.CompletedProcess, label: str,
                    what: str, pattern: re.Pattern = CONTINUITY_PATTERN
                    ) -> None:
    assert_surface(proc, label, what)
    assert proc.returncode != 0, (
        f"{label}: {what} debe rechazarse (rc≠0); rc={proc.returncode}:\n"
        f"{tail(output(proc))}")
    text = output(proc)
    assert text.strip(), (
        f"{label}: {what} se rechazó sin diagnóstico observable")
    assert pattern.search(text), (
        f"{label}: el rechazo de {what} debe nombrar la condición de "
        f"continuidad (causa observable); visto:\n{tail(text)}")


def json_doc(proc: subprocess.CompletedProcess, label: str,
             what: str) -> dict:
    assert_rc0(proc, label, what)
    assert proc.stdout.strip(), (
        f"{label}: {what} no emitió el documento JSON por stdout:\n"
        f"{tail(output(proc))}")
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{label}: stdout de {what} no es JSON válido: "
            f"{proc.stdout[:300]!r}") from exc
    assert isinstance(doc, dict), (
        f"{label}: el documento de {what} no es un objeto JSON: {doc!r}")
    return doc


def load_json(path: Path, label: str) -> dict:
    assert path.is_file(), f"{label}: falta el artefacto declarado {path}"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssertionError(
            f"{label}: el artefacto {path} no es JSON legible: {exc}") from exc
    assert isinstance(doc, dict), (
        f"{label}: el artefacto {path} no es un objeto JSON: {doc!r}")
    return doc


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    snap: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        snap[rel] = path.read_bytes() if path.is_file() else None
    return snap


def changed_paths(before: dict, after: dict) -> set[str]:
    return {
        rel for rel in set(before) | set(after)
        if before.get(rel) != after.get(rel) or (rel in before) != (rel in after)
    }


def files_under(base: Path) -> dict[str, bytes]:
    if not base.is_dir():
        return {}
    return {
        path.relative_to(base).as_posix(): path.read_bytes()
        for path in sorted(base.rglob("*")) if path.is_file()
    }


def assert_unchanged(before: dict, after: dict, label: str,
                     what: str) -> None:
    changed = changed_paths(before, after)
    assert not changed, (
        f"{label}: {what} no debe escribir; cambiaron: {sorted(changed)}")


def require_prev(body: dict, label: str, sha: str) -> object:
    """§2.3.1: todo cuerpo NUEVO declara `prev` (null en el génesis). Un
    cuerpo sin `prev` es legado y no demuestra la cadena."""
    assert PREV_KEY in body, (
        f"{label}: §2.3.1 — el cuerpo {sha[:12]}… no declara `prev`; la "
        f"cadena no es demostrable (claves: {sorted(body)})")
    return body[PREV_KEY]


def evidence_entry(eid: str, path: str, digest: str, *, status: str = "vigente",
                   reason: str = "verifica la base declarada",
                   antecedent: dict | None = None) -> dict:
    return {
        "id": eid,
        "reference": {"path": path, "sha256": digest},
        "status": status,
        "reason": reason,
        "antecedent": antecedent,
    }


class _Cases:
    """Acumula los fallos de contrato de casos independientes de un mismo PC.

    El RED de un PC con varios escenarios debe mostrar TODOS los escenarios
    incumplidos en una sola corrida; las excepciones que no son de aserción se
    propagan intactas (un fallo de fixture nunca se disfraza de contrato).
    """

    def __init__(self) -> None:
        self.problems: list[str] = []

    def run(self, label: str, case) -> None:
        try:
            case()
        except AssertionError as exc:
            self.problems.append(f"[{label}] {exc}")

    def raise_if_any(self, pc: str) -> None:
        if self.problems:
            detail = "\n".join(self.problems)
            raise AssertionError(
                f"{pc}: casos incumplidos ({len(self.problems)}):\n{detail}")


# ---------------------------------------------------------------- fixture


class _Project:
    """Proyecto descartable con el camino legítimo del CLI hasta el despacho."""

    def __init__(self, base: Path, name: str = "proj") -> None:
        self.base = base
        self.name = name
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.config_home = base / "config-home"
        self.config_home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        build_project(self.root)
        prepared = self.prepare()
        assert_rc0(prepared, f"{name}/prepare", "`prepare` debe publicar el "
                   "paquete")
        state = self.read_state()
        active = state.get("active_packet") or {}
        self.packet_id = active.get("id")
        self.execution_id = (state.get("execution") or {}).get("id")
        self.feature_id = state.get("active_feature")
        assert self.packet_id and self.execution_id, (
            f"precondición (fixture {name}): paquete y ejecución activos: "
            f"{state!r}")
        self.ctx = (self.root / ".cdad" / "executions" / self.execution_id
                    / "execution.json")
        self._update_count = 0

    # -- CLI (caja negra) -------------------------------------------------

    def env(self) -> dict:
        env = dict(os.environ)
        env["HOME"] = str(self.home)  # NUNCA el HOME real
        env["XDG_CONFIG_HOME"] = str(self.config_home)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    def run(self, cli: Path, *args: str) -> subprocess.CompletedProcess:
        assert cli.is_file(), f"CLI del repo ausente: {cli}"
        return subprocess.run(
            [sys.executable, str(cli), *args],
            capture_output=True, text=True, cwd=REPO_ROOT, env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S)

    def prepare(self, *extra: str) -> subprocess.CompletedProcess:
        return self.run(
            PACKET_CLI, "prepare", "--project-root", str(self.root),
            "--role", ROLE, "--substage", SUBSTAGE, "--objective", OBJECTIVE,
            *extra)

    # -- continuidad ------------------------------------------------------

    def write_update(self, *, attempt: int = 1, label: str = "base",
                     **overrides: object) -> Path:
        self._update_count += 1
        doc = {
            "packet_id": self.packet_id,
            "attempt": attempt,
            "goal": f"objetivo demo-700 ({label})",
            "decisions": [{"decision": "decisión demo-700",
                           "rationale": "razón demo-700"}],
            "uncertainties": [],
            "next_action": "continuar el encargo",
            "references": [],
        }
        doc.update(overrides)
        path = self.base / "updates" / f"{self.name}-{self._update_count}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n", encoding="utf-8")
        return path

    def begin(self, *, attempt: int = 1, label: str = "begin",
              **overrides: object) -> subprocess.CompletedProcess:
        update = self.write_update(attempt=attempt, label=label, **overrides)
        return self.run(
            CONTINUITY_CLI, "begin", "--project-root", str(self.root),
            "--execution-context", str(self.ctx), "--update", str(update),
            "--json")

    def checkpoint(self, *, attempt: int = 1, label: str = "cp1",
                   max_bytes: int | None = None,
                   **overrides: object) -> subprocess.CompletedProcess:
        update = self.write_update(attempt=attempt, label=label, **overrides)
        args = [
            "checkpoint", "--project-root", str(self.root),
            "--execution-context", str(self.ctx), "--update", str(update),
            "--json",
        ]
        if max_bytes is not None:
            args += ["--max-bytes", str(max_bytes)]
        return self.run(CONTINUITY_CLI, *args)

    def resume(self, *, role: str | None = None,
               extra: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
        args = [
            "resume", "--project-root", str(self.root),
            "--execution-context", str(self.ctx), "--json",
        ]
        if role is not None:
            args += ["--role", role]
        args += list(extra)
        return self.run(CONTINUITY_CLI, *args)

    def verify_begin(self, *, attempt: int = 1, packet: str | None = None,
                     ctx: Path | None = None,
                     extra: tuple[str, ...] = ()
                     ) -> subprocess.CompletedProcess:
        args = [
            "verify-begin", "--project-root", str(self.root),
            "--execution-context", str(ctx or self.ctx),
            "--packet", packet or self.packet_id, "--attempt", str(attempt),
            "--json",
        ]
        args += list(extra)
        return self.run(CONTINUITY_CLI, *args)

    def checkpoint_receipt(self, *, attempt: int = 1,
                           receipt: Path | None = None,
                           extra: tuple[str, ...] = ()
                           ) -> subprocess.CompletedProcess:
        args = [
            "checkpoint-receipt", "--project-root", str(self.root),
            "--execution-context", str(self.ctx),
            "--packet", self.packet_id, "--attempt", str(attempt),
            "--receipt", str(receipt or self.receipt_path()), "--json",
        ]
        args += list(extra)
        return self.run(CONTINUITY_CLI, *args)

    # -- despacho y recepción ---------------------------------------------

    def write_observation(self, *, session: str = FIXTURE_SESSION,
                          name: str = "observation.json") -> Path:
        path = self.root / ".cdad" / "inbox" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "runtime": "demo-runtime",
            "model_configured": "demo-model",
            "model_reported": "demo-model",
            "session": session,
            "started_at": "2026-10-24T00:00:00Z",
            "provenance": {
                "runtime": "reported by runtime (fixture)",
                "model_configured": "orchestrator (fixture)",
                "model_reported": "orchestrator (fixture)",
                "session": "orchestrator (fixture)",
                "started_at": "orchestrator (fixture)",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def record_dispatch(self, *, attempt_id: str = FIXTURE_ATTEMPT_ID,
                        n: int = 1, with_flag: bool = True,
                        observation: Path | None = None
                        ) -> subprocess.CompletedProcess:
        observation = observation or self.write_observation()
        args = [
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", self.packet_id,
            "--attempt-id", attempt_id, "--input", str(observation),
        ]
        if with_flag:
            args += ["--continuity-attempt", str(n)]
        return self.run(PACKET_CLI, *args)

    def mark_dispatched(self, *, attempt_id: str = FIXTURE_ATTEMPT_ID) -> Path:
        """Reconstruye la capa PREVIA al recibo con la forma REAL del registro
        I8 de 006-005 y el binding de estado que publica `prepare
        --record-dispatch`.

        Es un fixture de la RECEPCIÓN/CIERRE (el paquete ya está despachado,
        como después del camino legítimo); los tests de PC-02 ejercen el
        registro canónico por su propio camino y no usan este atajo.
        """
        state = self.read_state()
        active = dict(state.get("active_packet") or {})
        active["status"] = "dispatched"
        state["active_packet"] = active
        (self.root / STATE_REL).write_text(
            json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
        record = {
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "role": ROLE,
            "substage": SUBSTAGE,
            "runtime": "demo-runtime",
            "model_configured": "demo-model",
            "model_reported": "demo-model",
            "session": FIXTURE_SESSION,
            "started_at": "2026-10-24T00:00:00Z",
            "provenance": {
                "runtime": "fixture (007-003)",
                "model_configured": "fixture (007-003)",
                "model_reported": "fixture (007-003)",
                "session": "fixture (007-003)",
                "started_at": "fixture (007-003)",
            },
        }
        path = (self.root / ".cdad" / "executions" / self.execution_id
                / "dispatches" / f"{attempt_id}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n", encoding="utf-8")
        return path

    def stage_result(self, *, part_content: bytes = b"# role report (fixture)\n",
                     name: str = "role-report.md") -> Path:
        inbox = self.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        part = inbox / name
        part.write_bytes(part_content)
        (inbox / "changes.json").write_text(json.dumps({
            "schema_version": 1,
            "observation_status": "trusted",
            "baseline_ref": "demo-baseline",
            "baseline_sha256": "0" * 64,
            "changes": [],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        descriptor = inbox / "RESULT.json"
        descriptor.write_text(json.dumps({
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "feature_id": self.feature_id,
            "source": {"kind": "staged-file", "sdk_message_ref": None},
            "parts": [{
                "name": "role-report",
                "artifact_kind": "test-writer-role-report",
                "staged_path": f".cdad/inbox/{name}",
            }],
            "observed_changes": {
                "observation_status": "trusted",
                "baseline_ref": "demo-baseline",
                "baseline_sha256": "0" * 64,
                "manifest_path": ".cdad/inbox/changes.json",
            },
            "run_evidence_ref": None,
        }, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        return descriptor

    def receive(self, *, n: int = 1, with_flag: bool = True, late: bool = False,
                descriptor: Path | None = None,
                part_content: bytes = b"# role report (fixture)\n"
                ) -> subprocess.CompletedProcess:
        descriptor = descriptor or self.stage_result(part_content=part_content)
        args = [
            "receive", "--project-root", str(self.root),
            "--execution-context", str(self.ctx),
            "--packet", str(self.packet_dir() / "PACKET.md"),
            "--request", str(self.packet_dir() / "REQUEST.json"),
            "--descriptor", str(descriptor),
        ]
        if with_flag:
            args += ["--continuity-attempt", str(n)]
        if late:
            args.append("--late")
        return self.run(RESULT_CLI, *args)

    def validate_receipt(self, *, close: bool = False, attempt: int | None = None,
                         receipt: Path | None = None,
                         extra: tuple[str, ...] = ()
                         ) -> subprocess.CompletedProcess:
        args = [
            "validate-receipt", "--project-root", str(self.root),
            "--receipt", str(receipt or self.receipt_path()),
        ]
        if close:
            args += ["--close-continuity",
                     "--continuity-attempt", str(attempt)]
        args += list(extra)
        return self.run(RESULT_CLI, *args)

    def transition(self, kind: str, **kwargs: str
                   ) -> subprocess.CompletedProcess:
        args = [
            "register-transition", "--project-root", str(self.root),
            "--transition", kind,
        ]
        for key, value in kwargs.items():
            args += [f"--{key.replace('_', '-')}", value]
        return self.run(PACKET_CLI, *args)

    def delivery(self) -> subprocess.CompletedProcess:
        return self.transition(
            "delivery", stage="tdd", packet=self.packet_id)

    def closure(self) -> subprocess.CompletedProcess:
        closure = self.root / CLOSURE_REL
        closure.parent.mkdir(parents=True, exist_ok=True)
        closure.write_text("# closure fixture demo-700\n", encoding="utf-8")
        return self.transition(
            "closure", stage="merge", approve_by=APPROVER,
            closure_path=CLOSURE_REL)

    # -- observación de artefactos ---------------------------------------

    def read_state(self) -> dict:
        return load_json(self.root / STATE_REL, f"fixture {self.name}")

    def state_bytes(self) -> bytes:
        return (self.root / STATE_REL).read_bytes()

    def continuity_dir(self) -> Path:
        return (self.root / ".cdad" / "executions" / self.execution_id
                / "continuity")

    def head_path(self) -> Path:
        return self.continuity_dir() / "head.json"

    def head(self, label: str = "head") -> dict:
        return load_json(self.head_path(), label)

    def head_bytes(self) -> bytes:
        return self.head_path().read_bytes()

    def bodies_dir(self) -> Path:
        return self.continuity_dir() / "bodies"

    def body_path(self, sha: str) -> Path:
        return self.bodies_dir() / f"{sha}.json"

    def body(self, sha: str, label: str = "body") -> dict:
        return load_json(self.body_path(sha), f"{label} ({sha[:12]}…)")

    def body_raw(self, sha: str) -> bytes:
        return self.body_path(sha).read_bytes()

    def bodies(self) -> dict[str, dict]:
        if not self.bodies_dir().is_dir():
            return {}
        return {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(self.bodies_dir().glob("*.json"))
        }

    def write_body(self, doc: dict) -> str:
        """Escribe un cuerpo con su digest real (content-addressed)."""
        raw = canonical_body_bytes(doc)
        sha = sha256_bytes(raw)
        self.bodies_dir().mkdir(parents=True, exist_ok=True)
        self.body_path(sha).write_bytes(raw)
        return sha

    def write_head(self, doc: dict) -> None:
        self.head_path().write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")

    def continuity_files(self) -> dict[str, bytes]:
        return files_under(self.continuity_dir())

    def chain(self, label: str = "cadena") -> list[tuple[str, dict]]:
        """La cadena demostrable desde la cabeza hasta el génesis (§2.3.1)."""
        head = self.head(label)
        sha = head.get("body_sha256")
        assert isinstance(sha, str) and sha, (
            f"{label}: la cabeza no declara `body_sha256`: {head!r}")
        expected_seq = head.get("seq")
        assert isinstance(expected_seq, int), (
            f"{label}: la cabeza no declara `seq` entero: {head!r}")
        links: list[tuple[str, dict]] = []
        seen: set[str] = set()
        while sha is not None:
            assert sha not in seen, (
                f"{label}: la cadena se cicla en {sha[:12]}…")
            seen.add(sha)
            body = self.body(sha, label)
            links.append((sha, body))
            prev = require_prev(body, label, sha)
            if prev is None:
                assert expected_seq == 1, (
                    f"{label}: §2.3.1 — el génesis (prev=null) debe ser "
                    f"seq 1; la cadena llegó a seq {expected_seq}")
                break
            assert isinstance(prev, dict), (
                f"{label}: §2.3.1 — `prev` debe ser null o un objeto: "
                f"{prev!r}")
            assert prev.get("seq") == expected_seq - 1, (
                f"{label}: §2.3.1 — `prev.seq` debe decrecer en 1: "
                f"esperado {expected_seq - 1}, visto {prev.get('seq')!r}")
            sha = prev.get("checkpoint_sha256")
            expected_seq -= 1
        return links

    def chain_shas(self, label: str = "cadena") -> list[str]:
        return [sha for sha, _ in self.chain(label)]

    def close_links(self, attempt: int, label: str = "cierre"
                    ) -> list[tuple[str, dict]]:
        found = []
        for sha, body in self.bodies().items():
            marker = body.get(RECEIPT_CHECKPOINT_KEY)
            if not isinstance(marker, dict):
                continue
            if body.get("execution_id") != self.execution_id:
                continue
            if body.get("packet_id") != self.packet_id:
                continue
            if body.get("attempt") != attempt:
                continue
            found.append((sha, body))
        return found

    def close(self, attempt: int, label: str = "cierre") -> tuple[str, dict]:
        chain = set(self.chain_shas(label))
        links = [
            (sha, body) for sha, body in self.close_links(attempt, label)
            if sha in chain
        ]
        assert len(links) == 1, (
            f"{label}: §2.3.2 — debe existir UN cierre DEMOSTRABLE para "
            f"(execution, packet, attempt={attempt}); vistos {len(links)}: "
            f"{[sha[:12] for sha, _ in links]}")
        return links[0]

    def receipt_dir(self) -> Path:
        return (self.root / ".cdad" / "runtime" / "results" / self.execution_id
                / self.packet_id)

    def receipt_path(self) -> Path:
        return self.receipt_dir() / RECEIPT_NAME

    def receipt(self, label: str = "recibo") -> dict:
        return load_json(self.receipt_path(), label)

    def receipt_bytes(self) -> bytes:
        return self.receipt_path().read_bytes()

    def parts_files(self) -> dict[str, bytes]:
        return files_under(self.receipt_dir() / "parts")

    def inbox_files(self) -> dict[str, bytes]:
        return files_under(self.root / ".cdad" / "inbox")

    def packet_dir(self) -> Path:
        return self.root / ".cdad" / "packets" / self.packet_id

    def request_path(self) -> Path:
        return self.packet_dir() / "REQUEST.json"

    def request(self) -> dict:
        return load_json(self.request_path(), "request")

    def write_request(self, doc: dict) -> None:
        self.request_path().write_text(
            json.dumps(doc, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8")

    def dispatch_files(self) -> list[str]:
        base = (self.root / ".cdad" / "executions" / self.execution_id
                / "dispatches")
        if not base.is_dir():
            return []
        return sorted(
            path.relative_to(self.root).as_posix()
            for path in base.rglob("*") if path.is_file())

    def write_reference(self, rel: str, content: str) -> tuple[str, str]:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))
        return rel, sha256_file(path)

    def tree(self) -> dict[str, bytes | None]:
        return tree_snapshot(self.root)

    def resolve_receipt_path(self, value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = self.root / path
        return path.resolve()

    # -- aserciones compartidas -------------------------------------------

    def assert_new_link_coherent(self, before_head: dict | None,
                                 after_head: dict, body: dict,
                                 label: str) -> None:
        """§2.3.1: coherencia cuerpo↔cabeza del enlace nuevo."""
        prev = require_prev(body, label, after_head.get("body_sha256", "?"))
        seq = after_head.get("seq")
        assert isinstance(seq, int), (
            f"{label}: la cabeza no declara `seq`: {after_head!r}")
        if before_head is None:
            assert seq == 1, (
                f"{label}: §2.3.1 — el primer enlace tiene seq 1; visto {seq}")
            assert prev is None, (
                f"{label}: §2.3.1 — el primer enlace (s=1) tiene "
                f"`body.prev=null`; visto {prev!r}")
            assert after_head.get("prev_checkpoint_sha256") is None, (
                f"{label}: §2.3.1 — s=1 ⇒ `head.prev_checkpoint_sha256=null`; "
                f"visto {after_head.get('prev_checkpoint_sha256')!r}")
            return
        assert isinstance(prev, dict), (
            f"{label}: §2.3.1 — s>1 ⇒ `body.prev` es un objeto: {prev!r}")
        assert prev.get("checkpoint_sha256") == before_head.get("body_sha256"), (
            f"{label}: §2.3.1 — `body.prev.checkpoint_sha256` debe ser el "
            f"cuerpo de la cabeza anterior "
            f"{before_head.get('body_sha256')!r}; visto "
            f"{prev.get('checkpoint_sha256')!r}")
        assert prev.get("seq") == before_head.get("seq"), (
            f"{label}: §2.3.1 — `body.prev.seq` debe ser la posición de la "
            f"cabeza anterior {before_head.get('seq')!r}; visto "
            f"{prev.get('seq')!r}")
        assert after_head.get("prev_checkpoint_sha256") == \
            before_head.get("body_sha256"), (
            f"{label}: §2.3.1 — `head.prev_checkpoint_sha256` debe encadenar "
            f"la cabeza anterior; visto "
            f"{after_head.get('prev_checkpoint_sha256')!r}")
        assert seq == before_head.get("seq") + 1, (
            f"{label}: §2.3.1 — la secuencia crece en 1: esperado "
            f"{before_head.get('seq') + 1}, visto {seq}")

    def assert_close(self, attempt: int, label: str,
                     receipt: Path | None = None) -> tuple[str, dict]:
        """§2.3/§2.3.1/§2.3.2: cierre único, localizable y con la referencia
        durable exacta."""
        sha, body = self.close(attempt, label)
        receipt = receipt or self.receipt_path()
        assert receipt.is_file(), (
            f"{label}: falta el recibo durable {receipt}")
        marker = body.get(RECEIPT_CHECKPOINT_KEY)
        assert isinstance(marker, dict), (
            f"{label}: el cuerpo del cierre no declara "
            f"`{RECEIPT_CHECKPOINT_KEY}`: {sorted(body)}")
        assert set(marker) == {"path", "sha256"}, (
            f"{label}: §2.3 — `receipt_checkpoint` lleva exactamente `path` y "
            f"`sha256`; visto {sorted(marker)}")
        assert marker.get("sha256") == sha256_file(receipt), (
            f"{label}: §2.3 — `receipt_checkpoint.sha256` es el digest del "
            f"recibo durable ({sha256_file(receipt)!r}); visto "
            f"{marker.get('sha256')!r}")
        resolved = self.resolve_receipt_path(str(marker.get("path")))
        assert resolved == receipt.resolve(), (
            f"{label}: §2.3.2 — la ruta del cierre debe resolver al recibo "
            f"durable {receipt.resolve()}; visto {resolved}")
        chain = self.chain_shas(label)
        assert sha in chain, (
            f"{label}: §2.3.1 — el cierre debe ser localizable por "
            f"encadenamiento desde la cabeza; {sha[:12]}… no está en "
            f"{[item[:12] for item in chain]}")
        return sha, body


class _Stage:
    """Copia descartable del skill con el módulo de runtime de FIXTURE."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.config_home = base / "config-home"
        self.config_home.mkdir(parents=True, exist_ok=True)
        self.stage = base / "stage"
        shutil.copytree(
            SKILL_DIR, self.stage,
            ignore=shutil.ignore_patterns("__pycache__"))
        self.scripts = self.stage / "scripts"
        (self.scripts / f"cdad_delegate_{FIXTURE_RUNTIME}.py").write_text(
            FIXTURE_MODULE_SOURCE, encoding="utf-8")
        self.log = self.scripts / "fixture-calls.jsonl"
        self.exec_config = base / "exec-config.json"
        self.exec_config.write_text(
            json.dumps({"runtime": FIXTURE_RUNTIME}, sort_keys=True) + "\n",
            encoding="utf-8")
        self._write_runtimes()

    def _write_runtimes(self) -> None:
        path = self.config_home / "cdad" / "runtimes.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "version": 1,
            "runtimes": {
                FIXTURE_RUNTIME: {
                    "binary": str(self.base / "bin"),
                    "binary_version": "demo700fix 1.0",
                    "mode": "standalone",
                    "auto": True,
                    "wait": {"timeout_seconds": 30},
                },
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def env(self) -> dict:
        env = dict(os.environ)
        env["HOME"] = str(self.home)
        env["XDG_CONFIG_HOME"] = str(self.config_home)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    def _run(self, cli: Path, args: list[str], cwd: Path
             ) -> subprocess.CompletedProcess:
        assert cli.is_file(), f"CLI del repo ausente: {cli}"
        return subprocess.run(
            [sys.executable, str(cli), *args],
            capture_output=True, text=True, cwd=str(cwd), env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S)

    def dispatch(self, project: _Project, *extra: str
                 ) -> subprocess.CompletedProcess:
        return self._run(
            self.scripts / "cdad_dispatch.py",
            ["dispatch", "--project-root", str(project.root),
             "--packet", project.packet_id, "--runtime", FIXTURE_RUNTIME,
             "--json", *extra],
            project.root)

    def record(self, project: _Project, *extra: str
               ) -> subprocess.CompletedProcess:
        return self._run(
            self.scripts / "cdad_dispatch.py",
            ["record", "--project-root", str(project.root),
             "--packet", project.packet_id, "--attempt-id",
             FIXTURE_ATTEMPT_ID, "--runtime", FIXTURE_RUNTIME, "--json",
             *extra],
            project.root)

    def delegate(self, project: _Project, *extra: str
                 ) -> subprocess.CompletedProcess:
        return self._run(
            self.scripts / "cdad_delegate.py",
            ["--project-root", str(project.root),
             "--packet", project.packet_id,
             "--destination", FIXTURE_RUNTIME,
             "--exec-config", str(self.exec_config), *extra],
            project.root)

    def calls(self) -> list[dict]:
        if not self.log.is_file():
            return []
        return [json.loads(line) for line in
                self.log.read_text(encoding="utf-8").splitlines()
                if line.strip()]

    def transport_calls(self) -> list[dict]:
        """Invocaciones del WORKER/transporte (no los sondeos del runtime)."""
        return [
            entry for entry in self.calls()
            if "--capabilities" not in (entry.get("argv") or [])
            and "--observe" not in (entry.get("argv") or [])
        ]

    def clear_calls(self) -> None:
        if self.log.is_file():
            self.log.unlink()


# ================================================================ TESTS


def _transport_accepted(stage: _Stage, fx: _Project, label: str, call) -> None:
    """PC-01: con prueba válida el transporte EXISTENTE continúa."""
    stage.clear_calls()
    proc = call()
    assert_rc0(proc, label, "el transporte externo con prueba válida")
    calls = stage.transport_calls()
    assert len(calls) == 1, (
        f"{label}: PC-01 — con `begin` vigente el worker debe lanzarse UNA "
        f"vez; invocaciones de transporte observadas: {len(calls)}")
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{label}: el sobre del transporte no es JSON: "
            f"{proc.stdout[:300]!r}") from exc
    assert isinstance(envelope, dict), (
        f"{label}: el sobre del transporte no es un objeto: {envelope!r}")
    assert envelope.get("termination") in {
        "completed", "blocked", "transport-error", "timeout", "cancelled",
        "unknown"}, (
        f"{label}: terminación fuera del vocabulario declarado: "
        f"{envelope.get('termination')!r}")


def _transport_rejected(stage: _Stage, fx: _Project, label: str, call,
                        pattern: re.Pattern = CONTINUITY_PATTERN) -> None:
    """PC-01: el rechazo ocurre ANTES de lanzar el worker y sin efectos."""
    stage.clear_calls()
    before_state = fx.state_bytes()
    before_dispatch = fx.dispatch_files()
    before_inbox = fx.inbox_files()
    before_continuity = fx.continuity_files()
    proc = call()
    assert_rejected(proc, label, "el transporte externo", pattern)
    calls = stage.transport_calls()
    assert calls == [], (
        f"{label}: PC-01 — el worker fue LANZADO pese al rechazo "
        f"(invocaciones: {calls}); la comprobación debe estar antes de la "
        f"herramienta de transporte")
    assert fx.dispatch_files() == before_dispatch, (
        f"{label}: PC-01 — el rechazo publicó un registro de despacho: "
        f"{fx.dispatch_files()}")
    assert fx.state_bytes() == before_state, (
        f"{label}: PC-01/INV-2 — el rechazo modificó {STATE_REL}")
    assert fx.inbox_files() == before_inbox, (
        f"{label}: PC-01 — el rechazo escribió staging en `.cdad/inbox`")
    assert fx.continuity_files() == before_continuity, (
        f"{label}: PC-01 — el rechazo escribió continuidad")


def test_transport_requires_current_matching_begin(tmp_path: Path) -> None:
    """PC-01: sin `begin` vigente, o con ejecución/paquete/intento/cuerpo/
    cabeza discordantes, se rechaza el transporte externo ANTES de lanzar el
    worker; con prueba válida continúa el transporte existente.

    Superficies: `cdad_dispatch.py dispatch` (entrada externa) y
    `cdad_delegate.py` (borde del adaptador, invocable directamente sin
    eludir la precondición), ambas con `--continuity-attempt N`.

    RED hoy: `--continuity-attempt` no existe (argparse) y el transporte
    arranca el worker sin `begin` vigente → los casos de rechazo fallan en la
    aserción de contrato (superficie/rc≠0/worker no lanzado).
    """
    stage = _Stage(tmp_path / "stage")
    cases = _Cases()

    def valid_proof() -> None:
        fx = _Project(tmp_path / "valid")
        assert_rc0(fx.begin(attempt=1), "PC-01 válido", "`begin`")
        proof = json_doc(
            fx.verify_begin(attempt=1), "PC-01 válido", "`verify-begin`")
        head = fx.head("PC-01 válido")
        for key in ("execution_id", "packet_id", "attempt", "body_sha256",
                    "seq"):
            assert key in proof, (
                f"PC-01 válido: §2.1 — la salida de `verify-begin` declara "
                f"`{key}`; visto {sorted(proof)}")
        assert proof["execution_id"] == fx.execution_id
        assert proof["packet_id"] == fx.packet_id
        assert proof["attempt"] == 1
        assert proof["body_sha256"] == head.get("body_sha256")
        assert proof["seq"] == head.get("seq")

        _transport_accepted(
            stage, fx, "PC-01 dispatch válido",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))
        # Proyecto fresco: el despacho puede registrar su intento y dejar el
        # paquete fuera de `prepared`; el borde del adaptador se prueba sin
        # acoplar ese efecto.
        fx_delegate = _Project(tmp_path / "valid-delegate")
        assert_rc0(fx_delegate.begin(attempt=1), "PC-01 delegate válido",
                   "`begin`")
        _transport_accepted(
            stage, fx_delegate, "PC-01 delegate válido",
            lambda: stage.delegate(fx_delegate, "--continuity-attempt", "1"))

    def no_begin() -> None:
        fx = _Project(tmp_path / "no-begin")
        _transport_rejected(
            stage, fx, "PC-01 sin begin",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))
        _transport_rejected(
            stage, fx, "PC-01 delegate sin begin",
            lambda: stage.delegate(fx, "--continuity-attempt", "1"))

    def missing_flag() -> None:
        fx = _Project(tmp_path / "missing-flag")
        assert_rc0(fx.begin(attempt=1), "PC-01 flag ausente", "`begin`")
        _transport_rejected(
            stage, fx, "PC-01 dispatch sin --continuity-attempt",
            lambda: stage.dispatch(fx))
        _transport_rejected(
            stage, fx, "PC-01 delegate sin --continuity-attempt",
            lambda: stage.delegate(fx))

    def textual_id_does_not_substitute() -> None:
        fx = _Project(tmp_path / "textual-id")
        assert_rc0(fx.begin(attempt=1), "PC-01 id textual", "`begin`")
        _transport_rejected(
            stage, fx,
            "PC-01 dispatch con --attempt-id textual y sin entero",
            lambda: stage.dispatch(fx, "--attempt-id", TEXTUAL_ATTEMPT))

    def checkpoint_after_begin() -> None:
        fx = _Project(tmp_path / "checkpoint-after")
        assert_rc0(fx.begin(attempt=1), "PC-01 checkpoint", "`begin`")
        assert_rc0(fx.checkpoint(attempt=1, label="cp1"), "PC-01 checkpoint",
                   "`checkpoint`")
        head = fx.head("PC-01 checkpoint")
        assert head.get("record") == "checkpoint", (
            "precondición (fixture): la cabeza es un checkpoint posterior")
        _transport_rejected(
            stage, fx, "PC-01 cabeza checkpoint posterior al begin",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))

    def head_of_another_attempt() -> None:
        fx = _Project(tmp_path / "other-attempt")
        assert_rc0(fx.begin(attempt=1), "PC-01 otro intento", "`begin`")
        assert_rc0(fx.begin(attempt=2, label="attempt-2"),
                   "PC-01 otro intento", "`begin` del intento 2")
        _transport_rejected(
            stage, fx, "PC-01 cabeza de otro intento",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))

    def body_altered() -> None:
        fx = _Project(tmp_path / "body-altered")
        assert_rc0(fx.begin(attempt=1), "PC-01 cuerpo alterado", "`begin`")
        sha = fx.head("PC-01 cuerpo alterado").get("body_sha256")
        fx.body_path(sha).write_bytes(fx.body_raw(sha) + b" ")
        _transport_rejected(
            stage, fx, "PC-01 cuerpo alterado",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))

    def head_altered() -> None:
        fx = _Project(tmp_path / "head-altered")
        assert_rc0(fx.begin(attempt=1), "PC-01 cabeza alterada", "`begin`")
        head = fx.head("PC-01 cabeza alterada")
        head["seq"] = 99
        fx.write_head(head)
        _transport_rejected(
            stage, fx, "PC-01 cabeza alterada",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))

    def historical_record_absent() -> None:
        fx = _Project(tmp_path / "legacy-record")
        assert_rc0(fx.begin(attempt=1), "PC-01 record ausente", "`begin`")
        head = fx.head("PC-01 record ausente")
        body = fx.body(head["body_sha256"], "PC-01 record ausente")
        body.pop("record", None)
        sha = fx.write_body(body)
        head["body_sha256"] = sha
        fx.write_head(head)
        _transport_rejected(
            stage, fx, "PC-01 cuerpo histórico sin `record`",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"),
            pattern=re.compile(r"(?i)record|begin|continu"))

    def execution_mismatch() -> None:
        fx = _Project(tmp_path / "exec-mismatch")
        assert_rc0(fx.begin(attempt=1), "PC-01 ejecución", "`begin`")
        request = fx.request()
        request["execution_id"] = "exec-demo-700-foreign"
        fx.write_request(request)
        _transport_rejected(
            stage, fx, "PC-01 ejecución discordante",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))

    def packet_mismatch() -> None:
        fx = _Project(tmp_path / "packet-mismatch")
        assert_rc0(fx.begin(attempt=1), "PC-01 paquete", "`begin`")
        request = fx.request()
        request["packet_id"] = "demo-700-foreign-packet"
        fx.write_request(request)
        _transport_rejected(
            stage, fx, "PC-01 paquete discordante",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))

    def head_packet_mismatch() -> None:
        fx = _Project(tmp_path / "head-packet")
        assert_rc0(fx.begin(attempt=1), "PC-01 cabeza paquete", "`begin`")
        head = fx.head("PC-01 cabeza paquete")
        head["packet_id"] = "demo-700-foreign-packet"
        fx.write_head(head)
        _transport_rejected(
            stage, fx, "PC-01 cabeza de otro paquete",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))

    def authority_expired() -> None:
        fx = _Project(tmp_path / "authority")
        assert_rc0(fx.begin(attempt=1), "PC-01 autoridad", "`begin`")
        state = fx.read_state()
        state["hitl_delegation"]["status"] = "user-revoked"
        (fx.root / STATE_REL).write_text(
            json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
        context = json.loads(fx.ctx.read_text(encoding="utf-8"))
        context["hitl_delegation"] = {
            "authority_ref": AUTHORITY_REF,
            "expires_on": "2020-01-01",
        }
        expired = fx.base / "expired-execution.json"
        expired.write_text(
            json.dumps(context, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        assert_rejected(
            fx.verify_begin(attempt=1, ctx=expired),
            "PC-01 autoridad expirada", "`verify-begin` con autoridad vencida")
        _transport_rejected(
            stage, fx, "PC-01 autoridad expirada",
            lambda: stage.dispatch(fx, "--continuity-attempt", "1"))

    def verify_mismatches() -> None:
        fx = _Project(tmp_path / "verify-mismatch")
        assert_rc0(fx.begin(attempt=1), "PC-01 verify", "`begin`")
        assert_rejected(
            fx.verify_begin(attempt=2), "PC-01 verify intento",
            "`verify-begin` con intento discordante")
        assert_rejected(
            fx.verify_begin(attempt=1, packet="demo-700-foreign-packet"),
            "PC-01 verify paquete",
            "`verify-begin` con paquete discordante")

    for label, case in (
        ("prueba válida", valid_proof),
        ("sin begin", no_begin),
        ("flag ausente", missing_flag),
        ("id textual", textual_id_does_not_substitute),
        ("checkpoint posterior", checkpoint_after_begin),
        ("cabeza de otro intento", head_of_another_attempt),
        ("cuerpo alterado", body_altered),
        ("cabeza alterada", head_altered),
        ("record histórico ausente", historical_record_absent),
        ("ejecución discordante", execution_mismatch),
        ("paquete discordante", packet_mismatch),
        ("cabeza de otro paquete", head_packet_mismatch),
        ("autoridad expirada", authority_expired),
        ("verify-begin discordante", verify_mismatches),
    ):
        cases.run(label, case)
    cases.raise_if_any("PC-01")


def test_native_dispatch_and_registration_require_begin(tmp_path: Path) -> None:
    """PC-02: el wiring nativo declara la comprobación ANTES de la herramienta;
    el registro canónico rechaza un intento nuevo sin la misma prueba, sin
    publicar estado, observación ni staging; un replay byte-idéntico durable
    conserva su idempotencia.

    La comprobación del wiring es DOCUMENTAL (spec §4): se asevera sobre
    `sources/roles/orchestrator.md` y su derivado `agents/cdad-orchestrator.md`
    y NO se presenta como interceptación empírica de una herramienta del
    runtime. La parte ejecutable usa `prepare --record-dispatch` y el verbo
    nativo `record` con `--continuity-attempt N`.

    RED hoy: `--continuity-attempt` no existe en ninguno de los dos verbos y
    los cuerpos canónicos no declaran `verify-begin` → los casos fallan en la
    aserción de contrato.
    """
    stage = _Stage(tmp_path / "stage")
    cases = _Cases()

    def documentary_wiring() -> None:
        assert ORCHESTRATOR_SOURCE.is_file(), (
            f"PC-02/§2.2: falta el cuerpo canónico {ORCHESTRATOR_SOURCE}")
        assert ORCHESTRATOR_DERIVED.is_file(), (
            f"PC-02/§2.2: falta el derivado {ORCHESTRATOR_DERIVED}")
        source = ORCHESTRATOR_SOURCE.read_text(encoding="utf-8")
        derived = ORCHESTRATOR_DERIVED.read_text(encoding="utf-8")
        assert "verify-begin" in source, (
            "PC-02/§2.2: el cuerpo canónico del orquestador debe declarar "
            "`verify-begin` en el wiring de continuidad")
        assert "--continuity-attempt" in source, (
            "PC-02/§2.2: el cuerpo canónico del orquestador debe declarar "
            "`--continuity-attempt`")
        start = source.find("Continuity wiring")
        assert start >= 0, (
            "PC-02/§2.2: falta la sección `Continuity wiring` del cuerpo "
            "canónico")
        end = source.find("Re-entry wiring", start)
        section = source[start:end if end > start else len(source)]
        assert re.search(
            r"begin.*verify-begin.*(?:native|transport|dispatch|despacho|"
            r"tool|herramienta).*record",
            section, re.S), (
            "PC-02/§2.2: el wiring canónico debe declarar el orden "
            "`begin` → `verify-begin` → herramienta nativa → `record`")
        assert "verify-begin" in derived, (
            "PC-02/§2.2: el derivado generado `agents/cdad-orchestrator.md` "
            "debe declarar `verify-begin`")
        assert "--continuity-attempt" in derived, (
            "PC-02/§2.2: el derivado generado debe declarar "
            "`--continuity-attempt`")

    def registration_without_proof() -> None:
        fx = _Project(tmp_path / "reg-no-proof")
        # El intento declara continuidad (pasa el entero) pero no abrió cadena:
        # sin prueba el registro se rechaza. La observación de entrada se
        # materializa ANTES de los snapshots para que el oráculo mida sólo lo
        # que escribe el producto (no el propio fixture).
        observation = fx.write_observation()
        before_tree = fx.tree()
        before_state = fx.state_bytes()
        before_inbox = fx.inbox_files()
        proc = fx.record_dispatch(n=1, observation=observation)
        assert_rejected(
            proc, "PC-02 registro sin prueba",
            "el registro canónico sin `begin` vigente")
        assert fx.dispatch_files() == [], (
            "PC-02/§2.2: sin la prueba NO se publica observación (registro "
            f"I8); visto {fx.dispatch_files()}")
        assert fx.state_bytes() == before_state, (
            "PC-02/§2.2: sin la prueba NO se publica el binding de estado")
        assert fx.inbox_files() == before_inbox, (
            "PC-02/§2.2: sin la prueba NO se publica entrega staged")
        assert_unchanged(before_tree, fx.tree(), "PC-02 registro sin prueba",
                         "el rechazo del registro canónico")

    def registration_without_integer_but_textual_id() -> None:
        fx = _Project(tmp_path / "reg-textual")
        assert_rc0(fx.begin(attempt=1), "PC-02 id textual", "`begin`")
        before_state = fx.state_bytes()
        proc = fx.record_dispatch(attempt_id=TEXTUAL_ATTEMPT, with_flag=False)
        assert_rejected(
            proc, "PC-02 id textual sin entero",
            "el registro canónico con `--attempt-id` textual y sin "
            "`--continuity-attempt`")
        assert fx.dispatch_files() == [], (
            "PC-02/§2.1: el entero NO se infiere del `--attempt-id` textual; "
            f"se publicó un registro: {fx.dispatch_files()}")
        assert fx.state_bytes() == before_state

    def registration_with_proof() -> None:
        fx = _Project(tmp_path / "reg-proof")
        assert_rc0(fx.begin(attempt=1), "PC-02 registro válido", "`begin`")
        proc = fx.record_dispatch(n=1)
        assert_rc0(proc, "PC-02 registro válido", "el registro canónico")
        records = fx.dispatch_files()
        assert len(records) == 1, (
            f"PC-02: con la prueba se publica UN registro; vistos {records}")
        record = load_json(fx.root / records[0], "PC-02 registro")
        assert record.get("execution_id") == fx.execution_id
        assert record.get("packet_id") == fx.packet_id
        assert record.get("session") == FIXTURE_SESSION, (
            f"PC-02: la observación declarada se publica: {record!r}")
        state = fx.read_state()
        assert (state.get("active_packet") or {}).get("status") == \
            "dispatched", (
            "PC-02: con la prueba el binding de estado queda `dispatched`: "
            f"{state.get('active_packet')!r}")

    def native_record_without_proof() -> None:
        fx = _Project(tmp_path / "native-no-proof")
        before_state = fx.state_bytes()
        before_inbox = fx.inbox_files()
        proc = stage.record(fx, "--continuity-attempt", "1")
        assert_rejected(
            proc, "PC-02 record nativo sin prueba",
            "el verbo nativo `record` sin `begin` vigente")
        assert fx.dispatch_files() == [], (
            f"PC-02: `record` sin prueba publicó un registro: "
            f"{fx.dispatch_files()}")
        assert fx.inbox_files() == before_inbox, (
            "PC-02: `record` sin prueba escribió staging")
        assert fx.state_bytes() == before_state

    def native_record_with_proof() -> None:
        fx = _Project(tmp_path / "native-proof")
        assert_rc0(fx.begin(attempt=1), "PC-02 record nativo", "`begin`")
        proc = stage.record(fx, "--continuity-attempt", "1")
        assert_rc0(proc, "PC-02 record nativo", "el verbo nativo `record`")
        assert len(fx.dispatch_files()) == 1, (
            "PC-02: `record` con la prueba publica UN registro; vistos "
            f"{fx.dispatch_files()}")

    def durable_replay_is_idempotent() -> None:
        fx = _Project(tmp_path / "replay")
        assert_rc0(fx.begin(attempt=1), "PC-02 replay", "`begin`")
        assert_rc0(fx.record_dispatch(n=1), "PC-02 replay",
                   "el registro durable")
        records = fx.dispatch_files()
        assert len(records) == 1, "precondición (fixture): un registro durable"
        record_path = fx.root / records[0]
        before = record_path.read_bytes()
        # La cabeza avanza a otro intento: el replay NO es un transporte nuevo
        # y conserva la idempotencia (§2.2).
        assert_rc0(fx.begin(attempt=2, label="attempt-2"), "PC-02 replay",
                   "`begin` del intento 2")
        proc = fx.record_dispatch(n=1)
        assert_rc0(proc, "PC-02 replay", "el replay byte-idéntico durable")
        assert record_path.read_bytes() == before, (
            "PC-02/§2.2: el replay idéntico NO reescribe la observación")
        assert fx.dispatch_files() == records, (
            f"PC-02: el replay no crea otro registro: {fx.dispatch_files()}")

    def different_data_replay_is_rejected() -> None:
        fx = _Project(tmp_path / "replay-different")
        assert_rc0(fx.begin(attempt=1), "PC-02 replay distinto", "`begin`")
        assert_rc0(fx.record_dispatch(n=1), "PC-02 replay distinto",
                   "el registro durable")
        record_path = fx.root / fx.dispatch_files()[0]
        before = record_path.read_bytes()
        other = fx.write_observation(
            session="ses-demo-700-9999", name="other-observation.json")
        proc = fx.record_dispatch(n=1, observation=other)
        assert_rejected(
            proc, "PC-02 replay con datos distintos",
            "el replay con observación distinta (write-once)")
        assert record_path.read_bytes() == before, (
            "PC-02: el replay con datos distintos no modifica el registro")

    for label, case in (
        ("wiring documental", documentary_wiring),
        ("registro sin prueba", registration_without_proof),
        ("id textual sin entero", registration_without_integer_but_textual_id),
        ("registro con prueba", registration_with_proof),
        ("record nativo sin prueba", native_record_without_proof),
        ("record nativo con prueba", native_record_with_proof),
        ("replay durable idéntico", durable_replay_is_idempotent),
        ("replay con datos distintos", different_data_replay_is_rejected),
    ):
        cases.run(label, case)
    cases.raise_if_any("PC-02")


def _snapshot_receipt_state(fx: _Project) -> dict:
    return {
        "receipt": fx.receipt_bytes() if fx.receipt_path().is_file() else None,
        "parts": fx.parts_files(),
        "inbox": fx.inbox_files(),
        "continuity": fx.continuity_files(),
        "state": fx.state_bytes(),
    }


def _assert_receipt_state_unchanged(fx: _Project, before: dict,
                                    label: str) -> None:
    assert fx.receipt_bytes() == before["receipt"], (
        f"{label}: el recibo durable no debe cambiar")
    assert fx.parts_files() == before["parts"], (
        f"{label}: no se repite la recepción (parts intactas)")
    assert fx.inbox_files() == before["inbox"], (
        f"{label}: no se repite el staging")
    assert fx.continuity_files() == before["continuity"], (
        f"{label}: la cadena de continuidad no debe cambiar")
    assert fx.state_bytes() == before["state"], (
        f"{label}: INV-2 — la continuidad no escribe {STATE_REL}")


def test_receive_closes_continuity_idempotently(tmp_path: Path) -> None:
    """PC-03: una recepción ordinaria deja recibo durable y checkpoint
    correspondiente sin modificar `semantic_status=pending`; repetirla no
    añade enlaces ni repite otros efectos. Sin `--continuity-attempt` el
    cierre falla cerrado sin escribir; un `N` que discrepa de la cabeza se
    rechaza salvo que exista un cierre idéntico demostrable (§2.3.3).

    Variantes obligatorias: recibo ilegible, identidad ajena, cierre idéntico
    histórico y `receive --late` (intento ausente, discordante sin cierre,
    cierre idéntico con cabeza de otro intento y ejecución cerrada).

    RED hoy: `receive` no acepta `--continuity-attempt` y no cierra
    continuidad → los casos fallan en la aserción de superficie/cierre.
    """
    cases = _Cases()

    def normal_close_and_repeat() -> None:
        fx = _Project(tmp_path / "normal")
        begin = json_doc(fx.begin(attempt=1), "PC-03 normal", "`begin`")
        begin_head = fx.head("PC-03 normal")
        begin_body = fx.body(begin_head["body_sha256"], "PC-03 normal")
        fx.mark_dispatched()

        proc = fx.receive(n=1)
        receipt = json_doc(proc, "PC-03 normal", "`receive`")
        assert receipt.get("semantic_status") == "pending", (
            "PC-03: recibir NO aprueba; `semantic_status=pending` se "
            f"conserva: {receipt.get('semantic_status')!r}")
        assert fx.receipt().get("semantic_status") == "pending", (
            "PC-03: el recibo durable conserva `semantic_status=pending`")

        close_sha, close_body = fx.assert_close(1, "PC-03 normal")
        after_head = fx.head("PC-03 normal")
        fx.assert_new_link_coherent(
            begin_head, after_head, close_body, "PC-03 cierre")
        assert close_body.get("goal") == begin_body.get("goal"), (
            "PC-03/§2.3: el cierre conserva el objetivo del contexto que "
            f"cierra: {close_body.get('goal')!r} != {begin_body.get('goal')!r}")
        close_decisions = close_body.get("decisions") or []
        for decision in begin_body.get("decisions") or []:
            assert decision in close_decisions, (
                "PC-03/§2.3: el cierre conserva las decisiones del contexto "
                f"que cierra; falta {decision!r}")
        assert close_body.get("uncertainties") == begin_body.get("uncertainties"), (
            "PC-03/§2.3: el cierre conserva las incertidumbres del contexto")
        def _decision_text(item: dict) -> str:
            return f"{item.get('decision', '')} {item.get('rationale', '')}"

        new_texts = [
            _decision_text(item)
            for item in close_decisions
            if isinstance(item, dict)
            and item not in (begin_body.get("decisions") or [])
        ]
        assert any(re.search(r"(?i)recep|recib|mecán|mechanic", text)
                   for text in new_texts), (
            "PC-03/§2.3: el cierre agrega una decisión fundada de recepción "
            f"MECÁNICA; decisiones nuevas vistas: {new_texts}")
        assert begin.get("body_sha256") == begin_head.get("body_sha256")

        before = _snapshot_receipt_state(fx)
        again = fx.receive(n=1)
        assert_rc0(again, "PC-03 repetición", "la recepción repetida")
        _assert_receipt_state_unchanged(fx, before, "PC-03 repetición")
        assert len(fx.close_links(1)) == 1, (
            "PC-03: la repetición no agrega un segundo cierre")

    def without_flag_fails_closed() -> None:
        fx = _Project(tmp_path / "no-flag")
        assert_rc0(fx.begin(attempt=1), "PC-03 sin flag", "`begin`")
        fx.mark_dispatched()
        before = _snapshot_receipt_state(fx)
        proc = fx.receive(with_flag=False)
        assert_rejected(
            proc, "PC-03 sin --continuity-attempt",
            "`receive` sin el entero de continuidad",
            pattern=re.compile(r"(?i)continuity-attempt|continu|intent"))
        assert not fx.receipt_path().exists(), (
            "PC-03/§2.3.3: sin `N` NO se publica recibo nuevo")
        assert fx.continuity_files() == before["continuity"], (
            "PC-03/§2.3.3: sin `N` no se escribe continuidad")
        assert fx.state_bytes() == before["state"]

    def discordant_without_close() -> None:
        fx = _Project(tmp_path / "discordant")
        assert_rc0(fx.begin(attempt=1), "PC-03 discordante", "`begin`")
        fx.mark_dispatched()
        head_before = fx.head_bytes()
        proc = fx.receive(n=2)
        assert_rejected(
            proc, "PC-03 N discordante sin cierre",
            "el cierre con `N` discordante y sin cierre demostrable")
        assert fx.close_links(2) == [], (
            "PC-03/§2.3.3: sin cierre demostrable no se agrega cierre")
        assert fx.head_bytes() == head_before, (
            "PC-03/§2.3.3: el rechazo no rebobina ni reemplaza la cabeza")
        assert fx.receipt_path().is_file(), (
            "PC-03/§2.4: el recibo durable se publica ANTES del cierre; una "
            "falla del cierre no lo elimina")

    def discordant_with_demonstrable_close() -> None:
        fx = _Project(tmp_path / "discordant-close")
        assert_rc0(fx.begin(attempt=1), "PC-03 cierre histórico", "`begin`")
        fx.mark_dispatched()
        assert_rc0(fx.receive(n=1), "PC-03 cierre histórico",
                   "la recepción que cierra")
        fx.assert_close(1, "PC-03 cierre histórico")
        assert_rc0(fx.begin(attempt=2, label="attempt-2"),
                   "PC-03 cierre histórico", "`begin` del intento 2")
        before = _snapshot_receipt_state(fx)
        again = fx.receive(n=1)
        assert_rc0(again, "PC-03 cierre idéntico",
                   "el cierre idéntico demostrable con cabeza de otro intento")
        _assert_receipt_state_unchanged(fx, before, "PC-03 cierre idéntico")

    def unreadable_receipt() -> None:
        fx = _Project(tmp_path / "unreadable")
        assert_rc0(fx.begin(attempt=1), "PC-03 recibo ilegible", "`begin`")
        fx.mark_dispatched()
        assert_rc0(fx.receive(n=1), "PC-03 recibo ilegible",
                   "la recepción que cierra")
        fx.receipt_path().write_bytes(b"{not a receipt")
        before = fx.continuity_files()
        proc = fx.receive(n=1)
        assert_rejected(
            proc, "PC-03 recibo ilegible",
            "el cierre con un recibo ilegible")
        assert fx.continuity_files() == before, (
            "PC-03: el recibo ilegible no altera la continuidad")

    def foreign_identity() -> None:
        fx = _Project(tmp_path / "foreign")
        assert_rc0(fx.begin(attempt=1), "PC-03 identidad ajena", "`begin`")
        fx.mark_dispatched()
        descriptor = fx.stage_result()
        doc = json.loads(descriptor.read_text(encoding="utf-8"))
        doc["execution_id"] = "exec-demo-700-foreign"
        descriptor.write_text(
            json.dumps(doc, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8")
        before = fx.continuity_files()
        proc = fx.receive(n=1, descriptor=descriptor)
        assert_rejected(
            proc, "PC-03 identidad ajena",
            "la recepción de un descriptor de otra ejecución")
        assert not fx.receipt_path().exists(), (
            "PC-03: la identidad ajena no publica recibo")
        assert fx.continuity_files() == before

    def late_variants() -> None:
        fx = _Project(tmp_path / "late")
        assert_rc0(fx.begin(attempt=1), "PC-03 late", "`begin`")
        fx.mark_dispatched()
        assert_rc0(fx.receive(n=1), "PC-03 late", "la recepción que cierra")
        fx.assert_close(1, "PC-03 late")
        # Cabeza de otro intento ANTES de cerrar la feature.
        assert_rc0(fx.begin(attempt=2, label="attempt-2"), "PC-03 late",
                   "`begin` del intento 2")
        assert_rc0(fx.closure(), "PC-03 late", "la transición de cierre")
        before = _snapshot_receipt_state(fx)

        missing = fx.receive(late=True, with_flag=False)
        assert_rejected(
            missing, "PC-03 late sin intento",
            "`receive --late` sin `--continuity-attempt`",
            pattern=re.compile(r"(?i)continuity-attempt|continu|intent"))
        _assert_receipt_state_unchanged(
            fx, before, "PC-03 late sin intento")

        discordant = fx.receive(late=True, n=99)
        assert_rejected(
            discordant, "PC-03 late discordante",
            "`receive --late` con intento discordante y sin cierre")
        _assert_receipt_state_unchanged(
            fx, before, "PC-03 late discordante")

        identical = fx.receive(late=True, n=1)
        assert_rc0(
            identical, "PC-03 late cierre idéntico",
            "`receive --late` con cierre durable idéntico (cabeza de otro "
            "intento y ejecución cerrada)")
        _assert_receipt_state_unchanged(
            fx, before, "PC-03 late cierre idéntico")

    for label, case in (
        ("cierre normal y repetición", normal_close_and_repeat),
        ("sin flag", without_flag_fails_closed),
        ("N discordante sin cierre", discordant_without_close),
        ("N discordante con cierre", discordant_with_demonstrable_close),
        ("recibo ilegible", unreadable_receipt),
        ("identidad ajena", foreign_identity),
        ("receive --late", late_variants),
    ):
        cases.run(label, case)
    cases.raise_if_any("PC-03")


def _orphan_receipt(fx: _Project, *, close_attempt: int = 2,
                    label: str = "PC-04") -> None:
    """Recibo durable publicado con el cierre pendiente (§2.4).

    Se produce por el camino legítimo: el despacho del intento 1 registra la
    observación y `receive --continuity-attempt 2` publica el recibo antes de
    fallar el cierre (la cabeza es el `begin` del intento 1). Después se abre
    el `begin` del intento 2, que sí admite su cierre.
    """
    assert_rc0(fx.begin(attempt=1), label, "`begin` del intento 1")
    fx.mark_dispatched()
    pending = fx.receive(n=close_attempt)
    assert_rejected(
        pending, label,
        "la recepción con el cierre pendiente (cabeza de otro intento)")
    assert fx.receipt_path().is_file(), (
        f"{label}/§2.4: el recibo durable se publica antes del cierre")
    assert fx.close_links(close_attempt) == [], (
        f"{label}: no existe cierre para el intento {close_attempt}")
    assert_rc0(fx.begin(attempt=close_attempt, label=f"attempt-{close_attempt}"),
               label, f"`begin` del intento {close_attempt}")


def test_external_durable_receipt_uses_common_continuity_close(
        tmp_path: Path) -> None:
    """PC-04: un recibo durable externo converge al MISMO cierre común sin
    staged ni nueva recepción; repetir la validación con cierre no altera la
    cadena.

    Superficie: `validate-receipt --close-continuity --continuity-attempt N`
    (§2.3.3, tercera entrada de reentrada). Convergencia: el cierre que
    produce esta entrada es el mismo que reconoce `checkpoint-receipt` con el
    mismo recibo (éxito sin escribir), y `validate-receipt` sin las opciones
    conserva su comportamiento de sólo validación.

    RED hoy: `--close-continuity`/`--continuity-attempt` no existen en
    `validate-receipt` → los casos fallan en la aserción de superficie.
    """
    cases = _Cases()

    def converges_without_staging() -> None:
        fx = _Project(tmp_path / "converge")
        _orphan_receipt(fx, close_attempt=2)
        # La reentrada externa NO repite recepción ni staging: recibo, parts,
        # inbox y estado se comparan contra el estado previo al cierre (§2.4).
        before = _snapshot_receipt_state(fx)
        proc = fx.validate_receipt(close=True, attempt=2)
        assert_rc0(proc, "PC-04 convergencia",
                   "`validate-receipt --close-continuity`")
        fx.assert_close(2, "PC-04 convergencia")
        assert fx.receipt_bytes() == before["receipt"], (
            "PC-04: la convergencia externa no republica ni altera el recibo "
            "durable")
        assert fx.parts_files() == before["parts"], (
            "PC-04: la convergencia externa no repite la recepción (parts)")
        assert fx.inbox_files() == before["inbox"], (
            "PC-04: la convergencia externa no repite el staging")
        assert fx.state_bytes() == before["state"], (
            f"PC-04/INV-2 — el cierre común no escribe {STATE_REL}")
        # El cierre SÍ agrega su enlace de continuidad; el snapshot que mide
        # «repetir no altera la cadena» es el POSTERIOR al cierre.
        after_close = _snapshot_receipt_state(fx)

        # Mismo cierre común: `checkpoint-receipt` lo reconoce sin escribir.
        same = fx.checkpoint_receipt(attempt=2)
        assert_rc0(same, "PC-04 convergencia",
                   "`checkpoint-receipt` sobre el cierre ya producido")
        _assert_receipt_state_unchanged(fx, after_close, "PC-04 convergencia")

        # Sin `--close-continuity` sigue siendo sólo validación (INV-10).
        read_only = fx.validate_receipt()
        assert_rc0(read_only, "PC-04 sólo validación",
                   "`validate-receipt` sin cierre")
        _assert_receipt_state_unchanged(fx, after_close, "PC-04 sólo validación")

    def repeated_close_is_stable() -> None:
        fx = _Project(tmp_path / "repeat")
        _orphan_receipt(fx, close_attempt=2)
        assert_rc0(fx.validate_receipt(close=True, attempt=2),
                   "PC-04 repetición", "el cierre común")
        before = _snapshot_receipt_state(fx)
        again = fx.validate_receipt(close=True, attempt=2)
        assert_rc0(again, "PC-04 repetición", "la validación con cierre")
        _assert_receipt_state_unchanged(fx, before, "PC-04 repetición")

    def historical_close_with_head_of_another_attempt() -> None:
        fx = _Project(tmp_path / "historical")
        _orphan_receipt(fx, close_attempt=2)
        assert_rc0(fx.validate_receipt(close=True, attempt=2),
                   "PC-04 histórico", "el cierre común")
        assert_rc0(fx.begin(attempt=3, label="attempt-3"),
                   "PC-04 histórico", "`begin` del intento 3")
        before = _snapshot_receipt_state(fx)
        replay = fx.validate_receipt(close=True, attempt=2)
        assert_rc0(replay, "PC-04 histórico",
                   "el cierre idéntico con cabeza de otro intento")
        _assert_receipt_state_unchanged(fx, before, "PC-04 histórico")

    def unreadable_receipt() -> None:
        fx = _Project(tmp_path / "unreadable")
        _orphan_receipt(fx, close_attempt=2)
        fx.receipt_path().write_bytes(b"{not a receipt")
        before = fx.continuity_files()
        proc = fx.validate_receipt(close=True, attempt=2)
        assert_rejected(
            proc, "PC-04 recibo ilegible",
            "`validate-receipt --close-continuity` con recibo ilegible")
        assert fx.continuity_files() == before, (
            "PC-04: el recibo ilegible no altera la continuidad")

    def foreign_identity() -> None:
        fx = _Project(tmp_path / "foreign")
        _orphan_receipt(fx, close_attempt=2)
        doc = fx.receipt()
        doc["packet_id"] = "demo-700-foreign-packet"
        copy = fx.receipt_path().parent / "foreign-receipt.json"
        copy.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        before = fx.continuity_files()
        proc = fx.validate_receipt(close=True, attempt=2, receipt=copy)
        assert_rejected(
            proc, "PC-04 identidad ajena",
            "el cierre con un recibo de otro paquete")
        assert fx.continuity_files() == before, (
            "PC-04: la identidad ajena no agrega cierre")
        assert fx.close_links(2) == []

    for label, case in (
        ("convergencia sin staging", converges_without_staging),
        ("cierre repetido", repeated_close_is_stable),
        ("cierre histórico", historical_close_with_head_of_another_attempt),
        ("recibo ilegible", unreadable_receipt),
        ("identidad ajena", foreign_identity),
    ):
        cases.run(label, case)
    cases.raise_if_any("PC-04")


def _continuity_prefix(fx: _Project) -> str:
    return f".cdad/executions/{fx.execution_id}/continuity/"


def _assert_only_continuity_changed(fx: _Project, before: dict,
                                    label: str) -> None:
    changed = changed_paths(before, fx.tree())
    prefix = _continuity_prefix(fx)
    unexpected = sorted(rel for rel in changed if not rel.startswith(prefix))
    assert not unexpected, (
        f"{label}: la recuperación debe cerrar ÚNICAMENTE continuidad; "
        f"también cambió: {unexpected}")


def test_interrupted_receipt_or_transition_recovers_only_missing_checkpoint(
        tmp_path: Path) -> None:
    """PC-05: las interrupciones después del recibo y después de la
    transición se recuperan cerrando únicamente continuidad; recibo y
    transición permanecen idénticos; una cabeza adelantada se rechaza sin
    rebobinar. Con varios eslabones posteriores el cierre sigue localizándose
    por encadenamiento; un cuerpo huérfano no cuenta como cierre ni
    antecedente; un cuerpo legado sin `prev` es historia no demostrable.

    RED hoy: `checkpoint-receipt` no existe y los cuerpos no declaran `prev`
    → los casos fallan en la aserción de superficie/cadena.
    """
    cases = _Cases()

    def after_receipt() -> None:
        fx = _Project(tmp_path / "after-receipt")
        _orphan_receipt(fx, close_attempt=2)
        before = fx.tree()
        proc = fx.checkpoint_receipt(attempt=2)
        assert_rc0(proc, "PC-05 tras el recibo", "`checkpoint-receipt`")
        fx.assert_close(2, "PC-05 tras el recibo")
        _assert_only_continuity_changed(fx, before, "PC-05 tras el recibo")
        assert fx.receipt_path().is_file()

    def after_transition() -> None:
        fx = _Project(tmp_path / "after-transition")
        _orphan_receipt(fx, close_attempt=2)
        assert_rc0(fx.delivery(), "PC-05 tras la transición",
                   "la transición de entrega")
        state = fx.read_state()
        history_before = len(state.get("stage_history") or [])
        active_before = json.dumps(
            state.get("active_packet"), sort_keys=True, ensure_ascii=False)
        receipt_before = fx.receipt_bytes()
        before = fx.tree()
        proc = fx.checkpoint_receipt(attempt=2)
        assert_rc0(proc, "PC-05 tras la transición", "`checkpoint-receipt`")
        fx.assert_close(2, "PC-05 tras la transición")
        _assert_only_continuity_changed(
            fx, before, "PC-05 tras la transición")
        state_after = fx.read_state()
        assert len(state_after.get("stage_history") or []) == history_before, (
            "PC-05/§2.4: el cierre no repite la transición")
        assert json.dumps(
            state_after.get("active_packet"), sort_keys=True,
            ensure_ascii=False) == active_before, (
            "PC-05/§2.4: el cierre no reactiva ni altera el paquete activo")
        assert fx.receipt_bytes() == receipt_before, (
            "PC-05/§2.4: el recibo permanece idéntico")

    def several_later_links() -> None:
        fx = _Project(tmp_path / "later-links")
        _orphan_receipt(fx, close_attempt=2)
        assert_rc0(fx.checkpoint_receipt(attempt=2), "PC-05 eslabones",
                   "el cierre inicial")
        close_sha, _ = fx.assert_close(2, "PC-05 eslabones")
        for index in range(1, 4):
            assert_rc0(
                fx.checkpoint(attempt=2, label=f"later-{index}"),
                "PC-05 eslabones", "un checkpoint posterior")
        assert close_sha in fx.chain_shas("PC-05 eslabones"), (
            "PC-05/§2.3.1: el cierre sigue siendo localizable por "
            "encadenamiento tras varios eslabones")
        before = fx.continuity_files()
        replay = fx.checkpoint_receipt(attempt=2)
        assert_rc0(replay, "PC-05 eslabones",
                   "el replay del cierre tras varios eslabones")
        assert fx.continuity_files() == before, (
            "PC-05: el replay no agrega enlaces")

    def orphan_body_is_not_a_close() -> None:
        fx = _Project(tmp_path / "orphan")
        _orphan_receipt(fx, close_attempt=2)
        marker = {
            "path": str(fx.receipt_path()),
            "sha256": sha256_file(fx.receipt_path()),
        }
        orphan = {
            "schema_version": 1,
            "execution_id": fx.execution_id,
            "packet_id": fx.packet_id,
            "attempt": 2,
            "record": "checkpoint",
            "goal": "cuerpo huérfano (fixture)",
            "decisions": [],
            "uncertainties": [],
            "next_action": "ninguna",
            "references": [],
            "prev": {"checkpoint_sha256": "0" * 64, "seq": 99},
            "receipt_checkpoint": marker,
        }
        orphan_sha = fx.write_body(orphan)
        proc = fx.checkpoint_receipt(attempt=2)
        assert_rc0(proc, "PC-05 huérfano",
                   "`checkpoint-receipt` con un cuerpo huérfano")
        close_sha, _ = fx.assert_close(2, "PC-05 huérfano")
        assert close_sha != orphan_sha, (
            "PC-05/§2.3.3: un cuerpo huérfano no cuenta como cierre")
        assert orphan_sha not in fx.chain_shas("PC-05 huérfano"), (
            "PC-05/§2.3.1: el cuerpo huérfano no pertenece a la cadena "
            "demostrable")
        assert fx.body_path(orphan_sha).is_file(), (
            "PC-05/§2.3.1: la historia no demostrable no se borra ni se migra")

    def legacy_body_without_prev() -> None:
        fx = _Project(tmp_path / "legacy")
        _orphan_receipt(fx, close_attempt=2)
        head = fx.head("PC-05 legado")
        body2 = fx.body(head["body_sha256"], "PC-05 legado")
        prev2 = require_prev(body2, "PC-05 legado", head["body_sha256"])
        assert isinstance(prev2, dict), (
            "PC-05 legado: §2.3.1 — el segundo eslabón debe declarar "
            f"`prev` como objeto; visto {prev2!r}")
        sha1 = prev2.get("checkpoint_sha256")
        body1 = fx.body(sha1, "PC-05 legado")
        body1.pop(PREV_KEY, None)  # cuerpo legado: sin `prev`
        new_sha1 = fx.write_body(body1)
        body2[PREV_KEY]["checkpoint_sha256"] = new_sha1
        new_sha2 = fx.write_body(body2)
        head["body_sha256"] = new_sha2
        head["prev_checkpoint_sha256"] = new_sha1
        fx.write_head(head)
        before = fx.continuity_files()
        proc = fx.checkpoint_receipt(attempt=2)
        assert_rejected(
            proc, "PC-05 cuerpo legado sin prev",
            "el cierre sobre una cadena que tropieza con un cuerpo sin "
            "`prev` (historia no demostrable)",
            pattern=CHAIN_PATTERN)
        assert fx.continuity_files() == before, (
            "PC-05: la historia no demostrable no acredita el cierre ni se "
            "reescribe")

    def head_of_another_attempt_without_close() -> None:
        fx = _Project(tmp_path / "advanced")
        assert_rc0(fx.begin(attempt=1), "PC-05 adelantada", "`begin`")
        fx.mark_dispatched()
        pending = fx.receive(n=2)
        assert_rejected(pending, "PC-05 adelantada",
                        "la recepción con cierre pendiente")
        assert fx.receipt_path().is_file()
        assert_rc0(fx.begin(attempt=2, label="attempt-2"),
                   "PC-05 adelantada", "`begin` del intento 2")
        head_before = fx.head_bytes()
        before = fx.continuity_files()
        proc = fx.checkpoint_receipt(attempt=1)
        assert_rejected(
            proc, "PC-05 cabeza adelantada",
            "el cierre de un intento anterior con la cabeza adelantada")
        assert fx.head_bytes() == head_before, (
            "PC-05/§2.4: no se rebobina ni se reemplaza la cabeza")
        assert fx.continuity_files() == before

    def head_of_another_attempt_with_close() -> None:
        fx = _Project(tmp_path / "advanced-close")
        _orphan_receipt(fx, close_attempt=2)
        assert_rc0(fx.checkpoint_receipt(attempt=2),
                   "PC-05 cierre histórico", "el cierre del intento 2")
        assert_rc0(fx.begin(attempt=3, label="attempt-3"),
                   "PC-05 cierre histórico", "`begin` del intento 3")
        before = fx.continuity_files()
        replay = fx.checkpoint_receipt(attempt=2)
        assert_rc0(replay, "PC-05 cierre histórico",
                   "el cierre idéntico demostrable con cabeza de otro intento")
        assert fx.continuity_files() == before, (
            "PC-05: el cierre histórico no se reescribe")

    def failure_after_receipt_published() -> None:
        fx = _Project(tmp_path / "published")
        assert_rc0(fx.begin(attempt=1), "PC-05 recibo publicado", "`begin`")
        fx.mark_dispatched()
        head_before = fx.head_bytes()
        proc = fx.receive(n=2)
        assert_rejected(
            proc, "PC-05 recibo publicado",
            "la recepción cuyo cierre falla después de publicar el recibo")
        assert fx.receipt_path().is_file(), (
            "PC-05/§2.4: la falla del cierre no elimina el recibo durable")
        text = output(proc)
        assert re.search(r"(?i)recib|receipt|durable", text), (
            "PC-05/§2.4: el fallo debe distinguir «recibo durable "
            f"existente»; visto:\n{tail(text)}")
        assert re.search(r"(?i)continu|pendient|pending", text), (
            "PC-05/§2.4: el fallo debe distinguir «continuidad pendiente»; "
            f"visto:\n{tail(text)}")
        assert fx.head_bytes() == head_before, (
            "PC-05/§2.4: el fallo no presenta el recorrido como cerrado")
        assert fx.close_links(2) == []

    for label, case in (
        ("tras el recibo", after_receipt),
        ("tras la transición", after_transition),
        ("varios eslabones", several_later_links),
        ("cuerpo huérfano", orphan_body_is_not_a_close),
        ("cuerpo legado sin prev", legacy_body_without_prev),
        ("cabeza adelantada sin cierre", head_of_another_attempt_without_close),
        ("cabeza adelantada con cierre", head_of_another_attempt_with_close),
        ("fallo con recibo publicado", failure_after_receipt_published),
    ):
        cases.run(label, case)
    cases.raise_if_any("PC-05")


def test_repair_preserves_history_and_invalidates_evidence_explicitly(
        tmp_path: Path) -> None:
    """PC-06: replay del cierre (inmediato, tras varios checkpoints y con
    cabeza de otro intento) devuelve éxito y la identidad original sin
    alterar archivos; misma clave con contenido distinto se rechaza; rutas
    equivalentes cuentan como la misma; otro `attempt` es otro cierre.
    Repetir `begin`/`checkpoint` idénticos conserva bytes, digest y secuencia;
    `begin` divergente rechaza y `checkpoint` divergente agrega exactamente un
    enlace. Alterar `prev` sin actualizar el digest, o publicar cabeza/cuerpo
    incoherentes aun con digest válido, se rechaza sin reparación. Una
    reparación conserva el antecedente, proyecta evidencia invalidada con
    motivo y no la rehabilita por igualdad, cambio de hash ni reanclaje; los
    cuerpos antiguos siguen leyéndose.

    RED hoy: `checkpoint-receipt` no existe, los cuerpos no declaran `prev` y
    la proyección de `resume` no emite `changes`/`evidence` → los casos
    fallan en la aserción de contrato.
    """
    cases = _Cases()

    def closed_project(base: Path, name: str) -> tuple[_Project, str, dict]:
        fx = _Project(base / name)
        assert_rc0(fx.begin(attempt=1), name, "`begin`")
        fx.mark_dispatched()
        assert_rc0(fx.receive(n=1), name, "la recepción que cierra")
        close_sha, close_body = fx.assert_close(1, f"{name} cierre")
        return fx, close_sha, close_body

    def replay_immediate_later_and_other_attempt() -> None:
        fx, close_sha, _ = closed_project(tmp_path, "replay")
        before = fx.continuity_files()
        immediate = fx.checkpoint_receipt(attempt=1)
        assert_rc0(immediate, "PC-06 replay inmediato",
                   "el replay inmediato del cierre")
        assert fx.continuity_files() == before, (
            "PC-06: el replay inmediato no altera archivos")
        assert fx.close(1, "PC-06 replay inmediato")[0] == close_sha, (
            "PC-06: el replay devuelve la identidad original del cierre")

        for index in range(1, 4):
            assert_rc0(fx.checkpoint(attempt=1, label=f"later-{index}"),
                       "PC-06 replay posterior", "un checkpoint posterior")
        after_later = fx.continuity_files()
        later = fx.checkpoint_receipt(attempt=1)
        assert_rc0(later, "PC-06 replay posterior",
                   "el replay tras varios checkpoints")
        assert fx.continuity_files() == after_later, (
            "PC-06: el replay tras varios checkpoints no altera archivos")
        assert fx.close(1, "PC-06 replay posterior")[0] == close_sha

        assert_rc0(fx.begin(attempt=2, label="attempt-2"),
                   "PC-06 replay otro intento", "`begin` del intento 2")
        after_other = fx.continuity_files()
        other = fx.checkpoint_receipt(attempt=1)
        assert_rc0(other, "PC-06 replay otro intento",
                   "el replay con cabeza de otro intento")
        assert fx.continuity_files() == after_other, (
            "PC-06: el replay con cabeza de otro intento no altera archivos")
        assert fx.close(1, "PC-06 replay otro intento")[0] == close_sha

    def same_key_different_content() -> None:
        fx, _, _ = closed_project(tmp_path, "conflict")
        before = fx.continuity_files()
        copy = fx.receipt_path().parent / "receipt-copy.json"
        copy.write_bytes(fx.receipt_bytes())
        conflict_path = fx.checkpoint_receipt(attempt=1, receipt=copy)
        assert_rejected(
            conflict_path, "PC-06 conflicto de ruta",
            "el cierre con la misma clave y OTRA ruta normalizada",
            pattern=re.compile(
                r"(?i)cierre|close|conflict|existente|existing|ya existe"))
        assert fx.continuity_files() == before, (
            "PC-06/§2.3.2: el conflicto no escribe")
        assert len(fx.close_links(1)) == 1, (
            "PC-06/§2.3.2: no se agrega un segundo cierre")

        modified = json.loads(fx.receipt_bytes())
        modified["received_at"] = "2020-01-01T00:00:00.000000Z"
        other = fx.receipt_path().parent / "receipt-other-digest.json"
        other.write_text(
            json.dumps(modified, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        conflict_digest = fx.checkpoint_receipt(attempt=1, receipt=other)
        assert_rejected(
            conflict_digest, "PC-06 conflicto de digest",
            "el cierre con la misma clave y OTRO digest",
            pattern=re.compile(
                r"(?i)cierre|close|conflict|existente|existing|ya existe"))
        assert fx.continuity_files() == before

    def equivalent_paths() -> None:
        fx, _, _ = closed_project(tmp_path, "paths")
        before = fx.continuity_files()
        dotdot = (fx.root / "docs" / ".." / ".cdad" / "runtime" / "results"
                  / fx.execution_id / fx.packet_id / RECEIPT_NAME)
        link = fx.root / "docs" / "receipt-link.json"
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(fx.receipt_path())
        for label, path in (
            ("absoluta", fx.receipt_path()),
            ("con ..", dotdot),
            ("symlink", link),
        ):
            proc = fx.checkpoint_receipt(attempt=1, receipt=path)
            assert_rc0(proc, f"PC-06 ruta {label}",
                       f"el cierre con la ruta equivalente ({label})")
            assert fx.continuity_files() == before, (
                f"PC-06/§2.3.2: la ruta equivalente ({label}) es la MISMA "
                f"ruta; no debe escribir")

    def different_attempt_is_another_close() -> None:
        fx, close_one, _ = closed_project(tmp_path, "attempts")
        assert_rc0(fx.begin(attempt=2, label="attempt-2"),
                   "PC-06 otro intento", "`begin` del intento 2")
        proc = fx.checkpoint_receipt(attempt=2)
        assert_rc0(proc, "PC-06 otro intento",
                   "el cierre de otro `attempt`")
        close_two, _ = fx.assert_close(2, "PC-06 otro intento")
        assert close_two != close_one, (
            "PC-06/§2.3.2: un `attempt` distinto es OTRO cierre")
        assert len(fx.close_links(1)) == 1
        assert len(fx.close_links(2)) == 1

    def begin_and_checkpoint_idempotency() -> None:
        fx = _Project(tmp_path / "idempotency")
        assert_rc0(fx.begin(attempt=1, label="fixed"), "PC-06 begin",
                   "`begin`")
        head_before = fx.head_bytes()
        body_before = fx.body_raw(fx.head("PC-06 begin")["body_sha256"])
        repeat = json_doc(fx.begin(attempt=1, label="fixed"), "PC-06 begin",
                          "el `begin` idéntico")
        assert repeat.get("no_op") is True, (
            "PC-06/§2.3.1: un `begin` idéntico es no-op (`no_op: true`); "
            f"visto {repeat.get('no_op')!r}")
        assert fx.head_bytes() == head_before, (
            "PC-06: el `begin` idéntico conserva bytes de la cabeza")
        assert fx.body_raw(fx.head("PC-06 begin")["body_sha256"]) == \
            body_before, (
            "PC-06: el `begin` idéntico conserva el cuerpo y su digest")

        assert_rc0(fx.checkpoint(attempt=1, label="fixed-cp"),
                   "PC-06 checkpoint", "`checkpoint`")
        cp_head = fx.head_bytes()
        cp_head_doc = fx.head("PC-06 checkpoint")
        cp_sha = cp_head_doc["body_sha256"]
        cp_body = fx.body_raw(cp_sha)
        cp_repeat = json_doc(
            fx.checkpoint(attempt=1, label="fixed-cp"), "PC-06 checkpoint",
            "el `checkpoint` idéntico")
        assert cp_repeat.get("no_op") is True, (
            "PC-06/§2.3.1: un `checkpoint` idéntico es no-op; visto "
            f"{cp_repeat.get('no_op')!r}")
        assert fx.head_bytes() == cp_head
        assert fx.body_raw(cp_sha) == cp_body

        split = fx.begin(attempt=1, label="divergent")
        assert_rejected(
            split, "PC-06 begin divergente",
            "el `begin` divergente con la misma clave",
            pattern=re.compile(r"(?i)split-brain|diverg|conflict"))
        assert fx.head_bytes() == cp_head, (
            "PC-06: el `begin` divergente no sobrescribe la cabeza")

        seq_before = cp_head_doc["seq"]
        bodies_before = set(fx.bodies())
        divergent = fx.checkpoint(attempt=1, label="divergent-cp")
        assert_rc0(divergent, "PC-06 checkpoint divergente",
                   "el `checkpoint` divergente")
        head_after = fx.head("PC-06 checkpoint divergente")
        assert head_after.get("seq") == seq_before + 1, (
            "PC-06/§2.3.1: el `checkpoint` divergente agrega EXACTAMENTE un "
            f"enlace; seq {seq_before!r} → {head_after.get('seq')!r}")
        new_bodies = set(fx.bodies()) - bodies_before
        assert len(new_bodies) == 1, (
            f"PC-06: se agrega UN cuerpo nuevo; vistos {sorted(new_bodies)}")
        fx.assert_new_link_coherent(
            cp_head_doc, head_after,
            fx.body(head_after["body_sha256"]), "PC-06 checkpoint divergente")

    def integrity_is_rejected_without_repair() -> None:
        fx = _Project(tmp_path / "integrity")
        assert_rc0(fx.begin(attempt=1), "PC-06 integridad", "`begin`")
        assert_rc0(fx.checkpoint(attempt=1, label="cp1"),
                   "PC-06 integridad", "`checkpoint`")
        head = fx.head("PC-06 integridad")
        body = fx.body(head["body_sha256"], "PC-06 integridad")
        prev = require_prev(body, "PC-06 integridad", head["body_sha256"])
        assert isinstance(prev, dict), (
            "PC-06 integridad: §2.3.1 — el segundo eslabón debe declarar "
            f"`prev` como objeto; visto {prev!r}")
        # Alterar `prev` SIN actualizar el digest (mismo nombre de archivo).
        body["prev"]["checkpoint_sha256"] = "0" * 64
        fx.body_path(head["body_sha256"]).write_bytes(
            canonical_body_bytes(body))
        tree_before = fx.tree()
        proc = fx.resume()
        assert_rejected(
            proc, "PC-06 prev sin digest",
            "la verificación de un cuerpo con `prev` alterado y digest viejo",
            pattern=CHAIN_PATTERN)
        assert fx.tree() == tree_before, (
            "PC-06/§2.3.1: la discrepancia se rechaza sin reparación "
            "automática")

        # Cabeza/cuerpo incoherentes AUN con digest válido: `prev.seq` no
        # decrece en 1.
        fx2 = _Project(tmp_path / "incoherent")
        assert_rc0(fx2.begin(attempt=1), "PC-06 incoherencia", "`begin`")
        assert_rc0(fx2.checkpoint(attempt=1, label="cp1"),
                   "PC-06 incoherencia", "`checkpoint`")
        head2 = fx2.head("PC-06 incoherencia")
        body2 = fx2.body(head2["body_sha256"], "PC-06 incoherencia")
        prev2 = require_prev(body2, "PC-06 incoherencia", head2["body_sha256"])
        assert isinstance(prev2, dict), (
            "PC-06 incoherencia: §2.3.1 — el segundo eslabón debe declarar "
            f"`prev` como objeto; visto {prev2!r}")
        body2["prev"]["seq"] = 0
        new_sha = fx2.write_body(body2)
        head2["body_sha256"] = new_sha
        fx2.write_head(head2)
        tree_before = fx2.tree()
        proc2 = fx2.resume()
        assert_rejected(
            proc2, "PC-06 cabeza/cuerpo incoherentes",
            "la verificación de una cabeza incoherente con digest válido",
            pattern=CHAIN_PATTERN)
        assert fx2.tree() == tree_before, (
            "PC-06/§2.3.1: la incoherencia se rechaza sin reparación")

    def repair_evidence() -> None:
        fx = _Project(tmp_path / "evidence")
        rel1, sha1 = fx.write_reference(
            "docs/evidence/red-pc-1.txt", "prueba PC-1 (base)\n")
        rel2, sha2 = fx.write_reference(
            "docs/evidence/red-pc-1-fix.txt", "prueba PC-1 (reparada)\n")
        rel3, sha3 = fx.write_reference(
            "src/private-impl.py", "def private_impl():\n    return 1\n")
        begin = json_doc(
            fx.begin(
                attempt=1, label="evidence-base",
                changes=["base construida"],
                evidence=[evidence_entry("red-pc-1", rel1, sha1)]),
            "PC-06 evidencia", "`begin` con evidencia")
        begin_sha = begin.get("body_sha256")
        begin_body_bytes = fx.body_raw(begin_sha)
        assert begin.get("no_op") is False

        invalidated = evidence_entry(
            "red-pc-1", rel1, sha1, status="invalidada",
            reason="la reparación cambió el comportamiento verificado",
            antecedent={"body_sha256": begin_sha, "evidence_id": "red-pc-1"})
        substitute = evidence_entry(
            "red-pc-1-fix", rel2, sha2, status="vigente",
            reason="verifica PC-1 sobre la base reparada",
            antecedent={"body_sha256": begin_sha, "evidence_id": "red-pc-1"})
        hidden = evidence_entry(
            "private-proof", rel3, sha3, status="vigente",
            reason="prueba interna del fixture")
        repair = fx.checkpoint(
            attempt=1, label="repair",
            changes=["reparación de PC-1"],
            evidence=[invalidated, substitute, hidden])
        assert_rc0(repair, "PC-06 evidencia", "el checkpoint de reparación")
        assert fx.body_raw(begin_sha) == begin_body_bytes, (
            "PC-06/§2.5: la reparación conserva el cuerpo antecedente byte "
            "a byte")

        projection = json_doc(
            fx.resume(), "PC-06 evidencia", "`resume`")["projection"]
        changes = projection.get("changes")
        assert isinstance(changes, list) and "reparación de PC-1" in changes, (
            "PC-06/§2.6: la proyección emite `changes` declarados; visto "
            f"{changes!r}")
        entries = {
            item.get("id"): item
            for item in projection.get("evidence") or []
            if isinstance(item, dict)
        }
        evidence_ids = [
            item.get("id") for item in projection.get("evidence") or []
            if isinstance(item, dict)
        ]
        assert len(evidence_ids) == len(set(evidence_ids)), (
            "PC-06/§2.5: la proyección no duplica la identidad de la "
            f"evidencia; vistas {evidence_ids}")
        assert set(entries) >= {"red-pc-1", "red-pc-1-fix", "private-proof"}, (
            f"PC-06/§2.6: la proyección emite la evidencia completa; vista "
            f"{sorted(entries)}")
        old = entries["red-pc-1"]
        assert old.get("status") == "invalidada", (
            "PC-06/§2.5: la evidencia invalidada NO se presenta como "
            f"vigente; visto {old.get('status')!r}")
        assert old.get("status") in EVIDENCE_STATUSES
        assert old.get("reason"), (
            "PC-06/§2.5: la evidencia invalidada conserva su motivo")
        assert old.get("antecedent") == {
            "body_sha256": begin_sha, "evidence_id": "red-pc-1"}, (
            "PC-06/§2.5: la evidencia invalidada conserva el antecedente "
            f"trazable; visto {old.get('antecedent')!r}")
        assert old.get("reference") == {"path": rel1, "sha256": sha1}, (
            "PC-06/§2.5: la identidad de la evidencia invalidada no se "
            f"recalcula; visto {old.get('reference')!r}")
        assert entries["red-pc-1-fix"].get("status") == "vigente"
        assert entries["red-pc-1-fix"].get("antecedent") == {
            "body_sha256": begin_sha, "evidence_id": "red-pc-1"}

        # §2.6: el filtrado por rol alcanza a las referencias de evidencia.
        filtered = output(fx.resume(role="test-writer"))
        assert rel3 not in filtered, (
            "PC-06/§2.6: `resume --role test-writer` no debe exponer la "
            f"referencia de evidencia de implementación {rel3!r}")

        # §2.5: una evidencia invalidada no vuelve a `vigente` conservando su
        # identidad (igualdad, cambio de hash o reanclaje).
        before = fx.continuity_files()
        for label, entry in (
            ("igualdad", evidence_entry(
                "red-pc-1", rel1, sha1, status="vigente",
                reason="se reacredita por igualdad de bytes")),
            ("hash", evidence_entry(
                "red-pc-1", rel2, sha2, status="vigente",
                reason="se reacredita con otro hash")),
            ("reanclaje", evidence_entry(
                "red-pc-1", rel3, sha3, status="vigente",
                reason="se reacredita reanclada")),
        ):
            proc = fx.checkpoint(
                attempt=1, label=f"rehab-{label}",
                changes=[f"intento de rehabilitación ({label})"],
                evidence=[entry])
            assert_rejected(
                proc, f"PC-06 rehabilitación por {label}",
                "la rehabilitación de evidencia invalidada")
            assert fx.continuity_files() == before, (
                f"PC-06/§2.5: la rehabilitación por {label} no escribe")

    def invalid_evidence_structures() -> None:
        fx = _Project(tmp_path / "evidence-invalid")
        rel1, sha1 = fx.write_reference(
            "docs/evidence/red-pc-1.txt", "prueba PC-1\n")
        begin = json_doc(
            fx.begin(
                attempt=1, label="evidence-base",
                evidence=[evidence_entry("red-pc-1", rel1, sha1)]),
            "PC-06 evidencia inválida", "`begin` con evidencia")
        begin_sha = begin.get("body_sha256")
        base = evidence_entry(
            "red-pc-1", rel1, sha1, status="invalidada",
            reason="motivo del fixture",
            antecedent={"body_sha256": begin_sha, "evidence_id": "red-pc-1"})
        before = fx.continuity_files()

        missing_antecedent = dict(base)
        missing_antecedent["id"] = "red-pc-2"
        missing_antecedent["antecedent"] = {
            "body_sha256": "0" * 64, "evidence_id": "red-pc-1"}
        assert_rejected(
            fx.checkpoint(
                attempt=1, label="bad-antecedent",
                evidence=[missing_antecedent]),
            "PC-06 antecedente inexistente",
            "el cierre con antecedente inexistente")
        assert fx.continuity_files() == before

        duplicate = [dict(base), dict(base)]
        assert_rejected(
            fx.checkpoint(
                attempt=1, label="duplicate-id", evidence=duplicate),
            "PC-06 id duplicado",
            "el checkpoint con id de evidencia duplicado")
        assert fx.continuity_files() == before

        no_reason = dict(base)
        no_reason["reason"] = ""
        assert_rejected(
            fx.checkpoint(
                attempt=1, label="no-reason", evidence=[no_reason]),
            "PC-06 invalidación sin razón",
            "la invalidación sin motivo")
        assert fx.continuity_files() == before

        assert_rejected(
            fx.checkpoint(attempt=1, label="empty-evidence", evidence=[]),
            "PC-06 lista vacía",
            "el checkpoint con `evidence: []` (no puede retirar en silencio)")
        assert fx.continuity_files() == before

        # Omitir `evidence` conserva la declarada (§2.5).
        omitted = fx.checkpoint(
            attempt=1, label="omit-evidence", changes=["sin evidencia"])
        assert_rc0(omitted, "PC-06 omisión", "el checkpoint sin `evidence`")
        projection = json_doc(
            fx.resume(), "PC-06 omisión", "`resume`")["projection"]
        ids = {item.get("id") for item in projection.get("evidence") or []}
        assert "red-pc-1" in ids, (
            "PC-06/§2.5: omitir `evidence` conserva la evidencia declarada; "
            f"vistos {sorted(ids)}")

    def byte_cap_is_fail_closed() -> None:
        fx = _Project(tmp_path / "cap")
        assert_rc0(fx.begin(attempt=1), "PC-06 cap", "`begin`")
        before = fx.continuity_files()
        proc = fx.checkpoint(
            attempt=1, label="huge", max_bytes=64,
            changes=["x" * 400])
        assert proc.returncode != 0, (
            "PC-06/§2.5/§2.6: el exceso de bytes falla cerrado (rc≠0); "
            f"rc={proc.returncode}")
        assert fx.continuity_files() == before, (
            "PC-06: el exceso de bytes no persiste un cuerpo truncado")

    def old_bodies_remain_readable() -> None:
        fx = _Project(tmp_path / "old")
        begin = json_doc(fx.begin(attempt=1), "PC-06 legado", "`begin`")
        begin_sha = begin.get("body_sha256")
        raw = fx.body_raw(begin_sha)
        projection = json_doc(
            fx.resume(), "PC-06 legado", "`resume`")["projection"]
        assert projection.get("changes") == [], (
            "PC-06/§2.6: un cuerpo antiguo sin `changes` se proyecta con "
            f"lista vacía; visto {projection.get('changes')!r}")
        assert projection.get("evidence") == [], (
            "PC-06/§2.6: un cuerpo antiguo sin `evidence` se proyecta con "
            f"lista vacía; visto {projection.get('evidence')!r}")
        assert fx.body_raw(begin_sha) == raw, (
            "PC-06/§2.6: la lectura no reescribe el cuerpo antiguo ni cambia "
            "su digest")

    for label, case in (
        ("replay del cierre", replay_immediate_later_and_other_attempt),
        ("conflicto de contenido", same_key_different_content),
        ("rutas equivalentes", equivalent_paths),
        ("otro attempt", different_attempt_is_another_close),
        ("idempotencia begin/checkpoint", begin_and_checkpoint_idempotency),
        ("integridad", integrity_is_rejected_without_repair),
        ("reparación y evidencia", repair_evidence),
        ("estructuras de evidencia", invalid_evidence_structures),
        ("exceso de bytes", byte_cap_is_fail_closed),
        ("cuerpos antiguos", old_bodies_remain_readable),
    ):
        cases.run(label, case)
    cases.raise_if_any("PC-06")



