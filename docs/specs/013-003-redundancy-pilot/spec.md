# Spec draft — 013-003-redundancy-pilot

**Estado:** pendiente de aprobación.  
**Autoridad:** contrato de unidad del paquete `013-003-redundancy-pilot-architect-draft-001` y plan aprobado del epic 013.

## 1. Descripción funcional

Quien mantiene la suite recibe un lote pequeño con decisiones justificadas por la protección que aporta cada test respecto de los demás. Puede conservarlos o sustituir recorridos sin perder obligaciones vigentes.

El piloto examina el par B1 de `tests/test_005_013_t1_unit_projection.py`:

- **A:** `test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes`.
- **B:** `test_b1_collision_leaves_the_old_packet_valid_and_receivable`.

Se conserva como control vecino:

- **C:** `test_b1_no_collision_with_custom_out_dir_still_publishes`.

La elección aprovecha la semilla de 013-002 y un defecto contractual documentado. **No declara que A y B sean equivalentes ni obliga a consolidarlos.** Mantener ambos, con razones y evidencia contrastadas, constituye un resultado válido.

No se promete reducir tests, bytes ni tiempo.

## 2. Fuentes, producto y límites

### Fuentes admitidas

Repositorio autorizado por el paquete. Las referencias siguientes corresponden al snapshot indicado en el informe:

| Fuente | Función |
|---|---|
| `docs/epics/epic-013-test-criterion/plan.md`, Features y Contratos entre features | Alcance aprobado |
| `docs/specs/013-test-criterion-suite-review/discovery.md:99-110` | Candidato; diferencias conocidas; costes históricos, no ahorro |
| `docs/specs/013-001-criterion-coherence/spec.md`, PC-4–PC-7 | Disposiciones, conservación, POST-AUDIT y revisión |
| `docs/adr/ADR-041-evidencia-autorizada-y-criterio-de-contribucion.md`, decisiones 1 y 5 | Evidencia autorizada y sustitutos |
| `docs/specs/013-002-live-inventory/spec.md`, PC-5–PC-8 | Semilla, genealogía y mantenimiento |
| `docs/suite-maintenance.md:75-140,182-215` | Procedimiento y límites de validación |
| `docs/specs/005-013-unit-contract/spec.md`, PD-4–PD-6 e INV-3; `review.md`, B1 | Obligaciones del comportamiento vigente |
| `tests/test_005_013_t1_unit_projection.py:1117-1288` | Verificadores actuales |
| `pc-map.json:446-474`, bajo `docs/specs/008-002-suite-by-capability/` | Dos registros iniciales B1, ambos `VERIFY` |
| `tests/test_013_002_live_inventory.py:168-198` | Dependencia de aceptación que actualmente exige destinos de la semilla |

### Producto y responsables

- **Test-writer:** informe AUDIT y, si se aprueba mantenimiento, cambios exclusivamente en tests autorizados.
- **Orquestador:** materialización del informe y evidencias bajo `docs/specs/013-003-redundancy-pilot/`; deltas del inventario y mapa existentes.
- **Reviewer:** contraste independiente de decisiones y conservación.

El procedimiento de `docs/suite-maintenance.md` se aplica sin modificarlo por defecto.

Los cambios ordinarios de tests quedan acotados al par A/B. El control C permanece intacto. Si una sustitución requiere actualizar el verificador histórico de 013-002, ese cambio se identifica y aprueba expresamente en AUDIT.

### Entradas protegidas

No se modifican para obtener aceptación:

- Esta spec una vez aprobada y el contrato de unidad.
- Specs cerradas, especialmente 005-013, 008-002 y 008-006.
- Revisiones y evidencias anteriores usadas como referencia.
- Contratos y aserciones pertinentes durante los controles de sensibilidad.

Esta propuesta no concede permisos de escritura ni temporales: los despachos posteriores deben declararlos.

## 3. Contrato y postcondiciones

### Promesa A — Decidir con evidencia sobre un lote delimitado

**PC-1. Evaluación individual recuperable.**  
El AUDIT identifica la revisión inicial, los nodeids A/B y el control C. Para cada test registra una disposición única conforme a 013-001, su promesa, obligaciones, contribución respecto de los otros verificadores y evidencia utilizada.

La justificación distingue protección diferencial de riesgo genérico. Cuando no pueda resolver una diferencia relevante, registra **Mantener** e incertidumbre, sin afirmar suficiencia acreditada.

La presente spec no elimina obligaciones de 005-013; por tanto, no proporciona fundamento para **Retirar** sus verificadores.

**PC-2. Comparación de estados, acciones y comprobaciones.**  
El informe contrasta, como mínimo:

| Recorrido | Protección actual que debe examinarse |
|---|---|
| A, sin despacho previo | Rechazo de colisión; diagnóstico que nombra el paquete; conservación de proyección y `REQUEST.json` |
| B, con despacho previo | Conservación del pin; recepción posterior con validaciones `passed` y estado semántico `pending` |
| C, sin colisión | Publicación custom válida, ubicación canónica de la proyección y coherencia de sus pins |

