# Borrador del architect — 003-007 (ronda 1)

Sesión `arch-003-007-a1` (`mofgw/deepseek-v4.1-flash`), texto final transcripto sin cambios por el orquestador.

I have verified the terrain, the two defects, the live state of the existing checkpoints, and the constraints (including that `docs/cdad-policy.json` has a **strictly validated schema**). Here is the complete deliverable.

---

# Discovery — 003-007-living-continuity

**Rol:** cdad-architect (solo lectura). **Rama:** `codex/epic-003-context-efficiency`, HEAD `3237e62`. Nada de lo siguiente modifica el repo; es mapa + decisión + borradores.

## 0. Evidencia verificada en uso real (no asumida)

**T4-REF — vive hoy.** Los dos checkpoints existentes están hoy bloqueados, exactamente por referencias que ya divergieron:

| Ejecución | Referencias divergentes (verificado ahora) |
|---|---|
| `exec-003-004-context-continuity-001` (head `seq 1`, body `58c1df54…`) | `docs/specs/003-004-context-continuity/dispatch-ledger.md`, `…/debt.md` (`CHANGED`) |
| `exec-003-006-runtime-adoption-001` (head `seq 5`, body `74dfa738…`) | `docs/specs/003-006-runtime-adoption/dispatch-ledger.md`, `docs/epics/epic-003-context-efficiency/closure-amendment-draft.md` (`CHANGED`) |

El corte es literal: `skills/cdad-cycle/scripts/cdad_continuity.py:693-709` (`_verify_references`) aborta con `rc≠0` si **cualquier** referencia cambió, y lo invocan `reconcile` (`:831-835`), `resume` (`:1087-1089`) y `trigger` vía `_frozen_budget` (`:950-952`). Evidencia del bloqueo real: `evidence/t4/rotation-1-blocked.md:3-7`.

**T4-CKPT — vive hoy.** Un `checkpoint` con la misma clave que su `begin` cae en el mismo branch que un `begin` divergente (`cadad_continuity.py:557-573`): `_run_write` no distingue el comando (solo lo usa en el mensaje). Evidencia: `evidence/t4/checkpoint-after-ru1-REFUSED.txt:1`.

**Estado real de los stores** (verificado): `exec-003-004` tiene 1 body; `exec-003-006` tiene 5 bodies en 5 claves distintas (su split-brain histórico de `reviewer-review-005` fue retirado por RU-2). Ninguno queda hoy en split-brain.

**Compatibilidad hacia atrás (punto 4):** “seguir siendo legibles” solo puede significar *resumibles*: hoy `resume` ya falla sobre ambos y la causa es T4-REF. La corrección debe hacer que rindan proyección.

## 1. Mapa del terreno (anclas)

- **Cuerpo canónico** `_canonical_body` (`:463-483`): `schema_version, execution_id, packet_id, attempt, goal, authority, decisions, uncertainties, next_action, references[], budget?`. Content-addressed → `continuity/bodies/<body_sha256>.json`; `head.json` es el sobre (`_checkpoint_envelope` `:499-524`).
- **Referencias** hoy: `update.references` es una **lista de strings**; `_digest_references` (`:369-381`) exige existencia y guarda `{path, sha256(file bytes)}`.
- **No-op / conflicto** – `_run_write` (`:533-582`): misma clave + cuerpo idéntico → `no_op` rc 0 sin escribir; misma clave + cuerpo distinto → `split-brain` rc≠0 (todo o nada, RU-2).
- **Split-brain** `_detect_split_brain` (`:715-742`): agrupa bodies por `(execution_id, packet_id, attempt)` y considera split-brain a **>1** body por clave.
- **Cadena/tamper** `_verify_body` (`:647-672`), `_verify_chain` (`:675-690`).
- **Aislamiento de rol** `_visible_references` (`:635-641`) vía `docs/cdad-policy.json` (`path_policy`).
- **Autoridad** `_state_authority` (`:265-306`) lee solo `hitl_delegation` estructurado del state (`docs/.cdad-state.json:1340-1348`).
- **Esquemas**: `continuity-checkpoint.schema.json:52-69` (items `{path,sha256}`, `additionalProperties:false`), `active-record.schema.json`. **No hay validación de esquema en runtime** (deuda R-STR, `003-004/debt.md:24`).
- **Regla a reconciliar**: `sources/roles/orchestrator.md:69-72`.
- **Convención de tests**: focales `env -u TMPDIR python3 -m pytest …` (declarado en los `plan.md` de 003-004/003-006); wrapper `scripts/cdad_continuity.py`.

## 2. Restricción dura descubierta (decide D2)

