# test-audit.md — 016-003 (AUDIT)

**Unidad:** `016-003-suite-review-tranche-1` · **Subfase:** `audit` (test-writer)
**Contrato:** `docs/specs/016-003-suite-review-tranche-1/spec.md` (sha256 `b3f91691e9cd44e32b60f5fa9aa98b42fffa9e363757a4ec28592622d069f9c4`, aprobada 2026-11-03)
**Packet:** `016-003-suite-review-tranche-1-test-writer-audit-001` · **Alcance de lectura:** `docs/specs/016-003-suite-review-tranche-1` + `tests/` · **Escritura:** ninguna en esta subfase.

**Regla de selección (R2, hogar):** un test por promesa observable, nunca cuota por postcondición/simetría/cobertura. Cada incorporación declara qué protección falta y la consecuencia «sin este test, el usuario…». Cada test auditado recibe exactamente una disposición (PC-4). Ante incertidumbre, Mantener. Ninguna recomendación que requiera modificar tests se ejecuta aquí; se deriva a otra unidad.

**Oráculo de este audit:** deriva sólo del contrato aprobado + referencias recuperables en `tests/` (nombres, docstrings, mapeos test→postcondición declarados en cada módulo). No se leyó implementación. Búsquedas: `cdad_suite_review` / `suite-review` / `suite_review` en `tests/` = **cero coincidencias** → ninguna postcondición PC-1..PC-10 de esta unidad está protegida hoy.

## §1 — Disposiciones sobre verificadores existentes

La herramienta nueva (`skills/cdad-cycle/scripts/cdad_suite_review.py`, hoy inexistente) y la referencia (`references/suite-review.md`, hoy inexistente) son **aditivas**: no renombran, mueven ni borran nada existente. Esta feature **no elimina, sustituye ni consolida tests** (spec §1, invariantes). Por tanto no hay Sustituir/Consolidar/Retirar/Extender en este audit. Todo lo vigente se conserva con **Mantener**, verificado verde donde se corrió (ver Evidencia).

### 1A — Instalador: bytes y ownership de `skills/` (37 tests) → Mantener (37×)

| Módulo | Tests | Disposición |
|---|---|---|
| `tests/test_install_ownership.py` (11: case1..case10 + r3o2) | `test_t5_case1…case10`, `test_t5_r3o2_install_manifest_records_resolved_stack` | **Mantener** c/u |
| `tests/test_install_review5_regressions.py` (6) | todos | **Mantener** c/u |
| `tests/test_005_004_t2_installer_claims.py` (8) | todos | **Mantener** c/u |
| `tests/test_009_001_installer_agent_overlay.py` (12) | todos | **Mantener** c/u |

- **Promesa/postcondiciones que protegen:** las de sus propios contratos (004-001 PD-5/6/7/8/18, 012 PC-1..PC-4, overlay de agentes). **No protegen** ninguna PC-1..PC-10 de 016-003 (búsqueda sin coincidencias de `cdad_suite_review`/`suite-review`).
- **Contribución respecto de lo existente:** su oráculo es dinámico (manifiesto de staging) o por forma (`__pycache__`/`.pyc`/`.pyo` por shape; overlay por destinos declarados), no por lista fija de bytes de `skills/`. Añadir un script + una referencia sólo **agrega** artefactos al staging; ningún assert congela el conjunto exacto de `skills/`.
- **Consecuencia si faltara cada uno:** la de su propio contrato (p. ej. sin `test_t5_case1`, el usuario aceptaría un install a medio estado como propio). **Ninguna** cubre «sin este test, el usuario aceptaría un tramo irreproducible» → no sustituyen al RED de 016-003.
- **Restricción a GREEN (no a este audit):** el GREEN debe regenerar staging/instalación de forma que estos 37 sigan verdes; si alguno enrojeciera por el alta, el defecto es del GREEN, no causa de Retirar.

### 1B — Documentación: referencias únicas y frases normativas (55 tests) → Mantener (55×)

| Módulo | Tests | Disposición |
|---|---|---|
| `tests/test_010_001_documentary_contracts.py` (11) | `test_the_norm_defines_…` … `test_isolated_install_distributes_…` | **Mantener** c/u |
| `tests/test_010_002_documentary_role_properties.py` (7) | todos | **Mantener** c/u |
| `tests/test_010_002_documentary_role_integration.py` (29) | todos | **Mantener** c/u |
| `tests/test_010_003_documentary_pilot.py` (8) | todos | **Mantener** c/u |

