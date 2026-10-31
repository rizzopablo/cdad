#!/usr/bin/env python3
"""RED de T3/T5/T8 — 010-002-documentary-role-integration.

Contrato: ``docs/specs/010-002-documentary-role-integration/spec.md`` v4
(sha256 ``0d630c49…81abc``). Cubre las promesas A, B, C, D, E y F:

===================  ====================================================
Grupo                Postcondiciones
===================  ====================================================
``TestEngagement``   PC-01, PC-02, PC-03
``TestOdooApplicability``  PC-04, PC-05
``TestDispatchDoctrine``   PC-09 (y la mitad documental de PC-08)
``TestDistribution``       PC-11, PC-12.a
``TestAgentBinding``       PC-06, PC-07, PC-08, INV-04
``TestAgentBindingWriteAheadFinalization``  PC-08 (write-ahead, P-2/N2)
``TestRequestSchema``      PC-10
===================  ====================================================

T8 (review) añade dos controles de cierre a este módulo:

- **B1** — la vía nativa de los dos adaptadores fuente y del orquestador
  generado de cada runtime no promete un rechazo mecánico de la variante
  ausente (D4/PC-09). El detector decide la polaridad de la cláusula: una
  negación de la sustitución silenciosa no absuelve la promesa mecánica.
- **B2** — el delta Odoo de reviewer, implementer y test-writer, en su fuente y
  en los seis agentes generados, subordina la batería de addon al producto o al
  diff en la propia sección; la matriz de aplicabilidad de otra sección no
  cuenta.

Diseño del oráculo
------------------
Cada verificación se deriva del **contrato** (§2 D1–D5, §3 procedimiento, §4
postcondiciones) y de las superficies que el contrato nombra en §10. Los
documentos bajo prueba no se leyeron para construir el oráculo: las rutas, los
campos, los directorios de addon, las declaraciones por rol y las reglas de
selección provienen de la spec y del AUDIT aprobado. Presencia textual no es
suficiencia semántica (PC-13, reservada a T8): estos tests son estructurales.

Grupos de T5 (``TestAgentBinding`` y ``TestRequestSchema``)
-----------------------------------------------------------
El destinatario se deriva del rol y del ``stack`` vigente (D3). Las dos vías
públicas de publicación —``prepare`` ordinario y ``prepare --replace-packet``—
son **garantía por construcción**: se verifica el valor publicado y su
transición (reemplazo de histórico sin ``agent`` y reemplazo tras cambiar el
``stack``), nunca una rama de rechazo de agente inyectado que la interfaz no
permite alcanzar (spec §2 D3; AUDIT §5). El contraste **estático** de rol se
observa en ``validate-request``/``render``/``validate-packet``; no consulta el
``stack``. El contraste **contextual** se observa al registrar un intento
nuevo con agente declarado: un agente del mismo rol pero de otro ``stack`` se
rechaza nombrando rol, stack y agente esperado. La recepción, la repetición
idéntica y la finalización válida del write-ahead no reaplican ese contraste
(P-2/N2). El histórico admitido sin ``execution_context`` ni ``agent`` puede
registrar un intento nuevo sin contraste contextual y sin derivar ni sustituir
un agente (P-3/N6). El esquema se evalúa con un motor real de JSON Schema
(``jsonschema``); describe **forma** y no sustituye las comprobaciones del CLI.

Reglas de oráculo aplicadas en T5 (AUDIT §10):
``R2`` el caso contextual usa un agente del **mismo rol** con otro ``stack``
(no un agente de otro rol, que el contraste estático preemptaría); ``R3`` la
exclusión de ``agent`` del render compara dos requests **válidos** sin
contexto declarado; ``R5`` el reemplazo tras cambio de ``stack`` hace que
predecesor y esperado **difieran**; ``R6`` el esquema se valida sobre
instancias reales con ``iter_errors``; ``R7`` la repetición y el write-ahead
declaran el ``stack`` antes y después del cambio.

Reglas de oráculo aplicadas (AUDIT §10):

- R1: se localiza la región de aplicabilidad **por rol y archivo** y se exige
  el **par** exención documental + obligación de addon; para PC-09 se exige la
  **ausencia** de «otro valor → genérico» en todas las superficies, no solo la
  presencia de la palabra sufijo.
- R8: ``TestDistribution`` genera en una **copia descartable** del producto y
  nunca lee ``build/staging`` del checkout como oráculo del contenido corregido.
- R11: PC-03 es una obligación **procedimental**; el test verifica el
  procedimiento y la igualdad de alcances ya medida por ``test_packet_prepare``
  (defaults del implementer, del test-writer y de los roles read-only), no un
  rechazo mecánico inexistente.

Aislamiento (``tests/conftest.py``)
-----------------------------------
Se usa la raíz descartable por test del conftest (``HOME``/XDG/temporales) y se
retiran los overrides heredados. La instalación usa ``CDAD_INSTALL_ROOT``
propio y ``CDAD_SKILL_EXTRA_DIRS=""``; el HOME real no se toca. La única
variable que este módulo fija **en el proceso hijo** es
``CDAD_OPENCODE_AGENTS_DIR``, apuntada al destino **instalado** del propio
``CDAD_INSTALL_ROOT`` para resolver el agente en la superficie instalada.

Controles ya verdes (no se presentan como RED)
----------------------------------------------
- PC-02: fronteras de los seis roles en ``sources/roles/*.md`` y conjunto de
  once agentes por runtime sin variante documental (conservación).
- PC-03: defaults de ``prepare`` por rol (control de ``test_packet_prepare``).
- PC-11: ``make agents`` determinista y promovidos == staging.
- PC-12.a: el instalador publica agentes y skills con bytes de origen.

El RED de T3 lo producen las obligaciones **ausentes**: el procedimiento
documental y las declaraciones que lo acompañan, la matriz Odoo por rol, la
doctrina sin «otro valor → genérico», el rechazo mecánico/procedimental de la
variante ausente, y la presencia de esas superficies en los artefactos
distribuidos.

Límites honestos
----------------
Un verde aquí **no** acredita fidelidad semántica, suficiencia de una exclusión,
ni conducta efectiva de modelos. Este módulo no es un sandbox.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

try:  # Motor real de JSON Schema (AUDIT §10 R6). Su ausencia es bloqueo de
    # entorno, no defecto del producto: el test se declara omitido con causa.
    import jsonschema
except ImportError:  # pragma: no cover - entorno sin el motor
    jsonschema = None

from tests.product_staging import run_scoped_mkdtemp
from tests.test_003_002_t1_receive import STAGED_PARTS, EstablishedProjectCase
from tests.test_004_001_t6 import REQUIRED_REAL_DESTINATIONS
from tests.test_006_004_u3_principle_single_source import (
    disposable_product,
    read_document,
    relative,
)
from tests.test_006_005_u6fix5_write_ahead import (
    FAKE_VERSION as U65_FAKE_VERSION,
    ROW_MODEL as U65_ROW_MODEL,
    U65WriteAheadCase,
)
from tests.test_010_001_documentary_contracts import (
    AGENT_NAMES,
    INSTALLED_AGENTS_DIRS,
    NEGATION,
    PROMOTED_DIRS,
    RUNTIMES,
    STAGING_AGENTS,
    assert_concepts,
    fold,
    missing_in_best_window,
    role_of_agent,
)
from tests.test_packet_prepare import (
    PACKET_CLI,
    PrepareProject,
    run_cli_bytes,
    run_prepare,
)
from tests.test_role_packet_render import parse_packet


REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Superficies declaradas por el contrato (spec §10; AUDIT §4.1). Rutas del
# repositorio, ninguna ruta del host.
# ---------------------------------------------------------------------------

ROLES = ("architect", "test-writer", "implementer", "reviewer", "orchestrator", "scribe")
PRODUCER_ROLES = ("architect", "test-writer", "implementer")
REVIEW_ROLES = ("reviewer", "orchestrator", "scribe")

ROLE_SOURCES = {
    role: REPO_ROOT / "sources" / "roles" / f"{role}.md" for role in ROLES
}

HANDOFF = REPO_ROOT / "skills" / "cdad-cycle" / "references" / "handoff-prompts.md"
SUBAGENT = REPO_ROOT / "skills" / "cdad-cycle" / "references" / "sub-agent-strategies.md"
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"

ADAPTERS = {
    "opencode": REPO_ROOT / "sources" / "agents" / "adapters" / "opencode.md",
    "claude-code": REPO_ROOT / "sources" / "agents" / "adapters" / "claude-code.md",
}

ODOO_SKILLS = (
    "odoo-architect",
    "odoo-test-writer",
    "odoo-expert",
    "odoo-reviewer",
    "odoo-make-env",
)
ODOO_SKILL_FILES = {
    name: REPO_ROOT / "skills" / name / "SKILL.md" for name in ODOO_SKILLS
}

# Inventario acotado de T4 (spec §7 y plan T4): candidatos delimitados.
INVENTORY_REFERENCES = (
    REPO_ROOT / "skills" / "odoo-expert" / "references" / "evidence-and-quality.md",
    REPO_ROOT / "skills" / "odoo-make-env" / "references" / "run-budget-protocol.md",
    REPO_ROOT / "skills" / "odoo-make-env" / "references" / "odoo-sh.md",
    REPO_ROOT / "skills" / "odoo-make-env" / "references" / "odoo-19-traps.md",
)

# Superficies donde el contrato exige la frontera del addon (PC-04): las
# fuentes de rol, las skills Odoo y las referencias inventariadas.
BOUNDARY_SURFACES = (
    tuple(ROLE_SOURCES.items())
    + tuple((name, path) for name, path in ODOO_SKILL_FILES.items())
    + tuple((relative(path), path) for path in INVENTORY_REFERENCES)
)

# Superficies de la doctrina de selección (D4/PC-09).
NATIVE_SURFACES = (
    ("sources/roles/orchestrator.md", ROLE_SOURCES["orchestrator"]),
    ("skills/cdad-cycle/SKILL.md", SKILL_MD),
    ("skills/cdad-cycle/references/sub-agent-strategies.md", SUBAGENT),
)
ADAPTER_SURFACES = tuple(ADAPTERS.items())
SELECTION_SURFACES = NATIVE_SURFACES + ADAPTER_SURFACES

# B1 (review T8): la doctrina de la vía nativa también se publica en los
# adaptadores fuente y en el agente orquestador generado de cada runtime.
ADAPTER_NATIVE_SURFACES = ADAPTER_SURFACES + (
    ("agents/cdad-orchestrator.md", REPO_ROOT / "agents" / "cdad-orchestrator.md"),
    (
        "agents/claude-code/cdad-orchestrator.md",
        REPO_ROOT / "agents" / "claude-code" / "cdad-orchestrator.md",
    ),
)

# B2 (review T8): los seis agentes de rol con delta Odoo (tres roles por
# runtime) publican la sección que debe quedar condicionada. Observarlos evita
# aceptar la corrección solo en la fuente y dejar el agente generado viejo.
PROMOTED_ODOO_AGENTS = tuple(
    (f"agents/{prefix}cdad-{role}-odoo.md", path, role)
    for role in ("reviewer", "implementer", "test-writer")
    for prefix, path in (
        ("", REPO_ROOT / "agents" / f"cdad-{role}-odoo.md"),
        (
            "claude-code/",
            REPO_ROOT / "agents" / "claude-code" / f"cdad-{role}-odoo.md",
        ),
    )
)

# Superficies de la norma documental que PC-12.a distribuye corregidas.
CORRECTED_CDAD_SURFACES = (
    "SKILL.md",
    "references/handoff-prompts.md",
    "references/sub-agent-strategies.md",
)

# Raíces de skills que el instalador publica: se derivan de los destinos
# declarados por los tests del instalador (no se inventan rutas).
SKILL_ROOTS = tuple(
    destination[: -len("/cdad-cycle")]
    if destination.endswith("/skills/cdad-cycle")
    else destination
    for destination in REQUIRED_REAL_DESTINATIONS
    if destination.endswith("/skills/cdad-cycle") or destination.endswith("/skills")
)

MANIFEST = Path("build") / "staging" / "manifest.json"

# ---------------------------------------------------------------------------
# Anclas y ventanas
# ---------------------------------------------------------------------------

DOC_ANCHORS = ("documental", "documentary")
ODOO_ANCHORS = ("addon", "aplicabilidad", "applicability", "odoo")
SELECTION_ANCHORS = ("stack",)

# Ventana para la matriz por rol (bloque compacto dentro de una fuente).
NEAR = 1800
# Ventana para doctrina y procedimiento (secciones más amplias).
NEAR_WIDE = 2600

# ---------------------------------------------------------------------------
# Helpers estructurales (locales; los helpers de concepto se reutilizan de
# ``tests/test_010_001_documentary_contracts.py`` — una sola definición).
# ---------------------------------------------------------------------------

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_BLANK = re.compile(r"\n\s*\n")


def markdown_sections(text: str, max_level: int = 2) -> list[tuple[str, str]]:
    """Secciones de nivel <= ``max_level``; las profundas quedan en el cuerpo.

    Devuelve ``(encabezado, cuerpo)``. Un archivo sin encabezados devuelve una
    sola sección con encabezado vacío, de modo que la región es el archivo
    (los roles no usan encabezados markdown).
    """
    sections: list[tuple[str, str]] = []
    heading = ""
    body: list[str] = []
    for line in text.splitlines():
        match = _HEADING.match(line)
        if match and len(match.group(1)) <= max_level:
            if heading or body:
                sections.append((heading, "\n".join(body)))
            heading = line
            body = []
        else:
            body.append(line)
    if heading or body:
        sections.append((heading, "\n".join(body)))
    if not sections:
        sections.append(("", text))
    return sections


def documentary_region(text: str, anchors: tuple[str, ...] = DOC_ANCHORS) -> str:
    """Región de la que habla el contrato: secciones (o párrafos) documentales.

    Localiza por estructura, no por una palabra suelta: devuelve el texto de
    las secciones cuyo encabezado o cuerpo menciona el caso documental. Si el
    archivo no tiene encabezados, agrupa los párrafos que lo mencionan.
    """
    folded_anchors = tuple(fold(anchor) for anchor in anchors)
    matching = [
        heading + "\n" + body
        for heading, body in markdown_sections(text)
        if any(anchor in fold(heading + "\n" + body) for anchor in folded_anchors)
    ]
    if matching:
        return "\n\n".join(matching)
    paragraphs = [
        paragraph
        for paragraph in _BLANK.split(text)
        if any(anchor in fold(paragraph) for anchor in folded_anchors)
    ]
    return "\n\n".join(paragraphs)


def _positions(folded_text: str, alternatives: tuple[str, ...]) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for alternative in alternatives:
        needle = fold(alternative)
        start = 0
        while True:
            index = folded_text.find(needle, start)
            if index < 0:
                break
            spans.append((index, index + len(needle)))
            start = index + 1
    return spans


# ``fold`` colapsa espacios y recorta el final, así que la lista NEGATION del
# precedente pierde el espacio final y «ni » se vuelve «ni», que aparece dentro
# de «mechanical» o «definition». Para los detectores de este módulo la negación
# se comprueba con límites de palabra.
_NEGATION_RE = re.compile(
    r"(?<![a-z])(no|not|never|nunca|sin|tampoco|neither|nor|ni)(?![a-z])"
)


def negation_in(window: str) -> bool:
    """Negación real en la ventana (límites de palabra, no subcadena)."""
    return _NEGATION_RE.search(window) is not None


def concept_is_negated(
    text: str, concept: tuple[str, ...], radius: int = 500
) -> bool:
    """El concepto aparece en forma negativa dentro de la ventana."""
    folded = fold(text)
    return any(
        negation_in(folded[max(0, start - radius) : end + radius])
        for start, end in _positions(folded, concept)
    )


def document_is_negated_in_documentary_paragraph(
    text: str, objects: tuple[str, ...]
) -> bool:
    """Párrafo documental que niega una obligación sobre ``objects``.

    Exención documental: la negación tiene que estar **acotada** al caso
    documental y nombrar el objeto de la obligación que se exime. Un «no exige
    addon» sin acotar contradiría la columna addon de la misma matriz.
    """
    folded_objects = tuple(fold(item) for item in objects)
    for paragraph in _BLANK.split(text):
        folded = fold(paragraph)
        if not any(anchor in folded for anchor in (fold("documental"), "documentary")):
            continue
        if not any(item in folded for item in folded_objects):
            continue
        if negation_in(folded):
            return True
    return False


# ---------------------------------------------------------------------------
# PC-01 — declaraciones del encargo documental mediante los campos existentes.
# ---------------------------------------------------------------------------

DECLARATIONS = (
    ("objetivo y promesas", ("objetivo", "objective")),
    ("producto esperado", ("producto esperado", "expected output", "expected_output")),
    ("fuentes autorizadas", ("fuentes", "sources", "insumos", "inputs")),
    ("producto editable", ("alcance editable", "editable scope", "alcance", "scope")),
    ("verificadores protegidos", ("verificador", "verifiers", "verifier", "invariants")),
    ("evidencia", ("evidencia", "evidence")),
    ("límites", ("limite", "limit", "limits")),
)

EXISTING_FIELDS = (
    ("campo `contract`", ("contract", "contrato")),
    ("campo `objective`", ("objective",)),
    ("campo `expected_output`", ("expected_output", "expected output")),
    ("campo `inputs`", ("inputs",)),
    ("campo `read_scope`", ("read_scope", "read scope")),
    ("campo `write_scope`", ("write_scope", "write scope")),
    ("campo `invariants`", ("invariants", "invariantes")),
    ("campo `evidence_required`", ("evidence_required", "evidence required")),
)

NEW_SELECTOR_CONCEPTS = (
    "selector nuevo",
    "nuevo selector",
    "new selector",
    "selector paralelo",
    "parallel selector",
    "stack documental",
    "documentary stack",
    "campo nuevo",
    "new field",
)

# ---------------------------------------------------------------------------
# PC-02 — fronteras de los seis roles (conservación estructural).
# ---------------------------------------------------------------------------

ROLE_BOUNDARIES = {
    "orchestrator": (
        ("no ejecuta trabajo de rol inline", ("no ejecuta", "does not execute", "no realiza")),
        ("trabajo inline", ("inline", "trabajo de rol", "role work")),
    ),
    "architect": (
        ("no aprueba su propio texto", ("no aprueba", "does not approve")),
        ("propio", ("propio", "own")),
    ),
    "test-writer": (
        (
            "no deriva el oráculo del producto",
            ("no deriva", "does not derive", "no deduce", "never from", "nunca deriva"),
        ),
        ("producto producido / verificador", ("producido", "produced", "producto", "verifier")),
    ),
    "implementer": (
        ("no modifica tests", ("no modifica", "does not modify", "no edita")),
        ("tests", ("tests", "pruebas")),
    ),
    "reviewer": (
        ("read-only", ("read-only", "solo lectura", "read only")),
        ("contrasta", ("contrasta", "contrasts", "compare", "compara")),
    ),
    "scribe": (
        ("memory bank", ("memory bank",)),
        ("borrador", ("borrador", "draft")),
    ),
}

# ---------------------------------------------------------------------------
# PC-04 / PC-05 — matriz Odoo por rol (spec §4, tablas de PC-04 y PC-05).
#
# ``exemption_objects``: lo que el caso documental NO exige (negado en un
# párrafo documental). ``obligation``: lo que el caso addon SÍ exige.
# ``mixed``: la fila mixta.
# ---------------------------------------------------------------------------

MATRIX = {
    "architect": {
        "exemption_objects": ("inventario", "inventory", "entorno", "environment", "runner", "addon"),
        "exemption_extra": (("dominio y mapeo", ("dominio", "domain", "mapeo", "mapping")),),
        "obligation": (
            ("inventario", ("inventario", "inventory")),
            ("core/OCA", ("core", "oca")),
            ("antes de modificar", ("antes", "before")),
            ("modificar el addon", ("modific", "modify", "change")),
        ),
        "mixed": (
            ("mixto", ("mixto", "mixed")),
            ("ambas familias", ("ambas", "both")),
            ("familias", ("familias", "families", "obligaciones", "obligations")),
        ),
    },
    "test-writer": {
        "exemption_objects": ("transactioncase", "@tagged", "tagged", "runner", "addon"),
        "exemption_extra": (
            ("aislamiento", ("aislamiento", "isolation")),
            ("oráculo no derivado", ("oraculo", "oracle")),
        ),
        "obligation": (
            ("TransactionCase", ("transactioncase",)),
            ("@tagged", ("@tagged", "tagged")),
            ("fixtures", ("fixtures", "fixture")),
            ("runner Odoo", ("runner",)),
        ),
        "mixed": (
            ("mixto", ("mixto", "mixed")),
            ("separa regímenes", ("separa", "separates", "separate")),
            ("regímenes", ("regimen", "regime")),
        ),
    },
    "implementer": {
        "exemption_objects": ("pruebas", "tests", "lint", "instalacion", "install", "addon"),
        "exemption_extra": (("addon no modificado", ("no modificado", "unmodified")),),
        "obligation": (
            ("lint", ("lint",)),
            ("OCA", ("oca",)),
            ("instalación limpia", ("instalacion limpia", "instalación limpia", "clean install")),
            ("pruebas", ("pruebas", "tests")),
        ),
        "mixed": (
            ("mixto", ("mixto", "mixed")),
            ("productos respectivos", ("respectiv", "respective", "cada", "each")),
        ),
    },
    "reviewer": {
        "exemption_objects": ("bateria", "battery", "transactioncase", "addon test", "test de addon", "addon"),
        "exemption_extra": (("diff", ("diff",)),),
        "obligation": (
            ("diff real", ("diff",)),
            ("instalación limpia", ("instalacion limpia", "instalación limpia", "clean install")),
            ("lint", ("lint",)),
            ("OCA", ("oca",)),
        ),
        "mixed": (
            ("mixto", ("mixto", "mixed")),
            ("ambas evidencias", ("ambas", "both")),
            ("evidencia", ("evidencia", "evidence")),
        ),
    },
    "orchestrator": {
        "exemption_objects": ("inline", "trabajo de rol", "role work"),
        "exemption_extra": (("gate/evidencia", ("gate", "evidencia", "evidence")),),
        "obligation": (
            ("evidencia", ("evidencia", "evidence")),
            ("addon", ("addon",)),
            ("diff real", ("diff",)),
            ("sin trabajo inline", ("inline",)),
            ("negación", NEGATION),
        ),
        "mixed": (
            ("mixto", ("mixto", "mixed")),
            ("ambas familias", ("ambas", "both")),
            ("familias", ("familias", "families", "obligaciones", "obligations")),
        ),
    },
    "scribe": {
        "exemption_objects": ("produccion", "production", "verificacion", "verification", "ejecuta", "execute", "addon"),
        "exemption_extra": (("memory bank", ("memory bank",)),),
        "obligation": (
            ("addon", ("addon",)),
            ("memory bank", ("memory bank",)),
            ("no ejecuta", ("no ejecuta", "does not execute", "not execute")),
            ("no sustituye", ("sustitu", "substitut")),
        ),
        "mixed": (
            ("mixto", ("mixto", "mixed")),
            ("ambas clases", ("ambas", "both", "dos clases", "both classes")),
            ("evidencia", ("evidencia", "evidence")),
        ),
    },
}

# El diff real prevalece sobre la etiqueta (PC-05, reviewer y orquestador).
DIFF_PREVALENCE = (
    ("diff", ("diff",)),
    ("prevalece", ("prevalece", "prevails", "precedence", "takes precedence")),
)

HIDDEN_ADDON_UNDER_LABEL = (
    ("oculto bajo etiqueta", ("ocult", "hidden")),
    ("etiqueta", ("etiqueta", "label")),
    ("bloquea la aceptación", ("bloquea", "blocks", "impide", "prevent")),
)

RETROACTIVE_DENIED = (
    ("retroactivo", ("retroactiv",)),
    ("negación", NEGATION),
)

# PC-04: frontera del addon (D2).
ADDON_BOUNDARY = (
    ("models/", ("models/", "models ", "`models`")),
    ("views/", ("views/", "views ", "`views`")),
    ("controllers/", ("controllers/", "controllers ", "`controllers`")),
    ("wizards/", ("wizards/", "wizard/", "wizards ", "wizard ")),
    ("security/", ("security/", "security ", "`security`")),
    ("data/", ("data/", "data ", "`data`")),
    ("static/src/", ("static/src",)),
    ("__manifest__.py", ("__manifest__.py",)),
    ("readme/", ("readme/", "readme ", "`readme`")),
    ("static/description/", ("static/description",)),
    ("README.rst", ("readme.rst",)),
    ("doc/", ("doc/", "doc ", "`doc`")),
)

BOUNDARY_CLASSIFICATION = (
    ("producto documental", ("producto documental", "documentary product")),
    ("salvo contrato", ("salvo", "unless", "excepto", "except")),
)

BOUNDARY_LIMITS = (
    ("no cambia la clasificación de rutas", ("clasificacion de rutas", "path classification", "clasificacion", "classification")),
    ("permisos y alcances", ("permisos", "permissions")),
    ("alcances", ("alcances", "scopes")),
    ("negación", NEGATION),
)

BOUNDARY_LOCATION_ALONE = (
    ("ubicación dentro del módulo", ("por si sola", "alone", "per se", "ubicacion", "location")),
    ("no exige batería de addon", ("bateria", "battery", "test de addon", "addon test", "transactioncase")),
    ("negación", NEGATION),
)

# PC-04: el verificador documental no es un test de addon (D2).
VERIFIER_NOT_ADDON = (
    ("verificador documental", ("verificador", "verifier")),
    ("documental", DOC_ANCHORS),
    ("no exige batería de addon", ("transactioncase", "@tagged", "runner", "bateria", "battery")),
    ("negación", NEGATION),
    ("por dominio del proyecto", ("dominio del proyecto", "project domain", "solo por", "just because", "por el dominio", "because of the domain")),
)

ADDON_TEST_ATTRIBUTION = (
    ("tests de addon", ("tests de addon", "addon tests", "addon test")),
    ("producto de addon", ("producto de addon", "addon product")),
    ("aunque se escriba bajo tests/", ("aunque", "even though", "even if", "even when")),
    ("tests/", ("tests/", "bajo tests", "under tests")),
)

# ---------------------------------------------------------------------------
# B2 — los deltas Odoo de rol se condicionan al producto o al diff (review T8).
#
# PC-04/PC-05: la batería de addon rige para el trabajo de addon y no para el
# documental puro. La matriz de aplicabilidad vive en otra sección; su sola
# presencia no condiciona el delta, y la cercanía de «documentary» tampoco.
# La condición tiene que estar en la sección `cdad-section:odoo` y nombrar
# producto/diff/cambio + addon mediante una regla de aplicabilidad.
# ---------------------------------------------------------------------------

ODOO_SECTION_OPEN = re.compile(r"<!--\s*cdad-section:odoo\s*-->")
ODOO_SECTION_CLOSE = "<!-- /cdad-section -->"

ROLE_BATTERY = {
    "reviewer": ("make test-clean", "oca-checks", "pylint-odoo"),
    "implementer": ("make test", "clean lint", "pylint-odoo", "oca-checks"),
    "test-writer": ("@tagged", "make test-one", "make test"),
}

_CONDITION_MARKER = re.compile(
    r"(?<![a-z])(if|when|whenever|only|provided|subject|si|solo|cuando|"
    r"siempre|caso|condicion|conditional|applies|aplica)(?![a-z])"
)
_CONDITION_SUBJECT = re.compile(
    r"(?<![a-z])(product|products|producto|productos|diff|diffs|change|changes|"
    r"cambio|cambios|engagement|engagements|encargo|encargos|deliverable|"
    r"deliverables|entregable|entregables|work item|work items)(?![a-z])"
)
_CONDITION_ADDON = re.compile(r"addons?|odoo modules?|modulos? odoo")
_CONDITION_ACTION = re.compile(
    r"touch|modific|verif|affect|concern|involve|include|toca|modifica|"
    r"verifica|afecta|involucra|incluye|appl|aplic"
)
_CONDITION_COPULA = re.compile(
    r"(?<![a-z])(?:is|are|was|were|es|son|sea|sean)(?![a-z])"
)


def odoo_section(text: str) -> str:
    """Bloque `<!-- cdad-section:odoo -->` … `<!-- /cdad-section -->`."""
    match = ODOO_SECTION_OPEN.search(text)
    if match is None:
        return ""
    end = text.find(ODOO_SECTION_CLOSE, match.end())
    if end < 0:
        return ""
    return text[match.end() : end].strip()


def odoo_stack_delta_region(text: str) -> str:
    """Cuerpo del encabezado «Odoo stack delta» de un agente generado."""
    lines = text.splitlines()
    start = None
    level: int | None = None
    for index, line in enumerate(lines):
        heading = _HEADING.match(line)
        if not heading:
            continue
        title = fold(heading.group(2))
        if "odoo" in title and ("delta" in title or "stack" in title):
            start, level = index + 1, len(heading.group(1))
            break
    if start is None:
        return ""
    body: list[str] = []
    for line in lines[start:]:
        heading = _HEADING.match(line)
        if heading and level is not None and len(heading.group(1)) <= level:
            break
        body.append(line)
    return "\n".join(body).strip()


def _has_applicability_condition(section: str) -> bool:
    """Regla explícita que subordina la batería al producto o al diff."""
    for clause in _CLAUSE_SPLIT.split(fold(section)):
        if (
            _CONDITION_MARKER.search(clause)
            and _CONDITION_SUBJECT.search(clause)
            and _CONDITION_ADDON.search(clause)
            and (
                _CONDITION_ACTION.search(clause)
                or _CONDITION_COPULA.search(clause)
            )
        ):
            return True
    return False


def unconditional_addon_battery(section: str, role: str) -> list[str]:
    """Obligaciones de addon de una sección Odoo sin condición de aplicabilidad.

    Devuelve un extracto corto por obligación cuando la sección declara la
    batería del rol y ninguna cláusula de la MISMA sección la subordina al
    producto o al diff. Una condición en otra sección (la matriz) no cuenta.
    """
    if not section:
        return []
    folded = fold(section)
    battery = tuple(term for term in ROLE_BATTERY[role] if fold(term) in folded)
    if not battery:
        return []
    if _has_applicability_condition(section):
        return []
    extracts: list[str] = []
    for clause in _CLAUSE_SPLIT.split(section):
        if any(fold(term) in fold(clause) for term in battery):
            extracts.append(clause.strip()[:180])
    return extracts or [section.strip()[:180]]


def odoo_delta_unconditional(text: str, role: str) -> list[str]:
    """Igual que ``unconditional_addon_battery`` sobre la sección marcada."""
    return unconditional_addon_battery(odoo_section(text), role)


# ---------------------------------------------------------------------------
# PC-09 — doctrina de selección y variante ausente (D4).
# ---------------------------------------------------------------------------

EMPTY_CASE = (
    "ausente",
    "absent",
    "null",
    "nulo",
    "vacio",
    "vacío",
    "empty",
    "blank",
)

NON_EMPTY_CASE = (
    "no vacio",
    "no vacío",
    "non-empty",
    "nonempty",
    "not empty",
    "any non-empty",
    "cualquier valor no vacio",
    "cualquier valor no vacío",
    "cualquier cadena no vacia",
    "cualquier cadena no vacía",
    "cualquier stack no vacio",
    "cualquier stack no vacío",
    "stack no vacio",
    "stack no vacío",
    "todo stack no vacio",
    "todo stack no vacío",
    "cadena no vacia",
    "cadena no vacía",
    "distinto de vacio",
    "distinto de vacío",
    "not null and not empty",
    "any non-empty string",
)

GENERIC_FORM = (
    "cdad-<role>",
    "cdad-<rol>",
    "cdad-{role}",
    "cdad-{rol}",
    "cdad-$(role)",
    "cdad-$role",
    "cdad-[role]",
    "agente generico",
    "agente genérico",
    "generic agent",
    "agente del rol sin",
    "sin sufijo",
    "without a suffix",
    "without suffix",
    "no suffix",
)

SUFFIX_FORM = (
    "sufijo",
    "suffix",
    "cdad-<role>-<stack>",
    "cdad-<rol>-<stack>",
    "cdad-{role}-{stack}",
    "cdad-{rol}-{stack}",
)

OTHER_VALUE = (
    "otro valor",
    "otros valores",
    "cualquier otro valor",
    "cualquier valor distinto",
    "valor distinto de",
    "any other value",
    "any other values",
    "any value other than",
    "other value",
)

UNPUBLISHED_VARIANT = (
    "no publicad",
    "unpublished",
    "not published",
    "ausente",
    "missing",
    "no disponible",
    "not available",
    "no existe",
    "inexistente",
    "not found",
    "unavailable",
    "no se encuentra",
)

MECHANICAL_REJECTION = (
    "mecanic",
    "mechanical",
    "rechaz",
    "reject",
    "falla",
    "fail",
)

BEFORE_LAUNCH = (
    "antes",
    "before",
    "previo",
    "prior",
    "no lanza",
    "does not launch",
    "no se lanza",
    "sin lanzar",
    "no invoca",
    "does not invoke",
)

PROCEDURAL_STOP = (
    "deten",
    "stop",
    "no despacha",
    "do not dispatch",
    "no se despacha",
    "impide",
    "prevent",
)

PROCEDURAL_DUTY = (
    "procediment",
    "procedural",
    "obligacion",
    "obligación",
    "duty",
    "debe",
    "must",
)

NO_SILENT_SUBSTITUTION = (
    ("negación", NEGATION),
    ("sustitución/fallback", ("sustitu", "substitut", "fallback")),
)

_FOLDS = {
    "other_value": tuple(fold(item) for item in OTHER_VALUE),
    "generic": tuple(fold(item) for item in GENERIC_FORM)
    + (fold("generico"), fold("generic"), fold("sin stack"), fold("without stack")),
    "suffix": tuple(fold(item) for item in SUFFIX_FORM),
    "unpublished": tuple(fold(item) for item in UNPUBLISHED_VARIANT),
    "mechanical": tuple(fold(item) for item in ("mecanic", "mechanical")),
}


def forbidden_other_value_fallback(text: str, radius: int = 200) -> list[str]:
    """Cláusulas donde «otro valor» se asigna al agente genérico (D4).

    Devuelve un extracto corto por cláusula prohibida. Se considera prohibida
    una ventana alrededor de «otro valor» que nombra el agente genérico, no
    nombra el sufijo y no niega la asignación. Un texto corregido («otro valor
    no significa agente genérico» / «cualquier otro valor deriva el sufijo»)
    no dispara el detector.
    """
    clauses: list[str] = []
    for paragraph in _BLANK.split(text):
        folded = fold(paragraph)
        for start, end in _positions(folded, OTHER_VALUE):
            window = folded[max(0, start - radius) : end + radius]
            if not any(item in window for item in _FOLDS["generic"]):
                continue
            if any(item in window for item in _FOLDS["suffix"]):
                continue
            if negation_in(window):
                continue
            clauses.append(paragraph.strip()[:180])
    return clauses


# Polaridad de la cláusula de rechazo mecánico (review T8, B1). D4: en la vía
# nativa la variante ausente es una detención PROCEDIMENTAL; el rechazo
# mecánico corresponde al adaptador externo. Una negación de la sustitución
# silenciosa («never substitute it silently») no absuelve la promesa mecánica,
# y la descripción correcta del adaptador externo no se imputa a la vía nativa.
_NEGATION_TOKEN = (
    r"(?:no|not|never|nunca|sin|tampoco|neither|nor|ni|cannot|can't|"
    r"isn't|aren't|wasn't|weren't|doesn't|don't|didn't)"
)
_VERB_NEGATION = re.compile(
    rf"(?<![a-z]){_NEGATION_TOKEN}(?![a-z])\s+"
    r"(?:(?:se|be|been|being|is|are|was|were|do|does|did|has|have|had)\s+)?"
    r"(?:(?:mechanically|mecanicamente)\s+)?"
    r"(?:reject|rechaz|promise|promet|exist|existe|hay|falla|fail|dispatch|"
    r"despach|launch|lanz|block|bloque|prevent|imped|guarantee|garantiz|"
    r"enforce|aplic)\w*"
)
_NOUN_NEGATION = re.compile(
    rf"(?<![a-z]){_NEGATION_TOKEN}(?![a-z])\s+"
    r"(?:(?:new|nueva|nuevo|another|otra|otro|a|an|una|un|the|el|la|any)\s+){0,3}"
    r"(?:mecanic\w*|mechanical|guard\w*|guarda\w*|rejection|rechazo)\b"
)
_GUARD_ABSENT = re.compile(
    r"(?:mecanic\w*|mechanical)[^.;]{0,40}(?:absent|ausente|missing|inexistente|"
    r"nonexistent|not exist|no existe)|"
    r"(?:guard\w*|guarda\w*)[^.;]{0,40}(?:absent|ausente|missing|inexistente|"
    r"nonexistent|not exist|no existe)"
)
_EXTERNAL_ONLY = ("external", "externo", "externa", "externamente")
_NATIVE_PATH = ("native", "nativo", "nativa")
_CLAUSE_SPLIT = re.compile(r"(?<=[.!?])\s+|;\s*|\n+")
_BOLD_LABEL = re.compile(r"^\s*\*\*([^*]+)\*\*\s*$")
_NATIVE_BULLET = re.compile(
    r"^\s*[-*]\s+\*\*\s*Mechanism\s*\(\s*native\s*\)\s*\.?\s*\*\*",
    re.IGNORECASE,
)


def native_mechanism_region(text: str) -> str:
    """Cuerpo de la declaración «Mechanism (native)» (D4).

    Localiza el encabezado markdown, la etiqueta en negrita o el ítem de lista
    con lead-in en negrita que nombra mechanism + native. La región termina en
    el siguiente encabezado de nivel igual o superior, en la siguiente etiqueta
    o en el siguiente ítem de lista del mismo nivel. Devuelve "" si el
    artefacto no declara la sección.
    """
    lines = text.splitlines()
    start = None
    level: int | None = None
    bullet_indent: int | None = None
    for index, line in enumerate(lines):
        heading = _HEADING.match(line)
        if heading:
            title = fold(heading.group(2))
            if "mechanism" in title and "native" in title:
                start, level = index + 1, len(heading.group(1))
                break
            continue
        bullet = _NATIVE_BULLET.match(line)
        if bullet:
            start = index
            bullet_indent = len(line) - len(line.lstrip())
            break
        bold = _BOLD_LABEL.match(line)
        if bold:
            title = fold(bold.group(1))
            if "mechanism" in title and "native" in title:
                start = index + 1
                break
    if start is None:
        return ""
    if level is not None:
        body: list[str] = []
        for line in lines[start:]:
            heading = _HEADING.match(line)
            if heading and len(heading.group(1)) <= level:
                break
            body.append(line)
        return "\n".join(body).strip()
    if bullet_indent is not None:
        body = [lines[start]]
        for line in lines[start + 1 :]:
            if _HEADING.match(line):
                break
            item = re.match(r"^(\s*)[-*]\s+", line)
            if item and len(item.group(1)) <= bullet_indent:
                break
            body.append(line)
        return "\n".join(body).strip()
    body = []
    for line in lines[start:]:
        if _HEADING.match(line) or _BOLD_LABEL.match(line):
            break
        body.append(line)
    return "\n".join(body).strip()


def mechanical_guard_negated(clause: str) -> bool:
    """La cláusula niega la guarda o el rechazo mecánico (no otra cosa)."""
    folded = fold(clause)
    if _VERB_NEGATION.search(folded) or _NOUN_NEGATION.search(folded):
        return True
    return bool(_GUARD_ABSENT.search(folded))


def _clauses_with_spans(folded: str) -> list[tuple[int, int, str]]:
    """Cláusulas del texto plegado con su posición, para decidir polaridad."""
    clauses: list[tuple[int, int, str]] = []
    cursor = 0
    for separator in _CLAUSE_SPLIT.finditer(folded):
        raw = folded[cursor : separator.start()]
        clause = raw.strip()
        if clause:
            start = cursor + raw.index(clause)
            clauses.append((start, start + len(clause), clause))
        cursor = separator.end()
    raw = folded[cursor:]
    clause = raw.strip()
    if clause:
        start = cursor + raw.index(clause)
        clauses.append((start, start + len(clause), clause))
    return clauses


def _is_external_only(clause: str) -> bool:
    """La cláusula describe al adaptador externo, no a la vía nativa (D4)."""
    folded = fold(clause)
    return any(marker in folded for marker in _EXTERNAL_ONLY) and not any(
        marker in folded for marker in _NATIVE_PATH
    )


def claims_new_mechanical_guard(text: str, radius: int = 300) -> list[str]:
    """Cláusulas que prometen un rechazo mecánico de la variante ausente.

    La polaridad se decide sobre la cláusula que formula el rechazo. No
    absuelven la promesa una negación de la sustitución silenciosa ni la
    descripción del adaptador externo (donde la guarda mecánica sí existe);
    sí la absuelve una negación de la guarda o del rechazo mecánico.
    """
    claims: list[str] = []
    for paragraph in _BLANK.split(text):
        folded = fold(paragraph)
        clauses = _clauses_with_spans(folded)
        seen: set[str] = set()
        for start, end in _positions(folded, UNPUBLISHED_VARIANT):
            window = folded[max(0, start - radius) : end + radius]
            if not any(item in window for item in _FOLDS["mechanical"]):
                continue
            claim: str | None = None
            for clause_start, clause_end, clause in clauses:
                if clause_start <= start < clause_end and any(
                    item in clause for item in _FOLDS["mechanical"]
                ):
                    claim = clause
                    break
            if claim is None:
                best: tuple[int, str] | None = None
                for clause_start, clause_end, clause in clauses:
                    if clause_end < max(0, start - radius) or clause_start > end + radius:
                        continue
                    if not any(item in clause for item in _FOLDS["mechanical"]):
                        continue
                    distance = min(abs(clause_start - start), abs(clause_end - end))
                    if best is None or distance < best[0]:
                        best = (distance, clause)
                if best is None:
                    continue
                claim = best[1]
            if _is_external_only(claim):
                continue
            if mechanical_guard_negated(claim):
                continue
            if claim in seen:
                continue
            seen.add(claim)
            claims.append(claim[:180])
    return claims


def _home_env(base: dict) -> dict:
    """Entorno del proceso hijo con el HOME/XDG aislado de la sesión.

    Se parte del entorno **vigente** (de modo que TMPDIR apunte a la raíz del
    test que ejecuta el proceso, no a una raíz ya retirada) y se sustituyen
    solo las rutas de usuario por las de la copia descartable.
    """
    env = os.environ.copy()
    for key in (
        "HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_STATE_HOME",
        "XDG_CACHE_HOME",
        "XDG_RUNTIME_DIR",
    ):
        value = base.get(key)
        if isinstance(value, str):
            env[key] = value
    for key in (
        "CDAD_INSTALL_ROOT",
        "CDAD_SKILL_EXTRA_DIRS",
        "CDAD_OPENCODE_AGENTS_DIR",
    ):
        env.pop(key, None)
    return env


def _run_make_agents(product: Path, env: dict[str, str], label: str) -> None:
    run = subprocess.run(
        ["make", "agents"],
        cwd=str(product),
        env=_home_env(env),
        text=True,
        capture_output=True,
        check=False,
    )
    if run.returncode != 0:
        raise AssertionError(
            f"PC-11: `make agents` ({label}) falló en la copia descartable "
            f"(rc={run.returncode}):\n{run.stdout[-1500:]}\n{run.stderr[-1500:]}"
        )


def _tree_digests(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


_INSTALL: dict[str, object] = {}


def installed_product() -> dict[str, object]:
    """Copia descartable generada + instalación aislada de los dos runtimes.

    ``CDAD_INSTALL_ROOT`` propio y ``CDAD_SKILL_EXTRA_DIRS`` vacío; nunca la
    instalación global ni el HOME real (EV-05/PC-12.a).
    """
    if "install_root" in _INSTALL:
        return _INSTALL
    disposable = disposable_product()
    product = disposable["product"]
    base = dict(disposable["env"])  # type: ignore[arg-type]
    assert isinstance(product, Path)
    install_root = Path(run_scoped_mkdtemp("cdad-010-002-install-"))
    env = _home_env(base)
    env["CDAD_INSTALL_ROOT"] = str(install_root)
    env["CDAD_SKILL_EXTRA_DIRS"] = ""
    run = subprocess.run(
        ["bash", str(product / "install.sh")],
        cwd=str(product),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    _INSTALL.update(
        {"product": product, "home_env": base, "env": env, "install_root": install_root, "run": run}
    )
    return _INSTALL


class _ProductCase(unittest.TestCase):
    """Base con la copia descartable del producto ya dada de alta."""

    maxDiff = None

    def disposable(self) -> dict[str, object]:
        disposable = disposable_product()
        run = disposable["run"]
        self.assertNotIsInstance(run, BaseException)
        assert isinstance(run, subprocess.CompletedProcess)
        self.assertTrue(
            run.returncode == 0,
            "PC-11: `make agents` falló en la copia descartable "
            f"(rc={run.returncode}):\n{run.stdout[-1500:]}\n{run.stderr[-1500:]}",
        )
        return disposable

    def install(self) -> dict[str, object]:
        bundle = installed_product()
        run = bundle["run"]
        assert isinstance(run, subprocess.CompletedProcess)
        self.assertTrue(
            run.returncode == 0,
            "PC-12.a: la instalación aislada falló (rc="
            f"{run.returncode}):\n{run.stdout[-1500:]}\n{run.stderr[-1500:]}",
        )
        return bundle

    def prepare_with_installed_cli(
        self, role: str, stack: str | None, write_scope: str
    ) -> dict:
        """Prepara un encargo con el CLI **instalado** y devuelve su request.

        El encargo se ejecuta en un proyecto sintético (fixture público); la
        resolución del destinatario se apunta al destino instalado del propio
        ``CDAD_INSTALL_ROOT``, nunca al HOME real.
        """
        bundle = self.install()
        install_root = bundle["install_root"]
        env = _home_env(bundle["home_env"])  # type: ignore[arg-type]
        assert isinstance(install_root, Path)
        cli = install_root / ".config/opencode/skills/cdad-cycle/scripts/cdad_packet.py"
        self.assertTrue(
            cli.is_file(),
            "PC-12.a: la instalación aislada no publicó el CLI en "
            f"`{relative(cli)}`.",
        )
        project = PrepareProject(
            Path(tempfile.mkdtemp(prefix="cdad-010-002-journey-")), role, "green"
        )
        self.addCleanup(shutil.rmtree, project.root, True)
        if stack is not None:
            project.fixture.state["stack"] = stack
            project.state_path.write_text(
                json.dumps(project.fixture.state), encoding="utf-8"
            )
        env["CDAD_OPENCODE_AGENTS_DIR"] = str(
            install_root / INSTALLED_AGENTS_DIRS["opencode"]
        )
        result = run_prepare(
            cli,
            *project.args("--write-scope", write_scope),
            cwd=project.root,
            env=env,
        )
        self.assertEqual(
            result.returncode,
            0,
            "PC-12.a: la preparación con el CLI instalado falló (rc="
            f"{result.returncode}): {result.stderr.decode(errors='replace')[-1500:]}",
        )
        request_path = project.out_dir / project.packet_id(1) / "REQUEST.json"
        self.assertTrue(
            request_path.is_file(),
            f"PC-12.a: `prepare` no publicó `{request_path.name}`.",
        )
        return json.loads(request_path.read_text(encoding="utf-8"))


# ===========================================================================
# (A) TestEngagement — el encargo documental llega al rol correcto sin
# ampliar autoridad (PC-01…PC-03).
# ===========================================================================


class TestEngagement(unittest.TestCase):
    """Promesa A: procedimiento operativo documental, roles y alcance.

    Sin estos tests, el usuario no tiene procedimiento comprometido y el
    encargo documental se improvisa, con riesgo de superponer producto,
    fuentes y oráculos (PC-01/PC-03), o de recibir una variante documental
    paralela (PC-02).
    """

    maxDiff = None

    def procedure(self) -> str:
        text = read_document(
            HANDOFF, "PC-01: el procedimiento documental (references/handoff-prompts.md)"
        )
        region = documentary_region(text)
        self.assertTrue(
            region.strip(),
            "PC-01: `skills/cdad-cycle/references/handoff-prompts.md` no tiene "
            "una región documental: el procedimiento operativo comprometido por "
            "D1/§3 no existe (no hay sección ni párrafo que trate el encargo "
            "documental).",
        )
        return region

    def test_documentary_procedure_uses_the_existing_fields_without_a_new_selector(
        self,
    ) -> None:
        """PC-01: las siete declaraciones, por los campos existentes, sin selector.

        Sin este test, el usuario no tiene procedimiento comprometido: el
        encargo documental se improvisa y no se sabe por qué campo viaja cada
        declaración (objetivo, producto, fuentes, alcance, verificadores,
        evidencia, límites).
        """
        region = self.procedure()

        assert_concepts(
            self,
            region,
            DOC_ANCHORS,
            DECLARATIONS,
            "PC-01: declaraciones del encargo documental",
            radius=NEAR_WIDE,
        )
        assert_concepts(
            self,
            region,
            DOC_ANCHORS,
            EXISTING_FIELDS,
            "PC-01: transporte por los campos existentes (D1)",
            radius=NEAR_WIDE,
        )

        self.assertTrue(
            concept_is_negated(region, NEW_SELECTOR_CONCEPTS, radius=700),
            "PC-01: el procedimiento no declara en forma negativa que NO se "
            "introduce un selector nuevo, un selector paralelo, un stack "
            "documental ni un campo nuevo (D1/INV-01). Un selector documental "
            "paralelo rompería la resolución, clasificación y distribución "
            "existentes.",
        )

    def test_six_role_boundaries_and_no_documentary_variant(self) -> None:
        """PC-02: seis roles y agentes actuales; sin variante documental.

        Sin este test, el usuario podría recibir un agente o selector
        documental paralelo y su encargo dejaría de llegar por el flujo
        canónico. Las fronteras de los seis roles y el conjunto de once
        agentes por runtime son controles de conservación ya verdes; la
        obligación ausente es que el procedimiento lo declare.
        """
        self.conservation_controls()
        region = self.procedure()

        assert_concepts(
            self,
            region,
            DOC_ANCHORS,
            (
                (
                    "fronteras y separación de responsabilidades",
                    ("frontera", "boundary", "separacion", "separation"),
                ),
                ("roles", ("rol", "role")),
                (
                    "se conservan",
                    (
                        "conserva",
                        "keeps",
                        "preserves",
                        "se mantiene",
                        "mantiene",
                        "permanec",
                        "remains",
                    ),
                ),
            ),
            "PC-02: el procedimiento conserva las fronteras de los seis roles",
            radius=NEAR_WIDE,
        )
        self.assertTrue(
            concept_is_negated(
                region,
                (
                    "variante documental",
                    "variantes documentales",
                    "selector documental",
                    "agente documental",
                    "documentary variant",
                    "documentary variants",
                    "documentary selector",
                    "documentary agent",
                ),
                radius=700,
            ),
            "PC-02: el procedimiento no declara que NO se crean variantes "
            "documentales (D1: se descartan variantes documentales y el selector "
            "paralelo; se usan los seis roles y los agentes actuales).",
        )

    def conservation_controls(self) -> None:
        """Controles ya verdes: fronteras de los seis roles y once agentes.

        Se ejecutan antes de la obligación ausente para que el RED quede
        acotado: si el fixture o el árbol de agentes estuviera roto, el fallo
        lo diría aquí y no se confundiría con la obligación ausente.
        """
        for role, requirements in ROLE_BOUNDARIES.items():
            with self.subTest(role=role, control="frontera"):
                text = read_document(
                    ROLE_SOURCES[role], f"PC-02: sources/roles/{role}.md"
                )
                assert_concepts(
                    self,
                    text,
                    ("rol", "role", "cdad"),
                    requirements,
                    f"PC-02: frontera del rol {role}",
                    radius=NEAR_WIDE,
                )

        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime, control="agentes"):
                directory = REPO_ROOT / PROMOTED_DIRS[runtime]
                names = sorted(path.name for path in directory.glob("*.md"))
                self.assertEqual(
                    names,
                    sorted(AGENT_NAMES),
                    f"PC-02: el runtime {runtime} no publica exactamente los "
                    f"agentes actuales ({len(AGENT_NAMES)}): apareció o faltó una "
                    "variante (una variante documental sería un selector "
                    f"paralelo). Observado: {names!r}",
                )
                for name in names:
                    self.assertIn(
                        role_of_agent(name),
                        ROLES,
                        f"PC-02: el agente {name!r} no declara uno de los seis "
                        f"roles actuales ({ROLES!r}): apareció una variante que "
                        "no corresponde a un rol existente.",
                    )

    def scope_controls(self) -> None:
        """Controles de comportamiento ya verdes de PC-03.

        Igualdad de alcances por rol (default del implementer sin
        documentación ni tests; test-writer solo `tests`; roles read-only sin
        escritura de producto) y publicación literal del alcance documental
        explícito. Se ejecutan antes de la obligación ausente para que el RED
        quede acotado al procedimiento.
        """
        defaults = {}
        for role, substage in (
            ("implementer", "green"),
            ("test-writer", "red"),
            ("architect", "draft"),
            ("reviewer", "review"),
            ("scribe", "memory"),
        ):
            project = PrepareProject(
                Path(tempfile.mkdtemp(prefix=f"cdad-010-002-scope-{role}-")),
                role,
                substage,
            )
            self.addCleanup(shutil.rmtree, project.root, True)
            result = run_prepare(
                REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py",
                *project.args(),
            )
            self.assertEqual(
                result.returncode,
                0,
                f"PC-03: `prepare` falló para el rol {role} (rc="
                f"{result.returncode}): {result.stderr.decode(errors='replace')[-1200:]}",
            )
            request = json.loads(
                (
                    project.out_dir / project.packet_id(1) / "REQUEST.json"
                ).read_text(encoding="utf-8")
            )
            defaults[role] = request["write_scope"]

        implementer_classes = {entry["class"] for entry in defaults["implementer"]}
        self.assertNotIn(
            "docs",
            implementer_classes,
            "PC-03: el default del implementer incorpora documentación "
            f"({defaults['implementer']!r}); la producción documental exige "
            "alcance editable explícito.",
        )
        self.assertNotIn(
            "tests",
            implementer_classes,
            "PC-03: el default del implementer obtiene escritura en tests "
            f"({defaults['implementer']!r}).",
        )
        self.assertEqual(
            {entry["class"] for entry in defaults["test-writer"]},
            {"tests"},
            "PC-03: el default del test-writer dejó de ser exclusivamente "
            f"`tests` ({defaults['test-writer']!r}).",
        )
        for role in ("architect", "reviewer", "scribe"):
            self.assertEqual(
                defaults[role],
                [],
                f"PC-03: el rol read-only {role} obtuvo escritura de producto "
                f"({defaults[role]!r}).",
            )

        project = PrepareProject(
            Path(tempfile.mkdtemp(prefix="cdad-010-002-scope-docs-")),
            "implementer",
            "green",
        )
        self.addCleanup(shutil.rmtree, project.root, True)
        result = run_prepare(
            REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py",
            *project.args("--write-scope", "docs=docs"),
        )
        self.assertEqual(
            result.returncode,
            0,
            "PC-03: un encargo con alcance editable documental explícito fue "
            f"rechazado (rc={result.returncode}): "
            f"{result.stderr.decode(errors='replace')[-1200:]}",
        )
        documented = json.loads(
            (project.out_dir / project.packet_id(1) / "REQUEST.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            documented["write_scope"],
            [{"class": "docs", "root": "docs"}],
            "PC-03: el alcance editable documental declarado no se publicó tal "
            "cual; el producto editable debe viajar por `write_scope` sin "
            "ampliaciones.",
        )

    def test_explicit_editable_scope_and_stop_on_protected_overlap(self) -> None:
        """PC-03: alcance editable explícito y detención de superposiciones.

        Sin este test, el usuario podría tener un productor escribiendo en
        tests u oráculos, o un encargo documental produciendo sin alcance
        declarado. El procedimiento es la obligación ausente; la igualdad de
        alcances por rol ya está medida por `test_packet_prepare` y se
        conserva aquí como control de comportamiento.
        """
        self.scope_controls()
        region = self.procedure()

        assert_concepts(
            self,
            region,
            DOC_ANCHORS,
            (
                (
                    "alcance editable",
                    (
                        "alcance editable",
                        "editable scope",
                        "alcance de escritura",
                        "write scope",
                        "write_scope",
                    ),
                ),
                (
                    "declarado explícitamente",
                    ("explicit", "explicito", "explícito", "declarad", "declared", "delimitad"),
                ),
            ),
            "PC-03: alcance editable explícito",
            radius=NEAR_WIDE,
        )
        assert_concepts(
            self,
            region,
            DOC_ANCHORS,
            (
                ("detener", ("deten", "stop", "se detiene", "stops")),
                ("superposición o ambigüedad", ("superpos", "overlap", "ambigü", "ambigu")),
                (
                    "insumos protegidos",
                    ("proteg", "protected", "oraculo", "oracle", "fuentes", "sources"),
                ),
            ),
            "PC-03: detención ante superposición o ambigüedad con insumos protegidos",
            radius=NEAR_WIDE,
        )

# ===========================================================================
# (B) TestOdooApplicability — documentar en Odoo sin fingir ni eludir pruebas
# de addon (PC-04/PC-05).
# ===========================================================================


class TestOdooApplicability(_ProductCase):
    """Promesa B: frontera de addon y matriz Odoo por rol.

    Sin estos tests, en un proyecto Odoo el encargo documental queda bloqueado
    por una batería de addon que no modifica, el implementer modifica addon sin
    inventario ni entorno, o un cambio de addon oculto bajo etiqueta documental
    se acepta sin instalación limpia, lint ni OCA.
    """

    maxDiff = None

    def assert_role_matrix(self, role: str, text: str, label: str) -> None:
        """Celda del rol: exención documental + obligación de addon + mixto."""
        matrix = MATRIX[role]
        assert_concepts(
            self,
            text,
            DOC_ANCHORS,
            (
                ("objeto de la exención documental", matrix["exemption_objects"]),
                ("negación de la batería en el caso documental", NEGATION),
            )
            + tuple(matrix["exemption_extra"]),
            f"{label}: exención documental del rol {role}",
            radius=NEAR,
        )
        self.assertTrue(
            document_is_negated_in_documentary_paragraph(text, matrix["exemption_objects"]),
            f"{label}: el rol {role} no tiene un párrafo documental que NIEGUE "
            "la obligación de addon que no corresponde (la exención tiene que "
            "estar acotada al caso documental; un «no exige addon» sin acotar "
            "contradice la columna addon de la misma matriz).",
        )
        assert_concepts(
            self,
            text,
            ODOO_ANCHORS,
            matrix["obligation"],
            f"{label}: obligación de addon del rol {role}",
            radius=NEAR,
        )
        assert_concepts(
            self,
            text,
            ("mixto", "mixed"),
            matrix["mixed"],
            f"{label}: fila mixta del rol {role}",
            radius=NEAR,
        )

    def test_addon_boundary_and_module_documentation(self) -> None:
        """PC-04: frontera del addon y documentación del módulo (D2).

        Sin este test, la documentación dentro de un módulo se trataría como
        trabajo de addon (exigiendo una batería que no corresponde) o el addon
        se colaría como documentación («está dentro del módulo, es un
        documento»), y la ubicación por sí sola decidiría la obligación.
        """
        report: list[str] = []
        for label, path in BOUNDARY_SURFACES:
            text = read_document(path, f"PC-04: frontera del addon en {label}")
            missing = missing_in_best_window(
                text,
                ("__manifest__.py",),
                ADDON_BOUNDARY + BOUNDARY_CLASSIFICATION + BOUNDARY_LIMITS + BOUNDARY_LOCATION_ALONE,
                radius=5200,
            )
            if not missing:
                return  # una fuente competente contiene la frontera completa
            report.append(f"{label}: faltan {missing!r}")

        self.fail(
            "PC-04: ninguna fuente competente contiene la frontera del addon "
            "completa (D2): el trabajo de addon, la documentación del módulo "
            "como producto documental salvo contrato, la ubicación que por sí "
            "sola no exige batería, y el límite de que la frontera no cambia "
            "clasificación de rutas, permisos ni alcances.\n"
            + "\n".join(report[:8])
        )

    def test_producer_roles_matrix(self) -> None:
        """PC-04: matriz de architect, test-writer e implementer.

        Sin este test, architect/test-writer/implementer no sabrían cuándo
        rige la batería de addon: el architect exigiría inventario para
        documentación pura, el test-writer exigiría `TransactionCase` por el
        dominio, o el implementer modificaría un addon sin lint/OCA.
        """
        # Control de vacuidad del detector de la exención acotada.
        self.assertFalse(
            document_is_negated_in_documentary_paragraph(
                "A documentary engagement requires TransactionCase and @tagged.",
                ("transactioncase", "@tagged"),
            ),
            "control de vacuidad roto: el detector da por negada una obligación "
            "afirmada.",
        )
        self.assertTrue(
            document_is_negated_in_documentary_paragraph(
                "A documentary engagement does not require TransactionCase.",
                ("transactioncase",),
            ),
            "control de vacuidad roto: el detector no reconoce una exención "
            "documental negada.",
        )

        for role in PRODUCER_ROLES:
            with self.subTest(role=role):
                text = read_document(
                    ROLE_SOURCES[role], f"PC-04: sources/roles/{role}.md"
                )
                self.assert_role_matrix(role, text, "PC-04")

    def test_review_coordination_memory_matrix_and_diff_prevalence(self) -> None:
        """PC-05: matriz de reviewer, orquestador y scribe; el diff prevalece.

        Sin este test, un cambio de addon oculto bajo una etiqueta documental
        se aceptaría como documental puro, sin instalación limpia, lint ni OCA,
        y se concederían permisos retroactivos.
        """
        for role in REVIEW_ROLES:
            with self.subTest(role=role):
                text = read_document(
                    ROLE_SOURCES[role], f"PC-05: sources/roles/{role}.md"
                )
                self.assert_role_matrix(role, text, "PC-05")

        reviewer = read_document(
            ROLE_SOURCES["reviewer"], "PC-05: el diff real en el reviewer"
        )
        assert_concepts(
            self,
            reviewer,
            ("diff",),
            DIFF_PREVALENCE,
            "PC-05: el diff real prevalece sobre la etiqueta (reviewer)",
            radius=NEAR,
        )
        assert_concepts(
            self,
            reviewer,
            ("diff", "etiqueta", "label"),
            HIDDEN_ADDON_UNDER_LABEL,
            "PC-05: un cambio de addon oculto bajo etiqueta documental se informa y bloquea",
            radius=NEAR,
        )

        orchestrator = read_document(
            ROLE_SOURCES["orchestrator"], "PC-05: el diff real en el orquestador"
        )
        assert_concepts(
            self,
            orchestrator,
            ("diff",),
            DIFF_PREVALENCE,
            "PC-05: el diff real prevalece sobre la etiqueta (orquestador)",
            radius=NEAR,
        )
        assert_concepts(
            self,
            orchestrator,
            ("retroactiv", "permiso", "permission"),
            RETROACTIVE_DENIED,
            "PC-05: el orquestador no concede permisos retroactivos",
            radius=NEAR,
        )

        # Control de conservación: las cargas de dominio Odoo siguen presentes.
        for role in ROLES:
            with self.subTest(domain=role):
                text = read_document(
                    ROLE_SOURCES[role], f"PC-04/05: carga de dominio de {role}"
                )
                self.assertIn(
                    "odoo",
                    fold(text),
                    f"PC-04/05: la fuente del rol {role} perdió su carga de "
                    "dominio Odoo al corregir la aplicabilidad.",
                )

    def test_documentary_verifier_is_not_an_addon_test(self) -> None:
        """PC-04: un verificador documental no es un test de addon (D2).

        Sin este test, un verificador estructural documental se convertiría en
        test de addon por estar en un proyecto Odoo, y a la inversa: se
        olvidaría que los tests de addon verifican un producto de addon aunque
        el test-writer escriba exclusivamente bajo `tests/`.
        """
        text = read_document(
            ROLE_SOURCES["test-writer"],
            "PC-04: aplicabilidad del test-writer en proyectos Odoo",
        )
        assert_concepts(
            self,
            text,
            ("verificador", "verifier", "documental", "documentary"),
            VERIFIER_NOT_ADDON,
            "PC-04: el verificador documental no se convierte en test de addon",
            radius=NEAR,
        )
        assert_concepts(
            self,
            text,
            ("addon", "tests", "pruebas"),
            ADDON_TEST_ATTRIBUTION,
            "PC-04: los tests de addon verifican un producto de addon aunque se escriba bajo tests/",
            radius=NEAR,
        )

    def test_distributed_artifacts_carry_the_matrix(self) -> None:
        """PC-04/PC-05: los artefactos distribuidos llevan la matriz.

        Sin este test, la matriz quedaría en las fuentes pero no llegaría a los
        agentes generados y promovidos de ninguno de los dos runtimes: el
        agente que recibe el encargo seguiría aplicando la obligación
        incondicional de addon.
        """
        disposable = self.disposable()
        product = disposable["product"]
        assert isinstance(product, Path)
        staging = product / STAGING_AGENTS

        for runtime in RUNTIMES:
            for name in AGENT_NAMES:
                with self.subTest(runtime=runtime, agent=name):
                    path = staging / runtime / name
                    text = read_document(
                        path,
                        f"PC-04/05: agente generado {runtime}/{name}",
                    )
                    self.assert_role_matrix(
                        role_of_agent(name), text, f"PC-04/05 en {runtime}/{name}"
                    )

    def _odoo_delta_detector_self_check(self) -> None:
        """Control de vacuidad del detector de B2 y de la sección Odoo."""

        def wrap(body: str) -> str:
            return (
                "<!-- cdad-section:odoo -->\n"
                + body
                + "\n<!-- /cdad-section -->\n"
            )

        proximity = wrap(
            "Documentary engagements keep the addon battery. Evidence required: "
            "green `make test-clean` + pasted output; `oca-checks` with 0 "
            "findings; `pylint-odoo` with no blocking E/W."
        )
        self.assertTrue(
            odoo_delta_unconditional(proximity, "reviewer"),
            "control de vacuidad roto: la cercanía de «documentary» sin una "
            "regla de aplicabilidad no condiciona el delta Odoo.",
        )
        conditioned = wrap(
            "Evidence required only when the product or the diff touches addon "
            "code: green `make test-clean` + pasted output; `oca-checks` with 0 "
            "findings; `pylint-odoo` with no blocking E/W."
        )
        self.assertEqual(
            odoo_delta_unconditional(conditioned, "reviewer"),
            [],
            "control de vacuidad roto: el detector no reconoce la condición "
            "explícita «only when the product or the diff touches addon code».",
        )
        copula = wrap(
            "Evidence required when the product is an addon: `make test-clean` "
            "+ pasted output."
        )
        self.assertEqual(
            odoo_delta_unconditional(copula, "reviewer"),
            [],
            "control de vacuidad roto: el detector no reconoce la condición "
            "«when the product is an addon» (cópula, sin verbo de acción).",
        )
        spanish = wrap(
            "Solo si el encargo modifica o verifica un addon: `make test`, lint "
            "limpio, `oca-checks` sin hallazgos."
        )
        self.assertEqual(
            odoo_delta_unconditional(spanish, "implementer"),
            [],
            "control de vacuidad roto: el detector no reconoce la condición "
            "«solo si el encargo modifica o verifica un addon».",
        )
        elsewhere = wrap(
            "Evidence required: `make test`, lint limpio, `oca-checks` sin "
            "hallazgos."
        ) + (
            "\n## Applicability\n"
            "Documentary work does not require addon tests; addon work does.\n"
        )
        self.assertTrue(
            odoo_delta_unconditional(elsewhere, "implementer"),
            "control de vacuidad roto: una condición en otra sección no "
            "condiciona el delta; la tabla de aplicabilidad no es coherencia.",
        )

    def test_odoo_role_deltas_are_conditioned_on_product_or_diff(self) -> None:
        """PC-04/PC-05 — B2: el delta Odoo de rol no exige la batería sin condición.

        Sin este test, `cdad-reviewer-odoo`, `cdad-implementer-odoo` y
        `cdad-test-writer-odoo` —en su fuente y en los seis agentes generados—
        pueden exigir o fabricar evidencia de addon sobre un diff puramente
        documental: la tabla de aplicabilidad vive en otra sección y su
        presencia no subordina el delta (Promesa B, INV-05, B2).
        """
        self._odoo_delta_detector_self_check()
        surfaces: list[tuple[str, str, str]] = []
        for role in ("reviewer", "implementer", "test-writer"):
            text = read_document(ROLE_SOURCES[role], f"B2: sources/roles/{role}.md")
            surfaces.append((f"sources/roles/{role}.md", odoo_section(text), role))
        for label, path, role in PROMOTED_ODOO_AGENTS:
            text = read_document(path, f"B2: agente distribuido {label}")
            surfaces.append((label, odoo_stack_delta_region(text), role))
        missing_sections: list[str] = []
        battery_missing: list[str] = []
        unresolved_by_surface: dict[str, list[str]] = {}
        for label, region, role in surfaces:
            if not region:
                missing_sections.append(label)
                continue
            battery = [
                term for term in ROLE_BATTERY[role] if fold(term) in fold(region)
            ]
            if not battery:
                battery_missing.append(label)
                continue
            unresolved = unconditional_addon_battery(region, role)
            if unresolved:
                unresolved_by_surface[label] = unresolved[:1]
        self.assertEqual(
            missing_sections,
            [],
            "B2: no existe la sección Odoo del rol (marcador "
            "`<!-- cdad-section:odoo -->` o encabezado «Odoo stack delta»); el "
            f"delta Odoo no es verificable: {missing_sections!r}",
        )
        self.assertEqual(
            battery_missing,
            [],
            "B2: la sección Odoo perdió la batería de addon (PC-04/PC-05); no "
            f"se puede condicionar lo que se eliminó: {battery_missing!r}",
        )
        self.assertEqual(
            unresolved_by_surface,
            {},
            "B2: la sección Odoo declara la batería de addon sin una condición "
            "explícita sobre el producto o el diff (por ejemplo «only when the "
            "product or the diff touches addon code» / «solo si el encargo "
            "modifica o verifica un addon»). La tabla de aplicabilidad de otra "
            "sección no condiciona este delta. Un extracto por superficie: "
            f"{unresolved_by_surface!r}",
        )


# ===========================================================================
# (C) TestDispatchDoctrine — las instrucciones no prometen otra resolución
# (PC-09; mitad documental de PC-08).
# ===========================================================================


class TestDispatchDoctrine(unittest.TestCase):
    """Promesa D: derivación por sufijo y variante ausente.

    Sin estos tests, una sesión nativa caería al agente genérico para un stack
    no vacío, o una variante no publicada se sustituiría en silencio.
    """

    maxDiff = None

    def _detector_self_check(self) -> None:
        """Control de vacuidad: el detector distingue la cláusula de D4."""
        wrong = (
            "If the stack is absent, null, empty or any other value, "
            "the agent is `cdad-<role>`."
        )
        right = (
            "Only an absent, null or empty stack derives `cdad-<role>`. "
            "Any other value, meaning any non-empty stack, derives a suffix."
        )
        self.assertTrue(
            forbidden_other_value_fallback(wrong),
            "control de vacuidad roto: el detector no reconoce la cláusula "
            "«otro valor → agente genérico».",
        )
        self.assertEqual(
            forbidden_other_value_fallback(right),
            [],
            "control de vacuidad roto: el detector marca como prohibida una "
            "cláusula corregida (la negación o el sufijo la absuelven).",
        )
        self.assertTrue(
            claims_new_mechanical_guard(
                "An unpublished variant is rejected by a new mechanical guard "
                "on the native path."
            ),
            "control de vacuidad roto: el detector no reconoce la promesa de "
            "una guarda mecánica nueva en la vía nativa.",
        )
        self.assertEqual(
            claims_new_mechanical_guard(
                "An unpublished variant is a procedural duty on the native path: "
                "no new mechanical guard is promised."
            ),
            [],
            "control de vacuidad roto: el detector marca una cláusula que NIEGA "
            "la guarda mecánica nueva.",
        )

    def test_every_selection_surface_derives_a_suffix_and_keeps_no_other_value_fallback(
        self,
    ) -> None:
        """PC-09: toda superficie deriva sufijo y no conserva «otro valor → genérico».

        Sin este test, el usuario recibiría el agente genérico aunque su
        encargo declare un dominio no vacío, que es exactamente la falla que D4
        corrige.
        """
        self._detector_self_check()
        for label, path in SELECTION_SURFACES:
            with self.subTest(surface=label):
                text = read_document(path, f"PC-09: doctrina de selección en {label}")
                assert_concepts(
                    self,
                    text,
                    SELECTION_ANCHORS,
                    (
                        ("stack no vacío", NON_EMPTY_CASE),
                        ("derivación con sufijo", SUFFIX_FORM),
                    ),
                    f"PC-09: derivación con sufijo para todo stack no vacío ({label})",
                    radius=NEAR_WIDE,
                )
                assert_concepts(
                    self,
                    text,
                    SELECTION_ANCHORS,
                    (
                        ("ausente/null/vacío", EMPTY_CASE),
                        ("agente genérico", GENERIC_FORM),
                    ),
                    f"PC-09: el agente genérico solo para stack ausente/null/vacío ({label})",
                    radius=NEAR_WIDE,
                )
                forbidden = forbidden_other_value_fallback(text)
                self.assertEqual(
                    forbidden,
                    [],
                    f"PC-09 ({label}): queda una cláusula «otro valor → agente "
                    "genérico». D4: cualquier stack no vacío deriva un sufijo; "
                    "«otro valor» no significa agente genérico. Extracto: "
                    f"{forbidden[:2]!r}",
                )

    def test_absent_variant_is_mechanical_external_and_procedural_native(
        self,
    ) -> None:
        """PC-09/PC-08: variante ausente — mecánica externa, procedimental nativa.

        Sin este test, una variante requerida y no publicada se sustituiría en
        silencio, o se atribuiría al módulo una garantía mecánica que no tiene
        (D4: `prepare` y el registro de despacho no son detectores universales
        de publicación).
        """
        for label, path in ADAPTER_SURFACES:
            with self.subTest(surface=label, duty="mecánica"):
                text = read_document(
                    path, f"PC-09: variante ausente en el adaptador {label}"
                )
                assert_concepts(
                    self,
                    text,
                    ("agent", "agente", "stack"),
                    (
                        ("variante ausente o no publicada", UNPUBLISHED_VARIANT),
                        ("rechazo mecánico", MECHANICAL_REJECTION),
                        ("antes de lanzar el trabajo de rol", BEFORE_LAUNCH),
                    ),
                    f"PC-09: rechazo mecánico de la variante ausente en {label}",
                    radius=NEAR_WIDE,
                )
                assert_concepts(
                    self,
                    text,
                    ("agent", "agente", "stack"),
                    NO_SILENT_SUBSTITUTION,
                    f"PC-09: sin sustitución silenciosa en {label}",
                    radius=NEAR_WIDE,
                )

        for label, path in NATIVE_SURFACES:
            with self.subTest(surface=label, duty="procedimental"):
                text = read_document(
                    path, f"PC-09: variante ausente en la vía nativa {label}"
                )
                assert_concepts(
                    self,
                    text,
                    ("agent", "agente", "stack"),
                    (
                        ("variante ausente o no publicada", UNPUBLISHED_VARIANT),
                        ("detención del despacho", PROCEDURAL_STOP),
                        ("obligación procedimental", PROCEDURAL_DUTY),
                    ),
                    f"PC-09: detención procedimental de la variante ausente en {label}",
                    radius=NEAR_WIDE,
                )
                assert_concepts(
                    self,
                    text,
                    ("agent", "agente", "stack"),
                    NO_SILENT_SUBSTITUTION,
                    f"PC-09: sin sustitución silenciosa en {label}",
                    radius=NEAR_WIDE,
                )
                self.assertEqual(
                    claims_new_mechanical_guard(text),
                    [],
                    f"PC-09 ({label}): la vía nativa promete una guarda mecánica "
                    "nueva para la variante ausente. D4: la vía nativa es una "
                    "obligación procedimental; no se promete una nueva guarda "
                    "mecánica ni se atribuye al módulo una garantía que no "
                    f"tiene. Extracto: {claims_new_mechanical_guard(text)[:2]!r}",
                )

    def _native_guard_detector_self_check(self) -> None:
        """Control de vacuidad y de polaridad del detector de la vía nativa."""
        literal = (
            "A required variant that is not published is rejected mechanically "
            "before launching the role work"
        )
        self.assertTrue(
            claims_new_mechanical_guard(literal),
            "control de vacuidad roto: el detector no reconoce la promesa "
            "mecánica literal de la vía nativa (B1).",
        )
        self.assertTrue(
            claims_new_mechanical_guard(
                literal
                + "; never substitute it silently by the generic agent."
            ),
            "control de polaridad roto: una negación de la SUSTITUCIÓN "
            "silenciosa absuelve la promesa mecánica; B1 exige mirar la "
            "polaridad de la cláusula, no cualquier «never» de la ventana.",
        )
        for label, negative in (
            (
                "negación de la guarda nueva",
                "An unpublished variant is a procedural duty on the native "
                "path: no new mechanical guard is promised.",
            ),
            (
                "negación del rechazo mecánico",
                "An unpublished variant is not rejected mechanically on the "
                "native path.",
            ),
            (
                "negación del despacho mecánico",
                "An unpublished variant is not dispatched mechanically on the "
                "native path.",
            ),
            (
                "guarda mecánica ausente",
                "An unpublished variant on the native path: the mechanical "
                "guard is absent.",
            ),
        ):
            with self.subTest(negative=label):
                self.assertEqual(
                    claims_new_mechanical_guard(negative),
                    [],
                    f"control de vacuidad roto: el detector imputa a la vía "
                    f"nativa una promesa que la cláusula niega ({label}).",
                )
        self.assertEqual(
            claims_new_mechanical_guard(
                "The external adapter rejects a required but unpublished "
                "variant mechanically before launching the role work."
            ),
            [],
            "control de vacuidad roto: el detector imputa a la vía nativa la "
            "descripción correcta del adaptador externo, donde la guarda "
            "mecánica sí existe (D4).",
        )
        document = (
            "## Mechanism (external)\n"
            "The external adapter rejects a required but unpublished variant "
            "mechanically before launching the role work.\n\n"
            "## Mechanism (native)\n"
            + literal
            + "; never substitute it silently by the generic agent.\n"
        )
        region = native_mechanism_region(document)
        self.assertIn(
            "required variant",
            region,
            "control de vacuidad roto: la región nativa no es la sección "
            "declarada.",
        )
        self.assertNotIn(
            "external adapter",
            region,
            "control de vacuidad roto: la región nativa incluye el adaptador "
            "externo.",
        )
        self.assertTrue(
            claims_new_mechanical_guard(region),
            "control de vacuidad roto: el detector no reporta la promesa "
            "mecánica dentro de la región nativa.",
        )

    def test_native_adapters_do_not_claim_a_mechanical_guard(self) -> None:
        """PC-09/D4 — la vía nativa no promete rechazo mecánico (B1).

        Sin este test, el orquestador nativo omite la comprobación de
        publicación porque confía en una guarda mecánica inexistente: una
        variante requerida y no publicada se lanzaría o se sustituiría en
        silencio, y la instrucción se contradice (PC-09, D4, B1).
        """
        self._native_guard_detector_self_check()
        anchors = ("variant", "variante", "agent", "agente", "stack")
        missing_regions: list[str] = []
        claims_by_surface: dict[str, list[str]] = {}
        duties_missing: dict[str, dict[str, list[str]]] = {}
        for label, path in ADAPTER_NATIVE_SURFACES:
            text = read_document(path, f"B1: vía nativa en {label}")
            region = native_mechanism_region(text)
            if not region:
                missing_regions.append(label)
                continue
            claims = claims_new_mechanical_guard(region)
            if claims:
                claims_by_surface[label] = claims[:1]
            absence: dict[str, list[str]] = {}
            for concept, requirements in (
                (
                    "obligación procedimental",
                    (
                        ("variante ausente o no publicada", UNPUBLISHED_VARIANT),
                        ("detención del despacho", PROCEDURAL_STOP),
                        ("obligación procedimental", PROCEDURAL_DUTY),
                    ),
                ),
                ("sin sustitución silenciosa", NO_SILENT_SUBSTITUTION),
            ):
                missing = missing_in_best_window(
                    region, anchors, requirements, radius=NEAR_WIDE
                )
                if missing:
                    absence[concept] = missing
            if absence:
                duties_missing[label] = absence
        self.assertEqual(
            missing_regions,
            [],
            "B1: los artefactos distribuidos no declaran la declaración "
            "«Mechanism (native)» de D4; sin ella no hay obligación "
            f"procedimental verificable: {missing_regions!r}",
        )
        self.assertEqual(
            claims_by_surface,
            {},
            "B1: la vía nativa promete un rechazo mecánico de la variante "
            "ausente. D4: la vía nativa es una detención procedimental; la "
            "guarda mecánica corresponde al adaptador externo. Un extracto por "
            f"superficie: {claims_by_surface!r}",
        )
        self.assertEqual(
            duties_missing,
            {},
            "B1: la declaración nativa perdió la obligación procedimental o la "
            "prohibición de sustitución silenciosa de D4: "
            f"{duties_missing!r}",
        )


# ===========================================================================
# (D) TestDistribution — la integración se distribuye reproduciblemente
# (PC-11, PC-12.a).
# ===========================================================================


class TestDistribution(_ProductCase):
    """Promesa F: generación reproducible, instalación aislada y recorridos.

    Sin estos tests, los agentes distribuidos podrían no corresponder a las
    fuentes aprobadas, dos generaciones podrían diferir y el perfil documental
    descrito quedaría sin distribuir: el usuario no podría ejecutarlo tras
    instalar.
    """

    def test_generation_is_reproducible_and_promoted_matches_staging(self) -> None:
        """PC-11: dos generaciones idénticas y promovidos == staging.

        Control de conservación ya verde (``test_cdad_generate`` y
        ``TestPd13StaticBlockCeiling`` cubren el determinismo y el techo
        estático). Se conserva aquí porque es la garantía de procedencia que
        PC-11 exige: los promovidos no se editan a mano.
        """
        disposable = self.disposable()
        product = disposable["product"]
        env = disposable["env"]
        assert isinstance(product, Path)
        assert isinstance(env, dict)

        _run_make_agents(product, env, "primera generación")
        first = _tree_digests(product / "agents")
        first.update(
            {
                f"staging/{key}": value
                for key, value in _tree_digests(product / "build" / "staging").items()
            }
        )
        _run_make_agents(product, env, "segunda generación")
        second = _tree_digests(product / "agents")
        second.update(
            {
                f"staging/{key}": value
                for key, value in _tree_digests(product / "build" / "staging").items()
            }
        )
        differing = sorted(
            path for path in set(first) | set(second) if first.get(path) != second.get(path)
        )
        self.assertEqual(
            differing,
            [],
            "PC-11: dos generaciones con iguales entradas no producen agentes y "
            "manifiestos idénticos (difieren: "
            f"{differing[:8]!r}).",
        )
        self.assertTrue(
            (product / MANIFEST).is_file(),
            f"PC-11: `make agents` no publicó `build/staging/manifest.json`: no "
            "hay manifiesto de procedencia que comparar.",
        )

        staging = product / STAGING_AGENTS
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime):
                staged = sorted(path.name for path in (staging / runtime).glob("cdad-*.md"))
                self.assertEqual(
                    staged,
                    sorted(AGENT_NAMES),
                    f"PC-11: staging del runtime {runtime} no publica los "
                    f"{len(AGENT_NAMES)} agentes declarados: {staged!r}",
                )
                for name in AGENT_NAMES:
                    promoted = product / PROMOTED_DIRS[runtime] / name
                    self.assertTrue(
                        promoted.is_file(),
                        f"PC-11: `make agents` no promovió `{PROMOTED_DIRS[runtime] / name}`.",
                    )
                    self.assertEqual(
                        promoted.read_bytes(),
                        (staging / runtime / name).read_bytes(),
                        f"PC-11: el agente promovido {runtime}/{name} no coincide "
                        "con staging: un promovido editado a mano no procede de "
                        "las fuentes canónicas.",
                    )

    def test_isolated_install_distributes_corrected_surfaces_and_the_generic_journey(
        self,
    ) -> None:
        """PC-12.a: instalación aislada y recorrido documental genérico.

        Sin este test, el perfil documental no existiría tras instalar: las
        referencias corregidas, las skills Odoo y los agentes de ambos runtimes
        podrían quedar en el producto pero no en el destino, y un encargo
        documental genérico no resolvería su destinatario.
        """
        bundle = self.install()
        product = bundle["product"]
        install_root = bundle["install_root"]
        assert isinstance(product, Path)
        assert isinstance(install_root, Path)

        self.assertEqual(
            len(SKILL_ROOTS),
            3,
            "PC-12.a: los destinos `skills/` declarados por los tests del "
            f"instalador no son tres: {SKILL_ROOTS!r}",
        )
        for root in SKILL_ROOTS:
            for relpath in CORRECTED_CDAD_SURFACES:
                with self.subTest(skills_root=root, surface=relpath):
                    source = product / "skills" / "cdad-cycle" / relpath
                    installed = install_root / root / "cdad-cycle" / relpath
                    self.assertTrue(
                        installed.is_file(),
                        f"PC-12.a: la instalación no publicó `{root}/cdad-cycle/{relpath}`.",
                    )
                    self.assertEqual(
                        installed.read_bytes(),
                        source.read_bytes(),
                        f"PC-12.a: los bytes instalados de `{relpath}` en `{root}` "
                        "no coinciden con los bytes de origen.",
                    )
            for name in ODOO_SKILLS:
                with self.subTest(skills_root=root, skill=name):
                    source = ODOO_SKILL_FILES[name]
                    installed = install_root / root / name / "SKILL.md"
                    self.assertTrue(
                        installed.is_file(),
                        f"PC-12.a: la instalación no publicó `{root}/{name}/SKILL.md`.",
                    )
                    self.assertEqual(
                        installed.read_bytes(),
                        source.read_bytes(),
                        f"PC-12.a: los bytes instalados de `{name}/SKILL.md` en "
                        f"`{root}` no coinciden con los bytes de origen.",
                    )

        staging = product / STAGING_AGENTS
        for runtime in RUNTIMES:
            for name in AGENT_NAMES:
                with self.subTest(runtime=runtime, agent=name):
                    installed = install_root / INSTALLED_AGENTS_DIRS[runtime] / name
                    self.assertTrue(
                        installed.is_file(),
                        f"PC-12.a: la instalación no publicó el agente {runtime}/{name}.",
                    )
                    self.assertEqual(
                        installed.read_bytes(),
                        (staging / runtime / name).read_bytes(),
                        f"PC-12.a: los bytes instalados del agente {runtime}/{name} "
                        "no coinciden con staging.",
                    )

        request = self.prepare_with_installed_cli(
            "implementer", stack=None, write_scope="docs=docs"
        )
        self.assertEqual(
            request["role"],
            "implementer",
            "PC-12.a: la preparación del encargo documental genérico perdió el rol.",
        )
        self.assertEqual(
            request["agent"],
            "cdad-implementer",
            "PC-12.a: el encargo documental genérico (sin `stack`) no resuelve al "
            "agente genérico del rol.",
        )
        self.assertEqual(
            request["write_scope"],
            [{"class": "docs", "root": "docs"}],
            "PC-12.a: el encargo documental genérico no conserva su frontera de "
            "escritura (producto editable documental explícito).",
        )
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime, resolution="genérico"):
                installed = (
                    install_root
                    / INSTALLED_AGENTS_DIRS[runtime]
                    / f"{request['agent']}.md"
                )
                self.assertTrue(
                    installed.is_file(),
                    f"PC-12.a: el agente resuelto `{request['agent']}` no existe "
                    f"en el destino instalado de {runtime}.",
                )
                self.assertEqual(
                    installed.read_bytes(),
                    (staging / runtime / f"{request['agent']}.md").read_bytes(),
                    f"PC-12.a: el agente resuelto `{request['agent']}` instalado "
                    f"en {runtime} no procede de staging.",
                )

    def test_documentary_odoo_journey_keeps_domain_and_write_frontier(self) -> None:
        """PC-12.a: recorrido documental/Odoo con dominio y frontera de escritura.

        Sin este test, el recorrido documental con `stack=odoo` no conservaría
        el dominio: el encargo podría resolver el agente genérico, o la
        etiqueta documental podría ampliar la escritura hacia un addon que el
        contrato no autoriza.
        """
        bundle = self.install()
        product = bundle["product"]
        install_root = bundle["install_root"]
        assert isinstance(product, Path)
        assert isinstance(install_root, Path)

        request = self.prepare_with_installed_cli(
            "implementer", stack="odoo", write_scope="docs=docs"
        )
        self.assertEqual(
            request["role"],
            "implementer",
            "PC-12.a: la preparación del encargo documental/Odoo perdió el rol.",
        )
        self.assertEqual(
            request["agent"],
            "cdad-implementer-odoo",
            "PC-12.a: el encargo documental con `stack=odoo` no resuelve la "
            "variante Odoo del rol (el dominio no se conserva).",
        )
        classes = {entry["class"] for entry in request["write_scope"]}
        self.assertEqual(
            classes,
            {"docs"},
            "PC-12.a: la frontera de escritura del recorrido documental/Odoo no "
            f"es exclusivamente documental ({request['write_scope']!r}): la "
            "etiqueta documental no autoriza escritura de addon.",
        )

        staging = product / STAGING_AGENTS
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime, resolution="odoo"):
                name = f"{request['agent']}.md"
                installed = install_root / INSTALLED_AGENTS_DIRS[runtime] / name
                self.assertTrue(
                    installed.is_file(),
                    f"PC-12.a: el agente resuelto `{request['agent']}` no existe "
                    f"en el destino instalado de {runtime}.",
                )
                self.assertEqual(
                    installed.read_bytes(),
                    (staging / runtime / name).read_bytes(),
                    f"PC-12.a: el agente resuelto `{request['agent']}` instalado "
                    f"en {runtime} no procede de staging.",
                )
                self.assertNotEqual(
                    (staging / runtime / name).read_bytes(),
                    (staging / runtime / "cdad-implementer.md").read_bytes(),
                    f"PC-12.a: la variante Odoo {runtime}/{name} es idéntica al "
                    "agente genérico del mismo runtime: el dominio se perdió en "
                    "la generación.",
                )


# ===========================================================================
# (C/E) TestAgentBinding — publicación, coherencia y compatibilidad del
# destinatario (PC-06, PC-07, PC-08, INV-04; plan T5, AUDIT §11.2).
#
# Todo se observa por el CLI público (subproceso) sobre proyectos descartables;
# la implementación no se importa ni se lee. El `stack` vigente vive en
# `docs/.cdad-state.json` y es el único input de dominio que cada caso fija.
# ===========================================================================

CANONICAL_PACKETS = Path(".cdad") / "packets"
STACK_ABSENT = object()  # centinela: la clave `stack` no existe (D3)

OBSERVATION = {
    "runtime": "opencode",
    "model_configured": "glm-5.3-flash",
    "model_reported": "glm-5.3-flash",
    "started_at": "2026-10-31T00:00:00Z",
}


class AgentBindingCase(unittest.TestCase):
    """Proyecto descartable con el paquete publicado en la ruta canónica.

    El paquete se publica sin ``--out-dir`` para que ``prepare --replace-packet``
    resuelva el predecesor por la ruta que el flujo público usa. Las
    observaciones de despacho siguen la forma cerrada I8 ya declarada por
    004-002 (runtime, modelo, sesión, inicio y procedencia), sin inventar campos.
    """

    maxDiff = None

    # -- fixture ---------------------------------------------------------

    def project(
        self,
        *,
        role: str = "test-writer",
        substage: str = "red",
        stack: object = None,
        stack_absent: bool = False,
    ) -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-010-002-binding-")
        self.addCleanup(temp.cleanup)
        project = PrepareProject(Path(temp.name).resolve(), role, substage)
        self.apply_stack(project, stack, absent=stack_absent)
        return project

    def apply_stack(
        self, project: PrepareProject, stack: object, *, absent: bool = False
    ) -> None:
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        if absent:
            state.pop("stack", None)
        else:
            state["stack"] = stack
        project.pre_state = state
        project.state_path.write_text(
            json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def current_stack(self, project: PrepareProject) -> object:
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        return state["stack"] if "stack" in state else STACK_ABSENT

    def prepare_argv(self, project: PrepareProject) -> list[str]:
        """Argv de preparación ordinaria en la ruta canónica de paquetes."""
        argv = list(project.args())
        index = argv.index("--out-dir")
        del argv[index : index + 2]
        return argv

    def publish(self, project: PrepareProject) -> tuple[str, Path]:
        result = run_prepare(PACKET_CLI, *self.prepare_argv(project))
        self.assertEqual(
            result.returncode,
            0,
            msg="precondición (fixture): `prepare` debe publicar el paquete: "
            + result.stderr.decode(errors="replace")[-1500:],
        )
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        packet_id = str((state.get("active_packet") or {}).get("id") or "")
        self.assertTrue(
            packet_id,
            msg="precondición (fixture): `prepare` no registró `active_packet`",
        )
        packet_dir = project.root / CANONICAL_PACKETS / packet_id
        self.assertTrue(
            (packet_dir / "REQUEST.json").is_file(),
            msg="precondición (fixture): `prepare` no publicó "
            f"`{packet_dir / 'REQUEST.json'}`",
        )
        return packet_id, packet_dir

    # -- lecturas y escrituras del fixture -------------------------------

    @staticmethod
    def request_of(packet_dir: Path) -> dict:
        return json.loads((packet_dir / "REQUEST.json").read_text(encoding="utf-8"))

    @staticmethod
    def write_request(packet_dir: Path, request: dict) -> None:
        (packet_dir / "REQUEST.json").write_text(
            json.dumps(request, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def validate(self, project: PrepareProject, request_path: Path):
        return run_cli_bytes(
            PACKET_CLI,
            "validate-request",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
            "--request",
            str(request_path),
        )

    def render(self, project: PrepareProject, request_path: Path):
        return run_cli_bytes(
            PACKET_CLI,
            "render",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
            "--request",
            str(request_path),
        )

    def validate_packet(
        self, project: PrepareProject, request_path: Path, packet_path: Path
    ):
        return run_cli_bytes(
            PACKET_CLI,
            "validate-packet",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
            "--request",
            str(request_path),
            "--packet",
            str(packet_path),
        )

    def rebuild_packet(self, project: PrepareProject, packet_dir: Path) -> None:
        """Reconstruye el paquete canónico del request vigente.

        ``execution_context`` participa en la metadata del render: si el
        fixture lo retira para representar un histórico, el paquete publicado
        debe re-renderizarse (plan T5, «Adaptación de históricos»). No se
        compara contra el paquete moderno como si sus bytes fueran iguales.
        """
        rendered = self.render(project, packet_dir / "REQUEST.json")
        self.assertEqual(
            rendered.returncode,
            0,
            msg="precondición (fixture): el request histórico debe renderizar "
            "canónicamente: " + rendered.stderr.decode(errors="replace")[-1200:],
        )
        (packet_dir / "PACKET.md").write_bytes(rendered.stdout)

    def observation(self, project: PrepareProject, name: str, session: str) -> Path:
        path = project.root / name
        document = dict(OBSERVATION)
        document["session"] = session
        document["provenance"] = {
            "runtime": "reported by runtime",
            "model_reported": "orchestrator",
            "session": "orchestrator",
        }
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return path

    # -- operaciones del CLI ---------------------------------------------

    def record(
        self,
        project: PrepareProject,
        packet_id: str,
        attempt: str,
        observation_path: Path,
    ):
        return run_cli_bytes(
            PACKET_CLI,
            "prepare",
            "--project-root",
            str(project.root),
            "--record-dispatch",
            packet_id,
            "--attempt-id",
            attempt,
            "--input",
            str(observation_path),
        )

    def dispose(self, project: PrepareProject, packet_id: str):
        return run_cli_bytes(
            PACKET_CLI,
            "register-transition",
            "--project-root",
            str(project.root),
            "--transition",
            "disposition",
            "--packet",
            packet_id,
            "--resolution",
            "abandoned",
        )

    def replace(self, project: PrepareProject, packet_id: str):
        return run_cli_bytes(
            PACKET_CLI,
            "prepare",
            "--project-root",
            str(project.root),
            "--replace-packet",
            packet_id,
            "--reason",
            "010-002 T5 replacement",
        )

    # -- observaciones durables ------------------------------------------

    def execution_id(self, project: PrepareProject) -> str:
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        return str((state.get("execution") or {}).get("id") or "")

    def dispatch_dir(self, project: PrepareProject) -> Path:
        return (
            project.root
            / ".cdad"
            / "executions"
            / self.execution_id(project)
            / "dispatches"
        )

    def dispatch_files(self, project: PrepareProject) -> dict[str, bytes]:
        base = self.dispatch_dir(project)
        if not base.is_dir():
            return {}
        return {path.name: path.read_bytes() for path in sorted(base.glob("*.json"))}

    def successor(
        self, project: PrepareProject, predecessor: str
    ) -> tuple[str, Path, dict]:
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        successor_id = str((state.get("active_packet") or {}).get("id") or "")
        self.assertTrue(
            successor_id, msg="PC-06: el reemplazo no publicó un sucesor activo"
        )
        self.assertNotEqual(
            successor_id,
            predecessor,
            msg="PC-06: el reemplazo no publicó un paquete NUEVO",
        )
        packet_dir = project.root / CANONICAL_PACKETS / successor_id
        self.assertTrue(
            (packet_dir / "REQUEST.json").is_file(),
            msg=f"PC-06: el sucesor no publicó `{packet_dir / 'REQUEST.json'}`",
        )
        return successor_id, packet_dir, self.request_of(packet_dir)

    @staticmethod
    def diagnostic(result) -> str:
        return (result.stdout + result.stderr).decode("utf-8", errors="replace")


class TestAgentBinding(AgentBindingCase):
    """Promesa C: el destinatario es coherente sin reinterpretar la historia.

    Sin estos tests, el usuario podría recibir su encargo en un agente de otro
    rol (contraste estático ausente), en la variante de un dominio que ya no
    rige (contraste contextual ausente), o un reemplazo legítimo le publicaría
    un destinatario copiado del predecesor en vez del vigente. Los históricos
    sin ambos campos y las transiciones de recepción/repetición/write-ahead se
    protegen como controles: la corrección no puede endurecer de más.
    """

    # -- PC-06/PC-07(a) — publicación ordinaria --------------------------

    def test_ordinary_publication_publishes_derived_agent_and_context(self) -> None:
        """PC-06/PC-07(a): `prepare` publica el agente derivado del rol y del
        `stack` vigente (genérico para ausente/null/vacío; variante para
        `odoo`) y el `execution_context` canónico; el render del request válido
        no expone `agent`.

        Garantía por construcción (spec §2 D3; AUDIT §5): se observa el valor
        publicado, no una rama de rechazo que la interfaz no permite. Sin este
        test, el usuario no sabría a qué destinatario se publicó su encargo y
        un cambio de dominio podría quedar sin variante.

        Control declarado: hoy ya publica `agent` (006-005 U1c) y el render lo
        excluye; debe seguir verde.
        """
        cases = (
            ("null", None, False, "cdad-test-writer"),
            ("vacío", "", False, "cdad-test-writer"),
            ("ausente", None, True, "cdad-test-writer"),
            ("odoo", "odoo", False, "cdad-test-writer-odoo"),
        )
        for label, stack, absent, expected in cases:
            with self.subTest(stack=label):
                project = self.project(stack=stack, stack_absent=absent)
                _, packet_dir = self.publish(project)
                request = self.request_of(packet_dir)
                self.assertEqual(
                    request.get("agent"),
                    expected,
                    msg="PC-06 violada (§2 D3): la preparación ordinaria debe "
                    f"publicar el agente derivado del rol y del stack vigente "
                    f"({label!r}): vio {request.get('agent')!r}",
                )
                context = request.get("execution_context")
                self.assertIsInstance(
                    context,
                    str,
                    msg="PC-06 violada: la publicación nueva debe declarar "
                    f"`execution_context` textual; vio {context!r}",
                )
                self.assertTrue(
                    context.strip(),
                    msg="PC-06 violada: `execution_context` no puede ser vacío",
                )
                self.assertFalse(
                    Path(context).is_absolute(),
                    msg="PC-06 violada: `execution_context` es el localizador "
                    f"canónico relativo, no una ruta absoluta: {context!r}",
                )
                self.assertTrue(
                    context.endswith("/execution.json"),
                    msg="PC-06 violada: `execution_context` debe nombrar el "
                    f"documento canónico de la ejecución: {context!r}",
                )

                rendered = self.render(project, packet_dir / "REQUEST.json")
                self.assertEqual(
                    rendered.returncode,
                    0,
                    msg="PC-06/PC-08: el render del request publicado debe ser "
                    "válido: " + rendered.stderr.decode(errors="replace")[-1200:],
                )
                self.assertEqual(
                    rendered.stdout,
                    (packet_dir / "PACKET.md").read_bytes(),
                    msg="PC-06: el `PACKET.md` publicado debe ser el render "
                    "canónico del request",
                )
                metadata, _, _ = parse_packet(rendered.stdout.decode("utf-8"))
                self.assertNotIn(
                    "agent",
                    metadata,
                    msg="PC-08 violada: el render metadata expone `agent`; debe "
                    f"quedar excluido (metadata: {sorted(metadata)})",
                )

    # -- PC-06 — publicación por reemplazo -------------------------------

    def test_replacement_of_historical_successor_without_agent_rederives(
        self,
    ) -> None:
        """PC-06/PC-07(a) (B1/P-4): el reemplazo de un predecesor histórico
        admitido sin `execution_context` ni `agent` publica un sucesor con
        `execution_context` y el agente derivado del rol y del stack vigente,
        sin reescribir los bytes históricos.

        Sin este test, un reemplazo legítimo de un histórico quedaría sin
        destinatario (el sucesor copiaría la ausencia del predecesor) y el
        encargo no llegaría a ningún agente.

        RED hoy: el reemplazo copia el `agent` del predecesor; como el
        predecesor histórico no lo declara, el sucesor publica contexto sin
        agente.
        """
        project = self.project(stack=None)
        packet_id, packet_dir = self.publish(project)
        published = self.request_of(packet_dir)
        historical = dict(published)
        historical.pop("agent", None)
        historical.pop("execution_context", None)
        self.write_request(packet_dir, historical)
        self.rebuild_packet(project, packet_dir)
        historical_bytes = (packet_dir / "REQUEST.json").read_bytes()

        record = self.record(
            project,
            packet_id,
            "attempt-historical",
            self.observation(project, "obs-historical.json", "ses-010-002-historical"),
        )
        self.assertEqual(
            record.returncode,
            0,
            msg="precondición (P-3): el histórico sin contexto ni agente debe "
            "registrar un intento nuevo: "
            + record.stderr.decode(errors="replace")[-1200:],
        )
        disposed = self.dispose(project, packet_id)
        self.assertEqual(
            disposed.returncode,
            0,
            msg="precondición (007-002): la disposición del predecesor debe "
            "registrarse: " + disposed.stderr.decode(errors="replace")[-1200:],
        )

        # Publicación nueva (P-4): el sucesor deriva el agente del estado
        # vigente, no lo copia del predecesor.
        self.apply_stack(project, "odoo")
        replacement = self.replace(project, packet_id)
        self.assertEqual(
            replacement.returncode,
            0,
            msg="PC-06 violada: el reemplazo de un predecesor histórico "
            "dispuesto debe publicar el sucesor (rc=0): "
            + replacement.stderr.decode(errors="replace")[-1500:],
        )
        _, _, successor = self.successor(project, packet_id)
        self.assertEqual(
            successor.get("agent"),
            "cdad-test-writer-odoo",
            msg="PC-06 violada (P-4/B1): el sucesor debe REDERIVAR el agente "
            "del rol y del stack vigente (`odoo`), no copiar el del "
            f"predecesor (que no lo tenía): vio {successor.get('agent')!r}",
        )
        successor_context = successor.get("execution_context")
        self.assertIsInstance(
            successor_context,
            str,
            msg="PC-06 violada: el sucesor de un histórico debe publicar "
            f"`execution_context`; vio {successor_context!r}",
        )
        self.assertTrue(successor_context.strip())
        self.assertEqual(
            (packet_dir / "REQUEST.json").read_bytes(),
            historical_bytes,
            msg="PC-06 violada: el reemplazo reescribió los bytes históricos "
            "del request predecesor",
        )

    def test_replacement_after_stack_change_rederives_current_stack(self) -> None:
        """PC-06/PC-07(a) (R5/P-4): tras cambiar solo el `stack`, el sucesor
        publica el agente del stack vigente, no una copia del anterior, y los
        bytes del request predecesor quedan intactos.

        Sin este test, un cambio de dominio publicaría un sucesor que iría al
        dominio anterior: el encargo llegaría al agente equivocado.

        RED hoy: el reemplazo copia el agente del predecesor.
        """
        project = self.project(stack="odoo")
        packet_id, packet_dir = self.publish(project)
        predecessor = self.request_of(packet_dir)
        predecessor_agent = predecessor.get("agent")
        self.assertEqual(
            predecessor_agent,
            "cdad-test-writer-odoo",
            msg="precondición (fixture): el predecesor declara el agente del "
            f"stack original; vio {predecessor_agent!r}",
        )
        predecessor_bytes = (packet_dir / "REQUEST.json").read_bytes()

        record = self.record(
            project,
            packet_id,
            "attempt-predecessor",
            self.observation(project, "obs-predecessor.json", "ses-010-002-pred"),
        )
        self.assertEqual(
            record.returncode,
            0,
            msg="precondición: el intento del predecesor se registra: "
            + record.stderr.decode(errors="replace")[-1200:],
        )
        disposed = self.dispose(project, packet_id)
        self.assertEqual(
            disposed.returncode,
            0,
            msg="precondición: la disposición se registra: "
            + disposed.stderr.decode(errors="replace")[-1200:],
        )

        self.apply_stack(project, None)
        self.assertIsNone(
            self.current_stack(project),
            msg="precondición (R7): el stack vigente cambió a null antes del "
            "reemplazo",
        )
        expected = "cdad-test-writer"
        self.assertNotEqual(
            predecessor_agent,
            expected,
            msg="precondición (R5): predecesor y esperado deben diferir para "
            "que la copia no pase por derivación",
        )

        replacement = self.replace(project, packet_id)
        self.assertEqual(
            replacement.returncode,
            0,
            msg="PC-06 violada: el reemplazo tras cambiar el stack debe "
            "publicar el sucesor: "
            + replacement.stderr.decode(errors="replace")[-1500:],
        )
        _, _, successor = self.successor(project, packet_id)
        self.assertEqual(
            successor.get("agent"),
            expected,
            msg="PC-06 violada (R5/P-4): el sucesor debe publicar el agente del "
            "stack VIGENTE, no una copia del anterior "
            f"({predecessor_agent!r}): vio {successor.get('agent')!r}",
        )
        self.assertEqual(
            (packet_dir / "REQUEST.json").read_bytes(),
            predecessor_bytes,
            msg="PC-06 violada: el reemplazo reescribió los bytes históricos "
            "del request predecesor",
        )

    # -- PC-07(b) — contraste estático de rol ----------------------------

    def test_static_role_contrast_rejects_foreign_agent_and_does_not_evaluate_stack(
        self,
    ) -> None:
        """PC-07(b)/PC-08 (P-1): `validate-request` rechaza un `agent` de otro
        rol, con diagnóstico que nombra rol, agente recibido y familia
        esperada, y declara que el `stack` no se evalúa; `render` no produce un
        paquete válido y `validate-packet` tampoco; no se registra despacho.

        El contraste es estático: un agente del MISMO rol con otro sufijo no
        se rechaza en lectura (el stack posterior no invalida la lectura), y la
        coincidencia parcial del nombre del rol no basta.

        Sin este test, un agente de otro rol recibiría el trabajo y el
        diagnóstico no permitiría distinguir este rechazo del contextual.

        RED hoy: la validación compartida no contrasta el rol y acepta un
        agente de otro rol.
        """
        project = self.project(stack=None)
        packet_id, packet_dir = self.publish(project)
        request = self.request_of(packet_dir)
        # Un stack posterior distinto del agente genérico: el contraste
        # estático no debe consultarlo.
        self.apply_stack(project, "odoo")

        same_role = self.validate(project, packet_dir / "REQUEST.json")
        self.assertEqual(
            same_role.returncode,
            0,
            msg="PC-07(b) violada: un `agent` del mismo rol no se rechaza en "
            "lectura solo por diferir del stack posterior: "
            + same_role.stderr.decode(errors="replace")[-1200:],
        )
        # La verificación de un paquete ya publicado tampoco introduce el
        # contraste contextual (PC-08: se conserva el estático).
        verified_after_change = self.validate_packet(
            project, packet_dir / "REQUEST.json", packet_dir / "PACKET.md"
        )
        self.assertEqual(
            verified_after_change.returncode,
            0,
            msg="PC-08 violada: cambiar solo el stack invalidó la "
            "VERIFICACIÓN de un paquete ya publicado (el contraste "
            "contextual no debe aplicarse en lectura): "
            + verified_after_change.stderr.decode(errors="replace")[-1200:],
        )

        foreign = dict(request)
        foreign["agent"] = "cdad-reviewer"
        self.write_request(packet_dir, foreign)
        try:
            rejected = self.validate(project, packet_dir / "REQUEST.json")
        finally:
            self.write_request(packet_dir, request)
        self.assertNotEqual(
            rejected.returncode,
            0,
            msg="PC-07(b) violada: `validate-request` aceptó un agente de otro "
            "rol (el contraste estático agente↔rol no existe o no se aplica)",
        )
        diagnostic = self.diagnostic(rejected).lower()
        for token in ("test-writer", "cdad-reviewer", "cdad-test-writer"):
            self.assertIn(
                token,
                diagnostic,
                msg="PC-07(b)/P-1 violada: el diagnóstico debe nombrar el rol "
                f"declarado, el agente recibido y la familia esperada "
                f"(falta {token!r}): {diagnostic[-1200:]!r}",
            )
        self.assertRegex(
            diagnostic,
            r"(?s)stack.{0,200}(no|not|never|sin|nunca)|(no|not|never|sin|nunca)"
            r".{0,200}stack",
            msg="PC-07(b)/P-1 violada: el diagnóstico estático debe declarar "
            "que el `stack` NO se evalúa (sin esa declaración, un rechazo "
            f"estático preemptor pasaría por contextual): {diagnostic[-1200:]!r}",
        )

        # Se reescribe solo el agente sobre el request publicado; el paquete
        # canónico no cambia porque el render excluye `agent`.
        self.write_request(packet_dir, foreign)
        try:
            rendered = self.render(project, packet_dir / "REQUEST.json")
            validated_packet = self.validate_packet(
                project, packet_dir / "REQUEST.json", packet_dir / "PACKET.md"
            )
        finally:
            self.write_request(packet_dir, request)
        self.assertNotEqual(
            rendered.returncode,
            0,
            msg="PC-07(b) violada: `render` produjo un paquete con un agente "
            "de otro rol",
        )
        self.assertNotIn(
            b"---cdad-packet-json",
            rendered.stdout,
            msg="PC-07(b) violada: `render` emitió un paquete válido para un "
            "request con agente de otro rol",
        )
        self.assertNotEqual(
            validated_packet.returncode,
            0,
            msg="PC-07(b)/D3 violada: la validación de un paquete publicado no "
            "aplica el contraste estático de rol",
        )

        before = self.dispatch_files(project)
        self.write_request(packet_dir, foreign)
        try:
            recorded = self.record(
                project,
                packet_id,
                "attempt-foreign-role",
                self.observation(project, "obs-foreign.json", "ses-010-002-foreign"),
            )
        finally:
            self.write_request(packet_dir, request)
        self.assertNotEqual(
            recorded.returncode,
            0,
            msg="PC-07(b) violada: un request con agente de otro rol registró "
            "un despacho",
        )
        self.assertEqual(
            self.dispatch_files(project),
            before,
            msg="PC-07(b) violada: el rechazo estático dejó un registro de "
            "despacho nuevo",
        )

        accepted = ("cdad-test-writer", "cdad-test-writer-odoo")
        refused = ("cdad-test-write", "cdad-test-writerx")
        for agent in accepted + refused:
            mutated = dict(request)
            mutated["agent"] = agent
            self.write_request(packet_dir, mutated)
            try:
                result = self.validate(project, packet_dir / "REQUEST.json")
            finally:
                self.write_request(packet_dir, request)
            if agent in accepted:
                self.assertEqual(
                    result.returncode,
                    0,
                    msg="PC-07(b)/P-1 violada: el nombre genérico exacto "
                    "`cdad-<rol>` y el prefijo completo con sufijo no vacío "
                    f"deben validar; {agent!r} fue rechazado: "
                    + result.stderr.decode(errors="replace")[-800:],
                )
            else:
                self.assertNotEqual(
                    result.returncode,
                    0,
                    msg="PC-07(b)/P-1 violada: una coincidencia parcial del "
                    f"nombre del rol no basta; {agent!r} validó",
                )

    # -- PC-07(c) — contraste contextual de stack ------------------------

    def test_contextual_contrast_rejects_a_new_intent_with_wrong_stack_agent(
        self,
    ) -> None:
        """PC-07(c)/PC-08 (P-2/R2): tras cambiar solo el `stack`, un intento
        NUEVO con el agente declarado anterior (mismo rol, otro dominio) falla
        antes de publicar el registro, con diagnóstico que nombra rol, stack y
        agente esperado, sin efectos nuevos.

        La publicación nueva es garantía por construcción (los valores
        derivados se verifican en los tests de publicación); esta rama
        observable es el registro del intento nuevo. Sin este test, un encargo
        se despacharía a un dominio que ya no corresponde.

        RED hoy: el registro no aplica contraste contextual y acepta el
        intento.
        """
        project = self.project(stack=None)
        packet_id, packet_dir = self.publish(project)
        request = self.request_of(packet_dir)
        self.assertEqual(
            request.get("agent"),
            "cdad-test-writer",
            msg="precondición (fixture): el agente publicado es el genérico "
            f"(stacks distintos se distinguen); vio {request.get('agent')!r}",
        )
        # Cambia SOLO el stack durante la vida del paquete: el agente
        # declarado sigue siendo del mismo rol (no lo preempta el contraste
        # estático) pero ya no corresponde al dominio vigente.
        self.apply_stack(project, "odoo")
        self.assertEqual(self.current_stack(project), "odoo")

        before_files = self.dispatch_files(project)
        before_request = (packet_dir / "REQUEST.json").read_bytes()
        before_packet = (packet_dir / "PACKET.md").read_bytes()
        state_before = json.loads(project.state_path.read_text(encoding="utf-8"))
        status_before = (state_before.get("active_packet") or {}).get("status")

        recorded = self.record(
            project,
            packet_id,
            "attempt-new-intent",
            self.observation(project, "obs-new-intent.json", "ses-010-002-new"),
        )
        self.assertNotEqual(
            recorded.returncode,
            0,
            msg="PC-07(c) violada (R2): un intento nuevo con agente declarado "
            "del stack anterior fue aceptado tras cambiar solo el stack",
        )
        diagnostic = self.diagnostic(recorded).lower()
        for token in ("test-writer", "odoo", "cdad-test-writer-odoo"):
            self.assertIn(
                token,
                diagnostic,
                msg="PC-07(c) violada: el diagnóstico contextual debe nombrar "
                f"rol, stack y agente esperado (falta {token!r}): "
                f"{diagnostic[-1200:]!r}",
            )
        self.assertIn(
            "stack",
            diagnostic,
            msg="PC-07(c) violada: el diagnóstico contextual debe nombrar el "
            f"`stack` vigente (discrimina del estático): {diagnostic[-1200:]!r}",
        )

        self.assertEqual(
            self.dispatch_files(project),
            before_files,
            msg="PC-07(c) violada: el rechazo publicó un registro de despacho",
        )
        self.assertEqual(
            (packet_dir / "REQUEST.json").read_bytes(),
            before_request,
            msg="PC-07(c) violada: el rechazo alteró el request publicado",
        )
        self.assertEqual(
            (packet_dir / "PACKET.md").read_bytes(),
            before_packet,
            msg="PC-07(c) violada: el rechazo alteró el paquete publicado",
        )
        state_after = json.loads(project.state_path.read_text(encoding="utf-8"))
        self.assertEqual(
            (state_after.get("active_packet") or {}).get("status"),
            status_before,
            msg="PC-07(c) violada: el rechazo cambió el estado del paquete",
        )

    # -- PC-08/P-3 — histórico sin contexto ni agente --------------------

    def test_historical_without_both_fields_records_a_new_intent_without_destination_contrast(
        self,
    ) -> None:
        """PC-08/P-3/N6: un request histórico admitido sin `execution_context`
        ni `agent` registra un intento NUEVO aunque el stack haya cambiado: no
        hay agente declarado que contrastar y no se deriva ni se sustituye uno
        en silencio.

        Sin este test, la corrección podría rechazar históricos legítimos al
        endurecer el contraste contextual, o inventarles un destinatario.

        Control declarado: hoy el registro admite el histórico; debe seguir
        verde y sin ganar campos.
        """
        project = self.project(stack=None)
        packet_id, packet_dir = self.publish(project)
        published = self.request_of(packet_dir)
        historical = dict(published)
        historical.pop("agent", None)
        historical.pop("execution_context", None)
        self.write_request(packet_dir, historical)
        self.rebuild_packet(project, packet_dir)
        historical_bytes = (packet_dir / "REQUEST.json").read_bytes()

        # Un stack posterior no debe disparar contraste ni derivación: no hay
        # agente declarado.
        self.apply_stack(project, "odoo")
        self.assertEqual(self.current_stack(project), "odoo")

        before = self.dispatch_files(project)
        recorded = self.record(
            project,
            packet_id,
            "attempt-historical-new",
            self.observation(project, "obs-historical-new.json", "ses-010-002-hist"),
        )
        self.assertEqual(
            recorded.returncode,
            0,
            msg="PC-08/P-3 violada: el request histórico sin contexto ni "
            "agente no pudo registrar un intento nuevo: "
            + recorded.stderr.decode(errors="replace")[-1200:],
        )
        after = self.dispatch_files(project)
        self.assertEqual(
            len(after),
            len(before) + 1,
            msg="PC-08/P-3 violada: el registro del intento nuevo no quedó "
            f"durable (registros: {sorted(after)})",
        )
        record_path = self.dispatch_dir(project) / "attempt-historical-new.json"
        self.assertTrue(
            record_path.is_file(),
            msg=f"PC-08/P-3 violada: falta el registro durable {record_path.name}",
        )
        record = json.loads(record_path.read_text(encoding="utf-8"))
        self.assertNotIn(
            "agent",
            record,
            msg="PC-08/P-3 violada: el registro derivó o sustituyó un agente "
            f"en silencio (claves: {sorted(record)})",
        )
        self.assertEqual(
            record.get("session"),
            "ses-010-002-hist",
            msg="PC-08/P-3 violada: el registro no corresponde a la "
            "observación del intento nuevo",
        )
        self.assertEqual(
            (packet_dir / "REQUEST.json").read_bytes(),
            historical_bytes,
            msg="PC-08/P-3 violada: el registro alteró el request histórico "
            "(le agregó `agent` o `execution_context`)",
        )
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        self.assertEqual(
            (state.get("active_packet") or {}).get("status"),
            "dispatched",
            msg="PC-08/P-3 violada: el paquete no quedó `dispatched` tras el "
            f"registro: {(state.get('active_packet') or {}).get('status')!r}",
        )

    # -- PC-08/O2 — presencia de agent y render --------------------------

    def test_context_without_agent_is_rejected_on_validation_and_publication(
        self,
    ) -> None:
        """PC-08/O2: un request con `execution_context` y sin `agent` se
        rechaza en la validación, no renderiza paquete válido y no registra
        despacho; el histórico con AMBOS campos ausentes sigue admitido.

        Sin este test, un request con contexto quedaría sin destinatario y la
        regla de presencia no protegería el vínculo agente↔contexto.

        RED hoy: la validación, el render y el registro aceptan contexto sin
        agente.
        """
        project = self.project(stack=None)
        packet_id, packet_dir = self.publish(project)
        request = self.request_of(packet_dir)
        self.assertIn("agent", request)
        self.assertIn("execution_context", request)

        without_agent = dict(request)
        without_agent.pop("agent", None)
        self.write_request(packet_dir, without_agent)
        validation = self.validate(project, packet_dir / "REQUEST.json")
        self.assertNotEqual(
            validation.returncode,
            0,
            msg="PC-08/O2 violada: un request con `execution_context` y sin "
            "`agent` fue aceptado por `validate-request`",
        )
        self.assertIn(
            "agent",
            self.diagnostic(validation).lower(),
            msg="PC-08/O2 violada: el rechazo no nombra el campo `agent` "
            f"ausente: {self.diagnostic(validation)[-1000:]!r}",
        )
        rendered = self.render(project, packet_dir / "REQUEST.json")
        self.assertNotEqual(
            rendered.returncode,
            0,
            msg="PC-08/O2 violada: `render` produjo un paquete con contexto "
            "sin agente",
        )
        self.assertNotIn(
            b"---cdad-packet-json",
            rendered.stdout,
            msg="PC-08/O2 violada: `render` emitió un paquete válido para un "
            "request con contexto y sin agente",
        )
        before = self.dispatch_files(project)
        recorded = self.record(
            project,
            packet_id,
            "attempt-context-without-agent",
            self.observation(project, "obs-no-agent.json", "ses-010-002-no-agent"),
        )
        self.assertNotEqual(
            recorded.returncode,
            0,
            msg="PC-08/O2 violada: un request con contexto y sin agente "
            "registró un despacho",
        )
        self.assertEqual(
            self.dispatch_files(project),
            before,
            msg="PC-08/O2 violada: el rechazo de presencia dejó un registro "
            "de despacho nuevo",
        )

        # El histórico admitido tiene AMBOS campos ausentes (D3/P-3).
        historical = dict(request)
        historical.pop("agent", None)
        historical.pop("execution_context", None)
        self.write_request(packet_dir, historical)
        self.rebuild_packet(project, packet_dir)
        admitted = self.validate(project, packet_dir / "REQUEST.json")
        self.assertEqual(
            admitted.returncode,
            0,
            msg="PC-08 violada: el histórico sin contexto ni agente dejó de "
            "admitirse estructuralmente: "
            + admitted.stderr.decode(errors="replace")[-1200:],
        )
        rendered = self.render(project, packet_dir / "REQUEST.json")
        self.assertEqual(
            rendered.returncode,
            0,
            msg="PC-08 violada: el histórico admitido no renderiza paquete "
            "canónico: " + rendered.stderr.decode(errors="replace")[-1200:],
        )
        metadata, _, _ = parse_packet(rendered.stdout.decode("utf-8"))
        self.assertNotIn("agent", metadata)
        self.assertNotIn(
            "execution_context",
            metadata,
            msg="PC-08: el render del histórico no debe reintroducir "
            "`execution_context` en la metadata",
        )

    def test_agent_is_excluded_from_render_between_valid_requests(self) -> None:
        """PC-08 (R3): el render no cambia entre dos requests VÁLIDOS que
        difieren solo en `agent`, y la metadata no lo declara.

        La línea base es el request válido sin `agent` (sin contexto declarado):
        quitar `execution_context` cambia la metadata, así que el paquete
        moderno no se usa como si sus bytes fueran iguales (plan T5).

        Sin este test, un campo de transporte entraría al render y rompería la
        compatibilidad de bytes entre requests válidos.

        Control declarado: hoy el render ya excluye `agent`; debe seguir verde.
        """
        project = self.project(stack=None)
        _, packet_dir = self.publish(project)
        request = self.request_of(packet_dir)
        self.assertEqual(request.get("agent"), "cdad-test-writer")

        baseline = dict(request)
        baseline.pop("execution_context", None)
        without_agent = dict(baseline)
        without_agent.pop("agent", None)
        with_path = packet_dir / "REQUEST-with-agent-no-context.json"
        without_path = packet_dir / "REQUEST-without-agent.json"
        self.write_request(packet_dir, baseline)
        with_path.write_bytes((packet_dir / "REQUEST.json").read_bytes())
        self.write_request(packet_dir, without_agent)
        without_path.write_bytes((packet_dir / "REQUEST.json").read_bytes())
        self.write_request(packet_dir, request)

        for path in (with_path, without_path):
            validation = self.validate(project, path)
            self.assertEqual(
                validation.returncode,
                0,
                msg="precondición (R3): ambos requests comparados deben ser "
                "válidos: " + validation.stderr.decode(errors="replace")[-1000:],
            )

        with_agent = self.render(project, with_path)
        without = self.render(project, without_path)
        self.assertEqual(
            with_agent.returncode,
            0,
            msg="PC-08 violada: el request válido con `agent` no renderiza: "
            + with_agent.stderr.decode(errors="replace")[-1000:],
        )
        self.assertEqual(
            without.returncode,
            0,
            msg="PC-08 violada: el request válido sin `agent` no renderiza: "
            + without.stderr.decode(errors="replace")[-1000:],
        )
        self.assertEqual(
            with_agent.stdout,
            without.stdout,
            msg="PC-08 violada: `agent` entró al render — los bytes difieren "
            "entre dos requests válidos que solo difieren en el campo",
        )
        metadata, _, _ = parse_packet(with_agent.stdout.decode("utf-8"))
        self.assertNotIn(
            "agent",
            metadata,
            msg="PC-08 violada: la metadata del render declara `agent` "
            f"(claves: {sorted(metadata)})",
        )

    # -- PC-08/P-2 — repetición idéntica --------------------------------

    def test_identical_repetition_after_stack_change_stays_idempotent(self) -> None:
        """PC-08/P-2 (R7): tras cambiar solo el `stack`, repetir un registro
        IDÉNTICO conserva rc=0, los bytes y el estado; reutilizar el mismo
        identificador con datos distintos sigue rechazado sin sobrescribir.

        Sin este test, la excepción temporal podría convertirse en una
        revalidación del stack sobre registros ya hechos (rompiendo la
        idempotencia) o en una relajación general del ledger.

        Control declarado: hoy la repetición es idempotente y el conflicto se
        rechaza; debe seguir verde con la excepción.
        """
        project = self.project(stack=None)
        packet_id, _ = self.publish(project)
        observation = self.observation(
            project, "obs-idempotent.json", "ses-010-002-idem"
        )
        first = self.record(project, packet_id, "attempt-idem", observation)
        self.assertEqual(
            first.returncode,
            0,
            msg="precondición: el registro inicial se publica: "
            + first.stderr.decode(errors="replace")[-1200:],
        )
        record_path = self.dispatch_dir(project) / "attempt-idem.json"
        self.assertTrue(record_path.is_file())
        bytes_before = record_path.read_bytes()

        # Cambia SOLO el stack después de que el registro existe.
        self.apply_stack(project, "odoo")
        self.assertEqual(
            self.current_stack(project),
            "odoo",
            msg="precondición (R7): el stack vigente cambió de verdad",
        )
        repeat = self.record(project, packet_id, "attempt-idem", observation)
        self.assertEqual(
            repeat.returncode,
            0,
            msg="PC-08/P-2 violada: la repetición idéntica de un registro fue "
            "rechazada tras cambiar solo el stack: "
            + repeat.stderr.decode(errors="replace")[-1200:],
        )
        self.assertEqual(
            record_path.read_bytes(),
            bytes_before,
            msg="PC-08/P-2 violada: la repetición idéntica cambió los bytes del "
            "registro",
        )
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        self.assertEqual(
            (state.get("active_packet") or {}).get("status"),
            "dispatched",
            msg="PC-08/P-2 violada: la repetición idéntica no conservó el "
            "estado `dispatched`",
        )

        # Discriminador: la excepción no relaja el ledger. Un identificador
        # reutilizado con datos distintos se rechaza sin sobrescribir.
        conflict = self.record(
            project,
            packet_id,
            "attempt-idem",
            self.observation(project, "obs-idem-other.json", "ses-010-002-other"),
        )
        self.assertNotEqual(
            conflict.returncode,
            0,
            msg="PC-08 violada: reutilizar el identificador con datos "
            "distintos fuera de la finalización admitida fue aceptado",
        )
        self.assertEqual(
            record_path.read_bytes(),
            bytes_before,
            msg="PC-08 violada: el registro contradictorio sobrescribió el "
            "intento existente",
        )


class TestAgentBindingReception(EstablishedProjectCase):
    """PC-08 (R9): la recepción de un paquete ya publicado y despachado no
    reevalúa su agente contra un stack cambiado; se conserva el contraste
    estático de rol y el recibo durable.

    Sin este test, un cambio de dominio durante la ejecución invalidaría la
    recepción de un trabajo ya despachado. Control declarado: hoy la recepción
    no aplica contraste temporal; debe seguir verde con la corrección.
    """

    def test_reception_after_stack_change_keeps_the_static_contrast_only(
        self,
    ) -> None:
        """PC-08/R9: secuencia completa `prepare` → `record-dispatch` →
        cambiar solo el stack → `receive`: rc=0 y recibo durable.

        El agente del request publicado es del mismo rol (`cdad-test-writer`)
        y el stack vigente pasa a `odoo`: solo el contraste estático puede
        aplicarse en la recepción, y debe pasar.
        """
        self.new_dispatched_project()
        request = json.loads(self.request_path.read_text(encoding="utf-8"))
        self.assertEqual(
            request.get("agent"),
            "cdad-test-writer",
            msg="precondición (fixture): el paquete despachado declara el "
            f"agente del rol; vio {request.get('agent')!r}",
        )
        state_path = self.root / "docs" / ".cdad-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stack"] = "odoo"
        state_path.write_text(
            json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self.assertEqual(
            json.loads(state_path.read_text(encoding="utf-8")).get("stack"),
            "odoo",
            msg="precondición (R7): el stack vigente cambió de verdad antes "
            "de la recepción",
        )

        parts = self.write_staged_parts()
        self.assertEqual(parts, STAGED_PARTS)
        self.write_manifest(changes=[])
        descriptor = self.write_descriptor(
            self.build_descriptor(parts=parts, observed=self.observed_changes())
        )
        proc = self.run_receive(descriptor)
        self.assertEqual(
            proc.returncode,
            0,
            msg="PC-08/R9 violada: la recepción de un paquete ya publicado y "
            "despachado se rechazó por el stack cambiado (el contraste "
            "contextual no se reaplica en recepción): "
            + proc.stderr.decode("utf-8", errors="replace")[-1200:],
        )
        self.assertTrue(
            self.receipt_path().is_file(),
            msg="PC-08/R9 violada: la recepción tras cambiar solo el stack no "
            "produjo recibo durable",
        )


SLOW_CLIENT_SOURCE = r'''#!/usr/bin/env python3
"""Cliente lento del fixture 010-002 T5 (NO es producto).

