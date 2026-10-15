#!/usr/bin/env python3
"""005-006 T6 RED — review-fix del dueño sobre la familia de arranque
(hallazgos A, B, C de la review formal del cierre de 005-006).

Test de consistencia ESTRUCTURAL de artefactos distribuidos, caja negra
(precédentes: `tests/test_005_006_t1_start_procedure.py` T1,
`tests/test_005_006_t2_intake.py` T2 y `tests/test_005_005_t2_docs_policy.py`).
Cada test lee los archivos AL EJECUTARSE y los evalúa contra las propiedades
del hallazgo correspondiente. Los oráculos NO fueron derivados leyendo los
archivos evaluados (aislamiento de fase, ADR-011): provienen del informe de
review-fix del dueño (tres hallazgos materiales: tal como está, la aceptación
real R2 fallaría) y del contrato aprobado.

Extensiones sobre la familia T1/T2 (REEMPLAZO o AMPLIACIÓN de la garantía,
nunca borrado): la familia PD-10/INV-5 de T1/T2 aceptaba como ruta del CLI
instalado el marcador `$CDAD_INSTALL_ROOT`; ese marcador es justamente el
defecto A (variable de instalación, no de runtime) y deja de contar.

MARCADOR DECLARADO — ORÁCULO DEL HALLAZGO A2:
`<skill-dir>` es el marcador elegido para la ruta derivada del directorio de
la skill cargada. El runtime informa ese directorio al cargar la skill (en
OpenCode el tool de skills devuelve su base directory), de modo que cada
invocación del CLI en el cableado debe escribirse, p. ej.:

    <skill-dir>/scripts/cdad_packet.py
    <skill-dir>/references/continuity.md

y NUNCA como `$CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/...` (defecto A1)
ni como `scripts/...` relativo al proyecto consumidor (que no existe en otro
proyecto). El docstring arriba es el oráculo: implementar contra él.

Mapeo test ↔ hallazgo (uno por hallazgo):

- A1  → `CDAD_INSTALL_ROOT` NO aparece en los archivos de cableado (el intake
        del orquestador, las skills/cdad-cycle que lo citan, README y los dos
        agentes generados); sí puede aparecer en `install.sh`, que es un
        archivo de instalación y NO es cableado de runtime.
- A2  → cada invocación del CLI en el cableado (`cdad_*.py`) se expresa con
        la ruta derivada `<skill-dir>/scripts/cdad_*.py`, marcada de forma
        explícita.
- B1  → `project-start.md` da la SECUENCIA CONCRETA de comandos del arranque,
        con sus argumentos (abrir la ejecución nueva, `prepare`, las
        validaciones, `begin`, despachar), sin obligar a leer
        `project-execution.md` ni el código del CLI.
- B2  → UNA comprobación única de versión: una sola cosa que correr que diga
        si proyecto/agentes/CLI son la misma versión; NO una comparación
        manual con diffs (la medición real: ~6 de 9,7 min, evidence
        `docs/epics/epic-005-real-operation/evidence/005-006-attempt-2.md`).
- C   → el texto manda conservar las convenciones y el nombrado PROPIOS del
        proyecto, y presenta la convención de CDAD (`<epic-num>-<feat-num>-
        <slug>`) como la de CDAD, a usar SOLO cuando el proyecto no tenga una.
        El texto defectuoso de `project-start.md:42-43` (la convención
        `<epic-num>-<feat-num>-<slug>` presentada como «del proyecto») queda
        proscrito: el proyecto de aceptación usa `E001`/`F001-001`; imponer el
        nomenclado de CDAD
        contradice PD-5/INV-2 (preservar lo existente).

Expectativa RED: HOY los cinco tests fallan por falla conductual explícita
(el cableado sigue citando `$CDAD_INSTALL_ROOT` y sin `<skill-dir>`; la
secuencia de arranque y la comprobación única de versión no existen como
propiedades; el nomenclado de CDAD sigue presentado como convención del
proyecto). El modo de fallo esperado es AssertionError / `pytest.fail` de
conducta, nunca ImportError/SyntaxError/NameError/AttributeError/ValueError.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Archivos de CABLEADO del arranque (hallazgo A): fuentes/agentes/referencias
# que se ejecutan o se leen en runtime. `install.sh` NO está aquí: es el
# archivo de instalación y allí sí vive la variable (hallazgo A, parte 1).
WIRING_FILES = [
    ("sources/roles/orchestrator.md", REPO / "sources" / "roles" / "orchestrator.md"),
    ("skills/cdad-cycle/SKILL.md", REPO / "skills" / "cdad-cycle" / "SKILL.md"),
    (
        "skills/cdad-cycle/references/continuity.md",
        REPO / "skills" / "cdad-cycle" / "references" / "continuity.md",
    ),
    (
        "skills/cdad-cycle/references/project-start.md",
        REPO / "skills" / "cdad-cycle" / "references" / "project-start.md",
    ),
    ("README.md", REPO / "README.md"),
    ("agents/cdad-orchestrator.md", REPO / "agents" / "cdad-orchestrator.md"),
    (
        "agents/claude-code/cdad-orchestrator.md",
        REPO / "agents" / "claude-code" / "cdad-orchestrator.md",
    ),
]

PSTART = REPO / "skills" / "cdad-cycle" / "references" / "project-start.md"


def _load_wiring(label: str, path: Path) -> str:
    if not path.is_file():  # documento faltante es estado conductual, no error de oráculo
        pytest.fail(f"hallazgo A: documento de cableado requerido no existe: {label}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Hallazgo A1 — `CDAD_INSTALL_ROOT` NO aparece en el cableado. Es una variable
# de INSTALACIÓN (install.sh la usa como raíz); no existe en runtime y
# `$CDAD_INSTALL_ROOT/skills/cdad-cycle` resuelve a `~/skills/cdad-cycle`,
# que NO existe (las skills viven en `~/.config/opencode/skills`,
# `~/.agents/skills`, `~/.claude/skills`).
# ---------------------------------------------------------------------------

INSTALL_ROOT_TOKEN = re.compile(r"\bCDAD_INSTALL_ROOT\b")


def test_hallazgo_a1_no_install_root_in_wiring():
    offenders = []
    for label, path in WIRING_FILES:
        text = _load_wiring(label, path)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if INSTALL_ROOT_TOKEN.search(line):
                offenders.append(f"{label}:{lineno}")
    assert not offenders, (
        "HALLAZGO A1 violado: CDAD_INSTALL_ROOT sigue apareciendo en el "
        "cableado (offsets file:línea, " + ", ".join(offenders) + "). Es una "
        "variable de INSTALACIÓN (install.sh), no de runtime: con instalación "
        "global no está definida y `$CDAD_INSTALL_ROOT/skills/cdad-cycle` "
        "resuelve a `~/skills/cdad-cycle`, que NO existe (las skills viven en "
        "`~/.config/opencode/skills`, `~/.agents/skills`, `~/.claude/skills`). "
        "La ruta del CLI instalado debe expresarse como se redefine en el "
        "hallazgo A2 (marcador `<skill-dir>`), no con esta variable."
    )


# ---------------------------------------------------------------------------
# Hallazgo A2 — cada invocación del CLI en el cableado se expresa como una
# ruta DERIVADA DEL DIRECTORIO DE LA SKILL CARGADA, con el marcador explícito
# `<skill-dir>` (oráculo declarado en el docstring del módulo), y NO como un
# `scripts/...` relativo al proyecto consumidor.
# ---------------------------------------------------------------------------

CLI_TOKEN = re.compile(r"\bcdad_[a-z_]+\.py\b")
SKILL_DIR_ROUTE = re.compile(r"<skill-dir>[^\S\n]*/?[^\n]{0,64}?\bcdad_[a-z_]+\.py\b")


def test_hallazgo_a2_cli_invocations_derived_from_skill_dir():
    offenders = []
    for label, path in WIRING_FILES:
        text = _load_wiring(label, path)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not CLI_TOKEN.search(line):
                continue
            if SKILL_DIR_ROUTE.search(line):
                continue
            offenders.append(f"{label}:{lineno}: {line.strip()[:140]}")
    assert not offenders, (
        "HALLAZGO A2 violado: invocaciones del CLI en el cableado sin la ruta "
        "derivada del directorio de la skill cargada (oráculo `<skill-dir>`): "
        + "; ".join(offenders)
        + ". Cada invocación debe escribirse con el marcador explícito "
        "`<skill-dir>/scripts/cdad_*.py` (el runtime informa el directorio de "
        "la skill al cargarla; en OpenCode el tool de skills devuelve su base "
        "directory) y NO como ruta relativa al proyecto consumidor ni como "
        "$CDAD_INSTALL_ROOT (defecto A1)."
    )


# ---------------------------------------------------------------------------
# Hallazgo B1 — el procedimiento da la SECUENCIA CONCRETA de comandos del
# arranque, con sus argumentos (abrir la ejecución nueva, `prepare`, las
# validaciones, `begin`, despachar), sin obligar a leer project-execution.md
# ni el código del CLI. La forma de los comandos proviene de la suite
# (tests/test_005_006_t5_acceptance.py, test_003_006_t3_receive_wiring.py,
# test_004_002_t4_dispatch.py): `cdad_continuity.py begin --project-root …`,
# `cdad_packet.py prepare --project-root …`, `cdad_packet.py validate-*`,
# despachar via `--record-dispatch` / `cdad_result.py receive`.
# ---------------------------------------------------------------------------

B1_OPEN_EXEC = re.compile(
    r"(?i)(?:ejecuci[oó]n\s+nuev\w*|nuev\w*\s+ejecuci[oó]n|new\s+execut\w*|"
    r"abr\w*\s+(?:la\s+|el\s+)?(?:nueva?\s+|primera\s+)?ejecuc\w*|"
    r"open(?:ing)?\s+(?:the\s+)?(?:new\s+)?execution)"
)
B1_BEGIN_CMD = re.compile(
    r"\bcdad_continuity\.py\b[^\n]{0,140}\bbegin\b|\bbegin\b[^\n]{0,80}--project-root"
)
B1_PREPARE_CMD = re.compile(
    r"\bcdad_packet\.py\b[^\n]{0,140}\bprepare\b|\bprepare\b[^\n]{0,80}--project-root"
)
B1_VALIDATE_CMD = re.compile(
    r"\bcdad_packet\.py\b[^\n]{0,140}validate-\w+|validate-\w+\b[^\n]{0,120}--project-root"
)
B1_DISPATCH = re.compile(
    r"(?i)--record-dispatch|\brecord[- ]dispatch\b|\bcdad_result\.py\b[^\n]{0,100}receive"
)

B1_ARG = re.compile(r"--[a-z][a-z0-9\-]+")

B1_HELP_DEDUC = re.compile(r"cdad_[a-z_]+\.py\s+--help")


def _step_with_args(text: str, step: re.Pattern, argv: re.Pattern | None) -> bool:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not step.search(line):
            continue
        if argv is None:
            return True
        window = "\n".join(lines[max(0, i - 1) : i + 2])
        if argv.search(window):
            return True
    return False


def test_hallazgo_b1_concrete_start_command_sequence():
    if not PSTART.is_file():
        pytest.fail(
            "B1: documento requerido no existe: skills/cdad-cycle/references/"
            "project-start.md (la secuencia concreta no puede existir sin él)"
        )
    text = PSTART.read_text(encoding="utf-8")

    steps = [
        ("abrir la ejecución nueva", B1_OPEN_EXEC, None),
        ("begin (cdad_continuity.py begin --project-root …)", B1_BEGIN_CMD, B1_ARG),
        ("prepare (con argumentos)", B1_PREPARE_CMD, B1_ARG),
        ("las validaciones (validate-* --project-root …)", B1_VALIDATE_CMD, B1_ARG),
        ("despachar (--record-dispatch / cdad_result.py receive)", B1_DISPATCH, B1_ARG),
    ]
    missing = [
        name
        for name, step, argv in steps
        if not _step_with_args(text, step, argv)
    ]
    assert not missing, (
        "HALLAZGO B1 violado: project-start.md no da la SECUENCIA CONCRETA de "
        f"comandos del arranque con sus argumentos (faltan: {missing}). El "
        "arranque no debe obligar a leer project-execution.md ni el código del "
        "CLI para deducir la secuencia (evidence 005-006-attempt-2: ~6 de 9,7 "
        "minutos deduciendo): cada paso debe estar spelled out con su forma "
        "exacta de invocación (los pasos begin/prepare/validate/· despachar "
        "con sus flags, p. ej. `--project-root`)."
    )

    # Prohibido deducir la secuencia por --help del CLI (el oráculo de
    # conducta: la receta debe ser concreta, no auto-descubierta).
    assert not B1_HELP_DEDUC.search(text), (
        "HALLAZGO B1 violado: la secuencia de arranque reenvía a deducir los "
        "comandos del CLI (cdad_*.py --help) en lugar de dar la receta concreta"
    )


# ---------------------------------------------------------------------------
# Hallazgo B2 — UNA comprobación única de versión: una sola cosa que correr
# que diga si proyecto/agentes/CLI son la misma versión. No una comparación
# manual (hoy a mano con diffs, evidence attempt-2).
# ---------------------------------------------------------------------------

B2_VERSION_WORD = re.compile(
    r"(?i)\bversi[oó]n(?:es)?\b|\bversion\b|\bversiones\b"
)
B2_TRI_PROJECT = re.compile(r"(?i)\b(?:proyecto|project)\b")
B2_TRI_AGENTS = re.compile(r"(?i)\bagentes?\b|\bagents?\b")
B2_TRI_CLI = re.compile(r"(?i)\bcli\b|cdad_[a-z_]+\.py")
B2_COHERENCE = re.compile(
    r"(?i)(?:misma\s+versi[oó]n|versiones?\s+coincid\w*|coherente?s?\s+de\s+"
    r"versi[oó]n|coherencia\s+de\s+versi[oó]n|same\s+version|version\s+"
    r"coherence|coincide?s?\s+la\s+versi[oó]n|versi[oó]n\s+coincid\w*)"
)
B2_MANUAL = re.compile(
    r"(?i)(?:a\s+mano|manualmente|manually|by\s+hand|con\s+dif ?f|con\s+diff)"
)
B2_COMPARE = re.compile(r"go\b|\bdif ?f\b|compar\w*|cotejar")
B2_NEGATE = re.compile(r"(?i)\b(?:no|nunca|never|jam[aá]s|avoid|evitar|sin|without)\b")


def _window_neigh(text: str, i: int, w: int) -> str:
    lines = text.splitlines()
    return "\n".join(lines[max(0, i - w) : min(len(lines), i + w + 1)])


def test_hallazgo_b2_single_version_check_not_manual_diff():
    if not PSTART.is_file():
        pytest.fail(
            "B2: documento requerido no existe: skills/cdad-cycle/references/"
            "project-start.md (la comprobación única de versión no puede "
            "existir sin él)"
        )
    text = PSTART.read_text(encoding="utf-8")
    lines = text.splitlines()

    # (1) Comprobación designada: hay un punto donde versión + coherencia
    #     proyecto/agentes/CLI (los tres actores, no solo uno) y una forma de
    #     comando concreta (cosa que correr).
    anchors = []
    for i, line in enumerate(lines):
        window = _window_neigh(text, i, 3)
        if B2_VERSION_WORD.search(line) and B2_COHERENCE.search(window):
            window_ok = (
                B2_TRI_PROJECT.search(window)
                and B2_TRI_AGENTS.search(window)
                and B2_TRI_CLI.search(window)
            )
            anchors.append((i, window_ok, line))
    assert anchors and any(ok for _, ok, _ in anchors), (
        "HALLAZGO B2 (1) violado: project-start.md no declara UNA "
        "comprobación de versión que diga si PROYECTO/AGENTES/CLI son la "
        "misma versión (los tres actores juntos); hoy no existe una cosa "
        "única que correr ni una comparación manual codificada"
    )

    # (2) La comprobación designada es UNA sola cosa que correr: en los
    #     anclajes validados hay exactamente UNA forma de comando distinta
    #     (una única interpretación canónica).
    anchored_forms = set()
    for i, ok, _ in anchors:
        if not ok:
            continue
        window = _window_neigh(text, i, 3)
        for span in re.findall(r"`([^`\n]{1,140})`", window):
            if not B2_VERSION_WORD.search(span):
                continue
            if not re.search(r"--|\.py|/", span):
                continue
            anchored_forms.add(re.sub(r"\s+", " ", span).strip())
    assert anchored_forms, (
        "HALLAZGO B2 (2) violado: la comprobación de versión declarada no "
        "viene acompañada de UNA cosa que correr (ningún comando concreto "
        "junto a la coherencia proyecto/agentes/CLI)"
    )
    assert len(anchored_forms) == 1, (
        "HALLAZGO B2 violado: la comprobación de versión NO es única — hay "
        f"{len(anchored_forms)} formas distintas de comprobarla: "
        f"{sorted(anchored_forms)}; debe ser UNA sola cosa que correr que "
        "diga si proyecto/agentes/CLI son la misma versión"
    )

    # (3) No una comparación manual: ninguna instrucción de comparar/diff
    #     "a mano" en contexto de versión, sin negación que la prohíba.
    offenders = []
    for i, line in enumerate(lines):
        window = _window_neigh(text, i, 1)
        if not B2_VERSION_WORD.search(window):
            continue
        if not (B2_COMPARE.search(line) and B2_MANUAL.search(line)):
            continue
        if B2_NEGATE.search(window):
            continue
        offenders.append(f"línea {i + 1}: {line.strip()[:140]}")
    assert not offenders, (
        "HALLAZGO B2 (3) violado: hay instrucciones de comprobación de "
        "versión MANUAL (diffs/comparaciones a mano) sin la prohibición "
        f"explícita: {offenders}; debe ser una sola cosa que correr, no una "
        "comparación hecha a mano"
    )


# ---------------------------------------------------------------------------
# Hallazgo C — el texto manda conservar las convenciones y el nombrado PROPIOS
# del proyecto, y presenta la convención de CDAD como la de CDAD (a usar solo
# cuando el proyecto no tenga una). El texto defectuoso :42-43 (la convención
# `<epic-num>-<feat-num>-<slug>` presentada como «del proyecto») queda
# proscrito: el proyecto de aceptación usa `E001`/`F001-001`.
# ---------------------------------------------------------------------------

C_CDAD_MARKER = re.compile(r"`?<epic-num>-<feat-num>-<slug>`?")
C_CONV_WORD = re.compile(r"(?i)\b(?:convenc\w*|nomenclatur\w*|naming|conventions?)\b")
C_PROJECT_WORD = re.compile(r"(?i)\b(?:proyecto|project)\b")
C_OWN_OR_PRECEDENCE = re.compile(
    r"(?i)\bpropi[oa]s?\b|\bown\b|\bprecedenc\w*|\bprioridad\b|\bpriority\b|"
    r"\bprimero\b|\bfirst\b|\bpreserv\w*|\bconserv\w*|\bintact\w*|"
    r"\bfallback\b|\bdefault\b"
)
C_CDAD_WORD = re.compile(r"(?i)\bcdad\b")
C_FALLBACK = re.compile(
    r"(?i)(?:"
    r"cuando\s+(?:el\s+)?proyecto\s+no\s+tenga|"
    r"proyecto\s+no\s+tenga|"
    r"cuando\s+no\s+tenga|"
    r"s[oó]lo\s+cuando|solo\s+cuando|only\s+when|usar\s+(?:solo|s[oó]lo)|"
    r"use\s+(?:it\s+)?only|"
    r"proyecto\s+no\s+cuenta\s+(?:con\s+)?(?:una?\s+)?(?:convenc|nomenclatur|naming)|"
    r"sin\s+(?:una?\s+)?(?:convenc|nomenclatur|naming)|"
    r"if\s+the\s+project\s+(?:has\s+none|has\s+no\b|doesn'?t\s+have|lacks)|"
    r"project\s+has\s+(?:none|no\s+(?:own\s+)?(?:conventions?|naming))"
    r")"
)


def test_hallazgo_c_project_conventions_first_cdad_labeled():
    if not PSTART.is_file():
        pytest.fail(
            "C: documento requerido no existe: skills/cdad-cycle/references/"
            "project-start.md"
        )
    text = PSTART.read_text(encoding="utf-8")
    lines = text.splitlines()

    # (1) Mandato positivo: conservar las convenciones/nombrado PROPIOS del
    #     proyecto (con término de propiedad/precedencia, no solo «del
    #     proyecto» pegado al patrón CDAD como hoy).
    mandate = [
        (i, line)
        for i, line in enumerate(lines)
        if C_CONV_WORD.search(line)
        and C_PROJECT_WORD.search(line)
        and C_OWN_OR_PRECEDENCE.search(_window_neigh(text, i, 1))
    ]
    assert mandate, (
        "HALLAZGO C violado: project-start.md no manda conservar las "
        "convenciones y el nombrado PROPIOS del proyecto (término de "
        "propiedad/precedencia junto a convenciones/nomenclatura del "
        "proyecto); la garantía PD-5/INV-2 se aplica a lo que YA definió el "
        "proyecto (p. ej. el proyecto de aceptación usa `E001`/`F001-001`), no al patrón de CDAD"
    )

    marker_hits = [
        (i, line) for i, line in enumerate(lines) if C_CDAD_MARKER.search(line)
    ]
    assert marker_hits, (
        "HALLAZGO C violado: la convención de CDAD "
        "(``<epic-num>-<feat-num>-<slug>``) ni siquiera aparece etiquetada "
        "como LA CONVENCIÓN DE CDAD en project-start.md (pierde el punto de "
        "referencia para el caso sin convenciones propias)"
    )

    # (2) La convención de CDAD presentada como LA DE CDAD con el fallback
    #     explícito (a usar solo cuando el proyecto no tenga una).
    fallback_near = []
    for i, _ in marker_hits:
        window = _window_neigh(text, i, 2)
        has_cdad_label = C_CDAD_WORD.search(window) and C_CONV_WORD.search(window)
        if not has_cdad_label:
            continue
        if C_FALLBACK.search(_window_neigh(text, i, 4)):
            fallback_near.append(i)
    assert fallback_near, (
        "HALLAZGO C violado: la convención de CDAD "
        "(``<epic-num>-<feat-num>-<slug>``) no está presentada como LA DE "
        "CDAD con el fallback explícito «a usar solo cuando el proyecto no "
        "tenga una» (etiqueta CDAD + palabra de convención + frase de "
        "fallback cerca del marcador); hoy el texto la presenta como "
        "«convención del proyecto», lo que contradice su intención"
    )

    # (3) Prohibición: el marcador de CDAD NO puede seguir presentado como
    #     convención «del proyecto» (el defecto original de :42-43).
    defect = [
        f"línea {i + 1}: {line.strip()[:140]}"
        for i, line in enumerate(lines)
        if C_CDAD_MARKER.search(line)
        and re.search(
            r"(?i)del\s+proyecto|of\s+the\s+project", _window_neigh(text, i, 1)
        )
        and C_CONV_WORD.search(_window_neigh(text, i, 1))
    ]
    assert not defect, (
        "HALLAZGO C violado: la convención ``<epic-num>-<feat-num>-<slug>`` "
        "sigue presentada como convención DEL PROYECTO (defecto :42-43): "
        + "; ".join(defect)
        + ". Debe presentarse como LA CONVENCIÓN DE CDAD (a usar solo cuando "
        "el proyecto no tenga una), dejando a cada proyecto sus propias "
        "convenciones (proyecto de aceptación: `E001`/`F001-001`)."
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
