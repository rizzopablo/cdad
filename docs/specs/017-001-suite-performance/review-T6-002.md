# Revisión T6-002

**Veredicto: T6 no pasa el gate.** No quedan cerrados los seis puntos: el conteo de huérfanos no comprueba lo que declara y el runner puede devolver éxito aunque el canario detecte cambios. Por tanto, **no queda acreditado como seguro usar `--workers 2` para la corrida final `--all`**. No apruebo ni modifico el producto.

## Hallazgos bloqueantes

### 1. El conteo de huérfanos excluye descendientes reales

**Required · Verdict: BLOCKING · Bucket: h**

En `scripts/cdad-suite.py:1597–1625`, `live_pids_with_marker()` cuenta únicamente descendientes cuya línea de comandos contiene la ruta de evidencia. Un proceso hijo o nieto puede no contener esa ruta. Además, cuando su padre termina, puede ser reasignado a otro padre y dejar de aparecer como descendiente del runner.

**Reproducción independiente:** lancé un hijo `sleep 30`, comprobé que `_is_descendant_of(pid, os.getpid())` devolvía `True` y llamé al contador con una ruta que no figuraba en sus argumentos. El resultado fue `reported=[]`, pese al hijo vivo. Luego terminé y esperé el proceso.

**Consecuencia:** `orphans_checked: true, orphans: 0` no demuestra ausencia de procesos dejados por el lote. La limpieza ante lanzamiento parcial (`:1628–1648`) también termina y espera los workers directos, pero no acredita por sí sola la terminación de sus descendientes.

**Cierre verificable:** identificar y gestionar la familia de procesos del lote sin depender de que sus argumentos contengan la ruta de evidencia; demostrar detección y limpieza con un descendiente vivo sin ese marcador, incluidos los casos de terminación normal y fallo parcial.

### 2. Un canario alterado no hace fallar el lote

**Required · Verdict: BLOCKING · Bucket: h**

`checkout_unchanged` se calcula en `scripts/cdad-suite.py:2012–2014`, pero el retorno en `:2116–2119` es `first_rc` aunque haya cambios en el checkout. Incluso para el canario de configuración, un delta solo produce un aviso. Esto contradice el contrato de `performance/parallelism.md`, que exige descartar el lote si se altera el checkout y que el canario falle si cambian `build/` o `.cdad/`.

**Consecuencia:** una corrida con tests verdes y escrituras compartidas puede devolver `rc=0` y presentarse como utilizable pese a haber perdido la garantía de aislamiento.

**Cierre verificable:** devolver un estado inequívoco de fallo o descarte cuando cualquiera de los canarios exigidos cambie, conservando la evidencia; comprobarlo mediante una alteración controlada y una corrida limpia.

## Estado de los seis puntos solicitados

1. **Worker vacío:** la implementación filtra grupos vacíos antes de lanzar procesos. La verificación ejecutable quedó pendiente al cierre de esta respuesta.
2. **Paredes:** los JSON accesibles registran para los workers **586,612 s** y **533,136 s**; el segundo finalizó antes. Los instantes registrados respaldan que no heredó la espera del primero.
3. **Huérfanos:** **no cierra**, por el hallazgo 1. El dato publicado `orphans: 0` no acredita ausencia real de descendientes.
4. **Inventario y canario:** el documento enumera tres archivos con sockets y declara el riesgo residual de la sonda de puerto libre. El JSON registra un canario del checkout `unchanged: true`, pero el comportamiento de fallo ante cambios **no cierra**, por el hallazgo 2.
5. **Evidencia y atribución:** los JSON accesibles registran la misma revisión `379c1a5d…` y `dirty=0`; la pared paralela es **586,613 s**, el trabajo **1115,537 s**, el solapamiento **533,135 s** y la preparación duplicada **0,049396 s**, calculada desde perfiles. El serial registra 57 tests aprobados y sus timestamps dan **871 s** con resolución de segundos; la reducción publicada de **32,7 %** concuerda con las cifras redondeadas. Esta medición corresponde a una muestra de 57 tests, no a `--all`.
6. **Oráculo y regresiones:** no puedo afirmar que estén verdes en esta revisión: la ejecución independiente seguía en curso al cerrar la respuesta. El diff inspeccionado no modifica el cuerpo de `close`, aunque sí añade un campo al perfil compartido.

## Verificación y límites

- **Intake:** Route C validada; `validate-packet` terminó sin diagnóstico y el render de identificación coincide. El contexto de ejecución es v2.
- **Comandos principales:** `git status --short`, inspección del diff y de los JSON de evidencia; reproducción Python de `_is_descendant_of()` y `live_pids_with_marker()`.
- **Ejecución iniciada, resultado no disponible:** `python3 -m pytest -p no:cacheprovider --basetemp=<tmp>/review-t6-015/pytest` sobre el oráculo T6 y las focales T1/T2/T3/T4; después de esa ejecución quedó encolado `python3 scripts/cdad-suite.py validate`. No atribuyo un resultado a ninguno.
- **Estado Git observado:** `HEAD ebd5f1f5`; `M docs/.cdad-state.json` preexistente. No hice commit ni edité archivos del producto.

## Abstentions

- No afirmo que los **12 tests del oráculo**, las focales ni `validate` estén verdes sin el resultado de la ejecución iniciada.
- No afirmo equivalencia ni seguridad de la suite completa: la evidencia examinada corresponde a la muestra, y el conteo de procesos tiene el defecto descrito.
- No ejecuté la suite completa `--all`.
