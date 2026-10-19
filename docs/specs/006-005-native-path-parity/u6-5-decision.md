# U6-5 — registro write-ahead del intento externo (enmienda)

Status: Decisión del orquestador bajo la delegación HITL amplia del owner (2026-10-19), pendiente de review contra E4 antes del RED.

## Problema (evidencia)

Ver `docs/epics/epic-006-opencode-concurrency/execution.md`, «006-005 U6: recorrido real», E4 y U6-5.

Por la vía externa, el módulo OpenCode registra su intento I8 **al terminar**. Esa regla viene de 006-001: D-5 / PD-3, «registro de worker en toda terminación». Si el proceso de `dispatch` muere con el cliente del runtime vivo (caída del coordinador, timeout de la herramienta de shell de un coordinador agente, OOM), pasa lo siguiente:

- no queda registro, el paquete sigue `prepared` y `reconcile` dice `not-started` / `repeat_effect: false`;
- `disposition` se niega («only a dispatched packet can be dispositioned»), y el siguiente `prepare` se niega («complete or fail it», PD-4);
- el huérfano termina y commitea sin que el estado lo registre;
- el chequeo de intento previo (PD-9 de 006-001, INV-10) no encuentra registro y un re-despacho abriría un segundo escritor.

E4 de 006-005 («un intento que **no vuelve** … sin repetir efectos») y la condición (d) de PD-19 no se cumplen. El único rodeo sería editar el estado a mano, que el método prohíbe.

## Lectura de los consumidores (sin cambios)

Los tres consumidores ya tratan bien un registro con sesión y sin recibo:

- `reconcile`: un despacho registrado sin recibo es `dispatched-unknown`, «repeating is not authorized» (`cdad_continuity.py`, `_classify`).
- `disposition`: exige un registro de despacho y entonces deja el paquete en `failed` (PD-19).
- Intento previo (PD-9 de 006-001): un registro previo del mismo paquete cuya fila existe sin idle ⇒ `blocked`, sin invocar `run`.

Falta solo que el registro exista **antes** de que el cliente pueda producir efectos.

## Decisión

- **D-U65-1 (write-ahead).** El módulo externo escribe su registro I8 **antes de lanzar el cliente** del runtime: después de cargar `REQUEST.json`, de elegir el id de sesión y de pasar el chequeo de intento previo. Lleva lo que ya sabe: `session` (la elegida), `model_configured`, `started_at`, runtime, rol y subfase. `model_reported` sale `null`, y su procedencia lo declara **pendiente de observación al terminar**. Una terminación anterior al lanzamiento registra como hoy, en esa terminación.
- **D-U65-2 (una sola compleción).** Al terminar, el **mismo** registro del mismo intento se completa **una vez**: solo `model_reported` y su procedencia, desde la fila del store (se conserva D-ADP-2). Cualquier otra diferencia sobre un registro existente se sigue rechazando: el ledger mantiene la identidad write-once. Un registro sin campos pendientes no admite compleción. PD-1 se mantiene: un registro por despacho.
- **D-U65-3 (consumidores).** `reconcile`, `disposition` y el chequeo de intento previo no cambian. Después de una caída, la secuencia es esta:
  1. `reconcile` ⇒ `dispatched-unknown`, sin autorizar la repetición;
  2. `disposition` ⇒ `failed` y `validate-state` VALID;
  3. el siguiente `prepare` procede;
  4. un re-despacho del mismo paquete con la sesión viva ⇒ `blocked`.
- **D-U65-4 (vía nativa: límite declarado).** `record` es posterior por construcción: la sesión la crea la herramienta del runtime. Un coordinador que muere antes de `record` no deja registro. La recuperación disponible es que el siguiente coordinador ejecute `record` del paquete con `--parent`/`--since`. Se declara límite en §9 de la spec, y la evidencia de E4 se acota a la vía externa.
- **D-U65-5 (la salida del huérfano: deuda).** Después de `failed`, el texto final del huérfano queda en el store sin escenificar. Sus efectos en git son visibles, y el registro nombra la sesión para que el orquestador la inspeccione. Recuperar esa salida como entrega tardía desde el store queda como deuda con disparador. PD-19 conserva el tratamiento de entregas tardías ya escenificadas; no lo amplía.

## Contratos que toca

- **006-001:** cambia el momento de D-5 / PD-3 («registro en toda terminación» pasa a «registro antes del lanzamiento, completado en la terminación»). PD-8 no cambia: `session` es la elegida en toda terminación posterior al arranque.
- **Ledger** (`cdad_packet.py prepare --record-dispatch`): la regla write-once admite una sola compleción de campos declarados pendientes.
- **006-005:** E4 queda cubierto por la vía externa; D-U65-4 entra a §9 como límite.

## Oráculos del RED

Se ejecutan a nivel de proceso, con el módulo real, un binario falso que duerme y un store descartable:

1. Caída del grupo de `dispatch` a mitad de la corrida, y luego:
   - existe un registro I8 con la sesión;
   - `reconcile` no declara segura la repetición;
   - `disposition` ⇒ `failed`, con `validate-state` VALID;
   - el siguiente `prepare` procede.
2. Re-despacho del mismo paquete con la sesión viva (fila sin idle) ⇒ `blocked`, sin invocar `run`.
3. Una terminación normal deja exactamente **un** registro, con `model_reported` del store.
4. Una segunda compleción, o una compleción que cambia otro campo ⇒ rechazo.
5. Una terminación anterior al lanzamiento registra como hoy.
