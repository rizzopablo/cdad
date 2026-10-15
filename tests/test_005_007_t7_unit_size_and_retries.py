#!/usr/bin/env python3
"""005-007 T7 RED — tamaño de unidad por costo total y vínculo reintentos↔unidad.

Test de consistencia ESTRUCTURAL, caja negra (precedentes dentro de esta
misma feature: `tests/test_005_007_t1_progressive_detail_rule.py` en los
helpers de estructura y `tests/test_005_007_t6_templates.py` en la
convención de casos). Los archivos de producto se leen AL EJECUTARSE
(archivo faltante = estado conductual => `pytest.fail`); los oráculos
derivan SOLO del contrato aprobado (`docs/specs/005-007-progressive-
planning/spec.md`, PD-3/PD-4/PD-13 y §6 D3/D4) y de la ficha T7 del plan
aprobado. El test-writer NO derivó ningún oráculo leyendo los archivos de
producto (`skills/cdad-cycle/references/stage-2-specification.md`,
`skills/cdad-cycle/references/re-entry.md`); los rótulos pueden variar, así
que las aserciones son de PRESENCIA por familias de tokens (declaradas
abajo como decisiones de oráculo), nunca de prosa completa, estilo ni
número de líneas.

Contrato que el test fija (un caso por postcondición exigida, trazado):

- CASE 1 (PD-3; AC-6; D3; ficha T7) -> la sección de tamaño de unidad de
  `stage-2-specification.md` declara el criterio por COSTO TOTAL como
  condiciones VERIFICABLES y SIN números inventados: (a) un reviewer no
  podría rechazar la unidad sin rechazar su vecina; (b) la unidad cierra
  su propio resultado verificable con su CONSUMIDOR NOMBRADO; (c) sus
  COSTOS FIJOS (planeación + apertura de sesión + revisión independiente +
  integración) superan el AVANCE MARGINAL que entrega; (d) no mueve la
  feature hacia un resultado verificable (FRAGMENTACIÓN). Además la
  sección REFERENCIA el criterio de «costo de coordinación»
  (planning-contract-draft.md:155) y NO declara umbrales numéricos
  (porcentajes, mínimos de tareas/archivos/líneas, comparadores ≥/<=
  numéricos) como criterio.
- CASE 2 (PD-4; AC-6; D4; ficha T7) -> `re-entry.md` (dueño único de la
  regla de reintentos) declara el disparador a NIVEL DE UNIDAD: un
  reintento SIN INFORMACIÓN NUEVA sobre una unidad dispara una REVISIÓN DE
  ESTRATEGIA que puede REPLANTEAR la unidad (tamaño, frontera o detalle),
  con el número de intentos como SEÑAL y no como criterio.
- CASE 3 (PD-12; fuente única; ficha T7) -> la sección de tamaño de
  `stage-2-specification.md` REFERENCIA la regla de reintentos / su hogar
  (`re-entry.md`) sin re-enunciarla: el CONTEO de intentos (la regla de
  dos intentos) no aparece como segunda declaración en la sección de
  tamaño; la fuente del conteo sigue siendo re-entry.md.
- CASE 4 (PD-13; INV-8; ficha T7) -> la cláusula de replanteo de unidad
  declara la TRAZABILIDAD: replantear conserva OBJETIVO, DEPENDENCIAS y
  RAZONES, y NO reescribe un contrato ya DESPACHADO sin RECONCILIACIÓN
  declarada.

Fallos del modo RED esperados (declared behavior, no error de fixture;
hoy ni el criterio por costo total ni el vínculo a nivel de unidad
existen en esas fuentes — spec PD-3 «Resuelve VERIFY 4» y PD-4 «sólo
falta el vínculo con la unidad», discovery.md:230-235 según contrato):
CASE 1 -> `AssertionError` (ninguna sección de tamaño declara las cuatro
condiciones cualitativas: no hay par costo-fijo/marginal ni
reviewer/vecina). CASE 2 y CASE 4 -> `AssertionError` (ninguna sección de
re-entry.md declara el replanteo de la unidad ni, por ende, su
trazabilidad). CASE 3 -> `AssertionError` (la sección de tamaño no
referencia la regla de reintentos; el guard de ausencia de segunda
declaración del conteo es preventivo y puede pasar hoy). Nunca
ImportError/SyntaxError/NameError/fixture-exception. Nada de skip.
"""

from __future__ import annotations

import re

from tests.test_005_007_t1_progressive_detail_rule import (
    HEADING,
    REPO,
    _lines,
    _load,
    _near,
    _sections,
)

STAGE2 = REPO / "skills/cdad-cycle/references/stage-2-specification.md"
RE_ENTRY = REPO / "skills/cdad-cycle/references/re-entry.md"

