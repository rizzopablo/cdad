# Borrador del architect — 003-007 (ronda 2)

Sesión resume `arch-003-007-a2` (`<ses-264>`, `mofgw/deepseek-v4.1-flash`), texto final transcripto sin cambios. La spec y el plan aprobados son las dos piezas de este texto.

Read both files and HEAD confirmed (`e8775e9`). Applying every accepted disposition — BL-1, BL-2, BL-3, R-1 (comparison bridge, replacing the blanket), R-2 (debt), R-3, R-4, and the `reconcile`-after-append abstention; R-5 rejected (keep `--optimus`). Here are the complete final drafts.

---

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

> **Borrador (ronda 2)** derivado de `architect-draft-001.md` aplicando
> `review-draft-001.md` con la disposición `review-draft-001-decision.md`
> (BL-1, BL-2, BL-3; R-1 aceptado y reemplaza el puente blanket de legado; R-2
> a deuda; R-3, R-4 aceptados; R-5 rechazado; abstención de `reconcile`
> aceptada). El orquestador materializa y el usuario aprueba; el architect no
> aprueba su propia propuesta (ADR-003). Las decisiones D1–D10 están abajo.

## 1. Descripción funcional

Permitir que `cdad_continuity` **tolere la evolución normal del trabajo**: un
orquestador que trabaja horas escribe ledgers, deuda y Memory Bank después de
cada checkpoint, y eso no debe impedir reanudar. Hoy sí lo impide
(T4-REF, deuda alta de 003-006) y un checkpoint de límite se confunde con un
`begin` duplicado (T4-CKPT). Se distinguen dos clases de referencia:

- **contrato/autoridad** (spec y plan aprobados, `docs/cdad-policy.json`,
  aprobaciones, delegación HITL, state con proyección de autoridad): si cambia,
  la acción **se detiene** (fail closed);
- **documento vivo** (ledgers, `debt.md`, Memory Bank, adoption/continuity
  ledgers, borradores de cierre/enmienda): si cambia, **se informa** como
  progreso y se reconcilia; **no** bloquea.

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
| Checkpoint existente pre-003-007 | body sin `record`/`class` | Resolución **por comparación** (D6): intacto → verificado `contract`; divergido → `changed` con `legacy: true`, no bloquea |

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

### `--update.references[]` (extiende; ver D2/D4/BL-3)

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
  `{"path","class","sha256","current_sha256","state","legacy"?}` con `state` ∈
  `unchanged|changed|missing`; `legacy: true` cuando la clase provino de un cuerpo
  legado resuelto por comparación (D6).

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
- **P4 (proyección de autoridad del state; modos de fallo cerrados — BL-3).**
  Con `fields`, el digest cubre solo la proyección canónica de esas claves; el
  resto del state (progreso) no afecta la integridad. Subconjunto recomendado:
  `hitl_delegation`, `approver`, `execution`. Sin `fields` → digest de archivo
  completo. **`fields` sobre un archivo no-JSON → `rc≠0` al escribir** (el
  digest se congela en el body: la validación es de tiempo de escritura).
  **`fields` que no resuelve ninguna clave (proyección vacía) → `rc≠0` al
  escribir**; nunca un digest constante que dé cero integridad en silencio.
- **P5 (checkpoint ≠ begin, T4-CKPT).** Un `checkpoint` con la clave del head se
  **apendea** como eslabón nuevo (`seq+1`, `prev_checkpoint_sha256` = body del
  head), no se rechaza como split-brain. Un `begin` divergente con la misma clave
  sigue fallando cerrado (despacho duplicado). La faceta `begin` del contrato
  RU-2 permanece intacta; sólo cambia la semántica de rechazo del `checkpoint`.
- **P6 (integridad de cadena y tamper preservados).** `record` viaja en el body
  (checkpoint) y en el sobre; un `checkpoint` re-ejecutado con cuerpo idéntico es
  no-op; `seq`/`prev`/`body_sha256` y los negativos de tamper no cambian.
  `_detect_split_brain` sigue detectando **≥2 bodies con `record != "checkpoint"`
  por clave** (begins/legados divergentes, p. ej. huérfanos pre-RU-2).
