#!/usr/bin/env python3
"""003-007 T4 RED — regla de encargo como unidad despachable (D9/R-4),
declaración de clases living/contract en el bloque "Continuity wiring"
(BL-1), y resume/reconcile/trigger de solo lectura con `resume` como primer
paso de una sesión nueva (P10 + punto (d) de discovery-probe-decision.md).

Contract:
- docs/specs/003-007-living-continuity/spec.md P10 ("regla de encargo
  reconciliada y declaración de clases en el orquestador") y criterio de
  aceptación 9 ("test de coherencia").
- docs/specs/003-007-living-continuity/plan.md T4: focales declarados este
  archivo + tests/test_003_006_t3_receive_wiring.py; "Validación: el agente
  regenerado expresa la unidad despachable, la trazabilidad
  test↔postcondición, el diff acotado, el ejemplo RED/GREEN y la
  declaración de clases del wiring".
- docs/specs/003-007-living-continuity/discovery-probe-decision.md punto
  (d): el cableado dice que `resume`, `reconcile` y `trigger` son de SOLO
  LECTURA y que `resume` es el PRIMER PASO de toda sesión nueva que retoma
  trabajo; el RED de T4 lo verifica en el agente regenerado.
- Decisión D9 (spec §8): texto de la regla con el ejemplo RED/GREEN como
  despachos separados; bloque "Continuity wiring" declara `living`
  (ledgers, debt.md, Memory Bank, borradores de cierre/enmienda) y
  `contract` (spec/plan aprobados, docs/cdad-policy.json, state con
  `fields` de autoridad) — o puntero estricto a la sección de clases de
  continuity.md.

Superficie observable (documentación de comportamiento, NO plumbing):
- sources/roles/orchestrator.md (fuente canónica editable);
- agents/cdad-orchestrator.md y agents/claude-code/cdad-orchestrator.md
  (agentes regenerados como ARTEFACTOS DE SALIDA del pipeline `make
  agents`; se leen solo para asertar texto observable, decisión declarada
  del orquestador — nota de la tarea; su pipeline NO se lee).

Estado hoy (probes 2026-10-08) y fallos esperados del RED:
- (a) la regla de encargo aún dice "one postcondition, one test, one diff;
  do not group sub-phases": NO expresa la unidad despachable plan-task /
  TDD-subphase, ni el ejemplo RED/GREEN como despachos separados.
- (b) el bloque "Continuity wiring" NO clasifica referencias
  living/contract ni tiene puntero a la sección de clases.
- (d) el cableado NO declara resume/reconcile/trigger de solo lectura ni
  `resume` como primer paso de la sesión nueva.
Todos los fallos del RED son AssertionError sobre el TEXTO AUSENTE/PRESENTE
(nunca ImportError ni sintaxis). Los GUARDs que ya pasan hoy (trazabilidad
≥1 test por postcondición y diff acotado como CONCEPTOS ya presentes en el
texto viejo; coherencia fuente↔agentes; señales del cableado 003-006-T3)
se declaran como guards: tras el GREEN deben SEGUIR pasando con el texto D9.

RED mínimo (paquete; suite completa NO; nunca background; stdin cerrado):
    env -u TMPDIR python3 -m pytest -q \
        tests/test_003_007_t4_atomic_unit_rule.py < /dev/null
Regresión focal constante (verde hoy):
    env -u TMPDIR python3 -m pytest -q \
        tests/test_003_006_t3_receive_wiring.py < /dev/null
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Cuerpos operativos del orquestador (fuente + agentes regenerados).
ORCH_REL = "sources/roles/orchestrator.md"
AGENT_RELS = (
    ORCH_REL,
    "agents/cdad-orchestrator.md",
    "agents/claude-code/cdad-orchestrator.md",
)
DOC_PATHS = {rel: REPO_ROOT / rel for rel in AGENT_RELS}


def doc_text(rel: str) -> str:
    """Texto del cuerpo operativo tal cual (la fuente es canónica; los
    agentes llevan banner/frontmatter del generador, que no afecta las
    señales por párrafo/bloque)."""
    return DOC_PATHS[rel].read_text(encoding="utf-8")


def paragraph_units(text: str) -> list[str]:
    """Párrafos redacción-tolerantes: bloques separados por línea(s)
    vacía(s), con líneas unidas y marcas de lista/encabezado quitadas."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        joined = " ".join(
            ln.strip().lstrip("#").strip().lstrip("- ").lstrip("* ").strip()
            for ln in para.splitlines() if ln.strip())
        if joined:
            out.append(joined)
    return out


