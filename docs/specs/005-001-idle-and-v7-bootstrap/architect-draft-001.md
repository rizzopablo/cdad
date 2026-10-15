# Borrador del architect — 005-001 (discovery + spec/plan)

Fuente: despacho 2 del orquestador (camino temporal fuera del CLI por I2
circular; ver `dispatch-ledger.md`). Architect `cdad-architect`,
`mofgw/deepseek-v4.1-flash`, sesión `<ses-62>` (subagente
del harness), solo lectura, 2026-10-08.

Este archivo conserva verbatim el TEXTO FINAL del architect. Las versiones
canónicas aprobadas están en `spec.md` y `plan.md`.

---

# 1. DISCOVERY — 005-001 (idle + bootstrap v7), puntos b–e

Base de código: `skills/cdad-cycle/scripts/cdad_packet.py` (v7 `ce09ed0`; los scripts del repo y de la raíz adoptada son byte a byte iguales, `dispatch-ledger.md`). Versión del CLI en el repo = versión operativa.

## 1.1 Mapa del control I2 (aprobación de contrato) y la circularidad

Cadena del control, de la superficie al registro:

- `prepare` (CLI) → `prepare()` (`cdad_packet.py:2478`) → lock (`:2490`) → `_select_execution` (`:2497`, def `:1454`) → bootstrap/reuso → resolución de contrato `_contract_for` (`:2523`, def `:912`) → armado del `request` (`:2573-2591`) → `validate_request(request, …)` (`:2600`).
- `validate_request` (`:681`) → `validate_state` (`:683`, def `:472`) → rama v2 → `_validate_v2_state` (`:582`) → `_validate_v2_vigency` (`:1313`) → `_approved_stage_entry` (`:1324`, def `:1263`).
- `validate-state` (CLI) → `main` (`:2991-3010`) → `_resolve_active_execution` (`:1607`) o `--execution-context` → `validate_state` (misma cadena). `render`/`validate-request`/`validate-packet` → `validate_request` (`:3016-3025`). `--resume-packet` → `_resume_packet` (`:1558`) → `validate_request` (`:1600`).

`_approved_stage_entry` (`:1263-1274`): recorre `state["stage_history"]` y devuelve la **primera** entrada con `item["feature"] == feature_id`, `item["stage"] == "specification"` y `approved_by` no vacío. **No recibe rol**, no examina ruta ni hash. La invoca `_validate_v2_vigency` (`:1324`) **para todos los roles**.

`_contract_for` (`:912-925`): `architect` → `("approved-epic-plan", "docs/epics/<epic>/plan.md")`; cualquier otro rol → `("approved-feature-spec", "docs/specs/<feature>/spec.md")`. El architect sin epic activo es rechazado con diagnóstico OPT-4/PD-12 (`:915-923`).

**La circularidad:** el contrato del architect es el **plan del epic**, pero el gate I2 le exige una entrada `stage: "specification"` (justo la spec que el architect va a redactar). El defecto no es el registro en sí, sino que el control es **agnóstico del rol**.

**Entrada rectificada (estado actual):** `docs/.cdad-state.json:1399-1407` — `{feature: 005-001-idle-and-v7-bootstrap, stage: "discovery-authorization", authorized_by: "Pablo", rectified_at, evidence: plan.md}`; `active_packet` ya es `null` (`:1494`). Como no tiene `stage: "specification"` ni `approved_by`, **hoy no habilita nada**; `dispatch-ledger.md:18` documenta `validate-state → rc=2 (I2)`.

## 1.2 El contrato del paquete ya está "pineado"; la **aprobación** no

`prepare` calcula el contrato leyendo el archivo real: `_read_bytes` + `sha256` (`:2555-2557`) y lo guarda en `request["contract"] = {kind, path, sha256, commit}`. `validate_request` re-lee el archivo y compara (`:750-753`): `"contract sha256 does not match exact content"`. Es decir, **el paquete ya queda atado a los bytes de la spec**; lo único que no queda atado es el **registro de aprobación**. `validate_request` además exige que `kind`/`path` coincidan con rol+ejecución (`:740-745`) y valida los bindings de `active_packet` (`:772-781`). Este es el punto que hace viable "aprobar esa spec concreta (ruta y sha256)": basta pinear el registro de aprobación y compararlo contra el contrato ya verificado.

