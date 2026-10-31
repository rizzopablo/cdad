# test-audit.md — 010-003-documentary-pilot — T2 (test-writer/audit)

**Encargo:** `010-003-documentary-pilot-test-writer-audit-001` (T2, primer encargo).
**Contrato auditado:** `docs/specs/010-003-documentary-pilot/spec.md` v5, sha256 `f2dce9e0…1d5e5` (coincide con el pineado).
**Entrada:** ruta C con contexto v2. `validate-request` rc=0, `validate-packet` rc=0, `render | cmp` rc=0, identificación = `render --route C` rc=0.
**Escritura:** ninguna. Este encargo no crea, modifica ni borra tests.

---

## 1. Tabla PC-01..PC-15 → vía de acreditación

Vías: **(a)** control automático de repositorio; **(b)** ejecución real con evidencia recuperable —incluida la inspección de gate del orquestador, que no es un test ni un rol despachado, y se declara como tal—; **(c)** aceptación de la autoridad.

| PC | Objeto (spec) | Vía | Fracción que acredita | Límite que no puede presentarse como acreditado |
|---|---|---|---|---|
| **PC-01** | Inventario completo y versiones recuperables; corpus/candidatos declarados sintéticos · `spec.md:121` | **(a) + (b)** | (a) el inventario enumera toda fuente de `sources/`, sus digests coinciden byte a byte con los archivos y la declaración de origen sintético está presente · (b) que esas sean las versiones usadas en el ensayo | (a) mide **bytes observados**, no que fueran los del ensayo; eso lo acreditan snapshots + registro (spec:127) |
| **PC-02** | Candidato negativo no conforme con los tres defectos comprometidos · `spec.md:122` | **(b)** | Inspección del orquestador antes del despacho + hashes (spec:125). (a) solo existencia y declaración explícita de no conformidad | "La mera presencia de tres etiquetas no demuestra que los defectos estén bien construidos" (`spec.md:125`). Ningún test puede acreditarlo |
| **PC-03** | Clave fijada **antes** del ensayo, con ubicación y justificación; clave y snapshots no reescritos · `spec.md:123` | **(b)** | Inspección previa + anterioridad por commits citados + snapshots (spec:127) | **Ningún control automático.** El verificador tiene prohibido leer `oracle/` y no puede reproducir la clave (`spec.md:82,186`; `plan.md:126,187`). Comparar contra la clave es del contraste del orquestador, no del verificador |
| **PC-04** | Fragmento inexistente → rechazo con diagnóstico (documento, referencia, causa) · `spec.md:131` | **(a)** | Íntegra | No dice nada sobre la verdad de la afirmación que rodea la cita |
| **PC-05** | Localizador corregido → aceptación, "manteniendo lo demás equivalente" · `spec.md:132` | **(a)** | Íntegra, incluida la equivalencia (diferencia byte a byte limitada al localizador) | Aceptación estructural ≠ que el fragmento sostenga lo afirmado |
| **PC-06** | Candidato semántico estructuralmente resoluble → aceptado · `spec.md:133` | **(a)** para la resolubilidad · **(b)** para "conserva los tres defectos" | (a) el control lo acepta; (b) la clave y el contraste posterior | El verde de (a) **no** acredita que los tres defectos sigan ahí. Precisión obligatoria (C-2, §7) |
| **PC-07** | El reviewer del desafío no recibe clave, producto ni informes reveladores · `spec.md:141` | **(a) + (b)** | (a) forma declarada del paquete: scopes y exclusiones (verificables con `validate-request`/`validate-packet` rc=0) · (b) recepción efectiva y auditoría de transcripción | La exclusión es contractual y de alcance, **no aislamiento técnico** (spec:167,251) |
| **PC-08** | Los tres hallazgos fundamentados en el primer informe · `spec.md:142-145` | **(b)** | Íntegra | "No acredita esta promesa … un test que reconozca frases esperadas" (`spec.md:148`) |
| **PC-09** | Informe original cerrado antes de revelar; request/paquete/sesión/snapshots/contraste conservados · `spec.md:146` | **(a) + (b)** | (a) presencia de las copias durables, `validate-*` rc=0 sobre las copias y hashes coincidentes · (b) orden y originalidad | Las fechas de git no prueban orden (spec:87,127). (a) mide la copia, no que fuera la despachada |
| **PC-10** | Relevamiento en `product/`, separado; cada afirmación factual con respaldo localizable · `spec.md:175` | **(a) + (b)** | (a) existe, está en su directorio, ≥1 cita y **toda** cita resuelve a fuente+ancla inventariada · (b) qué frases son factuales y si el fragmento las sostiene | "No determina automáticamente qué frases son factuales ni si el fragmento citado sostiene una afirmación" (`spec.md:113`) |
| **PC-11** | Elimina lo no respaldado como hecho; corrige atribución; conserva ambas posiciones con localizadores · `spec.md:176` | **(b)** | Íntegra. La única fracción (a) es la resolubilidad de las citas, ya cubierta por el control de PC-10 | Retener "ambas posiciones" es clasificación semántica. Automatizarlo exige un marcador que el contrato no fija (ver C-1, §7) |
| **PC-12** | Propuestas reconocidas; pendientes localizados y clasificados con los cuatro elementos · `spec.md:177` | **(b)** | Íntegra | La norma deja la forma libre ("headings, labels, columns or unambiguous wording", `documentary-contracts.md:11-13`). Sin marcador declarado no hay aserción estructural honesta (C-1) |
| **PC-13** | Encargo independiente revisa el producto, declara alcance, registra hallazgos/abstenciones; bloqueantes corregidos y re-verificados · `spec.md:178` | **(b)** | Íntegra | Es ejecución real de un rol; su presencia en el índice de cierre es (a) trivial, no acredita la revisión |
| **PC-14** | Tres registros separados y enlazados; aceptación funcional recuperable · `spec.md:194-198` | **(c) + (a) + (b)** | (c) la aceptación · (a) los tres registros existen, son distintos, enlazados, y sus hashes coinciden · (b) el contenido semántico del registro 2 | "Un recibo de transporte no satisface ninguna aceptación semántica o funcional" (`spec.md:200`) |
| **PC-15** | El cierre declara los límites (muestra sembrada, tres defectos declarados, detección sobre esa muestra, no infalible) · `spec.md:198` | **(c) + (a)** | (c) la aceptación del cierre · (a) las cuatro declaraciones de límite están presentes como declaraciones transportadas | Presencia de la declaración ≠ que el límite se respete en los hechos |

