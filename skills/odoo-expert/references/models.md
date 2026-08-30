# Model Design & ORM Patterns

## Model Declaration

```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model Description'
    _order = 'name, create_date desc'
    _rec_name = 'name'           # field for display (default: name)
    _inherit = ['mail.thread', 'mail.activity.mixin']  # mixins
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Name must be unique!'),
    ]
```

### Meta Attributes

| Attribute | Purpose |
|---|---|
| `_name` | Model identifier (required for new models) |
| `_description` | UI label (shown in debug mode) |
| `_order` | Default sort for search results |
| `_rec_name` | Field used for display/label |
| `_inherit` | Parent model(s) to extend |
| `_inherits` | Delegation mapping `{parent: fk_field}` |
| `_table` | Override DB table name (auto: dots → underscores) |
| `_sql_constraints` | List of (name, sql_def, message) |
| `_auto` | Auto-create table (set False for custom SQL views) |
| `_log_access` | Auto-create access fields (default: True) |

## Field Patterns

### Scalar Fields

```python
name = fields.Char(string='Name', required=True, index=True)
description = fields.Text()
notes = fields.Html()
quantity = fields.Integer(default=0)
price = fields.Float(digits='Product Price')  # uses decimal_precision
active = fields.Boolean(default=True)
code = fields.Char(size=10)  # limited length
color = fields.Integer()  # for kanban color picker
```

### Temporal Fields

```python
date_start = fields.Date(string='Start Date')
date_deadline = fields.Date(string='Deadline')
create_date = fields.Datetime(readonly=True)  # auto-managed
last_check = fields.Datetime()

# Date helpers
from odoo.fields import Date, Datetime
today = Date.today()
now = Datetime.now()
Date.to_date('2026-05-05')
Date.context_today(env)
```

### Selection Fields

```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
], default='draft', required=True, tracking=True)

# Dynamic selection
type = fields.Selection(selection='_selection_type')

def _selection_type(self):
    return [('a', 'A'), ('b', 'B')]
```

### Relational Fields

```python
# Many2one (FK)
partner_id = fields.Many2one(
    'res.partner', 
    string='Partner',
    required=True,
    ondelete='cascade',  # cascade | set null | restrict
    domain=[('customer_rank', '>', 0)],
    context={'default_customer_rank': 1},
    tracking=True,
)

# One2many (reverse relation)
order_line_ids = fields.One2many(
    'sale.order.line',    # comodel
    'order_id',            # inverse field (on comodel)
    string='Order Lines',
    copy=True,
)

# Many2many (junction table)
tag_ids = fields.Many2many(
    'res.partner.category',  # comodel
    'my_model_tag_rel',       # relation table (optional)
    'my_model_id',            # column1 (optional)
    'tag_id',                 # column2 (optional)
    string='Tags',
)
```

### Computed Fields — Complete Patterns

```python
# Basic computed field
amount_total = fields.Monetary(
    compute='_compute_amount_total',
    store=True,  # default for computed in v19
    currency_field='currency_id',
)

@api.depends('line_ids', 'line_ids.price_subtotal')
def _compute_amount_total(self):
    for order in self:
        order.amount_total = sum(order.line_ids.mapped('price_subtotal'))

# Writable computed field (with inverse)
partner_name = fields.Char(
    compute='_compute_partner_name',
    inverse='_set_partner_name',
    store=False,
)

def _compute_partner_name(self):
    for rec in self:
        rec.partner_name = rec.partner_id.name

def _set_partner_name(self):
    for rec in self:
        if rec.partner_id:
            rec.partner_id.name = rec.partner_name

# Computed with search
task_priority = fields.Selection(
    [('0', 'Low'), ('1', 'Medium'), ('2', 'High')],
    compute='_compute_priority',
    search='_search_priority',
)

def _search_priority(self, operator, value):
    # Return domain on underlying fields
    return [('priority', operator, value)]
```

### Boolean Computed Fields (Search Pattern)

```python
is_expired = fields.Boolean(
    compute='_compute_is_expired',
    search='_search_is_expired',
)

@api.depends('end_date')
def _compute_is_expired(self):
    today = fields.Date.today()
    for rec in self:
        rec.is_expired = bool(rec.end_date) and rec.end_date < today

def _search_is_expired(self, operator, value):
    today = fields.Date.context_today(self)
    if (operator == '=' and value) or (operator == '!=' and not value):
        return [('end_date', '<', today)]
    return ['|', ('end_date', '>=', today), ('end_date', '=', False)]
```

## Constraints

