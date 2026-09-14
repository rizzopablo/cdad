# State Detection — Epic level

Logic to detect which epic stage the project is in.

## Algorithm

Apply it in order, stop at the first condition that matches.

### Step 1 — Does `docs/.cdad-state.json` exist?

If yes, read the epic fields:

- `active_epic`: id of the active epic, or `null`/absent.
- `epic_stage`: `epic-discovery | epic-planning | features-loop | epic-integration | epic-closure | epic-done`.
- `epic_features`: list of the epic's features with their status (`done | in-progress | queued | blocked`).

If `active_epic` is `null` or the field does not exist: there is no active epic. The user is starting a new one or working only at the standalone feature level.

### Step 2 — If there is no state file, infer from files

Look for `docs/epics/`. If it exists:

- Most recent folder without `closure.md` → active epic.
- If it has `plan.md` with an approval mark → the epic is in `features-loop` or later.
- If it has an unapproved `plan.md` → `epic-planning`.
- If it has `decomposition.md` only, without `plan.md` → `epic-discovery`.
- If it has `integration.md` but not `closure.md` → `epic-integration`.
- If it has `integration.md` with green E2E and `closure.md` in draft → `epic-closure`.

### Step 3 — Detect feature progress within the epic

For each feature listed in `epic_features` (or inferred from `docs/specs/<epic-num>-*`):

- Look for an entry in `docs/progress.md`. If it is under "Done", mark `done`.
- If it is under "In progress", mark `in-progress`.
- If it does not appear, mark `queued`.
- If it has a blocking mark, mark `blocked`.

### Step 4 — Detect the feature currently in development

If `active_feature` is set in the state file and starts with the active epic's prefix (`<epic-num>-...`), that is the epic's in-progress feature.

If `active_feature` is set but does NOT belong to the active epic: the user is working on a standalone feature in parallel. This is valid but worth flagging:

> *"I detected that you are working on feature `<X>` but it does not belong to the active epic `<epic-id>`. Is it a standalone feature (in parallel to the epic) or do you want to change the active epic?"*

### Step 5 — Output

Communicate to the user in a single sentence:

> *"You are in epic `<epic-id>`, stage **<epic-stage>**. <X of Y features done>. Next step: <proposal>. Shall we advance?"*

## Special cases

### Epic without features defined yet

If `epic_features` is empty and `epic_stage` is `epic-planning`, the plan is incomplete. Go back to Stage E2 to complete the decomposition before advancing.

### Epic with a standalone feature that seems to belong

Example: there is an active epic `001-facturacion-afip`, and the user creates spec `005-validar-cuit` (without the epic prefix). Likely: the user forgot to use the epic's naming convention.

Ask them:

> *"I see you created spec `005-validar-cuit`. Does it belong to epic `001-facturacion-afip`? If yes, I suggest renaming it to `001-NNN-validar-cuit` to keep traceability. If not, I'll treat it as standalone."*

### Multiple active epics

CDAD-epic assumes **one active epic at a time**. If you detect two `active_epic` (it shouldn't happen, but human error can), flag it:

> *"I detected two epics marked as active. CDAD assumes one at a time. Which one is really active and which one do we move to 'paused'?"*

For "paused", add the field `epic_features[].status: paused` or a `paused_epics: []` field to the state.

## Sanity check between state and files

If the state says `epic_stage: features-loop` but `docs/epics/<id>/plan.md` does not exist: stale state. Flag it:

> *"The state said 'features-loop' but `plan.md` is missing. I'll correct it to 'epic-planning' and we'll start from there."*
