#!/usr/bin/env python3
"""005-013 T1 RED — proyección de unidad: localizador estructural, fallback
declarado, anclas por declaración del producto, publicación/pin y
recepción/resume contra el contrato recibido.

Contract:
- docs/specs/005-013-unit-contract/spec.md §2.1-§2.3 (proyección de unidad,
  localizador estructural, ubicación/pin/kind-path y fallback, anclas por
  declaración del producto), §2.6 (recepción/resume contra el contrato
  recibido), §3 PD-1..PD-6 y PD-12, §5 AC-1..AC-4.
- docs/specs/005-013-unit-contract/plan.md §4 ficha T1 (test focal declarado
  `tests/test_005_013_t1_unit_projection.py`; las TRES formas de plan de
  B1.4/AC-9).

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI
del repo; el módulo NUNCA se importa y la implementación NUNCA se lee):

    python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root R \\
        --role architect --substage discovery --objective <texto>
    python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root R \\
        --record-dispatch <id> --attempt-id <a> --input <obs.json>
    python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root R \\
        --resume-packet <id>
    python3 <skill-dir>/scripts/cdad_packet.py render|status --project-root R ...
    python3 <skill-dir>/scripts/cdad_result.py receive --project-root R \\
        --execution-context E.json --packet PACKET.md --request REQUEST.json \\
        --descriptor RESULT.json

Los proyectos son fixtures sintéticos en tempdirs (patrón ya existente:
`build_project` + `prepare` real de tests/test_004_002_t2_bootstrap.py y
tests/test_005_007_t3_open_unit.py / test_005_007_t4_architect_report_
materialization.py), con el `HOME` del subproceso SIEMPRE en un tempdir
vacío (nunca el HOME real). Los ids, títulos y rutas de los fixtures son
inventados (`999-…`, `epic-999-fixture`): ningún proyecto real, ninguna
ruta absoluta del dueño, ningún id de sesión real.

Mapa test → postcondición / criterio de aceptación:

  test_pd1_pd4_projection_locates_unit_and_pins_digest
      -> PD-1 (parte `unit` = encabezado de la tabla + la única fila con el
         id como token completo, verbatim; partes `shared` incluidas) y
         PD-4 (publicación única + pin por digest) / AC-1, AC-3.
  test_pd1_locator_accepts_plain_link_and_backtick_cells
      -> PD-1 (la localización NO exige igualdad exacta de la celda:
         texto plano / enlace / backticks) / AC-1.
  test_pd1_inv10_locator_ignores_section_titles
      -> PD-1/INV-10 (el localizador no mira el título de la sección).
  test_pd12_origin_records_unit_plan_sha_approver_and_policy
      -> PD-12 (origen: unidad, path del plan, sha del plan, approved_by y
         policy_sha256) / AC-8.
  test_pd2_fallback_when_no_row_contains_the_feature_id
      -> PD-2 (cero filas → fallback declarado) / AC-2.
  test_pd2_fallback_when_two_rows_contain_the_feature_id
      -> PD-2 (más de una fila → fallback declarado) / AC-2.
  test_pd3_history_excluded_and_authorization_included_as_shared
      -> PD-3 (anclas por declaración del producto: historia excluida,
         autorización incluida como `shared`).
  test_pd3_plan_without_anchors_is_conservative_and_not_closed
      -> PD-3 (sin anclas: todas `shared`, conservador; NO falla cerrado,
         NO produce `impeded`) / AC-2.
  test_b14_three_plan_forms_locator_and_coherent_pin
      -> PD-1/PD-2 (tres formas de plan) / AC-9 (B1.4).
  test_pd6_receive_and_resume_against_the_received_contract
      -> PD-6 (receive rc=0 con las validaciones passed y
         semantic_status pending; `--resume-packet` re-emite byte a byte)
         / AC-4.
  test_pd6_control_receive_does_not_approve_and_status_is_read_only
      -> PD-6/PD-11 CONTROL: recibir no aprueba y `status` no escribe.
         Este control PASA hoy y debe seguir pasando (guardia de
         neutralidad); se declara como tal.
  test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes
      -> INV-3/PD-4 (B1 de la review formal, bucket h: la proyección publicada
         NUNCA se reescribe). `prepare` con `--out-dir` custom VACÍO cuyo
         `packet_id` acuñado es el MISMO de un paquete ya publicado en el
         directorio por defecto → falla cerrada (rc!=0) nombrando el paquete en
         conflicto y bytes del paquete viejo byte-idénticos (sha256 antes ==
         sha256 después). Condición de cierre 1 de B1.
  test_b1_collision_leaves_the_old_packet_valid_and_receivable
      -> INV-3/PD-4/PD-6 (B1): tras el intento de colisión, el paquete viejo
         conserva su pin (`contract.sha256` == digest del archivo) y sigue
         recebible (`receive` rc=0, validaciones `passed`,
         `semantic_status: pending`). Condición de cierre 1 de B1.
  test_b1_no_collision_with_custom_out_dir_still_publishes
      -> PD-4/PD-5 (control de B1): sin colisión (ningún paquete con ese id en
         el directorio por defecto), `--out-dir` custom publica la proyección
         en la ruta canónica con el pin coherente
         (`sha256(archivo) == contract.sha256 == active_packet.contract_sha256`)
         y el paquete queda en el directorio custom: la corrección no rompe el
         camino sin colisión.

RED hoy (hecho medido): el contrato del architect sigue siendo el plan
completo (`approved-epic-plan`), NO se publica `UNIT-CONTRACT.md`, `prepare`
no informa motivo de fallback en stderr y `status` no tiene el bloque
`unit_contract`; tras agregar una unidad futura independiente al plan, el
sha del plan cambia y `receive`/`--resume-packet` fallan contra los bytes
vivos del plan. Cada caso falla en la ASERCIÓN del comportamiento del
contrato (AssertionError), nunca en ImportError, SyntaxError, un error de
uso del CLI ni un fixture mal armado.

RED hoy del tramo review-fix de B1 (hecho MEDIDO sobre el CLI del repo, con los
tres casos nuevos de abajo): (1) la colisión `--out-dir` custom REESCRIBE el
`UNIT-CONTRACT.md` del paquete viejo (sha `2237d30d…` → `cec98be9…`) y devuelve
rc=0 sin nombrar el paquete en conflicto; (2) el paquete viejo queda con el pin
roto y `receive` responde rc=2 («contract sha256 does not match exact content»);
(3) sin colisión, `prepare` con `--out-dir` custom responde rc=2 («cannot write
prepared packet: [Errno 2] … extra-000 -> …/UNIT-CONTRACT.md») porque el commit
de la proyección asume que el directorio del paquete existe en la ruta canónica.
Los tres casos fallan en la ASERCIÓN del comportamiento del contrato
(AssertionError), nunca en ImportError, SyntaxError, un error de uso del CLI ni
un fixture mal armado.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
# Superficie declarada por la ficha T1: el CLI del producto (el archivo que
# T1 modifica y su helper de recepción, sin cambios de esquema).
PACKET_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
RESULT_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_result.py"

CLI_TIMEOUT_S = 120

# ---------------------------------------------------------------- contrato
EPIC_ID = "epic-999-fixture"
FEATURE_ID = "999-001-fixture-unit"
OTHER_FEATURE_ID = "999-002-fixture-other"
FUTURE_FEATURE_ID = "999-003-fixture-future"

PLAN_REL = f"docs/epics/{EPIC_ID}/plan.md"
AUTHORITY_REL = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_REL = "docs/cdad-policy.json"
STATE_REL = "docs/.cdad-state.json"
SPEC_REL = f"docs/specs/{FEATURE_ID}/spec.md"

APPROVER = "orquestador"

CONTRACT_KIND_PROJECTION = "approved-unit-contract"
CONTRACT_KIND_FALLBACK = "approved-epic-plan"

# ---------------------------------------------------------------- plan fixture
PLAN_TITLE = f"# Epic plan fixture ({EPIC_ID})"

# Forma (i): la del epic (tabla de unidades + sección de historia).
UNITS_TITLE = "## Entregas"
UNITS_HEADER = "| Orden | Feature | Estado | Depende de |"
UNITS_SEPARATOR = "|---|---|---|---|"

# Forma (ii): la de la plantilla del producto.
TEMPLATE_UNITS_TITLE = "## Decomposition into features"
TEMPLATE_HEADER = "| Feature ID | Objective | Scope | Dependencies |"
TEMPLATE_SEPARATOR = "|---|---|---|---|"
TEMPLATE_UNIT_ROW = f"| {FEATURE_ID} | objetivo del fixture | alcance del fixture | — |"
TEMPLATE_OTHER_ROW = f"| {OTHER_FEATURE_ID} | otro objetivo | otro alcance | — |"
TEMPLATE_HISTORY_TITLE = "## Plan changes"
TEMPLATE_HISTORY_BODY = (
    f"- 2026-10-14: alta de la unidad {OTHER_FEATURE_ID} (registro del fixture).")

# Forma (iii): fixture sintético y anónimo (celda enlace, sin historia ni
# autoridad; ids y títulos inventados).
ANON_UNITS_TITLE = "## Workstreams"
ANON_HEADER = "| Ref | Item | State |"
ANON_SEPARATOR = "|---|---|---|"
ANON_NOTES_TITLE = "## Notas del fixture"
ANON_NOTES_BODY = "Notas compartidas del fixture anonimo."

# Sección compartida que prevalece sobre las filas (patrón «Ajuste de los
# ciclos pendientes» del epic real, declarado en la spec §2.1).
SHARED_PREVAILS_TITLE = "## Ajuste del fixture"
SHARED_PREVAILS_BODY = "Esta seccion compartida prevalece sobre las filas de la tabla."
HISTORY_TITLE = "## Cambios al plan"
HISTORY_BODY = (
    f"- 2026-10-14: alta de la unidad {OTHER_FEATURE_ID} (registro del fixture).")
AUTHORITY_TITLE = "## Autoridad"
AUTHORITY_BODY = "Autoridad del epic declarada por el fixture."
OPERATION_TITLE = "## Operacion"
OPERATION_BODY = "Reglas compartidas de operacion del fixture."


def plain_cell(feature_id: str = FEATURE_ID) -> str:
    return f"{feature_id} — unidad activa del fixture"


def link_cell(feature_id: str = FEATURE_ID) -> str:
    return f"[{feature_id} — unidad activa del fixture](docs/specs/{feature_id}/spec.md)"


def backtick_cell(feature_id: str = FEATURE_ID) -> str:
    return f"`{feature_id}`"


def unit_row(cell: str) -> str:
    return f"| 1 | {cell} | in-progress | — |"


OTHER_ROW = f"| 2 | {OTHER_FEATURE_ID} — unidad futura del fixture | queued | — |"
FUTURE_ROW = f"| 3 | {FUTURE_FEATURE_ID} — unidad futura independiente | queued | — |"
# Segunda fila que contiene el id de la unidad activa como token completo
# (ambigüedad declarada de PD-2).
DEPENDENT_ROW = f"| 3 | {OTHER_FEATURE_ID} — dependiente | queued | {FEATURE_ID} |"

HISTORY_EDIT_LINE = (
    f"- 2026-10-14: alta de la unidad {FUTURE_FEATURE_ID} (registro del fixture).")


def plan_text(
    *,
    units_title: str = UNITS_TITLE,
    units_header: str = UNITS_HEADER,
    units_separator: str = UNITS_SEPARATOR,
    body_rows: list[str] | None = None,
    history_title: str = HISTORY_TITLE,
    history_body: str = HISTORY_BODY,
    authority_title: str = AUTHORITY_TITLE,
    authority_body: str = AUTHORITY_BODY,
    extra_sections: tuple[tuple[str, str], ...] = (),
) -> str:
    """Plan fixture sintético. `history_title=""` / `authority_title=""`
    omiten la sección (plan sin esa ancla declarada)."""
    rows = (body_rows if body_rows is not None
            else [unit_row(plain_cell()), OTHER_ROW])
    lines = [PLAN_TITLE, ""]
    for title, body in extra_sections:
        lines += [title, "", body, ""]
    lines += [units_title, "", units_header, units_separator, *rows, "",
              SHARED_PREVAILS_TITLE, "", SHARED_PREVAILS_BODY, ""]
    if history_title:
        lines += [history_title, "", history_body, ""]
    if authority_title:
        lines += [authority_title, "", authority_body, ""]
    lines += [OPERATION_TITLE, "", OPERATION_BODY, ""]
    return "\n".join(lines)


def unit_block(header: str = UNITS_HEADER, separator: str = UNITS_SEPARATOR,
               row: str | None = None) -> str:
    """Parte `unit` declarada por PD-1: encabezado de la tabla (fila de
    encabezado + separador) + la fila de la unidad, verbatim."""
    return f"{header}\n{separator}\n{row if row is not None else unit_row(plain_cell())}\n"


# ---------------------------------------------------------------- helpers


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    """Cada entrada bajo root: archivos → bytes, directorios → None."""
    snap: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        snap[rel] = path.read_bytes() if path.is_file() else None
    return snap


def state_document(*, epic_plan_approved: bool = True) -> dict:
    """State sintético del fixture: el architect queda habilitado por la
    entrada `epic_history` `epic-plan` con `approved_by` (PD-12/D1-D2) y la
    delegación HITL activa (patrón de tests/test_005_007_t4_architect_
    report_materialization.py)."""
    epic_history: list[dict] = []
    if epic_plan_approved:
        epic_history.append({
            "epic": EPIC_ID,
            "stage": "epic-plan",
            "approved_by": APPROVER,
            "approved_at": "2026-10-14T00:00:00Z",
            "plan_path": PLAN_REL,
            "note": "plan del fixture aprobado (registro del fixture)",
        })
    return {
        "version": 1,
        "stack": None,
        "active_epic": EPIC_ID,
        "epic_stage": "features-loop",
        "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
        "epic_history": epic_history,
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": "red",
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": [],
        "approver": APPROVER,
        "last_updated": "2026-10-14T00:00:00Z",
        "execution": None,
        "active_packet": None,
        "hitl_delegation": {
            "status": "active",
            "epic_id": EPIC_ID,
            "source": AUTHORITY_REL,
            "scope": EPIC_ID,
            "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
        },
    }


def observation_document() -> dict:
    """Documento de observación del intento (registro I8; sin datos de host
    ni ids de sesión reales)."""
    return {
        "runtime": "opencode",
        "model_configured": "fixture-model",
        "model_reported": "fixture-model",
        "session": "ses-fixture-0001",
        "started_at": "2026-10-14T00:00:00Z",
        "provenance": {
            "runtime": "reported by runtime",
            "model_reported": "orchestrator",
            "session": "orchestrator",
        },
    }


def build_project(root: Path, plan: str, *,
                  epic_plan_approved: bool = True) -> Path:
    """Proyecto sintético válido para `prepare` (política + plan del epic +
    autoridad + state con la autorización del architect)."""
    root.mkdir(parents=True, exist_ok=True)
    for rel in ("tests", "src", "docs"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    (root / POLICY_REL).write_text(json.dumps({
        "schema_version": 1,
        "path_policy": {
            "test_roots": ["tests"],
            "implementation_roots": ["src", "lib"],
            "documentation_roots": ["docs"],
        },
        "temporary_roots": [".cdad/tmp"],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / PLAN_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / PLAN_REL).write_text(plan, encoding="utf-8")
    (root / AUTHORITY_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / AUTHORITY_REL).write_text(
        "# Authorized execution fixture (epic-999)\n", encoding="utf-8")
    (root / SPEC_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / SPEC_REL).write_bytes(b"# Spec fixture (solo insumo del fixture)\n")
    state = state_document(epic_plan_approved=epic_plan_approved)
    (root / STATE_REL).write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
    return root


class Fixture:
    """Proyecto sintético autocontenido en un tempdir, con HOME aislado."""

    def __init__(self, base: Path, plan: str) -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        build_project(self.root, plan)

    # -- CLI (caja negra) ----------------------------------------------

    def run(self, script: Path, *args: str) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env["HOME"] = str(self.home)  # NUNCA el HOME real
        return subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True, text=True, cwd=REPO_ROOT, env=env,
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
        )

    def prepare(self, *, role: str = "architect", substage: str = "discovery",
                objective: str = "005-013 T1 fixture") -> subprocess.CompletedProcess:
        return self.run(
            PACKET_CLI, "prepare", "--project-root", str(self.root),
            "--role", role, "--substage", substage, "--objective", objective)

    def prepare_ok(self, **kwargs) -> subprocess.CompletedProcess:
        proc = self.prepare(**kwargs)
        assert proc.returncode == 0, (
            "precondición (fixture): `prepare` del architect debe publicar el "
            f"paquete (rc=0): rc={proc.returncode} stdout={proc.stdout!r} "
            f"stderr={proc.stderr!r}")
        return proc

    def status(self) -> subprocess.CompletedProcess:
        return self.run(PACKET_CLI, "status", "--project-root", str(self.root))

    def render(self, packet_id: str) -> subprocess.CompletedProcess:
        return self.run(
            PACKET_CLI, "render", "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path),
            "--request", str(self.packet_dir(packet_id) / "REQUEST.json"))

    def resume(self, packet_id: str) -> subprocess.CompletedProcess:
        return self.run(
            PACKET_CLI, "prepare", "--project-root", str(self.root),
            "--resume-packet", packet_id)

    def dispatch(self, packet_id: str) -> subprocess.CompletedProcess:
        observation = self.root / "docs" / "observations-fixture.json"
        observation.write_text(
            json.dumps(observation_document(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return self.run(
            PACKET_CLI, "prepare", "--project-root", str(self.root),
            "--record-dispatch", packet_id, "--attempt-id", "att-fixture-0001",
            "--input", str(observation))

    def dispatch_ok(self, packet_id: str) -> subprocess.CompletedProcess:
        proc = self.dispatch(packet_id)
        assert proc.returncode == 0, (
            "precondición (fixture): `--record-dispatch` debe registrar el "
            f"intento (rc=0): rc={proc.returncode} stdout={proc.stdout!r} "
            f"stderr={proc.stderr!r}")
        assert self.state()["active_packet"]["status"] == "dispatched", (
            "precondición (fixture): el paquete activo debe quedar dispatched: "
            f"{self.state()['active_packet']['status']!r}")
        return proc

    def receive(self, packet_id: str) -> subprocess.CompletedProcess:
        inbox = self.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        part_name = "architect-report"
        (inbox / f"{part_name}.md").write_bytes(
            b"# Role report (fixture 005-013 T1)\nInforme del architect.\n")
        manifest_rel = ".cdad/inbox/changes.json"
        (self.root / manifest_rel).write_text(json.dumps({
            "schema_version": 1,
            "observation_status": "trusted",
            "baseline_ref": "orchestrator-staged-reference",
            "baseline_sha256": "0" * 64,
            "changes": [],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        descriptor = {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": packet_id,
            "feature_id": FEATURE_ID,
            "source": {"kind": "staged-file", "sdk_message_ref": None},
            "parts": [{
                "name": part_name,
                "artifact_kind": "role-report",
                "staged_path": f".cdad/inbox/{part_name}.md",
            }],
            "observed_changes": {
                "observation_status": "trusted",
                "baseline_ref": "orchestrator-staged-reference",
                "baseline_sha256": "0" * 64,
                "manifest_path": manifest_rel,
            },
            "run_evidence_ref": None,
        }
        descriptor_path = self.root / ".cdad" / "inbox" / "RESULT.json"
        descriptor_path.write_text(
            json.dumps(descriptor, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8")
        return self.run(
            RESULT_CLI, "receive", "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path),
            "--packet", str(self.packet_dir(packet_id) / "PACKET.md"),
            "--request", str(self.packet_dir(packet_id) / "REQUEST.json"),
            "--descriptor", str(descriptor_path))

    # -- ediciones declaradas del plan --------------------------------

    def edit_plan_add_independent_unit(self) -> None:
        """Agrega una unidad futura INDEPENDIENTE al plan y registra la
        edición en la sección de historia (§1.1 paso 2)."""
        path = self.root / PLAN_REL
        before = path.read_bytes()
        text = path.read_text(encoding="utf-8")
        assert OTHER_ROW in text, (
            "precondición (fixture): la tabla de unidades debe existir")
        text = text.replace(OTHER_ROW, OTHER_ROW + "\n" + FUTURE_ROW, 1)
        assert HISTORY_BODY in text, (
            "precondición (fixture): la sección de historia debe existir")
        text = text.replace(HISTORY_BODY, HISTORY_BODY + "\n" + HISTORY_EDIT_LINE, 1)
        path.write_text(text, encoding="utf-8")
        assert path.read_bytes() != before, (
            "precondición (fixture): la edición debe cambiar los bytes del plan")

    # -- oráculos de lectura -------------------------------------------

    def state(self) -> dict:
        return json.loads((self.root / STATE_REL).read_text(encoding="utf-8"))

    def state_bytes(self) -> bytes:
        return (self.root / STATE_REL).read_bytes()

    def plan_bytes(self) -> bytes:
        return (self.root / PLAN_REL).read_bytes()

    def policy_bytes(self) -> bytes:
        return (self.root / POLICY_REL).read_bytes()

    def snapshot(self) -> dict[str, bytes | None]:
        return tree_snapshot(self.root)

    @property
    def execution_id(self) -> str:
        execution_id = (self.state().get("execution") or {}).get("id")
        assert execution_id, (
            "precondición (fixture): state.execution debe referenciar el "
            "contexto v2")
        return execution_id

    @property
    def execution_context_path(self) -> Path:
        return (self.root / ".cdad" / "executions" / self.execution_id
                / "execution.json")

    def packet_id(self) -> str:
        active = self.state().get("active_packet") or {}
        assert active.get("id"), (
            "precondición (fixture): debe existir un paquete activo")
        return active["id"]

    def packet_dir(self, packet_id: str | None = None) -> Path:
        return (self.root / ".cdad" / "packets"
                / (packet_id or self.packet_id()))

    def packet_bytes(self, packet_id: str | None = None) -> bytes:
        return (self.packet_dir(packet_id) / "PACKET.md").read_bytes()

    def request(self, packet_id: str | None = None) -> dict:
        return json.loads(
            (self.packet_dir(packet_id) / "REQUEST.json").read_text(encoding="utf-8"))

    def unit_contract_path(self, packet_id: str | None = None) -> Path:
        return self.packet_dir(packet_id) / "UNIT-CONTRACT.md"

    def unit_contract_text(self, packet_id: str | None = None) -> str:
        path = self.unit_contract_path(packet_id)
        assert path.is_file(), (
            "PD-4 violada: `prepare` del architect debe publicar la proyección "
            f"de unidad en {path.relative_to(self.root)}; no existe (hoy el "
            "contrato sigue siendo el plan completo)")
        return path.read_text(encoding="utf-8")

    def status_block(self) -> dict:
        proc = self.status()
        assert proc.returncode == 0, (
            "precondición (fixture): la vista `status` debe emitir (rc=0): "
            f"{proc.stdout!r} {proc.stderr!r}")
        try:
            doc = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise AssertionError(
                "precondición (fixture): stdout de `status` no es JSON: "
                f"{proc.stdout[:200]!r}") from exc
        return doc.get("unit_contract") or {}


@pytest.fixture
def fx(tmp_path: Path) -> Fixture:
    return Fixture(tmp_path, plan_text())


def make_fixture(tmp_path: Path, plan: str, name: str = "proj") -> Fixture:
    return Fixture(tmp_path / name, plan)


# ---------------------------------------------------------------- PD-1 / PD-4


def test_pd1_pd4_projection_locates_unit_and_pins_digest(fx: Fixture) -> None:
    """PD-1/PD-4 (AC-1/AC-3): `prepare --role architect --substage discovery`
    publica `.cdad/packets/<packet_id>/UNIT-CONTRACT.md`; la parte `unit` es
    el ENCABEZADO de la tabla (fila de encabezado + separador) + la fila de
    la unidad, verbatim; las filas de otras unidades se remueven; una sección
    compartida aparece como parte `shared`; y el digest del archivo coincide
    con `contract.sha256` del REQUEST.json y con
    `state.active_packet.contract_sha256`.

    RED hoy: no se publica `UNIT-CONTRACT.md` (el contrato es el plan
    completo) → falla la aserción de la proyección (AssertionError).
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    text = fx.unit_contract_text(packet_id)

    block = unit_block()
    assert block in text, (
        "PD-1 violada: la parte `unit` debe ser el encabezado de la tabla "
        "(fila de encabezado + separador) + la fila de la unidad, verbatim: "
        f"{block!r} no aparece en la proyección: {text!r}")
    assert text.count(unit_row(plain_cell())) == 1, (
        "PD-1 violada: la tabla de unidades se remueve de la sección que la "
        "contiene (sus líneas no se duplican en la parte `shared`); la fila "
        f"de la unidad aparece {text.count(unit_row(plain_cell()))} veces")
    assert OTHER_ROW not in text, (
        "PD-1 violada: las filas de OTRAS unidades se remueven de la "
        f"proyección (agregar una unidad futura no la cambia): {OTHER_ROW!r}")

    assert SHARED_PREVAILS_TITLE in text, (
        "PD-1 violada: la sección compartida que prevalece sobre las filas "
        f"debe ser parte `shared`: falta {SHARED_PREVAILS_TITLE!r}")
    assert SHARED_PREVAILS_BODY in text, (
        "PD-1 violada: el cuerpo de la sección compartida debe incluirse "
        f"verbatim: falta {SHARED_PREVAILS_BODY!r}")

    origin = text.split(block, 1)[0]
    assert "shared" in origin, (
        "PD-1 violada: el bloque de origen debe listar las partes con su "
        f"clase (`unit` | `shared`); `shared` no aparece en el origen: "
        f"{origin!r}")
    assert "unit" in origin, (
        "PD-1 violada: el bloque de origen debe listar las partes con su "
        f"clase (`unit` | `shared`); `unit` no aparece en el origen: "
        f"{origin!r}")

    contract = fx.request(packet_id)["contract"]
    assert contract["kind"] == CONTRACT_KIND_PROJECTION, (
        "PD-4/PD-5 violada: el contrato del paquete debe ser "
        f"{CONTRACT_KIND_PROJECTION!r}: {contract!r}")
    assert contract["path"] == f".cdad/packets/{packet_id}/UNIT-CONTRACT.md", (
        "PD-4 violada: el path del contrato debe ser la proyección publicada "
        f"junto al paquete: {contract['path']!r}")
    assert contract["sha256"] == sha256_bytes(
        fx.unit_contract_path(packet_id).read_bytes()), (
        "PD-4 violada: `contract.sha256` debe ser el digest de los bytes "
        "exactos de la proyección")
    assert contract["commit"] is None, (
        f"PD-4 violada: `commit` se conserva null: {contract['commit']!r}")
    assert fx.state()["active_packet"]["contract_sha256"] == contract["sha256"], (
        "PD-4 violada: `active_packet.contract_sha256` debe ser el digest de "
        f"la proyección: {fx.state()['active_packet']['contract_sha256']!r} "
        f"!= {contract['sha256']!r}")


