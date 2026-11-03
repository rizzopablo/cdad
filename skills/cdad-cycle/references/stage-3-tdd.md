# Stage 3 — Anti-gaming TDD with isolated sessions

The longest stage. The main trap: a single agent writing test and implementation in the same session. Your role as orchestrator is precisely to prevent that by emitting separate handoffs.

## Test convention: contract, not implementation

Feature tests verify **behavioral postconditions (the contract)**, not implementation details. The GREEN stage needs real design freedom: the *how* is decided by the implementer; the *what* is defined by the test. This convention governs the RED packet and the acceptance criterion of the whole stage.

**Forbidden in RED**: tests that depend on internal structure — middleware call order, internal function names, mocks over plumbing. A mock over an internal detail freezes an implementation decision before an implementation exists: it inverts the flow (the test-writer "implements mentally" and the implementer merely translates), which is exactly what isolated sessions seek to avoid.

**Allowed in RED**: tests that verify the observable contract — wire messages, command results, emitted events, rejected auth, or generally any effect that crosses a boundary an external consumer of the system (another process, another service, the user) can see. An internal coordination event between two modules that never leaves the system is **not** observable for this purpose, even if technically it is "an emitted event" — it is plumbing dressed up as contract. If you are unsure whether something is observable, ask: *would an external consumer of the system perceive it if it changed?*

**Exhaustive coverage, load/perf, and edge cases not derived from the spec do not belong to the feature cycle.** They are the responsibility of a separate, later hardening stage/epic. Mixing both questions in the same gate makes the easier one to measure (coverage %) devour the time of the harder one to reason about (is the contract correct?).

**Property tests are NOT the same question as exhaustive coverage** — when the spec marks explicit invariants (sub-phase 3.4), the property test verifies THAT specific invariant, it does not maximize cases. The contradiction to avoid: reading the sentence above as "there are no property tests in the feature cycle" collides head-on with sub-phase 3.4 below, which does have them with their own gate. What falls outside the cycle is generating property tests for the sake of coverage (with no spec invariant behind them), not the ones the spec explicitly asks for.

**RED verifies the requirement, it does not maximize coverage.** Selection and its justification are rule R2 — single editable definition `sources/roles/test-writer.md` (`cdad-shared:convention-rule`): read it there for what to write, how to trace it and what to declare. This reference applies R2 to the stage and never restates its obligations; the application is what follows. What the stage prevents is concrete: facing a postcondition, a battery of unrequested edge cases or a property test with generators the spec never asked for produces tests extremely hard or impossible to satisfy, consuming time and tokens in GREEN iterations without reaching a result, and replaces the spec's "done" criterion with the test-writer's imagination. So every RED test (and every property test) must be able to point to the promise it serves and to the numbered postconditions it protects; if it cannot, it is superfluous — the same "Relevance" rule below.

**"Not a ceiling" (AJ2) is owned by R2, not by this file.** Whether a distinct committed behaviour needs more tests, and what equivalence forbids, are read in the rule's home; a promotion with a recorded reason is read in the gate's home (R4, `sources/roles/orchestrator.md`). This reference neither restates nor narrows either.

**Acceptance criterion of a feature**: every promise the spec commits is verified by behavior before the feature is accepted — not a coverage percentage, and not a count of tests.

**Relevance of tests**: every test written must serve a committed promise and trace to the numbered postconditions it protects. Tests are not written for completeness or for coverage; they are written because they verify a declared objective. If a test serves no promise, it is superfluous — record it in a test↔promise/postcondition traceability audit (see "Relevance audit" below).

**Mandatory counterpart**: since there are no exhaustive tests, the burden of precision moves to the spec; it does not disappear. The functional objectives, specifications, and requirements must be **maximally clear** — numbered, testable postconditions — before opening RED (see Stage 2). An ambiguous spec produces ambiguous tests and an incorrect implementation that still passes the suite (AP-13, Garbage Cascade).

### Counterweight: reducing redundancy does not reduce guarantees (R7)

R7 — the single editable home of this counterweight; the consumers cite it and
never restate it:

- Every promise the spec commits is verified by behavior before the feature is
  accepted. Reducing redundancy reduces the **number of tests**, never the
  guarantees.
- One test may verify several postconditions: that is many-to-one traceability,
  not a missing verification.
- `deferred-hardening` never allows postponing a committed promise, and never
  relaxes security, integrity or data preservation. What it defers is hardening
  (extra variants, load/perf, edge cases with no committed promise), with its
  reason recorded.
- The exceptional promotions — a test demanded with no user consequence — are
  defined ONLY in the gate's home (R4, `sources/roles/orchestrator.md`). This
  file does not define them again.

