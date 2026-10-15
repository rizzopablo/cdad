# ADR-025: La orientación al retomar es una proyección read-only del estado y el encargo de tarea trae su contrato aplicable

- **Status**: Proposed
- **Date**: 2026-10-12
- **Deciders**: orquestador OpenCode (HITL delegada epic-005) + architect
- **Confidence**: Media
- **Aprobación**: orquestador OpenCode bajo la delegación HITL del epic-005
  (`docs/epics/epic-005-real-operation/execution.md`), con evidencia (spec aprobada `d630fdf9…`, review
  formal 0 blocking, focales de la feature). El architect no aprueba su propia propuesta. **La
  confianza es Media porque la aceptación de uso real está pendiente del despliegue** (bloqueo
  declarado): la decisión está implementada y revisada, pero su efecto medido sobre una sesión real
  nueva no está verificado.

## Contexto y problema

El estado operativo (`docs/.cdad-state.json`) medía **320.880 B**, de los cuales el `stage_history`
era **304.075 B = 94,8 %**: el orquestador pagaba dos órdenes de magnitud de contexto para leer un
puñado de campos operativos al retomar (caso S-BOOT-04: 215.292 caracteres leídos del estado). Además,
al despachar una tarea de un plan aprobado, el rol necesitaba releer la spec entera para conocer sus
comandos de validación y las postcondiciones aplicables. ¿Cómo se sirve la orientación con contexto
acotado **sin** migrar el formato del estado ni crear una segunda memoria, y **sin** obligar a releer
el contrato completo?

## Opciones consideradas

### Opción A: proyección read-only del estado existente + encargo autosuficiente aditivo
- Pros: no toca el formato del estado ni a sus consumidores; el historial se consulta selectivamente;
  el contrato neutral sobrevive; el paquete de tarea deja de exigir releer la spec.
- Contras: hay que mantener la proyección y sus límites; el contrato del paquete gana un modo aditivo
  que hay que probar (byte-identidad sin la opción); el calificador fino de «trabajo pendiente» no es
  implementable con las fuentes declaradas (deuda F2, propuesta al dueño).

### Opción B: migrar el estado — separar el `stage_history` a un archivo aparte / adelgazar el estado
- Pros: el estado en disco queda chico; una sola lectura basta.
- Contras: cambia el documento de estado y obliga a mantener compatibilidad de **todos** los
  consumidores (`prepare`, `validate-state`, `_approved_spec_entries`, la continuidad con `fields`
  proyectados); movería bytes fuera del alcance del pin del checkpoint (`head.json`); el insumo del
  dueño lo prohíbe explícitamente («no convertir esta optimización en una reescritura obligatoria del
  sistema de estado»).

### Opción C: mantener la lectura completa del estado (statu quo)
- Pros: cero código nuevo.
- Contras: no reduce el contexto; el coste de orientación sigue siendo el 94,8 % del estado.

## Decision

La orientación se sirve con **(A1)** una **proyección read-only generada por código** desde las
fuentes existentes (`compact-view-v1`), acotada por un **límite de bytes normativo con fallo cerrado**,
que **no emite el historial** y deja el estado **byte-idéntico**; y **(A2)** un **contrato aplicable
del encargo** (`packet-contract-v1`) **aditivo**: el paquete de una tarea **rinde los comandos de
validación de esa tarea desde el bloque canónico `plan-tasks`** del plan aprobado, las referencias al
contrato y la regla de cuándo ampliar, de modo que **no sea obligatorio releer la spec entera**.

## Reasons

1. El coste lo paga el agente que lee a contexto, no el CLI: una proyección de salida lo resuelve sin
   migrar el formato ni tocar a los consumidores.
2. Separar el historial obligaría a cambiar el documento de estado, mantener compatibilidad de todos
   los consumidores y mover bytes fuera del pin del checkpoint (prohibido por el insumo del dueño).
3. El bloque `plan-tasks` del plan aprobado **ya** es la fuente canónica de los comandos por tarea; el
   paquete puede rendirlo **por provenance** (comparado con lo parseado, no con texto a mano), en vez
   de exigir arqueología de la spec.
4. La extensión es **aditiva y declarada**: sin la tarea declarada el paquete se emite byte-idéntico y
   el conjunto cerrado de campos solo se **extiende** con una propiedad opcional (una clave
   desconocida sigue rechazándose).

## Consequences

**Positivas:**
- El orquestador retoma con un documento de pocos KB (1.679 B medidos sobre el proyecto real) en lugar
  del estado completo; el historial se consulta solo ante una duda concreta.
- El rol recibe su contrato aplicable en el paquete y no rearma la spec entera.
- La vista es determinista y read-only; no puede escribir el estado ni aprobar nada.

**Negativas / trade-offs:**
- Hay que mantener la proyección y su límite; el `entry` depende de campos existentes y su calificador
  fino no es implementable hoy (deuda F2, decisión de contrato propuesta al dueño).
- Cambiar un asset de instrucción **invalida** los paquetes publicados antes del cambio (consecuencia
  inherente al contrato de paquete; deuda F3, declarable con su camino legítimo).
- El `--replace-packet` con tarea declarada no tiene oráculo de test (deuda F7; verificado por sonda).

**Neutrales:**
- El medidor sigue sin estar instalado (ausencia, no incoherencia); el despliegue es del dueño.
- Las bandas numéricas de aceptación son **orientación derivada**, no umbrales automáticos.

## Notas

- Contrato normativo: `docs/specs/005-003-orientation-reduction/spec.md` (§2.1–§2.9, PD-1..PD-12,
  INV-1..INV-10); plan: `docs/specs/005-003-orientation-reduction/plan.md` (tareas T1..T6, bloque
  `plan-tasks`); contrato de la feature: fila 8 **enmendada y aprobada** del plan del epic-005
  (`b22bc687…`).
- Análogo a **ADR-016** (proyección on-demand) y **ADR-024** (instrumento read-only no-gate);
  frontera con ADR-013/ADR-019/ADR-020 (contrato, aprobación por rol, política de evidencia).
- **Deuda asociada:** `docs/specs/005-003-orientation-reduction/debt.md` (F2 propuesto al dueño;
  F3/F4-bis/F5/F6/F7 a deuda con condición de cierre).
- **Límite honesto:** la aceptación de uso real (A1/A2/A6/A9 y la observación de A8) está **pendiente
  del despliegue** (`acceptance.md` §7, bloqueo declarado).
