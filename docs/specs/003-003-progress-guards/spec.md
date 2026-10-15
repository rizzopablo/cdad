---
feature_id: 003-003-progress-guards
feature_name: Guards de progreso y recuperación acotada
created_at: 2026-10-06
status: approved
approved_by: Pablo (HITL delegada al orquestador Claude)
approved_at: 2026-10-06
---

# Spec: Guards de progreso y recuperación acotada

> **Versión final** derivada de `architect-draft-001.md` aplicando
> `review-draft-001.md`: F2 (citas re-apuntadas al archivo correcto —
> `handoff-architect-001.md` en vez de `remaining-features-handoff.md` y
> `plan.md:86` en vez de `plan.md:37`), O1 (`steps:300` no ejercitado en vivo),
> O2 (el pre-flight **lee** la política, no la escribe) y O3 (clave de dedup
> explícita en `guards-ledger.md`), más la **fusión de tareas 7→5** (§4).
> Las decisiones **D1–D11 quedan resueltas** por el orquestador bajo la
> delegación HITL del epic (ver §8). El architect no aprueba su propia
> propuesta (ADR-003); la materialización y aprobación las ejecuta el
> orquestador/dueño.

## 1. Descripción funcional

Detectar y resolver interrupciones y repeticiones improductivas en desarrollos
reales, preservando autonomía y utilidad, sin reconstruir restricciones rígidas
ni crear un supervisor que consuma más que el trabajo que evita.

La capacidad se compone de (a) un analizador determinista **read-only** sobre las
señales ya existentes (DB de sesiones de OpenCode + artefactos de 001/002), que
emite **incidentes y eventos durables**; y (b) una **tabla cerrada evento→acción**
que el orquestador usa para decidir. El juicio semántico permanece en el
orquestador; el guard no es orquestador estratégico
(`remaining-features-handoff.md:130-144`). Vigila también agentes auxiliares y
sesiones reanudadas (`remaining-features-handoff.md:132-133`).

Construye sobre: techo `steps:300` ya desplegado como runaway mecánico, receipts/
idempotencia de 002, estado/medición de 001. No los redefine.

## 2. Casos cubiertos y distinciones (señal anclada, verificada contra el repo)

### Fuentes de señal

| Señal | Fuente real | Notas |
|---|---|---|
| Llamadas de herramienta por agente/rol/herramienta/verbo | DB OpenCode read-only `~/.local/share/opencode/opencode.db`, tablas `session_v2` + `session_message`; `content[].type=="tool"`, `name`, `state.input`, `error.type=="permission.rejected"` | Patrón ya probado: `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/opencode-session-scan.py:21-54` |
| Hijos/auxiliares y sesiones reanudadas | `session_v2.parent_id is not null` (scan:23) + API `children`/`fork` (`runtime-discovery.md:23-25`) | Cubre auxiliares y reanudadas |
| Identidad de sesión por paso | `session_message` (mensajes con `agent` y `content`) → conteo de steps | scan:34-41,62-65 |
| Intento despachado (durable) | `.cdad/executions/<execution_id>/dispatches/<attempt>.json` (I8): `packet_id`, `role`, `substage`, `runtime`, `session`, `model_configured/reported`, `started_at` | Ej. real `.cdad/executions/exec-004-002-project-execution-bootstrap-001/dispatches/review-009-a1.json` |
| Ciclo de vida del paquete | `docs/.cdad-state.json` → `active_packet.status ∈ prepared|dispatched|completed|failed` | `docs/specs/003-001-role-packets/spec.md:478-480`; single-writer = orquestador (001) |
| Reintentos/tokens/límite reportados | `packet-metric.schema.json` (`retry_count`, `input/output_tokens`, `context_limit`, `outcome`), unknowns en `null` | `docs/specs/003-001-role-packets/spec.md:560-568`; `additionalProperties:false`: no inventar campos |
| Efectos ya aplicados (anti-duplicado) | Receipts/journal de 002 (`.cdad/runtime/results/<exec>/…`, `materializations/…`); `semantic_status` siempre `pending` | `docs/specs/003-002-artifact-tools/closure.md:13-19`; reutilizar, no redefinir |
| Tokens/modelos/tiempo reportados | Mensajes/`step-finish` con tokens, modelo/proveedor, tiempos y costo reportado | `runtime-discovery.md:27-29`; costo ≠ facturación |
| Registro humano de despachos | `docs/specs/*/dispatch-ledger.md` | Fuente de incidentes reales |

