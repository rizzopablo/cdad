T2 RED está hecho y confirmado en el commit `215b0b52`, que contiene solo `tests/test_019_002_resting_orientation.py`. El caso `done`/`null` falla hoy por aserción, que es lo esperado. El otro test pasa ya, porque ese camino funciona en el producto actual.

**Entrada (ruta C).** `cdad_packet.py render --request …/REQUEST.json` dio rc=0 y su salida es idéntica byte a byte a `PACKET.md`. `validate-packet` dio rc=0. El sha256 del spec coincide con el del paquete. No leí código de implementación: solo spec, audit, tests y los CLI públicos. `docs/.cdad-state.json` ya estaba modificado antes de empezar y no lo toqué.

**Tests** (fixtures descartables reutilizados de `test_005_012_t1_register_transition_base`):
- **`test_pc7_closure_status_recommends_open_unit_and_it_succeeds`:** cierra con `register-transition --transition closure`, comprueba que `status` da `entry=next-unit` y nombra `open-unit`, y que `open-unit` abre la siguiente unidad en cola. Pasa hoy.
- **`test_pc7_done_null_state_gets_diagnosis_not_open_unit_and_no_mutation`:** parte del mismo cierre real, pone `current_stage=done` con `active_feature=null` y pide diagnóstico, sin `open-unit`, sin `at-rest` y sin mutar el state.

La consecuencia sin el segundo test es que `status` manda al usuario a un `open-unit` que falla.

**RED.** El segundo test falla con esta aserción: `PC-7 violada: 'done'/'null' no debe producir recomendación 'open-unit'`.
- Hoy `status` devuelve `entry: next-unit`, `situation: at-rest` y la ruta `run cdad_packet.py open-unit`, mientras `open-unit` rechaza ese state.
- Las precondiciones del test (cierre aplicado, `open-unit` rechazando el state) pasan, así que no es un fallo de setup ni de import.
- La aserción final de diagnóstico no llegó a ejecutarse, porque el test cae antes. Busca las palabras `diagnos`, `incoheren` o `inconsisten`. Si el implementador usa otro vocabulario, habrá que ajustarla.

**Comandos y resultados** (con `PYTHONPATH=.:tests`):
- `python3 -m pytest tests/test_019_002_resting_orientation.py -q` dio `1 failed, 1 passed`.
- `python3 -m pytest tests/test_005_001_t3_idle.py tests/test_005_003_t1_compact_view.py tests/test_005_007_t3_open_unit.py tests/test_005_012_t3_closure_dispatch_resolution.py -q` dio `32 passed`.
- `python3 scripts/cdad-suite.py validate` dio "integridad insuficiente", como se esperaba: faltan el módulo y sus 2 nodeids sin inventariar. No hay gate de inventario en RED.

**Delta de inventario para que el orquestador materialice.** Añadir en `suite-inventory.json` una entrada de módulo para `tests/test_019_002_resting_orientation.py`:
- **Capability:** `closure-and-resting-orientation`. Es una suposición mía, no verifiqué si existe un nombre vigente. Conviene ajustarla al vocabulario del inventario.
- **Contract:** `docs/specs/019-002-effective-discovery-instructions/spec.md` (PC-7).
- **Provenance:** `019-002 T2 RED, test-writer; PC-7, test-audit N2`.
- **`helper_dependencies`:** `test_005_012_t1_register_transition_base`.
- **`static_test_nodeids`:** 2, que son los dos nodeids de la sección Tests.
- **`product_surfaces`:** `scripts/cdad_packet.py`, por inferencia, porque no leí código del producto.

**`pc-map.json`:** sin delta, porque no cambió ningún origen ni destino de mapeo.

**Límites.**
- No ejecuté la suite completa.
- Las distinciones activa/suspendida/pendiente no se re-prueban aquí. Las siguen protegiendo `test_007_001`, `test_007_007` y `test_005_003_f2`, sin cambios.
- El caso `done`/`null` se arma mutando el state tras un cierre real, no con un cierre defectuoso real.