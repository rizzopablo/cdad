#!/usr/bin/env python3
"""RED 007-002 — recuperación del despacho dispuesto (PC-1..PC-16, INV-1..INV-8).

Contract:
- docs/specs/007-002-dispatch-recovery/spec.md, aprobada: §2.1 (fuente y
  verificación de la disposición), §2.2 (salida de `reconcile`, precedencia y
  campos que cambian / no cambian), §2.3 (elegibilidad de `prepare
  --replace-packet`), §2.4 (sucesor, trazabilidad y `replaced_by`), §2.5
  (compatibilidad con 007-001), §3 (INV-1..INV-8) y §4 (PC-1..PC-16 con los
  nombres estables de cada test).
- Insumo de contexto: docs/specs/007-002-dispatch-recovery/discovery.md.

Superficie observable bajo prueba (CAJA NEGRA: SOLO subproceso sobre el CLI del
repo; ningún módulo de implementación se importa ni se lee):

    python3 skills/cdad-cycle/scripts/cdad_continuity.py reconcile \\
        --project-root <ABS> --execution-context <execution.json> \\
        --packet <packet-id> --json
    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \\
        --project-root <ABS> --transition disposition --packet <id> \\
        --resolution abandoned|superseded [--replaced-by <id>] \\
        [--supersedes <transition_key>]
    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare \\
        --project-root <ABS> --replace-packet <id> --reason <razón>
    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare|status|validate-state
    python3 skills/cdad-cycle/scripts/cdad_result.py receive|materialize

Fixture: proyecto descartable en un tempdir, con el `HOME` del subproceso en un
tempdir VACÍO FUERA del proyecto (nunca el HOME real, nunca este repo). La capa
previa se produce por el camino legítimo del CLI (`prepare` →
`prepare --record-dispatch` → `register-transition disposition` → `closure` /
`receive --late` / `materialize`), y las variantes que el productor no emite
(claves manipuladas, payloads reducidos, decisiones contradictorias,
duplicados) se construyen en el fixture a partir de una entrada REAL del
productor, recomputando la clave con la serialización canónica que declara
§2.1.5. Los ids del fixture son sintéticos y anónimos.

Mapeo test → postcondición:

  test_reconcile_abandoned_dispatch_is_disposed
      -> PC-1: con despacho, sin recibo y disposición canónica `abandoned`,
         `reconcile` devuelve `disposed`, `repeat_effect=false` y una
         referencia verificable a la entrada (path exacto, índice del historial
         y clave que recomputa desde su payload).
  test_reconcile_superseded_dispatch_preserves_declared_successor
      -> PC-2: con `superseded`, la señal conserva exactamente `resolution`,
         `replaced_by` (el declarado, verbatim) y la referencia a su entrada.
  test_reconcile_failed_without_disposition_remains_unresolved
      -> PC-3: un despacho sin recibo y sin disposición sigue siendo
         `dispatched-unknown`; una marca `failed` aislada no produce `disposed`.
  test_replace_disposed_packet_without_drift_prepares_successor
      -> PC-4: el activo dispuesto y elegible se reemplaza AUNQUE contrato,
         companion y política no hayan cambiado; se publica un sucesor nuevo
         `prepared` (sin despacho automático).
  test_replace_disposed_packet_preserves_assignment_and_explicit_corrections
      -> PC-5: el sucesor conserva el encargo y los bindings opcionales
         (`plan_task`, `current_decisions`) salvo corrección explícita
         (contrato re-resuelto para la preparación actual); las listas
         `conserved_fields`/`changed_fields` de `.superseded.json` no afirman
         nada que no sea observable.
  test_replace_disposed_packet_publishes_trace_without_rewriting_predecessor
      -> PC-6: la publicación deja `.superseded.json` apuntando al sucesor, con
         razón no vacía y digests correctos; `REQUEST.json`/`PACKET.md`
         anteriores no cambian.
  test_replace_disposed_packet_does_not_duplicate_existing_declared_successor
      -> PC-7: con `replaced_by` declarado —sucesor existente coherente,
         existente incoherente y declarado inexistente— se rechaza citando al
         sucesor declarado (y, en el inexistente, la vía practicable con
         `--supersedes <transition_key defectuosa>`), sin publicar ni alterar
         nada.
  test_replace_failed_or_received_packet_requires_eligible_disposition
      -> PC-8: sin disposición canónica verificable el activo `failed` se
         rechaza sin publicación; un paquete recibido o `completed` tampoco
         entra.
  test_reconcile_disposition_respects_authority_and_receipt_precedence
      -> PC-9: la disposición no desplaza autoridad expirada, recibo ilegible,
         recibo legible ni recibo con materialización (las señales no se
         pierden); una disposición verificable SIN evidencia de despacho
         produce `unknown`; `signals.disposition` está siempre presente.
  test_disposition_consumers_reject_unverifiable_or_conflicting_records
      -> PC-10: clave incorrecta, payload ausente/divergente/incompleto con
         hash recalculado, otro binding, resolución inválida, sustitución
         registrada y decisiones contradictorias no habilitan `disposed` ni
         reemplazo; la ausencia simple se distingue del `stage_history`
         inválido; sólo cuenta la disposición vigente.
  test_replace_disposed_packet_checks_active_identity_open_feature_and_no_receipt
      -> PC-11: el reemplazo rechaza paquete no activo, request ajeno o
         incoherente, feature cerrada y cualquier directorio de recibo durable;
         cada rechazo nombra la causa y no publica.
  test_replace_disposed_packet_preserves_policy_and_approval_checks
      -> PC-12: la disposición no permite saltarse política reconciliada,
         validaciones de encargo ni aprobación aplicable.
  test_reconcile_disposition_is_read_only_deterministic_and_additive
      -> PC-13: dos reconciliaciones del mismo fixture producen el mismo JSON y
         dejan el árbol byte-idéntico; el envelope conserva campos y agrega
         `signals.disposition`; con duplicados idénticos se selecciona el
         primer índice del historial.
  test_replace_disposed_packet_has_no_extra_effects_and_cannot_repeat
      -> PC-14: la preparación aceptada cambia únicamente artefactos de
         publicación y trazabilidad (sin disposiciones, recibos, despachos,
         aprobaciones ni checkpoints nuevos) y una segunda invocación no crea
         otro sucesor.
  test_prepared_packet_replacement_still_requires_verifiable_drift
      -> PC-15 (guarda de conservación): el reemplazo de un activo `prepared`
         mantiene su requisito de deriva; esta extensión no habilita reemplazar
         un preparado intacto.
  test_dispatch_recovery_preserves_007_001_status_contract
      -> PC-16: antes y después del reemplazo, `status` cumple 007-001 sin
         vocabulario, forma ni significado nuevos en `situation`,
         `next.operation` ni `authority.approval_reference`.

RED hoy (HEAD 2afdc18, medido con esta misma fixture):
- `reconcile` publica el envelope `reconcile-v1` con
  `signals.receipt|materialization|dispatch` pero SIN `signals.disposition`, y
  clasifica el despacho dispuesto como `dispatched-unknown` (no existe el valor
  `disposed`). PC-1/2/3/9/10/13 fallan en la aserción de la señal / la
  clasificación.
- `prepare --replace-packet` de un paquete `failed` se rechaza («only a
  prepared packet can be replaced»): PC-4/5/6/7/11/12/14/16 fallan en la
  aserción del contrato (rc=0 y publicación), nunca en la invocación.
- PC-8 y PC-15 son GUARDAS declaradas: hoy ya se cumple el rechazo que fijan
  (paquete sin disposición / recibido / `completed`, y preparado intacto) y se
  conservan para que la extensión no los relaje; no se les inventa un oráculo.
- Todo fallo RED es una AssertionError de contrato: jamás ImportError,
  SyntaxError, JSONDecodeError, KeyError de fixture ni error de setup.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
CONTINUITY_CLI = (
    REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_continuity.py")
RESULT_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_result.py"

# Fixture sintético y anónimo (ids inventados; ningún proyecto real).
EPIC_ID = "epic-demo-700-fixture"
FEATURE_ID = "demo-700-recovery-fixture"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_REL = "docs/cdad-policy.json"
STATE_REL = "docs/.cdad-state.json"
SPEC_REL = f"docs/specs/{FEATURE_ID}/spec.md"
PLAN_REL = f"docs/specs/{FEATURE_ID}/plan.md"
DECISION_REL = "docs/adr/ADR-demo-decision.md"
CLOSURE_REL = "docs/closures/demo-closure.md"

SPEC_BYTES = b"# Spec fixture (demo-700 dispatch recovery)\n"
SPEC_BYTES_CORRECTED = (
    b"# Spec fixture (demo-700 dispatch recovery)\n\n"
    b"correccion declarada del encargo\n")
CLOSURE_BYTES = b"# Closure fixture (demo-700)\n"
DECISION_ROW = {
    "file": DECISION_REL,
    "state": "vigente",
    "summary": "Una decision vigente del fixture demo-700.",
    "roles": ["test-writer"],
    "reference": DECISION_REL,
}
PLAN_TASK_ID = "U1"
PLAN_TASKS = {
    "validation_strategy": "Estrategia fixture demo-700.",
    "tasks": [{
        "id": PLAN_TASK_ID,
        "produce": [],
        "consume": [],
        "depends_on": [],
        "parallel": [],
        "files": ["tests/test_007_002_dispatch_recovery.py"],
        "focal_tests": ["tests/test_007_002_dispatch_recovery.py"],
        "observable_checks": ["el sucesor conserva el encargo"],
        "regressions": [],
        "integration_gate": "@validation_strategy",
        "owner": "RED: test-writer; GREEN: implementer",
    }],
}
PLAN_BYTES = (
    "# Plan fixture demo-700\n\n## 1. Bloque canonico plan-tasks\n\n"
    "```plan-tasks\n"
    + json.dumps(PLAN_TASKS, indent=1, sort_keys=True)
    + "\n```\n"
).encode("utf-8")

OBJECTIVE = "recuperar el despacho dispuesto (fixture demo-700)"
APPROVER = "Demo Approver"
REASON = "el despacho quedo sin entrega: se prepara el sucesor del dispuesto"
ROLE, SUBSTAGE = "test-writer", "red"
PACKET_BEGIN = "---cdad-packet-json"
SUPERSEDED_FILE = ".superseded.json"
RECEIPT_NAME = "receipt.json"
MATERIALIZE_NAME = "MATERIALIZE.json"
CLI_TIMEOUT_S = 120

# §2.1.6: resoluciones canónicas de la disposición.
RESOLUTIONS = ("abandoned", "superseded")
# §2.2: literales del envelope que NO cambian.
RECEIPT_KEYS = {"state", "effect", "semantic_status"}
# §2.4: campos del encargo que el sucesor conserva (salvo corrección explícita).
ASSIGNMENT_KEYS = (
    "role", "substage", "objective", "execution_id", "inputs", "read_scope",
    "write_scope", "invariants", "expected_output", "evidence_required",
    "plan_task", "current_decisions",
)
# §2.4: bindings opcionales nombrados por la spec.
OPTIONAL_BINDINGS = ("plan_task", "current_decisions")
# §2.1.4: el payload completo que produce el productor, con sus claves.
PAYLOAD_KEYS = frozenset({
    "execution_id", "feature_id", "packet_id", "transition", "stage",
    "substage", "resolution", "replaced_by", "postcondition", "current_stage",
    "artifacts", "approved_by", "contract", "plan", "closure", "receipt_sha256",
})
# 007-001 §2.1/§2.2/§2.3: vocabularios y formas PROTEGIDAS (PC-16).
SITUATIONS = {
    "diagnosis", "packet-dispatched", "packet-prepared",
    "pending-work-unresolved", "execution-active", "at-rest",
}
OPERATION_KEYS = {"verb", "script", "procedure", "source"}
APPROVAL_REFERENCE_KEYS = {
    "role", "object", "status", "record", "contract", "reason"}
APPROVAL_STATUSES = {
    "vigente", "ausente", "sustituida", "contrato cambiado", "no requerida",
    "desconocida",
}
PACKET_VIEW_KEYS = {"id", "role", "status", "substage"}


# ---------------------------------------------------------------- helpers


def entries(state: dict) -> list[dict]:
    """`stage_history` como lista (la lectura es del fixture, no del producto)."""
    history = state.get("stage_history")
    assert isinstance(history, list), (
        f"fixture: `stage_history` debe ser una lista, hay {type(history).__name__}")
    return history


def canonical_digest(payload: dict) -> str:
    """Serialización canónica declarada por §2.1.5: JSON UTF-8, ensure_ascii
    False, claves ordenadas y separadores (",", ":"), sha256 en hex."""
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def is_index(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    """Cada entrada bajo el proyecto: archivos → bytes, directorios → None."""
    return {
        path.relative_to(root).as_posix():
            path.read_bytes() if path.is_file() else None
        for path in sorted(root.rglob("*"))
    }


def changed_paths(before: dict, after: dict) -> set[str]:
    return {
        rel for rel in set(before) | set(after)
        if before.get(rel) != after.get(rel) or (rel in before) != (rel in after)
    }


def next_packet_id(packet_id: str) -> str:
    """El id siguiente según el esquema observado `<prefijo>-<NNN>`."""
    match = re.match(r"^(.*-)(\d{3})$", packet_id)
    assert match is not None, f"fixture: esquema de id inesperado {packet_id!r}"
    return f"{match.group(1)}{int(match.group(2)) + 1:03d}"


def envelope(proc: subprocess.CompletedProcess, label: str) -> dict:
    """El documento JSON de `reconcile`, o AssertionError de contrato."""
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        f"{label}: `reconcile` debe emitir la reconciliación (rc=0); "
        f"rc={proc.returncode}: {out!r}")
    assert proc.stdout.strip(), (
        f"{label}: `reconcile` no emitió el documento por stdout: {out!r}")
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{label}: stdout de `reconcile` no es un documento JSON válido: "
            f"{proc.stdout[:200]!r}") from exc
    assert isinstance(doc, dict), (
        f"{label}: el envelope de `reconcile` no es un objeto JSON: {doc!r}")
    return doc


def disposition_signal(doc: dict, label: str):
    """§2.2/PC-9: `signals.disposition` está SIEMPRE presente (null o el
    objeto). La falta de la clave es una violación de contrato, no un KeyError.
    """
    signals = doc.get("signals")
    assert isinstance(signals, dict), (
        f"{label}: `signals` debe ser un objeto: {signals!r}")
    assert "disposition" in signals, (
        f"{label}: PC-9/§2.2 — `signals.disposition` debe estar SIEMPRE "
        f"presente (`null` cuando no hay disposición admisible); claves de "
        f"`signals`: {sorted(signals)}")
    return signals["disposition"]


def assert_disposed_signal(signal: object, label: str) -> dict:
    """§2.2: el objeto de la señal tiene EXACTAMENTE los campos declarados."""
    assert isinstance(signal, dict), (
        f"{label}: PC-1/§2.2 — con disposición canónica verificable "
        f"`signals.disposition` es el objeto declarado, no {signal!r}")
    assert set(signal) == {"resolution", "replaced_by", "record"}, (
        f"{label}: §2.2 — la señal lleva exactamente `resolution`, "
        f"`replaced_by` y `record`; visto {sorted(signal)}")
    assert signal.get("resolution") in RESOLUTIONS, (
        f"{label}: §2.1.6 — `resolution` pertenece a "
        f"`abandoned|superseded`: {signal.get('resolution')!r}")
    record = signal.get("record")
    assert isinstance(record, dict), (
        f"{label}: §2.2 — `record` debe ser un objeto: {record!r}")
    assert set(record) == {"path", "index", "transition_key"}, (
        f"{label}: §2.2 — `record` lleva exactamente `path`, `index` y "
        f"`transition_key`; visto {sorted(record)}")
    assert record.get("path") == STATE_REL, (
        f"{label}: §2.2 — `record.path` es exactamente {STATE_REL!r}: "
        f"{record.get('path')!r}")
    assert is_index(record.get("index")), (
        f"{label}: §2.2 — `record.index` es un entero no negativo (base cero "
        f"en `stage_history`): {record.get('index')!r}")
    assert is_sha256(record.get("transition_key")), (
        f"{label}: §2.2 — `record.transition_key` es la clave verificada "
        f"(sha256): {record.get('transition_key')!r}")
    return signal


def assert_reference_locates_entry(
        state: dict, signal: dict, label: str) -> dict:
    """§2.2: el índice localiza la entrada en la instantánea observada y la
    clave comprueba su identidad (recomputada desde el payload)."""
    history = entries(state)
    index = signal["record"]["index"]
    assert index < len(history), (
        f"{label}: §2.2 — `record.index` ({index}) debe localizar una entrada "
        f"del `stage_history` observado ({len(history)} entradas)")
    entry = history[index]
    assert isinstance(entry, dict), (
        f"{label}: §2.2 — la entrada referida no es un objeto: {entry!r}")
    assert entry.get("transition") == "disposition", (
        f"{label}: §2.2 — la entrada referida es la disposición: {entry!r}")
    assert entry.get("transition_key") == signal["record"]["transition_key"], (
        f"{label}: §2.1.5/§2.2 — la clave de la referencia es la de la entrada "
        f"referida: {signal['record']['transition_key']!r} != "
        f"{entry.get('transition_key')!r}")
    payload = entry.get("transition_key_payload")
    assert isinstance(payload, dict), (
        f"{label}: §2.1.4 — la entrada referida lleva su payload: {entry!r}")
    assert canonical_digest(payload) == signal["record"]["transition_key"], (
        f"{label}: §2.1.5 — la clave de la referencia debe RECOMPUTARSE desde "
        f"el payload canónico (la referencia es verificable, no una etiqueta): "
        f"recomputada {canonical_digest(payload)!r}")
    return entry


def assert_names(text: str, pattern: str, label: str, what: str) -> None:
    assert re.search(pattern, text), (
        f"{label}: el rechazo debe nombrar {what} (causa observable); "
        f"visto: {text!r}")


# ---------------------------------------------------------------- fixture


class _RecoveryProject:
    """Proyecto descartable con el camino legítimo del CLI hasta el despacho.

    `plan_task=True` declara `--plan-task U1` (con su bloque `plan-tasks`) y
    `decision=True` declara una fila `--current-decision`; ambos son los
    bindings opcionales de §2.4 que PC-5 exige conservar.
    """

    def __init__(self, base: Path, *, plan_task: bool = False,
                 decision: bool = False) -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        self._build_project()
        prepared = self.prepare(plan_task=plan_task, decision=decision)
        assert prepared.returncode == 0, (
            "precondición (fixture, comportamiento existente): `prepare` debe "
            f"publicar el paquete (rc=0): {prepared.stdout!r} "
            f"{prepared.stderr!r}")
        state = self.read_state()
        active = state.get("active_packet") or {}
        self.packet_id = active.get("id")
        self.execution_id = (state.get("execution") or {}).get("id")
        assert self.packet_id and self.execution_id, (
            f"precondición (fixture): paquete y ejecución activos: {state!r}")
        self._observation = self.root / "docs" / "dispatch-observation.json"
        self._observation.write_text(
            json.dumps({
                "runtime": "demo-runtime",
                "model_configured": "demo-model",
                "model_reported": "demo-model",
                "session": "ses-demo-700-0001",
                "started_at": "2026-10-24T00:00:00Z",
                "provenance": {
                    "runtime": "reported by runtime",
                    "model_reported": "orchestrator",
                    "session": "orchestrator",
                },
            }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # -- construcción (interfaz pública del CLI) --------------------------

    def _build_project(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        for rel in ("tests", "src", "lib", "docs"):
            (self.root / rel).mkdir(exist_ok=True)
        (self.root / POLICY_REL).write_text(
            json.dumps({
                "schema_version": 1,
                "path_policy": {
                    "test_roots": ["tests"],
                    "implementation_roots": ["src", "lib"],
                    "documentation_roots": ["docs"],
                },
                "temporary_roots": [".cdad/tmp"],
            }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (self.root / SPEC_REL).parent.mkdir(parents=True, exist_ok=True)
        (self.root / SPEC_REL).write_bytes(SPEC_BYTES)
        (self.root / PLAN_REL).write_bytes(PLAN_BYTES)
        (self.root / DECISION_REL).parent.mkdir(parents=True, exist_ok=True)
        (self.root / DECISION_REL).write_text(
            "# ADR fixture demo-700\n", encoding="utf-8")
        (self.root / CLOSURE_REL).parent.mkdir(parents=True, exist_ok=True)
        (self.root / CLOSURE_REL).write_bytes(CLOSURE_BYTES)
        authority = self.root / AUTHORITY_REF
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text(
            "# Authorized execution fixture (demo-700)\n", encoding="utf-8")
        self.write_state({
            "version": 1,
            "stack": None,
            "active_epic": EPIC_ID,
            "epic_stage": "features-loop",
            "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
            "epic_history": [],
            "active_feature": FEATURE_ID,
            "current_stage": "tdd",
            "tdd_substage": "red",
            "audit_status": "approved",
            "postconditions_status": {},
            # Aprobación pineada (forma de 005-001 D3): habilita `prepare`.
            "stage_history": [{
                "feature": FEATURE_ID,
                "stage": "specification",
                "approved_by": APPROVER,
                "approved_at": "2026-10-24T00:00:00Z",
                "contract_path": SPEC_REL,
                "contract_sha256": hashlib.sha256(SPEC_BYTES).hexdigest(),
            }],
            "approver": APPROVER,
            "last_updated": "2026-10-24T00:00:00Z",
            "execution": None,
            "active_packet": None,
            "hitl_delegation": {
                "status": "active",
                "epic_id": EPIC_ID,
                "source": AUTHORITY_REF,
                "scope": EPIC_ID,
                "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
            },
        })

    # -- CLI (caja negra) -------------------------------------------------

    def env(self) -> dict:
        env = dict(os.environ)
        env["HOME"] = str(self.home)  # NUNCA el HOME real
        return env

    def _run(self, script: Path, args: list[str]
             ) -> subprocess.CompletedProcess:
        assert script.is_file(), f"CLI del repo ausente: {script}"
        return subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True, text=True, cwd=REPO_ROOT, env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
        )

    def run_packet(self, *args: str) -> subprocess.CompletedProcess:
        return self._run(PACKET_CLI, list(args))

    def run_result(self, *args: str) -> subprocess.CompletedProcess:
        return self._run(RESULT_CLI, list(args))

    def prepare(self, *, plan_task: bool = False, decision: bool = False,
                packet_id: str | None = None
                ) -> subprocess.CompletedProcess:
        args = [
            "prepare", "--project-root", str(self.root),
            "--role", ROLE, "--substage", SUBSTAGE, "--objective", OBJECTIVE,
        ]
        if packet_id is not None:
            args += ["--replace-packet", packet_id]
        if plan_task:
            args += ["--plan-task", PLAN_TASK_ID]
        if decision:
            args += ["--current-decision", json.dumps(DECISION_ROW)]
        return self.run_packet(*args)

    def dispatch(self, packet_id: str | None = None) -> subprocess.CompletedProcess:
        return self.run_packet(
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", packet_id or self.packet_id,
            "--attempt-id", "attempt-demo-700-001",
            "--input", str(self._observation))

    def dispose(self, resolution: str = "abandoned", *,
                replaced_by: str | None = None,
                supersedes: str | None = None,
                packet_id: str | None = None) -> subprocess.CompletedProcess:
        args = [
            "register-transition", "--project-root", str(self.root),
            "--transition", "disposition",
            "--packet", packet_id or self.packet_id,
            "--resolution", resolution,
        ]
        if replaced_by is not None:
            args += ["--replaced-by", replaced_by]
        if supersedes is not None:
            args += ["--supersedes", supersedes]
        return self.run_packet(*args)

    def replace(self, packet_id: str | None = None,
                reason: str = REASON) -> subprocess.CompletedProcess:
        """El sub-modo con argv PURO (identidad reusada del predecesor)."""
        return self.run_packet(
            "prepare", "--project-root", str(self.root),
            "--replace-packet", packet_id or self.packet_id,
            "--reason", reason)

    def closure(self) -> subprocess.CompletedProcess:
        return self.run_packet(
            "register-transition", "--project-root", str(self.root),
            "--transition", "closure", "--stage", "merge",
            "--approve-by", APPROVER, "--closure-path", CLOSURE_REL)

    def delivery(self, packet_id: str | None = None
                 ) -> subprocess.CompletedProcess:
        return self.run_packet(
            "register-transition", "--project-root", str(self.root),
            "--transition", "delivery", "--stage", "tdd",
            "--packet", packet_id or self.packet_id)

    def status(self) -> subprocess.CompletedProcess:
        return self.run_packet("status", "--project-root", str(self.root))

    def validate_state(self) -> subprocess.CompletedProcess:
        return self.run_packet(
            "validate-state", "--project-root", str(self.root))

    def reconcile(self, packet_id: str | None = None
                  ) -> subprocess.CompletedProcess:
        return self._run(CONTINUITY_CLI, [
            "reconcile",
            "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path()),
            "--packet", packet_id or self.packet_id,
            "--json",
        ])

    # -- camino legítimo del recibo y la materialización ------------------

    def _stage_result(self) -> Path:
        inbox = self.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "role-report.md").write_bytes(
            b"# Role report (fixture demo-700)\n")
        (inbox / "changes.json").write_text(
            json.dumps({
                "schema_version": 1,
                "observation_status": "trusted",
                "baseline_ref": "demo-baseline",
                "baseline_sha256": "0" * 64,
                "changes": [],
            }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        descriptor = inbox / "RESULT.json"
        descriptor.write_text(
            json.dumps({
                "schema_version": 1,
                "execution_id": self.execution_id,
                "packet_id": self.packet_id,
                "feature_id": FEATURE_ID,
                "source": {"kind": "staged-file", "sdk_message_ref": None},
                "parts": [{
                    "name": "role-report",
                    "artifact_kind": "test-writer-role-report",
                    "staged_path": ".cdad/inbox/role-report.md",
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

    def receive(self, *, late: bool = False) -> subprocess.CompletedProcess:
        descriptor = self._stage_result()
        packet = self.packet_dir() / "PACKET.md"
        request = self.packet_dir() / "REQUEST.json"
        assert packet.is_file() and request.is_file(), (
            "precondición (fixture): el paquete del fixture está publicado")
        args = [
            "receive", "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path()),
            "--packet", str(packet), "--request", str(request),
            "--descriptor", str(descriptor),
        ]
        if late:
            args.append("--late")
        return self.run_result(*args)

    def materialize(self) -> subprocess.CompletedProcess:
        receipt = self.receipt_path()
        assert receipt.is_file(), (
            "precondición (fixture): el recibo durable existe antes de "
            "materializar")
        authorization = self.root / ".cdad" / "inbox" / MATERIALIZE_NAME
        authorization.write_text(
            json.dumps({
                "schema_version": 1,
                "execution_id": self.execution_id,
                "packet_id": self.packet_id,
                "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
                "authorized_by": APPROVER,
                "authority_ref": AUTHORITY_REF,
                "approval_effect": False,
                "copies": [{
                    "part": "role-report",
                    "target": f"docs/specs/{FEATURE_ID}/role-report.md",
                    "expected_previous_sha256": None,
                }],
            }, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        return self.run_result(
            "materialize", "--project-root", str(self.root),
            "--receipt", str(receipt), "--authorization", str(authorization))

    # -- observación ------------------------------------------------------

    def read_state(self) -> dict:
        return json.loads(
            (self.root / STATE_REL).read_text(encoding="utf-8"))

    def write_state(self, state: dict) -> None:
        (self.root / STATE_REL).write_text(
            json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")

    def state_bytes(self) -> bytes:
        return (self.root / STATE_REL).read_bytes()

    def state_entries(self) -> list[dict]:
        return entries(self.read_state())

    def execution_context_path(self) -> Path:
        return (self.root / ".cdad" / "executions" / self.execution_id
                / "execution.json")

    def packet_dir(self, packet_id: str | None = None) -> Path:
        return self.root / ".cdad" / "packets" / (packet_id or self.packet_id)

    def packet_ids(self) -> list[str]:
        base = self.root / ".cdad" / "packets"
        if not base.is_dir():
            return []
        return sorted(p.name for p in base.iterdir() if p.is_dir())

    def request_of(self, packet_id: str) -> dict:
        return json.loads(
            (self.packet_dir(packet_id) / "REQUEST.json").read_text(
                encoding="utf-8"))

    def packet_bytes(self, packet_id: str, name: str) -> bytes:
        return (self.packet_dir(packet_id) / name).read_bytes()

    def superseded_path(self, packet_id: str | None = None) -> Path:
        return self.packet_dir(packet_id) / SUPERSEDED_FILE

    def receipt_dir(self, packet_id: str | None = None) -> Path:
        return (self.root / ".cdad" / "runtime" / "results" / self.execution_id
                / (packet_id or self.packet_id))

    def receipt_path(self, packet_id: str | None = None) -> Path:
        return self.receipt_dir(packet_id) / RECEIPT_NAME

    def dispatch_files(self) -> list[str]:
        """Archivos de despacho de la ejecución (`<execution>/dispatches/`).

        El filtro es por la ruta RELATIVA al proyecto: la ruta absoluta del
        tempdir puede contener la palabra "dispatch" (p. ej. `no-dispatch`) y
        contaminaría la observación con `execution.json`, que no es evidencia
        de despacho.
        """
        base = (self.root / ".cdad" / "executions" / self.execution_id
                / "dispatches")
        if not base.is_dir():
            return []
        return sorted(
            path.relative_to(self.root).as_posix()
            for path in base.rglob("*")
            if path.is_file())

    def tree(self) -> dict[str, bytes | None]:
        return tree_snapshot(self.root)

    # -- aserciones compartidas -------------------------------------------

    def assert_no_effects(self, label: str, before_tree: dict,
                          before_state: bytes) -> None:
        assert self.tree() == before_tree, (
            f"{label}: hubo escrituras con un rechazo — el árbol del proyecto "
            f"cambió en {sorted(changed_paths(before_tree, self.tree()))}")
        assert self.state_bytes() == before_state, (
            f"{label}: el rechazo modificó {STATE_REL} (INV-7: fallo cerrado "
            "sin efectos)")
        for packet_id in self.packet_ids():
            assert not self.superseded_path(packet_id).is_file(), (
                f"{label}: quedó un registro de superación con rechazo "
                f"({SUPERSEDED_FILE} en {packet_id})")


def _status_document(project: _RecoveryProject, label: str) -> dict:
    proc = project.status()
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        f"{label}: `status` debe emitir la vista (rc=0); rc={proc.returncode}: "
        f"{out!r}")
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{label}: stdout de `status` no es un documento JSON válido: "
            f"{proc.stdout[:200]!r}") from exc
    assert isinstance(doc, dict), (
        f"{label}: la vista no es un objeto JSON: {doc!r}")
    return doc


def _disposition_entries(state: dict) -> list[dict]:
    return [e for e in entries(state)
            if isinstance(e, dict) and e.get("transition") == "disposition"]


def _craft(entry: dict, mutate) -> dict:
    """Copia la entrada REAL del productor y la muta (fixture): la verificación
    de §2.1 es del consumidor, así que el fixture debe poder ofrecer entradas
    no canónicas."""
    crafted = copy.deepcopy(entry)
    mutate(crafted)
    return crafted


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class _Cases:
    """Acumula los fallos de contrato de casos independientes de un mismo PC.

    El RED de un PC con varios escenarios debe mostrar TODOS los escenarios
    incumplidos en una sola corrida (el fallo sigue siendo AssertionError de
    contrato: las excepciones que no son de aserción se propagan intactas).
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



