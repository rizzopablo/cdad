| `reconcile --packet …reviewer-review-005` | **1** | **split-brain → escalate** |
| `trigger --packet …reviewer-review-005` | 0 | `trigger: unknown` (sin contador de contexto) |

---

### 1) Objetivo
Cerrar **003-006-runtime-adoption**: cablear y activar en **OpenCode, Claude Code y Codex** lo construido en 003-001..004. T4 = re-adopción v5 (`d958672`), recorrido real por runtime, `receive` y continuidad reales, y borrador de **enmienda de cierre del epic** para el dueño. **Sin push.**

### 2) Autoridad vigente y de dónde sale
- `authority.state = "active"`, `authority_ref = docs/epics/epic-003-context-efficiency/execution.md`, `expires_on = null`.
- Sale **del propio checkpoint** (`resume` → `projection.authority`), anclado al execution context `exec-003-006-runtime-adoption-001`. Nada en la salida la revoca ni la reasigna.

### 3) Decisiones tomadas (con su razón, según el checkpoint)
1. **Spec P1-P12 y plan T1-T4 aprobados bajo delegación HITL** — `review-draft-001-decision.md`; el usuario dijo “ok” a la feature el 2026-10-07.
2. **T1, T2 y T3 cerradas** tras review GLM; **B-1 de T2 corregido** — `dispatch-ledger` filas 6, 15 y 21.
3. **RU-1**: el hook emitido fija `CDAD_PACKET_CLI` a la raíz adoptada — `t4-ru1-decision.md`: el guard buscaba el clasificador en HOME (copia vieja) y fallaba cerrado.
4. **La activación real del repo y la confianza de Claude Code quedan para el dueño** — el clasificador de permisos denegó la activación del repo real; la confianza es un cambio de seguridad en HOME.
5. **RU-1 GREEN `5c09770` aceptado**; hook emitido verificado por `bash -c` — `adoption-ledger.md` Paso 3.
6. **RU-1 cerrado** por re-review focal recibida con `cdad_result receive` y materializada — `review-ru1-rereview.md`; reconcile = `received`, `repeat_effect false`.
7. **La rotación 1 se bloqueó por integridad de referencias**; se registra como deuda **T4-REF** y se repite tras un `begin` nuevo sin escrituras intermedias — `adoption-ledger.md` Paso 5.

### 4) Incertidumbres
Declaradas por el checkpoint:
- Claude Code: las skills de usuario ganan a las de proyecto → despachar con `--setting-sources project,local` o retirar copias de HOME (**decisión del dueño**).
- Codex: el catálogo lista **las dos copias**; en la sonda usó la de proyecto.
- `trigger` sigue dando **unknown** (sin lector de contexto).
- T4-REF / T4-CKPT: los documentos vivos referenciados **invalidan `resume` al cambiar**.

Añadidas por esta lectura:
- **Split-brain no resuelto** en el paquete `…reviewer-review-005` (ver 6).
- `trigger` no aporta nada operativo: `context_used_tokens`/`context_limit` = `None`, `profile: null`, `budget.attempts: []`, `consumed: 0` → **no hay telemetría de contexto ni de intentos**.

### 5) Próxima acción concreta
Según el checkpoint: **Rotación 2** (resume en sesión nueva) y luego suite de cierre en worktree fijado → despachar el paquete de **scribe** (`003-006-runtime-adoption-scribe-memory-001`, attempt 1, que es el checkpoint activo) → Memory Bank + `closure.md` de 003-006 → completar la enmienda → presentar las **4 decisiones al dueño**.

**Pero** queda condicionada: el paquete que el checkpoint declara activo (scribe) es *sucesor* de `reviewer-review-005`, y ese último está en split-brain (punto 6). Con lo que hay, la acción inmediata real es **escalar la divergencia**, no despachar.

