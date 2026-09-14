# Feature Handoff — Delegation to `cdad-cycle`

How the epic coordinator issues the handoff so the user starts a feature by delegating to the `cdad-cycle` skill.

## When to issue a feature handoff

In the feature loop (the stage between E2 and E3 of the epic), after a feature closes, you identify the next `queued` feature whose dependencies are `done`.

Logic:

1. Filter `epic_features` by `status: queued`.
2. For each queued one, verify that all the features in its "Dependencies" column are `done`.
3. If there are several candidates (parallelizable), ask the user which one to start.
4. If there is only one, that one is next.

## Handoff packet format

```
🔀 HANDOFF: Next feature of the epic

Feature: <id>
Description: <1 line from the plan>
Dependencies: <list, all marked done>

──────────────────────────────────────────
To start it (recommended: new chat if there are no sub-agents):
Note: the feature runs respecting the Roles Contract of `cdad-cycle`
(independent of the harness: delegates via `cdad-*` sub-agents if there are any,
handoff packet to a new chat if not). The epic does not assume a harness.

1. Open a new chat (or let `cdad-cycle` delegate if there are `cdad-*` sub-agents).
2. Invoke the `cdad-cycle` skill with this phrase:

   "Let's start feature `<feat-id>` of epic `<epic-id>` following CDAD."

3. The feature coordinator will:
   - Read the state (it will see that it belongs to epic <epic-id>)
   - Load the epic context (plan.md, cross-feature contracts)
   - Start Stage 1 (per-feature Discovery)

4. When the feature closes (Memory Bank updated, merged), 
   come back here to `cdad-epic` with: "Feature <feat-id> done."

──────────────────────────────────────────

Meanwhile, I (the epic coordinator) wait. Current state:

- Epic: <epic-id>, stage: features-loop
- Features done: <list>
- In progress now: <feat-id>
- Remaining queued: <list>
```

After the packet, **you end your turn**.

## Re-entry — feature done

When the user comes back saying *"Feature `<id>` done"* or equivalent:

### Validations

1. **Verify in `progress.md`** that the feature appears under "Done".
2. **Verify in the state file** that `current_stage` is `done` and `active_feature` is null or changed.
3. **Verify in `activeContext.md`** that there is a recent entry with the feature closed.

If something is missing:

> *"Before marking it done in the epic, `<X>` is missing. Did you complete it, or do you want us to review it?"*

If all OK:

1. Update `epic_features[<feat>].status: done` and `completed_at`.
2. Identify the next eligible feature.
3. If there are queued features left: issue the handoff for the next feature.
4. If ALL are done: close the loop and advance to Stage E3 (integration).

## Special case — feature in-progress in parallel

If the user is working on two features of the epic in parallel (on different branches), `active_feature` in the state file does not capture both. Options:

**Option A — single track**: one feature at a time in the state file. If they start in parallel, the second one is not tracked by the state until the first one closes.

**Option B — extended field**: add `parallel_features: [<id1>, <id2>]` to the state.

By default: **option A**. It is simpler and most projects don't need real parallelism with CDAD (the isolated-sessions discipline is easier with one feature in focus).

If the user insists on parallel: add the `parallel_features` field to the state and track both. When one closes, move it to `done` and the other remains as the single active one.

## Special case — an epic feature fails and pushes work back

If during a feature the user detects that the epic plan is wrong (e.g. an unaccounted dependency, an insufficient cross-feature contract), the epic plan has to be revisited.

The user comes back to `cdad-epic` saying *"the plan needs adjustment because of X"*. You:

1. Pause the feature in the state (`epic_features[<feat>].status: paused`).
2. Load `epic-planning.md` and apply the change to the plan.
3. Re-approval if the change touches scope or criteria. If it is only decomposition (feature split, reordering), a commit of the change is enough.
4. When the plan is updated, go back to the feature: change the status to `in-progress` and issue the continuation handoff to the user.

## Special case — a standalone feature that does not belong to the epic

If the user starts a standalone feature (without the epic prefix) while the epic is active, that's fine. CDAD does not force pausing the epic to do a standalone feature (an urgent bug fix, for example).

In that case:

- `cdad-cycle` runs normally with the standalone feature.
- `cdad-epic` is not involved.
- The state file reflects: `active_epic` stays active, but `active_feature` points to the standalone one (not of the epic).
- When the standalone closes, `cdad-epic` can resume the epic loop.

## Operational reminder

The handoff to `cdad-cycle` is the **only time** you issue something "of" an external role. You are not generating a prompt for a sub-agent; you are telling the user to use another skill. The difference matters: the other skill has its own intelligence and will coordinate its own sub-agents (test-writer, implementer, etc.).

That is why the handoff is simpler than `cdad-cycle`'s internal handoffs: you just tell the user "start `cdad-cycle` with this feature".
