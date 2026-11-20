# Revisión T6-005

## Dictamen

- **Bloqueante 1 — descendiente que abandona grupo y sesión: cerrado** para el caso reproducido. La sonda independiente detectó y limpió el proceso, y descartó el lote.
- **Bloqueante 2 — huella del checkout: cerrado** para el caso registrado. La evidencia cruda confirma el descarte y la implementación calcula la huella por contenido.
- **T6 pasa el gate de esta revisión**, con la salvedad de que el árbol de trabajo **no estaba completamente limpio**: `docs/.cdad-state.json` ya figuraba modificado al comenzar y seguía igual al terminar.
- **`--workers 2` queda acreditado para intentar la corrida final bajo las garantías y límites registrados**, no como demostración anticipada del resultado de `--all`. T7 debe comprobar sobre la suite completa, en una misma revisión, tanto la reducción de pared de al menos 15 % como la equivalencia exacta por nodeid.

No encontré nuevos hallazgos bloqueantes en las comprobaciones realizadas. Este informe no constituye aprobación.

## Comprobación de los bloqueantes

### 1. Descendiente con sesión propia

Creé fuera del repositorio un test que lanza `/bin/sleep 120` con `start_new_session=True` y lo ejecuté mediante:

```text
python3 scripts/cdad-suite.py parallel --workers 1 \
  --evidence-root ~/<workspace>/tmp/review-017-001-005/a/evidence \
  --nodeids ~/<workspace>/tmp/review-017-001-005/a/nodeids
```

Resultado: **rc 3**, `verdict=discarded`, `orphans_found=1`, `orphans_cleaned=1`, `orphans_remaining=0`. El PID creado por la sonda ya no existía en `/proc` tras la corrida.

Inspeccioné `scripts/cdad-suite.py`: activa `PR_SET_CHILD_SUBREAPER`, busca descendientes por cadena de PPID además de los grupos de procesos y cosecha hijos con `waitpid` en bucle. La detección no depende de que los argumentos del proceso contengan la ruta de evidencia.

### 2. Huella del checkout

No repetí la mutación de `build/`, conforme al encargo. Leí el `parallel.json` crudo de la sonda C en `~/<workspace>/tmp/017-001-probes/fingerprint/evidence/`:

- `verdict`: **rejected: canary detected changes**
- `checkout_canary.unchanged`: **false**
- Algoritmo: `sha256-per-file-sorted`
- Huella: `c4f52953…`
- `fingerprint_cost_s`: **3.067 s**

Coincide con la evidencia publicada. La implementación ordena las rutas y combina la ruta con el SHA-256 del contenido de cada archivo; por ello, el caso de reescritura de igual tamaño y mtime queda cubierto. El archivo centinela de la sonda estaba ausente al verificar.

## Ventana de gracia

Ejecuté una segunda sonda, equivalente a la anterior pero con `/bin/sleep 1.5`:

```text
python3 scripts/cdad-suite.py parallel --workers 1 \
  --evidence-root ~/<workspace>/tmp/review-017-001-005/b/evidence \
  --nodeids ~/<workspace>/tmp/review-017-001-005/b/nodeids
```

Resultado: **rc 0**, `verdict=accepted`, `orphans_found=1`, `orphans=0`, `orphans_cleaned=0`, `orphans_remaining=0`. El PID de la sonda ya no existía tras la corrida.

## Contraste de la muestra de rendimiento

Los JSON crudos de `final5` atribuyen ambas corridas a `3da3f4c6…`, con `dirty=0` en ambas:

| Medida | Resultado contrastado |
|---|---:|
| Serial, diferencia de timestamps | 873.0 s |
| Paralelo, `total_wall_s` | 546.359 s |
| Reducción calculada | 37.416 % |
| Paredes por worker | 546.358 s y 493.806 s |
| PGID | 2843323 y 2843324 |
| Trabajo medido | 1036.567 s |
| Solapamiento | 493.805 s |
| Procesos | 8 transitorios encontrados; 0 restantes |
| Preparación / duplicada | 0.1364 s / 0.00495 s |
| Huella del checkout | `b68410ce…`; coste 3.105 s |

Comparé los resultados de los XML JUnit serial y paralelos por identificador de caso: **57 frente a 57, exactamente iguales**, sin diferencias de resultado. Esto acredita la **muestra**, no la suite completa.

## Regresión y otras garantías

Ejecuté conjuntamente el oráculo T6, las focales T1–T4 y la regresión proporcional:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider \
  --basetemp=~/<workspace>/tmp/review-017-001-005/pytest -q \
  tests/test_017_001_suite_parallel.py \
  tests/test_017_001_suite_profile.py \
  tests/test_017_001_suite_operations.py \
  tests/test_017_001_suite_reconcile.py \
  tests/test_017_001_suite_external.py \
  tests/test_008_002_suite_evidence.py \
  tests/test_008_002_suite_selection.py \
  tests/test_008_005_ci_gate.py
```

**Resultado: 107 passed en 276.88 s; rc 0.** La ejecución conjunta no proporciona aquí un desglose independiente por archivo.

`PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` devolvió **rc 0**, `status: ok` y 2054 nodeids recolectados; su sección de timing sigue declarando `pending`.

El cuerpo de `cmd_close` es idéntico al de `88381176`, mediante comparación de la función extraída con AST. El barrido de usos de sockets confirma los tres archivos inventariados y los usos de puerto efímero; permanece el riesgo residual documentado de reutilización de un puerto liberado antes de su uso.

## Estado y trazabilidad

- Route C validada: `validate-request` y `validate-packet` sin error; identificación renderizada coincidente y contexto v2.
- `HEAD`: `a12090871528f1587ec27ef1450019a43e92a2bc`.
- Estado observado antes y después: `M docs/.cdad-state.json`. No puedo describir el checkout actual como completamente limpio.
- Archivos del producto modificados por esta revisión: **ninguno**. Las sondas y su evidencia se crearon fuera del repositorio.
- Commit realizado por esta revisión: **ninguno**.

## Abstentions

- No ejecuté `--all`; no afirmo que la suite completa ya cumpla la regla final ni extrapolo a ella el 37.4 % de la muestra.
- La garantía de familia observada depende de Linux, `prctl` y `/proc`. No la extrapolo a otras plataformas.
- No repetí la mutación del checkout: el cierre de ese punto combina inspección de implementación con la evidencia cruda de la sonda C.
