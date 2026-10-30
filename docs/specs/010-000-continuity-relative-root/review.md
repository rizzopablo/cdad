## Review 010-000-continuity-relative-root (stage 4, reviewer)

**Verdict: no blocking findings.** I found 0 blocking, 6 optional and 2 abstentions. I am reviewing, not approving; you decide on the findings and approve.

### Intake (route A)
- The packet has exactly one `---cdad-packet-json` marker and its closing `---end-cdad-packet-json`.
- `validate-request` with the installed CLI (`~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py`), the absolute root and the declared execution context returned rc=0.
- `render` returned rc=0. Its output is identical to the published `PACKET.md`.
- I compared every received byte against the full render: `equal True 5864 5864`, sha256 `c1bd9806…e1c7`.
- Contract: sha256 of `spec.md` is `623b15e1…f01737e2`, which matches.
- Tests: sha256 of the test file is `6f5f84ef…49ad9`, which matches the GREEN gate recorded in the state file.
- Range reviewed: `34dcd9b..HEAD` (HEAD = `d45d374`). It covers 3842e18 (impl), 6e71e78 (tests), 2ddd040, 8b6ed56, 88e552b and d45d374 (docs/state).

### Checks against the PCs

**PC-01 and PC-02 (equivalent roots work the same):**
- Both CLI handlers now resolve the root first: `_run_write` (`cdad_continuity.py:1160-1162`) and the CLI border (`:3182`).
- `plan_write` resolves the root on entry (`cdad_continuity.py:1035-1038`).
- `verify_published_packet` (`cdad_packet.py:1954`), `_project_path` (`:301-305`) and `classify_path_observable` (`:433-444`) all compare a resolved candidate against a resolved root.

**PC-03 (`plan_write` only plans):** the diff adds no writes. The tests compare the whole project tree before and after planning and after replay.

**PC-04 and PC-05 (portable evidence, replay):**
- Only the root is resolved. References and body fields are unchanged.
- test_B compares the body bytes from the absolute and relative roots and checks that the absolute path does not appear in them.
- Replay with the other root is `no_op` with an unchanged tree. A conflicting update is still rejected without effects.

**PC-06 (admission and authority):**
- An altered packet is rejected with `differs from canonical`.
- A suspended unit is rejected with `suspended`, with no effects.
- The order identity → replay → authority in `main` (`cdad_continuity.py:3181-3199`) is untouched.

**PC-07 (containment kept):**
- Traversal, absolute paths and an outside symlink are rejected with identical output from a relative and an absolute root.
- The outside witness file stays intact.
- `update.references` keeps its lexical check, as the spec requires.
- Using the resolved root does not weaken containment: an inner symlink pointing outside still fails `relative_to(root)`.

**Policy precedence:** `docs/cdad-policy.json` is classified as `policy` from both roots, because both sides of the comparison are now resolved.

**PC-08 (installed consumer):** confirmed in an isolated copy; see Evidence.

### Blocking findings
None.

### Optional findings
Each finding uses the 4-field form: Verdict, Bucket, Rationale, Provenance. Every bucket here is `h`: full diff, exact citations, and spec in context. I did not count the "different model family" point because the implementer's model is not declared.

1. **No test for `verify-begin` with a relative root.** Verdict: OPTIONAL · Bucket: h
   - Rationale: PC-01 says the `begin` "queda verificable mediante el mecanismo existente", but none of the 010-000 tests runs `verify-begin`.
   - `verify_begin` uses `Path(project_root)` without resolving it (`cdad_continuity.py:1326`, CLI at `:3211`).
   - I checked it in a temporary fixture: rc=0 and an identical `body_sha256` from `.` and from the absolute path.
   - Consequence: a later change could break verifying a `begin` made from a relative root, and nothing would catch it.
   - Provenance: `tests/test_010_000_continuity_relative_root.py:236-313`.
   - Closure condition: test_A runs `verify-begin --project-root .` and asserts rc=0 and the same `body_sha256` as from the absolute root.

2. **`plan_write(command="checkpoint")` and the symlink root through the API are never tested.** Verdict: OPTIONAL · Bucket: h
   - Rationale: PC-02 promises the same plan "para `begin` y `checkpoint`", but test_A2 only uses `command="begin"` and only `.`.
   - My fixture showed relative and symlink roots give the same envelope and writes as the absolute root for `checkpoint`.
   - Consequence: a regression in programmatic checkpoint planning would go unnoticed.
   - Provenance: `tests/...:347,360`.
   - Closure condition: test_A2 compares the `checkpoint` envelope and writes from absolute, relative and symlink roots.

3. **The symlink variant in test_A checks only `record`, `seq` and `no_op`.** Verdict: OPTIONAL · Bucket: h
   - Rationale: acceptance §5.5 asks for equivalence evidence that includes a symlink root. test_B compares bytes, but only for the relative root.
   - Consequence: if a resolved path leaked into the body only when the root is a symlink, no test would see it.
   - Provenance: `tests/...:288-295`.
   - Closure condition: compare `_bodies(sym_origin)` with `_bodies(abs_root)` byte for byte.

