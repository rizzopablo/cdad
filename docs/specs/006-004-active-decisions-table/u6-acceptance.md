# 006-004 U6 — recorrido de aceptación real (PD-12, PD-9, PD-13)

Status: recorrido del orquestador bajo la delegación HITL amplia del owner (2026-10-22), **sin despliegue a HOME**, por orden del owner (hay una sesión activa en OpenCode que no se debe tocar). La CLI y el adaptador son los del repo en HEAD `efc1b2e` (U1–U5 y U7), y corren dentro del proyecto descartable. Runtime: OpenCode v2.0.32 en modo server (el servidor permanente, sin reiniciarlo), con los agentes globales instalados. Proyecto **descartable**: un worktree del repo con `.cdad` copiado. Nunca HOME como proyecto ni el proyecto activo. Las rutas del host se reemplazaron por `<walk>`.

## Resultado por escenario

| Escenario | Resultado | Evidencia (salida real) |
|---|---|---|
| **E1** la fila llega al rol nombrado | Cumple | `prepare --role test-writer --current-decision <fila ADR-006>` ⇒ rc=0, paquete `…-test-writer-red-007`. `REQUEST.current_decisions` trae la fila con sus cinco campos. `PACKET.md:26` tiene `## Current decisions` con `Decision: docs/adr/ADR-006-…`, state, summary, roles y reference, antes de `## Task validation plan`. Negativo: la fila de ADR-034 (architect y reviewer) en un paquete del test-writer ⇒ rc=2 «does not name the packet role 'test-writer' … (R-5)». |
| **E2** fila reemplazada | Cumple | En la tabla sembrada, ADR-007 está `obsoleto (reemplazado por ADR-033)`. Declararla en un paquete ⇒ rc=2 «is not admissible in a packet: it is obsoleto and superseded by docs/adr/ADR-033-modelos-por-configuracion-sin-perfiles.md (R-6)». |
| **E3** sin filas aplicables; fila ajena | Cumple | **Byte-identidad en la misma revisión:** se renderiza el `REQUEST.json` del paquete E1 sin el campo `current_decisions` (`render` rc=0) y se compara con su `PACKET.md` menos la sección (cuerpo debajo de la cabecera JSON) ⇒ «body identical without section: True», sha `2a500f666c7f` en los dos lados. Un paquete del implementer sin filas ⇒ sin sección y sin la clave en `REQUEST.json`. **Fila ajena:** ADR-034 en un paquete del implementer ⇒ rc=2 «does not name the packet role 'implementer' … (R-5)». |
| **E4** la fila apunta a un ADR inexistente | Cumple | En la CLI, una fila con archivo inexistente declarada en un paquete ⇒ rc=2 «the file does not exist in the project (R-3)». **Hallazgo del reviewer** (despacho real, paquete `…-reviewer-review-001`), sobre la fila `ADR-901-no-existe.md` que el orquestador escribió en la tabla: «B-1 — La tabla declara vigente un ADR inexistente · Ubicación: `docs/systemPatterns.md:38` · Verdict: BLOCKING · Bucket: m», con la condición de cierre «retirar la fila fantasma … o corregirla para que represente una decisión realmente aprobada cuyo archivo exista … No basta crear un archivo vacío». Es un hallazgo, no una puerta: el estado no cambia por él. |
| **E5** proyecto sin ADR | Cumple | Con `docs/adr/` retirado del worktree: `prepare` del implementer ⇒ rc=0, sin `## Current decisions`. El render del mismo `REQUEST.json` con `current_decisions: []` es idéntico en el cuerpo («empty list body identical: True»). |
| **E6** la casa del principio | Cumple | `skills/cdad-cycle/references/design-principles.md` existe en el árbol instalable. `agents/cdad-architect.md` y `agents/cdad-reviewer.md` lo nombran, y `references/stage-4-review.md` también. |
| **E7** la cadena del CAS (DEC-13) | Cumple; hallazgos **W-U6-1** y **W-U6-3** | Ver la cadena abajo. |
| **V-5** dos fases entre revisiones | Cumple | Se publica el paquete `…-test-writer-red-007` con la fuente `packets/substages/test-writer-red.md` en `3dfd2985…`. Se cambia la fuente (`05441863…`) y se recibe una entrega preparada ⇒ rc=2 «packet differs from its canonical rendering (validate-packet)». La política declarada (`references/re-entry.md:207-208`): «finish it under the revision it was published with, or prepare a new one under the revision now in force». La fuente se restauró. |

