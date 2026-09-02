# Progress

Estado de features del proyecto.

## In progress

- **Temas 2-5 de superpowers-gaps** (decisión Pablo 02 Sep: investigación
  a fondo por tema → síntesis → aprobación → cycle/epic según amerite).
  Tema 1 (receiving-feedback) DONE como cycle. En cola: git-safety,
  debugging, planning, parallel-dispatch.

## Done

- **cdad-006-git-safety-close** (2026-09-02) — §5.6 "Cierre de la branch
  (git safety)" en stage-5-merge: entorno+guard submodule, base confirmada,
  menú fijo, discard literal, provenance; AP-17. RED 13/13+guard, GREEN
  19/19, review aprobado (H1 cita §5.6 fixeado). Commits: baba7cf, 0824503,
  be88880.
- **cdad-005-receiving-feedback** (2026-09-02) — protocolo anti-sicofantía
  (reference receiving-feedback.md + transmisor íntegro en stage-4/handoff +
  AP-16 + reconsideración del reviewer con steelman/reversals). RED 22/23,
  GREEN 23/23, suite 121/121, cdad-004 10/10, review aprobado 0 bloqueantes.
  Commits: b626929 (spec+RED), 4e8aa6f (GREEN), 6398cc9 (review).
- **cdad-004-lint-gate** (2026-09-02) — `make lint` (pre-commit-vauxoo) como
  4º target del contrato odoo-make-env + evidencia obligatoria en review.
  Commits: 586a244 (spec+RED), 46d71e2 (GREEN), 3020a09 (fix test stale),
  ef08084 (fixes review), bbccdc9 (review.md).
- **cdad-003-odoo** (2026-08-28) — especialización Odoo de CDAD (ver
  docs/specs/cdad-003-odoo/). Previa al bootstrap de este Memory Bank.

## Queued

- Investigación temas 3-5 de superpowers-gaps (debugging sistemático,
  planning granular, parallel-dispatch) — cada uno: research → síntesis →
  aprobación de Pablo → cycle.
- CI del repo (GitHub Actions) — deuda de bootstrap.

## Blocked

_(ninguna)_

---

Última actualización: 2026-09-02
