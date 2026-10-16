> Plan **v2 (etapa 2, subetapa `draft`, enmienda 001), SIN APROBAR.** Lo redacta el **architect**. Se
> aprueba junto con la spec, por el **orquestador Claude** bajo la HITL delegada del epic-006
> (`docs/epics/epic-006-opencode-concurrency/execution.md`) o por el dueño. El architect no aprueba su
> propia propuesta.
>
> - **Contrato:** `docs/epics/epic-006-opencode-concurrency/plan.md` (sha256 `a8e415f7…`), §5, y el cambio
>   de alcance aprobado por el dueño (`execution.md:38-63`).
> - **Base:** spec v2 (§2.3b, §5.5, PD-13, PD-14, D-9..D-13) y plan v1. Sigue el formato `plan-tasks` de
>   `docs/specs/005-011-common-entry/plan.md` §4.
> - **Tramo conservado:** T1 está en GREEN; T2 tiene su RED registrado (commit `8447443`). La enmienda
>   **suma T1b** encima de T1 y ajusta T2/T3.
> - **Valores:** sin valores del host (`<ROOT>`, `<provider>`, `<VAR>`, `<bin>`, `<m>`, `<url>`, `<state>`).
> - **Validación del bloque (solo lectura):** pasé el bloque por `_plan_tasks_from_contract`,
>   `_check_plan_tasks` y `_check_plan_validation_plan`: **OK**, tareas T1, T1b, T2 y T3 con estrategia
>   declarada. `_plan_task_applicable_ids(_plan_task_ficha(...))` no queda vacío para ninguna de las cuatro.

# Plan — 006-001-opencode-concurrency-reliability (v2)

## 1. Ficha de la feature

- **Feature ID:** `006-001-opencode-concurrency-reliability` · **Epic:** `epic-006-opencode-concurrency` ·
  **Estado:** DRAFT (etapa 2, enmienda 001).
- **Resultado buscado:** selección de ejecución explícita y verificable —con `server`, `service` y
  `standalone`—, espera proporcional y recuperación que conserva la correlación (spec §1), con
  PD-1..PD-14. AC-7 queda en la recepción.
- **Instalación estable del ciclo:** la registrada en `execution.md`. La candidata se construye y valida
  en una raíz aislada; no se despliega.

## 2. Unidades → tareas

| Unidad del epic §5 | Tarea | PD | Por qué así |
|---|---|---|---|
| T1 | **T1** | PD-1..PD-5 | Selección, preflight de servidor, procedencia y secretos: todo lo que ocurre antes de `run` y el registro de cada intento. **Entregada (GREEN, commits `4bc8934`, `a96c2d8`).** |
| T1 (enmienda) | **T1b** | PD-1, PD-2, PD-3, PD-4, PD-5, PD-13, PD-14 | El **modo servicio** encima de T1: `service status`, gate de versión, despacho sin flags, fallback declarado y procedencia. Mismo archivo que T1 (`depends_on: [T1]`). |
| T2 | **T2** | PD-7..PD-11 | Espera, clasificación y recuperación. Comparte archivo: **serializada** con T1 y **T1b** (`depends_on: [T1, T1b]`). Su RED ya está registrado y **no cambia** (espera y recuperación son independientes del modo). |
| T3 | **T3** | PD-6, PD-12 | Integración concurrente (fixture y dos recorridos reales), referencia, config de ejemplo y candidato. Cierra el código: suite completa una vez y review independiente. |

`parallel: []` en todas, porque las cuatro tocan el adaptador o dependen de él.

**Por qué T2 depende de T1b:** T2 modifica el mismo archivo que T1b
(`skills/cdad-cycle/scripts/cdad_delegate_opencode.py`); la regla de v1 («comparte archivo ⇒ serializada»)
se extiende a T1b. El RED de T2 ya registrado (commit `8447443`) no se ve afectado: escribe un fake propio
y fabrica su propio registro previo, y sus aserciones de procedencia parsean por subcadena
(`store_reads=`), así que los pares nuevos de T1b (agregados **al final**) no lo rompen.

## 3. Estrategia de validación (declarada una vez)

- **Siempre:** procedencia, `git diff` contra el alcance, focales de la tarea (segundos, con los valores
  chicos de spec §2.1) y regresiones del adaptador.
