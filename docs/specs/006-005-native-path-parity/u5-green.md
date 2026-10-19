## Reporte — implementer GREEN, U5 de 006-005-native-path-parity

### Cambios (1 archivo, +14/−4)

`skills/cdad-cycle/scripts/cdad_packet.py` — rama `elif transition == "disposition"` de `register_transition` (efecto sobre el estado):

```python
active = state.get("active_packet")
if isinstance(active, dict) and active.get("id") == packet_id:
    new_state["active_packet"] = {**active, "status": "failed"}
```

El `pass` anterior se reemplaza por el efecto terminal de PD-19/D-4. Nada más se toca: `new_state` se construye con `dict(state)` y sólo `stage_history`, `last_updated` y `active_packet.status` difieren. No se tocó `_dispatched_packet_ids` / `_missing_required_deliveries` (leen el ledger), ni la ruta `late-delivery`, ni el rechazo con recibo durable, ni `_validate_v2_state` (el `failed` ya estaba en `VALID_PACKET_STATUSES:44` y fuera de `ACTIVE_PACKET_STATUSES:120`, así que `validate_state` y el desbloqueo de `prepare` ya eran coherentes). Idempotencia: la clave de transición existente (`_transition_key` / `_registered_transition`) sigue gobernando el no-op antes de cualquier escritura.

### Tabla test → resultado

| Test | Resultado |
|---|---|
| `tests/test_006_005_u5_disposition_failed.py::test_pd19_a_disposition_marks_only_the_identified_packet_failed` | PASS (antes FAIL: `assert 'dispatched' == 'failed'`) |
| `…::test_pd19_b_identical_disposition_is_a_byte_identical_noop` | PASS |
| `…::test_pd19_prepare_is_blocked_before_and_unblocked_after` | PASS |
| `…::test_pd19_durable_receipt_rejection_names_receive` | PASS |
| `…::test_pd19_c_late_delivery_stays_registrable_on_the_same_failed_packet` | PASS |
| `…::test_pd19_d_failed_is_a_state_mark_and_reconcile_stays_read_only` | PASS |
| **focal U5** | **6 passed** |
| `tests/test_005_012_t1_register_transition_base.py` | PASS |
| `tests/test_005_012_t3_closure_dispatch_resolution.py` (A-1 reformulado) | PASS |
| `tests/test_005_012_t4_late_delivery.py` | PASS |
| `tests/test_005_001_t2_replace_packet.py` | PASS |
| `tests/test_005_001_t3_idle.py` | PASS |
| `tests/test_006_003_rf_review_fixes.py` | PASS |
| `tests/test_006_003_rf2_review_fixes.py` | PASS |
| `tests/test_packet_prepare.py` | PASS |
| **regresiones de la ficha U5** | **80 passed** (186.96s) |
| **todos los focales `tests/test_006_005_*.py`** | **76 passed** (81.60s) |
| extra: `test_005_012_t2_gate_authority.py`, `t5_approval_vigency.py`, `test_005_014_closure_replay.py` (otras clases de `register-transition`) | 26 passed |

### Comandos con salida

```
$ python3 -m pytest tests/test_006_005_u5_disposition_failed.py -q     # RED antes del cambio
FAILED …::test_pd19_a_disposition_marks_only_the_identified_packet_failed
E  AssertionError: PD-19 violada (a): … visto 'dispatched' / assert 'dispatched' == 'failed'
1 failed in 1.02s

$ python3 -m pytest tests/test_006_005_u5_disposition_failed.py -q     # GREEN
......                                                                   [100%]
6 passed in 7.27s

$ python3 -m pytest tests/test_005_012_t1_… t3_… t4_… t2_replace_packet t3_idle rf_review_fixes rf2_review_fixes test_packet_prepare -q
........................................................................ [ 90%]
........                                                                 [100%]
80 passed in 186.96s (0:03:06)

$ python3 -m pytest tests/test_006_005_*.py -q
........................................................................ [ 94%]
....                                                                     [100%]
76 passed in 81.60s (0:01:21)

$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
make: *** [Makefile:22: validate] Error 1
```

**F011 — ambiental, declarado.** `bash scripts/validate-subagents.sh` falla sólo en `[repo] cross-check: install.sh --check`:

```
DRIFT: differs <home>/.claude/skills/cdad-cycle/scripts/__pycache__/cdad_delegate_opencode.cpython-313.pyc
DRIFT: differs <home>/.claude/skills/cdad-cycle/references/cli-delegation.md
❌ install.sh --check failed (rc=1)
```

Son copias instaladas **desactualizadas** respecto de commits anteriores (`4052939` U1a, `eb677a9` U2), no de este cambio: `skills/cdad-cycle/references/cli-delegation.md` está sin modificar en el repo (`git diff --stat` vacío) y el drift ya existía contra `HEAD` antes de mi edición. `cdad_packet.py` **no aparece** en la lista de drift (`grep -c` → 0). El resto del validador pasa (10/10 agentes runtime, artefactos por rol OK, models OK, F012, 005-004 PD-1, F011 sub-checks B8).

### Commit

`0a260ab` — `feat: 006-005 U5 GREEN — la disposicion del despacho sin recibo deja el paquete activo en failed (PD-19/D-4)` (sin `--no-verify`, sin `git stash`, sin push). 1 archivo, +14/−4.

Sin edición de `tests/`. Los untracked `docs/planning/` y `findings/incremental-construction-and-reproducible-validation-2026-10-17.md` quedaron intactos y fuera del commit (no son míos).