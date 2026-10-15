> Materializado por el orquestador desde `architect-draft-001.md` (architect,
> `mofgw/deepseek-v4.1-flash`, sesión `<ses-62>`),
> verbatim salvo frontmatter y la sección de decisiones/aprobación. Aprobada por
> el orquestador OpenCode bajo la delegación HITL de epic-005 (`execution.md`),
> 2026-10-08.
>
> **Enmienda 2026-10-09 (T-CORR).** Dos correcciones acotadas de T1/T2 instruidas
> por el dueño (`docs/epics/epic-005-real-operation/plan.md`, apartado «Cambios al
> plan», 2026-10-09): (C1) el pin de la aprobación de spec exige `contract_path`
> además de `contract_sha256` (PD-3/PD-5 ajustadas; PD-18 nueva); (C2)
> `--replace-packet` conserva el encargo anterior y admite las opciones de
> corrección `--input/--read-scope/--write-scope/--invariant/--expected-output/--evidence`
> (PD-19..PD-24 nuevas; D4 enmendada; D7 nueva). No cambia el alcance ni los
> criterios del epic. La enmienda fue **aprobada el 2026-10-09** por el
> orquestador OpenCode (HITL delegada epic-005) y su aprobación pineada se
> re-registró en `stage_history` con los bytes nuevos de este archivo (la
> aprobación del 2026-10-08 cubría los bytes previos y quedó superada, PD-4).

## Spec — 005-001-idle-and-v7-bootstrap

**Feature ID:** `005-001-idle-and-v7-bootstrap` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobada (2026-10-08, orquestador OpenCode, HITL delegada epic-005);
**enmienda T-CORR (2026-10-09) aprobada (orquestador OpenCode, HITL delegada epic-005)**.
ADR-011 gobierna autoridad, capacidades y límites.

```yaml
feature_id: 005-001-idle-and-v7-bootstrap
feature_name: Aprobación por rol, reemplazo de paquetes obsoletos y reposo legítimo
created_at: 2026-10-08
amended_at: 2026-10-09
amended_approved_by: orquestador OpenCode (HITL delegada epic-005)
amended_approved_at: 2026-10-09
approved_by: orquestador OpenCode (HITL delegada epic-005)
approved_at: 2026-10-08
```

### 1. Descripción funcional

El CLI de CDAD deja de tratar la spec como precondición para producir la spec: el **architect** se habilita con la aprobación del **plan del epic**; **test-writer, implementer y reviewer** exigen la aprobación de la **spec concreta** (ruta y `sha256`). Un paquete preparado y **nunca despachado** cuyo contrato cambió puede **reemplazarse** registrando el motivo y conservando el anterior, reusando solo la autorización vigente (sin aprobar el contrato nuevo); un paquete **despachado** sigue exigiendo reconciliación. Los bloqueos son distinguibles (aprobación pendiente / paquete obsoleto / estado incoherente) y dicen qué falta y cómo seguir. `validate-state` acepta un state en reposo legítimo y sigue rechazando uno incoherente (VALIDATE-IDLE).

Alcance del punto (a) ya cumplido: el primer `prepare` del epic publicó los agentes de proyecto v7 (`source_dir` y 11/11 hashes verificados, `dispatch-ledger.md`); se registra como evidencia, no como tarea.

**Enmienda T-CORR (2026-10-09).** Dos correcciones acotadas dentro de la misma feature, instruidas por el dueño antes de su cierre: (C1) la **ruta de la aprobación** — el registro de aprobación de spec debe *nombrar* el contrato: no alcanza con el `sha256` correcto si el `contract_path` registrado es otro (o falta); (C2) la **conservación y corrección en el reemplazo** — `--replace-packet` deja de recomputar los valores por defecto y conserva el encargo anterior del `REQUEST.json` vigente, permitiendo corregirlo con opciones explícitas, manteniendo siempre los pisos obligatorios del rol y registrando qué se conservó y qué cambió. No cambia el alcance ni los criterios del epic.

### 2. Contrato

**Superficie CLI:**

```
prepare --project-root R --role <rol> --substage <sub> --objective <texto>      # sin cambios
prepare --project-root R --replace-packet <packet-id> --reason <texto>          # NUEVO sub-modo
prepare --project-root R --replace-packet <packet-id> --reason <texto> \        # correcciones (C2)
    [--input P=P] [--read-scope C[=S]] [--write-scope C[=S]] \
    [--invariant T] [--expected-output T] [--evidence T]
validate-state --project-root R [--execution-context P]                          # idle aceptado
```

