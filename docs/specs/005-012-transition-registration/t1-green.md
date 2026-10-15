# Informe GREEN — 005-012 T1 (`implementer`, subetapa `green`)

**Paquete:** `005-012-transition-registration-implementer-green-001` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Tarea:** T1
**Contrato:** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) · **Plan:** `…/plan.md` §4 ficha T1
**Commit:** `401f966` — `feat: 005-012 T1 GREEN — register-transition (delivery/advance, digests derivados, identidad)`
**Archivo modificado (único):** `skills/cdad-cycle/scripts/cdad_packet.py` (+312, −0). Raíz del repo en este informe: `<repo>`.

## (a) Qué implementé y dónde

Todo aditivo, en `skills/cdad-cycle/scripts/cdad_packet.py`, sin tocar `prepare`, ni el lock, ni la publicación, ni `receive`/`materialize`:

1. **Superficie (PD-1).** Subcomando `register-transition` declarado en `build_parser` (bloque nuevo junto a `open-unit`) y despachado en `main` (`register_transition(args, project_root)` → `sys.stdout.write(...)`). `--help` propio; `--transition` con vocabulario cerrado.
2. **Escritor único (PD-1/INV-1).** Toda escritura pasa por `_ProjectLock` + `_publish_owned_atomically` + la serialización única `_serialize_document`. No agregué un segundo escritor ni una segunda serialización; no toqué `prepare` (conserva su rol).
3. **Forma aditiva del registro (§2.2).** Una entrada de `stage_history` (append) con las claves existentes de la historia más las nuevas declaradas: `transition`, `transition_key`, `supersedes`, `approval_effect: false` (más `packet_id`/`receipt_ref`/`receipt_sha256`/`artifacts`/`note`/`by`/`substage` como en la historia real, con `null` para lo ausente). Ninguna entrada histórica se reescribe ni se le exige la clave nueva (PD-17/INV-3).
4. **Resolvedor de digests derivados (PD-20).** `--receipt` y `--artifact <path>[=<sha256>]` son **opcionales**: si se omiten, el digest se **deriva** de los bytes actuales, se escribe en la entrada y se **imprime**; si se afirman, se **verifican** y una diferencia falla cerrado. El CLI **sólo lee** el archivo citado (nunca lo escribe).
5. **Clase `delivery` (PD-2/PD-3/PD-4/PD-12(iii)/PD-18).** Resuelve el recibo durable `.cdad/runtime/results/<exec>/<packet>/receipt.json`, aplica `active_packet.status: "completed"` cuando el paquete citado es el activo, y `tdd_substage`/`postconditions_status` si se declaran. No escribe `approved_by`, `contract_*`, `plan_*` ni campos de juicio: **recibir nunca aprueba**. Marcadores por condición: paquete ajeno a la ejecución activa o recibo ausente/divergente → `evidence missing`; paquete sin registro de despacho → `state incoherent`.
6. **Clase `advance` (PD-7).** Fija `current_stage` y/o `tdd_substage` con el vocabulario operativo cerrado (`VALID_CURRENT_STAGES` = los seis de `state-detection.md:20-37`; `VALID_SUBSTAGES` reusado). Un valor fuera del vocabulario → rc=2 `state incoherent` nombrando el valor rechazado y los admitidos, sin efectos.
7. **Identidad y repetición (PD-10/PD-11/PD-12).** `transition_key = sha256(canonical(execution_id, feature_id, transition, stage, substage, packet_id, receipt_sha256, resolution))`. Repetición idéntica → rc=0, **sin** escribir (state byte a byte idéntico) y salida que **nombra la clave existente**; clave distinta → entrada nueva; exclusión estructural → `state incoherent`. El no-op no depende de la cabeza (busca en toda la historia).

**Usable de verdad (no sólo verde en el test):** verifiqué la invocación real sobre un proyecto descartable (sonda fuera del repo, `<tmp>`, HOME del subproceso en un tempdir vacío). Salida real (fragmento; ids sintéticos del fixture, `<tmp>` sustituye el tempdir):

