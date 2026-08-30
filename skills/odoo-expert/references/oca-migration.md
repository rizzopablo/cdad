# OCA — migrar un módulo entre versiones de Odoo

Fuente: `OCA/maintainer-tools` wiki, "Migration to version 17.0", consultado
2026-08-30. **El procedimiento es genérico**; la tabla de APIs deprecadas es
específica de cada salto de versión — verificá la wiki del target antes de migrar.

## Antes de empezar

1. Repasar las convenciones OCA vigentes (`oca-contributing.md`).
2. Suscribirse a la lista del proyecto.
3. **Anunciar la intención en el issue de migración** del repo. Evita trabajo
   duplicado: alguien más puede estar migrando el mismo módulo.
4. Instalar `pre-commit`.

## Procedimiento git (preserva la historia)

```sh
git clone https://github.com/OCA/$repo -b $NEW
cd $repo
git checkout -b $NEW-mig-$module origin/$NEW

# traer la historia del modulo desde la version anterior, no copiar archivos
git format-patch --keep-subject --stdout origin/$NEW..origin/$OLD -- $module | git am -3 --keep

# 1er commit: solo el formateo automatico, aislado del trabajo de migracion
pre-commit run -a
git add -A
git commit -m "[IMP] $module: pre-commit auto fixes" --no-verify

# ... adaptaciones de codigo ...

git add --all
git commit -m "[MIG] $module: Migration to $NEW"
git push $user_org $NEW-mig-$module --set-upstream
```

**Por qué `format-patch` y no copiar:** preserva autoría e historia del módulo,
que es lo que exige OCA. Copiar archivos pierde el rastro de quién escribió qué.

**Título del PR:** `[$NEW][MIG] <module>: Migration to $NEW`

## Qué actualizar siempre

- **Versión del manifest** → `$NEW.1.0.0`.
- **Borrar la carpeta `migrations/`** de la versión anterior.
- Revisar `README.rst` y dependencias.

## Qué NO tocar

**No cambies años de copyright ni autores originales** en los encabezados.
La migración agrega un autor, no reemplaza a los anteriores.

## APIs deprecadas — ejemplo del salto 16.0 → 17.0

Ilustra el *tipo* de cambio a buscar. Para otro salto, consultá su wiki.

| Antes | Ahora |
|---|---|
| `name_get()` | sobreescribir `_compute_display_name` |
| `get_resource_path` | `file_path` |
| hooks con `cr, uid` | reciben `env` |
| `active_id` en contexto | `id` |
| `active_model` en contexto | nombre del modelo hardcodeado |
| `attrs` y `states` en XML | expresiones Python en `invisible`, `required`, `readonly` |
| `readonly=True` en el modelo | definir `readonly` en la vista |
| `invisible="1"` en tree | `column_invisible="1"` |
| `owl="1"` en templates | se elimina |

**Vistas de settings:** `<div class="app_settings_block">` → `<app>`;
`o_settings_container` → `<block>`; `<h2>` → atributo `title` del `<block>`;
`o_setting_box` → `<setting>`; se eliminan `o_setting_right_pane` /
`o_setting_left_pane`.

## Tests en una migración

- Usar `BaseCommon` como clase base.
- **Mockear peticiones HTTP externas** — un test no debe salir a la red.
- Aprovechar para subir cobertura: la migración es el momento en que alguien
  vuelve a leer el módulo entero.
