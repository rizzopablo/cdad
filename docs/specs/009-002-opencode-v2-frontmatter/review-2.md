## Re-review 009-002 (packet `…-reviewer-review-002`): BLOCKING, B1 is still open; O2 is closed

The two fix commits `0939a1f` and `a20c3f3` repair t5 and t7, but 8 PD-10 mutation tests still fail at HEAD (B1-r).

**Intake:** route A. `cdad_packet.py render` output matches `PACKET.md` byte for byte (`cmp` → PACKET_MATCH), `validate-packet` rc=0, and the spec's sha256 is `c62c9e7c…`.

**What the fixes close**
- **Global collection:** `pytest --collect-only tests/` collects 1849 tests with no errors.
- **t5 and t7:** run together with t7_capacity, 005_004_t4, u6fix7, 006_006_u4, 009_002 and read_map, 82 tests pass. t7 imports `RULE_RE` again and its frontmatter cut (`[4:-4]`) is correct.
- **`without_maps`:** it now removes only read, grep, glob and edit. The shell rules (including V1 `bash`, read as shell), the `*` rule, the other keys and the body are still compared. The new test shows it notices a changed shell effect.
- **O2:** the tests now check the 11 committed `agents/*.md`. They fail if none are found and when a PC-2 agent is missing. Staging is only an extra check.

**B1-r: the PD-10 mutation tests still use V1 anchors** (Required · Verdict: BLOCKING · Bucket: h)
- **Evidence:**
  - `tests/test_004_001_t7_pd10.py:184,298`: `test_mut_m1` through `m8` fail with `harness precondition: mutation anchor not found`. The anchors are V1 lines such as `'  read:'`.
  - Run on fresh `git archive` copies after `make agents`: 16 passed at `9fc90b1`, 11 failed at `86c8ccc`, 8 failed at `e3f59bd`, 8 failed at `a20c3f3`.
  - The PD-10 checker itself is already on V2 and passes 39/39 on the real agents.
- **Consequence:**
  - The full suite fails, so the closer cannot close the unit.
  - Nothing proves the private-path and permission checker can still fail. A checker that passes everything would go unnoticed.
  - The pd10 family was part of B1's closure condition. The previous review missed this file.
- **Closure condition:** move the m1–m8 anchors to the V2 `permissions:` list, then `pytest tests/test_004_001_t7_pd10.py` → 16 passed.

**Out of scope here:** O1 is listed by `cdad-suite.py validate` and stays with the coordinator. O3 is a declared limit of this unit.

## Abstentions
I did not run the full suite or the OpenCode runtime.

## Evidence
- **Modified files:** none in the repo. `git status` still shows only the existing ` M docs/.cdad-state.json`. My copies are under `/tmp/opencode/rr-*`.
- **Commits:** none.
- **Commands:** `render`/`validate-packet`, `pytest --collect-only`, the targeted `pytest` runs, `cdad-suite.py validate`, and `git archive` + `make agents` on 4 revisions.
