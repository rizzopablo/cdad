#!/usr/bin/env python3
"""019-004 T4 E2E — consumidor instalado aislado (spec §9 "Use", PC-15).

Contract: docs/specs/019-004-project-layout-and-dispatch-intake/spec.md
(sha256 8ad2d594…0d839), §8 promesa E (PC-15) y §9 (receta de uso).

Método: caja negra. El árbol actual se instala con el instalador del proyecto
en un HOME aislado (directorio temporal; nunca el HOME real ni un despliegue al
entorno del usuario). Luego, SIN depender del checkout, se invoca la CLI
instalada como lo haría un consumidor: se publica un paquete con `prepare`, se
valida una identificación Route C controlada con `intake` y se rechaza una
alterada, y se comprueba que el árbol del proyecto no cambió.

Si el instalador no puede correr aislado (p.ej. falta el staging y no se puede
generar, o el instalador falla antes de desplegar) el test se SALTA con la
razón y la limitación registradas: nunca produce un falso verde.

Mapeo test -> postcondición (una promesa observable, R2):

  test_installed_consumer_validates_controlled_route_c_and_rejects_altered
      -> PC-15 (guía/CLI instalada usable sin redescubrirla), PC-10 (C),
         PC-12 (C alterado rechazado), PC-13 (solo lectura). Sin este test,
         un consumidor con la instalación aislada no podría usar `intake`
         (ni `layout`) o un despacho alterado se aceptaría desde la
         instalación aunque el checkout lo rechace.

Límite: evidencia acotada a la instalación ejercida y a la representación
suministrada; no es procedencia nativa de entrega (§9).
"""
from __future__ import annotations

from _layout_support import OPERATIONAL_DIR

import json
import os
import pwd
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.product_staging import product_root
from tests.test_packet_prepare import PrepareProject, run_prepare, tree_snapshot

DECLARATION = "Route C — explicit file backup"
RESULT_KEYS = {
    "schema_version",
    "validation",
    "route",
    "packet_id",
    "execution_id",
    "project_root",
    "methodology_dir",
}


def _real_home_marker() -> tuple:
    """Observable state of the REAL home install, to prove it is untouched."""
    # The suite's conftest redirects $HOME per test; the account's real home
    # comes from the password database, not from the environment.
    real = Path(pwd.getpwuid(os.getuid()).pw_dir)
    probes = [
        real / ".claude" / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py",
        real / ".claude" / ".cdad-install-manifest.json",
        real / ".cdad-install-manifest.json",
    ]
    return tuple(
        (str(p), p.stat().st_mtime_ns if p.exists() else None) for p in probes
    )


class InstalledConsumerIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._real_before = _real_home_marker()
        try:
            cls.product = product_root()
        except Exception as exc:  # staging cannot be produced
            raise unittest.SkipTest(
                f"installer cannot run isolated: staging unavailable ({exc}); "
                "limitation: no installed-consumer evidence was produced"
            )
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-019004-install-")
        cls.install_root = Path(cls._tmp.name).resolve()
        env = os.environ.copy()
        env["HOME"] = str(cls.install_root)
        env["CDAD_INSTALL_ROOT"] = str(cls.install_root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        run = subprocess.run(
            ["bash", str(cls.product / "install.sh"), "--basic"],
            cwd=cls.product,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if run.returncode != 0:
            cls._tmp.cleanup()
            raise unittest.SkipTest(
                f"installer cannot run isolated: rc={run.returncode}; reason: "
                f"{(run.stderr or run.stdout).strip()[-400:]}; limitation: "
                "no installed-consumer evidence was produced"
            )
        cls.cli = (
            cls.install_root / ".claude/skills/cdad-cycle/scripts/cdad_packet.py"
        )
        cls.skill_dir = cls.install_root / ".claude/skills/cdad-cycle"

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "_tmp"):
            cls._tmp.cleanup()

    def run_cli(self, *args, cwd):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["HOME"] = str(self.install_root)
        return subprocess.run(
            [sys.executable, "-I", str(self.cli), *map(str, args)],
            cwd=str(cwd),
            env=env,
            capture_output=True,
            check=False,
        )

    def test_installed_consumer_validates_controlled_route_c_and_rejects_altered(
        self,
    ) -> None:
        # The installed skill documents the new surfaces.
        self.assertTrue(self.cli.is_file(), "installer omitted the installed CLI")
        installed_text = "\n".join(
            p.read_text(encoding="utf-8", errors="replace")
            for p in self.skill_dir.rglob("*")
            if p.is_file() and p.suffix in {".md", ".json"}
        )
        self.assertIn("intake", installed_text, "installed skill lacks intake guidance")
        self.assertIn("project-layout", installed_text, "installed skill lacks layout guidance")

        # The installed CLI exposes both commands.
        for sub in ("intake", "layout"):
            helped = self.run_cli(sub, "--help", cwd=self.install_root)
            self.assertEqual(helped.returncode, 0, helped.stderr.decode(errors="replace"))

        with tempfile.TemporaryDirectory(prefix="cdad-019004-consumer-") as tmp:
            base = Path(tmp).resolve()
            root = base / "consumer"
            root.mkdir()
            project = PrepareProject(root)
            packets_dir = root / OPERATIONAL_DIR / "packets"
            prep = run_prepare(
                self.cli,
                *project.args(objective="installed-consumer controlled dispatch",
                              out_dir=packets_dir),
                cwd=base,
                env={**os.environ, "HOME": str(self.install_root)},
            )
            self.assertEqual(prep.returncode, 0, prep.stderr.decode(errors="replace"))
            state = json.loads(project.state_path.read_text(encoding="utf-8"))
            packet_id = state["active_packet"]["id"]
            request = packets_dir / packet_id / "REQUEST.json"

            rendered = self.run_cli(
                "render", "--project-root", root, "--request", request,
                "--route", "C", cwd=base,
            )
            self.assertEqual(rendered.returncode, 0, rendered.stderr.decode(errors="replace"))
            text = rendered.stdout.decode("utf-8")
            identification = json.loads(text[text.index("```json\n") + 8: text.rindex("\n```")])

            def wrap(ident, pre="Runtime note.\n\n", post="\nInert trailing text.\n"):
                body = json.dumps(ident, indent=2, ensure_ascii=False)
                return f"{pre}{DECLARATION}\n\n```json\n{body}\n```\n{post}"

            good = base / "received-good.txt"
            good.write_text(wrap(identification), encoding="utf-8")
            bad_ident = dict(identification, packet_id=identification["packet_id"] + "-x")
            bad = base / "received-altered.txt"
            bad.write_text(wrap(bad_ident), encoding="utf-8")

            before = tree_snapshot(root)
            ok = self.run_cli("intake", "--project-root", root, "--received", good, cwd=base)
            self.assertEqual(ok.returncode, 0, ok.stderr.decode(errors="replace"))
            result = json.loads(ok.stdout)
            self.assertEqual(set(result), RESULT_KEYS)
            self.assertEqual(result["validation"], "structural-dispatch")
            self.assertEqual(result["route"], "C")
            self.assertEqual(result["packet_id"], packet_id)
            self.assertEqual(result["project_root"], str(root))

            rej = self.run_cli("intake", "--project-root", root, "--received", bad, cwd=base)
            self.assertEqual(rej.returncode, 2, rej.stderr.decode(errors="replace"))
            self.assertEqual(rej.stdout, b"", "rejection must not print a success object")
            self.assertTrue(rej.stderr.strip(), "rejection needs a diagnostic")
            self.assertNotIn(b"Traceback", rej.stderr)

            self.assertEqual(tree_snapshot(root), before, "project tree changed (PC-13)")

        self.assertEqual(
            _real_home_marker(), self._real_before, "real HOME was touched"
        )


if __name__ == "__main__":
    unittest.main()
