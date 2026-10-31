# plan-review: 010-004 packet-dispatch-ergonomics, spec draft v3

- **Object reviewed:** `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`. Form: spec. Kind: draft-plan. plan_version 3.
- **Digest:** `051ab1de12ce14d762195253b976d237082eb527ad1671aea224f230fa04d62d`, recomputed with `sha256sum` at the start and end of this review; it matches the contract.
- **Packet:** `010-004-packet-dispatch-ergonomics-reviewer-plan-review-004` · execution `exec-010-004-packet-dispatch-ergonomics-001` · HEAD `eebc08dd`.

**Verdict:** this is a review, not an approval. I found **2 BLOCKING** and **1 OPTIONAL** findings.

- **N-1 is closed.** The owner's rule that everything new is v2 and C is v2-only is applied correctly.
- **The two blockers are new.** Both come from applying that rule to old projects, and both close with text only, with no new mechanism.
- **Earlier closures hold:** B-1, B-2, O-1 to O-5, O-A and O-B stay closed, and I-4 and I-5 are preserved.
- **§2.1 stays pending for Pablo.** This review does not resolve it.

## Intake (route C)

```
python3 scripts/cdad_packet.py render --request $P/REQUEST.json --execution-context $E > /tmp/opencode-render-004.md → rc=0
cmp /tmp/opencode-render-004.md $P/PACKET.md                                                                       → rc=0 (identical)
python3 scripts/cdad_packet.py validate-request --request $P/REQUEST.json --execution-context $E                   → rc=0
python3 scripts/cdad_packet.py validate-packet --request $P/REQUEST.json --execution-context $E --packet $P/PACKET.md → rc=0
sha256sum docs/specs/010-004-packet-dispatch-ergonomics/spec.md                                                    → 051ab1de…4d62d
```

- **Paths:** `P=.cdad/packets/010-004-packet-dispatch-ergonomics-reviewer-plan-review-004` and `E=.cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json`.
- **Failed attempt, reported verbatim:** `python3 scripts/cdad_packet.py validate --help` → `invalid choice: 'validate'`. It was a `--help` probe only.
- **Metadata:** packet_id, execution_id, execution_context, request, packet and contract (sha256, plan_version, object_kind) match REQUEST.json and PACKET.md.

## Materialization

I re-ran `.cdad/inbox/materialize-architect-v3.py` in a temporary tree, with base `ffef53bd:…/spec.md` and `architect-v3-proposal.md`.

- It printed base `8d2b948e…`, proposal `9f78a403…`, result `051ab1de…`, 45026 bytes.
- `cmp` against `spec.md` → rc=0, so the claims in `architect-v3-materialization.md:7-9` reproduce.

## Closure of earlier findings

| Finding | Status | Grounds |
|---|---|---|
| N-1 | **Closed** | C requires a v2 context in its canonical location, even for a historical request with no field (`spec.md:248`). v1 gets a specific diagnostic (`:249`). The verifier stays v2 and is not widened (`:251,254`). PC-02 gives one outcome (`:399`). The §4.4 row agrees (`:325`). This matches `cdad_packet.py:1975-1980,2945-2955`. |
| B-1 | **Closed** | One matrix for all three commands (`:150-163`). A historical request with no argument is rejected, with no fallback (`:159`). This is compatible with today's `required=True` (`cdad_packet.py:9485-9491`). |
| B-2 | **Closed**, narrowed to v2 by the owner's decision | Domain and identity at `:113-127`, rejection with no effects at `:409`, using the real `_project_path`. |
| O-1 to O-5 | **Closed** | Exclusive identification (`:262-275,306-312`), published request (`:246-247`), root and arguments (`:142-148`), PC-08a and PC-08b (`:417-419`), consumers delimited (`:86-88,97,138`). |
| O-A | **Closed** | Layers separated at `:129-138`, plus PC-06 (`:409`). `validate_request` is not credited with a path comparison, which it cannot do (`cdad_packet.py:1582-1584`). |
| O-B | **Closed** | The annex is labelled non-normative (`:522-524`). Labelling was one of the permitted options. |
| I-4 / I-5 | **Preserved** | §2.2, §2.3, PC-10 and PC-11 (`:35-48,425-427`). |

