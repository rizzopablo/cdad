#!/usr/bin/env python3
"""RED 006-006 W-1 (E4/W-1) — el paquete de revisión de BORRADOR preparado y
nunca despachado se puede reemplazar.

Hallazgo W-1 (recorrido U6, `docs/specs/006-006-spec-plan-review/u6-acceptance.md`
fila E4 y tabla de hallazgos):

    Con un paquete `reviewer`/`plan-review` sobre un contrato `draft-plan`
    PREPARADO y no despachado, `prepare --replace-packet <id> --reason <r>`
    falla con «plan-review subphase requires a draft-plan contract: an
    approved contract is not the object this procedure reviews (PD-2)», y
    `register-transition --transition disposition` lo rechaza por no
    despachado. Tras editar el borrador, el usuario queda SIN SALIDA para
    preparar la re-review focal (E4: «la re-review tras la corrección es
    focal y verificable»).

Contrato:

- `docs/specs/006-006-spec-plan-review/spec.md` §3.1 fila **E4** (la
  re-review focal tras la corrección es exigible) y §3 PD-2/PD-8/PD-13/PD-15
  (la forma se declara, la re-review es focal, el recorrido es real, los
  guardas vigentes siguen verdes).
- El contrato VIGENTE de `--replace-packet` (005-001 T2, PD-7..PD-11, PD-16)
  y su conservación (005-005): reemplazar un paquete **preparado, nunca
  despachado y obsoleto**, con **razón obligatoria**, sin efectos cuando se
  rechaza, y sin tocar la autorización (INV-2).

Superficie observable bajo prueba (CAJA NEGRA: el CLI se invoca como
subproceso; el código de implementación NUNCA se lee):

    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare \\
        --project-root <PROY> --role reviewer --substage plan-review \\
        --objective <obj> --contract-kind draft-plan \\
        --contract-path <borrador> --plan-version <v> \\
        [--object-kind spec|plan] [--spec-path <spec> --spec-version <v>]
    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare \\
        --project-root <PROY> --replace-packet <id> --reason <texto>
    python3 skills/cdad-cycle/scripts/cdad_packet.py validate-packet ...

El sub-modo `--replace-packet` admite **argv puro** (ninguna opción de otro
sub-modo: `--out-dir` y `--execution-context` se rechazan), y por eso la
fixture usa el directorio POR DEFECTO (`.cdad/packets`) y deja el contexto
de ejecución en su ruta canónica: es la forma en que el orquestador invoca
el reemplazo.

Fixture: proyecto **descartable** en un tempdir (política válida, spec
aprobada y pineada, autoridad HITL vigente, ejecución v2 real creada por el
CLI) con un `HOME` vacío en el subproceso (nunca el HOME real, nunca este
repo). Los borradores son fixtures PROPIOS de este archivo (no se reusa el
`DRAFT_PLAN_RELPATH` compartido). Ninguna mutación toca el state de este
repo. No hay mocks sobre el plumbing.

ORÁCULOS DECLARADOS (interfaces que fija este RED, derivadas del contrato):

1. El reemplazo de un paquete de revisión de borrador **preparado y no
   despachado** tiene **rc=0** y publica un **paquete nuevo** (id siguiente
   libre) cuyo contrato es el **borrador del día** con su **digest nuevo**;
   el paquete anterior queda **intacto** (INV-3) y recibe el registro durable
   de superación (`.superseded.json`: `superseded_by`, `reason`,
   `superseded_at`, `contract_sha256_old`, `contract_sha256_new`); el
   `active_packet` apunta al nuevo con `status: "prepared"`; la identidad se
   reusa (rol, subfase, objetivo, `execution_id`); `stage_history` y
   `epic_history` **no** cambian (INV-2: el reemplazo no autoriza nada); y
   stdout es el `PACKET.md` publicado (INV-5). El paquete nuevo es además un
   paquete **válido** (`validate-packet` rc=0): es el «prepare nuevo de
   plan-review sobre los bytes editados» que la re-review focal necesita.
2. El reemplazo **no cambia la forma** del objeto revisado: el `kind`
   (`draft-plan`), la ruta del principal, la versión y la **forma declarada**
   (`object_kind`) se conservan, y el acompañante (cuando lo hay) sigue
   viajando con su digest, calculado de los bytes del archivo.
3. El reemplazo **no convierte el borrador en un contrato aprobado**: el
   `kind` del paquete nuevo sigue siendo `draft-plan`, el `active_packet`
   declara `contract_kind: "draft-plan"` y el `stage_history` no gana ninguna
   entrada de aprobación.
4. Los **rechazos vigentes** del reemplazo se conservan: un paquete ya
   **despachado** se rechaza (rc≠0, marcador `packet obsolete`, sin
   efectos) y `--replace-packet` **sin razón** se rechaza (rc≠0, sin
   efectos).
5. **CONTROL**: el reemplazo sobre un contrato **aprobado** sigue igual que
   hoy (rc=0, sucesor publicado, registro de superación) y el guard vigente
   «`plan-review` sobre un kind aprobado ⇒ rechazo» sigue verde.

DECLARACIÓN A-1 (no se congela ningún oráculo vigente):

- Este RED **NO REEMPLAZA** ningún oráculo: los ficheros de 005-001 T2
  (`tests/test_005_001_t2_replace_packet.py`), 005-005, 004-003 T1/T2 y el
  focal `tests/test_006_006_u1_draft_object_form.py` se EJECUTAN como
  regresiones y no se tocan.
- El control del punto 5 afirma el rechazo del `plan-review` sobre un kind
  aprobado **por su efecto** (rc≠0, sin publicación, state byte a byte
  idéntico) y **NO** por su texto: el diagnóstico vigente de ese rechazo
  («plan-review subphase requires a draft-plan contract…») **es el mismo
  texto** que el rechazo que hoy bloquea el caso de este RED, y fijarlo
  sería congelar el defecto (A-1). El RED afirma, en cambio, que ese texto
  **deja de ser** el resultado del reemplazo de un borrador: el rc del
  reemplazo es 0.
- Los rechazos que este RED sí fija (marcador `packet obsolete` del paquete
  despachado, rc≠0 sin razón) son **rechazos vigentes** que el caso de W-1
  NO toca: se comprueban para que el arreglo no los relaje.

Mapeo test → postcondición:

  test_w1_e4_a_prepared_draft_review_packet_can_be_replaced
      -> E4/W-1 + PD-2/PD-13: el reemplazo del paquete de revisión de
         borrador preparado y no despachado tiene rc=0 y publica el paquete
         nuevo sobre los bytes editados (digest nuevo), con el registro
         durable de superación, el anterior intacto, sin tocar la
         autorización y con stdout = PACKET.md publicado.
  test_w1_e4_the_replacement_keeps_the_declared_form_of_the_reviewed_object
      -> E4/W-1 + PD-2 (R-7/R-8): la forma declarada (aquí `plan`, con
         spec acompañante) y la versión no cambian en el reemplazo; sólo
         cambia el digest del documento editado, y el acompañante sigue
         declarándose con el digest de sus bytes.
  test_w1_e4_the_replacement_does_not_authorize_the_draft
      -> E4/W-1 + INV-2/PD-7: el reemplazo no convierte el borrador en un
         contrato aprobado ni inventa una aprobación.
  test_w1_e4_the_vigente_rejections_of_the_replacement_are_conserved
      -> 005-001 PD-9/PD-10 (vigentes, conservados): paquete despachado ⇒
         rechazo con marcador `packet obsolete`; sin `--reason` ⇒ rechazo;
         ambos sin efectos.
  test_w1_e4_control_the_replacement_over_an_approved_contract_is_unchanged
      -> 005-001 PD-7 (control): el reemplazo sobre un contrato aprobado se
         comporta igual que hoy; y el guard vigente «`plan-review` sobre un
         kind aprobado ⇒ rechazo» sigue verde (efecto, no texto — A-1).
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
# El CLI DEL PRODUCTO (la copia que `install.sh` instala). Se INVOCA; su
# código nunca se lee (INVARIANTE: «Do not read implementation code»).
PRODUCT_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"

EPIC_ID = "epic-006-opencode-concurrency"
FEATURE_ID = "006-006-w1-fixture"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"

# El contrato APROBADO por omisión del rol reviewer (el que el sub-modo de
# reemplazo re-resuelve hoy: ése es el defecto de W-1).
APPROVED_SPEC = f"docs/specs/{FEATURE_ID}/spec.md"

# Los BORRADORES revisados (fixtures PROPIOS de este archivo).
DRAFT_SPEC = "docs/drafts/006-006-w1-spec-draft.md"
DRAFT_PLAN = "docs/drafts/006-006-w1-plan-draft.md"
COMPANION_SPEC = "docs/drafts/006-006-w1-companion-spec.md"

DRAFT_VERSION = "draft-001"
COMPANION_VERSION = "companion-001"

# Los bytes revisados: v1 (los que se revisan) y v2 (los editados, sobre los
# que se pide la re-review focal).
DRAFT_SPEC_V1 = b"# 006-006 W-1 - borrador de spec (fixture propia)\n\ncontenido v1\n"
DRAFT_SPEC_V2 = b"# 006-006 W-1 - borrador de spec (fixture propia)\n\ncontenido v2 editado\n"
COMPANION_V1 = b"# 006-006 W-1 - spec acompanante (fixture propia)\n\nacompanante v1\n"
COMPANION_V2 = b"# 006-006 W-1 - spec acompanante (fixture propia)\n\nacompanante v2 editado\n"

# Un plan con el bloque `plan-tasks` que las reglas vigentes exigen (checks
# estructurales y por tarea). Los bytes de v2 cambian el texto del plan, no
# su forma: sigue siendo un plan válido.
_PLAN_TASKS = [
    {
        "id": "w1",
        "consume": [],
        "produce": [{"artifact": "contract-w1", "contract": "w1-v1"}],
        "depends_on": [],
        "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
        "focal_tests": ["tests/test_006_006_w1_replace_draft_packet.py"],
        "regressions": ["tests/test_005_001_t2_replace_packet.py"],
        "integration_gate": "make validate",
        "owner": "RED: test-writer; GREEN: implementer",
    },
    {
        "id": "w1b",
        "consume": [{"artifact": "contract-w1", "producer": "w1", "contract": "w1-v1"}],
        "produce": [],
        "depends_on": ["w1"],
        "files": [],
        "observable_checks": ["el reemplazo publica el paquete sobre los bytes editados"],
        "regressions": [],
        "integration_gate": "make validate",
        "owner": "RED: test-writer; GREEN: implementer",
    },
]


def _plan_bytes(text: str) -> bytes:
    return (
        f"# 006-006 W-1 - borrador de plan (fixture propia)\n\n{text}\n\n```plan-tasks\n".encode()
        + json.dumps({"tasks": _PLAN_TASKS}, indent=2, sort_keys=True).encode()
        + b"\n```\n"
    )


DRAFT_PLAN_V1 = _plan_bytes("contenido v1")
DRAFT_PLAN_V2 = _plan_bytes("contenido v2 editado")

APPROVED_SPEC_V1 = b"# 006-006 W-1 - spec aprobada (fixture propia)\n"
APPROVED_SPEC_V2 = b"# 006-006 W-1 - spec aprobada (fixture propia)\neditada\n"

REASON = "el borrador se edito: la revision anterior no cubre los bytes nuevos"
PACKET_BEGIN = "---cdad-packet-json"
OBSOLETE_MARKER = "packet obsolete"
SUPERSEDED_FILE = ".superseded.json"


# ------------------------------------------------------------------ helpers


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        snapshot[rel] = path.read_bytes() if path.is_file() else None
    return snapshot


def state_bytes(root: Path) -> bytes:
    return (root / STATE_FILE).read_bytes()


def read_state(root: Path) -> dict:
    return json.loads(state_bytes(root).decode("utf-8"))


def packet_dir(root: Path, packet_id: str) -> Path:
    return root / ".cdad" / "packets" / packet_id


def packet_ids(root: Path) -> list[str]:
    base = root / ".cdad" / "packets"
    if not base.is_dir():
        return []
    return sorted(d.name for d in base.iterdir() if d.is_dir())


def packet_bytes(root: Path, packet_id: str, name: str) -> bytes:
    return (packet_dir(root, packet_id) / name).read_bytes()


def request_of(root: Path, packet_id: str) -> dict:
    return json.loads(packet_bytes(root, packet_id, "REQUEST.json").decode("utf-8"))


def execution_context_path(root: Path) -> Path:
    execution = read_state(root)["execution"]
    return root / ".cdad" / "executions" / execution["id"] / "execution.json"


def _without_digests(contract: dict) -> dict:
    """El contrato declarado sin los digests de los documentos: el resto es
    la FORMA del objeto revisado (kind, ruta, versión, forma declarada,
    acompañante) y no puede cambiar en el reemplazo."""
    return {k: v for k, v in contract.items() if k not in ("sha256", "spec_sha256")}


# ------------------------------------------------------------------ fixture


class W1Case(unittest.TestCase):
    """Proyecto descartable: política, spec aprobada y pineada, autoridad
    HITL vigente y estado inicial. El `HOME` del subproceso es un tempdir
    VACÍO (nunca el HOME real)."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._projects = 0

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-006-006-w1-")
        self.addCleanup(self._tmp.cleanup)
        self.home = Path(tempfile.mkdtemp(prefix="cdad-006-006-w1-home-"))
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        return subprocess.run(
            [sys.executable, str(PRODUCT_CLI), *args],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
            check=False,
        )

    def make_project(self) -> Path:
        self._projects += 1
        root = Path(self._tmp.name) / f"proj-{self._projects}"
        for rel in ("tests", "src", "lib", "docs"):
            (root / rel).mkdir(parents=True, exist_ok=True)
        (root / POLICY_FILE).write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "path_policy": {
                        "test_roots": ["tests"],
                        "implementation_roots": ["src", "lib"],
                        "documentation_roots": ["docs"],
                    },
                    "temporary_roots": [".cdad/tmp"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        approved = root / APPROVED_SPEC
        approved.parent.mkdir(parents=True, exist_ok=True)
        approved.write_bytes(APPROVED_SPEC_V1)
        authority = root / AUTHORITY_REF
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Autoridad de ejecucion (fixture 006-006 W-1)\n", encoding="utf-8")
        state = {
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
            "stage_history": [
                {
                    "feature": FEATURE_ID,
                    "stage": "specification",
                    "approved_by": "Owner Fixture",
                    "approved_at": "2026-10-20T00:00:00Z",
                    "contract_path": APPROVED_SPEC,
                    "contract_sha256": hashlib.sha256(APPROVED_SPEC_V1).hexdigest(),
                }
            ],
            "approver": "Owner Fixture",
            "last_updated": "2026-10-20T00:00:00Z",
            "execution": None,
            "active_packet": None,
            "hitl_delegation": {
                "status": "active",
                "epic_id": EPIC_ID,
                "source": AUTHORITY_REF,
                "scope": EPIC_ID,
                "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
            },
        }
        (root / STATE_FILE).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return root

    # -- documents --------------------------------------------------------

    @staticmethod
    def write(root: Path, relpath: str, data: bytes) -> None:
        target = root / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    # -- invocations ------------------------------------------------------

    def prepare_review(
        self,
        root: Path,
        *,
        contract_path: str,
        plan_version: str = DRAFT_VERSION,
        object_kind: str | None = "spec",
        companion: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        """La revisión de un borrador: kind `draft-plan` sobre el documento
        declarado, con su forma declarada."""
        args = [
            "prepare",
            "--project-root",
            str(root),
            "--role",
            "reviewer",
            "--substage",
            "plan-review",
            "--objective",
            "revisar el borrador (fixture W-1)",
            "--contract-kind",
            "draft-plan",
            "--contract-path",
            contract_path,
            "--plan-version",
            plan_version,
        ]
        if object_kind is not None:
            args += ["--object-kind", object_kind]
        if companion:
            args += ["--spec-path", COMPANION_SPEC, "--spec-version", COMPANION_VERSION]
        return self.run_cli(*args)

    def prepare_review_over_approved_kind(self, root: Path) -> subprocess.CompletedProcess[str]:
        """La MISMA subfase de revisión sobre el contrato APROBADO por
        omisión (kind `approved-feature-spec`): el guard vigente de 006-006
        (PD-15, guard 2) lo rechaza."""
        return self.run_cli(
            "prepare",
            "--project-root",
            str(root),
            "--role",
            "reviewer",
            "--substage",
            "plan-review",
            "--objective",
            "revisar el contrato aprobado (fixture W-1)",
        )

    def replace(self, root: Path, packet_id: str, *, reason: str | None = REASON):
        """El sub-modo de reemplazo, con argv PURO (ninguna opción de otro
        sub-modo: es la forma en que el orquestador lo invoca)."""
        args = ["prepare", "--project-root", str(root), "--replace-packet", packet_id]
        if reason is not None:
            args += ["--reason", reason]
        return self.run_cli(*args)

    def dispatch(self, root: Path, packet_id: str) -> subprocess.CompletedProcess[str]:
        """Precondición `dispatched` por vía PÚBLICA (`--record-dispatch`)."""
        observation = root / "docs" / "dispatch-observation.json"
        observation.parent.mkdir(parents=True, exist_ok=True)
        observation.write_text(
            json.dumps(
                {
                    "runtime": "opencode",
                    "model_configured": "fixture-model",
                    "model_reported": "fixture-model",
                    "session": "ses-006-006-w1-fixture-001",
                    "started_at": "2026-10-20T00:00:00Z",
                    "provenance": {
                        "runtime": "reported by runtime",
                        "model_reported": "orchestrator",
                        "session": "orchestrator",
                    },
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return self.run_cli(
            "prepare",
            "--project-root",
            str(root),
            "--record-dispatch",
            packet_id,
            "--attempt-id",
            "att-w1-fixture",
            "--input",
            str(observation),
        )

    # -- assertions -------------------------------------------------------

    def assert_no_effects(self, root: Path, label: str, before: dict, state_before: bytes) -> None:
        self.assertEqual(tree_snapshot(root), before, f"{label}: hubo escrituras (árbol modificado)")
        self.assertEqual(state_bytes(root), state_before, f"{label}: el state cambió")
        for pid in packet_ids(root):
            self.assertFalse(
                (packet_dir(root, pid) / SUPERSEDED_FILE).is_file(),
                f"{label}: quedó un registro de superación con rc≠0 ({SUPERSEDED_FILE} en {pid})",
            )

    def assert_behavioural_rejection(
        self, root: Path, label: str, before: dict, state_before: bytes, proc
    ) -> str:
        """Un rechazo COMPORTAMENTAL (no un error de uso): rc≠0, stdout vacío,
        sin traceback, y sin efectos."""
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized arguments",
            out,
            f"{label}: el CLI no conoce la superficie invocada — un error de uso "
            f"no es un rechazo comportamental: {out!r}",
        )
        self.assertNotEqual(proc.returncode, 0, f"{label}: se esperaba un rechazo: {out!r}")
        self.assertEqual(proc.stdout, "", f"{label}: el rechazo imprimió contenido por stdout")
        self.assertNotIn("Traceback", proc.stderr, f"{label}: fallo con traceback: {proc.stderr!r}")
        self.assert_no_effects(root, label, before, state_before)
        return proc.stderr


# ------------------------------------------------------------------ the RED


class TestW1ReplaceThePreparedDraftPacket(W1Case):
    """E4/W-1: el paquete de revisión de borrador preparado y no despachado
    se puede reemplazar (forma `spec`)."""

    def prepared_review(self) -> tuple[Path, str, dict]:
        root = self.make_project()
        self.write(root, DRAFT_SPEC, DRAFT_SPEC_V1)
        proc = self.prepare_review(root, contract_path=DRAFT_SPEC, object_kind="spec")
        self.assertEqual(
            proc.returncode,
            0,
            "precondición (fixture): la revisión del borrador debe publicarse: "
            + proc.stderr,
        )
        active = read_state(root)["active_packet"]
        self.assertEqual(active.get("status"), "prepared", f"precondición (fixture): {active!r}")
        return root, active["id"], active

    def test_w1_e4_a_prepared_draft_review_packet_can_be_replaced(self) -> None:
        """E4/W-1: `prepare --replace-packet <id> --reason <texto>` sobre un
        paquete de revisión de borrador PREPARADO y no despachado tiene
        **rc=0** y publica un paquete NUEVO sobre los bytes EDITADOS (digest
        nuevo); el anterior queda intacto con su registro durable de
        superación; el `active_packet` apunta al nuevo; la autorización no se
        toca; y stdout es el `PACKET.md` publicado."""
        root, pid, _ = self.prepared_review()
        old_packet_md = packet_bytes(root, pid, "PACKET.md")
        old_request_bytes = packet_bytes(root, pid, "REQUEST.json")
        old_request = json.loads(old_request_bytes.decode("utf-8"))
        old_digest = old_request["contract"]["sha256"]

        # La corrección del arquitecto: los bytes del borrador cambian.
        self.write(root, DRAFT_SPEC, DRAFT_SPEC_V2)
        new_digest = hashlib.sha256(DRAFT_SPEC_V2).hexdigest()
        self.assertNotEqual(new_digest, old_digest, "fixture: el borrador no cambió")

        state_pre = read_state(root)

        proc = self.replace(root, pid)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized arguments",
            out,
            f"E4/W-1: la superficie --replace-packet debe reconocerse: {out!r}",
        )
        self.assertEqual(
            proc.returncode,
            0,
            "E4/W-1: el paquete de revisión de borrador preparado y no "
            "despachado debe poder reemplazarse (E4: la re-review focal tras "
            "la corrección es exigible); hoy el reemplazo falla: " + out,
        )
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            f"E4/W-1: stdout no comienza con el paquete canónico: {out!r}",
        )

        # El paquete NUEVO existe y es el que lleva los bytes editados.
        packets_after = packet_ids(root)
        self.assertIn(pid, packets_after, "E4/W-1/INV-3: el paquete anterior desapareció del disco")
        successors = [p for p in packets_after if p != pid]
        self.assertEqual(len(successors), 1, f"E4/W-1: paquetes en disco tras el reemplazo: {packets_after}")
        new_id = successors[0]
        match = re.match(r"^(.*-)(\d{3})$", pid)
        self.assertIsNotNone(match, f"fixture: esquema de id inesperado: {pid!r}")
        expected_next = f"{match.group(1)}{int(match.group(2)) + 1:03d}"
        self.assertEqual(
            new_id,
            expected_next,
            f"E4/W-1: se esperaba el id siguiente libre ({expected_next!r}) y se "
            f"publicó {new_id!r}",
        )

        # INV-3: los bytes del paquete anterior intactos.
        self.assertEqual(
            packet_bytes(root, pid, "PACKET.md"), old_packet_md, "E4/W-1/INV-3: PACKET.md del anterior cambió"
        )
        self.assertEqual(
            packet_bytes(root, pid, "REQUEST.json"),
            old_request_bytes,
            "E4/W-1/INV-3: REQUEST.json del anterior cambió",
        )

        # El contrato del día: el BORRADOR con su digest NUEVO.
        new_request = request_of(root, new_id)
        new_contract = new_request.get("contract", {})
        self.assertEqual(
            new_contract.get("sha256"),
            new_digest,
            "E4/W-1: el paquete nuevo no lleva el digest de los bytes "
            f"editados ({new_digest[:12]}…): {json.dumps(new_contract)!r}",
        )
        self.assertEqual(
            new_contract.get("path"),
            DRAFT_SPEC,
            f"E4/W-1: el paquete nuevo no lleva la ruta del borrador editado: {new_contract!r}",
        )
        self.assertEqual(
            new_contract.get("kind"),
            "draft-plan",
            f"E4/W-1: el paquete nuevo no conserva el kind del borrador: {new_contract!r}",
        )

        # La identidad se reusa (rol, subfase, objetivo, ejecución).
        self.assertEqual(new_request.get("role"), old_request.get("role"), "E4/W-1: la identidad (role) no se reusó")
        self.assertEqual(
            new_request.get("substage"), old_request.get("substage"), "E4/W-1: la identidad (substage) no se reusó"
        )
        self.assertEqual(
            new_request.get("objective"),
            old_request.get("objective"),
            "E4/W-1: la identidad (objective) no se reusó",
        )
        self.assertEqual(
            new_request.get("execution_id"),
            old_request.get("execution_id"),
            "E4/W-1: la identidad (execution_id) no se reusó",
        )

        # El `active_packet` apunta al nuevo, `prepared`, con el digest del día.
        state_after = read_state(root)
        active = state_after.get("active_packet") or {}
        self.assertEqual(active.get("id"), new_id, f"E4/W-1: active_packet no apunta al paquete nuevo: {active!r}")
        self.assertEqual(active.get("status"), "prepared", f"E4/W-1: el paquete nuevo no quedó `prepared`: {active!r}")
        self.assertEqual(
            active.get("contract_sha256"),
            new_digest,
            f"E4/W-1: active_packet no lleva el digest del día: {active!r}",
        )
        self.assertEqual(
            state_after.get("execution"), state_pre.get("execution"), "E4/W-1: la identidad de ejecución cambió"
        )

        # El registro durable de superación en el directorio del anterior.
        superseded_path = packet_dir(root, pid) / SUPERSEDED_FILE
        self.assertTrue(
            superseded_path.is_file(),
            f"E4/W-1: no quedó registro durable {SUPERSEDED_FILE} en el paquete anterior",
        )
        record = json.loads(superseded_path.read_text(encoding="utf-8"))
        self.assertEqual(
            record.get("superseded_by"), new_id, f"E4/W-1: superseded_by no nombra al paquete nuevo: {record!r}"
        )
        self.assertEqual(
            record.get("reason"), REASON, f"E4/W-1: reason no es el motivo de --reason: {record!r}"
        )
        self.assertTrue(record.get("superseded_at"), f"E4/W-1: superseded_at vacío: {record!r}")
        self.assertEqual(
            record.get("contract_sha256_old"),
            old_digest,
            f"E4/W-1: contract_sha256_old no es el sha registrado: {record!r}",
        )
        self.assertEqual(
            record.get("contract_sha256_new"),
            new_digest,
            f"E4/W-1: contract_sha256_new no es el sha actual: {record!r}",
        )

        # INV-2: el reemplazo NO autoriza nada.
        self.assertEqual(
            state_after.get("stage_history"),
            state_pre.get("stage_history"),
            "E4/W-1/INV-2: stage_history cambió con el reemplazo",
        )
        self.assertEqual(
            state_after.get("epic_history"),
            state_pre.get("epic_history"),
            "E4/W-1/INV-2: epic_history cambió con el reemplazo",
        )

        # INV-5: stdout es el paquete publicado.
        self.assertEqual(
            proc.stdout,
            packet_bytes(root, new_id, "PACKET.md").decode("utf-8"),
            "E4/W-1/INV-5: stdout difiere del PACKET.md publicado",
        )

        # El paquete nuevo es un paquete VÁLIDO: es el «prepare nuevo de
        # plan-review sobre los bytes editados» que la re-review focal
        # necesita para despacharse.
        validated = self.run_cli(
            "validate-packet",
            "--project-root",
            str(root),
            "--execution-context",
            str(execution_context_path(root)),
            "--request",
            str(packet_dir(root, new_id) / "REQUEST.json"),
            "--packet",
            str(packet_dir(root, new_id) / "PACKET.md"),
        )
        self.assertEqual(
            validated.returncode,
            0,
            "E4/W-1: el paquete nuevo no es un paquete válido (no se podría "
            "despachar la re-review): " + validated.stderr,
        )

    def test_w1_e4_the_replacement_keeps_the_declared_form_of_the_reviewed_object(self) -> None:
        """E4/W-1 + PD-2 (R-7/R-8): con un borrador de forma `plan` y su spec
        acompañante, el reemplazo publica el paquete nuevo sobre los bytes
        EDITADOS del plan, conserva la forma declarada (`plan`), la versión y
        el acompañante (con el digest de SUS bytes); sólo cambia el digest
        del documento principal."""
        root = self.make_project()
        self.write(root, DRAFT_PLAN, DRAFT_PLAN_V1)
        self.write(root, COMPANION_SPEC, COMPANION_V1)
        proc = self.prepare_review(
            root, contract_path=DRAFT_PLAN, object_kind="plan", companion=True
        )
        self.assertEqual(
            proc.returncode,
            0,
            "precondición (fixture): la revisión del plan con acompañante debe "
            "publicarse: " + proc.stderr,
        )
        pid = read_state(root)["active_packet"]["id"]
        old_request = request_of(root, pid)
        old_contract = old_request["contract"]
        old_digest = old_contract["sha256"]

        # La corrección del arquitecto sobre el plan (y sobre el acompañante).
        self.write(root, DRAFT_PLAN, DRAFT_PLAN_V2)
        self.write(root, COMPANION_SPEC, COMPANION_V2)
        new_digest = hashlib.sha256(DRAFT_PLAN_V2).hexdigest()
        new_companion_digest = hashlib.sha256(COMPANION_V2).hexdigest()
        self.assertNotEqual(new_digest, old_digest, "fixture: el plan no cambió")

        replaced = self.replace(root, pid)
        out = replaced.stdout + replaced.stderr
        self.assertEqual(
            replaced.returncode,
            0,
            "E4/W-1: el paquete de revisión de un borrador de forma `plan` "
            "preparado y no despachado debe poder reemplazarse; hoy falla: " + out,
        )

        new_id = [p for p in packet_ids(root) if p != pid][0]
        new_request = request_of(root, new_id)
        new_contract = new_request["contract"]

        # La FORMA no cambia en silencio.
        self.assertEqual(
            new_contract.get("object_kind"),
            old_contract.get("object_kind"),
            f"E4/W-1: el reemplazo cambió la forma declarada del objeto: {new_contract!r}",
        )
        self.assertEqual(
            new_contract.get("kind"),
            "draft-plan",
            f"E4/W-1: el reemplazo cambió el kind del objeto: {new_contract!r}",
        )
        self.assertEqual(
            new_contract.get("path"),
            DRAFT_PLAN,
            f"E4/W-1: el reemplazo cambió la ruta del objeto: {new_contract!r}",
        )
        self.assertEqual(
            new_contract.get("plan_version"),
            old_contract.get("plan_version"),
            f"E4/W-1: el reemplazo cambió la versión del borrador: {new_contract!r}",
        )
        # El digest es el ÚNICO cambio del contrato (junto al digest del
        # acompañante, cuando lo hay: los dos se recalculan de los bytes).
        self.assertEqual(
            new_contract.get("sha256"),
            new_digest,
            f"E4/W-1: el paquete nuevo no lleva el digest de los bytes editados "
            f"del plan: {new_contract!r}",
        )
        self.assertEqual(
            _without_digests(new_contract),
            _without_digests(old_contract),
            "E4/W-1: el reemplazo cambió algo del contrato más allá de los "
            f"digests de los documentos: {new_contract!r} vs {old_contract!r}",
        )

        # El acompañante sigue declarándose, con el digest de SUS bytes.
        self.assertEqual(
            new_contract.get("spec_path"),
            COMPANION_SPEC,
            f"E4/W-1: el reemplazo perdió el acompañante: {new_contract!r}",
        )
        self.assertEqual(
            new_contract.get("spec_version"),
            old_contract.get("spec_version"),
            f"E4/W-1: el reemplazo cambió la versión del acompañante: {new_contract!r}",
        )
        self.assertEqual(
            new_contract.get("spec_sha256"),
            new_companion_digest,
            "E4/W-1: el acompañante no lleva el digest de sus bytes actuales: "
            f"{new_contract!r}",
        )
        # Los `inputs` siguen declarando el objeto completo (principal y
        # acompañante), en el mismo orden.
        self.assertEqual(
            [entry.get("path") for entry in new_request.get("inputs", [])],
            [entry.get("path") for entry in old_request.get("inputs", [])],
            "E4/W-1: los inputs del paquete nuevo no declaran el mismo objeto: "
            f"{new_request.get('inputs')!r} vs {old_request.get('inputs')!r}",
        )

    def test_w1_e4_the_replacement_does_not_authorize_the_draft(self) -> None:
        """E4/W-1 + INV-2/PD-7: el reemplazo NO convierte el borrador en un
        contrato aprobado ni inventa una aprobación: el `kind` del paquete
        nuevo sigue siendo `draft-plan`, el `active_packet` declara el kind
        del borrador, el `stage_history` no gana ninguna entrada y el
        borrador en disco no lo toca el CLI."""
        root = self.make_project()
        self.write(root, DRAFT_SPEC, DRAFT_SPEC_V1)
        proc = self.prepare_review(root, contract_path=DRAFT_SPEC, object_kind="spec")
        self.assertEqual(proc.returncode, 0, "precondición (fixture): " + proc.stderr)
        pid = read_state(root)["active_packet"]["id"]
        self.write(root, DRAFT_SPEC, DRAFT_SPEC_V2)
        state_pre = read_state(root)

        replaced = self.replace(root, pid)
        self.assertEqual(
            replaced.returncode,
            0,
            "E4/W-1: el reemplazo debe tener éxito: " + replaced.stdout + replaced.stderr,
        )

        new_id = [p for p in packet_ids(root) if p != pid][0]
        new_request = request_of(root, new_id)
        self.assertEqual(
            new_request.get("contract", {}).get("kind"),
            "draft-plan",
            "E4/W-1: el paquete nuevo convirtió el borrador en un contrato "
            f"aprobado: {new_request.get('contract')!r}",
        )
        self.assertNotIn(
            "approved-feature-spec",
            json.dumps(new_request.get("contract")),
            "E4/W-1: el contrato del paquete nuevo se aprobó a sí mismo",
        )
        active = read_state(root).get("active_packet") or {}
        self.assertEqual(
            active.get("contract_kind"),
            "draft-plan",
            f"E4/W-1: el active_packet declara un kind aprobado: {active!r}",
        )
        state_after = read_state(root)
        self.assertEqual(
            state_after.get("stage_history"),
            state_pre.get("stage_history"),
            "E4/W-1/INV-2: el reemplazo añadió una entrada al stage_history",
        )
        self.assertEqual(
            (root / DRAFT_SPEC).read_bytes(),
            DRAFT_SPEC_V2,
            "E4/W-1: el CLI modificó el borrador revisado",
        )


class TestW1TheVigenteRejectionsAreConserved(W1Case):
    """Los rechazos VIGENTES del reemplazo (005-001 PD-9/PD-10) se conservan:
    el arreglo de W-1 no los relaja."""

    def test_w1_e4_the_vigente_rejections_of_the_replacement_are_conserved(self) -> None:
        """E4/W-1 + 005-001 PD-9/PD-10 (vigentes, conservados): (a) un paquete
        ya DESPACHADO no se reemplaza (rc≠0, marcador `packet obsolete`, sin
        efectos); (b) `--replace-packet` SIN `--reason` se rechaza (rc≠0, sin
        efectos)."""
        # (a) paquete despachado
        root = self.make_project()
        self.write(root, DRAFT_SPEC, DRAFT_SPEC_V1)
        prepared = self.prepare_review(root, contract_path=DRAFT_SPEC, object_kind="spec")
        self.assertEqual(prepared.returncode, 0, "precondición (fixture): " + prepared.stderr)
        pid = read_state(root)["active_packet"]["id"]
        dispatched = self.dispatch(root, pid)
        self.assertEqual(
            dispatched.returncode,
            0,
            "precondición (fixture): --record-dispatch debe registrar el "
            "intento: " + dispatched.stderr,
        )
        self.assertEqual(
            read_state(root)["active_packet"].get("status"),
            "dispatched",
            "precondición (fixture): el paquete debe quedar `dispatched`",
        )
        self.write(root, DRAFT_SPEC, DRAFT_SPEC_V2)
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc = self.replace(root, pid)
        stderr = self.assert_behavioural_rejection(root, "E4/W-1 (despachado)", before, state_before, proc)
        self.assertIn(
            OBSOLETE_MARKER,
            stderr,
            f"E4/W-1: el rechazo del paquete despachado perdió el marcador "
            f"vigente {OBSOLETE_MARKER!r}: {stderr!r}",
        )
        self.assertIn(
            pid,
            stderr,
            f"E4/W-1: el rechazo del paquete despachado no nombra al paquete: {stderr!r}",
        )

        # (b) sin razón
        root = self.make_project()
        self.write(root, DRAFT_SPEC, DRAFT_SPEC_V1)
        prepared = self.prepare_review(root, contract_path=DRAFT_SPEC, object_kind="spec")
        self.assertEqual(prepared.returncode, 0, "precondición (fixture): " + prepared.stderr)
        pid = read_state(root)["active_packet"]["id"]
        self.write(root, DRAFT_SPEC, DRAFT_SPEC_V2)
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc = self.replace(root, pid, reason=None)
        self.assert_behavioural_rejection(root, "E4/W-1 (sin razón)", before, state_before, proc)


class TestW1ControlOverAnApprovedContract(W1Case):
    """CONTROL: el reemplazo sobre un contrato APROBADO se comporta igual que
    hoy, y el guard vigente «`plan-review` sobre un kind aprobado ⇒ rechazo»
    sigue verde."""

    def test_w1_e4_control_the_replacement_over_an_approved_contract_is_unchanged(self) -> None:
        """E4/W-1 + 005-001 PD-7 (control): con un paquete de construcción
        sobre el contrato APROBADO, editado y re-pineado, el reemplazo tiene
        rc=0, publica el sucesor con el digest del día y deja el registro
        durable de superación; y el guard vigente «`plan-review` sobre un
        kind aprobado ⇒ rechazo» sigue rechazando (por su EFECTO, no por su
        texto — A-1)."""
        # (a) reemplazo sobre contrato aprobado (comportamiento vigente)
        root = self.make_project()
        prepared = self.run_cli(
            "prepare",
            "--project-root",
            str(root),
            "--role",
            "test-writer",
            "--substage",
            "red",
            "--objective",
            "RED del fixture W-1",
        )
        self.assertEqual(prepared.returncode, 0, "precondición (fixture): " + prepared.stderr)
        pid = read_state(root)["active_packet"]["id"]

        # El contrato del día cambia y el orquestador lo re-pinea (INV-2: la
        # aprobación la registra el orquestador, no el CLI).
        self.write(root, APPROVED_SPEC, APPROVED_SPEC_V2)
        new_digest = hashlib.sha256(APPROVED_SPEC_V2).hexdigest()
        state = read_state(root)
        repinned = False
        for entry in state.get("stage_history", []):
            if entry.get("feature") == FEATURE_ID and entry.get("stage") == "specification":
                entry["contract_sha256"] = new_digest
                repinned = True
        self.assertTrue(repinned, "precondición (fixture): no hay entrada `specification` que re-pinear")
        (root / STATE_FILE).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

        replaced = self.replace(root, pid)
        out = replaced.stdout + replaced.stderr
        self.assertEqual(
            replaced.returncode,
            0,
            "E4/W-1 (control): el reemplazo sobre un contrato aprobado debe "
            "seguir funcionando como hoy: " + out,
        )
        new_id = [p for p in packet_ids(root) if p != pid][0]
        self.assertEqual(
            request_of(root, new_id)["contract"].get("sha256"),
            new_digest,
            "E4/W-1 (control): el sucesor no lleva el digest del contrato del día",
        )
        self.assertTrue(
            (packet_dir(root, pid) / SUPERSEDED_FILE).is_file(),
            "E4/W-1 (control): no quedó el registro durable de superación",
        )
        self.assertEqual(
            (read_state(root).get("active_packet") or {}).get("id"),
            new_id,
            "E4/W-1 (control): el active_packet no apunta al sucesor",
        )

        # (b) guard vigente: `plan-review` sobre un kind aprobado ⇒ rechazo.
        #     Se afirma el EFECTO (rc≠0, sin publicación, state intacto) y
        #     NO el texto del diagnóstico (A-1: ese texto es el mismo que hoy
        #     bloquea el caso de W-1).
        guard_root = self.make_project()
        before = tree_snapshot(guard_root)
        state_before = state_bytes(guard_root)
        proc = self.prepare_review_over_approved_kind(guard_root)
        stderr = self.assert_behavioural_rejection(
            guard_root, "E4/W-1 (control: plan-review sobre kind aprobado)", before, state_before, proc
        )
        self.assertRegex(
            stderr,
            r"(?m)^ERROR: ",
            f"E4/W-1 (control): el guard vigente no es un rechazo "
            f"comportamental: {stderr!r}",
        )
        self.assertEqual(
            packet_ids(guard_root),
            [],
            "E4/W-1 (control): el guard vigente publicó un paquete",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
