# Revisión formal — etapa 4 · 005-002-session-context-meter

## Evidencia de la revisión

- **Diff revisado completo** (rango y commits): `7be52d4..HEAD` = 13 commits (`dc6b454`→`c50d8f3`): RED/GREEN de T1 (207 arch.), T2, T3, corrección de tests `49d27ad`, PD-14 en reference `1dc4e9c`, cierre `c50d8f3`. 9 archivos, +5774/-6.
- **Contrato verificado**: `sha256sum docs/specs/005-002-session-context-meter/spec.md` → `a70f6d500457e86769e85168f7cf5e3850d034b9cc79661856e99de53bd42e8f` (**coincide** con el pin del paquete). Spec y plan leídos íntegros.
- **Comandos corridos** (read-only; nada modificado; `review.md` lo materializa el orquestador):
  1. `python3 -m pytest tests/test_005_002_t1_neutral_record.py tests/test_005_002_t2_milestones.py tests/test_005_002_t3_application_privacy.py tests/test_005_002_t4_acceptance.py -q` → **`22 passed, 2 skipped in 7.70s`** (2 skips = integración real y S-BOOT-04 por variable de entorno, con diagnóstico explícito — no verde fabricado).
  2. `git show b153cb3:.../cdad_context_meter.py | grep _hash_ref` → el adaptador del GREEN de T2 **ya** tenía hashing (`:133/:686/:766`) → confirma (e).
  3. `git show fd58199 --stat` + diff `b153cb3..fd58199` → el GREEN de T3 solo agregó anotación/relaciones; **ningún mecanismo nuevo de privacidad/compacción**.
  4. `grep -rn "context-meter|context_meter" agents/ sources/ scripts/ Makefile` → **0 referencias en gates** (PD-13/INV-5 ✓).
  5. `grep -c "session_v2|session_message"` sobre asset y reference → **0** (neutralidad PD-1/INV-3 ✓).
  6. `grep` del diff por `ofap|/home/|4\.67|GB|anthropic|opencode\.db` → **sin fugas** (PD-10/INV-7 ✓).
  7. Auditoría test↔PD: los 4 archivos de tests leídos completos (912+1346+911+1069 líneas).

**Veredicto por postcondición** (código + tests la verifican): PD-1/2/3/4/5/6/7/8/9/10/11/12/13/15/16 ✓ observables (PD-1 con salvedad F3, PD-9 con salvedad F4). PD-14 ✓ resuelta documentalmente por reference (verificará P:(d)). Sin PD sin test salvo la PD-14 declarada; sin tests huérfanos sin PD. No hay aserciones sobre nombres internos ni mocks sobre plumbing: todo test observa el **wrapper por subproceso** (JSON/stdout/rc/stderr).

---

## Hallazgos

### F1 — `_milestone` fabrica `time_relative: 0.0` cuando el tiempo del hito no es observable
- **Veredicto: OPTIONAL** (no rompe el camino feliz pinneado, pero viola INV-2/PD-3/PD-4 en un caso de esquema válido) · **Bucket: h**
- **Rationale**: cuando el hito tiene llamada detectada pero el tiempo es no-observable (t_created no numérico en el mensaje, o inicio del tramo sin tiempo), `_relative_minutes` devuelve `None` y `_milestone` sustituye ese `None` por `0.0` en `time_relative` con `status: observed`; la medida `time_to_first_resume/_dispatch` sale entonces con value `0.0` en **bucket `observed`** — un **cero fabricado**, exactamente lo que la spec prohíbe (D7: desconocido ≠ cero). El contrato observable queda roto en el borde aunque los stores reales típicamente traigan timestamps; no hay test que cubra este caso.
- **Procedencia**: `skills/cdad-cycle/scripts/cdad_context_meter.py:624-635` (`time_relative if time_relative is not None else 0.0`), `:618-621`, `:683-686/:687-690` (bucket `observed` si el hito se observó); PD-3/PD-4/INV-2; sin test.
- **Cierre verificable**: emitir `unknown` (value null + causa) cuando el tiempo no sea observable, y un test con el mensaje del hito portando `t_created` no numérico que afirme `bucket=unknown`, `value=null`, rc=0.