@pytest.mark.parametrize(
    "cell_label,cell",
    [
        ("texto plano", plain_cell()),
        ("enlace", link_cell()),
        ("backticks", backtick_cell()),
    ],
    ids=["texto-plano", "enlace", "backticks"],
)
def test_pd1_locator_accepts_plain_link_and_backtick_cells(
        tmp_path: Path, cell_label: str, cell: str) -> None:
    """PD-1 (AC-1): la localización NO exige igualdad exacta de la celda: con
    la celda de la unidad como TEXTO PLANO, como ENLACE
    (`[<ID> — <título>](<ruta>)`) y entre BACKTICKS, el localizador encuentra
    la MISMA fila (la que la contiene) y publica la proyección con un pin
    coherente.

    RED hoy: no se publica `UNIT-CONTRACT.md` → falla la aserción.
    """
    fx = make_fixture(tmp_path, plan_text(body_rows=[unit_row(cell), OTHER_ROW]))
    fx.prepare_ok()
    packet_id = fx.packet_id()
    text = fx.unit_contract_text(packet_id)
    block = unit_block(row=unit_row(cell))
    assert block in text, (
        f"PD-1 violada (celda {cell_label}): el localizador debe encontrar la "
        f"fila de la unidad sin exigir igualdad exacta de la celda: {block!r} "
        f"no aparece en la proyección: {text!r}")
    contract = fx.request(packet_id)["contract"]
    assert contract["kind"] == CONTRACT_KIND_PROJECTION, (
        f"PD-4 violada (celda {cell_label}): {contract!r}")
    assert contract["sha256"] == sha256_bytes(
        fx.unit_contract_path(packet_id).read_bytes()), (
        f"PD-4 violada (celda {cell_label}): el pin debe ser el digest de la "
        "proyección publicada")


