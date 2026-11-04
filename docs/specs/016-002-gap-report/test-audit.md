# test-audit.md — 016-002-gap-report (AUDIT)


## 0. Alcance y método

- Contrato: `docs/specs/016-002-gap-report/spec.md` sha256 `315fad2c…54bc7c4b` (verificado por bytes).
- Subfase: AUDIT. Sin edición de tests. Selección por promesa observable (R2 hogar), contribución respecto de lo existente (PC-1–PC-3), una única disposición por test (PC-4).
- Búsqueda: `tests/test_016_001_contract_test_link.py` (11 `def test_`), `grep` por `cdad_contract_links|contract-test-links|gap-report|--help|subcommand`, inventario `tests/test_*install*`, `test_005_005_*`, `test_010_*`, `test_role_packet_render.py`, `test_packet_prepare.py`, `test_004_001_t7_capacity.py`.
- Resultado: **cero verificadores existentes protegen PC-1..PC-10 de 016-002** (ningún test menciona `gap-report`; el único consumidor de `cdad_contract_links` es 016-001 `validate`). Todo lo RED es `Añadir`. Ningún `Sustituir/Consolidar` (no hay original vigente que reemplazar) y por tanto nada va a POST-AUDIT en este ciclo.
- Oráculo RED futuro: caja negra por ruta (`python3 <cdad-cycle>/scripts/cdad_contract_links.py gap-report ...`), fixtures propios autocontenidos (estado, contrato, registro, colección, exclusiones), nunca el producto bajo `skills/`.

## 1. Verificadores existentes potencialmente afectados — disposiciones

Todas las disposiciones son finales en este AUDIT. Referencias posteriores no duplican disposición.

### 1.1 Interfaz de `cdad_contract_links.py` — 016-001 (11 verificadores)

**Archivo:** `tests/test_016_001_contract_test_link.py` — 11 tests:
`R_A1`, `R_B1`, `R_B2`, `R_C1`, `R_C2`, `R_D1`, `R_D2`, `R_B3`, `R_B4`, `R_B5`, `R_B6`.

- **Disposición: Mantener (×11, una por test).**
- **Promesa / PCs que protegen:** las de 016-001 (`validate`), no las de 016-002.
- **Contribución respecto de lo existente:** fijan que `validate` mantiene códigos, `mode` (`markers|legacy|not_configured|invalid`), `obligations`, `gaps`, `new_unlinked`, `not_configured` vs `invalid`, y no-modificación. La spec 016-002 §2 declara explícitamente "esto no cambia los códigos ni el comportamiento de `validate`".
- **Por qué Mantener y no Extender:** `gap-report` es subcomando nuevo con flags propios (`--state`, `--registry UNIT=...`, `--collection`, `--exclusions`); ningún test 016-001 invoca `gap-report` ni enumera subcomandos del CLI de links, luego no hay colisión. Extenderlos para cubrir `gap-report` mezclaría promesas de dos unidades y violaría R2.
- **Consecuencia si se retiraran:** "without this test, the user would accept a `gap-report` change that silently breaks `validate` (falso verde/rojo de trazabilidad existente) sin detectarlo".
- **Riesgo vigilado (no acciona disposición):** si GREEN toca el parser compartido (marcadores, `duplicate_marker`, reorden-insensible, `mode`), estos 11 son la red de regresión; el runner de cierre los incluye.

### 1.2 Instalador — comparación de bytes de `skills/`

**Archivos:** `tests/test_005_004_t2_installer_claims.py` (bytes staged==deployed, ayuda del instalador), `tests/test_006_003_u2_installer_without_profiles.py`, `tests/test_006_002_u4_skill_without_models.py`, `tests/test_006_002_u2_neutral_skill.py`, `tests/test_009_001_installer_agent_overlay.py`, `tests/test_012_installer_ignore_pycache.py`, `tests/test_install_ownership.py`, `tests/test_install_review5_regressions.py`.

- **Disposición: Mantener (cada test conserva la suya; ante incertidumbre se conserva).**
- **Contribución:** garantizan despliegue verbatim, no lista cerrada de archivos. El producto 016-002 vive bajo `skills/` (subcomando + ampliación de `contract-test-links.md` + punteros), es decir añade bytes staged que el instalador debe desplegar intactos.
- **Por qué no Extender:** ningún test fija hoy la lista exacta de archivos de `skills/cdad-cycle/`; son agnósticos a archivos nuevos. Si alguno enumerara inventario cerrado de `skills/`, ese solo pasaría a Extender en RED con motivo registrado — la inspección actual no encuentra tal enumeración.
- **Consecuencia:** "without these tests, the user would ship a `gap-report` whose bytes differ between staged and deployed (instalación que recorta/transforma) creyendo que instaló lo aprobado".

### 1.3 Documentación — referencias únicas

**Archivos:** `tests/test_010_001_documentary_contracts.py`, `tests/test_010_002_documentary_role_integration.py`, `tests/test_010_003_documentary_pilot.py`, `tests/test_005_005_t2_docs_policy.py`, `tests/test_005_005_t3_provenance.py` y familia `010_004_*`.

