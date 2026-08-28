# Módulo de prueba CDAD×Odoo — `idea_log`

> **Propósito:** sujeto de prueba compartido para validar (1) los entornos `make`
> de odoo.sh y de un staging privado, y (2) el framework Odoo-CDAD (F1). Un solo módulo, mismos
> gates, dos entornos → comparación limpia.
> **Principio:** suficientemente completo para ejercitar todos los gates de
> calidad (estructura OCA, ORM, seguridad, vistas, data/demo, tests), sin nada
> más que eso. Sin dependencias pesadas: instala rápido, itera rápido.
> **Status:** borrador para revisión (no commitear sin aprobación).

## Dominio

"Registro de ideas": capturar ideas, puntuarlas, votarlas, seguir su estado.
Dominio neutro, sin referencias a ningún producto/infra, publicable tal cual.

- Módulo: `idea_log` (minúsculas, `[a-z0-9_]`, forma singular — convención OCA)
- Modelos: `idea.log` (principal) + `idea.vote` (línea relacional)
- Dependencia: `base` + `web` (web es requisito del helper `Form` en tests — verificado en spike F2: `NotImplementedError: onchange() is implemented in module 'web'`)

## Estructura de archivos (OCA-compliant)

```
idea_log/
├── __init__.py                      # import models
├── __manifest__.py
├── models/
│   ├── __init__.py                  # idea_log antes que idea_vote
│   ├── idea_log.py                  # model idea.log
│   └── idea_vote.py                 # model idea.vote
├── security/
│   ├── idea_log_security.xml        # grupo idea_log.group_reviewer
│   └── ir.model.access.csv          # ACLs (después del xml en 'data')
├── data/
│   └── idea_sequence.xml            # ir.sequence para idea.code
├── demo/
│   └── idea_log_demo.xml            # 2-3 ideas + votos (solo modo demo)
├── views/
│   ├── idea_log_views.xml           # tree + form + search + 1 vista heredada
│   └── idea_log_menus.xml           # action + menús
├── tests/
│   ├── __init__.py
│   └── test_idea_log.py
├── readme/
│   ├── DESCRIPTION.rst
│   ├── USAGE.rst
│   └── CONTRIBUTORS.rst
└── README.rst                       # normalmente generado (oca-gen-addon-readme)
```

## Manifest (claves con propósito)

```python
{
    "name": "Idea Log",
    "summary": "Capture ideas, score them and track their status",
    "version": "19.0.1.0.0",          # <odoo>.<maj>.<min>.<patch> — C8106
    "category": "Productivity",
    "author": "<Author Name>",         # placeholder público
    "website": "https://github.com/<org>/<repo>",  # placeholder
    "license": "LGPL-3",
    "development_status": "Beta",
    "depends": ["base"],
    "data": [
        "security/idea_log_security.xml",   # ⚠ orden importa: grupos antes que CSV
        "security/ir.model.access.csv",
        "data/idea_sequence.xml",
        "views/idea_log_views.xml",
        "views/idea_log_menus.xml",
    ],
    "demo": ["demo/idea_log_demo.xml"],
    "application": False,
    "installable": True,
}
```

Detalle deliberado: `ir.model.access.csv` referencia `idea_log.group_reviewer`
(definido en el XML), por eso el XML va primero en `data`. Es un gotcha real de
Odoo que los gates deben poder atrapar.

## Modelos

