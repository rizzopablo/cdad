# Informe RED — 005-012 T4 (`test-writer`, subetapa `red`)

**Rol:** test-writer · **Subetapa:** `red` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Paquete:** `005-012-transition-registration-test-writer-red-006` · **Tarea:** T4
**Contrato (oráculo):** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) — **derivado de la spec** (§2.1 superficie, §2.2 forma del registro, §2.3 PD-13/PD-4/PD-20, §2.4 INV-2/INV-3/INV-7/INV-9, §5 D-5), **no de la implementación**.
**Plan:** `docs/specs/005-012-transition-registration/plan.md` §4 ficha T4 + bloque canónico `plan-tasks` (T4) rendido por el paquete.
**Archivo creado (único):** `tests/test_005_012_t4_late_delivery.py` (nuevo, 787 líneas, sha256 `59621c2a…6689b`).
**Commit:** `f8fd4fb` — `test: 005-012 T4 RED — entrega tardia (receive --late + late-delivery, PD-13/PD-4; 7 focales rojas por asercion)` (1 archivo, +787; `git diff --name-only` acotado al alcance `tests/`).

*Nota de anonimización:* la raíz del repo se cita como `<repo>`; el archivo no contiene rutas absolutas del dueño (la raíz se deriva de `__file__` en el runner heredado de T1), ni ids crudos de sesión, ni nombres de otros proyectos: los ids del fixture son inventados (`epic-demo-100-fixture`, `demo-100-transition-fixture`, `ses-demo-0001`).

## (a) Casos y PD que verifica cada test

Superficie ejercida (caja negra, sólo subprocess sobre el CLI del repo): `cdad_result.py receive … [--late]`, `cdad_packet.py register-transition --transition late-delivery --feature <feat> --packet <id>`, `validate-state`, más el camino legítimo previo (`prepare` → `prepare --record-dispatch` → `receive` → `register-transition --transition delivery` → `prepare` → `register-transition --transition closure`).

| Test | PD | Caso del encargo | Verifica |
|---|---|---|---|
| `test_pd13_receive_late_persists_durable_receipt_and_normal_receive_stays_closed` | **PD-13 (1)** + INV-2 | **1** | Feature CERRADA (por el `closure` de T3) + entrega staged en `.cdad/inbox`: `receive --late` → rc=0, **recibo durable** en `.cdad/runtime/results/<exec>/<packet>/receipt.json` con `semantic_status: "pending"` y ligando ejecución/paquete/feature; el `receive` **normal** sobre la misma feature cerrada **sigue fallando cerrado** y **no deja recibo**; el `receive --late` **no escribe el state** (INV-2) |
| `test_pd13_late_delivery_leaves_durable_trace_without_reopening_or_approving` | **PD-13 (2)** + INV-9 + PD-17 | **2** | `late-delivery` → rc=0; la feature **sin cambio de estado** (`epic_features[].status` sigue `done`, `closed_at`/`active_feature` (null)/`current_stage` (idle) sin cambios); **ninguna aprobación nueva** (`approval_effect: false`, sin `approved_by`); **traza durable**: UNA entrada con `stage: "late-delivery"` y `transition: "late-delivery"` que **nombra el paquete**; la única diferencia del state (sha256 antes/después) es el append de la traza + `last_updated`; `validate-state` verde antes y después |
| `test_pd13_late_delivery_with_open_feature_fails_closed_state_incoherent` | **PD-13** (rechazo) + INV-7 | **3(a)** | Feature **ABIERTA** → rc=2, marcador **`state incoherent`**, sin efectos (state byte a byte idéntico) |
| `test_pd13_late_delivery_without_durable_receipt_fails_closed_evidence_missing` | **PD-13** (rechazo) + reparto de marcadores + INV-7 | **3(b)** | Feature **CERRADA sin** recibo durable → rc=2, marcador **`evidence missing`**, nombrando `<packet_id>` y `receipt.json`, sin efectos |
| `test_pd4_late_delivery_entry_has_no_approval_or_judgement_fields_and_prepare_stays_closed` | **PD-4** (re-aplicado) + PD-18 + INV-9 | **4** | La entrada de `late-delivery` **no** lleva `approved_by` ni pin de contrato/plan ni campos de juicio (`verdict`, `disposition`, `criterion`, `review_path`, `review_sha256`); y con la feature cerrada un `prepare --role test-writer` posterior **sigue fallando cerrado** y no publica paquete ni escribe traza |
| `test_pd10_pd11_late_delivery_entry_has_transition_key_and_identical_repetition_is_noop` | **PD-10** + **PD-11** (+ PD-13 cond. 3) | **5** | La entrada lleva `transition_key` (sha256 de la identidad); repetir la invocación **idéntica** → rc=0, **sin segunda entrada**, state **byte a byte idéntico** y salida que **nombra la entrada existente** (`transition_key`) |
| `test_pd17_validate_state_stays_green_across_the_late_delivery` | **PD-17** (+ PD-13, PD-20) | **6** | `validate-state` rc=0 **antes**, tras `receive --late` y tras `late-delivery` (vía de reposo, token `idle`). Sin porcentajes ni conteos del state vivo (el state auditado es el del FIXTURE) |

