# Standards: pylint-odoo, OCA Patterns & Best Practices

## pylint-odoo Rules Reference

Install: `pip install pylint-odoo`
Run: `pylint --load-plugins=pylint_odoo my_module/`

### Python Rules (W8xxx / E8xxx / C8xxx)

| Code | Name | Severity | Fix |
|---|---|---|---|
| W8105 | api-one-deprecated | Warning | Use `@api.model` or iterate recordset |
| W8106 | method-required-super | Warning | Add `super().method()` call |
| W8110 | missing-return | Warning | Add return statement |
| W8111 | method-compute | Warning | Use proper `_compute_*` method name |
| W8112 | method-inverse | Warning | Use proper `_set_*` method name |
| W8113 | method-search | Warning | Use proper `_search_*` method name |
| W8114 | invalid-character | Warning | Remove non-ASCII chars from identifiers |
| W8115 | external-request-timeout | Warning | Add `timeout` param to HTTP requests |
| W8120 | sql-injection | Warning | Use parameterized queries `%s` |
| W8121 | eval-referenced | Warning | Avoid `eval()` |
| W8122 | except-pass | Warning | Log or handle exception properly |
| W8130 | translation-field | Warning | Use `_()` for translatable strings |
| W8131 | translation-required | Warning | Mark strings for translation |
| W8135 | use-vim-comment | Warning | Remove vim modeline comments |
| W8138 | attribute-deprecated | Warning | Use new attribute syntax |
| W8145 | deprecated-odoo-module | Warning | Don't import from deprecated odoo modules |
| W8155 | deprecated-data-xml-node | Warning | Use `<odoo>` instead of `<openerp>` |
| E8101 | dangerous-default-value | Error | Mutable default in function args |
| E8102 | dangerous-qweb-replace-noupdate | Error | `noupdate="1"` with `position="replace"` |
| E8103 | duplicate-id | Error | Duplicate XML ID |
| E8104 | dangerous-filter-duplicate | Error | Filter duplication risk |
| E8107 | dangerous-view-replace-wo-priority | Error | View replace without priority |
| C8101 | manifest-author-string | Convention | Don't put author as string |
| C8102 | manifest-maintainer-list | Convention | Use list for maintainers |
| C8103 | manifest-version-format | Convention | Version must match format |
| C8104 | manifest-deprecated-key | Convention | Remove deprecated manifest keys |
| C8105 | license-allowed | Convention | Use valid SPDX license |
| C8106 | category-allowed | Convention | Use valid module category |
| C8107 | manifest-bad-keys | Convention | Fix deprecated manifest keys |

### XML Rules (W7xxx)

| Code | Name | Severity | Fix |
|---|---|---|---|
| W7902 | create-user-wo-reset-password | Warning | Add password reset action |
| W7903 | dangerous-qweb-expr | Warning | Use safe expressions in QWeb |
| W7904 | duplicate-id-csv | Warning | Duplicate CSV record ID |
| W7905 | duplicate-xml-record-id | Warning | Duplicate XML record |
| W7906 | duplicate-xml-fields | Warning | Same field twice in view |
| W7907 | duplicate-xml-record-id | Warning | Duplicate record ID in XML |
| W7908 | missing-newline-extra-blank | Warning | Formatting: missing blank line |
| W7909 | redundant-hotkey | Warning | Redundant hotkey definition |

### Common Fixtures

```python
# .pylintrc
[MASTER]
load-plugins=pylint_odoo

[odoolint]
manifest_required_authors=Your Company
manifest_version_format=^\d+\.\d+\.\d+\.\d+$
```

## OCA Patterns

### Module Structure (OCA standard)

```
oca_module/
├── README.rst                    # OCA README (mandatory)
├── __init__.py
├── __manifest__.py
├── README.md                     # Module description
├── models/
├── views/
├── security/
├── tests/
├── static/
├── i18n/                         # Translations
├── migrations/                   # Migration scripts
│   └── 19.0.1.0.0/
│       └── pre-migration.py
└── setup/
```

### OCA Conventions

```python
# 1. No grouping imports
import os
import re
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

# 2. Model classes in same file if small, separate if large
# 3. One model per file when models are complex

# 4. _name always first class attribute
class MyModel(models.Model):
    _name = 'my.model'
    _description = '...'
    _inherit = ['mail.thread']
    _order = 'name'
    
    # Then fields, grouped logically
    # Name/identifier
    name = fields.Char(required=True)
    # Relations
    partner_id = fields.Many2one('res.partner')
    # State/flags
    state = fields.Selection([...])
    # Computed
    total = fields.Float(compute='_compute_total')
    
    # Then methods
```

### OCA Test Pattern