4. **The PC-08 test skips `make staging` when the checkout already has a staging manifest.** Verdict: OPTIONAL · Bucket: h
   - Rationale: `product_staging.product_root()` uses the real checkout if `build/staging/manifest.json` exists. Here it exists and dates from Oct 28, before the fix, so in this checkout test_D does not run `make staging` from an isolated copy as PC-08 and §5.7 describe.
   - Mitigation:
     - `install.sh:1261-1276` copies the skill scripts straight from the source tree, not from staging.
     - I ran test_D in a copy without `build/`: staging was generated in a temporary copy and the test passed (`1 passed in 19.85s`).
   - Consequence: a stale manifest makes the PC-08 evidence depend on the state of the checkout.
   - Provenance: `tests/product_staging.py` (fast path), `tests/...:809-811`.
   - Closure condition: test_D always uses an isolated copy with its own `make staging`, and asserts that the installed scripts are byte-identical to `skills/cdad-cycle/scripts/`.

5. **Private helpers now raise a bare `ValueError` instead of `PolicyError` when given a relative root.** Verdict: OPTIONAL (FYI) · Bucket: h
   - Rationale: `_project_path` now returns a candidate under the resolved root. Helpers that then call `candidate.relative_to(<the root as passed>)` raise `ValueError` when called directly with a relative root:
     - `_relative_display` (`cdad_packet.py:492-493`, used from `_reject_overlap` at `:503`),
     - `_validate_temporary_roots` (`:551`),
     - `_scope_contains` (`:1440`).
   - Reproduced: `_reject_overlap(pp, Path('.'), …)` gives `ValueError '/tmp/.../docs' is not in the subpath of '.'`.
   - It still fails closed, and none of these is reachable from the APIs in scope or from the CLIs, which pass an already-resolved root.
   - Closure condition (optional): resolve the root in those helpers too, or document the precondition.

6. **The current-decisions table in `docs/systemPatterns.md` does not mention ADR-037, ADR-038 or ADR-039.** Verdict: OPTIONAL · Bucket: h
   - Rationale: all three are `Proposed`, so they get no row, which is correct. But the list of excluded Proposed ADRs (`docs/systemPatterns.md:44`) does not name them either, so the table and `docs/adr/` are out of step.
   - This predates the diff.
   - Respect check: the change keeps ADR-038 (full byte comparison), ADR-016 (content-addressed continuity) and ADR-017 (isolated-root install).
   - Closure condition: add ADR-037, ADR-038 and ADR-039 to the list at line 44.

**Nit:** `classify_path_observable` resolves the root, and `_project_path` resolves it again on every call (`cdad_packet.py:301,433`). This costs only extra `resolve()` calls and has no functional effect.

## Abstentions
- **Full suite:** ABSTAIN. `.cdad/evidence/full-suite-010-000.log` (14 lines, last one about 54%) has no summary line and no rc yet. I leave it to the orchestrator as the closer. It does not block the rest of the verdict.
- **Model family:** I cannot confirm that the implementer used a different model family, because it is not declared. I did not count that point towards the bucket.

## Evidence
- **Files modified in the repo:** none. `git status --short` showed only the untracked `discovery.md`, before and after.
  - I wrote only temporary files: `/tmp/opencode-render.txt`, `/tmp/opencode/rv010`, `/tmp/opencode/iso` and `/tmp/opencode/adr-*.txt`.
  - One `write` attempt was denied by permissions (it was for the byte comparison). I did that comparison through stdin instead.
- **Commit:** none, since this role is read-only. HEAD reviewed: `d45d374`.
- **Commands:**
  - `cdad_packet.py validate-request|render --project-root <abs> --execution-context <abs>/.cdad/executions/exec-010-000-continuity-relative-root-001/execution.json --request <abs>/.cdad/packets/010-000-continuity-relative-root-reviewer-review-004/REQUEST.json` → both rc=0.
  - `git diff 34dcd9b..HEAD` (6 files, +363/−41).
  - `python3 -m pytest -q -p no:cacheprovider tests/test_010_000_continuity_relative_root.py` → `5 passed in 31.20s`. This was that one file, not the suite; test_D installed only into a temporary root.
  - Isolated copy (rsync without `.git`/`build`): `pytest ...::test_D_installed_consumer_reproduces_relative_equivalence` → `1 passed in 19.85s`.
  - Temporary fixture (results quoted above):
    - `begin .` → rc=0;
    - `verify-begin` from the absolute root and from `.` → rc=0, same `body_sha256`;
    - checkpoint plan, relative vs absolute → equal (True True), symlink vs absolute → equal (True True);
    - begin with `/etc/passwd` in references → rc=1 `reference must be relative to project root`;
    - `validate-request` from the absolute root and from `.` → rc=0.
- **FYI:** `docs/specs/010-000-continuity-relative-root/discovery.md` is untracked and outside the range reviewed.
