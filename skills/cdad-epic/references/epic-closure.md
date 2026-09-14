# Stage E4 — Epic closure

Epic closure: Memory Bank consolidation, brief retrospective, pending ADRs (if epic-level decisions emerged that are not yet documented), closing commit.

## Your role

You coordinate. You issue the handoff to the **scribe in epic mode** for drafts. The user (human or a higher-hierarchy autonomous agent) approves; the orchestrator commits.

## Steps

### Step 1 — Handoff to the scribe

It is similar to the feature scribe (`cdad-cycle`) but with an expanded scope: it covers the whole epic.

Generate the packet with:

- `docs/epics/<id>/plan.md` (approved).
- `docs/epics/<id>/integration.md`.
- The specs of all the epic's features.
- Current Memory Bank: `projectbrief.md`, `activeContext.md`, `progress.md`, `systemPatterns.md`, `docs/adr/`.
- Aggregate epic diff (if your environment allows it, generate a cumulative diff between the epic's base commit and HEAD).

```
You are a scribe sub-agent in CDAD epic-closure mode.

Task: produce four drafts for the epic closure:
1. Epic closure entry in activeContext.md.
2. progress.md update (move the whole epic to "done").
3. ADR(s) if you detect architectural decisions of the epic that are not yet 
   documented in docs/adr/. Per-feature ones may already exist; here you look 
   for the ones that span the epic.
4. Draft of docs/epics/<id>/closure.md with summary, brief retrospective, 
   technical debt carried forward.

Context:
1. Epic plan: <paste plan.md>
2. Integration report: <paste integration.md>
3. Feature specs: <paste all>
4. Current Memory Bank
5. ADRs already created during the epic's features: <list names>

Strict rules:
- Permissions: read-only.
- You do NOT commit. You generate drafts; the user approves; the orchestrator commits.
- For new ADRs: only if the decision clearly belongs to the epic (spanning 
  several features) and is not yet documented. Mark confidence High/Medium/Low.

Expected output, four blocks:
[Draft 1: closure activeContext entry]
[Draft 2: progress.md changes]
[Draft 3: new ADRs | "No new ADRs"]
[Draft 4: closure.md]

When done:
"READY. Four drafts: <blocks>"
```

Deliver the packet, end your turn.

### Step 2 — Re-entry

Validate that the four drafts are present. Pass to the user for approval; you commit after approval.

### Step 3 — User validation (non-delegable)

Tell the user:

> *"The scribe finished. Four drafts:*
>
> *1. activeContext entry: <paste>*
> *2. progress changes: <paste>*
> *3. New ADRs: <paste | 'no ADRs', with confidence>*
> *4. closure.md: <paste>*
>
> *Edit whatever the scribe misunderstood. When you are satisfied, approve; the orchestrator commits with prefix `docs(memory): close epic <id>`. Let me know when it's done."*

### Step 4 — Decision on new ADRs

If the scribe proposed new ADRs:

- **High confidence**: it typically deserves an ADR if it spans the epic. Pass to the user to expand it.
- **Medium confidence**: ask the user whether it's worth it.
- **Low confidence**: discard by default.

Heuristic: did the decision affect how several features were designed? Could someone 6-12 months from now ask "why was this epic built this way"? If yes → ADR. If no → discard.

ADRs that emerged during individual features **should already be** in `docs/adr/` (written in E5 of `cdad-cycle`). The epic scribe does NOT duplicate those; it only adds the ones that are specifically epic-level and not yet documented.

### Step 5 — Final closure

Once:

- Full CI green.
- The four drafts approved by the user and committed by the orchestrator.
- ADRs (if any) committed.

You merge the epic branch to main (or whatever the project's flow indicates). Strategy according to the project's convention.

## 🛑 Exit gate (E4 → epic done)

- [ ] Full CI green.
- [ ] `docs/epics/<id>/closure.md` exists with summary, retrospective, debt carried forward.
- [ ] `docs/activeContext.md` with the epic closure entry.
- [ ] `docs/progress.md` moved the epic to "done".
- [ ] New epic ADRs (if any) committed.
- [ ] Commit with prefix `docs(memory): close epic <id>` — approved by the user, executed by the orchestrator.
- [ ] Epic merged.

When all OK: update the state file:

```json
{
  "active_epic": null,
  "epic_stage": null,
  "epic_features": [],
  "epic_history": [..., {"stage": "epic-closure", "completed_at": "..."}]
}
```

And close:

> *"Epic `<id>` closed. <X features> delivered. Memory Bank consolidated. Next epic, next standalone feature, or do we call it a day?"*

## Structure of `closure.md`

Template in `assets/epic-closure-template.md`. Structure:

```markdown
# Epic <id> — Closure

Closed: <YYYY-MM-DD>

## Summary

<2-3 lines: what was delivered, against what problem>

## Features delivered

<list with id, name, individual closure date>

## Acceptance criteria

<each criterion from the plan + ✅ verified / ❌ not met (with reason)>

## Brief retrospective

### What worked well
<1-3 points>

### What got complicated
<1-3 points>

### Lessons for future epics
<1-3 points>

## Technical debt carried forward

<short list: things we decided not to do in this epic and why>

## Architectural decisions made

<list of ADRs created during the epic, with link>
```

Keep it short. One page, two at most. If the epic was small, a single "Summary" and "Debt" section is enough.

## Anti-patterns

- **EAP-3**: speculative ADRs at closure. Only ADRs documenting real decisions made during the epic. Not "we are going to use X in the future".
- **Exhaustive closure**: a 10-page closure does not get read. One page, two at most.
- **Skipping the closure** because "it's already merged". Without closure, in 6 months nobody remembers what was done and why. It is invisible debt.

## After closure

The epic is done. Back to the initial state: the user can start another epic, a standalone feature, or end the session.
