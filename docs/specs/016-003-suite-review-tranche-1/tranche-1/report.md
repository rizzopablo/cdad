# Informe del tramo 1 (20 %) — revisión de suite por tramos

- **Feature:** 016-003-suite-review-tranche-1
- **Selección congelada:** revisión `120fa8b9eefbc10a64367c55b84c98de7e53b65b`, 398 nodeids de
  36 módulos y 25 unidades de contrato (`tranche-1/selection.json`, reproducible byte a byte con
  `cdad_suite_review.py select`).
- **Contrato del tramo:** `docs/specs/016-003-suite-review-tranche-1/spec.md` (PC-1…PC-10).

## 1. Qué se revisó

398 de los 1.988 nodeids inventariados (20 %), elegidos por el selector congelado y no por
preferencia: 36 módulos de prueba que cubren 25 unidades de contrato, desde 016-001 (la más nueva)
hasta 007-003/007-004/007-006/007-007/007-008, 008-001…008-005, 009-001/009-002, 010-000…010-004,
012, 013-001/013-002, 014-001, 015-001/015-002 y 016-001/016-002.

Cada fila se leyó con su preparación suficiente para entender el resultado observable, no por su
nombre ni su docstring: 398 filas en `tranche-1/audit.json`, una por nodeid, sin omisiones ni
incorporaciones externas.

## 2. Qué protege cada fila

- Distribución por promesa: 48 filas `B`, 43 `A`, 42 `C`, 34 `D`, 13 `E`, 7 `F` y 211 con
  promesa nombrada de su propio contrato (`rechazo-protocolo`, `rechazo-ante-efectos`,
  `vigencia-conservadora`, `convergencia-entradas`, etc.).
- Cada fila declara `check` con fragmentos tomados del test, `setup` y `helpers` reales;
  `consequence` concreta («sin este test, el usuario…»); `evidence` y `references` con localizador
  que aparece exactamente una vez en su archivo. El validador **no** comprueba que el fragmento sea
  literal: lo verificó la revisión independiente y encontró seis filas con fragmentos tomados del
  registro en vez del test, ya corregidas (H3). Medido por cuerpo de función, 16 filas citan algún
  fragmento que vive en un helper que ejecutan (10) o en un test hermano que no ejecutan (6):
  `test_013_001_criterion_coherence.py::…coherent_instructions_without_quota_or_read`,
  `test_010_002_documentary_role_integration.py::…documentary_verifier_is_not_an_addon_test`,
  `test_010_004_t3_red.py::…pc03_pc12_dispatch_surfaces_name_the_route_c_path`,
  `test_010_004_t2_red.py::…active_v1_packet_is_diagnosed_and_escalated_without_effects`,
  `test_010_000_continuity_relative_root.py::test_A_relative_root_begin_and_checkpoint_match_absolute`
  y `…::test_C_existing_controls_hold_under_relative_root`. Esas seis citan identificadores del módulo
  más que aserciones propias: el límite queda declarado con sus nodeids, no oculto.
- **Disposiciones:** 398 `Mantener`. **Candidatos:** 0. **Incertidumbres declaradas:** 12 filas
  (asignaciones múltiples de módulo a dos contratos y límites de recuperación de promesa), ninguna
  convertida en disposición de retiro o consolidación.

Interpretación honesta de ese resultado: no haber encontrado candidatos **no** acredita que la
suite no tenga redundancia. El método sólo puede declarar que, con la lectura exigida por §5, no se
identificó protección observable duplicada ni promesa irrecuperable en este tramo.

## 3. Correspondencia y vínculos

- 25 unidades afectadas tienen registro de vínculo validado por `cdad_contract_links.py` (modo
  legacy por demanda para los contratos anteriores a los marcadores `cdad:pc`; modo marcadores para
  016-001/016-002). Total: 26 registros del proyecto, todos rc 0 contra su colección.
- Sin backfill: cada registro indexa sólo las obligaciones que los tests de este tramo protegen.
  Una unidad que aparece en dos lotes (010-002: B2b + B5) tiene un único registro fusionado por
  `contract.path` + `sha256`, con los vínculos de ambos lotes.
- El registro de 016-001 se amplió con los cuatro verificadores R-B3…R-B6 del tramo; el de 007-006
  se completó en dos lotes (B3: 12 obligaciones, B4: +2).
- Los seis verificadores nuevos de la propia feature quedan vinculados en
  `docs/specs/016-003-suite-review-tranche-1/contract-test-links.json` (6 vínculos), conforme a
  016-001. La revisión independiente detectó que faltaba el vínculo de R_F: con la colección viva
  (1 994 nodeids) y la congelada (1 988) como baseline el registro daba rc 1 por `new_unlinked`; ya
  está agregado y hoy da rc 0 con y sin baseline (H1).

## 4. Costo y decisión

`costs.json` reconstruye el costo por actividad: 17 actividades de auditoría (una por lote más el
piloto), la revisión independiente, el bloque de cierre con sus 31 comandos medidos individualmente
y tres bloques de preparación compartida (RED del validador, fixture de R-F y GREEN del validador),
cada uno con sesión, rol, alcance, nodeids, comandos, tokens con lectura y escritura de
caché cuando el runtime las expone, inicio, fin y duración observada.

