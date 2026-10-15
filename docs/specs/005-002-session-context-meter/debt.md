# Deuda priorizada — 005-002-session-context-meter

Origen: review formal de la etapa 4 (`review.md`, reviewer `mofgw/glm-5.3-flash`, familia
distinta a la del implementer `mofgw/deepseek-v4.1-flash`), veredicto **0 blocking · 10 optional ·
0 abstenciones**. Los 10 hallazgos **no rompen el camino feliz** del contrato (PD-1..PD-16 sobre las
muestras pinneadas, PD-14 documental), por eso se registran acá con su **condición de cierre
verificable** y no bloquean el cierre de la feature (regla del tramo: lo que no rompe el camino
feliz va a deuda). La severidad del reviewer **no se relaja**: se conserva su veredicto y su bucket.

> **Actualización 2026-10-12 — reapertura acotada por el criterio de review vigente.** El dueño
> aprobó un criterio nuevo (`docs/epics/epic-005-real-operation/execution.md`, sección «Criterio de
> review vigente — 2026-10-12»): se bloquea y se corrige ya lo que compromete el **resultado**, la
> **evidencia** o el **uso previsto**; va a deuda priorizada lo que es una mejora o variante sin
> impacto material. Bajo ese criterio, la feature se **reabrió** y se corrigieron **D1, D2, D3, D4 y
> D5** (una sola clase de defecto: *desconocido informado como cero / magnitud parcial presentada
> como completa / ausencia no declarada*), más la **subclase que el propio RED detectó** (agregados
> del tramo) y el **agregado por rol** que encontró la review de la reapertura (hallazgo **R1**,
> bloqueante). **D6 queda en deuda por encargo del dueño.** Cada ítem de abajo lleva ahora su estado.
>
> Evidencia del tramo: commits `5a4d567` (reapertura) … `d435e9b` (GREEN de R1); RED y GREEN focales
> por unidad; review de la reapertura `review-reopen-2026-10-12.md` (**1 blocking · 5 optional · 2
> abstenciones declaradas**) y su segunda pasada acotada
> `review-reopen-2026-10-12-second-pass.md` (**R1 CERRADO**); integración real de T4 en solo lectura
> **5 passed** en cada gate; suite completa de cierre en worktree fijado a `d435e9b`.

## Prioridad 1 — producto (comportamiento observable en un caso de borde válido)

### D1 (= F1) — `time_relative: 0.0` fabricado cuando el tiempo del hito no es observable  — **CERRADA 2026-10-12**

> **Cerrada por la reapertura** (obs. del criterio nuevo): el hito observado emite `time_relative: null` + causa cuando el tiempo no es observable y la medida hermana (`time_to_first_resume`/`time_to_first_dispatch`) queda `unknown` con `value: null` (antes: `observed` con value null, un cubo mentiroso). Regresión focal: `tests/test_005_002_t5_unknown_declared.py::test_t5_1…` (RED `0083d82`, GREEN `3e481d4`).
- **Veredicto/bucket del reviewer:** OPTIONAL · h. **Procedencia:** `skills/cdad-cycle/scripts/cdad_context_meter.py:624-635` (`time_relative if time_relative is not None else 0.0`), `:618-621`, `:683-690`; PD-3/PD-4/INV-2.
- **Por qué es el primero:** viola el invariante central del contrato (desconocido ≠ cero) en un esquema válido donde el mensaje del hito no trae tiempo numérico. Hoy ningún test lo cubre y los stores reales traen timestamps.
- **Condición de cierre:** emitir `unknown` (value `null` + causa) cuando el tiempo no sea observable, con un test que use un mensaje de hito con `t_created` no numérico y afirme `bucket=unknown`, `value=null`, `rc=0`.

### D2 (= F2) — el límite normativo de 16384 bytes (PD-12) no está garantizado por la implementación  — **CERRADA 2026-10-12**

> **Cerrada por la reapertura**: se **forzó el límite** (no se reescribió el reference). Por defecto `input_per_step` porta un resumen de tamaño fijo (`count/last/previous/min/max/unobserved`) con indicador `truncated {truncated, cause, omitted_steps, detail_flag}` que declara la omisión y su causa; el detalle por paso completo exige la bandera explícita `--steps`, documentada en `context-meter.md`. Medición del rol: documento por defecto de UNA sesión = 8.001 B (1.000 pasos) y 8.006 B (4.000 pasos) frente a los 16.384 publicados; con `--steps` el límite no aplica (el usuario pidió el detalle). Regresión focal: `tests/test_005_002_t5_bounded_output.py` (RED `f22d292`, GREEN `41b45f9`).
- **Veredicto/bucket:** OPTIONAL · h. **Procedencia:** `skills/cdad-cycle/references/context-meter.md:150-154`; `tests/test_005_002_t3_application_privacy.py:837-856`; `scripts/cdad_context_meter.py:459-484,500,508-539`.
- **Por qué importa:** el reference lo publica como normativo por sesión, pero el adaptador no tiene lógica de tamaño; el único test de tamaño verifica la muestra 1. Una sesión de miles de llamadas supera el límite y se emite igual (`rc=0`), contradiciendo lo publicado que 005-003 leerá como contrato.
- **Condición de cierre:** o forzar el límite (fallo cerrado nombrando la causa, o truncado **declarado** con `unknown`/causa), o reescribir el reference como garantía solo sobre las muestras; más un test con un fixture grande (p. ej. 5000 pasos) que haga observable la política elegida.