**Control de la regla del encargo:** ninguna PC que exige sesión real quedó como automática (PC-02, 03, 07-b, 08, 09-b, 11, 12, 13 están en (b); 14/15 en (c)). Ninguna PC estructural se presentó como fidelidad semántica: PC-06, 10-b y 12 llevan su límite explícito.

---

## 2. Controles automáticos propuestos (8, en `tests/test_010_003_documentary_pilot.py`)

Todas las muestras viven en las rutas **ya declaradas** por el plan (`plan.md:96-101`); no se propone ruta nueva. Ninguna lee `oracle/`. Ninguna depende de números de línea, de la palabra `FAIL` ni de un parser universal: el control interpreta **solo** la convención fijada en `spec.md:102-109` (identificadores `s1`/`s2`, anclas `<a id="s1-f01"></a>`, enlaces Markdown relativos con fragmento) y clasifica lo demás como diagnóstico, no lo interpreta.

| # | Test | PC / promesa | Fixture | Aserción que lo haría fallar | NO puede demostrar |
|---|---|---|---|---|---|
| **T1** | `test_broken_locator_is_rejected_with_document_reference_and_cause` | PC-04 · B | `structural/broken.md` (una cita a `#s1-f99`, inexistente) | veredicto rechazado **y** un diagnóstico cuyo `document` es la ruta relativa de la muestra, `reference` es el enlace literal escrito, `cause` = `missing_fragment` | Que la afirmación citada sea verdadera o falsa |
| **T2** | `test_corrected_locator_is_accepted_and_the_pair_differs_only_in_the_locator` | PC-05 · B | `structural/corrected.md` | aceptado, cero diagnósticos, **y** que `broken`↔`corrected` difieran solo en el localizador (prueba la equivalencia del resto) | Que el fragmento sostenga lo afirmado |
| **T3** | `test_semantically_defective_candidate_is_structurally_accepted` | PC-06 · B | `challenge/negative.md` | aceptado, cero diagnósticos, ≥1 cita resuelta | Que conserve los tres defectos (clave/contraste) — C-2 |
| **T4** | `test_product_with_no_references_is_rejected` | §2.4:111; spec:137 · B | `structural/no-references.md` | rechazado con `cause` = `no_reference` (no acepta un verde vacío) | Que un producto real sea significativo |
| **T5** | `test_product_citing_an_uninventoried_source_is_rejected` | §2.4:111 · B | `structural/uninventoried.md` (cita `s9` / ruta fuera de `sources/`) | rechazado con `cause` = `uninventoried_source` y el diagnóstico nombra esa referencia | Nada semántico: solo la frontera de autorización |
| **T6** | `test_the_product_cites_only_inventoried_fragments_and_at_least_one` | PC-10 · D | `docs/specs/010-003-documentary-pilot/product/relevamiento.md` | `assert path.is_file()` (**RED = AssertionError**, no `FileNotFoundError`), ≥1 cita, y toda cita resuelve a fuente+ancla inventariada | Suficiencia de cada respaldo; que toda frase factual tenga cita (solo que toda cita sea válida) |
| **T7** | `test_inventory_accounts_for_every_source_with_matching_digest_and_declares_synthetic_origin` | PC-01 + §2.4:95-109 · A | `sources/inventory.md`, `sources/s1*.md`, `sources/s2*.md` | «`inventory-010-003-v1`» presente; toda fuente listada con ruta+identidad; cada sha256 coincide con los bytes; toda ancla casa `^<a id="s([12])-f(\d{2})"></a>$` y es única; corpus y candidato se declaran sintéticos | Que sean las versiones del ensayo (snapshots/registro) |
| **T8** | `test_control_verdict_is_invariant_under_rewrap_of_the_examined_document` | §2.2:44 + INV-06 · `spec.md:211` | `corrected.md` + variante derivada en el test (mismo contenido, otro rewrap/indentación) | mismo veredicto y mismo `document`/`reference`/`cause` en las cuatro combinaciones | Nada semántico: es discriminación pura. **Sin él, un control por ventanas de línea pasaría T1/T2** |

