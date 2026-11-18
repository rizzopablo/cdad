PC-4 GREEN está terminado y commiteado (`cbd7828a`). Los tres archivos de test pasan: 17 tests en verde.

**Validación del paquete (ruta C):** `cdad_packet.py render --request …/REQUEST.json` devolvió rc=0 y su salida es idéntica byte a byte a `PACKET.md` (`cmp` → SAME). No hubo mezcla de rutas ni cuerpo parcial.

**Cambio:** un solo archivo, `skills/cdad-cycle/scripts/cdad_result.py`, con 4 líneas añadidas en `_allowed_kinds`. Para `architect`, la subfase `brainstorm` ahora admite exactamente `role-report`. Los kinds de borrador (`architect-spec-draft` y `architect-plan-draft`) quedan rechazados ahí. Las subfases `discovery` y `draft` y la tabla de los demás roles no cambian. No se impuso cardinalidad global de partes múltiples. No toqué adaptadores, tests ni docs.

**Comando ejecutado** (desde `<repo>`):
```
python3 -m pytest -q tests/test_019_002_discovery_delivery.py tests/test_006_005_u7_scribe_role_report.py tests/test_005_007_t4_architect_report_materialization.py
```
Salida: `17 passed in 47.25s`. No hizo falta ajustar `PYTHONPATH`: el `conftest.py` de `tests/` resolvió los helpers. No corrí la suite completa; solo el foco pedido, así que queda como "suite completa no realizada".

**Commit:** `cbd7828a2237bbbda28598da12693625a5d3a5bc`, "feat: architect/brainstorm admits role-report (019-002 PC-4)". Solo incluye ese archivo. El `docs/.cdad-state.json` modificado ya estaba así antes de mi cambio y no lo commiteé.

**Sin verificar:** el RED registraba 4 fallos de aserción y 6 pases. No miré cuántos de los 17 tests de hoy corresponden a esos 10. Que los tres archivos pasen completos cubre los 4 fallos esperados.