Route C validado y RED completado. Reporte del rol:

## 1. Intake (Route C — explicit file backup)

- Identificación única en el prompt (`packet_id` 017-001-suite-performance-test-writer-red-022, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py render --request …/REQUEST.json` vs `PACKET.md`: **RENDER_MATCH** (byte a byte).
- Contexto de ejecución `.cdad/executions/exec-017-001-suite-performance-001/execution.json`: `schema_version: 2` → **v2 confirmado**, no hubo switch silencioso.
- Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C. Cuerpo inline ausente: admisible en route C.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.

## 2. Pre-RED

Búsqueda en `tests/` + contrato + insumos autorizados: ningún verificador cubre el lote paralelo (las 37 menciones a "parallel" son de otros contextos). Protección faltante → archivo nuevo justificado, sin tocar existentes. Forma serial de referencia aprendida del insumo autorizado `test_008_002_suite_evidence.py` (`attempt.json → pytest_summary.passed/failed/skipped`, canarios `canary-before/after.txt`).

## 3. Resultado RED

**Archivo:** `tests/test_017_001_suite_parallel.py` (nuevo, 455 líneas, solo stdlib). 6 tests, uno por promesa observable, todos → **PC-10 (promesa E)**; el del default cita además la decisión PC-9:

| Test | Promesa |
|---|---|
| `…_aggregate_reports_wall_work_overlap_and_matches_serial` | agregado: N workers, pared/worker + total, trabajo rotulado como tal, solapamiento declarado, consolidado = serial (`close` mismos nodeids) |
| `…_distinct_recorded_home_xdg_tmp_roots` | HOME/XDG/TMP distintas y registradas |
| `…_partition_is_by_file_without_repetition` | partición por archivo, sin repetición |
| `…_keeps_canary_clean_and_terminates_children` | canario sin cambios + hijos terminados (registro o conductual vía `ps`) |
| `…_rejects_invalid_worker_counts` | `--workers` 0/−1/nproc → salida 2 + motivo `worker*` por stderr |
| `…_default_is_two_workers_without_using_all_cores` | default 2, < nproc |

**Comando exacto:** `python3 -m pytest tests/test_017_001_suite_parallel.py -v` → **6 failed en 1.59 s**, las 6 con `AssertionError` de promesa ausente (`invalid choice: 'parallel'`, rc=2 del parser). Cero `ImportError`/errores de colección. Caso notable: el test de rechazos también falla (rc=2 se cumple pero stderr no trae motivo de workers) → rojo por la razón correcta, no verde falso.

**Commit:** `8021094f63b4dfa3adb2daaa229e78b7e6d768e5` — `git show --stat HEAD`: solo `tests/test_017_001_suite_parallel.py`. (Los cambios preexistentes en el worktree —`M docs/.cdad-state.json`, `?? …/parallelism.md`— no son míos y no entraron al commit.)

## 4. Delta de inventario vivo (como texto)

```
+ tests/test_017_001_suite_parallel.py (017-001 T6, PC-10): oráculo del lote
  `parallel --workers N --evidence-root <dir> [--nodeids <f>]`. Cubre agregado
  pared/trabajo/solapamiento + equivalencia serial, raíces por worker,
  partición por archivo, canario + hijos, rechazos de workers inválidos y
  default 2. Estado: RED (6/6 AssertionError, subcomando inexistente).
```

## 5. Declaraciones honestas

- **Nunca leí implementación**: no abrí ningún archivo bajo `scripts/`. Solo ejecuté la CLI como caja negra (`--help`, invocaciones `parallel` vía subprocess en los tests) para observar el comportamiento prometido.
- Timeouts de subprocess (300 s) son guardas de liveness, no oráculos de duración (convención 11).
- Directorio temporal de validación del render (`./tmp-red022`) eliminado; evidencia de corridas RED en `tmp_path` (fuera del repo).
