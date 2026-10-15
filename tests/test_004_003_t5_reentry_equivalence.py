#!/usr/bin/env python3
"""RED tests for 004-003 T5 (G1–G3; PD-5/PD-6/PD-7/PD-10; owner decision D4).

Contract: docs/specs/004-003-planning-procedures/spec.md — plan T5: "Regla
documentada e instalable: citar una corrida registrada cuando hay
equivalencia; forzar corrida nueva cuando falla; reconciliación dos-intentos ↔
sin-progreso". Files (G1–G3 table of the spec §5):

- G1 owner: `skills/cdad-cycle/references/re-entry.md` — el re-entry puede
  CITAR una corrida registrada cuando se muestra equivalencia de
  árbol/política/entorno; corrida nueva solo si la equivalencia falla (PD-5,
  PD-6).
- G2 owner: `skills/cdad-cycle/references/stage-3-tdd.md` — el gate "suite
  completa una vez por GREEN / suite completa verde" gana la cláusula de
  equivalencia.
- G3 owners: `re-entry.md` + `SKILL.md` (conducta del orquestador) — regla de
  dos intentos reconciliada con el criterio de información nueva /
  sin progreso (PD-10), sin reintentos ilimitados.
- D4: `re-entry.md` es el dueño canónico ÚNICO de la regla de equivalencia;
  los consumidores derivados (`stage-4-review.md` que generaliza la regla
  solo-reviewer, `SKILL.md`) LA REFERENCIAN, no la copian (PD-12 / invariante
  6: una fuente editable por regla).

Superficie observable: los documentos fuente canónicos del skill (producto
publicado de este repo; mismo precedente que T4 F2/F-A — el doc es el
artefacto cuando el entregable es una regla). El test lee los docs; el
test-writer no leyó ningún documento objetivo antes del GREEN (los oráculos
provienen solo de la spec y del plan aprobados, con marcadores estables, no
frases literales).

Oráculos (marcadores estables, case-insensitive; el texto puede estar en
español o inglés — TRANSLATION-GLOSSARY.md permite ambas lenguas en las
fuentes):

- PD-5/G1: re-entry.md declara una región de EQUIVALENCIA (accent-tolerante)
  que, en conjunto, nombra: la cita de una corrida registrada (cit*
  + corrida registrada/registered), los objetos de equivalencia
  (árbol/branch|tree + política/policy + entorno/environment) y LA EVIDENCIA
  REGISTRADA (path+ruta, línea y commit), y cubre todas las dimensiones de la
  tabla del contrato: versión del producto, versión de tests incluyendo
  cambios sin commitear, selección ejecutada, comando, resultado,
  entorno/config/dependencias y disponibilidad del original.
- PD-6/G1: la misma regla fuerza corrida nueva cuando la equivalencia falla:
  árbol materialmente cambiado / política-snapshot divergente /
  entorno no equivalente re-ejecutan las comprobaciones afectadas antes del
  cierre; la incertidumbre se DECLARA, no se ASUME; y queda fijado el
  discriminador del contrato: "el mismo commit por sí solo ≠ entorno
  equivalente".
- PD-7/G2: focal vs transversal se tratan distinto: una corrección local usa
  pruebas focales; un cambio de contrato compartido o impacto incierto
  amplía — en una misma región de decisión de la regla.
- PD-10/G3: la regla de dos intentos queda reconciliada con el criterio de
  información nueva / sin progreso: un reintento responde a una hipótesis o
  información nueva; la repetición idéntica / sin avance dispara revisión de
  estrategia; sin reintentos ilimitados y sin poder saltar controles ni
  declarar éxito sin evidencia. Exigido en re-entry.md (regla) y en SKILL.md
  (conducta del orquestador, dueño co-canónico según G3).
- G2: stage-3-tdd.md conecta su gate de suite completa con la cláusula de
  equivalencia (o refiere la fuente), para que RED/GREEN y el cierre citen la
  misma regla.
- D4 distribución: stage-4-review.md y SKILL.md refieren re-entry.md
  (generalizar la regla solo-reviewer / gate 3→4). CONTROL ya verde hoy
  (ambos referencian re-entry.md en la línea base); el test protege el GREEN
  contra degradación a segunda copia — el CONTENIDO de la regla lo exigen
  los oráculos de re-entry.md, no los de distribución.

RED esperado: 6 tests AssertionError sobre la regla ausente en la fuente
canónica (PD-5, PD-6, PD-7, PD-10 re-entry, PD-10/G3 SKILL, G2) — no
ImportError ni fallo de sintaxis; 2 tests de distribución (D4) ya verdes hoy
como controles. Los tests no leen código de implementación (cdad_packet.py)
ni tests/.sensitive-patterns.local.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
REENTRY = SKILL_DIR / "references" / "re-entry.md"
STAGE3 = SKILL_DIR / "references" / "stage-3-tdd.md"
STAGE4 = SKILL_DIR / "references" / "stage-4-review.md"
SKILL = SKILL_DIR / "SKILL.md"

# --- marcadores estables (bilingües, case-insensitive) ---------------------

CITE_RE = re.compile(r"\bcit|citat|citing|make reference|referencia\b", re.IGNORECASE)
REGISTERED_RUN_RE = re.compile(r"registrad|recorded|logged", re.IGNORECASE)
RUN_NOUN_RE = re.compile(r"corrida|run|ejecuci|execution", re.IGNORECASE)

EQUIVALENCE_RE = re.compile(r"equivalenc", re.IGNORECASE)

TREE_RE = re.compile(r"[áa]rbol|tree", re.IGNORECASE)
POLICY_RE = re.compile(r"pol[íi]tica|policy", re.IGNORECASE)
ENV_RE = re.compile(r"entorn|environ", re.IGNORECASE)

PRODUCT_VERSION_RE = re.compile(r"versi[óo]n del producto|product version|\bproducto\b|\bproduct\b", re.IGNORECASE)
UNCOMMITTED_RE = re.compile(
    r"sin commitear|sin committing|uncommitted|sin commit", re.IGNORECASE
)
SELECTION_RE = re.compile(r"selecci|selection", re.IGNORECASE)
COMMAND_RE = re.compile(r"comando|\bcommand\b", re.IGNORECASE)
RESULT_RE = re.compile(r"resultado|result|outcome", re.IGNORECASE)
DEPENDENCIES_RE = re.compile(r"dependenc|configuraci|config", re.IGNORECASE)
ORIGINAL_AVAILABLE_RE = re.compile(r"disponibilidad|availability|el original|the original", re.IGNORECASE)

EVIDENCE_PATH_RE = re.compile(r"ruta|path", re.IGNORECASE)
EVIDENCE_LINE_RE = re.compile(r"l[íi]nea|line", re.IGNORECASE)
EVIDENCE_COMMIT_RE = re.compile(r"commit", re.IGNORECASE)

MATERIAL_CHANGE_RE = re.compile(r"material|cambio de l[áa]rbol|tree chang", re.IGNORECASE)
FORCED_NEW_RUN_RE = re.compile(r"nueva corrida|new run|nueva ejecuci|re-ejecut|re-run|forz", re.IGNORECASE)
UNCERTAINTY_DECLARED_RE = re.compile(r"incertid|uncertaint", re.IGNORECASE)
DECLARED_VERB_RE = re.compile(r"declara|declared|no se asume|not assumed", re.IGNORECASE)
ASSUMED_FORBIDDEN_RE = re.compile(r"asum|assum", re.IGNORECASE)
SAME_COMMIT_ALONE_RE = re.compile(r"mismo commit|same commit", re.IGNORECASE)
ALONE_NOT_EQUAL_RE = re.compile(r"solo|alone|por s[íi]|does not imply|≠|no garantiz|not imply", re.IGNORECASE)
BEFORE_CLOSURE_RE = re.compile(r"final|clos|cierre|before closing", re.IGNORECASE)

FOCAL_RE = re.compile(r"focal", re.IGNORECASE)
TRANSVERSAL_RE = re.compile(r"transversal|contrato compartido|shared contract", re.IGNORECASE)
EXPAND_RE = re.compile(r"ampl[íi]|expand|extend", re.IGNORECASE)
LOCAL_RE = re.compile(r"local|correcci[óo]n puntual|localized", re.IGNORECASE)

ATTEMPT_RE = re.compile(r"intento|attempt|retry|reintent|prueba", re.IGNORECASE)
NEW_INFO_RE = re.compile(
    r"nueva informaci|new information|nueva hip[óo]tesis|new hypothesis|hip[óo]tesis",
    re.IGNORECASE,
)
NO_PROGRESS_RE = re.compile(
    r"sin progreso|no progress|sin avance|no avance|sin ganar|stall|blocked|estancado",
    re.IGNORECASE,
)
STRATEGY_REVIEW_RE = re.compile(r"revisi[óo]n de estrategia|strategy review|revisar la estrategia", re.IGNORECASE)
UNLIMITED_RE = re.compile(r"ilimitad|unlimited", re.IGNORECASE)
SKIPPING_RE = re.compile(r"saltar|skipping|sortear|controles|controls", re.IGNORECASE)
EVIDENCE_RE = re.compile(r"evidencia|evidence", re.IGNORECASE)

ONCE_PER_GREEN_RE = re.compile(r"una vez|once", re.IGNORECASE)
GREEN_RE = re.compile(r"green", re.IGNORECASE)

REENTRY_REF_RE = re.compile(r"re-entry", re.IGNORECASE)


def sections(text: str) -> list[str]:
    """Máximas regiones por encabezado markdown; el texto suelto inicial
    cuenta como una región. La regla puede repartir sus dimensiones en
    viñetas dentro de una sección sin romper el oráculo."""
    return [chunk for chunk in re.split(r"(?m)^#{1,6} .*$", text) if chunk.strip()]


def paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def load(path: Path) -> str:
    assert path.is_file(), (
        f"la superficie canónica de la regla no existe: {path} "
        "(PD-5: la regla de re-entry debe estar documentada e instalada)"
    )
    return path.read_text(encoding="utf-8")


def equivalence_regions(text: str) -> list[str]:
    """Regiones (secciones + párrafos) que tratan la equivalencia."""
    hits = set()
    for region in sections(text) + paragraphs(text):
        if EQUIVALENCE_RE.search(region):
            hits.add(region)
    return sorted(hits)


def find_region(text: str, *patterns: re.Pattern[str]) -> str | None:
    """El primer párrafo que contiene TODOS los patrones en conjunto."""
    for para in paragraphs(text):
        if all(p.search(para) for p in patterns):
            return para
    return None


class ReEntryRuleOracle(unittest.TestCase):
    """Base: carga re-entry.md una vez para todo el caso."""

    def setUp(self) -> None:
        self.text = load(REENTRY)


class TestPd5CiteRegisteredRunWithEquivalenceEvidence(ReEntryRuleOracle):
    def test_pd5_reentry_cites_registered_run_when_equivalence_shown(self) -> None:
        """PD-5 / G1: re-entry.md declara la equivalencia y la cita de una
        corrida registrada con TODAS las dimensiones de la tabla del contrato
        (versión del producto; versión de tests incl. cambios sin commitear;
        selección; comando; resultado; entorno/config/dependencias;
        disponibilidad del original; evidencia ruta+línea+commit). RED de
        hoy: la palabra 'equivalencia' no existe en la fuente → AssertionError
        sobre el marcador ausente."""
        self.assertTrue(equivalence_regions(self.text), (
            "re-entry.md no declara ninguna regla de equivalencia; G1 exige "
            "que citar una corrida registrada sea válido mostrando "
            "equivalencia de árbol/política/entorno (PD-5)"
        ))

        regions = equivalence_regions(self.text)
        full = "\n\n".join(regions)

        self.assertRegex(full, CITE_RE, "la regla no declara la CITA de la corrida")
        self.assertRegex(full, REGISTERED_RUN_RE, "la regla no exige corrida REGISTRADA")
        self.assertRegex(full, RUN_NOUN_RE, "la regla no usa la noción de corrida/ejecución")

        for label, pattern in (
            ("árbol|tree", TREE_RE),
            ("política|policy", POLICY_RE),
            ("entorno|environment", ENV_RE),
            ("versión del producto|product", PRODUCT_VERSION_RE),
            ("cambios sin commitear|uncommitted", UNCOMMITTED_RE),
            ("selección", SELECTION_RE),
            ("comando", COMMAND_RE),
            ("resultado", RESULT_RE),
            ("config/dependencias", DEPENDENCIES_RE),
            ("disponibilidad del original", ORIGINAL_AVAILABLE_RE),
            ("evidencia: ruta", EVIDENCE_PATH_RE ),
            ("evidencia: línea", EVIDENCE_LINE_RE),
            ("evidencia: commit", EVIDENCE_COMMIT_RE),
        ):
            self.assertRegex(
                full,
                pattern,
                f"la regla de equivalencia de re-entry.md no nombra {label!r} "
                "(las dimensiones registradas del PD-5 deben cubrir la tabla "
                "del contrato de la spec)",
            )


class TestPd6NewRunForcedWhenEquivalenceFails(ReEntryRuleOracle):
    def test_pd6_material_change_forces_new_run_and_declares_uncertainty(self) -> None:
        """PD-6 / G1: la misma regla de re-entry.md fuerza corrida nueva
        cuando la equivalencia falla; la incertidumbre se declara y no se
        asume; el mismo commit por sí solo no equivale a entorno equivalente;
        las comprobaciones afectadas se re-ejecutan antes del cierre. RED:
        el discriminador del mismo commit y la probición de asunción no
        existen en la fuente."""
        combined = "\n\n".join(equivalence_regions(self.text)) or self.text
        self.assertRegex(combined, FORCED_NEW_RUN_RE, "la regla no fuerza una corrida NUEVA")
        self.assertRegex(combined, MATERIAL_CHANGE_RE, "la regla no declara el cambio material/tree")

        uncertainty = find_region(
            self.text,
            UNCERTAINTY_DECLARED_RE,
            DECLARED_VERB_RE,
            ASSUMED_FORBIDDEN_RE,
        )
        self.assertIsNotNone(
            uncertainty,
            "la regla no declara la incertidumbre condicionada (PD-6: se "
            "declara, no se asume)",
        )

        same_commit = find_region(self.text, SAME_COMMIT_ALONE_RE)
        self.assertIsNotNone(
            same_commit,
            "la regla no declara el caso del MISMO COMMIT (PD-6: no equivale "
            "por sí solo a entorno equivalente)",
        )
        self.assertRegex(same_commit, ALONE_NOT_EQUAL_RE, "el mismo commit no está discriminado con 'por sí solo'")
        self.assertRegex(combined, BEFORE_CLOSURE_RE, "la regla no ancla la re-ejecución antes del cierre/final")


class TestPd7FocalVsTransversalAreDistinct(ReEntryRuleOracle):
    def test_pd7_focal_objects_local_transversal_expands(self) -> None:
        """PD-7: la regla de re-entry distingue focal vs transversal (una
        corrección local usa pruebas focales; un cambio de contrato compartido
        amplía) — mismo marco de decisión, no dos reglas sueltas ni álgebra
        idénticas."""
        decision = find_region(
            self.text,
            FOCAL_RE,
            TRANSVERSAL_RE,
            EXPAND_RE,
            LOCAL_RE,
        )
        self.assertIsNotNone(
            decision,
            "re-entry.md no distingue pruebas focales (corrección local) de la "
            "ampliación transversal (contrato compartido / impacto incierto) "
            "en una misma regla de decisión; el PD-7 exige trato distinto",
        )


class TestPd10TwoAttemptsReconciledWithNoProgress(ReEntryRuleOracle):
    def test_pd10_reentry_reconciles_two_attempts_with_new_info_or_no_progress(self) -> None:
        """PD-10 / G3 en re-entry.md: la regla de dos intentos queda
        reconciliada con el criterio de información nueva / sin progreso —
        reintento con hipótesis o información nueva; repetición idéntica /
        sin avance dispara revisión de estrategia; sin reintentos ilimitados;
        ningún límite salta controles ni declara éxito sin evidencia."""
        combined = "\n\n".join(paragraphs(self.text))
        decision = find_region(
            self.text,
            ATTEMPT_RE,
            NEW_INFO_RE,
            NO_PROGRESS_RE,
        )
        self.assertIsNotNone(
            decision,
            "re-entry.md no concilia dos intentos con el criterio "
            "'respuesta a una hipótesis o información nueva / sin progreso' "
            "(PD-10 / G3)",
        )
        self.assertRegex(
            combined,
            STRATEGY_REVIEW_RE,
            "sin progreso no dispara revisión de estrategia",
        )
        self.assertRegex(combined, UNLIMITED_RE, "no se prohíben reintentos ilimitados")
        self.assertRegex(
            combined,
            SKIPPING_RE,
            "no se prohíbe saltar controles/sortear límites",
        )
        self.assertRegex(
            combined,
            EVIDENCE_RE,
            "no se prohíbe declarar éxito sin evidencia",
        )

    def test_g3_skill_md_carries_orchestrator_conduct(self) -> None:
        """PD-10 / G3 en SKILL.md (dueño co-canónico de la conducta del
        orquestador): el párrafo de conducta ancla intentos ↔ información
        nueva/sin progreso ↔ revisión de estrategia."""
        text = load(SKILL)
        decision = find_region(
            text,
            ATTEMPT_RE,
            NEW_INFO_RE,
            NO_PROGRESS_RE,
        )
        self.assertIsNotNone(
            decision,
            "SKILL.md no reconcilia la regla de dos intentos con 'información "
            "nueva / sin progreso' en un mismo párrafo (G3: conducta del "
            "orquestador)",
        )
        self.assertRegex(
            decision,
            re.compile(r"estrategia|strategy\b", re.IGNORECASE),
            "la conducta de SKILL.md ante reintento sin información nueva / "
            "sin progreso no deriva en la estrategia (revisión de estrategia, "
            "PD-10)",
        )


class TestG2Stage3GateGainsEquivalenceClause(unittest.TestCase):
    def test_g2_stage3_tdd_gate_cites_the_equivalence_clause(self) -> None:
        """G2: el gate 'suite completa una vez por GREEN / suite completa
        verde' de stage-3-tdd.md gana la cláusula de equivalencia (o refiere
        la fuente única), para que el cierre del ciclo cite la misma regla de
        re-entry."""
        text = load(STAGE3)
        gate = find_region(
            text,
            ONCE_PER_GREEN_RE,
            GREEN_RE,
            EQUIVALENCE_RE,
        )
        self.assertIsNotNone(
            gate,
            "stage-3-tdd.md no presenta el gate de suite completa una vez por "
            "GREEN con la cláusula de equivalencia (G2): el cierre del ciclo "
            "no cita la regla única de corridas de re-entry",
        )


class TestG1DistributionReferencesTheCanonicalOwner(unittest.TestCase):
    """D4: los consumidores derivados refieren la fuente canónica
    (re-entry.md). CONTROL verde en RED: tanto stage-4-review.md como
    SKILL.md ya refieren re-entry.md hoy; el test protege el GREEN contra la
    degradación a segunda copia (el contenido de la regla lo exigen los
    oráculos de re-entry.md, no éstos)."""

    def test_d4_stage4_review_references_reentry_rule(self) -> None:
        """D4 / G1: stage-4-review.md (consumidor derivado que generaliza la
        regla solo-reviewer) REFIERE la fuente canónica re-entry; no la
        sustituye en silencio (PD-12, invariante 6: una fuente editable por
        regla, consumidores derivados)."""
        text = load(STAGE4)
        self.assertRegex(
            text,
            REENTRY_REF_RE,
            "stage-4-review.md no refiere re-entry.md (el dueño canónico de "
            "la regla de equivalencia): la regla quedaría duplicada o "
            "invisible para el reviewer",
        )

    def test_d4_skill_md_references_reentry_rule(self) -> None:
        """D4 / G1: SKILL.md (gate 3→4 en la tabla de validaciones) refiere
        re-entry.md como la fuente de la regla de re-entry."""
        text = load(SKILL)
        self.assertRegex(
            text,
            REENTRY_REF_RE,
            "SKILL.md no refiere re-entry.md en su tabla de gates/validación "
            "(gate 3→4): el orquestador no ve la regla citada",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
