# Plan-review de la spec 007-003 — 2026-10-24

Dictamen: **NO APTO**. Tres BLOCKING, todos de contrato (no de redacción).

## BLOCKING 1 — la cadena histórica exigida no puede reconstruirse con el almacenamiento descrito
`spec.md:59-67,94-98,139-140` frente a `cdad_continuity.py:557-581,609-624,684-688,781-798`.
El cuerpo no incorpora el enlace anterior; `prev_checkpoint_sha256` vive sólo en la cabeza, que se reemplaza, y la verificación mira únicamente el cuerpo inmediatamente anterior. Tras varios checkpoints hay cuerpos direccionados por contenido pero no sus enlaces, así que no puede probarse pertenencia a la cadena vigente. Afecta PC-03/04/06: dos implementaciones válidas pueden aceptar huérfanos o rechazar cierres legítimos.
**Cierre exigido:** representación aditiva del enlace histórico dentro del almacenamiento existente, sin reescribir cuerpos antiguos, y tratamiento explícito de historia no demostrable; caso con varios enlaces posteriores y un cuerpo huérfano que no cuente.

## BLOCKING 2 — la identidad del cierre incluye los datos cuya discrepancia debe detectar
`spec.md:67`. Con identidad `(execution_id, packet_id, attempt, path, sha256)`, cambiar ruta o digest produce otro cierre, no un conflicto. Falta separar clave de unicidad de contenido comparado y declarar normalización de la ruta durable.
**Cierre exigido:** clave de unicidad distinta del contenido, normalización de ruta, y casos de mismo paquete/intento con digest distinto y rutas equivalentes.

## BLOCKING 3 — falta el origen de `attempt` en la recepción automática
`spec.md:41,54-59,69,163` frente a `cdad_result.py:542-548,599-627`. El recibo no contiene el intento de continuidad y el replay durable retorna antes de cargar contexto/request. §7 resuelve la propagación para despacho y registro, no para recepción.
**Cierre exigido:** declarar cómo todas las entradas de recepción reciben o recuperan `N` sin deducirlo del `attempt-id` textual, qué ocurre si falta o discrepa, y cubrirlo en PC-03/04/05 incluido `receive --late`.

## Observaciones
No hay duplicación con 007-001/007-002 ni registro de intentos nuevo. `changes`/`evidence` mantiene separada la aplicabilidad de la deriva. §7 (agregar, no reescribir) es compatible con `receive --late`, pero depende de resolver identidad e historia.
