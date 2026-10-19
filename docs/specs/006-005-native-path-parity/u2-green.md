All gates run. Final evidence below.

## Role report — implementer, `006-005-native-path-parity`, substage **GREEN** (unit U2)

### 1. Modified files (write scope only)

| File | Change |
|---|---|
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` | **modified** (+435 / −41). Nothing else. `tests/` untouched (`git show --stat HEAD`: 1 file). The pre-existing untracked `docs/planning/` and `findings/incremental-construction-and-reproducible-validation-2026-10-17.md` are not mine and were not touched. |

### 2. What changed, per postcondition

| PD | Implementation |
|---|---|
| **PD-11** (D-ADP-1, INV-11) | `_preflight_server` now relays `credential_value` (the credential resolved with the precedence already in force: env `OPENCODE_PASSWORD`→`OPENCODE_SERVER_PASSWORD`, then the 0600 file); `delegate` takes it **only** in the `server` effective mode and `_invoke_destination(..., credential_env=…)` injects it as `OPENCODE_PASSWORD` **only into the child env**, next to the pinned `PWD`. Never in argv/outputs/I8/receipt; `standalone`/`service` inject nothing (`client_credential` stays `None`). |
| **PD-14** (D-ADP-4, INV-13) | New `_packet_agent(request, role)`: agent = `REQUEST.json.agent` (role+`stack`, PD-7), else `cdad-<role>` **plus a diagnosis note declaring the absent field**. `_check_derived_agent_published(project_root, agent)` now verifies **that** agent (fail closed before dispatch, naming it); the invocation carries it (`--agent`). |
| **PD-5 external** (§2.3, INV-15) | `_check_durable_identity` → `_durable_identity_verdict(row, packet_agent)` with a closed triple: `match`; `contradiction` → **rejection** `blocked` naming the `agent` key; `unknown` (either side not evaluable) → `unknown`, **no delivery**, never compared against a supposed value. No parent comparison, no `directory == root` equality anywhere. |
| **PD-23 external** (§2.8, INV-14) | `FINAL_TEXT_ARTIFACT_KIND` (fixed constant) removed; `_derived_artifact_kind(role, substage)` derives from `cdad_result._allowed_kinds` (the single source, the table the module already imports): exactly-one-kind ⇒ it; `role-report` admitted ⇒ it; scribe (§2.8.3) ⇒ `role-report`. **`_allowed_kinds` is NOT touched** (U7). `_persist_delivery` writes the derived kind in `descriptor.parts[].artifact_kind`. |
| **PD-10 / PD-12 / PD-13** (§2.2/§2.3, INV-6) | `--capabilities`: exactly the five keys (the entry requires the exact set, `cdad_dispatch.py:975`); `session_correlation` = identity key `agent` observable **and** ≥1 discriminating key observed (parent / moment / project-directory, O-3) and the `reason` declares the observed columns and names what is missing. `--observe`: ONE bounded `mode=ro` access, no polling; requires the keys it evaluates (fails closed naming the absent column, e.g. `agent`); returns the correlated row (by the chosen `--session`, or the native `--parent`) with the declared `store_reads` counter. |
| **attempt** | Unchanged: still declared in the envelope by the module (its own record). |

### 3. Test → result (focal, `tests/test_006_005_u2_opencode_module.py`)

| Test | Result |
|---|---|
| `TestPd11::test_pd11_server_mode_injects_the_resolved_credential_into_the_client_env` | GREEN (was RED) |
| `TestPd11::test_pd11_standalone_injects_nothing` | GREEN (anchor preserved) |
| `TestPd14::test_pd14_run_argv_carries_the_agent_of_the_packet` | GREEN (was RED) |
| `TestPd14::test_pd14_unpublished_packet_agent_fails_closed_before_dispatch` | GREEN (was RED) |
| `TestPd14::test_pd14_packet_without_agent_uses_the_role_agent_and_declares_it` | GREEN (was RED) |
| `TestPd5::test_pd5_external_association_is_the_session_the_module_chose` | GREEN (anchor) |
| `TestPd5::test_pd5_external_accepts_a_directory_inside_the_project_and_elsewhere` | GREEN (anchor) |
| `TestPd5::test_pd5_foreign_agent_row_is_a_rejection_that_names_the_key` | GREEN (anchor) |
| `TestPd12::test_pd12_external_accepts_a_store_without_parent_nor_directory` | GREEN (anchor) |
| `TestPd12Pd13::test_pd12_observe_returns_the_correlated_row_of_the_installed_schema` | GREEN (was RED) |
| `TestPd12Pd13::test_pd12_observe_fails_closed_naming_the_absent_column` | GREEN (was RED) |
| `TestPd12Pd13::test_pd13_observe_is_one_read_only_access_and_declares_its_counter` | GREEN (was RED) |
| `TestPd10::test_pd10_installed_schema_accredits_correlation_and_names_columns` | GREEN (was RED) |
| `TestPd10::test_pd10_only_agent_store_denies_correlation_naming_the_key` | GREEN (was RED) |
| `TestPd10::test_pd10_module_without_the_new_surface_does_not_accredit` | GREEN (anchor) |
| `TestPd23::test_pd23_plan_review_kind_materializes_with_identical_sha` | GREEN (was RED) |
| `TestPd23::test_pd23_test_writer_kind_materializes_with_identical_sha` | GREEN (was RED) |
| `TestPd23::test_pd23_architect_draft_kind_stays_role_report` | GREEN (anchor) |
| `TestPd23::test_pd23_scribe_declares_role_report_and_its_row_is_u7` | GREEN (anchor) |

**19 passed** — the 11 RED of `9a260c4` and the 8 declared anchors intact.

### 4. Exact commands and outputs

```
$ python3 -m pytest tests/test_006_005_u2_opencode_module.py -q
19 passed in 19.12s

