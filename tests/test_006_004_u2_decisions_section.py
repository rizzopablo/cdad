#!/usr/bin/env python3
"""006-004 U2 RED — la sección aditiva del render.

Contrato: `docs/specs/006-004-active-decisions-table/spec.md` (PD-5, PD-6,
PD-13; R-9, R-10, R-11) + `docs/specs/006-004-active-decisions-table/plan.md`
§3 (ficha U2) y su bloque `plan-tasks` (tarea U2).

Superficie observable bajo prueba (caja negra: sólo *subprocess* sobre los CLI
públicos del repo; la implementación NUNCA se lee, NUNCA se importa):

    python3 scripts/cdad_packet.py prepare --project-root <ABS> \\
        --role <rol> --substage <subfase> --objective <encargo> \\
        [--plan-task <TASK_ID>] [--current-decision <JSON>]...
    python3 scripts/cdad_packet.py render --project-root <ABS> \\
        --execution-context <ABS> --request <ABS>

Cada proyecto es un fixture **descartable** en un tempdir propio, con su HOME
aislado; nunca se toca el repo real, ni el HOME real, ni el estado real, ni
ninguna ruta de este host.

INTERFAZ DECLARADA POR ESTE RED (la satisface el implementer leyendo el test;
la spec §2.1 y §2.3 fijan el contrato y dejan la mecánica dentro):

1. `## Current decisions` es el **título literal** de la sección nueva (R-9,
   R-10) y es una sección de nivel 2: una línea que empieza por `## ` y nada
   más. No hay otros títulos posibles.
2. **Posición** (R-10): la sección va **inmediatamente después de `## Contract`**
   y **antes del bloque de plan-task** (las secciones `## Task validation plan`
   y `## Applicable contract`).
3. **Forma de la sección** (R-10): una entrada por fila, **en el orden
   declarado**, y cada entrada lleva los **cinco campos** de la fila —`file`,
   `state`, `summary`, `roles`, `reference`— **en ese orden**. El RED no fija
   la sintaxis concreta (viñetas, sangrías, tabla): fija la **presencia**, el
   **orden** y la **pertenencia** de cada valor a la entrada de su fila.
4. **Aditividad** (R-9, PD-5): sin `current_decisions` (o con la lista vacía) el
   render no lleva la sección y sus bytes no cambian; con filas, la sección es
   lo **único** que se añade.

LÍMITE DECLARADO DE ESTE RED (no sobre-especifica la mecánica):

- El RED **no** congela el `PACKET.md` entero ni ningún digest de una fuente de
  instrucción: entre revisiones esos bytes cambian legítimamente (L-1). La
  comparación byte a byte es **intra-revisión**: las dos o más variantes se
  renderizan **con el mismo producto y en la misma corrida** (PD-5, PD-13).
- El RED **no** exige la redacción concreta del diagnóstico: es una
  postcondición de render, no de rechazo.
- El RED **no** afirma nada *entre* revisiones: el caso de dos fases (V-5) es de
  U6.

A-1 (declarada, plan §4): **esta feature NO reemplaza ningún oráculo
vigente.** La forma de las secciones del paquete se comprueba **por presencia**,
no por conjunto exhaustivo ⇒ una sección nueva no rompe los oráculos vigentes.
Este RED **vuelve a comprobar** esa propiedad (los oráculos de presencia de
`tests/test_005_003_t6_packet_contract.py`:747 y
`tests/test_004_003_t1_reviewfix.py`:167-169, con fixtures PROPIOS) y **sólo
añade casos**; no modifica, no sustituye y no invisibiliza ninguna prueba
vigente. El RED de U2 no toca ningún archivo de `tests/` ajeno a este.

RED hoy: `prepare` acepta y valida la fila (U1 GREEN) y la lleva en
`request["current_decisions"]`, pero el **render la ignora**: el `PACKET.md` no
emite `## Current decisions`. Fallan por `AssertionError` de CONTRATO (la
sección ausente; la diferencia que el render debería añadir), nunca por
ImportError, sintaxis, JSONDecodeError ni error de E/S no capturado.

Estado de cada caso hoy (RED): fallan los **cuatro** casos que exigen la
sección —`test_pd5_the_section_is_emitted_after_contract_with_one_entry_per_row`,
`test_pd5_without_rows_the_render_is_byte_identical_and_the_rows_add_only_the_section`,
`test_pd5_the_section_precedes_the_plan_task_block` y
`test_pd6_the_rows_travel_inside_the_package_and_the_scope_does_not_change`—;
**pasan hoy** los dos controles
(`test_pd6_a_role_without_applicable_rows_carries_no_section` y
`test_pd13_the_vigente_section_presence_oracles_stay_green_with_the_new_section`):
son controles (los brazos sin filas y los oráculos vigentes), no la falla, y deben
seguir verdes después del GREEN.

Mapeo test → postcondición:

  test_pd5_the_section_is_emitted_after_contract_with_one_entry_per_row
      -> PD-5 (con filas: la sección existe, va después de `## Contract`, trae
         una entrada por fila con los cinco campos y respeta el orden
         declarado)
  test_pd5_without_rows_the_render_is_byte_identical_and_the_rows_add_only_the_section
      -> PD-5 (sin el campo y con la lista vacía el render es byte-idéntico
         dentro de la misma revisión; con filas la sección es lo único que se
         añade) + PD-13 (aditividad)
  test_pd5_the_section_precedes_the_plan_task_block
      -> PD-5 (la sección va antes del bloque de plan-task — R-10)
  test_pd6_the_rows_travel_inside_the_package_and_the_scope_does_not_change
      -> PD-6 (las filas viajan dentro del paquete, no por el alcance de
         lectura: el alcance del paquete no cambia)
  test_pd6_a_role_without_applicable_rows_carries_no_section
      -> PD-6 (el paquete de un rol sin filas aplicables no lleva la sección)
  test_pd13_the_vigente_section_presence_oracles_stay_green_with_the_new_section
      -> PD-13 (los oráculos vigentes de presencia de secciones siguen verdes sin
         cambio de oráculo)
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"

FEATURE_ID = "006-004-active-decisions-table"
EPIC_ID = "epic-006-opencode-concurrency"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
PLAN_FILE = f"docs/specs/{FEATURE_ID}/plan.md"
CONTRACT_BYTES = b"# Contrato fixture 006-004 U2\n"

ROLE = "test-writer"
SUBSTAGE = "red"
# Un rol que ninguna fila del fixture nombra: su paquete no lleva filas.
OTHER_ROLE = "scribe"
OTHER_SUBSTAGE = "memory"
OBJECTIVE = "006-004 U2: la seccion aditiva del render"

# El título literal de la sección nueva (R-9, R-10).
SECTION_TITLE = "## Current decisions"
# La referencia NO se verifica (R-3/L-4): puede apuntar al árbol instalado.
REFERENCE = "skills/cdad-cycle/references/design-principles.md"

HEADING_RE = re.compile(r"(?m)^## .*$")
# Una ruta de documento (relativa al proyecto o al árbol instalado).
PATH_RE = re.compile(r"[A-Za-z0-9_./][A-Za-z0-9_./-]*\.md")
CLI_TIMEOUT_S = 120


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
        timeout=CLI_TIMEOUT_S,
    )


def packet_blocks(text: str) -> list[tuple[str | None, str]]:
    """Los bloques del paquete como (encabezado, bytes).

    El preámbulo (lo que precede al primer `## `) es el bloque de encabezado
    `None`. Cada bloque llega hasta el **siguiente** encabezado: el separador
    (línea en blanco) entre dos secciones pertenece al bloque anterior.
    """
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [(None, text)]
    blocks: list[tuple[str | None, str]] = [(None, text[: matches[0].start()])]
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(0), text[match.start() : end]))
    return blocks


def block_titles(text: str) -> list[str]:
    """Los títulos de sección, en orden."""
    return [title for title, _ in packet_blocks(text) if title is not None]


def section_text(text: str, title: str) -> str | None:
    """El texto de la sección `## <title>` (sin el encabezado), o None."""
    for heading, block in packet_blocks(text):
        if heading == title:
            return block[len(heading) :]
    return None


def section_text_by_presence(text: str, title: str) -> str | None:
    """La **misma** lectura por presencia de los oráculos vigentes
    (`tests/test_005_003_t6_packet_contract.py`:389-395 y
    `tests/test_004_003_t1_reviewfix.py`:165-172): se busca el marcador y se
    toma hasta el próximo `## `. Es un control, no una aserción nueva.

    `title` es el encabezado completo, con sus `## ` (los oráculos vivos
    reciben el nombre de la sección; aquí se pasa el encabezado tal cual)."""
    marker = f"\n{title}\n"
    index = text.find(marker)
    if index < 0:
        return None
    start = index + len(marker)
    nxt = text.find("\n## ", start)
    return text[start : nxt if nxt >= 0 else len(text)]


def decision_flags(rows: list[dict]) -> list[str]:
    """La invocación declarada: una bandera repetible por fila, en el orden."""
    flags: list[str] = []
    for row in rows:
        flags += ["--current-decision", json.dumps(row, ensure_ascii=False)]
    return flags


def good_row(
    file: str,
    *,
    state: str = "vigente",
    summary: str = "Resumen de la decision.",
    roles: list[str] | None = None,
    reference: str = REFERENCE,
) -> dict:
    """La forma buena de la fila (R-2), tal como la declara la spec."""
    return {
        "file": file,
        "state": state,
        "summary": summary,
        "roles": [ROLE] if roles is None else list(roles),
        "reference": reference,
    }


# ------------------------------------------------------------------- fixture


class RenderProject:
    """Proyecto descartable: política, state, contrato y autoridad."""

    def __init__(
        self,
        root: Path,
        *,
        role: str = ROLE,
        substage: str = SUBSTAGE,
        with_plan: bool = False,
    ) -> None:
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
        if with_plan:
            (root / PLAN_FILE).write_bytes(self._plan_bytes())

    # -- el plan del fixture (bloque canónico `plan-tasks`) ---------------

    @staticmethod
    def _plan_bytes() -> bytes:
        task = {
            "id": "U2",
            "produce": [],
            "consume": [],
            "depends_on": ["U1"],
            "parallel": [],
            "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
            "focal_tests": ["tests/test_006_004_u2_decisions_section.py"],
            "observable_checks": [
                "la seccion aparece despues de Contract y antes del plan-task"
            ],
            "regressions": ["tests/test_role_packet_render.py"],
            "integration_gate": "@validation_strategy",
            "owner": "RED: test-writer; GREEN: implementer",
        }
        block = json.dumps(
            {"validation_strategy": "Estrategia fixture.", "tasks": [task]},
            indent=1,
            sort_keys=True,
        )
        head = (
            "# Plan fixture 006-004 U2\n\n"
            "## 4. Bloque canonico plan-tasks\n\n"
        )
        return (head + "```plan-tasks\n" + block + "\n```\n").encode("utf-8")

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

    # -- utilidades --------------------------------------------------------

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

    def write_decision(self, name: str) -> str:
        """Crea el archivo de la decisión en el proyecto; devuelve su ruta."""
        rel = f"docs/adr/{name}.md"
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {name}\n\nDecision fixture.\n", encoding="utf-8")
        return rel

    def write_request_variant(self, name: str, request: dict) -> Path:
        """Una variante del request (para el render) en la raíz temporal."""
        path = self.root / ".cdad" / "tmp" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
        return path


class RenderCase(unittest.TestCase):
    """Base: un proyecto descartable por test, con HOME aislado."""

    def project(
        self,
        role: str = ROLE,
        substage: str = SUBSTAGE,
        with_plan: bool = False,
    ) -> RenderProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-006-004-u2-")
        self.addCleanup(temp.cleanup)
        return RenderProject(
            Path(temp.name).resolve() / "proj",
            role=role,
            substage=substage,
            with_plan=with_plan,
        )

    # -- oráculos de salida ------------------------------------------------

    def prepare_ok(self, project: RenderProject, *extra: str) -> subprocess.CompletedProcess[bytes]:
        result = run_cli(PACKET_CLI, "prepare", *project.args(*extra), env=project.env())
        self.assertEqual(
            result.returncode,
            0,
            "prepare falló: " + result.stderr.decode(errors="replace"),
        )
        return result

    def packet_dir(self, project: RenderProject) -> Path:
        base = project.root / ".cdad" / "packets"
        packets = sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []
        self.assertEqual(
            len(packets), 1, f"se esperaba un paquete publicado: {packets}"
        )
        return packets[0]

    def packet_text(self, project: RenderProject) -> str:
        path = self.packet_dir(project) / "PACKET.md"
        self.assertTrue(path.is_file(), f"prepare no escribió {path}")
        return path.read_text(encoding="utf-8")

    def request_of(self, project: RenderProject) -> dict:
        path = self.packet_dir(project) / "REQUEST.json"
        self.assertTrue(path.is_file(), f"prepare no escribió {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def execution_context(self, project: RenderProject) -> Path:
        docs = sorted((project.root / ".cdad" / "executions").glob("*/execution.json"))
        self.assertTrue(docs, "fixture: no hay contexto de ejecución v2 publicado")
        return docs[0]

    def render_request(self, project: RenderProject, request: dict, name: str) -> str:
        """El render del request con el producto de ESTA corrida (intra-revisión)."""
        path = project.write_request_variant(name, request)
        result = run_cli(
            PACKET_CLI,
            "render",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(self.execution_context(project)),
            "--request",
            str(path),
            env=project.env(),
        )
        self.assertEqual(
            result.returncode,
            0,
            "render falló: " + result.stderr.decode(errors="replace"),
        )
        return result.stdout.decode("utf-8")


# ------------------------------------------------------------------- PD-5


class TestPd5TheSectionIsEmitted(RenderCase):
    def test_pd5_the_section_is_emitted_after_contract_with_one_entry_per_row(self) -> None:
        """PD-5 (con filas): el render emite `## Current decisions`
        **inmediatamente después de `## Contract`**, con **una entrada por fila**,
        **en el orden declarado**, y cada entrada lleva los **cinco campos**
        (`file`, `state`, `summary`, `roles`, `reference`) **en ese orden**."""
        project = self.project()
        first = project.write_decision("ADR-001-decision-fixture")
        second = project.write_decision("ADR-002-decision-fixture")
        rows = [
            good_row(first, summary="Resumen de la primera decision."),
            good_row(
                second,
                summary="Resumen de la segunda decision.",
                roles=[ROLE, "reviewer"],
            ),
        ]
        self.prepare_ok(project, *decision_flags(rows))

        packet = self.packet_text(project)
        titles = block_titles(packet)
        self.assertIn(
            SECTION_TITLE,
            titles,
            "PD-5: el render no emite la sección "
            f"{SECTION_TITLE!r} (secciones emitidas: {titles})",
        )
        # La sección va inmediatamente después de `## Contract` (R-10).
        self.assertEqual(
            titles[titles.index(SECTION_TITLE) - 1],
            "## Contract",
            "PD-5: la sección de decisiones no va inmediatamente después de "
            f"`## Contract` (secciones: {titles})",
        )

        section = section_text(packet, SECTION_TITLE)
        self.assertIsNotNone(section, "PD-5: la sección de decisiones no tiene texto")
        assert section is not None  # para el analizador de tipos

        # Una entrada por fila: cada `file` aparece **una sola vez** y cada
        # entrada (línea que nombra una decisión) corresponde a una fila.
        for row in rows:
            self.assertEqual(
                section.count(row["file"]),
                1,
                f"PD-5: la fila {row['file']} aparece {section.count(row['file'])} "
                "veces en la sección (se espera una entrada por fila)",
            )
        entry_lines = [
            line for line in section.splitlines() if any(row["file"] in line for row in rows)
        ]
        self.assertEqual(
            len(entry_lines),
            len(rows),
            f"PD-5: la sección tiene {len(entry_lines)} entradas y se declararon "
            f"{len(rows)} filas",
        )
        # «Una entrada por fila»: la sección no nombra ninguna ruta que no sea
        # de una fila declarada (una entrada de más se delata por su ruta).
        declared_paths = {row["file"] for row in rows} | {row["reference"] for row in rows}
        unexpected = set(PATH_RE.findall(section)) - declared_paths
        self.assertEqual(
            unexpected,
            set(),
            "PD-5: la sección nombra rutas que no son de las filas declaradas: "
            f"{sorted(unexpected)}",
        )

        # Orden de las entradas: el de las filas declaradas.
        positions = [section.find(row["file"]) for row in rows]
        self.assertEqual(
            positions,
            sorted(positions),
            "PD-5: las entradas de la sección no respetan el orden declarado",
        )

        # Cada entrada lleva los cinco campos, en el orden declarado.
        for index, row in enumerate(rows):
            start = positions[index]
            end = positions[index + 1] if index + 1 < len(positions) else len(section)
            entry = section[start:end]
            for role in row["roles"]:
                self.assertIn(
                    role,
                    entry,
                    f"PD-5: la entrada de {row['file']} no nombra el rol {role!r}: "
                    f"{entry!r}",
                )
            where = []
            for field in (row["file"], row["state"], row["summary"], row["roles"][0]):
                self.assertIn(
                    field,
                    entry,
                    f"PD-5: la entrada de {row['file']} no lleva el campo {field!r}: "
                    f"{entry!r}",
                )
                where.append(entry.find(field))
            self.assertIn(
                row["reference"],
                entry,
                f"PD-5: la entrada de {row['file']} no lleva el campo "
                f"'reference': {entry!r}",
            )
            where.append(entry.find(row["reference"]))
            self.assertEqual(
                where,
                sorted(where),
                "PD-5: la entrada de "
                f"{row['file']} no lleva los cinco campos en el orden declarado "
                f"(file, state, summary, roles, reference): {entry!r}",
            )


class TestPd5ByteIdentity(RenderCase):
    def test_pd5_without_rows_the_render_is_byte_identical_and_the_rows_add_only_the_section(
        self,
    ) -> None:
        """PD-5 + PD-13 (aditividad): sin `current_decisions` y con la lista
        vacía el render es **byte-idéntico** (comparación **intra-revisión**:
        las dos variantes se renderizan con el mismo producto, en la misma
        corrida); con filas, la sección nueva es lo **único** que el render
        añade: el resto del paquete conserva sus bytes exactos."""
        project = self.project()
        decision = project.write_decision("ADR-001-decision-fixture")
        row = good_row(decision, summary="Resumen de la primera decision.")
        self.prepare_ok(project, *decision_flags([row]))

        request = self.request_of(project)
        self.assertIn(
            "current_decisions",
            request,
            "PD-6: el request no lleva la propiedad declarada `current_decisions`",
        )

        without_key = {k: v for k, v in request.items() if k != "current_decisions"}
        empty_list = dict(request)
        empty_list["current_decisions"] = []

        rendered_rows = self.render_request(project, request, "request-rows.json")
        rendered_without = self.render_request(
            project, without_key, "request-without.json"
        )
        rendered_empty = self.render_request(project, empty_list, "request-empty.json")

        # (1) Los dos brazos sin filas son byte-idénticos entre sí.
        self.assertEqual(
            rendered_without.encode("utf-8"),
            rendered_empty.encode("utf-8"),
            "PD-5: el render con `current_decisions: []` no es byte-idéntico al "
            "render sin la propiedad",
        )
        # (2) Ninguno de los dos lleva la sección.
        for label, text in (("sin la propiedad", rendered_without), ("lista vacía", rendered_empty)):
            self.assertNotIn(
                SECTION_TITLE,
                text,
                f"PD-5: el render ({label}) emite la sección {SECTION_TITLE!r}",
            )
        # (3) Con filas, la sección es lo único que se añade.
        blocks_rows = packet_blocks(rendered_rows)
        blocks_without = packet_blocks(rendered_without)
        titles_rows = [title for title, _ in blocks_rows]
        self.assertIn(
            SECTION_TITLE,
            titles_rows,
            "PD-5: el render con filas no emite la sección "
            f"{SECTION_TITLE!r} (secciones: {titles_rows})",
        )
        index = titles_rows.index(SECTION_TITLE)
        self.assertEqual(
            titles_rows[index - 1],
            "## Contract",
            "PD-5: la sección de decisiones no va inmediatamente después de "
            f"`## Contract` (secciones: {titles_rows})",
        )
        # El resto de los bloques conserva sus bytes exactos; sólo el bloque
        # `## Contract` puede diferir en su separador final (la línea en
        # blanca que abre la sección nueva).
        self.assertEqual(
            len(blocks_rows),
            len(blocks_without) + 1,
            "PD-5: el render con filas difiere del render sin filas en más de "
            "la sección nueva",
        )
        for position, (title, block) in enumerate(blocks_without):
            if title is None:
                counterpart = blocks_rows[position]
            elif position < index:
                counterpart = blocks_rows[position]
            else:
                counterpart = blocks_rows[position + 1]
            self.assertEqual(
                counterpart[0],
                title,
                "PD-5: el render con filas cambió el orden de las secciones",
            )
            if title == "## Contract":
                self.assertEqual(
                    counterpart[1].rstrip("\n"),
                    block.rstrip("\n"),
                    "PD-5: el bloque `## Contract` cambió de bytes con la sección "
                    "nuevas",
                )
            else:
                self.assertEqual(
                    counterpart[1],
                    block,
                    f"PD-5: el bloque {title!r} cambió de bytes con la sección nueva",
                )


class TestPd5PlanTaskPosition(RenderCase):
    def test_pd5_the_section_precedes_the_plan_task_block(self) -> None:
        """PD-5 (R-10): la sección nueva va **antes del bloque de plan-task**
        (las secciones `## Task validation plan` y `## Applicable contract`)."""
        project = self.project(with_plan=True)
        decision = project.write_decision("ADR-001-decision-fixture")
        row = good_row(decision, summary="Resumen de la primera decision.")
        self.prepare_ok(project, "--plan-task", "U2", *decision_flags([row]))

        packet = self.packet_text(project)
        titles = block_titles(packet)
        self.assertIn(
            "## Task validation plan",
            titles,
            "fixture: el paquete no trae el bloque de plan-task declarado",
        )
        self.assertIn(
            SECTION_TITLE,
            titles,
            "PD-5: el render no emite la sección "
            f"{SECTION_TITLE!r} (secciones: {titles})",
        )
        self.assertLess(
            titles.index(SECTION_TITLE),
            titles.index("## Task validation plan"),
            "PD-5: la sección de decisiones no va antes del bloque de plan-task "
            f"(secciones: {titles})",
        )
        self.assertEqual(
            titles[titles.index(SECTION_TITLE) - 1],
            "## Contract",
            "PD-5: la sección de decisiones no va inmediatamente después de "
            f"`## Contract` (secciones: {titles})",
        )


# ------------------------------------------------------------------- PD-6


class TestPd6RowsTravelInsideThePackage(RenderCase):
    def test_pd6_the_rows_travel_inside_the_package_and_the_scope_does_not_change(
        self,
    ) -> None:
        """PD-6 (las filas viajan en el encargo, no en un archivo que el rol
        debe abrir): el **paquete** del rol lleva las filas dentro, y el
        **alcance** del paquete no cambia (el test-writer sigue sin poder leer
        `docs/`; las filas llegan dentro, no por el alcance)."""
        project = self.project()
        decision = project.write_decision("ADR-001-decision-fixture")
        row = good_row(decision, summary="Resumen de la primera decision.")
        self.prepare_ok(project, *decision_flags([row]))

        packet = self.packet_text(project)
        section = section_text(packet, SECTION_TITLE)
        self.assertIsNotNone(
            section,
            "PD-6: el paquete del rol no lleva la sección de decisiones "
            f"{SECTION_TITLE!r}",
        )
        assert section is not None
        for value in (row["file"], row["summary"], row["reference"]):
            self.assertIn(
                value,
                section,
                f"PD-6: el paquete no lleva el dato {value!r} de la fila dentro",
            )

        # El alcance (read_scope/write_scope) no cambia: la misma fila no abre
        # ninguna ruta al rol.
        with_rows = self.request_of(project)
        other = self.project()
        self.prepare_ok(other)
        without_rows = self.request_of(other)
        self.assertEqual(
            with_rows["read_scope"],
            without_rows["read_scope"],
            "PD-6: el alcance de lectura del paquete cambió al declarar filas",
        )
        self.assertEqual(
            with_rows["write_scope"],
            without_rows["write_scope"],
            "PD-6: el alcance de escritura del paquete cambió al declarar filas",
        )


class TestPd6RoleWithoutRows(RenderCase):
    def test_pd6_a_role_without_applicable_rows_carries_no_section(self) -> None:
        """PD-6 (el paquete de un rol sin filas aplicables no lleva la sección):
        un rol al que ninguna fila declarada concierne recibe un paquete **sin**
        la sección, y su render es byte-idéntico al de la lista vacía."""
        project = self.project(role=OTHER_ROLE, substage=OTHER_SUBSTAGE)
        # La decisión existe y gobierna a OTROS roles: al scribe no le aplica.
        decision = project.write_decision("ADR-001-decision-fixture")
        self.assertTrue(decision)
        self.prepare_ok(project)

        packet = self.packet_text(project)
        self.assertNotIn(
            SECTION_TITLE,
            packet,
            "PD-6: el paquete de un rol sin filas aplicables lleva la sección "
            f"{SECTION_TITLE!r}",
        )
        request = self.request_of(project)
        empty_list = dict(request)
        empty_list["current_decisions"] = []
        rendered_empty = self.render_request(project, empty_list, "request-empty.json")
        self.assertEqual(
            rendered_empty.encode("utf-8"),
            packet.encode("utf-8"),
            "PD-6: el render del rol sin filas aplicables no es byte-idéntico "
            "al render con la lista vacía",
        )


# ------------------------------------------------------------------- PD-13


class TestPd13VigenteOracles(RenderCase):
    def test_pd13_the_vigente_section_presence_oracles_stay_green_with_the_new_section(
        self,
    ) -> None:
        """PD-13 (los oráculos vigentes de presencia de secciones siguen verdes
        **sin cambio de oráculo**): con la sección nueva presente, la lectura
        **por presencia** de los oráculos vigentes (`tests/test_005_003_t6_packet_contract.py`:747
        y `tests/test_004_003_t1_reviewfix.py`:167-169) encuentra lo mismo que
        antes, y las secciones que exige conservan sus bytes exactos: una
        sección nueva no rompe un oráculo por presencia (no es un conjunto
        exhaustivo)."""
        project = self.project()
        decision = project.write_decision("ADR-001-decision-fixture")
        row = good_row(decision, summary="Resumen de la primera decision.")
        self.prepare_ok(project, *decision_flags([row]))

        packet = self.packet_text(project)
        request = self.request_of(project)
        without_key = {k: v for k, v in request.items() if k != "current_decisions"}
        packet_without = self.render_request(
            project, without_key, "request-without.json"
        )

        for title in ("## Inputs", "## Evidence required"):
            found = section_text_by_presence(packet, title)
            self.assertIsNotNone(
                found,
                f"PD-13: con la sección nueva, la lectura por presencia ya no "
                f"encuentra {title!r}",
            )
            self.assertEqual(
                found,
                section_text_by_presence(packet_without, title),
                f"PD-13: la sección {title!r} cambió de bytes al declarar filas",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
