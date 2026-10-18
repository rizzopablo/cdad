#!/usr/bin/env python3
"""006-002 U6 RED — disciplina de contexto de los orquestadores (PD-6; INV-4).

Contrato (oráculo — nada se deriva de la implementación):
- ``docs/specs/006-002-delegation-by-layer/spec.md`` §2 **PD-6** (las cuatro
  reglas de contexto en AMBOS orquestadores generados con staging;
  `references/orientation.md` §1 sigue siendo el dueño de «vista primero» y el
  orquestador lo CITA sin duplicarlo) y §3 **INV-4**, ambos leídos con la
  **«Enmienda 002 — `/tmp` fuera de la metodología»** (aprobada por el dueño,
  2026-10-17; REEMPLAZA la enmienda 001): la limitación de `/tmp` era de un
  servidor concreto (aislamiento por proceso del SO), no de la metodología, y
  otros usuarios no la tienen. **PD-6 regla (4)** e **INV-4** quedan así: lo
  que debe durar, dejar evidencia o leerlo otro proceso o rol (artefactos,
  recibos, registros de corrida) va a rutas ESTABLES del workspace del
  proyecto — `.cdad/inbox` para el recibo y el workspace declarado para lo
  demás —; y **ningún texto instalable nombra `/tmp`** (ni para prohibirlo ni
  para admitirlo).
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
  (4) rutas estables para lo que debe durar (enmienda 002): lo que debe durar,
      dejar evidencia o leerlo otro proceso o rol va a rutas estables del
      workspace del proyecto (`.cdad/inbox` para el recibo; el workspace
      declarado para lo demás). `/tmp` queda FUERA de la metodología: no se
      nombra en el texto instalable, ni para prohibirlo ni para admitirlo.

Superficie observable (caja negra, consumidor): la salida GENERADA
``build/staging/agents/{opencode,claude-code}/cdad-orchestrator.md`` producida
con ``make staging PROFILE=basic`` en una COPIA temporal del checkout (fixture
de U1, patrón de ``tests/product_staging.py``: nunca se escribe en el repo), y
el texto INSTALABLE del árbol (``skills/**``, los agentes generados
``agents/**`` y los agentes/orquestadores generados con staging) para
el oráculo de ausencia de `/tmp` de INV-4. El test-writer NO leyó
implementación (``skills/``, ``sources/``, ``scripts/``, ``agents/``) para
derivar aserciones: los oráculos salen del spec y del plan; los artefactos se
leen al EJECUTARSE.

Marcadores = conceptos con alternativas de idioma (patrón ``require_any`` de
``tests/test_005_010_t3_references.py``/u1/u2), nunca frases exactas, con dos
nombres normativos que el contrato fija: ``orientation.md`` (§1, dueño de «vista
primero») y ``.cdad/inbox`` (la ruta del recibo, PD-5/INV-4). El token ``/tmp``
deja de ser un marcador de la regla 4 (enmienda 002: no se nombra) y pasa a ser
el objeto del ORÁCULO DE AUSENCIA del texto instalable. La forma de la prosa la
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
  4 ``TestPd6Rule4StableWorkspacePaths::test_pd6_rule4_durable_evidence_and_cross_role_reads_go_to_stable_workspace_paths``   PD-6(4)/INV-4 (enmienda 002, (a))
  5 ``TestPd6OrientationOwnerCited::test_pd6_orchestrators_reference_the_view_first_owner``                     PD-6 (cita, no duplica)
  6 ``TestPd6NoTmpInInstallableText::test_pd6_no_installable_text_names_tmp``                                   PD-6(4)/INV-4 (enmienda 002, (b) — oráculo de ausencia)

RED observado contra el árbol vigente (U1–U6 en GREEN: los orquestadores ya
declaran las cuatro reglas; la **enmienda 001** había relativizado la regla 4
MANTENIENDO la mención de `/tmp`, y la **enmienda 002** la reemplaza: `/tmp`
sale de la metodología) — OBSERVADO ejecutando este módulo, todo fallo es
AssertionError de CONTENIDO, nunca ImportError/SyntaxError ni fallo del fixture:

  (1)-(3) GUARD pre-satisfecho declarado (OBSERVADO verde): las reglas 1–3 ya
      están declaradas y co-ubicadas; los tests las protegen contra degradación.
  (4)/(a) GUARD pre-satisfecho declarado (OBSERVADO verde): la regla de rutas
      estables (lo durable / la evidencia / lo que lee otro proceso o rol →
      rutas estables del workspace con `.cdad/inbox` para el recibo) ya está
      declarada y co-ubicada en ambos orquestadores generados — la dejó el
      GREEN de la enmienda 001 y la enmienda 002 la CONSERVA (es su mitad
      superviviente: solo retira la mención de `/tmp`). El test la protege
      contra degradación.
  (5) GUARD pre-satisfecho declarado (OBSERVADO verde): la cita a
      `references/orientation.md` ya existe en los dos orquestadores
      generados (no la introduce U6); el test la protege contra degradación.
      Que la sección citada siga siendo el DUEÑO de «vista primero» y que el
      orquestador no la duplique es prosa: la verifica el review de stage 4.
  (6)/(b) FALLA por AssertionError de CONTENIDO (OBSERVADO: 6 ofensores en la
      corrida): el texto instalable del árbol vigente NOMBRA `/tmp` — la capa
      del skill (`skills/cdad-cycle/SKILL.md:174`, el puntero de «context
      discipline»; `skills/cdad-cycle/references/handoff-prompts.md:628`, los
      run logs) y los agentes generados (`agents/cdad-orchestrator.md:102`,
      `agents/claude-code/cdad-orchestrator.md:107` y sus equivalentes en el
      staging, el ítem «`/tmp` only for ephemeral drafts of one same
      process» de la enmienda 001) —, que es exactamente lo que la enmienda 002
      retira del texto instalable. La aserción enumera cada archivo:línea
      ofensor (el árbol observado nombra `/tmp`; contra un árbol ya saneado la
      lista queda vacía y el test pasa).

Reformulación de acoplados (enmienda A-1) y alcance de este RED: se reformula la
superficie de SU unidad — los tres oráculos de la regla 4/INV-4 de este módulo
(enmienda 001 → enmienda 002). `grep -rn "/tmp" tests/*.py tests/*.sh` (pedido
por el encargo): NINGÚN otro test del repo exige una mención de `/tmp` en texto
instalable (ni el «never `/tmp`» del orquestador ni el permiso acotado), así que
no se reformula ninguna otra superficie: las demás apariciones de `/tmp` en
`tests/` son fixtures de `temporary_roots`/tempdirs, rutas absolutas del
path-policy y menciones dentro de docstrings de los propios tests — usos de los
tests, que no se tocan. `tests/validate-consistency.sh` (cero apariciones de
`/tmp`) y `tests/test_005_009_t3_spawn_reconciliation.py` no fijan las reglas de
contexto: se corren como regresión. La paridad fuente↔generado sí depende de que
el GREEN regenere los agentes (`make agents`), que es su trabajo, no una
reformulación de tests.

Límite honesto (PD-6): el test prueba que la regla EXISTE y que `/tmp` NO se
nombra, no que la regla se OBEDEZCA. La única evidencia de comportamiento es el
transcript de la corrida de aceptación (U8) y es una muestra. El oráculo de
prosa de la regla 4 es heurístico sobre CONCEPTOS con alternativas
(co-ubicación de unidad/ventana); el oráculo de ausencia es literal sobre el
token `/tmp` (con límites de palabra, para no matchear `.cdad/tmp` ni
`temporary`). La redacción fina la verifica el review de stage 4.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Reuso declarado (una sola definición de cada helper/constante, patrón
# u2→u5): el fixture de staging y las rutas de los orquestadores
# generados de u1. Los conceptos con alternativas de idioma se construyen con
# `rx`/`assert_rule` de este módulo (mismo patrón `require_any` de u2).
from tests.test_006_002_u1_delegation_section import (
    CC_ORCH_REL,
    OC_ORCH_REL,
    staging_root,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# Texto INSTALABLE (INV-4, enmienda 002): la capa del skill, los agentes
# generados del repo y los agentes/orquestadores generados con staging.
# `docs/**` queda fuera (evidencia no instalable, PD-9).
INSTALLABLE_SUFFIXES = (".md", ".json", ".sh", ".py", ".yaml", ".yml")

# Token literal de `/tmp` (enmienda 002: objeto del oráculo de AUSENCIA). Los
# límites de palabra evitan matchear `.cdad/tmp`, `temporary` o `/tmpfoo`.
TMP_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_.])/tmp(?![A-Za-z0-9_])")

# ---- enmienda 002: conceptos de la regla 4 (rutas estables, sin `/tmp`) ----

# Lo durable / la evidencia / lo que lee OTRO proceso o rol: la CONDICIÓN que
# la regla 4 manda a rutas estables (el par «recibo»/«.cdad/inbox» tiene su
# propio grupo: no cuenta como condición de durabilidad).
DURABLE_OR_XPROCESS_RE = re.compile(
    r"(?i)(?:\bdurable\b|\bmust last\b|\blong-?lived\b|\bpersist(?:s|ent)?\b|"
    r"\bsurvive\b|\boutlive\b|\bleave (?:a )?(?:trace|record|evidence)\b|"
    r"\bevidence\b|\bevidencia\b|\bdebe durar\b|\bdebe permanecer\b|"
    r"\bdejar evidencia\b|\bsobrevivir\b|"
    r"\banother (?:process|role|session|agent)\b|"
    r"\bother (?:processes|roles|sessions|agents)\b|\bcross-?process\b|"
    r"\bcross-?role\b|\bbetween (?:processes|roles|sessions)\b|"
    r"\bread by (?:another|other)\b|\ble[íi]do por\b|"
    r"\botro (?:proceso|rol|sesi[óo]n|agente)\b|"
    r"\botros (?:procesos|roles|sesiones)\b|"
    r"\bentre (?:procesos|roles|sesiones)\b)"
)
# La ruta estable del workspace declarado (concepto, alternativas).
STABLE_WORKSPACE_PATH_RE = re.compile(
    r"(?i)(?:\bstable\b[^.\n]{0,30}\b(?:path|paths|location|workspace|"
    r"directory|place|root)\b|"
    r"\b(?:path|paths|location|workspace|directory|place|root)\b[^.\n]{0,30}"
    r"\bstable\b|"
    r"\bdeclared workspace\b|\bworkspace declared\b|\bdeclared path\b|"
    r"\bworkspace declarado\b|\brutas? (?:estables?|del workspace|de workspace)\b|"
    r"\bestables? del workspace\b|"
    r"\bpersistent (?:path|location|workspace|directory)\b|"
    r"\bdurable (?:path|location|directory)\b)"
)
# El recibo: `.cdad/inbox` es un nombre normativo (PD-5/INV-4).
RECEIPT_INBOX_RE = re.compile(r"(?i)\.cdad/inbox|cdad/inbox")

# Igual que en u5: las marcas se combinan por CONCEPTO, no por frase; la regla
# se declara cuando TODOS sus grupos co-ubican en una misma unidad (o, en su
# defecto, en una ventana alrededor de un ancla propia de la regla).
RULE4_GROUPS = (
    ("lo durable / la evidencia / lo que lee otro proceso o rol",
     DURABLE_OR_XPROCESS_RE),
    ("ruta estable del workspace declarado", STABLE_WORKSPACE_PATH_RE),
    ("recibo → `.cdad/inbox`", RECEIPT_INBOX_RE),
)


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
    """Base del oráculo U6: lee los orquestadores generados (staging)."""

    def orchestrator(self, rel: Path) -> tuple[str, str]:
        root = staging_root()
        label = rel.parent.parent.name + "/" + rel.parent.name
        return read(root / rel, f"PD-6 staging ({label})"), label


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


# -------- PD-6(4)/INV-4 (enmienda 002) — rutas estables, `/tmp` fuera


class TestPd6Rule4StableWorkspacePaths(U6Case):
    """PD-6 regla 4/INV-4 con la **enmienda 002** (dueño, 2026-10-17; reemplaza
    la enmienda 001): lo que debe durar, dejar evidencia o leerlo otro proceso
    o rol (artefactos, recibos, registros de corrida) va a rutas ESTABLES del
    workspace del proyecto — `.cdad/inbox` para el recibo y el workspace
    declarado para lo demás. El texto instalable NO nombra `/tmp`."""

    def test_pd6_rule4_durable_evidence_and_cross_role_reads_go_to_stable_workspace_paths(
            self) -> None:
        """PD-6 (enmienda 002): ambos orquestadores generados (staging)
        declaran que lo durable / la evidencia / lo que lee otro proceso o rol
        va a rutas ESTABLES del workspace del proyecto, co-ubicado con el
        recibo `.cdad/inbox` (la ruta válida del recibo; INV-4)."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                assert_rule(text, label, "lo que debe durar, dejar evidencia o "
                                         "leerlo otro proceso o rol va a rutas "
                                         "estables del workspace del proyecto, "
                                         "con `.cdad/inbox` para el recibo",
                            RULE4_GROUPS,
                            (DURABLE_OR_XPROCESS_RE, STABLE_WORKSPACE_PATH_RE,
                             RECEIPT_INBOX_RE))


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