- **P7 (compatibilidad hacia atrás por comparación — R-1).** Los checkpoints
  pre-003-007 siguen siendo legibles. Una referencia **sin `class`** en un cuerpo
  legado se resuelve en lectura **por comparación**: digest actual igual al
  congelado → se verifica como `contract` (su integridad se afirma); digest
  distinto o ausente → se reporta `changed`/`missing` con `legacy: true` y **no
  bloquea**. Satisface el punto 4 hoy (en ambas ejecuciones sólo divergen
  ledgers/drafts; specs y planes congelados están intactos) y deja visible
  cualquier deriva futura de una spec "cerrada". Excepción documentada: la clase
  de legado **no está congelada** (se deriva del estado actual del archivo).
- **P8 (aislamiento de rol preservado).** `resume --role` sigue filtrando
  referencias de implementación; los campos nuevos no filtran material de
  implementación.
- **P9 (aceptación con rotación real).** Dentro de 003-007, tras el último
  checkpoint de un paquete se escribe en un documento vivo → `resume` tiene
  **éxito** y reporta el/los documentos vivos cambiados; una edición deliberada
  de una referencia `contract` (spec aprobada) **bloquea** (`rc≠0`), verificado
  sin editar la spec aprobada del repo. La versión nueva se invoca desde una raíz
  aislada por ruta explícita, sin reactivar el repo. La verificación sobre los
  **stores reales** de `exec-003-004-context-continuity-001` y
  `exec-003-006-runtime-adoption-001` vive aquí como observable (no como fixture;
  R-3).
- **P10 (regla de encargo reconciliada y declaración de clases en el orquestador).**
  `sources/roles/orchestrator.md` expresa el encargo como **una unidad
  despachable** (una tarea del plan o una subfase TDD, sin agrupar subfases), con
  sus postcondiciones, cada una trazada a ≥1 test y un único diff acotado y
  revisable; el texto aclara que **una tarea del plan cuyos RED y GREEN son
  despachos separados satisface la regla** (R-4). Además, el bloque "Continuity
  wiring" declara explícitamente qué referencias son `living` (ledgers,
  `debt.md`, Memory Bank, borradores de cierre/enmienda) y qué `contract`
  (spec/plan aprobados, `docs/cdad-policy.json`, state con `fields` de autoridad)
  — o un puntero estricto a la sección correspondiente de `continuity.md` (BL-1).
  Los agentes regenerados reflejan ambos textos.

## 4. Invariantes verificables

1. El CLI es determinista y read-only sobre el producto salvo
   `.cdad/executions/<id>/continuity/**`; el orquestador es el único escritor de
   `docs/.cdad-state.json`; el CLI nunca aprueba.
2. Desconocido permanece desconocido; bytes ≠ tokens; no se fabrica límite.
3. **No hay clasificación por rutas fijas dentro del CLI** (D2); la clase viene
   de la referencia (o, a futuro, del policy).
4. Deriva `contract` siempre falla cerrado; deriva `living` **nunca** bloquea en
   silencio: siempre se reporta. Un `fields` que no protege nada es un error de
   escritura, no un chequeo silencioso (P4/BL-3).
5. Los checkpoints pre-003-007 permanecen legibles (resolución por comparación).
6. Sin servicio, sin agente permanente, sin controlador LLM; sin cambio de
   permisos.
7. Las restricciones por rol sobreviven a checkpoint/repackage.

## 5. Criterios de aceptación

1. P1–P10 verificadas por tests focales, cada test mapeado a su postcondición.
2. Referencia `contract` cambiada → `rc≠0` con delta (focal, proyecto sintético);
   referencia `living` cambiada → `rc 0` y `state: changed`.
