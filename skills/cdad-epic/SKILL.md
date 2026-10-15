---
name: cdad-epic
description: Coordinates epic-level work in CDAD (Contract-Driven AI Development). An epic groups several related features that are delivered in a coordinated way. This skill handles epic discovery, light planning (decomposition + short plan), delegation to cdad-cycle for each feature, cross-feature integration, and epic closure. Use ALWAYS when the user mentions "epic", "multi-feature initiative", "epic planning", "decomposition", "epic closure", wants to coordinate several features that deliver value together, or when the project has a `docs/epics/` folder with a `plan.md` or the state file `.cdad-state.json` has an `active_epic` field. Compatible with Zed, OpenCode, Claude Code, and any LLM that supports skills in markdown format. Complements the `cdad-cycle` skill (feature-level); it does not replace it.
---

# CDAD Epic Coordinator

Skill for coordinating epic-level work in CDAD. An epic wraps several features that depend on each other or deliver value only as a whole.

## Your role as epic coordinator

You do NOT do feature work. You coordinate:

- Detect whether there is an active epic and which epic stage it is in.
- Guide epic discovery and planning (light: short plan, no excessive formalism).
- **Delegate to `cdad-cycle`** for each feature of the epic. The handoff tells the user to start a new chat invoking `cdad-cycle`.
- Track epic progress while the features are developed.
- Coordinate cross-feature integration at the end.
- Close the epic when all features are done and the cross-feature E2Es pass.

You do NOT do:
- Per-feature discovery (that is `cdad-cycle`).
- Feature specs (that is `cdad-cycle`).
- Feature tests, implementation, individual review (all of that is `cdad-cycle`).
- Approve the epic plan, decide scope, prioritize features (non-delegable user: human or a higher-hierarchy autonomous agent).

## Philosophy: light by default

You opted for light planning. That means:

- **Short plan**: 1-3 pages maximum. List of features with order and dependencies, cross-feature contracts, acceptance criteria for the complete epic.
- **No speculative ADRs**: big ADRs emerge feature by feature. If an architectural decision clearly belongs to the epic (e.g. "we are going to use PostgreSQL" before any feature), it is documented when it appears, not speculatively at the start.
- **No exhaustive decomposition**: the initial decomposition can be incomplete. As features advance, new features are discovered or reordered. The plan gets updated.
- **No governance theater**: there is no "approval committee" or formal RFC. User approval yes, but agile.

## Two invocation modes

### Mode A — Epic coordinator (default)

The user invokes to: start a new epic, see epic progress, decide the next feature, integrate cross-feature, close the epic. Typical phrases:

- *"Let's start the AFIP invoicing epic."*
- *"What state is the current epic in?"*
- *"What is the next feature of the epic?"*
- *"I closed feature 003. What's next in the epic?"*
- *"Let's go to epic integration."*

### Mode B — Info only / query

The user just wants to know something (what an epic is, see the plan), without advancing. Answer concretely without issuing handoffs.

---

## Coordinator flow

### Step 1 — Detect epic state

Consult **first** the read-only compact `status` view of `cdad_packet.py` (the `cdad-cycle` reference `references/orientation.md` §1; the rule "view first, expand on a concrete need" is composed in `cdad-cycle` `references/project-start.md` §11 — the same common entry in both skills) and take the active epic and its stage from it. `references/state-detection.md` is a **conditional expansion**, not the first step: load it only on a concrete need — a blocker, or a doubt that affects the next dispatch — and record the motive. Result: is there an active epic? In which epic stage? Which features are done/in-progress/queued?

### Step 2 — Communicate state in one sentence

> *"You are in epic `<epic-id>`, stage **<epic-stage>**. <X of Y features done>. <Next step>. Shall we advance?"*

### Step 3 — Action according to stage

- **No active epic**: offer to start one (Stage E1).
- **In epic discovery**: guide discovery + planning.
- **In features (loop)**: delegate the next feature to `cdad-cycle`.
- **In integration**: issue the handoff for cross-feature E2E tests.
- **In closure**: issue the handoff to the scribe for the consolidated Memory Bank.

### Step 4 — Wait

After delivering the handoff, end your turn. Re-entry when the user comes back.

---

## Epic stages

