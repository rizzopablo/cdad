# Epic epic-005-real-operation — Cierre

Cerrado: 2026-10-14 · Epic: «Operación real y medición de contexto» · Autoridad: orquestador OpenCode con
HITL delegada (`docs/epics/epic-005-real-operation/execution.md`), por instrucción del dueño

## Resumen

Puso en uso real la versión instalada, hizo que un proyecto arranque con una instrucción breve, midió el
contexto que consume cada rol y recortó la orientación del orquestador **con datos medidos, no
presupuestos** (`plan.md` §Resultado buscado). Se entregaron **14 unidades**, cada una con su gate de
etapa 5 y su evidencia, y el epic se cierra **sin publicar**: el saneamiento de contenido está hecho y la
decisión de publicar con **historial nuevo** es del dueño.

## Versión de referencia

| Dato | Valor |
|---|---|
| Commit de producto del repo al cierre | **`d3b9ccd`** (rama `codex/epic-005-real-operation`) |
| Commit instalado en HOME | **`29a4805`** — `install.sh --check` PASS; desplegado por el dueño el 2026-10-14 (`execution.md` §Pendientes para el cierre; `runtime-adopted-version.md` §Versión vigente) |
| Equivalencia de producto | `git diff --name-only 29a4805..d3b9ccd` = **solo** `docs/epics/epic-005-real-operation/execution.md` → **cero diferencias de producto** |
| Último commit que toca producto | **`a4028af`** (005-014 T1 GREEN), precedido por **`6fd515d`** (005-012, commit final revisado) |

La instalación nueva está **disponible**, pero **el servidor de OpenCode no se reinició**; el derivado de
este proyecto todavía declara la versión anterior y el `status` lo da como **DRIFT en la pierna del
proyecto** (`runtime-adopted-version.md` §Versión vigente y §Nota de reconciliación: la instalación nueva
«no cambia las instrucciones que una sesión ya tiene cargadas ni reinicia el servidor»).

## Features entregadas

| # | Feature | Resultado (una línea) | Cerrada | Evidencia |
|---|---|---|---|---|
| 1 | 005-001-idle-and-v7-bootstrap | Aprobación de contrato por rol (corrige la circularidad I2), reemplazo de paquete preparado y no despachado, marcadores accionables y reposo legítimo en `validate-state`; publica los agentes de proyecto v7 | 2026-10-09 | [closure.md](../specs/005-001-idle-and-v7-bootstrap/closure.md) |
| 2 | 005-005-adoption-coherence | El reemplazo valida el encargo resultante completo; una sola política de evidencia; procedencia de la instalación declarada en el artefacto publicado | 2026-10-09 | [closure.md](../specs/005-005-adoption-coherence/closure.md) |
| 3 | 005-006-guided-project-start | Una instrucción breve basta para la primera delegación útil: procedimiento corto de arranque + entrada *boot-at-rest*, sin código de producto nuevo | 2026-10-10 | [closure.md](../specs/005-006-guided-project-start/closure.md) |
| 4 | 005-008-project-path-capabilities | Mapas de permisos coherentes con el clasificador para tests anidados dentro de la implementación: el test-writer lee y edita sus tests declarados y `private` gana por findLast | 2026-10-10 | [closure.md](../specs/005-008-project-path-capabilities/closure.md) |
| 5 | 005-009-cli-delegation | Interfaz común de delegación externa con un adaptador por destino (el primero, OpenCode), reusando paquete, I8, ledger, recibos y reconciliación sin crear otro state | 2026-10-11 | [closure.md](../specs/005-009-cli-delegation/closure.md) |
| 6 | 005-010-real-opencode-delegation | El adaptador OpenCode completa un recorrido real: señal durable leída del store en solo lectura, `mode: subagent` como entrada soportada e invocación que el CLI instalado realmente soporta | 2026-10-11 | [closure.md](../specs/005-010-real-opencode-delegation/closure.md) |
| 7 | 005-002-session-context-meter | Medición neutral del runtime y opcional (`context-meter-v1`) + lector read-only de sesiones de OpenCode, por sesión y por rol; el medidor nunca aprueba | 2026-10-11 | [closure.md](../specs/005-002-session-context-meter/closure.md) |
| 8 | 005-003-orientation-reduction | Orientación acotada al primer despacho legítimo: vista compacta `status` (proyección read-only, límite 16.384 B fail-closed), selección de entrada y contrato aplicable del encargo | 2026-10-12 | [closure.md](../specs/005-003-orientation-reduction/closure.md) |
| 9 | 005-007-progressive-planning | Planificación progresiva (marcador cerrado `detail`), `open-unit` que abre la unidad sin editar el state a mano, materialización del informe del architect y plantillas del recorrido de uso | 2026-10-13 | [closure.md](../specs/005-007-progressive-planning/closure.md) |
| 10 | 005-004-claude-code-roles | Roles CDAD activos en Claude Code por el mecanismo nativo, con un ciclo corto real despachado desde una sesión nueva con la versión instalada al empezar | 2026-10-13 | [closure.md](../specs/005-004-claude-code-roles/closure.md) |
| 11 | 005-011-common-entry | La entrada al proceso es la vista `status` —en las skills y en el prompt del agente orquestador— y el state completo es ampliación condicional; raíz relativa unificada | 2026-10-14 | [closure.md](../specs/005-011-common-entry/closure.md) |
| 12 | 005-013-unit-contract | El contrato de la unidad es una proyección generada del plan, pineada por digest, con fallback declarado y veredicto por identidad y clase de parte | 2026-10-14 | [closure.md](../specs/005-013-unit-contract/closure.md) |
| 13 | 005-012-transition-registration | Operación del CLI que registra la transición con evidencia exigida, identidad por contenido y un cierre que comprueba antes de aplicar | 2026-10-14 | [closure.md](../specs/005-012-transition-registration/closure.md) |
| 14 | 005-014-closure-replay | Repetir un cierre ya aplicado no falla ni sugiere abrir la unidad: no-op rc=0 con el state byte a byte igual | 2026-10-14 | [closure.md](../specs/005-014-closure-replay/closure.md) |

