---
feature_id: 003-006-runtime-adoption
feature_name: Adopción y cableado de las herramientas CDAD por runtime
created_at: 2026-10-07
status: approved
approved_by: orchestrator (HITL delegation epic-003)
approved_at: 2026-10-07
---

# Plan — 003-006-runtime-adoption

> **Versión final** derivada de `architect-draft-001.md` aplicando
> `review-draft-001-decision.md`: BL-1 (re-adopción v5 como primer paso de T4),
> BL-2 (fuera `.claude/settings.json`), R-1..R-8 y N-1..N-3. El plan define el
> **contrato**, nunca el código (`stage-2-specification.md:115-119`); usa el bloque
> canónico `plan-tasks` (`planning-contract-draft.md` §4.1). 4 tareas (máximo del
> encargo).

## Restricciones globales (copia de la spec)

- Repo en español. Tooling Python **stdlib-only**.
- Nunca instalar/modificar CDAD en las configuraciones del HOME real
  (`~/.claude`, `~/.agents`, `~/.config/opencode`); activación **por proyecto**
  hacia la raíz aislada adoptada. Configs de activación **git-ignoradas**.
- La re-adopción (v5) escribe **solo** bajo `~/.cache` (raíz aislada versionada),
  nunca en las configuraciones del HOME real.
- No endurecer permisos; sin push automático. OpenCode 2.0.16 (referencia).
- `receive` no aprueba; el state lo escribe solo el orquestador. Reutilizar
  `cdad_result.py`/`cdad_continuity.py` (sin CLI nuevo).
- Ledger y docs nuevos **sin rutas absolutas locales** (marcadores
  `<adopted-root>`, `<project-root>`).

## 1. Tareas

### T1 — Cableado del descubrimiento en SKILL y referencias
- **Postcondiciones:** P1 (mitad `SKILL.md`), P10.
- **Alcance incluido:** enlazar `references/continuity.md` en la tabla de
  referencias; nombrar `receive`/`begin`/`checkpoint`/`reconcile`/`resume`/
  `trigger` en su paso del ciclo; `classify` declarado fuera. Sin duplicar
  interfaces.
- **Excluido:** el cuerpo operativo del orquestador (T3) y la activación (T2).
- **Archivos:** Modify `skills/cdad-cycle/SKILL.md`;
  Modify `skills/cdad-cycle/references/progress-guards.md` (nota de paso);
  Test `tests/test_003_006_t1_wiring.py`.
- **Dependencias:** ninguna.
- **Validación (focal):** el test afirma que `continuity.md` está enlazada y que
  cada comando aparece en el paso correcto; `classify` declarado fuera.
- **Owner:** RED test-writer; GREEN implementer.

### T2 — Generador de activación por proyecto (determinista, no-clobber, sin HOME)
- **Postcondiciones:** P2, P3, P5 (mitad de unidad: bytes/ruta del hook/ausencia
  de `~/.claude`).
- **Alcance incluido:** `scripts/cdad-activate.py` desde
  `(project_root, adopted_root)`; emisión OpenCode / Claude Code / Codex;
  reescritura determinista del `command:` del guard (R-1); `--dry-run`;
  no-clobber con error si el destino existe y difiere (R-5); identidad de versión
  contra el `.cdad-install-manifest.json` de `A` (R-4); `.gitignore` para
  `.claude/` y `.agents/`. **No se emite `.claude/settings.json`.**
- **Excluido:** adaptador de agentes Codex; hooks CC adicionales; parametrizar el
  guard en `cdad-generate.py` (deuda).
- **Archivos:** Create `scripts/cdad-activate.py`;
  Create `skills/cdad-cycle/references/runtime-adoption.md`;
  Modify `.gitignore`; Test `tests/test_003_006_t2_activation.py`.
- **Validación (focal):** dos corridas → bytes idénticos; **ningún `command:`
  emitido contiene `~/.claude`** y el hook resuelve a
  `<A>/.claude/cdad-scripts/path-guard.sh`; cero escrituras en las configuraciones
  del HOME real (HOME temporal en el test); `git check-ignore` sobre los 3
  directorios; destino existente divergente → error (dry-run lo muestra);
  identidad contra los sha del manifest de `A`.
