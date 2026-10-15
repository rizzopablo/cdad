# Informe RED — 005-012 T5 (`test-writer`, subetapa `red`)

**Rol:** test-writer · **Subetapa:** `red` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Paquete:** `005-012-transition-registration-test-writer-red-003` · **Tarea:** T5
**Contrato (oráculo):** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) — **derivado de la spec, no de la implementación**. PD cubiertas: **PD-14, PD-15** (+ PD-10/PD-11 y PD-17 como postcondiciones soporte declaradas por el encargo).
**Plan:** `docs/specs/005-012-transition-registration/plan.md` §4 ficha T5 + bloque canónico `plan-tasks` (rendido por el paquete).
**Archivo creado (único):** `tests/test_005_012_t5_approval_vigency.py` (nuevo, 631 líneas, sha256 `514d19d1…5ea79`).
**Commit:** `9669c0a` — `test: 005-012 T5 RED — vigencia estructural de la aprobacion (supersedes + lector aditivo; PD-14/PD-15, 5 focales rojas por asercion)` (1 archivo, +631; `git diff` acotado al alcance `tests/`).

*Nota de anonimización:* la raíz del repo se cita como `<repo>`; el archivo de test no contiene rutas absolutas del dueño (la raíz se deriva de `__file__`), ni ids crudos de sesión, ni nombres de otros proyectos: los ids del fixture son inventados (`epic-demo-100-fixture`, `demo-100-transition-fixture`).

## (a) Casos y PD que verifica cada test

Superficie ejercida (caja negra, solo subprocess): el **lector** es el que usa el propio CLI para autorizar a los roles de construcción (`_approved_spec_entries`/`_contract_approval_for`), observable por su efecto — `prepare --role test-writer --substage red` que se **habilita** (rc=0) o se **bloquea** con `approval pending` (rc=2) — más el registro `register-transition … --transition gate --stage specification … [--supersedes <key>]` y `validate-state`.

| Test | PD | Caso del encargo | Verifica |
|---|---|---|---|
| `test_pd14_second_vigente_without_supersedes_fails_closed` | PD-14 (registro) + INV-7 | **1** | Con un `(feature, contract_path)` que ya tiene entrada vigente, un segundo `gate --stage specification` para el **mismo** `contract_path` **sin** `--supersedes` → rc=2, marcador `state incoherent`, nombrando la entrada vigente y el campo `supersedes`; **sin efectos** (state byte a byte idéntico) |
| `test_pd14_supersedes_replaces_the_vigent_entry_for_the_reader` | PD-14 (registro + lector) | **2 + 3** | Con `--supersedes <key>` que nombra una entrada existente de la misma feature y el mismo `contract_path` → rc=0; la entrada nueva lleva `transition_key` y el campo `supersedes`, el par queda con **dos** entradas sin reescribir ninguna; y el lector **solo** habilita por la nueva: con el contrato de la **sustituida** → rc=2 `approval pending` (sin efectos), con el **vigente** → rc=0 |
| `test_pd15_prose_note_is_not_the_control_and_the_structural_field_is` | PD-15 | **4** | Control negativo con **dos lados**: dos entradas con el pin correcto y una **nota en prosa** «reemplaza a la anterior» **sin** `supersedes` → **ambas siguen habilitando** (rc=0 con cada juego de bytes: la prosa no cambia nada); con el **campo estructural** `supersedes` → solo la nueva habilita (la reemplazada bloquea, rc=2, y la nueva habilita, rc=0) |
| `test_pd17_operation_keeps_validate_state_green_and_history_append_only` | PD-17 + INV-3 | **5** | `validate-state` rc=0 **antes y después**; las entradas históricas **sin** `supersedes` **no** se invalidan ni se reescriben (append-only: state byte-idéntico tras el rechazo, entradas previas intactas, no ganan el campo nuevo) y la entrada histórica **sigue habilitando**. Sin porcentajes ni conteos del state vivo del repo |
| `test_pd10_pd11_gate_with_supersedes_carries_key_and_repeat_is_noop` | PD-10/PD-11 + PD-14 (el no-op no deshace el reemplazo) | **6** | La entrada del `gate` con `--supersedes` lleva `transition_key` y `supersedes`; repetir la invocación **idéntica** es **no-op** (rc=0, sin segunda entrada, state byte a byte idéntico, salida que nombra la entrada existente); el no-op no tiene efectos sobre la vigencia (la entrada reemplazada sigue sin habilitar) |

