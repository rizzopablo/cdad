#!/usr/bin/env python3
"""006-005 U4 RED — entrada única del orquestador, secciones `delegation` y
borde de adopción de la migración (PD-20; V-4, V-6; §2.1, §2.5, §2.6.1, §2.7).

Contrato (oráculo — nada se deriva de la implementación):
- ``docs/specs/006-005-native-path-parity/spec.md`` (sha256
  ``3a824be31e45cd8e6122b7d6f23d3f4d3e6af847ab73f7babef8aa90ce20df01``),
  **PD-20** y la tabla normativa **§5 D-6** (cinco filas con su condición y su
  acción única), **V-4** (la etiqueta «## Delegation (adapter)» con contenido
  nativo se corrige en U4), **V-6** (la condición stale de
  ``.cdad/execution.json`` en el mandato se corrige en U4), **§2.1** (la regla
  de transporte y la superficie ``cdad_dispatch.py --project-root R --packet
  <id> --runtime X``), **§2.5** (la credencial la resuelve e inyecta el módulo,
  sólo en el entorno del proceso cliente), **§2.6.1** (el borde de adopción:
  migrar → ``capabilities`` → despachar con ``--runtime``; una sola fuente
  vigente) y **§2.7** (el agente viaja en el paquete y el módulo lo traduce).
- ``docs/specs/006-005-native-path-parity/plan.md`` (sha256
  ``21d6954e200d303af46f190112b1c240d955203989aa436468a77a06dc8ede00``), ficha
  **U4** y su bloque ``plan-tasks``.

Superficie observable (caja negra, consumidor): los artefactos DECLARADOS por
la ficha U4 se leen al EJECUTARSE, nunca al escribir este módulo:

- ``sources/roles/orchestrator.md`` — fuente del mandato (el intake que PD-20
  reemplaza por la tabla de cinco filas de D-6);
- ``sources/agents/adapters/opencode.md`` y ``…/claude-code.md`` — dueñas del
  bloque ``<!-- cdad-section:delegation -->`` (D-1 de 006-002);
- ``skills/cdad-cycle/references/cli-delegation.md`` — dueña del borde de
  adopción de §2.6.1;
- los orquestadores GENERADOS recomputados con ``make staging`` en una copia
  temporal del checkout (patrón ``tests/product_staging.py``), y las salidas
  declaradas ``agents/**`` (``make agents`` nunca se edita a mano).

Los oráculos de texto verifican HECHOS DECLARADOS por el contrato (condiciones
de la vista, orden, ausencia de la condición stale, regla de transporte,
conceptos de las secciones y del borde de adopción, determinismo del staging),
no la redacción: las palabras no deciden el significado y la prosa fina la
juzga la review de stage 4 (límite honesto, PD-15). Un test de texto prueba que
la regla ESTÁ declarada; que el modelo la obedezca sólo lo muestra el recorrido
real (U6, PD-22) y no se acredita aquí.

Mapa test → postcondición (un test por hecho observable de PD-20):

  1 ``test_pd20_mandate_has_the_five_d6_rows_in_order_without_shared_conditions``
        PD-20 / D-6 / §2.1 (fuente y generado recomputado; orden, unicidad y
        ausencia de condiciones solapadas; la decisión se conduce desde
        ``status.entry``/``next``).
  2 ``test_pd20_stale_execution_json_condition_is_gone``
        PD-20 / V-6 (el mandato no usa ``.cdad/execution.json`` como condición
        de entrada; fuente y generado).
  3 ``test_pd20_transport_rule_is_declared``
        PD-20 / §2.1 / D-9 (mismo runtime ⇒ herramienta nativa + ``record``;
        otro runtime ⇒ ``cdad_dispatch.py … --runtime`` → ``receive``).
  4 ``test_pd20_delegation_sections_name_entry_packet_agent_and_module_credential``
        PD-20 / §2.5 / §2.7 (las secciones ``delegation`` de los dos
        adaptadores y de sus generados nombran la entrada nueva con
        ``--runtime``, el agente que viaja en el paquete y que la credencial la
        inyecta el módulo; y no nombran ``--exec-config`` como camino del
        orquestador).
  5 ``test_pd20_cli_delegation_declares_the_migration_adoption_border``
        PD-20 / §2.6.1 (migrar → ``capabilities`` → despachar con
        ``--runtime``; una sola fuente vigente; nada indica que el producto lea
        un exec-config).
  6 ``test_pd20_generated_delegation_label_drops_the_adapter_qualifier``
        PD-20 / V-4 (el generado ya no titula «## Delegation (adapter)» el
        contenido nativo; la sección sigue existiendo).
  7 ``test_pd20_staging_is_deterministic_and_matches_committed_outputs``
        PD-20 / plan U4 (``make staging`` determinista: dos corridas, mismos
        bytes; y el generado coincide con la fuente recomputada).

RED esperado en el árbol vigente (U1a–U3 y U7 en GREEN; U4 es esta unidad):
los tests 1–6 fallan por AssertionError de CONTENIDO — el mandato todavía tiene
las cuatro entradas solapadas con la condición stale, no declara la regla de
transporte nueva, las secciones ``delegation`` no nombran la entrada nueva ni
el agente del paquete ni la credencial del módulo, ``cli-delegation.md`` no
lleva el borde de adopción y el generado titula «## Delegation (adapter)».
El test 7 es el oráculo de regresión del generador (guard: hoy el staging es
determinista y las salidas declaradas están sincronizadas); su contraste RED se
materializa cuando el GREEN toca ``sources/**`` y debe regenerar ``agents/**``.
Ningún fallo es ImportError/SyntaxError/NameError ni fallo de fixture.

Regla A-1 — declaración expresa de NO reemplazo: se verificó por barrido de los
11 archivos de regresión de la ficha U4 (``tests/test_005_006_t2_intake.py``,
``tests/test_006_002_u1_delegation_section.py``,
``tests/test_006_002_u2_neutral_skill.py``,
``tests/test_006_002_u3_runtime_references.py``,
``tests/test_006_002_u6_context_discipline.py``,
``tests/test_006_003_u3_texts_without_profiles.py``,
``tests/test_cdad_generate.py``, ``tests/test_bash_policy_selection.py``,
``tests/test_opencode_read_map_and_steps.py``,
``tests/test_005_004_t2_installer_claims.py``,
``tests/test_role_packet_render.py``) que NINGUNO fija como contenido exigido
las cuatro entradas solapadas, la condición ``.cdad/execution.json``, la
etiqueta «## Delegation (adapter)» ni el camino del orquestador por
``cdad_delegate.py --exec-config``: no hay test acoplado que reemplazar en este
RED. Se declara además el borde adyacente observado: ``test_005_006_t2_intake``
usa anclas DINÁMICAS del intake («Prepared execution path», «Legacy path»,
«legacy-loads») para localizar su ventana; no exige esas frases como
postcondición y su ventana tolera corrimientos, pero si el GREEN elimina los
tres tokens por completo la regresión fallará por deriva de fixture y decide el
orquestador (no se toca aquí sin evidencia de acoplamiento).
"""

