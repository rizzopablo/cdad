# Informe GREEN — 005-012 T5 (`implementer`, subetapa `green`)

**Rol:** implementer · **Subetapa:** `green` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Paquete:** `005-012-transition-registration-implementer-green-003` · **Tarea:** T5
**Contrato:** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) — PD-14, PD-15 (+ PD-10/PD-11 y PD-17 como soporte). **Oráculo rojo:** `docs/specs/005-012-transition-registration/t5-red.md`, focal `tests/test_005_012_t5_approval_vigency.py` (commit `9669c0a`).

*Nota de anonimización:* la raíz del repo se cita como `<repo>`; los ids del fixture (`epic-demo-100-fixture`, `demo-100-transition-fixture`, `ses-demo-0001`) son sintéticos del fixture del test, no de otros proyectos.

## (a) Qué implementé y dónde

Un solo archivo: `skills/cdad-cycle/scripts/cdad_packet.py` (+62/−2). Dos piezas, ambas aditivas:

1. **Lector aditivo (el predicado «vigente»).** Nuevo helper `_superseded_transition_keys(state)` (junto a `_approved_spec_entries`, `:~1398`): recorre `stage_history` y devuelve el conjunto de claves nombradas por el campo estructural `supersedes` de cualquier entrada. `_approved_spec_entries` ahora descarta las entradas cuyo `transition_key ∈ superseded`. **No toca la regla del pin** (D3/PD-18): sólo filtra qué entradas llegan a la comparación de pin de `_contract_approval_for`, que queda intacto. Sin ninguna clave `supersedes` en el state, el conjunto es vacío y la selección es idéntica a la actual (aditividad/PD-17). Una entrada `supersedes`/`transition_key` `null` (forma de las entradas emitidas por la operación en clases sin marca) se ignora por el `isinstance(str)`.

2. **Guard de registro (PD-14, registro).** Dentro de `register_transition`, en el bloque de exclusiones estructurales (después del no-op de PD-11 y antes de cualquier escritura): cuando `--transition gate` con `--stage specification` y `--contract-path P`, se buscan las entradas `specification` **vigentes** del `(feature, P)`.
   - **Sin `--supersedes` y con alguna vigente** → `PolicyError` `state incoherent` que **nombra la entrada vigente** (`transition_key`) y el **campo `supersedes`**, antes de escribir (INV-7).
   - **Con `--supersedes <key>`** → se exige que la clave nombre una entrada **existente**, de la **misma feature** y el **mismo `contract_path`** (reusando `_registered_transition`); si no, `state incoherent`. Si es válida, el registro sigue y la entrada nueva escribe el campo `supersedes` (ya lo hacía desde T1/T2).
   - Se agregó la constante `SPEC_GATE_STAGE = "specification"` junto a `TRANSITION_CLASSES` (naming intencional).

Comentarios en inglés (convención del producto), diagnósticos accionables en el estilo existente. Ninguna reescritura de entradas (INV-3): la sustitución se deriva de la declaración de la entrada nueva. Ninguna validación nueva exige campos a las entradas históricas (sin `transition_key`).

## (b) Corridas (salida pegada, post-commit)

```
$ python3 -m pytest tests/test_005_012_t5_approval_vigency.py -q
.....                                                                    [100%]
5 passed in 11.04s
```

```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py tests/test_005_012_t2_gate_authority.py -q
.............................                                            [100%]
29 passed in 22.64s
```

```
$ python3 -m pytest tests/test_005_001_t1_role_approval.py tests/test_005_001_tcorr.py \
    tests/test_005_005_t1_replace_conserved.py tests/test_packet_prepare.py -q
..........................................                               [100%]
42 passed in 44.60s
```

Nota: la **suite completa no se corrió** (política del paquete: la corre una vez quien cierra). Se corrió el focal + los focales T1/T2 que el lector y el registro tocan + las regresiones declaradas, tal como pide la ficha.

## (c) Prueba de que `tests/` no se tocó

```
$ git diff --name-only 9669c0a..HEAD -- tests/
(empty)

$ git status --porcelain -- tests/
(empty)
```

El oráculo congelado (`9669c0a`) queda intacto: ni ediciones ni archivos nuevos bajo `tests/`. `git status` global sólo muestra `docs/.cdad-state.json` (registro del despacho hecho por el orquestador; **no** es mío y **no** lo commiteé).

## (d) Commit

```
$ git log --oneline -1
c164b30 feat: 005-012 T5 GREEN — vigencia estructural de la aprobacion (supersedes + lector aditivo)

$ git show --stat --oneline HEAD | tail -3
c164b30 feat: 005-012 T5 GREEN — vigencia estructural de la aprobacion (supersedes + lector aditivo)
 skills/cdad-cycle/scripts/cdad_packet.py | 64 +++++++++++++++++++++++++++++++-
 1 file changed, 62 insertions(+), 2 deletions(-)
```

Un solo archivo, prefijo `feat:`. Sin `--no-verify`, sin push, sin despliegue, sin tocar HOME. `sha256` del archivo implementado: `2003fe0a…57fe`.

## (e) Interpretaciones y límites

1. **Alcance del guard.** Se aplica sólo a `gate` con `--stage specification` **y** `--contract-path` citado, que es el par sobre el que PD-14 declara la vigencia. Los gates de otras etiquetas (T2 usa `tdd-review`, y su contrato de etapa 2 usa una ruta distinta para no colisionar con la entrada pinneada del fixture) no se ven afectados: 29/29 verdes.
2. **Caso `--supersedes` inválido (no cubierto por el focal, declarado).** El RED declaró no asertarlo porque la spec declara el caso válido pero no el marcador del inválido. Implementé el chequeo fail-closed mínimo (`state incoherent`, nombrando el hecho) porque sin él una clave inexistente dejaría la sustitución sin efecto y las dos aprobaciones vigentes, contra el sentido de D-8. No inventa oráculo ni marcador nuevo: reusa `state incoherent` (disciplina estructural).
3. **Sin condiciones de detención.** El predicado «vigente» no obligó a re-declarar la regla del pin (se consume intacta) ni a exigir campos a entradas históricas; por eso no me detuve (INV-3/INV-4 verdes, PD-17 con `validate-state` rc=0 antes y después del focal).
4. **Frontera del juicio respetada.** El guard decide por el campo **estructural**; la prosa del `note` no participa (PD-15, verificado por el focal: dos entradas con nota «reemplaza» y sin campo siguen habilitando). No se parsea ningún texto.

Sin bloqueos. El contrato fue verificable y el focal pasó de 5 rojas a 5 verdes sin editar los tests.
