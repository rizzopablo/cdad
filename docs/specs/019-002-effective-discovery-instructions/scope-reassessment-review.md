# Dictamen ejecutivo

**Recomiendo una reversión selectiva, no restaurar todavía todo el orquestador anterior.** La corrección metodológica original —elegir la verificación según cada promesa— debe conservarse. También hubo una ampliación posterior de alcance: el dueño aprobó expresamente el trabajo de diálogo y, más tarde, la unidad de estrategia de verificación. No corresponde tratar todo ese trabajo como no autorizado.

El problema aparece en parte de su ejecución: se transformaron hallazgos de ejercicios puntuales en reglas generales rígidas. Hoy el candidato todavía exige, entre otras cosas, registrar cada mensaje antes de cualquier despacho al arquitecto, hacer una pregunta por decisión y copiar literalmente todas las entregas. Esto contradice la dirección actual de conservar la capacidad del orquestador para resolver situaciones y permitir correcciones formales triviales.

Hay además una contradicción operativa concreta: el skill exige completar el control de preparación **antes de cualquier despacho al arquitecto**, aunque otra instrucción prevé que la consulta al arquitecto ayude a preparar ese resultado. Eso puede impedir justamente la consulta necesaria para resolver una incertidumbre.

Propongo:

1. **Pausar los parches de escenarios** y acordar con Pablo el alcance corregido, sin reescribir las aprobaciones históricas.
2. **Conservar** la verificación proporcional por promesa y, provisionalmente, las correcciones acotadas de entrega de consulta y orientación de estado, sujetas a sus evidencias.
3. **Reformular selectivamente** las restricciones del orquestador: prohibir que escriba producto o tests, preservar la independencia sustantiva de los roles y permitir correcciones formales triviales sin alterar evidencia, conclusiones ni contenido sustantivo.
4. **Decidir aparte** cuánto del diseño de diálogo aprobado sigue siendo deseable. Mantener la fidelidad de decisiones no obliga necesariamente a conservar cada estructura, índice o gate introducido.
5. Dejar para decisiones separadas la instalación, la recuperación del `--check` instalado y una posible separación entre `cdad/` y `docs/`.

**El candidato 019-002 no está acreditado.** Los ejercicios observados y la suite tienen límites materiales; tampoco se demuestra que el candidato esté desplegado. No hice cambios, ejecuté tests ni aprobé nada.

---

# Detailed audit

## Scope, authority and baseline

This is a retrospective review, not authorization to implement, restore, deploy or change tests. The controlling owner direction is `docs/specs/019-002-effective-discovery-instructions/owner-direction-scope-reassessment.md`; the earlier correction is `owner-decision-orchestrator-scope.md`. The approved 019-002 contract remains historically pinned: the new direction does not silently rewrite it.

The pre-epic baseline is **`f15068afca3b30a42c80b0c55f9b7ab36c621c4c`**, the parent of `0673839d`, which opened the epic. At that baseline, `sources/roles/orchestrator.md` already prohibited inline role work, including tests, implementation and full-diff review, while assigning investigation and deviation resolution to the orchestrator’s wider responsibilities. Its materialization rule referred to role final text, but did not add the later blanket word **“verbatim.”**

### Recorded evolution—not all one original authorization

