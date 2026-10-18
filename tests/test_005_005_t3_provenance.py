#!/usr/bin/env python3
"""005-005 T3 RED — procedencia de la instalación (PD-12..PD-15, INV-7).

Contract:
- docs/specs/005-005-adoption-coherence/spec.md §2 «Registros y artefactos»
  y PD-12..PD-15, §3 INV-7, §6 T3, §7 D4/D5/D6.
- docs/epics/epic-005-real-operation/plan.md (T3; tabla «Cambios al plan»).

Superficie observable (proyectos sintéticos en tempdirs, fixture de raíces
adoptadas sintéticas, registro de activación sintético del PROYECTO):

    CDAD_OPENCODE_AGENTS_DIR=<opcional> \
      python3 scripts/cdad_packet.py prepare --project-root R \
        --role <rol> --substage <sub> --objective <encargo>   # sin flags nuevos

Caja negra: SOLO subprocess sobre el entrypoint del repo; el módulo NUNCA
se importa y el código de implementación NUNCA se lee (INV del rol).

Aislamiento (riesgo R7 del plan): NINGUNA corrida toca el HOME real ni
depende de una activación real — el HOME del subproceso siempre es un
tmpdir VACÍO (precedente de tests/test_003_006_t2_activation.py) y el
registro `.cdad/activation.json` es SIEMPRE sintético del fixture.

Fijaciones RED por postcondición (un test por postcondición; cada
negativo con control positivo interno, exigido por spec §4):

- PD-12 (origen resuelto): con `.cdad/activation.json` presente en el
  proyecto del fixture (formato `{adopted_root, manifest_sha256, paths}`)
  y SIN la variable `CDAD_OPENCODE_AGENTS_DIR`, un `prepare` publica los
  agentes de proyecto y el `source_dir` del manifiesto
  `.opencode/agents/.cdad-derived.json` es la carpeta de agentes de la
  raíz adoptada REGISTRADA (`<adopted_root>/.config/opencode/agents`),
  no la global de HOME. HOY: prepare NO consulta el registro — con
  HOME vacío y sin variable no hay fuente y NO publica derivados; el
  RED fracasa en esa aserción de comportamiento. Control positivo
  interno: SIN activación, el camino vigente por la variable explícita
  (orden 1 del PD-12) sigue publicando con `source_dir` = la fuente
  declarada (camino vigente probado GREEN en 004-002 T5/T7).
- PD-13 (contradicción diagnosticada): cuando el origen resuelto difiere
  del registrado (variable apunta a OTRA instalación; brazo a) o del
  `source_dir` del manifiesto anterior (caso MIX-V6V7; brazo b),
  `prepare` emite en stderr un diagnóstico que nombra `.cdad/activation.json`
  y la(s) versión(es)/commit en juego (los tags deterministas de las
  raíces `cdad-adopted-<tag>` del fixture); HOY re-deriva o avisa SIN
  nombrar el registro ni las versiones (MIX-V6V7 real:
  dispatch-ledger.md:84-101). Control positivo interno (coherencia):
  origen resuelto == registrado → sin diagnóstico de contradicción.
  Se aserta rc=0 porque el diagnóstico "dice cuál usaría y cómo
  resolverlo": la publicación continúa CON el aviso (INV-7).
- PD-14 (versión verificable): el manifiesto (y/o cada agente publicado)
  declara la versión/commit de la instalación de origen. Fixture (las DOS
  opciones del paquete): raíz adoptada con el patrón de nombre
  `cdad-adopted-<tag>` (tag = sha determinista de 8 hex) Y un marcador de
  versión en la raíz (`version.txt` con el sha COMPLETO del commit,
  no deducible de ruta alguna). Con el origen explícito y coherente
  (variable == registro) el artefacto sí se publica y se lee: el fallo
  RED es exactamente la ausencia de la declaración de versión (hoy el
  manifiesto sólo lleva `source_dir` + hashes y los derivados no
  declaran versión).
- PD-15 (documental, SIN test de comportamiento): la recarga y la
  procedencia del runtime están documentadas. Dueño original:
  `skills/cdad-cycle/references/opencode-delegation.md`; **reformulado por
  006-002 U3 (PD-9)**: esa referencia sale del árbol instalable y su detalle
  histórico/verificación (recarga y versión, canal `delegate`, 429,
  procedencia) se conserva como evidencia **no instalable** bajo `docs/**`
  (el oráculo de esa preservación es 006-002 U3,
  `tests/test_006_002_u3_runtime_references.py`). NO se aserta con código en
  este módulo — queda para la evidencia por grep del audit/review (la
  metodología lo lee de documents, no de un oráculo). Nota de mapeo:
  PD-15 ← evidencia documental, no test.

Mapa test → postcondición:
  test_pd12_prepare_resolves_origin_from_registered_adoption_without_env_var
    -> PD-12 (+ control: orden 1 explicit variable, camino vigente)
  test_pd13_contradiction_diagnosed_names_registry_and_versions
    -> PD-13 (brazo a: variable vs registro; brazo b: MIX-V6V7
       manifiesto anterior) + control de coherencia + INV-7
  test_pd14_version_declared_in_published_artifact
    -> PD-14 (+ control: el artefacto publicado es legible)
  (PD-15: mapeada a evidencia por grep, sin test — comentario arriba)

Todo fallo RED es AssertionError de comportamiento de superficie
observable; nunca ImportError, nunca traceback del CLI. Los agentes
`agents/cdad-*.md` se COPIAN sin inspección (fixture, precedente
004-002 T5 §fixtures: «copiada sin inspección: es fixture, no lectura
de implementación»). Las helpers de bootstrap se reutilizan del módulo
compartido test_004_002_t2_bootstrap (patrón 004-002 T5/T7: importados,
no redefinidos). Ninguna escritura en este repo.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (  # noqa: E402
    REPO_ROOT,
    SCRIPT,
    build_project,
    prepare_args,
    read_state,
    write_state,
)

AGENTS_ENV = "CDAD_OPENCODE_AGENTS_DIR"
DERIVED_DIR = ".opencode/agents"
MANIFEST = ".cdad-derived.json"
REGISTRY = ".cdad/activation.json"
POLICY_REL = "docs/cdad-policy.json"
AGENTS_SUBDIR = (".config", "opencode", "agents")

# Política del layout CDAD (igual a la real de este repo; fixture probado
# para la derivación en 004-002 T5/T7, layout "cdad").
POLICY_DOC = {
    "schema_version": 1,
    "path_policy": {
        "test_roots": ["tests"],
        "implementation_roots": ["agents", "skills", "scripts",
                                 "sources", "build"],
        "implementation_files": ["install.sh"],
        "documentation_roots": ["docs"],
        "colocated_test_roots": ["scripts", "agents"],
        "colocated_test_prefixes": ["test_"],
        "colocated_test_suffixes": ["_test.py"],
    },
    "temporary_roots": [".cdad/tmp"],
}

LAYOUT_FILES = ("scripts/x.py", "scripts/test_h.py", "agents/y.md",
                "agents/test_y.md", "tests/test_a.py", "install.sh")


# ---------------------------------------------------------------- helpers


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tag(label: str) -> str:
    """Tag determinista de 8 hex (la «versión» del fixture)."""
    return hashlib.sha256(f"cdad-fixture-{label}".encode()).hexdigest()[:8]


def make_adopted_root(base: Path, label: str) -> Path:
    """Raíz adoptada sintética `cdad-adopted-<tag>` con la carpeta de
    agentes del runtime (<A>/.config/opencode/agents) poblada por COPIA
    sin inspección de agents/cdad-*.md (fixture, precedent 004-002 T5) y
    un instalador manifest sintético (.cdad-install-manifest.json) con
    los sha256 correctos, del que derivará `manifest_sha256` del registro."""
    a = base / "adopted" / f"cdad-adopted-{_tag(label)}"
    agents_dir = a.joinpath(*AGENTS_SUBDIR)
    agents_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(REPO_ROOT.glob("agents/cdad-*.md")):
        shutil.copy2(src, agents_dir / src.name)  # copy WITHOUT reading
    # Marcador de versión de la instalación (paquete objetivo PD-14: «un
    # marcador de versión en la raíz»): sha COMPLETO determinista, que NO
    # es deducible de ninguna ruta publicada (el tag del nombre es de 8
    # hex; el commit observable es de 64).
    version_sha = hashlib.sha256(f"commit-{label}".encode()).hexdigest()
    (a / "version.txt").write_text(version_sha + "\n")
    manifest_artifacts = {}
    for p in sorted(agents_dir.glob("cdad-*.md")):
        rel = (Path(*AGENTS_SUBDIR) / p.name).as_posix()
        manifest_artifacts[rel] = {
            "sha256": _sha256_bytes(p.read_bytes()),
            "source": f"sources/{rel}",
        }
    manifest = {
        "manifest_version": 1,
        "artifacts": manifest_artifacts,
        "conflicts": [],
        "installer": "install.sh (synthetic)",
        "pending_removal": [],
        "profile": "synthetic",
        "runtime": "opencode",
        "stack": "generic",
    }
    (a / ".cdad-install-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return a


def read_manifest(root: Path) -> Path:
    return root / DERIVED_DIR / MANIFEST


def published_agents(root: Path) -> dict[str, str]:
    out = {}
    manifest_path = root / DERIVED_DIR / MANIFEST
    if not manifest_path.is_file():
        return out
    for p in sorted((root / DERIVED_DIR).glob("cdad-*.md")):
        out[p.name] = p.read_text(encoding="utf-8")
    return out


def source_tag(adopted: Path) -> str:
    return adopted.name.replace("cdad-adopted-", "")


def source_version(adopted: Path) -> str:
    """Versión/commit del origen (marcador de versión en la raíz del
    fixture; PD-14): sha completo determinista observable."""
    return (adopted / "version.txt").read_text(encoding="utf-8").strip()


# ---------------------------------------------------------------- base


class ProvenanceCase(unittest.TestCase):
    """Base: proyecto sintético + settings aislados en su propio tempdir
    (HOME del subproceso vacío, registro de activación sintético)."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-005-t3-")
        self.addCleanup(lambda: subprocess.run(
            ["rm", "-rf", self._tmp], check=False))
        self.base = Path(self._tmp)

    def make_project(self, name: str = "proj") -> Path:
        root = build_project(self.base / name)
        (root / POLICY_REL).write_text(
            json.dumps(POLICY_DOC, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        for rel in LAYOUT_FILES:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# fixture {rel}\n", encoding="utf-8")
        return root

    def make_adopted_root(self, label: str) -> Path:
        return make_adopted_root(self.base, label)

    def make_home(self, label: str = "home") -> Path:
        home = self.base / f"home-{label}"
        home.mkdir(parents=True, exist_ok=True)
        return home

    def write_registry(self, root: Path, adopted: Path) -> dict:
        """Registro de activación sintético (contrato §2): `{adopted_root,
        manifest_sha256, paths}` con los shas del fixture."""
        manifest_path = adopted / ".cdad-install-manifest.json"
        manifest_sha = _sha256_bytes(manifest_path.read_bytes())
        agents_dir = adopted.joinpath(*AGENTS_SUBDIR)
        paths = {
            (Path(*AGENTS_SUBDIR) / p.name).as_posix(): {
                "sha256": _sha256_bytes(p.read_bytes()),
                "type": "file",
            }
            for p in sorted(agents_dir.glob("cdad-*.md"))
        }
        paths[".cdad-install-manifest.json"] = {
            "sha256": manifest_sha, "type": "file"}
        doc = {
            "adopted_root": str(adopted),
            "manifest_sha256": manifest_sha,
            "paths": paths,
        }
        (root / ".cdad").mkdir(parents=True, exist_ok=True)
        (root / REGISTRY).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n")
        return doc

    def run_prepare(self, root: Path, *, agents_dir: Path | None,
                    home: Path, objective: str = "005-005 T3 procedencia"
                    ) -> subprocess.CompletedProcess:
        """prepare por subprocess. El HOME del subproceso SIEMPRE es un
        tmpdir vacío (R7: nunca HOME real); la variable de agentes se
        inyecta (agents_dir) o se QUITA (None)."""
        env = dict(os.environ)
        env["HOME"] = str(home)
        env.pop(AGENTS_ENV, None)
        if agents_dir is not None:
            env[AGENTS_ENV] = str(agents_dir)
        return subprocess.run(
            [sys.executable, str(SCRIPT),
             *prepare_args(root, role="test-writer", substage="red",
                           objective=objective)],
            capture_output=True, text=True, cwd=REPO_ROOT, env=env,
            stdin=subprocess.DEVNULL,
        )

    def mark_active_completed(self, root: Path) -> None:
        """El fixture actúa como ORQUESTADOR (precedente 004-002 T2/T5
        mark_active_packet): sin cerrar el paquete, un segundo prepare
        rechaza por PD-4 — el MOD se marca completed, el paquete activo
        y su manifiesto publicado permanecen en disco."""
        state = read_state(root)
        active = state.get("active_packet") or {}
        if not active.get("id"):
            raise AssertionError(
                f"fixture: sin active_packet id para completar: {active!r}")
        active["status"] = "completed"
        write_state(root, state)


# ---------------------------------------------------------------- PD-12


class TestPd12OriginFromActivationRegistry(ProvenanceCase):
    """PD-12 (fuente por defecto = registro de activación; INV-7): con
    `.cdad/activation.json` presente y SIN la variable, `prepare` publica
    los agentes de proyecto y el `source_dir` del manifiesto es la
    carpeta de agentes de la raíz adoptada REGISTRADA, no la global de
    HOME. Control positivo interno: sin activación, el camino vigente
    (variable explícita, orden 1) sigue funcionando."""

    def test_pd12_prepare_resolves_origin_from_registered_adoption_without_env_var(self) -> None:
        home = self.make_home("regist")
        registered = self.make_adopted_root("registered")
        root = self.make_project()
        self.write_registry(root, registered)
        expected_source = str(registered.joinpath(*AGENTS_SUBDIR))

        proc = self.run_prepare(root, agents_dir=None, home=home)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-12: el prepare del fixture (registro presente, sin "
                f"variable) debe correr: {proc.stdout!r} {proc.stderr!r}")

        manifest = read_manifest(root)
        self.assertTrue(
            manifest.is_file(),
            msg=f"PD-12: prepare NO publica los agentes de proyecto desde "
                f"la raíz adoptada REGISTRADA en {REGISTRY} (sin "
                f"{AGENTS_ENV} el origen cae en la instalación global/HOME "
                f"o en «sin fuente» — el registro de activación no se "
                f"consulta): falta {DERIVED_DIR}/{MANIFEST}; stderr: "
                f"{proc.stderr!r}")
        data = json.loads(manifest.read_text(encoding="utf-8"))
        source_dir = data.get("source_dir")
        self.assertEqual(
            source_dir, expected_source,
            msg=f"PD-12: el source_dir del manifiesto publicado es "
                f"{source_dir!r} y debe ser la carpeta de agentes de la "
                f"raíz adoptada REGISTRADA ({expected_source!r}, PD-12 "
                f"orden 2; INV-7: la procedencia no recuerda al registro "
                f"ni silencia el cambio respecto a HOME)")
        self.assertNotEqual(
            source_dir, str(Path(home).joinpath(*AGENTS_SUBDIR)),
            msg="PD-12: el manifiesto resuelve su origen a la instación "
                "global de HOME del subproceso (la global del HOME "
                "propietario debe quedar DÉS pero el origen declarado es "
                "el del registro)")

        # Control positivo interno (spec §4): SIN activación, el camino
        # vigente (variable explícita = origen declarado, PD-12 orden 1)
        # sigue publicando derivados coherentes (camino verde de 004-002
        # T5/T7) — la correspondencia de este camino NO es parte del RED
        # y debe cumplirlo también el GREEN.
        control_adopted = self.make_adopted_root("control")
        rootc = self.make_project("proj-control")
        procc = self.run_prepare(
            rootc, agents_dir=control_adopted.joinpath(*AGENTS_SUBDIR),
            home=self.make_home("control"),
            objective="005-005 T3 test-pd12 control positivo")
        self.assertEqual(
            procc.returncode, 0,
            msg=f"PD-12 (control): prepare con la variable explícita "
                f"debe publicar el camino vigente: "
                f"{procc.stdout!r} {procc.stderr!r}")
        manifestc = read_manifest(rootc)
        self.assertTrue(
            manifestc.is_file(),
            msg="PD-12 (control): el manifiesto del camino with-explícito "
                "variable no se publicó")
        dc = json.loads(manifestc.read_text(encoding="utf-8"))
        self.assertEqual(
            dc.get("source_dir"),
            str(control_adopted.joinpath(*AGENTS_SUBDIR)),
            msg="PD-12 (control): con la variable explícita el source_dir "
                "no es la fuente declarada por ella (camino vigente "
                "roto — no es parte del RED)")


# ---------------------------------------------------------------- PD-13


class TestPd13ContradictionDiagnosed(ProvenanceCase):
    """PD-13 (contradicción diagnosticada, INV-7): cuando el origen
    resuelto difiere del registrado en `.cdad/activation.json` (variable
    apunta a OTRA instalación; brazo a) o del `source_dir` del manifiesto
    anterior (caso MIX-V6V7; brazo b), `prepare` emite en STDERR un
    diagnóstico que nombra el registro y las versiones en juego; nunca
    re-deriva otra versión en silencio. Control positivo interno:
    coherencia (origen == registro) → sin diagnóstico de contradicción."""

    def test_pd13_prepare_names_registry_and_versions_on_origin_contradiction(self) -> None:
        home = self.make_home("contr")
        registered = self.make_adopted_root("registered")
        other = self.make_adopted_root("other")
        old = self.make_adopted_root("old")
        reg_tag, other_tag, old_tag = (source_tag(a) for a in
                                       (registered, other, old))

        # ---- brazo (a): la variable apunta a OTRA instalación
        root = self.make_project()
        self.write_registry(root, registered)
        proc_a = self.run_prepare(
            root, agents_dir=other.joinpath(*AGENTS_SUBDIR), home=home,
            objective="005-005 T3 PD-13 brazo a (variable vs registro)")
        self.assertEqual(
            proc_a.returncode, 0,
            msg=f"PD-13(a): el diagnóstico «da cuál usaría» — la "
                f"preparación sigue (rc=0) pero CON el aviso: "
                f"{proc_a.stdout!r} {proc_a.stderr!r}")
        self.assertIn(
            REGISTRY, proc_a.stderr,
            msg=f"PD-13(a): el re-derivo de OTRA instalación a través de "
                f"la variable no nombra el registro de activación "
                f"({REGISTRY}) en el diagnóstico — hoy es SILENCIOSO "
                f"(contradicción variable-vs-registro sin aviso, invoca "
                f"a MIX-V6V7); stderr: {proc_a.stderr!r}")
        for tag in (reg_tag, other_tag):
            self.assertIn(
                tag, proc_a.stderr,
                msg=f"PD-13(a): el diagnóstico no nombra la versión de la "
                    f"instalación {tag!r} registrada en el juego — un "
                    f"aviso sin versiones no alcanza; stderr: "
                    f"{proc_a.stderr!r}")

        # ---- control de coherencia (a): variable == registro → sin
        # diagnóstico de contradicción
        rootc = self.make_project("proj-coherente-a")
        self.write_registry(rootc, registered)
        procc_a = self.run_prepare(
            rootc, agents_dir=registered.joinpath(*AGENTS_SUBDIR),
            home=home, objective="005-005 T3 PD-13 control coherente (a)")
        self.assertEqual(
            procc_a.returncode, 0,
            msg=f"PD-13(a control): el caso coherente debe correr: "
                f"{procc_a.stdout!r} {procc_a.stderr!r}")
        self.assertNotIn(
            REGISTRY, procc_a.stderr,
            msg="PD-13(a control): el caso coherente (origen resuelto == "
                "registrado) NO debe producir el diagnóstico de "
                "contradicción que nombra el registro")

        # ---- brazo (b): resolución difiere del manifiesto anterior
        # (MIX-V6V7: se re-deriva otra versión sin avisar). El manifiesto
        # PREVIO lo crea el propio CLI con la instalación vieja (fixture
        # por superficie declarada, no a mano).
        root2 = self.make_project("proj-mix")
        first = self.run_prepare(
            root2, agents_dir=old.joinpath(*AGENTS_SUBDIR), home=home,
            objective="005-005 T3 PD-13 brazo b primer prepare (old)")
        self.assertEqual(
            first.returncode, 0,
            msg=f"PD-13(b primer prepare): el fixture-prepare de la "
                f"instalación vieja debe publicar el manifiesto previo: "
                f"{first.stdout!r} {first.stderr!r}")
        self.assertTrue(
            read_manifest(root2).is_file(),
            msg="PD-13(b): el manifiesto previo no se publicó — el "
                "fixture no configuró la contradicción MIX-V6V7")
        # El fixture actúa como orquestador: sin cerrar el paquete, un
        # segundo prepare es bloqueado por PD-4 (el paquete activo
        # `prepared` debe completarse primero) — el MOD no agrega
        # restricciones a prepare, marca el pauseo activo completed y
        # deja el manifiesto/derivados de la instalación vieja intactos.
        self.mark_active_completed(root2)
        self.write_registry(root2, registered)  # el registro NOMBRA la nueva
        proc_b = self.run_prepare(
            root2, agents_dir=None, home=home,
            objective="005-005 T3 PD-13 brazo b (resuelto vs manifiesto)")
        self.assertEqual(
            proc_b.returncode, 0,
            msg=f"PD-13(b): el diagnóstico «dice cuál usaría» — la "
                f"preparación contra el registro sigue (rc=0) con aviso: "
                f"{proc_b.stdout!r} {proc_b.stderr!r}")
        self.assertIn(
            REGISTRY, proc_b.stderr,
            msg=f"PD-13(b): la resolución del registro ({registered.name}) "
                f"difiere del source_dir del manifiesto anterior "
                f"({source_tag.__name__}: {old.name}) y el prepare NO "
                f"nombra {REGISTRY} — hoy el cambio de versión respecto "
                f"del manifiesto anterior es silencioso (MIX-V6V7 real: "
                f"la re-derivación re-publicó 11 agentes de otra versión "
                f"sin aviso); stderr: {proc_b.stderr!r}")
        for tag in (reg_tag, old_tag):
            self.assertIn(
                tag, proc_b.stderr,
                msg=f"PD-13(b): el diagnóstico no nombra las DOS versiones "
                    f"en juego ({tag!r} entre el manifiesto anterior y el "
                    f"registro); stderr: {proc_b.stderr!r}")


# ---------------------------------------------------------------- PD-14


class TestPd14VersionDeclaredInPublishedArtifact(ProvenanceCase):
    """PD-14 (versión verificable por sesión): el manifiesto declarado y/o
    cada agente publicado declara la versión/commit de la instalación de
    origen. Fixture (opciones del paquete): raíz adoptada con el patrón de
    nombre `cdad-adopted-<tag>` Y un marcador de versión en la raíz
    (`version.txt` con el sha COMPLETO del commit, no deducible de ruta
    alguna); el RED fracasa exactamente en la DECLARACIÓN de la versión.
    Control interno: el artefacto publicado sí existe y se lee (preparación
    con la variable explícita, coherente)."""

    def test_pd14_origin_version_is_declared_and_readable_in_published_artifact(self) -> None:
        home = self.make_home("vers")
        adopted = self.make_adopted_root("registered")
        tag = source_tag(adopted)
        version = source_version(adopted)
        root = self.make_project()
        self.write_registry(root, adopted)

        # Origen EXPLÍCITO coherente con el registro (orden 1): publica
        # el artefacto contrato-vigente. La AUSENCIA de versión es la
        # postcondición contratada (D5: en el manifiesto y/o en cada
        # agente publicado).
        proc = self.run_prepare(
            root, agents_dir=adopted.joinpath(*AGENTS_SUBDIR), home=home,
            objective="005-005 T3 PD-14 origen explícito/coherente")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-14 (precondición): el prepare explícito debe "
                f"publicar: {proc.stdout!r} {proc.stderr!r}")
        manifest = read_manifest(root)
        self.assertTrue(
            manifest.is_file(),
            msg="PD-14 (control): el manifiesto del artefacto publicado "
                "no existe — el test no puede evaluar la declaración")
        agents = published_agents(root)
        self.assertTrue(
            agents,
            msg=f"PD-14 (control): prepare no publicó derivados en "
                f"{DERIVED_DIR}/")

        blob = manifest.read_text(encoding="utf-8")
        in_manifest = version in blob
        in_every_agent = agents and all(
            version in text for text in agents.values())
        self.assertTrue(
            in_manifest or in_every_agent,
            msg=f"PD-14: el artefacto publicado NO declara la versión/"
                f"commit de la instalación de origen ({adopted.name}, "
                f"marcador version.txt={version[:12]}… tag={tag!r}): el "
                f"manifiesto sólo lleva `source_dir` + hashes y los "
                f"agentes publicados no declaran versión — NO es "
                f"verificable qué versión cargó una sesión (PD-14; "
                f"D5 decide manifiesto y/o agentes)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
