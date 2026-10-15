---
name: "odoo-reviewer"
description: >
  OCA checklist + current pylint-odoo catalog + mandatory/advisory split for
  the CDAD reviewer role on Odoo projects. Mapping of checks to the 5 review
  axes (correctness/readability/architecture/security/performance) and
  required evidence (make test-clean + pasted output + oca-checks). Use in
  stage 4 (Review) of any feature on an Odoo addon.
---

# odoo-reviewer — Odoo addon review (OCA + pylint-odoo)

> OCA standards (CONTRIBUTING.rst, pylint-odoo, oda-pre-commit-hooks,
> manifestoo) + official Odoo docs. Complements the generic CDAD reviewer
> (the 5 axes of the reviewer role); here is the Odoo-specific catalog.

## Basic checks per axis (mapping to the 5 axes of the generic reviewer)

| CDAD axis | Odoo checks |
|---|---|
| **Correctness** | ORM with no forbidden writes, correct `@api.depends`, pure `_compute`, `onchange` without persistence, no commits at runtime, no inheriting states without super |
| **Readability & Simplicity** | naming of records/fields, descriptive `_name` context, views without unnecessary duplicate view, clean manifest (author/version/format) |
| **Architecture** | module in its correct layer (model/view/controller/wizard/security), minimal and correct manifest `depends`, no hidden coupling between addons |
| **Security** | parameterized SQL (concatenation forbidden), `ir.rule`/groups in `security/`, justified `sudo()` commands, external requests with timeout |
| **Performance** | N+1 (searches inside loops), `search` without limit, redundant reads, inefficient compute methods |

## Current pylint-odoo catalog (key checks)

Catalog of `pylint-odoo` (verified rules; rule code → meaning).
The E/W/C prefix is severity (error/warning/convention). Only `E` checks
block in mandatory.

| Code | Rule | Meaning |
|---|---|---|
| **E8103** | sql-injection | SQL with `%`/`format` interpolating without parameters — injection risk (Security) |
| **E8102** | invalid-commit | `self.env.cr.commit()` in Odoo runtime (forbidden outside own transaction) |
| **E8135** | no-write-in-compute | write inside a `@api.depends`/`_compute` method — forbidden effects (Correctness) |
| **E8140** | no-raise-unlink | `raise` inside `unlink()` without context — deleting records with dependencies |
| **W8106** | method-required-super | method that requires calling `super()` and does not — broken inheritance |
| **E8106** | external-request-timeout | external HTTP request without `timeout` — risk of hanging the worker |
| **E8130** | test-folder-imported | the `tests` package is imported without a correct `__init__.py` |
| **C8102** | manifest-required-key | `__manifest__.py` missing a mandatory key (`license`, `category`, `version`, etc.) |
| **C8106** | manifest-version-format | manifest `version` not in the correct OCA semver format |
| **C8101** | manifest-required-author | missing `author` in the manifest |

## Mandatory / advisory split

The project's `.pylintrc-mandatory` **blocks only the `E` checks** (errors),
which must be at zero to approve the review. `W` (warnings) and `C`
(conventions) are **advisory**: they are reported and prioritized by
leverage, but do not block the merge on their own, except for explicit
documented exceptions. The review marks each finding as `mandatory`
(blocking, severity Required/Critical) or `advisory` (optional, severity
Optional/Nit/FYI).

Lint evidence is mandatory in the review:
- Output of `make lint --all` (`pre-commit-vauxoo`) pasted, with `0` blocking.
- Output of `pylint` pasted, with `0` `E` checks and the `W`/`C` listed.

## Required evidence (non-negotiable)

The review of an Odoo feature requires, in addition to the diff analysis:

1. **`make test-clean`** green — install-from-scratch gate with demo data,
   pasted output (`0 failed, 0 error(s) of N tests` line).
2. **oca-checks** with no findings — the OCA manifest checker (`oca-checks
   --manifest` / `--oca-addons-cfg`) returns 0 problems.
3. **pylint-odoo** with no blocking `E` (see catalog above), `W`/`C`
   documented as advisory.
4. **`make lint --all`** (`pre-commit-vauxoo`) with `0` blocking, pasted
   output; lint `W`/`C` findings are advisory per the mandatory/advisory
   split above.
5. Evidence is **pasted**, not described ("the suite is green" is not
   enough).

> Note: lint (`make lint`) is static and runs on the developer's machine
> (not in managed environments); the output travels with the review.

## Procedure

- Review the full diff with the checklist from the per-axis table.
- Verify the author's verification: `make test-clean` + pasted output +
  oca-checks + pylint with no E.
- Report each finding with location (file:lines), problem, suggestion (the
  move), severity, and whether it is mandatory/advisory.
- Close with "DONE. Summary: <X> blocking, <Y> optional."

## Anti-rationalizations (reject these)

| Rationalization | Reality |
|---|---|
| "The suite passes" | It does not catch sql-injection, bad view design, or malformed manifests. |
| "It's just a warning (W)" | A `W` can be a process gate or the signal of a latent bug; make it mandatory when the rule demands it. |
| "The code doesn't touch security" | A new field can open an `ir.rule` or an endpoint without groups. |
| "It's custom, OCA doesn't apply" | OCA standards apply to EVERY publishable addon, custom included. |