# ---------------------------------------------------------------- PC-1


def test_reconcile_abandoned_dispatch_is_disposed(tmp_path: Path) -> None:
    """PC-1: con despacho registrado, ausencia de recibo y disposición canónica
    `abandoned`, `reconcile` devuelve `classification: disposed`,
    `repeat_effect: false` y `signals.disposition` con `resolution`,
    `replaced_by` y la referencia verificable a la entrada
    (`path` exacto, `index` base cero del historial y `transition_key` que
    recomputa desde su `transition_key_payload`).

    RED hoy: el envelope no tiene `signals.disposition` y la clasificación
    sigue `dispatched-unknown` → falla la aserción de la señal (AssertionError
    de contrato).
    """
    fx = _RecoveryProject(tmp_path)
    dispatched = fx.dispatch()
    assert dispatched.returncode == 0, (
        "precondición (fixture, comportamiento existente): el intento debe "
        f"registrarse (rc=0): {dispatched.stdout!r} {dispatched.stderr!r}")
    assert (fx.read_state().get("active_packet") or {}).get(
        "status") == "dispatched", (
        "precondición (fixture): el paquete activo está `dispatched`")
    assert not fx.receipt_path().exists(), (
        "precondición (fixture): el despacho NO tiene recibo durable")

    disposed = fx.dispose("abandoned")
    assert disposed.returncode == 0, (
        "precondición (comportamiento existente 006-005): la disposición "
        f"`abandoned` se registra (rc=0): {disposed.stdout!r} "
        f"{disposed.stderr!r}")
    state = fx.read_state()
    history = entries(state)
    expected_index = len(history) - 1
    assert history[expected_index].get("resolution") == "abandoned", (
        "precondición (fixture): la última entrada es la disposición")

    doc = envelope(fx.reconcile(), "PC-1")

    assert doc.get("classification") == "disposed", (
        "PC-1 violada: con despacho, sin recibo y disposición canónica "
        f"`abandoned`, `reconcile` clasifica `disposed`; visto "
        f"{doc.get('classification')!r} (envelope={json.dumps(doc, sort_keys=True)[:600]})")
    assert doc.get("repeat_effect") is False, (
        "PC-1/INV-4 violada: `disposed` NO autoriza repetir el efecto del "
        f"predecesor (`repeat_effect: false`); visto {doc.get('repeat_effect')!r}")
    assert doc.get("escalate") is False, (
        f"PC-1: `disposed` no escala (`escalate: false`): {doc.get('escalate')!r}")

    signal = assert_disposed_signal(
        disposition_signal(doc, "PC-1"), "PC-1")
    assert signal["resolution"] == "abandoned", (
        f"PC-1 violada: la señal conserva la resolución registrada: "
        f"{signal['resolution']!r}")
    assert signal["replaced_by"] is None, (
        "PC-1 violada: `abandoned` no declara sucesor "
        f"(`replaced_by: null`): {signal['replaced_by']!r}")
    assert signal["record"]["index"] == expected_index, (
        "PC-1/§2.2 violada: el índice referencia la entrada de la decisión "
        f"({expected_index}); visto {signal['record']['index']!r}")
    entry = assert_reference_locates_entry(state, signal, "PC-1")
    assert entry.get("packet_id") == fx.packet_id, (
        f"PC-1 violada: la entrada referida cita el paquete examinado: "
        f"{entry.get('packet_id')!r}")
    assert entry.get("feature") == FEATURE_ID, (
        f"PC-1 violada: la entrada referida pertenece a la feature: "
        f"{entry.get('feature')!r}")

    signals = doc.get("signals") or {}
    receipt = signals.get("receipt")
    assert isinstance(receipt, dict) and set(receipt) == RECEIPT_KEYS, (
        f"PC-1/§2.2 violada: la señal del recibo conserva su forma "
        f"(§2.2: el literal de ausencia no cambia): {receipt!r}")
    assert receipt.get("state") == "absent", (
        "PC-1 violada: sin recibo durable la señal del recibo dice `absent`: "
        f"{receipt.get('state')!r}")
    assert signals.get("dispatch") == "dispatched", (
        f"PC-1 violada: la señal del despacho se conserva: {signals.get('dispatch')!r}")
    assert signals.get("materialization") == "open", (
        "PC-1 violada: sin materialización la señal dice `open`: "
        f"{signals.get('materialization')!r}")

    reasons = doc.get("reasons")
    assert isinstance(reasons, list) and reasons, (
        f"PC-1 violada: `reasons` explica la clasificación: {reasons!r}")
    text = " ".join(str(reason).lower() for reason in reasons)
    assert re.search(r"dispos|abandon|decision|decisi", text), (
        "PC-1/§2.2 violada: `reasons` identifica la DECISIÓN registrada como "
        f"causa de `disposed`: {reasons!r}")
    assert re.search(r"repeat|repet|not authoriz|no autoriza|never authoriz",
                     text), (
        "PC-1/INV-4 violada: `reasons` distingue la decisión registrada de una "
        f"autorización para repetir: {reasons!r}")