- **Detener si:** V2 (descubrimiento Codex) no se puede fijar → declarar límite, no
  inventar.
- **Owner:** RED test-writer; GREEN implementer.

### T3 — Adopción de `receive` + continuidad en el cuerpo del orquestador
- **Postcondiciones:** P1 (mitad orquestador), P7, P8, P9.
- **Alcance incluido:** reglas operativas del orquestador (staging + `receive` +
  transición única; `begin`/`checkpoint`/`reconcile`/`resume`); regenerar los
  agentes (OpenCode + Claude Code) desde `sources/`.
- **Excluido:** cambios a `cdad_result.py`/`cdad_continuity.py` (se reutilizan);
  el recorrido real (T4).
- **Archivos:** Modify `sources/roles/orchestrator.md`;
  Regenerate `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`
  (`make agents`); Test `tests/test_003_006_t3_receive_wiring.py`.
- **Dependencias:** T1 (consume el contrato de cableado).
- **Validación (focal):** el agente regenerado nombra `receive`/`begin`/
  `checkpoint`/`reconcile`/`resume`; `reconcile = received` con receipt sintético
  (pytest, sin runtime).
- **Nota (R-3):** `make agents` copia **todos** los `cdad-*.md` de staging
  (`Makefile:17-19`); T3 parte de **staging limpio** y el commit lista solo los
  archivos realmente tocados.
- **Owner:** RED test-writer; GREEN implementer.

### T4 — Re-adopción v5 + recorrido real por runtime + enmienda de cierre del epic (borrador)
- **Postcondiciones:** P4, P5 (mitad runtime), P6, P9 (evidencia), P10, P11, P12.
- **Alcance incluido (en orden):**
  1. **Re-adopción (BL-1, primer paso):** `CDAD_INSTALL_ROOT=$HOME/.cache/cdad-adopted-<rev>
     bash install.sh --optimus` del commit de cierre de T1–T3 (staging regenerado);
     fila **v5** en `docs/runtime-adopted-version.md` (tabla vigente + historial);
     verificación de consumidor; **repunte de la raíz adoptada** en la activación
     (regenerar con el generador de T2). Límite declarado: escribe bajo `~/.cache`,
     nunca en las configuraciones del HOME real.
  2. **Guion de aceptación no interactivo (R-2):** `claude -p` / `codex exec` con
     flags no interactivos; se ejecutan con **HOME temporal** (`HOME=<raíz
     desechable>`) cuando sea viable y, si la autenticación lo impide, se declara
     en el ledger. Se declara que `claude`/`codex` escriben sus propios
     logs/sesiones bajo HOME — eso **no** instala ni modifica CDAD.
  3. **`receive` real** de la salida de un rol con `reconcile = received`.
  4. **Reconstrucción** con `resume` en sesión nueva, sin re-preguntar (R-7: las
     reglas nuevas se aplican desde una sesión nueva de orquestador tras la
     re-adopción, o leídas del repo; queda en el ledger).
  5. **Ledger anonimizado (R-8)** + **borrador de enmienda de cierre del epic**
     para el dueño.
- **Excluido:** benchmark; comparación A/B; forzar la feature para repetirla;
  escribir en `~/.claude`, `~/.agents` o `~/.config/opencode`.
- **Archivos:** Create `docs/specs/003-006-runtime-adoption/adoption-ledger.md`;
  Modify `docs/runtime-adopted-version.md` (fila v5);
  Create `docs/epics/epic-003-context-efficiency/closure-amendment-draft.md`.
- **Registro obligatorio del ledger:** `runtime | base cargada (file:line) |
  receive rc/receipt | reconcile | resume | límites | pendiente` (rutas con
  marcadores `<adopted-root>`/`<project-root>`).
- **Validación (observable):** la sesión nueva reporta la base adoptada y los 4
  scripts; `reconcile = received`; `resume` no re-pregunta; v5 registrada.
- **Dependencias:** T1, T2, T3 verdes.
- **Owner:** orquestador.

## 2. Estimaciones (rango, método, incertidumbre)

- Rango: **bajo–medio** (T1, T3), **medio** (T2), **medio** (T4).
  Método: comparación cualitativa con 003-002/003-004. Incertidumbre **alta** por
  V1/V2 (descubrimiento CC/Codex) y por la autenticación de los runtimes en T4.

