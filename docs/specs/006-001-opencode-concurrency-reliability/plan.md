> Plan **DRAFT (etapa 2, subetapa `draft`), SIN APROBAR.** Lo redacta el **architect**. Se aprueba junto
> con la spec, por el **orquestador Claude** bajo la HITL delegada del epic-006
> (`docs/epics/epic-006-opencode-concurrency/execution.md`) o por el dueño. El architect no aprueba su
> propia propuesta.
>
> - **Contrato:** `docs/epics/epic-006-opencode-concurrency/plan.md` (sha256 `a8e415f7…`), §5.
> - **Base:** discovery §4. Sigue el formato `plan-tasks` de `docs/specs/005-011-common-entry/plan.md` §4.
> - **Valores:** sin valores del host (`<ROOT>`, `<provider>`, `<VAR>`, `<bin>`, `<m>`).
> - **Validación del bloque (solo lectura):** pasé el bloque por `_plan_tasks_from_contract`,
>   `_check_plan_tasks` y `_check_plan_validation_plan`: **OK**, tareas T1..T3 con estrategia declarada.
>   `_plan_task_applicable_ids(_plan_task_ficha(...))` no queda vacío para ninguna de las tres.

# Plan — 006-001-opencode-concurrency-reliability

## 1. Ficha de la feature

- **Feature ID:** `006-001-opencode-concurrency-reliability` · **Epic:** `epic-006-opencode-concurrency` ·
  **Estado:** DRAFT (etapa 2).
- **Resultado buscado:** selección de ejecución explícita y verificable, espera proporcional y recuperación
  que conserva la correlación (spec §1), con PD-1..PD-12. AC-7 queda en la recepción.
- **Instalación estable del ciclo:** la registrada en `execution.md`. La candidata se construye y valida en
  una raíz aislada; no se despliega.

## 2. Unidades → tareas

| Unidad del epic §5 | Tarea | PD | Por qué así |
|---|---|---|---|
| T1 | **T1** | PD-1, PD-2, PD-3, PD-4, PD-5 | Selección, preflight, procedencia y secretos: todo lo que ocurre antes de `run` y el registro de cada intento. Va primero porque T2 clasifica sobre su registro. |
| T2 | **T2** | PD-7, PD-8, PD-9, PD-10, PD-11 | Espera, clasificación y recuperación. Comparte archivo con T1 (`cdad_delegate_opencode.py`): **serializada** (`depends_on: [T1]`). |
| T3 | **T3** | PD-6, PD-12 | Integración concurrente (fixture y real), referencia, config de ejemplo y candidato. Cierra el código: suite completa una vez y review independiente. |

`parallel: []` en todas, porque las tres tocan el adaptador o dependen de él.

## 3. Estrategia de validación (declarada una vez)

- **Siempre:** procedencia, `git diff` contra el alcance, focales de la tarea (segundos, con los valores
  chicos de spec §2.1) y regresiones del adaptador.
- **RED:** el focal falla por aserción, no por import ni sintaxis. Se comprueba en un **worktree**, nunca
  con `git stash`.
- **GREEN:** focal verde más regresiones.
- **Suite completa una sola vez,** al cierre de código (T3), la corre quien cierra. Solo se repite si un
  cambio o una evidencia invalidada lo justifican.
- **Review formal e independiente al final** (familia distinta a la del implementer). Después, una
  re-review solo de bloqueantes; las variantes sin impacto material van a deuda.
