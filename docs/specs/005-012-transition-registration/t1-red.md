# Informe RED — 005-012 T1 (`test-writer`, subetapa `red`)

**Paquete:** `005-012-transition-registration-test-writer-red-001` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Tarea:** T1
**Contrato (oráculo):** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) — derivado de la spec, **no** de la implementación.
**Archivo escrito (único):** `tests/test_005_012_t1_register_transition_base.py` (nuevo, 965 líneas).
**Commit:** `878091b` — `test: 005-012 T1 RED — register-transition (delivery/advance, digests derivados, identidad)` (1 archivo, +965; `git diff --stat` acotado al alcance declarado `tests/`).

*Nota de anonimización:* las salidas de pytest de abajo traen rutas absolutas del repo; en este informe se sustituye la raíz del repo por `<repo>`. El archivo de test no contiene rutas absolutas del dueño (la raíz se deriva de `__file__`), ni ids crudos de sesión, ni nombres de otros proyectos: los ids del fixture son inventados (`epic-demo-100-fixture`, `demo-100-transition-fixture`).

## (a) Casos y PD verificado por cada uno

Fixtures (proyecto descartable en tempdir, `HOME` del subproceso en tempdir vacío, sintético y anónimo), construidos **solo por el camino legítimo del CLI**: `prepare` → `prepare --record-dispatch` → `cdad_result.py receive`. Modos: `ready` (paquete `dispatched` + recibo durable real), `dispatched_no_receipt`, `prepared`.

| Test | PD | Verifica |
|---|---|---|
| `test_pd1_prepare_keeps_its_role_and_does_not_register_transitions` | PD-1 / INV-1 | La superficie es el subcomando del CLI (todos los casos lo invocan como subproceso real) y `prepare` conserva su rol: tras una transición registrada, un `prepare` posterior **no agrega entradas** de `stage_history` (no hay segundo escritor) |
| `test_pd2_pd20_delivery_derives_receipt_digest_and_completes_packet` | PD-2 + PD-20 | Forma mínima `delivery` **sin afirmar ningún digest**: rc=0; +1 entrada; `active_packet.status` → `completed`; `receipt_sha256` **derivado** de los bytes actuales, escrito en la entrada **e impreso** en la salida; `validate-state` rc=0 |
| `test_pd3_delivery_without_durable_receipt_fails_closed` | PD-3(a) / INV-7 | Sin recibo durable: rc=2, marcador `evidence missing`, diagnóstico que nombra el paquete y `receipt.json`; state byte a byte idéntico |
| `test_pd3_asserted_receipt_digest_divergent_fails_closed` | PD-3(b) / INV-7 | `--receipt <sha256>` afirmado divergente: rc=2 `evidence missing`, nombra el digest esperado; state byte a byte idéntico |
| `test_pd3_artifact_absent_or_divergent_digest_fails_closed` | PD-3(c) / INV-7 | `--artifact <path>` con ruta ausente y con `=<sha256>` divergente: rc=2 `evidence missing` en cada variante; state byte a byte idéntico |
| `test_pd4_delivery_never_approves` | PD-4 | La entrada de `delivery` **no lleva** `approved_by`/`contract_path`/`contract_sha256`/`plan_path`/`plan_sha256`; el recibo sigue `semantic_status: pending`; control: sin entrada `specification` pinneada, `prepare --role implementer --substage green` sigue bloqueado con `approval pending` (rc≠0) |
| `test_pd7_advance_moves_operational_fields` | PD-7 (+) | `advance` fija `tdd_substage` (verde), deja `current_stage` como estaba (no declarado) y deja **una** entrada nueva con `transition: "advance"` |
| `test_pd7_advance_rejects_out_of_vocabulary_values` | PD-7 (−) | `--current-stage`/`--substage` fuera del vocabulario: rc=2 `state incoherent`, nombra el valor rechazado y los admitidos; state byte a byte idéntico |
| `test_pd10_entry_carries_transition_key_identity` | PD-10 | La entrada lleva `transition_key` (clave nueva y aditiva, forma sha256 de 64 hex) |
| `test_pd11_identical_repetition_is_noop_byte_identical` | PD-11 | Repetición idéntica: rc=0, **sin** segunda entrada, state byte a byte idéntico, y la salida **nombra** la entrada existente (su `transition_key`) |
| `test_pd12_distinct_transition_appends_new_entry` | PD-12 / INV-3 | `transition_key` distinto (otra `--stage`) → entrada nueva; las entradas previas quedan idénticas (append-only); `validate-state` rc=0 |
| `test_pd12_delivery_of_not_dispatched_packet_fails_closed` | PD-12(iii) | Exclusión estructural: `delivery` de un paquete no `dispatched` → rc=2 `state incoherent`, sin efectos |
| `test_pd17_validate_state_green_before_and_after_and_history_additive` | PD-17 | `validate-state` rc=0 **antes y después**; la entrada histórica sin `transition_key` no rompe nada ni es reescrita. **Sin porcentajes ni conteos del state vivo** |
| `test_pd18_delivery_entry_has_no_judgement_fields` | PD-18 | La entrada de `delivery` no lleva `verdict`/`disposition`/`criterion`/`review_path`/`review_sha256` |
| `test_pd20_asserted_receipt_digest_that_matches_is_verified` | PD-20 | Afirmar un digest que **coincide** se verifica y se acepta (rc=0) y queda escrito en la entrada: la aserción opcional no puede rechazar por defecto |

