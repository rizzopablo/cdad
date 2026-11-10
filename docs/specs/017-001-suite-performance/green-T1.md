# FINAL TEXT — implementer GREEN T1 (017-001-suite-performance)

## Route C validation — PASS (before working)
- Dispatch carries only the Route C identification block (no inline body → no route mixture).
- Execution context `.cdad/executions/exec-017-001-suite-performance-001/execution.json` has `schema_version=2` → v2, Route C admissible.
- `python3 scripts/cdad_packet.py render --request … --execution-context …` output is **byte-identical** to `.cdad/packets/017-001-suite-performance-implementer-green-001/PACKET.md` (`diff` empty).
- `packet_id`, `execution_id`, contract `path`+`sha256` match `REQUEST.json`; contract sha256 `472bab0c…192672e` matches `docs/specs/017-001-suite-performance/spec.md` on disk.
- Worked only on Route C, substage `green`, packet inputs/scopes. `tests/` never edited (read-only).

## Resultado GREEN
Los 5 tests RED de `tests/test_017_001_suite_profile.py` ahora pasan **por la razón correcta**: `close` conserva `pytest.xml` + `profile.json` por intento sin cambiar la semántica del cierre.

## Archivos modificados (commit `b3c9770e`, solo `scripts/`)
1. **`scripts/cdad_suite_observer.py` (creado)** — plugin pytest mínimo cargado solo por el hijo vía `-p cdad_suite_observer`. Registra cada fase realmente emitida (`nodeid/when/duration_s/outcome`) y la vuelca a `phases-raw.json` al final de la sesión. Solo observa: ante cualquier fallo de captura lo declara por stderr y deja el sumidero ausente; nunca altera selección, resultado ni ejecución. Fase no emitida = ausente, nunca fila de duración cero.
2. **`scripts/cdad-suite.py` (modificado, +~130/-7)** —
   - `run_pytest_to_logs` ejecuta la **única** corrida pytest del intento con `--junitxml=<intento>/pytest.xml`, `-p cdad_suite_observer` (con `PYTHONPATH` al `scripts/` propio) y sumidero de fases por env; devuelve `(rc, pared_monotónica, argv_efectivo)`. Conserva la neutralización de `PYTEST_ADDOPTS`/`addopts`/`COLUMNS` de §4.3.
   - `build_profile` arma `profile.json` (`schema_version`, `status complete/incomplete`, `diagnosis`, `pytest_argv`, `pytest_wall_s`, `phases`, `operations: []`, `operation_scope: {status pending-T2, reference}` — el alcance de operaciones es T2, se declara pendiente, no se finge). `complete` exige XML parseable con casos + fases no vacías + ≥1 fase por nodeid seleccionado; lo demás es `incomplete` con diagnosis y nunca sustituye el rc.
   - `cmd_close` conserva resultado, rc, selección, skips, interrupciones, canario y artefactos previos; `attempt.json` referencia `pytest.xml`/`profile.json` (aditivo — los checks `<=` de `test_008_002_suite_evidence.py` siguen valiendo). Interrupción (KeyboardInterrupt/aborto): intenta dejar perfil `incomplete` diagnosticado best-effort y preserva `state running/interrupted` + rc no-éxito. Sin dependencias externas nuevas.

## Evidencia (comandos exactos + salida)
- Focal: `python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **5 passed in 6.69s** (antes: 5 failed por promesa ausente; ningún cambio en tests).
- Regresión proporcional declarada: `python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **49 passed in 46.23s**.
- Humo: `python3 scripts/cdad-suite.py validate` → RC 0.
- Suite completa **no realizada** (ciclo focal + regresión proporcional como rutina; corresponde a cierre de feature/epic según la política declarada en el paquete).
- Commit: `b3c9770e feat: implement phase-profile-v1 artifacts in close (017-001 T1 GREEN)` (diff limitado a `scripts/`). `docs/.cdad-state.json` figuraba modificado antes de empezar; no lo toqué ni lo commiteé.

## Límites honestos
- T1 entrega resultados+fases (parte de PC-1) + conservación de PC-2. No acredita operaciones calibradas, base completa ni PC-3 (T2–T4 pendientes); `operations` queda `[]` con alcance `pending-T2` explícito.
- Veredicto de `complete` en corrida limpia verificado focalmente; la correspondencia XML↔selección la cubre el XML junit + checks del test, no un mapeo nodeid↔classname frágil.
- Ningún test considerado incorrecto; ninguno tocado.
