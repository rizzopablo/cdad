---
feature_id: 003-002-artifact-tools
feature_name: Recepción original y materialización explícita
created_at: 2026-09-17
reconciled_at: 2026-10-05
status: approved
approved_by: Pablo (HITL delegada al orquestador OpenCode)
approved_at: 2026-10-05
---

# Spec: Recepción original y materialización explícita

> Borrador reconciliado con el runtime de paquetes **v2** (004-002) y el contrato
> de planificación vigente (ADR-013 / `planning-contract-draft.md`). Materializado
> por el orquestador desde el TEXTO FINAL del architect (ADR-003); aprobado por el
> dueño (HITL delegada) el 2026-10-05. El plan de la feature (`plan.md`, T1–T4) es
> su contrato de división y de validación por unidad; esta spec es su contrato
> funcional.

## Descripción funcional

CDAD recibe el resultado original de un rol identificado por los contratos de 001,
persiste exactamente sus bytes de forma atómica e idempotente y emite un recibo
mecánico breve. Después, una operación separada y autorizada por el orquestador
puede copiar partes del resultado a destinos canónicos permitidos para el rol.

Recepción, materialización y aprobación semántica son hechos distintos. Ningún
recibo aprueba un spec, una review, un audit ni Memory Bank; ningún texto es
resumido o regenerado por estas operaciones. La recepción construye sobre el
runtime de paquetes **v2** vigente (identidad de ejecución, paquete renderizado,
binding de autoridad y observación de dispatch) y no redefine sus esquemas.

## Contrato

### 0. Base y dependencia: runtime de paquetes v2

003-002 no redefine las interfaces de 001; consume su runtime **v2** vigente
(evolucionado por 004-002; el contexto v1 no se adopta hacia atrás):

- **Política del proyecto** `docs/cdad-policy.json` (ADR-012): única política
  editable (`schema_version`, `path_policy`, `temporary_roots`); ningún rol la edita.
- **Contexto de ejecución v2** en `.cdad/executions/<execution-id>/execution.json`
  (`schema_version: 2`): identidad lógica (`id`, `epic_id`, `feature_id`, `scope`,
  `authority_ref`, `model_policy`) más snapshot verificable de la política
  (`policy_sha256`, `policy`, `policy_history`). Runtime, modelo y sesión son
  observaciones de dispatch (I8), **no** parte de la identidad.
- **Paquete renderizado** en `.cdad/packets/<packet-id>/` (`REQUEST.json` +
  `PACKET.md`) y binding en `state.execution` / `state.active_packet`.
- **Validadores públicos reutilizados**: `validate-state`, `validate-request`,
  `validate-packet` (identidad, vigencia, scopes tipados y hash exacto del
  contrato). `validate-state` v2 aplica la vigencia completa: aprobación de
  contrato (I2 — entrada de `stage_history` con `stage: "specification"` y
  `approved_by` no vacío) y delegación HITL activa.
- **Observación de dispatch (I8)**: el orquestador registra el intento con
  `prepare --record-dispatch <packet-id> --attempt-id <id> --input <attempt.json>`
  (documento de claves cerradas: `runtime`, `model_configured`, `model_reported`,
  `session`, `started_at`, `provenance`), lo que fija
  `active_packet.status = "dispatched"`.

Consecuencia operativa declarada: `prepare` —y por tanto todo paquete de 003-002—
exige que la spec esté aprobada y registrada en `stage_history`. La herramienta no
crea, no completa ni modifica esa aprobación.

### 1. Dependencia e instalación

002 consume las interfaces estables aprobadas de 001 (execution context v2, packet
metadata, `validate-state`, `validate-packet`, identidad de `active_packet`,
contrato SHA-256 y scopes tipados). No redefine esos schemas.

La implementación canónica usa Python 3 stdlib y vive junto a 001:

```text
skills/cdad-cycle/scripts/cdad_result.py
```

El repo expone un wrapper fino `scripts/cdad_result.py`. La instalación ofrece un
entrypoint equivalente que resuelve schemas relativos a la skill instalada. No se
introduce un framework de workflow, blob store ni cache general.