- **RED:** el focal falla por aserción, no por import ni sintaxis, y se comprueba en un **worktree**,
  nunca con `git stash`.
- **GREEN:** focal verde más regresiones.
- **Suite completa una sola vez,** al cierre de código (T3), la corre quien cierra. Solo se repite si un
  cambio o una evidencia invalidada lo justifican.
- **Review formal e independiente al final** (familia distinta a la del implementer). Después, una
  re-review solo de bloqueantes; las variantes sin impacto material van a deuda.
- **El sentido de `cli-delegation.md` lo juzga la review.** No hay tests de listas de palabras.
- **Oráculos que cambian** (los autoriza el orquestador al aprobar). El test-writer los ajusta en el RED
  de su tarea; el implementer no edita tests:
  1. **T1 (ya hecho).** `tests/test_005_010_t2_load_mode_invocation.py:361-385` sirve `/api/info` desde un
     fixture en loopback con la versión del fake, en vez de `fixture.invalid` (`:94`). Se conserva la
     aserción de argv. *(spec D-1)*.
  2. **T1 (ya hecho).** El fake compartido de `tests/test_005_009_t2_opencode_adapter.py` responde
     `--version` **antes** de escribir el store o registrar la llamada (hoy después, `:879-880`).
  3. **T1b (nuevo, sin cambio de oráculo).** El focal de T1b usa un **binario falso propio** que registra
     cada invocación (argv, en orden) y responde: `service status` (URL o `stopped`), `--version`, y `run`.
     No toca el fake compartido ni los focal de T1/T2.
  4. **T2 y T3 (sin cambio de oráculo).** Cada focal mantiene su fake propio.
- **Oráculos que deben seguir verdes sin cambio:**
  - `NEVER_INVOKED_TOKENS` de T1 (`tests/test_006_001_t1_selection.py:195`, usado en `:648`): su alcance
    es el **modo servidor**, donde `service status` no se invoca. El focal de T1b declara su **propio**
    conjunto refinado: permite `service status`, prohíbe `serve`,
    `service start|stop|restart|get|set|unset` y `reload`.
  - Los pares de procedencia de T1 (`:960-966`) y el parseo por subcadena de T2 (`store_reads=`).
  - las asignaciones de llamada única (`:287`, `:1139`, `:1400`; spec D-2);
  - `"no-idle": "timeout"` (`:399`); `TEST_WAIT_TIMEOUT_SECONDS = 2` (`:417`; spec D-3);
  - `transport-error` inmediato (spec D-4).
- **Sin `--no-verify`, sin push, sin desplegar, sin tocar HOME,** sin leer `tests/.sensitive-patterns.local`,
  sin ejecutar `service get|set|start|stop|restart` ni reiniciar/reconfigurar el servicio vivo.

## 4. Fichas mínimas de tarea y bloque canónico

### T1 — Selección de modo, preflight del servidor, procedencia por intento y secretos *(entregada)*
- **Resultado observable / PD cubiertas:** PD-1, PD-2, PD-3, PD-4, PD-5; INV-2, INV-4, INV-6, INV-9; D-1, D-2, D-5.
- **Estado:** GREEN (commits `4bc8934`, `a96c2d8`; informe `t1-green.md`).
- **Alcance entregado:** leer/validar `mode` (server|standalone) y las claves `wait.*`; preflight de
  servidor con el orden de contraseñas del cliente; procedencia de §2.6 y registro del worker en toda
  terminación; redacción de URL y contraseña.
- **Archivos:** *Modify* `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`,
  `tests/test_005_010_t2_load_mode_invocation.py` (oráculo 1) y `tests/test_005_009_t2_opencode_adapter.py`
  (fake, oráculo 2); *Test* `tests/test_006_001_t1_selection.py`.
- **Verificación:** focal `python3 -m pytest tests/test_006_001_t1_selection.py -q -p no:cacheprovider`
  (18 passed en el GREEN) y las regresiones de su ficha.
- **Herencia a T1b:** `VALID_MODE_VALUES` debe pasar a `("server","service","standalone")`; el resto de la
  maquinaria de selección se reusa.