Orden de ejecución: 005-001, 005-005, 005-006, 005-008, 005-009, 005-010, 005-002, 005-003, 005-007,
005-004, 005-011, 005-013, 005-012, 005-014. Cada feature tiene además su gate de etapa 5 en su propio
`closure.md` (y su `closure-suite.md` cuando la suite completa se corrió ahí).

## Criterios de aceptación del epic

| # | Criterio (`plan.md` §Criterios de aceptación del epic) | Estado | Motivo y evidencia |
|---|---|---|---|
| 1 | Todas las features del plan cerradas, cada una con su gate de etapa 5 | **✅** | Las **14** están en `done` con su cierre: tabla de §Features entregadas |
| 2 | Cada ciclo corre de punta a punta con una versión instalada estable; la versión nueva se entrega en el repo al cierre y se despliega entre ciclos; verificado en cada `prepare` por `source_dir`, hashes y la versión declarada por la instalación | **✅** (en la parte que el criterio manda verificar) | Cada `prepare` comprobó `source_dir`, hashes y la versión declarada; la versión nueva se entregó en el repo al cierre y se desplegó entre ciclos (**`29a4805`**, `install.sh --check` PASS). **Con límites declarados:** **RD-a** (los derivados del proyecto siguen declarando la versión anterior; el `status` da DRIFT en la pierna `project` y lo resuelve el próximo `prepare`), la deuda **D6** de 005-002 (versión heterogénea del runtime, en deuda por encargo del dueño) y **MIX-V6V7** de 003-007 |
| 3 | Informe de medición de contexto antes y después de 005-003, producido por la herramienta de 005-002 sobre sesiones reales | **✅** | Existe **como las secciones citadas** —005-003 §9 («antes»), 005-007 §7 y 005-011 AC-6/AC-7 («después»)— producidas con el instrumento de 005-002 sobre sesiones reales. **No hay un documento consolidado aparte y se declara así** |
| 4 | Suite completa verde al cierre, corrida por el orquestador en un worktree fijado al commit de cierre; validadores sin fallos nuevos | **✅** | Suite completa corrida por el orquestador en un worktree fijado al commit de cierre (§Suite de cierre); `make validate` **155 PASS / 1 FAIL**, el fallo **F011 preexistente**, declarado |
| 5 | Aceptación conjunta del consumidor: una sesión nueva inicia el consumidor con una instrucción breve, conserva sus IDs y organización, registra lo faltante y realiza la primera delegación útil | **❌ no ejecutado** | Depende del **dueño del consumidor** («el otro proyecto activo»); arrastra la **R2 real de 005-006** y los **VERIFY 1/5/6 de 005-008**. Se declara: **no se convierte en verde ni bloquea el cierre**, por decisión del dueño, que instruyó el cierre |