### `idea.log`
| Campo           | Tipo       | Detalle                                                             |
| --------------- | ---------- | ------------------------------------------------------------------- |
| `code`          | Char       | autogenerado por secuencia (`default=lambda self: next_by_code`)      |
| `name`          | Char       | required, index=True, translate=True                                  |
| `description`   | Text       |                                                                     |
| `status`        | Selection  | draft / submitted / accepted / rejected / implemented; default draft |
| `score`         | Integer    | 1..10, **constrain** (ValidationError fuera de rango)                 |
| `effort`        | Selection  | quick(1) / medium(2) / large(3)                                     |
| `weighted_value`| Integer    | **computed store=True**: score × peso(effort); `@api.depends('score','effort')` |
| `accepted_date` | Date       | readonly, seteada por `action_accept()`                               |
| `vote_ids`      | One2many   | → `idea.vote.idea_id`                                                 |
| `total_votes`   | Integer    | computed: len(vote_ids) — `@api.depends('vote_ids')`                  |
| `net_score`     | Integer    | computed: ups − downs — `@api.depends('vote_ids.vote_type')`          |
| `rejected_reason`| Char      | **groups='idea_log.group_reviewer'** (seguridad a nivel campo)        |

Método: `action_accept()` → `ensure_one()`, setea `status='accepted'` y
`accepted_date = fields.Date.context_today(self)`.
Métodos compute nombrados `_compute_<field>`; constrain `_check_score`.

### `idea.vote`
| Campo        | Tipo      | Detalle                                             |
| ------------ | --------- | --------------------------------------------------- |
| `idea_id`    | Many2one  | `idea.log`, required, ondelete='cascade', index=True |
| `voter_name` | Char      |                                                     |
| `vote_type`  | Selection | up / down                                           |

## Seguridad

- **Grupo**: `idea_log.group_reviewer` (implied by `base.group_user` o standalone — decidir en implementación; sugerido: independiente, para que el test de field-level sea más fuerte).
- **ACL CSV**: `idea.log` y `idea.vote` — lectura para `base.group_user`,
  escritura/creación para `base.group_user`; unlink restringido a reviewer
  (ejercita perm_unlink diferenciado).
- **Field-level**: `rejected_reason` solo `group_reviewer` (AccessError para
  usuario base — testeable y determinístico).
- **Fuera de alcance**: record rules (`ir.rule`) — se agregan solo si F1 las
  necesita; hoy aportarían complejidad a todos los tests sin beneficio para el
  objetivo.

## Vistas

- **Tree**: code, name, status (con decoration), score, weighted_value, total_votes.
- **Form**: statusbar en status, notebook con página de votos (tree editable).
- **Search**: filtros por status, group by effort.
- **1 vista heredada** (ejercita xpath + checks XML de OCA): agrega un campo o
  hint al tree view.

## Data vs Demo

- **`data/`**: `ir.sequence` (código `idea.log`, prefijo `IDEA`) — data
  operativa real, se carga siempre.
- **`demo/`**: 2-3 ideas con votos — artefacto de demostración, solo modo demo.
  Su gate es la **instalación con demo en DB limpia** (`make test-clean`): si
  la data demo tiene referencias rotas o evals inválidos, la instalación falla.
- **Regla**: los tests NUNCA dependen de demo data (OCA + Odoo oficial) — cada
  test crea sus fixtures.

## Tests (8 — cada uno mapea a una postcondición o riesgo)

| # | Test | Qué valida | Técnica |
|---|------|------------|---------|
| 1 | `test_create_defaults` | name requerido; code autogenerado por secuencia; status draft | TransactionCase |
| 2 | `test_weighted_value` | fórmula score×peso y recompute al cambiar score/effort | stored computed |
| 3 | `test_score_constraint` | score 0 y 11 → ValidationError; 1 y 10 OK | `@api.constrains` |
| 4 | `test_action_accept` | status accepted + accepted_date = context_today | action + ensure_one |
| 5 | `test_votes_aggregate` | total_votes = len(votes); net_score = ups − downs | computed sobre o2m |
| 6 | `test_field_security` | user base → AccessError en rejected_reason; reviewer → OK | `new_test_user` + `with_user().sudo(False)` |
| 7 | `test_form_create` | crear idea + voto vía Form y assert estado guardado | `odoo.tests.Form` |
| 8 | `test_install_demo` (gate externo) | demo data carga sin error en DB limpia | `make test-clean` (no es test Python) |