def rule_pars(text: str) -> list[str]:
    """Párrafos de la REGLA DE ENCARGO: el (los) párrafo(s) que definen
    qué transporta el paquete/handoff (unidad despachable). Anclas de
    selección robustas a la reescritura D9: 'dispatchable' (unidad
    despachable), 'atomic task' (texto viejo), 'encargo'."""
    marks = re.compile(
        r"dispatchable|atomic task|encargo|packet/handoff carries",
        re.IGNORECASE)
    return [u for u in paragraph_units(text) if marks.search(u)]


def wiring_block(text: str) -> str:
    """Cuerpo del bloque `Continuity wiring` (desde su encabezado — con o
    sin '#' — hasta el siguiente bloque: `Re-entry wiring`, `Procedure
    detail` o cualquier encabezado markdown)."""
    lines = text.splitlines()
    start = end = None
    for i, raw in enumerate(lines):
        if re.match(r"^#{0,6}\s*Continuity wiring", raw):
            start = i
            continue
        if start is not None and (
            re.match(r"^#{0,6}\s*(Re-entry wiring|Procedure detail)", raw)
            or re.match(r"^#{1,6}\s", raw)
        ):
            end = i
            break
    if start is None:
        return ""
    return "\n".join(lines[start:end if end is not None else len(lines)])


def wiring_units(text: str) -> list[str]:
    """Párrafos del bloque Continuity wiring ("" si el bloque no existe)."""
    block = wiring_block(text)
    return paragraph_units(block) if block.strip() else []


# ------------------------------------------------------------ predicados


def rule_has(text: str, pattern: str) -> bool:
    """La regla de encargo (párrafos anclados) contiene `pattern`."""
    pat = re.compile(pattern, re.IGNORECASE)
    return any(pat.search(u) for u in rule_pars(text))


def wiring_has(text: str, pattern: str) -> bool:
    """El bloque Continuity wiring contiene `pattern`."""
    pat = re.compile(pattern, re.IGNORECASE)
    return any(pat.search(u) for u in wiring_units(text))


# señales P10 como predicados (compartados por los tests y la coherencia)
SIGNALS: dict[str, str] = {
    # (a) unidad despachable: una tarea del plan...
    "rule-plan-task": r"plan",
    # ...o una subfase TDD
    "rule-tdd-subphase": r"tdd",
    # diff acotado y revisable
    "rule-scoped-diff": r"diff",
    # cada postcondición trazada a ≥1 test
    "rule-test-per-postcondition": r"postcondition|postcondici",
}

SUBPHASE_RX = r"sub-?phases?"
SCOPED_RX = r"scop|revis|re-?view|acotado"
GROUPING_RX = r"never|do not|don't|without|sin |no agrup|not group"
FIRST_STEP_RX = r"first step|primer paso|first\b|primero"
NEW_SESSION_RX = r"sesión nueva|nueva sesión|new session|start|iniciar|inicio"
READ_ONLY_RX = r"read[ -]?only|solo lectura|sólo lectura"
LIVING_ENUM_RX = r"ledger|debt\.md|memory bank|borrador|draft"
CONTRACT_CONTENT_RX = r"spec|plan|policy|state|fields|aprobado"
CLASSES_POINTER_RX = (
    r"continuity\.md[^\n]{0,160}\b(class|classes|living)\b"
    r"|\b(class|classes|living)\b[^\n]{0,160}continuity\.md")


# ---------------------------------------------------------------- tests