### Suite de cierre (criterio 4)

La corrió el orquestador OpenCode (HITL delegada del epic-005) el 2026-10-14, **una sola vez**, en un
**worktree aparte** `--detach` fijado a **`d3b9ccd`** (el commit de producto del repo al cierre) armado con
`make staging`:

- `python3 -m pytest tests -q -p no:cacheprovider` → **1028 passed / 4 skipped, sin fallos** (20 min 31 s).
- `make validate` → **155 PASS / 1 FAIL**; el fallo es **F011** (`scripts/validate-subagents.sh`, drift de
  copia instalada), **preexistente y declarado** (D-6 de 005-011), el mismo resultado que las suites de
  cierre de 005-012 y 005-014.
- **Equivalencia:** `git diff --name-only 29a4805..d3b9ccd` es solo documentación
  (`docs/epics/epic-005-real-operation/execution.md`), así que la corrida corresponde al mismo código de
  producto que la instalación `29a4805`. Los resultados de las suites de cierre de cada unidad están en el
  §Suite de cierre de su `closure.md` y en su `closure-suite.md`.
- **Nota de evidencia (declarada):** el barrido de saneamiento registró «suite con el barrido: 1024 passed
  / 4 skipped» (`execution.md`); esta corrida, sobre el árbol del cierre y con los 4 focales de 005-014
  incluidos, da **1028**. La diferencia (4) no queda explicada por ese registro y **no** hay fallos nuevos
  en ninguna de las dos corridas: se deja declarada y la cifra del cierre es esta.

## Tres distinciones

### 1. Producto instalado frente a sesiones activas

La instalación nueva **está disponible**, pero **el servidor de OpenCode no se reinició**: el derivado de
este proyecto todavía declara la versión anterior y el `status` lo da como **DRIFT en la pierna del
proyecto**. El **próximo `prepare` actualiza los archivos, pero no cambia las instrucciones que una sesión
ya tiene cargadas**. La **adopción coherente de versión antes de iniciar un ciclo sigue pendiente**
(**RD-a**: `docs/specs/005-011-common-entry/debt.md`; `execution.md` §Pendientes para el cierre).

### 2. Fiabilidad frente a eficiencia

Hay mejoras de funcionamiento **demostradas**: contratos, planificación progresiva, medición, delegación
entre runtimes, registro de transiciones y recuperación ante interrupciones, con **menos edición manual
del state**. Hay una **reducción clara de la preparación en Claude Code** (AC-7) y en OpenCode **el ahorro
de contexto fue pequeño** (AC-6). El epic entrega una base **más fiable**, pero **no demuestra** que la
carga de coordinación de la metodología sea pequeña y proporcional en todos los desarrollos: ese objetivo
**continúa**, y la meta **no es un tope de sesión** —el contexto se reserva para el proyecto según su
complejidad y **la eficacia va primero**.

Mediciones ya existentes, citadas verbatim:

- **Instrumento** (`docs/specs/005-002-session-context-meter/closure.md` §1: «un formato de medición
  neutral respecto del runtime (opcional para la metodología) y su primer adaptador: un lector de solo
  lectura de las sesiones de OpenCode que informa, por sesión y por rol, tokens, lecturas, llamadas de
  herramienta y el momento del primer `resume`»; «**No enganchado en ningún gate** (medición opcional)»);
  decisión en `docs/adr/ADR-024-medicion-contexto-instrumento-opcional-readonly-no-gate.md`.
