## Evidencia (comandos exactos + salida)

| # | Comando | Resultado |
|---|---|---|
| E1 | `git log --oneline -15` / `git diff --stat 00dd557..6c03533` | diff = `cdad_continuity.py` (+198/−7), `continuity.md` (nuevo, 70 líneas), `tests/test_003_004_t3_trigger.py` (nuevo, RED ya existente), ledger, review-t2-rereview, `.cdad-state.json` |
| E2 | `git diff da60093..6c03533 -- tests/` | **salida vacía** → tests intactos entre RED y GREEN (sin edición de tests) |
| E3 | Verificación de código: `cdad_guard.py::_collect_attempts` (líneas 612–641) vs `cdad_continuity.py::_collect_guard_attempts` (líneas 375+) | **idénticos lógicamente de forma línea por línea** (mismo evento/paquete/filtro de errores clavados, libras, orden). Invariante 5 / "reutiliza, no redefine" verdadero por lectura |
| E4 | `python3 -m unittest discover -s tests -p "test_003_004_*.py"` -v `< /dev/null` (foreground; desde el árbol 6c03533→b2e076b) | `Ran 32 tests in 22.116s — OK` (focos T1–T3 completos, stdin cerrado, nunca en segundo plano) |
| E5 | `python3 -m unittest tests.test_003_004_t3_trigger -v` (forma de invocación alternativa) | `ModuleNotFoundError: No module named 'test_004_002_t2_bootstrap'` (ver hallazgo N6) |
| E6 | Sondas manuales sobre un proyecto sintético en `/tmp/opencode/probe-t3`, stdin cerrado (`subprocess.run(..., stdin=DEVNULL)`): contador booleano; enteros negativos (used=−5, limit=−10); instantánea ok (source="step-finish"); head manipulado (`body_sha256="0"*64`) | bool → `unknown` + `unknowns[]: ["context_used_tokens: no integer counter reported (got True)"]`, nulos ✓; negativos → `rotate` con `profile.rotate_at=−50010` (ver O2); ok → `ok`, `context_source="step-finish"`, `profile` completo ✓; head manipulado → **rc 1** fail-closed con delta exacto, sin stdout fabricado ✓ |
| E7 | Verificación de correspondencia doc↔código de `continuity.md` | `no-checkpoint` rc 0 (`_run_resume:972`), `--role`→`docs/cdad-policy.json` (`POLICY_REL_PATH:96`), `_detect_split_brain` existe (`:612`), `begin` sin operación rc 0 / `expired` no escribe checkpoint (`_require_current_authority:348`), `reconcile` desconocido-no-fabricado (`_run_reconcile:721` + señales): **todas las afirmaciones verificables en el doc corresponden al código** |

## Hallazgos por eje

### Correctness (P6/P4/D5 — focos 1 y 2)

Los números tienen fuentes trazables: `context_used_tokens`/`context_limit` se leen **solo** del snapshot congelado `update.budget` en la cabeza (plan T3: "snapshot de presupuesto embebido en el checkpoint, `budget.source`"), propagado como `context_source`; CONSTANTES DEL PERFIL desde la planificación T3 "perfil 200k/150k/120k" (plan:78). No existe la conversión de bytes a tokens en ningún lugar (test "bytes-no-son-tokens" + probe). El presupuesto de intentos se lee del durable de 003 en `.cdad/executions/<id>/guards/**` con el mismo filtro que `cdad_guard budget`, con `source`, y `trigger` no escribe nada (tests de snapshot árbol + ingestas de guard de superficie real + lectura de código). Sin señal → siempre `unknown`+nulls+`unknowns[]` (subtest a–e todos verdes).

### Seguridad / arquitectura / legibilidad / rendimiento

- **Foco 3 (read-only):** `_run_trigger` no contiene ninguna escritura; `_frozen_budget` solo lee/verifica; el corte C `_safe_segment` del paquete ocurre ANTES de cualquier lectura (correcto: fail-closed que nombra el campo, test `..`/`../../x`/`a/b` → rc≠0 con la tienda intacta). ✓
- **Foco 4 (continuity.md):** exacto respecto al código (superficie, rc, límites — E7); la columna "No aplica" con "casi siempre unknown" es honesta respecto a V1/V3 y le dice al orchestrator cuándo girar en el límite natural de la tarea. Útil y sin fabricaciones.

## Hallazgos

**O1 — Optional/Consider · Bucket: m.** El perfil se extrapola a cualquier límite entero, no solo al 200k declarado. `PROFILE_RESERVE=50_000`/`PROFILE_PREPARE_AT=120_000` (cdad_continuity.py:87-89) se aplican a cualquier `context_limit` entero: con límite=250000 el código rota a 200000, mientras que la planificación T3 declara la terna "200k/150k/120k" (que solo ancla rotate_at=150000 **para** 200000); con límite<120000 el `prepare_at` fijo queda sobre el propio límite. Sonda: la extrapoolación es transparente (`profile` viaja en el envelope con límite/reserva/preparar/rotar) y D5 lo permite como señal, pero es una regla sin fuente para límites ≠200k (invariante 2 "ningún número sin fuente" se aplica a las CONSTANTES del perfil, no solo a los datos). Cierre sugerido: nombrar el perfil en el envelope (ej. `profile.name="200k"`) o documentar en `continuity.md` la regla de extrapoolación reservada.