3. `docs/.cdad-state.json`: cambio en `stage_history`/`active_packet` no bloquea;
   cambio en `hitl_delegation`/`approver`/`execution` bloquea.
4. `fields` sobre no-JSON → `rc≠0` al escribir; `fields` con proyección vacía →
   `rc≠0` al escribir.
5. `checkpoint` con la clave del `begin` → eslabón nuevo (`seq+1`, `prev`);
   `begin` divergente con la misma clave → conflicto/escalado sin sobrescribir;
   `reconcile` de un paquete cuya clave ya no es el head → comportamiento
   cubierto por el RED de T2.
6. Compatibilidad hacia atrás (P7) probada con **copias de los stores en tmp**
   (fixtures autocontenidos); el render sobre los stores reales se verifica en T3.
7. `resume --role test-writer` no expone `implementation_roots`.
8. Rotación real dentro de 003-007 registrada en
   `docs/specs/003-007-living-continuity/continuity-ledger.md`, con instalación
   por ruta explícita desde raíz aislada y **sin reactivar** el repo.
9. Regla de encargo reconciliada y clases declaradas en
   `sources/roles/orchestrator.md` (BL-1) y agentes regenerados (`make agents`),
   con test de coherencia.
10. Sin regresiones en `tests/test_003_004_*` y `tests/test_003_006_t4_*`
    (incluida la faceta `begin` de `test_003_006_t4_ru2_refused_write.py`);
    validadores del repo sin regresiones (F011 y A3 son deuda preexistente).
11. Cero afirmaciones de ahorro no medido; tokens/contexto ausentes quedan `null`.

## 6. Fuera de alcance

- Defaults de clase por policy (bloqueado por el esquema estricto de
  `docs/cdad-policy.json`, `cdad_packet.py:404-415`); requiere coordinación con el
  renderer → deuda.
- Detección de forks de checkpoint (dos checkpoints divergentes bajo la misma
  clave); sigue siendo responsabilidad del orquestador.
- Lector de sesiones por runtime, medición de contexto, CI, caché universal de
  evidencia, benchmark.
- Cambiar permisos, autoridad o política; nuevo epic de seguridad.

### Deuda priorizada (declarada, no oculta)

1. **Defaults de clase por policy** (causa: `cdad_packet.py:406` exige
   `set(document) == POLICY_KEYS`).
2. **Detección de forks de checkpoints mismo-key** (residual tras D5).
3. **Integridad de `stage_history` (R-2):** las aprobaciones registradas sólo en
   el historial del state quedan fuera de todo digest; el state no está
   protegido por referencias en los dos checkpoints existentes y
   `_state_authority` cubre revocación vía `hitl_delegation.revoked_at`.
4. **Huérfanos pre-RU-2 y `_detect_split_brain` casi-muerto:** con P5 la
   detección sólo dispara con cuerpos legados/huérfanos; mantener el límite de
   orfans documentado en `continuity.md:65-67`.

## 7. Contexto técnico (anclas)

- `skills/cdad-cycle/scripts/cdad_continuity.py:369-381,463-483,499-573,693-742,824-888,943-954,1053-1118`.
- `skills/cdad-cycle/references/continuity.md` (se extiende; con ejemplo con clases).
- `skills/cdad-cycle/assets/continuity-checkpoint.schema.json:52-69`.
- `docs/.cdad-state.json:1339-1408` (`approver`, `hitl_delegation`, `execution`).
- `sources/roles/orchestrator.md:69-72,77-82` (regla + Continuity wiring).
- `docs/specs/003-006-runtime-adoption/debt.md:17-18`; `evidence/t4/rotation-1-blocked.md:3-7`, `checkpoint-after-ru1-REFUSED.txt:1`.
- `tests/test_003_006_t4_ru2_refused_write.py:1-59` (faceta `begin` intacta; faceta `checkpoint` reespecificada por P5).
- Stores reales: `.cdad/executions/{exec-003-004-context-continuity-001,exec-003-006-runtime-adoption-001}/continuity/`.

