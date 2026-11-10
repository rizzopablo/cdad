FINAL TEXT — implementer review-fix (Route C, 017-001 T1 segunda vuelta, rama skip)

## Route C validation — PASS (before working)

- Dispatch identification block equals canonical `render --route C` output (byte-identical structure, verified via `scripts/cdad_packet.py render --route C`).
- `validate-request` → rc=0. `validate-packet` → rc=0.
- `packet_id` (017-001-suite-performance-implementer-review-fix-002), `execution_id` (exec-017-001-suite-performance-001), contract path+sha256 (`docs/specs/017-001-suite-performance/spec.md`, `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e`) match REQUEST.json; contract sha256 matches file on disk.
- Execution context `schema_version=2` → v2, Route C admissible. Zero `---cdad-packet-json` markers in dispatch → no route mixture.
- Proceeded on Route C, substage `review-fix`, inputs/scopes of the packet only. No full cycle/spec skill loaded.

## Objective executed

Review-fix acotado de T1, segunda vuelta: cierra el bloqueante de `review-T1-002.md` (rama test omitido) en `scripts/cdad-suite.py::build_profile`.

Hallazgo verificado contra su evidencia antes de cambiar código: `scripts/cdad-suite.py:1038-1044` (pre-fix) hacía `if skipped: continue` — si el XML identificaba un omitido o alguna fase traía outcome skipped, se saltaban todas las comprobaciones de ese nodeid, de modo que una captura con `setup: skipped` pero sin el `teardown` emitido quedaba `complete` sin diagnosis.

Fix aplicado (mínimo, sin debilitar las nueve protecciones, sin cambiar semántica de `close`, sin tocar tests/ ni contrato):
- Para nodeid omitido (`base in xml_skipped` o algún `outcome == "skipped"`), se exigen las fases esperables según donde ocurrió el skip: `setup` presente y `teardown` presente. Cada ausencia agrega `fase 'setup'/'teardown' ausente para {nodeid}: captura parcial de omitido` → `incomplete` con diagnosis.
- Única excepción legítima conservada: `call` no se exige al omitido (pytest no la ejecuta cuando no corrió).
- Resultado: skip limpio (setup skipped + teardown emitido) sigue `complete` con diagnosis vacía y rc intacto; pérdida real del teardown queda `incomplete` con diagnosis y rc contractual intacto.
- Se movió `whens = {...}` antes del branch de skip (el primer intento ingenuo lo referenciaba antes de definirlo y rompía R2/R3 con `profile.json` ausente; detectado por focal, corregido; lección registrada abajo).
- Docstring de `build_profile` actualizado para no prometer la regla vieja ("un omitido se conforma con su fase emitida").

## Modified files

- `scripts/cdad-suite.py` (+21/−6): docstring §§1006-1015 + branch skip en `build_profile` (~líneas 1042-1060). Ningún otro archivo de producto tocado.
- Commit: `869b2825` — `fix: require setup+teardown for skipped tests, keep call exempt (review-T1-002)` (1 file).
- `tests/` intacto: `git diff --stat -- tests/` vacío. Contrato intacto: `git diff --stat -- docs/specs/017-001-suite-performance/spec.md` vacío.
- `docs/.cdad-state.json` aparece `M` por rotación del orquestador (`active_packet` → este implementer-review-fix-002, status prepared); no lo edité ni lo commiteé (fuera de mi write_scope `scripts`).

## Exact commands + outputs

- Focal (9, incluye la nueva skip-rama): `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **9 passed in ~14s** (R1–R5 + H1–H3 + skip-rama (a)+(b) verdes).
- Regresión proporcional declarada: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **49 passed in 47.73s**.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` → **rc 0**, `status: "ok"` (salida conserva `timing.status: "pending"` y destinos placeholder, como en la revisión).
- Suite completa **no realizada** (ciclo focal + regresión proporcional como rutina; sin autorización para completa; no se ejecuta `cdad-ci-gate.py` como comprobación rutinaria de T1 por plan del paquete).
- Nota honesta del turno: el primer intento del fix referenció `whens` antes de definirlo → 3 failed / 6 passed (R2, R3 y skip-rama con `profile.json` ausente por excepción en `build_profile`). Baseline con stash confirmó 2/2 verdes sin el cambio; tras mover `whens` antes del branch, 9/9 verdes. Ningún test fue editado para obtener el verde.

## Límites

- No se acredita suite completa, ni intervalos de operaciones calibrados, ni línea base (tareas posteriores).
- La regla nueva exige `setup` + `teardown` a todo omitido con al menos una fase registrada; un omitido con cero fases ya era `incomplete` por la rama `nodeid sin fases` y lo sigue siendo. Skips en puntos distintos (setup/call/teardown) quedan cubiertos porque solo se exime `call`.
- Calidad (5 checks): early exit por branch con `continue` tras comprobar setup/teardown; estados ilegales no representables (ausente sigue ausente, nunca fila cero); predecible y atómico (misma captura → mismo status/diagnosis, sin mutar entradas); fail fast fail loud (pérdida real → `incomplete` con diagnosis accionable, rc intacto); nombres intencionales (`captura parcial de omitido`).
