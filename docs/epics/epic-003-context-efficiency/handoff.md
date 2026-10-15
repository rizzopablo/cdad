# Handoff operativo — epic 003

Última actualización: 2026-10-05. Código base: `1408445`; HEAD documental: `1408445`.
Rama: `codex/epic-003-context-efficiency`. Sin push automático.

> **Reanudación 2026-10-05 (leer antes que nada):** el epic fue reactivado por
> reconciliación tras el cierre de epic-004. El punto de entrada vigente es
> [handoff-resume-2026-10-05.md](handoff-resume-2026-10-05.md) — contiene el estado
> reconciliado, la autoridad HITL re-registrada (nueva, **no heredada**), los cambios
> de 004 que afectan a 003 y la siguiente acción. Lo de abajo es historia de la
> suspensión.
>
> **Estado de 003-002 al 2026-10-05:** spec reconciliada y **aprobada**; plan
> replanificado, revisado y **aprobado**; ejecución `exec-003-002-artifact-tools-001`;
> **T1, T2 y T3 cerradas** (con sus reviews y review-fixes); P1–P5 implementadas.
> **Pendiente: T4** (integración: recorrido receive → reconcile → materialize +
> smoke instalado) y el cierre de la feature. Deuda consolidada en
> `docs/specs/003-002-artifact-tools/supervision-record.md`.
>
> **Versión operativa adoptada:** `2ec12a7` en raíz aislada (`8cb6580` conservada como recuperación), ámbito de proyecto —
> ver `docs/runtime-adopted-version.md`. Se adopta una versión nueva **solo** en un
> límite de tarea/ciclo y después de su revisión.
>
> **Calibración de la revisión (decisión del dueño, 2026-10-05):**
> `docs/owner-decision-review-calibration-2026-10-05.md` — proporcionalidad, cierre
> por clase, usabilidad como criterio. Ya incorporada al proyecto (`675c18e`).
>
> **Evidencia de utilidad:** `evidence-utility-2026-10-05.md`.

## Punto de entrada vigente

Leer primero [Continuación con GLM](../../handoffs/2026-09-23-glm-continuation.md).
El usuario quiere desarrollo con GLM y análisis profundo/revisión con GPT o
Claude. La selección histórica de Sol no es la instrucción actual.

Se propone resolver antes de 003-002 un epic acotado de fuente única,
bootstrap y procedimientos de planificación:
[plan 004, borrador](../epic-004-single-source-planning/plan.md).
No está aprobado ni activo. El inventario y dictamen C0 ya existen; el siguiente
paso es el delta y spec/plan 004-001 de la enmienda vigente, sin reabrir 001.

## Estado verificado

| Feature | Estado | Evidencia / siguiente acción |
|---|---|---|
| 003-001-role-packets | Done, 2026-09-18 | Review-4 aprobado con comentarios; cierre en Memory Bank. |
| 003-005-claude-code-packets | Done, 2026-09-18 | Prepare + adaptación Claude Code; review-2 aprobado con comentarios. |
| 003-002-artifact-tools | Queued | Tres drafts persistidos, no aprobados. Revisar tras nuevos contratos de 004. |
| 003-003-progress-guards | Queued | Brief en remaining-features-handoff.md. |
| 003-004-context-continuity | Queued | Brief en remaining-features-handoff.md. |

`docs/.cdad-state.json`: epic 003 en `features-loop`, `active_feature: null`,
`current_stage: idle`. No se modificó el state al escribir esta guía. No hay
trabajo delegado por este handoff; no resucitar sesiones antiguas como si
fueran agentes activos. Comprobar el runtime al comenzar otra sesión.

## Autoridad y política de ejecución

El mandato de Codex y la transición posterior a Claude constan en
[execution.md](execution.md) y en el historial de state. No convertir esa
historia en una delegación automática a GLM ni al epic nuevo. La política
concreta de autoridad/runtime se prepara para C0. Dentro del alcance aprobado,
GLM podrá resolver acciones rutinarias sin consulta por cada vuelta.

ADR-010 conserva alcance/vencimiento; no se hereda en 004. La construcción
GLM + review GPT/Claude no demuestra por sí misma la aceptación de modelo único
que aún figura en el plan 003. Resolver esa condición explícitamente antes del
recorrido final, sin A/B ni desarrollos duplicados.

## Evidencia y pendientes

- Suite Python observada sobre `4a821a0`: 52 passed, 149.23s, en una comprobación
  anterior de esta conversación. No se repitió para este cambio documental.
- Validadores aislados: PASS según cierres de 001/005; no reejecutados aquí.
- Producto instalado: problemas conocidos de layout público bajo HOME y archivos
  obsoletos; no se comprobó ni modificó ahora la instalación real.
- Receipts, guards, continuidad automática y cumplimiento 200k siguen pendientes.
- No hay evidencia nueva que permita cerrar el epic ni aprobar sus drafts.

Contratos que se conservan: identidad/autoridad de ejecución, paquetes
canónicos, aislamiento de roles, evidencia vigente y gates. Las enmiendas
necesarias se revisan, no se sortean mediante defaults o guards desactivados.

## Próxima acción exacta

Actualización 2026-09-24: inventario y reporte C0 ya entregados. GLM incorpora
[ADR-011](../../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md)
y prepara spec/plan de 004-001 según la
[enmienda C0 vigente](../epic-004-single-source-planning/c0-amendment-supervised-autonomy-2026-09-24.md).
Se simplifica la política antes de generar; no repetir el inventario completo. No se
le pide volver a analizar toda la historia ni implementar 003-002 todavía.
Después de cerrar el trabajo estructural aprobado, retomar los briefs de
[003-002/003/004](remaining-features-handoff.md), adaptándolos a los contratos
realmente entregados, sin regenerarlos desde cero.

Antes de cada delegación/transición: guardar objetivo, HEAD/diff, rol, autoridad,
entradas y límites, trabajo en curso, evidencia y próxima acción en el handoff.
Después: conservar resultado original, dictamen y estado reconciliado.

## Historia preservada

El handoff anterior tenía encabezado de 001 bloqueada y cierre añadido al final.
Se conserva como [archivo histórico](history/handoff-through-2026-09-18.md),
con el nombre personal normalizado; se mantiene su contenido técnico.
Sus instrucciones de retomar RED, cerrar 001 o usar Sol ya no son vigentes.
Specs, tests, reviews y commits históricos no se reescriben.