### T1b — Modo servicio configurado *(nueva)*
- **Resultado observable / PD cubiertas:** PD-1, PD-2, PD-3, PD-4, PD-5, PD-13, PD-14; INV-2, INV-6, INV-10; D-9, D-10, D-11, D-12, D-13.
- **Alcance incluido:**
  - aceptar `"service"` en `mode` y la clave booleana `service.require` (spec §2.1) con validación antes
    del despacho;
  - la fila `service` de la tabla §2.2 y el preflight de servicio de §2.3b: `service status` acotado, la
    interpretación cerrada (URL / `stopped` / inesperado) y el despacho **sin flags**;
  - el gate de versiones de §2.3b punto 2 con el mecanismo de **D-11** (`--version` del cliente solo
    cuando el servicio corre);
  - el fallback declarado y contable (`fallback=service-unavailable`) y la variante estricta
    (`service.require: true` → `blocked`);
  - los pares nuevos de procedencia de §2.6 (`dispatch_flags=`, `service_status=`, `fallback=`) y el
    valor `service` en `mode_requested`/`mode_effective`;
  - la redacción/extensión de PD-5: la salida de `service status` se descarta salvo el discriminante y la
    URL del servicio no entra en ninguna salida.
- **Excluido:** la espera, el `Popen` y la comprobación del intento previo (T2); reiniciar, arrancar,
  detener o configurar el servicio (fuera de alcance); tocar `cdad_delegate.py` o el esquema I8.
- **Consume:** `execution-selection` (`execution-selection-v1`) de T1. **Produce:** `service-selection`
  (`service-selection-v1`).
- **Dependencias:** T1 (mismo archivo).
- **Archivos:**
  - *Modify* `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`;
  - *Test* `tests/test_006_001_t1b_service_mode.py` (nuevo, con binario falso propio).
- **Contexto por rol:**
  - **RED:** spec §2.1-§2.3b, §2.6 y §3 (PD-13, PD-14, y las filas de `service` de PD-1/PD-2/PD-3/PD-5);
    `cdad_delegate_opencode.py:107-124,517-599,610-642,689-771,1090-1118,1206-1260`;
    `test_006_001_t1_selection.py:195,648,960-966`.
  - **GREEN:** ídem.
- **Evidencia al re-entry:**
  - focal rojo→verde con: la matriz `service` completa (corre+compatible → sin flags; no corre →
    standalone con `fallback=service-unavailable`; no corre + `service.require: true` → `blocked`; corre
    e incompatible → `blocked`; `service status` con respuesta inesperada → `blocked`); el orden de
    invocaciones en modo servicio (`service status`, `--version`, `run`) y la ausencia de invocaciones de
    gestión (`serve`, `service <start|stop|restart|get|set|unset>`, `reload`); los pares de procedencia
    nuevos (con `store_reads`/`prior_check_reads` intactos al final de `provenance.session`); y el barrido
    de la contraseña centinela **y** de la URL del servicio;
  - `git diff` acotado al adaptador y al focal nuevo;
  - `cdad_delegate.py` sin cambios.
- **Verificación RED→GREEN:**
  - focal: `python3 -m pytest tests/test_006_001_t1b_service_mode.py -q -p no:cacheprovider`;
  - regresiones: `python3 -m pytest tests/test_006_001_t1_selection.py tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py tests/test_005_010_reviewfix.py tests/test_005_010_b1_last_assistant.py -q -p no:cacheprovider`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:**
  - **Si el orquestador no ratifica D-11 (fuente de la versión del servicio), DETENER antes del GREEN** y
    volver al orquestador con la alternativa (B) y su conflicto declarado (spec §6 D-11);
  - si el fake de T1b necesitara tocar el fake compartido o un focal de T1/T2, **detener**;
  - si algún oráculo vigente distinto de los tres declarados cambia, **detener** y reportarlo antes de
    tocarlo.

### T2 — Espera proporcional, clasificación, correlación, terminación ordenada e intento previo *(ajustada)*
- **Resultado observable / PD cubiertas:** PD-7, PD-8, PD-9, PD-10, PD-11; INV-1, INV-3, INV-10; D-3, D-4, D-6.
- **Estado:** RED registrado (commit `8447443`, `t2-red.md`). **El RED no cambia** con la enmienda.
- **Alcance incluido:** `Popen` con grupo propio y terminación ordenada; cero lecturas mientras el cliente
  vive; backoff y validación de esquema una vez por intento; la tabla de clasificación de §2.4 con el
  `error` durable de `failed`; `session` elegida en toda terminación posterior a `run`; comprobación del
  intento previo (§2.7); reserva y gracia de §2.5; conteo `store_reads`.