- **El sentido de `cli-delegation.md` lo juzga la review.** No hay tests de listas de palabras.
- **Oráculos que cambian** (los autoriza el orquestador al aprobar). El test-writer los ajusta en el RED
  de su tarea; el implementer no edita tests:
  1. **T1.** `tests/test_005_010_t2_load_mode_invocation.py:361-385`
     (`test_pd4_server_config_uses_server_without_standalone`) pasa a servir `/api/info` desde un fixture
     en loopback con la versión del fake, en vez de `fixture.invalid` (`:94`).
     - **Por qué:** spec D-1 (preflight en el modo servidor efectivo).
     - **Se conserva:** la aserción de argv (`--server <url>` sin `--standalone`).
  2. **T1, fixture compartido.** El fake de `tests/test_005_009_t2_opencode_adapter.py` responde
     `--version` **antes** de escribir el store o registrar la llamada (hoy lo hace después, `:879-880`).
     - **Por qué:** así un `--version` del preflight no crea una fila ni cuenta como llamada.
     - **Se conserva:** el resto del fake.
  3. **Fakes de T2 y T3 (sin cambio de oráculo).** Las variantes nuevas de T2 (nieto en `hangs`,
     `slow-then-idle`, store bloqueado, etc.) y las escrituras SQLite transaccionales de T3 (el fake
     compartido usa `os.replace`, `:678`, `:768`) viven en un fake **propio de cada focal**. El fake
     compartido solo cambia en T1 (oráculo 2), así que los `files` de T2 y T3 no tocan
     `test_005_009_t2_opencode_adapter.py`.
- **Oráculos que deben seguir verdes sin cambio:**
  - `OUTPUT_KEYS` (`tests/test_005_009_t1_interface.py:100`);
  - las asignaciones de llamada única (`:287`, `:1139`, `:1400`; spec D-2);
  - `"no-idle": "timeout"` (`:399`): con la cota de 2 s vence antes que el asentamiento de 30 s;
  - `TEST_WAIT_TIMEOUT_SECONDS = 2` (`:417`; spec D-3);
  - `transport-error` inmediato (spec D-4).
- **Sin `--no-verify`, sin push, sin desplegar, sin tocar HOME,** sin leer `tests/.sensitive-patterns.local`.

## 4. Fichas mínimas de tarea y bloque canónico

### T1 — Selección de modo, preflight del servidor, procedencia por intento y secretos
- **Resultado observable / PD cubiertas:** PD-1, PD-2, PD-3, PD-4, PD-5; INV-2, INV-4, INV-6, INV-9; D-1, D-2, D-5.
- **Alcance incluido:**
  - en `cdad_delegate_opencode.py`: leer y validar `mode` y las claves `wait.*` nuevas (spec §2.1-§2.2);
  - el preflight de §2.3, con el orden de contraseñas del cliente;
  - la procedencia de §2.6 y el registro del worker en toda terminación (pre y post despacho);
  - la redacción de URL y contraseña en los diagnósticos.
- **Excluido:**
  - la espera, el `Popen` y la comprobación del intento previo (T2);
  - tocar `cdad_delegate.py` o el esquema I8.
- **Consume:** — . **Produce:** `execution-selection` (`execution-selection-v1`).
- **Dependencias:** — .
- **Archivos:**
  - *Modify* `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`,
    `tests/test_005_010_t2_load_mode_invocation.py` (oráculo 1) y
    `tests/test_005_009_t2_opencode_adapter.py` (fake, oráculo 2);
  - *Test* `tests/test_006_001_t1_selection.py`.
- **Contexto por rol:**
  - **RED:** spec §2.1-§2.3, §2.6 y §3 (PD-1..PD-5);
    `cdad_delegate_opencode.py:251-304,494-560,754-834`; `cdad_packet.py:2371-2445`;
    `test_005_010_t2_load_mode_invocation.py:94,361-385`; `test_005_009_t2_opencode_adapter.py:879-880,1075-1095`.
  - **GREEN:** ídem.
- **Evidencia al re-entry:**
  - focal rojo→verde con la matriz de modos, las filas del preflight (fixture HTTP con Basic auth y
    `version` configurable), los registros de worker por camino y el barrido de la contraseña centinela;
  - oráculos 1 y 2 ajustados y verdes;
  - `git diff` acotado;
  - `cdad_delegate.py` sin cambios.
- **Verificación RED→GREEN:**
  - focal: `python3 -m pytest tests/test_006_001_t1_selection.py -q -p no:cacheprovider`;
  - regresiones: `python3 -m pytest tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py tests/test_005_010_reviewfix.py tests/test_005_010_b1_last_assistant.py -q -p no:cacheprovider`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:**
  - si el preflight exigiera cambiar la interfaz o el esquema I8, **detener** (INV-4);
  - si un oráculo distinto de los dos declarados cambia, **detener** y reportarlo antes de tocarlo.

