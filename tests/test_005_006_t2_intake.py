#!/usr/bin/env python3
"""005-006 T2 RED — intake del orquestador: arranque desde reposo + rutas
instaladas (PD-2, PD-10, PD-14; INV-4, INV-5).

Test de consistencia ESTRUCTURAL de artefactos distribuidos, caja negra
(precedentes: `tests/test_005_006_t1_start_procedure.py`, tarea T1 de esta
feature; `tests/test_005_005_t2_docs_policy.py`). Cada test lee los archivos
AL EJECUTARSE y los evalúa contra postcondiciones derivadas de
`docs/specs/005-006-guided-project-start/spec.md` (§2 PD-n, §3 INV-n) y de la
tarea T2 del plan aprobado (`plan.md` §T2). Los oráculos NO fueron derivados
leyendo los archivos evaluados (la implementación no fue leída en esta sesión
— aislamiento de fase, ADR-011): provienen del contrato aprobado, y nunca
buscan «frases del prompt» ni intentan probar determinísticamente que el
modelo seguirá instrucciones
(`docs/specs/004-003-planning-procedures/efficient-orchestration-requirements.md:107`).

Los archivos evaluados por los tests (no por el test-writer):
- `sources/roles/orchestrator.md` — fuente canónica del intake (PD-2, PD-10,
  PD-14; región según spec: intake `:19-43`, wiring `:80-98`, resume `:86`).
  Las ventanas son DINÁMICAS (ancladas a los tokens declarados por la spec en
  §6: «Prepared execution path», «Legacy path (fallback», «legacy-loads», y a
  las menciones del CLI de continuidad/re-entry), para tolerar corrimientos.
- `agents/cdad-orchestrator.md` y `agents/claude-code/cdad-orchestrator.md` —
  SALIDAS DECLARADAS del generador (Makefile: «DECLARED OUTPUTS … never edit
  them by hand»; plan §R3). Paridad fuente↔generado por la forma más fuerte
  que el repo soporta (recomputar la salida del generador y compararla, como
  `tests/test_cdad_generate.py`), ejecutando el generador en cada corrida.
- `skills/cdad-cycle/references/project-start.md` — procedimiento corto (T1).
- `scripts/cdad-generate.py` — invocado como subprocess (caja negra).

Un test por postcondición / foco de invariante (verificables de la spec):
- PD-2 (a) → la fuente del intake tiene una entrada de arranque desde reposo:
  instrucción breve / sin ejecución preparada / proyecto no reconocido, que
  (i) ordena cargar la metodología primero (`cdad-cycle`) y (ii) señala
  `references/project-start.md`. Hoy la única vía es «Legacy (fallback,
  SECOND)»: un arranque desde reposo sin camino definido.
- PD-2 (b) → contrato del generador: la salida recomputada coincide byte a
  byte con los agentes publicados y el generado refleja la entrada (los
  agentes son salidas declaradas, no se editan a mano).
- PD-10 (puntos T2) → el cableado de continuidad/re-entry del intake
  (spec `:80-98`) invoca el CLI instalado y las rutas del wiring quedan
  corregidas/marcadas como relativas-a-la-instalación (no relativas al
  proyecto consumidor).
- PD-14 → el intake conserva una salida legítima ante bloqueo: diagnóstico de
  qué falta y cómo seguir, reusando los marcadores existentes («approval
  pending», «state incoherent»; por referencia), y sin publicar un paquete
  inválido.
- INV-4 → el arranque nunca ejecuta `resume` sin ejecución activa, nunca
  fabrica autoridad y nunca cambia de versión en silencio (enunciado en el
  intake; corrije la prescripción ambigua `orchestrator.md:86` para la rama
  de arranque).
- INV-5 → se opera con el producto instalado: barrido de TODA la fuente por
  rutas del CLI relativas al proyecto consumidor, sin marcador de
  instalación; reusa la procedencia fijada por 005-005 (referencia). La
  misma regla se extiende, por el hallazgo F1 de la review formal, a la
  región de los Pasos 5-8 del flujo del orquestador en `SKILL.md`
  (≈:277-443; re-entry ≈:278).

Expectativas RED: hoy (pre-implementación de T2) los tests sobre el intake
fallan con AssertionError de comportamiento — la entrada de arranque no
existe, el wiring sigue relativo al proyecto, la salida legítima no está
enunciada. El test de paridad PD-2(b) es el oráculo de regresión del
contrato del generador; su contraste RED se materializa en la proyección de
la entrada en el generado (misma cláusula PD-2).

El modo de fallo esperado es AssertionError / `pytest.fail` de conducta
(documento inconsistente o ausente respecto del contrato aprobado), nunca
ImportError/SyntaxError/NameError/AttributeError/ValueError.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
ORCH_SOURCE = REPO / "sources" / "roles" / "orchestrator.md"
SKILL = REPO / "skills" / "cdad-cycle" / "SKILL.md"
GEN_OC = REPO / "agents" / "cdad-orchestrator.md"
GEN_CC = REPO / "agents" / "claude-code" / "cdad-orchestrator.md"
GENERATOR = REPO / "scripts" / "cdad-generate.py"
PSTART = REPO / "skills" / "cdad-cycle" / "references" / "project-start.md"

RUNTIMES = (
    ("opencode", GEN_OC),
    ("claude-code", GEN_CC),
)

STACK = "odoo"
PROFILE = "optimus"


def _load(path: Path) -> str:
    if not path.is_file():  # documento faltante es estado conductual, no error de oráculo
        pytest.fail(f"documento requerido no existe: {path}")
    return path.read_text(encoding="utf-8")


def _window(text: str, lo: int, hi: int):
    """Líneas [lo, hi] (1-based, índices tolerantes al fin del archivo)."""
    lines = text.splitlines()
    return [(i + 1, lines[i]) for i in range(max(0, lo - 1), min(len(lines), hi))]


def _in_reg(text: str, lo: int, hi: int, pattern: re.Pattern):
    """¿Alguna línea de la ventana [lo, hi] matchea el patrón?"""
    return any(pattern.search(line) for _, line in _window(text, lo, hi))


def _in_reg_all(text: str, lo: int, hi: int, pattern: re.Pattern):
    return [
        (lineno, line.strip())
        for lineno, line in _window(text, lo, hi)
        if pattern.search(line)
    ]


# ---------------------------------------------------------------------------
# Ventanas dinámicas ancladas a los tokens que la propia spec declara
# (§6, verificado: «Prepared execution path» + «Legacy path (fallback,
# SECOND)» en `sources/roles/orchestrator.md:19-43`, idéntico en el agente
# generado; «legacy-loads: cdad-cycle only»; wiring continuidad/re-entry
# `:80-98`). Si un ancla desaparece, la estructura declarada por la spec se
# alteró: fallo de contracto, no error de oráculo.
# ---------------------------------------------------------------------------

A_PREPARED = re.compile(r"(?i)\bPrepared\s+execution\s+path\b")
A_LEGACY = re.compile(r"(?i)\bLegacy\s+path\b")
A_LEGACY_LOADS = re.compile(r"(?i)\blegacy-loads\b")
A_CLI_WIRING = re.compile(r"(?i)cdad_continuity\.py|cdad_result\.py|re-entry\.md")


def _intake_window(text: str):
    """Región del intake de `sources/roles/orchestrator.md` (spec :19-43).

    Anclaje dinámico: (mín - 8, máx + 22) sobre los anclas declarados por la
    spec («Prepared execution path», «Legacy path», «legacy-loads»), que
    absorbe la entrada nueva sin salirse de la región del intake.
    """
    lines = text.splitlines()
    hits = [
        i + 1 for i, line in enumerate(lines)
        if A_PREPARED.search(line) or A_LEGACY.search(line) or A_LEGACY_LOADS.search(line)
    ]
    assert hits, (
        "PD-2: la estructura declarada del intake del orquestador (spec §6 "
        ":19-43: «Prepared execution path» + «Legacy path (fallback, "
        "SECOND)») ya no está localizable en sources/roles/orchestrator.md; "
        "no se puede verificar la entrada de arranque desde reposo"
    )
    return min(hits) - 8, max(hits) + 22


def _wiring_window(text: str):
    """Región del cableado de continuidad/re-entry del intake (spec :80-98).

    Anclaje dinámico a las menciones del CLI/re-entry declaradas por la spec
    (§6: `cdad_continuity.py` en :81-82, `re-entry.md`/`cdad_result.py` en
    :97-98).
    """
    lines = text.splitlines()
    hits = [i + 1 for i, line in enumerate(lines) if A_CLI_WIRING.search(line)]
    assert hits, (
        "PD-10: el cableado de continuidad/re-entry (spec §6 :80-98: "
        "cdad_continuity.py, re-entry.md, cdad_result.py) ya no es "
        "localizable en sources/roles/orchestrator.md — no se puede verificar "
        "la ruta del CLI instalado"
    )
    return min(hits) - 6, max(hits) + 10


# ---------------------------------------------------------------------------
# PD-2 (a) — la fuente del intake tiene una entrada explícita de arranque
# desde reposo, con (i) la metodología cargada PRIMERO y (ii) el puntero a
# `references/project-start.md`. Hoy la única vía es legacy/SECOND: el
# arranque desde reposo con proyecto no reconocido no tiene camino definido.
# ---------------------------------------------------------------------------

REST_CONCEPT = re.compile(
    r"(?i)(?:desde\s+reposo|desde\s+cero|at\s+rest|from\s+rest|no\s+"
    r"prepared|without\s+(?:a\s+)?prepared|sin\s+ejecuci[oó]n|no\s+hay\s+"
    r"ejecuci[oó]n|not\s+prepar\w*|no\s+execution|no\s+active|absent\s+"
    r"execution|unrecognized|not\s+recogniz\w*|no\s+reconocid\w*|"
    r"instrucci[oó]n\s+breve|brief\s+instruction)"
)
ENTRY_POINTER = re.compile(r"perences/project-start\.md|references/project-start\.md|project-start\.md")
METHODOLOGY = re.compile(r"(?i)\b(?:cdad-?cycle|methodolog\w*|metodolog\w*)\b")
FIRST_ORDER = re.compile(
    r"(?i)\b(?:first|primero|first of all|antes que nada|before anything|"
    r"load\s+first|carg\w+\s+primero|first\s+load|primera\s+carga)\b"
)


def _find_boot_entry(text: str, lo: int, hi: int):
    """Primera entrada de arranque desde reposo en la región [lo, hi].

    Una entrada: una línea (± 10 líneas de contexto) que declara el caso
    «resto» y en su vecindad (i) ordena cargar la metodología primero y
    (ii) señala `references/project-start.md`.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        lineno = i + 1
        if not (lo <= lineno <= hi):
            continue
        if not REST_CONCEPT.search(line):
            continue
        neigh = "\n".join(lines[max(0, i - 10): min(len(lines), i + 11)])
        if (
            ENTRY_POINTER.search(neigh)
            and METHODOLOGY.search(neigh)
            and FIRST_ORDER.search(neigh)
        ):
            return lineno, line.strip()
    return None


