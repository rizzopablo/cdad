#!/usr/bin/env python3
"""Session bootstrap for the test suite (004-001 T3 test-writer session).

The suite's modules import each other via `from tests.<module> import ...`,
which requires the repository root on sys.path. `python3 -m pytest` provides
that implicitly; the bare `pytest` binary does not. This conftest adds the
repository root unconditionally and additively, so both invocation styles
behave the same. It changes no test semantics.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ------------------------------------------------------------------ 008-001
# Aislamiento HOME/XDG por test (spec 008-001 §4, AJ1-AJ2).

import os
import shutil
import tempfile

import pytest

_MANAGED_DIRS = {
    "HOME": "home",
    "XDG_CONFIG_HOME": "xdg/config",
    "XDG_DATA_HOME": "xdg/data",
    "XDG_STATE_HOME": "xdg/state",
    "XDG_CACHE_HOME": "xdg/cache",
    "XDG_RUNTIME_DIR": "xdg/runtime",
    "TMPDIR": "tmp",
    "TMP": "tmp",
    "TEMP": "tmp",
}
# AJ2: overrides CDAD heredados que desvían configuración, instalación,
# agentes o store hacia ubicaciones externas. El resto de CDAD_* se conserva.
_RETIRED_OVERRIDES = (
    "CDAD_INSTALL_ROOT",
    "CDAD_OPENCODE_AGENTS_DIR",
    "CDAD_CONTEXT_METER_STORE",
)



from tests.product_staging import _fallback_base as _system_temp_base  # noqa: E402


def _isolate_into(root: Path) -> None:
    """Fija las nueve rutas bajo `root`, siembra los agentes canónicos en su
    HOME y retira los overrides AJ2."""
    for key, rel in _MANAGED_DIRS.items():
        path = root / rel
        path.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(path)
    (root / _MANAGED_DIRS["XDG_RUNTIME_DIR"]).chmod(0o700)
    # Origen global de agentes sembrado con los canónicos del repo
    # (copias, no symlinks): el camino por defecto usa bytes reales.
    agents_dir = root / _MANAGED_DIRS["HOME"] / ".config" / "opencode" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted((_REPO_ROOT / "agents").glob("*.md")):
        shutil.copyfile(src, agents_dir / src.name)
    for key in _RETIRED_OVERRIDES:
        os.environ.pop(key, None)
    tempfile.tempdir = None


def _restore(saved_env: dict, saved_tempdir) -> None:
    for key, value in saved_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    tempfile.tempdir = saved_tempdir


@pytest.fixture(scope="session", autouse=True)
def _cdad_session_tmp_root(tmp_path_factory):
    """Raíz estable de sesión: basetemp de pytest y aislamiento de sesión.

    pytest resuelve el basetemp en el primer uso; si eso ocurriera dentro de
    la raíz por test, el teardown de ese test lo borraría. Se fuerza aquí,
    antes de cualquier test, bajo una raíz que vive toda la sesión. Además
    HOME/XDG/TMP quedan fijados bajo esta raíz (con los agentes canónicos
    sembrados) toda la sesión, para que `setUpClass` y fixtures de módulo,
    que corren fuera de la fixture por test, nunca vean los del operador.
    """
    keys = tuple(_MANAGED_DIRS) + _RETIRED_OVERRIDES
    saved_env = {k: os.environ.get(k) for k in keys}
    saved_tempdir = tempfile.tempdir
    root = Path(tempfile.mkdtemp(prefix="cdad-test-session-",
                                 dir=_system_temp_base())).resolve()
    from tests import product_staging
    try:
        _isolate_into(root)
        tmp_path_factory.getbasetemp()
        product_staging._RUN_SCOPED_BASE = root
        yield root
    finally:
        product_staging._RUN_SCOPED_BASE = None
        _restore(saved_env, saved_tempdir)
        shutil.rmtree(root, ignore_errors=True)


@pytest.fixture(autouse=True)
def _cdad_isolated_home(_cdad_session_tmp_root):
    """Raíz descartable por test; se restaura todo al terminar.

    Autouse de alcance function: se prepara antes y se finaliza después que
    los fixtures del test, de modo que sus procesos ya terminaron cuando se
    retira la raíz. No reimpone variables que el test quite o vacíe (AJ1).
    """
    keys = tuple(_MANAGED_DIRS) + _RETIRED_OVERRIDES
    saved_env = {k: os.environ.get(k) for k in keys}
    saved_tempdir = tempfile.tempdir
    root = Path(tempfile.mkdtemp(prefix="cdad-test-home-",
                                 dir=_system_temp_base())).resolve()
    try:
        _isolate_into(root)
        yield root
    finally:
        _restore(saved_env, saved_tempdir)
        shutil.rmtree(root, ignore_errors=True)