Convenciones cumplidas: caja negra sobre el CLI real como subproceso; **ningún mock** del cableado interno; ningún test de cobertura no derivado de un PD; ningún test que decida el significado de un texto por listas de palabras; cada test cita su PD en el docstring y en el mensaje de aserción.

## (b) Corrida focal: comando exacto y salida real

```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py -q
```

Salida real (tail; `15 failed in 11.85s`):

```
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd1_prepare_keeps_its_role_and_does_not_register_transitions
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd2_pd20_delivery_derives_receipt_digest_and_completes_packet
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd3_delivery_without_durable_receipt_fails_closed
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd3_asserted_receipt_digest_divergent_fails_closed
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd3_artifact_absent_or_divergent_digest_fails_closed
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd4_delivery_never_approves
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd7_advance_moves_operational_fields
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd7_advance_rejects_out_of_vocabulary_values
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd10_entry_carries_transition_key_identity
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd11_identical_repetition_is_noop_byte_identical
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd12_distinct_transition_appends_new_entry
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd12_delivery_of_not_dispatched_packet_fails_closed
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd17_validate_state_green_before_and_after_and_history_additive
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd18_delivery_entry_has_no_judgement_fields
FAILED tests/test_005_012_t1_register_transition_base.py::test_pd20_asserted_receipt_digest_that_matches_is_verified
15 failed in 11.85s
```

**Motivo del fallo, caso por caso** — corrida con traza en una línea (misma sesión, mismo archivo), comando exacto:

```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py -q --tb=line
```
(salidas con la raíz del repo sustituida por `<repo>`)