**Registros de aprobación (contrato de datos):**

- Aprobación de **spec** (roles de construcción): entrada de `stage_history`
  `{feature, stage: "specification", approved_by: <no vacío>, approved_at?, contract_path: <ruta>, contract_sha256: <64 hex>}`.
  La entrada **habilita solo si su pin NOMBRA el contrato** verificado para el rol:
  `contract_path == contract["path"]` **Y** `contract_sha256 == sha256` verificado
  (C1; PD-18; D3). Una entrada con el `contract_sha256` correcto pero otro
  `contract_path` (o sin `contract_path`) **no autoriza**.
- Aprobación del **plan** (architect): entrada de `epic_history`
  `{epic | epic_id: <epic>, stage: "epic-plan", approved_by: <no vacío>}` (campos extra tolerados; **sin** pin de hash — decisión D2).

**Marcadores de diagnóstico (stderr, rc=2), estables y observables:**

- `approval pending` — falta la aprobación (del plan para architect; de la spec concreta para los demás), o su pin no nombra el contrato.
- `packet obsolete` — el paquete no es reanudable/reemplazable-en-frío sin resolver (contrato o revisión de política cambiados).
- `state incoherent` — el state contradice sus propios registros (binding, feature/epic, idle).

**Postcondiciones (numeradas y verificables):**

**PD-1 (architect habilitado por el plan del epic).** Con epic activo `E` y una entrada de `epic_history` `{epic==E, stage=="epic-plan", approved_by no vacío}`, `prepare --role architect` (cualquier subfase válida) → `rc=0`, publica contexto v2 + paquete, **sin** requerir entrada `specification` de la feature.

**PD-2 (el architect NO se habilita con la aprobación de spec).** Sin la entrada `epic-plan` de `E`, aunque exista una entrada `stage_history` `specification` con `approved_by`, `prepare --role architect` → `rc=2` con marcador `approval pending` que nombra el plan del epic; sin efectos.

**PD-3 (roles de construcción bloqueados sin la spec aprobada).** Sin una entrada `specification` cuyo `contract_path` sea `docs/specs/<feature>/spec.md` **y** cuyo `contract_sha256 == sha256(docs/specs/<feature>/spec.md)`, `prepare --role test-writer|implementer|reviewer` (subfase válida) → `rc=2`, marcador `approval pending`, nombra `stage_history`/`specification`/`approved` y la ruta de la spec; el árbol y el state quedan idénticos (sin publicaciones parciales). *(Ajustada por C1: la ausencia del path registrado cuenta como falta de aprobación.)*

**PD-4 (deriva del contrato invalida la aprobación).** Si la entrada `specification` existe con pin y luego se edita `spec.md` (el sha deja de coincidir), `prepare` para esos roles → `rc=2` `approval pending`, nombrando el digest registrado y el actual.

**PD-5 (aprobación pineada correcta habilita).** Con la entrada del PD-3/PD-4 presente, su `contract_path` coincidente con el contrato verificado y el `contract_sha256` **coincidente** con el archivo, `prepare` para esos roles → `rc=0`. *(Ajustada por C1: el pin habilita solo si nombra el contrato — path y sha.)*

**PD-6 (una entrada rectificada no habilita nada).** Un state cuya única señal es una entrada `{stage: "discovery-authorization", authorized_by, rectified_at}`: `prepare --role architect` → `rc=2` (no es `epic-plan`); `prepare --role test-writer` → `rc=2` (no es `specification`). Es exactamente el caso del `stage_history[161]` real (rectificado el 2026-10-08).

**PD-7 (reemplazo de paquete preparado y no despachado).** Con `active_packet.id == <id>`, `status == "prepared"` y obsolescencia verificada (PD-8), `prepare --replace-packet <id> --reason "<texto>"` → `rc=0`; se publica un **paquete nuevo** (id siguiente libre) con el contrato **actual** y la autorización vigente; `state.active_packet` pasa a apuntar al nuevo con `status: "prepared"`; el `REQUEST.json` y `PACKET.md` del paquete anterior quedan **byte a byte idénticos**; queda un registro durable de superación (`.cdad/packets/<id>/.superseded.json`) con `{superseded_by, reason, superseded_at, contract_sha256_old, contract_sha256_new}` (ampliado por PD-24); **ninguna** entrada de `stage_history`/`epic_history` se crea ni se modifica.