Duerme antes de escribir la fila idle y el texto final, de modo que el test
pueda cambiar SOLO el stack del estado mientras el intento ya está en vuelo.
"""
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

_STORE = Path(%STORE%)
_VERSION = %VERSION%
_MODEL = %MODEL%
_SLEEP = %SLEEP%


def _option(name):
    argv = sys.argv[1:]
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith(name + "="):
            return token[len(name) + 1:]
    return None


if "--version" in sys.argv[1:]:
    sys.stdout.write(_VERSION + "\n")
    sys.stdout.flush()
    sys.exit(0)

session_id = _option("--session") or ""
agent_id = _option("--agent") or ""
time.sleep(_SLEEP)
now_ms = int(time.time() * 1000)
connection = sqlite3.connect(str(_STORE))
try:
    connection.execute(
        "INSERT INTO session_v2 (id, parent_id, agent, model, time_created,"
        " time_idle, idle_outcome, directory) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (session_id, None, agent_id, _MODEL, now_ms - 1000, now_ms,
         "succeeded", os.environ.get("PWD") or os.getcwd()))
    for seq, kind, text in (
        (1, "user", "010-002 fixture"),
        (2, "assistant", "# 010-002 final\n"),
    ):
        connection.execute(
            "INSERT INTO session_message (id, session_id, type, seq, data)"
            " VALUES (?, ?, ?, ?, ?)",
            ("msg-010-002-%d-%s" % (seq, session_id), session_id, kind, seq,
             json.dumps({"content": [{"type": "text", "text": text}]},
                        sort_keys=True)))
    connection.commit()
finally:
    connection.close()
'''


class TestAgentBindingWriteAheadFinalization(U65WriteAheadCase):
    """PC-08/P-2/N2: la finalización válida del write-ahead de un intento ya
    iniciado no se reaplica al contraste contextual tras cambiar solo el stack.

    Se reutiliza el patrón público del adaptador externo con runtime falso
    (A3): el cliente duerme antes de escribir la fila idle, el test cambia
    SOLO el `stack` mientras el intento está en vuelo y la terminación debe
    completar el MISMO registro provisional una vez, con identidad fija.

    Sin este test, un cambio de dominio durante la ejecución impediría
    completar un trabajo ya despachado. Control declarado: hoy completa; debe
    seguir verde con la excepción.
    """

    def write_fake_binary(self) -> Path:
        path = self.fixture_dir / "bin" / "opencode-010002-slow"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            SLOW_CLIENT_SOURCE.replace(
                "%STORE%", json.dumps(str(self.store_path))
            )
            .replace("%VERSION%", json.dumps(U65_FAKE_VERSION))
            .replace("%MODEL%", json.dumps(U65_ROW_MODEL))
            .replace("%SLEEP%", "3"),
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path

    def state_document(self) -> dict:
        return json.loads(
            (self.project["root"] / "docs" / ".cdad-state.json").read_text(
                encoding="utf-8"
            )
        )

    def project_stack(self) -> object:
        state = self.state_document()
        return state["stack"] if "stack" in state else STACK_ABSENT

    def write_project_stack(self, value: object) -> None:
        path = self.project["root"] / "docs" / ".cdad-state.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["stack"] = value
        path.write_text(
            json.dumps(document, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def request_bytes(self) -> bytes:
        return (
            self.project["root"]
            / CANONICAL_PACKETS
            / str(self.project["packet_id"])
            / "REQUEST.json"
        ).read_bytes()

    def test_write_ahead_finalization_after_stack_change_completes_once(
        self,
    ) -> None:
        """PC-08/P-2/N2: write-ahead iniciado con stack A → cambio solo de
        stack durante la ejecución → terminación válida del MISMO intento: un
        único registro final, identidad fija, sin rechazo por el stack.

        R7: se asserta el stack antes y después del cambio, de modo que el
        test no pase trivialmente sin haber cambiado el dominio.
        """
        self.assertIsNone(
            self.project_stack(),
            msg="precondición (R7): el intento se publica con el stack A (null)",
        )
        request_before = self.request_bytes()

        proc = self.start_dispatch()
        self.track_client()
        provisional = self.wait_for(
            lambda: self.provisional_records() or None, timeout=30
        )
        self.assertTrue(
            provisional,
            msg="precondición (U6-5/E4): el write-ahead debe existir antes de "
            "lanzar el cliente; no apareció un registro provisional",
        )
        self.assertEqual(
            len(provisional),
            1,
            msg="precondición (PD-1): el intento inicia con UN registro "
            f"provisional: {sorted(provisional)}",
        )
        provisional_stem, provisional_doc = next(iter(provisional.items()))
        self.assert_provisional_shape(provisional_doc, "PC-08 write-ahead")

        # Cambia SOLO el stack con el intento ya en vuelo.
        self.write_project_stack("odoo")
        self.assertEqual(
            self.project_stack(),
            "odoo",
            msg="precondición (R7): el stack vigente cambió de verdad durante "
            "la ejecución",
        )

        stdout, stderr = proc.communicate(timeout=120)
        completed = subprocess.CompletedProcess(
            proc.args, proc.returncode, stdout, stderr
        )
        out = self.envelope(completed, "PC-08 write-ahead")
        self.assertEqual(
            out.get("termination"),
            "completed",
            msg="PC-08/P-2 violada: el cambio de stack impidió la terminación "
            f"válida del intento ya iniciado: {out.get('diagnosis')!r}",
        )
        final_stem, final_doc = self.single_record()
        self.assertEqual(
            final_stem,
            provisional_stem,
            msg="PC-08/P-2 violada: la finalización no completó el MISMO "
            f"intento (provisional {provisional_stem!r}, final "
            f"{final_stem!r})",
        )
        self.assert_final_record(final_doc, "PC-08 write-ahead")
        self.assert_no_rejection_note(out, final_doc, "PC-08 write-ahead")
        self.assertEqual(
            self.request_bytes(),
            request_before,
            msg="PC-08/P-2 violada: la finalización alteró el request publicado",
        )


# ===========================================================================
# (E) TestRequestSchema — el asset publicado describe forma y compatibilidad
# (PC-10; plan T5, AUDIT §10 R6). La evaluación es real: motor `jsonschema`,
# `check_schema` e `iter_errors` sobre instancias construidas desde un request
# publicado por `prepare`; no se inspeccionan solo nombres de propiedades.
# ===========================================================================

SCHEMA_PATH = REPO_ROOT / "skills" / "cdad-cycle" / "assets" / "packet-request.schema.json"


class TestRequestSchema(AgentBindingCase):
    """Promesa E: el esquema declara los campos publicados y su compatibilidad.

    Sin estos tests, el esquema publicado rechazaría requests válidos (campos
    admitidos por el CLI) o aceptaría contexto sin agente, y un consumidor
    obtendría un veredicto distinto del CLI. El esquema describe **forma** y no
    sustituye el contraste estático de rol ni el contextual de stack, que son
    comprobaciones del CLI.
    """

    def validator(self):
        if jsonschema is None:
            self.skipTest(
                "bloqueo de entorno (no defecto del producto): el motor real "
                "de JSON Schema (`jsonschema`) no está disponible"
            )
        self.assertTrue(
            SCHEMA_PATH.is_file(),
            msg="PC-10 violada: el asset publicado del request no existe en "
            f"`{relative(SCHEMA_PATH)}`",
        )
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator_class = jsonschema.validators.validator_for(schema)
        validator_class.check_schema(schema)
        return validator_class(schema), schema

    def current_request(self) -> dict:
        project = self.project(stack=None)
        _, packet_dir = self.publish(project)
        request = self.request_of(packet_dir)
        self.assertEqual(
            request.get("agent"),
            "cdad-test-writer",
            msg="precondición (fixture): el request publicado declara el "
            "agente derivado (006-005 U1c)",
        )
        self.assertIn(
            "execution_context",
            request,
            msg="precondición (fixture): el request publicado declara el "
            "localizador canónico (010-004)",
        )
        return request

    def test_schema_accepts_valid_current_and_historical_requests(self) -> None:
        """PC-10: el esquema admite el request actual válido (agente y
        contexto), el histórico con solo agente y el histórico sin ninguno de
        los dos.

        El caso «contexto sin agente» NO se admite: la condición estructural de
        D5/PC-10 lo rechaza y se verifica en el test de rechazos. (El objetivo
        del paquete lo listaba entre los admitidos; prevalece el contrato
        aprobado, que es el oráculo de este test.)

        RED hoy: el esquema no declara `agent` ni `execution_context` y rechaza
        el request actual por claves desconocidas.
        """
        current = self.current_request()
        agent_only = dict(current)
        agent_only.pop("execution_context", None)
        historical = dict(current)
        historical.pop("agent", None)
        historical.pop("execution_context", None)

        validator, _ = self.validator()
        for label, instance in (
            ("actual (agent + execution_context)", current),
            ("histórico con solo agent", agent_only),
            ("histórico sin ambos", historical),
        ):
            with self.subTest(case=label):
                errors = list(validator.iter_errors(instance))
                self.assertEqual(
                    [error.message for error in errors],
                    [],
                    msg="PC-10 violada: el esquema publicado rechaza un "
                    f"request admitido ({label}): "
                    f"{[error.message for error in errors][:4]}",
                )

    def test_schema_rejects_invalid_shape_unknown_keys_and_context_without_agent(
        self,
    ) -> None:
        """PC-10/PC-08: el esquema conserva `additionalProperties: false`,
        rechaza tipos inválidos de `agent` por su TIPO (no porque el campo sea
        desconocido) y rechaza contexto presente sin agente por la dependencia
        estructural (no por clave desconocida).

        RED hoy: `agent`/`execution_context` son claves desconocidas, así que
        los rechazos ocurren por `additionalProperties`, no por la forma
        corregida.
        """
        current = self.current_request()
        validator, _ = self.validator()

        unknown = dict(current)
        unknown["unknown_key_outside_the_closed_set"] = 1
        unknown_errors = list(validator.iter_errors(unknown))
        self.assertTrue(
            unknown_errors,
            msg="PC-10 violada: una clave desconocida fue aceptada "
            "(`additionalProperties` dejó de estar cerrado)",
        )
        self.assertTrue(
            any(error.validator == "additionalProperties" for error in unknown_errors),
            msg="PC-10 violada: la clave desconocida no se rechazó por el "
            f"cierre del conjunto: {[error.message for error in unknown_errors][:4]}",
        )

        invalid_type = dict(current)
        invalid_type["agent"] = 42
        type_errors = list(validator.iter_errors(invalid_type))
        self.assertTrue(
            type_errors,
            msg="PC-10 violada: un `agent` no textual fue aceptado",
        )
        self.assertTrue(
            any(
                error.validator == "type"
                and list(error.absolute_path)[-1:] == ["agent"]
                for error in type_errors
            ),
            msg="PC-10 violada: `agent` no textual no se rechazó por su TIPO "
            "(el rechazo observado no corresponde a la propiedad corregida): "
            f"{[error.message for error in type_errors][:4]}",
        )

        context_without_agent = dict(current)
        context_without_agent.pop("agent", None)
        dependency_errors = list(validator.iter_errors(context_without_agent))
        self.assertTrue(
            dependency_errors,
            msg="PC-10/PC-08 violada: el esquema aceptó `execution_context` "
            "sin `agent`",
        )
        self.assertFalse(
            any(
                error.validator == "additionalProperties"
                for error in dependency_errors
            ),
            msg="PC-10 violada: contexto sin agente se rechaza solo porque "
            "`agent` es una clave desconocida, no por la dependencia "
            f"estructural: {[error.message for error in dependency_errors][:4]}",
        )

    def test_schema_shape_is_distinct_from_cli_role_and_dispatch_contrast(
        self,
    ) -> None:
        """PC-10: el asset declara `agent` y `execution_context` como
        propiedades OPCIONALES de tipo textual, y el esquema describe forma: no
        decide la coherencia de rol ni la de stack, que son comprobaciones del
        CLI (`validate-request`/`render` y `record-dispatch`).

        Se demuestra con instancias que el esquema debe ADMITIR por forma y que
        el CLI rechaza por política: un agente de otro rol (contraste estático)
        y un agente del mismo rol con otro stack (contraste contextual). Esos
        rechazos se verifican en `TestAgentBinding`; aquí se declara y protege
        la frontera del esquema.

        RED hoy: las propiedades no están declaradas.
        """
        current = self.current_request()
        validator, schema = self.validator()

        properties = schema.get("properties") or {}
        for name in ("agent", "execution_context"):
            self.assertIn(
                name,
                properties,
                msg="PC-10 violada: el asset no declara la propiedad "
                f"`{name}` (propiedades: {sorted(properties)})",
            )
            declared_type = properties[name].get("type")
            declared_types = (
                [declared_type] if isinstance(declared_type, str) else list(declared_type or [])
            )
            self.assertIn(
                "string",
                declared_types,
                msg=f"PC-10 violada: `{name}` no declara tipo textual "
                f"(declaración: {properties[name]!r})",
            )
        required = set(schema.get("required") or [])
        for name in ("agent", "execution_context"):
            self.assertNotIn(
                name,
                required,
                msg=f"PC-10 violada: `{name}` dejó de ser opcional; los "
                "históricos representativos dejarían de admitirse",
            )

        foreign_role = dict(current)
        foreign_role["agent"] = "cdad-reviewer"
        wrong_stack = dict(current)
        wrong_stack["agent"] = "cdad-test-writer-odoo"
        for label, instance in (
            ("agente de otro rol", foreign_role),
            ("agente del mismo rol con otro stack", wrong_stack),
        ):
            with self.subTest(case=label):
                errors = list(validator.iter_errors(instance))
                self.assertEqual(
                    [error.message for error in errors],
                    [],
                    msg="PC-10 violada: el esquema decidió coherencia de rol o "
                    f"stack ({label}); eso corresponde al CLI, no a la forma: "
                    f"{[error.message for error in errors][:4]}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
