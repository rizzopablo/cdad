# Spec — `006-002-delegation-by-layer`

- **Feature:** `006-002-delegation-by-layer` (epic `epic-006-opencode-concurrency`)
- **Stage:** 2 (Specification) — **DRAFT. NOT APPROVED.**
- **Contract:** `docs/epics/epic-006-opencode-concurrency/plan.md` §8 (enmienda 001) + §9 (enmienda 002).
  Verified: `sha256(plan.md) = b6a59502…f2e63`.
- **Stage-1 input:** `docs/specs/006-002-delegation-by-layer/discovery.md`.
- **Depends on:** `006-001-opencode-concurrency-reliability` (closed).
- **Status:** awaiting explicit user decision. This document approves nothing.

## 1. Functional description

Today the *same* runtime mechanism lives in **five installable places at once**, while the
generated agents carry only a neutral rule:

- `skills/cdad-cycle/SKILL.md:134-173` (§4), `:243`, `:263-275`, `:462-466`, `:499-504`;
- `skills/cdad-cycle/references/opencode-delegation.md:1-194` and
  `references/claude-code-delegation.md:1-122` (whole files);
- `references/handoff-prompts.md:36-49, 86-91`; `references/sub-agent-strategies.md:97-105`;
- `references/cli-delegation.md:267-276`; `references/progress-guards.md:27, 38`;
- versus a single hardcoded neutral rule in `scripts/cdad-generate.py:812-828`.

The measured consequence is recorded: a consumer orchestrator read the skill as if it mandated the
CLI adapter (`docs/epics/epic-006-opencode-concurrency/execution.md:112-118`).

**Outcome.** Each text returns to its layer, mechanically:

| Layer | Artifact | Holds after this feature |
|---|---|---|
| **SKILL** | `skills/cdad-cycle/SKILL.md` §4 | principle, order, adapter rule, role invariants, spawn guard — **no runtime tool names** |
| **SKILL** | `references/re-entry.md` | the materialization protocol + a **transport-equivalence** subsection |
| **SKILL** | `references/handoff-prompts.md`, `sub-agent-strategies.md` | methodology templates only |
| **AGENT** (source) | `sources/agents/adapters/{opencode,claude-code}.md` | new `<!-- cdad-section:delegation -->` |
| **AGENT** (generated) | `build/staging/agents/*/cdad-orchestrator.md` → `agents/**` | the composed delegation rule |
| **SCRIPT** | `scripts/cdad-generate.py` | composes `sections["delegation"]`; no hardcoded order |
| **ADAPTER** (doc) | `references/cli-delegation.md` | the adapter contract, **without** the transport-choice rule |
| **DOCS** (non-installable) | `docs/**` | historical detail: reload, dead `delegate` channel, 429, provenance |

## 2. Postconditions (numbered, observable, testable)

> Absence oracle (shared by PD-1/PD-3/PD-6/PD-11): pattern of
> `tests/test_005_010_t3_references.py:88-114` (`CONCRETE_MODEL_ID_RE`, `SPACED_MODEL_LINE_RE`,
> `PROVIDER_RE`) extended with **tool *forms*** — code-spans `` `task` ``, `` `delegate` ``,
> `` `Agent` ``, the token `subagent_type`, `opencode run`, `sessions_spawn`, `Agent tool`.
> It does **not** match the bare word *task* (prose such as "atomic task"): discovery §4 risk 6.

**PD-1 — Skill layer free of runtime tools and concrete models.**
No installable skill text (`skills/cdad-cycle/**`, `skills/cdad-epic/**`) names a runtime dispatch
tool or a concrete model in a delegation context.
*Oracle:* absence test (pattern above). **Explicit exclusion:** `references/context-meter.md` is a
**reader/measurement** contract — it declares `task`/`subagent` as *recognized dispatch tool names*
(`context-meter.md:156-172`), i.e. measurement data, not a delegation instruction.

