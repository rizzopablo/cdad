The review-006 blocker is fixed by regenerating `build/staging`, and the isolated install now delivers the candidate bytes. I didn't change any tracked product files, so there is no commit.

**Intake.** `validate-request` and `validate-packet` both returned rc=0. The full render matches `PACKET.md` byte for byte. The route C identification matches the dispatch.

**Cause.** `build/staging` is gitignored and generated, and `install.sh` reads only from it. Before regeneration, both `cdad-orchestrator.md` copies in staging (opencode and claude-code) differed from the candidates in `agents/`. The other 20 agent files were identical.

**Fix.** The canonical procedure is `make staging`, which runs `scripts/cdad-generate.py` for opencode and claude-code with the odoo stack into `build/staging`. It exited rc=0. After it ran, all 22 staged agent files were identical to the candidates.

**Isolated install.** I ran `CDAD_INSTALL_ROOT=<tmp> CDAD_SKILL_EXTRA_DIRS="" bash install.sh` at HEAD `5f3f60c3` (candidate `73b44e62`). It exited rc=0, with "11 cdad agents present". I compared every agent and skill file changed between `0b11b5fb` and `73b44e62` (14 agents, 16 skill files) with `cmp`:
- **Agents:** 7 opencode agents and 7 claude-code agents were identical, including both orchestrators.
- **Skills:** all 16 skill files were identical at each of the three skill destinations.
- **Result:** 0 differences and 0 files missing at any destination.

**Durability.** Since staging isn't tracked, distribution needs no tracked source change. It does need `make staging` run before any install or publish, because a stale `build/staging` brings the blocker back. I hand-edited no derived files.

I didn't touch the real installation, edit tests or run the full suite. The only modified file in the working tree is `docs/.cdad-state.json`, which was already modified before I started.

Evidence is in `.cdad/orchestration/epic-019/019-003-review-fix-006-evidence/`:
- `REPORT.md`
- `staging.log`
- `isolated-install.log`