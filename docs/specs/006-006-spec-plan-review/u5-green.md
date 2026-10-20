GREEN complete. Final report:

---

# CDAD — implementer GREEN, U5 (006-006-spec-plan-review)

**Packet**: `006-006-spec-plan-review-implementer-green-002` · exec `exec-006-006-spec-plan-review-001` · substage `green` · rol `implementer`
**Contrato**: `docs/specs/006-006-spec-plan-review/spec.md` (sha256 `4d029a11…d298`) · plan `docs/specs/006-006-spec-plan-review/plan.md` §3 U5 · errata **B-5** aceptada en la aprobación

## 1. Fichero modificado (único)

| Fichero | Cambio | Zona de la ficha U5 |
|---|---|---|
| `skills/cdad-cycle/scripts/cdad_packet.py` | +139 / −5 | las **cuatro** zonas + la calificación de la rama de no-op (B-4) |

Nada más: `git diff --name-only a95cc2c..HEAD -- tests/` → **0 ficheros**. `docs/.cdad-state.json` (modificado por el orquestador), `docs/planning/` y `findings/*` (sin trackear) siguen **sin tocar**. No leí ni escribí la config, el store, el runtime ni la instalación del HOME.

**Qué implementa (mínimo, el contrato y nada más):**

1. **Parser** (`:6715-6731`): `--exempted-by`, `--exemption-reason`, `--requested-by` y `--delegated` (interruptor) en `register-transition`.
2. **Admisibilidad de clase** (`:5614-5626`): las cuatro banderas sólo con `--transition gate`; fuera ⇒ rc≠0 **nombrando la clase** (`gate`), **antes del lock** ⇒ state byte-idéntico y sin segunda entrada.
3. **Entrada** (`:6112-6116`): la entrada de `gate` suma `exempted_by`, `reason`, `requested_by`, `delegated` **planos y sólo si se declaran** (D-6: la exención viaja en la misma entrada que la aprobación; el pin no cambia).
4. **Payload de identidad** (`:5163-5216`): bloque `exemption` **condicional** con **exactamente** los campos declarados (R-11/R-12). Sin exención declarada el payload conserva sus **16 claves** ⇒ serialización y `transition_key` **byte-idénticas** al producto vigente (R-13/D-14, sin enmienda de 005-014 PD-23 ni 006-005 PD-19(b)).
5. **Rama de no-op calificada + rechazo de colisión** (`:5988-6025`, auxiliares `:5264-5307`): el replay de la **vigente** sigue siendo no-op; la colisión con una entrada histórica **no vigente** mientras compite una vigente **nunca** es no-op: con `--supersedes` ⇒ **rechazo explícito de colisión** (`state incoherent`, nombra la clave que colisiona, que **no** es la vigente, la clave de la vigente y las **dos salidas**); sin `--supersedes` ⇒ el **rechazo vigente** de PD-14 (una sola aprobación).

## 2. Tabla test → resultado (focal `tests/test_006_006_u5_exemption_record.py`)

| # | Test | PD | Resultado |
|---|---|---|---|
| 1 | `..._exemption_flags_write_the_four_fields_in_the_entry` | PD-9 | 🟢 |
| 2 | `..._without_the_flags_the_entry_carries_no_exemption_field` | PD-9 ctrl | 🟢 |
| 3 | `..._flags_outside_the_gate_class_are_rejected_naming_the_class` | PD-9 | 🟢 |
| 4 | `..._exemption_entry_does_not_enable_construction` | PD-9+PD-14 | 🟢 |
| 5 | `..._approval_with_exemption_stays_vigente_for_the_closure` | PD-9+V-4 | 🔴 **inalcanzable** (§5) — la implementación es correcta |
| 6 | `..._payload_carries_the_exemption_block_with_exactly_the_declared_fields` | R-11/R-12 | 🟢 |
| 7 | `..._payload_block_carries_only_the_declared_fields` | R-12 | 🟢 |
| 8 | `..._identical_repetition_with_the_same_exemption_is_a_noop` | PD-11+R-14(a) | 🟢 |
| 9 | `..._repetition_that_changes_the_exemption_is_not_a_noop` | B-2+INV-12 | 🟢 |
| 10 | `..._two_revisions_gate_keeps_the_identity_and_the_replay_is_a_noop` | R-13 (control) | 🟢 |
| 11 | `..._two_revisions_closure_keeps_the_identity_...` | PD-23 (control) | 🟢 |
| 12 | `..._two_revisions_disposition_keeps_the_identity_...` | PD-19(b) (control) | 🟢 |
| 13 | `..._aba_walk_rejects_the_return_to_the_previous_payload` | R-14(b)+D-15 | 🟢 |
| 14 | `..._aba_walk_registers_the_return_with_a_distinguishable_value` | R-14(b)+D-15 | 🟢 |

