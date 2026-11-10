# review-T4-002.md

## Veredicto

**Los dos bloqueantes de `review-T4.md` cierran en esta revisión focal. T4 pasa el gate de revisión focal**, con las abstenciones indicadas abajo. Este dictamen no constituye aprobación del usuario ni acredita el cierre de la feature o del epic.

1. **Resto desconocido:** `baseline.md` y `baseline.json` ya no lo clasifican por descarte como trabajo contractual ni deducen de él un techo de optimización. El informe exige una medición focal adicional cuando la decisión dependa de ese costo.
2. **Identidad contable:** la reconciliación reproducida publica los totales desde valores sin redondear y coincide con la base. Con aritmética decimal, preparación más resto coincide exactamente con `sum_S_test`; `sum_S_test + R_pytest` difiere de `T_pytest` en **0.001 s**, justo en el límite declarado.

## Hallazgos bloqueantes

Ninguno dentro del alcance de esta revisión focal.

## Evidencia

- **Route C:** `validate-request` y `validate-packet` finalizaron con código 0; `render --route C` reprodujo la identificación recibida. El contexto de ejecución es v2.
- **Reproducción de la reconciliación:**

  ```text
  python3 scripts/cdad-suite.py reconcile \
    --attempt .cdad/tmp/017-001-baseline-attempt \
    --out .cdad/tmp/017-001-review-013-reconcile
  ```

  Resultado: `status=complete, diagnostics=none`. El bloque `run` reproducido coincide con el de `baseline.json`: preparación **186.506 s**, resto **4800.094 s**, `sum_S_test` **4986.600 s**, `R_pytest` **7.671 s** y `T_pytest` **4994.270 s**. Se declara la cota de **1.017 s** para la suma de los valores por test publicados y el cálculo de totales desde valores sin redondear. La segunda identidad está en el borde exacto de la tolerancia; una comparación binaria directa necesita considerar la representación de punto flotante.

- **Cobertura:** la reconciliación reproducida informa `all-selection`, `missing: []`, `without_entry: []` y `blocked: false`. Declara `product.copy` y `product.generate` no ejercitadas; el registro conserva `wait.*` como desconocidas.
- **Protección y regresión focal:**

  ```text
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= \
    -p no:cacheprovider tests/test_017_001_suite_reconcile.py \
    tests/test_017_001_suite_profile.py tests/test_017_001_suite_operations.py \
    tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py
  ```

  Resultado: **42 passed in 40.78s**, incluido el test nuevo de totales. `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` devolvió `status: ok`.

- **Revisión examinada:** `6a375afc`; el cambio de código de totales está en `990d794a`. No modifiqué archivos del producto; generé únicamente la salida temporal de reconciliación declarada arriba. Al iniciar, `docs/.cdad-state.json` ya figuraba modificado.

## Abstenciones

- **Revisión integral del diff y tabla de decisiones vigentes frente a `docs/adr/`:** no completadas; el veredicto es focal sobre los bloqueantes y comprobaciones solicitadas, no una conformidad general.
- **`make validate`:** no lo reejecuté. El informe GREEN registra un fallo F011 y lo atribuye a deriva de instalación preexistente; no verifiqué independientemente esa atribución.
- **Suite completa en la revisión actual:** no ejecutada. La base documenta una corrida anterior sobre `7426438b`, con cinco omisiones; no equivale a una suite completa de la revisión actual ni a evidencia de cierre de epic.
- No contrasté independientemente cada cifra secundaria del informe ni la totalidad de intervalos crudos y sus propietarios; la reproducción acredita los totales y la cobertura informados por el reconciliador.
