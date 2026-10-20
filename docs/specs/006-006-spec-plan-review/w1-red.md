# Informe de rol — test-writer, substage RED (006-006 W-1 / E4)

## Archivos modificados

| Archivo | Cambio |
|---|---|
| `tests/test_006_006_w1_replace_draft_packet.py` | **NUEVO** (1005 líneas) — RED de W-1 |

Nada más tocado: `docs/.cdad-state.json` (modificado antes de mi sesión), `docs/planning/` y `findings/` (sin trackear, ajenos) siguen intactos y fuera del commit.

## HECHO OBSERVADO (medido, CLI real, proyecto descartable)

Reproduje el W-1 antes de escribir el RED (sonda con el CLI como subproceso, en `/tmp`, sin leer implementación):

```
prepare (reviewer/plan-review, draft-plan, --object-kind spec)   -> rc=0  (paquete 001, status "prepared")
edición del borrador                                              -> digest nuevo
prepare --project-root R --replace-packet <id> --reason "..."     -> rc=2
   ERROR: plan-review subphase requires a draft-plan contract: an approved contract is not the object this procedure reviews (PD-2)
```

Causa observable: el sub-modo de reemplazo re-resuelve el contrato **aprobado por omisión** (`docs/specs/<F>/spec.md`, kind `approved-feature-spec`) en vez del borrador declarado, y la guarda de la subfase `plan-review` lo rechaza. Medí también que el sub-modo de reemplazo admite **argv puro** (`--out-dir` y `--execution-context` se rechazan: *"prepare sub-mode 'replace' admits no options from another mode"*), por lo que la fixture usa el directorio por defecto `.cdad/packets` y el contexto de ejecución en su ruta canónica.

## Mapa test → postcondición

| Test | PD / contrato | Resultado |
|---|---|---|
| `test_w1_e4_a_prepared_draft_review_packet_can_be_replaced` | **E4/W-1** + PD-2/PD-13 (spec §3.1 E4) — el reemplazo del paquete de revisión de borrador preparado y no despachado: rc=0, sucesor publicado con el digest de los bytes editados, anterior intacto + `.superseded.json` (superseded_by/reason/superseded_at/old/new), `active_packet` → sucesor `prepared`, identidad reusada, `stage_history`/`epic_history` intactos (INV-2), stdout = `PACKET.md` (INV-5), sucesor **válido** (`validate-packet` rc=0) | 🔴 RED |
| `test_w1_e4_the_replacement_keeps_the_declared_form_of_the_reviewed_object` | **E4/W-1** + PD-2 (R-7/R-8), forma `plan` con acompañante: la forma declarada, la versión, la ruta y el acompañante no cambian; sólo los digests (principal y acompañante) se recalculan de los bytes | 🔴 RED |
| `test_w1_e4_the_replacement_does_not_authorize_the_draft` | **E4/W-1** + INV-2/PD-7: el kind sigue siendo `draft-plan`, `active_packet.contract_kind` = `draft-plan`, `stage_history` no gana entradas, el borrador en disco no lo toca el CLI | 🔴 RED |
| `test_w1_e4_the_vigente_rejections_of_the_replacement_are_conserved` | 005-001 **PD-9/PD-10 vigentes** (conservados): despachado ⇒ rc≠0 con marcador `packet obsolete` nombrando el paquete; sin `--reason` ⇒ rc≠0; ambos **sin efectos** | 🟢 control |
| `test_w1_e4_control_the_replacement_over_an_approved_contract_is_unchanged` | 005-001 PD-7 (control): el reemplazo sobre contrato aprobado sigue rc=0 con sucesor + `.superseded.json`; y el guard vigente «`plan-review` sobre kind aprobado ⇒ rechazo» sigue verde (**por su efecto, no por su texto**) | 🟢 control |

## A-1 (declarado)

