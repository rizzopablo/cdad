# Cierre — 005-003-orientation-reduction

Octava feature del epic-005-real-operation. **Cerrada el 2026-10-12** (ciclo técnico completo), con
un **bloqueo declarado** que se explica en §6.

## 1. Resultado entregado

**Orientación acotada al primer despacho legítimo** sobre el proceso completo de delegación: el
orquestador llega a la próxima unidad con **contexto chico** y **sin reconstruir preventivamente** ni
la historia del proyecto ni la implementación del CLI, conservando autoridad, contratos, evidencia y
capacidad de orquestar. Seis piezas, todas **generadas por código desde fuentes existentes**:

1. **Vista compacta** `status` (read-only): proyección determinista del estado operativo; **no** emite
   `stage_history`; límite normativo **16.384 B con fallo cerrado** sin proyección parcial; diagnóstico
   de la asimetría de raíz relativa en la salida.
2. **Selección explícita de entrada** (`entry`: `continuity-reconcile` | `next-unit` | `diagnosis`):
   atiende primero un paquete pendiente; no depende de la palabra «inicializar»; sin campo nuevo en el
   estado.
3. **Interfaz operativa** (`references/orientation.md`) + **asset canónico de ejemplos ejecutables**
   (`assets/orientation-examples.json`): la utilidad no se verifica buscando frases.
4. **Disposición de versión y medidor**: ausencia ≠ incoherencia; «medidor no instalado» = ausencia.
5. **Resumen del conjunto** (`set-summary-v1`, aditivo) + **regla del documento multiplexado (R4)**;
   el registro neutral por sesión de 005-002 queda **byte-congelado**.
6. **Contrato aplicable del encargo** (`packet-contract-v1`, aditivo): con `--plan-task <ID>` el
   paquete rinde los **comandos de validación de esa tarea desde el bloque canónico `plan-tasks`** del
   plan aprobado, las referencias al contrato y la regla de cuándo ampliar; la **política de la suite**
   se declara una sola vez; el **cierre incluye el commit**.

Además: **inventario de capacidades efectivas** (`references/capabilities.md`) con fallback portable, y
el **paso de orientación por la vista** en el procedimiento canónico de arranque (`project-start.md`
§11, por referencia, sin copiar la estructura de los dueños).

## 2. Commits (rango `009902b..HEAD`, sin push)

| Unidad | Commits |
|---|---|
| T1 (vista + selección) | `2bdf314b` RED · `2bc159a3` GREEN |
| T2 (interfaz + versión + evidencia + arranque) | `350aa58` RED · `5e628de2` testfix firmado · `1810370` GREEN |
| T3 (resumen + R4 + **cierre de D11**) | `8b5673d` RED · `48d47f7` GREEN |
| T4 (capacidades, sin código) | `afd7fd4` RED · `b6e567b` GREEN |
| T6 (contrato del encargo) | `d805876` RED · `d45e627` GREEN |
| Corrección del cableado (gate de cierre) | `5316650` · `a13576f` |
| Docs/state | `1dd46c2`, `67514af`, `eda3299`, `6ea8065`, `bacb74b`, `ea9f94a`, `65e7caa`, `ddd6a62`, `5ad965d`, `8fe…`/`86fe768`, `ff153cf`, `04feda6`, `c4326bc`, `2dc000c`, `b573603` y el cierre |

**Todos los roles commitearon su producto**, salvo el **GREEN de T2 en su primer intento**, que
**bloqueó legítimamente** (oráculo mutuamente insatisfacible), **paró sin tocar tests ni commitear** y
se completó en un re-despacho que commiteó (§5).

## 3. Gates con números (verificación del orquestador)