Los 6 casos mínimos del encargo quedan cubiertos (los casos 2 y 3 son las dos mitades de un mismo flujo: `--supersedes` → lector; se implementan como un test para que la mitad discriminante sea observable en una sola corrida, como declara el docstring).

**Convenciones cumplidas:** caja negra sobre el CLI real como **subproceso** (nunca se importa ni se lee la implementación); proyecto **descartable** en `<tmp>` con el **`HOME` del subproceso en un tempdir vacío** (verificado: `ls -A` del HOME del subproceso queda vacío); fixture **sintético y anónimo**; aserciones sobre `rc`, stdout/stderr y **bytes del state**; sin mocks del cableado interno; sin tests de cobertura no derivados de un PD; nada de listas de palabras que decidan el significado de un texto (la prosa de PD-15 es **dato del fixture**, y el test solo comprueba que no cambia qué entrada habilita). Cada test cita su PD en docstring y en el mensaje de aserción. Ninguna aserción sobre porcentajes ni conteos del state vivo.

## (b) Corrida focal: comando exacto y salida real

```
$ python3 -m pytest tests/test_005_012_t5_approval_vigency.py -q
```

Salida real (`5 failed in 10.23s`):

```
FAILED tests/test_005_012_t5_approval_vigency.py::test_pd14_second_vigente_without_supersedes_fails_closed
FAILED tests/test_005_012_t5_approval_vigency.py::test_pd14_supersedes_replaces_the_vigent_entry_for_the_reader
FAILED tests/test_005_012_t5_approval_vigency.py::test_pd15_prose_note_is_not_the_control_and_the_structural_field_is
FAILED tests/test_005_012_t5_approval_vigency.py::test_pd17_operation_keeps_validate_state_green_and_history_append_only
FAILED tests/test_005_012_t5_approval_vigency.py::test_pd10_pd11_gate_with_supersedes_carries_key_and_repeat_is_noop
5 failed in 10.23s
```

**Motivo del fallo, caso por caso** — corrida con traza en una línea (misma sesión, mismo archivo), comando exacto:

```
$ python3 -m pytest tests/test_005_012_t5_approval_vigency.py -q --tb=line
```

| Test | Línea | Aserción que falla | Esperado vs visto (hoy) | Tipo |
|---|---|---|---|---|
| `test_pd14_second_vigente_without_supersedes_fails_closed` | `:303` | `PD-14 violada: registrar un segundo gate … SIN --supersedes debe fallar cerrado (rc=2)` | esperado **rc=2** + `state incoherent`; hoy **rc=0** — el CLI registra la segunda vigente (`registered transition gate stage 'specification' … transition_key: b7e3922b…`, `stage_history: 3 entries (+1)`) | AssertionError (contrato) |
| `test_pd14_supersedes_replaces_the_vigent_entry_for_the_reader` | `:387` | `PD-14 violada (lector): presentando el contrato de la aprobación SUSTITUIDA el rol de construcción ya NO se habilita (rc=2)` | esperado **rc=2** `approval pending`; hoy **rc=0** — la entrada reemplazada (pin todavía coincidente) sigue habilitando | AssertionError |
| `test_pd15_prose_note_is_not_the_control_and_the_structural_field_is` | `:462` | `PD-15 violada (el campo SÍ es el control): con supersedes la entrada nombrada deja de habilitar … (rc=2)` | esperado **rc=2** `approval pending`; hoy **rc=0** — el campo `supersedes` no cambia qué entrada habilita (la prosa y el campo se comportan igual) | AssertionError |
| `test_pd17_operation_keeps_validate_state_green_and_history_append_only` | `:520` | `PD-17 violada (por PD-14): la segunda vigente sin --supersedes debe rechazarse (rc=2) sin tocar la historia` | esperado **rc=2** y state byte-idéntico; hoy **rc=0** (`stage_history: 4 entries (+1)`) | AssertionError |
| `test_pd10_pd11_gate_with_supersedes_carries_key_and_repeat_is_noop` | `:621` | `PD-11/PD-14 violadas: la repetición idéntica no debe tener efectos sobre la vigencia: el contrato de la entrada reemplazada sigue sin habilitar (rc=2)` | esperado **rc=2** `approval pending`; hoy **rc=0** | AssertionError |

