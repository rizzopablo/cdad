I'll start by reading the approved contract and the test file in scope.
Now let me scan the tests directory for other blocks that require models or `cdad-models.sh`.
Let me check for any test that exercises this specific oracle block (mutation tests) and any other model-demanding asserts.
Now I'll reformulate the P1.reviewer block, declaring the replacement by PD-1e/INV-3.
Now the gate: run the reformulated validator.
Falsifiability check (mutation on an ephemeral copy — never reading the implementation, only proving the predicate can fail):
Exactly the declared expectation: only the known F011/validate-subagents (DT-8 environmental) fails. Let me review my diff.
## Role report — test-writer / RED (testfix U1, `006-003-installer-single-profile-delegation-config`)

### What conflicted and how it was resolved
`tests/validate-odoo-specialization.sh` **P1.reviewer** read the frontmatter `model:` line of `agents/cdad-implementer-odoo.md` / `agents/cdad-reviewer-odoo.md` and demanded both exist and differ. PD-1e (`grep -rc '^model:' agents/cdad-*.md agents/claude-code/*.md` → 0) and INV-3 (no installable text fixes a model) make that assert **unsatisfiable by construction**. It is **replaced, not deleted** (rule A-1): the oracle now demands that **neither** `-odoo` agent fixes a model, and the family invariant is declared as moved to the configuration verification of PD-4/U5 (comment + both pass/fail messages carry the reference). No other P1 assert was touched.

### Modified files (only declared write scope)
- `tests/validate-odoo-specialization.sh` (+24 / −14). Commit `bb674b4` contains exactly this file.

### assert → postcondition map

| New/kept assert | Contract postcondition | Direction |
|---|---|---|
| `P1 rev (implementer-odoo): fixes no model: line` | **PD-1e / INV-3** (006-003) — replaces “the reviewer’s model differs from the implementer’s” of `docs/specs/cdad-003-odoo/spec.md` P1 | absence of `^model:` |
| `P1 rev (reviewer-odoo): fixes no model: line` | **PD-1e / INV-3** (006-003) — same replacement | absence of `^model:` |
| comment + messages: family invariant → `cdad_model_family.py` (same-family / guaranteed-by-configuration / not-verifiable / invariant-not-guaranteed, rc=0) + declaration in `review.md` | **PD-4 a–e / INV-5**, unit **U5** | declared remit |
| all other P1 asserts (P1.1 variants, PD-10 semantic permission block, permissive-bash loop) and P2–P6 + A3 | unchanged | untouched |

### Audit of other blocks demanding models / `cdad-models.sh` (declared)
- `tests/validate-odoo-specialization.sh`: only the P1.reviewer block. **No other block demands a model.**
- `tests/validate-consistency.sh` **F008** (`:467-489`): already reformulated by 006-003 U1 — asserts map retired (`assert_file_missing scripts/cdad-models.sh`), no `^model:` in agents, no map consumer in `install.sh scripts/`. **No change needed.**
- `tests/validate-consistency.sh` **F001** (`:380-399`): already inverted by U1 — §2 of both orchestrators must be *free* of model names. **No change needed.**
- Observation (NOT a model demand, left untouched, flagged for U5): `F001:343-352` demands §2 declare the family invariant “guaranteed by configuration” + “declared”, with a stale parenthetical “(when the profile fixes models)” — the wording after PD-1/PD-7b should read “configured in the delegation config”. Same for the `--basic` caveat asserts (`:357-361`), which the approved contract keeps (`--basic` accepted, deprecated). Both pass on the current tree; neither belongs to the model-removal testfix.
- Only two `tests/validate-*.sh` exist.

### Commands and outputs (evidence)

```
$ bash tests/validate-odoo-specialization.sh
...
PASS: P1 rev (implementer-odoo): fixes no model: line (006-003 PD-1e/INV-3, replaces "reviewer's model differs from the implementer's"; family invariant -> PD-4/U5)
PASS: P1 rev (reviewer-odoo): fixes no model: line (006-003 PD-1e/INV-3, replaces "reviewer's model differs from the implementer's"; family invariant -> PD-4/U5)
...
Assert PASS: 68
Assert FAIL: 0
PASS: all postconditions P1..P6 and the A3 criterion verified.
RC=0
```
→ **GATE 1 met: PASS** (the product already complies; the two new asserts pass on the shipped tree).

Falsifiability proof (mutation on an **ephemeral copy** in `/tmp/opencode/…`, content never displayed — only the predicate outcome):
```
--- unmutated (as shipped) ---
PREDICATE=TRUE(fixes no model:) [imp.md]
PREDICATE=TRUE(fixes no model:) [rev.md]
--- mutated: append a model: line to the reviewer copy ---
PREDICATE=FALSE(contains model:) -> the P1.rev assert FAILS as intended [rev.md mutated]
cleaned /tmp/opencode/cdad-u1-mut.Kqw32E
```

```
$ bash tests/validate-consistency.sh
...
PASS: F008 (006-003 PD-1c): the model map is retired (was scripts/cdad-models.sh)
PASS: F008 (006-003 PD-1e/INV-3): no agent artifact fixes a model
PASS: F011: tests/validate-odoo-specialization.sh → PASS (zero regression over cdad-003/004)
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
Assert PASS: 160 / Assert FAIL: 1
RC=1
```
→ **GATE 2 met: sole failure is F011/validate-subagents (DT-8 ambiental, declared in the packet).**

### Commit
```
bb674b4 test: 006-003 U1 testfix — P1.reviewer pasa de exigir model: distinto a exigir ausencia de model: (PD-1e/INV-3, familia -> PD-4/U5)
 tests/validate-odoo-specialization.sh | 38 ++++++++++++++++++++++-------------
 1 file changed, 24 insertions(+), 14 deletions(-)
```
`git show --name-only` → only `tests/validate-odoo-specialization.sh`. No `--no-verify`, no stash, no push, nothing staged outside `tests/`.

### Honest limitations / declarations
- I did not open any implementation file (`agents/**`, `install.sh`, `skills/**`, `scripts/**`). The only reads of `agents/` were performed **by the harness of the declared gate** (the validator) and by a byte `cp` for the mutation copy, whose content was never rendered to me.
- Read: `docs/specs/006-003-…/spec.md`, `tests/**` only. `tests/.sensitive-patterns.local` was not read.
- Untracked `docs/planning/` and `findings/incremental-construction-and-reproducible-validation-2026-10-17.md` were left untouched (still untracked, never staged).
- The full suite was **not** run (packet policy: the closer runs it once at closure).