from __future__ import annotations

import atexit
import hashlib
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

# Reuso declarado (una sola definición de las rutas de los orquestadores
# generados): patrón u6→u1 de 006-002.
from tests.test_006_002_u1_delegation_section import CC_ORCH_REL, OC_ORCH_REL

REPO_ROOT = Path(__file__).resolve().parents[1]

ORCH_SOURCE_REL = Path("sources") / "roles" / "orchestrator.md"
OC_ADAPTER_REL = Path("sources") / "agents" / "adapters" / "opencode.md"
CC_ADAPTER_REL = Path("sources") / "agents" / "adapters" / "claude-code.md"
CLI_REF_REL = Path("skills") / "cdad-cycle" / "references" / "cli-delegation.md"

RUNTIMES = (
    ("opencode", OC_ORCH_REL, REPO_ROOT / "agents"),
    ("claude-code", CC_ORCH_REL, REPO_ROOT / "agents" / "claude-code"),
)

# Salidas declaradas del generador (mismas 11 por runtime que fija 004-001 T3).
ROLES = ("architect", "test-writer", "implementer", "reviewer", "scribe")
AGENT_NAMES = tuple(
    ["cdad-%s.md" % role for role in ROLES]
    + ["cdad-%s-odoo.md" % role for role in ROLES]
    + ["cdad-orchestrator.md"]
)

SECTION_OPEN_RE = re.compile(r"<!--\s*cdad-section:delegation\s*-->")
SECTION_CLOSE_RE = re.compile(r"<!--\s*/cdad-section\s*-->")
HEADING_RE = re.compile(r"^#{1,6}[ \t]")
ANY_HEADING_RE = re.compile(r"(?m)^(#{1,6})[ \t]")


# ---------------------------------------------------------------------------
# Lectura de artefactos declarados (existencia = puerta AssertionError)
# ---------------------------------------------------------------------------


def read(path: Path, why: str) -> str:
    """Artefacto declarado por el contrato: existe y no está vacío."""
    assert path.is_file(), (
        f"{why}: el artefacto declarado por el contrato no existe (drift de la "
        f"superficie): {_display(path)}"
    )
    text = path.read_text(encoding="utf-8")
    assert text.strip(), (
        f"{why}: el artefacto declarado está vacío: {_display(path)}"
    )
    return text


def read_recomputed(rel: Path, why: str) -> str:
    """Salida del generador RECOMPUTADA con `make staging` en una copia."""
    return read(_recomputed_root() / rel, f"{why} (staging recomputado)")


def _display(path: Path) -> str:
    """Ruta relativa al repo; el staging recomputado (copia temporal) se
    prefija como tal."""
    bases = [(REPO_ROOT, "")]
    if _STAGING_COPY is not None:
        bases.append((_STAGING_COPY, "recomputed/"))
    for base, prefix in bases:
        try:
            return prefix + path.relative_to(base).as_posix()
        except ValueError:
            continue
    return path.name