`docs/cdad-policy.json` **no es extensible en este MVP**: `cdad_packet.py:404-415` valida `set(document) != POLICY_KEYS` (`POLICY_KEYS = {"schema_version","path_policy","temporary_roots"}`, `:117`) y `path_policy` rechaza campos desconocidos (`_validate_policy_path_policy`, `:364-382`). Agregar una sección `continuity` al policy **rompería todo `prepare`/`validate-policy`** (que cargan el policy en cada despacho) o forzaría a tocar el renderer de paquetes — fuera del alcance de una “feature chica”. Por eso la clasificación se declara **en la propia referencia** (opción explícitamente admitida por el encargo, punto 2), no en el policy.

## 3. Decisiones D1..D10 (con VERIFY)

### D1 — Proyección de autoridad de `docs/.cdad-state.json`
El state se referencia con un selector de campos `fields`. El digest cubre **solo la proyección canónica** de esas claves top-level:
- **Autoridad (bloquea):** `hitl_delegation`, `approver`, `execution`.
- **Progreso (informa):** `stage_history`, `epic_features`, `epic_history`, `delegation_history`, `active_packet`, `current_stage`, `postconditions_status`, `audit_status`, `review_status`, `active_feature`, `active_epic`, `epic_stage`, `stack`, `last_updated`.
- **`stage_history` es progreso, no autoridad** (aunque el encargo lo liste): se apendea en cada transición; digerirlo como autoridad recrearía literalmente T4-REF. Las aprobaciones durables viven en el artefacto que aprueban (spec/plan/closure), que son referencias de contrato.
- Proyección: `{k: doc[k] for k in fields if k in doc}` serializado canónico (`json.dumps(sort_keys=True, separators=(",",":"))`). Campo ausente = ausente.

### D2 — Fuente de la clasificación: la referencia (no el CLI)
Cada entrada de `--update.references[]` puede ser un string (compat) o un objeto `{"path", "class"?: "contract"|"living", "fields"?: [str]}`. Precedencia: **clase explícita > contrato**. El CLI **nunca** deriva la clase de la ruta. Se evaluó y descartó la ruta policy por la restricción §2. (Extensión futura: defaults por policy.)
- **VERIFY V1:** ¿el encargo acepta “referencia” como única fuente en este MVP, con policy diferido? (El punto 2 admite “política **o** … referencia”.)

### D3 — Semántica contract/vivo en la lectura
- **contract** + cambio/ausencia → `rc≠0` con `path` y digests exactos (P1, preserva tamper de 003-004).
- **living** + cambio/ausencia → **no bloquea**; el comando emite y reporta por referencia `state: changed|missing` y `current_sha256` (P2).
- La resolución se **congela** en el body al escribir (la clase resuelta se estampa), para que la lectura sea determinista y no dependa de un archivo compartido mutable.

### D4 — Forma de referencia + congelado
Entrada acepta string u objeto; el body guarda `{"path","sha256","class","fields"?}` (la clase siempre estampada en cuerpos nuevos). El modo `fields` solo vale para JSON; en modo archivo el digest es de los bytes.
- **VERIFY V2:** definición canónica de la proyección `fields` (orden, ausencia) — fijar en RED.
- **VERIFY V3:** el esquema `continuity-checkpoint-v1` gana `class`/`fields` opcionales en los items; confirmar que ningún validador valida el esquema en runtime (R-STR) y que `make validate` no lo consume.

### D5 — T4-CKPT: un `checkpoint` es un eslabón, un `begin` duplicado sigue fallando cerrado
- El body de **checkpoint** gana `"record": "checkpoint"`; el body de **begin** queda **byte-idéntico** al actual (BC del no-op `begin`).
- `_run_write`, misma clave: cuerpo idéntico → no-op; `command == "checkpoint"` → **append** (`seq+1`, `prev` = body del head); `command == "begin"` divergente → **fail closed** (despacho duplicado).
- `_detect_split_brain` se redefine: split-brain = **≥2 bodies con `record != "checkpoint"`** (i.e. ≥2 begins/legados) bajo la misma clave. Los checkpoints son eslabones.
- El sobre gana `record` (`begin|checkpoint`) como campo opcional del esquema.
- **Límite residual declarado:** dos checkpoints divergentes bajo la misma clave (restore/concurrencia) ya no se detectan por conteo; sigue siendo “responsabilidad del orquestador” (límite ya declarado en `continuity.md:62-64`). Candidato a deuda.

### D6 — Compatibilidad hacia atrás de los checkpoints existentes (punto 4)
Las referencias **sin `class`** en un cuerpo **legado** se resuelven como **vivas** (informan). Justificación: el punto 4 exige que `resume` no se rompa sobre las dos ejecuciones existentes, y sus referencias **ya divergieron** (evidencia §0). Esto hace que ambas rindan proyección y reporten los documentos vivos cambiados.
- **Contrapartida honesta:** en cuerpos legados la autoridad (spec/plan) también informa en vez de bloquear; es aceptable porque ambas ejecuciones están cerradas, y los checkpoints **nuevos** declaran `contract` explícito (P1 se cumple donde importa).
- **VERIFY V4:** que el orquestador acepte esta resolución para el punto 2 vs punto 4 (es el único puente que satisface ambos).

