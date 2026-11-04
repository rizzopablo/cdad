# review.md — 016-003, tramo 1 (etapa 4)

**Paquete:** ruta C, `016-003-suite-review-tranche-1-reviewer-review-001`. El paquete es válido: `validate-request` dio rc 0 y `validate-packet` dio rc 0. `render` es byte a byte idéntico a `PACKET.md`. `render --route C` coincide con la identificación recibida. El SHA256 del contrato coincide con `b3f91691…`.

## Veredicto

**rechazado.** Uno de los seis tests nuevos de la feature no tiene vínculo, y el informe afirma lo contrario. El propio mecanismo de 016-001 da rc 1 al validarlo en modo revisión, así que no se cumple el criterio §10.7. Además, `costs.json` omite sesiones reales, lo que debilita PC-7 y PC-8. El resto del tramo se sostiene bien: se trata de correcciones acotadas, no de rehacer la auditoría.

## Hallazgos

### H1 — bloqueante · un test nuevo sin vínculo, y el informe dice que todos están vinculados (§10.7, PC-4)
- **Dónde:** `docs/specs/016-003-suite-review-tranche-1/contract-test-links.json` y `report.md` §3 («Los seis verificadores nuevos … quedan vinculados … (5 vínculos)»).
- **Qué verifiqué:** la colección actual tiene 1994 nodeids, 6 de ellos de `test_016_003`. El registro tiene 5 vínculos, de R_A a R_E. Falta `SuiteReviewTranche1Red::test_R_F_contrato_sin_marcadores_resuelve_por_indice_legacy`, que es justamente el verificador de la corrección GREEN-002.
- **Evidencia:** `cdad_contract_links.py validate --registry <016-003> --collection <actual> --baseline tranche-1/collection.json` → **rc=1**, `new_unlinked: [...test_R_F...]`. Sin `--baseline` da rc 0, y ese es el «rc 0» que cita el informe.
- **Consecuencia:** se acredita un cierre con un verificador nuevo sin trazabilidad. Es justo lo que 016-001 prohíbe en revisión.
- **Para cerrarlo:** agregar el vínculo de R_F a la obligación que protege (PC-3/PC-4) y volver a validar con `--baseline` hasta obtener rc 0. Además, corregir la frase del informe.
- Verdict: BLOCKING · Bucket: h

### H2 — mayor · `costs.json` no permite reconstruir el costo real por actividad (PC-7, PC-8)
- **Dónde:** `tranche-1/costs.json`, `report.md` §4 y `decision.md` («costo estabilizado y predecible»).
- **Qué verifiqué:** `costs.json` registra 15 actividades: B1a–B12 y el cierre. En `.cdad/packets/` hay 18 paquetes de auditoría. Faltan en el registro:
  - `audit-002` y `audit-003`: el piloto, primera pasada sobre los módulos de B1 y B2.
  - `audit-018`: la reemisión B12b.
  - `red-002`, `red-003` y `implementer-green-002`: la corrección del validador, que se volvió necesaria a mitad del tramo.
  - La selección y la materialización, que §7 lista como alcances.
  
  El propio `decision.md` reconoce «la segunda pasada de normalización que consumió B1a/B1b/B2a/B2b», pero esa primera pasada no tiene costo registrado.
- **Consecuencia:** los «≈15,6 s por test» y el `fixed_s` de 42,3 s (que es solo el cierre) subestiman el costo observado. La proyección del tramo 2 parte de una base incompleta y no presenta una cifra proyectada para los 1590 nodeids restantes.
  - La afirmación de que el costo es «estabilizado» no se sostiene: los lotes van de 292 a 581 s, y faltan sesiones.
  - Lo que sí está bien: los lotes fueron secuenciales (verifiqué que inicio y fin no se solapan, así que no hay doble conteo) y los tokens del orquestador figuran como «no disponibles», no como cero.
- **Para cerrarlo:** agregar las actividades omitidas, o declararlas como omisiones con su motivo. Recalcular `t_audit` y el costo fijo, y matizar la frase de `decision.md`.
- Verdict: OPTIONAL (mayor; el dueño decide si bloquea) · Bucket: h

