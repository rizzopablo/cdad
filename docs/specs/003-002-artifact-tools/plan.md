---
feature_id: 003-002-artifact-tools
feature_name: Recepcion original y materializacion explicita
created_at: 2026-09-17
replanned_at: 2026-10-05
status: approved
approved_by: Pablo (HITL delegada al orquestador OpenCode)
approved_at: 2026-10-05
---

# Plan — 003-002 Artifact tools (replanificado al contrato de planificacion 004-003)

> **Estado:** borrador, **no aprobado**. El architect no aprueba su propia propuesta
> (ADR-003). Replanificacion PD-13 de `004-003-planning-procedures`: se adapta el
> `plan-draft.md` (sesion 2026-09-18) al contrato de planificacion vigente
> (`planning-contract-draft.md` §4 y §4.1) conservando el trabajo valido; **no se
> reimplementa 003-002**. Cada tarea es la unidad minima con su propio RED,
> rechazable de forma independiente.
>
> Materializado por el orquestador desde el TEXTO FINAL del architect (ADR-003),
> sesion `<ses-26>`, paquete
> `004-003-planning-procedures-architect-draft-001`.

## Restricciones globales

- Depender solo de validadores publicos estables de 001.
- Python 3 stdlib; implementacion instalable junto al helper de 001.
- Store operacional `.cdad/runtime`, gitignored.
- UTF-8 no vacio, maximo agregado 1 MiB por packet.
- Una finalizacion por execution/packet.
- Receipt mecanico, estado y aprobacion semantica separados.
- Fixtures offline; sin fetch OpenCode/Codex.

## Trazabilidad postcondiciones ↔ tareas

| Postcondicion (spec-draft) | Tarea(s) |
|---|---|
| P1 recepcion exacta e identificada | T1 |
| P2 publicacion atomica e idempotente | T1 |
| P3 receipt mecanico sin aprobacion | T1 (base) + T2 (no aprueba) |
| P4 materializacion exacta y autorizada | T2 |
| P5 evidencia de suite vigente y no vacia | T3 |
| P6 scopes y limites de prueba explicitos | T1 (base) + T2 (parte) + T4 (integracion) |

## Propiedad del estado (resuelto 2026-10-05)

`docs/.cdad-state.json` tiene **un solo escritor: el orquestador**. Ninguna
herramienta de 003-002 lo toca.

| Productor | Escribe | NO escribe |
|---|---|---|
| `receive` (T1) | el store operacional `.cdad/runtime/…` (gitignored) + el receipt | el state, el contexto de ejecucion, el arbol de trabajo |
| `materialize` (T2) | los artefactos destino permitidos por la politica de artefactos (create-only/CAS) + su journal | el state; `approval_effect` es siempre `false` |
| `run-evidence` (T3) | su registro de evidencia + snapshots | el state |
| **orquestador** | `docs/.cdad-state.json`, `stage_history`, el binding del paquete y la materializacion de los artefactos de solo-lectura (ADR-003) | el contenido de los artefactos de rol |

Regla de la ficha §4 (`planning-contract-draft.md`): la referencia de receipt/estado
en el state la agrega **el orquestador**, no las herramientas; `receive` y
`materialize` no lo modifican.

## Incertidumbres del plan resueltas (2026-10-05)

Las cuatro marcas VERIFY del replan, resueltas con evidencia antes de construir:

| Tarea | VERIFY | Resolucion (evidencia) |
|---|---|---|
| T1 | ruta exacta del state schema | `skills/cdad-cycle/assets/state-template.json` existe (schema_version 1, 454 bytes) y es la plantilla del state; el validador vive en `skills/cdad-cycle/scripts/cdad_packet.py` (`validate-state`). El wrapper `scripts/cdad_packet.py` no se edita. |
| T2 | lista cerrada `artifact_kind -> target` | Se adopta la tabla de la spec §7 con una precision: la tabla fija la **raiz permitida** por kind y el **target exacto se declara en la autorizacion** (asi se materializo en 004-003: `review-t1.md`, `review-t2.md` y `review-second-look.md` no caben en un unico `review.md`). Sin motor de reglas general. |
| T3 | el runner no requiere red | El runner ejecuta `python3 -m unittest` sobre los tests del proyecto; la suite del repo corre sin red (evidencia: corridas de 004-001/002/003 con `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest`). Fixtures offline. |
| T4 | punto de insercion en el state schema | **No requiere cambio de esquema**: la referencia usa la forma ya existente de `stage_history`. Se retira `state-template.json` de los archivos de T4. |

## Tareas

### T1 — Receive atomico e idempotente

- **ID / version:** T1 · plan v1 (replan 2026-10-05).
- **Resultado observable / postcondiciones:** P1, P2 y base de P3/P6. `receive`
  persiste bytes identicos, liga execution/packet/feature/role/substage y emite un
  receipt mecanico; un retry identico converge; contenido conflictivo no sobrescribe.
- **Alcance incluido / excluido:** helper + CLI `receive`/`validate-receipt`, schemas,
  store. Excluido: materializacion (T2), runner (T3), integracion (T4). **F5
  (resuelto 2026-10-05):** `.gitignore` **no** se modifica — el store vive bajo
  `.cdad/`, ya ignorado en este repo (`.gitignore:11`, confirmado con
  `git check-ignore`); una regla nueva seria cosmetica y no cambia comportamiento.
- **Consume:** execution context y packet validados por 001; `RESULT.json`; staged
  UTF-8 parts bajo `.cdad/inbox`; manifest observado opcional. (Dependencias externas
  al plan: no tienen productor interno.)
- **Produce:** `cdad-result-helper` (contrato `cli-v1`) y `cdad-receipt`
  (contrato `receipt-v1`); consumidores T2/T3/T4.
- **Dependencias previas / condicion de arranque:** contratos aprobados de 001; no
  depende de T2–T4.
- **Archivos:** Create `skills/cdad-cycle/scripts/cdad_result.py`; Create wrapper
  `scripts/cdad_result.py`; Create schemas
  `skills/cdad-cycle/assets/result-descriptor.schema.json`,
  `.../result-bundle.schema.json`, `.../result-receipt.schema.json`; Test
  `tests/test_003_002_t1_receive.py`.
- **Entradas de contexto por rol y motivo:** test-writer: spec-draft P1/P2/P3/P6 +
  contratos de 001; implementer: los mismos + el test RED. Motivo: fijar identidad,
  atomicidad y receipt sin exponer implementacion al test-writer.
- **Decisiones autonomas / capacidades / restricciones:** implementer decide la
  estructura interna del store (temp + fsync + rename, journal) y el formato de
  digests; test-writer decide la bateria RED dentro de P1/P2/P3/P6. Capacidades:
  ejecutar `python3`, escribir en el scope declarado. Restriccion: el implementer no
  edita tests; `receive` no modifica state.
- **Evidencia al re-entry:** receipt durable + digests; una interrupcion se
  diagnostica por presencia/validez del directorio final (antes/despues de publicar).
- **Estimacion inicial:** media (aprox. 1–2 sesiones de implementer). Metodo:
  estimacion cualitativa del architect; incertidumbre media (concurrencia y kill).
- **Verificacion RED→GREEN / integracion / responsable:** RED
  `tests/test_003_002_t1_receive.py` (bytes/digests, 1 MiB, UTF-8, identidad, status
  dispatched, scope; retry/interrupcion/dos procesos). GREEN: write/fsync/rename
  minimo + receipt inmutable. Gate de integracion: `@validation_strategy`.
  Responsable: RED test-writer; GREEN implementer.
