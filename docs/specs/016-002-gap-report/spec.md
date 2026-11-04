---
feature_id: 016-002-gap-report
approved_by: Pablo (HITL delegada al orquestador, docs/epics/epic-016-traceability-and-suite-review/execution.md)
approved_at: 2026-11-03
source: architect draft (sesión <ses-347>), materializado por el orquestador (ADR-003)
decision: se aprueban el subcomando gap-report, el universo tomado del estado con cierre registrado, las exclusiones justificadas como priorización (no verificadores) y el informe JSON reproducible por stdout
---

# Spec: 016-002-gap-report

**Estado: aprobada** (2026-11-03, HITL delegada al orquestador; ver encabezado). Las interfaces y campos nuevos descritos a continuación son propuestas, no capacidades existentes.

## 1. Descripción funcional

**Actor:** dueño del proyecto o responsable de revisar la suite.

**Objetivo:** identificar qué compromisos de contratos cerrados necesitan revisión, distinguiendo falta de verificador, falta de índice y exclusiones justificadas.

**Punto de partida:** estado CDAD con cierres registrados y registros de vínculos incorporados por demanda.

**Primer resultado útil:** un informe reproducible que permite elegir el siguiente tramo de revisión sin presentar desconocimiento como cobertura ni como hueco.

El informe comprueba estructura y referencias. No ejecuta tests ni afirma pertinencia semántica, sensibilidad o aceptación del contrato.

## 2. Interfaz propuesta

```sh
python3 <cdad-cycle>/scripts/cdad_contract_links.py gap-report \
  --project-root ROOT \
  --state STATE.json \
  [--registry UNIT=REGISTRY.json ...] \
  [--collection CURRENT.json] \
  [--exclusions EXCLUSIONS.json]
```

- Las rutas relativas se interpretan respecto de `ROOT`.
- Las referencias deben permanecer dentro del proyecto después de resolver symlinks.
- Los registros se entregan explícitamente: no se descubren recorriendo las specs.
- `CURRENT.json` conserva el formato de colección de 016-001. Se requiere cuando se procesa al menos un registro existente, sin ejecutar automáticamente el runner.
- No se recibe baseline: este informe no comprueba altas de tests.
- La CLI produce JSON por stdout y no modifica archivos.

**Códigos propuestos:**

| Código | Significado |
|---|---|
| `0` | Informe producido con entradas válidas; puede contener huecos, exclusiones o contratos no indexados. |
| `1` | Datos presentes inválidos o referencias rotas; resultado explícitamente incompleto. |
| `2` | Uso inválido de la CLI. |

Esto no cambia los códigos ni el comportamiento de `validate`. Un informe producido correctamente no significa «contratos protegidos».

## 3. Universo de contratos

La fuente es el archivo de estado indicado por `--state`.

Se consideran las filas de:

- `epic_features[]`;
- `epic_history[].epic_features[]`.

Para cada identidad de unidad, la fila actual tiene precedencia sobre sus copias históricas. Sin fila actual, las copias históricas equivalentes se deduplican; cierres incompatibles se informan como ambigüedad, sin elegir uno arbitrariamente.

Una unidad entra al universo cuando:

1. su estado es `done`;
2. tiene `closure_evidence.path` y `closure_evidence.sha256`;
3. el documento de cierre resuelve y coincide con ese hash;
4. existe `docs/specs/<unit-id>/spec.md`.

No se infiere un cierre por el nombre de un archivo, por texto libre ni por el cierre del epic.

- Una fila `done` sin evidencia de cierre aparece separadamente como **cierre no registrado**; no entra como cubierta ni como hueco.
- Una evidencia declarada pero rota produce error, no una omisión silenciosa.
- Las demás filas quedan fuera del universo, con su estado recuperable.
- Un estado existente ilegible o corrupto es inválido.
- Un estado válido sin cierres produce un universo vacío explícito.

El informe identifica el hash actual de cada spec examinada. No afirma que esos bytes sean los del momento del cierre salvo que una referencia admitida los vincule; un registro presente exige siempre el hash de contrato de 016-001.

**Límite del universo:** cubre los cierres registrados en las estructuras indicadas, no todos los documentos históricos del repositorio.

## 4. Obligaciones y clasificación

### Obtención de obligaciones

- **Con marcadores reales:** se usa el universo mecánico definido por 016-001, incluidos sus criterios para distinguir marcadores de ejemplos.
- **Sin marcadores:** se usa únicamente `legacy_obligations` de un registro explícito válido.
- **Sin marcadores ni índice declarado:** la spec aparece como `not_indexed`; no se inventan promesas ni huecos.
- **Registro presente sin obligaciones:** sigue siendo inválido, conforme a 016-001.
- No se mezclan marcadores e índice legacy.

