# Informe — implementer GREEN (review-fix B2) · 005-012 T1

**Paquete:** `005-012-transition-registration-implementer-green-008` · **Ejecución:** `exec-005-012-transition-registration-001` · **Tarea:** T1 (review-fix del bloqueante B2)
**Contrato (oráculo):** `docs/specs/005-012-transition-registration/spec.md` sha256 `56d0be4b…edd5` — **verificado** con `sha256sum` antes de trabajar (la spec **enmendada**: PD-10/PD-11/PD-12, §2.2, D-7). Plan: sha256 `fb270b70…` (verificado).

*Nota de anonimización:* la raíz del repo se sustituye por `<repo>` y el tempdir por `<tmp>`; sin rutas absolutas del dueño, sin ids crudos de sesión ni nombres de otros proyectos.

## (a) Qué implementé y dónde

**Un solo archivo, en el alcance declarado (`skills`):** `skills/cdad-cycle/scripts/cdad_packet.py` (**+91 / −16**). `scripts/cdad_packet.py` es un *wrapper* delgado (`runpy.run_path` del canónico) y no contiene la operación.

1. **`_transition_identity_payload(...)` (nueva, sobre `_transition_key`).** Construye el payload canónico de PD-10: la tupla declarada (`execution_id`, `feature_id`, `transition`, `stage`, `substage`, `packet_id`, `receipt_sha256`, `resolution`) **más los insumos con efecto** — `replaced_by`, `postcondition` (`{"n": str(n), "outcome": …}` resuelta, o `null`), `current_stage` declarado, `artifacts` como **lista de pares `[path, sha256]` ordenada por `path`**, `approved_by` (sólo `gate`/`closure`), `contract`/`plan`/`closure` (`{"path","sha256"}` resueltos, o `null`). Ausente ⇒ `null` (nunca `""`); `note`/`by` **fuera** del payload.
2. **`_transition_key(payload)` (reescrita).** Aplica **la serialización declarada**: `json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",",":"))` sobre UTF-8 + sha256 hex. Misma firma que el oráculo del test.
3. **Payload como clave nueva y aditiva (§2.2).** La entrada escribe `transition_key_payload: payload` junto a `transition_key`.
4. **No-op honesto (PD-11/B2).** El atajo de no-op (que sigue corriendo **antes** de las exclusiones estructurales, como manda PD-11) deja de ser mudo: además de nombrar la entrada existente por su `transition_key`, declara que la **anotación** de esta invocación (`--note`/`--by`, fuera del payload) **no se escribió**.
5. El payload se construye **después** de resolver toda la evidencia: los digests que lleva son los **resueltos** por el CLI (PD-20), los mismos que la entrada escribe.

## (b) Corridas (salidas pegadas)

**RED de partida (antes del fix):**
```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py -q
5 failed, 16 passed in 26.92s
```

**1) Focal de B2 (obligatorio) — verde:**
```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py -q
.....................                                                    [100%]
21 passed in 26.10s
```
(21 = los 16 previos + los 5 nuevos del RED de B2.)

**2) Regresiones declaradas por la ficha T1 — verde:**
```
$ python3 -m pytest tests/test_005_007_t3_open_unit.py tests/test_005_003_t1_compact_view.py tests/test_005_003_f2_idle_history.py tests/test_packet_prepare.py tests/test_004_002_t2_bootstrap.py -q
........................................................                 [100%]
56 passed in 47.30s
```

**3) Otros focales de la feature (mismo número antes y después):**
```
$ python3 -m pytest tests/test_005_012_t2_gate_authority.py tests/test_005_012_t3_closure_dispatch_resolution.py tests/test_005_012_t4_late_delivery.py tests/test_005_012_t5_approval_vigency.py tests/test_005_012_t6_open_context_guard.py -q
3 failed, 37 passed in 59.32s
```
**Los 3 rojos son exactamente los 3 rojos de B1** (otra tarea, T3/B1: no los arreglé).

**4) Lint (no declarado en el paquete; chequeo propio):**
```
$ ruff check skills/cdad-cycle/scripts/cdad_packet.py
All checks passed!          # idéntico sobre HEAD~1 (baseline)
```

## (c) Prueba de que `tests/` no se tocó

```
$ git show --name-only --format="%h %s" HEAD | head -3
64a32d3 feat: 005-012 review-fix B2 — la identidad de la transicion incluye los insumos …
skills/cdad-cycle/scripts/cdad_packet.py          # 1 file changed, +91 / -16

$ git diff --name-only da2f784..HEAD -- tests/     # mi ejecución
(vacío)
```

