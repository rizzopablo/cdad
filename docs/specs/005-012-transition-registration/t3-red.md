# Informe RED — 005-012 T3 (`test-writer`, subetapa `red`)

**Rol:** test-writer · **Subetapa:** `red` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Paquete:** `005-012-transition-registration-test-writer-red-004` · **Tarea:** T3
**Contrato (oráculo):** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) — **derivado de la spec, no de la implementación**. PD cubiertas: **PD-8, PD-9, PD-21** (+ PD-12(iv), PD-11, PD-17, PD-20 como soporte declarado por el encargo).
**Plan:** `docs/specs/005-012-transition-registration/plan.md` §4 ficha T3 + bloque canónico `plan-tasks` (rendido por el paquete).
**Archivo creado (único):** `tests/test_005_012_t3_closure_dispatch_resolution.py` (nuevo, 1004 líneas, sha256 `26e69366…5de06`).
**Commit:** `99b65e6` — `test: 005-012 T3 RED — closure (comprobacion antes de aplicar) y disposition (despacho sin recibo, B1; PD-8/PD-9/PD-21, 8 focales rojas por asercion)` (1 archivo, +1004; `git diff --name-only` acotado al alcance `tests/`).

*Nota de anonimización:* la raíz del repo se cita como `<repo>`; el archivo no contiene rutas absolutas del dueño (la raíz se deriva de `__file__` en el runner heredado), ni ids crudos de sesión, ni nombres de otros proyectos: los ids del fixture son inventados (`epic-demo-100-fixture`, `demo-100-transition-fixture`, `ses-demo-0002`).

## (a) Casos y PD que verifica cada test

Superficie ejercida (caja negra, solo subprocess sobre el CLI del repo): `register-transition --transition closure …` y `register-transition --transition disposition --packet <id> --resolution <abandoned|superseded> [--replaced-by <packet-id>]`, más `validate-state` y el camino legítimo de la capa previa (`prepare` → `prepare --record-dispatch` → `cdad_result.py receive` → `register-transition --transition delivery`).

