# 1. Tabla de casos (señal / límite de observación / decisión / recuperación)

## Fuentes de señal ancladas (verificadas contra el repo)

| Señal | Fuente real | Notas |
|---|---|---|
| Llamadas de herramienta, por agente/rol/herramienta/verbo | DB OpenCode read-only `~/.local/share/opencode/opencode.db`, tablas `session_v2` + `session_message`; `content[].type=="tool"`, `name`, `state.input`, `error.type=="permission.rejected"` | Patrón ya probado y determinista: `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/opencode-session-scan.py:21-54` |
| Hijos/auxiliares y sesiones reanudadas | `session_v2.parent_id is not null` (scan:23) + API `children`/`fork` (`runtime-discovery.md:23-25`) | Cubre el requisito "vigilar auxiliares y sesiones reanudadas" (`remaining-features-handoff.md:132-133`) |
| Identidad de sesión por paso | `session_message` (mensajes con `agent` y `content`) → conteo de steps | scan:34-41,62-65 |
| Intento despachado (durable) | `.cdad/executions/<execution_id>/dispatches/<attempt>.json` (I8): `packet_id`, `role`, `substage`, `runtime`, `session`, `model_configured/reported`, `started_at` | Ej. real `.cdad/executions/exec-004-002-…/dispatches/review-009-a1.json` |
| Ciclo de vida del paquete | `docs/.cdad-state.json` → `active_packet.status ∈ prepared|dispatched|completed|failed` (`003-001/spec.md:478-480`) | Single-writer = orquestador (001) |
| Reintentos/tokens/límite reportados | `packet-metric.schema.json` (`retry_count`, `input/output_tokens`, `context_limit`, `outcome`), unknowns en `null` (`003-001/spec.md:560-568`) | `additionalProperties:false`: no inventar campos |
| Efectos ya aplicados (anti-duplicado) | Receipts/journal de 002 (`.cdad/runtime/results/<exec>/…`, `materializations/…`); `semantic_status` siempre `pending` (`003-002/closure.md:13-19`) | Reutilizar, no redefinir |
| Tokens/modelos/tiempo reportados por el runtime | Mensajes/`step-finish` con tokens, modelo/proveedor, tiempos y costo reportado (`runtime-discovery.md:27-29`) | Costo ≠ facturación |
| Registro humano de despachos | `docs/specs/*/dispatch-ledger.md` | Fuente de incidentes reales |

## Casos prioritarios