El store durable operacional es:

```text
PROJECT_ROOT/.cdad/runtime/
```

Es aditivo dentro de `.cdad/` (no colisiona con `.cdad/executions`,
`.cdad/packets`, `.cdad/.lock` ni `.cdad/.txn`). Debe quedar excluido del control
de versiones; en este repositorio `.cdad/` ya está ignorado, por lo que no se
requiere una regla nueva de `.gitignore`. Los artefactos versionados siguen bajo
sus destinos canónicos; el store no los reemplaza.

### 2. Interfaz pública

```text
python3 scripts/cdad_result.py receive \
  --project-root ROOT \
  --execution-context EXECUTION.json \
  --packet PACKET.md \
  --request REQUEST.json \
  --descriptor RESULT.json

python3 scripts/cdad_result.py validate-receipt \
  --project-root ROOT \
  --receipt RECEIPT.json

python3 scripts/cdad_result.py materialize \
  --project-root ROOT \
  --receipt RECEIPT.json \
  --authorization MATERIALIZE.json

python3 scripts/cdad_result.py run-python-unittest \
  --project-root ROOT \
  --execution-context EXECUTION.json \
  --packet PACKET.md \
  --request REQUEST.json \
  --run-request RUN.json

python3 scripts/cdad_result.py validate-run-evidence \
  --project-root ROOT \
  --execution-context EXECUTION.json \
  --packet PACKET.md \
  --request REQUEST.json \
  --run-request RUN.json \
  --evidence EVIDENCE.json
```

`EXECUTION.json` es el contexto de ejecución v2; `PACKET.md` y `REQUEST.json` son
los del paquete publicado en `.cdad/packets/<packet-id>/`. `--project-root` es
opcional y por defecto es el directorio de trabajo actual. Éxito devuelve `0`.
`receive` escribe en stdout exactamente los bytes del `receipt.json` canónico; un
retry idéntico escribe los mismos bytes. Una violación devuelve código distinto de
`0`, diagnóstico por stderr y ningún recibo, artefacto o evidencia parcial por
stdout. Los paths persistidos son project-relative y normalizados.

### 3. Descriptor de resultado

`RESULT.json` (los identificadores son ilustrativos; se aceptan como segmentos
seguros, no como un formato impuesto):

```json
{
  "schema_version": 1,
  "execution_id": "exec-003-002-artifact-tools-001",
  "packet_id": "003-002-artifact-tools-architect-draft-001",
  "feature_id": "003-002-artifact-tools",
  "source": {
    "kind": "staged-file",
    "sdk_message_ref": null
  },
  "parts": [
    {
      "name": "spec",
      "artifact_kind": "architect-spec-draft",
      "staged_path": ".cdad/inbox/spec.md"
    },
    {
      "name": "plan",
      "artifact_kind": "architect-plan-draft",
      "staged_path": ".cdad/inbox/plan.md"
    }
  ],
  "observed_changes": {
    "observation_status": "trusted",
    "baseline_ref": "<orchestrator-prepared-reference>",
    "baseline_sha256": "<64 lowercase hex>",
    "manifest_path": ".cdad/inbox/changes.json"
  },
  "run_evidence_ref": null
}
```

`source.kind` obligatorio en el MVP: `staged-file`. Cada part referencia un archivo
regular bajo el inbox fijo `.cdad/inbox` (aditivo dentro de `.cdad/`); traversal,
symlink escape y paths fuera del inbox son rechazados.

`sdk_message_ref` es opcional y sólo registra provenance declarada. Puede
acompañar un staged export exacto producido por un adaptador externo, pero 002 no
obtiene mensajes desde OpenCode/Codex ni autentica la referencia. No existe
`source.kind=sdk-fetch` en esta feature.

Cada part debe ser UTF-8 válido y no vacío. La suma de bytes de todas las parts de
un packet no supera 1 MiB. Nombres de part son únicos. Para architect draft se
admite el bundle pequeño `spec` + `plan`; cada archivo conserva sus bytes por
separado y en orden declarado.