### H3 — menor · 6 filas con «aserciones» que no son literales del test (PC-3; §2 del informe)
- **Filas en `010-002`:** `test_absent_variant_is_mechanical_external_and_procedural_native`, `test_native_adapters_do_not_claim_a_mechanical_guard`, `test_contextual_contrast_rejects_a_new_intent_with_wrong_stack_agent` y `test_historical_without_both_fields_records_a_new_intent_without_destination_contrast`. Sus fragmentos no aparecen en ningún archivo de `tests/`: vienen del registro y de `test-audit.md`.
- **Filas en `008-001`:** `test_pc3_inherited_overrides_neutralized_per_aj2` y `test_pc7_envelope_after_cota_within_margin_is_relayed`. Sus fragmentos parafrasean aserciones que en el test ocupan varias líneas.
- Hay además filas que pasan como «literales» con fragmentos que no identifican ninguna aserción. Ejemplos: la fila 366 cita `self.assertGreater(`/`self.assertTrue(`, la 395 `no_op`/`bytes canónicos`, la 397 `CDAD_INSTALL_ROOT`, la 383 `RUNTIME_PREAMBLE`/`route_c`.
- El validador no comprueba que las aserciones sean literales. Por eso la frase del informe «cada fila declara `check` con aserciones literales» va más allá de lo que se controló.
- **Para cerrarlo:** reemplazar los fragmentos de las 6 filas por aserciones reales del test y matizar la afirmación del informe.
- Verdict: OPTIONAL · Bucket: h

### H4 — menor · motivos plantilla contradictorios en 18 filas de 007-006
- **Dónde:** filas 70, 71 y 73–80 (variantes de `republish_agents_preserves_existing_derivation_guards` y `prepared_begin..._both_orders`), y filas 93–100 (variantes de `withdraw_rejects_effects_and_inconclusive_signals`).
- **Qué dicen:** «…no cubierta por otra fila del lote; Señal ya cubierta por su variante dedicada; ninguna otra fila del tramo la protege».
- La misma frase afirma y niega que haya cobertura, y se copia sin cambios entre variantes. No muestra un juicio hecho fila por fila.
- **Para cerrarlo:** reescribir el motivo de esas filas o derivarlas a la sospecha S3.
- Verdict: OPTIONAL · Bucket: m

### H5 — menor · inconsistencias de texto
- `decision.md` dice que el control detectó «dos defectos reales de producto». `report.md` §6 lista uno de producto y dos de forma.
- La spec congela la revisión `ad15c58a`, y la selección usa `120fa8b9` sin declarar el cambio. Verifiqué que `select` sobre las dos revisiones da exactamente la misma lista de 398, así que no tiene efecto material. Basta con declararlo.
- Verdict: OPTIONAL · Bucket: h

## Sospechas que el tramo no reportó (sin declarar redundancia)

**S1 — una aserción que no observa la promesa que declara.**
- **Test:** `tests/test_014_001_suite_evidence_defaults.py::test_A_defaults_inequivocos_y_autorizacion_suficiente`, vinculado a PC-1–PC-4.
- **Por qué:** solo comprueba que ciertas palabras estén presentes en documentos (`recomendad`, `obligatoria`, `dispensa expresa`, `ADR-041`). Un texto con la norma invertida pero las mismas palabras lo pasaría.
- **Evidencia que faltaría:** una mutación del documento que invierta el sentido y conserve los términos.
- Lo mismo vale para `test_B`, `test_C` y `test_D` del mismo módulo.

**S2 — una hipótesis que la propia fila plantea y descarta.**
- **Test:** `tests/test_009_001_installer_agent_overlay.py::AgentOverlayContract::test_pc3_legacy_unowned_overlay_conflict_is_adopted_on_update` (fila 333).
- **Por qué:** el motivo dice «hipótesis de redundancia parcial con PC-3 base», pero `candidate` es `null`. Eso contradice el criterio de §5.
- **Posible duplicado:** `test_pc3_overlay_remains_owned_and_unchanged_check_is_successful`.
- **Evidencia que faltaría:** romper solo la adopción de la entrada heredada sin dueño (la base distinta) y ver si el test base falla.

