# Role report — implementer (GREEN), 006-005 U6-6

## 1. Modified files

- `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` — the module that owns the store. In `_observe_document` (the single point where the observation handed to `cdad_dispatch.py record` is rendered) the row's `model` is now rendered with the **existing single implementation** of the external rule, `_model_reported_from_row` (the one the external path already uses at `:2884`), plus the named constant `STORE_MODEL_COLUMN` and the docstring declaring it. No test touched; `tests/` untouched; the untracked `docs/planning/` and `findings/*.md` were neither read nor added.
- Commit: `ef88817` — `fix: 006-005 U6-6 — model_reported paritario en la via nativa` (1 file, +19/−2), no `--no-verify`, no stash, no push.

Why there and not in the entry: §2.2 says the observation surface is the module's, and the module is the one that knows its store (same precedent as U6-4, where the module converts `time_created` epoch-ms into an ISO instant before handing the row over). Normalizing at that one boundary makes both correlation inputs (`--parent`, `--session`) report the external form and adds no second copy of the rule. The external path is unaffected: it registers `model_reported` from its own store read (`:2884`), not from `--observe`, so its behavior is unchanged.

## 2. Test → result

| Test / gate | Result |
|---|---|
| `tests/test_006_005_u6fix6_model_parity.py` (RED before, focal) | **2 passed** (was 1 failed, 1 passed) |
| `tests/test_006_005_*.py` (all focal of the feature) | **118 passed** |
| `tests/test_005_010_reviewfix.py` + `tests/test_005_009_t2_opencode_adapter.py` + `tests/test_006_001_t2_wait_recovery.py` | **29 passed** |
| Proportional: `tests/test_005_009_t1_interface.py`, `tests/test_005_010_t1_durable_signal.py`, `tests/test_005_010_t4_integration.py` (external-path `model_reported` pins) | **10 passed, 1 skipped** |

No flakiness of the waiter margin appeared.

## 3. Exact commands and output

```
$ python3 -m pytest tests/test_006_005_u6fix6_model_parity.py -q        # RED, before
F.                                                                       [100%]
E  AssertionError: '{"id": "u66-fixture-model-id", "providerID": "u66-fixture-provider", "variant": "default"}' != 'u66-fixture-provider/u66-fixture-model-id'
1 failed, 1 passed in 3.06s

$ python3 -m pytest tests/test_006_005_u6fix6_model_parity.py -q        # GREEN, after
..                                                                       [100%]
2 passed in 2.36s

$ python3 -m pytest tests/test_006_005_*.py -q
118 passed in 163.16s (0:02:43)

$ python3 -m pytest tests/test_005_010_reviewfix.py tests/test_005_009_t2_opencode_adapter.py tests/test_006_001_t2_wait_recovery.py -q
29 passed in 59.84s

$ python3 -m pytest tests/test_005_009_t1_interface.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t4_integration.py -q
10 passed, 1 skipped in 18.99s

$ git commit -m "fix: 006-005 U6-6 — model_reported paritario en la via nativa"
[main ef88817] fix: 006-005 U6-6 — model_reported paritario en la via nativa
 1 file changed, 19 insertions(+), 2 deletions(-)
```

## 4. Extra check (declared, out of this unit's gates)

`make validate` was run as a cheap sanity check although the plan does not list it for U6-6. Result: `Assert PASS: 168 / Assert FAIL: 1`, the failing assert being F011 `scripts/validate-subagents.sh`. Run directly, that script fails on **host installation drift** (`DRIFT: differs ~/.claude/skills/cdad-cycle/references/re-entry.md`, `.../cli-delegation.md`, and `install.sh --check` against the installed `~/.config/opencode` and `~/.agents` trees) — files this change does not touch, i.e. a pre-existing environmental condition of the machine, not caused by the diff (I did not read or write those config values beyond the project's own validator reporting their paths). Everything else in `make validate` passes.

## 5. Honest limits

- The non-JSON case is a declared guard: it was already green and stays green; it only discriminates against a "parse-and-invent" fix (the reused rule preserves plain text verbatim and returns `None` on no value — never a fabricated one).
- The model is normalized in the observation rendering, so the `--observe` document no longer shows the store's raw `model` blob; no test or consumer pins the raw blob (only `cdad_dispatch.py record` consumes `--observe`), and the module's other surfaces are untouched.
- Full suite not run (policy: the closer runs it once).

## 6. Commit

`ef88817` — `fix: 006-005 U6-6 — model_reported paritario en la via nativa` (not pushed).