# --- PD-6(4)/INV-4 (enmienda 002) — oráculo de ausencia: `/tmp` no se nombra


class TestPd6NoTmpInInstallableText(unittest.TestCase):
    """PD-6 regla 4/INV-4 (enmienda 002): NINGÚN texto INSTALABLE nombra `/tmp`,
    ni para prohibirlo ni para admitirlo — la limitación era del servidor del
    dueño, no de la metodología. Superficie: la capa del skill (`skills/**`),
    los agentes generados del repo (`agents/**`) y los orquestadores/agentes
    generados con staging (`build/staging/agents/**` en la copia del
    fixture de U1, nunca el repo)."""

    def installable_files(self) -> list[Path]:
        roots = (
            REPO_ROOT / "skills",
            REPO_ROOT / "agents",
            staging_root() / "build" / "staging" / "agents",
        )
        files: list[Path] = []
        for root in roots:
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*")):
                if path.is_file() and path.suffix in INSTALLABLE_SUFFIXES:
                    files.append(path)
        return files

    def display(self, path: Path) -> str:
        """Ruta legible: relativa al repo; el staging (fuera del repo,
        copia temporal del fixture) se prefija para no confundirlo con el
        árbol instalable del checkout."""
        for base, prefix in ((REPO_ROOT, ""),
                             (staging_root(), "staging/")):
            try:
                return prefix + path.relative_to(base).as_posix()
            except ValueError:
                continue
        return path.as_posix()

    def test_pd6_no_installable_text_names_tmp(self) -> None:
        """PD-6 (enmienda 002, (b)): ninguna línea de texto instalable nombra
        `/tmp` — ni una prohibición ni un permiso ni un uso: la regla 4 declara
        rutas estables del workspace (`.cdad/inbox` para el recibo) y `/tmp`
        queda fuera de la metodología."""
        files = self.installable_files()
        self.assertTrue(
            files,
            msg="PD-6(4)/INV-4 (enmienda 002): no se localizó texto instalable "
                "bajo skills/, agents/ ni el staging (drift de la "
                "superficie del oráculo de ausencia)",
        )
        offenders: list[str] = []
        for path in files:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if "/tmp" not in text.lower():
                continue
            for number, line in enumerate(text.splitlines(), start=1):
                if TMP_TOKEN_RE.search(line):
                    offenders.append(
                        f"{self.display(path)}:{number} → {line.strip()[:140]}"
                    )
        self.assertEqual(
            offenders, [],
            msg=("PD-6(4)/INV-4 (enmienda 002): texto instalable que nombra "
                 "`/tmp` (la limitación era del servidor del dueño, no de la "
                 "metodología: ni prohibirlo ni admitirlo pertenece al texto "
                 "instalable — lo que debe durar, dejar evidencia o leerlo "
                 "otro proceso o rol va a rutas estables del workspace del "
                 f"proyecto, `.cdad/inbox` para el recibo): {offenders!r}"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