```python
from odoo.tests import Form, tagged

@tagged('post_install', '-at_install')
class TestMyModel(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.my_model = cls.env['my.model']
    
    def test_01_create_and_confirm(self):
        """Test creation flow."""
        # Use Form for realistic data entry
        with Form(self.my_model) as f:
            f.name = 'Test Record'
            f.partner_id = self.env.ref('base.res_partner_1')
        record = f.save()
        
        self.assertEqual(record.state, 'draft')
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
```

## Code Style Rules

### Imports

```python
# ❌ WRONG
import os, sys, re
from odoo import models, fields

# ✅ CORRECT
import os
import re
import sys

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
```

### String Translations

```python
# ❌ WRONG
raise UserError("This is an error")

# ✅ CORRECT
from odoo import _
raise UserError(_("This is an error"))

# With placeholders
raise UserError(_("Record %s cannot be processed", record.name))
```

### Logging

```python
import logging
_logger = logging.getLogger(__name__)

_logger.info('Starting process')
_logger.debug('Processing record %s', record.id)
_logger.warning('Deprecated method called')
_logger.error('Failed to process: %s', error)
```

### Domain Expressions

```python
# ✅ Use domain class (v19)
from odoo.orm.domains import Domain
domain = Domain([('state', '=', 'draft')]) & Domain([('active', '=', True)])

# Or list notation
domain = [
    '&',
    ('state', '=', 'draft'),
    ('active', '=', True),
]

# Or pythonic (implicit AND)
domain = [('state', '=', 'draft'), ('active', '=', True)]

# Common operators
# '=', '!=', '>', '>=', '<', '<='
# 'in', 'not in'
# 'like', 'ilike', 'not like', 'not ilike'
# '=like', '=ilike'  (SQL LIKE patterns)
# 'child_of', 'parent_of'
# '=?'  (conditional: value=None → ignored)

# Conditional domain element
domain = [('state', '=?', filter_state)]  # if filter_state is None, ignored

# Combining
domain_a = [('state', '=', 'draft')]
domain_b = [('active', '=', True)]
combined = domain_a + domain_b  # AND
combined = ['|'] + domain_a + domain_b  # OR
```

## Validation Workflow (Generate → Verify → Fix)

```
1. Generate code (models, views, security, manifest)
2. Run pylint-odoo → fix violations
3. Try install: odoo-bin -i module --stop-after-init
4. Run tests: odoo-bin -i module --test-enable
5. Fix any errors → repeat
```

### CI/CD Integration

```bash
# Full validation script
pylint --load-plugins=pylint_odoo my_module/ && \
odoo-bin -c odoo.conf -i my_module --stop-after-init --test-enable && \
echo "Module passes all checks"
```

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| `@api.one` | Deprecated, causes recordset issues | Use `@api.model` or iterate |
| `cr.execute("... %s" % val)` | SQL injection | `cr.execute("... %s", (val,))` |
| `_inherit` + `_name` confusion | Creates new table instead of extending | Use only `_inherit` to extend |
| No `super()` in overrides | Breaks parent behavior | Always call `super()` |
| `store=False` computed in tree view | Performance hit on list loads | Move to form or set `store=True` |
| Hardcoded XML IDs | Conflicts between modules | Use unique naming |
| No ACLs on new model | Nobody can access it | Add ir.model.access.csv |
| `sudo()` without reason | Security bypass | Use with justification |
| Empty `except: pass` | Silent failures | Log or raise |
| Mutable default in method | Shared state bug | Use `default=None` then set |

## Performance Rules

```python
# ❌ N+1 query problem
for order in orders:
    print(order.partner_id.name)  # DB hit per order

# ✅ Prefetch
partners = orders.mapped('partner_id')  # single query
for order in orders:
    print(order.partner_id.name)  # from cache

# ❌ Loop writes
for line in lines:
    line.write({'state': 'done'})

# ✅ Bulk write
lines.write({'state': 'done'})

# ❌ search in loop
for order in orders:
    invoices = env['account.move'].search([('invoice_origin', '=', order.name)])

# ✅ search with 'in'
order_names = orders.mapped('name')
invoices = env['account.move'].search([('invoice_origin', 'in', order_names)])
```

## Module Manifest Best Practices

```python
{
    'name': 'My Module',
    'version': '19.0.1.0.0',  # MAJOR.MINOR.PATCH.BUILD (Odoo convention)
    'category': 'Sales/Sales',
    'summary': 'Short summary shown in apps list',
    'description': """
Long description in reStructuredText.

Features:
* Feature one
* Feature two
""",
    'author': 'My Company',
    'website': 'https://mycompany.com',
    'license': 'LGPL-3',  # OCA prefers AGPL-3
    'depends': ['base', 'sale', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'data/demo.xml',
    ],
    'installable': True,
    'application': False,  # True if top-level app
    'auto_install': False,  # True if auto-installs when deps are present
}
```

### Version Format

`{odoo_version}.{major}.{minor}.{patch}` → `19.0.1.0.0`

- `19.0` — target Odoo version
- `1` — major feature release
- `0` — minor feature release
- `0` — patch/bugfix