## 1.3 Mapa de `active_packet` y del reemplazo (punto c)

- `_validate_active_packet` (`:440-469`): claves exactas `{id, role, substage, status, packet_version, contract_kind, contract_sha256}`; estados `{prepared, dispatched, completed, failed}` (`VALID_PACKET_STATUSES`, `:43`); en vuelo `ACTIVE_PACKET_STATUSES = {prepared, dispatched}` (`:100`).
- Ciclo de vida: `prepare` publica `prepared` (`:2596-2599`); `_record_dispatch` mueve solo `prepared→dispatched` (`:1926-1934`), nunca a `completed/failed`.
- **Bloqueo actual de reemplazo:** en la rama v2, si `active_packet.status ∈ {prepared,dispatched}` y el directorio del paquete tiene `REQUEST.json`/`PACKET.md` publicados, `prepare` lanza `"active packet … is …: complete or fail it before preparing a new packet (PD-4)"` (`:2498-2516`). Solo descarta la lectura a medio escribir si **no** está publicada (`:2503-2519`).
- **No existe camino en el CLI** para retirar un paquete `prepared` no despachado cuyo contrato cambió. `--resume-packet` lo rechaza vía `validate_request` (sha distinto, `:752-753`) o vía el control de revisión de política I11 (`:1590-1599`). Confirmado empíricamente en `dispatch-ledger.md:17`.
- Selección de sub-modos: `_reject_mode_mix` (`:2906-2944`); selectores reconcile/record/resume; flags ordinarios `_ORDINARY_FLAGS` (`:2872-2888`); parser `prepare` (`:2815-2847`). Un sub-modo nuevo debe declararse aquí.

## 1.4 Mapa del reposo (idle) y del bootstrap v2 (punto e)

- `validate-state` sin `--execution-context` → `_resolve_active_execution` (`:1607-1613`) exige `state.execution.id`; luego `validate_state`. Con un state en reposo que conserva el bloque `execution` de la última feature, `_validate_v2_vigency` falla porque `active_feature` (null) ≠ `execution.feature_id` (`:1327-1331`).
- Deuda **VALIDATE-IDLE** (`docs/specs/003-007-living-continuity/debt.md:16`): rechaza un state en reposo (`active_feature` nulo con el bloque `execution` de la última feature); debería aceptar `idle` o pedir archivar `execution`.
- Definición canónica de idle: `skills/cdad-cycle/references/state-detection.md:27-30` — `current_stage: "idle"` es válido solo cuando `active_feature` es `null`.
- Bootstrap v2: `_bootstrap_v2_execution` (`:1387-1429`) crea el contexto desde state+política+autoridad; `authority_ref` = `hitl_delegation.source` si hay epic, si no la ruta del contrato (`:1400-1407`).

## 1.5 Consumidores documentales y esquemas

- `references/project-execution.md` §2 (autoridad, `:51-65`), §4 (resume, `:82-91`), §6 (reconcile, `:104-122`).
- Convención de la marca de aprobación: `references/re-entry.md:117-121`, `references/state-detection.md:62-70`, `references/stage-2-specification.md:143-152`.
- Esquemas: `assets/active-packet.schema.json:9-20`, `assets/packet-request.schema.json:6-22`, `assets/state-template.json`. **`stage_history`/`epic_history` no tienen esquema validador** (entradas libres); el único sub-esquema de estado con claves exactas es `active_packet` (`_validate_active_packet`). Por eso pinear el registro de aprobación **no exige cambiar un archivo de esquema** — solo código + docs.

## 1.6 Radio de impacto (fixtures/oráculos afectados por el nuevo modelo de aprobación)

Fixtures que hoy acreditan el contrato con `{feature, stage: "specification", approved_by}` **sin pin** — quedarán inválidos para los roles de construcción si el pin es obligatorio:

