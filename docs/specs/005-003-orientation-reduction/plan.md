> Plan **APROBADO (2026-10-12, ronda draft-003)**, texto del **architect** (subetapa `draft`,
> etapa 2), materializado por el orquestador (ADR-003) **sin cambios de contenido** y aprobado por el
> orquestador OpenCode bajo la delegación HITL del epic-005; el architect **no** aprobó su propia
> propuesta (anti-sesgo). Sustituye al texto del draft 002 (aprobado en `009902b`) **conservando
> íntegro todo lo demás** y aplicando **solo** los ajustes de **A1–A3** (los de A4–A6 son de
> redacción y quedan en la spec y en las fichas de aceptación). Contrato: `docs/epics/epic-005-real-operation/plan.md`
> — **fila 8 ENMENDADA Y APROBADA** (commit `5b912aa`; sha256 `b22bc687…`) **citada como contrato
> vigente** — **más** la sección «Ajuste de los ciclos pendientes». Deriva de
> `docs/specs/005-003-orientation-reduction/discovery.md` §5 (unidades candidatas T1–T10) y del delta
> `discovery-inputs-2026-10-12.md`. **Sin valores de este VPS.** El bloque canónico `plan-tasks` de §4
> sigue el formato de `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4.1
> (**se referencia, no se copia**) y **valida** con el validador del CLI (productor/consumidor,
> contratos compatibles, sin ciclos, paralelismo seguro, plan de validación por tarea).

# Plan — 005-003-orientation-reduction

## 1. Ajuste de las unidades del discovery a tareas atómicas

Las diez unidades candidatas del discovery §5 (T1–T10) se agrupan en **seis tareas atómicas TDD**,
**una por clase de postcondiciones**; un **RED** cubre una clase y su **GREEN** va en **otra sesión**,
sin mezclar roles. Justificación del agrupamiento:

| Unidad del discovery | Tarea atómica | Por qué se agrupa |
|---|---|---|
| T1 (vista compacta) + T2 (selección de entrada) | **T1** | La selección es el **campo `entry`** que emite la misma vista; un solo producto de código (`compact-view-v1`) y una sola sesión RED. |
| T3 (interfaz operativa) + T4 (evidencia mecánica) + T5 (versión/medidor) + el paso de orientación de la fila 8 enmendada | **T2** | Una sola **referencia corta + ejemplos ejecutados + procedimiento de arranque** cubre «operar y orientarse con el CLI»: interfaz, disposición de versión, captura del `rc` y **la vista primero en el arranque/reentrada** (A3). **Sin código nuevo**: su verificación es un focal (ejemplos ejecutados) más comprobaciones observables (el recorrido de arranque). |
| T6 (resumen del conjunto / R4) + T9 (declaración de redundancia) + **la deuda D11** | **T3** | Ambos son **consumo y evidencia del medidor**: la regla del documento multiplexado (R4) precede al resumen, la declaración de redundancia es parte de la misma evidencia, y **D11** es la misma clase (la evidencia del medidor sobre la base real). |
| T8 (capacidades efectivas) | **T4** | Ciclo **sin código** (inventario + fallback): `observable_checks`. |
| — (fila 8 enmendada: «cada encargo trae los comandos de validación de su tarea…»; origen A2) | **T6 (unidad NUEVA)** | Clase distinta: el **contrato aplicable del encargo** (producto de **código**: el render del paquete + la instrucción de la subetapa). **No** se pliega a T2: mezclaría una clase de código con una de documentación y dos oráculos distintos (ejecución de ejemplos vs provenance contra el bloque `plan-tasks`) en un solo RED/GREEN. |
| T10 (medición y aceptación) | **T5** | **Gate de aceptación** (no RED/GREEN de producto): `observable_checks` + gate de integración. |

**T7 del discovery (extensión del medidor: hito «primera acción del encargo») NO se planifica**: es
**PROPUESTA al dueño**, no se asume ni se pliega al alcance comprometido (INV-5, D8).

**Qué tarea cambió en esta ronda y por qué (explícito):**
- **T2** suma el **paso de orientación por la vista** en el procedimiento canónico de arranque y
  reentrada (A3): se le agrega `skills/cdad-cycle/references/project-start.md` a sus archivos y una
  comprobación observable; su regresión pasa a incluir el test estructural de 005-006 sobre ese
  archivo. **Motivo:** la fila 8 enmendada exige que «el procedimiento canónico de arranque y
  reentrada consulte primero la vista compacta y amplíe solo ante una necesidad concreta», y su
  consumidor es la vista que T2 ya consume.
- **T3** suma el **cierre de D11** (A1): pruebas focales nuevas y la corrección de la aserción de la
  base viva; la referencia declara la regla de la integración real. **Motivo:** D11 estaba sin dueño y
  T5 terminaba en un bloqueo declarado; la fila 8 enmendada cierra D11 **dentro de la feature**.
- **T6 (nueva)** agrega el **contrato aplicable del encargo** (A2). **Motivo:** el producto que la
  revisión entre tramos señaló como ausente para A10 («lo más caro de la línea base queda fuera del
  producto»); la fila 8 enmendada lo asigna a esta feature.
- **T5** deja de ser el dueño implícito del gate de D11/R4: ahora **verifica** que T3 los cerró
  (entregables) y consume también el producto de T6. **Motivo:** A1.
- **T1 y T4 no cambian.**

**Frontera con 005-007.** 005-003 aporta el **contrato aplicable** y las **referencias del paquete**;
el **tamaño de unidad** y la **preparación de encargos** son de 005-007 (INV-4). La extensión de T6 es
**aditiva y declarada**: no reescribe los contratos de paquete de 005-001/005-005 (un paquete sin
`plan_task` se emite byte-idéntico). **Frontera con 005-006.** T1/T2 **reusan** el procedimiento
existente; **no** crean bootstrap (INV-3).

## 2. Estrategia de validación (declarada una vez)

- **Dos niveles.** **Siempre**: procedencia, `git diff` contra el alcance del paquete, alcance
  declarado y **pruebas focales** (segundos). **Solo con un motivo concreto**: la suite o la
  integración. Se **reutiliza evidencia equivalente** con procedencia verificada por **referencia** a
  la regla canónica `skills/cdad-cycle/references/re-entry.md` (*Equivalence of a registered run*).
- **Suite completa una vez, al cierre** (motivo: toca el CLI/la metodología y cierra la feature). No
  se corre la suite dentro de cada tarea; **no se corre salvo que el paquete lo pida** (la corre quien
  cierra) — es lo que la instrucción del paquete declara (T6, PD-10-iv).
- **Comandos concretos por encargo** (fichas de §3), **tomados del bloque `plan-tasks`** de este plan
  y rendidos en el paquete (T6). RED: el focal debe fallar por aserción (no por import/sintaxis).
  GREEN: focal verde + regresiones del área.
- **El cierre incluye el commit** y el reporte del rol lo declara (PD-10-v); un rol que termina sin
  commitear es un **bloqueo declarado** registrado en la aceptación, no aceptado en silencio.
- **Metas numéricas = orientación (A6).** Las bandas de A1/A7/A9 y el proxy de A8 son **orientación
  derivada de la línea base medida**, **no** demostración automática ni umbral que acepte o rechace
  por sí solo; la aceptación la juzga el orquestador con el registro de la sesión real.
- **Sin `--no-verify`; sin push; sin desplegar.**

## 3. Fichas mínimas de tarea

### T1 — Vista compacta + selección de entrada
- **Resultado observable / PD cubiertas:** PD-1, PD-2 (y la parte de PD-5 del **diagnóstico de
  asimetría en la salida de la vista**; base de PD-4/PD-6 en su parte de versión).
- **Alcance incluido:** subcomando `status` (proyección + `entry`), **límite normativo de 16.384 B con
  fallo cerrado** (C1) y **diagnóstico de la asimetría de raíz relativa en la salida** (C4).
  **Excluido:** migrar el formato del estado, separar el historial, emitir `stage_history`, dashboard.
- **Consume:** — . **Produce:** `compact-view` (`compact-view-v1`).
- **Dependencias:** — .
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`,
  `skills/cdad-cycle/references/orientation.md`; *Test* `tests/test_005_003_t1_compact_view.py`.