1. **Dialogue epic.** The initial plan committed at `0673839d` describes the single interlocutor and mediated architect interaction as the epic purpose. `f3060be2` records approval and clarifies both normal and lightweight workflow scopes. Therefore, dialogue work is not merely an unauthorized invention, even though the current owner direction asks that its cost and restrictions be reassessed.
2. **019-001 documentary design.** An attempted RED was removed (`fc029f67`, `309d8e8d`); `verification-blocker.md` explains why the test could not establish semantic fidelity. At `7b20d074`, Pablo directly decided that independent semantic review is verification for documentary-only units of this epic. The design was accepted under delegation at `4e26157e`. Acceptance is evidence of a historical decision, not permission to preserve every later restriction unchanged.
3. **019-003 general strategy.** The plan amendment at `01c34435` records Pablo’s approval of the simplified per-promise strategy. The feature specification was approved at `a568954f`; implementation began at `5547c14a`, with subsequent consumer-alignment fixes. This broadened the narrowly documentary decision into executable, semantic-only and mixed routing **with recorded approval**.
4. **019-002 activation.** Its approved spec, baseline `bc922c04`, implements the accepted dialogue design and includes separately requested idle/done orientation. `3322aaf3` activated the mediated path and consultation delivery; `c11825b4` changed status orientation. The owner subsequently superseded the spec’s ban on orchestrator investigation (`ae429087`), and `1ef42cc2` withdrew the explicit ban. The new retrospective direction now pauses further implementation and asks for a wider reassessment.

The owner’s present recollection identifies the verification-method correction as the necessary original objective. The repository independently establishes the later approvals above; it does not justify erasing them or assuming that every detailed restriction was individually approved.

## Findings

### 1. Readiness is required before the consultation that may establish it

**Required — Verdict: BLOCKING · Bucket: h**

- **Evidence:** `skills/cdad-cycle/SKILL.md:23` requires a recorded R1–R5 readiness result before **any** architect dispatch. `references/stage-2-specification.md:34–36` instead describes a consultation returning first, followed by readiness; `references/re-entry.md`, “Architect — brainstorm consultation and readiness,” allows dispatching a targeted consultation when readiness fails.
- **Consequence:** With consequential technical uncertainty, an orchestrator following the high-level skill literally can be told to finish the readiness check before it can ask the architect to resolve the uncertainty. The applicable entry points give incompatible ordering and can prevent or confuse legitimate work.
- **Closure:** Reconcile the canonical and effective instructions so consultation can occur when useful and the readiness decision precedes **drafting**, without imposing a new general restriction. Inspect generated consumers and verify the two routes—consultation needed and no consultation needed—against the agreed contract.

### 2. Materialization and dialogue controls exceed the owner’s current proportional boundary

**Required — Verdict: BLOCKING · Bucket: h**

- **Evidence:** `sources/roles/orchestrator.md:135–151,172–175` prohibits alteration of reports and requires verbatim final text. `references/stage-2-specification.md:19,32` requires every owner message before any architect dispatch, one decision at a time, and a prescribed append-only supersession index. `abb83c85` applied several of these after run1; its review explicitly proposed F11, the one-decision-at-a-time rule, as **optional** (`pc11-run1-review-009.md`, F11). The current owner direction expressly permits trivial formal corrections and rejects a catalogue of permitted activities as the replacement for the core product/test boundary.
- **Consequence:** A typo or formatting correction to a role delivery is treated like a substantive change, and routine multi-topic conversation can acquire unnecessary gates and recording work. This reduces the orchestrator’s ability to resolve ordinary situations without demonstrating a corresponding user benefit.
- **Closure:** Obtain an approved, proportionate formulation that permits trivial formal correction while preserving authorship, evidence, conclusions and independent role work. Reconcile the source, generated agents and methodological consumers. For dialogue, preserve recoverable current decisions and corrections while removing or justifying mandatory machinery against an actual need. This is a recommendation for rework, not authority to modify the approved contract.

### 3. Observations were converted into broad rules beyond what they demonstrated

**Required — Verdict: BLOCKING · Bucket: h**

- **Evidence:** Run1’s independent review reports real problems with unaccepted defaults becoming normative, incomplete decision provenance and summarized review records. It also states that the candidate packet route and stage references were **not exercised**, and therefore F1–F9 cannot be attributed to their wording alone (`pc11-run1-review-009.md`, F10 and limits). Nevertheless `abb83c85` applied F1–F8 and optional F11 to instructions. F1/F6’s investigation prohibition was subsequently withdrawn by owner decision and `1ef42cc2`.
- **Consequence:** A failed, partly nonrepresentative exercise drove general operational restrictions, including one the owner explicitly rejected. Continuing that patch-by-scenario approach risks further loss of practical capability without establishing causation.
- **Closure:** Classify each proposed rule by the real failure it prevents, the effective route actually exercised and its proportional remedy. Preserve the failed observations, but do not treat their proposed remedies—or a producer’s assertion—as proof of an instruction defect.

