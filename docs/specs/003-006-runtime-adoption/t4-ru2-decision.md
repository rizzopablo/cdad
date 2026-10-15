# T4 RU-2 — un `checkpoint`/`begin` rechazado deja escrito su cuerpo (orquestador, delegación HITL)

**Defecto real de `cdad_continuity.py` (entregado en 003-004), encontrado en el uso de T4.**
Un `checkpoint` con la misma clave `(execution_id, packet_id, attempt)` que la cabeza y un cuerpo
distinto se rechaza (rc=1, split-brain), como corresponde. Pero **antes de rechazar deja escrito el
cuerpo** en `continuity/bodies/<sha>.json`. En la evidencia está `2aee8d80…` (02:47:40), escrito por
el checkpoint rechazado. Desde ahí, `reconcile --packet <ese paquete>` encuentra dos cuerpos para la
misma clave y falla para siempre con `divergent checkpoint heads` (`evidence/t4/rotation-2-split-brain.md`).
Un rechazo convierte así un error de uso en un bloqueo permanente.

**Cierre:** un `begin` o un `checkpoint` rechazado no escribe nada: ni cuerpo, ni cabeza, ni
directorios nuevos. El cuerpo se escribe solo después de pasar todas las validaciones (todo o nada).
Va como review-fix RED → GREEN. El cuerpo huérfano ya existente lo quita el orquestador a mano
(único escritor), con la evidencia registrada en el ledger.
