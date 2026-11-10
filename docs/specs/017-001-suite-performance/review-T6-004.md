# Revisión T6-004 — resultado incompleto

**No puedo ratificar el cierre de los dos bloqueantes de `review-T6-003.md`, ni afirmar que T6 pase el gate o que `--workers 2` esté acreditado como seguro para la corrida final `--all`.** No es un hallazgo nuevo de fallo: faltan verificaciones independientes exigidas por el encargo.

## Evidencia obtenida

- **Route C:** `validate-request` y `validate-packet` finalizaron sin error. El render de identificación coincidió con el recibido.
- **Revisión examinada:** `e419c5ad530a3067852c1c3408e9f97958a79691`. Entre `3da3f4c6` y `HEAD`, el diff mostrado afecta únicamente a `performance/parallelism.md`.
- **Oráculo T6:** `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_017_001_suite_parallel.py` → **17 passed in 160.10s**. Una primera ejecución tuvo timeout antes de completar y no se usa como resultado.
- **Validación:** `python3 scripts/cdad-suite.py validate` → **`status: ok`**, 2054 nodeids recolectados.
- **Archivos modificados por esta revisión:** ninguno. `docs/.cdad-state.json` ya aparecía modificado al comenzar. No hice commit ni ejecuté la suite completa.

## Abstentions

- **Descendiente con sesión propia:** no ejecuté la sonda independiente de detección, limpieza y descarte. No doy por cerrado el primer bloqueante.
- **Huella del checkout:** la sonda pedida requiere modificar un archivo de `build/`, aunque después se restaure. Eso entra en conflicto con mi contrato de revisión de **solo lectura**, por lo que no la ejecuté. No doy por cerrado el segundo bloqueante.
- **Ventana de gracia:** no ejecuté la sonda independiente del hijo transitorio.
- **Cifras publicadas y resto de PC-10:** confirmé la existencia de los directorios de evidencia, pero no contrasté íntegramente sus datos, la equivalencia, el inventario de puertos ni todas las garantías.
- **Focales T1–T4, regresión proporcional y comportamiento de `close`:** no completé su verificación independiente; no atribuyo resultados ni cantidades.

**Para completar el reingreso:** se necesita una revisión que ejecute las sondas pendientes en un entorno autorizado para la modificación temporal del checkout, contraste la evidencia cruda y ejecute las selecciones focales y de regresión solicitadas.
