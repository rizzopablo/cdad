# Independent review — recovery draft

**Verdict: two blocking defects.** The replacement spec and plan need clarification before approval. This review does not approve either document or authorize implementation.

Reviewed bytes:

- `recovery-plan.md`: SHA-256 `7d4fcec1604d1d8f5dd7421dd93def4cd7b82ae253c0bff49f786245e6f46cc8`
- `recovery-spec.md`: SHA-256 `b7195c04c27bcccad1249d7fd1c2d25b27845a82077dc6390068fbf87f21dc1f`

## Findings

### 1. PC-4’s “exactly one” delivery is not established by the planned table change

**Required — Verdict: BLOCKING · Bucket: m**

- **Evidence:** `recovery-spec.md:51–59` promises that architect/brainstorm accepts *exactly one* `role-report`, and directs a table change. `recovery-plan.md:11–12,100–123` confines GREEN to the smallest closed-table change. But the existing `cdad_result.py:273–323` accepts any nonempty list of uniquely named parts; reception uses that list at `:708–721`, and materialization checks allowed kinds per copied part at `:1064–1094`. `_allowed_kinds` at `:826–840` controls kinds, not the number of parts. Both adapters normally construct one part (`cdad_dispatch.py:1020–1044`; `cdad_delegate_opencode.py:2160–2181`), but that does not establish that another admitted result cannot contain multiple reports.
- **Consequence:** A table-only implementation and the currently specified positive tests could pass while the executable “exactly one” acceptance promise remains false. This is a mismatch between the contract and its verification, not a demonstrated need for a new permission system.
- **Closure:** Clarify whether PC-4 promises one **kind/normal adapter delivery** or enforces **one part at the result boundary**. If the latter remains, adjust the scoped implementation and independent tests to demonstrate rejection of multiple report parts; if the former is intended, amend the wording and acceptance criterion through the applicable draft procedure. See `stage-2-specification.md` §“Verification strategy per promise.”

### 2. Trivial corrections are permitted without reconciling the existing materialization route

**Required — Verdict: BLOCKING · Bucket: m**

- **Evidence:** `recovery-spec.md:39–41` permits trivial formal corrections “when materializing” while preserving original receipts and reports. `recovery-plan.md:20–24,180–229` assigns instruction changes but no corresponding change to the materialization mechanism. The existing route requires staging the exact original (`re-entry.md:36–53`) and copying the received parts to canonical targets (`:60–76`). `cdad_result.py:967–1002,1086–1094` copies the durable source bytes and treats a later divergent target as a conflict on replay.
- **Consequence:** An ordinary typo correction to a role deliverable has no clearly specified, compatible route: changing the original would compromise the receipt, while changing the canonical target after materialization can conflict with the materialization journal. A reviewer could find the wording consistent in isolation without establishing that the orchestrator can actually use the promised autonomy.
- **Closure:** Specify a proportionate actionable route that preserves the durable original and its attribution while distinguishing any corrected presentation from the journaled canonical materialization—or explicitly constrain where and when such correction is permitted. Demonstrate the route against the existing receipt/materialization and retry behavior during contextual review. This does **not** require changing frozen packet bytes or inventing a new permission system.

## Evidence and limits

- Route C intake: `validate-request` and `validate-packet` completed without output or error; `render --route C` matched the supplied identification; execution context schema is **2**.
- `git rev-parse HEAD` returned `c29ef97cea79ebd603491f62dae99bed0bcf05f9`. `git diff --quiet bc922c04 -- sources agents skills scripts tests install.sh build` returned **0**. This compares the named tracked product surfaces; it is not implementation evidence for the recovery.
- Examined the cited existing tests before the relevant implementation, the owner direction and retrospective, the retained 019-003 contract, and the current-decisions table against `docs/adr/`. No table row pointed to a missing ADR file. The unlisted ADRs 037–039 declare themselves proposed.
- **Commands executed:** the packet validation and render commands above; `sha256sum` for both drafts; `git status --short`, `git rev-parse HEAD`, and the baseline `git diff --quiet`; targeted `rg`, `nl`, `sed`, and a read-only Python comparison of ADR paths.
- **Product tests run:** none. This is a pre-production draft review, not evidence that PC-1–PC-7 have been delivered. Their closure categories are **unable to verify / not yet executed**.
- **Files modified and commits created by this reviewer:** none. The working tree already contained a modified state file and untracked recovery artifacts.

## Abstentions

- I did not independently execute a multi-part result or a corrected-target replay; the two findings identify the draft’s mismatch with the inspected executable paths and require verification in the eventual candidate.
- I did not establish the feasibility of the complete actual-use exercise in the installed runtime; no deployment or installation was authorized.