- **Riesgo examinado:** `test_no_installable_surface_copies_the_normative_phrases` (010-001, PC-13) barre `skills/`, `sources/`, `agents/` excluyendo la propia referencia. La nueva `references/suite-review.md` **no rompe** ese test salvo que copie frases normativas (≥6 palabras / líneas ≥8) de `documentary-contracts.md` o viceversa.
- **Contribución:** protegen unicidad y punteros de la casa normativa; **no protegen** PC-1..PC-10 de 016-003 (el procedimiento del tramo no es frase normativa de esa casa).
- **Consecuencia si faltara cada uno:** la de su contrato (duplicación silenciosa de la casa). Ninguna cubre el tramo.
- **Restricción a GREEN:** redactar `suite-review.md` con vocabulario propio, sin reproducir oraciones normativas de la casa; el puntero `contract-test-links.md → suite-review` (si se añade) nombra archivo, no redacción (verbatim admitido por 010-001 §4).

### 1C — Tests que enumeran scripts o subcomandos (72 tests) → Mantener (72×)

| Módulo | Tests | Disposición |
|---|---|---|
| `tests/test_008_004_packet_enforcement.py` (19) | todos | **Mantener** c/u |
| `tests/test_008_005_ci_gate.py` (13) | todos | **Mantener** c/u |
| `tests/test_008_002_suite_selection.py` (27) | todos (usan `scripts/cdad-suite.py` sintético en tmp, no el checkout) | **Mantener** c/u |
| `tests/test_008_002_suite_evidence.py` (9) | todos | **Mantener** c/u |
| `tests/test_008_002_variant_controls.py` (4) | todos | **Mantener** c/u |

- **Riesgo examinado:** ningún módulo fija la lista exacta de `skills/cdad-cycle/scripts/` ni los subcomandos de `cdad_contract_links.py`. `008-005` construye CLIs grabadoras sintéticas; `008-004` valida paquetes, no inventario de scripts; `008-002` copia el CLI a tmp. Añadir `cdad_suite_review.py` (binario nuevo, no subcomando de `cdad_contract_links.py`) no altera sus oráculos.
- **Consecuencia si faltara cada uno:** la de su contrato (gate, selección, evidencia). Ninguna cubre el selector por antigüedad de módulo.

### 1D — Inventario, coherencia y evidencia de suite (16 tests) → Mantener (16×)

| Módulo | Tests | Disposición |
|---|---|---|
| `tests/test_013_002_live_inventory.py` (7) | `test_013_002_A_…` (2), `_B_…`, `_C_…` (2), `_D_…` (2) | **Mantener** c/u |
| `tests/test_013_001_criterion_coherence.py` (5) | todos | **Mantener** c/u |
| `tests/test_014_001_suite_evidence_defaults.py` (4) | `test_A_…`, `test_B_…`, `test_C_…`, `test_D_…` | **Mantener** c/u |

- **Riesgo examinado:** `013-002` lista módulos del inventario de tests y referencias fijas (`handoff-prompts`, `re-entry`, …); no enumera `skills/cdad-cycle/scripts/` ni fija el universo de referencias (no menciona `suite-review`). `014-001` fija el hogar de evidencia, no la lista de referencias. Verdes hoy (ver Evidencia: 15 passed con 012, 24 passed con 015-001/002).
- **Consecuencia si faltara cada uno:** la de su contrato (inventario no vivo, criterio incoherente, defaults ambiguos). Ninguna cubre PC-1..PC-10 del tramo.

### 1E — Los 11 de 016-001 + 5 de 016-002 (16 tests) → Mantener (16×)

- `tests/test_016_001_contract_test_link.py` (11: `test_R_A1`, `test_R_B1..B6`, `test_R_C1`, `test_R_C2`, `test_R_D1`, `test_R_D2`) → **Mantener** c/u.
- `tests/test_016_002_gap_report.py` (5: `test_R_A`, `test_R_B`, `test_R_C`, `test_R_D`, `test_R_E`) → **Mantener** c/u.
- **No comparten módulo** con el futuro RED de esta unidad (nuevo archivo `tests/test_016_003_suite_review_tranche_1.py`, nombre sin colisión). Comparten **patrón** de fixtures (proyecto temporal, colecciones `CURRENT/BASE`, registros) pero sin importación cruzada: cada módulo copia sus helpers (`make_project`, `make_collection`, `sha256_of`). El CLI es **binario distinto** (`cdad_contract_links.py` `validate`/`gap-report` vs nuevo `cdad_suite_review.py` `select`): sin interferencia de subcomandos. Verdes hoy (16 passed).
- **Contribución:** protegen vínculos (016-001) e informe de huecos (016-002); son **insumos** del tramo (colección, historial, mapa de PC), no su verificación. Sin ellos no habría qué revisar, pero ninguno afirma nada sobre selección 398/1988, filas por nodeid, experimentos o costo.
- **Consecuencia si faltara cada uno:** la declarada en su docstring (p. ej. sin `R_C1`, nodeids nuevos sin vínculo pasarían silenciosos). Ninguna cubre «tramo congelado correcto».

