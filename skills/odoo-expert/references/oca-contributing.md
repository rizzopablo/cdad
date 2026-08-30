# OCA — requisitos para publicar y colaborar

Fuente: `OCA/odoo-community.org` (`website/Contribution/CONTRIBUTING.rst` y
`oca_repository_policy.rst`), consultado 2026-08-30. Ante la duda, el repo manda.

## Mensajes de commit

Formato: `[TAG] module_name: descripción breve`

- Resumen ≤ 50 caracteres, **sin prefijo antes del tag**; líneas de cuerpo ≤ 80.
- **Inglés**, presente imperativo: "Fix formatting", no "Fixes" ni "Fixed".
- Debe decir **qué módulo** toca y **por qué** el cambio.

| Tag | Uso |
|---|---|
| `[ADD]` | módulo o funcionalidad nueva |
| `[FIX]` | corrección de bug |
| `[IMP]` | mejora de algo existente |
| `[REF]` | refactor sin cambio funcional |
| `[MIG]` | migración de versión |
| `[REM]` | eliminación |

**Prohibido:**

- Commits de una palabra ("bugfix", "improvements").
- Commits tipo "Fix pep8", "Code review", "Add unittest" **encima** de un commit
  de feature — eso va dentro del commit que corresponde.
- Un commit que toque **varios módulos** a la vez: se parte en uno por módulo.

## Nombres

**Módulos** — minúsculas y guiones bajos, en **singular** (salvo que el modelo
Odoo ya sea plural, p.ej. `mrp_operations_*`):

| Caso | Prefijo | Ejemplo |
|---|---|---|
| Base para otros módulos | `base_` | `base_location_nuts` |
| Localización | `l10n_CC_` (CC = código de país) | `l10n_es_pos` |
| Extiende un módulo Odoo | `<modulo_odoo>_` | `mail_forward` |
| Combina Odoo + OCA | el nombre de Odoo primero | `crm_partner_firstname` |

**Repositorios** — con guiones, no guiones bajos (`l10n-belgium`,
`connector-magento`). Nunca "odoo" ni "openerp" en el nombre.

**Archivos** — solo `[a-z0-9_]`. Permisos: directorios 755, archivos 644.

## Versión en el manifest

Versión mayor de Odoo + `x.y.z` del módulo: el primer release de un módulo para
19.0 es `19.0.1.0.0`.

## Qué exige un módulo antes de mergear

**Manifest**

- Sin claves vacías.
- `license` e `images` presentes.
- `author` termina con `Odoo Community Association (OCA)`.
- `website` apuntando al repo: `https://github.com/OCA/<repo>`.

**Documentación**

- `README.rst` explicando propósito, instalación y uso.
- Dependencias externas documentadas en la sección de instalación.
- Descripción según el template, **sin secciones vacías**.
- **Sin logos ni branding de empresa** — se acredita en autores/contribuidores.

**Código**

- PEP8 (flake8) y guidelines OCA de Python, XML, JavaScript y CSS.
- Todos los tests en verde.

**Tests**

- Test unitario para funcionalidad nueva.
- Test de regresión para cada bugfix.
- **Sin depender de demo data.**
- Cobertura igual o mejor que antes.

**Dependencias**

- Externas en `external_dependencies` del manifest.
- Paquetes Python en `requirements.txt`.
- Dependencias OCA en `oca_dependencies.txt`.
- **Sin pinear versiones exactas.**

**Migraciones**

- Un cambio incompatible exige script de migración.
- Migrar entre versiones mayores de Odoo: script o nota en el README.

**Traducciones**

- Un PR **nunca** modifica `.po` directamente: eso es responsabilidad de Weblate.
- Excepción: un módulo nuevo puede traer sus propios `.po`.

## Proceso de revisión

- Hacen falta **dos cosas distintas**: revisión de código y prueba funcional.
- Al menos una aprobación debe ser de un miembro del PSC o con permiso de
  escritura en el repo. Se puede convocar a `@OCA/core-maintainers`.
- Mergean personas con permiso de escritura, preferentemente Core Maintainers,
  respetando al autor (`--author`) y su mensaje de commit.
- Un PR sin actividad por **6 meses** puede cerrarse.

**Checklist del revisor:** ¿es lo bastante genérico para la comunidad? ¿no
duplica otro módulo OCA? ¿está documentado? ¿el enfoque es correcto? ¿hay casos
de uso? ¿no hay configuración hardcodeada? ¿trae demo data? ¿los commits están
limpios?

**Tono:** agradecer primero, ser cordial, explicar el motivo de cada pedido.

## Política del repositorio OCA

Un módulo en nivel **Stable** o **Mature** debe cumplir tres cosas:

1. **Calidad** — pasa los checks automáticos y fue revisado por pares.
2. **Estabilidad** — no rompe instalaciones existentes ni módulos dependientes
   de la misma versión de Odoo.
3. **Relevancia** — genérico, y sin solaparse significativamente con módulos OCA
   que ya existen.

En **Alpha** y **Beta** el criterio se relaja (basta con los checks automáticos)
para no frenar a quien recién contribuye. El código de incubación abandonado se
borra.

Cada repositorio tiene un **PSC** (Project Steering Committee) responsable, que
decide excepciones de nombres y organización.