class T4AtomicUnitRule(unittest.TestCase):
    """P10(a) — la regla de encargo como UNIDAD DESPACHABLE (D9/R-4):
    una tarea del plan o una subfase TDD (nunca dos subfases en una
    invocación), cada postcondición trazada a ≥1 test, un diff acotado y
    revisable, y el ejemplo RED/GREEN como despachos separados que
    SATISFACE la regla."""

    @classmethod
    def setUpClass(cls):
        cls.texts = {rel: doc_text(rel) for rel in AGENT_RELS}

    def _assert_rule_signal(self, rel: str, text: str, desc: str,
                            pattern: str):
        self.assertTrue(
            rule_has(text, pattern),
            f"P10(a)/D9: {rel} — la regla de encargo NO expresa {desc} "
            f"(patrón {pattern!r}) ⇒ AssertionError por comportamiento "
            f"ausente. Párrafos de la regla: "
            f"{sorted(r[:140] for r in rule_pars(text))}")

    def test_p10a_rule_expresses_single_dispatchable_unit(self):
        """P10(a)/D9: la regla expresa la unidad despachable — una tarea
        del plan O una subfase TDD, nunca dos subfases en una
        invocación — en los tres cuerpos operativos."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                # selector: la regla sigue hablando de la unidad del paquete
                self.assertTrue(
                    rule_pars(text),
                    f"P10(a)/D9: {rel} NO tiene párrafo de regla de encargo "
                    "identificable (anclas dispatchable/atomic task) "
                    "⇒ AssertionError por comportamiento ausente")
                self._assert_rule_signal(
                    rel, text, "la unidad despachable plan-task",
                    r"plan[^\n]{0,80}\btask|task[^\n]{0,40}\bplan\b")
                self._assert_rule_signal(
                    rel, text, "la unidad despachable TDD-subphase",
                    rf"\btdd\b[^\n]{{0,80}}{SUBPHASE_RX}"
                    rf"|{SUBPHASE_RX}[^\n]{{0,80}}\btdd\b")
                self._assert_rule_signal(
                    rel, text, "la prohibición de agrupar dos subfases",
                    rf"{GROUPING_RX}[^\n]{{0,80}}(two|group|agrup|combin)"
                    rf"[^\n]{{0,60}}{SUBPHASE_RX}"
                    rf"|{SUBPHASE_RX}[^\n]{{0,60}}(never|do not|without|sin )")

    def test_p10a_rule_requires_a_test_per_postcondition(self):
        """P10(a): en los tres cuerpos la regla exige CADA postcondición
        trazada a AL MENOS UN test (GUARD: el concepto ya está hoy en el
        texto viejo; tras el GREEN debe sobrevivir en el texto D9)."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                self._assert_rule_signal(
                    rel, text,
                    "la trazabilidad de cada postcondición a ≥1 test",
                    r"postcondition[^\n]{0,120}\b(test|traced)"
                    r"|\btest[^\n]{0,60}postcondition")

    def test_p10a_rule_requires_a_scoped_reviewable_diff(self):
        """P10(a): en los tres cuerpos la regla pide un diff acotado y
        revisable (GUARD: el concepto ya está hoy en el texto viejo; tras
        el GREEN debe sobrevivir en el texto D9)."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                self._assert_rule_signal(
                    rel, text, "el diff acotado y revisable",
                    rf"diff[^\n]{{0,80}}{SCOPED_RX}"
                    rf"|{SCOPED_RX}[^\n]{{0,80}}diff")

    def test_p10a_separated_red_green_dispatch_satisfies_the_rule(self):
        """P10(a)/D9/R-4: en los tres cuerpos la regla dice EXPLÍCITAMENTE
        que una tarea del plan cuyos RED y GREEN son DESPACHOS SEPARADOS
        SATISFACE la regla (ejemplo)."""
        example_rx = (
            r"\bRED\b[^\n]{0,200}\bGREEN\b[^\n]{0,120}"
            r"(sep-?arat|despach|dispatch|satisf)"
            r"|\bGREEN\b[^\n]{0,200}\bRED\b[^\n]{0,120}"
            r"(sep-?arat|despach|dispatch|satisf)"
            r"|(sep-?arat|separad)[^\n]{0,80}dispatch[^\n]{0,120}\bRED\b"
            r"|(sep-?arat|separad)[^\n]{0,80}dispatch[^\n]{0,120}\bGREEN\b")
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                self.assertTrue(
                    re.search(example_rx, text),
                    f"P10(a)/D9/R-4: {rel} NO dice que una tarea cuyos RED "
                    "y GREEN son despachos separados SATISFACE la regla "
                    "(ejemplo D9) ⇒ AssertionError por comportamiento "
                    "ausente. Párrafos de la regla: "
                    f"{sorted(r[:140] for r in rule_pars(text))}")

    def test_p10a_guard_old_parenthetical_removed(self):
        """GUARD P10(a): el paréntesis literal 'one postcondition, one
        test, one diff; do not group sub-phases' YA NO ESTÁ en la regla de
        encargo (el punto (a) exige 'ya no dice'; el reemplazo es D9).
        Hoy FALLA (texto viejo presente); tras el GREEN pasa."""
        offenders = []
        for rel, text in self.texts.items():
            m = re.search(
                r"one postcondition[^\n]{0,10}one test[^\n]{0,10}one diff",
                text, re.IGNORECASE)
            if m:
                offenders.append(f"{rel}: {m.group(0)[:80]}")
        self.assertEqual(
            offenders, [],
            "P10(a)/D9-GUARD: el paréntesis literal 'one postcondition, "
            "one test, one diff; do not group sub-phases' sigue PRESENTE "
            "en la regla de encargo (debe eliminarse y reemplazarse por "
            "la unidad despachable de D9) ⇒ AssertionError por "
            f"comportamiento presente que no debería estar. Ofensores: "
            f"{offenders}")


class T4ContinuityWiringClasses(unittest.TestCase):
    """P10(b)/BL-1 — el bloque `Continuity wiring` clasifica las
    referencias `living` (ledgers, debt.md, Memory Bank, borradores de
    cierre/enmienda) y `contract` (spec/plan aprobados, docs/cdad-policy.
    json, state con fields de autoridad), o tiene un puntero ESTRICTO a la
    sección de clases de `continuity.md`."""

    @classmethod
    def setUpClass(cls):
        cls.texts = {rel: doc_text(rel) for rel in AGENT_RELS}

    def test_p10b_living_class_declared_in_wiring(self):
        """P10(b)/BL-1: el bloque Continuity wiring declara la clase
        `living` y enumera ejemplos (ledgers, debt.md, Memory Bank o
        borradores)."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                self.assertTrue(
                    wiring_has(text, r"\bliving\b"),
                    f"P10(b)/BL-1: {rel} NO declara la clase `living` en "
                    "el bloque Continuity wiring ⇒ AssertionError por "
                    "comportamiento ausente. Unidades del wiring: "
                    f"{sorted(w[:140] for w in wiring_units(text))}")
                self.assertTrue(
                    wiring_has(text, LIVING_ENUM_RX),
                    f"P10(b)/BL-1: {rel} NO enumera ejemplos `living` "
                    "(ledgers/debt.md/Memory Bank/borradores) en el bloque "
                    "Continuity wiring ⇒ AssertionError por comportamiento "
                    "ausente. Unidades del wiring: "
                    f"{sorted(w[:140] for w in wiring_units(text))}")

    def test_p10b_contract_class_declared_or_strict_pointer(self):
        """P10(b)/BL-1: el bloque declara la clase `contract` con contenido
        (spec/plan aprobados, policy, state con fields de autoridad) O un
        puntero ESTRICTO a la sección de clases de continuity.md (el
        pointer genérico 'contracts in continuity.md' preexistente NO
        basta: debe apuntar a las CLASES)."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                declared = re.compile(
                    r"\bcontract", re.IGNORECASE).search(
                        " ".join(wiring_units(text))) and wiring_has(
                            text, CONTRACT_CONTENT_RX)
                pointer = wiring_has(text, CLASSES_POINTER_RX)
                self.assertTrue(
                    declared or pointer,
                    f"P10(b)/BL-1: {rel} NO declara la clase `contract` "
                    "con su contenido NI tiene puntero estricto a la "
                    "sección de clases de continuity.md en el bloque "
                    "Continuity wiring ⇒ AssertionError por comportamiento "
                    "ausente. Unidades del wiring: "
                    f"{sorted(w[:140] for w in wiring_units(text))}")


class T4ReadOnlyResumeFirstStep(unittest.TestCase):
    """P10(c) + punto (d) — el cableado dice que `resume`, `reconcile` y
    `trigger` son de SOLO LECTURA, y que `resume` es el PRIMER PASO de toda
    sesión nueva que retoma trabajo (antes de leer el state a mano)."""

    @classmethod
    def setUpClass(cls):
        cls.texts = {rel: doc_text(rel) for rel in AGENT_RELS}

    def _cmd_read_only_units(self, text: str, command: str) -> list[str]:
        """Párrafos que nombran `command` junto a una marca de SOLO
        LECTURA (redacción-tolerante ES+EN)."""
        cpat = re.compile(rf"\b{re.escape(command)}\b", re.IGNORECASE)
        ro = re.compile(READ_ONLY_RX, re.IGNORECASE)
        return [u for u in dict.fromkeys(paragraph_units(text))
                if cpat.search(u) and ro.search(u)]

    def test_p10c_resume_reconcile_trigger_declared_read_only(self):
        """P10(c)/(d): cada cuerpo declara resume, reconcile y trigger
        como comandos de SOLO LECTURA en el cableado de continuidad."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                missing = [cmd for cmd in ("resume", "reconcile", "trigger")
                           if not self._cmd_read_only_units(text, cmd)]
                cmd_pars = sorted(
                    u[:140] for u in paragraph_units(text)
                    if re.search(r"resume|reconcile|trigger", u, re.I))
                self.assertEqual(
                    missing, [],
                    f"P10(c)/(d): {rel} NO declara {missing} como de solo "
                    "lectura (discovery-probe-decision: la sesión nueva no "
                    "invocó `resume` porque el wiring no lo dice) "
                    "⇒ AssertionError por comportamiento ausente. "
                    f"Párrafos con los comandos: {cmd_pars}")

    def test_p10c_resume_is_first_step_of_a_new_session(self):
        """P10(c)/(d): cada cuerpo dice que `resume` es el PRIMER PASO de
        toda sesión nueva que RETOMA trabajo (antes de reconstruir a
        mano)."""
        for rel, text in self.texts.items():
            with self.subTest(archivo=rel):
                hits = [
                    u for u in dict.fromkeys(paragraph_units(text))
                    if re.search(r"\bresume\b", u, re.IGNORECASE)
                    and re.search(NEW_SESSION_RX, u, re.IGNORECASE)
                    and re.search(FIRST_STEP_RX, u, re.IGNORECASE)]
                resume_pars = sorted(
                    u[:140] for u in paragraph_units(text)
                    if re.search(r"resume", u, re.I))
                self.assertTrue(
                    hits,
                    f"P10(c)/(d): {rel} NO dice que `resume` es el primer "
                    "paso de toda sesión nueva que retoma trabajo "
                    "⇒ AssertionError por comportamiento ausente. "
                    f"Párrafos con `resume`: {resume_pars}")