### Casos prioritarios

| Caso | Señal disponible | Límite de observación | Decisión que necesita el orquestador | Recuperación mínima |
|---|---|---|---|---|
| **C1. Un agente termina sin entregar resultado utilizable** | `active_packet.status` sigue `dispatched`; no existe receipt para `(execution_id, packet_id)`; el artefacto `produce` no aparece; el cliente `opencode run` retornó pero la sesión sigue viva; `time_created` del último mensaje no avanza | "Sin reporte final" no es un campo estructurado: el mensaje final puede venir en otro idioma o confuso (`friction-intake-004-001.md:42-44,64-68`). Ausencia de receipt confunde "no entregó" con "entregó por otra vía". Sesión "viva" puede estar estancada (ECONNRESET + auto-resume, `friction-intake-004-001.md:44-48`) | ¿Sigue siendo productivo (mensajes/steps avanzan en tiempo) o terminó sin resultado? Si terminó: clasificar (crash / límite de proveedor / fallo silencioso de herramienta) y elegir reanudar vs. redespachar con diagnóstico | **Esperar sobre la DB de sesiones, no sobre el cliente** (`docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/results.md:37-39`). Preservar trabajo parcial y evidencia antes de decidir. Reconciliar efectos (receipt 002) antes de cualquier retry. Reanudar la misma sesión 1 vez; redespachar solo con hipótesis/información nueva |
| **C2. Una ejecución iniciada por el agente muere al terminar su sesión** | El proceso en background (p. ej. suite) no deja artefacto de evidencia; la sesión termina; no hay `run-evidence`/snapshot de esa corrida | La DB **no expone** el proceso hijo del SO ni su exit code; "murió" solo se infiere por ausencia de evidencia durable, y esa ausencia es débil (podría estar pendiente). El guard no puede observar un proceso que no controla | ¿Existe corrida registrada y equivalente para citar? ¿O hay que re-ejecutar? ¿El efecto material ya se aplicó (receipt/journal de 002)? | Citar la corrida registrada si la equivalencia se demuestra (producto+tests+selección+entorno, `re-entry.md:67-79`; aplicado ~10× en `evidence-utility-2026-10-05.md:15-21`). Si no hay corrida válida: re-ejecutar **una vez en primer plano**. Nunca duplicar un efecto ya recibido. **Incidente real: 5 ocurrencias** (`evidence-utility-2026-10-05.md:50-54`; `docs/specs/004-003-planning-procedures/dispatch-ledger.md:16`) |
| **C3. Se repiten llamadas, errores o intentos sin información nueva** | Mismas llamadas (`name` + input canonicalizado) con la misma clase de resultado (`error.type=="permission.rejected"`, error de herramienta, salida vacía) ×N; `retry_count`/`outcome` en la métrica; `dispatches/*.json` repetidos | La equivalencia exige canonicalizar; la DB no documenta de forma completa el contenido/exit del resultado (§V1). Hash del output completo es frágil (`remaining-features-handoff.md:191-192`). "Sin información nueva" requiere una señal de progreso (git/artefacto/state) que la DB **no** trae. Relectura justificada, test flaky y nueva hipótesis se ven idénticos a nivel llamada | ¿Reconsiderar estrategia (regla de dos intentos) o es fricción del entorno? ¿Desvío del agente o fallo de herramienta/política? Ambigüedad → paquete breve al orquestador | Retry **solo con un cambio**; conservar evidencia; no reintentos ilimitados (`re-entry.md:79`). **Incidente real: 2.073 reintentos idénticos, ~20 h, costo 15,86 vs ~0,14 normal** (`docs/specs/opencode-read-map-and-steps-2026-09-29/spec.yaml:18-23`). El techo `steps:300` **puede** cortar el runaway mecánico, pero su enforcement **no fue ejercitada en vivo** (`docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/results.md:24`; V5): el guard **observa y registra**, no lo reimplementa |
| **C4. Un obstáculo de capacidades/permisos impide trabajo legítimo y provoca rodeos** | `permission.rejected` por herramienta/agente/verbo (scan:46-52); evidencia de salida de ámbito en el ledger (implementer corrió `install.sh` sobre HOME real; test-writer `git stash`) (`friction-intake-004-001.md:52-61`) | La DB muestra el deny pero no la intención/objetivo: **un rechazo no es mala conducta** (`handoff-architect-001.md:38`). Legitimidad exige objetivo/scope del rol (del paquete/execution, no del DB). Pre-flight no puede afirmar un sandbox inexistente (`runtime-discovery.md:60-65`; `docs/adr/ADR-011-autonomia-supervisada-limites-proporcionales.md:75-79`; `docs/specs/004-002-project-execution-bootstrap-001/t7-live-walk.md:38-66`: grep/glob se median por patrón, no por ruta) | Clasificar por **objetivo, rol, scope y efecto**, no por nombre de comando (`remaining-features-handoff.md:139-141`). ¿Es defecto del producto (deny de operación legítima) o fuera de rol? Escalar síntesis accionable; **no** conceder ni endurecer permisos automáticamente por un contador (`remaining-features-handoff.md:141`) | Sin loop ilimitado de la misma llamada denegada. Prevalidar contra `docs/cdad-policy.json` + mapa de rol. Si es defecto del producto, escalar con repro; re-encauzar al rol a la alternativa declarada sin cambiar autoridad. Un rechazo legítimo es **defecto a corregir en la fuente**, no métrica a optimizar (`friction-intake-004-001.md:13-14`) |

