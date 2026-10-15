# 1. Tabla — lo que ya existe vs. lo que falta (reutilización)

| # | Capacidad | Existe hoy (ancla verificada) | Qué falta exactamente | Disposición |
|---|---|---|---|---|
| 1 | Identidad/estado/paquete | `docs/.cdad-state.json` con `execution`, `active_packet`, `hitl_delegation`, `epic_features`, `stage_history` (`state-template.json:1-19`; contrato `003-001/spec.md:436-526`) | Una **vista de continuidad** (no un schema de estado nuevo) | **Reutilizar** state tal cual; no tocar su schema |
| 2 | Resultado original + receipts idempotentes | `cdad_result.py`; `.cdad/runtime/results/<exec>/<packet>/{receipt.json,bundle.json,parts}` (real en `.cdad/runtime/results/exec-003-002-artifact-tools-001/…`); `result-receipt.schema.json` (`semantic_status=pending`, `state_transition_requested=received`) | Nada: es la autoridad de "efecto aplicado" | **Reutilizar** como oráculo de reconciliación (`re-entry.md:57-63`) |
| 3 | Eventos + presupuesto de intentos | `cdad_guard.py` `record`/`budget` bajo `.cdad/executions/<id>/guards/**` (`cdad_guard.py:72-83,586-587`); `guard-event.schema.json`; `guard_budget.max_attempts` (`cdad_guard.py:645-651`) | Cómo **sobrevive** al cambio de sesión (ya durable; falta el puente en `resume`) | **Reutilizar** el presupuesto de 003; no duplicarlo (`003-003/spec.md:219,225`) |
| 4 | Intento despachado (I8) | `.cdad/executions/<id>/dispatches/*.json` (`packet_id`, `role`, `substage`, `runtime`, `session`, `model_configured/reported`, `started_at`) | — | **Referenciar** en la reconciliación |
| 5 | "Active record" **manual** | `docs/activeContext.md` (entry por feature), `docs/epics/.../handoff*.md`, `handoff.md:96-98` ("guardar objetivo/HEAD/rol/autoridad/trabajo en curso/próxima acción") | Es **prosa, sin checksum ni campos cerrados**; no es reconstruible de forma determinista | **Reemplazar por esquema** (L1/L2), conservando los handoffs como historia (L3) |
| 6 | Historia referenciable | `stage_history`/`epic_history` (state), receipts/journal (002), guard events (003), dispatches (I8), Memory Bank (`activeContext.md`, `progress.md`, `systemPatterns.md`), `docs/adr/ADR-015` | Nada que inventar | **L3 = referencias** a lo existente (no un log nuevo) |
| 7 | **Checkpoint inmutable con checksum** | — | Snapshots create-only, content-addressed, encadenados, con integridad de referencias | **CREAR** |
| 8 | **Active record pequeño y acotado** (objetivo, scope, autoridad, decisiones con razón, incertidumbres, tareas/gates, agentes en curso, receipts, presupuesto, próxima acción) | Parcial en prosa (5) | Esquema cerrado + cap de bytes + proyección reproducible | **CREAR** |
| 9 | **Reconciliación write-ahead + post-dispatch** | 001 valida binding en `prepare`/`materialize`; 002 reconcilia receipts a mano (`re-entry.md:46-63`) | Algoritmo determinista "sesión desaparecida ≠ fracaso", antes de retry/resume | **CREAR** |
| 10 | **Trigger preventivo** (200k/150k/120k) | 003 mide intentos, **no** contexto; no hay lector de sesiones (`progress-guards.md:17`); no hay límite duro público (`runtime-discovery.md:39-41,43-46`; `003-003/spec.md:234` V4) | Cálculo con `null` + unknowns por runtime | **CREAR** (señal, nunca límite fabricado) |
| 11 | Resolución split-brain/stale/autoridad vencida/tarea cerrada | Autoridad vencida ya bloquea `prepare`/`materialize` (`003-001/spec.md:487-509`; `activeContext.md:84-90`) | Regla en el **resume** (single-writer, generación monotónica) | **CREAR** |
| 12 | Estado de sesión por runtime ("viva/estancada/muerta") | API `status/children/fork` listada (`runtime-discovery.md:23-25`) pero **no probada** para distinguir estados | Declarar VERIFY; no asumir | **VERIFY** (no construir sobre API supuesta) |

**Frontera con 003 (sin redefinir):** `003-003` declaró que sus interfaces "no obstaculizan la continuidad" (keyed por `execution_id`, sin truncar) — `003-003/spec.md:158-161`. 003-004 **consume** esa promesa; no la reescribe.

---

# 2. Schema del active record + reconciliación + triggers + matriz

## 2.1 Tres capas, autoridad y checksum

| Capa | Artefacto | Autoridad | Checksum / integridad |
|---|---|---|---|
| **L1 active record** (caché derivada, mutable) | `.cdad/executions/<execution_id>/continuity/ACTIVE.json` | **Derivada** (proyección de L2-head + receipts + state). Si discrepa, **pierde** y se reconstruye | `record_sha256` (self) + `checkpoint_ref.sha256`; cap de bytes (≤ 16 KiB declarado) |
| **L2 checkpoint inmutable** (autoridad de delegación/decisiones/presupuesto del instante) | `.cdad/executions/<execution_id>/continuity/checkpoints/<seq4>-<sha256>.json` (create-only) | **Autoridad** para "qué se delegó, qué se decidió (con razón), qué presupuesto había" en el write-ahead/rotación | Nombre = `sha256(cuerpo canónico)`; `prev_checkpoint_sha256` (cadena → omisión/tamper detectable); `references[]` con `path+sha256` (existencia + integridad) |
| **L3 historia referenciable** (append-only existente) | `stage_history`/`epic_history`, receipts/journal (002), guard events (003), dispatches (I8), Memory Bank, handoffs/ADRs | Histórica/auditable | Identity ya existente (content-addressed en 002; dispatch por attempt; state por transición) |