# ---------------------------------------------------------------- PC-2


def test_reconcile_superseded_dispatch_preserves_declared_successor(
        tmp_path: Path) -> None:
    """PC-2: con disposición canónica `superseded`, la señal conserva
    EXACTAMENTE `resolution` (`superseded`), `replaced_by` (el identificador
    declarado, verbatim) y la referencia a su entrada —sin agregar ni perder
    campos.

    RED hoy: `signals.disposition` no existe → falla la aserción de la señal.
    """
    fx = _RecoveryProject(tmp_path)
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture): el despacho se registra (rc=0)")
    declared = next_packet_id(fx.packet_id)
    registered = fx.dispose("superseded", replaced_by=declared)
    assert registered.returncode == 0, (
        "precondición (comportamiento existente): `superseded` con "
        f"`--replaced-by` se registra (rc=0): {registered.stdout!r} "
        f"{registered.stderr!r}")
    state = fx.read_state()

    doc = envelope(fx.reconcile(), "PC-2")
    assert doc.get("classification") == "disposed", (
        f"PC-2 violada: la disposición `superseded` clasifica `disposed`; "
        f"visto {doc.get('classification')!r}")

    signal = assert_disposed_signal(
        disposition_signal(doc, "PC-2"), "PC-2")
    assert signal["resolution"] == "superseded", (
        f"PC-2 violada: la señal conserva `resolution`: {signal['resolution']!r}")
    assert signal["replaced_by"] == declared, (
        "PC-2 violada: la señal conserva el sucesor DECLARADO verbatim: "
        f"esperado {declared!r}, visto {signal['replaced_by']!r}")
    entry = assert_reference_locates_entry(state, signal, "PC-2")
    assert entry.get("resolution") == "superseded", (
        f"PC-2 violada: la entrada referida declara la resolución: {entry!r}")
    assert entry.get("replaced_by") == declared, (
        "PC-2 violada: la entrada referida declara el mismo sucesor: "
        f"{entry.get('replaced_by')!r}")


# ---------------------------------------------------------------- PC-3


def test_reconcile_failed_without_disposition_remains_unresolved(
        tmp_path: Path) -> None:
    """PC-3: (a) un despacho sin recibo y sin disposición sigue siendo
    `dispatched-unknown`, con `signals.disposition: null`; (b) una marca
    `failed` aislada (sin entrada de disposición) no produce `disposed`.

    RED hoy: `signals.disposition` no existe (el resto de la clasificación ya
    se cumple) → falla la aserción de la señal, no la invocación.
    """
    fx = _RecoveryProject(tmp_path)
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture): el despacho se registra (rc=0)")
    assert not _disposition_entries(fx.read_state()), (
        "precondición (fixture): no hay ninguna entrada de disposición")

    doc = envelope(fx.reconcile(), "PC-3 (a)")
    assert doc.get("classification") == "dispatched-unknown", (
        "PC-3 violada (a): despacho sin recibo y sin disposición sigue "
        f"`dispatched-unknown`; visto {doc.get('classification')!r}")
    assert disposition_signal(doc, "PC-3 (a)") is None, (
        "PC-3 violada (a): sin disposición admisible la señal es `null` "
        "(la ausencia no se disfraza de decisión)")

    # (b) marca `failed` aislada: el estado la declara, el historial no.
    state = fx.read_state()
    active = dict(state.get("active_packet") or {})
    active["status"] = "failed"
    state["active_packet"] = active
    fx.write_state(state)
    assert not _disposition_entries(fx.read_state()), (
        "precondición (fixture, (b)): la marca `failed` no agrega disposición")
    before = fx.state_bytes()

    marked = envelope(fx.reconcile(), "PC-3 (b)")
    assert marked.get("classification") != "disposed", (
        "PC-3/INV-7 violada (b): una marca `failed` aislada NO produce "
        f"`disposed`: {marked.get('classification')!r}")
    assert marked.get("classification") == "dispatched-unknown", (
        "PC-3 violada (b): sin disposición verificable la clasificación sigue "
        f"siendo `dispatched-unknown`; visto {marked.get('classification')!r}")
    assert disposition_signal(marked, "PC-3 (b)") is None, (
        "PC-3 violada (b): la marca de estado no se presenta como disposición")
    assert fx.state_bytes() == before, (
        "PC-3/INV-2 violada (b): `reconcile` es de solo lectura")


