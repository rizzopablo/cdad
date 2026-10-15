# Informe GREEN — 005-012 T4 (`implementer`, subetapa `green`)

**Rol:** implementer · **Subetapa:** `green` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Paquete:** `005-012-transition-registration-implementer-green-005` · **Tarea:** T4
**Contrato:** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) · **Plan:** §4 ficha T4 · **Oráculo congelado:** `tests/test_005_012_t4_late_delivery.py` (RED `f8fd4fb`). Raíz del repo: `<repo>`.
**No hubo detención**: el modo `--late` no exigió debilitar ninguna validación de identidad ni de digest (INV-2/D-6: se invirtió **sólo** la precondición de vigencia).

## (a) Qué implementé y dónde

Dos módulos, aditivo, mínimo, sin segunda máquina de recibos.

**1. `skills/cdad-cycle/scripts/cdad_result.py`**
- `receive(...)`: bandera declarada `late = getattr(args, "late", False)`. **Sin `--late` el camino es el de hoy, byte por byte**: `validate_request` y la comprobación «`active_packet` está `dispatched`» quedan intactas (ahora bajo `if not late:`). Con `--late` se **reemplaza únicamente** ese bloque de vigencia por la precondición inversa (helper nuevo `_late_vigency`): la feature destino **está cerrada** (`cdad_packet.CLOSED_FEATURE_STATUSES` vía `_feature_status`) y el paquete **pertenece a su ejecución** (`request.execution_id/feature_id` == la ejecución del contexto). Todo lo demás del recibo se **reusa sin tocar**: `_validate_descriptor`, `_validate_source`, `_read_parts` (digests de partes), el cotejo del `PACKET.md` contra `render_packet`, las identidades descriptor↔ejecución↔request, `_validate_scope`, `_publish` y el **esquema** del `receipt.json` con `semantic_status: "pending"` **siempre**. `receive` sigue **sin escribir el state** (INV-2). La unicidad del modo quedó documentada en el docstring del módulo, el de `_late_vigency`/`receive`, el `help` de `--late` y el comentario inline.
- `build_parser()`: `receive_parser.add_argument("--late", action="store_true", …)` (PD-13/D-5).

**2. `skills/cdad-cycle/scripts/cdad_packet.py`**
- `TRANSITION_CLASSES` suma `"late-delivery"` (vocabulario cerrado de seis valores, §2.1) y se declara `LATE_DELIVERY_STAGE = "late-delivery"` (etiqueta **canónica**, forma de `DISPOSITION_STAGE`; la clase **no** acepta `--stage`, decisión (a) del encargo).
- `register_transition`: feature resuelta con `--feature` **sólo** para `late-delivery` (con la feature cerrada `active_feature` es null; las demás clases conservan su resolución exacta de hoy); nueva clase `late-delivery` que comprueba **antes de escribir** (INV-7): `--packet` obligatorio, feature **cerrada** (si no → rc=2 **`state incoherent`**), paquete de su ejecución (si no → rc=2 `state incoherent`), y **recibo durable obligatorio** con digest **derivado** (PD-20; si falta → rc=2 **`evidence missing`** nombrando el paquete y `receipt.json`). Escribe **solo** la traza: `stage: "late-delivery"`, `transition: "late-delivery"`, `transition_key`, `approval_effect: false`, `packet_id`, `receipt_ref`/`receipt_sha256`; **sin** `approved_by` y **sin** campos de juicio. Rama de efecto explícita **`pass`** (como `disposition`): no toca `epic_features[].status`, `closed_at`, `active_feature`, `current_stage` ni `active_packet` — sólo el append + `last_updated`.
- `build_parser()`: `register.add_argument("--feature", …)` (superficie §2.1: default `active_feature`; requerida por `late-delivery`).
- La idempotencia (PD-11) sale del **mecanismo existente** (`transition_key` = sha256 de la identidad content-addressed + `_registered_transition`): la repetición idéntica devuelve rc=0, no escribe y nombra la entrada existente con su `transition_key`.

## (b) Corridas (comando exacto + línea de resumen)

```
$ python3 -m pytest tests/test_005_012_t4_late_delivery.py -q
.......                                                                  [100%]
7 passed in 12.99s
```
```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py tests/test_005_012_t2_gate_authority.py tests/test_005_012_t3_closure_dispatch_resolution.py tests/test_005_012_t5_approval_vigency.py -q
..........................................                               [100%]
42 passed in 53.21s
```
```
$ python3 -m pytest tests/test_003_002_t1_receive.py tests/test_003_002_t2_materialize.py tests/test_005_007_t4_architect_report_materialization.py -q
.........................                                                [100%]
25 passed in 32.26s
```
Regresión proporcional adicional (motivo concreto: el cambio toca la **superficie compartida** `receive` —que cablea 003-006— y `register-transition`):
```
$ python3 -m pytest tests/test_003_002_t2_reviewfix.py tests/test_003_002_t4_integration.py tests/test_003_006_t1_wiring.py tests/test_003_006_t3_receive_wiring.py tests/test_005_001_t4_decisive.py tests/test_005_013_t1_unit_projection.py -q
.............................................................            [100%]
61 passed in 71.04s (0:01:11)
```
**La suite completa no se corrió** (política del paquete: la corre una vez quien cierra).

