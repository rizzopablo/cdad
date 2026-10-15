## Enmienda de oráculo firmada — test-writer, substage RED (005-003 T2)

Rol: **test-writer**. Alcance tocado: **solo `tests/test_005_003_t2_examples_execute.py`**. No leí implementación (`skills/**`, `scripts/**`); ejecuté el focal y la regresión del área como caja negra (subprocess). No corrí la suite completa, no desplegué, no toqué HOME, no hice push.

### (1) Diff exacto del oráculo

Solo se cambió **una clase**: el conjunto de claves *permitidas* del `UPDATE` de continuidad, más su comentario/docstring. La aserción de contenido mínimo (`>=`) ya existía en `:411` y **se conserva**; la aserción de exclusividad pasa a ser una cota de claves permitidas **sin contradecir al CLI**.

```diff
-# §2.3: el UPDATE de continuidad exige estas cuatro; `budget` es opcional.
+# §2.3: el UPDATE de continuidad exige estas cuatro de CONTENIDO; `budget` es
+# opcional y el CLI exige además las claves de idempotencia (`packet_id`,
+# `attempt`). La spec fija el contenido mínimo, no un conjunto exclusivo.
 CONTINUITY_REQUIRED = ("goal", "decisions", "uncertainties", "next_action")
-CONTINUITY_ALLOWED = set(CONTINUITY_REQUIRED) | {"budget"}
+CONTINUITY_ALLOWED = set(CONTINUITY_REQUIRED) | {"budget", "packet_id", "attempt"}

@@ def test_pd3_asset_declares_minimum_examples
-    vista `status`) está presente; se localizan por el asset, nunca por prosa."""
+    vista `status`) está presente; se localizan por el asset, nunca por prosa.
+
+    Enmienda de oráculo (test-writer): la spec §2.3 fija el CONTENIDO MÍNIMO
+    del `UPDATE` (las cuatro claves de contenido; `budget` opcional), NO un
+    conjunto exclusivo de claves. El CLI de continuidad exige además las claves
+    de idempotencia `packet_id` (string no vacío) y `attempt` (int) de nivel
+    superior y falla cerrado sin ellas, así que las claves permitidas se acotan
+    al contenido mínimo + `budget` + esas dos claves del CLI; exigir exclusividad
+    a `{goal, decisions, uncertainties, next_action, budget}` contradecía al CLI
+    y era insatisfacible a la vez que
+    `test_pd3_continuity_update_example_executes`."""

@@ aserciones
-    # §2.3: el UPDATE exige las cuatro claves; `budget` es la única opcional.
+    # §2.3: el UPDATE exige las cuatro claves de CONTENIDO; `budget` es
+    # opcional y el CLI exige además la idempotencia (`packet_id`, `attempt`).
     ...
     assert set(cont_obj) <= CONTINUITY_ALLOWED, (
         "PD-3 violada: el UPDATE de continuidad declara claves fuera del "
-        f"contrato (§2.3: solo `budget` es opcional): "
+        "contrato (§2.3: contenido mínimo + `budget` opcional + las claves de "
+        f"idempotencia exigidas por el CLI): "
         f"{sorted(set(cont_obj) - CONTINUITY_ALLOWED)}"
     )
```

Nota honesta sobre la forma: en lugar de *solo* cambiar `<=` por `>=` (lo que duplicaría la aserción de contenido mínimo ya presente en `:411` y **debilitaría** la garantía al eliminar toda cota de claves), apliqué la opción que el propio encargo habilita —«las claves permitidas son las de contenido **más** las que el CLI exige»—. Así la garantía se conserva acotada y deja de contradecir al CLI.

### (2) Por qué la aserción anterior era más estricta que el contrato

La spec §2.3 fija el **contenido mínimo** del `UPDATE` (`goal`/`decisions`/`uncertainties`/`next_action` + `budget` opcional): **no** un conjunto exclusivo. El oráculo lo leyó como exclusivo (`set(cont_obj) <= {goal,decisions,uncertainties,next_action,budget}`), pero el CLI de continuidad **exige además** la clave de idempotencia y **falla cerrado** sin ella:

- `test_pd3_continuity_update_example_executes` ejecuta el mismo ejemplo contra `cdad_continuity.py begin` y exige `rc=0`. La ejecución real del focal mostró la contradicción (1 failed / 9 passed) con:
  `AssertionError: PD-3 violada: … claves fuera del contrato (§2.3: solo 'budget' es opcional): ['attempt', 'packet_id']`
- El CLI (evidencia ya reproducida por el orquestador) da `rc=1` sin `packet_id`/`attempt`: `update.packet_id must be a non-empty string (idempotency key (execution_id, packet_id, attempt), P3); got None`; con ellos, `rc=0`.
- La regresión aprobada `tests/test_003_004_t1_reviewfix.py` exige `rc != 0` sin `packet_id`, así que el CLI **no** se relaja → el que debía cambiar era el oráculo.

Por eso las dos aserciones eran mutuamente insatisfacibles y la corrección corresponde al oráculo, no al producto.

### (3) Focal

```
$ python3 -m pytest tests/test_005_003_t2_examples_execute.py -q
..........                                                               [100%]
10 passed in 1.79s
```

### (4) Regresión del área

```
$ python3 -m pytest tests/ -q -k "packet or state or role_packet or orientation"
133 passed, 695 deselected in 206.47s (0:03:26)
```

Sin fallos nuevos. (La suite completa **no** se corrió, conforme al encargo.)

### (5) Commit del testfix

`5e628de24c939483b9c1853b200b7feba246f606`

```
test(005-003): testfix T2 - el oraculo del UPDATE exige contenido minimo, no un conjunto exclusivo de claves
 1 file changed, 19 insertions(+), 5 deletions(-)   [solo tests/test_005_003_t2_examples_execute.py]
```

Solo se commiteó el archivo de test; el trabajo de producto que ya estaba en el árbol (`skills/cdad-cycle/assets/orientation-examples.json`, `references/orientation.md`, `references/project-start.md`, `docs/.cdad-state.json`) quedó **sin commitear**, fuera de mi alcance.