### Relevance audit (avoiding self-service)

The test→postcondition mapping (`test-audit.md` or equivalent) is **not audited by the same session that wrote the tests**. If the test-writer certifies its own relevance, the criterion "if a test doesn't map, it's superfluous" becomes self-serving. Use a third isolated session (or the Stage 4 reviewer) for that audit, just as test-writer and implementer are isolated from each other.

## Run budget (keeping the runtime from devouring the cycle)

Durante el ciclo la suite completa no corre como rutina de iteración o depuración (ver defaults por momento en §"Test evidence policy"). In projects with a slow suite
(typical in Odoo: the setup from scratch dominates the cost, not the number of
tests), iteration uses minimal runs with an anti-loop cycle: read the full
failure → written hypothesis → ONE change → ONE run; maximum 2 runs without
convergence → STOP and escalate, never re-run "to see if it passes". Hard
budget per stage with a STOP rule; exceeding it is a signal to escalate, not
justification for "one more run". In Odoo projects the full protocol lives in
`odoo-make-env/references/run-budget-protocol.md`; in other stacks,
adapt it to the same structure (cheap debugging, single authorized full gate when authorized).

## Test evidence policy

Single canonical owner of the evidence policy — hogar canónico. Consumers (`packets/`, `SKILL.md`,
the stage references) **reference** this section and never copy its text (INV-6).

Defaults por momento (PC-2):

| Momento | Default |
|---|---|
| Durante el ciclo | Tests focales y regresión proporcional; sin suite completa como rutina de iteración o depuración. |
| Cierre de feature | Suite completa recomendada. Si se omite se registra «suite completa no realizada», motivo, selección ejecutada y límites. |
| Cierre de epic | Suite completa obligatoria por defecto. Omitirla requiere dispensa expresa del dueño, registrada con motivo para ese cierre. |

La aprobación de esta política autoriza la corrida ordinaria de cierre de epic. Ninguna instrucción
operativa exige autorización adicional para esa corrida ni permite omitirla por simple ausencia de
permiso individual (PC-3). Autorizar una modificación, cerrar una tarea o disponer de un comando no
autoriza por sí sola otras corridas. La autorización no equivale a evidencia, ni autoriza publicación,
despliegue o reintentos indiscriminados.

1. **Proportional regression.** A change is verified with the **focused** tests
   plus the tests of the modules it touches; the regresión proporcional to
   the change, not a fixed retake of the whole suite on every sub-phase. La suite
   completa recomendada al cierre de feature y obligatoria al cierre de epic no
   sustituyen esta regresión proporcional durante el ciclo.
2. **Complete suite por momento.** Durante el ciclo no corre como rutina; al cierre de feature es
   recomendada; al cierre de epic es obligatoria por defecto salvo dispensa expresa del dueño para
   ese cierre. Sin autorización suficiente para esa corrida se registra suite completa no realizada,
   with the executed selection and its limits; never declare a green complete suite (nor a green
   CI gate) without its evidence. Ninguna omisión se etiqueta como verde ni como gate ejecutado.
   If the authorized evidence is insufficient for a committed obligation, that part blocks and
   requests the owner's decision. Un fallo, error o resultado no atribuible impide declarar verde
   la corrida; el cierre conserva el diagnóstico y la evidencia. La dispensa de ejecutar una suite
   no transforma una corrida roja en verde ni elimina una promesa incumplida.
3. **Equivalence of a registered run.** A recorded run may be cited instead of
   re-executed; the rule has a single canonical owner in `re-entry.md`
   §"Equivalence of a registered run" — this policy **references** it and does
   not copy its text.
4. **The methodology defines the evidence; the project declares the commands.**
   What evidence each gate requires is defined by the methodology; the comando focal
   and the comando completo (suite completa) are **declared by the project** (e.g. its
   Makefile or systemPatterns). Cada proyecto declara además: entorno, costo conocido con
   procedencia o costo desconocido expreso, presupuesto y estrategia de ejecución. Una suite
   lenta no constituye dispensa implícita: exige resolver presupuesto/entorno o solicitar
   dispensa cuando sea admisible; sin dispensa implícita por lentitud, costo o disponibilidad.
5. **Local/environment conditions.** A local or environment condition is
   captured in the evidence **registration** (registered as data) and does not
   become a requirement.