`execution_id`, `packet_id`, `feature_id` y nombres de part son segmentos seguros:
ASCII `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`. No contienen separadores, whitespace,
`..` como segmento ni caracteres de control. La identidad se valida contra el
paquete y el execution context vigentes; no se infiere ni se re-deriva de nombres.

### 4. Identidad, scopes y freshness

Sólo existe una finalización durable por `(execution_id, packet_id)`. Un
`result_id` libre no permite finalizar otra vez el mismo packet.

Antes de una recepción nueva, la operación:

1. valida execution/state mediante `validate-state` v2 de 001 (identidad, vigencia
   de contrato I2 y delegación);
2. valida `PACKET.md` mediante `validate-packet` de 001 usando el `REQUEST.json`
   exacto;
3. exige coincidencia de execution, feature y packet;
4. exige `active_packet.status == "dispatched"` (fijado por la observación de
   dispatch del orquestador) o reconcilia un recibo durable ya existente para el
   mismo packet;
5. calcula SHA-256 y longitud de cada part y del manifest canónico del bundle;
6. valida el manifest de cambios observado contra el write scope declarado.

El manifest de cambios es JSON canónico:

```json
{
  "schema_version": 1,
  "observation_status": "trusted",
  "baseline_ref": "<opaque ref>",
  "baseline_sha256": "<64 lowercase hex>",
  "changes": [
    {"path": "scripts/example.py", "operation": "modified"}
  ]
}
```

Operaciones válidas: `added`, `modified`, `deleted`, `renamed`; rename incluye
`previous_path`. Entries ordenados por path, sin duplicados. Descriptor y manifest
coinciden en status, baseline y digest. `observation_status` es `trusted` o
`unknown`.

El manifest es preparado por la orquestación desde un baseline explícito. La
comparación demuestra únicamente que los paths declarados están dentro del scope.
No prueba autoría del rol, exhaustividad de lecturas, ausencia de cambios ocultos
fuera de la observación ni causalidad entre payload y diff. Si el runtime no
ofrece un manifest confiable, el resultado es `unknown`: receive puede persistir un
receipt pending, pero éste no puede usarse como gate ni materializarse hasta una
comprobación independiente trusted del orquestador. Un path observado fuera de
scope falla antes de publicar y no deja finalización durable.

Los targets propuestos por architect, reviewer, audit o scribe no se comparan
contra el write scope de la sesión read-only. Se validan después mediante una
política separada de artefactos materializables (§7). Proponer un artifact target
no concede permiso de escritura al rol.

### 5. Persistencia atómica, concurrencia y retry

Destino final:

```text
.cdad/runtime/results/<execution_id>/<packet_id>/
├── parts/<name>.utf8
├── bundle.json
└── receipt.json
```

La operación escribe parts, bundle y receipt en un directorio temporal hermano,
sincroniza los archivos y publica el directorio final mediante rename exclusivo en
el mismo filesystem.

- Interrupción antes de publicar: no existe resultado final; el retry puede limpiar
  sólo temporales que pertenecen al mismo execution/packet.
- Interrupción después de publicar: el retry lee y valida el receipt durable.
- Dos receives concurrentes idénticos: uno publica; el otro compara identidad y
  digests y devuelve exactamente el receipt durable existente.
- Mismo execution/packet con channel identity, part set, bytes o digests distintos:
  conflicto; no sobrescribe ni crea una segunda finalización.
- Receipt o payload durable incompleto/tampered: error de integridad; no se repara
  silenciosamente desde el input.

Al iniciar `receive`, antes de exigir el binding con `active_packet`, se busca un
resultado durable para execution/packet. Si existe, se valida su integridad y se
compara como retry. Así un retry read-only idéntico funciona aunque el orquestador
ya haya avanzado el packet. Autoridad vencida impide nuevas recepciones y
materializaciones, pero no leer ni validar receipts previos.

El retry no repite materialización ni transición de estado. Devuelve el mismo
receipt y permite al orquestador reconciliar qué efectos externos ya aplicó.

### 6. Recibo mecánico e inmutable

`receipt.json` incluye al menos:

```json
{
  "schema_version": 1,
  "execution_id": "exec-003-002-artifact-tools-001",
  "packet_id": "003-002-artifact-tools-architect-draft-001",
  "feature_id": "003-002-artifact-tools",
  "role": "architect",
  "substage": "draft",
  "source": {
    "kind": "staged-file",
    "sdk_message_ref": null
  },
  "parts": [
    {
      "name": "spec",
      "artifact_kind": "architect-spec-draft",
      "sha256": "<64 lowercase hex>",
      "bytes": 1234,
      "stored_ref": ".cdad/runtime/results/.../parts/spec.utf8"
    }
  ],
  "bundle_sha256": "<64 lowercase hex>",
  "packet_validation": "passed",
  "identity_validation": "passed",
  "scope_validation": "passed",
  "run_evidence_status": "not-provided",
  "semantic_status": "pending",
  "state_transition_requested": "received",
  "received_at": "<UTC timestamp>"
}
```

Valores de `scope_validation`: `passed`, `failed`, `unknown`. Valores de
`run_evidence_status`: `valid-current`, `invalid`, `stale`, `not-provided`.
`semantic_status` producido por receive siempre es `pending`.

`state_transition_requested` expresa una transición **lógica** (`received`). El
orquestador la mapea al estado válido de paquete `completed` (vocabulario de 001) y
es quien aplica el cambio; `receive` no lo aplica.

`receive` no modifica `docs/.cdad-state.json`. El orquestador es dueño de cambiar
el estado después de validar el receipt. Ante retry, primero reconcilia el receipt
durable y no repite un cambio ya reflejado en state.

### 7. Materialización explícita

`MATERIALIZE.json`:

```json
{
  "schema_version": 1,
  "execution_id": "exec-003-002-artifact-tools-001",
  "packet_id": "003-002-artifact-tools-architect-draft-001",
  "receipt_sha256": "<64 lowercase hex>",
  "authorized_by": "Pablo (HITL delegada al orquestador OpenCode)",
  "authority_ref": "docs/epics/epic-003-context-efficiency/execution.md",
  "approval_effect": false,
  "copies": [
    {
      "part": "spec",
      "target": "docs/specs/003-002-artifact-tools/spec.md",
      "expected_previous_sha256": null
    },
    {
      "part": "plan",
      "target": "docs/specs/003-002-artifact-tools/plan.md",
      "expected_previous_sha256": null
    }
  ]
}
```

La operación valida receipt, authority binding y una tabla cerrada que fija la
**raíz permitida** por `artifact_kind`; el **target exacto** se declara en la
autorización (no se infiere del texto del payload):

| artifact_kind / rol-subfase | Raíz permitida | Target |
|---|---|---|
| architect spec/plan draft | `docs/specs/<feature>/` | declarado en auth (`spec.md`, `plan.md`) |
| test-writer audit | `docs/specs/<feature>/` | `test-audit.md` |
| reviewer (`review`, `plan-review`) | `docs/specs/<feature>/` | declarado en auth (p. ej. `review.md`, `review-<n>.md`) |
| scribe | `docs/projectbrief.md`, `docs/systemPatterns.md`, `docs/activeContext.md`, `docs/progress.md` | cada target explícito en auth |
| test-writer no-audit | `docs/specs/<feature>/` | `test-writer-role-report.md` |
| implementer/refactor/review-fix | `docs/specs/<feature>/` | `implementer-role-report.md` |

Rol/subfase y `artifact_kind` usan una tabla cerrada; un kind de otro rol falla.
Los role-report son evidencia auxiliar, no sustituyen tests, diff, commit o suite.
Los ADR (`docs/adr/`) **no** están en esta tabla; su materialización sigue siendo
del orquestador (ADR-003) y ampliar la tabla a ADRs queda fuera de alcance (VERIFY
para el dueño).

El target debe ser exacto y permanecer bajo project root. No se infiere desde texto
del payload. `expected_previous_sha256=null` significa create-only: el target debe
estar ausente, salvo que ya contenga los bytes nuevos, caso idempotente. Un digest
no nulo autoriza reemplazo CAS sólo si coincide con el contenido actual. Otro
digest produce conflicto sin overwrite.

