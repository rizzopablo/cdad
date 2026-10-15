#!/usr/bin/env python3
"""005-006 T4 RED — arranque guiado en el README (PD-11; INV-6).

Test de consistencia ESTRUCTURAL de un artefacto de distribución, caja negra
(precedentes: `tests/test_005_006_t1_start_procedure.py`,
`tests/test_005_005_t2_docs_policy.py`). Cada test lee `README.md` (único
`documentation_file` de la política del proyecto) AL EJECUTARSE y lo evalúa
contra las postcondiciones derivadas de
`docs/specs/005-006-guided-project-start/spec.md` (§2 PD-11, §3 INV-6) y de la
tarea T4 del plan aprobado (`plan.md` §T4). Los oráculos no fueron derivados
leyendo el README — provienen del contrato aprobado, y nunca buscan "frases
del prompt" ni intentan probar determinísticamente que el modelo seguirá
instrucciones (`efficient-orchestration-requirements.md:107`).

Un test por postcondición (el INV como foco estructural aparte):
- PD-11 → `README.md` incorpora una sección corta de arranque guiado que
          (a) enuncia que una instrucción breve basta para llegar a una
          primera delegación útil y (b) referencia el procedimiento
          `skills/cdad-cycle/references/project-start.md`.
- INV-6 → el prompt largo NO se reproduce en el README ni se traslada a una
          plantilla: comprobación ESTRUCTURAL (ausencia del bloque largo y de
          un artefacto-plantilla anunciado/creado para el arranque), nunca
          búsqueda de frases del prompt.

El modo de fallo esperado es AssertionError / `pytest.fail` de comportamiento
(documento inconsistente o inexistente respecto del contrato aprobado), nunca
ImportError/SyntaxError/NameError/AttributeError.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
README = REPO / "README.md"


def _load(path: Path) -> str:
    if not path.is_file():  # documento faltante es estado conductual, no error de oráculo
        pytest.fail(f"documento requerido no existe: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers estructurales (caja negra; derivados del contrato aprobado).
# ---------------------------------------------------------------------------

def _sections(text: str, heading_re: re.Pattern):
    """Devuelve (títulos,[headings], bloques[body]) de las secciones cuyo
    heading matchea `heading_re`; el body llega hasta el siguiente heading
    de cualquier nivel (o fin de archivo)."""
    sections = []
    lines = text.splitlines()
    hits = [i for i, line in enumerate(lines) if heading_re.match(line.strip())]
    for n, start in enumerate(hits):
        end = hits[n + 1] if n + 1 < len(hits) else len(lines)
        body_lines = []
        for line in lines[start + 1 : end]:
            if re.match(r"^#{1,6}\s", line.strip()) and body_lines:
                break
            body_lines.append(line)
        sections.append((lines[start].strip(), body_lines))
    return sections


def _fenced_blocks(body_lines):
    """Bloques cercados (```/~~~) del body de la sección, como listas de líneas."""
    blocks = []
    current = None
    for line in body_lines:
        if current is None:
            if re.match(r"^\s*(```|~~~)", line):
                current = []
            continue
        if re.match(r"^\s*(```|~~~)\s*$", line):
            blocks.append(current)
            current = None
        else:
            current.append(line)
    if current is not None:
        blocks.append(current)  # bloque sin cerrar: verificado tal cual
    return blocks


def _near(text: str, first_re: re.Pattern, second_re: re.Pattern, max_gap: int = 4):
    """True si `first_re` tiene una coincidencia a ≤ `max_gap` líneas de
    alguna de `second_re` (mismo párrafo corto; los wrapping no rompen el
    par)."""
    lines = text.splitlines()
    first_hits = [i for i, line in enumerate(lines) if first_re.search(line)]
    second_hits = [i for i, line in enumerate(lines) if second_re.search(line)]
    return any(
        abs(i - j) <= max_gap for i in first_hits for j in second_hits
    )


def _is_prompt_like_block(block_lines) -> bool:
    """Bloque cercado que reproduce un prompt largo: forma, no frases.

    Un prompt replicado es un bloque con muchas líneas o párrafos largos; una
    instrucción de instalación típica es una o dos líneas cortas. Umbral
    estructural: ≥ 6 líneas, o ≥ 3 párrafos, o alguna línea de párrafo larga."""
    if len(block_lines) >= 6:
        return True
    long_lines = [ln for ln in block_lines if len(ln.strip()) > 100]
    return len(long_lines) >= 3


# ---------------------------------------------------------------------------
# PD-11 — README: sección corta de arranque guiado que enuncia que una
# instrucción breve basta hasta la primera delegación útil y remite a
# references/project-start.md.
# ---------------------------------------------------------------------------

PD11_HEADING = re.compile(
    r"(?i)^#{1,6}\s+.*\b(?:"
    r"arranque\s+guiado|arranque\s+r[aá]pido|arrancar|"
    r"guided\s+(?:project\s+)?start|getting\s+started|quick\s+start|"
    r"start(?:ing)?\s+with|usando\s+cdad|c[oó]mo\s+usar"
    r")\b"
)
PD11_REFERENCE = re.compile(
    r"(?i)project-start\.md|cdad-cycle/references/project-start"
)
PD11_BRIEF_INSTRUCTION = re.compile(
    r"(?i)\binstrucci[oó]n\s+(?:breve|corta|sola)\b|\buna\s+sola\s+instrucci[oó]n\b"
    r"|\bbrief\s+(?:instruction|message|prompt)\b|\bshort\s+instruction\b|\bone[- ]?liner\b"
)
PD11_SUFFICES = re.compile(
    r"(?i)\b(?:basta|bastan|hace\s+falta|es\s+suficiente|suficiente|"
    r"\bis\s+enough|suffic\w*)\b"
)
PD11_FIRST_DELEGATION = re.compile(
    r"(?i)\b(?:primera\s+delegaci[oó]n\s+]?[uú]til|primer(?:o|a)?\s+(?:encargo|entrega)|"
    r"first\s+(?:useful\s+)?(?:delegation|assignment|delivery)|primera\s+entrega)\b"
)
PD11_SHORT_SECTION_MAX_LINES = 40  # «sección CORTA»: tope estructural del contrato


