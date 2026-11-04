```markdown
# review-r2.md — 016-003, tramo 1 (re-revisión, etapa 4)

**Paquete:** ruta C, `016-003-suite-review-tranche-1-reviewer-review-002`. Verificado antes de trabajar: `validate-request` → rc 0; `render` byte a byte idéntico a `PACKET.md`; `render --route C` coincide con la identificación recibida (packet_id, execution_id, contract y sha256 `b3f91691…`, igual al archivo real). Sin escrituras en el repo; temporales en `/tmp/opencode/review-016-003-r2`.

## Veredicto

**rechazado.** Cuatro de los cinco hallazgos están cerrados y el núcleo del tramo (selección, 398 filas, vínculos, validadores) resiste la re-ejecución; pero `costs.json` y `report.md` §4 todavía acreditan costo que no está en el archivo: la actividad de cierre que sostenía los 41,44 s desapareció sin reemplazo, y una duración de sesión está truncada 425 s con solapamiento real de 90 s — justo lo que PC-7 prohíbe («evita doble conteo de trabajo paralelo»). Son dos correcciones puntuales, no rehacer el tramo.

## Estado de los hallazgos

### H1 — vínculo de R_F · **cerrado**
- `contract-test-links.json` tiene **6 vínculos**; el nuevo es `test_R_F_contrato_sin_marcadores_resuelve_por_indice_legacy` con `pc_ids: [PC-3, PC-4]`.
- Colección viva generada con `pytest --collect-only -q tests/`: **1 994 nodeids** (coincide con lo declarado). `cdad_contract_links.py validate --registry <016-003> --collection <viva> --baseline tranche-1/collection.json` → **rc 0**, `status: ok`, `new_unlinked: []`, `gaps: []`, obligaciones PC-3 y PC-4 con los dos verificadores.
- Los dos `evidence` resuelven: `sha256` del archivo `c59cc32a…` coincide; cada `locator` aparece **exactamente una vez** (`grep -c` = 1, líneas 674 y 730).
- `limits` dice «Estructural; no acredita pertinencia semántica … ni sensibilidad»: no promete detección semántica. ✔
- El informe §3 ya no cita el rc 0 sin baseline y describe el rc 1 anterior. ✔

### H2 — costo · **cerrado parcialmente**
Lo que **sí** cierra, verificado contra la fuente (base de sesiones del runtime, `session_message`):
- **Tokens exactos, fila por fila, 21/21.** Ejemplos: B1a 208 822/32 216 · audit-018 203 561/14 677 · revisión 64/16 364 · GREEN 110 394/21 138. Totales 2 716 861 / 702 509 = suma exacta.
- **Separación de totales correcta:** 7 081,8 + 353,6 + 891,2 = **8 326,6**; 17 actividades de auditoría (piloto incluido) + 1 revisión + 4 preparación = **22 sesiones**. Las listas de `nodeids` por actividad son subconjuntos reales de la selección (871 menciones = 398 únicos + 398 de la revisión + 70 del piloto + 5 de la reemisión): el excedente está explicado, no es doble conteo.
- **Reloj:** 9 643,7 s = intervalo real 00:43:45 → 03:24:29. Los intervalos **declarados** no se solapan.
- **Proyección:** 1 590 × 17,79 = **28 286,1 s** ✔; fijos 891,2 + 353,6 = **1 244,8** ✔; total **29 530,9 s** ≈ 8,2 h ✔. Los supuestos declaran explícitamente que **no es muestra aleatoria**, que es **cota alta**, que no descuenta los cambios de método y que el costo experimental queda sin calibrar. Eso responde a lo pedido.

Lo que **no** cierra (detalle en B1 y B2 abajo):
1. `totals.commands_s` = 41,44 s no tiene respaldo: la actividad «cierre del tramo» con 31 comandos existía en `77717c1e` y **ya no está** en el archivo; los 41,44 s solo se mencionan en `totals` y en el texto.
2. `corrección de producto: GREEN del validador legacy` declara 615,1 s; la sesión real abarca **1 032,3 s** (último turno del implementer 01:19:23, 425,2 s después del fin declarado) y se solapa **90,1 s** con la sesión del fixture RED (01:12:39–01:14:09).
3. La actividad «selección congelada y materialización» declara 11,7 s y sus marcas 03:15:26–03:16:08 son del turno de cierre: `selection.json` se commiteó a las 01:29 UTC (`4a8cce87`, 22:29:10−03:00), 1 h 46 min antes.

### H3 — seis filas no literales · **cerrado**
- Recorrí **las 398 filas**: para cada fragmento de `check.assertions` cuento su aparición **en el cuerpo de su propia función** (AST) → **0 fragmentos no literales** (antes 6). Las seis filas reemitidas (`010-002` ×4: texto 142, 143, 151, 152; `008-001` ×2: 347, 358) aparecen todas al menos una vez en su función.
- Las filas que había señalado como «literales pero genéricas» (`010-001` 366→367, `010-004` 383→384, `010-000` 395→396 y 397→398) **quedaron intactas**: el `git show 77717c1e:audit.json` contra el actual da 25 filas cambiadas, 6 de `check` y 19 de `motive`, y ninguna de esas cuatro está entre ellas. Ver O4.

### H4 — motivos plantilla · **cerrado**
- El texto completo de `audit.json` da **0 ocurrencias** de «Señal ya cubierta por su variante dedicada» y **0** de «ninguna otra fila del tramo la protege».
- Las 18 filas de `007-006` y la de `009-001` (S2) tienen motivo propio y **cada uno nombra la señal o el caso de su `param`**: `context-unreadable` → contexto v2 corrupto; `second-destination-directory` → directorio tras reemplazo parcial y contraste con `destination-read-only`; `dispatch-identity-absent` → registro sin `packet_id` frente a `dispatch-registered`; `materialization-unreadable` → corrupción frente a `registered`. Ver O3.

### H5 — inconsistencias de texto · **cerrado parcialmente**
- `decision.md` ya no dice «dos defectos de producto»: ahora dice «un defecto real de producto … y dos defectos de forma». ✔
- `report.md` §6 tabula **seis** defectos con naturaleza (producto / forma de la entrega / trazabilidad) y estado. ✔
- §7 declara `ad15c58a` → `120fa8b9` y la verificación es **correcta**: `select` sobre ambas revisiones da la **misma lista de 398** y es byte-idéntica a `selection.json`. ✔
- **Quedan dos afirmaciones sin sostén** (B1 y O1): el párrafo de §4 y la distribución por promesa de §2.

### S1, S2, S3 · **registradas correctamente**
- `experiments/suspicions.json` contiene las tres, con `hypothesis`, `why_not_promoted` y `evidence_needed`; la nota dice explícitamente que **no** se promueven y que sin evidencia experimental **no se declara redundancia**; `candidates.json` sigue `[]` y `manifest.json` declara `candidate_count: 0`. No se presentan como prueba. ✔
- Única tensión: O3.

## Hallazgos nuevos (introducidos por los fixes)

### B1 — `commands_s` huérfano y §4 autocontradictorio · **Critical de evidencia**
- **Verdict: BLOCKING · Bucket: h**
- **Dónde:** `tranche-1/costs.json` (`totals.commands_s`, `totals.commands_note`), `report.md` §4 (párrafo previo a la tabla), `decision.md` («Evidencia de costo»).
- **Qué verifiqué:** `totals.commands_s` = 41,44 s con la nota «solo los comandos medidos (actividad de cierre)». En el archivo **no hay actividad de cierre**: la entrada de las 03:15 es «selección congelada y materialización», con **un** comando de 11,7 s. En `git show 77717c1e:…/costs.json` sí existía «cierre del tramo: verificación, costo y decisión», 42,3 s y **31 comandos** — de ahí salían los 41,44 s. La versión nueva la reemplazó por la selección, sin conservar el bloque ni los comandos, y dejó las referencias en `totals`, en `report.md` §4 («más una actividad de cierre con 31 comandos medidos individualmente») y en `decision.md`.
- **Consecuencia:** PC-7 pide reconstruir costo por actividad, sesiones **y comandos**; los 41,44 s ya no son reconstruibles desde el archivo, y §4 se contradice con su propia tabla («14 actividades» en el párrafo, «17 actividades» en la fila). Es la misma clase de defecto que H1: el texto acredita lo que el archivo no tiene.
- **Cierre verificable:** restaurar la actividad de cierre (con sus 31 comandos y 42,3 s) o eliminar `commands_s`, su nota y las tres menciones; corregir «14» → «17»; reejecutar el validador del tramo (debe seguir rc 0) y `git diff` sin tocar `audit.json` ni `selection.json`.

### B2 — duración de GREEN-002 truncada y solapamiento no declarado · **Critical de evidencia**
- **Verdict: BLOCKING · Bucket: h**
- **Dónde:** `tranche-1/costs.json`, bloque `shared_preparation`, entrada `corrección de producto: GREEN del validador legacy`.
- **Qué verifiqué:** declara `started 01:02:11` / `ended 01:12:26` / `duration_s 615,1`. La sesión (`<ses-369>`) va de **01:02:19 a 01:19:31** = **1 032,3 s**, con turnos del implementer hasta 01:19:23. Las otras 20 entradas tienen su fin declarado a ≤63 s del último mensaje; esta es la única desviada, **+425,2 s**. Además, con el intervalo real la sesión se solapa **90,1 s** con `corrección de producto: fixture de R-F` (01:12:39–01:14:09), que sí figura contada completa.
- **Consecuencia:** la preparación compartida real es ≈1 339 s y no 891,2 s (+50 %), el costo fijo ≈1 692 s y no 1 244,8 s (+36 %), y la afirmación «lotes secuenciales: sin doble conteo» deja de valer para el trabajo paralelo, que es exactamente lo que PC-7 prohíbe. El 30 % que `decision.md` fija como umbral de revisión de la proyección queda superado por el propio error de medición.
- **Cierre verificable:** recalcular con el intervalo real de la sesión (615,1 → 1 032,3) y declarar el solapamiento de 90,1 s —o, si el fin 01:12:26 corresponde a un recibo de entrega, citarlo como fuente y declarar el tramo 01:12:26–01:19:31 como actividad aparte— y actualizar `preparation_s`, `aggregated_s`, `fixed_s` y la proyección. Alternativa legítima: dejar los números y declarar explícitamente la base de medición y que el solapamiento no se descontó.

### O1 — distribución por promesa del informe no coincide con `audit.json` · **Required**
- **Verdict: OPTIONAL (el dueño decide) · Bucket: h**
- **Dónde:** `report.md` §2, primera viñeta.
- **Qué verifiqué:** `audit.json` da **48 B, 43 A, 42 C, 34 D, 13 E, 7 F** y 211 promesas nombradas. El informe dice «48 `B`, 43 `A`, 42 `C`, 34 `D`, **21 `E`**, **13 `F`**». Las cuatro primeras coinciden; las dos últimas no (21/13 frente a 13/7). No encontré criterio alternativo que reproduzca 21 y 13: ni por `obligation`, ni por letra en `pc_ids`.
- **Consecuencia:** un número del informe que su propio artefacto no sostiene; en una entrega documental el informe es producto.
- **Cierre verificable:** corregir a 13 `E` / 7 `F` (o declarar la regla de conteo que da 21/13).

### O2 — los tokens omiten `cache_read`, que es el volumen dominante · **Optional/Consider**
- **Verdict: OPTIONAL · Bucket: h**
- **Dónde:** `costs.json` (campos `tokens`), `report.md` §4 (fila de tokens).
- **Qué verifiqué:** todas las entradas declaran solo `input`/`output`. La base del runtime expone además `cache.read`: B1a 8 950 449 · audit-003 3 495 607 · B3 5 386 236, del orden de **40×** el input declarado. El archivo dice «tokens cuando el runtime los expone» y el runtime los expone.
- **Consecuencia:** el «costo reconstruible» de PC-7 se lee en input/output, pero quien planifique el tramo 2 con estas cifras subestima el volumen real de tokens en un orden de magnitud (el costo monetario depende del precio de caché). No rompe ninguna postcondición literal.
- **Cierre verificable:** agregar `cache_read`/`cache_write` por actividad, o declarar en `limits` que se omiten y por qué.

### O3 — la fila 334 declara la conclusión que `suspicions.json` difiere
- **Verdict: OPTIONAL · Bucket: h**
- **Dónde:** `audit.json` fila 334 (`test_pc3_legacy_unowned_overlay_conflict_is_adopted_on_update`), frente a `experiments/suspicions.json` S2.
- **Qué verifiqué:** el motivo dice «sospecha S2 examinada y no promovida … **ningún verificador alternativo cubre la rama de adopción legacy**». S2 dice que eso mismo requiere experimento («sin experimento de sensibilidad comparada no se promueve») y la nota del archivo afirma que «sin evidencia experimental no se declara redundancia». «Examinada» también sugiere un examen que no ocurrió.
- **Consecuencia:** se introduce por fila una afirmación de no-redundancia sin la evidencia que el propio registro pide; PC-6 protege la dirección inversa, pero la coherencia del registro es el sostén de la decisión.
- **Cierre verificable:** quitar del motivo la conclusión de no-cobertura y dejar «insumos distintos; sin experimento comparado se mantiene», o agregar la evidencia que S2 lista.

### O4 — residuo de H3: un fragmento literal pero genérico en la fila 142
- **Verdict: OPTIONAL · Bucket: h**
- **Dónde:** `audit.json` fila 142, primera aserción: `assert_concepts(`.
- **Qué verifiqué:** es literal (aparece 4 veces en la función) pero es el **nombre del helper**, no una aserción; pertenece a la misma clase que las cuatro filas que señalé como «literales pero genéricas». Las otras cinco reemitidas sí citan aserciones reales (`self.assertEqual(self.current_stack(project), "odoo")`, `"did not answer within"`, etc.).
- **Consecuencia:** ninguna material; queda como muestra del límite que el propio informe §2 declara (el validador no comprueba literalidad ni pertinencia).
- **Cierre verificable:** sustituir por la aserción observable de la llamada (p. ej. el par `("variante ausente o no publicada", UNPUBLISHED_VARIANT)`).

## Controles re-ejecutados

| Comando | Resultado |
| --- | --- |
| `cdad_packet.py validate-request` / `render` / `render --route C` | rc 0; `PACKET.md` byte-idéntico; identificación igual |
| `pytest --collect-only -q tests/` | **1 994** nodeids |
| `cdad_contract_links.py validate … --collection <viva> --baseline collection.json` | rc 0 · `new_unlinked: []` · `gaps: []` |
| `cdad_contract_links.py validate` sobre los **26** registros del proyecto, colección viva | **26/26 rc 0** |
| `cdad_suite_review.py select --revision 120fa8b9…` | 398 · byte-idéntico a `selection.json` |
| `cdad_suite_review.py select --revision ad15c58a…` | 398 · **misma lista** que 120fa8b9 |
| `cdad_suite_review.py validate` (tramo + 26 registros) | `ok`: 398 filas, 0 candidatos, 0 errores |
| `pytest tests/test_016_001* test_016_002* test_016_003*` | **22 passed** |
| Recálculo de tokens/duraciones contra `~/.local/share/opencode/opencode.db` | 21/21 tokens exactos; 1 duración desviada (B2) |
| Conteo literal de fragmentos por función (AST) sobre 398 filas | 0 no literales |
| `git status --short` | solo `docs/.cdad-state.json` (ya modificado antes de la revisión) |

## Límites de esta re-revisión

- **No releí semánticamente las 398 filas.** Contrasté las 25 que cambiaron (6 de `check`, 19 de `motive`) y las cuatro «genéricas» que quedaron iguales; el resto solo pasó por los controles mecánicos que acabo de listar. Que un fragmento sea literal no acredita que observe la promesa de su fila: eso sigo sin poder afirmarlo fuera de la muestra.
- **No verifiqué la correspondencia semántica de los 26 registros de vínculo** (contrato ↔ obligación ↔ test). Verifiqué que validan rc 0 y que el SHA256 del contrato de 016-003 coincide; la pertinencia de cada vínculo ajeno al tramo no la reabrí.
- **No medí el costo de la materialización por lote** (absorb/receive/materialize): el archivo declara que ocurre dentro de los turnos del orquestador y no se instrumentó. Con B2 abierto, esa omisión pesa más que antes.
- **No re-corrí la suite completa:** el régimen del ciclo focal no la exige y no había autorización para ella; ejecuté los tres módulos de la feature y de sus dos antecesoras (22 verdes), que es lo que el informe cita.
- **No evalué** si el umbral del 30 % de `decision.md` se mide contra auditoría sola o contra el costo fijo total; con la corrección de B2 la lectura cambia y la decisión de dueño es del dueño.

## Abstenciones

- **Si «Mantener» es la disposición correcta en las 398 filas:** no me pronuncio fuera de las 25 que cambiaron.
- **Si el fin declarado 01:12:26 de GREEN-002 corresponde a un recibo de entrega** (y el tramo 01:12:26–01:19:31 es trabajo de otra actividad ya contada): no lo puedo decidir; si el dueño lo aporta, B2 baja a declaración faltante y deja de bloquear.
- **Si el volumen de `cache_read` entra en la noción de costo que el dueño quiere gobernar:** es decisión de negocio, no de contrato; por eso O2 es opcional.
- **Si S1, S2 y S3 son redundancias reales:** no lo declaro. Falta la evidencia experimental que cada una describe, y el trámite es del dueño.
- **Si la autoridad delegada (mandato del 2026-11-02) alcanza el tramo 2 con los cambios de método listados:** no me corresponde ratificarlo; no es mi rol aprobar.
```

Nota de método: el sobre del paquete se validó antes de trabajar y no escribí nada en el repositorio; todo el trabajo quedó en `/tmp/opencode/review-016-003-r2`.