- **Incertidumbres / detener / replanificar:** VERIFY la ruta exacta del state schema
  (¿`assets/state-template.json` + validador en `cdad_packet.py`?). Detener si 001 no
  expone validacion de packet/execution reutilizable; replanificar si el store debe
  quedar fuera de project root.

### T2 — Materializacion por politica de artefactos

- **ID / version:** T2 · plan v1 (replan 2026-10-05).
- **Resultado observable / postcondiciones:** P3, P4 y parte de P6. `materialize`
  copia bytes originales a un target permitido por artifact policy; create-only/CAS;
  journal durable; sin efecto de aprobacion.
- **Alcance incluido / excluido:** tabla cerrada `artifact_kind -> target`, schema de
  autorizacion, journal. Excluido: receive (T1), runner (T3).
- **Consume:** `cdad-receipt` (`receipt-v1`) de T1; `MATERIALIZE.json`; authority
  binding vigente; artifact policy. (Authority binding es externo.)
- **Produce:** `cdad-materialize` (contrato `cli-v1`); consumidor T4.
- **Dependencias previas / condicion de arranque:** T1 verde. **Archivo compartido
  (resuelto 2026-10-05):** T2 y T3 extienden el mismo modulo
  `skills/cdad-cycle/scripts/cdad_result.py`. Division explicita de
  responsabilidades: T2 posee el comando `materialize` y sus dos esquemas
  (`materialize.schema.json`, `artifact-policy.json`); T3 posee el comando de
  evidencia de corrida y sus dos esquemas (`run-request.schema.json`,
  `run-evidence.schema.json`); ninguno reordena ni reescribe las secciones del
  otro. **Serializacion:** T3 declara `depends_on: [T1, T2]` — no se despachan en
  paralelo sobre el mismo archivo.
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_result.py`; Create
  `skills/cdad-cycle/assets/materialize.schema.json`; Create
  `skills/cdad-cycle/assets/artifact-policy.json`; Test
  `tests/test_003_002_t2_materialize.py`.
- **Entradas de contexto por rol y motivo:** spec-draft P3/P4/P6 + artifact policy
  propuesta; el test-writer no ve implementacion.
- **Decisiones autonomas / capacidades / restricciones:** implementer decide el
  journal y la semantica CAS. Capacidades: `python3`, escritura en scope. Restriccion:
  no cambia `semantic_status` ni state; `approval_effect` siempre `false`.
- **Evidencia al re-entry:** journal + SHA-256 final por copy; retry multi-copy
  continua desde journal sin prometer atomicidad global.
- **Estimacion inicial:** media. Metodo: cualitativa; incertidumbre media (CAS/journal).
- **Verificacion RED→GREEN / integracion / responsable:** RED target
  permitido/prohibido, receipt/authority mismatch, traversal, target igual/divergente.
  GREEN: temp + rename exacto, sin approval effect ni state mutation; verificar que
  read-only target policy no amplia source write scope. Gate `@validation_strategy`.
  Responsable: RED test-writer; GREEN implementer.
- **Incertidumbres / detener / replanificar:** VERIFY la lista cerrada
  `artifact_kind -> target` (spec-draft §7 la propone; confirmar contra los roles
  reales). Detener si la policy no puede expresarse sin un motor de reglas general.

### T3 — Evidencia Python unittest

- **ID / version:** T3 · plan v1 (replan 2026-10-05).
- **Resultado observable / postcondiciones:** P5. El runner captura argv/log/exit/
  conteos y snapshots before/after; `validate-run-evidence` devuelve
  `valid-current | invalid | stale | unknown`.
- **Alcance incluido / excluido:** solo `python3 -m unittest`; snapshots propios.
  Excluido: otros runners, cache generica.
- **Consume:** `cdad-result-helper` (`cli-v1`) de T1 (identidad/helper); `RUN.json`;
  argv; snapshots source/test/contract. (`RUN.json` es externo.)
- **Produce:** `cdad-run-evidence` (contrato `evidence-v1`); consumidor T4.
- **Dependencias previas / condicion de arranque:** T1 (identidad y helper) **y T2**
  (serializacion del archivo compartido `skills/cdad-cycle/scripts/cdad_result.py`;
  ver la division de responsabilidades declarada en T2).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_result.py`; Create
  `skills/cdad-cycle/assets/run-request.schema.json`, `.../run-evidence.schema.json`;
  Test `tests/test_003_002_t3_run_evidence.py`.
