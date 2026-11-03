# Test run budget protocol (CDAD-Odoo)

> Applicability: this protocol budgets runs of the addon test contract (the
> `odoo-make-env` targets). An engagement that modifies no addon — a
> documentary-pure product included — owes no addon run; its budget is zero.
> The boundary that decides addon work is owned by the `odoo-expert` skill.

> Origin: protocol designed and validated empirically during a feature of
> a multi-module CDAD-Odoo project (Sep 2026), where the real cost turned out
> to be `full setup × repeated runs × property tests`, not the number of
> tests. Incorporated into CDAD as a standard.
> Numeric budgets: **defaults calibrated for 15-20 min setups** —
> the owner (HITL) adjusts them per project in `systemPatterns.md`.

## Principles

1. **Defaults por momento (hogar canónico `skills/cdad-cycle/references/stage-3-tdd.md` §"Test evidence policy").**
   Durante el ciclo: `test-one` focal + regresión proporcional, sin suite completa como rutina;
   cierre de feature: suite completa recomendada, si se omite se registra suite completa no realizada
   con motivo, selección ejecutada y límites; cierre de epic: suite completa obligatoria por defecto,
   omitirla requiere dispensa expresa del dueño para ese cierre. Debugging =
   `test-one` on the warm DB; la aprobación de la política autoriza la corrida ordinaria de cierre
   de epic sin exigir autorización adicional para esa corrida.
2. **The cost is the setup.** Minimize the number of setups, not the number
   of tests. A setup that does not follow a change with a hypothesis is pure
   waste.
3. **Every run follows a change.** Cycle: read the full failure → written
   hypothesis → ONE change → ONE run. Never re-run "to see if it passes".
4. **Hard budget per stage, set by the owner.** Exceeding it = STOP and
   escalate, not retry.
5. **Evidence already produced is reusable** if the code tree is identical
   (see "Review: budget 0").
6. **El N de property tests es presupuesto declarado, no contrato.** La postcondición
   define QUÉ invariante; su presupuesto se rige por R2
   (`sources/roles/test-writer.md`, `cdad-shared:convention-rule`): finito y
   positivo declarado y justificado antes de cada campaña (invariante, dominio
   y coste), sin mínimos ni máximos universales. Evidencia reproducible por
   referencia a R2.

## Budget per stage (defaults; adjust per project)

| Stage | Allowed run | Default budget |
|---|---|---|
| RED (test-writer) | `test-one` per class, warm DB | 1-2 runs, 0 full |
| GREEN (implementer, iteration = Durante el ciclo) | `test-one` | max 2 per failure without convergence → STOP. `test-clean`/`make test` forbidden during iteration |
| Cierre de feature | `test-all` recomendada (fresh DB); si se omite, suite completa no realizada con motivo, selección ejecutada y límites | 0-1, recomendada |
| Cierre de epic | `test-all` obligatoria por defecto (fresh DB); omitirla requiere dispensa expresa del dueño para ese cierre | 1 por defecto, 0 solo con dispensa registrada |
| Review (reviewer) | none if the tree is identical; if it changed, evidencia proporcional al cambio, no una nueva suite completa automática; `test-all` solo cuando el momento lo exige (cierre) o con autorización suficiente para esa corrida, otherwise cite + suite completa no realizada | 0-1 cuando el momento lo exige |
| Review fix | mini RED→fix cycle with `test-one` + evidencia proporcional; `test-all` solo cuando el momento lo exige, otherwise focal + suite completa no realizada | ~15 `test-one`; completa solo si el momento la exige |

## Instalación limpia frente a amplitud (PC-14)