**Focal: `1 failed, 13 passed`** (antes: `10 failed, 4 passed`).

## 3. Comandos y salida

```
$ python3 -m pytest tests/test_006_006_u5_exemption_record.py -q
13 passed, 1 failed in 20.39s        # post-commit; el que falla es el #5 (§5)

$ python3 -m pytest -q tests/test_006_006_u5_exemption_record.py tests/test_006_006_u1_draft_object_form.py \
    tests/test_005_012_t1_register_transition_base.py tests/test_005_012_t2_gate_authority.py \
    tests/test_005_012_t3_closure_dispatch_resolution.py tests/test_005_012_t4_late_delivery.py \
    tests/test_005_012_t5_approval_vigency.py tests/test_005_014_closure_replay.py \
    tests/test_006_005_u5_disposition_failed.py
1 failed, 105 passed in 146.42s

$ python3 -m pytest -q tests/test_005_001_t2_replace_packet.py tests/test_005_001_t3_idle.py \
    tests/test_006_003_rf_review_fixes.py tests/test_006_003_rf2_review_fixes.py tests/test_packet_prepare.py
41 passed in 120.84s

$ make validate
Assert PASS: 168 · Assert FAIL: 1     → F011 = scripts/validate-subagents.sh (F011 ambiental, ver §4)
```

| Regresión de la ficha | tests | Resultado |
|---|---|---|
| `test_005_012_t1_register_transition_base.py` | 21 | 🟢 |
| `test_005_012_t2_gate_authority.py` (O-1) | 14 | 🟢 |
| `test_005_012_t3_closure_dispatch_resolution.py` | 11 | 🟢 |
| `test_005_012_t4_late_delivery.py` | 7 | 🟢 |
| `test_005_012_t5_approval_vigency.py` (O-1) | 8 | 🟢 |
| `test_005_014_closure_replay.py` (B-3) | 4 | 🟢 |
| `test_006_005_u5_disposition_failed.py` (B-3) | 6 | 🟢 |
| `test_005_001_t2_replace_packet.py` | 8 | 🟢 |
| `test_005_001_t3_idle.py` | 4 | 🟢 |
| `test_006_003_rf_review_fixes.py` | 4 | 🟢 |
| `test_006_003_rf2_review_fixes.py` | 6 | 🟢 |
| `test_packet_prepare.py` | 19 | 🟢 |
| **focal de U1** `test_006_006_u1_draft_object_form.py` | 21 | 🟢 |

**Sin cambio de oráculo** (A-1): los tres oráculos que B-4 no toca siguen verdes sin cambio (`t2:630` no-op de la vigente · `t5:341` segunda vigente sin `--supersedes` · `t5:622` `gate` con `--supersedes` y repetición no-op).

**Recorridos (salida real, para la evidencia de U6):**

```
A) A→B→A
  A key = c1af54b0…76f7   B key = c9be8f67…d3f   (distintas: True)
  (iii) A sin --supersedes  -> rc=2  state incoherent: … already has a vigente `specification` approval
        … (transition_key 'c9be8f67…d3f'); registering a second vigente one requires --supersedes …
        entradas 4 -> 4 ; state sha256 idéntico: True
  (iv)  A con --supersedes  -> rc=2  state incoherent: this invocation collides with the historical
        transition_key 'c1af54b0…76f7', which is NOT the vigente `specification` approval … (the vigente
        one is 'c9be8f67…d3f'); … Two legitimate exits: (i) register the change with a DISTINGUISHABLE
        value — cite the owner's decision as evidence with `--artifact <path>` …; (ii) RECONCILE the history …
        entradas 4 ; state sha256 idéntico: True
  (v)   replay de la vigente -> rc=0  transition already registered: gate stage 'specification'
        (c9be8f67…d3f); no-op, no effects      entradas 4 ; state sha256 idéntico: True
  LECTOR (prepare de un rol de construcción) -> rc=0   (la vigente sigue habilitando)

B) registro con VALOR DISTINGUIBLE (la salida que el rechazo nombra)
  rc=0 ; clave nueva 8b64103b…421c (≠ A, ≠ B) ; supersedes = c9be8f67…d3f (la vigente B)
  bloque `exemption` en el payload: None   (la exención queda retirada de verdad)
  LECTOR tras la retirada -> rc=0          (la entrada nueva habilita)
```

