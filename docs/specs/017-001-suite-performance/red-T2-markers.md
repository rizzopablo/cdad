# FINAL TEXT — test-writer RED T2 (017-001-suite-performance)

## Route C validation — PASS (before working)
- Identification block in the dispatch equals the canonical `render --route C` output (byte-identical, verified via `scripts/cdad_packet.py`).
- `validate-request` → exit 0; `validate-packet` → exit 0 (full render vs `PACKET.md`, not header-only).
- `packet_id`, `execution_id`, contract `path`+`sha256` match `REQUEST.json`; contract sha256 `472bab0c…192672e` matches `docs/specs/017-001-suite-performance/spec.md` on disk.
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture.
- Proceeded on Route C, substage `red`, inputs/scopes of the packet only.

## Pre-RED (authorized sources only)
- Searched `tests/` for existing operations verifiers: no matches for `suite_operation_markers|suite_operations` and none for `"operations"` assertions. T1 oracle (`test_017_001_suite_profile.py`) covers XML/phases only — no interval identity, context, nesting, exceptional close, or missing-capture diagnosis. Contribution declared: 4 new tests, one per observable promise below; without them the user calibrates on fiction or enters baseline on broken capture.

## Resultado RED
Módulo nuevo `tests/suite_operation_markers.py` (costura neutra: canal `cdad.suite.operations`, contexto test/compartido, padre, proceso, rama, terminación; sin observador no emite ni escribe; `finally` con error) + oráculo nuevo `tests/test_017_001_suite_operations.py` (4 tests, P1–P4, trazados a PC-1 parte operaciones §§4.2, INV-1/INV-2/INV-6/INV-8). Oráculo derivado del contrato y del esquema `performance/operation-scope.json` (mechanism `explicit-synchronous-markers`) con el formato `profile.json` de T1 vía `close` caja negra sobre repos sintéticos; ninguna aserción toca `scripts/cdad_suite_observer.py` ni su API interna.

Comando exacto:
`python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py`
→ **4 failed in ~3.8s**, los 4 por `AssertionError` de promesa ausente (el perfil T1 existe pero trae `operations: []`), **ningún ImportError ni error de colección**. Fallos esperados, uno por test:
1. `test_active_observer_captures_intervals_with_identity_context_and_nesting` — el perfil no trae operaciones observadas (línea 168).
2. `test_exceptional_exit_clo<session>_with_error_termination` — el perfil no trae operaciones; sin captura no se exige el cierre por excepción (línea 211). La parte en proceso (begin+end error, propagación intacta) pasa; el test falla en la promesa pendiente del implementador.
3. `test_without_observer_helper_is_neutral_and_leaves_no_evidence` — idem, contraste de no-evidencia sin operaciones que acreditar (línea 241). La neutralidad en proceso (resultado intacto, excepción propagada, cero archivos) pasa.
4. `test_missing_markers_capture_is_diagnosed_as_incomplete_measurement` — el alcance exige 8 familias comprometidas y el perfil capturó cero (línea 267).

Notas honestas: sin umbrales temporales como oráculo (solo presencia/identidad/diagnóstico); P3 no afirma que el perfil deba estar vacío sin observador, solo que sin operaciones no hay contraste que acredite la neutralidad a nivel perfil; el nombre exacto del campo de referencia al alcance se acepta tolerante (`operation_scope`/`scope_ref`/…).

## Evidencia del rol
- Implementación leída: **ninguna** (`scripts/cdad-suite.py`, observador e implementación de tests no leídos; aislamiento de fase preservado).
- Archivos modificados: **dos** — `tests/suite_operation_markers.py` (creado, 149 líneas), `tests/test_017_001_suite_operations.py` (creado, 273 líneas). `docs/.cdad-state.json` figuraba modificado antes de empezar; no lo toqué ni lo commiteé.
- Colección limpia: `--collect-only` 4 tests, 0 errores.
- Suite completa **no realizada** (ciclo focal; corresponde a GREEN/revisión).
- Commit: `ed9e2bc5242917e3400970a4d6c431008a4522a5` (diff limitado a `tests/`, 2 archivos, 422 inserciones).

## Delta de inventario vivo (texto, para materializar por el orquestador)
- Alta propuesta con disposición **Añadir** (no materializada en inventario por este rol): `tests/test_017_001_suite_operations.py` —
  - `::test_active_observer_captures_intervals_with_identity_context_and_nesting` | capacidad T2-check-1 | contrato operation-markers-v1 (spec §4.2, PC-1 parte operaciones, INV-1/INV-8) | procedencia: nuevo RED T2.
  - `::test_exceptional_exit_clo<session>_with_error_termination` | T2-check-2 | operation-markers-v1 (PC-1 parte, INV-2) | nuevo RED T2.
  - `::test_without_observer_helper_is_neutral_and_leaves_no_evidence` | T2-check-3 | operation-markers-v1 (PC-1 parte, INV-2) | nuevo RED T2.
  - `::test_missing_markers_capture_is_diagnosed_as_incomplete_measurement` | T2-check-4 | operation-markers-v1 (PC-1 parte, INV-6/INV-8) | nuevo RED T2.
- Soporte (no verificador): `tests/suite_operation_markers.py` — costura neutra propuesta (mapping §2, mechanism explicit-synchronous-markers).
- Existentes sin cambios: T1 (`test_017_001_suite_profile.py`) **Mantener**; 0 Extender/Sustituir/Consolidar/Retirar.
