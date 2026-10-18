Now let me implement. Starting with `install.sh` — the shared removal rule:
Now the prune reader loop and decision:
Now OPT-1 in the delegation adapter:
All gates are green. Final report:

---

# Implementer report — 006-003 review-fix 2, GREEN

**Packet:** `006-003-installer-single-profile-delegation-config-implementer-green-011` · **Substage:** green · **Contract:** `spec.md` sha256 `c25ebf0e…d890` ✓ (unchanged, read-only input) · **RED under test:** `tests/test_006_003_rf2_review_fixes.py` @ `26667b5`

## 1. Modified files (`git show --stat HEAD`)

```
 install.sh                                         | 142 +++++++++++++++++----
 skills/cdad-cycle/scripts/cdad_delegate_opencode.py |  12 +-
 2 files changed, 124 insertions(+), 30 deletions(-)
```

Nothing else: `tests/**` untouched (invariant), no writes to the real `HOME`, the untracked `docs/planning/` and `findings/…` left alone.

### `install.sh` — B-1 (structural remedy: the column collapse is gone)

| Site | Before | After |
|---|---|---|
| `owned_removal_state` (`:642-671`) | `[ -z "$recorded" ] \|\| bytes match → removable`; comment documented «also when no digest was recorded … the historical rule» | new verdict **`unverifiable`**: no usable digest (empty **or** `null`) → never removable; the empty-digest branch of the rule is annotated (comment at `:643-664` updated to the new rule, incl. why a symlink keeps its historical verdict) |
| `prune_owned_obsolete` emitter (`:1230-1261`) | `"%s\t%s\t%s\t%s\n"` (TSV) | NUL-framed fields (`\0`), `null`/non-string → `""` (never the repr `None`) |
| `prune_owned_obsolete` reader (`:1264-1268`) | `while IFS=$'\t' read -r abs rel sha source` (tab = IFS whitespace ⇒ consecutive tabs = 1 delimiter) | `while IFS= read -r -d '' abs && … rel && … sha && … source` — each field arrives exactly as published, empty ones included |
| prune decision (`:1285-1300`) | `modified) …` | `modified\|unverifiable)`: one outcome, two reasons — `unverifiable` reports *«no recorded sha256 to compare its bytes against; PRESERVED and kept registered»* (never «registered \<source\>»); `*) die` for an unexpected state. The kept record is built from the *exact* fields → `{"sha256": "", "source": <source>}` |
| `uninstall_by_manifest` emitter/reader (`:1400-1440`) | same TSV pair | same NUL framing; `unverifiable` handled with `PRESERVED for explicit resolution`; `removable) ;;` + `*) die` explicit |
| `load_previous_ownership` (`:769-800`) | `IFS=$'\t' read -r rel sha source` | NUL framing (a collapsed digest used to be read as its neighbour at every deploy decision) |
| `check_installed_staging` (`:1687-1751`) | `IFS=$'\t' read -r rel owned_sha source` | NUL framing (an empty digest made the `source` slot empty → a staged artifact misread as legacy) |
| summaries (`:1302`, `:1511`) | «preserved (locally modified …)» | «preserved (locally modified, or with no recorded digest — explicit resolution needed)» |
| plan/keep streams | TSV written by bash | **kept** TSV, with a comment stating why it is immune: they are parsed by *Python* `split("\t", maxsplit=2)`, which preserves empty fields — no bash `read` splits a record anywhere anymore |

No `read` of a manifest record by bash remains: `grep -n "IFS=\$'\\\\t' read" install.sh` → only `:935`, `:1885` (STAGING manifest `rel<TAB>sha`, sha last: immune) and `:1747` (`rel<TAB>sha`, sha last, only `rel` used).

### `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` — OPT-1

`_unauthorized_diagnosis`: `path = credential["path"] or _credential_file_path()` (the RESOLVED path — the configured `credential_env_file` or the default) and the ENVIRONMENT branch now closes with *«no credential file was consulted — to move the credential there, the alternative is the credential file <path> … with mode 0600 or 0400»*. Docstring updated. The value is never interpolated (INV-1).

## 2. Gates — test → result

**Focal (`tests/test_006_003_rf2_review_fixes.py`) — the RED oracle**

| Test | Result |
|---|---|
| `test_b1_a_empty_digest_without_source_is_preserved_and_disclosed` | **PASS** |
| `test_b1_a2_uninstall_does_not_remove_an_empty_digest_record` | **PASS** |
| `test_b1_b_empty_digest_with_present_source_publishes_a_coherent_record` | **PASS** |
| `test_b1_c_null_digest_publishes_a_coherent_record` | **PASS** |
| `test_b1_control_correct_digest_still_retires_the_obsolete_own_file` | **PASS** (healthy prune intact) |
| `test_opt1_wrong_env_credential_diagnosis_also_names_the_default_file` | **PASS** |

**Proportional regression + every install.sh-invoking suite I could identify**

