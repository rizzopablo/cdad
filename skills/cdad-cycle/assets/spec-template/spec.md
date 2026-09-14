---
feature_id: <NNN-feature-id>
feature_name: <short name>
created_at: <YYYY-MM-DD>
approved_by: <pending>
approved_at: <pending>
---

# Spec: <feature name>

## Functional description

<Description in language close to the end user. What the feature does, what it is for, in what context it is used. 2-5 lines.>

## Contract (signature and invariants)

**Signature:**

```<language>
<signature of the function / method / endpoint, with types>
```

**Postconditions (numbered and verifiable):**

1. <If <valid input>, returns <expected output with specific properties>.>
2. <If <error case>, throws/returns <specific behavior>.>
3. <...>

## Verifiable invariants

<Properties that hold for every valid input. Basis for property tests. If the feature has no clear invariants, delete this section.>

- ∀ <variable> valid: <property>
- <...>

## Acceptance criteria

<Measurable metrics, not vague adjectives.>

- [ ] Unit test for each postcondition passes.
- [ ] Line coverage in `<main file>` ≥ <X>%.
- [ ] Property test with <N> random inputs passes.
- [ ] <E2E test if applicable: description of the full flow>.

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