# ---------------------------------------------------------------------------
# Familias de tokens (decisiones de oráculo; los rótulos exactos varían).
# ---------------------------------------------------------------------------

# Localizador de la sección de tamaño de unidad (CASE 1/3): el encabezado
# habla de tamaño/size, o el cuerpo co-ocurre tamaño+unidad.
SIZE_HEADING = re.compile(r"(?i)\btama|\bsize\b|task\s+size")
SIZE_BODY = re.compile(r"(?i)tama[nñ]o|size")
UNIT_BODY = re.compile(r"(?i)unidad|unit\b")

# PD-3 (a): reviewer no podría rechazarla sin rechazar su vecina.
REJECT = re.compile(r"(?i)rechaz|reject|rechaz")
NEIGHBOR = re.compile(r"(?i)vecin|neighbor|sibling")
REVIEWER = re.compile(r"(?i)reviewer|revisor|revisi[óo]n\s+independiente")

# PD-3 (b): cierra su propio resultado verificable con su consumidor nombrado.
RESULT = re.compile(r"(?i)resultado|result\b|outcome")
CONSUMER = re.compile(r"(?i)consumidor|consumer")
NAMED = re.compile(r"(?i)nombrad|named|consumidor\s+nombrado|named\s+consumer")

# PD-3 (c): costos fijos superan el avance marginal.
FIXED_COST = re.compile(r"(?i)costo[s]?\s+fijos?|fixed\s+costs?")
MARGINAL = re.compile(r"(?i)marginal")
PLANNING_COST = re.compile(r"(?i)planeaci|planning")
SESSION_COST = re.compile(r"(?i)apertura\s+de\s+sesi[óo]n|session\s+(?:open|start)")
INDEP_REVIEW = re.compile(r"(?i)revisi[óo]n\s+independiente|independent\s+review")
INTEGRATION_COST = re.compile(r"(?i)integraci|integration")

# PD-3 (d): no mueve la feature hacia un resultado verificable (fragmentación).
NO_MOVE = re.compile(r"(?i)no\s+mueve|does\s+not\s+move|doesn'?t\s+move|no\s+avanza")
FRAGMENT = re.compile(r"(?i)fragmentaci|fragmentat|fragment")

# PD-3: referencia al criterio de «costo de coordinación» (por referencia).
COORD_COST_REF = re.compile(
    r"(?i)costo\s+de\s+coordinaci|coordination\s+cost|planning-contract-draft"
)

# PD-3: umbrales numéricos PROHIBIDOS como criterio (ausencia).
NUMERIC_THRESHOLD = re.compile(
    r"(?i)\b\d+\s*%"
    r"|\b(?:m[ií]nimo|minimum|max[ií]mo|maximum|al\s+menos|at\s+least"
    r"|no\s+menos\s+de|no\s+more\s+than|no\s+m[áa]s\s+de|m[áa]s\s+de)"
    r"\s*:?\s*\d"
    r"|\b\d+\s+(?:tareas|archivos|l[ií]neas|lines|tasks|files)\b"
    r"|(?:≥|<=|>=|>)\s*\d"
)

# PD-4: disparador a nivel de unidad en re-entry.md (CASE 2/4).
REPLAN = re.compile(
    r"(?i)replantear|replan(?:ea|ear)?|remodelar|reformular"
    r"|revisi[óo]n\s+de\s+estrategia|strategy\s+review"
)
RETRY_WORD = re.compile(r"(?i)reintent|retry|retries|attempt")
NO_NEW_INFO = re.compile(
    r"(?i)sin\s+(?:nada\s+de\s+)?informaci[óo]n\s+nueva"
    r"|no\s+(?:aporta|aporte|suma)\s+(?:nada\s+nuevo|informaci[óo]n\s+nueva)"
    r"|without\s+(?:any\s+)?new\s+information|no\s+new\s+information"
)
STRATEGY = re.compile(r"(?i)estrategia|strategy")
UNIT_WORD = re.compile(r"(?i)unidad|unit\b")
DIMENSION = re.compile(r"(?i)tama[nñ]o|size|frontera|boundary|detalle|detail|alcance")
SIGNAL = re.compile(r"(?i)se[ñn]al|signal")
CRITERION = re.compile(r"(?i)criterio|criterion")
SIGNAL_NOT_CRITERION = re.compile(
    r"(?i)(?:se[ñn]al|signal)[^\n]{0,80}(?:no\s+es|no\s+como|no\s+un|rather\s+than|not)"
    r"|(?:no\s+es|no\s+como|not\s+a|not\s+as)\s+(?:un\s+)?(?:el\s+)?criteri"
)

