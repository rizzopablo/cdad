# Role report — test-writer (RED), 006-005 U6-6

## 1. Modified files (only `tests/`)

- **New:** `tests/test_006_005_u6fix6_model_parity.py` (453 lines, 2 process-level tests).
- Commit: `12c29a7` — `test: 006-005 U6-6 RED — paridad de model_reported en la via nativa` (1 file changed, 453 insertions).
- Nothing outside `tests/` touched; `docs/planning/` and the two `findings/*.md` remain untracked and were not added. No `--no-verify`, no stash, no push.

## 2. Test → postcondition map

| Test | Postcondition / decision |
|---|---|
| `test_u66_json_model_is_reported_as_provider_over_model` | **PD-5 / D-ADP-2 (U6-6), §2.4** — a *verified* native `record` reports `model_reported` = `<provider>/<model>`, the same normalized form the external path fixes; never the raw store JSON |
| `test_u66_non_json_model_is_not_fabricated` | **PD-5 / D-ADP-2 (U6-6)** — a row whose `model` is not the declared JSON is not invented: the observed value is reported (external rule: plain text preserved, `test_005_010_reviewfix.py::TestR2ModelReportedFromDurableRow::test_r2_plain_text_row_model_is_preserved`), never a fabricated one. Declared GUARD. |

Docstrings are tagged «PD-5/D-ADP-2 (U6-6)».

Oracle discipline: the entry is run **as a process** from a staged copy of the skill tree; the real `cdad_delegate_opencode.py` is resolved by the `opencode` section of `runtimes.json` under temporary `XDG_CONFIG_HOME`/`HOME`; the disposable SQLite store carries the real shape (`time_created INTEGER` epoch **ms**, `model TEXT` = `{"id","providerID","variant"}`). The verified path asserts `session == child` as a precondition (parent + moment + project-by-membership reach the O-3 threshold). No implementation file was read or imported.

## 3. Commands and output

```
$ python3 -m pytest tests/test_006_005_u6fix6_model_parity.py -q
F.                                                                       [100%]
...
E  AssertionError: '{"id": "u66-fixture-model-id", "providerID": "u66-fixture-provider", "variant": "default"}'
   != 'u66-fixture-provider/u66-fixture-model-id'
   : el registro I8 de la via nativa no reporta `model_reported` en la MISMA forma ...
tests/test_006_005_u6fix6_model_parity.py:418: AssertionError
1 failed, 1 passed in 2.58s
```

```
$ python3 -m pytest tests/test_006_005_*.py -q
1 failed, 117 passed in 213.51s (0:03:33)
```

Only declared failure: the JSON case, an `AssertionError` about the missing behavior (the native record carries the raw JSON). The non-JSON case is green today (declared guard) and must stay green after the fix.

Reference rule on the external path (not a regression of this unit, run to confirm the form this RED extends):

```
$ python3 -m pytest "tests/test_005_010_reviewfix.py::TestR2ModelReportedFromDurableRow" -q
2 passed in 3.48s
```

Full suite not run (policy: the closer runs it once).

## 4. A-1 declaration

**No existing test is reformulated.** Verified by inspection of the declared `tests/` scope:

- No test pins the raw JSON as *product* behavior of the native path. `tests/test_006_005_u1b_dispatch_entry.py` relays a fixture module whose observation is `model_reported: null` (:387-400); `tests/test_006_005_u6fix4_native_selection.py` never asserts `model_reported`; `tests/test_006_005_u6fix5_write_ahead.py` exercises the **external** path with a plain-text row model.
- The external-path D-ADP-2 tests (`test_005_009_t2_opencode_adapter.py:346-357,803`; `test_005_010_reviewfix.py:503-536` and `:549-571`) fix the rule this RED extends to the native path and remain untouched.

## 5. Honest limits

- The non-JSON test is a guard, not a failing RED: today's raw copy happens to satisfy the declared external rule. Declined to over-specify shapes not fixed by the contract; it stays discriminating against a "parse-and-invent" fix.
- Only the declared read scope (`docs/specs/006-005-native-path-parity/`, `tests/`) was read; `execution.md` (cited as the finding's source) is outside the declared read scope and was not opened — the packet's U6-6 description supplied the finding. No host values used.