### 4. Candidate acceptance remains unsupported; the approval-route observation is not proof of a new product defect

**Required — Verdict: BLOCKING · Bucket: h**

- **Evidence:** Run1’s independent review found PC-11 cases unmet and recorded missing packet-route evidence. Run2’s `RUN-RECORD.md` reports no completed draft/review and explicitly says no independent evaluation was requested. Run3’s producer record reports an inferred exemption and later backfill in a controlled PC-4 scenario at candidate `9a6e841f`; it does not establish that the same event occurred in ordinary production use. `8902d9b1` subsequently made approval text more salient, but no successful independent re-exercise is established here.
- **Consequence:** Neither the current candidate’s observed dialogue fidelity nor its PC-4 route can be accredited from these records. Conversely, the run3 scenario alone does not justify redesigning owner-decision handling or asserting a newly introduced real-world defect.
- **Closure:** First decide the intended contract and whether the committed observed exercise remains required. Under the existing unchanged 019-002 contract, required evidence must be produced and independently assessed; alternatively, any change to that commitment requires the applicable owner decision and contract process. Do not claim that clearer wording alone proves agent compliance.

## What changed, and recommended disposition

| Group | Evidence and consequence | Recommendation |
|---|---|---|
| **Per-promise verification** | `5547c14a` and follow-up commits modify stage 2–4 guidance, role sources, packets and generated agents. `019-003/closure.md` records independent review and a bounded 38-test regression. | **Retain the principle and necessary consumer routing.** Do not replace semantic review with fabricated RED; preserve tests before implementation where executable behavior is pending and both forms for mixed promises. Reassess excess wording separately. |
| **Dialogue design and activation** | 019-001 was accepted; `3322aaf3` changed architect/orchestrator sources, generated agents, handoffs, packets and guidance. The approved epic wanted faithful decisions and one interlocutor. | **Rework selectively.** Keep the useful distinction between confirmed, proposed and unresolved decisions and a usable handoff; reconsider rigid record format, one-question quota and universal pre-dispatch gate with the owner. |
| **Investigation ban** | Run1 F1/F6 proposed it; `1ef42cc2` withdrew its explicit form after `ae429087`. However `sources/roles/orchestrator.md:136–137` still says technical bootstrap material comes from the architect’s report, and its technical-question wording should be assessed against the later permission to investigate. | **Do not restore the ban.** Reconcile remaining ambiguities with owner direction; retain attribution when technical evidence matters. |
| **Verbatim delivery** | Added in the cumulative diff and reflected in generated agents; it prevents silent substantive rewriting but also bans trivial formal corrections. | **Rework**, preserving the independent author’s substance and evidence, not mandatory byte identity for every presentation correction. Frozen packet integrity remains a separate obligation. |
| **Consultation delivery, PC-5** | `cdad_result.py` changed at `3322aaf3`; `tests/test_019_002_discovery_delivery.py` exercises native and OpenCode derivation, materialization and draft-kind rejection. An obsolete rejection expectation was intentionally changed. | **Provisionally retain**, because the approved dialogue route needs a deliverable report. Its mechanical tests do not prove dialogue fidelity. Revisit only if the owner changes that route. |
| **Closure orientation, PC-7** | `c11825b4` changes `cdad_packet.py` status and closing guidance; `tests/test_019_002_resting_orientation.py` exercises closure → status → opening and incoherent `done/null`. The epic plan records the separate owner request. | **Provisionally retain**, independently of dialogue restrictions, subject to applicable evidence. This is not part of the original semantic-verification objective but was expressly added. |
| **README regressions** | `regression-audit.md` attributes one installed-path regression to 019-002 and four README failures to `3b62d552`, before 019-002; later fixes include `deda7786` and `2de6e72b`. | **Do not attribute all five to this epic’s new dialogue design.** Retain or assess the fixes on their own merits; do not reverse them merely because they occurred during the epic. |
| **Installed-methodology access loader** | The proposed loader and bootstrap interface were reviewed but not implemented. `reference-access-simplified-draft.md` explains the smaller scoped AUDIT; the final test audit records that the installed methodology was consulted as role instruction. | **Do not build the loader on this evidence.** The failed proposal shows scope escalation, not an existing vulnerability. The product-under-review boundary must not be confused with a ban on using installed methodology. |
| **Directory separation** | Owner direction calls `cdad/` versus `docs/` a separate proposal. | **Defer.** No migration is authorized or needed for this audit. |