**PD-2 — Each orchestrator agent declares its mechanism, generated from the adapter source.**
(a) `sources/agents/adapters/opencode.md` and `sources/agents/adapters/claude-code.md` each carry
exactly one `<!-- cdad-section:delegation -->` block (grammar: `scripts/cdad-generate.py:107-155`;
`REQUIRED_ADAPTER_SECTIONS` at `:64`).
(b) `compose_orchestrator_agent` (`scripts/cdad-generate.py:749-870`) emits that section and no
longer hardcodes the order (`:812-828`).
(c) Staging `PROFILE=basic`: each orchestrator names its native mechanism + `subagent_type: cdad-<role>`
and **does not** require the CLI adapter intra-runtime.
(d) Each section declares the byte-identical packet pass and the receipt link.
*Oracle:* text test over `build/staging/agents/{opencode,claude-code}/cdad-orchestrator.md` with
`PROFILE=basic` + generator test.

**PD-3 — §4 keeps the neutral core.**
`SKILL.md:134-173` retains, in abstract form, the seven points — (1) principle, (2) order,
(3) adapter rule (*owner of the session lifecycle*), (4) role invariants, (5) spawn guard,
(6) receipt, (7) packet and re-entry transport-independent — naming no runtime.
*Oracle:* concept test (alternatives per concept, pattern of `require_any`,
`tests/test_005_010_t3_references.py:139-152`) + the PD-1 absence test over that section.

**PD-4 — A `basic` reviewer dispatch is resolved without ambiguity.**
An OpenCode orchestrator under `basic` has one answer: dispatch by the native mechanism; it does not
use the CLI adapter intra-runtime; it **declares the family not guaranteed by the installer** and
registers the attempt; it **never chooses or invents a model**.
*Observables:* the OpenCode `delegation` section (staging `basic`) contains (i) the native mechanism,
(ii) the intra-runtime adapter prohibition, (iii) the `basic` + "not guaranteed" + registration
phrase, (iv) the declaration that a model is passed **only if it comes from the environment
configuration** (VERIFY-3 resolution, D-3).
*Plus:* the bounded real run of the acceptance unit — **behavioural evidence, not proof**.

**PD-5 — The native receipt is linked.**
`references/re-entry.md` declares the transport equivalence: native dispatch returns FINAL TEXT in
the orchestrator's session; the orchestrator stages the **exact bytes** under `.cdad/inbox` +
`RESULT.json` and runs `receive` → `validate-receipt` → `materialize` → transition; the receipt
stays `semantic_status: pending` (receiving approves nothing).
*Observables:* (a) the subsection exists in `re-entry.md` (protocol at `re-entry.md:14-68`);
(b) §4 **and** each `delegation` section link to "Orchestrator materialization protocol";
(c) `receive` still accepts only `source.kind="staged-file"`
(`skills/cdad-cycle/scripts/cdad_result.py:238-240`) — the existing `receive` unit test stays green.

**PD-6 — Context discipline in both orchestrators.**
Both generated orchestrators (staging `basic`) carry the 4 rules: (1) orient with the compact
`status` view first, **no** dumps of state/ledger/skill; (2) rotate the session at task boundaries,
not mid-unit; (3) do not self-repair — re-dispatch the role naming the defect; (4) **never `/tmp`**
as channel or workspace. `references/orientation.md` §1 remains the owner of "view first"; the
source **cites** it and does not duplicate it.
*Oracle:* text test over staging `basic` + absence grep for `/tmp` in installable text.
*Honest limit:* the test proves the rule **exists**, not that it is obeyed. The only behavioural
evidence is the acceptance run's transcript, and it is a sample.

**PD-7 — Deterministic generation + validators green.**
`make staging PROFILE=basic && make agents` is deterministic/idempotent (second `make agents` →
empty `git diff`); `make validate` (`tests/validate-consistency.sh` +
`tests/validate-odoo-specialization.sh`, `Makefile:22-25`) passes; the focal suite of the 6 coupled
modules passes.

