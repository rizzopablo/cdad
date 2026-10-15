# Cierre — 003-004-context-continuity (2026-10-07)

- **Entrega:** `skills/cdad-cycle/scripts/cdad_continuity.py` (+ wrapper
  `scripts/cdad_continuity.py` + schemas `continuity-checkpoint.schema.json` y
  `active-record.schema.json`): `begin`/`checkpoint` (write-ahead, solo bajo
  `.cdad/executions/<id>/continuity/**`), `reconcile` y `resume` (read-only,
  deterministas), `trigger` (señal); contratos `continuity-checkpoint-v1`,
  `reconcile-v1`, `trigger-v1`; referencia operativa
  `skills/cdad-cycle/references/continuity.md`. **El CLI nunca escribe
  `docs/.cdad-state.json`** (single-writer = orquestador) y `continuity` **consume** el
  receipt 002 como oráculo, no materializa.

- **Tareas:**
  - **T1** (checkpoint inmutable + memoria activa + `resume`; P1/P2/P5/P7): RED `d496b13`,
    GREEN `9705aec`; review-fix RED `f710617`, GREEN `209643f`, cierre de test `071b61b`;
    re-review **T1 cerrada**.
  - **T2** (write-ahead + `reconcile` + fixtures de la matriz; P3/P8-fixtures): RED
    `d14d80d`, GREEN `02bc021`; review-fix RED `2209841`, GREEN `00dd557`; re-review
    **T2 cerrada**.
  - **T3** (`trigger` con unknowns + `references/continuity.md`; P6): RED `da60093`, GREEN
    `6c03533`; review sin bloqueantes, **T3 cerrada**.
  - **T4** (adopción real en un límite natural; P8): **orquestador**. RU-1/`RU-1b`/`RU-2`
    registradas en `continuity-ledger.md`; commit `6110e07`.

- **Commits:** spec/plan aprobados `9e3a7c5`; T1 `9705aec` + `209643f` (+ test `071b61b`);
  T2 `02bc021` + `00dd557`; T3 `6c03533`; RU-1 (review-fix real) `0005128`; evidencia T4 `6110e07`.

- **Gate:** suite completa **523 passed** (786 s), en un worktree fijado a `6110e07`, con stdin cerrado. Validadores:
  - `tests/validate-consistency.sh`: 142 PASS / 1 FAIL. El FAIL es F011 (`scripts/validate-subagents.sh`), preexistente: `install.sh --check` se compara contra copias instaladas.
  - `tests/validate-odoo-specialization.sh`: PASS en árbol limpio.
  - Sin regresiones nuevas. La ausencia de CI se declara como deuda (convención vigente).

- **Uso real (`continuity-ledger.md`):**
  - **RU-1** — primer `begin` real sobre `exec-003-004-context-continuity-001`: rc 1
    (`execution_id must be a safe path segment … None`). El contexto real de 001 trae
    `execution.id` anidado y la delegación vive en el state; los fixtures usaban un
    contexto sintético. **Defecto de integración real** → review-fix antes de completar
    T4 (`0005128`), aceptando la forma real de 001 y leyendo la autoridad del state (D4).
  - **RU-1b** — tras el fix, `begin` real rc 0 (`seq 1`, `body 58c1df54…`); repetir el
    mismo cuerpo → `no_op: true` sin escritura (`evidence/t4/begin-*.json`). Write-ahead
    idempotente sobre datos reales.
  - **RU-2** — **rotación real en el límite natural T3→cierre:** sesión nueva de
    `cdad-orchestrator` (OpenCode 2.0.16, `mofgw/deepseek-v4.1-flash`, sin historial ni
    lectura de archivos, solo `resume`/`reconcile`/`trigger`). Reconstruyó objetivo,
    autoridad y su fuente, las 5 decisiones con su razón, las incertidumbres y la próxima
    acción; **no preguntó nada al usuario**; `reconcile` = `dispatched-unknown` con
    `repeat_effect: false`. **P2 y P3 demostradas en uso real.** Duración ~1 min; máximo
    de contexto reportado: no disponible (`null`).

- **Deuda:** `debt.md` — alta: ninguna. Media: T3-O1 (perfil 200k extrapolado a cualquier
  límite entero), T3-O2 (enteros sin sentido dan señal definitiva), V1/V3 (tokens por paso
  vs acumulados y límite observable no verificados), rollback/replay de head viejo y
  tamper autoconsistente, validadores preexistentes F011/A3, **RU-2a** (adoptar
  `cdad_result receive` en el flujo de despacho). Baja: T3-N1..N7, T2 nits, F2, **RU-2b**
  (el checkpoint no incluye HEAD ni timestamp de emisión; hoy se cubren con `--update`).

- **Limitaciones honestas:**
  - `trigger` es **casi siempre `unknown`**: sin contador y límite de contexto observables
    (V1/V3), el CLI no fabrica un límite y declara `unknowns[]`.
  - `reconcile` está **limitado sin `receive`**: en el modo de despacho actual la salida de
    los roles no pasa por `cdad_result receive`, así que solo puede clasificar
    `dispatched-unknown` (deuda RU-2a).
  - **Rollback/replay de un head viejo y tamper autoconsistente no son detectables** (sin
    firma ni contraste de `seq`), documentado en `continuity.md`.

- **Memory Bank:** `activeContext.md`, `progress.md`, `systemPatterns.md`, ADR-016 y este
  `closure.md` — **pendientes de aprobación del dueño** (borradores del scribe; el
  orquestador materializa).

- **Siguiente:** cierre/integración del **epic-003** (última feature del epic); la
  aprobación estratégica del cierre es del **dueño**.