### 1F — Resto del tramo congelado mencionado en §4 (verificación de no-colisión)

Los módulos del tramo (`test_007_006` 61, `test_007_007` 19, `test_007_003` 19, `test_007_008` 17, `test_008_001_*`, `test_009_*`, `test_010_004_*`, `test_012` 4, `test_015_*` 19, etc.) son el **objeto** de la revisión documental, no sus verificadores RED: sus dispositions R2 se auditan en la fotografía del tramo (filas `audit.json`), no en este audit de suite. No se dispone sobre ellos aquí salvo 1D/1E ya cubiertos; el resto **Mantener por defecto ante incertidumbre** (PC-4: ante incertidumbre se conserva con Mantener) y sin evidencia de sensibilidad a dos archivos aditivos bajo `skills/cdad-cycle/`.

## §2 — Mapeo promesa→verificadores RED (PC-1..PC-10, grupos A–E)

Ningún verificador existente protege estas postcondiciones (§1: cero coincidencias + oráculos disjuntos). Se requieren **5 Añadir** (uno por promesa observable A–E; cada uno traza a sus PCs; la trazabilidad múltiple es deliberada, no cuota). El RED falla por `AssertionError` sobre conducta pendiente (CLI `select` inexistente / referencia inexistente), nunca por `ImportError`.

- **R-A — Promesa A (Recuperar y repetir el tramo) → PC-1, PC-2 → Añadir** `test_R_A_seleccion_congelada_reproducible_y_diagnostico_ante_insumo_incompatible`.
  Sin este test, el usuario aceptaría un tramo distinto del congelado (§4: 398 nodeids, `dc5fa7…`/`c73368…`) o un `0` ante colección fallida/duplicados/revisión incompatible/historial superficial. **Mecánico:** orden por `(timestamp módulo desc, ruta asc, nodeid asc)`, `ceil(N/5)`, identidad literal con parámetros, bytes idénticos al repetir; códigos `0/1/2`. **A revisión independiente:** que la antigüedad por módulo sea proxy declarado (no genealogía individual) — el test no lo acredita, lo declara en límites.
- **R-B — Promesa B (Saber qué se revisó y qué protege) → PC-3, PC-4 → Añadir** `test_R_B_fila_por_nodeid_con_disposicion_y_vinculo_recuperable`.
  Sin este test, el usuario recibiría filas de menos/más, disposiciones sin evidencia, o un vínculo inventado contado como protección. **Mecánico:** exactamente una fila por nodeid, aserciones/preparación/helpers/consecuencia/referencias+localizadores/disposición R2/motivo/candidato/incertidumbres; conteo de altas reales de vínculo. **A revisión independiente:** pertinencia (una referencia que resuelve ≠ protección pertinente) y corrección de la disposición R2 elegida.
- **R-C — Promesa C (Contrastar sospechas) → PC-5, PC-6 → Añadir** `test_R_C_candidato_con_hipotesis_y_comparacion_con_resultado_acotado`.
  Sin este test, el usuario leería un candidato como redundancia probada y podaría protección real. **Mecánico:** hipótesis preregistrada, defecto contractual concreto, candidato + conjunto literal de comparación, revisiones/entorno/comandos/presupuesto/condición de parada, 5 pasos del §6, clasificación aporte/solapamiento/inconcluso. **A revisión independiente:** idoneidad del defecto y del conjunto de comparación, y que ningún resultado acotado se presente como universal ni autorice poda.
- **R-D — Promesa D (Conocer el costo) → PC-7, PC-8 → Añadir** `test_R_D_costo_reconstruible_y_proyeccion_con_supuestos_mas_decision`.
  Sin este test, el usuario escalaría a ciegas: doble conteo de paralelo, métricas ausentes leídas como cero, tramo nuevo tratado como muestra aleatoria. **Mecánico:** por actividad (sesión, alcance, nodeids/candidatos, comandos+rc+refs, tokens o «no disponibles»), separación transcurrido/agregado/comandos/compartido, fórmula de proyección con cantidades observadas, `decision.md` (continuar / continuar-con-cambios / no-continuar + responsable/autoridad/motivo/evidencia/alcance). **A revisión independiente:** razonabilidad de supuestos y de la decisión.
