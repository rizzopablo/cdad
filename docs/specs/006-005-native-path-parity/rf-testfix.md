All work is committed. Here is the role report.

## Role report — test-writer, substage RED (006-005 review-fix testfix A‑1)

Packet `006-005-native-path-parity-test-writer-red-024` · contract `docs/specs/006-005-native-path-parity/spec.md` (sha256 `3a824be…`) · authority `docs/epics/epic-006-opencode-concurrency/execution.md` §«006‑005: review de etapa 4» (decisión **B‑1**).

### 1. Modified files (1 — inside the packet's write scope `tests/`)

| File | Change |
|---|---|
| `tests/test_005_008_t1_nested_tests.py` | **A‑1**: the implementer's `edit` verdict for the literal `tests/` dir nested under an implementation root (`webmin-module/module/tests/x.py`) changes from `allow` → `deny`; the A‑1 amendment is declared in the module docstring and in the assertion message; the test's docstring no longer says «el implementer allow en edit». |

Nothing else was touched. The `validate-policy --classify` control in the same test is **unchanged** (still requires `implementation` for that path) — the policy classification and the control do not move.

### 2. The oracle that was replaced

The pre‑fix oracle and its message were the *same* oracle already replaced in `tests/test_004_002_t5_reviewfix.py` (A‑1): it demanded `allow` because "un `tests/` literal under an implementation root is implementation, so denying it would be over‑restriction". Decision B‑1 inverts it: **the role barrier wins** — the implementer never edits tests (conventional, co‑located or declared) even inside an implementation root, and the derived map is never more permissive than the generated agent it derives from. Same amendment text as the 004‑002 precedent (PD‑7's «ni sobre‑restricción» axis amended for the implementer; classification untouched).

### 3. Sweep for other oracles of the same kind

Bounded sweep over `tests/` (grep of every `"allow"` expectation + every implementer/`verdict` probe, 92 hits reviewed). **Exactly one** other oracle fixed `allow` of the implementer over a test inside an implementation root. Verified as already correct and left untouched:

- `test_005_008_t1_nested_tests.py` PD‑4 (`:298` implementer `edit` of `main.pl` — implementation code, not a test), PD‑8 (`:541` `edit src/app.py` — code).
- `test_005_008_t3_acceptance.py:268-270` (implementer: `read` tests `allow`, `edit` impl `allow`, `edit` tests `deny`).
- `test_004_002_t5_runtime.py:526-531`, `test_004_002_t7_w2.py:169-175`, `test_004_002_t7_private_paths.py:279-283`, `test_004_001_t7_capacity.py:434-436` (implementer: `deny` on tests; `allow` only on non‑test code).
- `test_006_005_u6fix7_write_lever.py:524-527`, `test_006_005_u6fix7b_derived_strips_write.py:385-388` (implementer `tests` → `deny`).

One point of interpretation, stated explicitly: B‑1 is scoped to **editing**. The implementer's `read` over tests stays `allow` (no entries for tests in its read map) — asserted by 005‑008 PD‑4 (`:312`), which I did **not** reformulate, because the decision says "nunca edita tests", not "nunca lee tests".

### 4. RED evidence — the failure was an assertion, not an import/syntax error

The pre‑fix file (materialized from `HEAD` into a temp copy inside `tests/`, run, then deleted) fails by **`AssertionError`**, exactly on the replaced expectation:

```
E           AssertionError: 'deny' != 'allow'
E            : PD-7: el mapa `edit` de cdad-implementer.md resolvió edit('webmin-module/module/tests/x.py') como 'deny' — sobre-restricción: es implementación
tests/_tmp_a1_prefix_oracle_check.py:491: AssertionError
1 failed in 0.60s
```

That is the RED of the **superseded** oracle: the product (GREEN `3ca6597`) already resolves `deny`, so the old expectation was the only thing failing — it was a stale oracle, not a missing behavior. The **new** oracle's own RED is the 006‑005 B‑1 RED at `056c0f1` (`test_b1_derived_implementer_denies_tests_inside_implementation_roots`, failing by assertion before the implementation existed).

### 5. Commands and output

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_005_008_t1_nested_tests.py
9 passed in 3.70s

$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
      tests/test_006_005_reviewfix.py tests/test_005_008_t2_language_commands.py tests/test_005_008_t3_acceptance.py
16 passed in 45.11s

$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
      tests/test_004_002_t1_policy.py tests/test_004_002_t1_reviewfix.py tests/test_004_002_t2_bootstrap.py \
      tests/test_004_002_t6_landing.py tests/test_004_002_t7_acceptance.py tests/test_004_002_t7_private_paths.py \
      tests/test_004_002_t7_limits_rule.py tests/test_004_002_t5_runtime.py tests/test_004_002_t5_reviewfix.py \
      tests/test_003_002_t1_receive.py tests/test_003_002_t2_materialize.py tests/test_packet_prepare.py \
      tests/test_005_005_t2_docs_policy.py
147 passed in 148.00s (0:02:27)

$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
      tests/test_006_005_u3_temporary_scope.py tests/test_006_005_u3b_derived_temporary_permission.py
14 passed in 7.26s

$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
      tests/test_005_008_t1_nested_tests.py tests/test_006_005_reviewfix.py
18 passed in 11.08s

$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
make: *** [Makefile:22: validate] Error 1
```

**F011 is the pre‑existing environmental failure** already recorded in `docs/specs/006-005-native-path-parity/rf-green.md` §4 (same assert, same count 168/1): `scripts/validate-subagents.sh` compares the **repo** tree against the **installed** skill/agents in `HOME` (`❌ cdad-reviewer.md declares model:` — the owner‑personalized agent copy). It inspects the agent tree, not `tests/`, so it is unaffected by this test‑only change. I did not read or write the installation in `HOME`.

### 6. Commit

```
$ git add tests/ && git commit -F -   # subject: test: 006-005 review-fix testfix — A-1 en 005-008 nested tests
[main e99bc5a] test: 006-005 review-fix testfix — A-1 en 005-008 nested tests
 1 file changed, 40 insertions(+), 7 deletions(-)
```

`git show --stat HEAD` → `e99bc5acbbb2de7579da93fcadd6b176ea0da04f`, one file: `tests/test_005_008_t1_nested_tests.py`. No `--no-verify`, no `git stash`, no `push`. `git status` after the commit: only `M docs/.cdad-state.json` (orchestrator's) and the untracked `docs/planning/`, `findings/*` — not mine, left as they were.

### 7. Honest limitations / abstentions

- **The full suite was not run** (PD‑21: it is run once, by whoever closes the task). The declared regressions of the validation plan plus the 005‑008 family and the 006‑005 reviewfix file were run and are green; `make validate` shows the same pre‑existing F011.
- **No implementation code was read.** The work used only the spec, `rf-green.md` §5, the `execution.md` decision B‑1, and `tests/`. The RED evidence was obtained by running the pre‑fix *test* file, not by inspecting the product.
- `tests/.sensitive-patterns.local` was never read; no host values, endpoints or credentials appear in the change.
- The A‑1 declaration cites the 005‑008 spec by PD name and by the wording carried in the test file itself (its own header and class docstring); the 005‑008 spec file was **not** opened, because it lies outside this packet's declared read scope (`docs/specs/006-005-native-path-parity`, `tests`).