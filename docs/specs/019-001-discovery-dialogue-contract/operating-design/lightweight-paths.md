# Lightweight paths (PC-7)

Locators are at revision `64aa4670`. Status: proposal. Each path below has a
resolved applicability. None is left as "pending".

## 1. The three surfaces

| Surface | Where it is described | Nature |
|---|---|---|
| **A. Trivial normal-cycle spec** | `skills/cdad-cycle/references/stage-2-specification.md:116-122` ("Trivial (point fix): the spec can be one paragraph + one failing test. Still brainstorm + approval, but shorter.") | A size variant **inside** the normal cycle. |
| **B. Standalone `cdad-spec-and-test`** | `skills/cdad-spec-and-test/SKILL.md:16-25` (minimal spec: context, resolution, postcondition, verification) and `:95-104` (integration: "`cdad-cycle` owns gates/format; this skill never replaces them") | A standalone workflow for deliberately bounded work. It runs **outside** the cycle. |
| **C. "CDAD light"** | `CDAD_metodologia.md:114` (tier 5–6: "Brief spec … TDD with isolated sessions for the critical components only, optional review") and `:195` (lighter spec for simple features) | An explanatory label in the public methodology. It is **not** an operative workflow. |

The README recommends surface B for "smaller, deliberately bounded work"
(`README.md:21-25`).

## 2. Resolved applicability

**A — applies whenever a feature runs the normal cycle.** It shortens the artifact;
it does not remove an obligation. Discovery, mediated brainstorm, readiness,
independent draft review and explicit approval all apply (`readiness-and-approval.md`
§3). The pinned contract hash also applies.

**B — applies to deliberately bounded work that is not run through the cycle.**
It produces: a postcondition, a verification checklist, and the recorded decisions
of the task. It does **not** execute the normal-cycle gates. Its artifact therefore
states, in its own words:

- "Not reviewed by an independent reviewer under the cycle." Unless an independent review was actually run and recorded.
- "Not approved under the cycle." The requester's acceptance of the stated outcome is acceptance of the task, not an approval of a cycle spec.
- The verification that was actually run, with its result. A checklist that was not run is listed as not run.

If the work grows to need the cycle's gates (for example, isolated test writing
and review), the feature moves to surface A. The move is recorded. B does not
claim the gates it did not execute.

**C — is not a third protocol.** It describes the normal cycle at small scale.
Its operative content is the cycle's own references, which are authoritative
(`activation-map.md`, rule R8). Two statements in C are reconciled to them:

- "Optional review" is replaced, for surface A, by the mandatory draft review of
  `stage-2-specification.md:47-75`, unless the owner records an exemption as set
  out in `readiness-and-approval.md` §3.
- The "isolated sessions for the critical components only" phrasing is not used to
  relax the role separations of stage 3. Those separations stay as the cycle
  states them. This design does not change stage 3.

The methodology page itself is an explanatory consumer. It receives a pointer to
the cycle references. Its text does not activate anything.

## 3. Shared fidelity rules and proportion (D4)

Surfaces A and B share the classes of `handoff-fidelity.md` §1: confirmed decision,
proposal, unresolved item, technical evidence and correction. Their recording is
proportional.

| Obligation | A: trivial normal-cycle spec | B: standalone `cdad-spec-and-test` |
|---|---|---|
| Mediated dialogue through the orchestrator | Required (shorter). | Only as needed to settle the outcome and boundaries. |
| Architect technical consultation | Triggered by a consequential uncertainty or missing evidence, not by every question. | Triggered the same way, performed by whoever carries the task, and reported as such. |
| Recording of confirmed decisions with authority | Required, in the dialogue context. | Required, in the minimal artifact. |
| Readiness check (R1–R5) | Required. | Applied to the decisions the task depends on. |
| Independent draft review | Required, unless exempted (`readiness-and-approval.md` §3). | Not executed. The artifact says so. |
| Explicit approval and pinned hash | Required. | Not applicable under the cycle. The requester's acceptance is recorded as such. |
| Stage 3 separations (tests, implementation, review) | Required, as the cycle states. | Not claimed. Checks the author ran are reported as checks the author ran. |

### Rules that apply to both

- **No invented consent.** Neither surface may treat silence, or a default, as an answer.
- **No concealed uncertainty.** A *VERIFY* item or an unresolved item stays visible in the artifact.
- **No false review label.** An artifact that was not independently reviewed is not labelled as reviewed.
- **Proportion.** No fixed questionnaire, no number of questions per task, no delegation of every question to a subagent, and no scenario quota. The amount of record follows the risk of the change. These are rules for the form of the record; they do not fix a number of questions.

## 4. Lightweight example (illustrative)

*Illustrative, not a transcript.* A bounded wording correction in a user-facing message.

- **Intended:** the minimal task artifact records the requested replacement wording, its scope (one message template), the verification (the template is rendered and the wording matches the owner's text), and the result. It states "not independently reviewed; not approved under the cycle".
- **Unacceptable:** requiring unrelated domain research before the wording change, or stating that the short checklist proves completion of the normal-cycle gates.
