# Changelog

Changes to the CDAD project. The full development history remains in the
repository; this file summarizes deliveries, fixes, and publications.

New entries distinguish repository delivery, publication, and deployment: closing
a unit does not by itself establish that it was published, installed, or tested in real use.

## 2026-11-13 — Orchestrator startup (018-001)

- Entry through the compact `status` view, help for fixed formats, examples tied
  to the procedure, and guidance for capturing exit codes and bytes without altering them.
- [Progress](docs/progress.md) records the unit as closed, neither published nor deployed,
  with **6 surface tests** and an independent review with no blocking findings. No
  `closure.md` for the unit or epic appears in the inspected tree.
- **Limit:** the PC-9 real startup trial was not performed; neither a complete cycle
  nor a measured latency improvement is established. The documentation guides the agent;
  it does not guarantee what it reads. The [plan](docs/epics/epic-018-orchestrator-start/plan.md)
  retains the scope and criteria for the pending trial.

## 2026-11-08 — Epic 017: suite instrumentation and parallel execution

- Runner profiles and raw evidence, reproducible reconciliation, and a per-file
  parallel batch with a verdict that rejects incomplete or inconsistent evidence.
- The [closure](docs/epics/epic-017-suite-performance/closure.md) documents a serial/parallel
  comparison on the same revision, with exactly equivalent results by
  nodeid. The observed improvement applies to that trial, not to orchestrator latency
  or to every adoption environment.
- Shareable installation preparation was not demonstrated; that optimization was not applied.
  Unattributed time and canary limitations remain. The closure declares the delivery
  **neither published nor deployed**; it does not make the batch a generic CDAD capability.

## 2026-11-04 — Epic 016: traceability and the first suite-review segment

- A test→contract→promise registry, deterministic validation, and a gap report distinguishing
  unindexed obligations from obligations without a verifier. The registry does not replace
  the inventory or introduce a gate for projects that do not use it.
- First segment reviewed: **398 tests**, all assigned the Keep disposition. This is neither
  a full-suite review nor a reduction in tests. The remaining segments are
  outside the epic.
- The [closure](docs/epics/epic-016-traceability-and-suite-review/closure.md) links semantic
  review and an attributable gate; [progress](docs/progress.md) records subsequent publication
  and deployment, with a pre-existing symlink conflict: that installation check
  is not declared green. A later export fix included the legacy fixture
  missing from a public clone; its exclusion by `.gitignore` remains an outstanding issue.

## 2026-11-03 — Epic 015: consistent dispatch and reception

- `record-dispatch` and `receive` verify against the assignment's frozen sources,
  not live sources that may have changed while the role was working.
- Diagnostics with examples for fixed formats and guidance for `docs` and
  `contract` references; `open-unit` excludes queued units from closed epics and rejects
  ambiguous attribution.
- The [closure](docs/epics/epic-015-dispatch-reception/closure.md) records an attributable
  green full-suite run, limitations of fix reviews, and a transient flaky test under load.
  This evidence is not equivalent to publication or deployment.

## 2026-11-02 — Epics 013 and 014: test criteria and evidence policy

- **013:** selection by promise, contribution beyond existing protection,
  a single disposition, and replacement supported by sensitivity evidence; declared
  property budgets instead of per-postcondition quotas. A living inventory and
  maintenance procedure. The pilot retained the tests: **it did not confirm savings**.
- Its [closure](docs/epics/epic-013-test-criterion/closure.md) records focused checks
  and no full-suite run at that time; `013-004` was not opened. It is not presented as
  a delivered feature or as suite pruning.
- **014:** policy by timing: focused cycle checks, a full suite recommended at feature
  closure and required at epic closure unless the owner explicitly waives it. Approval
  of this policy authorizes the ordinary epic-closure run; it does not impose hosted CI
  on every project.
- The [014 closure](docs/epics/epic-014-suite-evidence-policy/closure.md) documents an attributable
  green gate and later additional evidence for 013, without rewriting its original
  closure. It preserves the limitations of literal oracles and fix reviews.

## 2026-11-01 — Independent fixes 011 and 012

- **011:** `begin` v2 rejects unpublished packets before writing, with a diagnostic
  directing the user to `prepare`; it does not itself repair already-blocked executions.
- **012:** the installer excludes Python bytecode and caches from ownership and comparison;
  the existing manifest is cleaned up on reinstallation.
- These are **independent features, not epics 011/012**. [Progress](docs/progress.md) records
  commits, focused gates, outstanding issues, and subsequent publication/deployment. The
  full suite was not run at their individual closures.

## 2026-10-31 — Epic 010: documentation specialization

- Contracts for discovery reports, processes, and user stories with verifiable evidence;
  integration into existing roles, without new agents or stages. Odoo specialization
  depends on the actual product or change, not the coordinator's environment.
- Dispatch ergonomics with explicit context and `render --route C` without retranscribing
  the body; corrected resolution of relative and absolute roots.
- The [closure](docs/epics/epic-010-documentary-specialization/closure.md) documents a pilot
  with independent defect detection, correction, and re-verification, plus a green
  closure suite. Pilot acceptance was under an HITL mandate, not direct owner approval.
  Publication and deployment remained separate acts; the closure preserves
  integration debt and installed-version drift.