- **Entradas de contexto por rol y motivo:** spec-draft P5 + contrato del runner.
- **Decisiones autonomas / capacidades / restricciones:** implementer decide la
  serializacion canonica de snapshots. Capacidades: ejecutar subprocess
  `python3 -m unittest` sin shell. Restriccion: no acepta digests del caller.
- **Evidencia al re-entry:** evidence + snapshots before/after; mutacion de source o
  tests invalida la evidencia.
- **Estimacion inicial:** media. Metodo: cualitativa; incertidumbre media (equivalencia
  de snapshots).
- **Verificacion RED→GREEN / integracion / responsable:** RED argv no permitido,
  exit != 0, cero tests, snapshot cambiado, digest desconocido. GREEN: ejecucion sin
  shell, conteo > 0, captura exacta y comparacion de equivalencia. Gate
  `@validation_strategy`. Responsable: RED test-writer; GREEN implementer.
- **Incertidumbres / detener / replanificar:** VERIFY que el runner no requiere red
  (fixtures offline). Detener si `python3 -m unittest` no puede aislarse sin shell.

### T4 — Integracion con re-entry e instalacion

- **ID / version:** T4 · plan v1 (replan 2026-10-05).
- **Resultado observable / postcondiciones:** integracion P1–P6. Flujo
  recibir → reconciliar root → materializar; una transicion de state; smoke instalado.
- **Alcance incluido / excluido:** `re-entry.md`, instrucciones de salida/
  materializacion, instalacion/README, referencia minima en state. Excluido:
  reimplementar 003-002 o cambiar gates ajenos.
- **Consume:** `cdad-receipt` (T1), `cdad-materialize` (T2), `cdad-run-evidence` (T3).
  (Decision/autoridad del orquestador es externa.)
- **Produce:** `cdad-reentry-flow` (contrato `flow-v1`).
- **Dependencias previas / condicion de arranque:** T1–T3 verdes.
- **Archivos:** Modify `skills/cdad-cycle/references/re-entry.md`; Modify `install.sh`,
  `README.md`; Modify el validador `skills/cdad-cycle/scripts/cdad_packet.py` (canónico;
  el wrapper `scripts/cdad_packet.py` no requiere edición) **solo si** la referencia de
  receipt exige una regla de validación; **no** se modifica
  `skills/cdad-cycle/assets/state-template.json` (resuelto: la referencia usa la forma
  existente de `stage_history`). Test `tests/test_003_002_t4_integration.py`.
- **Entradas de contexto por rol y motivo:** spec-draft §4/§6 + `re-entry.md`; el
  test-writer no ve implementacion.
- **Decisiones autonomas / capacidades / restricciones:** implementer decide la forma
  de la referencia de receipt/status en state. Capacidades: escribir en scope, correr
  el smoke instalado. Restriccion: state lo cambia el orquestador; receive/materialize
  no lo tocan.
- **Evidencia al re-entry:** recorrido offline receive → reconcile → materialize sin
  doble efecto + smoke instalado desde raiz aislada.
- **Estimacion inicial:** media. Metodo: cualitativa; incertidumbre media-alta
  (integracion + smoke instalado).
- **Verificacion RED→GREEN / integracion / responsable:** RED retry con state ya
  reconciliado no repite efecto. GREEN: el **orquestador** agrega una referencia
  pequena al receipt/status en `stage_history` (forma existente; `receive` y
  `materialize` no escriben el state — F4 resuelto 2026-10-05) y el re-entry parte
  del original durable; suite P1–P6 + smoke instalado. Regresiones (propuestas a
  confirmar): `tests/validate-consistency.sh`, `tests/test_packet_prepare.py`. Gate
  `@validation_strategy`. Responsable: RED test-writer; GREEN implementer; integracion
  orquestador.
