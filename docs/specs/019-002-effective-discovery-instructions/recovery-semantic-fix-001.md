I fixed the three blockers in the four allowed reference files and committed them as `5bb788dc`. One consistency check, F011, fails, but it fails the same way without my changes.

**Packet validation (route C):** `python3 -I scripts/cdad_packet.py render --request <REQUEST.json>` output is byte-identical to `PACKET.md` (`cmp` returned SAME). The spec sha256 matches `cd61455c…1f0382`. I did not run `validate-request` or `validate-packet` myself.

**Changes** (all under `skills/cdad-cycle/references/`):
1. **`stage-5-merge.md`:** the closing instruction now says to use the existing closure transition (`register-transition --transition closure`, `project-execution.md` §9). That transition leaves `idle`/`null`. The contradictory "update state to `done`/`null`" mandate is gone, and the text now says not to hand-write `done`/`null`.
2. **Optional consultation:**
   - `stage-1-discovery.md` exit gate: the brainstorm handoff is sent only if consequential uncertainty or needed independent judgment remains. Otherwise it goes straight to the spec-writing draft (Stage 2, sub-phase 2.2) with no consultation.
   - `stage-2-specification.md`: sub-phase 2.1 is labeled "only when consulted" and skipped when readiness already holds. The spec-writing input uses a brainstorm summary only if a consultation happened. Otherwise it uses the recoverable decisions made in the dialogue.
   - `stage-2-specification.md` line 146: "Still brainstorm + approval" now reads "Still dialogue (consultation only if warranted) + approval".
   - `re-entry.md`: after per-feature discovery, it advances to the brainstorm only if a consultation is still warranted. Otherwise it goes to spec writing.
3. **`stage-1-discovery.md`:** "one to three per turn" now reads "as many per turn as are useful in context". I added no new quota, gate or schema.

**Evidence:**
- `pytest tests/test_019_*.py` plus the template, decisions-table, docs-policy and re-entry-equivalence tests: 33 passed in 17.06s.
- `bash tests/validate-consistency.sh`: 182 pass, 1 fail. The failure is "F011: scripts/validate-subagents.sh (active profile) → FAIL". It gives the same 182/1 result with my changes stashed, so my edits did not cause it. I did not look into why that script fails.
- I did not run the full suite. I touched no tests and no files outside the four named ones.
- `docs/.cdad-state.json` and `recovery-contextual-review-001.md` were already changed or untracked before I started, and I left them alone.