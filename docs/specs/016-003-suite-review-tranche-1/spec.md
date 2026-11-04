---
feature_id: 016-003-suite-review-tranche-1
approved_by: Pablo (HITL delegada al orquestador, docs/epics/epic-016-traceability-and-suite-review/execution.md)
approved_at: 2026-11-03
source: architect draft (sesión <ses-348>), materializado por el orquestador (ADR-003)
decision: se aprueban el selector reproducible con antigüedad por módulo, el tramo congelado de 398 nodeids sobre 1988, la auditoría con evidencia por fila, los experimentos acotados a candidatos, el costo medido por actividad y la decisión explícita de continuación; sin poda en esta feature
---

# Spec: 016-003-suite-review-tranche-1

## 1. Descripción funcional

**Actor:** responsable del mantenimiento de la suite.

**Objetivo:** revisar el 20% más nuevo de una colección congelada, identificar protección y posibles redundancias, comprobar experimentalmente los candidatos y conocer el costo antes de comprometer los siguientes tramos.

**Primer resultado útil:** un informe recuperable con una fila por nodeid seleccionado, disposición de R2, evidencia, altas reales de vínculo, resultados experimentales y decisión explícita sobre continuar.

Esta feature **no elimina, sustituye ni consolida tests**. Las oportunidades acreditadas originan, si se autorizan, unidades posteriores.

## 2. Decisiones de diseño

### Selección por colección, no por contadores del inventario

Se propone una herramienta pequeña bajo `skills/cdad-cycle/` que consuma la colección real de 016-001 y el historial Git. No dependerá del inventario específico de CDAD ni ejecutará automáticamente el runner.

Se descarta seleccionar el 20% de los módulos: módulos de tamaños muy distintos no representan el 20% de los tests.

### Antigüedad por módulo como aproximación explícita

Se ordenan los nodeids por antigüedad de incorporación de su **ruta de módulo**, no por incorporación histórica de cada protección. Es reproducible y barato; no permite afirmar cuándo nació una protección particular.

Se descarta reconstruir la genealogía individual de todos los nodeids: parametrizaciones, renombrados y movimientos convertirían la selección en otra investigación.

### Experimentos acotados, no demostración universal de redundancia

Quitar un test y obtener verde sobre el producto sano no demuestra redundancia. Para candidatos se compara su sensibilidad con la de verificadores alternativos frente a defectos contractuales concretos.

El resultado queda limitado a los defectos y al conjunto de comparación efectivamente examinados.

## 3. Fuentes, producto y responsabilidades

### Fuentes admitidas y protegidas

- Plan y mandato del epic 016.
- Propuesta de evidencia y trazabilidad, especialmente §3.C y §3ter.
- Specs y cierres de 016-001 y 016-002.
- Referencias canónicas de vínculos, R2 y mantenimiento de suite.
- Colección congelada, historial Git, inventario y mapa de PC.
- Tests seleccionados, fixtures/helpers necesarios y verificadores alternativos identificados.
- Contratos, auditorías y evidencia histórica recuperables de las unidades involucradas.
- Implementación: sólo para el encargo separado que prepare los experimentos; no como oráculo del test-writer.

### Producto propuesto

Bajo `skills/cdad-cycle/`:

- `scripts/cdad_suite_review.py`: selector reproducible.
- `references/suite-review.md`: procedimiento del tramo y límites.
- Puntero desde `contract-test-links.md`, sin duplicar su formato ni R2.

Fotografía documental del tramo, materializada por el orquestador:

```text
docs/specs/016-003-suite-review-tranche-1/tranche-1/
    report.md
    collection.json
    selection.json
    audit.json
    experiments/
    costs.json
    decision.md
```

`audit.json` contiene las filas; `report.md` presenta resumen y referencias, sin mantener otra clasificación independiente.

Los registros afectados conservan su ubicación de 016-001:

```text
docs/specs/<unidad-protegida>/contract-test-links.json
```

El test-writer propone sus deltas como texto. El orquestador los materializa. GREEN no modifica contratos, registros ni verificadores.

Los experimentos requieren una copia desechable y un workspace **declarados antes del despacho**. Este borrador no concede permisos sobre temporales ni autoriza mutaciones en el checkout original.

## 4. Selección congelada

### Regla

Para una revisión completa `R` y una colección válida del ámbito `["tests"]`:

1. Cada nodeid conserva su identidad literal, incluidos parámetros.
2. Su módulo es la parte anterior al primer `::`.
3. Para cada ruta se obtienen sus incorporaciones alcanzables desde `R`:

   ```sh
   git log --no-renames --diff-filter=A --format='%ct %H' R -- RUTA
   ```

4. Su incorporación de referencia es el mínimo par `(committer_timestamp, commit_hash)` de ese resultado.
5. Se ordenan los nodeids por:
   - timestamp de incorporación del módulo, descendente;
   - ruta de módulo, ascendente;
   - nodeid literal, ascendente.