## E7 — la cadena del CAS, paso a paso

| Paso | Qué | Digest / resultado |
|---|---|---|
| 1 | **D0**: el orquestador registra la base al preparar el paquete del scribe `…-scribe-memory-001` (la base también va en el objetivo) | `docs/systemPatterns.md` = `ff7b9218d1928e85…` |
| 2 | **Propuesta sobre D0**: despacho real del scribe ⇒ `termination: completed` | parte `b4bf34e9a228…` |
| 3 | **D1**: el orquestador escribe su fila (`ADR-900-recorrido-u6.md`, con su archivo) directamente en `docs/` y commitea | `3d26947d027ff25f…`; el validador permanente pasa las comprobaciones de la tabla (solo falla F011, la deriva ambiental conocida) |
| 4 | **Rechazo**: `materialize` con `expected_previous_sha256` = D0 | rc=2 «conflict: target 'docs/systemPatterns.md' current digest does not match expected_previous_sha256 (CAS): refusing to overwrite»; el destino sigue en D1 |
| 5 | **Re-despacho**: se cierra la entrega del 001 (delivery, con la nota del rechazo) y se prepara un paquete **nuevo**, `…-scribe-memory-002`, con base D1 | `prepare` rc=0 |
| 6 | **Propuesta sobre D1**: despacho real ⇒ `completed` | parte `d80370089a73…` |
| 7 | **Materialización** con `expected_previous_sha256` = D1 | rc=0 |
| 8 | **Documento final** = `d80370089a73…`: conserva la fila `ADR-900` que venía en D1 (1 aparición) y trae la línea del scribe | `git diff` D1→final: 8 inserciones, 6 borrados (abajo) |

**Bytes aplicados (diff final contra D1):**

```text
+Recorrido U6: esta linea la agrego el scribe.
-  autorización de repetir, invariante 3). `continuity` **consume** el receipt de 002; **no
-  materializa** (eso sigue siendo del orquestador con autorización explícita). Para
+  autorización de repetir, invariante 3). `continuity` **consume** el receipt de 002; **no**
+  materializa (eso sigue siendo del orquestador con autorización explícita). Para
-  capacidad como observada/documentada/no disponible/desconocida, con el **fallback portable**
+  capacidad como observada/documentada/no disponible/desconocido, con el **fallback portable**
-Última actualización: 2026-10-20 (006-005)
+Última actualización: 2026-10-20 (006-005)
```

No se fusionó a mano ni se retocó el digest esperado. Las líneas que siguen a la del scribe son cambios **no pedidos** (W-U6-1).

## Hallazgos

| Id | Clase | Estado |
|---|---|---|
| W-U6-1 | fidelidad del rol: en las dos propuestas, el scribe cambió líneas fuera de lo encargado (negrita, «desconocida→desconocido», un espacio final), aunque el objetivo decía «no cambies ninguna otra línea». El CAS protege la concurrencia, no la fidelidad. La salida existente es la revisión del diff del Memory Bank antes de aprobarlo | observación; no es de 006-004 |
| W-U6-2 | el adaptador lanzó una sesión nueva para un paquete que ya tenía una entrega completa y un receipt durable. Fue un error del orquestador: el script del recorrido volvió a despachar el paquete viejo porque `prepare` había fallado, y eso pasó dos veces. Los clientes se cortaron y quedaron dos sesiones del scribe huérfanas, de solo lectura y solo en el store (`ses_3f25…`, `ses_0cd0…`). La salida de 006-005 E4 («re-despacho ⇒ blocked») cubre el caso `dispatched-unknown`, no este | **a verificar**: se registra como deuda. Causa no investigada |
| W-U6-3 | ergonomía del CAS hacia el Memory Bank: el adaptador entrega una sola parte `role-report`, cuya raíz permitida es la carpeta de la spec. Materializar a `docs/systemPatterns.md` exigió que el orquestador recibiera la misma entrega con un descriptor propio de clase `scribe-systemPatterns`. Las clases ya existen en la política cerrada; lo que falta es que el adaptador las declare | observación de la cadena; no bloquea (el CAS se ejerció con el producto real) |
| — | `register-transition --transition delivery --artifact` rechaza el digest de un artefacto que cambió después; se omitió la aserción, como pide el mensaje | conforme |
