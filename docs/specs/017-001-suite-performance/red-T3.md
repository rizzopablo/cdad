Route C validado antes de trabajar:
- Identificación del dispatch idéntica al render canónico `render --request … --route C` (packet_id, contract+sha256, execution_id, rutas).
- `PACKET.md` idéntico byte a byte al render canónico completo (`diff` limpio).
- `validate-request` y `validate-packet`: exit 0.
- Contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…` verificado contra el archivo; contexto de ejecución v2 presente (`schema_version: 2`).
- No se cargó `cdad-cycle` ni otro skill de ciclo; solo el packet como contrato de ejecución.

Trabajo ejecutado (test-writer, substage `red`, paquete `017-001-suite-performance-test-writer-red-014`, T3):

**Pre-RED:** busqué en `tests/` y contratos autorizados protección existente para el agregador (`reconcile`/`entry-check`): no existe `test_017_001_suite_reconcile.py` ni ningún verificador de esos subcomandos (solo `close` de T1/T2 y el contrato operativo `t3-aggregator-contract.md`). Protección faltante declarada → test nuevo, sin tocar existentes. No leí `scripts/cdad-suite.py` ni implementación alguna (solo lo ejercí como caja negra por CLI, como autoriza el packet).

**Oráculo escrito (PC-6; INV-5/INV-6 donde se indica), un archivo nuevo:**
- `tests/test_017_001_suite_reconcile.py` (599 líneas, 9 tests):
  1. `test_reconcile_two_tests_reports_s_test_attributed_and_remainder` — S_test/atribuido/resto. Sin él, el usuario no puede localizar el costo.
  2. `test_reconcile_nested_child_is_breakdown_not_additional_cost` — padre-hijo sin doble conteo. Sin él, la preparación puede superar S_test.
  3. `test_reconcile_partial_overlap_counts_union_not_sum` — solapamiento como unión. Sin él, la intersección se cuenta dos veces.
  4. `test_reconcile_shared_operation_stays_separate` — compartido en bloque propio. Sin él, se infla el S_test del primer test.
  5. `test_reconcile_run_and_exterior_residuals_keep_sign_and_resolution` — R_pytest/R_exterior con signo y resolución. Sin él, el tiempo fuera de fases/hijo es invisible o se fuerza a cero.
  6. `test_incomplete_status_still_reconciles_but_blocks_entry` — incomplete: reconcile rc 0 + entry rc 1 con diagnóstico. Sin él, o se pierde el diagnóstico o la base entra sobre captura rota.
  7. `test_missing_count_vs_register_blocks_entry` — `missing-operation-vs-register` y entrada bloqueada. Sin él, la base entra con operaciones faltantes.
  8. `test_reconcile_is_byte_for_byte_deterministic` — mismo JSON byte a byte. Sin él, la evidencia deja de ser reproducible.
  9. `test_unusable_inputs_return_2_with_stderr_reason` — código 2 con motivo por stderr. Sin él, una entrada rota pasa como 0/1 silencioso.
- Cada test verifica códigos de salida y que `reconciliation.md`/`entry.md` existan y no estén vacíos. Forma de salida documentada en el header (conceptos del contrato; alias de clave aceptados donde el contrato fija conceptos, no claves).

**Evidencia RED (comando exacto y fallos esperados):**
- `python3 -m pytest tests/test_017_001_suite_reconcile.py --collect-only -q` → 9 tests, colección limpia (sin ImportError).
- `python3 -m pytest tests/test_017_001_suite_reconcile.py -q` → **9 failed**, todos `AssertionError` de promesa ausente, nunca ImportError ni error de colección. Ejemplo: `reconcile debe salir 0 con intento completo; salio 2: … invalid choice: 'reconcile' …`. El test del código 2 falla porque el stderr actual dice `invalid choice` en vez del motivo contractual (`profile.json`/`attempt.json`). Comportamiento hoy: ambos subcomandos inexistentes → rc 2 del parser.
- `git status` confirma diff limitado a `tests/`; ausencia de lecturas de implementación declarada honestamente (límite PD-15: guard por nombre, no sandbox; solo leí `docs/specs/017-001-suite-performance/*` y `tests/`).

**Commit:** `1834e0d5` — `017-001 T3 RED: oraculo contable del agregador y condicion de entrada (PC-6)` — 1 archivo, solo `tests/test_017_001_suite_reconcile.py`.

**Delta de inventario vivo (como texto, no materializado — fuera de write_scope):**
- Nuevo verificador: `tests/test_017_001_suite_reconcile.py` (9 tests RED, PC-6) sobre revisión `1834e0d5`.
- Sin cambios de producto ni de inventario estructural; T3 sigue pendiente de GREEN (implementar `reconcile`/`entry-check` en `scripts/cdad-suite.py` según `t3-aggregator-contract.md`).
- Suite completa no realizada (ciclo focal; solo el focal RED de arriba + `--collect-only`).
