I removed the orchestrator's investigation prohibitions and replaced them with one short rule. The eight test files you listed pass (68 passed in 147s), and the change is committed as `1ef42cc2`.

The packet checked out before I started. The canonical render matched `PACKET.md` byte for byte, and `validate-packet` returned rc=0.

**What changed**
- **`skills/cdad-cycle/SKILL.md`:** I deleted the first "You do NOT" bullet (the ban on reading code and running the product). In its place, above the list, is your canonical rule: the orchestrator may investigate, never writes tests or the product, records technical findings as attributed technical evidence in the Dialogue context, and consults the architect when it needs an independent judgment or the spec draft. The approval/exemption bullet is untouched; it is now the first bullet in the list.
- **`sources/roles/orchestrator.md`:**
  - The old pointer bullet is replaced by a short pointer to the new rule, and the exemption pointer now says "first bullet".
  - I dropped "You do NOT answer technical questions yourself" and the "never read sources or run the product" sentence.
  - I removed "technical investigation" from the roles-contract row's list of work the orchestrator never does.
- **`skills/cdad-cycle/references/re-entry.md` R4:** technical uncertainty is investigated "by the orchestrator or the architect". The bounded/blocking wording and the rule for a verified contradiction of an owner assumption are unchanged.
- **`skills/cdad-cycle/references/stage-2-specification.md`:** "You do not investigate technically" is replaced by a pointer to the attributed-evidence rule, and the ban on authoring the report, the spec or the review stays.
- **`agents/`:** regenerated with `make agents`. Only the two orchestrator files changed, `agents/cdad-orchestrator.md` and `agents/claude-code/cdad-orchestrator.md`.

I didn't edit any tests. `docs/.cdad-state.json` shows as modified in the working tree and is left uncommitted. It is outside my write scope, and I didn't investigate why it changed.

Command run: `python3 -m pytest -q tests/test_019_002_discovery_delivery.py tests/test_cdad_generate.py tests/test_004_002_t7_l1_derived.py tests/test_005_006_t2_intake.py tests/test_006_006_u3_review_route_and_gate.py tests/test_006_002_u6_context_discipline.py tests/test_role_packet_render.py tests/test_role_packet_consumers.py`. I did not run the complete suite; it is not recorded as run.