- `tests/test_role_packets.py:101-108` y `:190-197` (portador v2 real, rol test-writer; crea `docs/specs/<f>/spec.md` en `:83-87`).
- `tests/test_packet_prepare.py:332-369` (prepara `architect/draft` desde un fixture **sin** `epic_history` epic-plan).
- `tests/test_004_002_t2_bootstrap.py:402-409` (negativo de aprobación vía `prepare`; positivos de `validate-state` en `:329`); `tests/test_004_002_t2_reviewfix.py:186-189,223-226`; `tests/test_004_002_t6_landing.py:116-120`.
- `tests/test_003_002_t1_receive.py:156-159`, `test_003_002_t2_materialize.py:162-165`, `test_003_002_t3_run_evidence.py:183-186`, `test_003_002_t4_integration.py:158-161`.

Debe seguir fallando (control negativo): `tests/test_004_002_t56_reviewfix.py:276-314` (architect sin epic activo).

## 1.7 UNKNOWN / no verificado en el código (declarado, sin inventar)

- **U1** — El valor exacto de `current_stage` del state en reposo de 003-006 (VALIDATE-IDLE) no está en el árbol ni en `debt.md`; no puedo fijar si usa `"idle"`. `VERIFY` con el dueño o el historial git.
- **U2** — No hay fuente única del vocabulario de `epic_history`: epic-003 usa `stage: "epic-planning"` (`docs/.cdad-state.json:110`) y epic-005 usa `stage: "epic-plan"` (`:156`). Afecta a cómo se localiza la aprobación del plan (ver Decisión abierta D1).
- **U3** — Si `--replace-packet` debe reutilizar la identidad/objetivo del paquete anterior o aceptar flags nuevos: decisión de diseño (ver D4).
- **U4** — No verifiqué el nombre exacto del test de paridad del CLI instalado (`tests/test_packet_prepare.py:748`, `test_p5_installed_cli_prepare_matches_repo_prepare`): confirmar en el RED.

---

# 2. SPEC (borrador)

```yaml
feature_id: 005-001-idle-and-v7-bootstrap
feature_name: Aprobación por rol, reemplazo de paquetes obsoletos y reposo legítimo
created_at: 2026-10-08
approved_by: <pending>
approved_at: <pending>
```

## Descripción funcional

El CLI de CDAD deja de tratar la spec como precondición para producir la spec: el **architect** se habilita con la aprobación del **plan del epic**; **test-writer, implementer y reviewer** exigen la aprobación de la **spec concreta** (ruta y `sha256`). Un paquete preparado y **nunca despachado** cuyo contrato cambió puede **reemplazarse** registrando el motivo y conservando el anterior, reusando solo la autorización vigente (sin aprobar el contrato nuevo); un paquete **despachado** sigue exigiendo reconciliación. Los bloqueos son distinguibles (aprobación pendiente / paquete obsoleto / estado incoherente) y dicen qué falta y cómo seguir. `validate-state` acepta un state en reposo legítimo y sigue rechazando uno incoherente (VALIDATE-IDLE).

Alcance del punto (a) ya cumplido: el primer `prepare` del epic publicó los agentes de proyecto v7 (`source_dir` y 11/11 hashes verificados, `dispatch-ledger.md:21-47`); se registra como evidencia, no como tarea.

## Contract (superficie e invariantes)

**Superficie CLI (propuesta):**

```
prepare --project-root R --role <rol> --substage <sub> --objective <texto>      # sin cambios
prepare --project-root R --replace-packet <packet-id> --reason <texto>          # NUEVO sub-modo
validate-state --project-root R [--execution-context P]                          # idle aceptado
```

**Registros de aprobación (contrato de datos):**

- Aprobación de **spec** (roles de construcción): entrada de `stage_history`
  `{feature, stage: "specification", approved_by: <no vacío>, approved_at?, contract_path: "docs/specs/<feature>/spec.md", contract_sha256: <64 hex>}`.
- Aprobación del **plan** (architect): entrada de `epic_history`
  `{epic | epic_id: <epic>, stage: "epic-plan", approved_by: <no vacío>}` (campos extra tolerados; **sin** pin de hash — rationale en D2).

**Marcadores de diagnóstico (stderr, rc=2), estables y observables:**

