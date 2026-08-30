# XML Views, Actions & Menus

## View Types

### Form View

```xml
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form string="My Model">
            <header>
                <button name="action_confirm" type="object" string="Confirm" 
                        class="btn-primary" invisible="state != 'draft'"/>
                <button name="action_cancel" type="object" string="Cancel"
                        invisible="state in ('done', 'cancel')"/>
                <field name="state" widget="statusbar" 
                       statusbar_visible="draft,confirmed,done"/>
            </header>
            <sheet>
                <div class="oe_button_box" name="button_box">
                    <button name="action_view_lines" type="object" 
                            class="oe_stat_button" icon="fa-list">
                        <field name="line_count" widget="statinfo" string="Lines"/>
                    </button>
                </div>
                <widget name="web_ribbon" title="Archived" bg_color="text-bg-danger"
                        invisible="active"/>
                <group>
                    <group string="General">
                        <field name="name"/>
                        <field name="partner_id"/>
                        <field name="date"/>
                    </group>
                    <group string="Details">
                        <field name="amount"/>
                        <field name="currency_id"/>
                        <field name="company_id" groups="base.group_multi_company"/>
                    </group>
                </group>
                <notebook>
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <tree editable="bottom">
                                <field name="product_id"/>
                                <field name="quantity"/>
                                <field name="price"/>
                                <field name="subtotal"/>
                            </tree>
                        </field>
                    </page>
                    <page string="Other Info" name="other_info">
                        <group>
                            <field name="create_uid"/>
                            <field name="create_date"/>
                        </group>
                    </page>
                </notebook>
            </sheet>
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### Tree/List View

```xml
<record id="view_my_model_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree string="My Model" 
              decoration-success="state == 'done'"
              decoration-warning="state == 'confirmed'"
              decoration-danger="state == 'cancel'"
              sample="1">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date"/>
            <field name="amount" sum="Total"/>
            <field name="state"/>
            <button name="action_confirm" type="object" string="Confirm"
                    icon="fa-check" invisible="state != 'draft'"/>
        </tree>
    </field>
</record>
```

### Kanban View

```xml
<record id="view_my_model_kanban" model="ir.ui.view">
    <field name="name">my.model.kanban</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state" class="o_kanban_mobile">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="amount"/>
            <field name="state"/>
            <templates>
                <t t-name="kanban-box">
                    <div t-attf-class="oe_kanban_card...">
                        <div class="o_dropdown_kanban dropdown">
                            <a role="button" class="dropdown-toggle" 
                               data-bs-toggle="dropdown">
                                <span class="fa fa-ellipsis-v"/>
                            </a>
                            <ul class="dropdown-menu">
                                <li><a type="edit">Edit</a></li>
                                <li><a type="delete">Delete</a></li>
                            </ul>
                        </div>
                        <div class="oe_kanban_content">
                            <div class="o_kanban_record_title">
                                <strong><field name="name"/></strong>
                            </div>
                            <div class="o_kanban_record_body">
                                <field name="partner_id"/>
                            </div>
                            <div class="o_kanban_record_bottom">
                                <div class="oe_kanban_bottom_left">
                                    <field name="amount" widget="monetary"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

### Search View

```xml
<record id="view_my_model_search" model="ir.ui.view">
    <field name="name">my.model.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search string="Search My Model">
            <field name="name" filter_domain="['|', ('name', 'ilike', self), ('partner_id', 'ilike', self)]"/>
            <field name="partner_id"/>
            <field name="state"/>
            <separator/>
            <filter name="draft" string="Draft" domain="[('state', '=', 'draft')]"/>
            <filter name="confirmed" string="Confirmed" domain="[('state', '=', 'confirmed')]"/>
            <filter name="my_records" string="My Records" 
                    domain="[('create_uid', '=', uid)]"/>
            <separator/>
            <group expand="0" string="Group By">
                <filter name="group_partner" string="Partner" 
                        context="{'group_by': 'partner_id'}"/>
                <filter name="group_state" string="State" 
                        context="{'group_by': 'state'}"/>
                <filter name="group_date" string="Date" 
                        context="{'group_by': 'date'}"/>
            </group>
        </search>
    </field>
</record>
```

## View Inheritance (xpath)

**Always use xpath — never copy-paste entire views.**

