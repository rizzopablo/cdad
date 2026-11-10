# Revisión T6-003

**Veredicto: T6 no pasa el gate.** El bloqueante relativo a la familia de procesos no cierra: reproduje una corrida que dejó un descendiente vivo y, aun así, devolvió éxito y declaró `orphans: 0`. Por tanto, **`--workers 2` no queda acreditado como seguro para la corrida final `--all`**.

El descarte por canario está implementado, pero no pude completar su verificación ejecutable independiente antes de cerrar esta revisión. Además, encontré una limitación material de la huella utilizada para detectar cambios persistentes.

## Hallazgos bloqueantes

### 1. Un descendiente que crea su propia sesión escapa al barrido

**Required · Verdict: BLOCKING · Bucket: h**

El runner asigna un grupo de procesos a cada worker y luego busca exclusivamente miembros de ese grupo (`scripts/cdad-suite.py:1664–1685, 2166`). Un descendiente puede iniciar otra sesión y salir de ese grupo.

**Reproducción independiente:** creé fuera del repositorio un test temporal que lanzó `/bin/sleep 120` con `start_new_session=True`, sin la ruta de evidencia en sus argumentos. El comando:

```text
python3 scripts/cdad-suite.py parallel --workers 1 \
  --evidence-root <directorio-temporal>/evidence \
  --nodeids <directorio-temporal>/nodeids
```

terminó con **rc 0**, `veredicto=accepted` y `orphans=0`, mientras el proceso hijo seguía vivo. Lo terminé explícitamente después y borré la sonda y su archivo de selección. La primera tentativa no llegó a ejecutar el test porque no había creado el directorio de evidencia; la reproducción citada es la segunda, corregida.

No es solo una posibilidad hipotética de la API: hay tests de la selección que usan `start_new_session=True`, por ejemplo `tests/test_006_001_t3_integration.py:313`.

**Consecuencia:** el lote puede declarar que todos los procesos terminaron y aceptarse pese a dejar actividad viva que afecte ejecuciones posteriores. Esto impide acreditar la garantía de procesos finalizados de PC-10.

**Cierre verificable:** gestionar o detectar también descendientes que cambien de grupo, tanto tras la terminación normal como ante fallo parcial; repetir la sonda y demostrar detección, limpieza y descarte. Si la solución impone una limitación explícita en vez de ofrecer esa garantía, debe demostrarse que los consumidores de la selección final la cumplen y ajustar las afirmaciones de evidencia.

### 2. La huella del checkout puede no detectar una modificación persistente

**Required · Verdict: BLOCKING · Bucket: h**

`checkout_canary_snapshot()` (`scripts/cdad-suite.py:1522–1565`) reduce todo el árbol a cantidad de archivos, suma de tamaños y **un único** mtime máximo. Si se modifica un archivo manteniendo su tamaño y otro archivo ya tiene un mtime posterior, la huella puede permanecer idéntica.

Lo reproduje independientemente sobre una raíz temporal, invocando la misma función: cambié el contenido de un archivo de `one` a `two`, manteniendo otro archivo con mtime posterior. Resultado: `same_fingerprint True`, aunque el contenido había cambiado.

**Consecuencia:** una escritura persistente en `build/` o `.cdad/` puede quedar sin detectar y permitir un resultado `accepted`, pese al contrato del lote que exige descartarlo cuando cambie el checkout. Esto no exige una garantía universal contra escrituras transitorias —que la spec expresamente excluye—, sino que señala una modificación persistente concreta que la huella pierde.

**Cierre verificable:** comparar una huella por entrada suficiente para detectar este caso, o sustituirla por otro control que demuestre la detección; reproducir el cambio de igual tamaño con un mtime máximo ajeno y comprobar descarte y conservación de evidencia.

## Contraste de los puntos anteriores

- **Worker vacío:** el código filtra grupos vacíos antes de lanzar pytest. La comprobación ejecutable independiente estaba todavía en curso.
- **Paredes:** el JSON registra **618,2529 s** y **577,1724 s**; los timestamps muestran que el segundo terminó antes. El solapamiento registrado es **577,1708 s**.
- **Familia de procesos:** la búsqueda ya no depende de la línea de comandos y registra PGID, pero **no cubre descendientes que abandonan el grupo**, como demuestra la reproducción.
- **Canario y puertos:** existe lógica de rechazo por delta de canario y el documento inventaría tres archivos consumidores de puertos, con riesgo residual declarado para la sonda de puerto libre. No ratifico todavía el comportamiento ejecutable de rechazo ni la seguridad de `--all`.
- **Cifras:** los JSON accesibles atribuyen ambas corridas a `32676177…`, con `dirty=0`. La serial tiene timestamps separados por **855 s**; el paralelo registra **618,2545 s**, trabajo **1191,835 s**, preparación **0,1670 s** y duplicada **0,0337 s**. La reducción calculada es **27,69 %**, redondeada a **27,7 %**. Se registran 57 aprobados en ambos agregados. La evidencia es de una muestra, no de `--all`.
- **`close`:** el diff inspeccionado desde antes de la introducción del paralelo no cambia el cuerpo de `cmd_close`; sí añade un campo de preparación al perfil compartido.
- **Validación:** `python3 scripts/cdad-suite.py validate` devolvió **rc 0**, `status: ok`.

## Evidencia y límites de ejecución

- **Route C validada:** `validate-request` y `validate-packet` terminaron sin error; el render de identificación coincide.
- **Revisión examinada:** `HEAD 20ed39f1`; `scripts/cdad-suite.py` tiene el mismo SHA-256 que en `32676177`. `docs/.cdad-state.json` figuraba modificado antes de mi revisión.
- **Focales y regresión:** lancé en segundo plano el oráculo T6 y las selecciones T1–T4 y de regresión proporcional. Al cierre solo había salida parcial, sin resumen; **no atribuyo un número de pruebas verdes ni un resultado final**.
- No modifiqué archivos del producto ni hice commit. No ejecuté la suite completa.

## Abstentions

- No afirmo que los **14 tests del oráculo** ni las demás focales estén verdes en esta revisión hasta disponer del resultado completo.
- No afirmo haber verificado mediante una alteración real de `build/` el ciclo completo de rechazo y conservación de evidencia; tampoco afirmo cerrada la comprobación ejecutable del worker vacío.
- No extrapolo las cifras de la muestra a la suite completa ni doy por demostrada su equivalencia o seguridad.
