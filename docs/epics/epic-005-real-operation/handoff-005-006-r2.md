# Handoff al dueño — cerrar 005-006 (activación + R2 real)

Fecha: 2026-10-10. Estado: **005-006-guided-project-start tiene el ciclo técnico completo (etapa 5) y
queda `in-progress`** hasta que se cumplan las dos condiciones de abajo (F4 del review formal).

Los valores de esta instalación (rutas, raíz adoptada, proyecto de aceptación) están en el registro
local `.cdad/local/handoff-005-005.local.md` (fuera de git). No los infieras: si no lo tenés, pedíselo
al dueño.

## Por qué está bloqueada

1. **El producto instalado en HOME no contiene los textos nuevos.** El ciclo se desarrolló y se
   entregó en el repo; **desplegar es otra tarea** y está reservada al dueño (INV-7 de la spec,
   `execution.md`). Correr la aceptación sobre la instalación vigente sería correr con la versión
   vieja: violaría el criterio 2 del epic (una versión estable por ciclo, sin mezclas).
2. **La aceptación real R2 no es automatizable.** Es el arranque de un proyecto **existente
   parcialmente inicializado** elegido por el dueño; su resultado es comportamiento de una sesión
   nueva del orquestador, no un test unitario. Por eso queda como gate de integración orquestador +
   dueño (PD-16), y cierra el **VERIFY 5** del discovery.

## Condición 1 — activar la versión nueva (dueño)

- Entregable del ciclo: rama `codex/epic-005-real-operation`, commit de cierre técnico
  `44c1e83` (producto: `421ddf2`, `4d96905`, `8dd8c09`, `fe8d742`, `19d561e`).
- Al activarla, la comprobación esperada es `bash install.sh --check` **rc=0**. Hoy da **1 FAIL**
  (`validate-subagents.sh`) **precisamente porque la instalación de HOME todavía no tiene los textos
  nuevos** (`project-start.md` y los archivos tocados): es el drift F011 preexistente, no un defecto
  del diff.
- Recordá que el servidor permanente de OpenCode hereda el entorno del arranque: tras desplegar hay
  que **recargarlo** para que las sesiones nuevas tomen los agentes y las skills nuevos.

## Condición 2 — correr la R2 real (dueño + orquestador)

Proyecto de aceptación: el registrado en `.cdad/local/handoff-005-005.local.md` §005-006 (no se
publica en este repo).

1. Abrí una **sesión nueva** de OpenCode **en el directorio contenedor** del proyecto de aceptación
   (no necesariamente en su raíz CDAD: el arranque debe reconocer la raíz anidada).
2. Instrucción **breve**, sin ayudas: «usá CDAD para inicializar este proyecto y comenzar su análisis
   preliminar».
3. Observá, en este orden, los cinco puntos del recorrido esperado (son los que la feature promete):
   - **carga la metodología por iniciativa propia** (sin que se lo pidas): `cdad-cycle` primero;
   - **reconoce el proyecto y el estado** sin imponer layout ni buscar por todo el workspace;
   - **sincroniza el state con el plan aprobado** (si hay desfase en `epic_features`, lo **nombra** y
     encamina la sincronización; no inventa features);
   - **no ejecuta `resume`** si no hay ejecución activa;
   - **prepara el primer encargo con el CLI instalado** y lo **despacha**: la primera delegación útil.
4. Evidencia a registrar: la instrucción textual, los comandos que corrió, el paquete preparado
   (id + `REQUEST.json` válido) y el resultado de la delegación. Con eso se cierra **VERIFY 5**.

## Actualización 2026-10-10 — review-fix del dueño aplicado (ANTES de desplegar)

La revisión del dueño encontró tres defectos materiales que habrían hecho fallar la R2; están
corregidos y re-revisados (detalle: `docs/specs/005-006-guided-project-start/closure.md` §8 y
`review-owner-reviewfix.md`). Para el despliegue y la R2 esto cambia dos cosas concretas:

- **El cableado ya no usa `$CDAD_INSTALL_ROOT`**: usa `<skill-dir>` — el directorio que el runtime
  informa al cargar la skill (`Base directory for this skill: …`). El CLI queda alcanzable en
  cualquier proyecto consumidor.
- **Hay una comprobación única de versión**: `<skill-dir>/scripts/cdad-version-check.py`.
  Esperá `COHERENT` (rc=0) recién después de activar; en un checkout de desarrollo el veredicto
  correcto es `UNKNOWN` (rc≠0): solo `COHERENT` devuelve 0.

- **`project-start.md` ahora trae la receta concreta** del arranque (abrir la ejecución, `prepare`,
  los tres `validate-*`, `begin`, despachar) con sus argumentos, y una nota de trazabilidad: la
  spec aprobada (PD-10) fija el marcador viejo y se lee con la enmienda del cierre.

## Qué NO hace falta

- No hay que simular la R2 con fixtures: los recorridos R1 (proyecto nuevo) y R3 (configuración
  incompleta) ya están cubiertos por tests deterministas en `tests/test_005_006_t5_acceptance.py`.
- No hay que repetir la suite completa: el cierre técnico ya la corrió sobre el árbol final
  (`closure.md` §2).
- No hay que reabrir la review: 0 bloqueantes, F1 cerrado como review-fix.

## Después

Con (1)+(2) cumplidos: `epic_features[005-006].status = done` en `docs/.cdad-state.json` y el epic
sigue en `features-loop`. **Siguiente por prioridad: 005-002-session-context-meter**, que depende de
esta misma activación.
