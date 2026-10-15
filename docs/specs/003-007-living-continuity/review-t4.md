Evidence gathering is complete. Full review report follows.

---

# Review T4 (P10) — 003-007-living-continuity

**Packet:** `003-007-living-continuity-reviewer-review-003` · role: reviewer (read-only, write_scope = ∅) · contract: `docs/specs/003-007-living-continuity/spec.md` (sha256 `3b4e8c4a…`, verificado contra el árbol: ✅ coincide)

**Objeto revisado:** diff `86bbb87..1f5fdac` (RED `bc96fc4` + chores `a87c373`/`aadb11b` + GREEN `1f5fdac`), contra spec.md (P10), plan.md (T4), discovery-probe-decision.md (punto d) y review-t2-decision.md (R-1, O-1c).

## Evidencia (comandos exactos y salidas)

| # | Comando | Resultado |
|---|---|---|
| 1 | `git diff 86bbb87..1f5fdac --stat` | 7 archivos: `sources/roles/orchestrator.md` (+27/−), `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`, `skills/cdad-cycle/references/continuity.md`, `tests/test_003_007_t4_atomic_unit_rule.py` (443 líneas nuevas), `docs/.cdad-state.json`, `dispatch-ledger.md` |
| 2 | `git show bc96fc4 --stat` | RED = **solo el test** (TDD limpio; cero implementación en el RED) |
| 3 | Worktree en `bc96fc4`: `env -u TMPDIR python3 -m pytest -q tests/test_003_007_t4_atomic_unit_rule.py < /dev/null` | **7 failed, 3 passed** — RED real, todos `AssertionError` por texto ausente/presente (sin ImportError ni sintaxis), y los 3 guards que pasan hoy coinciden con lo declarado en el docstring del test |
| 4 | Gate en HEAD: `env -u TMPDIR python3 -m pytest -q tests/test_003_007_t4_atomic_unit_rule.py tests/test_003_006_t3_receive_wiring.py < /dev/null` | **25 passed in 2.89s** |
| 5 | Mutación (worktree en `1f5fdac`): revertir la regla al texto viejo + borrar los bullets `living`/`contract` → mismo pytest | **4 failed**: `test_p10a_guard_old_parenthetical_removed`, `test_p10a_rule_expresses_single_dispatchable_unit`, `test_p10b_living_class_declared_in_wiring`, `test_p10_coherence_source_and_regenerated_agents` |
| 6 | Worktree en `82e9b86`: `make agents` → `git status --porcelain` | **salida vacía** — regeneración idempotente; los agentes commiteados en `1f5fdac` son byte-coherentes con la fuente vía el pipeline real |
| 7 | `bash tests/validate-consistency.sh` | 141 PASS / **2 FAIL** (F011, A3) |

## Verificación de los 6 puntos del orquestador

**1. El texto nuevo de la regla conserva lo que protegía la vieja** — ✅ (`sources/roles/orchestrator.md:69-77`, espejado en ambos agentes):
- "never two sub-phases in one invocation" conserva la prohibición de agrupar (mutación A la detecta).
- "each postcondition is traced to at least one test" conserva la trazabilidad test↔postcondición (guard `test_p10a_rule_requires_a_test_per_postcondition`).
- "one scoped, reviewable diff" conserva el diff revisable (guard `test_p10a_rule_requires_a_scoped_reviewable_diff`).
- **No abre puerta a encargos sin límite:** la unidad queda acotada a "one task of the plan or one TDD sub-phase" — es un límite de unidad, no de tamaño de postcondición, exactamente lo que D9/R-4 disponen; y la línea 77 acota el ejemplo ("each dispatch is its own unit, with its own diff").

**2. Clases living/contract del wiring** — ✅ coherentes con `continuity.md:70-77,111-113` y con el código: `living` = ledgers/debt.md/Memory Bank/borradores de cierre-enmienda (enumera idéntico a continuity.md); `contract` = spec/plan aprobados + `docs/cdad-policy.json` + state con `fields` (`hitl_delegation`,`approver`,`execution`) — coincide con D1 y con `_state_authority` (que solo consume esos campos estructurales). No copia flags del CLI (no aparece `--update.references[]` ni `--max-bytes`): es declaración conceptual + puntero estricto a la sección de clases de continuity.md, forma sancionada por BL-1/P10.

**3. "resume read-only, primer paso"** — ✅ verificado en el código: `_run_resume` (cdad_continuity.py:1229-1325), `_run_reconcile` (:994-1063) y `_run_trigger` (:1154-1215) terminan en `_emit()` (stdout) y no contienen ninguna llamada de escritura (`_write_synced` solo en `_run_write`). El help del parser ya rotulaba `reconcile`/`trigger` "read-only"; el wiring ahora lo declara y añade `resume`. "Primer paso" es una directiva de procedimiento del orquestador (punto d), coherente con el wiring — el código no puede imponer orden de invocación; no hay contradicción con otras reglas del rol.

**4. make agents** — ✅ doble verificación: (a) el diff solo toca los dos agentes orquestador (ningún otro agente cambió); (b) `make agents` en worktree de `82e9b86` produce **cero diff** (los agentes de `1f5fdac` = regeneración actual).

**5. Los tests no son triviales ni sobre-especifican** — ✅ con matiz: la mutación A (regresión real del texto) derriba 4 tests, incluyendo el guard de coherencia. Los matchers son tolerantes a redacción (párrafos unidos, variantes ES/EN, anclas múltiples `dispatchable|atomic task|encargo|packet/handoff carries`; si el párrafo de regla desaparece, falla cerrado con "NO tiene párrafo de regla identificable"). El test del ejemplo D9 exige los literales `RED`/`GREEN` — pero ese ejemplo es texto mandado por D9, así que no es sobre-especificación.