**Orden de precedencia en toda reconciliación:** state (autoridad/packet) **>** receipts 002 (efecto aplicado) **>** checkpoint L2 (intención/decisiones) **>** ACTIVE L1 (caché) **>** narración humana (handoffs). Un `ACTIVE.json` que contradiga L2/state/receipts se marca `stale` y se reconstruye; **nunca** se usa para autorizar un retry.

Dónde escriben: el CLI escribe **solo** bajo `.cdad/executions/<id>/continuity/**`. `docs/.cdad-state.json` sigue con **un solo escritor = el orquestador** (invariante de 002/003, `re-entry.md:57-63`).

## 2.2 Schema mínimo (L1 body ≡ cuerpo del checkpoint)

```json
{
  "schema_version": 1,
  "record": "active-record-v1",
  "execution_id": "exec-003-004-context-continuity-001",
  "epic_id": "epic-003-context-efficiency",
  "feature_id": "003-004-context-continuity",
  "seq": 3,
  "generation": 3,
  "objective": "…",
  "scope": "…",
  "authority": {"ref": "docs/epics/epic-003-context-efficiency/execution.md",
                "status": "active|expired|revoked", "expires_on": ["epic-closed","epic-cancelled","user-revoked"],
                "source": "state.hitl_delegation"},
  "stage": {"current_stage": "tdd", "tdd_substage": "green",
            "active_packet": {"id": "…", "role": "…", "substage": "…", "status": "dispatched"}},
  "decisions": [{"id": "D3", "decision": "…", "reason": "…", "at": "…", "source": "…"}],
  "uncertainties": [{"id": "V1", "text": "…", "kind": "verify", "owner": "dueño"}],
  "tasks": [{"id": "T3", "status": "open|closed", "depends_on": ["T2"], "gate": "…"}],
  "agents": [{"role": "implementer", "packet_id": "…", "session": "ses_…|null",
              "status": "in-flight|unknown|done"}],
  "receipts": [{"packet_id": "…", "receipt_sha256": "…", "semantic_status": "pending",
                "effect": "none|received|materialized"}],
  "budget": {"profile": "200k", "attempts_used": 2, "attempts_max": 3,
             "source": "cdad_guard budget", "context_used_tokens": null,
             "context_limit": null, "reserve": 50000},
  "next_action": {"text": "…", "owner": "…", "packet_id": "…"},
  "references": [{"path": "docs/specs/…/spec.md", "sha256": "…"}],
  "checkpoint_ref": {"seq": 3, "sha256": "…",
                     "path": ".cdad/executions/<id>/continuity/checkpoints/0003-<sha>.json"},
  "generated_at": "2026-10-07T…Z"
}
```

Body del checkpoint = lo anterior **+** `{"kind": "write-ahead|rotation|closed", "prev_checkpoint_sha256": "…|null"}`. Reglas de contenido: `unknown` se representa con `null` (nunca 0 ni cadena vacía); **no hay transcripciones** — sólo `references[]` y resúmenes acotados (≤ 16 KiB; exceder → rc≠0, jamás truncado silencioso, `plan.md:124-126`).

## 2.3 Algoritmo de reconciliación (write-ahead antes de dispatch; posterior por status + receipts)

**A. `begin` (write-ahead, antes de despachar) — 4 pasos**
1. **Precondiciones:** execution context válido; binding de state válido (reutiliza `validate_state` de 001); `authority.status=="active"` y ningún evento de `expires_on` ocurrido (`003-001/spec.md:487-509`). Falla → rc≠0, sin escribir.
2. **Merge:** cuerpo = (checkpoint anterior) ⊕ (`--update`) con las decisiones/incertidumbres/tareas/`next_action` vigentes y el nuevo `agents[]` en estado `in-flight` (`packet_id`, `role`, `substage`, `session|null`).
3. **Escribir L2** `<seq4>-<sha256>.json` **create-only** (si existe con bytes distintos → rc≠0, sin overwrite) con `prev_checkpoint_sha256` = head anterior.
4. **Escribir L1** `ACTIVE.json` atómica (temp+fsync+rename). Tras esto, **el orquestador** (y sólo él) marca `active_packet.status="dispatched"` en state. El CLI no toca el state.

**B. `reconcile --packet P` (antes de cualquier retry / al reanudar) — clasificación cerrada**

| Evidencia para `(execution_id, P)` | `status` | Acción permitida |
|---|---|---|
| `receipt.json` existe en `.cdad/runtime/results/<exec>/<P>/` | `effect-applied` | **No repetir** efecto; mapear `state_transition_requested=received` → `completed` (una sola transición, orquestador) |
| `materializations/` journal existe | `effect-materialized` | **No repetir** materialización |
| dispatch I8 existe, **sin** receipt | `dispatched-unknown` | **No** es fracaso ni autorización de repetir; preservar parcial; `resume-same-session` (1×) o re-dispatch sólo con hipótesis/información nueva (`re-entry.md:79`) |
| sin dispatch y sin receipt | `not-started` | Re-dispatch seguro |
| state `completed` **y** receipt | `already-closed` | No re-despachar; reportar cerrado |
| señales contradictorias / runtime no observable | `unknown` | Escalar paquete breve; **no** fabricar éxito ni fracaso |

