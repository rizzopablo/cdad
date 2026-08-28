# Trampas de API Odoo 19 (verificadas 2026-08-28)

Hallazgos empíricos de la especialización Odoo, verificados en entornos reales
(odoo.sh y staging privado). Acumulá aquí las trampas de API nuevas que confirmes
al implementar; no las dupliques en otro lugar del repo.

## 1. `res.groups.category_id` → renombrado a `privilege_id` (Odoo 19)

En Odoo 19 el campo de agrupación de derechos cambió de nombre:
- **Antes (≤17):** `res.groups.category_id` — categoría que agrupa grupos.
- **Ahora (19):** `res.groups.privilege_id`, apuntando al modelo
  **`res.groups.privilege`**.

Al referenciar la agrupación de un grupo de seguridad (`security/` o en
código), usá el nombre nuevo. Cualquier referencia legacy
`category_id` / `res.groups.category` a un `res.groups` raíz típico del 17
falla o queda huérfana en 19.

## 2. Vista <list> en vez de <tree> (Odoo 19)

La etiqueta `<tree>` de las vistas de lista se renombró a **`<list>`**
(`<tree>` era la etiqueta histórica de `ir.ui.view` en versiones previas).
- **Antes (≤17):** `<tree>` en `views/*.xml`.
- **Ahora (19):** `<list>` (con atributos equivalentes: `editable`,
  `create`, `delete`, multiplies, etc.).

Un addon del 17 escrito con `<tree>` no carga su vista en 19; migrar a
`<list>` al portar.

## 3. Reconfirmado en el entorno de tests

Estas dos trampas se confirmaron al montar el entorno de test de la
especialización (contrato make): el `make test-clean` instala el módulo desde
cero y expone estos renombres de API como error de carga si un addon los usa
con el nombre viejo. El antídoto es versionar el addon contra la API 19
(`res.groups.privilege` + `<list>`).

## Relación con el drift de schema

El drift de schema en builds gestionados (rebuild de plataforma que deja
columnas fantasma, ver SKILL.md §Trampas) se suma a estas renombradas de API:
un addon que el build no re-instala desde cero puede quedar en un estado
intermedio (vista `<tree>` vieja + DB con schema nuevo). `make test-clean`
(instalación desde cero) es el detector real.