## 8. Decisiones (D1–D10) y VERIFY

Propuesta del arquitecto; **el orquestador las adopta/corrige bajo la delegación
HITL**. Las filas marcadas “(ronda 2)” incorporan la review y su disposición.

| ID | Decisión |
|---|---|
| D1 | State con proyección `fields`; autoridad = `hitl_delegation`+`approver`+`execution`; `stage_history` es progreso (residuo R-2 → deuda) |
| D2 | Clase declarada en la referencia (no en el CLI); policy descartado por esquema estricto (`cdad_packet.py:404-415`) |
| D3 | `contract` cambia → `rc≠0`; `living` cambia → informa con `state`/`current_sha256` |
| D4 | `references[]` acepta string u objeto; modo `fields` para JSON; clase resuelta congelada en el body |
| D4b (ronda 2, BL-3) | `fields` sobre no-JSON → `rc≠0` al escribir; proyección vacía → `rc≠0` al escribir |
| D5 | Body de checkpoint gana `record`; mismo-`begin`-clave divergente sigue cerrado; begin byte-idéntico (BC no-op); `_detect_split_brain` = ≥2 begins/legados por clave |
| D6 (ronda 2, R-1) | Legado sin `class`: resolución **por comparación** — igual → verificado `contract`; distinto → `changed` con `legacy: true`, **no bloquea** (reemplaza el puente blanket). Excepción: la clase de legado no está congelada |
| D7 | Uso sin reactivar: raíz aislada + ruta explícita + `--optimus` (R-5 rechazado); ledger con marcadores |
| D8 | `continuity.md` documenta forma y convención de clases, **con ejemplo que declara clases** (BL-1) |
| D9 (ronda 2, BL-1/R-4) | `orchestrator.md`: el bloque "Continuity wiring" declara `living`/`contract` explícitamente (o puntero estricto); texto de la regla con el ejemplo de RED/GREEN como despachos separados |
| D10 | Alcance mínimo y deuda (defaults por policy, forks, integridad de `stage_history`, huérfanos pre-RU-2) |

**VERIFY:** V1 fuente “referencia” aceptada; V2 canonicalización de `fields`;
V3 esquema sin validación en runtime (R-STR); V5 headroom 16 KiB (la review se
abstuvo de medirlo: queda para el RED); V6 focales/gate por tarea; V7 bloqueo
verificado sin editar la spec real; V8 no hay otros consumidores de `references[]`.

---

Status: draft (pendiente de aprobación del orquestador/usuario).
```

---

```markdown
---
feature_id: 003-007-living-continuity
feature_name: Continuidad que tolera documentos vivos
created_at: 2026-10-08
status: draft
approved_by: null
approved_at: null
---

# Plan — 003-007-living-continuity (borrador, ronda 2)

> Borrador del architect derivado de `architect-draft-001.md` aplicando
> `review-draft-001.md` con la disposición `review-draft-001-decision.md`
> (BL-1, BL-2, BL-3; R-1, R-2, R-3, R-4; R-5 rechazado; abstención de
> `reconcile` aceptada). 4 tareas (máximo del encargo). La **última** tarea
> concentra los cambios de `sources/roles/orchestrator.md` (clases del wiring
> BL-1 + texto D9/R-4) y regenera agentes (`make agents`). El plan define el
> contrato, nunca el código. Gate de tests vigente (2026-10-08): el implementer
> corre **focales + tests de los módulos tocados**; suite completa al cierre o si
> toca instalador/staging/renderer. Focales nombrados por tarea.

## Restricciones globales (copia de la spec)

- Repo en español. Tooling Python **stdlib-only**.
- Nunca instalar/modificar CDAD en el HOME real; raíces aisladas bajo `~/.cache`.
- Sin push automático. Ledger y docs nuevos **sin rutas absolutas** (marcadores
  `<adopted-root>`/`<project-root>`).
