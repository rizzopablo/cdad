# Odoo 19 Framework Architecture

## Core ORM Structure

Odoo 19 restructures the ORM into `odoo/orm/` (previously flat files in `odoo/`).

### Key Directories

```
odoo/odoo/orm/
├── models.py            # Model, AbstractModel base classes
├── model_classes.py     # Model class assembly, inheritance resolution
├── models_transient.py  # TransientModel (wizards)
├── environments.py      # Environment (env), transaction management
├── registry.py          # Module registry, model lookup
├── fields.py            # Field base class
├── fields_relational.py # Many2one, One2many, Many2many
├── fields_numeric.py    # Integer, Float, Monetary
├── fields_textual.py    # Char, Text, Html
├── fields_temporal.py   # Date, Datetime
├── fields_misc.py       # Boolean, Id, Json, Selection
├── fields_binary.py     # Binary, Image
├── fields_properties.py # Properties, PropertiesDefinition (v19)
├── decorators.py        # @depends, @onchange, @constrains, @model, etc.
├── domains.py           # Domain class, domain expressions
├── commands.py          # Command class for relational writes
├── types.py             # Type annotations
└── utils.py             # ORM utilities
```

### Top-Level Modules

```
odoo/odoo/
├── api.py               # API helpers (deprecated patterns)
├── http.py              # HTTP routing, controllers
├── exceptions.py        # UserError, ValidationError, AccessError, etc.
├── sql_db.py            # Database connections, cursor management
├── tools/               # Utilities (cache, config, misc, translation)
├── cli/                 # Command-line interface (odoo-bin)
├── service/             # Server services
├── tests/               # Test framework
├── addons/              # Core addons (base, etc.)
└── orm/                 # ORM (see above)
```

## Environment (env)

The `Environment` wraps: `cr` (cursor), `uid` (user), `context` (dict), and `registry`.

```python
# Access
self.env  # in model methods
env = request.env  # in controllers

# Common operations
env['model.name']           # get model class
env.ref('module.xml_id')    # get record by XML ID
env.user                    # current user (res.users)
env.company                 # current company
env.lang                    # current language
env.context.get('key')      # context value
env(context=new_ctx)        # return env with new context
env(sudo=True)              # return env with superuser
env(user=admin_user)        # return env as specific user
```

### Context Best Practices

```python
# Use with_context for temporary context changes
record.with_context(active_test=False).search([...])

# Common context keys
# 'active_test' — filter by active field (default True)
# 'lang' — language for translations
# 'tz' — timezone for datetimes
# 'company_id' — current company
# 'force_company' — override company for multi-company
# 'default_<field>' — default values in create
```

## Registry

Maps model names to model classes. Populated during startup.

```python
# Access via env
registry = env.registry
model_class = registry['model.name']

# Model lifecycle
# 1. Python class defined with _name
# 2. _register() adds to pool
# 3. _build_model() assembles inheritance
# 4. _init_columns() creates DB schema
# 5. Module loaded and ready
```

## Recordsets

Odoo 19 uses recordsets (ordered collections of records):

```python
# Recordset operations
len(records)              # count
records[0]                # first record
for r in records: ...     # iteration
records | other           # union
records & other           # intersection
records - other           # difference
records.filtered(lambda r: r.state == 'done')
records.sorted(key=lambda r: r.date)
records.mapped('name')    # list of values
records.mapped('partner_id.name')  # traverses relations

# Ensure singleton
record.ensure_one()       # raise ValueError if not exactly one
```

## Fields Deep Dive

### Field Attributes (common)

| Attribute | Type | Purpose |
|---|---|---|
| `string` | str | UI label (auto-generated from field name if omitted) |
| `help` | str | Tooltip text |
| `readonly` | bool | Read-only in UI |
| `required` | bool | Required in UI |
| `default` | value/callable | Default value |
| `index` | bool | Add DB index |
| `copy` | bool | Copy field value on duplicate (default: True) |
| `tracking` | bool/str | Track field changes in chatter |
| `groups` | str | Comma-sep group XML IDs for visibility |
| `store` | bool | Store computed field in DB (default: True for computed) |
| `compute` | str | Method name for computed field |
| `inverse` | str | Method for write on computed field |
| `search` | str | Method for search on computed field |
| `related` | str | Dot-notation related field |
| `domain` | str/list | Filter for relational fields |
| `context` | dict | Context for relational fields |
| `ondelete` | str | Cascade/set null/restrict for Many2one |

