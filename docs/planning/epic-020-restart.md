# Epic 020 restart — discovery intake

## Owner decision

The owner instructed the coordinator to discard the entire first attempt and restart the cycle. Commit `fd00a789` restores the tracked tree exactly to `c19a2080`, before epic 020 intake. The discarded attempt is retained on a local archive branch, not as an approved design or usable delivery.

All former epic 020 approvals and completion claims are superseded. The final PC-9 delivery is discarded as well. No execution or role assignment from that attempt is to be resumed.

## User intent retained for fresh discovery

- Keep methodology documents and the placement declaration versioned.
- Keep execution records local; a clone should still recognize the project.
- Preserve supported existing projects without automatic migration.
- Keep the change simple: introduce path indirection, not a storage framework.
- Publication, deployment and global installation remain outside this work.

## Design constraints from the owner's correction

Do not repeat content-based store selection, a multi-rule ambiguity mechanism,
fixture pin files or independent selection logic per consumer. Neither a pure
rename nor a compatibility rule is approved merely because it was discussed.
First establish where the path value is declared, how it is passed, and what
compatibility is actually necessary.

## Next discovery output

Present a short proposed approach before changing product or tests:

1. The single source of the operational path and its relative/absolute boundary.
2. The minimum compatibility rule, if needed, with its reason.
3. Exact consumer and fixture scope, including a grep-based verification.
4. A baseline test command and integrated regression selection, executed early
   enough to detect collateral changes rather than at the end.

Do not import the discarded specification, postconditions or task plan as new
requirements. Fresh specification and implementation remain pending.

## Discovery authorized

The owner said to proceed with the fresh discovery. This authorizes a bounded,
read-only architect consultation, not approval of a design or implementation.
The compact view reports rest; `open-unit` finds no eligible queued feature.
Do not reopen the unrelated queued unit of closed epic 013. With no new epic
plan approved, use the documented legacy architect-consultation handoff rather
than inventing execution authority or reusing discarded packets.

Consultation scope: the current operational path literals and their consumer
interfaces, the current layout declaration, and fixture construction relevant
to replacing those literals. Return one recommended small approach and the
necessary decisions, with source references. Do not draft a full specification
or run a full suite during this consultation. The new baseline is `95e09290`;
the installed methodology is a separate resource, not the product being changed.

## Owner's design and test budget

The owner requires the minimum-change design and a ceiling of **two new tests
in total**, not two files or two parametrized functions hiding more new cases.
Adapt existing tests to the agreed new behavior, preserving the promises that
remain valid. Do not add new tests for behavior already protected by those
adaptations. If the agreed scope cannot be verified within this budget, report
the concrete uncovered promise before proposing any exception; never increase
the budget silently.

The owner also declined the UI request to trust the nested project's OpenCode
configuration. Do not accept trust, suppress the prompt, or change permissions
to bypass that decision. If it prevents the consultation, stop that part and
report the specific runtime restriction.

## Owner correction — controlling discovery requirements

The owner rejected the recommendation in `epic-020-restart-discovery.md`.
Keeping `.cdad/` and merely tracking its locator does not meet the goal.
That report remains an attributed historical proposal, not the design mandate.

- Do not retain the `cdad/` plus `.cdad/` directory split.
- All state files that must be versioned belong in `cdad/`, not just the locator.
- Determine the smallest arrangement for local records consistent with those
  requirements. Do not presume that another top-level operational directory is
  authorized or recreate a content-based store selector.
- The owner rejects relocating sessions as a working strategy. Investigate how
  scripts resolve relative paths from their execution directory and their
  explicit project-root argument; do not make session relocation a product
  requirement. No further relocation is authorized by this discovery task.
- Minimum-change design and the two-new-tests-total ceiling remain binding.

Commission a corrected, read-only consultation before drafting the spec.
Distinguish the state required for a clone to recognize the project from
machine-local execution records. Any unresolved classification or unavoidable
compatibility choice must be stated explicitly, not silently selected.

## Migration alternative requested for analysis

The owner now proposes `cdad/` for versioned state and `.cdad-execution/`
for local records, replacing the former `.cdad/`. This supersedes the
single-directory candidate as the proposal to evaluate; it is not yet an
approved specification.

Proposed manual steps: move `.cdad/project-layout.json` into `cdad/`, rename
the remaining `.cdad/` to `.cdad-execution/`, and ignore `.cdad-execution/`.
Assess whether anything else is required, especially for open executions,
embedded paths/digests and existing methodology directories. Prefer a brief
entry-point diagnostic pointing to a migration Markdown guide over automatic
migration or permanent compatibility. Do not implement either yet.

The owner clarified that migration must also work for projects with open
development when the new CDAD version is installed. Requiring rest, finishing
or retiring active work, or retaining the previous runtime is not an acceptable
prerequisite. Analyze how to preserve continuation of active and suspended work
under mandatory manual migration, with concrete persisted-reference evidence.

## Final owner decisions for planning — supersede earlier candidates

The owner authorized planning on the following basis:

- Move `.cdad/project-layout.json` to `cdad/project-layout.json`.
  Do not broaden this into relocating all existing methodology documents,
  contracts, policies or Memory Banks.
- Declare the operational directory in that layout; the new default is
  `.cdad-execution/`. New publications use this declared directory.
- Manually rename the remaining `.cdad/` to `.cdad-execution/` and add the
  root operational directory to ignore rules. Identify any genuinely required
  additional live-state adjustment explicitly in the migration guide.
- Historical packages and evidence stay byte-identical. They are not to be
  made replayable under the new toolchain. No historical-path alias subsystem
  or hash-chain rewriting is commissioned.
- On detecting a methodology version change, the orchestrator reads the change
  notice/migration guide, performs the indicated migration, and generates a
  new package before the next role dispatch. This is an explicit orchestrator
  responsibility, not automatic package invalidation or automatic migration.
- Work may be open at upgrade time. Preserve its user-level progress; do not
  require feature/epic closure or a return to the previous installed version.
  Planning must distinguish continuing the work with a fresh assignment from
  replaying an old package.
- Whoever upgrades while agents are running is responsible for notifying and
  coordinating with them. Do not add a concurrent-worker upgrade mechanism.
- Reuse the existing version check and lifecycle operations where they fit.
  Verify what they actually detect: same-version source edits are not assumed
  detectable. Identify any narrow missing transition instead of inventing a
  compatibility framework or silently bypassing a gate.
- Minimum implementation change; at most two added test cases in total.
  Adapt existing tests as a coherent set and measure baseline/regression early.
- No session relocation, trust approval/bypass, global installation, deployment
  or publication is authorized by this planning instruction.

The earlier migration reports are retained as attributed analysis, not adopted
designs. Their clean-boundary condition, full documentation move and historical
alias proposals are not requirements. Next output: a short architect draft
specification and implementation plan for owner consideration, not approval.

## Draft review commission

The owner said to proceed after presentation of
`epic-020-minimal-migration-draft.md`. Advance to independent draft review,
not implementation. Review the proposed live-state handoff against actual
preparation, suspension and result-recovery behavior before admitting it as
sufficient. Do not treat the owner's acknowledgement as evidence that those
mechanics work. Draft family round 1/2; no extra correction round authorized.
Keep the approved scope, two-new-tests ceiling and historical evidence intact.

## Draft review disposition — first correction

Materialized `epic-020-minimal-migration-draft-review-001.md` unchanged.
Accept its three concrete findings for a narrow draft correction:

1. Migration itself may occur with active and suspended work. Selecting a
   suspended unit later must not overwrite another active unit. Specify the
   exact saved progress fields, preserve other registry entries, and verify
   current governing approvals/policy before authorizing renewed work. Do not
   turn the unit-selection condition into a project-at-rest migration gate.
2. Operator coordination remains the owner's responsibility. The guide must
   require establishing outstanding effects before authorizing overlapping
   work; unknown effects require investigation, not implicit completion or a
   generic objective telling the next worker to repeat them. No new automatic
   concurrency or migration subsystem is commissioned.
3. Ignore the actual declared operational directory. The default root ignore
   entry is an example, not a restriction to that default.

Draft family: round 1/2 reviewed; correction commissioned for closing check
at round 2/2. No increase in test budget, product scope or correction ceiling.
The architect returns the corrected draft as final text; it does not edit the
product, tests or original review. After correction, independently check these
findings and adjudicate remaining issues without an automatic extra loop.

Materialized the architect's correction unchanged as
`epic-020-minimal-migration-draft-002.md`; prior draft and review remain intact.
Draft family round 2/2: commission the closing check of the three findings
against the corrected text. No implementation or test changes authorized.
Any remaining blocker requires explicit adjudication/replanning, not automatic
extension or dismissal based on the exhausted allowance.

## Planning close — owner approval pending

The independent closing review is materialized unchanged in
`epic-020-minimal-migration-draft-review-002.md`. All three findings are
resolved; no remaining blocker or direct correction regression was identified
within that check. Draft family closes at 2/2 without another correction.

The candidate for owner approval is
`epic-020-minimal-migration-draft-002.md`, including the explicit manual
live-state handoff exception. Review readiness is not approval. No executable
evidence is claimed: baseline, test audit/adaptations, implementation and
integrated verification remain pending. No product or test changes are
authorized by receiving this report.

## Clarification accepted by the owner — new-project default

The example with `"methodology_dir": "docs"` in the architect's draft
illustrates an existing legacy project only. The already-existing default for
new projects is `cdad/` (`cdad_layout.py`, `BOOTSTRAP_DIR`); it is not changed
by this plan. The owner confirmed this clarification.

For a new project the intended declaration is:

```json
{
  "schema_version": 2,
  "methodology_dir": "cdad",
  "operational_dir": ".cdad-execution"
}
```

Existing projects retain their actual methodology directory. This attributed
clarification does not alter the original role outputs or record overall plan
approval: the owner's acknowledgement concerned the default-directory question.
