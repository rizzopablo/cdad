## (a) Tests and the postcondition/AC each covers

Focal file: `tests/test_005_013_t2_change_classification.py` — 15 tests, derived only from the contract (`spec.md` §2.4/§2.5/§2.8 + §3 PD-7..PD-11 + §5 AC-5..AC-7), never from the implementation. Black-box: the repo CLI as a subprocess over synthetic fixture projects in tempdirs (subprocess `HOME` in an empty tempdir), reusing by reference the T1 harness (`tests/test_005_013_t1_unit_projection.py`, untouched).

| Test | PD / AC | Observable assertion |
|---|---|---|
| `test_pd8_current_when_independent_unit_added_without_effect` | PD-8 / AC-5 | dispatch → add independent unit + history edit → `current`, no `.impact.json`, `receive` rc=0 / `pending` |
| `test_pd8_current_when_only_history_edited` | PD-8 / AC-5 | history-only edit → `current`, no journal |
| `test_pd9_impact_when_unit_scope_changes_with_durable_record` | PD-9 / AC-5 | unit scope edit → `impact`; journal in baseline packet dir with `reason`/`contract_sha256_old`(==registered)/`contract_sha256_new`(≠)/`changed_parts`(names `unit`); state/policy unchanged |
| `test_pd9_impact_when_unit_dependency_changes` | PD-9 / AC-5 | unit dependency edit → `impact` + journal naming `unit` |
| `test_pd9_impact_when_shared_part_changes` | PD-9 / AC-5 | shared section edit → `impact` + journal naming the section |
| `test_pd9_impact_does_not_block_reception_of_dispatched_packet` | PD-9 / PD-6 / AC-5 | scope edit → `impact`; `receive` still rc=0 / `passed` / `pending` |
| `test_pd8_pd10_edited_authorization_section_is_impact_never_impeded` | PD-8 / PD-10 / AC-6 | authorization section edit → rc=0 `impact`, never `impeded`/rc=2 |
| `test_pd10_impeded_when_epic_plan_approval_retired_with_exit` | PD-10 / AC-6 | approval retired → rc=2 `impeded` + `approval pending` + exit `epic-plan`; restore → `prepare` rc=0, new packet's projection becomes baseline |
| `test_pd10_impeded_when_hitl_delegation_revoked_with_exit` | PD-10 / AC-6 | delegation revoked → rc=2 `impeded` + `state incoherent` + exit named; no journal |
| `test_pd7_baseline_is_the_most_recent_packet_of_the_unit` | PD-7 / AC-5 | two successive packets → journal in the most-recent packet dir; `registered.packet_id`/`sha256` declared |
| `test_pd7_no_registered_projection_yields_current` | PD-7 / AC-5 | no packet with a registered projection → `current`, no journal, `registered` null |
| `test_pd11_status_informs_verdict_and_writes_nothing` | PD-11 / AC-7 | two `status` byte-identical (no journal); block informs `mode`/unit/baseline/live/verdict/changed_parts/reason; view keeps its existing fields |
| `test_pd9_journal_is_idempotent_for_same_digest_pair` | PD-9 / PD-11 / AC-7 | same digest pair → journal byte-identical; distinct pair appends a record without overwriting |
| `test_inv8_restrictive_prose_is_impact_never_impeded` | PD-10 / INV-8 | restrictive prose in a `shared` part → `impact`, never `impeded` |
| `test_inv1_inv9_verdict_does_not_write_state_nor_policy` | PD-11 / INV-1 / INV-9 | verdict writes neither state (incl. `stage_history`) nor policy |

## (b) Files created

- `tests/test_005_013_t2_change_classification.py` (new, 942 lines). No other file touched; implementation (`skills/**`), policy, receipt schema and other features' tests untouched.

## (c) Exact command and RED evidence

Command: `python3 -m pytest tests/test_005_013_t2_change_classification.py -q`

Result: **15 failed in 8.56s**, exit=1. Every failure is an `AssertionError` (contract assertion) — none is `ImportError`/`AttributeError`/`SyntaxError`/fixture error. With `--tb=line`:

```
tests/.../test_005_013_t2_change_classification.py:375: AssertionError: PD-8 violada: agregar una unidad futura independiente NO tiene efecto (veredicto `current`, rc=0); hoy rc=2 (subcomando inexistente): "ERROR: cdad_packet.py: argument command: invalid choice: 'validate-unit-contract' ..."
...:407: AssertionError: PD-8 violada: editar la historia no tiene efecto (veredicto `current`, rc=0); hoy rc=2 ...
...:441: AssertionError: PD-9 violada: un cambio de la parte `unit` da `impact` (rc=0); hoy rc=2 ...
...:492: AssertionError: PD-9 violada: un cambio de dependencia de la unidad da `impact` (rc=0); hoy rc=2 ...
...:518: AssertionError: PD-9 violada: un cambio de una parte `shared` da `impact` (rc=0); hoy rc=2 ...
...:547: AssertionError: PD-9 violada: el cambio de alcance da `impact` (rc=0); hoy rc=2 ...
...:581: AssertionError: PD-8/PD-10 violada: editar la sección de autorización da `impact` (rc=0), nunca `impeded` (rc=2); hoy rc=2 ...
...:306: AssertionError: PD-10 (aprobación retirada): el resultado es un error de uso del CLI ('invalid choice'), no el comportamiento del contrato ...
...:306: AssertionError: PD-10 (delegación revocada): el resultado es un error de uso del CLI ('invalid choice'), no el comportamiento del contrato ...
...:717: AssertionError: PD-7 violada: el veredicto debe emitirse (rc=0); hoy rc=2 ...
...:760: AssertionError: PD-7 violada: sin línea base el veredicto es `current` (rc=0); hoy rc=2 ...
...:815: AssertionError: PD-11 violada: el bloque debe informar la línea base: {'changed_parts': [], 'live': None, 'mode': 'projection', 'reason': None, 'registered': None, 'unit': '999-001-fixture-unit', 'verdict': None}
...:851: AssertionError: PD-9 violada: el veredicto debe emitirse (rc=0); hoy rc=2 ...
...:907: AssertionError: INV-8/PD-10 violada: la prosa restrictiva de una parte `shared` da `impact` (rc=0), nunca `impeded`; hoy rc=2 ...
...:931: AssertionError: PD-11 violada: el veredicto debe emitirse (rc=0): "ERROR: ... invalid choice: 'validate-unit-contract' ..."
```

The two `impeded` tests assert rc=2 first (today's usage error satisfies it) and then fail on `_no_usage_error` — the domain rejection with the existing marker and the named exit — so they fail for the right reason (missing contract behavior), not because rc≠2. The 15 names are exactly those listed in (a).

## (d) Commit

- `c61db34` — `test: 005-013 T2 RED — focal del veredicto de consecuencias (PD-7..PD-11, AC-5..AC-7)` (branch `codex/epic-005-real-operation`; 1 file changed, 942 insertions; `git show --stat` limited to `tests/`). `docs/.cdad-state.json` was already modified by the orchestrator and was **not** committed (out of my write scope).

## (e) Points where I stopped / declared inferences

I did not stop; no contract point contradicted what the fixture can observe. Declared items (all observed black-box, never reading implementation):

1. **`validate-unit-contract` does not exist yet** (probed `--help`: only `validate-state, validate-policy, render, validate-request, validate-packet, prepare, open-unit, validate-metric, status`). T1's projection/publication/pin and the `unit_contract` block already exist (from commit `021a491`), so the T2 tests target the missing verdict machinery: the block currently reports `registered: null`, `live: null`, `verdict: null`.
2. **Part identity in `changed_parts`** is *inferred* from the contract (spec fixes the classes `unit`/`shared` and that `changed_parts` names "las partes que difieren", but not the literal identifier): I assert `unit` for the unit part and the section title for a `shared` part. Flagged for the implementer/reviewer.
3. **`validate-unit-contract` stdout format** is not fixed by the spec beyond "emite el veredicto … con las partes que difieren"; I assert the verdict token appears in stdout+stderr, plus rc and the durable journal (whose shape *is* fixed).
4. **Revoked-delegation marker**: the spec names `state incoherent`/vigencia; I assert `state incoherent`.
5. **Two successive packets** are produced by clearing the active packet (declared orchestrator transition between substages) and running `prepare --role architect --substage draft`; `--replace-packet` was probed and refuses without verifiable obsolescence (the projection is immutable), so it is not usable for this.
6. **"No registered projection → current"** fixture reaches the pre-first-packet state by publishing the execution then removing the packet directory; `validate-state` stays green (rc=0), so it is a valid state, and it is declared in the test docstring.
7. I ran only the focal (per the full-suite policy: the closer runs the full suite); the declared regressions were not run here.
