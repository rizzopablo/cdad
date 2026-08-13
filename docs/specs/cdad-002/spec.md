# CDAD-002: Validation Spike — Claude Code Sub-agents

**Status:** Planning  
**Feature ID:** cdad-002-validate-claude-code-subagents  
**Spike Type:** Validation of ADR-008 implementation (CDAD Claude Code support)  

---

## Executive Summary

CDAD-002 is NOT a real feature; it is a validation spike that exercises all 5 CDAD roles (architect, test-writer, implementer, reviewer, scribe) with a trivial mini-feature to verify:

1. ✅ Sub-agents install correctly via `install.sh`
2. ✅ Agent spawning via `Agent` tool works (no spawn recursion)
3. ✅ State-passing (agents receive context without parent session bleed-through)
4. ✅ Path-scoping guards work (hooks block intended paths)
5. ✅ Model routing by profile works (`cdad_model_claude`)
6. ✅ Artefacts produced per stage + materialized correctly
7. ✅ No hidden issues with Claude Code vs OpenCode differences

**Acceptance Criteria:** 5/5 CDAD stages completed (Discovery → Specification → TDD → Review → Merge+Memory), all artefacts produced, no blockers in agent execution, validation findings documented in `findings/validation-cdad-002.md`.

---

## Discovery Phase — Landscape

### The Mini-Feature

**Feature:** "Calculator add function" — trivially simple on purpose.

A new public function `Add(a int, b int) -> int` that returns the sum of two integers.

**Why this feature?**
- Small enough to complete all 5 CDAD stages in a single validation run (not a real deployment).
- Complex enough to exercise all role responsibilities:
  - **Architect**: brainstorm options (trivial, but exercises Discovery).
  - **Test-writer AUDIT**: identify existing calc tests if any (likely none).
  - **Test-writer RED**: write a test that verifies `Add(2, 3) == 5` (fails, no impl).
  - **Implementer**: implement `func Add(a, b int) int { return a + b }` (trivial, passes test).
  - **Reviewer**: audit against spec (5 ejes, should find nothing wrong, but verifies review flow).
  - **Scribe**: draft Memory Bank update (capture the spike validation itself as a lesson learned).

### Codebase Landscape

**Target language:** Go (existing CDAD test project in this repo uses Go).  
**Package location:** `pkg/calc/` (new package).  
**Test location:** `pkg/calc/calc_test.go` (new).  

**Existing code:**
- Already has Go test framework (Go built-in).
- Repo has `Makefile` with test target: `make test`.
- Repo already has GitHub Actions CI (will run tests post-merge, separate from this spike).

---

## Specification — Postconditions

| ID | Postcondition | Observable |
|----|---|---|
| P1 | `Add` function exists in `pkg/calc` | `go test ./pkg/calc -run TestAdd` passes |
| P2 | `Add(2, 3)` returns `5` | Test `TestAdd_basic` passes |
| P3 | `Add` is a public function (capitalized) | `pkg/calc.Add` is callable from outside the package |
| P4 | No panics on valid inputs (2 integers) | Test `TestAdd_no_panic` passes |

