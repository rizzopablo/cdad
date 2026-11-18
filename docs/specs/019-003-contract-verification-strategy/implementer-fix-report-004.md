I fixed the blocker from `review-004` and committed it as `fc7988f5`. I did not install or deploy anything.

**Validation:** I used Route C. `validate-request` passed, and the render of `REQUEST.json` is byte-identical to `PACKET.md`.

**Fix in `skills/cdad-cycle/SKILL.md`:** I reworked "Verification — required evidence" to follow each promise's approved method.
- Executable parts keep RED/GREEN and the existing Test evidence policy.
- Semantic-only parts get no fabricated RED and no suite requirement. Their evidence is the production plus contextual independent review at Stage 4.
- Mixed promises carry both.
- I also fixed the "Coverage ≠ contract" rule, the "I'll add tests later" refutation, and the "Coverage is already high" refutation.
- I added a Stage 4 row for the contextual-review evidence.
- I reworded the R7 line near the top of the guide, which said every promise is verified "by behavior", so it follows the per-promise method too.

**Other consumer found:** `sources/roles/orchestrator.md` said every postcondition is traced to "at least one test". I made it conditional the same way. I applied the same text change by hand to the two tracked agent files, `agents/cdad-orchestrator.md` and `agents/claude-code/cdad-orchestrator.md`. I then regenerated them with `scripts/cdad-generate.py` for both runtimes and confirmed they match the source.

**Tests:** I ran `python3 -m pytest -q tests -k "019 or 010_001 or documentary or orchestrator or generate or drift" -x`. All passed, with no failures. The log is at `.cdad/orchestration/epic-019/019-003-fix-004-pytest.log`, and it holds only the pytest tail, not the full run output. I did not edit any tests.

**Not done:**
- I did not run the full suite, so "suite completa no realizada" applies.
- I did not run `validate-subagents.sh`. The review reported a pre-existing install-drift failure there, and I did not measure the baseline.
- I did not re-examine the Stage 4 files, which the review had already corrected.

`docs/.cdad-state.json` was already modified before I started. I left it out of the commit.