6. Se toman los primeros `ceil(N/5)`, calculados como `(N + 4) // 5`.

No se siguen renombrados. No se usa fecha del filesystem, numeración de feature ni último cambio del archivo.

Una colección fallida, nodeids duplicados, revisión incompatible, módulo inexistente en la revisión, historial superficial o incorporación no recuperable impiden acreditar la selección; no se resuelven mediante estimaciones.

### Interfaz nueva propuesta — todavía no existe

```sh
python3 skills/cdad-cycle/scripts/cdad_suite_review.py select \
  --project-root ROOT \
  --revision REVISION_COMPLETA \
  --collection COLLECTION.json
```

Produce JSON por stdout, sin escribir archivos ni ejecutar tests. Incluye revisión, identidad del insumo, regla, incorporaciones por módulo, total, tamaño y lista literal ordenada del tramo.

Códigos propuestos: `0` selección válida; `1` insumo o historial incompatible; `2` uso inválido.

### Congelación propuesta para esta feature

- Revisión: `ad15c58a858e9a19994efb175bf65538975586f9`.
- Colección: **1988 nodeids**, 231 módulos.
- Tramo: **398 nodeids**.
- Restantes: **1590 nodeids**.
- SHA256 de la colección ordenada lexicalmente, un nodeid UTF-8 seguido de LF:

  ```text
  dc5fa7c4f5da1637c06b7f29569aaa1f0c701997b25380d701d1a5948dcea9d3
  ```

- SHA256 del tramo en el orden definido, misma codificación:

  ```text
  c733683243cfec2970768d58940139356dffd883027fca1f1a3aa860c98f9178
  ```

El conjunto exacto comprende **todos los nodeids recolectados** de estos módulos:

| Módulo, bajo `tests/` | Nodeids |
|---|---:|
| `test_016_002_gap_report.py` | 5 |
| `test_016_001_contract_test_link.py` | 11 |
| `test_015_002_intake_guards.py` | 10 |
| `test_015_001_frozen_reception.py` | 9 |
| `test_014_001_suite_evidence_defaults.py` | 4 |
| `test_013_002_live_inventory.py` | 7 |
| `test_013_001_criterion_coherence.py` | 5 |
| `test_012_installer_ignore_pycache.py` | 4 |
| `test_010_003_documentary_pilot.py` | 8 |
| `test_010_002_documentary_role_properties.py` | 7 |
| `test_010_002_documentary_role_integration.py` | 29 |
| `test_010_001_documentary_contracts.py` | 11 |
| `test_010_004_t6_b1_guard.py` | 1 |
| `test_010_004_t6_red.py` | 2 |
| `test_010_004_t5_e2e.py` | 2 |
| `test_010_004_t5_properties.py` | 2 |
| `test_010_004_t4_red.py` | 2 |
| `test_010_004_t3_red.py` | 7 |
| `test_010_004_t2_red.py` | 6 |
| `test_010_000_continuity_relative_root.py` | 5 |
| `test_009_002_opencode_v2_frontmatter.py` | 3 |
| `test_009_001_installer_agent_overlay.py` | 12 |
| `test_008_005_ci_gate.py` | 19 |
| `test_008_004_packet_enforcement.py` | 27 |
| `test_008_003_lifecycle_decisions.py` | 9 |
| `test_008_002_suite_evidence.py` | 5 |
| `test_008_002_suite_selection.py` | 25 |
| `test_008_002_variant_controls.py` | 4 |
| `test_008_001_pc8_adapter_budget.py` | 6 |
| `test_008_001_pc7_wrapper_margin.py` | 3 |
| `test_008_001_home_xdg_isolation.py` | 8 |
| `test_007_008_receipt_next_action.py` | 17 |
| `test_007_006_withdraw_and_republish.py` | 61 |
| `test_007_007_suspend_resume_units.py` | 19 |
| `test_007_003_legacy_reanchor.py` | 19 |

Son **374 nodeids**. Se añaden los 24 primeros nodeids lexicales de `tests/test_007_004_termination_not_success.py`: todos corresponden a

```text
test_007_004_delegate_rejects_invalid_delivery_combinations[PARAMETRO]
```

con estos parámetros exactos:

```text
blocked-none-valid
blocked-received-valid
blocked-staged-valid
cancelled-none-valid
cancelled-received-valid
cancelled-staged-valid
completed-none-null
completed-received-empty
completed-received-null
completed-received-wrong-type
completed-staged-empty
completed-staged-null
completed-staged-wrong-type
completed-unknown-valid
not-a-termination-none-null
timeout-none-valid
timeout-received-valid
timeout-staged-valid
transport-error-none-valid
transport-error-received-valid
transport-error-staged-valid
unknown-none-valid
unknown-received-valid
unknown-staged-valid
```

