#!/usr/bin/env python3
"""006-006 U4 RED — el rol reviewer y los agentes generados declaran la
revisión de borrador.

Contrato:
- `docs/specs/006-006-spec-plan-review/spec.md` — §2.8 (el rol y los agentes:
  la etapa 2, el artefacto `plan-review.md` y la revisión de borrador),
  §3 PD-11 (el rol y los agentes generados nombran la revisión de borrador;
  `make staging` determinista; `make validate` verde), §6 V-2 (el determinismo
  de `cdad-generate.py`) e INV-4 (no se crean agentes nuevos: se alinean los
  declarados).
- `docs/specs/006-006-spec-plan-review/plan.md` §3 ficha U4 (archivos, RED,
  regresiones, A-1) y su bloque `plan-tasks` (los `observable_checks` de U4).

Superficie bajo prueba — TEXTO y PROCESO REAL:

- `sources/roles/reviewer.md` — la FUENTE EDITABLE del rol: su fila de la
  tabla de contrato (la que compone la fila de §2) y su sección de directiva;
- los CUATRO agentes del reviewer — SALIDAS DECLARADAS de
  `scripts/cdad-generate.py` (`Makefile`:15-18), que NUNCA se editan a mano:
  se generan invocando el generador como PROCESO en una COPIA DESCARTABLE del
  repo (nunca en el árbol de trabajo, nunca en el HOME);
- `make staging` — el determinismo (control V-2), medido en esa misma copia
  descartable.

Oráculos (por CONCEPTO, no por frase exacta; sólo se cita verbatim lo que la
ficha cita: el artefacto `plan-review.md`):

- O-S1 — la fila de la tabla de contrato declara las etapas 2 Y 4.
- O-S2 — la fila nombra el artefacto `plan-review.md` ADEMÁS de `review.md`
  (los dos: `plan-review.md` no sustituye a `review.md`).
- O-S3 — el texto de la fila dice que la revisión de BORRADOR es parte del
  rol.
- O-S4 — la sección de directiva nombra la revisión de borrador NO APROBADO
  como parte del encargo del rol.
- O-A1 — los CUATRO agentes GENERADOS (en la copia descartable) lo contienen.
- O-A2 — los CUATRO agentes PROMOVIDOS en el repo (`make agents`) lo contienen.
- O-D1 — CONTROL (V-2): `make staging` es determinista: dos corridas, mismos
  bytes (comparación byte a byte de los cuatro agentes del reviewer).

`make validate` NO es oráculo de este RED (declarado): el bloque F011 del
validador contrasta la instalación ACTIVA del HOME (`install.sh --check`) y
falla en este checkout por una deriva PREEXISTENTE y ajena a esta feature (la
copia instalada en el HOME va por detrás de este árbol). Convertirlo en
oráculo daría un RED que falla por el AMBIENTE y no por el contrato; su
resultado observado se declara en la entrega de la unidad.

Fallos del modo RED esperado: `AssertionError` de comportamiento sobre el
texto (falta la etapa 2, falta el artefacto `plan-review.md`, falta la
revisión de borrador) o `pytest.fail` de estado conductual (fuente o agente
requerido inexistente). NUNCA ImportError, SyntaxError, NameError ni error de
fixture. Nada de skip.

A-1 (plan §4): este RED **NO reemplaza ningún oráculo vigente**; sólo AÑADE
casos. Comprobado sobre las regresiones que nombra la ficha
(`test_cdad_generate`, `test_role_packets`, `test_role_packet_render`,
`test_005_006_t2_intake`, `test_bash_policy_selection`,
`test_opencode_read_map_and_steps`, `test_005_004_t2_installer_claims`,
`test_006_002_u1_delegation_section`, `test_006_002_u3_runtime_references`,
`test_006_003_u3_texts_without_profiles`, `test_006_005_u4_single_entry`):
ninguna fija el texto de `sources/roles/reviewer.md` ni la declaración de los
cuatro agentes del reviewer — las que miden el paquete del reviewer calculan
el sha256 del substage DINÁMICAMENTE (luego no lo fijan). Los fixtures
compartidos (`DRAFT_PLAN_RELPATH`) no se tocan: este RED no usa ese fixture
(usa su propia copia descartable del repo).

Mapeo test → postcondición:

  test_pd11_role_source_contract_row_declares_stages_2_and_4
      -> PD-11 (O-S1): la fila de la tabla de contrato declara las etapas 2 y 4.
  test_pd11_role_source_contract_row_declares_the_plan_review_artifact
      -> PD-11 (O-S2): el artefacto `plan-review.md` además de `review.md`.
  test_pd11_role_source_contract_row_says_the_draft_review_is_part_of_the_role
      -> PD-11 (O-S3): el texto de la fila dice que la revisión de borrador es
         parte del rol.
  test_pd11_role_source_directive_names_the_review_of_an_unapproved_draft
      -> PD-11 (O-S4): la sección de directiva nombra la revisión de borrador
         no aprobado.
  test_pd11_generated_reviewer_agents_carry_the_declaration
      -> PD-11 (O-A1): los cuatro agentes generados, tras la generación real.
  test_pd11_promoted_reviewer_agents_carry_the_declaration
      -> PD-11 (O-A2): los cuatro agentes promovidos en el repo.
  test_pd11_make_staging_is_deterministic_across_two_runs
      -> PD-11 / V-2 (O-D1, control): `make staging` determinista.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
ROLE_SOURCE = REPO / "sources" / "roles" / "reviewer.md"

# Los CUATRO agentes del reviewer: SALIDAS DECLARADAS de scripts/cdad-generate.py
# (`Makefile`:15-18). En el staging de la copia descartable, bajo
# build/staging/agents/<runtime>/; en el repo, promovidos por `make agents`.
STAGED_AGENTS = (
    "agents/opencode/cdad-reviewer.md",
    "agents/opencode/cdad-reviewer-odoo.md",
    "agents/claude-code/cdad-reviewer.md",
    "agents/claude-code/cdad-reviewer-odoo.md",
)
PROMOTED_AGENTS = (
    "agents/cdad-reviewer.md",
    "agents/cdad-reviewer-odoo.md",
    "agents/claude-code/cdad-reviewer.md",
    "agents/claude-code/cdad-reviewer-odoo.md",
)

# El artefacto del dictamen (verbatim de §2.8 y de la ficha U4).
PLAN_REVIEW_ARTIFACT = "plan-review.md"
# El artefacto vigente del dictamen de resultado (verbatim de §2.8: "además de").
REVIEW_ARTIFACT = "review.md"
# El artefacto de la revisión de borrador, el que NO sustituye al anterior.
PLAN_REVIEW_RE = re.compile(re.escape(PLAN_REVIEW_ARTIFACT))
# `review.md` SIN el prefijo de `plan-` (el artefacto vigente, nombrado aparte).
STANDALONE_REVIEW_RE = re.compile(r"(?<![A-Za-z0-9_-])review\.md\b")

# Las etapas del contrato, por número: el dígito o un nombre equivalente.
STAGE_2_NAMES = re.compile(
    r"specification|\bspec\b|\bdraft review\b|plan-review|stage\s*2|etapa\s*2",
    re.IGNORECASE,
)
STAGE_4_NAMES = re.compile(
    r"\breview\b|final review|result review|stage\s*4|etapa\s*4",
    re.IGNORECASE,
)

# El concepto «borrador» (el objeto revisado en la etapa 2).
DRAFT_WORD = re.compile(
    r"\bdraft\b|\bborrador\b|\bpre-?approval\b|\bun[- ]?approved\b", re.IGNORECASE
)
# El concepto «revisión».
REVIEW_WORD = re.compile(r"\breview\w*|\brevisi[oó]n\b", re.IGNORECASE)
# El concepto «no aprobado» (el borrador revisado NO lleva aprobación).
NOT_APPROVED = re.compile(
    r"\bun[- ]?approved\b|\bnot (?:yet |been )?approved\b|\bnever approved\b|"
    r"\bno approval\b|\bwithout approval\b|\bno aprobado\b|\bsin aprob\w+|"
    r"\bnon approuv\w*|\bpending approval\b|\baprobaci[oó]n pendiente\b",
    re.IGNORECASE,
)

# Lo que NO se copia de la copia descartable: el estado del ciclo (.cdad), el
# historial de git y —declarado— el fichero privado de patrones sensibles.
_IGNORED_NAMES = frozenset(
    {
        ".git",
        ".cdad",
        "build",
        "__pycache__",
        ".pytest_cache",
        "logs",
        ".opencode",
        ".sensitive-patterns.local",
    }
)


def _ignore(_dirname: str, names: list[str]) -> set[str]:
    return {name for name in names if name in _IGNORED_NAMES}


# ---------------------------------------------------------------------------
# Helpers (caja negra; archivo faltante = estado conductual)
# ---------------------------------------------------------------------------


def _load(path: Path, label: str) -> str:
    """Artefacto requerido faltante = estado conductual (nunca ImportError)."""
    if not path.is_file():
        pytest.fail(f"{label}: el artefacto requerido no existe: {path}")
    return path.read_text(encoding="utf-8")


def _cells(line: str) -> list[str]:
    """Las celdas de una fila de tabla Markdown (sin celdas fantasma)."""
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    parts = stripped.split("|")
    return [part.strip() for part in parts[1:-1]]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells)


def _contract_row(text: str, label: str) -> dict[str, str]:
    """La fila del contrato del rol `reviewer`, por nombre de columna.

    Se localiza la TABLA (la que compone la fila de §2) por su cabecera — la
    que nombra Role/Stages/Does/Artifact — y dentro de ella la fila cuya
    primera celda es `reviewer`. Así el oráculo no depende del número de
    línea ni del orden de las columnas.
    """
    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        cells = _cells(line)
        lowered = {cell.lower() for cell in cells}
        if {"role", "stages", "artifact"} <= lowered:
            header_index = index
            break
    assert header_index is not None, (
        f"{label}: no se encontró la tabla de contrato (la que compone la "
        "fila de §2: Role / Stages / Does / Artifact)."
    )
    header = _cells(lines[header_index])
    columns = {name.lower(): index for index, name in enumerate(header)}
    for line in lines[header_index + 1 :]:
        cells = _cells(line)
        if not cells:
            break
        if _is_separator(cells):
            continue
        if cells[0].lower() == "reviewer":
            return {
                name: (cells[index] if index < len(cells) else "")
                for name, index in columns.items()
            }
    raise AssertionError(
        f"{label}: la tabla de contrato no tiene la fila del rol `reviewer`."
    )


def _source_directive(text: str, label: str) -> str:
    """La sección de directiva de la fuente editable."""
    start = text.find("<!-- cdad-section:directive -->")
    assert start != -1, (
        f"{label}: la fuente no tiene la sección de directiva "
        "(`<!-- cdad-section:directive -->`)."
    )
    end = text.find("<!-- /cdad-section -->", start)
    assert end != -1, (
        f"{label}: la sección de directiva de la fuente no está cerrada."
    )
    return text[start:end]


def _agent_directive(text: str, label: str) -> str:
    """La sección «Main directive» del agente generado (el render de la
    sección de directiva de la fuente)."""
    match = re.search(r"(?m)^#{2,}[ \t]*Main directive[ \t]*$", text)
    assert match is not None, (
        f"{label}: el agente no tiene la sección «Main directive» (el render "
        "de la sección de directiva de la fuente)."
    )
    rest = text[match.end() :]
    following = re.search(r"(?m)^#{2,}[ \t]", rest)
    return rest[: following.start()] if following else rest


def _near_chars(text: str, first: re.Pattern, second: re.Pattern, radius: int) -> bool:
    """True si algún match de `first` tiene un match de `second` a <= `radius`
    caracteres (el wrapping no rompe la pareja)."""
    for match in first.finditer(text):
        low = max(0, match.start() - radius)
        high = min(len(text), match.end() + radius)
        if second.search(text, low, high):
            return True
    return False


def _names_stage(cell: str, number: int) -> bool:
    """True si la celda nombra esa etapa (por su número o por un nombre
    equivalente): la convención del repo es el número («1 Discovery, 2 Spec»,
    «3: audit, …», «4», «5»)."""
    if re.search(rf"\b{number}\b", cell):
        return True
    return bool((STAGE_2_NAMES if number == 2 else STAGE_4_NAMES).search(cell))


# ---------------------------------------------------------------------------
# Los cuatro oráculos del TEXTO (compartidos por la fuente y por los agentes)
# ---------------------------------------------------------------------------


def _assert_stages(row: dict[str, str], label: str) -> None:
    stages = row.get("stages", "")
    assert _names_stage(stages, 2), (
        f"{label}: la fila del contrato del rol reviewer no declara la ETAPA 2 "
        f"(la revisión del borrador): la celda «Stages» dice {stages!r}."
    )
    assert _names_stage(stages, 4), (
        f"{label}: la fila del contrato del rol reviewer no declara la ETAPA 4 "
        f"(la revisión del resultado): la celda «Stages» dice {stages!r}."
    )


def _assert_artifacts(row: dict[str, str], label: str) -> None:
    artifact = row.get("artifact", "")
    assert PLAN_REVIEW_RE.search(artifact), (
        f"{label}: la fila del contrato del rol reviewer no nombra el "
        f"artefacto `{PLAN_REVIEW_ARTIFACT}` (el dictamen de la revisión de "
        f"borrador): la celda «Artifact» dice {artifact!r}."
    )
    assert STANDALONE_REVIEW_RE.search(artifact), (
        f"{label}: la fila del contrato del rol reviewer no nombra el "
        f"artefacto `{REVIEW_ARTIFACT}` ADEMÁS de `{PLAN_REVIEW_ARTIFACT}`: "
        f"la revisión de borrador se SUMA al dictamen de resultado, no lo "
        f"sustituye. La celda «Artifact» dice {artifact!r}."
    )


def _assert_draft_review_in_does(row: dict[str, str], label: str) -> None:
    does = row.get("does", "")
    assert DRAFT_WORD.search(does), (
        f"{label}: el texto de la fila del contrato del rol reviewer no dice "
        f"que la revisión de BORRADOR es parte del rol: la celda «Does» dice "
        f"{does!r}."
    )
    assert REVIEW_WORD.search(does) and _near_chars(does, DRAFT_WORD, REVIEW_WORD, 200), (
        f"{label}: el texto de la fila del contrato del rol reviewer no une "
        "el borrador con su revisión: la celda «Does» dice " + repr(does) + "."
    )


def _assert_unapproved_draft_review(directive: str, label: str) -> None:
    assert DRAFT_WORD.search(directive), (
        f"{label}: la sección de directiva no nombra el BORRADOR revisado."
    )
    assert REVIEW_WORD.search(directive), (
        f"{label}: la sección de directiva no nombra la REVISIÓN."
    )
    assert _near_chars(directive, DRAFT_WORD, REVIEW_WORD, 300), (
        f"{label}: la sección de directiva no une el borrador con su revisión."
    )
    assert NOT_APPROVED.search(directive), (
        f"{label}: la sección de directiva no dice que el borrador revisado "
        "NO está aprobado (la revisión de borrador.no.aprobado es parte del "
        "encargo del rol; «no aprobado»: unapproved / not approved / no "
        "aprobado / sin aprobación)."
    )


def _assert_declaration(
    text: str, label: str, directive: str
) -> None:
    """Las tres declaraciones de PD-11 sobre una superficie de texto."""
    row = _contract_row(text, label)
    _assert_stages(row, label)
    _assert_artifacts(row, label)
    _assert_draft_review_in_does(row, label)
    _assert_unapproved_draft_review(directive, label)


# ---------------------------------------------------------------------------
# La copia descartable del repo (nunca el árbol de trabajo, nunca el HOME)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def disposable_repo(tmp_path_factory: pytest.TempPathFactory):
    """Copia descartable del repo + un HOME descartable.

    La generación se invoca SIEMPRE dentro de la copia: el árbol de trabajo no
    se regenera nunca y el HOME real no se toca nunca.
    """
    base = tmp_path_factory.mktemp("cdad-006-006-u4")
    product = base / "product"
    shutil.copytree(REPO, product, symlinks=True, ignore=_ignore)
    home = base / "home"
    home.mkdir()
    yield product, home
    shutil.rmtree(base, ignore_errors=True)


def _subprocess_env(home: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["XDG_CONFIG_HOME"] = str(home / ".config")
    return env


def _run_staging(product: Path, home: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", "staging"],
        cwd=str(product),
        env=_subprocess_env(home),
        text=True,
        capture_output=True,
        check=False,
    )


def _staging_digests(product: Path, home: Path) -> dict[str, str]:
    """Una corrida de `make staging` en la copia + el sha256 de los cuatro
    agentes del reviewer."""
    result = _run_staging(product, home)
    assert result.returncode == 0, (
        "`make staging` falló en la copia descartable (rc="
        f"{result.returncode}):\n{result.stdout}\n{result.stderr}"
    )
    staging = product / "build" / "staging"
    digests: dict[str, str] = {}
    for relpath in STAGED_AGENTS:
        path = staging / relpath
        assert path.is_file(), (
            f"`make staging` no publicó el agente declarado {relpath} en la "
            "copia descartable."
        )
        digests[relpath] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


# ---------------------------------------------------------------------------
# PD-11 — la FUENTE editable del rol
# ---------------------------------------------------------------------------


def test_pd11_role_source_contract_row_declares_stages_2_and_4() -> None:
    """PD-11: la fila del contrato del rol reviewer declara las etapas 2 y 4.

    O-S1: la celda «Stages» de la fila nombra la ETAPA 2 (la revisión del
    borrador) y sigue nombrando la ETAPA 4 (la revisión del resultado): el rol
    cubre las dos. Se acepta el número (la convención del repo) o un nombre
    equivalente de la etapa.
    """
    text = _load(ROLE_SOURCE, "PD-11 (O-S1)")
    row = _contract_row(text, "PD-11 (O-S1): sources/roles/reviewer.md")
    _assert_stages(row, "PD-11 (O-S1): sources/roles/reviewer.md")


def test_pd11_role_source_contract_row_declares_the_plan_review_artifact() -> None:
    """PD-11: la fila nombra `plan-review.md` además de `review.md`.

    O-S2: la celda «Artifact» nombra el artefacto de la revisión de borrador
    (`plan-review.md`) Y el vigente (`review.md`): el dictamen de borrador se
    SUMA al dictamen de resultado, no lo sustituye.
    """
    text = _load(ROLE_SOURCE, "PD-11 (O-S2)")
    row = _contract_row(text, "PD-11 (O-S2): sources/roles/reviewer.md")
    _assert_artifacts(row, "PD-11 (O-S2): sources/roles/reviewer.md")


def test_pd11_role_source_contract_row_says_the_draft_review_is_part_of_the_role() -> None:
    """PD-11: el texto de la fila dice que la revisión de borrador es parte del
    rol.

    O-S3: la celda «Does» nombra el borrador y su revisión (por vecindad: el
    wrapping de la tabla no rompe la pareja).
    """
    text = _load(ROLE_SOURCE, "PD-11 (O-S3)")
    row = _contract_row(text, "PD-11 (O-S3): sources/roles/reviewer.md")
    _assert_draft_review_in_does(row, "PD-11 (O-S3): sources/roles/reviewer.md")


def test_pd11_role_source_directive_names_the_review_of_an_unapproved_draft() -> None:
    """PD-11: la sección de directiva nombra la revisión de borrador NO
    aprobado.

    O-S4: la sección de directiva de la fuente dice que el encargo del rol
    incluye la revisión de un borrador que NO está aprobado (la etapa 2): el
    objeto, la revisión y su carácter no aprobado, unidos por vecindad.
    """
    text = _load(ROLE_SOURCE, "PD-11 (O-S4)")
    directive = _source_directive(text, "PD-11 (O-S4): sources/roles/reviewer.md")
    _assert_unapproved_draft_review(
        directive, "PD-11 (O-S4): sources/roles/reviewer.md"
    )


# ---------------------------------------------------------------------------
# PD-11 — los CUATRO agentes (generados y promovidos)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("relpath", STAGED_AGENTS)
def test_pd11_generated_reviewer_agents_carry_the_declaration(
    disposable_repo, relpath: str
) -> None:
    """PD-11: los cuatro agentes GENERADOS lo contienen tras la generación.

    O-A1: el generador se invoca como PROCESO en la COPIA DESCARTABLE del
    repo (`make staging`, nunca el árbol de trabajo ni el HOME) y los cuatro
    agentes del reviewer que publica llevan las tres declaraciones de PD-11:
    la etapa 2 en «Stages», `plan-review.md` junto a `review.md` en
    «Artifact» y la revisión de borrador no aprobado en la directiva.
    """
    product, home = disposable_repo
    _staging_digests(product, home)
    path = product / "build" / "staging" / relpath
    text = _load(path, f"PD-11 (O-A1): agente generado {relpath}")
    label = f"PD-11 (O-A1): agente generado {relpath}"
    _assert_declaration(text, label, _agent_directive(text, label))


@pytest.mark.parametrize("relpath", PROMOTED_AGENTS)
def test_pd11_promoted_reviewer_agents_carry_the_declaration(relpath: str) -> None:
    """PD-11: los cuatro agentes PROMOVIDOS en el repo lo contienen.

    O-A2: los cuatro agentes del reviewer del repo —salidas declaradas de
    `scripts/cdad-generate.py`, promovidas por `make agents`— llevan las
    tres declaraciones de PD-11. Se leen; no se editan a mano.
    """
    path = REPO / relpath
    text = _load(path, f"PD-11 (O-A2): agente promovido {relpath}")
    label = f"PD-11 (O-A2): agente promovido {relpath}"
    _assert_declaration(text, label, _agent_directive(text, label))


# ---------------------------------------------------------------------------
# PD-11 / V-2 — el control de determinismo
# ---------------------------------------------------------------------------


def test_pd11_make_staging_is_deterministic_across_two_runs(disposable_repo) -> None:
    """PD-11 / V-2: `make staging` es determinista (dos corridas, mismos bytes).

    CONTROL (V-2): verde con el producto en vigor; debe seguir verde después
    (la fuente del rol cambia, el generador no). Comparación byte a byte de
    los cuatro agentes del reviewer entre dos corridas, en la copia
    descartable.
    """
    product, home = disposable_repo
    first = _staging_digests(product, home)
    second = _staging_digests(product, home)
    assert first == second, (
        "PD-11/V-2: `make staging` no es determinista: dos corridas sobre las "
        "mismas fuentes produjeron bytes distintos.\n"
        f"primera: {first}\nsegunda: {second}"
    )