| Test | PD | Caso del encargo | Verifica |
|---|---|---|---|
| `test_pd8a_closure_with_unreceipted_dispatch_fails_closed_naming_evidence` | PD-8(a) + INV-7 | **1** | Paquete de la ejecución activa con registro de despacho y **sin recibo durable** → `closure` rc=2, marcador `evidence missing`, nombrando el `<packet_id>` y `receipt.json`, y **ofreciendo las dos salidas legítimas** (`receive` / `disposition`; `late-delivery` **ya no se ofrece**, B1); state **byte a byte idéntico** (PD-8 comprueba antes de escribir) |
| `test_pd8b_closure_without_vigent_specification_pin_fails_closed` | PD-8(b) + INV-7 | **2** (dos variantes) | **(a)** sin ninguna entrada `specification` de la feature; **(b)** con la entrada cuyo pin **ya no nombra** el contrato (digest divergente de los bytes actuales) → rc=2, marcador `approval pending`, nombrando la aprobación faltante, sin efectos |
| `test_pd9_closure_applied_records_evidence_and_rests` | PD-9 + PD-20 + PD-17 | **3** | Con las dos comprobaciones verdes → rc=0; entrada de traza (`transition: "closure"`, `stage: "feature-closure"`, `closure_path` y `closure_sha256` **derivado** de los bytes, impreso); `epic_features[<feat>].status: "done"` + `closed_at` + `closure_evidence{path, sha256}`; `active_feature: null`; `current_stage: "idle"`; `active_packet` null o terminal; historia previa intacta (append-only); `validate-state` rc=0 antes y después (token `idle`) |
| `test_pd21_disposition_of_unreceipted_dispatch_is_structural_and_does_not_touch_the_rest` | PD-21 (cond. 1) + INV-9 + PD-10 + PD-17 | **4(a)** | Feature **abierta** + despacho **sin recibo** → `disposition --resolution abandoned` rc=0; UNA entrada con `transition: "disposition"`, `stage: "dispatch-disposition"`, `resolution`, `approval_effect: false`, `transition_key` (sha256) y **sin** `approved_by`; **ningún otro campo del state cambia** salvo `stage_history` y `last_updated`; el paquete sigue `dispatched` (no se fabrica un `completed`); `validate-state` rc=0 antes y después |
| `test_pd21_b1_closure_rejects_then_the_disposition_unblocks_and_the_closure_advances` | PD-21 (cond. 2) + PD-8(a) + PD-9 + PD-17 | **4(b)** (el caso que la review del orquestador exigió) | Cierre rechaza nombrando el despacho sin recibo → se registra la disposición → **el cierre AVANZA** (rc=0), estado de reposo coherente (`validate-state` rc=0, `active_feature: null`, `current_stage: "idle"`, feature `done`) |
| `test_pd21_superseded_disposition_records_replaced_by` | PD-21 (cond. 1, `superseded`) + PD-12 | **4(c)** | `--resolution superseded --replaced-by <packet-id>` → rc=0 y la entrada lleva `resolution`/`replaced_by` (paquete REAL de la misma ejecución), `approval_effect: false`, sin `approved_by`; el negativo (sin `--replaced-by`) → rc=2, **sin efectos** y sin ser error de uso del CLI |
| `test_pd21_disposition_rejections_fail_closed_state_incoherent` | PD-21 + PD-12(iv) | **5** | Cuatro variantes → rc=2, marcador `state incoherent`, nombrando el hecho, sin efectos: **(i)** paquete ajeno a la ejecución activa; **(ii)** paquete no `dispatched`; **(iii)** paquete que **ya tiene recibo durable** (la guarda que impide saltar una entrega que existe); **(iv)** feature **cerrada** |
| `test_pd11_pd21_identical_disposition_is_noop_and_another_resolution_appends` | PD-11 + PD-21 (cond. 3) + PD-12 | **6** | Repetición idéntica → rc=0, sin segunda entrada, state **byte a byte idéntico** y salida que nombra la entrada existente (`transition_key`); resolución **distinta** (`abandoned` → `superseded`) → entrada **nueva** (append), sin reescribir la anterior |

Los 7 casos mínimos del encargo quedan cubiertos (el caso 4 se reparte en tres tests: (a), (b) y (c); PD-8(a) se cubre dos veces, con un despacho sin recibo **y** con el flujo B1 completo).

**Aislamiento de causas (declarado en cada docstring):** el cierre exige (a) que cada paquete despachado de la ejecución activa tenga recibo **o** disposición y (b) una aprobación `specification` vigente cuyo pin nombre el contrato. El fixture **`double`** tiene dos paquetes de la misma ejecución —el primero **con** recibo (y entregado por T1) y el segundo **sin** recibo— de modo que la única entrega sin resolver es la segunda; el fixture **`ready`** tiene todas las entregas satisfechas (el único paquete tiene recibo), así que PD-8(b) es la única causa posible del rechazo; el fixture **`single`** es el caso B1 mínimo, y cada variante del caso 5 incumple **una** condición de la disposición.

**Convenciones cumplidas:** caja negra sobre el CLI real como **subproceso** (nunca se importa ni se lee la implementación); proyecto **descartable** en `<tmp>` con el **`HOME` del subproceso en un tempdir vacío** (heredado del runner del focal T1: `env["HOME"] = <tempdir>/home`); fixture **sintético y anónimo**; aserciones sobre `rc`, stdout/stderr y los **bytes del state**; sin mocks del cableado interno; sin tests de cobertura no derivados de un PD; ninguna lista de palabras que decida el significado de un texto (las salidas legítimas que el rechazo debe **ofrecer** se reconocen por los nombres de operación del contrato —`receive`/`disposition`—, no por prosa); ninguna aserción sobre porcentajes ni conteos del state **vivo** del repo (PD-17 se verifica con `validate-state` rc=0 antes y después **sobre el fixture**).

## (b) Corrida focal: comando exacto y salida real