**Owner-decision fidelity:**

- All new preparation being v2 is covered at `:167-179`, PC-04 and INV-12.
- Line citations in the delta (`:2928-2942`, `:2898-2911`, `:6202`, `:6433-6441`) match the code.
- `_replace_packet` already loads by v2 identity (`cdad_packet.py:3413`), so `:177` is accurate. It builds the successor field by field (`:3530-3552`), so `:175` needs real work but is feasible.
- `--resume-packet` is correctly limited to v2 (`:195`).
- No closed-schema copy exists in other scripts: `plan_task` and `current_decisions` appear only in `cdad_packet.py`.

## Findings

### N-2: the v2 route for old projects depends on a mechanism that does not exist for a pending v1 packet
**Verdict: BLOCKING · Bucket: h · Severity: Required (correctness)**

**Evidence:**
- §4.1 step 5 says "Resolver previamente los bloqueos de paquete activo… por los mecanismos existentes" (`spec.md:205`).
- The continuation row says "resolverlo por el procedimiento existente aplicable" (`:222`).
- PC-07b promises cause, owner and continuation for this situation (`:413`).
- `prepare` is the only thing that writes `prepared`, and I found no CLI route that moves a v1 packet out of that status. `--record-dispatch`, `--replace-packet`, `--resume-packet` and `register-transition` all fail on the v2 loader or the v2 check.
- `cdad_result` only acts on `dispatched` (`cdad_result.py:702-703`).

**Reproduced** in a throwaway project built from the v1 fixture in `tests/test_004_002_t6_landing.py`:

| Step | Result |
|---|---|
| No policy, v1 packet `prepared`, a second plain `prepare` **today** | rc=0, publishes `-002` |
| After materializing the proposed policy: `prepare` | rc=2, "requires --new-execution" |
| `prepare --new-execution` | rc=2, "active packet … is 'prepared': complete or fail it before preparing a new packet (PD-4)" |
| `--replace-packet`, `--resume-packet`, `--record-dispatch`, `withdraw`, `disposition` | rc=2, "execution context not found: .cdad/executions/exec-consumer-legacy-v1/execution.json" |

**Consequence:**
- Today's second `prepare` works because the guard at `cdad_packet.py:6203` only runs for v2. That is the implicit path v3 correctly closes, so the active-packet blocker now applies to these projects as well.
- An old project whose last CLI step was `prepare` then reaches the exact case the owner wants to support. The person is told to "complete or fail" a packet that no command can complete or fail.
- The temptation left open is to edit the state by hand, which `:222` forbids.
- The test-writer cannot write this case deterministically, because the row cites a procedure that does not exist for it.
- The generic clause at `:226` (declare the gap and escalate) softens this, but it does not close it. The specific row points elsewhere. The owner also asked for "cualquier laguna real" to be identified and for an actionable continuation (`owner-decision-v2-new-assignments.md:7,13`).

**This is not a request for hardening.** No v1 withdraw, disposition or migration mechanism should be added; §3 excludes them.

**Closed when:**
- §4.1 names this case: a non-terminal v1 active packet has no existing CLI route.
- The continuation states the cause and escalates to the owner.
- It explicitly leaves the state untouched and does not prepare v1.
- PC-07b, or §4.5, gives one observable result for this case. If the owner wants any other outcome, that is their decision, recorded in the spec.

### N-3: the spec reverses an approved behaviour and its tests without tracing that change
**Verdict: BLOCKING · Bucket: h · Severity: Required (architecture / traceability)**

**Evidence:**
- `docs/specs/004-002-project-execution-bootstrap/spec.md:115` states that a representative legacy project "conserva su intake".
- `tests/test_004_002_t6_landing.py:606-642`, `test_pd12_legacy_without_policy_keeps_legacy_intake`, reads this as implicit `prepare` publishing a v1 packet with no policy, rc=0.
- `tests/test_packet_prepare.py:402-424`, `test_p2_default_execution_context_and_out_dir_under_project_cdad`, passes today on a flat `.cdad/execution.json` with no policy in the test. Its default context is the path being closed.
- v3 inverts this at `spec.md:173,179`, PC-04, §7.1. `grep -n "PD-12\|legacy"` found no mention of 004-002 PD-12 in the spec, and §7 and §9 name neither the amended clause nor the tests.
- There is precedent for tracing this: `tests/test_004_002_t2_bootstrap.py:695-702` records the PD-10 explicit-v1 retirement in `v1-fixture-trace.md`.

