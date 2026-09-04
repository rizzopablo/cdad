# Progress

Estado de features del proyecto.

## In progress

_(ninguna — "Temas 2-5 de superpowers-gaps" cerró completo con
cdad-006..009, ver Done; nota vieja no se había actualizado al cerrar esas
features. Corregido en epic-002-cdad-audit-fixes.)_

## Done

- **fix-path-guard-colocated-tests** (2026-09-04, sin ciclo formal — ver
  nota de proceso en activeContext.md) — `scripts/claude-code-path-guard.sh`
  reconoce tests colocados (Go `*_test.go`, JS/TS `*.test.{js,ts,mjs,cjs}` /
  `*.spec.{ts,js}`, Python `test_*.py`) además de `tests/**`. Fix de un
  proyecto cliente sincronizado a la canónica, más el lado inverso no
  reportado:
  implementer/implementer-odoo ahora bloquean edición de tests colocados
  (gate anti-trampa). Factorizado en `TEST_FILE_GLOBS` + `is_test_file()`.
  Verificado 19/19. Commit: `0fd023f`.
- **epic-002-cdad-audit-fixes** (2026-09-02) — 12 features corrigiendo los
  11 bloqueantes + 10 medios de `findings/audit-consistencia-2026-09-02.md`
  (auditoría de consistencia de toda la metodología, agentes y skills).
  HITL delegado por Pablo ("actuá como hitl, tomá las mejores decisiones").
  Highlights: bash allowlist calibrada en test-writer/implementer (fuga que
  esquivaba el path-scoping, calibrada para no perder capacidad legítima
  por pedido explícito del dueño); guard anti-bias extendido a
  cdad_model_claude (premium tenía reviewer==implementer=opus); taxonomía
  del reviewer unificada (4/4 en addyosmani); orquestador Claude Code
  reparado (mecanismo de delegación + resolución de stack); contrato de
  veredicto (Bucket/Abstenciones) llevado a los 4 agentes reviewer;
  contradicción property tests resuelta + disciplina "RED verifica
  requerimiento, no maximiza cobertura"; `tests/validate-consistency.sh`
  nuevo (124 asserts) verificando todo lo anterior; cierre retroactivo de
  epic-001-superpowers-gaps (nunca había tenido closure.md formal). Detalle
  completo: `docs/epics/epic-002-cdad-audit-fixes/plan.md` y `closure.md`.
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
