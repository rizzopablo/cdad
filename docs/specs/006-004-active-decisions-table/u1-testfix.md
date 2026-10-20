## Informe de rol — test-writer, subfase `red` (TESTFIX de U1)

### 1. Diagnóstico del defecto

El RED construía la fila del subcaso «file inexistente» así (`tests/test_006_004_u1_decisions_field.py:481`, antes del arreglo):

```python
row = good_row(existing, **override)      # override = {"file": "docs/adr/ADR-999-no-existe.md"}
```

`good_row` declara `file` como **primer parámetro posicional** (`tests/…:206-214`), así que `file` llega dos veces → `TypeError: got multiple values for argument 'file'` **dentro del test, antes de invocar la CLI**. No era una aserción de contrato: el subcaso nunca alcanzaba el producto. Los otros 7 subcasos del mismo test sí llegaban y pasaban.

### 2. Cambio (único, local, en `tests/`)

`tests/test_006_004_u1_decisions_field.py`, +8/-1, dentro de `test_pd1_malformed_rows_are_rejected_without_publication`:

```python
kwargs = dict(override)
row_file = kwargs.pop("file", existing)
row = good_row(row_file, **kwargs)
```

Se separa la variante `file` del resto de la variante y se entrega como argumento **posicional** (la firma del helper queda intacta y sus demás llamadas no cambian). **El oráculo se conserva literalmente**: el token sigue siendo `("ADR-999-no-existe.md",)` y el control sigue siendo `assert_rejected_without_publication` (rc≠0 · `ERROR:` · sin `unrecognized` · stdout vacío · out-dir vacío · state byte-idéntico · árbol sin cambios). **No se tocó ningún otro oráculo, caso, helper ni archivo de `tests/`.**

### 3. Comandos y salida

**a) Antes del arreglo — el fallo reproducido:**

```
$ python3 -m pytest "tests/test_006_004_u1_decisions_field.py::TestPd1RowShape::test_pd1_malformed_rows_are_rejected_without_publication" -v
>               row = good_row(existing, **override)
E               TypeError: good_row() got multiple values for argument 'file'
tests/test_006_004_u1_decisions_field.py:481: TypeError
FAILED … 1 failed in 1.09s
```

**b) Sonda de no-vacuidad (en `/tmp/opencode/`, fuera del repo, importando los helpers sin editarlos) — el subcaso ahora LLEGA a la CLI:**

```
[fila construida] {"file": "docs/adr/ADR-999-no-existe.md", "reference": "skills/cdad-cycle/references/design-principles.md", "roles": ["test-writer"], "state": "vigente", "summary": "Una decisión vigente de una línea."}
[rc] 2
[stdout] ''
[stderr] ERROR: current decision row docs/adr/ADR-999-no-existe.md: the file does not exist in the project: docs/adr/ADR-999-no-existe.md (R-3)
[out-dir] []
[token en el diagnóstico] True
[OK ] el subcaso alcanza la CLI y el oráculo (rechazo sin publicación) se sostiene
```

**c) Después del arreglo — focal completo:**

```
$ python3 -m pytest tests/test_006_004_*.py -v
test_pd1_good_row_is_accepted_and_request_carries_the_declared_order PASSED
test_pd1_malformed_rows_are_rejected_without_publication           PASSED
test_pd2_row_must_name_the_packet_role                            PASSED
test_pd3_obsolete_row_is_not_admissible                           PASSED
test_pd4_row_cap_fails_closed                                     PASSED
test_v1_installed_product_renders_the_same_package_with_rows      PASSED
test_v3_receive_revalidates_the_request_with_the_widened_set      PASSED
test_a1_unknown_request_key_is_still_rejected                     PASSED
============================== 8 passed in 14.00s ==============================
```

**d) Alcance del cambio (por qué el focal basta):**

```
$ rg -n "test_006_004_u1|good_row|decision_flags" tests/ --glob '!tests/test_006_004_u1_decisions_field.py'
(ninguno)
```

Corrección **local** (una方法的 cuerpo de un test; ningún otro archivo de `tests/` referencia el módulo ni sus helpers) ⇒ según la regla declarada de *widen*, la validación es el **focal**; las 11 regresiones de la ficha U1 no pueden verse afectadas. No corrí la suite completa (política del paquete: la corre una vez quien cierra).

### 4. Commit

```
$ git add tests/test_006_004_u1_decisions_field.py
$ git commit -m "test: 006-004 U1 testfix — subcaso file inexistente"
[main 4f745ac] test: 006-004 U1 testfix — subcaso file inexistente
 1 file changed, 8 insertions(+), 1 deletion(-)
```

```
$ git show --name-only --format='' HEAD
tests/test_006_004_u1_decisions_field.py
```

`4f745acd0140c2bd977d7e3dff4ec17ef968b766` — **sólo `tests/`**. Sin `--no-verify`, sin `git stash`, sin push.

### 5. Límites honestos y desviaciones

- **El focal queda GREEN, no RED** — y se declara con nombre: el producto de U1 (commit `b529f63`) **ya cumple** la cláusula «`file` inexistente ⇒ rc≠0 nombrando la ruta» de PD-1. Esta tarea reparó el **test**, no el producto; el defecto estaba en el helper del RED, como declaró el GREEN en su §5.
- **Aislamiento de fase preservado**: no leí código de implementación. Leí el contrato (`docs/specs/006-004-active-decisions-table/spec.md`), el informe `u1-green.md` (dentro de la raíz de contrato declarada) y `tests/`. `scripts/`, `skills/`, `sources/`, `agents/` y `build/` no fueron leídos.
- **No leí `tests/.sensitive-patterns.local`**; no hay valores del host en el cambio (el comentario sólo menciona el parámetro `file` del helper).
- **No toqué** `docs/.cdad-state.json` (modificado por el orquestador), `docs/planning/` ni `findings/` — siguen sin trackear y fuera de mi commit. `git status --short` tras el commit los muestra intactos.
- La sonda del §3b vive en `/tmp/opencode/probe_u1_file_case_fixed.py`, fuera del repo: no es parte del commit.
- **Siguiente paso sugerido al orquestador**: re-despachar U1 al implementer para el cierre de GREEN (el único rojo focal ya no existe) o, si corresponde, cerrar U1 con la evidencia de este TESTFIX.