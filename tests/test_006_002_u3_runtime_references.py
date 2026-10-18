#!/usr/bin/env python3
"""006-002 U3 RED — retiro de las dos referencias por runtime y `cli-delegation.md`
como contrato del adaptador (PD-9, PD-10; PD-1 sin las exclusiones de U3).

Contrato (oráculo):
- ``docs/specs/006-002-delegation-by-layer/spec.md`` — §1 (tabla de capas),
  §2 PD-9 (``references/opencode-delegation.md`` y
  ``references/claude-code-delegation.md`` salen del árbol instalable; su
  detalle histórico/verificación —recarga y versión, canal ``delegate`` muerto,
  429, procedencia— se preserva bajo ``docs/**`` como evidencia **no
  instalable**; la tabla «How to read the references» pierde las dos filas de
  runtime ``SKILL.md:447-473``) y §2 PD-10 (``cli-delegation.md`` conserva el
  contrato del **adaptador** y pierde la regla de elección de transporte, que se
  muda a la sección ``delegation`` del agente del runtime); §3 INV-1/INV-3.
- ``docs/specs/006-002-delegation-by-layer/plan.md`` — ficha U3 (archivos, gate
  «PD-9 verde; ningún puntero colgante») + enmienda A-1 (los asserts acoplados
  de esta superficie se reformulan en ESTE RED, nunca en el GREEN).
- ``docs/specs/006-002-delegation-by-layer/discovery.md`` §1.2 filas 14/15/16 —
  qué contenido se retira y cuál se preserva (fuente del oráculo de conceptos).

Superficie (caja negra; el oráculo NO se deriva leyendo la implementación): se
LEEN al ejecutarse (a) el árbol instalable ``skills/cdad-cycle/**``,
``skills/cdad-epic/**`` y los agentes GENERADOS ``agents/**`` —el contrato los
declara salida del generador—, y (b) los documentos bajo ``docs/**`` donde PD-9
manda preservar el detalle retirado. Las aserciones usan los nombres y las
superficies que el contrato fija por su ruta, nunca detalles internos.

Cómo se localiza lo que PD-10 retira **por su contenido** (la instrucción del
paquete): la regla de elección de transporte es el bloque que decide el despacho
intra-runtime nombrando el mecanismo NATIVO del runtime (`` `task` `` /
`` `Agent` `` / «native mechanism» / ``subagent_type``) junto a un verbo de
elección de transporte (*choose*, *prefer*, *instead of*, *within the runtime*,
*intra-runtime*). No se fija ninguna línea ni ninguna frase literal.

Mapa test → postcondición (un test por afirmación observable):

  1 ``TestPd9RuntimeReferencesWithdrawn::test_pd9_runtime_references_are_withdrawn_from_the_installable_tree``
    PD-9 (ausencia de las dos referencias en el árbol instalable)
  2 ``TestPd9RuntimeReferencesWithdrawn::test_pd9_history_is_preserved_as_non_installable_evidence_under_docs``
    PD-9 (el detalle retirado existe como evidencia no instalable bajo ``docs/**``)
  3 ``TestPd9RuntimeReferencesWithdrawn::test_pd9_reference_table_drops_the_two_runtime_rows``
    PD-9 (la tabla «How to read the references» no apunta a las dos rutas)
  4 ``TestPd9RuntimeReferencesWithdrawn::test_pd9_no_installable_text_points_to_the_withdrawn_references``
    PD-9 (ningún texto instalable de ``skills/**`` ni de ``agents/**`` apunta a esas rutas)
  5 ``TestPd10CliDelegationIsTheAdapterContract::test_pd10_adapter_contract_concepts_are_conserved``
    PD-10 (mitad de conservación: modos server/service/standalone, preflight,
    espera, recibo/correlación)
  6 ``TestPd10CliDelegationIsTheAdapterContract::test_pd10_transport_choice_rule_is_gone``
    PD-10 (mitad de ausencia: la regla de elección de transporte ya no está)

RED esperado (árbol vigente, U1/U2 ya en GREEN):
- (1) FALLA: las dos referencias siguen instalables (``skills/cdad-cycle/
  references/``).
- (2) FALLA: ningún documento de ``docs/**`` fuera de los de PLANIFICACIÓN de
  esta feature conserva HOY juntos el detalle retirado (recarga/versión, canal
  ``delegate``, 429, procedencia) declarándose evidencia no instalable.
- (3) FALLA: la tabla lleva hoy las dos filas (``SKILL.md`` §«How to read the
  references»).
- (4) FALLA: hay punteros instalables a esas rutas (``SKILL.md``,
  ``references/runtime-adoption.md``, ``references/sub-agent-strategies.md``,
  ``references/cli-delegation.md`` — el diagnóstico del propio test los lista).
- (5) PASA hoy: **GUARD pre-satisfecho** declarado (el contrato del adaptador ya
  está documentado por 005-010 y esta unidad no lo agrega); protege la mitad
  retirada contra un GREEN que borre el documento en vez de podarlo.
- (6) FALLA: el bloque que decide el despacho intra-runtime nombrando el
  mecanismo nativo sigue en ``cli-delegation.md`` (hacia el final del documento,
  como declara la spec PD-10).
Ningún fallo es ImportError/SyntaxError/NameError: todas las superficies
faltantes son aserción de contrato.

Límites honestos declarados:
- El oráculo de (2) NO fija ninguna ruta: acepta cualquier documento de
  ``docs/**`` que se declare evidencia no instalable. Excluye **solo** los
  documentos de planificación de esta feature (spec/plan/discovery/u*-red/
  u*-green), porque son los que *mandan* mover el detalle y aceptarlos volvería
  vacuo el assert (mismo criterio con que U2 excluyó ``context-meter.md``).
- (5) es un guard pre-satisfecho: mide que la conservación sigue ahí, no que esta
  unidad agregue texto del adaptador.
- Los mensajes de falla de (4)/(6) imprimen la procedencia (archivo:línea y un
  encabezado corto) del texto ofensor: es el propio test leyendo el producto por
  diseño, no una lectura de implementación del test-writer.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Árbol instalable de la skill (PD-1/PD-3/PD-9: la misma superficie de U2).
SKILL_ROOTS = (
    REPO_ROOT / "skills" / "cdad-cycle",
    REPO_ROOT / "skills" / "cdad-epic",
)
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"
CLI_REFERENCE = (
    REPO_ROOT / "skills" / "cdad-cycle" / "references" / "cli-delegation.md"
)

# ---------------------------------------------------------------- PD-9
# Las dos referencias por runtime que PD-9 retira del árbol instalable.
WITHDRAWN_REFERENCES = (
    "skills/cdad-cycle/references/opencode-delegation.md",
    "skills/cdad-cycle/references/claude-code-delegation.md",
)
WITHDRAWN_NAMES = ("opencode-delegation.md", "claude-code-delegation.md")

# Superficie instalable que no debe quedar apuntando a las rutas retiradas:
# el árbol de la skill y los agentes GENERADOS (salida declarada del generador).
POINTER_SCAN_ROOTS = (
    REPO_ROOT / "skills",
    REPO_ROOT / "agents",
)

# ------------------------------------------------- evidencia no instalable
# Documentos de PLANIFICACIÓN de esta feature: describen el MOVIMIENTO («el
# detalle se muda a docs/»), no SON el detalle preservado. Exclusión declarada
# (no una ruta fijada): la evidencia puede vivir en cualquier OTRO documento de
# docs/**, incluido uno nuevo en este mismo directorio.
PLANNING_DOC_RE = re.compile(
    r"^(?:spec|plan|discovery|u\d+-(?:red|green))\.md$"
)
PLANNING_DOC_DIR = (REPO_ROOT / "docs" / "specs"
                    / "006-002-delegation-by-layer")

# Marcador de que un documento se declara EVIDENCIA NO INSTALABLE (PD-9).
EVIDENCE_FRAME = (
    "non-installable", "not installable", "no instalable", "not installed",
    "withdrawn", "retirad", "moved to docs", "moved into docs", "historical",
    "histórico", "historia", "history", "evidence", "evidencia", "archive",
    "not shipped", "no se instala", "removed from the skill",
)

# Detalle histórico/verificación que PD-9 manda preservar (spec PD-9; discovery
# §1.2 fila 14), por concepto y con alternativas de idioma.
HISTORY_CONCEPTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("recarga del servidor ya iniciado",
     ("reload", "recarga", "re-load")),
    ("versión que cargó una sesión",
     ("version", "versión")),
    ("canal `delegate`",
     ("`delegate`", "delegate channel", "canal `delegate`", "delegate tool")),
    ("fallback 429",
     ("429",)),
    ("procedencia de la instalación",
     ("provenance", "procedencia")),
)

# ---------------------------------------------------------------- PD-10
# Formas de HERRAMIENTA nativa (spec §2: code-spans y formas de herramienta;
# nunca la palabra suelta *task*).
NATIVE_TOOL_FORM_RE = re.compile(
    r"(?i)`\s*task\s*`|`\s*Agent\s*|\btask tool\b|\bAgent tool\b|"
    r"\bnative mechanism\b|\bnative dispatch\b|\bnative task\b|"
    r"\bsubagent_type\b"
)
# Elección de TRANSPORTE **intra-runtime**: el bloque decide con qué mecanismo
# se despacha DENTRO del runtime (adaptador CLI vs mecanismo nativo). La marca
# intra-runtime es la que distingue la regla retirada del contrato del adaptador
# que se conserva (p. ej. «el adaptador elige el id de sesión» no es una
# elección de transporte).
INTRA_RUNTIME_RE = re.compile(
    r"(?i)\b(?:inside|within)\s+(?:the\s+|a\s+|this\s+)?"
    r"(?:opencode|claude\s*code|runtime|harness|same\s+runtime)\b"
    r"|\bintra-runtime\b|\bsame runtime\b|\bmismo runtime\b"
    r"|\bdelegat\w*\s+(?:inside|within)\b"
)
# Contrato del ADAPTADOR (PD-10: se conserva): modos, preflight, espera,
# recibo/correlación (alternativas de idioma; conceptos, no frases).
ADAPTER_CONTRACT_CONCEPTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("modo server", ("--server", "server mode", "`server`")),
    ("modo service", ("service",)),
    ("modo standalone", ("--standalone", "standalone")),
    ("preflight", ("preflight", "pre-flight", "pre flight")),
    ("espera del resultado", ("wait", "espera", "timeout")),
    ("recibo / correlación de sesión",
     ("receipt", "recibo", "correlation", "correlaci", "--session")),
)


# ---------------------------------------------------------------------------
# Helpers compartidos (los módulos acoplados importan de acá: una sola
# definición de «evidencia no instalable» para toda la feature — PD-9).
# ---------------------------------------------------------------------------


def doc_relative(path: Path) -> str:
    """Ruta relativa a la raíz del repo (para los diagnósticos)."""
    return path.relative_to(REPO_ROOT).as_posix()


def read_document(path: Path, why: str) -> str:
    """Lee una superficie declarada por el contrato. Su ausencia es una
    aserción de contrato (AssertionError), nunca un error de entorno."""
    assert path.is_file(), (
        f"{why}: la superficie declarada por el contrato no existe "
        f"(drift del oráculo): {path}"
    )
    return path.read_text(encoding="utf-8")


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def require_any(text: str, alternatives: tuple[str, ...],
                concept: str) -> str | None:
    """Exige UN concepto con alternativas de idioma (patrón `require_any` de
    005-010 T3 / 006-002 U2): None si está, o el detalle de su falta."""
    lowered = text.lower()
    if any(alternative.lower() in lowered for alternative in alternatives):
        return None
    return (f"concepto ausente '{concept}' "
            f"(alternativas buscadas {list(alternatives)!r})")


def missing_concepts(text: str,
                     concepts: tuple[tuple[str, tuple[str, ...]], ...],
                     ) -> list[str]:
    return [
        detail
        for concept, alternatives in concepts
        if (detail := require_any(text, alternatives, concept))
    ]


def docs_documents() -> list[Path]:
    """Todos los documentos `.md` bajo `docs/**`."""
    return sorted(path for path in (REPO_ROOT / "docs").rglob("*.md")
                  if path.is_file())


def non_installable_evidence_documents() -> list[Path]:
    """Candidatos a evidencia NO instalable (PD-9): todo `docs/**` menos los
    documentos de planificación de esta feature (exclusión declarada: son los
    que mandan mover el detalle, no el detalle)."""
    candidates: list[Path] = []
    for path in docs_documents():
        if (path.parent == PLANNING_DOC_DIR
                and PLANNING_DOC_RE.match(path.name)):
            continue
        candidates.append(path)
    return candidates


def framed_evidence_documents() -> list[Path]:
    """Candidatos que se declaran evidencia no instalable (PD-9): contienen
    algún marcador de `EVIDENCE_FRAME`. Es la superficie sobre la que se
    verifica que el detalle retirado NO se perdió."""
    return [
        path for path in non_installable_evidence_documents()
        if require_any(path.read_text(encoding="utf-8"), EVIDENCE_FRAME,
                       "marcador de evidencia no instalable") is None
    ]


def installable_markdown() -> list[Path]:
    """Texto instalable declarado por PD-9: `skills/**` + agentes `agents/**`."""
    documents: list[Path] = []
    for root in POINTER_SCAN_ROOTS:
        documents.extend(sorted(path for path in root.rglob("*.md")
                                if path.is_file()))
    return documents


def reference_table_region(text: str) -> tuple[str, int, int] | None:
    """Región de la tabla «How to read the references» de `SKILL.md`: del
    encabezado hasta el siguiente `---` o encabezado. Devuelve
    (texto, primera línea, última línea) 1-based, o None (drift)."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if re.match(r"(?i)^#{2,6}\s+How to read the references\s*$", line):
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r"^(?:---\s*$|#{1,6}\s+\S)", lines[index]):
            end = index
            break
    return "\n".join(lines[start:end]), start + 1, end


