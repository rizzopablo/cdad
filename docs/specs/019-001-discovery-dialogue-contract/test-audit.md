Audit report — 019-001 discovery dialogue contract (test-writer, AUDIT)

Scope read: approved contract `docs/specs/019-001-discovery-dialogue-contract/spec.md` (sha256 `80d26ba7...`) and `tests/`. Implementation code was not read.

Modified files: none (audit is read-only).

Existing verifier inventory and contribution assessment:
- `tests/test_010_001_documentary_contracts.py` — protects the shared documentary norm, categories, locators, role boundaries and pointer/uniqueness rules. It does not protect any 019-specific postcondition; it is an adjacent structural control.
- `tests/test_010_002_documentary_role_integration.py` — protects documentary engagement applicability, role binding, dispatch doctrine and agent distribution. It preserves role boundaries, but does not verify 019's discovery-dialogue fidelity behaviors.
- `tests/test_010_003_documentary_pilot.py` — structural pilot only; not a 019 semantic oracle.
- Existing controls that must stay green and should not be duplicated:
  - `tests.test_006_004_u3_principle_single_source` uniqueness/ceiling controls
  - `tests.test_cdad_generate` eleven-agent-per-runtime control
  - `tests.test_packet_prepare` Claude barrier control

Mapping of 019 postconditions to existing protection:
- PC-1 … PC-12: no existing test protects them directly.
- Protected controls relevant to 019 activation remain PC-16-style agent/boundary controls, not 019 semantic acceptance.

Disposition per test:
- All existing tests above: Mantener. They protect their own approved contracts; extending them for 019 would create a second oracle for the same observable behavior.

Missing protection / pending behavioral verification strategy:
- One new documentary verifier under `tests/` should be derived from the approved 019 contract and admitted inputs, never from the future produced design.
- One test per observable promise, not per postcondition:
  1. Promise A — role assignment, mediated round trip, and required activation boundary changes.
  2. Promise B — handoff distinguishes confirmed answers, unaccepted proposals, consequential unknowns, technical evidence and corrections; fresh-session recovery.
  3. Promise C — readiness rules and unambiguous route to drafting, independent review and explicit approval.
  4. Promise D — supported lightweight surfaces and proportionate obligations.
  5. Promise E — canonical ownership map and actionable activation handoff, including architect-brainstorm incompatibility, draft re-entry bypass, frozen-packet behavior and idle/status consistency.
  6. Promise F — worked examples with acceptable/unacceptable alternatives, plus acceptance protocol separating structural verification, semantic review, illustrative examples and observed evidence.
- Structural checks may verify references, file presence and ownership maps; they cannot establish semantic fidelity. Independent semantic review remains separate.
- No new role, state field, gate, communication service or packet field may be introduced by the design or tests.

Commands run:
- `python3 scripts/cdad_packet.py validate-request ...` → rc 0
- `python3 scripts/cdad_packet.py validate-packet ...` → rc 0
- `python3 -m pytest -q tests/test_010_001_documentary_contracts.py tests/test_010_002_documentary_role_integration.py` → 40 passed in 56.41s
- `git diff -- tests` → no output

Commit: none created (audit makes no test changes).