## (c) Prueba de que `tests/` no se tocó

```
$ git diff --name-only f8fd4fb..HEAD -- tests/
( vacío )

$ git rev-parse f8fd4fb:tests/test_005_012_t4_late_delivery.py   # blob del oráculo congelado
a42850c151f6bf8b30f3f63e2c369356f7d51ca2
$ git rev-parse HEAD:tests/test_005_012_t4_late_delivery.py
a42850c151f6bf8b30f3f63e2c369356f7d51ca2
$ git hash-object tests/test_005_012_t4_late_delivery.py
a42850c151f6bf8b30f3f63e2c369356f7d51ca2

$ git status --porcelain
 M docs/.cdad-state.json      # registro de despacho del orquestador: NO mío, no lo toqué ni lo commiteé
```
Ningún archivo de `tests/**` fue editado (ni en el worktree ni en el commit).

## (d) Commit

```
$ git log --oneline -1
f5e0fc2 feat: 005-012 T4 GREEN — entrega tardia (receive --late + late-delivery; PD-13/PD-4)

$ git show --stat --oneline HEAD
f5e0fc2 feat: 005-012 T4 GREEN — entrega tardia (receive --late + late-delivery; PD-13/PD-4)
 skills/cdad-cycle/scripts/cdad_packet.py | 68 ++++++++++++++++++++++++++++++-
 skills/cdad-cycle/scripts/cdad_result.py | 69 +++++++++++++++++++++++++++++---
 2 files changed, 130 insertions(+), 7 deletions(-)
```
Commiteado con `git add` **explícito** de los dos módulos (sin `--no-verify`, sin push, sin desplegar, sin tocar HOME, sin leer `tests/.sensitive-patterns.local`).

## (e) Interpretaciones (y ausencia de detención)

1. **Condición de detención: NO se activó.** El modo `--late` no necesitó debilitar identidad ni digests: conservé `_validate_descriptor`/`_validate_source`/`_read_parts`/cotejo del render/`_validate_scope`/esquema del recibo y **añadí** dos identidades (`request.execution_id`/`feature_id` contra la ejecución del contexto). Lo que se invierte es **sólo** la vigencia (feature cerrada + paquete de su ejecución en lugar de feature abierta + `active_packet dispatched`), tal como fija PD-13/D-5.
2. **`late-delivery` sin `--stage`** (decisión (a) ya fijada por el focal): etiqueta canónica `late-delivery`, idéntica forma que `disposition`/`dispatch-disposition`; la clase **rechaza** `--stage` para que la clave de identidad no dependa de un texto sin efecto.
3. **El paquete objetivo es `prepared`, no `dispatched`** (decisión (b)): la precondición implementada es «**pertenece a su ejecución**» (`REQUEST.json` de la misma `execution_id`) y «la feature está cerrada»; **no** exijo registro de despacho, consistente con PD-13 y con que el cierre de T3 quede verde con un `prepared` sin recibo.
4. **Aditividad verificada por el focal mismo:** el caso 1 del RED exige que el `receive` **normal** sobre la feature cerrada siga fallando cerrado y no deje recibo; ese aserto pasa con mi implementación (el camino sin `--late` no cambió). Único modo que invierte la vigencia: `--late`.
5. **Reparto de marcadores** en los rechazos de `late-delivery`: feature abierta → `state incoherent`; cerrada sin recibo → `evidence missing` nombrando `<packet>` y `receipt.json`; el diagnóstico de «paquete ajeno» usa `state incoherent` (hecho estructural, coherente con `disposition`).
6. **Alcance respetado:** no se tocó `prepare --new-execution` (T6), ni el barrido de campos derivados (D-2), ni el staging del buzón / `RESULT.json` (D-8), ni los bytes del buzón; no se reabre la feature ni se aprueba nada (`approval_effect: false`, sin `approved_by`, `semantic_status: pending`). Sólo se reusó la máquina de recibos existente (005-004 PD-10 respetado).

Sin bloqueos; los 7 focales de T4 pasan por la razón del contrato y los 42 focales de T1/T2/T3/T5 junto con las 25 regresiones declaradas (y 61 proporcionales) quedan verdes.
