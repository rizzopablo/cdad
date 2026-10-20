#!/usr/bin/env python3
"""006-006 U2 RED — la fuente canónica de «qué se revisa» deja de ser plan-céntrica.

Test de derivación TEXTUAL (precedente: `tests/test_005_007_t1_progressive_detail_rule.py`),
caja negra: los dos archivos de procedimiento se leen AL EJECUTARSE (archivo faltante =
estado conductual => `pytest.fail`); NO se lee ningún archivo de implementación.

Contrato: `docs/specs/006-006-spec-plan-review/spec.md` (PD-6, PD-12; §2.5 «Qué se
revisa (una sola fuente) y quién lo dice», §5 D-9, §6 V-5) +
`docs/specs/006-006-spec-plan-review/plan.md` §3 ficha U2 (archivos, RED, regresiones,
A-1) y su bloque `plan-tasks` (observable_checks de U2).

Superficie bajo prueba (TEXTO DE PROCEDIMIENTO, no código de implementación):
- `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` — dueño único de
  «qué se revisa» (INV-9, D-7);
- `skills/cdad-cycle/packets/roles/reviewer.md` — regla de rol; es una *consumidora*
  («no copia» la regla).

Oráculos (decisiones de oráculo, derivadas del contrato, NO de la prosa vigente):

- O-1 (ficha U2; spec §2.5) — el objeto de revisión es el **objeto de especificación**:
  nombra la spec Y el plan. La etiqueta plan-céntrica («plan draft») no puede quedar
  como objeto ÚNICO: se permite que aparezca si el mismo enunciado nombra también la
  spec. Y el substage no puede *excluir* la spec del objeto («not only the spec»).
- O-2 (PD-6; D-9; ficha U2) — el dictamen nombra el objeto revisado **y su digest**:
  la mención del digest, la obligación de nombrar y la mención del dictamen se
  comprueban por proximidad (ventana de caracteres), no por frase exacta.
- O-3 (ficha U2; spec §2.5) — la regla de rol nombra el objeto **que el contrato
  declara, con su forma declarada** (spec o plan) y no la etiqueta «the plan draft».
- O-4 (PD-12) — se CONSERVAN las obligaciones vigentes: separación entre validación
  estructural y juicio semántico; juicio sobre la intención; la sección `## Abstentions`
  y la frase «never mark the reviewed draft approved» (ambas citadas VERBATIM por la
  ficha, de ahí la aserción literal); el marcador `detail` consumido POR REFERENCIA.
- O-5 (PD-12; control negativo de la ficha) — el substage no es un segundo hogar
  normativo de la regla de detalle progresivo. La operacionalización determinista es la
  del oráculo vigente 005-007 PD-12 (P5): quien menciona el conjunto cerrado de valores
  del marcador tiene que REFERENCIAR la regla / su hogar. El juicio de si un párrafo
  «re-enuncia» la regla es del review (INV-8 de 005-013: sin listas de palabras), no de
  un test; aquí se fija lo determinista: el puntero al hogar canónico sobrevive.
- O-6 (V-5; PD-12) — el bloque estático del paquete del reviewer (`common.md` +
  `roles/reviewer.md` + `substages/reviewer-plan-review.md`, unidos por «\n», la convención
  congelada 003-001) se MIDE y queda por debajo del techo declarado de 12000 bytes.
  Límite inclusivo, como el oráculo vigente de `tests/test_role_packet_render.py`:279.

Fallos del modo RED esperado: `AssertionError` de comportamiento sobre el texto
(faltan el objeto generalizado, el digest, la forma declarada) o `pytest.fail` de estado
conductual (archivo requerido inexistente). Nunca ImportError/SyntaxError/NameError.
Nada de skip. Sin asserts de prosa completa, de estilo ni de número de líneas.

A-1 (plan §4): este RED **NO reemplaza ningún oráculo vigente**; sólo AÑADE casos.
Comprobado sobre las cinco regresiones de la ficha: ninguna fija el texto plan-céntrico
(no hay ninguna ocurrencia de «PLAN DRAFT» en `tests/`; el único «plan draft» — el
objetivo local `tests/test_004_003_t2_plan_review.py`:75 — es una cadena del propio
test, y ese archivo calcula el sha256 del substage DINÁMICAMENTE, luego no lo fija).
Los fixtures compartidos `DRAFT_PLAN_RELPATH` no se tocan.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.test_005_007_t1_progressive_detail_rule import (
    DETAIL_TOKEN,
    QUOTED_NEXT,
    QUOTED_PLANNED,
    RULE_REFERENCE,
    _lines,
    _restates_closed_values,
)

REPO = Path(__file__).resolve().parents[1]
PACKETS_ROOT = REPO / "skills" / "cdad-cycle" / "packets"
SUBSTAGE = PACKETS_ROOT / "substages" / "reviewer-plan-review.md"
ROLE_RULE = PACKETS_ROOT / "roles" / "reviewer.md"

# El bloque estático del paquete reviewer/plan-review (convención congelada 003-001).
STATIC_SOURCES = (
    "common.md",
    "roles/reviewer.md",
    "substages/reviewer-plan-review.md",
)
STATIC_CEILING_BYTES = 12000

CANONICAL_HOME_NAME = "stage-2-specification.md"

# --- Anclas semánticas (familias de tokens, nunca prosa completa) -------------

# Las dos formas que el contrato puede declarar.
SPEC_MENTION = re.compile(r"(?i)\bspec(?:ification)?\b")
PLAN_MENTION = re.compile(r"(?i)\bplan\b")
# La etiqueta plan-céntrica del objeto (citada por la ficha).
PLAN_ONLY_LABEL = re.compile(r"(?i)\bplan\s+draft\b")
# Una construcción que EXCLUYE la spec del objeto revisado.
SPEC_EXCLUSION = re.compile(
    r"(?i)\bnot\s+(?:(?:only|just)\s+)?the\s+spec\b|\bthe\s+spec\s+alone\b"
)
# El dictamen y su digest (PD-6; D-9).
DICTAMEN = re.compile(r"(?i)\bdictamen(?:s|es)?\b")
DIGEST = re.compile(r"(?i)\bdigest\b|\bsha[-_ ]?256\b|\bchecksum\b")
# La obligación de NOMBRAR (familia del verbo, no una frase exacta).
NAMING = re.compile(
    r"(?i)\b(?:nam\w+|identif\w+|stat\w+|declar\w+|record\w+|specif\w+|cit\w+)\b"
)
# Obligaciones vigentes del substage (PD-12).
STRUCTURAL = re.compile(r"(?i)\bstructural\b")
SEMANTIC = re.compile(r"(?i)\bsemantic\w*\b")
SEPARATION = re.compile(r"(?i)\bseparate\w*|\bdistinct\b|\bdiffer\w*")
INTENTION = re.compile(r"(?i)\bintention\b|\bintent\b")
BLOCKING = re.compile(r"(?i)\bblocking\b")
OPTIONAL = re.compile(r"(?i)\boptional\b")
CONFIDENCE_THRESHOLD = re.compile(r"(?i)>=\s*80|≥\s*80|80\s*%|\b80\b")
VERDICT_TUPLE = re.compile(r"(?i)\bverdict[-\s]?tuple\b")
# Obligaciones vigentes de la regla de rol (PD-12).
READ_ONLY = re.compile(r"(?i)read[- ]only")
VERDICT = re.compile(r"(?i)\bverdict\w*\b")
CONFIDENCE = re.compile(r"(?i)\bconfidence\b")
RATIONALE = re.compile(r"(?i)\brationale\b")
LOCATION = re.compile(r"(?i)\blocation\b")
ABSTAIN = re.compile(r"(?i)\babstain\w*\b")
# La regla de rol nombra el objeto que el contrato declara.
CONTRACT_DECLARES = re.compile(
    r"(?i)\bcontract\s+declares\b|\bdeclares\s+the\s+(?:object|form|shape)\b"
)


# --- Helpers (caja negra; archivo faltante = estado conductual) ---------------


def _load(path: Path) -> str:
    """Archivo requerido faltante es estado conductual, no error de oráculo."""
    if not path.is_file():
        pytest.fail(f"archivo de procedimiento requerido no existe: {path}")
    return path.read_text(encoding="utf-8")


def _norm(text: str) -> str:
    """Proso normalizado (espacios colapsados) para citas verbatim de la ficha."""
    return re.sub(r"\s+", " ", text)


def _mask_home(text: str) -> str:
    """Oculta el nombre del hogar canónico: su nombre NO cuenta como «nombrar la
    spec» (el objeto revisado se nombra en otro sitio del procedimiento)."""
    return text.replace(CANONICAL_HOME_NAME, " ").replace("stage-2-specification", " ")


def _opening(text: str) -> str:
    """El enunciado de revisión (la instrucción que abre el procedimiento)."""
    return re.split(r"[.—\n]", text, maxsplit=1)[0]


def _near_chars(text: str, first: re.Pattern, second: re.Pattern, radius: int = 500) -> bool:
    """True si algún match de `first` tiene un match de `second` a <= `radius`
    caracteres (mismo enunciado; el wrapping no rompe la pareja)."""
    for match in first.finditer(text):
        low = max(0, match.start() - radius)
        high = min(len(text), match.end() + radius)
        if second.search(text, low, high):
            return True
    return False


# ---------------------------------------------------------------------------
# PD-6 / PD-12 — el objeto de revisión es el objeto de especificación.
# ---------------------------------------------------------------------------


def test_pd6_pd12_u2_substage_reviewed_object_is_not_the_plan_alone():
    """PD-6 / PD-12: el substage declara como objeto de revisión el objeto de
    especificación (la spec Y el plan), no el plan solo.

    O-1: la etiqueta plan-céntrica («plan draft») no puede quedar como objeto
    ÚNICO del enunciado de revisión; y el substage no puede excluir la spec del
    objeto («not only the spec»).
    """
    text = _load(SUBSTAGE)
    opening = _opening(text)
    masked = _mask_home(text)

    assert not (
        PLAN_ONLY_LABEL.search(opening) and not SPEC_MENTION.search(opening)
    ), (
        "PD-6/PD-12: el enunciado de revisión nombra el objeto con la etiqueta "
        "plan-céntrica y NO nombra la spec junto a él: el objeto declarado debe "
        "ser el objeto de especificación (la spec y el plan). Enunciado: "
        f"{opening.strip()!r}"
    )
    assert not SPEC_EXCLUSION.search(masked), (
        "PD-6/PD-12: el substage EXCLUYE la spec del objeto revisado (la spec "
        "aparece como «not only the spec»): el objeto declarado debe incluir la "
        "spec y el plan."
    )
    assert SPEC_MENTION.search(masked), (
        "PD-6/PD-12: el substage no nombra la spec como parte del objeto revisado."
    )
    assert PLAN_MENTION.search(masked), (
        "PD-6/PD-12: el substage no nombra el plan como parte del objeto revisado."
    )


# ---------------------------------------------------------------------------
# PD-6 (D-9) — el dictamen nombra el objeto revisado y su digest.
# ---------------------------------------------------------------------------


def test_pd6_u2_substage_requires_the_dictamen_to_name_the_object_and_its_digest():
    """PD-6 (D-9): el procedimiento exige que el dictamen nombre el objeto
    revisado y su digest.

    O-2: la mención del digest, la obligación de nombrar y la mención del
    dictamen se comprueban por proximidad (ventana de caracteres), no por frase
    exacta: la ficha exige el CONTENIDO de la obligación, no su redacción.
    """
    text = _load(SUBSTAGE)

    assert DIGEST.search(text), (
        "PD-6/D-9: el substage no exige que el dictamen nombre el DIGEST del "
        "objeto revisado (la obligación de nombrar el objeto y su digest es "
        "parte del procedimiento, no un enforcement del producto)."
    )
    assert _near_chars(text, DIGEST, NAMING), (
        "PD-6/D-9: la mención del digest no está unida a la obligación de "
        "NOMBRAR el objeto revisado (vecindad de 500 caracteres)."
    )
    assert _near_chars(text, DIGEST, DICTAMEN), (
        "PD-6/D-9: la mención del digest no está unida al DICTAMEN que debe "
        "nombrar el objeto revisado y su digest (vecindad de 500 caracteres)."
    )


# ---------------------------------------------------------------------------
# PD-12 — la regla de rol nombra el objeto que el contrato declara.
# ---------------------------------------------------------------------------


def test_pd12_u2_role_rule_names_the_contract_declared_object_with_its_form():
    """PD-12: la regla de rol deja de ser plan-céntrica.

    O-3: nombra el objeto que el contrato declara (con su forma declarada: spec
    o plan) y no la etiqueta «the plan draft». El kind `draft-plan` puede
    seguir nombrándose (D-11: la deuda de nombres se conserva): lo que no puede
    quedar es la etiqueta del objeto.
    """
    text = _load(ROLE_RULE)
    masked = _mask_home(text)

    assert not PLAN_ONLY_LABEL.search(masked), (
        "PD-12: la regla de rol sigue siendo plan-céntrica: nombra el objeto "
        "revisado con la etiqueta «the plan draft» en vez del objeto que el "
        "contrato declara con su forma declarada."
    )
    assert SPEC_MENTION.search(masked), (
        "PD-12: la regla de rol no nombra la forma «spec» del objeto declarado."
    )
    assert PLAN_MENTION.search(masked), (
        "PD-12: la regla de rol no nombra la forma «plan» del objeto declarado."
    )
    assert CONTRACT_DECLARES.search(masked), (
        "PD-12: la regla de rol no dice que el objeto revisado es el que el "
        "contrato declara."
    )


# ---------------------------------------------------------------------------
# PD-12 — se conservan las obligaciones vigentes (guardas).
# ---------------------------------------------------------------------------


def test_pd12_u2_substage_keeps_its_vigente_obligations():
    """PD-12: el substage conserva sus obligaciones vigentes al generalizarse.

    O-4: separación entre validación estructural y juicio semántico; juicio
    sobre la intención; la sección `## Abstentions` y la frase «never mark the
    reviewed draft approved» (citadas VERBATIM por la ficha); el marcador
    `detail` consumido por referencia. Guardas: pasan hoy y deben seguir
    pasando con el producto nuevo.
    """
    text = _load(SUBSTAGE)
    norm = _norm(text).lower()

    assert STRUCTURAL.search(text) and SEMANTIC.search(text) and SEPARATION.search(text), (
        "PD-12: el substage pierde la separación entre validación estructural y "
        "juicio semántico."
    )
    assert INTENTION.search(text) and BLOCKING.search(text), (
        "PD-12: el substage pierde el juicio sobre la intención (un objeto "
        "coherente que no la alcanza es bloqueante)."
    )
    assert "## abstentions" in norm, (
        "PD-12: el substage pierde la sección `## Abstentions` (citada verbatim "
        "por la ficha U2)."
    )
    assert "never mark the reviewed draft approved" in norm, (
        "PD-12: el substage pierde la obligación «never mark the reviewed draft "
        "approved» (citada verbatim por la ficha U2)."
    )
    assert DETAIL_TOKEN.search(text), (
        "PD-12: el substage deja de mencionar el marcador `detail` que debe "
        "consumir."
    )
    assert RULE_REFERENCE.search(text), (
        "PD-12: el substage deja de referenciar la regla de detalle progresivo "
        "o su hogar canónico (debe consumir el marcador por referencia)."
    )
    assert OPTIONAL.search(text) and CONFIDENCE_THRESHOLD.search(text) and VERDICT_TUPLE.search(text), (
        "PD-12: el substage pierde la taxonomía del efecto (OPTIONAL/BLOCKING), "
        "el umbral de confianza o el verdict-tuple (ficha U2)."
    )


def test_pd12_u2_role_rule_keeps_its_vigente_obligations():
    """PD-12: la regla de rol conserva el resto de sus obligaciones.

    O-4 aplicado a la regla de rol: read-only, veredicto, bucket de confianza,
    rationale fundamentada, ubicación exacta y abstención. Guarda: pasa hoy y
    debe seguir pasando con el producto nuevo (`read-only` lo exige además el
    oráculo vigente de `tests/test_role_packet_render.py`).
    """
    text = _load(ROLE_RULE)

    assert READ_ONLY.search(text), (
        "PD-12: la regla de rol pierde la obligación de trabajar en solo lectura."
    )
    assert VERDICT.search(text), (
        "PD-12: la regla de rol pierde el veredicto por hallazgo."
    )
    assert CONFIDENCE.search(text), (
        "PD-12: la regla de rol pierde el bucket de confianza."
    )
    assert RATIONALE.search(text), (
        "PD-12: la regla de rol pierde la rationale fundamentada."
    )
    assert LOCATION.search(text), (
        "PD-12: la regla de rol pierde la ubicación exacta."
    )
    assert ABSTAIN.search(text), (
        "PD-12: la regla de rol pierde la abstención cuando la evidencia no alcanza."
    )


# ---------------------------------------------------------------------------
# PD-12 — control negativo: el substage no re-enuncia la regla de detalle.
# ---------------------------------------------------------------------------


def test_pd12_control_negative_u2_substage_is_a_consumer_not_a_second_home():
    """PD-12 (control negativo de la ficha U2): el substage consume el marcador
    `detail` POR REFERENCIA y no re-enuncia la regla de detalle progresivo.

    O-5: operacionalización determinista = la del oráculo vigente 005-007 PD-12
    (P5): quien menciona el conjunto cerrado de valores del marcador tiene que
    REFERENCIAR la regla / su hogar. Aquí se fija lo determinista —el puntero al
    hogar canónico sobrevive—; el juicio de si un párrafo «re-enuncia» la regla
    es del review (INV-8 de 005-013), no de un test por listas de palabras.
    """
    text = _load(SUBSTAGE)
    lines = _lines(text)

    assert CANONICAL_HOME_NAME in text, (
        "PD-12 (control negativo): el substage deja de apuntar al hogar canónico "
        "de la regla de detalle progresivo: debe consumir el marcador por "
        "referencia, no re-enunciar la regla."
    )
    if _restates_closed_values(lines):
        assert RULE_REFERENCE.search(text), (
            "PD-12 (control negativo): el substage menciona el conjunto cerrado "
            "de valores del marcador SIN referenciar la regla / su hogar: sería "
            "una segunda copia normativa (oráculo vigente 005-007 P5)."
        )
    # El marcador por referencia y el puntero a su hogar (P4 del oráculo vigente).
    assert DETAIL_TOKEN.search(text) and RULE_REFERENCE.search(text), (
        "PD-12 (control negativo): el substage debe mencionar el marcador "
        "`detail` Y referenciar su regla / hogar canónico."
    )
    # La referencia apunta a la regla, no al bloque de valores con la forma de
    # un consumidor que declara el conjunto cerrado.
    assert not (
        QUOTED_NEXT.search(text)
        and QUOTED_PLANNED.search(text)
        and not CANONICAL_HOME_NAME in text
    ), (
        "PD-12 (control negativo): el substage declara el conjunto cerrado de "
        "valores del marcador sin apuntar a su hogar canónico."
    )


# ---------------------------------------------------------------------------
# V-5 (PD-12) — medición del bloque estático del paquete del reviewer.
# ---------------------------------------------------------------------------


def test_v5_pd12_u2_reviewer_static_block_is_measured_and_below_the_ceiling():
    """V-5 (PD-12): el bloque estático del paquete del reviewer se mide y queda
    por debajo del techo declarado.

    O-6: el bloque es `common.md` + `roles/reviewer.md` +
    `substages/reviewer-plan-review.md`, unidos por «\n» (la convención
    congelada 003-001, la misma que compone el paquete). Techo declarado por el
    contrato: 12000 bytes (límite inclusivo, como el oráculo vigente de
    `tests/test_role_packet_render.py`:279). La medición se REGISTRA en el
    mensaje del fallo.
    """
    parts = []
    for relative in STATIC_SOURCES:
        path = PACKETS_ROOT / relative
        if not path.is_file():
            pytest.fail(f"fuente de instrucción requerida no existe: {relative}")
        parts.append(path.read_bytes())

    measured = len(b"\n".join(parts))
    assert measured <= STATIC_CEILING_BYTES, (
        f"V-5: el bloque estático del paquete del reviewer mide {measured} bytes "
        f"y supera el techo declarado de {STATIC_CEILING_BYTES} bytes."
    )
