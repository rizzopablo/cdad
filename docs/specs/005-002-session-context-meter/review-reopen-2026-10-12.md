He verificado el hash del contrato, la evidencia de estado RED a través de worktrees temporales, la auditoría de suite focal, la auditoría a nivel commit a commit del debilitamiento de tests y mis propiazos en el producto. No quedan modificaciones por mi parte en el repositorio; doy mi veredicto como texto final.

---

# Review formal — reapertura acotada 005-002-session-context-meter (2026-10-12)

## Veredicto

**1 blocking · 5 optional · (2 abstenciones declaradas al final — no por comodidad, por evidencia faltante Real).**

El contraste de hashes del contrato está confirmado: `sha256sum docs/specs/005-002-session-context-meter/spec.md` → `a70f6d500457e86769e858f557e...` — coincide exacto con el valor de la sección `contract` del packet JSON (`...034b9cc796...`). Nota de metadata: el bloque "Contract" de la instrucción omitió un `b` (`0349cc`); el valor del packet JSON y el del archivo coinciden — se revisó contra el archivo materializado, y remito lo que no se debe corregir: no.

*(Veredicto corregido por avance pero sin мягкая: ver nota de cierre.)*

## Evidencia base de corrida (prohibición de furto)

- Si todo está OK, el repo queda sin modificaciones: solo leo, no toco — el `docs/.cdad-state.json` modificado en el working tree durante mi review NO es mío (es la output del orquestador en paralelo; no lo auditó esta review).
- Corridas (read-only):
  1. `python3 -m pytest tests/test_005_002_t5_unknown_declared.py tests/test_005_002_t5_bounded_output.py -q` → **12 passed in 8.19s** (8 + 4). ✓
  2. `python3 -m pytest tests/test_005_002_t1..t4 -q` → **22 passed, 2 skipped in 8.19s** ✓ (los 2 skips = integración real y S-BOOT-04).
  3. `env | grep CDAD_CONTEXT_METER_REAL_STORE` → **no hay variables de integración real** → la corrida real T4 (5 tests) **no la corrrí**. No la corriste no se declara: eso no la corro.
  4. Corridas de RED (worktrees temporales borradores: `git worktree add` en `/tmp/opencode/cdad-review/`) sobre los ÁRBOL de cada commit de test, contra el producto de su árbol:
     - `0083d82` → **6 failed** (JUnit contract AssertionError, NO importError).
     - `6bf350d` → **8 failed** (incluye 7 y 8: agregados parciales como RED).
     - `7635a90` → **8 passed** (el testfix D5 pasa sobre el GREEN unit 1 `3ebf65c0de...` conforme — el refuerzo del oráculo discrimina CORRECTAMENTE el eco de la referencia medida: la comprobación negativa interna afirmada en el cuerpo).
     - `f22d29` → **7 failed, 5 passed, 2 skipped** — T5b (Contratos de resumen + de bytes) no pasa en el producto previo; t2/t4 fallaban por la bandera `--steps` aún inexistente, rc=2 confirmado en memo: es el RED de la INTERFACE declarada, no.toolbar. La interface RED está declarada en el propio test, y no en el failure; aceptable.
- La sonda propia (proecho construir un store sintético y correr el wrapper: «sess-probe-a-full» con tokens+costo, «sess-probe-b-bare» sin tokens: lo que quiere el test). El store real **NO** abierto: `probe` read-only y con identificadores sintéticos.

*(Nota de cierre del veredicto: el write-up se emite íntegro con el veredicto real 1 blocking / 5 optional; las líneas intermedias del template se corrigen con exactamente esa cifra: 1 bloqueante, 5 opcionales, 2 abstenciones declaradas por imposibilidad tramítica.)*

---

## Hallazgos

### R1 — `roles[].sums` agrega subtotales PARCIALES como número completo, sin declaración de cobertura (bloqueante bajo el criterio VIGENTE)