# PD-12: segunda declaración PROHIBIDA del conteo de intentos (ausencia).
ATTEMPT_COUNT_DECL = re.compile(
    r"(?i)dos\s+intentos|two\s+attempts|two\s+tries"
    r"|segundo\s+intento|second\s+attempt|segunda\s+oportunidad"
    r"|single\s+attempt|un\s+solo\s+intento"
)
# PD-12: referencia por nombre a la regla de reintentos / su hogar.
RETRY_RULE_REF = re.compile(r"(?i)re-entry\.md|reintentos?|retry|retries")

# PD-13: trazabilidad del replanteo (CASE 4).
OBJECTIVE = re.compile(r"(?i)objetivo|goal|objective")
DEPENDENCIES = re.compile(r"(?i)dependenc|dependencias?|depends")
REASONS = re.compile(r"(?i)razones?|raz[óo]n|reasons?|motivos?")
PRESERVE = re.compile(
    r"(?i)conserva|preserva|se\s+mantiene|kept|preserved|retiene"
    r"|no\s+(?:se\s+)?(?:borra|reescribe|descarta|elimina|rescribe)"
)
RECONCILIATION = re.compile(r"(?i)reconcili")
DISPATCHED = re.compile(r"(?i)despachad|dispatched|en\s+vuelo|in\s+flight|shipped")


def _size_sections(text: str) -> list[list[str]]:
    """Secciones candidatas a ser la regla de tamaño de unidad: encabezado
    que habla de tamaño, o cuerpo que co-ocurre tamaño+unidad."""
    lines_ = _lines(text)
    starts = [i for i, ln in enumerate(lines_) if HEADING.match(ln.strip())]
    out = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines_)
        body = lines_[start : end]
        if SIZE_HEADING.search(lines_[start]) or (
            any(SIZE_BODY.search(ln) for ln in body)
            and any(UNIT_BODY.search(ln) for ln in body)
        ):
            out.append(body)
    return out


def _has_all_size_conditions(section: list[str]) -> bool:
    """Las cuatro condiciones cualitativas de PD-3 en una misma sección."""
    return (
        _near(section, REVIEWER, NEIGHBOR, max_gap=3)
        and _near(section, REJECT, NEIGHBOR, max_gap=3)
        and _near(section, RESULT, CONSUMER, max_gap=3)
        and _near(section, CONSUMER, NAMED, max_gap=3)
        and _near(section, FIXED_COST, MARGINAL, max_gap=3)
        and any(PLANNING_COST.search(ln) for ln in section)
        and any(INTEGRATION_COST.search(ln) for ln in section)
        and (
            any(INDEP_REVIEW.search(ln) for ln in section)
            or any(SESSION_COST.search(ln) for ln in section)
        )
        and _near(section, NO_MOVE, RESULT, max_gap=3)
        and any(FRAGMENT.search(ln) for ln in section)
    )


def _replan_sections(text: str) -> list[list[str]]:
    """Secciones de re-entry.md que declaran el replanteo de la unidad."""
    lines_ = _lines(text)
    starts = [i for i, ln in enumerate(lines_) if HEADING.match(ln.strip())]
    out = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines_)
        body = lines_[start : end]
        if any(REPLAN.search(ln) for ln in body):
            out.append(body)
    return out


# ---------------------------------------------------------------------------
# CASE 1 — PD-3 (AC-6; D3; ficha T7): criterio de tamaño por costo total,
# condiciones verificables, sin números inventados.
# ---------------------------------------------------------------------------

def test_case1_pd3_unit_size_by_total_cost_qualitative_conditions():
    text = _load(STAGE2)
    candidates = _size_sections(text)
    assert candidates, (
        "PD-3: stage-2-specification.md no declara sección alguna de tamaño "
        "de unidad (ni encabezado de tamaño ni cuerpo tamaño+unidad)."
    )
    declaring = [s for s in candidates if _has_all_size_conditions(s)]
    assert declaring, (
        "PD-3: la regla de tamaño de unidad no declara el criterio por costo "
        "total como condiciones verificables: falta al menos una de las "
        "cuatro condiciones cualitativas en toda sección de tamaño — "
        "(a) reviewer no puede rechazarla sin rechazar su vecina; (b) cierra "
        "su propio resultado verificable con su consumidor nombrado; (c) "
        "costos fijos (planeación + apertura de sesión + revisión "
        "independiente + integración) superan el avance marginal; (d) no "
        "mueve la feature hacia un resultado verificable (fragmentación). "
        f"Secciones candidatas examinadas: {len(candidates)}."
    )
    for section in declaring:
        assert any(COORD_COST_REF.search(ln) for ln in section), (
            "PD-3: la sección de tamaño no REFERENCIA el criterio de «costo "
            "de coordinación» (planning-contract-draft.md:155); debe reusarlo "
            "por referencia, no re-enunciarlo."
        )
        hits = [ln for ln in section if NUMERIC_THRESHOLD.search(ln)]
        assert not hits, (
            "PD-3: la sección de tamaño declara umbrales numéricos como "
            "criterio (prohibido: sin números inventados, sin mínimo de "
            "tareas, sin límite de archivos ni líneas): " + "; ".join(hits[:3])
        )