| Test | Línea | Aserción que falla | Tipo |
|---|---|---|---|
| `test_pd1_…` | `<repo>/tests/test_005_012_t1_register_transition_base.py:438` | `PD-1 violada: register-transition debe ser un subcomando del CLI del repo y aceptar la forma mínima (rc=0); hoy rc=2` | AssertionError (contrato) |
| `test_pd2_pd20_…` | `:481` | `PD-2 violada: delivery … sin afirmar ningún digest debe aceptarse (rc=0); hoy rc=2` | AssertionError |
| `test_pd3_delivery_without_durable_receipt…` | `:540` | `PD-3 violada (a): el rechazo debe llevar el marcador «evidence missing»` | AssertionError |
| `test_pd3_asserted_receipt_digest_divergent…` | `:570` | `PD-3 violada (b): … marcador «evidence missing»` | AssertionError |
| `test_pd3_artifact_absent_or_divergent…` | `:602` | `PD-3 violada (c, ruta ausente): … marcador «evidence missing»` | AssertionError |
| `test_pd4_…` | `:622` | `PD-4 violada: la entrega debe registrarse (rc=0) para evaluar que recibir no aprueba; hoy rc=2` | AssertionError |
| `test_pd7_advance_moves_operational_fields` | `:680` | `PD-7 violada: advance con vocabulario válido debe aceptarse (rc=0); hoy rc=2` | AssertionError |
| `test_pd7_advance_rejects_out_of_vocabulary…` | `:727` | `PD-7 violada (--current-stage fuera del vocabulario): … marcador «state incoherent»` | AssertionError |
| `test_pd10_…` | `:750` | `PD-10 violada: la transición debe registrarse (rc=0) para llevar su clave de identidad; hoy rc=2` | AssertionError |
| `test_pd11_…` | `:774` | `PD-11 violada: la primera invocación debe registrar la transición (rc=0); hoy rc=2` | AssertionError |
| `test_pd12_distinct_transition_appends_new_entry` | `:814` | `PD-12 violada: la primera transición debe registrarse (rc=0); hoy rc=2` | AssertionError |
| `test_pd12_delivery_of_not_dispatched…` | `:864` | `PD-12 violada (iii): … marcador «state incoherent»` | AssertionError |
| `test_pd17_…` | `:894` | `PD-17 violada: la transición debe registrarse (rc=0) para evaluar la aditividad; hoy rc=2` | AssertionError |
| `test_pd18_…` | `:922` | `PD-18 violada: la entrega debe registrarse (rc=0) para evaluar que no escribe juicio; hoy rc=2` | AssertionError |
| `test_pd20_asserted_receipt_digest_that_matches…` | `:951` | `PD-20 violada: un --receipt afirmado que coincide … debe verificarse y aceptarse (rc=0); hoy rc=2` | AssertionError |

Diagnóstico observado del CLI (idéntico en todos los casos, es la salida real del subproceso):

```
ERROR: cdad_packet.py: argument command: invalid choice: 'register-transition'
(choose from validate-state, validate-policy, render, validate-request,
validate-packet, prepare, open-unit, validate-metric, status, validate-unit-contract)
```

**Los 15 son AssertionError** (fallos por aserción de contrato): ningún `ImportError`, `SyntaxError`, `JSONDecodeError`, traceback ni fallo de precondición de fixture (la capa `prepare` → `--record-dispatch` → `receive` y el `validate-state` previo dieron rc=0 en los tres modos: no aparece ningún fallo con el prefijo `precondición (fixture…`).

Declaración honesta de un matiz del RED: en los **tres casos negativos** (PD-3(a)/(b)/(c), PD-7 negativo, PD-12(iii)) la primera aserción es `rc == 2`, y hoy argparse también sale con rc=2, así que esa aserción pasa por coincidencia y el test cae en la **siguiente** aserción (el marcador del contrato). El rojo sigue siendo por aserción de contrato, no por error de uso: el test distingue el rechazo de dominio por el marcador (`evidence missing` / `state incoherent`), no por el rc.

**Evidencia extra (motivo concreto: el módulo nuevo se suma a la suite e importa un módulo de test existente; se verifican las regresiones declaradas por la ficha T1):**

```
$ python3 -m pytest tests/test_005_007_t3_open_unit.py tests/test_005_003_t1_compact_view.py \
    tests/test_005_003_f2_idle_history.py tests/test_packet_prepare.py \
    tests/test_004_002_t2_bootstrap.py -q
56 passed in 36.21s
```

La suite completa **no** se corrió (política del paquete: la corre quien cierra).

## (c) El archivo NO importa el módulo de implementación

Importaciones del archivo (grep real sobre el archivo):

```
101: import hashlib
102: import json
103: import os
104: import re
105: import subprocess
106: import sys
107: from pathlib import Path
109: import pytest
111: from test_004_002_t2_bootstrap import (
112:     prepare_args,
113:     read_state,
114:     write_state,
115: )
```

