# FINAL TEXT — implementer GREEN T2 (017-001-suite-performance): BLOCKED, mismatch reported, no implementation written

## 1. Route C validation — PASS (before working)

- Dispatch identification block equals the canonical render byte-for-byte: `python3 scripts/cdad_packet.py render --project-root … --execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json --request .cdad/packets/017-001-suite-performance-implementer-green-002/REQUEST.json --route C` reproduces the prompt block exactly (`packet_id` 017-001-suite-performance-implementer-green-002, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`).
- Full render byte-identical to `PACKET.md` (9109 bytes, `cmp` clean); `validate-request` and `validate-packet` both exit 0.
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture. Full cycle skills not loaded.
- Proceeded on Route C, substage `green`, packet inputs/scopes only.

## 2. Scope respected

- Reads only: `docs/specs/017-001-suite-performance/` (spec, mapping, scope JSON, red-T2-markers-fix), `scripts/cdad_suite_observer.py`, `scripts/cdad-suite.py`, `tests/suite_operation_markers.py`, both T1/T2 test files (read-only, as contract).
- **Zero product edits, zero commits.** `git status` shows only the orchestrator's pre-existing `docs/.cdad-state.json` transition (red-006 completed → green-002 prepared, dated before this session). Product diff by me: empty.

## 3. Baseline evidence (commands run, outputs kept)

- T2 focal (RED confirmed, matches the declared oracle):
  `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py` → **3 failed, 1 passed in 3.61s** (P1 fails on `operations: []`, P2 fails on no capture with rc≠0 preserved, P3 passes as designed control, P4 fails at line 349: mark-less close yields `status complete`, oracle demands `incomplete`).
- T1 focal (must be conserved per packet: "diecisiete protecciones"):
  same invocation over `tests/test_017_001_suite_profile.py` → **17 passed in 19.98s** (9 + 8 matrix params).
- `python3 scripts/cdad-suite.py validate` → rc 0.
- Suite completa no realizada (focal cycle only; no authorization for a complete run claimed).

## 4. Blocking mismatch: packet rule (4) contradicts the approved T1 oracles — no contract-grounded implementation exists

Packet objective §(4) orders: *"scope has committed families + zero captured operations → status incomplete with non-empty diagnosis"*. The committed scope (`performance/operation-scope.json`: 8 committed families, waits unknown) resolves identically for every `close` from this CLI. Implementing rule (4) in `build_profile` flips **6 of the 17 T1 protections** from `complete` to `incomplete`:

- `test_incomplete_measurement_is_diagnosed_not_presented_as_contract` (R4-clean, `test_017_001_suite_profile.py:296`: mark-less `["test_pass","test_skip"]` → `complete`),
- skip-clean (`:527`: mark-less `["test_skip"]` → `complete`),
- 4× matrix-clean (`:827`: mark-less single selections → `complete`).

T2 P4A (`test_017_001_suite_operations.py:349`) demands `incomplete` for a run that is **indistinguishable from close's perspective**: same CLI binary, same resolved scope file, zero emitted marks (helper not importable in the synthetic child), complete phases, rc 0. Any implementation that returns `incomplete` for P4A and `complete` for the T1 runs must key on a test-harness artifact, not a contract signal. Enumerated and rejected:

- conftest-sentinel presence / `SUITE_PROFILE_PYTEST_SENTINEL` env (present in T1 workspaces, absent in T2) — harness scaffolding, semantically void;
- SAMPLE body contents (5 tests vs 1) and selection composition — the status of a measurement cannot honestly depend on how many dummy tests a fixture wrote;
- nodeid-name matching against committed selections — would exempt P4A itself (synthetic `test_pass` matches no `C-*` selection), so it cannot even make P4 pass.

All of these are test-gaming (fitting the implementation to the oracle instead of the contract), against R5/honesty and the packet's own "follow the contract" mandate. I will not implement any of them, and per role contract I do not edit tests to dissolve the conflict.

Spec grounding for the diagnosis: spec §4.4 orders *"un recorrido no ejercitado se distingue de un fallo de captura; si falta un intervalo **que debía emitirse**, la medición queda incompleta"*. Neither T1's synthetic selections nor P4A's synthetic `test_pass` exercise any committed recorrido (`C-R/C-E/C-U1/C-U4/C-U3/C-D`), so per spec neither "debía emitir" — P4A's oracle treats non-exercise as capture failure, which the spec expressly distinguishes. (Consistent with this, the AUDIT record already notes R4's standing assertion that phases-without-operations do not satisfy calibration — at calibration level, not as per-profile `incomplete` for non-exercising selections.)

## 5. Direction requested from the orchestrator (any one unblocks GREEN)

- **(a)** Re-scope rule (4) per §4.4 — zero-capture → `incomplete` only when the selection exercises a committed recorrido that should have emitted; **(b)** test-writer revises P4A to the spec-consistent oracle for non-exercising selections (phases-OK → `complete`, with the scope contrast recording recorridos-no-ejercitados; `incomplete`+diagnosis reserved for expected-but-missing intervals); or **(c)** owner-level revision of the closed T1 oracles. My recommendation is (a)+(b): they preserve all 17 T1 protections, keep P4's genuine capture-failure direction, and match the spec's exercised-vs-captured distinction.
- On receipt of the revised packet/oracle I will implement the operations sink, monotonic observer clock, interval nesting, `operation_scope` reference (path+sha256+status), and the scoped diagnostic rule in `scripts/` only, then run T2 focal + T1 focal + proportional regression + `validate` with full evidence.

## 6. Role evidence summary

- Modified files: **none**. Commit: **none**. Product diff: **empty**.
- Test files untouched (read-only). Contract, scope registry, seam helper, and oracles untouched.
- Full-suite policy: suite completa no realizada — executed selection is T2 focal (3F/1P, RED as declared) + T1 focal (17/17 green, conserved baseline) + `validate` (rc 0); limits: no complete-suite run, no implementation change pending the orchestrator's decision on §4 above.
