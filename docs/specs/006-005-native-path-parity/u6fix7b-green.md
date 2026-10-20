## Role report — implementer, GREEN (U6-7b), 006-005-native-path-parity

**Intake path:** validated packet (`packet_id: 006-005-native-path-parity-implementer-green-016`). No cycle skill loaded. I read the approved contract, the RED report, the RED tests, and the implementation. I did **not** read the HOME installation, the store, the config, nor the runtime.

### 1. Modified files (write scope only)

| File | Change |
|---|---|
| `skills/cdad-cycle/scripts/cdad_packet.py` | Derivation of derived agents: the `write` key of the installed copy's `permission` block now belongs to the region the derivation replaces, and it is **not emitted**. |

Nothing under `tests/` was touched (`git show --stat HEAD` = 1 file). `docs/.cdad-state.json` and the untracked `docs/planning/`, `findings/*` were already dirty before my session and were left alone (outside my write scope).

**Mechanism** (`_rewrite_derived_agent`): the frontmatter loop now recognizes every `permission` map key the derivation owns — `read/grep/glob/edit` (replaced by the derived maps) and `write` (retired). The retired key is dropped with its children, in both the scalar form (`  write: ask`) and the block form (`  write:` + children). When a role has no map to emit (the read-only roles), the origin keeps its own map verbatim and only the retired key is removed — the previous early return (`if not maps: return origin`) is what let the lever survive.

### 2. Test → result

| Test | RED (HEAD) | GREEN (now) |
|---|---|---|
| `test_u6_7b_every_derived_agent_ignores_the_installed_write_lever` | FAIL (`'ask' != 'deny'/'allow'`) | **PASS** |
| `test_u6_7b_derived_implementer_and_readers_keep_their_maps` | FAIL (`'ask' != 'deny'`) | **PASS** |
| `test_u6_7b_derived_test_writer_keeps_tests_docs_and_temporary` | FAIL (masked by `'ask'`) | **FAIL** — 1 subtest, see §5 |
| `test_u6_7b_derived_orchestrator_control_stays_allow` | PASS | **PASS** |
| `test_u6_7b_second_prepare_does_not_claim_hand_edits` | PASS | **PASS** |
| A-1 `test_004_002_t5_runtime.py` (19 tests) | PASS | **PASS** |

Focal `tests/test_006_005_u6fix7b_derived_strips_write.py`: **1 failed, 4 passed** (RED was 3 failed / 2 passed). `tests/test_006_005_*.py`: **1 failed, 132 passed**. Derived regressions (t5_runtime, t5_reviewfix, t7_l1_derived, t7_w2, t7_private_paths, test_packet_prepare): **75 passed**. Broader regressions (t1_policy, t1_reviewfix, t2_bootstrap, t6_landing, t7_acceptance, t7_limits_rule, 003_002_t1_receive, 003_002_t2_materialize, 005_005_t2_docs_policy): **86 passed**. Drift check: a second `prepare` does not claim hand edits, and regenerates identical bytes.

### 3. Commands and output

```
$ python3 -m pytest tests/test_006_005_u6fix7b_derived_strips_write.py -q --tb=line
F.FF.                                                    [100%]
AssertionError: 'ask' != 'deny'
AssertionError: 'ask' != 'allow'
AssertionError: 'ask' != 'deny'
3 failed, 2 passed in 1.69s                      # RED (HEAD)
```
```
$ python3 -m pytest tests/test_006_005_u6fix7b_derived_strips_write.py -q --tb=no   # GREEN
..F..                                                    [100%]
FAILED ...::test_u6_7b_derived_test_writer_keeps_tests_docs_and_temporary
1 failed, 4 passed in 1.92s
```
```
$ python3 -m pytest tests/test_006_005_*.py -q
1 failed, 132 passed in 145.58s (0:02:25)
$ python3 -m pytest tests/test_004_002_t5_runtime.py tests/test_004_002_t5_reviewfix.py \
    tests/test_004_002_t7_l1_derived.py tests/test_004_002_t7_w2.py \
    tests/test_004_002_t7_private_paths.py tests/test_packet_prepare.py -q
75 passed in 52.23s
$ python3 -m pytest tests/test_004_002_t1_policy.py ... tests/test_005_005_t2_docs_policy.py -q
86 passed in 123.16s (0:02:03)
$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
```

**F011 declared environmental** (`bash scripts/validate-subagents.sh`): (i) `install.sh --check` reports `DRIFT: differs ~/.claude/skills/cdad-cycle/scripts/cdad_packet.py` — the expected consequence of a repo fix **not yet deployed to HOME** (execution.md: the HOME deployment is the owner's order; I did not read or write the HOME installation); (ii) `missing staged agents/opencode/cdad-{orchestrator,reviewer}.md` — HOME installation coverage state; (iii) `cdad-reviewer.md declares model: openai/gpt-6.1-sol` — the **installed** copy in HOME declares a model (owner's change of 2026-10-19); the repo's agent has no `model:` key. Items (ii) and (iii) are independent of this change.

### 4. Commit

`58af287` — `fix: 006-005 U6-7b — los derivados no heredan la palanca write` (1 file, +57/−19). No `--no-verify`, no `git stash`, no push.

### 5. Mismatch to route back to the test-writer (I did not edit the test)

One assertion of the approved RED is unsatisfiable under the contract, and it was **masked in the RED state by the very lever this unit removes**:

`test_u6_7b_derived_test_writer_keeps_tests_docs_and_temporary` asserts `cdad-test-writer-odoo.md` → `addons/m/tests/test_m.py` = **allow**; the derived agent resolves **deny**.

Proof it is a test defect, not a product gap:
1. The verdict comes from `_derived_maps` (untouched by this change): HEAD and the working tree agree — `edit(addons/m/tests/test_m.py) = deny` in both (measured by loading each revision of `cdad_packet.py` and deriving from the same origin).
2. The fixture's policy is the **cdad** layout (`policy_doc("cdad")`): `test_roots=["tests"]`, `implementation_roots=[agents,skills,scripts,sources,build]` → `addons/` is unclassified → the catch-all `*: deny` applies. 004-002 PD-7: *"Los scopes pueden restringir la política, nunca ampliarla"*; 006-005 §2.9: the derived test-writer map is `deny *` + `tests/` + colocated (+ temporaries + barriers).
3. The same expectation **is** true under the odoo policy (measured): `policy=odoo → addons/m/tests/test_m.py=allow, addons/m/models/m.py=deny`.
4. The already-green U6-7 RED asserts that odoo case only for the **generated** agents (the global odoo map has `**/tests/**` allow); for the **derived** agents it asserts cdad-layout probes only. The U6-7b RED added the odoo probes to the derived case by analogy.

Making it pass in production would require either the union of stack test conventions in the derived map or a stack-aware derived map — both contradict PD-7/§2.9 and would open the test-writer's writes to product test trees outside the declared policy (and outside the packet's write scope). **I did not do that.** Suggested A-1 for the test-writer: either compare the derived odoo agent's write verdict against its own `edit` verdict (the invariant the first test already asserts), or add a second fixture with `policy_doc("odoo")` and assert `addons/m/tests/test_m.py`=allow / `addons/m/models/m.py`=deny there.

**Request to the orchestrator:** route that single assertion back to the test-writer (A-1) so the focal closes green; the production fix is complete and committed as `58af287`.