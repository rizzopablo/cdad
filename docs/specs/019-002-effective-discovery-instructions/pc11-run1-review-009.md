## Review: PC-11 observed run1 (019-002), route C

**Verdict: run1 does not support accreditation.** C1–C5 are all not met. J3, J4 and J5 failed. PC-1, PC-2 and PC-3 are not met. PC-4 is only partly observed. Every item below is BLOCKING under PC-11, which says an unobserved, failed or unrecoverable required case blocks accreditation. Nothing here approves anything, and I made no repository edits.

### 0. Intake (route C)

- The identification block in the prompt matches `cdad_packet.py render --route C` exactly.
- `validate-request` and `validate-packet` both returned rc=0.
- A full `render` is byte-identical to `PACKET.md` (`cmp` reported IDENTICAL).
- The contract digest matches `spec.md`. The six protected inputs all verify against `MANIFEST.sha256`.

### 1. Per-case record, C1–C5

Input digests are verified by `sha256sum -c` (prefixes shown). Turn numbers are `run1/transcript-turnN.txt`. Artifacts are `run1/artifacts-docs/`.

| Case | Protected input | Actual response (turn) | Resulting treatment (artifact) | Observed | Locators |
|---|---|---|---|---|---|
| **C1** partial answer | T2 `d2d111cb` | T2: orchestrator says the owner "deferred the rest, so I'll proceed on the recommended defaults" (line 3). | Owner's answer kept (discovery.md L37–40). But the draft commits undecided items as normative: plain-list tags (promise D, first draft at `11ffbe7`); case folding PC-9 (spec L73); refusal rules PC-10 (L74). | **Not met** | spec L71–74; `11ffbe7` |
| **C2** unaccepted default | T2 `d2d111cb` | T2: defaults handed to the architect with "write them into the spec as stated assumptions" (architect Task prompt, line 11). | Recorded as pending in activeContext and in A2/A3/A6/A8/A9 (L112–118). Yet PC-9/PC-10 make A2/A8 binding postconditions. The default is distinguishable in the notes, not in the product. | **Not met** (product); record-level distinction met | spec L73–74, L112, L118; activeContext |
| **C3** corrected decision | T4 `bcc6456a` | T4: "Correction to what I said before … ANY". Orchestrator treats it as a confirmed decision and sends the architect a revision. | Outcome correct: PC-6, acceptance criterion 2, A10 say ANY (`d164079`). Provenance missing: no Dialogue-context entry for T4, no supersedes link, no supersession index. The owner's "what I said before" matches no recorded entry (the single-tag default was the orchestrator's, not the owner's). | **Not met** (provenance); outcome met | discovery.md L37–40; spec PC-6, A10; `d164079` |
| **C4** unresolved consequential choice | T5 `fbfa65d9`, T6 `14c9577a` | T5: plain-list display moved to an "Open decision" section, PC-7 reserved, approval blocked (`b680355`). T6: owner's go-ahead was conditional ("if everything else is settled"); orchestrator drafted anyway with recommended defaults for A2/A3/A6/A8/A9/A12 (turn 6, line 2). | Plain-list choice held visibly after T5 (met for that choice). Other consequential choices drafted as binding text and reported as "ready for owner decision" (`ec397d3`). | **Not met** overall; met for plain-list after T5 | turn5 L2, L9; turn6 L2, L22; spec L104, L121–122 |
| **C5** technical uncertainty | T3 `ac255345` | T3: orchestrator ran the CLI and read `storage.py` and `cli.py` itself; asserted "Neither assumption holds" (turn3 L3–5). No architect consultation. | "Numbering shifts" was already pinned by PC-13 before T3 (added in review round 1, turn 2), so it is not a result of T3. "Existing file is rewritten on first change" appears in activeContext (turn 6) and the chat, but in no spec or discovery section. | **Not met** (routing); evidence not carried into the spec | turn3; spec PC-13; activeContext |

### 2. Journey J1–J7 (J8 not simulated, per protocol)

| Step | Result | Basis |
|---|---|---|
| J1 need | Observed | turn1 (owner wording only paraphrased; see limits) |
| J2 functional dialogue | Observed | turn1 `question` call (three questions in one call; no answer returned); answer recorded as "Owner (2026-11-15)" without a message id (see F2) |
| J3 targeted consultation | **Failed** | Only architect dispatch before drafting asked for "Discovery and spec draft" in one call (turn2 line 11), not a consultation on a consequential uncertainty. The T3 uncertainty went to the orchestrator (F6, F7). |
| J4 recorded decisions | **Failed** | discovery.md Dialogue context has 2 entries. T3–T6 appear only in activeContext. No classes, supersession links or message ids (F2). |
| J5 readiness R1–R5 | **Failed** | No readiness record in transcripts or in `.cdad-state.json` `stage_history` (bootstrap, discovery, specification only). Drafting started at T2 and again at T6 under unmet conditions (F3). |
| J6 draft as final text | Observed | architect returned the spec unapproved (status Pending approval); but produced before readiness (order defect under F3) |
| J7 independent draft review | Observed, with defects | Reviewer ran in its own session (`<session>…`, distinct from orchestrator `<session>…` and architect `<session>…`). Blockers went to the architect and each design change got a focused re-review. Nothing was approved. Defects in F8. |