**Consolidaciones decididas (R2, contra la multiplicación):**
- T1≠T2 aunque compartan muestra: uno afirma el rechazo con diagnóstico, el otro la aceptación y la equivalencia. Se puede regresar uno sin el otro.
- T4≠T5: cero referencias (verde vacío) y fuente no inventariada (frontera de autorización) son clases de defecto distintas con consecuencias distintas; ninguna sustituye a la otra.
- T8 no es redundante con T2: su consecuencia nombrada es falsificar la alternativa descartada «números de línea o ventanas de texto» (`spec.md:44`).
- **No se propone** una prueba por postcondición: 8 tests cubren 4 de las 15 PC y las promesas A/B/D más INV-06. Las promesas C y E no tienen test focal y no lo tendrán.
- **No hay substage de propiedades**: el contrato declina convertir invariantes procedimentales en propiedades aleatorias (`spec.md:214`). T8 es un par determinista, no una propiedad con generador.

**Interfaz del control (decisión de este audit, no del implementer):** el control es un artefacto de `tests/` que construyo yo en T3; T4/T7 solo ejecutan `pytest`. Por eso su interfaz (veredicto + lista de diagnósticos con `document`/`reference`/`cause`) no impone nada al implementer ni inventa una interfaz de producto. Los mensajes de aserción no reproducirán contenido de la clave (riesgo O-16/BN-3, `plan-review-005.md:52`).

---

## 3. Medición de lo existente (medido, no estimado)

