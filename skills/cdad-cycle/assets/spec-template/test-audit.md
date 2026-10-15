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

## Modified tests

Each entry has this structure:

```
### <test-name>
- **Change**: [brief description]
- **Spec ref**: [line/section where the change is justified]
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

List of tests that did not exist and this feature requires:

- `test_descuento_incompatible_con_cupones`
- `test_cupones_validos_sin_descuento_por_cliente_frecuente`

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

---

## Test Audit Gate

- [ ] Every modified test is justified in spec.md with an explicit reference
- [ ] There is no modified test without documented justification
- [ ] Untouched tests are listed (confirms the implications are known)
- [ ] Regression risk assessment completed
- [ ] The user (human or higher-hierarchy agent) approved this report before moving to RED