def test_pd1_inv10_locator_ignores_section_titles(tmp_path: Path) -> None:
    """PD-1/INV-10: el MISMO fixture con los títulos de sección cambiados (la
    tabla de unidades en una sección llamada distinto, sin la palabra
    «Entregas», y con una tabla señuelo) sigue localizando la unidad: el
    localizador no mira el título de la sección.

    RED hoy: no se publica `UNIT-CONTRACT.md` → falla la aserción.
    """
    fx = make_fixture(tmp_path, plan_text(
        units_title="## Unidades del fixture",
        extra_sections=(("## Otra tabla del fixture", "| A | B |\n|---|---|\n| x | y |"),)))
    fx.prepare_ok()
    packet_id = fx.packet_id()
    text = fx.unit_contract_text(packet_id)
    block = unit_block()
    assert block in text, (
        "PD-1/INV-10 violada: el localizador es estructural y no depende del "
        "título de la sección (la tabla está en «## Unidades del fixture»): "
        f"{block!r} no aparece en la proyección: {text!r}")
    assert "Entregas" not in (fx.root / PLAN_REL).read_text(encoding="utf-8"), (
        "precondición (fixture): el plan NO debe contener la palabra "
        "«Entregas»")


def test_pd12_origin_records_unit_plan_sha_approver_and_policy(fx: Fixture) -> None:
    """PD-12 (AC-8): el bloque de origen registra la unidad activa, el path
    del plan, el sha del plan al generar, el `approved_by` de la entrada
    `epic_history` `epic-plan` aprobadora y el `policy_sha256`.

    RED hoy: no hay proyección → falla la aserción.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    text = fx.unit_contract_text(packet_id)
    origin = text.split(unit_block(), 1)[0]

    assert FEATURE_ID in origin, (
        "PD-12 violada: el origen debe registrar la unidad activa "
        f"({FEATURE_ID!r}): {origin!r}")
    assert PLAN_REL in origin, (
        f"PD-12 violada: el origen debe registrar el path del plan "
        f"({PLAN_REL!r}): {origin!r}")
    assert sha256_bytes(fx.plan_bytes()) in origin, (
        "PD-12 violada: el origen debe registrar el sha del plan al generar "
        f"({sha256_bytes(fx.plan_bytes())!r}): {origin!r}")
    assert APPROVER in origin, (
        "PD-12 violada: el origen debe registrar el `approved_by` de la "
        f"entrada `epic-plan` aprobadora ({APPROVER!r}): {origin!r}")
    assert sha256_bytes(fx.policy_bytes()) in origin, (
        "PD-12 violada: el origen debe registrar el `policy_sha256` de la "
        f"ejecución ({sha256_bytes(fx.policy_bytes())!r}): {origin!r}")


# ---------------------------------------------------------------- PD-2


def test_pd2_fallback_when_no_row_contains_the_feature_id(tmp_path: Path) -> None:
    """PD-2 (AC-2): un plan SIN ninguna fila con el id de la feature →
    `prepare` rc=0; NO se publica `UNIT-CONTRACT.md`; el `contract` del
    REQUEST.json es `approved-epic-plan` + `docs/epics/<epic_id>/plan.md` +
    el digest del plan (y `active_packet.contract_sha256` coincide); el
    stdout sigue siendo el `PACKET.md` byte a byte (mismo render que
    `render`); el motivo (con la ruta del plan) aparece en stderr; y `status`
    informa el fallback (`unit_contract.mode == "fallback"` + `reason`).

    RED hoy: `prepare` rc=0 y el contrato vigente ya son el comportamiento de
    hoy, pero el motivo NO se informa en stderr y `status` NO tiene el bloque
    `unit_contract` → fallan esas aserciones (AssertionError).
    """
    fx = make_fixture(tmp_path, plan_text(body_rows=[OTHER_ROW]))
    proc = fx.prepare_ok()
    packet_id = fx.packet_id()

    assert not fx.unit_contract_path(packet_id).exists(), (
        "PD-2 violada: en fallback NO se publica la proyección "
        f"({fx.unit_contract_path(packet_id).relative_to(fx.root)})")
    contract = fx.request(packet_id)["contract"]
    assert contract["kind"] == CONTRACT_KIND_FALLBACK, (
        f"PD-2 violada: el contrato del fallback es {CONTRACT_KIND_FALLBACK!r}: "
        f"{contract!r}")
    assert contract["path"] == PLAN_REL, (
        f"PD-2 violada: el path del fallback es {PLAN_REL!r}: {contract!r}")
    assert contract["sha256"] == sha256_bytes(fx.plan_bytes()), (
        "PD-2 violada: el sha del fallback es el digest de los bytes del "
        f"plan: {contract['sha256']!r}")
    assert contract["commit"] is None, (
        f"PD-2 violada: `commit` se conserva null: {contract['commit']!r}")
    assert fx.state()["active_packet"]["contract_sha256"] == contract["sha256"], (
        "PD-2 violada: `active_packet.contract_sha256` debe coincidir con el "
        "contrato del fallback")

    assert proc.stdout == fx.packet_bytes(packet_id).decode("utf-8"), (
        "PD-2 violada: el stdout de `prepare` en fallback sigue siendo el "
        "`PACKET.md` byte a byte")
    rendered = fx.render(packet_id)
    assert rendered.returncode == 0, (
        f"precondición (fixture): `render` debe emitir (rc=0): {rendered.stderr!r}")
    assert rendered.stdout == proc.stdout, (
        "PD-2 violada: stdout de `prepare` == render canónico")

    assert PLAN_REL in proc.stderr, (
        "PD-2 violada: el motivo del fallback debe informarse en el "
        f"diagnóstico (stderr) nombrando la ruta del plan ({PLAN_REL!r}): "
        f"{proc.stderr!r}")
    block = fx.status_block()
    assert block.get("mode") == "fallback", (
        "PD-2 violada: `status` debe informar el fallback "
        f"(`unit_contract.mode == \"fallback\"`): {block!r}")
    assert block.get("reason"), (
        "PD-2 violada: `status` debe informar el motivo del fallback "
        f"(`unit_contract.reason`): {block!r}")


def test_pd2_fallback_when_two_rows_contain_the_feature_id(tmp_path: Path) -> None:
    """PD-2 (AC-2): un plan con DOS filas que contienen el id como token
    completo (ambigüedad) → mismo fallback declarado: `prepare` rc=0, sin
    `UNIT-CONTRACT.md`, contrato `approved-epic-plan` + plan + digest, motivo
    en stderr y `status` en `fallback`.

    RED hoy: el motivo en stderr y el bloque `unit_contract` de `status` no
    existen → fallan esas aserciones.
    """
    fx = make_fixture(tmp_path, plan_text(
        body_rows=[unit_row(plain_cell()), OTHER_ROW, DEPENDENT_ROW]))
    proc = fx.prepare_ok()
    packet_id = fx.packet_id()

    assert not fx.unit_contract_path(packet_id).exists(), (
        "PD-2 violada: con más de una fila con el id NO se publica la "
        "proyección")
    contract = fx.request(packet_id)["contract"]
    assert contract["kind"] == CONTRACT_KIND_FALLBACK, (
        f"PD-2 violada: el contrato del fallback es {CONTRACT_KIND_FALLBACK!r}: "
        f"{contract!r}")
    assert contract["path"] == PLAN_REL and contract["sha256"] == sha256_bytes(
        fx.plan_bytes()), (
        f"PD-2 violada: contrato del fallback incoherente: {contract!r}")
    assert proc.stdout == fx.packet_bytes(packet_id).decode("utf-8"), (
        "PD-2 violada: stdout sigue siendo el `PACKET.md` byte a byte")
    assert PLAN_REL in proc.stderr, (
        "PD-2 violada: el motivo (más de una fila, con la ruta del plan) debe "
        f"informarse en stderr: {proc.stderr!r}")
    block = fx.status_block()
    assert block.get("mode") == "fallback", (
        f"PD-2 violada: `status` debe informar `mode: \"fallback\"`: {block!r}")


# ---------------------------------------------------------------- PD-3


def test_pd3_history_excluded_and_authorization_included_as_shared(
        fx: Fixture) -> None:
    """PD-3: con la declaración del producto presente, la sección de HISTORIA
    (título declarado «Cambios al plan») queda EXCLUIDA de la proyección (su
    contenido no aparece) y la de AUTORIZACIÓN («Autoridad») queda INCLUIDA
    como parte `shared` (sin efecto de veredicto).

    RED hoy: no hay proyección → falla la aserción.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    text = fx.unit_contract_text(packet_id)

    assert HISTORY_TITLE not in text, (
        "PD-3 violada: la sección de historia (ancla declarada por el "
        f"producto) se excluye de la proyección: {HISTORY_TITLE!r} aparece")
    assert HISTORY_BODY not in text, (
        "PD-3 violada: el contenido de la historia no debe aparecer en la "
        f"proyección: {HISTORY_BODY!r}")
    assert AUTHORITY_TITLE in text, (
        "PD-3 violada: la sección de autorización (ancla declarada por el "
        f"producto) se incluye como parte `shared`: falta {AUTHORITY_TITLE!r}")
    assert AUTHORITY_BODY in text, (
        "PD-3 violada: el cuerpo de la sección de autorización debe incluirse "
        f"verbatim: falta {AUTHORITY_BODY!r}")
    origin = text.split(unit_block(), 1)[0]
    assert "shared" in origin, (
        "PD-3 violada: la parte de autorización se etiqueta como `shared` en "
        f"el origen: {origin!r}")


