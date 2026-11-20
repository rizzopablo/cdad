## Report — implementer / GREEN (006-005 U6-5)

**Status: BLOCKED — one approved oracle contradicts another. Stopped per the packet instruction ("Si un oraculo aprobado contradice otro, detenete y reportalo; no edites tests"). I did not edit `tests/`. I did not commit.**

The implementation is complete; **10 of 11** focal oracles are GREEN, and the single remaining failure is an assertion that is logically incompatible with oracle 8 of the same approved RED and with D-U65-1's last bullet.

---

## 1. Modified files (implementation only)

| File | Change |
|---|---|
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (+61/−4) | Provisional **write-ahead** I8 record written after preflight + prior-attempt check + session choice and **before** `_invoke_destination`; fail-closed `blocked` (client never launched) if it fails; the existing per-termination `register_note` / `_persist_delivery` calls are now the **single completion** of that record. Docstring §8 + `register_note` docstring updated. |
| `skills/cdad-cycle/scripts/cdad_packet.py` (+86/−9) | `_record_dispatch` accepts **exactly one** completion over a record whose `provenance.session` starts with `write-ahead:`: incoming observation unmarked + fixed identity (`execution_id`, `packet_id`, role, substage, runtime, `started_at`) ⇒ atomically replaces it with a final record. A final record, a marked "completion" and a changed identity are rejected with the pre-existing write-once diagnostic. Nothing else in the rule changed. |

Provisional record shape (O-4, verified by `assert_provisional_shape`):
`provenance.session = "write-ahead: provisional: the observation is completed ONCE at termination; store=configured sessions_db; row=unknown; store_reads=unknown; prior_check_reads=<n>"`, `session` = chosen id, `model_reported: null`.

`reconcile`, `disposition` and the prior-attempt check are **untouched** (D-U65-3).

## 2. Test → result

| Command | Result |
|---|---|
| `pytest tests/test_006_005_u6fix5_write_ahead.py -q` | **1 failed, 10 passed** (17.15 s) — only oracle 3's `len(after)==1` |
| `pytest tests/test_006_005_u{1a,1b,1c,2,3,3b,4,5,u6fix1,u6fix4,u7}_*.py -q` | **105 passed** (131 s) |
| `pytest tests/test_006_001_t2_wait_recovery.py test_packet_prepare.py test_005_010_t1_durable_signal.py test_005_010_t4_integration.py test_005_010_reviewfix.py -q` | **46 passed, 1 skipped** (110 s) |
| `pytest tests/test_005_009_t1_interface.py test_006_001_t1_selection.py test_006_001_t1b_service_mode.py test_006_003_u6_server_credential.py test_006_003_u8_acceptance.py -q` | **1 failed, 48 passed** — see §4 (load flakiness, A/B verified) |
| `pytest tests/test_004_002_t4_dispatch.py test_005_009_t2_opencode_adapter.py test_005_009_t4_acceptance.py test_005_010_t2_load_mode_invocation.py test_005_007_t5_delegation_dispatch.py test_006_002_u5_transport_equivalence.py test_006_003_u4_delegation_config.py -q` | **51 passed, 1 skipped** (110 s) |
| `make validate` | **168 PASS / 1 FAIL → `F011: scripts/validate-subagents.sh (active profile)`** — declared environmental (F011), pre-existing |
| `git diff --check` / `py_compile` both scripts | clean |

The 10 GREEN oracles include the RED's 5 declared failures except 7a (now GREEN): crash-midrun, crash-before-launch, write-ahead failure (fail-closed, 0 `run` invocations), and the ledger's first completion. The 6 declared GUARDs (4, 5a, 5b, 7b, 7c, 8) stayed GREEN.

## 3. The contradiction (evidence)

Failing assertion — `tests/test_006_005_u6fix5_write_ahead.py:1324`:

```
AssertionError: 2 != 1 : PD-1: el re-despacho bloqueado no debe registrar un segundo intento:
['opencode-6e3d4c6fc985', 'opencode-71692350e1b6']
```

The two records after the blocked re-dispatch (measured from a scratch copy under `/tmp/opencode`, `tests/` untouched):

```
DIAG opencode-6e3d4c6fc985 session='ses_5ade…' mark='write-ahead: provisional' …
DIAG opencode-71692350e1b6 session=None  term_source='not dispatched; store=configured sessions_db; row=absent; store_reads=unknown; prior_check_reads=1'
```

The second record is **exactly** the "terminación anterior al write-ahead (intento previo vivo) registra como hoy, un registro final" that D-U65-1's last bullet mandates, and that **oracle 8 of the same approved RED asserts**:

- `u6-5-decision.md:34`: *"Una terminación anterior al write-ahead (preflight, **intento previo vivo**, request inválido) registra como hoy, en esa terminación, un registro final y no provisional."*
- Oracle 8 (`test_u65_termination_before_write_ahead_is_not_provisional`) blocks on a live prior attempt and asserts `len(records) == 2` — it passes. Measured: same state (`active_packet.status == 'dispatched'`), same code path (`blocked_before_dispatch` → `register_note`).
- Oracle 3 is the same termination class (prior attempt live ⇒ `blocked`, no `run`) and asserts `len(records) == 1`.

No implementation can satisfy both: both terminations are `blocked_before_dispatch` from `_prior_attempt_check`, in identical state. The only way to make oracle 3 pass is a rule not in the contract — skip registration when the blocking record is *provisional* but not when it is *final* — which would contradict D-U65-1 and break oracle 8. I did not invent it.

**Options for you (orchestrator):**
- **(A, recommended) test-writer testfix of oracle 3**: change the final assertion to `len(after) == 2` and assert the *new* record is final (`session: null`, no mark) while the provisional one is untouched — preserves oracle 8 and D-U65-1 verbatim. Everything else is already GREEN.
- (B) An explicit contract amendment making a blocked re-dispatch not register; this overturns D-U65-1's last bullet and requires rewriting oracle 8 (a contract change, not this substage).

## 4. Honest limitations declared

- **Load flakiness (pre-existing, A/B verified).** `tests/test_006_001_t1_selection.py` occasionally exceeds the fixture's 2.0 s interface bound under host load (load average **23.5** on 8 cores). Isolated: `-k same_errand_in_server_mode` **6/6 passed** and `-k client_stderr_url_redacted` **6/6 passed** with the change; whole-file runs: **1 failure / 3 runs with the change** vs **1 failure / 3 runs at HEAD** (clean `git archive` copy). Different tests fail on different runs ⇒ environment, not the change. The write-ahead adds ~0.25 s (measured `cdad_packet.py --help` = 0.246 s median) and was deliberately placed **before** `remaining_for_invoke` is computed so the client's budget absorbs it (PD-11).
- `make validate`'s only failure is **F011** (`validate-subagents.sh`, active profile), environmental and pre-existing.
- Full suite not run (policy: the closer runs it once).

## 5. Commit

**Not created.** The commit was contingent on the GREEN gate; it is not met because of the contradictory oracle. The working tree holds the reviewed diff above (`git diff --stat`: 2 files, +136/−11), ready to commit unchanged as `fix: 006-005 U6-5 — registro write-ahead del intento externo` as soon as the oracle is rectified. Untracked `docs/planning/` and `findings/incremental-construction-and-reproducible-validation-2026-10-17.md` are pre-existing and were not touched.