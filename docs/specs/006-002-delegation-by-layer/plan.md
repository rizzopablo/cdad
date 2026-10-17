# Plan — `006-002-delegation-by-layer`

Spec: `docs/specs/006-002-delegation-by-layer/spec.md` (this feature, draft).
Contract: epic plan §8/§9, `sha256 = b6a59502…f2e63`.

**Full-suite policy:** the complete suite is **not** run per unit — the closer runs it once at
closure (declared in the packet's common part; not restated here).

**Coupled regressions (discovery §1.5 — run focally in every unit that touches their surface):**
1. `tests/test_005_004_t1_dispatch_tool_name.py` — paths of the two runtime references (`:62-64`)
2. `tests/test_005_004_t4_cc_guard_decisions.py` — `claude-code-delegation.md` as `CONSUMER` (`:95`)
3. `tests/test_005_005_t3_provenance.py` — `opencode-delegation.md` documents reload/provenance (`:61`)
4. `tests/test_005_009_t3_spawn_reconciliation.py` — spawn-ban conservation (`:231-264, 485-500`)
5. `tests/test_005_010_t3_references.py` — content of `cli-delegation.md`/`opencode-delegation.md` (`:67-114`)
6. `tests/validate-consistency.sh` — F004 table (`:132-136`), F010 M6 (`:227-232`), F001 (`:260-268`)

## Units

| # | Unit | Depends on | Gate |
|---|---|---|---|
| **U1** | Adapter `delegation` sections + generator composition | — | staging `basic` emits the section in both runtimes |
| **U2** | Neutral §4 + de-runtimization of the skill | — | PD-1/PD-3 text tests green |
| **U3** | Withdraw the two runtime references → `docs/` | U1 | PD-9 asserts green; F004 reformulated |
| **U4** | `SKILL.md` §2 without models; F001 reformulated | — | PD-11 + F001 green |
| **U5** | Transport equivalence in `re-entry.md` + links | U1, U2 | PD-5 green |
| **U6** | The 4 context rules in the orchestrator source | — | PD-6 green |
| **U7** | Update the coupled tests **in the same diff** as the text move | U2, U3, U4, U5 | all 6 coupled modules green |
| **U8** | Acceptance: bounded real AC-4 run | U1–U7 | PD-4 behavioural evidence, or declared blocked |

### U1 — Adapter `delegation` sections + generator composition
- **Files:** `sources/agents/adapters/opencode.md`, `sources/agents/adapters/claude-code.md`,
  `scripts/cdad-generate.py` (`compose_orchestrator_agent:749-870`; remove the hardcoded block
  `:812-828`), regenerated `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`.
- **Content:** each section declares the native mechanism, `subagent_type: cdad-<role>`, the
  role→subagent mapping, the byte-identical packet pass, the intra-runtime adapter prohibition, the
  three-part family declaration (D-3), and the link to PD-5.
- **RED tests (new, fixing PD-2 + PD-4 text part):** staging `PROFILE=basic` text asserts
  (a) `task` + `subagent_type` in OpenCode; (b) `Agent` + `subagent_type` in Claude Code;
  (c) neither requires the adapter; (d) the `basic` branch with "not guaranteed" + registration;
  (e) the intra-runtime adapter prohibition.
- **Regressions:** `test_cdad_generate.py`, #1, #4, `validate-consistency.sh`.
- **Gate:** `make staging PROFILE=basic` + the new text tests green.

### U2 — Neutral §4 + de-runtimization of the skill
- **Files:** `skills/cdad-cycle/SKILL.md` (§4 `:134-173`; §2 preamble `:42-46`; mode-B
  recommendation `:243`; step 4 `:263-275`; reference table `:462-466`; multi-env `:497-504`),
  `references/handoff-prompts.md` (`:36-49, 86-91`), `references/sub-agent-strategies.md`
  (`:11-55, 97-105, 131-166`), `references/progress-guards.md` (only under the adapter rule).
- **RED tests (PD-1, PD-3):** absence oracle + concept test over §4.
- **Regressions:** #1, #4, #5, `validate-consistency.sh`.
- **Gate:** PD-1/PD-3 green; §4 keeps the seven points.

### U3 — Withdraw the two runtime references
- **Files:** delete `references/opencode-delegation.md`, `references/claude-code-delegation.md`;
  add their historical detail under `docs/**` (non-installable); update the reference table
  `SKILL.md:447-473`.
- **RED tests (PD-9):** absence of the files in `skills/**`; existence of the preserved detail under
  `docs/**`; F004 no longer requires the CC row.
- **Regressions:** #1, #2, #3, #4, #5, `validate-consistency.sh` (F004/F010).
- **Gate:** PD-9 green; no dangling pointer in `SKILL.md`.

### U4 — `SKILL.md` §2 without models
- **Files:** `SKILL.md:67-77`, `references/handoff-prompts.md:515`,
  `tests/validate-consistency.sh:260-268` (F001 reformulated).
- **RED tests (PD-11):** absence of the model column/profiles paragraph and of the concrete model
  example; F001 asserts the new sentence.
- **Regressions:** #5, `validate-consistency.sh`.
- **Gate:** PD-11 + F001 green.

### U5 — Transport equivalence in `re-entry.md`
- **Files:** `references/re-entry.md` (new subsection after `:14-68`); links from §4 and from each
  `delegation` section.
- **RED tests (PD-5):** the subsection exists; both link sources exist; the existing `receive` unit
  test stays green.
- **Regressions:** `tests/test_003_002_t1_receive.py`, `tests/test_004_003_t5_reentry_equivalence.py`.
- **Gate:** PD-5 green.

### U6 — The 4 context rules
- **Files:** `sources/roles/orchestrator.md` (directive section, `:18-150`; the 4 rules; cite
  `orientation.md` §1), `references/orientation.md` §1 (owner of "view first", cites rotation),
  `SKILL.md` (one sentence referring to them, no duplication).
- **RED tests (PD-6):** text test over staging `basic` for the 4 concepts + `/tmp` absence grep.
- **Regressions:** `validate-consistency.sh`; `test_005_009_t3_spawn_reconciliation.py` (#4).
- **Gate:** PD-6 green.

### U7 — Coupled tests updated **in the same diff**
- **Files:** the 6 modules of §1.5 — repoint `CONSUMER`/paths to the new owner or reformulate the
  assertion, never delete coverage.
- **Dependency rule:** lands **atomically** with U2–U5 (same diff/commit); otherwise PD-7 is
  unreachable.
- **RED tests:** the reformulated asserts fail against the old tree, pass against the new one.
- **Gate:** the 6 modules + `make validate` green.

### U8 — Acceptance: bounded real AC-4 run
1. `make staging PROFILE=basic && bash install.sh --basic` with **redirected root**
   (`CDAD_INSTALL_ROOT=<throwaway dir>`, pattern of `tests/test_005_008_t3_acceptance.py:160-180`) —
   **never HOME**.
2. `cdad_packet.py prepare` for a reviewer packet on a throwaway feature.
3. One-line commission to the OpenCode orchestrator: "dispatch the reviewer of this packet", **one
   task**.
4. **Required transcript evidence:** one native dispatch call with `subagent_type: cdad-reviewer`;
   **zero** invocations of the CLI adapter or a shell `run`; the reviewer's FINAL TEXT staged under
   `.cdad/inbox` and `receive` with a `pending` receipt.
5. **Environment blocking rule:** if the provider does not respond (precedent
   `execution.md:168-170`), the run is declared **blocked by environment** and is **not** replaced by
   a text test presented as behaviour.

## Unit size and gates
Each unit is one reviewable diff, one dispatchable role task. No unit spans two sub-phases. The
acceptance unit is the only one requiring an operational run, and it is the only one that can close
as **blocked** without invalidating PD-1…PD-11 (all of which are text-observable).

## Approval amendments (orchestrator, delegated HITL, 2026-10-17)

- **A-1 — U7 is folded into the units.** Tests belong to the test-writer and text to the implementer, so "the same diff" is not possible. Each unit's RED reformulates the coupled assertions of its own surface (from the list above) so that they fail against the old tree; its GREEN moves the text without touching `tests/`. `tests/validate-consistency.sh` (F001, F004, F010) is a test: it changes only in a RED. U7 no longer exists as a unit; the dependency of U8 on U7 becomes a dependency on U1–U6.
- **A-2 — U8 isolation (VERIFY-5).** A redirected install root is not enough: OpenCode reads agents from the user configuration and from the project. Before the run, U8 records how the throwaway project gets the generated agents (project-level agents directory or an isolated configuration root) without touching HOME and keeping the owner's provider configuration read-only. If isolation cannot be achieved, U8 closes **blocked by environment**, as its rule already says.

Status: Approved by orquestador Claude (HITL delegada epic-006) on 2026-10-17, with amendments A-1 and A-2.