- `approval pending` — falta la aprobación (del plan para architect; de la spec concreta para los demás).
- `packet obsolete` — el paquete no es reanudable/reemplazable-en-frío sin resolver (contrato o revisión de política cambiados).
- `state incoherent` — el state contradice sus propios registros (binding, feature/epic, idle).

**Postcondiciones (numeradas y verificables):**

**PD-1 (architect habilitado por el plan del epic).** Con epic activo `E` y una entrada de `epic_history` `{epic==E, stage=="epic-plan", approved_by no vacío}`, `prepare --role architect` (cualquier subfase válida) → `rc=0`, publica contexto v2 + paquete, **sin** requerir entrada `specification` de la feature.

**PD-2 (el architect NO se habilita con la aprobación de spec).** Sin la entrada `epic-plan` de `E`, aunque exista una entrada `stage_history` `specification` con `approved_by`, `prepare --role architect` → `rc=2` con marcador `approval pending` que nombra el plan del epic; sin efectos.

**PD-3 (roles de construcción bloqueados sin la spec aprobada).** Sin una entrada `specification` cuyo `contract_sha256 == sha256(docs/specs/<feature>/spec.md)`, `prepare --role test-writer|implementer|reviewer` (subfase válida) → `rc=2`, marcador `approval pending`, nombra `stage_history`/`specification`/`approved` y la ruta de la spec; el árbol y el state quedan idénticos (sin publicaciones parciales).

**PD-4 (deriva del contrato invalida la aprobación).** Si la entrada `specification` existe con pin y luego se edita `spec.md` (el sha deja de coincidir), `prepare` para esos roles → `rc=2` `approval pending`, nombrando el digest registrado y el actual.

**PD-5 (aprobación pineada correcta habilita).** Con la entrada del PD-3/PD-4 presente y el `sha256` **coincidente** con el archivo, `prepare` para esos roles → `rc=0`.

**PD-6 (una entrada rectificada no habilita nada).** Un state cuya única señal es una entrada `{stage: "discovery-authorization", authorized_by, rectified_at}`: `prepare --role architect` → `rc=2` (no es `epic-plan`); `prepare --role test-writer` → `rc=2` (no es `specification`). Es exactamente el caso de `docs/.cdad-state.json:1399-1407`.

**PD-7 (reemplazo de paquete preparado y no despachado).** Con `active_packet.id == <id>`, `status == "prepared"` y obsolescencia verificada (PD-8), `prepare --replace-packet <id> --reason "<texto>"` → `rc=0`; se publica un **paquete nuevo** (id siguiente libre) con el contrato **actual** y la autorización vigente; `state.active_packet` pasa a apuntar al nuevo con `status: "prepared"`; el `REQUEST.json` y `PACKET.md` del paquete anterior quedan **byte a byte idénticos**; queda un registro durable de superación (`.cdad/packets/<id>/.superseded.json`) con `{superseded_by, reason, superseded_at, contract_sha256_old, contract_sha256_new}`; **ninguna** entrada de `stage_history`/`epic_history` se crea ni se modifica.

**PD-8 (reemplazo solo ante obsolescencia genuina).** `--replace-packet` es aceptado solo si (a) el `sha256` del contrato registrado en el `REQUEST.json` difiere del actual, **o** (b) la revisión de política del paquete difiere de la aceptada (I11). Si no hay obsolescencia verificable → `rc=2`, sin efectos (no es un atajo para saltar PD-4).

**PD-9 (el reemplazo exige motivo).** `--replace-packet` sin `--reason` no vacío → `rc=2`, sin efectos. `--reason` sin `--replace-packet` → `rc=2`.

**PD-10 (un paquete despachado no se reemplaza).** Con `status == "dispatched"`, `--replace-packet` → `rc=2`, marcador `packet obsolete`, mensaje que nombra la **reconciliación** requerida; sin efectos.

**PD-11 (el reemplazo no inventa autorización).** Si el contrato actual **no** está autorizado (p. ej. la spec cambió y el pin ya no coincide), `--replace-packet` → `rc=2` `approval pending`; no se publica paquete nuevo; el paquete viejo queda intacto. *(Recuperación sin inventar evidencia.)*