- **Incertidumbres / detener / replanificar:** VERIFY el punto exacto de insercion en
  el state schema; el smoke requiere raiz aislada (regla del proyecto: nunca instalar
  CDAD en HOME real). Detener si el smoke no puede correr aislado.

#### Desviaciones registradas de T4 (2026-10-05)

- **`README.md` — diferido con razon (F1.2 de `review-t4.md`).** El plan listaba
  `README.md` en el alcance de T4. **Ningun rol puede escribirlo** bajo
  `docs/cdad-policy.json`: la politica clasifica `install.sh` como unico
  `implementation_file`; `README.md` (raiz del repo, fuera de `documentation_roots`)
  queda **sin clasificar**. Revisar la politica esta **fuera de alcance** de 003-002
  (spec §Fuera de alcance) y cambiarla a mitad de ciclo altera `policy_sha256` e
  invalida el contexto de ejecucion y la evidencia vigente (desproporcionado). Ampliar
  el scope de un paquete por encima de la politica crearia un scope mayor que la
  politica — peor que una linea desactualizada. **Disposicion:** se documenta la
  desviacion (deja de ser silenciosa) y se registra la **brecha de la politica**
  (clasificar `README.md`) como decision del dueno. El flujo queda documentado en su
  dueno canonico (`re-entry.md`, dentro de `skills/`, si escribible).
- **`install.sh` y `skills/cdad-cycle/scripts/cdad_packet.py` — sin cambio, fundado.**
  El arbol instalado ya lleva el entrypoint y los assets (probado por el smoke de T4);
  la referencia de estado usa la forma existente de `stage_history` y
  `_approved_stage_entry` no rechaza claves extra, asi que no hay regla de validacion
  nueva. Declarado con evidencia en el reporte del GREEN y verificado por el reviewer.

## Bloque canonico `plan-tasks`

El plan de validacion por unidad (PD-8) se declara aqui, en la unica forma legible
por maquina, segun `planning-contract-draft.md` §4.1; cada tarea lo resume en su campo
Verificacion. La estrategia comun se declara una vez y se referencia con
`@validation_strategy`.