- **Ninguna** importación de `cdad_packet` ni `cdad_result` (ni por nombre ni por ruta): los CLIs se invocan **solo como subproceso** (`subprocess.run([sys.executable, <CLI>, …])`), tal como exige la spec §4 y la ficha T1.
- El único import no estándar es `test_004_002_t2_bootstrap`, un **módulo de test** ya existente de la suite (patrón declarado en la ficha y usado por `tests/test_005_003_t1_compact_view.py` y `tests/test_005_007_t3_open_unit.py`), del que se reutilizan tres helpers de fixture (`prepare_args`, `read_state`, `write_state`); **no** se importa lógica de producto.
- No se leyó código de implementación. La superficie de `receive` (argv de §2 de 003-002) se derivó de un **test** existente (`tests/test_003_002_t1_receive.py`, dentro del alcance de lectura declarado) y la capa de fixture se validó corriendo el CLI como subproceso sobre un proyecto descartable en tempdir.

## (d) Commit

```
$ git log --oneline -1
878091b test: 005-012 T1 RED — register-transition (delivery/advance, digests derivados, identidad)

$ git show --stat --oneline HEAD | tail -3
878091b test: 005-012 T1 RED — register-transition (delivery/advance, digests derivados, identidad)
 tests/test_005_012_t1_register_transition_base.py | 965 ++++++++++++++++++++++
 1 file changed, 965 insertions(+)
```

Estado del árbol tras el commit: `M docs/.cdad-state.json`. **No es un cambio mío**: es el registro del despacho de este mismo paquete (transición `architect/draft-002 → test-writer/red-001`), hecho por el orquestador; no lo toqué ni lo commiteé. Mi único archivo escrito y commiteado es el test focal.

## Ambigüedades / límites declarados (no inventé oráculo ni debilité tests)

Nada me bloqueó: el contrato fue verificable. Declaro estos puntos de interpretación y límites, con la decisión tomada y su fundamento:

1. **PD-4 / PD-18 — presencia vs. valor nulo.** La spec dice literalmente que la entrada «no lleva» `approved_by`, `contract_*`, `plan_*` (PD-4) y «no lleva» `verdict`/`disposition`/`criterion`/`review_*` (PD-18). Lo aserto como **ausencia de la clave** (`field not in entry`), no como valor falsy. Es la lectura literal; si el GREEN escribiera la clave con `null`, el test lo rechaza —la corrección es del implementador (la entrada tampoco escribe esos campos, INV-9)—. Si el orquestador prefiriera tolerar nulos, es un cambio de contrato, no del test.
2. **INV-7 — mitad «árbol».** Aserto el **state byte a byte idéntico** en todo rechazo (lo que la propia evidencia de AC-4 pide: `sha256` del state antes/después) y **no** aserto el snapshot completo del árbol, porque hoy no es verificable qué artefactos toca el escritor (lock/journal) y una aserción de árbol podría rechazar por una razón ajena al contrato. La mitad «árbol» de INV-7 queda para el gate de aceptación (T8).
3. **PD-1 — «prepare produce bytes idénticos con los mismos insumos».** Verifico la parte observable y falsable del PD-1 en la focal (el subcomando existe y `prepare` **no registra** transiciones tras una transición registrada); la comparación de bytes de `prepare` con/sin la transición requiere un gemelo sintético y puede volverse frágil por razones ajenas a PD-1, así que la dejo al gate de T8/AC-1 (donde la evidencia declarada es «el state es byte a byte el producido por el CLI»).
4. **PD-7 — «nombrando los valores admitidos».** Lo aserto como «aparece al menos un miembro del vocabulario declarado en la salida»; no uso listas de palabras para decidir significado (prohibido por el criterio del dueño).
5. **PD-11 — «salida que nombra la entrada existente».** Lo aserto como «la salida contiene el `transition_key` de la entrada existente» (la clave **es** la identidad de la entrada, PD-10), evitando depender de prosa.
6. **Anonimización del fixture.** Los ids son inventados (`epic-demo-100-fixture`, `demo-100-transition-fixture`) en vez de reutilizar ids de features reales de este repo (que sí usan otros tests de la suite). Verifiqué empíricamente, por sonda en un tempdir y por las precondiciones del fixture (todas rc=0 hoy), que la forma coherente se sostiene con esos ids.
