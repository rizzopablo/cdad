# Deuda priorizada — 005-003-orientation-reduction

Origen: **review formal de la etapa 4** (`review.md`, reviewer `mofgw/glm-5.3-flash`, **familia
distinta** a la del implementer `mofgw/deepseek-v4.1-flash`), con el **criterio de review vigente**
(2026-10-12, `docs/epics/epic-005-real-operation/execution.md`): **0 BLOCKING · 6 OPTIONAL · 7
abstenciones declaradas**. Los seis OPTIONAL van acá con su **condición de cierre verificable**; la
severidad del reviewer **no se relaja** y sus reproducciones propias se conservan en `review.md`.

## Disposición del orquestador (HITL delegada del epic-005)

| Hallazgo | Severidad | Disposición |
|---|---|---|
| **F1** — el plan declaraba un focal inexistente (`tests/test_005_003_t3_meter_no_write.py`) en la ficha de T3 y en el **bloque canónico `plan-tasks`** | OPTIONAL · m | **CORREGIDO YA** (ver abajo) |
| **F4** — `acceptance.md` citaba un identificador **crudo** de sesión (§2.9 pide referencia hasheada) | OPTIONAL · l (nit) | **CORREGIDO YA** (ver abajo) |
| **F2** — `_pending_work` no aplica el calificador de la spec §2.2 («estado distinto de `completed`») → `entry` falso en reposo con directorios de paquete históricos | OPTIONAL · m | **A DEUDA** con condición de cierre + **propuesta al dueño** |
| **F3** — cambiar un asset de instrucción (T6) invalida los paquetes publicados **antes** del cambio | OPTIONAL · m | **A DEUDA** con condición de cierre |
| **F4-bis** — la cobertura del oráculo de INV-6 es **parcial** (el test escanea solo `capabilities.md`) | OPTIONAL · l | **A DEUDA** con condición de cierre |
| **F5 / F6** — el verdicto de versión usa el `cdad-version-check.py` hermano del CLI en ejecución; la frase «the complete suite is the closure gate» persiste en `references/` | FYI · l | **A DEUDA** (notas, sin defecto material) |

### Corregido ya: F1 (reconciliación declarada, no silenciosa)

La ficha de T3 y el bloque `plan-tasks` del plan **aprobado** declaraban
`tests/test_005_003_t3_meter_no_write.py` como focal nuevo para las comprobaciones D11-(1)/(2). Ese
archivo **nunca existió**: las comprobaciones viven en `tests/test_005_003_t3_set_summary.py`
(`test_d11_1_*`, `test_d11_2_*`), y el GREEN de T3 lo **declaró** al volver (registrado también en
`acceptance.md` §1). El **orquestador** alineó el plan a la **spec** (PD-12 dice «el test focal nuevo
de T3», **singular**) y a lo entregado: se quitó el archivo inexistente de la ficha y del
`focal_tests` de T3 en el bloque canónico, y se dejó la reconciliación **declarada en la propia
ficha**. **Motivo de la corrección en el cierre y no en una ronda:** es una contradicción interna del
plan contra la spec (que prevalece), el desvío ya estaba declarado por el rol, y el bloque
`plan-tasks` es la **fuente que T6 renderiza** en cada paquete (dejarlo habría publicado un focal no
ejecutable). El bloque sigue **válido** para el validador del CLI (verificado). El plan cambió de
sha256: el state re-registra su pin.

**Condición de cierre (verificada):** `grep -c t3_meter_no_write plan.md` → **1**, y esa única
ocurrencia es la **nota de reconciliación** (ninguna declaración de archivo).

### Corregido ya: F4 (nit de privacidad)

El identificador crudo de la sesión del GREEN de T2 (primer intento) se reemplazó por su
**referencia hasheada** (`sha256:1934e5517e6087c4…`), como pide la spec §2.9.

**Condición de cierre (verificada):** `grep -rEn "\bses_[A-Za-z0-9]{6,}\b" docs/specs/005-003-orientation-reduction/` → **vacío**.