- Este RED **no reemplaza ni congela** ningún oráculo vigente: los ficheros de 005-001 T2/Tcorr/T3/T4, 005-005 T1/T4, 004-003 T2 y el focal `test_006_006_u1_draft_object_form.py` se **ejecutan como regresiones** y no se tocan (60 passed).
- **El único oráculo que hoy Fixaría el rechazo actual es el texto del guard vigente** («plan-review subphase requires a draft-plan contract…»), que es **el mismo texto** que hoy bloquea el caso de W-1. Por eso el control (b) afirma el **efecto** (rc≠0, sin publicación, state byte a byte idéntico, sin traceback) y **no** el texto. El RED afirma, en cambio, que ese texto **deja de ser** el resultado del reemplazo de un borrador (rc=0). Ningún oráculo existente se fija en el texto del rechazo del caso de W-1.
- Los rechazos que sí fijo (marcador `packet obsolete` del paquete despachado; rc≠0 sin razón) son **rechazos vigentes** que W-1 no toca: se comprueban para que el arreglo no los relaje.
- Fixtures **propios** (borradores y proyecto sintéticos nuevos): no se reusa el `DRAFT_PLAN_RELPATH` compartido por 11 ficheros.

## Comandos y salidas

```
$ python3 -m pytest tests/test_006_006_w1_replace_draft_packet.py -v
tests/...::TestW1ReplaceThePreparedDraftPacket::test_w1_e4_a_prepared_draft_review_packet_can_be_replaced FAILED [ 20%]
tests/...::TestW1ReplaceThePreparedDraftPacket::test_w1_e4_the_replacement_does_not_authorize_the_draft FAILED [ 40%]
tests/...::TestW1ReplaceThePreparedDraftPacket::test_w1_e4_the_replacement_keeps_the_declared_form_of_the_reviewed_object FAILED [ 60%]
tests/...::TestW1TheVigenteRejectionsAreConserved::test_w1_e4_the_vigente_rejections_of_the_replacement_are_conserved PASSED [ 80%]
tests/...::TestW1ControlOverAnApprovedContract::test_w1_e4_control_the_replacement_over_an_approved_contract_is_unchanged PASSED [100%]
E  AssertionError: 2 != 0 : E4/W-1: el paquete de revisión de borrador preparado y no despachado debe poder
   reemplazarse (E4: la re-review focal tras la corrección es exigible); hoy el reemplazo falla:
   ERROR: plan-review subphase requires a draft-plan contract: an approved contract is not the object this procedure reviews (PD-2)
========================= 3 failed, 2 passed in 3.44s ==========================
```

Los 3 RED fallan por **aserción de comportamiento ausente** (`rc 2 != 0`), nunca por ImportError/uso de CLI.

```
$ python3 -m pytest tests/test_005_001_t2_replace_packet.py tests/test_005_001_tcorr.py \
    tests/test_005_001_t3_idle.py tests/test_005_001_t4_decisive.py \
    tests/test_005_005_t1_replace_conserved.py tests/test_005_005_t4_integration.py \
    tests/test_006_006_u1_draft_object_form.py tests/test_004_003_t2_plan_review.py
======================== 60 passed in 73.13s (0:01:13) =========================
```

```
$ make validate
Assert PASS: 168
Assert FAIL: 1        # F011: scripts/validate-subagents.sh (active profile) → FAIL
```
`make validate` falla por **deriva ambiental pre-existente** entre el repo y el producto instalado en el HOME (`~/.config/opencode`, `~/.claude`: `install.sh --check` ⇒ DRIFT + "missing staged agents/…"). **No lo causa mi commit**: reproducido idéntico sobre `HEAD~1` vía `git archive` (168 PASS / 1 FAIL). No lo corrijo (fuera de mi write scope `tests/`).

## Commit

```
4f755ac test: 006-006 W-1 RED — reemplazo de un paquete de revision de borrador
 tests/test_006_006_w1_replace_draft_packet.py | 1005 +++++++++++++++++++++++++
 1 file changed, 1005 insertions(+)
```

## Límites respetados

- Sólo `tests/` escrito; commit con un único fichero.
- **No leí implementación**: `skills/cdad-cycle/scripts/` sólo se invoca como CLI (subproceso); los oráculos del contrato de reemplazo se derivaron de la **suite vigente** (`tests/test_005_001_t2_replace_packet.py`, PD-7..PD-11), leída desde el read scope `tests/`.
- Sin valores del host: `HOME` del subproceso = tempdir vacío; fixture sintética y anónima; el proyecto es descartable (nunca el repo, nunca el HOME).
- Sin `--no-verify`, sin `git stash`, sin `push`; la suite completa no se corre (política del paquete: la corre quien cierra).