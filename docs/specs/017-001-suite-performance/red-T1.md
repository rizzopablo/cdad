# FINAL TEXT — test-writer RED T1 (017-001-suite-performance)

## Route C validation — PASS (before working)
- Identification block in the dispatch equals the canonical `render --route C` output (byte-identical, verified via `scripts/cdad_packet.py`).
- Full `render` diff vs `PACKET.md` → empty (complete match, 9694 bytes, not header-only).
- `packet_id`, `execution_id`, contract `path`+`sha256` match `REQUEST.json`; contract sha256 `472bab0c…192672e` matches `docs/specs/017-001-suite-performance/spec.md` on disk.
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture.
- Proceeding on Route C, substage `red`, inputs/scopes of the packet only.

## Resultado RED
Módulo nuevo `tests/test_017_001_suite_profile.py` (5 tests, uno por promesa C1–C5 del AUDIT, trazados a PC-1 parte resultados/fases y PC-2, §§4.2–4.3). Oráculo derivado del contrato aprobado y de los patrones de repos sintéticos + CLIs/conftest grabadoras de `test_008_002_suite_evidence.py` / `test_008_005_ci_gate.py`, sin modificar esos verificadores.

Comando exacto:
`python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py`
→ **5 failed in ~5.5s**, los 5 por `AssertionError` de promesa ausente (artefacto `pytest.xml`/`profile.json` no conservado por el intento), **ningún ImportError ni error de colección** del módulo nuevo. Fallos esperados, uno por test:
1. `test_close_emits_xml_and_pha<session>_emitted_selection` — falta `pytest.xml` (línea 121).
2. `test_attempt_preserves_argv_and_new_artifacts_across_attempts` — falta `profile.json` (línea 113).
3. `test_profile_preserves_failures_skips_and_interruptions_without_substituting_rc` — falta `pytest.xml` en caso fallo (línea 121).
4. `test_incomplete_measurement_is_diagnosed_not_presented_as_contract` — falta `profile.json` (línea 113).
5. `test_instrumented_close_runs_single_pytest_and_records_wall_argv` — falta `profile.json` (línea 113).

Notas honestas: sin umbrales temporales como oráculo (pared solo presencia/tipo/≥0, sin techo ni igualdad); R5 reutiliza a nivel gate el PC-1 existente sin duplicarlo; la conftest grabadora supone que `close` propaga el entorno al hijo pytest (hereda el patrón de los verificadores existentes).

## Evidencia del rol
- Implementación leída: **ninguna** (`scripts/cdad-suite.py` y el observador no leídos; aislamiento de fase preservado).
- Archivos modificados: **uno** — `tests/test_017_001_suite_profile.py` (creado, 365 líneas). `docs/.cdad-state.json` figuraba modificado antes de empezar; no lo toqué ni lo commiteé.
- Suite completa **no realizada** (ciclo focal; corresponde a GREEN/revisión).
- Commit: `dd3927ec49cb21c1594b796dbbfc7504f440e79f` (diff limitado a `tests/`).

## Delta de inventario vivo (texto, para materializar por el orquestador)
- Alta propuesta con disposición **Añadir** (no materializada en inventario por este rol): `tests/test_017_001_suite_profile.py` —
  - `::test_close_emits_xml_and_pha<session>_emitted_selection` | capacidad T1-check-1 | contrato phase-profile-v1 (spec §§4.2–4.3, PC-1 parte, INV-1/INV-6) | procedencia: nuevo RED T1.
  - `::test_attempt_preserves_argv_and_new_artifacts_across_attempts` | T1-check-2 | phase-profile-v1 (PC-1 parte, PC-2 reserva, INV-1) | nuevo RED T1.
  - `::test_profile_preserves_failures_skips_and_interruptions_without_substituting_rc` | T1-check-3 | phase-profile-v1 (PC-2, INV-6) | nuevo RED T1.
  - `::test_incomplete_measurement_is_diagnosed_not_presented_as_contract` | T1-check-4 | phase-profile-v1 (PC-1 parte, INV-6) | nuevo RED T1.
  - `::test_instrumented_close_runs_single_pytest_and_records_wall_argv` | T1-check-5 | phase-profile-v1 (PC-2 §4.3, INV-7) | nuevo RED T1.
- Existentes sin cambios: 41 funciones **Mantener** (5 evidencia + 25 selección + 11 gate) según AUDIT aprobado; 0 Extender/Sustituir/Consolidar/Retirar.