### D3 (= F5) — `len(input_per_step) == 102` sobre la base real: oráculo más estricto que el contrato  — **CERRADA 2026-10-12**

> **Cerrada por la reapertura** según su condición de cierre: el assert pasó a `assertGreaterEqual(steps, 101 llamadas pinneadas)` con el conteo exacto declarado como **sonda** en el mensaje, y se conservan las dos llaves de consistencia que sí son contrato (`steps[-1] == 203.276`, `steps[-2] == 202.222`). Commit `f22d292` (solo tests), verificado por la review de la reapertura (auditoría commit por commit: ninguna aserción de contrato se debilitó).
- **Veredicto/bucket:** OPTIONAL · h. **Procedencia:** `tests/test_005_002_t4_acceptance.py:645-649,665-664`; spec §4 PD-5 y §6.
- **Por qué importa:** la spec no pinea la cantidad de mensajes `assistant` del tramo (101 es el conteo de llamadas de herramienta). Un tramo real válido con mensajes sin herramienta intermedios rompería el oráculo de aceptación sin violar el contrato.
- **Condición de cierre:** relajar a `len(steps) >= tool_calls` o usar una llave de consistencia («el último paso contiene el proxy 203.276 y el anterior 202.222»), dejando el conteo exacto como sonda declarada.

### D4 (= F7) — el detector de despacho reconoce solo `subagent` y un despacho por otra herramienta se reporta `absent`  — **CERRADA 2026-10-12**

> **Cerrada por la reapertura**: la salida declara las herramientas reconocidas (`reader.dispatch_tools` = `subagent`, `task`) y la causa de `absent` nombra el conjunto reconocido y declara el límite («un despacho hecho con otra herramienta NO es detectado por este lector»), de modo que la ausencia distingue «no ocurrió» de «no reconocido». Regresión focal: `tests/test_005_002_t5_unknown_declared.py::test_t5_5…`.
- **Veredicto/bucket:** OPTIONAL · h. **Procedencia:** `scripts/cdad_context_meter.py:111-112,137-138,611-615`; spec PD-6/D5 («p. ej. subagent»).
- **Por qué importa:** la causa de `absent` no distingue «no hubo despacho» de «despacho por herramienta no reconocida»; 005-003/005-006 podrían subcontar sin saberlo.
- **Condición de cierre:** declarar en el reference la lista exacta de herramientas reconocidas y/o hacer que la causa de `absent` nombre el conjunto reconocido («recognizes only: subagent»). Sin ampliar el alcance de 005-002.

### D5 (= F8) — `--session` parcialmente casado se mide como subconjunto silencioso  — **CERRADA 2026-10-12**

> **Cerrada por la reapertura**: con varias `--session` y una inexistente, `rc = 0`, la existente se mide y la referencia pedida que no se encuentra se declara en `unknowns[]` con causa que nombra la referencia de forma **hasheada** (nunca el id crudo); el fallo cerrado cuando ninguna casa se conserva. El oráculo se reforzó en `7635a90` (la causa debe nombrar una referencia hasheada distinta de toda referencia medida) tras detectarse que el patrón previo era satisfacible con el eco de una referencia medida. Regresión focal: `tests/test_005_002_t5_unknown_declared.py::test_t5_6…`.
- **Veredicto/bucket:** OPTIONAL · h. **Procedencia:** `scripts/cdad_context_meter.py:827-831`; PD-2/PD-15 (espíritu fail-closed); PD-11.
- **Por qué importa:** si se piden varias referencias y algunas no están, mide las encontradas con `rc=0` y no declara las no encontradas (solo falla cerrado si ninguna coincide). La muestra parecería completa.
- **Condición de cierre:** `unknown` con causa nombrando el ref pedido, o fallo cerrado cuando alguna referencia solicitada no case; test con una ref errónea + una válida.

### D6 (= F10, nit) — `run.runtime_version` con sesiones de versiones heterogéneas  — **SIGUE ABIERTA (por encargo del dueño)**