**C. `resume` (reconstrucción selectiva para sesión nueva)**
1. Leer L2-head y `ACTIVE.json`; verificar `ACTIVE.checkpoint_ref.sha256 == head` y la cadena (`prev_*`).
2. Verificar cada `references[].path` existe y su `sha256` coincide (tampering / referencia inexistente → P1).
3. Verificar autoridad (`active` + no expirada).
4. Render **acotado**: objetivo, scope, autoridad+expiración, decisiones con razón, incertidumbres, tareas/gates, agentes en curso, receipts, presupuesto, próxima acción. **Sin transcript.** Con `--role <rol>`, filtra `references[]` al scope del rol (P5: el test-writer nunca recibe implementación).
5. Si stale/tamper: rc≠0 con el delta exacto; `--allow-stale` marca `stale=true` + delta, **nunca** silencioso.

## 2.4 Trigger preventivo — perfil 200k/150k/120k con unknowns por runtime

Envelope `continuity-trigger-v1`:
```json
{"trigger": "ok|prepare|rotate|unknown",
 "profile": "200k", "entry_max": 150000, "reserve": 50000, "prepare_at": 120000,
 "context_used_tokens": null, "context_limit": null,
 "unknowns": ["context_limit no reportado por el runtime"],
 "source": "runtime step-finish | none"}
```
Regla: `trigger` sólo se calcula si `context_used_tokens` **y** `context_limit` son enteros; en cualquier otro caso → `unknown` con `unknowns[]`. **Prohibido convertir bytes en tokens** o presentar un proxy como límite (`plan.md:121-126`; `runtime-discovery.md:43-46`).

| Runtime | `context_used_tokens` | `context_limit` | `trigger` | Unknown declarado |
|---|---|---|---|---|
| **OpenCode** | último `step-finish`/mensaje (tokens reportados, `runtime-discovery.md:27-29`) | **`null`** (no hay límite duro público; `runtime-discovery.md:39-41`; V4 de 003-003) | `unknown` | ¿`input_tokens` es acumulativo de sesión o del paso? (**VERIFY**) |
| **Claude Code** | `null` (sin lector de producto; `progress-guards.md:17`) | `null` | `unknown` | reporte manual del usuario; sin lector |
| Cualquiera sin contador | `null` | `null` | `unknown` → **rotar en un límite natural de tarea** | — |

Presupuesto de **intentos** (distinto de contexto): se lee del durable de 003 (`cdad_guard budget`), keyed por `execution_id+packet_id`; un restart/sesión nueva **no** lo reinicia (P4).

## 2.5 Matriz crash / restart / split-brain / stale / autoridad vencida / tarea ya cerrada

| Escenario | Señal observable | Decisión | Garantía que la respalda |
|---|---|---|---|
| **Crash antes de dispatch** | checkpoint escrito, sin dispatch, sin receipt | `not-started` → re-despacho permitido | ningún efecto aplicado |
| **Crash tras dispatch; sesión desapareció** | dispatch I8, sin receipt | `dispatched-unknown`: **no** es fracaso, **no** autoriza repetir; preservar parcial; `resume-same-session` 1×; re-dispatch sólo con hipótesis nueva | `remaining-features-handoff.md:235-237`; `re-entry.md:79` |
| **Restart / sesión nueva** | `resume` reconstruye L1 desde L2+receipts+state | Continúa **sin** pedir objetivo/aprobaciones; autoridad vencida no permite despachar | P2; `plan.md:75-76` |
| **Split-brain (dos sesiones reanudadas)** | dos escritores de ACTIVE con `generation` distinto | Gana la `generation` mayor del **single-writer** (orquestador); la otra **se detiene** y reporta; conflicto de igual generación → escalar | single-writer; `re-entry.md:57-63` |
| **Checkpoint stale / referencia faltante / tamper** | `ACTIVE.checkpoint_ref ≠ head` o `sha256` no coincide | rc≠0 con delta exacto; reconstruir L1 desde L2/state; **no** usar ACTIVE para autorizar | P1 |
| **Autoridad vencida** | `hitl_delegation.status != active` / evento de `expires_on` | `resume` puede **reconstruir** contexto pero **no** autorizar dispatch/materialize; escalar | `003-001/spec.md:487-509`; `activeContext.md:84-90` |
| **Tarea ya cerrada** | receipt + state `completed`/feature `done` | `already-closed`: no re-despachar; reportar | idempotencia 002 (`re-entry.md:46-50`) |

---

# 3. Decisiones abiertas para el dueño (numeradas, con recomendación)

> **B** = bloqueante de aprobación; **S** = decidible durante la spec. El architect **no aprueba** su propuesta (ADR-003/ADR-011).