| Gate | Resultado |
|---|---|
| RED T1 | **11 failed**, todas `AssertionError` de contrato (0 ERROR) |
| GREEN T1 | focal **11 passed**; regresión del área **131 passed** |
| RED T2 | **10 failed**, todas `AssertionError`; regresión de 005-006 **15 passed** |
| testfix T2 | focal **10 passed** (enmienda de oráculo **firmada**); área **133 passed** |
| GREEN T2 | focal **10 passed**; 005-006 **15 passed**; T1 **11 passed** |
| RED T3 | **5 failed / 4 passed**, todas `AssertionError`; regresiones de 005-002 **10 passed / 2 skipped** |
| GREEN T3 | focal **9 passed**; regresiones de 005-002 **22 passed / 2 skipped**; T1+T2 **21 passed**; **INV-5 verificado por bytes** (medidor `009902b` vs `HEAD` sin `--set-summary` → `cmp` igual) |
| RED T4 | **6 failed**, todas `AssertionError` |
| GREEN T4 | focal **6 passed**; focales T1+T2+T3 **30 passed** |
| RED T6 | **6 failed / 1 passed** (el que pasa ya estaba satisfecho: `commit` en la evidencia), todas `AssertionError`; área **113 passed** sin fallos nuevos |
| GREEN T6 | focal **7 passed**; focales de la feature **36 passed**; regresiones de 005-002 **10 passed / 2 skipped**; área **183 passed** sin fallos nuevos |
| **Gate de cierre (1.er intento)** | **1 failed / 845 passed / 4 skipped** → **el fallo es una regresión REAL de esta feature** (§4) |
| Corrección del cableado | oráculo A2 de 005-006 **5 passed**; grep de la clase **vacío** |
| **Suite completa de cierre (intento final)** | ver §4 |

## 4. El gate de cierre encontró una regresión real (y se corrigió)

**Primer intento** (`d45e627`, worktree fijado): **1 failed / 845 passed / 4 skipped**.

- **Fallo:** `tests/test_005_006_t6_owner_reviewfix.py::test_hallazgo_a2_cli_invocations_derived_from_skill_dir`
  — el **oráculo A2 aprobado en 005-006** exige que toda invocación del CLI en el **cableado** se
  escriba con el marcador explícito `<skill-dir>/scripts/cdad_*.py`. La sección §11 que agregó **T2**
  escribió `cdad_packet.py status` **sin** el marcador (`project-start.md:196`).
- **Disposición (una sola clase, un solo GREEN):** corregidos `project-start.md` §11 **y**
  `orientation.md` (frase inicial + tabla de operaciones) en `5316650`, y los **dos ofensores que el
  rol declaró sin tocar** (`orientation.md:69`/`:71`) plegados a la misma clase en `a13576f`.
  **Los tests no se tocaron**: el oráculo que manda ya existía.
- **Lección del gate:** la suite de cierre vio lo que los focales de la feature **no podían** ver —
  una regresión sobre un oráculo de **otra** feature. Es exactamente el motivo del gate.
- **`make validate` (mismo worktree):** **142 PASS / 1 FAIL** = **F011**
  (`scripts/validate-subagents.sh`), el **drift** de las copias instaladas en HOME: resolverlo exige
  **desplegar**, acción **reservada al dueño** y **prohibida** en este tramo → **desviación declarada**,
  no silenciosa (es el mismo FAIL del cierre original y de la reapertura de 005-002).
- **Suite completa del intento final** (`a13576f`, worktree **fijado** a ese commit; los commits
  posteriores son docs-only, así que el árbol de producto y tests es idéntico y la corrida es
  equivalente): `make staging` dentro del worktree **OK** (12 + 12 agentes) y
  **`846 passed, 4 skipped` — exit 0, 931,02 s (0:15:31)**. Comparación con el primer intento:
  845 passed / 4 skipped / **1 failed** → **846 passed / 4 skipped / 0 failed** (el único test que
  cambió de estado es el oráculo A2 que se corrigió).

## 5. Review formal (etapa 4) y su disposición

`review.md` — reviewer `mofgw/glm-5.3-flash` (**familia distinta** a la del implementer
`mofgw/deepseek-v4.1-flash`), con el **criterio vigente**: **0 BLOCKING · 6 OPTIONAL · 7 abstenciones
declaradas**.

Sondas propias del reviewer (no repitió los tests): con un estado de **12,1 MB** la proyección es
**byte-idéntica** (el límite **no crece con el historial**); en el borde exacto `--max-bytes 1744`
→ `rc=0` y `1743` → `rc=2` con **stdout vacío** y diagnóstico que nombra el límite (**falla cerrado sin
proyección parcial**); el registro neutral del medidor es **byte-idéntico** sin `--set-summary`; el
resumen del conjunto deja lo no observado como `unknown`/`null` **con causa** (nunca subtotal ni `0`);
`--replace-packet` con tarea declarada conserva y **re-resuelve** (sonda); render cross-versión con
worktree en `009902b`. Auditó el **debilitamiento de tests** commit por commit: el testfix de T2 **no**
debilitó ninguna garantía y **correspondía al oráculo**; la corrección de D11-3 **retira** la aserción
inestable de la base viva y **conserva** la garantía por las comprobaciones controladas.

