---
epic_id: <NNN-epic-id>
epic_name: <short name>
created_at: <YYYY-MM-DD>
approved_by: <pending>
approved_at: <pending>
---

<!-- 005-013 PD-3: product anchor declaration. `history` = the plan change log
     (its sections are EXCLUDED from the unit projection); `authorization` = the
     epic authority section (INCLUDED as a shared part, no verdict effect). The
     declaration lists the English title of this template and the Spanish form of
     the product's plans; a `##` section is the anchor when its normalized title
     equals the declared title or starts with it followed by a non-alphanumeric
     separator. -->
<!-- cdad:plan-anchors
{"history": ["Plan changes", "Cambios al plan"], "authorization": ["Stakeholders", "Autoridad"]}
-->

# Epic <NNN>: <name>

## Summary

<2-3 lines: what problem it solves, what is delivered when it is done.>

## Scope

**In scope:**
- <point 1>
- <point 2>

**Out of scope:**
- <point 1>
- <point 2>

## Decomposition into features

| # | Feature ID | Description (1 line) | Dependencies | Parallelizable |
|---|-----------|------------------------|--------------|---------------|
| 1 | <epic-num>-001-<slug> | <description> | — | Yes |
| 2 | <epic-num>-002-<slug> | <description> | 001 | No |
| 3 | <epic-num>-003-<slug> | <description> | 002 | No |

## Cross-feature contracts

<If applicable: interfaces shared between features. Keep minimal, signatures only.>

```<language>
<signature of the shared contract>
```

Used by: <list of features>.

<Or delete this section if it does not apply.>

## Epic acceptance criteria

<Measurable, covering the complete cross-feature flow.>

- [ ] The <N> features are done individually.
- [ ] Cross-feature E2E test: <description of the main flow>. Passes.
- [ ] Failure E2E test: <description of the error path>. Passes.
- [ ] <Other epic-specific criteria>.

## Risks / expected debt

<Optional. Risks identified while planning, planned mitigations, debt that is known will remain.>

- Risk: <...>. Mitigation: <...>.
- Expected debt: <...>.

<Or delete this section if it does not apply.>

## Stakeholders

- **Epic plan approver**: <name>
- **Feature spec approver**: <name>
- **Result operator**: <name>

## Plan changes

<Section updated during the feature loop if the plan changes. Initially empty.>

<!-- Example entry:
### YYYY-MM-DD — Split feature 003
Reason: during implementation we detected that enviar-ws has two responsibilities that are worth separating.
Change: feature 003 is split into 003a (submission) and 003b (synchronous response handling).
-->

---

Status: <Pending approval | Approved by <name> on <YYYY-MM-DD>>