**Aislamiento de causas (declarado en cada docstring):** tres causas distintas, cada caso armado para que la única posible sea la que quiere probar — (i) el rechazo del `receive` **normal** sobre la feature cerrada (fixture cerrado, único cambio: `--late`); (ii) `late-delivery` con la feature **abierta** (el paquete citado **tiene** recibo durable y pertenece a la ejecución activa → la única causa es la vigencia); (iii) `late-delivery` **sin** recibo (feature cerrada correcta y paquete de su ejecución → la única causa es la evidencia ausente). El fixture tiene **dos paquetes de la misma ejecución**: el primero con recibo y ya entregado (T1), el segundo `prepared` (sin registro de despacho), de modo que el cierre legítimo de T3 queda verde (PD-8(a) sólo exige recibo o disposición a los paquetes **con** registro de despacho) y el paquete de la entrega tardía pertenece a la ejecución cerrada.

**Convenciones cumplidas:** caja negra sobre el CLI real como **subproceso**; proyecto **descartable** en `<tmp>` con el **HOME del subproceso en un tempdir vacío**; fixture **sintético y anónimo**; aserciones sobre `rc`, stdout/stderr, bytes del state y campos estructurales; sin mocks del cableado interno; ningún test de cobertura no derivado de un PD; ninguna lista de palabras que decida el significado de un texto; ninguna aserción sobre porcentajes ni conteos del state **vivo** del repo.

## (b) Corrida focal: comando exacto y salida real

```
$ python3 -m pytest tests/test_005_012_t4_late_delivery.py -q
FFFFFFF                                                                  [100%]
FAILED tests/test_005_012_t4_late_delivery.py::test_pd13_receive_late_persists_durable_receipt_and_normal_receive_stays_closed
FAILED tests/test_005_012_t4_late_delivery.py::test_pd13_late_delivery_leaves_durable_trace_without_reopening_or_approving
FAILED tests/test_005_012_t4_late_delivery.py::test_pd13_late_delivery_with_open_feature_fails_closed_state_incoherent
FAILED tests/test_005_012_t4_late_delivery.py::test_pd13_late_delivery_without_durable_receipt_fails_closed_evidence_missing
FAILED tests/test_005_012_t4_late_delivery.py::test_pd4_late_delivery_entry_has_no_approval_or_judgement_fields_and_prepare_stays_closed
FAILED tests/test_005_012_t4_late_delivery.py::test_pd10_pd11_late_delivery_entry_has_transition_key_and_identical_repetition_is_noop
FAILED tests/test_005_012_t4_late_delivery.py::test_pd17_validate_state_stays_green_across_the_late_delivery
7 failed in 11.09s
```

**Motivo del fallo, caso por caso** — corrida con traza en una línea (misma sesión, post-commit), comando exacto:

```
$ python3 -m pytest tests/test_005_012_t4_late_delivery.py -q --tb=line
```