**Los 5 son AssertionError de contrato.** Ningún `ImportError`, `SyntaxError`, `JSONDecodeError`, traceback ni fallo de precondición de fixture: no aparece ninguna falla con el prefijo `precondición (fixture…)`; las precondiciones (`prepare` del fixture, `--record-dispatch`, `receive`, primer `gate`, `delivery`, `validate-state` previos) pasan hoy con rc=0. El rojo del registro (`:303`, `:520`) discrimina por `rc` (2 vs 0), no por error de uso: hoy `--supersedes` es un argumento aceptado y el registro sin el campo simplemente se hace.

**Evidencia extra (motivo concreto: el archivo nuevo se suma a la suite e importa dos módulos de test existentes; se corren las regresiones declaradas por el paquete, sin correr la suite completa):**

```
$ python3 -m pytest tests/test_005_001_t1_role_approval.py tests/test_005_001_tcorr.py \
    tests/test_005_005_t1_replace_conserved.py tests/test_packet_prepare.py -q
42 passed in 70.61s (0:01:10)
```

La **suite completa no se corrió** (política del paquete: la corre una vez quien cierra).

```
$ git diff --name-only HEAD -- tests/          # vacío
$ git status --porcelain -- tests/             # vacío
```

## (c) El archivo NO importa la implementación

Importaciones reales del archivo (únicas líneas `import`/`from`):

```
import hashlib
import subprocess
from pathlib import Path
import pytest
from test_004_002_t2_bootstrap import prepare_args
from test_005_012_t1_register_transition_base import (
    APPROVER, CONTRACT_BYTES, CONTRACT_FILE, FEATURE_ID, STATE_INCOHERENT,
    APPROVAL_PENDING, TRANSITION_DIGEST_RE, _Fixture as _BaseFixture,
    assert_unchanged, entries, last_entry_with,
)
```

- **Ninguna** importación de `cdad_packet` ni `cdad_result`: las únicas apariciones de esos nombres están en el **docstring** que declara la superficie de invocación. Los CLIs se invocan **solo como subproceso** (`subprocess.run([sys.executable, <CLI>, …])`, runner heredado del focal T1), como exigen la spec §4 y la ficha T5.
- Los únicos imports no estándar son módulos **de test** ya existentes (helpers del focal T1: runner de subproceso, proyecto descartable, observación, `assert_unchanged`; `prepare_args` del fixture de 004-002) — el patrón declarado por el paquete. Se reutiliza además el **patrón** del focal T2 (subclase de fixture + helper `gate`), sin importar lógica de producto.
- **No se leyó código de implementación.** La forma del state, la de la delegación y la base de resolución relativa de `--contract-path` se derivaron de **tests** dentro del alcance de lectura y se validaron **corriendo el CLI como subproceso** en proyectos descartables (sondas desechables fuera del repo, en `<tmp>`, borradas; jamás dentro del árbol de tests).

## (d) Commit

```
$ git log --oneline -1
9669c0a test: 005-012 T5 RED — vigencia estructural de la aprobacion (supersedes + lector aditivo; PD-14/PD-15, 5 focales rojas por asercion)

$ git show --stat --oneline HEAD | tail -3
9669c0a test: 005-012 T5 RED — vigencia estructural de la aprobacion (supersedes + lector aditivo; PD-14/PD-15, 5 focales rojas por asercion)
 tests/test_005_012_t5_approval_vigency.py | 631 ++++++++++++++++++++++++++++++
 1 file changed, 631 insertions(+)
```

