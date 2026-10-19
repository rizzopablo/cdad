…vigilar. Anclas declaradas en los docstrings: PD-18 (disjunción temporal↔producto ya vigente), el control negativo de PD-24 y las dos precedencias de O-4 (hoy `deny` gana porque no hay `allow`); son exactamente las regresiones que U3 debe preservar.

### 3. Comandos exactos y salida

```
$ python3 -m pytest tests/test_006_005_u3_temporary_scope.py tests/test_006_005_u3b_derived_temporary_permission.py -q --tb=line
9 failed, 5 passed in 5.48s          # 4 corridas consecutivas: idéntico (sin flakiness)

Focales fallan por ASERCIÓN (AssertionError), nunca ImportError/sintaxis/fixture:
  PD-15  'docs/cdad-policy.json' not found in 'ERROR: scope class is invalid'
  PD-15  2 != 0 : con la raíz temporal declarada por la política el paquete debe aceptarse
  PD-16  'gitignore' not found in 'ERROR: scope class is invalid'   (x2: no-ignorado y no-git)
  PD-16  2 != 0 : con el selector ignorado el paquete debe aceptarse
  PD-17  2 != 0 : (precondición) el paquete con temporal declarado e ignorado debe aceptarse  (x2)
  PD-24  'deny' != 'allow'   (raíz temporal debe ser `allow` en `edit`)
  PD-24  'deny' != 'allow'   (control positivo del fixture de colisión privada)
```
Todas las aserciones expresan la postcondición; la causa raíz común es la conducta ausente (la clase de scope `temporary` no existe hoy: `prepare --write-scope temporary=…` ⇒ rc 2 `scope class is invalid`).

```
$ python3 -m pytest tests/test_004_002_t1_policy.py tests/test_004_002_t1_reviewfix.py \
    tests/test_004_002_t2_bootstrap.py tests/test_004_002_t6_landing.py \
    tests/test_004_002_t7_acceptance.py tests/test_004_002_t7_private_paths.py \
    tests/test_004_002_t7_limits_rule.py tests/test_004_002_t5_runtime.py \
    tests/test_004_002_t5_reviewfix.py tests/test_003_002_t1_receive.py \
    tests/test_003_002_t2_materialize.py tests/test_packet_prepare.py \
    tests/test_005_005_t2_docs_policy.py -q
147 passed in 157.44s        # las 13 regresiones de la ficha U3, verdes (baseline previo: 147 passed)
```

Sondas de caja negra usadas para fijar el oráculo (tempdirs, sin escritura en el repo):
`prepare --write-scope temporary=.cdad/tmp/work` ⇒ rc 2 `scope class is invalid` (RED); `validate-policy` con `temporary_roots:["scripts/tmp"]`/`["docs/tmp"]` ⇒ rc 2 (PD-18 vigente); `prepare` con raíz declarada ⇒ rc 0 **sin** ninguna entrada de temporal en el `edit` del derivado (RED de PD-24); `git check-ignore -q .cdad/tmp/work` ⇒ 0 (ignorado) / 1 (no ignorado). El mecanismo del fixture de PD-17 (prepare→`--record-dispatch`→manifiesto por `git ls-files --cached --others --exclude-standard`→descriptor→`receive`) se validó con un scope `tests` puro: `receive` rc 0, `scope_validation: passed`, `semantic_status: pending` — así el único delta que queda en RED es la clase `temporary`.

### 4. Regla A-1 / V-8

**No hay reemplazo.** Verificado por grep en `tests/`: ningún test fija el valor de la propuesta (`temporary_roots: []` en `propose_policy`) — `test_004_002_t1_policy.py` sólo comprueba determinismo y que la propuesta materializada valide; `test_003_003_t2_preflight.py:105`, `test_004_002_t1_reviewfix.py:125` y `test_004_002_t6_landing.py:666` son **fixtures de política**, y `test_004_002_t6_landing.py:374` sólo parsea el JSON. Tampoco hay test que fije el mapa `edit` completo del test-writer derivado (los de T5/T7/005-008 usan el evaluador findLast con sondas, no listas doradas). Por eso el control negativo de PD-24 usa comparación **entre dos proyectos** (lista vacía vs. raíz declarada, descontando las líneas de la raíz) en vez de una lista dorada: una lista dorada se rompería por cualquier cambio de layout ajeno a la PD.

### 5. `make validate` — condición preexistente declarada

`make validate` ⇒ `Assert PASS: 168 / Assert FAIL: 1`; el fallo es **F011** (`scripts/validate-subagents.sh`), por drift de las **copias instaladas** de skills: `install.sh --check` reporta `DRIFT: differs ~/.claude/skills/cdad-cycle/references/cli-delegation.md` (la copia instalada es del 18-Oct 18:07; el repo tiene el texto de U1a, 19-Oct 00:27) y un `.pyc`. No depende de `tests/` (mi cambio es sólo A-added de dos archivos de test; `git diff --stat` tracked vacío) y ya estaba en el HEAD `0c8c199` del paquete. Queda reportado para que el orquestador decida (reinstalar o registrar la condición).

### 6. Commit

```
$ git commit -m "test: 006-005 U3 RED — temporal del test-writer: clase temporary validada contra
la política, git check-ignore en prepare, recibo con scope_validation passed, sonda ignorada fuera
del manifiesto (PD-15..PD-18) y permiso de edición del agente derivado con la precedencia de las
barreras probada en dos colisiones (PD-24)"
[main 0b38f07] 2 files changed, 1112 insertions(+)
 create mode 100644 tests/test_006_005_u3_temporary_scope.py
 create mode 100644 tests/test_006_005_u3b_derived_temporary_permission.py
```
`git show --stat HEAD`: sólo los dos archivos de `tests/`. Sin `--no-verify`, sin `git stash`, sin push. `git status` post-commit: sólo los untracked preexistentes ajenos.

### 7. Límites declarados en los propios tests (PD-15, honestidad)

- **PD-17**: `scope_validation: passed` **no** prueba que el auxiliar se haya podido escribir — un cambio en una raíz ignorada nunca entra al manifiesto (INV-3, y el test lo demuestra con `git ls-files` + `git check-ignore`). La escritura real con la herramienta del rol es de U6 (E2/V-14); aquí no se sustituye por `passed`. Declarado en el docstring del test y en el del módulo.
- **PD-24/O-4(a)**: el fixture prueba que el validador admite la raíz temporal que solapa una ruta privada fuera de producto (precondición verificada con `validate-policy` rc 0) y que el `deny` privado gana; su control positivo (la raíz temporal es `allow`) es la aserción que hoy falla, así que la precedencia queda discriminante en GREEN.

### 8. Bloqueos / conflictos

Ninguno de contrato. Único pendiente del entorno: F011 de `make validate` (§5), preexistente y ajeno a `tests/`.