def test_pd3_plan_without_anchors_is_conservative_and_not_closed(
        tmp_path: Path) -> None:
    """PD-3 (b)+(c) / AC-2: un plan SIN las anclas declaradas NO falla
    cerrado: todas sus secciones `##` son partes `shared`, la unidad se
    localiza, `prepare` rc=0 y NO se produce `impeded` (esa causa es de T2:
    autorización retirada, nunca una sección del plan).

    RED hoy: no hay proyección → falla la aserción de las secciones `shared`.
    """
    fx = make_fixture(tmp_path, plan_text(
        history_title="", authority_title="",
        extra_sections=(("## Registro del fixture", "Registro compartido del fixture."),)))
    proc = fx.prepare_ok()
    packet_id = fx.packet_id()
    text = fx.unit_contract_text(packet_id)

    for title, body in (
        (SHARED_PREVAILS_TITLE, SHARED_PREVAILS_BODY),
        (OPERATION_TITLE, OPERATION_BODY),
        ("## Registro del fixture", "Registro compartido del fixture."),
    ):
        assert title in text and body in text, (
            "PD-3 violada: sin ancla de historia, TODAS las secciones del "
            f"plan son partes `shared` (conservador): falta {title!r} / "
            f"{body!r} en la proyección: {text!r}")
    assert "impeded" not in (proc.stdout + proc.stderr).lower(), (
        "PD-3(c) violada: ninguna sección del plan produce `impeded`: "
        f"{(proc.stdout + proc.stderr)!r}")


