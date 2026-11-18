RED complete for Promise A (PC-1, PC-2) of approved 019-001.

- **Modified files:** `tests/test_019_001_discovery_dialogue_contract.py` (new, 128 lines).
- **Exact command:** `python3 -m pytest -q tests/test_019_001_discovery_dialogue_contract.py`
- **Output:** `1 failed in 0.10s` — `AssertionError: PC-1/PC-2: el directorio del producto documental no existe: docs/specs/019-001-discovery-dialogue-contract/operating-design` (right-reason failure, not import/syntax).
- **Commit:** `fc029f678960f5b0579506f464b920ddad7463b1`.

Live inventory addition (text):
- **nodeid:** `tests/test_019_001_discovery_dialogue_contract.py::TestPromiseA::test_promise_a_role_assignment_and_activation_boundaries`
- **capability:** documentary RED for Promise A — role assignment to named existing roles/authorities, mediated round trip without fictitious direct interaction, and role-boundary changes for activation with preserved prohibitions (PC-1, PC-2).
- **contract:** `docs/specs/019-001-discovery-dialogue-contract/spec.md` (sha256 `80d26ba7826fe94c85329953014ff013281f843d2ddf1211e7c11675201f0539`).
- **provenance:** approved contract + `red-selection.md` (Promise A selected) + `test-audit.md` (no existing protection for PC-1/PC-2; all prior tests Mantener).

Map deltas: none — no prior test protects PC-1/PC-2; no substitution/consolidation applied. Implementation code was not read.