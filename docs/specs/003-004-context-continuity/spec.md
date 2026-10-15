---
feature_id: 003-004-context-continuity
feature_name: Memoria activa, checkpoints y reanudación automática
created_at: 2026-10-07
status: approved
approved_by: orchestrator (HITL delegation epic-003)
approved_at: 2026-10-07
---

# Spec: Memoria activa, checkpoints y reanudación automática

> **Versión final** derivada de `architect-draft-001.md` aplicando
> `review-draft-001.md` con la disposición `review-draft-001-decision.md`
> (BL-1, BL-2, R1–R8, O1–O4). Las decisiones **D1–D11 están resueltas por el
> orquestador** bajo la delegación HITL del epic-003 (§8); el architect no
> aprueba su propia propuesta (ADR-003). Aprobación registrada en el frontmatter.

## 1. Descripción funcional

Permitir que un orquestador **rote o reanude su sesión** durante trabajo
prolongado sin pedir al usuario que repita objetivo ni autorizaciones, sin
duplicar efectos y sin cargar el historial completo: memoria activa pequeña +
referencias íntegras recuperables (`remaining-features-handoff.md:202-209`).

Se compone de (a) una **proyección de memoria activa** acotada, con campos
cerrados y reconstruible on-demand; (b) un **checkpoint inmutable** con checksum
y cadena de proveniencia; (c) un **algoritmo de reconciliación write-ahead /
posterior** apoyado en receipts de 002, eventos/presupuesto de 003 y el estado de
001. El juicio semántico y la escritura de `docs/.cdad-state.json` permanecen en
el orquestador (`remaining-features-handoff.md:235-237`; `re-entry.md:57-63`).

Construye sobre el estado/binding de 001 (`003-001/spec.md:436-526`), los
receipts/idempotencia de 002 (`003-002/closure.md:13-19`) y los
eventos/presupuesto de 003 (`003-003/spec.md:219-225`). No los redefine.

## 2. Casos cubiertos y límites de observación

| Caso | Señal real (anclada) | Límite | Decisión del orquestador |
|---|---|---|---|
| Rotación antes/después de un dispatch | checkpoint L2 + `active_packet.status` + dispatch I8 (`.cdad/executions/<id>/dispatches/*.json`) | `status` de sesión no distingue vivo-estancado (VERIFY V2) | Reconstruir y continuar |
| Sesión desaparece sin entregar | dispatch I8 sin `receipt.json` en `.cdad/runtime/results/<exec>/<packet>/` | Ausencia de receipt confunde "no entregó" con "entregó por otra vía" | `dispatched-unknown`: no repetir; reanudar 1× o re-despachar con hipótesis nueva |
| Efecto ya aplicado | receipt 002 (`semantic_status=pending`) y journal de materialización | — | No duplicar; mapear `received → completed` (una transición) |
| Re-begin idéntico tras crash | head existente con cuerpo canónico idéntico | — | **No-op exitoso** (rc 0, devuelve el checkpoint existente); clave `(execution_id, packet_id, attempt)` |
| Contexto próximo al límite | tokens de `step-finish` (`runtime-discovery.md:27-29`) | Sin límite duro observable (`runtime-discovery.md:39-41`; VERIFY V1/V3) | Señal `prepare` sólo con contador **y** límite; si no, `unknown` + límite natural de tarea |
| Autoridad vencida / epic discordante | state `hitl_delegation` + `expires_on` (`003-001/spec.md:487-509`) | La prosa del archivo de autoridad no se parsea (`003-001/spec.md:500-501`) | Reconstruir contexto; **no** autorizar dispatch/materialize |
| Dos sesiones reanudadas (split-brain) | cabezas de checkpoint divergentes o igual-sha-con-cuerpo-distinto | — | **Escalar**; sólo un escritor (el orquestador) encadena checkpoints |

**Sin señal fiable:** el estado permanece `unknown`; el paquete al orquestador
declara la limitación y **no se fabrica éxito ni fracaso** (`003-003/spec.md:150-151`).
Un `ACTIVE.json` persistido **no** existe: la memoria activa es una proyección
on-demand desde la cabeza L2 (O1), por lo que su ausencia no es error de
`reconcile` ni de `resume`.

