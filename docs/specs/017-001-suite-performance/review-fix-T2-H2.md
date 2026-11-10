FINAL TEXT — implementer review-fix hallazgo 2 (017-001-suite-performance, T2)

## Route C validation — PASS (before working)
- Dispatch identification block equals the canonical render byte-for-byte: `python3 scripts/cdad_packet.py render --request .cdad/packets/017-001-suite-performance-implementer-review-fix-004/REQUEST.json --route C` reproduces the prompt block exactly (`packet_id` 017-001-suite-performance-implementer-review-fix-004, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`).
- `validate-request` exit 0; `validate-packet --request … --packet …` exit 0.
- Contract sha256 matches spec on disk (`sha256sum` → `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e`).
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture. Full cycle skills not loaded.
- Proceeded on Route C, substage `review-fix`, packet inputs/scopes only.

## Finding verified against original evidence
- `review-T2.md` hallazgo 2: `committed_exercised_families()` solo consultaba `family["selection"]` (`scripts/cdad-suite.py:998-1033`); familia `u3-disposable-product` sin selección a nivel de familia pero operación `u3.contract-staging` con `selection: "C-U3"` (`performance/operation-scope.json`).
- Consecuencia confirmada: nodeid de `C-U3` sin captura quedaba `complete`. Corrección grounded, sin cambiar semántica de `close`.

## Fix applied (only `scripts/`)
- `scripts/cdad-suite.py` — `committed_exercised_families()`: la selección aplicable se resuelve a nivel de familia **y** a nivel de operación. Regla preservada: solo selecciones explícitas con lista de `nodeids` cuentan (`all-required-selections` sin nodeids nunca ejercita); solo entradas con estado `comprometida` en ambos niveles (operación sin `state` hereda comprometida; operación con estado no comprometido se omite); familia ejercitada a nivel de familia cortocircuita, si no se examinan sus operaciones. Deduplicado por familia. Docstring actualizado.
- No se tocó `tests/`, ni el contrato, ni la semántica de `close`.

## Evidence — exact commands + output
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py` → **5 passed in 7.91s** (P5 caso A `incomplete`+diagnosis; B/C `complete`; P1–P4 intactas).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **17 passed in 26.49s** (diecisiete protecciones T1 conservadas).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_evidence.py tests/test_008_005_ci_gate.py` → **24 passed in 17.27s** (regresión proporcional).
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` → **status: ok**, 2016 nodeids recolectados, timing `pending` (límite conocido del inventario, no de este cambio).

## Limits
- Suite completa no realizada (rutina focal + regresión proporcional; el cierre de feature/epic y su autorización pertenecen al orquestador). Selección ejecutada: T2-focal (5) + T1-focal (17) + regresión 008-002/008-005 (24) + `validate`. Límite: no se acredita verde de suite completa.
- `docs/.cdad-state.json` ya estaba modificado antes de empezar (transición del orquestador a este paquete, `prepared`); intacto y sin commitear.

## Role evidence
- Modified files: **one** — `scripts/cdad-suite.py` (+36/−15, solo `committed_exercised_families` + docstring).
- Product diff outside `scripts/`: **empty** salvo el `.cdad-state.json` preexistente no tocado por este rol (`git status --short` → solo `M docs/.cdad-state.json` tras el commit).
- Commit: `ca68d89f` (`feat: implement operation-level selection diagnosis (review-T2 H2)`, 1 file).
