The fixture fix is committed as `51b89346`, tests only. The five audited cases still fail RED, and every other u1b and u1a case passes. I did not read or edit implementation code or docs.

**Intake.** I validated the packet with `cdad_packet.py validate-request` and `validate-packet` against the on-disk `REQUEST.json` and `PACKET.md`; both returned rc=0. I did not run `intake --received`, because the dispatch text was not available to me as a file or on stdin. So this is not automated received-dispatch validation.

**Fixture correction** (`tests/test_006_005_u1b_dispatch_entry.py`):
- **Unavailable observation:** the fixture module's `--observe` now exits rc=3 and writes `observation surface unavailable: no-store` (or `no-schema`) to stderr. Its log entry records `unavailable: true`.
- **No matching row:** a successful observation with no matching row, or an ambiguous one, still prints `null` with rc 0. Production code is not asked to interpret fixture-specific reasons.
- **PD-4 explicit-input cases:** they are now labelled `missing`, `empty` and `directory (not a regular file)`. A fourth case uses a real regular file with chmod 0, and runs only if `os.access` confirms the executing OS user (uid 1000) is denied.
- **Controls and nodeids:** the original controls and the five audited nodeids are unchanged.

**Collection evidence.** Both runs collect 36 tests, and the sorted lists of nodeids are identical (`diff` printed `NODEIDS_IDENTICAL`). The "before" run was against a `git archive` of `2f7e1d7f^` extracted to `/tmp/nrc-parent`.

**Commands and results.** Files are in `tests/.native-record-evidence/`, committed in `51b89346`:
- **Collection:** `pytest --collect-only -q <u1b> <u1a>` gave rc=0 both times (`collect-before-parent-2f7e1d7f.txt`, `collect-after.txt`).
- **Focal five:** `pytest -q -rf -k "pd4 or pd6 or pd9 or pd5_native_only or pd5_native_contradiction" <u1b>` gave rc=1, **5 failed, 1 passed, 11 deselected** (`focal-five.txt`).
- **Full u1b + u1a:** `pytest -q -rf <u1b> <u1a>` gave rc=1, **5 failed, 31 passed** in 77.86s (`full-u1b-u1a.txt`).

The five failing nodeids are the same in both runs:
1. `TestPd4WithoutFinalTextThereIsNoDelivery::test_pd4_without_final_text_no_staging_no_descriptor_no_receipt`
2. `TestPd5NativeCorrelation::test_pd5_native_contradiction_is_a_rejection_naming_the_key`
3. `TestPd5NativeCorrelation::test_pd5_native_only_agent_evaluable_is_unknown_o3`
4. `TestPd6UnverifiableIdentityKeepsNoSession::test_pd6_byte_exact_result_with_unverifiable_identity_keeps_no_session`
5. `TestPd9NewVerbsRejectTheRetiredToken::test_pd9_exec_config_token_is_rejected_on_dispatch_record_capabilities`

The focal run's 1 pass is the audited `test_pd5_native_only_agent_evaluable_is_unknown_o3`-adjacent selection's sixth match, not an audited failure; focal and full agree on the same five failures.

**Right reason.** All five are `AssertionError`s from the entry returning `no execution configuration for runtime u1bfix … has no u1bfix section`, which is the pending defect. There are no import, syntax or setup failures.

**Mapping.**

| PC | Test |
|---|---|
| PC-1, PC-2, PC-3, PC-4 | PD-6 partitions and PD-5 only-agent with `{}` |
| PC-5 | PD-5 contradiction |
| PC-6 | PD-4 |
| PC-7, PC-8 | PD-9 |
| PC-9 | unchanged u1a and u1b controls |

**Live-inventory textual delta (no docs edited).** There are no new nodeids. The u1b capability entry should note the added protection "native recording without external configuration, PC-1..PC-8". Four files are now committed under `tests/.native-record-evidence/` and are not in `suite-inventory.json`. Integrity is not a RED gate here.

**Limits.**
- **Unreached cases:** the PD-4 unreadable-regular-file case and the later explicit-input cases only run after the earlier unavailable-observation step passes. They have not yet executed, so they are exercised only once GREEN exists.
- **Whether the entry treats rc≠0 as "unavailable":** this stays unverified until implementation (PC-4, PC-6).
- **Existing stash:** `stash@{0}` is not mine and I left it alone.
- **`runtime` and `credential_env_file` keys:** the earlier limit stands. No new assertions for them, because the contract names only `model` for rejection.

No correction ceiling was extended.
