# Integración — epic-014-suite-evidence-policy

- Features: 014-001 (defaults por momento, ADR-042) y 014-002 (oráculo PD-10), ambas cerradas.
- **Suite completa de cierre (obligatoria por defecto, ADR-042):** gate atribuible `scripts/cdad-ci-gate.py`,
  commit `b29e9445`, árbol limpio: **1948 passed, 0 failed, 5 skipped**, verde atribuible
  (`.cdad/local/epic014b/gate-20261102T195338083008Z-3066446-c117446e`, ~68 min).
- Primera corrida (`.cdad/local/epic014/…`, `e9969d9e`): 1947 passed, 1 failed, 5 skipped. El rojo
  (`test_pd10_installed_cli_paths_in_t1_wiring_points`) venía del epic 013 (falla en `c4271693`, pasa en `0eab565c`) y
  se corrigió en 014-002. Es la primera vez que el epic 013 se verifica con suite completa.
- Skips (5): integración real de entorno (variables CDAD_* ausentes); no son promesas del epic 014.
