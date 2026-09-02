# cdad-006: Git safety al cierre de la branch

> Estado: APROBADO — Status: Approved by Pablo on 2026-09-02 (delegación HITL
> de ciclo: "sos dueño del proceso, HITL hasta el final de los temas").
> Fecha: 2026-09-02 · Origen: research tema 2
> (docs/epics/research-tema2-git-safety/research.md). Cycle light aprobado.

## Descripción funcional

`stage-5-merge.md` cubre CI + Memory Bank pero la mecánica de integración de
la branch (merge/PR/keep/discard, base branch, entorno, limpieza) no existe:
el orquestador cierra el Memory Bank y no hay contrato para el paso que puede
destruir trabajo. Se incorpora §5.4 "Cierre de la branch (git safety)" con
detección de entorno, confirmación de base branch, menú fijo, descarte con
palabra literal y limpieza por provenance — respetando §5.3 (el usuario
DECIDE, el orquestador EJECUTA).

## Restricciones de diseño

- **R1 — No duplicar §5.1/§5.3:** la suite verde es precondición heredada
  (no se re-pide); el principio aprobación/ejecución ya existe — §5.4 lo
  extiende a la decisión de integración.
- **R2 — Orden CDAD:** la sección va DESPUÉS del Memory Bank (CI → Memory
  Bank → integración). El cierre de feature existente no se reordena.
- **R3 — Nunca destructivo por iniciativa propia:** sin `--force`, sin
  auto-resolver conflictos, sin borrar worktrees ajenos (provenance:
  solo `.worktrees/`/`worktrees/` creados por el propio ciclo).
- **R4 — Descarte con palabra literal `discard`:** lista previa de qué se
  borra; un "sí, borralo" no alcanza.
- **R5 — Alcance cerrado:** solo `stage-5-merge.md` (+ validación). Un solo
  contrato, un solo rol (orquestador).

## Contrato (postcondiciones numeradas)

**P1 — Sección §5.4.** `skills/cdad-cycle/references/stage-5-merge.md`
contiene una sección nueva "Cierre de la branch (git safety)" numerada 5.6 (la numeración 5.4/5.5 ya existe en el archivo — desviación detectada y resuelta en AUDIT) con:
(a) detección de entorno: repo normal vs. worktree vinculado vs. detached
HEAD vía `git rev-parse --git-dir` vs `--git-common-dir`, con guard de
submodule (`--show-superproject-working-tree`) y adaptación del menú
(detached: sin merge local); (b) base branch: si no está registrada en
spec/state, se confirma con el usuario — nunca se asume; (c) menú fijo de 4
opciones presentado textualmente: merge local / push+PR / keep as-is /
discard — el usuario elige, el orquestador ejecuta (§5.3); (d) merge local:
checkout base → merge → **re-verificación de suite sobre el resultado
mergeado** → recién entonces borrar branch; conflicto = STOP sin
auto-resolver (listar archivos, decisión del usuario); (e) push+PR: push
explícito + worktree/branch viven para iterar feedback de review;
(f) discard: solo a pedido explícito, con lista de branch+commits+worktree y
espera de la palabra literal `discard` (R4); (g) limpieza por provenance (R3):
`worktree remove` + `prune` SOLO para worktrees del propio ciclo, desde la
raíz del repo principal, después del merge/discard confirmado; worktree ajeno
o remoción rechazada → mostrar contenido y preguntar, sin `--force`;
(h) orden crítico documentado: merge primero → worktree después → branch al
final (borrar branch con worktree vivo referenciándola falla);
(i) tabla anti-racionalización propia + "cuándo NO aplica" (squash-merge por
convención del proyecto: cambia el comando, no la decisión del usuario;
monorepo sin branch de feature).

**P2 — Anti-patrón.** `skills/cdad-cycle/references/anti-patterns.md` agrega
**AP-17 — Integración destrutiva unilateral** (formato del catálogo:
Síntoma / Por qué es malo / Corrección) citando §5.4: el agente mergea,
borra branches/worktrees o descarta sin menú ni confirmación (incluye el
riesgo en vivo: reset de openchamber 05 Ago 2026 documentado en MEMORY.md
del workspace — patrón de referencia sin exponer rutas privadas).

**P3 — Mapa de lectura.** La sección es referenciable: `stage-5-merge.md` ya
está en la tabla de lectura del SKILL.md — no requiere fila nueva; el
contrato se valida por la existencia de §5.4 (P1) y AP-17 (P2).

## Invariantes

- No se modifica ningún otro archivo de `skills/` ni `agents/`.
- La aprobación de integración es del usuario (extensión de §5.3/AP-10);
  el orquestador nunca elige opción del menú por defecto.
- La suite de cdad-003 (121/121) y checks cdad-004 (10/10) y cdad-005 (23/23)
  siguen verdes tras GREEN.

## Criterios de aceptación (verificables)

1. `stage-5-merge.md` contiene `## 5.4` con las 9 piezas de P1 (checks grep
   por pieza: detección+guard, base confirmada, menú 4 opciones, conflicto
   STOP, discard literal, provenance, prune, orden merge→worktree→branch,
   anti-racionalización, cuándo NO aplica).
2. `anti-patterns.md` contiene `## AP-17` con las 3 sub-secciones del formato.
3. `## 5.3` y el resto de stage-5-merge.md intactos (guard: los encabezados
   previos siguen presentes).
4. RED: checks definidos ANTES de editar y fallando sobre el estado actual.
5. Sin regresión: suites de cdad-003/004/005 verdes tras GREEN.
