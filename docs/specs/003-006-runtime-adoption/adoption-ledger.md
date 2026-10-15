# Adoption ledger — 003-006-runtime-adoption (T4)

Marcadores: `<adopted-root>` = raíz aislada v5 (`~/.cache/cdad-adopted-d958672`, fuera
de las configs de HOME); `<wt>` = worktree desechable del proyecto para el recorrido.
Los runtimes se ejecutaron con el HOME real porque la autenticación vive allí. Escriben ahí
sus propios logs y sesiones, lo que no es instalar CDAD. Las configs de CDAD en HOME
(`~/.claude/agents`, `~/.claude/skills`, `~/.agents/skills`, `~/.config/opencode`) no se
tocaron: sus mtime son 2026-09-17 y 2026-09-29.

## Paso 1 — Re-adopción v5 (P11, parcial)
- `make staging` rc=0; `CDAD_INSTALL_ROOT=<adopted-root> bash install.sh --optimus --force` rc=0
  (`Verify: PASS — 11 cdad agents`); `--check` rc=0 (`Check: PASS (363 artifact groups in sync with staging/skills)`).
- `<adopted-root>/.config/opencode/skills/cdad-cycle/scripts/` = `cdad_continuity.py cdad_guard.py cdad_packet.py cdad_result.py`.
- Activación en `<wt>`: `scripts/cdad-activate.py --project-root <wt> --adopted-root <adopted-root>` rc=0; re-corrida rc=0.
  El hook emitido es `command: <adopted-root>/.claude/cdad-scripts/path-guard.sh implementer`.

## Paso 2 — Identidad por runtime (P4, P5, P6)

| Runtime | Base cargada | Scripts | Agentes | Hook | Veredicto |
|---|---|---|---|---|---|
| OpenCode (`opencode run`, agente `build`) | `<adopted-root>/.config/opencode/skills/cdad-cycle` (devuelta por el runtime) | los 4 | publicados por `prepare` (sin cambio) | n/a | **v5 ✓** (P4) |
| Claude Code 2.1.285 (`claude -p`) | `~/.claude/skills/cdad-cycle` (**global viejo**) | sin verificar (`ls` fuera del directorio de trabajo) | **proyecto ✓**: el subagente orquestador cita "Continuity wiring (contracts in …continuity.md" | **no se ejecutó**: el implementer escribió en `tests/` | **mezcla de versiones ✗** (P5 runtime, P11) |
| Codex (`codex exec`, solo lectura) | catálogo con dos copias: `<wt>/.agents/skills/cdad-cycle` y `~/.agents/skills/cdad-cycle` | los 4 en la de proyecto | sin adaptador (fuera de alcance) | n/a | **ambiguo** (P6): ver sonda dirigida |

### Causas verificadas en Claude Code
- **Skills:** el log de depuración muestra `Loading skills from: … user=~/.claude/skills, project=[<wt>/.claude/skills]`
  y `Loaded 47 unique skills (… user: 18, project: 8 …)`. Cuando el nombre se repite, gana la copia de
  usuario. Desde el proyecto no se puede corregir sin tocar HOME.
- **Hooks:** el log de depuración dice `Skipping frontmatter hooks for agent 'cdad-implementer': the folder its definition file came from is not trusted (source: projectSettings)`.
  La confianza se resuelve sobre la ruta del repositorio principal, aun desde el worktree. Habilitarla es un cambio de seguridad en `~/.claude.json` y le toca al dueño.
- **El guard, con confianza, fallaría cerrado:** corrido a mano, `<adopted-root>/.claude/cdad-scripts/path-guard.sh implementer`
  devuelve rc=2: `cannot classify … invalid choice: 'validate-policy'`. Busca el clasificador en
  `$HOME/.claude/skills/cdad-cycle/scripts/cdad_packet.py`, una copia vieja (`path-guard.sh:134`). Se corrige en la activación (RU-1).

### Sondas dirigidas
- **Claude Code con `--setting-sources project,local`:** el log de depuración da `Loaded 8 unique skills (… user: 0, project: 8 …)`
  y `Skill` devuelve `Base directory for this skill: <wt>/.claude/skills/cdad-cycle`, o sea la v5.
  Esa opción da un camino de despacho sin tocar HOME. No resuelve las sesiones interactivas
  abiertas sin la opción, ni la confianza que necesitan los hooks.
- **Codex, sonda de contenido:** citó la oración de Step 6 que solo existe en v5 (`the CLI is scripts/cdad_result.py`)
  y la ruta leída fue `<wt>/.agents/skills/cdad-cycle/SKILL.md`, así que **usó la copia de proyecto (P6 ✓)**.
  Límite: el catálogo sigue listando también la copia vieja de HOME, y la elección la hace el modelo.

## Paso 3 — RU-1 y verificación del hook emitido (P5, mitad comando)
- `begin` real antes de despachar RU-1 GREEN: rc=0, `seq` inicial, `body 89652deb…` (`evidence/t4/begin-green-005.json`).
  `reconcile` durante el despacho dio `dispatched-unknown`, lo esperado sin receipt.
- RU-1 GREEN `5c09770`. Re-activación de `<wt>`: rc=0. Línea emitida:
  `command: CDAD_PACKET_CLI=<adopted-root>/.claude/skills/cdad-cycle/scripts/cdad_packet.py <adopted-root>/.claude/cdad-scripts/path-guard.sh implementer`.