- **D1 (B) — Forma y frontera del instrumento.** ¿CLI nuevo, o ampliar `cdad_guard`? **Recomiendo:** CLI determinista **`cdad_continuity.py`** (Python stdlib) + wrapper `scripts/cdad_continuity.py`, **read-only** sobre el producto; escribe sólo bajo `.cdad/executions/<id>/continuity/**`. Sin servicio ni agente permanente (`remaining-features-handoff.md:35`; `plan.md:50-51`).
- **D2 (B) — Autoridad de las tres capas.** **Recomiendo:** L2 checkpoint inmutable = autoridad de delegación/decisiones/presupuesto; L1 = caché derivada que pierde ante L2/receipts/state; L3 = referencias a la historia existente (state/stage_history, receipts 002, eventos 003, dispatches I8, Memory Bank). **No** inventar un log nuevo ni un schema de estado nuevo.
- **D3 (B) — Propiedad de escritura.** **Recomiendo:** el CLI nunca escribe `docs/.cdad-state.json`; el state mantiene un solo escritor (el orquestador), como 002/003. La transición `received → completed` la aplica **sólo** el orquestador (`re-entry.md:57-63`).
- **D4 (B) — Época/vigencia de la autoridad al reanudar.** **Recomiendo:** leer autoridad y vigencia del **state** (`hitl_delegation` + `authority_ref`), reutilizando `validate_state` de 001; autoridad vencida reconstruye contexto pero **no** autoriza efectos.
- **D5 (B) — Semántica del trigger.** **Recomiendo:** umbral = **señal**, no límite duro; `prepare_at=120k` sólo si el runtime reporta contador y límite; si no, `unknown` + rotación en un **límite natural de tarea**. “Habrá que calibrar con uso real” (`handoff-architect-001.md:32`).
- **D6 (B) — Write-ahead y anti-duplicado.** **Recomiendo:** `begin` antes de despachar; `reconcile` antes de todo retry/resume; “sesión desaparecida ≠ fracaso ni autorización de repetir”; receipts de 002 deciden los efectos ya aplicados (`remaining-features-handoff.md:235-237`; `re-entry.md:46-50,79`).
- **D7 (S) — Split-brain.** **Recomiendo:** single-writer + `generation` monotónica; el perdedor se detiene; empate → escalar.
- **D8 (S) — Cobertura de runtimes.** **Recomiendo:** MVP **OpenCode** (subagentes nativos, un nivel) + artefactos portables; Claude Code declarado posterior, **sin** prometer paridad (`plan.md:69-72`).
- **D9 (S) — Adopción real.** **Recomiendo:** una reconstrucción automática en un **límite natural de tarea** de una feature pendiente, registrada en `continuity-ledger.md`; no terminar la feature antes para repetirla (`remaining-features-handoff.md:263-270`).
- **D10 (S) — Interacción con el protocolo de materialización de 002.** **Recomiendo:** `continuity` **consume** el receipt de 002 como oráculo y **no** materializa nada; la materialización sigue siendo del orquestador con autorización explícita (`re-entry.md:14-63`).
- **D11 (S) — Registro de decisiones.** **Recomiendo:** decisiones/incertidumbres/tareas viajan en el `--update` del `begin`/`checkpoint` y quedan congeladas en el checkpoint (con razón); la historia humana (ADRs/handoffs) sigue siendo L3.

**Bloqueantes para aprobar spec/plan:** D1, D2, D3, D4, D5, D6, D10. El resto puede cerrarse durante la spec.

---

# 4. Borrador de `spec.md`

