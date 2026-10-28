---
feature_id: <NNN-feature-id>
feature_name: <short name>
created_at: <YYYY-MM-DD>
approved_by: <pending>
approved_at: <pending>
---

# Spec: <feature name>

This spec opens with the functional description derived from a **user journey**, not with a code block.

From a legitimate starting point, the actor pursues a goal and obtains a first useful result:

**User journey**

- **Actor**: <who walks the journey, and in what role>.
- **Goal**: <what the actor wants to obtain, in the actor's own words>.
- **Legitimate starting point**: <the legitimate resting state the actor starts from; what already exists and works>.
- **First useful result**: <the first useful result the actor obtains; what the actor can now do>.

<2-5 lines, in language close to the end user, describing what the feature does and in what context it is used, derived from the journey above.>

## Acceptance criteria (observable behavior over the journey)

<Measurable, observable behavior over the journey above — what an observer can see at the end of it, not internal structure and not a threshold on internal quality.>

- [ ] From its legitimate starting point, the <actor> completes the journey and obtains the <first useful result>, observable as <what can be seen or measured>.
- [ ] <Main-path behavior: the observable outcome 2 of the journey>.
- [ ] <Recovery behavior: if <observable failure case> happens, the actor observes <observable recovery outcome> instead of a silent failure>.

## Contract (promises, postconditions and invariants)

**Promises (observable, one per user-visible guarantee):** group the numbered
postconditions by the **observable promise** they serve — the promise is what the
user can see, and its postconditions are the parts of that promise you commit to
verify. Equivalent scenarios with the same observable result are ONE
postcondition, never a quota of variants; distinct committed behaviours still get
the postconditions they need (R1 — `sources/roles/architect.md`).

| Promise | What the user can see | Postconditions |
| --- | --- | --- |
| A — <promise> | <observable result the user perceives> | PC-1, PC-2 |
| B — <promise> | <observable result the user perceives> | PC-3 |

**Postconditions (numbered and verifiable; each belongs to exactly one promise above):**

1. <PC-1: if <valid input>, returns <expected output with specific properties>.>
2. <PC-2: if <error case>, throws/returns <specific behavior>.>
3. <...>

**Signature (supporting detail for the implementer; never the opening block):**

```<language>
<signature of the function / method / endpoint, with types>
```

**Verifiable invariants**

<Properties that hold for every valid input. Basis for property tests. If the feature has no clear invariants, delete this section.>

- ∀ <variable> valid: <property>
- <...>

## deferred-hardening

What you decided NOT to verify or harden, each with its reason. `None` means
there is none — never "we did not think about it". No item here postpones a
committed promise, and none relaxes security, integrity or data preservation:
the acceptance counterweight is R7
(`skills/cdad-cycle/references/stage-3-tdd.md`).

- <deferred item> — reason: <why it is deferred>; what would promote it: <trigger>.

## Out of scope

<What the feature does NOT do, to avoid scope creep.>

- <Case 1 explicitly out>
- <Case 2>

## Implementation notes (optional)

<Technical decisions made during the brainstorm that clarify the how without imposing it. Trade-offs, discarded alternatives, etc. can go here.>

## Technical context

<Output of the per-feature discovery: which APIs/hooks/modules it touches, specific conventions that apply, known gotchas.>

---

Status: <Pending approval | Approved by <name> on <YYYY-MM-DD>>
