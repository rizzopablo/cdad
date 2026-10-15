# Review T3 — `receive` + continuidad en el cuerpo del orquestador (diff `85e30aa..d958672`)

**Packet:** `003-006-runtime-adoption-reviewer-review-004` · **Contrato:** `docs/specs/003-006-runtime-adoption/spec.md` (sha256 verificado = `dc485e80…d7cb7` ✓ coincide con el packet) · **Lectura:** solo lectura, write_scope vacío respetado (ningún archivo modificado).

## Evidencia (comandos exactos + salida)

| Comando | Resultado |
|---|---|
| `git log --oneline 85e30aa..d958672` | `d958672` (feat T3 GREEN), `3f8633c` (test: coherencia solo pasajes de cableado) — **2 commits, no 3** |
| `git diff --stat 85e30aa..d958672` | 5 archivos: `agents/cdad-orchestrator.md` (+15), `agents/claude-code/cdad-orchestrator.md` (+15), `skills/cdad-cycle/SKILL.md` (+1/−1), `sources/roles/orchestrator.md` (+15), `tests/test_003_006_t3_receive_wiring.py` (+39/−4) |
| `sha256sum docs/specs/003-006-runtime-adoption/spec.md` | `dc485e80aa86b545c75c86f71a3fa590321c1ca6a66221e1115c69b75a7d7cb7` = contract ✓ |
| `python3 tests/test_003_006_t3_receive_wiring.py -v` | **15/15 OK** (2.331 s) — incluye P7/P8 con los CLIs REALES (`cdad_result.py`, `cdad_continuity.py`) sobre tmpdir |
| `make validate` | **141 PASS / 2 FAIL** — F011: `scripts/validate-subagents.sh` (drift contra HOME) + `tests/validate-odoo-specialization.sh` (A3: patrones sensibles en `docs/specs/004-003-*` y `test_role_packets.py`) |
| `git diff d958672..HEAD --stat` | Solo ledger + state (`14f78ba`, chore) — el árbol revisado no diverge del objeto revisado |

**Modified files (delta del diff):** los 5 listados arriba. Verificación del punto (4) del orquestador: entre `agents/` solo cambiaron los **dos** agentes del orquestador (diffstat confirma; ningún otro agente tocado). Los cambios a `sources/roles/orchestrator.md` y `SKILL.md` están en el plan T3 (`plan.md:155`) el primero; `SKILL.md` **no** está en la lista de archivos de T3 pero su única línea tocada es la F1, asignada a T3 por `review-t1-decision.md:5-7` ("se corrige en T3… El RED de T3 lo cubre con una aserción") y por el objetivo de esta revisión — cadena de autoridad documentada, FYI-2 abajo.

## Veredicto por eje

### (1) Ejecutabilidad por sesión nueva — Correctness: OK

`agents/cdad-orchestrator.md:71-84` (idéntico en `agents/claude-code/cdad-orchestrator.md:76-89` y `sources/roles/orchestrator.md:77-90`): la sesión nueva sabe **dónde stagear** (`.cdad/inbox` con `RESULT.json`), **qué script** (`cdad_result.py` para re-entry, `cdad_continuity.py` para continuidad), y el **orden** es inferible de los triggers declarados: `begin` "before dispatching" (:73) → despacho → `receive` (:80-82) → `checkpoint` al cierre de límite (:74); `reconcile` antes de retry/resume (:75); `resume` en sesión nueva (:76). Las flags se delegan a las references por diseño ("never duplicated here", :72/:79) — coherente con §2.1 "sin duplicar interfaces" y con P1, que solo exige *nombrar* en el paso correspondiente. Los tests `wired()` verifican exactamente ese contrato observable.

### (2) Contradicciones con `references/re-entry.md` / `references/continuity.md` — ninguna

- Staging mecánico, receipt `pending`, único escritor del state: coincide con `re-entry.md:25-63` (RECEIVE/RECONCILE/STATE) e I5.
- `begin`/`checkpoint`/`reconcile`/`resume` con sus disparadores: coincide con la tabla `continuity.md:14-20`. `trigger`/`classify` no contradicen (ver O-2 sobre su omisión en el cuerpo).

### (3) Ajustes del test — justificados, debilitamiento unidireccional

