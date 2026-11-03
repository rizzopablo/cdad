# Integración — epic-015-dispatch-reception

- Features: 015-001 (recepción congelada), 015-002 (guardas de entrada), 015-003 (oráculo de conjunto cerrado); cerradas.
- **Suite completa de cierre (obligatoria, ADR-042):** gate atribuible `scripts/cdad-ci-gate.py`, commit `a2663482`,
  árbol limpio: **1967 passed, 0 failed, 5 skipped**, verde atribuible
  (`.cdad/local/epic015c/gate-20261103T031214290036Z-1791981-e8c19d44`).
- Intentos previos conservados (PC-8 de ADR-042, no se reintentó hasta verde sin hipótesis):
  1. `epic015` (`8acccc41`): 1966 passed, 1 failed → regresión real de 015-001 en el oráculo INV-04 de 010-002;
     corregida en 015-003.
  2. `epic015b` (`a2663482`): 1966 passed, 1 failed (`test_006_005_u6fix5_write_ahead::test_u65_crash_midrun_recovers_through_disposition`,
     «el cliente falso no escribió su fila durable»): temporización del fixture bajo carga (loadavg 6–7); aislado pasa y
     el archivo pasa 3/3. Hipótesis: carga. Tercer intento sin otra actividad en paralelo → verde.
- Skips (5): integraciones reales que requieren variables de entorno; no son promesas del epic.
