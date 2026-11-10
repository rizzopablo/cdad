# FINAL TEXT — test-writer RED (Route C, 017-001 T1 segunda vuelta, rama skip)

## Route C validation — PASS (before working)

- Identification block in the dispatch equals canonical `render --route C` output (byte-identical, verified).
- `validate-request` → rc=0. `validate-packet` → rc=0.
- `packet_id`, `execution_id`, contract `path`+`sha256` match `REQUEST.json`; contract sha256 `472bab0c…192672e` matches `docs/specs/017-001-suite-performance/spec.md` on disk.
- Execution context `schema_version=2` → v2, Route C admissible. Zero `---cdad-packet-json` markers in dispatch → no route mixture.
- Proceeded on Route C, substage `red`, inputs/scopes of the packet only.

## Objective executed

RED de corrección de T1, segunda vuelta tras `review-T1-002.md` (BLOCKING, rama skip). Agregada a `tests/test_017_001_suite_profile.py` **una protección nueva, sin modificar las ocho existentes** (R1–R5 + H1–H3 intactas, diff solo aditivo), trazada a review-T1-002 + spec §§4.2–4.3 / PC-2 / INV-6, por medio externo, con `AssertionError` de promesa ausente (nunca `ImportError` ni error de colección). Oráculo solo desde contrato/review/tests autorizados; no se leyó `scripts/cdad-suite.py` ni el observador.

## Modified files

- `tests/test_017_001_suite_profile.py` (+105, solo agregados; ninguna de las 8 existentes tocada — cero líneas eliminadas).
- Commit: `b7d46c4c` — `017-001 T1 RED segunda vuelta: skip-rama protege teardown perdido de omitido (falla por promesa ausente)` (1 file, 105 insertions).
- `docs/.cdad-state.json` aparece `M` preexistente al inicio del turno; no tocado ni commiteado por este rol (write_scope `tests`).

## Test added (promesa observable, con consecuencia)

- `test_skipped_teardown_loss_is_incomplete_while_clean_skip_stays_complete` (review-T1-002 → PC-2/INV-6, §§4.2–4.3). Medio externo: sombra de `cdad_suite_observer.py` en el workspace del hijo que solo registra `setup` (conserva setup skipped, descarta el teardown emitido — mismo patrón probado de H1, reutilizado desde el test autorizado, no desde implementación). **(b)** Contrapeso primero: skip limpio sin call (setup skipped + teardown emitido) exige `status complete` + diagnosis vacía + rc intacto — pasa hoy. **(a)** Rama pendiente: con la pérdida inducida exige `status incomplete` + `diagnosis` no vacía + rc contractual intacto — falla hoy. *Sin este test, el usuario consume una medición parcial de un test omitido creyéndola íntegra; sin el contrapeso, una corrección futura podría marcar todo skip como incompleto y bloquear la base sobre skips limpios.*

## Exact commands + outputs (RED)

- `python3 scripts/cdad_packet.py validate-request --request .cdad/packets/017-001-suite-performance-test-writer-red-003/REQUEST.json --execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json` → rc=0
- `python3 scripts/cdad_packet.py validate-packet --request … --packet .cdad/packets/017-001-suite-performance-test-writer-red-003/PACKET.md --execution-context …` → rc=0
- `python3 scripts/cdad_packet.py render --request … --execution-context … --route C` → identificación canónica (coincide con el dispatch)
- Focal RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **`1 failed, 8 passed in 13.95s/20.60s`** (dos corridas: mismo veredicto). Las 8 existentes pasan sin modificación; la nueva falla por la aserción de la promesa:
  - skip-rama (a): `AssertionError: … se declaro 'complete'; debe ser incomplete` (`assert 'complete' == 'incomplete'`, línea 590)
  - El fallo ocurre en la aserción (a) **después** de pasar todas las aserciones (b) del contrapeso en la misma corrida — (b) verde en ruta, (a) rojo por promesa ausente. Reproduce en ejecución el hallazgo de review-T1-002.
- Ningún fallo es `ImportError`, error de colección ni sintaxis. Suite completa **no realizada** (ciclo focal; sin autorización para completa). Regresiones T1 (`test_008_002_suite_evidence`, `test_008_002_suite_selection`, `test_008_005_ci_gate`) no re-ejecutadas en RED (ningún archivo suyo tocado; corresponden al GREEN; no se ejecuta `cdad-ci-gate.py` como comprobación rutinaria de T1 por plan del paquete).

## Delta de inventario vivo (como texto, para materializar por el orquestador)

> En RED no hay altas materializadas; propuesta con disposición prevista **Añadir** (las 8 existentes quedan **Mantener** exactamente):
> - Añadir `tests/test_017_001_suite_profile.py::test_skipped_teardown_loss_is_incomplete_while_clean_skip_stays_complete` (review-T1-002 → PC-2/INV-6, §§4.2–4.3).
> - Mantener las 8 existentes sin cambio (R1–R5 + H1–H3). Incertidumbre: ninguna que obligue a conservar de más.

## Evidencia del rol / honestidad

- Implementación leída: **ninguna** (aislamiento preservado). Solo spec/review/red previo/tests. El medio externo (sombra del observador) se reutilizó del test H1 autorizado, no de archivos de producto.
- Diff limitado a `tests/` (1 archivo, +105/−0). Sin lecturas fuera de `docs/specs/017-001-suite-performance` + `tests/`. Sin edición fuera de `tests/`.
- Nota: durante el turno la inserción inicial reemplazó transitoriamente el comentario de cabecera de H3; se restauró de inmediato y el diff final confirma cero eliminaciones — las 8 funciones existentes están byte-intactas.
