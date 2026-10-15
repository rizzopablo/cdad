# Informe testfix — 005-007 T2 (packet 005-007-progressive-planning-test-writer-red-003, substage red)

Actor: test-writer (sesion aislada). Contrato: docs/specs/005-007-progressive-planning/spec.md
(sha256 54877103d622ca75994b503ee4be016bf39682c2c6a6f89962a8436d8d309a4a — verificado en el arbol;
refs aplicables PD-1/PD-2 confirmadas en el spec §6/D1 antes de tocar el fixture).

## Defecto corregido

`tests/test_005_007_t2_progressive_plan_validator.py` @ 07abeb2 (commit / gate detectado):
el helper `planned_task(...)` aceptaba los kwargs `objective/uncertainty/owner/resolves_when`
pero NUNCA los usaba: los escribia hardcodeados en `entry`, por lo que el bucle borrador final
(`if entry[field] is None: del entry[field]`) no se disparaba nunca para esos cuatro campos.
Resultado: un campo pedido como ausente (`None`) quedaba PRESENTE con su default; el fixture
negativo era identico al positivo y el caso no probaba lo que declaraba (PD-1).

## Cambio (lado test unicamente; Nothing fuera de tests/)

- Signatura e intencion documentada del helper PRESERVADAS: `_SENTINEL` = default;
  explicito = valor tal cual; `None` = la clave queda REALMENTE ausente.
- Negativos sin tocar; positivos (`PLANNED_ONLY_TASKS`, `MIXED_MATCHED_TASKS`, controles de
  regresion) sin cambios semanticos: re-verificados con el mismo dict que antes.
- Cada caso seguira mapeado a PD-1/PD-2: la tarea `"planned"` sin uno de sus cuatro campos
  debe ser RECHAZADA (rc != 0, `ERROR: ...`, stdout vacio, sin publicar, estado/arbol
  inmutables) con diagnostico que nombre la tarea y el campo.

## Evidencia 1 — el fixture ahora SI omite el campo (dict del helper, no test nuevo)

```
$ python3 -c "from tests.test_005_007_t2_progressive_plan_validator import planned_task; print(planned_task('t1', **{'objective': None}))"
{'id': 't1', 'detail': 'planned', 'produce': [{'artifact': 'contract-a', 'contract': 'a-v1'}], 'consume': [], 'depends_on': [], 'parallel': [], 'files': [], 'uncertainty': 'Incertidumbre declarada de la unidad planificada.', 'owner': 'orchestrator', 'resolves_when': 'revision de la tanda del epic'}
$ python3 -c "from tests.test_005_007_t2_progressive_plan_validator import planned_task; print(planned_task('t1', **{'resolves_when': None}))"
{'id': 't1', 'detail': 'planned', 'produce': [{'artifact': 'contract-a', 'contract': 'a-v1'}], 'consume': [], 'depends_on': [], 'parallel': [], 'files': [], 'objective': 'Objetivo completo de la unidad planificada (sin detalle falso).', 'uncertainty': 'Incertidumbre declarada de la unidad planificada.', 'owner': 'orchestrator'}
# positivo sin cambio de forma:
{'id': 't1', 'detail': 'planned', 'produce': [{'artifact': 'contract-a', 'contract': 'a-v1'}], 'consume': [], 'depends_on': [], 'parallel': [], 'files': [], 'objective': 'Objetivo completo de la unidad planificada (sin detalle falso).', 'uncertainty': 'Incertidumbre declarada de la unidad planificada.', 'owner': 'orchestrator', 'resolves_when': 'revision de la tanda del epic'}
```

## Evidencia 2 — corrida del oraculo focal

```
$ python3 -m pytest tests/test_005_007_t2_progressive_plan_validator.py -v
6 passed in 5.93s
```

(6/6 PASSED: caso PD-1/PD-2 positivo, el caso negativo corregido
`test_pd2_planned_missing_progressive_field_is_rejected` con 4 subTest — objective /
uncertainty / owner / resolves_when —, fail-closed `detail` fuera del conjunto cerrado,
checks mecanicos, y los 2 controles de regresion.)

## Evidencia 3 — diff y commit

```
$ git diff --stat -- tests/
 tests/test_005_007_t2_progressive_plan_validator.py | 15 ++++++++++-----
 1 file changed, 10 insertions(+), 5 deletions(-)
$ git log --oneline -1
7d683c9 test: fix 005-007 T2 oracle fixture — planned_task omits a field named as absent (None=omit), negatives now test PD-1 truly
```

Commit: **7d683c9** (branch `codex/epic-005-real-operation`, solo el archivo de tests;
nada mas commiteado).

## Declaracion honesta del estado del arbol

La implementacion de T2 esta **SIN COMMITEAR** en el arbol: el cambio del implementer
(`skills/cdad-cycle/scripts/cdad_packet.py`, modificado, no leido ni tocado — front de
fase), que no commiteo porque el gate no estaba verde. Esta corrida mide **con esa
implementacion presente**: por eso los casos ahora pasan sustantivamente (el fixture
realmente omite el campo y el validador lo rechaza como corresponde). El RED corregido
debe verificarse contra HEAD **sin** esa implementacion, en un worktree fijado —
verificacion del orquestador, no de esta sesion.

## Limites declarados

- No se corrio la suite completa: policy de suite (el closer la corre una vez al cierre);
  correccion local, validacion = pruebas focales per el validation plan.
- No se leyo codigo de implementacion en ningun momento (`skills/`, `scripts/` invisible;
  la correccion deriva del contrato y del defecto medido por el orquestador).
