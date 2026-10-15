# Architect draft 001 — 004-003 planning procedures (borrador)

> **Estado: BORRADOR para revisión del dueño.** No es `spec.md` ni `plan.md`
> aprobados. Materializado por el orquestador desde el TEXTO FINAL del
> architect (ADR-003), sin edición de contenido.
>
> - Despacho: legacy identificado (no hay paquete v2 posible; brecha I2/D8).
> - Modelo: `mofgw/deepseek-v4.1-flash`. Sesión: `<ses-1>`.
> - Fecha: 2026-10-05. Base: HEAD `a4689eb` (con cambios sin commitear en
>   `docs/` ajenos a este borrador).
> - Encargo: `handoff-architect-001.md` + `efficient-orchestration-requirements.md`.

---

## Architect — 004-003 Planning Procedures (Discovery + Spec + Plan draft)

**Base:** HEAD `a4689eb`; worktree has uncommitted docs in `docs/specs/004-003-planning-procedures/` and epic docs (noted). Read-only. All claims cite `archivo:línea`.

Note on the packet gap: this delivery is legacy-identified. Root cause confirmed in source: `_approved_stage_entry` requires a `stage_history` entry with `feature=004-003`, `stage='specification'`, non-empty `approved_by` (`skills/cdad-cycle/scripts/cdad_packet.py:1220-1231`), and `_validate_v2_vigency` additionally requires `active_feature == execution.feature_id` (`:1284-1288`). In discovery neither exists for 004-003, so no v2 packet can be prepared — precisely D8. No falsified `approved` was used (`planning-contract-draft.md:200-201`).

---

## 1. Discovery (brief)

**Problem.** CDAD has no *procedure* to plan work and to review a plan **before** it is approved. Planning is scattered: cycle stage-2 has complex-feature planning (`skills/cdad-cycle/references/stage-2-specification.md:98-149`), epic has light planning with no producer/consumer control (`skills/cdad-epic/references/epic-planning.md`), and the renderer's contract model only knows two contracts. There is no independent technical review of *division, expected context, or the producer of each input* (`docs/epics/epic-004-single-source-planning/plan.md:76-77`), and no support for reviewing a **draft** plan object.

**Users.** The epic coordinator and the cycle orchestrator (they plan and delegate); the architect (produces the plan); the reviewer (reviews the plan in an independent session); the owner (approves scope/authority). These are **existing roles** — 004-003 creates no new agent (`efficient-orchestration-requirements.md:15-17`).

**What is missing today (evidence).**
- Renderer rejects any contract kind outside `{approved-epic-plan, approved-feature-spec}` (`cdad_packet.py:50`), routes architect→`approved-epic-plan`, everyone else→`approved-feature-spec` (`:700-704`, `:869-882`), and mirrors that enum in the schema (`skills/cdad-cycle/assets/active-packet.schema.json:16`). A **draft-plan review has no honest home**.
- Packet substages have no plan-review: there is `reviewer-review.md` only; no `reviewer-plan-review` / `architect-plan` files (`skills/cdad-cycle/packets/substages/` listing; `reviewer-review.md` content is code-diff oriented).
- Evidence reuse is a reviewer-side special case only (`stage-4-review.md:88-97`), not a general re-entry rule; `re-entry.md` demands "complete suite green" (`re-entry.md:71-73`) and re-run language (`stage-3-tdd.md:123`, `:150-152`) even when the tree is unchanged.
- The orchestrator source states supervision is proportional already (`sources/roles/orchestrator.md:116-118`) but the **procedure** that makes it executable for implementer/orchestrator/reviewer in one flow is not written.

**What does NOT enter (out of scope).** No new agent/planner; no metrics platform, universal cache, or per-command restrictions (`efficient-orchestration-requirements.md:15-17`, `plan.md:36-40`); no 003-002 receipt subsystem, no 003-003 stall detection, no 003-004 context renewal — only the hooks/facets 004-003 needs (`efficient-orchestration-requirements.md:110-120`); no Odoo clean-env redesign — preserve its real requirements (`:84-86`); no migrating v1 execution contexts (004-002 D2); F4 co-located scope fix is **evaluated, not silently absorbed** (see §4 D3).

