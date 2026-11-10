# Delta de inventario vivo — T2 (017-001-suite-performance)

Materializado por el orquestador desde `red-T2-markers.md` y
`red-T2-markers-fix.md`, antes de la siguiente transicion.

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_operations.py::test_active_observer_captures_intervals_with_identity_context_and_nesting` | T2-check-1 | operation-markers-v1 (spec §4.2, PC-1 parte, INV-1/INV-8) | RED T2 corregido D1 |
| `tests/test_017_001_suite_operations.py::test_exceptional_exit_closes_interval_with_error_termination` | T2-check-2 | operation-markers-v1 (PC-1 parte, INV-2) | RED T2 corregido D1 |
| `tests/test_017_001_suite_operations.py::test_without_observer_helper_is_neutral_and_leaves_no_evidence` | T2-check-3 | operation-markers-v1 (PC-1 parte, INV-2) | RED T2 corregido D1 (control) |
| `tests/test_017_001_suite_operations.py::test_missing_markers_capture_is_diagnosed_as_incomplete_measurement` | T2-check-4 | operation-markers-v1 (PC-1 parte, INV-6/INV-8) | RED T2 corregido D2 |

Soporte (no verificador): `tests/suite_operation_markers.py`, costura neutra de
marcas con canal dedicado. 4 nodeids, disposicion Añadir. T1 sin cambios.

## Tranche 1: marcas reales (2026-11-07)

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_tranche1.py::test_real_product_lookup_emits_branch_and_stays_neutral` | T2-check-6 | operation-markers-v1 (spec §4.2, PC-1 parte, INV-1/INV-2/INV-8) | tranche 1 |

Soporte: marcas reales en `tests/conftest.py`, `tests/product_staging.py`,
`tests/test_007_002_dispatch_recovery.py` y `tests/test_007_003_continuity_at_edges.py`.
Total del oraculo T2: 6 nodeids.

## Tranche 2: staging U1/U3/U4 y documental (2026-11-07)

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_tranche2.py::test_real_tranche2_lookups_emit_branch_and_stay_neutral` | T2-check-7 | operation-markers-v1 (spec §4.2, PC-1 parte, INV-1/INV-2/INV-8) | tranche 2 |

Soporte: marcas reales en `tests/test_006_002_u1_delegation_section.py`,
`tests/test_006_004_u3_principle_single_source.py`,
`tests/test_006_005_u4_single_entry.py` y
`tests/test_010_002_documentary_role_integration.py`.

Correccion de entorno declarada: `_temp_root()` exigia solo `is_dir()` sobre
`/tmp/opencode`, que en este host pertenece a otro usuario; los tests de U3 y D
fallaban con `PermissionError` antes de cualquier cambio de esta feature. Se
exige writability y se cae a la base estable de sesion (commit `27ac3a88`).
Total del oraculo T2: 7 nodeids.

## Sumideros multiples y C-P (2026-11-07)

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_operations.py::test_concurrent_sinks_coexist_and_both_receive_events` | T2-check-8 | operation-markers-v1 (spec §4.2, PC-1 parte, INV-1/INV-8) | P7 |
| `tests/test_017_001_suite_operations.py::test_product_root_cold_then_reuse` | T2-check-9 | calibrate C-P-cold (spec §4.2/§4.4) | C-P |
| `tests/test_017_001_suite_operations.py::test_product_root_existing_manifest_then_reuse` | T2-check-10 | calibrate C-P-present (spec §4.2/§4.4) | C-P |

Soporte: `tests/suite_operation_markers.py` pasa a sumideros multiples (P7).
Total del oraculo T2: 9 nodeids en `tests/test_017_001_suite_operations.py`.

## T3: oraculo contable (2026-11-07)

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_reconcile.py` (9 nodeids) | T3-check-1..9 | PC-6 (§4.4) via `t3-aggregator-contract.md` | T3 |

Modulo nuevo: `tests/test_017_001_suite_reconcile.py` (9 tests, sin helpers).
Total del inventario: 244 modulos.