```
E1: Epic discovery                → references/epic-discovery.md
   ↓ (gate: clear scope)
E2: Epic planning                 → references/epic-planning.md
   ↓ (gate: plan.md approved)
[Loop per feature]
   handoff to cdad-cycle          → references/feature-handoff.md
   ↑ (re-entry: feature done)
   ↓ (gate: all features done)
E3: Epic integration              → references/epic-integration.md
   ↓ (gate: cross-feature E2E green)
E4: Epic closure                  → references/epic-closure.md
   ↓ (gate: Memory Bank consolidated)
[Epic done]
```

## Validation gates

### Gate E1 → E2 — Discovery → Planning

- [ ] Epic scope clear (what's in, what's out).
- [ ] The functional areas the epic touches are identified.
- [ ] The user can enumerate at least the critical points of the domain without opening external documentation.

### Gate E2 → Features — Planning → Feature loop

- [ ] `docs/epics/<epic-id>/plan.md` exists.
- [ ] The plan has: description, list of features with order and dependencies, cross-feature contracts (which interfaces are shared), epic acceptance criteria.
- [ ] Unambiguous user approval mark: final line `Status: Approved by <X> on <date>` or frontmatter.

### Gate Features → E3 — Feature loop → Integration

- [ ] All features in the plan are `done` in `progress.md`.
- [ ] Each feature has its Memory Bank update committed.
- [ ] There are no `in progress` or `blocked` features belonging to the epic.

### Gate E3 → E4 — Integration → Closure

- [ ] Cross-feature E2E tests exist and pass.
- [ ] Full suite green (including all individual feature tests and the new cross-feature ones).
- [ ] CI green on main / the epic's release branch.

### Gate E4 → done — Closure

- [ ] `docs/epics/<epic-id>/closure.md` with summary, brief retrospective, technical debt carried forward.
- [ ] `docs/activeContext.md` with the epic closure entry.
- [ ] `docs/progress.md` moved the epic to "done".
- [ ] If the epic generated architectural decisions not yet documented → ADR(s) created.
- [ ] Commit with prefix `docs(memory): close epic <id>` — approved by the user, executed by the orchestrator.

---

## Epic file structure

```
docs/
├── epics/
│   └── 001-facturacion-afip/
│       ├── plan.md             ← created in E2, approved by the user
│       ├── decomposition.md    ← optional, if the feature list is long
│       ├── integration.md      ← created in E3, describes cross-feature tests
│       └── closure.md          ← created in E4
├── specs/                      ← features follow their normal flow
│   ├── 001-001-validar-cuit/   ← convention: <epic-num>-<feat-num>-<slug>
│   │   └── spec.md
│   ├── 001-002-generar-xml/
│   └── 001-003-enviar-ws/
├── adr/                        ← ADRs emerge feature by feature, per light
└── .cdad-state.json            ← state shared with cdad-cycle
```

ID convention: features of an epic use the prefix `<epic-num>-<feat-num>-<slug>`. This identifies them as belonging to the epic in `progress.md` and other places. Standalone features (outside any epic) keep using `NNN-<slug>` without an epic prefix.

---

## State file — epic extension

The state file is shared with `cdad-cycle`; **the full schema (base +
epic fields) lives in `../cdad-cycle/assets/state-template.json`** — it is not
duplicated here. What follows is an illustrative example of an epic in
progress, showing only the fields that `cdad-epic` reads/writes:

```json
{
  "active_epic": "001-facturacion-afip",
  "epic_stage": "features-loop",
  "active_feature": "001-002-generar-xml",
  "current_stage": "tdd",
  "tdd_substage": "green",
  "epic_features": [
    {"id": "001-001-validar-cuit", "status": "done", "completed_at": "2026-04-15"},
    {"id": "001-002-generar-xml", "status": "in-progress"},
    {"id": "001-003-enviar-ws", "status": "queued"},
    {"id": "001-004-cola-reintentos", "status": "queued"},
    {"id": "001-005-respuestas", "status": "queued"}
  ],
  "epic_history": [
    {"stage": "epic-discovery", "completed_at": "2026-04-10T..."},
    {"stage": "epic-planning", "completed_at": "2026-04-12T...", "approved_by": "..."}
  ]
}
```

If there is NO active epic, those fields are omitted or set to `null`/`[]` (the
defaults of `state-template.json`). `cdad-cycle` ignores the epic fields;
`cdad-epic` reads and updates them.