- **Disposición: Mantener.**
- **Contribución:** fijan unicidad/no-paráfrasis de referencias normativas y distribución de la referencia. La ampliación de `contract-test-links.md` (entradas, salida, exclusiones, códigos, límites) debe redactarse sin duplicar frases normativas existentes ni romper punteros.
- **Consecuencia:** "without these tests, the user would merge a `contract-test-links.md` ampliada que duplica o contradice la referencia canónica y la auditoría citaría dos normas distintas para la misma entrada".

### 1.4 Oráculos que enumeran subcomandos o `--help`

**Archivos:** `tests/test_role_packet_render.py::test_p1_all_role_substage_pairs_render_and_validate` (+ `require_command("validate-request")`), `tests/test_packet_prepare.py` (`prepare --help`, `validate-packet`, `validate-state`), `tests/test_004_001_t7_capacity.py` (`--help` expone `prepare`), `tests/test_005_011_t1_relative_root.py` (`consistent_across_subcommands`).

- **Disposición: Mantener.**
- **Contribución:** fijan la superficie de `cdad_packet.py` (`prepare|render|validate-*|...`), no la de `cdad_contract_links.py`. `gap-report` no añade subcomando a `cdad_packet.py`, luego no los afecta. Ningún test actual enumera los subcomandos de `cdad_contract_links.py` (`validate` vs `gap-report`), por lo que no hay oráculo que se vuelva rojo por el mero añadido.
- **Consecuencia:** "without these tests, the user would rename/remove a subcommand of the packet CLI during the `gap-report` change and the dispatch chain would break silently".
- **Nota prospectiva (no disposición):** si en RED alguien propone un test que enumere `validate|gap-report --help`, ese sería `Añadir` de 016-002, nunca `Extender` de estos: promesas distintas, CLIs distintos.

## 2. Mapeo promesa → verificadores RED (PC-1..PC-10, grupos A–E)

Cada fila es un `Añadir` (creación por protección faltante, nunca destino de sustitución). Un test por promesa observable; un test puede cubrir sus 2 PCs (trazabilidad, no cuota). Todo lo semántico (pertinencia, sensibilidad, aceptación) queda fuera por spec §1/§4/§10 y se declara en límites; el verificador solo comprueba estructura, referencias, códigos y reproducibilidad.

Fixturas propias exigidas (autocontenidas, sin demo-data, sin leer producto): estados con cierres registrados + históricos + ambiguos; contratos con marcadores y con índice legacy; registros válidos/rotos/corruptos/ausentes; colecciones CURRENT válidas/fallidas/vacías; exclusiones válidas e inválidas. Cada RED invoca `gap-report` por ruta como caja negra y falla por `AssertionError` de comportamiento (exit/payload), nunca `ImportError`.

### R-A — promesa A "Saber qué contratos se examinaron" — PCs 1, 2 — Añadir

- **Cubre:** universo desde `--state` (epic_features + epic_history, precedencia actual, deduplicación histórica, ambigüedad por cierres incompatibles); cierre no registrado fuera del universo con diagnóstico vs evidencia rota → exit 1 con referencia identificada, sin informe completo.
- **Sin este test, el usuario:** reincorporaría silenciosamente una unidad cerrada-histórica sobre una fila actual no cerrada, o confundiría "sin evidencia" con "evidencia rota" y aceptaría un informe incompleto como completo.
- **Mecánico vs semántico:** mecánico = reglas de universo, hash de cierre, recuperabilidad de evidencia; semántico (no se testea) = si el cierre "debió" aceptarse.
- **Fixtures:** estado con `done` + `closure_evidence{path,sha256}` válida; fila actual no-`done` + copia histórica `done` (debe quedar fuera); `done` sin evidencia (cierre no registrado); evidencia con sha mismatch / path irresoluble (exit 1); estado corrupto (exit 1); estado válido sin cierres (universo vacío explícito).

### R-B — promesa B "Distinguir huecos de desconocimiento" — PCs 3, 4 — Añadir

- **Cubre:** obligaciones desde marcadores reales (con criterio ejemplo-vs-obligación, backtick suelto, duplicado) o solo `legacy_obligations`, sin mezclar; sin ambos → `not_indexed`; registro presente sin obligaciones → inválido (exit 1); quitar último verificador → `gap` agrupado por promesa; compartir verificador no exige más; `review` válido cuenta como declarado sin ejecutarse; cobertura legacy dice "obligaciones indexadas; no extracción exhaustiva".
- **Sin este test, el usuario:** presentaría `not_indexed` como cubierta o como hueco, inventaría promesas, o exigiría un test por obligación compartida (cuota), o confundiría un `review` con un test ejecutado.
- **Mecánico vs semántico:** mecánico = indexación, agrupación, conteo de disposiciones (`declared|gap|excluded` exactamente una por obligación válida); semántico (no se testea) = pertinencia/sensibilidad del verificador.
- **Fixtures:** contrato con marcadores (incl. inline/backtick/duplicado), contrato legacy solo con índice, contrato sin ambos, registro vacío, registro roto, colección con/sin nodeids.

