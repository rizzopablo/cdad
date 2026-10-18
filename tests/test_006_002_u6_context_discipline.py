#!/usr/bin/env python3
"""006-002 U6 RED — disciplina de contexto de los orquestadores (PD-6; INV-4).

Contrato (oráculo — nada se deriva de la implementación):
- ``docs/specs/006-002-delegation-by-layer/spec.md`` §2 **PD-6** (las cuatro
  reglas de contexto en AMBOS orquestadores generados con staging `basic`;
  `references/orientation.md` §1 sigue siendo el dueño de «vista primero» y el
  orquestador lo CITA sin duplicarlo) y §3 **INV-4**, ambos leídos con la
  **«Enmienda 001 — regla 4 de contexto»** (aprobada por el dueño, 2026-10-17):
  `/tmp` se ADMITE para borradores efímeros de un mismo proceso; lo que debe
  durar, dejar evidencia o leerlo otro proceso o rol va a rutas estables del
  workspace (`.cdad/inbox` para el recibo; el workspace declarado para lo
  demás), porque `/tmp` se limpia y no deja evidencia.
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
  (4) disciplina de `/tmp` RELATIVIZADA (enmienda 001): `/tmp` se ADMITE para
      borradores efímeros de un MISMO proceso; lo que debe durar, dejar
      evidencia o leerlo otro proceso o rol va a rutas estables del workspace
      (`.cdad/inbox` para el recibo; el workspace declarado para lo demás).
      NO existe una prohibición absoluta de `/tmp` («never `/tmp`» sin matiz
      viola la enmienda).

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
  4 ``TestPd6Rule4TmpRelativized::test_pd6_rule4_durable_evidence_and_cross_role_reads_go_to_stable_workspace_paths``   PD-6(4)/INV-4 (enmienda 001, (a))
  5 ``TestPd6Rule4TmpRelativized::test_pd6_rule4_tmp_relativized_admitted_for_same_process_drafts_without_absolute_prohibition``   PD-6(4)/INV-4 (enmienda 001, (b))
  6 ``TestPd6OrientationOwnerCited::test_pd6_orchestrators_reference_the_view_first_owner``                     PD-6 (cita, no duplica)
  7 ``TestPd6NoTmpCrossScopeInstructionInInstallableText::test_pd6_no_installable_text_uses_tmp_as_cross_scope_channel_or_artifact_place``   PD-6(4)/INV-4 (enmienda 001, (c) — oráculo de ausencia)

RED observado contra el árbol vigente (U1–U6 en GREEN: los orquestadores ya
declaran las cuatro reglas con el «Never `/tmp` as channel or workspace`» de la
spec ORIGINAL; la **enmienda 001** relativiza la regla 4 y este RED la
reformula) — OBSERVADO ejecutando este módulo, todo fallo es AssertionError de
CONTENIDO, nunca ImportError/SyntaxError ni fallo del fixture:

  (1)-(3) GUARD pre-satisfecho declarado (OBSERVADO verde): las reglas 1–3 de la
      spec original ya están declaradas y co-ubicadas; los tests las protegen
      contra degradación.
  (4)/(a) FALLA: la regla 4 vigente no declara que lo durable, la evidencia y lo
      que lee otro proceso o rol va a rutas estables del workspace con
      `.cdad/inbox` para el recibo — los conceptos existen en el documento pero
      NO co-ubicados con la mención de `/tmp`: la regla no está declarada como
      regla relativizada.
  (5)/(b) FALLA (ambas mitades OBSERVADAS en la misma corrida): (i) falta el
      concepto «de un mismo proceso» del permiso acotado; (ii) la regla vigente
      es una prohibición ABSOLUTA («Never `/tmp` as channel or workspace»), sin
      el matiz que la enmienda exige.
  (6) GUARD pre-satisfecho declarado (OBSERVADO verde): la cita a
      `references/orientation.md` ya existe en los dos orquestadores
      generados (no la introduce U6); el test la protege contra degradación.
      Que la sección citada siga siendo el DUEÑO de «vista primero» y que el
      orquestador no la duplique es prosa: la verifica el review de stage 4.
  (7)/(c) GUARD pre-satisfecho declarado (OBSERVADO verde): ningún texto
      instalable del árbol actual (`skills/**` + `agents/**`) usa `/tmp` como
      canal entre procesos o roles ni como lugar de un artefacto, recibo o
      evidencia; el oráculo de ausencia RELATIVIZADO de la enmienda 001 se
      conserva contra la degradación futura.

Reformulación de acoplados (enmienda A-1) y alcance de este RED: se reformula la
superficie de SU unidad — los tres oráculos de la regla 4/INV-4 de este módulo.
`grep -rn "/tmp" tests/*.py tests/*.sh` (pedido por la enmienda 001): ningún
otro test fija el «never `/tmp`» del orquestador o de la skill; las demás
apariciones de `/tmp` en `tests/` son fixtures de `temporary_roots`/tempdirs y
rutas absolutas del path-policy, ajenas a la regla 4, así que no se reformula
ninguna otra. `tests/validate-consistency.sh` (cero apariciones de `/tmp`) y
`tests/test_005_009_t3_spawn_reconciliation.py` no fijan las reglas de contexto:
se corren como regresión. La paridad fuente↔generado sí depende de que el GREEN
regenere los agentes (`make agents`), que es su trabajo, no una reformulación de
tests.

Límite honesto (PD-6): el test prueba que la regla EXISTE, no que se OBEDEZCA.
La única evidencia de comportamiento es el transcript de la corrida de
aceptación (U8) y es una muestra. Los oráculos de prosa son heurísticos sobre
CONCEPTOS con alternativas (co-ubicación de unidad/ventana para (a)/(b);
proximidad línea a línea para el oráculo de ausencia (c)): la redacción fina la
verifica el review de stage 4.
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

# Nombres normativos (el contrato fija el NOMBRE, no la prosa): `/tmp` es el
# token literal de la regla 4/INV-4 (enmienda 001), `.cdad/inbox` es el inbox
# del recibo (PD-5) y `orientation.md` el dueño de «vista primero» (PD-6).
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

# ---- enmienda 001: conceptos de la regla 4 RELATIVIZADA (no frases) -------

# Permiso acotado: `/tmp` se ADMITE (no es una prohibición absoluta).
TMP_PERMISSION_RE = re.compile(
    r"(?i)(?:\b(?:admit|admitted|admits|admisi[óo]n|allow(?:ed|s)?|"
    r"permit(?:ted|s)?|permissible|acceptable|accepted|valid|legal)\b"
    r"|\b(?:may|can)\b[^.\n]{0,12}\b(?:use|write|store|keep|hold|put|create)\b"
    r"|\b(?:is|are|remains?)\b[^.\n]{0,12}\b(?:fine|okay|ok|acceptable|"
    r"admitted|allowed)\b"
    r"|\bse admite\b|\badmitid[oa]s?\b|\bse permite\b|\bpermitid[oa]s?\b"
    r"|\bpuede\b|\bes v[áa]lid[oa]\b|\best[áa] bien\b|\bes aceptable\b)"
)
# Borrador efímero/desechable: lo único que la enmienda admite en `/tmp`.
EPHEMERAL_DRAFT_RE = re.compile(
    r"(?i)\b(?:ephemeral|ef[ií]mer[oa]s?|throwaway|scratch(?:pad)?|"
    r"disposable|desechabl[es]?|transient|one-off|short-lived|draft|drafts|"
    r"borrador(?:es)?|temporar[yi]|temporales|temporal)\b"
)
# De un MISMO proceso (no entre procesos ni roles).
SAME_PROCESS_RE = re.compile(
    r"(?i)(?:(?:same|single|own|one|mismo|[úu]nico|propio)[^.\n]{0,20}process"
    r"|process[^.\n]{0,20}(?:same|own|local)"
    r"|\bwithin (?:the|a) process\b|\bin-?process\b|\bmismo proceso\b"
    r"|\bun mismo proceso\b|\bdel mismo proceso\b|\b[úu]nico proceso\b)"
)
# Lo durable / la evidencia / lo que lee OTRO proceso o rol: la CONDICIÓN que
# la enmienda manda a rutas estables (el par «recibo»/«.cdad/inbox» tiene su
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

# Canal entre procesos o roles: acotar una prohibición de `/tmp` a ESTE uso la
# vuelve NO-absoluta (la enmienda relativiza la regla; una prohibición sin
# matiz ni acotación es la «never `/tmp`» que falla).
CROSS_PROCESS_ROLE_RE = re.compile(
    r"(?i)(?:\bbetween (?:processes|roles|sessions|agents)\b|"
    r"\bacross (?:processes|roles|sessions|agents)\b|"
    r"\bcross-?process\b|\bcross-?role\b|"
    r"\banother (?:process|role|session|agent)\b|"
    r"\bother (?:processes|roles|sessions|agents)\b|"
    r"\bnext (?:process|role|session|agent)\b|"
    r"\bentre (?:procesos|roles|sesiones|agentes)\b|"
    r"\botro (?:proceso|rol|sesi[óo]n|agente)\b)"
)
# Lugar de un artefacto, recibo o evidencia: el otro uso que la enmienda manda
# FUERA de `/tmp` (canal entre procesos/roles o lugar de un artefacto/recibo/
# evidencia son los dos usos prohibidos por el oráculo de ausencia).
ARTIFACT_RECEIPT_EVIDENCE_RE = re.compile(
    r"(?i)(?:\bartifact\b|\bartefacto\b|\breceipt\b|\brecibo\b|\bevidence\b|"
    r"\bevidencia\b|\bdescriptor\b|\bdeliverable\b|\bentregable\b|"
    r"\bresult\.json\b)"
)
# `/tmp` usado como LUGAR (destino/fuente/ubicación), no como mera mención
# (permiso o prohibición): `in /tmp`, `to /tmp`, `/tmp/<name>`, etc.
TMP_AS_PLACE_RE = re.compile(
    r"(?i)(?:/tmp/[^\s`]+"
    r"|(?:in|into|to|at|under|via|through|from|on|en|bajo)\s+`?/tmp(?![A-Za-z0-9_])"
    r"|`?/tmp(?![A-Za-z0-9_])`?\s*(?:holds?|contains?|is where|is the place))"
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

# ------------------------------------- regla 4 (enmienda 001, relativizada)
# El token `/tmp` sigue siendo normativo, pero la enmienda lo RELATIVIZA: la
# regla se declara cuando la mención de `/tmp` co-ubica con el permiso acotado
# (borrador efímero de un mismo proceso). Alternativa de idioma por concepto.
TMP_MENTION = rx("/tmp")
# El matiz que vuelve NO-ABSOLUTA la regla 4 (tres conceptos co-ubicados con la
# mención de `/tmp`).
TMP_PERMITTED_FOR_DRAFTS = (
    ("permiso acotado (`/tmp` admitido/permitido)", TMP_PERMISSION_RE),
    ("borrador efímero/desechable", EPHEMERAL_DRAFT_RE),
    ("de un mismo proceso", SAME_PROCESS_RE),
)
RULE4_GROUPS = (("mención de `/tmp`", TMP_MENTION),) + TMP_PERMITTED_FOR_DRAFTS
# (a) la regla 4 contrasta `/tmp` con su alternativa: lo durable / la evidencia
# / lo que lee otro proceso o rol → rutas estables del workspace, con
# `.cdad/inbox` para el recibo (la mención de `/tmp` es parte de la MISMA regla).
RULE4_DURABLE_GROUPS = (
    ("mención de `/tmp`", TMP_MENTION),
    ("lo durable / la evidencia / lo que lee otro proceso o rol",
     DURABLE_OR_XPROCESS_RE),
    ("ruta estable del workspace declarado", STABLE_WORKSPACE_PATH_RE),
    ("recibo → `.cdad/inbox`", RECEIPT_INBOX_RE),
)

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


def absolute_tmp_prohibitions(text: str) -> list[str]:
    """Unidades que prohíben `/tmp` SIN el matiz de la enmienda 001.

    Una prohibición es legítima sólo si está ACOTADA: o declara el permiso
    acotado (borrador efímero de un mismo proceso) o restringe explícitamente
    el uso prohibido al canal entre procesos/roles. Una regla «never `/tmp`»
    sin matiz es ABSOLUTA y viola la enmienda (el dueño la relativizó al quitar
    el aislamiento por proceso del SO)."""
    offenders: list[str] = []
    for unit in rule_units(text):
        if not TMP_TOKEN_RE.search(unit):
            continue
        if not TMP_PROHIBITION_RE.search(unit):
            continue
        if all(pattern.search(unit) for _, pattern in TMP_PERMITTED_FOR_DRAFTS):
            continue
        if CROSS_PROCESS_ROLE_RE.search(unit):
            continue
        offenders.append(" ".join(unit.split())[:160])
    return offenders


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


# --------- PD-6(4)/INV-4 (enmienda 001) — `/tmp` relativizado, no prohibido


class TestPd6Rule4TmpRelativized(U6Case):
    """PD-6 regla 4/INV-4 con la **enmienda 001** (dueño, 2026-10-17): la regla
    está RELATIVIZADA. `/tmp` NO está prohibido en absoluto: se admite para
    borradores efímeros de un mismo proceso. Lo que debe durar, dejar evidencia
    o leerlo otro proceso o rol va a rutas estables del workspace (`.cdad/inbox`
    para el recibo; el workspace declarado para lo demás)."""

    def test_pd6_rule4_durable_evidence_and_cross_role_reads_go_to_stable_workspace_paths(
            self) -> None:
        """PD-6(4)/INV-4 (enmienda 001, (a)): ambos orquestadores generados
        declaran que lo durable, la evidencia y lo que lee otro proceso o rol
        va a rutas ESTABLES del workspace, co-ubicado con el recibo
        `.cdad/inbox` (el canal válido; `/tmp` se limpia y no deja evidencia)."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                assert_rule(text, label, "lo durable / la evidencia / lo que "
                                         "lee otro proceso o rol va a rutas "
                                         "estables del workspace, con "
                                         "`.cdad/inbox` para el recibo",
                            RULE4_DURABLE_GROUPS,
                            (TMP_MENTION, STABLE_WORKSPACE_PATH_RE,
                             RECEIPT_INBOX_RE, DURABLE_OR_XPROCESS_RE))

    def test_pd6_rule4_tmp_relativized_admitted_for_same_process_drafts_without_absolute_prohibition(
            self) -> None:
        """PD-6(4)/INV-4 (enmienda 001, (b)): la mención de `/tmp` co-ubica con
        el permiso ACOTADO (borrador efímero de un mismo proceso) y NO existe
        una prohibición absoluta: una regla tipo «never `/tmp`» sin matiz falla
        la enmienda."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                problems: list[str] = []
                try:
                    assert_rule(text, label, "`/tmp` admitido para borradores "
                                             "efímeros de un mismo proceso",
                                RULE4_GROUPS,
                                (TMP_MENTION, TMP_PERMISSION_RE,
                                 EPHEMERAL_DRAFT_RE))
                except AssertionError as exc:
                    problems.append(str(exc))
                offenders = absolute_tmp_prohibitions(text)
                if offenders:
                    problems.append(
                        "prohibición ABSOLUTA de `/tmp` sin matiz (la enmienda "
                        "001 la relativiza: sólo se admite para borradores "
                        f"efímeros de un mismo proceso): {offenders!r}"
                    )
                self.assertEqual(
                    problems, [],
                    msg=(f"PD-6 ({label}): regla 4 (enmienda 001) NO "
                         "relativizada:\n- " + "\n- ".join(problems)),
                )


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


# ------- PD-6(4)/INV-4 (enmienda 001) — oráculo de ausencia relativizado


class TestPd6NoTmpCrossScopeInstructionInInstallableText(unittest.TestCase):
    """PD-6 regla 4/INV-4 (enmienda 001): en texto INSTALABLE (`skills/**` + los
    agentes generados `agents/**`) NO hay instrucciones que usen `/tmp` como
    canal entre procesos o roles, ni como lugar de un artefacto, recibo o
    evidencia. Las menciones que lo PROHÍBEN o lo EXCLUYEN explícitamente, y las
    que lo admiten para borradores efímeros de un mismo proceso, son válidas
    (la enmienda ya no prohíbe toda mención de `/tmp`)."""

    def installable_files(self) -> list[Path]:
        files: list[Path] = []
        for root in (REPO_ROOT / "skills", REPO_ROOT / "agents"):
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*")):
                if path.is_file() and path.suffix in INSTALLABLE_SUFFIXES:
                    files.append(path)
        return files

    def test_pd6_no_installable_text_uses_tmp_as_cross_scope_channel_or_artifact_place(
            self) -> None:
        """PD-6(4)/INV-4 (enmienda 001, (c)): ninguna línea de texto instalable
        en un bloque NO prohibitivo usa `/tmp` como LUGAR (destino/fuente) de un
        artefacto, recibo o evidencia, ni como canal entre procesos o roles; una
        instrucción de ese uso es una violación (el canal es `.cdad/inbox` y lo
        durable va al workspace declarado, porque `/tmp` se limpia y no deja
        evidencia)."""
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
                if PROHIBITIVE_RE.search(block):
                    continue
                for line in block.splitlines():
                    if not TMP_TOKEN_RE.search(line):
                        continue
                    if not TMP_AS_PLACE_RE.search(line):
                        continue
                    if not (CROSS_PROCESS_ROLE_RE.search(line)
                            or ARTIFACT_RECEIPT_EVIDENCE_RE.search(line)):
                        continue
                    offenders.append(f"{relative}:{number} → {line.strip()}")
        self.assertEqual(
            offenders, [],
            msg=("PD-6(4)/INV-4 (enmienda 001): texto instalable que usa `/tmp` "
                 "como canal entre procesos o roles, o como LUGAR de un "
                 "artefacto, recibo o evidencia (prohibirlo, o admitirlo para "
                 "borradores efímeros del mismo proceso, es válido): "
                 f"{offenders!r}"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