- **`3f8633c` (strip de frontmatter + banner del generador, tests:116-149):** el defecto era real (ledger #18: el banner fijo del generador contiene `start/resume/advance`; sin el strip la coherencia es imposible pasando solo por la fuente — el generador sobreescribe `agents/`). Dirección del debilitamiento verificada adversarialmente: `grep -n "resume/advance"` muestra que la frase existe **solo** en los agentes (frontmatter :2/:3 y párrafo introductorio :9/:14), **no** en `sources/roles/orchestrator.md`. Por tanto ninguna unidad de cableado de la fuente puede ser eliminada por `strip_banner_units`; una unidad de cableado del agente que la contuviera sería eliminada del lado agente → `missing`/`divergent` → fallo (dirección **false-fail**, no false-pass). El exclusion es mínima en el sentido que importa: no puede enmascarar cableado ausente en la fuente.
- **`3efe069` (NO_DUP_FLAGS acotado): NO está en el rango** — ver FYI-1.

## Hallazgos

### Bloqueantes

Ninguno.

### Opcionales

**O-1 · El paso `receive` del cuerpo omite el paso MATERIALIZE del protocolo de re-entry.**
- **Verdict: OPTIONAL · Bucket: m · Severity: Nit/Consider**
- `agents/cdad-orchestrator.md:80-83` (+ espejos en `agents/claude-code/cdad-orchestrator.md:87-90`, `sources/roles/orchestrator.md:86-89`): el bullet comprime staging → receive → validar receipt → transición única, pero **no nombra `materialize`** (paso 3 de `re-entry.md:51-56`, con autorización explícita y target CAS/create-only). `SKILL.md:278` sí lo nombra ("Materialize and `receive`…"), y el cuerpo remite el detalle a `re-entry.md`, así que una sesión nueva que cargue la reference lo ejecuta. Pero la regla operativa del cuerpo, leída *tal cual* sin cargar la reference, produce un rol recibido sin materializar su output canónico (p.ej. `review.md` nunca llega a `docs/specs/`).
- Sugerencia: agregar al bloque re-entry un bullet `- materialize — copy received parts to their canonical targets with explicit authorization` o mencionarlo dentro del bullet `receive`. 3 líneas, mismo estilo.

**O-2 · P1: "trigger se declara advisory y classify fuera" no aparece en el cuerpo del orquestador.**
- **Verdict: OPTIONAL · Bucket: m · Severity: Nit**
- `grep -n "trigger|classify"` sobre los tres cuerpos del orquestador = 0 resultados. Ambos se declaran en `skills/cdad-cycle/SKILL.md:279` (Step 6) y P10 los cubre; la frase de P1 es ambigua sobre si la declaración debe vivir en el cuerpo o en el cableado del ciclo. Lectura indulgente satisfecha; lectura literal del cuerpo, no.
- Sugerencia: decidir explícitamente (nota de 2 líneas en el spec o una línea advisory/outer en el bloque de wiring del cuerpo). No re-trabajar código.

**O-3 · `BANNER_PHRASE` es más ancho que el banner real.**
- **Verdict: OPTIONAL · Bucket: l · Severity: Nit**
- `tests/test_003_006_t3_receive_wiring.py:121,134-142`: cualquier párrafo que contenga `start/resume/advance` se excluye de la coherencia para siempre. Hoy es seguro (la fuente no contiene la frase — verificado); si mañana un párrafo de cableado legítimo de la fuente la incluyera, se excluiría silenciosamente de la comparación. Dirección actual es false-fail, pero es deuda latente de false-pass.
- Sugerencia: anclar el match a la oración exacta del banner (prefijo "You are the **orchestrator**…" o el patrón completo del generador) en lugar de la frase suelta.

**O-4 · Tolerancias de keywords flojas en `wired()`.**
- **Verdict: OPTIONAL · Bucket: l · Severity: Nit**
- `tests/…:217-218` ("stage" como substring también matchea "staging"/"stages") y `tests/…:255-260` ("transición" sola satisface "transición ÚNICA"). Son aserciones de existencia sobre contenido real presente (`agents/cdad-orchestrator.md:80-83` dice literalmente "single state transition"), así que el riesgo de false-pass es teórico; no debilitan lo que hoy se verifica.

### FYI

**FYI-1 · La nota del orquestador es imprecisa sobre el rango:** `85e30aa..d958672` contiene **un solo** ajuste del test-writer (`3f8633c`). `3efe069` (NO_DUP_FLAGS) es **anterior** a `85e30aa` (es parte del estado RED ya revisado; `git log` lo confirma). No cambia el veredicto; se señala para que el registro del ciclo cite el rango correcto.

**FYI-2 · `skills/cdad-cycle/SKILL.md` no está en `files` de T3 (`plan.md:155`):** su edición (1 línea) está autorizada por `review-t1-decision.md:5-7` (F1 → "se corrige en T3") y por el objetivo de esta revisión. Cadena decisión→tarea documentada; sugerencia menor: que la decisión quede referenciada en el plan o ledger para trazabilidad (ya lo está en dispatch-ledger #6, aceptable).

**FYI-3 · `make validate` = 141/2:** ambos fallos son **preexistentes** (ledger #10, entrada del T2 GREEN, fecha 2026-10-08 previa a este diff: "Validadores 141/2: F011 + A3 … preexistente → deuda"). El drift de F011 lista **todos** los agentes (no solo los dos cambiados aquí), consistente con el estado pre-adopción que T4 resuelve (P4/P11; I1 prohíbe escribir en HOME). No es regresión nueva del diff — criterio de aceptación 1 no violado por T3.

## Abstentions

- **Suite completa (563 tests):** no re-ejecutada por esta revisión (solo focal 15/15 + `make validate`). El "563 passed (802 s)" es la aseveración del ledger #20; el alcance proporcional para un diff de documentación + test no lo exige, pero no lo confirmo por medición propia.
- **Preexistencia exacta de los 2 fallos de `make validate` en el commit `85e30aa`:** verificada indirectamente por el ledger #10 (registrado antes del diff); no re-ejecutada sobre checkout limpio de `85e30aa` (hubiera requerido worktree, escritura fuera de write_scope vacío).
- **Consumo real del wiring por un runtime en vivo** (que un subagente OpenCode/Claude Code nuevo ejecute begin→despacho→receive→checkpoint sin fricción): es el rehearsal de T4 (P4, P11, recorrido real); indocumentado aquí no es juzgable desde los artefactos.

## Resumen

**Veredicto: PASS — 0 bloqueantes, 4 opcionales (O-1…O-4), 3 abstenciones.** El cableado del orquestador es ejecutable por sesión nueva tal como P1/§2.1/§2.3/§2.4 lo contratan, no contradice `re-entry.md` ni `continuity.md`, los ajustes del test debilitan solo hacia false-fail, y el diff respeta el alcance declarado (2 agentes + fuente + F1 en SKILL.md + test focal).
