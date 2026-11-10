Route C valid and RED complete. Role report:

## Intake — Route C validada

- Identificación recibida (un solo bloque, sin inline body → sin mezcla de rutas A/C) comparada contra el render canónico: `render --route C` reproduce byte a byte la identificación del dispatch.
- `validate-request` RC=0; `validate-packet` RC=0.
- Contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e` coincide con el archivo; contexto de ejecución v2 (`schema_version: 2`); `packet_id`/`execution_id`/contrato coinciden en REQUEST.json, PACKET.md y dispatch.
- Trabajado solo el packet declarado: substage `red`, plan task T7, write_scope `tests`.

## Hecho (test-writer, RED)

Agregadas **4 protecciones** a `tests/test_017_001_suite_parallel.py`, append-only (**+376/−0**; los 18 tests existentes intactos), una por promesa observable → **PC-10** (R4 con apoyo INV-1/INV-6). Sin leer implementación (`scripts/cdad-suite.py` no leído ni tocado); CLI como caja negra; timeouts solo como guardas de liveness. Pre-RED: ningún verificador cubría estos bloqueantes.

- **R1** `test_parallel_unverifiable_family_is_not_accepted` — con `CDAD_SUITE_FAULT=no-subreaper` y `no-sweep`: exige rc≠0, veredicto no aceptado y motivo nombrado.
- **R2** `test_parallel_late_checkout_write_after_pytest_discards_run` — control sin escritura sale accepted; hijo que duerme ~2 s, escribe archivo único en `build/` y termina en gracia exige descarte con veredicto reject/discard (limpieza en `finally`).
- **R3** `test_parallel_unreadable_sweep_area_discards_run_and_records_incomplete` — subdirectorio modo 000 bajo `.cdad/tmp`: exige no-accepted + campo explícito de incompletitud con la ruta (permisos restaurados y borrado en `finally`).
- **R4** `test_parallel_rejects_or_isolates_reused_evidence_root` — segunda invocación en el mismo evidence-root: exige rechazo con motivo por stderr o intento propio, y que nunca reporte los tests del intento anterior.

## Evidencia RED (fallo por la razón correcta, AssertionError)

Comando: `python3 -m pytest tests/test_017_001_suite_parallel.py -k "unverifiable_family or late_checkout_write or unreadable_sweep or rejects_or_isolates" -p no:cacheprovider` → **4 failed, 18 deselected in 45.77s** (repetido 2×, mismo resultado):

- R1: `con CDAD_SUITE_FAULT=no-subreaper la corrida NO debe declararse accepted… hoy sale accepted con rc=0`
- R2: `el lote con escritura tardía en build/ (…) debe descartarse… hoy la foto se toma antes y sale accepted con rc=0` (el control accepted pasó antes)
- R3: `con .sweep_probe_… ilegible (modo 000) el lote NO debe declararse accepted… hoy… se omite en silencio con rc=0`
- R4: `la segunda invocación… reutilizó los artefactos del intento anterior… alterados: ['worker-0/phases-raw.json', 'worker-0/profile.json', 'worker-0/pytest.xml', 'worker-0/stdout.log']`

Sin residuos en el checkout (`build/` sin `late_write_*`, `.cdad/tmp` sin sondas). Sintaxis verificada por colección + `ast.parse`.

## Commit

- `7685333b` — `017-001 RED-032: cuatro protecciones fail-closed del veredicto del lote (R1..R4, PC-10)` — 1 archivo, 376 inserciones. Solo `tests/`; la modificación preexistente de `docs/.cdad-state.json` no es mía y quedó fuera del commit.

## Delta de inventario vivo (texto propuesto, no materializado — fuera de mi write_scope)

- Nuevos verificadores: `tests/test_017_001_suite_parallel.py::test_parallel_unverifiable_family_is_not_accepted`, `::test_parallel_late_checkout_write_after_pytest_discards_run`, `::test_parallel_unreadable_sweep_area_discards_run_and_records_incomplete`, `::test_parallel_rejects_or_isolates_reused_evidence_root` — protegen PC-10 contra los 4 bloqueantes de `review-final-product.md`; estado RED (fallan por la razón esperada) en commit `7685333b`; 18 verificadores previos sin cambios.
- Declaraciones honestas: no leí código de implementación; diff limitado a `tests/`; lecturas limitadas a los inputs declarados (`spec.md`, `review-final-product.md`, `performance/parallelism.md`, el oráculo existente).