- **Ajuste de la enmienda (sin tocar el RED):** la ficha consigna explícitamente que la comprobación del
  intento previo aplica **igual** tras un `timeout` en modo servicio o servidor y que ningún camino de
  recuperación re-despacha solo, arranca el servicio ni abre un standalone. Es una precisión de contrato
  (PD-9/PD-10/INV-10), no un test nuevo.
- **Excluido:** reintentos automáticos; abortar sesiones del servidor; cambiar el vocabulario; la
  gestión del servicio.
- **Consume:** `execution-selection` (`execution-selection-v1`) de T1. **Produce:** `wait-recovery`
  (`wait-recovery-v1`).
- **Dependencias:** T1, **T1b** (mismo archivo; serializada).
- **Archivos:** *Modify* `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`; *Test*
  `tests/test_006_001_t2_wait_recovery.py`.
- **Contexto por rol:**
  - **RED/GREEN:** spec §2.4-§2.7 y §3 (PD-7..PD-11); `cdad_delegate_opencode.py:432-505,1024-1060`;
    `cdad_delegate.py:131-162,252-283`; `test_005_009_t2_opencode_adapter.py:242-250,399,417`;
    discovery D4 (`:124-145`).
- **Evidencia al re-entry:** focal rojo→verde con fake propio y las variantes de su informe; `store_reads`
  contra la cota; PD-11 en sus tres variantes; `git diff` acotado.
- **Verificación RED→GREEN:** focal
  `python3 -m pytest tests/test_006_001_t2_wait_recovery.py -q -p no:cacheprovider`; regresiones (lista
  del bloque, con `tests/test_006_001_t1b_service_mode.py` incorporado).
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** las de v1; si el margen de `test_005_010_reviewfix.py` (ya declarado por
  T1 GREEN) vuelve a fallar por su guarda de tiempo, reportarlo al orquestador **sin** tocar la lógica de
  selección.

### T3 — Integración concurrente (fixture y dos recorridos reales), referencia, config de ejemplo y candidato *(ajustada)*
- **Resultado observable / PD cubiertas:** PD-6, PD-12; INV-2, INV-6, INV-7; D-7, D-8.
- **Alcance incluido:**
  - focal de concurrencia con fixture (dos proyectos, mismo store y mismo servidor de fixture);
  - test real con opt-in por entorno (spec §5): servidor descartable, credencial por `{env:<VAR>}`, guarda
    `debug paths`, dos delegaciones concurrentes y el complemento standalone;
  - **recorrido real en modo servicio contra el servicio VIVO** (spec §5.5): un despacho y luego dos
    concurrentes, con encargo mínimo, uso normal del servicio, sin reiniciarlo ni reconfigurarlo, con la
    atribución de AC-1 (D-12);
  - observaciones VERIFY de spec §10;
  - `cli-delegation.md` (modos `server|service|standalone`, claves, preflight de servidor y de servicio,
    fallback y `service.require`, clasificación, límites, receta de aislamiento, responsable del servidor
    y **del servicio**: el servicio lo gestiona el dueño/operador, CDAD no);
  - `skills/cdad-cycle/assets/opencode-exec-config.example.json` con `mode: "service"` y `service.require`;
  - candidato en raíz aislada;
  - suite completa una vez y review independiente.
- **Excluido:** desplegar en HOME; tocar el runtime, la base viva **o el servicio**; AC-7.
- **Consume:** `execution-selection` (T1), `service-selection` (`service-selection-v1`, T1b),
  `wait-recovery` (T2). **Produce:** `concurrency-acceptance` (`concurrency-acceptance-v1`).