- La línea, pasada por `bash -c` con `CLAUDE_PROJECT_DIR=<wt>` y el JSON del hook:
  `tests/zz.txt` → rc=2 `CDAD path-guard: implementer may not edit tests (tests/zz.txt is test)`;
  `scripts/zz.py` → rc=0. El clasificador v5 decide bien. Que Claude Code lo ejecute en runtime
  sigue dependiendo de que el dueño marque la carpeta como de confianza.

## Paso 4 — `receive` y continuidad reales (P7, P8, P9)
- `begin` antes de despachar la re-review focal (`review-005`): rc=0, encadenado al checkpoint anterior (`evidence/t4/begin-review-005.json`).
- El FINAL TEXT del reviewer se extrajo byte a byte de la base de datos de OpenCode y se stageó en `.cdad/inbox/` junto a `RESULT.json` y el manifest de cambios (baseline `git:<HEAD al despachar>`, `changes: []`).
- `cdad_result.py receive` (v5): rc=0, `identity/packet/scope_validation: passed`, `semantic_status: pending`, `state_transition_requested: received`.
  **El reintento idéntico dejó el receipt y el stdout byte a byte iguales** (P7). `validate-receipt`: `VALID: receipt`.
- `cdad_continuity.py reconcile`: **`received`**, `repeat_effect: false`, `unknowns: []` (P8; antes era `dispatched-unknown`).
- `materialize` con autorización explícita, create-only, `approval_effect: false`: rc=0. `review-ru1-rereview.md` es idéntico al FINAL TEXT.
- Transición única en el state: paquete `completed` y entrada en `stage_history` con ruta y sha del receipt.
- **`checkpoint` después del receive: rc=1, rechazado** (`evidence/t4/checkpoint-after-ru1-REFUSED.txt`). Mensaje: `split-brain: a checkpoint with the same idempotency key (… packet_id='…review-005', attempt=1) diverges from the head … refusing to overwrite`.
  Es el contrato, no un defecto: la clave es `(execution_id, packet_id, attempt)` y el `begin` de ese paquete ya ocupó la clave.
  **Fricción real:** el checkpoint de límite tiene que llevar la clave del paquete *siguiente*, así que en la práctica el próximo `begin` hace de checkpoint de límite. La referencia no lo dice → deuda T4-CKPT.

## Paso 5 — Rotación en sesión nueva (P9)

### Intento 1: bloqueado por integridad de referencias
- Una sesión nueva de `cdad-orchestrator` (OpenCode, deepseek-v4.1-flash, `rot-003-006-a1`), sin historial,
  limitada a `resume`/`reconcile`/`trigger` de la v5. **Los tres comandos abortaron** con
  `docs/specs/003-006-runtime-adoption/dispatch-ledger.md changed since the checkpoint (expected 63fb39f1…, got 1a7e196d…)`.
- **Bien:** no inventó objetivo ni autoridad, no re-despachó, declaró el re-despacho indeterminado por falta de evidencia
  y preguntó al usuario cómo seguir (`evidence/t4/rotation-1-blocked.md`). Es la conducta fail-closed de P1.
- **Fricción real (deuda T4-REF):** las referencias del checkpoint incluyen documentos vivos (ledgers, debt) que el
  orquestador sigue escribiendo después del `begin`. Cualquier fila nueva invalida la reanudación. Sumado a T4-CKPT
  (no se puede refrescar la cabeza sin la clave de un paquete nuevo), en uso diario la reanudación queda bloqueada salvo
  que el orquestador no escriba nada entre el último `begin` y la rotación. 003-004 RU-2 funcionó porque no hubo escrituras en ese intervalo.

### RU-2 y limpieza del store real
- RU-2 GREEN `abcd4d3`. El orquestador mandó a la papelera el cuerpo huérfano `bodies/2aee8d80….json`, escrito por el checkpoint rechazado de las 02:47:40
  (sha registrado; el orquestador es el único escritor). Con el CLI corregido del repo, `reconcile --packet …review-005` **ya no da split-brain**: ahora falla por T4-REF
  (`dispatch-ledger.md changed since the checkpoint`, `evidence/t4/reconcile-after-cleanup-REF.txt`), lo esperado tras las escrituras posteriores.
- La raíz v5 (`d958672`) no incluye RU-1 ni RU-2: el cierre re-adopta una v6.

### Intento 3: rotación correcta (P9 ✓)
- `begin` de `review-006` (seq 4) y, **sin escrituras intermedias**, sesión nueva `rot-003-006-a3`. `resume` reconstruyó objetivo, autoridad, las 8 decisiones con razón, las incertidumbres y la próxima acción.
  `reconcile review-005` → `already-closed` ("a valid receipt plus a materialization journal exist … no retrabajo") y `reconcile review-006` → `not-started`.
  Conclusión de la sesión: "cero re-despachos; un despacho nuevo (`review-006`)". No hizo falta preguntar al usuario (`evidence/t4/rotation-3-ok.md`).
- Después se despachó `review-006`. Su FINAL TEXT se recibió con `receive` (rc=0, `VALID: receipt`), `reconcile` dio **`received`** y se materializó idéntico en `review-ru2-rereview.md`.
