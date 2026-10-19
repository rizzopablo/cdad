## Implementer report — 006-005 U6-4 GREEN

**Result: RED → GREEN. 9/9 focal, 105/105 `tests/test_006_005_*.py`, 192 regressions passed (2 skipped), `make validate` F011 fails ambient (declared, pre-existing and unrelated). Commit `b06bd2f`, no `--no-verify`, no stash, no push. Tests untouched.**

### What changed (2 files, implementation only)

`skills/cdad-cycle/scripts/cdad_delegate_opencode.py` — the module, which knows its store, now **hands an interpretable instant** and **selects the candidate**:
- `STORE_MOMENT_COLUMN`/`STORE_MOMENT_EPOCH_MILLISECONDS` + `_store_instant()`: `session_v2.time_created` (INTEGER, epoch **ms** per the extended V-7 probe) is converted to an ISO UTC instant before the row leaves the module. The entry never guesses units.
- `_native_candidate()`: ONE `SELECT … WHERE parent_id = ?` (mode `ro`, no polling, unchanged URI); candidates = rows under the declared parent whose `agent` is the packet's agent **and** whose moment is **after `--since`**. Exactly one ⇒ row handed (ISO moment); none ⇒ `(None, detail|None)`; more than one ⇒ `(None, ambiguity named)` — never a rejection. Unreadable `time_created` ⇒ named as **not interpretable** (distinct from the U6-3 ancestor wording). The detail also names the keys that matched (`parent`).
- `--agent`/`--since` added to `--observe`; a diagnostic that accredits no row goes to stderr with rc=0 (so the entry declares it, never fails closed on a mere absence).

`skills/cdad-cycle/scripts/cdad_dispatch.py` — the entry **declares** what the module reports:
- `observe_model()` → `(row, problem, detail)`, passing the packet agent (`REQUEST.json.agent`) and `--since` so the module selects; `problem` (unusable surface) still fails closed only when there is no byte-exact native result.
- `correlate(..., detail=…)`: the non-verified note names the module's diagnostic, names the keys that **did** match (`matched: …`), and stays non-verified (never a rejection) — so PD-6 still delivers with `session: null` + declared provenance.
- The verified note names a `not-evaluable` project key (U6-3 ancestor layout), which the U6-4 ancestor case requires in the diagnosis.

### Test → result (at HEAD `b06bd2f`)

| Test | Before | After |
|---|---|---|
| `u6fix4_native_selection.py::test_u64_verified_child_inside_the_root` | FAIL | PASS |
| `…ancestor_directory_is_verified_by_parent_and_moment` | FAIL | PASS |
| `…same_agent_child_before_since_is_not_a_candidate` (ms discriminator) | FAIL | PASS |
| `…earlier_child_of_another_role_is_not_a_candidate` | FAIL | PASS |
| `…two_candidates_are_ambiguous_and_never_accredited` | FAIL | PASS |
| `…no_candidate_earlier_child_is_not_a_rejection` (declared GUARD) | pass (wrong reason) | PASS (now discriminating) |
| `…no_candidate_other_agent_with_native_result_delivers_under_pd6` | FAIL | PASS |
| `…uninterpretable_instant_is_named_as_such` | FAIL | PASS |
| `…unverified_note_names_the_keys_that_matched` | FAIL | PASS |

### Commands and output

```
$ python3 -m pytest -q --tb=short tests/test_006_005_u6fix4_native_selection.py
9 passed in 10.87s            (before the fix: FFFF.FFFF → 8 failed, 1 passed)

$ python3 -m pytest -q tests/test_006_005_*.py
105 passed in 128.09s

$ python3 -m pytest -q <U1b regressions + U2 regressions + test_packet_prepare …24 files>
192 passed, 2 skipped in 387.83s

$ make validate
Assert PASS: 168 / Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
$ bash tests/validate-odoo-specialization.sh
Assert PASS: 68 / Assert FAIL: 0 → PASS        (second target of `validate`, run directly)
```

**Ambient F011 (declared, not mine):** `bash scripts/validate-subagents.sh` reports `DRIFT: differs …/skills/cdad-cycle/references/re-entry.md` and `cli-delegation.md` between the repo and the **installed** copies under `~/.claude`, `~/.config/opencode`, `~/.agents`, and those installed trees carry **no `scripts/`** at all (`diff` check), so the drift is stale installed markdown, not this change.

**Flakiness (declared):** one full regression run had 7 failures in `tests/test_006_001_t1_selection.py` / `t1b_service_mode.py` under load (the known waiter-margin flakiness); re-run in isolation → `34 passed in 54.61s`, and the same full set re-run clean → `192 passed, 2 skipped`.

### Commit

```
b06bd2f fix: 006-005 U6-4 — momento en ms y seleccion del candidato nativo
 skills/cdad-cycle/scripts/cdad_delegate_opencode.py | 160 ++++++++++++++++++---
 skills/cdad-cycle/scripts/cdad_dispatch.py          |  74 +++++++---
 2 files changed, 197 insertions(+), 37 deletions(-)
```
Untracked `docs/planning/` and `findings/incremental-construction-and-reproducible-validation-2026-10-17.md` left out (not mine). `tests/**` never written; the real config/store/binary were never read or written (every fixture is per-test temporary).