| Batch | Result |
|---|---|
| `tests/test_006_003_*.py` + `test_install_ownership.py` + `test_install_review5_regressions.py` + `test_005_004_t2_installer_claims.py` (re-run post-commit) | **90 passed** |
| `test_004_001_acceptance_matrix.py` `test_004_001_t6.py` `test_005_004_t2…` `test_006_003_u2…` `test_006_003_u8…` | **32 passed** |
| `test_004_003_t2_plan_review.py` `test_packet_prepare.py` `test_003_002_t4_integration.py` `test_005_005_t4_integration.py` `test_role_packet_consumers.py` `test_004_002_t6_landing.py` `test_role_packets.py` (the other install.sh invokers) | **51 passed** |
| `test_005_009_t2_opencode_adapter.py` `test_006_001_t1_selection.py` `test_006_001_t2_wait_recovery.py` `test_005_007_t4…` `test_opencode_read_map_and_steps.py` `test_cdad_adapters_opencode.py` (adapter consumers of the changed file) | **52 passed** |
| Post-comment-edit targeted: `rf2` + `rf_review_fixes` + `u7_prune_obsolete` + `u6_server_credential` | **22 passed** |
| `bash tests/validate-consistency.sh` | **1 FAIL: `F011: scripts/validate-subagents.sh (active profile)`** — the declared HOME drift, unchanged (evidence below) |

No `'timeout'` flake occurred in any run; nothing had to be retried in isolation.

## 3. Commands and output (verbatim tails)

```
$ bash -n install.sh && echo "install.sh OK" && python3 -m py_compile skills/cdad-cycle/scripts/cdad_delegate_opencode.py && echo "py OK"
install.sh OK
py OK

$ timeout 900 python3 -m pytest tests/test_006_003_rf2_review_fixes.py -q
......                                                                   [100%]
6 passed in 67.10s (0:01:07)

$ timeout 2400 python3 -m pytest tests/test_006_003_*.py tests/test_install_ownership.py tests/test_install_review5_regressions.py tests/test_005_004_t2_installer_claims.py -q
........................................................................ [ 80%]
..................                                                       [100%]
90 passed in 795.97s (0:13:15)

$ bash tests/validate-consistency.sh   # tail
PASS: F011 (B8): validate-subagents.sh still verifies impl.diff's format (well-formed diff)
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
PASS: F011: tests/validate-odoo-specialization.sh → PASS (zero regression over cdad-003/004)
FAIL: 1 assert(s) failed.
```

**F011 is the pre-existing real-HOME drift, not this change** (`timeout 300 bash scripts/validate-subagents.sh`):

```
DRIFT: differs <home>/.claude/skills/cdad-cycle/SKILL.md
DRIFT: differs <home>/.claude/skills/cdad-cycle/assets/opencode-exec-config.example.json
❌ install.sh --check failed (rc=1)   # drift against the host's OLD ~/.config, ~/.claude, ~/.agents installs
✅ models OK (no agent fixes a model)
```

The concrete drifted files are ones this packet never touched (the host install predates the current sources); the dir-level drift list is the host's old install vs the repo. Reading that host tree is the validator's own declared behaviour (it cross-checks `[repo]` vs the installed root); this role wrote nothing outside the redirected temp roots.

## 4. Commit

```
d52084e fix: 006-003 review-fix 2 GREEN (B-1 sha-less manifest records never removable + OPT-1 env-branch diagnosis names the credential file)
 install.sh                                         | 142 +++++++++++++++++----
 skills/cdad-cycle/scripts/cdad_delegate_opencode.py |  12 +-
 2 files changed, 124 insertions(+), 30 deletions(-)
```

`git status --short` after the commit: only the two modified files staged/committed; `?? docs/planning/`, `?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md` untouched. No `--no-verify`, no `git stash`, no push. (`--amend` used once, and only to repair a word my shell ate from the message — the tree is identical.)

## 5. Honesty / out of scope

- **B-1 closing condition 5 (`rf-red.md` §4 correction) is not mine to do:** `docs/**` is not in this packet's write scope, and the task's QUÉ CAMBIA lists only `install.sh` + the adapter. Reported here, not edited (the orchestrator owns that record).
- **`--dry-run` on a degenerate record** was not re-probed black-box (not in B-1's closing conditions): by code path it cannot delete (`do_run` only logs) and now announces `DRY-RUN CONFLICT … preserved (… no recorded sha256 …)`. Stated as a code reading, not a measurement.
- **Symlinks deliberately keep the historical removable verdict** even with an empty digest (unlinking destroys nothing of the user's); documented in the rule's comment. The rf2 oracles only exercise regular files.
- **Test snapshot, not just final state:** the RED file was read (`git show 26667b5`, working-tree copy) before implementing; the full suite was run twice (pre- and post-commit) with the same result; no test was edited, and `git diff HEAD~1 HEAD --stat` shows only the two implementation files.
