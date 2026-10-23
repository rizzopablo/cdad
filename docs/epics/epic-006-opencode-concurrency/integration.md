# Epic 006 — integración entre features (E3)

Status: hecha el 2026-10-22 por el orquestador bajo la delegación HITL amplia del owner. Producto: la copia de HOME desplegada desde `adb7c31` (las seis features). Runtime: OpenCode v2.0.32 en modo server, con el servidor permanente de OpenChamber (sin reiniciarlo). Proyecto **descartable**: un worktree del repo con `.cdad` copiado, nunca HOME ni el proyecto activo.

## Recorrido entre features

Un único encargo que cruza las features:

1. **006-006 + 006-004.** `prepare --role reviewer --substage plan-review --contract-kind draft-plan --object-kind spec --contract-path docs/specs/999-int-draft/spec.md --plan-version 1 --current-decision <fila ADR-034>` ⇒ rc=0, paquete `…-reviewer-plan-review-005`. El contrato es `draft-plan` con `object_kind: spec` y `sha256 3527d8f8…`, igual a `sha256sum` del borrador. `PACKET.md` trae `## Current decisions` con la fila de ADR-034.
2. **006-001 + 006-003 + 006-005.**
   - Despacho real por el adaptador instalado (`cdad_delegate.py`, `mode: server`) ⇒ `termination: completed`, recibo `VALID`, `semantic_status: pending`.
   - La sesión del store (leída en `mode=ro`) es `agent: cdad-reviewer`, con el modelo de la configuración del agente instalado e `idle_outcome: succeeded`.
3. **006-006 (recepción).**
   - `materialize` ⇒ rc=0. Escribe `docs/specs/006-004-active-decisions-table/plan-review-int.md` en la carpeta (copia versionada: `integration-plan-review.md`) de la feature activa, byte-idéntico a la parte.
   - El dictamen nombra el objeto y el digest («SHA-256 verificado: `3527d8f8…`») y dice «Este dictamen no constituye aprobación».
   - Aplica la decisión vigente que llevaba el paquete: «ADR-034 se aplicó como criterio; no hay evidencia de que este cambio necesite una abstracción adicional».

## Otras evidencias que la integración reutiliza (no se repiten)

- **AC-3 (concurrencia):** 006-001, PD-6 en `mode: server`. Tres despachos concurrentes `completed`, sin servidores privados ni locks (`execution.md`).
- **AC-4 (fallo recuperable):** 006-005 E4. Write-ahead, `reconcile` ⇒ `dispatched-unknown`, y re-despacho ⇒ `blocked`.
- **Suite completa** al cierre de 006-004: 1458 passed, 5 skipped, 2 failed intermitentes en módulos que no toca ninguna de las últimas features (`docs/specs/006-004-active-decisions-table/closure.md`).

## AC-7 (recepción real en el consumidor)

El propio repo usó como consumidor real el adaptador instalado en modo server para todos los roles de 006-002..006-004, conviviendo con la actividad normal del servidor compartido. Una sesión de otro proyecto activo seguía viva durante 006-004, y el despliegue esperó a que entrara en reposo. **La reanudación de una unidad pendiente del otro proyecto activo no la ejecutó este orquestador:** queda **pendiente del owner**, con siguiente acción: reanudar allí una unidad desde su estado reconciliado con la versión desplegada (`adb7c31`).

**Ejecutada (2026-10-22/23, owner + orquestador del otro proyecto activo).** Con la versión desplegada se retomó una unidad pendiente desde su estado: `status` → `checkpoint` (re-anclaje de contrato aprobado) → `reconcile` rc 0 → disposición `abandoned` del intento fallido previo → `resume` rc 0 → `prepare` de un paquete nuevo → `begin` → despacho nativo → `cdad_dispatch.py record` (con `--parent`/`--since`) → `receive` rc 0, `semantic_status: pending`. **AC-7 cumplido.** El recorrido exigió diagnóstico externo en cada paso; los defectos están en la deuda post-cierre de `closure.md`.
