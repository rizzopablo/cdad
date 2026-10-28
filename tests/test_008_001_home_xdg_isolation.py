#!/usr/bin/env python3
"""008-001 RED — aislamiento HOME/XDG por test (PC-1..PC-5; PC-6 es gate).

Contract: docs/specs/008-001-home-xdg-isolation/spec.md (PC-1..PC-6 y los
ajustes AJ1–AJ3, que prevalecen).

Superficie observable:
- PC-1/PC-3/PC-4/PC-5: corridas ANIDADAS de pytest por subprocess sobre un
  directorio temporal externo al repo. Su `conftest.py` registra
  `tests.conftest` como plugin (`pytest_plugins`), de modo que la fixture
  transversal de la suite rige los tests internos exactamente como en la
  suite real. Los tests internos reportan JSON en archivos cuya ruta llega
  por `CDAD_TEST_*` (conservadas por AJ2). El HOME del controlador es un
  HOME EXTERNO SINTÉTICO: nunca se usa el HOME real del operador.
- PC-2: un driver en subprocess importa
  `skills/cdad-cycle/scripts/cdad_packet.py` con HOME=A y DESPUÉS cambia
  HOME sin reimportar; consulta `_derived_source_dir(project_root)` (nombre
  y firma citados por la spec §2) y `main(argv)` (`prepare`) para el
  oráculo por bytes del manifiesto y los agentes publicados.

Mapa test → postcondición (causa RED esperada hoy: no hay fixture autouse ni
resolución lazy; todas fallan por AssertionError de contrato):
  test_pc1_roots_exclusive_and_inherited               -> PC-1 (+variantes)
  test_pc2_global_agents_origin_follows_current_home   -> PC-2 (lazy)
  test_pc2_precedence_override_activation_fallback     -> PC-2 (variantes)
  test_pc3_inherited_overrides_neutralized_per_aj2     -> PC-3 (tabla AJ2)
  test_pc3_real_acceptances_stay_skipped_without_vars  -> PC-3 (skip)
  test_pc4_writes_confined_external_home_unchanged     -> PC-4
  test_pc4_canary_detects_deliberate_external_write    -> PC-4 (control -)
  test_pc5_restores_env_and_tempdir_after_failure      -> PC-5 (+variantes)
  PC-6: SIN test en RED; gate del closer (tres corridas completas, AJ3).

Límite declarado (PC-4): el canario compara inventario y `mtime_ns` del HOME
externo sintético; NO observa lecturas ni escrituras transitorias revertidas
entre snapshots.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from test_005_005_t3_provenance import (  # noqa: E402
    AGENTS_SUBDIR,
    POLICY_DOC,
    POLICY_REL,
    make_adopted_root,
)
import test_005_005_t3_provenance as _provenance  # noqa: E402
from test_004_002_t2_bootstrap import (  # noqa: E402
    REPO_ROOT,
    build_project,
    prepare_args,
)

PRODUCT_MODULE = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"

MANAGED = ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME",
           "XDG_CACHE_HOME", "XDG_RUNTIME_DIR", "TMPDIR", "TMP", "TEMP")
RETIRED = ("CDAD_INSTALL_ROOT", "CDAD_OPENCODE_AGENTS_DIR",
           "CDAD_CONTEXT_METER_STORE")
PRESERVED = {"CDAD_DELEGATE_DESTINATION": "decoy-destination",
             "CDAD_STATIC_BLOCK_LIMIT": "4242",
             "CDAD_TEST_PRESERVED_PROBE": "probe-value"}
REAL_ACCEPTANCE_VARS = ("CDAD_CONTEXT_METER_REAL_STORE",
                        "CDAD_005_002_SBOOT04_SESSION_ID")

INNER_CONFTEST = textwrap.dedent(f"""
    import json, os, sys, tempfile
    sys.path.insert(0, {str(REPO_ROOT)!r})
    pytest_plugins = ["tests.conftest"]
    MANAGED = {MANAGED!r}
    SNAP_KEYS = MANAGED + {RETIRED!r}

    def _snap():
        return {{"env": {{k: os.environ.get(k) for k in SNAP_KEYS}},
                 "tempdir": tempfile.tempdir}}

    def pytest_sessionstart(session):
        preset = os.environ.get("CDAD_TEST_PRESET_TEMPDIR")
        tempfile.tempdir = preset or None
        _write("session", _snap())

    def pytest_runtest_logstart(nodeid, location):
        _write("before::" + nodeid.split("::")[-1], _snap())

    def pytest_runtest_logfinish(nodeid, location):
        _write("after::" + nodeid.split("::")[-1], _snap())

    def pytest_sessionfinish(session, exitstatus):
        _write("sessionfinish", _snap())

    def _write(key, value):
        path = os.environ["CDAD_TEST_CONTROLLER_LOG"]
        data = json.load(open(path)) if os.path.exists(path) else {{}}
        data[key] = value
        open(path, "w").write(json.dumps(data))
