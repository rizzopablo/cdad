# test-writer RED — role report (Route C, packet `017-001-suite-performance-test-writer-red-020`)

## 1. Intake (Route C — valid, validated before working)

- Dispatch declares **Route C** with exactly one identification block; prompt carries **zero** `---cdad-packet-json` markers → no route mixture.
- Identification vs validated files — all match:
  - `packet_id` = `017-001-suite-performance-test-writer-red-020` ✓
  - `contract` = `docs/specs/017-001-suite-performance/spec.md`, sha256 `472bab0c…192672e` — matches `sha256sum` of the file ✓
  - `execution_id` = `exec-017-001-suite-performance-001`, matches `execution.json` (`schema_version: 2` → v2 context, not v1) ✓
- Canonical checks (all in `<repo>`):
  - `python3 scripts/cdad_packet.py validate-request --request .cdad/packets/…/REQUEST.json` → **exit 0**
  - `python3 scripts/cdad_packet.py validate-packet --request …/REQUEST.json --packet …/PACKET.md` → **exit 0**
  - `python3 scripts/cdad_packet.py render --request …/REQUEST.json` → **byte-for-byte identical** to `PACKET.md` (`diff` clean)
- Scope respected: read only the 5 declared inputs + read_scope (`docs/specs/017-001-suite-performance`, `tests/`); **no implementation code read** (no read/grep of `scripts/`, `agents/`, etc.). The CLI was exercised only as a black box via synthetic attempts in scratch dirs outside the repo (`<tmp>/cdad-probe-020/`), the same oracle mechanism the existing tests use. `git status` confirms the only other modification is the orchestrator's pre-existing `M docs/.cdad-state.json` (packet rotation 019→020, not committed by me).
- No full cycle/spec skill loaded; packet is the execution contract.

## 2. Pre-RED finding (contribution)

The 13 existing tests in `tests/test_017_001_suite_reconcile.py` (confirmed: 13 collected) do **not** cover the run-level triple identity: caso 1 uses 1-decimal-friendly values (1.3/2.0), caso 5 checks residual presence/sign but not run-level `preparation_s`/`remainder_s` totals nor their identity with `sum_S_test`, and no test demands a declared rounding bound for summing published per-test values. Black-box probe (200×`call: 0.1234`, `pytest_wall_s: 30.0`): `run = {sum_S_test: 24.68, R_pytest: 5.32, T_pytest: 30.0}` — **no** `preparation_s`/`remainder_s` keys; per-test published sum = 200×0.123 = 24.6 vs run total 24.68 (**gap 0.08 s** >> tol 1e-3); no `round`/`redond`/`cota`/`bound` token anywhere in JSON+MD. So the protection is genuinely missing — **without this test, a silently-rounded run aggregate passes the suite** (real base: 0.309 s drift over 2034 tests, review-T4 hallazgo 2).

## 3. RED (new test, additive only)

- **Modified files:** `tests/test_017_001_suite_reconcile.py` only (+118 lines, 0 deletions in existing code — `git diff` shows no `-` lines in the test file). The thirteen existing tests are untouched.
- **New test:** `test_run_level_accounting_identity_with_rounding_bound` (PC-6/INV-5, spec §4.4 + t3-contract §Reglas 6–8, review-T4 hallazgo 2). Synthetic: 200 tests × `call 0.1234 s` with prep `0.0234 s` each (unrounded sums: total 24.68, prep 4.68, resto 20.0; `T_pytest=30.0`). Asserts: run publishes `sum_S_test`/`preparation_s`/`remainder_s` (alias-tolerant) equal to `round(unrounded,3)` and multiples of 0.001; `prep+rem==sum` and `sum+R_pytest==T_pytest` within 1e-3; JSON+MD declares the rounding bound (`round`/`redondeo` + `cota`/`bound`/`toler`). Imports only what the file already imports — no new dependencies.
- **Commit:** `0b956dbb` — `test(017-001): RED run-level accounting identity with rounding bound (T4 hallazgo-2)` (1 file, 118 insertions). `docs/.cdad-state.json` left uncommitted (orchestrator-owned).

## 4. RED command evidence (fails for the right reason)

Collection gate (oracle is an assertion vehicle, never ImportError):
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --collect-only -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py` → `14 tests collected` (13 existing + 1 new), zero collection error.

RED run:
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py -k run_level_accounting_identity` → `1 failed, 13 deselected` with:
`AssertionError: 017-001 T4 hallazgo-2 (PC-6): el bloque run no publica preparation_s … sin esos totales la identidad contable no se puede reconstruir con las cifras publicadas` — promise-absent assertion, never ImportError/collection error.

Regression guard (existing suite intact):
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py` → `1 failed, 13 passed in 6.24s` (the 1 failure is the new RED; all thirteen pre-existing pass).

Suite completa: no realizada (RED focal; cierre de epic con suite completa queda para el momento de cierre con su autorización y evidencia).

## 5. Live-inventory delta (as text, for the orchestrator to materialize — write_scope is `tests/` only)

```text
LIVE-INVENTORY-DELTA — 017-001 T4 RED hallazgo-2 reencuadrado (test-writer-red-020, 2026-11-07, CON CAMBIOS):
- Agregado: tests/test_017_001_suite_reconcile.py::test_run_level_accounting_identity_with_rounding_bound (commit 0b956dbb, +118/-0; trece existentes intactos: 13 passed).
- Protege: PC-6/INV-5, spec §4.4 — totales de corrida sum_S_test/preparation_s/remainder_s a 3 decimales desde valores sin redondear, prep+rem==sum y sum+R==T (tol 1e-3), más cota de redondeo declarada.
- Estado RED: falla hoy por AssertionError de promesa ausente (run sin preparation_s/remainder_s; gap 0.08 s en sintético 200x0.1234 s; sin token round/cota/bound) — nunca ImportError ni error de colección.
- Pendiente (implementador T4): publicar los dos totales faltantes + la cota en reconciliation.json/md; luego este RED debe pasar a GREEN sin modificar el test.
```