| Medida | Valor observado |
| --- | --- |
| Tests auditados | 398 en 17 actividades de auditoría (piloto incluido) |
| Tiempo de auditoría | 7.081,8 s (≈ 17,79 s por test) |
| Revisión independiente | 353,6 s |
| Preparación compartida | 1.304,6 s (incluye el intervalo completo de GREEN-002, 1.040,2 s) |
| Cierre (verificación y comandos) | 42,3 s de reloj, 41,44 s de comandos medidos |
| Tiempo agregado (unión de intervalos) | 8.692,5 s en 22 sesiones |
| Suma cruda de sesiones | 8.782,3 s; el solapamiento de 90,1 s entre GREEN-002 y RED-003 está declarado y no se descuenta |
| Tiempo de reloj del tramo | 9.643,7 s |
| Tokens de entrada / salida | 2.716.861 / 702.509 |
| Tokens de caché (lectura / escritura) | 92.903.503 / 117.392 — dominan el volumen real |
| Costo experimental | **sin calibrar**: cero candidatos |

El bloque de cierre se registra con el rótulo `ses_orquestador_cierre`, que no es un id de sesión del
runtime: sus tokens se declaran «no disponibles» (no cero) y sus 31 comandos son reconstruibles desde
el archivo.
| Proyección del resto (1.590 nodeids) | 28.286,1 s de auditoría + 1.700,5 s fijos ≈ 8,3 h (cota alta, sin descontar los cambios de método) |

`decision.md` registra la decisión autorizada: **continuar con el tramo 2 aplicando cambios
explícitos de método**, con responsable, autoridad (delegación HITL del dueño, 2026-11-02), motivo,
evidencia y alcance. No autoriza poda, backfill ni reescritura de contratos cerrados.

## 5. Declarado, ejecutado y contrastado

- **Control estructural (automático):** `cdad_suite_review.py validate` sobre el tramo real con los
  26 registros → `ok`, 398 filas, 0 candidatos, 0 errores; `cdad_contract_links.py validate` → 26/26
  rc 0; `select` reproducible y byte-idéntico a la selección congelada; `pytest
  tests/test_016_003_suite_review_tranche_1.py` → 6 verdes; `pytest` de 016-001/016-002 → 16 verdes.
- **Ejecución real registrada:** los comandos, sus códigos de salida y sus duraciones están en
  `costs.json` y en las bitácoras de lote de los informes de rol; la herramienta de validación **no
  ejecuta pruebas**.
- **Revisión semántica independiente:** queda para el reviewer de la etapa 4 sobre este informe,
  `audit.json` y los registros. Ninguna disposición de este tramo autoriza modificar tests.

## 6. Defectos detectados durante el trabajo

| Defecto | Naturaleza | Estado |
| --- | --- | --- |
| El validador del tramo no resolvía obligaciones de contratos sin marcadores (35 de 36 módulos) | producto | corregido con RED `37af51dc`, fixture `34e628f4`, GREEN `81c6d0fd`: `--registry` legacy por `contract.path`+`sha256` |
| 13 filas repetidas byte-idénticas en B8 | forma de la entrega del rol | contenida: el materializador descarta sólo repeticiones idénticas y aborta ante contenido divergente |
| `sha256` transcripto en las 5 filas de 010-000 (B12) | forma de la entrega del rol | reemitidas por el rol con hash calculado (B12b), validadas rc 0 |
| Vínculo faltante del verificador R_F (H1 de la revisión) | trazabilidad | agregado al registro; `--baseline` con colección viva da rc 0 |
| Seis filas con fragmentos de aserción no literales (H3) | forma de la entrega del rol | reemitidas por el rol con fragmentos del test, verificados por conteo literal |
| 18 motivos plantilla contradictorios en 007-006 y uno en 009-001 (H4, S2) | forma de la entrega del rol | reescritos con juicio por fila; tres sospechas quedan registradas en `experiments/suspicions.json` |

**Sospechas registradas, no declaradas redundancia:** `experiments/suspicions.json` conserva S1
(los cuatro tests de 014-001 verifican presencia de términos: una mutación que invierta la norma
conservando los términos los pasaría), S2 (009-001: adopción de entrada heredada sin dueño frente a
entrada propia) y S3 (tres variantes de `withdraw_rejects_effects_and_inconclusive_signals` con la
misma tríada de aserciones). Cada una declara qué evidencia experimental faltaría para promoverla o
descartarla; ninguna autoriza poda.

## 7. Límites

- El tramo es el 20 % más nuevo del inventario **por construcción**: no es una muestra aleatoria del
  resto y no autoriza extrapolación estadística.
- Una referencia que resuelve no equivale a protección pertinente: la pertinencia la declara la
  revisión independiente, no el validador.
- Cero candidatos deja el costo experimental sin calibrar.
- La spec congela la revisión `ad15c58a` y la selección quedó tomada sobre `120fa8b9`; verificado que
  `select` produce exactamente los mismos 398 nodeids en ambas, pero el cambio queda declarado.
- Persisten los pendientes declarados en `spec.md` §11 (antigüedad individual de cada protección,
  demostración universal de redundancia, poda efectiva, backfill fuera del tramo, autenticación
  criptográfica de métricas, automatización del juicio semántico).
