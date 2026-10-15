# Enmienda de cierre de epic-003

**Estado: aprobada por el dueño y aplicada.** El dueño aprobó cerrar el epic con esta enmienda el
2026-10-08 ("De acuerdo, avanza con eso", sobre la lista de decisiones del orquestador). La
aplicación se difirió al cierre de 003-007. Después de la aprobación, el texto se actualizó con
los resultados de 003-007 (criterios 1 y 3, adopción, deuda). Si el dueño no está de acuerdo con
esa actualización, el cierre se revierte reabriendo el epic.

## Propuesta
Cerrar epic-003 como **fase de infraestructura del MVP**, no como cumplimiento del objetivo
original de autonomía prolongada con contexto reducido. Los criterios 2, 5 y 6 se enmiendan o
quedan como límites declarados.

## Balance contra los criterios del plan (§ "Validación hacia adelante y aceptación")

| # | Criterio | Estado | Evidencia / límite |
|---|---|---|---|
| 1 | Features cerradas con evidencia y Memory Bank | ✅ 003-001..007 cerradas (003-006 y 003-007 el 2026-10-08) | `closure.md` de cada feature |
| 2 | Desarrollo real con **un mismo modelo** en todos los roles, dentro del presupuesto medido | ❌ **enmendado** | El dueño asignó modelos por rol: DeepSeek construye; GLM revisa y escribe tests. El presupuesto no se puede medir porque ningún runtime informa contador ni límite de contexto (`trigger` = `unknown`). Criterio reemplazado por "desarrollo real con asignación de modelos por rol y review en sesión separada". La medición queda diferida |
| 3 | Reconstrucción de sesión en un límite natural, sin re-preguntar ni repetir | ✅ | 003-004: reconstrucción manual. 003-007 T3: rotación real con `resume` v7 **después de escribir documentos vivos**, sin bloqueo y sin escrituras; un cambio de contrato o de autoridad sí bloquea (copia controlada). 003-007 sonda 2: un orquestador nuevo invoca `resume` y `reconcile` **sin que se los nombren** (tras 18 lecturas de orientación). **Límite:** la sonda 2 corrió en un worktree activado con la v7; los agentes del repo siguen en v6 hasta que el dueño active la v7 |
| 4 | Recepción idempotente; fuera de rol, evidencia obsoleta y suite vacía no cuentan | ✅ | 003-002; 003-006 y 003-007 recibieron y materializaron reviews y Memory Bank con `receive` (reintentos idempotentes, CAS) |
| 5 | Casos de trazas: bucles, presupuesto tras reanudación, polling | ⚠️ parcial | `cdad_guard` cumple sobre fixtures. **No hay lector de sesiones por runtime**, así que `classify` no observa sesiones reales: límite declarado |
| 6 | Cierre con tiempo, contexto máximo, recuperaciones; suite, integración y CI | ⚠️ | Suite verde en cada cierre. **Sin CI.** Validadores en el repo 141/2: F011 (copias de HOME desactualizadas a propósito) y A3 (patrones sensibles; deuda ANON-1). El contexto máximo no se puede medir. 003-007 aplicó la regla nueva de gates (3 corridas de suite completa del implementer, todas en T4, más la de cierre; frente a 7 en 003-006) |

## Adopción por runtime
- **OpenCode:** la v6 está activa en el repo (activada por el dueño el 2026-10-08). La v7 (`ce09ed0`)
  está instalada en una raíz aislada y verificada, sin activar.
- **Codex:** usa la copia de proyecto (enlaces de `cdad-activate`). El catálogo también lista la copia
  vieja de HOME.
- **Continuidad:** T4-REF y T4-CKPT, encontradas en el uso real de 003-006, **quedaron resueltas** en
  003-007. Queda **MIX-V6V7**: usar una sola versión del CLI por ejecución.
- **Claude Code:** las skills de usuario ganan a las de proyecto, y los hooks del frontmatter de los
  agentes de proyecto no corren si la carpeta no es de confianza. Se mitiga despachando con
  `--setting-sources project,local`.

## Decisiones del dueño
1. **Cerrar epic-003 con esta enmienda:** aprobado el 2026-10-08 y aplicado al cierre de 003-007.
2. **Activar la v7 en el repo:** un solo comando, verificado en un worktree desechable:
   `scripts/cdad-activate.py --project-root . --adopted-root <cache>/cdad-adopted-ce09ed0 --runtime opencode --runtime codex`.
   Los agentes de OpenCode se publican en el próximo `prepare` desde esa raíz.
3. **Claude Code:** marcar el repo como carpeta de confianza (`~/.claude.json`) y retirar o actualizar
   las copias viejas `~/.claude/skills/cdad-*` y `~/.agents/skills/cdad-*`. Ambos son cambios en HOME.
4. **Deuda a priorizar en el próximo epic:** lector de sesiones, medición de contexto, CI, ANON-1, y
   la de 003-007 (MIX-V6V7, R2-STAGE, POLICY-CLASS).
