I'll start by reading the approved contract, plan, RED report, and the failing tests.
Now let me read the RED report and the failing test file.
Now let me examine the current adapter implementation and git state.
The file already has uncommitted modifications. Let me check the diff against HEAD and the state file.
The working tree already has a T2 implementation (likely a prior attempt). Let me check the state file and run the focal test to see the current state.
Let me run the focal test to see the current state of the work-in-progress implementation.
The focal test passes (12 passed). The working tree already contains a T2 implementation (prior attempt). Let me review the rest of the diff to understand it fully, then verify regressions.
The implementation is complete and coherent. Now let me run the regression set (run 1 of 3 consecutive combined runs).
Run 1 green (93 passed, 1 skipped). Run 2:
Run 2 green. Run 3:
Three consecutive combined runs are green. Let me verify the working tree state before committing.
Only the adapter is modified; tests untouched; no stray processes. Let me verify no forbidden invocations exist in the adapter, then commit.
All checks pass. Let me commit only the adapter.
Committed as `ddba831`. The working tree is clean. Here is the role report.

---

# Implementer GREEN — 006-001 T2 (packet `…-implementer-green-003`)

## Estado de entrada (provenance, declarado)
Al entrar, el árbol ya estaba **sucio** con una implementación T2 completa en el único archivo de write-scope (`M skills/cdad-cycle/scripts/cdad_delegate_opencode.py`, 422+/74−), del linaje previo de este mismo paquete GREEN (HEAD `798cd2c`, "T2 GREEN despachado"). No la reescribí: la revisé contra el contrato, la validé de punta a punta (focal + regresiones + 3 corridas combinadas) y commiteé el adaptador. Tests intactos, `cdad_delegate.py` intacto.

## Archivos
- **Modificado / commiteado:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (1 file, +422/−74).
- **No tocado (verificado por `git status`):** `tests/**`, `skills/cdad-cycle/scripts/cdad_delegate.py`, `cdad_packet*.py`, `OUTPUT_KEYS`, vocabulario de terminación, esquema I8.

## Resumen por PD
- **PD-7 (clasificación tras la salida).** `_await_durable_outcome` clasifica desde el hecho material: idle→outcome; `no-row` + rc≠0 → `transport-error`; `_settle_decides` resuelve **standalone** `no-idle`/`rc0-no-row` a `unknown` al vencer `settle_seconds`; en **server/service** la espera durable sigue hasta la cota → `timeout` (settle ignorado). `_last_idle_message_error` lee el ÚLTIMO `session_message` tipo `idle` y `_classify` acota `error.type`/`error.message` a `IDLE_ERROR_MESSAGE_LIMIT=200`.
- **PD-8 (correlación + terminación ordenada).** `_invoke_destination` corre el cliente con `start_new_session=True`; `_terminate_own_group` hace SIGTERM al grupo → gracia efectiva → SIGKILL al grupo (el nieto muere). Toda terminación post-`Popen` (`timeout`/`unknown`/`transport-error`/`blocked`) lleva la **sesión elegida** en el envelope; pre-despacho o binario no arrancado → `session: null`.
- **PD-9 (intento previo, §2.7).** `_prior_attempt_check` recorre `.cdad/executions/<id>/dispatches/*.json` del mismo `packet_id`, lee la fila previa (ro): fila existente no idle → **`blocked` antes de invocar** (diag nombra la sesión previa); idle/ausente → despacho normal. Sin re-despacho ni standalone (INV-3/INV-10).
- **PD-10 (espera proporcional, §2.4).** Cero lecturas mientras el cliente vive (la espera arranca en `exit_ts`, tras `communicate`); backoff exponencial de `poll_initial_seconds` duplicando hasta `poll_max_seconds`; conexión `mode=ro` con `timeout=0` para que la contención aflore como `_StoreBusy` y gobierne el calendario (no el busy handler de SQLite); **solo lectura, nunca escritura** (INV-1). `store_reads` reporta el conteo y se contrasta con la traza.
- **PD-11 (responde dentro de la cota, D-3).** `timeout_seconds <= WAIT_RESERVE_SECONDS` → `blocked` pre-despacho nombrando la clave; gracia efectiva `g = min(terminate_grace_seconds, 0.25×(timeout−RESERVE))`, descontada del presupuesto (`_wait_budget(timeout, grace)`); piso `CLIENT_MIN_BUDGET_SHARE=0.75` evita que un preflight lento mate un cliente sano con falso `timeout`; el stack HTTP se importa **perezosamente** dentro de `_preflight_get_info` para no pagar el costo de arranque en standalone/service (mitigación de la latencia del orquestador).

**Seguridad verificada:** la única invocación de `service` es `("service","status")`; ninguna argv lleva `serve`, `service start|stop|restart|get|set|unset` ni `reload` (solo aparecen en comentarios/diagnósticos, no en ejecución).

## Comandos y resultados (salidas finales literales)
- **Focal T2:** `python3 -m pytest tests/test_006_001_t2_wait_recovery.py -q -p no:cacheprovider`
  → `12 passed in 30.03s`
- **Tres corridas combinadas consecutivas** (regresiones de la ficha T2 + `t1_selection` + `t1b_service_mode`):
  `python3 -m pytest tests/test_006_001_t1_selection.py tests/test_006_001_t1b_service_mode.py tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py tests/test_005_009_t3_spawn_reconciliation.py tests/test_005_009_t4_acceptance.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py tests/test_005_010_reviewfix.py tests/test_005_010_b1_last_assistant.py -q -p no:cacheprovider`
  - Run 1 → `93 passed, 1 skipped in 120.43s (0:02:00)`
  - Run 2 → `93 passed, 1 skipped in 118.73s (0:01:58)`
  - Run 3 → `93 passed, 1 skipped in 127.64s (0:02:07)`

  Las regresiones con cota de 2 s (modo servidor feliz de `t1_selection`, `t2_load_mode_invocation`, `succeeded-no-text` de `reviewfix`, `test_pd2_unparseable_server_version_blocks`) cerraron verdes en las tres corridas: **el flake de ~1 de cada 3 no se reprodujo** con el piso de presupuesto del cliente y el import perezoso del stack HTTP (no se subió ninguna cota de test).
- **Commit:** `git add skills/cdad-cycle/scripts/cdad_delegate_opencode.py && git commit -m "feat: 006-001 T2 GREEN …"` → `ddba831`, 1 file changed, +422/−74. `git status --short` limpio tras el commit.

Fuera de alcance respetado: sin T3, sin tocar `cdad_delegate.py`/`OUTPUT_KEYS`/vocabulario/I8, sin `git stash`/`--no-verify`/push, sin tocar HOME ni el runtime/servicio real.
