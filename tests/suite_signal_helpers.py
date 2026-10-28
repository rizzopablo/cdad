"""Helpers de forma compartidos por el piloto 005-010 (008-002 T4, PC-4).

Sólo duplicaciones de FORMA documentadas en pc-map.json
(`form_only_duplication_for_T4`); ninguna aserción cambia de contenido.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


def assert_diag_actionable(case: unittest.TestCase, out: dict,
                           label: str) -> str:
    """Salida legítima ante bloqueo/terminación no completada: diagnóstico
    accionable no vacío (vocabulario de la spec §2)."""
    diagnosis = out.get("diagnosis")
    case.assertIsInstance(
        diagnosis, str, msg=f"{label}: el diagnóstico no es texto")
    case.assertTrue(
        diagnosis.strip(),
        msg=f"{label}: diagnóstico vacío (la salida legítima exige un "
            f"diagnóstico accionable)")
    return diagnosis


def text_hits(base: Path, text: str) -> list:
    """Archivos bajo `base` que contienen `text` (bytes UTF-8)."""
    return [
        path for path in sorted(base.rglob("*"))
        if path.is_file() and text.encode("utf-8") in path.read_bytes()]


def rewrite_config(path: Path, mutate) -> None:
    """Aplica `mutate` a la config JSON de ejecución y la reescribe."""
    config = json.loads(path.read_text(encoding="utf-8"))
    mutate(config)
    path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