## Prioridad 1 — producto (comportamiento observable en un caso de borde válido)

### F2 — la selección de entrada no aplica el calificador declarado en reposo

- **Veredicto/bucket del reviewer:** OPTIONAL · m. **Procedencia:** `_pending_work`
  (`skills/cdad-cycle/scripts/cdad_packet.py`), spec §2.2, PD-2.
- **Qué pasa (reproducción propia del reviewer):** con `active_packet=null` y un directorio de
  paquete histórico bajo `.cdad/packets/`, la vista emite `entry = continuity-reconcile` y un `next`
  que apunta a una ejecución inexistente, donde la spec §2.2 dice «reposo sin trabajo pendiente →
  `next-unit`». La implementación cuenta **cualquier** directorio de paquete como pendiente, sin el
  calificador «con estado distinto de `completed`» que la spec declara.
- **Por qué no es bloqueante (juicio del reviewer, compartido por el orquestador):** el error **erra
  del lado seguro** (nunca omite trabajo pendiente; puede inventarlo), es **recuperable**
  (`continuity-reconcile` sin paquete/ejecución lleva a `resume` → `no-checkpoint` con `rc=0`, sin
  pérdida) y su alcance real es **no verificado** (abstención 5 del reviewer).
- **Por qué NO se corrige en el cierre:** el calificador **no es implementable con las fuentes que la
  spec declara** (los directorios `.cdad/packets/<id>/` portan `REQUEST.json` + `PACKET.md`, **sin
  estado propio**; el único estado de paquete vive en `active_packet`). La corrección honesta exige
  **o** añadir una fuente de estado por paquete **o** reconciliar la cláusula de la spec con la
  aproximación conservadora implementada. Ambas son **decisiones de contrato** y se **proponen al
  dueño** en vez de editarlas en el cierre.
- **Propuesta al dueño (dos opciones):** (a) reconciliar §2.2 declarando la regla implementada
  («un directorio de paquete publicado cuenta como pendiente mientras `active_packet` no diga lo
  contrario», con el motivo: la fuente por paquete no existe); o (b) abrir la fuente de estado por
  paquete y aplicar el calificador. **Condición de cierre verificable:** un test que, con
  `active_packet` ausente y un directorio de paquete **completado**, afirme `entry == "next-unit"`; o
  la declaración explícita de la aproximación en la spec/reference.

### F3 — cambiar un asset de instrucción invalida los paquetes publicados antes del cambio

- **Veredicto/bucket del reviewer:** OPTIONAL · m. **Procedencia:** `render_packet`
  (`skills/cdad-cycle/scripts/cdad_packet.py`), `packets/common.md`, `packets/roles/implementer.md`,
  `packets/substages/implementer-green.md` (T6).
- **Qué pasa (reproducción propia del reviewer, worktree en `009902b`):** un paquete preparado con
  los assets previos a T6 y validado en `HEAD` da `rc=2 ERROR: packet differs from canonical
  rendering`; el mismo paquete valida con el CLI previo. El paquete embebe los hashes y el **texto
  compuesto** de su instrucción, así que cambiar un asset lo invalida.
- **Juicio del reviewer (respondido a la pregunta del orquestador):** **no** compromete el resultado,
  la evidencia ni el uso previsto; es una **consecuencia inherente** al contrato de paquete y
  **exigida** por PD-10-(iv) (la feature no puede evitar tocar esos assets); el fallo es **ruidoso y
  recuperable** (re-preparar/reconciliar).
- **Condición de cierre verificable:** declarar la consecuencia y el **camino legítimo**
  (re-preparar o reconciliar un paquete en vuelo) en `references/re-entry.md` u
  `references/orientation.md`, nombrando que cambiar un asset de instrucción invalida los paquetes
  publicados antes del cambio. **No** requiere corregir el renderer.

## Prioridad 2 — proceso y cobertura

