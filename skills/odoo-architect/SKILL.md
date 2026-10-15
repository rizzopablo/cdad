---
name: "odoo-architect"
description: >
  Implementation guide for Odoo projects for the CDAD architect role.
  GAP Analysis→Kick-Off→Implementation→Go-Live phase model (with effort
  weights), PL/SPoC/Developer roles, the "configuration first, custom only
  with a justified gap" principle, OCA/core module inventory before
  specifying, and the Discovery output format (process→module mapping). Use
  in stages 1 (Discovery) and 2 (Spec) of any feature on an Odoo project.
---

# odoo-architect — Odoo project implementation methodology

> Source: the implementation methodology published by Odoo
> (PDF accessible via https://www.odoo.com/web/content/17936384).
> The consulting phase model and the PL/SPoC/Developer roles are the frame of
> reference of that document. The effort PERCENTAGES per phase are a
> HEURISTIC of this skill — indicative weights, not part of the cited
> document. The technical foundation is standard Odoo implementation practice
> demanded by the industry and verified in OCA/core; cite the document as
> reference when justifying the state of an implementation.

## Automatic detection (`stack: odoo`)

This skill is the Odoo specialization of CDAD (see `cdad-cycle` §3.1 and
`references/bootstrap.md` Step 2b, in the generic skill). A project is a
candidate for `stack: odoo` when there is objective evidence in the repo:

- there is at least one `__manifest__.py` (unambiguous marker of an Odoo module), or
- `docs/projectbrief.md` or the user's initial specification mentions
  "Odoo", "module"/"addon" in that sense, or a framework from another
  domain (Django, Rails…) does not appear.

With clear evidence, bootstrap sets `stack: odoo` without asking. With
ambiguity, it is a question to the user (if one is present) — never an
assumption.

## Before advancing to Stage 2 (Spec): is there something to run tests on?

Stage 1 (Discovery) should not close without knowing this — if it is only
discovered in Stage 3 (TDD), the feature already has an approved spec and the
problem blocks later and more expensively.

Load the `odoo-make-env` skill and follow its environment detection
procedure **once, at the start of the project** (not per feature). If no
execution environment has been resolved yet, it is an issue to settle before
closing Discovery, not a surprise in TDD.

## Guiding principle

**"Configuration first; custom only with a justified gap."** The rule of
Odoo implementation is to solve the process with native configuration
(standard apps, fields, views, access rights) and to resort to custom
development (own modules) only when the requirement cannot be satisfied in a
maintainable way with out-of-the-box functionality. A "gap" is a requirement
that native configuration does not cover and that the process owner accepts
as necessary — not a default desire to "let's do it custom".

## Phase model (implementation project)

The implementation follows an iterative phase model, with effort weights
that orient the plan. The weights are a HEURISTIC (indicative, not part of
the cited document): the exact distribution depends on the client's scope
and maturity.

| Phase | Focus | Effort (indicative weight) |
|---|---|---|
| **GAP Analysis** | Map the current processes, identify the gap between what the business does and what Odoo covers by configuration; inventory of candidate OCA/core modules | 25% |
| **Kick-Off** | Align stakeholders, define scope, phase plan, owners (PL/SPoC/Developer), schedule and acceptance criteria | 5% |
| **Implementation** | Configuration first + custom (gaps only); development in cycles with continuous testing (CDAD make contract) | 55% |
| **Go-Live** | Data migration/loading, training, cutover, post-implementation support and final acceptance | 15% |

## Project roles

- **PL (Project Lead)** — responsible for the plan, scope, schedule and the
  relationship with the process owner; decides (with the SPoC) what is
  configuration and what is a gap.
- **SPoC (Single Point of Contact)** — the single channel between the
  project and the client/business; consolidates requirements and validates
  that the solution matches the real process.
- **Developer** — implements the configuration and the authorized custom
  work (gaps only), keeping the (make) test contract and OCA standards.

## Module inventory BEFORE specifying

Before describing the contracts of an Odoo feature, complete the **module
inventory**: which Odoo *core* apps and which **OCA** (Open Community
Association) modules cover (partially or fully) the process/movement the
feature touches. The recommendation is to reuse an existing OCA/core module
before specifying new custom work — document the discard when applicable
(`VERIFY` if you cannot confirm the exact module). The inventory goes to
the "Technical context" section of the spec.

## Discovery output format (process→module mapping)

The Discovery of an Odoo feature delivers a **process→module** mapping: which
business process (or flow) the feature represents and which modules
(core/OCA) materialize it, with their state (already exists / extend / create
custom due to gap).

Output format:

```markdown
## Process → module mapping
- Process: <name of the process/flow>
  - Core module: <app.core / none>
  - OCA module: <odoo/community-addons: name | none>
  - Custom module: <needed only if gap justified | no>
  - Justified gap: <yes, because <reason> | no>
## Models/entities touched
<...>
## Hooks/extension points available
<...>
## Applicable conventions
<...>
## Pending verifications
<...>
```

## Socratic question frame (Odoo-specific)

In the brainstorm, in addition to inputs/outputs/errors/permissions, ask:
- Is the requirement covered by **configuration** (rights, views, demo
  data, standard fields) or does it demand **custom**?
- Is there an **OCA/core** module that already solves it?
- Which **SPoC** validates the business logic? And which **PL** defines the
  scope?
- Is the gap **justified** by the process owner, or is it a "custom by
  default"?

## Anti-patterns to avoid

- Specifying custom without having done the OCA/core inventory.
- Skipping the "configuration first" judgment and going straight to
  development.
- Confusing roles: the PL defines scope, the SPoC validates business, the
  Developer implements only what is authorized.
