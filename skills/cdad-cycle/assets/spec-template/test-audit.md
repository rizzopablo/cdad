# Test Audit Report — <feature-id>

**Feature**: <name>
**Spec version**: <version or date>
**Test Writer**: <name/role>
**Audit completed**: <date>

## Behavior that changes (summary)

(Short paragraph listing the main changes. Reference to lines in spec.md)

Example:
- Frequent-customer discount now validates a 6-month period (previously 12 months)
- Discount is mutually exclusive with coupons (new behavior)
- Percentage discount calculation stays the same

---

## Test selection by promise (R2)

Selection and its justification are rule R2 — single editable definition in
`sources/roles/test-writer.md` (`cdad-shared:convention-rule`); the detail and the
acceptance counterweight R7 live in
`skills/cdad-cycle/references/stage-3-tdd.md`. This table applies it and never
redefines it: what is recorded here is, per test, the promise it serves, the
postconditions it protects and its declared consequence.

| Test | Promise | Postconditions protected | Without this test, the user... |
| --- | --- | --- | --- |
| `test_<name>` | <A / B / ...> | PC-1, PC-3 | <the user consequence, or `deferred-hardening: <reason>`> |

A test with no named user consequence is not an ordinary requirement: register
it in the spec's `deferred-hardening` with its reason (gate rule R4,
`sources/roles/orchestrator.md`; what is deferred reaches the closure through R6,
`sources/roles/scribe.md`).

---

## Modified tests

Each entry has this structure:

```
### <test-name>
- **Change**: [brief description]
- **Spec ref**: [line/section where the change is justified]
- **Promise**: [the observable promise it serves]
- **Postconditions protected**: [PC-n, PC-m]
- **Without this test, the user**: [the user consequence]
- **New expectation**: [what it verifies now]
- **Why**: [brief justification]
```

**Example:**

```
### test_descuento_aplicado_a_cliente_frecuente
- **Change**: Update the time window from 12 to 6 months
- **Spec ref**: Section "Eligibility", line "last 6 months"
- **New expectation**: Customer with purchases >$10k in the last 6 months qualifies for the discount
- **Why**: New feature requires a more restrictive period for Q2 budget control
```

---

## New tests to write

List of tests that did not exist and this feature requires, each with its
promise, the postconditions it protects and the user consequence:

- `test_descuento_incompatible_con_cupones` — promise B; PCs 2, 4; without this test, the user...
- `test_cupones_validos_sin_descuento_por_cliente_frecuente` — promise B; PC 2; without this test, the user...

Do not add a second test for an equivalent observable result, and do not leave
out a distinct committed behaviour: the unit of selection is the promise.

---

## Unchanged tests (untouched)

**These tests stay EXACTLY as they are** because they validate behavior that remains valid:

- `test_aplicar_descuento_si_criterio_cumple` (the % calculation is the same)
- `test_sin_descuento_si_cliente_nuevo` (the new-customer rule stays)
- `test_descuento_maximo_permitido` (the maximum limit does not change)

**Importance**: listing them explicitly confirms that the implementer must NOT touch these tests.

---

## Regression Risk Assessment

Is there behavior described in the new spec that has NO test coverage?

- ✅ Full coverage
- ⚠️ Risk: [list what is missing]

For each risk, name the promise it leaves unverified. A risk you decide not to
cover goes to the spec's `deferred-hardening` with its reason — never to a
silence.

---

## Test Audit Gate

- [ ] Every modified test is justified in spec.md with an explicit reference
- [ ] Every test names the promise it serves, the postconditions it protects and the user consequence ("without this test, the user...")
- [ ] No test was added for an equivalent observable result (no quota per postcondition, symmetry or coverage)
- [ ] There is no modified test without documented justification
- [ ] Untouched tests are listed (confirms the implications are known)
- [ ] Regression risk assessment completed; every deferred risk is registered in `deferred-hardening` with its reason
- [ ] The user (human or higher-hierarchy agent) approved this report before moving to RED
