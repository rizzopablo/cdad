# Revisión independiente de T1

**Dictamen: rechazo de T1 para el gate de integración**, sujeto a la decisión del responsable. Encontré defectos que pueden presentar una captura parcial como completa o alterar el resultado contractual del cierre. No se modificaron archivos durante esta revisión.

## Hallazgos

### 1. Una captura parcial puede declararse completa

**Required — Verdict: BLOCKING — Bucket: h**  
**Ubicación:** `scripts/cdad-suite.py:962-977`; `scripts/cdad_suite_observer.py:29-42`

El observador captura excepciones al registrar una fase y continúa. Sin embargo, `build_profile` solo comprueba que exista **alguna** fase por nodeid; tampoco usa los nombres devueltos por `read_xml_names`. Por tanto, una captura que perdió una fase emitida puede terminar con `status: complete`.

Lo comprobé con un XML parseable sin casos y un registro que contenía únicamente `setup`: `build_profile` devolvió `complete`. El test de captura incompleta (`tests/test_017_001_suite_profile.py:280-328`) cubre una interrupción, pero no induce la pérdida de una fase con el hijo terminado.

**Consecuencia:** el responsable puede consumir un perfil incompleto creyendo que las fases y resultados están íntegros, contrario a §4.3 e INV-6.

**Corrección propuesta:** conservar explícitamente los errores de captura del observador y hacer que fuercen `incomplete`; comprobar la integridad y correspondencia de la captura sin inventar fases no emitidas. La condición de cierre es demostrar, con una pérdida inducida de una fase y con XML inconsistente, diagnóstico incompleto sin alterar el rc de pytest.

### 2. Un fallo al generar el perfil puede sustituir el resultado de pytest

**Required — Verdict: BLOCKING — Bucket: h**  
**Ubicación:** `scripts/cdad-suite.py:1083-1090`

Después de terminar el hijo, `build_profile` y `write_json_atomic` se ejecutan antes de registrar `state="finished"` y `rc`, sin protección frente a errores de instrumentación. Por ejemplo, un error de escritura de `profile.json` propaga la excepción: el intento puede quedar en `running` con `rc: null`, aunque pytest ya haya terminado.

**Consecuencia:** un fallo de medición cambia el resultado observable de `close` y oculta el rc real, en contradicción con §4.3 y PC-2.

**Corrección propuesta:** separar la finalización contractual del intento de la escritura del perfil; ante fallo de captura, conservar el rc del hijo y dejar un diagnóstico recuperable o una ausencia explícita del perfil. La condición de cierre es inducir un fallo de escritura del perfil tras un pytest terminado y verificar tanto el rc devuelto como el registrado.

### 3. Una interrupción manejada pierde el argv y el tiempo del hijo

**Required — Verdict: BLOCKING — Bucket: h**  
**Ubicación:** `scripts/cdad-suite.py:895-916, 1057-1066`

`child_argv` y `child_wall_s` solo se asignan cuando `run_pytest_to_logs` retorna. Si se produce `KeyboardInterrupt` durante la ejecución, el perfil incompleto se escribe con `pytest_argv: []` y `pytest_wall_s: null`, aunque el proceso hijo ya haya sido lanzado.

**Consecuencia:** el perfil de un intento interrumpido no permite reconstruir qué comando se midió ni el tiempo transcurrido, pese a que T1 exige argv efectivo y tiempo del hijo recuperables.

**Corrección propuesta:** conservar el argv antes de lanzar el hijo y recuperar el tiempo monotónico también en la ruta de interrupción, sin cambiar el tratamiento contractual de esta. Verificarlo mediante una interrupción manejada; el test actual usa `SIGKILL`, que no ejercita esa ruta.

## Evidencia y alcance

- Commit revisado: `b3c9770e1a7c65f311ee84b31a1c6c9937e15912`. El diff contiene únicamente `scripts/cdad-suite.py` y el nuevo `scripts/cdad_suite_observer.py`; no modifica `tests/`. El RED aprobado está en `dd3927ec`.
- Focal ejecutado:  
  `python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py`  
  **Resultado:** `5 passed in 6.76s`.
- Validación requerida: `python3 scripts/cdad-suite.py validate` → **rc 0**, `status: "ok"`, 1999 nodeids recolectados, 239 módulos inventariados y 31 entradas de mapa. La salida también declara `timing.status: "pending"` y tres destinos placeholder.
- El informe GREEN declara la regresión de tres módulos con `49 passed`; no la volví a ejecutar en esta revisión. La suite completa no se ejecutó.
- La prueba puntual de `build_profile` descrita en el hallazgo 1 produjo: `empty XML and setup-only: complete`.

## Abstentions

- No acredité de forma independiente la regresión proporcional declarada en GREEN ni el comportamiento integral de la suite completa.
- La entrega T1, incluso corregida, no acredita por sí sola operaciones calibradas ni una base completa; corresponden a tareas posteriores del plan.
