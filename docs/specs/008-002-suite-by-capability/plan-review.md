# Plan review: 008-002-suite-by-capability (draft at 1127e82)

**Verdict: the draft cannot be dispatched in its current form.** I found 3 BLOCKING findings, 4 IMPORTANT and 3 MINOR. This is a review only. I approved nothing and edited nothing.

## BLOCKING

**B1. The plan has no canonical `plan-tasks` block, so it cannot be dispatched in batches.** `plan.md:1-76` contains only prose steps. The template requires exactly one block with id, files, focal_tests, regressions, depends_on and owner per task (`skills/cdad-cycle/assets/feature-plan-template.md:27-52`), and says a block that is missing or malformed is rejected.
- **Consequence:**
  - There is no list of files per task. Step 3 touches `scripts/` and step 4 touches `tests/`, so the write_scope cannot be audited.
  - There are no dependencies between tasks. For example, step 4 needs the step-2 map and the step-3 `validate`.
  - Ownership is unclear. Step 3 names only PC-1/2/3/5 for the test-writer (`plan.md:34`). Step 5 (PC-6, PC-7) names no RED/GREEN owner at all (`plan.md:52-60`).
- **Closure:** add a `plan-tasks` block with one task per batch, each with owner, files, focal_tests and depends_on. It must cover PC-1..PC-8.
- Verdict: BLOCKING · Bucket: h

**B2. The suite-wide net-reduction requirement in PC-4 may be infeasible, and failing it blocks the feature by design.**
- `spec.md:163` requires a net reduction across the whole suite, counting the new tests this feature adds. `spec.md:169` says the feature is not done unless it shows that reduction.
- The pilot is limited to 3 modules totalling 1,362 lines (`wc -l`: 534 + 575 + 253).
- The same feature adds new tests for PC-1, PC-2, PC-3, PC-5 (in synthetic git repos), PC-6 and PC-7, with negative controls and five-plus variants each. It is plausible those exceed whatever the pilot saves. That is my estimate, not a measurement.
- **Consequence:** the closure condition depends on the size of the new tests rather than on the quality of the consolidation. That pushes the test-writer to write thinner tests for the new CLI, which is the gaming this cycle is meant to prevent.
- **Closure:** pick one and state it in the spec:
  - (a) measure the reduction on the pilot set and report the new feature tests as a separate line; or
  - (b) widen the pilot so a suite-wide net reduction is realistically reachable.
- Verdict: BLOCKING · Bucket: h

**B3. `validate` is promised a guarantee it cannot observe.** `spec.md:159` says "a lost variant makes `validate` fail".
- `validate` compares the inventory, the map and pytest collection (`spec.md:113`). It can detect a missing record or a target nodeid that does not exist.
- It cannot detect that a target test no longer covers a variant it claims to cover. That would need semantic analysis, which `spec.md:249` itself rules out.
- **Consequence:** PC-3 would be marked green on the strength of the map's self-declaration. This is the "author's conclusion as proof" pattern.
- **Closure:** rewrite PC-3 so `validate` only checks structural integrity (target exists, no accredited obligation disappears, no `VERIFY` before an elimination). Variant preservation should rest on the targeted negative controls. Say where those controls live (a versioned file or test), who writes them, and how they are run reproducibly.
- Verdict: BLOCKING · Bucket: h

## IMPORTANT

**I1. Scope pulls in work that belongs to 008-005.**
- The epic defines 008-002 as organisation plus a keep/merge/delete inventory (`epic plan.md:52`).
- The epic already treats the surface gate as a shared gate that 008-005 runs (`epic plan.md:66`).
- The spec adds a canonical versioned gate (decision 5, PC-5), `close` with attempt preservation (PC-6), and the 2s debt (PC-7). These are three new product capabilities. Decision 5 also does not say whether `.cdad/local/surface-gate.sh` gets replaced or wrapped. The file is not tracked (`git ls-files .cdad/local` is empty).
- **Closure:** state the reason for this extension against the epic, and spell out the contract handed to 008-005. Otherwise move PC-5 and PC-6 into 008-005.
- Bucket: m

**I2. PC-6 promises atomic reservation, but its oracle cannot see atomicity.**
- `spec.md:181` promises that `close` reserves each attempt directory atomically.
- The oracle in `spec.md:194` is two sequential attempts. That cannot observe a race.
- **Closure:** either add a concurrent case (two simultaneous reservations end up in different directories) or drop "atomically" and promise only no reuse when attempts run one after another.
- Bucket: m

**I3. The PC-5 variant "deletion with substitute" relies on the base revision's inventory, which may not exist.** `spec.md:127` has `surface` look up the inventory and map as of `<ref>`. For any base older than this feature, those files do not exist.
- **Closure:** define what happens when the base has no inventory: a non-zero diagnostic, or select everything. Add it as a PC-5 variant.
- Bucket: m

**I4. The CLI is proportionate in size but not in what each subcommand promises.**
- `validate`, `list`, `run` and `surface` are justified.
- `measure` and `close` turn reporting and the closer's run into product. `close` runs the full suite (`spec.md:118`). The packet policy assigns the full suite to the closer, and nothing says whether the closer is required to use `close`, so there could be two ways to close.
- **Closure:** state that `close` is the closer's only mechanism, or remove it.
- Bucket: m

## MINOR

- **M1.** `spec.md:220` says the 008-001 isolation tests and affected consumers stay green, but never lists them. Name the nodeids or the selection that counts.
- **M2.** `spec.md:232-243` gives a second baseline (207 modules / 138,436 lines at ef6256a) next to the discovery's (205 / 137,712 at 0cef470). That is fine as long as PC-4 compares only before/after taken with the same method in this feature. Say so explicitly.
- **M3.** `plan.md:71` cites `scripts/cdad_packet.py`. It exists, so the reference is fine. PC-7 adds artifact validation that rejects a missing disposition or one that claims the 2s ceiling is solved (`spec.md:205`), but no command performs it. Say whether `validate` does it.

## What holds up (checked, no finding)

- Every citation I checked is accurate:
  - the 5s ceiling at `tests/test_005_009_t2_opencode_adapter.py:417-421`;
  - `.cdad/local` is not tracked, which is consistent with `spec.md:253`;
  - the scope of the three 005-010 modules.
- 008-001's isolation is not weakened in principle: `spec.md:54` and `spec.md:220` protect it explicitly.

## Abstentions

- I did not check `spec.md:21-27` line by line beyond the 5s ceiling.
- I can't judge whether the inventory by nodeid for about 203 test modules fits a single batch without a plan-tasks breakdown (B1).

## Evidence

- **Files modified:** none. **Commit:** none.
- **Commands run:**
  - `cat -n` on spec.md, plan.md and discovery.md
  - `sed -n 415,422p tests/test_005_009_t2_opencode_adapter.py`
  - `grep plan-tasks` (template)
  - `grep 008-002` / `gate` on the epic plan
  - `wc -l` on the three 005-010 modules
  - `git ls-files .cdad`
  - `ls scripts/cdad_packet.py scripts/cdad-suite.py`
  - `git status --short`
- **Key output:**
  - The three modules total 1,362 lines.
  - `scripts/cdad-suite.py` does not exist; it is proposed.
  - The working tree has only `M docs/.cdad-state.json`, which was there before this review.
