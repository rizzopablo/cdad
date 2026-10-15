# Informe GREEN — 005-007 T3: `open-unit` (PD-7) + dependencias declaradas (obs 2)

**Role:** implementer · **Substage:** green · **Packet:** `005-007-progressive-planning-implementer-green-004` · **Execution:** `exec-005-007-progressive-planning-001`
**Contrato:** `docs/specs/005-007-progressive-planning/spec.md` (PD-7, PD-12; AC-2) + `plan.md` ficha T3 + `review-claude-spec-2026-10-13.md` obs 2.
**Commit GREEN:** `54eeed6` (rama `codex/epic-005-real-operation`). `tests/` intacto (AP-4).

## 1. Qué cambié y dónde

Todos los cambios bajo el write scope declarado (`implementation`, root `skills`):

1. `skills/cdad-cycle/scripts/cdad_packet.py` (+151/-3):
   - Subcomando nuevo `open-unit` (`--project-root`, `--feature <ID>`), registrado en `build_parser()` y despachado en `main()`.
   - `open_unit()`: precondición de reposo (`_validate_idle_coherence`; con una unidad ya abierta rechaza nombrando `active_feature`), selección (primera `queued` del orden de `epic_features`, o `--feature` que debe existir y estar `queued`), verificación de `depends_on` declaradas (`_check_open_unit_dependencies`), efecto atómico (`active_feature`, entrada `in-progress`+`opened_at`, `current_stage=discovery`, `epic_stage` intacto), reuso de `_bootstrap_v2_execution` para la ejecución y `_validate_v2_state` antes de escribir; publicación con `_publish_owned_atomically` bajo `_ProjectLock`.
   - `_next_route`: la ruta `next-unit` de la vista `status` NOMBRA la operación (`open-unit`).
   - NO toqué `prepare`, el render de paquetes ni validaciones existentes.
2. `skills/cdad-cycle/references/project-start.md` (+20): sección `### 6.1 ... open-unit` que documenta la operación POR REFERENCIA (spec PD-7, asset de ejemplos, `orientation.md`), sin duplicar el procedimiento.
3. `skills/cdad-cycle/references/orientation.md` (+6/-1): fila en la tabla «Frequent operations» y mención del ejemplo `open-unit` en el asset.
4. `skills/cdad-cycle/assets/orientation-examples.json` (+12): ejemplo localizable por el asset (`id: "open-unit"`, `kind: "unit-open-invocation"`, `command: [... open-unit --project-root <ABS>]`).

Autoridad conservada: `stage_history`, `approver`, `hitl_delegation`, `version` y `docs/cdad-policy.json` quedan idénticos (test 4 de la focal).

## 2. Oráculo congelado (verde)

```
$ python3 -m pytest tests/test_005_007_t3_open_unit.py -q
......                                                                   [100%]
6 passed in 5.39s
```

## 3. Regresión proporcional (declarada por la ficha T3)

| Test | Resultado |
|---|---|
| `tests/test_005_003_t1_compact_view.py` | 11 passed in 6.44s |
| `tests/test_005_003_t2_examples_execute.py` | 10 passed in 1.94s |
| `tests/test_005_003_f2_idle_history.py` | 3 passed in 1.41s |
| `tests/test_005_001_t3_idle.py` | 4 passed in 8.07s |

Comando por archivo: `python3 -m pytest <archivo> -q`.

## 4. Validación ampliada (el cambio toca un contrato compartido)

`cdad_packet.py` (CLI: bootstrap/status/prepare) y `project-start.md` (documento compartido) → amplié la validación:

```
$ python3 -m pytest tests/test_005_006_t1_start_procedure.py tests/test_005_006_t2_intake.py \
    tests/test_005_006_t3_epic_features.py tests/test_005_006_t4_readme.py \
    tests/test_005_006_t5_acceptance.py tests/test_005_006_t6_owner_reviewfix.py -q
36 passed in 1.74s

$ python3 -m pytest tests/test_004_002_t2_bootstrap.py tests/test_packet_prepare.py \
    tests/test_005_003_t6_packet_contract.py tests/test_005_007_t2_progressive_plan_validator.py \
    tests/test_004_003_t3_plan_checks.py tests/test_004_003_t4_validation_fields.py -q
65 passed in 36.02s
```

## 5. Ejecución del ejemplo del asset

Localizado por el asset (**no** por prosa) y ejecutado contra un proyecto sintético en reposo (tempdir, HOME aislado). Script desechable `/tmp/opencode/run_t3_example.py`:

```
$ python3 /tmp/opencode/run_t3_example.py
ASSET EXAMPLE id     : open-unit
ASSET EXAMPLE kind   : unit-open-invocation
ASSET EXAMPLE target : docs/.cdad-state.json
ARGV                 : python3 <skill-dir>/scripts/cdad_packet.py open-unit --project-root <ABS>
RC                   : 0
STDOUT               :
opened unit '005-007-progressive-planning': active_feature=005-007-progressive-planning current_stage=discovery execution=exec-005-007-progressive-planning-001
no declared dependencies for '005-007-progressive-planning'; the plan order is the authority (dependencies not verified)
EFFECT active_feature: 005-007-progressive-planning
EFFECT current_stage : discovery
EFFECT entry status  : in-progress opened_at: 2026-10-13T05:42:42.959193+00:00
```

## 6. Diff y commit

```
$ git show --stat --oneline HEAD
54eeed6 feat: 005-007 T3 open-unit abre la primera unidad queued del plan por CLI (PD-7) + ruta status la nombra + dependencias declaradas (obs 2)
 skills/cdad-cycle/assets/orientation-examples.json |  12 ++
 skills/cdad-cycle/references/orientation.md        |   6 +-
 skills/cdad-cycle/references/project-start.md      |  20 +++
 skills/cdad-cycle/scripts/cdad_packet.py           | 151 ++++++++++++++++++++-
 4 files changed, 186 insertions(+), 3 deletions(-)
```

`git status --short` → ` M docs/.cdad-state.json` (runtime del ciclo, ajeno a esta sesión; **no** lo toqué ni lo commiteé).

## 7. Límites honestos

- La suite completa **no** la corrí (política: la corre una vez quien cierra). Verifiqué: focal + 4 regresiones declaradas + 101 tests del contrato compartido (005-006 doc de arranque; bootstrap/prepare/packet/T2).
- Los tests son caja negra (subprocess); no inspeccionan la implementación.
- `depends_on` es un campo de la entrada `epic_features` (representación que la sonda del RED confirmó tolerada hoy por el validador). Si se adoptara otra representación, obs 2 se re-discute con el contrato.
- No se tocó HOME real, ni la base real de sesiones, ni `--no-verify`; sin push.

Status: GREEN registrado — 6/6 focales verdes, regresiones y ampliación verdes, ejemplo del asset ejecutado (rc=0), commit `54eeed6`.
