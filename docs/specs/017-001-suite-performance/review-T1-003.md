# Revisión T1-003

**Dictamen: T1 no pasa el gate de integración.** La corrección cierra el caso específico de pérdida de `teardown` probado en la novena protección focal, pero mantiene una vía por la que una fase `call` ejecutada y perdida se declara completa.

**Commit revisado:** `869b28256dfcd9efa699221f41c7aa8ec5e5bea3`. Las comprobaciones se ejecutaron sobre `48d233e2ef873ba519f89b7a59948f168421e4d9`, sin diferencias posteriores en `scripts/cdad-suite.py` ni `tests/`.

## Hallazgo

### La exención de `call` se aplica también cuando el test sí llegó a ejecutarse

**Required — Verdict: BLOCKING — Bucket: h**  
**Ubicación:** `scripts/cdad-suite.py:1045-1060`

La rama considera omitido al test si el XML contiene `<skipped>` o cualquier fase capturada tiene resultado `skipped`. En ese caso exige `setup` y `teardown`, pero **nunca exige `call`**, aun cuando `setup` haya pasado.

Un test puede ejecutar `pytest.skip()` dentro de `call`. Si el observador pierde precisamente esa fase, quedan `setup: passed`, `teardown: passed` y un XML que indica skip. El perfil se declara `complete`, con diagnóstico vacío, aunque falte una fase realmente ejecutada. El responsable puede así consumir una medición parcial creyéndola íntegra, en contra de la spec §§4.2–4.3 y el cierre solicitado en la revisión anterior.

**Evidencia independiente:** llamé a `build_profile` con esas fases y ese resultado XML simulados; devolvió:

```text
setup=passed, XML=skipped, call=lost, teardown=passed: complete diagnosis: None
```

La sonda ejercita la decisión del perfil con entradas simuladas; no afirma haber reproducido una pérdida real del observador.

**Corrección propuesta:** determinar si `call` era esperable a partir del resultado de `setup`, no del mero estado omitido del caso. Conservar la exención cuando `setup` terminó en skip o fallo; exigir `call` cuando `setup` pasó. Cerrar el hallazgo demostrando pérdida real de `call` en un skip ocurrido dentro de esa fase: `incomplete`, diagnóstico y rc contractual intacto, junto con el contrapeso del skip limpio en `setup`.

## Evidencia de revisión

- `git diff --stat 869b2825^ 869b2825` → solo `scripts/cdad-suite.py`, **21 inserciones y 6 eliminaciones**. `git diff --name-only 869b2825^ 869b2825 -- tests` → sin salida. El fix no editó tests.
- `python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **9 passed in 18.84s**. Incluye el contraste de `teardown` perdido y skip limpio sin `call`.
- `python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **49 passed in 49.26s**.
- `python3 scripts/cdad-suite.py validate` → **rc 0**, `status: "ok"`, 2003 nodeids, 239 módulos y 31 entradas de mapa. La salida mantiene `timing.status: "pending"` y tres destinos placeholder.
- La sonda del hallazgo cargó `scripts/cdad-suite.py` mediante `importlib.util`, sustituyó en memoria `read_sink_payload` y `read_xml_info`, y llamó a `build_profile`; no modificó archivos.
- `git status --short` mostró `M docs/.cdad-state.json`, cambio preexistente que no edité.

## Abstentions

- No ejecuté la suite completa: esta es una revisión focal de T1. Tampoco ejecuté `cdad-ci-gate.py`, conforme al gate declarado.
- No acredito la calibración de operaciones ni la línea base: corresponden a tareas posteriores.
- El paquete validado identifica la spec como aprobada, aunque su texto conserva `status: draft` y «No aprobado». No verifiqué independientemente la procedencia de la aprobación.