### F4-bis — la cobertura del oráculo de INV-6 es parcial

- **Veredicto/bucket del reviewer:** OPTIONAL · l. **Procedencia:** `test_inv6_*` de
  `tests/test_005_003_t4_capabilities_inventory.py` (escanea **solo** `capabilities.md`).
- **Por qué importa:** INV-6 («sin valores de este VPS») aplica a spec, plan y producto; el
  identificador crudo que apareció en `acceptance.md` (F4) **no** lo habría detectado ese test.
- **Condición de cierre verificable:** ampliar el chequeo de privacidad a los documentos de la
  feature (`docs/specs/<feature>/**`) además del producto, o declarar explícitamente su alcance
  acotado. Hoy `spec.md`, `plan.md` y el producto **cumplen** (verificado por el reviewer).

### F5 — el verdicto de versión usa el `cdad-version-check.py` hermano del CLI en ejecución

- **Veredicto/bucket del reviewer:** FYI · l. **Procedencia:** `_version_verdict`
  (`skills/cdad-cycle/scripts/cdad_packet.py`).
- **Qué pasa:** corriendo el CLI del repo, el verdicto es `UNKNOWN` (ausencia) — exactamente lo
  observado por la aceptación (`version.verdict=UNKNOWN` con causa). Es coherente con «la versión
  correspondiente al CLI cargado» y no es un defecto material.
- **Condición de cierre verificable:** ninguna (nota). Se documenta para que la aceptación real
  distinga el CLI del checkout del instalado al leer el verdicto.

### F6 — «the complete suite is the closure gate» persiste en `references/`

- **Veredicto/bucket del reviewer:** FYI · l. **Procedencia:** `references/stage-3-tdd.md`,
  `references/re-entry.md`, `references/handoff-prompts.md`, `references/anti-patterns.md`.
- **Qué pasa:** la política de la suite completa está declarada **una sola vez** en
  `packets/common.md` (y los assets de rol/subetapa la referencian, verificado por el oráculo de T6);
  la frase persiste en references, donde es **consistente** con «la corre quien cierra, al cierre» y
  queda **fuera del alcance declarado** por la spec §2.8-(c).
- **Condición de cierre verificable:** ninguna (nota); unificar la redacción si una feature futura
  toca la política de evidencia.

## Abstenciones declaradas (del reviewer, conservadas)

1. **Aceptación de uso real (A1/A2/A6/A8/A9):** requiere desplegar la versión y observar una sesión
   real nueva (reservado al dueño; prohibido en este tramo). Es el **bloqueo declarado** de
   `acceptance.md` §7.
2. **Suite completa:** no corrida por política; la corre quien cierra, una sola vez (el orquestador,
   en un worktree fijado al commit de cierre).
3. **Base real de sesiones:** nunca abierta (ni en lectura).
4. **Render de un paquete de T3 contra el repo real:** no ejecutado (habría escrito en `.cdad/`
   real); la conclusión de F1 es de lectura.
5. **Alcance real de F2:** la consecuencia observable está reproducida; la frecuencia real queda no
   verificada.
6. **Comportamiento contra la versión instalada:** no ejercido (F5).
7. **`--replace-packet` con `plan_task`:** sin oráculo de test; verificado con sonda propia del
   reviewer (funciona) → ver **F7** abajo.

### F7 — `--replace-packet` con `plan_task` no tiene oráculo de test (derivado de la abstención 7)

- **Origen:** abstención 7 del reviewer (sonda propia: conserva la tarea y **re-resuelve** el
  contenido desde el plan vigente; funciona).
- **Por qué queda en deuda:** el contrato lo declara (§2.8-(iv)) y la sonda lo confirma, pero **no hay
  test que lo proteja de regresión**.
- **Condición de cierre verificable:** un test que prepare con `--plan-task`, reemplace con
  `--replace-packet` y afirme que la tarea se conserva y que el contenido de validación se
  **re-resuelve** desde el plan vigente.
