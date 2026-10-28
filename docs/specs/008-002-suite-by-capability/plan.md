# Plan — Suite por capacidad y contrato

## Steps

- [ ] Fijar baseline e inventario exhaustivo de capacidades y contratos.
- [ ] Construir mapa acreditado PC→test antes/después y delimitar el piloto.
- [ ] Implementar por TDD la CLI y el gate sensible a cambios sólo de tests.
- [ ] Consolidar el piloto preservando variantes e imports.
- [ ] Preservar intentos del gate y documentar la deuda temporal.
- [ ] Revisar, medir y cerrar con evidencia reproducible.

## 1. Baseline e inventario

Registrar revisión y árbol; guardar manifest y medición inicial con el algoritmo de la spec.

Recolectar pytest sin ejecutar la suite. Inventariar todos los módulos, diferenciando infraestructura de cobertura. Clasificar módulos mixtos por nodeid.

No introducir una taxonomía derivada sólo de prefijos históricos.

**Salida:** inventario completo y baseline reproducible.

## 2. Mapa y piloto

Vincular obligaciones acreditadas con specs, enmiendas, reviews y cierres. Registrar variantes y genealogía.

Auditar exclusivamente para consolidación los tres módulos 005-010 identificados en la spec. Mantener otros módulos, aunque el inventario registre oportunidades futuras.

Antes de retirar cada caso, identificar sustituto y control dirigido que demuestre su sensibilidad. Si la evidencia no alcanza, mantenerlo.

**Salida:** mapa base y delta propuesto revisable, sin eliminación anticipada.

## 3. CLI y superficie

Test-writer aislado escribe controles observables para PC-1, PC-2, PC-3 y PC-5; implementer implementa sólo el producto autorizado.

Usar repositorios sintéticos para probar cambios comprometidos, sin commit, sólo de tests y helpers. Evitar depender del estado del checkout del operador.

Conectar el mecanismo local al gate versionado sin mantener dos selectores independientes.

**Salida:** selector usable por capacidad y gate que no acepta una reorganización invisible.

## 4. Consolidación

Las modificaciones de tests corresponden al rol autorizado a editar tests, no al implementer.

Consolidar preparación o casos equivalentes únicamente dentro del piloto. Preservar diferencias de store, texto final y último assistant. No trasladar imports de clases recolectables como estrategia de reutilización.

Validar colección, consumidores de helpers, controles dirigidos y subconjunto afectado después de cada cambio.

**Salida:** reducción demostrable **del piloto** y mapa actualizado sin pérdida de variantes.

## 5. Evidencia y deuda

Implementar reserva exclusiva de directorios de intento y metadatos de cierre. Probar preservación por hashes usando ejecuciones sintéticas pequeñas.

Mantener canario y motivos de skips. Declarar interrupciones honestamente.

Registrar los cuatro casos temporales y re-declarar la deuda de 2s sin cambiar silenciosamente el contrato del producto.

**Salida:** evidencia no sobrescribible y deuda delimitada.

## 6. Review y cierre

Reviewer independiente contrasta inventario, mapa, controles de equivalencia, selector y medición.

Actualizar informe con el mismo algoritmo e incluir archivos nuevos en el denominador. Una reducción que sólo mueve líneas fuera del denominador no satisface PC-4.

Ejecutar selección afectada y:

```text
python3 scripts/cdad_packet.py validate-state --project-root .
```

El closer ejecuta el gate final **únicamente** mediante `python3 scripts/cdad-suite.py close --evidence-root <directorio>` y conserva todos los intentos. No publicar ni desplegar automáticamente.

**Salida:** informe antes/después, review y cierre; cualquier cobertura sin resolver permanece bloqueante.

## Tareas del plan

