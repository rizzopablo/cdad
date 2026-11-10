# Review T3 — 017-001-suite-performance

**Resultado: T3 no pasa el gate de revisión.** Hay un defecto bloqueante en la vinculación entre cada selección y su intento. Además, no pude completar la reejecución solicitada de la CLI sobre la evidencia real por una denegación de permisos al crear el directorio temporal de salida.

## Hallazgo bloqueante

### Required — La entrada puede darse por satisfecha con una selección equivocada

**Verdict: BLOCKING · Bucket: h**

En `scripts/cdad-suite.py:1996-2012`, `selection-coverage` comprueba las **claves del mapa**, pero no que la selección registrada en cada `attempt.json` corresponda a la clave y a los nodeids del registro. Los conteos se contrastan usando la clave del mapa (`2033-2035`), independientemente de la selección declarada por el intento.

Lo comprobé cargando los ocho intentos reales y evaluando el método de entrada: primero devolvió `satisfied: true`; después cambié **solo en memoria** la selección declarada del intento C-R por `tests/incorrect.py::test_wrong`. El resultado siguió siendo `satisfied: true`, con los seis checks en `pass`.

**Consecuencia:** una asociación equivocada al construir el mapa puede acreditar una calibración para una selección que el intento no declara, y permitir iniciar la base sin demostrar la correspondencia exigida por la spec (§4.4 y PC-1).

**Cierre verificable:** vincular cada clave con la selección efectiva y ordenada del intento y con el registro, rechazando discrepancias. Comprobar tanto que las ocho selecciones reales siguen pasando como que una asociación errónea o una selección alterada bloquea la entrada.

## Hallazgo opcional

### Optional — Se diagnostica como discrepancia una diferencia menor que la resolución declarada

**Verdict: OPTIONAL · Bucket: h**

En `scripts/cdad-suite.py:1839-1843`, `R_exterior` se compara contra `0.001 s`, aunque el informe declara para el reloj exterior una resolución de `1 s`. El contrato operativo, líneas 58–61, pide usar la tolerancia o la resolución declarada si es mayor. Una prueba en memoria con `R_exterior = -0.5 s` produjo `residual-sign`.

Esto puede señalar como anomalía una diferencia que el propio reloj no permite resolver. No bloquea el check de entrada por sí solo.

**Remedio:** usar la resolución aplicable a cada comparación y comprobar diferencias a ambos lados de ese límite.

## Evidencia verificada

- **Packet:** Route C validada; `validate-request` y `validate-packet` terminaron con rc 0 y la identificación coincide con `render --route C`. Contexto v2.
- **Tests:**  
  `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py tests/test_017_001_suite_profile.py tests/test_017_001_suite_operations.py tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py`  
  → **84 passed in 90.85s**.
- **Validación:** `python3 scripts/cdad-suite.py validate` → **rc 0**, `status: ok`.
- **GREEN y tests:** `git diff --name-status 1834e0d5..2ccebd86 -- tests/` no produjo salida. El commit GREEN `2ccebd86` modificó únicamente `scripts/cdad-suite.py`.
- **Agregación:** inspeccioné la unión de intervalos y ejecuté los nueve tests sintéticos T3, incluidos anidamiento, solapamiento, compartido, incompleto y determinismo.
- **Cobertura:** sobre el perfil real C-R, al retirar en memoria `recovery.construct` se informó esperado 1 / observado 0; al duplicarlo se informó esperado 1 / observado 2.
- **Entrada real:** la evaluación directa en memoria de los ocho perfiles y el registro devolvió `satisfied: true`, seis checks aprobados y ningún diagnóstico. Esto **no sustituye** la reejecución solicitada del comando CLI.
- **Estado:** revisión examinada `8dc9fc183d70b6d35dc6f497be849c5276f19d42`. No modifiqué archivos; `docs/.cdad-state.json` ya figuraba modificado.

## Abstentions

- **Reejecución de `entry-check` y determinismo sobre archivos reales:** `mktemp -d /tmp/opencode/t3-review-XXXXXX` devolvió `Permission denied`. No intenté una ruta alternativa tras la denegación. Por tanto, no puedo acreditar en esta revisión ni el resultado de la CLI desde cero ni la comparación byte a byte y la comprobación de no modificación de los intentos reales.
- **Suite completa:** no ejecutada; se ejecutaron las focales y la regresión proporcional indicadas arriba.
- **Tabla de decisiones y ADR:** no completé el contraste integral; no emito dictamen sobre esa obligación.
