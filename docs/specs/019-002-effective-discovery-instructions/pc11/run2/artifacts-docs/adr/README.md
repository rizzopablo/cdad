# Architecture Decision Records (ADR)

The project's architectural decisions. Immutable once accepted.

## When to create an ADR

If within 6 months, someone (you or an agent) could ask **"why did we do X this way?"**, that decision deserves an ADR.

Typical examples:

- Choice of database.
- Architecture decision (monolith vs services, layering, bounded contexts).
- Choice of a main library when there were alternatives.
- Patterns that are deliberately forbidden.

## When NOT to create an ADR

- Local implementation decisions (which algorithm to use inside a function).
- General project conventions (they go to `systemPatterns.md`).
- Current state or work in progress (it goes to `activeContext.md`).

## Numbering and format

`ADR-NNN-title-in-kebab-case.md`. Sequential numbering.

Template in `<skill>/assets/adr-template/ADR.md`.

## Possible states

- **Proposed**: under discussion.
- **Accepted**: approved, in force.
- **Deprecated**: no longer applies but was not replaced.
- **Superseded by ADR-NNN**: replaced by another ADR.

Once **Accepted**, an ADR is not modified. If the decision changes, a new ADR is created that `supersede`s the previous one.
