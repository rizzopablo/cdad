**Condiciones de sesión (verdict-tuple):** familia de modelo distinta del implementador ✔ · diff completo en contexto ✔ · citas file:line verificables ✔ · spec+plan en contexto ✔ → bucket base **h**.

## Verificado y correcto (evidencia positiva breve)

- Focales T1: `6 passed in 1.24s` (probe C). Suite completa 445 passed en 4933ed0 tomada como dada (instrucción del orquestador; no repetida).
- `classify` es determinista (stdout idéntico entre corridas, test p01 + `sort_keys`) y read-only (`tree_snapshot` antes/después, test p01/p07).
- Wrapper `scripts/cdad_guard.py` propaga rc correctamente: probe B1 → `rc=1` vía `PIPESTATUS[0]` (runpy + `SystemExit(main())`).
- P1/P2/P7 comportamientos focales: bucle de 5 → 1 incidente con regla/huella/evidencia; progreso en cada tramo de 3 → 0 incidentes; args distintas → huellas distintas; poll pre-deadline → `wait`; post-deadline → exactamente 1 `escalate`.
- Alcance: el diff toca exactamente los 5 archivos declarados en plan T1 (`plan.md:205`). Sin desvíos de write-scope.

---

## Hallazgos BLOCKING

### B1 — Token de progreso ausente se trata como "progreso congelado": incidente fabricado desde señal desconocida

- **Verdict:** `BLOCKING` · **Bucket:** `h` (sonda en vivo) · **Severidad:** Required
- **Evidencia (file:lines + sonda):** `skills/cdad-cycle/scripts/cdad_guard.py:95-100` agrupa entradas comparando `run[0]["progress_token"] == progress_token`; con `progress_token` ausente en ambas entradas, `None == None` agrupa y dispara el incidente. El schema (`skills/cdad-cycle/assets/guard-trace.schema.json`, `entries.items.properties`) **no requiere** `progress_token`. Sonda A (4 `tool_call` equivalentes **sin** `progress_token`): `rc=0`, 1 incidente con `evidence.progress.changed: false`.
- **Consecuencia:** viola la invariante 4 ("desconocido permanece desconocido"), P5 (no fabricar éxito ni fracaso) y P7 (intervención solo bajo condiciones claras): el guard emite un incidente —la salida que dispara intervención del orquestador— afirmando `changed: false` cuando **nunca observó** progreso. En uso real (cuando `observe` graba trazas de la DB), cualquier fuente que omita el token genera falsa alarma con evidencia falsa.
- **Cierre verificable:** focal nuevo: traza con ≥3 `tool_call` equivalentes sin `progress_token` → **cero incidentes** (o marcador explícito `unknown` en la evidencia); en el guard, token ausente/no-string ⇒ señal desconocida ⇒ no-disparo (fail-closed al lado no-alarma, proporcional a D3).

### B2 — Traza fuera de contrato se clasifica en silencio con rc=0 (validación de entrada fail-open)

- **Verdict:** `BLOCKING` · **Bucket:** `h` (sonda en vivo) · **Severidad:** Required
- **Evidencia:** sonda B3: traza con `trace:"trace-v9"`, `schema_version:9`, `entries:"oops"` → `rc=0`, envolvente "válida" con resultados vacíos (`_cmd_classify`/`classify_trace`, `cdad_guard.py:181-196` no validan nada; `entries` no-lista se traga en `:155-157`). El spec §3 (`spec.md:104-106`) declara: "Éxito → 0; **violación → rc≠0 con diagnóstico por stderr y sin salida parcial**". El asset `guard-trace.schema.json` existe pero no lo carga ningún código ni test (grep: solo `docs/`).
- **Consecuencia:** una traza grabada bajo otro contrato produce un veredicto silenciosamente vacío y válido — evidencia inválida consumida como válida; drift del schema indetectable. Familia de validación de entrada (incluye B1-probe: `FileNotFoundError` con traceback crudo, y B2-probe: `JSONDecodeError` con traceback — rc≠0 pero diagnóstico no diseñado, mismo eje).
- **Cierre verificable:** `classify` valida contrato de entrada (`trace=="trace-v1"`, `schema_version==1`, `entries` lista) → en desvío, rc≠0 + mensaje por stderr y sin salida parcial; archivo/JSON ilegible → rc≠0 con diagnóstico determinista (no traceback). Focal de error-path que lo pruebe.

### B3 — La huella no canonicaliza args: la regla emitida afirma algo que el código no hace (D2)