**PD-8 (reemplazo solo ante obsolescencia genuina).** `--replace-packet` es aceptado solo si (a) el `sha256` del contrato registrado en el `REQUEST.json` difiere del actual, **o** (b) la revisión de política del paquete difiere de la aceptada (I11). Si no hay obsolescencia verificable → `rc=2`, sin efectos (no es un atajo para saltar PD-4).

**PD-9 (el reemplazo exige motivo).** `--replace-packet` sin `--reason` no vacío → `rc=2`, sin efectos. `--reason` sin `--replace-packet` → `rc=2`.

**PD-10 (un paquete despachado no se reemplaza).** Con `status == "dispatched"`, `--replace-packet` → `rc=2`, marcador `packet obsolete`, mensaje que nombra la **reconciliación** requerida; sin efectos.

**PD-11 (el reemplazo no inventa autorización).** Si el contrato actual **no** está autorizado (p. ej. la spec cambió y el pin ya no coincide, o su `contract_path` no nombra el contrato), `--replace-packet` → `rc=2` `approval pending`; no se publica paquete nuevo; el paquete viejo queda intacto. *(Recuperación sin inventar evidencia.)*

**PD-12 (diagnósticos distinguibles y accionables).** Para cada condición (aprobación pendiente / paquete obsoleto / estado incoherente) el CLI sale `rc=2` y el stderr contiene el marcador correspondiente (`approval pending`, `packet obsolete`, `state incoherent`), nombra el registro/falta concreto y la acción legítima siguiente; no altera el state ni publica archivos. Los marcadores son mutuamente excluyentes por condición.

**PD-13 (reposo legítimo aceptado).** Con `active_feature == null` y `current_stage == "idle"`, un state que conserva el bloque `execution` de la última feature (y/o un `active_packet` terminal `completed|failed`) → `validate-state` (rc=0) con salida `VALID` que declara el reposo (p. ej. `VALID: idle`).

**PD-14 (state incoherente rechazado).** `active_feature == null` con `current_stage` distinto de `"idle"` → `rc=2` `state incoherent`; y `active_feature` no nulo con `current_stage == "idle"` → `rc=2` `state incoherent`.

**PD-15 (reposo con paquete en vuelo rechazado).** `active_feature == null`, `current_stage == "idle"`, pero `active_packet.status ∈ {prepared, dispatched}` → `rc=2` `state incoherent` (un paquete en vuelo no puede coexistir con el reposo).

**PD-16 (resume de un paquete obsoleto falla con marcador).** `prepare --resume-packet <id>` sobre un paquete cuyo contrato o revisión de política cambió → `rc=2` `packet obsolete`, nombrando el valor registrado y el actual; si `status == prepared`, señala `--replace-packet`; si `dispatched`, señala reconciliación. Se preserva el comportamiento I11 vigente.

**PD-17 (prueba decisiva, un solo escenario secuencial):**
1. Fixture con epic `E` (entrada `epic_history` `stage: epic-plan`, `approved_by`), feature `F`, **sin** spec aprobada. `prepare --role architect --substage discovery` → `rc=0` (discovery autorizado).
2. `prepare --role test-writer --substage red` → `rc=2` `approval pending`; sin paquete en disco (construcción bloqueada).
3. Se crea `docs/specs/F/spec.md` y se registra la aprobación pineada (path+sha). `prepare --role test-writer --substage red` → `rc=0`, paquete P1.
4. Se **edita el plan del epic** (contrato del architect) → el paquete del architect (del paso 1) queda obsoleto. `prepare --resume-packet <architect-id>` → `rc=2` `packet obsolete`.
5. `prepare --replace-packet <architect-id> --reason "plan editado"` → `rc=0`; paquete nuevo con el sha actual del plan; bytes del anterior intactos; `.superseded.json` con el motivo; **sin** cambios en `stage_history`/`epic_history`.
6. Negativo: `--replace-packet` sobre otro paquete **no** obsoleto → `rc=2`, sin efectos.