def test_pd2_intake_has_boot_at_rest_entry():
    text = _load(ORCH_SOURCE)
    lo, hi = _intake_window(text)

    entry = _find_boot_entry(text, lo, hi)
    assert entry is not None, (
        "PD-2 violada: el intake de sources/roles/orchestrator.md no tiene "
        "una entrada explícita de arranque desde reposo (una instrucción "
        "breve, sin ejecución preparada, proyecto no reconocido) que ordene "
        "cargar la metodología (cdad-cycle) PRIMERO y señale "
        "references/project-start.md (spec PD-2, plan §T2); hoy la única vía "
        "para no-ejecución-preparada es «Legacy path (fallback, SECOND)»: "
        "el arranque desde reposo queda sin camino definido y ambiguo"
    )

    # La condición (no/menu) de reposo estaba cubierta por el legacy; la
    # entrada nueva debe estar EN el intake (región), no fuera de él.
    lo2, hi2 = _intake_window(text)
    assert lo2 <= entry[0] <= hi2, (
        "PD-2 violada: la entrada de arranque desde reposo declarada fuera "
        "de la región del intake (spec :19-43) no es la entrada del intake"
    )

    # El procedimiento señalado EXISTE (el intake apunta a una lectura real;
    # el puntero de un camino que no existe es otra forma de no tener camino).
    if not PSTART.is_file():
        pytest.fail(
            "PD-2 violada: el intake señala un procedimiento de arranque que "
            "no existe: skills/cdad-cycle/references/project-start.md "
            "(camino definido apunta a nada)"
        )


