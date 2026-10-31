# Corrección de alcance — oráculos residuales de T2 (010-004, POST-AUDIT correctivo `-004`)

- **Feature:** `010-004-packet-dispatch-ergonomics`
- **Execution:** `exec-010-004-packet-dispatch-ergonomics-001`
- **Estado registrado:** POST-AUDIT correctivo `010-004-packet-dispatch-ergonomics-test-writer-post-audit-004` recibido y materializado (`post-audit-fixture-migration.md`), commit de tests `db8aa9c6`.
- **Naturaleza:** desviación **de proceso** (alcance del encargo), **no** de contrato, **no** de producto, **no** de la spec.

---

## 0. Qué se corrige y de quién es el defecto

El encargo del POST-AUDIT correctivo `-004` acotó los cambios de aserción a **una sola celda**: la celda C2 (`tests/test_004_002_t7_acceptance.py::_cell_legacy`, `:430-473`). Esa cota era **incorrecta por defecto de alcance del encargo**: dejó fuera tres expectativas legítimas del archivo `tests/test_packet_prepare.py` que PC-04 y §7 exigen actualizar u ordenar, y que la migración de la convención de fixture (ordenada en ese mismo encargo) vuelve inevitables.

**De quién es el defecto:** del **orquestador que redactó el encargo** (esta sesión supervisora), no del rol. El rol hizo lo correcto: respetó la cota, no absorbió los tres fallos, los reportó con causa exacta y los escaló (`post-audit-fixture-migration.md` §5). No hubo debilitamiento ni violencia sobre los tests.

**Consecuencia registrada (medida, no reportada):** tras `db8aa9c6` el universo de los 14 archivos migrados pasa de **63 → 3** fallos, y los 3 residuales están **todos** en `tests/test_packet_prepare.py`:

| Residual | Test | Naturaleza |
|---|---|---|
| (i) | `TestPrepareEffects::test_p1_prepare_writes_three_files_and_stdout_equals_packet_and_render` | oráculo de **conjunto** desalineado por orden de evidencia |
| (ii) | `TestPrepareFailureHasNoEffects::test_p4_unserializable_state_fails_without_effects` | oráculo de **igualdad de árbol** desalineado por orden de evidencia |
| (iii) | `TestPrepareDefaults::test_p2_default_request_derivations_per_role` | oráculo de **conjunto cerrado del request** que no declara `execution_context` |

Ninguno es defecto de producto ni debilitamiento: los tres son **oráculos de test** que PC-04 exige evolucionar. La corrección de alcance se registra aquí y se ejecuta en una unidad propia (§5).

---

## 1. Marco normativo

- **PC-04** (`docs/specs/010-004-packet-dispatch-ergonomics/spec.md:406`): «Toda preparación nueva que publica un encargo […] utiliza contexto v2 y **declara en request y cabecera su localizador canónico**».
- **§7** (`spec.md:449-460`): «Expectativas verificadas por lectura que deben actualizarse **para PC-04**» […]; «el test-writer audita la **lista completa** de tests afectados y actualiza las expectativas **con trazabilidad por test** al requisito anterior, a esta sustitución y a la decisión owner, conservando las garantías aún vigentes. Los dos tests nombrados **no constituyen una lista exhaustiva** ni evidencia de ejecución».
- **§4.1** (matriz de locadores): la preparación nueva recibe el contexto en `.cdad/executions/<execution_id>/execution.json`; la copia `ROOT/EXECUTION.json` sigue admitida solo como vía **histórica explícita** de `render`/`validate-*`/`validate-state`.

La cota del encargo `-004` («una aserción solo puede cambiar en la celda C2») contradijo el §7 en su propio texto: la lista de expectativas a actualizar **no era exhaustiva** y el universo se define por **ejecución**, no por enumeración. Esta corrección no cambia PC-04, ni la spec, ni el producto: PC-04 está implementado como está especificado (`a273042e`) y los fallos son su efecto exigido.

---

## 2. Residual (i) — `test_p1_prepare_writes_three_files_and_stdout_equals_packet_and_render`

**Promesa del test (intacta).** `prepare` escribe exactamente `REQUEST.json`, `PACKET.md` y el state; `stdout == PACKET.md == render`; `validate-packet` pasa. El oráculo es una **igualdad de conjunto exacto** de lo añadido al árbol (`added`, `tests/test_packet_prepare.py:233`) más las igualdades de bytes y `changed == [state_rel]`.