```plan-tasks
{
  "validation_strategy": "Regresiones focales por lote; suite completa exclusivamente por el closer mediante close, conforme a la política del paquete.",
  "tasks": [
    {
      "id": "T1",
      "owner": "test-writer: inventario y baseline; reviewer: contraste independiente",
      "files": [
        "docs/specs/008-002-suite-by-capability/suite-inventory.json",
        "docs/specs/008-002-suite-by-capability/measurement-before.json"
      ],
      "focal_tests": [],
      "depends_on": [],
      "observable_checks": [
        "PC-1: todos los módulos Python versionados bajo tests están inventariados y la colección tiene capacidad y contrato",
        "PC-4/PC-8: baseline identifica revisión, árbol, método, universo y conjunto piloto"
      ],
      "regressions": [],
      "integration_gate": "Revisión independiente del inventario y baseline",
      "produce": [{"artifact": "suite-baseline", "contract": "suite-baseline-v1"}],
      "consume": [],
      "parallel": []
    },
    {
      "id": "T2",
      "owner": "test-writer: mapa y controles; reviewer: equivalencias",
      "files": [
        "docs/specs/008-002-suite-by-capability/pc-map.json",
        "docs/specs/008-002-suite-by-capability/variant-controls.json",
        "tests/test_008_002_variant_controls.py"
      ],
      "focal_tests": ["tests/test_008_002_variant_controls.py"],
      "depends_on": ["T1"],
      "observable_checks": [
        "PC-3: cada variante candidata a retirada tiene fuente contractual, sustituto, control negativo y comando",
        "Toda equivalencia no demostrada conserva el caso original"
      ],
      "regressions": [
        "tests/test_005_010_t1_durable_signal.py",
        "tests/test_005_010_reviewfix.py",
        "tests/test_005_010_b1_last_assistant.py"
      ],
      "integration_gate": "Mapa y controles revisados antes de eliminar casos",
      "produce": [{"artifact": "pilot-obligations", "contract": "pilot-obligations-v1"}],
      "consume": [{"artifact": "suite-baseline", "producer": "T1", "contract": "suite-baseline-v1"}],
      "parallel": []
    },
    {
      "id": "T3",
      "owner": "RED: test-writer; GREEN: implementer",
      "files": [
        "scripts/cdad-suite.py",
        "tests/test_008_002_suite_selection.py",
        "docs/specs/008-002-suite-by-capability/timing-disposition.json"
      ],
      "focal_tests": ["tests/test_008_002_suite_selection.py"],
      "depends_on": ["T2"],
      "observable_checks": [
        "PC-1/PC-2: inventario validado y selección exacta ejecutable",
        "PC-3: controles estructurales rechazan destinos ausentes, obligaciones desaparecidas y VERIFY antes de eliminar",
        "PC-5: cambios sólo de tests y base sin inventario fallan o seleccionan según contrato",
        "PC-7: validate rechaza disposición temporal ausente o resolución sin evidencia"
      ],
      "regressions": ["tests/test_008_001_home_xdg_isolation.py"],
      "integration_gate": "@validation_strategy",
      "produce": [{"artifact": "canonical-selector", "contract": "suite-selector-v1"}],
      "consume": [{"artifact": "pilot-obligations", "producer": "T2", "contract": "pilot-obligations-v1"}],
      "parallel": []
    },
    {
      "id": "T4",
      "owner": "test-writer: consolidación y controles; reviewer: conservación",
      "files": [
        "tests/test_005_010_t1_durable_signal.py",
        "tests/test_005_010_reviewfix.py",
        "tests/test_005_010_b1_last_assistant.py",
        "tests/suite_signal_helpers.py",
        "tests/test_008_002_variant_controls.py",
        "docs/specs/008-002-suite-by-capability/suite-inventory.json",
        "docs/specs/008-002-suite-by-capability/pc-map.json",
        "docs/specs/008-002-suite-by-capability/variant-controls.json"
      ],
      "focal_tests": [
        "tests/test_008_002_variant_controls.py",
        "tests/test_005_010_t1_durable_signal.py",
        "tests/test_005_010_reviewfix.py",
        "tests/test_005_010_b1_last_assistant.py"
      ],
      "depends_on": ["T3"],
      "observable_checks": [
        "PC-3/PC-4: variantes preservadas y reducción del piloto sin excluir helpers ni controles añadidos",
        "PC-8: colección e imports válidos; aislamiento y consumidores afectados permanecen verdes"
      ],
      "regressions": [
        "tests/test_005_009_t2_opencode_adapter.py",
        "tests/test_005_010_t2_load_mode_invocation.py",
        "tests/test_005_010_t4_integration.py",
        "tests/test_008_001_home_xdg_isolation.py",
        "tests/test_008_001_pc7_wrapper_margin.py",
        "tests/test_008_001_pc8_adapter_budget.py"
      ],
      "integration_gate": "@validation_strategy",
      "produce": [{"artifact": "consolidated-pilot", "contract": "preserved-pilot-v1"}],
      "consume": [{"artifact": "canonical-selector", "producer": "T3", "contract": "suite-selector-v1"}],
      "parallel": []
    },
    {
      "id": "T5",
      "owner": "RED: test-writer; GREEN: implementer",
      "files": [
        "scripts/cdad-suite.py",
        "tests/test_008_002_suite_evidence.py"
      ],
      "focal_tests": ["tests/test_008_002_suite_evidence.py"],
      "depends_on": ["T4"],
      "observable_checks": [
        "PC-6: reservas secuenciales y concurrentes exclusivas, sin reuso ni sobrescritura",
        "PC-8: measure informa sin escribir; close preserva canario, skips e intentos"
      ],
      "regressions": [
        "tests/test_008_002_suite_selection.py",
        "tests/test_008_001_home_xdg_isolation.py"
      ],
      "integration_gate": "@validation_strategy",
      "produce": [{"artifact": "canonical-close", "contract": "suite-close-v1"}],
      "consume": [{"artifact": "canonical-selector", "producer": "T3", "contract": "suite-selector-v1"}],
      "parallel": []
    },
    {
      "id": "T6",
      "owner": "reviewer: contraste; closer: medición y cierre",
      "files": [
        "docs/specs/008-002-suite-by-capability/measurement-after.json",
        "docs/specs/008-002-suite-by-capability/suite-report.md",
        "docs/specs/008-002-suite-by-capability/closure.md"
      ],
      "focal_tests": [],
      "depends_on": ["T5"],
      "observable_checks": [
        "PC-1..PC-8: evidencia y controles revisados independientemente",
        "PC-4: bytes y líneas LF del piloto disminuyen con idéntico método; delta global sólo informativo",
        "PC-7: deuda temporal explícita sin atribuir cumplimiento de 2s",
        "PC-8: validate-state satisfactorio y gate final ejecutado únicamente mediante close"
      ],
      "regressions": ["@validation_strategy"],
      "integration_gate": "Review independiente y cierre conforme al paquete; sin publicación automática",
      "produce": [{"artifact": "suite-handoff", "contract": "canonical-suite-gate-v1"}],
      "consume": [
        {"artifact": "consolidated-pilot", "producer": "T4", "contract": "preserved-pilot-v1"},
        {"artifact": "canonical-close", "producer": "T5", "contract": "suite-close-v1"}
      ],
      "parallel": []
    }
  ]
}
```

`tests/suite_signal_helpers.py` sólo se crea si la extracción resulta necesaria y segura; no autoriza ampliar el piloto. El gate final debe incluir todas las regresiones de PC-8 y los consumidores adicionales acreditados por el inventario.