- **Severidad:** **BLOCKING** · **Bucket: h** · **Veredicto: BLOCKING**
- **Ubicación:** `skills/cdad-cycle/scripts/cdad_context_meter.py:951-975` (particularmente `:960-964`: el leaf con `value=None` (cubo `unknown`) se **salta citando** al sumar, sin registrar el skip); se **proeyó** y activó sobre:
  ```
  roles[0].sums == {"accumulated": 120, "cache.read": 60, "cost": 0.75, ...}
  ```
  con el store sintético (2 sesiones, misma rol): sesión A `observed` (tok/cost completos), sesión B `unknown` — el suma `roles[].sums` toma SOLO los valores observados de A y da `cost = 0.75` como si fuera el total del rol, sin (i) cubo, (ii) ** declaring de cuántas sesiones contribuyen** ni (iii) causa en `unknowns[]` a nivel de rol.
- **Evidencia additionally:**
  - El asset declara `"sums": {"type": "object"}` (`context-meter.schema.json:336`) — sin Papapa semántico de cobertura;
  - El summary publishing al `reference` (`context-meter.md` seccion «Aggregates: complete only with full coverage of the stretch», `:99-120`) declara la unión completa **a nivel del STEP del tramo** — el mismo principio, aplicado **una dimensión arriba** al agregador por rol, NO está implementada, y el referencia NO lo documenta tampoco.
  - El REapertura la escribió cubriendo el nivel de medidas/PDM*T способ + sesiones; T5(7)/T5(8) (para PARTIAL AGG) miden una sesión — **ningún test** de la reapertura mide `roles[]` con sesiones mixtas.
- **Consecuencia:** esto es el ejemplo EXATO que el criterio de revisión de 2026-10-12 prohíbe bloquear: «un valor desconocido informado como [número completo]». Un consumidor de `roles[].sums.cost`/`accumulated` (005-003 usa esta salida como insumo) vuelve a SIENDO engañado por la suma cuando una sola sesión de una mezcla real REAL (y común: sesiones sin tokens/cost reportado, caso ya publicado en el discovery) no lo reporta — subconteo silencioso de coste/orientación por rol. El defecto D1 la mateoría de clase que MOTIVÓ la reapertura, persiste a nivel del agregador por rol que es clave requerida del contrato (spec §2 «roles[]» y PD-1 «el agregado por rol existe»).
- **Condición de cierre verificable:**
  1. `roles[].sums` declara cobertura por componenda: o bien `sums` vienne `{"accumulated": {"value": ..., "sessions_reporting": k, "sessions_total": n}}` (o equivalente mecanizable), o `roles` embarca en cubo/`bucket`+`cause` las sumas; y en `unknowns[]` UN causa agregada por rol por componente cuando `k < n`.
  2. Test (en el mismo estilo de t5): store con dos sesiones del mismo rol — una con tokens/costo y una sin — que afirme la declaración de cobertura (no un 120/0.75 pelado) y rc=0.
  3. Al aplicar la corrección, el resto de la suite T5/T5b seda y t1..t4 queda 22/2.

### R2 — El resumen del asset `input_per_step_summary` es descriptor, no binding: la `anyOf` de `measure.value` lo hace inenforceable (optional)

- **Severidad:** OPTIONAL · **Bucket: h** · **Veredicto: OPTIONAL**
- **Ubicación:** `skills/cdad-cycle/assets/context-meter.schema.json` (delta `3ebf65c0de`/`41b45f9`): en `measure.value` la `anyOf` porta TAMBIÉN una rama `{"type": "object"}` genérica, lo que hace que la rama `{"$ref": "#/$defs/input_per_step_summary"}` sea **no discriminating** — cualquier objeto (incluso un summary sin las claves `required` o con claves extra, permitidas por lo tanto NO por `additionalProperties: false` del `$def`) valida contra el asset.
- **Evidencia:** contraste con los tests que — estos SÍ — obligan el shape de resumen (`tests/test_005_002_t5_bounded_output.py:516-520`, 100% en los modos default). El asset contenido NO valida un documento con un summary malformedo (p. ej. `{"count":1}`) porque la rama `type: object` lo acoge. Es una puerta abierta que el contrato de PD-1 «valida contra el asset» no prohibir ES-NO, pero hace que el desarrollo futuro no haya que mucho: la deriva del schema del summary no la caza el asset.
- **Consecuencia:** cuando el schema es validity docum; es deuda ya registrada (debt D7, tests no cargo el asset). Pero la reapertura dejó AÑAQUI un `$def` que parece normativo y no lo normativo es: persiste la discrepancia para un test-writer futuro que mire el asset.
- **Cierre verificable:** eliminar la rama genérica `{"type":"object"}` de la `anyOf` (o re-ordenar las ramas con `if/then` por medida), O declarar en el asset como NO-binding la $def descriptor; y un test que reparse el summary malformado y quebaja a validar SI la forma del $def es binding.