- No endurecer permisos; sin CLI nuevo; reutilizar `cdad_continuity.py`.
- No tocar `docs/cdad-policy.json` (esquema estricto, `cdad_packet.py:404-415`).
- Instalación aislada con el perfil del proyecto: `CDAD_INSTALL_ROOT=… bash install.sh --optimus`
  (R-5 rechazado).

## 1. Tareas

### T1 — Clases de referencia (contrato/vivo) + proyección de autoridad + compatibilidad
- **Postcondiciones:** P1, P2, P3, P4, P7, P8.
- **Alcance incluido:** `--update.references[]` acepta string u objeto
  (`class`, `fields`); modo `fields` para JSON con **fallo cerrado al escribir**
  si el archivo no es JSON o si la proyección resuelve vacía (BL-3); el digest de
  `contract` bloquea y el de `living` informa (`state`/`current_sha256` en el
  sobre de `resume`/`reconcile`/`trigger`); clase resuelta congelada en el body;
  **legado por comparación** (D6/R-1): igual → verificado `contract`, distinto →
  `changed` con `legacy: true` sin bloquear; filtro de rol intacto. `continuity.md`
  documenta la forma, la convención de clases y **un ejemplo que declara clases**
  (BL-1).
- **Excluido:** T4-CKPT (T2); defaults por policy (deuda).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Modify `skills/cdad-cycle/assets/continuity-checkpoint.schema.json`;
  Modify `skills/cdad-cycle/references/continuity.md`;
  Create `tests/test_003_007_t1_reference_classes.py`.
- **Focales:** `tests/test_003_007_t1_reference_classes.py`,
  `tests/test_003_004_t1_resume.py`, `tests/test_003_004_t1_checkpoint.py`,
  `tests/test_003_004_t4_real_context.py`.
- **Validación (fixtures autocontenidos, R-3):** `contract` cambiada → `rc≠0`;
  `living` cambiada → `rc 0` con `state: changed`; cambio de `stage_history` no
  bloquea y de `hitl_delegation` bloquea; `fields` sobre no-JSON → `rc≠0`;
  `fields` con proyección vacía → `rc≠0`; `resume --role test-writer` sin
  implementación. **P7 se prueba con copias de los stores en tmp**; el render
  sobre los stores reales queda como observable de T3.
- **Detener si:** V2 (canonicalización de `fields`) no se fija sin ambigüedad.
- **Owner:** RED test-writer; GREEN implementer.

### T2 — T4-CKPT: `checkpoint` distinto de `begin`
- **Postcondiciones:** P5, P6.
- **Alcance incluido:** `record` en el body de checkpoint (begin byte-idéntico);
  `checkpoint` con la clave del head apendea eslabón (`seq+1`, `prev`); `begin`
  divergente con la misma clave sigue cerrado; `record` en el sobre;
  `_detect_split_brain` redefinido (**≥2 bodies con `record != "checkpoint"` por
  clave**, p. ej. huérfanos pre-RU-2). **Se declara explícitamente la
  modificación de la faceta `checkpoint` de
  `tests/test_003_006_t4_ru2_refused_write.py`** (BL-2): el test-writer la
  reespecifica en el RED de T2 con trazabilidad a P5; la faceta `begin`
  divergente y el all-or-nothing RU-2 quedan **intactos** y siguen siendo el
  corazón del test. Incluir en el RED el escenario de la abstención aceptada:
  `reconcile` de un paquete **cuya clave ya no es el head** tras un append.
  Actualizar `continuity.md` (detección vigente + límite de orfans).
- **Excluido:** detección de forks de checkpoint mismo-key (deuda).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Modify `skills/cdad-cycle/assets/continuity-checkpoint.schema.json`;
  Modify `skills/cdad-cycle/references/continuity.md`;
  Modify `tests/test_003_006_t4_ru2_refused_write.py` (sólo faceta `checkpoint`);
  Create `tests/test_003_007_t2_checkpoint_vs_begin.py`.