# ---------------------------------------------------------------------------
# PD-2 (b) — contrato del generador: los agentes publicados son la salida del
# generador (byte-parity con la salida recomputada) y reflejan la entrada de
# arranque desde reposo (proyección de la fuente). Forma más fuerte que el
# repo soporta, como `test_cdad_generate.py` (subprocess caja negra).
# ---------------------------------------------------------------------------

def test_pd2_generated_outputs_parity_and_boot_entry_projection():
    assert GENERATOR.is_file(), (
        "PD-2 (contrato del generador): scripts/cdad-generate.py es el "
        "generador declarado (Makefile/004-001 T3) y no existe — no se puede "
        "verificar la paridad fuente↔generado requerida por PD-2"
    )
    for path in (GEN_OC, GEN_CC):
        if not path.is_file():
            pytest.fail(f"PD-2: salida declarada del generador no existe: {path}")

    with tempfile.TemporaryDirectory(prefix="cdad-t2-parity-") as tmp:
        for runtime, committed in RUNTIMES:
            out = Path(tmp) / runtime
            result = subprocess.run(
                [sys.executable, str(GENERATOR),
                 "--runtime", runtime,
                 "--stack", STACK,
                 "--profile", PROFILE,
                 "--out", str(out)],
                cwd=str(REPO),
                text=True,
                capture_output=True,
                check=False,
            )
            assert result.returncode == 0, (
                "PD-2 (contrato del generador): la regeneración para "
                f"{runtime} falló (rc={result.returncode}); el contrato "
                "exige que el generado coincida con la fuente y no hay "
                f"salida verificable. stderr: {result.stderr.strip()}"
            )
            produced = out / "agents" / runtime / "cdad-orchestrator.md"
            assert produced.is_file(), (
                "PD-2 (contrato del generador): la regeneración no publicó "
                f"agents/{runtime}/cdad-orchestrator.md"
            )
            assert produced.read_bytes() == committed.read_bytes(), (
                f"PD-2 violada (paridad fuente↔generado): "
                f"{committed.relative_to(REPO)} no coincide byte a byte con "
                "la salida recomputada del generador — el generado está "
                "desincronizado de la fuente canónica (los agentes son "
                "salidas declaradas: editar sources/ y regenerar; plan §R3)"
            )

    # La entrada proyectada: el generado publicado refleja la entrada de
    # arranque desde reposo (misma cláusula PD-2: «el generado refleja la
    # fuente»). Barredura sobre el archivo completo: el texto compuesto del
    # agente inserta la fuente dentro de una plantilla.
    missing = [
        str(path.relative_to(REPO)) for path in (GEN_OC, GEN_CC)
        if _find_boot_entry(path.read_text(encoding="utf-8"), 1, 10_000) is None
    ]
    assert not missing, (
        "PD-2 violada (proyección en el generado): el agente generado no "
        f"refleja la entrada de arranque desde reposo en: {missing} — la "
        "fuente no incorpora la entrada y el generado coincide con ella; "
        "el camino de arranque sigue sin estar definido en el motor (persiste la "
        "ambigüedad legacy-SECOND); hay que editar la fuente y regenerar"
    )