**No coverage requirements.** No performance benchmarks. No edge-case tests for this spike (that's hardening, a separate phase). Just the postconditions above.

---

## TDD Anti-Trampa — Test Strategy

### AUDIT (existing tests)

Expect: zero existing `Add`-related tests (new function).

### RED (new tests)

```go
func TestAdd_basic(t *testing.T) {
  result := Add(2, 3)
  if result != 5 {
    t.Errorf("Add(2, 3) = %d, want 5", result)
  }
}

func TestAdd_no_panic(t *testing.T) {
  defer func() {
    if r := recover(); r != nil {
      t.Errorf("Add(2, 3) panicked: %v", r)
    }
  }()
  Add(2, 3)
}
```

### GREEN (implementation)

```go
package calc

// Add returns the sum of two integers.
func Add(a, b int) int {
  return a + b
}
```

### REFACTOR (optional)

No refactoring needed (2-line function, trivial).

---

## Review Criteria (5 Ejes)

### Eje 1: Correctness

- ✅ P1-P4 all implemented.
- ✅ No feature creep.

### Eje 2: Robustness

- ✅ No panics on valid inputs.
- ✅ No error handling needed (simple addition).

### Eje 3: Maintainability

- ✅ Clear function name, 1 line of logic.
- ✅ Function properly exported (capitalized).

### Eje 4: Testability

- ✅ Tests are behavioral (verify postconditions), not structural.

### Eje 5: Performance

- ✅ No SLO in spec, so N/A.

**Expected Review Result:** No CRITICAL or MAJOR findings (spike is intentionally trivial).

---

## Memory Bank — Lessons Learned

This spike's artefact is the validation process itself. The Memory Bank entry documents:

1. **Agents installed and working**: which agents were invoked, which profiles tested.
2. **State-passing verified**: agents received correct context; no parent bleed-through.
3. **Path-scoping verified**: test-writer couldn't read `src/`; implementer couldn't write to `tests/`.
4. **Model routing verified**: each agent had the correct model per profile.
5. **Artefact flow verified**: spec → tests → implementation → review → memory.
6. **Validation findings**: fricciones, timeouts, hook behavior, actual vs. declared.

**Entry template:**
```
## Spike CDAD-002: Claude Code Validation

**Date:** 2026-08-13  
**Profiles tested:** optimus (primary)  
**Agents spawned:** 5/5 (architect, test-writer, implementer, reviewer, scribe)  

### Lessons Learned

- [Lesson 1 from spike]
- [Lesson 2 from spike]
- ...

### Frictions Discovered

- [Friction 1: agent behavior vs. expected]
- [Friction 2: hook behavior, timing, etc.]

### Validation Result

- **Overall:** PASS / FAIL
- **Blocker findings:** [list]
- **Non-blocker findings:** [list]
```

---

## Next Phase (post-spike)

Once CDAD-002 completes:

1. Validation findings documented in `findings/validation-cdad-002.md`.
2. If blockers found: fix agents/guards/install.sh, re-validate.
3. If clear: mark ADR-008 as "Verified" in `task_plan.md` (Phase 7).
4. Optional: extend `install.sh` to ask which runtime(s) to install (OpenCode-only, Claude Code-only, both).

---

## Validation Spike Checklist (Manual Steps)

**Prerequisites:**
- [ ] Agents installed: `bash cdad/install.sh --dry-run --optimus`
- [ ] Guard script present: `~/.claude/cdad-scripts/path-guard.sh` exists and is +x
- [ ] Claude Code CLI available: `claude --version`

**Stage 1 (Discovery):**
- [ ] Invoke `cdad-cycle` skill (in Claude Code session)
- [ ] Detect no existing `pkg/calc/` (fresh feature)
- [ ] Spawn `cdad-architect` subagent with Discovery prompt
- [ ] Architect produces brainstorm + spec draft
- [ ] User approves spec (simulated: "looks good")

**Stage 2 (Specification):**
- [ ] Orchestrator refines spec (optional, should be ready from stage 1)
- [ ] Spec approved and finalized

**Stage 3.0 (TDD AUDIT):**
- [ ] Spawn `cdad-test-writer` with AUDIT substage prompt
- [ ] Test-writer audits `pkg/calc/` (expects zero `Add`-related tests)
- [ ] Test-writer produces test-audit.md

**Stage 3.1 (TDD RED):**
- [ ] Spawn `cdad-test-writer` with RED substage prompt
- [ ] Test-writer writes failing test (TestAdd_basic + TestAdd_no_panic)
- [ ] Tests run and fail (AssertionError: expected 5, got <nil>)
- [ ] Tests committed

**Stage 3.2 (TDD GREEN):**
- [ ] Spawn `cdad-implementer` with GREEN substage prompt
- [ ] Implementer writes `Add` function
- [ ] Suite runs fully green
- [ ] Implementation committed

**Stage 4 (Review):**
- [ ] Spawn `cdad-reviewer` subagent
- [ ] Reviewer audits (5 ejes, expects no blockers given trivial feature)
- [ ] Reviewer produces review.md (likely "PASS, no CRITICAL/MAJOR")

**Stage 5 (Memory Bank):**
- [ ] Spawn `cdad-scribe` subagent
- [ ] Scribe drafts Memory Bank update (capture what this validation learned)
- [ ] User approves memory entry
- [ ] Orchestrator commits memory update

**Verification:**
- [ ] All 5 stages completed
- [ ] All artefacts produced (spec, test-audit, tests, implementation, review, memory)
- [ ] No re-spawning from subagents (GUARDIA DE SPAWN respected)
- [ ] Path-scoping honored (hook attempts logged if any)
- [ ] Findings documented in `findings/validation-cdad-002.md`

---

## Post-Spike Cleanup

After validation, revert the mini-feature:

```bash
git reset --hard HEAD~N  # N = number of commits during spike
```

(This keeps the validation findings + Memory Bank entry but removes the feature code itself.)

Alternatively, leave it in the repo as a permanent "hello-world" test of CDAD.
