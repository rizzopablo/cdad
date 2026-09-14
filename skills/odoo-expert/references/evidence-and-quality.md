# Required evidence and anti-rationalization

Rescued from the `odoo-dev-methodology` skill (retired; its content lives here).

## Evidence — non-negotiable

**Golden rule:** "it seems to work" is never enough. A module is ready when there is
**evidence**, not when it seems to work.

| Verification | Required evidence (empirical, not assumed) |
|---|---|
| Lint | `pylint --load-plugins=pylint_odoo -d all -e odoolint <module>/` with no errors |
| OCA checks | `oca-checks-odoo-module <module>/` with no findings |
| Tests | the project's runner green, with the summary line: `0 failed, 0 error(s) of N tests` |
| Installation from scratch | installation on a **clean DB**, not an update over the development one |
| Sources | every design decision citing the Odoo addon where it was verified |

> **How tests are run is defined by the environment, not this skill.** If the
> project exposes the `odoo-make-env` contract, it is `make test` (suite),
> `make test-one` (one) and `make test-clean` (installation from scratch). **Do
> not invoke `odoo-bin` by hand in a gate**: you lose the contract's guards — in
> particular, `-u` over a module that is not installed reports *"0 failed, 0 error(s)
> of 0 tests"* with **exit 0**, which a gate would read as green with zero tests
> run.

**Evidence rules**

1. **The output is the proof.** Paste the last lines of the run, with the summary.
   "The tests pass" without output is not evidence.
2. **No evidence, no deploy.** A module without a green suite does not get installed
   in production.
3. **Coverage ≠ correctness.** A passing test proves the code does what the test
   says, not that the contract is correct. Verifying against the Odoo source is
   complementary, not optional.
4. **Demo data ≠ test data.** Tests must pass without depending on demo records
   (OCA rule).
5. **Documented debt ≠ hidden debt.** If a check cannot be run today, it gets
   recorded explicitly; it is never silently omitted.

## Anti-rationalization

When the excuse shows up, the refutation is already written. Not negotiable.

| Excuse | Refutation |
|---|---|
| "It's a small module, no test needed" | Size does not predict risk: 50 lines can break a base model's view. Every module carries its tests. |
| "I tested it by hand and it works" | Testing by hand verifies one path; tests verify the contract and protect it from regressions. |
| "pylint-odoo gives false positives, I skip it" | Odoo checks are the difference between a maintainable module and one that someone will have to tear apart. A false positive gets justified with a comment, not by omission. |
| "It's a one-line change in the XML" | A misplaced `<field>` in an xpath breaks the whole view at runtime and is discovered in production. The checks catch it in dev. |
| "No time, I'll add the test later" | A test written afterwards verifies what the code does, not what the spec asks. And "later" never comes. |
| "The client needs it NOW" | Urgency does not eliminate risk: it transfers it. A broken deploy costs more than the time saved. |
| "Odoo already does it that way, no need to verify" | That is the starting point of verification, not its end: read the source and cite where. |
| "I'll do it quickly through the web editor" | The web editor generates unversioned debt: it is not reviewed, not tested, not migrated, not audited. Module, not editor. |

**Red flags that trigger this table:** "it's quick", "I tested it by hand", "no
need", "the client is waiting", "pylint is annoying", "I'll test it later".

## pre-commit (OCA setup)

OCA uses `pre-commit` for automatic formatting. In a migration, the
`pre-commit run -a` step goes in a **separate** commit (`[IMP] <module>: pre-commit auto
fixes`), isolated from the real work, so that the migration diff stays readable.
