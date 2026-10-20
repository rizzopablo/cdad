#!/usr/bin/env python3
"""006-004 U1 RED — el encargo: la fila declarada, su forma y el tope.

Contrato: `docs/specs/006-004-active-decisions-table/spec.md` (PD-1, PD-2,
PD-3, PD-4, PD-6; R-1..R-11) + `docs/specs/006-004-active-decisions-table/plan.md`
§3 (ficha U1) y sus desconocidos V-1 y V-3.

Superficie observable bajo prueba (caja negra: sólo *subprocess* sobre los CLI
públicos del repo; la implementación NUNCA se lee, NUNCA se importa):

    python3 scripts/cdad_packet.py prepare --project-root <ABS> \
        --role <rol> --substage <subfase> --objective <encargo> \
        [--current-decision <JSON>]...
    python3 scripts/cdad_packet.py validate-request --project-root <ABS> \
        --execution-context <ABS> --request <ABS>
    python3 scripts/cdad_packet.py render --project-root <ABS> \
        --execution-context <ABS> --request <ABS>
    python3 scripts/cdad_result.py receive --project-root <ABS> \
        --execution-context <ABS> --packet <ABS> --request <ABS> \
        --descriptor <ABS>

Cada proyecto es un fixture **descartable** en un tempdir propio, con su HOME
aislado; nunca se toca el repo real, ni el HOME real, ni el estado real, ni
ninguna ruta de este host. El producto instalado (V-1) se instala en un
`CDAD_INSTALL_ROOT` temporal, con `CDAD_SKILL_EXTRA_DIRS` vacío.

INTERFAZ DECLARADA POR ESTE RED (la satisface el implementer leyendo el test;
la spec §2.1 fija el contrato y deja la mecánica dentro — la forma de la fila,
el nombre del rol, el tope y el orden son el contrato):

1. `prepare --current-decision <JSON>` es **repetible**: cada valor es un
   objeto JSON con la forma cerrada de la fila y las filas quedan en
   `request["current_decisions"]` **en el orden declarado** (R-8, PD-6).
2. La forma de la fila (R-2): claves exactamente `file`, `state`, `summary`,
   `roles`, `reference` y `superseded_by` **condicional** (exigido con
   `state: obsoleto`, prohibido con `state: vigente`); `file` debe existir en el
   proyecto; `state` ∈ {`vigente`, `obsoleto`}; `summary` de una línea; `roles`
   no vacío y dentro del vocabulario cerrado (los cinco roles delegados más
   `orchestrator`).
3. Admisión: **toda** fila declarada nombra al rol del paquete (R-5) y una fila
   `obsoleto` **no** es admisible (R-6); el tope es **32** filas y falla
   cerrado (R-7).
4. **Identidad de la fila**: la fila se nombra en el diagnóstico por su `file`
   (el único dato que la identifica); el rol del paquete se nombra por su
   nombre (`test-writer`). Es una decisión de interfaz de este RED, dentro de la
   libertad que deja el contrato ("naming the row"). El RED comprueba el
   **nombre del archivo** (el último segmento de la ruta): toda forma de
   nombrar el archivo en el diagnóstico lo contiene.
5. `receive` revalida el request con el conjunto ampliado (V-3): acepta un
   paquete cuyo request lleva `current_decisions` y rechaza uno con una fila
   malformada.

LÍMITE DECLARADO DE ESTE RED (no sobre-especifica la mecánica): el RED exige
el **rc distinto de cero** y la **ausencia de publicación** en todos los
negativos, y exige el **nombre del dato culpable** sólo donde el contrato lo
exige explícitamente (PD-1: la clave desconocida, el valor de `state` y su
vocabulario, la ruta de `file`, el valor de un rol fuera de vocabulario; PD-2:
la fila y el rol; PD-3: la fila y su `superseded_by`; PD-4: el número y el
tope). En los negativos restantes (`superseded_by` ausente/presente, `roles`
vacío, `summary` con salto de línea) el RED NO exige una redacción concreta
del diagnóstico.

A-1 (declarada, plan §4): **esta feature NO reemplaza ningún oráculo
vigente.** El conjunto cerrado del request se **extiende** con una propiedad
declarada (`current_decisions`) y la clausura **no** se relaja: este RED
**vuelve a comprobar** el control negativo (una clave cualquiera distinta de
`current_decisions` sigue rechazándose) y **sólo añade casos**; no modifica ni
invisibiliza ninguna prueba vigente. El RED de U1 no toca ningún archivo de
`tests/` ajeno a este.

RED hoy: `prepare` no conoce `--current-decision` (rc=2, «unrecognized
arguments») ⇒ el request no puede llevar filas, la forma de la fila no se
valida, la admisión y el tope no existen, `receive` rechaza cualquier request
con la propiedad nueva y el producto instalado tampoco la admite. Cada test
falla por `AssertionError` de CONTRATO (rc, contenido del request, diagnóstico
o ausencia de publicación), nunca por ImportError, sintaxis, JSONDecodeError
ni error de E/S no capturado.

Mapeo test → postcondición:

  test_pd1_good_row_is_accepted_and_request_carries_the_declared_order
      -> PD-1 (forma buena aceptada) + PD-6 (las filas viajan en el encargo, en
         el orden declarado)
  test_pd1_malformed_rows_are_rejected_without_publication
      -> PD-1 (los ocho negativos de la forma: clave desconocida, `state` fuera
         del vocabulario, `superseded_by` ausente con `obsoleto`, `superseded_by`
         presente con `vigente`, `file` inexistente, `roles` vacío, rol fuera
         del vocabulario, `summary` con salto de línea) — cada uno sin publicar
         y con el state byte-idéntico
  test_pd2_row_must_name_the_packet_role
      -> PD-2 (la fila nombra al rol del paquete: la que no lo nombra y la que
         nombra a otro rol delegado se rechazan por la misma regla)
  test_pd3_obsolete_row_is_not_admissible
      -> PD-3 (sólo lo vigente viaja: la fila `obsoleto` se rechaza nombrando
         la fila y su `superseded_by`)
  test_pd4_row_cap_fails_closed
      -> PD-4 (32 filas admitidas; 33 rechazadas nombrando el número y el tope,
         sin publicar)
  test_v1_installed_product_renders_the_same_package_with_rows
      -> V-1 (el producto instalado renderiza el paquete con las filas byte a
         byte igual que el del repo)
  test_v3_receive_revalidates_the_request_with_the_widened_set
      -> V-3 (`receive` recibe un paquete con filas y rechaza uno con una fila
         malformada)
  test_a1_unknown_request_key_is_still_rejected
      -> A-1 (control negativo explícito: la clausura del request NO se relaja)
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.product_staging import product_root

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"
RESULT_CLI = REPO_ROOT / "scripts" / "cdad_result.py"

FEATURE_ID = "006-004-active-decisions-table"
EPIC_ID = "epic-006-opencode-concurrency"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
CONTRACT_BYTES = b"# Contrato fixture 006-004 U1\n"

ROLE = "test-writer"
SUBSTAGE = "red"
OBJECTIVE = "006-004 U1: la fila declarada, su forma y el tope"

# Vocabularios cerrados (R-2/R-4) y tope (R-7), tal como los declara la spec.
STATE_VOCABULARY = ("vigente", "obsoleto")
ROLE_VOCABULARY = ("architect", "test-writer", "implementer", "reviewer", "scribe", "orchestrator")
MAX_ROWS = 32
# La referencia NO se verifica (R-3/L-4): puede apuntar al árbol instalado.
REFERENCE = "skills/cdad-cycle/references/design-principles.md"

# Parts del fixture de recepción (V-3): un part por artifact-kind del rol.
RECEIVE_PARTS: dict[str, bytes] = {
    "role-report": b"# Role report (fixture 006-004 U1)\n",
    "role-notes": b"# Role notes (fixture 006-004 U1)\n",
}
RECEIVE_PART_KINDS: dict[str, str] = {
    "role-report": "test-writer-role-report",
    "role-notes": "test-writer-notes",
}
RECEIVE_ATTEMPT_ID = "attempt-006-004-u1-red-001"
RECEIVE_DESCRIPTOR = ".cdad/inbox/RESULT.json"
RECEIVE_MANIFEST = ".cdad/inbox/changes.json"
RECEIVE_BASELINE_REF = "orchestrator-prepared-reference"
RECEIVE_BASELINE_SHA256 = "0" * 64


# --------------------------------------------------------------------- helpers


def run_cli(
    cli: Path, *args: str, cwd: Path = REPO_ROOT, env: dict | None = None
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(cli), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        check=False,
    )


def run_prepare(
    cli: Path, *args: str, cwd: Path = REPO_ROOT, env: dict | None = None
) -> subprocess.CompletedProcess[bytes]:
    return run_cli(cli, "prepare", *args, cwd=cwd, env=env)


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    """Cada entrada bajo root: archivos → bytes, directorios → None."""
    snapshot: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        snapshot[rel] = path.read_bytes() if path.is_file() else None
    return snapshot


def decision_flags(rows: list[dict]) -> list[str]:
    """La invocación declarada: una bandera repetible por fila, en el orden."""
    flags: list[str] = []
    for row in rows:
        flags += ["--current-decision", json.dumps(row, ensure_ascii=False)]
    return flags


def file_token(rel: str) -> str:
    """El nombre del archivo como token del diagnóstico: cualquier forma de
    nombrar el archivo (ruta relativa, absoluta o su último segmento) lo
    contiene, y a la vez identifica el archivo sin ambigüedad."""
    return Path(rel).name


def good_row(
    file: str = "docs/adr/ADR-001-decision-fixture.md",
    *,
    state: str = "vigente",
    summary: str = "Una decisión vigente de una línea.",
    roles: list[str] | None = None,
    reference: str = REFERENCE,
    extra: dict | None = None,
) -> dict:
    """La forma buena de la fila (R-2) con las variantes de cada negativo."""
    row = {
        "file": file,
        "state": state,
        "summary": summary,
        "roles": [ROLE] if roles is None else list(roles),
        "reference": reference,
    }
    if extra:
        row.update(extra)
    return row


class DecisionProject:
    """Proyecto descartable: política, state, contrato y autoridad (fixture propio)."""

    def __init__(self, root: Path, *, role: str = ROLE, substage: str = SUBSTAGE) -> None:
        self.root = root
        self.role = role
        self.substage = substage
        # HOME aislado FUERA del proyecto: el snapshot del árbol no lo ve.
        self.home = root.parent / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        root.mkdir(parents=True, exist_ok=True)
        (root / "tests").mkdir(exist_ok=True)
        (root / "src").mkdir(exist_ok=True)
        (root / "docs" / "specs" / FEATURE_ID).mkdir(parents=True, exist_ok=True)
        (root / CONTRACT_FILE).write_bytes(CONTRACT_BYTES)
        authority = root / AUTHORITY_REF
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Authorized execution fixture\n", encoding="utf-8")
        policy = {
            "schema_version": 1,
            "path_policy": {
                "test_roots": ["tests"],
                "implementation_roots": ["src", "lib"],
                "documentation_roots": ["docs"],
            },
            "temporary_roots": [".cdad/tmp"],
        }
        (root / POLICY_FILE).write_text(
            json.dumps(policy, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (root / STATE_FILE).write_text(
            json.dumps(self._state(), ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def _state(self) -> dict:
        return {
            "version": 1,
            "stack": None,
            "active_epic": EPIC_ID,
            "epic_stage": "features-loop",
            "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
            "epic_history": [],
            "active_feature": FEATURE_ID,
            "current_stage": "tdd",
            "tdd_substage": SUBSTAGE,
            "audit_status": "approved",
            "postconditions_status": {},
            "stage_history": [
                {
                    "feature": FEATURE_ID,
                    "stage": "specification",
                    "approved_by": "fixture",
                    "approved_at": "2026-10-20T00:00:00Z",
                    "contract_path": CONTRACT_FILE,
                    "contract_sha256": hashlib.sha256(CONTRACT_BYTES).hexdigest(),
                }
            ],
            "approver": "fixture",
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

    def env(self) -> dict:
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        return env

    def args(self, *extra: str, objective: str = OBJECTIVE) -> list[str]:
        return [
            "--project-root",
            str(self.root),
            "--role",
            self.role,
            "--substage",
            self.substage,
            "--objective",
            objective,
            *extra,
        ]

    @property
    def state_path(self) -> Path:
        return self.root / STATE_FILE

    @property
    def packets_dir(self) -> Path:
        return self.root / ".cdad" / "packets"

    def write_decision(self, name: str) -> str:
        """Crea el archivo de la decisión en el proyecto; devuelve su ruta relativa."""
        rel = f"docs/adr/{name}.md"
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {name}\n\nDecision fixture.\n", encoding="utf-8")
        return rel

    def write_temporary(self, name: str, payload: dict) -> Path:
        """Documento temporal del proyecto (raíz temporal declarada: .cdad/tmp)."""
        path = self.root / ".cdad" / "tmp" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path


class DecisionCase(unittest.TestCase):
    """Base: un proyecto descartable por test, con HOME aislado."""

    def project(self, role: str = ROLE, substage: str = SUBSTAGE) -> DecisionProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-006-004-u1-")
        self.addCleanup(temp.cleanup)
        return DecisionProject(Path(temp.name).resolve() / "proj", role=role, substage=substage)

    # -- oráculos de salida ------------------------------------------------

    def prepare_ok(self, project: DecisionProject, *extra: str) -> subprocess.CompletedProcess[bytes]:
        result = run_prepare(PACKET_CLI, *project.args(*extra), env=project.env())
        self.assertEqual(
            result.returncode,
            0,
            "prepare falló: " + result.stderr.decode(errors="replace"),
        )
        return result

    def published_packets(self, project: DecisionProject) -> list[Path]:
        if not project.packets_dir.is_dir():
            return []
        return sorted(p for p in project.packets_dir.iterdir() if p.is_dir())

    def request_of(self, project: DecisionProject) -> dict:
        packets = self.published_packets(project)
        self.assertEqual(len(packets), 1, f"se esperaba un paquete publicado: {packets}")
        path = packets[0] / "REQUEST.json"
        self.assertTrue(path.is_file(), f"prepare no escribió {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def execution_context(self, project: DecisionProject) -> Path:
        docs = sorted((project.root / ".cdad" / "executions").glob("*/execution.json"))
        self.assertTrue(docs, "fixture: no hay contexto de ejecución v2 publicado")
        return docs[0]

    # -- el control de "sin publicación" -----------------------------------

    def assert_rejected_without_publication(
        self,
        project: DecisionProject,
        extra: list[str],
        tokens: tuple[str, ...],
        label: str,
    ) -> subprocess.CompletedProcess[bytes]:
        """rc≠0, diagnóstico, stdout vacío, out-dir vacío, state byte-idéntico
        y árbol del proyecto sin cambios (el control de
        `tests/test_004_003_t4_validation_fields.py`:399-423)."""
        before = tree_snapshot(project.root)
        state_before = project.state_path.read_bytes()
        result = run_prepare(PACKET_CLI, *project.args(*extra), env=project.env())
        stderr = result.stderr.decode(errors="replace")
        self.assertNotEqual(
            result.returncode,
            0,
            f"{label}: el caso se aceptó pese a la postcondición: {stderr!r}",
        )
        self.assertRegex(stderr, r"(?m)^ERROR: ", f"{label}: stderr sin 'ERROR: ...': {stderr!r}")
        # La bandera declarada debe reconocerse: si el CLI no la conoce, el
        # rechazo no viene de la fila y los nombres exigidos abajo no dirían
        # nada (guarda que hace significativa la comprobación del diagnóstico).
        self.assertNotIn(
            "unrecognized",
            stderr,
            f"{label}: la bandera declarada `--current-decision` debe reconocerse: {stderr!r}",
        )
        for token in tokens:
            self.assertIn(
                token,
                stderr,
                f"{label}: el diagnóstico no nombra el dato culpable {token!r}: {stderr!r}",
            )
        self.assertEqual(result.stdout, b"", f"{label}: stdout debe estar vacío")
        self.assertEqual(
            self.published_packets(project), [], f"{label}: out-dir ganó entradas"
        )
        self.assertEqual(
            project.state_path.read_bytes(), state_before, f"{label}: el state cambió"
        )
        self.assertEqual(
            tree_snapshot(project.root), before, f"{label}: el árbol del proyecto cambió"
        )
        return result


# ------------------------------------------------------------------- PD-1 / PD-6


class TestPd1RowShape(DecisionCase):
    def test_pd1_good_row_is_accepted_and_request_carries_the_declared_order(self) -> None:
        """PD-1 (la forma buena se acepta) + PD-6 (las filas viajan en el
        encargo, en el orden declarado): una fila con `file` existente,
        `state: vigente`, `summary` de una línea, `roles` con el rol del
        paquete y `reference` se acepta; el `REQUEST.json` lleva
        `current_decisions` con las filas **en el orden declarado**."""
        project = self.project()
        first = project.write_decision("ADR-001-decision-fixture")
        second = project.write_decision("ADR-002-decision-fixture")
        rows = [
            good_row(first, summary="Primera decisión vigente."),
            good_row(second, summary="Segunda decisión vigente.", roles=[ROLE, "reviewer"]),
        ]
        self.prepare_ok(project, *decision_flags(rows))

        request = self.request_of(project)
        self.assertIn(
            "current_decisions",
            request,
            "PD-6: el request no lleva la propiedad declarada `current_decisions`",
        )
        self.assertEqual(
            request["current_decisions"],
            rows,
            "PD-1/PD-6: las filas no viajan en el request como fueron declaradas",
        )

    def test_pd1_malformed_rows_are_rejected_without_publication(self) -> None:
        """PD-1 (la forma de la fila falla cerrado): clave desconocida, `state`
        fuera del vocabulario, `superseded_by` ausente con `obsoleto`,
        `superseded_by` presente con `vigente`, `file` inexistente, `roles`
        vacío, un rol fuera del vocabulario y `summary` con salto de línea se
        rechazan con rc distinto de cero; en cada caso **nada se publica** y
        el state queda byte-idéntico."""
        cases = (
            ("clave desconocida", {"extra": {"clave_desconocida": "x"}}, ("clave_desconocida",)),
            (
                "state fuera del vocabulario",
                {"state": "pendiente"},
                ("pendiente", "vigente", "obsoleto"),
            ),
            ("superseded_by ausente con obsoleto", {"state": "obsoleto"}, ()),
            ("superseded_by presente con vigente", {"extra": {"superseded_by": "docs/adr/ADR-002-x.md"}}, ()),
            ("file inexistente", {"file": "docs/adr/ADR-999-no-existe.md"}, ("ADR-999-no-existe.md",)),
            ("roles vacío", {"roles": []}, ()),
            ("rol fuera del vocabulario", {"roles": ["wizard"]}, ("wizard",)),
            ("summary con salto de línea", {"summary": "Una línea.\nOtra línea."}, ()),
        )
        for label, override, tokens in cases:
            with self.subTest(caso=label):
                project = self.project()
                existing = project.write_decision("ADR-001-decision-fixture")
                row = good_row(existing, **override)
                self.assert_rejected_without_publication(
                    project, decision_flags([row]), tokens, f"PD-1 ({label})"
                )


# ------------------------------------------------------------------- PD-2


class TestPd2RowNamesThePacketRole(DecisionCase):
    def test_pd2_row_must_name_the_packet_role(self) -> None:
        """PD-2 (la fila nombra al rol del paquete): una fila que **no** nombra
        al rol del paquete se rechaza nombrando la fila y el rol; una fila que
        nombra a otro rol delegado se rechaza por la misma regla."""
        cases = (
            ("la fila no nombra al rol del paquete", ["architect", "scribe"]),
            ("la fila nombra a otro rol delegado", ["reviewer"]),
            ("la fila nombra sólo al orquestador", ["orchestrator"]),
        )
        for label, row_roles in cases:
            with self.subTest(caso=label):
                project = self.project()
                existing = project.write_decision("ADR-001-decision-fixture")
                row = good_row(existing, roles=row_roles)
                self.assert_rejected_without_publication(
                    project,
                    decision_flags([row]),
                    (file_token(existing), ROLE),
                    f"PD-2 ({label})",
                )
                # La fila ajena no viaja al paquete del rol correcto (PD-6):
                # el rechazo no publica paquete alguno.
                self.assertEqual(self.published_packets(project), [])


# ------------------------------------------------------------------- PD-3


class TestPd3OnlyCurrentRowsTravel(DecisionCase):
    def test_pd3_obsolete_row_is_not_admissible(self) -> None:
        """PD-3 (sólo lo vigente viaja): una fila `obsoleto` **no** es
        admisible en un paquete ⇒ rc distinto de cero, nombrando la fila y su
        `superseded_by`; nada se publica."""
        project = self.project()
        existing = project.write_decision("ADR-001-decision-fixture")
        successor = project.write_decision("ADR-002-decision-fixture")
        row = good_row(existing, state="obsoleto", extra={"superseded_by": successor})
        self.assert_rejected_without_publication(
            project,
            decision_flags([row]),
            (file_token(existing), file_token(successor)),
            "PD-3 (fila obsoleto)",
        )


# ------------------------------------------------------------------- PD-4


class TestPd4RowCap(DecisionCase):
    def test_pd4_row_cap_fails_closed(self) -> None:
        """PD-4 (el tope de filas falla cerrado): 32 filas se admiten y el
        request las lleva; 33 se rechazan nombrando el número declarado y el
        tope, sin publicar nada y con el state byte-idéntico."""
        project = self.project()
        rows = []
        for index in range(MAX_ROWS):
            rel = project.write_decision(f"ADR-{index + 1:03d}-decision-fixture")
            rows.append(good_row(rel, summary=f"Decisión vigente número {index + 1}."))
        self.prepare_ok(project, *decision_flags(rows))
        request = self.request_of(project)
        self.assertEqual(
            len(request.get("current_decisions") or []),
            MAX_ROWS,
            f"PD-4: {MAX_ROWS} filas deben ser admitidas",
        )

        overflow = self.project()
        overflow_rows = []
        for index in range(MAX_ROWS + 1):
            rel = overflow.write_decision(f"ADR-{index + 1:03d}-decision-fixture")
            overflow_rows.append(good_row(rel, summary=f"Decisión vigente número {index + 1}."))
        self.assert_rejected_without_publication(
            overflow,
            decision_flags(overflow_rows),
            (str(MAX_ROWS + 1), str(MAX_ROWS)),
            "PD-4 (33 filas)",
        )


# ------------------------------------------------------------------- V-1


class InstalledProductCase(unittest.TestCase):
    """Una instalación aislada (CDAD_INSTALL_ROOT, sin skill dirs extra), patrón P5."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.install_product = product_root()
        cls._install_tmp = tempfile.TemporaryDirectory(prefix="cdad-006-004-u1-install-")
        cls.install_root = Path(cls._install_tmp.name).resolve()
        env = os.environ.copy()
        env["CDAD_INSTALL_ROOT"] = str(cls.install_root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        cls.install_result = subprocess.run(
            ["bash", str(cls.install_product / "install.sh"), "--basic"],
            cwd=cls.install_product,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        cls.installed_cli = cls.install_root / ".claude/skills/cdad-cycle/scripts/cdad_packet.py"

    @classmethod
    def tearDownClass(cls) -> None:
        cls._install_tmp.cleanup()

    def setUp(self) -> None:
        self.assertEqual(
            self.install_result.returncode,
            0,
            self.install_result.stderr or self.install_result.stdout,
        )


class TestV1InstalledProduct(InstalledProductCase):
    def test_v1_installed_product_renders_the_same_package_with_rows(self) -> None:
        """V-1: el **producto instalado** (un `install.sh` en un root temporal,
        sin leer el repo fuente) renderiza el paquete con las filas byte a byte
        igual que el CLI del repo: mismo rc, mismo `REQUEST.json` (con las
        filas) y mismo `PACKET.md`."""
        outcomes: dict[str, tuple] = {}
        for label, cli in (("repo", PACKET_CLI), ("installed", self.installed_cli)):
            temp = tempfile.TemporaryDirectory(prefix=f"cdad-006-004-u1-{label}-")
            self.addCleanup(temp.cleanup)
            project = DecisionProject(Path(temp.name).resolve() / "proj")
            rel = project.write_decision("ADR-001-decision-fixture")
            row = good_row(rel, summary="Decisión vigente del fixture instalado.")
            result = run_prepare(cli, *project.args(*decision_flags([row])), env=project.env())
            packets = sorted(p for p in project.packets_dir.iterdir()) if project.packets_dir.is_dir() else []
            packet_dir = packets[0] if packets else None
            request_bytes = (
                (packet_dir / "REQUEST.json").read_bytes()
                if packet_dir is not None and (packet_dir / "REQUEST.json").is_file()
                else None
            )
            packet_bytes = (
                (packet_dir / "PACKET.md").read_bytes()
                if packet_dir is not None and (packet_dir / "PACKET.md").is_file()
                else None
            )
            outcomes[label] = (result.returncode, result.stdout, result.stderr, request_bytes, packet_bytes)

        repo, installed = outcomes["repo"], outcomes["installed"]
        self.assertEqual(repo[0], 0, "control del repo: " + repo[2].decode(errors="replace"))
        self.assertEqual(
            installed[0],
            0,
            "V-1: el producto instalado no admite las filas declaradas: "
            + installed[2].decode(errors="replace"),
        )
        self.assertEqual(installed[1], repo[1], "V-1: stdout instalado != stdout del repo")
        self.assertEqual(
            installed[3], repo[3], "V-1: el REQUEST.json instalado difiere del del repo"
        )
        self.assertEqual(
            installed[4], repo[4], "V-1: el PACKET.md instalado difiere del del repo"
        )
        self.assertIn(b"current_decisions", repo[3] or b"", "V-1: el request no lleva las filas")


# ------------------------------------------------------------------- V-3


class TestV3ReceiveRevalidatesTheRequest(DecisionCase):
    def _dispatched_project(self) -> tuple[DecisionProject, Path, Path, Path]:
        """Proyecto con el paquete publicado y observado como dispatched (I8)."""
        project = self.project()
        self.prepare_ok(project)
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        packet_id = state["active_packet"]["id"]
        execution_id = state["execution"]["id"]
        context = project.root / ".cdad" / "executions" / execution_id / "execution.json"
        packet_dir = project.root / ".cdad" / "packets" / packet_id
        observation = project.root / "docs" / "observations-fixture.json"
        observation.write_text(
            json.dumps(
                {
                    "runtime": "opencode",
                    "model_configured": "fixture-model",
                    "model_reported": "fixture-model",
                    "session": "ses-fixture-006-004-u1",
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
        record = run_prepare(
            PACKET_CLI,
            "--project-root",
            str(project.root),
            "--record-dispatch",
            packet_id,
            "--attempt-id",
            RECEIVE_ATTEMPT_ID,
            "--input",
            str(observation),
            env=project.env(),
        )
        self.assertEqual(
            record.returncode,
            0,
            "fixture: --record-dispatch debe registrar el intento: "
            + record.stderr.decode(errors="replace"),
        )

        inbox = project.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        for name, data in RECEIVE_PARTS.items():
            (inbox / f"{name}.md").write_bytes(data)
        manifest = project.root / RECEIVE_MANIFEST
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "observation_status": "trusted",
                    "baseline_ref": RECEIVE_BASELINE_REF,
                    "baseline_sha256": RECEIVE_BASELINE_SHA256,
                    "changes": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        descriptor_path = project.root / RECEIVE_DESCRIPTOR
        descriptor_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "execution_id": execution_id,
                    "packet_id": packet_id,
                    "feature_id": FEATURE_ID,
                    "source": {"kind": "staged-file", "sdk_message_ref": None},
                    "parts": [
                        {
                            "name": name,
                            "artifact_kind": RECEIVE_PART_KINDS[name],
                            "staged_path": f".cdad/inbox/{name}.md",
                        }
                        for name in RECEIVE_PARTS
                    ],
                    "observed_changes": {
                        "observation_status": "trusted",
                        "baseline_ref": RECEIVE_BASELINE_REF,
                        "baseline_sha256": RECEIVE_BASELINE_SHA256,
                        "manifest_path": RECEIVE_MANIFEST,
                    },
                    "run_evidence_ref": None,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return project, context, packet_dir, descriptor_path

    @staticmethod
    def _receive(
        project: DecisionProject, context: Path, packet: Path, request: Path, descriptor: Path
    ) -> subprocess.CompletedProcess[bytes]:
        return run_cli(
            RESULT_CLI,
            "receive",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(context),
            "--packet",
            str(packet),
            "--request",
            str(request),
            "--descriptor",
            str(descriptor),
            env=project.env(),
        )

    def test_v3_receive_revalidates_the_request_with_the_widened_set(self) -> None:
        """V-3 (`receive` revalida el request con el conjunto ampliado): un
        paquete cuyo request lleva `current_decisions` **se recibe**; otro
        cuyo request lleva una fila malformada **se rechaza** (rc distinto de
        cero) y no publica recibo."""
        # (a) paquete con filas -> recibido.
        project, context, packet_dir, descriptor = self._dispatched_project()
        rel = project.write_decision("ADR-001-decision-fixture")
        published_request = packet_dir / "REQUEST.json"
        request = json.loads(published_request.read_text(encoding="utf-8"))
        request["current_decisions"] = [good_row(rel)]
        crafted = project.write_temporary("REQUEST.with-rows.json", request)

        # El paquete canónico del request con filas; si el render todavía no
        # conoce la propiedad, se usa el paquete publicado (mismo control).
        rendered = run_cli(
            PACKET_CLI,
            "render",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(context),
            "--request",
            str(crafted),
            env=project.env(),
        )
        packet = (packet_dir / "PACKET.md").read_bytes()
        if rendered.returncode == 0:
            packet = rendered.stdout
        packet_path = project.root / ".cdad" / "tmp" / "PACKET.with-rows.md"
        packet_path.parent.mkdir(parents=True, exist_ok=True)
        packet_path.write_bytes(packet)
        received = self._receive(project, context, packet_path, crafted, descriptor)
        self.assertEqual(
            received.returncode,
            0,
            "V-3: receive debe aceptar el paquete con filas: "
            + received.stderr.decode(errors="replace"),
        )

        # (b) paquete con una fila malformada -> rechazado, sin recibo.
        other, other_context, other_packet_dir, other_descriptor = self._dispatched_project()
        other_rel = other.write_decision("ADR-001-decision-fixture")
        other_request = json.loads(
            (other_packet_dir / "REQUEST.json").read_text(encoding="utf-8")
        )
        other_request["current_decisions"] = [
            good_row(other_rel, state="pendiente")
        ]
        bad = other.write_temporary("REQUEST.malformed-row.json", other_request)
        rejected = self._receive(
            other, other_context, other_packet_dir / "PACKET.md", bad, other_descriptor
        )
        self.assertNotEqual(
            rejected.returncode,
            0,
            "V-3: receive aceptó un request con una fila malformada: "
            + rejected.stdout.decode(errors="replace"),
        )
        results = other.root / ".cdad" / "runtime" / "results"
        receipts = sorted(results.rglob("receipt.json")) if results.is_dir() else []
        self.assertEqual(receipts, [], "V-3: el rechazo no debe publicar un recibo")


# ------------------------------------------------------------------- A-1


class TestA1ClosureIsNotRelaxed(DecisionCase):
    def test_a1_unknown_request_key_is_still_rejected(self) -> None:
        """A-1 (control negativo explícito): el conjunto cerrado del request se
        **extiende** con una propiedad declarada, pero la clausura **no** se
        relaja: una clave cualquiera distinta de `current_decisions` sigue
        rechazándose. Este RED **no reemplaza ningún oráculo vigente**: sólo
        añade casos."""
        project = self.project()
        self.prepare_ok(project)
        published = self.published_packets(project)[0] / "REQUEST.json"
        context = self.execution_context(project)

        control = run_cli(
            PACKET_CLI,
            "validate-request",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(context),
            "--request",
            str(published),
            env=project.env(),
        )
        self.assertEqual(
            control.returncode,
            0,
            "A-1 (control positivo): el request publicado debe validar: "
            + control.stderr.decode(errors="replace"),
        )

        request = json.loads(published.read_text(encoding="utf-8"))
        request["clave_desconocida"] = "x"
        mutated = project.write_temporary("REQUEST.unknown-key.json", request)
        rejected = run_cli(
            PACKET_CLI,
            "validate-request",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(context),
            "--request",
            str(mutated),
            env=project.env(),
        )
        self.assertNotEqual(
            rejected.returncode,
            0,
            "A-1: la clausura del request se relajó: una clave desconocida fue aceptada",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