**Consequence:**
- GREEN correctly breaks tests belonging to other features, and the implementer cannot edit tests.
- The closing suite then fails, or the test-writer inverts approved tests with no named authority in the spec. A later reader sees 004-002 PD-12 and 010-004 contradicting each other.
- The owner's decision authorizes the change, so this is about traceability, not the rule itself.

**Closed when:**
- The spec cites the amended clause of 004-002 PD-12, with `owner-decision-v2-new-assignments.md` as its authority.
- It lists the tests whose expectation changes.
- §7 assigns their signed update to the test-writer stage.
- The historical spec is not edited.

### O-C: the §8 decision table is split by a blank line
**Verdict: OPTIONAL · Bucket: h · Severity: Nit (format only)**

**Evidence:** `spec.md:474` is blank, so rows `:475-478` have no header and render as plain text. They are the decisions added by v3. The meaning is intact.

## Checked areas with no finding

- **No unjustified expansion:** every addition traces to the owner's decision. No hardening was added beyond it, and §3 and §10 keep their exclusions.
- **Consumers:** `cdad_delegate_opencode.py:2098` and `cdad_continuity` pass the canonical context explicitly, so the matrix does not change their behaviour.
- **Exit codes:** a missing argument is rc=2 today through argparse. A `PolicyError` is also rc=2, so `:355` is feasible.

## Abstentions

- **Table of current decisions / `docs/adr/`:** the packet declares no `current_decisions`. I only skimmed ADR-012 for v1 mentions and did not reopen the ADR set.
- **How common N-2 is in real projects:** I did not inspect any real v1 project. Some may have edited their state by hand.
- **Whether a completed or failed v1 packet bootstraps cleanly:** covered in part by `test_pd10_new_execution_flag_creates_v2_leaving_v1_intact`, which I read but did not run.
- **Exhaustive list of affected tests:** N-3 names what I verified. The closing list is the test-writer's job.
- **`test_pd12_…` was not run:** its install setup exceeded the 120 s timeout. My evidence is its assertions plus the rc=0 reproduction on the same fixture.
- **Each runtime's ability to export the received message, interoperability between installed versions, and the PC-12 isolated consumer:** not checked or not run. §10 covers the first two.
- **Reader model versus implementer model family:** unknown, so I did not count that point in the bucket.
- **§2.1:** owner's decision.

## Evidence

- **Files modified:** none (`write_scope: []`).
- **Temporary writes, all outside the repo and deleted:**
  - `/tmp/opencode-render-004.md`
  - `/tmp/rv4` and `/tmp/rv5`, holding simulation scripts and a copy of the materialization script
  - `/tmp/rv4-*`, `/tmp/rv4m-*` and `/tmp/rv5-*`, holding throwaway projects
  - A timed-out pytest run may have left its own fixture directory in the system temp folder; I did not check for one.
- **Commands beyond intake:**
  - `sed`, `grep` and `read` over `cdad_packet.py`, `cdad_result.py`, `cdad_delegate_opencode.py`, `project-execution.md`, `project-start.md`, the 004-002 spec and the cited tests.
  - The materialization re-run above.
  - Two throwaway-project simulations. Their scripts were written inline and removed afterwards, and they imported `tests/test_004_002_t6_landing.py` as a fixture with bytecode disabled.
  - `pytest tests/test_packet_prepare.py -k test_p2_default_execution_context` → 1 passed.
  - `pytest tests/test_004_002_t6_landing.py -k test_pd12_legacy_without_policy` → timed out at 120 s.
- **No full suite, generation, install or push.**
- **Final git state:**
  - `git rev-parse HEAD` → `eebc08dd2d98ad655910368a6ae326ce4e7579fe`.
  - `git status --short` → `?? docs/specs/010-000-continuity-relative-root/discovery.md`, which was already there.
  - `git diff --exit-code` → 0. `git diff --cached --exit-code` → 0.
- **Commit:** none.

**Draft not approved. This review authorizes no implementation.**
