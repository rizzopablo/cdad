Route C validada (PACKET.md == render canónico, identificación == `render --route C`, contrato sha256 472bab0… verificado contra el archivo, contexto de ejecución v2). Trabajo dentro de `scripts/` únicamente; `tests/` intacto.

## FINAL TEXT — Reporte review-fix T3 (017-001-suite-performance)

**Hallazgos verificados contra su evidencia original antes de cambiar código:** ambos confirmados en `scripts/cdad-suite.py` (residuo exterior contra `1e-3` en vez de `1 s` declarado; `selection-coverage` solo con claves del mapa, sin vincular la selección declarada del intento).

**Cambios (solo `scripts/cdad-suite.py`, commit `ee72f372`):**
1. **Bloqueante (PC-1):** nuevo `_t3_declared_selection_nodeids()` que extrae la selección efectiva del intento según su forma real (dict de `close` con `selection.nodeids`, o `value` si es lista; lista plana sintética; escalar irresoluble → `None`, nunca inventado). `selection-coverage` ahora compara por clave ese conjunto contra los `nodeids` del registro para esa selección; la discrepancia agrega motivo que nombra la selección y la diferencia (`{key}: la seleccion declarada por el intento no coincide con el registro (declarada=…, registro=…)`), y el check pasa solo si `not reasons` (antes ignoraba los motivos nuevos — defecto que detecté porque el test bloqueante seguía en verde tras el primer edit).
2. **Opcional (PC-6):** `R_exterior` se diagnostica `residual-sign` solo bajo `−max(1.0 s, 1e-3)`; `R_pytest` conserva `1e-3`. Semántica de `reconcile` por lo demás intacta.

**Evidencia:**
- Focal T3 (11 tests, incluye los 2 nuevos): `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py` → **11 passed in 3.62s**.
- Focal T1 + focal T2 + regresión proporcional: mismo comando sobre `test_017_001_suite_reconcile.py test_017_001_suite_profile.py test_017_001_suite_operations.py test_008_002_suite_evidence.py test_008_002_suite_selection.py test_008_005_ci_gate.py` → **86 passed in 77.91s**.
- `python3 scripts/cdad-suite.py validate` → **rc 0, status: ok**.
- Entry-check real (mapa `~/clawd/tmp/017-001-calibration-map.json`, salida `~/clawd/tmp/017-001-entrycheck`, fuera de `/tmp/opencode` por el `Permission denied` reportado en review): **rc 0, satisfied=true, seis checks pass, sin diagnósticos** — las ocho selecciones reales siguen pasando con el vínculo nuevo.
- Control negativo sobre evidencia real sin modificarla (mapa temporal con `C-R` apuntando al intento de `C-E`): **rc 1, satisfied=false**, `selection-coverage` FAIL con `C-R: la seleccion declarada por el intento no coincide con el registro (declarada=['tests/test_007_003…'], registro=['tests/test_007_002…'])`.
- `git diff --name-status -- tests/`: sin salida (tests intactos). `docs/.cdad-state.json` figuraba modificado antes de mi trabajo (consta en review-T3.md); no lo toqué ni lo commiteé.

**Límites:** suite completa no realizada (rutina de ciclo: focal + regresión proporcional; cierre de feature/epic la exigiría por política). Determinismo byte-a-byte y no-modificación de intentos reales vía CLI cubiertos por los tests 8 y 6/7 en la regresión; la reejecución CLI real sí se completó aquí (ver arriba).