| Caso | Señal disponible | Límite de observación | Decisión que necesita el orquestador | Recuperación mínima |
|---|---|---|---|---|
| **C1. Un agente termina sin entregar resultado utilizable** | `active_packet.status` sigue `dispatched`; no existe receipt para `(execution_id, packet_id)`; el artefacto `produce` no aparece; el cliente `opencode run` retornó pero la sesión sigue viva; `time_created` del último mensaje no avanza | "Sin reporte final" no es un campo estructurado: el mensaje final puede venir en otro idioma o confuso (`friction-intake-004-001.md:42-44,64-68`). Ausencia de receipt confunde "no entregó" con "entregó por otra vía". Sesión "viva" puede estar estancada (ECONNRESET + auto-resume, `friction-intake:44-48`) | ¿Sigue siendo productivo (mensajes/steps avanzan en tiempo) o terminó sin resultado? Si terminó: clasificar (crash / límite de proveedor / fallo silencioso de herramienta) y elegir reanudar vs. redespachar con diagnóstico | **Esperar sobre la DB de sesiones, no sobre el cliente** (`results.md:38-39`). Preservar trabajo parcial y evidencia antes de decidir. Reconciliar efectos (receipt 002) antes de cualquier retry. Reanudar la misma sesión 1 vez; redespachar solo con hipótesis/información nueva |
| **C2. Una ejecución iniciada por el agente muere al terminar su sesión** | El proceso en background (p. ej. suite) no deja artefacto de evidencia; la sesión termina; no hay `run-evidence`/snapshot de esa corrida | La DB **no expone** el proceso hijo del sistema operativo ni su exit code; "murió" solo se infiere por ausencia de evidencia durable, y esa ausencia es débil (podría estar pendiente). El guard no puede observar un proceso que no controla | ¿Existe corrida registrada y equivalente para citar? ¿O hay que re-ejecutar? ¿El efecto material ya se aplicó (receipt/journal de 002)? | Citar la corrida registrada si la equivalencia se demuestra (producto+tests+selección+entorno, `re-entry.md:67-79`; aplicado 10× en `evidence-utility-2026-10-05.md:15-21`). Si no hay corrida válida: re-ejecutar **una vez en primer plano**. Nunca duplicar un efecto ya recibido. **Incidente real: 5 ocurrencias** (`evidence-utility:50-54`; `004-003/dispatch-ledger.md:16`) |
| **C3. Se repiten llamadas, errores o intentos sin información nueva** | Mismas llamadas (`name` + input canonicalizado) con la misma clase de resultado (`error.type=="permission.rejected"`, error de herramienta, salida vacía) ×N; `retry_count`/`outcome` en la métrica; `dispatches/*.json` repetidos | La equivalencia exige canonicalizar; el DB no documenta de forma completa el contenido/exit del resultado (§VERIFY). Hash del output completo es frágil (`remaining-features-handoff.md:191-192`). "Sin información nueva" requiere una señal de progreso (git/artefacto/state) que la DB **no** trae. Relectura justificada, test flaky y nueva hipótesis se ven idénticos a nivel llamada | ¿Reconsiderar estrategia (regla de dos intentos) o es fricción del entorno? ¿Desvío del agente o fallo de herramienta/política? Ambigüedad → paquete breve al orquestador | Retry **solo con un cambio**; conservar evidencia; no reintentos ilimitados (`re-entry.md:79`). **Incidente real: 2.073 reintentos idénticos, ~20 h, costo 15,86 vs ~0,14 normal** (`…/spec.yaml:18-23`). El techo `steps:300` ya corta el runaway mecánico; el guard **observa y registra**, no lo reimplementa |
| **C4. Un obstáculo de capacidades/permisos impide trabajo legítimo y provoca rodeos** | `permission.rejected` por herramienta/agente/verbo (scan:46-52); evidencia de salida de ámbito en el ledger (implementer corrió `install.sh` sobre HOME real, T6; test-writer `git stash`, T7b) (`friction-intake:52-61`) | El DB muestra el deny pero no la intención/objetivo: **un rechazo no es mala conducta** (`remaining-features-handoff.md:38`). Legitimidad exige objetivo/scope del rol (del paquete/execution, no del DB). Pre-flight no puede afirmar un sandbox inexistente (`runtime-discovery.md:60-65`; ADR-011:75-79; `t7-live-walk.md:38-66`: grep/glob se median por patrón, no por ruta) | Clasificar por **objetivo, rol, scope y efecto**, no por nombre de comando (`remaining-features-handoff.md:139-141`). ¿Es defecto del producto (deny de operación legítima) o fuera de rol? Escalar síntesis accionable; **no** conceder ni endurecer permisos automáticamente por un contador (mismo:141) | Sin loop ilimitado de la misma llamada denegada. Prevalidar contra `docs/cdad-policy.json` + mapa de rol. Si es defecto del producto, escalar con repro; re-encauzar al rol a la alternativa declarada sin cambiar autoridad. Un rechazo legítimo es **defecto a corregir en la fuente**, no métrica a optimizar (`friction-intake:13-14`) |

## Distinciones (no-alarma)

| Distinción | Cómo se separa (evidencia observable) |
|---|---|
| **Ejecución larga pero saludable** | `time_created` de mensajes avanza, hay steps/mensajes nuevos y artefactos/state cambian → **sin alerta** (`friction-intake:44-48`) |
| **Polling justificado** | Condición esperada + deadline + cadencia declarados → no cortar antes del vencimiento; al vencer, escalar **una sola vez** (`remaining-features-handoff.md:175-176,180-181`) |
| **Nueva iteración por hipótesis distinta** | Cambian args/fingerprint o clase de resultado y hay progreso → no es repetición equivalente (regla de dos intentos, `re-entry.md:79`) |

## Sin señal fiable

Cuando el runtime no expone la señal (tokens por sesión, exit de subproceso, semántica de `status`): el estado **permanece `unknown`**, el paquete al orquestador declara explícitamente la limitación y **no se fabrica éxito ni fracaso** (`remaining-features-handoff.md:43`; `planning-contract-draft.md:208-209`). La ausencia de incidentes no activa relajaciones automáticas.

---

