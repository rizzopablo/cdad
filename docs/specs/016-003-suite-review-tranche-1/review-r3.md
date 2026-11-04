```markdown
# review-r3.md — 016-003, tramo 1 (tercera pasada, cierres)

**Paquete:** ruta C, `016-003-suite-review-tranche-1-reviewer-review-003`. Verificado antes de trabajar: una sola identificación de ruta C, que coincide con `validate-request` (rc 0), con `render` byte a byte idéntico a `PACKET.md` y con `render --route C`; contrato `b3f91691…` igual al archivo. Sin escrituras en el repo; temporales en `/tmp/opencode/review-016-003-r3`.

## Veredicto

**aprobado con observaciones.** Los seis cierres se sostienen contra los archivos y la aritmética cierra al decimal (unión 8.692,5 s, fijos 1.700,5 s, resto 29.986,6 s, tokens y caché exactos contra el runtime). Queda una sola cifra mal escrita, en dos documentos: `report.md` §4 y `decision.md` dicen «cuatro bloques de preparación compartida» cuando el archivo tiene tres, y la enumeración suma 23 sesiones donde el propio informe declara 22. Es una corrección de una línea en cada archivo; no afecta ningún total ni postcondición.

## Estado de los cierres

### B1 — `commands_s` huérfano · **cerrado**
- Existe la actividad `cierre del tramo: verificación, costo y decisión` (`ses_orquestador_cierre`), con **31 comandos**, todos con `duration_s`, que suman **41,44 s** exactos = `totals.commands_s`.
- `totals.commands_note` dice que ese bloque es la única fuente; `commands_measured` repite 31 y aclara que los comandos de los lotes no se midieron y **no se computan como cero**.
- La actividad fantasma de «selección congelada y materialización» ya no existe (grep sin resultados en `costs.json`, `report.md` y `decision.md`).
- `report.md` §4 y `decision.md` reescribieron las cifras: 17 actividades de auditoría, revisión, cierre y preparación separados. Sin residuos de «14 actividades», «891,2», «8.326,6» ni «1.244,8» (grep vacío).

### B2 — GREEN-002 · **cerrado**
- `duration_s` 1.040,2 s = `ended` (01:19:31) − `started` (01:02:11), y el `ended` coincide con el **último mensaje de la sesión** en `session_v2` (01:19:31,97). `duration_s_receipt` 615,1 se conserva con su explicación (`measurement`): recibo de entrega frente a intervalo completo.
- **Solapamiento declarado y real:** `overlap_with` apunta a `<ses-368>` (fixture de R-F) con 90,1 s; la sesión del fixture (01:12:39–01:14:09) cae íntegra dentro de GREEN (01:02:11–01:19:31) → intersección exacta **90,1 s**.
- **`aggregated_s` es unión, no suma:** recalculé la unión de los 22 intervalos desde los timestamps → **8.692,5 s**, idéntico al declarado; `sessions_sum_s` 8.782,3 = suma cruda; 8.782,3 − 90,1 = 8.692,2… y la unión medida da 8.692,5 por los bordes de intervalo. La afirmación «la unión evita el doble conteo» se verifica.
- **Totales derivados correctos:** preparación 174,3 + 90,1 + 1.040,2 = **1.304,6** ✔; `fixed_s` 1.304,6 + 353,6 + 42,3 = **1.700,5** ✔; proyección 28.286,1 + 1.700,5 = **29.986,6 s ≈ 8,3 h** ✔.
- `elapsed_s` 9.643,7 = intervalo 00:43:45 → 03:24:29 ✔ (no cambia al extender GREEN, porque el máximo sigue siendo la revisión).

### O1 — distribución por promesa · **cerrado**
`audit.json` da **48 B, 43 A, 42 C, 34 D, 13 E, 7 F y 211 nombradas**; `report.md` §2 dice exactamente eso. Sin rastro de «21 `E`».

### O2 — caché · **cerrado**
- Cada actividad con métricas declara `cache_read`/`cache_write` dentro de `tokens`; contrasté **las 21 entradas con sesión resoluble** contra `session_v2`: **coinciden las cuatro cifras en todas** (0 diferencias).
- Totales: entrada 2.716.861 · salida 702.509 · caché lectura **92.903.503** · caché escritura **117.392**, idénticos a la suma de la base del runtime.
- Un supuesto declara que `cache_read` domina el volumen y no se tarifa como entrada; `report.md` §4 y `decision.md` lo publican como fila propia («dominan el volumen real»).

### O3 — fila 334 · **cerrado**
El motivo ya no afirma la no-cobertura: declara que los insumos difieren, que ante incertidumbre R2 ordena Mantener y que S2 queda «registrada … como examinada y no promovida a candidato: sin experimento de sensibilidad comparada no se promueve ni se descarta», con la evidencia que faltaría (quitar legacy-unowned y su recíproca). Coherente con `suspicions.json` S2 y con la nota del archivo. `candidates.json` sigue `[]`.

### O4 — fila 142 · **cerrado**
La primera aserción ya no es `assert_concepts(`: cita el par exigido `variante ausente o no publicada`, que aparece **2 veces en el cuerpo de su función** (el par y el mensaje del subTest). Las otras dos siguen siendo literales.

## Hallazgos nuevos

### N1 — «cuatro bloques de preparación» contra tres que existen · **Required**
- **Verdict: OPTIONAL (el dueño decide) · Bucket: h**
- **Dónde:** `report.md` §4 (línea 58) y `decision.md` (línea 29).
- **Qué dice:** «…y cuatro bloques de preparación compartida (RED-002, RED-003, GREEN-002 y la corrección del validador)»; `decision.md`: «el bloque de cierre con 31 comandos medidos y **4 bloques** de preparación compartida».
- **Qué hay:** `costs.json.shared_preparation` tiene **3** entradas: `corrección de producto: RED del validador legacy` (174,3 s), `corrección de producto: fixture de R-F` (90,1 s) y `corrección de producto: GREEN del validador legacy` (1.040,2 s). El cuarto nombrado («la corrección del validador») es el mismo que «RED-002»: la corrección del validador se cuenta dos veces. Además, la enumeración 17 + 1 + 1 + 4 da **23 sesiones**, y los dos documentos y el archivo declaran **22**.
- **Consecuencia:** un lector del informe —o del memory bank— cuenta cuatro bloques de preparación y 23 sesiones; el artefacto tiene tres y 22. Es la misma clase de defecto que B1 (texto contra archivo), de magnitud mucho menor: ningún total está mal, solo la descripción.
- **Cierre verificable:** «cuatro» → «tres» en los dos archivos y quitar de la enumeración el bloque duplicado (dejar RED del validador, fixture de R-F y GREEN del validador); `grep -c "4 bloques\|cuatro bloques"` → 0.

### N2 — el id de sesión del cierre no resuelve en el runtime · **FYI**
- **Verdict: OPTIONAL · Bucket: h**
- `cierre del tramo` usa `"session": "ses_orquestador_cierre"`, que no existe en `session_v2` (consulta directa: sin fila). Los tokens se declaran «no disponibles», lo que PC-7 admite expresamente (distingue ausencia de cero), y los comandos son reconstruibles. Pero «22 sesiones» cuenta un rótulo, no una sesión verificable.
- **Cierre opcional:** renombrar al id real de la sesión del orquestador o declarar explícitamente que es un rótulo sin id de runtime.

### N3 — seis filas citan texto que solo existe en otro test del módulo · **Optional/Consider**
- **Verdict: OPTIONAL · Bucket: h**
- Al medir literalidad **por cuerpo de función** (más estricto que la pasada anterior, que medía por archivo) aparecen **16 filas** con algún fragmento fuera de su función. En 10 el fragmento vive en un helper que la fila ejecuta (p. ej. `_assert_ambiguous_block`, `_assert_sucesor_captura_vigente`): la aserción se ejecuta, aunque no esté en el cuerpo del test. En **6** vive **solo en un test hermano** que la fila no ejecuta: filas **49, 138, 385, 391, 394, 397** — p. ej. la 138 cita `TransactionCase` y la 397 cita `PolicyError`/`containment`, identificadores más que aserciones.
- **Consecuencia:** esas seis no evidencian por sí mismas la promesa que declaran; el validador no lo controla y el informe §2 ya declara ese límite, así que la entrega no lo oculta. No es una regresión de estos fixes: es el residuo de la clase «literal pero genérica» que señalé en H3/O4 y que quedó intacta.
- **Cierre verificable:** sustituir en esas seis filas el fragmento por una aserción ejecutada por la propia fila, o declararlas en el informe como citas de módulo.

## Controles re-ejecutados

| Comando | Resultado |
| --- | --- |
| `cdad_packet.py validate-request` / `render` / `render --route C` | rc 0; `PACKET.md` byte-idéntico; identificación igual |
| `pytest --collect-only -q tests/` | 1.994 nodeids |
| `cdad_suite_review.py validate` (tramo + 26 registros) | rc 0 · `ok` · 398 filas · 0 candidatos · 0 errores |
| `cdad_contract_links.py validate` 016-003 con baseline | rc 0 · `new_unlinked: []` · `gaps: []` |
| `cdad_contract_links.py validate` 016-003 sin baseline | rc 0 · 10 obligaciones |
| `cdad_contract_links.py validate` los 26 registros, colección viva | 26/26 rc 0 |
| `pytest tests/test_016_001* test_016_002* test_016_003*` | **22 passed** |
| Recálculo de duraciones, unión y solapamiento desde `costs.json` | unión 8.692,5 = declarada; overlap 90,1 = declarado; `duration == end−start` en las 22 entradas |
| Recálculo de tokens (entrada, salida, caché) contra `opencode.db` | 21/21 sesiones exactas; totales 2.716.861 / 702.509 / 92.903.503 / 117.392 |
| `commands`: conteo y suma del bloque de cierre | 31 comandos, 41,44 s, todos medidos |
| Proyección | 28.286,1 + 1.700,5 = 29.986,6 s ≈ 8,3 h |
| Distribución de promesas desde `audit.json` | 48/43/42/34/13/7 + 211 |
| Literalidad por función sobre 398 filas (AST) | 0 fragmentos ausentes del módulo; 16 filas con cita fuera de su función (6 solo de test hermano) |
| `git status --short` | solo `docs/.cdad-state.json` (ya modificado antes) |

Sin escrituras ni commits: `review-r3.md` no se materializó en el repo.

## Límites de esta pasada

- **No releí semánticamente las 398 filas.** De esta pasada solo reabrí las filas 334 y 142 y repetí el control mecánico de literalidad; el resto sigue apoyado en la muestra de la primera revisión.
- **Corrijo un método de mi pasada anterior:** allí dije «0 fragmentos no literales» midiendo por archivo. Medido por cuerpo de función hay 16 filas con citas fuera de su función (N3). La conclusión de H3 (los seis fragmentos reemitidos son literales) se mantiene; la afirmación más fuerte no.
- **No verifiqué la pertinencia semántica de los 26 registros de vínculo** ni la de cada fila contra su contrato; solo que validan rc 0 y que el SHA256 del contrato coincide.
- **No re-corrí la suite completa** (no la exige el ciclo focal); ejecuté los tres módulos de la feature y sus dos antecesoras, que es lo que el informe cita.
- **No verifiqué si el bloque de cierre corrió realmente en la sesión principal del orquestador** (N2): el runtime no expone tokens de esa sesión y el archivo declara la ausencia.
- **No revisé línea por línea todo el informe:** barrí con grep las cifras viejas que el paquete enumera y leí §2, §4, §5 y §7 completos y `decision.md` completo.

## Abstenciones

- **Si «Mantener» es la disposición correcta en las 398 filas:** no me pronuncio fuera de la muestra contrastada.
- **Si las seis filas de N3 comprometen la promesa que declaran:** requeriría lectura semántica fila por fila; el control mecánico no lo decide y no lo declaro.
- **Si S1, S2 y S3 son redundancias reales:** no lo declaro; falta la evidencia experimental que cada una describe y el trámite es del dueño.
- **Si el umbral del 30 % de `decision.md` se mide contra auditoría sola o contra el costo fijo:** la cifra «7,9 h de auditoría» está bien usada para auditoría; la lectura del umbral es decisión del dueño.
- **Si el rótulo `ses_orquestador_cierre` debe llevar el id real:** N2 no cambia ningún total; lo dejo como observación.
```

Con esto queda cerrada la re-revisión: los seis cierres verifican contra los archivos y la aritmética cierra; solo N1 (tres bloques, no cuatro) pide una corrección de texto antes de que el cierre de la feature se apoye en `report.md` y `decision.md`.