def test_pd11_readme_guided_start_section_short_statement_and_procedure_reference():
    text = _load(README)
    sections = _sections(text, PD11_HEADING)

    assert bool(sections), (
        "PD-11 violada: README.md no tiene ninguna sección de arranque guiado "
        "(heading de arranque/getting started); espera: una sección corta que "
        "enuncie que una instrucción breve basta y remita a "
        "skills/cdad-cycle/references/project-start.md"
    )

    ok = []
    for title, body_lines in sections:
        body = "\n".join(body_lines)
        scores = []
        # (a) la instrucción breve basta → primera delegación útil
        scores.append(
            _near(body, PD11_BRIEF_INSTRUCTION, PD11_SUFFICES)
        )
        # (b) referencia al procedimiento corto de arranque
        scores.append(bool(PD11_REFERENCE.search(body)))
        # CORTA: tope estructural de líneas de la sección
        non_blank = [ln for ln in body_lines if ln.strip()]
        scores.append(len(non_blank) <= PD11_SHORT_SECTION_MAX_LINES)
        if all(scores) and PD11_FIRST_DELEGATION.search(body):
            ok.append(title)

    assert ok, (
        "PD-11 violada: la sección de arranque guiado de README.md no cumple "
        "el contrato (sección CORTA que (a) enuncie que una instrucción breve "
        "basta hasta la primera delegación útil y (b) referencie "
        "references/project-start.md); secciones candidatas: "
        f"{[t for t, _ in sections]}"
    )


# ---------------------------------------------------------------------------
# INV-6 — el prompt largo NO se reproduce en el README ni se traslada a una
# plantilla: comprobación ESTRUCTURAL (bloque/plantilla ausente), nunca por
# frases («no frases del prompt», efficient-orchestration-requirements:107).
# ---------------------------------------------------------------------------

INV6_TEMPLATE_POINTER = re.compile(
    r"(?i)[`<?]*[\w/.\-\s]*(?:plantilla|template)[\w/.\-]*\.(?:md|txt|j2|tmpl)[`>]*"
)
INV6_START_TEMPLATE_NAME = re.compile(
    r"(?i)project[-_ ]?start.*(prompt|template|plantilla)"
    r"|(?:prompt|template|plantilla)[-_.]*(?:project[-_ ]?start|guided[-_ ]?start|arranque)"
)


def test_inv6_no_long_prompt_block_and_no_template_for_the_start():
    text = _load(README)
    sections = _sections(text, PD11_HEADING)
    if not sections:
        pytest.fail(
            "INV-6 no evaluable: README.md no tiene sección de arranque guiado "
            "(PD-11 sin implementar); el invariante se evalúa sobre la "
            "sección que cumple el contrato (el arranque guiado debe existir "
            "COMO puntero corto, no como ausencia total)"
        )

    # (i) ninguna sección candidata de arranque reproduce el prompt largo
    #     (bloque cercado largo/no contenido en un pointer corto).
    offenders = []
    for title, body_lines in sections:
        for block in _fenced_blocks(body_lines):
            if _is_prompt_like_block(block):
                offenders.append(title)
                break
    assert not offenders, (
        "INV-6 violada: la sección de arranque de README.md contiene un bloque "
        f"cercado con forma de prompt largo en: {offenders}; el arranque es un "
        "puntero corto al procedimiento, no una copia de instrucciones"
    )

    # (ii) la sección no traslada el prompt a una plantilla (puntero a un
    #      artefacto plantilla en vez del procedimiento).
    template_ptrs = []
    for title, body_lines in sections:
        if INV6_TEMPLATE_POINTER.search("\n".join(body_lines)):
            template_ptrs.append(title)
    assert not template_ptrs, (
        "INV-6 violada: la sección de arranque de README.md remite a una "
        f"plantilla en: {template_ptrs}; debe referenciar "
        "references/project-start.md (INV-6: el prompt largo no se traslada a "
        "una plantilla)"
    )

    # (iii) ningún artefacto-plantilla nuevo para el arranque/prompt largo en
    #       la zona de documentación del repo (estructura, no frases).
    template_files = []
    candidates = [REPO / "docs", README]
    for root in candidates:
        if root.is_file():
            if INV6_START_TEMPLATE_NAME.search(root.name):
                template_files.append(str(root.relative_to(REPO)))
            continue
        if root.is_dir():
            for f in root.rglob("*.md"):
                if INV6_START_TEMPLATE_NAME.search(f.name):
                    template_files.append(str(f.relative_to(REPO)))
    assert not template_files, (
        "INV-6 violada: hay artefactos tipo plantilla del arranque/prompt "
        f"largo en: {template_files}; la solución es el procedimiento corto "
        "por referencia (D8/PD-15), no una plantilla"
    )
