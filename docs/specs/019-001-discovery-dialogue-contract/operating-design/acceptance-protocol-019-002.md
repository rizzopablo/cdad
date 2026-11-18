# Observed acceptance protocol for 019-002 (PC-11)

Locators are at revision `64aa4670`. Status: protocol. It is run by 019-002, after the
activation handoff (`activation-handoff-019-002.md`) has been delivered and its consumers
republished (`activation-map.md`). Nothing here has been observed.

Sources: `spec.md` Promise F, PC-11 and acceptance criterion 5; `discovery.md` §6.

## 1. Preconditions

1. The activation items are delivered and their consumers are regenerated or republished. The executed instruction versions are recorded (§5).
2. The protected scenario inputs are materialized **outside** `docs/specs/019-001-discovery-dialogue-contract/operating-design/` by the orchestrator, before the run. Their identifiers and digests are recorded in the run record.
3. An independent reviewer is available, in a session separate from the producer and the architect.
4. The run record is written outside the product directory (`verification.md` §4).

## 2. The journey (all steps required)

The complete journey must be observed from **need** to **independent draft review**.

| Step | Required observation |
|---|---|
| J1 Need | The owner states the need through the orchestrator. |
| J2 Functional dialogue | The orchestrator asks the functional questions and records the attributed answers. |
| J3 Targeted architect input | At least one consequential uncertainty is sent to the architect as a consultation. The consultation returns as one role report. |
| J4 Recorded decisions | Confirmed decisions, proposals, unresolved items, technical evidence and corrections are recorded in the Dialogue context section with authority (`handoff-fidelity.md` §3). |
| J5 Readiness | The orchestrator checks R1–R5 and records readiness or the blocking item. |
| J6 Draft | The architect returns a spec draft as final text, unapproved. |
| J7 Independent draft review | A reviewer in a separate session reviews the draft. The verdict is materialized and the blockers are routed. |

The protocol does **not** simulate J8 (approval). Approval belongs to the authorized
approver, or to the orchestrator only under the sole delegation exception of
`roles-and-dialogue.md` §1 (cited and within its limits). Its absence is recorded as a limitation, not as a failure of J1–J7.

## 3. The five cases (each one required)

Every case below requires observed evidence. Each one has these fields in the run record:

- **Protected-input locator:** the identifier and digest of the scenario input that exercised the case.
- **Actual response:** the agent's response, located by transcript turn.
- **Resulting treatment:** the resulting record, handoff, readiness outcome or draft treatment, located by artifact section.
- **Observed result** against the criterion below (met, not met, or not observed).
- **Recoverable locators** with the examined versions.

| Case | Criterion (from the approved spec) |
|---|---|
| **C1 Partial response** | The answered portion is preserved, and no answer is invented for the remaining consequential questions. |
| **C2 Unaccepted default** | The proposed default remains distinguishable from a confirmed decision. Silence, or an answer to another question, does not accept it. |
| **C3 Corrected decision** | The correction replaces the superseded understanding in the current decision context and in the resulting handoff or draft. Its provenance is recoverable. |
| **C4 Unresolved behavioural choice** | The consequential choice stays visible and prevents premature readiness until it is resolved or excluded by the authorized decision-maker. |
| **C5 Technical uncertainty** | The unverified assumption stays visible and is routed to targeted investigation. Its later treatment reflects recovered evidence, or an explicit limitation or blocker, not an assertion of fact without backing. |

**Coverage rules for cases:**

- One execution may cover several cases. Additional executions may supply missing coverage. There is **no scenario quota** and no fixed number of equivalent variants.
- A correctly observed blocked-readiness outcome can demonstrate C4 (or C5). It does **not** by itself demonstrate the complete journey (§2), which needs its own observed evidence.
- A response or artifact that cannot be recovered does not establish coverage.

## 4. Comparison and reporting

- Each case is compared with its criterion in §3. The comparison is recorded by the reviewer, not by the producer.
- **Failures are reported as failures.** A failed observation remains failed, even if a later run succeeds. A rerun is a new execution with its own record. It does not overwrite the failed one.
- **Limitations** are reported explicitly. A declared limitation does not convert an unobserved or failed case into a success.
- **Illustrative examples, structural checks, validators and declared limitations are not evidence of observed use.** They cannot substitute for a missing or failed observation.
- The run record is kept separately from any structural check (`documentary-contracts.md` §6).

## 5. Effective instruction versions

The run record lists the effective instruction versions used by the run:

- The commit of the repository at execution.
- For each effective instruction file (generated agents for the runtime used, packet sources, reference files the orchestrator loads), its path and SHA-256.
- For each published packet used in the run, its packet identifier and its frozen digests (`cdad_packet.py` frozen backup, `activation-map.md` R9).

A run that used an instruction version other than the one recorded does not count for that version.

## 6. Protected scenario inputs

- The scenario inputs are written by the orchestrator and materialized before the run, outside the product directory and outside the producer's write scope.
- The producer does not edit them. A correction to an input returns to the orchestrator and is recorded as a new input version.
- Each input is referenced in the run record by identifier and digest.

## 7. Limits

This protocol establishes observed use of the documented behaviour in the runtime and
instruction versions recorded. It does not establish:

- deployment or distribution of the instructions,
- universal runtime compatibility, or
- compliance in runtimes or scenarios that were not observed.

Those limits are reported in the run record.