**O2 — Optional/Consider · Bucket: m.** Enterouts de rango sin sentido producen una señal definitiva. Sonda E6: `used=-5, limit=-10` → `trigger: rotate`, `profile.rotate_at=-50010`. P6 requiere enteros (condición necesaria cumplida) pero invariante 2 en espíritu: datos basura presentados como señal usable sin ninguna bandera en `unknowns[]`. Cierre sugerido: `limit<=0` (y opcionalmente `used<0` o `used>limit` de forma grotesca) → `unknown` con `unknowns[]` que nombre la anomalía. No es límite duro fabricado — es menos severo que eso.

**N1 — Nit · Bucket: l.** `--runtime` se analiza y nunca se usa (cdad_continuity.py:1051): sin efecto ni validación. Está en la firma §3 (V6 lo fijó así en RED), pero un consumidor podría creer que cambia el comportamiento del runtime.

**N2 — Nit · Bucket: l.** El envelope de `trigger` no se auto-identifica como `trigger-v1`: `begin` lleva `"checkpoint": "continuity-checkpoint-v1"` y `reconcile` lleva `"reconcile": "reconcile-v1"`, pero el envelope de trigger no tiene clave de nombre de contrato. El RED (que fijó V6) tampoco lo declaró, así que GREEN siguió el RED — divergencia de uniformidad entre contratos hermanos (`continuity-v1` contrato interno común), no defecto de comportamiento.

**N3 — Nit · Bucket: l.** `budget` en el envelope siempre es un dict (nunca null), mientras que el RED declaró `{…} | null` (test docstring:44-53). Divergencia inofensiva de la superficie RED-declarada: con 0 guards reporta `{source, consumed:0, attempts:[]}` honesto.

**N4 — Nit · Bucket: l.** `begin`/`checkpoint` congelan `budget` sin validación de forma: un contador booleano se freezing feliz (sonda E6: begin rc 0 con `context_used_tokens: true`); se detecta downstream solo porque `_is_int` lo rechaza en trigger (honesto, pero el error de autoría viaja inmutable). La validación de presupuesto en tiempo de escritura fallaría antes, como `_require_content_fields` hace para las decisiones.

**N5 — Nit · Bucket: l.** `continuity.md:50-51` agrupa `--max-bytes` tras la frase "reconcile/resume/trigger son read-only…", pero `trigger` no acepta `--max-bytes` (solo begin/checkpoint/resume). Legible con esfuerzo; una coma separadora de cláusula independiente lo resolvería.

**N6 — Nit/FYI · Bucket: l.** La focal no es ejecutable con `python3 -m unittest tests.test_003_004_t3_trigger` (E5 falla con ModuleNotFoundError por `from test_004_002_t2_bootstrap import tree_snapshot`); solo corre con `discover -s tests` (E4, la forma de suite de facto). Bajo declarado en la referencia de ejecución del propio archivo.

**N7 — Nit · Bucket: l.** La conducta tamper de `trigger` (rc≠0 fail-closed, sonda E6) no está cubierta por ningún test ni declarada en los `Known limits` de `continuity.md` — la conducta es la correcta (consistente con P1), solo está sin documentar ni probar. Ídem: ningún subtest cubre contador booleano (`_is_int` lo rechaza; solo se prueba float).

## Bloqueantes

Ninguno. Los cuatro focos del orchestrator cierran: (1) cada número tiene fuente declarada (snapshot congelado con `context_source`, perfil trazado a plan T3:78); (2) el presupuesto se lee del durable de 003 con el filtro idéntico al de `cdad_guard budget` (invariante 5) y no se reinicia (criterio 6, test con superficie real `cdad_guard record`); (3) trigger es solo lectura verificado por árbol-snapshot y por lectura de código; (4) `continuity.md` es exacta respecto a/comandos/rc/límites/código (E7) y declara honestamente el "casi siempre unknown". RED→GREEN limpio (tests intactos, E2), 32/32 focos verdes con stdin cerrado (E4), proporcionalidad MVP respetada.

## Abstenciones

- **V1** (tokens de `step-finish`: ¿por paso o acumulados?) — no verificable en esta sesión; el trigger confía en el snapshot que el propio orchestrator recibe en `--update`. Deuda declarada, no defecto.
- **V3** (¿existe un límite duro de contexto observable en OpenCode/Claude Code?) — no observado; `continuity.md` lo refleja con "casi siempre unknown". No pude verificación de runtimes reales desde esta sesión.
- No puedo verificar la ejecución de la suite completa post-GREEN reportada por el implementador (519 tests verdes, ledger:20): solo ejecuté las focales T1–T3 (alcance del packet). No lo tomo como verificado ni como falso.
