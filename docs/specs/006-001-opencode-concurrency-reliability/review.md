Now let me examine the remaining diff artifacts: the adjusted oracles, example config, reference doc, and check anonymization across the diff.
Let me verify the interface's bound and a couple of remaining details (prior-check fail-open coverage, interface kill envelope).
# Informe del reviewer — 006-001-opencode-concurrency-reliability (etapa 4, subetapa `review`)

**Contrato:** spec v2 aprobada (`docs/specs/006-001-opencode-concurrency-reliability/spec.md`, sha256 `dac418b9…`). **Objeto revisado:** diff `f537aa5..HEAD` (HEAD `c03e2f34`). Read-only: `git status --short` vacío al final (verificado). Sesión independiente, sin informe del implementer como prueba; todo verificado sobre el repositorio.

---

## Evidencia (obligatoria del packet)

**Comandos y salidas (repositorio `<repo>`):**

| Comando | Salida relevante |
|---|---|
| `git log --oneline -15` | HEAD `c03e2f3` (docs state); commits de producto dentro del rango ↓ |
| `git diff --stat f537aa5..HEAD` | 23 files, +8638/−676 (incl. docs/state) |
| `git diff f537aa5..HEAD --stat -- skills/ tests/` | 10 files, +6690/−152 |
| `git log --oneline f537aa5..HEAD -- skills/ tests/` | `d0a7963`, `5e5828a`, `ddba831`, `b949849`, `7ccedb4`, `8447443`, `a96c2d8`, `4bc8934`, `91f7e98` |
| `git rev-parse HEAD` | `c03e2f34f475a78613defad5cc94fe37bb73eee0` |
| `git status --short` | vacío (sin modificaciones del reviewer) |