> **Queda en deuda por encargo explícito**: la reapertura acotada no la incluye. La review de la reapertura la reexaminó (R6) y no encontró evidencia de que hoy comprometa el uso previsto; su condición de revisión es que 005-003 compare contextos por versión de runtime antes de consumir `run.runtime_version`.
- **Veredicto/bucket:** OPTIONAL · h. **Procedencia:** `scripts/cdad_context_meter.py:859-868`; spec §2.
- **Condición de cierre:** lista de versiones o `unknown` con causa cuando sean heterogéneas.

## Prioridad 2 — proceso y documentación

### D7 (= F3) — «valida contra el asset» (PD-1/PD-16) no se verifica cargando el asset
- **Veredicto/bucket:** OPTIONAL · h. **Procedencia:** `tests/test_005_002_t1_neutral_record.py:568-698`; spec PD-1/PD-16; 0 usos del asset en los tests.
- **Condición de cierre:** un test (stdlib) que parsee el asset y verifique recursivamente el documento emitido (`required`/`additionalProperties`/condicionales de `$defs`) más un caso negativo (documento sin una clave obligatoria → no valida).

### D8 (= F4) — `application.ref` anclado al store medido cuando no hay `--application-ref`
- **Veredicto/bucket:** OPTIONAL · h. **Procedencia:** `scripts/cdad_context_meter.py:773-810`; `context-meter.md:107-109`; asset `:261-267`; `tests/test_005_002_t3_application_privacy.py:511-536`.
- **Condición de cierre:** distinguir el significado en el asset/reference (p. ej. `ref` nulable con causa para ese caso) o dejar registrada la aprobación explícita de la instrumentación en la memoria del feature. Comportamiento declarado; no es bloqueo.

### D9 (= F6) — el RED de T3 no fue RED para PD-10/PD-12 (pre-satisfechos por el GREEN de T2)
- **Veredicto/bucket:** OPTIONAL · h. **Procedencia:** `tests/test_005_002_t3_application_privacy.py:747-894`; `git show b153cb3:skills/cdad-cycle/scripts/cdad_context_meter.py`; `git diff b153cb3 fd58199 --stat`.
- **Condición de cierre:** registrar en el docstring de T3 (o en el state) que PD-10/PD-12 llegaron pre-satisfechas por el GREEN de T2 y que su RED fue de banderas. Evidencia de proceso, no corrección de código.

### D10 (= F9) — el reference publica conteos nuevos de la base real (7/22/30 hijos)
- **Veredicto/bucket:** OPTIONAL · h. **Procedencia:** `skills/cdad-cycle/references/context-meter.md:196-208`; spec PD-10/INV-7.
- **Condición de cierre:** reescribir sin cifras («ninguna candidata en la ventana cumple el conteo declarado: 13») o registrar la decisión del dueño que aprueba publicar esos agregados. Sin identificadores, rutas ni proveedor: no viola la lista prohibida.

## Deuda declarada por el propio contrato (no es hallazgo de la review)

- **Sesión de cierre de 005-001 (V6 / PD-14):** con el criterio declarado (13 sesiones hijas) ninguna candidata de la ventana lo satisface (7, 22 y 30 hijos). La muestra queda **`unknown` con causa** y este ítem abierto; el criterio reproducible queda documentado en `skills/cdad-cycle/references/context-meter.md`.
- **V3/V11 del discovery** (ruta exacta del CLI de continuidad; campo de ruta de `read` por versión): siguen abiertos y se confirman en implementación/consumo posterior.
- **V4 del discovery:** semántica de `resume_attempts`/`time_idle`/`idle_outcome` declarada `unknown` con causa (no se les atribuye el hito de resume).

## Deuda de la review de la REAPERTURA (2026-10-12)

Origen: `review-reopen-2026-10-12.md` (reviewer `mofgw/glm-5.3-flash`, familia distinta a la del
implementer; criterio vigente 2026-10-12), veredicto **1 blocking · 5 optional · 2 abstenciones
declaradas**. El bloqueante **R1 quedó CERRADO** (RED `bb3141e`, GREEN `d435e9b`, segunda pasada
acotada `review-reopen-2026-10-12-second-pass.md` → **R1 CERRADO**, sin hallazgos nuevos). Los
OPTIONAL pasan a esta lista con su condición de cierre verificable; el criterio vigente los dejó en
deuda porque son mejoras o variantes **sin impacto material** (no comprometen el resultado, la
evidencia ni el uso previsto con el texto publicado).