| Test | Línea | Aserción que falla | Esperado vs visto (hoy) | Tipo |
|---|---|---|---|---|
| `test_pd13_receive_late_…` | `:425` | `PD-13 violada (1): receive --late … debe persistir el recibo durable (rc=0)` | esperado **rc=0 + recibo durable**; hoy **rc=2** `cdad_result.py: error: unrecognized arguments: --late` | AssertionError (contrato) |
| `test_pd13_late_delivery_leaves_durable_trace_…` | `:475` | `PD-13 violada (1): el recibo durable de la entrega tardía debe existir …` | esperado **rc=0**; hoy **rc=2** (`--late` no existe) | AssertionError |
| `test_pd13_late_delivery_with_open_feature_…` | `:590` | `PD-13 violada (3a): el rechazo debe llevar el marcador «state incoherent»` | hoy rc=2 pero por `invalid choice: 'late-delivery' (choose from delivery, advance, gate, closure, disposition)` — **falta el marcador** | AssertionError |
| `test_pd13_late_delivery_without_durable_receipt_…` | `:627` | `PD-13 violada (3b): el rechazo debe llevar el marcador «evidence missing»` | idem: rc=2 por error de uso, **falta el marcador** | AssertionError |
| `test_pd4_late_delivery_entry_…` | `:660` | `PD-13 violada (1): recibo durable de la entrega tardía (rc=0)` | esperado **rc=0**; hoy **rc=2** (`--late` no existe) | AssertionError |
| `test_pd10_pd11_late_delivery_entry_…` | `:717` | `PD-13 violada (1): recibo durable de la entrega tardía (rc=0)` | esperado **rc=0**; hoy **rc=2** (`--late` no existe) | AssertionError |
| `test_pd17_validate_state_stays_green_…` | `:769` | `PD-17 violada: el receive --late debe prosperar sobre el reposo coherente (rc=0)` | esperado **rc=0**; hoy **rc=2** (`--late` no existe) | AssertionError |

**Los 7 son AssertionError de contrato.** Ningún `ImportError`, `SyntaxError`, `JSONDecodeError`, traceback ni fallo de precondición de fixture: **ninguna** falla lleva el prefijo `precondición (fixture…)` — las precondiciones del fixture (`prepare`, `--record-dispatch`, `receive`, `register-transition --transition delivery`, el segundo `prepare`, el `closure` de T3, `validate-state` previos) pasan **todas** con rc=0. En los casos de rechazo, `rc=2` hoy **coincide** con el esperado (error de uso de argparse) y por eso la aserción **discriminante es el marcador**, no el `rc`; en los casos de aceptación el rojo discrimina por `rc` (0 vs 2).

**Evidencia extra, motivo concreto** (el archivo nuevo se suma a `tests/` e importa dos módulos de test existentes y ejercita el área de `receive`; se corren las **regresiones declaradas** por el paquete, sin correr la suite completa):

```
$ python3 -m pytest tests/test_003_002_t1_receive.py tests/test_003_002_t2_materialize.py \
    tests/test_005_007_t4_architect_report_materialization.py -q
.........................                                                [100%]
25 passed in 38.07s
```

La **suite completa no se corrió** (política del paquete: la corre una vez quien cierra).

```
$ git diff --name-only HEAD~1..HEAD -- tests/    # tests/test_005_012_t4_late_delivery.py (único)
$ git status --porcelain                         # M docs/.cdad-state.json  (no es mío: registro del despacho del orquestador)
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
    APPROVER, FEATURE_ID, RECEIPT_NAME, EVIDENCE_MISSING, STATE_INCOHERENT,
    TRANSITION_DIGEST_RE, _Fixture as _BaseFixture, assert_unchanged, entries,
    last_entry, last_entry_with,
)
from test_005_012_t3_closure_dispatch_resolution import (
    CLOSURE_BYTES, CLOSURE_REL, CLOSURE_STAGE, FEATURE_CLOSED, IDLE,
    _feature_entry, assert_validate_green, names_path,
)
```

- **Ninguna** importación de `cdad_packet` ni `cdad_result`: las únicas apariciones de esos nombres están en el **docstring** que declara la superficie de invocación. Los CLIs se invocan **sólo como subproceso** (`subprocess.run([sys.executable, <CLI>, …])`, runner heredado del focal T1).
- Los únicos imports no estándar son módulos **de test** ya existentes (helpers y fixture base de T1; constantes/helpers del cierre de T3) — el patrón declarado por el paquete.
- **No se leyó código de implementación.** La forma del state, del recibo y del descriptor se derivaron de **la spec, el plan, el discovery y los tests** dentro del alcance de lectura, y se validaron **corriendo el CLI como subproceso** sobre proyectos descartables en `<tmp>`.

## (d) Commit