## 2026-10-29 — Epic 009: updates and owner configuration

- Updates preserve the accepted `model:` overlay; other modifications are
  retained as conflicts. Preserving files is not equivalent to a clean check.
- OpenCode agents generated with native V2 frontmatter, including project-derived
  agents; real verification of model/variant recognition and V1→V2 upgrades.
  The product does not ship a model selection.
- The [closure](docs/epics/epic-009-installer-updates/closure.md) records an attributable gate
  and overlay limitations. Publication of 009-001 was explicit; the closure neither published
  009-002 nor installed into HOME.

## 2026-10-28 — Epic 008: suite coherence and sustainability

- HOME/XDG/temporary-directory isolation in tests, a capability-based selector, inventory,
  preserved closure evidence, and a shared core for lifecycle decisions.
- Assignment admission with a verified canonical packet and an attributable green
  development gate for this repository. Packets are transmitted byte for byte: a valid
  header or a terminated process establishes neither an assignment nor its acceptance.
- The [closure](docs/epics/epic-008-suite-coherence/closure.md) documents consecutive runs
  on the same revision and their limitations: they prove neither a universal absence of
  flakiness nor interception of every runtime action. The literal suite reduction was not
  achieved; it was replaced by the contractual-protection criterion. CI activation
  remained reserved to the owner, with no version-controlled workflow.

## 2026-10-26 — Epic 007 “Reliable cycle operation” (8/8, closed) and legacy genesis repair

**Published as a single summary commit.** Per-unit details live in
`docs/specs/<feature>/` and `docs/progress.md`; epic status lives in
`docs/epics/epic-007-reliable-cycle-operation/`.

### Delivered capabilities

- **007-001 — Unambiguous entry.** The compact view (`status`) states the situation, the next
  operation with its script, and a verifiable reference to the current approval.
- **007-002 — Dispatch recovery.** A recorded disposition resolves the attempt for
  `reconcile`; the successor is prepared without manual reconstruction or repeated effects.
- **007-003 — Continuity at boundaries.** `begin` / `verify-begin` before dispatch and
  `checkpoint-receipt` after reception; legacy history repaired through an explicit,
  approved `reanchor` with `legacy_anchor` (amendment 007-003 §2.3.1).
- **007-004 — Termination is not delivery.** The delegation envelope adds `delivery`
  (`none | staged | received`) with a fixed table; neither `rc` nor `termination` establishes
  reception or approval. Historical compatibility is validated and linked to the producer's verifier.
- **007-005 — Real serial reception.** A cross-project segment went through entry → packet →
  continuity → dispatch → delivery → reception → closure with the adopted version, without manual
  state edits. Delivered as verifiable evidence (a manifest with private resolution), not as a product
  change. Includes a declared and accepted budget deviation (two transports; the first
  rejected on identity, without a record or effects).
- **007-006 — Withdrawal and republication.** `register-transition --transition withdraw` withdraws
  a `prepared` packet that will not be dispatched, recording a reason and unblocking `prepare`;
  `republish-agents` republishes derived agents without preparing a packet, preserving the installed
  `model:`. Transactional publication with rollback.
- **007-008 — Receipt-closure action.** A new closure no longer inherits the pre-dispatch instruction
and writes a canonical action: reception is mechanical, neither dispatch nor reception is repeated,
and review does not presume approval. Historical closures are not migrated.
- **007-007 — Suspend and resume.** A unit is suspended at a safe boundary, another is worked on, and
  the first is explicitly resumed without losing identity or repeating effects. First real use
  during the epic itself.

### Operation

- Deployment of the adopted version `538ec57` into HOME, with a prior backup and the owner's
  `model:` settings preserved.
- Full suite: **1705 passed, 5 skipped, 0 failed**.
- Surface gates adopted as a practice: focused gates were hiding regressions in
  continuity consumers.

### Declared outstanding issues

- `REC-NEXT-ACTION-STALE`: the reception-closure body retains the previous `next_action`; the
  compact view and `reconcile` protect against repeating the effect.
- `SUITE-CONTAMINATION`: tests that pass in isolation and fail in larger runs because HOME/XDG
  are not isolated; a capability-based suite audit remains pending.
- `SUSP-GUARD`, `SUSP-LOCK`, `SUSP-APPROVAL`, `SUSP-IDENTITY`, and inherited issues (DT-8/F011, DT-9, CI).
- The epic **closes 8/8**. The happy path from rest was **observed within a declared scope**
  (007-008 entry and packetized dispatches; native RED/GREEN/review without a packet, a deviation
  declared in its closure). The failure path **was not observed in real use**: its mechanism is
  verified in a controlled environment. The closure suite had 1721 passed, 5 skipped, 1 failed
  that passed in isolation (`SUITE-CONTAMINATION`), and is not declared green.

### Editorial correction

- A local absolute path was replaced with `<repo>` in `docs/specs/007-004-termination-not-success/spec.md`
  §11 (draft evidence), without changing the contract's semantics.