---

## 2. Spec draft

> Format mirrors `docs/specs/004-002-project-execution-bootstrap/spec.md`. Status: **Draft** (no approval mark — `re-entry.md:44`).

### 1. Descripción funcional

004-003 turns the planning contract (`planning-contract-draft.md`) and the proportional-orchestration requirements (`efficient-orchestration-requirements.md`) into **procedures of the existing roles**, installed and consumable, with explicit contract support to review a plan **draft** object. It does not create a planner, a metrics platform, or a cache; it edits canonical sources and derives consumers so no competitor copies of a rule exist (single editable source + coherent derivation, `plan.md:101-104`).

Two surfaces are added: (a) a **plan-review** procedure (reviewer reviews intent + constraints + plan, not only spec), and (b) a **validation/re-entry** procedure that lets a complete verifiable result satisfy consecutive implementer→orchestrator→reviewer controls **without three equivalent full runs** when the tree/policy/environment equivalence is established (`efficient-orchestration-requirements.md:94-95`).

The **real acceptance journey** is this repo: the procedure is exercised to replan the pending work of 003-002, recording the verdict and concrete changes, without reimplementing 003-002 (`plan.md:269-270`).

### 2. Contracto

**Interfaces (proposed; not existing).**

| Surface | Behavior |
|---|---|
| Plan-review packet (substage `plan-review` on reviewer) | prepare renders intent + constraints + the plan object + its **version/identity** and a **non-approval** reference; the reviewer returns findings + dictamen; approval stays separate. |
| Contract kind for a draft object | A distinct `contract_kind` (e.g. `draft-plan`) with `authority_ref` (who requested the review) and a declared **plan version**. Falsifying `approved-*` is prohibited. |
| Re-entry equivalence check | A declared, evidence-based comparison (product version, test version incl. uncommitted, selection run, command, result, env/config/deps, original availability) that accepts citing a prior run or requires a new one. |
| Per-unit validation plan in the plan file | Each task declares focal tests, affected regressions, integration gate, and who runs each check; shared project strategy can be referenced. No-code cycles declare observable checks fitted to the artifact. |

**Postcondiciones (verified behavior).**

1. **PD-1 — Draft-plan review is a first-class, non-approving contract.** `prepare` can render a reviewer packet whose contract object is a plan **draft** with its version and an authority reference, without marking it `approved`; the emission carries the draft's sha/version, not an approval. Reusing `approved-*` to pass the guard is detected and rejected. *Cite:* replaces the two-kind enum at `cdad_packet.py:50,700-704,869-882` and `active-packet.schema.json:16`.

2. **PD-2 — Review is independent and semantic.** The reviewer receives original intent + constraints + plan (not only spec, `plan.md:278-279`), in a session distinct from the author. Structural validation (schema/references/rules) and semantic judgment are separated: a full-fields plan can still be rejected; a checklist does not certify optimality (`planning-contract-draft.md:105-107`). Only findings ≥80% confidence; verdict-tuple + abstentions apply (`sources/roles/reviewer.md:24-35`).

3. **PD-3 — Plan review does not self-approve scope.** Reviewing ≠ approving. Artifact reviewed, authorization reference, and approval state stay separate (`plan.md:290-291`). A boundary/authority/contract change goes to the owner; a valid reorder or permitted implementation detail does not require full re-approval (`planning-contract-draft.md:116-119`).

4. **PD-4 — Procedural, not a new agent.** The plan-review runs on the existing reviewer role; no permanent planner or new sub-agent is created (`plan.md:282-283`). It is invocable from an **installed** product without reading the whole source repo or converting the draft to approved (`plan.md:305-306`).

5. **PD-5 — Proportionate validation, no duplicate full runs.** Given a complete verifiable result, the same tree/policy/environment can satisfy implementer, orchestrator, and reviewer with the recorded evidence cited (path+line+commit), not three full suites. Recorded equivalence covers product version, test version incl. uncommitted changes, selection, command, result, env/config/deps, and original availability; a change to a shared contract or environment uncertainty forces the affected checks (`efficient-orchestration-requirements.md:37-43,94-97`).

