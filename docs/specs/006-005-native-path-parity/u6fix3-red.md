## Informe — test-writer, subfase RED (006-005 U6-3)

**Vía de intake:** packet validado (`006-005-native-path-parity-test-writer-red-014`). No se cargaron skills de ciclo completas. No se leyó código de implementación ni `tests/.sensitive-patterns.local`.

### Archivos modificados

- `tests/test_006_005_u1b_dispatch_entry.py` (+226 líneas; único archivo tocado)
  - Docstring del módulo: corrección declarada U6-3 (llave «proyecto» con tres valores) y mapa actualizado.
  - Constantes `ATTEMPT_U63_A/B/D`.
  - Clase nueva `TestPd5E1NativeProjectKeyU63` con 4 casos.

### Mapa test → PD

| Test | PD / fuente | Resultado hoy |
|---|---|---|
| `test_u63_ancestor_directory_with_a_matching_parent_is_verified` | PD-5 / E1 (U6-3), INV-15, §2.3, §3.1 E1 | **RED** (AssertionError: rechazo `the project key does not match`) |
| `test_u63_ancestor_directory_without_a_discriminating_key_is_unknown_pd6` | PD-5 / E1 (U6-3) + PD-6 (O-3) | **RED** (AssertionError: mismo rechazo) |
| `test_u63_foreign_directory_is_a_rejection_naming_the_project_key` | PD-5 / E1 (U6-3), INV-2 | Pasa (control: el hermano ajeno sigue siendo rechazo) |
| `test_u63_directory_inside_the_root_still_matches` | PD-5 / E1 (U6-3), INV-15 | Pasa (control: pertenencia dentro de la raíz intacta) |

Diseño relevante: en (b) `--session` declara únicamente la fila candidata para que exista la lectura acotada del store y la llave «proyecto» se evalúe de verdad; el test aserta `session: null` (el id declarado no acredita en la vía nativa) y exige la entrada `observe` del log del módulo para que el caso no pase en vacío. En (a) se verifica al padre como llave discriminante, un intento (`single_record`), una entrega (descriptor + parte byte-exacta) y la sesión observada.

**A-1:** se auditó la suite `tests/test_006_005_*` y no hay test existente que fije el directorio **ancestro** como contradicción (el caso previo de rechazo usa un **hermano** de la raíz, `self.base / "otra-carpeta"`, que U6-3 mantiene como ajeno). No hizo falta reformular ningún test existente; queda declarado en el docstring.

### Comandos y salidas

1. Estado inicial y focal completo (verde pre-RED):

```
$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py -q
13 passed in 15.85s
```

2. Focal nuevo (RED por aserción, sin ImportError/SyntaxError):

```
$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py -q -k u63
2 failed, 2 passed, 13 deselected in 3.33s

FAILED ...::test_u63_ancestor_directory_with_a_matching_parent_is_verified
FAILED ...::test_u63_ancestor_directory_without_a_discriminating_key_is_unknown_pd6
E  AssertionError: 1 != 0 : PD-5/E1 (U6-3): el directorio ANCESTRO de la raíz ... es una llave NO EVALUABLE, nunca una contradicción ...
E  cdad_dispatch: the native identity contradicts the observation ...: the `project` key does not match — ... The session directory must belong to the authorized project root ...
```

3. Focal completo del archivo:

```
$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py -q
2 failed, 15 passed in 18.86s
```

4. Todos los focales `tests/test_006_005_*.py` (U1a, U1b, U1c, U2, U3, U3b, U4, U5, U6fix1, U7):

```
$ python3 -m pytest tests/test_006_005_u1a_runtime_config.py \
    tests/test_006_005_u1b_dispatch_entry.py tests/test_006_005_u1c_packet_agent.py \
    tests/test_006_005_u2_opencode_module.py tests/test_006_005_u3_temporary_scope.py \
    tests/test_006_005_u3b_derived_temporary_permission.py tests/test_006_005_u4_single_entry.py \
    tests/test_006_005_u5_disposition_failed.py tests/test_006_005_u6fix1_capabilities_entry.py \
    tests/test_006_005_u7_scribe_role_report.py -q
2 failed, 94 passed in 119.50s (0:01:59)
```

Las únicas dos fallas son los dos casos RED declarados; el resto de la familia 006-005 sigue verde. Suite completa: no ejecutada (política declarada; la corre quien cierra).

### Commit

```
f6054ce test: 006-005 U6-3 RED — llave proyecto de la vía nativa con ancestro no evaluable
 tests/test_006_005_u1b_dispatch_entry.py | 226 ++++++++++++++++++++++++++++++
 1 file changed, 226 insertions(+)
```

`git status --porcelain` posterior: sólo los no trackeados ajenos (`docs/planning/`, `findings/…`). Sin `--no-verify`, sin stash, sin push.