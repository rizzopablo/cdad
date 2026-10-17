I'll start by reading the contract, review, RED report, and the RED test file.
​
​
​
​
​
Now I understand the mechanism. Let me implement the three fixes.
Now the `_prior_attempt_check` fail-closed change (B2):
Now the caller-side block and the B1 capped floor:
Let me instrument temporarily to measure the real timings (I'll remove the debug before committing).
15/15 pass with the margin at 0.8. Now let me remove the temporary instrumentation.
Now the required foreground test runs — focal first:
The fail-closed path also catches a nonexistent store, which breaks two approved oracles (their second dispatch legitimately uses a store not yet created). Per §2.7 ("fila ausente no bloquea"), I need a precise distinction:
Now the full `test_006_001_*` regression set (per file, to isolate any timing flake):
All required tests pass. Committing the two files:
All required runs green and the commit is clean. Final report:

## Archivos modificados (commit `161c9ff`, solo producto — `tests/` intacto)

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` | B1 + B2 + O1 (docstring) |
| `skills/cdad-cycle/assets/opencode-exec-config.example.json` | O1 (`logs_dir` fuera) |

```
$ git show --stat HEAD
 .../assets/opencode-exec-config.example.json       |  1 -
 .../cdad-cycle/scripts/cdad_delegate_opencode.py   | 92 +++++++++++++++++++---
 2 files changed, 79 insertions(+), 14 deletions(-)
```

## Resumen por bloqueante

**B1 (PD-11 / D-3 / §2.5) — piso `CLIENT_MIN_BUDGET_SHARE` acotado.** Constante nueva `COMPLETION_MARGIN_SECONDS = 0.8` y tope del piso:
```python
remaining = max(0.0, wait_deadline - time.monotonic())
floor_ceiling = remaining + max(0.0, WAIT_RESERVE_SECONDS - grace - COMPLETION_MARGIN_SECONDS)
remaining_for_invoke = max(remaining, min(client_floor, floor_ceiling))
```
queda `E + cota_cliente + gracia + margen ≤ cota_interfaz` siempre: el piso solo gasta la reserva que la gracia y el margen dejan libre. El adaptador responde con su envelope (`timeout` + sesión elegida); la interfaz ya no lo mata (`did not answer within` / `session: null` desaparece). **Honesto:** con la gracia de los fixtures/defaults (`g ≥ 0.2`) el tope da extra 0 (la reserva la consume la gracia + el margen), así que en esa banda el piso no eleva la cota del cliente — PD-11 manda; el piso sigue vivo con gracia chica. Medido (instrumentación temporal, removida): respuesta del adaptador a ≈9.33–9.39 s de cota 10 s → 15/15 y 5/5 corridas verdes.

**B2 (PD-9 / INV-9 / INV-10 / §2.7) — intento previo innegociable.** `_prior_attempt_check` ahora devuelve `unaffirmable_session` cuando el store **existe** pero la fila no puede afirmarse (`_StoreBusy` = escritor vivo sosteniendo el lock, o `AdapterError` = ilegible/esquema desconocido) y el llamador bloquea **antes del despacho**: `blocked`, sin `run`, `session: null`, diagnóstico «no se puede afirmar el estado del intento previo … Lo no observado es `unknown`, nunca «ausente» … INV-3/INV-10». Docstring «fail open» reemplazado. **Nuance de contrato:** un store **inexistente** es un hecho determinante distinto (§2.7 «fila … ausente no bloquea»; ningún escritor puede sostener un store que SQLite todavía no creó) y no bloquea — necesario para no romper oráculos aprobados (005-009 T2 PD-5/PD-6 despachan dos veces con stores distintos, el segundo aún no creado). Declarado en el docstring.

**O1 (PD-12).** `logs_dir` eliminado del asset de ejemplo; el docstring del adaptador ya no lo declara leído (línea 1 de «What this adapter does»).

**B3:** ya verde en RED (cobertura declarada por el test-writer); no requería cambio — sigue verde.

## Comandos y líneas finales

```
$ python3 -m ruff check skills/cdad-cycle/scripts/cdad_delegate_opencode.py
All checks passed!

$ timeout 280 python3 -m pytest tests/test_006_001_reviewfix.py -q          # focal
....                                                                     [100%]
4 passed in 18.99s

$ for i in 1..5: pytest tests/test_006_001_reviewfix.py::TestB1AdapterEnvelopeWithinCota -q
1 passed in 10.50s / 11.60s / 11.40s / 10.50s / 10.54s

$ timeout 1800 python3 -m pytest tests/test_006_001_reviewfix.py tests/test_006_001_t1_selection.py \
    tests/test_006_001_t1b_service_mode.py tests/test_006_001_t2_wait_recovery.py \
    tests/test_006_001_t3_concurrency.py tests/test_006_001_t3_integration.py \
    tests/test_005_009_t2_opencode_adapter.py tests/test_005_010_t2_load_mode_invocation.py \
    tests/test_005_010_reviewfix.py tests/test_005_010_t3_references.py -q
81 passed, 1 skipped in 143.08s (0:02:23)
```

**Flakes declarados (DT-9):** en una primera pasada por archivos con load ~7.9 fallaron 3 tests (`t1_selection::test_pd4_same_errand_in_server_mode`, `t1_selection::test_pd5_client_stderr_url_redacted_before_diagnosis`, `t1b::test_pd13_no_management_invocations_in_any_mode`); repetidos aislados dieron verde (`1 passed in 2.02s`; `18 passed in 32.55s`) y la corrida consolidada final fue 81 passed. Fallo de margen bajo carga, no del contrato.

```
$ git commit -m "fix: 006-001 review-fix GREEN (B1 piso del cliente acotado por la reserva; B2 intento previo innegociable ante store ocupado; O1 logs_dir fuera del asset)"
[main 161c9ff] 2 files changed, 79 insertions(+), 14 deletions(-)
$ git status --short      # vacío
```

Commit **`161c9ff`**, solo los dos archivos de producto; sin `--no-verify`, sin stash, sin push, sin tocar HOME, sin ejecutar el runtime/servicio reales. Suite completa no corrida (policy: la corre quien cierra).
