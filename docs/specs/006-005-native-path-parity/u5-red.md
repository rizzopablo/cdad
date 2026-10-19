## Reporte — test-writer, RED de U5 (006-005-native-path-parity)

### 1. Archivos modificados

| Archivo | Tipo | Cambio |
|---|---|---|
| `tests/test_006_005_u5_disposition_failed.py` | **nuevo** (612 líneas) | Focal de PD-19: 6 tests de comportamiento sobre el CLI como subproceso |
| `tests/test_005_012_t3_closure_dispatch_resolution.py` | modificado (+38/−15) | **A-1 declarado**: reformulación de `:745-830` |

Nada fuera de `tests/`. No se leyó código de implementación (`skills/cdad-cycle/scripts/**` no se abrió; el único contacto con la superficie fue ejecutar el CLI como proceso, igual que los tests existentes). No se leyó `tests/.sensitive-patterns.local`. `docs/planning/` y `findings/…` siguen sin trackear y no entraron al commit.

### 2. Mapa test → PD

| Test | Postcondición |
|---|---|
| `test_pd19_a_disposition_marks_only_the_identified_packet_failed` | PD-19 (a): `active_packet.id` intacto y `status: failed`; resto del paquete intacto; sólo `active_packet.status` + entrada nueva de `stage_history` + `last_updated` cambian; entrada con `transition/stage/resolution/approval_effect:false/transition_key`, sin `approved_by`; `validate-state` VALID antes y después |
| `test_pd19_b_identical_disposition_is_a_byte_identical_noop` | PD-19 (b): segunda invocación idéntica → rc=0, sin entrada nueva, estado byte-idéntico |
| `test_pd19_prepare_is_blocked_before_and_unblocked_after` | PD-19 oráculo `prepare`: bloqueado sin escribir antes / rc=0 con paquete nuevo `prepared` después |
| `test_pd19_durable_receipt_rejection_names_receive` | PD-19 cláusula del recibo: rechazo que **nombra `receive`**, sin efectos, sin entrada de disposición |
| `test_pd19_c_late_delivery_stays_registrable_on_the_same_failed_packet` | PD-19 (c): sobre el **mismo** paquete `failed`, cierre legítimo + `receive --late` + `late-delivery` rc=0 con su traza; la feature no reabre |
| `test_pd19_d_failed_is_a_state_mark_and_reconcile_stays_read_only` | PD-19 (d): delta del árbol de la disposición == sólo `docs/.cdad-state.json` (sin recibo/ledger/pid) y `reconcile` rc=0, JSON, estado byte-idéntico |

La condición (d) se cubrió por lo observable, como pedía el encargo: `failed` no lanza ni mata nada (la disposición no escribe más que el estado) y `reconcile` sigue read-only sobre ese paquete. No se inventó oráculo sobre procesos remotos.

### 3. Reformulación A-1 declarada

`tests/test_005_012_t3_closure_dispatch_resolution.py` — `test_pd21_disposition_of_unreceipted_dispatch_is_structural_and_does_not_touch_the_rest`:

- **Se reemplaza**: la aserción `after_packet.status == "dispatched"` ("NO fabrica un estado terminal") y la lista de claves inmutables que excluía sólo `stage_history`/`last_updated`.
- **Por**: «`active_packet.status` pasa a `failed` (terminal); el resto del estado intacto» — se asevera `status == "failed"`, que el resto del dict `active_packet` es idéntico campo a campo salvo `status`, y la inmutabilidad de todo lo demás excluyendo también `active_packet`.
- **Razón**: PD-19 / D-4 enmienda la consecuencia de INV-9 de 005-012; la enmienda está **aprobada por el dueño** (`execution.md`:260). El reemplazo queda declarado en el docstring del test, en el comentario de la aserción y en el mapa del encabezado del módulo.
- El resto del test (forma de la entrada, `approval_effect: false`, ausencia de `approved_by`, `transition_key`, historia append-only, `validate-state`) **no se tocó ni se debilitó**.
- **Flujo B1 (:835)**: `test_pd21_b1_closure_rejects_then_the_disposition_unblocks_and_the_closure_advances` → **PASS** hoy (1 passed). No requirió cambios: no asevera el status del paquete.

### 4. Comandos y salida

```
$ python3 -m pytest tests/test_006_005_u5_disposition_failed.py -q
FAILED ...::test_pd19_a_disposition_marks_only_the_identified_packet_failed
FAILED ...::test_pd19_b_identical_disposition_is_a_byte_identical_noop
FAILED ...::test_pd19_prepare_is_blocked_before_and_unblocked_after
FAILED ...::test_pd19_c_late_delivery_stays_registrable_on_the_same_failed_packet
FAILED ...::test_pd19_d_failed_is_a_state_mark_and_reconcile_stays_read_only
5 failed, 1 passed in 5.49s
```

Todas las fallas son **AssertionError de contrato**, nunca import/setup/sintaxis:

```
PD-19 violada (a): el efecto del `disposition` sobre el paquete citado es `status: 'failed'` … visto 'dispatched'
PD-19 violada (b): la primera disposición deja el paquete `failed` … visto 'dispatched'
PD-19 violada: la disposición deja el paquete `failed`; visto 'dispatched'
PD-19 violada (c): el paquete queda `failed` antes del recorrido tardío; visto 'dispatched'
PD-19 violada (d): el paquete queda `failed`; visto 'dispatched'
PD-19 violada (006-005 U5, A-1): … debe dejar `active_packet.status: failed` (terminal); visto 'dispatched'
```

`test_pd19_durable_receipt_rejection_names_receive` es **GREEN hoy** (1 passed): la guarda de 005-012/PD-21(iv) ya nombra `receive`. Se declara como guarda de PD-19 y **no se le inventó un oráculo** para forzar el RED.

```
$ python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py -q
FAILED ...::test_pd21_disposition_of_unreceipted_dispatch_is_structural_and_does_not_touch_the_rest
1 failed, 10 passed in 19.17s        # B1 incluido en los 10 passed

$ python3 -m pytest <regresiones U5: t1_base, t3, t4_late, 005_001_t2, 005_001_t3,
                     006_003_rf, 006_003_rf2, test_packet_prepare> -q
1 failed, 79 passed in 171.97s       # el único fallo es el test reformulado A-1
```

Control de que el RED no es un falso rojo: con un fixture que simula el efecto nuevo (`disposition` ⇒ `failed`), los 6 focales y el test reformulado de A-1 pasan (**GREEN-SIM OK ×7**), sin tocar el test. Es una verificación del oráculo, no evidencia GREEN del producto.

`make validate`: 168 asserts PASS, **1 FAIL preexistente y ajeno**: `F011: scripts/validate-subagents.sh` → `install.sh --check` detecta drift en copias instaladas fuera del repo (`~/.claude/skills/…/cli-delegation.md`, un `.pyc`). No lo causan estos cambios (sólo tocan `tests/`) y no se tocó nada para "arreglarlo".

### 5. Commit

```
43ee3a0 test: 006-005 U5 RED — la disposición mueve el paquete activo a failed (PD-19)
 tests/test_005_012_t3_closure_dispatch_resolution.py |  53 +++++---
 tests/test_006_005_u5_disposition_failed.py          | 612 +++++++++++++++++++++
 2 files changed, 650 insertions(+), 15 deletions(-)
```

Sin `--no-verify`, sin `git stash`, sin push. `docs/planning/` y `findings/…` quedaron sin trackear.