### 3. PC-1 to PC-4

- **PC-1 (responsibilities): not met.** Orchestrator read code (turn1 L2–3), ran commands on scratch data and asserted technical facts (turn3), and wrote technical bootstrap content (`systemPatterns.md`, `projectbrief.md`) from its own reading. Architect returned its draft as final text (met). See F1.
- **PC-2 (recoverable context): not met.** discovery.md was created after the spec draft (write order: spec at turn2 L13, discovery at L28). Entries are incomplete. The reviewer's round-1 prompt got a summary, not the attributed context. See F2, F8.
- **PC-3 (readiness R1–R5): not met.** R1 fails: deferred and conditional items were not treated as unanswered. R2 fails: defaults were used as consent. R3 partly fails: correction has no authority or supersession record. R4 fails: technical uncertainty was not sent to the architect. R5 fails: T3–T6 are not recoverable from the Dialogue context. See F3, F5, F6.
- **PC-4 (reviewed route): reviewed route met; exempted route and bypass attempts not observed.** The spec requires three observed routes (reviewed, exempted with four fields, bypass attempts with and without fields). Only the first occurred (F9).

### 4. Findings

Bucket follows `verdict-tuple.md`: +1 for a different model family from the run's orchestrator (gpt-6.1-terra), +1 for a grounded file or turn citation, +1 for spec and candidate sources in context, +1 for complete record in context. All findings score 3–4, so all are h. None rests on elicited confidence.

**F1 — Orchestrator did technical investigation (PC-1, C5).** BLOCKING · h
- Evidence: turn1 (reads `notes/*`, states "a note's id is its position"); turn3 (runs the CLI and reads `storage.py`, `cli.py`); bootstrap writes.
- Candidate defect: `sources/roles/orchestrator.md`, operating rules (about L132–145), forbids answering technical questions but does not forbid reading source or running the product to settle an owner's claim, or to write technical facts into the Memory Bank.
- Minimal remedy: add one sentence: "Claims about existing code or behaviour, including the owner's, are technical uncertainties: send them to a targeted architect consultation; do not read sources or run the product to settle them." Technical sections of bootstrap documents come from the architect's report.

**F2 — Dialogue context late, incomplete and unattributable (PC-2, J4, R5).** BLOCKING · h
- Evidence: write order (turn2 L13 before L28); discovery.md L37–40 holds two entries; owner entries have date but no message identifier, class, fragment, supersession or next action.
- Candidate defect: `stage-1-discovery.md:63` says the file is created "if owner answers were already recorded", and `stage-2-specification.md` §2.1 says "create it if needed". Neither makes creation a gate before the first architect dispatch or the draft.
- Minimal remedy: make it a gate: discovery.md with a Dialogue context section must exist before any architect dispatch or spec draft. Each owner message gets an entry carrying its message identifier. R5 checks completeness.

**F3 — No readiness check; drafting proceeded (PC-3, J5, C4).** BLOCKING · h
- Evidence: turn2 L3 and turn6 L2 (see table above); turn6 final text admits "the defaults below are not settled"; no readiness record anywhere. Stage-1 exit gate ("no assumptions of the form 'I think X exists' remain pending") not checked: the architect's discovery kept [assumption] items.
- Candidate defect: `references/re-entry.md` R1 (about L236–243) requires "an explicit owner answer or an explicit owner exclusion" but does not say that "deferred / leave it for later / leave it open" is an unresolved item, nor that a conditional go-ahead counts only when R1–R5 pass at that moment. The run read "deferred" as licence to use defaults.
- Minimal remedy: add to R1: "A deferral is an unresolved item, not an exclusion. A conditional go-ahead counts only after R1–R5 pass, recorded at that moment."

**F4 — Unaccepted defaults committed as normative text (C1, C2).** BLOCKING · h
- Evidence: the T2 draft already promised plain-list tags (journey text, turn2 L13) before any owner answer; owner later reserved it (T5). PC-9 (spec L73) and PC-10 (L74) make folding and refusal binding while A2 and A8 (L112, L118) say "pending owner". Same default, normative in the Contract and pending in the assumptions.
- Candidate defect: the spec-writing packet (`references/handoff-prompts.md`, draft section, about L262–290) and the spec-draft checks (`re-entry.md` "Architect — spec draft", about L250–258) do not forbid normative postconditions or acceptance criteria that rest on unresolved items, proposals or unaccepted defaults. The reviewer's criteria in the run did not check decision traceability either.
- Minimal remedy: add to the spec-draft check: "Every numbered postcondition and acceptance criterion traces to a current decision. Unresolved items, proposals and unaccepted defaults appear only as labelled open assumptions, never in the Contract or acceptance criteria." Add the same check to the plan-review packet.

