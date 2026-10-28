# Revisión stage 4 — 008-002 T3 (`scripts/cdad-suite.py` @ 9e3fda8, `timing-disposition.json`)

**Archivos modificados:** ninguno, la revisión fue de solo lectura. **Commit:** ninguno; revisé 9e3fda8 y la fase RED en 03531bb.

**Comandos que ejecuté y su resultado:**
- `sha256sum docs/specs/008-002-suite-by-capability/spec.md` → `295c309c…ee02bb`. Coincide con el paquete.
- `python3 -m pytest -q -p no:cacheprovider tests/test_008_002_suite_selection.py` → **15 passed in 15.42s**.
- `python3 scripts/cdad-suite.py validate` sobre el checkout real → **falla**. Da 2 módulos sin inventariar (`tests/test_008_002_suite_selection.py` y `tests/test_008_002_variant_controls.py`), 18 nodeids sin capacidad y `pc-map` con `decision invalida 'eliminar-propuesto (original se conserva hasta el gate de review de T2/T4)'`.
  - El `rc=0` que se ve en la salida corresponde a `head`, no al CLI.
- Prueba de renombre en un repo temporal: `git mv tests/test_old.py tests/test_new.py`.
  - `git diff --name-only HEAD --` → solo `tests/test_new.py`.
  - Con `--no-renames` → `test_new.py` y `test_old.py`.

## Hallazgos

**1. Un test trasladado pierde sus sustitutos y contratos — Required.** Veredicto: BLOCKING. Bucket: h.
- **Dónde:** `scripts/cdad-suite.py:379`.
- **Qué pasa:** `git diff --name-only` aplica la detección de renombres por defecto. En un traslado, la ruta antigua nunca llega a `selection_for_changes`, así que no se consultan el inventario ni el mapa de la base. Lo verifiqué arriba.
- **Por qué importa:** §5 lo pide explícitamente: «Test eliminado o trasladado: consulta el inventario y mapa de la base». Además, el piloto T4 va a mover y fusionar código de test.
- **Arreglo:** añadir `--no-renames` a la llamada de la línea 379.
- **Cierre verificable:** un test sintético con `git mv` que seleccione los destinos del mapa de la base.

**2. La conservación de obligaciones acreditadas se compara contra HEAD, no contra la base anterior — Required.** Veredicto: BLOCKING. Bucket: h.
- **Dónde:** `scripts/cdad-suite.py:270-283`.
- **Qué pasa:** en cuanto se commitea un `pc-map` sin la obligación, HEAD ya no la tiene y `validate` vuelve a verde. Solo detecta desapariciones sin commitear.
- **Por qué importa:** §4 dice que «una obligación antes acreditada no puede desaparecer del mapa después», y el flujo CDAD commitea cada lote. El test `test_pc3_validate_rejects_disappeared_accredited_obligation` (`tests/…:256`) solo cubre el caso sin commit, así que es una autodeclaración parcial.
- **Arreglo:** comparar contra una referencia fija:
  - una baseline acreditada versionada (por ejemplo el `pc-map` de T2 o `measurement-before`), o
  - un `--base` o el merge-base.
- **Cierre verificable:** un test que commitee la eliminación y espere un código no cero.

**3. Faltan 4 de las 7 variantes de PC-5 en los tests — Required.** Veredicto: BLOCKING. Bucket: h.
- **Dónde:** `tests/test_008_002_suite_selection.py:279-305`.
- **Qué falta:** PC-5 exige test nuevo, eliminación con sustituto, helper compartido y cambio de producto. Solo están cubiertos el cambio sin commit, la base sin inventario y `--all`.
- **Qué queda sin oráculo:** los caminos fail-closed que pide el objetivo:
  - helper sin consumidores (`:462-465`);
  - test eliminado sin sustituto (`:472-477`);
  - test nuevo sin trackear (`:380`);
  - cambio del propio selector, que selecciona todo (`:452`).
- **Variantes de PC-2 y PC-1 que tampoco tienen test:**
  - módulo mixto con nodeids explícitos (PC-2);
  - control negativo «asignación mixta incompleta» (PC-1).
- **Nodeid inexistente:** `test_pc1_validate_rejects_nonexistent_nodeid` solo lo prueba vía destino del mapa, no vía `nodeids` del inventario (`:212-214`).
- **Cierre verificable:** un test por cada variante citada, con nodeids seleccionados y código de salida como oráculo.

**4. `validate` falla sobre el repositorio real tras T3 — Required.** Veredicto: BLOCKING. Bucket: m.
- **Evidencia:** la salida de `validate` de arriba.
- **Qué pasa:**
  - El vocabulario cerrado `DECISIONS` (`:40`) rechaza el valor `eliminar-propuesto (…)` que T2 escribió en `pc-map.json`. Es un choque de contrato entre productor (T2) y consumidor (T3).
  - La propia feature deja sin inventariar sus dos módulos nuevos.
