# Informe RED (review-fix B3) — 005-012 T5 (`test-writer`, subetapa `red`)

**Paquete:** `005-012-transition-registration-test-writer-red-010` · **Ejecución:** `exec-005-012-transition-registration-001` · **Tarea:** T5 (review-fix del bloqueante B3)
**Contrato (oráculo):** `docs/specs/005-012-transition-registration/spec.md` (sha256 `9e34750f…e7cc9`, **draft-004 vigente**: PD-14 y D-8 enmendados) — **derivado del contrato, nunca de la implementación**. **Plan:** §4 ficha T5.
**Archivo editado (único):** `tests/test_005_012_t5_approval_vigency.py` — **+360 líneas, 0 borrados** (5 tests existentes **intactos** + 3 nuevos; 8 en total). **Commit:** `dc13903`.

*Nota de anonimización:* la raíz del repo se cita como `<repo>`; sin rutas absolutas del dueño, ids crudos de sesión ni nombres de otros proyectos: los ids del fixture son sintéticos.

## (a) Casos agregados y PD que verifica cada uno

El predicado enmendado es único: **«vigente» = la entrada cuyo pin (`contract_path` + `contract_sha256` derivado) NOMBRA los bytes actuales** — el mismo criterio que PD-8(b). Los tres casos lo ejercen en negro (subproceso; el **lector** se observa por su efecto: `prepare --role test-writer --substage red` que habilita rc=0 o bloquea `approval pending` rc=2).

| Test nuevo | PD | Caso | Verifica |
|---|---|---|---|
| `test_b3_pd14_reapproval_with_new_bytes_over_keyless_approval_needs_no_supersedes` | **PD-14** (consecuencia 1) + D-8; PD-20 | **1** | Entrada `specification` **keyless** cuyo pin **ya no nombra** los bytes actuales (el contrato se enmendó después): `gate --stage specification --contract-path <spec>` **sin** `--supersedes` → **rc=0**, sin marcador; entrada **nueva** con su `transition_key` y el **pin derivado** (PD-20), **sin** `supersedes`; la keyless queda **intacta** (append-only) y **no** habilita; el lector **se habilita** por la nueva (rc=0) |
| `test_b3_pd14_same_bytes_still_requires_supersedes_and_the_amendment_does_not` | **PD-14** (consecuencias 2 y 3); PD-20 | **2 + 3** | Con la entrada vigente **con clave** cuyo pin **nombra** los bytes actuales: reaprobar los **MISMOS** bytes **sin** `--supersedes` → **rc=2**, `state incoherent`, nombrando la entrada y el campo, state **byte a byte idéntico** (INV-7); **con** `--supersedes <key>` → **rc=0** con el campo escrito. Mitad discriminante (consecuencia 1, «tenga o no clave»): enmendados los bytes, esa vigente ya no compite → `gate` posterior **sin** `--supersedes` → **rc=0** |
| `test_b3_pd17_amendment_keeps_validate_state_green_and_history_untouched` | **PD-17** + INV-3 | **4** | Sobre el flujo del caso 1: `validate-state` **rc=0 antes y después**; **ninguna** entrada histórica keyless se invalida ni se reescribe (no ganan la clave nueva, no pierden el pin) y la operación **sólo anexa** (UNA entrada nueva). Sin porcentajes ni conteos del state vivo del repo |

**Caso 3** no es un flujo aparte: es la propiedad «sin efectos» del rechazo del caso 2, asertada con `assert_unchanged` dentro del mismo test. **Casos 2+3 juntos** porque son la **misma** invocación (el rechazo y su no-efecto).

**Convención cumplida:** caja negra sobre el CLI real como **subproceso**; proyecto **descartable** con el **HOME del subproceso en un tempdir vacío**; fixture **sintético y anónimo**; sin mocks del cableado; helpers del focal T5 reutilizados (dos nuevos: `keyless_spec_entry` —la forma de una aprobación registrada a mano, sin `transition_key`— y `contract_spec_entries`); ninguna aserción sobre porcentajes ni conteos del state vivo.

## (b) Comando exacto y salida real

