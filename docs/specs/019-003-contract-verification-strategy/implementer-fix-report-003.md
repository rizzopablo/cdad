Blocker fixed in two commits. The packet's own checks pass, and the regression selection passes (138 tests). `validate-consistency.sh` and `validate-subagents.sh` still fail, but on installed-copy drift that this change did not cause; details below.

**Packet validation (route C)**
- `validate-request`, `validate-packet` and `validate-state` all returned rc=0 with VALID.
- `render` for this packet is byte-identical to `PACKET.md` (7387 bytes).
- `render --route C` matches the identification in the dispatch on every field.
- The spec's sha256 matches the value in the packet.

**Changes**
- `skills/cdad-cycle/references/stage-4-review.md`
  - Loop step 3 and the exit-gate item no longer require an unconditional green suite. They now split the checks: executable parts keep the suite green under the evidence policy, semantic-only parts run the applicable structural checks and return to contextual review, and mixed promises need both.
  - The "suite green after each" wording in the receiving-feedback paragraph (line 179) now points to step 3.
  - Step 4 now says the "skip the second pass" option does not apply to a corrected semantic-only or mixed contextual part.
- `skills/cdad-cycle/SKILL.md` (Gate 4→5): same exit-gate condition, mirrored.
- `skills/cdad-cycle/references/receiving-feedback.md` (line 44): the unconditional "suite green after each" wording is now conditional, pointing to loop step 3.

I checked `agents/`, `build/`, `skills/` and `sources/` for the old phrases and found none left. `stage-4-review.md` has no source copy to regenerate, and no test asserts on the replaced wording.

**Commits**
- `77c6e458` — refactor: condition stage-4 loop/gate on applicable checks (019-003 review-003): stage-4-review.md, SKILL.md.
- `8ed624e9` — refactor: align receiving-feedback fix loop with conditional stage-4 checks (019-003 review-003): receiving-feedback.md.
- `docs/.cdad-state.json` was already modified when I started and is not in either commit.

**Commands and logs** (logs in `.cdad/orchestration/epic-019/`, not committed)
- Regression, final tree:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider` on `test_006_006_u2_review_procedure.py`, `test_006_006_u3_review_route_and_gate.py`, `test_006_006_u5_exemption_record.py`, `test_cdad_generate.py`, `test_cdad_adapters_opencode.py`, `test_010_001_documentary_contracts.py`, `test_010_002_documentary_role_integration.py`, `test_010_003_documentary_pilot.py`, `test_006_004_u3_principle_single_source.py`, `test_005_005_t2_docs_policy.py`, `test_014_001_suite_evidence_defaults.py`, `test_004_003_t5_reentry_equivalence.py`, `test_006_002_u2_neutral_skill.py`, `test_006_003_u5p_no_family_requirement.py`. Result: **138 passed**, log `019-003-fix-003-final-pytest.log`. (`…-fix-003-post-pytest.log` is an earlier run, before the receiving-feedback edit; superseded.)
- `bash tests/validate-consistency.sh`: rc=1, 182 passed, 1 failed (F011). Log `019-003-fix-003-validate-consistency.log`.
- `bash scripts/validate-subagents.sh`: rc=1 (the earlier rc=0 came from `tail`, not the script). Log `019-003-fix-003-validate-subagents.log`.

**F011, stated plainly:** the failure comes from `install.sh --check`, which compares the installed copies under the home directory with the repo. The drift list includes agents and skills this change does not touch, so the check fails with or without this diff. I did not measure the parent commit. The installed `cdad-cycle` skill now also differs further from the repo, as expected; installing is not in scope, so I did not install anything.

**Routes**
- *Semantic-only correction:* fix → applicable structural checks → contextual independent re-review (step 4 cannot skip it) → closure category. Without that re-review the promise is "Missing", not "Supported".
- *Mixed:* the executable part keeps the suite green under the evidence policy; the contextual part gets its re-review; neither replaces the other.

**Flagged for the reviewer:** step 4 (the "skip the second pass for mechanical fixes" clause) was not in the literal blocker. I changed it because it would otherwise let a corrected semantic product close without the only verification it gets. It is a judgment call, so please weigh it.

**Not done**
- Full suite not run. Recorded as *suite completa no realizada*: this is a review-fix, not a feature close. The run covers only the 14 files above; it does not establish the state of the rest of the suite.
- The `test_pd16b` docstring that the review flagged as stale is untouched; per the packet, test edits belong to the test-writer.