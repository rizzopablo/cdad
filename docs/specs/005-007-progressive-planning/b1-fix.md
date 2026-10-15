# Review-fix (etapa 4, GREEN) — 005-007-progressive-planning · implementer · B1 (ACOTADO)

**Packet:** `005-007-progressive-planning-implementer-review-fix-002` · **Ejecución:** `exec-005-007-progressive-planning-001` · **Rol:** implementer · **Substage:** `review-fix`.
**Contrato:** `docs/specs/005-007-progressive-planning/spec.md` — sha256 `54877103d622ca75994b503ee4be016bf39682c2c6a6f89962a8436d8d309a4a` ✅ (PD-1, PD-2, INV-5).
**Review:** `review.md` (B1, bloqueante, acotado al camino `planned`).
**Oraculo congelado (no editado):** `tests/test_005_007_reviewfix_blockings.py` (testfix `e3375e4`) + `tests/test_005_007_t2_progressive_plan_validator.py`.

## Resultado

- **B1 → CORREGIDO, oráculo de review-fix verde.** `2 passed` (B1 + B2).
- Oraculos de etapa 3 que no debían romperse: **30 passed** (T1/T2/T3/T5/T6/T7).
- Regresiones de área: **16 passed** (004-003 T3/T4) + **26 passed** (contrato de paquete / prepare).
- `tests/**` **NO tocado** (AP-4, invariante del packet).

## Cambio (mínimo, acotado a la tarea `planned`)

`skills/cdad-cycle/scripts/cdad_packet.py` — rama `detail == "planned"` de `_check_plan_validation_plan`
(única superficie; el camino `next`/sin marcador queda **intacto**, INV-5):

- Junto a los campos ya exigidos (`objective` no vacío, `uncertainty`, `owner`, `resolves_when`) se exige ahora la clave **`depends_on` PRESENTE** y **con forma de lista**; `[]` es válido y declara «sin dependencias» (misma mecánica que `regressions`).
- Un caso ausente/malformado **falla cerrado**: `rc≠0`, `ERROR: ...` que **nombra la tarea y el campo**, stdout vacío, nada publicado, state y árbol sin cambios.
- Forma malformada con la clave presente (p. ej. `"x"`) ya era rechazada por `_check_plan_tasks` («depends_on must be a list of task ids»), que corre antes y sigue nombrando tarea+campo.
- **No se agregó ninguna exigencia al camino `next`/sin marcador.** Los casos amplios del encargo anterior (`b-sin-objective`/`c-sin-clave-depends_on` sobre el camino sin marcador) siguen retirados en el oráculo congelado; este fix no los reintroduce.
- Comentario de `PLAN_TASK_PLANNED_FIELDS` y docstring de `_check_plan_validation_plan` actualizados para declarar la dependencia obligatoria (fuente única de la regla en la rama `planned`).

### Diagnóstico observado (probe directo, mismo harness del oráculo)

```
$ python3 - <<'PY'  … (PrepareProject + plan_bytes([planned_task("t1", depends_on=None)]))
rc: 2
stdout: b''
stderr: ERROR: plan task 't1' is marked detail 'planned' but declares no depends_on list ([] declares no dependencies) (PD-1)
```

## Comandos y salidas (evidencia obligatoria)

### 1. Oraculo de review-fix (todos verdes, incluido el control `depends_on: []`)

```
$ timeout 300 python3 -m pytest tests/test_005_007_reviewfix_blockings.py -q
..                                                                       [100%]
2 passed in 2.83s
```

### 2. Oraculos de etapa 3 (por archivo)

```
$ python3 -m pytest tests/test_005_007_t2_progressive_plan_validator.py -q   ->  6 passed in 5.05s
$ python3 -m pytest tests/test_005_007_t1_progressive_detail_rule.py -q      ->  5 passed in 0.06s
$ python3 -m pytest tests/test_005_007_t3_open_unit.py -q                    ->  6 passed in 5.83s
$ python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py -q          ->  5 passed in 2.75s
$ python3 -m pytest tests/test_005_007_t6_templates.py -q                    ->  4 passed in 0.82s
$ python3 -m pytest tests/test_005_007_t7_unit_size_and_retries.py -q        ->  4 passed in 0.05s

# batch (misma corrida):
$ python3 -m pytest tests/test_005_007_t{2,1,3,5,6,7}_*.py -q
..............................                                           [100%]
30 passed in 13.35s
```

### 3. Regresiones de área

```
$ timeout 600 python3 -m pytest tests/test_004_003_t3_plan_checks.py tests/test_004_003_t4_validation_fields.py -q
................                                                         [100%]
16 passed in 7.62s

$ timeout 600 python3 -m pytest tests/test_005_003_t6_packet_contract.py tests/test_packet_prepare.py -q
..........................                                               [100%]
26 passed in 18.61s
```

### 4. `git diff --stat` (del commit)

```
$ git show --stat --oneline HEAD
282c70a feat: 005-007 review-fix B1 — la tarea 'planned' exige la clave depends_on (PD-1 acotado)
 skills/cdad-cycle/scripts/cdad_packet.py | 17 +++++++++++++++--
 1 file changed, 15 insertions(+), 2 deletions(-)
```

### 5. Hash del commit

```
$ git rev-parse HEAD
282c70abc04d4d20bd80f06d5a54465623814350
```

Commit **`282c70a`** (prefijo `feat:`), acotado a **`skills/cdad-cycle/scripts/cdad_packet.py`** (dentro del write scope: `implementation` / root `skills`). `tests/**` sin cambios (AP-4).

## Límites / alcance

- No corrí la suite completa (política: la corre **una vez** quien cierra).
- El working tree conserva ` M docs/.cdad-state.json` (dispatch del packet por el orquestador, **preexistente** a este rol; fuera del write scope: no commiteado).
- Sin `--no-verify`, sin push, sin despliegue.
