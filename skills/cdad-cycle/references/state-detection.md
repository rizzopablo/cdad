# State Detection

Lógica para determinar en qué etapa del ciclo CDAD está el proyecto y la feature activa.

## Algoritmo de detección

Aplicalo **en orden** y parate en la primera condición que coincide.

### Paso 1: ¿Existe `docs/.cdad-state.json`?

Si existe, leelo. La estructura mínima es:

```json
{
  "version": 1,
  "active_feature": "<feature-id>",
  "current_stage": "discovery|specification|tdd|review|merge|done",
  "tdd_substage": "red|green|refactor|properties|integration|null",
  "postconditions_status": { "1": "green|red|pending", ... }
}
```

Esa es la fuente de verdad. **Pero igual hacé un sanity check** contra los archivos reales del paso 2: si el state file dice `current_stage: tdd` pero no hay tests en el repo, está desactualizado y avisás al usuario.

### Paso 2: Si no existe state file, inferir desde archivos

Aplicá los siguientes checks en orden:

| Condición | Etapa inferida |
|-----------|---------------|
| No existe `docs/projectbrief.md` ni `docs/activeContext.md` | **bootstrap** (cargá `references/bootstrap.md`) |
| Existe Memory Bank pero `docs/specs/` está vacío o no existe | **discovery** (próxima feature por arrancar) |
| Existe `docs/specs/<feat>/spec.md` pero **sin marca de aprobación** | **specification** (en redacción/brainstorm) |
| Existe `docs/specs/<feat>/spec.md` aprobado, pero `tests/` no tiene tests para esta feature | **tdd**, sub-fase **red** (test-writer aún no escribió) |
| Tests para la feature existen pero fallan (RED real) | **tdd**, sub-fase **red→green** (listo para implementer) |
| Tests pasan (GREEN), pero faltan property tests si el spec los pedía | **tdd**, sub-fase **properties** |
| Tests + property tests verdes, pero falta E2E si el spec lo pedía | **tdd**, sub-fase **integration** |
| Toda la suite verde, pero no existe `docs/specs/<feat>/review.md` | **review** |
| Existe `review.md` con bloqueantes sin resolver (commits posteriores no los abordan) | **review** (loop con etapa 3) |
| Review limpio, suite verde, pero `docs/activeContext.md` no tiene entry para esta feature | **merge** (CI + Memory Bank update pendiente) |
| Memory Bank actualizado, feature mergeada | **done** |

### Paso 3: Detectar marca de aprobación del spec

Para distinguir spec aprobado vs. en draft, buscá **una de estas señales** en `docs/specs/<feat>/spec.md`:

1. Línea final del spec con formato: `Status: Approved by <X> on <YYYY-MM-DD>`
2. Frontmatter YAML con `approved_by: <X>` y `approved_at: <fecha>`
3. Commit message que diga `docs: approve spec for <feat>` (si tenés acceso a git log)

Si ninguna está → tratá como NO aprobado.

### Paso 4: Detectar feature activa

El campo `active_feature` del state file gana. Si no hay state file:

1. Si hay una sola carpeta en `docs/specs/` que no tiene `review.md` ni está marcada como done → esa es la activa.
2. Si hay varias en progreso → preguntale al usuario cuál es la activa antes de seguir.
3. Si no hay ninguna → activa es la próxima a crear.

### Paso 5: Verificar consistencia entre state file y archivos

Si state file dice una etapa pero los archivos reales sugieren otra, **el archivo gana** (es la realidad). Avisale al usuario:

> *"El state file decía `current_stage: review` pero los tests están rojos. Voy a corregir el state a `tdd:green` y arrancamos por ahí. ¿OK?"*

## Tests pasan / fallan — cómo verificarlo

Para determinar si los tests pasan o fallan:

1. Si tu entorno permite ejecución (`bash` disponible), corré la suite y leé el exit code.
2. Si no, pedile al usuario el output: *"¿Podés correr la suite y pegarme el resumen final? Necesito saber cuántos tests pasan y cuántos fallan."*
3. NO infiero "verde" porque el código compila ni porque el test "se ve bien". El verde se verifica empíricamente.

## Detección de Memory Bank

Mínimo para considerar Memory Bank inicializado:

- `docs/projectbrief.md` existe y no es solo placeholder.
- `docs/activeContext.md` existe.
- `docs/progress.md` existe.
- `docs/systemPatterns.md` existe (puede ser corto pero tiene contenido real).

Si falta cualquiera → bootstrap.

## Salida del paso

Después de aplicar la detección, comunicá al usuario en una sola frase corta:

> *"Estás en **<etapa>** trabajando en `<feature-id>`. <una frase con el próximo paso lógico>. ¿Avanzamos?"*

Y esperá su respuesta antes de continuar.