6. **PD-6 — A new run is required when equivalence fails.** If the tree changed materially, policy/snapshot diverged, or the environment cannot be shown equivalent, the affected checks are re-run before closure; uncertainty is declared, not assumed. Same commit alone ≠ equivalent environment (`efficient-orchestration-requirements.md:40-43`).

7. **PD-7 — Focal vs transversal, treated differently.** A local correction uses focal tests; a shared-contract/uncertain-impact change widens (`efficient-orchestration-requirements.md:32-36,98-99`). The procedure does not treat both identically.

8. **PD-8 — Per-unit validation plan is part of the plan.** Every task declares focal tests, affected regressions, integration gate, and responsible runner; no-code work declares observable checks appropriate to the artifact, without inventing a software suite (`efficient-orchestration-requirements.md:27-31`). It can reference a common strategy once.

9. **PD-9 — Sufficient, non-exhaustive assignments.** A packet carries useful objective, contract+version, relevant inputs, scope, autonomous decisions, validation strategy, expected output, and return triggers; it references precise sources and allows role-scoped reads; it does **not** copy history or load the whole methodology; full logs stay outside active context (`efficient-orchestration-requirements.md:57-62`). Packets must not request reads the policy denies (`docs/activeContext.md:74`).

10. **PD-10 — Intervención por falta de progreso.** A retry answers to a hypothesis/new info; identical repetition, no progress, environment obstacle, or disproportionate cost triggers strategy review, reconciled with the existing two-attempt rule — no unlimited retries (`efficient-orchestration-requirements.md:63-69`). No limit authorizes skipping controls or declaring success without evidence.

11. **PD-11 — Procedural parity across stacks (generalidad).** The procedure works for Python (`tests/`), **Go co-located tests** (`*_test.go`), and **no-code cycles** (docs/config/multimedia). A no-code cycle produces an observable check appropriate to the artifact, not a fabricated code suite (`efficient-orchestration-requirements.md:29-31`; heredado `plan.md:52-53`).

12. **PD-12 — Installed, single-source, non-competing.** The procedure reaches installation (`skills/` + packets + `sources/` + generated agents) and each rule has one editable source with derived consumers; no manual edit of generated outputs (`efficient-orchestration-requirements.md:74-90`). Existing role sources keep their ownership; no second manual per role.