```python
# @api.constrains (Python-level)
@api.constrains('date_start', 'date_end')
def _check_dates(self):
    for rec in self:
        if rec.date_start and rec.date_end:
            if rec.date_start > rec.date_end:
                raise ValidationError(_('Start date must be before end date'))

# SQL constraints (DB-level)
_sql_constraints = [
    ('name_unique', 'unique(name)', 'Name must be unique!'),
    ('price_positive', 'check(price > 0)', 'Price must be positive!'),
    ('code_length', 'check(length(code) <= 10)', 'Code too long!'),
]
```

## Methods — Best Practices

```python
# Override with super
def write(self, vals):
    if 'state' in vals:
        self._check_state_transition(vals['state'])
    return super().write(vals)

# Action methods (button handlers)
def action_confirm(self):
    self.ensure_one()  # or handle multiple
    self.write({'state': 'confirmed'})
    self.message_post(body='Order confirmed')
    return True

# Bulk operations
def _bulk_update_prices(self, price_map):
    """Update prices efficiently."""
    for product_id, new_price in price_map.items():
        self.browse(product_id).write({'list_price': new_price})

# Using Command for relational writes
def action_add_lines(self):
    vals_list = [(0, 0, {'product_id': p.id, 'qty': 1}) for p in products]
    self.write({'order_line_ids': vals_list})
```

## State Machine Pattern

```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('sale', 'Sales Order'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
], default='draft', tracking=True)

# State transitions with validation
def action_confirm(self):
    for order in self:
        if order.state != 'draft':
            raise UserError(_('Only draft orders can be confirmed'))
    self.write({'state': 'sale'})

def action_cancel(self):
    for order in self:
        if order.state in ('done', 'cancel'):
            raise UserError(_('Cannot cancel done/cancelled orders'))
    self.write({'state': 'cancel'})

# Use state in domains
state_buttons = {
    'draft': [('state', '=', 'draft')],
    'all': [],
}
```

## Onchange (UI Only)

```python
@api.onchange('partner_id')
def _onchange_partner(self):
    self.fiscal_position_id = self.partner_id.property_account_fiscal_position_id
    self.pricelist_id = self.partner_id.property_product_pricelist_id
    # Return warning
    return {
        'warning': {
            'title': _('Credit Limit Exceeded'),
            'message': _('This partner has exceeded their credit limit.'),
        }
    }
```

⚠️ **Onchange rules:**
- Only for UI updates — no permanent DB writes
- Don't do heavy DB operations (locks)
- Don't create/modify other records
- Use `return` for warnings/domains

## Cron Jobs

```python
# XML definition
<record id="ir_cron_cleanup" model="ir.cron">
    <field name="name">Cleanup Old Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">model._cron_cleanup()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="active">True</field>
</record>

# Python method
def _cron_cleanup(self):
    _logger.info('Starting cleanup cron')
    old_records = self.search([('create_date', '<', fields.Date.today() - timedelta(days=30))])
    old_records.unlink()
    _logger.info('Cleaned %d records', len(old_records))
```

## Wizard Pattern (TransientModel)

```python
class MyWizard(models.TransientModel):
    _name = 'my.model.wizard'
    _description = 'My Wizard'
    
    partner_ids = fields.Many2many('res.partner')
    date = fields.Date(default=fields.Date.today)
    
    def action_apply(self):
        self.ensure_one()
        for partner in self.partner_ids:
            partner.write({'last_contact': self.date})
        return {'type': 'ir.actions.act_window_close'}
```

## Test Pattern

```python
from odoo.tests import common, tagged

@tagged('post_install', '-at_install')
class TestMyModel(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.model = self.env['my.model']
    
    def test_create(self):
        record = self.model.create({'name': 'Test'})
        self.assertEqual(record.name, 'Test')
        self.assertEqual(record.state, 'draft')
    
    def test_action_confirm(self):
        record = self.model.create({'name': 'Test'})
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
```

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Model name | `dot.notation`, lowercase | `sale.order` |
| Model class | PascalCase | `SaleOrder` |
| Fields | snake_case, lowercase | `partner_id`, `date_order` |
| Many2one | `_id` suffix | `partner_id` |
| One2many | `_ids` suffix | `order_line_ids` |
| Many2many | `_ids` suffix | `tag_ids` |
| Methods | snake_case, verb prefix | `action_confirm`, `_compute_total` |
| Compute methods | `_compute_<field>` | `_compute_amount` |
| Search methods | `_search_<field>` | `_search_is_expired` |
| Inverse methods | `_set_<field>` | `_set_partner_name` |
| Action buttons | `action_<verb>` | `action_cancel` |
| Private methods | `_` prefix | `_check_state` |