# ---------------------------------------------------------------- PC-4


def test_replace_disposed_packet_without_drift_prepares_successor(
        tmp_path: Path) -> None:
    """PC-4: un paquete activo dispuesto y elegible se reemplaza AUNQUE
    contrato, companion y política no hayan cambiado (no se exige deriva); se
    publica un sucesor NUEVO con `status: prepared` y no se despacha
    automáticamente.

    RED hoy: `--replace-packet` del `failed` se rechaza («only a prepared
    packet can be replaced») → falla la aserción del contrato (rc=0).
    """
    fx = _RecoveryProject(tmp_path)
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture): el despacho se registra (rc=0)")
    digest_before = fx.request_of(fx.packet_id)["contract"]["sha256"]
    assert digest_before == hashlib.sha256(SPEC_BYTES).hexdigest(), (
        "precondición (fixture): el contrato registrado es el vigente (sin "
        "deriva)")
    policy_before = (fx.root / POLICY_REL).read_bytes()
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (comportamiento existente): la disposición se registra")

    proc = fx.replace()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PC-4 violada: la ruta de recuperación NO exige deriva; con el paquete "
        "activo dispuesto el reemplazo debe publicar el sucesor (rc=0); "
        f"rc={proc.returncode}: {out!r}")
    assert proc.stdout.startswith(PACKET_BEGIN), (
        "PC-4 violada: la preparación aceptada imprime el `PACKET.md` "
        f"publicado (INV-5/005-001): {proc.stdout[:200]!r}")

    successors = [pid for pid in fx.packet_ids() if pid != fx.packet_id]
    assert len(successors) == 1, (
        "PC-4 violada: se publica UN sucesor nuevo; paquetes en disco: "
        f"{fx.packet_ids()}")
    successor = successors[0]
    assert successor != fx.packet_id, (
        f"PC-4/INV-5 violada: el sucesor tiene id nuevo: {successor!r}")

    state = fx.read_state()
    active = state.get("active_packet") or {}
    assert active.get("id") == successor, (
        f"PC-4 violada: `active_packet` apunta al sucesor: {active!r}")
    assert active.get("status") == "prepared", (
        "PC-4/§2.4 violada: el sucesor queda `prepared` (no se despacha "
        f"automáticamente): {active!r}")

    request = fx.request_of(successor)
    assert request.get("packet_id") == successor, (
        f"PC-4 violada: el REQUEST del sucesor se identifica: {request.get('packet_id')!r}")
    assert request.get("execution_id") == fx.execution_id, (
        "PC-4 violada: el sucesor pertenece a la misma ejecución activa: "
        f"{request.get('execution_id')!r}")
    assert (request.get("contract") or {}).get("sha256") == digest_before, (
        "PC-4 violada: sin deriva, el contrato del sucesor es el vigente "
        f"({digest_before!r}): {request.get('contract')!r}")
    assert (fx.root / POLICY_REL).read_bytes() == policy_before, (
        "PC-4 violada: la preparación no reescribe la política")

    assert fx.dispatch_files() == [
        f".cdad/executions/{fx.execution_id}/dispatches/attempt-demo-700-001.json"
    ], (
        "PC-4/§2.4 violada: el sucesor no se despacha automáticamente; "
        f"despachos registrados: {fx.dispatch_files()}")


# ---------------------------------------------------------------- PC-5


def test_replace_disposed_packet_preserves_assignment_and_explicit_corrections(
        tmp_path: Path) -> None:
    """PC-5: el sucesor conserva los campos del encargo (rol, subfase,
    objetivo, ejecución, inputs, scopes, invariantes, salida esperada,
    evidencias y los bindings opcionales `plan_task`/`current_decisions`)
    excepto correcciones explícitas; y el diff de `.superseded.json`
    (`conserved_fields`/`changed_fields`) coincide con las diferencias
    observables entre predecesor y sucesor.

    Caso (a): recuperación sin corrección → encargo idéntico, contrato vigente.
    Caso (b): corrección explícita (contrato editado y aprobación re-pineada
    por el orquestador, mecanismo público de 005-001) → el sucesor resuelve el
    contrato ACTUAL, no la autoridad histórica, y conserva el resto.

    RED hoy: el reemplazo se rechaza antes de publicar → falla la aserción del
    contrato (rc=0).
    """
    # -- (a) recuperación sin corrección ----------------------------------
    fx = _RecoveryProject(tmp_path / "sin-correccion",
                          plan_task=True, decision=True)
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (comportamiento existente): la disposición se registra")

    proc = fx.replace()
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "PC-5 violada (a): la recuperación del dispuesto debe publicar el "
        f"sucesor (rc=0); rc={proc.returncode}: {out!r}")

    state = fx.read_state()
    active = state.get("active_packet") or {}
    successor = active.get("id")
    assert successor and successor != fx.packet_id, (
        f"PC-5 violada (a): hay sucesor nuevo activo: {active!r}")

    before_request = fx.request_of(fx.packet_id)
    after_request = fx.request_of(successor)
    for key in ASSIGNMENT_KEYS:
        assert after_request.get(key) == before_request.get(key), (
            f"PC-5 violada (a): el sucesor CONSERVA el encargo; "
            f"`{key}` cambió sin corrección explícita: "
            f"{before_request.get(key)!r} → {after_request.get(key)!r}")
    for binding in OPTIONAL_BINDINGS:
        assert after_request.get(binding) == before_request.get(binding), (
            f"PC-5 violada (a): el binding opcional `{binding}` se conserva: "
            f"{after_request.get(binding)!r}")
    assert after_request.get("plan_task") == PLAN_TASK_ID, (
        "PC-5 violada (a): `plan_task` declarado viaja al sucesor: "
        f"{after_request.get('plan_task')!r}")
    assert after_request.get("current_decisions"), (
        "PC-5 violada (a): `current_decisions` declaradas viajan al sucesor: "
        f"{after_request.get('current_decisions')!r}")

    record = _load_json(fx.superseded_path(fx.packet_id))
    conserved = record.get("conserved_fields")
    changed = record.get("changed_fields")
    assert isinstance(conserved, list) and isinstance(changed, list), (
        f"PC-5 violada (a): `.superseded.json` declara las listas del diff: {record!r}")
    observable = {
        key for key in set(before_request) | set(after_request)
        if key != "packet_id"
        and before_request.get(key) != after_request.get(key)
    }
    for name in changed:
        assert name in observable, (
            "PC-5 violada (a): `changed_fields` no puede afirmar un cambio "
            f"inexistente ({name!r}); diferencias observables: {sorted(observable)}")
    for name in conserved:
        assert name in after_request and name in before_request, (
            f"PC-5 violada (a): `conserved_fields` nombra campos del encargo "
            f"({name!r})")
        assert before_request.get(name) == after_request.get(name), (
            f"PC-5 violada (a): `conserved_fields` afirma conservación falsa "
            f"para {name!r}")
    assert observable <= set(changed), (
        "PC-5 violada (a): toda diferencia observable del encargo aparece en "
        f"`changed_fields`; faltan {sorted(observable - set(changed))}")

    # -- (b) corrección explícita del contrato ----------------------------
    corrected = _RecoveryProject(tmp_path / "con-correccion",
                                 plan_task=True, decision=True)
    assert corrected.dispatch().returncode == 0, (
        "precondición (fixture (b)): el despacho se registra (rc=0)")
    assert corrected.dispose("abandoned").returncode == 0, (
        "precondición (fixture (b)): la disposición se registra")
    historical = corrected.request_of(corrected.packet_id)["contract"]["sha256"]
    (corrected.root / SPEC_REL).write_bytes(SPEC_BYTES_CORRECTED)
    state = corrected.read_state()
    repinned = False
    for entry in entries(state):
        if entry.get("feature") == FEATURE_ID and entry.get("stage") == "specification":
            entry["contract_sha256"] = hashlib.sha256(
                SPEC_BYTES_CORRECTED).hexdigest()
            repinned = True
    assert repinned, "precondición (fixture (b)): hay una entrada que re-pinear"
    corrected.write_state(state)
    current = hashlib.sha256(SPEC_BYTES_CORRECTED).hexdigest()
    assert current != historical, (
        "precondición (fixture (b)): el contrato corregido deriva del histórico")

    proc = corrected.replace()
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "PC-5 violada (b): con la aprobación re-pineada al contrato corregido "
        f"la recuperación debe publicar el sucesor (rc=0); rc={proc.returncode}: "
        f"{out!r}")

    state = corrected.read_state()
    successor = (state.get("active_packet") or {}).get("id")
    assert successor and successor != corrected.packet_id, (
        f"PC-5 violada (b): hay sucesor nuevo activo: {state.get('active_packet')!r}")
    before_request = corrected.request_of(corrected.packet_id)
    after_request = corrected.request_of(successor)
    assert (after_request.get("contract") or {}).get("sha256") == current, (
        "PC-5/§2.4 violada (b): el contrato se resuelve para la preparación "
        f"ACTUAL ({current!r}), no se copia como autoridad histórica: "
        f"{after_request.get('contract')!r}")
    assert (before_request.get("contract") or {}).get("sha256") == historical, (
        "PC-5 violada (b): el predecesor conserva su contrato registrado "
        f"({historical!r})")
    for key in ASSIGNMENT_KEYS:
        assert after_request.get(key) == before_request.get(key), (
            f"PC-5 violada (b): la corrección explícita del contrato no altera "
            f"el encargo; `{key}` cambió: {before_request.get(key)!r} → "
            f"{after_request.get(key)!r}")
    record = _load_json(corrected.superseded_path(corrected.packet_id))
    assert record.get("contract_sha256_old") == historical, (
        f"PC-5 violada (b): el registro de superación cita el contrato anterior: {record!r}")
    assert record.get("contract_sha256_new") == current, (
        f"PC-5 violada (b): el registro de superación cita el contrato vigente: {record!r}")


# ---------------------------------------------------------------- PC-6


def test_replace_disposed_packet_publishes_trace_without_rewriting_predecessor(
        tmp_path: Path) -> None:
    """PC-6: la publicación deja `.superseded.json` en el directorio del
    predecesor apuntando al sucesor, con razón no vacía y los digests
    correctos (anterior registrado, nuevo vigente); los bytes anteriores de
    `REQUEST.json` y `PACKET.md` NO cambian (§2.4, INV-5).

    RED hoy: el reemplazo se rechaza antes de publicar → falla la aserción del
    contrato (rc=0 y traza).
    """
    fx = _RecoveryProject(tmp_path)
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (comportamiento existente): la disposición se registra")
    old_request_bytes = fx.packet_bytes(fx.packet_id, "REQUEST.json")
    old_packet_bytes = fx.packet_bytes(fx.packet_id, "PACKET.md")
    old_digest = fx.request_of(fx.packet_id)["contract"]["sha256"]

    proc = fx.replace()
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "PC-6 violada: el reemplazo del dispuesto debe publicar la traza "
        f"(rc=0); rc={proc.returncode}: {out!r}")

    state = fx.read_state()
    successor = (state.get("active_packet") or {}).get("id")
    assert successor and successor != fx.packet_id, (
        f"PC-6 violada: hay sucesor activo: {state.get('active_packet')!r}")

    assert fx.packet_bytes(fx.packet_id, "REQUEST.json") == old_request_bytes, (
        "PC-6/INV-5 violada: los bytes anteriores de REQUEST.json no cambian")
    assert fx.packet_bytes(fx.packet_id, "PACKET.md") == old_packet_bytes, (
        "PC-6/INV-5 violada: los bytes anteriores de PACKET.md no cambian")
    assert proc.stdout == fx.packet_bytes(successor, "PACKET.md").decode(
        "utf-8"), (
        "PC-6 violada: stdout es el `PACKET.md` publicado por la preparación "
        "aceptada (005-001 INV-5)")

    trace_path = fx.superseded_path(fx.packet_id)
    assert trace_path.is_file(), (
        f"PC-6 violada: la publicación deja {SUPERSEDED_FILE} en el "
        "directorio del predecesor")
    record = _load_json(trace_path)
    assert record.get("superseded_by") == successor, (
        f"PC-6 violada: `superseded_by` apunta al sucesor: {record!r}")
    reason = record.get("reason")
    assert isinstance(reason, str) and reason.strip(), (
        f"PC-6 violada: la razón es no vacía: {reason!r}")
    assert reason == REASON, (
        f"PC-6 violada: la razón es la declarada en `--reason`: {reason!r}")
    assert record.get("superseded_at"), (
        f"PC-6 violada: la traza queda fechada: {record!r}")
    new_digest = (fx.request_of(successor).get("contract") or {}).get("sha256")
    assert record.get("contract_sha256_old") == old_digest, (
        "PC-6 violada: `contract_sha256_old` es el digest registrado en el "
        f"predecesor ({old_digest!r}): {record.get('contract_sha256_old')!r}")
    assert record.get("contract_sha256_new") == new_digest, (
        "PC-6 violada: `contract_sha256_new` es el digest del sucesor "
        f"({new_digest!r}): {record.get('contract_sha256_new')!r}")
    assert new_digest == hashlib.sha256(SPEC_BYTES).hexdigest(), (
        "PC-6 violada: sin deriva, el digest nuevo es el del contrato vigente: "
        f"{new_digest!r}")


# ---------------------------------------------------------------- PC-7


