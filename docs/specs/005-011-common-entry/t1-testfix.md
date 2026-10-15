# Informe — test-writer RED, corrección acotada del oráculo T1 (005-011-common-entry)

- **Paquete:** `005-011-common-entry-test-writer-red-002` (etapa 3, subetapa `red`).
- **Rol:** test-writer. Solo se editó `tests/`. No se leyó implementación; el CLI se usó como caja negra (subprocess).
- **Contrato:** `docs/specs/005-011-common-entry/spec.md` (sha256 `37cd4593…c610bc`), PD-2/PD-3, §2.2/§5 AC-2/AC-3.
- **Focal:** `tests/test_005_011_t1_relative_root.py`.

## 1. Defecto confirmado (medido, antes de corregir)

`test_pd2_relative_root_consistent_across_subcommands` invocaba `validate-state --project-root .`
sobre el fixture SIN prepararlo. `build_project` deja `execution: None` y `validate-state` exige
un binding activo, así que fallaba cerrado por el binding, independientemente de la raíz:

```
$ python3 -m pytest tests/test_005_011_t1_relative_root.py -q
.F...                                                                    [100%]
...
E       AssertionError: PD-2 violada: `validate-state --project-root .` debe resolver la raíz relativa
contra el cwd (rc=0); hoy rc=2; stderr='ERROR: no active execution binding in state: state.execution is empty'
1 failed, 4 passed in 5.76s
```

La aserción `rc=0` no dependía de la resolución de la raíz → insatisfacible con el cambio declarado,
y satisfacerla relajando `validate-state` violaría PD-2 y el oráculo verde preexistente
`tests/test_005_001_t3_idle.py`.

## 2. Corrección aplicada (mínima, sin debilitar el oráculo)

Un solo archivo, `tests/test_005_011_t1_relative_root.py` (+24 −3), en `test_pd2_relative_root_consistent_across_subcommands`:

1. **Setup del fixture:** se agrega `fx.prepare()` (el propio helper del fixture, ya usado por el
   test #5) al inicio del test, con su aserción de éxito. El rechazo de un estado SIN binding queda
   como oráculo de `tests/test_005_001_t3_idle.py`: no se toca.
2. **Equivalencia relativa-vs-absoluta explícita para `validate-state`:** se corre la raíz absoluta
   como control y se afirma `relative.returncode == absolute.returncode` (además del veredicto
   `VALID`). La aserción ahora depende de la resolución de la RAÍZ, no del binding.
3. **`validate-policy` conservado tal cual** (rc=0 + veredicto `VALID` con raíz relativa).

No se tocó implementación, ni otros tests, ni el propósito del test.

## 3. Evidencia

### 3.1 Focal completo (verde, tras la corrección)

```
$ python3 -m pytest tests/test_005_011_t1_relative_root.py -q
.....                                                                    [100%]
5 passed in 4.32s
```

### 3.2 El oráculo no es vacuo (falsificación medida del comportamiento pre-GREEN)

Con el método que el plan sanciona (worktree, nunca `git stash`), se corrió el test corregido contra
el CLI **pre-fix** (commit `61d100e`, padre del GREEN `53413b3`), en un worktree temporal
`/tmp/opencode/wt-005-011-t1prefix` (ya removido; árbol compartido intacto):

```
$ git worktree add --detach /tmp/opencode/wt-005-011-t1prefix 61d100e
$ cp tests/test_005_011_t1_relative_root.py /tmp/opencode/wt-005-011-t1prefix/tests/
$ cd /tmp/opencode/wt-005-011-t1prefix && python3 -m pytest tests/test_005_011_t1_relative_root.py -q -k relative_root_consistent
E       AssertionError: PD-2 violada: `validate-state --project-root .` debe resolver la raíz relativa
contra el cwd y dar el MISMO veredicto que la raíz absoluta; hoy rc=2 != 0;
stderr='ERROR: --project-root must be an absolute existing directory: .'
1 failed, 4 deselected in 0.73s
$ git worktree remove --force /tmp/opencode/wt-005-011-t1prefix
```

Falla por el motivo correcto: AssertionError sobre la resolución de la raíz (relativa rc=2 vs
absoluta rc=0), no por import/sintaxis/setup.

### 3.3 `git diff --stat` acotado y commit

```
$ git diff --stat -- tests/
 tests/test_005_011_t1_relative_root.py | 27 ++++++++++++++++++++++++---
 1 file changed, 24 insertions(+), 3 deletions(-)

$ git show --name-only --format='' HEAD
tests/test_005_011_t1_relative_root.py

$ git log -1 --format='%H %s'
4ea82ea8309dc82e7dc639ef5a10ee1ee6964d8e test(005-011): T1 — corrige el fixture del oraculo PD-2 (prepara el binding antes de validate-state; conserva la equivalencia relativa-vs-absoluta)
```

## 4. Invariantes y alcance

- **Solo tests:** el commit contiene únicamente `tests/test_005_011_t1_relative_root.py`.
  `docs/.cdad-state.json` figura modificado pero es cambio **preexistente** del orquestador: no lo toqué.
- **Sin lectura de implementación:** el CLI se ejecutó como caja negra; el módulo nunca se importó.
- **Validación en dos niveles:** corrección **local** (fixture del focal, no sale del focal) →
  rige el focal; no se corren regresiones ni la suite completa (la corre quien cierra, política del paquete).
- **Mapeo test→postcondición:** se conserva; el test sigue siendo el oráculo de PD-2/AC-2 (raíz relativa
  consistente entre subcomandos).
- **Sin valores del VPS ni ids crudos de sesión** en el informe.

## 5. Resultado

El focal T1 queda **verde (5/5)** con el producto ya commiteado (`53413b3`); el test #2 ahora sí
discrimina la resolución de la raíz (falsifica el comportamiento pre-fix) y conserva la cobertura de
`validate-state` y de `validate-policy` sin aserciones más débiles. Commit `4ea82ea`.
