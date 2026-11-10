Route C work complete. FINAL TEXT report below.

---

# FINAL TEXT — test-writer RED review-fix T6 (017-001-suite-performance), packet `017-001-suite-performance-test-writer-red-024`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única en el prompt (`packet_id` 017-001-suite-performance-test-writer-red-024, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json --execution-context …/execution.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md --execution-context …` → **EXIT 0**.
- `python3 scripts/cdad_packet.py render --request … --execution-context … --route C` → identificación canónica **byte a byte igual** a la del dispatch.
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**, sin switch silencioso. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C. **No se cargó `cdad-cycle` ni otro skill de ciclo**: el packet es el contrato.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.
- Solo leí insumos declarados (`spec.md`, `review-T6.md`, `performance/parallelism.md`, `red-T6-parallel.md`, `green-T6-parallel.md`, `tests/test_017_001_suite_parallel.py`, tranche1/2 como selecciones livianas) y solo edité el write_scope (`tests/`). **No toqué `scripts/` ni el contrato.**

## 2. Pre-RED

Búsqueda en `tests/` + contrato + insumos autorizados: ningún verificador cubre los cinco bloqueantes (el oráculo de 6 tests cubre agregado/raíces/partición/canario-config/hijos-genérico/rechazos/default; nada sobre worker vacío, paredes reales, descendientes comprobados, canario de checkout ni preparación medida). Protección faltante → **extensión justificada del archivo existente**, sin tocar los seis tests (diff `430+/0-` en ese archivo, verificado por `git diff --numstat`). Duraciones seriales medidas para elegir selecciones con diferencia observable: tranche1 ~0.7 s vs tranche2 ~2.1 s de pared.

## 3. Resultado RED

**Archivo:** `tests/test_017_001_suite_parallel.py` (+430/−0). 5 tests nuevos, uno por promesa observable, todos → **PC-10 (promesa E)**:

| Test | Bloqueante | Falla hoy con |
|---|---|---|
| `test_parallel_single_file_launches_no_empty_worker` | 1, worker sin archivos | AssertionError: "el lote lanzo 1 worker(s) sin archivos (pytest sin seleccion); rc=2" (worker-1 con `nodeids: []`, rc=2 por error de colección de la suite completa intentada; con guarda `start_new_session` + `killpg` y timeout 90 s ≤ 120 s) |
| `test_parallel_workers_record_real_walls_and_overlap` | 2, paredes/solapamiento | AssertionError: "instante ausente o no textual: None" (los workers no traen `started_at`/`finished_at`; solo hay `started_at` de nivel comando) |
| `test_parallel_checks_descendants_and_cleans_up_partial_launch` | 3, huérfanos + fallo parcial | AssertionError: exige `orphans_checked == true` (hoy solo `orphans: 0` fijo); más barrido `/proc` sin procesos con la raíz y caso (b) con archivo `worker-1` bloqueante |
| `test_parallel_declares_checkout_canary_covering_build_and_cdad` | 4, canario checkout | AssertionError: cero candidatos de canario con conteo+bytes+mtime/huella+`unchanged == true` que cubran `build/`/`.cdad/` |
| `test_parallel_reports_measured_preparation_cost_not_by_subtraction` | 5, preparación duplicada | AssertionError: `preparation_source` informa `None`, no `'per-worker-profiles'`; exige además `preparation_measured_s` por worker ligado a su `profile.json` y `duplicated_preparation_s == sum − referencia ±1e-3` vía `--balance-from` |

**Comandos exactos y salidas:**
- `python3 -m pytest tests/test_017_001_suite_parallel.py -q -p no:cacheprovider` → **5 failed, 6 passed en 29.55 s**. Los 6 existentes siguen verdes (sin modificar ni debilitar); los 5 nuevos fallan todos por `AssertionError` de promesa ausente. Cero `ImportError`/errores de colección (`py_compile` OK).
- Barrido `/proc` post-corrida de `cdad-suite.py parallel` vivos → `none`. Nunca quedaron procesos vivos.
- `git diff --numstat -- tests/test_017_001_suite_parallel.py` → `430 0` (puro agregado).

**Commit:** `b517ef90` — solo `tests/test_017_001_suite_parallel.py`. (`M docs/.cdad-state.json` del worktree es preexistente a este packet y quedó fuera del commit.)

## 4. Delta de inventario vivo (como texto)

```
+ tests/test_017_001_suite_parallel.py::test_parallel_single_file_launches_no_empty_worker (017-001 T6-M1, PC-10): un archivo + --workers 2 no lanza workers vacios; workers_launched==1 o skipped_empty_workers==1 y consolidado == serial. Estado: RED (1 worker sin archivos, rc=2).
+ tests/test_017_001_suite_parallel.py::test_parallel_workers_record_real_walls_and_overlap (017-001 T6-M2, PC-10): started_at/finished_at ISO 8601 con zona por worker, wall_s == fin-ini ±1e-3, total >= max-1e-3, total-max <= 1.0, overlap == sum-total ±1e-2. Estado: RED (sin instantes por worker).
+ tests/test_017_001_suite_parallel.py::test_parallel_checks_descendants_and_cleans_up_partial_launch (017-001 T6-M3, PC-10): orphans_checked == true + cero PIDs con la raiz (/proc) + fallo parcial (archivo worker-1) sale !=0, nombra causa y no deja vivos. Estado: RED (sin orphans_checked).
+ tests/test_017_001_suite_parallel.py::test_parallel_declares_checkout_canary_covering_build_and_cdad (017-001 T6-M4, PC-10): canario checkout (conteo+bytes+mtime/huella, unchanged == true) mas canario config existente. Estado: RED (sin canario checkout).
+ tests/test_017_001_suite_parallel.py::test_parallel_reports_measured_preparation_cost_not_by_subtraction (017-001 T6-M5, PC-10): preparation_measured_s por worker desde su profile.json, preparation_source == per-worker-profiles, duplicated == sum - referencia ±1e-3 con --balance-from. Estado: RED (sin preparation_source).
```

## 5. Declaraciones honestas

- **Nunca leí implementación**: no abrí ningún archivo bajo `scripts/`. Solo ejecuté la CLI como caja negra (invocaciones `parallel`/`close` vía subprocess en los tests más una reproducción manual con evidencia en `/tmp/cdad-tw-m1`, fuera del repo y ya eliminable) y leí sus artefactos de evidencia (`parallel.json`, logs de worker) para precisar el motivo del rojo.
- Timeouts de subprocess (90 s en M1 por exigencia del packet, 300 s heredado en el resto) son guardas de liveness, no oráculos de duración (convención 11).
- Suite completa no realizada: sin autorización para corrida completa; selección ejecutada: el archivo T6 (11 tests: 6 viejos verdes + 5 nuevos rojos) más 2 corridas seriales de temporización de tranche1/2 (~3 s).