- **Por qué importa:** el plan de T3 dice «PC-1/PC-2: inventario validado» (`plan.md:138`). Si se deja para T4, tiene que constar explícitamente. Si no, T4 consume un selector que no valida su propia entrada.
- **Cierre verificable:** `validate` con rc 0 en el checkout antes de cerrar T4, y el valor de `decision` alineado con §4 (`mantener|fusionar|eliminar`, con la propuesta en un campo aparte).

**5. Validación débil de `timing-disposition.json` — Required.** Veredicto: OPTIONAL. Bucket: m.
- **Dónde:** `scripts/cdad-suite.py:286-306`.
- **Qué falla:**
  - `evidence` no se valida como lista. Un string se recorre carácter a carácter (`:299`).
  - Cualquier archivo existente, como `README.md`, cuenta como «evidencia propia».
  - No se comprueba que `target_ceiling_s == 2`. Un `resolved` con `target_ceiling_s: 5` pasa.
  - Los `cases` no se contrastan con la colección. PC-7 pide «expone las referencias de los casos existentes».
- **Por qué no bloquea:** el archivo actual (`pending`, 4 casos, motivo y criterio de resolución separados) cumple PC-7.
- **Cierre verificable:** comprobar tipos y que cada `cases[].nodeid` esté en la colección.

**6. `_is_collectible` acepta cualquier etiqueta `[…]` sobre un test plano — Consider.** Veredicto: OPTIONAL. Bucket: m.
- **Dónde:** `scripts/cdad-suite.py:223-234`.
- **Qué pasa:** `tests/x.py::test_a[ghost]` pasa como destino existente. Dentro de lo que pide §5 (integridad estructural) es aceptable, pero deja pasar errores tipográficos de etiqueta.
- **Arreglo:** exigir que la etiqueta figure en `variant-controls.json`.

**7. La colección y la ejecución no fijan `--rootdir` — Nit.** Veredicto: OPTIONAL. Bucket: l.
- **Dónde:** `scripts/cdad-suite.py:95-98` y `:357-359`.
- **Qué pasa:** un `pytest.ini` o `pyproject.toml` en un directorio ancestro del repo cambiaría el prefijo de los nodeids y se perderían coincidencias, que acabarían en diagnósticos falsos. En el repo real no hay archivo de configuración en la raíz.
- **Arreglo:** pasar `--rootdir=.` y `-c /dev/null`, o un equivalente.

**8. Escrituras fuera de los propios artefactos — FYI.**
- `measure` es de solo lectura.
- La caché de pytest está desactivada (`-p no:cacheprovider`).
- Los `.pyc` caen en `tests/__pycache__`, dentro de la raíz, y `surface` los filtra (`:370-374`).
- No encontré escrituras fuera de la raíz.

**9. Archivos de `tests/` que no son `.py` — FYI.**
- **Dónde:** `scripts/cdad-suite.py:479-481`.
- Las fixtures JSON bajo `tests/fixtures/` caen en `surface_consumers` y fallan cerrado («sin superficie clasificada») salvo que el inventario las declare. Es correcto según §5, pero cualquier cambio de fixture bloqueará el gate hasta que se clasifique.

**10. Base inválida con `--all` — FYI.**
- **Dónde:** `scripts/cdad-suite.py:494-509`.
- **Qué pasa:** una base mal escrita junto con `--all` se ignora y se ejecuta todo. Sin `--all`, el diagnóstico atribuye el fallo a la falta de inventario y no a una ref inválida, lo que confunde. Sigue siendo no cero.

## Lo que comprobé y no deja hallazgo

- `list` y `run` deduplican y ordenan (`:155`).
- Una selección vacía da código no cero en `:156-157`, `:352-353` y `:487-489`.
- `run` ejecuta solo los nodeids explícitos y propaga el código de pytest.
- `surface` sin inventario o mapa en la base da código no cero; `--all` es explícito.
- Un cambio en el selector o en los artefactos de selección selecciona todo.
- Un helper sin consumidores declarados y un test eliminado sin sustituto fallan cerrado.
- Los tests existentes usan oráculos observables (marcadores y código de salida), no mocks.

## Abstenciones

- **Defecto de `prepare`** (un root aceptado que después resulta ser un archivo): no hay `prepare` ni `close` en `cdad-suite.py` ni en los tests de T3. No pude localizar el código, así que no lo juzgo. Si está en `close` (PC-6), queda fuera de este lote.
- **Suite completa:** no la ejecuté, por la política del paquete.

Resultado: **3 BLOCKING** (hallazgos 1, 2 y 3), **1 BLOCKING de integración** (hallazgo 4, que puede diferirse a T4 solo de forma explícita) y el resto opcionales. Este dictamen no aprueba el lote; los bloqueantes los decide el usuario.
