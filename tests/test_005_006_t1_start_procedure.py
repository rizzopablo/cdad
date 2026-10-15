#!/usr/bin/env python3
"""005-006 T1 RED — procedimiento corto de arranque (PD-1, PD-3..PD-9, PD-13, PD-15; INV-1..INV-4).

Test de consistencia ESTRUCTURAL de artefactos distribuidos, caja negra
(precedente: `tests/test_005_005_t2_docs_policy.py`). Cada test lee los archivos
AL EJECUTARSE y los evalúa contra las postcondiciones derivadas de
`docs/specs/005-006-guided-project-start/spec.md` (§2 PD-n, §3 INV-n) y de la
tarea T1 del plan aprobado (`plan.md` §T1). Los oráculos no fueron derivados
leyendo los archivos evaluados — provienen del contrato aprobado, y nunca
buscan "frases del prompt" ni intentan probar determinísticamente que el
modelo seguirá instrucciones (`efficient-orchestration-requirements.md:107`).

Un test por postcondición (los INV como foco estructural aparte):
- PD-1  → `project-start.md` existe; hay fila en la tabla «How to read the
          references» de `SKILL.md`; procedure referencia los cinco dueños.
- PD-3  → reconoce la raíz sin imponer layout: nested/contenedor declarado,
          sesión = pista no norma, sin búsqueda global.
- PD-4  → tres clases (nuevo / parcialmente inicializado / configuración
          incompleta) usando los primitivos por referencia.
- PD-5  → preservación de lo existente ( bootstrap anti-patterns +
          project-execution no-clobber, referenciados).
- PD-6  → tabla (o lista canónica) restricción → lugar canónico, con las seis
          restricciones de la spec y sus lugares canónicos.
- PD-7  → inferible vs decisión del usuario; preguntas acotadas; sin usuario
          registra la duda (activeContext).
- PD-8  → encadenado hasta la preparación del primer encargo (camino de
          ejecución preparada, `project-execution`).
- PD-9  → rama «sin ejecución activa → no resume» en el procedimiento y en el
          paso 1 del flujo de `SKILL.md`.
- PD-10 (puntos T1) → los puntos de cableado que lista el plan
          (`SKILL.md` ~:260-261 y ~:451-452; `continuity.md` ~:31-44) no usan
          una ruta del CLI relativa al proyecto consumidor. Además, la región
          de los Pasos 5-8 del flujo del orquestador en `SKILL.md`
          (~:277-443, hallazgo F1 de la review formal — re-entry ~:278) se
          barre con la misma regla: 0 rutas del CLI relativas SIN marcar.
- PD-13 → `state-detection.md` declara el dueño canónico y apunta al arranque;
          el procedimiento no re-declara la propiedad.
- PD-15 / INV-6 → ninguna plantilla del prompt largo bajo `skills/cdad-cycle/assets/`.
- INV-1 → el procedimiento no copia los artefactos estructurales de los dueños
          (headings/tablas del algoritmo de detección ni de política/autoridad).
- INV-2 / INV-3 / INV-4 → enunciado explícito de no-pisa / solo-el-usuario-decide
          / nunca `resume` sin ejecución activa, nunca fabrica, nunca cambia
          de versión en silencio.

El modo de fallo esperado es AssertionError / `pytest.fail` de comportamiento
(documento inconsistente o inexistente respecto del contrato aprobado), nunca
ImportError/SyntaxError/NameError/AttributeError.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "cdad-cycle" / "SKILL.md"
REFS = REPO / "skills" / "cdad-cycle" / "references"
PSTART = REFS / "project-start.md"
EPIC_STATE_DETECTION = REPO / "skills" / "cdad-epic" / "references" / "state-detection.md"
CONTINUITY = REFS / "continuity.md"
ASSETS = REPO / "skills" / "cdad-cycle" / "assets"

OWNER_FILES = [
    REFS / "state-detection.md",
    REFS / "project-execution.md",
    REFS / "continuity.md",
    REFS / "bootstrap.md",
    EPIC_STATE_DETECTION,
]


def _load(path: Path) -> str:
    if not path.is_file():  # documento faltante es estado conductual, no error de oráculo
        pytest.fail(f"documento requerido no existe: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers estructurales (caja negra; derivados del contrato aprobado).
# ---------------------------------------------------------------------------

def _table_rows_under_heading(text: str, heading_re: re.Pattern):
    """Devuelve (idx_del_heading_o_None, filas_de_tabla_inmediatamente_posteriores).

    Una fila es una línea que empieza por `|` (o que abre la tabla) hasta la
    primera línea no-tabla no-vacía; las filas separadoras `|---|` se descartan.
    """
    lines = text.splitlines()
    idx = None
    for i, line in enumerate(lines):
        if heading_re.match(line.strip()):
            idx = i
            break
    if idx is None:
        return None, []
    rows = []
    for line in lines[idx + 1 :]:
        stripped = line.strip()
        if not stripped:
            if rows:
                break
            continue
        if re.match(r"^\|", stripped):
            body = stripped.strip("|")
            if not re.fullmatch(r"[\s:\-\|]+", body):
                rows.append(stripped)
        elif rows:
            break
    return idx, rows


def _table_or_list_lines(text: str):
    """Líneas con forma de fila de tabla o ítem de lista canónica."""
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if re.match(r"^\|", s):
            if not re.fullmatch(r"[\s:\-\|]+", s.strip("|")):
                out.append((i, s))
        elif re.match(r"^(?:[-*]|\d+[\.\)])\s", s):
            out.append((i, s))
    return out


def _structural_artifacts(text: str):
    """Artefactos estructurales de un dueño: headings (>=18 chars) y filas de
    tabla (>=2 pipes y >=25 chars de cuerpo).

    La copia estructural detectada aquí es la que INV-1 prohíbe: si
    `project-start.md` re-aparece un heading o una fila de tabla de un dueño
    (algoritmo de detección, tabla de política/autoridad), INV-1 está violada.
    """
    artifacts = set()
    for line in text.splitlines():
        s = line.rstrip()
        if s.startswith("#"):
            heading = s.lstrip("#").strip()
            if len(heading) >= 18:
                artifacts.add(_norm(heading))
            continue
        stripped = s.strip()
        if re.match(r"^\|", stripped) and stripped.count("|") >= 2:
            body = stripped.strip("|").strip()
            if not re.fullmatch(r"[\s:\-\|]+", body) and len(body) >= 25:
                artifacts.add(_norm(body))
    return artifacts


def _norm(text: str) -> str:
    """Normaliza un fragmento para comparación estructural (sin formato md)."""
    cleaned = re.sub(r"[`*_]", "", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned


def _window(text: str, lo: int, hi: int):
    """Líneas [lo, hi] (1-based, índices tolerantes al fin del archivo)."""
    lines = text.splitlines()
    return [(i + 1, lines[i]) for i in range(max(0, lo - 1), min(len(lines), hi))]


def _closest_n(text: str, target_re: re.Pattern, n: int):
    """(números_de_línea, líneas) de las primeras n coincidencias del patrón."""
    hits = [
        (i + 1, line)
        for i, line in enumerate(text.splitlines())
        if target_re.search(line)
    ]
    return hits[:n]


# ---------------------------------------------------------------------------
# PD-1 — procedimiento corto existente, fila de la tabla de referencias y
# referencia (no copia) de los cinco dueños canónicos.
# ---------------------------------------------------------------------------

PD1_HEADING = re.compile(r"^#{1,6}\s+How to read the references\s*$")

PD1_OWNER_REFS = [
    ("state-detection", re.compile(r"state-detection\.md")),
    ("project-execution", re.compile(r"project-execution\.md")),
    ("continuity", re.compile(r"continuity\.md")),
    ("bootstrap", re.compile(r"bootstrap\.md")),
    ("cdad-epic/references/state-detection", re.compile(r"cdad-epic")),
]


def test_pd1_procedure_exists_table_row_and_owner_references():
    # El archivo es estado conductual: si falta, el contrato PD-1 no está.
    if not PSTART.is_file():
        pytest.fail(f"PD-1 violada: el procedimiento corto no existe: {PSTART}")
    text = PSTART.read_text(encoding="utf-8")
    skill = _load(SKILL)

    # 1) La tabla «How to read the references» de SKILL.md tiene una fila para él.
    idx, rows = _table_rows_under_heading(skill, PD1_HEADING)
    assert idx is not None, (
        "PD-1 violada: SKILL.md no declara la sección «How to read the "
        "references» (título exacto, una sola instancia de carga)"
    )
    assert any("project-start.md" in row for row in rows), (
        "PD-1 violada: la tabla «How to read the references» de SKILL.md no "
        "tiene una fila que liste references/project-start.md"
    )

    # 2) El procedimiento es una sola lectura que REFERENCIA a los cinco dueños.
    missing = []
    for name, pattern in PD1_OWNER_REFS:
        if not pattern.search(text):
            missing.append(name)
    assert not missing, (
        "PD-1 violada: project-start.md no referencia a los dueños canónicos "
        f"declarados por la spec (faltan: {missing}); debe componer por "
        "referencia, nunca copiando (INV-1)"
    )

    # 3) Procedimiento corto: no re-declara la entrada de intake del orquestador
    #    ni el texto de regeneración (estructura propia de otras fuentes).
    forbidden_skills_intake = re.compile(
        r"(?i)\bPrepared execution path\b|\bLegacy path \(fallback"
    )
    assert not forbidden_skills_intake.search(text), (
        "PD-1 violada: project-start.md reproduce la estructura del intake del "
        "orquestador (camino preparado/legacy) en lugar de referenciarla"
    )


# ---------------------------------------------------------------------------
# PD-3 — reconocimiento de raíz sin imponer layout: sesión = pista, no norma;
# repo anidado/contenedor; sin búsqueda global.
# ---------------------------------------------------------------------------

P3_NESTED = re.compile(
    r"(?i)\b(?:nested|anid\w+|container|contenedor|host directory|parent "
    r"directory|directorio contenedor|directorio superior)\b"
)
P3_HINT_NOT_NORM = re.compile(
    r"(?i)(?:\b(?:hint|pista|clue|pista)\b)|(?:pista,\s*no\s*norma)|(?:hint,\s*not\s*(?:a\s*)?norm)"
)
P3_NO_GLOBAL_SEARCH = re.compile(
    r"(?i)\b(?:sin|no|without|avoid|not)\b[^.\n]{0,30}"
    r"(?:global|masiv\w*|masiva|exhaustiv\w*)[^.\n]{0,30}?"
    r"(?:search|searches|b[úu]squeda|b[uú]squeda|búsqueda|búsqueda global)"
)
P3_NO_IMPOSE = re.compile(
    r"(?i)\b(?:no|not|without|sin|nunca|never|jamás|i?jamás)\b[^.\n]{0,30}"
    r"(?:impos\w+|impon\w*|imponer|exig\w+|layout|estructura)\b"
)


def test_pd3_root_recognition_without_imposing_layout():
    text = _load(PSTART)

    # Directorio de sesión = pista, no norma (y algo de layout no impuesto).
    assert P3_NESTED.search(text), (
        "PD-3 violada: el procedimiento no declara el caso de sesión abierta en "
        "un directorio contenedor / repo anidado"
    )
    assert P3_HINT_NOT_NORM.search(text), (
        "PD-3 violada: el procedimiento no enuncia que el directorio de sesión "
        "es pista, no norma (hint, not norm)"
    )
    assert P3_NO_IMPOSE.search(text), (
        "PD-3 violada: el procedimiento no declara que reconoce la raíz sin "
        "imponer un layout"
    )
    # La detección llega a la raíz sin una búsqueda global.
    assert P3_NO_GLOBAL_SEARCH.search(text), (
        "PD-3 violada: el procedimiento no enuncia el reconocimiento de la raíz "
        "sin una búsqueda global (R2 exige llegar al repo anidado sin barrido "
        "global)"
    )


# ---------------------------------------------------------------------------
# PD-4 — clasificación nuevo / parcialmente inicializado / configuración
# incompleta, usando los primitivos existentes por referencia (sin re-declarar
# el algoritmo de detección: eso también lo cubre INV-1).
# ---------------------------------------------------------------------------

P4_CLASS_NEW = re.compile(r"(?i)\b(?:new|nuevo|desde\s+cero|fresh|virgen)\b")
P4_CLASS_PARTIAL = re.compile(r"(?i)\b(?:partial|parcial)\w*\b")
P4_CLASS_INCOMPLETE = re.compile(r"(?i)\b(?:incomplete|incompleta|incomplet\w*)\b")
P4_PARTIAL_SIGNAL = re.compile(r"(?i)\bactive_(?:epic|feature)\b")
P4_MEMORY_BANK = re.compile(r"(?i)\bmemory\s+bank\b|\bmemory bank\b")
P4_PRIMITIVES = [
    ("state-detection", re.compile(r"state-detection")),
    ("project-execution", re.compile(r"project-execution")),
]


def test_pd4_three_classes_by_reference_to_primitives():
    text = _load(PSTART)

    assert P4_CLASS_NEW.search(text), (
        "PD-4 violada: el procedimiento no nombra la clase «nuevo» (proyecto "
        "sin Memory Bank)"
    )
    assert P4_CLASS_PARTIAL.search(text), (
        "PD-4 violada: el procedimiento no nombra la clase «parcialmente "
        "inicializado»"
    )
    assert P4_CLASS_INCOMPLETE.search(text), (
        "PD-4 violada: el procedimiento no nombra la clase «configuración "
        "incompleta»"
    )
    # El caso parcial se define con los marcadores del estado (active_epic/epic).
    assert P4_PARTIAL_SIGNAL.search(text), (
        "PD-4 violada: la definición de «parcialmente inicializado» no usa los "
        "marcadores active_epic/active_feature del primitivo"
    )
    assert P4_MEMORY_BANK.search(text), (
        "PD-4 violada: el procedimiento no menciona Memory Bank (insumo de la "
        "clase nuevo/parcial)"
    )
    # Apunta a los primitivos existentes (referencia, no re-declaración).
    missing = [name for name, pattern in P4_PRIMITIVES if not pattern.search(text)]
    assert not missing, (
        "PD-4 violada: el procedimiento no apunta a los primitivos existentes "
        f"(faltan: {missing}); no debe re-declarar el algoritmo (INV-1)"
    )


# ---------------------------------------------------------------------------
# PD-5 — preservar lo existente: no pisa documentación, planes ni convenciones;
# referencia los anti-patrones de bootstrap y el no-clobber de project-execution.
# ---------------------------------------------------------------------------

P5_NO_PISA = re.compile(
    r"(?i)\b(?:no[- ]?(?:clobber|pisar|pisa)|not\s+(?:overwrite|pisa)|never\s+"
    r"(?:overwrite|pisa)|nunca\s+pisar?|do\s+not\s+(?:overwrite|clobber)|"
    r"(?:preserve|preserve|preserv\w+)|no\s+pisa?|intact)\b"
)
P5_ANTI_PATTERNS = re.compile(r"(?i)\banti[- ]?patternc\w*|anti[- ]?pattern\w*|anti[- ]?patr\w*")
P5_EXISTING = re.compile(
    r"(?i)\b(?:existing|existente|existentes|preexist\w*|preservar lo existente)\b"
)
P5_CONVENTIONS = re.compile(
    r"(?i)\b(?:convenciones|nomenclatur\w*|naming|conventions|planes)\b"
)


def test_pd5_preservation_of_existing():
    text = _load(PSTART)

    # Regla explícita de no-pisado / preservación (formato aislado).
    assert P5_NO_PISA.search(text) and P5_EXISTING.search(text), (
        "PD-5 violada: el procedimiento no enuncia la regla de preservación de "
        "lo existente (documentación, planes, convenciones, nomenclatura)"
    )
    assert P5_ANTI_PATTERNS.search(text), (
        "PD-5 violada: el procedimiento no referencia los anti-patrones de "
        "bootstrap.md (dueño canónico de la preservación en el bootstrap)"
    )
    assert P5_CONVENTIONS.search(text), (
        "PD-5 violada: el procedimiento no declara el alcance de la "
        "preservación (convenciones/nomenclatura/planes existentes)"
    )
    # Dueños referenciados, no re-implementados.
    assert re.search(r"bootstrap\.md", text), (
        "PD-5 violada: no referencia bootstrap.md (anti-patrones de bootstrap)"
    )
    assert re.search(r"project-execution\.md", text), (
        "PD-5 violada: no referencia project-execution.md (regla no-clobber)"
    )


# ---------------------------------------------------------------------------
# PD-6 — registro de restricciones en su lugar canónico (tabla o lista
# canónica): cada elemento contiene ambos lados del mapa.
# ---------------------------------------------------------------------------

P6_RESTRICTION_TABLE = [
    ("stack",
     re.compile(r"(?i)\bstack\b"),
     re.compile(r"(?i)\bstate\.stack\b")),
    ("privacidad",
     re.compile(r"(?i)\b(?:privacidad|privacy)\b"),
     re.compile(r"(?i)\b(?:private_paths|cdad-policy\.json)\b")),
    ("entorno de pruebas",
     re.compile(r"(?i)\b(?:entorno de prueb\w*|test environment|test environment)\b"),
     re.compile(r"(?i)\btest_roots\b")),
    ("límites operativos",
     re.compile(r"(?i)\b(?:l[ií]mites operativos|operational limits)\b"),
     re.compile(r"(?i)\b(?:temporary_roots|ADR-011)\b")),
    ("autoridad",
     re.compile(r"(?i)\b(?:autoridad|authority)\b"),
     re.compile(r"(?i)\b(?:hitl_delegation|approver|execution\.md)\b")),
    ("organización/convenciones",
     re.compile(r"(?i)\b(?:organizaci[oó]n|convenciones|conventions organization)\b"),
     re.compile(r"(?i)\b(?:projectbrief|systemPatterns)\b")),
]


def test_pd6_restriction_to_canonical_place_table():
    text = _load(PSTART)

    rows = _table_or_list_lines(text)
    assert rows, (
        "PD-6 violada: el procedimiento no contiene la forma máquina-legible "
        "(tabla o lista canónica) de restricción → lugar canónico"
    )

    # Cada restricción declarada por la spec aparece con su lugar canónico.
    violating = []
    for label, restriction_re, place_re in P6_RESTRICTION_TABLE:
        found = any(
            restriction_re.search(line) and place_re.search(line) for _, line in rows
        )
        if not found:
            violating.append(label)
    assert not violating, (
        "PD-6 violada: la tabla restricción → lugar canónico no registra (o "
        f"inventa un lugar distinto para) las restricciones: {violating}"
    )


# ---------------------------------------------------------------------------
# PD-7 — inferible vs decisión del usuario; preguntar solo lo segundo y acotado;
# sin usuario, registra la duda.
# ---------------------------------------------------------------------------

P7_INFERIBLE = re.compile(
    r"(?i)\b(?:inferib\w*|inferable|autodetect\w*|detectable|autom[áa]tic\w*)\b"
)
P7_USER_DECIDES = re.compile(
    r"(?i)(?:\bdecid\w+\b[^.\n]{0,25}\b(?:usuario|user)\b)|"
    r"(?:\b(?:usuario|user)\b[^.\n]{0,25}\bdecid\w*\b)|"
    r"(?:decisi[oó]n del usuario|user decision|non-delegable|no delegable)"
)
P7_BOUNDED_QUESTIONS = re.compile(
    r"(?i)(?:\b(?:tres|three)\b[^.\n]{0,30}(?:preguntas|questions|pregunta\b))|"
    r"(?:tres o cuatro preguntas|three or four questions|bounded questions|"
    r"minimum questions|preguntas acotadas)"
)
P7_ACTIVE_CONTEXT = re.compile(r"\bactiveContext\.md\b")
P7_WITHOUT_USER = re.compile(
    r"(?i)\b(?:sin (?:usuario|user)|without (?:a )?user|no user|absent user|"
    r"sin usuario presente|without user present)\b"
)
P7_REGISTERS_DOUBT = re.compile(r"(?i)\b(?:registra|record|log|nota|declares|anota)\w*\b")


def test_pd7_inferible_vs_user_decision_bounded_questions():
    text = _load(PSTART)

    # La distinción inferible/decisión-del-usuario existe.
    assert P7_INFERIBLE.search(text), (
        "PD-7 violada: el procedimiento no marca lo inferible (autodetectable "
        "con evidencia objetiva)"
    )
    assert P7_USER_DECIDES.search(text), (
        "PD-7 violada: el procedimiento no marca las restricciones que son "
        "decisión del usuario (autoridad, privacidad)"
    )
    # Pregunta solo lo segundo y acotado (regla existente de bootstrap).
    assert P7_BOUNDED_QUESTIONS.search(text), (
        "PD-7 violada: el procedimiento no acota las preguntas al mínimo "
        "(referencia a la regla «tres o cuatro preguntas concretas» de bootstrap)"
    )
    # Sin usuario: registra la duda en activeContext.md en vez de preguntar.
    assert P7_ACTIVE_CONTEXT.search(text), (
        "PD-7 violada: el procedimiento no refiere activeContext.md como lugar "
        "de registro de la duda (INV-3)"
    )
    assert P7_WITHOUT_USER.search(text) and P7_REGISTERS_DOUBT.search(text), (
        "PD-7 violada: falta el mandato «sin usuario → registra la duda, no "
        "inventa» (INV-3)"
    )


# ---------------------------------------------------------------------------
# PD-8 — el arranque encadena hasta la preparación del primer encargo (camino
# de ejecución preparada, project-execution), no meramente «haber reconocido».
# ---------------------------------------------------------------------------

P8_FIRST_COMMISSION = re.compile(
    r"(?i)\b(?:primer(?:o|a)?\s+encargo|first\s+(?:delegation|assignment|package)"
    r"|primera delegaci[oó]n útil|first useful delegation)\b"
)
P8_DISPATCHABLE = re.compile(
    r"(?i)\b(?:despachab\w*|dispatchab\w*|prepared|preparado|preparada|preparar|prepare)\b"
)
P8_PREPARED_EXECUTION = re.compile(r"(?i)\b(?:prepared[- ]execution|ejecuci[oó]n preparada)\b")
P8_RECOGNITION = re.compile(r"(?i)\b(?:reconocimiento|recognition|reconocer|recognize)\b")
P8_RESTRICTIONS = re.compile(r"(?i)\b(?:restricci[oó]n\w*|restrictions?)\b")


def test_pd8_end_chain_first_commission():
    text = _load(PSTART)

    assert P8_FIRST_COMMISSION.search(text), (
        "PD-8 violada: el encadenado no termina en el primer encargo (fin "
        "observable: un encargo preparado y despachable)"
    )
    assert P8_DISPATCHABLE.search(text), (
        "PD-8 violada: no se declara el estado terminal preparado/despachable"
    )
    assert P8_PREPARED_EXECUTION.search(text) or re.search(
        r"project-execution\.md", text
    ), (
        "PD-8 violada: el encadenado no usa el camino de ejecución preparada "
        "(project-execution) para preparar el primer encargo"
    )
    # La cadena reconocer → registrar restricciones → preparar encargo.
    assert P8_RECOGNITION.search(text) and P8_RESTRICTIONS.search(text), (
        "PD-8 violada: falta el encadenado reconocimiento → registro de "
        "restricciones → primer encargo"
    )


# ---------------------------------------------------------------------------
# PD-9 — «sin ejecución activa → no resume» en el procedimiento y en el paso 1
# del flujo de SKILL.md (rama de arranque; no reduce lecturas: eso es 005-003).
# ---------------------------------------------------------------------------

P9_BRANCH = re.compile(
    r"(?i)(?:sin\s+ejecuci[oó]n\s+activa|without\s+(?:an\s+)?(?:active|running)\s+"
    r"execution|no\s+active\s+execution|no\s+resume\b|not\s+resume\b|"
    r"n?unca\s+(?:resume|reanud\w*)|never\s+resume|do\s+not\s+resume\b)"
)
P9_RESUME = re.compile(r"\bresume\b")


def _has_resume_branch(text: str) -> bool:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if P9_RESUME.search(line):
            neighborhood = "\n".join(lines[max(0, i - 3) : i + 4])
            if P9_BRANCH.search(neighborhood):
                return True
    return False


def test_pd9_no_resume_at_rest_in_procedure_and_skill_step1():
    # (a) El procedimiento enuncia la rama.
    text = _load(PSTART)
    assert re.search(r"resume", text), (
        "PD-9 violada: el procedimiento de arranque no distingue la reanudación "
        "(resume) de la iniciación desde reposo"
    )
    assert _has_resume_branch(text), (
        "PD-9 violada: el procedimiento no enuncia la rama «sin ejecución activa "
        "→ no resume» (resume queda para una ejecución activa)"
    )

    # (b) El paso 1 del flujo de SKILL.md declara la rama corregida.
    skill = _load(SKILL)
    window = "\n".join(line for _, line in _window(skill, 230, 300))
    assert P9_RESUME.search(window), (
        "PD-9 violada: el paso 1 del flujo de SKILL.md (≈:242-244) no menciona "
        "resume; no se puede corregir la prescripción ambigua"
    )
    window_hits = [
        (lineno, line)
        for lineno, line in _window(skill, 230, 300)
        if P9_RESUME.search(line)
    ]
    branch = any(
        P9_BRANCH.search("\n".join(
            [l for _, l in _window(skill, max(0, lineno - 4), lineno + 4)]
        ))
        for lineno, _ in window_hits
    )
    assert branch, (
        "PD-9 violada: el paso 1 del flujo de SKILL.md no enuncia la rama "
        "«sin ejecución activa → no resume» (prescripción ambigua :244 sin "
        "corregir para la rama de arranque)"
    )


# ---------------------------------------------------------------------------
# PD-10 (puntos T1) — los puntos de cableado que lista el plan (SKILL.md
# ≈:260-261 y ≈:451-452; continuity.md ≈:31-44) invocan el CLI instalado
# y nunca una ruta relativa al proyecto consumidor. Review-fix del dueño
# (hallazgos A1/A2, T6 `tests/test_005_006_t6_owner_reviewfix.py`): el
# marcador `$CDAD_INSTALL_ROOT` era justamente el DEFECTO A (variable de
# INSTALACIÓN, no de runtime) y DEJA de contar como ruta instalada. El único
# marcador válido es la ruta derivada del DIRECTORIO DE LA SKILL CARGADA,
# expresada explícitamente con `<skill-dir>` (oráculo declarado en el T6).
# Las líneas con ese marcador cuentan como corregidas/marcadas (spec PD-10).
#
# Extensión (hallazgo F1, review formal): la región de los PASOS 5-8 del flujo
# del orquestador en SKILL.md (ventana ≈:277-443, entre el punto de cableado
# :260-261 y la tabla de carga :443-460 que lista el plan) es de la misma
# familia fricción-2 (re-entry ≈:278: «the CLI is `scripts/cdad_result.py`»
# sin marcar). Regla de cierre: 0 ofensores SIN marcar en esa región.
# ---------------------------------------------------------------------------

PD10_CLI_RELATIVE = re.compile(
    r"(?i)\b(?:skills/cdad-cycle/)?scripts/?cdad_(?:packet|continuity|result)\.py\b"
)
PD10_SKILL_DIR_MARK = re.compile(r"<skill-dir>")


def _unmarked_install_relative_lines(text: str, lo: int, hi: int):
    offenders = []
    for lineno, line in _window(text, lo, hi):
        if not PD10_CLI_RELATIVE.search(line):
            continue
        if PD10_SKILL_DIR_MARK.search(line):
            continue
        offenders.append((lineno, line.strip()))
    return offenders


def test_pd10_installed_cli_paths_in_t1_wiring_points():
    # SKILL.md ≈:260-261 y ≈:451-452 (ventanas acotadas a los puntos que lista
    # el plan; toleran el corrimiento de las ediciones del paso 1 ≈:242-244 y
    # de la fila de tabla ≈:443-460, sin arrastrar puntos fuera del plan).
    skill = _load(SKILL)
    for label, lo, hi in (("SKILL.md:260-261", 250, 276), ("SKILL.md:451-452", 444, 464)):
        window_lines = [line for _, line in _window(skill, lo, hi)]
        assert any(PD10_CLI_RELATIVE.search(line) for line in window_lines), (
            f"PD-10 violada: el punto de cableado {label} ya no invoca al CLI "
            "(cdad_packet/cdad_continuity/cdad_result) — no se puede corregir "
            "su ruta ni verificar la ruta instalada"
        )
        offenders = _unmarked_install_relative_lines(skill, lo, hi)
        assert not offenders, (
            f"PD-10 violada en {label}: ruta del CLI relativa al proyecto "
            "consumidor (debe expresarse con la ruta derivada del directorio "
            f"de la skill cargada, marcador `<skill-dir>`): {offenders}"
        )

    # continuity.md ≈:31-44.
    continuity = _load(CONTINUITY)
    window_lines = [line for _, line in _window(continuity, 20, 60)]
    assert any(PD10_CLI_RELATIVE.search(line) for line in window_lines), (
        "PD-10 violada: continuity.md (≈:31-44) ya no invoca al CLI — no se "
        "puede verificar la ruta instalada"
    )
    offenders = _unmarked_install_relative_lines(continuity, 20, 60)
    assert not offenders, (
        "PD-10 violada en continuity.md:31-44: el ejemplo de invocación del CLI "
        f"no usa la ruta derivada del directorio de la skill cargada (marcador "
        f"explícito `<skill-dir>`; hallazgo A1/A2 del review-fix): {offenders}"
    )

    # Pasos 5-8 del flujo del orquestador en SKILL.md (≈:277-443; hallazgo F1
    # de la review formal: re-entry ≈:278). El punto debe seguir mencionando
    # al CLI para que la ruta corregida sea verificable; la corrección es
    # MARCAR la ruta como instalada, no eliminar la mención.
    flow_cli = [
        (lineno, line.strip())
        for lineno, line in _window(skill, 277, 443)
        if PD10_CLI_RELATIVE.search(line)
    ]
    assert flow_cli, (
        "PD-10 violada: la región de los Pasos 5-8 del flujo del orquestador "
        "(SKILL.md ≈:277-443) ya no menciona al CLI (cdad_packet/cdad_"
        "continuity/cdad_result) — no se puede verificar la ruta instalada "
        "del punto re-entry (≈:278); la corrección debe MARCAR la ruta como "
        "instalada, no eliminar la mención"
    )
    offenders = _unmarked_install_relative_lines(skill, 277, 443)
    assert not offenders, (
        "PD-10 violada en SKILL.md Pasos 5-8 (≈:277-443): ruta del CLI "
        "relativa al proyecto consumidor SIN marcar (debe expresarse con la "
        "ruta derivada del directorio de la skill cargada "
        "<skill-dir>/scripts/…; hallazgo F1 review formal y hallazgo A1/A2 "
        f"del review-fix del dueño): {offenders}"
    )


# ---------------------------------------------------------------------------
# PD-13 — dueño canónico del reconocimiento declarado (unificado por
# referencia): state-detection.md (cdad-cycle) declara la propiedad y apunta al
# arranque; cdad-epic/references/state-detection.md mantiene el vocabulario
# epic_stage; el procedimiento no re-declara la propiedad.
# ---------------------------------------------------------------------------

P13_OWNER_DECLARATION = re.compile(
    r"(?i)\b(?:due[ñn]o can[oó]nico|canonical owner|owning document|owner "
    r"document)\b"
)
P13_POINTER_TO_START = re.compile(r"project-start\.md")
P13_EPIC_STAGE = re.compile(r"\bepic_stage\b")


def test_pd13_canonical_owner_declared_and_not_redeclared():
    state_detection = _load(REFS / "state-detection.md")

    # Declaración de dueño canónico del reconocimiento (feature/Memory-Bank).
    assert P13_OWNER_DECLARATION.search(state_detection), (
        "PD-13 violada: cdad-cycle/references/state-detection.md no declara "
        "que es el dueño canónico del reconocimiento feature/Memory-Bank"
    )
    # Puntero al procedimiento de arranque (composición de ambos dueños).
    assert P13_POINTER_TO_START.search(state_detection), (
        "PD-13 violada: cdad-cycle/references/state-detection.md no apunta al "
        "procedimiento de arranque (references/project-start.md)"
    )

    # El vocabulario epic_stage sigue bajo el dueño canónico de etapa epic.
    epic_sd = _load(EPIC_STATE_DETECTION)
    assert P13_EPIC_STAGE.search(epic_sd), (
        "PD-13 violada: cdad-epic/references/state-detection.md ya no declara "
        "el vocabulario epic_stage (dueño canónico de etapa de epic)"
    )

    # El procedimiento no re-declara la propiedad: referencia, no absorbe.
    text = _load(PSTART)
    assert not P13_OWNER_DECLARATION.search(text), (
        "PD-13 violada: project-start.md re-declara la propiedad del "
        "reconocimiento; debe referenciar a los dueños canónicos (D4/PD-13)"
    )
    assert PD1_OWNER_REFS and re.search(r"state-detection", text), (
        "PD-13 violada: project-start.md no referencia a los dueños canónicos "
        "del reconocimiento"
    )


# ---------------------------------------------------------------------------
# PD-15 / INV-6 — no se traslada el prompt largo a una plantilla: bajo
# skills/cdad-cycle/assets/ no hay ninguna plantilla del arranque/prompt largo.
# ---------------------------------------------------------------------------

PD15_FORBIDDEN_ASSET_NAME = re.compile(r"(?i)project[-_ ]?start")


def test_pd15_no_long_prompt_template_under_assets():
    if not ASSETS.is_dir():
        return  # invariante STRICTU SENSU: si no existe el directorio, no hay plantilla
    offenders = []
    for asset in sorted(ASSETS.rglob("*")):
        if not asset.is_file():
            continue
        # El procedimiento (o el prompt largo) promovido a plantilla bajo
        # assets/ es lo prohibido; artefactos PRE-EXISTIENTES a esta feature
        # (p. ej. plantillas de estado ajenas al arranque) no están en el
        # alcance del invariante (la spec prohíbe AGREGAR una plantilla).
        if PD15_FORBIDDEN_ASSET_NAME.search(asset.name):
            offenders.append(str(asset.relative_to(REPO)))
            continue
        content = asset.read_text(encoding="utf-8", errors="replace")
        if re.search(r"project-start", content) and re.search(
            r"(?i)(?:plantilla|template|prompt|instrucci[oó]n breve|intake)", content
        ):
            offenders.append(str(asset.relative_to(REPO)))
    assert not offenders, (
        "PD-15/INV-6 violada: hay artefactos bajo skills/cdad-cycle/assets/ que "
        f"reproducen el prompt largo o el procedimiento como plantilla: "
        f"{offenders}; el procedimiento debe ser referencia, no plantilla"
    )


# ---------------------------------------------------------------------------
# INV-1 — un solo procedimiento corto, por referencia: los artefactos
# estructurales de los dueños (algoritmo de detección, política/autoridad) no
# reaparecen en project-start.md.
# ---------------------------------------------------------------------------

def test_inv1_procedure_references_owners_without_copying_their_structure():
    if not PSTART.is_file():
        pytest.fail(f"INV-1 violada: el procedimiento corto no existe: {PSTART}")
    start_text = PSTART.read_text(encoding="utf-8")
    start_artifacts = _structural_artifacts(start_text)
    missing = [str(p) for p in OWNER_FILES if not p.is_file()]
    assert not missing, (
        f"INV-1 no evaluable: falta el dueño canónico declarado por la spec: "
        f"{missing} (documento requerido)"
    )

    copied = {}
    for owner in OWNER_FILES:
        owner_artifacts = _structural_artifacts(owner.read_text(encoding="utf-8"))
        shared = sorted(
            f"«{a}»" for a in start_artifacts & owner_artifacts
        )
        if shared:
            copied[str(owner.relative_to(REPO))] = shared
    assert not copied, (
        "INV-1 violada: project-start.md copia artefactos estructurales de los "
        f"dueños canónicos (segunda definición de las reglas): {copied}; debe "
        "referenciar, nunca copiar el algoritmo de detección ni la "
        "política/autoridad"
    )


# ---------------------------------------------------------------------------
# INV-2 — preservación: nunca pisa documentación, planes ni convenciones
# existentes (bootstrap.md:121-125; project-execution.md:84-97).
# ---------------------------------------------------------------------------

def test_inv2_never_overwrites_existing_docs_plans_conventions():
    text = _load(PSTART)
    lines = text.splitlines()

    paired_override = False
    for line in lines:
        if re.search(
            r"(?i)\b(?:never|nunca|do not|don't|no\s+pisa|no\s+pisar|"
            r"not\s+overwrite|without\s+overwriting|preserv\w+|no\s+clobber)\b",
            line,
        ) and re.search(
            r"(?i)\b(?:documentaci[oó]n|documentation|plane?\b|plan\b|"
            r"conventions?|conventions|convenciones|nomenclatur\w*|"
            r"[eé]picas?|epics?|features?|memory bank)\b",
            line,
        ):
            paired_override = True
            break
    assert paired_override, (
        "INV-2 violada: el procedimiento no enuncia el mandato de nunca pisar "
        "documentación/planes/convenciones existentes"
    )
    # Deja los dueños de la regla referenciados (sin re-abolver la regla).
    assert re.search(r"bootstrap\.md", text) and re.search(
        r"project-execution\.md", text
    ), (
        "INV-2 violada: el mandato de preservación no referencia a los dueños "
        "(bootstrap anti-patrones; project-execution no-clobber)"
    )


# ---------------------------------------------------------------------------
# INV-3 — solo el usuario decide lo no inferible (autoridad; edición de
# privacidad; alcance); sin usuario, registra la duda — nunca inventa.
# ---------------------------------------------------------------------------

def test_inv3_only_user_decides_non_inferable():
    text = _load(PSTART)

    # Autoridad y privacidad son decisión del usuario (no degradable).
    authority_user = re.search(
        r"(?i)\bautoridad\b[^.\n]{0,80}\b(?:usuario|user|due[ñn]o)\b"
        r"|\b(?:usuario|user|due[ñn]o)\b[^.\n]{0,80}\bautoridad\b",
        text,
    )
    privacy_user = re.search(
        r"(?i)\bprivacidad\b[^.\n]{0,80}\b(?:usuario|user|propon\w*|decid\w*)\b"
        r"|\bprivacidad\b[^.\n]{0,80}[^.\n]{0,80}(?:decid\w*|decisi[oó]n)",
        text,
    )
    assert authority_user, (
        "INV-3 violada: la autoridad no está reservada como decisión del "
        "usuario (no delegable); el arranque no puede inferirla"
    )
    assert privacy_user, (
        "INV-3 violada: la edición de privacidad (private_paths) no está "
        "marcada como decisión reservada (inferir y proponer, no escribir sin "
        "decisión)"
    )
    # Sin usuario: registra la duda (nunca inventa).
    assert P7_ACTIVE_CONTEXT.search(text) and P7_WITHOUT_USER.search(text), (
        "INV-3 violada: falta «sin usuario → registra la duda en "
        "activeContext.md»"
    )
    assert P7_REGISTERS_DOUBT.search(text), (
        "INV-3 violada: no declara cómo se registra la duda (activa) cuando no "
        "hay quién decida"
    )


# ---------------------------------------------------------------------------
# INV-4 — nunca resume sin ejecución activa, nunca fabrica autoridad y nunca
# cambia de versión en silencio.
# ---------------------------------------------------------------------------

def test_inv4_never_resume_without_active_no_fabrication_no_silent_version():
    text = _load(PSTART)
    lines = text.splitlines()

    # (i) Rama sin-ejecución-activa → no resume (ya verificada por PD-9, aquí
    # bajo la forma del invariante).
    assert _has_resume_branch(text), (
        "INV-4 violada: falta el enunciado de que el arranque nunca ejecuta "
        "resume sin ejecución activa"
    )

    # (ii) Nunca fabrica autoridad (inventar/fabricar prohibido).
    found_fabrication = False
    for line in lines:
        if re.search(
            r"(?i)\b(?:no|not|never|nunca|jamás|do not)\b[^.\n]{0,40}"
            r"\b(?:fabricat\w*|invent\w*|falsif\w*|sustituir|supplant)\w*",
            line,
        ) and re.search(
            r"(?i)\b(?:autoridad|authority|aprobaci[oó]n|approval|"
            r"versi[oó]n|version)\b",
            line,
        ):
            found_fabrication = True
            break
    assert found_fabrication, (
        "INV-4 violada: el procedimiento no enuncia la prohibición de fabricar "
        "autoridad / cambiar de versión en silencio"
    )

    # (iii) Cambio de versión en silencio prohibido (mencionado explícitamente).
    assert re.search(
        r"(?i)\bversi[oó]n\b|\bversion\b", text
    ), "INV-4 violada: el procedimiento no trata el cambio de versión"
    version_rule = [
        line for line in lines
        if re.search(r"(?i)\bversi[oó]n\b|\bversion\b", line) and re.search(
            r"(?i)\b(?:silencio|silently|silent|no|not|never|nunca|sin)\b", line
        )
    ]
    assert version_rule, (
        "INV-4 violada: el procedimiento no declara la regla «nunca cambia de "
        "versión en silencio»"
    )