```
$ python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py -q
FFFFFFFF                                                                 [100%]
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd8a_closure_with_unreceipted_dispatch_fails_closed_naming_evidence
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd8b_closure_without_vigent_specification_pin_fails_closed
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd9_closure_applied_records_evidence_and_rests
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd21_disposition_of_unreceipted_dispatch_is_structural_and_does_not_touch_the_rest
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd21_b1_closure_rejects_then_the_disposition_unblocks_and_the_closure_advances
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd21_superseded_disposition_records_replaced_by
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd21_disposition_rejections_fail_closed_state_incoherent
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd11_pd21_identical_disposition_is_noop_and_another_resolution_appends
8 failed in 11.12s
```

**Motivo del fallo, caso por caso** — corrida con traza en una línea (misma sesión, mismo archivo, post-commit), comando exacto:

```
$ python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py -q --tb=line
```

| Test | Línea | Aserción que falla | Esperado vs visto (hoy) | Tipo |
|---|---|---|---|---|
| `test_pd8a_…_fails_closed_naming_evidence` | `:431` | `PD-8(a) violada: el rechazo debe llevar el marcador «evidence missing»` | esperado rc=2 **+ `evidence missing`** + nombre del paquete + las dos salidas; hoy rc=2 con `argument --transition: invalid choice: 'closure' (choose from delivery, advance, gate)` (la clase no existe) | AssertionError (contrato) |
| `test_pd8b_…_without_vigent_specification_pin…` | `:519` | `PD-8(b) violada (sin entrada 'specification'): el rechazo debe llevar el marcador «approval pending»` | esperado rc=2 **+ `approval pending`**; hoy rc=2 por error de uso de `--transition` | AssertionError |
| `test_pd9_closure_applied_records_evidence_and_rests` | `:565` | `PD-9 violada: con las dos comprobaciones verdes el cierre debe aplicarse (rc=0)` | esperado **rc=0** + efecto completo; hoy **rc=2** (`invalid choice: 'closure'`) | AssertionError |
| `test_pd21_disposition_…_does_not_touch_the_rest` | `:668` | `PD-21 violada: la disposición … debe registrarse (rc=0)` | esperado **rc=0** + entrada estructural; hoy **rc=2** (`invalid choice: 'disposition'`) | AssertionError |
| `test_pd21_b1_closure_rejects_then_the_disposition_unblocks…` | `:751` | `PD-8(a) violada (B1): el rechazo debe llevar el marcador «evidence missing»` | esperado rc=2 **+ marcador** (el flujo B1 arranca por el rechazo del cierre); hoy rc=2 por error de uso | AssertionError |
| `test_pd21_superseded_disposition_records_replaced_by` | `:816` | `PD-21 violada (superseded): la disposición 'superseded' con '--replaced-by' debe registrarse (rc=0)` | esperado **rc=0** + `resolution`/`replaced_by`; hoy **rc=2** (`invalid choice: 'disposition'`) | AssertionError |
| `test_pd21_disposition_rejections_fail_closed_state_incoherent` | `:923` | `PD-21 violada (paquete ajeno a la ejecución activa): el rechazo debe llevar el marcador «state incoherent»` | esperado rc=2 **+ `state incoherent`**; hoy rc=2 por error de uso | AssertionError |
| `test_pd11_pd21_identical_disposition_is_noop_and_another_resolution_appends` | `:955` | `PD-11 violada: la primera disposición debe registrar la transición (rc=0)` | esperado **rc=0** + no-op byte-idéntico; hoy **rc=2** | AssertionError |

**Los 8 son AssertionError de contrato.** Ningún `ImportError`, `SyntaxError`, `JSONDecodeError`, traceback ni fallo de precondición de fixture: ninguna falla lleva el prefijo `precondición (fixture…)` — las precondiciones (`prepare`, `prepare --record-dispatch`, `receive`, `register-transition --transition delivery`, `validate-state` previos) pasan **todas** con rc=0, incluido el fixture `double`, que publica un **segundo** paquete en la misma ejecución y lo despacha. En los casos de rechazo, `rc=2` hoy **coincide** con el esperado (error de uso de argparse) y por eso la aserción **discriminante es el marcador** y el nombre del hecho, no el `rc`; en los casos de aceptación el rojo discrimina por `rc` (0 vs 2).