- **R-E — Promesa E (Entrega sin alterar garantías) → PC-9, PC-10 → Añadir** `test_R_E_experimentos_en_copia_y_entrega_con_control_declarado`.
  Sin este test, el usuario aceptaría un tramo cuyos experimentos mutaron tests/producto original, o una aceptación con pendientes que impiden verificar una promesa. **Mecánico:** inmutabilidad de tests y producto original durante experimentos (diff confinado a copia + workspace declarado), logs en copia; entrega que distingue estructural/ejecución/revisión semántica. **A revisión independiente:** qué afirmó cada registro y sus límites (ningún gate promete detección semántica infalible).

**Lo que queda a revisión independiente en todos los grupos** (nunca al RED mecánico): correspondencia filas↔fuentes↔vínculos↔conclusiones (aceptación §6), pertinencia de cada protección, y límites de la evidencia. El control automático acredita estructura; la revisión declara qué contrastó.

## §3 — Fixtures propios del RED (autocontenidos, sin leer implementación)

- Repositorio git temporal con módulos de antigüedad conocida (commits con `committer_timestamp` controlado, renombrados presentes para probar que **no** se siguen, §4 regla).
- Colecciones válida (1988 sintéticos o muestra con misma regla `ceil(N/5)`), fallida (`exit_code=1`), con duplicados, con revisión incompatible, con módulo inexistente, con historial superficial (`--depth 1`).
- `nodeids` literales con parámetros; `collection.json`/`selection.json` esperados por bytes.
- Caja negra por ruta: `python3 skills/cdad-cycle/scripts/cdad_suite_review.py select …` (hoy inexistente → RED rojo por `AssertionError`, no `ImportError`).

## §4 — deferred-hardening (sin test ordinario; con motivo)

- Antigüedad individual por protección (se usa proxy por módulo; genealogía individual excede lo comprometido — spec §11).
- Demostración universal de redundancia (experimentos finitos y acotados).
- Poda/consolidación efectivas (requieren unidades propias con conservación + sensibilidad).
- Extrapolación estadística (el tramo nuevo no es muestra probabilística).
- Backfill fuera del tramo (sólo vínculos demandados por esta revisión).
- Autenticación criptográfica de ejecuciones/métricas (atribución operacional + límite).
- Automatización general del juicio semántico (no sustituye revisión independiente).

## Evidencia (re-entry)

- **Archivos modificados:** ninguno (AUDIT no altera tests; informe como TEXTO FINAL para aprobación del dueño y materialización por el orquestador).
- **Comandos exactos:**
  - `python3 skills/cdad-cycle/scripts/cdad_packet.py render --request .cdad/packets/016-003-suite-review-tranche-1-test-writer-audit-001/REQUEST.json` → `diff` contra `PACKET.md` = idéntico (PACKET_MATCH:YES); `sha256sum docs/specs/016-003-suite-review-tranche-1/spec.md` = `b3f91691…069f9c4` (coincide); `execution.json schema_version: 2`.
  - `python3 -m pytest tests/test_016_001_contract_test_link.py tests/test_016_002_gap_report.py -q` → **16 passed in 13.00s**.
  - `python3 -m pytest tests/test_012_installer_ignore_pycache.py tests/test_013_002_live_inventory.py tests/test_014_001_suite_evidence_defaults.py -q` → **15 passed in 109.52s**.
  - `timeout 300 python3 -m pytest tests/test_013_001_criterion_coherence.py tests/test_015_001_frozen_reception.py tests/test_015_002_intake_guards.py -q` → **24 passed in 61.92s**.
  - Búsquedas sólo en `tests/`: `cdad_suite_review|suite-review` = 0; `contract-test-link|cdad:pc` sólo en 016-001 (11 tests); `gap-report` sólo en 016-002 (5 tests).
- **Salida:** la citada arriba (verdes proporcionales del ciclo focal; suite completa no realizada en este audit — la política canónica la reserva al cierre de feature/epic; se registra selección y límites aquí).
- **Commit:** ninguno en esta subfase (sin cambios en `tests/`; la decisión del dueño sobre este audit precede a RED).

**Decisión propuesta al dueño:** aprobar (1) los 196+ Mantener de la superficie examinada (1A–1E; resto Mantener por defecto ante incertidumbre) y (2) los 5 Añadir R-A..R-E con sus fixtures. Tras la aprobación, RED crea exclusivamente `tests/test_016_003_suite_review_tranche_1.py` (un módulo por promesa-grupo, sin tocar módulos vigentes).