**Enmienda de PD-17 (2026-10-09).** La letra de PD-17 se enmienda para que coincida
con el recorrido **realmente ejecutado** (autoridad: instrucción del dueño,
`docs/epics/epic-005-real-operation/plan.md`; evidencia: `closure.md:51-57`,
`debt.md:9-18` B2, `dispatch-ledger.md` fila 13): el paquete del **architect** se
**recibe y completa** — `record-dispatch` → staging → `receive` → `validate-receipt`
→ transición — **antes** de preparar al **test-writer**; y el reemplazo se prueba
sobre un paquete **todavía `prepared` y NO despachado** (nunca `dispatched`). Es una
enmienda **documental**: no cambia el alcance ni los criterios del epic. Decisión
sobre el **pin** de aprobación de 005-001: al ser una enmienda documental de una
feature `done`, el orquestador (HITL delegada epic-005) **re-registra** el pin con
los bytes nuevos (`contract_sha256` derivado, PD-4) y **no** habilita ningún paquete
nuevo.

**PD-18 (el pin de la spec debe nombrar el contrato — C1).** Una entrada `specification` habilita a los roles de construcción **solo** si su pin nombra el contrato verificado: `contract_path == contract["path"]` **y** `contract_sha256 == sha256` verificado. Una entrada con el `contract_sha256` correcto pero `contract_path` distinto (o ausente) → `prepare --role test-writer|implementer|reviewer` → `rc=2`, marcador `approval pending`, que nombra el `contract_path` **registrado** y el **esperado**; sin efectos (árbol y state byte a byte idénticos). *Control positivo interno:* la misma entrada con el `contract_path` correcto → `rc=0` (PD-5). Es el caso de una aprobación copiada de otra feature (hash coincidente por casualidad de contenido, ruta ajena) o de una entrada sin pin de ruta.

**PD-19 (conservación del encargo anterior en el reemplazo — C2).** Con `active_packet.id == <id>` `prepared` y obsolescencia verificada (PD-8), `prepare --replace-packet <id> --reason <texto>` **sin** ninguna opción de corrección publica un paquete nuevo cuyo `REQUEST.json` conserva, tal cual, los valores del `REQUEST.json` anterior para: `execution_id`, `role`, `substage`, `objective`, `inputs`, `read_scope`, `write_scope`, `invariants`, `expected_output` y `evidence_required`. La identidad, la subetapa y el objetivo ya se reusaban (D4 previa); ahora también las seis listas/campos del encargo. El contrato se **re-resuelve** al actual (no se conserva) y el paquete se publica solo si la aprobación vigente lo habilita (PD-11). *(Deja de recomputar los valores por defecto.)*

**PD-20 (opciones de corrección, reemplazo de la lista entera y lista vacía — C2).** En el sub-modo `--replace-packet` se admiten, además del selector y `--reason`, exactamente estas opciones de corrección: `--input`, `--read-scope`, `--write-scope`, `--invariant`, `--expected-output`, `--evidence`. Cada una, **si se da**, reemplaza esa lista/campo **entero** (no se agrega a lo conservado). El valor centinela `-` (un único guion), como **único** valor del campo, deja la lista **vacía**; `-` mezclado con otros valores del mismo campo → `rc=2` (ambigüedad), sin efectos. `expected_output` es un escalar: `--expected-output -` lo deja vacío. Dejar una lista vacía está permitido **cuando el resultado sigue siendo un encargo válido** (PD-22): `inputs` vacío es legítimo; `write_scope` vacío es legítimo (p. ej. architect); un `read_scope` vacío es rechazado si deja un `input` fuera de alcance; `invariants`/`evidence_required` nunca quedan por debajo del piso obligatorio del rol (PD-21).

**PD-21 (pisos obligatorios del rol, imposibles de quitar — C2).** `--invariant` reemplaza la lista pero **nunca** elimina los `DEFAULT_INVARIANTS` del rol (se re-agregan): para un rol con invariantes obligatorios, el `invariants` del paquete publicado los contiene siempre, aunque se dé `--invariant -`. `--evidence` reemplaza la lista pero **nunca** elimina la evidencia mínima del rol (`DEFAULT_EVIDENCE`, se re-agrega). Observable en el `REQUEST.json` del paquete nuevo: cada elemento obligatorio del rol está presente. *(Un rol sin invariantes obligatorios — architect — puede quedar con `invariants` vacío.)*

