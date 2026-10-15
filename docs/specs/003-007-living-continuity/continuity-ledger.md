# Continuity ledger — 003-007-living-continuity (T3, aceptación P9)

Versión bajo prueba: v7 `2ed4c8d`, instalada en una raíz aislada (`<cache>/cdad-adopted-2ed4c8d`,
`install.sh --optimus`, Check PASS de 363 grupos) e invocada **por ruta explícita**. El repo sigue
activado en v6 (`abcd4d3`); no se reactivó. HOME sin tocar (mtimes previos a la feature).

| situación | evidencia | decisión | autoridad vigente | presupuesto | falsas alarmas | retrabajo | pendiente |
|---|---|---|---|---|---|---|---|
| T4-REF en uso real sobre 003-007: `t2-record-decision.md` enmendada después del último `begin` (escrito por v6, sin clases) | `evidence/t3/v6-resume.out` (rc 1, digest mismatch); `evidence/t3/v7-resume.out` (rc 0, `changed` + `legacy: true`) | v7 resuelve el legado por comparación; v6 bloquea | delegación HITL epic-003 | intentos 1; contexto `null` (sin lector) | 0 | 0 | — |
| Stores cerrados de 003-004 y 003-006 | `evidence/t3/exec-003-00{4,6}-*-v{6,7}.out` | v6 bloquea los dos por ledgers, debt o borrador de enmienda; v7 reanuda los dos y solo informa los vivos `changed` (specs y planes `unchanged`) | idem | 1 por store; contexto `null` | 0 | 0 | — |
| `begin` v7 con clases declaradas (8 referencias: 6 `contract`, una con `fields` de autoridad del state; 2 `living`) | `begin` seq 8, `record: begin` | — | idem | 3020 B de 16384 | 0 | 0 | — |
| T4-CKPT en uso real: checkpoint de límite con la misma clave que el `begin` | seq 9, `record: checkpoint`, `prev` = body del `begin` | append (P5), ya no split-brain | idem | — | 0 | 0 | — |
| Escrituras vivas posteriores: fila 13 del ledger y una entrada de progreso en `stage_history` | commit `4d9ab1e` | intencional, para probar la tolerancia | idem | — | — | — | — |
| **Rotación**: sesión nueva, solo `resume` v7 | `evidence/t3/rotation.md` | reconstruyó objetivo, 14 decisiones con su razón, autoridad y próxima acción; informó 1 `living` `changed` y 6 `contract` `unchanged`; "no impide continuar"; cero escrituras | idem | 1 llamada; contexto `null` | 0 | 0 | — |
| Bloqueo de contrato (copia controlada; la spec del repo no se tocó) | `evidence/t3/contract-block-copy.txt` | spec editada en la copia → rc 1 con `path` y digests | idem | — | 0 | 0 | — |
| Bloqueo de autoridad del state (copia) | `evidence/t3/authority-block-copy.txt` | `hitl_delegation` alterada → rc 1; un cambio de `stage_history`/`current_stage` → rc 0 | idem | — | 0 | 0 | — |

**Resultado P9: cumplida.** Límite declarado: los bodies legados resueltos por comparación informan
cualquier documento cambiado, incluida una decisión que en un checkpoint nuevo sería `contract`
(caso `t2-record-decision.md`). Es la excepción documentada de P7; los checkpoints nuevos la evitan
declarando la clase.