### Selective reversal versus restoring the old orchestrator

- **Selective reversal is preferable as the next decision:** it can remove the observed overconstraints while preserving the approved verification strategy, PC-5 transport, PC-7 orientation, and independent role boundaries. Its cost is a careful cross-consumer consistency review.
- **Restoring the baseline orchestrator** is a legitimate fallback if the owner concludes the accumulated dialogue instructions cannot be simplified safely. It is **not** a complete rollback of the initiative: the methodology references, packets, generated agents, executable changes and tests would remain. Restoring only one file would leave incompatible consumers; restoring everything could discard separately approved and useful corrections. Neither outcome has been tested, so no claim is made that either is mechanically safer.
- If restoration is chosen, reapply only owner-approved essentials—including per-promise routing—and reconcile all affected consumers. That requires a new authorized implementation assignment, not action by this reviewer.

## Verification and closure categories

The labels below describe the evidence examined, **not feature acceptance**:

| Promise | Category | Basis and limit |
|---|---|---|
| A / PC-1–3, dialogue fidelity | **Failed** in observed run1; current full candidate **unable to verify** | Run1 independently found failures but did not exercise the candidate packet route. Run2 did not complete the journey or receive independent evaluation. Owner superseded the investigation prohibition. |
| B / PC-4, reviewed or exempted draft | **Failed** in the recorded run3 producer observation; current candidate **unable to verify** | Later wording changed; no successful independent re-exercise established. This is not evidence of a newly introduced automatic CLI gate defect. |
| C / PC-5–6, delivery and frozen packets | **Unable to verify as a whole** | Tests and historical reports were inspected, not rerun; this audit did not independently check all promised old/new packet byte comparisons. |
| D / PC-7, closure orientation | **Unable to verify as a whole** | Black-box tests and implementation delta inspected; no independent execution in this assignment. |
| E / PC-8–10, coherent consumers | **Contradictory** | The pre-consultation readiness conflict is present; full consumer coverage and distribution were not independently established. |
| F / PC-11, observed use | **Failed / missing required evidence** | Run1 failed; run2 and run3 do not close the committed journey and cases. |

### Verification actually recorded

- `019-003-final-regression.log`: at `c8fff61b`, the recorded command was `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_cdad_generate.py tests/test_010_001_documentary_contracts.py tests/test_role_packet_render.py`; output **38 passed**, exit 0. This is bounded mechanical evidence, not semantic certification.
- `019-epic-tests-suite.log`: interrupted, **5 failed, 915 passed, 4 skipped**, exit 2. `019-epic-suite-2.log` ends mid-run. The separately named `019-epic-complete-suite.log` stopped during collection because `odoo` was unavailable. **No completed green epic suite is established.**
- `review-fix-009.md` reports 68 selected tests passing after `1ef42cc2`; I did not independently rerun or verify a full log for that claim.
- `local-deploy-verified-check.log` ends in **FAIL** with missing/drifted skill destinations. The 019-003 closure says installation was separately requested and completed, but its `--check` cause remained unresolved. This does not establish that 019-002 was deployed.