- **Antes** — `docs/specs/005-003-orientation-reduction/acceptance.md` §9 (instalación `0650655`):
  **74 llamadas previas**, **399.082 car.** de salida previa, **5,02 min** hasta el despacho.
- **Después (OpenCode)** — `docs/specs/005-007-progressive-planning/acceptance.md` §7 (instalación
  `9d89a4b`): **70 llamadas previas**, **304.054 car.** de salida previa (−24 %), **7** comandos sobre
  `docs/.cdad-state.json`, **0** ediciones manuales para abrir la unidad (`open-unit`), **5,82 min**
  (medidor) y despacho **detectado por el medidor** (`observed`, llamada 71).
- **Después (por runtime)** — `docs/specs/005-011-common-entry/acceptance.md` **AC-7 (Claude Code)**:
  primer `Agent` de la llamada **23** a la **14**; salida previa de **105 mil** a **54 mil caracteres
  (−49 %)**; duración **8,7 → 3,0 min**. **AC-6 (OpenCode, corrida 3, `7212ead`)**: skill en la llamada
  **1**; `status` en la llamada **3** en vez de la 21; primer despacho **71 → 59 (−17 %)**; salida previa
  **304 mil → 296 mil (−3 %)**; tiempo **5,8 → 4,7 min**. **Brecha declarada**: la lectura del state
  completo en la llamada 2 (**53 mil caracteres**) precede a la vista.

### 3. Finalización frente a publicación

Cerrar el epic **no implica publicar**. El **saneamiento** de contenido está hecho (`a367b8c`, `29a4805`)
y está registrada la decisión del dueño de publicar **con historial nuevo**; el **historial privado se
conserva** para la trazabilidad de la evidencia (`execution.md` §Pendientes para el cierre). **A3** queda
solo con **falsos positivos de un patrón local no acotado**, y **lo acota el dueño** — no se convierte en
un ciclo.

## Retrospectiva breve

**Qué funcionó bien**

- El **criterio de review vigente (2026-10-12)** —bloquear y corregir ya lo que compromete el resultado, la
  evidencia o el uso previsto— produjo correcciones inmediatas y no por proximidad: **R1** de la reapertura
  de 005-002, **B1/B2/B3** de 005-012 y **B1** de 005-013 (`execution.md` §Criterio de review vigente).
- La **review formal de familia distinta** encontró escapes del contrato numerado que los focales verdes no
  veían: en 005-012, **B1** (la comprobación de autoridad de PD-6 no aplicada a `closure`) y **B2** (una
  identidad que tragaba invocaciones distintas como no-op afirmativo) (`docs/specs/005-012-transition-registration/closure.md` §3).
- **Unidades que se miden y se corrigen a sí mismas**: 005-012 se cerró con la operación que entrega —de
  sus **32** entradas de tramo, **26 las registró la operación** y 6 a mano, cada una con su motivo
  declarado (`closure.md` §6)— y 005-014 se cerró con `register-transition --transition closure`,
  repitiendo la orden idéntica como no-op (`docs/specs/005-014-closure-replay/closure.md` §7).

**Qué se complicó**

- La **medición**: con **una sola sonda por variante** es **indicativa, no estadística** (`plan.md`
  §Riesgos). AC-6 quedó **cumplido en parte y declarado así**, con la causa del orden estricto **no
  demostrada** (`docs/specs/005-011-common-entry/acceptance.md`, decisión del gate T4; `debt.md` RD-b).
- El **comportamiento nuevo no existía en la versión instalada** hasta el despliegue: quedó como bloqueo
  declarado con responsable (dueño) en 005-012 (§4 «Despliegue pendiente») y 005-013, sin declararlo verde
  por proximidad.
- **Tres reaperturas** dentro del epic (B1 de 005-010, el criterio de review nuevo sobre 005-002, F2 de
  005-003), con un mecanismo acotado de reapertura (RED/GREEN focales, worktree fijado, cierre con nota).