# ---------------------------------------------------------------------------
# PD-9 — retiro de las dos referencias por runtime, historia preservada
# ---------------------------------------------------------------------------


class TestPd9RuntimeReferencesWithdrawn(unittest.TestCase):
    """PD-9: `references/opencode-delegation.md` y
    `references/claude-code-delegation.md` salen del árbol instalable de la
    skill; su detalle histórico/verificación se preserva bajo `docs/**` como
    evidencia NO instalable; la tabla «How to read the references» pierde las
    dos filas de runtime y ningún texto instalable queda apuntando a esas
    rutas."""

    def test_pd9_runtime_references_are_withdrawn_from_the_installable_tree(
            self) -> None:
        """PD-9: las dos referencias por runtime no existen en el árbol
        instalable (ni en su ruta declarada ni con ese nombre bajo
        `skills/**`) — el mecanismo del runtime vive en su orquestador (D-1)."""
        present = [rel for rel in WITHDRAWN_REFERENCES
                   if (REPO_ROOT / rel).is_file()]
        self.assertEqual(
            present, [],
            msg=(
                "PD-9: las referencias por runtime siguen en el árbol "
                "instalable de la skill (el mismo árbol se copia a las tres "
                "bases: no hay referencia instalable «por runtime»): "
                f"{present!r}"
            ),
        )

        orphans: list[str] = []
        for root in SKILL_ROOTS:
            for name in WITHDRAWN_NAMES:
                orphans.extend(doc_relative(path)
                               for path in root.rglob(name) if path.is_file())
        self.assertEqual(
            orphans, [],
            msg=(
                "PD-9: el nombre de una referencia por runtime reaparece bajo "
                f"skills/**: {orphans!r}"
            ),
        )

        self.assertGreater(
            len(installable_markdown()), 0,
            msg="drift del oráculo PD-9: no se recolectó texto instalable bajo "
                f"{[doc_relative(root) for root in POINTER_SCAN_ROOTS]}",
        )

    def test_pd9_history_is_preserved_as_non_installable_evidence_under_docs(
            self) -> None:
        """PD-9: el detalle histórico/verificación del runtime (recarga del
        servidor ya iniciado y versión que cargó una sesión, canal `delegate`,
        fallback 429, procedencia de la instalación) existe bajo `docs/**` como
        evidencia declarada NO instalable. El oráculo no fija ninguna ruta más
        allá de `docs/` (excluye solo los documentos de planificación de esta
        feature: son los que mandan mover el detalle, no el detalle)."""
        candidates = non_installable_evidence_documents()
        self.assertGreater(
            len(candidates), 0,
            msg="drift del oráculo PD-9: no hay documentos bajo docs/** "
                "fuera de los de planificación de esta feature",
        )

        coverage: list[tuple[int, str, list[str]]] = []
        for path in candidates:
            text = path.read_text(encoding="utf-8")
            missing = missing_concepts(text, HISTORY_CONCEPTS)
            frame = require_any(text, EVIDENCE_FRAME,
                                "marcador de evidencia no instalable")
            coverage.append(
                (len(HISTORY_CONCEPTS) - len(missing), doc_relative(path),
                 missing + ([frame] if frame else []))
            )
        coverage.sort(key=lambda row: (-row[0], row[1]))

        preserved = [row for row in coverage if row[0] == len(HISTORY_CONCEPTS)
                     and not row[2]]
        self.assertTrue(
            preserved,
            msg=(
                "PD-9: el detalle histórico/verificación de las referencias "
                "retiradas no existe como evidencia NO instalable bajo "
                "docs/** (recarga/versión, canal `delegate`, 429, procedencia "
                "—juntos en un mismo documento que se declare no instalable). "
                "Mejores candidatos (conceptos presentes / faltantes): "
                f"{[row[:2] + (row[2][:3],) for row in coverage[:3]]!r} "
                f"sobre {len(candidates)} documentos"
            ),
        )

    def test_pd9_reference_table_drops_the_two_runtime_rows(self) -> None:
        """PD-9: la tabla «How to read the references» de `SKILL.md` no tiene
        filas que apunten a `opencode-delegation.md` ni a
        `claude-code-delegation.md`, y conserva su razón de ser (sigue siendo
        una tabla de referencias: no se satisface vaciándola)."""
        text = read_document(SKILL_MD, "PD-9 (tabla de referencias)")
        region = reference_table_region(text)
        self.assertIsNotNone(
            region,
            msg="drift del oráculo PD-9: SKILL.md no expone la sección "
                "«How to read the references» (superficie declarada por PD-9)",
        )
        assert region is not None
        section, first, last = region

        table_rows = [
            line for line in section.splitlines()
            if re.match(r"^\s*\|.*\.md", line)
        ]
        self.assertGreaterEqual(
            len(table_rows), 5,
            msg=(
                "drift del oráculo PD-9: la tabla «How to read the "
                "references» perdió sus filas (PD-9 retira DOS filas de "
                f"runtime, no la tabla): {table_rows!r}"
            ),
        )

        offenders: list[str] = []
        for name in WITHDRAWN_NAMES:
            for match in re.finditer(re.escape(name), section):
                offenders.append(
                    f"{doc_relative(SKILL_MD)}:"
                    f"{first - 1 + line_of(section, match.start())} — {name}"
                )
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-9: la tabla «How to read the references» sigue apuntando a "
                "las referencias por runtime retiradas (la tabla indexa el "
                f"material de consulta vigente): {offenders!r} "
                f"(sección en líneas {first}-{last})"
            ),
        )

    def test_pd9_no_installable_text_points_to_the_withdrawn_references(
            self) -> None:
        """PD-9: NINGÚN texto instalable (`skills/**`, agentes generados
        `agents/**`) apunta a las rutas retiradas — el puntero a un archivo
        inexistente es el «puntero colgante» que la ficha U3 declara prohibido."""
        documents = installable_markdown()
        self.assertGreater(len(documents), 0, "drift del oráculo PD-9")
        self.assertIn(
            SKILL_MD, documents,
            msg="drift del oráculo PD-9: SKILL.md no está en la superficie "
                "instalable escaneada",
        )

        offenders: list[str] = []
        for path in documents:
            text = path.read_text(encoding="utf-8")
            for name in WITHDRAWN_NAMES:
                for match in re.finditer(re.escape(name), text):
                    offenders.append(
                        f"{doc_relative(path)}:{line_of(text, match.start())} "
                        f"— {name}"
                    )
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-9: hay texto instalable que apunta a las referencias por "
                "runtime retiradas (retirar los archivos deja punteros "
                f"colgantes): {offenders[:20]!r} ({len(offenders)} en total)"
            ),
        )