Todos `@tagged` explícitos (sin tag no corren), fixtures propias, sin fechas
dinámicas (accepted_date usa context_today → testeable con fecha fija).

## Especificación en formato CDAD (puente a F1)

**Postcondiciones (verificables por test):**
1. Crear idea con `name` produce `code` autogenerado y `status='draft'`.
2. `weighted_value = score × weight(effort)` y se recomputa ante cambios de `score`/`effort`.
3. `score ∉ [1,10]` → ValidationError.
4. `action_accept()` (una idea) → `status='accepted'` y `accepted_date` = fecha del contexto.
5. `total_votes = |vote_ids|`; `net_score = #up − #down`.
6. Usuario sin `group_reviewer` recibe AccessError al leer/escribir `rejected_reason`; reviewer puede.
7. Instalación con demo data en DB limpia termina sin error y con los registros demo presentes.

**Invariantes:**
- `status` ∈ {draft, submitted, accepted, rejected, implemented} (enforced por Selection).
- `score` es None o 1..10 (enforced por constrain).

**Criterios de aceptación (para F2/F3):**
- `make test`, `make test-one TEST=idea_log:TestIdeaLog.test_score_constraint` y
  `make test-clean` verdes en el entorno, con output de resumen pegado.
- pylint-odoo (mandatory) y oca-checks sin errores.
- El módulo no referencia nada privado: publicable tal cual.

## Fuera de alcance (explícito)

onchange, record rules, mail.thread, i18n/.pot, icon.png, wizards, reports,
tests post_install, property tests. Todo listado como extensiones futuras si F1
los requiere.

## Supuestos a verificar en F0 (Discovery de entornos)

- Versión de Odoo soportada por cada entorno (asumido 19.0 — ajustar manifest si difiere).
- Acceso a postgres / creación de DBs de test en cada entorno.
- En odoo.sh: cuánto del gate es CLI local y cuánto es push + CI de plataforma.

## Hallazgos del spike F2 (odoo.sh) — verificados 2026-08-28

1. **Odoo 19: `res.groups.category_id` ya no existe.** Reemplazado por
   `privilege_id` → `res.groups.privilege` (que tiene `category_id` a
   `ir.module.category`). XML de seguridad correcto: categoría →
   `<record model="res.groups.privilege">` → grupo con `<field
   name="privilege_id" ref="..."/>`. Verificado en source del addon base.
2. **Odoo 19: el tag `<tree>` se renombró a `<list>`.** "Invalid view type:
   'tree'. Allowed types are: list, form, graph...". Los xml_ids pueden
   seguir llamándose `*_view_tree` (son identificadores).
3. **`Form` en tests exige `web` instalado** → `depends` incluye `web`.
4. **`-i` sobre módulo ya instalado es no-op** (0 tests). Para reinstalar en
   una DB existente: resetear estado `to install` vía SQL y correr `-i`
   (mecanismo de `test-clean` en odoo.sh). En DB nueva (staging privado) esto no aplica:
   dropdb/createdb + `-i`.
5. **Drift de esquema del build dev de odoo.sh**: la DB tenía la columna
   `res_users_settings.color_scheme` NOT NULL sin default, pero el campo no
   existe en el código actual (fue de `web_enterprise` en otra revisión).
   Cualquier creación de usuario interno fallaba (rompe `new_test_user`).
   Workaround de spike: `ALTER TABLE ... SET DEFAULT 'light'`. Se resuelve
   de raíz con rebuild de la plataforma (DB nueva). Lección: en odoo.sh,
   ante estados raros de la DB dev, el rebuild es la herramienta de clean.
6. **scp no funciona en odoo.sh** (subsistema restringido); transferir
   archivos vía `tar` por stdin sobre SSH funciona.
7. Los 3 targets `make test` / `test-one` / `test-clean` corren verdes en la
   instancia (7/7 tests, 3 registros demo cargados en `test-clean`).