**PD-8 — Boundary respected.**
The diff touches **neither** `install.sh`, **nor** `scripts/cdad-models.sh`, **nor** the CLI
delegation adapter (`skills/cdad-cycle/scripts/cdad_delegate*.py`), **nor** `docs/adr/ADR-007*`,
**nor** the consumer's handoff/config. It **does** touch the *agent adapter sources*
(`sources/agents/adapters/*.md`, decision D-1) and the reference document `cli-delegation.md`
(PD-10) — AC-8's "the adapter" means the delegation **program**, not the agent adapter sources.
*Oracle:* `git diff --name-only` bounded to `skills/**`, `sources/**`, `agents/**`, `tests/**`,
`docs/**`, plus explicit exclusion asserts.

**PD-9 — Runtime references withdrawn; history preserved.**
`references/opencode-delegation.md` and `references/claude-code-delegation.md` leave the installable
skill tree; their historical/verification detail (reload/version, dead `delegate` channel, 429,
provenance) is preserved under `docs/**` as **non-installable** evidence; the "How to read the
references" table (`SKILL.md:447-473`) drops the two runtime rows.
*Oracle:* existence/absence asserts + reformulated F004.

**PD-10 — `cli-delegation.md` is the adapter contract only.**
The reference keeps the adapter contract (`cli-delegation.md:1-266, 278-334`) and loses the
transport-choice rule (`cli-delegation.md:267-276`), which moves into the runtime agent's
`delegation` section.
*Oracle:* absence assert on the removed block + conservation assert on the adapter contract.

**PD-11 — `SKILL.md` §2 without models.**
§2 loses the "Model family" column (`SKILL.md:67-75`) and the profiles paragraph (`SKILL.md:77`),
replaced by one sentence: the model of each role is the one configured in the runtime, the skill
names no models, and the reviewer's different family is an invariant guaranteed by configuration
when the profile fixes models and **declared** when not. `handoff-prompts.md:515` loses its concrete
model example. F001 of `tests/validate-consistency.sh:260-268` is **reformulated, not deleted**.
*Oracle:* absence assert + rewritten F001 asserting the new sentence and the `basic` caveat where it
still belongs.

## 3. Invariants

- **INV-1.** No skill names a runtime dispatch tool for delegating (the absence oracle targets tool
  *forms*, never the bare word *task*).
- **INV-2.** No installable text fixes models in a delegation context; the model is the configured one.
- **INV-3.** The packet and the receipt are **independent of the transport** — the same `receive`
  ends every route (`re-entry.md:14-68`).
- **INV-4.** Nothing uses `/tmp` as a channel or workspace; the receipt goes to `.cdad/inbox` and
  temporals to the declared workspace.
- **INV-5.** Delegation expands neither authority nor scope; the worker does not write
  `docs/.cdad-state.json` (`SKILL.md:136-141`).
- **INV-6.** A separate session is **not** a sandbox: it guarantees neither isolation nor another
  model family (`SKILL.md:140-141`).
- **INV-7.** The reviewer's family differs from the implementer's — **guaranteed by configuration**
  when the profile fixes models, **declared** when it does not (never silently omitted).
- **INV-8.** `references/context-meter.md` remains a **reader/measurement contract**; naming
  `task`/`subagent` there is a recognized-dispatch declaration, not a delegation instruction.

## 4. Decisions

- **D-1 (=a, A1).** Each runtime's delegation rule lives in its orchestrator agent, generated from a
  new `delegation` section of the adapter source (`sources/agents/adapters/{opencode,claude-code}.md`)
  composed by `scripts/cdad-generate.py`. The two runtime references leave the skill: their core goes
  to the agent, their historical detail to `docs/`. `cli-delegation.md` stays as the adapter contract
  without its transport-choice rule. **A2 discarded** (evidence: `install.sh:1036-1045` copies the
  *same* skill tree to all three bases — a per-runtime reference inside the skill is not installable
  today).
- **D-2 (=b).** §4 keeps the seven points of discovery §2(b), with no tool or runtime names.
- **D-3 (=c, resolves VERIFY-3).** Three-part declaration, identical in each orchestrator:
  (1) by profile — guaranteed by configuration when the profile fixes models; under `basic` **not**
  guaranteed, and the orchestrator **neither chooses nor invents** a model; (2) registration —
  `runtime`, `model_configured`, `model_reported`, `session` with `null`/`unknown` when unobserved,
  and the review gate writes "invariant not guaranteed" instead of omitting it; (3) legitimate exit —
  the new-chat handoff where **the user** picks the model. The orchestrator may pass a model **only if
  it comes from the environment configuration**. 006-003 supplies the family-comparison script;
  006-002 does not implement it.