- **Dependencias:** T1 (mismo archivo; evita conflicto).
- **Focales:** `tests/test_003_007_t2_checkpoint_vs_begin.py`,
  `tests/test_003_006_t4_ru2_refused_write.py`,
  `tests/test_003_004_t2_writeahead.py`.
- **Validación:** checkpoint mismo-key → `seq+1` con `prev` correcto; begin
  divergente mismo-key → `rc≠0`; checkpoint idéntico re-ejecutado → no-op;
  split-brain para dos begins; `reconcile` con clave no-head consistente.
- **Owner:** RED test-writer; GREEN implementer.

### T3 — Aceptación: rotación real dentro de 003-007
- **Postcondición:** P9.
- **Alcance incluido:** instalar la versión nueva en una raíz aislada
  (`CDAD_INSTALL_ROOT=… bash install.sh --optimus`, bajo `~/.cache`) e invocarla
  por ruta explícita, **sin reactivar** el repo (D7); tras el último checkpoint
  de un paquete, escribir en un documento vivo (ledger/deuda) → `resume`
  **rinde** y reporta los vivos cambiados; verificar el bloqueo de una referencia
  `contract` (spec aprobada) sin editar la spec del repo (proyecto sintético en
  T1 y/o copia controlada). **Verificar el render sobre los stores reales** de
  `exec-003-004-context-continuity-001` y `exec-003-006-runtime-adoption-001`
  (R-3). Registrar en el ledger.
- **Excluido:** editar la spec aprobada; benchmark.
- **Archivos:** Create `docs/specs/003-007-living-continuity/continuity-ledger.md`;
  Modify `docs/specs/003-007-living-continuity/dispatch-ledger.md`.
- **Registro obligatorio:** `situación | evidencia (file:line) | decisión |
  autoridad vigente | presupuesto (intentos/contexto o null) | falsas alarmas |
  retrabajo | pendiente`, con rutas en marcadores.
- **Observable:** `resume` sobre la ejecución real de 003-007 rinde y lista los
  vivos `changed`; `resume` sobre las dos ejecuciones existentes rinde y reporta
  los legados divergidos; bloqueo `contract` reproducido (copia); sin
  reactivación.
- **Dependencias:** T1, T2 verdes.
- **Owner:** orquestador.

### T4 — Regla de encargo reconciliada + declaración de clases del wiring (última, separada)
- **Postcondición:** P10.
- **Alcance incluido (BL-1 + R-4):**
  (a) reemplazar el paréntesis "one postcondition, one test, one diff; do not
  group sub-phases" de `sources/roles/orchestrator.md:69-72` por el texto de D9,
  que incluye el ejemplo: *una tarea del plan cuyos RED y GREEN son despachos
  separados satisface la regla*;
  (b) en el bloque "Continuity wiring" (`orchestrator.md:77-82`) declarar
  explícitamente qué se registra `living` (ledgers, `debt.md`, Memory Bank,
  borradores de cierre/enmienda) y qué `contract` (spec/plan aprobados,
  `docs/cdad-policy.json`, state con `fields` de autoridad), o un puntero
  estricto a la sección de `continuity.md`;
  (c) regenerar `agents/` (`make agents`).
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
  trazabilidad test↔postcondición, el diff acotado, el ejemplo RED/GREEN y la
  declaración de clases del wiring; `make agents` determinista (sin diff
  inesperado).
- **Nota:** T4 es funcionalmente independiente de T1–T3 y se secuencia última
  (mismo archivo de rol que nada más toca; regenera agentes).
- **Owner:** RED test-writer; GREEN implementer.

## 2. Cobertura spec↔plan

P1,P2,P3,P4,P7,P8→T1; P5,P6→T2; P9→T3; P10→T4. Ninguna P sin tarea; ninguna
tarea sin P.

## 3. Estimaciones (rango, método, incertidumbre)

- Rango: **medio** (T1), **bajo–medio** (T2), **bajo** (T3), **bajo–medio** (T4).
  Método: comparación cualitativa con 003-004. Incertidumbre **media** por V2
  (canonicalización de `fields`) y V5 (headroom 16 KiB, no medido por la review:
  queda para el RED).