Materialize mantiene un journal durable ligado a receipt y authorization hash.
Cada copy usa archivo temporal + rename y registra target y SHA-256 final. No se
promete atomicidad entre múltiples targets: una interrupción puede dejar un prefijo
aplicado. El retry valida journal y contenido, omite copias ya aplicadas e idénticas
y continúa; nunca repite o sobrescribe un efecto divergente.

`approval_effect` siempre es `false` en esta feature. Materialize no agrega marcas
de aprobación, no cambia `semantic_status` y no actualiza state. La aprobación y
cualquier reemplazo posterior requieren la decisión CDAD externa correspondiente.

### 8. Evidencia de runner soportado

El único runner de evidencia nuevo es Python unittest. `RUN.json` contiene:

```json
{
  "schema_version": 1,
  "execution_id": "exec-003-002-artifact-tools-001",
  "packet_id": "003-002-artifact-tools-implementer-green-001",
  "argv": ["python3", "-m", "unittest", "discover", "-s", "tests"],
  "source_selection": ["skills/cdad-cycle/scripts", "scripts"],
  "test_selection": ["tests"],
  "contract_sha256": "<packet contract sha256>"
}
```

Sólo se admiten argv cuyo prefijo sea exactamente `python3 -m unittest`; los
argumentos posteriores son argv, sin shell, redirecciones ni operadores. Las
selecciones son roots/paths explícitos; si no puede demostrarse que cubren lo
relevante, la equivalencia es `unknown`.

La herramienta calcula snapshots; no acepta digests del caller. Para cada selección
descubre archivos tracked y untracked no ignorados, excluye `.git`, `.cdad/runtime`
y `.cdad/inbox`, ordena paths project-relative, calcula SHA-256 por archivo y
serializa entries como JSON canónico; el snapshot hash es SHA-256 de esos bytes.
Outputs de coordinación sólo se incluyen si la selección los nombra y su relevancia
está justificada.

El runner captura argv, cwd relativo, log combinado, exit code, timestamp y conteos
`tests_run`, `failures`, `errors`, `skipped`, `runner_exceptions`, más snapshots
before/after. Mutación de source o tests invalida la evidencia.

Evidencia `valid-current` requiere exit `0`, `tests_run > 0`, al menos un test no
skipped, `failures=errors=runner_exceptions=0`, snapshots before/after iguales y
contract vigente. Cero tests o suite sólo skipped no son verde. Estados:
`valid-current`, `invalid`, `stale`, `unknown`.

`validate-run-evidence` recalcula snapshots actuales desde `RUN.json` y valida
contra execution, packet y request actuales; no acepta autocoincidencia con los
digests/argv grabados en evidence. Campo ausente, selección incompleta, digest
desconocido o diferencia produce `stale`/`unknown`; no existe cache genérica.

Fixtures offline simulan staged payloads, concurrencia y unittest. Crash se prueba
matando un subprocess en el límite observable antes/después de publicar, o
preparando pending dirs documentados; no hay flag público de fallo ni mocks de
plumbing. No se requiere fetch OpenCode ni red.

### 9. Propiedad del estado y plan de validación por unidad

**Propiedad del estado (resuelto).** `docs/.cdad-state.json` tiene un solo
escritor: **el orquestador**. Ninguna herramienta de 003-002 lo toca.

| Productor | Escribe | NO escribe |
|---|---|---|
| `receive` (T1) | el store operacional `.cdad/runtime/…` + el receipt | el state, el contexto de ejecución, el árbol de trabajo |
| `materialize` (T2) | los artefactos destino permitidos por la política de artefactos (create-only/CAS) + su journal | el state; `approval_effect` es siempre `false` |
| `run-evidence` (T3) | su registro de evidencia + snapshots | el state |
| **orquestador** | `docs/.cdad-state.json`, `stage_history`, el binding del paquete y la materialización de los artefactos de solo-lectura (ADR-003) | el contenido de los artefactos de rol |

La referencia de receipt/estado en el state la agrega **el orquestador** (forma
existente de `stage_history`), no las herramientas. No se modifica
`state-template.json` ni el esquema del state.

