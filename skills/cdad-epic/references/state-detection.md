# State Detection — Epic level

Lógica para detectar en qué etapa de epic está el proyecto.

## Algoritmo

Aplicalo en orden, parate en la primera condición que coincide.

### Paso 1 — ¿Existe `docs/.cdad-state.json`?

Si sí, leé los campos de epic:

- `active_epic`: id del epic activo, o `null`/ausente.
- `epic_stage`: `epic-discovery | epic-planning | features-loop | epic-integration | epic-closure | epic-done`.
- `epic_features`: lista de features del epic con su status (`done | in-progress | queued | blocked`).

Si `active_epic` es `null` o no existe el campo: no hay epic activo. El usuario está empezando uno nuevo o trabajando solo a nivel feature standalone.

### Paso 2 — Si no hay state file, inferir desde archivos

Buscar `docs/epics/`. Si existe:

- Carpeta más reciente sin `closure.md` → epic activo.
- Si tiene `plan.md` con marca de aprobación → epic está en `features-loop` o más adelante.
- Si tiene `plan.md` sin aprobar → `epic-planning`.
- Si tiene `decomposition.md` solo, sin `plan.md` → `epic-discovery`.
- Si tiene `integration.md` pero no `closure.md` → `epic-integration`.
- Si tiene `integration.md` con E2E verde y `closure.md` en draft → `epic-closure`.

### Paso 3 — Detectar progreso de features dentro del epic

Para cada feature listada en `epic_features` (o inferida desde `docs/specs/<epic-num>-*`):

- Buscar entry en `docs/progress.md`. Si está en "Done", marcar `done`.
- Si está en "In progress", marcar `in-progress`.
- Si no aparece, marcar `queued`.
- Si tiene marca de bloqueo, marcar `blocked`.

### Paso 4 — Detectar feature actualmente en desarrollo

Si `active_feature` está seteado en el state file y empieza con el prefijo del epic activo (`<epic-num>-...`), esa es la feature in-progress del epic.

Si `active_feature` está seteado pero NO pertenece al epic activo: el usuario está trabajando en una feature standalone en paralelo. Esto es válido pero conviene avisar:

> *"Detecté que estás trabajando en feature `<X>` pero no pertenece al epic activo `<epic-id>`. ¿Es feature standalone (en paralelo al epic) o querés cambiar el epic activo?"*

### Paso 5 — Salida

Comunicá al usuario en una sola frase:

> *"Estás en el epic `<epic-id>`, etapa **<epic-stage>**. <X de Y features done>. Próximo paso: <propuesta>. ¿Avanzamos?"*

## Casos especiales

### Epic sin features definidas todavía

Si `epic_features` está vacío y `epic_stage` es `epic-planning`, el plan está incompleto. Volvés a Etapa E2 a completar la decomposición antes de avanzar.

### Epic con feature standalone que parece pertenecer

Ejemplo: hay epic `001-facturacion-afip` activo, y el usuario crea spec `005-validar-cuit` (sin prefijo de epic). Probable: el usuario olvidó usar la convención de naming del epic.

Preguntale:

> *"Veo que creaste spec `005-validar-cuit`. ¿Pertenece al epic `001-facturacion-afip`? Si sí, te sugiero renombrarla a `001-NNN-validar-cuit` para mantener trazabilidad. Si no, la trato como standalone."*

### Múltiples epics activos

CDAD-epic asume **un epic activo por vez**. Si detectás dos `active_epic` (no debería pasar, pero por error humano puede), avisás:

> *"Detecté dos epics marcados como activos. CDAD asume uno por vez. ¿Cuál es el activo realmente y cuál movemos a 'pausado'?"*

Para "pausado", agregás campo `epic_features[].status: paused` o un campo `paused_epics: []` al state.

## Sanity check entre state y archivos

Si state dice `epic_stage: features-loop` pero `docs/epics/<id>/plan.md` no existe: state desactualizado. Avisás:

> *"State decía 'features-loop' pero falta `plan.md`. Voy a corregir a 'epic-planning' y arrancamos por ahí."*
