#!/usr/bin/env python3
"""003-006 T1 RED — cableado del descubrimiento en SKILL.md (P1 mitad SKILL, P10).

Contract:
- docs/specs/003-006-runtime-adoption/spec.md (§2.1 cableado del ciclo; P1
  mitad `SKILL.md`: "enlaza `references/continuity.md` en su tabla de
  referencias" + comandos en su paso, "sin duplicar las interfaces";
  P10: `classify` declarado fuera, `trigger` señal advisory).
- docs/specs/003-006-runtime-adoption/plan.md (T1; test focal declarado
  `tests/test_003_006_t1_wiring.py`; validación: "el test afirma que
  `continuity.md` está enlazada y que cada comando aparece en el paso
  correcto; `classify` declarado fuera").

Superficie observable bajo prueba: SOLO `skills/cdad-cycle/SKILL.md`
(su contenido es el "código" de T1 — documentación observable, no
plumbing). El cuerpo del orquestador y agentes regenerados quedan
EXCLUIDOS (T3) y NO se tocan aquí.

Pasos del ciclo (spec §2.1) asociados a cada comando:

    begin       → antes de despachar un paquete (Step 4, write-ahead)
    checkpoint  → al cerrar el límite de tarea/subfase
    receive     → re-entry / materialización de rol (Step 6)
    reconcile   → antes de todo retry o resume
    resume      → al iniciar una sesión nueva (Step 1)
    trigger     → señal advisory antes de rotar
    classify    → declarado FUERA (sin lector de sesiones)

Aserciones robustas a redacción (por sección/paso/keyword, no frases
exactas; acepciones ES+EN). RED honesto: si una aserción pasa hoy se
declara GUARD (pre-satisfecha) con su razón; no se fabrica una falla.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"

# ---------------------------------------------------------------- helpers

HEADING_RE = re.compile(r"^#{1,6}\s")


def skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def section_between_headings(text: str, needle: str) -> str | None:
    """Texto del encabezado que contiene `needle` hasta el siguiente
    encabezado Markdown (spans flexibles: 'How to read the references'
    puede ser '##' o '###')."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if HEADING_RE.match(line) and needle.lower() in line.lower():
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if HEADING_RE.match(lines[j]):
            end = j
            break
    return "\n".join(lines[start:end])


def lines_with(text: str) -> list[str]:
    """Líneas no vacías, sin el prefijo '#' de encabezado (redacción-tolerante:
    un paso puede nombrarse en un heading o en una tabla)."""
    out = []
    for raw in text.splitlines():
        if raw.startswith("#"):
            raw = raw.lstrip("#").strip()
        if not raw:
            continue
        out.append(raw)
    return out


def associated_mentions(text: str, command: str, step_keywords: list[str]) -> list[str]:
    """Líneas (heading-tolerante) que NOMBRAN `command` y contienen una marca
    de su paso del ciclo (misma línea: el patrón '- `cmd` — paso ...' del
    contrato)."""
    pat = re.compile(rf"\b{re.escape(command)}\b", re.IGNORECASE)
    hits = []
    for kw in step_keywords:
        kpat = re.compile(re.escape(kw), re.IGNORECASE)
        for line in lines_with(text):
            if pat.search(line) and kpat.search(line):
                hits.append(line)
    return hits


# ---------------------------------------------------------------- tests


