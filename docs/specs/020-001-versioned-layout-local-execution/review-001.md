## Verdict: blocking findings

The result is **not ready for owner acceptance**. These findings continue the correction loop within result-family round 1/2; this report does not authorize an additional round or approve the feature.

### Required — CI gate writes into the legacy store on migration refusal

**Verdict: BLOCKING · Bucket: h**  
`scripts/cdad-ci-gate.py:148–162, 931–934`

When `operational_dir()` rejects an unmigrated or invalid layout, `default_evidence_root()` falls back to `.cdad/local`. The gate then reserves a run directory there before reporting the underlying problem. This both writes despite PC-2’s no-write refusal and creates new operational evidence under the old hardcoded path, contrary to PC-1.

**Smallest correction:** propagate the layout error and stop with migration guidance before reserving evidence; do not fall back to `.cdad/local`.

### Required — Migration instructions cannot handle all declared legacy states

**Verdict: BLOCKING · Bucket: h**  
`skills/cdad-cycle/references/layout-migration.md:38–50, 59–73`

The guide says to stop whenever `cdad/project-layout.json` exists, but a declaration lacking `operational_dir` is explicitly an unmigrated state and must be updated in place. It also unconditionally says to move `.cdad/project-layout.json`, although the guide later recognizes projects with no locator. Following the steps as written therefore stops or fails for supported migrations.

**Smallest correction:** distinguish an existing schema-1 declaration from a conflicting destination, and make moving the old locator conditional on its existence. Give the no-locator and fixed-path schema-1 cases explicit paths through the steps without merging stores.

## Verified and limits

- Reviewed the approved spec, plan, migration guide, the changed test diff and selected implementation paths. The version-change pointers distinguish marker disagreement from same-version edits.
- `python3 scripts/cdad-suite.py validate` returned **rc=0**, status `ok`. The historical continuity fixture files are recorded as **100% identical renames** in the diff.
- The packet preflight’s listed report exemptions were inspected; no writing or dispatching command is listed, and `prepare --propose-policy` retains its separate exemption.
- I did **not** run the full or focused test suites, reproduce the CI-gate write, independently establish the exact new/renamed nodeid counts, or exhaustively verify every changed test and consumer. The coordinator’s full-suite run is separate and was not available as evidence here.
- **PC-3 contextual closure remains open** because of the guide finding; PC-1 and PC-2 remain open because of the CI-gate finding. The inspected PC-4 pointer supports its semantic promise, subject to the executable evidence above not being independently rerun.

## Abstentions

I abstain from a complete verdict on test conservation—including the rule-4 text oracle and all 26 renamed/inverted nodeids—and on the executability of every outstanding-effect disposition and suspended-unit path. Those require further independent verification; they are not asserted as defects here.