6. **Skips, esperados e inestables.** Los skips y los esperados no ejecutados satisfactoriamente —
   incluidos xfail cuando corresponda — quedan visibles con motivo y efecto sobre las obligaciones
   comprometidas. No bloquean por mera existencia, pero sí cuando dejan una promesa comprometida sin
   verificación suficiente. rc=0 no demuestra por sí solo suficiencia contractual. Una inestabilidad
   (inestable) no se resuelve reintentando hasta obtener verde ni repitiendo hasta lograr verde: se
   conservan los intentos; otro intento exige hipótesis nueva o información nueva y respeto al
   presupuesto. Si no puede acreditarse el resultado, se declara el bloqueo y se escala, sin
   seleccionar únicamente el intento favorable.
7. **Instalación limpia de addon (dimensión distinta).** When applicable, demonstrate instalación limpia
   from scratch with `test-clean` or the project's declared equivalent mechanism (verificación pertinente
   del addon; a warm run never replaces it). Instalación limpia and amplitud of selection are distinct
   dimensions: never infer the whole suite from the `test-clean`/`test-all` name. If the runner inseparably
   joins required clean install with a non-authorized complete suite, report the block and request
   authorization or environment resolution; omit neither silently nor invent flags/targets. Encargos without
   addon changes acquire no installation obligations by project domain.

## Conceptual anchor: the TDD loop is induction, not abduction