# ---------------------------------------------------------------------------
# PD-10 (puntos T2) — el cableado de continuidad/re-entry del intake (spec
# :80-98) invoca el CLI instalado; las líneas del wiring quedan corregidas o
# marcadas como relativas-a-la-instalación (no relativas al proyecto
# consumidor). El origen de la instalación se reusa de la procedencia que ya
# fijó 005-005 (referencia, sin re-declarar precedencia).
# ---------------------------------------------------------------------------

CLI_SCRIPT_RE = re.compile(
    r"(?i)\b(?:skills/cdad-cycle/)?scripts/?cdad_(?:continuity|result)\.py\b"
)
CLI_DOC_RE = re.compile(
    r"(?i)\b(?:skills/cdad-cycle/references/)?(?:continuity|re-entry)\.md\b"
)
# Review-fix del dueño (hallazgos A1/A2, T6 `tests/test_005_006_t6_owner_
# reviewfix.py`): el marcador `$CDAD_INSTALL_ROOT` era justamente el DEFECTO A
# (variable de INSTALACIÓN, no de runtime) y DEJA de contar como «ruta
# instalada». El único marcador válido es la ruta derivada del DIRECTORIO DE
# LA SKILL CARGADA, expresada explícitamente con `<skill-dir>` (oráculo
# declarado en el T6).
INSTALL_MARKER_RE = re.compile(r"<skill-dir>")


