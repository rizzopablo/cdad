# Encargo al architect — 003-007-living-continuity (discovery + spec/plan draft)

Rol: `cdad-architect`, solo lectura. Entregas en tu respuesta (el orquestador
materializa). Objetivo de tiempo: ~30-40 min. Sin `opencode run`/`claude`/`codex`
anidados, sin comandos en segundo plano, sin instalar nada.

## Objetivo
Que la continuidad (`cdad_continuity`) **tolere la evolución normal del trabajo**: un
orquestador que trabaja horas escribe ledgers, deuda y Memory Bank después de cada
checkpoint, y eso no debe impedir reanudar. Hoy sí lo impide (T4-REF, deuda **alta**
de 003-006) y además un checkpoint de límite se confunde con un `begin` duplicado
(T4-CKPT). Feature chica, MVP proporcional; endurecimiento a deuda. Es la última
feature de epic-003; su cierre habilita el cierre del epic con enmienda.

## Hallazgos verificados en uso real (003-006 T4, evidencia en `docs/specs/003-006-runtime-adoption/evidence/t4/`)
1. **T4-REF:** `resume`/`reconcile`/`trigger` fallan cerrados si cambió el sha de
   **cualquier** documento referenciado por el checkpoint. Los ledgers y `debt.md` cambian
   en cada paso; la rotación 1 de 003-006 quedó bloqueada por eso
   (`rotation-1-blocked`). La rotación 3 funcionó solo porque no se escribió nada entre el
   último `begin` y la reanudación.
2. **T4-CKPT:** un `checkpoint` de límite con la misma clave
   `(execution_id, packet_id, attempt)` que su `begin` se rechaza como split-brain
   (`checkpoint-after-ru1-REFUSED.txt`). Hoy el `begin` del paquete siguiente hace las
   veces de checkpoint.

## Dirección acordada con el dueño (punto de partida, no diseño cerrado)
- El checkpoint conserva una **fotografía estable** de decisiones y evidencias.
- Dos clases de referencia:
  - **contrato/autoridad** (spec y plan aprobados, `docs/cdad-policy.json`, aprobaciones,
    delegación HITL): si cambia, la acción correspondiente se **detiene** (fail closed).
  - **documento vivo** (ledgers, `debt.md`, Memory Bank, adoption/continuity ledgers): si
    cambia, se **informa** como progreso ("cambiado desde el checkpoint") y se reconcilia;
    no bloquea.
- No quitar indiscriminadamente las comprobaciones de integridad: distinguir qué cambio
  invalida una evidencia y cuál representa progreso.
- Un nuevo checkpoint del mismo trabajo **no** debe confundirse con duplicar un despacho.

## Puntos de diseño que el discovery debe resolver (decisiones D1..Dn)
1. **`docs/.cdad-state.json` es de las dos clases:** contiene autoridad (`hitl_delegation`,
   `approved_by`, `stage_history`) y progreso. Un sha del archivo completo no sirve; proponer
   qué campos se digieren como autoridad.
2. **Fuente de la clasificación:** la separación contrato/vivo debe venir de la política
   del proyecto o de la propia referencia (p. ej. una clase declarada al hacer `begin`), no
   de rutas fijas dentro del CLI. Lo **no clasificado = contrato** (falla cerrado).
3. **T4-CKPT:** distinguir `checkpoint` de `begin` por el comando que escribió el registro
   (o una secuencia propia del checkpoint), no solo por la clave. Un `begin` duplicado
   divergente sigue fallando cerrado; un checkpoint nuevo es un eslabón nuevo de la cadena.
4. **Compatibilidad hacia atrás:** los checkpoints existentes de
   `exec-003-004-context-continuity-001` y `exec-003-006-runtime-adoption-001` deben
   seguir siendo legibles (`resume` no puede romperse sobre ellos).
5. **Uso sin reactivar:** tras la review, la versión nueva se instala en una raíz aislada
   y se invoca por ruta explícita; no requiere re-activación del repo.

## Reconciliación de regla (tarea separada, la última)
`sources/roles/orchestrator.md:70` exige encargos atómicos "one postcondition, one test,
one diff". La práctica (003-002..006) ya despacha **unidades coherentes** (una tarea del
plan con varias postcondiciones relacionadas, un RED y un GREEN por tarea). Proponer el
texto que reconcilia la regla con esa práctica sin perder lo que protege (trazabilidad
test↔postcondición, diffs revisables). Regenera agentes (`make agents`), por eso va como
**última tarea, separada** de la continuidad.

## Restricciones del dueño (no negociables)
- Nunca instalar ni modificar CDAD en el HOME real; solo raíces aisladas.
- Sin push automático. Anonimizar rutas/identidades en lo commiteado.
- No endurecer permisos.
- Gates de tests (vigente 2026-10-08): el implementer corre focales + tests de los módulos
  tocados; suite completa solo al cierre de la feature o si toca instalador/staging/renderer.
  El plan debe nombrar los focales por tarea.

## Entradas (leer)
- `docs/epics/epic-003-context-efficiency/plan.md` (fila 4c), `closure-amendment-draft.md`
- `docs/specs/003-004-context-continuity/{spec.md,closure.md,debt.md}`
- `docs/specs/003-006-runtime-adoption/{debt.md,adoption-ledger.md,closure.md}` y `evidence/t4/`
- `skills/cdad-cycle/references/continuity.md`, `skills/cdad-cycle/scripts/cdad_continuity.py`
- `tests/` de continuidad (`test_003_004_*`, `test_003_006_t4_*`)
- `sources/roles/orchestrator.md`, `docs/cdad-policy.json`

## Entregables
- Discovery (puntos 1–5) con decisiones D1..Dn y VERIFY.
- Borrador `spec.md` (postcondiciones P1..Pn verificables) y `plan.md` (≤4 tareas,
  dependencias, RED esperado y focales por tarea). Criterio de aceptación obligatorio: una
  **rotación real dentro de 003-007** con escrituras de ledger posteriores al último
  checkpoint → `resume` tiene éxito e informa los documentos vivos cambiados; una edición
  deliberada de la spec aprobada → bloquea. Última tarea = reconciliación de
  `orchestrator.md:70`.