### T2 — Espera proporcional, clasificación, correlación, terminación ordenada e intento previo
- **Resultado observable / PD cubiertas:** PD-7, PD-8, PD-9, PD-10, PD-11; INV-1, INV-3; D-3, D-4, D-6.
- **Alcance incluido:**
  - `Popen` con grupo propio y terminación ordenada (SIGTERM, gracia efectiva, SIGKILL);
  - cero lecturas mientras el cliente vive;
  - backoff y validación de esquema una vez por intento;
  - la tabla de clasificación de §2.4, con el `error` durable de `failed`;
  - `session` elegida en toda terminación posterior a `run`;
  - comprobación del intento previo (§2.7);
  - reserva y gracia de §2.5;
  - conteo `store_reads` en la procedencia de T1.
- **Excluido:** reintentos automáticos; abortar sesiones del servidor; cambiar el vocabulario.
- **Consume:** `execution-selection` (`execution-selection-v1`) de T1. **Produce:** `wait-recovery`
  (`wait-recovery-v1`).
- **Dependencias:** T1 (mismo archivo).
- **Archivos:**
  - *Modify* `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`;
  - *Test* `tests/test_006_001_t2_wait_recovery.py`.
- **Contexto por rol:**
  - **RED:** spec §2.4, §2.5, §2.7 y §3 (PD-7..PD-11); `cdad_delegate_opencode.py:96-97,287-299,409-488,697-727,836-914`;
    `cdad_delegate.py:131-162,252-283`; `test_005_009_t2_opencode_adapter.py:242-250,399,417`;
    discovery D4 (`:124-145`).
  - **GREEN:** ídem.
- **Evidencia al re-entry:**
  - focal rojo→verde con un fake propio del focal y las variantes nuevas: `failed-with-idle-error`,
    `rc0-no-row`, `exit-row-not-idle` (standalone y servidor), `slow-then-idle`, `hangs` con nieto y pid
    registrado, store bloqueado en rollback journal, y registro previo con fila no idle;
  - `store_reads` contra la cota;
  - PD-11 en sus tres variantes;
  - `git diff` acotado.
- **Verificación RED→GREEN:**
  - focal: `python3 -m pytest tests/test_006_001_t2_wait_recovery.py -q -p no:cacheprovider`;
  - regresiones: `python3 -m pytest tests/test_006_001_t1_selection.py tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py tests/test_005_009_t3_spawn_reconciliation.py tests/test_005_009_t4_acceptance.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py tests/test_005_010_reviewfix.py tests/test_005_010_b1_last_assistant.py -q -p no:cacheprovider`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:**
  - si la terminación ordenada dejara procesos vivos que el adaptador no puede alcanzar, **detener** y
    declararlo como límite (PD-15), sin ampliar el alcance;
  - si un oráculo vigente distinto de los declarados cambia, **detener**.

### T3 — Integración concurrente (fixture y real), referencia, config de ejemplo y candidato
- **Resultado observable / PD cubiertas:** PD-6, PD-12; INV-2, INV-6, INV-7; D-7, D-8.
- **Alcance incluido:**
  - focal de concurrencia con fixture (dos proyectos, mismo store y mismo servidor de fixture);
  - test real con opt-in por entorno (spec §5): servidor descartable, credencial por `{env:<VAR>}`,
    guarda `debug paths`, dos delegaciones concurrentes y el complemento standalone;
  - observaciones VERIFY (c) y (d) de spec §10;
  - `cli-delegation.md` (modos, claves, preflight, clasificación, límites, receta de aislamiento,
    responsable del servidor);
  - `skills/cdad-cycle/assets/opencode-exec-config.example.json`;
  - candidato en raíz aislada;
  - suite completa una vez y review independiente.
- **Excluido:** desplegar en HOME; tocar el runtime o la base viva; AC-7.
- **Consume:** `execution-selection` (`execution-selection-v1`) de T1 y `wait-recovery`
  (`wait-recovery-v1`) de T2. **Produce:** `concurrency-acceptance` (`concurrency-acceptance-v1`).