**PD-12 (diagnósticos distinguibles y accionables).** Para cada condición (aprobación pendiente / paquete obsoleto / estado incoherente) el CLI sale `rc=2` y el stderr contiene el marcador correspondiente (`approval pending`, `packet obsolete`, `state incoherent`), nombra el registro/falta concreto y la acción legítima siguiente; no altera el state ni publica archivos. Los marcadores son mutuamente excluyentes por condición.

**PD-13 (reposo legítimo aceptado).** Con `active_feature == null` y `current_stage == "idle"`, un state que conserva el bloque `execution` de la última feature (y/o un `active_packet` terminal `completed|failed`) → `validate-state` (rc=0) con salida `VALID` que declara el reposo (p. ej. `VALID: idle`).

**PD-14 (state incoherente rechazado).** `active_feature == null` con `current_stage` distinto de `"idle"` → `rc=2` `state incoherent`; y `active_feature` no nulo con `current_stage == "idle"` → `rc=2` `state incoherent`.

**PD-15 (reposo con paquete en vuelo rechazado).** `active_feature == null`, `current_stage == "idle"`, pero `active_packet.status ∈ {prepared, dispatched}` → `rc=2` `state incoherent` (un paquete en vuelo no puede coexistir con el reposo).

**PD-16 (resume de un paquete obsoleto falla con marcador).** `prepare --resume-packet <id>` sobre un paquete cuyo contrato o revisión de política cambió → `rc=2` `packet obsolete`, nombrando el valor registrado y el actual; si `status == prepared`, señala `--replace-packet`; si `dispatched`, señala reconciliación. Se preserva el comportamiento I11 vigente.

## Invariantes (verificables)

- **INV-1.** `prepare` (incluido `--replace-packet`) jamás publica un paquete sin que pase la verificación de autorización del rol sobre el contrato del día.
- **INV-2.** Ninguna operación de `prepare`/`--resume-packet`/`--replace-packet` **escribe** aprobaciones (`stage_history`/`epic_history`): el registro de aprobación es del orquestador, no del CLI.
- **INV-3.** El reemplazo nunca borra ni reescribe los bytes del paquete anterior (`REQUEST.json`/`PACKET.md` byte-idénticos).
- **INV-4.** El conjunto y el significado de `active_packet.status` no cambian (`{prepared, dispatched, completed, failed}`).
- **INV-5.** Determinismo: los mismos insumos producen los mismos bytes de paquete (se reusa el pipeline transaccional existente).
- **INV-6.** Ninguna entrada histórica no conforme (rectificada, de otro vocabulario o sin pin) habilita autoridad alguna.
- ∀ state con `active_feature == null` ⟺ `current_stage == "idle"` (coherencia de reposo).

## Criterios de aceptación

- [ ] Un test por postcondición (PD-1..PD-16), con control positivo interno donde haya negativo.
- [ ] **Prueba decisiva del plan** (PD-17, ver abajo) verde end-to-end.
- [ ] Suite completa verde (repo toca el **renderer/CLI** → suite completa, no solo focales) y `make validate` sin fallos nuevos al cierre.
- [ ] El paquete del architect se prepara **sin spec aprobada** y el de test-writer queda **bloqueado** hasta la aprobación pineada (evidencia pegada).
- [ ] `validate-state` acepta el reposo y rechaza el incoherente (evidencia pegada).

**PD-17 (prueba decisiva, un solo escenario secuencial):**
1. Fixture con epic `E` (entrada `epic_history` `stage: epic-plan`, `approved_by`), feature `F`, **sin** spec aprobada. `prepare --role architect --substage discovery` → `rc=0` (discovery autorizado).
2. `prepare --role test-writer --substage red` → `rc=2` `approval pending`; sin paquete en disco (construcción bloqueada).
3. Se crea `docs/specs/F/spec.md` y se registra la aprobación pineada (path+sha). `prepare --role test-writer --substage red` → `rc=0`, paquete P1.
4. Se **edita el plan del epic** (contrato del architect) → el paquete del architect (del paso 1) queda obsoleto. `prepare --resume-packet <architect-id>` → `rc=2` `packet obsolete`.
5. `prepare --replace-packet <architect-id> --reason "plan editado"` → `rc=0`; paquete nuevo con el sha actual del plan; bytes del anterior intactos; `.superseded.json` con el motivo; **sin** cambios en `stage_history`/`epic_history`.
6. Negativo: `--replace-packet` sobre otro paquete **no** obsoleto → `rc=2`, sin efectos.