### D7 — Uso sin reactivar (punto 5)
Tras la review, la versión nueva se instala en una raíz aislada bajo `~/.cache` (`CDAD_INSTALL_ROOT=$HOME/.cache/cdad-adopted-<rev> bash install.sh --optimus`) y se invoca **por ruta explícita** (`<adopted-root>/…/cdad_continuity.py`); no se corre `cdad-activate` sobre el repo. El ledger registra rutas con marcadores `<adopted-root>`/`<project-root>`. Sin escrituras en el HOME real.

### D8 — Documentación de la convención
`skills/cdad-cycle/references/continuity.md` documenta: forma de `--update.references[]`, default `contract`, y la convención recomendada (**contract**: spec/plan aprobados, `docs/cdad-policy.json`, aprobaciones, delegación; **living**: `dispatch-ledger.md`, `debt.md`, `adoption-ledger.md`, `continuity-ledger.md`, Memory Bank, drafts de enmienda/closure).

### D9 — Reconciliación de `sources/roles/orchestrator.md:69-72`
Texto propuesto (reemplaza el paréntesis “one postcondition, one test, one diff; do not group sub-phases”):

> `- State passing: every role session arrives fresh — the packet/handoff`
> `  carries one complete dispatchable unit (one plan task, or one TDD`
> `  sub-phase — never two sub-phases in one invocation) with all the`
> `  postconditions that unit covers, each traced to at least one test, and a`
> `  single bounded, reviewable diff; plus its inputs, strict rules and`
> `  expected format. Never assume the role remembers anything.`

Protege lo que la regla original cuidaba: no se agrupan subfases; cada postcondición del unit queda trazada a ≥1 test; el diff sigue acotado y revisable. Reconciliación con la práctica 003-002..006 (una tarea del plan, un RED y un GREEN).

### D10 — Alcance mínimo y deuda
Entra: clases contract/vivo, `fields`, T4-CKPT, BC, docs, uso sin reactivar. **Deuda priorizada:** defaults por policy (bloqueado por el esquema estricto del policy; requiere coordinar con el renderer), detección de forks de checkpoint, lector de sesiones/medición de contexto.

### VERIFY restantes
- **V5:** headroom de `--max-bytes` (16 KiB) con `record`+`class` añadidos a un update realista.
- **V6:** que el gate de tests quede nombrado por tarea (focales + módulos tocados; suite completa en T4 por tocar staging/renderer vía `make agents`).
- **V7:** que la verificación de bloqueo (edición de la spec aprobada) se haga **sin editar la spec del repo** (proyecto sintético en focal y/o copia controlada bajo la raíz aislada).
- **V8:** confirmar que no hay otros consumidores del shape `references[]` fuera de `cdad_continuity.py` (grep hecho: solo ese CLI).

## 4. Gate 1→2 (Discovery)
- [x] APIs/hooks identificados sin “creo que existe”: todo citado `file:line`.
- [x] Cero supuestos pendientes del tipo “quizá X”: la ambigüedad policy-vs-referencia se resolvió con evidencia (`cdad_packet.py:404-415`) y los puntos 1–5 quedaron como D1..D7.
- [x] Frontera de compatibilidad medida contra los stores reales.
- [ ] Aprobación del usuario/orquestador de las decisiones (no delegable al architect).

---

# Borrador `spec.md`

