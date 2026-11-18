# Plan — 019-007-suite-selector-maintenance

Status: Approved by CDAD orchestrator under Pablo's renewed HITL delegation for epic 019 on 2026-11-17.

Architect draft received 2026-11-17 (packet
019-007-suite-selector-maintenance-architect-draft-003, which adds the mandatory
plan-tasks block to the prior draft), materialized by the orchestrator without
altering its text (ADR-003). It remains unapproved until the independent draft
review and the owner decision are recorded.

### Plan propuesto — 019-007

**Estado:** borrador no aprobado, consistente con la especificación materializada.

#### Tarea única: corregir ambos selectores y verificar sus consumidores

**Archivos:**
- `tests/test_install_ownership.py`
- `tests/test_install_review5_regressions.py`
- `tests/test_004_001_t6.py`, únicamente si necesita adaptar el consumidor importado.

**Trabajo:**
Resolver el archivo instalado mediante la relación exacta `source → destino` de `.cdad-install-manifest.json`, comprobar su existencia y fallar explícitamente ante selección ausente o ambigua. Adaptar los consumidores necesarios, sin selección silenciosa por basename ni dependencia del orden del filesystem.

Conservar todas las aserciones funcionales, incluida la mutación de staging, actualización del hash, inaccesibilidad de `sources/`, instalación satisfactoria y comparación exacta de bytes.

Se prefiere la identidad publicada por el manifiesto frente a ordenar `rglob` o fijar una ruta de runtime: evita duplicar el layout y resuelve también los nombres homónimos sin introducir infraestructura nueva.

**Aceptación — PC-1–4 de la especificación:**
- Evidencia ejecutable de selección por origen con variantes homónimas de bytes distintos y rechazo de selección no resoluble.
- Revisión independiente que confirme preservación de aserciones y alcance exclusivamente de tests.
- Ejecutar satisfactoriamente, en este orden:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_install_ownership.py::TestT5StagingIsSourceOfTruth

PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_install_ownership.py tests/test_install_review5_regressions.py tests/test_004_001_t6.py

CDAD_TEST_TMP_BASE=/var/tmp/cdad-suite-epic2 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests
```

La suite final debe ejecutarse sin trabajo concurrente y alimentar el cierre del epic.

**Evidencia exigida:** snapshot/commit probado, diff, revisión independiente, comandos exactos, salidas completas, códigos de salida y skips justificados. Método combinado; ninguna ejecución aislada ni revisión demuestra ausencia universal de regresiones.

**Rondas:** máximo **2**, provisional, independiente para draft, audit y result; especificación y plan comparten la asignación draft. Justificación: cambio localizado, pero dos helpers y un consumidor entre módulos pueden generar falsos verdes si se pierde la identidad del origen.

**Deferred-hardening:** no unificar todos los helpers ni endurecer exhaustivamente manifiestos maliciosos; no son necesarios para esta corrección. Ninguna postcondición comprometida queda diferida.

**Pendiente bloqueante para ejecución:** revisión independiente y aprobación de especificación y plan; no se presumen concedidas.

```plan-tasks
{
  "validation_strategy": "Método combinado sobre PC-1–PC-4 de docs/specs/019-007-suite-selector-maintenance/spec.md: demostrar ejecutablemente la selección por source exacto, existencia del destino, distinción de variantes homónimas de bytes distintos y fallo explícito ante selección ausente o ambigua; revisar independientemente ambos helpers, sus consumidores, la preservación de todas las aserciones funcionales y el alcance exclusivo de tests. Ejecutar las regresiones declaradas en el orden indicado; la suite final debe correr sin trabajo concurrente y alimentar el cierre del epic. Conservar snapshot/commit probado, diff, revisión independiente, comandos exactos, salidas completas, códigos de salida y skips justificados. Una ejecución fallida o incompleta no acredita suite verde; tests y revisión no demuestran ausencia universal de regresiones. La ejecución requiere previamente revisión independiente y aprobación de especificación y plan.",
  "tasks": [
    {
      "id": "T1",
      "objective": "Corregir ambos selectores de artefactos instalados y sus consumidores necesarios, manteniendo íntegra la promesa de staging como fuente de verdad y sin modificar el producto.",
      "produce": [
        {
          "artifact": "selectores-y-consumidores-de-tests-corregidos",
          "contract": "PC-1–PC-4 de docs/specs/019-007-suite-selector-maintenance/spec.md"
        }
      ],
      "consume": [],
      "depends_on": [],
      "parallel": [],
      "detail": "next",
      "observable_checks": [
        "PC-1: al comparar bytes de un origen de staging, el destino proviene de una entrada de .cdad-install-manifest.json cuyo source coincide exactamente con ese origen y se comprueba que el archivo existe; variantes homónimas de bytes distintos no se intercambian por el orden del filesystem.",
        "PC-2: ambos helpers y sus consumidores necesarios usan destinos registrados; una selección ausente o todavía ambigua falla explícitamente, sin alternativa silenciosa por basename.",
        "PC-3: test_t5_case8_install_deploys_staging_bytes_without_sources conserva la mutación de staging, la actualización del hash, sources/ inaccesible, instalación satisfactoria y comparación exacta con los bytes mutados; la revisión independiente confirma que se conservan las restantes aserciones funcionales.",
        "PC-4: la revisión independiente confirma que el diff funcional queda limitado a tests/test_install_ownership.py, tests/test_install_review5_regressions.py y, solo si resulta necesario adaptar el consumidor importado, tests/test_004_001_t6.py; no cambia el comportamiento ni los artefactos del producto."
      ],
      "regressions": [
        "Primero: PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_install_ownership.py::TestT5StagingIsSourceOfTruth",
        "Después: PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_install_ownership.py tests/test_install_review5_regressions.py tests/test_004_001_t6.py",
        "Finalmente, sin trabajo concurrente: CDAD_TEST_TMP_BASE=/var/tmp/cdad-suite-epic2 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "Corrección de helpers, consumidores y verificadores bajo alcance de tests: test-writer independiente; revisión del diff, aserciones y cumplimiento: reviewer independiente; coordinación, materialización de evidencias y suite final sin concurrencia: orchestrator; aprobación: autoridad competente. Cada dispatch conserva los límites de su rol y alcance."
    }
  ]
}
```
