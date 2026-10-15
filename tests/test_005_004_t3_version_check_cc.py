"""RED — 005-004-claude-code-roles, T3: pata Claude Code del chequeo de version.

Contrato: `docs/specs/005-004-claude-code-roles/spec.md` (sha256 79d57e0a…),
postcondiciones PD-3 (a)-(d) con AC-3 y las invariantes INV-3, INV-4, INV-7.

Metodo (regla del paquete): el oraculo es el comprobador **como programa**, no su
codigo. Este archivo invoca `cdad-version-check.py` como subproceso sobre
*fixtures de raices de instalacion* (HOME aislado + copia del comprobador dentro
del layout de una raiz de instalacion) y solo lee su salida observable y su `rc`.

Mapa test -> afirmacion del contrato:
  test_pd3_cc_leg_reports_version_when_coherent        -> PD-3(a)(i) / AC-3
  test_pd3_cc_leg_participates_in_verdict_drift        -> PD-3(a)(c) / AC-3 / INV-7
  test_pd3_no_cc_installation_declares_absence_...     -> PD-3(b) / INV-4 (item 2)
  test_pd3_missing_cc_marker_is_unknown_with_cause     -> PD-3(d) / INV-3 / INV-7
  test_pd3_existing_verdicts_unchanged_without_cc[...] -> PD-3(b) / INV-4 (item 4)
  test_pd3_checkout_without_marker_stays_unknown_f2    -> PD-3(c) / INV-4 (F2)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "skills" / "cdad-cycle" / "scripts" / "cdad-version-check.py"

# Versiones sinteticas de fixture: opacas, distintas entre si y sin subcadenas
# que se confundan con una declaracion de ausencia.
OC_VERSION = "a1a1a1a1"
CC_VERSION = "b2b2b2b2"
OTHER_VERSION = "c3c3c3c3"

# Marcadores de "unknown con causa" / ausencia declarada (no un valor fabricado).
ABSENCE = re.compile(
    r"(?i)no version\.txt|not found|unknown|absent|missing|not detected"
    r"|no installation|unavailable|no marker|not present"
)


# --------------------------------------------------------------------------- #
# Fixtures de raices de instalacion (sin tocar HOME real ni el repo)
# --------------------------------------------------------------------------- #
def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _opencode_root(base: Path, *, version: str | None) -> Path:
    """Raiz de instalacion con el layout de agentes de OpenCode.

    `version=None` deja la raiz **sin** marcador (`<root>/version.txt`).
    """
    root = base / "opencode-install"
    (root / ".config" / "opencode" / "agents").mkdir(parents=True, exist_ok=True)
    if version is not None:
        _write(root / "version.txt", version + "\n")
    return root


def _checker_in_root(root: Path) -> Path:
    """Copia el comprobador dentro del layout de instalacion de una raiz.

    El arbol donde vive el comprobador define su propia pata "CLI": la raiz es
    el directorio que contiene `.config/opencode/skills/...`.
    """
    dest = (
        root / ".config" / "opencode" / "skills" / "cdad-cycle" / "scripts"
        / "cdad-version-check.py"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(CHECKER, dest)
    return dest


def _project(base: Path, *, source_dir: Path | None, source_version: str) -> Path:
    """Proyecto con (o sin) el manifiesto derivado de agentes.

    `source_dir=None` produce un proyecto sin derivados registrados.
    """
    proj = base / "project"
    proj.mkdir(parents=True, exist_ok=True)
    if source_dir is not None:
        _write(
            proj / ".opencode" / "agents" / ".cdad-derived.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "source_version": source_version,
                    "source_dir": str(source_dir),
                    "agents": {},
                }
            ),
        )
    return proj


def _cc_home(base: Path, *, version: str | None) -> Path:
    """HOME de fixture con una instalacion de Claude Code.

    Detectable = existe el directorio global de agentes CC del runtime
    (`<home>/.claude/agents`). El marcador de version de esa raiz es
    `<home>/version.txt` (y, por el patron "junto a los agentes", tambien
    `<home>/.claude/agents/version.txt`); `version=None` lo omite.
    """
    home = base / "home"
    (home / ".claude" / "agents").mkdir(parents=True, exist_ok=True)
    _write(home / ".claude" / "agents" / "cdad-implementer.md", "# fixture agent\n")
    _write(home / ".claude" / "agents" / "cdad-test-writer.md", "# fixture agent\n")
    if version is not None:
        _write(home / "version.txt", version + "\n")
        _write(home / ".claude" / "agents" / "version.txt", version + "\n")
    return home


def _bare_home(base: Path) -> Path:
    """HOME de fixture **sin** instalacion de Claude Code detectable."""
    home = base / "home"
    home.mkdir(parents=True, exist_ok=True)
    return home


def _run(checker: Path, *, project: Path, home: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("CDAD_")}
    env["HOME"] = str(home)
    env.pop("XDG_CONFIG_HOME", None)
    return subprocess.run(
        [sys.executable, str(checker), "--project-root", str(project)],
        capture_output=True,
        text=True,
        env=env,
    )


# --------------------------------------------------------------------------- #
# Lectura de la salida observable del programa
# --------------------------------------------------------------------------- #
def _leg(output: str, label: str) -> str | None:
    """Valor declarado por una pata existente (project / agents / CLI)."""
    m = re.search(rf"(?im)^\s*{label}\s*:\s*(.+?)\s*$", output)
    return m.group(1) if m else None


def _verdict(output: str) -> str | None:
    m = re.search(r"(?im)^\s*verdict:\s*(\S+)", output)
    return m.group(1) if m else None


def _cc_report(output: str) -> str | None:
    """Valor declarado para la pata Claude Code, o None si no se declara.

    Acepta la etiqueta de la pata con cualquier forma razonable
    (`claude-code:`, `Claude Code:`, `cc:`) o embebida en otra linea.
    """
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower().startswith(("cdad version check", "verdict")):
            continue
        m = re.match(r'(?i)^\s*(?:claude(?:[\s\-_]*code)?|cc)\s*[:=]\s*(.+?)\s*$', line)
        if m:
            return m.group(1)
    for line in output.splitlines():
        m = re.search(r'(?i)\bclaude(?:[\s\-_]*code)?\s*[:=]\s*([^\s,;)\]]+)', line)
        if m:
            return m.group(1)
    return None


def _is_absence(value: str) -> bool:
    return bool(ABSENCE.search(value))


# --------------------------------------------------------------------------- #
# PD-3(a)(i) — la pata CC informa la version de una instalacion detectable
# --------------------------------------------------------------------------- #
def test_pd3_cc_leg_reports_version_when_coherent(tmp_path: Path) -> None:
    """PD-3(a)(i) / AC-3: con una instalacion CC detectable cuyos valores son
    coherentes, el comprobador informa la version del lado CC y el veredicto
    sigue siendo COHERENT (rc 0)."""
    root = _opencode_root(tmp_path, version=OC_VERSION)
    checker = _checker_in_root(root)
    proj = _project(
        tmp_path, source_dir=root / ".config" / "opencode" / "agents",
        source_version=OC_VERSION,
    )
    home = _cc_home(tmp_path, version=OC_VERSION)

    result = _run(checker, project=proj, home=home)

    assert _leg(result.stdout, "project") == OC_VERSION, result.stdout
    assert _leg(result.stdout, "agents") == OC_VERSION, result.stdout
    assert _leg(result.stdout, "CLI") == OC_VERSION, result.stdout
    cc = _cc_report(result.stdout)
    assert cc is not None, (
        "PD-3(a)/AC-3: con una instalacion de Claude Code detectable el "
        f"comprobador no informa la version de esa pata:\n{result.stdout}"
    )
    assert OC_VERSION in cc, (
        "PD-3(a)/AC-3: la pata CC no informa la version de su raiz de "
        f"instalacion (esperado {OC_VERSION!r}, reportado {cc!r})"
    )
    assert _verdict(result.stdout) == "COHERENT", result.stdout
    assert result.returncode == 0, result.stdout


# --------------------------------------------------------------------------- #
# PD-3(a)(c) — la pata CC participa del veredicto sin cruzar la frontera
# --------------------------------------------------------------------------- #
def test_pd3_cc_leg_participates_in_verdict_drift(tmp_path: Path) -> None:
    """PD-3(a)(c) / AC-3 / INV-7: con una instalacion CC detectable en OTRA raiz
    (version distinta de la del lado OpenCode), la pata CC participa y el
    veredicto pasa a DRIFT (rc 1); la pata no presta la version de la otra
    instalacion (no cruza la frontera)."""
    root = _opencode_root(tmp_path, version=OC_VERSION)
    checker = _checker_in_root(root)
    proj = _project(
        tmp_path, source_dir=root / ".config" / "opencode" / "agents",
        source_version=OC_VERSION,
    )
    home = _cc_home(tmp_path, version=CC_VERSION)

    result = _run(checker, project=proj, home=home)

    # Control de la fixture: el lado OpenCode es coherente por si mismo.
    assert _leg(result.stdout, "project") == OC_VERSION, result.stdout
    assert _leg(result.stdout, "agents") == OC_VERSION, result.stdout
    assert _leg(result.stdout, "CLI") == OC_VERSION, result.stdout

    cc = _cc_report(result.stdout)
    assert cc is not None, (
        "PD-3(a)/AC-3: con una instalacion de Claude Code detectable el "
        f"comprobador no informa la version de esa pata:\n{result.stdout}"
    )
    assert CC_VERSION in cc, (
        "PD-3(a)/AC-3/INV-7: la pata CC no informa la version de SU raiz de "
        f"instalacion (esperado {CC_VERSION!r}, reportado {cc!r})"
    )
    assert OC_VERSION not in cc, (
        "PD-3(c)/INV-7: la pata CC presto la version de la otra instalacion "
        f"({OC_VERSION!r}) en lugar de la de su raiz:\n{result.stdout}"
    )
    assert _verdict(result.stdout) == "DRIFT", (
        "PD-3(a)/AC-3: con una instalacion CC detectable de version distinta la "
        f"pata no participa del veredicto (esperado DRIFT):\n{result.stdout}"
    )
    assert result.returncode == 1, result.stdout


# --------------------------------------------------------------------------- #
# PD-3(b) — sin instalacion CC detectable: veredicto/rc de hoy + ausencia
# --------------------------------------------------------------------------- #
def test_pd3_no_cc_installation_declares_absence_and_keeps_verdict(tmp_path: Path) -> None:
    """PD-3(b) / INV-4 (item 2): SIN instalacion de Claude Code detectable, el
    veredicto y el `rc` son IDENTICOS a los de hoy (COHERENT / 0) y aparece una
    linea declarada de ausencia de la pata."""
    root = _opencode_root(tmp_path, version=OC_VERSION)
    checker = _checker_in_root(root)
    proj = _project(
        tmp_path, source_dir=root / ".config" / "opencode" / "agents",
        source_version=OC_VERSION,
    )
    home = _bare_home(tmp_path)  # sin .claude/agents

    result = _run(checker, project=proj, home=home)

    assert _verdict(result.stdout) == "COHERENT", result.stdout
    assert result.returncode == 0, result.stdout
    cc = _cc_report(result.stdout)
    assert cc is not None, (
        "PD-3(b)/INV-4: sin instalacion CC detectable no aparece la linea "
        f"declarada de ausencia de la pata:\n{result.stdout}"
    )
    assert _is_absence(cc), (
        "PD-3(b): la linea de la pata CC sin instalacion detectable no declara "
        f"la ausencia con causa (reportado {cc!r})"
    )


# --------------------------------------------------------------------------- #
# PD-3(d) — marcador faltante: unknown con causa, nunca 0 ni prestada
# --------------------------------------------------------------------------- #
def test_pd3_missing_cc_marker_is_unknown_with_cause_not_borrowed(tmp_path: Path) -> None:
    """PD-3(d) / INV-3 / INV-7: una instalacion CC detectable **sin** marcador de
    version produce `unknown` CON CAUSA, nunca `0` ni la version prestada del
    manifiesto derivado de OpenCode."""
    root = _opencode_root(tmp_path, version=OC_VERSION)
    checker = _checker_in_root(root)
    proj = _project(
        tmp_path, source_dir=root / ".config" / "opencode" / "agents",
        source_version=OC_VERSION,
    )
    home = _cc_home(tmp_path, version=None)  # agentes CC presentes, sin marcador

    result = _run(checker, project=proj, home=home)

    cc = _cc_report(result.stdout)
    assert cc is not None, (
        "PD-3(d)/INV-3: con agentes CC detectables y marcador faltante el "
        f"comprobador no declara la pata CC:\n{result.stdout}"
    )
    assert _is_absence(cc), (
        "PD-3(d)/INV-3: un marcador faltante no produce `unknown` con causa "
        f"(reportado {cc!r})"
    )
    assert OC_VERSION not in cc, (
        "PD-3(d)/INV-7: la pata CC infirio su version leyendo el manifiesto "
        f"derivado de OpenCode ({OC_VERSION!r}) en lugar de declarar la causa "
        f"({cc!r})"
    )
    assert not re.fullmatch(r"0(?:\.0+)?", cc.strip()), (
        f"PD-3(d)/INV-3: la pata CC reporto 0 como version ({cc!r})"
    )


# --------------------------------------------------------------------------- #
# PD-3(b) — los cuatro veredictos/rc existentes no cambian sin CC
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("case", "expected_verdict", "expected_rc"),
    [
        ("drift", "DRIFT", 1),
        ("unknown", "UNKNOWN", 3),
        ("no-project-agents", "NO-PROJECT-AGENTS", 4),
    ],
)
def test_pd3_existing_verdicts_unchanged_without_cc(
    tmp_path: Path, case: str, expected_verdict: str, expected_rc: int
) -> None:
    """PD-3(b) / INV-4 (item 4): sin instalacion CC detectable, los veredictos y
    `rc` existentes siguen comportandose como hoy, con la linea de ausencia de la
    pata declarada y sin alterar el veredicto (el caso COHERENT/0 esta cubierto
    por `test_pd3_no_cc_installation_declares_absence_and_keeps_verdict`)."""
    if case == "no-project-agents":
        root = _opencode_root(tmp_path, version=None)
        proj = _project(tmp_path, source_dir=None, source_version=OC_VERSION)
    elif case == "unknown":
        root = _opencode_root(tmp_path, version=None)
        proj = _project(
            tmp_path, source_dir=root / ".config" / "opencode" / "agents",
            source_version=OC_VERSION,
        )
    elif case == "drift":
        root = _opencode_root(tmp_path, version=OTHER_VERSION)
        proj = _project(
            tmp_path, source_dir=root / ".config" / "opencode" / "agents",
            source_version=OC_VERSION,
        )
    else:  # pragma: no cover - parametrizacion cerrada
        raise AssertionError(f"caso no declarado: {case}")

    checker = _checker_in_root(root)
    home = _bare_home(tmp_path)

    result = _run(checker, project=proj, home=home)

    assert _verdict(result.stdout) == expected_verdict, result.stdout
    assert result.returncode == expected_rc, result.stdout
    cc = _cc_report(result.stdout)
    assert cc is not None, (
        "PD-3(b)/INV-4: sin instalacion CC detectable no aparece la linea "
        f"declarada de ausencia de la pata (caso {case}):\n{result.stdout}"
    )
    assert _is_absence(cc), (
        f"PD-3(b): la linea de la pata CC no declara la ausencia (caso {case}, "
        f"reportado {cc!r})"
    )


# --------------------------------------------------------------------------- #
# PD-3(c) — F2: checkout sin marcador sigue siendo UNKNOWN
# --------------------------------------------------------------------------- #
def test_pd3_checkout_without_marker_stays_unknown_f2(tmp_path: Path) -> None:
    """PD-3(c) / INV-4 (F2): una invocacion desde un checkout sin marcador sigue
    siendo UNKNOWN (rc 3) — el comprobador del repo, sin marcador en su arbol, no
    adopta una version ajena — y declara la ausencia de la pata CC."""
    root = _opencode_root(tmp_path, version=OC_VERSION)
    proj = _project(
        tmp_path, source_dir=root / ".config" / "opencode" / "agents",
        source_version=OC_VERSION,
    )
    home = _bare_home(tmp_path)

    result = _run(CHECKER, project=proj, home=home)

    assert _leg(result.stdout, "project") == OC_VERSION, result.stdout
    assert _leg(result.stdout, "agents") == OC_VERSION, result.stdout
    assert _leg(result.stdout, "CLI") == "(no version.txt found)", result.stdout
    assert _verdict(result.stdout) == "UNKNOWN", result.stdout
    assert result.returncode == 3, result.stdout
    cc = _cc_report(result.stdout)
    assert cc is not None, (
        "PD-3(b)/INV-4: sin instalacion CC detectable no aparece la linea "
        f"declarada de ausencia de la pata:\n{result.stdout}"
    )
    assert _is_absence(cc), (
        f"PD-3(b): la linea de la pata CC no declara la ausencia (reportado {cc!r})"
    )
