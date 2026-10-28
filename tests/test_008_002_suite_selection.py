"""008-002 T3 RED — selector canónico de suite por capacidad (scripts/cdad-suite.py).

Deriva de docs/specs/008-002-suite-by-capability/spec.md (§4, §5, §6 PC-1,
PC-2, PC-3 estructural, PC-5, PC-7). Cada caso opera sobre un repositorio git
sintético en tmp: copia del CLI en ``scripts/cdad-suite.py``, tests mínimos
que escriben marcadores en ``$CDAD_SUITE_MARKERS`` y artefactos sintéticos
bajo ``docs/specs/008-002-suite-by-capability/``. El checkout real no se toca.

Supuestos de interfaz declarados (la spec no fija esos detalles):
- el CLI se invoca con cwd = raíz del repositorio a validar;
- asignación de módulo completo: ``{"capability", "contract", "scope": "module"}``
  (forma del inventario T2); un test en varias capacidades = varias asignaciones;
- ``list`` emite JSON: lista de nodeids o un objeto con clave ``nodeids``;
- ``timing-disposition.json``: ``target_ceiling_s``, ``effective_threshold_s``,
  ``status`` (``pending``/``resolved``), ``evidence`` (lista de referencias),
  ``reason_5s_not_2s``, ``resolution_criterion`` y ``cases``;
- desaparición de obligación: entrada ``acreditada`` presente en el pc-map de
  HEAD y ausente del árbol de trabajo.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "scripts" / "cdad-suite.py"
SPEC_DIR = "docs/specs/008-002-suite-by-capability"
CONTRACT = "docs/specs/999-synthetic/spec.md"

CAPS = [
    "delivery-evidence", "continuity", "dispatch-recovery",
    "orientation-planning", "suspension", "retirement",
    "packets-authority-identity", "generation-install-permissions",
    "suite-isolation",
]


def _test_src(name, fail=False):
    return (
        "import os, pathlib\n\n"
        f"def test_{name}():\n"
        "    d = pathlib.Path(os.environ['CDAD_SUITE_MARKERS'])\n"
        f"    (d / '{name}').write_text('ran')\n"
        f"    assert {not fail}\n"
    )


def _module(path, caps, kind="test"):
    return {
        "path": path,
        "kind": kind,
        "assignments": [
            {"capability": c, "contract": CONTRACT, "scope": "module"} for c in caps
        ],
        "decision": "mantener",
        "rationale": "sintetico",
        "targets": [],
        "product_surfaces": [],
        "helper_dependencies": [],
    }


def _disposition(**over):
    d = {
        "schema_version": 1,
        "target_ceiling_s": 2,
        "effective_threshold_s": 5,
        "status": "pending",
        "evidence": [],
        "measurement_scope": "sintetico",
        "reason_5s_not_2s": "la cota instrumental de 5s no mide un techo de 2s",
        "resolution_criterion": "medicion propia del techo de 2s",
        "epic_debt": "epic-008-suite-coherence",
        "cases": ["tests/test_a.py::test_a"],
    }
    d.update(over)
    return d


def _entry(original, target, decision="mantener", status="acreditada"):
    return {
        "contract": {"spec": CONTRACT, "id": "PC-1"},
        "accreditation_source": f"{CONTRACT}:1",
        "amendment": None,
        "status": status,
        "original_nodeid": original,
        "variant_observable": "marcador escrito",
        "target_nodeid": target,
        "decision": decision,
        "equivalence_justification": "sintetico",
    }


def _git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


class Synth:
    def __init__(self, tmp_path):
        self.root = tmp_path / "repo"
        self.markers = tmp_path / "markers"
        self.markers.mkdir()
        (self.root / "scripts").mkdir(parents=True)
        if CLI.is_file():
            shutil.copy2(CLI, self.root / "scripts" / "cdad-suite.py")
        (self.root / "tests").mkdir()
        (self.root / Path(CONTRACT).parent).mkdir(parents=True)
        (self.root / CONTRACT).write_text("# sintetico\n")
        self.tests = {
            "a": (["continuity"], False),
            "b": (["continuity", "suspension"], False),
            "c": (["retirement"], False),
        }
        self.modules = None
        self.entries = None
        self.disposition = _disposition()
        _git(self.root, "init", "-q")

    def write_tests(self):
        for n, (_, fail) in self.tests.items():
            (self.root / "tests" / f"test_{n}.py").write_text(_test_src(n, fail))

    def write_artifacts(self):
        d = self.root / SPEC_DIR
        d.mkdir(parents=True, exist_ok=True)
        modules = self.modules if self.modules is not None else [
            _module(f"tests/test_{n}.py", caps) for n, (caps, _) in self.tests.items()
        ]
        entries = self.entries if self.entries is not None else [
            _entry(f"tests/test_{n}.py::test_{n}", f"tests/test_{n}.py::test_{n}")
            for n in self.tests
        ]
        inv = {"schema_version": 1, "feature_id": "008-002-suite-by-capability",
               "capabilities": CAPS, "modules": sorted(modules, key=lambda m: m["path"])}
        (d / "suite-inventory.json").write_text(json.dumps(inv, indent=2))
        (d / "pc-map.json").write_text(json.dumps({"schema_version": 1, "entries": entries}, indent=2))
        if self.disposition is not None:
            (d / "timing-disposition.json").write_text(json.dumps(self.disposition, indent=2))
        elif (d / "timing-disposition.json").exists():
            (d / "timing-disposition.json").unlink()

    def build(self):
        self.write_tests()
        self.write_artifacts()
        return self

    def commit(self, msg="base"):
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", msg)

    def cli(self, *args):
        assert CLI.is_file(), f"CLI ausente: {CLI} no existe (008-002 T3 sin implementar)"
        env = {**os.environ, "CDAD_SUITE_MARKERS": str(self.markers)}
        p = subprocess.run([sys.executable, "scripts/cdad-suite.py", *args], cwd=self.root,
                           capture_output=True, text=True, env=env, timeout=120)
        return p.returncode, p.stdout + p.stderr, p.stdout

    def ran(self):
        return sorted(p.name for p in self.markers.iterdir())


@pytest.fixture
def synth(tmp_path):
    return Synth(tmp_path)


def _nodeids(stdout):
    data = json.loads(stdout)
    if isinstance(data, dict):
        data = data["nodeids"]
    return data


# PC-1 -----------------------------------------------------------------------

def test_pc1_validate_ok_with_complete_inventory(synth):
    synth.build()
    rc, out, _ = synth.cli("validate")
    assert rc == 0, out


def test_pc1_validate_rejects_omitted_module(synth):
    synth.build()
    synth.modules = [_module("tests/test_a.py", ["continuity"]),
                     _module("tests/test_b.py", ["continuity"])]
    synth.write_artifacts()
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "tests/test_c.py" in out, out


def test_pc1_validate_rejects_nonexistent_nodeid(synth):
    synth.build()
    synth.entries = [_entry("tests/test_a.py::test_a", "tests/test_a.py::test_a"),
                     _entry("tests/test_b.py::test_b", "tests/test_b.py::test_b"),
                     _entry("tests/test_c.py::test_c", "tests/test_c.py::test_c"),
                     _entry("tests/test_a.py::test_ghost", "tests/test_a.py::test_ghost")]
    synth.write_artifacts()
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "test_ghost" in out, out


def test_pc1_validate_rejects_unknown_capability(synth):
    synth.tests["c"] = (["teleportation"], False)
    synth.build()
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "teleportation" in out, out


# PC-2 -----------------------------------------------------------------------

def test_pc2_list_returns_exact_sorted_unique_selection(synth):
    synth.build()
    rc, out, stdout = synth.cli("list", "--capability", "continuity")
    assert rc == 0, out
    ids = _nodeids(stdout)
    assert ids == ["tests/test_a.py::test_a", "tests/test_b.py::test_b"], ids
    rc, out, stdout = synth.cli("list", "--capability", "suspension")
    assert rc == 0 and _nodeids(stdout) == ["tests/test_b.py::test_b"], out


def test_pc2_run_executes_only_selection(synth):
    synth.build()
    rc, out, _ = synth.cli("run", "--capability", "continuity")
    assert rc == 0, out
    assert synth.ran() == ["a", "b"], (synth.ran(), out)


def test_pc2_run_propagates_selected_failure(synth):
    synth.tests["b"] = (["continuity"], True)
    synth.build()
    rc, out, _ = synth.cli("run", "--capability", "continuity")
    assert rc != 0, out
    assert "c" not in synth.ran(), synth.ran()


# PC-3 estructural -----------------------------------------------------------

def test_pc3_validate_rejects_missing_target(synth):
    synth.build()
    synth.entries = [_entry("tests/test_a.py::test_a", "tests/test_a.py::test_a"),
                     _entry("tests/test_b.py::test_b", "tests/test_b.py::test_b"),
                     _entry("tests/test_c.py::test_c", "tests/test_gone.py::test_gone",
                            decision="fusionar")]
    synth.write_artifacts()
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "test_gone" in out, out


def test_pc3_validate_rejects_disappeared_accredited_obligation(synth):
    synth.build()
    synth.commit()
    synth.entries = [_entry("tests/test_a.py::test_a", "tests/test_a.py::test_a"),
                     _entry("tests/test_b.py::test_b", "tests/test_b.py::test_b")]
    synth.write_artifacts()
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "test_c" in out, out


def test_pc3_validate_rejects_elimination_with_pending_verify(synth):
    synth.build()
    synth.entries = [_entry("tests/test_a.py::test_a", "tests/test_a.py::test_a"),
                     _entry("tests/test_b.py::test_b", "tests/test_b.py::test_b"),
                     _entry("tests/test_c.py::test_c", "tests/test_a.py::test_a",
                            decision="eliminar", status="VERIFY")]
    synth.write_artifacts()
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "VERIFY" in out, out


# PC-5 -----------------------------------------------------------------------

def test_pc5_surface_selects_uncommitted_test_only_change(synth):
    synth.build()
    synth.commit()
    (synth.root / "tests" / "test_b.py").write_text(_test_src("b", fail=True))
    rc, out, _ = synth.cli("surface", "--base", "HEAD")
    assert rc != 0, out
    assert synth.ran() == ["b"], (synth.ran(), out)


def test_pc5_surface_base_without_inventory_fails(synth):
    synth.write_tests()
    synth.commit()
    synth.write_artifacts()
    rc, out, _ = synth.cli("surface", "--base", "HEAD")
    assert rc != 0, out
    low = out.lower()
    assert "invent" in low or "pc-map" in low or "mapa" in low, out


def test_pc5_surface_all_explicit_selects_everything(synth):
    synth.tests["c"] = (["retirement"], True)
    synth.write_tests()
    synth.commit()
    synth.write_artifacts()
    rc, out, _ = synth.cli("surface", "--base", "HEAD", "--all")
    assert synth.ran() == ["a", "b", "c"], (synth.ran(), out)
    assert rc != 0, out


# PC-7 -----------------------------------------------------------------------

def test_pc7_validate_rejects_missing_timing_disposition(synth):
    synth.disposition = None
    synth.build()
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "timing-disposition" in out, out


def test_pc7_validate_rejects_resolved_without_evidence(synth):
    synth.disposition = _disposition(status="resolved", evidence=[])
    synth.build()
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "timing-disposition" in out, out


# T3 RED segunda vuelta (review-t3.md BLOCKING 1-3) ---------------------------
#
# Supuestos de interfaz adicionales declarados:
# - asignación por nodeids (módulo mixto):
#   ``{"capability", "contract", "scope": "nodeids", "nodeids": [...]}``;
# - ``helper_dependencies`` nombra el módulo helper por su stem (forma del
#   inventario T2), ``product_surfaces`` por ruta relativa;
# - baseline de PC-3 (decisión del orquestador): ``validate`` compara el
#   pc-map contra la revisión ``commit`` de ``measurement-before.json``.

def _multi_src(*names):
    body = "import os, pathlib\n"
    for n in names:
        body += (f"\n\ndef test_{n}():\n"
                 "    d = pathlib.Path(os.environ['CDAD_SUITE_MARKERS'])\n"
                 f"    (d / '{n}').write_text('ran')\n")
    return body


def _nodeids_assignment(cap, nodeids):
    return {"capability": cap, "contract": CONTRACT, "scope": "nodeids",
            "nodeids": nodeids}


def _mixed(synth, assignments):
    synth.write_tests()
    (synth.root / "tests" / "test_m.py").write_text(_multi_src("m1", "m2"))
    mods = [_module(f"tests/test_{n}.py", caps) for n, (caps, _) in synth.tests.items()]
    m = _module("tests/test_m.py", [])
    m["assignments"] = assignments
    synth.modules = mods + [m]
    synth.entries = [_entry(f"tests/test_{n}.py::test_{n}", f"tests/test_{n}.py::test_{n}")
                     for n in synth.tests]
    synth.write_artifacts()


# PC-1

def test_pc1_validate_rejects_incomplete_mixed_assignment(synth):
    _mixed(synth, [_nodeids_assignment("continuity", ["tests/test_m.py::test_m1"])])
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "test_m2" in out, out


def test_pc1_validate_rejects_nonexistent_inventory_nodeid(synth):
    _mixed(synth, [_nodeids_assignment("continuity", ["tests/test_m.py::test_m1"]),
                   _nodeids_assignment("retirement", ["tests/test_m.py::test_m2",
                                                      "tests/test_m.py::test_ghost"])])
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "test_ghost" in out, out


# PC-2

def test_pc2_mixed_module_selects_exact_nodeids(synth):
    _mixed(synth, [_nodeids_assignment("continuity", ["tests/test_m.py::test_m1"]),
                   _nodeids_assignment("retirement", ["tests/test_m.py::test_m2"])])
    rc, out, _ = synth.cli("validate")
    assert rc == 0, out
    rc, out, stdout = synth.cli("list", "--capability", "continuity")
    assert rc == 0, out
    assert _nodeids(stdout) == ["tests/test_a.py::test_a", "tests/test_b.py::test_b",
                                "tests/test_m.py::test_m1"], out
    rc, out, stdout = synth.cli("list", "--capability", "retirement")
    assert rc == 0 and _nodeids(stdout) == ["tests/test_c.py::test_c",
                                            "tests/test_m.py::test_m2"], out


# PC-3 contra baseline

def _write_baseline(synth, commit):
    (synth.root / SPEC_DIR / "measurement-before.json").write_text(
        json.dumps({"commit": commit, "files": []}, indent=2))


def test_pc3_validate_rejects_committed_disappearance_vs_baseline(synth):
    synth.build()
    synth.commit("baseline")
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=synth.root, check=True,
                         capture_output=True, text=True).stdout.strip()
    _write_baseline(synth, sha)
    synth.commit("measurement-before")
    rc, out, _ = synth.cli("validate")
    assert rc == 0, out
    synth.entries = [_entry("tests/test_a.py::test_a", "tests/test_a.py::test_a"),
                     _entry("tests/test_b.py::test_b", "tests/test_b.py::test_b")]
    synth.write_artifacts()
    synth.commit("borra obligacion acreditada")
    rc, out, _ = synth.cli("validate")
    assert rc != 0 and "test_c" in out, out


# PC-5 variantes

def test_pc5_surface_selects_new_untracked_test(synth):
    synth.build()
    synth.commit()
    (synth.root / "tests" / "test_d.py").write_text(_test_src("d", fail=True))
    rc, out, _ = synth.cli("surface", "--base", "HEAD")
    assert "d" in synth.ran() and "a" not in synth.ran(), (synth.ran(), out)
    assert rc != 0, out


def test_pc5_surface_deleted_test_selects_declared_substitute(synth):
    synth.build()
    synth.entries = [_entry("tests/test_a.py::test_a", "tests/test_a.py::test_a"),
                     _entry("tests/test_b.py::test_b", "tests/test_b.py::test_b"),
                     _entry("tests/test_c.py::test_c", "tests/test_a.py::test_a",
                            decision="fusionar")]
    synth.write_artifacts()
    synth.commit()
    _git(synth.root, "rm", "-q", "tests/test_c.py")
    _git(synth.root, "commit", "-q", "-m", "elimina c")
    rc, out, _ = synth.cli("surface", "--base", "HEAD~1")
    assert "a" in synth.ran(), (synth.ran(), out)


def test_pc5_surface_moved_test_selects_base_map_targets(synth):
    synth.build()
    synth.entries = [_entry("tests/test_a.py::test_a", "tests/test_a.py::test_a"),
                     _entry("tests/test_b.py::test_b", "tests/test_b.py::test_b"),
                     _entry("tests/test_c.py::test_c", "tests/test_a.py::test_a",
                            decision="fusionar")]
    synth.write_artifacts()
    synth.commit()
    _git(synth.root, "mv", "tests/test_c.py", "tests/test_moved.py")
    rc, out, _ = synth.cli("surface", "--base", "HEAD")
    assert "a" in synth.ran(), (synth.ran(), out)


def test_pc5_surface_helper_change_selects_declared_consumers(synth):
    synth.write_tests()
    (synth.root / "tests" / "shared_helper.py").write_text("X = 1\n")
    mods = [_module(f"tests/test_{n}.py", caps) for n, (caps, _) in synth.tests.items()]
    mods[1]["helper_dependencies"] = ["shared_helper"]
    synth.modules = mods + [_module("tests/shared_helper.py", ["continuity"], kind="helper")]
    synth.write_artifacts()
    synth.commit()
    (synth.root / "tests" / "shared_helper.py").write_text("X = 2\n")
    rc, out, _ = synth.cli("surface", "--base", "HEAD")
    assert rc == 0, out
    assert synth.ran() == ["b"], (synth.ran(), out)


def test_pc5_surface_product_change_selects_surface_assignments(synth):
    synth.write_tests()
    (synth.root / "scripts" / "prod.py").write_text("V = 1\n")
    mods = [_module(f"tests/test_{n}.py", caps) for n, (caps, _) in synth.tests.items()]
    mods[2]["product_surfaces"] = ["scripts/prod.py"]
    synth.modules = mods
    synth.write_artifacts()
    synth.commit()
    (synth.root / "scripts" / "prod.py").write_text("V = 2\n")
    rc, out, _ = synth.cli("surface", "--base", "HEAD")
    assert rc == 0, out
    assert synth.ran() == ["c"], (synth.ran(), out)


def test_pc5_surface_selector_change_selects_everything(synth):
    synth.build()
    synth.commit()
    cli = synth.root / "scripts" / "cdad-suite.py"
    if cli.is_file():
        cli.write_text(cli.read_text() + "\n# cambio sintetico del selector\n")
    rc, out, _ = synth.cli("surface", "--base", "HEAD")
    assert rc == 0, out
    assert synth.ran() == ["a", "b", "c"], (synth.ran(), out)
