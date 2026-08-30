# Module Structure & Anatomy

## Complete Module File-by-File

### `__init__.py` (root)

```python
from . import models
from . import wizards
from . import report
```

### `__manifest__.py`

```python
{
    'name': 'My Module',
    'version': '19.0.1.0.0',
    'category': 'Category/Subcategory',
    'summary': 'Short summary',
    'description': 'Long description (reST)',
    'author': 'Author Name',
    'website': 'https://example.com',
    'license': 'LGPL-3',
    'depends': ['base'],  # list of required modules
    'data': [  # loaded in order
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml',
    ],
    'demo': ['data/demo.xml'],
    'installable': True,
    'application': False,
    'assets': {  # web assets (Odoo 15+)
        'web.assets_backend': [
            'my_module/static/src/**/*.js',
            'my_module/static/src/**/*.scss',
        ],
    },
}
```

### Data Loading Order

Odoo loads `data` files **in order**. Critical:
1. Security (groups, ACLs, rules) FIRST
2. Models data (ir.model, categories)
3. Views (need security)
4. Menus (need views/actions)
5. Demo data LAST

If a file references something from another file, the referenced file MUST come first.

### `__init__.py` (models/)

```python
from . import my_model
from . import my_model_line
```

### Model File Pattern

```python
# models/my_model.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ── Fields ──
    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)

    # ── Compute methods ──
    @api.depends('line_ids', 'line_ids.amount')
    def _compute_total(self):
        for record in self:
            record.total = sum(record.line_ids.mapped('amount'))

    # ── Constraints ──
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for r in self:
            if r.date_start and r.date_end and r.date_start > r.date_end:
                raise ValidationError(_('End date must be after start date'))

    # ── CRUD overrides ──
    def create(self, vals_list):
        # pre-create logic
        records = super().create(vals_list)
        # post-create logic
        return records

    def write(self, vals):
        # pre-write logic
        result = super().write(vals)
        # post-write logic
        return result

    def unlink(self):
        for record in self:
            if record.state == 'done':
                raise UserError(_('Cannot delete completed records'))
        return super().unlink()

    # ── Action methods ──
    def action_confirm(self):
        self.write({'state': 'confirmed'})
        return True

    # ── Internal methods ──
    def _my_internal_helper(self):
        """Do something internal."""
        pass
```

## Data Files

### Demo Data

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="demo_my_record" model="my.model">
        <field name="name">Demo Record</field>
        <field name="partner_id" ref="base.res_partner_1"/>
        <field name="state">draft</field>
    </record>
</odoo>
```

### Configuration Data (noupdate)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Sequences -->
        <record id="seq_my_model" model="ir.sequence">
            <field name="name">My Model Sequence</field>
            <field name="code">my.model</field>
            <field name="prefix">MY/%(year)s/</field>
            <field name="padding">5</field>
        </record>

        <!-- Email templates -->
        <record id="mail_template_confirm" model="mail.template">
            <field name="name">Confirmation Email</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="subject">{{ object.name }}</field>
            <field name="email_to">{{ object.partner_id.email }}</field>
            <field name="body_html" type="html">
                <p>Your record has been confirmed.</p>
            </field>
        </record>
    </data>
</odoo>
```

## Report Files

```python
# report/my_report.py
from odoo import api, models


class MyReport(models.AbstractModel):
    _name = 'report.my_module.my_report_template'
    _description = 'My Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['my.model'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'my.model',
            'docs': docs,
            'data': data,
        }
```

```xml
<!-- report/my_report_template.xml -->
<template id="my_report_template">
    <t t-call="web.external_layout">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <div class="page">
                    <h2>Report for <t t-esc="o.name"/></h2>
                </div>
            </t>
        </t>
    </t>
</template>
```

```xml
<!-- report/report_action.xml -->
<record id="action_report_my_model" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.my_report_template</field>
    <field name="report_file">my_module.my_report_template</field>
    <field name="print_report_name">'Report - %s' % (object.name)</field>
</record>
```

## Migration Scripts

```python
# migrations/19.0.1.0.0/pre-migration.py
def migrate(cr, version):
    """Run BEFORE module update."""
    # Rename column
    cr.execute("ALTER TABLE my_model RENAME COLUMN old_field TO new_field")
    # Update values
    cr.execute("UPDATE my_model SET state = 'draft' WHERE state IS NULL")


# migrations/19.0.1.0.0/post-migration.py
def migrate(cr, version):
    """Run AFTER module update."""
    # Can use ORM through env (but version is None if fresh install)
    if not version:
        return
    # Cleanup
    cr.execute("DELETE FROM my_model WHERE active = false")
```

## Tests Directory

```
tests/
├── __init__.py
├── test_my_model.py
├── test_my_wizard.py
└── common.py           # shared test fixtures
```

### Test File

```python
from odoo.tests import common, Form, tagged


@tagged('post_install', '-at_install')
class TestMyModel(common.TransactionCase):
    """Test My Model functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.my_model = cls.env['my.model']
        cls.partner = cls.env.ref('base.res_partner_1')

    def test_01_create(self):
        """Basic creation test."""
        record = self.my_model.create({
            'name': 'Test',
            'partner_id': self.partner.id,
        })
        self.assertEqual(record.name, 'Test')
        self.assertEqual(record.partner_id, self.partner)

    def test_02_form(self):
        """Test with Form (simulates UI)."""
        with Form(self.my_model) as f:
            f.name = 'Form Test'
            f.partner_id = self.partner
        record = f.save()
        self.assertEqual(record.name, 'Form Test')

    def test_03_state_transition(self):
        """Test state machine."""
        record = self.my_model.create({'name': 'Test'})
        self.assertEqual(record.state, 'draft')
        
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
        
        record.action_done()
        self.assertEqual(record.state, 'done')

    def test_04_constraint(self):
        """Test validation constraint."""
        from odoo.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.my_model.create({
                'name': 'Bad Dates',
                'date_start': '2026-05-10',
                'date_end': '2026-05-01',
            })
```

### Test Tags

| Tag | When to Use |
|---|---|
| `post_install` | After all modules installed |
| `at_install` | During module install (default) |
| `-at_install` | NOT during install (skip with --test-enable) |
| `standard` | Run in standard test suite |
| `slow` | Takes >10 seconds |
| `multi` | Requires multiple DBs |

## Module Dependencies

### `depends` in Manifest

```python
'depends': [
    'base',       # always needed
    'mail',       # for chatter
    'sale',       # for sale order extension
    'account',    # for accounting
]
```

### Conditional Dependencies

```python
'depends': ['base', 'sale'],
# If you need account only when it's installed:
'auto_install': True,  # auto-installs when all deps are present
```

### Cross-Module Extension

```python
# my_module/models/sale_order.py
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    my_custom_field = fields.Char()
```

This extends `sale.order` only when `my_module` AND `sale` are installed.