# ---------------------------------------------------------------------------
# PD-10 — `cli-delegation.md` es el contrato del adaptador (y nada más)
# ---------------------------------------------------------------------------


class TestPd10CliDelegationIsTheAdapterContract(unittest.TestCase):
    """PD-10: la referencia conserva el contrato del ADAPTADOR (modos
    server/service/standalone, preflight, espera, recibo/correlación) y pierde
    la regla de elección de transporte, que se muda a la sección `delegation`
    del agente del runtime."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_document(CLI_REFERENCE, "PD-10")

    def test_pd10_adapter_contract_concepts_are_conserved(self) -> None:
        """PD-10 (conservación): el contrato del adaptador sigue documentado —
        modos server/service/standalone, preflight, espera del resultado y
        recibo/correlación de sesión (conceptos con alternativas; la prosa la
        juzga el review). GUARD pre-satisfecho: pasa hoy y protege contra un
        GREEN que borre el documento en vez de podar la regla de transporte."""
        missing = missing_concepts(self.text, ADAPTER_CONTRACT_CONCEPTS)
        self.assertEqual(
            missing, [],
            msg=(
                "PD-10: `cli-delegation.md` perdió conceptos del contrato del "
                "adaptador (la unidad retira la regla de elección de "
                f"transporte, no el contrato): {missing}"
            ),
        )

    def test_pd10_transport_choice_rule_is_gone(self) -> None:
        """PD-10 (ausencia): ningún bloque de `cli-delegation.md` decide el
        despacho DENTRO del runtime (intra-runtime) nombrando el mecanismo
        NATIVO del runtime — esa regla vive en la sección `delegation` del
        orquestador del runtime (D-1). Se localiza por CONTENIDO (no por línea
        ni por frase literal); el contrato del adaptador que se conserva (p. ej.
        el adaptador elige el id de sesión y lo pasa con `--session`) NO es una
        elección de transporte intra-runtime y no debe caer en el oráculo."""
        text = self.text
        blocks: list[tuple[int, str]] = []
        offset = 0
        for raw in re.split(r"\n\s*\n", text):
            first = offset
            offset += len(raw) + 2
            if raw.strip():
                blocks.append((first, raw.strip()))

        offenders: list[str] = []
        for start, block in blocks:
            native = NATIVE_TOOL_FORM_RE.search(block)
            intra = INTRA_RUNTIME_RE.search(block)
            if native and intra:
                head = block.splitlines()[0][:70]
                offenders.append(
                    f"{doc_relative(CLI_REFERENCE)}:"
                    f"{line_of(text, start)} — bloque «{head}» "
                    f"(mecanismo nativo {native.group(0)!r} + "
                    f"marca intra-runtime {intra.group(0)!r})"
                )
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-10: `cli-delegation.md` todavía contiene la regla de "
                "elección de transporte (un bloque que decide el despacho "
                "intra-runtime nombrando el mecanismo NATIVO del runtime): la "
                "regla se muda a la sección `delegation` del orquestador del "
                f"runtime: {offenders[:6]!r} ({len(offenders)} en total)"
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