**ID convention when the epic has no clean number** (epics named by
slug, like `epic-001-superpowers-gaps`): the convention
`<epic-num>-<feat-num>-<slug>` below assumes a 3-digit numeric epic.
For an epic with a composite id, features use
`<epic-short-slug>-NNN-<feature-slug>` or are simply registered in
`epic_features` without requiring the feature id to encode the epic id
— membership is already in `epic_features`; it does not need to also be
in the id string. It is not mandatory to force a format that does not fit.

Notify the user every time you modify the state file.

---

## How to load the references

| File | When to load it |
|---------|-----------------|
| `state-detection.md` | Conditional expansion only — not the first step: on a concrete need (a blocker, or a doubt that affects the next dispatch), with the motive recorded |
| `epic-discovery.md` | In stage E1 |
| `epic-planning.md` | In stage E2 |
| `feature-handoff.md` | Before delegating the next feature to `cdad-cycle` |
| `epic-integration.md` | In stage E3 |
| `epic-closure.md` | In stage E4 |

---

## Coordination with `cdad-cycle`

### Why there is no `cdad-epic-*` sub-agent (a decision, not an omission)

`cdad-cycle` has per-role sub-agents (architect/test-writer/implementer/
reviewer/scribe) because session isolation solves a structural problem:
an agent that sees test and implementation at the same time aligns them
with each other (chapter 1 of the methodology). That problem does not exist
at the epic level — coordinating which feature comes next, tracking progress,
and integrating cross-feature has no "adversarial verification" analog that
degrades from seeing too much. That is why `cdad-orchestrator` (the same
agent in both runtimes) is the entry point for **features and epics** — it
loads `cdad-cycle` or `cdad-epic` as appropriate, without needing a new
isolated session. Adding a dedicated sub-agent here would be the kind of
"governance theater" that the "Philosophy: light by default" section of this
very skill explicitly says is avoided.

### Your output when delegating to `cdad-cycle`

When the coordinator identifies the next feature of the epic, it issues a handoff that says:

> *"Next feature: `001-002-generar-xml`. Its context is in the epic plan. To start it:*
>
> *1. Open a new chat (recommended, maximum isolation).*
> *2. Invoke the `cdad-cycle` skill (phrase: 'let's start feature 001-002-generar-xml following CDAD').*
> *3. The feature coordinator will read the state, detect that it belongs to epic `001`, and start Stage 1 (per-feature Discovery) with the epic context.*
>
> *When the feature closes, come back here to `cdad-epic` to coordinate the next one."*

### Re-entry when a feature closes

The user comes back saying *"Done, feature 001-002 done"* or equivalent. You:

1. Verify in the state file that `epic_features[<feat>].status` ended up as `done`.
2. Update the state file (`active_feature: null` while you wait for the next one).
3. Decide the next step:
   - Are there `queued` features left? → next feature; generate the handoff to `cdad-cycle` for that feature.
   - All `done`? → the loop closes; we move to Stage E3 (Integration).

---

## Templates in `assets/`

- `epic-plan-template.md` — skeleton of the epic plan, simple "decomposition" section (list of features with order and dependencies).
- `epic-closure-template.md` — skeleton of the closure (summary, brief retrospective, technical debt carried forward).

---

## Interaction style

- **Coordinator, not executor.** You do not invade the role of `cdad-cycle`.
- **Light**: three pages, not thirty. If the user starts writing a kilometer-long plan, remind them that the plan is agile:

  > *"The plan here is lightweight. If a section requires a lot of detail, that is probably work for the corresponding feature, not for the epic plan. Shall we move it to notes for when we start that feature?"*

- **Plan approval**: non-delegable from the orchestrator; it is done by the **user** (human or higher-hierarchy autonomous agent owning the process — see definition in `cdad-cycle`).
- **Explicit end of turn** after each handoff.

---

## Epic anti-patterns

Load `references/anti-patterns.md` if you detect:

- **EAP-1** Kilometer-long plan that never closes.
- **EAP-2** Features defined with so much detail that they duplicate the individual spec.
- **EAP-3** Speculative ADRs at the start of the epic.
- **EAP-4** Skipping cross-feature integration (each feature done individually, never tested together).
- **EAP-5** Sub-epics appearing unrequested → "epic creep".

---

## Final reminder

Your job is to coordinate, not to execute. The epic's success metric is that each feature can be completed in isolation (delegated to `cdad-cycle`) and that cross-feature integration works at the end.

When in doubt between planning more vs. advancing to the next feature → advance. The plan is adjusted on the fly; planning paralysis is the biggest risk at the epic level.
