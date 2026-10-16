I have the contract, plan (ficha T1b), the T1 RED report, and the fixture machinery. Let me check a few remaining fixture details before writing the T1b focal.
El árbol está limpio. Ahora escribiré el focal T1b con su propio binario envolvedorio falso (que intercepta `service status` y delega el resto en el fake compartido sin modificar) y el accesorio de registro del servicio según D-11.
Ahora ejecutaré el foco y veré cómo se comporta el RED:
Los 16 fallan. Permíteme verificar que cada uno sea un AssertionError por el motivo del contrato adecuado (no por importación/fixture), y verificar si hay algún error que no sea de aserción:
Dos anomalías: los envíos `standalone` de mis pruebas fallan con «the durable session store ... does not exist», mientras que el standalone de T1 es GREEN. Déjame depurar empíricamente la ruta del fixture:
El binario delegado en el falso no se ejecuta en absoluto (sin `store`, sin `calls.jsonl`). Déjame comparar con el fixture de T1 que es GREEN hoy:
T1 standalone pasa con su wrapper. Permíteme probar mi wrapper directamente:
El `wrapper` omite `import os` — la delegación se interrumpe con un `NameError`. Lo corrijo:
Ambos ahora están en RED por las razones correctas. Déjame catalogar cada una de las 16 líneas de fallo para demostrar que todas son AssertionError por la razón del contrato declarada:
Las 16 fallas son `AssertionError`s de contrato con las razones declaradas; cero ImportError/SyntaxError/fixture. Ahora las regresiones de la ficha T1b:
Todas las regresiones en verde (54 aprobados). Ahora confirmaré únicamente el nuevo archivo de prueba:
RED de T1b registrado. Reporte final del rol:

## Summary

**Files modified** (write-scope `tests/`, compliant; nada fuera de `tests/`):
- `tests/test_006_001_t1b_service_mode.py` (nuevo, 16 tests, 1157 líneas) — commit `7ccedb4`. Un solo archivo; el fake compartido, los focales de T1/T2 y `docs/.cdad-state.json` intactos.

**No se leyó implementación:** `skills/`, `scripts/`, `agents/`, `sources/`, `build/`, `install.sh` jamás abiertos. Lecturas: solo `docs/specs/006-001-opencode-concurrency-reliability/` (spec v2, plan v2, t1-red.md) y `tests/`. El comportamiento del adaptador vigente se observó solo por los mensajes de fallo (p. ej. `"invalid 'mode' value 'service': expected one of ('server', 'standalone')"`).

**Piezas de fixture propias** (plan §3, oráculo 3 — binario falso propio sin tocar el compartido):
1. `T1B_WRAPPER_BINARY_SOURCE` (vía `T1bServiceCase.fake_runtime_service`): registra cada invocación en su propio log (`t1b-calls.jsonl`), responde ÉL MISMO `service status` según escenario (`service-scenario.json`: stdout+rc → URL / `stopped` / salida inesperada / rc≠0), y delega `--version` y `run` por `os.execv` al fake real compartido con protocolo intacto. Conjunto de tokens prohibidos propio (refinado del plan): permite `service status`; prohíbe `serve`, `service start|stop|restart|get|set|unset`, `reload`.
2. Registro del servicio de fixture (D-11): esquema `{id, version, url, pid, password}` con contraseña centinela, escrito en directorio de estado descartable (`XDG_STATE_HOME` del subproceso, nunca HOME) en las dos ubicaciones plausibles de la spec (`<state>/service.json` y `<state>/opencode/service.json`, mismo contenido): la aserción es de comportamiento (proyección de la sola clave `version`), no de ruta interna (deuda DT-6). URL del servicio = puerto cerrado de loopback: si el adaptador abriera conexiones (PD-14 lo prohíbe), el despacho feliz no podría completar.

