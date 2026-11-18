## Report: 019-003 review-fix-002

**Route C validated.** `validate-request` and `validate-packet` exit 0. The full canonical render is byte-identical to PACKET.md (7904 bytes), and the route C identification matches the dispatch. The dispatch's `sha256` matches the spec file.

**Result:** both blockers are fixed in two `skills/` commits. Nothing else changed. No tests were edited. There was no install, deployment, or full suite run.

- `0104b026` refactor: align lightweight verification guide and re-entry compatibility with renderer (019-003)
- `64472996` refactor: point lightweight exemption at canonical approval record; drop local evidence path from re-entry (019-003)

Files: `skills/cdad-cycle/references/re-entry.md` and `skills/cdad-spec-and-test/SKILL.md`. `agents/` and `sources/` were not changed, so I did not regenerate derived agents. `grep` shows the old claim survives only in historical review records under `docs/specs/`, which I left alone.

### Blocker 2 — re-entry.md compatibility

I checked the behavior against the renderer and a frozen packet. The probe used a scratch copy of the skill tree, and the repo was not changed.

| Case | Result |
|---|---|
| A. Frozen request, unmodified | render == PACKET.md |
| B. Frozen request, live `common.md` drifted | validate-request 0, validate-packet 0, render byte-identical |
| C. Historical request (no `instruction_sources`), live drifted | validate-packet 2: "packet differs from canonical rendering" |
| D. Frozen request, repo as is | validate-packet 0 |
| E. Historical request, repo as is | validate-packet 2 |
| Exit 1: historical, frozen revision live again | validate-packet 0 |

The new text describes frozen and historical requests separately. It says that a structural match is not semantic currency, and it cites the existing controls: the two exits and the rule that validating a receipt approves nothing. The probe showed that `validate-request` alone does not catch a historical drift. Only `validate-packet` does.

### Blocker 1 — lightweight guide

- The per-promise format now includes property, method, acceptance, evidence, limits and checks.
- Rule 2 now requires, before the 1→2 transition, either the independent sufficiency review (stage-2 "Draft review sub-phase", proportional depth) or the owner's exemption. The exemption is registered in the approval's `stage_history` entry, which is the canonical record.
- The 1→2 row carries the same requirement. No new gate row was added.
- The mixed-promise closure sentence, the closing section and the 2→3 and 3→4 rows are unchanged.
- The walkthrough is in `.cdad/orchestration/epic-019/019-003-fix-002-walkthrough.md`. It is a textual trace of the mixed-promise and exemption branches. It was not an agent run.

### Commands and evidence

Regression selection, run before the edits, after the edits, and after the final text:

```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
  tests/test_006_006_u2_review_procedure.py tests/test_006_006_u3_review_route_and_gate.py \
  tests/test_006_006_u5_exemption_record.py tests/test_cdad_generate.py \
  tests/test_cdad_adapters_opencode.py tests/test_010_001_documentary_contracts.py \
  tests/test_010_002_documentary_role_integration.py tests/test_010_003_documentary_pilot.py
```

Result: **94 passed** each time (83.86s, 82.41s, 102.71s). This includes `test_pd16b_*` and `test_pd10_stage2_states_the_declared_form_of_the_exemption`. Logs: `.cdad/orchestration/epic-019/019-003-fix-002-{baseline,post,final}-pytest.log`.

Probe: `bash probe.sh <project> <scratch>`, a script kept in `/tmp` outside the repo. Output: `.cdad/orchestration/epic-019/019-003-fix-002-probe.log`, `…-exit1.log`, `…-snapshot.log`.

Snapshot revision: the probe started at `ffba1ed6`. The final probe ran at `64472996`. The renderer and `skills/cdad-cycle/packets/` are unchanged. `scripts/cdad_packet.py` is a wrapper that runs the canonical `skills/cdad-cycle/scripts/cdad_packet.py`, so there is only one renderer.

### Open items for the orchestrator

1. **Lightweight route approval (decision needed).** The exemption record is now pointed to canonically. But no text says whether the lightweight route has a spec-approval step, and `cdad-spec-and-test` never mentions approval. If the route has no approval, the exemption branch has no record. I did not invent a mechanism, as the packet asked.
2. **Semantic currency drift.** Frozen packet 002 runs under older implementer instructions (`ef3dab…`). The live `roles/implementer.md` at HEAD is `6e13306…`. Any historical request is rejected today (case E). This is a currency decision for you, not a fix.
3. **Test wording conflict (for the test-writer).** `test_pd16b_reentry_declares_the_compatibility_policy_between_revisions` has a docstring that says every published package becomes non-receivable after source changes. That is false for frozen packages. The regex still passes because of the historical bullet. I did not edit the test.
4. **Scope notes.** The 1→2 row and rule 2 were edited, as the finding required. Rows 2→3 and 3→4 and the closing section were not. The logs in `.cdad/orchestration/` are git-ignored, uncommitted, and outside write_scope, as the packet directed. `docs/.cdad-state.json` was already modified and I did not touch it.