`docs/.cdad-state.json` **no es un cambio mío**: es el registro del despacho de este paquete hecho por el orquestador; no lo toqué ni lo commiteé (mi commit tiene un solo archivo). Sin `--no-verify`, sin push, sin despliegue, sin tocar HOME, sin leer `tests/.sensitive-patterns.local`.

## Interpretaciones, límites y ambigüedades declarados (no inventé oráculo ni debilité tests)

1. **La segunda vigente tiene que ser una transición DISTINTA.** PD-10 fija los campos de `transition_key` (`execution_id, feature_id, transition, stage, substage, packet_id, receipt_sha256, resolution`) y `supersedes` **no** está entre ellos; PD-11 hace que una invocación idéntica sea no-op. Por eso, para que exista una **segunda entrada** vigente del mismo par, la invocación difiere en un campo de la clave (`--substage`). Si el segundo registro fuera idéntico, PD-11 (no-op, rc=0) y PD-14 (rc=2) se contradirían; interpreté PD-14 sobre la transición **distinta** (la lectura que no hace pelear dos postcondiciones). Queda **declarado** en el docstring del archivo.
2. **Cómo se observa «la sustituida deja de habilitar».** El par comparte el `contract_path`; lo que cambia entre dos aprobaciones es el **contenido** del archivo (el caso real de esta misma feature: el contrato se corrige y se re-aprueba). El test presenta primero los bytes de la aprobación **sustituida** (hoy habilitan porque su pin coincide → rc=0) y después los de la **vigente** (rc=0). La comparación es controlada: mismo fixture, mismas entradas, solo cambian los bytes del contrato.
3. **El control negativo de PD-15 se arma sobre el state del fixture** (dos entradas con el pin correcto + nota en prosa), porque registrar una segunda vigente sin `--supersedes` es justamente lo que PD-14 rechaza. La nota es **dato**; el test no decide su significado (§3, frontera del juicio): solo comprueba que no altera qué entrada habilita.
4. **Dos mitades ya verdes hoy, declaradas.** En el test de PD-17 y en el de PD-10/PD-11 hay aserciones que el comportamiento **de hoy** ya satisface (el oráculo de PD-17 es por contrato `validate-state` rc=0 antes y después, y el no-op de PD-11 para el `gate` con `--supersedes` sale de la forma aditiva de T1). Para respetar la disciplina RED («cada test corre y falla por aserción»), cada uno de esos tests lleva su **mitad discriminante en el mismo flujo**: la de PD-17 es el rechazo de la segunda vigente con el state byte-idéntico; la de PD-10/PD-11 es la vigencia — el no-op no deshace el reemplazo. Ambas están declaradas en los docstrings.
5. **No cubierto, declarado (sin oráculo inventado):** (i) un `--supersedes` que **no** nombre una entrada existente: la spec declara el caso válido (rc=0) pero **no** el marcador del inválido, así que no lo aserté; (ii) nombrar una entrada histórica **sin** `transition_key` (no hay clave que citar) y el efecto de PD-14 sobre una vigente *keyless* — el focal usa una primera aprobación **registrada por el CLI** (con clave), que es la forma real del escenario «segunda vigente»; (iii) la mitad «árbol» de INV-7 (solo aserto el state byte a byte), mismo límite que declararon los RED de T1/T2.
6. **Sin cifras del state vivo.** PD-17 se verifica con `validate-state` rc=0 antes/después y comparaciones del fixture consigo mismo; ningún porcentaje ni conteo del repo. El test del lector corre **a lo sumo una invocación habilitante** por fixture (una `--transition delivery` legítima deja el paquete terminal), para no confundir el bloqueo por vigencia con el bloqueo por paquete activo — la otra causa de rc≠0 del `prepare` (declarado en el docstring).

Nada me bloqueó: el contrato fue verificable. El rojo está congelado en `9669c0a` para que el GREEN implemente `supersedes` + el lector aditivo **sin editar los tests**.
