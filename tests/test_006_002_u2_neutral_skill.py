#!/usr/bin/env python3
"""006-002 U2 RED — §4 neutral de cdad-cycle y skill sin herramientas de runtime.

Contract:
- ``docs/specs/006-002-delegation-by-layer/spec.md`` §2 PD-1 (skill layer free
  of runtime tools and concrete models; oráculo de ausencia al inicio de §2),
  §2 PD-3 (§4 conserva el núcleo neutral de siete puntos, sin nombrar runtimes),
  §3 INV-1/INV-2.
- ``docs/specs/006-002-delegation-by-layer/plan.md`` ficha U2 (archivos y gate
  PD-1/PD-3) + enmienda A-1 (los asserts acoplados de esta superficie se
  reformulan en ESTE RED, nunca en el GREEN).

Oráculo de ausencia (spec §2, cabecera): el patrón de
``tests/test_005_010_t3_references.py`` (``CONCRETE_MODEL_ID_RE``,
``SPACED_MODEL_LINE_RE``, ``PROVIDER_RE`` — importados, una sola definición)
extendido con **formas de herramienta** de despacho: code-span ``task`` /
``delegate`` / ``Agent``, el token ``subagent_type``, ``opencode run``,
``sessions_spawn``, «Agent tool». NUNCA la palabra suelta *task* (prosa como
"atomic task": discovery §4 risk 6).

Exclusiones declaradas de esta unidad (cada una con su dueño):
- ``references/context-meter.md`` — contrato de LECTOR/MEDICIÓN (INV-8): declara
  ``task``/``subagent`` como nombres de herramienta *reconocidos* (dato de
  medición, no instrucción de delegación).
- **sección §2 de ``SKILL.md``** (columna "Model family" + párrafo de perfiles,
  ``:67-77``) — superficie de **PD-11** (plan U4): el oráculo de MODELOS la
  neutraliza (misma numeración de líneas) y su ausencia la fija el RED de esa
  unidad (enmienda A-1: cada RED cubre su superficie).

Ya NO hay exclusiones temporales: el RED de **U3** (``test_006_002_u3_…``, PD-9/
PD-10) retiró las dos referencias por runtime del árbol instalable y la regla de
elección de transporte de ``cli-delegation.md``, así que este oráculo corre
sobre el árbol completo (``skills/cdad-cycle/**`` y ``skills/cdad-epic/**``)
salvo las dos exclusiones con dueño de arriba — el contrato PD-1 no distingue
por unidad: ningún texto instalable de la skill nombra una herramienta de
despacho de un runtime.

Mapa test → postcondición (un test por afirmación observable):
  1 ``TestPd1SkillWithoutRuntimeTools::test_pd1_no_dispatch_tool_form_in_installable_skill_text``   PD-1 / INV-1
  2 ``TestPd1SkillWithoutRuntimeTools::test_pd1_no_concrete_model_in_delegation_context``           PD-1 / INV-2
  3 ``TestPd3Section4NeutralCore::test_pd3_section4_keeps_the_seven_points_in_abstract_form``       PD-3
  4 ``TestPd3Section4NeutralCore::test_pd3_section4_names_no_runtime_tool_form``                    PD-3 / INV-1

RED esperado (árbol actual: U2 ya en GREEN; el RED de U3 retiró las exclusiones
temporales de la superficie de PD-9/PD-10):
- (1) FALLA por AssertionError de CONTENIDO: las formas de herramienta que aún
  quedan en el texto instalable son las de las DOS referencias por runtime que
  PD-9 retira (``references/opencode-delegation.md``: ``task``/``delegate``/
  ``subagent_type``; ``references/claude-code-delegation.md``: ``Agent``/
  ``Agent tool``/``subagent_type``) y la regla de elección de transporte de
  ``cli-delegation.md`` (``task``): exactamente la superficie de U3, cuyo RED
  (``tests/test_006_002_u3_runtime_references.py``) las baja del árbol con los
  punteros reconciliados.
- (2) pasa hoy: **GUARD pre-satisfecho** (el árbol no fija modelos fuera de §2 —
  superficie de PD-11); protege el GREEN contra un intercambio de nombres de
  modelo en la superficie de delegación.
- (3)/(4): PASAN hoy (U2 GREEN); son los controles de conservación de §4.
Ningún fallo es ImportError/SyntaxError.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Reuso declarado (spec §2): los patrones de modelo/proveedor ya fijados por
# 005-010 T3 — una sola definición, sin copiarlos.
from tests.test_005_010_t3_references import (
    CONCRETE_MODEL_ID_RE,
    PROVIDER_RE,
    SPACED_MODEL_LINE_RE,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

SKILL_ROOTS = (
    REPO_ROOT / "skills" / "cdad-cycle",
    REPO_ROOT / "skills" / "cdad-epic",
)
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"

# --------------------------------------------------------------------------
# Exclusiones de esta unidad — cada una declara su dueño (spec §2 PD-1/PD-9,
# PD-10; INV-8).
# --------------------------------------------------------------------------

# INV-8 / PD-1: contrato de LECTOR (medición): reconoce `task`/`subagent` como
# nombres de herramienta observados, no instruye delegación.
READER_CONTRACT_EXCLUSIONS = (
    "skills/cdad-cycle/references/context-meter.md",
)
# Única exclusión vigente del oráculo de FORMAS DE HERRAMIENTA. Las exclusiones
# TEMPORALES de U3 (PD-9: las dos referencias por runtime; PD-10: la regla de
# elección de transporte de cli-delegation.md) se retiraron en el RED de U3
# (tests/test_006_002_u3_runtime_references.py): hoy el oráculo corre sobre el
# árbol instalable completo.
TOOL_FORM_EXCLUSIONS = READER_CONTRACT_EXCLUSIONS

# --------------------------------------------------------------------------
# Oráculo de ausencia — FORMAS DE HERRAMIENTA de despacho (spec §2, cabecera)
# --------------------------------------------------------------------------

TOOL_FORM_PATTERNS = (
    (re.compile(r"`\s*task\s*`"),
     "code-span `task` (forma de herramienta de despacho)"),
    (re.compile(r"`\s*delegate\s*`"),
     "code-span `delegate` (forma de herramienta de despacho)"),
    (re.compile(r"`\s*Agent\s*`"),
     "code-span `Agent` (forma de herramienta de despacho)"),
    (re.compile(r"(?i)\bsubagent_type\b"),
     "token `subagent_type` (parámetro de herramienta de despacho)"),
    (re.compile(r"(?i)\bopencode\s+run\b"),
     "invocación CLI `opencode run` (mecanismo de un runtime)"),
    (re.compile(r"(?i)\bsessions_spawn\b"),
     "token `sessions_spawn` (herramienta de un runtime)"),
    (re.compile(r"(?i)\bAgent\s+tool\b"),
     "«Agent tool» (herramienta de despacho de un runtime)"),
)

# --------------------------------------------------------------------------
# Oráculo de ausencia — MODELOS concretos (INV-2)
# --------------------------------------------------------------------------

# `claude-code` / `claude-code-*` son el nombre del RUNTIME (producto), no un
# modelo: ``CONCRETE_MODEL_ID_RE`` (familia + guion) los captura por prefijo
# `claude-`, así que el nombre del runtime se excluye explícitamente del
# oráculo de modelos.
RUNTIME_NAME_RE = re.compile(r"(?i)^claude-code[\w.\-]*$")


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+\S")


def numbered_section_region(text: str, number: int) -> tuple[str, int, int] | None:
    """Región de la sección numerada `number` (el contrato la llama «§N»): del
    encabezado numerado N hasta el siguiente encabezado de nivel igual o
    superior. Devuelve (texto, primera línea, última línea) 1-based, o None si
    la sección no se puede delimitar. No captura subsecciones («4.1»)."""
    lines = text.splitlines()
    heading_re = re.compile(
        rf"^#{{1,6}}[ \t]*(?:§[ \t]*)?{number}(?!\d)(?!\.\d)[.)\s:—–-]?"
    )
    headings = [
        (index, len(match.group(1)))
        for index, line in enumerate(lines)
        if (match := HEADING_RE.match(line))
    ]
    for index, level in headings:
        if not heading_re.match(lines[index]):
            continue
        end = len(lines)
        for other, other_level in headings:
            if other > index and other_level <= level:
                end = other
                break
        return "\n".join(lines[index:end]), index + 1, end
    return None


def model_scan_text(path: Path, text: str) -> str:
    """Texto sobre el que corre el oráculo de MODELOS (PD-1/INV-2).

    Exclusión declarada: la sección §2 de ``SKILL.md`` (columna "Model family" y
    párrafo de perfiles con modelos concretos) es la superficie de **PD-11**
    (plan U4) — su ausencia la fija el RED de esa unidad. Aquí se neutraliza esa
    región (misma numeración de líneas) para que este oráculo mida el contexto
    de delegación y no la deuda de otra unidad (enmienda A-1: cada RED cubre su
    superficie)."""
    if path != SKILL_MD:
        return text
    region = numbered_section_region(text, 2)
    assert region is not None, (
        "drift del oráculo PD-1 (modelos): SKILL.md no expone una sección §2 "
        "delimitable por su encabezado numerado (superficie de PD-11)"
    )
    _, first, last = region
    lines = text.splitlines()
    lines[first - 1:last] = [""] * (last - first + 1)
    return "\n".join(lines)


def model_offences(text: str) -> list[str]:
    """Modelos/proveedores concretos presentes en `text` (INV-2), sin los
    nombres de runtime (`claude-code`)."""
    found: list[str] = []
    for pattern, label in (
        (CONCRETE_MODEL_ID_RE, "identificador de modelo concreto"),
        (SPACED_MODEL_LINE_RE, "nombre de modelo concreto espaciado"),
        (PROVIDER_RE, "nombre de proveedor concreto"),
    ):
        for match in pattern.finditer(text):
            token = match.group(0)
            if label == "identificador de modelo concreto" and RUNTIME_NAME_RE.match(token):
                continue
            found.append(f"{label}: {token!r}")
    return found


# --------------------------------------------------------------------------
# Recolección del texto instalable
# --------------------------------------------------------------------------


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def installable_text_documents() -> list[Path]:
    """Texto instalable de la SKILL: los documentos `.md` de
    ``skills/cdad-cycle/**`` y ``skills/cdad-epic/**`` (la prosa donde vive la
    regla de delegación; los ayudantes ejecutables y assets no son texto de
    delegación y quedan fuera del oráculo)."""
    documents: list[Path] = []
    for root in SKILL_ROOTS:
        documents.extend(sorted(path for path in root.rglob("*.md") if path.is_file()))
    return documents


def scanned_documents(exclusions: tuple[str, ...]) -> list[Path]:
    excluded = set(exclusions)
    return [path for path in installable_text_documents() if relative(path) not in excluded]


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def read(path: Path) -> str:
    assert path.is_file(), (
        "PD-1: el oráculo de ausencia apunta a un documento instalable "
        f"inexistente (drift de la superficie declarada): {relative(path)}"
    )
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# PD-1 / INV-1 — la skill no nombra herramientas de despacho de un runtime
# --------------------------------------------------------------------------


class TestPd1SkillWithoutRuntimeTools(unittest.TestCase):
    """PD-1: ningún texto instalable de ``skills/cdad-cycle/**`` y
    ``skills/cdad-epic/**`` nombra una herramienta de despacho de un runtime ni
    un modelo concreto en un contexto de delegación."""

    def test_pd1_no_dispatch_tool_form_in_installable_skill_text(self) -> None:
        """PD-1/INV-1: ausencia de FORMAS DE HERRAMIENTA de despacho en el texto
        instalable de la skill (code-span `task`/`delegate`/`Agent`,
        `subagent_type`, `opencode run`, `sessions_spawn`, «Agent tool»); la
        palabra suelta *task* NO cuenta."""
        documents = scanned_documents(TOOL_FORM_EXCLUSIONS)
        self.assertGreater(
            len(documents), 0,
            "drift del oráculo PD-1: no se recolectó ningún documento instalable "
            f"bajo {[relative(root) for root in SKILL_ROOTS]}"
        )
        self.assertIn(
            SKILL_MD, documents,
            "drift del oráculo PD-1: skills/cdad-cycle/SKILL.md no está en la "
            "superficie escaneada"
        )

        offenders: list[str] = []
        for path in documents:
            text = read(path)
            for pattern, label in TOOL_FORM_PATTERNS:
                for match in pattern.finditer(text):
                    offenders.append(
                        f"{relative(path)}:{line_of(text, match.start())} — {label}"
                    )

        self.assertEqual(
            offenders, [],
            msg=(
                "PD-1/INV-1: el texto instalable de la skill nombra formas de "
                "herramienta de despacho de un runtime (el mecanismo pertenece al "
                "orquestador de cada runtime, no a la skill): "
                f"{offenders[:20]!r}"
            ),
        )

    def test_pd1_no_concrete_model_in_delegation_context(self) -> None:
        """PD-1/INV-2: ausencia de modelos concretos y de proveedores en el texto
        instalable de la skill (la familia de cada rol es la configurada en el
        runtime; la skill no nombra ninguna)."""
        documents = scanned_documents(TOOL_FORM_EXCLUSIONS)
        self.assertGreater(len(documents), 0, "drift del oráculo PD-1 (modelos)")

        offenders: list[str] = []
        for path in documents:
            text = model_scan_text(path, read(path))
            for offence in model_offences(text):
                offenders.append(f"{relative(path)} — {offence}")

        self.assertEqual(
            offenders, [],
            msg=(
                "PD-1/INV-2: el texto instalable de la skill fija modelos "
                "concretos o proveedores en el contexto de delegación (el modelo "
                "de cada rol es el configurado en el runtime): "
                f"{offenders[:20]!r}"
            ),
        )


# --------------------------------------------------------------------------
# PD-3 — §4 conserva el núcleo neutral de siete puntos, sin nombrar runtimes
# --------------------------------------------------------------------------


def section4_region(text: str) -> tuple[str, int, int] | None:
    """Región de §4 (spec PD-3: ``SKILL.md`` §4)."""
    return numbered_section_region(text, 4)


def require_any(text: str, alternatives: tuple[str, ...], concept: str) -> str | None:
    """Concepto exigido con alternativas de idioma (patrón `require_any` de
    005-010 T3): devuelve None si el concepto está, o el detalle de su falta."""
    lowered = text.lower()
    if any(alternative.lower() in lowered for alternative in alternatives):
        return None
    return f"concepto ausente '{concept}' (alternativas buscadas {list(alternatives)!r})"


# Los SIETE puntos de §4 (spec §2 PD-3, en su orden) con alternativas de idioma.
SECTION4_CONCEPTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("1. principio de la delegación", ("principle", "principio")),
    ("2a. orden — mecanismo nativo", ("native", "nativo")),
    ("2b. orden — handoff", ("handoff",)),
    ("2c. orden — inline", ("inline",)),
    ("3. regla de adaptadores: dueño del ciclo de vida de la sesión",
     ("session lifecycle", "session's lifecycle", "lifecycle of the session",
      "ciclo de vida de la sesión", "ciclo de vida de la sesion")),
    ("4. invariantes de rol", ("invariant", "invariante")),
    ("5. spawn guard", ("spawn guard", "spawn")),
    ("6. recibo", ("receipt", "recibo")),
    ("7a. paquete / re-entry", ("re-entry", "reentry", "reentrada", "reingreso",
                                "packet", "paquete")),
    ("7b. independiente del transporte", ("transport", "transporte")),
)


class TestPd3Section4NeutralCore(unittest.TestCase):
    """PD-3: ``SKILL.md`` §4 conserva, en forma abstracta, los siete puntos —
    principio; orden nativo → handoff → inline; regla de adaptadores por dueño
    del ciclo de vida de la sesión; invariantes de rol; spawn guard; recibo;
    paquete y re-entry independientes del transporte — sin nombrar runtimes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(SKILL_MD)
        region = section4_region(cls.text)
        assert region is not None, (
            "drift del oráculo PD-3: SKILL.md no expone una sección §4 "
            "delimitable por su encabezado numerado"
        )
        cls.section, cls.first_line, cls.last_line = region

    def test_pd3_section4_keeps_the_seven_points_in_abstract_form(self) -> None:
        """PD-3: los siete puntos están presentes en §4 en forma abstracta
        (concepto con alternativas de idioma; la redacción es libre)."""
        missing = [
            detail
            for concept, alternatives in SECTION4_CONCEPTS
            if (detail := require_any(self.section, alternatives, concept))
        ]
        self.assertEqual(
            missing, [],
            msg=(
                "PD-3: §4 de SKILL.md no conserva el núcleo neutral completo "
                f"(líneas {self.first_line}-{self.last_line}). Ausentes: {missing}"
            ),
        )

    def test_pd3_section4_names_no_runtime_tool_form(self) -> None:
        """PD-3/INV-1: §4 (el núcleo neutral) no nombra ninguna forma de
        herramienta de despacho de un runtime — el mecanismo concreto vive en el
        orquestador de cada runtime."""
        offenders: list[str] = []
        for pattern, label in TOOL_FORM_PATTERNS:
            for match in pattern.finditer(self.section):
                offenders.append(
                    f"{relative(SKILL_MD)}:{self.first_line - 1 + line_of(self.section, match.start())}"
                    f" — {label}"
                )
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-3/INV-1: §4 de SKILL.md nombra formas de herramienta de "
                "despacho de un runtime (debe ser abstracto: el mecanismo vive en "
                f"el orquestador generado): {offenders[:20]!r}"
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