def test_replace_disposed_packet_does_not_duplicate_existing_declared_successor(
        tmp_path: Path) -> None:
    """PC-7: con `replaced_by` declarado en la disposición:
      (a) sucesor existente y coherente → rechazo que CITA al sucesor
          declarado, sin asignar otro identificador ni activarlo;
      (b) sucesor existente pero ilegible/incoherente → rechazo que informa la
          inconsistencia, sin crear una alternativa;
      (c) sucesor declarado inexistente → rechazo que nombra el sucesor y la
          vía practicable (`--supersedes <transition_key defectuosa>` cambiando
          la resolución), sin prometer una corrección que el productor no
          permite;
    en los tres casos no se publica ni se altera nada (árbol byte-idéntico).

    RED hoy: el reemplazo se rechaza con el guard de estado («only a prepared
    packet can be replaced»), sin citar al sucesor declarado → fallan las
    aserciones del diagnóstico y del contrato.
    """
    declared = next_packet_id("demo-700-recovery-fixture-test-writer-red-001")
    cases = _Cases()

    # -- (a) sucesor existente y coherente --------------------------------
    def case_a() -> None:
        fx = _RecoveryProject(tmp_path / "a")
        assert fx.packet_id == "demo-700-recovery-fixture-test-writer-red-001", (
            f"precondición (fixture): id esperado, hay {fx.packet_id!r}")
        assert declared == fx.packet_id[:-3] + "002", (
            f"precondición (fixture): el sucesor declarado es {declared!r}")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (a)): el despacho se registra (rc=0)")
        assert fx.dispose("superseded", replaced_by=declared).returncode == 0, (
            "precondición (fixture (a)): la disposición declara el sucesor")
        created = fx._run(PACKET_CLI, [
            "prepare", "--project-root", str(fx.root),
            "--role", ROLE, "--substage", SUBSTAGE, "--objective", OBJECTIVE,
        ])
        assert created.returncode == 0, (
            "precondición (fixture (a), comportamiento existente 006-005): tras "
            f"la disposición el CLI publica el paquete sucesor (rc=0): "
            f"{created.stdout!r} {created.stderr!r}")
        assert declared in fx.packet_ids(), (
            f"precondición (fixture (a)): el sucesor declarado existe "
            f"({declared!r}); paquetes: {fx.packet_ids()}")
        state = fx.read_state()
        failed_active = dict(state.get("active_packet") or {})
        failed_active["id"] = fx.packet_id
        failed_active["status"] = "failed"
        state["active_packet"] = failed_active
        fx.write_state(state)
        assert fx.validate_state().returncode == 0, (
            "precondición (fixture (a)): el estado del escenario es coherente")
        successor_bytes = fx.packet_bytes(declared, "REQUEST.json")
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-7 violada (a): un sucesor ya declarado y existente impide "
            f"generar otro paquete: el reemplazo se rechaza; rc={proc.returncode}: "
            f"{out!r}")
        assert PACKET_BEGIN not in proc.stdout, (
            "PC-7 violada (a): el rechazo no publica un paquete por stdout")
        assert declared in out, (
            "PC-7 violada (a): el rechazo CITA al sucesor declarado "
            f"({declared!r}): {out!r}")
        assert fx.packet_bytes(declared, "REQUEST.json") == successor_bytes, (
            "PC-7 violada (a): el sucesor declarado no se reescribe")
        assert [pid for pid in fx.packet_ids() if pid not in (
            fx.packet_id, declared)] == [], (
            f"PC-7/INV-6 violada (a): no se crea un tercer paquete: "
            f"{fx.packet_ids()}")
        fx.assert_no_effects("PC-7 (a)", before_tree, before_state)

    # -- (b) sucesor existente pero ilegible/incoherente -------------------
    def case_b() -> None:
        fx = _RecoveryProject(tmp_path / "b")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (b)): el despacho se registra (rc=0)")
        assert fx.dispose("superseded", replaced_by=declared).returncode == 0, (
            "precondición (fixture (b)): la disposición declara el sucesor")
        created = fx._run(PACKET_CLI, [
            "prepare", "--project-root", str(fx.root),
            "--role", ROLE, "--substage", SUBSTAGE, "--objective", OBJECTIVE,
        ])
        assert created.returncode == 0 and declared in fx.packet_ids(), (
            "precondición (fixture (b)): el sucesor declarado existe")
        (fx.packet_dir(declared) / "REQUEST.json").write_bytes(b"{no es json\n")
        state = fx.read_state()
        failed_active = dict(state.get("active_packet") or {})
        failed_active["id"] = fx.packet_id
        failed_active["status"] = "failed"
        state["active_packet"] = failed_active
        fx.write_state(state)
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-7 violada (b): un sucesor declarado ilegible/incoherente "
            f"también se rechaza; rc={proc.returncode}: {out!r}")
        assert declared in out, (
            "PC-7 violada (b): el rechazo nombra el sucesor declarado "
            f"({declared!r}): {out!r}")
        assert_names(out.lower(), r"incoheren|inconsist|ilegible|unreadable|"
                     r"corrupt|invalid|no se puede leer",
                     "PC-7 (b)", "la inconsistencia del sucesor")
        assert [pid for pid in fx.packet_ids() if pid not in (
            fx.packet_id, declared)] == [], (
            f"PC-7/INV-6 violada (b): no se crea una alternativa: "
            f"{fx.packet_ids()}")
        fx.assert_no_effects("PC-7 (b)", before_tree, before_state)

    # -- (c) sucesor declarado inexistente --------------------------------
    def case_c() -> None:
        fx = _RecoveryProject(tmp_path / "c")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (c)): el despacho se registra (rc=0)")
        ghost = f"{FEATURE_ID}-test-writer-red-777"
        assert fx.dispose("superseded", replaced_by=ghost).returncode == 0, (
            "precondición (fixture (c)): la disposición declara un sucesor")
        defective_key = fx.state_entries()[-1].get("transition_key")
        assert is_sha256(defective_key), (
            "precondición (fixture (c)): la entrada lleva su clave")
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-7 violada (c): un sucesor declarado inexistente se rechaza (no "
            f"se inventa un identificador); rc={proc.returncode}: {out!r}")
        assert ghost in out, (
            "PC-7 violada (c): el rechazo nombra el sucesor declarado "
            f"({ghost!r}): {out!r}")
        assert "supersedes" in out.lower(), (
            "PC-7 violada (c): el rechazo indica la vía practicable —registrar "
            "la disposición corregida con `--supersedes <transition_key "
            f"defectuosa>`—: {out!r}")
        assert defective_key in out, (
            "PC-7 violada (c): el diagnóstico cita la clave defectuosa "
            f"({defective_key!r}): {out!r}")
        assert [pid for pid in fx.packet_ids() if pid != fx.packet_id] == [], (
            f"PC-7/INV-6 violada (c): no se publica nada: {fx.packet_ids()}")
        fx.assert_no_effects("PC-7 (c)", before_tree, before_state)

    cases.run("(a)", case_a)
    cases.run("(b)", case_b)
    cases.run("(c)", case_c)
    cases.raise_if_any("PC-7")


# ---------------------------------------------------------------- PC-8


def test_replace_failed_or_received_packet_requires_eligible_disposition(
        tmp_path: Path) -> None:
    """PC-8: sin disposición canónica verificable, reemplazar un activo
    `failed` se rechaza sin publicación; un paquete recibido (recibo durable) o
    `completed` tampoco entra (INV-7: fallo cerrado).

    GUARDA declarada: hoy estos rechazos ya se cumplen; el test los conserva
    para que la extensión no los relaje y no se le inventa un oráculo nuevo.
    """
    # (a) `failed` sin disposición
    fx = _RecoveryProject(tmp_path / "failed")
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture (a)): el despacho se registra (rc=0)")
    state = fx.read_state()
    active = dict(state.get("active_packet") or {})
    active["status"] = "failed"
    state["active_packet"] = active
    fx.write_state(state)
    before_tree = fx.tree()
    before_state = fx.state_bytes()
    proc = fx.replace()
    assert proc.returncode != 0, (
        "PC-8 violada (a): un `failed` sin disposición canónica verificable NO "
        f"habilita el reemplazo; rc={proc.returncode}: {proc.stdout!r} "
        f"{proc.stderr!r}")
    assert PACKET_BEGIN not in proc.stdout, (
        "PC-8 violada (a): el rechazo no publica un paquete")
    assert fx.packet_ids() == [fx.packet_id], (
        f"PC-8 violada (a): no se publica sucesor: {fx.packet_ids()}")
    fx.assert_no_effects("PC-8 (a)", before_tree, before_state)

    # (b) paquete recibido (recibo durable, sin materialización)
    fx = _RecoveryProject(tmp_path / "received")
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture (b)): el despacho se registra (rc=0)")
    received = fx.receive()
    assert received.returncode == 0 and fx.receipt_path().is_file(), (
        "precondición (fixture (b), comportamiento existente): el recibo "
        f"durable se persiste: {received.stdout!r} {received.stderr!r}")
    before_tree = fx.tree()
    before_state = fx.state_bytes()
    proc = fx.replace()
    assert proc.returncode != 0, (
        "PC-8 violada (b): un paquete ya RECIBIDO queda fuera de esta "
        f"recuperación; rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    assert PACKET_BEGIN not in proc.stdout and fx.packet_ids() == [fx.packet_id], (
        f"PC-8 violada (b): no se publica sucesor: {fx.packet_ids()}")
    fx.assert_no_effects("PC-8 (b)", before_tree, before_state)

    # (c) paquete `completed` (entrega registrada)
    delivered = fx.delivery()
    assert delivered.returncode == 0, (
        "precondición (fixture (c), comportamiento existente): la entrega se "
        f"registra (rc=0): {delivered.stdout!r} {delivered.stderr!r}")
    assert (fx.read_state().get("active_packet") or {}).get(
        "status") == "completed", (
        "precondición (fixture (c)): el paquete quedó `completed`")
    before_tree = fx.tree()
    before_state = fx.state_bytes()
    proc = fx.replace()
    assert proc.returncode != 0, (
        "PC-8 violada (c): un paquete `completed` tampoco entra; "
        f"rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    assert PACKET_BEGIN not in proc.stdout and fx.packet_ids() == [fx.packet_id], (
        f"PC-8 violada (c): no se publica sucesor: {fx.packet_ids()}")
    fx.assert_no_effects("PC-8 (c)", before_tree, before_state)


# ---------------------------------------------------------------- PC-9


def test_reconcile_disposition_respects_authority_and_receipt_precedence(
        tmp_path: Path) -> None:
    """PC-9: la disposición no desplaza las condiciones de mayor precedencia —
    autoridad expirada, recibo ilegible, recibo legible y recibo con
    materialización— y las señales/diagnósticos comprobados no se pierden. Una
    disposición verificable SIN evidencia de despacho produce `unknown`.
    `signals.disposition` está siempre presente (null sin disposición
    admisible).

    RED hoy: falta `signals.disposition` en todos los casos → falla la
    aserción de la señal; las clasificaciones de precedencia ya se cumplen.
    """
    # (i) autoridad expirada
    fx = _RecoveryProject(tmp_path / "expired")
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture (i)): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (fixture (i)): la disposición se registra")
    state = fx.read_state()
    state["hitl_delegation"] = dict(
        state.get("hitl_delegation") or {}, status="revoked")
    fx.write_state(state)
    doc = envelope(fx.reconcile(), "PC-9 (i)")
    assert doc.get("classification") == "expired-authority", (
        "PC-9 violada (i): la autoridad expirada precede a la disposición; "
        f"visto {doc.get('classification')!r}")
    assert disposition_signal(doc, "PC-9 (i)") is not None, (
        "PC-9 violada (i): la disposición comprobada no se pierde aunque "
        "domine `expired-authority` (la señal debe seguir presente)")

    # (ii) recibo presente pero ilegible
    fx = _RecoveryProject(tmp_path / "unreadable")
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture (ii)): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (fixture (ii)): la disposición se registra")
    fx.receipt_dir().mkdir(parents=True, exist_ok=True)
    fx.receipt_path().write_bytes(b"{no es un receipt\n")
    doc = envelope(fx.reconcile(), "PC-9 (ii)")
    assert doc.get("classification") == "unknown", (
        "PC-9 violada (ii): el recibo ilegible precede a la disposición; "
        f"visto {doc.get('classification')!r}")
    assert disposition_signal(doc, "PC-9 (ii)") is not None, (
        "PC-9 violada (ii): la disposición comprobada no se pierde")
    unknowns = doc.get("unknowns")
    assert isinstance(unknowns, list) and unknowns, (
        f"PC-9 violada (ii): el diagnóstico del recibo ilegible se conserva: {unknowns!r}")
    assert any("receipt" in str(u).lower() or "recibo" in str(u).lower()
               for u in unknowns), (
        f"PC-9 violada (ii): el diagnóstico identifica el recibo: {unknowns!r}")

    # (iii) recibo legible sin materialización
    fx = _RecoveryProject(tmp_path / "received")
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture (iii)): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (fixture (iii)): la disposición se registra")
    closed = fx.closure()
    assert closed.returncode == 0, (
        "precondición (fixture (iii), comportamiento existente): el cierre se "
        f"registra (rc=0): {closed.stdout!r} {closed.stderr!r}")
    late = fx.receive(late=True)
    assert late.returncode == 0 and fx.receipt_path().is_file(), (
        "precondición (fixture (iii), comportamiento existente 006-005): el "
        f"recibo tardío se persiste: {late.stdout!r} {late.stderr!r}")
    doc = envelope(fx.reconcile(), "PC-9 (iii)")
    assert doc.get("classification") == "received", (
        "PC-9 violada (iii): el recibo legible precede a la disposición; "
        f"visto {doc.get('classification')!r}")
    assert disposition_signal(doc, "PC-9 (iii)") is not None, (
        "PC-9 violada (iii): la disposición comprobada no se pierde")
    assert (doc.get("signals") or {}).get("receipt", {}).get(
        "state") == "readable", (
        "PC-9 violada (iii): la señal del recibo legible se conserva: "
        f"{(doc.get('signals') or {}).get('receipt')!r}")

    # (iv) recibo legible CON materialización (`already-closed`)
    # El recibo y la materialización se producen por el camino legítimo en un
    # gemelo con los MISMOS ids; la entrada de disposición (producida por el
    # productor en el otro gemelo) se incorpora al estado observado porque el
    # productor no permite disponer un paquete ya recibido.
    producer = _RecoveryProject(tmp_path / "closed-producer")
    assert producer.dispatch().returncode == 0, (
        "precondición (fixture (iv)): el despacho se registra (rc=0)")
    assert producer.dispose("abandoned").returncode == 0, (
        "precondición (fixture (iv)): la disposición se produce")
    disposition_entry = copy.deepcopy(_disposition_entries(
        producer.read_state())[-1])

    closed_fx = _RecoveryProject(tmp_path / "closed")
    assert (closed_fx.packet_id, closed_fx.execution_id) == (
        producer.packet_id, producer.execution_id), (
        "precondición (fixture (iv)): ambos gemelos comparten los bindings")
    assert closed_fx.dispatch().returncode == 0, (
        "precondición (fixture (iv)): el despacho se registra (rc=0)")
    receipted = closed_fx.receive()
    assert receipted.returncode == 0, (
        "precondición (fixture (iv)): el recibo se persiste "
        f"(rc=0): {receipted.stdout!r} {receipted.stderr!r}")
    materialized = closed_fx.materialize()
    assert materialized.returncode == 0, (
        "precondición (fixture (iv), comportamiento existente): la "
        f"materialización se aplica (rc=0): {materialized.stdout!r} "
        f"{materialized.stderr!r}")
    state = closed_fx.read_state()
    state.setdefault("stage_history", []).append(disposition_entry)
    closed_fx.write_state(state)
    doc = envelope(closed_fx.reconcile(), "PC-9 (iv)")
    assert doc.get("classification") == "already-closed", (
        "PC-9 violada (iv): el recibo con materialización precede a la "
        f"disposición; visto {doc.get('classification')!r}")
    assert disposition_signal(doc, "PC-9 (iv)") is not None, (
        "PC-9 violada (iv): la disposición comprobada no se pierde")
    assert (doc.get("signals") or {}).get("materialization") == "closed", (
        "PC-9 violada (iv): la señal de materialización se conserva: "
        f"{(doc.get('signals') or {}).get('materialization')!r}")

    # (v) disposición verificable SIN evidencia de despacho → `unknown`
    fx = _RecoveryProject(tmp_path / "no-dispatch")
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture (v)): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (fixture (v)): la disposición se registra")
    dispatch_files = fx.dispatch_files()
    assert dispatch_files, "precondición (fixture (v)): hay evidencia de despacho"
    for rel in dispatch_files:
        (fx.root / rel).unlink()
    doc = envelope(fx.reconcile(), "PC-9 (v)")
    assert doc.get("classification") == "unknown", (
        "PC-9 violada (v): una disposición verificable SIN evidencia de "
        "despacho es una CONTRADICCIÓN y produce `unknown` (nunca `disposed` "
        f"ni `not-started`); visto {doc.get('classification')!r}")
    assert disposition_signal(doc, "PC-9 (v)") is not None, (
        "PC-9 violada (v): la disposición comprobada se conserva en la señal")