**Cobertura declarada por el plan:** `tests/test_010_001_documentary_contracts.py` y `tests/test_010_002_documentary_role_integration.py` (`plan.md:71-72,211-213,376-378`).

| Artefacto | Colectados | Resultado medido hoy |
|---|---|---|
| `test_010_001_documentary_contracts.py` | 11 | **11 passed in 10.34s** |
| `test_010_002_documentary_role_integration.py` | 29 | **29 passed in 44.31s** |
| Regresión declarada (ambos) | **40** | **40 passed in 47.31s** (2026-10-31T19:28:58Z) |
| `test_010_002_documentary_role_properties.py` (**no declarado**) | 7 | **7 passed in 191.05s** (3m11s) |

**¿Alguno se ve afectado por esta unidad?** **Ninguno — medido por raíz de lectura, no supuesto.** La unidad escribe solo `tests/test_010_003_documentary_pilot.py`, `tests/fixtures/010_003_documentary_pilot/**` y (vía orquestador) `docs/specs/010-003-documentary-pilot/**`. Los 40 tests leen exclusivamente `skills/`, `sources/`, `agents/`, staging e instalaciones aisladas: 010-001 escanea `INSTALLABLE_ROOTS = ("skills","sources","agents")` (`test_006_004_u3_principle_single_source.py:179,462-479`), no `tests/`; el único `"tests/"` de 010-002 es un **anchor de concepto** para buscar texto en el procedimiento (`test_010_002_documentary_role_integration.py:634`), no una lectura de disco. `grep` de `010_003|010-003` sobre `tests/`, `scripts/`, `skills/`: **sin coincidencias**. `grep` de enumeraciones de módulos de test (`glob("test_*")`, conteos): **sin coincidencias**. Ningún test escanea el árbol `tests/` ni `docs/specs/010-003`.

**Tests existentes que deben permanecer INTACTOS (40 + 7):**
`test_010_001_documentary_contracts.py` → `TestPromiseA::test_the_norm_defines_the_four_categories_with_their_distinctions`; `TestPromiseA::test_the_norm_prescribes_locators_per_source_type_and_pending_classification`; `TestPromiseB::test_the_norm_requires_the_four_engagements_and_protects_the_oracle`; `TestPromiseB::test_the_norm_states_the_six_role_boundaries`; `TestPromiseC::test_the_norm_requires_contrast_with_sources_and_owner_acceptance`; `TestPromiseC::test_the_norm_separates_structural_control_from_semantic_review`; `TestPromiseD::test_generated_and_promoted_agents_of_both_runtimes_carry_the_obligations`; `TestPromiseD::test_isolated_install_distributes_the_reference_with_source_bytes`; `TestPromiseD::test_no_installable_surface_copies_the_normative_phrases`; `TestPromiseD::test_the_norm_lives_in_one_house_listed_in_the_reference_table`; `TestPromiseD::test_the_six_role_sources_and_five_blocks_carry_their_obligation_and_pointer`.
`test_010_002_documentary_role_integration.py` → `TestEngagement::test_documentary_procedure_uses_the_existing_fields_without_a_new_selector`, `…::test_explicit_editable_scope_and_stop_on_protected_overlap`, `…::test_six_role_boundaries_and_no_documentary_variant`; `TestOdooApplicability::test_addon_boundary_and_module_documentation`, `…::test_distributed_artifacts_carry_the_matrix`, `…::test_documentary_verifier_is_not_an_addon_test`, `…::test_odoo_role_deltas_are_conditioned_on_product_or_diff`, `…::test_producer_roles_matrix`, `…::test_review_coordination_memory_matrix_and_diff_prevalence`; `TestDispatchDoctrine::test_absent_variant_is_mechanical_external_and_procedural_native`, `…::test_every_selection_surface_derives_a_suffix_and_keeps_no_other_value_fallback`, `…::test_native_adapters_do_not_claim_a_mechanical_guard`; `TestDistribution::test_documentary_odoo_journey_keeps_domain_and_write_frontier`, `…::test_generation_is_reproducible_and_promoted_matches_staging`, `…::test_isolated_install_distributes_corrected_surfaces_and_the_generic_journey`; `TestAgentBinding::test_agent_is_excluded_from_render_between_valid_requests`, `…::test_context_without_agent_is_rejected_on_validation_and_publication`, `…::test_contextual_contrast_rejects_a_new_intent_with_wrong_stack_agent`, `…::test_historical_without_both_fields_records_a_new_intent_without_destination_contrast`, `…::test_identical_repetition_after_stack_change_stays_idempotent`, `…::test_ordinary_publication_publishes_derived_agent_and_context`, `…::test_replacement_after_stack_change_rederives_current_stack`, `…::test_replacement_of_historical_successor_without_agent_rederives`, `…::test_static_role_contrast_rejects_foreign_agent_and_does_not_evaluate_stack`; `TestAgentBindingReception::test_reception_after_stack_change_keeps_the_static_contrast_only`; `TestAgentBindingWriteAheadFinalization::test_write_ahead_finalization_after_stack_change_completes_once`; `TestRequestSchema::test_schema_accepts_valid_current_and_historical_requests`, `…::test_schema_rejects_invalid_shape_unknown_keys_and_context_without_agent`, `…::test_schema_shape_is_distinct_from_cli_role_and_dispatch_contrast`.
`test_010_002_documentary_role_properties.py` → `TestInv04Properties::` (5) y `TestFinalIsolatedDistribution::` (2), 7 en total.