### R3 — `unknowns[]` ajustado multiplexado: los errores agregados de varias sesiones son Indistinguibles (optional)

- **Severidad:** OPTIONAL · **Bucket: h** · **Veredicto: OPTIONAL**
- **Ubicación:** `_build_document` (`skills/cdad-cycle/scripts/cdad_context_meter.py:1089` — `unknowns[] = sorted(set(unknowns))` va contra causas de todas las sesiones); los causes agregados del paquete reintroduce (`_coverage_cause`) portan cifras de cobertura («3 of 5») que **varían por sesión**; la sonda de会产生 (2 sesiones) mosaic muestra 2 entradas cache.write con/el suffix diferente (una sin cobertura en sesión A, otra «0 of 2» en B) sin identificar a cuál sesión pertenece.
- **Evidencia:** el spec §2 no obliga atribuir unknowns[] a sesiones — diseño previo —, así que NO viola una postcondición publicada. PERO la reapertura volvió a las causas **más informativas** (cifras de cobertura) y al mismo tiempo **más\(...\)** si no sabes para qué sesión son: una habilidad de la doc de la reapertura persistente es un consumidor no puede accionar/cazar la de la sesión que la produce.
- **Consecuencia:** ambigüedad de evidencia en la salida MULTISESIÓN (default `--limit 20`). El uso previsto de 005-003 pasa por identificar a sesión.
- **Cierre verificable:** atribuir la causa con la `session_ref` hasheada (o mover las causas por sesión a un key por sesión con pivote), más un test que en una corrida de 2 sesiones mixtas distinga las entradas.

### R4 — Documento por defecto MULTISESION: la agregación supera los 16384 publicados, con rc=0 y sin indicador, lo que con solo ES la posición declarada del válido se escribe solo (optional)

- **Severidad:** OPTIONAL · **Bucket: h** · **Veredicto: OPTIONAL (defendible el encuadre del orquestador, con este debug conocido que debe quedarse público)**
- **Ubicación:** la sonda propia: mi store sintético de 2 sesiones de 2 pasos cada una produce un doc de **15.849 bytes** en el modo por defecto — con `--limit 20` (el default declarado de la spec) la salida supera los 16384 **en total** con `rc = 0`.
- **Evidencia:** el texto publicado («Per single-session document», `context-meter.md:215-222`) sostiene el encuadre: es el texto de la spec (el que se emitió en la MUESTRA 1 y PD-12 dice «el documento de la muestra 1») — la norma vuelve que el encaje del orquestador de la imagen está **defensible con el texto**. Pero
  quedan dos defectos documentales requeribles: (i) la numérica NO encuentra referencia UNICAMENTE en el single-session doc, y (ii) no hay medición de tamaño documental. PERO el texto publicado NO prometía el total multiplexado — el uso previsto (005-003 particularmente) -> también son sesiones específicas.
- **Consecuencia:** borde publicado inteligible para el consumidor del placeholder — riesgo de interpretación, no defecto del comportamiento.
- **Cierre verificable:** (declarado en el `reference`, por ejemplo «el total de un documento multiplexado es ≤ N × el límite por sesión, y es el límite POR DOCUMENTO de sesión») o el doc porte un `size_notes` visible; test pequeño que pida la frase.

### R5 — La «consistencia» de E l`edge` «borde alternativo» del fixture de la unidad 2 tiene un `EDGE_PROXY_DEFAULT` que el contrato no pinea — la sonda FUE realmentale de instrumento (optional)

- **Severidad:** OPTIONAL · **Bucket: l** · **Veredicto: OPTIONAL**
- **Ubicación:** `tests/t5_bounded_output.py:116-121`, `:585-594`, `:599-600`, `:768` — un TEST — no es defecto de producto. PERO dentro del test hay 4 cifras de cifras pinneadas (`203276`/`202222`) y aplican también a partir de LEDs — la aseveración del separador 202222/203276 en la MUESTRA DE fixture fuerza `EDGE_TOOL_CALLS=101` tal que el borde alternativo (200 + cada paso) y el penúltimo y último por esta la última posición, al final, la aserción del `previous`+`last` sea ilustrada.
- **Consecuencia:** la cradential de `min/ max` en el fixture (la sonda del fixture) está bien (no de acuerdo a lo predecido declarado, y las dos cifras pinneadas las preserva). La cobertura del aspecto que CIERRA D2 no queda testeada por pulsera nativa de simulación Real: lo ejemplifica la sonda de T5b(1) ## el test 4 fixture de T5b es lo que sigo
  siguiendo (cf. «No pude verificar» (1) abajo). Sin imputación a la cosa: lo declaro como sonda con impacto del test y no del producto.

