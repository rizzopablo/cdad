Done. Final report:

## 1) Archivos escritos / corregidos (con hash)

| Archivo | Acción | sha256 |
|---|---|---|
| `tests/test_005_003_t3_set_summary.py` | **nuevo** (focal T3, 9 tests) | `7b2f667717a133ead14c8bd7b7ec8137b3db89196332704bb34287e0e7b720ed` |
| `tests/test_005_002_t4_acceptance.py` | **corregido** (D11‑3) | `1e6ab59d644f5005fa36702c6c6b3c8a86d87208d2a162534e441bd82a1201bd` |

Nada fuera de `tests/**`. `docs/.cdad-state.json` ya estaba modificado **antes** de este encargo (fuera de mi write scope) y **no** se commiteó.

## 2) Mapeo test → postcondición/borde

**`tests/test_005_003_t3_set_summary.py`** (focal nuevo)

| Test | Postcondición / borde |
|---|---|
| `test_pd6_set_summary_minimal_keys_and_no_detail_by_default` | **PD‑6/C2**: corrida multi‑sesión con `--set-summary` → documento aditivo `set-summary-v1` con el conjunto mínimo de claves (`run{sessions_ref,runtime_version,schema}`, `sessions_included` hasheadas, `coverage{sessions_reporting,sessions_total,cause}`, `milestones{first_resume,first_dispatch}`, `magnitudes{value,unit,bucket,sessions_reporting,sessions_total,cause}`, `detail_ref`, `detail_flag`, `unknowns[]`); sin ids crudos ni ruta absoluta; **detalle por sesión NO emitido** (ningún nodo `measures`) |
| `test_pd6_set_summary_detail_flag_restores_per_session_detail` | **PD‑6**: la bandera `detail_flag` (=`--detail`) restaura el detalle por sesión |
| `test_pd6_partial_magnitude_is_unknown_not_partial_total` | **PD‑6 borde**: magnitud sin cobertura total → `unknown` + `value:null` + causa; nunca subtotal parcial como total, nunca `0` (INV‑9) |
| `test_pd6_set_summary_is_additive_existing_records_unchanged` | **PD‑6/INV‑5**: aditivo — sin la bandera, corridas de 1 y 2 sesiones siguen emitiendo `context-meter-v1` con `sessions[]` |
| `test_r4_reference_declares_total_bound_by_n_times_session_limit` | **PD‑6/R4/V3 elemento (a)**: `context-meter.md` declara *total ≤ N × límite por sesión* |
| `test_r4_reference_declares_limit_is_per_session_document` | **PD‑6/R4/V3 elemento (b)**: el límite normativo es **por documento de sesión** (ya publicado; pasa hoy) |
| `test_d11_1_controlled_temp_base_byte_identical_after_read` | **D11‑(1)**: ausencia de escrituras sobre **base temporal controlada** — byte‑idéntica tras la lectura |
| `test_d11_2_read_completes_and_results_expected_with_concurrent_writer` | **D11‑(2)**: **otro escritor activo** durante la lectura; la lectura se completa y sus resultados son los esperados (con contador que prueba que el escritor escribió ≥1 vez) |
| `test_d11_4_real_base_never_written_rule_declared_and_absent_in_tests` | **D11‑(4)**: regla declarada en `context-meter.md` (nunca escribir la base real, ni para demostrarlo) + **ausencia verificable** en `tests/**` |

**D11‑3** (corrección en `tests/test_005_002_t4_acceptance.py`): se eliminó la aserción de `(tamaño, mtime)` de la base **viva** en `test_c4` (subtest `store-intacto`) y en `test_c5`; ahora la integración real afirma **solo la lectura y los resultados** (`rc`/documento, ya cubiertos por `run_real_single` + cifras pinneadas). El snapshot de `(tamaño,mtime)` sobre **fixtures** en `test_c3` se conserva (base controlada). Docstrings actualizados.

**Interfaz declarada por el test** (el spec deja la redacción/forma al implementer): bandera `--set-summary` (documento aditivo separado) y `--detail` (restaura el detalle). Forzado por INV‑5: emisión automática en multi‑sesión rompería `test_005_002_t1` (store de 2 sesiones que hoy debe seguir dando el registro neutral), que el encargo exige verde.

## 3) Comandos y salidas

```
$ python3 -m pytest tests/test_005_003_t3_set_summary.py -q
5 failed, 4 passed in 1.29s
  FAILED test_pd6_set_summary_minimal_keys_and_no_detail_by_default
  FAILED test_pd6_set_summary_detail_flag_restores_per_session_detail
  FAILED test_pd6_partial_magnitude_is_unknown_not_partial_total
  FAILED test_r4_reference_declares_total_bound_by_n_times_session_limit
  FAILED test_d11_4_real_base_never_written_rule_declared_and_absent_in_tests
```
Las 5 fallas son **`AssertionError` de contrato** (verificado con `--tb=line`): tres por `rc=2` («el resumen NO existe todavía», bandera `--set-summary` ausente), una por la regla R4‑(a) ausente y una por la regla D11‑(4) ausente. Sin `ImportError`/sintaxis/errores de E/S. Los 4 verdes: `r4-(b)` (ya publicado), `additive`/INV‑5, `d11_1`, `d11_2`.

```
$ python3 -m pytest tests/test_005_002_t4_acceptance.py -q
3 passed, 2 skipped in 1.74s      # los 2 skipped son las integraciones reales (sin env)
$ python3 -m pytest tests/test_005_002_t1_neutral_record.py -q
7 passed in 2.62s                 # regresión 005-002 verde
$ python3 -m pytest ...::test_d11_2_... -q   # x5 → 5/5 passed (no flaky)
```

## 4) Hash del commit

```
8b5673db120a4be63c0ec288f5b5ce16113a6602
test(005-003): RED T3 - resumen del conjunto, regla del documento multiplexado y cierre de D11
tests/test_005_002_t4_acceptance.py |  49 +-
tests/test_005_003_t3_set_summary.py | 810 ++++++
```

## 5) Bordes sin cubrir y por qué

- **`tests/test_005_003_t3_meter_no_write.py`**: el `plan-tasks` lo lista como focal separado para D11(1)/(2), pero el **encargo del paquete** indicó explícitamente poner los puntos 1, 2 y D11(1)/(2)/(4) en el **único** focal `test_005_003_t3_set_summary.py`. Seguí el paquete (contrato de ejecución) — divergencia declarada respecto del plan.
- **Multi‑sesión explícita** (`--session A --session B`) y corridas parciales (`--limit`) con `--set-summary`: no cubiertas; la postcondición asignada fija el resumen para la corrida multi‑sesión (store con ≥2 sesiones), no cada forma de invocación.
- **Nombres de las `magnitudes`**: el contrato no los enumera; el oráculo afirma la **forma** de cada entrada + la **regla de cobertura parcial**, no claves concretas.
- **D11‑(4)(b)** es un chequeo estático sobre `tests/**` (ausencia de intentos de escritura a la base real en las fuentes), no un sandbox en runtime.
- **`--set-summary` en corrida de una sola sesión**: no testeado (el contrato dice «emitido para corridas multi‑sesión»).
- Límite honesto: observé la **superficie** del CLI con `--help` (no leí código de implementación); **no** leí `context-meter.md` ni `scripts/cdad_context_meter.py`.