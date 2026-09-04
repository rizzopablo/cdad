# Active Context

Estado actual del proyecto. Cada feature cerrada agrega una entry. Las entries más recientes arriba.

---

## 2026-09-04 — Fix: path-guard reconoce tests colocados (sin ciclo formal)

Fix en `scripts/claude-code-path-guard.sh` (commit `0fd023f`), detectado en
Foxbridge con Claude y reportado por Pablo. El guard asumía tests en
`tests/**` dedicado, pero Go EXIGE tests en el mismo paquete/directorio
(`*_test.go`, requisito del compilador) y JS/TS coloca `*.test.{js,ts}`
junto al módulo. Consecuencias corregidas en AMBOS lados:

- **test-writer-write / test-writer-odoo-write**: la allowlist de escritura
  ahora acepta tests colocados (`**/*_test.go`, `**/*.test.{js,ts,mjs,cjs}`,
  `**/*.spec.{ts,js}`, `**/test_*.py`), además de `tests/**` y `**/tests/**`.
  Sin esto, el rol quedaba sin NINGÚN path escribible en un repo Go.
- **implementer / implementer-odoo** (lado inverso, no reportado — detectado
  en revisión): la blocklist ahora incluye los mismos patrones. Sin esto, el
  implementer podía editar tests colocados y romper silenciosamente el gate
  anti-trampa.
- **test-writer-read**: excepción de lectura para tests colocados bajo
  `src/**`/`lib/**` (el test-writer debe poder leer la suite que edita).
- **Factorización**: array `TEST_FILE_GLOBS` + `is_test_file()` como fuente
  única usada por ambos lados.

Verificación: batería de 19 casos por rol (bloqueos/permisos, ambos layouts,
variantes Odoo) — 19/19 PASS. Copia instalada (`~/.claude/cdad-scripts/`)
redesplegada e idéntica a la canónica.

**Deuda de proceso (documentada, no oculta):** el fix se aplicó inline y
antes del spec — bypass del ciclo CDAD (Pablo pidió ciclo light a mitad de
camino; se decidió no retroactivar y solo documentar). La batería de 19
casos no vive como test permanente en `tests/` — si el guard vuelve a
tocarse, incorporarla como RED formal de esa feature.

## 2026-09-02 — Epic: epic-002-cdad-audit-fixes (12 features, cerrado)

Cerrado el epic que corrige los hallazgos de
`findings/audit-consistencia-2026-09-02.md` (auditoría completa de
metodología, agentes OpenCode/Claude Code y skills, pedida por Pablo).
Delegación HITL explícita para todo el epic (spec approval, priorización,
Memory Bank) — ver `docs/.cdad-state.json` campo `hitl_delegation`.

Decisiones relevantes:
- **B1 (bash como fuga del aislamiento)**: calibrado como defensa en
  profundidad, no reescritura estricta — decisión explícita de Pablo antes
  de ejecutar: *"la combinación de barrera estructural parcial + conductual
  está funcionando bastante bien"*. La allowlist de bash cierra la fuga de
  contenido (cat/head/tail/rg) preservando TODO lo legítimo (tests, lint,
  git commit propio, navegación) — ningún rol perdió capacidad real.
- **Perfil `basic`**: es el más usado por Pablo (costo de tokens) y su
  comportamiento NO cambió — el fix fue puramente documental (dejar de
  afirmar el anti-bias como garantizado ahí, cuando ADR-007 ya documentaba
  la excepción).
- **RED verifica requerimiento, no cobertura**: refuerzo explícito pedido
  por Pablo — un test-writer no debe sobre-especificar más allá del spec
  (tests carísimos/imposibles de satisfacer, tiempo y tokens perdidos).
  Agregado a SKILL.md, stage-3-tdd.md, y a los 4 agentes test-writer.

Deuda técnica detectada:
- Esta misma entry es la primera desde cdad-004 (2026-09-02) —
  activeContext.md no tenía entries para cdad-005..009 pese a estar `done`
  en progress.md. No se backfillea acá (fuera del scope de este epic); si
  hace falta detalle de esas 5 features, está en sus commits y en
  `docs/epics/epic-001-superpowers-gaps/closure.md`.
- Deuda ya registrada sin cambios: CI del repo, dogfood pendiente de varias
  features (ver progress.md Queued).

Próxima feature en cola: ninguna decidida — Pablo define.

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
