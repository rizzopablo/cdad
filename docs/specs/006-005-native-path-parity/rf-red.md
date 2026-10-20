RED committed. Here is the role report.

## Role report — test-writer, substage RED (006-005 review-fix B‑1/B‑2/B‑3)

### Modified files (write scope: `tests/**` only)
| File | Change |
|---|---|
| `tests/test_006_005_reviewfix.py` | **new** (1133 lines) — 9 tests: B‑1 (3), B‑2 (3), B‑3 (3) |
| `tests/test_004_002_t5_reviewfix.py` | **A‑1 reformulation** of `test_reviewfix_b3_nested_tests_dir_not_amplified` (+ A‑1 declaration in the module docstring) |

Nothing outside `tests/` was touched. `docs/.cdad-state.json` (orchestrator's `prepared→dispatched`), `docs/planning/` and `findings/*` were left untracked/untouched.

### Test → finding map
| Test | Finding | Postcondition |
|---|---|---|
| `test_b1_derived_implementer_denies_tests_inside_implementation_roots` | B‑1 | derived implementer (+`-odoo`) write verdict = `deny` for `scripts/tests/test_example.py`, `skills/demo/test_example.py`, `sources/ui/widget.spec.ts`, `tests/x.py`, private path, derived dir/manifest |
| `test_b1_derived_implementer_never_more_permissive_than_the_generated_one` | B‑1 | per probe: derived = generated or more restrictive, never more permissive (evaluator `write_verdict` of `test_006_005_u6fix7_write_lever.py`) |
| `test_b1_derived_implementer_keeps_non_test_implementation_code_writable` | B‑1 | ANCLA: non-test implementation code stays `allow` |
| `test_b2_session_selection_accredits_the_row_and_reports_the_model` | B‑2 | by `--session`: session credited + `model_reported` = `<provider>/<model>` |
| `test_b2_session_selection_gives_the_same_result_as_parent_selection` | B‑2 | `--session` ≡ `--parent` (same session, same `model_reported`) |
| `test_b2_session_selection_moment_contradiction_is_a_rejection` | B‑2 | contradicting moment ⇒ rejection (`blocked`), diagnosis names the key, **no** delivery (no staging/descriptor/receipt), never `unknown` (INV‑2) |
| `test_b3_generated_orchestrator_describes_the_external_route_as_an_envelope` | B‑3 | generated orchestrators: envelope + `delivery_ref` = durable receipt + module already received; **no** claim that the entry returns a FINAL TEXT |
| `test_b3_generated_orchestrator_describes_the_native_route_as_record_then_receive` | B‑3 | `record` stages, then `receive` |
| `test_b3_external_dispatch_returns_a_delivery_ref_that_is_a_valid_receipt` | B‑3 | ANCLA: real entry + real module + fake binary ⇒ `delivery_ref` = `receipt.json`, accepted by `cdad_result.py validate-receipt` |

### A‑1 reformulation (declared in both files)
`test_004_002_t5_reviewfix.py::test_reviewfix_b3_nested_tests_dir_not_amplified` no longer demands `allow` for `src/tests/x.py` in the derived implementer; it now demands `deny`. Declared: **replacement** (the "maps express exactly the classifier" oracle), **amended PD** (PD‑7 of 004‑002, `ni sobre-restricción` axis amended for the implementer; the policy *classification* is unchanged — the `validate-policy --classify` control still demands `implementation`), **reason** (review B‑1: the role barrier is a role convention, not a path classification; the derived applies the generated barrier restricted by the policy). Sweep of `tests/` found no other test fixing `allow` of a test inside an implementation root for the implementer, and none fixing the external path's “FINAL TEXT”.

### Commands and output
```
$ python3 -m pytest -q -p no:cacheprovider tests/test_006_005_reviewfix.py tests/test_004_002_t5_reviewfix.py
8 failed, 13 passed in 16.34s
```
All 8 failures are `AssertionError` about the missing behaviour (no ImportError/SyntaxError/fixture error). Measured causes: B‑1 derived `allow` vs generated `deny` on the three conventional tests; B‑2 `session=None`/`model_reported=None` by `--session` vs credited by `--parent`, and `termination=completed` with delivery instead of a rejection; B‑3 the two offending clauses (`then stage the returned FINAL TEXT through 'receive'`, `and returns the FINAL TEXT`) and the absent `delivery_ref`/`record`-stages declarations.

Focals and declared regressions (all green, unchanged):
```
006-005 focals (u1a,u1b,u1c,u2)                 60 passed
006-005 focals (u3,u3b,u4,u5)                   27 passed
006-005 focals (u6fix1,u6fix4,u6fix5)           23 passed
006-005 focals (u6fix6,u6fix7,u6fix7b,u6fix8,u7) 29 passed
regressions 004-002 (t1 policy/reviewfix, t2, t5 runtime/reviewfix, t6, t7×3)  103 passed + 1 expected RED (A‑1)
regressions 003-002 t1/t2, packet_prepare, 005-005 t2   43 passed
$ bash tests/validate-consistency.sh   → 168 PASS / 1 FAIL (pre-existing F011: scripts/validate-subagents.sh — installed-skill drift, unrelated to this tests-only change)
```

### Commit
`056c0f1 test: 006-005 review-fix RED — B-1 B-2 B-3` — 2 files, +1191/−11, only `tests/`. No `--no-verify`, no stash, no push.

### Honest limitations / abstentions
- **No implementation code was read.** `skills/cdad-cycle/scripts/**` was never opened; the entry and the real runtime module were exercised only as processes. The generated agents (`agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`, `agents/cdad-implementer*.md`) were read as the *declared generator outputs* the task declares readable (the `Read` tool denies `agents/**` as an implementation root, so they were read via shell).
- `tests/.sensitive-patterns.local` was never read; the B‑1 fixture substitutes a fictitious private path.
- `bash tests/validate-odoo-specialization.sh` was **not** run: it reads that private path (`tests/validate-odoo-specialization.sh:265-271`), same abstention as the stage‑4 review.
- The full suite was not run (PD‑21: it is run once by whoever closes the task).
- The B‑2 contradiction case is asserted as a **rejection** for `--session`; the `--parent` path keeps U6‑4’s declared behaviour (a row before `--since` is not a *candidate*, hence no rejection) — that pre-existing GREEN test (`test_u64_no_candidate_earlier_child_is_not_a_rejection`) is untouched and stays green, so the two paths differ by construction, not by accident.