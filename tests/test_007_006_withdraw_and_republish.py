#!/usr/bin/env python3
"""RED 007-006 — retiro (withdraw) de paquetes preparados y republicación
independiente de agentes derivados.

Contract: `docs/specs/007-006-withdraw-and-republish/spec.md` (aprobada
2026-10-25; prevalece la sección final «Ajustes del orquestador» AJ1–AJ4 con
las 8 postcondiciones consolidadas — los nombres de test de la tabla
§"Postcondiciones y verificación" son orientativos y las variantes van
parametrizadas). Autorización y excepción de arranque:
`docs/planning/handoff-2026-10-24-epic-007.md:58-61`.

Método obligatorio (cambio de método del 2026-10-25):
- Los fixtures y tests EXISTENTES de la capacidad se reutilizan por import y
  se extienden, no se copian: `_RecoveryProject` (007-002: camino legítimo
  prepare → despacho → disposición → receive → materialize), `_begin`,
  `_suspend` y `_state` (007-007: continuidad con evidencia identificable y
  guarda de suspensión compartida). Este módulo agrega SOLO los constructores
  propios del retiro/republicación (instalación simulada para DRIFT,
  trasplante del rastro real de recepción, fábricas de variantes).
- Oráculos estructurados: rc, JSON (estado, manifiesto, continuidad, vista)
  y bytes de archivo (snapshot del árbol / mtimes). La única lectura de texto
  es el diagnóstico del rechazo (regex sobre stdout+stderr que exige
  fuente/causa); nunca se afirma prosa libre.
- Las FUNCIONES de test no contienen `if`/`for`: una postcondición por test,
  variantes por parametrización (fábricas de fixture/orden declaradas a nivel
  de módulo). Los constructores de fixture usan bucles y comprensiones
  mecánicas de construcción de directorios; no contienen lógica de oráculo.

Mapeo test → postcondición (AJ3, 8 consolidadas ↔ PCs de la tabla):

  PC-01 test_withdraw_prepared_packet_preserves_artifacts_and_frees_prepare
  PC-02 test_withdraw_requires_reason_and_matching_active_prepared_packet  (6 variantes)
  PC-03 test_withdraw_rejects_effects_and_inconclusive_signals             (10 variantes)
  PC-04 test_withdraw_closes_current_begin_without_fabricating_delivery    (+ AJ2: evidencia)
  PC-05 test_withdraw_handles_absent_foreign_and_invalid_continuity        (4 variantes)
  PC-06 test_withdraw_is_idempotent_and_rejects_conflicting_repetition
  PC-07 test_withdraw_rejects_unrelated_transition_flags                   (21 variantes)
  PC-08 test_republish_agents_repairs_project_drift_without_cycle_changes
  PC-09 test_republish_agents_inherits_installed_model_and_is_idempotent
  PC-10 test_republish_agents_preserves_existing_derivation_guards         (8 variantes, incl. transaccionales)
  PC-11 test_status_preserves_prepared_situation_and_exposes_independent_drift_resolution
  PC-12 test_prepared_begin_and_project_drift_recovery_both_orders         (2 órdenes AJ4)
  PC-13 test_withdraw_publication_failure_preserves_state_and_continuity   (2 variantes transaccionales)
  AJ1  test_withdraw_and_republish_respect_suspended_units                 (PC consolidada 7)
  AJ1  test_withdraw_suspension_guard_is_per_unit_with_other_unit_active   (review-002: guarda por unidad)

Ampliación review-002 (2026-10-26): tres hallazgos agregan los casos
transaccionales de `republish-agents` (fallo del reemplazo del segundo destino
y fallo de la escritura del manifiesto: TODOS los destinos byte-idénticos, sin
conjunto parcial), los transaccionales del retiro (fallo publicando la cabeza y
fallo publicando el estado tras el checkpoint: snapshot completo de
`continuity/` incluido `bodies/` idéntico, sin cuerpo nuevo) y la guarda de
suspensión POR UNIDAD (con A suspendida y B activa, el paquete de A → rc=1 y el
retiro real de B con su replay idéntico sigue el contrato). Condiciones reales
de filesystem (destino convertido en directorio, `.tmp` bloqueado por un
directorio); snapshot completo de bytes e inventario antes/después; el
rechazo nombra la causa buscada.

RED hoy (HEAD 7c34fde; superficie medida con sondas de CLI en tempdirs):
- `register-transition` acepta {delivery,advance,gate,closure,late-delivery,
  disposition} y NO `withdraw`; el verbo `republish-agents` no existe
  (`invalid choice`, rc=2). Toda prueba de retiro falla en la GUARDA de
  superficie (`--help` rc=0 debe listar `withdraw`) y toda prueba de
  republicación en la GUARDA (`republish-agents -h` rc=0): AssertionError de
  contrato que evita un RED falso verde cuando el verbo no existe (un
  argparse ausente y un rechazo de dominio devuelven el mismo rc).
- PC-11 falla además en su aserción de resolución: la vista de HOY dice
  «the next `prepare` republishes…» y no nombra `republish-agents`.
- Los controles de forma que HOY ya se cumplen (situation `packet-prepared`
  con begin+DRIFT, `validate-packet`, `divergent_legs: ["project"]`,
  `execution-active → resume` con binding terminal, conservación de
  `suspended_units`) quedan como guardas de no-regresión de la extensión.
- Código de salida declarado por contrato: éxito 0; rechazo de dominio 2
  (convención 007-002/007-007); CONFLICTO protegido 1 (AJ1 fija rc=1 para la
  guarda de suspensión; «es conflicto» del retiro repetido con otro motivo
  sigue la misma clase de 007-003 reanchor `_assert_rc1_unchanged`).
Ningún fallo RED es ImportError, SyntaxError, JSONDecodeError ni error de
fixture: las precondiciones del fixture se asercionan con mensajes propios.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from test_007_002_dispatch_recovery import (
    CONTINUITY_CLI,
    FEATURE_ID,
    PACKET_CLI,
    REPO_ROOT,
    _RecoveryProject,
    canonical_digest,
    entries,
)
from test_007_007_suspend_resume_units import (
    FEATURE_B,
    STATE_REL,
    _begin,
    _state,
    _suspend,
)

CLI_TIMEOUT_S = 120
SKILLS_TREE = REPO_ROOT / "skills"
AGENTS_TREE = REPO_ROOT / "agents"
MANIFEST_REL = ".opencode/agents/.cdad-derived.json"
DERIVED_DIR_REL = ".opencode/agents"
FOREIGN_AGENT = "mi-agente-propio.md"

# Versiones sintéticas de fixture (opacas, distintas entre sí).
VERSION_V1 = "aaaa11111"   # instalación de origen del prepare inicial
VERSION_V2 = "bbbb22222"   # instalación actualizada (DRIFT de la pata project)
VERSION_V0 = "000zzzzz"    # una instalación ajena para la pata `agents`

WITHDRAW_NOTE = "el encargo no llegó a despacharse: se retira el paquete preparado (fixture 007-006)"
OTHER_NOTE = "motivo distinto del retiro ya registrado (conflicto fixture 007-006)"

EVIDENCE_REL = "docs/withdraw-evidence.md"
EVIDENCE_BYTES = b"evidencia vigente del fixture 007-006\n"
BEGIN_EVIDENCE = [{
    "id": "withdraw-evidence",
    "reference": {"path": EVIDENCE_REL,
                  "sha256": hashlib.sha256(EVIDENCE_BYTES).hexdigest()},
    "status": "vigente",
    "reason": "evidencia vigente de begin (fixture AJ2)",
    "antecedent": None,
}]

# Diagnóstico: fuente/causa del rechazo (stems bilingües, insensible a caja).
DISPATCH_CAUSE = re.compile(r"(?i)dispatch|despach")
RESULTS_CAUSE = re.compile(r"(?i)result|resultado|bundle|staged|receipt|recibo")
RECEIPT_CAUSE = re.compile(r"(?i)receipt|recibo|result|resultado")
MATERIALIZATION_CAUSE = re.compile(r"(?i)materializ")
DISPOSITION_CAUSE = re.compile(r"(?i)dispos")
NOT_PREPARED_CAUSE = re.compile(r"(?i)prepared|prepar|dispatched|failed")

# PC-07: los campos ajenos enumerados por la interfaz del retiro (§Contrato CLI).
FOREIGN_FLAGS: tuple[tuple[str, str | None], ...] = (
    ("--stage", "merge"),
    ("--resolution", "abandoned"),
    ("--replaced-by", f"{FEATURE_ID}-test-writer-red-002"),
    ("--approve-by", "Demo Approver"),
    ("--contract-path", f"docs/specs/{FEATURE_ID}/spec.md"),
    ("--contract-sha256", "0" * 64),
    ("--plan-path", f"docs/specs/{FEATURE_ID}/plan.md"),
    ("--plan-sha256", "1" * 64),
    ("--exempted-by", "Demo Approver"),
    ("--exemption-reason", "razón ajena"),
    ("--requested-by", "Demo Approver"),
    ("--delegated", None),
    ("--current-stage", "tdd"),
    ("--substage", "red"),
    ("--receipt", "2" * 64),
    ("--artifact", f"docs/specs/{FEATURE_ID}/role-report.md"),
    ("--postcondition", "1"),
    ("--outcome", "red"),
    ("--supersedes", "3" * 64),
    ("--closure-path", "docs/closures/demo-closure.md"),
    ("--closure-sha256", "4" * 64),
)


# ---------------------------------------------------------------- helpers


def _assert_withdraw_surface(fx: _RecoveryProject) -> None:
    """Guarda RED: la superficie `--transition withdraw` debe existir.

    Sin la guarda, un argparse sin la elección devolvería rc=2 igual que un
    rechazo de dominio y el RED pasaría en falso.
    """
    proc = fx.run_packet("register-transition", "--help")
    assert proc.returncode == 0, (
        "guarda RED 007-006: `register-transition --help` debe responder "
        f"rc=0 antes de probar el retiro; visto rc={proc.returncode}: "
        f"{proc.stdout!r} {proc.stderr!r}")
    assert "withdraw" in proc.stdout, (
        "guarda RED 007-006: `--transition withdraw` no existe en la "
        "superficie de `register-transition` (elecciones de hoy en la "
        f"ayuda): {proc.stdout!r}")


def _assert_republish_surface(fx: _RecoveryProject) -> None:
    """Guarda RED: el verbo `republish-agents` debe existir."""
    proc = fx.run_packet("republish-agents", "-h")
    assert proc.returncode == 0, (
        "guarda RED 007-006: `republish-agents -h` debe responder rc=0 antes "
        "de probar la republicación; visto rc="
        f"{proc.returncode} (hoy el verbo es `invalid choice`): "
        f"{proc.stdout!r} {proc.stderr!r}")


def _withdraw(fx: _RecoveryProject, *extra: str, packet_id: str | None = None,
              note: str | None = WITHDRAW_NOTE) -> subprocess.CompletedProcess:
    args = [
        "register-transition", "--project-root", str(fx.root),
        "--transition", "withdraw", "--packet", packet_id or fx.packet_id,
    ]
    if note is not None:
        args += ["--note", note]
    return fx.run_packet(*args, *extra)


def _withdraw_with_flag(fx: _RecoveryProject, flag: str,
                        value: str | None) -> subprocess.CompletedProcess:
    extra = [item for item in (flag, value) if item is not None]
    return _withdraw(fx, *extra)


def _republish(fx: _RecoveryProject) -> subprocess.CompletedProcess:
    return fx.run_packet("republish-agents", "--project-root", str(fx.root))


def _restore_prepared(fx: _RecoveryProject) -> None:
    """Fixture: devuelve el binding activo a `prepared` conservando los demás
    campos (variante inconclusa: señal presente, estado preparado)."""
    state = _state(fx)
    active = dict(state.get("active_packet") or {})
    active["status"] = "prepared"
    state["active_packet"] = active
    fx.write_state(state)


def _dispatch_record_path(fx: _RecoveryProject,
                          attempt_id: str = "attempt-demo-700-001") -> Path:
    """El archivo REAL de despacho que `fx.dispatch()` publica."""
    return (fx.root / ".cdad" / "executions" / fx.execution_id / "dispatches"
            / f"{attempt_id}.json")


def _continuity_dir(fx: _RecoveryProject) -> Path:
    return fx.root / ".cdad" / "executions" / fx.execution_id / "continuity"


def _continuity_snapshot(fx: _RecoveryProject) -> dict[str, bytes]:
    base = _continuity_dir(fx)
    if not base.is_dir():
        return {}
    return {path.relative_to(fx.root).as_posix(): path.read_bytes()
            for path in sorted(base.rglob("*")) if path.is_file()}


def _head_doc(fx: _RecoveryProject) -> dict:
    path = _continuity_dir(fx) / "head.json"
    assert path.is_file(), f"fixture: falta la cabeza de continuidad {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _body_doc(fx: _RecoveryProject, sha: str) -> dict:
    path = _continuity_dir(fx) / "bodies" / f"{sha}.json"
    assert path.is_file(), f"fixture: falta el cuerpo {sha[:12]}… en {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _bodies_of(fx: _RecoveryProject) -> set[str]:
    base = _continuity_dir(fx) / "bodies"
    if not base.is_dir():
        return set()
    return {path.name for path in base.glob("*.json")}


def _write_evidence_file(fx: _RecoveryProject) -> None:
    (fx.root / EVIDENCE_REL).write_bytes(EVIDENCE_BYTES)


def _packet_files(fx: _RecoveryProject) -> dict[str, bytes]:
    base = fx.packet_dir()
    return {path.relative_to(fx.root).as_posix(): path.read_bytes()
            for path in sorted(base.rglob("*")) if path.is_file()}


def _packets_snapshot(fx: _RecoveryProject) -> dict[str, bytes]:
    base = fx.root / ".cdad" / "packets"
    if not base.is_dir():
        return {}
    return {path.relative_to(fx.root).as_posix(): path.read_bytes()
            for path in sorted(base.rglob("*")) if path.is_file()}


def _manifest_doc(fx: _RecoveryProject) -> dict:
    path = fx.root / MANIFEST_REL
    assert path.is_file(), f"fixture: falta el manifiesto {MANIFEST_REL}"
    return json.loads(path.read_text(encoding="utf-8"))


def _write_manifest_doc(fx: _RecoveryProject, manifest: dict) -> None:
    (fx.root / MANIFEST_REL).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")


def _derived_snapshot(fx: _RecoveryProject) -> dict[str, bytes]:
    base = fx.root / DERIVED_DIR_REL
    if not base.is_dir():
        return {}
    return {path.name: path.read_bytes()
            for path in sorted(base.iterdir()) if path.is_file()}


def _derived_mtimes(fx: _RecoveryProject) -> dict[str, int]:
    base = fx.root / DERIVED_DIR_REL
    if not base.is_dir():
        return {}
    return {path.name: path.stat().st_mtime_ns
            for path in sorted(base.iterdir()) if path.is_file()}


def _model_line(path: Path) -> list[str]:
    """Las líneas `model:` del frontmatter del agente publicado (I6)."""
    parts = path.read_text(encoding="utf-8").split("---", 2)
    assert len(parts) == 3, f"fixture: {path.name} tiene frontmatter delimitado"
    return [line.strip() for line in parts[1].splitlines()
            if line.strip().startswith("model:")]


def _changed_keys(before: dict, after: dict) -> list[str]:
    return sorted(key for key in set(before) | set(after)
                  if before.get(key) != after.get(key))


def _alternative_verbs(doc: dict) -> list[str]:
    alternatives = (doc.get("next") or {}).get("alternatives") or []
    return [item.get("verb") for item in alternatives
            if isinstance(item, dict)]


def _view(proc: subprocess.CompletedProcess, label: str) -> dict:
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        f"{label}: la vista `status` debe emitir la proyección (rc=0); "
        f"rc={proc.returncode}: {out[-600:]!r}")
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{label}: stdout de `status` no es un documento JSON válido: "
            f"{proc.stdout[:200]!r}") from exc
    assert isinstance(doc, dict), f"{label}: la vista no es un objeto: {doc!r}"
    return doc


def _installed_status(fx: _RecoveryProject, install: Path
                      ) -> subprocess.CompletedProcess:
    """`status` con el CLI instalado simulado (el verificador real de versión)."""
    cli = install / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
    return fx._run(cli, ["status", "--project-root", str(fx.root)])


def _materialization_record_path(fx: _RecoveryProject) -> Path:
    base = (fx.root / ".cdad" / "runtime" / "materializations"
            / fx.execution_id / fx.packet_id)
    records = sorted(base.glob("*.json")) if base.is_dir() else []
    assert len(records) == 1, (
        f"fixture: la materialización real deja UN registro; hay {records}")
    return records[0]


# ------------------------------------------------- fixtures de republish


class _DriftProject(_RecoveryProject):
    """`_RecoveryProject` cuyo `prepare` deriva agentes desde una instalación
    simulada (precedencia por variable de entorno, PD-12 de 005-005)."""

    def __init__(self, base: Path, *, install: Path,
                 agents_rel: str = ".config/opencode/agents") -> None:
        self.install = install
        self.agents_source = install / agents_rel
        super().__init__(base)

    def env(self) -> dict:
        env = super().env()
        env["CDAD_OPENCODE_AGENTS_DIR"] = str(self.agents_source)
        return env


def _simulated_install(base: Path, name: str, *, version: str,
                       omit: frozenset[str] = frozenset()) -> Path:
    """Instalación simulada: copia de `skills/` + marcador de versión + agentes
    generados del repo copiados sin inspección (fixture, no implementación)."""
    install = base / name
    shutil.copytree(SKILLS_TREE, install / "skills", symlinks=True)
    (install / "version.txt").write_text(version + "\n", encoding="utf-8")
    agents = install / ".config" / "opencode" / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    for source in sorted(AGENTS_TREE.glob("cdad-*.md")):
        if source.name in omit:
            continue
        shutil.copy2(source, agents / source.name)
    return install


def _mutate_source_agent(install: Path, name: str, marker: bytes) -> None:
    path = install / ".config" / "opencode" / "agents" / name
    path.write_bytes(path.read_bytes() + marker)


def _retire_source_agent(install: Path, name: str) -> None:
    """Fixture: la instalación v2 dejó de desplegar un agente administrado."""
    path = install / ".config" / "opencode" / "agents" / name
    assert path.is_file(), f"fixture: la fuente v1 trae {name}"
    path.unlink()


def _with_custom_model(install: Path, name: str, model: str) -> None:
    """Fixture: declara un `model:` personalizado en la fuente instalada."""
    path = install / ".config" / "opencode" / "agents" / name
    parts = path.read_text(encoding="utf-8").split("---", 2)
    assert len(parts) == 3, f"fixture: {name} tiene frontmatter delimitado"
    assert not any(line.strip().startswith("model:")
                   for line in parts[1].splitlines()), (
        f"fixture: {name} no trae modelo en la fuente copiada")
    path.write_text(
        "---" + parts[1] + f"model: {model}\n" + "---" + parts[2],
        encoding="utf-8")


def _real_delivery_trail(base: Path, name: str = "trail-donor"
                         ) -> dict[str, bytes]:
    """Rastro REAL de recepción (bundle + parts + receipt) del productor.

    Los ids del fixture son deterministas, así que el rastro del donante es
    coherente con cualquier proyecto `_RecoveryProject` y se trasplanta tal
    cual (variante construida a partir de artefactos reales del productor).
    """
    donor = _RecoveryProject(base / name)
    evidence = donor.root / "docs" / "donor-evidence.md"
    evidence.write_bytes(b"donor evidence for real trail\n")
    update = donor.base / "donor-update.json"
    update.write_text(json.dumps({
        "packet_id": donor.packet_id, "attempt": 1, "goal": "rastro real",
        "decisions": [{"decision": "donar", "rationale": "fixture"}],
        "uncertainties": [], "next_action": "continuar", "references": [],
        "evidence": [{
            "id": "donor-evidence",
            "reference": {"path": "docs/donor-evidence.md",
                          "sha256": hashlib.sha256(
                              b"donor evidence for real trail\n").hexdigest()},
            "status": "vigente", "reason": "evidencia del donante",
            "antecedent": None,
        }],
    }), encoding="utf-8")
    begun = donor._run(CONTINUITY_CLI, [
        "begin", "--project-root", str(donor.root),
        "--execution-context", str(donor.execution_context_path()),
        "--update", str(update), "--json",
    ])
    assert begun.returncode == 0, (
        f"fixture: begin del donante: {begun.stdout!r} {begun.stderr!r}")
    dispatched = donor.run_packet(
        "prepare", "--project-root", str(donor.root),
        "--record-dispatch", donor.packet_id,
        "--attempt-id", "attempt-donor-001", "--input", str(donor._observation),
        "--continuity-attempt", "1")
    assert dispatched.returncode == 0, (
        f"fixture: despacho del donante: {dispatched.stdout!r} "
        f"{dispatched.stderr!r}")
    descriptor = donor._stage_result()
    received = donor.run_result(
        "receive", "--project-root", str(donor.root),
        "--execution-context", str(donor.execution_context_path()),
        "--packet", str(donor.packet_dir() / "PACKET.md"),
        "--request", str(donor.packet_dir() / "REQUEST.json"),
        "--descriptor", str(descriptor), "--continuity-attempt", "1")
    assert received.returncode == 0, (
        f"fixture: recepción del donante: {received.stdout!r} "
        f"{received.stderr!r}")
    results = donor.receipt_dir()
    return {path.relative_to(results).as_posix(): path.read_bytes()
            for path in sorted(results.rglob("*")) if path.is_file()}


def _transplant_trail(fx: _RecoveryProject, trail: dict[str, bytes],
                      *, without: frozenset[str] = frozenset(),
                      corrupt: str | None = None) -> None:
    base = fx.receipt_dir()
    for rel, blob in sorted(trail.items()):
        if rel in without:
            continue
        target = base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"{broken" if rel == corrupt else blob)


# ------------------------------------------------- fábricas PC-02


def _case_foreign_packet(fx: _RecoveryProject):
    foreign = f"{FEATURE_ID}-test-writer-red-009"
    return (lambda: _withdraw(fx, packet_id=foreign)), re.compile(re.escape(foreign))


def _case_state_identity_mismatch(fx: _RecoveryProject):
    wrong = f"{FEATURE_ID}-test-writer-red-777"
    real = fx.packet_id
    state = _state(fx)
    active = dict(state.get("active_packet") or {})
    active["id"] = wrong
    state["active_packet"] = active
    fx.write_state(state)
    cause = re.compile(f"{re.escape(wrong)}|{re.escape(real)}")
    return (lambda: _withdraw(fx, packet_id=wrong)), cause


def _case_dispatched_state(fx: _RecoveryProject):
    dispatched = fx.dispatch()
    assert dispatched.returncode == 0, (
        f"fixture PC-02: despacho real del paquete: {dispatched.stdout!r} "
        f"{dispatched.stderr!r}")
    return (lambda: _withdraw(fx)), DISPATCH_CAUSE


def _case_failed_state(fx: _RecoveryProject):
    state = _state(fx)
    active = dict(state["active_packet"])
    active["status"] = "failed"
    state["active_packet"] = active
    fx.write_state(state)
    return (lambda: _withdraw(fx)), NOT_PREPARED_CAUSE


def _case_empty_note(fx: _RecoveryProject):
    return (lambda: _withdraw(fx, note="")), re.compile(
        r"(?i)note|motivo|reason|vac[íi]o|empty")


def _case_absent_note(fx: _RecoveryProject):
    return (lambda: _withdraw(fx, note=None)), re.compile(
        r"(?i)note|motivo|reason|requir|obligator|mandatory")


# ------------------------------------------------- fábricas PC-03


def _effect_case_dispatch_registered(fx: _RecoveryProject):
    assert fx.dispatch().returncode == 0, "fixture PC-03: despacho real"
    _restore_prepared(fx)
    return (lambda: _withdraw(fx)), DISPATCH_CAUSE


def _effect_case_dispatch_unreadable(fx: _RecoveryProject):
    assert fx.dispatch().returncode == 0, "fixture PC-03: despacho real"
    _restore_prepared(fx)
    _dispatch_record_path(fx).write_bytes(b"{broken")
    return (lambda: _withdraw(fx)), DISPATCH_CAUSE


def _effect_case_dispatch_identity_absent(fx: _RecoveryProject):
    assert fx.dispatch().returncode == 0, "fixture PC-03: despacho real"
    _restore_prepared(fx)
    path = _dispatch_record_path(fx)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert "packet_id" in record, (
        "fixture: el registro real de despacho declara su identidad")
    record.pop("packet_id")
    path.write_text(
        json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")
    return (lambda: _withdraw(fx)), DISPATCH_CAUSE


def _effect_case_dispatch_identity_mismatch(fx: _RecoveryProject):
    assert fx.dispatch().returncode == 0, "fixture PC-03: despacho real"
    _restore_prepared(fx)
    path = _dispatch_record_path(fx)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert "packet_id" in record, (
        "fixture: el registro real de despacho declara su identidad")
    record["packet_id"] = f"{FEATURE_ID}-test-writer-red-555"
    path.write_text(
        json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")
    return (lambda: _withdraw(fx)), DISPATCH_CAUSE


def _effect_case_result_without_receipt(fx: _RecoveryProject):
    trail = _real_delivery_trail(fx.base, "trail-sin-recibo")
    assert fx.dispatch().returncode == 0, "fixture PC-03: despacho real"
    _restore_prepared(fx)
    _dispatch_record_path(fx).unlink()
    _transplant_trail(fx, trail, without=frozenset({"receipt.json"}))
    return (lambda: _withdraw(fx)), RESULTS_CAUSE


def _effect_case_receipt_unreadable(fx: _RecoveryProject):
    trail = _real_delivery_trail(fx.base, "trail-recibo-ilegible")
    assert fx.dispatch().returncode == 0, "fixture PC-03: despacho real"
    _restore_prepared(fx)
    _dispatch_record_path(fx).unlink()
    _transplant_trail(fx, trail, corrupt="receipt.json")
    return (lambda: _withdraw(fx)), RECEIPT_CAUSE


def _effect_case_materialization_registered(fx: _RecoveryProject):
    # Ruta fiel completa: el `begin` acredita el cierre de la recepción
    # (007-003 §2.3.3/§2.4: sin cadena, `receive --continuity-attempt` se
    # rechaza fail-closed; y sin el flag la recepción también falla cerrada).
    assert _begin(fx, "begin que acredita el cierre").returncode == 0, (
        "fixture PC-03: el `begin` vigente que acredita el cierre de la "
        "recepción (007-003 §2.3.3/§2.4)")
    dispatched = fx.run_packet(
        "prepare", "--project-root", str(fx.root),
        "--record-dispatch", fx.packet_id,
        "--attempt-id", "attempt-materialized-001",
        "--input", str(fx._observation), "--continuity-attempt", "1")
    assert dispatched.returncode == 0, (
        f"fixture PC-03: despacho real: {dispatched.stdout!r} "
        f"{dispatched.stderr!r}")
    descriptor = fx._stage_result()
    received = fx.run_result(
        "receive", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--packet", str(fx.packet_dir() / "PACKET.md"),
        "--request", str(fx.packet_dir() / "REQUEST.json"),
        "--descriptor", str(descriptor), "--continuity-attempt", "1")
    assert received.returncode == 0, (
        f"fixture PC-03: recepción real con cierre acreditado: "
        f"{received.stdout!r} {received.stderr!r}")
    materialized = fx.materialize()
    assert materialized.returncode == 0, (
        f"fixture PC-03: materialización real: {materialized.stdout!r} "
        f"{materialized.stderr!r}")
    _restore_prepared(fx)
    _dispatch_record_path(fx, "attempt-materialized-001").unlink()
    # Aislamiento de la señal (disciplina reanchor PC-R5): del rastro REAL de
    # recepción queda SOLO el registro de materialización — recibo, bundle,
    # partes y copia materializada se retiran para que la causa nombrada por
    # el rechazo sea la materialización y no un archivo de resultado ajeno.
    results = fx.receipt_dir()
    (results / "bundle.json").unlink()
    (results / "receipt.json").unlink()
    shutil.rmtree(results / "parts")
    (fx.root / "docs" / "specs" / FEATURE_ID / "role-report.md").unlink(
        missing_ok=True)
    record = _materialization_record_path(fx)
    assert record.is_file(), (
        f"fixture PC-03: el registro REAL de materialización queda: {record}")
    return (lambda: _withdraw(fx)), MATERIALIZATION_CAUSE


def _effect_case_materialization_unreadable(fx: _RecoveryProject):
    _effect_case_materialization_registered(fx)
    _materialization_record_path(fx).write_bytes(b"{broken")
    return (lambda: _withdraw(fx)), MATERIALIZATION_CAUSE


def _effect_case_disposition_registered(fx: _RecoveryProject):
    assert fx.dispatch().returncode == 0, "fixture PC-03: despacho real"
    disposed = fx.dispose("abandoned")
    assert disposed.returncode == 0, (
        f"fixture PC-03: disposición real: {disposed.stdout!r} "
        f"{disposed.stderr!r}")
    _dispatch_record_path(fx).unlink()
    _restore_prepared(fx)
    return (lambda: _withdraw(fx)), DISPOSITION_CAUSE


def _effect_case_disposition_unverifiable(fx: _RecoveryProject):
    assert fx.dispatch().returncode == 0, "fixture PC-03: despacho real"
    disposed = fx.dispose("abandoned")
    assert disposed.returncode == 0, (
        f"fixture PC-03: disposición real: {disposed.stdout!r} "
        f"{disposed.stderr!r}")
    _dispatch_record_path(fx).unlink()
    state = _state(fx)
    entry = state["stage_history"][-1]
    assert entry.get("transition") == "disposition", (
        "fixture: la última entrada real es la disposición")
    entry["transition_key"] = "0" * 64
    active = dict(state.get("active_packet") or {})
    active["status"] = "prepared"
    state["active_packet"] = active
    fx.write_state(state)
    return (lambda: _withdraw(fx)), DISPOSITION_CAUSE


# ------------------------------------------------- fábricas PC-10


def _guard_case_missing_source(fx: _DriftProject):
    fx.agents_source = fx.base / "missing-agents-dir"
    return (lambda: _republish(fx)), re.compile(
        r"(?i)source|fuente|agents|origin|instal")


def _guard_case_policy_illegible(fx: _DriftProject):
    (fx.root / "docs" / "cdad-policy.json").write_bytes(b"{broken")
    return (lambda: _republish(fx)), re.compile(r"(?i)policy|pol[íi]tica")


def _guard_case_policy_mismatch(fx: _DriftProject):
    policy = fx.root / "docs" / "cdad-policy.json"
    policy.write_bytes(policy.read_bytes() + b"\n")
    return (lambda: _republish(fx)), re.compile(
        r"(?i)policy|pol[íi]tica|sha|aceptada|accepted")


def _guard_case_context_unreadable(fx: _DriftProject):
    fx.execution_context_path().write_bytes(b"{broken")
    return (lambda: _republish(fx)), re.compile(
        r"(?i)context|contexto|execution|ejecuci")


def _guard_case_hand_modified_derived(fx: _DriftProject):
    derived = fx.root / DERIVED_DIR_REL / "cdad-scribe.md"
    derived.write_text(
        derived.read_text(encoding="utf-8") + "\n<!-- mano -->\n",
        encoding="utf-8")
    return (lambda: _republish(fx)), re.compile(
        r"(?i)modified|modificad|hand|mano|local|diverg|edited")


def _guard_case_destination_read_only(fx: _DriftProject):
    (fx.install / "version.txt").write_text(VERSION_V2 + "\n", encoding="utf-8")
    _mutate_source_agent(fx.install, "cdad-architect.md",
                         b"<!-- fixture v2 source -->\n")
    (fx.root / DERIVED_DIR_REL).chmod(0o555)

    def call() -> subprocess.CompletedProcess:
        proc = _republish(fx)
        (fx.root / DERIVED_DIR_REL).chmod(0o755)  # árbol limpio para cleanup
        return proc

    return call, re.compile(
        r"(?i)writ|escrib|denied|permiso|read-only|permission")


def _guard_case_second_destination_directory(fx: _DriftProject):
    """Transaccional (review-002): DOS agentes derivados a actualizar; el
    destino del SEGUNDO (orden alfabético) se vuelve un DIRECTORIO — condición
    real de filesystem que hace fallar el reemplazo DESPUÉS del primer
    reemplazo. El rechazo debe dejar TODOS los destinos byte-idénticos al
    estado anterior (sin conjunto parcial de derivados)."""
    _mutate_source_agent(fx.install, "cdad-architect.md",
                         b"<!-- fixture v2 source architect -->\n")
    _mutate_source_agent(fx.install, "cdad-implementer.md",
                         b"<!-- fixture v2 source implementer -->\n")
    second = fx.root / DERIVED_DIR_REL / "cdad-implementer.md"
    assert second.is_file(), (
        "fixture: el destino del segundo derivado a actualizar existe")
    second.unlink()
    second.mkdir()
    return (lambda: _republish(fx)), re.compile(r"(?i)implementer")


def _guard_case_manifest_destination_blocked(fx: _DriftProject):
    """Transaccional (review-002): la ESCRITURA del manifiesto falla (su
    `.tmp` está bloqueado por un directorio — condición real de fs, el
    manifiesto previo sigue legible) → rc≠0 y todos los destinos, incluido el
    manifiesto, byte-idénticos (sin conjunto parcial de derivados)."""
    _mutate_source_agent(fx.install, "cdad-architect.md",
                         b"<!-- fixture v2 source architect (manifest) -->\n")
    blocked = fx.root / (MANIFEST_REL + ".tmp")
    blocked.parent.mkdir(parents=True, exist_ok=True)
    blocked.mkdir()
    return (lambda: _republish(fx)), re.compile(
        r"(?i)manifest|cdad-derived")


# ------------------------------------------------- órdenes AJ4 (PC-12)


def _run_order_republish_first(fx: _DriftProject) -> None:
    """Ruta AJ4 1: republicar (sin retiro) y LUEGO retirar."""
    republished = _republish(fx)
    assert republished.returncode == 0, (
        "PC-12/AJ4 (republicar primero): la republicación funciona SIN "
        f"retirar: {republished.stdout!r} {republished.stderr!r}")
    doc = _view(_installed_status(fx, fx.install),
                "PC-12/AJ4 republicar primero")
    assert doc["packet"]["status"] == "prepared", (
        "PC-12/AJ4 (republicar primero): el paquete sigue preparado tras "
        f"republicar (la ruta 1 no retira): {doc['packet']!r}")
    withdrawn = _withdraw(fx)
    assert withdrawn.returncode == 0, (
        f"PC-12/AJ4 (republicar primero): el retiro posterior: "
        f"{withdrawn.stdout!r} {withdrawn.stderr!r}")


def _run_order_withdraw_first(fx: _DriftProject) -> None:
    """Ruta AJ4 2: retirar con DRIFT presente y LUEGO republicar."""
    withdrawn = _withdraw(fx)
    assert withdrawn.returncode == 0, (
        "PC-12/AJ4 (retirar primero): el retiro funciona durante DRIFT "
        f"(no exige coherencia de agentes): {withdrawn.stdout!r} "
        f"{withdrawn.stderr!r}")
    republished = _republish(fx)
    assert republished.returncode == 0, (
        "PC-12/AJ4 (retirar primero): republicar admite el paquete terminal "
        f"y no opera sobre él: {republished.stdout!r} {republished.stderr!r}")


# ================================================================ PC-01


def test_withdraw_prepared_packet_preserves_artifacts_and_frees_prepare(
        tmp_path: Path) -> None:
    """PC-01: el retiro válido tiene éxito, conserva byte a byte el paquete y
    su contexto, registra `withdraw`/`withdrawn` con clave verificable, deja
    el binding en `failed` cambiando SOLO binding/entrada/last_updated, y
    habilita un `prepare` nuevo sin reemplazo."""
    fx = _RecoveryProject(tmp_path)
    _assert_withdraw_surface(fx)
    packet_before = _packet_files(fx)
    context_before = fx.execution_context_path().read_bytes()
    state_before = _state(fx)
    history_before = entries(state_before)

    proc = _withdraw(fx)
    assert proc.returncode == 0, (
        f"PC-01: el retiro válido debe tener éxito (rc=0); "
        f"{proc.stdout!r} {proc.stderr!r}")

    assert _packet_files(fx) == packet_before, (
        "PC-01/I2: REQUEST.json, PACKET.md y demás archivos del paquete "
        "permanecen byte a byte")
    assert fx.execution_context_path().read_bytes() == context_before, (
        "PC-01/I2: el contexto de ejecución permanece byte a byte")

    state_after = _state(fx)
    active_before = state_before.get("active_packet") or {}
    active_after = state_after.get("active_packet") or {}
    history_after = entries(state_after)
    assert len(history_after) == len(history_before) + 1, (
        "PC-01: `stage_history` agrega exactamente una entrada; antes "
        f"{len(history_before)}, después {len(history_after)}")
    expected_state = {
        **state_before,
        "active_packet": {**active_before, "status": "failed"},
        "stage_history": history_after,
        "last_updated": state_after.get("last_updated"),
    }
    assert state_after == expected_state, (
        "PC-01: sólo cambian `active_packet.status`, la entrada añadida y "
        f"`last_updated`; claves divergentes: "
        f"{_changed_keys(state_before, state_after)}")
    assert active_after.get("id") == fx.packet_id and active_after.get(
        "status") == "failed", (
        f"PC-01: el binding queda `failed` con el mismo id: {active_after!r}")

    entry = history_after[-1]
    assert entry.get("transition") == "withdraw", (
        f"PC-01: la entrada declara `transition: withdraw`: {entry!r}")
    assert entry.get("resolution") == "withdrawn", (
        f"PC-01: resolución implícita `withdrawn`: {entry!r}")
    assert entry.get("packet_id") == fx.packet_id, (
        f"PC-01: la entrada cita el paquete retirado: {entry!r}")
    assert entry.get("feature") == FEATURE_ID, (
        f"PC-01: la entrada cita la feature: {entry!r}")
    assert fx.execution_id in json.dumps(entry, ensure_ascii=False), (
        f"PC-01: la entrada menciona la ejecución (identidad habitual): "
        f"{entry!r}")
    assert WITHDRAW_NOTE in json.dumps(entry, ensure_ascii=False), (
        "PC-01: la entrada lleva el motivo no vacío: "
        f"{json.dumps(entry, ensure_ascii=False)[:400]!r}")
    payload = entry.get("transition_key_payload")
    assert isinstance(payload, dict), (
        "PC-01: la entrada lleva la identidad y clave verificable habituales "
        f"(`transition_key_payload`): {entry!r}")
    assert canonical_digest(payload) == entry.get("transition_key"), (
        "PC-01: la clave de la entrada se recomputa desde su payload "
        f"canónico: {entry!r}")

    freed = fx.prepare()
    assert freed.returncode == 0, (
        "PC-01: tras el retiro un `prepare` nuevo sin reemplazo debe "
        f"publicar el paquete siguiente (rc=0): {freed.stdout!r} "
        f"{freed.stderr!r}")
    active_new = (_state(fx).get("active_packet") or {})
    assert active_new.get("id") != fx.packet_id, (
        f"PC-01: el prepare nuevo publica OTRO paquete: {active_new!r}")
    assert active_new.get("status") == "prepared", (
        f"PC-01: el paquete nuevo queda `prepared`: {active_new!r}")


# ================================================================ PC-02


@pytest.mark.parametrize(
    "attempt",
    [_case_foreign_packet, _case_state_identity_mismatch,
     _case_dispatched_state, _case_failed_state, _case_empty_note,
     _case_absent_note],
    ids=["foreign-packet", "state-identity-mismatch", "dispatched-state",
         "failed-state", "empty-note", "absent-note"])
def test_withdraw_requires_reason_and_matching_active_prepared_packet(
        tmp_path: Path, attempt) -> None:
    """PC-02: motivo ausente/vacío, identidad discordante, otro paquete o
    estado no preparado → rechazo (rc=2) sin cambios, nombrando la causa."""
    fx = _RecoveryProject(tmp_path / attempt.__name__.replace("_case_", ""))
    _assert_withdraw_surface(fx)
    call, cause = attempt(fx)
    before = fx.tree()
    proc = call()
    assert proc.returncode == 2, (
        f"PC-02 ({attempt.__name__}): rechazo de dominio rc=2; "
        f"rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    assert fx.tree() == before, (
        f"PC-02 ({attempt.__name__}): el rechazo no modifica ningún archivo "
        "persistente; cambios: "
        f"{sorted(set(before) ^ set(fx.tree()))}")
    text = proc.stdout + proc.stderr
    assert cause.search(text), (
        f"PC-02 ({attempt.__name__}): el rechazo nombra fuente y causa "
        f"(patrón {cause.pattern!r}); visto: {text!r}")


# ================================================================ PC-03


@pytest.mark.parametrize(
    "effect",
    [_effect_case_dispatch_registered, _effect_case_dispatch_unreadable,
     _effect_case_dispatch_identity_absent,
     _effect_case_dispatch_identity_mismatch,
     _effect_case_result_without_receipt, _effect_case_receipt_unreadable,
     _effect_case_materialization_registered,
     _effect_case_materialization_unreadable,
     _effect_case_disposition_registered, _effect_case_disposition_unverifiable],
    ids=["dispatch-registered", "dispatch-unreadable",
         "dispatch-identity-absent", "dispatch-identity-mismatch",
         "result-without-receipt", "receipt-unreadable",
         "materialization-registered", "materialization-unreadable",
         "disposition-registered", "disposition-unverifiable"])
def test_withdraw_rejects_effects_and_inconclusive_signals(
        tmp_path: Path, effect) -> None:
    """PC-03: toda señal positiva o inconclusa (despacho, resultado,
    materialización, disposición; presente, ilegible o sin identidad
    verificable) impide el retiro: rc=2, fuente/causa nombrada y árbol
    persistente intacto (I3: inconcluso nunca se interpreta como ausente)."""
    fx = _RecoveryProject(
        tmp_path / effect.__name__.replace("_effect_case_", ""))
    _assert_withdraw_surface(fx)
    call, cause = effect(fx)
    before = fx.tree()
    proc = call()
    assert proc.returncode == 2, (
        f"PC-03 ({effect.__name__}): señal que impide el retiro → rc=2; "
        f"rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    assert fx.tree() == before, (
        f"PC-03 ({effect.__name__}): el rechazo conserva el árbol byte a "
        "byte; cambios: " + str(sorted(set(before) ^ set(fx.tree()))))
    text = proc.stdout + proc.stderr
    assert cause.search(text), (
        f"PC-03 ({effect.__name__}): el rechazo nombra la fuente/causa "
        f"(patrón {cause.pattern!r}); visto: {text!r}")


# ================================================================ PC-04


def test_withdraw_closes_current_begin_without_fabricating_delivery(
        tmp_path: Path) -> None:
    """PC-04 (+AJ2): con `begin` vigente del paquete, el retiro anexa un
    checkpoint enlazado con decisión de retiro (cita clave y motivo), conserva
    `evidence` con su clasificación y antecedentes, declara la siguiente
    acción, y NO crea recibo ni `receipt_checkpoint` ni begin nuevo."""
    fx = _RecoveryProject(tmp_path)
    _assert_withdraw_surface(fx)
    _write_evidence_file(fx)
    begun = _begin(fx, "begin del retiro", evidence=BEGIN_EVIDENCE)
    assert begun.returncode == 0, (
        f"fixture PC-04: begin público con evidencia: {begun.stdout!r} "
        f"{begun.stderr!r}")
    begin_sha = json.loads(begun.stdout)["body_sha256"]
    begin_body = _body_doc(fx, begin_sha)
    substituted = [
        {
            "id": "withdraw-evidence",
            "reference": dict(BEGIN_EVIDENCE[0]["reference"]),
            "status": "invalidada",
            "reason": "la referencia cambió después del begin (fixture AJ2)",
            "antecedent": {"body_sha256": begin_sha,
                           "evidence_id": "withdraw-evidence"},
        },
        {
            "id": "withdraw-evidence-2",
            "reference": {"path": EVIDENCE_REL,
                          "sha256": hashlib.sha256(
                              EVIDENCE_BYTES + b"reemplazo\n").hexdigest()},
            "status": "vigente",
            "reason": "sustitución con antecedente (fixture AJ2)",
            "antecedent": {"body_sha256": begin_sha,
                           "evidence_id": "withdraw-evidence"},
        },
    ]
    (fx.root / EVIDENCE_REL).write_bytes(EVIDENCE_BYTES + b"reemplazo\n")
    update = fx.base / "checkpoint-update.json"
    update.write_text(json.dumps({
        "packet_id": fx.packet_id, "attempt": 1, "goal": "checkpoint previo",
        "decisions": [{"decision": "avance", "rationale": "fixture"}],
        "uncertainties": [], "next_action": "continuar el encargo",
        "references": [], "evidence": substituted,
    }), encoding="utf-8")
    checked = fx._run(CONTINUITY_CLI, [
        "checkpoint", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--update", str(update), "--json",
    ])
    assert checked.returncode == 0, (
        f"fixture PC-04: checkpoint con sustitución de evidencia: "
        f"{checked.stdout!r} {checked.stderr!r}")
    current = _head_doc(fx)
    current_sha = current["body_sha256"]
    current_body = _body_doc(fx, current_sha)
    assert current_body.get("evidence") == substituted, (
        "fixture PC-04: la cadena lleva evidencia clasificada y con "
        f"antecedentes: {current_body.get('evidence')!r}")

    proc = _withdraw(fx)
    assert proc.returncode == 0, (
        f"PC-04: retiro con begin vigente (rc=0): {proc.stdout!r} "
        f"{proc.stderr!r}")

    head = _head_doc(fx)
    withdraw_sha = head["body_sha256"]
    assert withdraw_sha != current_sha, (
        "PC-04: el retiro publica un checkpoint nuevo")
    assert head.get("seq") == current.get("seq") + 1, (
        f"PC-04/AJ2: la secuencia avanza normal: {head!r}")
    withdraw_body = _body_doc(fx, withdraw_sha)
    assert withdraw_body.get("record") == "checkpoint", (
        "PC-04: el retiro anexa `record: checkpoint`, no un begin ni un "
        f"cierre de recibo: {withdraw_body!r}")
    prev = withdraw_body.get("prev")
    assert isinstance(prev, dict) and prev.get(
        "checkpoint_sha256") == current_sha, (
        "PC-04: el checkpoint conserva el vínculo `prev` hacia la cabeza "
        f"anterior ({current_sha[:12]}…): {prev!r}")
    assert withdraw_body.get("attempt") == begin_body.get("attempt"), (
        "PC-04/AJ2: el checkpoint conserva el intento del contexto previo")
    assert withdraw_body.get("packet_id") == fx.packet_id, (
        "PC-04/AJ2: el checkpoint conserva el paquete del contexto previo")
    assert withdraw_body.get("evidence") == substituted, (
        "PC-04/AJ2: `evidence`, su clasificación y antecedentes se conservan "
        "intactos; visto: "
        f"{json.dumps(withdraw_body.get('evidence'), ensure_ascii=False)[:400]!r}")
    assert _bodies_of(fx) == {f"{begin_sha}.json", f"{current_sha}.json",
                              f"{withdraw_sha}.json"}, (
        f"PC-04: la cadena agrega SOLO el checkpoint de retiro; cuerpos: "
        f"{sorted(_bodies_of(fx))}")
    entry = entries(_state(fx))[-1]
    transition_key = entry.get("transition_key")
    assert isinstance(transition_key, str) and transition_key, (
        "PC-04: el retiro registra su clave de transición: "
        f"{json.dumps(entry, ensure_ascii=False)[:300]!r}")
    assert transition_key in json.dumps(withdraw_body, ensure_ascii=False), (
        "PC-04: la decisión de retiro del checkpoint cita la clave de "
        f"transición ({transition_key[:12]}…): "
        f"{json.dumps(withdraw_body.get('decisions'), ensure_ascii=False)[:400]!r}")
    assert WITHDRAW_NOTE in json.dumps(
        withdraw_body.get("decisions", []), ensure_ascii=False), (
        "PC-04: la decisión de retiro cita el motivo: "
        f"{json.dumps(withdraw_body.get('decisions'), ensure_ascii=False)[:400]!r}")
    assert withdraw_body.get("next_action") != begin_body.get("next_action"), (
        "PC-04: `next_action` declara el estado nuevo del encargo, no el "
        f"anterior: {withdraw_body.get('next_action')!r}")
    assert set(withdraw_body).isdisjoint(
        {"receipt_checkpoint", "receipt", "receipt_sha256"}), (
        "PC-04: no hubo entrega → el checkpoint no crea recibo; claves: "
        f"{sorted(withdraw_body)}")
    assert not fx.receipt_path().exists(), (
        "PC-04: no se crea recibo durable en el retiro")

    resumed = fx._run(CONTINUITY_CLI, [
        "resume", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()), "--json",
    ])
    assert resumed.returncode == 0, (
        "PC-04: el verificador canónico de continuidad proyecta la cadena "
        f"íntegra (rc=0): {resumed.stdout!r} {resumed.stderr!r}")
    doc = json.loads(resumed.stdout)
    projection = doc.get("projection") or {}
    assert projection.get("evidence") == substituted, (
        "PC-04: `resume` muestra la evidencia conservada del retiro: "
        f"{json.dumps(projection.get('evidence'), ensure_ascii=False)[:400]!r}")
    assert projection.get("next_action") == withdraw_body.get("next_action"), (
        f"PC-04: `resume` muestra la siguiente acción del retiro: "
        f"{projection.get('next_action')!r}")
    assert WITHDRAW_NOTE in json.dumps(
        projection.get("decisions", []), ensure_ascii=False), (
        f"PC-04: `resume` muestra la decisión de retiro: "
        f"{json.dumps(projection.get('decisions'), ensure_ascii=False)[:400]!r}")

    refused = fx.dispatch()
    assert refused.returncode != 0, (
        f"PC-04: el paquete retirado ya no se despacha: {refused.stdout!r} "
        f"{refused.stderr!r}")
    assert fx.dispatch_files() == [], (
        "PC-04: el despacho del paquete retirado queda sin registro: "
        f"{fx.dispatch_files()}")


# ================================================================ PC-05


def _continuity_case_absent_head(fx: _RecoveryProject):
    execution_before = _state(fx).get("execution")

    def follow(fx: _RecoveryProject,
               proc: subprocess.CompletedProcess) -> None:
        assert not _continuity_dir(fx).exists(), (
            "PC-05: sin cabeza el retiro NO crea continuidad ficticia; "
            f"existe {_continuity_dir(fx)}")
        state_after = _state(fx)
        entry = entries(state_after)[-1]
        assert entry.get("transition") == "withdraw" and entry.get(
            "resolution") == "withdrawn", (
            "PC-05: sin cabeza el historial igual registra el retiro: "
            f"{entry!r}")
        assert (state_after.get("active_packet") or {}).get(
            "status") == "failed", "PC-05: sin cabeza el binding queda `failed`"
        assert state_after.get("execution") == execution_before, (
            "PC-05: la ejecución vinculada no cambia")

    return (lambda: _withdraw(fx)), 0, follow


def _continuity_case_foreign_head(fx: _RecoveryProject):
    assert _begin(fx, "cabeza del paquete A").returncode == 0, (
        "fixture PC-05: begin del paquete A")
    first = _withdraw(fx)
    assert first.returncode == 0, (
        f"fixture PC-05: retiro del paquete A (su cabeza propia): "
        f"{first.stdout!r} {first.stderr!r}")
    prepared_b = fx.prepare()
    assert prepared_b.returncode == 0, (
        f"fixture PC-05: paquete B tras retirar A: {prepared_b.stdout!r} "
        f"{prepared_b.stderr!r}")
    packet_b = (_state(fx).get("active_packet") or {}).get("id")
    assert isinstance(packet_b, str) and packet_b != fx.packet_id, (
        f"fixture PC-05: paquete B distinto: {packet_b!r}")
    head_before = (_continuity_dir(fx) / "head.json").read_bytes()
    bodies_before = _bodies_of(fx)

    def follow(fx: _RecoveryProject,
               proc: subprocess.CompletedProcess) -> None:
        assert (_continuity_dir(fx) / "head.json").read_bytes() == head_before, (
            "PC-05: la cabeza vigente de OTRO paquete permanece byte a byte")
        assert _bodies_of(fx) == bodies_before, (
            "PC-05: no se agregan cuerpos a la cadena ajena")
        entry = entries(_state(fx))[-1]
        assert entry.get("transition") == "withdraw" and entry.get(
            "packet_id") == packet_b, (
            "PC-05: el historial registra el retiro del paquete B: {entry!r}")

    return (lambda: _withdraw(fx, packet_id=packet_b)), 0, follow


def _continuity_case_unreadable_head(fx: _RecoveryProject):
    assert _begin(fx, "cabeza a corromper").returncode == 0, (
        "fixture PC-05: begin para la cadena ilegible")
    head_path = _continuity_dir(fx) / "head.json"
    assert head_path.is_file(), "fixture PC-05: cabeza existe"
    head_path.write_bytes(b"{broken")
    before = fx.tree()

    def follow(fx: _RecoveryProject,
               proc: subprocess.CompletedProcess) -> None:
        assert fx.tree() == before, (
            "PC-05: cabeza ilegible → rechazo sin cambios")

    return (lambda: _withdraw(fx)), 2, follow


def _continuity_case_incoherent_head(fx: _RecoveryProject):
    assert _begin(fx, "cabeza incoherente").returncode == 0, (
        "fixture PC-05: begin para la cabeza incoherente")
    head_path = _continuity_dir(fx) / "head.json"
    head = json.loads(head_path.read_text(encoding="utf-8"))
    head["body_sha256"] = "f" * 64
    head_path.write_text(json.dumps(head, sort_keys=True) + "\n",
                         encoding="utf-8")
    before = fx.tree()

    def follow(fx: _RecoveryProject,
               proc: subprocess.CompletedProcess) -> None:
        assert fx.tree() == before, (
            "PC-05: cabeza incoherente → rechazo sin cambios (no se presume "
            "que pertenece a otro paquete)")

    return (lambda: _withdraw(fx)), 2, follow


@pytest.mark.parametrize(
    "variant",
    [_continuity_case_absent_head, _continuity_case_foreign_head,
     _continuity_case_unreadable_head, _continuity_case_incoherent_head],
    ids=["absent-head", "foreign-head", "unreadable-head", "incoherent-head"])
def test_withdraw_handles_absent_foreign_and_invalid_continuity(
        tmp_path: Path, variant) -> None:
    """PC-05: sin cabeza no se fabrica continuidad; la cabeza vigente de otro
    paquete permanece idéntica; una cadena ilegible/incoherente bloquea el
    retiro sin cambios."""
    fx = _RecoveryProject(tmp_path / variant.__name__.replace(
        "_continuity_case_", ""))
    _assert_withdraw_surface(fx)
    call, expected_rc, follow = variant(fx)
    proc = call()
    assert proc.returncode == expected_rc, (
        f"PC-05 ({variant.__name__}): rc esperado {expected_rc}; "
        f"rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    follow(fx, proc)


# ================================================================ PC-06


def test_withdraw_is_idempotent_and_rejects_conflicting_repetition(
        tmp_path: Path) -> None:
    """PC-06: repetir el retiro con el MISMO motivo → éxito sin escrituras ni
    nueva entrada; con un motivo DISTINTO → conflicto (rc=1, clase de
    007-003), sin cambios."""
    fx = _RecoveryProject(tmp_path)
    _assert_withdraw_surface(fx)
    first = _withdraw(fx)
    assert first.returncode == 0, (
        f"PC-06 fixture: primer retiro (rc=0): {first.stdout!r} "
        f"{first.stderr!r}")
    settled = fx.tree()
    history_len = len(entries(_state(fx)))

    replay = _withdraw(fx)
    assert replay.returncode == 0, (
        f"PC-06: la repetición idéntica es éxito (rc=0): {replay.stdout!r} "
        f"{replay.stderr!r}")
    assert fx.tree() == settled, (
        "PC-06/I4: la repetición idéntica no cambia bytes ni inventario")
    assert len(entries(_state(fx))) == history_len, (
        "PC-06/I4: la repetición idéntica no agrega entrada en "
        f"`stage_history`; hay {len(entries(_state(fx)))} entradas")

    conflicting = _withdraw(fx, note=OTHER_NOTE)
    assert conflicting.returncode == 1, (
        "PC-06: un motivo distinto para un retiro ya registrado es CONFLICTO "
        f"(rc=1, clase 007-003); rc={conflicting.returncode}: "
        f"{conflicting.stdout!r} {conflicting.stderr!r}")
    assert fx.tree() == settled, (
        "PC-06: el conflicto no modifica ningún archivo persistente")


# ================================================================ PC-07


@pytest.mark.parametrize("flag_value", FOREIGN_FLAGS,
                         ids=[flag for flag, _value in FOREIGN_FLAGS])
def test_withdraw_rejects_unrelated_transition_flags(
        tmp_path: Path, flag_value: tuple[str, str | None]) -> None:
    """PC-07: los campos ajenos enumerados en la interfaz del retiro no son
    ignorados: cada uno produce rechazo (rc=2) sin cambios."""
    flag, value = flag_value
    fx = _RecoveryProject(tmp_path / flag.lstrip("-").replace("-", "_"))
    _assert_withdraw_surface(fx)
    before = fx.tree()
    proc = _withdraw_with_flag(fx, flag, value)
    assert proc.returncode == 2, (
        f"PC-07: `{flag}` ajeno debe rechazar el retiro (rc=2); "
        f"rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    assert fx.tree() == before, (
        f"PC-07: `{flag}` ajeno rechaza sin cambios; cambios: "
        f"{sorted(set(before) ^ set(fx.tree()))}")
    assert flag in (proc.stdout + proc.stderr), (
        f"PC-07: el rechazo nombra la opción ajena `{flag}`; "
        f"visto: {(proc.stdout + proc.stderr)!r}")


# ================================================================ PC-08


def test_republish_agents_repairs_project_drift_without_cycle_changes(
        tmp_path: Path) -> None:
    """PC-08 (+cierre de PC-10): con paquete activo y DRIFT exclusivo de
    `project`, `republish-agents` republica derivados y manifiesto desde la
    fuente instalada, retira el nombre administrado obsoleto, conserva el
    archivo ajeno, y NO cambia estado, paquetes, política ni continuidad; el
    verificador deja de informar DRIFT de proyecto."""
    install = _simulated_install(tmp_path, "install", version=VERSION_V1)
    fx = _DriftProject(tmp_path / "proj-base", install=install)
    foreign = fx.root / DERIVED_DIR_REL / FOREIGN_AGENT
    foreign.write_bytes(b"# agente ajeno del proyecto (fixture)\n")
    assert foreign.is_file(), "fixture: archivo ajeno preexistente"

    # DRIFT exclusivo de project: la instalación sube de versión in situ.
    (install / "version.txt").write_text(VERSION_V2 + "\n", encoding="utf-8")
    _mutate_source_agent(install, "cdad-orchestrator.md",
                         b"<!-- fixture v2 source -->\n")
    _retire_source_agent(install, "cdad-scribe-odoo.md")
    doc = _view(_installed_status(fx, install), "PC-08 fixture")
    assert doc["version"]["verdict"] == "DRIFT", (
        "fixture PC-08: la instalación v2 debe reportar DRIFT; "
        f"visto {doc['version']!r}")
    assert doc["version"].get("divergent_legs") == ["project"], (
        "fixture PC-08: la única pata divergente debe ser `project`; "
        f"visto {doc['version'].get('divergent_legs')!r}")

    state_before = fx.state_bytes()
    policy_before = (fx.root / "docs" / "cdad-policy.json").read_bytes()
    packets_before = _packets_snapshot(fx)
    continuity_before = _continuity_snapshot(fx)

    _assert_republish_surface(fx)
    proc = _republish(fx)
    assert proc.returncode == 0, (
        f"PC-08: `republish-agents` debe publicar los derivados (rc=0): "
        f"{proc.stdout!r} {proc.stderr!r}")

    orchestrator = fx.root / DERIVED_DIR_REL / "cdad-orchestrator.md"
    assert "fixture v2 source" in orchestrator.read_text(encoding="utf-8"), (
        "PC-08: el derivado se re-deriva de la fuente instalada v2")
    manifest = _manifest_doc(fx)
    assert manifest.get("source_version") == VERSION_V2, (
        "PC-08: el manifiesto registra la versión instalada v2; "
        f"visto {manifest.get('source_version')!r}")
    assert manifest.get("source_dir") == str(fx.agents_source), (
        "PC-08: el manifiesto apunta a la fuente resuelta; "
        f"visto {manifest.get('source_dir')!r}")
    derived_after = _derived_snapshot(fx)
    assert "cdad-scribe-odoo.md" not in derived_after, (
        "PC-10: el nombre administrado obsoleto se retira; publicados: "
        f"{sorted(derived_after)}")
    assert foreign.read_bytes() == b"# agente ajeno del proyecto (fixture)\n", (
        "PC-10/I2: el archivo ajeno se conserva byte a byte")

    assert fx.state_bytes() == state_before, (
        "PC-08/I5: el estado del ciclo queda byte a byte idéntico")
    assert (fx.root / "docs" / "cdad-policy.json").read_bytes() == policy_before, (
        "PC-08/I5: la política queda byte a byte idéntica")
    assert _packets_snapshot(fx) == packets_before, (
        "PC-08/I5: los paquetes quedan byte a byte idénticos")
    assert _continuity_snapshot(fx) == continuity_before, (
        "PC-08/I5: la continuidad queda byte a byte idéntica")

    doc = _view(_installed_status(fx, install), "PC-08 verificación")
    assert doc["version"]["verdict"] == "COHERENT", (
        "PC-08: con las otras patas coherentes, el verificador deja de "
        f"informar DRIFT de proyecto tras republicar: {doc['version']!r}")


# ================================================================ PC-09


def test_republish_agents_inherits_installed_model_and_is_idempotent(
        tmp_path: Path) -> None:
    """PC-09: el `model:` instalado se conserva literalmente (y su ausencia
    permanece ausente) tras republicar; una segunda ejecución no reescribe
    archivos (bytes ya coincidentes → éxito sin reescritura)."""
    install = _simulated_install(tmp_path, "install", version=VERSION_V1)
    _with_custom_model(install, "cdad-test-writer.md", "my-custom-model-x9")
    fx = _DriftProject(tmp_path / "proj-base", install=install)
    writer_published = fx.root / DERIVED_DIR_REL / "cdad-test-writer.md"
    orchestrator_published = fx.root / DERIVED_DIR_REL / "cdad-orchestrator.md"
    assert writer_published.is_file() and orchestrator_published.is_file(), (
        "fixture PC-09: los derivados del prepare inicial existen")

    (install / "version.txt").write_text(VERSION_V2 + "\n", encoding="utf-8")
    _mutate_source_agent(install, "cdad-test-writer.md",
                         b"<!-- fixture v2 source (model unchanged) -->\n")
    _assert_republish_surface(fx)
    proc = _republish(fx)
    assert proc.returncode == 0, (
        f"PC-09: republicar tras la instalación v2 (rc=0): {proc.stdout!r} "
        f"{proc.stderr!r}")
    assert _model_line(writer_published) == ["model: my-custom-model-x9"], (
        "PC-09/I6: el `model:` instalado se conserva LITERALMENTE en el "
        f"derivado; visto {_model_line(writer_published)!r}")
    assert _model_line(orchestrator_published) == [], (
        "PC-09/I6: la AUSENCIA de modelo en la fuente permanece ausente en "
        f"el derivado; visto {_model_line(orchestrator_published)!r}")

    settled = _derived_snapshot(fx)
    mtimes = _derived_mtimes(fx)
    again = _republish(fx)
    assert again.returncode == 0, (
        f"PC-09: la segunda republicación tiene éxito (rc=0): "
        f"{again.stdout!r} {again.stderr!r}")
    assert _derived_snapshot(fx) == settled, (
        "PC-09/I4: la segunda ejecución no cambia bytes")
    assert _derived_mtimes(fx) == mtimes, (
        "PC-09: la segunda ejecución no REESCRIBE destinos coincidentes "
        f"(mtimes intactos); antes: {sorted(mtimes)}; después: "
        f"{sorted(_derived_mtimes(fx))}")


# ================================================================ PC-10


@pytest.mark.parametrize(
    "guard",
    [_guard_case_missing_source, _guard_case_policy_illegible,
     _guard_case_policy_mismatch, _guard_case_context_unreadable,
     _guard_case_hand_modified_derived, _guard_case_destination_read_only,
     _guard_case_second_destination_directory,
     _guard_case_manifest_destination_blocked],
    ids=["missing-source", "policy-illegible", "policy-mismatch",
         "context-unreadable", "hand-modified-derived",
         "destination-read-only", "second-destination-directory",
         "manifest-write-failure"])
def test_republish_agents_preserves_existing_derivation_guards(
        tmp_path: Path, guard) -> None:
    """PC-10: fuente/política/contexto inválidos y derivado modificado a mano
    producen rechazo sin publicación parcial; la condición real de filesystem
    (directorio de derivados de solo lectura) tampoco deja un conjunto
    parcial de derivados."""
    install = _simulated_install(tmp_path / "case", "install",
                                 version=VERSION_V1)
    fx = _DriftProject(tmp_path / "case" / "proj-base", install=install)
    _assert_republish_surface(fx)
    call, cause = guard(fx)
    before = fx.tree()
    proc = call()
    assert proc.returncode != 0, (
        f"PC-10 ({guard.__name__}): la guarda debe rechazar (rc≠0); "
        f"rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    assert fx.tree() == before, (
        f"PC-10 ({guard.__name__}): sin publicación parcial — el árbol queda "
        "byte a byte idéntico; cambios: "
        f"{sorted(set(before) ^ set(fx.tree()))}")
    text = proc.stdout + proc.stderr
    assert cause.search(text), (
        f"PC-10 ({guard.__name__}): el rechazo nombra la fuente/causa "
        f"(patrón {cause.pattern!r}); visto: {text!r}")


# ================================================================ PC-11


def test_status_preserves_prepared_situation_and_exposes_independent_drift_resolution(
        tmp_path: Path) -> None:
    """PC-11: la vista conserva su forma (`packet-prepared` /
    `validate-packet` incluso con begin vigente y DRIFT); SOLO el DRIFT
    exclusivo de `project` ofrece la resolución `republish-agents
    --project-root ROOT`; otras patas no reciben esa promesa; tras retirar, el
    paquete terminal no se propone como pendiente (`execution-active →
    resume`)."""
    install = _simulated_install(tmp_path / "drift", "install",
                                 version=VERSION_V1)
    fx = _DriftProject(tmp_path / "drift" / "proj-base", install=install)
    _write_evidence_file(fx)
    assert _begin(fx, "begin vigente + DRIFT").returncode == 0, (
        "fixture PC-11: begin vigente")
    (install / "version.txt").write_text(VERSION_V2 + "\n", encoding="utf-8")

    doc = _view(_installed_status(fx, install), "PC-11 (DRIFT project)")
    version_block = doc.get("version") or {}
    assert version_block.get("verdict") == "DRIFT", (
        f"fixture PC-11: DRIFT de la pata project; visto {version_block!r}")
    assert version_block.get("divergent_legs") == ["project"], (
        "fixture PC-11: pata exclusiva `project`; "
        f"visto {version_block.get('divergent_legs')!r}")
    assert doc.get("situation") == "packet-prepared", (
        "PC-11: con paquete coherente prepared (begin vigente y DRIFT) la "
        f"situación se conserva: {doc.get('situation')!r}")
    operation = (doc.get("next") or {}).get("operation") or {}
    assert operation.get("verb") == "validate-packet", (
        "PC-11: la operación propuesta se conserva (`validate-packet`): "
        f"{operation!r}")
    resolution = version_block.get("resolution")
    assert isinstance(resolution, str) and re.search(
        r"republish-agents", resolution), (
        "PC-11: con DRIFT exclusivo de `project` la resolución indica "
        f"`republish-agents`; visto {resolution!r}")
    assert "--project-root" in resolution, (
        "PC-11: la resolución nombra la forma completa con `--project-root`: "
        f"{resolution!r}")

    # Control: una pata que NO es project no recibe la promesa.
    other = _simulated_install(tmp_path / "drift", "other-install",
                               version=VERSION_V0)
    foreign_manifest = _manifest_doc(fx)
    foreign_manifest["source_dir"] = str(
        other / ".config" / "opencode" / "agents")
    foreign_manifest["source_version"] = VERSION_V2
    _write_manifest_doc(fx, foreign_manifest)
    doc = _view(_installed_status(fx, install), "PC-11 (DRIFT agents)")
    version_block = doc.get("version") or {}
    assert version_block.get("verdict") == "DRIFT", (
        f"fixture PC-11: DRIFT de la pata agents; visto {version_block!r}")
    assert version_block.get("divergent_legs") != ["project"], (
        "fixture PC-11: la pata divergente NO es project; "
        f"visto {version_block.get('divergent_legs')!r}")
    assert not re.search(r"republish-agents", json.dumps(version_block)), (
        "PC-11: otra divergencia no recibe la promesa de `republish-agents`; "
        f"visto {version_block!r}")

    # Tras retirar: el paquete terminal no se propone como pendiente.
    plain = _RecoveryProject(tmp_path / "retirado")
    _assert_withdraw_surface(plain)
    assert _withdraw(plain).returncode == 0, (
        "fixture PC-11: retiro del paquete preparado (sin cabeza)")
    doc = _view(plain.status(), "PC-11 (tras retiro)")
    assert doc.get("situation") == "execution-active", (
        "PC-11: tras retirar NO se selecciona el paquete terminal como "
        f"pendiente: {doc.get('situation')!r}")
    operation = (doc.get("next") or {}).get("operation") or {}
    assert operation.get("verb") == "resume", (
        "PC-11: con ejecución activa y sin otros pendientes corresponde "
        f"`execution-active → resume`: {operation!r}")
    route = (doc.get("next") or {}).get("route") or ""
    assert plain.packet_id not in route, (
        f"PC-11: la ruta no propone despachar el paquete retirado: {route!r}")


# ================================================================ AJ1


def test_withdraw_and_republish_respect_suspended_units(tmp_path: Path) -> None:
    """AJ1 (PC consolidada 7): con la unidad suspendida (007-007/A2), el
    retiro y su replay NO operan sobre su paquete (rc=1 sin cambios);
    `republish-agents` sin binding activo rechaza; `suspended_units` queda
    íntegro y `status` muestra sólo alternativas elegibles."""
    fx = _RecoveryProject(tmp_path)
    _assert_withdraw_surface(fx)
    suspended = _suspend(fx)
    assert suspended.returncode == 0, (
        "fixture AJ1: la unidad suspendida (borde seguro prepared): "
        f"{suspended.stdout!r} {suspended.stderr!r}")
    registry_before = (_state(fx).get("suspended_units") or {}).copy()
    assert registry_before, "fixture AJ1: la suspensión quedó registrada"
    before = fx.tree()

    refused = _withdraw(fx)
    assert refused.returncode == 1, (
        "AJ1: retirar el paquete de una unidad suspendida es estado "
        f"protegido (rc=1, sin cambios); rc={refused.returncode}: "
        f"{refused.stdout!r} {refused.stderr!r}")
    assert fx.tree() == before, "AJ1: el retiro rechazado no modifica nada"
    assert (_state(fx).get("suspended_units") or {}) == registry_before, (
        "AJ1: `suspended_units` queda íntegro")

    replay = _withdraw(fx)
    assert replay.returncode == 1, (
        "AJ1: la GUARDA precede al replay idempotente → rc=1 sin cambios; "
        f"rc={replay.returncode}: {replay.stdout!r} {replay.stderr!r}")
    assert fx.tree() == before, (
        "AJ1: el replay con unidad suspendida tampoco modifica nada")

    republished = _republish(fx)
    assert republished.returncode != 0, (
        "AJ1: sin binding activo verificable, republicar rechaza: "
        f"{republished.stdout!r} {republished.stderr!r}")
    assert fx.tree() == before, (
        "AJ1: la republicación rechazada no modifica nada")

    doc = _view(fx.status(), "AJ1 status")
    assert doc.get("situation") == "units-suspended", (
        f"AJ1: la vista sigue en reposo suspendido: {doc.get('situation')!r}")
    projected = doc.get("suspended_units") or []
    assert [item.get("feature_id") for item in projected] == [FEATURE_ID], (
        f"AJ1: la proyección conserva la unidad suspendida: {projected!r}")
    assert "open-unit" not in _alternative_verbs(doc), (
        "AJ1: no se ofrecen abrir unidades suspendidas (sólo elegibles): "
        f"{_alternative_verbs(doc)!r}")


# ================================================================ PC-12


@pytest.mark.parametrize(
    "run_order",
    [_run_order_republish_first, _run_order_withdraw_first],
    ids=["republish-then-withdraw", "withdraw-then-republish"])
def test_prepared_begin_and_project_drift_recovery_both_orders(
        tmp_path: Path, run_order) -> None:
    """PC-12/AJ4 (identidad genérica): paquete `prepared` + `begin` vigente +
    DRIFT exclusivo de `project`; las dos rutas independientes y su
    composición en AMBOS órdenes; tras ambas operaciones la cadena es
    trazable y un `prepare` nuevo es exitoso."""
    base = tmp_path / run_order.__name__.replace("_run_order_", "")
    install = _simulated_install(base, "install", version=VERSION_V1)
    fx = _DriftProject(base / "proj-base", install=install)
    _assert_withdraw_surface(fx)
    _assert_republish_surface(fx)
    _write_evidence_file(fx)
    begun = _begin(fx, "fixture integrado 007-006", evidence=BEGIN_EVIDENCE)
    assert begun.returncode == 0, (
        f"fixture PC-12: begin vigente: {begun.stdout!r} {begun.stderr!r}")
    begin_sha = json.loads(begun.stdout)["body_sha256"]
    packet_before = _packet_files(fx)
    original_packet = fx.packet_id

    (install / "version.txt").write_text(VERSION_V2 + "\n", encoding="utf-8")
    _mutate_source_agent(install, "cdad-orchestrator.md",
                         b"<!-- fixture v2 source -->\n")

    run_order(fx)

    head = _head_doc(fx)
    withdraw_sha = head.get("body_sha256")
    assert isinstance(withdraw_sha, str) and withdraw_sha != begin_sha, (
        f"PC-12: la cabeza avanzó al checkpoint de retiro: {head!r}")
    withdraw_body = _body_doc(fx, withdraw_sha)
    assert withdraw_body.get("record") == "checkpoint", (
        f"PC-12: el retiro anexa un checkpoint: {withdraw_body!r}")
    assert (withdraw_body.get("prev") or {}).get(
        "checkpoint_sha256") == begin_sha, (
        "PC-12: la cadena es trazable (begin → checkpoint de retiro)")
    assert withdraw_body.get("evidence") == BEGIN_EVIDENCE, (
        "PC-12/AJ2: la evidencia del begin se conserva en el checkpoint")
    assert _bodies_of(fx) == {f"{begin_sha}.json", f"{withdraw_sha}.json"}, (
        f"PC-12/I5: la republicación no agregó cuerpos; hay: "
        f"{sorted(_bodies_of(fx))}")
    assert _packet_files(fx) == packet_before, (
        "PC-12/I2: los bytes del paquete se conservan en ambas operaciones")
    doc = _view(_installed_status(fx, install), "PC-12 verificación")
    assert doc["version"]["verdict"] == "COHERENT", (
        "PC-12: tras ambas operaciones el DRIFT de proyecto quedó reparado: "
        f"{doc['version']!r}")
    assert entries(_state(fx))[-1].get("transition") == "withdraw", (
        "PC-12: el historial registra el retiro: "
        f"{entries(_state(fx))[-1]!r}")

    freed = fx.prepare()
    assert freed.returncode == 0, (
        f"PC-12: el `prepare` nuevo tras ambas operaciones es exitoso: "
        f"{freed.stdout!r} {freed.stderr!r}")
    active = (_state(fx).get("active_packet") or {})
    assert active.get("id") not in (None, original_packet), (
        f"PC-12: el paquete nuevo es distinto del retirado: {active!r}")
    assert active.get("status") == "prepared", (
        f"PC-12: el paquete nuevo queda `prepared`: {active!r}")


# ================================================================ PC-13


def _publication_failure_case_head(fx: _RecoveryProject):
    """Transaccional (review-002): el tmp de la cabeza (`head.json.tmp`) es un
    DIRECTORIO — condición real de fs que hace fallar la publicación del
    checkpoint de retiro."""
    blocked = _continuity_dir(fx) / "head.json.tmp"
    blocked.mkdir(parents=True, exist_ok=True)
    return (lambda: _withdraw(fx)), blocked


def _publication_failure_case_state(fx: _RecoveryProject):
    """Transaccional (review-002): el tmp del estado (`docs/.cdad-state.json
    .tmp`) es un DIRECTORIO — la publicación del estado falla DESPUÉS de
    publicar el checkpoint; el rollback conjunto debe restaurarlo."""
    blocked = fx.root / "docs" / (STATE_REL.rsplit("/", 1)[-1] + ".tmp")
    blocked.parent.mkdir(parents=True, exist_ok=True)
    blocked.mkdir()
    return (lambda: _withdraw(fx)), blocked


@pytest.mark.parametrize(
    "case",
    [_publication_failure_case_head, _publication_failure_case_state],
    ids=["head-publication-failure", "state-publication-failure"])
def test_withdraw_publication_failure_preserves_state_and_continuity(
        tmp_path: Path, case) -> None:
    """PC-13: un fallo real de escritura durante la publicación del retiro
    devuelve error y conserva CONJUNTAMENTE el estado y la continuidad
    anteriores: snapshot completo byte a byte (cabeza y `bodies/` incluidos)
    y ningún cuerpo nuevo."""
    fx = _RecoveryProject(
        tmp_path / case.__name__.replace("_publication_failure_case_", ""))
    _assert_withdraw_surface(fx)
    _write_evidence_file(fx)
    begun = _begin(fx, "begin del retiro transaccional")
    assert begun.returncode == 0, (
        f"fixture PC-13: begin válido: {begun.stdout!r} {begun.stderr!r}")
    head_before = (_continuity_dir(fx) / "head.json").read_bytes()
    bodies_before = _bodies_of(fx)
    call, blocked = case(fx)
    before = fx.tree()

    proc = call()
    assert proc.returncode != 0, (
        f"PC-13: el fallo real de escritura ({blocked.name}) debe devolver "
        f"error (rc≠0); rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    assert (proc.stdout + proc.stderr).strip(), (
        "PC-13: el fallo de publicación deja diagnóstico observable")
    assert fx.tree() == before, (
        f"PC-13: el fallo conserva el snapshot completo byte a byte (estado, "
        f"cabeza y bodies/ incluidos); cambios: "
        f"{sorted(set(before) ^ set(fx.tree()))}")
    assert (_continuity_dir(fx) / "head.json").read_bytes() == head_before, (
        "PC-13: la cabeza anterior permanece byte a byte")
    assert _bodies_of(fx) == bodies_before, (
        "PC-13: el fallo no deja ningún cuerpo nuevo; cuerpos: "
        f"{sorted(_bodies_of(fx))}")


# ================================================================ AJ1 (por unidad)


def test_withdraw_suspension_guard_is_per_unit_with_other_unit_active(
        tmp_path: Path) -> None:
    """AJ1 (review-002): la guarda de suspensión es POR UNIDAD. Con A
    suspendida y B activa, retirar el paquete de A → rc=1 (guarda, causa
    nombrada) sin cambios; el retiro real de B (unidad activa) y su replay
    idéntico se comportan según contrato, con A todavía suspendida."""
    fx = _RecoveryProject(tmp_path)
    _assert_withdraw_surface(fx)
    packet_a = fx.packet_id
    assert _suspend(fx).returncode == 0, (
        f"fixture AJ1: unidad A suspendida: {fx.packet_id}")
    # Contrato aprobado de B (patrón 007-007 PC-10): el archivo, la apertura y
    # el gate `specification` públicos ANTES del prepare de B.
    b_contract_rel = f"docs/specs/{FEATURE_B}/spec.md"
    b_contract_path = fx.root / b_contract_rel
    b_contract_path.parent.mkdir(parents=True, exist_ok=True)
    b_contract_path.write_bytes(
        b"# Approved fixture contract for unit B\n\n007-006 AJ1 fixture.\n")
    state = _state(fx)
    state["epic_features"].append({"id": FEATURE_B, "status": "queued"})
    fx.write_state(state)
    opened = fx.run_packet("open-unit", "--project-root", str(fx.root),
                           "--feature", FEATURE_B)
    assert opened.returncode == 0, (
        f"fixture AJ1: abrir B con A suspendida: {opened.stdout!r} "
        f"{opened.stderr!r}")
    gate = fx.run_packet(
        "register-transition", "--project-root", str(fx.root),
        "--transition", "gate", "--stage", "specification",
        "--approve-by", "Demo Approver", "--contract-path", b_contract_rel,
    )
    assert gate.returncode == 0, (
        f"fixture AJ1: aprobar el contrato de B por el gate público: "
        f"{gate.stdout!r} {gate.stderr!r}")
    assert _state(fx).get("active_feature") == FEATURE_B, (
        "fixture AJ1: B es la unidad activa")
    before = fx.tree()

    refused = _withdraw(fx, packet_id=packet_a)
    assert refused.returncode == 1, (
        "AJ1: retirar el paquete de la unidad SUSPENDIDA A es estado "
        f"protegido (rc=1) aunque B esté activa; rc={refused.returncode}: "
        f"{refused.stdout!r} {refused.stderr!r}")
    assert fx.tree() == before, (
        "AJ1: el retiro de A rechazado no modifica nada")
    text = refused.stdout + refused.stderr
    assert FEATURE_ID in text or packet_a in text, (
        f"AJ1: la guarda nombra la causa (la unidad/paquete suspendido de A): "
        f"{text!r}")

    prepared_b = fx.run_packet("prepare", "--project-root", str(fx.root),
                               "--role", "test-writer", "--substage", "red",
                               "--objective", "retiro real de B")
    assert prepared_b.returncode == 0, (
        f"fixture AJ1: B prepara su propio paquete: {prepared_b.stdout!r} "
        f"{prepared_b.stderr!r}")
    packet_b = (_state(fx).get("active_packet") or {}).get("id")
    assert isinstance(packet_b, str) and packet_b != packet_a, (
        f"fixture AJ1: B tiene su paquete propio: {packet_b!r}")

    first = _withdraw(fx, packet_id=packet_b)
    assert first.returncode == 0, (
        "AJ1: el retiro REAL de B (unidad activa) no lo bloquea la suspensión "
        f"de A (guarda por unidad): {first.stdout!r} {first.stderr!r}")
    entry = entries(_state(fx))[-1]
    assert entry.get("transition") == "withdraw" and entry.get(
        "packet_id") == packet_b, (
        f"AJ1: el retiro de B queda registrado: {entry!r}")
    settled = fx.tree()
    history_len = len(entries(_state(fx)))

    replay = _withdraw(fx, packet_id=packet_b)
    assert replay.returncode == 0, (
        "AJ1: el replay idéntico del retiro histórico REAL de B se comporta "
        f"según contrato (éxito sin efectos): {replay.stdout!r} "
        f"{replay.stderr!r}")
    assert fx.tree() == settled, (
        "AJ1: el replay de B no escribe")
    assert len(entries(_state(fx))) == history_len, (
        "AJ1: el replay de B no agrega entrada")
    assert FEATURE_ID in (_state(fx).get("suspended_units") or {}), (
        "AJ1: A permanece suspendida durante todo el recorrido de B")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
