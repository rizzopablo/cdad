#!/usr/bin/env python3
"""005-007 T1 RED — regla de detalle progresivo y su único hogar canónico.

Test de consistencia ESTRUCTURAL, caja negra (precedentes:
`tests/test_005_006_t4_readme.py`, `tests/test_005_006_t1_start_procedure.py`,
`tests/test_005_005_t2_docs_policy.py`). Cada test lee los archivos de
producto AL EJECUTARSE (archivo faltante = estado conductual => `pytest.fail`),
y los evalúa contra oráculos derivados SOLO del contrato aprobado
(`docs/specs/005-007-progressive-planning/spec.md`, PD-1/PD-2/PD-12 y §6 D1/D2)
y de la ficha T1 del plan aprobado. El test-writer NO derivó ningún oráculo
leyendo los archivos de producto.

Contrato que el test fija (un test por propiedad, trazada a su postcondición):

- P1 (PD-1; D1/D2) -> el HOGAR CANÓNICO
  `skills/cdad-cycle/references/stage-2-specification.md` declara el marcador
  por tarea `detail` y su conjunto CERRADO de valores: el token `detail` y los
  valores `"next"` y `"planned"` presentes, co-occurriendo con el marcador.
- P2 (PD-1 + PD-2) -> el hogar canónico declara los campos exigidos a una
  tarea `detail == "planned"` (`objective`, `depends_on`, `uncertainty`,
  `owner`, `resolves_when`) en la misma sección del marcador; y el plan de
  validación por tarea (`focal_tests`/`observable_checks`/`regressions`/
  `integration_gate`) queda declarado como exigido a las tareas `"next"`/sin
  marcador (la exigencia está anclada a `"next"`/«sin marcador», no a
  `"planned"`).
- P3 (PD-12; D1) -> la declaración del FORMATO
  (`docs/epics/epic-004-single-source-planning/planning-contract-draft.md`
  sección 4.1) menciona el marcador `detail` y REFERENCIA la regla / su hogar
  (no re-enuncia la regla: se afirman el token y la referencia, no prosa).
- P4 (PD-12) -> la subfase
  `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` menciona el
  marcador `detail` y referencia la regla / su hogar (la consume por
  referencia).
- P5 (PD-12; fuente única) -> el par de valores del conjunto cerrado aparece
  en el hogar canónigo y, si aparece en OTRO archivo de la skill
  (`skills/cdad-cycle/references/**/*.md`, `skills/cdad-cycle/packets/**/*.md`),
  ese archivo referencia la regla / su hogar (es consumidor, no segunda copia
  normativa).

Los fallos del modo RED esperado son `AssertionError` de comportamiento (la
regla aún no está en su hogar / no hay referencia) o `pytest.fail` de estado
(archivo requerido inexistente), nunca ImportError/SyntaxError/NameError.
Nada de skip. Sin asserts de prosa completa, de estilo ni de número de líneas.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

CANONICAL_HOME = REPO / "skills/cdad-cycle/references/stage-2-specification.md"
FORMAT_DECL = (
    REPO / "docs/epics/epic-004-single-source-planning/planning-contract-draft.md"
)
REVIEWER_SUBPHASE = (
    REPO / "skills/cdad-cycle/packets/substages/reviewer-plan-review.md"
)

# Globs de la fuente única (P5): ninguna otra referencia/paquete de la skill
# re-enuncía el conjunto cerrado de valores del marcador.
SINGLE_SOURCE_GLOBS = [
    "skills/cdad-cycle/references/**/*.md",
    "skills/cdad-cycle/packets/**/*.md",
]

DETAIL_TOKEN = re.compile(r"(?i)(?<![A-Za-z_])detail(?![A-Za-z_])")
QUOTED_NEXT = re.compile(r"[\"'`]next[\"'`]")
QUOTED_PLANNED = re.compile(r"[\"'`]planned[\"'`]")
CASE_INSENSITIVE = re.IGNORECASE

RULE_REFERENCE = re.compile(
    r"stage-2-specification\.md|(?i:regla\s+de\s+detalle\s+progresivo)|"
    r"progressive-detail"
)

PLANNED_FIELDS = [
    re.compile(r"(?i)(?<![A-Za-z_])objective(?![A-Za-z_])"),
    re.compile(r"(?i)(?<![A-Za-z_])depends_on(?![A-Za-z_])"),
    re.compile(r"(?i)(?<![A-Za-z_])uncertainty(?![A-Za-z_])"),
    re.compile(r"(?i)(?<![A-Za-z_])owner(?![A-Za-z_])"),
    re.compile(r"(?i)(?<![A-Za-z_])resolves_when(?![A-Za-z_])"),
]
VALIDATION_FIELDS = [
    re.compile(r"(?i)(?<![A-Za-z_])focal_tests(?![A-Za-z_])"),
    re.compile(r"(?i)(?<![A-Za-z_])observable_checks(?![A-Za-z_])"),
    re.compile(r"(?i)(?<![A-Za-z_])regressions(?![A-Za-z_])"),
    re.compile(r"(?i)(?<![A-Za-z_])integration_gate(?![A-Za-z_])"),
]
NON_PLANNED_SCOPE = re.compile(
    r"[\"'`]next[\"'`]|(?i:sin\s+(?:el\s+)?marcador)|(?i:markerless)"
)
HEADING = re.compile(r"^#{1,6}\s")
SECTION_41 = re.compile(r"(?m)^#{1,6}\s+4\.?1\b")


def _load(path: Path) -> str:
    """Archivo requerido faltante es estado conductual, no error de oráculo."""
    if not path.is_file():
        pytest.fail(f"archivo requerido no existe: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers estructurales (caja negra; derivados del contrato aprobado).
# ---------------------------------------------------------------------------

def _lines(text: str):
    return text.splitlines()


def _near(
    lines,
    first: re.Pattern,
    second: re.Pattern,
    max_gap: int = 4,
):
    """True si algún match de `first` está a <= max_gap líneas de algún match
    de `second` (mismo párrafo corto; el wrapping no rompe el par)."""
    first_hits = [i for i, ln in enumerate(lines) if first.search(ln)]
    second_hits = [i for i, ln in enumerate(lines) if second.search(ln)]
    return any(abs(i - j) <= max_gap for i in first_hits for j in second_hits)


def _sections(text: str):
    """(índice_título, body) por heading; body hasta el próximo heading de
    cualquier nivel (o fin de archivo)."""
    lines = _lines(text)
    starts = [i for i, ln in enumerate(lines) if HEADING.match(ln.strip())]
    sections = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        sections.append(lines[start + 1 : end])
    return sections


def _marker_sections(text: str):
    """Secciones (por heading) que contienen el marcador `detail` y el valor
    de cierre `"planned"`: el lugar donde la regla declara la tarea
    planificada-no-detallada."""
    return [
        body
        for body in _sections(text)
        if any(DETAIL_TOKEN.search(ln) for ln in body)
        and any(QUOTED_PLANNED.search(ln) for ln in body)
    ]


def _restates_closed_values(lines, max_gap: int = 4) -> bool:
    """Enunciar el conjunto cerrado de valores: el token `detail` co-ocurre
    (en una ventana corta) con `"next"` y con `"planned"`."""
    return (
        _near(lines, DETAIL_TOKEN, QUOTED_NEXT, max_gap)
        and _near(lines, DETAIL_TOKEN, QUOTED_PLANNED, max_gap)
    )


# ---------------------------------------------------------------------------
# P1 — PD-1 (D1/D2): el hogar canónico declara el marcador y su conjunto
# CERRADO de valores `"next"` | `"planned"`.
# ---------------------------------------------------------------------------

def test_p1_pd1_canonical_home_declares_detail_marker_and_closed_values():
    text = _load(CANONICAL_HOME)
    assert DETAIL_TOKEN.search(text), (
        "PD-1/D1: el hogar canónico skills/cdad-cycle/references/"
        "stage-2-specification.md no declara el marcador por tarea `detail`."
    )
    marker_lines = [
        i for i, ln in enumerate(_lines(text)) if DETAIL_TOKEN.search(ln)
    ]
    quoted_next = [
        i for i, ln in enumerate(_lines(text)) if QUOTED_NEXT.search(ln)
    ]
    quoted_planned = [
        i for i, ln in enumerate(_lines(text)) if QUOTED_PLANNED.search(ln)
    ]
    assert any(
        abs(i - j) <= 4 for i in marker_lines for j in quoted_next
    ), (
        "PD-1/D2: el conjunto cerrado de valores del marcador `detail` no está "
        "declarado: falta el valor \"next\" co-occurrente con `detail` en el "
        "hogar canónico."
    )
    assert any(
        abs(i - j) <= 4 for i in marker_lines for j in quoted_planned
    ), (
        "PD-1/D2: el conjunto cerrado de valores del marcador `detail` no está "
        "declarado: falta el valor \"planned\" co-occurrente con `detail` en "
        "el hogar canónico."
    )


# ---------------------------------------------------------------------------
# P2 — PD-1 + PD-2: campos exigidos a la tarea "planned" en la sección del
# marcador; plan de validación por tarea exigido a "next"/sin marcador.
# ---------------------------------------------------------------------------

def test_p2_pd1_pd2_planned_fields_and_validation_plan_scoping():
    text = _load(CANONICAL_HOME)
    sections = _marker_sections(text)
    assert sections, (
        "PD-1/D2: el hogar canónico no declara la tarea "
        "planificada-no-detallada (ninguna sección contiene `detail` con el "
        "valor \"planned\")."
    )
    missing_fields = [
        pattern.pattern
        for section in sections
        for pattern in PLANNED_FIELDS
        if not any(pattern.search(ln) for ln in section)
    ]
    # La exigencia es que la sección del marcador nombre los cinco campos;
    # si falta alguno en TODA sección candidata, la propiedad falla.
    all_present_in_one = any(
        all(
            any(pattern.search(ln) for ln in section)
            for pattern in PLANNED_FIELDS
        )
        for section in sections
    )
    assert all_present_in_one, (
        "PD-1: ninguna sección que declara el marcador `detail` enumera los "
        "campos exigidos a la tarea \"planned\" (objective, depends_on, "
        "uncertainty, owner, resolves_when); patrones ausentes en al menos "
        f"una sección de referencia: {missing_fields}."
    )
    scoped = any(
        _near(section, NON_PLANNED_SCOPE, pattern, max_gap=3)
        for section in sections
        for pattern in VALIDATION_FIELDS
    )
    assert scoped, (
        "PD-2: el hogar canónico no declara el plan de validación por tarea "
        "(focal_tests/observable_checks/regressions/integration_gate) como "
        "exigido a las tareas \"next\" o sin marcador (no hay co-ocurrencia "
        "co-ocurrencia con la ventana del marcador)."
    )
    # La exigencia de plan de validación NO queda declarada sobre la tarea
    # "planned": ningún par (planned, campo de validación) en la misma línea.
    entangled = [
        ln
        for section in sections
        for ln in section
        if QUOTED_PLANNED.search(ln)
        and any(p.search(ln) for p in VALIDATION_FIELDS)
    ]
    assert not entangled, (
        "PD-1: la sección del marcador declara el plan de validación por "
        "tarea sobre la línea de la tarea \"planned\" (debe quedar exigido "
        "solo a \"next\"/sin marcador): " + "; ".join(entangled[:3])
    )


# ---------------------------------------------------------------------------
# P3 — PD-12 (D1): el FORMATO (planning-contract-draft.md §4.1) menciona el
# marcador `detail` y REFERENCIA la regla, no la re-enuncia.
# ---------------------------------------------------------------------------

def test_p3_pd12_format_section_41_declares_field_by_reference():
    text = _load(FORMAT_DECL)
    lines = _lines(text)
    hit = next(
        (i for i, ln in enumerate(lines) if SECTION_41.search(ln)),
        None,
    )
    assert hit is not None, (
        "PD-12/D1: docs/epics/epic-004-single-source-planning/"
        "planning-contract-draft.md no tiene una sección 4.1 (declaración del "
        "formato) donde declarar el campo del bloque plan-tasks."
    )
    end = next(
        (
            i
            for i in range(hit + 1, len(lines))
            if HEADING.match(lines[i].strip())
        ),
        len(lines),
    )
    body = lines[hit + 1 : end]
    assert any(DETAIL_TOKEN.search(ln) for ln in body), (
        "PD-12/D1: la sección 4.1 del formato no menciona el marcador por "
        "tarea `detail` (el campo del bloque plan-tasks quedará sin "
        "declarar)."
    )
    assert any(RULE_REFERENCE.search(ln) for ln in body), (
        "PD-12/D1: la sección 4.1 del formato no REFERENCIA la regla de "
        "detalle progresivo ni su hogar canónico (stage-2-specification.md); "
        "re-enunciarla allí violaría la fuente única."
    )


# ---------------------------------------------------------------------------
# P4 — PD-12: la subfase reviewer-plan-review consume el marcador por
# referencia (menciona `detail` y referencia la regla).
# ---------------------------------------------------------------------------

def test_p4_pd12_reviewer_plan_review_consumes_marker_by_reference():
    text = _load(REVIEWER_SUBPHASE)
    assert DETAIL_TOKEN.search(text), (
        "PD-12: la subfase skills/cdad-cycle/packets/substages/"
        "reviewer-plan-review.md no menciona el marcador `detail` que debe "
        "consumir."
    )
    assert RULE_REFERENCE.search(text), (
        "PD-12: la subfase reviewer-plan-review.md no referencia la regla de "
        "detalle progresivo ni su hogar canónico (debe consumir el marcador "
        "por referencia, no re-enunciarlo)."
    )


# ---------------------------------------------------------------------------
# P5 — PD-12 (fuente única): el par de valores vive en el hogar canónico; en
# cualquier otro archivo de la skill, si aparece, ese archivo es/referencia
# la regla declarada (por ejemplo el formato o un consumidor por referencia).
# ---------------------------------------------------------------------------

def test_p5_pd12_single_source_no_second_copy_of_closed_value_set():
    canonical = _load(CANONICAL_HOME)
    canonical_lines = _lines(canonical)
    assert _restates_closed_values(canonical_lines), (
        "PD-12: el conjunto cerrado de valores del marcador (\"next\"|"
        "\"planned\") no está declarado en el hogar canónico."
    )
    offenders = []
    for pattern in SINGLE_SOURCE_GLOBS:
        paths = sorted(REPO.glob(pattern))
        assert paths, f"glob de fuente única sin archivos: {pattern}"
        for path in paths:
            if path == CANONICAL_HOME:
                continue
            text = path.read_text(encoding="utf-8")
            if _restates_closed_values(_lines(text)) and not (
                RULE_REFERENCE.search(text)
            ):
                offenders.append(str(path.relative_to(REPO)))
    assert not offenders, (
        "PD-12: hay una segunda copia del conjunto cerrado de valores del "
        "marcador (sin referencia a la regla ni a su hogar) fuera del hogar "
        "canónico: " + ", ".join(offenders)
    )
