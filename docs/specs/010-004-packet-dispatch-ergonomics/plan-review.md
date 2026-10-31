# plan-review: 010-004 packet-dispatch-ergonomics, spec draft plan_version 4

- **Object reviewed:** `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`. Form: spec. Kind: draft-plan. plan_version 4.
- **Digest:** `054d4657b5dae096114a9e41beaad3c356234fe8fd5c60236752c24c89212008`, recomputed with `sha256sum` at the start and end of this review. It matches the contract.
- **Packet:** `010-004-packet-dispatch-ergonomics-reviewer-plan-review-005` · execution `exec-010-004-packet-dispatch-ergonomics-001` · HEAD `63650f51`.

**Verdict:** this is a review, not an approval. There are **0 BLOCKING** and **3 OPTIONAL** findings.

- **N-2, N-3 and O-C are closed** against their closure conditions.
- **No blocking regression came from the seven hunks.** New finding N-4 is a real overstatement, but it is OPTIONAL because I could not show that the case is reachable.
- **Earlier closures are kept:** N-1, B-1, B-2, O-1 to O-5, O-A, O-B, I-4 and I-5. I did not re-examine them except where a hunk touched the same text.
- **`owner-decision-v2-new-assignments.md` was not reopened.**
- **§2.1 stays pending for Pablo.** This review does not resolve it.

## Intake (route C)

```
python3 -B scripts/cdad_packet.py render --request $P/REQUEST.json --execution-context $E > /tmp/opencode-render-005.md → rc=0
cmp /tmp/opencode-render-005.md $P/PACKET.md                                                         → rc=0 (identical)
python3 -B scripts/cdad_packet.py validate-request --request $P/REQUEST.json --execution-context $E  → rc=0
python3 -B scripts/cdad_packet.py validate-packet --request $P/REQUEST.json --execution-context $E --packet $P/PACKET.md → rc=0
sha256sum docs/specs/010-004-packet-dispatch-ergonomics/spec.md                                      → 054d4657…212008
```

- **Paths:** `P=.cdad/packets/010-004-packet-dispatch-ergonomics-reviewer-plan-review-005` and `E=.cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json`.
- **Metadata:** packet_id, execution_id, execution_context, request, packet and contract (path, sha256, plan_version, object_kind) match REQUEST.json and PACKET.md.

## Materialization of the seven hunks

- The commit that touched the spec is `869bf987`. Its parent version has digest `051ab1de…`, the base the patch declares.
- `git diff eebc08dd -- spec.md` has 7 hunks. With the `diff`, `index`, `---`, `+++` and `@@` lines removed, it equals `.cdad/inbox/010-004-architect-draft-004-original.patch` (`diff` rc=0).
- The working-tree file matches the version committed at `869bf987` (same digest).

## Closure of the requested findings

| Finding | Status | Grounds |
|---|---|---|
| N-2 | **Closed** | All four conditions at `plan-review.md:85-89` are met; see below. |
| N-3 | **Closed** | All four conditions at `plan-review.md:106-110` are met; see below. |
| O-C | **Closed** | The §8 table is contiguous at `spec.md:474-487`, with no blank line inside it. |

**N-2:**
- The case is named at `spec.md:205` and in its own row at `:222`.
- The cause and the escalation to the owner are stated at `:205`, `:222`, `:352` and `:414`.
- State stays untouched and v1 is not prepared, at the same lines.
- PC-07b and §4.5 give one observable result (`:414`, `:352`).
- `:222` forbids offering "completar o fallar" as a procedure, and no migration or v1 withdraw is added.
- The code supports this for `prepared`: `_record_dispatch` refuses a v1 context ("dispatch registration requires an active v2 execution context"), and reception acts only on `dispatched` (`cdad_result.py:702-706`).
- The citations `owner-decision-v2-new-assignments.md:7,13` point to the correct paragraphs.

**N-3:**
- The amended clause is cited at `spec.md:453`, with the decision as authority. `docs/specs/004-002-project-execution-bootstrap/spec.md:115` does contain "conserva su intake".
- Both tests are listed at `:457-458`, and I checked their line ranges and expectations by reading them.
- The test-writer owns the audit and the traceable update (`:460`).
- The implementer does not edit tests, the update is not deferred to closure, and the historical spec stays intact (`:453,460`).

**§9 traceability:** rows for N-2, N-3 and O-C were added at `:505-507` and are accurate.

## Findings

### N-4: the "no route" wording also covers `dispatched`, where a route exists
**Verdict: OPTIONAL · Bucket: m · Severity: Consider (correctness)**

**Evidence:**
- `spec.md:205,222,352,414` give one outcome for every non-terminal v1 active packet, "incluido `prepared`". `ACTIVE_PACKET_STATUSES` is `{"prepared", "dispatched"}` (`cdad_packet.py:177`), so `dispatched` is included.
- `cdad_packet.py:6218` lets `prepare` continue past a `dispatched` packet that has a durable receipt.
- `cdad_result receive` takes its context explicitly and validates a v1 context.

**Reproduced** in a throwaway project built from the v1 fixture in `tests/test_004_002_t6_landing.py`. I set `dispatched` by editing that project's state by hand.

| Step | Result |
|---|---|
| No policy, plain `prepare` (test-writer/red) | rc=0, v1 packet `-001` |
| `cdad_result receive` with `.cdad/execution.json` | rc=0, receipt written, status stays `dispatched` |
| Proposed policy materialized, plain `prepare` | rc=2, "requires --new-execution" |
| `prepare --new-execution` | rc=0, publishes `-002` on a new v2 execution |

