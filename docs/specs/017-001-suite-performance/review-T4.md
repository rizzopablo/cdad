# review-T4.md

## Veredicto

**T4 no pasa el gate.** El informe clasifica como trabajo contractual el resto no medido y extrae conclusiones de optimización de esa clasificación, en contradicción con la especificación. Además, las cifras publicadas de preparación y resto no concilian con `S_test` a la tolerancia declarada.

La revisión de la evidencia cruda queda **sin acreditar**: el intento solicitado está fuera del repositorio y el paquete solo declara `repository-read`. No accedí a esa ruta ni reejecuté `reconcile` sobre ella.

## Hallazgos bloqueantes

### 1. El resto desconocido se presenta como trabajo contractual y como límite de optimización

**Required — Verdict: BLOCKING — Bucket: h**

**Ubicación:** `performance/baseline.md:43-46, 86-98`; contrato `spec.md:326-330, 357-360`.

El informe llama al 96 % de resto “trabajo propio de los tests”, afirma que cada test de ese conjunto verifica una promesa y concluye que la optimización serial tiene un techo cercano al 3 % y que cualquier objetivo superior exige paralelismo. Sin embargo, ese resto está **sin desglosar**. La especificación prohíbe clasificar lo desconocido como ejecución contractual por descarte y exige una medición focal adicional si la decisión depende de ese costo.

**Consecuencia:** el responsable puede descartar preparación todavía no observada y decidir paralelismo sobre una atribución que la medición no demuestra.

**Cierre verificable:** presentar el resto como desconocido, retirar o condicionar las conclusiones que dependen de su composición y, si se quiere sostenerlas, aportar la medición adicional requerida por el contrato.

### 2. La atribución publicada no reconcilia con `S_test`

**Required — Verdict: BLOCKING — Bucket: h**

**Ubicación:** `performance/baseline.json:24-35, 62-65`; contrato `spec.md:291-306`.

El JSON declara `S_test = 4986.6 s`, preparación `186.221 s` y resto `4800.401 s`. La suma de estas dos últimas cifras es **4986.622 s**, una diferencia de **0.022 s**, superior a la tolerancia publicada de **0.001 s**. No se explica en el documento una diferencia de alcance o precisión que concilie esos valores.

**Consecuencia:** quien consuma la base no puede reproducir la identidad de atribución con los valores publicados ni distinguir redondeo de una discrepancia contable.

**Cierre verificable:** publicar cifras con precisión y alcance coherentes, reproducidas desde la evidencia cruda, de modo que la identidad se cumpla dentro de la tolerancia declarada o que cualquier diferencia tenga un residual y diagnóstico explícitos.

## Verificaciones realizadas

- Validación Route C: `validate-request` y `validate-packet` terminaron con código 0; `render --route C` produjo la identificación recibida.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py tests/test_017_001_suite_profile.py tests/test_017_001_suite_operations.py` → **39 passed in 36.42s**.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` → **`status: ok`**.
- Cálculo independiente del JSON: `186.221 + 4800.401 − 4986.6 = 0.022 s`.
- Revisión actual: `bb6f57df519ad9a965299ad716621c420b40f5c9`. `af28f9f1` modifica `scripts/cdad-suite.py`.
- No modifiqué archivos. El estado observado ya incluía `M docs/.cdad-state.json`.

## Abstenciones

- **Integridad y reproducibilidad del intento:** no verifiqué commit, canary, resultados, errores de captura, conservación del perfil, cobertura real ni atribución desde los datos crudos. La ruta indicada está fuera del alcance `repository-read`; corresponde al orquestador autorizarla o redirigir la revisión.
- **Atribución sin doble conteo y propiedad de intervalos compartidos en la corrida real:** los tests focales pasan, pero eso no sustituye el contraste con el perfil real.
- **Completitud del contraste all-selection y fidelidad de todas las cifras publicadas:** no acreditadas sin el intento y la reconciliación independientes.
- **Decisiones vigentes y revisión integral del diff:** no quedaron verificadas en esta revisión focal; no se infiere conformidad general.
- **Suite completa:** no se ejecutó en esta revisión.
