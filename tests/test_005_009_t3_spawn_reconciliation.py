#!/usr/bin/env python3
"""005-009 T3 RED — reconciliación de la prohibición de spawn (PD-9; INV-1/4/8).

Contract:
- docs/specs/005-009-cli-delegation/spec.md §2 PD-9, §3 INV-1/INV-4/INV-8,
  §7 D8, §6 (ubicaciones verificadas archivo:línea).
- docs/specs/005-009-cli-delegation/plan.md T3 (archivos, estructura del
  cambio y test focal declarado `tests/test_005_009_t3_spawn_reconciliation.py`).

Estilo (precedentes 005-005 T2 / 005-006 T1 / test_cdad_generate.py):
tests de CONSISTENCIA ESTRUCTURAL, caja negra. Cada test LEE los archivos
de producto AL EJECUTARSE y los evalúa contra marcas estructurales de la
PD — no frases del prompt ni nombres de funciones internas. Los oráculos
NO se derivaron leyendo esos archivos: provienen del contrato aprobado
(PD-9/explicit discovery §7) y del plan T3, que declara exactamente QUÉ
cambios debe resolver el GREEN:

- conservar el SPAWN GUARD / anti-recursión en
  `skills/cdad-cycle/SKILL.md` (:136-143), `sources/roles/orchestrator.md`
  (:74-76) y los generados (plan: "regenerados — salidas declaradas, nunca
  editadas a mano"); la cuarta superficie de esa lista,
  `references/claude-code-delegation.md`, fue RETIRADA del árbol instalable por
  006-002 U3 (PD-9): su detalle se preserva como evidencia no instalable bajo
  `docs/**` y la prohibición sigue viva en la capa del runtime (skill abstracta
  + orquestador generado);
- agregar la DISTINCIÓN: la delegación externa autorizada
  (coordinador→worker ENTRE CLIs) no es recursión de subagentes dentro
  del mismo runtime; una delegación no amplía autoridad ni permite al
  worker escribir el state (PD-9/INV-4/D8);
- el orquestador es el ÚNICO escritor de `docs/.cdad-state.json`
  (INV-1/PD-9), declarado en la fuente canónica y proyectado en los
  generados;
- límites honestos en el texto nuevo (INV-8): nada promete
  aislamiento/sandbox sin negación. Marcadores ESTRUCTURALES (sección,
  tokens de concepto, ventana, paridad de proyección), nunca frases
  exactas del prompt.

Paridad fuente↔generado (NO copias: proyección): el generador
`scripts/cdad-generate.py` (patrón de tests/test_cdad_generate.py,
subprocess caja negra) regenera el staging con los parámetros del
Makefile; los agentes del repo deben ser BYTE-IDÉNTICOS al staging
(salidas declaradas del generador, nunca editadas a mano) y contener las
mismas marcas estructurales que la fuente canónica
`sources/roles/orchestrator.md`.

RED esperado (según plan T3): fallan las aserciones sobre las marcas
NUEVAS declaradas por el plan (distinción de delegación externa en
fuentes, proyección en generados, frontera de autoridad INV-4,
escritor-único en la fuente canónica si aún no está declarada ahí);
PASAN las de CONSERVACIÓN (el SPAWN GUARD/anti-recursión y el
escritor-único que ya existen). Todo fallo RED es AssertionError de
comportamiento (documento sin la marca declarada por el contrato);
nunca ImportError/SyntaxError/NameError.

Reformulación declarada por 006-002 U2 (PD-1/PD-3; enmienda A-1): la mitad
«nombre del mutador concreto» del guard en SKILL.md se invierte — la skill no
nombra la herramienta de un runtime; el guard se conserva en forma abstracta y
el nombre concreto vive en el orquestador del runtime. El resto del guard
(prohibición, sub-subagentes, anti-bucle, handoff) queda intacto.

Reformulación declarada por 006-002 U3 (PD-9; enmienda A-1): la superficie
`references/claude-code-delegation.md` sale del árbol instalable, así que su
aserción de conservación se repunta al nuevo dueño (la evidencia no instalable
bajo `docs/**`, donde PD-9 manda preservar el detalle retirado) y el assert de
retiro; las otras dos superficies de esa aserción (SKILL.md abstracto + los
orquestadores generados) siguen cubiertas por los tests parametrizados de
arriba.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Helpers de 006-002 U3 (una sola definición de «evidencia no instalable»,
# PD-9): la superficie a la que se repunta el assert de conservación del
# consumidor retirado.
from tests.test_006_002_u3_runtime_references import (
    doc_relative,
    framed_evidence_documents,
)

REPO = Path(__file__).resolve().parents[1]

# Archivos declarados por plan.md T3 (§Files) — superficie de PD-9.
SKILL = REPO / "skills" / "cdad-cycle" / "SKILL.md"
ORCH_SRC = REPO / "sources" / "roles" / "orchestrator.md"
CC_REF = REPO / "skills" / "cdad-cycle" / "references" / "claude-code-delegation.md"
GEN_OC = REPO / "agents" / "cdad-orchestrator.md"
GEN_CC = REPO / "agents" / "claude-code" / "cdad-orchestrator.md"
STATE = REPO / "docs" / ".cdad-state.json"

GENERATOR = REPO / "scripts" / "cdad-generate.py"
EXTERNALLY_GENERATED = {
    GEN_OC: ("opencode", "agents/opencode/cdad-orchestrator.md"),
    GEN_CC: ("claude-code", "agents/claude-code/cdad-orchestrator.md"),
}
ROLES = ("architect", "test-writer", "implementer", "reviewer", "scribe")

# ---------------------------------------------------------------- helpers


def load(path: Path, why: str) -> str:
    if not path.is_file():
        pytest.fail(f"documento requerido por {why} no existe: {path}")
    return path.read_text(encoding="utf-8")


def guard_windows(text: str, needle: str, before: int, after: int) -> list[tuple[int, int]]:
    """Ventanas (índices de líneas, inclusivas) alrededor de cada ancla del
    SPAWN GUARD / anti-recursión — marcadores estructurales, no frases."""
    ranges = []
    for idx, line in enumerate(text.splitlines()):
        if re.search(needle, line):
            ranges.append((max(0, idx - before), min(len(text.splitlines()), idx + after)))
    if not ranges:
        return []
    merged = [list(ranges[0])]
    for start, end in ranges[1:]:
        if start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(r) for r in merged]


def window_text(text: str, ranges: list[tuple[int, int]]) -> str:
    lines = text.splitlines()
    return "\n".join("\n".join(lines[s : e + 1]) for s, e in ranges)


def first_line_of(text: str, needle: str) -> int | None:
    for idx, line in enumerate(text.splitlines()):
        if re.search(needle, line):
            return idx
    return None


# Marcas de conservación del SPAWN GUARD (discovery §7 — texto ancla).
SPAWN_MUTATOR = r"(?i)sessions_spawn"  # el mutador prohibido del guard
SPAWN_BAN_WORD = r"(?i)forbidden|forbidden|prohibited|banned|banned|forbid"
SUB_SUBAGENT = r"(?i)sub\s*-?\s*sub\s*-?\s*agents?|sub-subagentes"
ANTI_LOOP = r"(?i)\blog\b|loop|retry|reintent|retry"
HANDOFF = r"(?i)handoff|return control|return control|devolver|return control"
NEGATION = r"(?i)\bno\b|\bnot\b|\bnever\b|\bwithout\b|\bsin\b|\bnunca\b|don'?t|must not"

# Componentes de la DISTINCIÓN (spec PD-9 + plan T3/D8: la
# delegación externa autorizada coordinador→worker ENTRE CLIs NO es
# recursión de subagentes del mismo runtime; no amplía autoridad; el
# worker no escribe el state).
DIST_EXTERNAL = r"(?i)delegaci[óo]n externa|external delegation|external delegation"
DIST_COORDINATOR = r"(?i)coordinador|coordinator"
DIST_WORKER = r"(?i)\bworker\b"
DIST_NOT_RECURSION = (
    r"(?i)\bno\s+(?:es\s+)?recursi[óo]n"
    r"|\bnot\s+(?:is\s+)?recursion"
    r"|entre\s+CLIs|(?:between|across)\s+CLIs"
    r"|(?:otro|other|another|different)\s+(?:CLI|runtime)"
)
DIST_BOUNDARY_AUTHORITY = (
    r"(?i)(no\s+(?:expande?|ampl[íi]a|extiende?|incrementa?|añade)"
    r"|not\s+(?:\w+\s+)?expand\w*|does\s+not\s+(?:expand|increase|broaden|amplify|extend)"
    r"|without\s+(?:expanding|amplifying|expansion)"
    r"|no\s+(?:expansi[óo]n|ampliaci[óo]n|authority\s+expansion))"
)
DIST_WORKER_STATE = (
    r"(?i)(?:no\s+escribe|not\s+write\w*|without\s+writing|does\s+not\s+write\w*"
    r"|no\s+enabled\s+to\s+write|without\s+writing)"
)
DIST_STATE = r"(?i)\bstate\b|\.cdad-state"
SINGLE_WRITER_DECL = (
    r"(?i)single\s+writer|sole\s+writer|unique\s+writer"
    r"|escritor\s+[uú]\w*|[uú]nic\w*\s+escritor|uni\w*[\s]*escritor"
    r"|(?:only|alone|solo|only)\s+(?:the\s+)?(?:orchestrator|orquestador)"
)
NO_SANDBOX = r"(?i)\bsandbox\b|isolat\w*|guarantee|guarant\w*"


# Un test por faceta de PD-9 + INV-1/INV-4/INV-8:


# ------------------------------------------------------------------ PD-9
# (a) CONSERVACIÓN del SPAWN GUARD — el texto heredado NO fue eliminado.


def test_pd9_spawn_guard_conserved_in_skillmd():
    """PD-9: el SPAWN GUARD de skills/cdad-cycle/SKILL.md (discovery §7,
    :136-143) permanece: bloque marcado, prohibición de spawn desde
    subagente (sub-subagentes), anti-bucle, y devolución por handoff.

    Reformulado en el RED de 006-002 U2 (PD-1/PD-3; enmienda A-1): el nombre
    concreto del mutador (`sessions_spawn`) sale de la capa SKILL — el guard
    se conserva en forma ABSTRACTA y el nombre de la herramienta lo declara el
    orquestador del runtime (dueño de la capa de agente). La conservación del
    guard (aserción marcada + prohibición + sub-subagentes + anti-bucle +
    handoff) no se pierde: es el resto de esta misma aserción.
    """
    text = load(SKILL, "PD-9/plan T3")
    ranges = guard_windows(text, r"SPAWN GUARD", 10, 45)
    block = window_text(text, ranges if ranges else [(0, len(text.splitlines()) - 1)])
    assert ranges, (
        "PD-9 violada: skills/cdad-cycle/SKILL.md ya no contiene el bloque "
        "marcado SPAWN GUARD (conservación exigida por PD-9/plan T3)"
    )
    assert re.search(SPAWN_BAN_WORD, block), (
        "PD-9/conservación SKILL.md: la ventana SPAWN GUARD no declara la "
        "prohibición del spawn desde subagente"
    )
    # 006-002 U2 (PD-1/INV-1): la skill no nombra la herramienta de spawn de un
    # runtime; el §4 la generaliza y el nombre concreto vive en el orquestador
    # del runtime (adaptador fuente + agentes generados).
    assert not re.search(SPAWN_MUTATOR, block), (
        "PD-9/conservación SKILL.md + 006-002 PD-1 (U2): la ventana SPAWN GUARD "
        "nombra el mutador concreto de un runtime (sessions_spawn); el guard de "
        "la skill es abstracto — el nombre de la herramienta pertenece al "
        "orquestador del runtime"
    )
    assert re.search(SUB_SUBAGENT, block), (
        "PD-9/conservación SKILL.md: la ventana no menciona los "
        "sub-subagentes (prohibición heredada de spawn)"
    )
    assert re.search(ANTI_LOOP, block) and re.search(NEGATION, block), (
        "PD-9/conservación SKILL.md: la ventana ya no contiene la regla "
        "anti-bucle con su negación (no despawn en bucle)"
    )
    assert re.search(HANDOFF, block), (
        "PD-9/conservación SKILL.md: la ventana ya no declara la devolución "
        "por handoff packet al orquestador"
    )


@pytest.mark.parametrize(
    "label,path,needle",
    [
        ("fuente roles/orchestrator.md", ORCH_SRC, r"(?i)recursi|spawn"),
        ("generado opencode", GEN_OC, r"(?i)spawn"),
        ("generado claude-code", GEN_CC, r"(?i)spawn"),
    ],
    ids=["source-orchestrator", "generated-oc", "generated-cc"],
)
def test_pd9_anti_recursion_conserved(label, path, needle):
    """PD-9: la anti-recursión se CONSERVA en la fuente canónica
    sources/roles/orchestrator.md (:74-76) y en los orquestadores
    generados (proyectados por make agents, nunca editados a mano)."""
    text = load(path, "PD-9/plan T3")
    ranges = guard_windows(text, needle, 8, 40)
    assert ranges, f"PD-9 violada: {label} ya no menciona spawn/recursión"
    block = window_text(text, ranges)
    assert re.search(SUB_SUBAGENT, block) or re.search(r"(?i)recursi", block), (
        f"PD-9/conservación {label}: sin la prohibición de spawn "
        "sub-subagente/recursión nativa"
    )
    assert re.search(NEGATION, block), (
        f"PD-9/conservación {label}: sin negación (prohibición/never) en la "
        "ventana anti-recursión"
    )
    assert re.search(HANDOFF, block), (
        f"PD-9/conservación {label}: sin devolución por handoff al orquestador"
    )


def test_pd9_spawn_guard_conservation_survives_the_reference_withdrawal():
    """PD-9 (reformulado por 006-002 U3, PD-9 — enmienda A-1): la prohibición
    explícita que declaraba `references/claude-code-delegation.md` (discovery §7
    :63-69: prohibición + SPAWN GUARD + incidente) NO se pierde cuando esa
    referencia sale del árbol instalable: (i) el consumidor instalable ya no
    está — la prohibición sigue viva donde vive el runtime (la skill abstracta y
    el orquestador generado, cubiertos por los tests parametrizados de arriba);
    (ii) el detalle retirado se preserva como evidencia NO instalable bajo
    `docs/**` (006-002 PD-9), con la prohibición sub-agente→sub-agente y su
    registro del incidente."""
    assert not CC_REF.is_file(), (
        "PD-9 + 006-002 U3: references/claude-code-delegation.md sigue en el "
        "árbol instalable — la referencia por runtime sale de la skill (su "
        "detalle se preserva como evidencia no instalable bajo docs/**)"
    )

    evidence = framed_evidence_documents()
    assert evidence, (
        "PD-9 + 006-002 U3: no hay evidencia NO instalable bajo docs/** que "
        "conserve el detalle retirado — la prohibición de spawn y su incidente "
        "no pueden perderse con el archivo"
    )

    preserved: list[str] = []
    offenders: list[str] = []
    for path in evidence:
        text = path.read_text(encoding="utf-8")
        if not (re.search(SPAWN_BAN_WORD, text)
                and re.search(SUB_SUBAGENT, text)):
            continue
        preserved.append(doc_relative(path))
        if not re.search(r"(?i)incident|incidente|observad|hist[óo]ric|"
                         r"history|evidence|evidencia", text):
            offenders.append(doc_relative(path))
    assert preserved, (
        "PD-9 + 006-002 U3: la evidencia preservada no conserva la prohibición "
        "de spawn sub-agente→sub-agente del consumidor retirado (SPAWN GUARD + "
        "prohibición + sub-agentes) — el detalle histórico no puede "
        "desaparecer: la retirada lo conserva bajo docs/**"
    )
    assert not offenders, (
        "PD-9 + 006-002 U3: la evidencia que conserva la prohibición no la "
        "declara como detalle retirado/histórico del consumidor que salió del "
        f"árbol instalable: {offenders!r}"
    )


# (b) DISTINCIÓN de la delegación externa autorizada — MARCAS NUEVAS del plan.


@pytest.mark.parametrize(
    "label,path,needle,tokens",
    [
        ("skills/cdad-cycle/SKILL.md", SKILL, "SPAWN GUARD", None),
        ("sources/roles/orchestrator.md", ORCH_SRC, r"(?i)recursi|spawn", None),
    ],
    ids=["skillmd", "source-orchestrator"],
)
def test_pd9_external_delegation_distinction_present_in_sources(label, path, needle, tokens):
    """PD-9/D8: la distinción entre la delegación externa autorizada
    (coordinador→worker entre CLIs) y la recursión de subagentes del mismo
    runtime EXISTE en las fuentes canónicas, cerca del SPAWN GUARD
    (ventana ±80 líneas — marcador estructural, no frase).

    Reformulado por 006-002 U3 (PD-9; enmienda A-1): la tercera superficie que
    parametrizaba esta aserción (`references/claude-code-delegation.md`) sale
    del árbol instalable y su conservación se verifica ahora sobre la evidencia
    no instalable (`docs/**`) en
    `test_pd9_spawn_guard_conservation_survives_the_reference_withdrawal`."""
    text = load(path, "PD-9 (distinción)/plan T3")
    guard_lines = [
        idx
        for idx, line in enumerate(text.splitlines())
        if re.search(needle, line)
    ]
    assert guard_lines, f"PD-9: {label} sin ancla de spawn-guard"
    ext = first_line_of(text, DIST_EXTERNAL)
    coord = first_line_of(text, DIST_COORDINATOR)
    worker = first_line_of(text, DIST_WORKER)
    not_rec = first_line_of(text, DIST_NOT_RECURSION)
    assert ext is not None, (
        f"PD-9 violada en {label}: NO existe la distinción — falta el "
        "concepto «delegación externa» (la prohibición spawn sigue sin "
        "distinguirse de la delegación externa autorizada coordinador→worker)"
    )
    assert coord is not None and worker is not None, (
        f"PD-9 violada en {label}: la distinción no declara el recorrido "
        "coordinador→worker (falta «coordinador» o «worker»)"
    )
    assert not_rec is not None, (
        f"PD-9 violada en {label}: la distinción no declara que NO es "
        "recursión de subagentes dentro del mismo runtime / que cruza CLIs"
    )
    # Co-ubicación: la distinción debe estar cerca del guard (±80 líneas).
    nearest = min(abs(idx - g) for idx in (ext, coord, worker, not_rec) for g in guard_lines)
    assert nearest <= 80, (
        f"PD-9 violada en {label}: la distinción está a {nearest} líneas del "
        "SPAWN GUARD/anti-recursión — no está co-ubicada con la prohibición"
    )


@pytest.mark.parametrize(
    "label,path,runtime",
    [
        ("generado opencode", GEN_OC, "opencode"),
        ("generado claude-code", GEN_CC, "claude-code"),
    ],
    ids=["generated-oc", "generated-cc"],
)
def test_pd9_distinction_projected_into_generated_and_staging_parity(label, path, runtime):
    """PD-9 (paridad fuente↔generado, NO copias — proyección): los orquestadores
    generados (1) existen, (2) son byte-idénticos a la regeneración del
    generador con los parámetros del Makefile (salidas declaradas, nunca
    editadas a mano) y (3) llevan las MISMAS marcas del SPAWN GUARD y de la
    distinción que la fuente canónica sources/roles/orchestrator.md."""
    text = load(path, "PD-9 (proyección)/plan T3")
    for token, desc in [
        (SPAWN_BAN_WORD, "prohibición spawn"),
        (SUB_SUBAGENT, "sub-subagentes/recursión nativa"),
        (DIST_EXTERNAL, "distinción delegación externa"),
        (DIST_COORDINATOR, "rol del coordinador en la distinción"),
        (DIST_WORKER, "rol del worker en la distinción"),
        (DIST_NOT_RECURSION, "no-recursión / cruce entre CLIs"),
    ]:
        assert re.search(token, text), (
            f"PD-9 violada en {label}: el generado NO proyecta la marca "
            f"«{desc}» declarada por PD-9/solución D8 (editaste a mano o la "
            "fuente + make agents aún no la proyecta)"
        )
    # Paridad por byte con la regeneración del generador
    # (patterns: tests/test_cdad_generate.py + make agents del plan T3).
    assert GENERATOR.is_file(), (
        "paridad PD-9: el generador declarado scripts/cdad-generate.py no "
        "existe (proyección fuente↔generado no verificable)"
    )
    profile = "optimus"
    mk = (REPO / "Makefile").read_text(encoding="utf-8")
    m = re.search(r"(?m)^PROFILE\s*\?=\s*(\S+)", mk)
    if m:
        profile = m.group(1)
    with tempfile.TemporaryDirectory(prefix="cdad-t3-parity-") as tmp:
        out = Path(tmp) / "staging"
        proc = subprocess.run(
            [
                sys.executable,
                str(GENERATOR),
                "--runtime",
                runtime,
                "--stack",
                "odoo",
                "--profile",
                profile,
                "--out",
                str(out),
            ],
            cwd=str(REPO),
            text=True,
            capture_output=True,
            check=False,
        )
        assert proc.returncode == 0, (
            f"paridad PD-9: la regeneración ({runtime}, stack odoo, perfil "
            f"{profile}) falló: stderr={proc.stderr!r}"
        )
        staged = out / EXTERNALLY_GENERATED[(GEN_OC if runtime == "opencode" else GEN_CC)][1]
        assert staged.is_file(), (
            f"paridad PD-9: el staging no publicó el orquestador para {runtime}"
        )
        staged_sha = hashlib.sha256(staged.read_bytes()).hexdigest()
        committed_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        assert staged_sha == committed_sha, (
            f"PD-9 violada: paridad fuente↔generado rota para {label} — el "
            "generado del repo NO es byte-idéntico a la regeneración del "
            f"generador (perfil {profile}); una salida declarada fue editada "
            "a mano o make agents no se corrió tras editar la fuente"
        )


# ------------------------------------------------------------------- INV-1
# El orquestador sigue siendo el único escritor de docs/.cdad-state.json.


@pytest.mark.parametrize(
    "label,path",
    [
        ("fuente roles/orchestrator.md", ORCH_SRC),
        ("generado opencode", GEN_OC),
        ("generado claude-code", GEN_CC),
    ],
    ids=["source-orchestrator", "generated-oc", "generated-cc"],
)
def test_inv1_orchestrator_sole_writer_of_state(label, path):
    """INV-1/PD-9: el orquestador es el ÚNICO escritor de
    docs/.cdad-state.json — el artefacto del state existe y la declaración
    sigue presente en la fuente canónica (plan T3 la declara ahí) y en los
    generados, donde vive en la fila `| orchestrator` del roles-contract §2
    compuesto (discovery §2.7: agents/cdad-orchestrator.md:146 — el
    orquestador escribe docs/** + state; los roles no)."""
    assert STATE.is_file(), (
        "INV-1: el artefacto del state docs/.cdad-state.json no existe"
    )
    text = load(path, "INV-1/PD-9")
    writer_decl = re.search(SINGLE_WRITER_DECL, text)
    # Fila `| orchestrator` del roles-contract compuesto que declara la
    # escritura del state (con "docs" y "state" en la fila).
    orch_row = None
    for m in re.finditer(r"(?m)^\|\s*orchestrator\b[^\n]*$", text):
        if re.search(r"\bstate\b|(?:\bdocs\b)|\.cdad-state", m.group(0)):
            orch_row = m.group(0)
            break
    if path is ORCH_SRC:
        # plan T3 declara para la fuente canónica: "+ el orquestador como
        # escritor único del state" — la declaración debe existir ahí.
        assert writer_decl or orch_row, (
            f"INV-1 violada en {label}: la fuente canónica no declara al "
            "orquestador como escritor único del state (plan T3 exige la "
            "declaración de escritor único en fuentes/agentes — PD-9 "
            "verificable)"
        )
    else:
        # Conservación: en los generados la invariante ya vive en la fila
        # `| orchestrator` del roles-contract compuesto (discovery §2.7) —
        # T3 NO debe eliminarla; el GREEN conserva o agrega el row/body.
        assert orch_row or writer_decl, (
            f"INV-1 violada en {label}: el roles-contract compuesto ya no "
            "declara al orquestador como escritor del state de "
            "docs/.cdad-state.json"
        )
        # Los otros roles NO escriben el state (frontera de la tabla §2).
        for m in re.finditer(
            r"(?m)^\|\s*(" + "|".join(ROLES) + r")\b[^\n]*$", text
        ):
            row = m.group(0)
            assert ".cdad-state" not in row, (
                f"INV-1 violada en {label}: la fila del roles-contract de "
                f"{m.group(1)!r} concede escritura de docs/.cdad-state.json "
                "a un rol no-orquestador"
            )


# ------------------------------------------------------------------- INV-4
# Una delegación NO amplía autoridad ni permite al worker escribir el state.


@pytest.mark.parametrize(
    "label,path",
    [
        ("fuente roles/orchestrator.md", ORCH_SRC),
        ("generado opencode", GEN_OC),
        ("generado claude-code", GEN_CC),
    ],
    ids=["source-orchestrator", "generated-oc", "generated-cc"],
)
def test_inv4_delegation_does_not_expand_worker_authority(label, path):
    """INV-4/PD-9: donde se declara la distinción de la delegación externa,
    también se declara su frontera de autoridad: la delegación no amplía
    autoridad/alcance y el worker NO escribe el state (PD-9/INV-4/D8)."""
    text = load(path, "INV-4/PD-9")
    assert re.search(DIST_EXTERNAL, text), (
        f"INV-4 violada en {label}: sin la distinción de la delegación "
        "externa (el plan T3 la declara en fuentes y generados)"
    )
    ext_idx = first_line_of(text, DIST_EXTERNAL)
    lines = text.splitlines()
    boundary = "\n".join(lines[max(0, ext_idx - 15) : ext_idx + 16])
    assert re.search(DIST_BOUNDARY_AUTHORITY, boundary), (
        f"INV-4 violada en {label}: la distinción de la delegación externa "
        "no declara su frontera — falta la negación «la delegación no "
        "amplía autoridad/alcance» en el entorno de la distinción"
    )
    assert re.search(DIST_WORKER_STATE, boundary) and re.search(
        DIST_STATE, boundary
    ), (
        f"INV-4 violada en {label}: la distinción no declara que el worker "
        "NO escribe el state (queda concediendo la escritura de "
        "docs/.cdad-state.json al worker)"
    )


# ------------------------------------------------------------------- INV-8
# Los límites honestos se conservan/regeneran en el texto nuevo: una
# separación de procesos/clis NO es un sandbox (sin promesa de aislamiento).


@pytest.mark.parametrize(
    "label,path",
    [
        ("skills/cdad-cycle/SKILL.md", SKILL),
        ("sources/roles/orchestrator.md", ORCH_SRC),
        ("generado opencode", GEN_OC),
        ("generado claude-code", GEN_CC),
    ],
    ids=["skillmd", "source-orchestrator", "generated-oc", "generated-cc"],
)
def test_inv8_no_unbacked_isolation_promise(label, path):
    """INV-8: el texto DECLARADO por T3 (la distinción de la delegación
    externa, ±20 líneas alrededor de su marca) NO promete aislamiento ni
    sandbox del recorrido coordinador→worker: toda mención de
    sandbox/aislamiento/garantía lleva negación (precedente
    test_cdad_generate.py PD-15). En RED la distinción no existe todavía —
    el guard se SKIPEA honestamente y se activa con el GREEN (freno de
    no-regresión sobre el texto nuevo).

    Reformulado por 006-002 U3 (PD-9; enmienda A-1): la superficie
    `references/claude-code-delegation.md` sale del árbol instalable y deja de
    ser una superficie del texto VIVO; la cobertura de INV-8 sobre el texto
    vivo (skill + fuente canónica + ambos orquestadores generados) y sobre la
    evidencia preservada (PD-9) se conserva."""
    text = load(path, "INV-8/PD-9")
    ext_idx = first_line_of(text, DIST_EXTERNAL)
    if ext_idx is None:
        pytest.skip(
            f"INV-8 ({label}): la distinción de la delegación externa no "
            "existe todavía (RED de PD-9/D8); el guard de honestidad se "
            "activa sobre el texto nuevo del GREEN"
        )
    lines = text.splitlines()
    window = "\n".join(lines[max(0, ext_idx - 20) : ext_idx + 21])
    offending = [
        line.strip()
        for line in window.splitlines()
        if re.search(NO_SANDBOX, line) and not re.search(NEGATION, line)
    ]
    assert not offending, (
        f"INV-8 violada en {label}: la distinción promete "
        f"aislamiento/sandbox/garantía sin negación (líneas: {offending!r}) "
        "— un cambio de CLI/proceso NO es un sandbox ni garantiza otra "
        "familia de modelo (INV-8)"
    )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
