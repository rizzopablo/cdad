#!/usr/bin/env python3
"""Instrumentación de reproducción para A-3 (review-fix 2 RED).

Origen: evidencia de review `harness_b.py` / `p_orphan_inode.py`
(scratchpad de la review T3/T4 suplente). Parchea `os.open` del proceso
invocado para que ese proceso SE PAUSE (bandera) justo antes o justo
después de abrir `<raíz>/.cdad/.lock`. NO inyecta opciones (el argv que
recibe se pasa integro al CLI) ni modifica el SUT: solo congela el
tiempo en un punto donde el gancho oficial I5b/I5d no llega (entre el
`open` y el `flock`), tal como lo hizo el reviewer.

Uso:
    python3 tests/_rf2_open_pause.py <cdad_packet.py> <when> <flag> \
        <argv puro del CLI...>

  when: before-open | after-open
  flag: al llegar al punto se crea `<flag>.reached` y se espera a que
        exista `<flag>` (tope 30 s, mismo semántica que I5b). Es inerte
        para todo otro archivo.
"""

import os
import runpy
import sys
import time
from pathlib import Path

_PAUSE_MAX = 30


def _wait(flag: Path) -> None:
    Path(str(flag) + ".reached").write_text("x", encoding="utf-8")
    deadline = time.monotonic() + _PAUSE_MAX
    while not flag.exists() and time.monotonic() < deadline:
        time.sleep(0.02)


def main() -> None:
    script = sys.argv[1]
    when = sys.argv[2]
    flag = Path(sys.argv[3])
    args = sys.argv[4:]

    real_open = os.open
    hit = {"done": False}

    def patched(path, flags, *a, **k):
        if (not hit["done"]) and str(path).endswith(".cdad/.lock"):
            hit["done"] = True
            if when == "after-open":
                fd = real_open(path, flags, *a, **k)
                _wait(flag)
                return fd
            if when == "before-open":
                _wait(flag)
                return real_open(path, flags, *a, **k)
        return real_open(path, flags, *a, **k)

    os.open = patched
    sys.argv = [script, *args]
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
