# review-T1-004

**Dictamen: T1 pasa el gate focal de integración**, sujeto a la decisión del orquestador. No encontré bloqueantes para el cierre de la familia de pérdidas de fases revisada. Esta revisión no constituye una aprobación.

**Commit revisado:** `32904c2aec4f2d178bf910a9d31ec24b022980d0`. Las comprobaciones corrieron sobre `bc4dc12553c9bd6bb0e1a9e47fa11b3b83dede45`; no hay diferencias posteriores en el observador, el script ni los tests relevantes.

## Integridad de fases

La regla revisada cubre estructuralmente las fases esperables para los resultados ordinarios `passed`, `failed` y `skipped`:

- Exige `setup` y `teardown`; si falta alguno, diagnostica captura parcial.
- Exige `call` cuando `setup` pasó. La exime cuando `setup` falló o fue omitido, situaciones en que pytest no ejecuta `call`.
- Si no queda ninguna fase de un nodeid seleccionado, también declara el perfil incompleto.

La matriz focal comprueba mediante pérdida inducida los cuatro orígenes solicitados —skip en setup, call y teardown, y fallo de setup— y conserva los cuatro contrapesos limpios. Comprueba además diagnóstico y rc contractual. El caso que motivó `review-T1-003`, pérdida de `call` tras setup exitoso y skip en call, queda cerrado.

El diff de `32904c2a` modifica únicamente `scripts/cdad-suite.py`: 22 inserciones y 12 eliminaciones. La corrección afecta la evaluación del perfil; no modifica las rutas de cierre ni su rc.

## Hallazgo no bloqueante

### Tabla de decisiones desactualizada

**Optional — Verdict: OPTIONAL — Bucket: h**  
**Ubicación:** `docs/systemPatterns.md:5-46`; `docs/adr/ADR-040-especializacion-documental-por-contrato-casa-unica-y-dos-registros.md:3-8`.

La tabla se presenta como índice de decisiones vigentes, pero omite ADR-040, que figura como aceptado y afecta, entre otros, al reviewer. La omisión es preexistente y no altera el gate focal de T1; puede hacer que una delegación no reciba esa decisión por el mecanismo de distribución de la tabla.

**Cierre verificable:** que el mantenedor incorpore la fila correspondiente y confirme su referencia y roles. Las rutas de las filas existentes verificadas sí existen.

## Evidencia ejecutada

- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py`  
  → **17 passed in 25.90s**.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py`  
  → **49 passed in 48.82s**.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate`  
  → **rc 0**, `status: ok`; 2011 nodeids, 239 módulos y 31 entradas de mapa. Persiste `timing.status: pending` y hay tres destinos placeholder.
- `git diff 32904c2a HEAD --name-only -- scripts/cdad-suite.py scripts/cdad_suite_observer.py tests/test_017_001_suite_profile.py tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py`  
  → sin salida.
- `git status --short` → `M docs/.cdad-state.json`, cambio preexistente; **no modifiqué archivos**.

## Abstentions

- No ejecuté la suite completa ni `cdad-ci-gate.py`: esta es una revisión focal de T1 con regresión proporcional, no el cierre de la feature o del epic.
- No acredito la calibración de operaciones ni la línea base; corresponden a tareas posteriores.
- El paquete validado identifica la spec como aprobada, pero el documento aún dice `status: draft` y «No aprobado». No verifiqué independientemente la procedencia de la aprobación.
- La conclusión estructural se limita a la ejecución ordinaria y a los resultados de fase examinados; las pruebas inducen las pérdidas representativas de la matriz, no cada combinación posible mediante una ejecución independiente.
