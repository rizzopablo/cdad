# Plan review — 019-002 draft 005

**Reviewed object:** `docs/specs/019-002-effective-discovery-instructions/architect-draft-005.md`  
**SHA-256:** `cd6be450bcc4b4639156e47156a702d5d66c2817cd8c6a5083b65bdfbe007133`

**Dictamen:** one blocking finding. This is a review of the unapproved draft, not approval or authorization to implement.

## Required finding

### T1’s canonical task declaration cannot pass plan validation

**Verdict: BLOCKING · Bucket: h**

**Evidence.** The draft’s T1 task lists implementation files and a focal test in prose (`architect-draft-005.md:216–236`), but its canonical `plan-tasks` entry declares `"files": []` and provides `focal_tests`, not `observable_checks` (`:267–292`). The note at `:335` says the prose supplies the paths; it does not change how the canonical block is validated.

The existing validator classifies an unmarked task with an empty `files` list as code-less and requires `observable_checks` (`skills/cdad-cycle/scripts/cdad_packet.py:5628–5641`). I ran the draft through the plan checks; the result was:

```text
PolicyError: plan task 'T1' is missing its per-task validation plan:
a non-empty focal_tests (code task) or observable_checks
(code-less task) is required (PD-8)
```

**Consequence.** If this plan is submitted as a plan-form draft, packet preparation rejects it before publication. More importantly, T1’s machine-readable declaration contradicts the work it assigns, so its per-task validation and file-based checks cannot operate on the actual task. This review’s packet identifies the combined draft as a **spec-form** object; that explains why intake succeeded but does not make the embedded plan valid.

**Remedy and closure.** Put T1’s actual, exact task paths in its canonical `files` list, consistent with the task text and separately scoped test-writer and implementer assignments. Validate the resulting plan-form draft with the existing plan validator. Closure is observable when the validator accepts the corrected block and its declared paths match the intended task without broadening either role’s write scope.

## Verification assessment

The draft’s per-promise methods were assessed against `stage-2-specification.md`, §“Verification strategy per promise.” The following are **prospective evidence categories**, not claims that implementation acceptance has occurred:

| Promise | Category | Limit at this review |
|---|---|---|
| A — dialogue and handoff | **Missing** | Candidate instructions and observed application do not yet exist. |
| B — independent review route | **Missing** | Reviewed, exempted and invalid-exemption route observations remain to be performed. |
| C — consultation and frozen packets | **Missing** | Candidate executable behavior and focused results remain to be produced. |
| D — closure and orientation | **Missing** | The closure → status → opening regression and guidance review remain to be performed. |
| E — coherent consumers | **Missing** | Generated candidate consumers and delivery evidence remain to be examined. |
| F — observed use | **Missing** | J1–J7 and C1–C5 have not been observed. T3 correctly identifies candidate-runtime loading without unauthorized installation as an execution-blocking uncertainty; no viable runtime path has yet been demonstrated. |

Missing future execution evidence is not, by itself, an additional defect in this *draft*. It cannot later be converted into acceptance merely by recording the limitation.

## Checks and evidence

- Route C identification matched the canonical render; `validate-request` and `validate-packet` completed without diagnostics.
- Compared the draft with the approved epic plan, accepted 019-001 design and acceptance protocol, and approved 019-003 specification. Examined the relevant existing tests and implementation interfaces, including the supervised review gate and frozen-packet behavior.
- Compared the current-decisions index with `docs/adr/`: indexed paths exist; the unindexed ADRs include explicitly proposed decisions. No decision-table finding is raised for this draft.
- Reproduced the T1 validation failure using `_plan_tasks_from_contract`, `_check_plan_tasks` and `_check_plan_validation_plan` on the draft bytes.
- Repository HEAD examined: `9b69ca4c0498e868449f498c877e91d30695b6dc`. The relevant baseline surfaces checked against the draft’s stated revision had no intervening diff.
- No full suite, candidate-agent exercise, generation, installation or deployment was run. No product files were edited and no commit was created. `git status --short` reported the pre-existing modification to `docs/.cdad-state.json`.

## Abstentions

- **Candidate runtime feasibility:** T3 does not yet select or demonstrate a way to execute the changed effective instructions without installation or deployment. I cannot determine from this draft alone whether the eventual selected path will satisfy PC-11; it must be resolved and evidenced before that execution.