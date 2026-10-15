# Informe GREEN — 005-012 T2 (`implementer`, subetapa `green`)

**Rol:** implementer · **Subetapa:** `green` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Paquete:** `005-012-transition-registration-implementer-green-002` · **Tarea:** T2 · **Contrato:** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) · **Entrada RED:** `docs/specs/005-012-transition-registration/t2-red.md` (oráculo congelado, commit `112ce91`).
*Nota de anonimización:* la raíz del repo se cita como `<repo>`.

## (a) Qué implementé y dónde

**Único archivo escrito y commiteado:** `skills/cdad-cycle/scripts/cdad_packet.py` (código de implementación; `git show --stat` → 1 file changed, +152/−4). No toqué ningún archivo de tests, ni `prepare`, ni `_validate_v2_vigency`, ni el lock ni la publicación atómica.

1. **Superficie de la clase `gate`** (`TRANSITION_CLASSES` + parser): `gate` entra en el vocabulario cerrado de `--transition`; el subparser `register-transition` suma `--approve-by`, `--contract-path`, `--contract-sha256`, `--plan-path`, `--plan-sha256` (destinos `args.approve_by`, `args.contract_path/contract_sha256`, `args.plan_path/plan_sha256`).
2. **`_pin_relative_digest(project_root, path_text, asserted, label)`** (nuevo): PD-5/PD-20 para los archivos citados por ruta relativa al proyecto (`--contract-path`/`--plan-path`): **deriva** el sha256 de los bytes actuales, o **verifica** el afirmado contra ellos; archivo ausente o digest afirmado divergente → `PolicyError` con marcador **`evidence missing`**, sin efectos. Sólo lee; devuelve la ruta citada y el digest usado para que la entrada registre exactamente lo verificado.
3. **`_gate_authority(state, project_root, execution)`** (nuevo): PD-6 con los tres casos.
   - **A** — `hitl_delegation` presente: consume **`_validate_v2_vigency`** (sin re-declararlo ni cambiarlo, INV-4) más la vigencia **por fecha** que ese control no lee (D4: un `expires_on` ISO en el pasado no es vigente). Revocada/vencida → **`approval pending`** nombrando el registro, sin efectos.
   - **B** — fallo cerrado: todo `PolicyError` de la vigencia se re-emite con el marcador `approval pending`, el epic activo y el registro de autoridad.
   - **C** (P2) — **sin** registro `hitl_delegation` (y la variante `active_epic: null`): devuelve `None`; **no** se bloquea al dueño, se registra el aprobador declarado y la salida **declara que no hubo delegación que verificar**.
4. **Efecto de `gate` en `register_transition`**: exige `--approve-by` no vacío (guard temprano, fuera del lock); resuelve el pin de contrato y de plan antes de escribir; verifica la autoridad; la entrada lleva `approved_by` y `contract_path`/`contract_sha256` y `plan_path`/`plan_sha256` **sólo cuando se citan** (sin `packet_id`, sin recibo, sin campos de juicio — PD-18); el efecto sobre el state es **sólo** los campos operativos `current_stage`/`tdd_substage` si se declaran (mismo camino que `advance`); `transition_key` se computa con la identidad ya declarada (PD-10), así que PD-11 (no-op byte-idéntico) sale del camino de T1 sin cambios. La salida imprime `approved_by`, los digests usados (derivados o verificados) y la nota de autoridad.

**Marcadores usados:** `evidence missing` (pin ausente/divergente, PD-5/PD-20), `approval pending` (autoridad no vigente, PD-6), `state incoherent` (sólo para combinaciones de argumentos incoherentes: `--contract-sha256`/`--plan-sha256` sin su `--path`, y `gate` sin `--approve-by`).

## (b) Corrida focal y regresiones (salida pegada, post-commit)

```
$ python3 -m pytest tests/test_005_012_t2_gate_authority.py -q
..............                                                           [100%]
14 passed in 7.54s
```

Detalle: previamente verifiqué el rojo intacto antes de tocar código (`14 failed in 6.87s`, los 14 por `AssertionError` de contrato sobre `invalid choice: 'gate' (choose from delivery, advance)`), y tras la implementación el focal pasó a **14 passed**.

```
$ python3 -m pytest tests/test_005_001_t1_role_approval.py tests/test_005_001_t4_decisive.py tests/test_005_007_t3_open_unit.py tests/test_packet_prepare.py -q
.................................                                        [100%]
33 passed in 28.24s
```

(33 verdes coincide con la línea base que el propio informe RED declaró para esas mismas cuatro regresiones.)

**Regresión proporcional extra** (motivo concreto: el cambio toca el mismo subcomando y el parser del CLI del state; se suman las regresiones que T1 declaró para el área, sin correr la suite):

```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py tests/test_005_003_t1_compact_view.py tests/test_005_003_f2_idle_history.py tests/test_004_002_t2_bootstrap.py -q
..............................................                           [100%]
46 passed in 34.74s
```