- **Dependencias:** T1, T2.
- **Archivos:**
  - *Create/Modify* `skills/cdad-cycle/references/cli-delegation.md` y
    `skills/cdad-cycle/assets/opencode-exec-config.example.json`;
  - *Test* `tests/test_006_001_t3_concurrency.py` (focal, con fake propio) y
    `tests/test_006_001_t3_integration.py` (recorrido real, en `observable_checks`: sin credencial se
    omite, así que no puede mostrar un RED por aserción).
- **Contexto por rol:**
  - **RED:** spec §3 (PD-6, PD-12), §5; `test_005_010_t4_integration.py:169-342` (helpers de proyecto
    real, que se reutilizan); `test_005_009_t2_opencode_adapter.py:441-880` (fake); discovery §4
    (`:243-316`).
  - **GREEN:** ídem más `cli-delegation.md:112-183`.
- **Evidencia al re-entry:**
  - focal de concurrencia rojo→verde;
  - informe del recorrido real en modo servidor, con dos `completed`, nonces separados y versión, config
    anonimizada, carga, tiempos y `store_reads`; más el complemento standalone y las observaciones (c)/(d);
  - `make validate` sin fallos nuevos;
  - candidato aislado `--check` OK;
  - suite completa;
  - review independiente;
  - barrido de saneamiento sin hallazgos en los archivos tocados.
- **Verificación:**
  - **focal:** `python3 -m pytest tests/test_006_001_t3_concurrency.py -q -p no:cacheprovider`;
  - **real:** la corre el orquestador con la credencial del operador:
    `CDAD_OPENCODE_INTEGRATION=1 CDAD_OPENCODE_BINARY=<bin> CDAD_OPENCODE_MODEL=<m> CDAD_OPENCODE_KEY_ENV=<VAR> python3 -m pytest tests/test_006_001_t3_integration.py -q -p no:cacheprovider`;
    sin `<VAR>` definida se omite, y la omisión deja PD-6 en BLOQUEO;
  - **referencias:** `python3 -m pytest tests/test_005_010_t3_references.py -q -p no:cacheprovider` y `make validate`;
  - **candidato:** `make staging`, `HOME=<tmp> bash install.sh --force`, `HOME=<tmp> bash install.sh --check`;
  - **cierre de código, una vez:** `python3 -m pytest tests -q -p no:cacheprovider`;
  - **saneamiento (orquestador):** `python3 .cdad/local/sanitize.py .`, sin `--apply`.
- **Integración / responsable:**
  - **Gate de cierre de código de la feature:**
    - PD-6 aceptada solo con la evidencia del recorrido **real** en modo servidor; el fixture no basta
      y una omisión no es un pase;
    - suite completa una vez;
    - review independiente con re-review de bloqueantes.
  - **Responsables:** RED test-writer; GREEN implementer; recorrido real y suite, el orquestador; review,
    el reviewer.
- **Incertidumbres / detención:**
  - si la guarda `debug paths` no confina `db/data/state/log` bajo `<ROOT>`, **detener** sin despachar;
  - si la credencial por `{env:<VAR>}` falla (spec §5.3, VERIFY b), **detener** y volver al orquestador
    con la alternativa (B);
  - si el recorrido real exige reiniciar o recargar un servidor compartido, **detener**: está reservado
    al dueño.

### Bloque canónico `plan-tasks`