# ---------------------------------------------------------------- B1.4 / AC-9


@pytest.mark.parametrize(
    "form,plan,block",
    [
        (
            "forma del epic (tabla de unidades + historia)",
            plan_text(),
            unit_block(),
        ),
        (
            "forma de la plantilla del producto",
            plan_text(
                units_title=TEMPLATE_UNITS_TITLE,
                units_header=TEMPLATE_HEADER,
                units_separator=TEMPLATE_SEPARATOR,
                body_rows=[TEMPLATE_UNIT_ROW, TEMPLATE_OTHER_ROW],
                history_title=TEMPLATE_HISTORY_TITLE,
                history_body=TEMPLATE_HISTORY_BODY,
            ),
            unit_block(TEMPLATE_HEADER, TEMPLATE_SEPARATOR, TEMPLATE_UNIT_ROW),
        ),
        (
            "fixture sintetico anonimo (celda enlace, sin historia ni autoridad)",
            plan_text(
                units_title=ANON_UNITS_TITLE,
                units_header=ANON_HEADER,
                units_separator=ANON_SEPARATOR,
                body_rows=[unit_row(link_cell()), OTHER_ROW],
                history_title="",
                authority_title="",
                extra_sections=((ANON_NOTES_TITLE, ANON_NOTES_BODY),),
            ),
            unit_block(ANON_HEADER, ANON_SEPARATOR, unit_row(link_cell())),
        ),
    ],
    ids=["forma-epic", "forma-plantilla-producto", "forma-anonima"],
)
def test_b14_three_plan_forms_locator_and_coherent_pin(
        tmp_path: Path, form: str, plan: str, block: str) -> None:
    """B1.4/AC-9 (PD-1/PD-2): el focal corre sobre las TRES formas de plan
    (la de este epic; la de la plantilla del producto; un fixture sintético y
    anónimo con la celda de la unidad como enlace y sin historia ni
    autoridad). En las tres: el localizador encuentra la unidad, `prepare`
    rc=0 y el pin es coherente (`contract.kind`/`path`/`sha256` == digest de
    la proyección publicada == `active_packet.contract_sha256`).

    RED hoy: no se publica `UNIT-CONTRACT.md` → falla la aserción.
    """
    fx = make_fixture(tmp_path, plan)
    fx.prepare_ok()
    packet_id = fx.packet_id()

    text = fx.unit_contract_text(packet_id)
    assert block in text, (
        f"PD-1 violada ({form}): la parte `unit` debe ser el encabezado de la "
        f"tabla + la fila de la unidad, verbatim: {block!r} no aparece en la "
        f"proyección: {text!r}")
    contract = fx.request(packet_id)["contract"]
    assert contract["kind"] == CONTRACT_KIND_PROJECTION, (
        f"PD-4 violada ({form}): {contract!r}")
    assert contract["path"] == f".cdad/packets/{packet_id}/UNIT-CONTRACT.md", (
        f"PD-4 violada ({form}): {contract['path']!r}")
    assert contract["sha256"] == sha256_bytes(
        fx.unit_contract_path(packet_id).read_bytes()), (
        f"PD-4 violada ({form}): el pin debe ser el digest de la proyección")
    assert fx.state()["active_packet"]["contract_sha256"] == contract["sha256"], (
        f"PD-4 violada ({form}): el binding del state debe coincidir con el pin")