""")

# Reporte común de los tests internos: entorno, temporal y subprocess.
INNER_HELPERS = textwrap.dedent(f"""
    import json, os, subprocess, sys, tempfile
    from pathlib import Path
    MANAGED = {MANAGED!r}
    CHILD = ("import json,os,sys,tempfile;"
             "fd,p=tempfile.mkstemp();os.close(fd);"
             "print(json.dumps({{'env':{{k:os.environ.get(k) for k in "
             + repr(MANAGED) + "}},'tmp':p}}))")

    def report(name, extra=None):
        fd, tmp = tempfile.mkstemp()
        os.close(fd)
        child = json.loads(subprocess.run(
            [sys.executable, "-c", CHILD], capture_output=True, text=True,
            env=os.environ.copy(), check=True).stdout)
        marker = Path(os.environ["HOME"]) / ("marker-" + name)
        marker.write_bytes(("marker-" + name).encode())
        data = {{"env": {{k: os.environ.get(k) for k in MANAGED}},
                 "tmp": tmp, "child": child, "marker": str(marker),
                 "foreign_marker_seen": sorted(
                     p.name for p in Path(os.environ["HOME"]).glob("marker-*")
                     if p.name != "marker-" + name),
                 "tempdir": tempfile.gettempdir()}}
        data.update(extra or {{}})
        out = Path(os.environ["CDAD_TEST_REPORT_DIR"]) / (name + ".json")
        out.write_text(json.dumps(data))
""")

INNER_PC1 = INNER_HELPERS + textwrap.dedent("""
    def test_a():
        tempfile.gettempdir()  # puebla la caché antes del siguiente test
        report("a")

    def test_b():
        report("b")

    def test_c_local_override(tmp_path, monkeypatch):
        own = tmp_path / "own-home"
        own.mkdir()
        monkeypatch.setenv("HOME", str(own))
        report("c")
