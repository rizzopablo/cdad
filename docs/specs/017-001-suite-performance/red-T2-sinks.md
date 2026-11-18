Route C validated and task complete. FINAL TEXT below.

---

# FINAL TEXT — test-writer RED (packet `017-001-suite-performance-test-writer-red-013`, T2)

## 1. Intake validation (Route C — explicit file backup)

- Identification block metadata matches `REQUEST.json`: `packet_id=017-001-suite-performance-test-writer-red-013`, `execution_id=exec-017-001-suite-performance-001`, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`.
- Contract file sha256 verified on disk: `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e` ✅
- `PACKET.md` equals canonical render: `python3 scripts/cdad_packet.py render --request .cdad/packets/…/REQUEST.json` → `diff` against `PACKET.md` = **RENDER_MATCH** (rc=0).
- Execution context `.cdad/executions/exec-017-001-suite-performance-001/execution.json` is **v2** (`schema_version: 2`) ✅. No inline packet in the dispatch → no route mixture.
- Scopes honored: read only `docs/specs/017-001-suite-performance` + `tests/`; wrote only `tests/` (2 files). **No implementation code read** (`scripts/`, `agents/`, etc. never opened; `scripts/cdad-suite.py` used only as black-box CLI, the established pattern of the existing verifiers). `tdd_substage=red` confirmed in `docs/.cdad-state.json`.

## 2. Pre-RED finding (missing protection)

Searched `tests/test_017-001_suite_operations.py`, `test_017_001_suite_tranche1/2.py`, spec and calibration for simultaneous-sink protection: **none exists**. All existing verifiers use a single `observed()`; `attach()` replaced the unique sink, so a verifier's `observed()` displaced the close observer's sink. Consequence without fix: the C-P `close` run captures zero `product.*` marks although the child emitted them.

## 3. RED test (P7 — pending behavior, one test per promise)

New test `test_concurrent_sinks_coexist_and_both_receive_events` in `tests/test_017_001_suite_operations.py` (traces to **PC-1 parte operaciones, INV-1, INV-8**). Promise: *close observer and verifier `observed()` coexist and both capture*. It asserts: `attach` adds without displacing, `detach` removes its own or the last, `is_active` reflects any sink, `observed()` adds/removes only its own, both sinks receive identical begin+end.

**RED run (old helper, before fix):**
- cmd: `python3 -m pytest tests/test_017_001_suite_operations.py::test_concurrent_sinks_coexist_and_both_receive_events -q` (2026-11-07T15:19:39Z)
- result: `1 failed in 0.12s` — `AssertionError: 017-001 T2 P7: al salir observed() debe seguir activo el sumidero del close; si no, observed() desplazó al observador`. Right reason (assertion on missing behavior, not import/syntax) ✅

## 4. Test-scope fix (`tests/suite_operation_markers.py`, ordered by the packet)

Single `_sink` → `_sinks` list: `attach` appends (no duplicates), `detach(sink=None)` removes its own or the last (no-op when empty), `is_active` = any sink, `observed()` adds/removes only its own, `operation()` fans begin/end out to all sinks. Public signatures backward compatible (`detach()` no-arg still works; same behavior for single-sink callers) — existing 8 tests, tranche1/2, conftest and the in-process orchestrator keep working.

## 5. Verification (packet-ordered)

| Run (cmd, UTC) | Result |
|---|---|
| `pytest tests/test_017_001_suite_operations.py -q` (15:20:39Z) | **9 passed in 10.87s** (8 existing + P7; wall 11.6s) |
| `pytest tests/test_017_001_suite_profile.py -q` (15:20:53Z) | **17 passed in 22.04s** (T1 focal intact; wall 22.8s) |
| `pytest tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py -q` | **2 passed in 1.21s** (other helper consumers) |
| `close` C-P-cold **old helper** (sensitivity control): `python3 scripts/cdad-suite.py close --evidence-root ~/clawd/tmp/017-001-red013/evidence-prefix --nodeids …/nodeids-cp-cold.txt` (15:21:38Z) | rc=0, profile `complete` but **2 ops only** (`isolation.seed` ×2), **zero `product.*`** — defect reproduced |
| `close` C-P-cold **fixed helper**: same cmd → `evidence/attempt-20261107T152125851372Z-629874-279bcc55` (15:21:25Z, 2.8s wall) | rc=0, pytest 1 passed, profile `complete`, no diagnosis, **6 ops**: `product.lookup cold` (parent of copy+generate), `product.copy cold`, `product.generate cold`, `product.lookup cached` (root), +2 `isolation.seed`; scope_ref = repo `operation-scope.json` (draft); `pytest_wall_s=1.75` |

Per the full-suite policy (focal cycle + proportional regression): complete suite **not run** — executed selection (9 ops + 17 T1 + 2 tranche + 2 focal close runs) with the limits stated here.

## 6. Commit (tests only)

- `af26e0fb` — `test(017-001-T2): P7 coexistencia de sumideros y helper multi-sumidero (corrige desplazamiento del observador del close)` — **2 files**: `tests/suite_operation_markers.py`, `tests/test_017_001_suite_operations.py` (94+/15-).
- Honest declaration: `docs/.cdad-state.json` shows modified but is **pre-existing orchestrator state**, untouched by me and **not** in this commit. No `src/`/`scripts/` reads (content reads via shell were limited to `tests/` + declared spec inputs; the `/tmp/opencode` write-denial was worked around with repo-local temp files, removed afterwards).

## 7. Traceability

- P7 → PC-1 (operational part), INV-1, INV-8. *Without this test, the user enters the base with a close profile missing `product.lookup/copy/generate` although the child emitted them, and attributes staging cost to a broken capture.*
- No `deferred-hardening` entry: the promise is fully covered; no duration assertions used (convention 11).

**No blockers. No implementation reads. Phase isolation preserved (guard-by-name limit declared, PD-15).**