Los tests nuevos de esta feature no cambian retrospectivamente este universo; reciben sus vínculos por el recorrido ordinario.

## 5. Auditoría barata de cada test

Cada fila identifica:

- Nodeid y revisión congelada.
- Contrato, hash, obligación y promesa recuperables.
- Comprobación protegida: aserciones relevantes, preparación y helpers necesarios.
- Consecuencia concreta «sin este test, el usuario…».
- Referencias examinadas y localizadores.
- Exactamente una disposición del vocabulario canónico R2.
- Motivo de la disposición.
- Candidato a experimento, si corresponde, con hipótesis y verificadores alternativos.
- Incertidumbres y resultado del delta de vínculo.

Se lee el test y su preparación suficiente para entender el resultado observable, no sólo su nombre o docstring. El inventario orienta la búsqueda; no acredita pertinencia.

Se identifican candidatos cuando:

- Otro verificador parece proteger la misma promesa y el mismo defecto observable.
- Las variantes difieren internamente, pero no se identifica protección observable distinta.
- No se recupera una promesa vigente o las aserciones no parecen protegerla.

Un candidato no es una redundancia probada. Ante incertidumbre se aplica R2. Las recomendaciones que requieran modificar tests se derivan a otra unidad; no se ejecutan aquí.

**Sin vínculo inventado:** una ausencia queda como `VERIFY`, con búsquedas, fuentes y resolución necesaria. No se transforma en alta nominal ni en evidencia de protección. Si impide el vínculo comprometido para un test del tramo, bloquea acreditar el cierre salvo cambio autorizado del contrato.

## 6. Verificación cara de candidatos

Antes de ejecutar se registra, por candidato:

- Hipótesis y promesa.
- Defecto contractual concreto que se introducirá.
- Test candidato y conjunto literal de comparación, que puede incluir tests fuera del tramo.
- Justificación de inclusiones, exclusiones y dependencias compartidas.
- Revisiones, entorno, comandos, presupuesto finito y condición de parada.

El test-writer prepara la hipótesis desde contratos y tests, sin inspeccionar implementación. Un implementer separado prepara exclusivamente la degradación del producto en la copia autorizada; no modifica tests, contratos ni oráculos.

### Procedimiento

1. Ejecutar candidato y comparación contra producto sano.
2. Aplicar el defecto concreto en la copia y conservar su diff.
3. Ejecutar el candidato contra el producto degradado.
4. Ejecutar la comparación contra el mismo producto degradado, excluyendo literalmente al candidato.
5. Identificar si los fallos corresponden a la comprobación contractual esperada.

Un fallo de preparación, importación o infraestructura no cuenta como detección contractual.

### Interpretación

- **Aporte diferencial demostrado:** el candidato detecta un defecto válido que la comparación no detecta. Se registra el contraejemplo; no se propone suprimir esa protección.
- **Solapamiento observado:** los defectos válidos detectados por el candidato también los detecta la comparación. Sólo fundamenta una propuesta posterior, limitada a esos defectos y verificadores.
- **Inconcluso:** no se aplicó un defecto válido, ambos sobreviven, hay inestabilidad, faltan controles o se agotó el presupuesto. Se conserva el test; no se presenta como redundante.

Cada candidato debe tener un intento verificable y su resultado. Un plan sin ejecutar no satisface esta verificación. Si se agota el presupuesto dejando candidatos sin examinar, el tramo queda parcial y se solicita decisión; no se cierra silenciosamente.

No se realizan retiradas acumuladas ni se supone que varias retiradas individualmente admisibles sean compatibles juntas.

## 7. Costo y decisión de continuación

El registro conserva por actividad:

- Identificador de sesión y rol.
- Inicio, fin y duración observados.
- Alcance: selección, auditoría barata, experimento, revisión o materialización.
- Nodeids o candidatos atendidos.
- Comandos, duración, código de salida y referencias de logs.
- Tokens de entrada, salida y caché cuando el runtime los exponga; en caso contrario, **no disponibles**.

Se distinguen:

- Tiempo transcurrido total, sin sumar dos veces intervalos paralelos.
- Tiempo agregado de actividad por sesión.
- Tiempo de comandos.
- Preparación compartida frente a trabajo por test o candidato.

La proyección separa costo fijo, auditoría por test y experimentos por candidato. Usa cantidades observadas y muestra sus supuestos; no presenta el tramo más nuevo como muestra aleatoria del resto.

La ausencia de candidatos no acredita costo experimental cero: lo deja sin calibrar.

`decision.md` registra una decisión autorizada entre:

- Continuar con el siguiente tramo.
- Continuar con cambios explícitos de método o presupuesto.
- No continuar.

Incluye responsable, autoridad, motivo, evidencia de costo y alcance de lo autorizado. Una decisión pendiente no permite comprometer el tramo siguiente.