### Distinciones (no-alarma)

| Distinción | Cómo se separa (evidencia observable) |
|---|---|
| **Ejecución larga pero saludable** | `time_created` de mensajes avanza, hay steps/mensajes nuevos y artefactos/state cambian → **sin alerta** (`friction-intake-004-001.md:44-48`) |
| **Polling justificado** | Condición esperada + deadline + cadencia declarados → no cortar antes del vencimiento; al vencer, escalar **una sola vez** (`remaining-features-handoff.md:175-176,180-181`) |
| **Nueva iteración por hipótesis distinta** | Cambian args/fingerprint o clase de resultado y hay progreso → no es repetición equivalente (regla de dos intentos, `re-entry.md:79`) |

### Sin señal fiable

Cuando el runtime no expone la señal (tokens por sesión, exit de subproceso,
semántica de `status`): el estado **permanece `unknown`**, el paquete al
orquestador declara explícitamente la limitación y **no se fabrica éxito ni
fracaso** (`handoff-architect-001.md:43`;
`docs/epics/epic-004-single-source-planning/planning-contract-draft.md:208-209`).
La ausencia de incidentes no activa relajaciones automáticas.

## 3. Contrato

### Firma propuesta (VERIFY V7 — a fijar en RED)

```text
python3 skills/cdad-cycle/scripts/cdad_guard.py observe \
  --project-root ROOT [--execution-context EXEC.json] \
  [--runtime opencode] [--since RFC3339] [--until RFC3339] [--json]

python3 skills/cdad-cycle/scripts/cdad_guard.py classify \
  --project-root ROOT --trace TRACE.json      # trazas grabadas / fixtures

python3 skills/cdad-cycle/scripts/cdad_guard.py preflight \
  --project-root ROOT --execution-context EXEC.json --role ROLE [--operation OP] [--json]

python3 skills/cdad-cycle/scripts/cdad_guard.py budget \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID

python3 skills/cdad-cycle/scripts/cdad_guard.py record \
  --project-root ROOT --event EVENT.json
```

