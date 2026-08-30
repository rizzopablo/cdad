---
name: odoo-expert
description: >
  Generate, review, and modify Odoo 19 modules with expert-level knowledge of the ORM,
  views, security, and best practices. Use when: developing new Odoo modules, extending
  existing ones, writing models/views/security files, fixing Odoo code issues, implementing
  computed fields/relations/onchanges, creating XML views (form/tree/kanban/search),
  setting up ACLs/record rules/groups, or answering Odoo framework questions.
  Covers: Odoo ORM (new API), OCA patterns, pylint-odoo rules, module structure,
  inheritance (_inherit/_inherits), computed fields, wizards, reports, cron jobs,
  security architecture, and the OCA standards required to publish: commit and
  naming conventions, manifest/README requirements, review process, repository
  policy, and the module migration procedure between Odoo versions.
---

# Odoo 19 Expert

Turn AI agents into expert Odoo programmers. Ground every decision in Odoo source code,
OCA patterns, and pylint-odoo rules. **Never reinvent the wheel** — always check how
Odoo base/enterprise already solves it.

## Quick Workflow

1. **Understand the requirement** — map to Odoo concepts (model, field, view, security)
2. **Search existing code** — grep the Odoo source to find how Odoo/OCA already
   solves it (see "Where to Look in Source Code"). Never invent what base already does.
3. **Generate code** — follow standards below
4. **Validate** — code must pass pylint-odoo, `oca-checks-odoo-module`, and be
   installable from scratch. **How tests are run is defined by the project's
   environment, not by this skill** — if it exposes the `odoo-make-env` contract,
   use `make test` / `make test-one` / `make test-clean`, never raw `odoo-bin` in
   a gate (see `references/evidencia-y-calidad.md`).

## Module Structure (canonical)

```
custom_module/
├── __init__.py               # imports from models/, wizards/, etc.
├── __manifest__.py           # metadata, depends, data
├── models/                   # one file per model
│   ├── __init__.py
│   └── my_model.py
├── security/
│   ├── ir.model.access.csv   # ACLs (mandatory)
│   └── security.xml          # groups, record rules
├── views/
│   ├── my_model_views.xml    # form, tree, kanban, search
│   └── menus.xml             # actions + menus
├── data/                     # demo/data XML/CSV
├── static/src/               # JS/CSS/assets
├── wizard/                   # TransientModel wizards
├── report/                   # QWeb reports
└── tests/
    ├── __init__.py
    └── test_my_model.py
```

## Golden Rules

- **New API only** (Odoo 8+) — no `cr, uid, ids, context` signatures
- **Call `super()`** on every overridden method — `pylint-odoo` rule `method-required-super`
- **Never mix `_inherit` + `_name`** in same class unless intentionally creating a new table
- **One import per line** — PEP 8, enforced by `pylint-odoo`
- **`@api.one` is deprecated** — use iteration over recordset or `@api.model`
- **Computed fields**: `@api.depends()` must list ALL dependency fields, or infinite loops occur
- **Security first**: every new model needs ACL entries; follow least-privilege principle
- **Use `<xpath>` for view inheritance** — never copy-paste entire views

## Key Decorators (Odoo 19)

| Decorator | When to use |
|---|---|
| `@api.model` | No recordset context (create, search helpers) |
| `@api.depends(*fields)` | Computed field dependencies |
| `@api.onchange(*fields)` | UI-only dynamic updates (no DB write) |
| `@api.constrains(*fields)` | Python-level validations |
| `@api.returns(model)` | Return recordset of specific model |

See `references/framework.md` for full decorator details.

## Field Types (Odoo 19 ORM)

All fields in `odoo.orm.fields.*` (restructured in v19):

- **Scalar**: `Char`, `Text`, `Html`, `Integer`, `Float`, `Monetary`, `Boolean`, `Date`, `Datetime`
- **Relational**: `Many2one`, `One2many` (with `inverse`), `Many2many` (with `relation`/`column1`/`column2`)
- **Binary**: `Binary`, `Image`
- **Special**: `Selection`, `Properties`, `Json`, `Many2oneReference`, `Reference`, `Id`

See `references/models.md` for field patterns and computed field best practices.

## ORM Key Patterns

```python
# Search
records = env['model.name'].search([('field', '=', value)], limit=10)

# Create
record = env['model.name'].create({'field': value})

# Write
record.write({'field': new_value})

# Browse
record = env['model.name'].browse(id)

# Commands (for relational writes)
(0, 0, vals)    # create linked record
(1, id, vals)   # update linked record
(2, id)         # delete linked record
(3, id)         # unlink relationship
(4, id)         # link existing
(5,)            # unlink all
(6, 0, [ids])   # replace all links
```

## Where to Look in Source Code

**First, resolve the source root** — it varies by environment. Try, in order:

```sh
# odoo-sandbox: inside the sandbox
ls /home/odoo/src/odoo/odoo/orm 2>/dev/null
# a checkout on the host
python3 -c "import odoo, os; print(os.path.dirname(odoo.__file__))" 2>/dev/null
# last resort
find / -maxdepth 6 -type d -path '*/odoo/orm' 2>/dev/null | head -1
```

Call that root `$ODOO`. Then:

| Need | Look in |
|---|---|
| ORM internals | `$ODOO/orm/` |
| Base models (ir.*, res.*) | `$ODOO/addons/base/models/` |
| Field definitions | `$ODOO/orm/fields_*.py` |
| Decorators | `$ODOO/orm/decorators.py` |
| Exceptions | `$ODOO/exceptions.py` |
| View structure (ir.ui.view) | `$ODOO/addons/base/models/ir_ui_view.py` |
| Security rules (ir.rule) | `$ODOO/addons/base/models/ir_rule.py` |
| An existing OCA module doing something similar | the OCA repo for that domain on GitHub |

Search with `grep -rn` / `rg` over `$ODOO`. **Iron Rule:** every design decision
cites the addon where you verified it. Nothing invented.

## Reference Files

Load these as needed for detailed guidance:

- **`references/framework.md`** — Odoo 19 architecture, ORM internals, decorators, environments, registry
- **`references/models.md`** — Model design, inheritance, computed fields, relations, constraints
- **`references/views.md`** — XML view types, xpath inheritance, actions, menus, widgets
- **`references/security.md`** — ACLs, groups, record rules, compute_sudo, security patterns
- **`references/standards.md`** — pylint-odoo rules, OCA patterns, coding conventions, validation workflow
- **`references/module-structure.md`** — Complete module anatomy, manifest fields, data loading, tests
- **`references/oca-contributing.md`** — Qué exige OCA para publicar: commits, nombres, manifest, README, tests, dependencias, proceso de revisión y política del repositorio
- **`references/oca-migration.md`** — Migrar un módulo entre versiones: procedimiento git que preserva la historia, convención `[MIG]`, qué actualizar y qué no tocar
- **`references/evidencia-y-calidad.md`** — Evidencia requerida antes de dar algo por listo, tabla anti-racionalización, y setup de `pre-commit`

## Limitations

Cannot validate business logic correctness. Focus on: clear names, proper structure,
security, and maintainability. Human reviews business semantics.
