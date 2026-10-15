#!/usr/bin/env python3
"""005-007 T6 RED — plantillas alineadas (PD-5/PD-6, con PD-10 y PD-12).

Test de consistencia ESTRUCTURAL y de comportamiento, caja negra
(precedentes dentro de esta misma feature: `tests/test_005_007_t1_progressive_detail_rule.py`
en lo estructural y `tests/test_005_007_t2_progressive_plan_validator.py` /
`tests/test_004_003_t3_plan_checks.py` en el fixture de `prepare`).
Los archivos de producto se leen AL EJECUTARSE (archivo faltante = estado
conductual => `pytest.fail`, convención del RED de T1); los oráculos derivan
SOLO del contrato aprobado (`docs/specs/005-007-progressive-planning/spec.md`,
PD-5/PD-6/PD-10/PD-12 y §5 AC-5) y de la ficha T6 del plan aprobado. El
test-writer NO derivó ningún oráculo leyendo los archivos de producto; los
tokens/rótulos pueden variar, así que las aserciones son de PRESENCIA por
familias de tokens (declaradas abajo como decisiones de oráculo), nunca de
prosa completa, estilo ni número de líneas.

Contrato que el test fija (un test por caso exigido, trazado a su postcondición):

- CASE 1 (PD-5; AC-5 primera mitad) -> `assets/spec-template/spec.md` ABRE con
  la descripción funcional derivada de un RECORRIDO DE USO: las cuatro piezas
  (actor, objetivo, punto de partida legítimo, primer resultado útil) PRESENTES
  en la apertura (título + preámbulo + primera sección de nivel ≤2; los
  subtítulos internos `###` pertenecen a la apertura), y la FIRMA no es el
  primer bloque (ningún token de firma/código-signativo en la apertura). Sus
  criterios de aceptación son COMPORTAMIENTO observable (la sección de
  aceptación ancla al comportamiento) y el ítem «Line coverage ≥ X%» NO es
  criterio de contrato (ausencia del literal en todo el archivo).
- CASE 2 (PD-6; AC-5 segunda mitad) -> existe `assets/feature-plan-template.md`
  con la FICHA de la feature y EXACTAMENTE UN bloque canónico `plan-tasks` (el
  formato vive en `planning-contract-draft.md` §4.1; la plantilla es
  consumidora, no segunda declaración). Prueba fuerte: el bloque se EXTRAe de
  la plantilla tal cual, se arma un fixture mínimo (proyecto temporal con la
  ficha de `draft-plan` ya probada verde en 004-003/005-007 T2) cuyo `plan.md`
  contiene ese bloque, y `prepare` del producto lo ACEPTA (rc == 0, paquete
  publicado): el bloque de la plantilla es válido para el validador del
  producto.
- CASE 3 (PD-6/PD-10; ficha T6) -> `skills/cdad-cycle/references/stage-2-specification.md`
  REFERENCIA la plantilla de plan de feature (por su nombre de asset) y ancla
  la RECETA MÍNIMA de aceptación de uso, sin duplicar la receta ni el formato:
  la región de la referencia (ventana corta alrededor de la mención) no
  re-enuncia la regla de detalle progresivo.
- CASE 4 (PD-12) -> el FORMATO del bloque sigue declarado UNA VEZ en su hogar
  (`planning-contract-draft.md` §4.1) y la plantilla lo REFERENCIA (consumidor,
  no segunda regla: si re-enuncia el conjunto cerrado de valores del marcador
  `detail`, debe referenciar la regla / su hogar); ni la plantilla ni la
  referencia del CASE 3 re-enuncian la regla de detalle progresivo.

Fallos del modo RED esperado (declared behavior, no error de fixture):
CASE 1 -> AssertionError (hoy la plantilla de spec abre por `Signature` y su
aceptación exige cobertura de líneas; ninguna pieza del recorrido en la
apertura — `spec-template/spec.md:17-21,41` según el contrato). CASE 2 y
CASE 4 -> `pytest.fail` de estado conductual (la plantilla de plan de feature
no existe hoy — `discovery.md:176-179`, resuelto por referencia). CASE 3 ->
AssertionError (stage-2-specification.md no menciona la plantilla). Nunca
ImportError/SyntaxError/NameError/fixture-exception. Nada de skip.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import tempfile
import unittest

import pytest

from tests.test_004_003_t1_draft_contract import (
    DRAFT_PLAN_BYTES,
    DRAFT_PLAN_RELPATH,
    DRAFT_PLAN_VERSION,
)
from tests.test_packet_prepare import PACKET_CLI, PrepareProject, run_prepare
from tests.test_role_packets import REPO_ROOT
from tests.test_005_007_t1_progressive_detail_rule import (
    DETAIL_TOKEN,
    FORMAT_DECL,
    HEADING,
    QUOTED_NEXT,
    QUOTED_PLANNED,
    RULE_REFERENCE,
    SECTION_41,
    _lines,
    _near,
    _load,
    _restates_closed_values,
)

SPEC_TEMPLATE = REPO_ROOT / "skills/cdad-cycle/assets/spec-template/spec.md"
PLAN_TEMPLATE = REPO_ROOT / "skills/cdad-cycle/assets/feature-plan-template.md"
STAGE2 = REPO_ROOT / "skills/cdad-cycle/references/stage-2-specification.md"

# Padrones de PRESENCIA (tokens-familia; los rótulos exactos pueden variar).
# PD-5: las piezas del recorrido de uso.
ACTOR = re.compile(r"(?i)\b(?:actor|usuari[oa]|coordinador|duen[oa]|agente|orchestrator|agent)\b")
GOAL = re.compile(r"(?i)\b(?:objetivo|goal|propo?sito|purpose)\b")
STARTING_POINT = re.compile(
    r"(?i)punto\s+de\s+partida|starting\s+point|partida\s+legit?im|"
    r"legitimate\s+start|en\s+reposo|starting\s+state|in\s+rest"
)
FIRST_RESULT = re.compile(
    r"(?i)primer[oa]?\s+(?:resultado|uso|entrega)|resultado\s+del\s+primer\s+uso|"
    r"resultado\s+[uú]til|first\s+(?:use|result)|useful\s+(?:result|outcome)"
)
# PD-5: la firma no es el primer bloque.
SIGNATURE_TOKEN = re.compile(
    r"(?i)\bsignature\b|(?<![a-záéíóúñ])firma(?![a-záéíóúñ])|^\s*(?:async\s+)?def\s+\w+\s*\("
)
SIGNATURE_HEADING = re.compile(r"(?i)\bsignature\b|(?<![a-záéíóúñ])firma(?![a-záéíóúñ])")
# PD-5: comportamiento como criterio; cobertura retirada del contrato.
ACCEPTANCE_HEADING = re.compile(r"(?i)acepta|criterio|criterion|acceptance")
BEHAVIOR_TOKEN = re.compile(r"(?i)comportamiento|behavior|observable")
COVERAGE_CRITERION = re.compile(
    r"(?i)line\s+coverage|cobertura\s+(?:de\s+)?l[ií]neas?|l[ií]neas?\s+de\s+cobertura"
)
# PD-6: ficha, bloque canónico y su formato referenciado.
FICHA_TOKEN = re.compile(r"(?i)feature\s*[_ ]?id|ficha\s+de\s+la\s+feature")
PLAN_TASKS_FENCE = re.compile(r"(?m)^[ \t]{0,3}```plan-tasks[ \t]*$")
PLAN_TASKS_TOKEN = re.compile(r"(?i)plan-tasks")
FORMAT_REFERENCE = re.compile(r"(?i)planning-contract-draft|4\.1|secci[oó]n\s+4\b")
# PD-6/PD-10: referencia a la plantilla desde stage-2; receta mínima de uso.
TEMPLATE_REFERENCE = re.compile(r"feature-plan-template")
RECIPE_TOKEN = re.compile(
    r"(?i)receta\s+mi[nm]ima|receta\s+(?:de\s+)?(?:acepta|us[oa])|"
    r"minimum.{0,40}recipe|recipe.{0,40}(?:minimum|acceptance|use)"
)


# ---------------------------------------------------------------------------
# Helpers estructurales (caja negra; estilo del RED de T1).
# ---------------------------------------------------------------------------

def _headings_up_to(lines_: list[str], max_level: int) -> list[int]:
    """Índices de los títulos con nivel <= max_level (#{1..max_level})."""
    out: list[int] = []
    for i, line in enumerate(lines_):
        match = re.match(r"^(#{1,6})\s", line)
        if match and len(match.group(1)) <= max_level:
            out.append(i)
    return out


def _opening_lines(text: str) -> list[str]:
    """La APERTURA de la plantilla de spec: título + preámbulo + primera
    sección de nivel <= 2 (los subtítulos `###` quedan dentro)."""
    lines_ = _lines(text)
    starts = _headings_up_to(lines_, 2)
    if not starts:
        return lines_
    end = starts[1] if len(starts) > 1 else len(lines_)
    return lines_[:end]


def _acceptance_region(lines_: list[str]) -> list[str] | None:
    """La primera sección (por título de nivel <=3, incluido su título) que
    declara los criterios de aceptación."""
    headings = _headings_up_to(lines_, 3)
    for n, start in enumerate(headings):
        end = headings[n + 1] if n + 1 < len(headings) else len(lines_)
        region = lines_[start : end + 1]
        if any(ACCEPTANCE_HEADING.search(line) for line in region):
            return region
    return None


def _reference_restates_rule(text: str, token: re.Pattern[str], window: int = 3) -> list[str]:
    """True-offender: en la(s) ventana(s) alrededor de las líneas que mencionan
    `token` (la referencia por nombre), ¿se re-enuncia la regla de detalle
    progresivo (el marcador `detail` co-ocurrente con el conjunto cerrado de
    valores)? Devuelve las líneas ofensoras (descriptas)."""
    lines_ = _lines(text)
    mentions = [i for i, line in enumerate(lines_) if token.search(line)]
    offenders: list[str] = []
    for mention in mentions:
        window_lines = lines_[max(0, mention - window) : mention + window + 1]
        if _near(window_lines, DETAIL_TOKEN, QUOTED_PLANNED, max_gap=window) and _near(
            window_lines, DETAIL_TOKEN, QUOTED_NEXT, max_gap=window
        ):
            offenders.append(f"linea {mention + 1}: {' '.join(window_lines)[:120]!r}")
    return offenders


# ---------------------------------------------------------------------------
# CASE 1 — PD-5 (AC-5, primera mitad): la plantilla de spec abre por el
# recorrido de uso; su aceptación es comportamiento, no cobertura.
# ---------------------------------------------------------------------------

def test_case1_pd5_spec_template_opens_from_user_journey():
    text = _load(SPEC_TEMPLATE)
    lines_ = _lines(text)
    opening = _opening_lines(text)
    assert opening, "PD-5: la plantilla de spec no tiene apertura analizable"

    # (1) Las cuatro piezas del recorrido están presentes en la apertura.
    missing = [
        name
        for name, pattern in (
            ("actor", ACTOR),
            ("objetivo", GOAL),
            ("punto de partida legitimo", STARTING_POINT),
            ("primer resultado util", FIRST_RESULT),
        )
        if not any(pattern.search(line) for line in opening)
    ]
    assert not missing, (
        "PD-5: la apertura de la plantilla de spec (assets/spec-template/"
        "spec.md) no deriva de un recorrido de uso: faltan las piezas "
        f"{missing} en la apertura (titulo + preambulo + primera seccion)."
    )

    # (2) La firma no es el primer bloque: sin token de firma ni línea de
    # firma (def ...) en título, preámbulo o primera sección.
    signature_hits = [
        line for line in opening
        if SIGNATURE_TOKEN.search(line)
    ]
    assert not signature_hits, (
        "PD-5: la plantilla de spec abre por la firma en lugar de la "
        "descripción funcional del recorrido de uso; primeras líneas de la "
        "apertura con firma: " + "; ".join(signature_hits[:3])
    )

    # (3) La sección de criterios de aceptación existe, se ancla al
    # comportamiento observable y retira «Line coverage ≥ X%» del contrato.
    region = _acceptance_region(lines_)
    assert region is not None, (
        "PD-5: la plantilla de spec no declara una sección de criterios de "
        "aceptación (ningún título de nivel <=3 habla de aceptación/criterios)."
    )
    assert not COVERAGE_CRITERION.search(text), (
        "PD-5: el ítem de aceptación «Line coverage ≥ X%» sigue siendo "
        "criterio de contrato en la plantilla de spec (debe retirarse del "
        "archivo)."
    )
    assert any(BEHAVIOR_TOKEN.search(line) for line in region), (
        "PD-5: los criterios de aceptación de la plantilla no se anclan al "
        "comportamiento observable (la sección de aceptación no menciona "
        "comportamiento/observable)."
    )


# ---------------------------------------------------------------------------
# CASE 2 — PD-6 (AC-5, segunda mitad): existe la plantilla de plan de feature
# con ficha + bloque canónico `plan-tasks`, y ese bloque VALIDA con el
# validador del producto.
# ---------------------------------------------------------------------------

class T6PlanTemplateCase(unittest.TestCase):
    """Fixture de `prepare` con ficha `draft-plan` (patrón congelado de
    004-003 T1/T3 y 005-007 T2: proyecto temporal, nada del repo real)."""

    def project(self) -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-005-007-t6-")
        self.addCleanup(temp.cleanup)
        return PrepareProject(Path(temp.name).resolve(), "reviewer", "plan-review")

    @staticmethod
    def draft_flags() -> tuple[str, ...]:
        return (
            "--contract-kind",
            "draft-plan",
            "--contract-path",
            DRAFT_PLAN_RELPATH,
            "--plan-version",
            DRAFT_PLAN_VERSION,
        )


def test_case2_pd6_feature_plan_template_block_validates_with_product():
    template_text = _load(PLAN_TEMPLATE)  # faltante hoy = estado conductual (RED)

    # (1) La plantilla lleva la FICHA de la feature.
    assert FICHA_TOKEN.search(template_text), (
        "PD-6: la plantilla de plan de feature (assets/feature-plan-template."
        "md) no lleva la ficha de la feature (Feature ID / ficha)."
    )

    # (2) El bloque canónico `plan-tasks` existe EXACTAMENTE una vez: la
    # plantilla es consumidora del formato declarado, no segunda declaración.
    fences = PLAN_TASKS_FENCE.findall(template_text)
    assert len(fences) == 1, (
        f"PD-6: la plantilla de plan de feature debe llevar EXACTAMENTE UN "
        f"bloque canonico plan-tasks; encontrados {len(fences)}."
    )
    match = re.search(
        r"^[ \t]{0,3}```plan-tasks[ \t]*\n(.*?)\n[ \t]{0,3}```[ \t]*$",
        template_text,
        re.DOTALL | re.MULTILINE,
    )
    assert match is not None, (
        "PD-6: el bloque canonico plan-tasks de la plantilla no esta bien "
        "cerrado (```plan-tasks ... ```)."
    )
    try:
        block = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        unittest.TestCase().fail(
            f"PD-6: el bloque canonico plan-tasks de la plantilla no es JSON "
            f"valido: {error}"
        )
    assert isinstance(block, dict), (
        "PD-6: el bloque canonico plan-tasks debe ser un objeto JSON con la "
        "clave tasks (formato de planning-contract-draft.md seccion 4.1)."
    )
    assert isinstance(block.get("tasks"), list) and block["tasks"], (
        "PD-6: el bloque canonico plan-tasks de la plantilla no declara una "
        "lista de tareas no vacia."
    )

    # (3) Prueba fuerte: el bloque EXTRAIDO tal cual de la plantilla, insertado
    # en el plan de un proyecto fixture minimo, es ACEPTADO por `prepare`
    # del producto (rc == 0) y el paquete se publica.
    case = T6PlanTemplateCase()
    project = case.project()
    plan_file = project.root / DRAFT_PLAN_RELPATH
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_bytes(DRAFT_PLAN_BYTES + match.group(0).encode())
    result = run_prepare(PACKET_CLI, *project.args(*T6PlanTemplateCase.draft_flags()))
    assert result.returncode == 0, (
        "PD-6: el bloque plan-tasks de la plantilla de feature fue RECHAZADO "
        "por el validador del producto (debe ser aceptado): "
        + result.stderr.decode(errors="replace")
    )
    packet_dir = project.out_dir / project.packet_id()
    assert (packet_dir / "PACKET.md").is_file(), (
        "PD-6: el plan aceptado no publico su paquete (PACKET.md ausente)."
    )


# ---------------------------------------------------------------------------
# CASE 3 — PD-6/PD-10 (ficha T6): stage-2 referencia la plantilla de plan de
# feature y la receta mínima de aceptación de uso, por referencia.
# ---------------------------------------------------------------------------

def test_case3_pd6_pd10_stage2_references_template_and_use_acceptance_recipe():
    stage2 = _load(STAGE2)
    lines_ = _lines(stage2)

    # (1) REFERENCIA la plantilla de plan de feature por su nombre de asset.
    assert TEMPLATE_REFERENCE.search(stage2), (
        "PD-6/PD-10: skills/cdad-cycle/references/stage-2-specification.md no "
        "referencia la plantilla de plan de feature "
        "(assets/feature-plan-template.md)."
    )

    # (2) Ancla la RECETA MINIMA de aceptación de uso (por nombre; el
    # detalle vive por referencia, no se duplica).
    assert RECIPE_TOKEN.search(stage2), (
        "PD-10: stage-2-specification.md no ancla la receta minima de "
        "aceptacion de uso (referencia nombrada)."
    )

    # (3) La referencia no re-enuncia la regla de detalle progresivo (es un
    # puntero, no una segunda copia normativa de la regla).
    offenders = _reference_restates_rule(stage2, TEMPLATE_REFERENCE)
    assert not offenders, (
        "PD-12/PD-6: la referencia a la plantilla de plan de feature en "
        "stage-2-specification.md re-enuncia la regla de detalle progresivo "
        "en su entorno inmediato (debe ser puntero): " + "; ".join(offenders[:3])
    )


# ---------------------------------------------------------------------------
# CASE 4 — PD-12 (fuente única): el formato vive una sola vez en §4.1; ni la
# plantilla ni la referencia del CASE 3 re-enuncian la regla.
# ---------------------------------------------------------------------------

def test_case4_pd12_single_source_format_and_rule():
    template_text = _load(PLAN_TEMPLATE)  # faltante hoy = estado conductual (RED)

    # (1) La plantilla es CONSUMIDORA del formato: referencia la declaración
    # (planning-contract-draft.md sección 4.1).
    assert FORMAT_REFERENCE.search(template_text), (
        "PD-12/PD-6: la plantilla de plan de feature no referencia la "
        "declaracion del formato (planning-contract-draft.md seccion 4.1); "
        "es consumidora del formato ya declarado, no una segunda regla."
    )

    # (2) La plantilla no re-enuncia la regla de detalle progresivo: si
    # re-enuncia el conjunto cerrado de valores del marcador, debe
    # referenciar la regla / su hogar.
    if _restates_closed_values(_lines(template_text)):
        assert RULE_REFERENCE.search(template_text), (
            "PD-12: la plantilla de plan de feature re-enuncia el conjunto "
            "cerrado del marcador `detail` sin referencia a la regla de "
            "detalle progresivo ni a su hogar canónico (segunda copia "
            "normativa)."
        )

    # (3) El FORMATO sigue declarado UNA VEZ en su hogar: §4.1 existe y sigue
    # declarando el bloque plan-tasks alli.
    format_text = _load(FORMAT_DECL)
    format_lines = _lines(format_text)
    hit = next(
        (i for i, line in enumerate(format_lines) if SECTION_41.match(line)),
        None,
    )
    assert hit is not None, (
        "PD-12: docs/epics/epic-004-single-source-planning/"
        "planning-contract-draft.md perdio su seccion 4.1 (hogar de la "
        "declaracion del formato del bloque plan-tasks)."
    )
    end = next(
        (
            i
            for i in range(hit + 1, len(format_lines))
            if HEADING.match(format_lines[i].strip())
        ),
        len(format_lines),
    )
    section_body = format_lines[hit + 1 : end]
    assert any(PLAN_TASKS_TOKEN.search(line) for line in section_body), (
        "PD-12: la seccion 4.1 del formato ya no declara el bloque "
        "plan-tasks; el formato del bloque debe seguir viviendo una sola "
        "vez alli."
    )

    # (4) La referencia del CASE 3 no re-enuncia la regla (puntero, no copia).
    stage2 = _load(STAGE2)
    offenders = _reference_restates_rule(stage2, TEMPLATE_REFERENCE)
    assert not offenders, (
        "PD-12: la referencia a la plantilla en stage-2-specification.md "
        "re-enuncia la regla de detalle progresivo: " + "; ".join(offenders[:3])
    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
