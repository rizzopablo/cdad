T2 RED está hecho y confirmado en el commit `dbb15fbd`, que contiene solo los dos archivos de tests. Los 4 tests nuevos fallan hoy por aserción, sin errores de import ni de setup.

**Entrada (ruta C).** El render de `cdad_packet.py render --request …/REQUEST.json` es idéntico byte a byte a `PACKET.md`. El sha256 del spec coincide con el del paquete. No leí código de implementación. Solo leí spec, recovery-spec, recovery-plan, test-audit, tests y los CLI públicos. Revisión base: `a5883154`.

**Archivos modificados**
- **`tests/test_019_002_discovery_delivery.py` (nuevo):** reutilicé como evidencia los tests retirados del commit `91835a6b` y los reevalué contra el PC-4 de recuperación. Cambié las etiquetas PC-5 a PC-4 y los nombres de clase y test a `Pc4`. Agregué al docstring la consecuencia R4 y la aclaración de que no hay exigencia global de cardinalidad de partes. No se agrega ninguna aserción sobre varias partes.
- **`tests/test_006_005_u7_scribe_role_report.py`:** quité solo la tupla `("architect","brainstorm")` de `cases`, con comentario del motivo. Quedan las otras cuatro combinaciones: test-writer/red, test-writer/audit, implementer/green y reviewer/review. Los otros controles de rol cerrado no cambian.

**Consecuencia R4.** Sin estos tests, la consulta del architect no puede devolver de forma fiable su informe por el transporte soportado (nativo u OpenCode). Eso interrumpe el descubrimiento. Hay una promesa de usuario y 4 tests, sin cuota por postcondición.

**Comandos y resultados**
- `cd tests && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:. python3 -m pytest -p no:cacheprovider -q test_019_002_discovery_delivery.py` dio `4 failed`, todos `AssertionError`:
  - **Nativo:** `record` rechaza con rc=1 porque la tabla no determina un único kind para architect/brainstorm; hoy da `['architect-plan-draft','architect-spec-draft']`.
  - **OpenCode:** `termination` es `blocked` en lugar de `completed`, por el mismo motivo.
  - **Materialize de `role-report`:** rc=2, `artifact_kind 'role-report' is not permitted for role 'architect'/substage 'brainstorm'`.
  - **Kinds de borrador:** `architect-spec-draft` se acepta hoy con rc=0 en brainstorm, y debe rechazarse.
- `python3 -m pytest … test_006_005_u7_scribe_role_report.py` dio `6 passed`.
- No corrí la suite completa. No corrí `python3 scripts/cdad-suite.py validate`: fallaría hasta que el orquestador materialice el delta de inventario.

**Delta de inventario para materializar** (nodeids bajo `tests/test_019_002_discovery_delivery.py::`). La capability, la provenance y `product_surfaces` son supuestos míos; no verifiqué el vocabulario vigente del inventario.
- **Capability sugerida:** `consultation-delivery`.
- **Contract:** `docs/specs/019-002-effective-discovery-instructions/spec.md` y `recovery-spec.md`, PC-4.
- **Provenance:** `019-002 recovery T2 RED, test-writer; PC-4; reutiliza 91835a6b`.
- **`helper_dependencies`:** `test_006_005_u1b_dispatch_entry`, `test_006_005_u2_opencode_module`, `test_006_005_u7_scribe_role_report`.
- **`product_surfaces`:** `skills/cdad-cycle/scripts/cdad_result.py`, aunque no lo verifiqué.

| Nodeid | Qué protege |
|---|---|
| `TestPc4NativeDerivation::test_pc4_native_brainstorm_delivery_kind_is_role_report` | Despacho nativo: un único `role-report`. |
| `TestPc4OpenCodeDerivation::test_pc4_opencode_brainstorm_delivery_materializes` | Entrega por el adaptador OpenCode y materialización con sha idéntico. |
| `TestPc4BrainstormMaterialization::test_pc4_brainstorm_role_report_materializes_with_identical_sha` | Aceptación y materialización del `role-report`. |
| `TestPc4BrainstormMaterialization::test_pc4_brainstorm_draft_kinds_are_rejected` | Rechazo de `architect-spec-draft` y `architect-plan-draft`. |

**`pc-map.json`.** La tupla retirada en `test_006_005_u7…::test_pd26_role_axis_role_report_of_other_roles_stays_rejected` cambia el destino de un mapeo, porque ese test ya no cubre architect/brainstorm. Si `pc-map.json` mapea ese test por combinación rol/subfase, el orquestador debe actualizar la entrada. No lo pude verificar sin leer el mapa, que está fuera de mi alcance de escritura.

**Límites**
- El control de architect/draft sigue en `test_006_005_u1b…::TestPd23NativeDescriptorKind` y `test_006_005_u2…::TestPd23DerivedArtifactKind`, sin cambios.
- Que se acepte el `role-report` no demuestra diálogo fiel ni comprensión.
- `docs/.cdad-state.json` y los demás archivos modificados antes de empezar no los toqué.