### F2 — El límite normativo de 16384 bytes (PD-12) no es garantizado por la implementación más allá de las muestras
- **Veredicto: OPTIONAL** · **Bucket: h**
- **Rationale**: el reference declara el límite como **normativo por sesión** («The document for one session stays at or below it», referencia `context-meter.md:150-154`), pero el adaptador no contiene ninguna lógica de tamaño ni degradación declarada (el diff del GREEN de T3 no agregó compacción; verificado por `git diff b153cb3..fd58199`). El único test de tamaño (T3, `test_pd12_compact_output_with_references_no_transcript`) verifica **solo la muestra 1**. La salida crece linealmente con la cantidad de pasos (`input_per_step` con una entrada por mensaje, `:459-484/:535-539`; `previous_calls_by_tool`, `:699-702`): una sesión con miles de llamadas supera los 16384 bytes y el medidor la emite igual (rc=0), contradiciendo el reference publicado que 005-003 tratará como contrato. La spec en sentido estricto se cumple (PD-12 pide «el documento de la muestra 1 debajo del límite declarado»), pero lo publicado excede lo garantizado.
- **Procedencia**: `skills/cdad-cycle/references/context-meter.md:150-154`; `tests/test_005_002_t3_application_privacy.py:837-856`; `scripts/cdad_context_meter.py:459-484,500,508-539`; sin enforcement.
- **Cierre verificable**: o bien forzar el límite (fail-closed nombrando la causa, o truncado **declarado** con `unknown`/causa), o re-escribir el reference como acumulado-solo-sobre-las-muestras; más un test con una sesión grande (`--limit N` sobre un fixture de p. ej. 5000 pasos) haciendo observable la política elegida.

### F3 — «Valida contra el asset» (PD-1/PD-16) no se verifica dinámicamente: los tests duplican los controles sin cargar el asset
- **Veredicto: OPTIONAL** · **Bucket: h**
- **Rationale**: ninguna prueba carga `context-meter.schema.json` (grep sobre `tests/test_005_002_t*.py`: 0 usos); la verificación de claves/obligatoriedades/cubos se re-implementa en código de test (`test_005_002_t1_neutral_record.py:568-698`), y la postcondición negativa de PD-16 («un documento sin una clave obligatoria **no valida**») no se prueba en ningún lado. Una deriva futuro determinación (obligatoriedades, `additionalProperties`, `milestone.allOf` del asset) es invisible: el asset y el registro pueden divergir sin que nada falle. Los controles duplicados de hoy son una aproximación fiel pero no binding el contrato documentado.
- **Procedencia**: spec PD-1 (verificable: «el documento... valida contra el asset») y PD-16 (negativa); `tests/test_005_002_t1_neutral_record.py:568-698`; `grep` de usos del asset en tests → 0.
- **Cierre verificable**: un test (stdlib) que parseé el asset y verifiqué recursivamente que el documento emitido cumple `required`/`additionalProperties`/condicionales de `$defs`, más un caso negativo (documento al que le falta una clave obligatoria → no valida).

### F4 — Anotación de aplicación sin `--application-ref` (familia a declarar): `ref` queda anclado al store medido, no a evidencia de aplicación — decisión (c) del orquestador
- **Veredicto: OPTIONAL** (compatible con PD-9 en lo esencial: no inventa recibo, no juzga, no aprueba) · **Bucket: h**
- **Rationale**: cuando hay relación padre/hijo que PD-9 exige declarar pero no hay `--application-ref`, el medidor emite `application.ref = store_ref` (hasheado) con `limit=unknown` y la causa en `basis`. Es la forma **honestamente disponible**: el asset hace `ref` obligatorio (`context-meter.schema.json:261-267`), y PD-9 exige declarar sesiones/relaciones aunque no exista insumo; el `basis` y el reference lo explicitan («no application reference was provided... references the measurement store»: `cdad_context_meter.py:798-807`, `context-meter.md:107-109`). No obstante, la semántica de `ref` en PD-9 es «ruta/commit/recibo a la **evidencia de aplicación**»; un consumidor de 005-003 que siga `application.ref` aterriza en la referencia del **store** (insumo de medición), no en evidencia de aplicación. PD-9 y la no-aprobación quedan intactos, pero la función `ref` queda sobrecargada con dos significados.
- **Procedencia**: spec PD-9 (forma fijada, `ref` como referencial a evidencia); `scripts/cdad_context_meter.py:773-810`; `context-meter.md:107-109`; asset `:261-267`; tests T3(b) aceptan ambas formas (`test_005_002_t3:511-536`).
- **Cierre verificable**: distinguir el significado en el asset/reference (p. ej. `ref` nulable con causa para ese caso) o dejarlo como instrumentación **aprobada explícitamente** en la memoria del feature; hoy es comportamiento declarado y no es un bloqueo.