def _windows_around(text: str, pattern: re.Pattern, radius: int = 25):
    """Ventanas de texto alrededor de cada línea que matchea `pattern`."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if pattern.search(line):
            yield "\n".join(
                lines[max(0, index - radius):min(len(lines), index + radius + 1)]
            )


# ---------------------------------------------------------------------------
# D-6 — las cinco condiciones de la vista (tabla normativa de la spec)
#
# Cada condición se reconoce por sus VALORES declarados en D-6 (no por la
# redacción): `entry == diagnosis`; `continuity-reconcile` + paquete
# `dispatched`; ídem + `prepared`; ídem + sin paquete + ejecución activa; y
# `next-unit`. Una fila que reúna dos condiciones a la vez es el solape que
# PD-20 prohíbe.
# ---------------------------------------------------------------------------

RECONCILE_RE = re.compile(r"(?i)continuity-reconcile|\breconcile\b")
DISPATCHED_RE = re.compile(r"(?i)\bdispatched\b")
PREPARED_RE = re.compile(r"(?i)\bprepared\b|\bpreparada\b")
D6_ENTRY_TOKEN_RE = re.compile(r"(?i)\bentry\b|\bentrada\b")
DIAGNOSIS_RE = re.compile(r"(?i)\bdiagnosis\b|\bdiagn[oó]stico\b")
NEXT_UNIT_RE = re.compile(r"(?i)\bnext[-\s]unit\b")
ACTIVE_EXECUTION_RE = re.compile(
    r"(?i)\bresume\b|active execution|ejecuci[oó]n activa|active run|"
    r"corrida activa"
)
NO_PACKET_RE = re.compile(
    r"(?i)no packet|sin paquete|no active packet|no hay paquete|"
    r"without a packet|without packet"
)


def _condition_names(line: str) -> list[str]:
    """Condiciones de D-6 que una línea declara (una fila por condición)."""
    names: list[str] = []
    if DIAGNOSIS_RE.search(line) and (
        D6_ENTRY_TOKEN_RE.search(line) or "==" in line or "→" in line or "->" in line
    ):
        names.append("entry == diagnosis")
    if RECONCILE_RE.search(line) and DISPATCHED_RE.search(line):
        names.append("continuity-reconcile + packet dispatched")
    if RECONCILE_RE.search(line) and PREPARED_RE.search(line):
        names.append("continuity-reconcile + packet prepared")
    if (
        RECONCILE_RE.search(line)
        and ACTIVE_EXECUTION_RE.search(line)
        and NO_PACKET_RE.search(line)
    ):
        names.append("continuity-reconcile + no packet + active execution")
    if NEXT_UNIT_RE.search(line):
        names.append("next-unit")
    return names


D6_ROW_ORDER = (
    "entry == diagnosis",
    "continuity-reconcile + packet dispatched",
    "continuity-reconcile + packet prepared",
    "continuity-reconcile + no packet + active execution",
    "next-unit",
)


def _locate_d6_rows(text: str) -> dict[str, list[int]]:
    rows: dict[str, list[int]] = {name: [] for name in D6_ROW_ORDER}
    for index, line in enumerate(text.splitlines()):
        for name in _condition_names(line):
            rows[name].append(index)
    return rows


def _cluster(text: str, span: int = 60):
    """Primera ventana donde las cinco condiciones de D-6 aparecen juntas.

    Devuelve ``(start, end, firsts)`` con la línea de primera aparición de cada
    condición dentro de la ventana, o ``None`` si no forman una tabla única.
    """
    lines = text.splitlines()
    for start in range(len(lines)):
        end = min(len(lines), start + span)
        firsts: dict[str, int] = {}
        for index in range(start, end):
            for name in _condition_names(lines[index]):
                firsts.setdefault(name, index)
        if len(firsts) == len(D6_ROW_ORDER):
            return start, end, firsts
    return None


def _mandate_region(text: str) -> tuple[int, int, bool]:
    """Región del mandato: la tabla de cinco filas si es localizable.

    Si el mandato todavía no tiene las cinco filas (árbol previo a la unidad),
    la región es el documento completo: así el oráculo de la condición stale
    sigue siendo observable.
    """
    cluster = _cluster(text)
    if cluster is None:
        return 0, len(text.splitlines()), False
    start, end, _firsts = cluster
    return max(0, start - 10), min(len(text.splitlines()), end + 10), True


# ---------------------------------------------------------------------------
# Test 1 — PD-20 / D-6 / §2.1: cinco filas, en orden, sin condiciones solapadas
# ---------------------------------------------------------------------------


class TestPd20FiveD6Rows(unittest.TestCase):
    """PD-20: el mandato conduce la decisión desde `status.entry`/`next` con el
    orden de las cinco filas de D-6 y sin dos filas con la misma condición; la
    fuente y el generado recomputado llevan el mismo texto."""

    def assert_five_rows(self, text: str, label: str) -> None:
        rows = _locate_d6_rows(text)
        missing = [name for name in D6_ROW_ORDER if not rows[name]]
        self.assertEqual(
            missing,
            [],
            msg=(
                f"PD-20 ({label}): el mandato no declara las cinco condiciones "
                f"de §5 D-6 (faltan {missing!r}); D-6 es la tabla normativa y "
                "el intake debe conducir la decisión desde la vista "
                "`status.entry`/`next` con esas cinco filas, sin las cuatro "
                "entradas solapadas anteriores"
            ),
        )

        cluster = _cluster(text)
        self.assertIsNotNone(
            cluster,
            msg=(
                f"PD-20 ({label}): las cinco condiciones de D-6 aparecen en el "
                "documento pero NO forman una tabla única (no hay una ventana "
                "de 60 líneas que reúna las cinco): el mandato debe "
                "presentarlas juntas en su orden, no dispersas"
            ),
        )
        start, end, firsts = cluster

        # Ninguna fila declara dos condiciones a la vez (solape prohibido).
        lines = text.splitlines()
        overlapping = [
            f"{label}:{index + 1} → {_condition_names(lines[index])!r}"
            for index in range(start, end)
            if len(_condition_names(lines[index])) > 1
        ]
        self.assertEqual(
            overlapping,
            [],
            msg=(
                "PD-20: hay filas que declaran MÁS DE UNA condición de D-6 "
                f"(dos filas con la misma condición / solape): {overlapping!r}"
            ),
        )

        # Orden de la tabla: cada condición aparece por primera vez en el orden
        # normativo y sobre líneas distintas.
        first_lines = [firsts[name] for name in D6_ROW_ORDER]
        self.assertEqual(
            first_lines,
            sorted(first_lines),
            msg=(
                "PD-20: las cinco filas de D-6 no aparecen en el orden "
                "normativo (líneas 1-based: "
                f"{[i + 1 for i in first_lines]!r}, orden D-6: "
                f"{list(D6_ROW_ORDER)!r})"
            ),
        )
        self.assertEqual(
            len(set(first_lines)),
            len(D6_ROW_ORDER),
            msg=(
                "PD-20: dos condiciones de D-6 caen en la misma fila "
                f"(líneas {[i + 1 for i in first_lines]!r}); cada fila tiene "
                "UNA condición"
            ),
        )

        # La decisión se conduce desde la vista `status.entry`/`next`.
        region = "\n".join(lines[start:end])
        self.assertRegex(
            region,
            re.compile(r"(?i)\bstatus\b"),
            msg=(
                f"PD-20 ({label}): el mandato no nombra la vista `status` "
                "como insumo de la decisión (PD-20: se conduce desde "
                "`status.entry`/`next`)"
            ),
        )
        self.assertRegex(
            region,
            re.compile(r"(?i)\bentry\b|\bnext\b"),
            msg=(
                f"PD-20 ({label}): el mandato no nombra `entry`/`next` como "
                "insumo de la decisión"
            ),
        )

    def test_pd20_mandate_has_the_five_d6_rows_in_order_without_shared_conditions(
            self) -> None:
        """PD-20/D-6: fuente del mandato + orquestadores generados (staging)."""
        surfaces = [("sources/roles/orchestrator.md", read(ORCH_SOURCE_REL, "PD-20"))]
        for runtime, rel, _committed in RUNTIMES:
            surfaces.append(
                (f"generated {runtime}", read_recomputed(rel, f"PD-20 {runtime}"))
            )
        for label, text in surfaces:
            with self.subTest(surface=label):
                self.assert_five_rows(text, label)


# ---------------------------------------------------------------------------
# Test 2 — PD-20 / V-6: la condición stale de `.cdad/execution.json` no existe
# ---------------------------------------------------------------------------

STALE_PATH = ".cdad/execution.json"
# Vocabulario de condición/entrada: si la ruta aparece con él, se está usando
# como condición de la vista. Una referencia histórica o de contexto no lo usa.
CONDITION_TOKEN_RE = re.compile(
    r"(?i)\bentry\b|\bentrada\b|\bintake\b|\bdecision\b|\bdecisi[oó]n\b|"
    r"\bcondition\b|\bcondici[oó]n\b|\bprepared\b|\bpreparada\b|"
    r"\bexists?\b|\bexiste\b|\bpresent\b|\bpresente\b|\bwhen\b|\bcuando\b|"
    r"\bif\b|\bsi\b|→|->|\bthen\b|\bentonces\b"
)
STALE_NEGATION_RE = re.compile(
    r"(?i)\bno\b|\bnot\b|\bnever\b|\bnunca\b|\bsin\b|\bdo not\b|don't|"
    r"does not|must not|\bretired\b|\bretirad\w*|\bdeja de\b|\bno longer\b"
)


class TestPd20NoStaleExecutionJsonCondition(unittest.TestCase):
    """PD-20/V-6: la condición `.cdad/execution.json` del mandato viejo no
    sobrevive como entrada — ni en la fuente ni en el generado."""

    def stale_offenders(self, text: str, label: str) -> list[str]:
        lo, hi, _locatable = _mandate_region(text)
        lines = text.splitlines()
        offenders: list[str] = []
        for index in range(lo, hi):
            line = lines[index]
            if STALE_PATH not in line.lower():
                continue
            if not CONDITION_TOKEN_RE.search(line):
                continue
            if STALE_NEGATION_RE.search(line):
                continue
            offenders.append(f"{label}:{index + 1} → {line.strip()[:160]}")
        return offenders

    def test_pd20_stale_execution_json_condition_is_gone(self) -> None:
        """PD-20/V-6: `sources/roles/orchestrator.md` y sus generados."""
        surfaces = [("sources/roles/orchestrator.md", read(ORCH_SOURCE_REL, "PD-20/V-6"))]
        for runtime, rel, _committed in RUNTIMES:
            surfaces.append(
                (f"generated {runtime}", read_recomputed(rel, f"PD-20/V-6 {runtime}"))
            )
        all_offenders: list[str] = []
        for label, text in surfaces:
            all_offenders.extend(self.stale_offenders(text, label))
        self.assertEqual(
            all_offenders,
            [],
            msg=(
                "PD-20/V-6: el mandato sigue usando `" + STALE_PATH + "` como "
                "condición de entrada (el path v1 plano); la entrada única se "
                "conduce desde `status.entry`/`next` y esa condición stale "
                f"desaparece: {all_offenders!r}"
            ),
        )


# ---------------------------------------------------------------------------
# Test 3 — PD-20 / §2.1 / D-9: la regla de transporte declarada
# ---------------------------------------------------------------------------

SAME_RUNTIME_RE = re.compile(r"(?i)same runtime|mismo runtime")
NATIVE_RE = re.compile(
    r"(?i)\bnative\b|\bnativa\b|`task`|subagent_type|runtime tool|"
    r"herramienta del runtime"
)
RECORD_RE = re.compile(r"(?i)\brecord\b")
OTHER_RUNTIME_RE = re.compile(
    r"(?i)other runtime|different runtime|another runtime|otro runtime|"
    r"distinto runtime"
)
DISPATCH_ENTRY_RE = re.compile(r"cdad_dispatch\.py|cdad_dispatch")
RUNTIME_FLAG_RE = re.compile(r"--runtime\b")
RECEIVE_RE = re.compile(r"(?i)\breceive\b")


class TestPd20TransportRule(unittest.TestCase):
    """PD-20/§2.1/D-9: la regla de transporte está declarada en el mandato y en
    el generado — mismo runtime ⇒ herramienta nativa + `record`; otro runtime ⇒
    `cdad_dispatch.py --project-root R --packet <id> --runtime X` → `receive`."""

    def co_located(self, text: str, required: tuple[tuple[str, re.Pattern], ...],
                   anchor: re.Pattern, radius: int = 8) -> str | None:
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if not anchor.search(line):
                continue
            chunk = "\n".join(
                lines[max(0, index - radius):min(len(lines), index + radius + 1)]
            )
            if all(pattern.search(chunk) for _, pattern in required):
                return chunk
        return None

    def assert_transport_rule(self, text: str, label: str) -> None:
        native = self.co_located(
            text,
            (
                ("mismo runtime", SAME_RUNTIME_RE),
                ("herramienta nativa", NATIVE_RE),
                ("record", RECORD_RE),
            ),
            RECORD_RE,
        )
        self.assertIsNotNone(
            native,
            msg=(
                f"PD-20 ({label}): el mandato no declara que, para el MISMO "
                "runtime del orquestador, el transporte es la herramienta "
                "nativa + `record` (regla de D-6 fila 3 / §2.1)"
            ),
        )
        external = self.co_located(
            text,
            (
                ("otro runtime", OTHER_RUNTIME_RE),
                ("entrada cdad_dispatch.py", DISPATCH_ENTRY_RE),
                ("--runtime", RUNTIME_FLAG_RE),
                ("receive", RECEIVE_RE),
            ),
            DISPATCH_ENTRY_RE,
        )
        self.assertIsNotNone(
            external,
            msg=(
                f"PD-20 ({label}): el mandato no declara que, para OTRO "
                "runtime, el transporte es la entrada externa "
                "`cdad_dispatch.py --project-root R --packet <id> --runtime X` "
                "seguida de `receive` (regla de D-6 fila 3 / §2.1 / D-9)"
            ),
        )

    def test_pd20_transport_rule_is_declared(self) -> None:
        """PD-20/§2.1: la regla de transporte en fuente y generados."""
        surfaces = [("sources/roles/orchestrator.md", read(ORCH_SOURCE_REL, "PD-20/§2.1"))]
        for runtime, rel, _committed in RUNTIMES:
            surfaces.append(
                (f"generated {runtime}", read_recomputed(rel, f"PD-20/§2.1 {runtime}"))
            )
        for label, text in surfaces:
            with self.subTest(surface=label):
                self.assert_transport_rule(text, label)


# ---------------------------------------------------------------------------
# Test 4 — PD-20 / §2.5 / §2.7: las secciones `delegation`
# ---------------------------------------------------------------------------

REQUEST_JSON_RE = re.compile(r"(?i)request\.json|\bREQUEST\.json\b")
AGENT_FIELD_RE = re.compile(r"(?i)\bagent\b")
PACKET_RE = re.compile(r"(?i)\bpacket\b|\bpaquete\b|\bencargo\b")
CREDENTIAL_RE = re.compile(r"(?i)\bcredential\b|\bcredencial\b")
MODULE_RE = re.compile(r"(?i)\bmodule\b|\bm[oó]dulo\b|cdad_delegate")
INJECT_RE = re.compile(
    r"(?i)\binject\w*|\binyect\w*|environment|entorno"
)
EXEC_CONFIG_RE = re.compile(r"--exec-config\b")
EXEC_CONFIG_GUARD_RE = re.compile(
    r"(?i)\bno\b|\bnot\b|\bnever\b|\bnunca\b|\bsin\b|\bdo not\b|"
    r"does not|must not|\bmigrat\w*|\bmigrar\b|legacy|retired|retirad\w*|"
    r"internal|interno|interface|interfaz|adapter contract|"
    r"contrato del adaptador"
)


def delegation_scope(text: str, label: str) -> tuple[str, str]:
    """Bloque `delegation`: por marcadores (fuentes) o por encabezado."""
    match = SECTION_OPEN_RE.search(text)
    if match:
        close = SECTION_CLOSE_RE.search(text, match.end())
        assert close is not None, (
            f"PD-20 ({label}): el bloque `delegation` no tiene cierre "
            "`<!-- /cdad-section -->` (gramática de secciones del generador)"
        )
        return text[match.end():close.start()], "block"
    headings = []
    for match in ANY_HEADING_RE.finditer(text):
        line_end = text.find("\n", match.end())
        if line_end < 0:
            line_end = len(text)
        if "delegation" in text[match.end():line_end].lower():
            headings.append((match.start(), len(match.group(1))))
    if not headings:
        return text, "whole-document"
    start, level = headings[0]
    line_end = text.find("\n", start)
    if line_end < 0:
        return text, "whole-document"
    body = text[line_end:]
    end = len(text)
    for match in ANY_HEADING_RE.finditer(body):
        if len(match.group(1)) <= level:
            end = line_end + match.start()
            break
    return text[start:end], "heading"


class TestPd20DelegationSections(unittest.TestCase):
    """PD-20/§2.5/§2.7: las secciones `delegation` de los adaptadores (y sus
    generados) nombran la entrada nueva con `--runtime`, el agente que viaja en
    el paquete y que la credencial la inyecta el módulo."""

    @staticmethod
    def _missing_facts(scope: str) -> list[str]:
        """Hechos de la sección que faltan en `scope` (lista vacía = completa)."""
        missing: list[str] = []
        if not DISPATCH_ENTRY_RE.search(scope):
            missing.append(
                "la entrada nueva `cdad_dispatch.py` (D-9/§2.1)"
            )
        if not RUNTIME_FLAG_RE.search(scope):
            missing.append("`--runtime` (runtime explícito, §2.1)")

        lines = scope.splitlines()
        # El agente viaja en el paquete: `REQUEST.json` + campo `agent`.
        agent_declared = False
        credential_declared = False
        for index in range(len(lines)):
            chunk = "\n".join(lines[max(0, index - 6):index + 7])
            if (
                REQUEST_JSON_RE.search(chunk)
                and AGENT_FIELD_RE.search(chunk)
                and PACKET_RE.search(chunk)
            ):
                agent_declared = True
            if (
                CREDENTIAL_RE.search(chunk)
                and MODULE_RE.search(chunk)
                and INJECT_RE.search(chunk)
            ):
                credential_declared = True
        if not agent_declared:
            missing.append(
                "el agente que viaja en el paquete (`REQUEST.json` + campo "
                "`agent`, §2.7/D-ADP-4)"
            )
        if not credential_declared:
            missing.append(
                "la credencial que resuelve e inyecta el módulo en el entorno "
                "del proceso cliente (§2.5/D-ADP-1)"
            )

        # `--exec-config` no se nombra como camino del orquestador.
        offenders = [
            line.strip()[:160]
            for line in lines
            if EXEC_CONFIG_RE.search(line)
            and not EXEC_CONFIG_GUARD_RE.search(line)
        ]
        if offenders:
            missing.append(
                f"la ausencia de `--exec-config` como camino del orquestador "
                f"(§2.6/D-11); ofensores {offenders!r}"
            )
        return missing

    def assert_section_facts(self, text: str, label: str) -> None:
        scope, mode = delegation_scope(text, label)
        missing = self._missing_facts(scope)
        if missing and mode != "block":
            # Compuesto (sin marcadores): se acepta una unidad coherente del
            # generado — una ventana alrededor de la entrada nueva que reúna
            # todos los hechos (la composición puede intercalar secciones).
            for chunk in _windows_around(text, DISPATCH_ENTRY_RE, radius=25):
                if not self._missing_facts(chunk):
                    missing = []
                    break
        self.assertEqual(
            missing,
            [],
            msg=(
                f"PD-20 ({label}, scope={mode}): la sección `delegation` no "
                "declara todos los hechos que exige la spec — "
                f"faltan: {missing!r}"
            ),
        )

    def test_pd20_delegation_sections_name_entry_packet_agent_and_module_credential(
            self) -> None:
        """PD-20/§2.5/§2.7: bloques fuente de ambos adaptadores + generados."""
        surfaces = [
            ("sources/.../opencode.md", read(OC_ADAPTER_REL, "PD-20/§2.5/§2.7")),
            ("sources/.../claude-code.md", read(CC_ADAPTER_REL, "PD-20/§2.5/§2.7")),
        ]
        for runtime, rel, _committed in RUNTIMES:
            surfaces.append(
                (f"generated {runtime}", read_recomputed(rel, f"PD-20/§2.5/§2.7 {runtime}"))
            )
        for label, text in surfaces:
            with self.subTest(surface=label):
                self.assert_section_facts(text, label)


# ---------------------------------------------------------------------------
# Test 5 — PD-20 / §2.6.1: el borde de adopción en `cli-delegation.md`
# ---------------------------------------------------------------------------

MIGRATE_RE = re.compile(
    r"(?i)\bmigrate\b|\bmigrar\b|\bmigraci[oó]n\b|--legacy-exec-config"
)
CAPABILITIES_RE = re.compile(r"(?i)\bcapabilities\b")
RUNTIMES_JSON_RE = re.compile(r"runtimes\.json")
SINGLE_SOURCE_RE = re.compile(
    r"(?i)una sola fuente|[uú]nica fuente|single source|only source|"
    r"one source|one single source|una [uú]nica fuente"
)


class TestPd20AdoptionBorder(unittest.TestCase):
    """PD-20/§2.6.1: `cli-delegation.md` declara el borde de adopción de la
    migración — orden migrar → `capabilities` → despachar con `--runtime`, una
    sola fuente vigente — y no indica que el producto lea un exec-config."""

    @staticmethod
    def _border_block(text: str) -> str | None:
        """Bloque contiguo (párrafo o lista; hasta 3 bloques) que declara el
        borde COMPLETO en su orden: migrar → `capabilities` → despachar con
        `--runtime`, con `runtimes.json` como fuente."""
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        for index in range(len(blocks)):
            for width in (1, 2, 3):
                if index + width > len(blocks):
                    break
                chunk = "\n\n".join(blocks[index:index + width])
                migrate = MIGRATE_RE.search(chunk)
                if not migrate:
                    continue
                capabilities = CAPABILITIES_RE.search(chunk, migrate.end())
                if not capabilities:
                    continue
                if not RUNTIME_FLAG_RE.search(chunk, capabilities.end()):
                    continue
                if not RUNTIMES_JSON_RE.search(chunk):
                    continue
                return chunk
        return None

    def test_pd20_cli_delegation_declares_the_migration_adoption_border(
            self) -> None:
        """PD-20/§2.6.1/E5: borde de adopción documentado en la referencia."""
        text = read(CLI_REF_REL, "PD-20/§2.6.1")
        border = self._border_block(text)
        self.assertIsNotNone(
            border,
            msg=(
                "PD-20/§2.6.1: `skills/cdad-cycle/references/cli-delegation.md` "
                "no declara el borde de adopción de la migración en su orden "
                "normativo (migrar → `capabilities` → despachar con "
                "`--runtime`, con `runtimes.json` como fuente): el consumidor "
                "que hoy usa un exec-config queda sin recorrido documentado "
                "(E5)"
            ),
        )

        # Una sola fuente vigente en la entrada nueva.
        self.assertTrue(
            SINGLE_SOURCE_RE.search(border) or SINGLE_SOURCE_RE.search(text),
            msg=(
                "PD-20/§2.6.1: el borde de adopción no declara que la entrada "
                "lee UNA sola fuente vigente (la sección de `runtimes.json`; "
                "el exec-config deja de usarse)"
            ),
        )

        # Nada indica que el producto lea un exec-config fuera del paso de
        # migración (el token `--legacy-exec-config` es la bandera propia).
        offenders: list[str] = []
        for index, line in enumerate(text.splitlines(), start=1):
            if not EXEC_CONFIG_RE.search(line):
                continue
            if EXEC_CONFIG_GUARD_RE.search(line):
                continue
            offenders.append(
                f"cli-delegation.md:{index} → {line.strip()[:160]}"
            )
        self.assertEqual(
            offenders,
            [],
            msg=(
                "PD-20/§2.6.1/D-11: `cli-delegation.md` indica que el producto "
                "lee un exec-config como camino de despacho (la entrada no lo "
                f"declara; sólo existe el paso explícito de migración): "
                f"{offenders!r}"
            ),
        )


# ---------------------------------------------------------------------------
# Test 6 — PD-20 / V-4: la etiqueta generada pierde «(adapter)»
# ---------------------------------------------------------------------------

ADAPTER_LABEL_RE = re.compile(
    r"(?im)^#{1,6}[ \t]*[*_`]*delegation[*_`]*[ \t]*\(\s*adapter\s*\)(?=[^A-Za-z0-9_]|$)"
)
DELEGATION_HEADING_RE = re.compile(r"(?im)^#{1,6}[ \t]*[^\n]*\bdelegation\b")


class TestPd20GeneratedDelegationLabel(unittest.TestCase):
    """PD-20/V-4: el contenido de la sección generada es la regla NATIVA del
    orquestador, así que su etiqueta deja de decir «Delegation (adapter)»."""

    def test_pd20_generated_delegation_label_drops_the_adapter_qualifier(
            self) -> None:
        """PD-20/V-4: orquestadores generados (staging), ambos runtimes."""
        for runtime, rel, _committed in RUNTIMES:
            with self.subTest(runtime=runtime):
                text = read_recomputed(rel, f"PD-20/V-4 {runtime}")
                offenders = ADAPTER_LABEL_RE.findall(text)
                self.assertEqual(
                    offenders,
                    [],
                    msg=(
                        f"PD-20/V-4 ({runtime}): el generado todavía titula "
                        "«Delegation (adapter)» un contenido que es la regla "
                        f"nativa del orquestador: {offenders!r}"
                    ),
                )
                self.assertRegex(
                    text,
                    DELEGATION_HEADING_RE,
                    msg=(
                        f"PD-20/V-4 ({runtime}): el generado no conserva "
                        "ninguna sección de delegación (la etiqueta se "
                        "corrige, la sección no se borra)"
                    ),
                )


# ---------------------------------------------------------------------------
# Test 7 — PD-20 / plan U4: `make staging` determinista + paridad con agents/**
# ---------------------------------------------------------------------------


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _run_make_staging(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", "staging"],
        cwd=str(root),
        text=True,
        capture_output=True,
        check=False,
    )


_STAGING_COPY: Path | None = None


def _recomputed_root() -> Path:
    """Copia temporal del checkout con `make staging` ejecutado (nunca escribe
    en el repo): el generado que evalúan los oráculos es RECOMPUTADO."""
    global _STAGING_COPY
    if _STAGING_COPY is None:
        tmp = tempfile.mkdtemp(prefix="cdad-006-005-u4-")
        atexit.register(shutil.rmtree, tmp, ignore_errors=True)
        copy = Path(tmp) / "product"
        shutil.copytree(
            REPO_ROOT,
            copy,
            symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", ".pytest_cache", "__pycache__", "build"
            ),
        )
        run = _run_make_staging(copy)
        manifest = copy / "build" / "staging" / "manifest.json"
        if run.returncode != 0 or not manifest.is_file():
            raise AssertionError(
                "PD-20: `make staging` no generó el staging en la copia del "
                f"fixture (rc={run.returncode}): "
                f"{run.stdout[-400:]!r} {run.stderr[-400:]!r}"
            )
        _STAGING_COPY = copy
    return _STAGING_COPY


class TestPd20DeterministicStaging(unittest.TestCase):
    """PD-20/plan U4: `make staging` es determinista (dos corridas, mismos
    bytes) y el generado coincide con la fuente recomputada (salidas
    declaradas `agents/**`, nunca editadas a mano)."""

    def test_pd20_staging_is_deterministic_and_matches_committed_outputs(
            self) -> None:
        """PD-20/plan U4: determinismo + paridad fuente↔generado."""
        root = _recomputed_root()
        first = _run_make_staging(root)
        self.assertEqual(
            first.returncode,
            0,
            msg=(
                "PD-20/plan U4: `make staging` falló en la copia del fixture "
                f"(rc={first.returncode}): {first.stderr.strip()[-500:]!r}"
            ),
        )
        agents_dir = root / "build" / "staging" / "agents"
        self.assertTrue(
            agents_dir.is_dir(),
            msg=(
                "PD-20/plan U4: `make staging` no publicó "
                "build/staging/agents/ en la copia del fixture"
            ),
        )
        before = _tree_hashes(agents_dir)
        self.assertTrue(before, msg="PD-20/plan U4: el staging no publicó agentes")

        second = _run_make_staging(root)
        self.assertEqual(
            second.returncode,
            0,
            msg=(
                "PD-20/plan U4: la segunda corrida de `make staging` falló "
                f"(rc={second.returncode}): {second.stderr.strip()[-500:]!r}"
            ),
        )
        after = _tree_hashes(agents_dir)
        self.assertEqual(
            sorted(before),
            sorted(after),
            msg=(
                "PD-20/plan U4: `make staging` no es determinista — las dos "
                "corridas publicaron conjuntos de archivos distintos"
            ),
        )
        for rel in sorted(before):
            self.assertEqual(
                before[rel],
                after[rel],
                msg=(
                    f"PD-20/plan U4: `make staging` no es determinista — "
                    f"{rel} cambió entre dos corridas idénticas"
                ),
            )

        # Paridad fuente↔generado: cada salida declarada coincide byte a byte
        # con la recomputación; el generado no se edita a mano.
        for runtime, _rel, committed_dir in RUNTIMES:
            with self.subTest(runtime=runtime):
                staged_dir = agents_dir / runtime
                staged_names = sorted(p.name for p in staged_dir.glob("*.md"))
                self.assertEqual(
                    staged_names,
                    sorted(AGENT_NAMES),
                    msg=(
                        f"PD-20/plan U4 ({runtime}): el staging no publicó "
                        "exactamente los 11 agentes declarados"
                    ),
                )
                for name in AGENT_NAMES:
                    committed = committed_dir / name
                    self.assertTrue(
                        committed.is_file(),
                        msg=(
                            f"PD-20/plan U4 ({runtime}): la salida declarada "
                            f"{committed.relative_to(REPO_ROOT).as_posix()} no "
                            "existe (los agentes son salidas de `make agents`)"
                        ),
                    )
                    self.assertEqual(
                        (staged_dir / name).read_bytes(),
                        committed.read_bytes(),
                        msg=(
                            f"PD-20/plan U4 ({runtime}): "
                            f"{committed.relative_to(REPO_ROOT).as_posix()} no "
                            "coincide byte a byte con la salida recomputada — "
                            "el generado está desincronizado de la fuente "
                            "(editar sources/ y regenerar; nunca a mano)"
                        ),
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