### R2 — el `$def` del resumen en `measure.value` es descriptor, no binding (el asset no lo obliga)
- **Veredicto/bucket del reviewer:** OPTIONAL. **Procedencia:** `skills/cdad-cycle/assets/context-meter.schema.json`, `$defs.measure.value.anyOf` (rama genérica `{"type":"object"}`).
- **Estado tras la reapertura (segunda pasada):** **PARCIALMENTE avanzado.** La parte nueva del asset (`roles[].sums` y `roles[].distributions`, de `d435e9b`) **SÍ es binding** (verificado con `jsonschema`: forma vieja con número plano, entrada sin `sessions_reporting`, entrada `unknown` con `value` numérico, `cause: null` en `unknown`, clave extra → todas **NO validan**). El recorte original sigue abierto: la rama genérica de `measure.value` sigue acogiendo un `input_per_step_summary` mal formado.
- **Condición de cierre:** dar a `measure.value` una forma discriminante por medida (o quitar la rama genérica con un `$def` propio para `previous_calls_by_tool`), más un test que parsee el asset y afirme que un objeto mal formado **no** valida.

### R3 — las causas agregadas de varias sesiones son indistinguibles entre sí en `unknowns[]`
- **Veredicto/bucket:** OPTIONAL. **Procedencia:** `_build_document` (`unknowns[] = sorted(set(unknowns))`) con causas que portan cifras de cobertura y no se atribuyen a la sesión que las produce.
- **Por qué importa:** en una corrida multi-sesión (default `--limit 20`) un consumidor no puede saber a qué sesión pertenece cada causa.
- **Condición de cierre:** atribuir la causa con la `session_ref` hasheada (o mover las causas por sesión a una clave por sesión), más un test con dos sesiones mixtas que distinga las entradas.

### R4 — el documento por defecto MULTI-sesión supera los 16.384 bytes en total
- **Veredicto/bucket:** OPTIONAL. **Procedencia:** sonda propia del reviewer (2 sesiones sintéticas de 2 pasos: documento de 15.849 B; con `--limit 20` el total supera el límite) con `rc = 0`.
- **Por qué queda en deuda:** el límite publicado es **por documento de sesión** (`context-meter.md`), y el encargo del tramo lo acotó a «cualquier tamaño de sesión»; el reviewer juzgó **defendible** el encuadre. No compromete el resultado ni la evidencia con el texto publicado.
- **Condición de cierre:** declarar en el reference la regla del documento multiplexado (p. ej. «el total es ≤ N × el límite por sesión, y el límite normativo es POR DOCUMENTO DE SESIÓN») antes de que 005-003 consuma corridas multi-sesión; un test que afirme la frase.

### R5 — sonda del fixture de la unidad 2 (consistencia del borde alternativo)
- **Veredicto/bucket:** OPTIONAL. **Procedencia:** `tests/test_005_002_t5_bounded_output.py` (las cifras pinneadas 203.276/202.222 se afirman sobre el fixture; la sonda del fixture no cubre el cross-product de tamaños).
- **Por qué queda en deuda:** es del **test**, no del producto, y la cobertura del eje que cierra D2 (cantidad de pasos) sí está cubierta (1.000/4.000 pasos).
- **Condición de cierre:** ampliar la sonda del fixture (o declararla explícitamente) si un consumidor futuro necesita más formas.

### R6 — `run.runtime_version` con versiones heterogéneas (D6)
- Es el mismo D6 de arriba: la review de la reapertura lo reexaminó y no encontró evidencia de impacto actual; queda en deuda por encargo del dueño.

## Deuda detectada en la verificación del orquestador Claude (2026-10-12)

### D11 — el chequeo de no escritura de la integración real es inestable con la base viva
- **Procedencia:** `tests/test_005_002_t4_acceptance.py::AcceptanceT4Test::test_c5_sboot04_primer_despacho_por_entorno`
  compara el `(tamaño, mtime)` del store y de sus `-wal`/`-shm` antes y después de abrirlo.
- **Observado:** con OpenCode escribiendo en paralelo (otros proyectos activos), falló 7 de 8
  corridas consecutivas: los tamaños son iguales y solo cambian los mtime, que escribe otro
  proceso. En momentos sin actividad pasa (5 passed). La garantía de solo lectura del producto
  (PD-11) sigue verificada sobre el fixture temporal; lo que no es confiable es esta evidencia
  sobre la base viva.
- **Prioridad 1 (criterio vigente: compromete la evidencia del gate de integración).** Se cierra
  antes de usar la integración real como gate de 005-003.
- **Condición de cierre (corregida tras la verificación de Codex, 2026-10-12):** comparar el estado
  global de una base que otros procesos escriben no identifica quién escribió, así que tampoco
  sirven el tamaño ni la presencia de archivos. (1) La ausencia de escrituras se verifica sobre
  una base temporal controlada. (2) La concurrencia se cubre con una prueba controlada que tenga
  otro escritor activo durante la lectura. (3) En la integración real se comprueba solo la
  lectura y los resultados, sin exigir que la base quede inmóvil. (4) Nunca se intenta escribir
  en la base real para demostrar que está prohibido. Corridas verdes repetidas no sustituyen esta
  corrección. Cerrarla antes de usar la integración como gate de 005-003; no bloquea su
  discovery.
