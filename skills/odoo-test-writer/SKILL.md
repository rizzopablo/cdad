---
name: "odoo-test-writer"
description: >
  Odoo test framework for the CDAD test-writer role on Odoo projects.
  TransactionCase, mandatory @tagged, Form→web, freeze_time for dates,
  self-contained fixtures without demo data (OCA), make test-one for RED /
  make test for AUDIT, new_test_user for permissions, post_install for
  cross-module. Use in stage 3 (TDD) of any feature on an Odoo addon.
---

# odoo-test-writer — test framework in Odoo addons

> OCA rules + official Odoo docs (testing framework). The execution contract
> (`make test` / `make test-one` / `make test-clean`) lives in the
> `odoo-make-env` skill; here is the test content, not the runner.

## Test class: TransactionCase (the modern single class)

Use **`TransactionCase`** as the base class. It is the class recommended by
Odoo 17+ (tests run inside a transaction that is rolled back at the end, a
`SavepointCase` that does not create its own DB). Avoid unnecessary
fragmentation into several classes inherited from old margins; a single
TransactionCase class per file unless there is a real reason to group.

```python
from odoo.tests import TransactionCase, tagged

@tagged("cdad")
class TestIdeaLog(TransactionCase):
    ...
```

## `@tagged` is MANDATORY

Tests **without a tag do not run** in the suite under Odoo's standard
`--test-enable` (tags are the selection filter). Every test you want to run
must carry a `@tagged(...)` decorator with at least one tag. The tag also
allows selecting with `--test-tags` and marking `post_install`.

```python
@tagged("cdad")          # runs in the default suite
@tagged("post_install", "-at_install")  # runs after installing all addons (cross-module)
```

## `Form[...]->web`: the Form helper requires the `web` dependency

The `Form` object (UI mock for building records as a form) requires the
addon to declare the `web` module in `depends` of the `__manifest__.py`.
Without that dependency, `Form` is not available in the test environment.

```
Form[self.model_name]->web   # the iterator auto-sends in version 17+
```

In Odoo 17+ `Form` is an iterable that adds the record to the auto-send; the
construction is validated against `env["..."]` with `web` present.

## Dates: `freeze_time` (no real clock)

For assertions over dates, freeze the clock with `freeze_time` from
`odoo.tests` (wraps the test body with a fixed date) instead of depending on
the runner's real clock. This makes the test deterministic.

```python
from odoo.tests import freeze_time

def test_payment_date(self):
    with freeze_time("2026-01-15"):
        record.action_register()
        self.assertEqual(record.date, "2026-01-15")
```

## Self-contained fixtures — DEPENDENCE ON DEMO DATA FORBIDDEN

A test's fixtures must be **self-contained**: create the data the test needs
inside the test itself (partner records, products, etc.) **without depending
on the addon's demo data** or on pre-existing data. OCA rule: a test must
not assume that demo data is loaded or that a record "always exists". If the
module needs to create a partner, you create it in the setUp with
`env["res.partner"].create(...)`.

**Critical case — invoicing/accounting:** in Odoo 19 the CLI creates test
DBs WITHOUT demo data (`config.py:233`). Every test that invoices or touches
accounting configures its own journals/accounts (generic chart template) in
its fixture. Without this: it passes on the warm DB (journals from previous
stories) and fails on the gate's fresh DB with `UserError: No journal could
be found`, a failure that appears far from the cause.

## Location: addon's tests/ with __init__.py

- Tests live in the addon's `**/tests/`, each file with its `__init__.py`.
- The `tests/__init__.py` imports the test modules.
- The addon's `__init__.py` imports `tests` (or declares the package).
- One test file per area/case; names `test_<description>.py`.

## Runner: `make test-one` for RED, `make test` for AUDIT

- **RED** (new test that must fail): run ONLY that test with
  `make test-one TEST=mod:Class.method` and verify it fails for the right
  reason. Two valid forms of RED in Odoo (verified 2026-08-28):
  * Postcondition over existing behavior (method present, logic
    incomplete/changed) → fails with **AssertionError**.
  * New feature (the method does NOT exist yet) → fails with
    **AttributeError** (`'x.y' object has no attribute '...'`). This is also
    valid RED: the method genuinely is not implemented.
  * Invalid as RED: **ImportError** or module load error (indicates the
    test or `tests/__init__.py` is broken, not the feature).
- **AUDIT / full suite**: `make test` runs the whole suite on the warm DB.
- **Install gate**: `make test-clean` (or `test-all` in multi-module)
  installs from scratch on a fresh DB — the gate's only full run.
- Evidence = pasted output with the `0 failed, 0 error(s) of N tests` line.

**Run budget:** RED and iteration ONLY with `test-one` on the warm DB (full
suite = gate, not debugging). Anti-loop cycle: read the full failure →
written hypothesis → ONE change → ONE run; max 2 without convergence → STOP
and report. Full protocol:
`odoo-make-env/references/run-budget-protocol.md`.

## Property tests: N as calibration, not contract

The spec defines WHAT invariant (postcondition); the N of random scenarios
is a runtime budget, not semantics. Feature-cycle default: small (8-10),
with a **fixed seed** and explicit N as a file constant. Reducing N is
documented in the commit as calibration (never as weakening the test);
raising N belongs to hardening, without touching postconditions.

## Permissions: `new_test_user`

For tests that exercise **permissions/security**, create the test user with
`env["res.users"].new_test_user(...)` (Odoo 17+ helper) with the groups the
scenario requires, instead of real users or manual `_check_access` calls.
Verify that the user without the group fails (AccessError) and the one with
it passes.

```python
user = self.env["res.users"].new_test_user(login="operator", groups="base.group_user")
```

## Cross-module: `post_install`

When the test validates a **cross-module** flow (involves other addons
beyond the one under test), mark the test with `@tagged("post_install",
"-at_install")` so it runs after all the DB's addons are installed.

## Anti-patterns to avoid

- Test that depends on demo data or assumed records (breaks in `test-clean`).
- Test without `@tagged` (never runs in the suite).
- Using `Form` in an addon that does not declare `web` (ImportError at runtime).
- Dates dependent on the runner's real clock.
- `pass` or asserts that verify nothing (a test that is not an oracle).