# 2. Decisiones abiertas para el dueño (numeradas, con recomendación)

> Las marco como **bloqueantes de aprobación** (B) o **decidibles durante la spec** (S). El spec/plan de §3/§4 son **borradores**: no se materializan ni aprueban hasta resolver las B (invariante anti-auto-aprobación, ADR-003).

- **D1 (B) — Forma del guard.** ¿CLI determinista sin servicio, o daemon? **Recomiendo**: CLI determinista `cdad_guard.py` (Python stdlib), **read-only** sobre la DB de OpenCode y los artefactos 001/002, que emite eventos durables bajo `.cdad/`; el juicio queda en el orquestador. Sin agente permanente ni servicio nuevo (`remaining-features-handoff.md:35`).
- **D2 (B) — Huella canónica de intento.** ¿Qué la compone? **Recomiendo**: `herramienta + argumentos canonicalizados (solo campos estables) + clase de resultado cerrada`; conservar la evidencia original **por referencia**, nunca hash del output completo (`remaining-features-handoff.md:158-160,191-192`).
- **D3 (B) — Semántica del umbral.** ¿Bloqueo duro o señal? **Recomiendo**: límite como **señal para reconsiderar estrategia**, no prueba de incumplimiento (`remaining-features-handoff.md:37`); regla conservadora y explícita; `steps:300` sigue siendo el único techo mecánico. Sin auto-bloqueo duro nuevo.
- **D4 (B) — Presupuesto durable: ubicación y propiedad.** **Recomiendo**: registros bajo `.cdad/executions/<execution_id>/guards/…`, keyed por `execution_id+packet_id+attempt`; el guard **no** escribe `docs/.cdad-state.json` (single-writer = orquestador, como 002, `closure.md:53`). Reanudar **no** reinicia contadores. Alternativa: extender `packet-metric.schema.json` — requiere header de schema (hoy `additionalProperties:false`, `planning-contract-draft.md:213-216`).
- **D5 (B) — Tabla cerrada evento→acción y frontera de lo automático.** **Recomiendo**: solo acciones reversibles y proporcionadas (backoff/poll, retry con cambio, repackage, nueva sesión desde checkpoint, escalar, recomendar-bloqueo); ambigüedad → paquete breve al orquestador sin decisión semántica encubierta (`remaining-features-handoff.md:44,166-168`). El guard **nunca** cambia spec, autoridad ni prioridad.
- **D6 (B) — Pre-flight de capacidad/permisos.** ¿Alcance? **Recomiendo**: pre-flight determinista sobre `docs/cdad-policy.json` + mapa de rol + execution context (detectar antes de llamar una operación que la política declara denegada o fuera de raíz); **sin afirmar sandbox inexistente** (`remaining-features-handoff.md:161-163`).
- **D7 (S) — Interacción con 002.** **Recomiendo**: el guard **no** repite efectos; consulta receipt/journal de 002 para saber si la acción terminó. "Comprobar si una acción terminó antes de repetirla" se satisface **reconciliando**; el guard solo señala (`remaining-features-handoff.md:41`).
- **D8 (S) — Cobertura de runtimes.** **Recomiendo**: integración concreta **OpenCode** (lo que el epic pide, `plan.md:85`); el analizador opera sobre artefactos portables y Claude Code se declara como posterior, sin prometer paridad no probada (`plan.md:69-72`).
- **D9 (S) — Generalidad Go / ciclos sin código.** **Recomiendo**: usar `observable_checks` en vez de `focal_tests` para ciclos sin código; fixtures con tests co-ubicados Go y un ciclo documental (`remaining-features-handoff.md:48`; `planning-contract-draft.md:132-137`).
- **D10 (B) — Frontera con 003-004.** **Recomiendo**: declarar solo interfaces que **no obstaculicen** la rotación de contexto (schema de evento/presupuesto estable, keyed por `execution_id`, sin truncar), y **no** implementar checkpoints ni reconstrucción automática (`remaining-features-handoff.md:47`; `plan.md:37,86`).
- **D11 (S) — Adopción y registro de uso real + de-dup.** **Recomiendo**: adopción en un **límite de tarea real** del epic y registro por situación en `guards-ledger.md` (situación, evidencia, decisión, falsas alarmas, costo, pendiente) (`remaining-features-handoff.md:54-56`); sin alertas repetidas del mismo incidente sin cambio relevante (`remaining-features-handoff.md:45`).

