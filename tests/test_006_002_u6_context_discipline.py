#!/usr/bin/env python3
"""006-002 U6 RED — disciplina de contexto de los orquestadores (PD-6; INV-4).

Contrato (oráculo — nada se deriva de la implementación):
- ``docs/specs/006-002-delegation-by-layer/spec.md`` §2 **PD-6** (las cuatro
  reglas de contexto en AMBOS orquestadores generados con staging `basic`;
  `references/orientation.md` §1 sigue siendo el dueño de «vista primero» y el
  orquestador lo CITA sin duplicarlo) y §3 **INV-4** (`/tmp` no es canal ni
  espacio de trabajo; el recibo va a `.cdad/inbox` y los temporales al
  workspace declarado).
- ``docs/specs/006-002-delegation-by-layer/plan.md`` ficha **U6** (archivos:
  la sección directiva de ``sources/roles/orchestrator.md``, ``references/
  orientation.md`` §1 como dueño de «vista primero», y una frase de ``SKILL.md``
  que las referencia; regresiones declaradas ``tests/validate-consistency.sh`` y
  ``tests/test_005_009_t3_spawn_reconciliation.py``) + **enmienda A-1** (los
  asserts acoplados de la superficie de esta unidad se reformulan en ESTE RED,
  nunca en el GREEN) + el encargo del packet U6 (las cuatro reglas, con los
  conceptos y no las frases).

Las CUATRO reglas de contexto que PD-6 exige en cada orquestador generado:
  (1) orientarse primero con la vista compacta `status`, sin volcar el state,
      el ledger ni la skill completa;
  (2) rotar la sesión en los bordes de tarea, no a mitad de una unidad;
  (3) no reparar por su cuenta: si un rol devuelve algo roto o incompleto se
      re-despacha al rol nombrando el defecto; el orquestador no escribe
      reparaciones;
  (4) nunca `/tmp` como canal ni espacio de trabajo (la alternativa sancionada
      es `.cdad/inbox` / el workspace declarado).

Superficie observable (caja negra, consumidor): la salida GENERADA
``build/staging/agents/{opencode,claude-code}/cdad-orchestrator.md`` producida
con ``make staging PROFILE=basic`` en una COPIA temporal del checkout (fixture
de U1, patrón de ``tests/product_staging.py``: nunca se escribe en el repo) y el
texto INSTALABLE del árbol (``skills/**`` + los agentes generados ``agents/**``)
para el oráculo de ausencia de INV-4. El test-writer NO leyó implementación
(``skills/``, ``sources/``, ``scripts/``, ``agents/``) para derivar aserciones:
los oráculos salen del spec y del plan; los artefactos se leen al EJECUTARSE.

Marcadores = conceptos con alternativas de idioma (patrón ``require_any`` de
``tests/test_005_010_t3_references.py``/u1/u2), nunca frases exactas, con dos
nombres normativos que el contrato fija: ``orientation.md`` (§1, dueño de «vista
primero») y ``/tmp`` (el token literal de INV-4). La forma de la prosa la
verifica el review de stage 4.

Co-ubicación (anti-falso-verde): una regla debe declararse en su PROPIA unidad
—bloque separado por línea en blanco, subdividido en cada ítem de lista o
encabezado—, no repartida por el documento. Si ninguna unidad sola reúne los
conceptos, se admite una ventana ±10 líneas alrededor de un ancla propia de la
regla (respaldo declarado: tolera sub-ítems de la misma regla sin volver
trivial el oráculo).

Mapa test → postcondición (un test por regla observable):

  1 ``TestPd6Rule1OrientationFirst::test_pd6_rule1_orient_first_with_the_compact_status_view_without_dumps``   PD-6(1)
  2 ``TestPd6Rule2SessionRotation::test_pd6_rule2_rotate_the_session_at_task_boundaries_not_mid_unit``          PD-6(2)
  3 ``TestPd6Rule3NoSelfRepair::test_pd6_rule3_no_self_repair_redispatch_the_role_naming_the_defect``           PD-6(3)
  4 ``TestPd6Rule4NoTmp::test_pd6_rule4_never_tmp_as_channel_or_workspace``                                     PD-6(4)/INV-4
  5 ``TestPd6Rule4NoTmp::test_pd6_rule4_declares_the_sanctioned_alternative_to_tmp``                            PD-6(4)/INV-4
  6 ``TestPd6OrientationOwnerCited::test_pd6_orchestrators_reference_the_view_first_owner``                     PD-6 (cita, no duplica)
  7 ``TestPd6NoTmpInstructionInInstallableText::test_pd6_no_installable_text_instructs_tmp``                    PD-6(4)/INV-4 (oráculo de ausencia)

RED observado contra el árbol vigente (U1–U5 en GREEN, U6 sin implementar) —
OBSERVADO ejecutando este módulo, todo fallo es AssertionError de contenido,
nunca ImportError/SyntaxError ni fallo del fixture:

  (1) FALLA: el orquestador tiene los tres conceptos del documento pero NO
      co-ubicados en una misma unidad/ventana — la regla no está declarada
      como regla.
  (2) FALLA: concepto ausente `no a mitad de la unidad`.
  (3) FALLA: concepto ausente `no auto-reparación`.
  (4) FALLA (ambas mitades): los orquestadores generados no mencionan `/tmp`
      en absoluto.
  (6) GUARD pre-satisfecho declarado (OBSERVADO verde): la cita a
      `references/orientation.md` ya existe en los dos orquestadores
      generados (no la introduce U6); el test la protege contra degradación.
      Que la sección citada siga siendo el DUEÑO de «vista primero» y que el
      orquestador no la duplique es prosa: la verifica el review de stage 4.
  (7) GUARD pre-satisfecho declarado (OBSERVADO verde): ningún texto
      instalable del árbol actual (`skills/**` + `agents/**`) manda usar
      `/tmp`; el oráculo de ausencia de INV-4 se conserva contra la
      degradación futura.

Sin reformulación de acoplados en este RED (enmienda A-1): U6 AGREGA texto
(la sección directiva del orquestador fuente, §1 de `orientation.md` y una
frase de `SKILL.md`) y no cambia ninguno de los textos que fijan
`tests/test_005_009_t3_spawn_reconciliation.py` (conservación del SPAWN GUARD,
anti-recursión, distinción de delegación externa, escritor único del state,
paridad fuente↔generado) ni `tests/validate-consistency.sh` (F001/F004/F007/
F010/F011): no fijan las reglas de contexto. Ambos se corren como regresión.
La paridad fuente↔generado sí depende de que el GREEN regenere los agentes
(`make agents`), que es su trabajo, no una reformulación de tests.

Límite honesto (PD-6): el test prueba que la regla EXISTE, no que se OBEDEZCA.
La única evidencia de comportamiento es el transcript de la corrida de
aceptación (U8) y es una muestra.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Reuso declarado (una sola definición de cada helper/constante, patrón
# u2→u5): el fixture de staging `basic` y las rutas de los orquestadores
# generados de u1; el oráculo de conceptos `require_any` de u2.
from tests.test_006_002_u1_delegation_section import (
    CC_ORCH_REL,
    OC_ORCH_REL,
    basic_staging_root,
)
from tests.test_006_002_u2_neutral_skill import require_any

REPO_ROOT = Path(__file__).resolve().parents[1]

# Texto INSTALABLE (INV-4): la capa del skill y los agentes generados que el
# instalador copia. `docs/**` queda fuera (evidencia no instalable, PD-9).
INSTALLABLE_SUFFIXES = (".md", ".json", ".sh", ".py", ".yaml", ".yml")

# Alternativa sancionada y su negación (INV-4: «el recibo va a `.cdad/inbox` y
# los temporales al workspace declarado»).
TMP_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_.])/tmp(?![A-Za-z0-9_])")
# Marcas que vuelven VÁLIDA una mención de `/tmp` (la prohíben o la excluyen):
# negación/evitación, o exclusión explícita («outside», «instead of»).
PROHIBITIVE_RE = re.compile(
    r"(?i)\b(?:no|not|never|without|nunca|jam[áa]s|sin|avoid|evitar|"
    r"prohibited|forbidden|prohibido|must not|do not|don'?t|"
    r"outside|fuera de|instead of|en lugar de)\b"
)
TMP_PROHIBITION_RE = re.compile(
    r"(?i)(?:\bnever\b|\bnot\b|\bno\b|\bnunca\b|\bjam[áa]s\b|\bsin\b|"
    r"\bmust not\b|\bdo not\b|\bprohibited\b|\bforbidden\b)"
    r"[^.\n]{0,60}/tmp"
    r"|/tmp[^.\n]{0,60}"
    r"(?:\bis not\b|\bare not\b|\bis never\b|\bis forbidden\b|"
    r"\bis prohibited\b|\bno es\b|\bnunca\b|\bjam[áa]s\b|\bprohibido\b)"
)

# Marcas de la alternativa sancionada (INV-4/PD-6 regla 4): el inbox fijo del
# recibo o el workspace declarado. `.cdad/inbox` es un nombre normativo.
SANCTIONED_ALTERNATIVE_RE = re.compile(
    r"(?i)\.cdad/inbox|cdad/inbox|declared workspace|workspace declarado|"
    r"espacio de trabajo declarado|the workspace declared|the declared workspace"
)

# Igual que en u5: las marcas se combinan por CONCEPTO, no por frase; los
# patrones de las reglas son ventanas de negación acotadas en la misma línea y
# exigen además la co-ubicación con los conceptos hermanos de su regla.


def rx(*tokens: str) -> re.Pattern:
    """Concepto con alternativas de idioma (una sola definición)."""
    return re.compile("|".join(re.escape(token) for token in tokens),
                      re.IGNORECASE)


# --------------------------------------------------------------- regla 1
ORIENT_FIRST = rx("orient", "orientation", "orientarse", "view first",
                  "vista primero", "first read", "read first", "primero se lee",
                  "primero leer", "before acting", "antes de actuar")
COMPACT_STATUS_VIEW = rx("`status`", "status view", "compact status",
                         "compact view", "compact-view", "vista compacta",
                         "resumen compacto", "compact summary")
NO_DUMP_RE = re.compile(
    r"(?i)(?:\bno\b|\bnot\b|\bnever\b|\bwithout\b|\bnunca\b|\bjam[áa]s\b|"
    r"\bsin\b|\bdo not\b|\bmust not\b|\bavoid\b)"
    r"[^.\n]{0,90}?"
    r"(?:\bdump|\bvolcar|\bvolc|\bentire\b|\bwhole\b|\bfull\b|\bcompleto|"
    r"\bcompleta|\bentero|\bledger\b|\blibro mayor\b|"
    r"\bread the (?:state|ledger|skill))"
)

# --------------------------------------------------------------- regla 2
SESSION_ROTATION = rx("rotate", "rotation", "rotación", "rotar",
                      "fresh session", "new session", "nueva sesión",
                      "sesion nueva", "restart the session", "restart session",
                      "reiniciar la sesión", "session rotation")
TASK_BOUNDARY = rx("boundar", "frontera", "between units", "between tasks",
                   "entre unidades", "entre tareas", "end of the unit",
                   "unit ends", "task ends", "task boundary", "unit boundary",
                   "límite de tarea", "limite de tarea", "límite de unidad",
                   "limite de unidad", "cierre de la unidad",
                   "cierre de tarea", "after the unit", "al cerrar la unidad")
NOT_MID_UNIT_RE = re.compile(
    r"(?i)(?:\bnever\b|\bnot\b|\bno\b|\bnunca\b|\bjam[áa]s\b|\bsin\b|"
    r"\bmust not\b|\bdo not\b)"
    r"[^.\n]{0,60}?"
    r"(?:mid-?unit|mid-?task|middle of (?:the )?(?:unit|task|a unit)|"
    r"in the middle|a mitad de|mitad de la (?:unidad|tarea|trabajo))"
)

# --------------------------------------------------------------- regla 3
NO_SELF_REPAIR_RE = re.compile(
    r"(?i)(?:\bnever\b|\bnot\b|\bno\b|\bnunca\b|\bjam[áa]s\b|\bsin\b|"
    r"\bdoes not\b|\bdo not\b|\bdoesn'?t\b|\bmust not\b)"
    r"[^.\n]{0,60}?"
    r"(?:self-?repair|auto-?repair|autorrepar|autorepar|self-?fix|repair|"
    r"reparar|arreglar|\bfix\b)"
)
REDISPATCH = rx("re-dispatch", "redispatch", "re dispatch", "dispatch again",
                "re-delegate", "redelegate", "re-despachar", "redespachar",
                "volver a despachar", "dispatch the role again",
                "dispatch it again", "send it back", "return it to the",
                "devolver al rol", "back to the role", "back to that role",
                "otra vez al rol", "retry the dispatch")
NAMES_THE_DEFECT = rx("naming the defect", "name the defect",
                      "nombrando el defecto", "nombrar el defecto",
                      "stating the defect", "cite the defect",
                      "describing the defect", "with the defect",
                      "con el defecto", "defect", "defecto", "what failed",
                      "qué falló", "que fallo", "the failure", "la falla",
                      "broken", "roto", "incomplete", "incompleto",
                      "no cumple", "not complete")

# --------------------------------------------------------------- regla 4
TMP_MENTION = rx("/tmp")
SANCTIONED_ALTERNATIVE = SANCTIONED_ALTERNATIVE_RE

# Un grupo de una regla = (concepto, patrón). La regla se declara cuando TODOS
# los grupos co-ubican en una misma unidad (o, en su defecto, en una ventana).
RULE1_GROUPS = (("vista primero / orientarse primero", ORIENT_FIRST),
                ("vista compacta `status`", COMPACT_STATUS_VIEW),
                ("prohibición de volcar state/ledger/skill completa", NO_DUMP_RE))
RULE2_GROUPS = (("rotación de la sesión", SESSION_ROTATION),
                ("borde de tarea/unidad", TASK_BOUNDARY),
                ("no a mitad de la unidad", NOT_MID_UNIT_RE))
RULE3_GROUPS = (("no auto-reparación", NO_SELF_REPAIR_RE),
                ("re-despacho", REDISPATCH),
                ("nombra el defecto", NAMES_THE_DEFECT))
RULE4_GROUPS = (("mención de `/tmp`", TMP_MENTION),
                ("prohibición co-ubicada de `/tmp`", TMP_PROHIBITION_RE))
RULE4_ALTERNATIVE_GROUPS = (("prohibición co-ubicada de `/tmp`", TMP_PROHIBITION_RE),
                            ("alternativa sancionada (inbox/workspace declarado)",
                             SANCTIONED_ALTERNATIVE))

H2_RE = re.compile(r"(?m)^#{1,6}[ \t]")
LIST_ITEM_RE = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]")


def read(path: Path, why: str) -> str:
    """Artefacto declarado por el contrato: existe y no está vacío."""
    assert path.is_file(), (
        f"{why}: el artefacto declarado por el contrato no existe (drift de la "
        f"superficie): {path.relative_to(REPO_ROOT).as_posix()}"
    )
    text = path.read_text(encoding="utf-8")
    assert text.strip(), (
        f"{why}: el artefacto declarado está vacío: "
        f"{path.relative_to(REPO_ROOT).as_posix()}"
    )
    return text


def rule_units(text: str) -> list[str]:
    """Unidades de regla: bloques separados por línea en blanco, subdivididos
    en cada ítem de lista (``-``/``*``/``1.``) o encabezado. Una regla debe
    declararse en su propia unidad, no repartida por el documento."""
    units: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if any(line.strip() for line in current):
            units.append("\n".join(current))
        current.clear()

    for line in text.splitlines():
        if not line.strip():
            flush()
            continue
        if H2_RE.match(line) or LIST_ITEM_RE.match(line):
            flush()
        current.append(line)
    flush()
    return units


def rule_region(text: str, groups: tuple[tuple[str, re.Pattern], ...],
                anchor: re.Pattern, window: int = 10) -> str | None:
    """Región que co-ubica TODOS los grupos de una regla: primero una unidad
    de regla sola; si ninguna la reúne, una ventana ±`window` alrededor de una
    línea-ancla propia de la regla (respaldo declarado)."""
    for unit in rule_units(text):
        if all(pattern.search(unit) for _, pattern in groups):
            return unit
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not anchor.search(line):
            continue
        lo, hi = max(0, index - window), min(len(lines), index + window + 1)
        chunk = "\n".join(lines[lo:hi])
        if all(pattern.search(chunk) for _, pattern in groups):
            return chunk
    return None


def assert_rule(text: str, label: str, rule: str,
                groups: tuple[tuple[str, re.Pattern], ...],
                anchors: tuple[re.Pattern, ...]) -> None:
    """La regla `rule` de PD-6 debe estar declarada en `text`: todos sus
    conceptos co-ubicados. El mensaje distingue «falta el concepto» de «está
    pero no co-ubicado» (drift de la superficie vs. redacción dispersa)."""
    for anchor in anchors:
        if rule_region(text, groups, anchor):
            return
    absent = [name for name, pattern in groups if not pattern.search(text)]
    if absent:
        raise AssertionError(
            f"PD-6 ({label}): la regla «{rule}» no está declarada — conceptos "
            f"ausentes: {absent}"
        )
    raise AssertionError(
        f"PD-6 ({label}): la regla «{rule}» tiene sus conceptos en el "
        "documento pero NO co-ubicados en una misma unidad/ventana "
        f"({[name for name, _ in groups]!r}): la regla no puede quedar "
        "dispersa por el documento"
    )


class U6Case(unittest.TestCase):
    """Base del oráculo U6: lee los orquestadores generados (staging `basic`)."""

    def orchestrator(self, rel: Path) -> tuple[str, str]:
        root = basic_staging_root()
        label = rel.parent.parent.name + "/" + rel.parent.name
        return read(root / rel, f"PD-6 staging basic ({label})"), label


# ------------------------------- PD-6(1) — vista primero, sin volcar nada


class TestPd6Rule1OrientationFirst(U6Case):
    """PD-6 regla 1: el orquestador se orienta PRIMERO con la vista compacta
    `status` y NO vuelca el state, el ledger ni la skill completa."""

    def test_pd6_rule1_orient_first_with_the_compact_status_view_without_dumps(
            self) -> None:
        """PD-6(1): ambos orquestadores generados declaran la vista primero
        (compacta, `status`) y su prohibición de volcar state/ledger/skill."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                assert_rule(text, label, "orientarse primero con la vista "
                                         "compacta `status`, sin volcar el "
                                         "state/ledger/skill completa",
                            RULE1_GROUPS, (ORIENT_FIRST, COMPACT_STATUS_VIEW))


