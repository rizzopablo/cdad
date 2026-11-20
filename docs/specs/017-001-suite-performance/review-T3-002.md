# Review T3-002 — 017-001-suite-performance

**Resultado: T3 no pasa el gate de revisión.** El fix rechaza la asociación incorrecta probada en el control real, pero todavía acepta un intento cuya selección no puede verificarse. Por eso, el hallazgo bloqueante anterior **no cierra completamente**. El hallazgo opcional sobre la resolución del reloj exterior **sí cierra**.

## Hallazgo bloqueante

### Required — Una selección ausente se acepta como cobertura válida

**Verdict: BLOCKING · Bucket: h**

En `scripts/cdad-suite.py:2055-2056`, si `_t3_declared_selection_nodeids()` no puede obtener la selección declarada, el código ejecuta `continue` sin agregar un motivo de fallo. Por tanto, `selection-coverage` puede pasar sin haber vinculado la clave del mapa con la selección del intento.

Lo reproduje sin modificar la evidencia original: copié `attempt.json` y `profile.json` del intento real C-R a un directorio temporal, eliminé únicamente `selection` del `attempt.json` copiado y apunté C-R a esa copia. Resultado:

```text
cdad-suite: entry-check ... (satisfied=true)
rc=0
selection-coverage= {'name': 'selection-coverage', 'passed': True, 'reasons': []}
```

**Consecuencia:** se puede acreditar la entrada a la base aunque falte el dato necesario para demostrar qué selección corresponde al intento. Esto incumple el cierre solicitado para el hallazgo anterior y la identidad verificable de la calibración.

**Cierre verificable:** tratar una selección ausente o irresoluble como fallo nombrado de `selection-coverage`, sin inventarla; comprobar `rc=1`, `satisfied=false` y motivo con la clave afectada. Conservar el control positivo real y el negativo C-R→C-E.

## Cierre de los hallazgos anteriores

- **Vinculación de selección: no cierra completamente.** El mapa correcto de ocho selecciones pasó y el intercambio C-R→C-E fue rechazado por discrepancia de selección, pero persiste el caso bloqueante de selección ausente descrito arriba.
- **Resolución del residuo exterior: cierra.** El código usa `max(1.0, 1e-3)` y el test nuevo comprueba que −0,5 s no produce `residual-sign`, mientras que −1,5 s sí lo produce.

## Evidencia independiente

- **Route C:** `validate-request` y `validate-packet` finalizaron con rc 0; `render --route C` reprodujo la identificación recibida. Contexto de ejecución v2.
- **Tests:**  
  `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py`  
  → `11 passed in 3.83s`. Inspeccioné los dos tests nuevos: cubren el intercambio de selecciones y ambos lados de la resolución de 1 s; no cubren la selección ausente.
- **Validación:** `python3 scripts/cdad-suite.py validate` → rc 0, `status: ok`.
- **Mapa real correcto:**  
  `python3 scripts/cdad-suite.py entry-check --attempts ~/<workspace>/tmp/017-001-calibration-map.json --out ~/<workspace>/tmp/017-001-review-independent/good`  
  → rc 0, `satisfied=true`, seis checks aprobados.
- **Control negativo real:** generé una copia temporal del mapa cambiando solo C-R para que apuntara al intento C-E y ejecuté el mismo comando con esa copia. → rc 1, `satisfied=false`; `selection-coverage` nombró C-R y ambas selecciones discrepantes.
- **Ámbito del fix:** `git diff --name-status ee72f372^ ee72f372` muestra únicamente `scripts/cdad-suite.py`; el diff equivalente limitado a `tests/` no produce salida. El commit de los tests nuevos es `0e604efc`; el fix es `ee72f372`. Revisión examinada: `b062b4044dc8e732b1ae6e417f83e8a2fe78a8e7`.
- **Archivos modificados por esta revisión:** ninguno en el repositorio. Se crearon exclusivamente mapas, copias de evidencia y salidas temporales bajo `~/<workspace>/tmp/017-001-review-independent/`. `docs/.cdad-state.json` ya figuraba modificado.

## Abstentions

- No ejecuté la suite completa: esta fue una re-revisión focal, con los 11 tests T3 y los controles indicados; no acredito el estado de la suite completa.
- No completé el contraste integral de la tabla de decisiones con los ADR ni una re-revisión integral del diff de toda la feature. Mi dictamen se limita a T3 y a los hallazgos examinados aquí.