## 4. Integración final

1. Suite completa del repo + validadores (sin regresiones; F011 y A3 deuda
   preexistente declarada).
2. Rotación real registrada en `continuity-ledger.md`, con render sobre las dos
   ejecuciones reales.
3. Spec y plan revisados juntos por sesión independiente antes de aprobar.

## 5. Incertidumbres / replanificación

- Si V2 no se resuelve, reacotar el shape de `fields` antes de RED.
- Si el render legado revela una deriva de spec no prevista, escalar al
  orquestador (no reinterpretar el puente D6/R-1).

```plan-tasks
{
  "validation_strategy": "focales por unidad (pytest, env -u TMPDIR) con proyectos y stores copiados a tmp (fixtures autocontenidos); módulos tocados (test_003_004_*, test_003_006_t4_*) en cada tarea; suite completa y validadores al cierre y en T4 (make agents toca staging/renderer); aceptación real en raíz aislada invocada por ruta explícita, sin reactivar el repo ni editar la spec aprobada; render sobre los stores reales como observable de T3; ledger anonimizado",
  "tasks": [
    {"id": "T1", "produce": [{"artifact": "cdad-continuity-reference-classes", "contract": "continuity-checkpoint-v1"}], "consume": [], "depends_on": [], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "skills/cdad-cycle/assets/continuity-checkpoint.schema.json", "skills/cdad-cycle/references/continuity.md", "tests/test_003_007_t1_reference_classes.py"], "focal_tests": ["tests/test_003_007_t1_reference_classes.py", "tests/test_003_004_t1_resume.py", "tests/test_003_004_t1_checkpoint.py", "tests/test_003_004_t4_real_context.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T2", "produce": [{"artifact": "cdad-continuity-checkpoint-record", "contract": "continuity-checkpoint-v1"}], "consume": [{"artifact": "cdad-continuity-reference-classes", "contract": "continuity-checkpoint-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "skills/cdad-cycle/assets/continuity-checkpoint.schema.json", "skills/cdad-cycle/references/continuity.md", "tests/test_003_006_t4_ru2_refused_write.py", "tests/test_003_007_t2_checkpoint_vs_begin.py"], "focal_tests": ["tests/test_003_007_t2_checkpoint_vs_begin.py", "tests/test_003_006_t4_ru2_refused_write.py", "tests/test_003_004_t2_writeahead.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T3", "produce": [{"artifact": "continuity-ledger-003-007", "contract": "n/a"}], "consume": [{"artifact": "cdad-continuity-reference-classes", "contract": "continuity-checkpoint-v1", "producer": "T1"}, {"artifact": "cdad-continuity-checkpoint-record", "contract": "continuity-checkpoint-v1", "producer": "T2"}], "depends_on": ["T1", "T2"], "parallel": [], "files": ["docs/specs/003-007-living-continuity/continuity-ledger.md", "docs/specs/003-007-living-continuity/dispatch-ledger.md"], "observable_checks": ["una rotacion real dentro de 003-007 con escrituras de ledger posteriores al ultimo checkpoint: resume rinde y reporta los documentos vivos cambiados", "una edicion deliberada de la spec aprobada (contrato) bloquea, verificado sin editar la spec del repo", "la version nueva se invoca por ruta explicita desde una raiz aislada bajo ~/.cache sin reactivar el repo", "resume sobre exec-003-004-context-continuity-001 y exec-003-006-runtime-adoption-001 rinde proyeccion y reporta los legados divergidos"], "regressions": ["tests/validate-consistency.sh", "tests/validate-odoo-specialization.sh"], "integration_gate": "@validation_strategy", "owner": "orquestador"},
    {"id": "T4", "produce": [{"artifact": "regla-encargo-atomico-y-clases-wiring", "contract": "n/a (reglas operativas)"}, {"artifact": "agentes-regenerados", "contract": "n/a (salidas generadas)"}], "consume": [], "depends_on": ["T3"], "parallel": [], "files": ["sources/roles/orchestrator.md", "agents/cdad-orchestrator.md", "agents/claude-code/cdad-orchestrator.md", "tests/test_003_007_t4_atomic_unit_rule.py"], "focal_tests": ["tests/test_003_007_t4_atomic_unit_rule.py", "tests/test_003_006_t3_receive_wiring.py"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"}
  ]
}
```