# ---------------------------------------------------------------- PD-6


def test_pd6_receive_and_resume_against_the_received_contract(fx: Fixture) -> None:
    """PD-6 (AC-4): con el paquete del architect DESPACHADO (flujo real:
    `prepare` + `--record-dispatch`), se AGREGA una unidad futura
    INDEPENDIENTE al plan (y la edición se registra en la sección de
    historia): `receive` → rc=0 con `packet_validation` /
    `identity_validation` `passed` y `semantic_status: pending` (el esquema
    del recibo NO cambia: no aparece `contract_sha256`); y
    `prepare --resume-packet <id>` re-emite el paquete BYTE A BYTE.

    RED hoy: el contrato sigue siendo el plan vivo; al agregar la unidad
    futura cambia el sha del plan y `receive`/`--resume-packet` fallan contra
    los bytes vivos → falla la aserción rc=0 (AssertionError).
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    packet_bytes = fx.packet_bytes(packet_id)
    fx.dispatch_ok(packet_id)

    fx.edit_plan_add_independent_unit()

    recv = fx.receive(packet_id)
    assert recv.returncode == 0, (
        "PD-6 violada: `receive` de un paquete despachado debe validar contra "
        "el contrato REGISTRADO (la proyección durable), no contra el plan "
        "vivo: agregar una unidad futura independiente no lo invalida. "
        f"rc={recv.returncode} stdout={recv.stdout!r} stderr={recv.stderr!r}")
    receipt = json.loads(recv.stdout)
    assert receipt.get("packet_validation") == "passed", (
        f"PD-6 violada: `packet_validation` debe ser `passed`: {receipt!r}")
    assert receipt.get("identity_validation") == "passed", (
        f"PD-6 violada: `identity_validation` debe ser `passed`: {receipt!r}")
    assert receipt.get("semantic_status") == "pending", (
        "PD-6 violada: recibir NO aprueba (`semantic_status: pending`): "
        f"{receipt.get('semantic_status')!r}")
    assert "contract_sha256" not in receipt, (
        "PD-6 violada: el esquema del recibo NO cambia (no guarda "
        f"`contract_sha256`): {sorted(receipt)}")

    resumed = fx.resume(packet_id)
    assert resumed.returncode == 0, (
        "PD-6 violada: `prepare --resume-packet` debe re-emitir el paquete "
        "contra el contrato recibido: "
        f"rc={resumed.returncode} stdout={resumed.stdout!r} "
        f"stderr={resumed.stderr!r}")
    assert resumed.stdout == packet_bytes.decode("utf-8"), (
        "PD-6 violada: `--resume-packet` re-emite el paquete BYTE A BYTE "
        "(mismo render)")


def test_pd6_control_receive_does_not_approve_and_status_is_read_only(
        fx: Fixture) -> None:
    """PD-6/PD-11 CONTROL (pasa hoy y debe seguir pasando): recibir no aprueba
    (`semantic_status` siempre `pending`) y el `status` de la vista no escribe
    nada (dos `status` consecutivos dejan el proyecto byte a byte idéntico,
    sin `.impact.json`).

    Este caso es una GUARDIA de neutralidad: no se declara rojo.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    fx.dispatch_ok(packet_id)

    state_before = fx.state_bytes()
    recv = fx.receive(packet_id)
    assert recv.returncode == 0, (
        "precondición (fixture, comportamiento existente 003-002): `receive` "
        f"debe aceptar la entrega (rc=0): {recv.stdout!r} {recv.stderr!r}")
    receipt = json.loads(recv.stdout)
    assert receipt.get("semantic_status") == "pending", (
        "PD-6 violada (neutralidad): recibir NO aprueba "
        f"(`semantic_status: pending`): {receipt.get('semantic_status')!r}")
    assert fx.state_bytes() == state_before, (
        "PD-6 violada (neutralidad): `receive` no debe escribir el state "
        "(el único escritor de la transición es el orquestador)")

    before = fx.snapshot()
    first = fx.status()
    assert first.returncode == 0, (
        f"precondición (fixture): `status` debe emitir (rc=0): {first.stderr!r}")
    second = fx.status()
    assert second.returncode == 0, (
        f"precondición (fixture): `status` debe emitir (rc=0): {second.stderr!r}")
    assert fx.snapshot() == before, (
        "PD-11 violada: `status` es de SOLO LECTURA; dos `status` consecutivos "
        "deben dejar el proyecto byte a byte idéntico")
    assert not list(fx.root.glob(".cdad/packets/*/.impact.json")), (
        "PD-11 violada: `status` nunca crea el journal de impacto")