**Lecciones**

- **El RED puede refutar el contrato:** en 005-014 el focal expuso una contradicción interna del v1 y la
  **enmienda precedió al GREEN**; igual patrón en B2 y B3 de 005-012.
- **El rol que se detiene cuando debe es evidencia, no un fallo:** en T3 de 005-012 el RED declaró **7/8**
  focales rojos y el bloqueo declarado resultó ser un defecto del **fixture** del test, no del producto; lo
  resolvió un testfix que tocó **solo** la precondición, sin tocar aserciones.
- **El gate de la suite de cierre ve regresiones que los focales no:** en 005-003 el intento de cierre
  encontró una **regresión real** sobre un oráculo de **otra** feature (`docs/specs/005-003-orientation-reduction/closure.md` §4).
- **El state crece:** al cierre de 005-012 el state pasa de **440 KB con 447 entradas**
  (`docs/specs/005-012-transition-registration/debt.md` D-3); al cierre de 005-011 pesa **~530 KB**,
  **~486 KB** en `stage_history` (`execution.md` §Pendientes para el cierre).

## Deuda priorizada que queda

| Deuda | Dueño / condición de cierre | Puntero |
|---|---|---|
| **RD-a — adopción de versión entre ciclos:** que un proyecto adopte una versión elegida entre ciclos y prepare y compruebe sus derivados **antes de abrir la sesión** | Cierre: que la primera sesión después de un despliegue use el prompt/orquestador de la versión adoptada; **no** republicar todos los proyectos en cada despliegue | `docs/specs/005-011-common-entry/debt.md` (RD-a); `execution.md` §Pendientes para el cierre |
| **RD-b — state operativo compacto con historia durable:** las autorizaciones vigentes, contratos, trabajo pendiente y la evidencia para reconciliar una interrupción deben seguir accesibles en el estado operativo | Cierre: que **leer el state completo cueste un orden de magnitud menos sin perder la historia** (archivada y referenciada), medido con el medidor y conteo propio | `docs/specs/005-011-common-entry/debt.md` (RD-b); `execution.md` §Pendientes para el cierre |
| **E-1 (priorizada) — `gate` ignora `--feature` en silencio:** la entrada queda huérfana | Cierre: una unidad que haga actuar/validar `--feature` en todas las clases, con RED (arreglo distinto al de 005-014) | `docs/specs/005-014-closure-replay/debt.md` |
| **E-2 (priorizada) — replay tras un cambio de feature activa:** la identidad incluye `execution_id` y `open-unit` acuña una ejecución nueva, así que no hay no-op | Cierre: una unidad que decida comparar el payload sin `execution_id` o buscar la ejecución de la feature, con RED | `docs/specs/005-014-closure-replay/debt.md` |
| **D-10 de 005-012 — autoridad sin delegación a nivel del estado:** la vigencia del state sigue exigiendo `hitl_delegation` con epic activo | Cierre: una unidad de **autoridad/HITL** (005-001 es dueño de la regla) que decida si el dueño sin delegación es autoridad vigente a nivel de estado | `docs/specs/005-012-transition-registration/debt.md` D-10 |
| **Mejora futura, sin unidad ni prioridad:** adaptador `cdad_delegate` → Claude Code (`claude -p --agent cdad-<rol>`, paquete por stdin, `--output-format json`), a verificar el aislamiento del test-writer antes de usarlo | Decisión del dueño, sin prioridad; coincide con D-3 de 005-004 | `execution.md` §Pendientes para el cierre |

El resto de la deuda del epic está **consolidada con su condición de cierre** en el `debt.md` de cada
feature (D-1..D-16 de 005-012, con D-9 retirada; O-1..O-4 de 005-014; O2..O5 y D-1..D-3 de 005-013;
OP-3..OP-5 de 005-011; R2–R5 y D6 de 005-002; MIX-V6V7 y demás de 003-007). La **F011** de `make validate`
es **preexistente** y se declara en cada cierre.

## Planificación siguiente

Estas prioridades **se registran en el cierre y no abren un epic nuevo ni unidades nuevas**:

