# Role report — test-writer, substage RED, U1b (006-005-native-path-parity)

**Intake path:** validated canonical packet (`006-005-native-path-parity-test-writer-red-002`). No full cycle/spec skill was loaded. Implementation code (`skills/cdad-cycle/scripts/**`) was **never read**; the entry was exercised only as a process (behaviour), which is how the module convention, the `--exec-config` sweep and the missing verbs were established.

## 1. Files

| File | Change |
|---|---|
| `tests/test_006_005_u1b_dispatch_entry.py` | **new**, 1318 lines — focal RED of U1b |
| `tests/test_005_009_t1_interface.py` | A-1: fixture destination registers its own attempt + relay oracle |
| `tests/test_005_010_t1_durable_signal.py` | A-1: single record per dispatch (`:431-449`, `:536-543`) |
| `tests/test_005_010_t4_integration.py` | A-1: same replacement (`:480-486`, `:540-557`) |
| `tests/test_005_010_reviewfix.py` | A-1: «the single new record of the dispatch» (`:489-500`) |

Nothing outside `tests/**` was touched; `docs/planning/` and `findings/…-2026-10-17.md` remain untracked and unmodified; `tests/.sensitive-patterns.local` was never read.

## 2. Test → PD map (focal)

| PD | Test | Oracle |
|---|---|---|
| PD-1 | `test_pd1_external_dispatch_registers_one_attempt_relayed_by_the_entry` | exactly 1 new ledger record; envelope `attempt` == that record; the fixture module's own log proves it registered |
| PD-2 | `test_pd2_record_writes_only_under_dot_cdad_and_never_the_store` | changed paths ⊆ `.cdad/` ∪ state (only the command's transaction); store bytes identical; state normalized equal |
| PD-3 | `test_pd3_native_result_part_is_byte_exact_and_the_receipt_stays_pending` | staged part bytes == input (sha256), descriptor points at it, `receive` (existing command) ⇒ `semantic_status: pending` |
| PD-4 | `test_pd4_without_final_text_no_staging_no_descriptor_no_receipt` | attempt registered + declared; `.cdad/inbox` unchanged; no `RESULT.json`; no receipt; termination ≠ completed |
| PD-5 | 6 tests (verified / O-3 unknown / parent contradiction / outside-root / membership / packet without `agent`) | `session` only ever comes from the store; contradiction ⇒ rejection naming the key, never `unknown`; membership (nested dir) accepted; only-`agent` version ⇒ `unknown`, neither concurrent session accredited |
| PD-6 | `test_pd6_byte_exact_result_with_unverifiable_identity_keeps_no_session` | `session: null` + non-empty `provenance["session"]`; byte-exact part still staged |
| PD-9 | `test_pd9_exec_config_token_is_rejected_on_dispatch_record_capabilities` | both token forms × `dispatch`/`record`/`capabilities` ⇒ rc≠0, diagnostic names `runtimes.json`, zero writes |
| PD-23 | `test_pd23_native_descriptor_kind_is_derived_from_role_and_substage` | test-writer/red ⇒ `test-writer-role-report`; architect/draft ⇒ `role-report` |

Fixture (declared in the test's docstring): staged copy of the skill tree, `cdad_delegate_u1bfix.py` next to the entry (the convention the product itself declares), disposable SQLite as store (`sessions_db` of the section), `XDG_CONFIG_HOME`/`HOME` redirected. The fixture module's `--observe` returns the observable `session_v2` columns of the correlated row (the keys §2.3 makes the entry evaluate); its columns **are** the fixture's "store version".

**Declared green guard:** the `--exec-config` rejection on the new verbs is already satisfied by U1a's pre-parse sweep (verified by behaviour) — it is reported as a pre-satisfied guard, not as RED.

## 3. A-1 reformulations (declared in this RED, per `plan.md` §4)

All four carry the three required items (test replaced / new postcondition / reason) in their docstrings and in the focal test:

1. `test_005_009_t1_interface.py` — *replaced*: the assertions in which the **interface** wrote the I8 record. *New postcondition*: the interface **relays** the attempt its destination declared and does not register; the `testdest` fixture now registers its own attempt through the existing ledger command (new oracle `assert_single_record_per_dispatch`). *Reason*: one registration per dispatch (D-14/PD-1) removes the interface/worker split inside the external path; the rest of the interface contract is unchanged. The old helper was **kept untouched** so the seven other consumers (`t2`, `t1b_service_mode`, `006_003_u6`, both 005-010 files) stay green.
2. `test_005_010_t1_durable_signal.py` (`:431-449`, `:536-543`) — same replacement; worker assertions (durable-row `session`/`model_reported`) preserved, interface-record block retired.
3. `test_005_010_t4_integration.py` (`:480-486`, `:540-557`) — same.
4. `test_005_010_reviewfix.py` (`:489-500`) — localisation becomes «the single new record of the dispatch»; `model_reported` assertions unchanged.

## 4. Commands and outputs (exact)

```
$ python3 -m pytest -q tests/test_006_005_u1b_dispatch_entry.py
12 failed, 1 passed in 9.62s
   → PD-1: rc=1 «the external transport is not available in this build … arrives with U1b»
   → PD-2/3/4/5(4)/6/23: rc=2 «unrecognized arguments: --attempt-id … --native-result … « (envelope precondition)
   → PD-5 contradiction & outside-root: declared-surface gate (AssertionError naming the missing verb/flags)
   → PD-9: guard, already green (U1a)
```
Focal RED is `AssertionError` on missing behaviour in every case — never Import/Syntax/fixture error. 10 fail on the envelope precondition (the message names the missing verb/transport), 2 on the rejection gate; with the verb absent nothing of the postcondition is observable.

```
$ python3 -m pytest -q <16 files: focal + the declared U1b regressions>
19 failed, 112 passed, 2 skipped in 289s
19 failed = 12 focal (U1b RED) + 4 A-1 t1_interface + 1 A-1 t1_durable_signal + 2 A-1 reviewfix
2 skipped = test_005_009_t4_acceptance (owner-run real integration) + test_005_010_t4_integration (goal: CDAD_OPENCODE_INTEGRATION=1)
```
Per-file A-1 evidence: `t1_interface` 4 failed/8 passed (each on `2 != 1 … la interfaz relaya el attempt y no registra`); `t1_durable_signal` 1 failed/5 passed; `reviewfix` 2 failed/7 passed; `t4_integration` 1 skipped. Adjacent safety: `test_005_009_t2_opencode_adapter.py` 8 passed, `test_006_001_t1b_service_mode.py` + `test_006_005_u1a_runtime_config.py` 35 passed.

Fixture self-check (throwaway probe, not committed): the fixture module answers `--capabilities` (5 keys), `--observe` (row of the disposable store), and a dispatch invocation registers `att-u1b-fixture-0001` and logs `registered: true` — so the RED is satisfiable once the entry resolves/invokes the module and relays its attempt.

```
$ git show --stat --format='' 27b85a4
 tests/test_005_009_t1_interface.py       |  161 +++-
 tests/test_005_010_reviewfix.py          |   33 +-
 tests/test_005_010_t1_durable_signal.py  |   63 +-
 tests/test_005_010_t4_integration.py     |   49 +-
 tests/test_006_005_u1b_dispatch_entry.py | 1318 ++++++++++++++++++++++++++++++
 5 files changed, 1522 insertions(+), 102 deletions(-)
```
Commit `27b85a4` — `test: 006-005 U1b RED — entrada única y registro único por despacho` (explicit `git add` of the 5 test files; no `--no-verify`, no stash, no push; working tree otherwise clean).

## 5. Finding to decide (pre-existing, not caused by this unit)

`tests/test_005_010_t1_durable_signal.py::TestPd6` (an A-1 target) asserts `record["model_configured"] is None` with the comment "this run does NOT provision a delegation config". That premise is false on any host where `~/.config/cdad/delegation.json` exists (it does here): the fixture neither redirects `XDG_CONFIG_HOME` nor `HOME`. Evidence: **at HEAD before my change** the test failed with `'mofgw/deepseek-v4.1-flash' is not None` (`:512`); with `XDG_CONFIG_HOME=/tmp/empty` the failure moves to the A-1 assertion (`:431`), proving the coupling. A-1 keeps this assertion ("se conservan las aserciones del registro del worker"), so the reformulated test cannot go green in this environment even after U1b GREEN. **Proposed minimal fix (not applied, to stay inside A-1's declared scope):** redirect `XDG_CONFIG_HOME`/`HOME` for the dispatch invocation — the precedent already exists in the same family (`delegation_home()` in `test_005_010_t4_integration.py:334`). Orchestrator decides.

Also observed (pre-existing, unrelated to this change): `TestPd2::test_pd2_unreadable_store…` is flaky (failed once, passed on re-run) and `reviewfix::TestR3::…succeeded_without_final_text…` failed once under batch load but passed 3/3 alone — both match the flakiness already documented in `test_005_009_t2_opencode_adapter.py` (waiter margin).

## 6. Declared dependencies (no failing test written for them)

* **scribe row** (`role-report` for `_allowed_kinds("scribe","memory")`) is U7/PD-26; U1b does not touch the table → no scribe case asserted (documented in the PD-23 test).
* **`agent` in the packet** is PD-7/U1c; the packet of this unit carries none, so the «agente» key is exercised in its contracted form (`unknown`, never `cdad-<rol>`), and the discriminators used are `parent` and `project` — no dependency on U1c.

## 7. Limits declared

Running the focal test is subprocess-only; the entry→module channel is pinned by the fixture as `--project-root` + `--packet`/`--packet-id` (or the packet path in argv) + `--exec-config`, and the packet on stdin — the same channel the existing interface already uses (observed). If the implementer chooses another channel, the fixture's permissive discovery (`argv` / env / packet path / single-row fallback, `--session`/`--parent` correlation) covers it; a mismatch would surface as an explicit fixture message, never as a silent pass. No host values appear in the tests; store/binary/config are all tempdir fixtures.