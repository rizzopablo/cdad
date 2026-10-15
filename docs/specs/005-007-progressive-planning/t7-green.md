# GREEN de T7 — 005-007-progressive-planning (implementer, substage `green`)

**Packet:** `005-007-progressive-planning-implementer-green-009` · **Contrato:** `docs/specs/005-007-progressive-planning/spec.md` (sha256 `54877103…`) · **Postcondiciones:** PD-3, PD-4, PD-13 (+ PD-12 estructural) · **Ficha:** T7 del plan (sha256 `1f636260…`).

## Qué se hizo

Cambio documental mínimo en las dos fuentes ya declaradas por la ficha T7 (sin tocar `tests/`):

1. **`skills/cdad-cycle/references/stage-2-specification.md` — sección «Task size» (PD-3).** El criterio de tamaño de la unidad pasa a ser **por costo total**, con las cuatro condiciones **cualitativas y verificables** del oráculo, y **sin** umbrales ni conteos inventados:
   - (a) un **reviewer** no podría **rechazar** la unidad sin rechazar su **vecina**;
   - (b) cierra su propio **resultado** verificable con su **consumidor nombrado**;
   - (c) sus **costos fijos** (planeación + apertura de sesión + revisión independiente + integración) superan el **avance marginal**;
   - (d) **fragmentación**: no mueve la feature hacia un resultado verificable.
   La sección **referencia por nombre** el criterio de «costo de coordinación» ya declarado en el contrato de planificación (§5), reusándolo por referencia y sin convertirlo en número ni en puntaje. Cierra con la cláusula de replanteo **por referencia** a la regla de reintentos de `references/re-entry.md` (sin re-enunciar la regla).
2. **`skills/cdad-cycle/references/re-entry.md` — nueva sección «Retry without new information — replanning the unit (canonical link)» (PD-4, PD-13).** Hogar único de la regla de reintentos: un **reintento sin información nueva** sobre una **unidad** dispara una **revisión de estrategia** que puede **replantear la unidad** (tamaño, frontera o detalle); el **número de intentos es señal, no criterio**. Y la trazabilidad (PD-13): replantear **conserva** objetivo, dependencias y razones, y **no reescribe un contrato ya despachado sin reconciliación declarada**.

**Fuente única (PD-12):** no se agregó una segunda copia normativa. El conteo de intentos sigue declarado **solo** en `re-entry.md`; `stage-2-specification.md` lo consume por referencia (la ficha T7 pide exactamente que la sección de tamaño no re-enuncie la regla) y el literal `planning-contract-draft.md` sigue apareciendo **una sola vez** en `stage-2-specification.md` (la referencia §4.1 preexistente), preservando el oráculo de `test_004_003_t4_validation_fields.py`.

## Trazabilidad al oráculo congelado

| Caso | Postcondición | Dónde lo satisface el cambio |
|---|---|---|
| CASE 1 | PD-3 | `stage-2-specification.md` § «Task size»: las 4 condiciones + `coordination cost` por referencia; sin `%`, mínimos ni conteos. |
| CASE 2 | PD-4 | `re-entry.md` § nueva: retry sin info nueva → strategy review → replan (tamaño/frontera/detalle); intentos = señal, no criterio. |
| CASE 3 | PD-12 | La § de tamaño referencia `re-entry.md`/la regla de reintentos sin segunda declaración del conteo. |
| CASE 4 | PD-13 | La § de replanteo en `re-entry.md` conserva objetivo/dependencias/razones y exige reconciliación de un contrato despachado. |

## Evidencia

### Oráculo congelado (focal) — rojo → verde

```
python3 -m pytest tests/test_005_007_t7_unit_size_and_retries.py -v
```

Antes (RED registrado): `4 failed in 0.08s` (4 `AssertionError`).
Ahora (GREEN):