# ---------------------------------------------------------------- PC-10


def test_disposition_consumers_reject_unverifiable_or_conflicting_records(
        tmp_path: Path) -> None:
    """PC-10: clave incorrecta, payload ausente, divergente o incompleto con
    hash recalculado, otro binding, resolución inválida, sustitución registrada
    y decisiones contradictorias NO habilitan `disposed` ni reemplazo. La
    ausencia simple (fuentes legibles, sin entradas) se distingue del
    `stage_history` inválido: sólo la primera es `dispatched-unknown`. Sólo
    cuenta la disposición VIGENTE: una sustituida no compite frente a su
    sustituta válida.

    RED hoy: falta `signals.disposition` (y el valor `disposed`), de modo que
    las aserciones de la señal y del caso positivo de sustitución fallan como
    contrato.
    """
    # Base: una disposición REAL del productor, que el fixture muta.
    fx = _RecoveryProject(tmp_path / "base")
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (fixture): la disposición real se registra")
    pristine_state = fx.read_state()
    real_entry = copy.deepcopy(_disposition_entries(pristine_state)[-1])
    assert set(real_entry.get("transition_key_payload") or {}) == PAYLOAD_KEYS, (
        "precondición (fixture): el payload real es el completo del productor: "
        f"{sorted(real_entry.get('transition_key_payload') or {})}")
    other_packet = f"{FEATURE_ID}-implementer-green-009"
    ghost = f"{FEATURE_ID}-test-writer-red-777"

    def with_entry(crafted: dict) -> bytes:
        state = copy.deepcopy(pristine_state)
        state["stage_history"][-1] = crafted
        fx.write_state(state)
        return fx.state_bytes()

    def assert_rejected(label: str) -> None:
        doc = envelope(fx.reconcile(), label)
        assert doc.get("classification") != "disposed", (
            f"{label}: un registro no verificable o contradictorio NO habilita "
            f"`disposed`; visto {doc.get('classification')!r}")
        assert disposition_signal(doc, label) is None, (
            f"{label}: sin disposición admisible la señal es `null` (no se "
            "presenta un registro defectuoso como decisión)")
        crafted_bytes = fx.state_bytes()
        proc = fx.replace()
        assert proc.returncode != 0, (
            f"{label}: sin disposición canónica verificable el reemplazo se "
            f"rechaza; rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
        assert PACKET_BEGIN not in proc.stdout, (
            f"{label}: el rechazo no publica un sucesor")
        assert fx.packet_ids() == [fx.packet_id], (
            f"{label}: no se publica ningún paquete: {fx.packet_ids()}")
        assert fx.state_bytes() == crafted_bytes, (
            f"{label}: el rechazo no reescribe el estado")

    # -- clave incorrecta
    def wrong_key(entry: dict) -> None:
        entry["transition_key"] = "0" * 64

    with_entry(_craft(real_entry, wrong_key))
    assert_rejected("PC-10 (clave incorrecta)")

    # -- payload ausente
    def drop_payload(entry: dict) -> None:
        entry.pop("transition_key_payload", None)

    with_entry(_craft(real_entry, drop_payload))
    assert_rejected("PC-10 (payload ausente)")

    # -- payload divergente de la entrada (clave recalculada correcta)
    def divergent(entry: dict) -> None:
        entry["transition_key_payload"]["resolution"] = "superseded"
        entry["transition_key_payload"]["replaced_by"] = ghost
        entry["transition_key"] = canonical_digest(
            entry["transition_key_payload"])

    with_entry(_craft(real_entry, divergent))
    assert_rejected("PC-10 (payload divergente)")

    # -- payload INCOMPLETO con hash recalculado (§2.1.4: no es canónico)
    def incomplete(entry: dict) -> None:
        payload = entry["transition_key_payload"]
        for key in ("approved_by", "artifacts", "closure", "contract", "plan",
                    "current_stage", "postcondition"):
            payload.pop(key, None)
        entry["transition_key"] = canonical_digest(payload)

    crafted = _craft(real_entry, incomplete)
    assert set(crafted["transition_key_payload"]) < PAYLOAD_KEYS, (
        "precondición (fixture): el payload mutado es un subconjunto")
    with_entry(crafted)
    assert_rejected("PC-10 (payload incompleto con hash recalculado)")

    # -- otro binding (payload coherente entre sí, ajeno al request)
    def foreign_binding(entry: dict) -> None:
        entry["transition_key_payload"]["packet_id"] = other_packet
        entry["transition_key"] = canonical_digest(
            entry["transition_key_payload"])

    with_entry(_craft(real_entry, foreign_binding))
    assert_rejected("PC-10 (otro binding)")

    # -- resolución inválida
    def invalid_resolution(entry: dict) -> None:
        entry["resolution"] = "cancelled"
        entry["transition_key_payload"]["resolution"] = "cancelled"
        entry["transition_key"] = canonical_digest(
            entry["transition_key_payload"])

    with_entry(_craft(real_entry, invalid_resolution))
    assert_rejected("PC-10 (resolución inválida)")

    # -- `superseded` que se declara a sí mismo como sucesor (§2.1.7)
    def self_successor(entry: dict) -> None:
        entry["resolution"] = "superseded"
        entry["replaced_by"] = entry["packet_id"]
        entry["transition_key_payload"]["resolution"] = "superseded"
        entry["transition_key_payload"]["replaced_by"] = entry["packet_id"]
        entry["transition_key"] = canonical_digest(
            entry["transition_key_payload"])

    with_entry(_craft(real_entry, self_successor))
    assert_rejected("PC-10 (sucesor que se declara a sí mismo)")

    # -- sustitución registrada: la sustituida no habilita por sí sola
    # La entrada real aparece sustituida por otra NO canónica: no queda ninguna
    # decisión vigente verificable, así que la sustitución registrada no
    # habilita nada.
    state = copy.deepcopy(pristine_state)
    substitute = copy.deepcopy(real_entry)
    substitute["supersedes"] = real_entry["transition_key"]
    substitute.pop("transition_key_payload", None)
    substitute["transition_key"] = "1" * 64
    state["stage_history"].append(substitute)
    fx.write_state(state)
    assert_rejected("PC-10 (sustitución registrada sin sustituta vigente)")

    # -- decisiones vigentes contradictorias (§2.1.9)
    state = copy.deepcopy(pristine_state)
    contradicting = copy.deepcopy(real_entry)
    contradicting["resolution"] = "superseded"
    contradicting["replaced_by"] = ghost
    contradicting["transition_key_payload"]["resolution"] = "superseded"
    contradicting["transition_key_payload"]["replaced_by"] = ghost
    contradicting["transition_key"] = canonical_digest(
        contradicting["transition_key_payload"])
    state["stage_history"].append(contradicting)
    fx.write_state(state)
    doc = envelope(fx.reconcile(), "PC-10 (decisiones contradictorias)")
    assert doc.get("classification") != "disposed", (
        "PC-10/§2.1.9 violada: dos decisiones vigentes DIFERENTES no permiten "
        f"seleccionar una arbitrariamente; visto {doc.get('classification')!r}")
    assert disposition_signal(doc, "PC-10 (decisiones contradictorias)") is None, (
        "PC-10 violada: sin decisión seleccionable la señal es `null`")
    proc = fx.replace()
    assert proc.returncode != 0 and PACKET_BEGIN not in proc.stdout, (
        "PC-10 violada: la contradicción tampoco habilita el reemplazo: "
        f"rc={proc.returncode} {proc.stdout!r} {proc.stderr!r}")
    assert fx.packet_ids() == [fx.packet_id], (
        f"PC-10 violada: no se publica nada: {fx.packet_ids()}")

    # -- sólo cuenta la disposición VIGENTE (positivo de sustitución)
    vigente = _RecoveryProject(tmp_path / "vigente")
    assert vigente.dispatch().returncode == 0, (
        "precondición (fixture vigente): el despacho se registra (rc=0)")
    first = vigente.dispose("superseded", replaced_by=ghost)
    assert first.returncode == 0, (
        "precondición (fixture vigente): la primera disposición se registra")
    first_key = _disposition_entries(vigente.read_state())[-1]["transition_key"]
    second = vigente.dispose("abandoned", supersedes=first_key)
    assert second.returncode == 0, (
        "precondición (fixture vigente, comportamiento existente): la "
        "corrección con `--supersedes` se registra (rc=0): "
        f"{second.stdout!r} {second.stderr!r}")
    history = vigente.state_entries()
    vigente_entry = history[-1]
    assert vigente_entry.get("supersedes") == first_key, (
        "precondición (fixture vigente): la entrada nueva sustituye a la anterior")
    doc = envelope(vigente.reconcile(), "PC-10 (sólo la vigente)")
    assert doc.get("classification") == "disposed", (
        "PC-10/§2.1.9 violada: con una sustituta válida la reconciliación "
        f"clasifica `disposed`; visto {doc.get('classification')!r}")
    signal = assert_disposed_signal(
        disposition_signal(doc, "PC-10 (sólo la vigente)"),
        "PC-10 (sólo la vigente)")
    assert signal["record"]["index"] == len(history) - 1, (
        "PC-10/§2.1.9 violada: se referencia la disposición VIGENTE (la última "
        f"entrada), no la sustituida; visto {signal['record']['index']!r}")
    assert signal["record"]["transition_key"] == vigente_entry["transition_key"], (
        "PC-10 violada: la clave referida es la de la disposición vigente: "
        f"{signal['record']['transition_key']!r}")
    assert signal["resolution"] == "abandoned", (
        "PC-10 violada: se conserva la resolución de la disposición vigente, no "
        f"la de la sustituida: {signal['resolution']!r}")

    # -- ausencia simple vs `stage_history` inválido
    absent = _RecoveryProject(tmp_path / "absent")
    assert absent.dispatch().returncode == 0, (
        "precondición (fixture ausencia): el despacho se registra (rc=0)")
    assert not _disposition_entries(absent.read_state()), (
        "precondición (fixture ausencia): no hay entradas de disposición")
    doc = envelope(absent.reconcile(), "PC-10 (ausencia simple)")
    assert doc.get("classification") == "dispatched-unknown", (
        "PC-10 violada: la ausencia simple (fuentes legibles, sin entradas) es "
        f"`dispatched-unknown`; visto {doc.get('classification')!r}")
    assert disposition_signal(doc, "PC-10 (ausencia simple)") is None, (
        "PC-10 violada: la ausencia simple deja la señal en `null`")

    invalid = _RecoveryProject(tmp_path / "invalid")
    assert invalid.dispatch().returncode == 0, (
        "precondición (fixture inválido): el despacho se registra (rc=0)")
    broken = invalid.read_state()
    broken["stage_history"] = {"no": "es una lista"}
    invalid.write_state(broken)
    doc = envelope(invalid.reconcile(), "PC-10 (stage_history inválido)")
    assert doc.get("classification") == "unknown", (
        "PC-10 violada: un `stage_history` inválido NO es ausencia; se "
        f"diagnostica `unknown`; visto {doc.get('classification')!r}")
    assert disposition_signal(doc, "PC-10 (stage_history inválido)") is None, (
        "PC-10 violada: sin disposición admisible la señal es `null`")
    unknowns = doc.get("unknowns")
    assert isinstance(unknowns, list) and unknowns, (
        "PC-10 violada: el estado ilegible/inválido se informa con causa en "
        f"`unknowns`: {unknowns!r}")
    assert any(re.search(r"state|estado|stage_history|historial",
                         str(item).lower()) for item in unknowns), (
        f"PC-10 violada: la causa identifica la fuente: {unknowns!r}")


# ---------------------------------------------------------------- PC-11


def test_replace_disposed_packet_checks_active_identity_open_feature_and_no_receipt(
        tmp_path: Path) -> None:
    """PC-11: el reemplazo por la ruta de recuperación rechaza (i) un paquete
    que ya no es el activo, (ii) un request ajeno o incoherente, (iii) una
    feature cerrada y (iv) cualquier directorio de recibo durable (aun con
    contenido ilegible); cada rechazo nombra la causa y no publica
    (`rc≠0`, estado byte-idéntico).

    RED hoy: los rechazos ocurren por el guard de estado («only a prepared
    packet can be replaced»), no por la causa declarada → fallan las
    aserciones del diagnóstico y del contrato.
    """
    cases = _Cases()

    # -- (i) paquete no activo
    def case_i() -> None:
        fx = _RecoveryProject(tmp_path / "not-active")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (i)): el despacho se registra (rc=0)")
        assert fx.dispose("abandoned").returncode == 0, (
            "precondición (fixture (i)): la disposición se registra")
        successor = fx._run(PACKET_CLI, [
            "prepare", "--project-root", str(fx.root),
            "--role", ROLE, "--substage", SUBSTAGE, "--objective", OBJECTIVE])
        assert successor.returncode == 0, (
            "precondición (fixture (i), comportamiento existente 006-005): el "
            f"sucesor se publica (rc=0): {successor.stdout!r} {successor.stderr!r}")
        assert (fx.read_state().get("active_packet") or {}).get(
            "id") != fx.packet_id, (
            "precondición (fixture (i)): el predecesor dejó de ser el activo")
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-11 violada (i): sólo el paquete ACTIVO es reemplazable; "
            f"rc={proc.returncode}: {out!r}")
        assert_names(out.lower(), r"active|activo", "PC-11 (i)",
                     "el paquete activo")
        assert PACKET_BEGIN not in proc.stdout, (
            "PC-11 violada (i): el rechazo no publica un sucesor")
        fx.assert_no_effects("PC-11 (i)", before_tree, before_state)

    # -- (ii) request ajeno o incoherente
    def case_ii() -> None:
        fx = _RecoveryProject(tmp_path / "foreign-request")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (ii)): el despacho se registra (rc=0)")
        assert fx.dispose("abandoned").returncode == 0, (
            "precondición (fixture (ii)): la disposición se registra")
        request_path = fx.packet_dir() / "REQUEST.json"
        request = fx.request_of(fx.packet_id)
        request["packet_id"] = f"{FEATURE_ID}-test-writer-red-900"
        request_path.write_text(
            json.dumps(request, ensure_ascii=False) + "\n", encoding="utf-8")
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-11 violada (ii): un REQUEST ajeno al paquete no es elegible; "
            f"rc={proc.returncode}: {out!r}")
        assert_names(out.lower(), r"request|solicitud|coincid|mismatch|ajen|"
                     r"incoheren|inconsist",
                     "PC-11 (ii)", "el request incoherente")
        assert PACKET_BEGIN not in proc.stdout, (
            "PC-11 violada (ii): el rechazo no publica un sucesor")
        fx.assert_no_effects("PC-11 (ii)", before_tree, before_state)

    # -- (iii) feature cerrada
    def case_iii() -> None:
        fx = _RecoveryProject(tmp_path / "closed-feature")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (iii)): el despacho se registra (rc=0)")
        assert fx.dispose("abandoned").returncode == 0, (
            "precondición (fixture (iii)): la disposición se registra")
        closed = fx.closure()
        assert closed.returncode == 0, (
            "precondición (fixture (iii), comportamiento existente): el cierre "
            f"se registra (rc=0): {closed.stdout!r} {closed.stderr!r}")
        state = fx.read_state()
        assert state.get("active_feature") is None, (
            "precondición (fixture (iii)): la feature quedó cerrada")
        restored = dict(state.get("active_packet") or {})
        restored["id"] = fx.packet_id
        restored["status"] = "failed"
        state["active_packet"] = restored
        fx.write_state(state)
        assert fx.validate_state().returncode == 0, (
            "precondición (fixture (iii)): el estado del escenario es coherente")
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-11 violada (iii): con la feature cerrada la recuperación no "
            f"crea trabajo; rc={proc.returncode}: {out!r}")
        assert_names(out.lower(), r"feature|unidad|closed|cerrad|abiert|open",
                     "PC-11 (iii)", "la feature cerrada")
        assert PACKET_BEGIN not in proc.stdout, (
            "PC-11 violada (iii): el rechazo no publica un sucesor")
        fx.assert_no_effects("PC-11 (iii)", before_tree, before_state)

    # -- (iv) directorio de recibo durable (contenido ilegible)
    def case_iv() -> None:
        fx = _RecoveryProject(tmp_path / "durable-receipt")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (iv)): el despacho se registra (rc=0)")
        assert fx.dispose("abandoned").returncode == 0, (
            "precondición (fixture (iv)): la disposición se registra")
        fx.receipt_dir().mkdir(parents=True, exist_ok=True)
        fx.receipt_path().write_bytes(b"{no es un receipt\n")
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-11 violada (iv): cualquier directorio de recibo durable (aun "
            f"ilegible) excluye la recuperación; rc={proc.returncode}: {out!r}")
        assert_names(out.lower(), r"receipt|recibo|results|resultado",
                     "PC-11 (iv)", "el recibo durable")
        assert PACKET_BEGIN not in proc.stdout, (
            "PC-11 violada (iv): el rechazo no publica un sucesor")
        fx.assert_no_effects("PC-11 (iv)", before_tree, before_state)

    cases.run("(i)", case_i)
    cases.run("(ii)", case_ii)
    cases.run("(iii)", case_iii)
    cases.run("(iv)", case_iv)
    cases.raise_if_any("PC-11")