**Evidencia extra, motivo concreto** (el archivo nuevo se suma a `tests/` e importa dos módulos de test existentes; se corren las **regresiones declaradas** por el paquete, sin correr la suite completa):

```
$ python3 -m pytest tests/test_005_001_t3_idle.py tests/test_005_003_f2_idle_history.py \
    tests/test_005_007_t3_open_unit.py tests/test_003_002_t1_receive.py -q
....................                                                     [100%]
20 passed in 28.29s
```

La **suite completa no se corrió** (política del paquete: la corre una vez quien cierra).

```
$ git diff --name-only HEAD~1..HEAD -- tests/      # tests/test_005_012_t3_closure_dispatch_resolution.py (único)
$ git status --porcelain                           # M docs/.cdad-state.json  (no es mío: registro del despacho del orquestador)
```

## (c) El archivo NO importa la implementación

Importaciones reales (todas las líneas `import`/`from` del archivo):

```
from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path
import pytest
from test_004_002_t2_bootstrap import prepare_args
from test_005_012_t1_register_transition_base import (
    APPROVER, CONTRACT_BYTES, CONTRACT_FILE, EVIDENCE_MISSING, FEATURE_ID,
    RECEIPT_NAME, STATE_INCOHERENT, APPROVAL_PENDING, TRANSITION_DIGEST_RE,
    _Fixture as _BaseFixture, assert_unchanged, entries, last_entry,
    last_entry_with,
)
```

- **Ninguna** importación de `cdad_packet` ni `cdad_result`: las únicas apariciones de esos nombres están en el **docstring** que declara la superficie de invocación. Los CLIs se invocan **solo como subproceso** (`subprocess.run([sys.executable, <CLI>, …])`, runner heredado del focal T1).
- Los únicos imports no estándar son módulos **de test** ya existentes (helpers de T1: runner de subproceso, fixture base, observación, `assert_unchanged`; `prepare_args` del fixture de 004-002) — el patrón declarado por el paquete. Se reutiliza además el **patrón** de T2 (subclase de fixture con helpers de invocación) y el de T5 (mutaciones declaradas de `stage_history`), sin importar lógica de producto.
- **No se leyó código de implementación.** La forma del state, la de los paquetes/recibos y la resolución relativa de `--contract-path`/`--closure-path` se derivaron de **la spec, del plan, del discovery y de los tests** dentro del alcance de lectura, y se validaron **corriendo el CLI como subproceso** sobre proyectos descartables en `<tmp>` (fixtures del propio test; nada se escribió fuera de `tests/`).

## (d) Commit

```
$ git log --oneline -1
99b65e6 test: 005-012 T3 RED — closure (comprobacion antes de aplicar) y disposition (despacho sin recibo, B1; PD-8/PD-9/PD-21, 8 focales rojas por asercion)

$ git show --stat --oneline HEAD | tail -3
99b65e6 test: 005-012 T3 RED — closure (comprobacion antes de aplicar) y disposition (despacho sin recibo, B1; PD-8/PD-9/PD-21, 8 focales rojas por asercion)
 .../test_005_012_t3_closure_dispatch_resolution.py | 1004 ++++++++++++++++++++
 1 file changed, 1004 insertions(+)
```

`docs/.cdad-state.json` **no es un cambio mío**: es el registro del despacho de este paquete hecho por el orquestador; no lo toqué ni lo commiteé (mi commit tiene un solo archivo). Sin `--no-verify`, sin push, sin despliegue, sin tocar HOME, sin leer `tests/.sensitive-patterns.local`.

## Interpretaciones, límites y ambigüedades declarados (no inventé oráculo ni debilité tests)