## Fuera de alcance

- Activar/instalar versiones en el repo real ni cambios en HOME (reservado al dueño).
- Roles en Claude Code (005-004); medición de contexto (005-002); reducción de orientación (005-003).
- El resto de la deuda de 003-007 (`R2-STAGE`, `POLICY-CLASS`, `CKPT-FORK`, …).
- Unificación del vocabulario de `epic_history` de epics históricos (U2/D1); migración de estados de epics cerrados.
- Tests por frases; tests de cobertura no derivados de un PD.

## Contexto técnico

- Punto de enforcement propuesto: mover la **aprobación de contrato por rol** de `_validate_v2_vigency` (`:1324`) a `validate_request` (`:681`, donde se conoce `role` y ya está verificado `contract["sha256"]` contra el archivo en `:750-753`). `_validate_v2_vigency` conserva la **coherencia de estado** (feature/epic/delegación) que exigen los negativos de `validate-state` (`test_004_002_t2_reviewfix.py:215,527`) y PD-1 de `test_004_002_t2_bootstrap.py:329`.
- El nuevo sub-modo `--replace-packet` debe declararse en `build_parser` (`:2815-2847`), `_reject_mode_mix` (`:2906-2944`) y `main` (`:2961-2985`), y correr **antes** del bloque PD-4 (`:2498-2516`).
- Reutiliza el pipeline transaccional de `prepare` (`:2608-2789`) para INV-1/INV-3/INV-5.

---

# 3. PLAN (borrador)

## Restricciones globales

- Rama `codex/epic-005-real-operation`; sin push; sin `--no-verify`.
- v7 `ce09ed0`; no instalar/activar versiones (dueño). No leer `tests/.sensitive-patterns.local`.
- **Gate de tests: la feature toca el renderer/CLI (`cdad_packet.py`) → suite completa una vez por GREEN** (plan §Operación: "suite completa al cierre de cada feature o si se toca instalador, staging o renderer"), más focales del área y `make validate` al cierre.

## Tareas

### T1 — Modelo de autorización por rol (corrige I2 circular) · PD-1..PD-6, PD-12(aprobación)
- **Files**: `skills/cdad-cycle/scripts/cdad_packet.py` (Modify: `_validate_v2_vigency`, `_validate_v2_state`, nueva `_contract_approval_for(role, contract, state, execution, project_root)` invocada desde `validate_request`); `skills/cdad-cycle/references/project-execution.md` §2 (Modify); `skills/cdad-cycle/references/re-entry.md` (Modify: forma pineada del registro); `skills/cdad-cycle/references/stage-2-specification.md` (Modify si corresponde). **Tests (RED/New)**: `tests/test_005_001_t1_role_approval.py`. **Tests (migrados, consecuencia)**: `tests/test_role_packets.py`, `tests/test_packet_prepare.py`, `tests/test_004_002_t2_bootstrap.py`, `tests/test_004_002_t2_reviewfix.py`, `tests/test_004_002_t6_landing.py`, `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_003_002_t3_run_evidence.py`, `tests/test_003_002_t4_integration.py`.
- **Produce**: autorización role-aware; forma pineada del registro de spec; marcador `approval pending`.
- **Consume**: contrato verificado en `validate_request`.
- **Depends_on**: —.
- **TDD steps**: RED (PD-1..PD-6 + migración de fixtures, todos `AssertionError` de comportamiento) → GREEN (mínimo) → focales + **suite completa**.
- **Owner**: RED: test-writer; GREEN: implementer.

### T2 — Reemplazo de paquete preparado no despachado + diagnósticos de obsolescencia · PD-7..PD-11, PD-16, PD-12(paquete obsoleto)
- **Files**: `cdad_packet.py` (Modify: parser, `_reject_mode_mix`, `main`, nueva `_replace_packet`, ajuste de `_resume_packet` para emitir el marcador); `references/project-execution.md` (Modify: nueva sección "Reemplazo"). **Tests (New)**: `tests/test_005_001_t2_replace_packet.py`.
- **Produce**: sub-modo `--replace-packet`/`--reason`; registro `.superseded.json`; marcador `packet obsolete`.
- **Consume**: T1 (la autorización vigente gatea el contrato nuevo).
- **Depends_on**: T1.
- **TDD steps**: RED → GREEN → focales + suite completa.
- **Owner**: RED: test-writer; GREEN: implementer.

