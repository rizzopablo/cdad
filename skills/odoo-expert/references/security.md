# Security: ACLs, Groups & Record Rules

## Security Architecture Layers

```
┌──────────────────────────────────────────┐
│  Layer 1: ACL (ir.model.access)          │  Model-level CRUD
│  Layer 2: Record Rules (ir.rule)         │  Row-level access
│  Layer 3: Field-level (groups attribute)  │  Field visibility
│  Layer 4: Python (check_access_rights)   │  Code-level guards
└──────────────────────────────────────────┘
```

## Layer 1: Access Control Lists (ACLs)

### CSV Format (`security/ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,my_module.group_user,1,0,0,0
access_my_model_manager,my.model.manager,model_my_model,my_module.group_manager,1,1,1,1
```

### CSV Field Mapping

| Column | Meaning |
|---|---|
| `id` | Unique XML ID |
| `name` | Human-readable label |
| `model_id:id` | Model reference (`model_<dot.to.underscore>`) |
| `group_id:id` | Group reference (leave blank for all users) |
| `perm_read` | Can read (0/1) |
| `perm_write` | Can write (0/1) |
| `perm_create` | Can create (0/1) |
| `perm_unlink` | Can delete (0/1) |

### Pattern: User/Manager Split

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_all,my.model.all,model_my_model,,1,0,0,0
access_my_model_user,my.model.user,model_my_model,group_my_module_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,group_my_module_manager,1,1,1,1
```

### Programmatic Access Check

```python
# Check before sensitive operations
self.env['my.model'].check_access_rights('write')

# Or use sudo() with caution
sudo_record = record.sudo()  # bypasses all security
```

## Layer 2: Record Rules

### XML Definition (`security/security.xml`)

```xml
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: User sees own records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('group_my_module_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>

<record id="rule_my_model_manager" model="ir.rule">
    <field name="name">My Model: Manager sees all</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('group_my_module_manager'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### Common Domain Patterns

```python
# User's own records
[('create_uid', '=', user.id)]

# User's company (multi-company)
[('company_id', 'in', company_ids)]

# User's company + subsidiaries (child_of)
[('company_id', 'child_of', [user.company_id.id])]

# Records assigned to user
[('user_id', '=', user.id)]

# Records where user is in team
[('team_id', 'in', user.sale_team_ids.ids)]

# Based on related model
[('partner_id.user_ids', 'in', [user.id])]

# Always true (full access)
[(1, '=', 1)]

# Always false (no access)
[(0, '=', 1)]
```

### Global Rules (no groups = all users)

```xml
<record id="rule_multi_company" model="ir.rule">
    <field name="name">Multi-company rule</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <field name="global" eval="True"/>  <!-- applies to ALL users, including admin -->
</record>
```

### Rule Combination Logic

- Rules of **same group** → OR (any matching rule grants access)
- Rules of **different groups** (user belongs to both) → AND (must pass ALL)
- ACL → must pass first, then rules apply
- `sudo()` bypasses everything

## Layer 3: Groups (Security Categories)

### Define Groups (`security/security.xml`)

```xml
<record id="module_category_my_module" model="ir.module.category">
    <field name="name">My Module</field>
    <field name="sequence">20</field>
</record>

<record id="group_my_module_user" model="res.groups">
    <field name="name">User</field>
    <field name="category_id" ref="module_category_my_module"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>

<record id="group_my_module_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="category_id" ref="module_category_my_module"/>
    <field name="implied_ids" eval="[(4, ref('group_my_module_user'))]"/>
    <field name="users" eval="[(4, ref('base.user_admin'))]"/>  <!-- auto-add admin -->
</record>
```

### Group Hierarchy

```
base.group_user (Employee)
    └── group_my_module_user
            └── group_my_module_manager (implies User)
```

Use `implied_ids` for hierarchy: if you have Manager, you implicitly have User.

### Field-Level Visibility

```xml
<!-- Only visible to managers -->
<field name="cost_price" groups="my_module.group_my_module_manager"/>

<!-- Readonly for users, editable for managers -->
<field name="margin" readonly="1" groups="my_module.group_my_module_manager"/>
```

### Check Groups in Python

```python
# Has group?
if user.has_group('my_module.group_my_module_manager'):
    ...

# Check with env
if self.env.user.has_group('base.group_system'):
    ...
```

## Layer 4: Security in Business Logic

```python
def action_sensitive_operation(self):
    self.ensure_one()
    # Check access
    self.check_access_rights('write')
    self.check_access_rule('write')
    
    # Or use access error
    if not self.env.user.has_group('my_module.group_manager'):
        raise AccessError(_('You must be a manager to perform this action'))
    
    # Proceed...
```

## compute_sudo — Security Gotcha

Since Odoo v13:
- `store=True` + computed field → `compute_sudo=True` by default
- `store=False` + computed field → `compute_sudo=False` by default

**Implication:** A stored computed field computes as superuser. If the underlying
records have record rules, the computation bypasses them. This can expose data
that should be restricted.

```python
# Explicit control
secret_total = fields.Monetary(
    compute='_compute_secret_total',
    store=True,
    compute_sudo=False,  # compute as current user (safer)
)
```

**Rule:** If computed data is sensitive → explicitly set `compute_sudo=False`.

## Security Checklist for New Models

- [ ] ACL entries in `security/ir.model.access.csv`
- [ ] Record rules if multi-user/multi-company
- [ ] Groups defined if role-based access needed
- [ ] Sensitive fields hidden with `groups` attribute
- [ ] `compute_sudo=False` on sensitive computed fields
- [ ] `check_access_rights` on sensitive methods
- [ ] Admin user added to manager group
- [ ] Security file listed in `__manifest__.py` `data`
- [ ] No hardcoded IDs or credentials
- [ ] Test with different user roles

## Manifest Security Reference

```python
{
    'data': [
        'security/security.xml',          # groups + rules
        'security/ir.model.access.csv',   # ACLs
        # ... other files
    ],
}
```

⚠️ Order matters! Security files should come BEFORE views/data that depend on them.
