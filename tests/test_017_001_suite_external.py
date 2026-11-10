"""017-001 T4-adicional RED: fronteras de proceso externo del resto observables.

Decision del dueno (medir antes de fijar objetivo, spec §4.4 regla de
desconocidos): el resto no desglosado de la base (4800.1 s) no fundamenta
ninguna optimizacion hasta medirse con una focal adicional. Esta sonda
focal cubre las fronteras de proceso externo de los seis archivos mas
caros de la base con marcas ``external.<clase>`` sobre
``tests/suite_operation_markers.py``:

- ``external.install``: ``bash <producto>/install.sh``.
- ``external.cli``: ``bash scripts/validate-subagents.sh``.
- ``external.python``: ``[sys.executable, <cli>, ...]``.

Cada pata invoca el helper real del archivo con argumentos rapidos
degenerados (``--help`` o la corrida real del validador sobre el repo):
atraviesa la misma linea envuelta con la misma forma de comando que la
corrida productiva; la marca no cambia comandos, argumentos, entornos,
aserciones, orden ni resultados. Sin observador las marcas son neutras;
con observador cada invocacion emite un par begin/end con terminacion
``ok``. Sin umbrales temporales como oraculo (convencion 11): solo
presencia, identidad y terminacion; nunca duraciones.

Promesa observable (spec §4.4 + PC-5/PC-6, INV-6): el responsable puede
localizar el costo externo del resto sin cifras ficticias. Sin este
test, el usuario podria fijar el objetivo de reduccion (PC-4) sobre
resto no atribuido y el informe presentaria tiempo externo no medido
como costo explicado.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from tests.suite_operation_markers import observed

REPO = Path(__file__).resolve().parents[1]

from tests.test_009_001_installer_agent_overlay import (  # noqa: E402
    run as run_009,
    run_validator,
)
from tests.test_010_002_documentary_role_properties import (  # noqa: E402
    _run as run_010_002,
    _run_product_install,
)
from tests.test_012_installer_ignore_pycache import (  # noqa: E402
    run_installer as run_012,
)
from tests.test_install_ownership import run_installer as run_ownership  # noqa: E402
from tests.test_install_review5_regressions import (  # noqa: E402
    run_installer as run_review5,
)
from tests.test_role_packet_render import run_cli  # noqa: E402
from tests.test_role_packets import PACKET_CLI  # noqa: E402


class ExternalBoundariesProbe(unittest.TestCase):
    def test_external_boundaries_emit_observed_events(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cdad-017-ext-probe-") as tmp:
            root = Path(tmp)
            env = os.environ.copy()
            legs = [
                ("009-install.sh", lambda: run_009(REPO, root, "--help"),
                 "external.install", True),
                # El validador real sobre el repo sin instalar devuelve
                # rc!=0 (conducta productiva intacta); la neutralidad de su
                # rc la cubre test_pc5 en la corrida de los seis archivos.
                ("009-validator", lambda: run_validator(REPO, root),
                 "external.cli", False),
                ("010_002-python-cli",
                 lambda: run_010_002(PACKET_CLI, "--help", cwd=REPO, env=env),
                 "external.python", True),
                ("010_002-product-install",
                 lambda: _run_product_install(REPO, env, "--help"),
                 "external.install", True),
                ("ownership-install.sh",
                 lambda: run_ownership(REPO, root, "--help"),
                 "external.install", True),
                ("review5-install.sh",
                 lambda: run_review5(REPO, root, "--help"),
                 "external.install", True),
                ("packet-render-cli", lambda: run_cli("--help"),
                 "external.python", True),
                ("012-install.sh",
                 lambda: run_012(REPO, root, "--help"),
                 "external.install", True),
            ]
            for label, invoke, expected, check_rc in legs:
                with self.subTest(leg=label):
                    with observed() as sink:
                        result = invoke()
                    begins = [e for e in sink
                              if e["event"] == "begin"
                              and e["operation"] == expected]
                    ends = [e for e in sink
                            if e["event"] == "end"
                            and e["operation"] == expected]
                    self.assertEqual(
                        len(begins), 1,
                        f"{label}: se esperaba exactamente un begin "
                        f"{expected}; eventos={sink!r}")
                    self.assertEqual(
                        len(ends), 1,
                        f"{label}: se esperaba exactamente un end "
                        f"{expected}; eventos={sink!r}")
                    self.assertEqual(
                        begins[0]["interval_id"], ends[0]["interval_id"],
                        f"{label}: begin/end pertenecen al mismo intervalo")
                    self.assertEqual(
                        ends[0]["termination"], "ok",
                        f"{label}: la invocacion debe cerrar el intervalo "
                        f"sin excepcion; rc={result.returncode}")
                    if not check_rc:
                        continue
                    self.assertEqual(
                        result.returncode, 0,
                        f"{label}: la marca no debe cambiar el resultado "
                        f"de la invocacion; rc={result.returncode} "
                        f"stderr={result.stderr!r}"[-1500:])


if __name__ == "__main__":
    unittest.main()