```
tests/test_005_007_t7_unit_size_and_retries.py::test_case1_pd3_unit_size_by_total_cost_qualitative_conditions PASSED [ 25%]
tests/test_005_007_t7_unit_size_and_retries.py::test_case2_pd4_retry_without_new_info_triggers_unit_replanning PASSED [ 50%]
tests/test_005_007_t7_unit_size_and_retries.py::test_case3_pd12_attempt_count_declared_only_in_re_entry PASSED [ 75%]
tests/test_005_007_t7_unit_size_and_retries.py::test_case4_pd13_replanning_preserves_trail_and_reconciles_dispatched PASSED [100%]

============================== 4 passed in 0.05s ===============================
```

### Regresión proporcional (tests que tocan `re-entry.md`/equivalencia y la skill)

```
python3 -m pytest -q tests/test_004_003_t5_reentry_equivalence.py \
  tests/test_005_007_t1_progressive_detail_rule.py \
  tests/test_005_007_t6_templates.py \
  tests/test_004_003_t4_validation_fields.py \
  tests/test_003_007_t4_atomic_unit_rule.py \
  tests/test_005_005_t2_docs_policy.py
```
→ `44 passed in 6.66s` (incluye la equivalencia de `re-entry.md`, el hogar canónico `detail` de T1, las plantillas/§4.1 de T6, el conteo único de la referencia §4.1 y la regla de reintentos).

```
python3 -m pytest -q tests/test_003_006_t1_wiring.py \
  tests/test_003_006_t3_receive_wiring.py \
  tests/test_005_006_t1_start_procedure.py \
  tests/test_005_006_t2_intake.py \
  tests/test_005_009_t2_opencode_adapter.py \
  tests/test_005_009_t4_acceptance.py
```
→ `55 passed, 1 skipped in 24.98s` (consumidores de `re-entry.md`; el skip es preexistente).

```
make validate
```
→ `Assert PASS: 141 / Assert FAIL: 2`. **Los 2 FAIL son preexistentes y ajenos al cambio**: verificados con `git stash` sobre las dos fuentes → el baseline da idéntico `Assert FAIL: 2` (`scripts/validate-subagents.sh` perfil activo y `tests/validate-odoo-specialization.sh`). No hay FAIL nuevo introducido.

### Diff acotado y commit

```
git diff --stat
 docs/.cdad-state.json                                 | 8 ++++----   (seguimiento del ciclo; NO tocado por este rol)
 skills/cdad-cycle/references/re-entry.md              | 8 ++++++++
 skills/cdad-cycle/references/stage-2-specification.md | 9 ++++++++-
 2 archivos del rol: 16 insertions(+), 1 deletion(-)
```

```
git show --stat --oneline HEAD
a59101d feat: 005-007 T7 — tamano de unidad por costo total (PD-3) y vinculo reintentos<->unidad (PD-4/PD-13)
 skills/cdad-cycle/references/re-entry.md              | 8 ++++++++
 skills/cdad-cycle/references/stage-2-specification.md | 9 ++++++++-
 2 files changed, 16 insertions(+), 1 deletion(-)
```

- **Commit:** `a59101d2832b49215e97840d987c629593bd69d4` — prefijo `feat:`.
- **Tests intactos (AP-4):** `git diff --stat 4462a9a..HEAD -- tests/` → salida vacía.
- **Archivos modificados por el rol:** `skills/cdad-cycle/references/stage-2-specification.md`, `skills/cdad-cycle/references/re-entry.md`. Nada fuera del write scope (`skills`).

### Política de suite
La suite completa **no** fue corrida por este rol: la corre una vez quien cierra (política de suite declarada en la parte común del paquete).

## Limitaciones honestas
- El juicio «sin umbrales numéricos» y «fuente única» se apoya en los oráculos congelados + la regresión citada; la lectura semántica de fondo (que el criterio no se degrade a prosa vaga) queda para el reviewer (stage 4).
- `docs/.cdad-state.json` aparece modificado en el worktree por el seguimiento del ciclo; este rol no lo tocó y no lo commiteó.
