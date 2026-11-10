# Revisión T1-002

**Dictamen: T1 no pasa el gate de integración.** La corrección cubre los escenarios focales de H2 y H3, pero H1 sigue abierto para capturas parciales de tests omitidos.

**Commit revisado:** `7b0b0b327237c3650da8b953e5610723233c2cfd`. La revisión y las comprobaciones se ejecutaron sobre `cbe47008689bc89b8ece9ef90ccdff1c698dc28d`; no hay diferencias posteriores en los dos scripts revisados ni en el test focal.

## Hallazgo

### Una fase perdida de un test omitido puede quedar como perfil completo

**Required — Verdict: BLOCKING — Bucket: h**  
**Ubicación:** `scripts/cdad-suite.py:1038-1044`

Si el XML identifica un test como omitido, o alguna de sus fases tiene resultado `skipped`, el código salta todas las comprobaciones restantes para ese nodeid. Por tanto, una captura que conserva `setup: skipped` pero pierde el `teardown` emitido puede declararse `complete`, sin diagnóstico. La excepción legítima es no exigir `call` cuando no se ejecutó; no justifica ignorar las demás fases emitidas.

La consecuencia es la misma que motivó H1: el responsable puede consumir una medición parcial creyéndola íntegra. El test nuevo de H1 induce pérdida de fases en un test que pasa, pero no cubre esta rama.

**Corrección propuesta:** comprobar las fases esperables según el punto en que ocurrió el skip, conservando la excepción de `call` no ejecutado. La condición de cierre es demostrar que una pérdida real de `teardown` queda `incomplete` con diagnóstico y rc intacto, mientras un skip limpio sin `call` permanece `complete`.

## Evidencia

- `git diff --stat 7b0b0b32^ 7b0b0b32`: el fix modifica únicamente `scripts/cdad-suite.py` y `scripts/cdad_suite_observer.py`. `git diff 2a9b893a 7b0b0b32 -- tests` no produjo salida: no se editaron tests en el fix.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **57 passed in 57.68s**. Esto incluye las ocho protecciones focales y los 49 casos de regresión declarados.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` → **rc 0**, `status: "ok"`, 2002 nodeids, 239 módulos y 31 entradas de mapa. La salida conserva `timing.status: "pending"` y tres destinos placeholder.
- El estado del checkout muestra `docs/.cdad-state.json` modificado; no lo edité. No observé poda ni debilitamiento de tests en el diff del fix.

## Abstentions

- Intenté una sonda independiente de la rama de skip, pero la creación de su directorio temporal en `/tmp/opencode` fue denegada con `PermissionError`. No reintenté por otra vía. El hallazgo se fundamenta en el flujo citado; no afirmo haber reproducido esa variante en ejecución.
- No ejecuté la suite completa: esta es una revisión focal de T1. Tampoco acredita intervalos de operaciones calibrados ni una línea base, que corresponden a tareas posteriores.
- La spec y el plan conservan texto de “borrador no aprobado”; el paquete validado los identifica como contrato aprobado. No verifiqué independientemente la procedencia de esa aprobación.