```markdown
---
feature_id: 003-007-living-continuity
feature_name: Continuidad que tolera documentos vivos
created_at: 2026-10-08
status: draft
approved_by: null
approved_at: null
---

# Spec: Continuidad que tolera documentos vivos (003-007)

> **Borrador del architect** (solo lectura; el orquestador materializa y el
> usuario aprueba). Deriva del encargo
> `handoff-architect-001.md` y de los hallazgos T4-REF / T4-CKPT de 003-006
> (`003-006/debt.md:17-18`). Las decisiones D1–D10 están abajo; el architect
> no aprueba su propia propuesta (ADR-003).

## 1. Descripción funcional

Permitir que `cdad_continuity` **tolere la evolución normal del trabajo**: un
orquestador que trabaja horas escribe ledgers, deuda y Memory Bank después de
cada checkpoint, y eso no debe impedir reanudar. Hoy sí lo impide
(T4-REF, deuda alta de 003-006) y un checkpoint de límite se confunde con un
`begin` duplicado (T4-CKPT). Se distinguen dos clases de referencia:

- **contrato/autoridad** (spec y plan aprobados, `docs/cdad-policy.json`,
  aprobaciones, delegación HITL): si cambia, la acción **se detiene** (fail
  closed);
- **documento vivo** (ledgers, `debt.md`, Memory Bank, adoption/continuity
  ledgers, drafts): si cambia, **se informa** como progreso y se reconcilia;
  **no** bloquea.

Se preserva la integridad que protege la evidencia y se distingue qué cambio
invalida una evidencia de cuál representa progreso. No se redefinen estado
(001), receipts (002) ni eventos/presupuesto (003).

## 2. Casos cubiertos y límites de observación

| Caso | Señal real (anclada) | Decisión |
|---|---|---|
| Ledger/deuda cambia tras el último checkpoint | digest de una referencia `living` vs. el congelado | Informar `changed`; `resume`/`reconcile`/`trigger` continúan |
| Spec/plan aprobado cambia | digest de una referencia `contract` | `rc≠0` con path y delta exacto |
| `docs/.cdad-state.json` cambia en progreso (`stage_history`, `active_packet`, …) | proyección `fields` = solo autoridad | No bloquea |
| `docs/.cdad-state.json` cambia en autoridad (`hitl_delegation`, `approver`, `execution`) | proyección `fields` | `rc≠0` |
| `checkpoint` de límite con la clave de su `begin` | `record` del body + cadena `seq`/`prev` | **Eslabón nuevo** de la cadena |
| `begin` divergente con la misma clave | `record=begin` + digest distinto | **Fail closed** (despacho duplicado) |
| Checkpoint existente pre-003-007 | body sin `record`/`class` | Referencias = vivas (informa); `resume` rinde |

**Sin señal fiable:** lo desconocido queda desconocido; no se fabrican digests
ni límites. Sin servicio, sin agente permanente, sin controlador LLM.

## 3. Contrato

### Superficie (misma firma; V6 de 003-004 se mantiene)

```text
begin      --project-root ROOT --execution-context EXEC.json --update UPDATE.json [--max-bytes N] [--json]
checkpoint --project-root ROOT --execution-context EXEC.json --update UPDATE.json [--max-bytes N] [--json]
reconcile  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID [--json]
resume     --project-root ROOT --execution-context EXEC.json [--role ROLE] [--max-bytes N] [--json]
trigger    --project-root ROOT --execution-context EXEC.json --packet PACKET_ID [--runtime opencode] [--json]
```

### `--update.references[]` (extiende; ver D2/D4)

Acepta un string (compat, `class` = `contract`) o un objeto:

```json
{"path": "docs/specs/003-007-living-continuity/debt.md", "class": "living"}
{"path": "docs/.cdad-state.json",
 "class": "contract",
 "fields": ["hitl_delegation", "approver", "execution"]}
