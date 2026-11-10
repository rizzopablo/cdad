FINAL TEXT — implementer review-fix (Route C, 017-001 T1 tercera vuelta, review-T1-003)

## Route C validation — PASS (before working)

- Identification block in the dispatch equals canonical `render --route C` output (byte-identical, verified via `render --route C`).
- `validate-request` → rc=0. `validate-packet` → rc=0.
- `packet_id`, `execution_id`, contract `path`+`sha256` match `REQUEST.json`; contract sha256 `472bab0c…192672e` matches `docs/specs/017-001-suite-performance/spec.md` on disk.
- Execution context `schema_version=2` → v2, Route C admissible. Zero `---cdad-packet-json` markers in dispatch → no route mixture.
- Proceeded on Route C, substage `review-fix`, inputs/scopes of the packet only. No `cdad-cycle`/`cdad-spec-and-test` skill loaded; packet is the execution contract.

## Finding verification (before changing code)

- Re-ran the review-T1-003 independent probe (in-memory `build_profile` with `setup=passed`, `teardown=passed`, `call` lost, XML `skipped`): returned `complete`, `diagnosis: None` — exact match of `review-T1-003.md:18-22`. Grounded BLOCKING confirmed.
- Post-fix probe on same inputs: `incomplete` with `fase 'call' ausente … (call esperable perdida)`. Counterweight probes (`setup-skip-clean`, `call-skip-clean`, `teardown-skip-clean`) stay `complete` with empty diagnosis.

## Fix applied (minimal, no close-semantics change)

- File: `scripts/cdad-suite.py` only (`build_profile`, skipped-branch + docstring, ~+26/−16 with docstring).
- Rule: phase integrity no longer depends on the mere omitted state. `call` exemption is derived from the `setup` outcome — `setup` skipped/failed do not execute `call`; `setup` passed requires `call`. `setup` and `teardown` are required whenever there was phase capture, so every emitted-and-lost phase (including `call` of a skip inside `call`) is `incomplete` with diagnosis and contractual rc intact. No phases invented; the four clean counterweights stay `complete`.
- `tests/` untouched (`git diff --name-only -- tests` empty). Contract untouched. `close` rc/state/canary/argv paths unchanged; only `profile.json` status/diagnosis for the lost-`call`-with-`setup`-passed case changes from `complete` to `incomplete`.

## Exact commands + outputs

- Focal complete: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **17 passed in 22.13s** (9 pre-existing + 8 matrix; prior failing `call-skip-drop-call` now PASSED).
- Proportional regression (packet-declared): `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **49 passed in 46.53s**.
- `python3 scripts/cdad-suite.py validate` → **rc 0**, `status: "ok"`, 2003 nodeids (reported collected count per run), 239 módulos, 31 entradas de mapa; `timing.status: "pending"` con tres destinos placeholder (unchanged).
- Suite completa **no realizada** (ciclo focal + regresión proporcional como rutina; sin autorización para completa). No se ejecutó `cdad-ci-gate.py` (excluido por el gate declarado de T1).

## Modified files / limits

- `M scripts/cdad-suite.py` (only product diff; see `git diff` above).
- `M docs/.cdad-state.json` is pre-existing orchestrator bookkeeping (`active_packet` → this packet `prepared`); not edited by this role, not part of the fix, left uncommitted.
- No commit made by this role (committing would sweep the out-of-scope state file; left for the orchestrator). `git status --short`: `M docs/.cdad-state.json`, `M scripts/cdad-suite.py`.
- Limits: no full suite, no operation-scope calibration/baseline (later tasks), no `close` semantics change, none of the 17 protections weakened (all 17 focal nodeids green).