## 3. Contrato

### Firma (VERIFY V6 — a fijar en RED)

```text
python3 skills/cdad-cycle/scripts/cdad_continuity.py begin \
  --project-root ROOT --execution-context EXEC.json --update UPDATE.json \
  [--max-bytes N] [--json]
python3 … cdad_continuity.py checkpoint \
  --project-root ROOT --execution-context EXEC.json --update UPDATE.json \
  [--max-bytes N] [--json]
python3 … cdad_continuity.py reconcile \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID [--json]
python3 … cdad_continuity.py resume \
  --project-root ROOT --execution-context EXEC.json [--role ROLE] [--max-bytes N] [--json]
python3 … cdad_continuity.py trigger \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID \
  [--runtime opencode] [--json]
```

`reconcile`, `resume` y `trigger` son **read-only** y deterministas.
`begin`/`checkpoint` escriben **sólo** bajo
`.cdad/executions/<execution_id>/continuity/**`, nunca `docs/.cdad-state.json`.
Tres contratos con nombre: `continuity-checkpoint-v1` (checkpoint + cuerpo de la
memoria activa + render de `resume`), `reconcile-v1`, `trigger-v1`.
`--max-bytes` es configurable (default 16 KiB); el exceso **falla cerrado sin
truncar** (rc≠0). No hay subcomando `verify-checkpoint` ni `budget` propio:
tamper/referencias se verifican en `resume`/`reconcile`, y el presupuesto de
intentos se consulta con `cdad_guard budget`.

### Postcondiciones

- **P1 (checkpoint íntegro y a prueba de tamper).** `resume`/`reconcile`
  verifican `sha256(cuerpo canónico)`, el eslabón `prev_checkpoint_sha256` y la
  existencia+digest de cada `references[]`. Cualquier fallo (sha alterado, cadena
  rota, referencia inexistente, digest de referencia alterado) → rc≠0 con el
  delta exacto.
- **P2 (reanudación útil y sin heredar autoridad).** `resume` reconstruye
  objetivo, decisiones con razón, autoridad e incertidumbres y la próxima acción
  sin pedir al usuario repetir objetivo ni aprobaciones, y **no** hereda
  delegaciones expiradas: autoridad vencida puede reconstruir contexto pero no
  autorizar dispatch/materialize.
- **P3 (reconciliación antes de retry; sin doble efecto).** El trabajo despachado
  se reconcilia antes de cualquier reintento; efectos ya **recibidos** o
  **materializados** (receipts/journal de 002) no se duplican. Una sesión
  desaparecida no se clasifica como fracaso ni autoriza repetir. Un `begin` con
  cuerpo canónico idéntico al head es **no-op** (rc 0).
- **P4 (presupuesto de intentos durable).** Intentos y causas se leen del durable
  de 003 (`.cdad/executions/<id>/guards/**`, clave
  `execution_id+packet_id+attempt`) y **no** se reinician al cambiar de sesión.
- **P5 (restricciones de rol sobreviven).** `resume --role test-writer` **nunca**
  incluye implementación ni rutas fuera del scope del rol (aislamiento
  conservado; `plan.md:106-107`).
- **P6 (trigger con unknowns, sin límite fabricado).** `trigger` sólo devuelve
  `prepare`/`rotate` si `context_used_tokens` **y** `context_limit` son enteros;
  en cualquier otro caso `trigger: unknown`, `context_*: null` y `unknowns[]`
  explícitos. **Prohibido** convertir bytes en tokens o presentar un proxy como
  límite (`plan.md:121-126`).
- **P7 (memoria activa pequeña y sin transcript).** La proyección respeta
  `--max-bytes` (default 16 KiB); no embebe transcripciones — la historia se
  consulta **por referencia** (`remaining-features-handoff.md:215-217`); exceder
  el cap falla cerrado, nunca trunca.
- **P8 (recorrido real + fixtures sin rehacer trabajo).** La adopción real
  incluye al menos **una reconstrucción automática** en un límite natural; los
  fixtures cubren crash/restart/split-brain/stale/autoridad vencida/tarea cerrada
  sin rehacer un trabajo ya cerrado ni provocar incidentes reales.

