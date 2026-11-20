All evidence collected. Final report:

---

# FINAL TEXT — implementer GREEN T6 review-T6-002 (017-001-suite-performance), packet `017-001-suite-performance-implementer-green-010`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única en el prompt (`packet_id` …-green-010, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json --execution-context …/execution.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md --execution-context …` → **EXIT 0**.
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C. **No cargué `cdad-cycle` ni otro skill de ciclo**: el packet es el contrato.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.
- Solo leí insumos declarados + alcance (`docs/specs/017-001-suite-performance`, `scripts`, `tests`); solo edité el write_scope (`scripts/`). **No toqué `tests/`** (`git diff --numstat -- tests/` vacío) **ni el contrato**.

## 2. Implementación (solo `scripts/cdad-suite.py`, +220/−14, commit `1428f27d`)

**Bloqueante 1 — familia de procesos real (review-T6-002 §1):**
- Cada worker se lanza con `start_new_session=True` (grupo de procesos propio); el `pgid` se registra por worker en `parallel.json` y en `parallel.md`.
- Tras esperar al hijo directo (poll por proceso, semántica de paredes M2 intacta), se barre `/proc/*/stat` por `pgid` (sin depender de la línea de comandos), excluyendo invocador y ancestros.
- Si queda familia viva: se informa (`orphans`/`orphans_found`/`orphans_cleaned`/`orphans_remaining` totales y por worker), se termina (TERM, luego KILL) y se espera; la corrida **no termina con éxito limpio** (sale `3`, veredicto `discarded: orphaned process family…`). En corrida limpia `orphans` es `0` entero y el estado es exitoso.
- El fallo parcial de lanzamiento aplica la misma limpieza por grupo (`_parallel_reap` + `_parallel_reap_pgrp` por `pgid` lanzado).
- Helpers nuevos: `_self_and_ancestor_pids`, `_pgrp_of`, `live_pids_in_pgrp`, `_parallel_reap_pgrp` (nunca toca el grupo propio del runner).

**Bloqueante 2 — canario que descarta (review-T6-002 §2):**
- Si el canario de configuración (`delta_lines != 0`) o el del checkout (`unchanged == false`) detectan cambios: `parallel.json` trae veredicto explícito (`rejected: canary detected changes, run discarded…`), sale distinto de 0 (`3` si pytest era 0) y **conserva la evidencia**. En corrida limpia sale 0 con veredicto `accepted`.
- Sin cambios en la semántica de paredes, partición, preparación ni `close`.

## 3. Evidencia: comandos, salidas y números

- `python3 -m py_compile scripts/cdad-suite.py` → COMPILE-OK.
- **Focal T6 completa (14):** `python3 -m pytest tests/test_017_001_suite_parallel.py -q -p no:cacheprovider` → **14 passed en 59.63 s** (incluye N1 `…without_cmdline_marker` y N2 `…altered_checkout_canary`, que antes fallaban con `orphans=0` y `rc=0`).
- **Focales T1/T2/T3/T4:** `… test_017_001_suite_profile.py …_operations.py …_reconcile.py …_external.py` → **41 passed en 45.60 s**.
- **Regresión proporcional** (consumidores de `close`/canarios): `test_008_002_suite_evidence.py`, `test_008_002_suite_selection.py`, `test_008_005_ci_gate.py`, `test_013_002_live_inventory.py`, `test_014_001_suite_evidence_defaults.py` → **60 passed en 45.90 s**.
- `python3 scripts/cdad-suite.py validate` → **rc 0**.
- **Corrida real corta** (dos archivos tranche, `--workers 2`, evidencia en `~/<workspace>/tmp/t6-green-evidence`, fuera del checkout) → **rc 0**: veredicto `accepted`; `orphans 0/0/0 checked True`; worker-0 `pgid=1207531 wall=0.699 s`, worker-1 `pgid=1207532 wall=1.853 s`, `total_wall=1.857 s` (≈ max, arranque conjunto), `overlap=0.696 s`; canario config `unchanged True delta 0`; checkout `unchanged True` (20199 archivos, 434253273 bytes); consolidado `passed=2 failed=0 skipped=0`.
- Higiene: `sleep 60` vivos → 0; centinelas `build/.canary_probe_*` → ninguno (los tests N1/N2 limpian los suyos).
- **Suite completa no realizada**: sin autorización para corrida completa y con prohibición expresa del packet; selección ejecutada: T6 (14) + T1–T4 (41) + regresión (60) + `validate`.

## 4. Archivos y commit

- Modificado: `scripts/cdad-suite.py` (+220/−14). Commit `1428f27d` — solo ese archivo.
- `M docs/.cdad-state.json` es **preexistente al packet** (consta en review-T6-002) y quedó **fuera del commit**, fuera de mi write_scope.

## 5. Límites

- La medición de la corrida corta es una muestra de 2 tests, no la suite completa; las paredes incluyen la carga del host registrada en `parallel.json.host`.
- La limpieza por `pgid` cubre la familia del lote; un `pgid` reutilizado por el SO entre el barrido y la limpieza es un riesgo residual teórico no observado.
- No se ejecutó la suite completa `--all` (sin autorización); la acreditación final con `--all` corresponde a T7.