def _unmarked_wiring_lines(text: str, lo: int, hi: int):
    offenders = []
    for lineno, line in _window(text, lo, hi):
        if not (CLI_SCRIPT_RE.search(line) or CLI_DOC_RE.search(line)):
            continue
        if INSTALL_MARKER_RE.search(line):
            continue
        offenders.append((lineno, line.strip()))
    return offenders


def test_pd10_intake_wiring_uses_installed_cli():
    text = _load(ORCH_SOURCE)
    lo, hi = _wiring_window(text)

    # El punto del wiring sigue invocando al CLI/re-entry (si no, no hay
    # nada que corregir ni una ruta instalada verificable).
    wired = _in_reg_all(text, lo, hi, CLI_SCRIPT_RE) + _in_reg_all(
        text, lo, hi, CLI_DOC_RE
    )
    assert wired, (
        "PD-10 violada: el cableado de continuidad/re-entry (spec :80-98) "
        "ya no invoca al CLI ni a las referencias declaradas — no se puede "
        "corregir su ruta ni verificar la ruta instalada"
    )
    offenders = _unmarked_wiring_lines(text, lo, hi)
    assert not offenders, (
        "PD-10 violada: el cableado de continuidad/re-entry del intake usa "
        "rutas relativas al proyecto consumidor sin marcarlas con la ruta "
        "derivada del directorio de la skill cargada (`<skill-dir>/scripts/…`; "
        "hallazgo A1/A2 del review-fix del dueño, T6), reusando la "
        f"procedencia de 005-005; rutas ofensoras: {offenders}; en otro "
        "proyecto esas rutas relativas no existen)"
    )


# ---------------------------------------------------------------------------
# PD-14 — el intake conserva una salida legítima ante bloqueo: ante un
# insumo faltante produce un diagnóstico que nombra qué falta y cómo seguir,
# reusando los marcadores existentes (approval pending / state incoherent;
# referencia, no re-implementación) y sin publicar un paquete inválido.
# ---------------------------------------------------------------------------

NEGATION = re.compile(r"(?i)\b(?:no|not|never|nunca|jam[aá]s|sin\b|do\s+not|don't|must\s+not)\b")
MISSING = re.compile(r"(?i)\b(?:missing|missing|falt\w*|unavailable|absent|pendin\w*)\b")
HOW_TO_CONTINUE = re.compile(
    r"(?i)\b(?:how\s+to\s+(?:cont\w+|proceed|go\s+on)|c[oó]mo\s+seguir|"
    r"c[oó]mo\s+continuar|who\s+decides|qui[eé]n\s+decide|where\s+to\s+"
    r"return|a\s+d[oó]nde\s+volver|qu[eé]\s+falta|what\s+(?:is\s+)?missing)\b"
)
EXISTING_MARKERS = re.compile(r"approval\s+pending|state\s+incoherent")
MARKER_DOCS = re.compile(
    r"(?i)\b(?:project-execution\.md|continuity\.md|cdad_continuity\.py)\b"
)
INVALID_PACKAGE = re.compile(
    r"(?i)\b(?:invalid|inv[aá]lido|malformed|inv[aá]lid\w*)\b[^.\n]{0,80}\b"
    r"(?:package|packet|paquete|paquete)\b|\b(?:package|packet|paquete|"
    r"paquete)\b[^.\n]{0,80}\b(?:invalid|inv[aá]lido)\b"
)


