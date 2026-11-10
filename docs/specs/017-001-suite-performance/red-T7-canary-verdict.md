Route C validada y RED completado. Reporte del rol test-writer (substage `red`):

## Validación Route C
- Identificación del dispatch (`packet_id` 017-001-suite-performance-test-writer-red-029, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`) coincide con `REQUEST.json` y con el bloque inline de `PACKET.md`.
- `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e` ✅ (coincide con el contrato declarado).
- Contexto de ejecución v2 (`schema_version: 2`) ✅. Sin mezcla de rutas (sin inline body + identificación juntos como doble vía; el bloque citado es solo identificación). Procedí por Ruta C.
- Leídos solo inputs declarados (spec, `performance/parallelism.md`, `t7-final-run-contract.md`, `review-T6-005.md`, `tests/test_017_001_suite_parallel.py`). **Implementación no leída** (`scripts/cdad-suite.py` intacto, sin lecturas). Solo caja negra vía CLI.

## Trabajo realizado
- Agregada **UNA** protección nueva `test_parallel_accepts_cdad_tmp_subdir_churn_without_content_change` (Q1 → **PC-10**, promesa E, con apoyo en PC-12) a `tests/test_017_001_suite_parallel.py`. Diff puramente aditivo: `git diff` muestra **113 inserciones, 0 eliminaciones**; los 17 tests existentes byte-idénticos (verificado: cero líneas `-` en el diff).
- Consecuencia declarada: *sin este test, el usuario vería rechazada toda corrida `--all` con scratch declarado bajo `.cdad/tmp` (rc 3 por mtime de directorios padres con contenido idéntico) sin que nada lo detecte como defecto de veredicto.*
- Sonda fuera de `tests/` (árbol temporal, pasada por `--nodeids`, embebe la ruta absoluta del repo, crea y retira `.cdad/tmp/canary-churn-<uuid>`, limpieza en `finally`, sin residuos). Sentido contrario (rechazo por contenido) no cubierto a propósito — ya protegido por N2/O2.

## Evidencia RED (fallo por la razón correcta)
Comando exacto:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider --basetemp=/tmp/pytest-017-001-red029 -q tests/test_017_001_suite_parallel.py::test_parallel_accepts_cdad_tmp_subdir_churn_without_content_change
```
Resultado: **1 failed en 7.11 s** — `AssertionError` de promesa (nunca ImportError ni error de colección; colección previa: 18 tests OK):
```
AssertionError: 017-001 T7 RED (Q1, PC-10): el lote con churn transitorio bajo
.cdad/tmp (crear y retirar canary-churn-c39f1303a8da sin tocar contenido) debe
terminar con exito (rc 0), no rechazar la corrida; rc=3
stderr='... veredicto=rejected: canary detected changes, ... (canario alterado
(config delta_lines=0, checkout unchanged=False))'
```
El fallo reproduce exactamente el defecto diagnosticado: contenido idéntico, solo churn de directorios.

## Commit
- `44d15f7c` — `test(017-001): T7 RED churn transitorio .cdad/tmp debe aceptarse (Q1, PC-10)` — 1 archivo, +113. Solo `tests/`.
- Sin residuos: ningún `canary-churn-*` bajo `.cdad/tmp`; `git status` limpio salvo el preexistente `M docs/.cdad-state.json` (ajeno a este task, no tocado por mí).

## Delta de inventario vivo (como texto)
- Tests: `tests/test_017_001_suite_parallel.py` 17 → **18 tests** (nuevo Q1, RED rojo). Producto: **0 archivos modificados**. Inventario de garantías sin cambios: la corrección del veredicto queda pendiente del implementer; T7 sigue no acreditada hasta el par completo sobre revisión única.