```plan-tasks
{
  "tasks": [
    {
      "consume": [],
      "depends_on": [],
      "files": [
        "scripts/cdad_result.py",
        "skills/cdad-cycle/assets/result-bundle.schema.json",
        "skills/cdad-cycle/assets/result-descriptor.schema.json",
        "skills/cdad-cycle/assets/result-receipt.schema.json",
        "skills/cdad-cycle/scripts/cdad_result.py"
      ],
      "focal_tests": [
        "tests/test_003_002_t1_receive.py"
      ],
      "id": "T1",
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "parallel": [],
      "produce": [
        {
          "artifact": "cdad-result-helper",
          "contract": "cli-v1"
        },
        {
          "artifact": "cdad-receipt",
          "contract": "receipt-v1"
        }
      ],
      "regressions": []
    },
    {
      "consume": [
        {
          "artifact": "cdad-receipt",
          "contract": "receipt-v1",
          "producer": "T1"
        }
      ],
      "depends_on": [
        "T1"
      ],
      "files": [
        "skills/cdad-cycle/assets/artifact-policy.json",
        "skills/cdad-cycle/assets/materialize.schema.json",
        "skills/cdad-cycle/scripts/cdad_result.py"
      ],
      "focal_tests": [
        "tests/test_003_002_t2_materialize.py"
      ],
      "id": "T2",
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "parallel": [],
      "produce": [
        {
          "artifact": "cdad-materialize",
          "contract": "cli-v1"
        }
      ],
      "regressions": []
    },
    {
      "consume": [
        {
          "artifact": "cdad-result-helper",
          "contract": "cli-v1",
          "producer": "T1"
        }
      ],
      "depends_on": [
        "T1",
        "T2"
      ],
      "files": [
        "skills/cdad-cycle/assets/run-evidence.schema.json",
        "skills/cdad-cycle/assets/run-request.schema.json",
        "skills/cdad-cycle/scripts/cdad_result.py"
      ],
      "focal_tests": [
        "tests/test_003_002_t3_run_evidence.py"
      ],
      "id": "T3",
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "parallel": [],
      "produce": [
        {
          "artifact": "cdad-run-evidence",
          "contract": "evidence-v1"
        }
      ],
      "regressions": []
    },
    {
      "consume": [
        {
          "artifact": "cdad-receipt",
          "contract": "receipt-v1",
          "producer": "T1"
        },
        {
          "artifact": "cdad-materialize",
          "contract": "cli-v1",
          "producer": "T2"
        },
        {
          "artifact": "cdad-run-evidence",
          "contract": "evidence-v1",
          "producer": "T3"
        }
      ],
      "depends_on": [
        "T1",
        "T2",
        "T3"
      ],
      "files": [
        "README.md",
        "install.sh",
        "skills/cdad-cycle/references/re-entry.md",
        "skills/cdad-cycle/scripts/cdad_packet.py"
      ],
      "focal_tests": [
        "tests/test_003_002_t4_integration.py"
      ],
      "id": "T4",
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer; integracion: orquestador",
      "parallel": [],
      "produce": [
        {
          "artifact": "cdad-reentry-flow",
          "contract": "flow-v1"
        }
      ],
      "regressions": [
        "tests/test_install_ownership.py",
        "tests/test_install_review5_regressions.py",
        "tests/test_packet_prepare.py",
        "tests/validate-consistency.sh"
      ]
    }
  ],
  "validation_strategy": "suite completa una vez por GREEN sobre el area tocada; cierre con suite completa y validadores del repo"
}
```

## Integracion final

1. Ejecutar fixtures offline de recepcion simple y architect bundle.
2. Ejecutar matriz interruption/concurrency/conflict.
3. Ejecutar artifact policy completa y verificar bytes/digests.
4. Ejecutar unittest green, red, empty, stale y unknown.
5. Ejecutar recorrido receive/retry/reconcile/materialize sin doble efecto.
6. Ejecutar suites estables de 001 y checks del repo aplicables.
7. Confirmar store gitignored y ausencia de cambios en instalacion real.
8. Exigir cero skips/bloqueados para el gate de 002.

## Auto-revision

- T1 → P1/P2/P3/P6. T2 → P3/P4/P6. T3 → P5. T4 → integracion P1–P6.
- No hay tarea sin postcondicion ni postcondicion sin tarea.
- PD-8: toda tarea declara pruebas focales, regresiones, gate de integracion y
  responsable en el bloque `plan-tasks`; no hay tarea sin plan de validacion.
- No se incluye fetch SDK, workflow engine, cache general ni continuidad.

## Adaptacion respecto del draft 2026-09-18

- Se conservan las 4 tareas, su mapeo a P1–P6, los pasos TDD y la integracion final.
- Se agrega el bloque canonico `plan-tasks` (§4.1) con el plan de validacion por
  unidad de PD-8: pruebas focales, regresiones, gate de integracion y responsable.
- Se explicitan por tarea los campos de la ficha §4 (consume/produce con productor,
  contexto por rol, decisiones autonomas, evidencia al re-entry, estimacion,
  incertidumbres) que el draft dejaba implicitos.
- Los inputs externos de 001 (execution context, packet validado, autoridad) se
  describen en prosa y no como entradas `consume` del bloque, porque no tienen
  productor dentro de este plan.

---

Status: Pending approval (borrador; el architect no aprueba su propia propuesta)
