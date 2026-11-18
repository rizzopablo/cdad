# Independent review — PC-7 actual-use exercise

**Verdict: PC-7 is supported within its declared limits.** The recorded journey reached an unapproved draft and a separate independent review without treating the review as approval. I found no demonstrated blocker to the bounded PC-7 exercise. This is **not acceptance of the feature**, an approval of the sample spec, or evidence of universal agent compliance.

## Findings

### Optional — The project brief remained stale after decisions were resolved

**Verdict: OPTIONAL · Bucket: m**

In the resulting scratch documents, `artifacts/docs/projectbrief.md:5,11–13,29–32` still describes search, case handling, runtime and storage as undecided, and the architect consultation as pending. By contrast, the newer decision record and draft capture the owner’s resolutions (`artifacts/docs/activeContext.md:36–46`; `artifacts/docs/specs/001-notes-tags/spec.md:7–26`).

A later reader using the brief alone could misunderstand the current state. The draft and its reviewer did receive the current, recoverable decisions, so this did **not** invalidate the observed PC-7 journey. If the disposable project is continued, update the brief or clearly point readers to the newer decision record.

## PC-7 assessment

Paths below are relative to `.cdad/orchestration/epic-019/recovery-exercise/`.

| Required observation | Assessment and evidence |
|---|---|
| **Need and partial answer** | **Supported.** `inputs/01-need.txt` states the need and leaves search and case open. `inputs/02-partial.txt` confirms terminal use and free text only. `turn2.transcript.md` and `artifacts/docs/activeContext.md:114–130` retain the omitted decisions as open. |
| **Unaccepted default** | **Supported.** The owner’s rejection of lowercase conversion is not turned into a case-sensitive decision: `inputs/03-default-correction.txt`, `turn3.transcript.md` and `artifacts/docs/activeContext.md:80–97`. Case-sensitive comparison is adopted only after explicit confirmation in `inputs/04-resolve.txt`. |
| **Authorized correction governs** | **Supported.** The owner changes team use to personal use; the displaced framing remains recoverable and is marked superseded (`inputs/03-default-correction.txt`; `artifacts/docs/activeContext.md:76–78`). The consultation and draft use personal scope. |
| **Uncertainty prevents readiness** | **Supported.** After consultation, the orchestrator asks for tag identity and search choices rather than drafting (`turn3.transcript.md`; `activeContext.md:61–72`). The owner subsequently resolves them in `inputs/04-resolve.txt` and `inputs/04a-precisions-publication.txt`. Remaining control-character, identifier and operation questions are expressly marked as blockers for a complete executable contract in the draft (`spec.md:77–84`). |
| **Targeted consultation before draft** | **Supported.** The separate architect session returned an alphabet-risk report before drafting. The handoff, actual session and report are preserved in `artifacts/docs/handoffs/2026-11-15-architect-alphabets.md`, `session-transcripts/<session>.json` and `artifacts/docs/consultations/2026-11-15-architect-alphabets-report.md`. It was a **legacy consultation**, not a frozen brainstorm-packet delivery; it therefore does not itself establish PC-4’s adapter-delivery promise. |
| **Unapproved draft and independent review** | **Supported.** A separate architect session produced the draft; a separate reviewer session examined it. Both delivered artifacts have receipts, and I verified their stored parts match the materialized documents byte-for-byte. The draft is explicitly unapproved (`artifacts/docs/specs/001-notes-tags/spec.md:1–5`); the review identifies the undefined control-character set as blocking future approval, not delivery of the draft (`plan-review.md:8–22`). |
| **No invented approval or product/tests** | **Supported within observation limits.** The owner expressly authorized the plan as discovery/draft scope, not spec approval (`inputs/04a-precisions-publication.txt`; `artifacts/docs/epics/001-notes-tags/execution.md:8–16`). The scratch history records documentation changes, and the final scratch Git status was clean. Recorded transitions for draft and review have `approval_effect: false`. This cannot prove that no unobserved transient write occurred. |
| **Candidate and provenance** | **Supported for this local exercise.** The recorded candidate is `196c6f4a…`; product paths have no diff from that revision to observed repository HEAD. All seven preserved input hashes matched. All nine frozen packet instruction-source hashes matched the repository candidate. The eleven post-publication agent hashes matched their recorded values; the relevant orchestrator, architect and reviewer **bodies** matched candidate bodies despite changed publication frontmatter. The consultation’s skill-loader output identifies the local candidate directories. `sessions.json` records distinct architect and reviewer sessions and their reported models. |

## Failed attempts and material limits

- The first consultation load failed because a path was passed as a skill identifier; the retry loaded the local skills and produced the report. Both are visible in the architect session transcript and consultation handoff.
- The first draft dispatch lost the terminal newline: the received inline packet was **6083 bytes**, versus **6084** canonical bytes. It was rejected before drafting and abandoned. The replacement draft packet and reviewer packet matched their recorded inline bytes exactly. These failures are not counted as successful deliveries.
- In a current-state validation, the **reviewer** packet validated and both delivered receipts validated. Revalidating either historical architect packet against the scratch project’s *current* state returned `active_packet mismatch: id`; the current active packet is the later reviewer packet. That result does not independently re-establish the earlier packet validations at dispatch time. Their recorded session comparisons and receipts are the historical evidence.
- The draft reviewer’s blocker concerns the sample CLI’s future executable contract. It is **not** a blocker to demonstrating an honest, unapproved draft and review.
- The declared full suite remains pending separate closure. Installation drift is excluded and is **not green**. I did not rerun focused tests or the full suite in this assessment.

## Verification record

- Route C intake: `validate-request` and `validate-packet` completed without diagnostic; `render --route C` reproduced the received identification. The contract SHA-256 was `cd61455c3a5b799cdbfa0d29b5c08fbe8eddc1bd601f69869baa6eb00a1f0382`.
- `git diff --quiet 196c6f4a37c72e19e1ce096af3afb2a548587329 HEAD -- sources agents skills scripts tests install.sh build CDAD_metodologia.md` returned **0**.
- Independent Python hash and byte comparisons returned: **7/7 input hashes matched; 9/9 packet instruction-source hashes matched; 11/11 recorded post-publication agent hashes matched; all three delivered parts matched their materialized documents**.
- `git diff --check bc922c04 HEAD -- sources agents skills scripts tests install.sh build CDAD_metodologia.md` returned **0**.
- I compared the current-decisions table with `docs/adr/`: all 32 referenced files exist; the additional ADRs are marked proposed. I found no applicable contradiction in this assessment.
- **Files modified by this review:** none. **Commit created:** none. Repository HEAD observed: `97adce7081b54450e6a85e0d61df9cf7052e64c5`; pre-existing worktree changes were left untouched.

## Abstentions

- I do not accredit PC-4’s native/OpenCode delivery tests, PC-5’s resting-state regressions, the full feature, or epic closure from this exercise; those require their separately selected evidence.
- I cannot establish universal behavior, installed/deployed behavior, or absence of all transient writes from one bounded recorded session.