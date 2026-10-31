# plan-review: 010-004 packet-dispatch-ergonomics, plan draft version 1

- **Object reviewed:** `docs/specs/010-004-packet-dispatch-ergonomics/plan.md`. Form: plan. Kind: draft-plan. plan_version 1.
- **Digest:** `9deee470f708a26d3e9418fcf0df5710693a510e7557d8e289494bcc349edd23`, recomputed with `sha256sum` at the start and end of this review. It matches the contract.
- **Spec pin (read only, not reopened):** `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`.
- **Packet:** `010-004-packet-dispatch-ergonomics-reviewer-plan-review-006` · execution `exec-010-004-packet-dispatch-ergonomics-001` · HEAD `2dffa9d095f55b6aa28269e9d85467e363d73113`.
- **Separate object:** this is not the earlier SPEC review (packet `-005`, digest `054d4657…`). `plan-review.md` stays as the historical record of that review.

**Verdict:** this is a review, not an approval. There is **1 BLOCKING** and **3 OPTIONAL** findings.

- **P-1 (BLOCKING):** the plan uses POST-AUDIT for the wrong procedure, so T5 can't be dispatched as written and T2 lacks the step that applies the audit.
- **T1:** its scope is sound. P-1 affects what T1 feeds into, not the AUDIT itself.
- **Everything else checked:** dependencies, RED/GREEN separation and the cited entry points hold up.
- **N-4, N-5 and N-6:** they remain OPTIONAL, open and deferred. I did not reopen them.

## Intake (route C)

```
python3 scripts/cdad_packet.py render --execution-context $E --request $P/REQUEST.json > ~/.cache/cdad-render-006.md → rc=0
cmp ~/.cache/cdad-render-006.md $P/PACKET.md                                                     → rc=0 (identical)
python3 scripts/cdad_packet.py validate-request --execution-context $E --request $P/REQUEST.json → rc=0
python3 scripts/cdad_packet.py validate-packet --execution-context $E --request $P/REQUEST.json --packet $P/PACKET.md → rc=0
```

- **Paths:** `P=.cdad/packets/010-004-packet-dispatch-ergonomics-reviewer-plan-review-006` and `E=.cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json`.
- **Identification:** project_root, packet_id, execution_id, execution_context, request, packet, and contract path, sha256, commit, plan_version and object_kind all match.
- **Disclosed gap:** the dispatched `contract` object omits `spec_path`, `spec_sha256` and `spec_version`, which REQUEST.json and PACKET.md carry.
  - The named metadata (packet_id, contract and its sha256, execution_id) all matched, and the published files passed full validation, so I admitted the packet.
  - This looks like a hand-composed identification. It is the problem `render --route C` is meant to remove.
- **Argument error:** my first `render` call omitted its required arguments and exited rc=2. It published nothing.

## Structural pass (mechanical; says nothing about quality)

| Check | Result |
|---|---|
| `plan-tasks` schema | `prepare` applies `_check_plan_tasks` and `_check_plan_validation_plan` to draft plans (`cdad_packet.py:6325-6337`). The packet exists, and by reading, the block satisfies both. |
| T1 `detail: next`, code-less | Has `observable_checks`, `regressions: []`, `integration_gate` and `owner` (`plan.md:85-99`). |
| T2–T6 `detail: planned` | Each has `objective`, `depends_on`, `uncertainty`, `owner` and `resolves_when`. |
| Dependencies | Linear T1→T6 with no cycle. `parallel` is empty, justified at `plan.md:19`. |
| Test references | Both T1 test names exist (`test_004_002_t6_landing.py:606`, `test_packet_prepare.py:402`). `test_role_packet_render.py:350` covers a tampered body and `test_role_packet_review_regressions.py:468` covers CRLF. |
| Generation entry points | `Makefile:10-18` matches. `build/staging` is gitignored, and `agents/` and `agents/claude-code/` are the promotion targets. |
| Suite entry point | `python3 scripts/cdad-suite.py close --help` confirms `--all` and `--evidence-root`. |
| Other citations | `orchestrator.md:274-281` is R4. `spec.md:129-165,319-335,513-524` and `owner-approval-2026-10-30.md:9-11` point to the right text. |
| Isolated install | `CDAD_INSTALL_ROOT` and `CDAD_SKILL_EXTRA_DIRS` exist in `install.sh:49,87`. |