def test_pd14_intake_keeps_legitimate_blocked_exit():
    text = _load(ORCH_SOURCE)
    lo, hi = _intake_window(text)
    region = "\n".join(line for _, line in _window(text, lo, hi))
    lines = region.splitlines()

    # (1) La salida ante bloqueo existe: qué falta + cómo seguir, en la
    # misma zona de la región del intake (región continua de ± 4 líneas).
    blocked_exit = any(
        MISSING.search(lines[i]) and HOW_TO_CONTINUE.search(
            "\n".join(lines[max(0, i - 4): min(len(lines), i + 5)])
        )
        for i in range(len(lines))
    )
    assert blocked_exit, (
        "PD-14 violada: el intake no conserva una salida legítima ante "
        "bloqueo (configuración incompleta R3 / autoridad sin pin): falta "
        "el diagnóstico que nombra qué falta y cómo seguir (región del "
        "intake, spec PD-14)"
    )

    # (2) Marcadores existentes reusados por REFERENCIA (sin re-implementar
    # el enforcement): «approval pending»/«state incoherent» o la referencia
    # a los dueños del comportamiento cerrado.
    assert EXISTING_MARKERS.search(region) or MARKER_DOCS.search(region), (
        "PD-14 violada: la salida ante bloqueo no reusa los marcadores "
        "existentes (approval pending / state incoherent ni referencia "
        "apuntando a los dueños del enforcement cerrado; la spec exige "
        "referencia, no re-implementación)"
    )

    # (3) Sin publicar un paquete inválido: la prohibición está enunciada
    # con una negación explícita sobre el paquete inválido.
    invalid_guard = any(
        INVALID_PACKAGE.search(lines[i]) and NEGATION.search(
            "\n".join(lines[max(0, i - 2): min(len(lines), i + 3)])
        )
        for i in range(len(lines))
    )
    assert invalid_guard, (
        "PD-14 violada: el intake no enuncia la prohibición de publicar/"
        "preparar un paquete inválido ante un insumo faltante (R3 exige "
        "parada cerrada, no un paquete inválido)"
    )


# ---------------------------------------------------------------------------
# INV-4 — el arranque nunca ejecuta resume sin ejecución activa, nunca
# fabrica autoridad y nunca cambia de versión en silencio (enunciado en el
# intake; corrije la prescripción ambigua `orchestrator.md:86` SOLO para la
# rama de arranque).
# ---------------------------------------------------------------------------

RESUME_TOKEN = re.compile(r"\bresume\b")
RESUME_BRANCH = re.compile(
    r"(?i)(?:sin\s+ejecuci[oó]n\s+activa|without\s+(?:an\s+)?(?:active|"
    r"running)\s+execution|no\s+active\s+execution|no\s+resume\b|not\s+"
    r"resume\b|never\s+resume|do\s+not\s+resume\b|nunca\s+resume)"
)
FABRICATION = re.compile(
    r"(?i)\b(?:fabricat\w*|invent\w*|falsif\w*|supplant|sustitu\w*|"
    r"inventar)\w*\b"
)
AUTHORITY_OR_VERSION = re.compile(
    r"(?i)\b(?:authority|autoridad|approval|aprobaci[oó]n|versi[oó]n|version)\b"
)
SILENT_VERSION = re.compile(
    r"(?i)\bsilently\b|\ben\s+silencio\b|\bsilencio\b|\bsilent[ly]?\b"
)
VERSION_WORD = re.compile(r"(?i)\bversi[oó]n\b|\bversion\b")


