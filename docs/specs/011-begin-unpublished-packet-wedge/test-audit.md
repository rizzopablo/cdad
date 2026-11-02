# AUDIT report — test-writer / audit — 011-begin-unpublished-packet-wedge (FINAL TEXT)

## 0. Intake validation (Route C — explicit file backup)

- Dispatch carried exactly one identification block, no inline packet body → Route C, no route mixture.
- `validate-request` → exit 0. `validate-packet` → exit 0.
- `render --route C` output is byte-identical to the dispatched identification JSON (packet_id, execution_id, contract + sha256, request/packet/execution_context paths, project_root).
- Contract digest verified: `sha256(spec.md) = 5fcea0bf…14f63` matches.
- Execution context `.cdad/executions/exec-011-begin-unpublished-packet-wedge-001/execution.json` declares `schema_version == 2` → v2, Route C admissible.
- **Verdict: packet VALID. Worked exclusively from the packet's declared inputs/scopes/invariants.**

## 1. Scope and isolation compliance

- Read: only `docs/specs/011-begin-unpublished-packet-wedge/spec.md` (approved contract) and files under `tests/` (read scope) — mapping tables/headers/bodies of the 6 focal files plus two adjacent files checked for pre-existing v2/`begin` coverage (`test_packet_prepare.py`, `test_010_004_t6_red.py`).
- **No implementation code read** (`skills/`, `scripts/`, `sources/`, `agents/` untouched). No `src/`/`lib/` exists in this repo; nothing outside `tests/`+spec was opened.
- Edited: nothing. Modified files: **none**. Commit: **none** (audit substage alters no tests by packet instruction).

## 2. test↔postcondition mapping (011 PC-1..PC-5 + INV-1/INV-2)

All 6 focal files use the black-box oracle (public CLIs on disposable projects; no product module imports — declared in 008_004 header §Oráculo). Fixture base `_RecoveryProject` (007-002) and legacy fixtures (003-007 T1) use **execution `schema_version: 1` throughout**; no focal test constructs a v2 execution document.

| 011 postcondition | Covering test (focal file) | What it proves | Verdict |
|---|---|---|---|
| PC-3 — non-v2, no packet tree, valid preconditions → `begin` rc==0 | `test_begin_legado_sin_arbol_de_paquetes_se_acepta` (008_004:718) — legacy project without `.cdad/packets`, accepts begin rc 0, persists continuity head | Direct cover of PC-3 (v1/legacy form, exactly what PC-3 requires) | ✅ COVERED |
| PC-4 — accredited exact replay → rc==0, `no_op==true`, no new bodies, head unchanged | `test_pc07_begin_identico_repetido_es_replay_sin_efectos` (008_004:523) — identical begin replay: rc 0 + `assert_no_effects` (tree + state byte-identical) | Covers rc==0 and byte-level no-effects; **does NOT assert `no_op == true`** on the begin-replay envelope (008_003:648 asserts `no_op is True` only for checkpoint/receive replays) | ✅ COVERED with precision note (see §4) |
| PC-5 — trace without `REQUEST.json` → rejected before persist, no new bodies, head unchanged | `test_begin_con_request_ausente_y_rastro_de_publicacion_se_rechaza` (008_004:692) — PACKET.md present + REQUEST.json deleted → clean rejection (rc≠0, no traceback) + `assert_no_effects` | Direct cover of PC-5 under v1 context; the v1-vs-v2 distinction is irrelevant to PC-5's wording (version-agnostic rejection) | ✅ COVERED |
| PC-1 — v2, new begin, `packet_id` with no published REQUEST and **no trace at all** → rc≠0; diagnostic names `packet_id`, signals missing `REQUEST.json`, indicates `prepare`; creates/modifies no bodies; head bytes preserved (or absent) | **No test.** Closest neighbor is 008_004:692 but it (a) runs under a v1 execution document and (b) always has a PACKET.md trace. Nothing exercises the v2 discriminator (`schema_version == 2` from the execution doc) or the zero-trace case. | — | ❌ GAP — new RED test required |
| PC-2 — after PC-1 rejection, corrected `prepare` → legitimate `begin` rc==0 + `verify-begin` rc==0, no manual repair | **No test.** `prepare→…→begin` legitimate path exists only as fixture setup (`_RecoveryProject` publishes via `prepare`), never asserted as a recovery flow; `verify-begin` is exercised in 007_003/007_007/008_003 files but never chained after a PC-1-style rejection + re-prepare. | — | ❌ GAP — new RED test required |
| INV-1 (discriminator = execution doc, never the trace) | Indirectly guarded by 008_004:692 (trace present + REQUEST absent → reject, not legacy) and 008_004:718 (no tree → accept). No test pins the discriminator to `schema_version == 2` vs trace presence. | Partial; the new PC-1 test (v2 + zero trace → reject) combined with 008_004:718 (v1 + zero trace → accept) will pin INV-1 exactly. | ⚠️ PINNED ONLY AFTER RED |
| INV-2 (fail-closed: no persistent effect of a new begin before admission) | `test_pc07_rechazo_no_altera_registros_durables_previos` (008_004:493), 008_004:692/304-series (`assert_no_effects`, tree+state snapshots before/after) | Established pattern; new PC-1 test must reuse it (inventory + body/head bytes before/after). | ✅ PATTERN EXISTS |