### R6 — (FYI / sanity de D6 según mandato) — semántica `run.runtime_version` con versiones heterogéneas: el encargo del dueño PIERDE ADECUADO, sin evidencia nueva de compromiso (optional-consider)

- **Severidad:** Optional-Consider · **Bucket: l** · **Veredicto: OPTIONAL**
- **Evidencia:** D6 (debt `:38-40`) sigue abierto; el código lo deja `versions[0]` (sin cambios en la reapertura: el diff no toca esa lógica), y `--session` mixto no lo reporta sin señal. NO expansión de alcance de la reopen: no lo cuento como defecto de la reapertura. NO encontré evidencia de que la correcta ejecución del PR este vía motive revisión de encargo del dueño: el caso requiere `--session` con versiones mixtas de la misma use y no hay test ni insumo de 005-003 que lo consuma hoy.
- **Condición de revisión del encargo:** si 005-003 compara contextos por versión de runtime, entonces el encargo R2 más específico debería revisarse ANTES de que 005-003 dependsa de `run.runtime_version`; hoy no es necesario y no ejecuto daño.

---

## Cobertura punto por punto (A–E del mandato)

### A — «Desconocido no es cero» como clase

**Conforme a nivel de medidas/tramo; NO conforme a nivel del agregador por rol (`roles[]`) → R1 bloqueante.**

- `time_relative` null + causa y medida hermana `unknown`/`null`: **conforme** (T5(1), ambas hitos; `cdad_context_meter.py` `_milestone` `:804-830`, apropiado).
- Proxy por paso (`(x or 0)` eliminado; proxy `null` cuando falta un componente): **conforme** (T5(2)+T5b(2)/(3); el diff con sub-tolerancia del fixture sin tokens-in-incompleteness delContracts — RED两个人的tests pasa).
- `max_output`/`total_output` sin salidas → `unknown`: **conforme** (T5(3); control positivo del 0 Observado T5(3)).
- Agregados `accumulated`/`cache.read`/`cost` (la subclase que el RED detectó): **conforme a nivel de sesión** (T5(7), causa agregada por médida; RED verificado en `6bf350d`).
Sondeo propio del resto de métricas por la misma clase: `segment_duration` (coerción a `None` con `_load_messages`, bucket `unknown`; conforme con el diff previo — sin regresión), `previous_calls`/`previous_reads`/`tool_calls`=0 como CONTEOS observados (0 legítimos, no fabricados; conforme la distinción del reference), `unobserved` (conteo honesto), milestones (cubierto). **La dimensión `roles[]` quedó sin barrer** → R1.
- D6 `run.runtime_version`: FUERA de alcance del dueno — no se cuenta aquí (ver R6 del hallazgo FYI).

### B — (D2) Límite 16384 por documento de sesión en el modo por defecto

**Conforme.** Resumen con forma FIJA objective + `truncated {truncated, cause, omitted_steps, detail_flag}`, `--steps` restaura el detalle completo y define la `truncated=false` con causa; fixture de 1000/4000 pasos: el doc DOE by default queda < 16384 con margen acotado (`SIZE_GROWTH_MARGIN_BYTES=512`), la salida del width y 4000 de difference en un margen acotado (12 tests pass; `T5b(4)`). El `reference` actualiza «Fixing the limit» (`:222+`) y la bandera está documentada en la en la superficie (`context-meter.md:36-40`). La sesión multiplexada queda aparte (R4, optional / disputa del documento publicado).

### C — (D4) Herramientas de despacho reconocidas y ausencia distinguible

**Conforme.** `DISPATCH_TOOL_NAMES = {"subagent","task"}`; el doc pesa top-level `reader.dispatch_tools`; la causa de `absent` nombra el conjunto reconocido y declara el límite («a dispatch made with any other tool is not detected by this reader»); el `reference` abre que un despacho fuera de reconoció NO ocurre; el «task» SE DECLARA en el reconocido con不同程度 (T5(5) cubre `task` reconocido + `dispatch_unknown` reconocido la región absent con causa que nombre resolución [subagent, task]).