```markdown
---
feature_id: 003-004-context-continuity
feature_name: Memoria activa, checkpoints y reanudación automática
created_at: 2026-10-07
approved_by: <pending>
approved_at: <pending>
---

# Spec: Memoria activa, checkpoints y reanudación automática

> **Draft** derivado del encargo `handoff-architect-001.md` y del brief §003-004
> (`remaining-features-handoff.md:202-276`). **Sin marca de aprobación**: requiere
> resolver D1–D11 (§8). El architect no aprueba su propia propuesta (ADR-003).

## 1. Descripción funcional

Permitir que un orquestador **rote o reanude su sesión** durante trabajo
prolongado sin pedir al usuario que repita objetivo ni autorizaciones, sin
duplicar efectos y sin cargar el historial completo: memoria activa pequeña
+ referencias íntegras recuperables (`remaining-features-handoff.md:202-209`).

Se compone de (a) una **memoria activa** acotada, reconstruible y con campos
cerrados; (b) un **checkpoint inmutable** con checksum y cadena de
proveniencia; (c) un **algoritmo de reconciliación write-ahead / posterior**
que se apoya en receipts de 002, eventos de 003 y el estado de 001. El juicio
semántico y la escritura de `docs/.cdad-state.json` permanecen en el
orquestador (`remaining-features-handoff.md:236-237`; `re-entry.md:57-63`).

Construye sobre: estado/binding de 001 (`003-001/spec.md:436-526`),
receipts/idempotencia de 002 (`003-002/closure.md:13-19`) y eventos/presupuesto
de 003 (`003-003/spec.md:219-225`). No los redefine.

## 2. Casos cubiertos y límites de observación

| Caso | Señal real (anclada) | Límite | Decisión del orquestador |
|---|---|---|---|
| Rotación antes/después de un dispatch | checkpoint L2 + `active_packet.status` + dispatch I8 (`.cdad/executions/<id>/dispatches/*.json`) | `status` de sesión no distingue vivo- estancado (VERIFY V2) | Reconstruir y continuar |
| Sesión desaparece sin entregar | dispatch I8 sin `receipt.json` en `.cdad/runtime/results/<exec>/<packet>/` | Ausencia de receipt confunde "no entregó" con "entregó por otra vía" | `dispatched-unknown`: no repetir; reanudar 1× o re-despachar con hipótesis nueva |
| Efecto ya aplicado | receipt 002 (`semantic_status=pending`) y journal de materialización | — | No duplicar; mapear `received → completed` (una transición) |
| Contexto próximo al límite | tokens de `step-finish` (`runtime-discovery.md:27-29`) | Sin límite duro observable (`runtime-discovery.md:39-41`; 003-004 V4) | Señal `prepare` sólo con contador **y** límite; si no, `unknown` + límite natural de tarea |
| Autoridad vencida / epic discordante | state `hitl_delegation` + `expires_on` (`003-001/spec.md:487-509`) | La prosa del archivo de autoridad no se parsea | Reconstruir contexto; **no** autorizar dispatch/materialize |
| Dos sesiones reanudadas | dos `ACTIVE.json` con `generation` distinta | — | Single-writer + `generation`: pierde/para la menor; empate → escalar |

**Sin señal fiable:** el estado permanece `unknown`; el paquete al orquestador
declara la limitación y **no se fabrica éxito ni fracaso**
(`remaining-features-handoff.md:43`; `003-003/spec.md:150-151`).

## 3. Contrato

### Firma propuesta (VERIFY V6 — a fijar en RED)

```text
python3 skills/cdad-cycle/scripts/cdad_continuity.py begin \
  --project-root ROOT --execution-context EXEC.json --update UPDATE.json [--json]
python3 … cdad_continuity.py checkpoint \
  --project-root ROOT --execution-context EXEC.json --update UPDATE.json [--json]
python3 … cdad_continuity.py reconcile \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID [--json]
python3 … cdad_continuity.py verify-checkpoint \
  --project-root ROOT --execution-context EXEC.json [--head | --checkpoint SHA] [--json]
python3 … cdad_continuity.py resume \
  --project-root ROOT --execution-context EXEC.json [--role ROLE] [--allow-stale] [--json]
python3 … cdad_continuity.py budget \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID [--json]
python3 … cdad_continuity.py trigger \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID [--runtime opencode] [--json]
```

`reconcile`, `verify-checkpoint`, `resume`, `budget` y `trigger` son **read-only**
y deterministas. `begin`/`checkpoint` escriben **sólo** bajo
`.cdad/executions/<execution_id>/continuity/**`, nunca `docs/.cdad-state.json`.
Éxito → `0`; violación → rc≠0 con diagnóstico por stderr **sin salida parcial**.
Los acotados por bytes (activo ≤ 16 KiB) fallan cerrado, nunca truncan.

### Postcondiciones

- **P1 (checkpoint íntegro y a prueba de tamper).** El checkpoint conserva todos
  los campos obligatorios y detecta tampering o referencias inexistentes:
  recomputar `sha256(cuerpo canónico)`, verificar `prev_checkpoint_sha256`
  (cadena) y la existencia+digest de cada `references[]`. Cualquier fallo → rc≠0.
- **P2 (reanudación útil y sin heredar autoridad).** `resume` reconstruye la
  próxima acción sin pedir al usuario repetir objetivo ni aprobaciones, y **no**
  hereda delegaciones expiradas (autoridad vencida ≠ permiso para despachar).
- **P3 (reconciliación antes de retry; sin doble efecto).** El trabajo despachado
  se reconcilia antes de cualquier reintento; efectos ya **recibidos** o
  **materializados** (receipts/journal de 002) no se duplican. Una sesión
  desaparecida no se clasifica como fracaso ni autoriza repetir.
- **P4 (presupuesto e intentos sobreviven).** Intentos y causas viven en el
  durable de 003 (keyed por `execution_id+packet_id`) y **no** se reinician al
  cambiar de sesión. Ninguna llamada gestionada se declara dentro del perfil si
  el contador de contexto no existe: se declara `null` con margen conservador.
- **P5 (restricciones de rol sobreviven).** El contexto reconstruido respeta el
  rol: `resume --role test-writer` **nunca** incluye implementación ni rutas
  fuera de su scope (aislamiento conservado; `plan.md:106-107`).
- **P6 (recorrido real + fixtures sin rehacer trabajo).** La adopción real
  incluye al menos **una reconstrucción automática** en un límite natural, más
  fixtures de crash/restart/split-brain/stale; ningún fixture rehace un trabajo
  ya cerrado ni provoca incidentes reales.
- **P7 (memoria activa pequeña y sin transcript).** El active record permanece
  bajo el cap declarado y **no** embebe transcripciones: la historia se consulta
  **por referencia** (`remaining-features-handoff.md:215-217`).

## 4. Invariantes verificables

1. El CLI es determinista y **read-only** sobre el producto; el orquestador es el
   único escritor de `docs/.cdad-state.json`; el CLI nunca aprueba.
2. Desconocido permanece desconocido; **no** se convierte bytes en tokens ni se
   fabrica un límite de contexto (`plan.md:121-126`).
3. “Sesión desaparecida” **≠** fracaso **≠** autorización de repetir
   (`remaining-features-handoff.md:236-237`).
4. Un receipt **no** es aprobación semántica; `semantic_status` siempre `pending`
   (`003-002/closure.md:13-19`).
5. Los receipts idempotentes de 002 y el presupuesto durable de 003 se
   **reutilizan**, no se redefinen (`003-003/spec.md:152-153`).
6. Sin servicio, sin agente permanente ni controlador LLM
   (`plan.md:50-51`; `remaining-features-handoff.md:35`).
7. Las restricciones por rol sobreviven a checkpoint/repackage.
8. Los límites de observabilidad del runtime se declaran; no se afirma sandbox ni
   lector inexistente (`runtime-discovery.md:60-65`; `progress-guards.md:17`).

## 5. Criterios de aceptación

1. P1–P7 verificadas por tests focales, cada test mapeado a su postcondición.
2. `verify-checkpoint` detecta por test: `sha256` alterado, eslabón de cadena
   roto, referencia inexistente y digest de referencia alterado (4 negativos).
3. `reconcile` clasifica por fixtures los seis estados de §2 (incluido
   `unknown`) y **no** repite un efecto con receipt (P3).
4. Una prueba de reanudación en frío reconstruye objetivo, decisiones con razón,
   autoridad y próxima acción **sin** volver a preguntar al usuario (P2).
5. Contexto no reportado ⇒ `trigger: unknown` y `context_used_tokens: null`
   (nunca un número fabricado) (P4).
6. Adopción real en un límite natural registrada en `continuity-ledger.md`
   (situación, evidencia `file:line`, decisión, falsas alarmas, límite, pendiente) (P6).
7. Suite del repo en verde + validadores (`tests/validate-consistency.sh`,
   `tests/validate-odoo-specialization.sh`, `scripts/validate-subagents.sh`) sin
   regresiones; ausencia de CI declarada como deuda (convención vigente).
8. Cero afirmaciones de ahorro no medido; tokens/contexto ausentes quedan `null`.

## 6. Fuera de alcance

- Redefinir estado/paquete (001), recepción/materialización (002) o
  eventos/presupuesto de intentos (003).
- Guard de progreso y clasificación de bucles (**003-003**, ya cerrada).
- Lector de sesiones por runtime, SDK/fetch, blob store, caché universal de
  evidencia, benchmark, motor de workflows.
- Garantizar un límite duro de contexto no observado; prometer paridad de
  runtimes no probada.
- Cambiar permisos, autoridad o política; nuevo epic de seguridad.

## 7. Contexto técnico (anclas)

- `docs/.cdad-state.json` + `skills/cdad-cycle/assets/state-template.json` (001).
- `skills/cdad-cycle/scripts/{cdad_packet.py,cdad_result.py,cdad_guard.py}`;
  `scripts/cdad_{packet,result,guard}.py` (wrappers del repo).
- Esquemas reutilizados: `result-receipt.schema.json`, `guard-event.schema.json`,
  `execution-context.schema.json`, `active-packet.schema.json`, `packet-metric.schema.json`.
- Stores reales: `.cdad/runtime/results/<exec>/<packet>/`,
  `.cdad/executions/<id>/{dispatches,guards}/`.
- `skills/cdad-cycle/references/{re-entry.md,state-detection.md,progress-guards.md}`.
- `docs/epics/epic-003-context-efficiency/{runtime-discovery.md,handoff*.md}`;
  ADR-011 (autonomía supervisada), ADR-003 (materialización), ADR-014, ADR-015.

## 8. Decisiones resueltas (D1–D11)

Resueltas por el orquestador bajo la delegación HITL del epic, **adoptando las
recomendaciones** de §3 del borrador (aún no cerradas al escribir este draft;
D1–D6 y D10 bloquean la aprobación).

## 9. Incertidumbres (VERIFY, no inventar)

- **V1**: ¿los tokens de `step-finish` son por paso o acumulados de sesión? (no
  verificado).
- **V2**: ¿el `status` de sesión distingue “viva pero estancada” de “terminada”?
- **V3**: ¿existe un límite duro de contexto por sesión observable en OpenCode o
  Claude Code? (no observado; `runtime-discovery.md:39-41`).
- **V4**: ¿el `--allow-stale` tiene un caso real que lo justifique o se elimina?
- **V5**: efectos de un `resume` sobre la medición de 001 (¿nuevo `packet-metric`
  de reconstrucción?) — a fijar en RED.
- **V6**: forma final del CLI y de los schemas `active-record-v1` /
  `continuity-checkpoint-v1`.

---

Status: pending approval by the owner (materializa el orquestador; ADR-003).
El architect no aprueba su propia propuesta.
```

---

# 5. Borrador de `plan.md`

```markdown
---
feature_id: 003-004-context-continuity
feature_name: Memoria activa, checkpoints y reanudación automática
created_at: 2026-10-07
status: pending-approval
approved_by: pending
approved_at: pending
---

# Plan — 003-004-context-continuity

> Borrador del arquitecto. 6 tareas pequeñas; cada una cierra su propio
> mini-ciclo RED→GREEN. El plan define el **contrato**, nunca el código
> (`stage-2-specification.md:115-119`). El plan de validación por unidad usa el
> bloque canónico `plan-tasks` de `planning-contract-draft.md` §4.1.

Principio transversal: **read-only** sobre el producto salvo
`.cdad/executions/<id>/continuity/**`; sin servicio; el juicio y la escritura
del state quedan en el orquestador.

## 1. Tareas

### T1 — Almacén de checkpoints inmutables + verificación de integridad
- **Resultado observable / postcondición:** P1.
- **Alcance incluido/excluido:** L2 create-only content-addressed + cadena
  `prev_checkpoint_sha256` + `references[]` con digest. Excluido: L1 (T2),
  write-ahead (T3).
- **Consume:** state/execution (001); esquemas existentes (001/003).
- **Produce:** `cdad-continuity-checkpoint` (contrato `continuity-checkpoint-v1`).
- **Archivos:** Create `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Create `scripts/cdad_continuity.py` (wrapper);
  Create `skills/cdad-cycle/assets/continuity-checkpoint.schema.json`;
  Test `tests/test_003_004_t1_checkpoint.py`.
- **Validación:** 4 negativos de tamper (sha alterado, cadena rota, referencia
  inexistente, digest de referencia alterado) + control verde de round-trip
  determinista (mismo input → mismo digest de bytes).
- **Detener si:** V6 (forma del schema) no se puede fijar sin ambigüedad.
- **Owner:** RED test-writer; GREEN implementer.

### T2 — Active record acotado, `resume` y aislamiento por rol
- **Resultado observable / postcondición:** P2, P5, P7.
- **Alcance incluido/excluido:** proyección L1 ≤ 16 KiB desde L2-head + receipts
  + state; `resume` con `--role`; sin transcripciones. Excluido: reconciliación (T3).
- **Consume:** `cdad-continuity-checkpoint` (`continuity-checkpoint-v1`, T1);
  receipts 002; state 001.
- **Produce:** `cdad-continuity-resume` (contrato `active-record-v1`).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Create `skills/cdad-cycle/assets/active-record.schema.json`;
  Test `tests/test_003_004_t2_active_record.py`,
  `tests/test_003_004_t2_resume.py`.
- **Validación:** reanudación en frío reconstruye objetivo/decisiones+razón/
  autoridad/próxima acción; `resume --role test-writer` no expone
  `implementation_roots` de la política; cap excedido → rc≠0 (nunca trunca).
- **Detener si:** el cap no se alcanza sin degradar información obligatoria →
  reacotar con el dueño.
- **Owner:** RED test-writer; GREEN implementer.

### T3 — Write-ahead `begin/checkpoint` + `reconcile` sin doble efecto
- **Resultado observable / postcondición:** P3.
- **Alcance incluido/excluido:** `begin` antes de dispatch; `reconcile` por
  `(execution_id, packet_id)` sobre receipts/journal/dispatch/state; clasificación
  cerrada de §2.4. Excluido: cambio de state (lo hace el orquestador) y de autoridad.
- **Consume:** L2 (T1), L1 (T2), `.cdad/runtime/results/**` y
  `materializations/**` (002), dispaches I8, `docs/.cdad-state.json` (001).
- **Produce:** `cdad-continuity-reconcile` (contrato `reconcile-v1`).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Test `tests/test_003_004_t3_writeahead.py`,
  `tests/test_003_004_t3_reconcile.py`.
- **Validación:** los 6 estados de §2.4 por fixtures; con receipt válido el CLI
  **no** ofrece repetir el efecto; autoridad vencida → no escribe checkpoint.
- **Detener si:** no se puede leer el receipt sin ambigüedad → `unknown`, escalar.
- **Owner:** RED test-writer; GREEN implementer.

### T4 — Presupuesto durable y trigger con unknowns
- **Resultado observable / postcondición:** P4.
- **Alcance incluido/excluido:** puente hacia el presupuesto de 003
  (`cdad_guard budget`) + política de perfil 200k/150k/120k. Excluido: medición de
  contexto nueva o lector de sesiones.
- **Consume:** `.cdad/executions/<id>/guards/**` y `guard_budget` (003); tokens
  reportados por el runtime (si existen).
- **Produce:** `cdad-continuity-budget` (contrato `budget-v1`) y
  `cdad-continuity-trigger` (contrato `trigger-v1`).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Test `tests/test_003_004_t4_budget_trigger.py`.
- **Validación:** nueva sesión sobre el mismo `packet_id` **no** reinicia
  intentos; sin contador/límite → `trigger: unknown` y `context_*: null`.
- **Detener si:** se pretende un número sin fuente → prohibido (invariante 2).
- **Owner:** RED test-writer; GREEN implementer.

### T5 — Fixtures de escenarios + referencia operativa
- **Resultado observable / postcondiciones:** P1, P3, P6 (parte fixtures).
- **Alcance incluido/excluido:** fixtures deterministas de crash/restart/
  split-brain/stale/autoridad vencida/tarea cerrada + guía
  `references/continuity.md`. Excluido: provocar incidentes reales; rehacer
  trabajo cerrado.
- **Consume:** contratos de T1–T4.
- **Produce:** `cdad-continuity-fixtures` (contrato `fixtures-v1`).
- **Archivos:** Test `tests/test_003_004_t5_fixtures.py`; fixtures bajo
  `tests/fixtures/003_004/**`; Create `skills/cdad-cycle/references/continuity.md`.
- **Validación:** cada fixture etiquetado **simulación**; los 6 escenarios de la
  matriz cubiertos; un escenario de trabajo legítimo progresivo **no** dispara
  rotación injustificada.
- **Regresión:** `tests/validate-consistency.sh`.
- **Owner:** RED test-writer; GREEN implementer.

### T6 — Adopción real en un límite natural de tarea
- **Resultado observable / postcondición:** P6 (adopción).
- **Alcance incluido/excluido:** una **reconstrucción automática** de sesión en
  un límite natural de una feature pendiente del epic, registrada en
  `continuity-ledger.md`. Excluido: terminar la feature antes para repetirla;
  benchmark; comparación A/B.
- **Consume:** `cdad-continuity-fixtures` (`fixtures-v1`, T5); límite natural real.
- **Produce:** `cdad-continuity-adoption` (contrato `adoption-v1`).
- **Archivos:** `docs/specs/003-004-context-continuity/continuity-ledger.md`.
- **Registro (campos obligatorios):** `situación | evidencia (file:line) |
  decisión | autoridad vigente | presupuesto (intentos/contexto o null) |
  falsas alarmas | retrabajo | pendiente`.
- **Validación:** la reconstrucción conserva decisiones y aprobaciones, reconcilia
  trabajo en curso y continúa sin repetir la tarea confirmada
  (`plan.md:165-169`).
- **Owner:** orquestador.

## 2. Prueba de no-regresión de continuidad (global)

Además de los fixtures de fallo, un escenario continuo **etiquetado simulación**:
varias llamadas y artefactos que progresan, un `reconcile` sin efecto nuevo y una
reconstrucción intermedia **no** disparan intervención ni retrabajo; la evidencia
queda en `continuity-ledger.md`.

## 3. Estimaciones (rango, método, incertidumbre)

- Rango por unidad: **bajo–medio** (T1, T4), **medio** (T2, T3, T5), **bajo**
  (T6, adopción). Método: comparación cualitativa con ciclos similares de
  003-002/003-003. Incertidumbre **alta** por V1–V6 (observabilidad del runtime).

## 4. Integración final

1. Suite completa + los tres validadores (sin regresiones; deuda de CI declarada).
2. Adopción real en un límite natural con `continuity-ledger.md` (T6).
3. Spec y plan revisados juntos por sesión independiente antes de aprobar.

## 5. Incertidumbres / replanificación

- Si V1–V6 no se resuelven, reacotar con el dueño antes de expandir
  infraestructura; no asumir APIs (`plan.md:191-197`).
- Si una unidad crece más allá de su mini-ciclo, pasa a candidata a feature propia.

```plan-tasks
{
  "validation_strategy": "focales por unidad (pytest, env -u TMPDIR) con fixtures deterministas etiquetados simulación; suite completa y validadores del repo al cierre; sin incidentes reales provocados; prueba global de continuidad sin retrabajo",
  "tasks": [
    {"id": "T1", "produce": [{"artifact": "cdad-continuity-checkpoint", "contract": "continuity-checkpoint-v1"}], "consume": [], "depends_on": [], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "scripts/cdad_continuity.py", "skills/cdad-cycle/assets/continuity-checkpoint.schema.json", "tests/test_003_004_t1_checkpoint.py"], "focal_tests": ["tests/test_003_004_t1_checkpoint.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T2", "produce": [{"artifact": "cdad-continuity-resume", "contract": "active-record-v1"}], "consume": [{"artifact": "cdad-continuity-checkpoint", "contract": "continuity-checkpoint-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "skills/cdad-cycle/assets/active-record.schema.json", "tests/test_003_004_t2_active_record.py", "tests/test_003_004_t2_resume.py"], "focal_tests": ["tests/test_003_004_t2_active_record.py", "tests/test_003_004_t2_resume.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T3", "produce": [{"artifact": "cdad-continuity-reconcile", "contract": "reconcile-v1"}], "consume": [{"artifact": "cdad-continuity-checkpoint", "contract": "continuity-checkpoint-v1", "producer": "T1"}, {"artifact": "cdad-continuity-resume", "contract": "active-record-v1", "producer": "T2"}], "depends_on": ["T1", "T2"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "tests/test_003_004_t3_writeahead.py", "tests/test_003_004_t3_reconcile.py"], "focal_tests": ["tests/test_003_004_t3_writeahead.py", "tests/test_003_004_t3_reconcile.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T4", "produce": [{"artifact": "cdad-continuity-budget", "contract": "budget-v1"}, {"artifact": "cdad-continuity-trigger", "contract": "trigger-v1"}], "consume": [{"artifact": "cdad-continuity-resume", "contract": "active-record-v1", "producer": "T2"}], "depends_on": ["T2"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "tests/test_003_004_t4_budget_trigger.py"], "focal_tests": ["tests/test_003_004_t4_budget_trigger.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T5", "produce": [{"artifact": "cdad-continuity-fixtures", "contract": "fixtures-v1"}], "consume": [{"artifact": "cdad-continuity-checkpoint", "contract": "continuity-checkpoint-v1", "producer": "T1"}, {"artifact": "cdad-continuity-resume", "contract": "active-record-v1", "producer": "T2"}, {"artifact": "cdad-continuity-reconcile", "contract": "reconcile-v1", "producer": "T3"}, {"artifact": "cdad-continuity-trigger", "contract": "trigger-v1", "producer": "T4"}], "depends_on": ["T1", "T2", "T3", "T4"], "parallel": [], "files": ["tests/test_003_004_t5_fixtures.py", "tests/fixtures/003_004/**", "skills/cdad-cycle/references/continuity.md"], "focal_tests": ["tests/test_003_004_t5_fixtures.py"], "observable_checks": ["los 6 escenarios de la matriz quedan cubiertos y etiquetados simulación; un flujo continuo legítimo no dispara rotación injustificada"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T6", "produce": [{"artifact": "cdad-continuity-adoption", "contract": "adoption-v1"}], "consume": [{"artifact": "cdad-continuity-fixtures", "contract": "fixtures-v1", "producer": "T5"}], "depends_on": ["T5"], "parallel": [], "files": ["docs/specs/003-004-context-continuity/continuity-ledger.md"], "observable_checks": ["una reconstrucción automática real en un límite natural queda registrada en continuity-ledger.md con situación, autoridad, presupuesto, falsas alarmas, retrabajo y pendiente"], "regressions": ["tests/validate-consistency.sh", "tests/validate-odoo-specialization.sh", "scripts/validate-subagents.sh"], "integration_gate": "@validation_strategy", "owner": "orquestador"}
  ]
}
```
```

---

## Nota metodológica (rol read-only)

- **Método:** solo lectura (`read`, `grep`, `glob`, `ls/cat/find` acotados). Sin `opencode run`, sin sondas, sin comandos en segundo plano. No escribí ningún archivo (el entregable viaja como texto; materializa el orquestador — ADR-003).
- **HEAD y diff:** `HEAD = c643390`; el único cambio en el árbol es el directorio **no trackeado** `docs/specs/003-004-context-continuity/` (este encargo). **Sin cambios de producto.**
- **Citas verificadas contra el repo:** contratos/schemas de 001/002/003, stores reales `.cdad/runtime/**` y `.cdad/executions/**`, referencias de skill y documentos del epic. Toda afirmación de "no existe" (contador de contexto, lector de sesiones, límite duro) proviene de los documentos citados; los puntos inciertos quedan marcados **VERIFY** (V1–V6) en lugar de asumidos.
- **Bloqueo declarado:** la aprobación de spec/plan depende de resolver **D1–D6 y D10** (§3) por el dueño/orquestador; no auto-apruebo (ADR-011, invariante anti-sesgo).