### F5 — Corrección `49d27ad` (pregunta a): la pinneación quedó **solo en lo que la spec pinea**; queda una aserción sobre-especificada respecto del contrato real (len(steps)=102 sobre la base real)
- **Veredicto: OPTIONAL** · **Bucket: h**
- **Rationale**: la corrección es fiel. (i) `max_output` sigue pinneada a 51.243 (lo único que PD-5/§6 pinea: `tests/t2:185,833-838`, `tests/t4:149,611-617`); (ii) `total_output` ya no pinea el número real: sobre fixture es la suma **calculada por el constructor** (`M1_TRAMO_TOTAL_OUTPUT = sum(_m1_tramo_output_size)`, `t2:208-209`, `t4:172-173`) y sobre la base real **solo** consistencia `total >= max` (`t4:618-636`); (iii) el fixture es fiel en el aspecto auditado: 100/101 llamadas con salida (la #1 con salida vacía — métricamente equivalente a «sin salida»: `len=0`) y distribución de tamaños inventados; (iv) no quedan más pinneaduras real-only prohibidas: 12,55/12,40/101/121/203.276/202.222/#19/18/8/9/desglose/#73 están todas **pinneadas por la spec** (§4/§6), y `seq` no se pinneadura real (`check_seq=False`, `t4:999`). **Excepción que sobrevive**: sobre la base real se pinneadura `len(input_per_step) == 102` (`t4:645-649`); la spec no pinneadura la cantidad de mensajes `assistant` del tramo (contador 101 perteneciente a llamadas de herramienta con herramientas + cierre), y un tramo válido real con mensajes sin herramienta intermedios rompería el oracle de aceptación sin que el contrato esté violado. No falló porque el gate real (commit `c50d8f3`: «gate de integracion real verde») confirmó la forma de la muestra real; es un oracle más estricto que el contrato.
- **Procedencia**: `tests/test_005_002_t4_acceptance.py:645-649,665-664`; spec §4 PD-5 y §6; sonda del orquestador (total 317.170, max 51.243) compatible con la corrección.
- **Cierre verificable**: relajar a `len(steps) >= tool_calls` o llave de consistencia («el último paso contiene el proxy 203.276 y el paso anterior 202.222»), dejando el conteo exacto como sonda declarada.

### F6 — RED parcial en T3: los tests de PD-10 y PD-12 (pregunta e) corrieron green ya en el RED porque el GREEN de T2 los pre-satisfizo
- **Veredicto: OPTIONAL** · **Bucket: h**
- **Rationale**: verificado: el adaptador de `b153cb3` (T2 GREEN) ya tenía `_hash_ref`/`session_ref`/`parent_ref`/`store_ref` hashados (`git show b153cb3:...:133,686-689,766`) y salida compacta por construcción; el GREEN de T3 (`fd58199`) no agregó ningún mecanismo de privacidad/compaction, solo anotación/relaciones. Por tanto el RED de T3 no fue fully RED: las aserciones de PD-10/PD-12 pasaban antes del GREEN de T3, y el RED real fue de contrato (flags `--application-*` rechazados). **No son vacías**: son guardas conductuales reales (negativos crudos/identificadores/absolutos, límite de bytes sobre fichero) que atraparían una regresión futura de embed-de-transcript o de hashead no. Debería haberse declarado en el archivo T3 (se declara en T4, `:96-102`).
- **Procedencia**: `tests/test_005_002_t3_application_privacy.py:747-894`; `git show b153cb3:skills/cdad-cycle/scripts/cdad_context_meter.py`; `git diff b153cb3 fd58199 --stat`; política honesta de RED declarada en T4 `:96-102`.
- **Cierre verificable**: registrar en el docstring de T3 (o en el state de etapa) que PD-10/PD-12 llegaron pre-satisfechas por el GREEN de T2 y su RED fue de flags — evidencia de proceso, no corrección de código.

### F7 — El detector de despacho es el conjunto cerrado `{subagent}` («p. ej. subagent» de la spec): despachos por otras herramientas se reportan `absent`
- **Veredicto: OPTIONAL** · **Bucket: h**
- **Rationale**: `DISPATCH_TOOL_NAMES = {"subagent"}` (`cdad_context_meter.py:112`) satisface el contrato aprobado (muestras pinneas y S-BOOT-04 via subagent; D5 dice «p. ej.»), pero la delegación de OpenCode no es esa herramienta por detección de sub-agentes — si la traza real despacha fuerzas por el tool de subagentes nativo (`task`) o variantes, `first_dispatch` sale `absent` con la causa «no role work dispatch tool call (e.g. subagent)» (`:137-138`), es decir **un falso absent declarado**. Para 005-006/005-003, que leen estos registros, la causa no distingue «no hubo despacho» de «despacho por herramienta no reconocida». Riesgo de medición subcontada silenciosa.
- **Procedencia**: spec PD-6/D5 («p. ej. subagent»); `scripts/cdad_context_meter.py:111-112,137-138,611-615`; alcance declarado del feature (out of scope ampliar a otros runtimes).
- **Cierre verificable**: declarar en el reference la lista exacta de herramientas reconocidas (ya declarada para resume? parcial — solo resume), y/o que la causa de `absent` nombre el conjunto reconocido con el riesgo («recognizes only: subagent»). Sin ampliar el alcance de 005-002.

### F8 — `--session` parcialmente casado se mide como subconjunto silencioso (rc=0, nada en `unknowns[]`)
- **Veredicto: OPTIONAL** · **Bucket: h**
- **Rationale**: si se piden varias referencias y **algunas** no están (errata de id, sesión retirada), el medidor mide las encontradas, sale `rc=0` y el documento no declara las no-encontradas (solo falla cerrado si **ninguna** coincide, `:828-831`). En contra del espíritu fail-closed de PD-2/PD-15 y del consumo de 005-003: la muestra medida parecería completa sin que el registro revele el subconjunto solicitado-no-medido. No rompe ningún postcondición pinneada (la spec no declara el comportamiento parcial), por eso no es bloqueo.
- **Procedencia**: `scripts/cdad_context_meter.py:827-831`; PD-2/PD-15 (esencia fail-closed); PD-11 (selección explícita y acotada).
- **Cierre verificable**: caos `unknown` con causa (nombrando el ref pedido, histograma) o fail-closed cuando alguna referencia solicitada no case; test con una ref errónea + una válida.

### F9 — El reference expone conteos nuevos de la base real (candidatas con 7/22/30 sesiones hijas) no publicados previamente
- **Veredicto: OPTIONAL** · **Bucket: h**
- **Rationale**: la resolución de PD-14 en el reference cita los conteos de hijos de las sesiones candidatas de la ventana 005-001 («**7, 22 y 30 child sessions**: context-meter.md:198-200`). No viola la lista prohibida por INV-7/PD-10 (no hay rutas, proveedor, modelo ni identificadores: solo un conteo tercero agregado), pero contradice la regla declarada de **no agregar valores nuevos** en contratos publicables sobre el store («sin agregar valores nuevos», PD-10/INV-7; el discovery publica los agregados ya citados). Baja severidad: son agregados derivados necesarios para demostrar «ninguna candidata cumple 13», y ningún identificador revela.
- **Procedencia**: `skills/cdad-cycle/references/context-meter.md:196-208`; spec PD-10/INV-7 (regla de «sin valores nuevos»).
- **Cierre verificable**: o re-escribir sin cifras («ninguna candidata en la ventana cumple el conteo declarado: 13»), o registrar la decisión del dueño que aprueba publicar esos agregados en la skill.

### F10 (nit) — `run.runtime_version` toma `versions[0]` de un conjunto ordenado cuando el documento combina varias versiones
- **Veredicto: OPTIONAL** · **Bucket: h**
- **Rationale**: si `--session` combina sesiones de versiones de runtime distintas, el documento declara una sola versión (la mínima ordenada: `:859-868`) y omite la heterogeneidad sin causa en `unknowns[]`. Caso degenerado (cada corrijo trae su propia versión), la spec no lo pinea; nit de exactitud.
- **Procedencia**: `scripts/cdad_context_meter.py:859-868`; spec §2 (`run.runtime_version`: versión observada).
- **Cierre verificable**: lista de versiones o `unknown` con causa cuando son heterogéneas.

---

## Respuestas a los puntos que el orquestador pidió esclarecer

- **(a) Corrección `49d27ad`**: **correcta y fiel**. Queda pineadado solo `max_output=51.243` (lo que la spec pinea; `t2:185`/`t4:149`); `total_output` es suma del fixture (`t2:208-209`) y sobre la base real solo `total>=max` (`t4:618-636`). Fixture fiel: 100/101 con salida (la #1 vacía: métricamente equivalente). **Una** aserción sobre-restrictiva del mismo tipo sobrevive, pero de otra clase: `len(input_per_step)==102` sobre la base real, ⓘ F5. La sonda del orquestador (317.170 total / 51.243 max) es consistente con la corrección.
- **(b) Decisiones de interfaz**: ninguna excede ni contradice la spec. (i) El límite 16384 es **el que PD-12 exige declarar** («un límite de bytes declarado») y está declarado en el reference `:150-154`; con la salvedad F2 (no garantizado por茶的). (ii) Las claves adicionales de `measures` (`segment_duration`, `tool_calls`, `session_tool_calls`, `session_reads`, `previous_calls_by_tool`) son compatibles: PD-16 dice «claves **mínimas** requeridas» y el asset permite adicionales (`measures.additionalProperties: measure`, asset `:179`); cada una trae `value/unit/provenance/bucket`. (iii) El tipo objeto de `measure.value` en el asset (permitido para `previous_calls_by_tool` y listas para `input_per_step`) es coherente con «lista/distribución declarada» de PD-16. (iv) Las banderas `--application-ref/--application-limit` completan el transporte declarable de la anotación (la spec no fija cómo llega el insumo; PD-15 pide que las banderas mínimas se acepten y la superficie lo empare clearly). Bien.
- **(c) Forma de la anotación sin ref de entrada**: declarado como **F4** — compatible con PD-9 en lo sustantivo (no inventa recibo, no juzga, el lector no aprueba; `basis` lo declara), con el hallazgo de sobrecarga semántica de `ref` (dto, referencial a evidencia ≠ referencial al store). No la protento como bloqueo.
- **(d) PD-14 sin test unitario**: la resolución es **honesta y suficiente**. El reference fija el criterio documentado (4 criterios reproducibles, comparando contra los valores declarados: `context-meter.md:171-194`), informa `unknown` con causa (criterio 13 no satisfecho por ninguna candidata: `:198-205`) y registra el ítem abierto/deuda (`:205-208`); no fabrica ninguna sesión. La postcondición admite exactamente esta forma («criterio documentado o unknown con causa + ítem abierto») y la verificación «por review» es la que este informe hace. La deuda queda solo en prosa del reference (no en un registro mecanizable de deuda): resonó como nota dentro de F9.
- **(e) Tests de PD-10/PD-12 pre-satisfechos**: son **guardas reales, no vacías** (aserciones negativas con marcadores únicos + límite de bytes), pero el RED de T3 no fue RED para ellas — verificado por commits (`b153cb3` ya hasheaba). Declarado como F6 (hallazgo de proceso, no de producto).

---

## Agregado

**0 blocking, 10 optional, 0 abstenciones.**

Dictamen para el orquestador: **sin bloqueantes**. Los 10 opcionales son deuda de cierre/borde (F1/F2/F5/F7/F8 con condiciones de cierre verificables; F3/F4/F6/F9/F10 de proceso/documentación). El camino feliz del contrato (PD-1..PD-16 sobre las muestras pinneadas, salvo PD-14 documental) está observado por tests conductuales verdes (22 passed, 2 skipped legítimos), el asset/reference/wrapper siguen la convención del repo, y no hay fugas de este VPS en el diff.
