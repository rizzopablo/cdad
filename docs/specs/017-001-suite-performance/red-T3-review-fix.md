Route C validada; trabajo ejecutado solo con el paquete.

**Validación control-plane (route C)**
- `validate-request` rc 0; `validate-packet` rc 0.
- `render --request ... --route C` reproduce byte por byte la identificación del despacho (packet_id `017-001-suite-performance-test-writer-red-015`, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`, execution_id `exec-017-001-suite-performance-001`, mismas rutas de packet/request/context/project_root).
- `sha256sum spec.md` = `472bab0c…` coincide. Execution context `schema_version: 2` (v2, no hubo switch silencioso).
- Sin cuerpo inline en el despacho: admisible en ruta C; no hay mezcla de rutas. No se buscó otro paquete.

**Alcance respetado**
- Leídos solo: los 4 inputs declarados (`spec.md`, `review-T3.md`, `t3-aggregator-contract.md`, `tests/test_017_001_suite_reconcile.py`). No se leyó implementación (`scripts/`, `src/`, `lib/`); la CLI se ejerció como caja negra, no se inspeccionó su código.
- Escrito solo `tests/` (un archivo). `docs/.cdad-state.json` ya figuraba modificado antes (consta en review-T3) y quedó fuera del commit.

**Pre-RED (contribución vs. lo existente)**
- 9 tests vigentes cubren los 8 casos contables + código 2; ninguno vincula la clave del mapa con `attempt.json selection` ni compara `R_exterior` contra 1 s. Los 2 tests nuevos declaran esa diferencia; sin ellos el usuario acredita una base con selección equivocada (bloqueante) o ve anomalías irresolubles de −0.5 s (opcional).

**Tests agregados (append-only, +110, 9 vigentes intactos)**
1. `test_entry_check_binds_map_key_to_declared_selection_and_register` → PC-1 (+PC-6). Contraste: C-R→intento que declara lo esperado sale 0/satisfied=true; C-R→intento que declara `test_other.py::test_wrong` debe salir 1/satisfied=false con motivo que nombre `c-r` y la discrepancia de selección.
2. `test_reconcile_exterior_residual_u<session>_one_second_resolution` → PC-6, INV-6. `R_exterior=−0.5 s` (T_pytest 5.0, T_ext 4.5) no debe dar `residual-sign`; `R_exterior=−1.5 s` (T_ext 3.5) sí. R_pytest=+4.0 aísla el código al exterior.

**Evidencia RED (comando exacto)**
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py::test_entry_check_binds_map_key_to_declared_selection_and_register tests/test_017_001_suite_reconcile.py::test_reconcile_exterior_residual_u<session>_one_second_resolution` → **2 failed in 0.82s**, ambos `AssertionError` de promesa ausente, nunca ImportError/colección:
  - T1: `debe salir 1; salio 0 … (satisfied=true)`.
  - T2: `-0.5 s … no debe diagnosticarse como residual-sign` (diagnósticos `['scope-unavailable','residual-sign']`, `R_exterior: -0.5`).
- Regresión proporcional: mismo runner con `-k "not binds and not one_second"` → **9 passed** (los 9 vigentes siguen verdes).

**Commit**
- Solo `tests/test_017_001_suite_reconcile.py`: commit `0e604efc` — `017-001 T3 RED correctivo: dos protecciones review-T3 (vinculo clave-seleccion y residuo exterior 1s)`; `git diff --stat -- tests/` = 1 file, 110 insertions(+), 0 deletions en tests vigentes.

**Delta de inventario vivo (texto, no editado por estar fuera del write_scope)**
- `tests/test_017_001_suite_reconcile.py`: 9 → 11 verificadores T3 (2 añadidos RED, 0 modificados, 0 retirados/sustituidos).