13. **PD-13 — Real journey over 003-002.** The procedure is exercised on the pending 003-002 work; verdict + concrete changes are recorded; 003-002 is not reimplemented here (`efficient-orchestration-requirements.md:102-104`, `plan.md:269-270`). Receipt vs quality-approval stays distinct (003-002's problem).

### 3. Invariantes verificables

1. `prepare` remains the **only** packet producer; no parallel producer, no hand-patching rejected packets (`sources/roles/orchestrator.md:28-36`).
2. Approval, mechanical receipt, and semantic compliance remain distinct; review never self-approves scope (`plan.md:290-291`; `ADR-011:127-129`).
3. Anti-bias: reviewer family ≠ implementer family; test-writer never sees implementation; test↔postcondition mapping audited by another session (`sources/roles/orchestrator.md:95-99`).
4. Role boundaries unchanged; plan review grants **no** implementation permission (`plan.md:290-291`).
5. Bash stays permissive; maps/hooks are not sandbox for launched processes (`ADR-012:27-30`).
6. Single editable source per rule; generated outputs never hand-edited (`efficient-orchestration-requirements.md:88-89`).
7. UNKNOWN stays explicit; missing metrics are not fabricated (`planning-contract-draft.md:154-156`).

### 4. Criterios de aceptación

1. PD-1–PD-13 traced to behavior tests; negative cases verify no approval is fabricated and no packet is produced for an unsupported contract.
2. A draft plan is reviewed **without** becoming approved, from a session distinct from the author, on an installed product.
3. Fixtures of a plan with an entry lacking a producer, a circular dependency, an incompatible contract, and invalid parallelism exercise the **checks actually implemented**; a schema does not decide semantic quality (`plan.md:301-306`).
4. The equivalence rule is exercised by at least one consecutive-flow case where a prior run is cited and one where a material change forces a fresh run (PD-5/PD-6).
5. Go co-located and a no-code cycle each have a declared, observable check (PD-11), even if minimal.
6. The 003-002 replan session yields a recorded verdict and concrete changes without reimplementing 003-002 (PD-13).
7. Validators pass; every retired/replaced assertion or fixture has traced justification (`004-002 spec §4.5` style).
8. Limitations accepted (e.g. mechanical limits not applied to GCC roles) are declared; UNKNOWN remains UNKNOWN.

### 5. Explicit gate changes required (for owner approval) and harmonization

The amendment requires making gate changes **explicit** (`efficient-orchestration-requirements.md:88-90`). Proposed **procedure changes, not new gates**, each harmonized with the canonical source that owns it:

| # | Gate/procedure change | Canonical source that owns it (single edit) | Derived consumers to reconcile (no new copy) |
|---|---|---|---|
| G1 | Re-entry may **cite** a recorded run when tree/policy/env equivalence is shown; a new run only when it fails | `skills/cdad-cycle/references/re-entry.md:54-73` | `stage-4-review.md:88-97` (generalizes the reviewer-only rule); `SKILL.md:318-346` gate 3→4 |
| G2 | "Full suite once per GREEN / complete suite green" gains the equivalence clause | `skills/cdad-cycle/references/stage-3-tdd.md:29-39,146-153` | `SKILL.md:521-522` evidence table |
| G3 | Two-attempt rule reconciled with new-info/no-progress criterion | `SKILL.md` (orchestrator behavior) + `re-entry.md` | `efficient-orchestration-requirements.md:63-69` |
| G4 | Plan-review substage + draft contract kind | `cdad_packet.py` (`VALID_CONTRACT_KINDS`, `ROLE_SUBSTAGES`, `_contract_for`) + `active-packet.schema.json` + new `packets/substages/reviewer-plan-review.md` | `packets/roles/reviewer.md`; `handoff-prompts.md` reviewer template |
| G5 | Per-unit validation plan field in the plan file | `planning-contract-draft.md` §4 (`:62-80`) and `stage-2-specification.md:106-112` | epic `plan.md` (procedure, already referenced) |

Ownership rule: each rule is edited **once** where it already lives; other surfaces reference it (`SKILL.md:435-437` "references are deepening material"; `plan.md:101-104`). The orchestrator source already states proportional supervision (`sources/roles/orchestrator.md:116-118`), so G1–G3 **make the procedure executable**, they do not add a second policy. No new gate is invented; where a change removes an old assertion it is replaced by an equivalent-guarantee check in the same coherent change (`c0-amendment:41`).

---

## 3. Plan draft (T1..Tn)

Each task = smallest unit with its own RED, independently rejectable (`stage-2-specification.md:102-104`). Files exact; Consumes/Produces = contract, not body.

| Task | Deliverable & verification (RED) | Consumes | Depende de |
|---|---|---|---|
| **T1 — Draft-plan contract kind (D8)** | Renderer accepts a distinct `contract_kind` for a **draft** plan with version + authority ref and **rejects** reusing `approved-*`; schema updated. RED: prepare renders a draft-plan reviewer packet whose contract is non-approved; a forged `approved-*` on a draft is diagnosed rc≠0 without publication. Files: `cdad_packet.py` (`:50,700-704,869-882,2252-2282`), `assets/active-packet.schema.json`, `tests/test_004_003_t1_draft_contract.py`. | `_approved_stage_entry`/`_validate_v2_vigency` semantics (`cdad_packet.py:1220-1231,1284-1288`) | spec/plan approved |
| **T2 — Plan-review substage & packet** | `ROLE_SUBSTAGES[reviewer]` gains `plan-review`; new `packets/substages/reviewer-plan-review.md`; reviewer packet carries intent+constraints+plan (not only spec). RED: an installed product renders a plan-review packet without reading the source repo; the static block stays ≤ limit. Files: `cdad_packet.py:51-57`, `packets/substages/reviewer-plan-review.md`, `handoff-prompts.md`, `tests/test_004_003_t2_plan_review.py`. | T1 | T1 |
| **T3 — Producer/consumer & dependency checks** | Mechanical checks over a plan fixture: entry without producer, circular dependency, incompatible contract, invalid parallelism (`plan.md:301-304`). RED: each fixture fails with a specific diagnostic; a valid plan passes. Files: `cdad_packet.py` (validator), `tests/test_004_003_t3_plan_checks.py`, fixtures. | T2 | T2 |
| **T4 — Per-unit validation plan (PD-8)** | Plan schema/section requires per-task: focal tests, affected regressions, integration gate, responsible runner, no-code observable checks. RED: a plan missing the field is rejected; a Go/no-code plan with an observable check passes. Files: `planning-contract-draft.md` §4, `stage-2-specification.md`, `tests/test_004_003_t4_validation_fields.py`. | T3 (plan format) | T3 |
| **T5 — Equivalence & re-entry procedure (G1–G3)** | Documented, installable rule: citation of a recorded run when equivalence holds; forced re-run when it fails; two-attempt ↔ no-progress reconciliation. RED: a "same tree, cite prior run" fixture passes without re-run; a "material change" fixture requires a new run; identical-retry without new info triggers strategy review. Files: `references/re-entry.md`, `references/stage-3-tdd.md`, `SKILL.md`, maybe `packets/common.md`; `tests/test_004_003_t5_reentry_equivalence.py`. | T1 (evidence identity) | T1 |
| **T6 — F4 co-located test-writer scopes (evaluated need)** | **Only if** D3 says 004-003's happy path needs it: `_default_scopes` derives test-writer scopes from `test_roots` only (`cdad_packet.py:902-907`) → with only `test_files`/co-located (`colocated_test_roots`) it yields empty write_scope and rejects the explicit scope (`debt-second-look.md:11`). RED: a Go-like policy (co-located `_test.go`) yields a non-empty, accepted test-writer write scope. Files: `cdad_packet.py:902-913`, `tests/test_004_003_t6_colocated_scopes.py`. | T1 | D3 decision |
| **T7 — Installed, real journey over 003-002 (PD-13)** | From an isolated install, run the plan-review on the pending 003-002 work; record verdict + concrete changes; no 003-002 reimplementation. RED is the journey's observable output (plan-review report + recorded changes), not a fabricated suite. Files: `docs/specs/004-003-planning-procedures/evidence/` + `docs/specs/003-002-*/` (plan changes only). | T1–T5 (T6 if needed) | T1–T5/T6 |

Self-review: every PD maps to ≥1 task (PD-1→T1, PD-2/3→T2/T7, PD-4→T2, PD-5/6→T5, PD-7→T5, PD-8→T4, PD-9→T2, PD-10→T5, PD-11→T4/T6, PD-12→T7, PD-13→T7). No `TBD` in contracts a task needs.

---

## 4. Owner decisions (with recommendation)

- **D1 — Support a native draft-plan contract in the renderer now, or interim legacy handoff?** *Recommend:* implement `draft-plan` in T1 **and** keep legacy-identified handoff only as transitional. *Why:* D8 requires explicit draft support (`plan.md:284-289`); legacy alone leaves the guard gap that blocked this very dispatch (`cdad_packet.py:1281`).
- **D2 — Does plan review require independent semantic review always, or only above a trigger?** *Recommend:* trigger-based (complex/new-interface/parallelism) plus mandatory review for the epic plan and the 003-002 replan. *Why:* avoid paperwork for trivial changes (`planning-contract-draft.md:110-114`), keep coverage where risk is.
- **D3 — Is F4 in 004-003 or a separate hardening feature?** *Recommend:* **in 004-003 only if the 003-002 happy-path replan runs on `tests/`** (this repo). Since this repo has `test_roots:["tests"]` (`docs/cdad-policy.json`), F4 is **not** on this repo's happy path; schedule F4 as **T6, conditional**, or as a separate feature before any Go consumer. *Why:* F4 is High but "No afecta a este repo" (`debt-second-look.md:11`); it only bites co-located layouts. Decide explicitly (herramienta/decisión, not a mention).
- **D4 — Which canonical file owns the equivalence rule?** *Recommend:* `re-entry.md` owns it; `stage-4-review.md` and `SKILL.md` reference. *Why:* re-entry is where a role's result is validated (`re-entry.md:1-10`); generalizes the reviewer-only rule (`stage-4-review.md:88-97`) — single source.
- **D5 — Metrics scope for 004-003.** *Recommend:* write into existing artifacts (supervision record + ledger), time/full-run-count/evidence-reuse/retrabajo; UNKNOWN declared; no telemetry platform. *Why:* `efficient-orchestration-requirements.md:122-127`; avoids 003-003 scope.
- **D6 — Models for the new plan-review role.** *Recommend:* reviewer of plan = reviewer model (family ≠ implementer/architect). *Why:* anti-bias (`sources/roles/orchestrator.md:95-99`); owner already fixed families per role (`supervision-record.md:8-10`).
- **D7 — Approval authority for the draft-plan kind.** *Recommend:* the owner approves scope; the review verdict is technical and separate. *Why:* `plan.md:290-291`; approval is non-delegable (`SKILL.md:28-29`).

---

## 5. Risks

1. **Gate-change blindness (highest).** Editing gate text without reconciling every consumer re-creates the divergence epic-002 fixed; mitigated by single-source ownership table (§2.5) and validators.
2. **Draft-contract scope creep.** Adding a contract kind touches the enum in 3 places (`cdad_packet.py:50`, schema `:16`, `_contract_for:869-882`) and the binding check (`:736`); missing one leaves a silent hole — T1 must test the negative (forged `approved-*`).
3. **Equivalence rule abused to skip real runs.** "Same tree" can hide env/dep drift (`efficient-orchestration-requirements.md:40-43`); PD-6 negative fixture is mandatory.
4. **Over-verification of prompts.** Testing that "a model always obeys" is prohibited (`efficient-orchestration-requirements.md:106-108`); acceptance must use small real cases.
5. **No-code/Go genericity under-tested.** PD-11 can pass on paper while Go co-located (F4) still fails at packet time (`cdad_packet.py:902-907`); T6 conditional + explicit D3.
6. **Replanning 003-002 collides with its own paused state.** 003-002 is `queued`, not reimplementable here; the journey must produce plan changes only, not code (`plan.md:269-270`; `efficient-orchestration-requirements.md:113-116`).
7. **Serialization fragility.** The v2 execution/state binding rejects mismatches (`cdad_packet.py:736`, `:494-495`); T7's installed journey must run isolated (`handoff-opencode-2026-10-05.md:36-39`).

---

## Limitations / ambiguities the orchestrator must resolve before materializing

1. **Packet-path status:** no v2 packet possible (verified, `cdad_packet.py:1281`); this draft is legacy. Materialization must be explicit and the gap recorded as D8's driver.
2. **Uncommitted inputs:** `docs/epics/.../plan.md`, `planning-contract-draft.md`, and the 004-003 docs are modified/untracked (`git status`); the owner must commit a durable reviewed revision before construction (`c0-amendment:96-98`).
3. **Epic plan shows `Status: Draft ... pendiente de ... aprobación` (`plan.md:357`)**, yet the owner activated epic 004. The spec relies on the epic plan as the architect contract (`cdad_packet.py:881`); the orchestrator should confirm whether the epic-plan approval mark needs to be recorded, since `_contract_for` reads it.
4. **`sources/roles/orchestrator.md` is already a mature canonical source**; G1–G3 must edit the reference files (which are its declared procedure sources, `sources/roles/orchestrator.md:76-78`), not the role source's prose, to avoid a competing copy.
5. **D3 (F4) decision gates T6** — the plan cannot be finalized with T6 until the owner rules on it.
6. **Not read (by design):** `tests/.sensitive-patterns.local` (prohibited). No access was denied during this session.