# -------------------- PD-6(2) — rotar la sesión en los bordes de tarea


class TestPd6Rule2SessionRotation(U6Case):
    """PD-6 regla 2: la sesión rota en los BORDES de tarea/unidad, no a mitad
    de una unidad."""

    def test_pd6_rule2_rotate_the_session_at_task_boundaries_not_mid_unit(
            self) -> None:
        """PD-6(2): ambos orquestadores generados declaran la rotación de
        sesión co-ubicada con el borde de tarea y con la prohibición de rotar
        a mitad de la unidad."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                assert_rule(text, label, "rotar la sesión en los bordes de "
                                         "tarea, no a mitad de la unidad",
                            RULE2_GROUPS, (SESSION_ROTATION, NOT_MID_UNIT_RE))


# ------------- PD-6(3) — no reparar por su cuenta: re-despacho al rol


class TestPd6Rule3NoSelfRepair(U6Case):
    """PD-6 regla 3: el orquestador NO repara por su cuenta; re-despacha al
    mismo rol nombrando el defecto y no escribe reparaciones."""

    def test_pd6_rule3_no_self_repair_redispatch_the_role_naming_the_defect(
            self) -> None:
        """PD-6(3): ambos orquestadores generados declaran la prohibición de
        auto-reparación co-ubicada con el re-despacho al rol nombrando el
        defecto."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                assert_rule(text, label, "no reparar por su cuenta: "
                                         "re-despachar al rol nombrando el "
                                         "defecto",
                            RULE3_GROUPS, (REDISPATCH, NO_SELF_REPAIR_RE))