1. **Adopción de versión entre ciclos (RD-a).**
2. **State operativo compacto con historia recuperable (RD-b).**
3. **Reducción proporcional de instrucciones y preparación**, medida en desarrollos reales y **separando
   la coordinación del desarrollo**; incluye un **recorrido liviano para tareas simples**.

## Requisitos ya identificados

Además de lo anterior, van a la planificación siguiente (declarados, sin unidad todavía):

- **El tipo de artefacto para el ADR:** el scribe **no tiene un *kind* de ADR** en la tabla cerrada del
  producto (`projectbrief`/`systemPatterns`/`activeContext`/`progress`); hoy el ADR se materializa aparte o
  se cita por ruta + digest (`docs/specs/005-012-transition-registration/debt.md` §3, punto 3).
- **La autoridad del dueño sin delegación:** **D-10 de 005-012** (`debt.md`).
- **La deuda priorizada E-1 y E-2 de 005-014** (`debt.md`).

## Decisiones arquitectónicas del epic

Las decisiones del epic están documentadas **por feature**; **ninguna nueva** se agrega en este cierre.

| ADR | Decisión (título) | Estado / confianza |
|---|---|---|
| [ADR-019](../adr/ADR-019-aprobacion-por-rol-nombra-el-contrato-reemplazo-conserva-el-encargo.md) | La aprobación de contrato por rol nombra el contrato; el reemplazo conserva y corrige el encargo anterior | **Aceptado** (2026-10-09) · Confianza **Media** |
| [ADR-020](../adr/ADR-020-politica-unica-de-evidencia-y-procedencia-declarada.md) | Una sola política de evidencia con dueño canónico y la procedencia de la instalación declarada en el artefacto publicado | **Aceptado** (2026-10-09) · Confianza **Media** |
| [ADR-021](../adr/ADR-021-arranque-guiado-procedimiento-corto-por-referencia.md) | El arranque desde reposo se resuelve con un procedimiento corto que compone por referencia, una entrada de intake y un dueño canónico por objeto de reconocimiento | **Aceptado** (2026-10-10) · Confianza **Media-Alta** |
| [ADR-022](../adr/ADR-022-mapas-de-permisos-derivados-coherentes-con-el-clasificador.md) | Los mapas de permisos derivados son una proyección coherente del clasificador único: la excepción de tests reabre solo lo declarado y `private` gana por findLast | **Aceptado** (2026-10-10) · Confianza **Media-Alta** |
| [ADR-023](../adr/ADR-023-delegacion-externa-interfaz-comun-adaptador-por-destino.md) | La delegación externa entre CLI es una interfaz común con un adaptador por destino; la entrega no aprueba el gate y la delegación no amplía autoridad | **Aceptado** (2026-10-11) · Confianza **Media-Alta** |
| [ADR-024](../adr/ADR-024-medicion-contexto-instrumento-opcional-readonly-no-gate.md) | La medición de contexto es un instrumento opcional, read-only y no-gate | **Accepted** (2026-10-11) · Confianza **Media** |
| [ADR-025](../adr/ADR-025-orientacion-proyeccion-readonly-y-contrato-aplicable-del-encargo.md) | La orientación al retomar es una proyección read-only del estado y el encargo de tarea trae su contrato aplicable | **Proposed** (2026-10-12) · Confianza **Media** |
| [ADR-026](../adr/ADR-026-roles-cdad-activos-en-claude-code-mecanismo-nativo.md) | Los roles CDAD se activan en Claude Code por el mecanismo nativo (`Agent`/`subagent_type`), reusando paquete, I8, `receive` y `reconcile` | **Proposed** (2026-10-13) · Confianza **Media-Alta** |
| [ADR-027](../adr/ADR-027-entrada-al-proceso-por-la-vista-compacta-en-skills-y-prompt-del-orquestador.md) | La entrada al proceso es la vista compacta `status` —en las skills y en el prompt del agente orquestador— y el state completo es ampliación condicional | **Proposed** (2026-10-14) · Confianza **Media** |
| [ADR-028](../adr/ADR-028-contrato-de-unidad-proyeccion-generada-pin-por-digest.md) | El contrato del architect es una proyección generada de la unidad, pineada por digest, con fallback declarado; el veredicto es por identidad y clase de parte | **Proposed** (2026-10-14) · Confianza **Media** |
| [ADR-029](../adr/ADR-029-registro-de-transiciones-identidad-por-contenido-vigencia-por-el-pin.md) | El registro de una transición es una operación del CLI con identidad por contenido, vigencia por el pin que nombra los bytes actuales y un cierre que comprueba antes de aplicar | **Proposed** (2026-10-14) · Confianza **Media** |
| [ADR-030](../adr/ADR-030-replay-de-cierre-identidad-resuelta-desde-la-ejecucion-ligada-y-techo-sin-feature-activa.md) | La repetición de un cierre se decide por identidad resuelta desde la ejecución ligada, y sin feature activa la operación nunca aplica un cierre | **Proposed** (2026-10-14) · Confianza **Media** |

