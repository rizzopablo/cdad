# Fixtures 003-004-context-continuity (T2) — **SIMULACIÓN**

Todos los artefactos de este directorio son **simulaciones de datos**
(criterio  de adopción P8: "los fixtures cubren crash/restart/split-brain/
stale/autoridad vencida/tarea cerrada **sin rehacer un trabajo ya cerrado
ni provocar incidentes reales**"). Ningún fixture representa un incidente
real: son formularios de los stores reales, sembrados por los tests foca-
les de T2 en proyectos sintéticos (tempdirs), nunca en este repo:

- `.cdad/runtime/results/<execution_id>/<packet_id>/receipt.json` — receipt
  de 002 (forma observada en `tests/test_003_002_t1_receive.py`).
- `.cdad/runtime/results/<execution_id>/<packet_id>/parts/<name>.utf8`
  — parts staged del bundle del receipt.
- `.cdad/runtime/materializations/<execution_id>/<packet_id>/<auth>.json`
  — journal de materialización de 002
  (`tests/test_003_002_t2_reviewfix.py:42`).
- `.cdad/executions/<execution_id>/dispatches/<attempt>.json` — registro I8
  del despacho (forma observada en `tests/test_004_002_t4_dispatch.py`).

El CLI (`cdad_continuity.py reconcile/resume/begin/checkpoint`) lee estos
stores **sólo como datos** (D10: consume el receipt como oráculo, no mate-
rializa; un receipt NO es aprobación semántica, `semantic_status` siempre
`pending`).

## Matriz (mapa fixture → caso de spec §2 → test)

| Fixture | Caso §2 simulado | Test consumidor |
|---|---|---|
| `dispatch-dispatched.simulacion.json` | dispatch I8 sin receipt → `dispatched-unknown` | `test_003_004_t2_reconcile.py` (matriz) |
| `receipt-received.simulacion.json` (+ parts) | Efecto ya recibido → `received`, sin ofrecer repetir | matriz + escenario continuo |
| `materialization-closed.simulacion.json` | Efecto ya materializado/tarea cerrada → `already-closed`, sin retrabajo | matriz + escenario continuo |
| `receipt-unreadable.simulacion.json` | Sin señal fiable → `unknown` (no fabrication) | matriz |

Los casos **split-brain** (cabezas divergentes) y **stale/tamper** se
siembran contra el store content-addressed de continuuity
(`.cdad/executions/<id>/continuity/{head.json,bodies/}`), creado por la
superficie real de T1; y la **autoridad vencida** se simula con el
`expires_on` del execution context del tempdir. La divergencia se siembra
como **dos cuerpos de la MISMA clave** `(execution_id, packet_id,
attempt)` en `bodies/` (content-addressed: nombre = sha256 de los bytes
del archivo), con el head sin mover — D7: "cabezas divergentes o
igual-digest-con-cuerpo-distinto → escalar".

Los marcadores `@EXECUTION_ID@` y `@PACKET_ID@` de las plantillas son
sustituidos por los tests al materializar el fixture en el tempdir
(los digests de parts/bundle se recalculan en el momento sobre los bytes
sembrados para que el receipt sea consistente internamente).