## 4. Invariantes verificables

1. El CLI es determinista y **read-only** sobre el producto salvo
   `.cdad/executions/<id>/continuity/**`; el orquestador es el único escritor de
   `docs/.cdad-state.json`; el CLI nunca aprueba.
2. Desconocido permanece desconocido; **no** se convierte bytes en tokens ni se
   fabrica un límite de contexto (`plan.md:121-126`).
3. "Sesión desaparecida" **≠** fracaso **≠** autorización de repetir
   (`remaining-features-handoff.md:235-237`).
4. Un receipt **no** es aprobación semántica; `semantic_status` siempre `pending`
   (`003-002/closure.md:13-19`).
5. Los receipts idempotentes de 002 y el presupuesto durable de 003 se
   **reutilizan**, no se redefinen (`003-003/spec.md:152-153`).
6. Sin servicio, sin agente permanente ni controlador LLM (`plan.md:50-51`).
7. Las restricciones por rol sobreviven a checkpoint/repackage.
8. Los límites de observabilidad del runtime se declaran; no se afirma sandbox ni
   lector inexistente (`runtime-discovery.md:60-65`; `progress-guards.md:17`).

## 5. Criterios de aceptación

1. P1–P8 verificadas por tests focales, cada test mapeado a su postcondición.
2. `resume`/`reconcile` detectan por test los cuatro negativos de P1 (sha alterado,
   cadena rota, referencia inexistente, digest de referencia alterado).
3. `begin` idéntico al head es no-op con rc 0; un `begin` divergente con la misma
   clave `(execution_id, packet_id, attempt)` se reporta como conflicto/escalado
   (no sobrescribe, no duplica cadena).
4. `reconcile` clasifica por fixtures los estados de §2 (incluido `unknown`), no
   repite un efecto con receipt y no falla por ausencia de `ACTIVE.json` (P3).
5. Una reanudación en frío reconstruye objetivo, decisiones con razón, autoridad y
   próxima acción **sin** volver a preguntar al usuario (P2).
6. Sesión nueva sobre el mismo `packet_id` **no** reinicia intentos (P4).
7. Contexto no reportado ⇒ `trigger: unknown` y `context_used_tokens: null`
   (nunca un número fabricado) (P6).
8. Exceder `--max-bytes` falla cerrado sin truncar (P7).
9. Adopción real en un límite natural registrada en `continuity-ledger.md`
   (situación, evidencia `file:line`, decisión, autoridad vigente, presupuesto,
   falsas alarmas, retrabajo, pendiente) (P8).
10. Suite del repo en verde + validadores (`tests/validate-consistency.sh`,
    `tests/validate-odoo-specialization.sh`, `scripts/validate-subagents.sh`) sin
    regresiones; ausencia de CI declarada como deuda (convención vigente).
11. Cero afirmaciones de ahorro no medido; tokens/contexto ausentes quedan `null`.

## 6. Fuera de alcance

- Redefinir estado/paquete (001), recepción/materialización (002) o eventos y
  presupuesto de intentos (003); un subcomando `budget` propio (R3).
- Guard de progreso y clasificación de bucles (**003-003**, ya cerrada).
- Lector de sesiones por runtime, SDK/fetch, blob store, caché universal de
  evidencia, benchmark, motor de workflows.
- Garantizar un límite duro de contexto no observado; prometer paridad de
  runtimes no probada.
- Cambiar permisos, autoridad o política; nuevo epic de seguridad.

## 7. Contexto técnico (anclas)

- `docs/.cdad-state.json` + `skills/cdad-cycle/assets/state-template.json` (001).
- `skills/cdad-cycle/scripts/{cdad_packet.py,cdad_result.py,cdad_guard.py}`;
  wrappers `scripts/cdad_{packet,result,guard}.py`.
- Esquemas reutilizados: `result-receipt.schema.json`, `guard-event.schema.json`,
  `execution-context.schema.json`, `active-packet.schema.json`,
  `packet-metric.schema.json`.