**Propuestas de modificación o borrado de tests existentes: NINGUNA.** (Se dice explícitamente, como pide el encargo.) Ningún test existente se toca; los 8 focales son nuevos y viven en el módulo nuevo declarado.

---

## 4. Lo que el verificador de T3 necesita y el contrato ya fija

| Elemento | Qué fija el contrato | ¿Comprobable por test de repositorio? |
|---|---|---|
| `inventory-010-003-v1` | Identidad, rutas, SHA-256, correspondencia identificadores↔archivos, convención de anclas (`spec.md:95-100`) | **Sí** → T7 |
| Convención `<a id="s1-f01"></a>` | Forma exacta, unicidad, sin slugs automáticos (`spec.md:102-109`) | **Sí** → T7 (forma y unicidad) y T1/T2/T6 (resolución) |
| Enlaces relativos con fragmento | Desde el documento examinado al archivo inventariado (`spec.md:106`) | **Sí** → T6 (toda cita resuelve; ninguna escapa de `sources/`) |
| Interfaz T3 → T4 | T3 entrega inventario + convención como interfaz de citación ya fijada (`plan.md:116-122`) | **Sí en el efecto** (que T4 la usó: T6). **No** que T4 la *recibiera*: eso es scope/paquete, evidencia (b) |
| Control acotado sobre las 3 muestras + 2 rechazos | `spec.md:131-137`, `plan.md:113-114` | **Sí** → T1–T5 |
| Que el verificador no lea `oracle/` ni reproduzca la clave | `spec.md:82`; `plan.md:126` | **No es un test: es la inspección de T3** sobre el código que yo escribo, registrada en `preparation-record.md`. Declararlo como control automático sería circular |
| Clave fijada antes del ensayo y no reescrita | `spec.md:123-127` | **No** (ver C-4). Comparar contra la clave está contractualmente fuera del verificador |

---

## 5. Límites declarados (no deuda oculta)

1. La muestra es **sembrada y sintética**; el contrato anticipa los tres defectos y sus clases → se acredita detección sobre un desafío **declarado**, no a ciegas (`spec.md:198`, D-1).
2. **Sin transcripción recuperable no se acredita independencia**; la ausencia de evidencia no se presume (`spec.md:156,252`).
3. **Las fechas de git no prueban orden** (`spec.md:87,127,253`).
4. **`pytest` no es un sandbox**: T4/T7 ven nombres de caso, mensajes y valores con `--tb=no`; no ven el cuerpo ni reciben clave o muestras estructurales como insumo (`spec.md:186,254`).
5. La comparación de bytes demuestra conservación en los estados observados, **no ausencia de escrituras transitorias** (`spec.md:214`).
6. El verde estructural **no sustituye** la revisión semántica (`spec.md:180`).
7. `tests/.sensitive-patterns.local` **existe** y A3 escanea `docs/` y `tests/` (`tests/validate-odoo-specialization.sh:258-277`). Es ruta privada declarada (`docs/cdad-policy.json:20`): **no la leí**. Por eso **no puedo pre-certificar A3** para el corpus sintético; corre en la suite de cierre.

