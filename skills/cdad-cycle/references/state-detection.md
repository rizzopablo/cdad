# State Detection

Logic to determine which stage of the CDAD cycle the project and the active feature are in.

> **Canonical owner (PD-13, 005-006).** This document is the canonical owner of
> the feature/Memory-Bank recognition (Steps 1-2 and "Memory Bank detection"
> below). The epic-stage vocabulary is owned by
> `cdad-epic/references/state-detection.md`. The start-from-rest composition that
> uses both — and re-declares neither — lives in `project-start.md`, which
> references this document.

## Detection algorithm

Apply it **in order** and stop at the first condition that matches.

### Step 1: Does `docs/.cdad-state.json` exist?

If it exists, read it. The minimal structure is:

```json
{
  "version": 1,
  "active_feature": "<feature-id>",
  "current_stage": "discovery|specification|tdd|review|merge|done|idle",
  "tdd_substage": "red|green|refactor|properties|integration|null",
  "postconditions_status": { "1": "green|red|pending", ... }
}
```

Full schema (all possible fields, including the epic ones):
`assets/state-template.json`. This table shows only the subset that
`cdad-cycle` needs to detect the stage of a feature.

`current_stage: "idle"` is valid only when `active_feature` is
`null` — "no feature in progress". It is not a stage of a feature's cycle
(those are the five: discovery|specification|tdd|review|merge, plus `done` at
closure); it is the resting value between features.

That is the source of truth. **But still do a sanity check** against the real files of step 2: if the state file says `current_stage: tdd` but there are no tests in the repo, it is outdated and you notify the user.

**Active epic detection**: if the state file has a non-null `active_epic` field, the current feature belongs to an epic. This does NOT change the flow of `cdad-cycle` (the feature runs the same way), but it does change three things:

1. **The feature ID usually has the epic's prefix**: `<epic-num>-<feat-num>-<slug>` (e.g. `001-002-generar-xml`). Treat that format as valid.
2. **There is additional context in `docs/epics/<epic-id>/plan.md`** worth reading in Stage 1 (per-feature discovery). Specifically: the "Cross-feature contracts" section of the plan may contain interfaces the current feature must respect.
3. **Feature closure must suggest going back to the epic coordinator** (see `references/stage-5-merge.md`, final section).

If you detect an active `active_epic`, communicate it to the user in the opening sentence:

> *"You are on feature `001-002-generar-xml` (part of epic `001-facturacion-afip`), stage **<X>**. <next step>. Shall we proceed?"*

### Step 2: If there is no state file, infer from files

Apply the following checks in order:

| Condition | Inferred stage |
|-----------|---------------|
| `docs/projectbrief.md` and `docs/activeContext.md` do not exist | **bootstrap** (load `references/bootstrap.md`) |
| Memory Bank exists but `docs/specs/` is empty or does not exist | **discovery** (next feature about to start) |
| `docs/specs/<feat>/spec.md` exists but **without an approval mark** | **specification** (in writing/brainstorm) |
| `docs/specs/<feat>/spec.md` approved, but `tests/` has no tests for this feature | **tdd**, sub-phase **red** (test-writer hasn't written yet) |
| Tests for the feature exist but fail (real RED) | **tdd**, sub-phase **red→green** (ready for implementer) |
| Tests pass (GREEN), but property tests are missing if the spec asked for them | **tdd**, sub-phase **properties** |
| Tests + property tests green, but E2E is missing if the spec asked for it | **tdd**, sub-phase **integration** |
| Whole suite green, but `docs/specs/<feat>/review.md` does not exist | **review** |
| `review.md` exists with unresolved blockings (later commits don't address them) | **review** (loop with stage 3) |
| Review clean, suite green, but `docs/activeContext.md` has no entry for this feature | **merge** (CI + Memory Bank update pending) |
| Memory Bank updated, feature merged | **done** |

> Suite frequency follows the evidence policy owned by
> `references/stage-3-tdd.md` §"Test evidence policy" (proportional regression;
> complete suite at feature closure).

### Step 3: Detect the spec's approval mark

To distinguish an approved spec from a draft one, look for **one of these signals** in `docs/specs/<feat>/spec.md`:

1. Final line of the spec with the format: `Status: Approved by <X> on <YYYY-MM-DD>`
2. YAML frontmatter with `approved_by: <X>` and `approved_at: <date>`
3. Commit message saying `docs: approve spec for <feat>` (if you have access to git log)

If none is present → treat as NOT approved.

### Step 4: Detect the active feature

The state file's `active_feature` field wins. If there is no state file:

1. If there is a single folder in `docs/specs/` that has no `review.md` and is not marked as done → that is the active one.
2. If several are in progress → ask the user which one is active before continuing.
3. If there is none → the active one is the next one to be created.

### Step 5: Verify consistency between state file and files

If the state file says one stage but the real files suggest another, **the file wins** (it is the reality). Notify the user:

> *"The state file said `current_stage: review` but the tests are red. I'm going to correct the state to `tdd:green` and we start from there. OK?"*

## Tests pass / fail — how to verify it

To determine whether the tests pass or fail:

1. If your environment allows execution (`bash` available), run the suite and read the exit code.
2. If not, ask the user for the output: *"Can you run the suite and paste the final summary for me? I need to know how many tests pass and how many fail."*
3. Do NOT infer "green" because the code compiles or because the test "looks good". Green is verified empirically.

## Memory Bank detection

Minimum to consider the Memory Bank initialized:

- `docs/projectbrief.md` exists and is not only placeholders.
- `docs/activeContext.md` exists.
- `docs/progress.md` exists.
- `docs/systemPatterns.md` exists (it can be short but has real content).

If any is missing → bootstrap.

## Output of the step

After applying the detection, communicate to the user in a single short sentence:

> *"You are in **<stage>** working on `<feature-id>`. <one sentence with the next logical step>. Shall we proceed?"*

And wait for their answer before continuing.