Reference: "Position: LLMs Can't Jump" (Zahavy, https://tomzahavy.com/files/llms-cant-jump.pdf). The paper itself uses "generating a function that satisfies unit tests" as its example of **Induction** — that is, CDAD's RED→GREEN loop is induction guided by an error signal. Implications for this cycle:

- **The separation architect (spec) vs implementer (tests) is not bureaucracy**: the specification with numbered postconditions is the prior axiomatization; the tests are the error signal that directs the inductive search. Without a clear spec, the implementer has no gradient (AP-13, Garbage Cascade).
- **What CDAD does NOT do is abduction**: generating new hypotheses/axioms (the paper's "jump") does not emerge from the test loop — it emerges in Stages 1-2 (Discovery/Planning) or in external review. If a feature requires a conceptual jump, the cycle will not produce it no matter how GREEN it is; it must be explicitly flagged to the orchestrator.
- **The exit gate measures induction, not judgment**: a green suite validates consistency with the contract, not that the contract is the right one. The contract's correctness is audited in Stage 4 (reviewer) and in external validation.

## Your role as orchestrator

You do NOT write tests, you do NOT implement, you do NOT refactor. You coordinate:

1. Identify which promise is next (the next promise with pending postconditions, or an orthogonal grouping of promises if the spec allows it).
2. Emit handoff to **test-writer** (RED).
3. Validate the red test at re-entry.
4. Emit handoff to **implementer** (GREEN).
5. Validate the green suite at re-entry.
6. Optionally: handoff to **refactorer** if there is evident friction.
7. Loop until every committed promise is verified.
8. If the spec marks invariants: handoff to **test-writer in properties mode**.
9. If the spec marks E2E criteria: handoff to **test-writer in E2E mode**.
10. Stage closure when all gates pass.

## Sub-phases

| Sub-phase | Role | When |
|----------|-----|--------|
| AUDIT / POST-AUDIT | test-writer | Existing suite + approved sustitutos of vigente (recorrido below, per R2) |
| RED | test-writer | Pending promise (pending behavior) |
| GREEN | implementer | After a valid RED |
| REFACTOR | refactorer | Optional, if there is friction |
| PROPERTIES | test-writer in properties mode | Spec marks invariants |
| INTEGRATION/E2E | test-writer in E2E mode | Spec marks E2E criteria |

Sustituto de comportamiento vigente (recorrido POST-AUDIT, por referencia a R2): R2 (`sources/roles/test-writer.md`, `cdad-shared:convention-rule`, puntos 5-6) owns the dispositions and the sustituto recorrido — physically new Sustituir/Consolidar admitted only in POST-AUDIT as identified in the approved AUDIT, with verde execution plus sensibilidad frente a defecto contractual concreto, originales kept until destination + evidence, mapa PC-5; never to RED for being a new file. Maintenance of vigente needs no GREEN when no implementation changes; pending behavior follows RED → GREEN separately.

## Sub-phase 3.1 — RED

Load `references/handoff-prompts.md` section "Test-writer (Stage 3 — RED)".

Before generating the packet, decide which promise to tackle (R2: the unit of
selection is the promise it defines, applied here to the sub-phase):

- The next promise of the spec with pending postconditions.
- Or a grouping of **orthogonal** promises (independent code paths that don't overlap). If they are coupled, one per cycle.

Before approving RED, apply the gate rule R4 (`sources/roles/orchestrator.md`):
ask and record "what breaks for the user without this test?" — with no answer
the test does not enter as an ordinary requirement.

Generate the packet with:
- The complete approved spec.
- Interface / signature of the module.
- Testing conventions (`docs/systemPatterns.md`).
- The promise to verify and the numbered postconditions it protects.
- Explicit reminder: observable-contract test, not internal structure — no mocks over plumbing (see "Test convention" above).

Deliver the packet, end the turn.

### Re-entry

Load `references/re-entry.md` section "Test-writer — RED". Critical checks:

- The test fails with an **AssertionError**, not an ImportError or a syntax error.
- The test verifies the observable contract, not internal structure (no mocks over plumbing, no asserts on call order or internal function names).

If it passes: update state, emit handoff to implementer.
If it fails for the wrong reason, or violates the contract convention: handoff back to the test-writer with the reason.

## Parallel dispatch

The orthogonal packet (one test-writer, N postconditions) remains the **default**: a single RED session, a single GREEN handoff. Parallel dispatch — several sessions of the same role running at once — is the exception, justified only when the packet is too large or the tasks are genuinely disjoint domains.

**Decision tree**:

- Are there 2+ (two or more) tasks **genuinely independent** — no shared state and no files in common? → parallel dispatch.
- Do they share a file or state? → sequential, or **wave dispatch** (turns: session 1 finishes and consolidates, only then does session 2 enter). Same file = serial, always.

**Precondition (mandatory)**: safe parallelism requires an **interface contract** — the plan's Consumes/Produces (see "Planning for complex features" in `references/stage-2-specification.md`). That contract is what makes the tasks independent: it defines what each session produces and what the next one consumes. Without it, there is no parallel dispatch: the sessions are serialized. "They don't collide today" is not a contract; it breaks tomorrow without anyone knowing.

**Dispatch rules**:

1. **Self-contained prompt per session** (rule §6 of state-passing): each packet includes the **owned files** (the files that session may touch) and a **do-not-touch list** (everything else, explicit).
2. **Verified disjoint scope**: when in doubt, `git diff --name-only` over the planned branches/domains before dispatching, and `comm -12` between the sets to detect overlap. The independence analysis is what enables parallelism, not what holds it back.
3. **Same role, different sessions**: each session still does not see the others' work — session isolation is not relaxed because there is parallelism. The only thing they share is the orchestrator's handoff.

**Final integration (ONLY the orchestrator)**: when all sessions have returned —

1. Review each summary (the agent's summary is **not evidence** that it went well).
2. Check file overlap between domains: `git diff --name-only` + `comm` (or equivalent) over what each session touched.
3. Run the evidence the consolidation requires per the **Test evidence policy** (§ above) with its defaults por momento (Durante el ciclo focal, Cierre de feature recomendada, Cierre de epic obligatoria por defecto o dispensa expresa); otherwise record suite completa no realizada with motive and limits (AP-3: without empirical verification there is no green).

Conflicts are resolved by the orchestrator, **never by the subagents** — a subagent resolving a conflict is touching someone else's domain, with a partial view and no contract. If integration fails, the orchestrator diagnoses and re-delegates with the corrected scope.

**State file**: ONLY the orchestrator writes it, ALWAYS. Parallel sessions never touch it — concurrent writes to the state file produce undefined state. The orchestrator consolidates it at every re-entry, just as in the sequential flow.

**Wave dispatch as the conservative default**: CDAD runs isolated sessions over the same working tree, so turns (waves) with disjoint domains are the conservative default mode. **Worktree-per-agent** (one branch + one worktree per session, orchestrated merge) is documented as an option for environments with native worktree support; the cleanup of those worktrees follows §5.6 — cleanup by provenance.

### Anti-rationalization table

| Rationalization | Reality |
|---|---|
| "The files don't collide, I don't need analysis" | The independence analysis is what enables parallelism, not what holds it back; without an interface contract, "no collisions today" breaks tomorrow. |
| "It's a single task, basically sequential" | Yes, and then it goes sequential — the decision tree does not present it as a parallel option. |
| "The agent's summary says it went well" | The summary is not evidence: run the evidence the consolidation requires per the **Test evidence policy** with its defaults por momento; otherwise suite completa no realizada with motive and limits (AP-3). |
| "The conflict is small, I'll fix it in my fix session" | Conflicts between domains are resolved by the orchestrator with full context, never by a subagent with a partial view. |
| "Same file in 2 tasks, I'll dispatch in parallel anyway" | Wave dispatch: same file = serial. |
| "Each session can update the state file" | Only the orchestrator: concurrent writes = undefined state. |

## Sub-phase 3.2 — GREEN

Handoff to implementer with: spec, the test that has to pass, interface, systemPatterns.

### Re-entry

Load `re-entry.md` section "Implementer — GREEN". Critical checks:

- Evidence per the **Test evidence policy** (§ above) with its defaults por momento: Durante el ciclo the focused test plus the
  modules the change touches; Cierre de feature con completa recomendada, Cierre de epic con completa obligatoria por defecto o dispensa expresa; otherwise suite completa no realizada with motive and limits.
- Implementer did NOT modify tests/.

The evidence follows the **Test evidence policy** (§ above) with its defaults por momento: the focused test plus
the regression the change requires; see the hogar canónico for the complete suite by moment (recomendada al cierre de feature, obligatoria por defecto al cierre de epic).
A registered run may be cited for consecutive
controls under the equivalence rule owned by `re-entry.md` §"Equivalence of a
registered run" (single canonical source), not duplicated here. If the
equivalence fails, the affected checks are re-run.

If it modified tests: AP-4. Ask to revert.

If it passes: update `postconditions_status: { "<N>": "green" }`. Ask whether to refactor or move to the next one.

If the suite is still red after the fix: **BEFORE re-delegating another GREEN**, the orchestrator triggers `references/stage-debugging.md` (systematic debugging: red loop first, ranked hypotheses, single fix on the root cause). The next fix handoff travels with the diagnostic protocol — re-delegating without a diagnosis is thrashing (AP-18).

## Sub-phase 3.3 — REFACTOR (optional)

**Only if there is evident friction** (duplication, poor naming, accidental complexity). If the code is clean, skip it. Refactoring for ritual's sake adds nothing.

Handoff to refactorer.

### Re-entry

Suite green AT ALL TIMES. If red: AP-11.

## Sub-phase 3.4 — PROPERTIES

Only if the spec marks verifiable invariants. Does not apply to code with many side effects or UI.

Handoff to test-writer in properties mode.

### Re-entry

Properties green with a fixed seed and a presupuesto finito y positivo declarado y justificado before the campaign (invariante, dominio y coste); evidence reproducible with semilla.

If a property fails with a specific input: that input is a bug. Handoff to implementer with the counterexample.

## Sub-phase 3.5 — INTEGRATION / E2E

Only if the spec marks E2E acceptance criteria or the feature touches multiple layers.

### Modes

- **A — outside-in**: E2E first, stays red throughout the cycle, and turns green as the pieces connect.
- **B — closure**: E2E at the end, after the units are green.

Decide it with the user at the start of Stage 3. For a clear central flow: A. For additions to existing flows: B.

Handoff to test-writer in E2E mode.

### Re-entry

If mode B and E2E red: assembly problem. Handoff to implementer.

## Loop between promises

Each time the GREEN (+ optional REFACTOR) of a promise closes, you decide:

- Are there promises with pending postconditions? → handoff to test-writer (RED) with the next promise.
- Are all green and the spec marks invariants? → handoff to properties.
- Are properties green and the spec marks E2E? → handoff to E2E (mode B) or verify the E2E that was already in place (mode A).
- Every committed promise verified? → stage closure (R7; the spec's `deferred-hardening` does not replace a pending promise).

## 🛑 Exit gate (Stage 3 → Stage 4)

- [ ] Test Audit completed and approved (a `test-audit.md` exists with benefit of the doubt resolved, if applicable).
- [ ] Every modified test has an explicit justification in spec.md.
- [ ] Every committed promise of the spec is verified by behavior — a test may verify several postconditions (R7).
- [ ] Every test written serves a committed promise and traces to its postconditions (no tests "for completeness").
- [ ] No test depends on internal structure (no mocks over plumbing).
- [ ] The test↔postcondition mapping audited by a session other than the one that wrote the tests.
- [ ] The spec's `deferred-hardening` records every deferral decided, with its reason.
- [ ] Suite green (verified empirically with the run output pasted by the user).
- [ ] If the spec marks invariants → property tests green.
- [ ] If the spec marks E2E criteria → E2E tests green.
- [ ] Granular commits (RED, GREEN, REFACTOR separate).

When all OK: update state (`current_stage: review`, `tdd_substage: null`). Announce the transition. Emit handoff to reviewer.

## Anti-patterns to watch for

- **AP-1**: single session for test + implementation.
- **AP-2**: test written after the code.
- **AP-3**: "green" test without empirical verification.
- **AP-4**: implementer modifies tests.
- **AP-11**: refactor breaks tests.
- **AP-12**: property tests with a random seed.
- **AP-13**: Garbage Cascade — ambiguous spec + non-exhaustive tests = incorrect implementation that passes the suite.
- **AP-14**: mock over plumbing — test coupled to internal structure instead of the observable contract.

Load `references/anti-patterns.md` if you detect signals.