# ---------------------------------------------------------------- PC-12


def test_replace_disposed_packet_preserves_policy_and_approval_checks(
        tmp_path: Path) -> None:
    """PC-12: la disposición no permite saltarse (i) la política reconciliada,
    (ii) la aprobación aplicable ni (iii) las validaciones de encargo: cada
    variante se rechaza sin publicar y sin efectos.

    RED hoy: los tres rechazos ocurren por el guard de estado, no por la causa
    declarada → fallan las aserciones del diagnóstico y del contrato.
    """
    cases = _Cases()

    # -- (i) política revisada y no reconciliada
    def case_i() -> None:
        fx = _RecoveryProject(tmp_path / "policy")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (i)): el despacho se registra (rc=0)")
        assert fx.dispose("abandoned").returncode == 0, (
            "precondición (fixture (i)): la disposición se registra")
        policy = _load_json(fx.root / POLICY_REL)
        policy["temporary_roots"] = [".cdad/tmp-revisado"]
        (fx.root / POLICY_REL).write_text(
            json.dumps(policy, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-12 violada (i): la recuperación no se salta la reconciliación "
            f"de la política; rc={proc.returncode}: {out!r}")
        assert_names(out.lower(), r"policy|pol[ií]tica|reconcile-policy|"
                     r"reconcili", "PC-12 (i)", "la política reconciliada")
        assert PACKET_BEGIN not in proc.stdout, (
            "PC-12 violada (i): el rechazo no publica un sucesor")
        fx.assert_no_effects("PC-12 (i)", before_tree, before_state)

    # -- (ii) aprobación aplicable no vigente (contrato derivado sin re-pin)
    def case_ii() -> None:
        fx = _RecoveryProject(tmp_path / "approval")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (ii)): el despacho se registra (rc=0)")
        assert fx.dispose("abandoned").returncode == 0, (
            "precondición (fixture (ii)): la disposición se registra")
        (fx.root / SPEC_REL).write_bytes(SPEC_BYTES_CORRECTED)
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-12 violada (ii): la disposición no sustituye la aprobación "
            f"aplicable al contrato del día; rc={proc.returncode}: {out!r}")
        assert_names(out.lower(), r"approval|aprob|pending|pendiente|authoriz|"
                     r"autoriza|obsolete|obsolesc|contract|contrato",
                     "PC-12 (ii)", "la aprobación/contrato aplicable")
        assert PACKET_BEGIN not in proc.stdout, (
            "PC-12 violada (ii): el rechazo no publica un sucesor")
        fx.assert_no_effects("PC-12 (ii)", before_tree, before_state)

    # -- (iii) validaciones del encargo (piso de rol del write-scope)
    def case_iii() -> None:
        fx = _RecoveryProject(tmp_path / "scope")
        assert fx.dispatch().returncode == 0, (
            "precondición (fixture (iii)): el despacho se registra (rc=0)")
        assert fx.dispose("abandoned").returncode == 0, (
            "precondición (fixture (iii)): la disposición se registra")
        request_path = fx.packet_dir() / "REQUEST.json"
        request = fx.request_of(fx.packet_id)
        request["write_scope"] = [{"class": "implementation", "root": "src"}]
        request_path.write_text(
            json.dumps(request, ensure_ascii=False) + "\n", encoding="utf-8")
        before_tree = fx.tree()
        before_state = fx.state_bytes()

        proc = fx.replace()
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PC-12 violada (iii): la recuperación no se salta las validaciones "
            f"del encargo (piso de rol del write-scope); rc={proc.returncode}: "
            f"{out!r}")
        assert_names(out.lower(), r"scope|alcance|role|rol|policy|pol[ií]tica",
                     "PC-12 (iii)", "la validación del encargo")
        assert PACKET_BEGIN not in proc.stdout, (
            "PC-12 violada (iii): el rechazo no publica un sucesor")
        fx.assert_no_effects("PC-12 (iii)", before_tree, before_state)

    cases.run("(i)", case_i)
    cases.run("(ii)", case_ii)
    cases.run("(iii)", case_iii)
    cases.raise_if_any("PC-12")


# ---------------------------------------------------------------- PC-13


def test_reconcile_disposition_is_read_only_deterministic_and_additive(
        tmp_path: Path) -> None:
    """PC-13: dos reconciliaciones del mismo fixture producen el MISMO JSON y
    dejan byte-idénticos el estado, los paquetes, los recibos y la continuidad;
    el envelope conserva campos/tipos (schema_version, reconcile-v1,
    execution_id, packet_id, authority, head, references, repeat_effect,
    escalate y `signals.receipt|materialization|dispatch`) y agrega
    `signals.disposition`; con DUPLICADOS IDÉNTICOS de una misma decisión se
    selecciona el PRIMER índice del historial.

    RED hoy: falta `signals.disposition` y el valor `disposed` → fallan las
    aserciones del contrato; el determinismo y la ausencia de escrituras ya se
    cumplen (se conservan como guardas).
    """
    fx = _RecoveryProject(tmp_path)
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (fixture): la disposición se registra")

    before_tree = fx.tree()
    first = fx.reconcile()
    doc = envelope(first, "PC-13")
    second = fx.reconcile()
    doc_again = envelope(second, "PC-13 (segunda)")

    assert second.stdout == first.stdout, (
        "PC-13 violada: dos reconciliaciones del mismo fixture producen el "
        "MISMO documento JSON (determinismo observable)")
    assert doc_again == doc, (
        "PC-13 violada: el documento no cambia entre dos lecturas del mismo "
        "estado")
    assert fx.tree() == before_tree, (
        "PC-13/INV-2 violada: `reconcile` es de SOLO LECTURA; el árbol cambió "
        f"en {sorted(changed_paths(before_tree, fx.tree()))}")

    # Campos que NO cambian (§2.2) + el agregado.
    assert isinstance(doc.get("schema_version"), int) and doc.get(
        "schema_version") == 1, (
        f"PC-13 violada: `schema_version` conserva nombre, tipo y valor: "
        f"{doc.get('schema_version')!r}")
    assert doc.get("reconcile") == "reconcile-v1", (
        f"PC-13 violada: el marcador `reconcile-v1` se conserva: "
        f"{doc.get('reconcile')!r}")
    assert doc.get("execution_id") == fx.execution_id, (
        f"PC-13 violada: `execution_id` se conserva: {doc.get('execution_id')!r}")
    assert doc.get("packet_id") == fx.packet_id, (
        f"PC-13 violada: `packet_id` se conserva: {doc.get('packet_id')!r}")
    assert isinstance(doc.get("authority"), dict), (
        f"PC-13 violada: `authority` conserva su forma: {doc.get('authority')!r}")
    assert "head" in doc, "PC-13 violada: `head` sigue presente en el envelope"
    assert isinstance(doc.get("references"), list), (
        f"PC-13 violada: `references` conserva su tipo: {doc.get('references')!r}")
    assert doc.get("repeat_effect") is False, (
        f"PC-13 violada: `repeat_effect` se conserva: {doc.get('repeat_effect')!r}")
    assert doc.get("escalate") is False, (
        f"PC-13 violada: `escalate` se conserva: {doc.get('escalate')!r}")
    signals = doc.get("signals") or {}
    for name in ("receipt", "materialization", "dispatch"):
        assert name in signals, (
            f"PC-13 violada: `signals.{name}` se conserva: {sorted(signals)}")
    assert doc.get("classification") == "disposed", (
        f"PC-13 violada: el valor nuevo `disposed` clasifica la disposición; "
        f"visto {doc.get('classification')!r}")
    signal = assert_disposed_signal(
        disposition_signal(doc, "PC-13"), "PC-13")

    # Duplicados idénticos: se referencia el PRIMER índice.
    state = fx.read_state()
    history = entries(state)
    first_index = next(
        index for index, entry in enumerate(history)
        if isinstance(entry, dict)
        and entry.get("transition_key") == signal["record"]["transition_key"])
    duplicate = copy.deepcopy(history[first_index])
    state["stage_history"] = history + [duplicate]
    fx.write_state(state)
    duplicated_tree = fx.tree()

    doc_dup = envelope(fx.reconcile(), "PC-13 (duplicados)")
    signal_dup = assert_disposed_signal(
        disposition_signal(doc_dup, "PC-13 (duplicados)"),
        "PC-13 (duplicados)")
    assert signal_dup["record"]["index"] == first_index, (
        "PC-13/§2.2 violada: con ocurrencias idénticas de una misma decisión se "
        f"referencia la PRIMERA por índice ({first_index}); visto "
        f"{signal_dup['record']['index']!r}")
    assert first_index < len(history), (
        "precondición (fixture): el primer índice no es el duplicado agregado")
    assert signal_dup["record"]["transition_key"] == signal["record"][
        "transition_key"], (
        "PC-13 violada: el duplicado idéntico no cambia la clave referida")
    assert fx.tree() == duplicated_tree, (
        "PC-13/INV-2 violada: la lectura con duplicados tampoco escribe")