### 6) ¿Algo que repetir o re-despachar? — No. Justificación con `reconcile`
`reconcile` **falló (exit 1)**:
```
split-brain: divergent checkpoint heads for key
(execution_id='exec-003-006-runtime-adoption-001',
 packet_id='003-006-runtime-adoption-reviewer-review-005', attempt=1):
['2aee8d80….json', 'f703ca13….json']
→ escalate — the CLI never chooses a winner (D7)
```
- Hay **dos cabezas divergentes para la MISMA clave** (mismo execution, mismo packet, mismo `attempt=1`) ⇒ el intento del reviewer está **duplicado/invalidado**, y no puedo determinar si su efecto ya se aplicó (`received`) o no.
- **No hay base para re-despachar**: re-despachar elegiría un ganador por mi cuenta, que es exactamente lo que D7 prohíbe; y repetir un efecto ya aplicado sería el daño opuesto.
- Señal agravante (inferencia, marcada): el `prev_checkpoint_sha256` del checkpoint de scribe es `f703ca13…`, **idéntico a una de las dos cabezas en conflicto** ⇒ la cadena de continuidad apunta a una cabeza mientras existe otra para el mismo slot; la procedencia del sucesor queda ambigua.
- `trigger` tampoco desempata: **unknown**, sin presupuesto consumido ni intentos registrados.

⇒ Estado: **las dos ramas se detienen; solo el usuario desempata.**

### 7) ¿Necesito preguntarle algo al usuario? — **Sí**
1. **Cómo resolver el split-brain** de `…reviewer-review-005` attempt 1: ¿cuál de `2aee8d80…` / `f703ca13…` es la cabeza canónica, y debe descartarse/archivarse la otra?
2. Si el efecto del reviewer **ya se recibió** (memoria materializada) o **debe repetirse** una vez designada la cabeza.
3. Autorización para avanzar a la **rotación 2** una vez reconciliado.
4. Las decisiones de dueño pendientes: **Claude Code** (`--setting-sources project,local` vs retirar copias de HOME), **Codex** (qué copia), activación del repo real y confianza en HOME.
5. Las **4 decisiones** de la enmienda de cierre que el checkpoint menciona pero no enumera.

### 8) Qué me faltó que el checkpoint no me dio
- **Run-state real del reviewer-review-005**: si su artefacto se materializó y si el `receive` ocurrió — `reconcile` no pudo resolverlo (era su razón de ser).
- **Qué contiene la otra cabeza** (`2aee8d80…`): sin su contenido no puedo saber si es un intento idéntico, un retry parcial o un resultado distinto.
- **Identidad/rol de `f703ca13…`**: aparece como cabeza en conflicto *y* como `prev_checkpoint_sha256`; falta la semántica explícita de ambas apariciones.
- **Telemetría**: `trigger = unknown`, sin `context_used_tokens`/`context_limit`/`profile`; `budget.attempts = []` y `consumed = 0` ⇒ no sé cuántos intentos reales hubo ni si quedan.
- **Cuerpo del paquete activo**: solo tengo `body_sha256` (`91c46322…`) y `bytes: 2232` del paquete de scribe; **no su contenido**, así que no podría validar ni despachar sin renderizar.
- **Los 4 documentos de decisión del dueño**: el checkpoint los **referencia con hash** (4 de 8 referencias) pero no transcribe su contenido; la enmienda de cierre solo aparece como ruta.
- **Evidencia de la suite de cierre**: el `next_action` la menciona (“suite de cierre en worktree fijado”) pero no hay estado, resultado ni worktree fijado en la proyección; el worktree tampoco está identificado.
- **Qué es T4-REF / T4-CKPT deuda en detalle** más allá del nombre y la causa declarada.
- **Frontera de escritura** del paquete pendiente (`write_scope`) y **timestamp de re-entry** del checkpoint.

**Bottom line:** objetivo y autoridad claros; la cadena de decisiones es coherente, pero **hay un bloqueo duro de integridad de continuidad**: `reconcile` = split-brain ⇒ **no se repite ni se re-despacha nada**; escalo al usuario para que desempate la cabeza canónica antes de la rotación 2 o de tocar el paquete de scribe.