**Mapa test → PD** (docstring del archivo con la versión completa):
- **PD-13** (6): `running_compatible_dispatches_without_flags` (fila corre+compatible de PD-1 + gate versión igual de PD-14 + orden §2.3: service status → --version → run), `stopped_require_false_falls_back_standalone_countably` (pares de fallback PD-3 + sin `--version` en fallback, D-2 + diagnóstico «servicio no disponible»), `stopped_require_true_blocks_before_run` (D-10), `unexpected_output_blocks_never_standalone`, `service_status_rc_nonzero_blocks`, `no_management_invocations_in_any_mode` (INV-2 refinada).
- **PD-14** (4): `version_mismatch_blocks_naming_both_versions` (+ URL del servicio ausente del diagnóstico, PD-5), `registry_absent_blocks_never_standalone`, `version_key_absent_blocks`, `registry_unparseable_blocks` — los tres últimos con «no verificable» en el diagnóstico, nunca standalone (INV-10).
- **PD-3** (2): `provenance_pairs_on_completed_service_dispatch` (7 pares de §2.6 con valores service: `mode_requested=service; mode_effective=service; client_version=1.0.0; server_version=1.0.0; dispatch_flags=none; service_status=running; fallback=none`; `store_reads`/`prior_check_reads` al final), `service_status_not_checked_outside_service_mode` (standalone: `not-checked`).
- **PD-4** (1): `same_errand_in_service_mode` (sha256 stdin, --agent/--session/--model/--auto, PWD, fila durable, completed→receive pending).
- **PD-5** (1): `service_registry_secret_never_in_outputs` (contraseña centinela del registro y URL del servicio ausentes de stdout/stderr/diagnóstico/registros I8/recibo/argv).
- **PD-1** (2): `service_ignores_configured_server` (cero requests a /api/info), `invalid_service_require_type_blocks` (§2.1: diagnóstico nombra la clave).
- **PD-2** (dif. enmienda, sin método propio): cubierta por los oráculos de T1 (`service` es token prohibido en su `NEVER_INVOKED_TOKENS`; exactamente `--version`+`run` en servidor; una sola invocación en standalone), declarados regresión de esta ficha.

**Comandos exactos y líneas finales:**

```
python3 -m pytest tests/test_006_001_t1b_service_mode.py -q -p no:cacheprovider
→ 16 failed in 20.89s
python3 -m pytest tests/test_006_001_t1_selection.py tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py tests/test_005_010_reviewfix.py tests/test_005_010_b1_last_assistant.py -q -p no:cacheprovider
→ 54 passed in 94.43s (0:01:34)
git add tests/test_006_001_t1b_service_mode.py && git commit -m "test: 006-001 T1b RED modo service (service status, gate de version, despacho sin flags, fallback declarado y secretos del servicio)"
→ [main 7ccedb4] 1 file changed, 1157 insertions(+)
```

**RED: los 16 fallan por AssertionError del contrato** (cero ImportError/Sintaxis/fixture):
- Caminos que deben despachar (corre+compatible, fallback standalone, PD-3 service, PD-4, PD-5, PD-1 ignora-server): `'blocked' != 'completed'` — hoy `mode: service` es inválido (conjunto T1: server|standalone) y bloquea sin invocar nada.
- Caminos que deben bloquear por causa del servicio (require true, inesperado, rc≠0, registro ausente, versión distinta): `0 != 1` — hoy NUNCA se invoca `service status` (el blocked de hoy es por la causa ajena «mode inválido»).
- PD-14 no-verificable: `'no verificable' not found in "invalid 'mode' value 'service'..."`.
- PD-3 standalone: `None != '--standalone'` — el registro de worker de T1 existe (con `mode_requested=standalone`) pero SIN los pares nuevos `dispatch_flags=`/`service_status=`/`fallback=`.
- PD-1 require inválido: `'completed' != 'blocked'` — hoy la clave se tolera (despacha standalone).

**Declaración honesta:** en la PRIMERA corrida del focal el envoltorio tenía un `NameError` (faltaba `import os` en la delegación) que contaminaba dos tests con fallo de fixture; corregido ANTES del RED registrado — la corrida con evidencia válida (la de arriba, 20.89s) es la que acredita el RED y es la commiteada. Sin `--no-verify`, sin stash, sin push; sin ejecutar el runtime real ni tocar HOME; sin leer `tests/.sensitive-patterns.local`; la suite completa no se corrió (política: quien cierra, en T3).

**Commit:** `7ccedb4` — `test: 006-001 T1b RED modo service (service status, gate de version, despacho sin flags, fallback declarado y secretos del servicio)`, `git status --short` limpio después.
