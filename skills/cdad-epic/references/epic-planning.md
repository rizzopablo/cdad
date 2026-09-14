# Stage E2 — Epic planning (light)

Produce a short `plan.md` with the decomposition into features, cross-feature contracts, and the epic's acceptance criteria. Output approved by the user (human or a higher-hierarchy autonomous agent).

## Your role

You coordinate. You draft the plan based on the discovery + your questions; the user (human or a higher-hierarchy autonomous agent) approves; the orchestrator commits the plan.

## Light philosophy (reminder)

- Plan of 1-3 pages.
- List of features with order and dependencies, not a detailed specification of each one (that is the feature's work in `cdad-cycle`).
- Cross-feature contracts only for interfaces shared by several features.
- No speculative ADRs. ADRs emerge feature by feature when they are needed.
- No formal RFC or heavy governance.

If the plan exceeds 3 pages and it is not because the epic is genuinely large (10+ features), it is heavy.

## Steps

### Step 1 — Decomposition into features

Conversation with the user. You do not issue a handoff to a role; you do it yourself + user (human or the agent owning the process) directly, similar to the Socratic brainstorm in `cdad-cycle`.

Ask questions:

- What functional units are you going to deliver? (each one is a feature)
- In what order do they make sense?
- Which ones depend on which?
- Which ones could be done in parallel?

You capture the decomposition as a table:

| # | Feature | Description (1 line) | Dependencies | Parallelizable |
|---|---------|-----------------------|--------------|---------------|
| 001 | validar-cuit | CUIT format validator with check digit | — | Yes |
| 002 | generar-xml | Generation of the AFIP XML from an invoice object | 001 | No |
| 003 | enviar-ws | Submission to the AFIP webservice with timeout handling | 002 | No |
| 004 | cola-reintentos | Persistent queue to retry failed submissions | 003 | No |
| 005 | respuestas | Parsing of AFIP responses and mapping to states | 003 | With 004 |

Naming: each feature uses the prefix `<epic-num>-<feat-num>-<slug>`. E.g.: `001-002-generar-xml`.

### Step 2 — Identify cross-feature contracts

If there are interfaces shared between features (e.g. an `Invoice` class that three features manipulate), document the minimal signatures. NOT the implementation detail, only the contract:

> *"Contract `Invoice`: dataclass with fields cuit (str), date (date), items (list[Item]), total (Decimal). Used by: 002, 003, 004."*

If there are NO evident cross-feature contracts (each feature is independent with its own interfaces), you skip this section.

### Step 3 — Acceptance criteria for the complete epic

Measurable criteria, just like in feature specs, but about the epic:

> *"The epic is done when:*
> *1. The 5 features are done individually (each one with its Stage 5 gate closed).*
> *2. Cross-feature E2E test: given a valid invoice, XML is generated, sent to the testing WS, a response is received, and state is persisted. Passes.*
> *3. Failure E2E test: given a failed submission, the retry queue picks it up and retries until success or timeout. Passes.*
> *4. Coverage of the `facturacion/` module ≥ 90%."*

### Step 4 — Risks and expected technical debt (optional, brief)

A short section:

> *"Risks: the AFIP WS latency in production can be variable; mitigation: configurable timeouts.*
> *Expected debt: the XML generation uses lxml; if the team prefers stdlib, consider a refactor in a later epic."*

If you have nothing relevant, omit this section.

### Step 5 — Produce `plan.md`

Load `assets/epic-plan-template.md` and fill it in with what was worked out. Minimum structure:

```markdown
# Epic <id>: <name>

## Summary
<1-3 lines: problem, result>

## Scope
- In: <list>
- Out: <list>

## Decomposition
<table of features with order and dependencies>

## Cross-feature contracts
<if applicable>

## Epic acceptance criteria
<measurable list>

## Risks / expected debt
<if applicable>

## Stakeholders
- Plan approver: <name>
- Feature spec approver: <name>
- Result operator: <name>

---

Status: <Pending approval | Approved by <X> on <YYYY-MM-DD>>
```

### Step 6 — User approval (non-delegable)

> *"Plan in `docs/epics/<id>/plan.md`. Review it: (a) decomposition correct and complete, (b) order and dependencies well defined, (c) measurable acceptance criteria. If it's OK, add the approval mark at the end. Let me know when it's done."*

**If the user asks you to approve it**: you politely decline.

> *"Plan approval requires your judgment on priorities and delivery commitment. I can propose changes if you want, but the mark goes with your name."*

## 🛑 Exit gate (E2 → Feature loop)

- [ ] `docs/epics/<epic-id>/plan.md` exists.
- [ ] Plan contains: scope, decomposition with order and dependencies, measurable acceptance criteria.
- [ ] Unambiguous user approval mark.
- [ ] State file updated with `epic_features` (list derived from the decomposition).

When all OK: update the state (`epic_stage: features-loop`, populate `epic_features` from the plan). Announce the transition. Load `references/feature-handoff.md` to prepare the delegation to `cdad-cycle` for the first feature.

## Anti-patterns

- **EAP-1**: kilometer-long plan that never closes. If you've spent more than 90 minutes planning, the plan is heavy: cut where you are, mark the rest as TBD to be defined when the corresponding features start.
- **EAP-2**: each feature in the plan has its mini-spec inside. That duplicates `cdad-cycle`'s work. In the plan: a 1-line description per feature. The real spec is done when the feature is started.
- **EAP-3**: speculative ADRs in the plan. If the plan has an "Architectural decisions" section, it is probably overkill. ADRs emerge feature by feature.

## If the plan needs to be updated during the feature loop

It is expected. As features are implemented, new info appears: the optimal order changes, some feature gets subdivided, another is dropped, a new one emerges.

When that happens: update `plan.md`, record the change in a "Plan changes" section with date and reason, and commit:

```
docs(epic): update plan — split feature 003 into 003a/003b

Reason: during implementation we detected that enviar-ws has 
two distinct responsibilities that are worth separating.
```

It does NOT require formal re-approval unless the change modifies the epic's scope or acceptance criteria. If it does, then yes: user re-approval.