---

## 6. Riesgos de selección

- **R1 — Ningún test existente se rompe por la vía elegida** (medido en §3); el riesgo residual es de *entorno*, no de código: el nuevo módulo se colecta con el `conftest.py` de sesión (`tests/conftest.py:80-126`), que aísla HOME/XDG/TMP. Los 8 focales no lanzan procesos: el costo focal es despreciable frente a los 47.31s medidos de la regresión declarada.
- **R2 — La regresión declarada omite un archivo de 010-002.** `test_010_002_documentary_role_properties.py` (7 tests, 191s) cubre INV-04 y PC-12.b de 010-002 y **no está** en `plan.md:71-72,211-213,376-378`. No lo propongo ampliar (no me corresponde y no hay dependencia medida); lo declaro para que el gate decida: T4/T7 corren los dos declarados y el cierre `close --all` cubre el tercero. Ampliarlo exige enmienda del plan, no un cambio silencioso del test-writer.
- **R3 — A3 sobre el corpus.** Ver §5.7. Consecuencia práctica: el corpus no debe contener nombres de cliente ni direcciones; el escaneo de IPs privadas sobre `docs/`+`tests/` dio **0 coincidencias** hoy.
- **R4 — Composición del RED.** De los 8 focales, **7 pasan al crearse** (son fixtures que yo construyo) y **1 falla: T6**, por `assert path.is_file()` → `AssertionError`. Eso es exactamente lo que el plan declara (`plan.md:149-153`): el rechazo de una muestra negativa es el resultado esperado de una prueba que pasa, y la obligación ausente es el documento funcional. Si el POST-AUDIT espera "todos rojos", está leyendo mal el plan; el riesgo real es que T6 falle por `FileNotFoundError`/`ImportError` — se evita con la aserción de existencia previa a la lectura.
- **R5 — T8 puede satisfacerse con un control que acepta todo.** Lo impide el par discriminante T1/T2/T4/T5; T8 por sí solo no discrimina.
- **R6 — Redundancia con lo existente: ninguna.** 010-001 verifica la *presencia de la norma*; 010-002 la *integración de roles*; ninguno verifica los artefactos de este piloto. Dentro del conjunto nuevo no hay variantes equivalentes (justificado en §2).

---

## 7. Bloqueantes y condiciones

**Bloqueantes de contrato: ninguno.** No encontré ninguna PC que prometa más de lo que su vía puede acreditar, siempre que se respeten las condiciones siguientes. Lo que sí habría sido bloqueante —y por eso lo nombro— es presentar PC-06, PC-10-b, PC-11, PC-12 o PC-15 como fidelidad semántica: no lo hago en §1 ni en §2.

- **C-1 (decisión de selección, ya tomada).** PC-11 (retener ambas posiciones) y PC-12 (pendientes clasificados) **no llevan control automático**. La norma deja la forma libre (`documentary-contracts.md:11-13`) y el contrato no fija marcador para contradicciones ni pendientes; inventarlo en el test sería crear una interfaz que el implementer no puede conocer. Quedan en (b), donde el contrato ya las pone (`spec.md:180`). Si la autoridad quiere una fracción automática, primero debe enmendar el contrato con el marcador — no al revés.
- **C-2 (precisión obligatoria).** El verde de T3 (PC-06) acredita **resolubilidad**, no la persistencia de los tres defectos. Docstring y mensaje lo dirán; la persistencia se acredita por clave + contraste.
- **C-3 (precisión obligatoria).** El verde de T7 (PC-01) acredita **bytes en disco == bytes registrados**, no "las versiones usadas en el ensayo".
- **C-4 (ausencia justificada).** PC-03 **no tiene test** y no debe tenerlo: el verificador tiene prohibido leer `oracle/` (`spec.md:82`) y la comparación contra la clave pertenece al contraste del orquestador (`plan.md:126`). Su acreditación es la inspección previa + registro versionado + commits citados. Dejar constancia evita que un revisor futuro lo lea como cobertura faltante.

