Review-007 is fixed and committed as **32b35026**. One check, `make validate`, still fails (F011), and it fails the same way without my change.

**What changed.** Property-test dispatch, the gate and the handoff now apply only to invariants for which the approved contract selects executable property tests. Invariants kept as reviewable restrictions get no campaign. They go to the contextual independent review at Stage 4. When the contract does select property tests, the gate and its reproducible evidence stay as before.

**Files edited.**
- `skills/cdad-cycle/references/stage-3-tdd.md`: the property-tests intro, step 8, the PROPERTIES table row, sub-phase 3.4, the re-entry question and the gate checklist.
- `skills/cdad-cycle/SKILL.md`: the property-tests paragraph, the 3.4 tree, the gate checklist and row 3.3-3.5.
- `skills/cdad-cycle/references/handoff-prompts.md`: the properties handoff now lists only the invariants the contract selected.
- `skills/cdad-cycle/references/state-detection.md` and `re-entry.md`: both now say the same.
- `skills/cdad-cycle/packets/substages/test-writer-properties.md`: the packet instruction now says the same.
- `sources/roles/test-writer.md`: rule 8 now says the same.
- The four derived agent files `agents/cdad-test-writer*.md` and `agents/claude-code/cdad-test-writer*.md`, regenerated with `make agents` (exit 0).

I did not edit tests and did not install or deploy. `docs/.cdad-state.json` was already modified before I started, so I left it out of the commit.

**Regression, exit codes.**
- Packet validation (`validate-packet`): 0.
- `pytest tests/test_*generate*.py`, which also matched `test_cdad_generate.py`: 10 passed, exit 0.
- `pytest` on `tests/test_role_packet_render.py` plus 25 test files that mention stage-3-tdd, handoff-prompts, properties or test-writer.md: 216 passed, 1 skipped, exit 0, 6m11s.
- `make validate`: exit 2. It has one failed assert, F011, which runs `scripts/validate-subagents.sh`. That script reports drift and missing files in the installed agent and skill copies under `~/.claude` and `~/.config/opencode`.
- I compared against a stashed baseline without my edits, which fails the same F011 check. I cannot fix it without installing, which the task forbids.

**Self-introduced break.** My first SKILL.md edit failed assert F006, which requires the phrase "Property tests derived from invariants". I restored that phrase, and F006 now passes.

I did not run the complete suite; the evidence is the selection above.