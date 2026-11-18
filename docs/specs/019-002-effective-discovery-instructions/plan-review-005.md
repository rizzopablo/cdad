# Plan review — 019-002 draft 006

**Reviewed object:** `docs/specs/019-002-effective-discovery-instructions/architect-draft-006.md`  
**SHA-256:** `9c29dcb5e9c2f61af101d0f59f570984b0c8b9243bedc6753a66ff6ed11d25cd`

**Dictamen:** one blocking finding. The prior T1 validation defect is corrected, but one mandatory T1 product path cannot be assigned under the current project policy. This review is neither approval nor authorization to implement.

## Required finding

### T1 requires a change that no implementer scope can currently carry

**Verdict: BLOCKING · Bucket: h**

**Evidence.** The specification requires removing contradictory lightweight-workflow guidance (`architect-draft-006.md:123–125`), and T1 explicitly assigns `CDAD_metodologia.md` as a product to modify (`:222–230`, `:294–295`). The accepted activation map identifies that file’s optional-review and partial-isolation wording as an incompatibility requiring reconciliation (`activation-map.md:80–85`).

The execution’s pinned path policy declares `README.md` as an exact documentation file, but not `CDAD_metodologia.md`; its documentation root is `docs/`. The actual classifier reports:

```text
CDAD_metodologia.md    unclassified
README.md              documentation
```

I also exercised the existing scope validator for an implementer:

```text
{'class': 'docs', 'path': 'CDAD_metodologia.md'}
=> PolicyError: scope selector is not classified as docs

{'class': 'implementation', 'path': 'CDAD_metodologia.md'}
=> PolicyError: scope selector is not classified as implementation
```

The validation rules are at `skills/cdad-cycle/scripts/cdad_packet.py:360–386,1419–1474`. Listing the path in `plan-tasks.files` does not declare it in the pinned path policy.

**Consequence.** The orchestrator cannot prepare a legitimate implementer write scope for this required correction under the present execution policy. Proceeding without resolving that boundary either leaves the contradictory lightweight guidance in place or requires an out-of-scope edit. The structural plan validator passing does not detect this assignment failure.

**Remedy and closure.** Return the policy/scope decision to the owner or orchestrator; do not bypass the policy or silently drop the consumer. Declare an authorized route that permits the required file to be edited while retaining the role boundaries and the accepted lightweight commitment. Closure is verifiable when the applicable execution policy classifies the file, the intended implementer scope passes the real validator, and the plan identifies the authorized route.

## Prior blocker and scope checks

The prior finding in `plan-review-004.md` is **closed with respect to the canonical block**. I parsed the actual draft 006 plan—not a reconstructed proposal—and ran `_plan_tasks_from_contract`, `_check_plan_tasks` and `_check_plan_validation_plan`:

```text
PASS actual draft: parser, task and validation checks
T1 files= 31 missing= ['tests/test_019_002_discovery_delivery.py']
T2 files= 4 missing= ['tests/test_019_002_resting_orientation.py']
T3 files= 0 missing= []
```

The two absent files are the explicitly planned new tests. T1 states that its file list is not a shared write scope and separates test-writer and implementer ownership (`architect-draft-006.md:369`). The finding above concerns the additional, independently verified **policy admissibility** of one declared product path.

I compared the revision with draft 005, the approved epic plan, accepted activation map and observed-acceptance protocol, and approved 019-003 specification. Verification sufficiency was assessed against `stage-2-specification.md`, §“Verification strategy per promise.”

## Prospective evidence categories

These categories describe the **future product**, not acceptance of this draft:

| Promise | Category | Limit |
|---|---|---|
| A — dialogue and handoff | Missing | Candidate instructions and observed application are not yet produced. |
| B — review route | Missing | Reviewed, exempted and invalid-exemption routes remain unobserved. |
| C — consultation and frozen packets | Missing | Candidate behavior and executable evidence remain to be produced. |
| D — closure and orientation | Missing | The regression and contextual guidance review remain to be performed. |
| E — coherent consumers | Missing | Candidate consumers and delivery evidence are absent; the path-policy blocker affects the planned correction. |
| F — observed use | Missing | J1–J7 and C1–C5 have not been observed. |

Missing future evidence alone is not an additional defect in an unimplemented draft; it cannot later be treated as acceptance by recording a limitation.

## Checks and evidence

- Route C identification matched the canonical route-C render. `validate-request` and `validate-packet` returned without diagnostics; full canonical render comparison returned `render_cmp=0`.
- The actual draft digest matched the packet contract.
- Compared the current-decisions table with `docs/adr/`: indexed files exist; the unindexed ADRs examined are proposed. No table-alignment finding is raised.
- Repository HEAD examined: `7d32db3028822fad8d9eaf8c57cd84bb270083c2`.
- **Files modified:** none. **Commit created:** none. `git status --short` showed the pre-existing modification to `docs/.cdad-state.json`.
- No full suite, candidate-agent exercise, generation, installation or deployment was run.

## Abstentions

- **Candidate runtime feasibility:** T3 does not yet establish how candidate agents and newly published packets will be consumed without unauthorized installation. I cannot determine whether the eventual route will satisfy PC-11; it remains an execution-blocking uncertainty and is not acceptance evidence.