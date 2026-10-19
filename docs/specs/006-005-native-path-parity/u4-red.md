## Report — test-writer / RED (006-005 U4)

### Files modified (committed)
- `tests/test_006_005_u4_single_entry.py` (new, 978 lines) — only file in the commit.
- Commit: `3d23ad6 test: 006-005 U4 RED entrada unica, secciones delegation y borde de adopcion` (`git show --stat`: 1 file changed, 978 insertions).
- Not touched: `docs/planning/`, `findings/…` (untracked, not mine), no implementation files.

### Test → postcondition map (all PD-20, facts taken from the approved spec D-6/§2.x/V-4/V-6)
| Test | Fact / PD |
|---|---|
| `TestPd20FiveD6Rows::test_pd20_mandate_has_the_five_d6_rows_in_order_without_shared_conditions` | PD-20 / §5 D-6 / §2.1 — five conditions, D-6 order, one condition per row, no overlap, decision from `status.entry`/`next`; source **and** recomputed generated |
| `TestPd20NoStaleExecutionJsonCondition::test_pd20_stale_execution_json_condition_is_gone` | PD-20 / V-6 — `.cdad/execution.json` is no longer an entry condition (source + generated) |
| `TestPd20TransportRule::test_pd20_transport_rule_is_declared` | PD-20 / §2.1 / D-9 — same runtime ⇒ native tool + `record`; other runtime ⇒ `cdad_dispatch.py … --runtime` → `receive` |
| `TestPd20DelegationSections::test_pd20_delegation_sections_name_entry_packet_agent_and_module_credential` | PD-20 / §2.5 / §2.7 — both adapter `delegation` blocks and their generated carriers: new entry with `--runtime`, agent travels in the packet (`REQUEST.json.agent`), credential resolved/injected by the module; `--exec-config` not named as the orchestrator path |
| `TestPd20AdoptionBorder::test_pd20_cli_delegation_declares_the_migration_adoption_border` | PD-20 / §2.6.1 / E5 — `cli-delegation.md`: migrate → `capabilities` → dispatch with `--runtime`, `runtimes.json`, one source; nothing says the product reads an exec-config |
| `TestPd20GeneratedDelegationLabel::test_pd20_generated_delegation_label_drops_the_adapter_qualifier` | PD-20 / V-4 — generated heading no longer `## Delegation (adapter)`; delegation section still exists |
| `TestPd20DeterministicStaging::test_pd20_staging_is_deterministic_and_matches_committed_outputs` | PD-20 / plan U4 — `make staging` twice ⇒ same bytes; `agents/**` byte-identical to the recomputed staging |

Oracles read product artifacts only at runtime (source mandate, adapter `delegation` blocks, `cli-delegation.md`, `make staging` recomputed in a temp copy, committed `agents/**`). No implementation text was opened by me; the generated text is recomputed, never taken from the stale `build/staging` in the repo.

### Commands and output (final, post-commit)
1. `python3 -m pytest tests/test_006_005_u4_single_entry.py -q`
   → **6 failed, 1 passed in 4.95s**. All six are `AssertionError` of content, never ImportError/SyntaxError:
   - missing five D-6 rows (old four overlapping entries);
   - stale condition present: `sources/roles/orchestrator.md:24 → **Prepared execution path.** If .cdad/execution.json exists…` and the same lines in both generated orchestrators;
   - transport rule absent (`same runtime ⇒ native + record`);
   - delegation blocks missing entry/`--runtime`/packet-agent/module-credential;
   - adoption border absent in `cli-delegation.md`;
   - generated still titled `## Delegation (adapter)`.
   The passing test is the declared guard: staging is deterministic and `agents/**` matches the recomputation today.
2. U4 regressions (11 files, one run)
   → **2 failed, 81 passed in 109.48s**. Both failures are **pre-existing at HEAD `77d0730`, introduced by earlier units, unrelated to this RED** (my commit adds only the test file):
   - `test_006_003_u3_texts_without_profiles.py::TestInv4InstallableTextWithoutTmp::test_inv4_installable_skill_text_names_no_tmp` → `skills/cdad-cycle/scripts/cdad_packet.py:166` and `:1230` name `/tmp` (INV-4 of 006-002); reproduced alone (1 failed in 0.09s).
   - `test_005_004_t2_installer_claims.py::test_pd2_i_sweep_…` → `skills/cdad-cycle/scripts/cdad_dispatch.py:34` claims the installer strips `model:`; reproduced alone (1 failed in 0.41s).
   Per the role contract I did not edit `skills/**`; the orchestrator decides (A-1 belongs to U1b/U3, not U4).

### A-1 (rule) — declared, no replacement applied
Swept the 11 U4 regression files: none fixes as required content the current four overlapping entries, the `.cdad/execution.json` condition, the `## Delegation (adapter)` label, or the orchestrator path via `cdad_delegate.py --exec-config`. Therefore no test was reformulated. Residual risk declared in the module docstring: `test_005_006_t2_intake.py` derives its intake window from dynamic anchors (`Prepared execution path`, `Legacy path`, `legacy-loads`); it does not assert them as postconditions, but if GREEN removes all three tokens the regression will fail as fixture drift and the orchestrator must decide. No `--no-verify`, no stash, no push.

### Honest limits
Text oracles prove the declared facts are present/absent and co-located; they do not prove the model obeys them (that is U6/PD-22), and prose quality is judged by stage-4 review. `make validate` and the full suite belong to the unit gate/closer and were not run.