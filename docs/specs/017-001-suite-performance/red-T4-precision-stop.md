# test-writer RED — role report (Route C, packet `017-001-suite-performance-test-writer-red-019`)

## 1. Intake (Route C — valid, validated before working)

- Dispatch declares **Route C** with exactly one identification block; prompt carries **zero** `---cdad-packet-json` markers → no route mixture.
- Identification vs validated files — all match:
  - `packet_id` = `017-001-suite-performance-test-writer-red-019` ✓
  - `contract` = `docs/specs/017-001-suite-performance/spec.md`, sha256 `472bab0c…192672e` — matches `sha256sum` of the file ✓
  - `execution_id` = `exec-017-001-suite-performance-001`, matches `execution.json` (`schema_version: 2` → v2 context, not v1) ✓
- Canonical checks (exact commands, all in `<repo>`):
  - `python3 scripts/cdad_packet.py validate-request --request .cdad/packets/…/REQUEST.json` → **exit 0**
  - `python3 scripts/cdad_packet.py validate-packet --request …/REQUEST.json --packet …/PACKET.md` → **exit 0**
  - `python3 scripts/cdad_packet.py render --request …/REQUEST.json` → **byte-for-byte identical** to `PACKET.md` (`diff` clean)
  - `python3 scripts/cdad_packet.py render --route C --request …/REQUEST.json` → **identical** to the received identification block
- Scope respected: read only the 4 declared inputs + read_scope (`docs/specs/017-001-suite-performance`, `tests/`); **no implementation code read** (no read/grep of `scripts/`, `agents/`, etc.). The CLI was exercised only as a black box via synthetic attempts in scratch dirs outside the repo (`~/clawd/tmp/cdad-render/probe*`). `git status` confirms the tree is untouched (only pre-existing `M docs/.cdad-state.json`, already noted in review-T4).

## 2. Pre-RED finding

The 13 existing tests in `tests/test_017_001_suite_reconcile.py` (confirmed: 13 collected, zero collection error) do **not** cover the aggregate triple identity with thousandths-sensitive totals — caso 1 uses 1-decimal-friendly values (1.3/2.0), caso 5 checks residual presence/sign, none asserts `sum_S_test == ΣS_test`, `Σprep+Σremainder == sum_S_test`, `sum_S_test + R_pytest == T_pytest` simultaneously. So the **protection is genuinely missing** (contribution declared: without it, a 1-decimal rounding of the aggregate passes the suite silently — exactly the review-T4 hallazgo 2 failure mode).

## 3. RED cannot be demonstrated — request premise contradicted by observable behavior (STOP + REPORT, no commit)

I built the exact synthetic from the objective (two tests × 6.004 s, total 12.008 s) plus two variants, all as black-box `reconcile` runs. Results:

- **Probe 1** (2× `call: 6.004`, `pytest_wall_s: 13.5`): `run.sum_S_test=12.008`, tests `S_test=6.004/6.004`, `preparation_s=0.5/0.5`, `remainder_s=5.504/5.504`, `R_pytest=1.492`, `T_pytest=13.5`. **All three identities hold with diff 0.0** — not 0.008.
- **Probe 2** (multi-phase setup/call/teardown summing to 6.004 each, `selection.kind: all` + register): identical — holds.
- **Probe 3** (large values 2× `2493.311`, `T_pytest=4994.27`, mimicking the real base): `run.sum_S_test=4986.622`, `ΣS_test=4986.622`, **diff 0.0**.

So `reconciliation.json` **already publishes 3-decimal aggregates**; the 1-decimal rounding (`sum_S_test: 4986.6` vs `186.221+4800.401=4986.622`, Δ=0.022) exists **only in `performance/baseline.json`**, a different artifact produced outside the `reconcile` surface fixed by `t3-aggregator-contract.md` (which mandates 3 decimals + tol 1e-3 — the current CLI honors it).

Consequences (anti-gaming):
- The test as specified would be **GREEN on first run**. Committing it as RED would misrepresent evidence; hunting for a contrived input that fails for another reason would test a different defect than the one assigned.
- Per the packet ("if the contract or test conflicts with the request, stop and report") and RED discipline (a sustituto-style GREEN for vigente behavior belongs to POST-AUDIT with verde+sensibilidad + approved map, never to RED), I **added no test and made no commit**. `modified files: none. commit: none.`

## 4. RED command evidence (what *would* have been the RED run)

Collection gate (passes — oracle is an assertion vehicle, never ImportError):
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --collect-only -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py` → `13 tests collected in 0.05s`.

Had the defect reproduced in `reconcile`, the RED command would have been:
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py -k rounding_or_accounting_identity` → expected `AssertionError` with Δ≈0.008 on the triple identity, never ImportError/collection error. **Actual: defect not present at this surface; run not committed.**

## 5. Live-inventory delta (as text, for the orchestrator to materialize — I did not edit `docs/`; write_scope is `tests/` only)

```text
LIVE-INVENTORY-DELTA — 017-001 T4 RED hallazgo-2 (test-writer-red-019, 2026-11-07, SIN CAMBIOS):
- Intentado: proteccion RED triple-identidad (sum_S_test / prep+resto / sum+R=T, tol 1e-3) sobre intento sintetico 2x6.004 s.
- Hallado: reconcile ya publica 3 decimales (probes 12.008 y 4986.622, diff 0.0); el redondeo a 1 decimal vive solo en performance/baseline.json (4986.6 vs 4986.622, Δ=0.022).
- Decidido: sin edicion de tests, sin commit; RED no reproducible en la superficie indicada.
- Pendiente (orquestador): re-rutear — (a) registrar la proteccion como hardening POST-AUDIT (verde, con sensibilidad demostrada), o (b) re-encuadrar RED sobre el paso que genera baseline.json con inputs autorizados que describan su produccion, o (c) asignar hallazgo 2 al paso de informe T4 (implementador), no al agregador.
```

## 6. Recommended orchestrator decision

1. **Do not** record a RED for this packet (there is no right-reason failure to evidence).
2. Either promote the missing triple-identity protection to **POST-AUDIT hardening** (I can write it there with verde + sensitivity against a concrete defect, e.g. a synthetic 1-decimal-rounded fixture), or re-scope a new RED packet against the **baseline-report step** with the authorized inputs that describe how `performance/baseline.json` is produced (currently absent from my inputs — and I will not read implementation to fill that gap).
3. Hallazgo 2's `resolves_when` should target the baseline publisher, not `reconcile`: current `reconcile` already satisfies spec §4.4 + t3-contract §8 for the tested shapes.
