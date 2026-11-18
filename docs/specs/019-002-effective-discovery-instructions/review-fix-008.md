The two rules are now in the places the orchestrator reads, and the 14 test files I ran all pass (142 passed, 4m07s). I did not run the complete suite, so "suite completa no realizada".

The packet passed `cdad_packet.py validate-packet` (rc=0) and its contract sha256 matches `spec.md`. The commit is `8902d9b1`, "fix: make discovery/approval rules salient in orchestrator SKILL.md and role source".

- **`skills/cdad-cycle/SKILL.md`:**
  - The "You do NOT" list has two new bullets, worded as you gave them: don't investigate the project yourself, and don't approve an unreviewed draft spec. The second states the four-field exemption rule (`exempted_by`, `delegated`, `requested_by`, `reason`) and never backfilling an exemption.
  - The "You do" list has the new bullet: have `discovery.md` with an attributed Dialogue context and a recorded readiness result (`re-entry.md` R1-R5) before any architect dispatch or spec draft.
- **`sources/roles/orchestrator.md`:** the first two bullets of "Operating rules (strict)" are now one-sentence pointers to those two "You do NOT" bullets. The existing detailed bullets are untouched.
- **Derived agents:** `make agents` regenerated `agents/cdad-orchestrator.md` and `agents/claude-code/cdad-orchestrator.md`, and both are in the commit.

I ran the eight test files you listed plus six more that reference `SKILL.md` or the "You do NOT" list: `test_006_002_u6_context_discipline`, `test_006_004_u4_decisions_table`, `test_005_006_t6_owner_reviewfix`, `test_010_001_documentary_contracts`, `test_010_002_documentary_role_integration` and `test_005_005_t2_docs_policy`. The first run timed out at 120s, so I reran it with a longer limit. I edited no tests.

The full output of the passing run is in `/tmp/impl008.log`.