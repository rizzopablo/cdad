I'll start by reading the contract inputs and the RED tests.
Now let me read the T1 selection test (base class) and the plan's T1b card.
I have enough context. Let me verify there are no other callers I'd break, then implement.
Now let me implement. First, the constants:
Now the `_invoke_destination` signature and argv:
Now `_observation`:
Now `_persist_delivery`:
Now `_validate_service_keys` and `_resolve_mode_effective`:
Now the service preflight helpers, inserted after `_preflight_server`:
Now the `delegate()` flow. Let me read the current state of that region:
Now the preflight branch and dispatch:
Now let me sanity-check syntax and run the focal test:
The fallback's diagnosis is dropped on the completed path. Let me carry the preflight note into the envelope:
Focal green (16 passed). Now the proportional regressions:
A known 2 s timing race (declared in the task). Let me re-run that regression isolated:
Isolated it passes. Re-running the combined regression set to confirm it's the declared load-dependent race:
All 54 regressions green on re-run (the earlier single failure was the declared 2 s timing race under load). Let me verify scope and re-run the focal for stability:
Let me update the module docstring to document the new service mode:
Now commit the adapter only:
Done. GREEN de T1b alcanzado.

## Archivos
- **Modificado:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (+366/-22). Único archivo del commit `b949849`. `tests/**`, `cdad_delegate.py`, `OUTPUT_KEYS`, vocabulario de terminación y esquema I8 intactos (`git status` limpio; solo el adaptador).

## Resumen por postcondición / PD
- **PD-13 / §2.2-§2.3b.** `VALID_MODE_VALUES` ahora `("server","service","standalone")`; `_resolve_mode_effective` marca `service` como provisional y `_preflight_service` decide el modo efectivo. `service status` se invoca **exactamente una vez** y es la **única** invocación de `service` (nunca `serve`, `service start|stop|restart|get|set|unset` ni `reload`). Interpretación cerrada: una línea URL http/https con host y sin userinfo → **corre**; literal `stopped` → **no corre**; vacío/varias líneas/no reconocible/rc≠0/timeout → **inesperado → `blocked`** (nunca standalone). Corre+compatible → `run` **sin flags**; no corre + `require:false` → `--standalone` con el fallback declarado y contable + diagnóstico «servicio no disponible»; no corre + `require:true` → `blocked` antes de `run`.
- **PD-14 / D-11.** `_read_service_version` proyecta **una sola clave `version`** del registro del servicio bajo `XDG_STATE_HOME` (`<state>/opencode/service.json`, `<state>/service.json`), **sin red, sin contraseña, sin URL**. Igual → despacho sin flags; distinta → `blocked` nombrando **las dos** versiones + acción siguiente; ausente/no parseable/clave ausente o no textual → `blocked` «versión del servicio no verificable». **Nunca** standalone con el servicio corriendo (INV-10).
- **PD-3 / §2.6.** Tres pares nuevos **al final** de `provenance.runtime`: `dispatch_flags=`, `service_status=`, `fallback=`; `mode_requested`/`mode_effective` aceptan `service`; `service_status=not-checked` fuera del modo servicio; pares de sesión (`store=`, `row=`, `store_reads=`, `prior_check_reads=`) intactos y con `prior_check_reads=` **al final**.
- **PD-1.** `service` ignora `server` (0 requests a `/api/info`); `service.require` no booleano → `blocked` antes de todo, diagnóstico que nombra la clave (validación incondicional, D-10).
- **PD-4 / PD-2 (dif. enmienda).** `run` sin flags transporta el mismo encargo (sha256/PWD/--agent/--session/--model/--auto/identidad durable/receive `pending`); `--version` **solo si el servicio corre** (D-2); `service status` no se invoca en servidor ni standalone.
- **PD-5 / INV-6.** La salida de `service status` se descarta salvo el discriminante; ni la URL del servicio ni la contraseña del registro entran en argv, diagnóstico, registros I8, stderr ni recibo.

## Comandos (líneas finales)
- Focal `python3 -m pytest tests/test_006_001_t1b_service_mode.py -q -p no:cacheprovider` → **`16 passed in 25.73s`** (verde estable, corrido 2×).
- Regresiones de la ficha (7 ficheros, misma invocación combinada) → **`54 passed in 94.05s`**. En la **primera** corrida combinada falló `test_pd1_mode_server_with_valid_url_dispatches_server_flag_only` con `'timeout' != 'completed'` (`destination 'opencode' did not answer within 2.0 seconds`): es la **carrera de tiempos conocida** de fixtures con cota de 2 s (la resuelve T2). **Repetido aislado → `1 passed in 2.07s`**; y la corrida combinada repetida → **54 passed**. Declarado, no oculto.
- `tests/test_006_001_t1_selection.py` aislado → **`18 passed in 28.27s`**.

## Commit
`b949849` — `feat: 006-001 T1b GREEN modo service (service status unico, gate de version D-11, despacho sin flags, fallback contable y secretos)` — `1 file changed, 366 insertions(+), 22 deletions(-)`, solo `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`.

## Desviaciones / límites
- Sin desviaciones de alcance: no se tocó nada de T2 (Popen/grupo, backoff, settle, intento previo, gracia) ni la interfaz.
- Un test flaqueó por la carrera de tiempos ya declarada; se repitió aislado y en conjunto y quedó verde — no se editó ningún test.
- Nota de diseño: `dispatch_flags` en un bloqueo **pre-despacho** de standalone se registra como `--standalone` (el flag que se habría usado); no lo asserta ningún test de T1/T1b y T2 no lo cubre.