**Plan de validación por unidad (PD-8).** El plan de la feature (`plan.md`) declara
el bloque canónico `plan-tasks` con T1–T4 y una estrategia común
(`@validation_strategy`). El formato de campos es de fuente única
(`planning-contract-draft.md` §4.1) y no se copia aquí. Cada tarea declara:

- `focal_tests` cuando hay código (T1–T4) — o `observable_checks` en ciclos sin
  código, adecuadas al artefacto y sin inventar una suite de software;
- `regressions` afectadas;
- `integration_gate` (referencia a la estrategia común o comprobación explícita);
- `owner` (quién ejecuta cada comprobación).

No hay tarea sin plan de validación ni postcondición sin tarea (ver Trazabilidad).

## Trazabilidad postcondición ↔ tarea

| Postcondición | Tarea(s) |
|---|---|
| P1 recepción exacta e identificada | T1 |
| P2 publicación atómica e idempotente | T1 |
| P3 recibo mecánico sin aprobación | T1 (base) + T2 (no aprueba) |
| P4 materialización exacta y autorizada | T2 |
| P5 evidencia de suite vigente y no vacía | T3 |
| P6 scopes y límites de prueba explícitos | T1 (base) + T2 (parte) + T4 (integración) |

## Postcondiciones

**P1. Recepción exacta e identificada.** Para un packet dispatched válido y un
descriptor válido, receive persiste cada part con bytes idénticos, liga
execution/packet/feature/role/substage y devuelve un receipt cuyos digests y
longitudes corresponden al payload. UTF-8 inválido, payload vacío o bundle mayor a
1 MiB falla sin resultado final.

**P2. Publicación atómica e idempotente.** Una interrupción previa a publicación no
deja resultado final; retry puede completar. Repetir o competir con contenido
idéntico devuelve el receipt durable byte a byte y existe una sola finalización por
execution/packet. Contenido, parts o provenance conflictivos fallan sin
sobrescribir.

**P3. Receipt mecánico sin aprobación.** El receipt es inmutable, valida packet,
identidad y scope declarado, conserva `unknown` cuando no hay prueba, y siempre
sale con `semantic_status=pending`. Receive no modifica state ni materializa
artefactos.

**P4. Materialización exacta y autorizada.** Una autorización válida copia los
bytes originales a un target permitido por la política de artefactos (raíz
permitida por `artifact_kind`; target exacto declarado en auth). Repetir con
iguales bytes es idempotente; CAS reemplaza Memory Bank sólo contra digest anterior
exacto. Target no permitido, authority/receipt discordante o contenido actual
inesperado falla. Retry multi-copy continúa desde journal sin prometer atomicidad
global. La operación no agrega aprobación ni actualiza state.

**P5. Evidencia de suite vigente y no vacía.** El runner calcula snapshots
before/after y registra argv, log, exit y conteos. Sólo exit `0`, tests > 0, alguno
no skipped, cero failures/errors/runner exceptions, árbol no mutado y equivalencia
actual exacta permiten `valid-current`; diferencia, selección incompleta o
desconocimiento impide reutilizarla como gate.

**P6. Scopes y límites de prueba explícitos.** El manifest observado fuera de write
scope falla; ausencia de manifest queda `unknown`. Targets read-only se validan por
la política de artefactos separada (§7). Ningún resultado afirma autoría, hidden
read audit, autenticidad del SDK ref o completitud del manifest más allá de la
evidencia entregada.

## Invariantes verificables

- Una pareja execution/packet tiene como máximo un bundle final durable.
- Bytes persistidos y materializados conservan SHA-256 y longitud.
- `semantic_status` no cambia por recepción o materialización.
- `docs/.cdad-state.json` sólo lo cambia el orquestador; `receive`, `materialize` y
  `run-evidence` no lo tocan.
- Evidencia desconocida o stale nunca se usa como gate verde.

## Criterios de aceptación

