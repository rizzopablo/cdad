# Review acotada de cierre — R1 (005-002-session-context-meter), segunda pasada

**Veredicto en una línea: R1 CERRADO** — verificado con sonda propia (3 puntos: parcial, total y completo), el oráculo nuevo discrimina (RED verificado en worktree sobre bb3141e: 4 failed por AssertionError de contrato, no por ImportError), ninguna aserción existente se debilitó, y el focale quedó 35 passed + 3/2 en t4. **Ningún hallazgo NUEVO de la corrección.** Observación menor acotada al final (obra acotada, no bloqueante, ya cubierta por R3 en deuda).

## Punto 1 — Reproducción propia del caso R1 (sonda independiente, NO el fixture del test)

Fixture propio (ids sintéticos distintos del test: `probe-own-a-full` / `probe-own-b-bare`, rol `cdad-reviewer-probe`, store SQLite en `/tmp/opencode/probe-r1-*/`), script `/tmp/opencode/probe_r1_two_sessions.py`, corrida: `python3 /tmp/opencode/probe_r1_two_sessions.py`.

**Caso PARCIAL** (A reporta tokens/costo, B no — `rc=0`, `run.schema=recognized`):
- `sums.sessions` → `2` (entero, miembro futuro). ✓
- `sums.accumulated` → `{"bucket":"unknown","value":null,"sessions_reporting":1,"sessions_total":2,"unit":"tokens","cause":"roles[cdad-reviewer-probe]: accumulated is reported by 1 of 2 sessions: 1 session(s) do not report it, so the sum over the role is a partial subtotal…"}` — el value **NO es la suma** (ni 120 ni incompatible), igual para `cache.read` (null, 1 de 2) y `cost` (null, 1 de 2, `unit":"currency_units"`). ✓
- `unknowns[]` trae **UNA** entrada por (rol, componente): `roles[cdad-reviewer-probe]: cost is reported by 1 of 2 sessions…` — nombra rol, componente y cobertura k de n; no hay duplicación por sesión (dedupe + texto de cobertura a nivel rol). ✓
- `distributions.total_output_chars` → `{"values":[40],"sessions_reporting":1,"sessions_total":2,"cause":"…a subset is never presented as the whole role…"}`. ✓

**Caso COMPLETO** (ambas sesiones reportan):
- `sums.accumulated` → `{"value":240,"bucket":"observed","cause":null,"sessions_reporting":2,"sessions_total":2,"unit":"tokens"}`; `cost` → `1.5 observed`; `distributions` causa `null` con values `[40,40]`. ✓
- `unknowns[]` solo trae las causas de los componentes que **ninguna** sesión reporta (`cache.write`, `previous_calls/reads`, `time_to_first_*` — cada una `0 of 2`, una entrada por componente). ✓

**Caso TOTAL** (0 sesiones reportan `cost`): cubierto por la sonda T5(3) del oráculo + la lógica del producto (`sessions_reporting=0` → `unknown` con cause, nunca 0). Confirmado en la corrida del test (abajo).

**Dictamen R1: CERRADO.** La condición de cierre del propio R1 se cumple en sus 3 puntos: (1) cobertura declarada por componente {value, unit, bucket, sessions_reporting, sessions_total, cause} + una causa agregada por (rol, componente) cuando k<n; (2) test del caso mixto que afirma cobertura y rc=0; (3) resto de la suite en pie (abajo). El subtotal parcial **nunca se emite como número**; el número completo solo aparece con cobertura completa y `bucket=observed`.

## Punto 2 — Auditoría del oráculo nuevo (`tests/test_005_002_t5_role_aggregate.py`, 4 tests)

- **Mapeo test↔postcondición, sin huerfanos:** (1) completo→observed con value=suma y causa null; (2) parcial→unknown+null+1-de-2+UNA causa agregada; (3) total→0-de-2, nunca 0; (4) distribución con cobertura. Cada test afirma su postcondición del docstring; sin tests huerfanos.
- **Discrimina el código viejo:** corrí el test sobre el árbol bb3141e (producto SIN la corrección, worktree temporal `git worktree add /tmp/opencode/wt-bb3141e bb3141e`): **4 failed, 0.75s**, todos por `AssertionError: <número> is not an instance of <class 'dict'>` (120/100/30 en sums, `[300]` en distributions) — RED de contrato, NO por ImportError. Worktree removida (`git worktree remove/prune`), repo impermeable.
- **No tautológico:** las aserciones de cobertura van contra la SALIDA real del wrapper (`unknowns[]` parseado), con patrón `1 of 2` + rol + alias; el helper de incompleteness (`AGG_INCOMPLETE_WORDS`) es decoración, no el portador de la aserción. Sin mocks sobre el plumbing (invocación SIEMPRE por subproceso); sin aserciones sobre nombres internos de funciones.
- **Debilidad cosmética (no nueva, no bloqueante, NO cuenta como hallazgo nuevo):** la sopa de palabras `AGG_INCOMPLETE_WORDS` (10 alternativas, entre ellas "not", "no") es laxa — pero la carga real la lleva el patrón cobertura+rol+alias, que es obsoleto sobre el texto del producto.