# ------------------------------------------------ B1 (INV-3/PD-4) review-fix
#
# Bloqueo B1 de la review formal (docs/specs/005-013-unit-contract/review.md,
# bucket h): `prepare` con `--out-dir` custom acuña el `packet_id` contra el
# directorio CUSTOM (vacío) mientras la proyección se publica en la ruta
# canónica bajo el directorio POR DEFECTO
# (`.cdad/packets/<packet_id>/UNIT-CONTRACT.md`); si ese `packet_id` ya existe
# ahí, el commit hacía `os.replace` y REESCRIBÍA el `UNIT-CONTRACT.md` del
# paquete viejo, dejando su `contract.sha256` durable sin coincidir con el
# archivo (paquete irrecebible). Viola INV-3 («una proyección publicada nunca
# se reescribe») y PD-4. La corrección elegida es la barata: escritura
# CREATE-ONLY que falla cerrada nombrando el paquete en conflicto.
#
# Los tres casos de abajo son de CAJA NEGRA (solo subprocess sobre el CLI del
# repo; el módulo nunca se importa y la implementación nunca se lee) y derivan
# del contrato (INV-3/PD-4/PD-5/PD-6 y la condición de cierre 1 de B1), no de
# la implementación.


def write_state(fx: Fixture, state: dict) -> None:
    """Escritura del state por el lado ORQUESTADOR del fixture (dispositivo ya
    usado por los focales vigentes del epic: `active_packet.status =
    "completed"` en tests/test_005_001_t4_decisive.py)."""
    (fx.root / STATE_REL).write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")


def complete_active_packet(fx: Fixture) -> None:
    """Transición declarada del ORQUESTADOR entre subetapas: el paquete activo
    se completa y el state queda listo para la generación siguiente (necesaria
    para que la segunda corrida de `prepare` llegue a la publicación; sin ella
    el CLI responde rc=2 «active packet … is 'prepared'»)."""
    state = fx.state()
    assert (state.get("active_packet") or {}).get("id"), (
        "precondición (fixture): debe existir un paquete activo")
    state["active_packet"]["status"] = "completed"
    write_state(fx, state)


def restore_active_packet(fx: Fixture, active_packet: dict) -> None:
    """Restituye el binding del paquete registrado (el `active_packet`
    dispatched que el fixture guardó) para observar que el paquete viejo sigue
    siendo el registrado."""
    state = fx.state()
    state["active_packet"] = active_packet
    write_state(fx, state)


def edit_active_unit_scope(fx: Fixture) -> None:
    """Edita el ALCANCE de la fila de la unidad activa (parte `unit`), como en
    el tramo 2 de AC-5: la proyección VIVA cambia. Sin esta edición los bytes
    regenerados serían idénticos y la identidad byte a byte no probaría nada."""
    path = fx.root / PLAN_REL
    text = path.read_text(encoding="utf-8")
    old = unit_row(plain_cell())
    assert old in text, (
        "precondición (fixture): la fila de la unidad activa debe existir")
    edited = text.replace(old, unit_row(plain_cell() + " (alcance editado)"), 1)
    assert edited != text, (
        "precondición (fixture): la edición debe cambiar los bytes del plan")
    path.write_text(edited, encoding="utf-8")


def make_custom_out_dir(fx: Fixture, name: str = "custom-out") -> Path:
    """`--out-dir` custom VACÍO: la numeración del `packet_id` se acuña contra
    él, así que con el directorio vacío vuelve a ser el `-001`."""
    out = fx.base / name
    out.mkdir(parents=True, exist_ok=True)
    return out