**Bloqueantes** para aprobar spec/plan: D1, D2, D3, D4, D5, D6, D10. El resto puede cerrarse durante la spec.

---

# 3. Borrador de `spec.md`

```markdown
# Spec — 003-003-progress-guards

Feature ID: 003-003-progress-guards · Epic: epic-003-context-efficiency
Estado: **draft** (sin marca de aprobación; requiere resolver D1–D11 del handoff)

## 1. Descripción funcional

Detectar y resolver interrupciones y repeticiones improductivas en desarrollos
reales, preservando autonomía y utilidad, sin reconstruir restricciones rígidas
ni crear un supervisor que consuma más que el trabajo que evita.

La capacidad se compone de (a) un analizador determinista **read-only** sobre las
señales ya existentes (DB de sesiones de OpenCode + artefactos de 001/002), que
emite **incidentes y eventos durables**; y (b) una **tabla cerrada evento→acción**
que el orquestador usa para decidir. El juicio semántico permanece en el
orquestador; el guard no es orquestador estratégico (`remaining-features-handoff.md:130-144`).
Vigila también agentes auxiliares y sesiones reanudadas (`ibid.:132-133`).

Construye sobre: techo `steps:300` ya desplegado (runaway mecánico), receipts/
idempotencia de 002, estado/medición de 001. No los redefine.

## 2. Contrato

### Firma propuesta (a validar — VERIFY)

```text
python3 skills/cdad-cycle/scripts/cdad_guard.py observe \
  --project-root ROOT [--execution-context EXEC.json] \
  [--runtime opencode] [--since RFC3339] [--until RFC3339] [--json]

python3 skills/cdad-cycle/scripts/cdad_guard.py classify \
  --project-root ROOT --trace TRACE.json      # trazas grabadas / fixtures

python3 skills/cdad-cycle/scripts/cdad_guard.py budget \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID

python3 skills/cdad-cycle/scripts/cdad_guard.py record \
  --project-root ROOT --event EVENT.json
