# Review-fix (etapa 4, GREEN) — 005-007-progressive-planning · implementer

**Packet:** `005-007-progressive-planning-implementer-review-fix-001` · **Ejecución:** `exec-005-007-progressive-planning-001` · **Rol:** implementer · **Substage:** `review-fix`.
**Contrato:** `docs/specs/005-007-progressive-planning/spec.md` — sha256 `54877103d622ca75994b503ee4be016bf39682c2c6a6f89962a8436d8d309a4a` ✅. **Review:** `review.md` (B1, B2). **Oraculo congelado:** `tests/test_005_007_reviewfix_blockings.py` (commit del test-writer `2cd13a6`).

## Resultado

- **B2 → CORREGIDO, oráculo verde.** `TestB2WrappedInvocationIsObservedDispatch` **1 passed**; oráculos previos T2/T3/T5/T6/T7 **25 passed**; regresiones del área **28 passed**; regresiones de contrato de paquete **26 passed**.
- **B1 → BLOQUEADO: el oráculo congelado es insatisfacible.** No implementé B1 (ver evidencia). Se requiere decisión test/contrato del orquestador.
- `tests/**` NO tocado (AP-4). `skills/cdad-cycle/scripts/cdad_packet.py` quedó **sin cambios** (diff vacío).

## B2 — lo que cambié (PD-9)

`skills/cdad-cycle/scripts/cdad_context_meter.py`:

- Nuevo resolutor `_segment_resolution(tokens, depth=0) -> (programa, tokens_de_la_invocación)`: parte del rol de `_segment_program` y **pela los prefijos de ENVOLTURA conocidos** `time`, `env`, `nohup`, `nice`, `ionice`, `stdbuf`, `command`, `timeout` (con su duración), `sudo`; resuelve el prefijo de intérprete (`python3 prog.py` → `prog.py`) y, ante un intérprete de shell con `-c "<command>"`, vuelve a resolver el comando citado **una sola vuelta** (cota `depth < 1`, sin recursión infinita), uniendo los tokens internos a los de la invocación.
- `_skip_wrapper(...)`: descarta las banderas de cada envoltura y sus argumentos (`_WRAPPER_ARGUMENT_FLAGS`) y el operando de duración de `timeout`.
- `_delegation_call_kind` usa `_segment_resolution` y clasifica la ayuda (`--help`/`-h`) sobre **todos** los tokens de la invocación (incluidos los internos del `-c`).
- La **clase de envoltura queda DECLARADA** en `DELEGATION_DISPATCH_METHOD` y `DELEGATION_DISPATCH_PROVENANCE` (constantes que el registro emite en `reader.dispatch_recognition` y en el `method` del hito observado).
- Conservados: la **no-detección de meras menciones** (`grep`/`write`), la exclusión de ayuda y la **byte-identidad del registro neutral SIN la bandera** (`--delegation-dispatch`).

## B1 — BLOCKER: el oráculo congelado es insatisfacible (evidencia dura)

El objetivo del packet pide exigir, para TODA tarea declarada, `objective` no vacío y la clave `depends_on`. Es **imposible** satisfacerlo junto con los oráculos que el propio packet declara «no deben romperse», porque **el fixture es byte-idéntico** en dos aserciones opuestas:

```
$ PYTHONPATH=. python3 /tmp/opencode/b1_conflict_probe.py
reviewfix control bytes == reviewfix case b 'sin-marcador' bytes: True
has 'objective' key in next_task('t1'): False
```

- `tests/test_005_007_reviewfix_blockings.py:187-193` (`prepare_valid_control`) escribe `[next_task("t1")]` y exige **ACEPTADO**.
- `tests/test_005_007_reviewfix_blockings.py:215-225` (caso `b-sin-objective`, variante `sin-marcador`) escribe `[next_task("t1")]` y exige **RECHAZADO** por `objective`.
- El helper `next_task("t1")` (congelado de T2, reusado verbatim) **no declara** `objective`.
- El oráculo **congelado** `tests/test_005_007_t2_progressive_plan_validator.py:402-417` (`TestPd2NextAndUnmarkedStillAccepted`) exige **ACEPTADO** el mismo fixture (variantes `detail-next` y `sin-marcador`), y su propio `prepare_valid_control` (`:267-272`) también.

Experimento (aplicando el B1 del packet —`objective`+`depends_on` para todas las tareas— y luego revertido):

```
$ # patch temporal en _check_plan_validation_plan (revertido; cdad_packet.py sin diff)
$ python3 -m pytest tests/test_005_007_reviewfix_blockings.py::TestB1... -q
AssertionError: 2 != 0 : la superficie honesta fue rechazada (control roto):
ERROR: plan task 't1' declares no non-empty objective (PD-1)
1 failed

$ python3 -m pytest tests/test_005_007_t2_progressive_plan_validator.py -q
6 failed   # TODOS los tests de T2 (su control usa next_task sin objective)
```

