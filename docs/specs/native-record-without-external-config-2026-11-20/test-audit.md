Auditing now: I've read the spec, the discovery notes and the existing native-record/config tests, and I'm writing the read-only audit report. I have not read implementation code or edited any tests.

# AUDIT report — `native-record-without-external-config-2026-11-20` (test-writer, audit, round 1 of 2)

**Intake.** I ran `cdad_packet.py intake --project-root <root> --received -` on the Route C identification. It returned rc=0, route C, with the packet and execution ids matching. I validated no inline body, because route C carries none. I read nothing outside the declared scopes.

**Files modified:** none. **Commit:** none. **Tests run:** none. Audit is read-only.

**Commands run:**
- `cdad_packet.py intake …`
- read/grep/ls of `tests/test_006_005_u1b_dispatch_entry.py`
- read/grep of `tests/test_006_005_u1a_runtime_config.py`
- grep of the other 006-005 files that call `record`

## 1. Existing verifiers and what they protect

| Test (nodeid kept) | Today it protects |
|---|---|
| `u1b::TestPd2…test_pd2_record_writes_only_under_dot_cdad…` | The write boundary of `record`, with `runtimes.json` always present. |
| `u1b::TestPd3…test_pd3_native_result_part_is_byte_exact…` | Staging of the exact bytes, the descriptor binding, and a receipt that stays `pending`. |
| `u1b::TestPd4…test_pd4_without_final_text…` | With no native text and observation available, one attempt is registered and nothing is staged. |
| `u1b::TestPd5…` verified, only-agent, ancestor and project-key cases, plus `TestPd5E1…` | Positive-correlation thresholds and ancestor/membership rules. |
| `u1b::…test_pd5_native_contradiction_is_a_rejection_naming_the_key` | Contradiction is a rejection naming `parent`. It has no native bytes and no check that nothing was registered or staged. |
| `u1b::…test_pd5_native_session_outside_the_authorized_root…` | Contradiction on the project key. |
| `u1b::TestPd6…test_pd6_byte_exact_result_with_unverifiable_identity…` | `session: null`, a provenance string, and a byte-exact part. It only runs with config present and a session declared. |
| `u1b::TestPd9…test_pd9_exec_config_token_is_rejected…` | The retired token on every verb. |
| `u1b::TestPd23…` | The derived descriptor kind. |
| `u1a::TestPd8…` (4 `--runtime` cases plus the no-module case) and `TestPd9…` (missing section, `model` key, derived section, retired token) | External dispatch fail-closed and the runtime-resolution diagnostics. They use `dispatch`, not `record`. |
| `test_006_005_reviewfix.py` (B2), `test_006_005_u6fix4_native_selection.py`, `test_006_005_u6fix6_model_parity.py` | `record` against the real OpenCode module with `sessions_db` configured. They are the configured-observation controls. |
| `test_006_005_u4_single_entry.py` | Reference-text pins for `cli-delegation.md`. |

**Coverage gaps:**
- No existing test runs `record` with `runtimes.json` absent, the section absent, or the map `{}` (PC-1, PC-2, PC-4).
- None checks the observation count or the section passed to the module (PC-3).
- Contradiction is never checked together with native bytes and no-effect (PC-5).
- The no-final-text case is never run with observation unavailable (PC-6).
- Native invalid JSON or a non-object section is never exercised (PC-7).
- Native `--runtime` rejection is never exercised (PC-8).

## 2. Dispositions (exactly one per test), keeping nodeids

**Extender**
- `u1b::test_pd6_byte_exact_result_with_unverifiable_identity_keeps_no_session`. **Promise A, PC-1, PC-2, PC-4 (PC-3 negative).**
  - Add configuration partitions inside the existing test with `subTest`: no `runtimes.json`, a file with no `runtimes` key or no section for the runtime, and `runtimes: {}`. The control with the full section stays, so the original assertions stay too.
  - Each partition keeps the existing assertions and adds:
    - rc=0
    - an envelope with `termination` `completed`, whatever the descriptor says, with the staged part byte-exact
    - `session` and `model_reported` null
    - a `provenance` or diagnosis that explains the missing evidence
    - exactly one new attempt
    - no receipt
  - The partitions that declare a session use an unavailable observation surface (PC-4), including a missing store. Assert the declared session value is not copied into the accredited identity (`session` null, the declared id absent as an accredited value).
  - One no-motive partition (no `--session` and no `--parent`, only `--since` and native bytes) asserts zero `observe` entries in the fixture module log (PC-3 negative).
  - Without this test, a user on a default installation completes native delegation and still cannot record or receive it.