- [ ] Tests black-box cubren P1-P6 mediante fixtures offline.
- [ ] Architect spec+plan prueba bundle multi-part con bytes preservados.
- [ ] Tests de kill/failure antes de rename y retry dejan un único resultado.
- [ ] Dos procesos concurrentes idénticos convergen al mismo receipt; payloads
      distintos producen conflicto sin overwrite.
- [ ] Matriz de materialización cubre raíces permitidas, targets exactos en auth,
      read-only roles, create-only, CAS de Memory Bank, retry parcial, conflicto y
      escape de root.
- [ ] Python unittest evidencia suite verde no vacía; cero tests, exit no cero,
      sólo skipped, runner exception, mutación, snapshot cambiado y selección
      incompleta no son reutilizables.
- [ ] El recorrido de integración receive → reconcile → materialize no duplica
      efectos ni escribe state desde las herramientas; el orquestador registra la
      única transición de state.
- [ ] Smoke instalado funciona desde proyecto fixture sin wrappers del repo.
- [ ] Suite local aplicable verde; ausencia de CI se registra conforme al gate ya
      vigente.

## Fuera de alcance

- Fetch directo de mensajes OpenCode/Codex o autenticación de SDK refs.
- Recepción de binarios, payloads mayores a 1 MiB o blob store remoto.
- Inferencia/aprobación semántica, resumen o reescritura del resultado.
- Sobrescritura de artefactos divergentes.
- Cache universal o soporte genérico de runners.
- Detección de loops y retries de agentes (`003-003`).
- Checkpoints y reanudación de sesiones (`003-004`).
- Atribuir cambios a un agente o auditar lecturas ocultas.
- Cambiar el esquema del state, el contexto de ejecución, el renderer/validador de
  paquetes o la política del proyecto.
- Materializar ADRs (`docs/adr/`) mediante la tabla de artifact policy.

## Limitaciones aceptadas

- **No es un sandbox.** La recepción, materialización y evidencia son operaciones
  de proceso local sobre archivos; no aíslan al agente ni impiden accesos fuera de
  scope por otras vías. El control es de contrato + auditoría del orquestador.
- **El manifest observado no prueba autoría ni exhaustividad** (sólo que los paths
  declarados están dentro del scope). Con runtime sin manifest confiable, el
  resultado es `unknown` y no sirve como gate.
- **`trusted`/`valid-current` sólo afirman hechos mecánicos**; nunca aprobación
  semántica ni cierre de gate.
- **El runner de evidencia se limita a `python3 -m unittest`**; no es un sistema
  general de evidencia ni una cache.
- **La equivalencia de snapshots es por selección declarada**; una selección
  incompleta o desconocida degrada a `stale`/`unknown`, no a verde.
- **La recepción depende de la orquestación** para el inbox staged, el manifest y
  la observación de dispatch; sin ellos no hay gate ni materialización.

## Contexto técnico

- Contratos aprobados de `003-001-role-packets` (base), evolucionados al runtime
  **v2** por `004-002-project-execution-bootstrap` (contexto de ejecución
  `schema_version: 2`, store `.cdad/packets` + `.cdad/executions`, política
  `docs/cdad-policy.json`, observación de dispatch I8, agentes derivados I9).
- `docs/cdad-policy.json` (ADR-012) — clasificación de paths y scopes.
- `skills/cdad-cycle/scripts/cdad_packet.py` — `validate-state`, `validate-request`,
  `validate-packet`, `prepare` (I2, I8); no se redefine.
- `skills/cdad-cycle/references/project-execution.md` — bootstrap, autoridad,
  resume, `--record-dispatch`, reconciliación de política.
- `skills/cdad-cycle/references/re-entry.md` y `handoff-prompts.md` — re-entry.
- `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4/§4.1 —
  ficha y bloque `plan-tasks` (fuente única del formato).
- Roles read-only materializados hoy por el orquestador: architect, reviewer,
  test-writer AUDIT y scribe (ADR-003).
- Store operacional nuevo `.cdad/runtime` (y `.cdad/inbox`), aditivos dentro de
  `.cdad/`, excluidos del control de versiones.
- `docs/runtime-adopted-version.md` — versión operativa adoptada (commit
  `8cb6580`, raíz aislada, ámbito de proyecto).