**Defecto de orden, no de expectativa de producto.** El literal esperado declaraba `".cdad"` como **creación de `prepare`** (`:260`) — cierto cuando el proyecto no tenía `.cdad` previo. Con la convención migrada, la fixture materializa el contexto canónico al primer acceso de `PrepareProject.execution_path`, y ese acceso ocurre dentro de `args()` (`:167-176`), es decir **después** del snapshot `before` (`:231`) y **antes** de `after`. Resultado: `added` incluye entradas que no son escrituras de `prepare` sino de la fixture — `.cdad`, `.cdad/executions`, `.cdad/executions/<id>`, `.cdad/executions/<id>/execution.json`.

**Corrección justa (ordenar la evidencia, conservar el oráculo).**

1. Construir los argumentos/materializar el contexto **antes** del snapshot `before`, de modo que `added` mida solo lo que `prepare` añade.
2. Quitar `".cdad"` del literal esperado, porque deja de describir una creación de **este** `prepare` (la fixture lo crea antes). El resto del literal se conserva tal cual, incluida la rama `([".cdad/.lock"] if lock_added else [])` que ya cubre el lock permanente.
3. **No** se elimina la comparación de conjunto: sigue siendo `assertEqual(added, sorted(...))` sobre el conjunto exacto, sin subconjuntos ni exclusiones.

**Medición que lo demuestra (reproducida por el orquestador, no tomada del reporte del rol):** con `args()` evaluado antes del snapshot, `added` resulta exactamente el literal esperado **menos `".cdad"`** más `".cdad/.lock"` — es decir: `.opencode`, `.opencode/agents`, los 12 derivados declarados (`derived_names`), el directorio del paquete y sus dos archivos, y `.cdad/.lock`. `prepare` rc=0. La promesa del test no se toca.

**Por qué no se arregla en la fixture (prohibido):** materializar el contexto en `StateFixture`/`PacketFixture`/`PrepareProject.__init__` deja `.cdad` pre-existente **antes** de que el test protegido `test_p2_default_execution_context_and_out_dir_under_project_cdad` ejecute su `cdad_dir.mkdir()` **plano** (`:416`), que fallaría con `FileExistsError`. Esa razón está medida, no supuesta.

---

## 3. Residual (ii) — `test_p4_unserializable_state_fails_without_effects`

**Promesa del test (intacta).** Un state legible con un escape surrogate aislado no re-serializable: `prepare` sale limpio con exit 2, no deja `.tmp`, no publica paquete, no altera el state ni el árbol.

**Defecto de orden, idéntico al anterior.** `before = tree_snapshot(project.root)` (`:710`) se toma **antes** de `run_prepare(PACKET_CLI, *project.args())` (`:712`); `args()` evalúa el getter entre ambos snapshots y materializa el contexto canónico, de modo que el árbol «cambia» por la **fixture**, no por `prepare`. La igualdad `tree_snapshot(project.root) == before` (`:719`) falla sin que la promesa esté rota.

**Corrección justa.** Evaluar `args` antes del snapshot `before` y pasar esos argumentos a `run_prepare`. Ni una aserción cambia.

**Medición que lo demuestra:** con el orden corregido, `rc=2`, `stderr` último renglón «ERROR: cannot serialize prepared packet: 'utf-8' codec can't encode character '\udc80' in position 1984: surrogates not allowed», árbol **sin cambios** (`True`), out-dir vacío, state byte-idéntico, sin `.tmp`. Requiere **cero** cambios de producto.

---

## 4. Residual (iii) — `test_p2_default_request_derivations_per_role`

**Promesa del test (intacta y endurecible).** El documento `REQUEST.json` es exactamente el dict declarado por rol/subfase (conjunto de claves **cerrado**), con `packet_id`, `contract`, `inputs`, scopes, invariantes, `expected_output` y `evidence_required`.