- **Verdict:** `BLOCKING` · **Bucket:** `h` · **Severidad:** Required
- **Evidencia:** `cdad_guard.py:57-72`: `payload = {"tool":…, "args": entry.get("args", []), …}` — los args entran **crudos** al hash; no existe filtro de "campos estables" (D2, `spec.md:217`: "solo campos estables") en el guard ni en ningún punto del repo (grep sin resultados). Sin embargo, la regla emitida en cada incidente (`REPETITION_RULE`, `cdad_guard.py:33-36` y sonda A) declara "tool + **canonicalized args** + result_class".
- **Consecuencia:** la clase exacta del incidente real que motiva P1 (2.073 reintentos con args que varían en campos inestables — rutas tmp, timestamps) **no se detecta**: args distintas solo por campo inestable → huellas distintas → cero incidentes, silenciosamente. Además la evidencia emitida es infiel: declara canonicalización que no ocurre. Hoy solo hay fixtures pre-canonicalizados, así que el defecto no es observable en los focales — pero es un escape alcanzable por uso normal apenas `observe` grabe trazas reales, y la regla emitida ya es infiel ahora.
- **Cierre verificable:** o (a) canonicalización declarada e implementada en el guard (p. ej. filtrado de claves/normalización de args) con focal que muestre que variantes solo-inestable colapsan a la misma huella; o (b) la canonicalización se declara responsabilidad del grabador en el contrato `trace-v1` (schema nota + docstring) y el texto de `REPETITION_RULE` deja de afirmar lo que no ejecuta. Una de las dos, verificable por test o por texto del contrato.

---

## Hallazgos OPTIONAL

- **O1 — Encuesta injustificada → `wait` sin marcar la condición.** `cdad_guard.py:139-146`: poll sin `condition`/`deadline`/`cadence` válidos decide `wait` (sonda E: `rc=0`, `wait`). El comentario dice "never fabricate a decision" pero `wait` **es** una decisión; el orquestador no distingue "espera justificada" de "señal desconocida" (P5 pide `unknown` explícito — su dueño es T3/escalado). **Verdict:** `OPTIONAL` · **Bucket:** `m`. Cierre sugerido: `justified: false` (o `decision: "unknown"`) en la decisión del poll.
- **O2 — Schema asset muerto: fixtures no validados contra él.** `guard-trace.schema.json` no es cargado por código ni tests; nada impide drift fixture↔schema (ya posible por B2). **Verdict:** `OPTIONAL` · **Bucket:** `m`. Cierre: un focal que valide los fixtures contra el schema (jsonschema o chequeo a mano en stdlib).
- **O3 — Nits (sin consecuencia contractual):** (a) `CANONICAL` en `scripts/cdad_guard.py:10` asignado y nunca usado; (b) `REPETITION_RULE` hardcodea ">=3" duplicando `REPETITION_THRESHOLD` (`cdad_guard.py:27,33-36`) — drift si el umbral cambia; (c) el docstring del test (`test_003_003_t1_repetition.py:15`) nombra el contrato de envolvente `classify-v1`, pero plan T1 declara producir `trace-v1`/`poll-v1` (`plan.md:68-69`) y la envolvente no trae campo `contract` — naming a fijar antes de que T3/T4 consuman la interfaz. **Verdict:** `OPTIONAL` · **Bucket:** `m`.

---

## Abstentions

- **V1 (clase de resultado real de la DB más allá de `permission.rejected`):** no ejercitable en T1 (`observe` no existe); fuera de este diff. No emito juicio sobre la grabación futura.
- **Estrategia de dedup cross-corrida (P7/O3 durable):** el `escalated` set de `_poll_decisions` (`cdad_guard.py:131`) es estado por-corrida; la dedup durable pertenece a T3/T5. No juzgo aquí si la interfaz actual bastará para T3.
- **Disponibilidad de `jsonschema` (draft 2020-12) en el entorno:** no lo verifiqué; el cierre de O2 no depende de ello (validación a mano en stdlib es suficiente), así que no abstengo el hallazgo, solo la elección de mecanismo.

## Evidencia (comandos y salidas exactas)

| # | Comando | Resultado |
|---|---|---|
| C | `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_003_003_t1_repetition.py tests/test_003_003_t1_polling.py -q` | `6 passed in 1.24s` |
| A | `python3 scripts/cdad_guard.py classify --project-root /tmp/opencode/probe-a/proj --trace …/trace.json` (4 tool_calls sin progress_token) | `rc=0`, 1 incidente, `progress.changed:false` **fabricado** |
| B1 | `… --trace nope.json` | `rc=1`, traceback `FileNotFoundError` |
| B2 | trace JSON inválido | `rc=1`, traceback `JSONDecodeError` |
| B3 | trace `trace-v9`/`schema_version:9`/`entries:"oops"` | **`rc=0`**, envolvente vacía "válida" |
| E | poll sin condition/deadline | `rc=0`, `wait` sin marca |

**Archivos modificados por mí:** ninguno (write_scope `[]`; sondas en `/tmp/opencode/`).
**Commit evaluado:** `4933ed0` (GREEN) sobre `47bc3bc` (review-fix fixture) sobre `1b03a9a` (RED tests-only) — trazabilidad RED→GREEN íntegra en el rango.

**Resumen:** **3 blocking · 3 optional · 3 abstentions.** El núcleo focal (P1/P2/P7 sobre fixtures canónicos) es correcto y determinista; los blockings comparten una familia de fondo — el guard trata "no observado" como dato (token ausente ⇒ sin progreso; contrato ausente ⇒ éxito vacío; args crudos ⇒ "canonicalizados") — y se resuelven con una sola pasada fail-closed sobre la validación de entrada y la honestidad de la regla emitida.