## 4. `make validate` — F011 ambiental (declarado, preexistente)

`Assert PASS: 168 · Assert FAIL: 1` → **F011 = `scripts/validate-subagents.sh`**: `install.sh --check` (DRIFT de la instalación del HOME) y «`cdad-reviewer.md` declares model». **Preexistente y ajeno a U5**: reproducido idéntico sobre un árbol limpio `git archive HEAD` (sin mi fichero) — `❌ install.sh --check failed (rc=1)` / `❌ cdad-reviewer.md declares model` / `RESULT: FAIL`. No lo toco (fuera de mi write scope) y lo declaro.

## 5. **Mismatch que reporto al orquestador** (no toco `tests/`)

`tests/test_006_006_u5_exemption_record.py:674` — `assert reader.returncode == 0` (dentro del test #5, `…_approval_with_exemption_stays_vigente_for_the_closure`) es **inalcanzable con cualquier implementación correcta**:

- La fixture `_ExemptionClosureFixture` (`tests/…:434-460`) extiende `_ClosureFixture` (modo `ready`) y **no registra la transición `delivery`**: el paquete activo queda `dispatched` y publicado. La fixture `gate` del propio RED sí lo hace (`self.deliver()`, `:398`) y su docstring lo declara («el LECTOR exige un paquete terminal»).
- El LECTOR es `prepare`, y `prepare` rechaza **antes** de la comprobación de la aprobación: `active packet '…' is 'dispatched': complete or fail it before preparing a new packet (PD-4)` (`cdad_packet.py:4739-4742`).
- **PD-4 es un oráculo vigente**: `tests/test_004_002_t2_bootstrap.py:522` `test_pd4_active_packet_prepared_or_dispatched_blocks_replacement` ⇒ ninguna implementación puede devolver `rc=0` ahí sin romperlo, y el cambio está fuera de las cuatro zonas de la ficha U5.
- **Evidencia de que la implementación es correcta** (sondas fuera del repo, `/tmp/opencode/u5/`): con el paquete terminal, la misma fixture da `gate rc=0` con la entrada `exempted_by/reason/requested_by/delegated`, el payload con el bloque `exemption`, y **lector `rc=0`**; y parcheando **sólo la fixture** (`self.delivery()` en `_ExemptionClosureFixture.__init__`, el mismo camino que ya usa `_ExemptionFixture`) el test #5 pasa **al 100 %** (las tres aserciones de V-4: lector, segunda aprobación rechazada y cierre `rc=0`).
- **Arreglo que le toca al test-writer** (fichero suyo, fuera de mi write scope): una línea en `_ExemptionClosureFixture.__init__` — `self.delivery()` (o `self.deliver()`) — igual que hace `_ExemptionFixture.__init__`. Sin ese cambio, la aserción del lector mide el estado del paquete activo, no la vigencia de la exención; **la sustancia de V-4 (la aprobación con exención sigue vigente para el cierre) queda demostrada** por el cierre `rc=0` del mismo recorrido.

No he editado ningún fichero de `tests/`, ni he tocado el oráculo de PD-4, ni he aplicado ninguna desviación para maquillar la aserción.

## 6. Commit

```
$ git add skills/cdad-cycle/scripts/cdad_packet.py
$ git commit -m "feat: 006-006 U5 GREEN — exencion en la identidad de la transicion"
[main 1cbccd5] feat: 006-006 U5 GREEN — exencion en la identidad de la transicion
 1 file changed, 139 insertions(+), 5 deletions(-)
```

`1cbccd5` · sin `--no-verify` (no hay hooks instalados), sin `git stash`, sin `push` · `tests/` intacto · estado del repo tras el commit: sólo `M docs/.cdad-state.json` (del orquestador) y los sin trackear de `docs/planning/` y `findings/` (no míos).

**Nota de alcance**: no ejecuté la suite completa (la corre una vez quien cierra, según la política del paquete) ni toqué `agents/`, `sources/`, `build/` o `install.sh` (esta unidad es de una sola zona de `cdad_packet.py`).