**Disposición del orquestador:** **F1** (el plan declaraba un focal inexistente) y **F4**
(identificador crudo en `acceptance.md`) **corregidos ya**; **F2** (la selección no aplica el
calificador de la spec §2.2 en reposo con directorios de paquete históricos) **a deuda y propuesto al
dueño** (el calificador no es implementable con las fuentes declaradas: es una decisión de contrato);
**F3**, **F4-bis**, **F5**, **F6** y **F7** **a deuda** con condición de cierre verificable.

## 6. Aceptación y bloqueo declarado

**PARCIAL, con bloqueo declarado** (`acceptance.md`):

- **Precondiciones del gate (INV-8) cerradas:** **D11** (en sus cuatro partes: no-escritura sobre base
  temporal controlada, concurrencia con otro escritor activo, la integración real afirmando solo
  lectura y resultados, y la regla «la base real nunca se escribe» declarada) y **R4** (los dos
  elementos de la regla del documento multiplexado), ambos **entregables de T3**.
- **Uso real observado:** la vista `status` sobre el proyecto real emitió **1.679 B** (límite 16.384 B)
  con exactamente las claves declaradas, **sin** `stage_history`, `entry=continuity-reconcile` y
  `version=UNKNOWN` **con causa** (ausencia). Contraste con la línea base: la lectura del estado
  completo en S-BOOT-04 fue de **215.292 caracteres**.
- **Observación A8 (proxy de tramo completo, NO garantía):** 12 sesiones de rol de este tramo
  (6 implementer / 6 test-writer; documento de la corrida **96.552 B**). **11 de 12** commitearon su
  producto; la excepción bloqueó legítimamente y se completó en un re-despacho.
- **Bloqueo declarado:** **A1/A2/A6 y la observación de A9 exigen una sesión real nueva con la versión
  nueva cargada** → requieren **desplegar**, acción **reservada al dueño** y **prohibida** en este
  tramo. **No se simula ni se declara satisfecha por proximidad.** Las bandas numéricas son
  **orientación derivada** de la línea base medida, **no** medidas y **no** umbrales que acepten o
  rechacen por sí solos.

## 7. Memory Bank y ADR

Cuatro borradores del **scribe** (sesión aislada), revisados por fidelidad y **materializados** por el
orquestador, **aprobados bajo la HITL delegada** (el alcance del epic incluye la aprobación del Memory
Bank con evidencia):

- `docs/projectbrief.md` (actualizado: CLI canónicos del ciclo, tooling de tests, delegación HITL).
- `docs/activeContext.md` (entry `2026-10-12` con el estado, las decisiones, los gates, la deuda y el
  bloqueo).
- `docs/progress.md` (005-003 en `Done` + log fechado).
- `docs/systemPatterns.md` (patrón «orientación acotada — proyección read-only y encargo
  autosuficiente»).
- **`docs/adr/ADR-025`** (propuesto, `Status: Proposed`, confianza **Media** declarada porque el efecto
  medido sobre una sesión real nueva no está verificado).

## 8. Deuda y próxima unidad

**Deuda** (`debt.md`, con condición de cierre verificable): F2 (propuesta al dueño), F3, F4-bis, F5,
F6, F7. **Cerradas en este tramo:** D11 y R4 (de 005-002) y los hallazgos F1/F4 de la review.

**Próxima unidad del epic:** `005-007-progressive-planning`; después `005-004-claude-code-roles`. El
epic-005 sigue en `features-loop` (**8/10** features cerradas).

**Pendiente del dueño:** desplegar la versión nueva (habilita la aceptación de uso real) y decidir F2.

## Reapertura por F2 (2026-10-13)

La verificación del orquestador Claude encontró F2 (`review-claude-spec-2026-10-12.md`). En reposo,
la vista `status` proponía retomar la ejecución de una feature cerrada, porque contaba como
pendiente cualquier directorio de `.cdad/packets/`. En este repo hay 375, así que pasaba siempre.
El dueño aprobó la enmienda de contrato (§2.2 «Reposo e historia», PD-2) y Claude orquestó la
corrección.

- RED `92d9bdc` (test-writer): 2 fallos por comportamiento (reposo con historia; directorio con
  recibo) y 12 passed.
- GREEN `03cea96` (implementer): una ejecución está activa solo si `execution.feature_id` coincide
  con `active_feature`; un directorio de paquete está pendiente solo si es de esa ejecución y no tiene
  recibo. Focales de 005-003 y 005-006: 82 passed.
- En este repo, con el state en reposo, `status` da `entry: next-unit`.
- Suite completa en un worktree fijado a `03cea96`: 849 passed / 4 skipped (15 min 46 s).