# ------------------ PD-6(4)/INV-4 — nunca `/tmp` como canal/workspace


class TestPd6Rule4NoTmp(U6Case):
    """PD-6 regla 4/INV-4: `/tmp` NUNCA es canal ni espacio de trabajo, y la
    regla nombra la alternativa sancionada (`.cdad/inbox` / workspace
    declarado)."""

    def test_pd6_rule4_never_tmp_as_channel_or_workspace(self) -> None:
        """PD-6(4)/INV-4: ambos orquestadores generados declaran la mención de
        `/tmp` co-ubicada con su prohibición («nunca como canal ni espacio de
        trabajo»)."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                assert_rule(text, label, "nunca `/tmp` como canal ni espacio "
                                         "de trabajo",
                            RULE4_GROUPS, (TMP_MENTION, TMP_PROHIBITION_RE))

    def test_pd6_rule4_declares_the_sanctioned_alternative_to_tmp(self) -> None:
        """PD-6(4)/INV-4: la prohibición de `/tmp` nombra la alternativa
        sancionada (`.cdad/inbox` o el workspace declarado) — prohibir sin
        declarar el canal válido deja al orquestador sin ruta."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                assert_rule(text, label, "alternativa sancionada a `/tmp` "
                                         "(`.cdad/inbox` / workspace declarado)",
                            RULE4_ALTERNATIVE_GROUPS,
                            (TMP_PROHIBITION_RE, SANCTIONED_ALTERNATIVE))