**6. continuity.md (R-1, O-1c)** — ✅ R-1: "no-op … **while that `begin` is still the head**; re-running it after an append to its own key fails closed and writes nothing — recovering that no-op is the `T2-R1` debt" — coincide con el código (`_run_write`: misma clave + cuerpo idéntico → no-op solo si el head es ese body; comando `begin` divergente → `ContinuityError` antes de escribir). ✅ O-1c: el texto de huérfanos ahora cubre "the current writer's own orphans: a crash between the two fsyncs" — real: `_run_write` hace exactamente dos `_write_synced` (body, head), un crash intermedio deja body con `record: "checkpoint"` que ningún head referencia.

## Findings

### F-1 · El texto nuevo de continuity.md perdió el no-op del `checkpoint` idéntico (P6)
- **Location:** `skills/cdad-cycle/references/continuity.md:46-51` (commit `1f5fdac`)
- **Rationale:** El párrafo viejo decía "**An identical write** (same `(execution_id, packet_id, attempt)` and same canonical body) is a successful no-op" — cubría `begin` **y** `checkpoint`. El reemplazo por R-1 dice solo "A `begin` re-executed … is a successful no-op". El no-op de un `checkpoint` re-ejecutado con cuerpo idéntico (postcondición **P6** del spec: "un `checkpoint` re-ejecutado con cuerpo idéntico es no-op") quedó **sin declaración en continuity.md** (`grep "identical\|idempot"` → 0 hits en todo el archivo). El comportamiento del código está intacto (`_run_write` devuelve no-op para body idéntico sin importar el comando), pero el lector de continuity.md solo ve "a divergent `checkpoint` appends" y puede inferir mal el caso idéntico. Es una regresión de documentación introducida en la misma edición del párrafo que T4 estaba corrigiendo.
- **Cierre verificable:** re-agregar una cláusula de una línea al párrafo (:46-51), p. ej. "the same holds for an identical re-executed `checkpoint` (no-op, P6)", y re-render de `make agents` si el bloque toca la fuente del rol (no la toca: continuity.md no se renderiza a agentes → solo editar continuity.md).
- **Verdict: OPTIONAL** · **Bucket: m** · **Severity: Required** (debe cerrarse antes del cierre del feature; no bloquea el gate T4)

### F-2 · Señal `rule-plan-task` = `r"plan"` es un no-op como discriminador
- **Location:** `tests/test_003_007_t4_atomic_unit_rule.py:150`
- **Rationale:** Como predicado de presencia, "plan" aparece en casi cualquier párrafo de regla; no discrimina nada. Mitigado: solo se usa en el test de coherencia (simétrico fuente↔agente, así que no puede dar falsa divergencia) y los tests fuertes usan patrones específicos (`test_p10a_rule_expresses_single_dispatchable_unit` usa `plan…task|task…plan`).
- **Verdict: OPTIONAL** · **Bucket: l** · **Severity: Nit**

### F-3 · Validadores F011/A3 fallan (preexistente, causa ambiental confirmada)
- **Location:** `tests/validate-consistency.sh` → `scripts/validate-subagents.sh` → `install.sh --check` (rc=1)
- **Rationale:** La causa es **drift de las copias instaladas en el home** (`~/.claude/`, `~/.config/opencode/`: schemas faltantes, agentes "differs"), no contenido del repo — T4 no tocó `install.sh` ni schemas, y spec §5.10 los declara deuda preexistente. Sin regresión atribuible al diff.
- **Verdict: OPTIONAL** (nada que hacer en T4; queda en la deuda declarada) · **Bucket: m**

## Abstentions
1. **Suite completa (599 passed):** reportada por el implementer; el gate del packet me ordena no repetirla. No la confirmé de forma independiente — evidencia de segunda mano, declarada como tal.
2. **Sonda 2** (repetición del prompt del punto d tras T4, discovery-probe-decision.md:19-20): observable de cierre del feature, no del diff de T4; no evaluada.
3. **No verifiqué exhaustivamente cada regex de `SIGNALS` contra redacciones futuras** (falsos negativos ante reformulaciones profundas del texto D9); el diseño fail-closed del ancla de párrafo mitiga, pero la tolerancia exacta a reformulación no es demostrable sin enumerar mutaciones infinitas.

## Conclusión
El diff cumple P10 (a/b/c), D9/R-4, BL-1 y el punto (d): RED real (7 fallas declaradas y observadas), GREEN mínimo con tests no triviales (verificado por mutación), regeneración `make agents` idempotente y coherente, comandos read-only confirmados en código, y continuity.md ahora dice la verdad sobre R-1 y O-1c. **Sin hallazgos bloqueantes.** Un hallazgo Required no bloqueante (F-1: el no-op de `checkpoint` idéntico salió del texto de continuity.md en la misma edición) debería cerrarse antes del cierre del feature 003-007, ya sea en el cierre de esta tarea o como deuda declarada.

**Modificaciones por mí:** ninguna en el repo (write_scope ∅ respetado). Temporales usados: `/tmp/opencode/t4-red-wt`, `/tmp/opencode/t4-mut-wt`, `/tmp/opencode/t4-review-wt` (worktrees de lectura, removidos al finalizar). Commits revisados: `bc96fc4` (RED), `a87c373`, `aadb11b`, `1f5fdac` (GREEN), `82e9b86` (paquete review).