**F5 — Correction provenance not recoverable (C3, R3).** BLOCKING · h
- Evidence: T4 correction is recorded only in activeContext and in the commit message (`d164079`); no Dialogue-context entry, no supersedes link; the replaced statement was never an owner entry.
- Candidate defect: `stage-2-specification.md` "Dialogue record convention" gives supersession links when a prior entry exists, and says an unauthorized correction supersedes nothing. It gives no rule for a correction that names a prior statement with no matching entry.
- Minimal remedy: add: "A correction that names an earlier statement with no matching entry is recorded as conflicting statements. The orchestrator asks the owner which statement it replaces and never supersedes by inference."

**F6 — Technical uncertainty not routed; recovered evidence not carried (C5, R4).** BLOCKING · h
- Evidence: turn3 (orchestrator checks both assumptions itself). The "file rewritten on first change" result is absent from spec.md and discovery.md (grep for rewrite and byte-level change: no match).
- Candidate defect: `re-entry.md` R4 (about L240) requires technical uncertainty to be investigated, bounded or blocking via the architect, but does not say that an owner's assumption about existing behaviour is such an uncertainty, nor that a verified contradiction must reach the discovery or the spec as a limitation or blocker.
- Minimal remedy: add to R4: "An owner's assumption about existing behaviour is technical uncertainty and goes to the architect. A verified contradiction is recorded as technical evidence ('contradicted') in the Dialogue context and reflected in the draft or as an explicit limitation or blocker."

**F7 — No targeted architect consultation (J3).** BLOCKING · h
- Evidence: only one architect dispatch before drafting (turn2 L11), combining discovery and draft. Later dispatches (turns 4–6) were revisions, not consultations.
- Candidate defect: the consultation packet (`handoff-prompts.md`, about L240–255) is adequate, but the run never loaded it (F10). No rule orders the steps: a spec-writing dispatch must not follow a dispatch that was not a consultation or an R4 "no consultation" record.
- Minimal remedy: state the order in `stage-2-specification.md` §2.1: "A spec-writing dispatch requires a recorded readiness result, and that result requires either the consultation route or a recorded 'no consultation' R4."

**F8 — Review evidence materialized in summary form; reviewer context summarized (J7, PC-2, PC-4).** BLOCKING · h
- Evidence: `plan-review.md` rounds 1–2 are "History of rounds" written by the orchestrator. Rounds 4–7 were appended by shell heredocs as "(reviewer FINAL TEXT, summarized)" (turn5 L9, turn6 L19). Round-1 reviewer prompt (turn2 L16) gives a summary of decisions and file pointers, not the Dialogue context.
- Candidate defect: `sources/roles/orchestrator.md`, "Materialization and git" (about L170–178), says "from their FINAL TEXT output" but does not say verbatim or forbid summaries inside verdict sections. `stage-2-specification.md` L63–67 gives the complete-Dialogue-context rule for the packet route (`--input`) and the legacy route (paste into the dispatch prompt). The native dispatch the run used maps to neither.
- Minimal remedy: require verbatim FINAL TEXT; any orchestrator summary goes in a separate, labelled note outside the verdict. For native dispatch, paste the complete Dialogue context into the prompt.

**F9 — PC-4 exempted and bypass routes not observed.** BLOCKING · h
- Evidence: only the reviewed route occurred. No approval was requested, which is correct, but the exemption and bypass cases the spec requires were not run.
- Candidate defect: none found; the routing text in `re-entry.md` matches the spec.
- Minimal remedy: run two more executions: an exempted route with all four fields (`exempted_by`, `delegated`, `requested_by`, `reason`), and bypass attempts with no exemption and with each field omitted. Record them as new executions.

**F10 — Packet route and stage references not exercised (PC-9, protocol §5).** BLOCKING · h
- Evidence: the orchestrator loaded only `SKILL.md` and bootstrap references (turn1 L4; bootstrap lines 80–140 in turn 2). It never loaded stage-1, stage-2, re-entry, handoff-prompts or the orchestrator source. It never ran `cdad_packet.py prepare`. It wrote `.cdad-state.json` by hand. Subagents got ad-hoc Task prompts (RUN-RECORD). No frozen packets, so no packet identities or digests to record.
- Candidate defect: `project-start.md` (about L98–106) sends the first commission through `cdad_packet.py prepare --role architect --substage discovery`. The run's scratch project lacked policy and state, so the orchestrator stayed in diagnosis and never reached a stage that would load its file. Because those files were never loaded, F1–F9 cannot be attributed to their wording alone.
- Minimal remedy: rerun the feature with the documented project-start route (policy, state, `prepare`), require the stage reference to be loaded at each stage entry, and record packet identities and frozen digests (protocol §5).