La **suite completa no se corrió** (política del paquete: la corre quien cierra).

## (c) Prueba de que `tests/` no se tocó

```
$ git diff --name-only 112ce91..HEAD -- tests/
(vacio)
$ git diff --name-only 112ce91 -- tests/   # incluye el área de trabajo
(vacio)
$ git status --porcelain -- tests/
(vacio)
```

Es decir: el oráculo congelado de RED está intacto respecto de `112ce91` **tanto en commits como en el árbol de trabajo**. Los 14 casos se hicieron verdes sin editar ni debilitar un solo test.

## (d) Commit

```
$ git log --oneline -2
21bada6 feat: 005-012 T2 GREEN — gate (pin de contrato/plan verificado por bytes, digests derivados y autoridad en tres casos)
3982fcc docs(005-012): T2 RED registrado con la operacion nueva (commit 112ce91; 14 focales rojas por asercion, 0 por import; regresiones 33 verdes)

$ git show --stat --oneline HEAD | tail -3
21bada6 feat: 005-012 T2 GREEN — gate (pin de contrato/plan verificado por bytes, digests derivados y autoridad en tres casos)
 skills/cdad-cycle/scripts/cdad_packet.py | 156 ++++++++++++++++++++++++++++++-
 1 file changed, 152 insertions(+), 4 deletions(-)

$ git status --porcelain   # tras el commit
 M docs/.cdad-state.json
```

`docs/.cdad-state.json` **no es un cambio mío**: es el registro del despacho de este paquete hecho por el orquestador; no lo toqué ni lo commiteé (mi commit tiene un solo archivo). sha256 del archivo de implementación commiteado: `a499bbd4724eb014cd38c8cf19d43debf86becac267608b57fedeeb2dfc6c023`.

## (e) Interpretaciones y decisiones (no me detuve; ninguna condición de detención se activó)

1. **No cambié `_validate_v2_vigency` y no relajé la vigencia del estado.** Se consume tal como está; no toqué 005-001 ni `validate-state`/`prepare`/`receive`. La deuda **D-10** queda declarada por la propia spec y no se modificó: los casos C asertán sólo el comportamiento de la **operación** (rc=0 + aprobador declarado), exactamente como fija PD-6 y como el RED declaró.
2. **La vigencia «vencida» no la lee `_validate_v2_vigency`.** Ese control cubre revocación, `status`, epic, `scope` y `source` resoluble, pero **no** `expires_on`; verifiqué el caso vencido contra la implementación y con el rojo (la vigencia pasaba con `expires_on: "2020-01-01"`). Por eso agregué en la **operación** la comprobación de fecha con el vocabulario ya declarado en D4 (`cdad_continuity.py:_state_authority`: `expires_on` ISO en el pasado → expired), sin re-declarar ninguna regla de otro dueño y sin tocar su fuente. La forma real de delegación (vence **por eventos**, `expires_on` ausente o lista de eventos — forma del fixture base) sigue siendo vigente por eventos.
3. **Base de resolución de `--contract-path`/`--plan-path`: raíz del proyecto** (misma convención de la bandera homónima del CLI), resuelta con el `_project_path` existente; el CLI sólo **lee** el archivo citado y no lo modifica (PD-20).
4. **Guards adicionales no exigidos por los tests, por fallo temprano y ruidoso:** `--contract-sha256`/`--plan-sha256` sin su `--path` → `state incoherent` (una aserción sin bytes que verificar no se ignora en silencio); `expires_on` con cadena no-ISO → `approval pending` (D4: «unknown nunca se fabrica como vigente»); `gate` sin `--approve-by` → `state incoherent`.
5. **La declaración de «no hubo delegación»** se verifica estructuralmente en el test (`"delegation"` en la salida), como el RED declaró; el **sentido** del texto lo juzga la review (criterio del dueño). Dejé las tres variantes de la nota de autoridad (verificada / sin epic activo / sin registro) para no afirmar algo falso en el caso «hay registro pero no hay epic activo».
6. **Alcance respetado:** no agregué `closure`/`disposition` (T3), `late-delivery` (T4), `supersedes` ni lector aditivo (T5), ni el guard de contexto abierto (T6); las clases nuevas del vocabulario quedan para sus tareas, sobre esta base.

## Archivos, comandos y evidencia

- **Modificados:** `skills/cdad-cycle/scripts/cdad_packet.py` (commit `21bada6`). Ningún otro.
- **Comandos exactos:** los cinco bloques pegados en (b) y (c), más `git log/show/status/diff` de (d).
- **Salida:** pegada arriba con su línea de resumen (`14 passed`, `33 passed`, `46 passed`, diffs de `tests/` vacíos).
- **Commit:** `21bada6` (prefijo `feat:`), acotado a un archivo de implementación; sin `--no-verify`, sin push, sin despliegue, sin tocar HOME.
- **No corrido (por política):** suite completa — la corre una vez quien cierra.
