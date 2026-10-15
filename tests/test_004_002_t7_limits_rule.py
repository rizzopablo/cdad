#!/usr/bin/env python3
"""004-002 T7 L-1 RED — regla general de límites inlineada en TODO prompt de
rol generado.

Contrato: docs/specs/004-002-project-execution-bootstrap/spec.md
(PD-7: los scopes derivados llegan completos a los prompts; PD-8: los
agentes generados en .opencode/agents/ proceden de las fuentes canónicas
y no son otra fuente editable) + decisión del dueño (2026-10-02): los
límites mecánicos del arnés son moderados y pueden no existir según el
proyecto (Go mezcla tests y código; hay ciclos CDAD sin código: documentos,
configuración, multimedia); en OpenCode la escritura no está acotada por
ruta (W-3, guía project-execution.md §7). La base de la disciplina es el
PROMPT del rol más la auditoría del orquestador.

Origen del hallazgo: la auditoría del review-fix-008 mostró que los agentes
generados agents/cdad-implementer.md y agents/cdad-reviewer.md (y sus
variantes -odoo) no inlinean la regla general de límites del núcleo
compartido (sources/, "limits-core": "Unexpected denial of legitimate work
→ brief diagnosis to the orchestrator; no equivalent retries"); solo
aparece un puntero ("Shared limits core ... composed into this agent").

Postcondición L-1 (encargo del paquete red-021): para cada rol generado
(architect, test-writer, implementer, reviewer, scribe y sus variantes
-odoo), el texto del agente debe contener explícitamente tres ideas:

  (a) su alcance: qué puede escribir y qué no (ya suele existir: el control
      positivo de este test solo exige que exista, no lo duplica);
  (b) escribir fuera del alcance o sortear un límite NO adelanta el trabajo:
      el orquestador lo detecta en la auditoría (git diff contra el
      write_scope) y el resultado se invalida;
  (c) si un límite (permiso, denegación, alcance) impide una tarea
      legítima, el rol se detiene y reporta el bloqueo al orquestador con
      evidencia (qué intentó, qué se denegó), sin reintentos equivalentes
      ni rodeos (bash, otra herramienta, otra ruta).

Oráculo (marcadores estables, no frases literales — encargo red-021): se
exige que UN MISMO párrafo del texto del agente contenga:

  (b) "invalid*" (invalid / invalida / invalidated / invalidado) + "audit"
      (audit / auditoría / audits) + una noción de trabajo fuera del scope
      (out/outside of scope / fuera del alcance|scope / write_scope);
  (c) "denied/denial/deneg" + "stop/report" + "retry/reintent/workaround/
      bypass/circumvent/sortear/rodeo".

RED hoy (marcador nuevo): la idea (b) no existe en ningún agente generado
y la idea (c) solo aparece en architect como bullet PD-15 acotado (sin
"stop/report"); la conjunción falla en los 10 → RED por AssertionError
sobre postcondición ausente, no por import/sintaxis. El control (a) queda
verde hoy y aísla el RED en la regla faltante.

Superficie observable: los agentes generados agents/cdad-*.md del repo
(producto publicado del generador, fuente declarada de los derivados
I9; mismo precedente que test_004_002_t5_runtime.py / t7_w2, que los
copian, y test_004_001_t6.py, que lee texto de agentes instalados como
superficie semántica). Los derivados deben ser byte-idénticos salvo los
mapas read/grep/glob/edit (PD-8, test_004_002_t5_runtime), por lo que
verificar la fuente cubre el derivado publicado. Lecturas autorizadas
explícitamente por el encargo; no se lee tests/.sensitive-patterns.local.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = REPO_ROOT / "agents"

# Roles gated del encargo L-1 (el orquestador no es un rol gated de TDD).
ROLE_AGENTS = (
    "architect", "test-writer", "implementer", "reviewer", "scribe",
)

AGENT_FILES = tuple(
    f"cdad-{role}{suffix}.md"
    for role in ROLE_AGENTS
    for suffix in ("", "-odoo")
)

# ---- marcadores estables (case-insensitive, por párrafo) -----------------

# (b) invalidación por auditoría de trabajo fuera de scope
INVALID_RE = re.compile(r"invalid", re.IGNORECASE)
AUDIT_RE = re.compile(r"audit", re.IGNORECASE)
OUT_OF_SCOPE_RE = re.compile(
    r"out of (the )?scope|outside (the )?scope|fuera del (alcance|scope)"
    r"|write[_ -]?scope",
    re.IGNORECASE,
)

# (c) bloqueo legítimo → stop + report, sin reintentos equivalentes ni rodeos
DENIED_RE = re.compile(r"denied|denial|deneg", re.IGNORECASE)
STOP_REPORT_RE = re.compile(r"stop|detiene|detén|report", re.IGNORECASE)
NO_RETRY_NO_BYPASS_RE = re.compile(
    r"retr(y|ies)|reintent|bypass|workaround|circumvent|sortear|rodeo",
    re.IGNORECASE,
)


def paragraphs(text: str) -> list[str]:
    """Párrafos de un agente: bloques separados por líneas en blanco.

    Se usa el texto completo (frontmatter + cuerpo): la regla puede
    inlinearse en el cuerpo o en un comentario de los mapas; el oráculo
    no fija la ubicación, solo la presencia explícita.
    """
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def find_paragraph(text: str, *patterns: re.Pattern[str]) -> bool:
    """True si ALGÚN párrafo contiene TODOS los patrones conjuntamente."""
    for para in paragraphs(text):
        if all(p.search(para) for p in patterns):
            return True
    return False


def load_agent(name: str) -> str:
    path = AGENTS_DIR / name
    if not path.is_file():
        raise AssertionError(
            f"L-1: falta el agente generado {name} en {AGENTS_DIR}; "
            "la regla debe llegar a TODOS los prompts de rol generados"
        )
    return path.read_text(encoding="utf-8")


class TestL1LimitsRuleInGeneratedAgents(unittest.TestCase):
    """L-1: la regla general de límites llega explícita a cada prompt."""

    def test_l1_a_scope_boundary_is_stated(self) -> None:
        """(a) CONTROL (verde hoy): cada agente generado declara su alcance
        de escritura (fila roles-contract, columna "May edit"). Este control
        aísla el RED en la regla faltante (b)/(c), no en la frontera que ya
        existe — el encargo pide no duplicar (a)."""
        for name in AGENT_FILES:
            with self.subTest(agent=name):
                text = load_agent(name)
                self.assertIn(
                    "May edit", text,
                    msg=f"L-1(a): {name} no declara su alcance de escritura "
                        "(fila roles-contract 'May edit' ausente)",
                )

    def test_l1_b_out_of_scope_writes_invalidated_by_audit(self) -> None:
        """(b) RED: escribir fuera del alcance o sortear un límite NO adelanta
        el trabajo — el orquestador lo detecta en la auditoría (git diff
        contra el write_scope) y el resultado se invalida. Cada agente
        generado debe tener un párrafo que lo exprese (marcadores:
        invalid* + audit + fuera-de-scope/write_scope). RED hoy: ningún
        agente inlinea esta idea."""
        for name in AGENT_FILES:
            with self.subTest(agent=name):
                text = load_agent(name)
                self.assertTrue(
                    find_paragraph(text, INVALID_RE, AUDIT_RE,
                                   OUT_OF_SCOPE_RE),
                    msg=f"L-1(b): {name} no inlinea la regla de que escribir "
                        "fuera del alcance o sortear un límite NO adelanta el "
                        "trabajo: el orquestador lo detecta en la auditoría "
                        "(git diff contra el write_scope) y el resultado se "
                        "invalida (decisión del dueño 2026-10-02; auditoría "
                        "del review-fix-008; limits-core no inlineado)",
                )

    def test_l1_c_blocked_legitimate_work_stops_and_reports(self) -> None:
        """(c) RED: si un límite (permiso, denegación, alcance) impide una
        tarea legítima, el rol se detiene y reporta el bloqueo al orquestador
        con evidencia (qué intentó, qué se denegó), sin reintentos
        equivalentes ni rodeos (bash, otra herramienta, otra ruta).
        Marcadores por párrafo: denied/denial/deneg + stop/report +
        retry/reintent/bypass/workaround/circumvent/sortear/rodeo. RED hoy:
        solo architect lleva un bullet PD-15 acotado sin 'stop/report'; los
        demás solo el puntero 'Shared limits core'."""
        for name in AGENT_FILES:
            with self.subTest(agent=name):
                text = load_agent(name)
                self.assertTrue(
                    find_paragraph(text, DENIED_RE, STOP_REPORT_RE,
                                   NO_RETRY_NO_BYPASS_RE),
                    msg=f"L-1(c): {name} no inlinea la regla de que un "
                        "bloqueo de trabajo legítimo (permiso, denegación, "
                        "alcance) exige detenerse y reportar al orquestador "
                        "con evidencia, sin reintentos equivalentes ni "
                        "rodeos (decisión del dueño 2026-10-02; auditoría "
                        "del review-fix-008; limits-core no inlineado)",
                )


if __name__ == "__main__":
    unittest.main()