Background (not direct 011 cover, explicitly untouched): 003_004_t2_writeahead (O1 divergent-begin conflict, RB1 malformed body, D4 expired authority, P3 writeahead→dispatch→reconcile), 003_007_t2_checkpoint_vs_begin (P5/P6/O1/V5 begin-vs-checkpoint discrimination), 003_004_t2_reconcile (P3 matrix, P1 stale-tamper, D7 split-brain, P8 legitimate scenario), 007_006 (withdraw/republish prepared-packet lifecycle incl. `test_prepared_begin_and_project_drift_recovery_both_orders`), 008_003 remainder (authority/suspension/replay-eligibility).

Adjacent v2 usages checked and ruled out: `test_packet_prepare.py:642` uses `{"schema_version": 2}` only as a *malformed-context* case for `prepare` failure; `test_010_004_t6_red.py` builds a v2 context only for the execution-locator feature (010-004). Neither issues a `begin` for an unpublished packet.

Traceability-convention note: 008_004 (17×) and 008_003 (8×) declare per-test consequences ("Sin este test…"); the other four focal files carry contract-mapping tables in their headers instead of per-test consequence lines. No content judgment made — recorded as-is.

## 3. Regression risks for the implementer (do-not-break list)

1. `test_begin_legado_sin_arbol_de_paquetes_se_acepta` — v1/legacy accept-path; the fix must key the new rejection **only** on `schema_version == 2` (INV-1). Keying on trace absence would flip this control red.
2. `test_pc07_begin_identico_repetido_es_replay_sin_efectos` — replay-before-admission ordering must be preserved: an accredited exact replay in v2 must still return rc 0, not be reclassified as a "new begin".
3. `test_begin_con_request_ausente_y_rastro_de_publicacion_se_rechaza` — PC-5 behavior must hold in both v1 and v2 after the fix (diagnostic + zero effects).
4. All fixtures run v1 contexts; the fix must not change v1 admission semantics anywhere (PC-3).

## 4. RED proposal (for post-audit approval; nothing written yet)

Per R2 (one test per observable promise): exactly **two new tests**, both in `tests/test_008_004_packet_enforcement.py` (the admission-boundary battery), reusing `_RecoveryProject`-style fixtures with a v2 execution document plus the `assert_no_effects` (tree + state bytes) pattern:

- **T1 (PC-1):** v2 execution, new `begin` for a `packet_id` with no published REQUEST and no packet-tree trace → rc≠0 with diagnostic naming the `packet_id`, signaling the missing `REQUEST.json`, indicating `prepare`; no bodies created/modified; head bytes preserved/absent. Must fail pre-fix by contract assertion (acceptance criterion 1), not by environment.
- **T2 (PC-2):** after T1's rejection, run `prepare` for that `packet_id`, then legitimate `begin` (rc==0) + `verify-begin` (rc==0), no manual repair.
- **Precision note (optional, orchestrator decides):** extend PC-4 cover with a `no_op == true` assertion on the begin-replay envelope (008_004:523 proves rc 0 + byte-identical state but not the flag 011 names). Not a new promise — an assertion-strengthening of existing cover.

Explicitly **not** proposed: exhaustive v1×v2 matrix variants, load/perf, or re-proof of background files — deferred-hardening material, none required by PC-1..PC-5.

## 5. Evidence

- Modified files: none. Commit: none (nothing to commit; pre-existing worktree state `M docs/.cdad-state.json` + untracked `docs/specs/010-000-…/discovery.md` left untouched — orchestrator-owned).
- Exact commands executed (all read-only; no test run per full-suite policy — the packet does not request a run, and the closer runs the suite at closure):
  - `python3 scripts/cdad_packet.py validate-request --request .cdad/packets/011-…/REQUEST.json --execution-context .cdad/executions/exec-011-…/execution.json` → exit 0
  - `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md --execution-context …` → exit 0
  - `python3 scripts/cdad_packet.py render --request … --execution-context … --route C` → output identical to dispatched identification block
  - `sha256sum docs/specs/011-begin-unpublished-packet-wedge/spec.md` → `5fcea0bf…14f63` (matches contract)
  - Read-only inspections: `ls tests/`, `grep` for test inventories / `schema_version` / `verify-begin` / `no_op` / consequence lines, full reads of 008_004 header + PC-07/admission-tail sections and the 011 spec.
- No implementation code was read; no phase isolation deviation to declare.