**PD-22 (las correcciones pasan las mismas validaciones — C2).** El paquete corregido pasa las MISMAS validaciones que un `prepare` normal: autorización por rol (PD-1..PD-5, PD-18), scopes contra la política, `inputs` dentro del `read_scope` y campos cerrados (ningún campo fuera del contrato del `REQUEST.json`). Ante una corrección inválida → `rc=2`, **sin publicar nada** y con el paquete anterior **byte a byte intacto**; el stderr nombra el **campo**, el **motivo** y la **opción** para corregirlo (p. ej. un `--read-scope` fuera de la política nombra `read_scope`, el motivo de política y `--read-scope`; un `--input` inexistente nombra `inputs`/`input.path`, el motivo y `--input`). *Control positivo interno:* la misma corrección válida → `rc=0` (PD-19/PD-20).

**PD-23 (argv mezclado en el reemplazo — C2).** `--replace-packet` **no** acepta `--role`, `--substage`, `--objective`, `--new-execution`, `--out-dir`, `--contract-kind`, `--contract-path`, `--plan-version`, `--resume-packet`, `--record-dispatch`, `--attempt-id`, `--reconcile-policy`, `--decision-ref` ni `--propose-policy`: un argv que los combine → `rc=2`, sin efectos (rechazado antes de cualquier lock o escritura). El contrato se **re-resuelve** al actual y se publica solo si la aprobación vigente lo habilita (PD-11 vigente). *Control positivo interno:* `--replace-packet` con las opciones de corrección de PD-20 → `rc=0`.

**PD-24 (traza de conservación/cambio del reemplazo — C2).** El registro durable `.cdad/packets/<id>/.superseded.json` conserva `{superseded_by, reason, superseded_at, contract_sha256_old, contract_sha256_new}` (PD-7) y **agrega** la traza por campo: `conserved_fields` (campos conservados del `REQUEST.json` anterior) y `changed_fields` (campos reemplazados por una opción de corrección), sobre el universo `{execution_id, role, substage, objective, inputs, read_scope, write_scope, invariants, expected_output, evidence_required}`. `conserved_fields` y `changed_fields` son **disjuntos** y su unión es el universo; un campo aparece en `changed_fields` si su valor en el `REQUEST.json` nuevo difiere del anterior, y en `conserved_fields` si es idéntico. Junto con los dos `REQUEST.json` guardados (el anterior y el nuevo), la traza muestra **qué se conservó, qué cambió y por qué** (`reason`).

### 3. Invariantes (verificables)

- **INV-1.** `prepare` (incluido `--replace-packet`) jamás publica un paquete sin que pase la verificación de autorización del rol sobre el contrato del día.
- **INV-2.** Ninguna operación de `prepare`/`--resume-packet`/`--replace-packet` **escribe** aprobaciones (`stage_history`/`epic_history`): el registro de aprobación es del orquestador, no del CLI.
- **INV-3.** El reemplazo nunca borra ni reescribe los bytes del paquete anterior (`REQUEST.json`/`PACKET.md` byte-idénticos).
- **INV-4.** El conjunto y el significado de `active_packet.status` no cambian (`{prepared, dispatched, completed, failed}`).
- **INV-5.** Determinismo: los mismos insumos producen los mismos bytes de paquete (se reusa el pipeline transaccional existente).
- **INV-6.** Ninguna entrada histórica no conforme (rectificada, de otro vocabulario o sin pin) habilita autoridad alguna.
- **INV-7 (C2).** El reemplazo conserva el encargo anterior campo a campo salvo lo que una opción de corrección reemplace explícitamente (PD-19/PD-20); los pisos obligatorios del rol (`DEFAULT_INVARIANTS`, `DEFAULT_EVIDENCE`) nunca se eliminan (PD-21).
- **INV-8 (C1).** Una entrada `specification` cuyo `contract_path` difiere del contrato verificado (o que carece de `contract_path`) no habilita autoridad alguna (PD-18; refuerza INV-6).
- ∀ state con `active_feature == null` ⟺ `current_stage == "idle"` (coherencia de reposo).

### 4. Criterios de aceptación

