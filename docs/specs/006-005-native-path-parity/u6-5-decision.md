# U6-5 — registro write-ahead del intento externo (enmienda)

Status: Decisión del orquestador bajo la delegación HITL amplia del owner (2026-10-19). Revisión 2 tras la review (`u6-5-decision-review.md`, 3 B y 3 O); re-review focal con E4 re-trazado, apta para RED (`u6-5-decision-rereview.md`; O-4 aplicada, O-5 a los gates).

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

## Decisión (revisión 2, tras `u6-5-decision-review.md`: B-1..B-3, O-1..O-3)

- **D-U65-1 (write-ahead provisional, fail-closed).** El módulo externo escribe su registro I8 **antes de lanzar el cliente** del runtime: después de cargar `REQUEST.json`, de pasar el chequeo de intento previo y de elegir el id de sesión.
  - **Contenido:** lo que ya sabe (`session` = la elegida, `model_configured`, `started_at`, runtime, rol y subfase).
  - **Marca:** el registro es **provisional**. La marca es declarada y legible: `provenance.session` empieza con el literal `write-ahead:` y nombra que la observación se completa al terminar. `model_reported` queda `null` mientras sea provisional. El registro provisional conserva la forma de §2.6 de 006-001: la marca va delante del primer literal y los pares van al final (`row=unknown; store_reads=unknown; prior_check_reads=<n>`), con unknown para lo no observado, nunca 0 ni vacío (O-4 de la re-review).
  - **Si el registro falla** (lock, política no reconciliada, escritura): el módulo **no lanza el cliente**. Termina `blocked` con el diagnóstico de la falla, sin efectos del rol. Esto reemplaza, solo para este paso, la regla de 006-001 D-5 «a registration failure never changes the termination».
  - Una terminación **anterior** al write-ahead (preflight, intento previo vivo, request inválido) registra como hoy, en esa terminación, un registro final y no provisional.
- **D-U65-2 (una sola compleción, en toda terminación).** En **toda** terminación posterior al write-ahead (`completed`, `timeout`, `unknown`, `transport-error`, `blocked` posterior al arranque, binario que no arranca) se reemplaza **una vez** la observación del mismo registro:
  - **Se reemplaza:** `session` (según PD-8: la elegida si el cliente arrancó, `null` si no arrancó), `model_reported` desde la fila del store cuando la hay (se conserva D-ADP-2) y **todos** los pares de procedencia de terminación de PD-3 (`row`, `store_reads` igual a la traza de la espera, `prior_check_reads` y `provenance.runtime`). Así el registro final es el mismo que hoy escribe la terminación.
  - **Identidad fija:** `execution_id`, `packet_id`, intento, rol, subfase, runtime y `started_at` no cambian; si difieren ⇒ rechazo.
  - **Una sola vez:** la compleción solo vale sobre un registro con la marca `write-ahead:` y produce uno sin ella. Un registro sin marca (ya final) no admite compleción ⇒ rechazo. Una segunda compleción ⇒ rechazo.
  - Fuera de esto, la regla write-once del ledger no cambia, y PD-1 se mantiene: un registro por despacho.
- **D-U65-3 (consumidores, sin cambios; verificado en la review).** Después de una caída, el registro queda provisional con la sesión elegida, y la secuencia es esta:
  1. `reconcile` ⇒ `dispatched-unknown`, que no autoriza repetir;
  2. `disposition` ⇒ `failed`, con `validate-state` VALID;
  3. el siguiente `prepare` procede;
  4. un re-despacho del mismo paquete con la sesión viva ⇒ `blocked` sin invocar `run`.
- **D-U65-4 (vía nativa: límite declarado).** `record` es posterior por construcción: la sesión la crea la herramienta del runtime. Un coordinador que muere antes de `record` no deja registro. La salida es **procedimental**: el siguiente coordinador ejecuta `record` del paquete con `--parent`/`--since`; `record` registra sobre un paquete `prepared` y el resto del camino es igual. Esto entra a §9 de la spec como límite, y la fila E4 de §3.1 se acota a la vía externa con ese hueco declarado.
- **D-U65-5 (la salida del huérfano: deuda).** Después de `failed`, el texto final del huérfano queda en el store sin escenificar, y el registro provisional queda con `model_reported` null y la marca. Sus efectos en git son visibles, y la sesión está nombrada para que el orquestador la inspeccione. Recuperar esa salida como entrega tardía desde el store queda como deuda con disparador. PD-19 conserva el tratamiento de entregas tardías ya escenificadas.

## Contratos que toca

- **006-001:**
  - **D-5:** el registro deja de escribirse solo al terminar. Pasa a escribirse al arranque como provisional y se completa una vez en toda terminación, y una falla del write-ahead cierra antes de lanzar.
  - **PD-3:** su contenido queda **intacto en el registro final**, porque la compleción reemplaza todos los pares de terminación.
  - **PD-8:** se enmienda su cláusula «antes del despacho `session` sigue `null`» **solo para el registro provisional**. El sobre y el registro final siguen PD-8 tal cual.
  - **PD-9:** no cambia.
- **Ledger** (`cdad_packet.py prepare --record-dispatch`): admite una compleción única de un registro con la marca `write-ahead:`. El resto de la regla write-once no cambia.
- **006-005:** E4 queda cubierto por la vía externa. Entran a la spec el límite D-U65-4 en §9 y el hueco declarado en la fila E4; el orquestador lo aplica como enmienda con registro en `execution.md`.

## Oráculos del RED

Se ejecutan a nivel de proceso, con el módulo real, un binario falso que duerme y un store descartable:

1. **Caída a mitad de corrida** (SIGKILL al grupo de `dispatch` y del módulo con el cliente vivo). Se asertan:
   - un registro I8 provisional, con la marca y la sesión;
   - `reconcile` no declara segura la repetición (`dispatched-unknown`);
   - `disposition` ⇒ `failed`, con `validate-state` VALID y el registro todavía provisional con `model_reported` null;
   - el siguiente `prepare` procede.
2. **Caída entre el write-ahead y el lanzamiento:** el mismo camino de recuperación que en 1.
3. **Re-despacho** del mismo paquete con la sesión viva (fila sin idle) ⇒ `blocked`, sin invocar `run`.
4. **Terminación `completed`:** exactamente **un** registro, sin marca, con `model_reported` del store, `row=present` y `store_reads` igual a la traza de la espera (PD-3).
5. **Binario que no arranca después del write-ahead:** un solo registro, final, con `session: null` (PD-8) y sin nota de rechazo del ledger. Un `timeout` sin fila completa igual con su procedencia.
6. **Falla del write-ahead:** ninguna invocación del cliente, terminación `blocked` con el diagnóstico y el paquete sin efectos.
7. **Ledger:** una segunda compleción ⇒ rechazo; una compleción sobre un registro sin marca ⇒ rechazo; una compleción que cambia la identidad ⇒ rechazo.
8. **Terminación anterior al write-ahead** (por ejemplo, un intento previo vivo) ⇒ registra como hoy.
