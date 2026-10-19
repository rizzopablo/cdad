Implementation complete and committed. Report below.

## 1. Files modified (implementation only — `tests/` untouched)

| File | Change |
|---|---|
| `scripts/cdad-generate.py` | `_write_lever_lines()` → `_write_key_note_lines()` emitting the brief note «la clave `write` no se emite: v2.0.27 la evalua para la escritura y anularia el mapa `edit` (U6-7)»; removed the three `  write: ask` emissions (test-writer / implementer / read-only+orchestrator branches). |
| `sources/agents/adapters/opencode.md` | Canonical source aligned: frontmatter bullet now declares `write` is NOT emitted (U6-7, watch rule fulfilled); `tool-loading` no longer says delegation depends on the lever (P3: subagent invocation needs no lever). |
| `skills/cdad-cycle/scripts/cdad_packet.py` | Derived implementer/`-odoo` `edit` map: added the role's test conventions (`_IMPLEMENTER_TEST_GLOBS`, the same barrier the generator emits) with PD-7/B3 precedence preserved (conventional denies → implementation-root allows → policy test/colocated denies). |
| `agents/cdad-*.md` (11 files) | Regenerated declared outputs via `make agents` (staging → repo). `agents/claude-code/*` unchanged. |

Key structural detail (declared, because two approved oracles meet here): the new U6-7 oracle requires the derived `cdad-implementer-odoo.md` to deny `addons/m/tests/test_m.py` even under a `cdad`-layout policy, while the pre-existing B3 regression (`test_004_002_t5_reviewfix.py::test_reviewfix_b3_nested_tests_dir_not_amplified`) forbids over-restricting `src/tests/x.py`, which the policy classifies implementation. A flat `**/tests/**` deny broke B3; the emitted order reconciles both: role test-convention denies first, then an allow for every declared implementation root (B3), then the policy's own test/colocated denies (so a declared test inside an implementation root still resolves deny). No other route gains permission (`deny *` first, policy/derived/private last).

## 2. Test → result

| Test | Result |
|---|---|
| `tests/test_006_005_u6fix7_write_lever.py` (focal) | **10 passed** |
| `tests/test_006_005_*.py` (all 006-005 focals) + `tests/test_004_001_t7_capacity.py` | **134 passed** |
| `t5_reviewfix` + `t5_runtime` + `t7_l1_derived` + `t7_w2` (with focal) | **55 passed** (incl. B3) |
| `t1_policy`, `t1_reviewfix`, `t2_bootstrap`, `t6_landing`, `t7_acceptance`, `t7_limits_rule`, `t7_private_paths`, `t3_002_t1_receive`, `t3_002_t2_materialize`, `t5_005_t2_docs_policy`, `test_packet_prepare`, `test_cdad_generate`, `test_004_001_t7_pd10`, `test_role_packet_consumers` (A‑1) | **147 passed** |
| `python3 tests/pd10_permission_semantics.py` | **39/39 passed** |
| `make validate` | 168 PASS / **1 FAIL: F011** — environmental (derives from the installed copy in HOME, older than HEAD), as the packet anticipated |
| `bash scripts/validate-subagents.sh` (repo mode) | **PASS rc=0** (see note) |
| `make agents` twice | no pending tracked diff (generator idempotent) |

No flaky waiter-margin failure appeared.

## 3. Exact commands and outputs

```
$ python3 -m pytest tests/test_006_005_u6fix7_write_lever.py -q
10 passed in 1.59s

$ python3 -m pytest tests/test_006_005_*.py tests/test_004_001_t7_capacity.py -q
134 passed in 273.09s (0:04:33)

$ python3 -m pytest tests/test_role_packet_consumers.py -q
5 passed in 9.58s

$ python3 tests/pd10_permission_semantics.py
PD-10 semantic checks: 39/39 passed

$ make validate
... Assert PASS: 168 / Assert FAIL: 1 / FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL

$ tmp=/tmp/opencode/cdad-repo-install
$ env -u XDG_CONFIG_HOME CDAD_INSTALL_ROOT="$tmp" bash install.sh          # rc=0, Verify: PASS — 11 cdad agents
$ env -u XDG_CONFIG_HOME CDAD_INSTALL_ROOT="$tmp" bash scripts/validate-subagents.sh
✅ 10/10 runtime agents present ... ✅ install.sh --check PASS ... ✅ models OK
== RESULT: PASS (all verifications OK) ==   (rc=0)
```

`validate-subagents.sh` was run in repo mode by pointing `CDAD_INSTALL_ROOT` at a temporary root populated from the repo — **HOME was never read or written** (the real installed copy is the owner's deployment decision). `make validate`'s F011 is therefore declared environmental, not caused by this change.

## 4. Commit

```
028cd79 fix: 006-005 U6-7 — sin palanca write en los agentes OpenCode
14 files changed, 110 insertions(+), 105 deletions(-)
```

No `--no-verify`, no `git stash`, no push. Untracked `docs/planning/`, `findings/*` and `docs/specs/006-005-native-path-parity/u6-acceptance.md` were left untouched (not mine); no test file was read-from or written to HOME, and no test file was edited.

## 5. Notes / honest limits
- The RED report's green-readiness simulation stated “removing only the `write:` line yields 0 mismatches”; that holds for write-vs-edit verdict parity, but not for the explicit derived `-odoo` barrier assertion, which needed the derived-map precedence change above. Both approved oracles (U6-7 and B3) are green with the ordered map; if the orchestrator prefers the stricter reading (derived maps strictly policy-derived, U6-7's derived `-odoo` assertion relaxed), that is a test change and belongs to the test-writer.
- The emitted permission note is the exact Spanish sentence the orchestrator specified; the rest of the generated artifacts stay English.