## 8. Promesas y postcondiciones

### A — Recuperar y repetir el tramo

<!-- cdad:pc PC-1 promise=A -->
**PC-1.** Con colección e historial válidos, el selector produce los nodeids definidos en §4, sus incorporaciones y tamaños; repetirlo con los mismos insumos produce los mismos bytes.

<!-- cdad:pc PC-2 promise=A -->
**PC-2.** Los insumos incompatibles definidos en §4 producen diagnóstico y salida no satisfactoria, sin acreditar un tramo completo ni ejecutar tests.

### B — Saber qué se revisó y qué protege

<!-- cdad:pc PC-3 promise=B -->
**PC-3.** El informe contiene exactamente una fila por nodeid seleccionado, sin omisiones ni incorporaciones externas, con comprobación, consecuencia, evidencia y una disposición R2 recuperables.

<!-- cdad:pc PC-4 promise=B -->
**PC-4.** Cada vínculo acreditado resuelve contra contrato y obligación reales conforme a 016-001; los deltas son materializados por el orquestador y comprobados contra colección actual. Una ausencia o referencia rota queda visible y no se contabiliza como vínculo válido.

### C — Contrastar las sospechas sin confundirlas con prueba

<!-- cdad:pc PC-5 promise=C -->
**PC-5.** Cada candidato tiene hipótesis preregistrada, selección de comparación y evidencia de los intentos del §6, con revisiones, comandos, resultados y límites recuperables.

<!-- cdad:pc PC-6 promise=C -->
**PC-6.** Un defecto detectado únicamente por el candidato se registra como aporte diferencial; un fallo ajeno a la comprobación contractual no se acredita como sensibilidad. Ningún resultado acotado se presenta como redundancia universal ni autoriza poda.

### D — Conocer el costo antes de escalar

<!-- cdad:pc PC-7 promise=D -->
**PC-7.** El informe permite reconstruir costo observado por actividad, sesiones y comandos, distingue ausencia de métricas de cero y evita doble conteo de trabajo paralelo.

<!-- cdad:pc PC-8 promise=D -->
**PC-8.** La proyección del resto declara fórmula, cantidades observadas y supuestos; la entrega incluye una decisión autorizada y explícita sobre continuar, modificar o detener.

### E — Entregar evidencia sin alterar las garantías

<!-- cdad:pc PC-9 promise=E -->
**PC-9.** El tramo deja intactos los tests y el producto original durante los experimentos; los cambios experimentales y logs pertenecen exclusivamente a la copia y workspace autorizados.

<!-- cdad:pc PC-10 promise=E -->
**PC-10.** La entrega distingue control estructural, ejecución real y revisión semántica independiente. No solicita aceptación con pendientes que impidan verificar una promesa comprometida.

## 9. Invariantes verificables

- Los nuevos tests no alteran la selección congelada.
- Parametrizaciones conservan nodeids literales.
- Una fila, una disposición R2.
- Candidato no equivale a redundante.
- Una referencia que resuelve no equivale a protección pertinente.
- Declarado, ejecutado y contrastado semánticamente permanecen separados.
- Ningún experimento modifica sus oráculos.
- Ninguna retirada o consolidación se ejecuta en esta feature.

## 10. Aceptación

El cierre requiere:

1. Selección congelada reproducible y materializada.
2. Las 398 filas de auditoría con evidencia recuperable.
3. Altas de vínculo reales, validadas, sin suplir faltantes con asociaciones nominales.
4. Candidatos contrastados según §6, conservando resultados negativos e inconclusos.
5. Costo medido y decisión autorizada.
6. Revisión independiente de correspondencia entre filas, fuentes, vínculos y conclusiones.
7. Evidencia de tests del selector y método; los nuevos verificadores quedan vinculados conforme a 016-001.

El control automático acredita estructura. La revisión independiente declara qué afirmaciones contrastó y sus límites. Ninguno promete detección semántica infalible.

La evidencia de cierre aplica la política canónica existente; no se crea otro gate ni se considera una colección como ejecución de la suite.

## 11. deferred-hardening

- **Antigüedad individual de cada protección:** se utiliza el proxy por módulo; reconstruir genealogía individual excede la selección comprometida.
- **Demostración universal de redundancia:** los experimentos son finitos y la comparación está acotada.
- **Poda y consolidación efectivas:** requieren unidades propias con conservación y sensibilidad acreditadas.
- **Extrapolación estadística de redundancia:** el tramo más nuevo no es muestra probabilística.
- **Backfill fuera del tramo:** sólo se incorporan vínculos demandados por esta revisión.
- **Autenticación criptográfica de ejecuciones y métricas:** se conserva atribución operacional y su límite.
- **Automatización general del juicio semántico:** no sustituye la revisión independiente.