## Findings

**Bucket derivation:** the whole object, spec and conventions were in context, and every rationale has exact citations. That gives 3 points, or `h`. The author's model family is unknown and scored 0. A plan has no diff, so I counted the complete object as the "full diff" point; without it the bucket is `m`.

### P-1: POST-AUDIT is assigned to the wrong moment and the wrong procedure
**Verdict: BLOCKING · Bucket: h · Severity: Required (correctness)**

**Evidence:**
- `plan.md:33,133` puts POST-AUDIT in T5, after GREEN, as an independent relevance audit. `plan.md:49` has the historical expectations updated "en RED".
- The canonical POST-AUDIT comes right after the approved AUDIT and updates existing tests:
  - `packets/substages/test-writer-post-audit.md`: "Apply only the approved audit changes to tests, verify every untouched test still passes, then add contract-mapped RED tests."
  - `handoff-prompts.md:220-225`: "a combined session of two sub-phases: POST-AUDIT + RED".
  - `handoff-prompts.md:334`: the plain RED template is for cases where POST-AUDIT does not apply. This feature has affected tests (`spec.md:455-460`).
- The relevance audit is a different control: a third isolated session or the Stage 4 reviewer (`stage-3-tdd.md:45-47,270`).
- In the sources I searched, nothing defines POST-AUDIT as a late relevance audit.

**Consequence:**
- A T5 `test-writer/post-audit` packet would tell the role to edit tests and add RED tests after GREEN, instead of auditing relevance. The plan's intent and the packet's instructions are incompatible.
- T2's `red` packet says only "smallest behavior-level test" (`test-writer-red.md`). It does not carry the duties to apply audited updates and verify untouched tests. Those are the duties `spec.md:460` depends on for the PD-12 substitution.
- `plan.md:133` also says "independientes cuando corresponda", which weakens a separation that `stage-3-tdd.md:270` requires for the exit gate.

**Closure condition:** all of the following are visible in the plan.
1. T2 starts with a post-audit (or post-audit + RED) dispatch after T1 is accepted and before GREEN.
2. T5 no longer uses POST-AUDIT. Its relevance audit is named as such and assigned to a session other than the test author, or moved to the Stage 4 test↔PC audit in T6.
3. The table (`:33`), the prose (`:49`) and the `plan-tasks` owners agree.

### P-2: full suite reserved for closure despite the rule's earlier triggers
**Verdict: OPTIONAL · Bucket: h · Severity: Consider (correctness)**

**Evidence:** `plan.md:36,72` reserves the suite for closure. Evidence-policy rule 2 (`stage-3-tdd.md:69-71`) says "or earlier if a change touches the installer, the staging pipeline or the renderer". T2–T3 modify the packet renderer's CLI, and T4 runs staging.

**Consequence:** a broad regression from the v2-only rule could surface only at T6, after T4 and T5 were built on it.

**Why it is not BLOCKING:**
- `spec.md:468` and `common.md` make the packet the place that asks for the suite.
- The plan defers to "conforme al paquete".
- The closure run still catches regressions.

**Closure condition:** the plan states whether T3 or T4 triggers an earlier full run, or records why not.

### P-3: PC-08a has no task that verifies it
**Verdict: OPTIONAL · Bucket: h · Severity: Consider (coverage)**

**Evidence:** PC-08a appears only in T1's separation (`plan.md:50`) and in a gate line (`:70`). T1 audits and does not verify. The rows for T2–T6 do not list it, while `stage-2-specification.md:192` asks for at least one task per postcondition. All other PCs are assigned: PC-01–02 and PC-04–07 in T2–T3, PC-03, PC-07b, PC-08b and PC-10–12 in T4, PC-09 across T2–T4, and PC-12 again in T5.

**Consequence:** a regression that is already green could go unowned until closure. The risk is low because of T3's "paquete íntegro" check and the final suite.

**Closure condition:** one task, naturally T3, names the PC-08a regressions.

### P-4: `--plan-task` on a `planned` task renders a false "none affected"
**Verdict: OPTIONAL · Bucket: h · Severity: Consider (usability)**