### R-C — promesa C "Apartar una promesa sin ocultar la decisión" — PCs 5, 6 — Añadir

- **Cubre:** exclusión válida mueve promesa completa a sección excluidas con motivo/archivo/hash/localizador recuperables, sin contarla como protegida; exclusión inválida (motivo vacío, identidad ambigua/duplicada, contrato promesa/ruta/sha que no corresponde al universo indexado) → exit 1 sin suprimir el hueco.
- **Sin este test, el usuario:** excluiría una promesa y la leería como "protegida" (cobertura inflada), o colaría una exclusión con motivo vacío/duplicada que borra huecos accionables del informe.
- **Mecánico vs semántico:** mecánico = validez referencial y preservación del motivo; semántico (no se testea) = si el motivo "justifica" priorizar (decisión del dueño/orquestador).
- **Fixtures:** exclusiones válidas e inválidas (una por caso: motivo blanco, unidad fuera del universo, promise fuera del índice, sha distinto, duplicada misma unidad+promesa).

### R-D — promesa D "Repetir y auditar el resultado" — PCs 7, 8 — Añadir

- **Cubre:** informe con entradas identificadas por hash, orden estable (unidades, promesas, obligaciones, verificadores canónicos, diagnósticos), byte-reproducible con mismas entradas, reorden de bindings sin efecto; no modifica entradas, no ejecuta tests, respeta códigos 0/1/2, defectos de registros/colecciones identificados sin acreditarlos, `validate` compatible.
- **Sin este test, el usuario:** aceptaría informes no reproducibles (con hora/rutas absolutas/aleatoriedad), o un exit 0 que en realidad ejecutó tests o mutó fuentes, o una regresión silenciosa de `validate`.
- **Mecánico vs semántico:** todo mecánico y determinista; la contrapartida de aceptación es R-E/Review independiente.
- **Fixtures:** doble corrida mismo input (igualdad byte a byte), bindings reordenados, colección fallida, registro inválido, snapshot pre/post de mtimes+hashes de entradas, matriz de códigos (0 válido con huecos/excluidos/no-indexados; 1 datos rotos; 2 CLI inválida).

### R-E — promesa E "Adoptarlo sin imponer una migración" — PCs 9, 10 — Añadir

- **Cubre:** sin registros se produce informe sin colección ("sin registro de vínculos declarado", no-indexados + huecos conocidos si hay marcadores, sin exigir inventario/`pc-map`/backfill, sin gate nuevo); informe y referencia operativa declaran comprobación estructural, distinguen cobertura legacy de universo de marcadores, niegan ejecución/pertinencia/sensibilidad/aprobación; documentación identifica al orquestador como materializador de exclusiones/fotografías.
- **Sin este test, el usuario:** bloquearía el ciclo normal por no tener registros, o exigiría migración (inventario vivo, backfill, gate) para adoptar `gap-report`, o leería el informe como prueba de ejecución/aceptación.
- **Mecánico vs semántico:** mecánico = producción sin colección y textos límite presentes; semántico = revisión independiente del tramo (criterio de aceptación §10, fuera de este test).
- **Fixtures:** proyecto sin registros (sin `--registry`, sin `--collection`), contrato con marcadores huérfanos (huecos conocidos sin registro), inspección de límites en stdout y en `contract-test-links.md` ampliada (cadenas "estructural", "no ejecuta", "obligaciones indexadas").

## 3. `deferred-hardening` (propuesto; el orquestador lo fija en spec)

Nada de abajo exige test RED en este ciclo; cada aplazamiento registra su motivo:

- Extracción exhaustiva del Markdown histórico; descubrimiento de cierres fuera de estructuras declaradas; autenticación de colecciones/autoría criptográfica; inferencia de pertinencia/sensibilidad/suficiencia; optimización sobre todo el corpus; comparación histórica automática — todos ya listados en spec §11, se conservan.

## 4. Evidencia de esta subfase

- `modified files`: ninguno (AUDIT no edita tests).
- `exact commands`: `sha256sum docs/specs/016-002-gap-report/spec.md`; `python3 scripts/cdad_packet.py validate-request ...`; `validate-packet ...`; `render ...` + `diff` vs `PACKET.md`; `grep -rln ... tests/`; `ls tests/test_016*`; conteo `def test_`.
- `command output`: sha `315fad2c…54bc7c4b` coincide con REQUEST/identificación; `validate-request EXIT:0`; `validate-packet EXIT:0`; `diff` vacío (`PACKET MATCHES CANONICAL RENDER`); `tests/test_016_001_contract_test_link.py` único consumidor de links con 11 tests; cero menciones a `gap-report` en `tests/`.
- `commit`: ninguno en AUDIT (el informe se entrega como TEXTO FINAL; el orquestador lo materializa y el commit lo acredita él).
