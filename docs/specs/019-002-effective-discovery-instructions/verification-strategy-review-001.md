# Review of the verification-strategy draft

**Object reviewed:** `docs/specs/019-002-effective-discovery-instructions/verification-strategy-draft.md`  
**SHA-256:** `dbe2b89bd7153e8f9ccf56a5403fae8647cf1152fb0e360224d4315f43bc4c60`

## Blocking findings

### 1. Deterministic delivery promises are assigned to semantic review alone

**Verdict: BLOCKING · Bucket: h · Severity: Required**

PC-1 requires specification instructions to identify verification methods, responsible verifiers, evidence and limits, while PC-2 requires methods to follow the property being verified. Yet both are assigned only an independent semantic review (`verification-strategy-draft.md:101–114`). PC-3 and PC-4 similarly include effective packet and legacy consumers, but assign semantic review while relegating mechanical controls to existing evidence (`:124–138`).

The draft itself recognizes that **distribution of instruction bytes** is a distinct deterministic property (`:116–120`) and requires distribution controls for PC-9 (`:186–190`). As written, however, PCs 1–4 can be accredited by reading selected instructions without establishing that the applicable rendered or distributed consumers contain those instructions. An agent could therefore receive stale or incomplete requirements while the relevant PC is reported satisfied.

**Remedy and closure:** distinguish semantic sufficiency from delivery for every PC that promises effective consumers. Identify the applicable deterministic distribution evidence alongside semantic review, or explicitly narrow those PCs and map their delivery obligation to PC-9. The evidence mapping must let a reviewer trace each promised effective surface to both the relevant semantic examination and, where applicable, its delivery check.

### 2. The comprehension-reading procedure requires criteria before the reviewer can necessarily be assigned

**Verdict: BLOCKING · Bucket: m · Severity: Required**

PC-5 says the reviewer prepares the reading task and evaluation criteria **before production** (`:142–148`), while PC-4 requires detailed instruments and acceptance inputs to be fixed before relevant production (`:136`). The draft does not specify an operational handoff for a reviewer’s pre-production work distinct from the later independent review, nor how that task is protected and recovered for the final evaluation.

This matters because the existing workflow assigns the reviewer to review artifacts after production; merely stating a pre-production responsibility does not establish who dispatches that earlier assignment, what it produces, or how the orchestrator preserves it. Without that handoff, a selected comprehension exercise can be prepared retrospectively against the produced text, or the later reviewer can lack the protected criteria needed to evaluate it.

**Remedy and closure:** specify the existing-role handoff: orchestrator dispatches the independent reviewer before relevant production, preserves the versioned task and criteria outside producer control, and provides them with the reader’s actual response to the evaluating reviewer. State how to proceed if the exercise was not selected or the criteria were not fixed in time. No new role or gate is necessary.

## Non-blocking findings

### 3. The proposed sequencing remains contingent on actual pinned inputs

**Verdict: OPTIONAL · Bucket: h · Severity: Optional/Consider**

The draft correctly instructs operators to stop if suspension or resumption rejects (`:254–280`), but “reconcile the changed 019-002 unit projection and any affected continuity evidence” (`:260`) does not identify which currently pinned inputs would be affected by the epic-plan amendment. The suspension implementation checks the active packet contract and vigente continuity references; resumption checks saved digests (`skills/cdad-cycle/scripts/cdad_packet.py:791–905, 1075–1100`).

This is not evidence that the proposed sequence will fail: the actual pins after this consultation’s re-entry are not yet known. Before materializing the amendment, inventory those exact references and establish a supported reconciliation path for any affected pin. Keep the stop-on-rejection instruction.

## Dictamen

The draft is **not ready for acceptance as written**: its self-application does not consistently connect promised effective instructions to distribution evidence, and its optional comprehension exercise lacks an executable pre-production handoff. The owner decides the findings and any changes; this review is not approval or authorization to implement.

The proposed `suspend-unit` → `open-unit` → `resume-unit` route exists in the CLI, and the reviewed tests cover suspension, opening another unit and resumption. I did not execute those transitions against the live project.

## Abstentions

- **Final sequencing safety:** I cannot establish the pins and continuity state that will exist after this consultation is received and reconciled. The draft’s stop-and-reconcile condition remains necessary.
- **Complete consumer coverage:** I did not independently inventory every generated agent, packet and installed distribution surface. The review therefore does not certify that the draft’s allocation captures all affected consumers.
- **Execution evidence:** No tests or full suite were run; this was a read-only draft review. Test and CLI source were inspected, not treated as evidence of a successful live transition.

## Review evidence

- Route C `validate-packet` completed successfully with no diagnostic output, using the named request, packet and execution context.
- `sha256sum` returned the draft digest stated above.
- Examined repository HEAD: `0ad05c9ceb0afac95c9653caa0e96b1ad20f04be`.
- Inspected the draft, relevant suspension/resumption tests and CLI implementation, epic plan, documentary-contract reference, ADR-040 and its current-decisions entry.
- **Modified files:** none by this review. `git status --short` showed a pre-existing modification to `docs/.cdad-state.json`.
- **Commit created:** none.