""")

INNER_PC3 = INNER_HELPERS + textwrap.dedent(f"""
    KEYS = {RETIRED + tuple(PRESERVED)!r}

    def test_env_view():
        report("pc3", {{"cdad": {{k: os.environ.get(k) for k in KEYS}}}})

    def test_prepare_ignores_decoy_agents():
        root = Path(os.environ["CDAD_TEST_PROJECT"])
        proc = subprocess.run(
            [sys.executable, {str(REPO_ROOT / "scripts" / "cdad_packet.py")!r},
             *json.loads(os.environ["CDAD_TEST_PREPARE_ARGS"])],
            capture_output=True, text=True, cwd={str(REPO_ROOT)!r},
            env=os.environ.copy(), stdin=subprocess.DEVNULL)
        published = sorted((root / ".opencode" / "agents").glob("cdad-*.md"))
        out = Path(os.environ["CDAD_TEST_REPORT_DIR"]) / "pc3-prepare.json"
        out.write_text(json.dumps({{
            "rc": proc.returncode,
            "decoy_seen": [p.name for p in published
                           if b"DECOY-AGENT-MARKER" in p.read_bytes()]}}))

    def _config_dir():
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cdad_delegate_pc3",
            {str(REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_delegate.py")!r})
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return str(mod.cdad_config_dir())

    def test_config_dir_consumer(tmp_path, monkeypatch):
        isolated_xdg = os.environ["XDG_CONFIG_HOME"]
        inherited = _config_dir()
        synthetic = tmp_path / "synthetic-install"
        synthetic.mkdir()
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.setenv("CDAD_INSTALL_ROOT", str(synthetic))
        local = _config_dir()
        Path(os.environ["CDAD_TEST_REPORT_DIR"], "pc3-config.json").write_text(
            json.dumps({{"inherited": inherited, "local": local,
                         "isolated_xdg": isolated_xdg,
                         "synthetic": str(synthetic)}}))

    def test_meter_store_consumer(tmp_path, monkeypatch):
        import tests.test_005_002_t1_neutral_record as neutral
        meter = [sys.executable,
                 {str(REPO_ROOT / "scripts" / "cdad_context_meter.py")!r},
                 "--limit", "1"]
        run = lambda: subprocess.run(meter, capture_output=True, text=True,
                                     cwd={str(REPO_ROOT)!r}, env=os.environ.copy(),
                                     stdin=subprocess.DEVNULL, timeout=120)
        inherited = run()
        store = tmp_path / "synthetic.sqlite"
        neutral._build_store(store, variant="valid")
        monkeypatch.setenv("CDAD_CONTEXT_METER_STORE", str(store))
        local = run()
        Path(os.environ["CDAD_TEST_REPORT_DIR"], "pc3-meter.json").write_text(
            json.dumps({{"inherited_rc": inherited.returncode,
                         "inherited_err": inherited.stderr,
                         "local_rc": local.returncode, "local_err": local.stderr}}))
""")

INNER_PC4 = INNER_HELPERS + textwrap.dedent("""
    import pytest, unittest
    EARLY = MANAGED + ("CDAD_INSTALL_ROOT", "CDAD_OPENCODE_AGENTS_DIR",
                       "CDAD_CONTEXT_METER_STORE")

    def early(name):
        Path(os.environ["HOME"], "early-" + name).write_bytes(b"early")
        Path(os.environ["CDAD_TEST_REPORT_DIR"], "early-" + name + ".json").write_text(
            json.dumps({k: os.environ.get(k) for k in EARLY}))

    class TestEarlyClass(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            early("setupclass")

        def test_noop(self):
            pass

    @pytest.fixture(scope="module")
    def module_fixture():
        early("module")

    def test_module_fixture(module_fixture):
        pass

    def test_writes():
        report("w")
        Path(os.environ["XDG_CONFIG_HOME"], "cfg-marker").write_bytes(b"cfg")
        Path(os.environ["XDG_STATE_HOME"], "state-marker").write_bytes(b"st")
""")

INNER_PC4_NEG = INNER_HELPERS + textwrap.dedent("""
    def test_escapes():
        report("w")
        Path(os.environ["CDAD_TEST_EXTERNAL_HOME"], "escaped").write_bytes(b"x")
""")

INNER_PC5 = INNER_HELPERS + textwrap.dedent("""
    import pytest, time

    @pytest.fixture
    def sleeper():
        proc = subprocess.Popen([sys.executable, "-c",
                                 "import time; time.sleep(60)"])
        yield proc
        proc.terminate()
        proc.wait(timeout=10)
        Path(os.environ["CDAD_TEST_REPORT_DIR"], "sleeper.json").write_text(
            json.dumps({"pid": proc.pid, "returncode": proc.returncode,
                        "home_existed_at_kill": Path(os.environ["HOME"]).is_dir()}))

    def test_fails_deliberately(sleeper):
        report("f")
        assert False, "fallo deliberado (PC-5)"

    def test_passes():
        report("p")
""")


# ---------------------------------------------------------------- helpers


def inventory(root: Path) -> dict:
    """Inventario {ruta relativa: (tipo, mtime_ns, size)} sin seguir enlaces."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in dirnames + filenames:
            p = Path(dirpath) / name
            st = p.lstat()
            out[str(p.relative_to(root))] = (oct(st.st_mode)[:-3],
                                             st.st_mtime_ns, st.st_size)
    return out


def common_root(env: dict) -> str:
    return os.path.commonpath([env[k] for k in MANAGED])


class NestedRunCase(unittest.TestCase):
    """Controlador de corridas anidadas con HOME/TMP externos sintéticos."""

    def setUp(self) -> None:
        self.base = Path(tempfile.mkdtemp(prefix="cdad-008-001-"))
        self.addCleanup(shutil.rmtree, self.base, True)
        self.ext_home = self.base / "external-home"
        self.ext_tmp = self.base / "external-tmp"
        self.reports = self.base / "reports"
        self.inner = self.base / "inner"
        for d in (self.ext_home, self.ext_tmp, self.reports, self.inner):
            d.mkdir()
        (self.ext_home / "operator.cfg").write_bytes(b"operator-config")
        (self.ext_home / ".config").mkdir()
        self.log = self.base / "controller.json"

    def parent_env(self, **extra: str) -> dict:
        env = os.environ.copy()
        env.update(HOME=str(self.ext_home), TMPDIR=str(self.ext_tmp),
                   TMP=str(self.ext_tmp), TEMP=str(self.ext_tmp),
                   XDG_CONFIG_HOME=str(self.ext_home / ".config"),
                   CDAD_TEST_REPORT_DIR=str(self.reports),
                   CDAD_TEST_CONTROLLER_LOG=str(self.log),
                   CDAD_TEST_EXTERNAL_HOME=str(self.ext_home))
        env.pop("XDG_RUNTIME_DIR", None)  # variante: originalmente ausente
        env.update(extra)
        return env

    def run_inner(self, body: str, env: dict) -> subprocess.CompletedProcess:
        (self.inner / "conftest.py").write_text(INNER_CONFTEST)
        (self.inner / "test_inner.py").write_text(body)
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "--rootdir", str(self.inner), str(self.inner)],
            capture_output=True, text=True, cwd=str(self.inner), env=env,
            stdin=subprocess.DEVNULL, timeout=300)

    def report(self, name: str) -> dict:
        return json.loads((self.reports / f"{name}.json").read_text())


# ---------------------------------------------------------------- PC-1


class TestPC1Roots(NestedRunCase):

    def test_pc1_roots_exclusive_and_inherited(self) -> None:
        proc = self.run_inner(INNER_PC1, self.parent_env())
        self.assertEqual(proc.returncode, 0,
                         msg=f"PC-1: la corrida anidada debe pasar\n{proc.stdout}{proc.stderr}")
        a, b, c = self.report("a"), self.report("b"), self.report("c")
        self.assertEqual([k for k in MANAGED if a["env"][k] is None], [],
                         msg=f"PC-1: las nueve variables gestionadas están definidas: {a['env']!r}")
        self.assertTrue(all(Path(v).is_absolute() for v in a["env"].values()),
                        msg=f"PC-1: las nueve variables son absolutas: {a['env']!r}")
        root_a, root_b = common_root(a["env"]), common_root(b["env"])
        self.assertNotEqual(root_a, root_b,
                            msg=f"PC-1: dos tests deben observar raíces distintas: {root_a!r}")
        self.assertNotEqual(os.path.commonpath([root_a, str(self.ext_home)]),
                            str(self.ext_home),
                            msg=f"PC-1: la raíz {root_a!r} no puede estar bajo el HOME externo")
        self.assertNotEqual(os.path.commonpath([root_a, str(self.ext_tmp)]),
                            str(self.ext_tmp),
                            msg=f"PC-1: la raíz {root_a!r} no puede estar bajo el TMPDIR heredado")
        self.assertEqual(a["child"]["env"], a["env"],
                         msg="PC-1: el subprocess (env copiado) hereda las nueve rutas")
        self.assertEqual(os.path.commonpath([root_b, b["tmp"]]), root_b,
                         msg=f"PC-1: el temporal de b {b['tmp']!r} debe quedar bajo su raíz "
                             f"aunque la caché tempfile estuviera poblada")
        self.assertEqual(os.path.commonpath([root_b, b["child"]["tmp"]]), root_b,
                         msg="PC-1: el temporal del subprocess queda bajo la raíz del test")
        self.assertFalse(Path(b["marker"]).exists(),
                         msg="PC-1: el marcador de b no sobrevive a su raíz descartable")
        self.assertEqual(b["foreign_marker_seen"], [],
                         msg=f"PC-1: b no ve marcadores de a: {b['foreign_marker_seen']!r}")
        self.assertEqual((c["env"]["HOME"], c["child"]["env"]["HOME"]),
                         (c["env"]["HOME"], c["env"]["HOME"]),
                         msg="PC-1 (override local): el subprocess hereda el HOME del test")
        self.assertTrue(c["env"]["HOME"].endswith("own-home"),
                        msg=f"PC-1 (override local): conserva efecto: {c['env']['HOME']!r}")
        self.assertEqual(sorted(p.name for p in self.ext_home.iterdir()),
                         [".config", "operator.cfg"],
                         msg="PC-1: ningún marcador en el HOME externo")


# ---------------------------------------------------------------- PC-2


PC2_DRIVER = textwrap.dedent("""
    import contextlib, importlib.util, io, json, os, sys
    from pathlib import Path
    args = json.loads(sys.argv[1])
    os.environ["HOME"] = args["home_import"]
    spec = importlib.util.spec_from_file_location("cdad_packet_pc2", args["module"])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    out = {}
    for step in args["steps"]:
        os.environ["HOME"] = step["home"]
        os.environ.pop("CDAD_OPENCODE_AGENTS_DIR", None)
        if step.get("override"):
            os.environ["CDAD_OPENCODE_AGENTS_DIR"] = step["override"]
        res = {"resolved": str(mod._derived_source_dir(Path(step["project"])))}
        if step.get("prepare"):
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    res["rc"] = mod.main(step["prepare"])
            except SystemExit as exc:
                res["rc"] = exc.code if isinstance(exc.code, int) else 1
            res["stderr"] = err.getvalue()
        out[step["name"]] = res
    print(json.dumps(out))
""")


class TestPC2LazyOrigin(unittest.TestCase):

    def setUp(self) -> None:
        self.base = Path(tempfile.mkdtemp(prefix="cdad-008-001-pc2-"))
        self.addCleanup(shutil.rmtree, self.base, True)

    def home_with_agents(self, label: str) -> Path:
        home = self.base / f"home-{label}"
        agents = home.joinpath(*AGENTS_SUBDIR)
        agents.mkdir(parents=True)
        for src in sorted(REPO_ROOT.glob("agents/cdad-*.md")):
            agents.joinpath(src.name).write_bytes(
                src.read_bytes() + f"\nPC2-MARKER-{label}\n".encode())
        return home

    def project(self, name: str) -> Path:
        root = build_project(self.base / name)
        (root / POLICY_REL).write_text(json.dumps(POLICY_DOC, indent=2) + "\n")
        return root

    def drive(self, home_import: Path, steps: list) -> dict:
        env = os.environ.copy()
        env.pop("CDAD_OPENCODE_AGENTS_DIR", None)
        proc = subprocess.run(
            [sys.executable, "-c", PC2_DRIVER, json.dumps(
                {"module": str(PRODUCT_MODULE), "home_import": str(home_import),
                 "steps": steps})],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
            stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(proc.returncode, 0,
                         msg=f"PC-2: el driver debe terminar rc=0\n{proc.stderr}")
        return json.loads(proc.stdout.strip().splitlines()[-1])

    def published_markers(self, root: Path) -> list:
        return sorted({line for p in (root / ".opencode" / "agents").glob("cdad-*.md")
                       for line in p.read_text().splitlines()
                       if line.startswith("PC2-MARKER-")})

    def test_pc2_global_agents_origin_follows_current_home(self) -> None:
        h_import, h_b, h_c = (self.home_with_agents(x) for x in ("imp", "b", "c"))
        p_b, p_c = self.project("pb"), self.project("pc")
        out = self.drive(h_import, [
            {"name": "b", "home": str(h_b), "project": str(p_b),
             "prepare": prepare_args(p_b)},
            {"name": "c", "home": str(h_c), "project": str(p_c),
             "prepare": prepare_args(p_c)},
        ])
        self.assertEqual(out["b"]["resolved"], str(h_b.joinpath(*AGENTS_SUBDIR)),
                         msg=f"PC-2: tras cambiar HOME el fallback sigue al HOME vigente: {out!r}")
        self.assertEqual(out["c"]["resolved"], str(h_c.joinpath(*AGENTS_SUBDIR)),
                         msg=f"PC-2: un segundo cambio de HOME cambia el fallback sin reimportar: {out!r}")
        self.assertEqual(self.published_markers(p_b), ["PC2-MARKER-b"],
                         msg="PC-2: prepare consume los bytes de los agentes del HOME vigente (b)")
        self.assertEqual(self.published_markers(p_c), ["PC2-MARKER-c"],
                         msg="PC-2: prepare consume los bytes de los agentes del HOME vigente (c)")

    def test_pc2_precedence_override_activation_fallback(self) -> None:
        h_import, h_now = self.home_with_agents("imp"), self.home_with_agents("now")
        override = self.home_with_agents("ovr").joinpath(*AGENTS_SUBDIR)
        adopted = make_adopted_root(self.base, "act")
        # Marcador propio de la activación, con manifiesto coherente con los bytes.
        manifest_path = adopted / ".cdad-install-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        for agent in sorted(adopted.joinpath(*AGENTS_SUBDIR).glob("cdad-*.md")):
            agent.write_bytes(agent.read_bytes() + b"\nPC2-MARKER-act\n")
            rel = (Path(*AGENTS_SUBDIR) / agent.name).as_posix()
            manifest["artifacts"][rel]["sha256"] = hashlib.sha256(
                agent.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        projects = {}
        for name in ("override", "activation"):
            root = projects[name] = self.project("p" + name)
            # Módulo, no la clase: importarla la haría recolectar aquí.
            _provenance.ProvenanceCase.write_registry(None, root, adopted)
        projects["fallback"] = self.project("pfallback")
        projects["absent"] = self.project("pabsent")
        empty_home = self.base / "home-empty"
        empty_home.mkdir()
        homes = {"override": h_now, "activation": h_now, "fallback": h_now,
                 "absent": empty_home}
        steps = [{"name": n, "home": str(homes[n]), "project": str(projects[n]),
                  "prepare": prepare_args(projects[n])} for n in homes]
        steps[0]["override"] = str(override)
        out = self.drive(h_import, steps)
        self.assertEqual(out["override"]["resolved"], str(override),
                         msg=f"PC-2: el override explícito vence a activación y HOME: {out!r}")
        self.assertEqual(out["activation"]["resolved"],
                         str(adopted.joinpath(*AGENTS_SUBDIR)),
                         msg=f"PC-2: la activación vence a HOME: {out!r}")
        self.assertEqual(out["fallback"]["resolved"], str(h_now.joinpath(*AGENTS_SUBDIR)),
                         msg=f"PC-2: sin override ni activación, HOME vigente: {out!r}")
        self.assertEqual(out["absent"]["resolved"],
                         str(empty_home.joinpath(*AGENTS_SUBDIR)),
                         msg=f"PC-2: origen ausente conserva la ruta contractual del HOME vigente: {out!r}")
        # Consumo real del origen: cada variante publica los bytes de su nivel.
        self.assertEqual((out["override"]["rc"], self.published_markers(projects["override"])),
                         (0, ["PC2-MARKER-ovr"]),
                         msg=f"PC-2: prepare consume los agentes del override: {out!r}")
        self.assertEqual((out["activation"]["rc"],
                          self.published_markers(projects["activation"])),
                         (0, ["PC2-MARKER-act"]),
                         msg=f"PC-2: prepare consume los agentes adoptados: {out!r}")
        self.assertEqual((out["fallback"]["rc"], self.published_markers(projects["fallback"])),
                         (0, ["PC2-MARKER-now"]),
                         msg=f"PC-2: prepare consume los agentes del HOME vigente: {out!r}")
        # Contrato existente (004-002 R9): rc 0 + aviso por stderr, sin derivados.
        self.assertEqual(out["absent"]["rc"], 0,
                         msg=f"PC-2: origen ausente conserva rc 0 (R9): {out!r}")
        self.assertRegex(out["absent"]["stderr"], r"deriv|agent",
                         msg=f"PC-2: origen ausente avisa que no publicó derivados: {out!r}")
        self.assertEqual(sorted((projects["absent"] / ".opencode" / "agents").glob("cdad-*.md")),
                         [], msg="PC-2: origen ausente no publica agentes")


# ---------------------------------------------------------------- PC-3


class TestPC3Overrides(NestedRunCase):

    def test_pc3_inherited_overrides_neutralized_per_aj2(self) -> None:
        decoy = self.base / "decoy"
        decoy_agents = decoy.joinpath(*AGENTS_SUBDIR)
        decoy_agents.mkdir(parents=True)
        (decoy_agents / "cdad-orchestrator.md").write_bytes(b"DECOY-AGENT-MARKER\n")
        (decoy / "meter.sqlite").write_bytes(b"DECOY-STORE")
        before = inventory(decoy)
        project = build_project(self.base / "proj")
        (project / POLICY_REL).write_text(json.dumps(POLICY_DOC, indent=2) + "\n")
        env = self.parent_env(
            CDAD_INSTALL_ROOT=str(decoy),
            CDAD_OPENCODE_AGENTS_DIR=str(decoy_agents),
            CDAD_CONTEXT_METER_STORE=str(decoy / "meter.sqlite"),
            CDAD_TEST_PROJECT=str(project),
            CDAD_TEST_PREPARE_ARGS=json.dumps(prepare_args(project)),
            **PRESERVED)
        proc = self.run_inner(INNER_PC3, env)
        self.assertEqual(proc.returncode, 0,
                         msg=f"PC-3: la corrida anidada debe pasar\n{proc.stdout}{proc.stderr}")
        view = self.report("pc3")["cdad"]
        self.assertEqual({k: view[k] for k in RETIRED}, dict.fromkeys(RETIRED),
                         msg=f"PC-3/AJ2: overrides desviantes heredados se retiran: {view!r}")
        self.assertEqual({k: view[k] for k in PRESERVED}, PRESERVED,
                         msg=f"PC-3/AJ2: destino, límite y CDAD_TEST_* se conservan: {view!r}")
        self.assertEqual(self.report("pc3-prepare")["decoy_seen"], [],
                         msg="PC-3: prepare no consume agentes del señuelo heredado")
        cfg = self.report("pc3-config")
        isolated_xdg = cfg["isolated_xdg"]
        self.assertEqual(os.path.commonpath([cfg["inherited"], isolated_xdg]), isolated_xdg,
                         msg=f"PC-3: cdad_config_dir ignora el CDAD_INSTALL_ROOT heredado "
                             f"y resuelve bajo el XDG aislado: {cfg!r}")
        self.assertEqual(os.path.commonpath([cfg["local"], cfg["synthetic"]]), cfg["synthetic"],
                         msg=f"PC-3: el override local de CDAD_INSTALL_ROOT rige: {cfg!r}")
        meter = self.report("pc3-meter")
        self.assertNotEqual(meter["inherited_rc"], 0,
                            msg=f"PC-3: sin store propio el medidor falla cerrado: {meter!r}")
        self.assertIn("CDAD_CONTEXT_METER_STORE", meter["inherited_err"],
                      msg=f"PC-3: el diagnóstico nombra el insumo faltante: {meter!r}")
        self.assertNotIn(str(decoy), meter["inherited_err"],
                         msg=f"PC-3: el medidor no consume el store señuelo: {meter!r}")
        self.assertEqual(meter["local_rc"], 0,
                         msg=f"PC-3: el override local del store rige: {meter!r}")
        self.assertEqual(inventory(decoy), before,
                         msg="PC-3: el señuelo (store/instalación) queda intacto")

    def test_pc3_real_acceptances_stay_skipped_without_vars(self) -> None:
        env = os.environ.copy()
        env.update({k: "" for k in REAL_ACCEPTANCE_VARS})
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider",
             "tests/test_005_002_t4_acceptance.py", "-k", "c5_sboot04"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
            stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(proc.returncode, 0,
                         msg=f"PC-3: la aceptación real sin variables no falla\n{proc.stdout}")
        self.assertIn("1 skipped", proc.stdout,
                      msg=f"PC-3: sin variables la aceptación real queda skip\n{proc.stdout}")
        self.assertIn("CDAD_CONTEXT_METER_REAL_STORE", proc.stdout,
                      msg="PC-3: el diagnóstico del skip nombra la variable faltante")


# ---------------------------------------------------------------- PC-4


class TestPC4Canary(NestedRunCase):

    def test_pc4_writes_confined_external_home_unchanged(self) -> None:
        before = inventory(self.ext_home)
        proc = self.run_inner(INNER_PC4, self.parent_env())
        self.assertEqual(proc.returncode, 0,
                         msg=f"PC-4: corrida válida rc=0\n{proc.stdout}{proc.stderr}")
        w = self.report("w")
        for name in ("setupclass", "module"):
            seen = self.report("early-" + name)
            self.assertEqual(
                ([k for k in MANAGED
                  if os.path.commonpath([seen[k], str(self.base)]) == str(self.base)],
                 {k: seen[k] for k in RETIRED}),
                ([], dict.fromkeys(RETIRED)),
                msg=f"PC-4/I1: {name} corre bajo la raíz de sesión, no la del operador: {seen!r}")
        self.assertEqual(inventory(self.ext_home), before,
                         msg="PC-4: inventario+mtime_ns del HOME externo sin diferencias")
        self.assertNotEqual(os.path.commonpath([w["marker"], str(self.ext_home)]),
                            str(self.ext_home),
                            msg=f"PC-4: el marcador {w['marker']!r} quedó bajo la raíz aislada")

    def test_pc4_canary_detects_deliberate_external_write(self) -> None:
        before = inventory(self.ext_home)
        proc = self.run_inner(INNER_PC4_NEG, self.parent_env())
        self.assertEqual(proc.returncode, 0,
                         msg=f"PC-4 (control -): la corrida termina rc=0\n{proc.stdout}{proc.stderr}")
        after = inventory(self.ext_home)
        self.assertIn("escaped", sorted(set(after) - set(before)),
                         msg=f"PC-4 (control -): el canario detecta exactamente la escritura "
                             f"deliberada fuera de la raíz aislada: {sorted(set(after) - set(before))!r}")


# ---------------------------------------------------------------- PC-5


class TestPC5Restore(NestedRunCase):

    def assert_restored(self, preset: str, **overrides: str) -> None:
        env = self.parent_env(CDAD_TEST_PRESET_TEMPDIR=preset, **overrides)
        for key in RETIRED:
            if key not in overrides:
                env.pop(key, None)
        proc = self.run_inner(INNER_PC5, env)
        self.assertEqual(proc.returncode, 1,
                         msg=f"PC-5: el fallo deliberado da rc=1 (no error de fixture)\n{proc.stdout}")
        self.assertIn("1 failed, 1 passed", proc.stdout,
                      msg=f"PC-5: un fallo deliberado y un pase, sin errors\n{proc.stdout}")
        log = json.loads(self.log.read_text())
        session = log["session"]
        self.assertEqual({k: session["env"][k] for k in RETIRED},
                         {k: overrides.get(k) for k in RETIRED},
                         msg=f"PC-5: el snapshot de sesión registra los overrides "
                             f"retirados con su presencia y valor: {session!r}")
        # La fixture de sesión (I1) rige entre tests: cada test devuelve el
        # nivel de sesión exacto, y el cierre de sesión devuelve el heredado.
        level = log["before::test_passes"]
        self.assertEqual(log["after::test_fails_deliberately"], level,
                         msg="PC-5: tras el test fallido entorno y tempdir vuelven exactos")
        # El último test cierra también la fixture de sesión: vuelve al heredado.
        self.assertEqual(log["after::test_passes"], session,
                         msg="PC-5: tras el test satisfactorio entorno y tempdir vuelven exactos")
        self.assertEqual(
            ([k for k in MANAGED
              if os.path.commonpath([level["env"][k], str(self.base)]) == str(self.base)],
             {k: level["env"][k] for k in RETIRED}),
            ([], dict.fromkeys(RETIRED)),
            msg=f"PC-5/I1: entre tests (setUpClass, fixtures de módulo) rige la raíz "
                f"de sesión, no el HOME/TMP/overrides del operador: {level!r}")
        self.assertEqual(log["sessionfinish"], session,
                         msg="PC-5: al cerrar la sesión entorno y tempdir vuelven a los heredados")
        f = self.report("f")
        self.assertNotEqual(f["env"]["HOME"], session["env"]["HOME"],
                            msg="PC-5: durante el test el HOME era el aislado, no el heredado")
        self.assertFalse(Path(common_root(f["env"])).exists(),
                         msg="PC-5: la raíz descartable se retira al terminar")
        sleeper = self.report("sleeper")
        self.assertEqual((sleeper["returncode"] is not None,
                          sleeper["home_existed_at_kill"]), (True, True),
                         msg=f"PC-5: el proceso del fixture terminó con la raíz aún presente: {sleeper!r}")

    def test_pc5_restores_env_and_tempdir_after_failure(self) -> None:
        self.assert_restored("")
        self.assert_restored(str(self.ext_tmp),
                             **{k: str(self.base / ("decoy-" + k)) for k in RETIRED})


if __name__ == "__main__":
    unittest.main()