**S3 — variantes con la misma triada de aserciones.**
- **Test:** `tests/test_007_006_withdraw_and_republish.py::test_withdraw_rejects_effects_and_inconclusive_signals[materialization-unreadable]`.
- **Posibles duplicados:** las variantes `[receipt-unreadable]` y `[dispatch-unreadable]`, que verifican lo mismo: `returncode == 2`, árbol sin cambios y causa en el texto.
- **Evidencia que faltaría:** un defecto en el lector específico de una sola señal que únicamente su variante detecte.

## Cobertura de la revisión

**Filas contrastadas a mano (26 filas de 13 unidades):** 24, 20 (015-002) · 328, 332 (009-001) · 395, 397 (010-000) · 27, 30 (015-001) · 62, 56 (010-003) · 214, 193 (008-002) · 387, 383 (010-004) · 225, 235 (007-004) · 42, 45 (013-002) · 366, 362 (010-001) · 51, 53 (012) · 323, 324 (008-003) · 49, 46 (013-001). También inspeccioné las filas 1 y 100.
- En las 26 comprobé cuatro cosas:
  - que la obligación existe en el contrato y dice lo que la fila afirma;
  - que la promesa coincide;
  - que las aserciones son literales;
  - que la consecuencia es concreta.
- El cuerpo completo del test solo lo leí en las filas 366 y 383.

**Controles mecánicos sobre las 398 filas:**
- Aserciones literales: 6 fallos (ver H3).
- Helpers: todos los nombres existen en `tests/`.
- SHA256 de referencias: sin deriva.
- Disposición: 398 «Mantener».

**Vínculos:** revisé los 26 registros, no solo 8.
- Ningún nodeid está fuera del tramo, salvo los propios de 016-003, como es esperable.
- Toda obligación indexada tiene al menos un vínculo.
- No hay nodeids duplicados.
- Los `pc_ids` de cada fila son idénticos a los del vínculo correspondiente.
- **Fusión de 010-002:** 36 vínculos para 36 filas, 12 obligaciones, sin pérdida ni duplicados.
- **Fusión de 007-006:** 61 vínculos para 61 filas, 14 obligaciones, sin pérdida ni duplicados.
- Contraste semántico solo en 014-001 y 009-002 (de ahí sale S1).

**Comandos que ejecuté**, sin escribir en el repositorio; los temporales quedaron en `/tmp/opencode/review-016-003`:
- `cdad_suite_review.py select`: reproduce `selection.json` byte a byte. El hash del tramo es `c7336832…` y el de la colección `dc5fa7c4…`, ambos coinciden con la spec.
- `cdad_suite_review.py validate` con los 26 registros → rc 0, 398 filas.
- `cdad_contract_links.py validate`: rc 0 para 010-002 y 007-006. Para 016-003 da rc 1 contra la colección congelada y contra la actual con `--baseline` (H1).
- `pytest` de 016-001, 016-002 y 016-003 → 22 passed.
- `pytest --collect-only` → 1994 nodeids.
- `git status`: solo aparece `docs/.cdad-state.json`, que ya estaba modificado antes.
- No modifiqué archivos ni hice commits.

## Límites

- Con cero candidatos, PC-5, PC-6 y PC-9 se cumplen solo porque no hubo nada que experimentar. No acreditan sensibilidad.
- No pude medir la duración de las sesiones omitidas en H2, así que no cuantifico la subestimación.
- El 93 % de las filas (372) no las contrasté semánticamente. Solo pasaron por los controles mecánicos.

## Abstentions

- **Si «Mantener» es correcto en las 398 filas:** no me pronuncio fuera de la muestra.
- **Si la autoridad delegada (mandato del 2026-11-02) alcanza el tramo 2:** no me corresponde ratificarlo, lo ratifica el dueño.
- **Si las tres sospechas son redundancias:** no lo declaro. Hace falta la evidencia experimental que indico en cada una.