- `u1b::test_pd5_native_contradiction_is_a_rejection_naming_the_key`. **PC-5 (and the PC-3 observation).**
  - Keep the original controls and add a native-bytes variant.
  - Assert rc and envelope `blocked + none + null` naming `parent`, zero new attempts, nothing in the inbox and no descriptor.
  - Run it also with an empty `{}` or absent section, so the contradiction returned by the module still blocks.
  - Without this test, a user could have a contradicting session accredited just because the native bytes exist.
- `u1b::test_pd4_without_final_text_no_staging_no_descriptor_no_receipt`. **PC-6.**
  - Keep the available-observation control: one attempt, `unknown + none`, no part, descriptor or receipt.
  - Add a partition with unavailable observation (no store, empty section): rc≠0, zero attempts registered, no staging.
  - Add explicit missing, empty and unreadable `--native-result` inputs: rc≠0 and never treated as omitted.
  - Without this test, a user could get a registered delivery when no final text exists.
- `u1b::test_pd5_native_only_agent_evaluable_is_unknown_o3`. **PC-3 observation.**
  - Add one sub-case of this existing observation control where the runtime section is `{}`.
  - Assert exactly one module `observe` call, whose logged received configuration is `{}` and has no `sessions_db`, with the unchanged `unknown` result.
  - The fixture module needs one test-side change: its `--observe` log entry records the config it received. That lives in the test file.
  - Without this test, motivated observation could be skipped on a default installation, so contradictions would go unseen.
- `u1b::test_pd9_exec_config_token_is_rejected_on_dispatch_record_capabilities`. **PC-7, PC-8.**
  - Keep the token sweep. Add native `record` subtests, each rc≠0 with a snapshot proving no durable registration or staging:
    - invalid JSON
    - an unreadable file
    - a non-object `runtimes` or section
    - a `model` key, still naming `delegation.json`
    - a missing, invalid or no-module `--runtime`, even with native text present
  - Without this test, a broken configuration would be silently ignored, or an invalid runtime would succeed when native text exists.

**Mantener** (preserve exactly)
- `u1b::test_pd2_record_writes_only_under_dot_cdad…` and `test_pd3_native_result_part_is_byte_exact…` keep their PD-3 byte-integrity and reception role, which the spec requires.
- The remaining `u1b` PD-5/E1 cases, PD-23 and PD-1.
- All `u1a::TestPd8*` and `TestPd9*` cases. They are the external fail-closed guards for PC-9: the missing-section diagnostic, `model` rejection, retired token, and migration.
- `reviewfix` (B2), `u6fix4` and `u6fix6`: the configured-observation controls.
- `u4_single_entry`: the reference-text pins.

**Añadir:** none proposed. **Sustituir, Consolidar, Retirar:** none. No new physical files and no nodeid changes, so no POST-AUDIT substitutes are expected.

## 3. PC → test mapping

| PC | Test | Disposition |
|---|---|---|
| PC-1, PC-2 | PD-6 partitions | Extender |
| PC-3 | PD-5 only-agent with `{}`, and PD-6 no-motive partition | Extender |
| PC-4 | PD-6 unavailable-surface partitions | Extender |
| PC-5 | PD-5 contradiction | Extender |
| PC-6 | PD-4 | Extender |
| PC-7, PC-8 | PD-9 native subtests | Extender |
| PC-9 | `u1a` Pd8/Pd9 external cases, `capabilities`, installer cases | Mantener (retained regression) |

## 4. Observations and risks

- **Fixture change.** The PD-6 and PD-5 partitions rely on the fixture module, which finds its own store when no `sessions_db` is passed. That behaves like a module that can still observe. Pure "unavailable observation" partitions should use a store-less fixture state. The fixture's `observe` log must record the received configuration. Both are edits in `tests/` only.
- **Ordering unspecified.** The spec doesn't fix whether configuration errors (PC-7) or packet admission come first for `record`. PC-7 tests should use a valid packet so either order passes.
- **Truncated read.** I did not re-read the `u1b` cases between lines 1200 and 1500 (E1/U63), so I haven't checked them for config coupling. They stay Mantener.

## 5. Live-inventory delta (text only; docs not edited)

The only documentary deltas are:
- No new test files, so nothing needs adding to `suite-inventory.json`.
- The mapping and docstrings in `tests/test_006_005_u1b_dispatch_entry.py` (PD-4, PD-5, PD-6 and PD-9) would gain PC-1..PC-8 traceability.
- The inventory capability entry that lists these tests should note the new protections (native recording without external configuration).
- `python3 scripts/cdad-suite.py validate` was not run and is not an audit gate.

**Round and ceiling:** audit family round 1 of 2. Nothing is blocking. Verification still required: POST-AUDIT is unnecessary, since there are no sustitutos. The next gate is user approval of this audit, then RED with defect-sensitive evidence for PC-1 through PC-8.