class T1SkillWiring(unittest.TestCase):
    """P1 (mitad SKILL) + P10 — observables de `skills/cdad-cycle/SKILL.md`."""

    @classmethod
    def setUpClass(cls):
        cls.text = skill_text()

    # (a) P1 mitad SKILL — tabla de referencias enlaza continuity.md

    def test_p1_references_table_links_continuity_md(self):
        """P1: la tabla 'How to read the references' enlaza
        references/continuity.md."""
        section = section_between_headings(self.text, "How to read")
        self.assertIsNotNone(
            section,
            "RED esperado: SKILL.md no tiene (aún) la sección de la tabla "
            "de referencias 'How to read the references' ⇒ el cableado no "
            "existe",
        )
        self.assertIn(
            "continuity.md",
            section,
            "RED esperado: la tabla de referencias de SKILL.md no enlaza "
            "references/continuity.md (los contratos de continuidad viven "
            "ahí y no hay puntero) ⇒ AssertionError por comportamiento "
            "ausente",
        )

    # (b) P1 mitad SKILL — cada comando en su paso del ciclo (§2.1)

    def test_p1_resume_named_at_step1(self):
        """P1: `resume` — iniciar una sesión nueva (Step 1)."""
        self._assert_named_in_step(
            "resume",
            ["step 1", "iniciar", "inician", "inicio", "sesión nueva", "new session",
             "session start", "comienza"],
            "essere",
        )

    def test_p1_begin_named_at_step4_dispatch(self):
        """P1: `begin` — antes de despachar un paquete (Step 4)."""
        self._assert_named_in_step(
            "begin",
            ["step 4", "despach", "dispatch", "paquete", "packet", "write-ahead", "antes de"],
            "essere",
        )

    def test_p1_checkpoint_named_at_task_boundary(self):
        """P1: `checkpoint` — al cerrar el límite de tarea/subfase."""
        self._assert_named_in_step(
            "checkpoint",
            ["cierre", "cerrar", "close", "límite", "limit", "tarea", "task", "subfase", "subphase"],
            "essere",
        )

    def test_p1_receive_named_at_reentry(self):
        """P1: `receive` — re-entry / materialización de rol (Step 6)."""
        self._assert_named_in_step(
            "receive",
            ["step 6", "re-entry", "reentrada", "materializ", "rol", "role"],
            "essere",
        )

    def test_p1_reconcile_named_before_retry_resume(self):
        """P1: `reconcile` — antes de todo retry o resume."""
        self._assert_named_in_step(
            "reconcile",
            ["retry", "reintento", "rehacer", "resume", "rotar", "rotate"],
            "essere",
        )

    def test_p1_trigger_named_advisory(self):
        """P1/P10: `trigger` — señal advisory (antes de rotar)."""
        self._assert_named_in_step(
            "trigger",
            ["advisor", "advisory", "avis", "rotar", "rotate", "rotación", "señal", "signal", "unknown"],
            "essere",
        )

    def _assert_named_in_step(self, command: str, step_keywords: list[str], _unused: str):
        hits = associated_mentions(self.text, command, step_keywords)
        self.assertTrue(
            hits,
            f"RED esperado para `{command}`: SKILL.md no lo nombra asociado a "
            f"SU PASO del ciclo (keywords {step_keywords} en la misma línea "
            f"que el comando; §2.1) ⇒ AssertionError por comportamiento "
            f"ausente. Menciones crudas: "
            f"{[ln.strip()[:80] for ln in self.text.splitlines() if re.search(rf'(?i)\\b{command}\\b', ln)]}",
        )

    # (c) P1 + P10 — classify declarado FUERA (sin lector)

    def test_p10_classify_declared_out_of_scope(self):
        """P1/P10: `cdad_guard classify` declarado fuera por falta de lector."""
        candidates = lines_with(self.text)
        out_lines = [
            ln
            for ln in candidates
            if re.search(r"\bclassify\b", ln, re.I)
            and re.search(r"fuera|out of scope|out-of-scope|sin lector|without reader|no reader", ln, re.I)
        ]
        self.assertTrue(
            out_lines,
            "RED esperado para `classify`: SKILL.md no lo declara FUERA de "
            "alcance (sin lector de sesiones; §2.1 — 'classify declarado "
            "fuera') ⇒ AssertionError por comportamiento ausente. "
            f"Menciones crudas: {[ln.strip()[:80] for ln in candidates if re.search(r'(?i)\\bclassify\\b', ln)]}",
        )

    # (d) P1 — SKILL.md SIN duplicar interfaces (contratos viven en las
    #     references; el cuerpo limita a referenciarlas)

    NO_DUP_FLAGS = [
        "--execution-context",   # firma del CLI de continuidad §3 V6
        "--record-dispatch",     # flag de cdad_packet (prepare, I8)
        "--adopted-root",        # firma del generador de activación §2.2
        "--project-root",        # flag transversal de los CLIs
        "--dry-run",             # flag del generador de activación §2.2
    ]

    def test_p1_no_duplicated_interface_tables(self):
        """P1: SKILL.md no copia tablas/bloques de flags ys argumentos de los
        CLIs (la interfaz vive en references/continuity.md,
        references/progress-guards.md y las specs 002/003/004)."""
        table_rows = [ln for ln in self.text.splitlines() if ln.lstrip().startswith("|")]
        offenders = [ln for ln in table_rows for f in self.NO_DUP_FLAGS if f in ln]
        self.assertEqual(
            offenders,
            [],
            "RED esperado: SKILL.md duplica la interfaz de los CLIs "
            "(filas de tabla con flags del generador/CLIs CDAD en vez de "
            "limitarse a referenciar los contratos; §2.1) ⇒ AssertionError "
            "por comportamiento presente que no debería estar. "
            f"Filas ofensoras: {[o.strip()[:120] for o in offenders]}",
        )


if __name__ == "__main__":
    unittest.main()