- [ ] Un test por postcondición (PD-1..PD-24, con PD-17 como prueba decisiva), con control positivo interno donde haya negativo.
- [ ] **Prueba decisiva del plan** (PD-17) verde end-to-end.
- [ ] **Test focal por C1** (PD-18): entrada con `contract_sha256` correcto y `contract_path` distinto → `approval pending` (con control positivo con el path correcto).
- [ ] **Los cinco tests focales de C2** (PD-19..PD-24): conservación sin opciones; rechazo sin efectos ante un insumo inexistente; recuperación con la corrección explícita; rechazo de un alcance fuera de la política; invariantes del rol imposibles de quitar.
- [ ] Suite completa verde (la feature toca el **renderer/CLI** → suite completa al cierre de la feature) y `make validate` sin fallos nuevos al cierre.
- [ ] El paquete del architect se prepara **sin spec aprobada** y el de test-writer queda **bloqueado** hasta la aprobación pineada (evidencia pegada).
- [ ] `validate-state` acepta el reposo y rechaza el incoherente (evidencia pegada).

### 5. Fuera de alcance

- Activar/instalar versiones en el repo real ni cambios en HOME (reservado al dueño).
- Roles en Claude Code (005-004); medición de contexto (005-002); reducción de orientación (005-003).
- El resto de la deuda de 003-007 (`R2-STAGE`, `POLICY-CLASS`, `CKPT-FORK`, …).
- Unificación del vocabulario de `epic_history` de epics históricos; migración de estados de epics cerrados.
- Tests por frases; tests de cobertura no derivados de un PD.
- **La enmienda T-CORR no cambia el alcance ni los criterios del epic**: corrige la forma de la autorización (C1) y del reemplazo (C2) dentro de 005-001; no agrega roles, sub-modos ni contratos nuevos.

### 6. Contexto técnico

- Punto de enforcement: mover la **aprobación de contrato por rol** de `_validate_v2_vigency` (`cdad_packet.py:1324`) a `validate_request` (`:681`, donde se conoce `role` y ya está verificado `contract["sha256"]` contra el archivo en `:750-753`). `_validate_v2_vigency` conserva la **coherencia de estado** (feature/epic/delegación) que exigen los negativos de `validate-state` (`test_004_002_t2_reviewfix.py:215,527`) y PD-1 de `test_004_002_t2_bootstrap.py:329`.
- **C1 (enmienda 2026-10-09).** `_contract_approval_for` (`:1342`) pasa a exigir también que la entrada `specification` **nombre** el contrato: `entry["contract_path"] == contract["path"]` además de `entry["contract_sha256"] == current` (hoy `:1389` compara solo el sha). El diagnóstico de PD-18 nombra el `contract_path` registrado y el esperado; el mensaje conserva los tokens `stage_history|specification|approved` y la ruta de la spec (R2).
- El nuevo sub-modo `--replace-packet` debe declararse en `build_parser` (`:2815-2847`), `_reject_mode_mix` (`:2906-2944`) y `main` (`:2961-2985`), y correr **antes** del bloque PD-4 (`:2498-2516`).
- Reutiliza el pipeline transaccional de `prepare` (`:2608-2789`) para INV-1/INV-3/INV-5.
- **C2 (enmienda 2026-10-09).** `_replace_packet` (`:1758`) deja de recomputar `_default_scopes`/`DEFAULT_INVARIANTS`/`DEFAULT_EXPECTED_OUTPUT`/`DEFAULT_EVIDENCE` (`:1839-1856`) y **conserva** el `REQUEST.json` anterior para `execution_id`, `role`, `substage`, `objective`, `inputs`, `read_scope`, `write_scope`, `invariants`, `expected_output` y `evidence_required`, aplicando encima las opciones de corrección (PD-20/PD-21). El parser suma `--input/--read-scope/--write-scope/--invariant/--expected-output/--evidence` al conjunto admitido del sub-modo replace y `_reject_mode_mix` (`:3250`) los excluye de los demás sub-modos y rechaza el argv mezclado (PD-23). El registro `.superseded.json` (`:1868-1874`) suma `conserved_fields`/`changed_fields` (PD-24). Las correcciones reusan `validate_request` (PD-22) y `_publish_generation` (INV-1/INV-3/INV-5).

### 7. Decisiones resueltas al aprobar (orquestador OpenCode, HITL delegada epic-005)