**Evidence:** `_plan_task_sections` prints "none declared (none affected)" for absent values and leaves the gate empty (`cdad_packet.py:5196-5204`). T2–T6 declare none of those fields. `plan.md:23,57` says detail is settled "antes del despacho" and in "cada paquete", but not where it is recorded or whether changing the plan needs new approval. This comes from reading the code; I did not run it.

**Consequence:** a T2 packet with `--plan-task T2` and an unchanged plan would tell the role that no regressions are affected, right where the plan expects many.

**Closure condition:** the plan says how a `planned` task becomes dispatchable: either the plan is updated to `next` with its approval effect stated, or detail travels in the packet without `--plan-task`.

## Checked areas with no finding

- **T1 scope:** the bounded reads, no edits, materialization by the orchestrator, PD-12 traceability and the PC-08a/PC-08b separation all fit `spec.md:453-465`.
- **RED/GREEN separation:** separate sessions and packets are declared, and the implementer does not edit tests (`plan.md:19`).
- **PROPERTIES and E2E:** separate dispatches, with an isolated installed consumer and no global install. POST-AUDIT is covered by P-1.
- **Mechanical vs semantic evidence:** kept apart (`plan.md:68-70`).
- **Owner decisions:** the plan keeps I-4/I-5, the exclusions and N-4/N-5/N-6 as approved, and adds no promises.

**FYI, not findings:**
- **Audit approval:** `plan.md:53,97` has the orchestrator validate the AUDIT, while `SKILL.md:302` and `test-writer-audit.md` name user approval. The HITL delegation (`execution.md:25-33`) and the 010-000 precedent (`approved_by: cdad-orchestrator`) cover this, though the mandate also excludes self-approving what is reserved to the user. Citing the mandate in the plan would remove the doubt. Whether it applies is the owner's call.
- **Trailer:** `plan.md:149-160` keeps the author's evidence without a non-normative label.
- **T1 task heading:** `## T1: alcance inmediato` does not match `_plan_task_ficha`, because the token is `T1:` rather than `T1`. The ficha comes back empty, with no real effect: it would only omit optional references, and the plan uses PCs, which that parser ignores anyway.
- **Test impact:** crude grep counts show 35 of 218 `tests/*.py` files mention `.cdad/execution.json` or `"execution.json"`. That supports T2's declared uncertainty but is not a list of affected tests.

## Abstentions

- **Exhaustive affected-test list:** assigned to the test-writer in T1. I did not build it.
- **Tests:** none were run, and the packet does not ask for it. References were checked by reading.
- **`planned` tasks:** I judged them by objective, dependencies, uncertainty, owner and resolution condition only, per the canonical rule.
- **Current decisions / `docs/adr/`:** the packet declares no `current_decisions`, and I did not review the ADR set.
- **Plan approval mechanics:** I did not establish whether `prepare` mechanically requires an approved plan before T1.
- **Author model family:** unknown.

## Evidence

- **Files modified:** none (`write_scope: []`). **Commit:** none.
- **Temporary files, all outside the repo and deleted:** `/tmp/e` and `~/.cache/cdad-render-006.{md,err}`.
- **Commands beyond intake:**
  - `read`, `grep`, `sed`, `ls` and `glob` over the plan, spec, owner records, packet sources, stage references, `handoff-prompts.md`, `SKILL.md`, `install.sh`, `Makefile`, `cdad_packet.py` and the cited tests.
  - Read-only `python3` snippets over `docs/.cdad-state.json`.
  - `python3 scripts/cdad-suite.py close --help`.
- **Delayed call:** the last shell call was first reported as rejected, then its result arrived. The result confirms the digest and the final tree.
- **Not run:** no tests, suite, generation, install or push.
- **Final state:**
  - `sha256sum` of `plan.md` → `9deee470f708a26d3e9418fcf0df5710693a510e7557d8e289494bcc349edd23`
  - `sha256sum` of `spec.md` (last taken before the delayed call) → `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`
  - `git rev-parse HEAD` → `2dffa9d095f55b6aa28269e9d85467e363d73113`
  - `git status --short` → `?? docs/specs/010-000-continuity-relative-root/discovery.md`, which was already there
  - `git diff --exit-code` → 0, `git diff --cached --exit-code` → 0 (both before the delayed call)

**Plan not approved. This review authorizes no implementation.**