## 3. Incertidumbres / replanificación

- Si V1/V2 no se resuelven, reacotar con el dueño antes de expandir
  infraestructura; no asumir APIs (V1–V5).
- Si T2 crece más allá de su mini-ciclo, dividir (OpenCode/CC vs Codex).
- Si T4 no puede ejecutar los runtimes con HOME temporal, se declara el límite en
  el ledger (P6) sin bloquear el resto del recorrido.

## 4. Self-review (architect, antes de cerrar Stage 2)

1. **Cobertura spec↔plan:** P1→T1+T3; P2→T2; P3→T2; P4→T4; P5→T2+T4; P6→T4;
   P7→T3; P8→T3; P9→T3+T4; P10→T1+T4; P11→T4; P12→T4. Ninguna P sin tarea; ninguna
   tarea sin P.
2. **Placeholders:** sin "TBD"/"TODO"/"similar a T N"; sin manejo vago.
3. **Consistencia de firmas:** `cdad-activate.py --project-root/--adopted-root/
   --runtime/--dry-run` idéntico en spec §2.2, T2 y el bloque `plan-tasks`.

```plan-tasks
{
  "validation_strategy": "focales por unidad (pytest, env -u TMPDIR) con HOME temporal en los tests de activación; suite completa y validadores del repo al cierre; re-adopción v5 en raíz aislada bajo ~/.cache; recorrido real por runtime no interactivo con HOME temporal cuando sea viable; ledger anonimizado; sin escribir en las configuraciones del HOME real ni afectar la sesión orquestadora",
  "tasks": [
    {"id": "T1", "produce": [{"artifact": "wiring-ciclo-skill", "contract": "n/a (documentación)"}], "consume": [], "depends_on": [], "parallel": [], "files": ["skills/cdad-cycle/SKILL.md", "skills/cdad-cycle/references/progress-guards.md", "tests/test_003_006_t1_wiring.py"], "focal_tests": ["tests/test_003_006_t1_wiring.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T2", "produce": [{"artifact": "cdad-activate", "contract": "activación-por-proyecto-v1"}], "consume": [], "depends_on": [], "parallel": [], "files": ["scripts/cdad-activate.py", "skills/cdad-cycle/references/runtime-adoption.md", ".gitignore", "tests/test_003_006_t2_activation.py"], "focal_tests": ["tests/test_003_006_t2_activation.py"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T3", "produce": [{"artifact": "orquestador-receive-continuidad", "contract": "n/a (reglas operativas)"}], "consume": [{"artifact": "wiring-ciclo-skill", "contract": "n/a (documentación)", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["sources/roles/orchestrator.md", "agents/cdad-orchestrator.md", "agents/claude-code/cdad-orchestrator.md", "tests/test_003_006_t3_receive_wiring.py"], "focal_tests": ["tests/test_003_006_t3_receive_wiring.py"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T4", "produce": [{"artifact": "adoption-ledger", "contract": "n/a"}, {"artifact": "runtime-adopted-version-v5", "contract": "n/a"}, {"artifact": "closure-amendment-draft", "contract": "n/a"}], "consume": [{"artifact": "cdad-activate", "contract": "activación-por-proyecto-v1", "producer": "T2"}, {"artifact": "orquestador-receive-continuidad", "contract": "n/a (reglas operativas)", "producer": "T3"}], "depends_on": ["T1", "T2", "T3"], "parallel": [], "files": ["docs/specs/003-006-runtime-adoption/adoption-ledger.md", "docs/runtime-adopted-version.md", "docs/epics/epic-003-context-efficiency/closure-amendment-draft.md"], "observable_checks": ["el commit de cierre de T1-T3 queda instalado en una raíz aislada nueva bajo ~/.cache y registrado como v5 con verificación de consumidor", "una sesión/subagente nuevo por runtime reporta la base adoptada y los 4 scripts", "un receive real produce receipt y reconcile clasifica received", "resume en sesión nueva reconstruye objetivo/decisiones/autoridad/next_action sin re-preguntar", "el adoption-ledger.md no contiene rutas absolutas locales"], "regressions": ["tests/validate-consistency.sh", "tests/validate-odoo-specialization.sh"], "integration_gate": "@validation_strategy", "owner": "orquestador"}
  ]
}
```