### D — (D5) `--session` con match parcial — declarado

**Conforme.** `unknowns[]` causa del parcial («not found», refs hasheadas + refs medidas + «nunca inventa y nunca se silencia») con `rc=0` y la sesión existente medida; sin errores el fallo cerrado conservado (`rc != 0` + stderr diagnóstico, T5(6, la parte final)). El refuerzo del oráculo (`7635a90`) — la causa debe nombrar una referencia hash distinta de todas las referencias medidas — HE EL polarizado y VERIFICADO AL RUN (RED /763 + sonda）； excluye el eco de la ref medida (no mide el ref interlocutivo; la refs y measured refs rollas los dedupes en set; y el número de pasos `estimated` es `len(digest)`=32 coincidiendo el grep de la causa que leá una ref distinta genérica de la misma longitud prefijada por sha256:...) — la dis-denominación está asida sin protección el eco. No se PERDE la invocación (los tests miran el wrapper subproceso y el JSON).

### E — (D3) Oráculo de aceptación según su condición de cierre en debt.md

**Conforme.** Ver sonda E abajo (consistencia en los mismos números, con el conteo exacto del fixture como sonda declarada). La condición de cierre en debt.md decía «pasos >= llamadas o llave de consistencia («el último paso 203.276 y el anterior 202.222»)»; el diff con la experiencia hace AMBAS (`assertGreaterEqual(steps_probe, M1_TRAMO_CALLS)` + `steps[-1]==203276` + `steps[-2]==202222`) y el conteo exacto del fixture-cielo (=102) reside como sonda declarada en `T2` y `T5b(1)`. El estilo decorativo del instrument lo tiene el test (real-only y fixture). La MUESTRA REAL en em powder real corre en el modo RED (++, noは no [ver «No pude verificar» (1)]).

---

## Respuestas a los 6 puntos del orquestador

**1. Resumen por defecto (count/last/previous/min/max/unobserved) + indicator `truncated {truncated,cause,omitted_steps,detail_flag}` — ¿mantienen PD-5/PD-12/PD-16 sin perder las cifras pinneadas (203.276 / 202.222)?**
**Sí, conformes.** `T5s matches test existence`: el por defecto统计分析 `count` (дистribución de tamaño fijo + último/penúltimo) mantiene el my Manifndo fingers 203.276 (`last`) y 202.222 (`previous`/`penúltimo paso con herramienta`) — tanto en el doc POR DEFECTO (`T5b(1)`) como con `--steps` (`T5b(3)` y `t4` real-чила). El `previous` null con `unobserved` counting honesto. El indicador declarado en la hoja de la medida es compatible con el asset (`truncated` añadido) y con PD-8/PD-16 (medidas`: カ نگöglich shape: value/unit/provenance/bucket`). La frase decide como fixture «nicas».
**Texto del spec qué se pierde:** nada — PD-12 con la (menciona)s «el documento lleva referencias (session + step/seq)» sigue acuérdose por milestones.position.call_index/seq en por defecto.

**2. Hito observado con `time_relative` null + causa y la medida hermana `unknown` — ¿es la lectura correcta de PD-3/PD-4/PD-16 o degrada una observación que debería conservarse?**
**Lectura correcta; no degrada — conservación REAL.** El posición (`call_index`/`seq`) queda observed y Visible (PD-6 la exige), el tiempo es desconocido con causa (PD-3/PD-4/INV-4), y PD-16 («`time_relative` obligatorio si observed») se cumple porque la clave existe con valor `null` y la asset la amplió a `["number","null"]` SIN quitar la obligatoriedad. La alternativa (degradar el hito a `unknown`) HABRÍA PERDIDO la posición, que es lo que pinea el contrato — el diseño en la reunapertura es honesta en validation, no degrada. El asset extiende el tipo; los tests aplican ambos hits (T5(1)).

**3. Bucket de los agregados parciales (`unknown` con causa agregada) y de `input_per_step` en modo resumen (`estimated` con `unobserved`) — ¿asignación disjunta y honesta (PD-1/INV-4)?**
**Disjunta y honesta a nivel de sesión** (T5(4) barrido: ninguna medida `observed` con value null; `unknown` con value null; aggregates parciales `unknown` (value null, causa con cobertura)); el нового продукта: `input_per_step` queda `estimated` TAMBIÉN cuando TODOS los proxies son no observables (`T5b(2)`) — el viejo design la convertía en `unknown`; el nuevo comportamiento es corrección formalizable y honesta porque NULLs declarados (`unobserved`+causas en `unknowns[]`), la medida sigue siendo un proxy declarado porолн. Es una decisión INTERFAZ con el mierto de nuevo va well-hidden en el reference y el asset (el $def). Conforme; es **asymmetric**: el mismo principio hace completo al valor `unknown` para el AGREGADOR de roles (`roles[].sums`) — corredó BACK a R1, que es el hallazgo de la revisión.
**Con la marca de `roles[]` el número no cae en la pantalla** (sin bucket, sin ninguna declaración, porque un SOTF válido ya el bucket con sistema perdente).

**4. La extensión del asset — `time_relative` nullable, `reader`, medida `truncated`, `value` anyOf — ¿permisiva de verdad, sin quitar claves ni romper PD-16, o es un colador?**
**Sin quitar claves: sí.** `time_relative` preformado: `number`, ahora `["number","null"]` (permisiva — no pierde la obligatoriedad «observed» y la forma del Cause optional); la clave `reader` es optional y `additionalProperties: false` «disponible» en su interno; la medida gana `truncated` SIN(apiaries) todos los cimientos de `measure` (dado `value/unit/provenance/bucket`), `additionalProperties: false` queda vigente a ambos en el productore. PD-16 no se rompe (además la leitura y tests lo confirman, «5b1 ...` untouchables»).
**¿Convertirse del colador? parcialmente (R2):** la rama `{"type":"object"}` de la `anyOf` de `value` hace que cualquier objeto sea accepted (la `$def` del summary no-binding, además que lunes la cualificada es la requirements seule una entrada). Es un cañón del APETJO del sistema pidiendo sea la protegí: el daño para el asset minos ese "$def"sua permitiendo `input_per_step_summary`: es un descriptor del contrary, no enFORCE — con los tests SÍ enforceables. El colador-ish ventaja real es el contrato de la medida.

**5. El límite de 16384 en corridas MULTI-sesion (`--limit N` sin `--session`) — ¿fuera de alcance con el texto publicado?**
**Defendible con el texto publicado** (el `reference` Y LA SPEC fijan el límite por documento de la muestra/por sesión a la única referencia de la norma, y der artículo PD-12 «el documento emitido para la muestra 1 está por debajo» imprescircular a session único; y el default publish declarations, así que esa redela se broatt anti Therefore WITHOUT common-looking — no declarado «output is compact and bounded» que es PARTE de lo, nunca un total cuando N>1 sesimientos. NO compromete porcos. **Residuo que recomiendo a documentar antes del consumo 005-003:** la probe para dos sesiones del tipo de« de la session él está en el metacon «session = a午后#5» («R4 el cierres naturales que mi propio store: el placeholder «RT S necessary» (de pass acá en 005-003 hay una misma (R4 optional con cierre en la prórrogación del article y regla documentada de N×16384).

**6. Cobertura del límite con fixture sintético (1000/4000) — ¿alcanza cómo evidencia?**
**Alcanza para el eje de crecimiento que definió D2** (los PASOS del tramo, el defecto original: lineal pasando por `input_per_step` completo): el fixture sintético pequeño (1000/4000) a cada escala «por defecto 16384 en 16384, más growth acotado», y el margen de la representación en la (pågla un punto en 512). **NO es exhaustiva**, prohed el resto de ejees del documento: presentación- que los tools de la session (por cada herramienta («tool names» de la session; typical ≤50 → la dictadurdad sin el emjet en ~1.2KB; caso patológico de cientos de nombres MCP no testeado), y la recursión adoption de `unknowns`[] en multiplexado en el doc de >15 Kb. No fui se reproduce un store realista que la cruce; por eso la推迟 de este punto (probe statement) es UNA ONLY candela sentido: se dice al gusto del mandato que «se exijo» lo que fue modelo?

---

## Auditoría de debilitamiento de tests aprobados (commit por commit)

- `tests/test_005_002_t1_neutral_record.py` y `t3` — **intactos** (los commits de la reapertura no los mueven).
- `t2_milestones` (`f22d292`): los subtests (e) e (i)/`PD-8(i)` cambia el MODO de la corrida de la lista `input_per_step` al modo `--steps` (interfaz de la unidad 2); las aserciones (`len(steps)==102`, `bucket estimated`, unidad) NO cambian — se conservan.
- `t4_acceptance` (`f22d292`): el oráculo de ambas corridas (fixture y base real) usa la `(d)` corriendo con `--steps`; la única relajación es «pasos ≥ llamadas» (D3, definida en debt: la condición de cierre) y el exacto conteo 102 del FIJTURE queda como sonda declarada en `T5b(1)` y en t2; `max_output=51243`, ventana, borde, el `#19` etc. TODAS quedan pinneadas intactas.
- `t5_unknown_declared`: creado por la reapertura (RED de `0083d82`+`6bf350d`); el estre que confirma su oráculo (`7635a90`) y la alineación de `b89252f` (solo cambia INVOCACIÓN por la bandera, las aserciones quedan idénticas: texto del diff garantizado: «las aserciones de contrato no se relajan ni se agregan»).
- `t5_bounded_output`: 4 tests; NO de product unchanged - es nuevo.

**Conclusión:** ningún test aprobado cedió en contrato: las relajaciones siguen las condiciones de cierre D3 y el resto es movimiento de modo por la interfaz `--steps` con aserciones intactas.

---

## Lo que NO pude verificar (obligatorio declarar)

1. **La corrida de la INTEGRACIÓN REAL de T4 (5 tests) NO la corrrí: no hay variables de entorno** (`CDAD_CONTEXT_METER_REAL_STORE`, `CDAD_005_002_M1_SESSION_ID`, `CDAD_005_002_S2_SESSION_ID`) — module skip con diagnóstico. Por eso las cifras pinneadas SOBRE LA BASE REAL (203.276/202.222, 12,55/12,40, 101/121, 51.243, `#19`, desglose) en los dos modos quedan confiadas a los recibos del implementer/orquestador (los commits de `7b044...` y ac77528 dicen «integración real 5 passed»); no las reproduje.
2. **No abriéndo la base REAL de sesiones TODO** (store declarado 4,67 GB): mi cobertura de la clase D1/D2 es sobre fixtures sintéticos + lectura del código; no publiqué identificadores y no toqué el store.
3. **El RED de la unidad 2 con la bandera `--steps` ya inexistente** seRED y verificado → NO darkness flag bc; FMI.
4. **La cruising borrar del la session de la multiplexada (R4)** es una sonda punto-prueba (2 sesiones sintéticas), no un un barrido exhaustivo de todas las combinaciones de causas.
5. **No cambié ni aprobé nada** — mi write scope está empty y el repo quedo SIN writes míos (el `docs/.cdad-state.json` modificado en el working tree es del orquestador en paralelo, no mío; no lo auditó esta review).

---

## Dictamen para el orquestador

**1 bloqueante (R1 — `roles[].sums` subtotal parcial presentado como completo) + 5 opcionales (R2 `anyOf` colador del summary en el asset; R3 unknowns[] sin atribuir sesión; R4 tamaño del doc multiplexado; R5 sonda del fixture de la unidad 2; R6 FYI D6 encargo vigente) · 2 abstenciones declaradas por evidencia faltante Real (integración T4 no corrida por falta de secretos; base real abierta).**

Bajo el criterio VIGENTE de 2026-10-12, la reapertura **conforma los cinco puntos que se propuso (A a nivel de sesión/tramo, B, C, D, E) con test focales verdes, RED verificada en 3 puntos, y sin debilitamiento de tests aprobados**, PERO la clase «desconocido no es cero» sigue viva (exaktno el ejemplo del criterio que motiva el bloqueo) en el agregador por rol `roles[].sums`: un subtotal parcial PRESENTADO como número completo, sin (i) cubo, (ii) declaración de cobertura ni (iii) causa — se recomienda arreglado con la condición de cierre verificable de R1 antes del cierre de 005-002 (el instrumento de la salida que 005-003 va a consumir). REcomendado, bajo cerrar la reapertura, tomar la decisión de si R1 es bloqueante para el CIERRDOCTYPE acne(CR) o insum para 005-003 antes del cierre.