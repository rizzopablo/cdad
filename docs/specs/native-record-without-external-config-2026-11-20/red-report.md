RED is in and committed as `2f7e1d7f`. It is tests only: `tests/test_006_005_u1b_dispatch_entry.py`, no implementation read or edited. The five audited cases fail on the missing-section defect, and all other u1b and u1a cases pass.

**Intake.** I validated the dispatch with `cdad_packet.py intake --project-root <root> --received -`, feeding the received text on stdin. It returned route C with `packet_id` and `execution_id` matching.

**Commands and results**
- **Baseline collection:** the file has 17 test methods before and after. A sorted diff of `def test_*` names against `HEAD` printed `NODEIDS_EQUAL`.
- **Adapted cases:** `pytest -q <u1b> -k "pd4 or pd6 or pd9 or pd5_native_only or pd5_native_contradiction"` gave 4 failed, 2 passed. The 2 passes were two of the five audited cases; the five-case total was 4 failed, 1 passed.
- **Full u1b + u1a:** `pytest -q <u1b> <u1a>` gave 5 failed, 31 passed. The 5 failures are exactly the five audited cases. Every control I did not adapt passes, including the external controls and u1a's PD-8/PD-9.
- **Right reason:** the failures are assertion failures from the entry's `no execution configuration for runtime u1bfix … has no u1bfix section`. They are not import, syntax or fixture errors.
- **`cdad-suite.py validate`:** it reports integrity insufficient because `tests/install_backup_oracle.py` and `tests/install_harness.py` are not in the inventory. I did not touch either, and integrity is not a RED gate.

**What changed**
- **Fixture module:** its `--observe` log entry now also records the configuration it received (`config`, `config_passed`).
- **Helpers:** I added fresh-project, configuration-partition (`set_runtimes`), observation-log, no-effects and staged-bytes helpers. `new_project` gained an optional `tag`.
- **PD-6 (PC-1..PC-4):** the original assertions stay. Six new partitions each run in a fresh project: no `runtimes.json`, no `runtimes` key, no section for the runtime, empty map, empty section, and a `--since`-only no-motive case. Each asserts rc 0, `completed + staged`, null session, an explanation, one attempt, original bytes staged and no receipt. It also asserts exactly one module observation when motivated and zero when not.
- **PD-5 only-agent (PC-3):** a new case with an empty section and native bytes asserts exactly one observation, with the module receiving `{}` and no `sessions_db`, and `unknown` identity.
- **PD-5 contradiction (PC-5):** the original assertions stay. New cases run with native bytes under full, absent and empty-map configuration. They assert `blocked + none + null` naming `parent`, one observation, and no ledger or inbox effect.
- **PD-4 (PC-6):** the original control stays. New cases cover unavailable observation (nonzero, no effects, and the failure must not be the missing-config diagnostic), plus explicit missing, empty and unreadable (a directory) `--native-result` inputs, each nonzero with no effects.
- **PD-9 (PC-7/PC-8):** the token sweep stays. New native `record` cases each fail nonzero with no effects: invalid JSON, `runtimes.json` as a directory, a non-object section (list and string), and a `model` key with `delegation.json` guidance. Two invalid-runtime cases (`Bad/Id` and a runtime with no module) also assert the rejection is not the missing-config one.

**Defect sensitivity.** The PD-6 partitions, the PD-5 `{}` case and the PD-5 contradiction-with-bytes case all fail today on the missing-section error. PD-4 and PD-9 are mixed: some of their new cases already pass today, as guards.

**Limits and risks**
- **`runtime` and `credential_env_file` keys:** I did not assert rejection for them. A first run showed the entry accepts a section containing `runtime`, and only `model` has existing rejection coverage. If the spec means those keys must be rejected on the native path, the implementer must handle that.
- **Fixture "unavailable":** it returns `null` for a missing store, indistinguishable from "no candidate". Whether the entry treats that as unavailable (PC-6 nonzero, no effects) is unverified until implementation.
- **PD-5 unmotivated cases:** I did not add a native-bytes, no-motive case there. The no-motive observation count is covered in PD-6 only.
- **Unprovable assumption:** the assertion that the module receives `{}` assumes the entry passes the section by `--exec-config` or `CDAD_EXEC_CONFIG`, as the existing fixture does.
- **Pre-existing stash:** `git stash list` shows one stash that is not mine; I left it alone.

**PC mapping**

| PC | Test |
|---|---|
| PC-1, PC-2 | PD-6 partitions |
| PC-3 | PD-6 no-motive partition; PD-5 only-agent with `{}` |
| PC-4 | PD-6 unavailable-surface partitions |
| PC-5 | PD-5 contradiction |
| PC-6 | PD-4 |
| PC-7, PC-8 | PD-9 |
| PC-9 | unchanged u1a controls |

**Live-inventory delta (text only, docs not edited):** no new files or nodeids, so nothing to add to `suite-inventory.json` or `pc-map.json` for new tests. The capability entry covering these u1b cases should note the new protection "native recording without external configuration, PC-1..PC-8".

**Correction rounds:** none consumed.
