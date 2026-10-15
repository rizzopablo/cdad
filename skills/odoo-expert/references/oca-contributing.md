# OCA — requirements for publishing and contributing

Source: `OCA/odoo-community.org` (`website/Contribution/CONTRIBUTING.rst` and
`oca_repository_policy.rst`), consulted 2026-08-30. When in doubt, the repo rules.

## Commit messages

Format: `[TAG] module_name: short description`

- Summary ≤ 50 characters, **no prefix before the tag**; body lines ≤ 80.
- **English**, present imperative: "Fix formatting", not "Fixes" nor "Fixed".
- It must say **which module** it touches and **why** the change.

| Tag | Use |
|---|---|
| `[ADD]` | new module or feature |
| `[FIX]` | bug fix |
| `[IMP]` | improvement of something existing |
| `[REF]` | refactor with no functional change |
| `[MIG]` | version migration |
| `[REM]` | removal |

**Forbidden:**

- One-word commits ("bugfix", "improvements").
- "Fix pep8", "Code review", "Add unittest" commits **on top of** a feature
  commit — that belongs inside the corresponding commit.
- One commit touching **several modules** at once: split it into one commit per module.

## Names

**Modules** — lowercase and underscores, in **singular** (unless the Odoo
model is already plural, e.g. `mrp_operations_*`):

| Case | Prefix | Example |
|---|---|---|
| Base for other modules | `base_` | `base_location_nuts` |
| Localization | `l10n_CC_` (CC = country code) | `l10n_es_pos` |
| Extends an Odoo module | `<odoo_module>_` | `mail_forward` |
| Combines Odoo + OCA | Odoo's name first | `crm_partner_firstname` |

**Repositories** — with dashes, not underscores (`l10n-belgium`,
`connector-magento`). Never "odoo" nor "openerp" in the name.

**Files** — only `[a-z0-9_]`. Permissions: directories 755, files 644.

## Version in the manifest

Odoo major version + module `x.y.z`: the first release of a module for
19.0 is `19.0.1.0.0`.

## What a module needs before merging

**Manifest**

- No empty keys.
- `license` and `images` present.
- `author` ends with `Odoo Community Association (OCA)`.
- `website` pointing to the repo: `https://github.com/OCA/<repo>`.

**Documentation**

- `README.rst` explaining purpose, installation and usage.
- External dependencies documented in the installation section.
- Description following the template, **no empty sections**.
- **No logos or company branding** — credit goes in authors/contributors.

**Code**

- PEP8 (flake8) and OCA guidelines for Python, XML, JavaScript and CSS.
- All tests green.

**Tests**

- Unit test for new functionality.
- Regression test for every bugfix.
- **No depending on demo data.**
- Coverage equal or better than before.

**Dependencies**

- External ones in `external_dependencies` of the manifest.
- Python packages in `requirements.txt`.
- OCA dependencies in `oca_dependencies.txt`.
- **No pinning exact versions.**

**Migrations**

- An incompatible change requires a migration script.
- Migrating between Odoo major versions: script or note in the README.

**Translations**

- A PR **never** modifies `.po` directly: that is Weblate's responsibility.
- Exception: a new module may ship its own `.po` files.

## Review process

- Two **different things** are needed: code review and functional testing.
- At least one approval must come from a PSC member or someone with write
  access to the repo. `@OCA/core-maintainers` can be called in.
- People with write access merge, preferably Core Maintainers,
  respecting the author (`--author`) and their commit message.
- A PR without activity for **6 months** may be closed.

**Reviewer's checklist:** is it generic enough for the community? does it
duplicate another OCA module? is it documented? is the approach correct? are there
use cases? is there hardcoded configuration? does it ship demo data? are the
commits clean?

**Tone:** thank first, be cordial, explain the reason for each request.

## OCA repository policy

A module at the **Stable** or **Mature** level must meet three things:

1. **Quality** — passes the automatic checks and was peer-reviewed.
2. **Stability** — does not break existing installations or modules that depend
   on the same Odoo version.
3. **Relevance** — generic, and without significant overlap with existing OCA
   modules.

At **Alpha** and **Beta** the criterion is relaxed (the automatic checks suffice)
so as not to slow down first-time contributors. Abandoned incubating code gets
deleted.

Each repository has a responsible **PSC** (Project Steering Committee), which
decides naming and organization exceptions.