**Discrepancia declarada (no silenciada).** El paquete pedía que `git diff --name-only f7fcbcc..HEAD -- tests/` fuera **vacío**; **no lo es**: contiene `tests/test_005_012_t3_closure_dispatch_resolution.py`, que introdujo el **RED de B1** (`331566c`, del test-writer de la otra tarea del review-fix), **anterior a esta sesión**. La prueba sustituta de no-injerencia es la de arriba (`da2f784..HEAD -- tests/` vacío + commit de un solo archivo). No me detuve porque la expectativa del paquete no coincide con un hecho del repo ajeno a mi alcance y no hay acción legítima que yo pueda tomar; lo reporto.

## (d) Commit

```
$ git show --stat --oneline HEAD | tail -2
64a32d3 feat: 005-012 review-fix B2 — la identidad de la transicion incluye los insumos con efecto (postcondicion resuelta, current_stage, artifacts ordenados, y los campos de cada clase) con el payload canonico escrito en la entrada como clave aditiva transition_key_payload, y el no-op (PD-11) deja de ser mudo
 skills/cdad-cycle/scripts/cdad_packet.py | 107 ++++++++++++++++++++++++++-----
 1 file changed, 91 insertions(+), 16 deletions(-)
```

**State del repo (PD-17, sólo lectura):** `validate-state` → `rc=0` **antes** y **después**. **No lo toqué**; el `M docs/.cdad-state.json` del working tree es el registro de despacho de este mismo paquete hecho por el orquestador. **No se migró** el state (D-12 se acepta tal cual).

## (e) Interpretaciones y límites

**Evidencia de la identidad y del no-op (corrida manual del fixture del RED, `<tmp>`, HOME aislado):**
```
### 1st delivery (postcondition 1) rc = 0
transition_key: 42cf66fd6d122bd540d7d9f02924c2aa0368b9ed831b4f0ad684d3ce97174d8f
### transition_key_payload escrito en la entrada
{ "approved_by": null, "artifacts": [], "closure": null, "contract": null, "current_stage": null,
  "execution_id": "exec-demo-100-transition-fixture-001", "feature_id": "demo-100-transition-fixture",
  "packet_id": "demo-100-transition-fixture-test-writer-red-001", "plan": null,
  "postcondition": {"n": "1", "outcome": "green"}, "receipt_sha256": "dcaf0f7c…b54a",
  "replaced_by": null, "resolution": null, "stage": "tdd-green-t1", "substage": null,
  "transition": "delivery" }
### recomputed sha256 == transition_key: True
### 2nd delivery (postcondition 2) rc = 0 — DOS entradas de esa etapa: True
### postconditions_status: {'1': 'green', '2': 'green'}

### repetición idéntica cambiando SÓLO la anotación
transition already registered: delivery stage 'tdd-green-t1' (7557281b…a359); no-op, no effects
no-op detail: the entry named above by its transition_key already registered this transition; the annotation of this invocation (--note/--by) is outside the identity payload and was NOT written (PD-11)
### state byte-identical: True
```

1. **`PD-12(iii)` — leí el contrato como lo pide el paquete y el RED:** «despachado» es la **noción derivada del registro de despacho** (`.cdad/executions/<exec>/dispatches/*.json`), **no** `active_packet.status`; la 2ª `delivery` del mismo paquete **se registra** (el caso 1 del RED está verde). Coherente con PD-8(a)/PD-21 y con que `active_packet.status` es un campo derivado que la propia operación escribe.
2. **`current_stage` del payload = el `--current-stage` declarado** (no el valor del state resultante): PD-10 dice «el campo operativo **declarado**».
3. **`approved_by` sólo para `gate`/`closure`**; `contract`/`plan` sólo cuando la clase los cita y el CLI los resuelve; un insumo declarado que la clase no aplica entra como `null`.
4. **`artifacts` ordenado por `path`** ⇒ el orden no cambia la identidad y la repetición idéntica resuelve al mismo par ⇒ no-op.
5. **`note`/`by` fuera del payload** ⇒ su divergencia no cambia la clave; se **declara** en la salida y no se escribe.
6. El contrato fija la **obligación** de la declaración del no-op, no su redacción: elegí una segunda línea que nombra la entrada por su `transition_key` y declara que `--note/--by` «is outside the identity payload and was NOT written». El juicio de suficiencia de la prosa queda a la review.
7. **Límite declarado (menor):** la salida **no** imprime el payload (PD-10 sólo exige escribirlo en la entrada; PD-20 sigue imprimiendo los digests usados). La identidad es recomputable desde el state.

**Aditividad y no-injerencia:** ninguna validación nueva exige campos a las entradas históricas; ninguna entrada existente se reescribe, borra ni migra; no se editó `tests/**`; no se tocó `docs/.cdad-state.json`; el cambio es aditivo en la entrada (una clave más) y en la clave (sólo puede *aumentar* distinciones: jamás convierte dos invocaciones distintas en la misma clave).
