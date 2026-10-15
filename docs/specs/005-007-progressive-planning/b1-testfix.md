#Informe testfix (stage 4 RED, test-writer) — 005-007 B1 acotado
`docs/specs/005-007-progressive-planning/reviewfix-green.md` declare que B2 queda corregido (commit `a86278e`) y se cerró el B1 como defecto de oráculo contrario; este testfix reescribe el oráculo (`tests/test_005_007_reviewfix_blockings.py`) dejando solo los casos entregables: B1 (a)/(b)/(c) sobre la tarea `planned`.

## Adjunto (bloque copiado del testfix)

- **Adjunta en el oraculo `tests/test_005_007_reviewfix_blockings.py`** los casos del packet original sobre el camino `next`/sin marcador:
  -    `b-sin-objective` con variante `detail-next` y `sin-marcador`: el fixture `[next_task("t1")]` es byte-idéntico al que el oraculo congelado de T2 `TestPd2NextAndUnmarkedStillAccepted` (tests/test_005_007_t2_progressive_plan_validator.py:402-417) exige [] (PD-1/PD-2), muerte dura evidenciada por implementer en `docs/specs/005-007-progressive-planning/reviewfix-green.md:22-58` y por mi en para penalizar un defecto no entregable (PD-1/INV-5, spec.md:44,84).
  -    `c-sin-clave-depends_on` sobre tarea no marcada: idem, contradicen PD-2/INV-5 y T2 (`[next_task("t1")]` sin clave).
  El RETIRO queda decisivo en el docstring del módulo con las citas exactas: review.md:23-35 ("Condición de cierre verificable": la review exige la clave `depends_on` a la tarea `planned`, **no** al camino sin marcador) y PD-2/INV-5 (spec.md:44,84). Nadie debe reintroducirlos salvo que el dueño reconcilie PD-1 con PD-2/INV-5.

- **Adjunta en el oraculo los casos del packet `a-planned`**: `(a) planned_task("t1", depends_on=None)` → rechazo rc≠0 naming #t1 + campo con diagnóstico; `(b) planned_task("t1")` con `depends_on=[]` + `objective` no vacío → aceptado (rc=0: la revisión acepta el `[]` explícito, review.md:33).

## Evidencia de corrida (salida real)

```
$ cd <repo>
$ git log --oneline -3 -- tests/test_005_007_reviewfix_blockings.py
e3375e4 test: 005-007 review-fix B1 acotado al camino planned (retiro por contradiccion con PD-2/INV-5 y T2 congelado)
2cd13a6 test: 005-007 RED de review-fix — un test por hallazgo bloqueante B1 (PD-1) y B2 (PD-9)
b7dadd4 (registro previo de T1..T7)
```

### A) Corrida del oráculo (estado post-commit `e3375e4`):

```
$ python3 -m pytest tests/test_005_007_reviewfix_blockings.py tests/test_005_007_t2_progressive_plan_validator.py -q

    FAILED tests/test_005_007_reviewfix_blockings.py::TestB1TaskAlwaysDeclaresObjectiveAndDependsOn::test_b1_pd1_planned_task_always_declares_depends_on
   AssertionError: 0 == 0 : plan aceptado pese a la postcondición PD-1 exigida (hallazgo B1): ''
E                       assert 0 == 0 ... 
1 failed, 7 passed in 7.13s
```

- ** Fallo correcto (RED)**: la versión de la tarea `planned` sin la clave `depends_on` (**snapshot del fixture en `_B1ValidatorCase.assert_rejected_without_publication`**) recibe `rc=0` hoy (la implementación no rechaza; el oráculo espera `rc≠0` con `ERROR:`). El fallo es genuinamente una `AssertionError` en la postcondición PD-1 (**no** por ImportError ni sintaxis), como el packet pide.
- ** Sin nuevos verdes**: `7 passed` = B2 (TestB2WrappedInvocationIsObservedDispatch, 1 test) + oráculo T2 congelado (7 test cases (`TestPd2ProgressivePlannedIsAccepted`, `TestPd1PlannedFieldNegativesAreRejected`, `TestPd2UnknownDetailFailsClosed`, `TestPd2MechanicalChecksApplyToPlanned`, `TestPd2NoMarkerRegression`, `TestPd2NextAndUnmarkedStillAccepted`)). Ningún control T2 fue tocado (INV-5 respaldado por referee).

### B) `git diff --stat` del commit (acotado a `tests/`):

```
 tests/test_005_007_reviewfix_blockings.py | 142 +++++++++++++++++-------------
 1 file changed, 80 insertions(+), 62 deletions(-)
```

### C) Hash del commit

```
$ git rev-parse HEAD
e3375e42004e98568933d01be6e239fe1891c0f4
```