1. **Nada me bloqueó: no hubo detención.** El contrato de T3 fue verificable de punta a punta; las ambigüedades que encontré se resolvieron **por la lectura literal de la spec + el caso mínimo del encargo** y quedan declaradas abajo.
2. **Etiqueta de la clase `closure`.** §2.1 deja `--stage` como token plano libre; el discovery (§4, tabla del ciclo: el script de cierre escribía `stage: "feature-closure"`) fija la etiqueta real, que es la que se usa y se asevera. La disposición **no** lleva `--stage` (la etiqueta canónica `dispatch-disposition` la escribe el CLI, PD-21).
3. **Forma del path guardado.** PD-9 exige que `closure_evidence{path, sha256}` y la traza nombren el cierre citado; el contrato **no** fija si el path se guarda tal como se pasó o resuelto. `names_path()` acepta cualquiera de las dos formas y el oráculo fuerte es el **digest derivado de los bytes** (PD-20).
4. **`active_packet` al cerrar.** PD-9 lo declara `null` **o** terminal; el fixture puede dejarlo `dispatched` (sin `delivery`), así que la aserción acepta `null` o un status terminal (`completed`/`failed`) y no impone cuál.
5. **Marcador del negativo `superseded` sin `--replaced-by`.** PD-21 declara que `--replaced-by` es **obligatorio** para `superseded`, pero **no** declara el marcador de su ausencia (el vocabulario de marcadores de PD-12 es por condición de estado/evidencia, no por argumento faltante). Ese negativo asevera `rc=2`, **sin efectos** (INV-7) y **sin ser un error de uso del CLI** (la clase existe), sin inventar marcador. Declarado.
6. **Ambigüedad real y cómo la resolví: «aprobación reemplazada» en PD-8(b).** El plan (§4 ficha T3) y AC-4 dicen «fixture con la aprobación reemplazada **sin** `supersedes` → rc=2 `approval pending`». Leído literalmente junto con PD-14/PD-15 eso **no se sostiene**: una sustitución **sin** el campo estructural `supersedes` no reemplaza nada — la nota en prosa **no** es un control y **ambas** entradas siguen habilitando (PD-15, que es el dominio del focal de T5). Por eso PD-8(b) lo cubro con las dos formas que el contrato sí hace observables y que el encargo nombra explícitamente: (a) la aprobación **falta** (no hay entrada `specification` de la feature) y (b) su pin **ya no nombra** los bytes actuales del contrato (**digest divergente** — el caso real de la re-aprobación, donde el contrato se corrige). Lo dejo señalado para que el orquestador confirme la lectura; si quería además el caso del `supersedes` estructural, ese comportamiento ya está fijado por el focal de T5 y el cierre lo **consume**, no lo re-declara.
7. **El caso (iv) y el negativo se arman sobre el state del fixture** con mutaciones declaradas por la suite (`epic_features status: "done"`, el vocabulario `CLOSED_FEATURE_STATUSES` que el discovery enumera) y la forma de §2.2; ningún campo inventado.
8. **Dos mitades ya verdes hoy, declaradas.** En `test_pd21_superseded_…` y en `test_pd21_disposition_rejections…` hay aserciones que el comportamiento de hoy (error de uso) ya satisface (`rc=2` + sin efectos): la mitad **discriminante** de esos tests es el registro `rc=0` de la disposición `superseded` y el **marcador** `state incoherent` respectivamente, y ambas están en el mismo flujo. El negativo de `superseded` suma la aserción explícita de que el rechazo **no** es un error de uso del CLI (precedente `_no_usage_error` del focal de `open-unit`), que hoy **falla**.
9. **Sin cifras del state vivo.** PD-17 se verifica con `validate-state` rc=0 **antes y después sobre el fixture**; ninguna aserción sobre porcentajes ni conteos del state del repo.
10. **Mitad «árbol» de INV-7:** como declararon los RED de T1/T2/T5, se asevera el **state byte a byte idéntico**; el snapshot completo del árbol no se asevera (el único artefacto que el CLI toca fuera del state es el rendezvous `.cdad/.lock`, comportamiento existente del lock).

Sin bloqueos. El rojo queda congelado en `99b65e6` para que el GREEN implemente `closure` (comprobación antes de aplicar) y `disposition` (B1) **sin editar los tests**.