- **Contexto por rol:** RED (test-writer) — spec §2.1/§2.2/§2.5 + discovery (b); **no** ve la
  implementación. GREEN (implementer) — spec §2.1/§2.2/§2.5 + `project-start.md`/`project-execution.md`.
- **Evidencia al re-entry:** focal rojo→verde; `git diff` acotado a los archivos declarados; el estado
  byte-idéntico (INV-1).
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_003_t1_compact_view.py -q` (rojo → verde).
  **Comprobaciones observables (C1/C4):** la vista **no supera 16.384 B** y **falla cerrado** por
  encima del límite **sin emitir proyección parcial**; el diagnóstico de raíz relativa **nombra la
  asimetría entre CLIs** y el camino de recuperación.
- **Integración / responsable:** `@validation_strategy`; GREEN implementer; review por el reviewer.
- **Incertidumbres / detención:** **V2 decidido** (nombres de campo = contrato de §2.1); **no**
  inventar campos del estado.

### T2 — Interfaz operativa + disposición de versión + evidencia mecánica + arranque con la vista primero
- **Resultado observable / PD cubiertas:** PD-3, PD-4, PD-5, **PD-11**.
- **Alcance incluido:** referencia corta + **ejemplos mínimos EJECUTADOS** (asset canónico, C3); regla
  de versión (ausencia ≠ incoherencia; medidor ausente); patrón de captura del `rc` y **qué afirma el
  test** (C4); **el procedimiento canónico de arranque y reentrada consulta primero la vista `status`
  y amplía solo ante una necesidad concreta** (A3/PD-11), **por referencia** al dueño canónico y sin
  copiar su estructura (INV-3). **Excluido:** manual extenso, generador de documentación, desplegar el
  medidor, otro bootstrap, redefinir `state-detection.md`.
- **Consume:** `compact-view` (`compact-view-v1`) de **T1**. **Produce:** `operational-interface`
  (`operational-interface-v1`).
- **Dependencias:** T1.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/assets/orientation-examples.json`,
  `skills/cdad-cycle/references/orientation.md`, `skills/cdad-cycle/references/project-start.md`;
  *Test* `tests/test_005_003_t2_examples_execute.py`.
