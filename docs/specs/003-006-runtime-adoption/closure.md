# Cierre — 003-006-runtime-adoption

**Cerrada:** 2026-10-08, por el orquestador bajo la delegación HITL de epic-003. La abrió el dueño el
2026-10-07 tras una revisión externa de la adopción ("ok").

## Qué entrega
Cablea, activa y comprueba lo construido en 003-001..004, sin funcionalidad nueva:
- **Descubrimiento:** `SKILL.md` y el cuerpo del orquestador nombran `receive`, `begin`, `checkpoint`,
  `reconcile`, `resume` y `trigger` en su paso del ciclo. `classify` queda declarado fuera.
- **Activación por proyecto:** `scripts/cdad-activate.py` (+ `references/runtime-adoption.md`).
  Es determinista, no pisa archivos ajenos, contiene las rutas dentro del proyecto y nunca escribe
  las configs de HOME. El hook de Claude Code usa el clasificador de la raíz adoptada (RU-1).
- **Continuidad corregida:** un `begin`/`checkpoint` rechazado no escribe nada (RU-2, `abcd4d3`).
- **Versiones adoptadas:** v5 `d958672` y v6 `abcd4d3`, instaladas en raíces aisladas
  (`docs/runtime-adopted-version.md`). **v6 no está activada en el repo** (decisión del dueño).

## Postcondiciones
| P | Estado | Evidencia |
|---|---|---|
| P1 | ✅ estructural | T1 `a0f2335`, T3 `d958672`; reviews T1/T3 PASS. **No demostrado en una sesión real:** todas las sondas y rotaciones recibieron los comandos explícitos, y el `cdad-orchestrator` del repo todavía usa el cuerpo de `818f12a`. Que una sesión nueva descubra `resume`/`receive` por su cuenta queda pendiente para después de la activación |
| P2, P3 | ✅ | T2 `04ba3d8` + `7ccea01`; re-review T2 |
| P4 | ✅ en el worktree | OpenCode cargó las skills v5 en el worktree desechable (`adoption-ledger.md` Paso 2); en el repo real sigue `818f12a` hasta la activación |
| P5 | ⚠️ parcial | El comando emitido bloquea/permite correctamente vía `bash -c` (Paso 3). En el runtime real, Claude Code **no ejecuta** los hooks de agentes de proyecto sin confianza de carpeta, y las skills de usuario ganan a las de proyecto |
| P6 | ✅ con límite | Codex usó la copia de proyecto (sonda de contenido); el catálogo también lista la de HOME |
| P7, P8 | ✅ | Dos `receive` reales; reintento byte a byte idéntico; `reconcile` = `received` |
| P9 | ✅ con fricción | Rotación 3 correcta. Las rotaciones 1 y 2 se bloquearon (T4-REF y RU-2) |
| P10 | ✅ | `trigger` `unknown`; `classify` fuera |
| P11 | ⚠️ parcial | v5/v6 instaladas y registradas; el repo sigue apuntando a v4 (activación denegada por el clasificador de permisos → dueño) |
| P12 | ✅ | `adoption-ledger.md` con marcadores; `closure-amendment-draft.md` entregado |

## Gate
- Suite de cierre: **567 passed (684 s)** en un worktree fijado a `ea095d5`, tras `make staging`
  (`evidence/closing-suite-tail.txt`). Una primera corrida sin staging dio 4 failed y 6 errors, todos
  por `Staging manifest missing` (precondición del harness, no del producto).
- Validadores en el repo: **141 PASS / 2 FAIL**, ambos preexistentes: F011 (las copias de HOME no se reinstalan a propósito) y A3 (patrones sensibles, ANON-1).
  En el worktree dan 142/1 porque falta `tests/.sensitive-patterns.local` (git-ignorado) y A3 usa solo los patrones por defecto, así que esa cifra **no es comparable**. Lo mismo infló la cifra del cierre de 003-004 (142/1).
- Sin CI.

## Deuda
`debt.md`. Alta: **T4-REF** (las referencias a documentos vivos bloquean la reanudación). Media: T4-CKPT,
T2-O1, T3-O1, ANON-1.

## Decisiones del dueño pendientes
Ver `docs/epics/epic-003-context-efficiency/closure-amendment-draft.md`.