class T4SourceAgentCoherence(unittest.TestCase):
    """P10 (criterio 9: "test de coherencia") — los agentes regenerados
    reflejan la fuente en las señales de la regla de encargo, el bloque
    Continuity wiring y la señal (d) de solo lectura (GUARD: hoy todos los
    pares coinciden en ausencia; tras el GREEN deben coincidir en
    presencia)."""

    @classmethod
    def setUpClass(cls):
        cls.texts = {rel: doc_text(rel) for rel in AGENT_RELS}

    @staticmethod
    def _signal(text: str, name: str) -> bool:
        if name == "rule-red-green":
            return bool(re.search(
                r"\bRED\b[^\n]{0,200}\bGREEN\b|\bGREEN\b[^\n]{0,200}\bRED\b",
                text))
        if name == "read-only-resume-new-session":
            return bool(re.search(
                rf"\bresume\b[^\n]{{0,200}}{READ_ONLY_RX}"
                rf"|{READ_ONLY_RX}[^\n]{{0,200}}\bresume\b", text,
                re.IGNORECASE))
        pattern = SIGNALS[name]
        if name.startswith("rule-"):
            return rule_has(text, pattern)
        return wiring_has(text, pattern)

    def test_p10_coherence_source_and_regenerated_agents(self):
        """P10/criterio 9: para cada señal, la fuente la contiene SI Y SOLO
        SI cada agente regenerado la contiene (divergencia = el agente no
        refleja `make agents` desde la fuente)."""
        src = self.texts[ORCH_REL]
        for rel in AGENT_RELS[1:]:
            with self.subTest(archivo=rel):
                for name in SIGNALS:
                    src_has = self._signal(src, name)
                    agt_has = self._signal(self.texts[rel], name)
                    self.assertEqual(
                        src_has, agt_has,
                        f"P10/coherencia: {rel} DIVERGE de la fuente "
                        f"{ORCH_REL} en la señal {name} (agente="
                        f"{agt_has}; fuente={src_has}) ⇒ AssertionError "
                        "por incoherencia")


if __name__ == "__main__":
    unittest.main()