- **Contexto por rol:** RED — spec §2.3/§2.4/§2.5/**§2.9** + esquemas (`packet-request.schema.json`,
  `execution-context.schema.json`, `state-template.json`) + `project-execution.md` §5 +
  `project-start.md` §6-§10. GREEN — ídem + `continuity.md`.
- **Evidencia al re-entry:** el test **ejecuta** los ejemplos **localizados por el asset** (no grep);
  focal rojo→verde; el recorrido de arranque observado y registrado con sus ampliaciones y su motivo.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_003_t2_examples_execute.py -q`;
  regresión `tests/test_005_006_t1_start_procedure.py` (estructural sobre `project-start.md`).
  **Comprobaciones observables (C3/C4/PD-11):** los ejemplos se **localizan por el asset canónico**
  (nunca por prosa); el **conjunto mínimo** se ejecuta contra la **versión correspondiente** y un
  **ejemplo inválido falla con el diagnóstico que nombra el campo**; el **`rc` capturado es el del CLI
  real** (no el de la tubería) y el error accionable **nombra la causa y la recuperación**; el
  procedimiento **consulta primero la vista** y **amplía solo con motivo**, y el recorrido de una
  sesión nueva se **observa y registra** (primera acción de orientación, ampliaciones, resultado) sin
  presentarlo como garantía.
- **Integración / responsable:** `@validation_strategy`; GREEN implementer.
- **Incertidumbres / detención:** redacción R4 (V3) y asimetría de raíz relativa — detener si aparece
  una asimetría nueva no verificada; el paso de orientación **no** debe copiar la estructura de los
  dueños (la regresión de 005-006 lo prohíbe).

### T3 — Resumen del conjunto (multi-sesión) + regla del documento multiplexado + **cierre de D11**
- **Resultado observable / PD cubiertas:** PD-6, PD-8, **PD-12** (y PD-7 como no-regresión).
- **Alcance incluido:** declarar la regla del documento multiplexado en `context-meter.md` (R4) con
  sus **dos elementos** (C5/V3) **primero**; resumen de corrida en **documento aditivo separado**
  (`set-summary-v1`, V1 decidido) con el **conjunto mínimo de claves** (C2) y el **detalle por sesión
  no emitido por defecto** (bandera declarada); declaración de redundancia; **cierre de D11** con su
  condición causal: **(1)** no-escritura sobre **base temporal controlada**; **(2)** concurrencia con
  **otro escritor activo durante la lectura** (prueba controlada); **(3)** en la **integración real**
  se comprueba **solo la lectura y los resultados**, sin exigir que la base quede inmóvil (se
  **corrige** la aserción de `(tamaño, mtime)` de la base viva); **(4)** **nunca** se intenta escribir
  en la base real; la regla se declara en el reference. **Excluido:** reescribir el registro
  neutral/por sesión, cambiar flags existentes, dashboard, extender el hito (T7 = propuesta),
  reescribir el contrato del medidor.
- **Consume:** — . **Produce:** `r4-rule` (`context-meter-r4-v1`), `set-summary` (`set-summary-v1`).
- **Dependencias:** — (pero **entregable de gate**: R4 y D11 cerrados **aquí**, antes de consumir
  multi-sesión y antes de usar la integración real como gate; INV-8).
- **Archivos:** *Create/Modify* `skills/cdad-cycle/references/context-meter.md`,
  `skills/cdad-cycle/scripts/cdad_context_meter.py` (aditivo); *Test*
  `tests/test_005_003_t3_set_summary.py` (las comprobaciones controladas (1) y (2) de D11 viven en
  este único focal: `test_d11_1_*` y `test_d11_2_*`); se **corrige** la aserción de la base viva en
  `tests/test_005_002_t4_acceptance.py` (D11-3). **Reconciliación declarada (review F1):** la versión
  aprobada de esta ficha y del bloque `plan-tasks` declaraban además un
  `tests/test_005_003_t3_meter_no_write.py` que **nunca existió**; el orquestador alineó el plan a la
  **spec** (PD-12 dice «el test focal nuevo de T3», singular) y a lo entregado.
- **Contexto por rol:** RED — spec §2.6 + delta R4 + `context-meter.md` + `debt.md` R4 **y D11
  (`:128-146`)**. GREEN — ídem + `context-meter.schema.json`.
- **Evidencia al re-entry:** R4 presente **antes** del consumo; resumen con las claves declaradas;
  regresión de 005-002 verde; focal rojo→verde; **el cierre de D11 declara las tres comprobaciones y
  dónde vive cada una** y que ninguna prueba escribe en la base real.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_003_t3_set_summary.py -q` (incluye la
  prueba controlada de concurrencia de D11-(2), que falla si el producto escribe o si la lectura
  concurrente no da los resultados esperados; la corrección de la aserción de la base viva es
  **corrección de evidencia**, no un RED de producto); regresión
  `tests/test_005_002_t1_neutral_record.py`.
  **Comprobaciones observables (C2/V3/D11):** el resumen emite el **conjunto mínimo de claves** y **no**
  emite el detalle por sesión por defecto (se pide con la bandera declarada); la regla del documento
  multiplexado contiene los **dos elementos** (total ≤ N × límite por sesión; límite normativo por
  documento de sesión); el cierre de D11 verifica la ausencia de escrituras sobre una **base temporal
  controlada**, cubre la **concurrencia** con otro escritor activo durante la lectura, y en la
  **integración real** comprueba **solo la lectura y los resultados** sin exigir que la base quede
  inmóvil y sin escribir en la base real.
- **Integración / responsable:** `@validation_strategy`; GREEN implementer.
- **Incertidumbres / detención:** **V1 decidido** (documento aditivo separado); **detener** si el owner
  exige la clave en el registro neutral (tocaría el asset de 005-002) o si el resumen no puede ser
  aditivo. Si la prueba controlada de concurrencia revela un defecto **real** del producto, es un
  **hallazgo nuevo declarado**, no una corrección silenciosa de esta ronda; corridas verdes repetidas
  **no** sustituyen la corrección de D11 (`debt.md:145-146`).

### T4 — Inventario de capacidades efectivas + fallback portable
- **Resultado observable / PD cubiertas:** PD-9.
- **Alcance incluido:** matriz corta (observada/documentada/no disponible/desconocida) ligada a
  versión/configuración + demostración del camino agente → artefacto → revisión por archivos/enlaces.
  **Excluido:** implementar OpenChamber/OnlyOffice, prometer API de UI, crear fuente de estado.
- **Consume:** — . **Produce:** `capabilities-inventory` (`capabilities-inventory-v1`).
- **Dependencias:** — .
- **Archivos:** *Create* `skills/cdad-cycle/references/capabilities.md`; *Test* —
  (ciclo **sin código**).
- **Contexto por rol:** test-writer — spec §2.7 + `findings/agent-operation-strategy-2026-10-11.md` §5.
- **Evidencia al re-entry:** comprobación observable roja→verde (inventario ausente → presente con el
  contenido exigido).
- **Verificación:** `observable_checks` (no hay focal de código).
- **Integración / responsable:** `@validation_strategy`; test-writer.
- **Incertidumbres / detención:** el contrato agente↔OpenChamber **no** está verificado — **detener**
  y no prometer más que el fallback portable.

### T5 — Medición y aceptación de uso real (gate)
- **Resultado observable / PD cubiertas:** criterios A1–A11; INV-8/INV-10.
- **Alcance incluido:** informe de medición con el **artefacto del repo en solo lectura** + próxima
  sesión real registrada (ayudas extraordinarias, bloqueos, resultado); **verificación de que T3 cerró
  D11 y R4** (entregables de la feature) antes de usar la integración real y las corridas multi-sesión;
  registro de las **corridas observadas con su motivo** (A10) y del **proxy de reorientación de rol**
  (A8). **Excluido:** desplegar el medidor, repetir la línea base, promediar cuts distintos, fijar un
  «0 corridas» rígido, tratar las bandas como umbral automático.
- **Consume:** `compact-view` (`compact-view-v1`) de **T1**, `set-summary` (`set-summary-v1`) de **T3**,
  **`packet-contract` (`packet-contract-v1`) de T6**. **Produce:** `acceptance-report`
  (`acceptance-report-v1`).
- **Dependencias:** T1, T3, **T6**. **Gate:** D11 y R4 cerrados **en T3** antes de usar la integración
  real y las corridas multi-sesión (si faltara su evidencia → **bloqueo declarado**, no atajo).
- **Archivos:** *Create* evidencia del informe (fuera del árbol publicable); *Test* — (gate, sin
  código).
- **Contexto por rol:** orchestrator — spec §5 + línea base (por referencia); architect — lectura.
- **Evidencia al re-entry:** comparación like-for-like, **medido vs derivado**, bandas declaradas
  **orientación** (no umbral), `unknown` con causa, corridas observadas con su motivo.
- **Verificación:** `observable_checks`.
- **Integración / responsable:** **gate de aceptación del epic-005** (ver §5); orchestrator (medición).
- **Incertidumbres / detención:** si la evidencia del cierre de D11/R4 no está, → **BLOQUEO
  declarado**, no atajo.

### T6 — Contrato aplicable del encargo (**unidad NUEVA**, A2)
- **Resultado observable / PD cubiertas:** **PD-10** (y A10/A8 en lo que el paquete habilita).
- **Alcance incluido:** el paquete de un **encargo de tarea** (i) **declara su tarea** con una opción
  **aditiva** (`--plan-task <ID>`) y un campo **opcional** (`plan_task`); (ii) emite una **sección
  declarada** con los **comandos de validación de esa tarea iguales a los del bloque canónico
  `plan-tasks`** del plan aprobado (`focal_tests` / `observable_checks` / `regressions` /
  `integration_gate`, con `@validation_strategy` resuelto) y la regla de **cuándo ampliarla**; una
  tarea **ausente** falla cerrado nombrando el id; (iii) emite **por referencia** las
  postcondiciones/invariantes/decisiones aplicables a la unidad (ids que resuelven a encabezados del
  contrato) con la referencia del contrato (path + `sha256`); (iv) la **instrucción** del paquete
  declara que la **suite completa no se corre salvo que el paquete lo pida** (la corre quien cierra),
  **corrigiendo** los dos assets que hoy afirman lo contrario; (v) el **cierre incluye el commit**.
  **Excluido:** cambiar el tamaño de unidad o la preparación de encargos de 005-007; reescribir los
  contratos de paquete de 005-001/005-005 (la extensión es **aditiva y declarada**); inferir la tarea
  de la prosa del objetivo; derivar la aplicabilidad automáticamente.
- **Consume:** — . **Produce:** `packet-contract` (`packet-contract-v1`).
- **Dependencias:** — . **Nota de paralelismo:** edita el **mismo archivo** que T1
  (`skills/cdad-cycle/scripts/cdad_packet.py`); **no** se declaran paralelas (`parallel: []`), así que
  la comprobación de paralelismo seguro del validador no aplica.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py` (render del paquete y
  extensión aditiva del request), `skills/cdad-cycle/assets/packet-request.schema.json` (propiedad
  opcional declarada), `skills/cdad-cycle/packets/common.md` (declaración única de la política de
  suite), `skills/cdad-cycle/packets/roles/implementer.md` y
  `skills/cdad-cycle/packets/substages/implementer-green.md` (corrección de la contradicción); *Test*
  `tests/test_005_003_t6_packet_contract.py`.
- **Contexto por rol:** RED — spec §2.8 + fila 8 enmendada (`plan.md:41`) +
  `planning-contract-draft.md` §4.1 + `packet-request.schema.json` + `packets/`. GREEN — ídem +
  `project-execution.md` §3/§5/§8.
- **Evidencia al re-entry:** focal rojo→verde; `git diff` acotado; la **provenance** de los valores
  contra el bloque (el test compara con lo parseado, no con texto a mano) y la declaración de la
  política de suite en las tres fuentes de instrucción con sus hashes.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_003_t6_packet_contract.py -q`;
  regresiones `tests/test_005_001_t2_replace_packet.py` y `tests/test_005_005_t1_replace_conserved.py`.
  **Comprobaciones observables (PD-10):** el paquete declara su tarea y emite los comandos de
  validación **iguales** a los del bloque `plan-tasks` (con `@validation_strategy` resuelto) y dice
  **cuándo ampliarla**; una tarea ausente **falla cerrado nombrando el id**; las referencias al
  contrato resuelven a encabezados; el bloque de instrucción declara que la suite completa no se corre
  salvo que el paquete lo pida y ningún asset lo contradice; el cierre exige el commit. **Sin**
  `plan_task`, el paquete se emite byte-idéntico.
- **Integración / responsable:** `@validation_strategy`; GREEN implementer.
- **Incertidumbres / detención:** si la extensión deja de ser **aditiva** (toca un campo obligatorio o
  relaja el cierre de campos), **detener**: la frontera con 005-001/005-005 es no negociable. La
  aplicabilidad de (iii) la declara el encargo; la spec **no** promete derivarla automáticamente.

## 4. Bloque canónico `plan-tasks`

```plan-tasks
{"validation_strategy": "Verificacion en dos niveles: siempre procedencia + diff + alcance + pruebas focales (segundos); suite o integracion solo con un motivo concreto; la suite completa la corre una vez quien cierra; se reutiliza evidencia equivalente con procedencia verificada (regla canonica en skills/cdad-cycle/references/re-entry.md, seccion Equivalence of a registered run), sin repetir la suite tres veces.",
 "tasks": [
  {"id": "T1",
   "produce": [{"artifact": "compact-view", "contract": "compact-view-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/references/orientation.md"],
   "focal_tests": ["tests/test_005_003_t1_compact_view.py"],
   "observable_checks": ["la vista no supera 16384 B y falla cerrado por encima del limite sin emitir proyeccion parcial; el diagnostico de raiz relativa nombra la asimetria entre CLIs y el camino de recuperacion"],
   "regressions": [],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "produce": [{"artifact": "operational-interface", "contract": "operational-interface-v1"}],
   "consume": [{"artifact": "compact-view", "contract": "compact-view-v1", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["skills/cdad-cycle/assets/orientation-examples.json", "skills/cdad-cycle/references/orientation.md", "skills/cdad-cycle/references/project-start.md"],
   "focal_tests": ["tests/test_005_003_t2_examples_execute.py"],
   "observable_checks": ["los ejemplos se localizan por el asset canonico declarado (nunca por prosa), el conjunto minimo se ejecuta contra la version correspondiente y un ejemplo invalido falla con el diagnostico que nombra el campo; el rc capturado es el del CLI real (no el de la tuberia) y el error accionable nombra la causa y la recuperacion", "el procedimiento canonico de arranque y reentrada consulta primero la vista status y amplia solo ante una necesidad concreta; el recorrido de una sesion nueva se observa y se registra (primera accion de orientacion, ampliaciones y su motivo, resultado) sin presentarlo como garantia"],
   "regressions": ["tests/test_005_006_t1_start_procedure.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "produce": [{"artifact": "r4-rule", "contract": "context-meter-r4-v1"}, {"artifact": "set-summary", "contract": "set-summary-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_context_meter.py", "skills/cdad-cycle/references/context-meter.md"],
   "focal_tests": ["tests/test_005_003_t3_set_summary.py", "tests/test_005_002_t4_acceptance.py"],
   "observable_checks": ["el resumen del conjunto emite el conjunto minimo de claves declarado y no emite el detalle por sesion por defecto (se pide con la bandera declarada); la regla del documento multiplexado contiene los dos elementos exigidos (total <= N x limite por sesion; limite normativo por documento de sesion)", "el cierre de D11 verifica la ausencia de escrituras sobre una base temporal controlada, cubre la concurrencia con otro escritor activo durante la lectura, y en la integracion real comprueba solo la lectura y los resultados sin exigir que la base quede inmovil y sin intentar escribir en la base real"],
   "regressions": ["tests/test_005_002_t1_neutral_record.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "produce": [{"artifact": "capabilities-inventory", "contract": "capabilities-inventory-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [],
   "observable_checks": ["el inventario declara cada capacidad como observada/documentada/no disponible/desconocida, ligada a version/configuracion, con el fallback portable por archivos o enlaces demostrado y sin prometer el contrato agente-superficie de OpenChamber"],
   "regressions": [],
   "integration_gate": "@validation_strategy",
   "owner": "test-writer"},
  {"id": "T5",
   "produce": [{"artifact": "acceptance-report", "contract": "acceptance-report-v1"}],
   "consume": [{"artifact": "compact-view", "contract": "compact-view-v1", "producer": "T1"}, {"artifact": "set-summary", "contract": "set-summary-v1", "producer": "T3"}, {"artifact": "packet-contract", "contract": "packet-contract-v1", "producer": "T6"}],
   "depends_on": ["T1", "T3", "T6"],
   "parallel": [],
   "files": [],
   "observable_checks": ["el informe aplica las bandas como orientacion derivada de la linea base medida (no como umbral que acepte o rechace por si solo) con comparacion like-for-like sobre una proxima sesion real, distingue medido de derivado, registra las corridas observadas con su motivo, observa y registra el proxy de reorientacion de rol como tramo completo, y deja lo ausente como unknown con causa"],
   "regressions": [],
   "integration_gate": "gate de aceptacion del epic-005: D11 y R4 cerrados en T3 (entregables de la feature) antes de usar la integracion real y las corridas multi-sesion; medicion con el artefacto del repo en solo lectura mientras el medidor no este instalado",
   "owner": "orchestrator (medicion); architect (lectura)"},
  {"id": "T6",
   "produce": [{"artifact": "packet-contract", "contract": "packet-contract-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/assets/packet-request.schema.json", "skills/cdad-cycle/packets/common.md", "skills/cdad-cycle/packets/roles/implementer.md", "skills/cdad-cycle/packets/substages/implementer-green.md"],
   "focal_tests": ["tests/test_005_003_t6_packet_contract.py"],
   "observable_checks": ["el paquete de un encargo de tarea declara su tarea y emite en una seccion declarada los comandos de validacion de esa tarea tomados del bloque canonico plan-tasks del plan aprobado (focal_tests/observable_checks/regressions/integration_gate, con @validation_strategy resuelto) y dice cuando ampliarla; los valores emitidos son iguales a los del bloque (no texto a mano) y una tarea ausente del bloque falla cerrado nombrandola; el bloque de instruccion del paquete declara que la suite completa no se corre salvo que el paquete lo pida (la corre quien cierra) y el cierre del encargo incluye el commit"],
   "regressions": ["tests/test_005_001_t2_replace_packet.py", "tests/test_005_005_t1_replace_conserved.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"}
 ]}
```

## 5. Condición del gate de aceptación

- **D11 y R4 son entregables de T3** y se cierran **dentro de la feature**, **antes** de usar la
  integración real y las corridas multi-sesión como gate (INV-8). T5 **verifica** ese cierre con su
  evidencia; si faltara, devuelve **bloqueo declarado**, no atajo. **T5 ya no termina en un bloqueo
  por diseño**: el bloqueo era el síntoma de que D11 no tenía tarea que lo cerrara (revisión entre
  tramos, punto 1), y T3 lo cierra.
- **Mientras el medidor no esté instalado**, la medición se hace con el **artefacto del repo en solo
  lectura**; el **despliegue** es del dueño y queda fuera de esta feature.
- La **aceptación** usa una **próxima sesión real** (A6) y aplica las bandas **como orientación
  derivada** de la línea base medida, con comparación like-for-like, declarando **medido vs derivado**
  y el **proxy observado** de reorientación (A8). **Las bandas no aceptan ni rechazan por sí solas**: la
  aceptación la juzga el orquestador con el **registro de la sesión real** (ayudas extraordinarias,
  bloqueos, resultado) y con las **corridas observadas y su motivo** (A10).

## 6. Restricciones globales

- Rama **`codex/epic-005-real-operation`**; **sin push**; **sin `--no-verify`**; **sin desplegar**;
  **sin tocar HOME**; **sin leer** `tests/.sensitive-patterns.local`.
- **No** reescribir los contratos de paquete de 005-001/005-005: la extensión de T6 es **aditiva y
  declarada** (un paquete sin `plan_task` se emite byte-idéntico).
- **No** reescribir los contratos de 005-002; **no** asumir la extensión del hito (T7 = propuesta).
- **Sin volcar salidas enormes** al contexto; evidencia completa por referencia.
- Para comprobar un RED **sin** el arreglo: **worktree** — **nunca `git stash`** en el árbol
  compartido.
- **Ante un obstáculo fuera de alcance: entregar el diagnóstico, no fabricar registros.**
- **Sin valores de este VPS** en spec, plan ni producto (INV-6).

## 7. Aprobación

- **Estado de este texto: APROBADO (2026-10-12, ronda draft-003).** Aprobado por el **orquestador
  OpenCode**, bajo la **delegación HITL del epic-005**
  (`docs/epics/epic-005-real-operation/execution.md`), **junto con la spec** (una sola acción). El
  architect **no** aprobó su propia propuesta (anti-sesgo). **Sin enmiendas al re-aprobar**.
- **Historial.** El texto del **draft 002** fue **aprobado (2026-10-12)** por el **orquestador
  OpenCode**, bajo la **delegación HITL del epic-005**
  (`docs/epics/epic-005-real-operation/execution.md`), **junto con la spec** (una sola acción), en el
  commit `009902b`, con **D1–D10** adoptadas. Entre tramos, el orquestador Claude revisó spec y plan
  (conforme en lo sustancial; dos puntos a resolver) y el dueño decidió **A1–A6**.
- **Cambios de esta ronda (draft-003), y por qué:** **T3** suma el cierre de **D11** (estaba sin tarea
  que lo cerrara; la fila 8 enmendada lo cierra dentro de la feature); **T2** suma el **paso de
  orientación por la vista** en el procedimiento de arranque y reentrada (A3); **T6 (nueva)** agrega el
  **contrato aplicable del encargo** (A2: el producto que faltaba para A10); **T5** pasa a **verificar**
  el cierre de D11/R4 y consume también `packet-contract`; **T1** y **T4** no cambian. No cambia el
  número de piezas de alcance, el ancla de aceptación, los límites ya fijados, las fronteras ni las
  prohibiciones.
- **Bloque canónico `plan-tasks`:** se validó con las funciones del **propio CLI** en solo lectura
  (`_plan_tasks_from_contract` + `_check_plan_tasks` + `_check_plan_validation_plan`): `OK`, tareas
  `T1..T6`, estrategia declarada.
- **T7 del discovery NO se planifica**: la extensión del medidor (hito «primera acción del encargo»)
  es **PROPUESTA** al dueño, no asumida (INV-5).
- **Gate de aceptación:** D11 y R4 se cierran **en T3** antes de usar la integración real y las
  corridas multi-sesión (§5).
- Status: Approved by orquestador OpenCode (HITL delegada epic-005) on 2026-10-12 (ronda draft-003)
