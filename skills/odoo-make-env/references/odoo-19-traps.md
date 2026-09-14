# Odoo 19 API traps (verified 2026-08-28)

Empirical findings from the Odoo specialization, verified in real
environments (odoo.sh and private staging). Accumulate here the new API traps
you confirm while implementing; do not duplicate them elsewhere in the repo.

## 1. `res.groups.category_id` → renamed to `privilege_id` (Odoo 19)

In Odoo 19 the rights-grouping field was renamed:
- **Before (≤17):** `res.groups.category_id` — category that groups groups.
- **Now (19):** `res.groups.privilege_id`, pointing to the
  **`res.groups.privilege`** model.

When referencing a security group's grouping (in `security/` or in code),
use the new name. Any legacy reference
`category_id` / `res.groups.category` to a typical 17-era root `res.groups`
fails or is left orphaned in 19.

## 2. <list> view instead of <tree> (Odoo 19)

The `<tree>` tag of list views was renamed to **`<list>`**
(`<tree>` was the historical tag of `ir.ui.view` in previous versions).
- **Before (≤17):** `<tree>` in `views/*.xml`.
- **Now (19):** `<list>` (with equivalent attributes: `editable`,
  `create`, `delete`, multiplies, etc.).

A 17-era addon written with `<tree>` does not load its view in 19; migrate
to `<list>` when porting.

## 3. Reconfirmed in the test environment

These two traps were confirmed while setting up the specialization's test
environment (make contract): `make test-clean` installs the module from
scratch and exposes these API renames as a load error if an addon uses them
under the old name. The antidote is versioning the addon against the 19 API
(`res.groups.privilege` + `<list>`).

## Relation to schema drift

Schema drift in managed builds (a platform rebuild that leaves ghost
columns, see SKILL.md §Traps) compounds these API renames: an addon that the
build does not re-install from scratch can end up in an intermediate state
(old `<tree>` view + DB with new schema). `make test-clean`
(install from scratch) is the real detector.