Un contrato con marcadores y sin registro tiene obligaciones conocidas y ningún verificador declarado: sus obligaciones aparecen como huecos. La falta de registro se declara separadamente.

### Resultado por obligación y promesa

Cada obligación indexada identifica unidad, contrato y hash, ID, promesa y verificadores admitidos.

Sus disposiciones son:

- `declared`: tiene al menos un verificador estructuralmente válido;
- `gap`: no tiene verificador y no está excluida;
- `excluded`: pertenece a una promesa excluida válidamente.

`declared` no significa ejecutada ni semánticamente protegida.

Una promesa se informa como hueco cuando tiene al menos una obligación `gap`; el informe enumera cuáles. No basta con vincular una de sus obligaciones para presentar el grupo entero como atendido.

Los registros inválidos se muestran como tales. No se usan para acreditar verificadores ni se presentan sus resultados como una clasificación definitiva y válida de la unidad.

La cobertura legacy siempre dice **«obligaciones indexadas; no extracción exhaustiva del contrato»**.

## 5. Exclusiones justificadas

Archivo opcional propuesto:

```json
{
  "schema_version": 1,
  "exclusions": [
    {
      "unit": "example-unit",
      "contract": {
        "path": "docs/specs/example-unit/spec.md",
        "sha256": "<hash>"
      },
      "promise": "A",
      "reason": "Motivo explícito de excluir esta promesa del listado accionable."
    }
  ]
}
```

Reglas:

- La exclusión afecta al grupo observable completo identificado por `promise`.
- La unidad y la promesa deben pertenecer al universo indexado del informe.
- El contrato debe coincidir por ruta y hash.
- `reason` debe contener texto no vacío después de quitar espacios.
- No se admiten varias exclusiones para la misma unidad y promesa.
- El resultado conserva motivo, archivo de origen, hash y localizador de la entrada.
- Una exclusión inválida produce error y no retira el hueco subyacente.
- Una exclusión nunca crea un verificador ni incrementa un contador de protección.
- Las exclusiones se muestran en sección propia; no desaparecen del informe.

El orquestador materializa el archivo de exclusiones conforme a la decisión autorizada. GREEN no modifica estos insumos para obtener un resultado favorable.

## 6. Forma y reproducibilidad del informe

El JSON contiene, como mínimo:

- versión del formato;
- estado de producción del informe;
- entradas efectivamente usadas, con rutas y hashes;
- universo admitido y alcance de su obtención;
- cierres no registrados y unidades fuera del universo;
- unidades inválidas y sus diagnósticos;
- modo de indexación y límite de cobertura por contrato;
- obligaciones y verificadores declarados;
- huecos agrupados por unidad y promesa;
- specs no indexadas;
- exclusiones con motivo recuperable;
- límites del resultado.

Orden estable:

1. unidades por ID;
2. promesas por identificador;
3. obligaciones por ID;
4. verificadores por representación canónica;
5. diagnósticos por ubicación y código.

No incorpora hora actual, rutas absolutas del host ni identificadores aleatorios. Con los mismos bytes de entrada y argumentos, produce los mismos bytes de salida. Reordenar bindings de registros no altera el resultado.

**Materialización:** stdout es el producto ordinario. Si se necesita una fotografía versionada, el orquestador conserva salida, comando y revisión en la documentación de la unidad o del tramo. La CLI no escribe ese archivo ni exige mantenerlo actualizado.

## 7. Promesas y postcondiciones

### A — Saber qué contratos se examinaron

<!-- cdad:pc PC-1 promise=A -->
**PC-1.** El informe obtiene el universo conforme a las reglas de cierre registrado, incluye las filas históricas aplicables y permite recuperar la evidencia de cierre de cada unidad admitida. Una fila actual no cerrada impide que una copia histórica la reincorpore silenciosamente.

<!-- cdad:pc PC-2 promise=A -->
**PC-2.** Un cierre no registrado se distingue de una evidencia declarada rota. El primero queda fuera del universo con diagnóstico; la segunda produce `1`, identifica la referencia afectada y no permite presentar el informe como completo.

### B — Distinguir huecos de desconocimiento

<!-- cdad:pc PC-3 promise=B -->
**PC-3.** El informe obtiene obligaciones de marcadores reales o del índice legacy admitido, sin mezclarlos. Una spec sin ambos aparece como no indexada, nunca como cubierta ni como hueco; un registro presente sin obligaciones sigue siendo inválido.

<!-- cdad:pc PC-4 promise=B -->
**PC-4.** Para cada universo válido, quitar el último verificador de una obligación produce un hueco recuperable y lo agrupa bajo su promesa. Compartir un verificador entre obligaciones no exige tests adicionales. Un `review` válido cuenta como verificador declarado sin convertirse en ejecución de test.