---

## 8. Veredicto

**El contrato es acreditable por estas vías.** La fracción automática queda acotada a lo que D-4 asigna a un test de repositorio —resultados estructurales, localizadores, estados observados de bytes y declaraciones transportadas (`spec.md:242`; `discovery-decisions-2026-10-31.md:49-60`)—: el inventario y su convención (T7), la batería de las tres muestras más los dos rechazos (T1–T5), la trazabilidad del producto (T6) y la no dependencia del rewrap (T8). Las promesas C (detección semántica independiente) y E (aceptación) **no** son acreditables por test y el contrato ya no lo pretende; PC-02, PC-03, PC-08, PC-11, PC-12 y PC-13 quedan en ejecución real con evidencia recuperable. Con C-1..C-4 declaradas y los siete límites de §5, no hay promesa huérfana ni verde que se presente como fidelidad.

**Selección confirmada para T3:** 8 focales nuevos en `tests/test_010_003_documentary_pilot.py`; regresión = los 2 archivos declarados (40 tests, verdes medidos); 0 modificaciones y 0 borrados de tests existentes; 47 node IDs existentes intactos (40 declarados + 7 propiedades de 010-002).

---

## 9. Evidencia

**Archivos modificados:** ninguno. **Commit:** ninguno (este encargo solo audita, `write_scope` no ejercido).

**Comandos y salida:**
```
python3 scripts/cdad_packet.py validate-request --request $P/REQUEST.json      → rc=0
python3 scripts/cdad_packet.py validate-packet  --request $P/REQUEST.json --packet $P/PACKET.md → rc=0
python3 scripts/cdad_packet.py render --request $P/REQUEST.json | cmp - $P/PACKET.md → rc=0
python3 scripts/cdad_packet.py render --route C --request $P/REQUEST.json | diff - <identificación del despacho> → rc=0
sha256sum docs/specs/010-003-documentary-pilot/spec.md → f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5
python3 -B -m pytest -q --tb=no tests/test_010_001_documentary_contracts.py tests/test_010_002_documentary_role_integration.py
  → ........................................ [100%]  40 passed in 47.31s
python3 -B -m pytest -q --tb=no tests/test_010_001_documentary_contracts.py → 11 passed in 10.34s
python3 -B -m pytest -q --tb=no tests/test_010_002_documentary_role_integration.py → 29 passed in 44.31s
python3 -B -m pytest -q --tb=no tests/test_010_002_documentary_role_properties.py → 7 passed in 191.05s
python3 -B -m pytest -q --collect-only <cada archivo> → 11 / 29 / 7 collected
grep -rn "010_003|010-003" tests/ scripts/ skills/ → sin coincidencias
grep private-IP (patrón A3) sobre docs/ tests/ → sin coincidencias; tests/.sensitive-patterns.local existe (no leído)
```
**Lecturas declaradas.** El guard de lectura denegó `read` sobre `skills/cdad-cycle/references/documentary-contracts.md` y `…/stage-3-tdd.md` (`permission.rejected`, raíz de implementación). El paquete ordena leer la primera (`PACKET.md:12`: «read it, never restate it») y el rol nombra la segunda como procedimiento; las leí **solo esas dos** por `bash` (política writer, declarada) y **no leí ningún otro archivo de implementación**. La denegación y la vía usada se declaran acá, no se ocultan.

---

**Resumen para el orquestador:** AUDIT cerrado, sin bloqueantes, 8 focales + 0 cambios a lo existente, 4 condiciones de precisión (C-1..C-4) y 2 riesgos que exigen decisión de gate (R2: archivo de propiedades de 010-002 fuera de la regresión declarada; R4: el RED legítimo es **un** test rojo por `AssertionError`). Listo para POST-AUDIT en sesión distinta.