Instalación limpia y amplitud son dimensiones distintas: `test-clean` (instalación desde cero en
DB nueva, módulo acotado) prueba instalación limpia, no amplitud de suite. La amplitud (cuántos
tests corren) no demuestra instalación limpia y la instalación limpia no demuestra amplitud total.
`test-clean` sigue exigible cuando la spec lo marca; si su runner une inseparablemente la
instalación exigida con una suite completa no autorizada para esa corrida, la salida es bloqueo de
instalación limpia y solicitud de autorización o resolución del entorno, nunca `suite completa no
realizada` como su salida válida. Un encargo sin cambios de addon no adquiere obligaciones de
instalación por dominio del proyecto.

## Target `test-all` (multi-module: one setup for all suites)

A single fresh DB that installs the deepest module (which pulls in the rest
via `depends`) and filters the tests of all the repo's modules:

```make
test-all:
	$(require-module)
	-dropdb --if-exists $(TEST_DB) 2>/dev/null || true
	$(RUN) odoo-bin -c $(CONF) -d $(TEST_DB) -i <deepest_module> \
		--test-tags /module_A,/module_B $(ODOO_FLAGS)
```

**Condition:** the abstraction "installing the deepest one pulls in the
rest" only holds if the dependency graph is a chain. With independent
modules, use `-i mod1,mod2`. It replaces N `test-clean` with 1 setup.

## Anti-false-green guards (mandatory in the Makefile)

- `require-installed`: `-u` on a non-installed module is a no-op that
  reports `0 failed, 0 error(s) of 0 tests` with rc=0 → reject, point to
  `test-clean`/`test-all`.
- `require-module`: `-i` of a non-existent module installs nothing and runs
  0 tests with rc=0 → verify the module exists in some addons_path.
- The warm DB (`$(INST)_test`) is for iteration; the fresh one of `test-all`
  is the evidence. **Never declare the gate closed with a warm run alone.**

## Comma trap in `--test-tags` (verified: `odoo/tests/tag_selector.py`,
`re.split(r',(?![^\[]*\])', spec)`)

The comma separates COMPLETE specs: `mod:ClassA,mod:ClassB` runs both
classes; `mod:ClassA,ClassB` takes `ClassB` as another spec (without module)
and runs fewer tests than expected, **without error**. Rule: repeat the
prefix in each spec, and verify the `of N tests` line against the expected
count.

## Review: budget 0 with tree identity

If `git diff --stat <commit-of-the-evidence-run>..HEAD` shows only
`[STATE]`/docs commits, the code tree is identical → **cite the log**
(path + line), do not re-run. Requirement: every gate run is recorded with
its log and its commit (state file or commit message). Static analyzers
(`make lint`) do not consume budget.

## Property tests: presupuesto declarado por referencia a R2

La postcondición define QUÉ invariante; el presupuesto se rige por R2
(`sources/roles/test-writer.md`, `cdad-shared:convention-rule`): finito y
positivo declarado y justificado antes de cada campaña (invariante, dominio y
coste), sin mínimos ni máximos universales; evidencia reproducible
(invariante, presupuesto declarado y cantidad realmente ejecutada, semilla
fija, versión/config del generador, contraejemplo pertinente). Cambiar el
presupuesto exige justificación y comprobar que no elimina obligaciones
comprometidas; se registra como calibración, nunca como cuota rival.

## Self-contained fixtures (fresh DB condition)

Verified in Odoo 19 source (`odoo/tools/config.py:233`): the CLI creates the
DBs **without demo data** (`--with-demo` default False). Consequence: every
test that invoices or touches accounting configures its own journals/accounts
(generic chart template) in its fixture. Without this, it passes on the warm
DB (journals from previous stories) and fails on the gate's fresh DB with
`UserError: No journal could be found`, far from the cause.

## Origin case (evidence)

Before: 6 full runs in ~6 h to validate an amendment; 1.5 h post-commit
without closing the gate; task cancelled. After: 4 `test-one` runs of ~45 s
identified 4 failures with exact assertion in ONE run; final gate 87/87 in
6m50s with 1 setup (`test-all`); review with 0 runs (tree identity). No
postcondition or assertion was weakened.