```plan-tasks
{
 "validation_strategy": "Verificacion en dos niveles: siempre procedencia + git diff contra el alcance + focales de la tarea (segundos, con valores de espera chicos en los fixtures) + regresiones del adaptador; RED falla por asercion y se comprueba en worktree, nunca git stash. La suite completa se corre una sola vez al cierre de codigo (T3), por quien cierra, y solo se repite si cambios o evidencia invalidada lo justifican; se reutiliza evidencia equivalente con procedencia verificada (skills/cdad-cycle/references/re-entry.md, Equivalence of a registered run). Review formal independiente al final con re-review de bloqueantes. El sentido de los textos lo juzga la review. Oraculos que cambian, declarados en el plan seccion 3: el de modo servidor de test_005_010_t2_load_mode_invocation.py y el --version del fake compartido.",
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
   "id": "T2",
   "objective": "Espera proporcional (cero lecturas con el cliente vivo, backoff acotado despues), clasificacion tras la salida del cliente con el error durable de failed, sesion elegida en toda terminacion posterior a run, terminacion ordenada del grupo propio con gracia efectiva, comprobacion del intento previo del mismo paquete y respuesta siempre dentro de la cota.",
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
    "T1"
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
   "objective": "Concurrencia util verificada con fixture permanente y con recorrido REAL en modo servidor contra un servidor descartable en loopback con contrasena aleatoria y store aislado (credencial por sustitucion {env:VAR}, sin copiar auth.json), complemento standalone, observaciones VERIFY, referencia canonica y config de ejemplo portables, candidato en raiz aislada, suite completa una vez y review independiente.",
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
     "artifact": "wait-recovery",
     "contract": "wait-recovery-v1",
     "producer": "T2"
    }
   ],
   "depends_on": [
    "T1",
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
    "recorrido REAL en modo servidor con tests/test_006_001_t3_integration.py (opt-in por entorno, lo corre el orquestador con la credencial del operador): servidor descartable en loopback con contrasena aleatoria, store aislado bajo ROOT confirmado por la guarda debug paths, credencial por {env:VAR} sin copiar auth.json, dos delegaciones concurrentes de dos proyectos descartables que terminan completed con nonces separados y sesion propia; complemento standalone; observaciones VERIFY (a)-(d) registradas; una omision por falta de credencial no es un pase"
   ],
   "regressions": [
    "tests/test_005_010_t3_references.py",
    "tests/test_006_001_t1_selection.py",
    "tests/test_006_001_t2_wait_recovery.py",
    "tests/test_005_009_t4_acceptance.py"
   ],
   "integration_gate": "gate de cierre de codigo de 006-001: PD-6 aceptada solo con evidencia del recorrido REAL en modo servidor (el fixture no basta; una omision por falta de credencial no es un pase y deja BLOQUEO declarado), make validate sin fallos nuevos, candidato aislado con install.sh --check OK, suite completa una vez por quien cierra y review independiente con re-review de bloqueantes; AC-7 queda para la recepcion",
   "owner": "RED: test-writer; GREEN: implementer; recorrido real y suite: orquestador; review: reviewer independiente"
  }
 ]
}
```

## 5. Trazabilidad PD/AC → tarea

| Tarea | PD | AC |
|---|---|---|
| T1 | PD-1, PD-2, PD-3, PD-4, PD-5 | AC-1, AC-2, AC-6 |
| T2 | PD-7, PD-8, PD-9, PD-10, PD-11 | AC-4, AC-5 |
| T3 | PD-6, PD-12 | AC-3, AC-8 |

AC-7 corresponde a la recepción.

## 6. Gate de la feature

- **La feature cierra el código cuando:**
  - PD-1..PD-5 y PD-7..PD-12 tienen focal rojo→verde con `git diff` acotado;
  - PD-6 tiene el fixture y el **recorrido real en modo servidor**;
  - la suite completa corrió una vez;
  - la review independiente no deja bloqueantes.
- **Sin la credencial del operador,** PD-6 queda en **BLOQUEO declarado**, con dueño y siguiente acción,
  nunca verde por proximidad.
- **Después:** candidato, review, evidencia y receta de despliegue y rollback (epic §7). AC-7 sigue pendiente
  hasta el despliegue autorizado.

## 7. Restricciones globales

- Sin push, sin `--no-verify`, sin desplegar y sin tocar HOME, la base viva ni el consumidor.
- No reiniciar, recargar ni terminar servidores compartidos. Solo se para el servidor descartable del test.
- Sin valores del host en la spec, el plan ni el producto. Los ids, rutas y tiempos crudos quedan en
  `.cdad/local/`.
- Nunca `git stash` en el árbol compartido: RED en worktree.
- Ante un obstáculo fuera de alcance: diagnóstico al orquestador, sin rodeos ni registros fabricados.

## 8. Estado

DRAFT pendiente de la decisión del orquestador bajo la HITL delegada del epic-006 (junto con la spec). Sin
marca de aprobación.
## 9. Decisión del orquestador (2026-10-16)

Aprobado junto con la spec (spec §14), bajo la HITL delegada de epic-006.

Status: Approved by Claude orchestrator (HITL delegated by Pablo for epic-006) on 2026-10-16
