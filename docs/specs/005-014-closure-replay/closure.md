# Cierre de 005-014-closure-replay

**Feature:** 005-014-closure-replay · **Epic:** `epic-005-real-operation` (fila 14, decimocuarta unidad) ·
**Cerrada:** 2026-10-14 · **Contrato:** `spec.md` sha256
`5c23caa2d00c748ea7bea7534dccbf05a7c46709e7bc34f35a1eb44946cd3e95` (v2, enmienda 001) · **Plan propio:**
no hay (forma liviana decidida por el dueño) · **Aprobación:** orquestador OpenCode bajo la HITL delegada del
epic-005 (`docs/epics/epic-005-real-operation/execution.md:8-23`).

## 1. Qué entrega la unidad

**Repetir un cierre ya aplicado no falla ni sugiere abrir la unidad.** Con la feature cerrada, la clase
`closure` de `register-transition` resuelve su feature (por `--feature`, por `state.active_feature` o por la
feature ligada por la **ejecución activa**), decide **por identidad** si la transición ya está registrada
(no-op rc=0 que lo dice, sin escribir el state) y, si no lo está, **rechaza cerrado** con un mensaje que
**no** sugiere abrir la unidad y que ofrece la salida legítima. Sin feature activa la operación **nunca
aplica** un cierre: sólo reconoce o rechaza. Decisión registrada en **ADR-030**
(`docs/adr/ADR-030-replay-de-cierre-identidad-resuelta-desde-la-ejecucion-ligada-y-techo-sin-feature-activa.md`).

**Alcance:** la clase `closure` y nada más. Las demás clases (`delivery`, `advance`, `gate`, `late-delivery`,
`disposition`) conservan su comportamiento; la identidad (PD-10), las reglas del pin y el efecto del cierre
quedan intactos. El defecto medido: con la feature cerrada `active_feature` es `null` y el guard de feature
nula corría **antes** de la búsqueda idempotente por `transition_key` (PD-11), así que un orquestador
interrumpido justo después del cierre no podía reanudar con la misma orden.

## 2. Gates de la etapa 3 (verificación propia del orquestador, no aceptación de la prosa)

| Tarea | Focal (RED → GREEN) | Regresiones | Otros |
|---|---|---|---|
| T1 `closure` sin feature activa (PD-22..PD-25, PD-27) | 4 rojos por **aserción** (`8a969d3`) → **4 passed** (`a4028af`) | cuatro módulos de 005-012 **47** | `git diff --name-only a4028af~1..a4028af -- tests/` **vacío**; `validate-state` rc=0; ruff limpio |
| T2 escenario de reanudación (AC-1/AC-2/AC-3) | — (prueba decisiva, no focal) | — | CLI real sobre proyecto descartable: **AC-1/AC-3** no-op rc=0, bytes iguales, 1 entrada; **AC-2** rc=2 `state incoherent`, sin `open-unit`, sin efectos (`acceptance.md`) |

El RED falló **por aserción** en los cuatro casos (0 `ImportError`, `SyntaxError` o errores de colección) y el
GREEN no tocó `tests/`. La enmienda del contrato (v2) precedió al GREEN: el focal **expuso una contradicción
interna del v1** (PD-22 no resolvía la feature en la repetición verbatim) y el contrato se corrigió antes de
implementar.

## 3. Etapa 4 — review

`review.md` (sha256 `f61c290029585f9d0e4386733b6e8dd599a4e1312c7af8af1fc9d905ada82a12`): **0 bloqueantes /
4 opcionales / 3 abstenciones**. Reviewer de **familia distinta** a la del implementer
(`mofgw/glm-5.3-flash` vs `mofgw/deepseek-v4.1-flash`). El reviewer reprodujo el focal, la regresión y la
aceptación por su cuenta y corrió **cinco sondas adversariales propias**, todas fail-closed con el state
idéntico. Los 4 opcionales (Nit/FYI, sin impacto material) van a **deuda** por el criterio vigente
2026-10-12; las 3 abstenciones (la suite completa, INV-7 a nivel de árbol y la estabilidad del digest del
documento citado) quedan declaradas.

## 4. Suite de cierre

`closure-suite.md`: una sola corrida, por quien cierra, en un **worktree aparte** fijado a `2de9747` (el
código de producto es byte a byte el de `a4028af`) armado con `make staging`: **1028 passed / 4 skipped, sin
fallos**; `make validate` **155 PASS / 1 FAIL**, el fallo **F011** preexistente y declarado (D-6 de 005-011).

## 5. Deuda y límites declarados

Consolidados en `debt.md`: **E-1..E-6** (spec §6) y **O-1..O-4** (review), cada uno con su motivo y su
condición de cierre. Los límites del arreglo (el replay tras un cambio de feature activa, la rama de PD-22
sin caso focal, la extensión del límite de PD-23 a los `--artifact` citados) están declarados, no ocultos.

## 6. Transiciones manuales del tramo

- **La enmienda del plan del epic** (fila 14 + «Cambios al plan» 2026-10-14) y su registro en `epic_history` y
  `epic_features` (alta de la entrada en cola): edición del state por el orquestador, **declarada** (no existe
  operación para el alta de una unidad del plan). El `plan_sha256` registrado es el del plan después de la
  edición.
- **`review_status`**: campo **derivado sin dueño** en la operación de transiciones (deuda D-2 de 005-012);
  actualizado a mano por el orquestador con el veredicto y la disposición de esta unidad, **declarado**.
- Todo lo demás del tramo (discovery, entregas, gates, aceptación, review y el cierre) se registró con
  `register-transition`.

## 7. Cómo se cierra la unidad (evidencia del arreglo en el propio repo)

El cierre se registra con `register-transition --transition closure` — la operación que la unidad corrige — y
**se repite una vez**: la repetición idéntica es un **no-op** (rc=0, dice «transition already registered»,
nombra la entrada y no escribe el state). Es la prueba de que el caso que la unidad arregla funciona sobre
este repo, no sólo sobre proyectos descartables.

## 8. Estado del epic

`epic-005-real-operation` sigue en **`features-loop`** con **14/14** unidades cerradas y **ninguna en cola**.
El epic **no se cierra** en este tramo: quedan el **gate de saneamiento antes de publicar** (lo hace el dueño
en un worktree aparte) y el **despliegue**, que decide el dueño. El proyecto queda **en reposo**.