$ python3 -m pytest tests/test_cdad_adapters_opencode.py tests/test_005_009_t2_opencode_adapter.py \
    tests/test_006_001_t1b_service_mode.py tests/test_006_001_t2_wait_recovery.py \
    tests/test_006_001_t3_concurrency.py tests/test_006_003_u6_server_credential.py \
    tests/test_003_003_t2_preflight.py -q
51 passed in 82.67s

$ python3 -m pytest tests/test_005_007_t4_architect_report_materialization.py \
    tests/test_003_002_t2_materialize.py tests/test_003_002_t2_reviewfix.py \
    tests/test_003_002_t1_receive.py -q
37 passed in 48.54s

$ python3 -m pytest tests/test_006_005_u1a_runtime_config.py tests/test_006_005_u1b_dispatch_entry.py \
    tests/test_006_005_u1c_packet_agent.py -q          # focales hermanos U1a/U1b/U1c
37 passed in 61.90s

$ python3 -m pytest tests/test_005_010_t2_load_mode_invocation.py tests/test_005_009_t4_acceptance.py -q
9 passed, 1 skipped in 12.74s

$ python3 -m pytest tests/test_006_005_u2_opencode_module.py -q   # baseline before the change (HEAD cdc48b8)
11 failed, 8 passed in 18.60s
```

Black-box probe of the new surfaces (no real runtime launched, no real store/config read):

```
$ python3 cdad_delegate_opencode.py --capabilities
{"external_transport": true, "native_observation": false, "reason": "the execution configuration declares no durable session store (`sessions_db`): … ; the execution configuration declares no destination binary (`binary`): the version cannot be observed", "session_correlation": false, "version": "unknown"}   rc=0
$ python3 cdad_delegate_opencode.py --observe
`--observe` requires the durable session store (`sessions_db`) in the execution configuration   rc=2
```

### 5. `make validate` — F011 **environmental** (declared)

```
$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
$ bash scripts/validate-subagents.sh          # the cause
DRIFT: differs <home>/.claude/skills/cdad-cycle/references/cli-delegation.md
❌ install.sh --check failed (rc=1)
```
The only failing assert is F011's `install.sh --check`, which compares the **installed** skill copies under `$HOME` with the repo: the drift it names is `references/cli-delegation.md` in the installed trees — an environmental condition of this host, independent of the file this unit changes (my file is not in the drift list). No other assert fails.

### 6. Flakiness of the waiter under load — reported, not hidden

Across three runs of the heavy regression battery, two runs showed `timeout` terminations with the *interface's own* envelope (`destination 'opencode' did not answer within 2.0 seconds`), each green in isolation:

| Failing test (loaded battery) | Isolated run |
|---|---|
| `test_006_001_t1b_service_mode.py::TestPd3ServiceProvenance::test_pd3_service_provenance_pairs_on_completed_service_dispatch` | `1 passed in 1.63s` |
| `test_005_009_t2_opencode_adapter.py::TestPd6::test_pd6_termination_vocabulary_from_material_facts_rc0_no_gate` + `TestPd7::test_pd7_bounded_context_single_dispatch_final_text_delivery` | `2 passed in 8.34s` |
| (third battery run) | `51 passed in 82.67s` — no flake |

The dispatch path gained only O(1) dict lookups (the new `--version`/store work is confined to the `--capabilities`/`--observe` surfaces), so the bound is consumed by host load, not by this change. No oracle was loosened.

### 7. Commit

```
$ git commit -m "feat: 006-005 U2 GREEN — modulo OpenCode: credencial inyectada al cliente en mode server, agente del paquete (REQUEST.json.agent), kind derivado de rol/subfase, capabilities/observe acotado (una lectura mode=ro con store_reads) y correlacion externa por el id de sesion elegido"
[main eb677a9] 1 file changed, 435 insertions(+), 41 deletions(-)
```
No `--no-verify`, no `git stash`, no push.

### 8. Declared decisions and limits (honest)

- **`--observe --parent`.** The focal only exercises `--session`; I also accept `--parent` because the entry's own declared call passes it (`cdad_dispatch.py:540-552`) and the native path has no session id from the transport, so without it the module's observation surface would be unreachable for that path. No focal oracle covers it (declared as extra, covered by U6).
- **`_observe` document shape.** The observation is the correlated row **plus** `store_reads` (the entry consumes the answer as the row, `cdad_dispatch.py:564-575`; PD-13 requires the counter in this output per the RED's declared note).
- **Scribe kind.** `role-report` for the scribe is derived in the **module** (§2.8.3) because the table's scribe row only admits it from **U7/PD-26** and the row is not touched here; after U7 the table branch handles it first, the branch being a declared transcription of §2.8.3.
- **Observation for the orchestrator (not a U2 gate).** The entry asks the capabilities surface with **no configuration** (`cdad_dispatch.py:955`: `[python, module, "--capabilities"]`, no section/`--destination`), so the real module can only answer *honestly*: `version: unknown`, `session_correlation: false`, `reason` naming what it cannot observe (it receives neither a config nor a runtime id, so it cannot resolve a `runtimes.json` section). This does not affect any U2/U1 focal or regression, but it limits the §2.6.1 verification (`capabilities --runtime X`) to a declared — not accredited — answer for the real module. Passing the derived configuration to `capabilities` is U1b (entry) surface: routed to the orchestrator, not changed here.
- No approved oracle was found to contradict another; no test was edited.