```

`observe`/`classify` son **read-only** y deterministas; `record` escribe solo
bajo `.cdad/` (nunca `docs/.cdad-state.json`). Éxito → `0`; violación → rc≠0 con
diagnóstico por stderr y sin salida parcial. Los schemas de evento/presupuesto
son propuestos y se validan en la spec (§VERIFY).

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
  a alertar.
- **P8 (generalidad y adopción).** La capacidad funciona para proyectos Go
  (tests co-ubicados) y ciclos sin código; se adopta en un **límite de tarea
  real** y registra su uso real (situación, evidencia, decisión, falsas alarmas,
  costo, pendiente).

## 3. Invariantes verificables

1. El guard es determinista y **read-only** sobre el producto; el orquestador es
   el único escritor del estado; el guard nunca cambia spec, autoridad ni prioridad.
2. Un rechazo de permisos **no** implica mala conducta; **no** se conceden ni
   endurecen permisos automáticamente por un contador (ADR-011).
3. Falta de progreso **≠** contar herramientas o tokens; **un timeout solo no
   prueba bloqueo**.
4. Desconocido permanece desconocido; la ausencia de incidentes **no** activa
   relajaciones automáticas.
5. Se reutilizan los contratos de 001/002 sin redefinirlos; un receipt **no** es
   aprobación semántica.
6. Sin agente permanente ni servicio nuevo sin justificación concreta; sin
   controlador LLM.
7. Se conserva resultado parcial y evidencia **antes** de recuperar/reintentar.
8. Las interfaces declaradas **no obstaculizan** la continuidad de contexto de
   003-004 (evento/presupuesto keyed por `execution_id`, sin truncar contratos).
9. No se duplica el techo mecánico `steps:300` ya desplegado.
10. Los límites de observabilidad del runtime se declaran; no se afirma sandbox
    inexistente ni mediación de procesos que el guard no controla.

## 4. Criterios de aceptación

1. P1–P8 verificadas por tests focales (o `observable_checks` en ciclos sin
   código), cada test mapeado a su postcondición.
2. Escenario de "trabajo legítimo que progresa" en verde y **sin intervención**
   (P7); falsas alarmas registradas con su causa.
3. Escenarios de fallo controlado (bucle, polling, deny, crash, flaky) probados
   sobre trazas grabadas y **etiquetados como simulación**; ningún incidente real
   provocado en proyectos reales (`plan.md:173-176`).
4. Reanudación: intentos y causas sobreviven al cambio de sesión (P4), verificado
   empíricamente.
5. Integración en un límite de tarea real, con `guards-ledger.md` (P8).
6. Suite del repo en verde + validadores (`tests/validate-consistency.sh`,
   `tests/validate-odoo-specialization.sh`, `scripts/validate-subagents.sh`) sin
   regresiones; ausencia de CI declarada como deuda (convención vigente).
7. Cero afirmaciones de ahorro no medido; tokens/contexto ausentes quedan `null`.

## 5. Fuera de alcance

- Renovación de contexto, checkpoints y reconstrucción automática (**003-004**).
- Recepción/persistencia/deduplicación de resultados (**003-002**, ya cerrada).
- Motor general de workflows; cache universal de evidencia; benchmark.
- Endurecer o conceder permisos automáticamente; nuevo epic de seguridad.
- Cualquier afirmación de sandbox o de mediación de procesos no observados.

## 6. Contexto técnico (anclas)

- `skills/cdad-cycle/scripts/cdad_packet.py` (001: state/medición/packet).
- `skills/cdad-cycle/scripts/cdad_result.py` (002: receipt/journal/idempotencia).
- `docs/.cdad-state.json`, `skills/cdad-cycle/assets/{packet-metric,state-template}.json`.
- `docs/cdad-policy.json` (path_policy), `.cdad/executions/<id>/dispatches/*.json`.
- `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/opencode-session-scan.py`
  (patrón read-only a promover; no importar el archivo como producto).
- `docs/epics/epic-003-context-efficiency/runtime-discovery.md` (observabilidad).
- ADR-011 (autonomía supervisada), ADR-003 (materialización), ADR-013 (plan borrador).

## 7. Incertidumbres (VERIFY, no inventar)

- **V1**: ¿la DB `session_message` expone contenido/exit-clase del resultado de
  herramienta más allá de `permission.rejected`? (hoy solo ese tipo está probado).
- **V2**: ¿el `status` de sesión distingue "viva pero estancada" de "terminada"?
- **V3**: ¿se puede observar/abortar hijos de una sesión muerta sin incidentes?
- **V4**: ¿existe límite duro de contexto por sesión observable? (no observado).
- **V5**: ¿está probada la *enforcement* de `steps:300` en vivo? (hoy **NOT
  exercised live**, `results.md:24`).
- **V6**: aislamiento de OpenCode: resolver la lectura de config heredada que
  invalidó el smoke **antes** de cualquier sonda en vivo o envío a proveedores
  (`remaining-features-handoff.md:169-170`; `runtime-discovery.md:60-65`).
- **V7**: forma final del schema de evento/presupuesto y del CLI (draft §2).

---
Status: draft — no aprobada (pendiente D1–D11; no materializar sin resolución).
```

---

# 4. Borrador de `plan.md`

```markdown
# Plan — 003-003-progress-guards (borrador)

Unidades pequeñas y coherentes; cada una con su plan de validación
(`planning-contract-draft.md` §4/§4.1). Complejidad: interfaces nuevas + varios
dominios (runtime, permisos, estado) ⇒ plan revisado por sesión independiente
junto con la spec (`planning-contract-draft.md:163-167`).

Principio transversal: **read-only**; sin servicio; el juicio en el orquestador.
La estrategia común de validación se declara una vez (`@validation_strategy`).

## T1 — Modelo de traza + núcleo determinista de repetición
- Resultado: `observe` detecta repeticiones equivalentes sin progreso con regla
  explícita y evidencia de equivalencia. Postcondición: **P1**.
- Consume: DB OpenCode read-only (scan:21-54); `dispatches/*.json`; state.
- Produce: `cdad-guard-trace` (trace-v1), `cdad_guard.py observe`.
- Archivos (propuestos): `skills/cdad-cycle/scripts/cdad_guard.py`,
  `scripts/cdad_guard.py` (wrapper), `assets/guard-trace.schema.json`,
  `tests/test_003_003_t1_repetition.py`.
- Validación: focales + trazas grabadas (bucle 2.073; progreso real; nueva
  hipótesis). Escenario de fallo **etiquetado simulación**.
- Detener si: **V1/V2/V5** no se resuelven ⇒ declarar límite, no asumir.

## T2 — Señal de progreso, polling y no-alarma
- Resultado: polling válido no se corta; al vencer escala una vez; trabajo
  legítimo progresivo continúa. Postcondiciones: **P2, P7**.
- Consume: trace-v1; artefactos/state/git como señal de progreso.
- Produce: `cdad-guard-poll` (poll-v1).
- Validación: focales con condición/deadline/cadencia y con progreso real
  (verde sin intervención).
- Generalidad: checks observables para ciclos sin código (D9).

## T3 — Pre-flight de capacidad/permisos + acotado de rechazos
- Resultado: rechazos prevalidados o acotados; sin loop ilimitado de la misma
  llamada denegada. Postcondición: **P3**.
- Consume: `docs/cdad-policy.json`, mapa de rol, execution context;
  `error.type=="permission.rejected"` (scan:46).
- Produce: `cdad-guard-preflight` (preflight-v1).
- Validación: focales — deny de operación legítima (defecto), deny fuera de rol
  (correcto), variantes de ruta mediadas por patrón (V6/`t7-live-walk.md:38-66`).
- Invariante: ningún auto-grant/auto-harden.

## T4 — Presupuesto durable y eventos sobre reanudación
- Resultado: cada recuperación consume presupuesto y emite receipt/evento;
  reanudar no reinicia. Postcondición: **P4**.
- Consume: execution context (001), receipt/journal (002), dispatch I8.
- Produce: `cdad-guard-budget` (budget-v1), `guard-event.schema.json`.
- Archivos: `.cdad/executions/<id>/guards/**` (no `docs/.cdad-state.json`).
- Validación: focales de restart/sesión nueva; reconciliación antes de retry.
- Frontera: interfaz que no obstaculiza 003-004 (D10).

## T5 — Paquete de escalado + tabla cerrada de acciones
- Resultado: ambigüedad/unknown devuelve paquete breve; tabla cerrada
  evento→acción; sin decisión semántica encubierta. Postcondición: **P5**.
- Produce: `cdad-guard-escalate` (escalation-v1); tabla en fuente canónica única.
- Validación: focales — caso ambiguo → escalar; caso sin señal → `unknown`; no se
  fabrica outcome.

## T6 — Fixtures de trazas + generalidad + simulación declarada
- Resultado: fixtures cubren bucle, progreso, polling, flaky y crash; Go
  co-ubicado y ciclo sin código; fallos provocados **etiquetados simulación**.
  Postcondiciones: **P6, P8 (parte generalidad)**.
- Validación: `observable_checks` para ciclos sin código; fixtures deterministas.
- Límite: no repetir un desarrollo completo; no provocar incidentes reales.

## T7 — Integración en un límite de tarea real + registro de uso
- Resultado: adopción real con `guards-ledger.md`; de-dup de incidentes.
  Postcondiciones: **P7 (de-dup), P8 (adopción)**.
- Consume: T1–T6.
- Validación: límite de tarea real del epic; registro situación/evidencia/decisión/
  falsas alarmas/costo/pendiente (`remaining-features-handoff.md:54-56`).

## Estimaciones (rangos, método declarado, incertidumbre)
- Rango por unidad: **bajo–medio** (T1–T2, T5–T6), **medio** (T3–T4, T7).
  Método: comparación con ciclos de tamaño similar de 003-002/004-003.
  Incertidumbre: alta por **V1–V6** (observabilidad del runtime).

## Prueba de trabajo legítimo progresivo (global)
Además de los fixtures de fallo, un escenario continuo: un encargo simulado que
progresa en varias llamadas y artefactos **no** dispara ninguna intervención;
la evidencia queda en `guards-ledger.md` con falsas alarmas = 0 registradas.

```plan-tasks
{
  "validation_strategy": "focales por unidad (pytest, env -u TMPDIR) + trazas grabadas etiquetadas simulación; suite completa y validadores del repo al cierre; no se provocan incidentes reales",
  "tasks": [
    {"id": "T1", "produce": [{"artifact": "cdad-guard-trace", "contract": "trace-v1"}], "consume": [], "depends_on": [], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_guard.py", "scripts/cdad_guard.py", "skills/cdad-cycle/assets/guard-trace.schema.json"], "focal_tests": ["tests/test_003_003_t1_repetition.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T2", "produce": [{"artifact": "cdad-guard-poll", "contract": "poll-v1"}], "consume": [{"artifact": "cdad-guard-trace", "contract": "trace-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_guard.py"], "focal_tests": ["tests/test_003_003_t2_polling.py"], "observable_checks": ["un ciclo sin código con progreso no recibe intervención"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T3", "produce": [{"artifact": "cdad-guard-preflight", "contract": "preflight-v1"}], "consume": [{"artifact": "cdad-guard-trace", "contract": "trace-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_guard.py", "docs/cdad-policy.json"], "focal_tests": ["tests/test_003_003_t3_preflight.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T4", "produce": [{"artifact": "cdad-guard-budget", "contract": "budget-v1"}], "consume": [{"artifact": "cdad-guard-trace", "contract": "trace-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_guard.py", "skills/cdad-cycle/assets/guard-event.schema.json"], "focal_tests": ["tests/test_003_003_t4_budget.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T5", "produce": [{"artifact": "cdad-guard-escalate", "contract": "escalation-v1"}], "consume": [{"artifact": "cdad-guard-budget", "contract": "budget-v1", "producer": "T4"}, {"artifact": "cdad-guard-trace", "contract": "trace-v1", "producer": "T1"}], "depends_on": ["T1", "T4"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_guard.py"], "focal_tests": ["tests/test_003_003_t5_escalation.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T6", "produce": [{"artifact": "cdad-guard-fixtures", "contract": "fixtures-v1"}], "consume": [{"artifact": "cdad-guard-trace", "contract": "trace-v1", "producer": "T1"}, {"artifact": "cdad-guard-poll", "contract": "poll-v1", "producer": "T2"}], "depends_on": ["T1", "T2", "T3", "T4", "T5"], "parallel": [], "files": ["tests/test_003_003_t6_fixtures.py"], "focal_tests": ["tests/test_003_003_t6_fixtures.py"], "observable_checks": ["tests Go co-ubicados y ciclo sin código cubiertos"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T7", "produce": [{"artifact": "cdad-guard-adoption", "contract": "adoption-v1"}], "consume": [{"artifact": "cdad-guard-fixtures", "contract": "fixtures-v1", "producer": "T6"}], "depends_on": ["T6"], "parallel": [], "files": ["docs/specs/003-003-progress-guards/guards-ledger.md"], "observable_checks": ["un límite de tarea real queda registrado en guards-ledger.md"], "regressions": ["tests/validate-consistency.sh", "tests/validate-odoo-specialization.sh", "scripts/validate-subagents.sh"], "integration_gate": "@validation_strategy", "owner": "orquestador"}
  ]
}
```

## Integración final
1. Suite completa del repo + los tres validadores (sin regresiones; deuda de CI
   declarada, convención vigente).
2. Adopción en un límite de tarea real del epic con `guards-ledger.md`.
3. `plan.md` y `spec.md` revisados juntos por sesión independiente antes de
   aprobar (interfaces nuevas + límites de confianza).

## Incertidumbres / replanificación
- Si **V1–V6** no se resuelven, reacotar el alcance explícitamente con el dueño
  antes de expandir infraestructura (`plan.md:193-197`) — no asumir APIs.
- Si una unidad crece más allá de su mini-ciclo, pasa a candidata a feature propia.
```

---

## Cierre y límites honestos

- **Entregado**: (1) tabla de casos, (2) decisiones D1–D11, (3) spec draft, (4) plan draft + bloque `plan-tasks`.
- **No entregado a propósito**: medición de tokens/contexto (el entorno **no** la expone; `evidence-utility-2026-10-05.md:104`), y cualquier afirmación de sandbox o de observación de procesos que el runtime no expone. Marqué esas como **VERIFY/V1–V6**.
- **Límite de mi rol**: no apruebo nada; los borradores se materializan recién cuando el dueño resuelva D1–D11 (ADR-003). No ejecuté `opencode run` ni sondas en vivo (prohibidas por el encargo y por V6).
- **Bloqueo declarado**: ninguno. Si en la revisión el dueño pide el esquema exacto de evento/presupuesto, eso exige resolver antes **V1/V7** con una sonda read-only sobre `session_message` (sin proveedores), que no ejecuté por la restricción del encargo.
