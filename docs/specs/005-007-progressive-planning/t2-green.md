# GREEN 005-007 T2 — BLOQUEADO por defecto en el oráculo congelado (no es un GREEN verde)

**Packet:** `005-007-progressive-planning-implementer-green-002`
**Contrato:** `docs/specs/005-007-progressive-planning/spec.md` (PD-1, PD-2, INV-5; sha256
`54877103…` — leído, no re-hasheado en esta sesión)
**Rama:** `codex/epic-005-real-operation`

## Resultado en una línea

Implementé la reconciliación del validador (PD-1/PD-2) en
`skills/cdad-cycle/scripts/cdad_packet.py`. **5 de 6** tests del oráculo pasan (los que
exigen el comportamiento progresivo + los 2 controles de regresión). El **6º**
(`TestPd1PlannedFieldNegativesAreRejected::test_pd2_planned_missing_progressive_field_is_rejected`)
**no es satisfacible con el oráculo congelado tal como está**: el fixture `planned_task()`
declara los parámetros `objective`/`uncertainty`/`owner`/`resolves_when` pero **no los usa**
(el dict los hardcodea), así que `planned_task("t1", objective=None)` **NO omite el campo**.
Me detengo y reporto; no edito `tests/` (AP-4 / invariante del rol).

## Qué cambié y dónde

Sólo `skills/cdad-cycle/scripts/cdad_packet.py` (mi write scope `skills`):

1. Constantes nuevas junto a `VALIDATION_STRATEGY_REF`:
   `PLAN_TASK_DETAIL_VALUES = ("next", "planned")`, `PLAN_TASK_DETAIL_PLANNED = "planned"`,
   `PLAN_TASK_PLANNED_FIELDS = ("objective", "uncertainty", "owner", "resolves_when")`.
2. En `_check_plan_validation_plan`, por tarea:
   - `detail` fuera del conjunto cerrado ⇒ `PolicyError` que nombra la tarea y el valor (INV-4).
   - `detail == "planned"` ⇒ valida sus campos propios (`objective`, `uncertainty`, `owner`,
     `resolves_when`, no vacíos) y **no** exige el plan de validación por tarea.
   - `detail == "next"` o sin marcador ⇒ rama de hoy, sin cambios (INV-5).
3. `_check_plan_tasks` **no** se tocó: los checks mecánicos siguen aplicándose a todas las
   tareas declaradas, `planned` incluidas (se ejecutan antes que `_check_plan_validation_plan`).
4. Render del paquete intacto; sin refactor de otras funciones.

## Comando del oráculo y salida

```
python3 -m pytest tests/test_005_007_t2_progressive_plan_validator.py -q
...
FAILED tests/test_005_007_t2_progressive_plan_validator.py::TestPd1PlannedFieldNegativesAreRejected::test_pd2_planned_missing_progressive_field_is_rejected
1 failed, 5 passed in 5.11s
EXIT=1
```

Verdes (comportamiento progresivo + controles):

- `TestPd2ProgressivePlannedIsAccepted::test_pd2_planned_task_without_validation_plan_is_accepted`
- `TestPd2UnknownDetailFailsClosed::test_pd2_detail_outside_closed_set_is_rejected`
- `TestPd2MechanicalChecksApplyToPlanned::test_pd2_mechanical_checks_apply_to_planned_tasks`
- `TestPd2NoMarkerRegression::test_pd2_unmarked_code_task_without_validation_plan_is_rejected`
- `TestPd2NextAndUnmarkedStillAccepted::test_pd2_next_and_unmarked_valid_plans_still_accepted`

Rojo (bloqueante, del fixture):

```
tests/test_005_007_t2_progressive_plan_validator.py:277: in assert_rejected_without_publication
    self.assertNotEqual(
E   AssertionError: 0 == 0 : plan accepted despite a required postcondition: ''
```

## Prueba del defecto (fixture, no implementación)

`planned_task()` (tests/test_005_007_t2_progressive_plan_validator.py:96-141) acepta
`objective=_SENTINEL`, `uncertainty=_SENTINEL`, `owner=_SENTINEL`, `resolves_when=_SENTINEL`
pero **nunca los inyecta en `entry`**: el dict usa strings literales
(`"objective": "Objetivo completo…"`, etc.). El borrado posterior sólo elimina el campo si
`entry[field] is None`, y como el literal nunca es `None`, no se borra nada.