# ------------------- PD-6 — orientation.md §1 sigue siendo el dueño


class TestPd6OrientationOwnerCited(U6Case):
    """PD-6/plan U6: `references/orientation.md` §1 sigue siendo el dueño de
    «vista primero»; los orquestadores lo CITAN (referencia presente)
    co-ubicada con el concepto, sin duplicar la regla."""

    def test_pd6_orchestrators_reference_the_view_first_owner(self) -> None:
        """PD-6: cada orquestador generado referencia `orientation.md`
        co-ubicado con el concepto de vista primero / vista compacta.

        La ausencia de DUPLICACIÓN del §1 es prosa: la verifica el review de
        stage 4 (límite honesto declarado en el docstring del módulo)."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                self.assertIn(
                    "orientation.md", text.lower(),
                    msg=(f"PD-6 ({label}): el orquestador no referencia "
                         "`references/orientation.md` (dueño de «vista "
                         "primero»); el orquestador debe CITAR al dueño, no "
                         "re-declarar la regla"),
                )
                assert_rule(
                    text, label, "cita al dueño de «vista primero» "
                                 "(orientation.md) co-ubicada con el concepto",
                    (("referencia a orientation.md", rx("orientation.md")),
                     ("concepto de vista primero", ORIENT_FIRST)),
                    (rx("orientation.md"),),
                )


# ----------------- PD-6(4)/INV-4 — oráculo de ausencia en texto instalable


class TestPd6NoTmpInstructionInInstallableText(unittest.TestCase):
    """PD-6 regla 4/INV-4: ningún texto INSTALABLE (`skills/**` + los agentes
    generados `agents/**`) manda usar `/tmp` como canal ni espacio de trabajo.
    Las menciones que lo PROHÍBEN (o lo excluyen explícitamente) son válidas."""

    def installable_files(self) -> list[Path]:
        files: list[Path] = []
        for root in (REPO_ROOT / "skills", REPO_ROOT / "agents"):
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*")):
                if path.is_file() and path.suffix in INSTALLABLE_SUFFIXES:
                    files.append(path)
        return files

    def test_pd6_no_installable_text_instructs_tmp(self) -> None:
        """PD-6(4)/INV-4: cada mención de `/tmp` en texto instalable está en un
        bloque que la prohíbe o la excluye; una mención prescriptiva es una
        violación (el canal es `.cdad/inbox` y los temporales el workspace
        declarado)."""
        files = self.installable_files()
        self.assertTrue(
            files,
            msg="PD-6(4)/INV-4: no se localizó texto instalable bajo skills/ y "
                "agents/ (drift de la superficie del oráculo de ausencia)",
        )
        offenders: list[str] = []
        for path in files:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if "/tmp" not in text.lower():
                continue
            relative = path.relative_to(REPO_ROOT).as_posix()
            for number, block in enumerate(re.split(r"\n\s*\n", text), start=1):
                for line in block.splitlines():
                    if not TMP_TOKEN_RE.search(line):
                        continue
                    if PROHIBITIVE_RE.search(block):
                        continue
                    offenders.append(f"{relative}:{number} → {line.strip()}")
        self.assertEqual(
            offenders, [],
            msg=("PD-6(4)/INV-4: texto instalable que manda usar `/tmp` como "
                 "canal o espacio de trabajo (las menciones que lo prohíben son "
                 f"válidas): {offenders!r}"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