- Stores reales: `.cdad/runtime/results/<exec>/<packet>/`,
  `.cdad/executions/<id>/{dispatches,guards}/`.
- `skills/cdad-cycle/references/{re-entry.md,state-detection.md,progress-guards.md}`
  y la nueva `continuity.md` (T3 del plan).
- `docs/epics/epic-003-context-efficiency/{runtime-discovery.md,handoff*.md}`;
  ADR-011 (autonomía supervisada), ADR-003 (materialización), ADR-014, ADR-015.

## 8. Decisiones resueltas (D1–D11)

Resueltas por el **orquestador** bajo la delegación HITL del epic-003
(`review-draft-001-decision.md`), adoptando las recomendaciones del architect
salvo donde se indica:

| ID | Decisión resuelta |
|---|---|
| **D1** | CLI determinista `cdad_continuity.py` (Python stdlib) + wrapper `scripts/cdad_continuity.py`; read-only sobre el producto; escribe sólo bajo `.cdad/executions/<id>/continuity/**`; sin servicio ni agente permanente (`plan.md:50-51`) |
| **D2** | Tres capas: L2 checkpoint inmutable = autoridad de delegación/decisiones/presupuesto; L1 = proyección on-demand (no persistida, O1); L3 = referencias a la historia existente (state/stage_history, receipts 002, eventos 003, dispatches I8, Memory Bank). Sin log ni schema de estado nuevos |
| **D3** | El CLI nunca escribe `docs/.cdad-state.json`; un solo escritor del state = el orquestador (`re-entry.md:57-63`) |
| **D4** | Autoridad y vigencia se leen del estado estructurado (`hitl_delegation` + `authority_ref`); no se parsea la prosa (`003-001/spec.md:500-501`). Autoridad vencida reconstruye contexto pero no autoriza efectos |
| **D5** | Trigger = **señal**, no límite duro; `prepare_at=120k` sólo con contador y límite reales; si no, `unknown` + límite natural de tarea |
| **D6** | Write-ahead `begin` antes de despachar; `reconcile` antes de todo retry/resume; receipts de 002 deciden efectos ya aplicados; sesión desaparecida ≠ fracaso ni autorización de repetir |
| **D7** | Split-brain por **cabezas divergentes**: sin contador `generation`; un solo `seq` monotónico; cabeza divergente o igual-sha-con-cuerpo-distinto → escalar (R2) |
| **D8** | MVP OpenCode (subagentes nativos, un nivel) + artefactos portables; Claude Code posterior, sin prometer paridad (`plan.md:69-72`) |
| **D9** | Adopción real en un **límite natural de tarea** de una feature pendiente, registrada en `continuity-ledger.md`; no terminar la feature antes para repetirla (`remaining-features-handoff.md:265-270`) |
| **D10** | `continuity` **consume** el receipt de 002 como oráculo y **no** materializa; la materialización sigue siendo del orquestador con autorización explícita (`re-entry.md:46-63`) |
| **D11** | Decisiones/incertidumbres/tareas viajan en `--update` y quedan congeladas en el checkpoint (con razón); la historia humana (ADRs/handoffs) sigue siendo L3 |

## 9. Incertidumbres (VERIFY, no inventar)

- **V1**: ¿los tokens de `step-finish` son por paso o acumulados de sesión? (no
  verificado).
- **V2**: ¿el `status` de sesión distingue "viva pero estancada" de "terminada"?
- **V3**: ¿existe un límite duro de contexto por sesión observable en OpenCode o
  Claude Code? (no observado; `runtime-discovery.md:39-41`).
- **V4**: `--allow-stale` **eliminado** (O3): stale → rc≠0 con el delta exacto.
- **V5**: efectos de un `resume` sobre la medición de 001 (¿nuevo `packet-metric`
  de reconstrucción?) — a fijar en RED.
- **V6**: forma final del CLI y de los esquemas `continuity-checkpoint-v1`,
  `reconcile-v1`, `trigger-v1` (a fijar en RED).

---

Status: Approved by orchestrator (HITL delegation epic-003) on 2026-10-07.