def test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes(
        fx: Fixture) -> None:
    """B1 (INV-3/PD-4; condición de cierre 1): con un paquete YA PUBLICADO en
    el directorio por defecto (su `UNIT-CONTRACT.md` y su `REQUEST.json` con el
    pin) y una segunda corrida de `prepare` con `--out-dir` a un directorio
    custom VACÍO —de modo que el `packet_id` acuñado sea el MISMO que el del
    paquete existente— `prepare` debe FALLAR CERRADO (rc!=0) con un diagnóstico
    que NOMBRE el paquete en conflicto, y los bytes del `UNIT-CONTRACT.md` del
    paquete viejo deben quedar BYTE-IDÉNTICOS (sha256 antes == sha256 después).

    RED hoy (medido): la colisión REESCRIBE la proyección publicada y devuelve
    rc=0 sin nombrar ningún paquete en conflicto → fallan las tres aserciones.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    projection = fx.unit_contract_path(packet_id)
    sha_before = sha256_bytes(projection.read_bytes())
    request_before = (fx.packet_dir(packet_id) / "REQUEST.json").read_bytes()

    edit_active_unit_scope(fx)
    complete_active_packet(fx)

    custom_out = make_custom_out_dir(fx)
    assert list(custom_out.iterdir()) == [], (
        "precondición (fixture): el `--out-dir` custom debe estar VACÍO (el "
        "`packet_id` acuñado vuelve a ser el `-001` del paquete ya publicado)")

    proc = fx.run(
        PACKET_CLI, "prepare", "--project-root", str(fx.root),
        "--role", "architect", "--substage", "discovery",
        "--objective", "005-013 T1 B1 colision", "--out-dir", str(custom_out))
    sha_after = sha256_bytes(projection.read_bytes())

    assert proc.returncode != 0, (
        "INV-3/PD-4 violadas (B1): `prepare` con `--out-dir` custom NO debe "
        "reescribir la proyección de un paquete ya publicado: debe fallar "
        "cerrado (rc!=0) nombrando el paquete en conflicto. "
        f"rc={proc.returncode} stdout={proc.stdout[:200]!r} "
        f"stderr={proc.stderr[:400]!r} "
        f"sha256(proyección) antes={sha_before} después={sha_after}")
    assert packet_id in proc.stderr, (
        "B1: el diagnóstico de la falla cerrada debe NOMBRAR el paquete en "
        f"conflicto ({packet_id!r}): stderr={proc.stderr[:400]!r}")
    assert sha_after == sha_before, (
        "INV-3 violada (B1): los bytes de una proyección publicada quedan byte "
        "a byte idénticos (sha256 antes == sha256 después); el paquete viejo "
        f"pasó de {sha_before} a {sha_after}")
    assert (fx.packet_dir(packet_id) / "REQUEST.json").read_bytes() == request_before, (
        "PD-4 violada (B1): el paquete viejo (su `REQUEST.json` con el pin) no "
        "debe tocarse")


def test_b1_collision_leaves_the_old_packet_valid_and_receivable(
        fx: Fixture) -> None:
    """B1 (INV-3/PD-4/PD-6; condición de cierre 1): tras el intento de colisión
    fallido, el paquete viejo sigue siendo el registrado y utilizable: su
    `contract.sha256` sigue coincidiendo con el archivo de la proyección y
    `receive` sigue dando lo que daba antes (rc=0 con `packet_validation` /
    `identity_validation` `passed` y `semantic_status: pending`, porque el
    paquete estaba despachado).

    Dispositivo del fixture (declarado): el paquete viejo se despacha; para que
    la segunda corrida de `prepare` llegue a la publicación el state pasa por la
    transición del orquestador, y antes de ejercitar `receive` se restituye el
    binding del paquete registrado (su `active_packet` dispatched).

    RED hoy (medido): la colisión reescribe la proyección del paquete viejo, su
    `contract.sha256` durable deja de coincidir con el archivo y `receive`
    responde rc=2 («contract sha256 does not match exact content») → el paquete
    queda irrecebible.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    fx.dispatch_ok(packet_id)
    active_before = fx.state()["active_packet"]

    edit_active_unit_scope(fx)
    complete_active_packet(fx)
    custom_out = make_custom_out_dir(fx)
    fx.run(
        PACKET_CLI, "prepare", "--project-root", str(fx.root),
        "--role", "architect", "--substage", "discovery",
        "--objective", "005-013 T1 B1 colision", "--out-dir", str(custom_out))

    restore_active_packet(fx, active_before)

    contract = fx.request(packet_id)["contract"]
    sha_file = sha256_bytes(fx.unit_contract_path(packet_id).read_bytes())
    assert contract["sha256"] == sha_file, (
        "INV-3/PD-4 violadas (B1): el `contract.sha256` durable del paquete "
        "viejo debe seguir coincidiendo con los bytes de su proyección: "
        f"{contract['sha256']!r} != {sha_file!r}")

    recv = fx.receive(packet_id)
    assert recv.returncode == 0, (
        "PD-6 violada (B1): el paquete viejo debe seguir siendo recebible "
        "(valida contra la proyección registrada, no contra la reescrita): "
        f"rc={recv.returncode} stdout={recv.stdout[:200]!r} "
        f"stderr={recv.stderr[:300]!r}")
    receipt = json.loads(recv.stdout)
    assert receipt.get("packet_validation") == "passed", (
        f"PD-6 violada (B1): `packet_validation` debe ser `passed`: {receipt!r}")
    assert receipt.get("identity_validation") == "passed", (
        f"PD-6 violada (B1): `identity_validation` debe ser `passed`: {receipt!r}")
    assert receipt.get("semantic_status") == "pending", (
        "PD-6 violada (B1): recibir NO aprueba (`semantic_status: pending`): "
        f"{receipt.get('semantic_status')!r}")


def test_b1_no_collision_with_custom_out_dir_still_publishes(
        fx: Fixture) -> None:
    """Control de B1 (PD-4/PD-5): con un `--out-dir` custom VACÍO y NINGÚN
    paquete con ese `packet_id` en el directorio por defecto, `prepare` rc=0 y
    la proyección se publica en la ruta canónica
    (`.cdad/packets/<packet_id>/UNIT-CONTRACT.md`), con
    `sha256(UNIT-CONTRACT.md) == contract.sha256 ==
    active_packet.contract_sha256`; el paquete (PACKET.md + REQUEST.json) queda
    en el directorio custom. Evita que la corrección de B1 rompa el camino sin
    colisión.

    El fixture publica primero un paquete de OTRA subetapa (draft) con el
    directorio por defecto, de modo que `.cdad` existe y el `packet_id` de la
    subetapa `discovery` (el `-001` acuñado contra el `--out-dir` vacío) NO
    existe en el directorio por defecto.

    RED hoy (medido): `prepare` rc=2 («cannot write prepared packet: [Errno 2]
    … extra-000 -> …/UNIT-CONTRACT.md») porque el commit de la proyección asume
    que el directorio del paquete ya existe en la ruta canónica.
    """
    fx.prepare_ok(substage="draft")
    draft_packet_id = fx.packet_id()
    complete_active_packet(fx)

    custom_out = make_custom_out_dir(fx)
    assert list(custom_out.iterdir()) == [], (
        "precondición (fixture): el `--out-dir` custom debe estar VACÍO")
    proc = fx.run(
        PACKET_CLI, "prepare", "--project-root", str(fx.root),
        "--role", "architect", "--substage", "discovery",
        "--objective", "005-013 T1 B1 control", "--out-dir", str(custom_out))
    assert proc.returncode == 0, (
        "PD-4/PD-5 violadas (control de B1): sin colisión, `prepare` con "
        "`--out-dir` custom debe publicar el paquete y su proyección (rc=0): "
        f"rc={proc.returncode} stdout={proc.stdout[:200]!r} "
        f"stderr={proc.stderr[:400]!r}")

    packet_id = fx.packet_id()
    assert packet_id != draft_packet_id, (
        "precondición (fixture): el paquete nuevo es de otra subetapa "
        f"({draft_packet_id!r})")
    text = fx.unit_contract_text(packet_id)
    assert unit_block() in text, (
        "PD-1 violada (control de B1): la proyección publicada debe ser la "
        f"proyección de la unidad: {unit_block()!r} no aparece en {text!r}")
    request = json.loads(
        (custom_out / packet_id / "REQUEST.json").read_text(encoding="utf-8"))
    contract = request["contract"]
    assert contract["kind"] == CONTRACT_KIND_PROJECTION, (
        f"PD-4 violada (control de B1): {contract!r}")
    assert contract["path"] == f".cdad/packets/{packet_id}/UNIT-CONTRACT.md", (
        f"PD-4 violada (control de B1): {contract['path']!r}")
    assert contract["sha256"] == sha256_bytes(
        fx.unit_contract_path(packet_id).read_bytes()), (
        "PD-4 violada (control de B1): el pin debe ser el digest de la "
        "proyección publicada")
    assert fx.state()["active_packet"]["contract_sha256"] == contract["sha256"], (
        "PD-4 violada (control de B1): el binding del state debe coincidir con "
        "el pin")
    for name in ("PACKET.md", "REQUEST.json"):
        assert (custom_out / packet_id / name).is_file(), (
            "control de B1: el paquete debe quedar en el `--out-dir` custom "
            f"({(custom_out / packet_id / name).relative_to(fx.base)})")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))