Identifica las diferencias entre los estados iniciales y el efecto de completar/restaurar el binding en B. No las descarta como internas sin justificación contractual.

Una consolidación solo resulta admisible si la comparación permite localizar en el destino las comprobaciones conservadas y acreditar los recorridos relevantes. Compartir `rc`, preparación o cobertura no basta.

### Promesa B — Ejecutar únicamente mantenimiento acreditable

**PC-3. Resultado antes/después atribuible.**  
Se ejecutan A/B/C sobre la revisión inicial y los destinos finales más C sobre la revisión candidata. La evidencia conserva revisión, selección exacta, comando, configuración relevante, salida y código de retorno.

Si se decide Mantener, los tests correspondientes permanecen exactamente intactos; el resultado posterior acredita su conservación, no una poda inexistente.

Si aparece un fallo inicial, se declara y resuelve antes de atribuir un verde posterior a este mantenimiento.

**PC-4. Sustitución condicionada a destino y sensibilidad.**  
Los cambios aprobados sobre comportamiento vigente se ejecutan en **POST-AUDIT**, incluidos destinos físicamente nuevos. No se fuerza RED ni se despacha GREEN si no hay implementación pendiente.

Antes de eliminar un origen deben existir:

1. Destino ejecutable y verde.
2. Mapa de conservación de PC-2.
3. Sensibilidad demostrada frente a un defecto contractual concreto, conforme a 013-001 PC-6.

El control negativo ejecuta el verificador candidato y produce un fallo pertinente atribuible al defecto. No cuentan errores de preparación/importación, aserciones falseadas ni controles ajenos al recorrido.

Si no puede acreditarse dentro del alcance autorizado, se conservan los originales y se registra el motivo. No se acepta la sustitución.

**PC-5. Experimento de mutación acotado y honesto.**  
El informe registra una evaluación de viabilidad y su resultado: realizado, no viable o inconcluso, con fundamento.

Si resulta viable, la propuesta inicial limita el experimento a **dos defectos contractuales**, aplicados separadamente:

- Sobrescritura de una proyección publicada al colisionar.
- Pérdida de receivabilidad del paquete íntegro después de la colisión.

Antes de ejecutarlo se declaran operador, ubicación, selección, presupuesto finito y mecanismo que permite comprobar que el defecto alcanza el CLI ejecutado por los tests. No se exige herramienta nueva ni porcentaje de mutantes eliminados.

Cada resultado registra defecto aplicado, verificador ejecutado, fallo observado y límites. Un mutante que no alcance el subproceso no acredita sensibilidad.

La mutación de implementación, si fuera necesaria, requiere un encargo separado con alcance apropiado sobre una copia declarada; no autoriza al test-writer a leer o modificar implementación. Un control negativo válido puede aportar la sensibilidad sin usar mutación de implementación.

### Promesa C — Conservar obligaciones y genealogía

**PC-6. Mapa completo del lote y deltas reproducibles.**  
El informe relaciona contrato, identificador y variante con origen, destino actual y ubicación de las comprobaciones. Examina también INV-3 y PD-4 en B, cuya semilla actual solo identifica PD-6.

Para cada cambio entrega el delta documental conforme a `suite-maintenance.md`:

- Conserva orígenes históricos y pasos de sustitución.
- Mantiene `target_nodeid` como cadena; varios destinos se desglosan.
- Identifica el piloto 013-003 sin borrar la procedencia 013-002.
- Distingue disposición del AUDIT de `decision` legacy.
- No cambia `VERIFY` por acreditación antes del contraste pertinente.
- Conserva los registros y deudas ajenos al lote.

Si no cambian asignaciones del inventario, se entrega un delta explícitamente vacío con su razón; no se inventan modificaciones para satisfacer una cuota.

El test-writer entrega los deltas como texto. El orquestador los materializa al re-entry antes de la siguiente transición.

**PC-7. Integridad y dependencias de aceptación conservadas.**  
Antes de entrar a Review y al cierre:

```sh
python3 scripts/cdad-suite.py validate
```

termina con **rc=0** sobre la revisión que contiene los últimos tests y deltas materializados.

La comparación de conservación usa una revisión anterior que contiene la semilla B1; el snapshot inicial indicado es una referencia disponible.

Si cambian destinos, AUDIT incluye el verificador `test_013_002_C_mapa_inicial_B1_identificado_por_entrada`: actualmente exige que pertenezcan a A/B. Su mantenimiento conserva la obligación histórica —destino actual antes de sustitución acreditada— y permite comprobar la genealogía posterior acreditada. No se elimina la comprobación para obtener verde ni se reescribe la spec cerrada de 013-002.

Si ambos tests se mantienen y no cambia esa expectativa, el verificador permanece intacto.

### Promesa D — Entregar una conclusión contrastada y limitada

**PC-8. Revisión y cierre sin extrapolación.**  
La revisión independiente contrasta:

- Disposiciones y contribución diferencial.
- Estados y obligaciones anteriores frente a destinos actuales.
- Evidencia verde y sensibilidad cuando exista sustitución.
- Mapa anterior, deltas y materialización final.
- Cualquier mantenimiento del verificador histórico de 013-002.

Registra fuentes, hallazgos, incertidumbres y abstenciones. La aceptación no equipara `validate rc=0` con equivalencia semántica.

El cierre separa:

1. Control estructural.
2. Ejecución focal.
3. Revisión semántica del lote.
4. Resultado y límites del experimento.
5. **Suite completa no realizada**.

No declara acreditación global, ahorro temporal ni mejora de rendimiento sin evidencia específica.

## 4. Invariantes verificables

1. Ninguna obligación vigente de un origen eliminado queda sin destino acreditado.
2. Ninguna incertidumbre relevante se resuelve eliminando el test.
3. El control C permanece intacto y conserva evidencia de ejecución.
4. El test-writer no modifica inventario/mapa ni deriva oráculos leyendo implementación.
5. El orquestador materializa deltas; no altera los oráculos para conseguir aceptación.
6. No se modifican contratos cerrados ni se borran antecedentes para obtener verde.
7. No se ejecuta la suite completa, el gate completo de CI ni una selección completa producida por `surface`.
8. Los resultados corresponden a revisiones y selecciones identificables.

## 5. Verificación y aceptación

### Selección inicial propuesta

```sh
python3 -m pytest -q -p no:cacheprovider \
  tests/test_005_013_t1_unit_projection.py::test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes \
  tests/test_005_013_t1_unit_projection.py::test_b1_collision_leaves_the_old_packet_valid_and_receivable \
  tests/test_005_013_t1_unit_projection.py::test_b1_no_collision_with_custom_out_dir_still_publishes
```

La selección final sustituye los orígenes solo cuando corresponda y añade los verificadores históricos efectivamente afectados. Los despachos declaran los espacios temporales y la configuración de ejecución.

Si cambian helpers compartidos de T1, se justifica regresión focal de sus consumidores; T2 importa `Fixture` y otros símbolos de T1 (`tests/test_005_013_t2_change_classification.py:105-123`). No se amplía esa superficie por conveniencia.

La aceptación exige:

- Evidencia pertinente de PC-1–PC-8.
- Ninguna sustitución pendiente de acreditar.
- Integridad estructural sobre las revisiones pertinentes.
- Revisión independiente y aprobación del dueño.

Mantener todo el lote puede satisfacer la aceptación, pero **no basta anunciar que se mantiene**: deben existir comparación, decisiones, ejecución y revisión.

## 6. Decisiones de diseño

- **Semilla B1 frente a otro lote:** ya dispone de referencias y diferencias concretas; minimiza exploración y evita ampliar el piloto.
- **Conservar el criterio general frente a imponer una fusión:** se aplican 013-001 y 013-002; la evidencia determina el resultado.
- **POST-AUDIT frente a RED artificial:** se mantiene comportamiento vigente, no se inventa implementación pendiente.
- **Control acotado frente a infraestructura universal de mutación:** importa detectar un defecto pertinente; una campaña o plataforma nueva no aporta valor necesario al MVP.
- **Actualizar el verificador histórico frente a congelar destinos:** permite mantener datos vivos sin perder la obligación histórica ni cambiar contratos cerrados.

## 7. VERIFY y dependencias de ejecución

| Pendiente | Efecto y condición de resolución |
|---|---|
| Consolidabilidad de A/B | Bloquea su sustitución, no el resultado Mantener. Se resuelve mediante AUDIT, evidencia y revisión independiente. |
| Sensibilidad y alcance del control negativo | Bloquea eliminar originales. Requiere control autorizado y fallo pertinente observado. |
| Viabilidad de mutación sobre el CLI real | Se informa con evidencia; no se presume. Su inviabilidad no permite omitir sensibilidad si se pretende sustituir. |
| Mantenimiento del verificador de 013-002 | Condicional a cambios de destino; debe figurar en AUDIT aprobado antes de editarlo. |
| Estado inicial de ejecución e integridad | Debe medirse en la ejecución del piloto; aquí no se presenta el cierre histórico de 013-002 como una corrida actual. |

Las deudas históricas ajenas al lote permanecen visibles y no bloquean por sí mismas este piloto.

## 8. deferred-hardening

- **Auditoría semántica global:** excluida por el epic; el compromiso es el lote B1.
- **Más candidatos de poda:** ampliar el lote no es necesario para demostrar el procedimiento.
- **Campaña universal de mutación o umbral de puntuación:** no acredita conservación y excede el experimento.
- **Rendimiento, paralelismo y optimización de fixtures:** pertenecen a una decisión posterior sobre 013-004.
- **Rediseño del selector o verificador de genealogía:** se utilizan los mecanismos existentes más contraste independiente.
- **Resolución de deudas históricas ajenas al piloto:** no es necesaria para sus promesas.
- **Suite completa y despliegue:** fuera de este encargo.

Ningún diferimiento aplaza una postcondición comprometida.
