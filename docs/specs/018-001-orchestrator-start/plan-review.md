## Plan review — `docs/specs/018-001-orchestrator-start/plan.md` (borrador)

**Reviewed object:** plan draft `docs/specs/018-001-orchestrator-start/plan.md` (+ spec draft `spec.md`) of feature `018-001-orchestrator-start`.
**Digest (plan):** `a4679ae989e06a2fc06ee99f80dfd31713e3e0800700ade74cce92f6ffc42e28`
**Digest (spec):** `b09b4a450d4152b412c32d547c4de8969dc5d3c54c50ca3161fab2c76cb09301`
**Contract:** `draft-plan` (no approval; review is not approval).

---

### Findings

**F1 — BLOCKING — Missing prerequisite dependency on ADR-021 amendment materialization**
- Verdict: BLOCKING | Bucket: h
- Location: `plan.md` T1 block, `depends_on: []`; `diseno-aprobado.md` §"Precedencia de entrada" ("Antes de T1 se requiere aprobación específica y materialización de la enmienda a ADR-021; no se difiere al cierre"); epic `plan.md` ("la enmienda de ADR-021 ya fue aprobada por Pablo y registrada en `0c83f2dd`").
- Rationale: The approved design explicitly gates T1 on the specific approval and materialization of the ADR-021 amendment before T1, not deferred to closure. The draft plan declares T1 with empty `depends_on`, so the plan as written would allow T1 to start without that gate. Either the dependency must be declared (on the materialization commit `0c83f2dd`/the amendment artifact) or the plan must state why it is already satisfied. As written, the gate is invisible to the execution machinery.

**F2 — BLOCKING — Synthetic acceptance case (R1–R5, sensitivity R3) not mapped to a verifiable task**
- Verdict: BLOCKING | Bucket: h
- Location: `spec.md` "Caso de aceptación sintético (R1–R5)"; `diseno-aprobado.md` §"Caso de aceptación y sensibilidad"; `plan.md` T3/T4 focal_tests (`test_005_003_t2_examples_execute.py`, `test_orchestrator_startup_usability.py` (does not exist yet)) and T4 `observable_checks`.
- Rationale: The design requires a protected synthetic encargo for architect/discovery over CSV export, with a verifier that accepts the complete encargo and rejects the variant omitting R3, oracle intact, no real authorization/dispatch. The plan lists no dedicated test or check for this case; T4 only says "revision independiente sin hallazgos bloqueantes". A stated postcondition (PC-6 transmission) with no named producer/test is an observable defect: the acceptance oracle cannot be exercised. Either add a focal test (e.g. in the new `test_orchestrator_startup_usability.py`) or declare the case out of the proportional regression with reason (deferred-hardening).

**F3 — REQUIRED — Empty `regressions` across all tasks despite proportional-regression obligation**
- Verdict: OPTIONAL... → Required (no prefix)
- Location: `plan.md` T1–T4, `"regressions": []`; design §5 ("regresiones de preparación, reemplazo y continuidad afectadas"); epic acceptance ("pruebas proporcionales").
- Rationale: The plan's validation_strategy is "Documental + subprocess + regresión proporcional + make validate + cdad-suite.py validate", but every task declares `regressions: []`. For T1 (orchestrator entry) the design explicitly lists four regression tests in `focal_tests`, which partially covers this, but T2/T3/T4 do not name proportional regressions even though they touch CLI help and examples. Populate per task or justify emptiness.

**F4 — REQUIRED — Missing `make agents` / derived-output verification for PC-8 determinism**
- Verdict: Required
- Location: `plan.md` T1 `files` (no `agents/**` — correct, derived); T4 `observable_checks` (`make validate`, `cdad-suite.py validate`); design §3 "Salidas derivadas: regenerar mediante `make agents`"; spec PC-8.
- Rationale: The design mandates regenerating derived agents via `make agents` and never editing `agents/**` manually. The plan's verification never runs `make agents` nor compares regenerated output. Add to T1 or T4 observable_checks (e.g. `make agents` + diff clean) to substantiate PC-8.

**F5 — REQUIRED — Trial environment isolation not specified in T4**
- Verdict: Required
- Location: `plan.md` T4 `observable_checks`; design §6 ("sesión nueva", "ámbito aislado", "autorización para cada ejecución"); spec PC-9.
- Rationale: PC-9 requires a real trial with explicit environment, measurements and limits. T4's observable_checks only list doc-independent review and make validate; no check captures the isolated-scope/authorization prerequisites or the trial report artifact. Add an observable check naming the isolated scope and the recorded measurements (calls, turns, reads, bytes, times, errors).

**F6 — Nit — `integration_gate: "@validation_strategy"` placeholder without per-task validation strategy**
- Verdict: Nit
- Location: `plan.md` all tasks.
- Rationale: The header claims "ficha completa (`validation_strategy` + bloque `plan-tasks` canónico)" but `validation_strategy` is only global and the per-task gate is a reference placeholder. Not blocking for a draft, but the canonical block should either include a per-task `validation_strategy` or drop the claim.

**F7 — Nit — New test module `test_orchestrator_startup_usability.py` referenced but absent**
- Verdict: Nit (informational; expected for RED phase)
- Location: `plan.md` T2/T3 `focal_tests`.
- Rationale: The file does not exist yet; consistent with "módulo nuevo propuesto" and RED phase. No action required beyond ensuring the test-writer creates it; noting for traceability.

---

### Abstentions

- **A1 — Transmissibility of the synthetic case via existing fields (PC-6).** I cannot judge whether the orchestrator's existing fields can carry all R1–R5 requirements without inspecting the actual CLI help/continuity schemas and the encargo contract. The plan asserts "mediante campos existentes" but I did not verify the field set. Abstain; requires a structural audit of `cdad_packet.py`/`cdad_continuity.py` help output and the packet schema.
- **A2 — Whether `regressions: []` is acceptable for T4 (review-only task).** T4 is reviewer/orchestrator/scribe with no code edits; proportional regression may legitimately be empty, but the boundary between "no regression scope" and "unspecified" is a policy call for the orchestrator. Abstain on severity; flagged as Required (F3) for the owner to resolve.
- **A3 — ADR-021 amendment commit `0c83f2dd` existence.** I did not verify the commit exists in git history; the epic plan asserts it. If absent, F1 escalates. Abstain pending `git log` check by the orchestrator.

---

### Dictamen

The draft plan is structurally well-formed and faithful to the approved design in scope, postconditions and invariants, but it **does not yet reach the stated intention under its constraints**: two blocking gaps (T1 missing the ADR-021 materialization gate; the synthetic R1–R5 acceptance case with no verifiable producer) must be resolved before approval. Required items (proportional regressions, `make agents` verification, trial isolation) should be closed or explicitly deferred with reason. Review is not approval; the owner decides blockers and whether to proceed. No files modified.
