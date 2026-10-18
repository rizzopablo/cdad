I'll start by reading the declared contract and the test file in scope.
Let me read the rest of the test file and the plan amendment A-6.
Now I have the full picture. Let me make the edits: first the `run_installer` env redirect (to keep `HOME` untouched), then the helpers, the docstring declarations, and the reformulated B3.
## Role report — test-writer / RED · `006-003-installer-single-profile-delegation-config` U7 **testfix**

**Packet** `006-003-installer-single-profile-delegation-config-test-writer-red-011` · substage `red` · contract `docs/specs/006-003-…/spec.md` (PD-6a..e, INV-2, D6) + `plan.md` enmienda **A-6** (leída). Write scope respected: **only `tests/`**. `install.sh` nunca fue leído/abierto; sólo se ejecutó black-box y se inspeccionaron sus efectos publicados (manifest, stdout/stderr, exit codes). `tests/.sensitive-patterns.local` no leído. `docs/planning/` y `findings/` (untracked, ajenos) intactos; sin `--no-verify`, sin stash, sin push.

## 1. Cambio (un solo archivo)

`tests/test_install_review5_regressions.py` — B3 reformulada declarando el reemplazo por **D6/A-6** (regla A-1):

| # | Test | Contrato | Oráculos observables |
|---|---|---|---|
| 1 | `TestReview5WithdrawnAgent::test_review5_b3_withdrawn_agent_is_retired_by_reinstall_and_uninstalled` | **PD-6a/D6/INV-2** | install #1 → el agente sale del staging → install #2: copia propia intacta **retirada del disco** y **fuera del manifiesto** (`artifacts`+`pending_removal`), **rc=0**, `--check` **sin PENDING-REMOVAL**, **rc=0 + PASS**, y `--uninstall` **sigue retirando lo registrado** (control sobre otro artefacto del manifiesto) y no resucita lo retirado |
| 2 | `…::test_review5_b3_locally_modified_withdrawn_agent_is_preserved_and_stays_registered` | **PD-6b/INV-2** | misma retirada, copia editada localmente: bytes **preservados byte a byte**, **CONFLICT** en una línea que **nombra la ruta**, y **sigue registrada** (`artifacts`/`pending_removal`) |

- Declaración explícita en el docstring del módulo (§ *ORACLE REPLACEMENTS*) y en el map test→postcondición: qué afirmaba B3 (sobrevivir, quedar `pending_removal`, `--check` en FAIL) y por qué D6/A-6 lo reemplaza; no se borró ningún assert sin declararlo. Se conserva el resto de B3 (mismo recorrido install→withdraw→reinstall→check→uninstall) y el resto del archivo.
- Helpers nuevos: `load_install_manifest`, `deployed_paths_for_source` (las rutas se leen del manifiesto que publica install #1, nunca hardcodeadas), `registered_entries_for` (neutral entre `artifacts`/`pending_removal`), `PENDING_REMOVAL_RE`; `run_installer(..., env_extra=…)` para redirigir `XDG_CONFIG_HOME` al temp (INV-6: nunca HOME). El CONFLICT se busca en una línea que combine `conflict` **y** la ruta, para que «0 conflict(s)» del summary no lo haga vacuo.

**Auditoría de otros tests con la regla vieja:** ninguno fija «una reinstalación conserva `pending_removal` sin modificar». `tests/test_install_ownership.py::test_t5_case3_check_reports_staging_obsolete_artifact` retira de staging y corre **sólo `--check`** (sin reinstalar), así que el prune de D6 no lo toca: queda válido sin reformular (`test_t5_case10` idem, drift). `test_003_006_t2_activation.py:109` y `test_005_005_t3_provenance.py:181` sólo usan `"pending_removal": []` como campo sintético.

## 2. Comandos y salida

```
$ python3 -m py_compile tests/test_install_review5_regressions.py && echo COMPILE_OK
COMPILE_OK
$ python3 -m pytest tests/test_install_review5_regressions.py --collect-only -q
6 tests collected in 0.05s
```

**GATE (RED) — B3 reformulada falla por aserción contra el árbol actual:**

```
$ python3 -m pytest tests/test_install_review5_regressions.py -q --tb=line
…/unittest/case.py:744: AssertionError: [] is not true : D6/PD-6b (replaces
  review-5 B3): a withdrawn own file modified locally must be disclosed as
  CONFLICT by the reinstall, naming the preserved path
  .config/opencode/agents/cdad-architect-odoo.md; output: …
…/unittest/case.py:732: AssertionError: Lists differ:
  ['.config/opencode/agents/cdad-architect-odoo.md'] != [] :
  D6/PD-6a (replaces review-5 B3): the own installed copy whose source
  agents/opencode/cdad-architect-odoo.md no longer deploys and whose bytes still
  match the recorded sha256 must be RETIRED by the reinstall;
  still on disk: ['.config/opencode/agents/cdad-architect-odoo.md']
2 failed, 4 passed in 83.07s
```

Ambas son `AssertionError` de comportamiento faltante (no ImportError/syntax/fixture). La variante intacta falla exactamente en «hoy el agente queda» (línea 513); la modificada en «hoy no se reporta CONFLICT». **El resto de review5 sigue verde (4/5 previos).** Corrida repetida: idéntico `2 failed, 4 passed` (83–97 s).

## 3. Commit

```
$ git commit -m "test: 006-003 U7 testfix — review-5 B3 reformulada por D6/A-6 (PD-6a/PD-6b, INV-2)"
[main 12a859b] 1 file changed, 272 insertions(+), 63 deletions(-)
$ git show --stat --oneline HEAD
12a859b … tests/test_install_review5_regressions.py | 335 ++++++++++++++++------
$ git status --short
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
```

## 4. Notas / límites honestos

1. **Acoplamiento declarado para el GREEN:** la variante intacta exige `install #2 → rc=0`. El GREEN de U7 midió que retirar un agente del staging hace fallar el `Verify` por la cuenta fija (`expected 11, found 10`); por eso A-6 incluye que la cuenta esperada salga del conjunto en staging. Sin esa segunda mitad, la primera aserción de rc seguirá roja por el motivo correcto (comportamiento del instalador), no por el test.
2. **Desviación menor de lectura:** inspeccioné `Makefile:10-13` (no es `install.sh` ni root de implementación del packet) sólo para ubicar el generador de `build/staging`; no leí `install.sh` en ningún momento.
3. La variante modificada **no** asserta rc (PD-6b fija los efectos: preservar + CONFLICT + seguir registrado; el archivo preservado sigue necesitando resolución explícita). Declarado en su docstring.
4. `--uninstall` se invoca sin `--force`, igual que B3 original (no interactivo en este instalador).
5. Suite completa **no** corrida (política del paquete: la corre quien cierra).