```

- `class` ∈ {`contract`, `living`}; ausente/desconocido → `contract` (falla cerrado).
- `fields` (opcional): subconjunto de claves top-level de un JSON; el digest cubre
  la proyección canónica.
- El CLI **no** clasifica por ruta.
- La clase resuelta se **estampa** en el body: `{"path","sha256","class","fields"?}`.

### Envolventes

- Checkpoint (`continuity-checkpoint-v1`): gana `record` (`begin`|`checkpoint`, opcional en el esquema; los escritores nuevos lo emiten).
- `resume`/`reconcile`/`trigger`: cada referencia visible se reporta como
  `{"path","class","sha256","current_sha256","state"}` con `state` ∈
  `unchanged|changed|missing` (`legacy: true` cuando la clase provino de un cuerpo legado).

### Postcondiciones

- **P1 (contrato bloquea).** `resume`/`reconcile`/`trigger` verifican cada
  referencia `contract` (digest de bytes o proyección `fields`). Cambio o
  ausencia → `rc≠0` citando `path` y los digests esperado/real; sin proyección.
- **P2 (vivo informa, no bloquea).** Una referencia `living` cambiada o ausente
  **no** bloquea: los tres comandos rinden y reportan `state: changed|missing` y
  `current_sha256`.
- **P3 (fuente de clase y default cerrado).** La clase viene de la declaración
  de la referencia; sin clase reconocible → `contract` (falla cerrado). El CLI
  no deriva la clase de rutas.
- **P4 (proyección de autoridad del state).** Con `fields`, el digest cubre solo
  la proyección canónica de esas claves; el resto del state (progreso) no afecta
  la integridad. Subconjunto recomendado: `hitl_delegation`, `approver`,
  `execution`. Sin `fields` → digest de archivo completo.
- **P5 (checkpoint ≠ begin, T4-CKPT).** Un `checkpoint` con la clave del head se
  **apendea** como eslabón nuevo (`seq+1`, `prev_checkpoint_sha256` = body del
  head), no se rechaza como split-brain. Un `begin` divergente con la misma clave
  sigue fallando cerrado.
- **P6 (integridad de cadena y tamper preservados).** `record` viaja en el body
  (checkpoint) y en el sobre; un `checkpoint` re-ejecutado con cuerpo idéntico es
  no-op; `seq`/`prev`/`body_sha256` y los negativos de tamper no cambian.
- **P7 (compatibilidad hacia atrás).** Los checkpoints pre-003-007 siguen siendo
  legibles: sus referencias se leen como vivas, de modo que un documento vivo
  divergido no vuelve irresumible la ejecución; `resume` sobre
  `exec-003-004-context-continuity-001` y `exec-003-006-runtime-adoption-001`
  rinde proyección y reporta los vivos cambiados.
- **P8 (aislamiento de rol preservado).** `resume --role` sigue filtrando
  referencias de implementación; los campos nuevos no filtran material de
  implementación.
- **P9 (aceptación con rotación real).** Dentro de 003-007, tras el último
  checkpoint de un paquete se escribe en un documento vivo → `resume` tiene
  **éxito** y reporta el/los documentos vivos cambiados; una edición deliberada
  de una referencia `contract` (spec aprobada) **bloquea** (`rc≠0`), verificado
  sin editar la spec aprobada del repo. La versión nueva se invoca desde una raíz
  aislada por ruta explícita, sin reactivar el repo.
- **P10 (regla reconciliada).** `sources/roles/orchestrator.md` expresa el
  encargo como **una unidad despachable** (una tarea del plan o una subfase TDD,
  sin agrupar subfases) con sus postcondiciones, cada una trazada a ≥1 test y un
  único diff acotado y revisable; los agentes regenerados reflejan el texto.

## 4. Invariantes verificables

1. El CLI es determinista y read-only sobre el producto salvo
   `.cdad/executions/<id>/continuity/**`; el orquestador es el único escritor de
   `docs/.cdad-state.json`; el CLI nunca aprueba.
2. Desconocido permanece desconocido; bytes ≠ tokens; no se fabrica límite.
3. **No hay clasificación por rutas fijas dentro del CLI** (D2); la clase viene
   de la referencia (o, a futuro, del policy).
4. Deriva `contract` siempre falla cerrado; deriva `living` **nunca** bloquea en
   silencio: siempre se reporta.
5. Los checkpoints pre-003-007 permanecen legibles.
6. Sin servicio, sin agente permanente, sin controlador LLM; sin cambio de
   permisos.
7. Las restricciones por rol sobreviven a checkpoint/repackage.

## 5. Criterios de aceptación

1. P1–P10 verificadas por tests focales, cada test mapeado a su postcondición.
2. Referencia `contract` cambiada → `rc≠0` con delta (focal, proyecto sintético);
   referencia `living` cambiada → `rc 0` y `state: changed`.
3. `docs/.cdad-state.json`: cambio en `stage_history`/`active_packet` no bloquea;
   cambio en `hitl_delegation`/`approver`/`execution` bloquea.
4. `checkpoint` con la clave del `begin` → eslabón nuevo (`seq+1`, `prev`);
   `begin` divergente con la misma clave → conflicto/escalado sin sobrescribir.
5. `resume` sobre `exec-003-004-context-continuity-001` y
   `exec-003-006-runtime-adoption-001` rinde proyección y reporta los vivos
   cambiados (compatibilidad punto 4).
6. `resume --role test-writer` no expone `implementation_roots`.
7. Rotación real dentro de 003-007 registrada en
   `docs/specs/003-007-living-continuity/continuity-ledger.md`, con instalación
   por ruta explícita desde raíz aislada y **sin reactivar** el repo.
8. Regla de encargo reconciliada en `sources/roles/orchestrator.md` y agentes
   regenerados (`make agents`), con test de coherencia.
9. Sin regresiones en `tests/test_003_004_*` y `tests/test_003_006_t4_*`;
   validadores del repo sin regresiones (F011 y A3 son deuda preexistente).
10. Cero afirmaciones de ahorro no medido; tokens/contexto ausentes quedan `null`.

## 6. Fuera de alcance

- Defaults de clase por policy (bloqueado por el esquema estricto de
  `docs/cdad-policy.json`, `cdad_packet.py:404-415`); requiere coordinación con el
  renderer → deuda.
- Detección de forks de checkpoint (dos checkpoints divergentes bajo la misma
  clave); sigue siendo responsabilidad del orquestador.
- Lector de sesiones por runtime, medición de contexto, CI, caché universal de
  evidencia, benchmark.
- Cambiar permisos, autoridad o política; nuevo epic de seguridad.

## 7. Contexto técnico (anclas)

- `skills/cdad-cycle/scripts/cdad_continuity.py:369-381,463-483,499-573,693-742,824-888,943-954,1053-1118`.
- `skills/cdad-cycle/references/continuity.md` (se extiende).
- `skills/cdad-cycle/assets/continuity-checkpoint.schema.json:52-69`.
- `docs/.cdad-state.json:1339-1408` (`approver`, `hitl_delegation`, `execution`).
- `sources/roles/orchestrator.md:69-72`.
- `docs/specs/003-006-runtime-adoption/debt.md:17-18`; `evidence/t4/rotation-1-blocked.md:3-7`, `checkpoint-after-ru1-REFUSED.txt:1`.
- Stores reales: `.cdad/executions/{exec-003-004-context-continuity-001,exec-003-006-runtime-adoption-001}/continuity/`.

## 8. Decisiones (D1–D10) y VERIFY

Resueltas por el arquitecto como propuesta; **el orquestador las adopta/corrige
bajo la delegación HITL**:

| ID | Decisión |
|---|---|
| D1 | State con proyección `fields`; autoridad = `hitl_delegation`+`approver`+`execution`; `stage_history` es progreso |
| D2 | Clase declarada en la referencia (no en el CLI); policy descartado por esquema estricto (`cdad_packet.py:404-415`) |
| D3 | `contract` cambia → `rc≠0`; `living` cambia → informa con `state`/`current_sha256` |
| D4 | `references[]` acepta string u objeto; modo `fields` para JSON; clase resuelta congelada en el body |
| D5 | Body de checkpoint gana `record`; mismo-`begin`-clave divergente sigue cerrado; begin byte-idéntico (BC no-op) |
| D6 | Split-brain = ≥2 bodies con `record != "checkpoint"` por clave; fork de checkpoints = límite declarado |
| D7 | Legado (sin `class`) → referencias vivas; hace resumibles las dos ejecuciones existentes |
| D8 | Uso sin reactivar: raíz aislada + ruta explícita; ledger con marcadores |
| D9 | `continuity.md` documenta forma y convención de clases |
| D10 | Texto reconciliado de `orchestrator.md:69-72` (D9 del discovery) |

**VERIFY:** V1 aceptación de “referencia” como fuente (punto 2); V2 canonicalización
de `fields`; V3 esquema sin validación en runtime (R-STR); V4 resolución legado-vivo
(punto 2 vs 4); V5 headroom 16 KiB; V6 focales/gate por tarea; V7 bloqueo verificado
sin editar la spec real; V8 no hay otros consumidores de `references[]`.

---

Status: draft (pendiente de aprobación del orquestador/usuario).
```

---

# Borrador `plan.md`

```markdown
---
feature_id: 003-007-living-continuity
feature_name: Continuidad que tolera documentos vivos
created_at: 2026-10-08
status: draft
approved_by: null
approved_at: null
---

# Plan — 003-007-living-continuity (borrador)

> Borrador del architect. 4 tareas (máximo del encargo). La **última** tarea es
> la reconciliación de `sources/roles/orchestrator.md:70`, separada porque
> regenera agentes (`make agents`). El plan define el contrato, nunca el código.
> Gate de tests vigente (2026-10-08): el implementer corre **focales + tests de
> los módulos tocados**; suite completa al cierre o si toca instalador/staging/
> renderer. Focales nombrados por tarea.

## Restricciones globales (copia de la spec)

- Repo en español. Tooling Python **stdlib-only**.
- Nunca instalar/modificar CDAD en el HOME real; raíces aisladas bajo `~/.cache`.
- Sin push automático. Ledger y docs nuevos **sin rutas absolutas** (marcadores
  `<adopted-root>`/`<project-root>`).
- No endurecer permisos; sin CLI nuevo; reutilizar `cdad_continuity.py`.
- No tocar `docs/cdad-policy.json` (esquema estricto, `cdad_packet.py:404-415`).

## 1. Tareas

### T1 — Clases de referencia (contrato/vivo) + proyección de autoridad del state + compatibilidad
- **Postcondiciones:** P1, P2, P3, P4, P7, P8.
- **Alcance incluido:** `--update.references[]` acepta string u objeto
  (`class`, `fields`); modo `fields` para JSON; el digest de `contract` bloquea y
  el de `living` informa (`state`/`current_sha256` en el sobre de
  `resume`/`reconcile`/`trigger`); clase resuelta congelada en el body; lectura
  legacy (sin `class`) como viva; filtro de rol intacto. Documentar la forma y la
  convención de clases en `continuity.md`.
- **Excluido:** T4-CKPT (T2); default por policy (deuda).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Modify `skills/cdad-cycle/assets/continuity-checkpoint.schema.json`;
  Modify `skills/cdad-cycle/references/continuity.md`;
  Create `tests/test_003_007_t1_reference_classes.py`.
- **Focales:** `tests/test_003_007_t1_reference_classes.py`,
  `tests/test_003_004_t1_resume.py`, `tests/test_003_004_t1_checkpoint.py`,
  `tests/test_003_004_t4_real_context.py`.
- **Validación:** `contract` cambiada → `rc≠0`; `living` cambiada → `rc 0` con
  `state: changed`; cambio de `stage_history` no bloquea y de `hitl_delegation`
  bloquea; `resume --role test-writer` sin implementación; `resume` rinde sobre
  las dos ejecuciones existentes.
- **Detener si:** V2 (canonicalización de `fields`) no se fija sin ambigüedad.
- **Owner:** RED test-writer; GREEN implementer.

### T2 — T4-CKPT: `checkpoint` distinto de `begin`
- **Postcondiciones:** P5, P6.
- **Alcance incluido:** `record` en el body de checkpoint (begin byte-idéntico);
  mismo-`begin`-clave divergente sigue cerrado; `checkpoint` con la clave del head
  apendea eslabón (`seq+1`, `prev`); `record` en el sobre; `_detect_split_brain`
  redefinido (≥2 begins por clave). Actualizar `continuity.md`.
- **Excluido:** detección de forks de checkpoint (deuda).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Modify `skills/cdad-cycle/assets/continuity-checkpoint.schema.json`;
  Modify `skills/cdad-cycle/references/continuity.md`;
  Create `tests/test_003_007_t2_checkpoint_vs_begin.py`.
- **Dependencias:** T1 (mismo archivo; evita conflicto).
- **Focales:** `tests/test_003_007_t2_checkpoint_vs_begin.py`,
  `tests/test_003_004_t2_writeahead.py`,
  `tests/test_003_006_t4_ru2_refused_write.py`.
- **Validación:** checkpoint mismo-key → `seq+1` con `prev` correcto; begin
  divergente mismo-key → `rc≠0`; checkpoint idéntico re-ejecutado → no-op;
  split-brain para dos begins.
- **Owner:** RED test-writer; GREEN implementer.

### T3 — Aceptación: rotación real dentro de 003-007
- **Postcondición:** P9.
- **Alcance incluido:** instalar la versión nueva en una raíz aislada
  (`~/.cache`) e invocarla por ruta explícita, **sin reactivar** el repo
  (D7/D8); tras el último checkpoint de un paquete, escribir en un documento vivo
  (ledger/deuda) → `resume` **rinde** y reporta los vivos cambiados; verificar el
  bloqueo de una referencia `contract` (spec aprobada) sin editar la spec del repo
  (proyecto sintético en T1 y/o copia controlada). Registrar en el ledger.
- **Excluido:** editar la spec aprobada; benchmark.
- **Archivos:** Create `docs/specs/003-007-living-continuity/continuity-ledger.md`;
  Modify `docs/specs/003-007-living-continuity/dispatch-ledger.md`.
- **Registro obligatorio:** `situación | evidencia (file:line) | decisión |
  autoridad vigente | presupuesto (intentos/contexto o null) | falsas alarmas |
  retrabajo | pendiente`, con rutas en marcadores.
- **Observable:** `resume` sobre la ejecución real de 003-007 rinde y lista los
  vivos `changed`; bloqueo `contract` reproducido (copia); sin reactivación.
- **Dependencias:** T1, T2 verdes.
- **Owner:** orquestador.

### T4 — Reconciliación de la regla de encargo atómico (última, separada)
- **Postcondición:** P10.
- **Alcance incluido:** reemplazar el paréntesis “one postcondition, one test,
  one diff; do not group sub-phases” de `sources/roles/orchestrator.md:69-72` por
  el texto de D9; regenerar `agents/` (`make agents`).
- **Excluido:** cualquier cambio de código del CLI.
- **Archivos:** Modify `sources/roles/orchestrator.md`;
  Regenerate `agents/cdad-orchestrator.md`,
  `agents/claude-code/cdad-orchestrator.md` (`make agents`);
  Create `tests/test_003_007_t4_atomic_unit_rule.py`.
- **Focales:** `tests/test_003_007_t4_atomic_unit_rule.py`,
  `tests/test_003_006_t3_receive_wiring.py`.
- **Regresión / gate:** `tests/validate-consistency.sh`; **suite completa** (toca
  staging/renderer vía `make agents`).
- **Validación:** el agente regenerado expresa la unidad despachable, la
  trazabilidad test↔postcondición y el diff acotado; `make agents` determinista
  (sin diff inesperado).
- **Owner:** RED test-writer; GREEN implementer.

## 2. Cobertura spec↔plan

P1,P2,P3,P4,P7,P8→T1; P5,P6→T2; P9→T3; P10→T4. Ninguna P sin tarea; ninguna
tarea sin P.

## 3. Estimaciones (rango, método, incertidumbre)

- Rango: **medio** (T1), **bajo–medio** (T2), **bajo** (T3, T4). Método:
  comparación cualitativa con 003-004. Incertidumbre **media** por V1–V4
  (resolución legado-vivo y canonicalización de `fields`).

## 4. Integración final

1. Suite completa del repo + validadores (sin regresiones; F011 y A3 deuda
   preexistente declarada).
2. Rotación real registrada en `continuity-ledger.md`.
3. Spec y plan revisados juntos por sesión independiente antes de aprobar.

```plan-tasks
{
  "validation_strategy": "focales por unidad (pytest, env -u TMPDIR) con proyectos sintéticos deterministas; módulos tocados (test_003_004_*, test_003_006_t4_*) en cada tarea; suite completa y validadores al cierre y en T4 (make agents toca staging/renderer); aceptación real en raíz aislada invocada por ruta explícita, sin reactivar el repo ni editar la spec aprobada; ledger anonimizado",
  "tasks": [
    {"id": "T1", "produce": [{"artifact": "cdad-continuity-reference-classes", "contract": "continuity-checkpoint-v1"}], "consume": [], "depends_on": [], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "skills/cdad-cycle/assets/continuity-checkpoint.schema.json", "skills/cdad-cycle/references/continuity.md", "tests/test_003_007_t1_reference_classes.py"], "focal_tests": ["tests/test_003_007_t1_reference_classes.py", "tests/test_003_004_t1_resume.py", "tests/test_003_004_t1_checkpoint.py", "tests/test_003_004_t4_real_context.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T2", "produce": [{"artifact": "cdad-continuity-checkpoint-record", "contract": "continuity-checkpoint-v1"}], "consume": [{"artifact": "cdad-continuity-reference-classes", "contract": "continuity-checkpoint-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "skills/cdad-cycle/assets/continuity-checkpoint.schema.json", "skills/cdad-cycle/references/continuity.md", "tests/test_003_007_t2_checkpoint_vs_begin.py"], "focal_tests": ["tests/test_003_007_t2_checkpoint_vs_begin.py", "tests/test_003_004_t2_writeahead.py", "tests/test_003_006_t4_ru2_refused_write.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T3", "produce": [{"artifact": "continuity-ledger-003-007", "contract": "n/a"}], "consume": [{"artifact": "cdad-continuity-reference-classes", "contract": "continuity-checkpoint-v1", "producer": "T1"}, {"artifact": "cdad-continuity-checkpoint-record", "contract": "continuity-checkpoint-v1", "producer": "T2"}], "depends_on": ["T1", "T2"], "parallel": [], "files": ["docs/specs/003-007-living-continuity/continuity-ledger.md", "docs/specs/003-007-living-continuity/dispatch-ledger.md"], "observable_checks": ["una rotacion real dentro de 003-007 con escrituras de ledger posteriores al ultimo checkpoint: resume rinde y reporta los documentos vivos cambiados", "una edicion deliberada de la spec aprobada (contrato) bloquea, verificado sin editar la spec del repo", "la version nueva se invoca por ruta explicita desde una raiz aislada bajo ~/.cache sin reactivar el repo", "resume sobre exec-003-004-context-continuity-001 y exec-003-006-runtime-adoption-001 rinde proyeccion"], "regressions": ["tests/validate-consistency.sh", "tests/validate-odoo-specialization.sh"], "integration_gate": "@validation_strategy", "owner": "orquestador"},
    {"id": "T4", "produce": [{"artifact": "regla-encargo-atomico", "contract": "n/a (reglas operativas)"}, {"artifact": "agentes-regenerados", "contract": "n/a (salidas generadas)"}], "consume": [], "depends_on": ["T3"], "parallel": [], "files": ["sources/roles/orchestrator.md", "agents/cdad-orchestrator.md", "agents/claude-code/cdad-orchestrator.md", "tests/test_003_007_t4_atomic_unit_rule.py"], "focal_tests": ["tests/test_003_007_t4_atomic_unit_rule.py", "tests/test_003_006_t3_receive_wiring.py"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"}
  ]
}
```

---

Status: draft (pendiente de aprobación del orquestador/usuario).
```

---

## Notas de cierre para el orquestador

1. **Lo más importante a validar antes de aprobar:** D7 (legado→vivo) es el único puente que satisface a la vez el punto 2 (no clasificado = contrato) y el punto 4 (`resume` no se rompe sobre los dos checkpoints existentes, cuyas referencias **ya** divergieron — evidencia dura en §0). Si el orquestador prefiere estricto (legado = contrato), el punto 4 queda sin cumplir y hay que reacotarlo con el dueño.
2. **Descarté la ruta “policy”** por una razón verificada, no por preferencia: `docs/cdad-policy.json` falla cerrado ante campos desconocidos (`cdad_packet.py:404-415` y `path_policy` en `:364-382`). Usarla exigiría tocar el renderer de paquetes (fuera de una feature chica) → deuda priorizada.
3. **P9 necesita T1+T2 instalados** en la raíz aislada; por eso T3 depende de ambos. T4 va separada y última porque `make agents` toca staging/renderer (dispara gate de suite completa).
4. No escribí nada: todo lo anterior es borrador de texto para que el orquestador materialice `docs/specs/003-007-living-continuity/{spec,plan}.md`.
