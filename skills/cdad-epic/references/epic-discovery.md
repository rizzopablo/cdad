# Stage E1 — Epic discovery

Map the domain of the whole epic. It is light: identify which functional areas it touches, not exhaustive.

## Your role

You coordinate. You do not do the discovery yourself, nor do you issue a handoff to a specific role. This stage is **you + user (human or the agent owning the process)** directly, just like the project's initial discovery in `cdad-cycle`.

## Why it is light

The epic already has a defined scope. The difference with feature discovery is that you touch multiple functional areas that have to be coordinated. What you need to establish:

1. **Clear scope**: what goes into the epic and what does not.
2. **Functional areas**: which modules/domains of the system it touches.
3. **External dependencies**: APIs, services, libraries, integrations the epic requires.
4. **Constraints**: regulatory, performance, compatibility, hard deadlines.
5. **Stakeholders**: who approves, who will use the result.

## Steps

### Step 1 — Confirm start

If the user says "let's start epic X", confirm it is new work:

> *"We are going to start epic `<X>`. I will ask you a few questions to map the scope, without getting into design yet. OK?"*

### Step 2 — Ask the questions

One to three questions per turn, waiting for answers. Cover:

**About scope:**
- What is the problem the epic solves, in one sentence?
- What result do you expect when the epic is done?
- What deliberately does NOT go into this epic? (initial out of scope)

**About functional areas:**
- Which modules or areas of the system does it touch?
- Are there new areas to create (new modules, new subdomains)?

**About dependencies:**
- Are there external APIs? Third-party services?
- Are there new libraries you will have to evaluate/choose?
- Is there pre-existing data to migrate or consume?

**About constraints:**
- Are there deadlines? Commitments with third parties?
- Regulatory constraints (compliance, audit)?
- Expected performance? Anticipated load?

**About stakeholders:**
- Who approves the epic plan?
- Who will use/operate the result?

You do not run a questionnaire. Three to five concrete questions and you move forward. If something important comes up on the user's side, you capture it.

### Step 3 — Capture in `docs/epics/<id>/discovery-notes.md` (optional)

For small epics this can be part of `plan.md` directly. For larger epics, it is worth having separate notes that are later condensed into the plan.

If you opt for a separate file:

```markdown
# Epic <id> — Discovery Notes

## Problem
<one sentence>

## Expected result
<what changes when it is done>

## Functional areas touched
<list>

## External dependencies
<list>

## Constraints
<list>

## Stakeholders
<list>

## Initial out of scope
<list>
```

If you opt to capture directly in `plan.md`, skip this file and build the plan in E2.

### Step 4 — Close the stage

When you have answers to the questions and the user confirms the scope is clear:

> *"Epic discovery closed. We have: <1-2 line summary>. Shall we move to planning to define the features that compose it?"*

## 🛑 Exit gate (E1 → E2)

- [ ] Epic scope clear: what's in, what's out.
- [ ] Functional areas identified.
- [ ] External dependencies known.
- [ ] Constraints documented.
- [ ] Plan approver identified.

If all OK: update the state file (`epic_stage: epic-planning`). Load `references/epic-planning.md`.

## Anti-patterns

- **EAP-1**: discovery turns into an exhaustive plan. Here you do NOT define features yet. That is E2. If the user starts listing features in detail, stop them and save the list for E2.
- **Avoid paralyzing analysis**: epic discovery is light. If you don't have an answer to a question, mark it as "VERIFY in feature N" and move forward. Some constraints are discovered while implementing, not while planning.
