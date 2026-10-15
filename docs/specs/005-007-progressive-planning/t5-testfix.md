# Informe del testfix — 005-007 T5 (packet 005-007-progressive-planning-test-writer-red-007)

Rol: test-writer · substage: red · alcance de edición: `tests/`. Ningún archivo fuera de
`tests/` fue editado por este rol. No se leyó código de implementación
(`scripts/cdad_context_meter.py`): el único contacto con él fue la observación black-box
de la salida del wrapper — el propio contrato del oráculo (subproceso, nunca import).

## 1. Defecto corregido

Oráculo `tests/test_005_007_t5_delegation_dispatch.py` (commit b3044b1). Causa (medida por
el orquestador, confirmada en mi baseline): `run_with_flag` devuelve lo que produce
`parse_session` — el DOCUMENTO completo (`doc`) — y los casos 1 (a), 1 (b), 2 y 3 lo
pasaban como `session` al helper `milestone(session, key, ctx)` (línea ~504), que hace
`session.get("milestones")`. El documento no tiene `milestones` (lo tiene cada entrada de
`sessions[]`), así que los tres casos fallaban con
`AssertionError: None is not an instance of <class 'dict'> : milestones es objeto` —
un AssertionError del HELPER, no del contrato — antes de ejercitar el comportamiento.

## 2. Cambio (solo extracción; cero aserciones cambiadas, cero casos agregados/quitados)

`git diff --stat` (HEAD c8e766d respecto de b3044b1, vía el diff del commit, ya que el
baseline se tomó del árbol):
```
 tests/test_005_007_t5_delegation_dispatch.py | 18 +++++++++++++-----
 1 file changed, 13 insertions(+), 5 deletions(-)
```

Cuatro sitios de llamada ahora extraen la entrada de sesión que `parse_session` ya validó
única y existente:

- Caso 1 (a): `doc_a = self.run_with_flag(...)` → `session = doc_a["sessions"][0]`
- Caso 1 (b): `doc_b = self.run_with_flag(...)` → `session = doc_b["sessions"][0]`
- Caso 2 (mención): `doc_mention = self.run_with_flag(...)` → `session = doc_mention["sessions"][0]`
- Caso 3 (ayuda): `doc_help = self.run_with_flag(...)` → `session = doc_help["sessions"][0]`

SIN cambios en: los helpers (`run_with_flag`, `parse_session`, `milestone`,
`measure_leaf`), todas las aserciones de contrato, los docstrings, los fixtures y los
casos 4 y 5 (que ya extraían correctamente: caso 4 usa `doc["sessions"][0]` tras
`parse_session`; caso 5 trabaja a nivel documento y sesión según la postcondición).

## 3. Evidencia de que la sesión ahora se extrae (una corrida real sobre el fixture
`delegate-skills` con `--delegation-dispatch`, sin importar el módulo del medidor)

```
EVIDENCIA EXTRACCION (testfix 007):
  doc: tipo=dict, claves-primer-nivel=['meter', 'reader', 'roles', 'run', 'schema_version', 'sessions', 'unknowns', 'window']
  doc['sessions']: tipo=list, len=1
  sesion devuelta doc['sessions'][0]: tipo=dict, claves-primer-nivel=['buckets', 'measures', 'milestones', 'model', 'parent_ref', 'role', 'runtime_version', 'session_ref', 'window']
  sesion tiene 'milestones': True (claves=['first_dispatch', 'first_resume'])
```

El objeto que ahora reciben los casos es el dict de la entrada de sesión, con
`milestones` presente — exactamente lo que `parse_session` ya valida (existe y es única).

## 4. Comandos exactos y salidas

(a) BASELINE ANTES del fix:
```
$ python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py -v
...
E   AssertionError: None is not an instance of <class 'dict'> : PD-9 caso 2: milestones es objeto
E   AssertionError: None is not an instance of <class 'dict'> : PD-9 caso 3: milestones es objeto
(ídem en el subtest del caso 1)
=========================== short test summary info ============================
FAILED tests/test_005_007_t5_delegation_dispatch.py::TestRealInvocationObserved::test_pd9_real_delegation_invocation_reports_observed_dispatch
FAILED tests/test_005_007_t5_delegation_dispatch.py::TestMentionIsNotDispatch::test_pd9_mention_only_reports_absent_with_honest_cause
FAILED tests/test_005_007_t5_delegation_dispatch.py::TestHelpCallIsNotDispatch::test_pd9_help_calls_report_absent_with_honest_cause
========================= 3 failed, 2 passed in 2.27s ==========================
```
Los tres fallos se detienen en `milestone` (línea 506): defecto del helper, no del contrato.