**Causa.** PC-04 (`spec.md:406`) obliga a que la preparación nueva **declare en el request su localizador canónico**. El request de la fixture (rol `implementer`, subfase `green`, entre otros) declara ahora `execution_context` con el localizador canónico y el dict esperado del test no tiene el campo. Verificado para las **cinco** combinaciones rol/subfase: `execution_context` es la **única** clave extra y su valor medido es siempre el mismo localizador canónico relativo a la raíz:

```
.cdad/executions/exec-003-001-role-packets-001/execution.json
```

**Corrección justa (endurecer, no relajar).** Añadir la clave al dict esperado **con su valor canónico exacto**, no solo su presencia; trazar la actualización a PC-04 y a §7 (lista no exhaustiva). Queda **prohibido** cualquier atajo equivalente a relajar: aserta solo presencia, comparar por sufijo, excluir el campo del dict, o cambiar la igualdad de documento por una comparación de subconjunto. La igualdad exacta del documento **se conserva**.

---

## 5. Decisión registrada

**Decisión (supervisor delegante).** Se corrige el alcance del encargo POST-AUDIT de T2: los tres oráculos residuales de `tests/test_packet_prepare.py` **entran** en el alcance de una unidad correctiva de cierre de T2, con la forma de §2-§4. No se reabre el AUDIT: la lista de trabajo sigue siendo el inventario medido (`fixture-impact-inventory.md`), que esta corrección amplía en tres oráculos de un archivo ya incluido en su §2.

**Fundamento.** (a) PC-04 y §7 ordenan actualizar las expectativas con trazabilidad, y §7 declara la lista no exhaustiva; (b) los tres fallos son de orden de evidencia o de expectativa de fixture/oráculo, medidos uno por uno; (c) ninguno requiere cambio de producto (§2-§4 lo demuestran con sondas reproducidas); (d) la alternativa —dejar tres fallos en el archivo, o absorberlos relajando aserciones— viola el «no-debilitamiento» del propio encargo y el §7.

**Unidad resultante (una subfase, alcance cerrado).** `test-writer` / `post-audit`; **solo** `tests/test_packet_prepare.py`; **solo** los tres tests nombrados. Prohibido tocar `tests/test_role_packets.py::StateFixture`, `PrepareProject.__init__`, la fixture compartida y cualquier otro archivo. **Éxito:** `tests/test_packet_prepare.py` completamente verde y universo de 14 archivos sin fallos, con los 14 tests protegidos verdes y byte-idénticos.

**Cláusula de parada.** Si al ejecutar la unidad alguno de los tres resultara **no** corregible con orden de evidencia o expectativa (es decir, exigiera producto), la unidad **no** lo absorbe: se detiene y lo reporta como regresión. Esta corrección de alcance no autoriza ningún cambio de producto.

---

## 6. Evidencia medida (reproducida por el orquestador)

| Comprobación | Comando (resumen) | Resultado |
|---|---|---|
| Universo 14 archivos, estado actual | `pytest <14 archivos> -q --tb=no -rf` | `3 failed, 96 passed`; los 3, en `test_packet_prepare.py` |
| Universo 14 archivos, baseline (`031fd8ff`, worktree) | ídem | `63 failed, 36 passed` |
| Tests protegidos | 6 RED T2 + 2 POST-AUDIT + 5 PC-08a + C3 f6 | `14 passed` |
| Residual (i), orden corregido | sonda: `p.args()` → snapshot → `prepare` | rc=0; `added` = literal − `".cdad"` + `".cdad/.lock"` |
| Residual (ii), orden corregido | sonda: `args` antes de `before` | rc=2; árbol igual; out-dir vacío; state igual; sin `.tmp` |
| Residual (iii), causa | sonda sobre 5 combinaciones rol/subfase | única clave extra `execution_context`, valor canónico constante |

---

## 7. Límites (honestidad)

- Esta corrección **no** modifica la spec, el plan, la política, el estado contractual ni el producto; el único efecto sobre el ciclo es de **alcance de un encargo de test** y su traza documental.
- El texto materializado del rol (`post-audit-fixture-migration.md`) se conserva **verbatim**, incluidas sus erratas (p. ej. «绿», «mint hunks», «pró todos»): ADR-003 exige fidelidad al FINAL TEXT entregado, no su reescritura por el orquestador.
- Las cifras de §0/§6 se reprodujeron en esta sesión (worktree temporal para el baseline, retirado tras la medición); no se ejecutó la suite completa.