**Consequence:**
- The sentence "no hay una ruta CLI terminal existente" is false as a description of how to unblock this case.
- It also conflicts with `:195`, where v1 re-entry keeps its explicit existing routes, and with the line in §4.6 that keeps reception in force.
- Read literally, PC-07b would lead a test or implementation to block a continuation that works today.

**Why it is not BLOCKING (calibration rule 5):**
- I found no CLI path that takes a v1 packet to `dispatched`. `_record_dispatch` refuses v1 in the current code and in `81ee8d3c`, the earliest version I checked.
- The only reachable non-terminal v1 state I could show is `prepared`, which is the case N-2 reproduced.
- If real v1 projects hold `dispatched` packets, this should be re-rated, and the owner decides that.
- The wording originates in N-2's own framing and in `orchestration-review-v3-corrections.md:7`. It is not an architect error.

**Remedy (text only, no mechanism):** limit the gap to `prepared` and to `dispatched` with no verified durable receipt, and state that `dispatched` with a receipt keeps the existing behaviour.

### N-5: two continuation rows apply to the same case, with no precedence
**Verdict: OPTIONAL · Bucket: m · Severity: Consider (correctness)**

**Evidence:**
- A legacy project with no policy and a v1 `prepared` packet matches both `spec.md:220` (propose a policy) and `:222` (escalate).
- PC-07b calls the second a "único resultado observable" (`:414`).
- Today's selection reads policy before the active-packet guard (`cdad_packet.py:2937-2942,6203`). The N-2 reproduction began from this state.

**Consequence:**
- Both outcomes keep state intact and prepare no v1, so no guarantee is lost.
- The owner may be asked to materialize a policy, only to hit the block next.
- The test-writer has to pick an expectation that the spec does not decide.

**Remedy:** state which diagnostic comes first, or make clear that "único" applies once policy exists.

### N-6: §4.6 was left with the unqualified wording
**Verdict: OPTIONAL · Bucket: h · Severity: Nit (consistency)**

**Evidence:** `spec.md:374` still says "orientar hacia el procedimiento existente" with no "solo cuando sea aplicable", unlike `:223` and `:352`. This line governs the instruction text.

**Consequence:** the instructions could promise a route the rest of the spec denies. The specific text at `:205` and `:222` limits the risk.

**Remedy:** align the qualifier.

## Checked areas with no finding

- **No new scope:** the hunks add no mechanism, gate or exclusion, and §3 and §10 are unchanged.
- **Owner decision:** the hunks do not widen it. "Se acepta… esta laguna" at `:205` is draft text that becomes binding only if the owner approves the spec, and it does not approve anything itself.
- **§7:** "conservando las garantías aún vigentes" (`:460`) preserves the v1 recognition and re-entry guarantees.

**FYI, not a finding:** `spec.md:3` still says "borrador v3". No hunk touched it and it is outside this mandate.

## Abstentions

- **Whether real v1 projects hold `dispatched` packets:** no real v1 project was inspected. The result also could not settle this: `cdad_result`, `--record-dispatch` and the v2 bootstrap all first appear in one squashed commit, `81ee8d3c`, so the order they arrived in cannot be recovered.
- **Whether `receive` fits every v1 role and substage:** I ran only test-writer/red, with a minimal descriptor.
- **Exhaustive list of affected tests:** assigned to the test-writer (`:460`). I did not build it.
- **The two tests named in N-3:** read, not run, as the packet does not ask for them.
- **Table of current decisions / `docs/adr/`:** the packet declares no `current_decisions`, and I did not review the ADR set.
- **Earlier simulations:** not repeated, per mandate. N-2 rests on the prior reproduction (`plan-review.md:67-74`) plus reading the code.
- **Reader model versus author model family:** unknown.
- **§2.1:** owner's decision.

## Evidence

- **Files modified:** none (`write_scope: []`).
- **Commit:** none.
- **Temporary writes, all outside the repo and deleted:**
  - `/tmp/opencode-render-005.md`
  - `/tmp/rv005`, holding the simulation script, the throwaway project, its hand-edited state and its receipt
- **Commands beyond intake:**
  - `sed`, `grep` and `read` over the spec, plan-review, owner decision, mandate, architect final text and patch, `cdad_packet.py`, `cdad_result.py`, `project-execution.md`, `stage-4-review.md`, the 004-002 spec and the cited tests.
  - `git diff`, `git show` and `git log` for hunk identity and chronology.
  - One throwaway simulation, `python3 -B sim.py test-writer red`, using `scripts/cdad_packet.py` and `scripts/cdad_result.py`.
- **Failed attempts, reported as they happened:**
  - The first runs of `sim.py` died with `TypeError: can only concatenate tuple (not "list") to tuple`, a bug in my script.
  - `sim.py reviewer plan-review` → `prepare` rc=2, "plan-review subphase requires a draft-plan contract: an approved contract is not the object this procedure reviews (PD-2)". This was a fixture mismatch, not a product finding.
- **No full suite, generation, install or push.**
- **Final git state:**
  - `git rev-parse HEAD` → `63650f51c10a400711aa34e23ba412f95c4edbf7`
  - `git status --short` → `?? docs/specs/010-000-continuity-relative-root/discovery.md`, which was already there
  - `git diff --exit-code` → 0
  - `git diff --cached --exit-code` → 0
  - `sha256sum` of the spec → `054d4657b5dae096114a9e41beaad3c356234fe8fd5c60236752c24c89212008`

**Draft not approved. This review authorizes no implementation.**