**F11 — Owner questions batched (not a protocol item).** OPTIONAL · h
- Evidence: turn1 has one `question` call with three questions, and text listing five decisions. The rule "one decision at a time" appears only for the architect's questions (`handoff-prompts.md:253`), not for the orchestrator's own (`stage-2` §2.1).
- Minimal remedy: add to `stage-2` §2.1: "Ask the owner one decision at a time, each with the reference that justifies it." (Mirrors handoff-fidelity §4.)

### 5. Limits

- **Owner messages are not in the transcripts.** The transcripts contain only the orchestrator's text, tool calls and subagent output. Binding protected inputs to turns rests on the orchestrator's paraphrase, with the digests as the only fixed record.
- **Chain of custody of the inputs is not shown.** The digests verify now. But the six input files and the transcripts all carry the same mtime, 2026-11-15 17:40:43 (−03), which is when the record was assembled. The run's turn-2 clock was 17:17 (−03). The files are `rw-r--r--`. So "written and write-protected before the run" is unverified. I found no sign of alteration.
- **Subagent output is clipped in the transcripts.** Architect and reviewer replies are cut at about 3,300 characters per tool line, mid-word, with no marker. Orchestrator writes and commands are complete. Where a finding depends on a subagent's full text, I say so (see abstentions).
- **Model.** The run's orchestrator used `openai/gpt-6.1-terra`, not the configured `opencode-go/deepseek-v4.1-flash#max` (quota deviation, RUN-RECORD). These observations apply to the model used. Subagent model inheritance was not verified.
- **Coverage.** The candidate packet route, stage loads and frozen publications were not exercised (F10). The run is therefore evidence about a different route, not the activated one.
- **Question tool.** No output was recorded in headless mode, so answer capture for J2 rests on turn 2 text.
- **Revisions.** The run used candidate `732a7275`. The spec was examined at `bc922c04`. The current repository HEAD is `95d31c7`.

### 6. Abstentions

- Whether each materialized `spec.md`, `plan-review.md` or `discovery.md` write matches the architect's or reviewer's full final text byte-for-byte. The full text is clipped in the record.
- The effective-agent hashes (`effective-agents.sha256`). The generated agent files sit in the scratch project, outside repository-read. I did not read them.
- The effective-skills hashes. I spot-checked two of 100 against `732a7275`: `stage-1-discovery.md` and `re-entry.md` both MATCH. I did not check the rest.
- Whether subagents ran on the configured model.
- Whether the owner messages match the protected inputs verbatim. No owner message is in the transcripts.
- Whether the operating-design files cited by the protocol and spec (`roles-and-dialogue.md`, `readiness-and-approval.md`) exist in the design directory. The candidate revision has no such files and uses `re-entry.md` instead. I did not check the design directory.

### 7. Evidence

- **Repository HEAD at review time:** `95d31c74e5527d235c5aedfac9d165d1aaf083ff`. Candidate revision in the run: `732a7275d45130498e047f79a2e3c9b9460262f7`.
- **Commands and key output:**
  - `cdad_packet.py validate-request --execution-context …/execution.json --request …/REQUEST.json` → rc=0
  - `cdad_packet.py validate-packet … --packet …/PACKET.md` → rc=0
  - `cdad_packet.py render … > /tmp/rev009-render.md; cmp /tmp/rev009-render.md PACKET.md` → IDENTICAL
  - `cdad_packet.py render --route C …` → identification block identical to the prompt
  - `sha256sum spec.md` → `dc0800fadd18d607e4563612fa17bf23fca077efa1d24a1b682aef9e8b728594`
  - `sha256sum -c MANIFEST.sha256` (in `pc11/inputs`) → six lines OK
  - `git show 732a7275:skills/cdad-cycle/references/{stage-1-discovery,re-entry}.md | sha256sum` → both MATCH the manifest
  - `git grep -n … 732a7275 -- sources skills` → citations above
  - `stat` / `ls -ld` on the scratch directory → metadata only, no content read
- **Modified files:** none in the repository. One ephemeral copy written to `/tmp/rev009-render.md` (render output for `cmp`).
- **Commit:** none (read-only role).

### 8. Remedy path

1. Apply F1–F8 and F11 to the candidate sources and references.
2. Rerun the feature through the packet route (F10), with stage references loaded and packet identities recorded.
3. Run the two PC-4 exemption and bypass executions (F9).
4. Record each run as a new execution. Keep run1 as a failed record.