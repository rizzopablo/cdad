#!/usr/bin/env python3
"""T2 RED — generador de activación por proyecto `scripts/cdad-activate.py`.

Contrato: docs/specs/003-006-runtime-adoption/spec.md §2.2 (P2, P3, P5 mitad
unidad) + docs/specs/003-006-runtime-adoption/t2-contract-note.md.

Cada test construye una raíz adoptada SINTÉTICA en tmpdir (con
`.cdad-install-manifest.json` con sha256 correctos) y un proyecto R temporal,
invocando el CLI como subproceso con HOME apuntando a otro tmpdir vacío para
detectar escrituras bajo HOME. Nunca lee implementación: los asserts son sobre
comportamiento observable (rc, bytes, enlaces, ausencia de archivos).

Mapa test ↔ postcondición:
- test_p2_deterministic_two_runs_identical ....... P2 (nota §Garantías)
- test_p5_hook_rewrite_no_tilde_no_settings ...... P5 + nota §Salidas claude-code
- test_p2_outputs_links_and_opencode_jsonc ....... nota §Salidas (P3 contexto)
- test_p3_activation_registry .................... nota §Salidas registro
- test_r4_identity_manifest_sha .................. nota §Identidad (R-4)
- test_r5_no_clobber_conflict .................... nota §No-clobber (R-5)
- test_r5_repoint_replaces_own_and_prunes ........ nota §No-clobber (R-5)
- test_dry_run_writes_nothing .................... nota §Garantías --dry-run
- test_runtime_filter ............................ nota §Entrada --runtime
- test_p3_zero_home_writes ....................... P3/I1
- test_p3_gitignore_covers_runtime_dirs .......... P3 (git check-ignore real)

RED review-fix T2 (review-t2-decision.md):
- test_b1_symlink_component_outside_rejected ..... B-1 + I1/P3 (escritura contenida en R)
- test_b1_prune_external_skills_symlink .......... B-1 poda (nunca borra fuera de R)
- test_o4_roots_relative_and_symlink_equivalent .. O-4 + P2 (raíces resueltas a realpath)

RED review-fix T4 RU-1 (t4-ru1-decision.md):
- test_t4_ru1_hook_lines_exact_command_format .... RU-1 + P5 (formato exacto del hook:
  `command: CDAD_PACKET_CLI=<A>/…/cdad_packet.py <A>/…/path-guard.sh <rol>`)
- test_t4_ru1_no_command_depends_on_home ......... RU-1 + P5 (ningún command: contiene
  `~`, `$HOME` ni el HOME de la prueba; toda línea fija CDAD_PACKET_CLI a A)

AJUSTE DECLARADO (autorizado por el orquestador): la aserción exacta del hook en
test_p5_hook_rewrite_no_tilde_no_settings contradice el formato RU-1 (la línea
ya no empieza con `command: <A>/…path-guard.sh` sino con
`command: CDAD_PACKET_CLI=<A>/…cdad_packet.py`); se actualiza al formato RU-1.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVATE = REPO_ROOT / "scripts" / "cdad-activate.py"

SKILLS = ("cdad-cycle", "cdad-epic")
AGENTS = ("cdad-architect", "cdad-implementer")
ROLE = "implementer"

AGENT_TEMPLATE = """---
name: {name}
description: synthetic agent for activation tests
hooks:
  PreToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: ~/.claude/cdad-scripts/path-guard.sh {role}