## Installed versus candidate

The installed `~/.agents/skills/cdad-cycle/SKILL.md` and candidate `skills/cdad-cycle/SKILL.md` differ. Their SHA-256 values observed in this audit were respectively:

- Installed: `a8d2ae5396e1126956e25a842115e6b8355d51919ec5482d6381ab8819d07298`
- Candidate: `e8aef484a9a553d2141fc11ff37f0ce3f8f2a58abd130742105822ac1ab4cf95`

The displayed diff shows the candidate’s new pre-dispatch readiness and approval bullets absent from that installed file. This is a **single-file comparison**, not a complete installed inventory or a deployment verdict. The recorded failed installation check further prevents claiming complete installed/candidate equivalence.

## ADR and role-boundary check

I inspected the current-decisions table in `docs/systemPatterns.md:5–50` and the `docs/adr/` listing. The reviewer-relevant decisions include ADR-003 on materialization, ADR-011 on proportional supervised autonomy, ADR-020/040 on evidence and documentary contracts, ADR-034 on design principles and ADR-042 on evidence by cycle moment. I found no row in the displayed table pointing to an absent ADR file. I did **not** establish a complete semantic status audit of every ADR in the directory; that is an abstention below.

The real change is mixed: documentary instructions **and** executable CDAD scripts/tests. It is not an Odoo addon change merely because some Odoo-specific guidance and generated agents changed; no addon clean-install claim is made.

## Smallest proposed recovery plan

1. Have the owner decide the desired scope for dialogue versus verification strategy, and resolve the current contradiction with the approved historical spec through the applicable contract procedure.
2. Commission a narrowly scoped independent design of the orchestrator wording and affected consumers: product/tests remain outside orchestrator authorship; independent substantive role work remains independent; trivial formal corrections remain possible.
3. Decide PC-5, PC-7 and existing README fixes separately from that wording; retain their tests unless an authorized test audit establishes a different disposition.
4. Review the resulting **actual** diff and proportional evidence, including effective generated consumers. If the existing PC-4/PC-11 commitments remain, observe and independently assess them without pretending structural checks prove comprehension.
5. Treat local installation/check diagnosis and any eventual deployment as separate authorized operations. Do not migrate directories in this recovery.

## Evidence and limits

- **Reviewed revision:** `6d32000b2424b982c4480253aaf413d04c2cb88f`; pre-epic baseline `f15068afca3b30a42c80b0c55f9b7ab36c621c4c`.
- **Packet intake:** `validate-request` and `validate-packet` completed without output or error; `render --route C` matched the received identification; `cmp` of the full render against `PACKET.md` returned `canonical_cmp=0`. Execution context declares schema version 2.
- **Principal commands:** `git log --reverse --oneline …`, `git diff 0673839d^ HEAD -- …`, `git show …`, targeted `rg`/`nl`, `sha256sum` of installed and candidate skill files, and `tail` of the named evidence logs. Their pertinent outputs are stated above.
- **Tests run by this reviewer:** none. The assignment expressly excluded test execution.
- **Files modified / commits created by this reviewer:** none. At the final check, `git status --short` was empty and `git diff --quiet` returned 0. Earlier in the session it showed a pre-existing state-file modification and untracked owner direction; their disappearance was not caused or investigated by this reviewer.

## Abstentions

- I cannot establish a complete line-by-line disposition of every changed consumer or every test in the cumulative 54-file product diff from this bounded pass.
- I cannot establish the complete cause of the installed `--check` failure, all installed versions, or runtime behavior after `1ef42cc2`.
- I cannot independently authenticate the complete original owner conversation beyond the recorded decisions and plan history cited here.
- I cannot establish that restoring the old orchestrator, or selective reversal, will be mechanically safe before an authorized implementation and verification.
- I did not fully reconcile the semantic status of every ADR against the decisions table.
- I do not approve the candidate, the recovery proposal, a contract amendment or an epic closure.