### T3 — Reposo legítimo + estado incoherente · PD-13..PD-15, PD-12(estado incoherente)
- **Files**: `cdad_packet.py` (Modify: rama `validate-state` en `main` `:2991-3010` + validación de coherencia de idle); `references/state-detection.md` (Modify: criterio de reposo). **Tests (New)**: `tests/test_005_001_t3_idle.py`.
- **Produce**: aceptación del reposo; marcador `state incoherent`.
- **Consume**: — (usa la coherencia v2 existente).
- **Depends_on**: T1 (no regresar la verificación de vigencia; misma rama de validación).
- **TDD steps**: RED (positivo idle + 2 negativos + en-vuelo) → GREEN → focales + suite completa.
- **Owner**: RED: test-writer; GREEN: implementer.

### T4 — Prueba decisiva e integración · PD-17
- **Files**: `tests/test_005_001_t4_decisive.py` (New). Sin cambios de producto.
- **Consume**: T1, T2, T3.
- **Depends_on**: T1, T2, T3.
- **TDD steps**: el escenario secuencial de PD-17 (si algo falla, vuelve a la tarea correspondiente); verificación adicional de `make validate`.
- **Owner**: test-writer (RED del escenario completo); implementer solo si destapa un defecto.

## Bloque canónico `plan-tasks`

```plan-tasks
{"validation_strategy": "suite completa una vez por GREEN (renderer/CLI tocado); regresiones del area tocada; make validate al cierre",
 "tasks": [
  {"id": "T1",
   "produce": [{"artifact": "autorizacion-por-rol", "contract": "spec-005-001-PD1-PD6"}],
   "consume": [{"artifact": "contrato-verificado", "contract": "cdad_packet.validate_request"}],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/references/project-execution.md", "tests/test_005_001_t1_role_approval.py"],
   "focal_tests": ["tests/test_005_001_t1_role_approval.py"],
   "regressions": ["tests/test_role_packets.py", "tests/test_packet_prepare.py", "tests/test_004_002_t2_bootstrap.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "produce": [{"artifact": "reemplazo-paquete-obsoleto", "contract": "spec-005-001-PD7-PD11-PD16"}],
   "consume": [{"artifact": "autorizacion-por-rol", "contract": "spec-005-001-PD1-PD6", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/references/project-execution.md", "tests/test_005_001_t2_replace_packet.py"],
   "focal_tests": ["tests/test_005_001_t2_replace_packet.py"],
   "regressions": ["tests/test_packet_prepare.py", "tests/test_004_002_t56_reviewfix.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "produce": [{"artifact": "reposo-legitimo", "contract": "spec-005-001-PD13-PD15"}],
   "consume": [],
   "depends_on": ["T1"],
   "parallel": ["T2"],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/references/state-detection.md", "tests/test_005_001_t3_idle.py"],
   "focal_tests": ["tests/test_005_001_t3_idle.py"],
   "regressions": ["tests/test_004_002_t2_reviewfix.py", "tests/test_004_002_w1_delegation.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "produce": [{"artifact": "prueba-decisiva", "contract": "spec-005-001-PD17"}],
   "consume": [{"artifact": "autorizacion-por-rol", "contract": "spec-005-001-PD1-PD6", "producer": "T1"},
               {"artifact": "reemplazo-paquete-obsoleto", "contract": "spec-005-001-PD7-PD11-PD16", "producer": "T2"},
               {"artifact": "reposo-legitimo", "contract": "spec-005-001-PD13-PD15", "producer": "T3"}],
   "depends_on": ["T1", "T2", "T3"],
   "parallel": [],
   "files": ["tests/test_005_001_t4_decisive.py"],
   "focal_tests": ["tests/test_005_001_t4_decisive.py"],
   "regressions": [],
   "integration_gate": "suite completa + make validate",
   "owner": "test-writer"}
 ]}
```