```
$ python3 -m pytest tests/test_005_012_t5_approval_vigency.py -q --tb=line -rf
.....FFF                                                                 [100%]
:756: AssertionError: PD-14 violada (consecuencia 1 / B3): reaprobar tras la enmienda de los bytes del contrato NO necesita `--supersedes` …; hoy rc=2: "ERROR: state incoherent: feature 'demo-100-transition-fixture' already has a vigente `specification` approval … (transition_key None); registering a second vigente one requires --supersedes <transition-key> …"
:911: AssertionError: PD-14 violada (consecuencia 1): tras la enmienda ninguna entrada vigente NOMBRA los bytes actuales, así que un `gate` posterior del mismo `contract_path` NO necesita `--supersedes` (rc=0); hoy rc=2 … (transition_key '128861ed…f117') …
:967: AssertionError: PD-17 violada (por PD-14/B3): la reaprobación tras la enmienda debe registrarse (rc=0) para poder evaluar la aditividad; hoy rc=2 …
3 failed, 5 passed in 15.08s
```

`.....FFF` = **los 5 tests existentes siguen pasando** y **los 3 nuevos fallan**; los tres son **`AssertionError` de contrato** (rc=2 del CLI en vez del rc=0 enmendado), con el diagnóstico crudo del CLI pegado en el mensaje. Ninguno es `ImportError`/`SyntaxError`/`JSONDecodeError` ni fallo de setup (0 fallas con el prefijo `precondición (…`).

**Regresiones declaradas por el paquete** (motivo concreto: el lector/el registro de la vigencia se tocan):
```
$ python3 -m pytest tests/test_005_001_t1_role_approval.py tests/test_005_001_tcorr.py tests/test_005_005_t1_replace_conserved.py tests/test_packet_prepare.py -q
42 passed in 43.58s
```
La suite completa **no** se corrió (política: la corre quien cierra).

## (c) Commit

```
$ git show --stat --oneline HEAD | tail -3
dc13903 test: 005-012 review-fix B3 RED — vigencia por el pin que nombra los bytes (reaprobacion tras enmienda sin --supersedes; PD-14/D-8, 3 focales rojas por asercion)
 tests/test_005_012_t5_approval_vigency.py | 360 ++++++++++++++++++++++++++++++
 1 file changed, 360 insertions(+)
```
Un solo archivo, +360 y **0 borrados** (los tests previos quedan literales). `M docs/.cdad-state.json` es del orquestador (registro del despacho); no lo commiteé.

## (d) Alcance y no-import de la implementación

- `git diff --name-only HEAD~1` = sólo el focal (dentro del `write_scope` `tests/`).
- El diff **no agrega ninguna importación**; las del archivo siguen siendo stdlib + `pytest` + **módulos de test** existentes. **Ninguna** referencia a `cdad_packet`/`cdad_result` fuera del docstring: los CLIs se invocan **sólo** como subproceso.
- **No se leyó código de implementación.** El caso de defecto se confirmó **corriendo el CLI en negro** (el propio diagnóstico nombra `transition_key None` para la entrada keyless: la evidencia de que esa entrada compite hoy).

## Interpretaciones, límites y ambigüedades declarados

1. **Tensión del encargo resuelta de forma declarada.** Los casos 2 y 3 son, por texto del encargo, comportamientos que **no cambian**: sus aserciones pasan **hoy**. Para no debilitar la disciplina RED, cada test nuevo lleva su **mitad discriminante en el mismo flujo** (declarada en el docstring): en el test 1 el `rc=0` tras la enmienda; en el test 2 la consecuencia 1 aplicada a una entrada vigente **con clave**; en el test 3 el `rc=0` que habilita medir la aditividad. Mismo criterio que declaró el RED anterior de T5.
2. **El caso raro de D-16 no se asertó** (y no se debilitó): reaprobar los **MISMOS** bytes desde una entrada vigente **keyless** no tiene salida por la operación y el contrato lo manda a **deuda D-16 sin marcador declarado**; testearlo exigiría inventar un oráculo. Límite declarado, no hueco silencioso.
3. **Forma del fixture keyless:** `specification` con su pin y **sin** `transition_key` (y sin `supersedes`), en línea con §0.1 y con la forma histórica del fixture base; sin campos inventados ni parseo de prosa.
4. **Alcance del oráculo:** la habilitación del lector en el test 1 está anclada en un test **verde existente** del mismo focal y no inventa oráculo nuevo.
5. **INV-7:** «byte a byte idéntico» sobre el **state**; la mitad «árbol» no se asertó (mismo límite ya declarado).
6. **Nada me bloqueó.** El rojo queda congelado en `dc13903` para que el GREEN implemente el predicado «el pin que nombra los bytes actuales» sin editar los tests.