### C — Apartar una promesa sin ocultar la decisión

<!-- cdad:pc PC-5 promise=C -->
**PC-5.** Una exclusión válida mueve la promesa y sus obligaciones a la sección de excluidas, conserva su motivo recuperable y no las presenta como protegidas.

<!-- cdad:pc PC-6 promise=C -->
**PC-6.** Una exclusión sin motivo válido, con identidad ambigua o con referencias que no corresponden al contrato y promesa produce `1`; no suprime el hueco que habría sin ella.

### D — Repetir y auditar el resultado

<!-- cdad:pc PC-7 promise=D -->
**PC-7.** El comando emite el informe con entradas identificadas por hash, orden estable y las distinciones comprometidas. Repetirlo con entradas idénticas produce salida idéntica; reordenar bindings de registros no cambia el resultado.

<!-- cdad:pc PC-8 promise=D -->
**PC-8.** Producir el informe no modifica sus entradas, no ejecuta tests y respeta los códigos definidos. Los defectos de registros o colecciones se identifican sin acreditarlos como verificadores válidos. El comportamiento existente de `validate` permanece compatible.

### E — Adoptarlo sin imponer una migración

<!-- cdad:pc PC-9 promise=E -->
**PC-9.** Un proyecto sin registros puede producir el informe sin colección: declara «sin registro de vínculos declarado», muestra lo no indexado y, cuando existen marcadores, sus huecos conocidos. No exige inventario vivo, `pc-map` ni backfill; el ciclo normal no adquiere un gate por esta feature.

<!-- cdad:pc PC-10 promise=E -->
**PC-10.** El informe y su referencia operativa declaran que la comprobación es estructural, distinguen cobertura legacy de universo de marcadores y no afirman ejecución, pertinencia semántica, sensibilidad ni aprobación. La documentación identifica al orquestador como materializador de exclusiones y fotografías opcionales.

## 8. Invariantes verificables

- Una unidad no aparece simultáneamente como no indexada y como cubierta o hueco.
- Ninguna exclusión añade verificadores.
- Toda obligación indexada válida tiene exactamente una disposición.
- Toda obligación sin verificador y sin exclusión válida es un hueco.
- Una referencia inválida nunca mejora la acreditación estructural.
- Inventario, genealogía y registros permanecen separados.
- La comprobación no modifica las fuentes examinadas.

## 9. Alcance y responsabilidades

**Producto bajo `skills/`:**

- subcomando propuesto `gap-report`;
- referencia canónica de entradas, salida, exclusiones, códigos y límites, ampliando `contract-test-links.md`;
- punteros operativos necesarios, sin copiar el formato ni crear gates.

**Verificadores bajo `tests/`:**

- pruebas observables de PC-1..PC-10;
- fixtures autocontenidas de estado, contratos, registros, colecciones y exclusiones.

El test-writer propone como texto los deltas de vínculos de esta unidad; el orquestador los materializa. GREEN no modifica contrato, registros documentales, exclusiones operativas ni verificadores.

Las fuentes protegidas son el contrato aprobado y los insumos de aceptación. El informe no utiliza inventario o genealogía como oráculo de cobertura.

## 10. Criterios de aceptación

- Desde cierres registrados se obtiene un informe que diferencia inequívocamente huecos, no indexados y excluidos.
- Cada hueco y exclusión permite recuperar contrato, obligación y promesa; la exclusión conserva su motivo.
- Una referencia rota produce un diagnóstico atribuible, no un informe aparentemente completo.
- La repetición sobre las mismas entradas es byte a byte reproducible.
- La ausencia de registros o inventario no impide continuar el ciclo normal.
- Los verificadores de esta feature quedan vinculados conforme a 016-001.
- Una revisión independiente contrasta el resultado y la documentación con el contrato antes de su aceptación.

## 11. deferred-hardening

- **Extracción exhaustiva del Markdown histórico:** se conserva el índice por demanda; se reconsiderará si un tramo demuestra necesidad de otra estrategia.
- **Descubrimiento de cierres fuera de las estructuras declaradas:** evita inferencias desde prosa y archivos sueltos; requiere ampliar explícitamente el contrato de fuentes.
- **Autenticación de colecciones y autoridad de las decisiones:** se comprueban artefactos y referencias, no su autoría criptográfica.
- **Inferencia de pertinencia, sensibilidad o suficiencia:** corresponde a revisión independiente y evidencia específica.
- **Optimización sobre todo el corpus:** no hay compromiso de rendimiento global; el primer tramo medirá el costo.
- **Comparación histórica automática de informes:** se entregan fotografías reproducibles, no un sistema de seguimiento temporal.

## 12. Fuera de alcance

Backfill masivo; reescritura de specs cerradas; revisión del primer tramo; poda de tests; nuevos gates; publicación y despliegue.