def test_inv4_intake_never_resume_without_active_no_fabrication_no_silent_version():
    text = _load(ORCH_SOURCE)
    lo, hi = _intake_window(text)
    lines = text.splitlines()

    # (i) La rama de arranque: cualquier mención de resume en el intake debe
    # estar cualificada por la rama «sin ejecución activa → no resume»
    # (corrije la prescripción ambigua :86 en el intake).
    resume_hits = [
        (i + 1, line) for i, line in enumerate(lines)
        if lo <= i + 1 <= hi and RESUME_TOKEN.search(line)
    ]
    assert resume_hits, (
        "INV-4(a): el intake de reposo ya no distingue la reanudación de la "
        "iniciación desde reposo — ninguna mención de resume en la región "
        "del intake para cualificar (spec :86; PD-9 escribe la rama en el "
        "procedimiento, el intake no debe re-prescribirla sin condición)"
    )
    for lineno, line in resume_hits:
        neigh = "\n".join(lines[max(0, lineno - 5): min(len(lines), lineno + 6)])
        assert RESUME_BRANCH.search(neigh), (
            f"INV-4(a) violada: la prescripción de resume {lineno} no está "
            "cualificada por la rama «sin ejecución activa → no resume»; "
            "hoy un arranque desde reposo puede reanudar prescribiendo "
            "resume sin ejecución activa (:86)"
        )

    # (ii) Nunca fabrica autoridad (ni cambia de versión en silencio).
    found = any(
        NEGATION.search(lines[i]) and FABRICATION.search(lines[i]) and AUTHORITY_OR_VERSION.search(
            "\n".join(lines[max(0, i - 2): min(len(lines), i + 3)])
        )
        for i in range(len(lines))
        if lo <= i + 1 <= hi
    )
    assert found, (
        "INV-4(b) violada: el intake no enuncia la prohibición de fabricar "
        "autoridad / de cambiar de versión en silencio"
    )

    # (iii) Cambio de versión en silencio tratado explícitamente (negación
    # junto a «versión»).
    version_rule = any(
        VERSION_WORD.search(lines[i]) and SILENT_VERSION.search(lines[i]) and NEGATION.search(
            "\n".join(lines[max(0, i - 2): min(len(lines), i + 3)])
        )
        for i in range(len(lines))
        if lo <= i + 1 <= hi
    )
    assert version_rule, (
        "INV-4(c) violada: el intake no enuncia la regla de NO cambiar de "
        "versión en silencio (nunca cambia de versión sin decision del "
        "dueño)"
    )


# ---------------------------------------------------------------------------
# INV-5 — se opera con el producto instalado: un barrido de toda la fuente
# del orquestador no encuentra ninguna ruta del CLI (cdad_continuity.py /
# cdad_result.py) relativa al proyecto consumidor sin marcador de
# instalación; reusa la procedencia fijada por 005-005.
#
# Extensión (hallazgo F1, review formal): el barrido cubre también la región
# de los Pasos 5-8 del flujo del orquestador en SKILL.md (≈:277-443, entre el
# punto de cableado :260-261 y la tabla de carga :443-460 que lista el plan;
# re-entry ≈:278 es de la misma familia fricción-2). Regla: 0 ofensores SIN
# marcar.
# ---------------------------------------------------------------------------

def test_inv5_no_project_relative_cli_route_in_source():
    text = _load(ORCH_SOURCE)
    offenders = [
        (lineno, line.strip())
        for lineno, line in enumerate(text.splitlines(), start=1)
        if CLI_SCRIPT_RE.search(line) and not INSTALL_MARKER_RE.search(line)
    ]
    assert not offenders, (
        "INV-5 violada: la fuente del orquestador usa rutas del CLI "
        "relativas al proyecto consumidor sin el marcador `<skill-dir>` "
        "(ruta derivada del directorio de la skill cargada; hallazgo A1/A2 "
        "del review-fix del dueño, T6), reusando la "
        f"procedencia de 005-005); rutas ofensoras (línea: contenido): "
        f"{offenders}"
    )

    # Misma regla sobre la región de los Pasos 5-8 de SKILL.md (≈:277-443):
    # el recorrido guiado atraviesa re-entry (≈:278), y una ruta relativa al
    # proyecto consumidor ahí no existe en un proyecto consumidor.
    skill = _load(SKILL)
    skill_offenders = [
        (lineno, line.strip())
        for lineno, line in _window(skill, 277, 443)
        if CLI_SCRIPT_RE.search(line) and not INSTALL_MARKER_RE.search(line)
    ]
    assert not skill_offenders, (
        "INV-5 violada: SKILL.md (Pasos 5-8 del flujo del orquestador "
        "≈:277-443) usa rutas del CLI relativas al proyecto consumidor sin "
        "el marcador `<skill-dir>` (ruta derivada del directorio de la "
        "skill cargada, reusando la procedencia de 005-005; hallazgo F1, "
        "review formal, y hallazgo A1/A2 del review-fix del dueño, T6): "
        f"{skill_offenders}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
