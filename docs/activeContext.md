# Active Context

Estado actual del proyecto. Cada feature cerrada agrega una entry. Las entries más recientes arriba.

---

## 2026-09-02 — Feature: cdad-004-lint-gate

Cerrada feature que incorpora `make lint` (pre-commit-vauxoo) como 4º target
del contrato odoo-make-env y como evidencia obligatoria en review/gates Odoo.

Decisiones relevantes:
- Lint con `uvx pre-commit-vauxoo==8.3.18`, SIEMPRE `--no-overwrite` (la
  bootstrap de configs es del proyecto, nunca del agente), corre en host,
  autofixes deshabilitados.
- El lint es evidencia mandatory en review Odoo; los hallazgos W/C siguen
  advisory (split mandatory/advisory intacto).
- Fix colateral: assert stale de cdad-003 (odoo-dev-methodology retirado en
  d9dc599, test nunca actualizado) → `assert_file_not_has`.

Deuda técnica detectada:
- CI inexistente en este repo (suite bash local hace de gate) — registrar en
  progress.
- H3/dogfood: `make lint` sin validar end-to-end contra un addon Odoo real.
- Runtime `delegate` (read-only) falló 8/8 por timeout en esta sesión —
  revisar infraestructura antes del próximo epic.

Próxima feature en cola: epic `superpowers-gaps` (5 features, orden
propuesto: G1 recepción de feedback → G5 git safety → G3 debugging → G4
planning → G2 despacho paralelo).

## 2026-09-02 — Bootstrap del proyecto

Memory Bank inicializado durante el cierre de cdad-004-lint-gate (primera
feature del repo con ciclo CDAD completo: spec → RED 10/10 → GREEN → review
two-layer → merge).

Pendientes para completar manualmente:
- CI del repo (GitHub Actions) — deuda registrada en progress.md.