### Monetary Fields

```python
amount = fields.Monetary(currency_field='currency_id')
currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
```

### Related Fields

```python
# Automatically reads through relation (computed, store=False by default)
partner_email = fields.Related('partner_id.email', store=True, readonly=True)
```

### Computed Fields

```python
total = fields.Float(compute='_compute_total', store=True, depends=['line_ids', 'line_ids.amount'])

@api.depends('line_ids', 'line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

**Critical rules:**
1. `@api.depends` must list ALL fields that affect the computation
2. Must assign value for EVERY record in self (even if no computation needed)
3. `store=True` (default in v19 for computed) → stored in DB, searchable, needs depends
4. `store=False` → computed on-the-fly, not searchable, lighter
5. `compute_sudo=True` (default when store=True since v13) → computes as superuser
6. Use `inverse` for writable computed fields

### Properties Fields (v19)

```python
# Dynamic property system (like res.partner properties but structured)
properties = fields.Properties(definition_field='property_definition')
property_definition = fields.PropertiesDefinition()
```

## Inheritance System

### 1. Extension (`_inherit`)

Extends existing model in-place. Shares DB table.

```python
class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    custom_field = fields.Char()  # added to sale.order
```

Multiple inheritance (extend multiple models):
```python
class MultiExtend(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
```

### 2. New Model via `_inherit` + `_name`

Creates NEW model, copying structure from parent. NEW DB table.

```python
class NewModel(models.Model):
    _name = 'my.new.model'
    _inherit = 'sale.order'  # copies sale.order structure
```

⚠️ **Use with intention** — this is NOT extending, it's cloning.

### 3. Delegation (`_inherits`)

Composition pattern. Creates FK to parent model.

```python
class ProductProduct(models.Model):
    _name = 'product.product'
    _inherits = {'product.template': 'product_tmpl_id'}
```

Delegated fields are accessible directly on child. Rarely used in modern Odoo.

## Model Classes

| Class | Use | DB Table |
|---|---|---|
| `models.Model` | Persistent data | Yes |
| `models.AbstractModel` | Mixin/reusable logic | No |
| `models.TransientModel` | Wizards/temporary | Yes (autovacuum) |

```python
# AbstractModel example (mixin)
class MyMixin(models.AbstractModel):
    _name = 'my.mixin'
    
    def common_method(self):
        pass

class RealModel(models.Model):
    _name = 'my.real'
    _inherit = 'my.mixin'  # gets common_method
```

## Controllers

```python
from odoo import http

class MyController(http.Controller):
    @http.route('/my/path', type='http', auth='user', methods=['GET'])
    def my_endpoint(self, **kwargs):
        return http.request.render('module.template', {'key': value})
    
    @http.route('/my/json', type='json', auth='public')
    def my_json(self, **kwargs):
        return {'result': 'ok'}
```

Route types: `http` (returns Response/HTML), `json` (returns JSON).
Auth: `user` (logged in), `public` (no auth), `none` (no session).

## HTTP & Routing

Key models for web:
- `ir.http` — request handling, routing, ACL checks for controllers
- `ir.attachment` — file storage
- `ir.binary` — file serving

## Caching

```python
# ORM automatically caches recordset data
# Manual cache with tools
from odoo.tools import ormcache

@ormcache('self.id')
def expensive_computation(self):
    ...
```

## Debugging

```bash
# Dev mode - auto-reload XML and Python
odoo-bin --dev=xml,qweb,werkzeug

# Log level
odoo-bin --log-level=debug

# Profiler
from odoo.tools.profiler import profile

@profile
def my_method(self):
    ...
```