(b) DESPUÉS del fix, en el árbol (donde la implementación de T5 está SIN COMMITEAR):
```
$ python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py -v
...
tests/test_005_007_t5_delegation_dispatch.py::TestRealInvocationObserved::test_pd9_real_delegation_invocation_reports_observed_dispatch PASSED [ 20%]
tests/test_005_007_t5_delegation_dispatch.py::TestMentionIsNotDispatch::test_pd9_mention_only_reports_absent_with_honest_cause PASSED [ 40%]
tests/test_005_007_t5_delegation_dispatch.py::TestHelpCallIsNotDispatch::test_pd9_help_calls_report_absent_with_honest_cause PASSED [ 60%]
tests/test_005_007_t5_delegation_dispatch.py::TestNeutralRecordByteIdentity::test_pd9_inv5_neutral_record_identical_and_subagent_task_unchanged PASSED [ 80%]
tests/test_005_007_t5_delegation_dispatch.py::TestRecordDeclaresSetAndMethod::test_pd9_record_declares_recognized_set_method_and_provenance PASSED [100%]
============================== 5 passed in 2.62s ===============================
```

(c) VERIFICACIÓN del lado RED — worktree efímero al HEAD `c8e766d` (la implementación de
T5 NO está ahí porque está sin commitear):
```
$ git worktree add /tmp/opencode/wt-head-007 HEAD && cd /tmp/opencode/wt-head-007 \
  && python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py -v
...
FAILED ...TestRealInvocationObserved::test_pd9_real_delegation_invocation_reports_observed_dispatch
FAILED ...TestMentionIsNotDispatch::test_pd9_mention_only_reports_absent_with_honest_cause
FAILED ...TestHelpCallIsNotDispatch::test_pd9_help_calls_report_absent_with_honest_cause
FAILED ...TestRecordDeclaresSetAndMethod::test_pd9_record_declares_recognized_set_method_and_provenance
========================= 4 failed, 1 passed in 1.85s ==========================
```
Los 4 fallos son AssertionError del oráculo (guard de RED en `run_with_flag`, línea 467),
p. ej.: «RED PD-9 caso 5 (a): la bandera nueva declarada `--delegation-dispatch` no es
aceptada aún por el medidor — comportamiento ausente (PD-9/AC-4) … AssertionError de RED,
nunca ImportError». El caso 4 (control INV-5) pasa: `1 passed`. Limpieza:
`git worktree remove --force /tmp/opencode/wt-head-007 && git worktree prune` (sin rastros).

## 5. Estado honesto del árbol y del par RED/GREEN

- Árbol: la implementación de T5 (`skills/cdad-cycle/scripts/cdad_context_meter.py`) y dos
  archivos de documentación del orquestador (`docs/.cdad-state.json`,
  `skills/cdad-cycle/references/context-meter.md`) están SIN COMMITEAR — estado
  preexistente del fix-loop del GREEN. Mi commit NO los toca (`git show --stat HEAD`
  abajo). `git status` posterior al commit no muestra ningún archivo nuevo modificado
  por este rol.
- Par RED/GREEN que el orquestador puede verificar en un worktree al HEAD:
  - RED (a HEAD): 4 failed (AssertionError — comportamiento ausente: la bandera no es
    aceptada) + 1 passed (control INV-5). Igual cualitativamente al RED registrado con el
    oráculo defectuoso (4 failed + 1 control), pero ahora las 4 fallas renacen en la
    guardia de RED por la BANDERA, no en el helper.
  - GREEN (en este árbol, con la implementación sin commitear y el oráculo corregido):
    5 passed — los tres casos corregidos ahora SÍ ejercitan el contrato real: detección
    de la invocación real (posición call_index/seq/time_relative, estado `observed`,
    método declarado), no-detección por mención con causa honesta, no-detección de ayuda,
    byte-identidad del registro neutral y declaración del conjunto con método/procedencia.

## 6. Modified files, commit

- Archivo modificado (único): `tests/test_005_007_t5_delegation_dispatch.py`
- Commit: `c8e766d`
  `test: 005-007 T5 testfix - los casos reciben la ENTRADA de sesion (doc['sessions'][0]) que parse_session ya valida, no el documento completo: el helper milestone(session,...) exige session.get('milestones'); el defecto del helper en b3044b1 hacia fallar los 3 casos por AssertionError del helper antes de ejercitar el contrato`
- `git show --stat HEAD`: `tests/test_005_007_t5_delegation_dispatch.py | 18 +++++++++++++-----
  1 file changed, 13 insertions(+), 5 deletions(-)`

## 7. Notas

- Validación ampliada NO requerida: corrección local de la extracción del propio oráculo
  focal T5 → prueba focal (solo el archivo del oráculo), sin suite completa (política de
  suite del common: quien cierra la corre una vez). Los regresiones declarados
  (`test_005_002_t2/t4/t1`) no se vieron afectados por este cambio (no toca el medidor ni
  su invocación: mismos argv, mismos fixtures; solo cambia qué objeto extraen los casos 1-3).
- Sin aserciones nuevas ni mensajes nuevos: lo que se verifica quedó intacto (el contrato
  del oráculo no cambió); solo cambió de QUÉ objeto se extraen `milestones`/`measures`.
- Honestidad: el GREEN (5 passed) es contra la implementación SIN COMMITEAR; el RED
  (4 failed + 1 control) está medido directamente en worktree al HEAD. Ambos con salida
  completa arriba.