# ---------------------------------------------------------------------------
# CASE 2 — PD-4 (AC-6; D4; ficha T7): el reintento sin información nueva
# dispara una revisión de estrategia que puede replantear la unidad.
# ---------------------------------------------------------------------------

def test_case2_pd4_retry_without_new_info_triggers_unit_replanning():
    text = _load(RE_ENTRY)
    lines_ = _lines(text)
    assert any(RETRY_WORD.search(ln) for ln in lines_), (
        "PD-4: skills/cdad-cycle/references/re-entry.md ya no declara la "
        "regla de reintentos (perdió su dueño canónico)."
    )
    replan = _replan_sections(text)
    assert replan, (
        "PD-4: re-entry.md no declara el vínculo reintentos↔unidad: ninguna "
        "sección declara el replanteo de la unidad (tamaño, frontera o "
        "detalle) como consecuencia de un reintento sin información nueva."
    )
    trigger = [
        s
        for s in replan
        if _near(s, RETRY_WORD, NO_NEW_INFO, max_gap=4)
        and _near(s, REPLAN, STRATEGY, max_gap=4)
        and _near(s, UNIT_WORD, DIMENSION, max_gap=4)
        and _near(s, SIGNAL, CRITERION, max_gap=4)
        and any(SIGNAL_NOT_CRITERION.search(ln) for ln in s)
    ]
    assert trigger, (
        "PD-4: la cláusula de replanteo no declara el disparador completo: "
        "reintento SIN información nueva sobre una unidad -> revisión de "
        "estrategia -> replanteo de la unidad (tamaño/frontera/detalle), con "
        "el número de intentos como señal y NO como criterio."
    )


# ---------------------------------------------------------------------------
# CASE 3 — PD-12 (fuente única; ficha T7): la sección de tamaño referencia
# la regla de reintentos sin re-enunciar el conteo de intentos.
# ---------------------------------------------------------------------------

def test_case3_pd12_attempt_count_declared_only_in_re_entry():
    text = _load(STAGE2)
    candidates = _size_sections(text)
    assert candidates, (
        "PD-12: stage-2-specification.md no declara sección alguna de tamaño "
        "de unidad donde verificar la referencia a la regla de reintentos."
    )
    referencing = [s for s in candidates if any(RETRY_RULE_REF.search(ln) for ln in s)]
    assert referencing, (
        "PD-12: la sección de tamaño de unidad de stage-2-specification.md "
        "no REFERENCIA la regla de reintentos ni su hogar (re-entry.md); el "
        "vínculo se consume por referencia, no como segunda regla."
    )
    for section in referencing:
        offenders = [ln for ln in section if ATTEMPT_COUNT_DECL.search(ln)]
        assert not offenders, (
            "PD-12: la sección de tamaño de stage-2-specification.md "
            "re-enuncia el conteo de intentos (la regla de dos intentos "
            "vive SOLO en re-entry.md): " + "; ".join(offenders[:3])
        )


# ---------------------------------------------------------------------------
# CASE 4 — PD-13 (INV-8; ficha T7): el replanteo conserva objetivo,
# dependencias y razones; no reescribe un contrato despachado sin
# reconciliación declarada.
# ---------------------------------------------------------------------------

def test_case4_pd13_replanning_preserves_trail_and_reconciles_dispatched():
    text = _load(RE_ENTRY)
    replan = _replan_sections(text)
    assert replan, (
        "PD-13: re-entry.md no declara el replanteo de la unidad (ninguna "
        "sección con replanteo), así que la trazabilidad del replanteo no "
        "está declarada."
    )
    traced = [
        s
        for s in replan
        if _near(s, OBJECTIVE, REASONS, max_gap=4)
        and _near(s, OBJECTIVE, DEPENDENCIES, max_gap=4)
        and any(PRESERVE.search(ln) for ln in s)
    ]
    assert traced, (
        "PD-13: la cláusula de replanteo no declara la trazabilidad: "
        "replantear una unidad conserva el OBJETIVO, las DEPENDENCIAS y las "
        "RAZONES (no borra ni reescribe el rastro de la unidad)."
    )
    reconciled = [
        s
        for s in traced
        if _near(s, RECONCILIATION, DISPATCHED, max_gap=4)
    ]
    assert reconciled, (
        "PD-13: la cláusula de replanteo no declara el límite duro: un "
        "contrato ya DESPACHADO no se reescribe sin RECONCILIACIÓN "
        "declarada."
    )


if __name__ == "__main__":
    import unittest

    unittest.main(verbosity=2)
