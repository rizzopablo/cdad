# Complete-suite execution record

## Serial attempt 1 — completed, not green

Snapshot: `196c6f4a`; command:

`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests`

Result: **2063 passed, 5 skipped, 6 failed**, exit 1, 4672.55 seconds.
Evidence: `.cdad/orchestration/epic-019/recovery-final-suite/`.

Four failures were the independently reproduced pre-existing README regressions,
subsequently corrected in `1ccc1eaf` with 7 focal and 53 consumer tests passing.
Two adapter cases passed when re-executed separately (2 passed in 20.21 seconds).
Their isolated retry does not establish the cause or make the serial run green.

## Serial attempt 2 — interrupted by owner-directed method change

The final-revision rerun was intentionally interrupted after the owner asked to
use four workers. Result: **74 passed, KeyboardInterrupt, exit 2**, 183.84 seconds.
This is not a completed suite and is not counted as final acceptance evidence.
Evidence: `.cdad/orchestration/epic-019/recovery-final-suite-2/`.

## Parallel complete-suite attempt — pending

The owner explicitly authorized four workers. The existing project runner
supports that setting and process/resource isolation; no dependency installation,
test modification or new parallel implementation is commissioned.

Command:

`PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py parallel --all --workers 4 --evidence-root .cdad/orchestration/epic-019/recovery-suite-4-workers`

The evidence directory was created empty, with the revision snapshot recorded
separately. The serial pytest process received SIGINT rather than running both
complete suites concurrently. No external model exercise remains active.

Final complete-suite acceptance requires the runner's actual exhaustive-selection,
per-worker and aggregate evidence. Do not infer success or a fourfold speedup.
The epic and feature closure remain unregistered pending that result.

## Subsequent outcomes

The parallel attempt was rejected: its canary detected concurrent changes to
installed agents and checkout. The result is not usable; its 16 failures are
not attributed to an established single cause.

The final serial suite at 65d0ba62 completed with 2069 passed, 5 skipped and
exit 0 in 4534.18 seconds; evidence lives in `recovery-final-suite-3/`.
Feature closure is recorded in `closure.md`; epic 019 remains open for 019-004.
