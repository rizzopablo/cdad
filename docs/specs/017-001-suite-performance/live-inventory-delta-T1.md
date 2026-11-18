# Delta de inventario vivo — T1 (017-001-suite-performance)

Entregado por el test-writer en el RED de T1 como texto y materializado por el
orquestador en el re-entry, antes de la siguiente transicion.

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_profile.py::test_close_emits_xml_and_pha<session>_emitted_selection` | T1-check-1 | phase-profile-v1 (spec §§4.2-4.3, PC-1 parte, INV-1/INV-6) | nuevo RED T1 |
| `tests/test_017_001_suite_profile.py::test_attempt_preserves_argv_and_new_artifacts_across_attempts` | T1-check-2 | phase-profile-v1 (PC-1 parte, PC-2 reserva, INV-1) | nuevo RED T1 |
| `tests/test_017_001_suite_profile.py::test_profile_preserves_failures_skips_and_interruptions_without_substituting_rc` | T1-check-3 | phase-profile-v1 (PC-2, INV-6) | nuevo RED T1 |
| `tests/test_017_001_suite_profile.py::test_incomplete_measurement_is_diagnosed_not_presented_as_contract` | T1-check-4 | phase-profile-v1 (PC-1 parte, INV-6) | nuevo RED T1 |
| `tests/test_017_001_suite_profile.py::test_instrumented_close_runs_single_pytest_and_records_wall_argv` | T1-check-5 | phase-profile-v1 (PC-2 §4.3, INV-7) | nuevo RED T1 |

Disposicion: Añadir (5 altas). Existentes sin cambios: 41 funciones Mantener
(5 evidencia + 25 seleccion + 11 gate); 0 Extender/Sustituir/Consolidar/Retirar.

## Ampliacion por la correccion del review de T1 (2026-11-07)

Altas adicionales entregadas en `red-T1-fix.md`, materializadas por el orquestador:

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_profile.py::test_partial_phase_capture_is_incomplete_with_intact_rc` | T1-H1 | spec §§4.2-4.3, PC-2, INV-6 | correccion review-T1 |
| `tests/test_017_001_suite_profile.py::test_profile_write_failure_preserves_pytest_rc` | T1-H2 | spec §4.3, PC-2, INV-6 | correccion review-T1 |
| `tests/test_017_001_suite_profile.py::test_handled_sigint_preserves_argv_and_wall` | T1-H3 | spec §§4.2-4.3, PC-2 | correccion review-T1 |

Las cinco altas anteriores quedan Mantener sin cambio. Total del modulo: 8 tests.

## Ampliacion por la segunda vuelta del review (2026-11-07)

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_profile.py::test_skipped_teardown_loss_is_incomplete_while_clean_skip_stays_complete` | T1-H1-skip | spec §§4.2-4.3, PC-2, INV-6 | review-T1-002 |

Total del modulo: 9 tests. Las ocho anteriores quedan Mantener.

## Ampliacion por la tercera vuelta del review (2026-11-07)

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_profile.py::test_matrix_phase_loss_is_incomplete_while_clean_stays_complete` (8 casos) | T1-H1-matriz | spec §§4.2-4.3, PC-2, INV-6 | review-T1-003 |

Total del modulo: 17 nodeids recolectados (9 tests + 8 casos parametrizados).
