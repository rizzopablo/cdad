#!/usr/bin/env python3
"""004-002 T5 RED — Scopes derivados y mecanismos runtime (PD-7, PD-8).

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md
(PD-7, PD-8) + docs/specs/004-002-project-execution-bootstrap/plan.md
(decisiones de interfaz I9, I10 del orquestador; condición de aprobación C2).

Superficie observable bajo prueba (proyectos sintéticos en tempdirs;
ninguna escritura fuera de ellos):

  OpenCode (I9 / PD-7 / PD-8):
    CDAD_OPENCODE_AGENTS_DIR=<copia de agents/cdad-*.md> \
      python3 scripts/cdad_packet.py prepare --project-root <raíz> ...
    → publica .opencode/agents/cdad-*.md y .opencode/agents/.cdad-derived.json.
    Los mapas permission (read/grep/glob/edit) de CADA derivado se evalúan con
    el evaluador findLast EXISTENTE (tests/pd10_permission_semantics.py,
    reutilizado por import; no se escribe otro evaluador). W-2 (2026-10-01,
    t7-live-walk.md §3, sonda en vivo): en OpenCode grep/glob se median por
    el PATRÓN de búsqueda, no por la ruta — los derivados NO emiten entradas
    por ruta en `grep`/`glob` (no declaran una barrera inexistente);
    `read`/`edit` conservan sus mapas por ruta.

  Claude Code (I10 / C2 / PD-8):
    echo '<hook json>' | CDAD_PACKET_CLI=<repo>/scripts/cdad_packet.py \
      bash scripts/claude-code-path-guard.sh <rol>   # cwd = proyecto sintético
    JSON con la forma REAL de cada herramienta:
      Read/Edit/Write {"file_path"}; Grep/Glob {"pattern"[, "path"]}.
    La interfaz de invocación (rol como argumento) es la que ya declaran los
    hooks generados en agents/claude-code/cdad-*.md (salidas declaradas del
    generador, mismo precedente de lectura que pd10_permission_semantics.py).

Mapa test → postcondición:

  TestPd8I9Publication
    test_pd8_i9_prepare_publishes_local_opencode_agents      -> PD-8/I9 (publicación)
    test_pd8_i9_manifest_records_policy_and_agent_hashes     -> PD-8/I9 (manifest)
    test_pd8_i9_foreign_file_survives_publication            -> PD-8/I9 (ajenos)
    test_pd8_i9_derived_body_is_byte_identical_to_source     -> PD-8/I9 (byte a byte salvo la región de permisos: mapas + cabecera `permission`, F-R1/review-012; U6-7b/A-1 suma `write` a la región reemplazada)
  TestPd7I9DerivedMaps
    test_pd7_i9_test_writer_cdad_layout_maps                 -> PD-7/I9 (layout CDAD) + W-2 (grep/glob sin entradas por ruta)
    test_pd7_i9_maps_conventional_and_colocated_layouts      -> PD-7/I9 (convencional + co-ubicado) + W-2
    test_pd7_i9_maps_odoo_layout                             -> PD-7/I9 (Odoo) + W-2
    test_pd7_i9_policy_edit_deny_for_every_derived_role      -> PD-7 (exclusión de la política)
  TestPd8I9DerivedLifecycle
    test_pd8_i9_hand_modified_derived_fails_without_overwrite -> PD-8/I9 (derivado a mano)
    test_pd8_i9_reconciled_policy_regenerates_deriveds        -> PD-5/I9 (regeneración)
  TestPd8I10CcGuard
    test_pd8_i10_c2_guard_denies_read_of_implementation       -> PD-8/I10/C2 (Read)
    test_pd8_i10_c2_guard_allows_tests_paths_for_test_writer  -> PD-8/I10 (lado positivo)
    test_pd8_i10_c2_guard_denies_scoped_grep_glob_into_impl   -> PD-8/I10/C2 (Grep/Glob con path)
    test_pd8_i10_c2_guard_blocks_unscoped_grep_glob           -> PD-8/I10/C2 (sin path: acotar)
    test_pd8_i10_c2_guard_denies_implementer_edit_of_tests    -> PD-7/I10 (barrera implementer)
    test_pd8_i10_c2_guard_blocks_on_invalid_policy            -> PD-8/I10 (sin fallback)
    test_pd8_i10_c2_guard_blocks_when_cli_unfindable          -> PD-8/I10 (sin fallback)
    test_pd8_i10_c2_guard_legacy_smoke_without_policy         -> PD-8/I10 (legacy conservado)
    test_pd8_i10_guard_odoo_layout_controls                   -> PD-7/I10 (layout Odoo)

RED hoy (post T2–T4 GREEN): `prepare` no publica .opencode/agents/ (ni
manifest) y el guard no carga la política del proyecto ni media Grep/Glob;
cada aserción expresa la postcondición (AssertionError), no la mecánica.
Nota de trazabilidad: los tests no leen implementación; los únicos archivos
del árbol de producto leídos son las salidas declaradas del generador
(agents/cdad-*.md como fuente de la copia temporal, copiada sin inspección;
agents/claude-code/*.md solo para documentar la interfaz del guard).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tests.agent_frontmatter import permissions as v2_permissions

from test_004_002_t2_bootstrap import (
    POLICY_FILE,
    REPO_ROOT,
    SCRIPT,
    build_project,
    prepare_args,
    read_state,
    write_state,
)

# Evaluador único (findLast): reutilizado, no reimplementado (PD-10 precedent).
from pd10_permission_semantics import (  # noqa: E402
    frontmatter,
    perm_map,
    verdict,
)
from test_opencode_read_map_and_steps import glob_to_regex  # noqa: E402

GUARD = REPO_ROOT / "scripts" / "claude-code-path-guard.sh"
AGENTS_ENV = "CDAD_OPENCODE_AGENTS_DIR"
CLI_ENV = "CDAD_PACKET_CLI"
DERIVED_DIR = ".opencode/agents"
MANIFEST = ".cdad-derived.json"
POLICY_REL = "docs/cdad-policy.json"

TEST_WRITER = "cdad-test-writer.md"
IMPLEMENTER = "cdad-implementer.md"
TEST_WRITER_ODOO = "cdad-test-writer-odoo.md"
IMPLEMENTER_ODOO = "cdad-implementer-odoo.md"
READER = "cdad-reviewer.md"


# ---------------------------------------------------------------- layouts


def policy_doc(layout: str) -> dict:
    """Política válida de tres campos para cada layout (clasificación T1)."""
    path_policy = {
        "cdad": {
            "test_roots": ["tests"],
            "implementation_roots": ["agents", "skills", "scripts",
                                     "sources", "build"],
            "implementation_files": ["install.sh"],
            "documentation_roots": ["docs"],
            "colocated_test_roots": ["scripts", "agents"],
            "colocated_test_prefixes": ["test_"],
            "colocated_test_suffixes": ["_test.py"],
        },
        "conventional": {
            "test_roots": ["tests"],
            "implementation_roots": ["src", "lib"],
            "documentation_roots": ["docs"],
            "colocated_test_roots": ["src"],
            "colocated_test_prefixes": ["test_"],
            "colocated_test_suffixes": ["_test.py"],
        },
        "odoo": {
            "test_roots": ["addons/m/tests"],
            "implementation_roots": ["addons/m/models", "addons/m/views"],
            "documentation_roots": ["docs"],
            "colocated_test_prefixes": ["test_"],
            "colocated_test_suffixes": ["_test.py"],
        },
    }[layout]
    return {"schema_version": 1, "path_policy": path_policy,
            "temporary_roots": [".cdad/tmp"]}


LAYOUT_FILES = {
    "cdad": ("scripts/x.py", "scripts/test_h.py", "agents/y.md",
             "agents/test_y.md", "tests/test_a.py", "install.sh"),
    "conventional": ("src/app.py", "src/test_mod.py", "src/pkg/test_a.py",
                     "tests/test_a.py"),
    "odoo": ("addons/m/models/m.py", "addons/m/views/v.xml",
             "addons/m/tests/test_m.py", "addons/m/__manifest__.py"),
}


# ---------------------------------------------------------------- helpers


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def policy_sha(root: Path) -> str:
    return sha256_bytes((root / POLICY_FILE).read_bytes())


def derived_dir(root: Path) -> Path:
    return root / DERIVED_DIR


def published_derived(root: Path) -> dict[str, bytes]:
    base = derived_dir(root)
    if not base.is_dir():
        return {}
    return {p.name: p.read_bytes() for p in sorted(base.glob("cdad-*.md"))}


def require_derived(tc: unittest.TestCase, root: Path,
                    names: tuple[str, ...]) -> dict[str, str]:
    """PD-8/I9: exige que prepare haya publicado los derivados; si no, AssertionError."""
    pub = published_derived(root)
    missing = [n for n in names if n not in pub]
    tc.assertEqual(
        missing, [],
        msg=f"PD-8/I9: prepare no publica los agentes derivados en "
            f"{DERIVED_DIR}/; faltan {missing}; publicados: {sorted(pub)}")
    return {n: pub[n].decode("utf-8") for n in names}


def without_maps(agent_text: str) -> str:
    """Agente sin la REGIÓN de permisos del frontmatter: lo que PD-8/I9
    exige byte a byte igual al origen.

    La región propia de la derivación comprende únicamente
    read/grep/glob/edit; shell, `*` y el resto del documento permanecen
    bajo comparación byte a byte.

    La región comprende (i) las secciones de mapas
    read/grep/glob/edit (block o inline) y (ii) la CABECERA
    `permission:`, en ambas formas que declara el producto: escalar
    (`permission: allow`) o la línea `permission:` que abre un mapa. La
    cabecera se normaliza (enmenda el oráculo; F-R1 del review-012,
    decisión del orquestador del 2026-10-02): con `private_paths`, la
    derivación correcta REEMPLAZA la línea escalar `permission: allow` del
    origen (agents/cdad-orchestrator.md:4) por el bloque `permission:` con
    mapas — y hoy publica YAML inválido —, de modo que la comparación byte
    a byte debe tratar la cabecera como parte de la región de permisos y NO
    como una divergencia.

    No se elimina el bloque `permissions:` entero: solo se filtran entradas
    cuya acción sea propiedad de la derivación. Se conserva el cuerpo exacto."""
    import yaml

    fm = frontmatter(agent_text)
    body = agent_text[len(fm):]
    data = yaml.safe_load(fm[4:-4]) or {}
    owned = {"read", "grep", "glob", "edit"}
    if isinstance(data.get("permissions"), list):
        retained = [
            (entry.get("action"), entry.get("resource"), entry.get("effect"))
            for entry in data["permissions"]
            if entry.get("action") not in owned
        ]
        data.pop("permissions")
    else:
        legacy = data.pop("permission", None)
        retained = []
        if isinstance(legacy, dict):
            for action, rules in legacy.items():
                if action in owned:
                    continue
                canonical_action = "shell" if action == "bash" else action
                if isinstance(rules, dict):
                    retained.extend((canonical_action, resource, effect)
                                    for resource, effect in rules.items())
                else:
                    retained.append((canonical_action, "*", rules))
        elif legacy is not None:
            retained.append(("*", "*", legacy))
    return repr(data) + "\n" + repr(retained) + "\n" + body


def test_without_maps_retains_non_owned_permissions_and_full_body():
    """PC-2/invariant 1: only owned maps vary; shell/* and body remain exact."""
    from test_004_002_t5_runtime import without_maps

    original = (
        "---\npermissions:\n"
        "  - action: edit\n    resource: tests/**\n    effect: allow\n"
        '  - action: shell\n    resource: "*"\n    effect: allow\n'
        '  - action: "*"\n    resource: "*"\n    effect: allow\n'
        "---\nbody full\n"
    )
    owned_only_changed = original.replace("tests/**", "other/**")
    shell_changed = original.replace(
        'action: shell\n    resource: "*"\n    effect: allow',
        'action: shell\n    resource: "*"\n    effect: deny',
    )
    assert without_maps(original) == without_maps(owned_only_changed)
    assert without_maps(original) != without_maps(shell_changed)
    assert without_maps(original).endswith("body full\n")


def policy_path_probes(layout: str) -> tuple[str, ...]:
    """W-2: sondas de ruta de la política del layout — cada raíz declarada
    (implementación, tests, documentación, co-ubicados), el archivo exacto,
    y los archivos reales del fixture. Cualquier entrada por ruta que la
    clasificación emitiera en `grep`/`glob` matchea alguna de estas."""
    doc = policy_doc(layout)["path_policy"]
    probes: list[str] = []
    for key in ("implementation_roots", "test_roots", "documentation_roots",
                "colocated_test_roots"):
        for root in doc.get(key, []):
            probes.append(root)
            probes.append(f"{root}/w2_probe")
    probes += list(doc.get("implementation_files", []))
    probes += list(LAYOUT_FILES[layout])
    return tuple(probes)


def path_entry_rules(agent_text: str, tool: str,
                     path_probes: tuple[str, ...]) -> list[str]:
    """W-2 (t7-live-walk.md §3): en OpenCode los permisos de `grep`/`glob`
    se evalúan contra el PATRÓN de búsqueda, no contra la ruta — las
    entradas por ruta que los derivados emitieran serían inertes. Devuelve
    las reglas del mapa `tool` (grep/glob) cuyo patrón matchea alguna
    sonda de ruta (entradas por ruta), con el findLast único (pd10)."""
    return [
        pattern for pattern, _verb in perm_map(agent_text, tool)
        if any(re.fullmatch(glob_to_regex(pattern), probe)
               for probe in path_probes)
    ]


def assert_no_search_path_entries(
        tc: unittest.TestCase, pub: dict[str, str],
        path_probes: tuple[str, ...]) -> None:
    """W-2 (t7-live-walk.md §3): para CADA derivado publicado, los mapas
    `grep` y `glob` NO contienen entradas por ruta de la política (no
    declaran una barrera inexistente: OpenCode media grep/glob por el
    patrón de búsqueda). Las aserciones de `read`/`edit` no cambian."""
    for name, text in sorted(pub.items()):
        for tool in ("grep", "glob"):
            with tc.subTest(agent=name, tool=tool,
                            w2="sin-entradas-por-ruta"):
                flagged = path_entry_rules(text, tool, path_probes)
                tc.assertEqual(
                    flagged, [],
                    msg=f"W-2: el derivado {name} declara entradas por ruta "
                        f"en `{tool}` — en OpenCode ese permiso se evalúa "
                        f"contra el patrón de búsqueda, no contra la ruta "
                        f"(t7-live-walk.md §3): entradas inertes "
                        f"{flagged!r}")


def mark_active_packet(root: Path, status: str) -> None:
    state = read_state(root)
    state["active_packet"]["status"] = status
    write_state(root, state)


def run_guard(root: Path, role: str, tool_name: str, tool_input: dict,
              *, packet_cli: str | None = None) -> subprocess.CompletedProcess:
    """Ejecuta el guard CC con la forma REAL del JSON de hook (I10/C2)."""
    env = dict(os.environ)
    env[CLI_ENV] = packet_cli or str(SCRIPT)
    payload = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
    return subprocess.run(
        ["bash", str(GUARD), role],
        input=payload, capture_output=True, text=True,
        cwd=str(root), env=env,
    )


class LayoutProject(unittest.TestCase):
    """Proyecto sintético con bootstrap v2 (fixtures T2–T4) por layout."""

    LAYOUT = "conventional"

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-t5-red-")
        self.addCleanup(lambda: subprocess.run(
            ["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)
        # Copia temporal de los agentes generados del repo (fuente I9),
        # copiada sin inspección: es fixture, no lectura de implementación.
        self.agents_src = Path(self._tmp) / "agents-src"
        self.agents_src.mkdir()
        for f in sorted((REPO_ROOT / "agents").glob("cdad-*.md")):
            shutil.copy2(f, self.agents_src / f.name)
        self.apply_layout(self.LAYOUT)

    def apply_layout(self, layout: str) -> None:
        (self.root / POLICY_FILE).write_text(
            json.dumps(policy_doc(layout), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        for rel in LAYOUT_FILES[layout]:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# fixture {rel}\n", encoding="utf-8")

    def prepare(self, *extra: str, role: str = "test-writer",
                substage: str = "red",
                objective: str = "T5 runtime encargo") -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env[AGENTS_ENV] = str(self.agents_src)
        args = prepare_args(self.root, role=role, substage=substage,
                            objective=objective, extra=extra)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True, cwd=REPO_ROOT, env=env,
        )


# ------------------------------------------------------- PD-8 / I9 publicación


class TestPd8I9Publication(LayoutProject):
    """PD-8/I9: prepare publica agentes locales OpenCode + manifest."""
    LAYOUT = "cdad"

    def test_pd8_i9_prepare_publishes_local_opencode_agents(self) -> None:
        """PD-8/I9: con CDAD_OPENCODE_AGENTS_DIR en una copia temporal de los
        agentes generados, un prepare publica .opencode/agents/cdad-*.md con
        los mismos nombres que sus equivalentes globales."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"el prepare del fixture debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        pub = published_derived(self.root)
        expected = sorted(p.name for p in self.agents_src.glob("cdad-*.md"))
        self.assertEqual(
            sorted(pub), expected,
            msg=f"PD-8/I9: los derivados publicados {sorted(pub)} deben "
                f"espejar la fuente {expected}")

    def test_pd8_i9_manifest_records_policy_and_agent_hashes(self) -> None:
        """PD-8/I9: .opencode/agents/.cdad-derived.json existe y registra el
        hash de la política aceptada y el hash de cada agente de origen y
        derivado."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"el prepare del fixture debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        manifest = derived_dir(self.root) / MANIFEST
        self.assertTrue(
            manifest.is_file(),
            msg=f"PD-8/I9: falta el manifest {DERIVED_DIR}/{MANIFEST}")
        blob = manifest.read_text(encoding="utf-8")
        self.assertIn(
            policy_sha(self.root), blob,
            msg="PD-8/I9: el manifest no registra el hash de la política aceptada")
        for name in sorted(p.name for p in self.agents_src.glob("cdad-*.md")):
            with self.subTest(agent=name):
                src_sha = sha256_bytes((self.agents_src / name).read_bytes())
                pub = published_derived(self.root)
                self.assertIn(
                    name, pub,
                    msg=f"PD-8/I9: derivado {name} no publicado")
                der_sha = sha256_bytes(pub[name])
                self.assertIn(
                    src_sha, blob,
                    msg=f"PD-8/I9: el manifest no registra el hash del "
                        f"agente de origen {name}")
                self.assertIn(
                    der_sha, blob,
                    msg=f"PD-8/I9: el manifest no registra el hash del "
                        f"derivado {name}")

    def test_pd8_i9_foreign_file_survives_publication(self) -> None:
        """PD-8/I9: un archivo ajeno preexistente en .opencode/agents/
        sobrevive a la publicación de los derivados."""
        foreign = derived_dir(self.root) / "mi-agento-propio.md"
        foreign.parent.mkdir(parents=True, exist_ok=True)
        foreign.write_text("# agente ajeno del proyecto\n", encoding="utf-8")
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"el prepare del fixture debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        self.assertEqual(
            foreign.read_text(encoding="utf-8"),
            "# agente ajeno del proyecto\n",
            msg="PD-8/I9: la publicación tocó un archivo ajeno en "
                ".opencode/agents/")
        require_derived(self, self.root, (TEST_WRITER,))

    def test_pd8_i9_derived_body_is_byte_identical_to_source(self) -> None:
        """PD-8/I9: salvo la REGIÓN de permisos (los mapas read/grep/glob/
        edit, la clave `write` y su cabecera `permission:`, escalar o
        map-opening), el derivado es byte a byte igual al agente de origen
        (no hay copias editables paralelas con contenido divergente).

        La cabecera `permission` es parte de la región (enmienda del
        oráculo; F-R1 del review-012, decisión del orquestador del
        2026-10-02): con `private_paths`, la derivación correcta reemplaza
        la línea escalar `permission: allow` del origen por el bloque
        `permission:` con mapas — esa sustitución NO es una divergencia.

        U6-7b (006-005) — A-1, reemplazo declarado: `write` también es
        parte de la región reemplazada. En OpenCode v2.0.27 la herramienta
        de escritura evalúa `edit` y `write` juntas (findLast): conservar
        el `write: ask` de una copia instalada previa al fix anularía el
        mapa derivado, así que la derivación lo reemplaza/retira. El resto
        del frontmatter y el cuerpo siguen comparándose byte a byte."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"el prepare del fixture debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root,
            tuple(p.name for p in sorted(self.agents_src.glob("cdad-*.md"))))
        for name, text in pub.items():
            with self.subTest(agent=name):
                origin = (self.agents_src / name).read_text(encoding="utf-8")
                self.assertEqual(
                    without_maps(text), without_maps(origin),
                    msg=f"PD-8/I9: {name} difiere del origen fuera de los "
                        f"mapas de permisos")


# --------------------------------------------------- PD-7 / I9 mapas semánticos


class TestPd7I9DerivedMaps(LayoutProject):
    """PD-7/I9: los mapas de cada derivado respetan la clasificación de la
    política del proyecto (evaluados con el findLast de pd10)."""

    def assert_verdicts(self, agent_text: str, agent: str,
                        expectations: tuple[tuple[str, str, str], ...]) -> None:
        for tool, probe, expected in expectations:
            with self.subTest(agent=agent, tool=tool, probe=probe):
                got = verdict(agent_text, tool, probe)
                self.assertEqual(
                    got, expected,
                    msg=f"PD-7/I9: {agent} — {tool}({probe!r}) resolvió "
                        f"{got!r}, la política exige {expected!r}")

    def test_pd7_i9_test_writer_cdad_layout_maps(self) -> None:
        """PD-7/I9 (layout CDAD — el de este repo): el derivado test-writer
        deniega leer implementación (scripts/x.py, agents/y.md — que el
        mapa global NO deniega), permite tests y co-ubicados declarados,
        edita solo tests y no puede editar la política.
        W-2 (t7-live-walk.md §3): además NO emite entradas por ruta en
        `grep`/`glob` (en OpenCode se median por el patrón de búsqueda —
        declararlas sería una barrera inexistente)."""
        self.apply_layout("cdad")
        proc = self.prepare()
        self.assertEqual(proc.returncode, 0,
                         msg=f"prepare falló: {proc.stdout} {proc.stderr}")
        tw = require_derived(self, self.root, (TEST_WRITER,))[TEST_WRITER]
        self.assert_verdicts(tw, TEST_WRITER, (
            ("read", "scripts/x.py", "deny"),
            ("read", "agents/y.md", "deny"),
            ("read", "tests/test_a.py", "allow"),
            ("edit", "tests/test_a.py", "allow"),
            ("read", "scripts/test_h.py", "allow"),   # co-ubicado declarado
            ("edit", "scripts/test_h.py", "allow"),
            ("edit", "scripts/x.py", "deny"),
            ("edit", "docs/cdad-policy.json", "deny"),
        ))
        assert_no_search_path_entries(self, {"cdad-test-writer.md": tw},
                                      policy_path_probes("cdad"))

    def test_pd7_i9_maps_conventional_and_colocated_layouts(self) -> None:
        """PD-7/I9 (layouts convencional y co-ubicado): test-writer sin
        lectura de src salvo co-ubicados; implementer edita implementación y
        ningún test; lectores sin edición de producto.
        W-2 (t7-live-walk.md §3): ningún derivado emite entradas por ruta
        en `grep`/`glob` (barrera inexistente en OpenCode)."""
        self.apply_layout("conventional")
        proc = self.prepare()
        self.assertEqual(proc.returncode, 0,
                         msg=f"prepare falló: {proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root, (TEST_WRITER, IMPLEMENTER, READER))
        self.assert_verdicts(pub[TEST_WRITER], TEST_WRITER, (
            ("read", "src/app.py", "deny"),
            ("read", "src/test_mod.py", "allow"),      # co-ubicado declarado
            ("edit", "src/test_mod.py", "allow"),
            ("read", "src/pkg/test_a.py", "allow"),    # co-ubicado (paquete)
            ("edit", "src/app.py", "deny"),
            ("read", "tests/test_a.py", "allow"),
            ("edit", "tests/test_a.py", "allow"),
            ("edit", "docs/cdad-policy.json", "deny"),
        ))
        self.assert_verdicts(pub[IMPLEMENTER], IMPLEMENTER, (
            ("edit", "src/app.py", "allow"),
            ("edit", "src/test_mod.py", "deny"),       # co-ubicado es test
            ("edit", "tests/test_a.py", "deny"),
            ("edit", "docs/cdad-policy.json", "deny"),
        ))
        self.assert_verdicts(pub[READER], READER, (
            ("edit", "src/app.py", "deny"),
            ("edit", "tests/test_a.py", "deny"),
            ("edit", "docs/specs/feat/spec.md", "deny"),
        ))
        assert_no_search_path_entries(
            self, pub, policy_path_probes("conventional"))

    def test_pd7_i9_maps_odoo_layout(self) -> None:
        """PD-7/I9 (layout Odoo addons/<m>/{models,views,tests}): el derivado
        odoo (y el base, según la política del proyecto) deniega leer
        models/views, permite tests; implementer-odoo edita su scope y ningún
        test. W-2 (t7-live-walk.md §3): ningún derivado emite entradas por
        ruta en `grep`/`glob` (barrera inexistente en OpenCode)."""
        self.apply_layout("odoo")
        proc = self.prepare()
        self.assertEqual(proc.returncode, 0,
                         msg=f"prepare falló: {proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root, (TEST_WRITER, TEST_WRITER_ODOO, IMPLEMENTER_ODOO))
        self.assert_verdicts(pub[TEST_WRITER_ODOO], TEST_WRITER_ODOO, (
            ("read", "addons/m/models/m.py", "deny"),
            ("read", "addons/m/views/v.xml", "deny"),
            ("read", "addons/m/tests/test_m.py", "allow"),
            ("edit", "addons/m/tests/test_m.py", "allow"),
            ("edit", "addons/m/models/m.py", "deny"),
            ("edit", "docs/cdad-policy.json", "deny"),
        ))
        # La política del proyecto clasifica models como implementación:
        # también el derivado base del test-writer debe denegarla.
        self.assert_verdicts(pub[TEST_WRITER], TEST_WRITER, (
            ("read", "addons/m/models/m.py", "deny"),
            ("read", "addons/m/tests/test_m.py", "allow"),
        ))
        self.assert_verdicts(pub[IMPLEMENTER_ODOO], IMPLEMENTER_ODOO, (
            ("edit", "addons/m/models/m.py", "allow"),
            ("edit", "addons/m/views/v.xml", "allow"),
            ("edit", "addons/m/tests/test_m.py", "deny"),
        ))
        assert_no_search_path_entries(self, pub, policy_path_probes("odoo"))

    def test_pd7_i9_policy_edit_deny_for_every_derived_role(self) -> None:
        """PD-7: la exclusión de docs/cdad-policy.json prevalece sobre
        cualquier permiso por clase: TODOS los derivados tienen edit deny."""
        self.apply_layout("cdad")
        proc = self.prepare()
        self.assertEqual(proc.returncode, 0,
                         msg=f"prepare falló: {proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root,
            tuple(p.name for p in sorted(self.agents_src.glob("cdad-*.md"))))
        for name, text in pub.items():
            with self.subTest(agent=name):
                self.assertEqual(
                    verdict(text, "edit", "docs/cdad-policy.json"), "deny",
                    msg=f"PD-7: {name} puede editar docs/cdad-policy.json")


# ------------------------------------------------------- PD-8/I9 ciclo de vida


class TestPd8I9DerivedLifecycle(LayoutProject):
    """PD-8/I9 (+PD-5): derivados modificados a mano y regeneración tras
    reconciliación."""
    LAYOUT = "cdad"

    def test_pd8_i9_hand_modified_derived_fails_without_overwrite(self) -> None:
        """PD-8/I9: un derivado modificado a mano hace fallar el prepare
        siguiente (rc≠0) SIN sobrescribirlo y sin publicar paquete."""
        proc = self.prepare()
        self.assertEqual(proc.returncode, 0,
                         msg=f"primer prepare falló: {proc.stdout} {proc.stderr}")
        derived = derived_dir(self.root) / "cdad-scribe.md"
        require_derived(self, self.root, ("cdad-scribe.md",))
        derived.write_text(
            derived.read_text(encoding="utf-8") + "\n<!-- mano -->\n",
            encoding="utf-8")
        mark_active_packet(self.root, "completed")
        snapshot = published_derived(self.root)
        second = self.prepare(role="implementer", substage="green",
                              objective="encargo tras derivado a mano")
        self.assertNotEqual(
            second.returncode, 0,
            msg="PD-8/I9: prepare aceptó un derivado modificado a mano")
        self.assertEqual(
            second.stdout, "",
            msg="PD-8/I9: el fallo imprimió un paquete despachable")
        self.assertEqual(
            published_derived(self.root), snapshot,
            msg="PD-8/I9: el derivado modificado a mano fue sobrescrito")
        self.assertIn(
            "<!-- mano -->",
            (derived_dir(self.root) / "cdad-scribe.md").read_text(encoding="utf-8"),
            msg="PD-8/I9: los bytes del derivado a mano no se conservaron")

    def test_pd8_i9_reconciled_policy_regenerates_deriveds(self) -> None:
        """PD-5/I9: tras reconciliar una política nueva, los derivados se
        regeneran antes del próximo paquete (nueva denegación presente y
        manifest con el hash de la revisión aceptada; el resto del agente
        sigue byte a byte igual al origen)."""
        proc = self.prepare()
        self.assertEqual(proc.returncode, 0,
                         msg=f"primer prepare falló: {proc.stdout} {proc.stderr}")
        require_derived(self, self.root, (TEST_WRITER,))
        # Revisión nueva de la política: raíz de implementación adicional.
        doc = json.loads((self.root / POLICY_FILE).read_text(encoding="utf-8"))
        doc["path_policy"]["implementation_roots"].append("vendor")
        (self.root / POLICY_FILE).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        new_sha = policy_sha(self.root)
        decision = self.root / "docs" / "decision-policy-revision.md"
        decision.write_text(
            f"# Decisión del dueño\nsha256: {new_sha}\n", encoding="utf-8")
        mark_active_packet(self.root, "completed")
        # A-2 (review-t3): argv PURO del modo reconciliación, sin las
        # opciones ordinarias que inyecta self.prepare (I5d).
        rec_env = dict(os.environ)
        rec_env[AGENTS_ENV] = str(self.agents_src)
        rec = subprocess.run(
            [sys.executable, str(SCRIPT),
             "prepare", "--project-root", str(self.root),
             "--reconcile-policy", new_sha,
             "--decision-ref", "docs/decision-policy-revision.md"],
            capture_output=True, text=True, cwd=REPO_ROOT, env=rec_env,
        )
        self.assertEqual(
            rec.returncode, 0,
            msg=f"la reconciliación (T3/I6, precondición) falló: "
                f"{rec.stdout} {rec.stderr}")
        # Próximo paquete: los derivados deben corresponder a la revisión
        # aceptada ANTES del despacho.
        second = self.prepare(role="implementer", substage="green",
                              objective="paquete tras reconciliar")
        self.assertEqual(
            second.returncode, 0,
            msg=f"prepare post-reconciliación falló: "
                f"{second.stdout} {second.stderr}")
        tw = require_derived(self, self.root, (TEST_WRITER,))[TEST_WRITER]
        self.assertEqual(
            verdict(tw, "read", "vendor/v.py"), "deny",
            msg="PD-5/I9: los derivados no reflejan la revisión reconciliada "
                "(vendor/ sigue legible para el test-writer)")
        blob = (derived_dir(self.root) / MANIFEST).read_text(encoding="utf-8")
        self.assertIn(
            new_sha, blob,
            msg="PD-5/I9: el manifest no registra la revisión aceptada")
        origin = (self.agents_src / TEST_WRITER).read_text(encoding="utf-8")
        self.assertEqual(
            without_maps(tw), without_maps(origin),
            msg="PD-8/I9: la regeneración alteró el agente fuera de los mapas")


# ------------------------------------------------- PD-8 / I10 / C2 guard CC


class TestPd8I10CcGuard(LayoutProject):
    """PD-8/I10/C2: el guard de Claude Code carga la política del proyecto y
    media Read/Edit/Write por file_path y Grep/Glob por su forma real."""
    LAYOUT = "cdad"

    def test_pd8_i10_c2_guard_denies_read_of_implementation(self) -> None:
        """PD-8/I10/C2: con política, el guard deniega (exit 2) el Read de
        implementación al test-writer en layout CDAD (scripts/, agents/ — que
        el mapa global NO deniega); relativo y absoluto."""
        for file_path in ("scripts/x.py", "agents/y.md",
                          str(self.root / "scripts" / "x.py")):
            with self.subTest(file_path=file_path):
                proc = run_guard(self.root, "test-writer-read", "Read",
                                 {"file_path": file_path})
                self.assertEqual(
                    proc.returncode, 2,
                    msg=f"PD-8/I10/C2: el guard permitió Read({file_path!r}) "
                        f"al test-writer con política que la clasifica "
                        f"implementación (rc={proc.returncode})")

    def test_pd8_i10_c2_guard_allows_tests_paths_for_test_writer(self) -> None:
        """PD-8/I10 (lado positivo): tests/ se lee y se edita; un Grep acotado
        a tests/ pasa."""
        cases = (
            ("test-writer-read", "Read", {"file_path": "tests/test_a.py"}),
            ("test-writer-write", "Edit", {"file_path": "tests/test_a.py"}),
            ("test-writer-read", "Grep",
             {"pattern": "def test_", "path": "tests"}),
        )
        for role, tool, tool_input in cases:
            with self.subTest(role=role, tool=tool, tool_input=tool_input):
                proc = run_guard(self.root, role, tool, tool_input)
                self.assertEqual(
                    proc.returncode, 0,
                    msg=f"PD-8/I10: el guard bloqueó {tool}({tool_input}) "
                        f"para {role} (rc={proc.returncode}: "
                        f"{proc.stderr.strip()})")

    def test_pd8_i10_c2_guard_denies_scoped_grep_glob_into_impl(self) -> None:
        """PD-8/I10/C2: con política, Grep con path=scripts y Glob con
        path=scripts al test-writer se deniegan (exit 2)."""
        cases = (
            ("Grep", {"pattern": "TODO", "path": "scripts"}),
            ("Grep", {"pattern": "TODO",
                      "path": str(self.root / "scripts")}),
            ("Glob", {"pattern": "**/*.py", "path": "scripts"}),
        )
        for tool, tool_input in cases:
            with self.subTest(tool=tool, tool_input=tool_input):
                proc = run_guard(self.root, "test-writer-read", tool,
                                 tool_input)
                self.assertEqual(
                    proc.returncode, 2,
                    msg=f"PD-8/I10/C2: el guard permitió {tool}"
                        f"({tool_input}) al test-writer sobre implementación "
                        f"(rc={proc.returncode})")

    def test_pd8_i10_c2_guard_blocks_unscoped_grep_glob(self) -> None:
        """PD-8/I10/C2: Grep/Glob SIN path (todo el proyecto) al test-writer,
        habiendo raíces de implementación, se bloquean con un mensaje que
        pide acotar la búsqueda a tests/docs."""
        for tool, tool_input in (
            ("Grep", {"pattern": "def "}),
            ("Glob", {"pattern": "**/*.py"}),
        ):
            with self.subTest(tool=tool):
                proc = run_guard(self.root, "test-writer-read", tool,
                                 tool_input)
                out = proc.stdout + proc.stderr
                self.assertEqual(
                    proc.returncode, 2,
                    msg=f"PD-8/I10/C2: el guard permitió {tool} sin path "
                        f"(rc={proc.returncode})")
                self.assertRegex(
                    out, r"acot|narrow|scope|tests|docs",
                    msg=f"PD-8/I10/C2: el bloqueo de {tool} sin path no pide "
                        f"acotar la búsqueda: {out!r}")

    def test_pd8_i10_c2_guard_denies_implementer_edit_of_tests(self) -> None:
        """PD-7/I10: el guard deniega (exit 2) el Edit de tests al
        implementer (dedicados y co-ubicados)."""
        for file_path in ("tests/test_a.py", "scripts/test_h.py"):
            with self.subTest(file_path=file_path):
                proc = run_guard(self.root, "implementer", "Edit",
                                 {"file_path": file_path})
                self.assertEqual(
                    proc.returncode, 2,
                    msg=f"PD-7/I10: el guard permitió al implementer editar "
                        f"el test {file_path!r} (rc={proc.returncode})")

    def test_pd8_i10_c2_guard_blocks_on_invalid_policy(self) -> None:
        """PD-8/I10: política inválida → el guard bloquea, sin fallback
        silencioso a los globs globales."""
        doc = json.loads((self.root / POLICY_FILE).read_text(encoding="utf-8"))
        doc["models"] = {"policy": "cheap"}  # campo extra → inválida (PD-1)
        (self.root / POLICY_FILE).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        proc = run_guard(self.root, "test-writer-read", "Read",
                         {"file_path": "scripts/x.py"})
        self.assertEqual(
            proc.returncode, 2,
            msg=f"PD-8/I10: con política inválida el guard permitió la "
                f"operación (fallback silencioso) (rc={proc.returncode})")

    def test_pd8_i10_c2_guard_blocks_when_cli_unfindable(self) -> None:
        """PD-8/I10 (detalle I10): con política presente y CDAD_PACKET_CLI
        no encontrable, el guard bloquea con diagnóstico: sin fallback."""
        proc = run_guard(self.root, "test-writer-read", "Read",
                         {"file_path": "scripts/x.py"},
                         packet_cli=str(self.root / "no-existe" / "cli.py"))
        self.assertEqual(
            proc.returncode, 2,
            msg=f"PD-8/I10: con CLI no encontrable y política presente el "
                f"guard permitió la operación (rc={proc.returncode})")

    def test_pd8_i10_c2_guard_legacy_smoke_without_policy(self) -> None:
        """PD-8/I10: sin política se conserva el comportamiento legacy
        (caso de humo): src/ denegado al test-writer, tests permitidos y el
        implementer no toca tests co-ubicados."""
        self.apply_layout("conventional")
        (self.root / POLICY_FILE).unlink()
        cases = (
            ("test-writer-read", "Read", {"file_path": "src/app.py"}, 2),
            ("test-writer-read", "Read",
             {"file_path": "tests/test_a.py"}, 0),
            ("implementer", "Edit", {"file_path": "src/test_mod.py"}, 2),
        )
        for role, tool, tool_input, expected in cases:
            with self.subTest(role=role, tool=tool, tool_input=tool_input):
                proc = run_guard(self.root, role, tool, tool_input)
                self.assertEqual(
                    proc.returncode, expected,
                    msg=f"PD-8/I10 (legacy sin política): {tool}"
                        f"({tool_input}) para {role} dio "
                        f"rc={proc.returncode}, esperado {expected}")

    def test_pd8_i10_guard_odoo_layout_controls(self) -> None:
        """PD-7/I10 (layout Odoo): controles del guard — models/ denegado al
        test-writer-odoo y tests/ denegado al implementer."""
        self.apply_layout("odoo")
        cases = (
            ("test-writer-odoo-read", "Read",
             {"file_path": "addons/m/models/m.py"}, 2),
            ("test-writer-odoo-read", "Read",
             {"file_path": "addons/m/tests/test_m.py"}, 0),
            ("implementer", "Edit",
             {"file_path": "addons/m/tests/test_m.py"}, 2),
        )
        for role, tool, tool_input, expected in cases:
            with self.subTest(role=role, tool=tool, tool_input=tool_input):
                proc = run_guard(self.root, role, tool, tool_input)
                self.assertEqual(
                    proc.returncode, expected,
                    msg=f"PD-7/I10 (odoo): {tool}({tool_input}) para {role} "
                        f"dio rc={proc.returncode}, esperado {expected}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