- **Dependencias:** T1, T1b, T2.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/references/cli-delegation.md` y
  `skills/cdad-cycle/assets/opencode-exec-config.example.json`; *Test* `tests/test_006_001_t3_concurrency.py`
  (focal, fake propio) y `tests/test_006_001_t3_integration.py` (recorrido real, en `observable_checks`).
- **Contexto por rol:** spec §3 (PD-6, PD-12), §5 y §5.5; `test_005_010_t4_integration.py:169-342`
  (helpers de proyecto real, reutilizables); discovery §4 (`:243-316`); `execution.md:48-55`.
- **Evidencia al re-entry:**
  - focal de concurrencia rojo→verde;
  - informe del recorrido real en modo **servidor** (dos `completed`, nonces separados, versión, config
    anonimizada, carga, tiempos, `store_reads`) y del recorrido real en modo **servicio contra el servicio
    vivo** (terminación, modo efectivo, `service_status`, `server_version`, `fallback`, tiempos, errores,
    y la atribución de AC-1); complemento standalone; observaciones VERIFY;
  - declaración explícita de que la eliminación de bloqueos **no** se demuestra (observación de la
    recepción, AC-7);
  - `make validate` sin fallos nuevos; candidato aislado `--check` OK; suite completa; review
    independiente; barrido de saneamiento sin hallazgos.
- **Verificación:**
  - **focal:** `python3 -m pytest tests/test_006_001_t3_concurrency.py -q -p no:cacheprovider`;
  - **real (servidor):** la corre el orquestador con la credencial del operador:
    `CDAD_OPENCODE_INTEGRATION=1 CDAD_OPENCODE_BINARY=<bin> CDAD_OPENCODE_MODEL=<m> CDAD_OPENCODE_KEY_ENV=<VAR> python3 -m pytest tests/test_006_001_t3_integration.py -q -p no:cacheprovider`;
    sin `<VAR>` definida se omite, y la omisión deja PD-6 en BLOQUEO;
  - **real (servicio vivo):** el despacho y los dos concurrentes de §5.5, corridos por el orquestador o el
    dueño con autorización, sin reiniciar ni reconfigurar el servicio;
  - **referencias:** `python3 -m pytest tests/test_005_010_t3_references.py -q -p no:cacheprovider` y
    `make validate`;
  - **candidato:** `make staging`, `HOME=<tmp> bash install.sh --force`,
    `HOME=<tmp> bash install.sh --check`;
  - **cierre de código, una vez:** `python3 -m pytest tests -q -p no:cacheprovider`;
  - **saneamiento (orquestador):** `python3 .cdad/local/sanitize.py .`, sin `--apply`.
- **Integración / responsable:**
  - **Gate de cierre de código de la feature:** PD-6 aceptada solo con la evidencia de los recorridos
    **reales** (servidor y servicio vivo); el fixture no basta y una omisión no es un pase; suite completa
    una vez; review independiente con re-review de bloqueantes.
  - **Responsables:** RED test-writer; GREEN implementer; recorridos reales y suite, el orquestador;
    review, el reviewer.
- **Incertidumbres / detención:**
  - si la guarda `debug paths` no confina `db/data/state/log` bajo `<ROOT>`, **detener** sin despachar;
  - si la credencial por `{env:<VAR>}` falla (spec §5.3, VERIFY b), **detener** y volver al orquestador
    con la alternativa (B);
  - si el recorrido contra el servicio vivo exigiera reiniciar, recargar o reconfigurar el servicio,
    **detener**: está reservado al dueño, y PD-6 queda en BLOQUEO declarado.

### Bloque canónico `plan-tasks`

```plan-tasks
{
 "validation_strategy": "Verificacion en dos niveles: siempre procedencia + git diff contra el alcance + focales de la tarea (segundos, con valores de espera chicos en los fixtures) + regresiones del adaptador; RED falla por asercion y se comprueba en worktree, nunca git stash. La suite completa se corre una sola vez al cierre de codigo (T3), por quien cierra, y solo se repite si cambios o evidencia invalidada lo justifican; se reutiliza evidencia equivalente con procedencia verificada (skills/cdad-cycle/references/re-entry.md, Equivalence of a registered run). Review formal independiente al final con re-review de bloqueantes. El sentido de los textos lo juzga la review. Oraculos que cambian, declarados en el plan seccion 3: el de modo servidor de test_005_010_t2_load_mode_invocation.py y el --version del fake compartido. La seleccion de modo incluye el modo servicio: el focal de T1b usa su propio binario falso que responde `service status` (URL o `stopped`) y su propio conjunto de tokens prohibidos (permite `service status`, prohibe `serve`, `service start|stop|restart|get|set|unset` y `reload`); nunca reinicia, arranca ni reconfigura el servicio ni un servidor real.",
 "tasks": [
  {
   "id": "T1",
   "objective": "Seleccion de modo explicita y compatible hacia atras sin fallback, preflight del modo servidor (version y credencial por entorno en el orden del cliente), procedencia por intento en texto libre del esquema I8 cerrado y registro del worker en toda terminacion, sin secretos ni URL en las salidas.",
   "produce": [
    {
     "artifact": "execution-selection",
     "contract": "execution-selection-v1"
    }
   ],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_delegate_opencode.py",
    "tests/test_005_010_t2_load_mode_invocation.py",
    "tests/test_005_009_t2_opencode_adapter.py"
   ],
   "focal_tests": [
    "tests/test_006_001_t1_selection.py"
   ],
   "regressions": [
    "tests/test_005_009_t1_interface.py",
    "tests/test_005_009_t2_opencode_adapter.py",
    "tests/test_005_010_t1_durable_signal.py",
    "tests/test_005_010_t2_load_mode_invocation.py",
    "tests/test_005_010_reviewfix.py",
    "tests/test_005_010_b1_last_assistant.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "T1b",
   "objective": "Modo `service` configurado: comprobar con `service status` si el servicio de fondo corre y si su version es compatible con el cliente; despachar SIN `--server`/`--standalone` cuando corre y es compatible; declarar en la procedencia el fallback `service`->`standalone` con su causa SOLO cuando `service status` informa que no corre (o `blocked` con `service.require`, o `blocked` cuando corre pero la version difiere o no es verificable); nunca arrancar, reiniciar, detener ni configurar el servicio; sin secreto del servicio en argv, diagnostico, registros I8 ni recibo.",
   "produce": [
    {
     "artifact": "service-selection",
     "contract": "service-selection-v1"
    }
   ],
   "consume": [
    {
     "artifact": "execution-selection",
     "contract": "execution-selection-v1",
     "producer": "T1"
    }
   ],
   "depends_on": [
    "T1"
   ],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_delegate_opencode.py"
   ],
   "focal_tests": [
    "tests/test_006_001_t1b_service_mode.py"
   ],
   "regressions": [
    "tests/test_006_001_t1_selection.py",
    "tests/test_005_009_t1_interface.py",
    "tests/test_005_009_t2_opencode_adapter.py",
    "tests/test_005_010_t1_durable_signal.py",
    "tests/test_005_010_t2_load_mode_invocation.py",
    "tests/test_005_010_reviewfix.py",
    "tests/test_005_010_b1_last_assistant.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "T2",
   "objective": "Espera proporcional (cero lecturas con el cliente vivo, backoff acotado despues), clasificacion tras la salida del cliente con el error durable de failed, sesion elegida en toda terminacion posterior a run, terminacion ordenada del grupo propio con gracia efectiva, comprobacion del intento previo del mismo paquete (que aplica tambien tras un timeout en modo servicio o servidor, sin abrir un standalone para destrabar) y respuesta siempre dentro de la cota.",
   "produce": [
    {
     "artifact": "wait-recovery",
     "contract": "wait-recovery-v1"
    }
   ],
   "consume": [
    {
     "artifact": "execution-selection",
     "contract": "execution-selection-v1",
     "producer": "T1"
    }
   ],
   "depends_on": [
    "T1",
    "T1b"
   ],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_delegate_opencode.py"
   ],
   "focal_tests": [
    "tests/test_006_001_t2_wait_recovery.py"
   ],
   "regressions": [
    "tests/test_006_001_t1_selection.py",
    "tests/test_006_001_t1b_service_mode.py",
    "tests/test_005_009_t1_interface.py",
    "tests/test_005_009_t2_opencode_adapter.py",
    "tests/test_005_009_t3_spawn_reconciliation.py",
    "tests/test_005_009_t4_acceptance.py",
    "tests/test_005_010_t1_durable_signal.py",
    "tests/test_005_010_t2_load_mode_invocation.py",
    "tests/test_005_010_reviewfix.py",
    "tests/test_005_010_b1_last_assistant.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "T3",
   "objective": "Concurrencia util verificada con fixture permanente, con recorrido REAL en modo servidor contra un servidor descartable en loopback y con recorrido REAL en modo servicio contra el servicio VIVO desde un proyecto descartable (un despacho y luego dos concurrentes con encargo minimo, uso normal del servicio sin reiniciarlo ni cambiar su configuracion), observaciones VERIFY, referencia canonica y config de ejemplo portables, candidato en raiz aislada, suite completa una vez y review independiente.",
   "produce": [
    {
     "artifact": "concurrency-acceptance",
     "contract": "concurrency-acceptance-v1"
    }
   ],
   "consume": [
    {
     "artifact": "execution-selection",
     "contract": "execution-selection-v1",
     "producer": "T1"
    },
    {
     "artifact": "service-selection",
     "contract": "service-selection-v1",
     "producer": "T1b"
    },
    {
     "artifact": "wait-recovery",
     "contract": "wait-recovery-v1",
     "producer": "T2"
    }
   ],
   "depends_on": [
    "T1",
    "T1b",
    "T2"
   ],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/references/cli-delegation.md",
    "skills/cdad-cycle/assets/opencode-exec-config.example.json"
   ],
   "focal_tests": [
    "tests/test_006_001_t3_concurrency.py"
   ],
   "observable_checks": [
    "recorrido REAL en modo servidor con tests/test_006_001_t3_integration.py (opt-in por entorno, lo corre el orquestador con la credencial del operador): servidor descartable en loopback con contrasena aleatoria, store aislado bajo ROOT confirmado por la guarda debug paths, credencial por {env:VAR} sin copiar auth.json, dos delegaciones concurrentes de dos proyectos descartables que terminan completed con nonces separados y sesion propia; complemento standalone; observaciones VERIFY registradas; una omision por falta de credencial no es un pase",
    "recorrido REAL en modo servicio contra el servicio VIVO (lo corre el orquestador o el dueno, con el servicio en uso normal, sin reiniciarlo ni cambiar su configuracion): un despacho CDAD real desde un proyecto descartable con encargo minimo y despues dos concurrentes; se registran terminacion, modo efectivo (sin flags), modo solicitado y efectivo, service_status, server_version, fallback, tiempos, errores y store_reads; la atribucion a servicio se verifica por la fila durable (session_v2.version) y por el inventario de procesos (sin `serve --stdio`/`serve --service` nuevos durante el despacho); queda declarado que la ELIMINACION de bloqueos no se demuestra y que es observacion empirica de la recepcion (AC-7)"
   ],
   "regressions": [
    "tests/test_005_010_t3_references.py",
    "tests/test_006_001_t1_selection.py",
    "tests/test_006_001_t1b_service_mode.py",
    "tests/test_006_001_t2_wait_recovery.py",
    "tests/test_005_009_t4_acceptance.py"
   ],
   "integration_gate": "gate de cierre de codigo de 006-001: PD-6 aceptada solo con evidencia de los recorridos REALES (servidor y servicio vivo; el fixture no basta; una omision por falta de credencial no es un pase y deja BLOQUEO declarado), make validate sin fallos nuevos, candidato aislado con install.sh --check OK, suite completa una vez por quien cierra y review independiente con re-review de bloqueantes; AC-7 queda para la recepcion",
   "owner": "RED: test-writer; GREEN: implementer; recorridos reales y suite: orquestador; review: reviewer independiente"
  }
 ]
}
```

## 5. Trazabilidad PD/AC → tarea

| Tarea | PD | AC |
|---|---|---|
| T1 | PD-1, PD-2, PD-3, PD-4, PD-5 | AC-1, AC-2, AC-6 |
| T1b | PD-1, PD-2, PD-3, PD-4, PD-5, PD-13, PD-14 | AC-1, AC-2, AC-6 |
| T2 | PD-7, PD-8, PD-9, PD-10, PD-11 | AC-4, AC-5 |
| T3 | PD-6, PD-12 | AC-3, AC-8 |

AC-7 corresponde a la recepción.

## 6. Gate de la feature

- **La feature cierra el código cuando:**
  - PD-1..PD-5 y PD-7..PD-12 tienen focal rojo→verde con `git diff` acotado;
  - **PD-13 y PD-14 tienen focal rojo→verde** en `tests/test_006_001_t1b_service_mode.py`;
  - PD-6 tiene el fixture y los **dos recorridos reales** (servidor y servicio vivo);
  - la suite completa corrió una vez;
  - la review independiente no deja bloqueantes.
- **Sin la credencial del operador,** PD-6 queda en **BLOQUEO declarado**, con dueño y siguiente acción,
  nunca verde por proximidad. Lo mismo si el recorrido contra el servicio vivo exigiera algo reservado al
  dueño.
- **Después:** candidato, review, evidencia y receta de despliegue y rollback (epic §7). AC-7 sigue
  pendiente hasta el despliegue autorizado, junto con la acción de declarar `mode: "service"` en las
  configs del consumidor (D-9, DT-7).

## 7. Restricciones globales

- Sin push, sin `--no-verify`, sin desplegar y sin tocar HOME, la base viva, el consumidor **ni el
  servicio de fondo**.
- **No se ejecuta** `service get|set|start|stop|restart` ni `reload`, y no se lee ni se imprime el registro
  del servicio ni ningún archivo con contraseñas (solo nombres de claves y mecanismos). Solo se invoca
  `service status` (lectura) con entorno aislado mientras se desarrolla.
- No reiniciar, recargar ni terminar servidores compartidos ni el servicio. Solo se para el servidor
  descartable del test.
- Sin valores del host en la spec, el plan ni el producto. Los ids, rutas y tiempos crudos quedan en
  `.cdad/local/`.
- Nunca `git stash` en el árbol compartido: RED en worktree.
- Ante un obstáculo fuera de alcance: diagnóstico al orquestador, sin rodeos ni registros fabricados.

## 8. Estado, archivos y evidencia del rol

- **Estado:** DRAFT pendiente de la decisión del orquestador bajo la HITL delegada del epic-006 (junto con
  la spec v2). Sin marca de aprobación. Puntos de decisión: spec §13.
- **Archivos modificados por este rol:** **ninguno.** El rol es de solo lectura (write scope `[]`).
  `git status --short` sin salida y `git diff --stat` vacío en `HEAD 25e669b`.
- **Comandos exactos de la investigación (solo lectura; entorno aislado en el scratchpad):**
  - `opencode --version` → `opencode v2.0.27`, rc=0;
  - `opencode service --help`, `service status --help`, `service get --help`, `service set --help`,
    `service start --help`, `run --help`, `serve --help` → ayuda textual (subcomandos y flags);
  - `opencode service status` con `XDG_DATA/STATE/CACHE/CONFIG_HOME` bajo `<SP>` → `stopped`, rc=0;
  - `opencode debug paths` con el mismo entorno → `db`, `data`, `state`, `cache`, `log`, `config` bajo
    `<SP>`;
  - `strings -n 6 <bin> > <SP>/bin.strings` y ventanas acotadas con Python (sin imprimir valores de
    secretos);
  - una consulta `sqlite3 "file:<db>?mode=ro" "SELECT id, version, agent, time_created FROM session_v2
    ORDER BY time_created DESC LIMIT 3"` → las tres filas con `version = 2.0.27`;
  - validación del bloque `plan-tasks` con `_plan_tasks_from_contract`, `_check_plan_tasks` y
    `_check_plan_validation_plan` → OK (T1, T1b, T2, T3).
- **Commit evidence:** no hubo commit de este rol (solo lectura). El tramo de partida es `HEAD 25e669b`
  (T2 RED `8447443`, cambio de alcance `db7000e`, T1 GREEN `4bc8934`/`a96c2d8`).
- **No ejecutado (declarado):** `service get`, `service set`, `service start`, `service stop`,
  `service restart`; lectura de `service.json`, `auth.json` o cualquier archivo con contraseñas;
  despachos de sesiones reales; la suite completa (política de suite: la corre quien cierra, en T3).

## Decisión del orquestador (enmienda 001, 2026-10-16)

Aprobado junto con la spec v2 (spec §15), bajo la HITL delegada de epic-006.

Status: Approved by Claude orchestrator (HITL delegated by Pablo for epic-006) on 2026-10-16
