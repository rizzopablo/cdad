#!/usr/bin/env python3
"""010-001 RED — contratos documentales compartidos.

Contrato: ``docs/specs/010-001-documentary-contracts/spec.md`` (aprobada
2026-10-31, sha256 ``9bf17a39…c94da``), §3 **Promesas A-D** (PC-01…PC-16),
§4 **INV-01…INV-08** y §5 (criterios medibles). Plan aprobado:
``docs/specs/010-001-documentary-contracts/plan.md``, tarea **T2** (clases
públicas ``TestPromiseA``…``TestPromiseD``, una clase por grupo, módulo
aditivo). Forma aprobada del RED y resoluciones del dueño:
``test-audit.md`` §8 y ``audit-approval-2026-10-31.md`` (A1-A10).

Superficie observable (caja negra: TEXTO publicado y PROCESOS reales; la
implementación nunca se lee ni se importa):

- ``skills/cdad-cycle/references/documentary-contracts.md`` — la casa
  normativa (archivo NUEVO: hoy no existe ⇒ este RED falla por ausencia de
  comportamiento, nunca por ImportError);
- ``skills/cdad-cycle/SKILL.md`` — la tabla «How to read the references»;
- las seis fuentes de rol ``sources/roles/{architect,implementer,test-writer,
  reviewer,scribe,orchestrator}.md``;
- los cinco bloques estáticos ``skills/cdad-cycle/packets/roles/``
  (architect, implementer, test-writer, reviewer, scribe: el orquestador no
  tiene bloque — A4);
- los agentes GENERADOS (``build/staging/agents/<runtime>/``) y PROMOVIDOS
  (``agents/`` y ``agents/claude-code/``) de los dos runtimes, incluidas sus
  variantes Odoo;
- la instalación AISLADA (``CDAD_INSTALL_ROOT``) con los destinos ``skills/``
  que declaran los tests del instalador (A6: no se inventan rutas).

Mapeo test → promesa → postcondiciones (un test por promesa observable; la
trazabilidad múltiple es deliberada, no una cuota por postcondición):

  TestPromiseA::test_the_norm_defines_the_four_categories_with_their_distinctions
      Promesa A — PC-01, PC-02, INV-05                      (T3)
  TestPromiseA::test_the_norm_prescribes_locators_per_source_type_and_pending_classification
      Promesa A — PC-03, PC-04                              (T3)
  TestPromiseB::test_the_norm_requires_the_four_engagements_and_protects_the_oracle
      Promesa B — PC-05, PC-06, PC-07                       (T3)
  TestPromiseB::test_the_norm_states_the_six_role_boundaries
      Promesa B — PC-08                                     (T3)
  TestPromiseC::test_the_norm_separates_structural_control_from_semantic_review
      Promesa C — PC-09, PC-10, INV-06, INV-08              (T3)
  TestPromiseC::test_the_norm_requires_contrast_with_sources_and_owner_acceptance
      Promesa C — PC-11, PC-12, INV-07                      (T3)
  TestPromiseD::test_the_norm_lives_in_one_house_listed_in_the_reference_table
      Promesa D — PC-13, INV-01                             (T3)
  TestPromiseD::test_no_installable_surface_copies_the_normative_phrases
      Promesa D — PC-13, INV-01                             (T4: mide el árbol final)
  TestPromiseD::test_the_six_role_sources_and_five_blocks_carry_their_obligation_and_pointer
      Promesa D — PC-14                         (T3 fuentes / T4 bloques)
  TestPromiseD::test_generated_and_promoted_agents_of_both_runtimes_carry_the_obligations
      Promesa D — PC-14                                     (T4)
  TestPromiseD::test_isolated_install_distributes_the_reference_with_source_bytes
      Promesa D — PC-15                                     (T4)

CONTROLES DECLARADOS (ya verdes hoy; NO se reimplementan aquí — duplicar un
oráculo vigente crearía dos métodos que pueden divergir, INV-01/A10). Sus
selectores exactos son:

  1. determinismo de ``make staging`` (PC-15/V-2):
     ``tests.test_006_004_u3_principle_single_source.TestPd13GeneratedAgents.
     test_pd13_make_staging_is_deterministic_across_two_runs``
  2. techo de 12000 bytes en los 14 pares rol/subfase (PC-15/V-4):
     ``tests.test_006_004_u3_principle_single_source.TestPd13StaticBlockCeiling.
     test_pd13_the_static_block_of_the_fourteen_role_substage_pairs_is_under_the_ceiling``
  3. exactamente los 11 agentes declarados por runtime (PC-16):
     ``tests.test_cdad_generate.GeneratorContractTests.
     test_pd_1e_generated_agents_carry_no_model_line``
  4. barreras de permisos de los agentes Claude Code (PC-16):
     ``tests.test_packet_prepare.TestPreparedInstalled.
     test_p6_claude_barriers_are_unchanged``

El informe RED declara estos controles por separado de los fallos: no son la
falla, son guardas que deben seguir verdes después del GREEN (A8). ``make
validate`` NO es oráculo de RED (A9).

INTERFAZ DECLARADA POR ESTE RED (la satisface el implementer leyendo el test;
el contrato fija las obligaciones y deja la redacción dentro):

1. **La casa** es ``skills/cdad-cycle/references/documentary-contracts.md`` y
   lleva, de forma localizable, las cuatro categorías de D1 con sus
   distinciones, los localizadores mínimos por tipo de fuente de D2 y la
   clasificación de pendientes de D3 (Promesa A), las cuatro declaraciones del
   encargo y las fronteras de los seis roles de PC-05…PC-08 (Promesa B) y la
   separación de registros y la aceptación de PC-09…PC-12 (Promesa C).
2. **Un concepto, varias redacciones (A2).** Los conceptos se buscan por
   vocabulario con alternativas ES/EN, sin congelar el idioma ni los párrafos.
   La comparación ignora acentos, mayúsculas y ajuste de línea.
3. **La unicidad (A1/PC-13)** se mide sobre las frases normativas de TODA la
   referencia (oraciones de ≥6 palabras y líneas de ≥8, umbrales del
   precedente), con espacios normalizados, barriendo ``skills/``, ``sources/``
   y ``agents/`` y excluyendo la propia referencia: ningún consumidor puede
   reproducir esas frases; las obligaciones breves de rol se PARAFRASEAN. Vale
   también en el sentido inverso: la referencia no reproduce frases que ya
   vivan en fuentes, bloques o agentes (habría dos casas de la misma frase).
4. **Los punteros** nombran el archivo ``documentary-contracts.md`` (verbatim:
   es un nombre de archivo, no una redacción). Se exigen en la tabla de
   ``SKILL.md``, en las seis fuentes, en los cinco bloques y en los agentes.
5. **Los cinco bloques** llevan obligación MÍNIMA + puntero (A3), no la
   obligación completa; el techo estático no se eleva.
6. **El orquestador** se verifica en su fuente y en el agente generado, no en
   un bloque ni en los adaptadores (A4).
7. **PC-16** queda en los guards existentes y en la revisión del diff: este
   módulo no añade un oráculo de ausencia por palabras clave (A7).
8. **INV-07** se verifica como AUSENCIA del nombre del aprobador de esta
   unidad (el que la spec nombra en §5 criterio 9 y §9) en ``skills/``,
   ``sources/`` y ``agents/`` (A5), con control de vacuidad.

DEPENDENCIA DECLARADA (A10): los helpers ``copies_of``, ``normative_units``,
``installable_documents``, ``disposable_product``, ``normalized``,
``read_document`` y ``relative`` se reutilizan de
``tests.test_006_004_u3_principle_single_source``; los destinos de instalación
``skills/`` se toman de ``tests.test_004_001_t6.REQUIRED_REAL_DESTINATIONS``
(A6) y la raíz con staging de ``tests.product_staging.product_root``. No se
duplica ningún método: una sola definición del oráculo (INV-01). No se
reutiliza ``staging_digests`` porque está atada al subconjunto
architect/reviewer y este oráculo mide los 11 agentes de los dos runtimes:
usarla mezclaría dos alcances distintos y perdería cobertura.

LÍMITE DECLARADO (PD-15/INV-06): estas comprobaciones son ESTRUCTURALES. Un
verde aquí no acredita fidelidad semántica, suficiencia ni verdad: eso lo
juzga la revisión independiente de T5. Este módulo no es un sandbox y no
demuestra ausencia de escrituras transitorias.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unicodedata
import unittest
from pathlib import Path

from tests.product_staging import product_root
from tests.test_004_001_t6 import REQUIRED_REAL_DESTINATIONS
from tests.test_006_004_u3_principle_single_source import (
    copies_of,
    disposable_product,
    installable_documents,
    normative_units,
    normalized,
    read_document,
    relative,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Superficies (rutas relativas al repo; ninguna ruta del host)
# ---------------------------------------------------------------------------

NORM_RELPATH = "skills/cdad-cycle/references/documentary-contracts.md"
NORM = REPO_ROOT / NORM_RELPATH

# El puntero: el NOMBRE del archivo de la casa normativa (verbatim).
POINTER = "documentary-contracts.md"

SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"

ROLES = ("architect", "test-writer", "implementer", "reviewer", "scribe")
ALL_ROLE_SOURCES = ROLES + ("orchestrator",)
ROLE_SOURCES = {
    role: REPO_ROOT / "sources" / "roles" / f"{role}.md" for role in ALL_ROLE_SOURCES
}
# Los cinco bloques existentes: el orquestador no tiene bloque (A4).
ROLE_BLOCKS = {
    role: REPO_ROOT / "skills" / "cdad-cycle" / "packets" / "roles" / f"{role}.md"
    for role in ROLES
}

# INV-07 (A5): el nombre concreto del aprobador de esta unidad. La spec lo
# nombra en §5 criterio 9 y §9; fuera de docs/ no puede aparecer.
APPROVER_NAME = "Pablo"

# PC-14: los 11 agentes declarados por runtime (5 roles × genérico/Odoo +
# orquestador), tal como los fija tests/test_cdad_generate.py.
RUNTIMES = ("opencode", "claude-code")
AGENT_NAMES = tuple(
    [f"cdad-{role}.md" for role in ROLES]
    + [f"cdad-{role}-odoo.md" for role in ROLES]
    + ["cdad-orchestrator.md"]
)
STAGING_AGENTS = Path("build") / "staging" / "agents"
PROMOTED_DIRS = {"opencode": Path("agents"), "claude-code": Path("agents") / "claude-code"}
INSTALLED_AGENTS_DIRS = {
    "opencode": ".config/opencode/agents",
    "claude-code": ".claude/agents",
}
# A6: los destinos `skills/` que publica el instalador se toman de los tests
# del instalador; no se inventan rutas.
SKILLS_DESTINATIONS = tuple(
    destination
    for destination in REQUIRED_REAL_DESTINATIONS
    if destination.endswith("skills/cdad-cycle")
)

# ---------------------------------------------------------------------------
# Conceptos (A2: alternativas ES/EN; la redacción es libre, el concepto no)
#
# La comparación se hace sobre texto PLEGADO: minúsculas, espacios colapsados
# y acentos retirados. No se congela el idioma del documento.
# ---------------------------------------------------------------------------

EVIDENCE_ANCHORS = ("evidencia", "evidence")
PROPOSAL_ANCHORS = ("propuesta", "proposal", "proposicion", "proposition")
CONTRADICTION_ANCHORS = ("contradicci", "contradict")
PENDING_ANCHORS = (
    "pendiente",
    "pending",
    "open question",
    "pregunta abierta",
    "cuestion abierta",
)

SOURCE = ("fuente", "source")
LOCATOR = ("localiz", "ubicaci", "locat", "donde", "where")
ATTRIBUTION = (
    "atribuye",
    "atribuir",
    "attribute",
    "demuestra",
    "demostr",
    "sostiene",
    "support",
    "prueba",
    "prove",
)
NEGATION = (
    "no ",
    "not ",
    "nunca",
    "never",
    "sin ",
    "does not",
    "doesn't",
    "ningun",
    "ninguna",
    "ni ",
    "tampoco",
    "neither",
)
FACT = ("hecho", "fact", "observad", "observed")
DECISION = ("decision", "decisi", "aprobad", "approved", "approval")
REFERENCE = ("referencia", "reference", "fuente", "source")
CONSENSUS = ("consenso", "consensus")
INCOMPATIBLE = ("incompatib", "incompatible", "contrapuest", "conflict")
ACCREDITED = ("acredit", "accredited", "registrad", "recorded", "documentad", "documented")
ELIMINATION = ("elimina", "remove", "removed", "suprime", "suppress", "descarta", "discard")
MISSING = ("falta", "missing", "carencia", "ausencia", "no acreditad", "unaccredited")
RESOLUTION = ("resolver", "resolve", "resolucion", "resolution", "cierre", "closure")
SILENT = ("silencios", "silently", "silencio")
UNILATERAL = ("unilateral",)
BLOCKING = ("bloquea", "bloqueante", "blocking")
NON_BLOCKING = ("no bloqueante", "no bloqueantes", "non-blocking", "non blocking", "nonblocking")
POSTCONDITION = ("postcondicion", "postcondition", "criterio de aceptacion", "acceptance criterion")
QUESTION = ("cuestion", "question", "issue", "asunto")
AFFECTED_LOCATION = ("ubicacion afectada", "affected location", "ubicacion", "location")
CLOSURE_CONDITION = ("condicion de cierre", "closure condition", "condicion para cerrar")
JUSTIFIED = ("justificad", "justified", "justifica")
DECISION_MAKER = ("decisor", "decision-maker", "decision maker", "responsable", "owner of the decision")
OUT_OF_SCOPE = ("fuera del alcance", "out of scope", "outside the scope")
UNCERTAINTY = ("incertidumbre", "uncertainty")
UNRECOVERABLE = (
    "no puede recuperarse",
    "cannot be recovered",
    "irrecuperable",
    "unrecoverable",
    "inaccesible",
    "inaccessible",
)
NOT_ACCREDITED = (
    "no se acredita",
    "not accredited",
    "no se respalda",
    "not backed",
    "no sostiene",
    "does not support",
)
CORRECT_OR_PENDING = ("corregir", "correct", "reformular", "reformulate", "pendiente", "pending")

# Promesa A — localizadores mínimos por tipo de fuente (D2).
REPOSITORY_FILE = ("archivo del repositorio", "repository file", "archivo del repo", "repo file")
RELATIVE_PATH = ("ruta relativa", "relative path", "ruta", "path")
INNER_LOCATOR = ("lin", "line", "seccion", "section", "identificador", "identifier")
SNAPSHOT = ("revision", "snapshot", "revision identificada")
MARKDOWN_INPUT = (
    "insumo markdown",
    "markdown input",
    "documento markdown",
    "documento de texto",
    "documento recibido",
    "texto recibido",
    "insumo de texto",
    "text input",
    "insumo",
)
VERSION = ("version", "version identificada", "snapshot")
FRAGMENT = ("fragmento", "fragment", "apartado", "excerpt", "extracto", "seccion", "section")
USER_MESSAGE = ("mensaje", "message")
RECOVERABLE_ID = ("identificador", "identifier", "recuperable", "recoverable")
DATE_CONTEXT = ("fecha", "date", "contexto", "context")
MINUTE = ("minuta", "minute", "transcripcion", "transcript")
TEMPORAL = ("marca temporal", "timestamp", "intervencion", "turn", "seccion", "section")
WEB_SOURCE = ("pagina web", "web page", "url")
INTERNAL_LOCATION = ("ubicacion interna", "internal location", "ancla", "anchor", "fragmento", "fragment")
CAPTURE = ("captura", "capture", "version", "snapshot")
INSUFFICIENT = ("no bastan", "no basta", "not enough", "insufficient", "no es suficiente")

# Promesa B — PC-05…PC-08.
AUTHORIZED_SOURCES = (
    "fuentes autorizadas",
    "authorized sources",
    "authorised sources",
    "fuentes permitidas",
    "permitted sources",
)
EDITABLE_PRODUCT = ("producto editable", "editable product", "producto modificable", "editable output")
DELIMITED_PATHS = ("rutas delimitadas", "delimited paths", "rutas acotadas", "delimitadas", "delimited")
VERIFIER = ("verificador", "verifier")
ACCEPTANCE_INPUT = ("insumo de aceptacion", "acceptance input", "insumos de aceptacion", "acceptance inputs", "insumo")
PROTECTED = ("proteg", "protect")
EXPECTED_EVIDENCE = ("evidencia esperada", "expected evidence")
VERIFICATION_LIMITS = ("limitacion", "limitation", "limite", "limit")
GREEN = ("green",)
DOCS_CLASSIFICATION = ("docs",)
OVERLAP = ("superposicion", "overlap", "ambiguedad", "ambiguity", "solapamiento")
STOP = ("detener", "stop", "halta", "halt", "detenerse")
CORRECT = ("corregir", "correct", "corrige")
PRODUCER = ("quien produce", "who produces", "producer", "quien lo produce")
MODIFY = ("modifica", "modify", "edita", "edit", "cambia", "change")
ORACLE = ("oraculo", "oracle")
COMPETENT_ROLE = ("rol competente", "competent role", "rol que corresponde")
APPROVAL = ("aprobacion", "approval", "aprobacion vigente")
FAVOURABLE = ("favorable", "favourable", "favorables")

# Promesa B — PC-08: fronteras de los seis roles.
ROLE_ANCHORS = {
    "orchestrator": ("orquestador", "orchestrator"),
    "architect": ("architect", "arquitecto"),
    "test-writer": ("test-writer", "test writer", "escritor de tests"),
    "implementer": ("implementer", "implementador"),
    "reviewer": ("reviewer", "revisor"),
    "scribe": ("scribe", "escriba"),
}
ROLE_OBLIGATIONS = {
    "orchestrator": (
        ("cuatro declaraciones (four / cuatro)", ("cuatro", "four")),
        ("declaracion (declaration)", ("declaracion", "declaration")),
        ("alcances (scope)", ("alcance", "scope")),
        ("evidencia (evidence)", ("evidencia", "evidence")),
        ("pendientes (pending)", ("pendiente", "pending")),
        ("gates existentes (gate)", ("gate", "compuerta")),
    ),
    "architect": (
        ("promesa (promise)", ("promesa", "promise")),
        ("verificable (verifiable)", ("verificable", "verifiable")),
        ("fuentes (sources)", SOURCE),
        ("limites (limits)", ("limite", "limit")),
        ("aceptacion (acceptance)", ("aceptacion", "acceptance")),
        ("borrador (draft)", ("borrador", "draft")),
        ("sin escribir (without writing)", ("sin escribir", "without writing", "no escribe", "does not write", "sin redactar")),
        ("sin aprobar (without approving)", ("sin aprobar", "without approving", "ni aprobar", "no aprueba", "does not approve")),
    ),
    "test-writer": (
        ("verificador (verifier)", ("verificador", "verifier", "oraculo", "oracle")),
        ("contrato (contract)", ("contrato", "contract")),
        ("insumos autorizados (authorized inputs)", ("insumo", "input", "fuente", "source")),
        ("documento producido (produced document)", ("documento producido", "produced document", "producto producido", "produced product", "documento que debe verificar")),
        ("tests autorizados (authorized tests)", ("tests autorizados", "authorized tests", "authorised tests", "solo tests", "only declared tests", "unicamente tests")),
    ),
    "implementer": (
        ("producto documental (documentary product)", ("producto documental", "documentary product", "producto de implementacion", "implementation product")),
        ("autorizado (authorized)", ("autorizad", "authorized", "authorised", "expresamente")),
        ("no edita (does not edit)", ("no edita", "does not edit", "never edit", "not edit", "no modifica", "does not modify")),
        ("fuentes (sources)", SOURCE),
        ("verificadores (verifiers)", VERIFIER),
        ("insumos protegidos (protected inputs)", ("insumo", "input", "artefacto", "artifact")),
    ),
    "reviewer": (
        ("independiente (independent)", ("independiente", "independent")),
        ("read-only", ("read-only", "solo lectura", "read only", "sin editar")),
        ("contraste (contrast)", ("contrast", "compare", "contrasta", "cotej")),
        ("fuentes (sources)", SOURCE),
        ("hallazgos (findings)", ("hallazgo", "finding")),
        ("abstenciones (abstentions)", ("abstencion", "abstention")),
        ("limites (limits)", ("limite", "limit")),
    ),
    "scribe": (
        ("Memory Bank", ("memory bank",)),
        ("borradores (drafts)", ("borrador", "draft")),
        ("evidencia (evidence)", ("evidencia", "evidence")),
        ("no asume (does not assume)", ("no asume", "does not assume", "not assume", "sin asumir", "no assume")),
        ("produccion documental (documentary production)", ("produccion documental", "documentary production", "documentary output", "productor documental")),
        ("no aprueba (does not approve)", ("no aprueba", "does not approve", "not approve", "sin aprobar", "ni aprobar")),
    ),
}

# Promesa C — PC-09…PC-12.
STRUCTURAL_CONTROL = (
    "control estructural",
    "structural control",
    "control automatico",
    "automatic control",
    "comprobacion estructural",
    "structural check",
)
SEMANTIC_REVIEW = (
    "revision semantica",
    "semantic review",
    "revision independiente",
    "independent review",
    "semantic revision",
)
RESULT = ("resultado", "result")
SCOPE = ("alcance", "scope")
LIMITATION = ("limitacion", "limitation", "limite", "limit")
CLAIMS = ("afirmacion", "claim", "assertion")
FINDINGS = ("hallazgo", "finding")
ABSTENTIONS = ("abstencion", "abstention")
PRESENCE = ("presencia", "presence")
FIDELITY = ("fidelidad", "fidelity", "suficiencia", "sufficiency", "verdad", "truth")
RECEIPT = ("recibo", "receipt")
TRANSPORT = ("transporte", "transport", "delivery", "entrega")
SANDBOX = ("sandbox",)
TRANSITORY = ("escrituras transitorias", "transient write", "transient writes", "escritura transitoria", "transient")
INSUFFICIENT_SUPPORT = (
    "respaldo insuficiente",
    "insufficient support",
    "soporte insuficiente",
    "insufficient backing",
    "respaldo debil",
)
OMITTED = ("omitid", "omitted", "omitida", "omitidas", "omitted")
DOES_NOT_SUPPORT = (
    "no sostienen",
    "do not support",
    "doesn't support",
    "no respaldan",
    "do not back",
    "no acreditan lo afirmado",
)
REAL_SCOPE = ("alcance real", "real scope", "alcance declarado", "declared scope")
INFALLIBLE = ("infalible", "infallible")
FUNCTIONAL_ACCEPTANCE = ("aceptacion funcional", "functional acceptance", "aceptacion del usuario")
APPROVING_OWNER = ("usuario", "user", "dueno", "owner")
APPROVES = ("aprueba", "approves", "aprobador", "approver")
PENDING = ("pendiente", "pending")
PREVENT = ("impide", "impedir", "prevent", "block", "bloquea")
CONTRACT = ("contrato", "contract")
VISIBLE = ("visible", "visibles", "visibles para", "visible")
CONTRADICTION = ("contradiccion", "contradiction", "contradicciones", "contradictions")

# Promesa D — obligación mínima que viaja en los cinco bloques (A3).
ROLE_MINIMUM = {
    "architect": (
        ("documental (documentary)", ("documental", "documentary")),
        ("verificable/promesa (verifiable/promise)", ("verificable", "verifiable", "promesa", "promise")),
    ),
    "test-writer": (
        ("documental (documentary)", ("documental", "documentary")),
        ("contrato/verificador (contract/verifier)", ("contrato", "contract", "verificador", "verifier")),
    ),
    "implementer": (
        ("documental (documentary)", ("documental", "documentary")),
        ("autorizado/producto (authorized/product)", ("autorizad", "authorized", "authorised", "producto", "product")),
    ),
    "reviewer": (
        ("documental (documentary)", ("documental", "documentary")),
        ("fuentes/contraste (sources/contrast)", ("fuente", "source", "contrast", "contrasta")),
    ),
    "scribe": (
        ("documental (documentary)", ("documental", "documentary")),
        ("evidencia/memory bank/borrador", ("evidencia", "evidence", "memory bank", "borrador", "draft")),
    ),
}

# A4: el orquestador no tiene bloque ni adaptadores; su obligación mínima se
# exige en su fuente y en el agente generado/promovido.
ROLE_MINIMUM["orchestrator"] = (
    ("cuatro declaraciones (four declarations)", ("cuatro", "four")),
    ("declaracion (declaration)", ("declaracion", "declaration")),
)

# Ventana de vecindad (caracteres plegados) para los conceptos que el contrato
# declara EN LA MISMA definición/obligación.
NEAR = 1400
NEAR_WIDE = 2600
NEAR_TIGHT = 700


# ---------------------------------------------------------------------------
# Helpers de concepto (caja negra; un artefacto que falta = estado conductual)
# ---------------------------------------------------------------------------


def fold(text: str) -> str:
    """minúsculas + espacios colapsados + acentos retirados."""
    decomposed = unicodedata.normalize("NFKD", normalized(text))
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _folded_alternatives(alternatives: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(fold(alternative) for alternative in alternatives)


def _has(window: str, alternatives: tuple[str, ...]) -> bool:
    return any(alternative in window for alternative in _folded_alternatives(alternatives))


def _occurrences(folded_text: str, alternatives: tuple[str, ...]) -> list[int]:
    positions: list[int] = []
    for alternative in _folded_alternatives(alternatives):
        start = 0
        while True:
            index = folded_text.find(alternative, start)
            if index < 0:
                break
            positions.append(index)
            start = index + 1
    return positions


def missing_in_best_window(
    text: str,
    anchors: tuple[str, ...],
    requirements: tuple[tuple[str, tuple[str, ...]], ...],
    radius: int = NEAR,
) -> list[str]:
    """Etiquetas de los requisitos que NINGUNA ventana alrededor de un ancla
    satisface (la mejor ventana es la que satisface más requisitos).

    Devuelve la lista completa si el ancla no aparece: el concepto no está.
    """
    folded = fold(text)
    positions = _occurrences(folded, anchors)
    if not positions:
        return [label for label, _alternatives in requirements]
    best: list[str] | None = None
    for position in positions:
        window = folded[max(0, position - radius) : position + radius]
        missing = [
            label for label, alternatives in requirements if not _has(window, alternatives)
        ]
        if best is None or len(missing) < len(best):
            best = missing
        if not missing:
            return []
    return list(best or [])


def assert_concepts(
    case: unittest.TestCase,
    text: str,
    anchors: tuple[str, ...],
    requirements: tuple[tuple[str, tuple[str, ...]], ...],
    label: str,
    radius: int = NEAR,
) -> None:
    """Afirma que la definición/obligación aparece en una misma zona del texto."""
    missing = missing_in_best_window(text, anchors, requirements, radius)
    case.assertEqual(
        missing,
        [],
        f"{label}: la definición/obligación no reúne sus conceptos en una misma "
        f"zona (faltan: {missing!r}). El contrato exige la distinción completa; "
        "la redacción es libre (ES/EN).",
    )


def require_any(
    case: unittest.TestCase,
    text: str,
    alternatives: tuple[str, ...],
    concept: str,
    label: str,
) -> None:
    folded = fold(text)
    hits = [alternative for alternative in alternatives if fold(alternative) in folded]
    case.assertTrue(
        hits,
        f"{label}: falta el concepto «{concept}» (alternativas buscadas: "
        f"{list(alternatives)!r}).",
    )


def negation_present(window: str) -> bool:
    return _has(window, NEGATION)


# ---------------------------------------------------------------------------
# La fila de la tabla de referencias (variante local del precedente: su
# `skill_reference_row` está atada a `design-principles.md`, A10)
# ---------------------------------------------------------------------------


def reference_row(text: str, pointer: str) -> bool:
    """La tabla «How to read the references» tiene una fila para el archivo."""
    inside = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            inside = "how to read the references" in stripped.lower()
            continue
        if not inside or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
        if not cells:
            continue
        if all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells):
            continue
        if pointer in cells[0]:
            return True
    return False


def role_of_agent(name: str) -> str:
    """`cdad-<rol>[-odoo].md` -> `<rol>`; `cdad-orchestrator.md` -> orchestrator."""
    stem = name[len("cdad-") : -len(".md")]
    if stem.endswith("-odoo"):
        stem = stem[: -len("-odoo")]
    return stem


# ---------------------------------------------------------------------------
# Promesa A — criterios compartidos (PC-01…PC-04)
# ---------------------------------------------------------------------------


class TestPromiseA(unittest.TestCase):
    """Promesa A: los roles disponen de criterios documentales inequívocos.

    Protege PC-01…PC-04 e INV-05. Tarea T3: la casa normativa es el artefacto
    que T3 publica; hoy no existe y estos tests fallan por comportamiento
    ausente (AssertionError), nunca por importación.
    """

    maxDiff = None

    def test_the_norm_defines_the_four_categories_with_their_distinctions(self) -> None:
        """PC-01/PC-02/INV-05: las cuatro categorías y sus distinciones (D1).

        Evidencia (fuente + localización + límite de atribución), propuesta
        (no es hecho observado ni decisión aprobada), contradicción
        (incompatibles con sus referencias, sin consenso inventado ni
        eliminación sin decisión acreditada) y pendiente (qué falta, qué lo
        resolvería, no se convierte en hecho). Ninguna categoría exige
        instancias ficticias ni secciones vacías: se comprueba el concepto.
        """
        text = read_document(NORM, "PC-01: la casa normativa documental")

        assert_concepts(
            self,
            text,
            EVIDENCE_ANCHORS,
            (
                ("fuente (source)", SOURCE),
                ("localizador (locator)", LOCATOR),
                ("límite: negación (negation)", NEGATION),
                ("límite: atribución/demostración (attribution)", ATTRIBUTION),
            ),
            "PC-01 (evidencia)",
        )
        assert_concepts(
            self,
            text,
            PROPOSAL_ANCHORS,
            (
                ("no es hecho (not a fact)", NEGATION),
                ("hecho/observado (fact/observed)", FACT),
                ("decisión/aprobada (decision/approved)", DECISION),
            ),
            "PC-01 (propuesta)",
        )
        assert_concepts(
            self,
            text,
            CONTRADICTION_ANCHORS,
            (
                ("incompatibilidad (incompatible)", INCOMPATIBLE),
                ("referencias (references)", REFERENCE),
                ("sin consenso inventado (no consensus)", CONSENSUS),
                ("negación (negation)", NEGATION),
                ("decisión acreditada (accredited decision)", ACCREDITED),
            ),
            "PC-01 (contradicción)",
        )
        assert_concepts(
            self,
            text,
            PENDING_ANCHORS,
            (
                ("qué falta (missing)", MISSING),
                ("qué lo resolvería (resolution/closure)", RESOLUTION),
                ("negación/silencio (negation/silent)", NEGATION + SILENT),
            ),
            "PC-01 (pendiente)",
        )
        require_any(
            self,
            text,
            ("hecho observado", "observed fact", "hecho", "fact"),
            "una propuesta no se presenta como hecho observado (INV-05)",
            "PC-02/INV-05",
        )

    def test_the_norm_prescribes_locators_per_source_type_and_pending_classification(
        self,
    ) -> None:
        """PC-03/PC-04: localizador mínimo por tipo de fuente (D2) y
        clasificación de pendientes (D3).

        Los cinco tipos de fuente de D2 con los componentes de su localizador;
        el tratamiento de fuentes inaccesibles/mutables/insuficientes; y la
        clasificación bloqueante/no bloqueante con sus datos mínimos, sin
        rebaja unilateral.
        """
        text = read_document(NORM, "PC-03: la casa normativa documental")

        source_types = (
            (
                "D2 archivo del repositorio",
                REPOSITORY_FILE,
                (
                    ("ruta relativa (relative path)", RELATIVE_PATH),
                    ("líneas/sección/identificador (inner locator)", INNER_LOCATOR),
                    ("revisión/snapshot (revision)", SNAPSHOT),
                ),
            ),
            (
                "D2 documento markdown/texto recibido",
                MARKDOWN_INPUT,
                (
                    ("ruta/identificador (path/identifier)", ("ruta", "path", "identificador", "identifier")),
                    ("sección/líneas/fragmento (section/fragment)", FRAGMENT),
                    ("versión/snapshot examinado (version)", VERSION),
                ),
            ),
            (
                "D2 mensaje o decisión del usuario",
                USER_MESSAGE,
                (
                    ("identificador recuperable (recoverable id)", RECOVERABLE_ID),
                    ("fecha/contexto (date/context)", DATE_CONTEXT),
                    ("fragmento/apartado (fragment)", FRAGMENT),
                ),
            ),
            (
                "D2 minuta o transcripción",
                MINUTE,
                (
                    ("identificador (identifier)", ("identificador", "identifier")),
                    ("versión (version)", VERSION),
                    ("sección/intervención/marca temporal (temporal)", TEMPORAL),
                ),
            ),
            (
                "D2 página web u otra fuente mutable",
                WEB_SOURCE,
                (
                    ("ubicación interna (internal location)", INTERNAL_LOCATION),
                    ("versión/captura (capture)", CAPTURE),
                    ("fecha de consulta/captura (date)", DATE_CONTEXT),
                ),
            ),
        )
        for label, anchors, requirements in source_types:
            with self.subTest(source=label):
                assert_concepts(self, text, anchors, requirements, f"PC-03/{label}")

        # D2: una URL viva y una fecha, sin el contenido examinado, no bastan.
        assert_concepts(
            self,
            text,
            INSUFFICIENT,
            (
                ("URL (url)", WEB_SOURCE),
                ("fecha (date)", DATE_CONTEXT),
            ),
            "PC-03 (fuente mutable insuficiente)",
            radius=NEAR_TIGHT,
        )
        # D2: una fuente que no puede recuperarse o no sostiene la afirmación
        # no se acredita: corregir, reformular o declarar un pendiente.
        assert_concepts(
            self,
            text,
            UNRECOVERABLE,
            (
                ("no se acredita/no se respalda (not accredited)", NOT_ACCREDITED),
                ("corregir/reformular/pendiente (correct or pending)", CORRECT_OR_PENDING),
            ),
            "PC-03 (fuente inaccesible o insuficiente)",
        )

        # D3: clasificación de pendientes, datos mínimos y prohibición de
        # aceptar una promesa incumplida mediante reclasificación unilateral.
        assert_concepts(
            self,
            text,
            PENDING_ANCHORS,
            (
                ("bloqueante (blocking)", BLOCKING),
                ("no bloqueante (non-blocking)", NON_BLOCKING),
                ("postcondición/criterio de aceptación (postcondition)", POSTCONDITION),
                ("cuestión (question)", QUESTION),
                ("ubicación afectada (affected location)", AFFECTED_LOCATION),
                ("condición de cierre (closure condition)", CLOSURE_CONDITION),
                ("clasificación justificada (justified classification)", JUSTIFIED),
            ),
            "PC-04 (clasificación de pendientes)",
            radius=NEAR_WIDE,
        )
        require_any(
            self,
            text,
            DECISION_MAKER,
            "el pendiente identifica al decisor/responsable (o declara que falta)",
            "PC-04 (datos mínimos)",
        )
        require_any(
            self,
            text,
            UNILATERAL,
            "el productor no rebaja unilateralmente una obligación",
            "PC-04 (prohibición de rebaja unilateral)",
        )
        require_any(
            self,
            text,
            OUT_OF_SCOPE,
            "un pendiente puede ser no bloqueante por estar fuera del alcance",
            "PC-04 (no bloqueante)",
        )
        require_any(
            self,
            text,
            UNCERTAINTY,
            "un pendiente puede ser no bloqueante si el contrato promete presentar "
            "la incertidumbre",
            "PC-04 (no bloqueante)",
        )


# ---------------------------------------------------------------------------
# Promesa B — el encargo separa producto, fuentes y oráculo (PC-05…PC-08)
# ---------------------------------------------------------------------------


class TestPromiseB(unittest.TestCase):
    """Promesa B: el encargo separa producto, fuentes y oráculo.

    Protege PC-05…PC-08. Tarea T3: la casa normativa es el artefacto.
    """

    maxDiff = None

    def test_the_norm_requires_the_four_engagements_and_protects_the_oracle(self) -> None:
        """PC-05/PC-06/PC-07: las cuatro declaraciones del encargo documental,
        la protección del oráculo y la regla «quien produce no modifica su
        oráculo»."""
        text = read_document(NORM, "PC-05: la casa normativa documental")

        require_any(self, text, AUTHORIZED_SOURCES, "fuentes autorizadas", "PC-05 (1)")
        require_any(self, text, EDITABLE_PRODUCT, "producto editable", "PC-05 (2)")
        require_any(self, text, DELIMITED_PATHS, "rutas delimitadas", "PC-05 (2)")
        require_any(self, text, VERIFIER, "verificadores", "PC-05 (3)")
        require_any(self, text, ACCEPTANCE_INPUT, "insumos de aceptación", "PC-05 (3)")
        require_any(self, text, PROTECTED, "insumos protegidos", "PC-05 (3)")
        require_any(self, text, EXPECTED_EVIDENCE, "evidencia esperada", "PC-05 (4)")
        require_any(self, text, VERIFICATION_LIMITS, "limitaciones de verificación", "PC-05 (4)")

        # PC-06: fuentes, contrato de aceptación, verificadores y plantillas
        # usadas como oráculo quedan FUERA del alcance editable de GREEN; que
        # compartan la clasificación `docs` no los hace producto editable; una
        # superposición o ambigüedad exige detener esa parte y corregir.
        require_any(self, text, GREEN, "la subfase GREEN", "PC-06 (alcance editable)")
        assert_concepts(
            self,
            text,
            GREEN,
            (
                ("fuentes (sources)", SOURCE),
                ("verificadores (verifiers)", VERIFIER),
                ("plantillas (templates)", ("plantilla", "template")),
                ("negación (negation)", NEGATION),
            ),
            "PC-06 (exclusiones del alcance editable)",
            radius=NEAR_WIDE,
        )
        assert_concepts(
            self,
            text,
            DOCS_CLASSIFICATION,
            (
                ("editable (editable)", ("editable", "editables")),
                ("negación (negation)", NEGATION),
                ("producto (product)", ("producto", "product")),
            ),
            "PC-06 (docs no es producto editable)",
        )
        assert_concepts(
            self,
            text,
            OVERLAP,
            (
                ("detener (stop)", STOP),
                ("corregir (correct)", CORRECT),
            ),
            "PC-06 (superposición o ambigüedad)",
        )

        # PC-07: «quien produce no modifica su oráculo»; el cambio legítimo
        # vuelve al rol competente y, si altera el contrato, a aprobación; no
        # se hace desde GREEN para obtener un resultado favorable.
        assert_concepts(
            self,
            text,
            ORACLE,
            (
                ("quien produce (producer)", PRODUCER),
                ("no modifica (does not modify)", NEGATION + MODIFY),
            ),
            "PC-07 (quien produce no modifica su oráculo)",
            radius=NEAR_TIGHT,
        )
        require_any(self, text, COMPETENT_ROLE, "el cambio vuelve al rol competente", "PC-07")
        require_any(self, text, APPROVAL, "un cambio que altera el contrato vuelve a aprobación", "PC-07")
        assert_concepts(
            self,
            text,
            FAVOURABLE,
            (
                ("GREEN (green)", GREEN),
                ("negación (negation)", NEGATION),
            ),
            "PC-07 (nada se cambia desde GREEN para obtener un resultado favorable)",
            radius=NEAR_WIDE,
        )

    def test_the_norm_states_the_six_role_boundaries(self) -> None:
        """PC-08: las fronteras documentales de los seis roles."""
        text = read_document(NORM, "PC-08: la casa normativa documental")
        for role in ALL_ROLE_SOURCES:
            with self.subTest(role=role):
                assert_concepts(
                    self,
                    text,
                    ROLE_ANCHORS[role],
                    ROLE_OBLIGATIONS[role],
                    f"PC-08 ({role})",
                    radius=NEAR_WIDE,
                )


# ---------------------------------------------------------------------------
# Promesa C — un verde estructural no es aceptación semántica (PC-09…PC-12)
# ---------------------------------------------------------------------------


class TestPromiseC(unittest.TestCase):
    """Promesa C: un verde estructural no se presenta como aceptación semántica.

    Protege PC-09…PC-12, INV-06, INV-07 e INV-08. Tarea T3.
    """

    maxDiff = None

    def test_the_norm_separates_structural_control_from_semantic_review(self) -> None:
        """PC-09/PC-10/INV-06/INV-08: dos registros separados y los límites de
        la comprobación estructural."""
        text = read_document(NORM, "PC-09: la casa normativa documental")

        require_any(self, text, STRUCTURAL_CONTROL, "control automático/estructural", "PC-09")
        require_any(self, text, SEMANTIC_REVIEW, "revisión semántica independiente", "PC-09")
        require_any(self, text, RESULT, "resultado", "PC-09")
        require_any(self, text, SCOPE, "alcance", "PC-09")
        require_any(self, text, LIMITATION, "limitaciones", "PC-09")
        require_any(self, text, CLAIMS, "afirmaciones examinadas", "PC-09")
        require_any(self, text, FINDINGS, "hallazgos", "PC-09")
        require_any(self, text, ABSTENTIONS, "abstenciones", "PC-09")

        # PC-10: la presencia de secciones/etiquetas/archivos/referencias
        # resolubles no demuestra fidelidad, suficiencia ni verdad semántica.
        assert_concepts(
            self,
            text,
            PRESENCE,
            (
                ("negación (negation)", NEGATION),
                ("fidelidad/suficiencia/verdad (fidelity/sufficiency/truth)", FIDELITY),
            ),
            "PC-10 (presencia no demuestra fidelidad)",
        )
        # PC-10: un recibo de transporte o la aceptación estructural del
        # paquete tampoco acreditan revisión semántica.
        assert_concepts(
            self,
            text,
            RECEIPT,
            (
                ("transporte/entrega (transport/delivery)", TRANSPORT),
                ("negación (negation)", NEGATION),
                ("semántica (semantic)", ("semantic", "semantica")),
            ),
            "PC-10 (recibo de transporte no acredita revisión semántica)",
        )
        # PC-10/INV-08: una obligación textual o un paquete NO es un sandbox
        # ni demuestra ausencia de escrituras transitorias.
        assert_concepts(
            self,
            text,
            SANDBOX,
            (
                ("negación (negation)", NEGATION),
                ("escrituras transitorias (transient writes)", TRANSITORY),
            ),
            "PC-10/INV-08 (obligación o paquete no es sandbox)",
        )

    def test_the_norm_requires_contrast_with_sources_and_owner_acceptance(self) -> None:
        """PC-11/PC-12/INV-07: contraste con fuentes, alcance real y aceptación
        funcional en el usuario/dueño que aprueba.

        INV-07 (A5) se verifica además como AUSENCIA del nombre del aprobador
        de esta unidad en ``skills/``, ``sources/`` y ``agents/``, con control
        de vacuidad.
        """
        text = read_document(NORM, "PC-11: la casa normativa documental")

        assert_concepts(
            self,
            text,
            CLAIMS,
            (("fuentes (sources)", SOURCE),),
            "PC-11 (contraste de afirmaciones con fuentes)",
        )
        require_any(self, text, INSUFFICIENT_SUPPORT, "respaldo insuficiente", "PC-11")
        require_any(self, text, CONTRADICTION, "contradicciones", "PC-11")
        require_any(self, text, OMITTED, "contradicciones omitidas", "PC-11")
        require_any(
            self,
            text,
            DOES_NOT_SUPPORT,
            "referencias que existen pero no sostienen lo afirmado",
            "PC-11",
        )
        require_any(self, text, REAL_SCOPE, "la revisión declara su alcance real", "PC-11")
        assert_concepts(
            self,
            text,
            INFALLIBLE,
            (("negación (negation)", NEGATION),),
            "PC-11 (no promete detección infalible)",
            radius=NEAR_TIGHT,
        )

        require_any(
            self, text, FUNCTIONAL_ACCEPTANCE, "aceptación funcional", "PC-12"
        )
        assert_concepts(
            self,
            text,
            FUNCTIONAL_ACCEPTANCE,
            (
                ("usuario/dueño (user/owner)", APPROVING_OWNER),
                ("aprueba (approves)", APPROVES),
            ),
            "PC-12 (la aceptación corresponde al usuario/dueño)",
        )
        assert_concepts(
            self,
            text,
            PENDING,
            (
                ("impide (prevents)", PREVENT),
                ("contrato (contract)", CONTRACT),
            ),
            "PC-12 (sin pendientes que impidan acreditar el contrato)",
            radius=NEAR_WIDE,
        )
        require_any(
            self,
            text,
            VISIBLE,
            "los pendientes admisibles permanecen visibles",
            "PC-12",
        )

        # INV-07 / A5: el nombre concreto del aprobador de esta unidad vive
        # sólo en sus documentos de autoridad bajo docs/.
        approver = fold(APPROVER_NAME)
        self.assertIn(
            approver,
            fold("prefijo " + APPROVER_NAME + " sufijo"),
            "control de vacuidad roto: el detector no reconoce el nombre del aprobador.",
        )
        self.assertNotIn(
            approver,
            fold("texto sin el nombre del aprobador"),
            "control de vacuidad roto: el detector marca un texto que NO nombra al aprobador.",
        )
        documents = installable_documents()
        self.assertGreater(
            len(documents),
            0,
            "INV-07: no se recolectó ningún archivo del árbol instalable.",
        )
        offenders = sorted(
            relpath for relpath, document in documents if approver in fold(document)
        )
        self.assertEqual(
            offenders,
            [],
            "INV-07: el nombre del aprobador de esta unidad aparece en texto "
            f"instalable (debe vivir sólo bajo docs/): {offenders[:10]!r}",
        )


# ---------------------------------------------------------------------------
# Promesa D — los criterios llegan por las vías existentes (PC-13…PC-16)
# ---------------------------------------------------------------------------


class TestPromiseD(unittest.TestCase):
    """Promesa D: los criterios llegan por las vías existentes sin ampliar
    autoridad (PC-13…PC-16, INV-01).

    Reparto T3/T4 (A8): la casa, la fila de ``SKILL.md`` y las seis fuentes
    son T3; la unicidad sobre el árbol final, los cinco bloques, los agentes y
    la instalación son T4.
    """

    maxDiff = None

    def test_the_norm_lives_in_one_house_listed_in_the_reference_table(self) -> None:
        """PC-13/INV-01 (T3): la casa existe y es localizable desde la tabla de
        referencias de ``SKILL.md``."""
        text = read_document(NORM, "PC-13/T3: la casa normativa documental")
        self.assertGreater(
            len(text.strip()),
            200,
            "PC-13/T3: la casa normativa existe pero no enuncia una norma "
            f"(contenido: {len(text.strip())} bytes).",
        )
        skill = read_document(SKILL_MD, "PC-13/T3: skills/cdad-cycle/SKILL.md")
        self.assertTrue(
            reference_row(skill, POINTER),
            "PC-13/T3: la tabla «How to read the references» de SKILL.md no "
            f"tiene una fila que nombre `{POINTER}`.",
        )

    def test_no_installable_surface_copies_the_normative_phrases(self) -> None:
        """PC-13/INV-01 (T4: mide el árbol final): ningún consumidor reproduce
        las frases normativas de la referencia.

        A1: se miden las unidades normativas de TODA la referencia (oraciones
        de ≥6 palabras y líneas de ≥8, umbrales del precedente), con espacios
        normalizados, sobre ``skills/``, ``sources/`` y ``agents/``,
        excluyendo la propia referencia. Control de vacuidad incluido.
        """
        text = read_document(NORM, "PC-13/T4: la casa normativa documental")
        units = normative_units(text)
        self.assertTrue(
            units,
            "PC-13/T4: la referencia no tiene frases normativas derivables "
            "(sin texto no hay unicidad que medir).",
        )
        probe = " ".join(units[0].split()[: max(4, len(units[0].split()) // 2)])
        self.assertEqual(
            copies_of([probe], [("sintetico.md", "otra cosa")]),
            [],
            "control de vacuidad roto: el detector marca un texto que NO "
            "contiene la frase.",
        )
        self.assertTrue(
            copies_of([probe], [("sintetico.md", "prefijo " + probe + " sufijo")]),
            "control de vacuidad roto: el detector NO detecta una copia sintética "
            "(ni siquiera re-ajustada).",
        )
        self.assertTrue(
            copies_of(units, [(NORM_RELPATH, text)]),
            "control de vacuidad roto: el detector no reconoce las propias "
            "frases de la referencia.",
        )
        documents = [
            (relpath, document)
            for relpath, document in installable_documents()
            if relpath != NORM_RELPATH
        ]
        self.assertGreater(
            len(documents),
            0,
            "PC-13/T4: no se recolectó ningún archivo del árbol instalable.",
        )
        offenders = copies_of(units, documents)
        self.assertEqual(
            offenders,
            [],
            "PC-13/T4: un consumidor reproduce frases normativas de la "
            f"referencia (los consumidores remiten; parafrasean): {offenders[:10]!r}",
        )

    def test_the_six_role_sources_and_five_blocks_carry_their_obligation_and_pointer(
        self,
    ) -> None:
        """PC-14: las seis fuentes de rol (T3) y los cinco bloques estáticos
        (T4) llevan su obligación documental y el puntero."""
        for role in ALL_ROLE_SOURCES:
            with self.subTest(role=role, task="T3"):
                text = read_document(
                    ROLE_SOURCES[role], f"PC-14/T3: sources/roles/{role}.md"
                )
                self.assertTrue(
                    POINTER in text,
                    f"PC-14/T3: la fuente del rol {role} no apunta a la casa "
                    f"normativa (falta `{POINTER}`).",
                )
                assert_concepts(
                    self,
                    text,
                    ("documental", "documentary", "encargo", "engagement"),
                    ROLE_OBLIGATIONS[role],
                    f"PC-14/T3: obligación documental de {role}",
                    radius=NEAR_WIDE,
                )

        for role, path in ROLE_BLOCKS.items():
            with self.subTest(role=role, task="T4"):
                text = read_document(
                    path, f"PC-14/T4: skills/cdad-cycle/packets/roles/{role}.md"
                )
                self.assertTrue(
                    POINTER in text,
                    f"PC-14/T4: el bloque estático del rol {role} no apunta a la "
                    f"casa normativa (falta `{POINTER}`).",
                )
                assert_concepts(
                    self,
                    text,
                    ("documental", "documentary"),
                    ROLE_MINIMUM[role],
                    f"PC-14/T4: obligación mínima documental de {role}",
                    radius=NEAR_WIDE,
                )

    def test_generated_and_promoted_agents_of_both_runtimes_carry_the_obligations(
        self,
    ) -> None:
        """PC-14 (T4): los agentes generados y promovidos de los dos runtimes,
        incluidas sus variantes Odoo, conservan las obligaciones."""
        disposable = disposable_product()
        run = disposable["run"]
        assert isinstance(run, subprocess.CompletedProcess)
        self.assertEqual(
            run.returncode,
            0,
            "PC-14/T4: `make agents` falló en la copia descartable (rc="
            f"{run.returncode}):\n{run.stdout}\n{run.stderr}",
        )
        product = disposable["product"]
        assert isinstance(product, Path)
        staging_root = product / STAGING_AGENTS

        for runtime in RUNTIMES:
            for name in AGENT_NAMES:
                role = role_of_agent(name)
                label = f"PC-14/T4: agente generado {runtime}/{name}"
                with self.subTest(runtime=runtime, agent=name, task="T4"):
                    path = staging_root / runtime / name
                    self.assertTrue(
                        path.is_file(),
                        f"{label}: `make agents` no publicó el agente declarado.",
                    )
                    text = path.read_text(encoding="utf-8", errors="replace")
                    self.assertTrue(
                        POINTER in text,
                        f"{label}: el agente no apunta a la casa normativa "
                        f"(falta `{POINTER}`).",
                    )
                    assert_concepts(
                        self,
                        text,
                        ("documental", "documentary"),
                        ROLE_MINIMUM[role],
                        label,
                        radius=NEAR_WIDE,
                    )

        for runtime, promoted_dir in PROMOTED_DIRS.items():
            for name in AGENT_NAMES:
                role = role_of_agent(name)
                label = f"PC-14/T4: agente promovido {runtime}/{name}"
                with self.subTest(runtime=runtime, agent=name, task="T4"):
                    path = REPO_ROOT / promoted_dir / name
                    self.assertTrue(
                        path.is_file(),
                        f"{label}: falta el agente promovido (correr `make agents`).",
                    )
                    text = path.read_text(encoding="utf-8", errors="replace")
                    self.assertTrue(
                        POINTER in text,
                        f"{label}: el agente no apunta a la casa normativa "
                        f"(falta `{POINTER}`): hay que correr `make agents`.",
                    )
                    assert_concepts(
                        self,
                        text,
                        ("documental", "documentary"),
                        ROLE_MINIMUM[role],
                        label,
                        radius=NEAR_WIDE,
                    )

    def test_isolated_install_distributes_the_reference_with_source_bytes(self) -> None:
        """PC-15 (T4): la instalación aislada distribuye la referencia y los
        consumidores con los bytes esperados.

        A6: la referencia con los bytes de la fuente en cada destino ``skills/``
        que publica el instalador (los declaran sus tests); los agentes con los
        bytes de staging. No se toca la instalación global ni el HOME real.
        """
        self.assertEqual(
            len(SKILLS_DESTINATIONS),
            2,
            "drift del oráculo PC-15/T4: los tests del instalador declaraban dos "
            "destinos `skills/cdad-cycle` y se encontraron "
            f"{list(SKILLS_DESTINATIONS)!r}.",
        )
        product = product_root()
        source = product / NORM_RELPATH
        self.assertTrue(
            source.is_file(),
            f"PC-15/T4: la referencia no existe en la raíz de producto "
            f"({relative(source)}): T3 debe publicarla antes de instalar.",
        )
        source_bytes = source.read_bytes()
        staging_root = product / STAGING_AGENTS

        with tempfile.TemporaryDirectory(prefix="cdad-010-001-install-") as tmp:
            install_root = Path(tmp)
            env = os.environ.copy()
            env["CDAD_INSTALL_ROOT"] = str(install_root)
            env["CDAD_SKILL_EXTRA_DIRS"] = ""
            result = subprocess.run(
                ["bash", str(product / "install.sh")],
                cwd=str(product),
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(
                result.returncode,
                0,
                "PC-15/T4: la instalación aislada falló (rc="
                f"{result.returncode}):\n{result.stdout}\n{result.stderr}",
            )

            for destination in SKILLS_DESTINATIONS:
                with self.subTest(destination=destination, task="T4"):
                    installed = (
                        install_root / destination / "references" / POINTER
                    )
                    self.assertTrue(
                        installed.is_file(),
                        f"PC-15/T4: la instalación no publicó la referencia en "
                        f"`{destination}/references/{POINTER}`.",
                    )
                    self.assertEqual(
                        installed.read_bytes(),
                        source_bytes,
                        f"PC-15/T4: los bytes instalados de la referencia en "
                        f"`{destination}` no coinciden con los bytes de la fuente.",
                    )

            for runtime in RUNTIMES:
                for name in AGENT_NAMES:
                    with self.subTest(runtime=runtime, agent=name, task="T4"):
                        staged = staging_root / runtime / name
                        self.assertTrue(
                            staged.is_file(),
                            f"PC-15/T4: staging no publicó el agente "
                            f"{runtime}/{name} (correr `make staging`).",
                        )
                        installed = install_root / INSTALLED_AGENTS_DIRS[runtime] / name
                        self.assertTrue(
                            installed.is_file(),
                            f"PC-15/T4: la instalación no publicó el agente "
                            f"{runtime}/{name} en "
                            f"`{INSTALLED_AGENTS_DIRS[runtime]}`.",
                        )
                        self.assertEqual(
                            installed.read_bytes(),
                            staged.read_bytes(),
                            f"PC-15/T4: los bytes instalados del agente "
                            f"{runtime}/{name} no coinciden con los bytes de "
                            "staging.",
                        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