# ---------------------------------------------------------------- PC-14


def test_replace_disposed_packet_has_no_extra_effects_and_cannot_repeat(
        tmp_path: Path) -> None:
    """PC-14: una preparación aceptada cambia ÚNICAMENTE artefactos de
    publicación y trazabilidad —no agrega disposiciones, recibos, despachos,
    aprobaciones ni checkpoints— y una segunda invocación no crea otro sucesor.

    RED hoy: la primera invocación se rechaza → falla la aserción del contrato
    (rc=0).
    """
    fx = _RecoveryProject(tmp_path)
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (fixture): la disposición se registra")
    state_before = fx.read_state()
    history_before = copy.deepcopy(entries(state_before))
    dispatch_before = fx.dispatch_files()
    before_tree = fx.tree()

    proc = fx.replace()
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "PC-14 violada: la preparación aceptada publica el sucesor (rc=0); "
        f"rc={proc.returncode}: {out!r}")

    state_after = fx.read_state()
    successor = (state_after.get("active_packet") or {}).get("id")
    assert successor and successor != fx.packet_id, (
        f"PC-14 violada: hay sucesor activo: {state_after.get('active_packet')!r}")

    assert entries(state_after) == history_before, (
        "PC-14/INV-1 violada: el reemplazo NO agrega ni reescribe entradas de "
        "`stage_history` (la disposición es el único registro de la decisión)")
    assert fx.dispatch_files() == dispatch_before, (
        "PC-14 violada: el reemplazo no registra despachos nuevos: "
        f"{fx.dispatch_files()}")
    assert not fx.receipt_dir(successor).exists(), (
        "PC-14 violada: el sucesor no nace con recibo")
    assert not fx.receipt_dir(fx.packet_id).exists(), (
        "PC-14 violada: el reemplazo no crea recibo del predecesor")

    after_tree = fx.tree()
    successor_dir = f".cdad/packets/{successor}"
    allowed_prefixes = (
        successor_dir,
        f"{successor_dir}/",
        f".cdad/packets/{fx.packet_id}/{SUPERSEDED_FILE}",
        STATE_REL,
    )
    unexpected = sorted(
        rel for rel in changed_paths(before_tree, after_tree)
        if not (rel == STATE_REL
                or rel == successor_dir
                or rel.startswith(f"{successor_dir}/")
                or rel == f".cdad/packets/{fx.packet_id}/{SUPERSEDED_FILE}"))
    assert not unexpected, (
        "PC-14 violada: la preparación aceptada sólo cambia artefactos de "
        "publicación y trazabilidad; cambios inesperados: "
        f"{unexpected} (permitido: {allowed_prefixes})")

    # Segunda invocación: no crea otro sucesor ni cambia nada.
    stable_state = fx.state_bytes()
    stable_tree = fx.tree()
    again = fx.replace()
    out_again = again.stdout + again.stderr
    assert again.returncode != 0, (
        "PC-14/INV-6 violada: el predecesor dejó de ser el activo, así que una "
        f"segunda invocación no puede publicar otro sucesor; rc="
        f"{again.returncode}: {out_again!r}")
    assert PACKET_BEGIN not in again.stdout, (
        "PC-14 violada: la segunda invocación no publica un paquete")
    assert fx.packet_ids() == sorted([fx.packet_id, successor]), (
        f"PC-14 violada: no se crea un tercer paquete: {fx.packet_ids()}")
    assert fx.state_bytes() == stable_state, (
        "PC-14 violada: la segunda invocación no cambia el estado")
    assert fx.tree() == stable_tree, (
        "PC-14 violada: la segunda invocación no escribe nada")


# ---------------------------------------------------------------- PC-15


def test_prepared_packet_replacement_still_requires_verifiable_drift(
        tmp_path: Path) -> None:
    """PC-15 (guarda de conservación): el reemplazo de un activo `prepared`
    mantiene su requisito de deriva verificable; esta extensión NO habilita
    reemplazar un preparado intacto. Con deriva sí se reemplaza (comportamiento
    vigente de 005-001).

    GUARDA declarada: hoy ya se cumple; se conserva para que la ampliación de
    §2.3 no relaje la ruta existente.
    """
    intact = _RecoveryProject(tmp_path / "intact")
    assert (intact.read_state().get("active_packet") or {}).get(
        "status") == "prepared", (
        "precondición (fixture): el paquete activo está `prepared`")
    before_tree = intact.tree()
    before_state = intact.state_bytes()

    proc = intact.replace()
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        "PC-15 violada: sin deriva verificable un `prepared` intacto NO se "
        f"reemplaza; rc={proc.returncode}: {out!r}")
    assert_names(out.lower(), r"obsolescen|obsolete|deriva|drift",
                 "PC-15", "la obsolescencia verificable")
    assert PACKET_BEGIN not in proc.stdout, (
        "PC-15 violada: el rechazo no publica un sucesor")
    intact.assert_no_effects("PC-15 (intacto)", before_tree, before_state)

    drifted = _RecoveryProject(tmp_path / "drifted")
    (drifted.root / SPEC_REL).write_bytes(SPEC_BYTES_CORRECTED)
    state = drifted.read_state()
    repinned = False
    for entry in entries(state):
        if entry.get("feature") == FEATURE_ID and entry.get("stage") == "specification":
            entry["contract_sha256"] = hashlib.sha256(
                SPEC_BYTES_CORRECTED).hexdigest()
            repinned = True
    assert repinned, "precondición (fixture): hay entrada que re-pinear"
    drifted.write_state(state)

    accepted = drifted.replace()
    out_accepted = accepted.stdout + accepted.stderr
    assert accepted.returncode == 0, (
        "PC-15 violada: con deriva verificable y aprobación vigente el "
        f"reemplazo del `prepared` sigue aceptándose (rc=0); rc="
        f"{accepted.returncode}: {out_accepted!r}")
    successors = [pid for pid in drifted.packet_ids() if pid != drifted.packet_id]
    assert len(successors) == 1, (
        f"PC-15 violada: se publica un sucesor nuevo: {drifted.packet_ids()}")


# ---------------------------------------------------------------- PC-16


def test_dispatch_recovery_preserves_007_001_status_contract(
        tmp_path: Path) -> None:
    """PC-16: antes y después del reemplazo, `status` cumple 007-001 sin
    vocabulario, forma ni significado nuevos en los tres campos protegidos:
    `situation` (uno de los seis valores aprobados), `next.operation` (sus
    cuatro campos obligatorios) y `authority.approval_reference` (sus seis
    campos comunes y su vocabulario de estado). Tras publicar el sucesor, la
    vista lo presenta como `packet-prepared` (007-001 §2.1).

    RED hoy: el reemplazo se rechaza, así que el estado «después» no existe →
    falla la aserción del contrato (rc=0).
    """
    fx = _RecoveryProject(tmp_path)
    assert fx.dispatch().returncode == 0, (
        "precondición (fixture): el despacho se registra (rc=0)")
    assert fx.dispose("abandoned").returncode == 0, (
        "precondición (fixture): la disposición se registra")

    before = _status_document(fx, "PC-16 (antes)")
    assert before.get("situation") in SITUATIONS, (
        "PC-16 violada (antes): `situation` pertenece al vocabulario aprobado "
        f"de 007-001: {before.get('situation')!r}")
    assert before.get("situation") not in {"disposed", "dispatch-recovery"}, (
        "PC-16 violada (antes): la recuperación NO introduce vocabulario nuevo "
        f"en `situation`: {before.get('situation')!r}")
    operation = before.get("next", {}).get("operation")
    assert isinstance(operation, dict) and set(operation) == OPERATION_KEYS, (
        "PC-16 violada (antes): `next.operation` conserva sus cuatro campos "
        f"obligatorios: {operation!r}")
    assert all(isinstance(operation.get(key), str) and operation.get(key)
               for key in OPERATION_KEYS), (
        f"PC-16 violada (antes): los cuatro campos son no vacíos: {operation!r}")
    reference = (before.get("authority") or {}).get("approval_reference")
    assert isinstance(reference, dict) and set(
        reference) == APPROVAL_REFERENCE_KEYS, (
        "PC-16 violada (antes): `authority.approval_reference` conserva sus "
        f"seis campos comunes: {reference!r}")
    assert reference.get("status") in APPROVAL_STATUSES, (
        "PC-16 violada (antes): el estado de la referencia pertenece al "
        f"vocabulario aprobado: {reference.get('status')!r}")
    before_packet = before.get("packet")
    assert isinstance(before_packet, dict) and set(
        before_packet) == PACKET_VIEW_KEYS, (
        f"PC-16 violada (antes): la vista del paquete conserva su forma: "
        f"{before_packet!r}")
    assert before_packet.get("id") == fx.packet_id, (
        f"PC-16 violada (antes): la vista reporta el paquete activo: "
        f"{before_packet.get('id')!r}")
    assert before_packet.get("status") == "failed", (
        "PC-16/§2.5 violada (antes): un predecesor `failed` NO se convierte en "
        f"`packet-prepared`/`packet-dispatched`: {before_packet.get('status')!r}")

    proc = fx.replace()
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "PC-16 violada: el estado «después» exige un sucesor publicado "
        f"(rc=0); rc={proc.returncode}: {out!r}")
    successor = (fx.read_state().get("active_packet") or {}).get("id")
    assert successor and successor != fx.packet_id, (
        "PC-16 violada: hay sucesor activo que observar")

    after = _status_document(fx, "PC-16 (después)")
    assert after.get("situation") in SITUATIONS, (
        "PC-16 violada (después): `situation` sigue en el vocabulario aprobado "
        f"de 007-001: {after.get('situation')!r}")
    assert after.get("situation") == "packet-prepared", (
        "PC-16/§2.5 violada (después): el sucesor activo `prepared` se presenta "
        f"según 007-001; visto {after.get('situation')!r}")
    operation_after = after.get("next", {}).get("operation")
    assert isinstance(operation_after, dict) and set(
        operation_after) == OPERATION_KEYS, (
        "PC-16 violada (después): `next.operation` conserva exactamente sus "
        f"cuatro campos: {operation_after!r}")
    assert all(isinstance(operation_after.get(key), str)
               and operation_after.get(key) for key in OPERATION_KEYS), (
        "PC-16 violada (después): los cuatro campos siguen siendo no vacíos: "
        f"{operation_after!r}")
    reference_after = (after.get("authority") or {}).get("approval_reference")
    assert isinstance(reference_after, dict) and set(
        reference_after) == APPROVAL_REFERENCE_KEYS, (
        "PC-16 violada (después): `authority.approval_reference` conserva sus "
        f"seis campos comunes: {reference_after!r}")
    assert reference_after.get("status") in APPROVAL_STATUSES, (
        "PC-16 violada (después): el estado de la referencia pertenece al "
        f"vocabulario aprobado: {reference_after.get('status')!r}")
    after_packet = after.get("packet")
    assert isinstance(after_packet, dict) and set(
        after_packet) == PACKET_VIEW_KEYS, (
        f"PC-16 violada (después): la vista del paquete conserva su forma: "
        f"{after_packet!r}")
    assert after_packet.get("id") == successor, (
        "PC-16 violada (después): la vista reporta el sucesor publicado: "
        f"{after_packet.get('id')!r}")
    assert after_packet.get("status") == "prepared", (
        "PC-16 violada (después): el sucesor está `prepared` en la vista: "
        f"{after_packet.get('status')!r}")
    assert set(operation_after) == set(operation), (
        "PC-16 violada: la forma de `next.operation` no cambia con la "
        "recuperación")
    assert set(reference_after) == set(reference), (
        "PC-16 violada: la forma de `authority.approval_reference` no cambia "
        "con la recuperación")
