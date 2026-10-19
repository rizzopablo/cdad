## Role report — implementer GREEN, `006-005-native-path-parity` U6-1

### Diagnosis (defect confirmed)
`capabilities()` resolved the module but never consulted `runtimes.json`, so the module answered without any configuration and could only declare `version: unknown` plus the missing-`sessions_db`/`binary` reason (U6-1). `dispatch` already delivered the section on the derived-config channel; `capabilities` did not.

### Modified files
- `skills/cdad-cycle/scripts/cdad_dispatch.py` (+35/−8) — only implementation file touched; `tests/` untouched.

Change:
- `capabilities(runtime, project_root, *, as_json)` now resolves the module, **loads the runtime section** (`load_runtime_section`, so absent section ⇒ PD-9 fail-closed diagnostic) and resolves the project root.
- `module_capabilities(module, *, runtime, section, root)` derives the transient internal configuration exactly as `dispatch` does (`derived_internal_config`: correspondence keys only — never `model` nor credentials) and hands it to the module as `--exec-config`, removing the file in a `finally`.

### Test → result

| Test | Result |
|---|---|
| `tests/test_006_005_u6fix1_capabilities_entry.py` (focal, 3 tests: PD-10, PD-25, PD-9) | **3 passed** (was RED: 3 failed) |
| `tests/test_006_005_u1a_runtime_config.py` (19) | 19 passed |
| `tests/test_006_005_u1b_dispatch_entry.py` (13) | 13 passed |
| `tests/test_006_005_u1c_packet_agent.py` (5) | 5 passed |
| `tests/test_006_005_u2_opencode_module.py` (19) | 19 passed |
| `tests/test_006_005_u3b_derived_temporary_permission.py` (6) | 6 passed |
| `tests/test_006_005_u3_temporary_scope.py` (8) | 8 passed |
| `tests/test_006_005_u4_single_entry.py` (7) | 7 passed |
| `tests/test_006_005_u5_disposition_failed.py` (6) | 6 passed |
| `tests/test_006_005_u7_scribe_role_report.py` (6) | 6 passed |
| `test_005_009_t1_interface`, `_t2_opencode_adapter`, `_t4_acceptance`, `test_005_007_t5_delegation_dispatch`, `test_004_002_t4_dispatch` (34 + 1 skipped) | 34 passed, 1 skipped |
| `test_005_010_t1_durable_signal`, `_t2_load_mode_invocation`, `_t4_integration`, `test_005_010_reviewfix` (22 + 1 skipped) | 22 passed, 1 skipped |
| `test_006_002_u5_transport_equivalence`, `test_006_001_t1_selection`, **`test_006_001_t1b_service_mode`**, `test_006_003_u4/u6/u8`, `test_packet_prepare` (78) | 78 passed |
| `make validate` | **F011 environmental** (see below) |

### Commands and output (excerpts)

```
$ python3 -m pytest -q tests/test_006_005_u6fix1_capabilities_entry.py
...                                                                      [100%]
3 passed in 5.19s

$ python3 -m pytest -q tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py \
    tests/test_005_009_t4_acceptance.py tests/test_005_007_t5_delegation_dispatch.py tests/test_004_002_t4_dispatch.py
..............s....................                                      [100%]
34 passed, 1 skipped in 39.07s

$ python3 -m pytest -q tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py \
    tests/test_005_010_t4_integration.py tests/test_005_010_reviewfix.py
.............s.........                                                  [100%]
22 passed, 1 skipped in 32.33s

$ python3 -m pytest -q tests/test_006_002_u5_transport_equivalence.py tests/test_006_001_t1_selection.py \
    tests/test_006_001_t1b_service_mode.py tests/test_006_003_u4_delegation_config.py \
    tests/test_006_003_u6_server_credential.py tests/test_006_003_u8_acceptance.py tests/test_packet_prepare.py
........................................................................ [ 92%]
......                                                                   [100%]
78 passed in 205.94s (0:03:25)

$ make validate
...
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
Assert PASS: 168 / Assert FAIL: 1
make: *** [Makefile:22: validate] Error 1
```

**F011 declared environmental** (not caused by this change, and not closable from the implementation scope): `install.sh --check` reports installed user copies lagging the repo — `~/.config/opencode/skills/cdad-cycle/scripts/cdad_dispatch.py` and `~/.agents/.../cdad_dispatch.py` *missing*, plus `cdad_delegate*.py`/`cdad_packet.py`/`cdad_result.py` and `references/re-entry.md`, `references/cli-delegation.md` differing, and both installed orchestrator agent files drifted. This is installation drift of many pre-existing files (the dispatch script itself is absent from the installed trees), unrelated to the capability fix; 168/169 asserts pass.

### Commit
```
[main caaab97] fix: 006-005 U6-1 — capabilities por la entrada recibe la seccion del runtime
 1 file changed, 35 insertions(+), 8 deletions(-)
```
No `--no-verify`, no `git stash`, no push. `git status --short` afterwards shows only the untracked, not-mine paths (`docs/planning/`, `findings/incremental-construction-and-reproducible-validation-2026-10-17.md`).

### Notes / limitations
- The derived transient config is written under the resolved project root (`--project-root`, else cwd) in the already git-ignored `.cdad/runtime/` and deleted in `finally`; no user config or real store is read or written.
- Full suite not run, per the packet's declared full-suite policy (the closer runs it once at closure); the feature focals, the ficha regressions and the integration-gate files listed in the objective were run explicitly.
- No test was edited; the PD-9 negative now passes because `capabilities` consults the single source before ever invoking the module.