---

Status: draft (pendiente de aprobación del orquestador/usuario).
```

---

## Cambios respecto del borrador 1

1. **BL-1 (aceptado) — wiring declara clases.** T4 amplía alcance: en el bloque "Continuity wiring" de `sources/roles/orchestrator.md` se declara explícitamente qué es `living` (ledgers, `debt.md`, Memory Bank, borradores de cierre/enmienda) y qué `contract` (spec/plan aprobados, `docs/cdad-policy.json`, state con `fields` de autoridad), o puntero estricto a `continuity.md`. Se refleja en **P10** y en el archivo/test de T4. T1 añade a `continuity.md` un **ejemplo que declara clases** (no solo strings).
2. **BL-2 (aceptado) — test RU-2.** T2 ahora declara explícitamente la modificación de la **faceta `checkpoint`** de `tests/test_003_006_t4_ru2_refused_write.py` (la hace el test-writer en el RED de T2, con trazabilidad a P5); la faceta `begin` divergente y el all-or-nothing RU-2 quedan intactos. El plan precisa además **qué sigue detectando** `_detect_split_brain` (≥2 begins/legados por clave, p. ej. huérfanos pre-RU-2). El test pasa de “focal sin autorización de edición” a archivo autorizado en el `write_scope` de T2.
3. **BL-3 (aceptado) — modos de fallo de `fields`.** **P4 extendida**: `fields` sobre archivo no-JSON → `rc≠0` al escribir; `fields` con proyección vacía → `rc≠0` al escribir. Añadido como **D4b** y a los criterios de aceptación (nº 4).
4. **R-1 (aceptado, reemplaza el puente blanket) — legado por comparación.** La antigua D6 “legado = vivo (blanket)” se sustituye por **D6 por comparación**: digest igual → verificado `contract`; distinto → `changed` con `legacy: true`, no bloquea. **P7 reescrita**; se documenta la excepción (la clase de legado no está congelada). El sobre gana el campo `legacy`.
5. **R-2 (aceptado como deuda).** La spec incorpora una sección **“Deuda priorizada”** con la integridad de `stage_history` (aprobaciones fuera de todo digest), además de defaults por policy, forks de checkpoint y huérfanos pre-RU-2. D1 deja de apoyarse en la generalización “las aprobaciones durables viven en el artefacto”.
6. **R-3 (aceptado) — fixtures autocontenidos.** **P7** y T1 se prueban con **copias de los stores en tmp**; el render sobre los stores reales de las dos ejecuciones pasa a **observable de T3** (P9).
7. **R-4 (aceptado) — ambigüedad D9.** El texto de la regla incluye el ejemplo: *una tarea del plan cuyos RED y GREEN son despachos separados satisface la regla*; **P10** lo recoge y T4 lo valida en su focal.
8. **R-5 (rechazado).** Se mantiene `bash install.sh --optimus`; se explicita que es el perfil del proyecto sobre raíz aislada.
9. **Abstención de `reconcile` (aceptada).** T2 incorpora al RED el escenario de `reconcile` de un paquete **cuya clave ya no es el head** tras un append; añadido al criterio de aceptación nº 5.
10. **Consecuentes menores:** tabla de casos (§2) con la fila de legado por comparación; invariante 4 menciona explícitamente el fallo cerrado de `fields`; VERIFY mantiene V5 (no medido por la review) y V2; D9/D10 reformulados para cubrir BL-1 y R-4; T4 pasa a “bajo–medio” en estimaciones y su alcance (a)(b)(c) queda desglosado.