## Auto-revisión del plan

- **Cobertura**: PD-1..PD-6→T1; PD-7..PD-11/PD-16→T2; PD-13..PD-15→T3; PD-17→T4; PD-12→definido por marcadores en T1/T2/T3. Sin PD huérfano; sin tarea sin PD.
- **Placeholders**: ninguno ("TBD"/"similar a"/vague handling ausentes).
- **Consistencia de firmas**: `--replace-packet`/`--reason`, `contract_path`/`contract_sha256`, marcadores `approval pending`/`packet obsolete`/`state incoherent` usados idénticos en spec y plan.
- **Consecuencia de alcance declarada**: T1 obliga a migrar fixtures (mismo patrón que 004-003 T4); las aserciones no se debilitan, solo se agrega el pin derivado del `spec.md` del fixture.

---

# 4. RIESGOS Y DECISIONES ABIERTAS

Para el dueño / orquestador (HITL delegado):

- **D1 — ¿De dónde sale la aprobación del plan para el architect?** Propuesta: entrada de `epic_history` `{stage: "epic-plan", approved_by}` (existe para epic-005, `docs/.cdad-state.json:155-162`). Alternativas: frontmatter del `plan.md` (`status: approved`, parseo nuevo) o un registro nuevo. Riesgo: vocabulario inconsistente (`epic-plan` vs `epic-planning`, U2). Elegir una fuente; no dos.
- **D2 — ¿Se pinea también la aprobación del plan?** Propuesta: **no**. El `plan.md` de epic-005 se editó **después** de la aprobación ("Cambios al plan") y la aprobación sigue vigente; pinear el hash bloquearía al architect. Para la spec, sí se pinea. Confirmar esta asimetría (plan = mandato vivo del epic; spec = contrato congelado de la feature).
- **D3 — Pin obligatorio de la spec y migración de fixtures.** Propuesta: `contract_path` + `contract_sha256` obligatorios en la entrada `specification`; migración mecánica de ~8 módulos de test (radio en §1.6). Si el dueño prefiere cero migración, habría que aceptar el pin solo "cuando está presente" → habilita atajos (no recomendado).
- **D4 — Semántica de `--replace-packet`.** Propuesta: sin flags ordinarios; reusa identidad/subfase/objetivo del `REQUEST.json` anterior y solo re-resuelve el contrato y la política; `--reason` obligatorio. Naming alternativo: `--supersede-packet`.
- **D5 — Definición de reposo legítimo.** Propuesta: `active_feature == null` ⟺ `current_stage == "idle"`; se tolera `execution` remanente y `active_packet` terminal; se rechaza paquete en vuelo. Depende de **U1** (¿el reposo real usa `current_stage: "idle"`?): verificar antes de fijar el oráculo.
- **D6 — Alcance del enforcement en `validate-state`.** Propuesta: `validate-state` valida coherencia de estado; la aprobación de contrato por rol se exige en `prepare`/`validate-request` (donde hay rol). ¿Se quiere que `validate-state` siga exigiendo alguna aprobación sin rol? Con `active_packet` presente podría usar su `role`, pero con `active_packet: null` (caso real actual) no hay rol.
- **R1 — Radio de la migración de fixtures** (§1.6): puede tocar 10 archivos; si crece, evaluar (como en 004-003) separar "T1-red-fixtures".
- **R2 — Mensajes vs oráculos existentes**: los negativos actuales exigen tokens `stage_history|specification|approved` (`test_004_002_t2_bootstrap.py:407`); el marcador nuevo debe **conservarlos**. Riesgo bajo, pero hay que verificar en el RED.
- **R3 — Paridad del CLI instalado** (U4): tocar `cdad_packet.py` obliga a que el test de paridad instalado (`test_packet_prepare.py:748`) siga verde; la suite completa por GREEN lo cubre.
- **R4 — Sin CI**: el gate 5 es la suite local + deuda registrada; `make validate` tiene 2 FAIL preexistentes conocidos (F011) que no deben atribuirse a este diff.

Fin del borrador. No escribí archivos ni ejecuté git de producto; `VERIFY` marcado en U1–U4.