## Límites declarados

- **Con el epic cerrado, `status` conserva la ruta `next unit`** (no tiene un modo «sin epic») y
  **`open-unit` responde rc=2** con el mensaje literal del producto
  `no 'queued' unit in epic_features: there is nothing to open`
  (`skills/cdad-cycle/scripts/cdad_packet.py:4555`), **sin efectos sobre el state** —verificado por el
  orquestador el 2026-10-14 sobre un proyecto desechable—. **No compromete resultado, evidencia ni uso
  previsto** (criterio vigente 2026-10-12): se declara y **no se abre un ciclo**.
- El **informe de medición no tiene documento consolidado aparte**: vive en las secciones citadas
  (005-003 §9 «antes»; 005-007 §7 y 005-011 AC-6/AC-7 «después»). Se declara así.
- **Una sola sonda por variante** → la medición es **indicativa, no estadística** (`plan.md` §Riesgos).
- El **producto nuevo existe en el repo y en la instalación `29a4805`**, pero **el servidor de OpenCode no
  se reinició** y los derivados de este repo todavía declaran la versión anterior (**DRIFT**, pierna
  `project`); lo resuelve el próximo `prepare`.
- El **criterio 5 está no ejecutado** y depende del dueño del consumidor; se declara, **no se convierte en
  verde ni bloquea el cierre**.
- **El cierre del epic se registró a mano en el state**: no existe operación del CLI para el cierre de un
  epic (`register-transition` cubre clases por feature y su clase `closure` exige feature activa y contrato
  pinneado). Se declara.
- **Quedó fuera del cierre la observación de redacción de PD-1** (contradicción PD-1 vs PD-2/INV-5,
  anotada en el cierre de 005-007 «para el cierre del epic»): no se resolvió y sigue como deuda de
  redacción, sin unidad.
- **Las aceptaciones que esperaban el despliegue no se repitieron acá** (005-003 A1/A2/A6, 005-007 D-1,
  la R2 real de 005-006): el despliegue del 2026-10-14 quitó la condición de bloqueo, pero la corrida
  sigue pendiente del dueño. Sólo se corrió el recorrido registrado en `execution.md` (repetir el cierre
  de 005-014 con el CLI instalado: no-op, rc=0, state intacto).

## Veredicto

El epic se cierra con las **14/14 unidades en `done`**, cada una con su cierre y su evidencia, con los
**criterios 1 a 4 verificados** —con los límites declarados de RD-a, D6 y MIX-V6V7— y el **criterio 5 no
ejecutado y declarado**. El cierre **no implica publicar**: el saneamiento de contenido está hecho y la
decisión de publicar con historial nuevo es del dueño. El epic entrega una base **más fiable** —contratos,
planificación progresiva, medición opcional, delegación entre runtimes, registro de transiciones y
reanudación tras una interrupción, con menos edición manual del state— y deja explícito lo que **no**
demostró: que la carga de coordinación sea pequeña y proporcional en todos los desarrollos, con las
mediciones disponibles como orientación y no como umbral. **Sin push y sin publicar.**