| Id | Propuesta del architect | Resolución | Rationale |
|---|---|---|---|
| D1 | Fuente de la aprobación del plan para el architect | Entrada de `epic_history` `{epic, stage: "epic-plan", approved_by}` | Existe para epic-005 (`docs/.cdad-state.json:155-162`); el frontmatter del plan no se parsea. Se tolera `epic_id` como alternativa de clave. |
| D2 | ¿Pin de hash de la aprobación del plan? | **No** para el plan; **sí** para la spec | El `plan.md` del epic se editó después de aprobado y la autorización sigue vigente; pinear bloquearía al architect. Asimetría: plan = mandato vivo del epic; spec = contrato congelado de la feature. |
| D3 | Pin obligatorio de la spec | Sí: `contract_path` + `contract_sha256` obligatorios en la entrada `specification` | Sin pin se habilitan atajos (PD-4); la migración de fixtures es mecánica y se declara en el plan (T1). |
| D4 | Semántica de `--replace-packet` | **(Enmendada 2026-10-09, T-CORR.)** **Conserva** el encargo anterior del `REQUEST.json` vigente — identidad (`execution_id`), `role`, `substage`, `objective`, `inputs`, `read_scope`, `write_scope`, `invariants`, `expected_output` y `evidence_required` — y admite, además del selector y `--reason`, las opciones de corrección `--input/--read-scope/--write-scope/--invariant/--expected-output/--evidence` (cada una reemplaza su lista/campo entero; `-` la deja vacía; los pisos obligatorios del rol se mantienen). **No** acepta rol/subetapa/objetivo, ni ejecución (`--new-execution`/`--out-dir`), ni contrato declarado, ni selectores de otros sub-modos. Re-resuelve contrato y política; `--reason` obligatorio. | La versión previa («sin flags ordinarios») impedía corregir el encargo de un paquete obsoleto; la corrección acotada del dueño (2026-10-09) mantiene el encargo atómico pero corregible, sin reabrir la identidad ni el contrato. |
| D5 | Definición de reposo legítimo | `active_feature == null` ⟺ `current_stage == "idle"`; se tolera `execution` remanente y `active_packet` terminal; se rechaza paquete en vuelo | Coincide con `references/state-detection.md:27-30`. El oráculo usa `"idle"` (U1); si el RED revela otro valor real de reposo, se ajusta el test con evidencia. |
| D6 | Alcance del enforcement | `validate-state` valida coherencia de estado; la aprobación de contrato por rol se exige en `prepare`/`validate-request` | Sin rol (`active_packet: null`) no hay contrato que aprobar; la aprobación por rol vive donde hay rol. |
| D7 | Forma de la lista vacía y pisos obligatorios en el reemplazo (C2) | Centinela `-` (único valor del campo) para dejar una lista vacía; `DEFAULT_INVARIANTS`/`DEFAULT_EVIDENCE` del rol se re-agregan siempre; el resultado debe pasar las validaciones de PD-22 | El centinela distingue «opción no dada» (conserva) de «lista vacía» (reemplaza por vacío) con una superficie de caja negra verificable; los pisos obligatorios preservan la disciplina de rol aunque el encargo se corrija. |

### 8. Aprobación

- Aprobador: **orquestador OpenCode** (HITL delegada epic-005, `docs/epics/epic-005-real-operation/execution.md`).
- Fecha: 2026-10-08.
- Registro: `docs/.cdad-state.json` → `stage_history` (entrada `specification` con `contract_path` y `contract_sha256`); evidencia `spec.md` + su sha256. El sha256 del archivo vive en el state y en `dispatch-ledger.md`, no dentro del archivo (no se auto-referencia).
- La severidad de los defectos no se relaja por la delegación (alcance del epic).
- **Enmienda T-CORR (2026-10-09), aprobada.** Instruida por el dueño (`plan.md` del epic, apartado «Cambios al plan», 2026-10-09) y aprobada el 2026-10-09 por el orquestador OpenCode (HITL delegada epic-005). Ajusta PD-3/PD-5, agrega PD-18..PD-24, enmienda D4 y agrega D7. Al cambiar los bytes de `spec.md`, su `contract_sha256` derivó (PD-4) y la aprobación pineada se re-registró en `stage_history` con el sha256 de esta versión; la entrada del 2026-10-08 (que cubría los bytes previos) queda superada y no habilita.