```
$ git log --oneline -1
f8fd4fb test: 005-012 T4 RED — entrega tardia (receive --late + late-delivery, PD-13/PD-4; 7 focales rojas por asercion)

$ git show --stat --oneline HEAD | tail -3
f8fd4fb test: 005-012 T4 RED — entrega tardia (receive --late + late-delivery, PD-13/PD-4; 7 focales rojas por asercion)
 tests/test_005_012_t4_late_delivery.py | 787 +++++++++++++++++++++++++++++++++
 1 file changed, 787 insertions(+)
```

`docs/.cdad-state.json` **no es un cambio mío**: es el registro del despacho de este paquete hecho por el orquestador; no lo toqué ni lo commiteé. Sin `--no-verify`, sin push, sin despliegue, sin tocar HOME, sin leer `tests/.sensitive-patterns.local`.

## Interpretaciones, límites y ambigüedades declarados (no inventé oráculo ni debilité tests)

1. **Nada me bloqueó: no hubo detención.** El contrato de T4 fue verificable de punta a punta; las ambigüedades se resolvieron por lectura literal de la spec + la ficha/superficie rendida por el paquete.
2. **`late-delivery` se invoca SIN `--stage` (ambigüedad real, resuelta por el paquete + PD-13).** §2.1 declara `--stage` «obligatoria salvo `disposition`», pero PD-13 (2) muestra la invocación **sin** `--stage` esperando la etiqueta **canónica** `stage: "late-delivery"` (misma forma que la etiqueta canónica `dispatch-disposition` de PD-21), y la superficie que este paquete manda ejercer **tampoco** la incluye. Se invoca sin `--stage` y se asevera la etiqueta canónica. **Señalado para el orquestador/GREEN:** la lectura que la ficha fija es la canónica (automática).
3. **El paquete de la entrega tardía es un paquete `prepared` de la ejecución cerrada.** PD-13 reemplaza la precondición «el paquete activo está `dispatched`» por «el paquete **pertenece** a su ejecución» (no exige `dispatched`), y el cierre legítimo de T3 (PD-8(a)) sólo exige recibo o disposición a los paquetes **con registro de despacho**: un paquete despachado y sin recibo **bloquearía** el cierre, así que el objetivo de la entrega tardía es el **segundo** paquete publicado de la misma ejecución (`prepared`, sin registro de despacho). El fixture se validó empíricamente: el `closure` de T3 da rc=0 y deja `done`/`idle`/`validate-state VALID`.
4. **Cadena entre los tests (inherente a PD-13).** Los tests 2/4/5/6 requieren primero el recibo durable, que es el resultado de PD-13 (1): hoy fallan en esa aserción de contrato (no en una precondición de fixture); una vez que GREEN implemente `receive --late`, esas mismas corridas alcanzan su aserción propia (traza, no-aprobación, `transition_key`/no-op). La secuencia es la que PD-13 declara (recibo → traza).
5. **El negativo «feature abierta»** usa el fixture base `ready` (feature abierta, paquete `dispatched` **con** recibo durable y de la ejecución activa): así la única causa del rechazo es la vigencia, no la evidencia.
6. **Marcadores de los rechazos.** Sólo se asertan los marcadores que el contrato declara para estas causas: `state incoherent` (feature abierta) y `evidence missing` (sin recibo). El reparto es por condición (§2.3, PD-12).
7. **Mitad «árbol» de INV-7:** como declararon los RED de T1/T2/T3/T5, se asevera el **state byte a byte idéntico**; el snapshot completo del árbol no se asevera.
8. **Sin cifras del state vivo.** PD-17 se verifica con `validate-state` rc=0 **antes y después sobre el fixture**; ninguna aserción sobre porcentajes ni conteos del state del repo.
9. **Dos mitades ya verdes hoy, declaradas.** El `receive` **normal** rechazado sobre la feature cerrada y el `prepare` posterior a la entrega tardía ya se satisfacen con el comportamiento de hoy; la mitad **discriminante** de esos tests es `receive --late` rc=0 con recibo `pending` y la propia entrada de `late-delivery`.

Sin bloqueos. El rojo queda congelado en `f8fd4fb` para que el GREEN implemente el modo `receive --late` (máquina de recibos reusada, sólo la precondición de vigencia invertida) y la clase `late-delivery` (traza durable, sin reabrir ni aprobar) **sin editar los tests**.