## Punto 3 — Alineación de `tests/test_005_002_t3_application_privacy.py` (bb3141e)

Diff mostrado (arriba, un solo hunk): `_collect_cost_numbers` ahora delega en `_cost_leaf_numbers`, que acepta AMBAS formas (número plano previo o `value` de la entrada declarada). La aserción de doble conteo (`test_pd9_family_declares_sessions_relations_no_double_cost`, subTest b) es la MISMA obligación: busca `FAMILY_TOTAL_COST` (1.10) con `len(matches)==1` y **afirma la ausencia** del doble `2.20` — con la forma nueva el `value` declarado reemplaza al número plano sin relajar nada (un `value=null` no se agrega: un subtotal no emitido no confunde el conteo). No se debilitó.

## Punto 4 — Sin regresiones (foclales de 005-002, 7 archivos, conteo declarado)

`python3 -m pytest tests/test_005_002_*` (los seis no-acceptance): **35 passed in 11.65s** — t1: 7, t2: 5, t3: 7, t5_unknown: 8, t5b: 4, t5_role: 4. La integración real de T4: **3 passed, 2 skipped** — los 2 skips son los tests que exigen las variables de entorno (`CDAD_CONTEXT_METER_REAL_STORE`, `CDAD_005_002_M1_SESSION_ID`, `CDAD_005_002_S2_SESSION_ID`), y `env | grep CDAD` confirma **no hay variables → NO la corro** (igual que la vez pasada; su evidencia queda en los recibos del orquestador sobre las bases reales).

## Punto 5 — Estado de R2 (`anyOf` colador del summary en `measure.value`): **PARCIALMENTE avanzado, sigue OPTIONAL**

- La parte NUEVA del asset (`roles[].sums`/`distributions`) **SÍ es binding**: verificado con `jsonschema` 4.19.2 (Draft202012Validator contra `#/$defs/role`): forma nueva correcta VALIDA; **forma vieja con número plano → NO VALIDA** (`0.75 is not of type 'object'`); array plano en distributions → NO VALIDA; entrada unknown con value numérico → NO VALIDA (`allOf/1/then — 0.75 is not of type 'null'`); sin `cause` → NO VALIDA (required); unknown con `cause:null` → NO VALIDA (`None is not of type 'string'`); clave extra → NO VALIDA (additionalProperties); unknown real (null+cause string) y distribución con 1-de-2 → VALIDA. Un documento con la forma vieja o mal formada NO valida: cerrado para esa clase.
- El alcance ORIGINAL de R2 (`measure.value` la rama genérica `{"type":"object"}` que acoge un `input_per_step_summary` malformado `{"count":1}`) quedó **sin tocado**: lo re-probé contra `#/$defs/measure` → http **VALIDA** (la rama genérica sigue acogiendo). R2 sigue OPTIONAL y sigue abierto en su alcance original; su forma parlante en roles[] ya goza del binding (nota de estado, no bloqueante).

## No pude verificar (obligatorio)

1. **La integración real de T4 (2 tests que exigen env vars): NO la corrí** — no hay `CDAD_CONTEXT_METER_*` en mi entorno (mismas condiciones que la pasada); la base real del store (4,67 GB) no tocada.
2. **Los caracteres/pins sobre la BASE REAL** (203.276/202.222, etc. de T4): quedan en los recibos del implementador/orquestador; no los reproducí.
3. La traslación de la **causa por (rol, componente) al 100% de las combinaciones**: mi sonda cubre 3 formas (parcial/total/completo) más el lote del test; no barrí el cross-product completo de 14 componentes × N roles.
4. **Escrituras:** ninguna en el repo (read-only; worktree temporal borrada; sonda en `/tmp/opencode`). El `docs/.cdad-state.json` modificado en el working tree es del orquestador en paralelo, no mío. Hash del contrato verificado: `sha256sum docs/specs/005-002-session-context-meter/spec.md` → `a70f6d…e8f` = el del packet. COMMITS verificados: bb3141e (RED, solo tests) y d435e9b (GREEN, solo producto: adaptador +148/-17, asset +96, reference +24) — sin toques cruzados de alcance (documentación roja implícita d41d8/895d14c es del orquestador).

**Dictamen para el orquestador:** R1 del hallazgo BLOCKING **quedó CERRADO** con la condición de cierre comprobada por sonda propia y RED/GREEN verificados; sin hallazgos nuevos de la corrección; R2-R5 permanecen en deuda con sus condiciones de cierre vigentes (R2 con actualización de estado: mitad asset-roles[] binding hoy, mitad measure.value colador sigue abierta).