`observe`/`classify`/`preflight` son **read-only** y deterministas; `record`
escribe solo bajo `.cdad/` (nunca `docs/.cdad-state.json`). Éxito → `0`;
violación → rc≠0 con diagnóstico por stderr y sin salida parcial. Los schemas de
evento/presupuesto se validan en RED (§V7). `preflight` **lee**
`docs/cdad-policy.json`; no lo modifica (O2).

### Postcondiciones

- **P1 (repetición sin progreso).** Con N llamadas equivalentes y cero progreso
  observable, el guard las detecta con una **regla explícita** y emite evidencia
  de **por qué** son equivalentes (fingerprint + clase de resultado + ausencia de
  cambio en artefacto/state/git). Sin regla explícita, no hay detección.
- **P2 (polling legítimo).** Un polling con condición, deadline y cadencia
  válidos **no se corta** antes del vencimiento; al vencer, escala **una sola vez**.
- **P3 (rechazos acotados).** Los rechazos de permiso/capacidad se prevalidan
  contra la política y el rol o se acotan; **nunca** existe loop ilimitado de la
  misma llamada denegada.
- **P4 (presupuesto durable).** Cada recuperación consume presupuesto durable y
  produce receipt/evento; un restart o una sesión nueva **no** lo reinicia.
  Reanudar conserva intentos y causas anteriores.
- **P5 (ambigüedad → orquestador).** La ambigüedad o la necesidad de decisión
  semántica vuelve al orquestador con un paquete breve y accionable, sin decisión
  autónoma encubierta. Ausencia de señal fiable ⇒ `unknown` explícito, sin
  fabricar éxito ni fracaso.
- **P6 (fixtures de trazas).** Fixtures de trazas cubren bucle, progreso real,
  polling, flaky y crash, **sin repetir un desarrollo completo**; los escenarios
  de fallo provocado se etiquetan como **simulación**.
- **P7 (sin falsos positivos / sin alertas repetidas).** Un trabajo legítimo y
  progresivo **puede continuar**: la intervención solo ocurre bajo condiciones
  claras y proporcionadas; el mismo incidente sin cambio relevante **no** vuelve
  a alertar. La re-alerta exige un **cambio en el token de relevancia** (digest de
  progreso en git/artefacto/state) o un cambio en la clase de la huella (O3).
- **P8 (generalidad y adopción).** La capacidad funciona para proyectos Go
  (tests co-ubicados) y ciclos sin código; se adopta en un **límite de tarea
  real** y registra su uso real (situación, evidencia, decisión, falsas alarmas,
  costo, pendiente).

## 4. Invariantes verificables

1. El guard es determinista y **read-only** sobre el producto; el orquestador es
   el único escritor del estado; el guard nunca cambia spec, autoridad ni prioridad.
2. Un rechazo de permisos **no** implica mala conducta; **no** se conceden ni
   endurecen permisos automáticamente por un contador (`handoff-architect-001.md:38,141`;
   ADR-011).
3. Falta de progreso **≠** contar herramientas o tokens (`handoff-architect-001.md:36`);
   **un timeout solo no prueba bloqueo** (`handoff-architect-001.md:39`).
4. Desconocido permanece desconocido; la ausencia de incidentes **no** activa
   relajaciones automáticas (`handoff-architect-001.md:43`).
5. Se reutilizan los contratos de 001/002 sin redefinirlos; un receipt **no** es
   aprobación semántica (`docs/specs/003-002-artifact-tools/closure.md:13-19`).
6. Sin agente permanente ni servicio nuevo sin justificación concreta; sin
   controlador LLM (`handoff-architect-001.md:35`; `plan.md:50-51`).
7. Se conserva resultado parcial y evidencia **antes** de recuperar/reintentar
   (`handoff-architect-001.md:40`).