Raíz: **contradicción de contrato en la spec aprobada**.
- **PD-1** (`spec.md:42`): «Toda tarea declara **siempre** un `objective` no vacío y sus `depends_on`.»
- **PD-2** (`spec.md:44`) / **INV-5** (`spec.md:84`): «Un bloque sin el marcador se comporta **exactamente** como hoy» / «Sin el campo `detail`, el bloque `plan-tasks` … idénticos a hoy».

El oráculo T2 (etapa 3, congelado) codifica PD-2/INV-5 para las tareas `next`/sin marcador; el oráculo de review-fix codifica PD-1. Ninguna implementación puede satisfacer ambos. Además, la review formal (B1, `review.md:23-35`) **acota** el hallazgo a la tarea `planned` sin `depends_on` y dice explícitamente «No se requiere tocar el camino sin marcador (INV-5)»; el packet amplía B1 a `objective`/`depends_on` para **todas** las tareas.

**Decisión requerida (orquestador/test-writer), no del implementer (anti-gaming: quien construye no edita su validador):**
1. Si PD-1 manda: el test-writer debe (a) dar `objective` al fixture de control del review-fix (`prepare_valid_control`) y a `next_task`/T2 (`TestPd2NextAndUnmarkedStillAccepted` y el control de T2), y (b) el dueño debe reconciliar PD-1 con PD-2/INV-5 (el bloque sin marcador dejaría de comportarse «exactamente como hoy»). Con eso, B1 se implementa de inmediato.
2. Si PD-2/INV-5 manda (mi lectura de la review): B1 se acota a `planned` → `depends_on` presente (lista; `[]` válido) + `objective` no vacío para la tarea marcada; los casos `b-sin-objective/sin-marcador` y `c-sin-clave-depends_on` del review-fix (que tocan el camino sin marcador) se retiran o se reescriben. Es el único cambio de `cdad_packet.py` que no rompe T2.

No apliqué ninguna de las dos sin decisión para no romper un oráculo congelado que el packet declara intocable.

## Comandos y salidas (evidencia obligatoria)

```
$ timeout 300 python3 -m pytest tests/test_005_007_reviewfix_blockings.py -q
FAILED tests/test_005_007_reviewfix_blockings.py::TestB1TaskAlwaysDeclaresObjectiveAndDependsOn::test_b1_pd1_task_always_declares_objective_and_depends_on
1 failed, 1 passed in 2.43s

$ timeout 300 python3 -m pytest tests/test_005_007_reviewfix_blockings.py::TestB2WrappedInvocationIsObservedDispatch -q
1 passed in 1.82s

$ timeout 300 python3 -m pytest tests/test_005_007_t2_progressive_plan_validator.py tests/test_005_007_t5_delegation_dispatch.py tests/test_005_007_t3_open_unit.py tests/test_005_007_t6_templates.py tests/test_005_007_t7_unit_size_and_retries.py -q
25 passed in 13.01s

$ timeout 300 python3 -m pytest tests/test_004_003_t3_plan_checks.py tests/test_004_003_t4_validation_fields.py tests/test_005_002_t2_milestones.py tests/test_005_002_t1_neutral_record.py -q
28 passed in 12.16s

$ timeout 300 python3 -m pytest tests/test_005_003_t6_packet_contract.py tests/test_packet_prepare.py -q
26 passed in 18.02s
```

Los `25 passed` de T2..T7 confirman que **T2/T5/T3/T6/T7 no se rompieron**; el único rojo es el caso B1 del oráculo de review-fix (defecto de oráculo descrito), no por mi cambio.

## Diff y commit

```
$ git show --stat --oneline HEAD
a86278e feat: 005-007 review-fix B2 — el medidor resuelve la invocación envuelta (PD-9)
 skills/cdad-cycle/scripts/cdad_context_meter.py | 132 ++++++++++++++++++++----
 1 file changed, 113 insertions(+), 19 deletions(-)

$ git rev-parse HEAD
a86278eaf33904f4a8d2cc08c79f5025afa69993
```

Commit `a86278e` (prefijo `feat:`), **acotado a `skills/cdad-cycle/scripts/cdad_context_meter.py`**. `skills/cdad-cycle/scripts/cdad_packet.py` **sin cambios** (diff vacío tras revertir el experimento).

## Límites / alcance

- `tests/**` NO editado (AP-4, invariante del packet). `docs/specs/005-007-progressive-planning/**` NO editado (fuera del write scope: `implementation` / root `skills`).
- El working tree conserva ` M docs/.cdad-state.json`, **preexistente** (declarado en `reviewfix-red.md:74`); no fue commiteado por este rol.
- No corrí la suite completa (política: la corre **una vez** quien cierra).
- B1 queda abierto por defecto del oráculo congelado; se reporta con evidencia reproducible, sin workaround ni edición de tests.
