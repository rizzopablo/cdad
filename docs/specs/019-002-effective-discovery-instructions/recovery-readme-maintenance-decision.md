# Bounded maintenance decision — preserve existing README promises

The restored `bc922c04` baseline also restores four known README regressions
from the earlier `3b62d552` change. They are not caused by the recovery dialogue
instructions. Their historical audit is `regression-audit.md`.

The orchestrator reproduced them against the current restored/reimplemented
candidate using:

`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_005_006_t4_readme.py tests/test_005_006_t6_owner_reviewfix.py`

Result: four failed, three passed; complete output:
`.cdad/orchestration/epic-019/recovery-readme-baseline.log`.

Under renewed delegated HITL, authorize a separate narrow maintenance assignment
after the current complete-suite snapshot finishes: restore the existing
005-006 user promises, using prior `2de6e72b` as evidence, not as an instruction
to replay unrelated changes.

Actual write scope: README.md only. Add a short guided-start pointer, remove the
installer-only environment variable from runtime wiring, and derive the status
CLI example from `<skill-dir>/scripts/`. No dialogue redesign, tests changes,
installation, models or directory migration. Independently review the resulting
small diff and run the protected regression tests.

Do not change product while the current full-suite snapshot is running. A final
suite must then cover the actual final revision or have explicitly justified
snapshot equivalence; do not present the current run as testing later edits.