```
$ PYTHONPATH=. python3 -c "from tests.test_005_007_t2_progressive_plan_validator import planned_task as p; import json; print(json.dumps(p('t1', objective=None), sort_keys=True))"
{"consume": [], "depends_on": [], "detail": "planned", "files": [], "id": "t1",
 "objective": "Objetivo completo de la unidad planificada (sin detalle falso).",
 "owner": "orchestrator", "parallel": [], "produce": [{"artifact": "contract-a", "contract": "a-v1"}],
 "resolves_when": "revision de la tanda del epic",
 "uncertainty": "Incertidumbre declarada de la unidad planificada."}
```

Es decir: el "negativo por campo" genera una tarea `planned` **completa** (mismos campos que
el positivo del caso 1, ya verde). Bajo PD-1/AC-1 esa tarea es **ACEPTADA** (rc=0); el test
exige **rechazo**. Luego:

- si se acepta (correcto por contrato) ⇒ `0 == 0`, el test falla;
- si se rechazara, el diagnóstico no podría nombrar el campo `objective` (está presente), y
  los casos 1 y 4 (misma forma, `planned` sin plan de validación) exigen aceptar.

No existe implementación posible que haga pasar este test sin violar PD-1/AC-1 y los casos
1/4 del propio oráculo. Es una contradicción interna del oráculo congelado, no de la
implementación.

## Regresión proporcional del área

```
python3 -m pytest tests/test_004_003_t3_plan_checks.py tests/test_004_003_t4_validation_fields.py tests/test_005_003_t6_packet_contract.py tests/test_packet_prepare.py -q
..........................................                                                               [100%]
42 passed in 24.90s
```

Los cuatro archivos declarados existen y pasan.

## Control explícito de INV-5 (plan sin marcador)

La rama `detail` es aditiva: sin `detail` la decisión es idéntica a hoy. La regresión de
arriba es la prueba — `tests/test_004_003_t3_plan_checks.py`,
`tests/test_004_003_t4_validation_fields.py`, `tests/test_005_003_t6_packet_contract.py` y
`tests/test_packet_prepare.py` usan bloques sin marcador y pasan (42/42). Además, dentro del
propio oráculo, los dos controles "sin marcador" (`TestPd2NoMarkerRegression` y el subTest
"no marker" de `TestPd2NextAndUnmarkedStillAccepted`) pasan. Comportamiento byte a byte del
validador/render sin marcador: conservado.

## git diff --stat

```
 skills/cdad-cycle/scripts/cdad_packet.py | 31 ++++++++++++++++++++++++++++++-
 1 file changed, 30 insertions(+), 1 deletion(-)
```

(`git diff --stat` completo también muestra `docs/.cdad-state.json`, que es escritura de
preparación/despacho del orquestador, fuera de mi write scope: no lo toqué.)

## Commit

**NO commiteé.** El gate GREEN no está satisfecho (el oráculo no está verde) y el defecto es
del test, no de la implementación; commitear presentaría un GREEN no validado. La
implementación queda **lista y sin commitear** en el worktree para revisión del orquestador.
Reejecutar el oráculo tras corregir el fixture es suficiente: **mi código no necesita más
cambios**.

## Fix mínimo propuesto (test-writer; yo no puedo tocar `tests/`)

En `planned_task()` (tests/test_005_007_t2_progressive_plan_validator.py:113-127), wirear los
parámetros en el dict:

```python
"objective": "Objetivo completo de la unidad planificada (sin detalle falso)." if objective is _SENTINEL else objective,
"uncertainty": "Incertidumbre declarada de la unidad planificada." if uncertainty is _SENTINEL else uncertainty,
"owner": "orchestrator" if owner is _SENTINEL else owner,
"resolves_when": "revision de la tanda del epic" if resolves_when is _SENTINEL else resolves_when,
```

Con eso, `planned_task("t1", **{field: None})` omite el campo (queda `None` y el `del` lo
borra) y mi validador lo rechaza nombrando tarea + campo ⇒ los 4 subTests del caso 2 pasan y
el oráculo llega a **6 passed**, sin tocar la implementación.

## Límites honestos (PD-15)

- No corrí la suite completa (política de suite: la corre una vez quien cierra).
- No puedo entregar la evidencia pedida "6 passed": está bloqueada por el defecto del fixture
  descripto arriba; no la fabrico.
- No re-hasheé el sha256 del contrato ni del plan en esta sesión (declarado como leído).
- Si el orquestador prefiere que commitee la implementación igual (para provenance) antes de
  re-despachar al test-writer, lo hago sin cambios de código; queda a su decisión.