---
body of {name}
"""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_adopted_root(
    base: Path,
    skills=SKILLS,
    agents=AGENTS,
    role: str = ROLE,
) -> Path:
    """Crea una raíz adoptada sintética A con manifest de sha256 correctos."""
    a = base / "A"
    files: dict[str, bytes] = {}
    for s in skills:
        files[f".config/opencode/skills/{s}/SKILL.md"] = f"# {s} (opencode)\n".encode()
        files[f".claude/skills/{s}/SKILL.md"] = f"# {s} (claude)\n".encode()
        files[f".agents/skills/{s}/SKILL.md"] = f"# {s} (codex)\n".encode()
    for n in agents:
        files[f".claude/agents/{n}.md"] = AGENT_TEMPLATE.format(name=n, role=role).encode()
    files[".claude/cdad-scripts/path-guard.sh"] = b"#!/bin/sh\nexit 0\n"

    for rel, data in files.items():
        p = a / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    artifacts = {
        rel: {"sha256": _sha256_bytes(data), "source": f"sources/{rel}"}
        for rel, data in files.items()
    }
    manifest = {
        "manifest_version": 1,
        "artifacts": artifacts,
        "conflicts": [],
        "installer": "install.sh (synthetic)",
        "pending_removal": [],
        "profile": "synthetic",
        "runtime": "opencode",
        "stack": "generic",
    }
    (a / ".cdad-install-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return a


def run_activate(project_root, adopted_root, extra=(), home=None, cwd=None):
    """Invoca el CLI como subproceso (foreground, stdin cerrado).

    cwd=None usa la raíz del repo; con cwd explícito se pueden probar
    ortografías relativas de --project-root/--adopted-root (O-4).
    """
    env = dict(os.environ)
    if home is not None:
        env["HOME"] = str(home)
    return subprocess.run(
        [
            sys.executable,
            str(ACTIVATE),
            "--project-root",
            str(project_root),
            "--adopted-root",
            str(adopted_root),
            *(str(x) for x in extra),
        ],
        cwd=str(cwd) if cwd is not None else str(REPO_ROOT),
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )


def snapshot(root: Path) -> dict:
    """Mapa relpath → (tipo, contenido|destino) de todo el árbol."""
    out: dict = {}
    for p in sorted(root.rglob("*")):
        rel = str(p.relative_to(root))
        if p.is_symlink():
            out[rel] = ("link", os.readlink(p))
        elif p.is_file():
            out[rel] = ("file", p.read_bytes())
        elif p.is_dir():
            out[rel] = ("dir", None)
    return out


@pytest.fixture
def workspace(tmp_path):
    """A sintética + R vacío + HOME vacío, todo bajo tmp_path."""
    a = make_adopted_root(tmp_path)
    r = tmp_path / "R"
    r.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    return a.resolve(), r, home


# ---------------------------------------------------------------- P2


def test_p2_deterministic_two_runs_identical(workspace):
    """P2: dos corridas con la misma entrada → bytes y enlaces idénticos.

    La segunda corrida sobre el mismo R encuentra destinos idénticos a lo que
    se emitiría → no es conflicto (nota §No-clobber) y rc=0.
    """
    a, r, home = workspace
    r2 = r.parent / "R2"
    r2.mkdir()

    first = run_activate(r, a, home=home)
    assert first.returncode == 0, (
        "1a corrida debe tener rc=0\n"
        f"stdout: {first.stdout}\nstderr: {first.stderr}"
    )
    second_same_r = run_activate(r, a, home=home)
    assert second_same_r.returncode == 0, (
        "re-corrida sobre destinos idénticos no es conflicto → rc=0\n"
        f"stdout: {second_same_r.stdout}\nstderr: {second_same_r.stderr}"
    )
    other = run_activate(r2, a, home=home)
    assert other.returncode == 0, (
        "corrida en R fresco debe tener rc=0\n"
        f"stdout: {other.stdout}\nstderr: {other.stderr}"
    )

    assert snapshot(r) == snapshot(r2), (
        "P2: dos corridas con la misma entrada producen árboles distintos"
    )


# ---------------------------------------------------------------- P5


def test_p5_hook_rewrite_no_tilde_no_settings(workspace):
    """P5 (mitad unidad): hook reescrito a <A>/..., ningún `command:` con
    `~/.claude`, y NO se emite `.claude/settings.json`.

    AJUSTE DECLARADO (RU-1, t4-ru1-decision.md, autorizado por el orquestador):
    la aserción exacta del hook se actualiza al formato RU-1 — la línea emitida
    fija CDAD_PACKET_CLI a la raíz adoptada antes del guard."""
    a, r, home = workspace
    res = run_activate(r, a, home=home)
    assert res.returncode == 0, (
        f"rc={res.returncode}\nstdout: {res.stdout}\nstderr: {res.stderr}"
    )

    claude_agents = r / ".claude" / "agents"
    emitted = sorted(claude_agents.glob("*.md"))
    assert [p.name for p in emitted] == [f"{n}.md" for n in AGENTS], (
        "deben emitirse los agentes de A/.claude/agents/"
    )
    for p in emitted:
        text = p.read_text()
        for line in text.splitlines():
            if "command:" in line:
                assert "~/.claude" not in line, (
                    f"P5: línea command: emitida contiene ~/.claude: {line!r}"
                )
                assert f"{a}/.claude/cdad-scripts/path-guard.sh" in line, (
                    f"P5: el hook debe resolver a <A>/.claude/cdad-scripts/…: {line!r}"
                )
        assert (
            f"command: CDAD_PACKET_CLI={a}/.claude/skills/cdad-cycle/scripts/cdad_packet.py"
            f" {a}/.claude/cdad-scripts/path-guard.sh {ROLE}"
        ) in text, (
            "P5/RU-1: el hook reescrito debe fijar CDAD_PACKET_CLI a la raíz "
            f"adoptada y apuntar el guard a A en {p.name}"
        )
    assert (a / ".claude" / "cdad-scripts" / "path-guard.sh").is_file(), (
        "el hook debe resolver a un archivo real en A"
    )
    assert not (r / ".claude" / "settings.json").exists(), (
        "P5: no se debe emitir .claude/settings.json"
    )


# ---------------------------------------------------------------- salidas


def test_p2_outputs_links_and_opencode_jsonc(workspace):
    """Salidas por runtime (nota §Salidas): enlaces de skills para claude-code
    y codex; opencode.jsonc con $schema y skills → A/.config/opencode/skills."""
    a, r, home = workspace
    res = run_activate(r, a, home=home)
    assert res.returncode == 0, (
        f"rc={res.returncode}\nstdout: {res.stdout}\nstderr: {res.stderr}"
    )

    for s in SKILLS:
        cc = r / ".claude" / "skills" / s
        cx = r / ".agents" / "skills" / s
        assert cc.is_symlink() and os.readlink(cc) == str(a / ".claude" / "skills" / s), (
            f"enlace claude-code {cc} → A/.claude/skills/{s}"
        )
        assert cx.is_symlink() and os.readlink(cx) == str(a / ".agents" / "skills" / s), (
            f"enlace codex {cx} → A/.agents/skills/{s}"
        )

    jsonc = r / ".opencode" / "opencode.jsonc"
    assert jsonc.is_file(), "debe emitirse .opencode/opencode.jsonc"
    # JSONC: permitir // comentarios — el contrato dice "JSON con"; verificamos
    # que el contenido sea JSON puro parseable.
    data = json.loads(jsonc.read_text())
    assert data.get("$schema") == "https://opencode.ai/config.json"
    assert data.get("skills") == [str(a / ".config" / "opencode" / "skills")]


def test_p3_activation_registry(workspace):
    """Registro `.cdad/activation.json`: adopted_root, sha del manifest de A y,
    por cada ruta emitida, su sha256 (archivo) o su destino (enlace)."""
    a, r, home = workspace
    res = run_activate(r, a, home=home)
    assert res.returncode == 0, (
        f"rc={res.returncode}\nstdout: {res.stdout}\nstderr: {res.stderr}"
    )

    reg_path = r / ".cdad" / "activation.json"
    assert reg_path.is_file(), "debe registrarse .cdad/activation.json"
    raw = reg_path.read_text()
    manifest_sha = _sha256_bytes((a / ".cdad-install-manifest.json").read_bytes())
    opencode_sha = _sha256_bytes((r / ".opencode" / "opencode.jsonc").read_bytes())

    data = json.loads(raw)
    assert data.get("adopted_root") == str(a), (
        f"adopted_root registrada debe ser {a}, hay {data.get('adopted_root')!r}"
    )
    assert manifest_sha in raw, "el sha256 del manifest de A debe estar registrado"
    assert opencode_sha in raw, (
        "el sha256 de cada ruta emitida (ej. opencode.jsonc) debe estar registrado"
    )
    assert str(a / ".claude" / "skills" / "cdad-cycle") in raw, (
        "el destino de cada enlace emitido debe estar registrado"
    )


# ---------------------------------------------------------------- R-4


def test_r4_identity_manifest_sha(workspace):
    """R-4: sha del manifest no coincide (o entrada faltante) → rc≠0 y nada
    escrito. Primero se prueba la corrida limpia (rc=0) para que RED no pase
    espuriamente con un error de CLI ausente."""
    a, r, home = workspace
    clean = run_activate(r, a, home=home)
    assert clean.returncode == 0, (
        "corrida limpia debe tener rc=0\n"
        f"stdout: {clean.stdout}\nstderr: {clean.stderr}"
    )

    # sha difiere
    a_bad = a.parent / "A-tampered"
    shutil.copytree(a, a_bad, symlinks=True)
    target = a_bad / ".config" / "opencode" / "skills" / "cdad-cycle" / "SKILL.md"
    target.write_text(target.read_text() + "\n# tampered\n")
    r_bad = a.parent / "R-bad"
    r_bad.mkdir()
    res = run_activate(r_bad, a_bad, home=home)
    assert res.returncode != 0, "sha divergente del manifest → debe fallar (rc≠0)"
    assert snapshot(r_bad) == {}, "R-4: con sha divergente no se escribe nada"

    # entrada faltante en el manifest
    a_missing = a.parent / "A-missing"
    shutil.copytree(a, a_missing, symlinks=True)
    manifest_path = a_missing / ".cdad-install-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["artifacts"].pop(".claude/cdad-scripts/path-guard.sh")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    r_missing = a.parent / "R-missing"
    r_missing.mkdir()
    res2 = run_activate(r_missing, a_missing, home=home)
    assert res2.returncode != 0, "entrada faltante del manifest → debe fallar (rc≠0)"
    assert snapshot(r_missing) == {}, "R-4: con entrada faltante no se escribe nada"


# ---------------------------------------------------------------- R-5


def test_r5_no_clobber_conflict(workspace):
    """R-5: destino ajeno divergente → rc≠0 nombrando la ruta, nada escrito
    (todo o nada). La corrida limpia de referencia se prueba primero (rc=0)."""
    a, r, home = workspace
    reference = a.parent / "R-ref"
    reference.mkdir()
    ok = run_activate(reference, a, home=home)
    assert ok.returncode == 0, (
        "corrida limpia de referencia debe tener rc=0\n"
        f"stdout: {ok.stdout}\nstderr: {ok.stderr}"
    )

    conflict = r / ".claude" / "agents"
    conflict.mkdir(parents=True)
    (conflict / "cdad-architect.md").write_text("# destino ajeno divergente\n")

    res = run_activate(r, a, home=home)
    assert res.returncode != 0, "destino ajeno divergente → debe fallar (rc≠0)"
    combined = res.stdout + res.stderr
    assert ".claude/agents/cdad-architect.md" in combined, (
        f"R-5: el mensaje debe nombrar la ruta en conflicto; salida: {combined!r}"
    )
    assert snapshot(r) == {
        ".claude": ("dir", None),
        ".claude/agents": ("dir", None),
        ".claude/agents/cdad-architect.md": ("file", b"# destino ajeno divergente\n"),
    }, "R-5: ante conflicto no se escribe nada (todo o nada)"


def test_r5_repoint_replaces_own_and_prunes(workspace):
    """R-5: re-apuntar a otra A reemplaza lo propio (destinos propios sin
    tocar se reemplazan) y quita las rutas propias que ya no se emiten."""
    a1, r, home = workspace
    a2 = make_adopted_root(r.parent / "a2-base", skills=("cdad-cycle",), agents=AGENTS)

    first = run_activate(r, a1, home=home)
    assert first.returncode == 0, (
        f"1a corrida (A1) debe tener rc=0\nstdout: {first.stdout}\nstderr: {first.stderr}"
    )
    assert (r / ".claude" / "skills" / "cdad-epic").is_symlink()

    second = run_activate(r, a2, home=home)
    assert second.returncode == 0, (
        "re-apuntar a A2 con destinos propios → rc=0\n"
        f"stdout: {second.stdout}\nstderr: {second.stderr}"
    )
    # propio reemplazado: opencode.jsonc ahora apunta a A2
    data = json.loads((r / ".opencode" / "opencode.jsonc").read_text())
    assert data.get("skills") == [str(a2 / ".config" / "opencode" / "skills")], (
        "los destinos propios se reemplazan al re-apuntar"
    )
    # propio podado: el skill ya no emitido por A2 desaparece
    assert not (r / ".claude" / "skills" / "cdad-epic").exists(), (
        "R-5: las rutas propias que ya no se emiten se quitan"
    )
    assert not (r / ".agents" / "skills" / "cdad-epic").exists()
    assert (r / ".claude" / "skills" / "cdad-cycle").is_symlink()
    reg = json.loads((r / ".cdad" / "activation.json").read_text())
    assert reg.get("adopted_root") == str(a2), "el registro queda apuntando a A2"


# ---------------------------------------------------------------- garantías


def test_dry_run_writes_nothing(workspace):
    """--dry-run: lista las rutas que escribiría y los conflictos; no escribe
    nada."""
    a, r, home = workspace
    before = snapshot(r)
    res = run_activate(r, a, extra=["--dry-run"], home=home)
    assert res.returncode == 0, (
        f"--dry-run debe tener rc=0\nstdout: {res.stdout}\nstderr: {res.stderr}"
    )
    listed = res.stdout + res.stderr
    assert ".opencode/opencode.jsonc" in listed, (
        "--dry-run debe listar las rutas que escribiría"
    )
    assert snapshot(r) == before, "--dry-run: no escribe nada"


def test_runtime_filter(workspace):
    """--runtime filtra: solo se emiten las salidas del runtime pedido."""
    a, r, home = workspace
    res = run_activate(r, a, extra=["--runtime", "opencode"], home=home)
    assert res.returncode == 0, (
        f"rc={res.returncode}\nstdout: {res.stdout}\nstderr: {res.stderr}"
    )
    assert (r / ".opencode" / "opencode.jsonc").is_file()
    assert not (r / ".claude").exists(), "--runtime opencode no emite .claude/"
    assert not (r / ".agents").exists(), "--runtime opencode no emite .agents/"

    r2 = r.parent / "R2"
    r2.mkdir()
    res2 = run_activate(
        r2, a, extra=["--runtime", "claude-code", "--runtime", "codex"], home=home
    )
    assert res2.returncode == 0, (
        f"rc={res2.returncode}\nstdout: {res2.stdout}\nstderr: {res2.stderr}"
    )
    assert (r2 / ".claude" / "agents" / "cdad-architect.md").is_file()
    assert (r2 / ".agents" / "skills" / "cdad-cycle").is_symlink()
    assert not (r2 / ".opencode").exists(), "--runtime sin opencode no emite .opencode/"


def test_p3_zero_home_writes(workspace):
    """P3/I1: cero escrituras en las configuraciones del HOME real — con HOME
    temporal vacío, la corrida no crea ni modifica nada bajo HOME."""
    a, r, home = workspace
    before = snapshot(home)
    res = run_activate(r, a, home=home)
    assert res.returncode == 0, (
        f"rc={res.returncode}\nstdout: {res.stdout}\nstderr: {res.stderr}"
    )
    assert snapshot(home) == before, (
        "P3: la activación no debe escribir nada bajo $HOME"
    )


def test_p3_gitignore_covers_runtime_dirs():
    """P3: el .gitignore REAL del repo ignora .opencode/, .claude/ y .agents/
    (y .cdad/), verificado con git check-ignore."""
    for d in (".opencode/", ".claude/", ".agents/", ".cdad/"):
        res = subprocess.run(
            ["git", "check-ignore", "-q", d],
            cwd=REPO_ROOT,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, (
            f"P3: git check-ignore debe ignorar {d} (rc={res.returncode})"
        )


# ------------------------------------------------- B-1 (review-t2-decision)


def _make_escape_case(tmp_path: Path, component: str):
    """Raíz adoptada sintética + R cuyo <component> es un symlink a un
    directorio EXTERNO a R (bajo tmp_path, nunca el HOME real)."""
    base = tmp_path / f"base-{component.strip('.')}"
    a = make_adopted_root(base)
    home = tmp_path / f"home-{component.strip('.')}"
    home.mkdir()
    ext = tmp_path / f"external-{component.strip('.')}"
    ext.mkdir()
    r = tmp_path / f"R-{component.strip('.')}"
    r.mkdir()
    os.symlink(ext, r / component)
    return a, home, ext, r


@pytest.mark.parametrize("component", [".claude", ".agents", ".opencode"])
def test_b1_symlink_component_outside_rejected(tmp_path, component):
    """B-1 (review-t2-decision) + I1/P3: si `R/<componente>` es un symlink que
    sale de --project-root, la activación debe rechazar antes de escribir:
    rc≠0, el mensaje nombra la ruta, y no se escribe nada NI dentro de R NI
    fuera de R (todo o nada, incluso con hoja inexistente / contenido vacío).
    """
    # Control: R sin symlink → la activación normal debe funcionar (rc=0),
    # así el RED no pasa ni falla espuriamente por un CLI roto.
    base_ctl = tmp_path / "base-control"
    a_ctl = make_adopted_root(base_ctl)
    home_ctl = tmp_path / "home-control"
    home_ctl.mkdir()
    r_ctl = tmp_path / "R-control"
    r_ctl.mkdir()
    ctl = run_activate(r_ctl, a_ctl, home=home_ctl)
    assert ctl.returncode == 0, (
        "control: activación sin symlinks debe tener rc=0\n"
        f"stdout: {ctl.stdout}\nstderr: {ctl.stderr}"
    )

    a, home, ext, r = _make_escape_case(tmp_path, component)
    before_r = snapshot(r)
    before_ext = snapshot(ext)

    res = run_activate(r, a, home=home)
    assert res.returncode != 0, (
        f"B-1: R/{component} es symlink que sale de --project-root → debe "
        f"rechazarse (rc≠0); hoy rc=0 y escribe a través del enlace.\n"
        f"stdout: {res.stdout}\nstderr: {res.stderr}"
    )
    combined = res.stdout + res.stderr
    assert component in combined, (
        f"B-1: el mensaje debe nombrar la ruta en conflicto ({component}); "
        f"salida: {combined!r}"
    )
    assert snapshot(r) == before_r, (
        f"B-1: ante escape de {component} no se escribe nada dentro de R "
        f"(todo o nada); árbol: {snapshot(r)}"
    )
    assert snapshot(ext) == before_ext, (
        f"B-1: ante escape de {component} no se escribe nada FUERA de R "
        f"(directorio externo {ext} intacto); árbol: {snapshot(ext)}"
    )


def test_b1_prune_external_skills_symlink(tmp_path):
    """B-1 poda (review-t2-decision): tras una activación válida, se reemplaza
    `R/.claude/skills` por un symlink externo que contiene un enlace con el
    mismo nombre que uno propio (mismo destino, hoja idéntica → no es conflicto
    R-5) → el repoint NO borra ni reapunta nada fuera de R: rc≠0 (o se omite),
    pero el directorio externo queda byte a byte intacto.
    """
    base1 = tmp_path / "base1"
    a1 = make_adopted_root(base1)
    # A2 emite un subconjunto: el repoint debe podar cdad-epic y repuntar cdad-cycle
    a2 = make_adopted_root(tmp_path / "base2", skills=("cdad-cycle",), agents=AGENTS)
    home = tmp_path / "home"
    home.mkdir()
    r = tmp_path / "R"
    r.mkdir()

    first = run_activate(r, a1, home=home)
    assert first.returncode == 0, (
        f"1a corrida (A1) debe tener rc=0\nstdout: {first.stdout}\nstderr: {first.stderr}"
    )

    # sustituir R/.claude/skills por symlink externo con enlace homónimo propio
    ext = tmp_path / "external-claude-skills"
    (ext / ".claude" / "skills").mkdir(parents=True)
    own_target = a1 / ".claude" / "skills" / "cdad-cycle"
    os.symlink(own_target, ext / ".claude" / "skills" / "cdad-cycle")
    skills_dir = r / ".claude" / "skills"
    shutil.rmtree(skills_dir)
    os.symlink(ext / ".claude" / "skills", skills_dir)

    before_ext = snapshot(ext)
    second = run_activate(r, a2, home=home)
    after_ext = snapshot(ext)

    assert after_ext == before_ext, (
        "B-1: el repoint NO debe borrar ni reapuntar nada fuera de R a través "
        f"del symlink .claude/skills; hoy la poda/escritura aterriza en {ext}. "
        f"rc={second.returncode}\nstdout: {second.stdout}\nstderr: {second.stderr}\n"
        f"externo antes: {before_ext}\nexterno después: {after_ext}"
    )
    if second.returncode != 0:
        combined = second.stdout + second.stderr
        assert ".claude" in combined, (
            f"B-1: ante rechazo, el mensaje debe nombrar la ruta involucrada; "
            f"salida: {combined!r}"
        )
    # "se omite" (rc=0 con externo intacto) es aceptable según el orquestador;
    # lo innegociable es que el directorio externo queda intacto (assert previo).


# ------------------------------------------------- O-4 (review-t2-decision)


def test_o4_roots_relative_and_symlink_equivalent(tmp_path):
    """O-4 (review-t2-decision) + P2: --project-root y --adopted-root se
    resuelven a realpath al validar argumentos: darlos como ruta relativa o a
    través de un symlink produce bytes idénticos (árbol completo, incluido el
    registro) a darlos absolutos.
    """
    base = tmp_path / "base"
    a_abs = make_adopted_root(base).resolve()
    home = tmp_path / "home"
    home.mkdir()

    # línea base: ortografía absoluta resuelta
    r_abs = tmp_path / "R-abs"
    r_abs.mkdir()
    ok = run_activate(r_abs, a_abs, home=home)
    assert ok.returncode == 0, (
        "control: corrida con raíces absolutas debe tener rc=0\n"
        f"stdout: {ok.stdout}\nstderr: {ok.stderr}"
    )
    baseline = snapshot(r_abs)
    assert baseline, "control: la corrida absoluta debe emitir algo"

    # ortografía relativa (respecto al cwd del subproceso)
    r_rel = tmp_path / "R-rel"
    r_rel.mkdir()
    res_rel = run_activate("R-rel", os.path.join("base", "A"), home=home, cwd=tmp_path)
    assert res_rel.returncode == 0, (
        "O-4: raíces relativas deben aceptarse (rc=0)\n"
        f"stdout: {res_rel.stdout}\nstderr: {res_rel.stderr}"
    )
    assert snapshot(r_rel) == baseline, (
        "O-4: ortografía RELATIVA de las raíces debe producir bytes idénticos "
        "a la ortografía absoluta (realpath en la validación de args)"
    )

    # ortografía vía symlink
    links = tmp_path / "links"
    links.mkdir()
    r_sym = tmp_path / "R-sym"
    r_sym.mkdir()
    os.symlink(r_sym, links / "R-link")
    os.symlink(a_abs, links / "A-link")
    res_sym = run_activate(links / "R-link", links / "A-link", home=home)
    assert res_sym.returncode == 0, (
        "O-4: raíces vía symlink deben aceptarse (rc=0)\n"
        f"stdout: {res_sym.stdout}\nstderr: {res_sym.stderr}"
    )
    assert snapshot(r_sym) == baseline, (
        "O-4: ortografía VÍA SYMLINK de las raíces debe producir bytes "
        "idénticos a la ortografía absoluta (realpath en la validación de args)"
    )


# ------------------------------------------------- T4 RU-1 (t4-ru1-decision)


def _emitted_command_lines(r: Path):
    """Todas las líneas `command:` emitidas en .claude/agents/*.md."""
    for p in sorted((r / ".claude" / "agents").glob("*.md")):
        for ln in p.read_text().splitlines():
            if "command:" in ln:
                yield p.name, ln


def test_t4_ru1_hook_lines_exact_command_format(workspace):
    """RU-1 (t4-ru1-decision.md, P5): cada línea `command:` emitida en
    .claude/agents/*.md es EXACTAMENTE
    `command: CDAD_PACKET_CLI=<A>/.claude/skills/cdad-cycle/scripts/cdad_packet.py
    <A>/.claude/cdad-scripts/path-guard.sh <rol>`
    con <A> resuelto a la raíz adoptada (el guard recibe el clasificador de A
    vía CDAD_PACKET_CLI y deja de resolverlo desde HOME)."""
    a, r, home = workspace
    res = run_activate(r, a, home=home)
    assert res.returncode == 0, (
        f"rc={res.returncode}\nstdout: {res.stdout}\nstderr: {res.stderr}"
    )

    expected = (
        f"command: CDAD_PACKET_CLI={a}/.claude/skills/cdad-cycle/scripts/cdad_packet.py"
        f" {a}/.claude/cdad-scripts/path-guard.sh {ROLE}"
    )
    lines = list(_emitted_command_lines(r))
    assert lines, "RU-1: los agentes emitidos deben contener al menos un hook command:"
    for name, ln in lines:
        # La indentación YAML del template no es parte del comando; la
        # aserción exacta es sobre la línea command: en sí (strip).
        cmd = ln.strip()
        assert cmd == expected, (
            "RU-1: la línea command: emitida debe fijar CDAD_PACKET_CLI a la "
            f"raíz adoptada y apuntar el guard a A.\n"
            f"esperado: {expected!r}\n"
            f"obtenido en {name}: {ln!r}"
        )


def test_t4_ru1_no_command_depends_on_home(workspace):
    """RU-1 (t4-ru1-decision.md, P5): ningún `command:` emitido depende de
    HOME — ninguna línea command: contiene `~`, `$HOME` ni la ruta del HOME
    de la prueba, y toda línea command: fija CDAD_PACKET_CLI apuntando a la
    raíz adoptada."""
    a, r, home = workspace
    res = run_activate(r, a, home=home)
    assert res.returncode == 0, (
        f"rc={res.returncode}\nstdout: {res.stdout}\nstderr: {res.stderr}"
    )

    lines = list(_emitted_command_lines(r))
    assert lines, "RU-1: los agentes emitidos deben contener al menos un hook command:"
    for name, ln in lines:
        assert "~" not in ln, f"RU-1: línea command: de {name} contiene '~': {ln!r}"
        assert "$HOME" not in ln, (
            f"RU-1: línea command: de {name} contiene '$HOME': {ln!r}"
        )
        assert str(home) not in ln, (
            f"RU-1: línea command: de {name} contiene el HOME de la prueba: {ln!r}"
        )
        assert (
            f"CDAD_PACKET_CLI={a}/.claude/skills/cdad-cycle/scripts/cdad_packet.py"
        ) in ln, (
            "RU-1: la línea command: no fija CDAD_PACKET_CLI a la raíz "
            f"adoptada ({name}): {ln!r}"
        )
