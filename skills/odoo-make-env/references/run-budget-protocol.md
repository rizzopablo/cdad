# Test run budget protocol (CDAD-Odoo)

> Origin: protocol designed and validated empirically during a feature of
> a multi-module CDAD-Odoo project (Sep 2026), where the real cost turned out
> to be `full setup × repeated runs × property tests`, not the number of
> tests. Incorporated into CDAD as a standard.
> Numeric budgets: **defaults calibrated for 15-20 min setups** —
> the owner (HITL) adjusts them per project in `systemPatterns.md`.

## Principles

1. **The full suite is for the gate, not for debugging.** Debugging =
   `test-one` on the warm DB; the full suite runs ONCE to close the gate.
2. **The cost is the setup.** Minimize the number of setups, not the number
   of tests. A setup that does not follow a change with a hypothesis is pure
   waste.
3. **Every run follows a change.** Cycle: read the full failure → written
   hypothesis → ONE change → ONE run. Never re-run "to see if it passes".
4. **Hard budget per stage, set by the owner.** Exceeding it = STOP and
   escalate, not retry.
5. **Evidence already produced is reusable** if the code tree is identical
   (see "Review: budget 0").
6. **The N of property tests is runtime calibration, not contract.** The
   postcondition defines WHAT invariant; M scenarios is a budget. A larger N
   belongs to hardening.

## Budget per stage (defaults; adjust per project)

| Stage | Allowed run | Default budget |
|---|---|---|
| RED (test-writer) | `test-one` per class, warm DB | 1-2 runs, 0 full |
| GREEN (implementer, iteration) | `test-one` | max 2 per failure without convergence → STOP. `test-clean`/`make test` forbidden during iteration |
| GREEN closure | ONE `test-all` (fresh DB) | 1 |
| Review (reviewer) | none if the tree is identical; if it changed, 1 `test-all` | 0-1 |
| Review fix | mini RED→fix cycle with `test-one` + ONE `test-all` gate | ~15 `test-one` and 2 full runs per feature |

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

## Property tests: N as calibration

The spec defines the postcondition; the default N of the feature cycle is
small (8-10), with a **fixed seed** and explicit N as a constant. Reducing N
is documented in the commit as calibration (not weakening). Raising N
belongs to hardening, without touching postconditions.

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
