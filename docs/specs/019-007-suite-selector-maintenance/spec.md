# Specification — 019-007-suite-selector-maintenance

Status: Approved by CDAD orchestrator under <owner>'s renewed HITL delegation for epic 019 on 2026-11-17.

Architect draft received 2026-11-17 (packet
019-007-suite-selector-maintenance-architect-draft-001), materialized by the
orchestrator without altering its text (ADR-003). It remains unapproved until
the independent draft review and the owner decision are recorded.

### Especificación propuesta — selección inequívoca del artefacto instalado

**Objetivo y contrato.** Corregir exclusivamente los selectores de los tests de instalación: localizar el archivo mediante el destino registrado en `.cdad-install-manifest.json`, no mediante la primera coincidencia del filesystem. Se conserva íntegra la promesa «staging es la fuente de verdad». Autoridad: plan aprobado, sección «Owner-approved extension — suite selector maintenance», líneas 231–246.

**Contexto comprobado.** Ambos helpers devuelven `matches[0]` tras `rglob` (`tests/test_install_ownership.py:147–153`; `tests/test_install_review5_regressions.py:224–230`). El manifiesto ofrece destinos asociados a `source`, interfaz ya usada por `deployed_paths_for_source` (`test_install_review5_regressions.py:240–251`). El caso fallido conoce el origen exacto `entry["file"]`, pero pierde esa identidad al seleccionar por basename (`test_install_ownership.py:564–595`).

**Alcance.** Los dos helpers y sus consumidores necesarios. Debe conservarse o adaptarse coherentemente el consumidor importado por `tests/test_004_001_t6.py:55,288`. Quedan fuera instalador, agentes, políticas, generación y comportamiento del producto.

### Promesa A — el test observa el despliegue correspondiente

- **PC-1.** Cuando compara bytes de un origen de staging, el test obtiene un destino del manifiesto cuyo `source` corresponde exactamente a ese origen y comprueba que el archivo existe. Dos variantes con el mismo basename no pueden intercambiarse por el orden del filesystem.
- **PC-2.** Ambos helpers y sus consumidores seleccionan mediante destinos registrados. Una selección ausente o todavía ambigua produce un fallo explícito, no una alternativa silenciosa por basename.
- **PC-3.** El caso `test_t5_case8_install_deploys_staging_bytes_without_sources` mantiene la mutación de staging, su hash actualizado, `sources/` inaccesible, instalación satisfactoria y comparación exacta con los bytes mutados. Se conservan las restantes aserciones funcionales.

**Verificación: combinada.** Evidencia ejecutable con variantes homónimas de bytes distintos, resolución por origen y rechazo de selección no resoluble; revisión independiente del delta y de las aserciones preservadas. Aceptación: PC-1–3 demostradas sin depender del orden de enumeración. Límites: pasar el caso aislado no demuestra integración; leer el manifiesto tampoco sustituye comparar los bytes reales.

**Criterio de diseño.** Se propone resolver identidad mediante la relación general `source → destino` publicada por el manifiesto, en lugar de ordenar `rglob` o fijar exclusivamente una ruta OpenCode. Evita depender tanto del filesystem como de un layout duplicado en los tests; no requiere crear una nueva infraestructura de helpers.

### Promesa B — mantenimiento del instrumento, sin cambio del producto

- **PC-4.** El diff funcional queda limitado a tests y sus consumidores necesarios; no cambia el comportamiento ni los artefactos del producto.

**Verificación: combinada.** Revisión independiente del diff más regresión ejecutable. Aceptación: alcance respetado, aserciones conservadas y comprobaciones siguientes satisfactorias, en este orden:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_install_ownership.py::TestT5StagingIsSourceOfTruth

PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_install_ownership.py tests/test_install_review5_regressions.py tests/test_004_001_t6.py

CDAD_TEST_TMP_BASE=/var/tmp/cdad-suite-epic2 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests
```

Guardar revisión, comandos, snapshot, salida completa, códigos de salida y skips justificados. La suite final se ejecuta sin trabajo concurrente y alimenta el cierre del epic. Un fallo o ejecución incompleta no permite declarar suite verde. Los tests y el diff no prueban ausencia universal de regresiones.

**Invariantes:** selección sustentada en el manifiesto; comparación independiente de bytes; aislamiento de fixtures conservado; ninguna modificación del producto.

**Rondas:** máximo propuesto **2**, provisional, aplicable independientemente a draft, audit y result. La corrección es localizada, pero existen dos helpers y un consumidor entre módulos; una selección errónea podría producir falsos verdes. No se autoriza ninguna extensión.

**Deferred-hardening:** unificar todos los helpers de instalación y endurecer exhaustivamente manifiestos maliciosos quedan fuera: no son necesarios para resolver esta ambigüedad. No se difiere ninguna postcondición comprometida.
