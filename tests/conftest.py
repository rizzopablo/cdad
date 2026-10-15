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
