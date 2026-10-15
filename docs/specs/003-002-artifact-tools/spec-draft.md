---
feature_id: 003-002-artifact-tools
feature_name: Recepción original y materialización explícita
created_at: 2026-09-17
approved_by: <pending>
approved_at: <pending>
---

# Spec: Recepción original y materialización explícita

## Descripción funcional

CDAD debe recibir el resultado original de un rol identificado por los
contratos de 001, persistir exactamente sus bytes de forma atómica e idempotente
y emitir un recibo mecánico breve. Después, una operación separada y autorizada
por el orquestador puede copiar partes del resultado a destinos canónicos
permitidos para el rol.

Recepción, materialización y aprobación semántica son hechos distintos. Ningún
recibo aprueba un spec, una review, un audit ni Memory Bank; ningún texto es
resumido o regenerado por estas operaciones.

## Contrato

### 1. Dependencia e instalación

002 consume las interfaces estables aprobadas de 001: execution context,
packet metadata, `validate-state`, `validate-packet`, identidad de
`active_packet`, contrato SHA-256 y scopes tipados. No redefine esos schemas.

La implementación canónica usa Python 3 stdlib y vive junto a 001:

```text
skills/cdad-cycle/scripts/cdad_result.py
```

El repo expone un wrapper fino `scripts/cdad_result.py`. La instalación ofrece
un entrypoint equivalente que resuelve schemas relativos a la skill instalada.
No se introduce un framework de workflow, blob store ni cache general.

El store durable operacional es:

```text
PROJECT_ROOT/.cdad/runtime/
```

Debe estar gitignored. Los artefactos versionados siguen bajo sus destinos
canónicos; el store no los reemplaza.

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

`--project-root` es opcional y por defecto es el directorio de trabajo actual.
Éxito devuelve `0`. `receive` escribe en stdout exactamente los bytes del
`receipt.json` canónico; un retry idéntico escribe los mismos bytes. Una
violación devuelve código distinto de `0`, diagnóstico por stderr y ningún
recibo, artefacto o evidencia parcial por stdout. Los paths persistidos son
project-relative y normalizados.

### 3. Descriptor de resultado

`RESULT.json`:

```json
{
  "schema_version": 1,
  "execution_id": "exec-003-002-0001",
  "packet_id": "packet-003-002-0001",
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

`source.kind` obligatorio en el MVP: `staged-file`. Cada part referencia un
archivo regular bajo el inbox fijo `.cdad/inbox`; traversal,
symlink escape y paths fuera del inbox son rechazados.

`sdk_message_ref` es opcional y sólo registra provenance declarada. Puede
acompañar un staged export exacto producido por un adaptador externo, pero 002
no obtiene mensajes desde OpenCode/Codex ni autentica la referencia. No existe
`source.kind=sdk-fetch` en esta feature.

Cada part debe ser UTF-8 válido y no vacío. La suma de bytes de todas las parts
de un packet no supera 1 MiB. Nombres de part son únicos. Para architect draft
se admite el bundle pequeño `spec` + `plan`; cada archivo conserva sus bytes
por separado y en orden declarado.

`execution_id`, `packet_id`, `feature_id` y nombres de part son segmentos
seguros: ASCII `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`. No contienen separadores,
whitespace, `..` como segmento ni caracteres de control.

### 4. Identidad, scopes y freshness

Sólo existe una finalización durable por `(execution_id, packet_id)`. Un
`result_id` libre no permite finalizar otra vez el mismo packet.

Antes de una recepción nueva, la operación:

1. valida execution/state mediante 001;
2. valida `PACKET.md` mediante 001 usando el `REQUEST.json` exacto;
3. exige coincidencia de execution, feature y packet;
4. exige `active_packet.status == "dispatched"` o reconcilia un recibo durable
   ya existente para el mismo packet;
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
`previous_path`. Entries ordenados por path, sin duplicados. Descriptor y
manifest coinciden en status, baseline y digest. `observation_status` es
`trusted` o `unknown`.

El manifest es preparado por la orquestación desde un baseline explícito. La comparación
demuestra únicamente que los paths declarados están dentro del scope. No prueba
autoría del rol, exhaustividad de lecturas, ausencia de cambios ocultos fuera de
la observación ni causalidad entre payload y diff. Si el runtime no ofrece un
manifest confiable, el resultado es `unknown`: receive puede persistir un
receipt pending, pero éste no puede usarse como gate ni materializarse hasta una
comprobación independiente trusted del orquestador. Un path observado fuera de
scope falla antes de publicar y no deja finalización durable.

Los targets propuestos por architect, reviewer, audit o scribe no se comparan
contra el write scope de la sesión read-only. Se validan después mediante una
política separada de artefactos materializables. Proponer un artifact target no
concede permiso de escritura al rol.

### 5. Persistencia atómica, concurrencia y retry

Destino final:

```text
.cdad/runtime/results/<execution_id>/<packet_id>/
├── parts/<name>.utf8
├── bundle.json
└── receipt.json
```

La operación escribe parts, bundle y receipt en un directorio temporal hermano,
sincroniza los archivos y publica el directorio final mediante rename exclusivo
en el mismo filesystem.

- Interrupción antes de publicar: no existe resultado final; el retry puede
  limpiar sólo temporales que pertenecen al mismo execution/packet.
- Interrupción después de publicar: el retry lee y valida el receipt durable.
- Dos receives concurrentes idénticos: uno publica; el otro compara identidad y
  digests y devuelve exactamente el receipt durable existente.
- Mismo execution/packet con channel identity, part set, bytes o digests
  distintos: conflicto; no sobrescribe ni crea una segunda finalización.
- Receipt o payload durable incompleto/tampered: error de integridad; no se
  repara silenciosamente desde el input.

Al iniciar `receive`, antes de exigir el binding con `active_packet`, se busca
un resultado durable para execution/packet. Si existe, se valida su integridad y
se compara como retry. Así un retry read-only idéntico funciona aunque el
orquestador ya haya avanzado el packet. Autoridad vencida impide nuevas
recepciones y materializaciones, pero no leer ni validar receipts previos.

El retry no repite materialización ni transición de estado. Devuelve el mismo
receipt y permite al orquestador reconciliar qué efectos externos ya aplicó.

### 6. Recibo mecánico e inmutable

`receipt.json` incluye al menos:

```json
{
  "schema_version": 1,
  "execution_id": "exec-003-002-0001",
  "packet_id": "packet-003-002-0001",
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

`receive` no modifica `.cdad-state.json`. El orquestador es dueño de cambiar el
estado después de validar el receipt. Ante retry, primero reconcilia el receipt
durable y no repite un cambio ya reflejado en state.

### 7. Materialización explícita

`MATERIALIZE.json`:

```json
{
  "schema_version": 1,
  "execution_id": "exec-003-002-0001",
  "packet_id": "packet-003-002-0001",
  "receipt_sha256": "<64 lowercase hex>",
  "authorized_by": "Codex (orquestador/HITL delegado)",
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

La operación valida receipt, authority binding y una tabla cerrada de
`artifact_kind -> target`:

- architect spec/plan draft → `docs/specs/<feature>/spec.md|plan.md`;
- test-writer audit → `docs/specs/<feature>/test-audit.md`;
- reviewer → `docs/specs/<feature>/review.md`;
- scribe → exclusivamente `docs/projectbrief.md`, `docs/systemPatterns.md`,
  `docs/activeContext.md` y `docs/progress.md`, cada target explícito en auth;
- test-writer no-audit → `docs/specs/<feature>/test-writer-role-report.md`;
- implementer/refactor/review-fix →
  `docs/specs/<feature>/implementer-role-report.md`.

Rol/substage y `artifact_kind` usan una tabla cerrada; un kind de otro rol falla.
Los role-report son evidencia auxiliar, no sustituyen tests, diff, commit o suite.

El target debe ser exacto y permanecer bajo project root. No se infiere desde
texto del payload. `expected_previous_sha256=null` significa create-only: el
target debe estar ausente, salvo que ya contenga los bytes nuevos, caso
idempotente. Un digest no nulo autoriza reemplazo CAS sólo si coincide con el
contenido actual. Otro digest produce conflicto sin overwrite.

Materialize mantiene un journal durable ligado a receipt y authorization hash.
Cada copy usa archivo temporal + rename y registra target y SHA-256 final. No se
promete atomicidad entre múltiples targets: una interrupción puede dejar un
prefijo aplicado. El retry valida journal y contenido, omite copias ya aplicadas
e idénticas y continúa; nunca repite o sobrescribe un efecto divergente.

`approval_effect` siempre es `false` en esta feature. Materialize no agrega
marcas de aprobación, no cambia `semantic_status` y no actualiza state. La
aprobación y cualquier reemplazo posterior requieren la decisión CDAD externa
correspondiente.

### 8. Evidencia de runner soportado

El único runner de evidencia nuevo es Python unittest. `RUN.json` contiene:

```json
{
  "schema_version": 1,
  "execution_id": "exec-003-002-0001",
  "packet_id": "packet-003-002-0001",
  "argv": ["python3", "-m", "unittest", "discover", "-s", "tests"],
  "source_selection": ["skills/cdad-cycle/scripts", "scripts"],
  "test_selection": ["tests"],
  "contract_sha256": "<packet contract sha256>"
}
```

Sólo se admiten argv cuyo prefijo sea exactamente
`python3 -m unittest`; los argumentos posteriores son argv, sin shell,
redirecciones ni operadores. Las selecciones son roots/paths explícitos; si no
puede demostrarse que cubren lo relevante, la equivalencia es `unknown`.

La herramienta calcula snapshots; no acepta digests del caller. Para cada
selección descubre archivos tracked y untracked no ignorados, excluye `.git`,
`.cdad/runtime` y `.cdad/inbox`, ordena paths project-relative, calcula SHA-256
por archivo y serializa entries como JSON canónico; el snapshot hash es SHA-256
de esos bytes. Outputs de coordinación sólo se incluyen si la selección los
nombra y su relevancia está justificada.

El runner captura argv, cwd relativo, log combinado, exit code, timestamp y
conteos `tests_run`, `failures`, `errors`, `skipped`, `runner_exceptions`, más
snapshots before/after. Mutación de source o tests invalida la evidencia.

Evidencia `valid-current` requiere exit `0`, `tests_run > 0`, al menos un test
no skipped, `failures=errors=runner_exceptions=0`, snapshots before/after iguales
y contract vigente. Cero tests o suite sólo skipped no son verde. Estados:
`valid-current`, `invalid`, `stale`, `unknown`.

`validate-run-evidence` recalcula snapshots actuales desde `RUN.json` y valida
contra execution, packet y request actuales; no acepta autocoincidencia con los
digests/argv grabados en evidence. Campo ausente, selección incompleta, digest
desconocido o diferencia produce `stale`/`unknown`; no existe cache genérica.

Fixtures offline simulan staged payloads, concurrencia y unittest. Crash se
prueba matando un subprocess en el límite observable antes/después de publicar,
o preparando pending dirs documentados; no hay flag público de fallo ni mocks
de plumbing. No se requiere fetch OpenCode ni red.

## Postcondiciones

**P1. Recepción exacta e identificada.** Para un packet dispatched válido y un
descriptor válido, receive persiste cada part con bytes idénticos, liga
execution/packet/feature/role/substage y devuelve un receipt cuyos digests y
longitudes corresponden al payload. UTF-8 inválido, payload vacío o bundle
mayor a 1 MiB falla sin resultado final.

**P2. Publicación atómica e idempotente.** Una interrupción previa a publicación
no deja resultado final; retry puede completar. Repetir o competir con contenido
idéntico devuelve el receipt durable byte a byte y existe una sola finalización
por execution/packet. Contenido, parts o provenance conflictivos fallan sin
sobrescribir.

**P3. Receipt mecánico sin aprobación.** El receipt es inmutable, valida packet,
identidad y scope declarado, conserva `unknown` cuando no hay prueba, y siempre
sale con `semantic_status=pending`. Receive no modifica state ni materializa
artefactos.

**P4. Materialización exacta y autorizada.** Una autorización válida copia los
bytes originales a un target permitido por artifact policy. Repetir con iguales
bytes es idempotente; CAS reemplaza Memory Bank sólo contra digest anterior
exacto. Target no permitido, authority/receipt discordante o contenido actual
inesperado falla. Retry multi-copy continúa desde journal sin prometer atomicidad
global. La operación no agrega aprobación ni actualiza state.

**P5. Evidencia de suite vigente y no vacía.** El runner calcula snapshots
before/after y registra argv, log, exit y conteos. Sólo exit `0`, tests > 0,
alguno no skipped, cero failures/errors/runner exceptions, árbol no mutado y
equivalencia actual exacta permiten `valid-current`; diferencia, selección
incompleta o desconocimiento impide reutilizarla como gate.

**P6. Scopes y límites de prueba explícitos.** El manifest observado fuera de
write scope falla; ausencia de manifest queda `unknown`. Targets read-only se
validan por artifact policy separada. Ningún resultado afirma autoría, hidden
read audit, autenticidad del SDK ref o completitud del manifest más allá de la
evidencia entregada.

## Invariantes verificables

- Una pareja execution/packet tiene como máximo un bundle final durable.
- Bytes persistidos y materializados conservan SHA-256 y longitud.
- `semantic_status` no cambia por recepción o materialización.
- Estado CDAD sólo lo cambia el orquestador después de reconciliar receipt.
- Evidencia desconocida o stale nunca se usa como gate verde.

## Criterios de aceptación

- [ ] Tests black-box cubren P1-P6 mediante fixtures offline.
- [ ] Architect spec+plan prueba bundle multi-part con bytes preservados.
- [ ] Tests de kill/failure antes de rename y retry dejan un único resultado.
- [ ] Dos procesos concurrentes idénticos convergen al mismo receipt; payloads
      distintos producen conflicto sin overwrite.
- [ ] Matriz de materialización cubre targets permitidos, read-only roles,
      create-only, CAS de Memory Bank, retry parcial, conflicto y escape de root.
- [ ] Python unittest evidencia suite verde no vacía; cero tests, exit no cero,
      sólo skipped, runner exception, mutación, snapshot cambiado y selección
      incompleta no son reutilizables.
- [ ] Smoke instalado funciona desde proyecto fixture sin wrappers del repo.
- [ ] Suite local aplicable verde; ausencia de CI se registra conforme al gate
      ya vigente.

## Fuera de alcance

- Fetch directo de mensajes OpenCode/Codex o autenticación de SDK refs.
- Recepción de binarios, payloads mayores a 1 MiB o blob store remoto.
- Inferencia/aprobación semántica, resumen o reescritura del resultado.
- Sobrescritura de artefactos divergentes.
- Cache universal o soporte genérico de runners.
- Detección de loops y retries de agentes (`003-003`).
- Checkpoints y reanudación de sesiones (`003-004`).
- Atribuir cambios a un agente o auditar lecturas ocultas.

## Contexto técnico

- Contratos aprobados de `003-001-role-packets`.
- `skills/cdad-cycle/references/re-entry.md`.
- `skills/cdad-cycle/references/handoff-prompts.md`.
- Roles read-only materializados hoy por el orquestador: architect, reviewer,
  test-writer AUDIT y scribe.
- Store operacional nuevo `.cdad/runtime`, separado de `docs/` y gitignored.

---

Status: Pending approval
