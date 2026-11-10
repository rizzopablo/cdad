# FINAL TEXT — test-writer RED (Route C, 017-001 T1 corrección H1–H3)

## Route C validation — PASS (before working)

- Identification block in the dispatch equals canonical `render --route C` output (byte-identical, verified).
- `validate-request` → rc=0. `validate-packet` → rc=0.
- `packet_id`, `execution_id`, contract `path`+`sha256` match `REQUEST.json`; contract sha256 `472bab0c…192672e` matches `docs/specs/017-001-suite-performance/spec.md` on disk.
- Execution context `schema_version=2` → v2, Route C admissible. Zero `---cdad-packet-json` markers in dispatch → no route mixture.
- Proceeded on Route C, substage `red`, inputs/scopes of the packet only.

## Objective executed

RED de corrección de T1 tras review independiente (`review-T1.md`, commit `b3c9770e`). Agregadas a `tests/test_017_001_suite_profile.py` tres protecciones nuevas, sin modificar las cinco existentes (R1–R5), cada una trazada a hallazgo + spec §§4.2–4.3 / PC-2 / INV-6, por medio externo, con `AssertionError` de promesa ausente (nunca `ImportError` ni error de colección). Oráculo solo desde contrato/plan/review; no se leyó `scripts/cdad-suite.py` ni el observador.

## Modified files

- `tests/test_017_001_suite_profile.py` (+181, solo agregados; ninguna de las 5 existentes tocada).
- Commit: `2a9b893a` — `017-001 T1 RED correccion: H1-H3 protegen review-T1 (falla por promesa ausente)` (1 file, 181 insertions).
- `docs/.cdad-state.json` aparece `M` preexistente al inicio del turno; no tocado ni commiteado por este rol (write_scope `tests`).

## Tests added (promesa observable, con consecuencia)

- `test_partial_phase_capture_is_incomplete_with_intact_rc` (H1, spec §§4.2–4.3, PC-2, INV-6). Medio externo: `cdad_suite_observer.py` shadowed en el entorno del hijo que solo registra `setup` (pierde `call`/`teardown`); XML del hijo sigue completo, rc 0. Exige `status incomplete` + `diagnosis` no vacía + rc intacto. *Sin este test, el usuario consume un perfil incompleto creyendo íntegras fases y resultados.*
- `test_profile_write_failure_preserves_pytest_rc` (H2, spec §4.3, PC-2, INV-6). Medio externo: directorio `profile.json` en el intento durante la corrida del hijo (`test_h2_slow`, sleep 2). Exige close rc 0 + intento `finished` rc 0 + sin `Traceback` + fallo de medición diagnosticado + sin perfil `complete` sustituto. *Sin este test, un fallo de medición cambia el resultado observable y oculta el rc real.*
- `test_handled_sigint_preserves_argv_and_wall` (H3, spec §§4.2–4.3, PC-2). Medio externo: `SIGINT` al process-group (no `SIGKILL`) durante `test_wait`. Exige `state interrupted`, rc no exitoso, `status incomplete`, `pytest_argv` efectivo con la selección y `pytest_wall_s` número ≥0. *Sin este test, el perfil interrumpido no permite reconstruir qué se midió ni cuánto tardó.*

## Exact commands + outputs (RED)

- `python3 scripts/cdad_packet.py validate-request --request .cdad/packets/017-001-suite-performance-test-writer-red-002/REQUEST.json --execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json` → rc=0
- `python3 scripts/cdad_packet.py validate-packet --request … --packet .cdad/packets/017-001-suite-performance-test-writer-red-002/PACKET.md --execution-context …` → rc=0
- `python3 scripts/cdad_packet.py render --request … --execution-context … --route C` → identificación canónica (coincide con el dispatch)
- Focal RED: `python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **`3 failed, 5 passed in 12.96s`**. Las 5 existentes (R1–R5) pasan sin modificación; las 3 nuevas fallan por la aserción de la promesa:
  - H1: `AssertionError: … se declaro 'complete'; debe ser incomplete` (`assert 'complete' == 'incomplete'`)
  - H2: `AssertionError: … sustituyo el rc del hijo (rc=1); debe conservar … 0` (`assert 1 == 0`)
  - H3: `AssertionError: … perdio el argv efectivo … ([]); debe conservarlo aunque hubo SIGINT` (`assert (True and [])`)
- Ningún fallo es `ImportError`, error de colección ni sintaxis. Suite completa **no realizada** (ciclo focal; sin autorización para completa). Regresiones T1 (`test_008_002_suite_evidence`, `test_008_002_suite_selection`, `test_008_005_ci_gate`) no re-ejecutadas en RED (sin archivos tocados; AUDIT las dejó en 5+25+19 passed; corresponden al GREEN).

## Delta de inventario vivo (como texto, para materializar por el orquestador)

> En RED no hay altas materializadas; propuesta con disposición prevista **Añadir** (las 5 R1–R5 quedan **Mantener** exactamente):
> - Añadir `tests/test_017_001_suite_profile.py::test_partial_phase_capture_is_incomplete_with_intact_rc` (H1 → PC-2/INV-6, §§4.2–4.3).
> - Añadir `tests/test_017_001_suite_profile.py::test_profile_write_failure_preserves_pytest_rc` (H2 → PC-2/INV-6, §4.3).
> - Añadir `tests/test_017_001_suite_profile.py::test_handled_sigint_preserves_argv_and_wall` (H3 → PC-2, §§4.2–4.3).
> - Mantener las 5 existentes sin cambio. Incertidumbre: ninguna que obligue a conservar de más.

## Evidencia del rol / honestidad

- Implementación leída: **ninguna** (aislamiento preservado). Solo ejecución black-box del CLI sobre repos sintéticos en `/tmp` para diseñar la inducción externa (variables `CDAD_SUITE_PHASE_SINK`/`PYTHONPATH` observadas desde salidas, no desde archivos). El stderr de una sonda H2 mostró un `Traceback` con rutas/líneas — salida observada del runner, no lectura de archivos; no se usó para el oráculo.
- Diff limitado a `tests/` (1 archivo). Sin lecturas fuera de `docs/specs/017-001-suite-performance` + `tests/`. Sin edición fuera de `tests/`.
