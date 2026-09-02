# Progress

Estado de features del proyecto.

## In progress

- **Temas 2-5 de superpowers-gaps** (decisión Pablo 02 Sep: investigación
  a fondo por tema → síntesis → aprobación → cycle/epic según amerite).
  Tema 1 (receiving-feedback) DONE como cycle. En cola: git-safety,
  debugging, planning, parallel-dispatch.

## Done

- **cdad-009-parallel-dispatch** (2026-09-02) — § "Despacho paralelo" en
  stage-3 (árbol, precondición cdad-008, owned/do-not-touch, integración
  final del orquestador, state file solo orquestador, wave dispatch default)
  + subsección en sub-agent-strategies. RED 9/9, GREEN 15/15 (H1 bug de
  oráculo ERE corregido), review aprobado. Cierra el conjunto
  superpowers-gaps (cdad-004..009). Commits: 401e9d5, 59eb932.
- **cdad-008-granular-planning** (2026-09-02) — "Planning de features
  complejas" en stage-2 (tamaño de tarea, Consumes/Produces, plan=contrato
  no implementación) + architect produce plan.md + AP-19. RED 12/12, GREEN
  17/17, review aprobado. Commits: 8db3286, 2413253.
- **cdad-007-systematic-debugging** (2026-09-02) — stage-debugging.md (ley de
  causa raíz, loop rojo = RED, hipótesis rankeadas, 3+ fixes → ADR) + AP-18 +
  enlaces en SKILL/stage-3/stage-5. RED 16/16, GREEN 23/23, review aprobado.
  Commits: cfe5948, 9a70295.
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

- CI del repo (GitHub Actions) — deuda de bootstrap.
- Dogfood pendiente: make lint (H3 cdad-004), §5.6 con worktree real,
  receiving-feedback con bloqueantes reales, stage-debugging con bug real,
  despacho paralelo con 2+ dominios disjuntos.

## Blocked

_(ninguna)_

---

Última actualización: 2026-09-02
