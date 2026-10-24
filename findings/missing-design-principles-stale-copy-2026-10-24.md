# `design-principles.md` "faltante": copia vieja del skill, no archivo ausente

Fecha: 2026-10-24. Estado: **deuda registrada; requiere limpieza, no corrección de producto.**
Origen: sesión del otro proyecto activo (reporte del architect: «esa ruta no existe en `~/clawd/skills/cdad-cycle/references/`»).

## Verificación

| Ubicación | Estado |
|---|---|
| `skills/cdad-cycle/references/design-principles.md` (repo) | **existe** |
| `~/.config/opencode/skills/cdad-cycle/references/design-principles.md` (instalado) | **existe** |
| `~/clawd/skills/cdad-cycle/references/` | **no existe**; esa copia es antigua (contiene `claude-code-delegation.md` y `opencode-delegation.md`, que el skill vigente ya no tiene) |

Las dos fuentes que citan la ruta —`sources/roles/architect.md:48` y `sources/roles/reviewer.md:48`— resuelven al skill instalado, no a `~/clawd/skills/`.

## Causa

El agent resolvió la ruta del skill a una **copia obsoleta** en `~/clawd/skills/cdad-cycle` y no a la instalada (`~/.config/opencode/skills/cdad-cycle`) ni al checkout. Al no encontrarla allí, declaró el archivo faltante.

## Impacto

El architect de esa sesión **no aplicó** el criterio de diseño canónico (`design-principles.md`), así que su comprobación del principio general/específico quedó más débil. No hay efecto sobre contratos ni sobre el estado: el archivo existe y los agentes instalados lo citan.

## Acción propuesta (dueño)

1. Archivar o eliminar la copia vieja `~/clawd/skills/cdad-cycle` (o marcarla como no instalable) para que nadie resuelva rutas contra ella.
2. Si se conserva, que un `README` diga que es histórica y cuál es la ruta vigente.

**No** se corrige el producto: la ruta citada es correcta y el archivo existe en las dos ubicaciones vigentes.