**Archivos modificados por la feature (diff `skills/ tests/`, anonimizados — `<repo>`/`<home>`):\*\*
- `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (+~1389: 2072 líneas finales; adaptador T1/T1b/T2)
- `skills/cdad-cycle/references/cli-delegation.md` (+170/−19), `skills/cdad-cycle/assets/opencode-exec-config.example.json` (nuevo, 22 líneas)
- Focales nuevos: `tests/test_006_001_{t1_selection,t1b_service_mode,t2_wait_recovery,t3_concurrency,t3_integration}.py` (+5192)
- Oráculos ajustados (autorizados por §15): `tests/test_005_009_t2_opencode_adapter.py` (fake `--version` responde antes de `_locate_packet` y del store), `tests/test_005_010_t2_load_mode_invocation.py` (oráculo 1 D-1: `FakeInfoServer` en loopback sirviendo la versión del fake)
- No tocados (verificado en el diff): `cdad_delegate.py`, `OUTPUT_KEYS`, vocabulario de terminación, esquema I8 (INV-4 ✓ para la revisión: sin cambios en ese diff).

**Verificación que NO corrí:** la suite (policy del packet: la corre quien cierra). Mis veredictos se apoyan en lectura de código en contexto + focales/oráculos + informes de rol (`t*-*.md`) + `execution.md` — ver Abstentions.

---

## Blockings

**B1 — El piso `CLIENT_MIN_BUDGET_SHARE` puede romper PD-11 en la banda de cota media (adaptador responde después de la cota de la interfaz)**
- *Severidad:* Required · *Verdict: BLOCKING* · *Bucket: m*
- *Provenance:* `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:1893-1896` (floor ≤ 0,75·budget sin tope superior), `:1817-1820` (budget/gracia), `:1846-1851` (preflight acotado solo por `min(preflight_timeout_configured, remaining)`); interfaz que mata: `skills/cdad-cycle/scripts/cdad_delegate.py:146-149`. PD-11 («siempre antes de la cota»), D-3, §2.5.
- *Mecanismo causal:* el comentario en `:1893-1894` afirma que «the reserve absorbs the overdraft», pero la reserva es fija (1,0 s) y el piso es proporcional al budget. Sea `E` el tiempo consumido antes de invocar al cliente y `B = T − 1 − g` el budget. El adaptador responde en `T_total ≈ E + max(R, 0,75·B) + g + ε`. Si el preflight (o un `--version`/`GET` lento bajo carga, hasta el tope de 5 s por defecto) consume `E > 0,25·B + ~0,8`, un cliente que llega a su límite hace que `T_total > T`: la interfaz mata al adaptador y emite el envelope **`did not answer within N seconds` con `session: null`** — exactamente el resultado que PD-11 prohíbe, perdiendo además la correlación de PD-8. Banda real con defaults: cota ≈ 4-20 s con preflight lento (el escenario de carga del propio epic: load ~9, `execution.md:69`). El banda 2 s de los fixtures es aritméticamente segura (por eso los tests no lo atrapan: `test_pd11_completed_server_mode_with_preflight_stays_within_cota` usa cota 2, y ningún test fija el piso en cota media — verificado: `grep CLIENT_MIN_BUDGET_SHARE tests/` sin resultados).
- *Consecuencia:* en la banda afectada, un preflight lento + colgado el cliente produce un envelope de la interfaz (no del adaptador), sin sesión, con clasificación fabricada; viola PD-11 y arruina la correlación de PD-8 justamente en el entorno de host compartido donde esta feature opera.
- *CONDICIÓN DE CIERRE VERIFICABLE:* acotar el piso para que `E + bound_cliente + g + ε ≤ T` valga siempre, p. ej. `remaining_for_invoke = max(remaining, min(0.75*budget, remaining + max(0.0, WAIT_RESERVE_SECONDS - g - margen_completación)))`, más un focal nuevo: cota ~10 s, preflight retardado >25 % del budget, cliente que se cuelga → el envelope proviene del adaptador (`timeout`, con la sesión elegida) y nunca `did not answer within`.

**B2 — La comprobación de intento previo falla ABIERTA ante store no legible/busy: permite un segundo worker vivo del mismo paquete**
- *Severidad:* Required · *Verdict: BLOCKING* · *Bucket: m*
- *Provenance:* `skills/cdad_delegate_opencode.py:747-749` (`except (_StoreBusy, AdapterError): continue` en `_prior_attempt_check`), documentado como «fail open on the prior check only» en `:726-727`; contra §2.7, PD-9 («nunca re-despacho… el worker puede seguir vivo»), INV-9 (lo no observado es `unknown`, no `ausente`), INV-10 y la interpretación cerrada de §2.3b («no se puede afirmar…» → `blocked`).
- *Mecanismo causal:* tras un `timeout` en modo servicio/servidor, el worker previo sigue vivo en el servicio y escribe intermitentemente en el store. El siguiente intento del mismo paquete lee los registros del ledger (JSON, sin lock), y al leer la fila previa con `timeout=0` puede encontrar `locked`/`busy` (el writer vive) → `continue` → el chequeo pasa vacuoso → se despacha un **segundo worker del mismo paquete contra el mismo servicio**: exactamente el doble-escritor que la precisión del dueño prohíbe y la feature existe para evitar. La lógica del propio spec usa fail-closed «no puedo afirmar → blocked» para `service status`; el intento previo usa lo contrario sin que §2.7 lo defina (la fila no es «ausente»: es *incognoscible*). El código reconoce la tensión y la resuelve hacia el lado débil. El foca T2 no cubre este camino (solo fila legible no-idle/idle: `tests/test_006_001_t2_wait_recovery.py:993,1032`).
- *Consecuencia:* duplicación de worker del mismo paquete en el rincón preciso donde el riesgo es máximo (worker vivo sosteniendo locks).
- *CONDICIÓN DE CIERRE VERIFICABLE:* en `_prior_attempt_check`, un registro previo con `session` no nulo cuya fila **no puede afirmarse** (`_StoreBusy` o store no legible) → `blocked_before_dispatch` con diagnóstico «no se puede afirmar el estado del intento previo», espejo de §2.3b; o, si el orquestador decide fail-open, enmienda declarada en la spec §2.7 con su justificación. Focal: registro previo con fila cuyo store está bloqueado por un escritor persistente del fixture → `blocked` sin invocar `run`.

**B3 — Sin cobertura focal de la cláusula PD-7 nombrada por la enmienda: «fila no idle en modo servicio → timeout (como servidor)»**
- *Severidad:* Required · *Verdict: BLOCKING* · *Bucket: m*
- *Provenance:* spec §2.4 («Se aplica igual en los tres modos efectivos») + §14 fila PD-7 + PD-7 dif.; `tests/test_006_001_t2_wait_recovery.py` cubre standalone (`:804`) y servidor (`:873`) pero **ninguna aserción de espera en modo servicio** (`grep -c service` en el archivo: solo `mode_effective=standalone` en `:664`); T1b cubre preflight/secretos, no la espera post-despacho.
- *Mecanismo:* la implementación lo resuelve compartiendo rama (`_settle_decides`: `!standalone` → settle ignorado, `:633-650`), pero un refactor que ponga `mode_effective == "server"` en vez de `!= "standalone"` dejaría el modo servicio asentando a `unknown` con todos los focas en verde. La spec nombra explícitamente esa fila como diff de la enmienda: la evidencia GREEN reivindica PD-7 completa sin cubrirla. Lo mismo vale para la cláusula PD-11 de la enmienda (preflight de servicio dentro del presupuesto restante): no hay focal de servicio para el presupuesto (solo servidor, `:1337`).
- *CONCIENDICIÓN DE CIERRE VERIFICABLE:* un focal T2: modo `service` (fixture `service status` con URL y versión compatible), fila no idle con `settle_seconds` chico → `timeout` al vencer la cota, `settle` ignorado, sin recibo; y un focal PD-11 de preflight de servicio acotado por presupuesto restante.

---

## Optionals

**O1 — `logs_dir` está declarado pero nadie lo lee; entra en la config de ejemplo que PD-12 exige «cada clave es una que el adaptador lee».**
- *Severidad:* Optional-Consider (literal de PD-12 violado) · *Verdict: OPTIONAL* · *Bucket: m*
- *Provenance:* `skills/cdad-cycle/assets/opencode-exec-config.example.json:7` (`"logs_dir": "<log>"`); `grep -rn logs_dir skills/cdad-cycle/scripts/` → solo el docstring `cdad_delegate_opencode.py:15` (que afirma que se lee); ningún `config.get("logs_dir")` en adaptador ni interfaz.
- *Mecanismo/consecuencia:* un operador que copie la config espera que los logs vayan a `logs_dir`; nada escribe allí. Funcionalmente inofensivo, pero PD-12 queda incumplida según su texto y el docstring es falso.
- *Cierre:* quitar `logs_dir` del asset (o consumirlo) y corregir el docstring `:14-17`.

**O2 — La deuda del flake de la cota de 2 s quedó etiquetada «DT-7» en `execution.md`, pero el DT-7 de la spec es otra deuda (fallback habitual).**
- *Severidad:* Nit · *Verdict: OPTIONAL* · *Bucket: l*
- *Provenance:* `docs/epics/epic-006-opencode-concurrency/execution.md:70` («DT-7: margen de los fixtures de 2 s») vs spec §8 DT-7 («El fallback `service` → `standalone` como camino habitual») y §11 «Flakiness de tiempos» (sin ID ni condición de cierre).
- *Mecanismo/consecuencia:* dos referentes con el mismo ID rompen la trazabilidad de deuda; el flake queda sin condición de cierre verificable.
- *Cierre:* corregir la etiqueta en `execution.md` o registrar el flake como DT nueva con condición de cierre.

**O3 — Anonimización: nombre de modelo/proveedor en la spec aprobada y nombre de otro proyecto en la evidencia del epic.**
- *Severidad:* Nit · *Verdict: OPTIONAL* · *Bucket: l*
- *Provenance:* `docs/specs/006-001-opencode-concurrency-reliability/spec.md:820` (`deepseek-v4.1-flash`, contra la propia regla de anonimización de la cabecera de la spec: sin nombres de proveedor/modelo); `docs/epics/epic-006-opencode-concurrency/execution.md:82,85,96` («OpenChamber», topología/otro proyecto del dueño). Producto (`skills/`, `tests/`): limpio (solo `127.0.0.1` de fixture, permitido).
- *Cierre:* sustituir por `<model>` en la spec y evaluar anonimización de `execution.md` según el destinatario del documento.

**O4 — Celda indefinida en la matriz §2.2: `mode` sin declarar + `server` presente pero inválida.**
- *Severidad:* Optional-Consider · *Verdict: OPTIONAL* · *Bucket: l*
- *Provenance:* spec §2.2 (filas 8-9 solo cubren «URL válida» y «ausente»); código `cdad_delegate_opencode.py:876-881` (decide `none`/`blocked`, comentado como derivación de INV-2).
- *Mecanismo/consecuencia:* la decisión (fail-closed, conservadora y razonable) no está ratificada por la spec; una config v1 con URL malformada pasa de un desperdicio silencioso a `blocked` sin base textual.
- *Cierre:* una fila explícita en §2.2 del orquestador (o del reviewer si se pervierte a standalone).

**O5 — Legibilidad/arquitectura.**
- *Severidad:* Nit · *Verdict: OPTIONAL* · *Bucket: l*
- *Provenance:* `cdad_delegate_opencode.py:1623-2057` (`delegate()` de ~450 líneas con 10+ caminos de cierre); `:323-331` docstring de `_terminate_own_group` («the group killed here is ONLY the adapter's own») es ambiguo — mata el **grupo propio del cliente** (`start_new_session=True` → `pgid` del hijo), nunca el del adaptador. También los focas se importan fixtures entre sí (`tests/test_005_010_t2_load_mode_invocation.py:88-91` importa `FakeInfoServer` desde `test_006_001_t1_selection`).
- *Cierre:* extraer funciones por fase (validación/preflight/espera/persistencia) y reescribir el docstring; considerar un módulo compartido de fixtures.

---

## Abstentions

1. **Atribución técnica plena de los recorridos reales de PD-6** (piernas b/c): solo existe evidencia documental narrada (`execution.md:72-96`, `t3-green.md`); el gate de versión real (2.0.22 vs 2.0.27), la credencial ausente y la topología OpenChamber no son reproducibles desde esta sesión read-only. Verifiqué la **consistencia interna** del relato con la spec (§5.5) y el código, no los hechos en el host.
2. **Suite completa y focales re-ejecutados:** no los corrí (policy del packet: la corre quien cierra, y el host estuvo bajo carga durante el ciclo, lo que sesgaría los focas de tiempos). Los tres veredictos BLOCKING son de análisis estático y de brecha estructural de cobertura — correr los focas actuales no los cambiaría (B1 y B2 no están cubiertos por construcción; B3 es su ausencia).
3. **Ventanas de texto del binario del runtime** citadas en spec §9/D-11 (comportamiento de `cli.server-connection.resolve`, `service status`, esquema del registro): verificado por el architect/orquestador en etapas previas; yo no analicé el binario. Juzgué el código contra la palabra de la spec, no contra el runtime.

---

## Resumen

**3 bloqueantes, 5 opcionales, 3 abstenciones.**

- **B1** PD-11/CLIENT_MIN_BUDGET_SHARE en banda de cota media · BLOCKING · m
- **B2** prior-check fail-open ante store no legible/busy · BLOCKING · m
- **B3** sin focal de la cláusula PD-7 «servicio: no idle → timeout» · BLOCKING · m
- O1 `logs_dir` muerto (PD-12 literal) · O2 etiqueta DT-7 confundida · O3 anonimización (modelo en spec; OpenChamber en docs) · O4 celda indefinida §2.2 · O5 legibilidad/docstring
- A1 recorridos reales PD-6 (solo evidencia documental) · A2 suite no re-ejecutada (policy) · A3 ventanas del binario

---

## Juicios pedidos

**1. Invariante central (la recuperación nunca reconstruye el problema) — CUMPLE, con un rincón a reparar (B2).**
Verificado por lectura de código en todos los caminos: los únicos argv construidos son `run --agent --session [--server|--standalone] [--auto] [--model]` (`:384-392`), `--version` (`:913`) y `service status` (`:1082-1084`) — ningún `serve`, `service start|stop|restart|get|set|unset` ni `reload` en código ejecutable (además oraculizado: `test_006_001_t1_selection.py:195`, `tests/test_006_001_t1b_service_mode.py:586`). Todo «el servicio corre + fallo» termina `blocked` (unexpected `:1177`, versión distinta/no verificable `:1238-1265`, require-true `:1193`), nunca standalone (INV-10); el único fallback es el declarado `service → standalone` por `stopped` con `require:false` (`:1207-1219`), contable en procedencia y probado por el recorrido real (`execution.md:93`, `completed` 33,9 s). No hay re-despacho: exactamente un punto de invocación `run` (`:1905-1911`) y el intento previo no-idle bloquea antes (`:1822-1835`); tras `timeout` en servicio/servidor el diagnóstico advierte worker vivo y no abre standalone (`:1917-1922`, `:1982-1987`). La terminación es ordenada del grupo del cliente (`SIGTERM→gracia→SIGKILL`, `:323-351`) sin tocar servicio ni servidor. La única grieta es B2: con el store no legible en la comprobación de intento previo, el guard falla abierto y puede reconstruir justo el doble-escritor que el invariante prohíbe; y O5 documenta mal esta misma decisión en el docstring de `_terminate_own_group`.

**2. Secretos (D-11, PD-5) — CUMPLE.**
El lector del registro del servicio es una proyección de una sola clave: `_read_service_version` (`:1140-1161`) lee el documento, descarta TODO salvo `version`, y ningún parámetro de salida transporta url/contraseña; la ruta candidata la decide `SERVICE_REGISTRY_RELPATHS` (`:145`), y un OSError/corrupto/clave ausente devuelven `None` → `blocked` (fail closed, `:1238-1252`). La salida de `service status` se descarta al discriminante en `_interpret_service_status` (`:1095-1113`) y ninguna diagnóstico la incluye (el `detail` de `:1178` solo lleva el motivo del timeout). La contraseña del `/api/info` va solo en la cabecera Basic (`:950-953`), nunca en argv (ningún constructor la recibe); el orden de lectura es el del cliente (`:892-902`); la red no usa proxy (`:954`). Barridos: `git diff f537aa5..HEAD -- skills/ tests/` sin rutas del dueño, endpoints ni ids (solo `127.0.0.1` de fixtures); el foca `test_pd5_service_registry_secret_never_in_outputs` (`test_006_001_t1b_service_mode.py:1000`, centinela en el registro) y el recorrido real (`execution.md:76`: URL comparada por digest sin registrarla) corroboran. Residual aceptable y declarado: DT-6 (acoplamiento al archivo no público).

**3. DT-7 (timeouts falsos con cota de 2 s) — deuda de los fixtures, no defecto bloqueante del adaptador.**
La clasificación `timeout` ante ausencia de señal en la cota es el comportamiento contract-estado correcto (§2.4/PD-7); no es un falso positivo del mecanismo. Los dos amortiguadores correctos están implementados: piso del cliente (`CLIENT_MIN_BUDGET_SHARE`, `:189`, defiende contra preflight lento que mataría un cliente sano) y stack HTTP importado perezosamente (`:937-946`, fuera del arranque en standalone/servicio). En uso real la cota es grande, la reserva fija de 1,0 s es despreciable y un `timeout` solo ocurre cuando el worker genuinamente no terminó (riesgo residual declarado §11). Los 3/7 fallos bajo load ~9 (`execution.md:69`) son fragilidad de la cota de 2 s de los fixtures **más** la banda media que B1 descubre (allí sí el adaptador puede mentir, no por error de clasificación sino por morir después de la cota). Conclusión: deuda (arreglar la política de corridas bajo carga y la banda de B1), no bloqueante; O2 para la trazabilidad del DT.

**4. Evidencia real y PD-6 — cerrable como BLOQUEO declarado, pero PD-6 NO está satisfecho y el cierre de la feature no puede reclamar concurrencia demostrada en la topología elegida.**
La spec prevé exactamente este desenlace: §5.5.7 («si el recorrido exigiera algo reservado al dueño, PD-6 queda en BLOQUEO declarado») y D-8. El estado es coherente y bien llevado: (a) fixture con SQLite real → verde (T3 foca, `t3-green.md`); (b) servicio vivo → la pierna c dio `blocked` **por el propio gate D-11** (2.0.22 vs 2.0.27, 1,3 s, sin fallback, INV-10 en producción — evidencia valiosa de que el invariante funciona); luego el dueño detuvo el servicio (2.0.22, imagen borrada) y los recorridos con servicio detenido completaron el fallback declarado y el `require:true` blocked (`execution.md:91-94` — comportamientos conforme a PD-13). Lo que NO existe: ningún despacho real `completed` con `dispatch_flags=none` contra un servicio en la versión del cliente, y las dos concurrencias contra el servidor único de OpenChamber están pendientes de una credencial que el orquestador no tiene. Ambos pendientes dependen del dueño (actualizar/reiniciar el servicio; entregar la credencial) → piernas b y c legítimamente en BLOQUEO declarado. Condición del cierre: registrar explícitamente PD-6 = BLOQUEO declarado con las dos acciones del dueño, y NO usar el único `completed` (33,9 s, vía fallback standalone) como prueba de la topología servicio: ese recorrido eficiente ejercita el adaptador de punta a punta, pero en modo efectivo standalone.

**5. `cli-delegation.md` — correcto y sin promesas de desaparición de bloqueos.**
Contrastado contra §2.2 (tabla de modos idéntica, D-9 texto a texto), §2.3/§2.3b (preflights, orden de credenciales, interpretación cerrada, descarte de la URL, gate D-11 con la barra de deuda DT-6), §2.1 (tabla de claves/defaults idéntica), INV-2/INV-10 (sección «Limits»: nunca gestionar servicio/servidores/store), PD-7/PD-13 (fallback declarado y contable) y D-13 (riesgo residual declarado tal cual). No promete lo que la base no da: declara dos veces, explícitamente, que «**The removal of the store's lock contention is NOT demonstrated**» y que un recorrido exitoso es observación empírica de AC-7. La receta de aislamiento repite la guarda de `debug paths`, el credencial-por-sustitución y «un skip no es un pass» (§5.3/§5.5). Único desvío menor: tampoco documenta la celda indefinida de O4 (coherente con la spec, que tampoco la define). Bien.

---

**No apruebo ni edito: read-only.** Los tres bloqueantes son cerrables con cambios acotados (una línea de tope + un rama de fail-closed + dos focas); recomiendo al orquestador atender B1 y B2 antes de cualquier cierre, y fijar el estado PD-6 en BLOQUEO declarado con dueño y acción de cierre.