```xml
<!-- Add field after existing field -->
<record id="view_sale_order_form_inherit" model="ir.ui.view">
    <field name="name">sale.order.form.inherit</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="custom_field"/>
        </xpath>

        <!-- Add to notebook -->
        <xpath expr="//notebook" position="inside">
            <page string="Custom Tab" name="custom_tab">
                <group>
                    <field name="custom_note"/>
                </group>
            </page>
        </xpath>

        <!-- Replace field -->
        <xpath expr="//field[@name='payment_term_id']" position="replace">
            <field name="payment_term_id" required="1"/>
        </xpath>

        <!-- Add before header field -->
        <xpath expr="//header" position="inside">
            <button name="action_custom" type="object" string="Custom Action"
                    class="btn-secondary" invisible="state != 'draft'"/>
        </xpath>

        <!-- Add inside page -->
        <xpath expr="//page[@name='order_lines']//field[@name='order_line']//tree" 
               position="inside">
            <field name="custom_line_field"/>
        </xpath>
    </field>
</record>
```

### XPath Position Values

| Position | Effect |
|---|---|
| `after` | Insert after matched element |
| `before` | Insert before matched element |
| `inside` | Insert as last child |
| `replace` | Replace matched element |
| `attributes` | Modify attributes |

### XPath Attribute Modification

```xml
<xpath expr="//field[@name='price_unit']" position="attributes">
    <attribute name="readonly">1</attribute>
    <attribute name="required">1</attribute>
</xpath>
```

## Actions

### Window Action

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form,kanban</field>
    <field name="search_view_id" ref="view_my_model_search"/>
    <field name="context">{'search_default_draft': 1}</field>
    <field name="domain">[('active', '=', True)]</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first record
        </p>
    </field>
</record>
```

### Act Window with Wizard

```xml
<record id="action_my_wizard" model="ir.actions.act_window">
    <field name="name">Run Wizard</field>
    <field name="res_model">my.model.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>  <!-- opens in modal -->
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">list</field>
</record>
```

### Server Action

```xml
<record id="action_server_my_action" model="ir.actions.server">
    <field name="name">Run Server Action</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">
        if records:
            records.action_custom()
    </field>
    <field name="binding_model_id" ref="model_my_model"/>
</record>
```

## Menus

```xml
<!-- Top-level menu -->
<menuitem id="menu_my_model_root" 
          name="My Module" 
          web_icon="my_module,static/description/icon.png"
          sequence="10"/>

<!-- Sub-menu -->
<menuitem id="menu_my_model_main" 
          name="Main" 
          parent="menu_my_model_root"
          sequence="1"/>

<!-- Action menu -->
<menuitem id="menu_my_model_action" 
          name="My Models" 
          parent="menu_my_model_main"
          action="action_my_model"
          sequence="10"/>
```

## Common Widgets

| Widget | Field Type | Purpose |
|---|---|---|
| `statusbar` | Selection | State progress bar (header) |
| `monetary` | Monetary/Float | Currency-formatted number |
| `many2many_tags` | Many2many | Tag-style display |
| `many2many_badges` | Many2many | Badge-style display |
| `many2many_avatar_*` | Many2many | Avatars for partners/users |
| `statinfo` | Integer | Stat button info |
| `image` | Binary/Image | Image preview |
| `html` | Html | Full HTML editor |
| `date` / `datetime` | Date/Datetime | Date picker |
| `float_time` | Float | Time picker (HH:MM) |
| `url` | Char | Clickable URL |
| `email` | Char | Clickable email |
| `phone` | Char | Clickable phone |
| `progress_bar` | Float | Progress visualization |
| `percentpie` | Float | Pie chart percentage |
| `label_selection` | Selection | Colored label |
| `toggle` | Boolean | Toggle switch |
| `priority` | Selection/Integer | Star priority |
| `handle` | Integer | Drag-reorder handle |
| `many2one_barcode` | Many2one | Barcode scanning |

## Conditional Visibility (Domains in Views)

```xml
<!-- invisible attribute (static or dynamic) -->
<field name="done_date" invisible="state != 'done'"/>
<field name="cancel_reason" invisible="state != 'cancel'"/>

<!-- attrs (v14+) -->
<field name="partner_id" attrs="{'invisible': [('type', '=', 'internal')]}"/>
<field name="internal_code" attrs="{'readonly': [('state', '!=', 'draft')]}"/>

<!-- column_invisible (in tree) -->
<field name="internal_notes" column_invisible="1"/>
<field name="create_date" column_invisible="parent.type == 'internal'"/>
```
