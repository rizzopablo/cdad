# Handoff — architect (discovery + borrador de spec/plan) — 005-001

Fecha: 2026-10-08. Encargo 2 del orquestador (OpenCode). Reemplaza al paquete
retirado `005-001-idle-and-v7-bootstrap-architect-discovery-001` (obsoleto; ver
`dispatch-ledger.md`).

## Identidad y entorno

- **Proyecto:** repo git `<repo>`. Usá rutas absolutas o
  `git -C <proyecto>`. NO trabajes en el repo contenedor (solo guarda el gitlink).
- **Rama:** `codex/epic-005-real-operation`. Sin push.
- **Versión operativa:** v7 `ce09ed0`. Los scripts del repo y de la raíz adoptada son
  byte a byte iguales: para **leer** código usá los del repo. No instales ni actives
  versiones (reservado al dueño).
- **Rol:** `cdad-architect`. **Solo lectura.** No escribís archivos, no ejecutás git de
  producto, no aprobás tu propia spec. Entregás discovery + borrador de spec/plan como
  **TEXTO FINAL** en tu respuesta; el orquestador materializa
  `docs/specs/005-001-idle-and-v7-bootstrap/{spec.md,plan.md}`.

## Autoridad

- Plan del epic aprobado por Pablo (2026-10-08): `docs/epics/epic-005-real-operation/plan.md`.
- Delegación HITL al orquestador OpenCode: `docs/epics/epic-005-real-operation/execution.md`.
- Este despacho va por el **camino temporal fuera del CLI** (por el defecto I2 circular que
  esta misma feature corrige; ver §Obstáculos). **No es una aprobación de spec**: la spec
  la aprobás vos no; la aprueba el orquestador (HITL delegado) recién cuando exista.

## Insumos (leelos antes de concluir)

1. `docs/epics/epic-005-real-operation/plan.md` — fila **005-001**, puntos **a–e** del
   resultado verificable, y el apartado **«Cambios al plan»**.
2. `docs/epics/epic-005-real-operation/handoff-opencode-2.md` §2–3 — estado comprobado y
   obstáculos conocidos (no los reconstruyas: ya están diagnosticados).
3. `docs/specs/003-007-living-continuity/debt.md` — deuda **VALIDATE-IDLE**.
4. Código del renderer/validador, en `skills/cdad-cycle/scripts/cdad_packet.py`:
   - `_approved_stage_entry` (~1263) — control **I2**.
   - `_validate_v2_vigency` (~1313) y `_validate_v2_state` (~582) — vigencia v2.
   - `_contract_for` (~912) — tipo de contrato por rol
     (`approved-epic-plan` para architect; `approved-feature-spec` para el resto).
   - `--resume-packet` y `validate-state` — re-emisión y validación (incluí la ruta del
     state en reposo/idle).
   - Complementá con `skills/cdad-cycle/references/` (stages/gates) y
     `skills/cdad-cycle/assets/*.schema.json` cuando corresponda.

## Pedido (una unidad atómica: discovery verificado + borrador spec/plan)

Entregá **discovery** (proceso→código, con citas `archivo:línea`) y **borrador de spec +
plan de tareas** con **postcondiciones verificables** que cubra:

- **(b) Aprobación por rol.** El architect se habilita con la aprobación del plan del epic;
  test-writer, implementer y reviewer exigen la aprobación de **esa spec concreta** (ruta y
  `sha256`). Corrige el I2 circular (`_approved_stage_entry` se aplica hoy a todos los roles)
  sin habilitar atajos.
- **(c) Reemplazo de un paquete preparado y no despachado cuyo contrato cambió.** Registra el
  motivo, conserva el anterior, prepara uno nuevo con la autorización vigente, **sin aprobar
  el contrato nuevo**; un paquete despachado sigue requiriendo reconciliación.
- **(d) Mensajes de bloqueo** que distinguen **aprobación pendiente** / **paquete obsoleto** /
  **estado incoherente**, dicen qué falta y cómo seguir, sin habilitar atajos.
- **(e) Reposo legítimo (VALIDATE-IDLE).** `validate-state` acepta un state en reposo legítimo
  y sigue rechazando uno incoherente.
- **Prueba decisiva del plan:** discovery autorizado sin spec → construcción bloqueada hasta
  su aprobación → recuperación de un paquete obsoleto sin inventar evidencia.
- **Entrada rectificada:** qué pasa con una entrada como la que hoy es
  `stage_history[161]` (`stage: discovery-authorization`, `authorized_by`, `rectified_at`):
  debe **no habilitar nada**; dejalo como postcondición (o test negativo) explícito.

## Formato de salida (TEXTO FINAL — no escribas archivos)

1. **Discovery** — hallazgos con citas `archivo:línea`; mapa del control I2 y del
   reposo/bootstrap v2.
2. **Spec** — postcondiciones observables numeradas `PD-n`, invariantes, criterios de
   aceptación y la prueba decisiva.
3. **Plan** — tareas `T1..Tn` con dependencias y gates de tests (focales + módulos tocados;
   suite completa si se toca instalador/staging/renderer).
4. **Riesgos y decisiones abiertas** para el dueño/orquestador.

No toques tests ni implementación. No inventes evidencia: si algo no lo pudiste verificar en
el código, decilo.