8. Las interfaces declaradas **no obstaculizan** la continuidad de contexto de
   003-004 (evento/presupuesto keyed por `execution_id`, sin truncar contratos,
   `handoff-architect-001.md:47`; `plan.md:86`;
   `remaining-features-handoff.md:223-224`).
9. No se duplica el techo mecánico `steps:300` ya desplegado; su enforcement no
   está ejercitada en vivo (`docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/results.md:24`).
10. Los límites de observabilidad del runtime se declaran; no se afirma sandbox
    inexistente (`runtime-discovery.md:60-65`; `docs/adr/ADR-011-...md:75-79`)
    ni mediación de procesos que el guard no controla.
11. Una reanudación conserva intentos y causas anteriores
    (`handoff-architect-001.md:42`).

## 5. Criterios de aceptación

1. P1–P8 verificadas por tests focales (o `observable_checks` en ciclos sin
   código), cada test mapeado a su postcondición.
2. Escenario de "trabajo legítimo que progresa" en verde y **sin intervención**
   (P7); falsas alarmas registradas con su causa.
3. Escenarios de fallo controlado (bucle, polling, deny, crash, flaky) probados
   sobre trazas grabadas y **etiquetados como simulación**; ningún incidente real
   provocado en proyectos reales (`plan.md:173-176`).
4. Reanudación: intentos y causas sobreviven al cambio de sesión (P4), verificado
   empíricamente.
5. Integración en un límite de tarea real, con `guards-ledger.md` que registra
   situación, evidencia, decisión, falsas alarmas, costo, pendiente y
   `dedup_key` (P8, O3).
6. Suite del repo en verde + validadores (`tests/validate-consistency.sh`,
   `tests/validate-odoo-specialization.sh`, `scripts/validate-subagents.sh`) sin
   regresiones; ausencia de CI declarada como deuda (convención vigente).
7. Cero afirmaciones de ahorro no medido; tokens/contexto ausentes quedan `null`.

## 6. Fuera de alcance

- Renovación de contexto, checkpoints y reconstrucción automática (**003-004**).
- Recepción/persistencia/deduplicación de resultados (**003-002**, ya cerrada).
- Motor general de workflows; cache universal de evidencia; benchmark.
- Endurecer o conceder permisos automáticamente; nuevo epic de seguridad.
- Cualquier afirmación de sandbox o de mediación de procesos no observados.

## 7. Contexto técnico (anclas)

- `skills/cdad-cycle/scripts/cdad_packet.py` (001: state/medición/packet).
- `skills/cdad-cycle/scripts/cdad_result.py` (002: receipt/journal/idempotencia).
- `docs/.cdad-state.json`, `skills/cdad-cycle/assets/{packet-metric,state-template}.json`.
- `docs/cdad-policy.json` (path_policy) — **leído**, no escrito; `.cdad/executions/<id>/dispatches/*.json`.
- `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/opencode-session-scan.py`
  (patrón read-only a promover; no importar el archivo como producto).