- **D-4 (=d).** Transport equivalence in `re-entry.md`, linked from §4 and from each `delegation`
  section (PD-5).
- **D-5 (=e).** The four context rules live in `sources/roles/orchestrator.md`, with
  `references/orientation.md` §1 as the owner of "view first" (PD-6).
- **D-6 (=f).** The model-family column and the profiles paragraph leave `SKILL.md`; F001 is
  reformulated, not deleted. `install.sh`, `scripts/cdad-models.sh` and ADR-007 are **not** touched
  (they belong to 006-003).
- **D-7.** **Risk 2 (the consumer)** — its handoff still prescribes the adapter
  (`execution.md:112-118`). Declared **at closure**; out of scope.

## 5. Unknowns (VERIFY)

- **VERIFY-1.** Whether the installed OpenCode accepts a per-call `model` parameter on the native
  dispatch tool. Repo evidence says the model is per-agent configuration
  (`opencode-delegation.md:28-35`). **Do not assert the contrary.** Resolution: inspect the tool
  schema in an isolated installation and record the observation.
- **VERIFY-2.** Whether `delegate` is still a dead channel in the installed version (evidence from a
  prior deploy, `opencode-delegation.md:99-105`). The rule must **not** depend on it: the native
  mechanism is `task`. Resolution: record the observation; the rule holds either way.
- **VERIFY-3.** **Resolved by D-3** — the orchestrator passes the configured value, never invents it.
- **VERIFY-4.** The exact impact on the 6 coupled test modules. Resolution: read each assertion while
  writing the plan and adjust the `CONSUMER` pointer or the assertion in the **same diff** as the text
  move (plan U7).

## 6. Out of scope

- The consumer's handoff and config (its owner updates them).
- **006-003:** installer always `basic`, delegation-config template, server credential, family
  comparison script; `install.sh`, `scripts/cdad-models.sh`, ADR-007.
- **006-004:** active-decisions table.
- New runtimes and a Claude Code CLI adapter (does not exist; 005-004 left it as an increment).
- OpenCode CLI adapter behaviour (006-001 closed).

## 7. Acceptance mapping

| AC (discovery §3) | Postcondition |
|---|---|
| AC-006-002-1 | PD-1 |
| AC-006-002-2 | PD-2 |
| AC-006-002-3 | PD-3 |
| AC-006-002-4 | PD-4 (+ acceptance unit U8) |
| AC-006-002-5 | PD-5 |
| AC-006-002-6 | PD-6 |
| AC-006-002-7 | PD-7 |
| AC-006-002-8 | PD-8 |
| (decisions a, f) | PD-9, PD-10, PD-11 |

- **VERIFY-5 (added at approval).** How the acceptance run isolates the generated agents for OpenCode without touching HOME (plan amendment A-2). Unresolved → U8 closes blocked by environment.

Status: Approved by orquestador Claude (HITL delegada epic-006) on 2026-10-17; VERIFY-4 is resolved by plan amendment A-1 (coupled assertions move in each unit's RED, never in GREEN).

## Enmienda 001 — regla 4 de contexto (dueño, 2026-10-17)

El «nunca `/tmp`» venía de una configuración de seguridad del SO que aislaba `/tmp` por proceso; el dueño la quitó y pidió relativizar la regla. **PD-6 regla (4)** e **INV-4** quedan así: `/tmp` se admite para borradores efímeros de un mismo proceso; lo que debe durar, dejar evidencia o leerlo otro proceso o rol va a rutas estables del workspace (`.cdad/inbox` para el recibo; el workspace declarado para lo demás), porque `/tmp` se limpia y no deja evidencia. El oráculo de ausencia de `/tmp` deja de prohibir toda mención: prohíbe instrucciones que usen `/tmp` como canal entre procesos o roles, o como lugar de un artefacto, recibo o evidencia.

Status: enmienda 001 approved by Pablo on 2026-10-17 (pedido explícito del dueño).