```
--- delivery (minimum form, no digest asserted): rc=0
registered transition delivery stage 'tdd-green-t1' for demo-100-transition-fixture
transition_key: 512100848baf4ce53ec37eb4e40c92c8c7fa551015892630a6e976a62c182c0e
packet: demo-100-transition-fixture-test-writer-red-001
receipt_sha256: 197349d9fd07f4b074e4eac30db9f9912686b78c2225bfc8a57fafab004ffd5a (.cdad/runtime/results/exec-demo-100-transition-fixture-001/demo-100-transition-fixture-test-writer-red-001/receipt.json)
stage_history: 2 entries (+1)

--- delivery repeated (identical): rc=0
transition already registered: delivery stage 'tdd-green-t1' (51210084…2c182c0e); no-op, no effects

--- delivery with a divergent asserted digest: rc=2
ERROR: evidence missing: the asserted receipt digest ffff…ffff for packet demo-100-transition-fixture-test-writer-red-001 does not match the current bytes 197349d9…004ffd5a of .cdad/runtime/results/…/receipt.json; omit --receipt to let the CLI derive the digest, or cite exactly the bytes reviewed

--- advance (out-of-vocabulary value): rc=2
ERROR: state incoherent: --current-stage 'grooming' is outside the closed vocabulary ['discovery', 'idle', 'merge', 'review', 'specification', 'tdd']; name one of those stages

--- delivery of a not-dispatched packet: rc=2
ERROR: state incoherent: packet demo-100-transition-fixture-test-writer-red-001 has no dispatch record in the active execution exec-demo-100-transition-fixture-001, so it cannot be received as a delivery (only a dispatched packet can have a durable receipt). Dispatch it first, or cite the dispatched packet
```

## (b) Verificación corrida (salida pegada)

Comando y salida del focal:

```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py -q
...............                                                          [100%]
15 passed in 14.38s
```

Comando y salida de las regresiones declaradas por la ficha:

```
$ python3 -m pytest tests/test_005_007_t3_open_unit.py tests/test_005_003_t1_compact_view.py \
    tests/test_005_003_f2_idle_history.py tests/test_packet_prepare.py \
    tests/test_004_002_t2_bootstrap.py -q
........................................................                 [100%]
56 passed in 36.53s
```

(56 = la misma línea base que el RED declaró, `t1-red.md:104`.)

Evidencia extra, motivo concreto (PD-17: aditividad de sólo lectura sobre el state vivo del repo, sin cifras; `validate-state` rc=0 antes y después — el reader no fue tocado, la operación no corre sobre el repo):

```
$ python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root .
VALID: execution=exec-005-012-transition-registration-001 feature=005-012-transition-registration model_policy=ordinary
rc=0
```

La suite completa **no** se corrió (política del paquete: la corre una vez quien cierra).

## (c) Prueba de que `tests/` no se tocó

```
$ git diff --name-only 878091b..HEAD -- tests/
(sin salida: vacío)

$ git show --stat --oneline HEAD | tail -2
 skills/cdad-cycle/scripts/cdad_packet.py | 312 +++++++++++++++++++++++++++++++
 1 file changed, 312 insertions(+)

$ git status --porcelain
(sin salida: árbol limpio)
```

Ninguna escritura fuera del alcance declarado (`skills/`, código de implementación). No leí `tests/.sensitive-patterns.local`.

## (d) Commit

```
$ git log --oneline -1
401f966 feat: 005-012 T1 GREEN — register-transition (delivery/advance, digests derivados, identidad)

$ git show --stat --oneline HEAD | tail -2
401f966 feat: 005-012 T1 GREEN — register-transition (delivery/advance, digests derivados, identidad)
 skills/cdad-cycle/scripts/cdad_packet.py | 312 +++++++++++++++++++++++++++++++
 1 file changed, 312 insertions(+)
```

## (e) Puntos del contrato que tuve que interpretar (no detuve nada)

No me detuve: **no** hubo que relajar ninguna validación de `prepare`, **no** hubo que reescribir ninguna entrada existente del state y **no** escribí ningún archivo citado por un digest — ninguna de las condiciones de detención de la ficha (INV-1, INV-3, PD-20) se activó. Las decisiones de interpretación:

1. **`--transition` declarado con las dos clases implementadas** (`delivery`, `advance`). Las otras cuatro del vocabulario cerrado de §2.1 quedan **excluidas** por la ficha (T2/T3/T4), así que no declaro una superficie a medio implementar: una clase no implementada falla cerrado con `invalid choice` (rc=2, error de uso). T2..T4 extienden esa tupla. `--feature` (bandera de la entrega tardía sobre una feature cerrada, T4) **no** se declara: en T1 `delivery`/`advance` operan sobre la feature activa (que es el default de §2.1); declarar una bandera sin efecto ensancharía la superficie.
2. **Orden de comprobaciones (crítico para PD-11 y PD-12).** El no-op (PD-11) se evalúa **antes** de la comprobación estructural «paquete despachado», y el digest del recibo se deriva **sólo leyendo** antes de esa comprobación, porque la clave de identidad lo incluye: si el no-op fuera después, la repetición idéntica de una `delivery` —que deja `active_packet.status: completed`— fallaría cerrado y contradiría PD-11. El orden final es: pertenencia del paquete (evidence missing, PD-3) → resolución de digests (evidence missing, PD-3/PD-20) → no-op (rc=0) → paquete despachado (`state incoherent`, PD-12) → recibo presente (`evidence missing`, PD-3). Con ese orden el fixture `prepared` (no despachado y sin recibo) da `state incoherent` y no `evidence missing`, como exige el reparto de marcadores de PD-12.
3. **«Despachado» derivado del registro de despachos** (`.cdad/executions/<exec>/dispatches/*.json`), no de `active_packet.status` solo: es la misma noción derivada que PD-8(a) declara para el conjunto de entregas requeridas, y sostiene el caso de un paquete de la ejecución activa que **no** es el paquete activo. El efecto sobre `active_packet` sigue siendo el de §2.2 (sólo «si el paquete citado es el activo»).
4. **Claves nuevas del registro.** Escribo siempre `transition`, `transition_key`, `supersedes` (con `null` si no se afirma) y `approval_effect: false`, porque §2.2 las declara como las claves nuevas de la entrada; `resolution`/`replaced_by` **no** se escriben porque su clase (`disposition`) queda excluida de T1. Las referencias opcionales quedan con `null` cuando no aplican, que es el estilo que ya usa la historia real (`packet_id: null`).
5. **`last_updated`** se actualiza con el mismo instante que el `at` de la entrada (INV-9 sanciona esa escritura). No afecta PD-11 ni INV-7: tanto el no-op como todo rechazo **no escriben nada**.
6. **`--artifact`** se resuelve con el helper existente (`_cwd_path`): acepta ruta absoluta o relativa al cwd del subproceso, y el sufijo se interpreta como digest **sólo** si son 64 hex tras el último `=` (PD-20). El `prepared --postcondition/--outcome` se exigen en pareja (si falta uno → rc=2 sin efectos).
7. **Marcadores y lenguaje.** Los comentarios del código están en inglés (convención del producto); los diagnósticos siguen el estilo de los existentes (`state incoherent:` / `evidence missing:` + el hecho + la acción siguiente). Sin rutas absolutas del dueño, sin ids crudos de sesión y sin nombres de otros proyectos en el código, el commit ni este informe.

**Matiz honesto heredado del RED (declarado allí y verificado acá):** en los casos negativos la primera aserción es `rc == 2`, y un error de uso de argparse también da rc=2; la aserción discriminante es el **marcador**. Ahora los marcadores provienen de los diagnósticos de dominio del CLI (ver la sonda de (a)), no del error de uso. **Límite declarado:** la mitad «árbol» de INV-7 (snapshot completo del árbol, más allá del state byte a byte idéntico) no la aserté, por el motivo que el RED ya declaró (T8). El único artefacto que el CLI toca fuera del state es el rendezvous `.cdad/.lock` (comportamiento existente del lock, no de esta operación).