- `docs/epics/epic-003-context-efficiency/runtime-discovery.md` (observabilidad).
- `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4/§4.1.
- ADR-011 (autonomía supervisada), ADR-003 (materialización), ADR-013 (plan borrador).

## 8. Decisiones resueltas (D1–D11)

Resueltas por el orquestador bajo la delegación HITL del epic, **adoptando las
recomendaciones del borrador** (ya no bloquean la aprobación):

| ID | Decisión resuelta | Ancla |
|---|---|---|
| **D1** | CLI determinista `cdad_guard.py` (Python stdlib), **read-only** sobre la DB de OpenCode y los artefactos 001/002, que emite eventos durables bajo `.cdad/`; sin agente permanente ni servicio nuevo; el juicio queda en el orquestador | `handoff-architect-001.md:34-35` |
| **D2** | Huella canónica = `herramienta + argumentos canonicalizados (solo campos estables) + clase de resultado cerrada`; evidencia original **por referencia**, nunca hash del output completo | `remaining-features-handoff.md:158-160,191-192` |
| **D3** | El umbral es **señal para reconsiderar estrategia**, no prueba de incumplimiento; regla conservadora y explícita; `steps:300` sigue siendo el único techo mecánico; sin auto-bloqueo duro nuevo | `handoff-architect-001.md:37`; `re-entry.md:79` |
| **D4** | Presupuesto durable bajo `.cdad/executions/<execution_id>/guards/…`, keyed por `execution_id+packet_id+attempt`; el guard **no** escribe `docs/.cdad-state.json` (single-writer = orquestador); reanudar **no** reinicia contadores | `docs/specs/003-002-artifact-tools/closure.md:53`; `docs/epics/epic-004-single-source-planning/planning-contract-draft.md:213-216` |
| **D5** | Tabla cerrada evento→acción con solo acciones reversibles y proporcionadas (backoff/poll, retry con cambio, repackage, nueva sesión desde checkpoint, escalar, recomendar-bloqueo); ambigüedad → paquete breve al orquestador; el guard **nunca** cambia spec, autoridad ni prioridad | `remaining-features-handoff.md:166-168`; `handoff-architect-001.md:44` |
| **D6** | Pre-flight determinista sobre `docs/cdad-policy.json` + mapa de rol + execution context (detectar antes de llamar una operación declarada denegada o fuera de raíz); **sin afirmar sandbox inexistente**; es lectura, no escritura de la política | `remaining-features-handoff.md:161-163`; `runtime-discovery.md:60-65` |
| **D7** | El guard **no** repite efectos; consulta receipt/journal de 002 para saber si la acción terminó; "comprobar si terminó antes de repetir" se satisface **reconciliando**; el guard solo señala | `handoff-architect-001.md:41`; `docs/specs/003-002-artifact-tools/closure.md:13-19` |
| **D8** | Integración concreta **OpenCode** (lo que el epic pide); el analizador opera sobre artefactos portables; Claude Code se declara posterior, sin prometer paridad no probada | `plan.md:85`; `plan.md:69-72` |
| **D9** | `observable_checks` en vez de `focal_tests` para ciclos sin código; fixtures con tests co-ubicados Go y un ciclo documental | `docs/epics/epic-004-single-source-planning/planning-contract-draft.md:132-137`; `handoff-architect-001.md:48` |
| **D10** | Declarar solo interfaces que **no obstaculicen** la rotación de contexto de 003-004 (schema de evento/presupuesto estable, keyed por `execution_id`, sin truncar); **no** implementar checkpoints ni reconstrucción automática | `handoff-architect-001.md:47`; `plan.md:86`; `remaining-features-handoff.md:223-224` |
| **D11** | Adopción en un **límite de tarea real** del epic y registro por situación en `guards-ledger.md` (situación, evidencia, decisión, falsas alarmas, costo, pendiente, **`dedup_key`**); sin alertas repetidas del mismo incidente sin cambio relevante | `handoff-architect-001.md:54-56,45` |

## 9. Incertidumbres (VERIFY, no inventar)

- **V1**: ¿la DB `session_message` expone contenido/exit-clase del resultado de
  herramienta más allá de `permission.rejected`? (hoy solo ese tipo está probado).
- **V2**: ¿el `status` de sesión distingue "viva pero estancada" de "terminada"?
- **V3**: ¿se puede observar/abortar hijos de una sesión muerta sin incidentes?
- **V4**: ¿existe límite duro de contexto por sesión observable? (no observado).
- **V5**: La *enforcement* de `steps:300` **no está ejercitada en vivo**
  (`docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/results.md:24`).
- **V6**: aislamiento de OpenCode: resolver la lectura de config heredada que
  invalidó el smoke **antes** de cualquier sonda en vivo o envío a proveedores
  (`handoff-architect-001.md:169-170`; `runtime-discovery.md:60-65`).
- **V7**: forma final del schema de evento/presupuesto y del CLI (draft §3).

---

Status: pending approval by the owner (materializa el orquestador; ADR-003). D1–D11 resueltas por el orquestador (delegación HITL del epic); el architect no aprueba su propia propuesta.
