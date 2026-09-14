# Contract-Driven AI Development (CDAD)

**A disciplined methodology for building software with AI agents**

---

## About this document

This document teaches a software development methodology designed specifically for working with artificial intelligence agents as implementers. The methodology is called **Contract-Driven AI Development** (CDAD).

CDAD starts from an uncomfortable observation: language models are brilliant but inconsistent. They can generate excellent code or defective code, and the difference is often not predictable. If you let an agent work without constraints —the pattern known as *vibe coding*— you will get results ranging from amazing to catastrophic. CDAD proposes an answer: introduce structural barriers (explicit specs, verifiable contracts, separation of phases into sub-agents with limited permissions, automated contract tests) that *force* the result to be correct, regardless of the consistency of the underlying model.

The document is organized into thirteen chapters. The first three are conceptual: why CDAD exists, its foundational principles, and a comparison with alternatives. Chapters four through nine are operational: how each phase of the cycle is executed, step by step, with concrete examples. Chapters ten through twelve go deeper into specific aspects: tool configuration, adaptation to opinionated frameworks, anti-patterns to avoid. Chapter thirteen is reference: glossary, checklist, resources.

**How to read this document.** If you have never worked with AI agents seriously, read it linearly. If you already have experience and want only the method, you can jump to chapter four and come back when something does not fit. The boxes marked as **For advanced readers** offer additional technical depth on specific topics; you can skip them on a first read without losing the thread.

**What you need to know to make the most of it.** We assume you know how to program in some modern language (Python, JavaScript, Java, Go, Rust, whatever it is), that you understand what Git and a unit test are, and that you have some exposure to generative AI tools for code. You do not need to have used an AI agent in a structured way before; that is exactly what you are going to learn here.

---

## Table of contents

1. [Why CDAD exists](#1-why-cdad-exists)  
2. [The five foundational principles](#2-the-five-foundational-principles)  
3. [CDAD compared with alternatives](#3-cdad-compared-with-alternatives)  
4. [The cycle: an overview](#4-the-cycle-an-overview)  
5. [Stage 1 — Discovery](#5-stage-1--discovery)  
6. [Stage 2 — Specification](#6-stage-2--specification)  
7. [Stage 3 — Anti-gaming TDD with isolated sessions](#7-stage-3--anti-gaming-tdd-with-isolated-sessions)  
8. [Stage 4 — Two-layer review](#8-stage-4--two-layer-review)  
9. [Stage 5 — Merge and Memory Bank](#9-stage-5--merge-and-memory-bank)  
10. [Tool configuration](#10-tool-configuration)  
11. [CDAD in opinionated frameworks](#11-cdad-in-opinionated-frameworks)  
12. [Documented anti-patterns](#12-documented-anti-patterns)  
13. [Quick reference and glossary](#13-quick-reference-and-glossary)

---

## 1\. Why CDAD exists

### 1.1 The problem of unconstrained AI agents

Let's work on a concrete scenario. Imagine you ask an AI agent: *"Implement a function that parses dates in ISO 8601 format and returns a datetime object, handling the typical cases."*

In the best scenario, the agent returns something correct: a robust function, with timezone handling, input validation, clear error messages, and tests covering typical and edge cases. In the worst scenario —and this is the one most people experience more often than they admit— the agent returns something plausible but defective: a function that works for the obvious cases, silently fails when the input includes a non-standard timezone, does not handle microseconds correctly, and the tests it writes are the ones that pass for its own implementation, not the ones that verify the real spec.

The problem is not that the model is bad. The problem is structural: when you give an agent the freedom to do everything (understand the problem, decide what to do, write tests, write code, validate), the agent optimizes for *internal coherence* (that its test passes for its code) instead of *external correctness* (that the code solves the real problem).

**Why this happens**

Language models are trained to generate plausible continuations of the text they see. If their context contains both the test they must satisfy and the code they are writing, they naturally tend to align both: they adjust the code so the test passes, or mentally adjust the test to be what their code will satisfy. It is the lowest-energy option in the space of possibilities. This is not a defect of specific models; it is an emergent property of the generation paradigm.

### 1.2 The intuitive answer (which does not work)

The intuitive answer to the problem is: *"have the human carefully review everything before accepting it."* This answer has three serious problems.

First, the human gets tired. After reviewing diffs of hundreds of lines for hours, attention decays and errors slip in. Review fatigue is a real and well-documented phenomenon.

Second, the human is not necessarily better than the agent at detecting subtle errors. If the code is well structured and the tests pass, a tired or rushed human reviewer will approve it even if it has subtle bugs that only manifest in production.

Third, the human bottleneck eliminates the main benefit of using agents: speed. If every line of code requires careful human review, you end up working slower than if you had coded it alone.

CDAD proposes a different answer: instead of relying on post-hoc human review, **insert structural barriers before and during** the implementation process. These barriers are automated, do not require sustained human attention, and *force* the result to have certain verifiable properties. The human still intervenes at key moments (spec approval, validation of the review's prioritization, architectural decisions), but is not the main guardian of quality.

### 1.3 The central idea of CDAD

The central idea of CDAD can be summarized in one sentence: **the agent must never be the only one responsible for verifying that its work is correct.**

This idea materializes in five structural principles that we will see in detail in the next chapter, but which in general terms are: specify with verifiable contracts before coding, separate the phases of the work into sub-agents with limited permissions, write the test before the code (for real, not as a ritual), validate the implementation against the contract (not against the test the same agent wrote), and maintain a persistent memory of the project that survives individual sessions.

flowchart LR

    A\[Working idea\] \--\> B\[Spec with\<br/\>verifiable contract\]

    B \--\> C\[Test written\<br/\>in isolated session\]

    C \--\> D\[Implementation\<br/\>in isolated session\]

    D \--\> E\[Review\<br/\>two-layer\]

    E \--\> F\[Merge with\<br/\>contract tests\]

    F \--\> G\[Memory Bank\<br/\>updated\]

    G \-.next feature.-\> A

Each arrow in this diagram is a *structural barrier*. The agent that writes the test does not see the code. The agent that implements does not see the reasoning of the one who wrote the test. The reviewer uses a different model from the implementer to have an independent perspective. The parameterized contract tests automatically verify that any implementation satisfies the contract's postconditions, not just the particular case the agent tried. And the Memory Bank captures learnings so the next session starts with context.

### 1.4 When CDAD is worth it

Before moving on, it is worth clarifying that CDAD is not for everything. The methodology has an operational cost: it requires discipline, documentation, tool configuration, and more agent sessions than a free-form workflow. For small and disposable tasks —a one-off data migration script, an exploratory experiment, a proof of concept that will be thrown away in a week— the discipline of CDAD is overkill.

CDAD is worth it when at least two of the following conditions hold:

- The code will live a long time (months or years), will evolve, and others will read and modify it later.  
- The correctness of the code matters beyond "it compiles and passes tests": there are economic, security, reputation, or regulatory consequences if it fails.  
- The project is large enough that no human can keep all the context in their head.  
- The team working on the project will use AI agents as a regular part of the workflow, not as an occasional tool.  
- Quality must be sustainable: it is not just "it works today" but "it remains maintainable six months from now when I come back to this code."

**Observable activation matrix.** The list above is a good intuitive filter, but when you are in the day-to-day and need to decide quickly whether a concrete task justifies the overhead, it helps to have a more operational criterion. The following matrix scores the task on three axes and suggests what level of CDAD to apply:

| Axis | Low (1) | Medium (2) | High (3) |
| :---- | :---- | :---- | :---- |
| **Expected lifespan of the code** | \< 1 month (one-off script, spike) | 1–12 months (single-project module) | \> 12 months (product core, shared infrastructure) |
| **Cost of a bug in production** | Cosmetic (non-critical UI, badly formatted log) | Operational (manual rework, friction for the user) | Economic/legal (direct monetary loss, corrupted data, regulatory exposure) |
| **Probability of evolution** | Stable (will not be touched) | Minor changes expected | Major changes expected (several developers, several features on top) |

You add up the scores (range 3–9) and apply the following criterion:

| Score | Recommended mode | What gets applied |
| :---- | :---- | :---- |
| 3–4 | **Vibe coding** | You ask for what you need, review the result, use it. No spec, no isolated sessions. |
| 5–6 | **CDAD light** | Brief spec (one paragraph \+ acceptance criteria), TDD with isolated sessions for the critical components only, optional review. Memory Bank if the project already has one. |
| 7–9 | **Full CDAD** | The five stages as described in the document, no shortcuts. |

**How to use the matrix.** It is not for pulling out the form and scoring every five-minute task; it is for the cases where you have doubts. If a task clearly falls into "it's an exploratory experiment" or clearly into "it's the core we maintain for five years", the matrix adds nothing. It adds value when the task is in the gray zone: a script you thought you would throw away but the client liked and it stayed in production, an integration with an external service that seems simple but touches a critical flow, a bug fix that starts small and reveals structural problems. In those cases, scoring the three axes gives you a defense when someone asks you "why so much process for this?" or "why so little process for this?".

**Defense against external pressure.** The matrix also serves for conversations with clients, project managers, or yourself in rushed mode. If a PM pushes for fast delivery and the task scores 8/9 on the matrix, you have a concrete argument for not skipping the process: the cost of a bug in production far exceeds the cost of a careful iteration. Conversely, if you tend to over-engineer and the task scores 4/9, the matrix is the reminder that full CDAD would be over-engineering.

**Self-assessment quiz**

1. Why does an agent that writes the test and the implementation in the same session tend to produce weak tests?  
2. What is the difference between relying on post-hoc human review and relying on pre-hoc structural barriers?  
3. In what kind of projects is it NOT advisable to use CDAD?

View answers 

1. Because the agent optimizes for internal coherence (that its test passes for its code) instead of external correctness (that the code solves the real problem). Since the agent sees both at the same time, it naturally aligns them with each other, losing the property that the test verifies the spec independently of the implementation.  
     
2. Post-hoc human review depends on sustained attention that gets tired, on judgment that can fail under pressure, and becomes a bottleneck. Pre-hoc structural barriers are automated (explicit specs, contract tests, import-linter, isolated sessions with limited permissions), do not require sustained human attention to function, and are consistent on every run.  
     
3. In small, disposable, exploratory tasks, or where correctness has no serious consequences. For example: a one-off migration script, an experiment that will be thrown away, a quick proof of concept. The discipline of CDAD adds overhead that is only justified when the code will live a long time, evolve, or have serious consequences if it fails.

---

## 2\. The five foundational principles

CDAD rests on five principles that, together, form the backbone of the methodology. Each one responds to a specific failure of the "let the agent work freely" paradigm. In this chapter we explore them in detail, with the justification of why each one exists.

### 2.1 Principle 1 — Spec before code (always)

**The principle.** Before any agent touches a single line of implementation code, there must exist a written document that defines what the feature does, with verifiable contracts and acceptance criteria.

**Why.** The act of writing a spec before coding fulfills three distinct functions that are often confused. First function: *force the formalization of the requirement*. When you try to write what a function must do with enough precision for another person (or an agent) to implement it correctly, you discover ambiguities that your original intuition had not detected. Second function: *create a human approval point before the expensive work*. The spec is the moment where you validate that you understood the problem and that the agent understood the problem, before spending time and tokens implementing the wrong thing. Third function: *establish the oracle of truth against which the implementation will be verified*. The test does not verify that the code compiles; it verifies that the code satisfies the spec's postconditions.

**What a spec includes in CDAD.** A minimal spec has four sections:

\# Spec: ISO 8601 date parsing

\#\# Functional description

Function that receives a string in ISO 8601 format and returns a native

datetime object of the language, with explicit timezone.

\#\# Contract (signature and invariants)

Function: parse\_iso\_date(s: str) \-\> DateTime

Postconditions:

1\. If s is a valid ISO 8601 string, it returns the corresponding DateTime.

2\. If s is not valid, it raises InvalidDateError with a descriptive message.

3\. The preserved precision is at least down to milliseconds.

4\. If s has a timezone offset (e.g. "+05:30"), the resulting DateTime reflects that offset.

5\. If s has no timezone, the resulting DateTime is explicit UTC.

6\. The function is pure: it has no side effects.

\#\# Verifiable invariants (they will become property tests)

\- ∀s valid: parse\_iso\_date(s).to\_iso\_string() is valid ISO 8601

\- ∀s valid: parse\_iso\_date(s) is deterministic (same input → same output)

\#\# Acceptance criteria

\- Unit test for each case of each postcondition passes

\- Property test with 1000 random strings passes

\- Line coverage in the solver's file ≥95%

\#\# Out of scope (what it does NOT do)

\- Does not parse non-standard formats like "MM/DD/YYYY"

\- Does not infer timezones from context

**Variant: lighter spec for simple features.** For very small features (a one-off bug fix, a simple computed field), the spec can be one paragraph \+ one failing test. What matters is that *something written* exists before the code, not that it has a specific format.

**For advanced readers — Executable specs**

An advanced variant of the principle is to write specs in executable languages like Gherkin (Cucumber, behave), TLA+ (formal verification), or property-based test specifications (Hypothesis stateful). These specs do not only describe what the feature does; they *are* the verification that the feature does it. It is the ideal of the principle taken to the extreme. In practice, for most projects, well-written markdown specs \+ regular Python tests achieve 80% of the value at 20% of the maintenance cost.

### 2.2 Principle 2 — Verifiable contracts as guardian

**The principle.** Contracts between components must be defined as formal types (interfaces, protocols, traits, depending on the language) with explicit postconditions, and verified automatically by parameterized tests that iterate over all registered implementations.

**Why.** When there are multiple implementations of the same interface (several solvers for the same problem, several adapters for the same external service, several storage backends for the same model), the agent can satisfy the test of one implementation and break another without noticing. Parameterized contract tests are the safety net that detects this automatically: if the contract says "all implementations must satisfy postcondition X", and a parameterized test checks postcondition X against all registered implementations, adding a new implementation or modifying an existing one that breaks the postcondition is detected immediately in CI.

**Example in Python with typing.Protocol.**

\# interfaces/optimizer.py

from typing import Protocol, Sequence, runtime\_checkable

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)

class Item:

    id: str

    weight: float

    value: float

@dataclass(frozen=True, slots=True)

class Solution:

    selected\_items: Sequence\[str\]

    total\_value: float

    total\_weight: float

@runtime\_checkable

class IKnapsackSolver(Protocol):

    """Solver for the 0/1 knapsack problem.

    

    Contractual postconditions (verified by contract tests):

    1\. selected\_items ⊆ {item.id for item in items}

    2\. total\_weight ≤ capacity

    3\. total\_value \= sum(item.value for item.id in selected\_items)

    4\. If capacity ≥ sum(item.weight for item in items), 

       all items are selected

    5\. Determinism: same input → same output

    """

    name: str

    

    def solve(

        self, 

        items: Sequence\[Item\], 

        capacity: float,

        \*,

        timeout\_seconds: float \= 30.0,

    ) \-\> Solution: ...

\# tests/test\_contract\_solvers.py

import pytest

from interfaces.optimizer import IKnapsackSolver, Item

from algorithms.greedy\_solver import GreedySolver

from algorithms.dp\_solver import DynamicProgrammingSolver

from algorithms.milp\_solver import MILPSolver

\# Every time an implementation is added, it goes here

IMPLEMENTATIONS: list\[IKnapsackSolver\] \= \[

    GreedySolver(),

    DynamicProgrammingSolver(),

    MILPSolver(),

]

@pytest.fixture

def sample\_items():

    return \[

        Item(id="a", weight=2.0, value=3.0),

        Item(id="b", weight=3.0, value=4.0),

        Item(id="c", weight=4.0, value=5.0),

    \]

@pytest.mark.parametrize("solver", IMPLEMENTATIONS, ids=lambda s: s.name)

def test\_contract\_selected\_items\_subset(solver, sample\_items):

    """Postcondition 1: selected\_items ⊆ items"""

    solution \= solver.solve(sample\_items, capacity=5.0)

    item\_ids \= {item.id for item in sample\_items}

    assert all(sid in item\_ids for sid in solution.selected\_items)

@pytest.mark.parametrize("solver", IMPLEMENTATIONS, ids=lambda s: s.name)

def test\_contract\_capacity\_respected(solver, sample\_items):

    """Postcondition 2: total\_weight ≤ capacity"""

    solution \= solver.solve(sample\_items, capacity=5.0)

    assert solution.total\_weight \<= 5.0

@pytest.mark.parametrize("solver", IMPLEMENTATIONS, ids=lambda s: s.name)

def test\_contract\_total\_value\_consistent(solver, sample\_items):

    """Postcondition 3: total\_value is the correct sum"""

    solution \= solver.solve(sample\_items, capacity=5.0)

    expected \= sum(

        item.value for item in sample\_items 

        if item.id in solution.selected\_items

    )

    assert solution.total\_value \== pytest.approx(expected)

When an agent adds a fourth implementation (say `BranchAndBoundSolver`), it must register it in the `IMPLEMENTATIONS` list. Automatically, the parameterized contract test runs the three postconditions against it. If it breaks any, CI fails and the merge is blocked.

**Table: verifiable contracts in different languages**

| Language | Contract mechanism | Postcondition verification |
| :---- | :---- | :---- |
| Python | `typing.Protocol` with `@runtime_checkable` | parameterized pytest |
| TypeScript | `interface` \+ `satisfies` operator | jest with `describe.each` |
| Java | `interface` with default methods | JUnit 5 with `@ParameterizedTest` |
| Go | `interface` (structural typing) | tests with table-driven approach |
| Rust | `trait` with methods | `#[test]` with macros for parameterization |
| C\# | `interface` with `[Required]` | xUnit with `[Theory]` and `[MemberData]` |

**Why this is the real guardian of the architecture**

Without verifiable contracts, the guardian of consistency between implementations is the developer's discipline (which the agent does not have) or the reviewer's attention (which gets tired). Contract tests are automated discipline: they run on every PR, detect inconsistencies immediately, do not get tired, do not have a bad day. The cost of writing them once is hugely amortized because every new implementation is automatically covered.

### 2.3 Principle 3 — Isolated sessions with granular permissions

**The principle.** The different phases of the work (write test, write code, refactor, review) are executed in different sub-agents with different file permissions, in sessions that do not share context.

**Why.** Language models, when they see in their context both the test and the code they are implementing, naturally tend to align them with each other. This is the central problem we saw in chapter 1, expressed as an emergent property: the model optimizes internal coherence over external correctness. The only structural solution is that the agent that writes the test *does not see* the implementation code, and that the implementing agent *does not see the reasoning* of the one who wrote the test.

flowchart TB

    subgraph "Session 1: test-writer"

        S1A\[Reads spec ✓\]

        S1B\[Reads interface ✓\]

        S1C\[Does NOT read algorithms ✗\]

        S1D\[Does NOT read adapters ✗\]

        S1E\[Writes failing test\]

    end

    

    subgraph "Session 2: implementer"

        S2A\[Reads spec ✓\]

        S2B\[Reads interface ✓\]

        S2C\[Reads written test ✓\]

        S2D\[Does NOT read session 1 reasoning ✗\]

        S2E\[Writes passing code\]

    end

    

    subgraph "Session 3: refactorer"

        S3A\[Reads green code ✓\]

        S3B\[Reads full suite ✓\]

        S3C\[Refactors keeping tests green\]

    end

    

    subgraph "Session 4: reviewer"

        S4A\[Reads full diff ✓\]

        S4B\[Reads original spec ✓\]

        S4C\[Reads import-linter ✓\]

        S4D\[Generates prioritized report\]

    end

    

    S1E \--\> S2A

    S2E \--\> S3A

    S3C \--\> S4A

**How it materializes.** In modern tools like OpenCode, Claude Code, Cursor, and other agentic environments, this is done through *sub-agents* configured with granular permissions by glob patterns. For example:

// opencode.jsonc (simplified example)

{

  "agents": {

    "test-writer": {

      "permissions": {

        "edit": \["tests/\*\*"\],

        "read": \["docs/specs/\*\*", "interfaces/\*\*", "tests/\*\*"\],

        "deny\_edit": \["src/\*\*", "algorithms/\*\*", "adapters/\*\*"\]

      },

      "system\_prompt": "You write failing tests that verify the spec. You never write implementation code. After writing the test, exit so a different agent can implement."

    },

    "implementer": {

      "permissions": {

        "edit": \["src/\*\*", "algorithms/\*\*", "adapters/\*\*"\],

        "read": \["docs/specs/\*\*", "interfaces/\*\*", "tests/\*\*"\],

        "deny\_edit": \["tests/\*\*"\]

      },

      "system\_prompt": "You write the minimum code that makes the existing failing test pass. You never modify the test. You never add features the test does not require."

    }

  }

}

The operational rule is strict: the test-writer session ends before the implementer session starts, and the implementer does not receive the test-writer's thinking context. It only receives the spec, the interface, and the already-written test.

**Variant: manual fallback without formal sub-agents.** Many real environments do not have orchestrators with granular permissions by glob pattern. You work with a generic agentic IDE, a web chat interface with the model, or a tool that indexes the whole repo automatically. In those cases you cannot enforce the separation at the tool level, but you can simulate it with discipline and concrete techniques:

1. **Conversations separated by phase.** Each phase of the cycle (test-writer, implementer, refactorer, reviewer) starts in a new conversation, not in a continuation. You explicitly close the previous one before opening the next. Laziness here is the enemy: the temptation to "keep going in the same conversation because it already has the context loaded" breaks the principle.  
     
2. **Manual loading of minimal context.** Instead of letting the tool autocomplete with the whole repo, you explicitly pass the agent only the files that sub-agent should see. For the test-writer: the spec, the interface, the existing tests. For the implementer: the spec, the interface, the freshly written test. For the reviewer: the diff, the spec, the QA configuration files. Manual selection replaces the permission system.  
     
3. **Prompts of explicit "contextual blindness".** At the start of each session, you tell the agent something like: *"For this task you will act as test-writer. Do NOT read files in `src/` or `algorithms/`. If the tool shows you those files, ignore them. Your task is to write tests that verify the attached spec, not to validate that my implementation works."* It is ritual, yes, but modern models usually respect this kind of instruction when it is placed at the start.  
     
4. **Temporary repos or branches as a sandbox.** A stronger technique: you make a clone of the repo (or create a temporary branch with `.aiignore` or equivalent) where the files the sub-agent should not see *physically* do not exist. The test-writer works in a repo where only the spec, the interface, and the tests folder exist. When it finishes, you copy the test to the main repo and open the implementer session there. The cost is friction (maintaining two checkouts), but the isolation is real.  
     
5. **Explicit post-hoc verification.** When the test-writer session ends, before moving to the implementer, you manually verify that the test assumes nothing about the implementation. A useful question: *"Would this test still be valid if the code were completely rewritten with a different algorithm?"* If the answer is no, the test is coupled to a particular implementation and must be rewritten.

**When to choose each fallback level.** If your tool supports sub-agents with granular permissions (OpenCode, Claude Code, etc.), use them: it is the cleanest path. If it does not support them but does support multiple independent conversations, use techniques 1+2+3 combined. If you work with a single conversation that persists the whole project context (some agentic IDEs), your only real defense is technique 4 (temporary repos). In no case is it acceptable to skip the principle simply because "the tool does not make it easy for me": the consequence is going back to "one session for everything" mode with tests that do not detect bugs.

### 2.4 Principle 4 — TDD with the "Iron Law"

**The principle.** Implementation code is never written without first having a test that fails for the right reason. No exceptions, no shortcuts, no "I'll add the test later."

**Why.** This may sound like classic TDD (Test-Driven Development by Kent Beck), and it is. The difference is that in CDAD the rule is applied with extra rigor because the implementer is an agent, not a disciplined human. A human who skips the test can remember the spec and write correct code. An agent that skips the test has no oracle: it implements what the model "believes" the spec says, without verification.

The rule has three parts:

First, *the test must fail before the implementation*. It is not enough for the test to exist; it must run and fail. This verifies that the test is actually testing something. If a test passes before the implementation exists, something is wrong: either the test does not verify what it claims to verify, or the implementation already existed.

Second, *the test must fail for the right reason*. If the test fails because the module does not import, that does not count. If it fails because the method does not exist yet, that does not count. The test must fail because the behavior it verifies is not implemented, with a clear error message indicating what was expected and what was obtained.

Third, *the code that is written must be the minimum that makes the test pass*. If the test verifies the single-element case, the code must not already handle the multiple-element case. That functionality arrives when the test that verifies it arrives. This is called YAGNI ("You Aren't Gonna Need It") and is critical to keep the agent focused.

**Example of the cycle.** Let's go back to the date parser.

\# Session 1: test-writer writes the first test

\# tests/test\_parse\_iso\_date.py

import pytest

from src.date\_parser import parse\_iso\_date  \# Fails here: module does not exist

from datetime import datetime, timezone

def test\_parse\_simple\_date\_with\_z\_timezone():

    """Postcondition 1: valid ISO string with Z returns UTC."""

    result \= parse\_iso\_date("2026-04-29T15:30:00Z")

    assert result \== datetime(2026, 4, 29, 15, 30, 0, tzinfo=timezone.utc)

We run: `pytest tests/test_parse_iso_date.py`. It fails with `ModuleNotFoundError: No module named 'src.date_parser'`. That is not a valid failure yet: the module still needs to be created.

\# Session 1 continues: creates the file with a stub that fails for the right reason

\# src/date\_parser.py

def parse\_iso\_date(s: str):

    raise NotImplementedError("not yet")

We run again: now it fails with `NotImplementedError: not yet`. This is a valid failure. The test proves that `parse_iso_date` must return a specific datetime, and the current implementation does not do it.

\# Session 2: implementer writes the minimal code

\# src/date\_parser.py

from datetime import datetime, timezone

def parse\_iso\_date(s: str) \-\> datetime:

    if s.endswith("Z"):

        return datetime.fromisoformat(s\[:-1\]).replace(tzinfo=timezone.utc)

    raise NotImplementedError("only Z timezone supported in this iteration")

We run: `pytest tests/test_parse_iso_date.py`. It passes. Green.

Now the next test covers the explicit offset case:

def test\_parse\_date\_with\_explicit\_offset():

    """Postcondition 4: offset preserved in datetime."""

    result \= parse\_iso\_date("2026-04-29T15:30:00+05:30")

    expected\_tz \= timezone(timedelta(hours=5, minutes=30))

    assert result \== datetime(2026, 4, 29, 15, 30, 0, tzinfo=expected\_tz)

It fails with `NotImplementedError: only Z timezone supported`. The implementer extends the minimal code to satisfy this new test, without touching what already works. And so on, postcondition by postcondition.

**Comparative table: classic TDD vs CDAD anti-gaming TDD**

| Aspect | Classic TDD | Anti-gaming TDD (CDAD) |
| :---- | :---- | :---- |
| Who writes the test | The developer | Isolated test-writer sub-agent |
| Who writes the code | The same developer | Isolated implementer sub-agent |
| Shared information | The developer sees everything in their head | Each sub-agent sees only what it needs |
| Risk of "gaming" | Moderate (depends on discipline) | Low (structural) |
| Initial speed | Faster (a single "session") | Slower (context switches) |
| Resulting test quality | Variable | Consistently higher |

### 2.5 Principle 5 — Persistent Memory Bank

**The principle.** The project maintains a set of versioned files that capture the current state, the decisions made, the accumulated learnings, and the context that the next sessions of any agent need in order to start being productive.

**Why.** AI agents have no memory between sessions. Every time you start a new conversation, the agent starts from scratch. If nothing documents the state of the project, the agent either reinvents the wheel (inefficient) or assumes incorrect things based on general patterns that do not apply to your project (dangerous). The Memory Bank solves this: it is the first thing any agent reads when starting a session.

**Typical Memory Bank structure.**

docs/

├── projectbrief.md         \# What the project is, scope, constraints

├── systemPatterns.md       \# Consolidated technical patterns

├── activeContext.md        \# Current state: what is being worked on now

├── progress.md             \# Status of each feature (in progress, done, blocked)

├── adr/                    \# Architecture Decision Records

│   ├── 001-elegimos-X-en-vez-de-Y.md

│   └── 002-arquitectura-hexagonal.md

└── specs/                  \# Feature specs

    ├── 001-feature-A/

    │   ├── spec.md

    │   ├── plan.md

    │   └── tasks.md

    └── 002-feature-B/

        └── ...

**Difference between specs and ADRs.** Specs describe *what a feature does*: they live while the feature is in development, eventually converging into documentation of the feature. ADRs (Architecture Decision Records) describe *why we made* an architectural decision: they are immutable once accepted. If the decision is later revisited, a new ADR is created that supersedes the previous one, but the original ADR remains as history.

**Example ADR.**

\# ADR-003: Using PostgreSQL instead of MongoDB

\*\*Status:\*\* Accepted  

\*\*Date:\*\* 2026-03-15  

\#\# Context

We need persistence for \[...\]. The options considered are

PostgreSQL, MongoDB, and SQLite.

\#\# Options considered

\#\#\# Option A: PostgreSQL

\- Pros: strong ACID, mature SQL queries, rich ecosystem, \[...\]

\- Cons: Requires explicit schema setup, \[...\]

\#\#\# Option B: MongoDB

\- Pros: Flexible schema, native horizontal scaling, \[...\]

\- Cons: weak ACID, less expressive queries, \[...\]

\#\#\# Option C: SQLite

\- Pros: Zero config, embedded, \[...\]

\- Cons: Limited concurrency, \[...\]

\#\# Decision

PostgreSQL.

\#\# Reasons

1\. Strong ACID is critical for our financial use cases.

2\. The team already has experience with SQL.

3\. The queries we need to run (complex joins) are native in SQL.

\#\# Consequences

\- We need to define the schema explicitly with migrations.

\- Operational cost of maintaining a Postgres in production.

\- Benefit of being able to use mature SQL tooling.

**How the agent uses the Memory Bank.** In each new session, the agent's first action should be to read (in order) `projectbrief.md` to understand the general context, `systemPatterns.md` to learn the technical conventions, `activeContext.md` to know what is being worked on now, and the ADRs relevant to the feature. After completing the feature, the agent (or you, validating) updates `activeContext.md` and `progress.md` before closing the session.

**Self-assessment quiz**

1. Why are parameterized contract tests more reliable than hand-written tests for each implementation?  
2. If a test passes before the implementation is written, what is wrong?  
3. What is the difference between a spec and an ADR?

View answers 

1. Because parameterized contract tests automatically verify that *all* registered implementations satisfy the postconditions, not just one particular one. When you add a new implementation, it is automatically covered without writing additional tests. Hand-written tests for each implementation can be forgotten or become outdated.  
     
2. There are three possibilities: the test does not verify what it claims to verify (it is trivial), the test verifies something that was already implemented (it was not a new feature), or the test has a bug that makes it always pass. In any case, the test is not fulfilling its function as an oracle.  
     
3. A spec describes what a feature does (mutable during development, eventually converging into documentation). An ADR describes why we made an architectural decision (immutable once accepted; if the decision is revisited, a new ADR that supersedes it is created).

---

## 3\. CDAD compared with alternatives

To understand CDAD in its context, it is worth comparing its characteristics with those of other methodologies and approaches. This helps to see which problems CDAD solves that others do not, and what is lost compared to simpler alternatives.

### 3.1 Comparative table of approaches

| Aspect | Vibe coding | Classic TDD | BDD | DDD | CDAD |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Who implements** | Unconstrained agent | Human developer | Human developer | Human developer | Sub-agents with limited permissions |
| **Spec before code** | No | Implicit (in one's head) | Yes (Gherkin features) | Yes (domain model) | Yes (structured markdown) |
| **Tests first** | Sometimes (depends on the prompt) | Yes (Beck's Iron Law) | Yes (Gherkin scenarios) | Not prescriptive | Yes (with isolated sessions) |
| **Formal contracts between components** | No | Optional | Not central | Yes (boundaries) | Yes (Protocols \+ contract tests) |
| **Persistent project memory** | No | Not prescriptive | Not prescriptive | Yes (model) | Yes (Memory Bank) |
| **Initial cost** | Very low | Medium | Medium-high | High | Medium-high |
| **Long-term sustainable quality** | Variable, frequently low | High if there is discipline | High | High for complex domains | Consistently high |
| **Works well with AI agents** | "Works" but unpredictable | Partially (gaming risk) | Yes, but heavy | Not prescriptive about AI | Designed for this |

### 3.2 When to choose what

**Choose vibe coding when:** you are in pure exploration, prototyping something disposable, learning a new technology with no quality commitment, or doing a one-off script you will throw away in a week.

**Choose classic TDD when:** you work alone or in a small human team, without significant AI agents in the workflow, and the discipline of not skipping the test is manageable. Classic TDD well applied is very powerful, and CDAD basically extends it to solve the specific problem of AI agents.

**Choose BDD when:** non-technical stakeholders are a central part of the process of defining behavior, and Gherkin scenarios are real communication tools with them. BDD adds ceremony that is only justified if you genuinely use it.

**Choose DDD when:** you are modeling a complex domain with many business rules, several bounded contexts, and domain complexity dominates technical complexity. DDD can be combined with CDAD perfectly: the DDD model is documented in the Memory Bank, the bounded contexts are enforced with import-linter in CDAD style.

**Choose CDAD when:** you will use AI agents as primary implementers, the code will live a long time, and sustainable quality matters more than initial speed.

### 3.3 CDAD is not exclusive

An important observation: CDAD does not exclude the other methodologies. You can combine CDAD with DDD perfectly (in fact, DDD's bounded contexts materialize very well as layers enforced with import-linter in CDAD). You can combine CDAD with BDD if your specs are executable Gherkin scenarios. You can combine CDAD with agile methodologies like Scrum or Kanban, because CDAD is about the technical process of implementation, not about how you organize iterations.

What CDAD explicitly replaces is vibe coding. If you are using AI agents and want sustainable quality, you cannot simply let the agent work free. The structural discipline is what makes the difference.

---

## 4\. The cycle: an overview

Before going deeper into each stage, it is worth having a panoramic view of the full cycle. CDAD organizes the work into five sequential stages per feature, with specific feedback loops when something fails.

### 4.1 The cycle in a diagram

flowchart TD

    Start(\[Feature idea\]) \--\> E1

    

    E1\[Stage 1\<br/\>Discovery\]

    E1 \--\> E2

    

    E2\[Stage 2\<br/\>Specification\]

    E2 \--\> ApprovalSpec{Spec\<br/\>approved?}

    ApprovalSpec \--\>|No| E2

    ApprovalSpec \--\>|Yes| E3

    

    E3\[Stage 3\<br/\>Anti-gaming TDD\]

    E3 \--\> TestsPass{Tests\<br/\>pass?}

    TestsPass \--\>|No| E3

    TestsPass \--\>|Yes| E4

    

    E4\[Stage 4\<br/\>Review two-layer\]

    E4 \--\> ReviewOk{Blocking\<br/\>resolved?}

    ReviewOk \--\>|No| E3

    ReviewOk \--\>|Yes| E5

    

    E5\[Stage 5\<br/\>Merge \+ Memory Bank\]

    E5 \--\> CIPass{CI\<br/\>passes?}

    CIPass \--\>|No| E3

    CIPass \--\>|Yes| Done(\[Feature done\])

    

    Done \-.next feature.-\> Start

    

    style E1 fill:\#e3f2fd

    style E2 fill:\#fff3e0

    style E3 fill:\#f3e5f5

    style E4 fill:\#e8f5e9

    style E5 fill:\#fff9c4

### 4.2 The five stages in a table

| Stage | Name | Who does what | Output | Typical time |
| :---- | :---- | :---- | :---- | :---- |
| 1 | Discovery | You manually or with a read-only architect agent | Knowledge of the terrain (APIs, hooks, conventions) | Variable: minutes to days |
| 2 | Specification | Brainstorm with the architect agent, you edit and approve | `docs/specs/NNN-feature/spec.md` approved | 30 min to 2 hs per feature |
| 3 | Anti-gaming TDD | test-writer and implementer sub-agents in separate sessions | Green code with tests passing | 1-8 hs per feature |
| 4 | Two-layer review | reviewer sub-agent \+ you validating the prioritization | Report of classified findings | 15-30 min per feature |
| 5 | Merge \+ Memory Bank | Automated CI \+ you updating context | Feature in main, Memory Bank updated | 10-20 min per feature |

### 4.3 Operational rules of the cycle

Before going deeper into each individual stage, it is worth internalizing three operational rules that apply to all of them:

**Rule 1: never skip stages.** The temptation to skip the spec because "it's a simple feature" is real and dangerous. Features that look simple at the beginning frequently reveal ambiguities during the implementation phase that a spec would have detected. The discipline of the process is what makes the result sustainable. If the feature is genuinely trivial (a single line of code), then the spec can be one paragraph long, but it exists.

**Rule 2: if a stage fails, you go back to the previous stage, not further back.** If the tests fail in stage 3, you do not go back to the spec; you adjust the implementation. If the reviewer detects divergences from the spec in stage 4, you go to stage 3 with specific instructions; you do not redo the spec. If the whole spec was wrong, then you do go back to stage 1 (discovery) and redo it. The rule minimizes rework while keeping the process intact.

**Rule 3: human approval at key moments is non-delegable.** You approve the spec before implementation starts. You validate the review's prioritization before the merge. You edit and commit the Memory Bank updates. These three points are where your judgment about the domain, the client, and the product matters more than the agent's execution speed.

---

## 5\. Stage 1 — Discovery

### 5.1 What it does and why it exists

The discovery stage exists to destroy the assumptions that any AI model carries from its training about the system you are going to work on. Models saw millions of lines of code during their training, but they did not see *your* code, *your* configuration, or *your* specific version of the framework. If you let them work without this stage, they invent APIs that do not exist, assume conventions that do not apply, or use patterns from earlier framework versions that are no longer valid.

The stage has two modes: the **initial discovery** of the whole project (done once at the start) and the **per-feature discovery** (a mini-phase that precedes each spec).

### 5.2 Initial discovery of the project

When you start a new project, before seriously involving AI agents, it is worth investing time in mapping the terrain. The idea is to produce a document `docs/landscape.md` (the name is flexible) that captures first-hand knowledge about the system you are going to work on.

**How it is done.** You bring up a clean instance of the system. You configure a realistic scenario representative of the use cases the project will cover. You enable developer mode and the debugger. You manually trace important flows. You note the real hooks, the available APIs, the naming conventions, the extension surfaces you are going to use. If it is a framework, you identify which methods are meant for `_inherit`, which classes are extensible, which patterns the official documentation recommends.

This knowledge goes into `docs/landscape.md` with sections per component or module. For example, in a project that extends a web framework, the document could have sections like "Available models", "Lifecycle hooks", "Migration conventions", "Plugin system", "Changes from the previous version", etc.

**Why it matters.** Without this, agents invent field names that do not exist and write code that fails on first load. With this, the first-shot hit rate rises dramatically because the agents have concrete factual context to base themselves on.

**Case study: date parser**

Imagine you are going to build the date parser we use as an example. What initial discovery makes sense?

- Check which date modules the language provides (`datetime` in Python, `Date` in JS, `time` in Go)  
- Check which ISO 8601 formats the standard parser covers and which it does not (Python's `fromisoformat` covers fewer cases than `dateutil`)  
- Research whether there are popular libraries for uncovered cases (`python-dateutil`, `arrow`, `pendulum`)  
- Map how the language represents timezones (Python has `timezone`, `pytz`, `zoneinfo`)  
- Identify version-specific gotchas (Python 3.11+ has an improved `fromisoformat` vs earlier versions)

This goes into the `landscape.md`: "The standard parser of Python 3.11+ covers \[...\], does not cover \[...\]. To cover \[...\] we will use `dateutil` as a fallback, imported only when the standard parser fails."

### 5.3 Per-feature discovery

Before each feature, there is a lighter mini-stage of discovery. Its goal is to verify that the agent's assumptions about the API it is going to touch are correct.

**How it is done.** You open a read-only session with an architect agent (large model, read-only permissions). You pass it the general context (Memory Bank) and ask it to map which hooks, methods, and fields relevant to the feature you are going to do exist. The agent explores the code, reads documentation if available, and produces a mapping. You validate that the mapping matches your intuition and what you see in the real code. If there are discrepancies, you investigate them.

The output of this mini-stage is incorporated into the feature's spec as a "Technical context" section or similar.

**For advanced readers — Exploration spike with real code**

For risky features or where the API to be used is not well known, it is worth running an exploratory *spike*: a session where your goal is not to implement the feature but to learn enough about the API to be able to specify it. The spike may involve writing exploratory code in a temporary branch that you throw away afterwards. The rule: spike code is never merged to main; what gets merged is the learned knowledge, folded back into the `landscape.md` or the spec.

### 5.4 How to manage this stage operationally

**You do the initial discovery manually.** You do not delegate this to the agent because it is the opportunity to gain first-hand knowledge that you will later use to critique what the agents propose. If you skip this, you are left without the foundation on which to critically evaluate later proposals.

**Per-feature discovery is done by a read-only architect agent**, supervised by you. You launch the session with a prompt like "explore section X of the code and map the available hooks for doing Y". You validate the output before incorporating it into the spec.

**When to consider the stage finished.** The initial discovery ends when you can explain to another person the central concepts of the system without opening the code. Per-feature discovery ends when you can write the spec without having to go look up API names in the code.

---

## 6\. Stage 2 — Specification

### 6.1 The three-step process

Specification is where a working idea becomes a technical document that can be implemented by an agent without ambiguity. The process has three steps: Socratic brainstorm, spec writing, human approval.

### 6.2 Step 1: Socratic brainstorm

**How it is done.** You start a session with an architect agent in plan-only mode (no edit permissions). You ask it: *"we are going to design feature X. Ask me the questions you need in order to understand exactly what I want, before proposing a design."*

The agent, if well configured, starts asking Socratic questions. Typical questions for our date parser example would be:

- What happens if the string is `null` or empty? Exception, default, or `None`?  
- What level of precision is worth preserving? Milliseconds? Microseconds? Nanoseconds?  
- Are there non-standard formats we must accept? For example, `"2026-04-29 15:30:00"` (space instead of T)?  
- What does it do if the timezone offset is invalid (`"+99:99"`)?  
- Should the function be thread-safe? Reentrant?  
- Are there performance constraints? Maximum latency per call? Expected throughput?

You answer. The agent refines. Questions may arise that you had not considered and that require consulting the client, looking at real data, or doing more research. This is exactly the function of the brainstorm: detecting ambiguities before they become bugs.

**When to end the brainstorm.** The brainstorm ends when the agent stops asking meaningful questions (the ones left are already implementation details) and you feel the feature is clear enough to start writing the spec. This can take twenty minutes for a simple feature or two hours for a complex one.

### 6.3 Step 2: spec writing

With the brainstorm complete, you write (or ask the agent to write and you edit) the spec document. The minimal structure is the one we saw in chapter 2:

\# Spec: \[feature name\]

\#\# Functional description

\[What it does, in non-technical language\]

\#\# Contract (signature and invariants)

\[Formal types with explicit postconditions\]

\#\# Verifiable invariants

\[Which will become property tests\]

\#\# Acceptance criteria

\[Measurable metrics for considering the feature done\]

\#\# Out of scope

\[What it does NOT do, to avoid scope creep\]

\#\# Implementation notes (optional)

\[Technical decisions made during the brainstorm\]

**Variants depending on the size of the feature.**

For trivial features (a fix, a configuration change), the spec can be one paragraph \+ one failing test. What matters is that something written exists.

For medium features (the majority), the previous format works perfectly.

For complex features spanning multiple components, the spec can be split into `spec.md` (what it does), `plan.md` (how it will be implemented, in what order), and `tasks.md` (list of concrete tasks with dependencies). This separation is valuable when the feature requires coordination.

### 6.4 Step 3: human approval

**How it is done.** You read the complete spec. You mark doubts. You ask the agent for adjustments if something is unclear. When you are satisfied, you approve it explicitly. The approval is materialized in some verifiable way: adding at the end of the spec a line `Status: Approved by [your name] on [date]`, making a commit with message `docs: approve spec for feature X`, or any mark that unambiguously indicates that you approved it.

**Why approval is non-delegable.** This is the stage where your judgment about the domain matters most. You know things the agent does not know: what the client really needs, what will surprise them, what will frustrate them, what fits with the rest of the product. If you skip this step, you will spend hours debugging implementations that solved a problem that was not yours.

**Case study: inventory REST API**

Imagine you are specifying an endpoint `POST /api/v1/products` that creates a product. Some questions the brainstorm should surface:

- Does the product have a unique SKU? Is uniqueness validated? In what scope (global, per tenant)?  
- Which fields are mandatory and which optional?  
- Can the price be zero or negative? What is the use case if so?  
- Is there an automatic `created_at` field? And `updated_at`? What happens with them in the request body?  
- What status code does it return on success? 201 with the created product? 200 with confirmation?  
- What status code on failed validation? Generic 400 or 422 with per-field details?  
- Is there rate limiting? Idempotency with the `Idempotency-Key` header?  
- Authorization? Who can create products?

Every unanswered question in the spec becomes a decision the agent makes without your input. The time investment is worth it.

### 6.5 How to manage this stage operationally

**You guide the brainstorm with your questions and domain knowledge.** The agent formulates Socratic questions and writes drafts. You edit and approve.

**Keep the spec in the repo.** It is not a Google Doc, it is not Notion. It is a versioned `.md` file in `docs/specs/NNN-feature/`. This allows it to be referenced from the code, its history to be visible, and the agent's next sessions to read it.

**If in the middle of implementation you detect something not contemplated in the spec**, you do not silently add it to the code. You go back to the spec, update it, and commit the spec change before implementing it. This keeps the spec as the source of truth.

**Self-assessment quiz**

1. What is the difference between the Socratic brainstorm and simply "thinking about the feature before coding"?  
2. Why is human approval of the spec non-delegable?  
3. What do you do if in the middle of implementation you discover a case not covered in the spec?

View answers 

1. The main difference is the externalization of reasoning. Thinking alone tends to skip the questions you already have "assumed". The Socratic brainstorm with an agent forces those assumptions to be made explicit because the agent does not have them assumed. It detects ambiguities that your intuition had suppressed.  
     
2. Because you have knowledge of the domain, of the client, and of the product that the agent does not have. If you delegate the approval, you lose the opportunity to verify that the feature solves the right problem. The consequences manifest later, when you have already spent time implementing something that was not what you wanted.  
     
3. You go back to the spec, update it explicitly, commit the spec change, and only then implement the case. If the spec does not capture something, adding the case silently to the code without updating the spec breaks the spec-as-source-of-truth principle and degrades the value of the process.

---

## 7\. Stage 3 — Anti-gaming TDD with isolated sessions

This is the longest stage and the one where discipline matters most. Let's go step by step with a complete example.

### 7.1 The structure of five sub-phases

Stage 3 is internally divided into five sub-phases. The first three correspond to the classic TDD cycle (RED → GREEN → REFACTOR). Two additional sub-phases are added: property tests for algorithmic components with clear invariants, and integration / E2E tests to verify the cross-component flows derived from the acceptance criteria.

sequenceDiagram

    participant You

    participant TW as test-writer

    participant Imp as implementer

    participant Ref as refactorer

    

    You-\>\>TW: Session 1: "Write test for postcondition X"

    TW-\>\>TW: Reads spec \+ interface (does not see code)

    TW-\>\>You: Failing test written (RED)

    You-\>\>You: Verify it fails for the right reason

    

    You-\>\>Imp: Session 2: "Make this test pass"

    Imp-\>\>Imp: Reads spec \+ test \+ interface

    Imp-\>\>You: Minimal code (GREEN)

    You-\>\>You: Verify it passes

    

    You-\>\>Ref: Session 3: "Refactor keeping green"

    Ref-\>\>Ref: Reads code \+ full suite

    Ref-\>\>You: Refactored code (REFACTOR)

    

    Note over You,Ref: When the algorithm is stable

    You-\>\>TW: Session 4: "Property tests for invariants"

    TW-\>\>You: Property tests (with Hypothesis or equiv.)

**Cycle granularity: grouping orthogonal postconditions.** The diagram shows the cycle applied to one postcondition. If a feature has ten postconditions, do you have to repeat the cycle ten times? The short answer is: not necessarily. The long answer requires distinguishing between *orthogonal* postconditions and *coupled* postconditions.

Two postconditions are **orthogonal** when they are implemented in code paths that do not overlap: they touch different functions, different branches of a conditional, different fields of a model. For orthogonal postconditions, you can group several in the same cycle: the test-writer writes the tests for several postconditions in one session (as long as none of those tests require seeing implementation code), the implementer covers them all in one GREEN iteration, and the refactor closes the cycle. It significantly speeds up the pace without losing the safety net, because the separation of phases (test before code) and the isolation of sessions (test-writer blind to the code) are preserved.

Two postconditions are **coupled** when they share logic: implementing the second forces touching the code that satisfies the first, or changing the algorithmic approach to accommodate both. For coupled postconditions, one-at-a-time cycles remain the correct option: if you put them together, the implementer can make an architectural decision that it later invalidates when the next postcondition shows up, and you end up rewriting.

**Practical heuristic.** Before starting the stage, you look at the spec's list of postconditions and group them into clusters. Postconditions that touch different fields of the same model, different error codes, different input formats, different endpoints: typically orthogonal, groupable. Postconditions that change the central algorithm, modify the shared data structure, or add cross-cutting logic (logging, transactions, auth): typically coupled, one at a time.

**Example with the date parser.** Of the five postconditions of the original spec, postconditions 1 (valid string → datetime), 2 (invalid string → InvalidDateError) and 6 (pure function) are orthogonal: the first and the sixth do not overlap at all, the second adds an independent validation branch. They can be grouped in a single cycle. Postcondition 3 (precision down to milliseconds) and 4 (offset preserved) touch the same parsing path and usually require joint algorithmic decisions: it is worth doing them in separate cycles or as a coupled cluster.

### 7.2 Sub-phase RED: writing the failing test

**Setup.** You start a new session with the `test-writer` sub-agent. You pass it:

- The approved spec (`docs/specs/NNN-feature/spec.md`)  
- The interface definition if it exists (`interfaces/[component].py`)  
- Eventually the `landscape.md` if the feature touches existing code

You ask it: *"Write the test that verifies postcondition \[N\] of the spec. The test must fail because the implementation does not exist yet."*

**What the test-writer does NOT see.** It does not see the algorithms folder, does not see the adapters, does not see implementation code that may already partially exist. Its read permissions are explicitly limited.

**What it produces.** A test that verifies the postcondition independently of how it will be implemented.

**Recurring example — date parser case**

Spec: postcondition 4 says "If s has a timezone offset (+05:30), the resulting DateTime reflects that offset."

The test-writer produces:

\# tests/test\_parse\_iso\_date.py

import pytest

from datetime import datetime, timezone, timedelta

from src.date\_parser import parse\_iso\_date

def test\_postcondition\_4\_explicit\_offset\_preserved():

    """Postcondition 4: explicit offset is preserved in the resulting datetime."""

    \# Simple case: positive offset

    result\_pos \= parse\_iso\_date("2026-04-29T15:30:00+05:30")

    expected\_pos \= datetime(

        2026, 4, 29, 15, 30, 0,

        tzinfo=timezone(timedelta(hours=5, minutes=30))

    )

    assert result\_pos \== expected\_pos

    

    \# Symmetric case: negative offset

    result\_neg \= parse\_iso\_date("2026-04-29T15:30:00-03:00")

    expected\_neg \= datetime(

        2026, 4, 29, 15, 30, 0,

        tzinfo=timezone(timedelta(hours=-3))

    )

    assert result\_neg \== expected\_neg

The test verifies that the offset is preserved. It assumes nothing about how the parser does the parsing internally.

**Mandatory verification before closing the session.** You run `pytest` and confirm the test fails for the right reason (the method returns something different from what is expected, or raises `NotImplementedError`, not an import or syntax error). If it fails for the wrong reason, the test is not valid and must be fixed within this same session before moving to the next one.

### 7.3 Sub-phase GREEN: implementing the minimal code

**Setup.** New session with the `implementer` sub-agent. You pass it:

- The spec  
- The test the test-writer wrote (visible)  
- The interface  
- Edit permissions on `src/`, `algorithms/`, `adapters/`

You ask it: *"Make this test pass by writing the minimum code necessary. Do not add functionality the test does not require."*

**What the implementer does NOT see.** It does not receive the test-writer's thinking context (the previous conversation). It only receives the final artifact: the written test. This prevents the implementer from "inheriting" the test-writer's mental approach and ending up with code too similar to the test-writer's mind.

**What it produces.** Code that makes the specific test pass, nothing more.

**Continuing the date parser case**

The implementer receives the test from the previous step. Its task is to add support for explicit offsets to `parse_iso_date`. If the current code only handles `Z`:

\# src/date\_parser.py (BEFORE)

from datetime import datetime, timezone

def parse\_iso\_date(s: str) \-\> datetime:

    if s.endswith("Z"):

        return datetime.fromisoformat(s\[:-1\]).replace(tzinfo=timezone.utc)

    raise NotImplementedError("only Z timezone supported")

The implementer extends it to satisfy the new test, without touching what already works:

\# src/date\_parser.py (AFTER)

from datetime import datetime, timezone

import re

\_OFFSET\_RE \= re.compile(r"(\[+-\]\\d{2}):(\\d{2})$")

def parse\_iso\_date(s: str) \-\> datetime:

    if s.endswith("Z"):

        return datetime.fromisoformat(s\[:-1\]).replace(tzinfo=timezone.utc)

    \# Python 3.11+ fromisoformat already handles offsets, but we illustrate

    \# the explicit approach for earlier versions

    return datetime.fromisoformat(s)

The implementer does NOT add functionality for timestamps without timezone (postcondition 5), because there is no test requiring it yet. That postcondition will come in its own iteration of the cycle.

**Verification.** You run `pytest` and confirm the new test passes AND that all the tests that were already passing keep passing. If a previous test broke, the implementer made changes that affected what already worked; go back to the implementer in the same session with the failure report.

### 7.4 Sub-phase REFACTOR: improving while keeping green

**Setup.** New session with the `refactorer` sub-agent (it can be the same `implementer` with a different prompt, or a dedicated sub-agent). You pass it:

- The code that already passes the tests  
- The full test suite visible  
- Edit permissions on code

You ask it: *"Refactor this code to improve readability, maintainability, and consistency with the rest of the codebase. All tests must keep passing. Do not change observable behavior."*

**What the refactorer does.** It renames variables for clarity, extracts functions when there is duplication, consolidates control structures, adds docstrings, adjusts types. What it does NOT do is change functionality, add features, or touch tests.

**When not to refactor.** If the code came out simple and clear after the GREEN, this sub-phase can be skippable. The rule is honest: refactor when it adds value, not out of process compulsion.

### 7.5 Sub-phase Property Tests: invariants with random generation

For algorithmic components (where correctness is not reduced to discrete cases but has general properties), we add a final sub-phase where we generate property tests using tools like Hypothesis (Python), QuickCheck (Haskell), fast-check (TypeScript), or equivalents in other languages.

**How it works.** Instead of writing specific cases, you write *properties* the algorithm must satisfy for *all* valid inputs. The library generates hundreds or thousands of random inputs and checks the property on each one. If it finds an input where it fails, it reports it to you minimized.

**Example: property tests of the date parser**

\# tests/test\_parse\_iso\_date\_properties.py

from hypothesis import given, strategies as st

from datetime import datetime, timezone, timedelta

from src.date\_parser import parse\_iso\_date

\# Strategy that generates random datetimes with timezone

aware\_datetimes \= st.datetimes(

    min\_value=datetime(1900, 1, 1),

    max\_value=datetime(2100, 12, 31),

    timezones=st.timezones(),

)

@given(dt=aware\_datetimes)

def test\_round\_trip\_property(dt):

    """Invariant: parse(format(dt)) \== dt for all dt."""

    iso\_string \= dt.isoformat()

    parsed \= parse\_iso\_date(iso\_string)

    assert parsed \== dt, (

        f"Round-trip failed for {iso\_string}: got {parsed}, expected {dt}"

    )

@given(s=st.from\_regex(r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"))

def test\_z\_timezone\_is\_utc\_property(s):

    """Invariant: any string with Z at the end is parsed as UTC."""

    try:

        result \= parse\_iso\_date(s)

        assert result.tzinfo \== timezone.utc

    except ValueError:

        pass  \# invalid strings may raise ValueError, that is OK

Hypothesis is going to generate thousands of strings and datetimes, and if it finds any where the property does not hold, it reports it. It frequently finds edge cases that deterministic tests do not detect: dates at the limit of the accepted range, unusual timezones, leap-year dates, etc.

**When to add property tests.** Not for everything. They work especially well for:

- Pure algorithms (parsers, encoders, solvers, data transformations)  
- Components with clear invariants (round-trip, idempotence, associativity)  
- Critical code where deterministic tests can have blind spots

They work less well for:

- Code with many side effects  
- Complex business logic with many conditions  
- UI

### 7.6 Sub-phase of integration and E2E tests

Unit tests, contract tests and property tests cover individual components and their invariants. But clients do not use components; they use complete flows. If the feature touches several layers (DB, business logic, API, UI), a test verifying that each component works in isolation can pass 100% while the end-to-end flow fails because the integration between the pieces is not the expected one.

**The risk of the agent that "aligns" is still present here.** At first sight, E2E tests are the phase where one feels tempted to relax the discipline: they are slow, they are few, "we already have unit coverage". But the risk of the agent aligning the E2E test with its implementation is exactly the same as with unit tests. If the implementer writes the E2E test, it will verify that the flow "works the way I built it", not that it satisfies the spec's acceptance criteria.

**The clean way out: derive E2E tests from the spec, not from the code.** The acceptance criteria of a well-written spec are, to a large extent, E2E tests in natural language. *"When the sale is confirmed, stock decreases and a draft invoice is generated"* is an E2E test. *"If the user does not have approval permissions, the endpoint returns 403"* is an E2E test. The operational rule is: E2E tests are written in a `test-writer` session that sees the spec (including acceptance criteria) and the public API of the system, but does not see the implementation of the feature in progress.

**How it fits into the cycle.** There are two valid modes, depending on the nature of the feature:

*Mode A — E2E first (outside-in).* The E2E test is written before any unit test. It is written from the spec downward, expressing a complete flow. This test stays red during the whole implementation cycle, until the individual pieces (covered by unit tests) connect and the full flow passes. It is the approach of classic Acceptance Test-Driven Development. It works well when the flow is clear from the start and you want a continuous progress metric ("how much is left until the E2E passes?").

*Mode B — E2E at the end as closure.* The E2E test is written after the units are implemented and green, but before the merge. It works as verification that the assembly is correct. It is operationally simpler and less heavy on CI during development, but you lose the continuous metric of approach A.

**Which to choose.** For features with a clear and central flow (a new endpoint, a defined business process), prefer mode A. For features that are additions to multiple existing flows (a new field that appears in five views, a validation applied on several endpoints), mode B is more practical.

**Structure of an E2E test in CDAD.** The E2E test follows the same principle as unit tests: arrange, act, assert, with assertions specific to the acceptance criteria. The difference is the granularity of the setup (complete data fixtures, not point mocks) and the scope of the act (a complete flow, not a function call).

**Example: feature "sale confirmation"**

Spec with acceptance criterion: *"When confirming a sales order with products in stock, (a) the order state changes to 'sale', (b) the stock of the products decreases by the corresponding quantity, (c) a draft invoice is generated with the order's lines, (d) if the client has no available credit, the confirmation fails with a specific message."*

The test-writer, in a session isolated from the implementer, translates this into something like:

\# tests/integration/test\_sale\_confirmation\_e2e.py

def test\_confirm\_sale\_with\_stock\_succeeds(self):

    \# Arrange: customer with credit, products with stock

    customer \= self.\_create\_customer(credit\_limit=10000)

    product \= self.\_create\_product(initial\_stock=10)

    order \= self.\_create\_draft\_order(customer, \[(product, 3)\])

    

    \# Act: confirm the order via the public API

    result \= self.client.post(f"/api/orders/{order.id}/confirm")

    

    \# Assert: four postconditions of the acceptance criterion

    assert result.status\_code \== 200

    order.refresh()

    assert order.state \== "sale"  \# (a)

    assert product.available\_stock \== 7  \# (b)

    invoice \= self.\_find\_draft\_invoice\_for(order)

    assert invoice is not None and invoice.state \== "draft"  \# (c)

    assert len(invoice.lines) \== 1

    assert invoice.lines\[0\].quantity \== 3

def test\_confirm\_sale\_without\_credit\_fails(self):

    customer \= self.\_create\_customer(credit\_limit=0)

    product \= self.\_create\_product(initial\_stock=10)

    order \= self.\_create\_draft\_order(customer, \[(product, 3)\])

    

    result \= self.client.post(f"/api/orders/{order.id}/confirm")

    

    assert result.status\_code \== 422

    assert "credit" in result.json()\["error"\].lower()  \# (d)

    order.refresh()

    assert order.state \== "draft"  \# state did not change

The test-writer writes these cases seeing only the spec and the public API of the system. It does not look at the code of the confirmer. The implementer receives these tests and makes them pass. Correct integration is verified automatically.

**When NOT to add E2E tests.** For purely algorithmic features without side effects (a parser, a data transformer), unit tests \+ property tests cover everything you need. Adding an E2E is ceremony without value. The rule: E2E when there is a cross-component flow with observable effects; unit \+ property when there is not.

### 7.7 How to manage this stage operationally

**You are the orchestrator.** You open and close sessions. You verify each step passes before moving forward. You make intermediate commits between sub-phases to have checkpoints.

**The typical pace.** For a postcondition with a full cycle (RED → GREEN → REFACTOR): between 30 and 90 minutes depending on complexity. For a feature with five postconditions, estimate between 3 and 8 hours in total. This includes the inevitable back-and-forth when some test fails for the wrong reason or the implementer does something unrequested. If you group orthogonal postconditions, the total time drops substantially.

**The temptation to resist: "a single session for everything."** It is the main trap of the stage. When the implementer also writes the test, you lose the independent oracle. The apparent speed you gain (not having to switch context) is paid for with weak tests that do not detect real bugs.

**Granular commits.** Each step of the cycle ends in a commit. Typical messages: `test: add failing test for postcondition 4`, `feat: implement parsing of explicit offsets`, `refactor: extract offset parsing helper`. This gives clean history and allows `git bisect` when something breaks later.

**Self-assessment quiz**

1. Why should the test-writer not see the implementation code?  
2. What does the implementer specifically do when a test fails for the wrong reason (e.g. ImportError)?  
3. When is it advisable to skip the REFACTOR sub-phase?  
4. In what kind of code are property tests most valuable?

View answers 

1. Because if it saw it, its test would tend to align with the particular implementation instead of verifying the spec independently. This would make the test pass not because the code is correct, but because the test was written to pass with that specific code. The separation guarantees that the test is a genuine oracle.  
     
2. It goes back to the test-writer to fix the test, not to the implementer. If the test fails with an ImportError or another technical error, the test is not verifying what it claims to verify. The test must be fixed before moving to the implementer.  
     
3. When the code that came out of the GREEN is already clear, concise, and consistent with the rest of the codebase. The REFACTOR sub-phase is not mandatory; it is an opportunity. If it adds nothing, do not do it. The rule is: refactor when it adds value, not out of ritualism.  
     
4. In algorithmic code with clear invariants: parsers, encoders/decoders, solvers, data transformations. Where you can express general properties that must hold for all valid inputs (round-trip, idempotence, associativity). It works less well on code with many side effects or business logic with many specific conditions.

---

## 8\. Stage 4 — Two-layer review

### 8.1 Why two layers

Traditional review in human teams has two problems on projects where agents implement: the human reviewer gets tired quickly in front of large diffs, and often does not detect divergences from the spec because they do not remember the spec in detail. CDAD proposes a two-layer model: first a reviewer agent does an exhaustive pass with the spec in context and produces a prioritized report; then you validate the prioritization (not the full diff).

flowchart LR

    Diff\[Full diff\<br/\>of the feature\] \--\> AReviewer\[Layer 1\<br/\>Reviewer agent\]

    Spec\[Approved spec\] \--\> AReviewer

    Linter\[import-linter\<br/\>boundaries\] \--\> AReviewer

    

    AReviewer \--\> Report\[Prioritized report\<br/\>Blocking / Optional\]

    

    Report \--\> Human\[Layer 2\<br/\>You\]

    

    Human \--\> Decision{Is the\<br/\>prioritization correct?}

    Decision \--\>|Yes| Done\[List of fixes\<br/\>for the implementer\]

    Decision \--\>|Adjust| Manual\[You add blocking ones\<br/\>or discard optional ones\]

    Manual \--\> Done

### 8.2 Layer 1: reviewer agent

**Setup.** New session with the `reviewer` sub-agent with read-only permissions. You pass it:

- The full diff of the feature  
- The approved spec  
- The interface the feature implements  
- The `.importlinter` file with the architectural boundaries  
- Project conventions if they exist (`AGENTS.md` or `CONTRIBUTING.md`)

**Ideally, you use a different model from the one that implemented.** This is an important practice: if the implementer was Claude Sonnet, the reviewer can be GPT-5 or Qwen. The reason is that different models have different blind spots; using a different one for review gives a real second perspective, not an echo. If you only have one model, it still works, but you lose that diversity.

**The prompt to the reviewer.** Something like:

\*"Review this diff against the attached spec. Report findings in these categories:

1. **Spec divergences**: the code does not implement what the spec asks for, or adds things the spec does not ask for.  
2. **Boundary violations**: imports forbidden by the import-linter, layers that do not respect the allowed dependencies.  
3. **Security risks**: SQL injection, command injection, hardcoded secrets, missing validation.  
4. **Consistency problems**: the code does not follow the conventions of the rest of the project.  
5. **Simplification suggestions**: opportunities to make the code simpler without changing behavior.

For each finding, mark: **Blocking** (must be fixed before the merge) or **Optional** (a suggestion, does not block).

Produce a structured report in markdown."\*

**The output.** A structured report, something like this:

\# Feature review: date parsing with offsets

\#\# Blocking

\#\#\# 1\. Spec divergence — Postcondition 5 not covered

Location: src/date\_parser.py:8-12

Problem: Postcondition 5 of the spec says "If s has no timezone, 

the resulting DateTime is explicit UTC". The current code uses 

fromisoformat() which in Python \<3.11 returns a naive datetime, not UTC.

Suggestion: add an explicit branch to detect absence of 

timezone offset and force UTC.

\#\#\# 2\. Boundary violation — import from algorithms to adapters

Location: algorithms/parser\_helpers.py:3

Problem: import-linter contract "algorithms-pure" forbids imports 

from algorithms/ to adapters/. Line 3 violates this contract.

Suggestion: move the helper to interfaces/ or duplicate the logic if 

it is trivial.

\#\# Optional

\#\#\# 3\. Simplification suggestion — unnecessary precompiled regex

Location: src/date\_parser.py:5

Problem: The regex compiled at module level is not used in the current code.

Suggestion: remove it if it will not be used.

\#\#\# 4\. Style — docstring format not consistent

Location: src/date\_parser.py:7

Problem: the docstring uses a format different from the rest of the project.

Suggestion: adjust to the format of the rest.

### 8.3 Layer 2: human validation

**How it is done.** You read the report, not the full diff. The reviewer already did the work of filtering and prioritizing; your job is to validate that prioritization.

For each blocking finding, you decide whether it is genuinely blocking. Most of the time you will agree, but there are cases where you know something the reviewer does not: maybe the "spec divergence" is because the spec changed and has not been updated yet, maybe the "boundary violation" has a legitimate exception documented in an ADR.

For each optional finding, you decide whether to apply it now or discard it. Some optionals are frankly good and it is worth riding the momentum; others are over-engineering that adds nothing.

**The output of layer 2.** A prioritized list of fixes that goes to the implementer in a new round. Something like:

\*"Apply these changes to the code:

1. \[Blocking\] Add a branch in parse\_iso\_date for cases without timezone, returning explicit UTC.  
2. \[Blocking\] Move parser\_helpers to interfaces/ and update imports.  
3. \[Accepted optional\] Remove the unused regex.

We ignore for now:

- Docstring change (I will do it myself later in a cleanup pass)."\*

### 8.4 The feedback loop with stage 3

If there are blocking findings, you go back to stage 3 with the list of fixes. The implementer applies the changes, the tests must keep passing (if the fixes require behavior changes, that means the spec needs updating and going back to stage 2). After the fixes, optionally another pass of the reviewer to verify.

**Table: severity matrix of findings**

| Finding type | Default severity | Exception |
| :---- | :---- | :---- |
| Spec divergence | Blocking | Only if you validate that the spec was outdated |
| Boundary violation | Blocking | Only if there is an explicit ADR authorizing it |
| Security risk | Blocking | No exceptions |
| Functional bug | Blocking | No exceptions |
| Style inconsistency | Optional | Blocking if it is massive |
| Simplification opportunity | Optional | Blocking if the current complexity is problematic |
| Suggestion of an additional feature | Discard | That is scope creep |

### 8.5 How to manage this stage operationally

**Keep the reviewer's report in the PR or in a temporary file.** Useful when the implementer applies fixes, to verify all blocking findings were covered.

**Review is NOT optional.** The temptation to skip review on small features is strong. Resist it. Even a brief review by a reviewer agent running over a 30-line diff is worth it: it detects inconsistencies that seem minor in the moment but accumulate.

**Check your own prioritization with healthy skepticism.** It is easy to reject a blocking finding because going back to the implementer is costly. If you do it systematically, you are mining quality. A useful heuristic: if you doubt whether a blocking finding is genuine, err on the side of treating it as blocking. The cost of an extra iteration is low; the cost of merging a bug is high.

---

## 9\. Stage 5 — Merge and Memory Bank

### 9.1 CI verification before the merge

Before merging, a full suite of automated verifications must pass. This is NOT optional, and it cannot be skipped because "I trust this change". The verifications are:

**Full linter.** It runs over all modified files, not just the diff's. It detects style violations, common bugs (unused variable, unused import), and problematic patterns.

**Type checker.** If the language supports static types (Python with mypy, TypeScript with tsc, etc.), it runs over the code. In CDAD, we recommend strict mode at least for the interface and contract files.

**Import-linter (or equivalent).** It verifies that the architectural boundaries were not violated. If there are layer contracts (presentation does not import from domain, algorithms does not import from framework), import-linter enforces them.

**Unit and integration tests.** The full suite, not just the new tests. The reason is that the new ones may have broken things that already worked.

**Parameterized contract tests.** If the feature adds an implementation of a Protocol, the contract tests automatically verify it. If it breaks any postcondition, it fails here.

**Property tests.** For algorithmic code with property tests configured, they run with the configured seed and verify the invariants hold.

**Project-specific verifications.** Any custom check the project has configured (verify the manifest was not modified without justification, verify there are no TODOs without an associated issue, etc.)

flowchart LR

    PR\[PR ready for merge\] \--\> CI{CI pipeline}

    CI \--\> L\[Linter\]

    CI \--\> T\[Type checker\]

    CI \--\> I\[Import-linter\]

    CI \--\> U\[Unit tests\]

    CI \--\> Int\[Integration tests\]

    CI \--\> CT\[Contract tests\]

    CI \--\> P\[Property tests\]

    

    L \--\> All\[Everything passes\]

    T \--\> All

    I \--\> All

    U \--\> All

    Int \--\> All

    CT \--\> All

    P \--\> All

    

    All \--\> Merge\[Merge to main\]

    

    L \-.fails.-\> Back\[Go back to stage 3\]

    T \-.fails.-\> Back

    I \-.fails.-\> Back

    U \-.fails.-\> Back

    Int \-.fails.-\> Back

    CT \-.fails.-\> Back

    P \-.fails.-\> Back

### 9.2 Updating the Memory Bank

After the merge, you update the Memory Bank. This is NOT busy-work; it is what ensures the next session starts with fresh context.

**What to update.**

`activeContext.md`: you add an entry with the date, what feature was closed, relevant technical decisions that affect the future, technical debt detected (if any). For example:

\#\# 2026-04-29 — Feature: date parsing with offsets

Closed the ISO 8601 parsing feature with explicit offset support.

Relevant decisions:

\- We use stdlib fromisoformat() instead of dateutil to minimize

  dependencies. Trade-off: in Python \<3.11 there are uncovered edge cases

  documented in the spec's out-of-scope.

Technical debt detected:

\- The parser assumes ASCII strings; supporting Unicode dates in other

  scripts (Japanese/Arabic) would require changes. Out of scope for now.

Next feature in the queue: inverse formatting (datetime → ISO string).

`progress.md`: you move the feature from "in progress" to "done", you update the overall project status.

**ADR if applicable.** If the feature involved a new architectural decision that was not documented, you create the ADR now. The rule is: if in 6 months someone (you or an agent) could ask "why did we do X this way?", that decision deserves an ADR.

**Who does the update: the Scribe pattern.** There is a real tension here. On the one hand, the principle says that updating the Memory Bank is a human responsibility, because it defines the context the next session will read and delegating it to the agent without supervision degrades quality. On the other hand, writing from scratch the `activeContext.md` entry after each feature takes 15-20 minutes, and under delivery pressure it is one of the first steps the human skips. The net result is an outdated Memory Bank, which is worse than any alternative.

The solution we recommend is to separate draft generation from final approval, materialized as a **Scribe** sub-agent:

1. **The Scribe drafts.** A read-only sub-agent that receives in its context: the feature's approved spec, the full diff of the PR, the reviewer's report (stage 4), and the current Memory Bank files. Its task is to produce three structured outputs: a proposed entry for `activeContext.md`, the proposed changes for `progress.md`, and a draft ADR if it detects there was a relevant architectural decision (with a "confidence" field indicating how sure it is that it merits an ADR).  
     
2. **You validate and edit.** You read the draft. You correct what the Scribe understood wrong. You add what the Scribe could not know (for example, client context, product decisions made outside the PR). You discard the ADR draft if the decision was not as architectural as the Scribe believed, or expand it if it was.  
     
3. **You commit.** The final commit carries your authorship and reflects your judgment. The distinctive mark of Memory Bank commits is the `docs(memory):` prefix so the history is easy to audit.

**Why this pattern preserves the principle.** The original argument ("if you delegate this to the agent without reviewing, quality eventually degrades") remains valid: the problem was not that the agent generated text, but that the human stopped reviewing. The Scribe pattern makes explicit that generation is assisted but approval is non-delegable, just as you already do in review (stage 4) where the reviewer drafts findings and you validate the prioritization. Friction drops from 15-20 minutes to 3-5 minutes per feature, which makes it far more likely to be done consistently.

**Minimal Scribe configuration.**

"scribe": {

  "default\_model": "claude-sonnet",  // large model for synthesis

  "permissions": {

    "edit": \[\],  // read-only, only proposes

    "read": \["docs/\*\*", "src/\*\*", "tests/\*\*", ".git/\*\*"\]

  },

  "instructions": "instructions/scribe.md"

}

The Scribe prompt in `instructions/scribe.md` is something like:

*"Your task is to produce a draft of the Memory Bank update after a merged PR. You receive the approved spec, the PR diff, and the reviewer's report. You produce three outputs in separate markdown blocks:*

*1\. **Entry for activeContext.md**: date, feature name, relevant technical decisions (with emphasis on those affecting future code), technical debt detected (if any), next feature in the queue if you know it.*

*2\. **Changes for progress.md**: which entries to move from in-progress to done, what to update.*

*3\. **Possible ADR**: if you detect an architectural decision that merits an ADR, produce the full draft with title, context, options considered, decision, and consequences. State your confidence (high/medium/low) that this really merits an ADR.*

*Be concise. Write in the tone of the rest of the existing Memory Bank. Do NOT invent context that is not in the inputs."*

**Automated variant via CI.** A lighter alternative to the Scribe sub-agent is a CI script that extracts structured data from the PR (commit message, modified files, reviewer findings if they are in a standardized comment) and generates a skeleton entry that you fill in. It loses the LLM's synthetic capability (it will not synthesize for you "this feature implies an approach change in X"), but gains in speed and predictability. It works well for projects where features are repetitive.

### 9.3 How to manage this stage operationally

**The merge itself is trivial.** If CI passes, you merge to main (ideally with squash to keep history clean). The work is in the previous steps.

**The Memory Bank update with Scribe takes 3-5 minutes.** Without Scribe, it takes 15-20 minutes. The difference is what makes the step get done consistently or not get done, which in turn determines whether the Memory Bank stays useful or degrades.

**Reset the agent sessions after the merge.** Do not reuse an old session for the next feature. Each feature starts with a new session, reading the updated Memory Bank. This avoids context drift.

**For advanced readers — Versioning the Memory Bank**

The Memory Bank lives in the repo, versioned with Git. Every update is a commit. This lets you see the project's evolution, do `git blame` to understand why a decision was made, and eventually roll back if a decision proves wrong. A useful practice: in commits that update the Memory Bank, use the `docs(memory):` prefix to distinguish them from code commits.

---

## 10\. Tool configuration

CDAD is agnostic about the specific AI model you use, but requires tools that support certain capabilities. In this chapter we discuss what features to look for and typical configurations.

### 10.1 Capabilities the orchestrator must support

Regardless of the concrete tool, the orchestrator (the piece of software you interact with to coordinate agents) must support:

- **Sub-agents with granular permissions by glob patterns** (which files it can read, which it can edit). This materializes the isolated sessions principle.  
- **Per-model configuration per agent** (the test-writer can use one model, the implementer another). This makes it possible to use different models for independent review.  
- **Hierarchical loading of instructions** (a root `AGENTS.md` that is always loaded, per-sub-agent specific instructions). This avoids repeating context.  
- **Language Server Protocol integration** (linter, real-time type checker available to the agents). This gives them immediate technical feedback.  
- **MCP (Model Context Protocol) or equivalent**: the ability to connect the agent to external tools (DB queries, docs fetching, etc.).

Tools that currently fulfill these capabilities to varying degrees include OpenCode, Claude Code, Cursor, Aider (partially), among others. Choosing between them depends on your UI preferences, budget, and available models. What matters is that **CDAD works with any orchestrator that fulfills the core capabilities**.

### 10.2 Typical orchestrator configuration

Regardless of the concrete tool, the configuration usually has a similar structure:

// Pseudo-config of the orchestrator (syntax adapted per tool)

{

  "providers": \[

    { "name": "anthropic", "models": \["claude-sonnet", "claude-opus"\] },

    { "name": "openai", "models": \["gpt-5"\] },

    { "name": "alibaba", "models": \["qwen3-coder", "kimi-k2"\] }

  \],

  "agents": {

    "architect": {

      "default\_model": "claude-opus",

      "permissions": {

        "edit": \[\],  // plan-only mode

        "read": \["\*\*"\]

      },

      "instructions": "instructions/architect.md"

    },

    "test-writer": {

      "default\_model": "qwen3-coder",

      "permissions": {

        "edit": \["tests/\*\*"\],

        "read": \["docs/specs/\*\*", "interfaces/\*\*", "tests/\*\*"\]

      },

      "instructions": "instructions/test-writer.md"

    },

    "implementer": {

      "default\_model": "claude-sonnet",

      "permissions": {

        "edit": \["src/\*\*", "algorithms/\*\*", "adapters/\*\*"\],

        "read": \["docs/specs/\*\*", "interfaces/\*\*", "tests/\*\*"\]

      },

      "instructions": "instructions/implementer.md"

    },

    "reviewer": {

      "default\_model": "kimi-k2",  // different from the implementer

      "permissions": {

        "edit": \[\],  // read-only review

        "read": \["\*\*"\]

      },

      "instructions": "instructions/reviewer.md"

    }

  },

  "lsp": \["pyright", "ruff"\],

  "mcp\_servers": {

    "context7": "url-to-docs-server",

    "project-db": "url-to-db-mcp"

  }

}

### 10.3 The root AGENTS.md

A central piece of the configuration is the `AGENTS.md` at the project root. This file is loaded automatically by all sub-agents and contains context that applies to the whole project.

**Typical structure.**

\# AGENTS.md — conventions of project X

\#\# Tech stack

\- Python 3.12, Postgres 16, FastAPI, SQLAlchemy

\- Tests with pytest, property tests with Hypothesis

\#\# Important commands

\- \`make test\`: runs the full suite

\- \`make test-fast\`: runs only unit tests

\- \`make lint\`: runs ruff \+ mypy \+ import-linter

\- \`make check\`: lint \+ tests, must pass before each commit

\#\# Coding standards

\- Errors with specific classes, not generic Exception

\- Complete type hints on public functions

\- Docstrings in Google style format

\- Imports sorted with isort

\#\# Don't touch list

\- \`migrations/\`: modify only via alembic, never by hand

\- \`\_\_manifest\_\_.py\`: requires a \`\# AGENT-REVIEWED:\` comment before changes

\- \`secrets/\`: never read nor modify

\#\# Architectural boundaries (enforced by import-linter)

\- \`algorithms/\` does not import from \`adapters/\`, \`models/\`, or the framework

\- \`domain/\` does not import from \`infrastructure/\`

\- \`presentation/\` may import from any deeper layer

\#\# Agent workflow

\- Before coding: read \`docs/activeContext.md\`, read the relevant spec

\- TDD mandatory: failing test before code

\- Never use /compact; when context \> 70%, do a fresh handoff

\- At the end of a feature: update \`docs/activeContext.md\` and \`docs/progress.md\`

\#\# Commit conventions

\- Prefixes: feat, fix, docs, refactor, test, chore

\- Messages in present tense: "add validation", not "added validation"

\- Reference the spec/issue when applicable

\#\# Critical changes in the current framework version

\[List of changes between versions the models do not know\]

### 10.4 QA tool configuration

CDAD requires certain QA tools configured. In Python, typically:

**ruff** (linter \+ formatter) in `pyproject.toml`:

\[tool.ruff\]

line-length \= 100

target-version \= "py312"

\[tool.ruff.lint\]

select \= \["E", "F", "W", "I", "N", "UP", "B", "SIM", "RUF"\]

ignore \= \["E501"\]  \# line length handled by the formatter

**mypy** (type checker) in `pyproject.toml`:

\[tool.mypy\]

python\_version \= "3.12"

strict \= false  \# globally lenient

\[\[tool.mypy.overrides\]\]

module \= "interfaces.\*"

strict \= true  \# interfaces are strict

**import-linter** in `.importlinter`:

\[importlinter\]

root\_packages \= src

\[importlinter:contract:1\]

name \= algorithms-pure

type \= forbidden

source\_modules \= src.algorithms

forbidden\_modules \= src.adapters, src.models, framework

\[importlinter:contract:2\]

name \= layers

type \= layers

layers \=

    src.presentation

    src.application

    src.domain

    src.infrastructure

**pre-commit** in `.pre-commit-config.yaml`:

repos:

  \- repo: https://github.com/astral-sh/ruff-pre-commit

    rev: v0.7.0

    hooks:

      \- id: ruff

      \- id: ruff-format

  \- repo: https://github.com/pre-commit/mirrors-mypy

    rev: v1.13.0

    hooks:

      \- id: mypy

        files: ^src/interfaces/

  \- repo: local

    hooks:

      \- id: import-linter

        name: import-linter

        entry: lint-imports

        language: system

        pass\_filenames: false

### 10.5 Equivalents in other languages

| Capability | Python | TypeScript | Java | Go | Rust |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Linter | ruff | eslint | checkstyle | golangci-lint | clippy |
| Type checker | mypy | tsc | (built-in) | (built-in) | (built-in) |
| Boundaries | import-linter | dependency-cruiser | ArchUnit | go-cleanarch | (manual via crates) |
| Tests | pytest | jest, vitest | JUnit | testing | cargo test |
| Property tests | hypothesis | fast-check | jqwik | rapid | proptest |
| Pre-commit | pre-commit | husky | (various) | pre-commit | pre-commit |

---

## 11\. CDAD in opinionated frameworks

So far the document describes CDAD assuming relatively decoupled architectures: modules with clear responsibilities, layers that can be enforced with `import-linter`, formal contracts between components. That works well for services built with FastAPI, stateless microservices, pure libraries, well-structured frontends. But much of the real work of software happens inside **strongly opinionated frameworks**: Odoo, Django, Rails, Webmin, WordPress, Drupal, Spring Boot, Laravel, and many others. These frameworks impose their own way of organizing code, their own extension mechanisms, their own coupled ORM (when applicable), their own testing patterns. CDAD works perfectly well inside these frameworks, but requires some adaptations to the concrete materialization of the principles.

This chapter first discusses which characteristics of opinionated frameworks break the assumptions of the "standard" document, then presents four case studies in different frameworks and languages (Odoo in Python, Django in Python, Rails in Ruby, Webmin in Perl), and closes with a general heuristic for adapting CDAD to frameworks the document does not explicitly cover. All the frameworks used as examples are free software.

### 11.1 What breaks and what is preserved

Opinionated frameworks have, almost by definition, the following properties:

- **ORM coupled to the domain model.** The model is not a pure class that is later mapped to the database; the model *is* an ORM entity that knows the database by construction. Inheriting from `models.Model` (Django, Odoo), `ApplicationRecord` (Rails) or equivalent automatically brings DB connection, validations, lifecycle, and an enormous API surface.  
    
- **Ad-hoc extension mechanisms.** Instead of dependency injection by interface, there is `_inherit` (Odoo), `class_eval` and monkey-patching (Rails), middleware and signals (Django), hooks and filters (WordPress). These mechanisms are perfectly valid in their context, but do not lend themselves to verifiable contracts via `Protocol` or `interface`.  
    
- **Implicit conventions the framework assumes.** Rails has convention over configuration; Django assumes a certain organization of apps; Odoo assumes a certain manifest structure. Breaking the conventions is technically possible but fighting the framework.  
    
- **Testing infrastructure provided by the framework.** Instead of pure pytest, you use Django's `TestCase` with its test runner, `Minitest`/`RSpec` with Rails fixtures, Odoo's `TransactionCase`/`HttpCase`. These classes bring setup/teardown, automatic transactions, fixtures, and specific patterns.

**What changes in CDAD in the face of these properties.** Three principles need adaptation:

*Principle 2 (verifiable contracts).* It is not always viable to express contracts as a formal `Protocol` or `interface`. The adaptation is to express the contracts as **tests over the behavior of the extended model or the exposed endpoint**: instead of "all implementations of `IKnapsackSolver` satisfy postcondition X", the contract becomes "all extensions of `sale.order` that add a `confirm()` method satisfy postcondition Y, verified by a parameterized test over the inheritance".

*Principle 3 (isolated sessions).* The idea is preserved, but the permissions by glob pattern are finer. In Odoo, you want the `test-writer` to read only `models/`, `tests/`, and the manifest, but not the XML views where behavior could be inferred. In Django, you want it to read `models.py`, `serializers.py`, `tests/`, but not `views.py`.

*Principle 4 (TDD with the Iron Law).* It is preserved literally, but the "test that fails for the right reason" has a heavier ritual: bringing up the test database, running migrations, instantiating the framework. The framework's QA tools (pylint-odoo, django-stubs, rubocop-rails) take the role that `import-linter` plays in generic CDAD.

**What stays intact.** The other three principles require no adaptation:

- Principle 1 (spec before code): equally valid, equally necessary.  
- Principle 5 (persistent Memory Bank): equally valid, equally necessary; the Memory Bank of an Odoo or Django project looks identical to that of any other project.  
- The five stages of the cycle (discovery, spec, anti-gaming TDD, review, merge) are applied the same way.

And all the anti-patterns of chapter 12 are still anti-patterns here.

### 11.2 Case study 1 — Odoo

Odoo is a Python ERP framework with a particular architecture: the whole domain is modeled as classes that inherit from `models.Model`, with a proprietary ORM, a multiple-inheritance-by-name mechanism (`_inherit`), specific field descriptors, declarative XML views, a permission system based on records and groups, and a manifest per module. The typical use is building custom modules that extend core models or OCA modules (Odoo Community Association).

**What breaks the assumptions of the standard document.**

- There is no clean way to apply orthodox `import-linter`. Models import from the core ORM constantly; views reference models by string; `self.env` is ubiquitous and crosses all layers.  
- The "interfaces" are not Python `Protocol`s; they are `_inherit` patterns that extend existing models. The extension surface is defined by the public methods of the core models.  
- Tests use `TransactionCase` or `HttpCase`, with setup that depends on Odoo's registry. They cannot be run as pure pytest without bringing up the framework.  
- The manifest (`__manifest__.py`) declares dependencies between modules; badly made changes break the loading order.

**Recommended adaptations.**

*Essential QA tool: pylint-odoo (OCA).* The OCA maintains `pylint-odoo`, a pylint plugin with checks specific to Odoo: detection of fields without `string`, missing translations, badly defined `sql_constraint`s, `compute` methods without `@api.depends`, badly declared manifest dependencies, and many more. **In Odoo projects, pylint-odoo is not optional**: it fulfills the role that `import-linter` fulfills in generic projects: enforcing structural rules the AI agent does not know by trade. Minimal configuration:

\# pyproject.toml

\[tool.pylint.MASTER\]

load-plugins \= \["pylint\_odoo"\]

\[tool.pylint."MESSAGES CONTROL"\]

enable \= \[

    "manifest-required-author",

    "manifest-required-key",

    "missing-readme",

    "no-write-in-compute",

    "translation-required",

    "sql-injection",

    "external-request-timeout",

    \# ... (complete list according to the project's needs)

\]

The reviewer (stage 4) and CI (stage 5) run `pylint --load-plugins=pylint_odoo` over the modified modules as part of the mandatory pipeline.

*Verifiable contracts as tests over the extended model.* Instead of `Protocol`, you express the contract as an abstract base class of parameterized tests that is executed against any extension of the model:

\# tests/contracts/test\_sale\_order\_confirm\_contract.py

from odoo.tests.common import TransactionCase

class SaleOrderConfirmContract(TransactionCase):

    """Contract: any extension that overrides sale.order.action\_confirm()

    must preserve these postconditions.

    

    Concrete subclasses: one per extension the module introduces.

    """

    

    def setUp(self):

        super().setUp()

        self.order \= self.\_build\_test\_order()  \# subclass may customize

    

    def \_build\_test\_order(self):

        \# default; subclasses may override if their extension 

        \# requires specific setup

        ...

    

    def test\_postcondition\_state\_changes\_to\_sale(self):

        self.order.action\_confirm()

        self.assertEqual(self.order.state, 'sale')

    

    def test\_postcondition\_invoice\_draft\_generated(self):

        self.order.action\_confirm()

        invoices \= self.order.\_get\_invoiced()

        self.assertTrue(any(inv.state \== 'draft' for inv in invoices))

    

    def test\_postcondition\_stock\_reserved(self):

        initial\_stock \= self.\_get\_total\_available\_stock()

        self.order.action\_confirm()

        self.assertLess(self.\_get\_total\_available\_stock(), initial\_stock)

Each extension registers a concrete subclass that activates the contract tests:

\# modules/custom\_sale/tests/test\_custom\_sale\_contract.py

from odoo.addons.contracts.tests.test\_sale\_order\_confirm\_contract import (

    SaleOrderConfirmContract

)

class TestCustomSaleContract(SaleOrderConfirmContract):

    """Verifies that custom\_sale.action\_confirm() respects the base contract."""

    \# Nothing else needed; it inherits the tests

When a new extension is added, it is enough to create its subclass and the contract tests run automatically. It is exactly the same principle as the `parametrize` in generic CDAD, adapted to Odoo's inheritance.

*Granular permissions for sub-agents.*

"odoo-test-writer": {

  "permissions": {

    "edit": \["modules/\*/tests/\*\*"\],

    "read": \[

      "docs/specs/\*\*",

      "modules/\*/models/\*\*",  // needs to see signatures and inheritance, not implementation

      "modules/\*/\_\_manifest\_\_.py",

      "modules/\*/tests/\*\*"

    \],

    "deny\_edit": \["modules/\*/models/\*\*", "modules/\*/views/\*\*", "modules/\*/data/\*\*"\]

  }

},

"odoo-implementer": {

  "permissions": {

    "edit": \["modules/\*/models/\*\*", "modules/\*/wizards/\*\*"\],

    "read": \[

      "docs/specs/\*\*",

      "modules/\*/tests/\*\*",

      "modules/\*/models/\*\*",

      "modules/\*/\_\_manifest\_\_.py"

    \],

    "deny\_edit": \["modules/\*/tests/\*\*", "modules/\*/\_\_manifest\_\_.py"\]

  }

}

Note that the implementer has `deny_edit` on the manifest: manifest changes are structural decisions that require your explicit approval, the agent does not make them on its own.

*Operational adaptations.*

- The project's AGENTS.md includes a "Odoo conventions" section with: how to name fields (`x_` for custom, `name` for descriptive), how to organize modules, when to use `_inherit` vs `_inherits` vs delegation, which core methods are safe to extend and which are not.  
- The `docs/landscape.md` maps the specific Odoo version in use, installed OCA modules, client customizations that affect the core, and hosting decisions (Odoo.sh, on-premise, Docker).  
- Tests use `TransactionCase` by default (automatic rollback) and only `HttpCase` when the flow really requires HTTP (controllers or JS widgets).

### 11.3 Case study 2 — Django

Django is a Python web framework with a "batteries included" philosophy: its own ORM (based on active record with managers), a system of modular apps, middleware, signals, a template system, an automatically generated admin, built-in authentication. The adoption curve is smoother than Odoo's, but it shares many of the same tensions with generic CDAD.

**What breaks the assumptions.**

- Models inherit from `models.Model` and carry DB coupling by construction. Wanting a pure domain and a separate persistence layer is swimming against the current.  
- The views (in the Django sense: controllers) have direct access to the request, the models, the ORM, the session, everything. Applying strict hexagonal architecture means fighting the convention.  
- Tests use `django.test.TestCase` with its own lifecycle (transactional rollback, fixtures, test client). Pure pytest works but requires `pytest-django`.

**Recommended adaptations.**

*Specific QA tools:*

- **`django-stubs`** for mypy: adds Django-specific type hints (QuerySets, Managers, fields). Without this, mypy does not detect common errors like calling `.filter()` on something that is not a Manager.  
- **`pylint-django`**: the analog of `pylint-odoo`. Detects framework-specific problems: fields without `verbose_name`, models without `__str__`, badly configured `Meta`.  
- **`django-test-plus`**: extends the tests with specific assertions (status assertions, redirect assertions, template contexts).

*Verifiable contracts as parameterized tests over managers or views.* Pattern analogous to Odoo's:

\# core/tests/contracts/test\_search\_manager\_contract.py

from django.test import TestCase

class SearchManagerContract:

    """Contract: any Manager implementing .search(query) must comply.

    

    Concrete subclasses: one per model that has search.

    """

    model\_class \= None  \# subclass sets it

    

    def setUp(self):

        super().setUp()

        self.searchable \= self.model\_class.objects.create(

            name="Test Item Searchable"

        )

        self.not\_searchable \= self.model\_class.objects.create(

            name="Different content"

        )

    

    def test\_search\_finds\_matching(self):

        results \= self.model\_class.objects.search("Searchable")

        self.assertIn(self.searchable, results)

    

    def test\_search\_excludes\_non\_matching(self):

        results \= self.model\_class.objects.search("Searchable")

        self.assertNotIn(self.not\_searchable, results)

    

    def test\_search\_empty\_query\_returns\_all(self):

        results \= self.model\_class.objects.search("")

        self.assertEqual(results.count(), 2\)

class ProductSearchContractTest(SearchManagerContract, TestCase):

    model\_class \= Product

class CategorySearchContractTest(SearchManagerContract, TestCase):

    model\_class \= Category

*Adapted boundaries.* Although you cannot enforce pure hexagonal architecture, you can enforce reasonable rules with `import-linter` (yes, it works in Django with care):

\[importlinter\]

root\_package \= myproject

\[importlinter:contract:1\]

name \= no-cross-app-imports

type \= forbidden

source\_modules \= myproject.apps.billing

forbidden\_modules \= myproject.apps.inventory.models, myproject.apps.users.models

\# forces apps to communicate via services or signals, not direct imports

\[importlinter:contract:2\]

name \= views-no-orm-direct

type \= forbidden

source\_modules \= myproject.apps.\*.views

forbidden\_modules \= django.db.models

\# forces views to use managers/services, not direct .filter()

*Granular permissions for sub-agents.*

"django-test-writer": {

  "permissions": {

    "edit": \["myproject/apps/\*/tests/\*\*"\],

    "read": \[

      "docs/specs/\*\*",

      "myproject/apps/\*/models.py",  // see schema, not view logic

      "myproject/apps/\*/serializers.py",

      "myproject/apps/\*/tests/\*\*"

    \],

    "deny\_edit": \["myproject/apps/\*/views.py", "myproject/apps/\*/services/\*\*"\]

  }

}

### 11.4 Case study 3 — Ruby on Rails

Rails is a Ruby web framework with the most extreme "convention over configuration" philosophy: ActiveRecord as ORM, RESTful controllers by convention, model callbacks, concerns for mixins, and a strong culture of metaprogramming. CDAD applies perfectly, but requires the greatest adaptations because the framework embraces patterns (callbacks, monkey-patching) that you would avoid in generic CDAD.

**What breaks the assumptions.**

- ActiveRecord couples model and persistence to the extreme. The whole domain "lives" in `app/models/`.  
- Callbacks (`before_save`, `after_create`) introduce logic that runs automatically and does not appear explicitly in the tests unless you look for it.  
- `class_eval` and class reopening make it possible for the "definition of a model" to be spread across five different files, all implicitly loaded.  
- Tests use Minitest or RSpec with fixtures (static) or factories (FactoryBot). Richer setup, different semantics from pytest.

**Recommended adaptations.**

*Specific QA tools:*

- **`rubocop-rails`**: linter with Rails-specific cops. Detects heavy callbacks, N+1 queries, badly written validations, reversible migrations.  
- **`brakeman`**: Rails-specific static security analysis. Detects SQL injection, mass assignment vulnerabilities, command injection.  
- **`bullet`**: detects N+1 queries at runtime during the tests.  
- **`sorbet` or `rbs`**: gradual type checking for Ruby; conceptual equivalent of mypy.

*Verifiable contracts as shared examples (RSpec) or test modules (Minitest).* Analogous pattern:

\# spec/contracts/billable\_contract\_spec.rb

RSpec.shared\_examples "a billable resource" do

  \# Contract: any model including the Billable concern must comply

  

  it "responds to \#total\_amount" do

    expect(subject).to respond\_to(:total\_amount)

  end

  

  it "\#total\_amount is non-negative" do

    expect(subject.total\_amount).to be \>= 0

  end

  

  it "transitions to :paid when payment is recorded" do

    subject.record\_payment(amount: subject.total\_amount)

    expect(subject.payment\_state).to eq("paid")

  end

end

\# spec/models/invoice\_spec.rb

RSpec.describe Invoice do

  it\_behaves\_like "a billable resource" do

    subject { create(:invoice, :with\_lines) }

  end

end

\# spec/models/subscription\_spec.rb

RSpec.describe Subscription do

  it\_behaves\_like "a billable resource" do

    subject { create(:subscription, :active) }

  end

end

*Boundaries with packwerk.* Rails has its own equivalent of `import-linter`: `packwerk` (from Shopify), which enforces boundaries between "packages" of the monolith. It is essential when the project grows beyond a few dozen models.

*Operational adaptations.*

- Model callbacks are documented explicitly in the feature's spec: if a postcondition is satisfied by an `after_save`, the spec must say so. This prevents the implementer from adding an "invisible" callback the reviewer does not detect.  
- Migrations are always made reversible (symmetric `change` or `up`/`down`), enforced by `rubocop-rails`.  
- Tests use FactoryBot with explicit factories; global fixtures are avoided because they couple tests that should be independent.

### 11.5 Case study 4 — Webmin

Webmin is a server administration tool written in Perl, distributed under a BSD-like license, with a module system where each module administers one system service (Apache, BIND, MySQL, Unix users, disk quotas, etc.). Its architecture is very different from the three previous cases: it has no ORM (the "data" are the operating system's configuration files), its extension mechanism is modules with a well-defined directory structure, and most of the "logic" are CGI scripts that render HTML and manipulate system files. The typical use of CDAD here appears when a sysadmin or team builds custom Webmin modules to administer their own services or client-specific configurations.

**What breaks the assumptions of the standard document.**

- Perl as the main language: the tooling ecosystem is mature but different from Python's, Ruby's or Java's. Static typing techniques are available (`Type::Tiny`, `Moose` with type constraints) but are not the cultural norm.  
- There is no ORM or model layer: the "domain" is configuration files (`/etc/apache2/apache2.conf`, `/etc/bind/named.conf`, etc.) that get parsed, modified and rewritten. The "entities" are Perl functions that abstract these files.  
- Extension mechanism by directory structure: each module is a directory with `.cgi` files (actions), `*-lib.pl` (shared libraries), `module.info` (metadata), `config-*` (per-OS configuration), and translation files in `lang/`. There is no `_inherit`-style inheritance; you extend by overriding or adding files.  
- Elevated privileges by construction: Webmin runs as root (or with extensive sudo). Any bug is potentially a serious security risk. This raises the cost of error and, therefore, the observable matrix of section 1.4 almost always scores high for Webmin modules.

**Recommended adaptations.**

*Essential QA tools:*

- **`Perl::Critic`** with a strict profile (`--severity 1`): a generic Perl linter with hundreds of policies. It is not Webmin-specific but is the closest equivalent. It allows custom policies written in Perl that can enforce project-specific conventions (e.g. forbid `system()` without argument escaping, forbid `open` without three arguments, etc.).  
- **`Perl::Tidy`** for consistent formatting.  
- **`Devel::Cover`** for test coverage.  
- **Custom `Perl::Critic` policies for Webmin-specific conventions.** This fulfills the role that `pylint-odoo` fulfills in Odoo: it is where you encapsulate the knowledge of the framework. For example, a custom policy that forbids reading configuration files without going through the `lock_file`/`unlock_file` functions of Webmin's library (`web-lib-funcs.pl`), or that verifies any `.cgi` file starts with the standard initialization (`require './something-lib.pl'; &init_config(); &ReadParse();`).

\# .perlcriticrc of the project

severity \= 1

verbose \= 8

\[Subroutines::ProhibitBuiltinHomonyms\]

\[InputOutput::ProhibitTwoArgOpen\]

\[InputOutput::RequireBriefOpen\]

\[Subroutines::RequireFinalReturn\]

\[ValuesAndExpressions::ProhibitInterpolationOfLiterals\]

\# Custom policies (in lib/Perl/Critic/Policy/Webmin/)

\[Webmin::RequireLockFileForConfig\]

\[Webmin::RequireInitConfigInCgi\]

\[Webmin::ProhibitDirectSystemCall\]

*Verifiable contracts as parameterized tests over configuration files.* Instead of `Protocol` or inheritance, you express the contract as a test verifying that any module function that parses/serializes configuration files respects the round-trip:

\# t/contracts/config\_roundtrip.t

use strict;

use warnings;

use Test::More;

use File::Temp qw(tempfile);

\# Any module that parses config files must register its pair

\# (parser, serializer) in this array

my @config\_handlers \= (

    {

        name      \=\> 'apache\_vhost',

        parser    \=\> \\\&apache::parse\_vhost,

        serializer \=\> \\\&apache::serialize\_vhost,

        sample    \=\> "t/fixtures/apache\_vhost\_sample.conf",

    },

    {

        name      \=\> 'bind\_zone',

        parser    \=\> \\\&bind8::parse\_zone,

        serializer \=\> \\\&bind8::serialize\_zone,

        sample    \=\> "t/fixtures/bind\_zone\_sample.conf",

    },

    \# ... you add handlers as modules show up

);

for my $handler (@config\_handlers) {

    subtest "round-trip for $handler-\>{name}" \=\> sub {

        my $original \= read\_file($handler-\>{sample});

        my $parsed \= $handler-\>{parser}-\>($original);

        my $serialized \= $handler-\>{serializer}-\>($parsed);

        my $reparsed \= $handler-\>{parser}-\>($serialized);

        is\_deeply($parsed, $reparsed,

            "parse(serialize(parse(x))) \== parse(x) for $handler-\>{name}");

    };

}

done\_testing();

When a new module handling a new config format is added, you register the handler in the array and the contract tests run automatically. It is the same principle you saw in the other cases, adapted to the Perl/Webmin idiosyncrasy.

*Granular permissions for sub-agents.*

"webmin-test-writer": {

  "permissions": {

    "edit": \["modules/\*/t/\*\*", "modules/\*/tests/\*\*"\],

    "read": \[

      "docs/specs/\*\*",

      "modules/\*/\*-lib.pl",  // see library signatures, not implementation

      "modules/\*/module.info",

      "modules/\*/t/\*\*",

      "t/fixtures/\*\*"

    \],

    "deny\_edit": \[

      "modules/\*/\*.cgi",

      "modules/\*/\*-lib.pl",

      "modules/\*/module.info",

      "modules/\*/config-\*"

    \]

  }

},

"webmin-implementer": {

  "permissions": {

    "edit": \[

      "modules/\*/\*.cgi",

      "modules/\*/\*-lib.pl",

      "modules/\*/lang/\*\*"

    \],

    "read": \[

      "docs/specs/\*\*",

      "modules/\*/t/\*\*",

      "modules/\*/\*-lib.pl",

      "modules/\*/module.info"

    \],

    "deny\_edit": \[

      "modules/\*/t/\*\*",

      "modules/\*/module.info",

      "modules/\*/config-\*"

    \]

  }

}

As with the manifest in Odoo, here `module.info` and the `config-*` files (per-operating-system configuration) are structural decisions that require your approval: the implementer does not touch them on its own.

*Specific operational adaptations.*

- **Security tests as first-class citizens.** Given that Webmin runs with elevated privileges, each new or modified module must have at least one test verifying: (a) that user inputs are escaped before being passed to `system()` or used to build shell commands, (b) that Webmin's ACL system is respected (`&foreign_available()` and `&can_access_*()`), (c) that `&lock_file()` is used before modifying system files.  
- **The project's AGENTS.md** includes a "Webmin conventions" section with: how to name functions (`module_name::function_name`), mandatory use of `&error()` to terminate with an error, use of `ui_*` to generate HTML (not inline), internationalization pattern with `&text()` and `lang/` files.  
- **The `docs/landscape.md`** maps the specific Webmin version in use (the APIs of `web-lib-funcs.pl` change between majors), core modules you depend on, and the target operating system (the service manipulation functions change between Debian/RedHat/BSD).  
- **Spec with focus on idempotence.** The operations of a Webmin module typically modify the operating system's state. Specs must make explicit the idempotence postcondition ("running the action twice produces the same final state as running it once"), and the tests must verify it.

**Note: why Webmin is a particularly clear case of the matrix in section 1.4.**

Almost any feature of a Webmin module scores high on the three axes: long lifespan (the modules are maintained for years), high bug cost (root privileges), high probability of evolution (the services it administers evolve). It is practically always "full CDAD" territory according to the matrix. This makes Webmin a good reminder that the matrix is not only for deciding whether to lower the rigor; it also confirms when to apply it in full.

### 11.6 General heuristic for uncovered frameworks

If you work with a free framework the document does not explicitly cover (Spring Boot, Laravel, WordPress, Drupal, Plone, NestJS, ASP.NET Core with Mono, etc.), the heuristic for adapting CDAD is the following:

1. **Identify the framework-specific linter.** Almost all opinionated frameworks have a tool analogous to `pylint-odoo`/`pylint-django`/`rubocop-rails`/custom `Perl::Critic` policies. For Spring Boot: `spring-javaformat` \+ `archunit`. For Laravel: `larastan` \+ `php-cs-fixer` with the Laravel preset. For WordPress: `phpcs` with `WordPress-Coding-Standards`. For Drupal: `drupal-check` \+ PHPStan-specific rules. For Plone: `plone.recipe.codeanalysis`. This tool fulfills the role of `import-linter` in generic CDAD: it is not optional.  
     
2. **Identify the framework's native extension mechanism.** In Odoo it is `_inherit`, in Rails it is concerns and callbacks, in Django it is signals and middleware, in Webmin it is directory structure \+ shared libraries, in Spring it is `@Configuration` and AOP, in WordPress it is hooks/filters, in Drupal it is hooks. The "verifiable contract" materializes as parameterized tests over extensions of that mechanism, not as a formal `Protocol`.  
     
3. **Identify the framework's base testing classes.** TransactionCase/HttpCase in Odoo, Django's TestCase, ActiveSupport::TestCase in Rails, Test::More \+ the project's modules in Webmin/Perl, `@SpringBootTest` in Spring, `TestCase` with `RefreshDatabase` in Laravel, `WP_UnitTestCase` in WordPress. Your tests inherit from those classes or use those modules; they are not the language's "pure" tests.  
     
4. **Adapt the sub-agent permissions to the framework's structure.** The separations that fulfill the "test-writer does not see the implementation" principle materialize according to the framework. In Spring: `test-writer` sees interfaces and `@Service` signatures but not `@Service` bodies. In Laravel: it sees `App\Models` and signatures of `App\Services` but not `app/Services/*` bodies. In WordPress: it sees hook declarations (`add_action`/`add_filter`) registered but not the callbacks implementing the logic.  
     
5. **Keep the principles intact.** Spec before code, isolated sessions, TDD with the Iron Law, persistent Memory Bank, two-layer review, the five-stage cycle. What adapts is always the technical materialization, never the principle.

**For advanced readers — When the framework makes a principle impossible**

There are cases where a CDAD principle genuinely cannot be applied in full. Common example in free software: on platforms like Drupal with its exportable configuration system (`config/sync/`), or WordPress with the Customizer and the visual Block Patterns, much of the presentation and workflow "logic" is not code but declarative configuration serialized in YAML, JSON or database entries. There is no clean way to apply TDD over that configuration as if it were code. The right answer is not to abandon CDAD; it is to apply it where the framework allows it (custom modules, hooks, services, PHP/Python/Perl code) and accept that the declarative part requires other techniques: structured manual testing with regression scripts, change sets reviewed by peers, sandboxes with regression data replayed automatically. The document prefers this pragmatism to a purism that is not applicable. What matters is not using the existence of declarative parts as an excuse to relax CDAD in the parts that are code.

**Self-assessment quiz**

1. Why is `pylint-odoo` (or the equivalent of the framework you use) not optional on projects over opinionated frameworks?  
2. How is a verifiable contract materialized in Rails without a formal `Protocol` or `interface`?  
3. Which CDAD principles stay intact when moving to an opinionated framework, and which require adaptation?

View answers 

1. Because it fulfills the role that `import-linter` fulfills in generic projects: automatically enforcing the framework's structural rules the AI agent does not know by trade (fields without string, missing translations, unsafe queries, badly defined manifest, etc.). Without that tool, the principle of "structural barriers that do not require human attention" weakens: many framework rules end up depending on the reviewer's judgment, which gets tired and lets things slip.  
     
2. Through `shared examples` in RSpec or shared test modules in Minitest. You define a set of parameterized tests that verify postconditions over any model or resource that complies with the contract; each concrete implementation inherits those tests with a specific setup. It is the same principle as `parametrize` in pytest, adapted to the Ruby ecosystem.  
     
3. They stay intact: spec before code (principle 1), persistent Memory Bank (principle 5), the five stages of the cycle, all the documented anti-patterns. They require adaptation: verifiable contracts (principle 2, materialized as parameterized tests over the framework's extension mechanism), isolated sessions (principle 3, the glob permissions are adjusted to the framework's structure), TDD with the Iron Law (principle 4, preserved literally but the ritual of the "test that fails for the right reason" is heavier due to the framework's setup).

---

## 12\. Documented anti-patterns

Anti-patterns are as important as patterns. In this chapter we document the most common mistakes we have seen when adopting CDAD, with the "before" (what is done wrong) and the "after" (how it is done correctly).

### 12.1 Anti-pattern: "one session for everything"

**Symptom.** The developer (you) opens a single session with the agent and asks it to "implement feature X in full, with tests". The agent writes the spec mentally, writes the tests, writes the code, all in the same conversation.

**Why it is problematic.** The agent sees test and implementation at the same time. It naturally aligns them with each other. The resulting tests verify what the code does, not what the spec asks for. If there is a bug in the code, the test does not detect it because it was written for the code.

**How it is done right.** Separate sessions: one for the spec, one for the test-writer, one for the implementer. It changes context, takes you longer, and produces far superior quality.

### 12.2 Anti-pattern: "the test that always passes"

**Symptom.** The test-writer writes a test that passes before the implementation exists. That should raise an alarm, but in the rush, it is taken at face value.

\# ANTI-PATTERN

def test\_parse\_iso\_date():

    result \= parse\_iso\_date("2026-04-29T15:30:00Z")

    assert result is not None  \# this passes with any implementation

**Why it is problematic.** The test verifies nothing concrete. `assert result is not None` passes with any implementation that returns something other than `None`, even an incorrect one.

**How it is done right.**

def test\_parse\_iso\_date():

    result \= parse\_iso\_date("2026-04-29T15:30:00Z")

    expected \= datetime(2026, 4, 29, 15, 30, 0, tzinfo=timezone.utc)

    assert result \== expected

The test compares against a specific expected value. If the code returns something different, it fails with a clear message of what was expected and what was obtained.

### 12.3 Anti-pattern: "implement more than the test asks for"

**Symptom.** The test verifies the single-element case, but the implementer already writes code that handles lists, edge cases, extra validations, optimizations. Just in case.

**Why it is problematic.** The code is not covered by tests. If a bug is in the "extra" part, no one will detect it. Also, it adds complexity that is probably not needed (YAGNI).

**How it is done right.** The implementer writes the minimum code that makes the test pass. The additional functionality arrives when the test that verifies it arrives. This is called "incremental development" in classic TDD and is a central discipline.

### 12.4 Anti-pattern: "the reviewer only reads the code"

**Symptom.** The reviewer receives the diff and evaluates it on its technical merits (it is elegant, follows conventions, etc.) without contrasting it against the spec.

**Why it is problematic.** The code can be technically impeccable and still not solve the right problem. The reviewer's main function is to verify that the code satisfies the spec, not that it is pretty.

**How it is done right.** The reviewer explicitly receives the spec in its context and is asked to report spec divergences as a primary category. Without the spec, the review loses much of its value.

### 12.5 Anti-pattern: "skip Memory Bank because the agent already knows"

**Symptom.** After several productive sessions with an agent on the same project, the developer assumes the agent "already knows" the context and stops updating the Memory Bank.

**Why it is problematic.** Agents have no memory between sessions. What yesterday's session knew is gone. The next session starts from scratch. Without an updated Memory Bank, the agent reinvents the wheel or assumes incorrect things.

**How it is done right.** After each feature, you update `activeContext.md` with the relevant decisions. This 10-20 minute consolidation work pays enormous dividends in future sessions.

### 12.6 Anti-pattern: "the spec is adjusted so the code compiles"

**Symptom.** In the middle of the implementation, the agent finds a case the spec does not contemplate. Instead of pausing, going back to the spec, and updating it, the agent "freely interprets" the spec so that its implementation makes sense.

**Why it is problematic.** The spec stops being the source of truth. The next time someone reads the spec, they will understand something different from what the code does. Consistency between spec and code breaks.

**How it is done right.** When an unconsidered case appears, the implementer pauses, you go back to the spec, update it explicitly, commit the spec change, and only then continue with the implementation. It takes 10 minutes but keeps the consistency.

### 12.7 Anti-pattern: "review optional for small features"

**Symptom.** For small features (a one-field fix, a configuration change), skipping the review "because it is trivial".

**Why it is problematic.** Trivial features are the ones that get the least attention and where most bugs slip in. The cost of review is low (a reviewer agent can review 30 lines in seconds). The benefit of detecting inconsistencies is high.

**How it is done right.** The review is always done, but its depth is proportional to the complexity. For trivial features, the reviewer only verifies there is no regression, that the spec is satisfied, and that there are no security risks. This takes little time.

**Case study: pricing optimization**

Imagine a feature: "calculate the final price applying quantity discounts and customer-category discounts, with priority rules."

Anti-pattern: "it's just a calculation", the developer opens a session, asks the agent to "implement pricing with discounts", the agent writes the spec mentally, code, and a quick test. It works. They merge it.

Three weeks later, accounting detects that for corporate customers with large orders, the discount is being applied twice. The bug got in because the "quick test" verified the simple case (one customer, one purchase), not the compound case.

With CDAD: in the spec, the brainstorm would have asked: "what happens if a customer qualifies for the quantity discount AND the category discount?". The answer would have been "the larger of the two is applied, not the sum". That postcondition would have become a specific test. The implementer agent could not have accumulated discounts without breaking the test.

**Self-assessment quiz**

1. If a test passes before the implementation is written, what three things can be wrong?  
2. Why should the implementer not add functionality the test does not require?  
3. What do you do if in the middle of stage 3 you discover the spec does not contemplate a case?

View answers 

1. (a) The test does not verify what it claims to verify (it is trivial, like `assert result is not None`); (b) the functionality already existed and was not a genuinely new feature; (c) the test has a bug that makes it always pass (e.g. an inverted conditional).  
     
2. For two reasons: (a) the extra functionality is not covered by tests, so bugs there are not detected; (b) it adds complexity that is probably not needed (YAGNI: You Aren't Gonna Need It). The functionality should arrive when the test that verifies it arrives.  
     
3. You pause the implementation. You go back to the spec in stage 2, update it to cover the case, commit it explicitly, and only then go back to stage 3 with the updated spec. Consistency between spec and code is an invariant; never break it for speed.

---

## 13\. Quick reference and glossary

### 13.1 Cycle cheatsheet

┌─────────────────────────────────────────────────────────────────┐

│                     CDAD — Cycle cheatsheet                     │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│  0\. DECISION                                                    │

│     □ Score the task (3-9) on the observable matrix             │

│     □ 3-4 → vibe coding;  5-6 → CDAD light;  7-9 → full         │

│                                                                 │

│  1\. DISCOVERY                                                   │

│     □ Map relevant APIs/hooks                                   │

│     □ Document in docs/landscape.md                             │

│                                                                 │

│  2\. SPEC                                                        │

│     □ Socratic brainstorm with the architect                    │

│     □ Write docs/specs/NNN-feature/spec.md                      │

│     □ Explicit postconditions \+ acceptance criteria             │

│     □ Human approval mandatory                                  │

│                                                                 │

│  3\. ANTI-GAMING TDD                                             │

│     □ Identify orthogonal postconditions to group               │

│     □ Session 1 (test-writer): failing test                     │

│     □ Verify failure for the right reason                       │

│     □ Session 2 (implementer): minimal code, test passes        │

│     □ Session 3 (refactorer): improve keeping green             │

│     □ Session 4 (test-writer): property tests if applicable     │

│     □ Session 5 (test-writer): E2E tests from accept. criteria  │

│                                                                 │

│  4\. REVIEW TWO-LAYER                                            │

│     □ Reviewer session (different model from the implementer)   │

│     □ Prioritized report: blocking / optional                   │

│     □ Human validation of the prioritization                    │

│     □ If there are blocking findings: go back to stage 3        │

│                                                                 │

│  5\. MERGE \+ MEMORY BANK                                         │

│     □ Full CI passes: lint, types, imports, tests, contracts    │

│     □ Merge to main                                             │

│     □ Scribe session: drafts the Memory Bank update             │

│     □ Validate/edit and commit with the docs(memory): prefix    │

│     □ Create an ADR if there was an architectural decision      │

│                                                                 │

└─────────────────────────────────────────────────────────────────┘

### 13.2 Checklist before each feature

Before starting a feature, check:

- [ ] The Memory Bank is up to date with the current state (last feature reflected)  
- [ ] The QA tools are configured and passing on main  
- [ ] The root AGENTS.md is up to date with current conventions  
- [ ] The sub-agents are configured with their correct permissions  
- [ ] The landscape.md covers the area of code you are going to touch (if not, per-feature discovery)

### 13.3 Checklist at the end of a feature

Before closing the feature as done:

- [ ] All tests pass locally and in CI  
- [ ] The review was done and the blocking findings resolved  
- [ ] The approved spec is in the repo and reflects what was implemented  
- [ ] `docs/activeContext.md` was updated with the feature's entry  
- [ ] `docs/progress.md` reflects the new state  
- [ ] If there was an architectural decision, an ADR was created  
- [ ] The branch is merged and the PR closed  
- [ ] Active agent sessions were closed (do not reuse for the next feature)

### 13.4 Glossary

**ADR (Architecture Decision Record).** Document that captures an architectural decision, its context, alternatives considered, decision made, and consequences. Immutable once accepted; if the decision is revisited, a new ADR is created that supersedes the previous one.

**Anti-gaming (TDD).** Variant of TDD where the separation between who writes the test and who writes the code is structural (sub-agents with limited permissions), not merely disciplinary. Designed to mitigate the tendency of LLM models to align test and implementation.

**Architectural boundaries.** Rules about which modules may import from which. Enforced automatically by tools like import-linter (Python), dependency-cruiser (TypeScript), ArchUnit (Java), packwerk (Rails). In opinionated frameworks, they are frequently delegated to framework-specific QA tools (pylint-odoo, pylint-django, rubocop-rails).

**Socratic brainstorm.** Conversation with an architect agent in plan-only mode where the agent formulates questions to clarify the feature before writing the spec. Analogous to the philosophical Socratic method, adapted to software development.

**CDAD (Contract-Driven AI Development).** The methodology this document describes.

**CDAD light.** Reduced variant of CDAD for tasks scoring 5-6 on the observable activation matrix: brief spec, TDD with isolated sessions for critical components, optional review, Memory Bank if the project already has one.

**Contract test.** Parameterized test that verifies the postconditions of a Protocol/interface against all its registered implementations. When a new implementation is added, it is automatically covered without additional tests. In opinionated frameworks, it materializes as `shared examples` (RSpec), shared test modules (Minitest), or parameterized TestCase base classes (Odoo, Django).

**E2E outside-in mode.** Mode of E2E testing where the full-flow test is written first (before the unit tests) and stays red during the whole implementation cycle, until the individual pieces connect. It gives a continuous progress metric of the feature.

**E2E closure mode.** Mode of E2E testing where the flow test is written after the units are green, as a final verification of correct assembly before the merge. Operationally simpler; loses the continuous metric.

**Opinionated frameworks.** Frameworks that impose a specific way of organizing code, their own extension mechanisms, an ORM coupled to the model (when applicable), and provided testing infrastructure. Examples: Odoo, Django, Rails, Webmin, WordPress, Drupal, Spring Boot, Laravel. CDAD applies with point adaptations (chapter 11).

**Hosting-agnostic.** Property of a software module of working across different hosting environments without depending on one's specific conventions. Important on projects where the code will be distributed to clients with diverse setups.

**Implementer.** Sub-agent with edit permissions on implementation code, without permissions on tests. Its task is to make the existing tests pass with minimal code.

**Import-linter.** Python tool that enforces contracts over imports (which module may import from which). Equivalents exist in other languages under different names.

**Iron Law (TDD).** Absolute rule: never write implementation code without first having a test that fails for the right reason. No exceptions, no shortcuts.

**Observable activation matrix.** Decision tool (section 1.4) that scores a task on three axes (lifespan, bug cost, probability of evolution) and suggests the level of CDAD to apply: vibe coding, light, or full.

**Memory Bank.** Set of versioned files (`projectbrief.md`, `activeContext.md`, `progress.md`, `adr/*`, `specs/*`) that capture the state of the project and are loaded at the start of each agent session.

**Orthogonal postconditions.** Postconditions implemented in independent code paths, without overlapping each other. They can be grouped in the same RED-GREEN-REFACTOR cycle to speed up development without losing the safety net. Contrast with coupled postconditions, which require separate cycles.

**Property test.** Test that verifies a general property (invariant) over all valid inputs, generating random inputs automatically. It detects edge cases that deterministic tests may not find.

**Protocol (Python).** Structural typing mechanism that defines an interface by the set of methods a class has, without requiring explicit inheritance. It enables verifiable contracts. Equivalents: TypeScript `interface` with `satisfies`, Java `interface`, Go `interface`, Rust `trait`.

**pylint-odoo.** Pylint plugin maintained by the OCA (Odoo Community Association) with checks specific to Odoo. In Odoo projects it fulfills the role that `import-linter` fulfills in generic projects: enforcing structural rules the AI agent does not know by trade.

**Refactorer.** Sub-agent whose task is to improve existing code (readability, consistency, simplicity) without changing observable behavior. All tests must keep passing after the refactor.

**Reviewer.** Read-only sub-agent that evaluates a full diff against the spec and produces a prioritized report of findings. Ideally it uses a different model from the implementer.

**Scribe.** Read-only sub-agent whose task is to draft the Memory Bank update after a merged PR: proposed entry for `activeContext.md`, changes for `progress.md`, and a possible draft ADR. The human validates and commits. It reduces the friction of the Memory Bank update from 15-20 minutes to 3-5 minutes per feature.

**Isolated session.** Conversation with an agent that does NOT share context with other sessions. Used in CDAD to force the separation of phases (the test-writer does not see code, the implementer does not see the test-writer's reasoning).

**Sub-agent.** Configuration of an agent with specific permissions (which files it can read/edit), specific instructions, and eventually a specific model. It makes it possible to materialize the isolated sessions principle.

**Test-writer.** Sub-agent with edit permissions only on `tests/`, without permissions on implementation code. Its task is to write tests that verify the spec and initially fail because there is no implementation.

**Vibe coding.** Anti-CDAD pattern where the agent is asked to "implement X" without a prior spec, without separation of phases, without verifiable contracts. It works for small tasks but does not produce sustainable quality for serious projects.

### 13.5 Resources for going deeper

**Classic TDD.**

- Kent Beck — *Test-Driven Development by Example* (foundational book)  
- James Shore — *The Art of Agile Development* (chapter on practical TDD)

**Domain-Driven Design (complementary to CDAD).**

- Eric Evans — *Domain-Driven Design* (foundational book)  
- Vaughn Vernon — *Implementing Domain-Driven Design* (more practical)

**Property-based testing.**

- David MacIver — Hypothesis documentation (Python)  
- Scott Wlaschin — *Domain Modeling Made Functional* (includes PBT in F\#)

**Clean Architecture and boundaries.**

- Robert Martin — *Clean Architecture* (chapters on layers and boundaries)  
- Vladimir Khorikov — *Unit Testing Principles, Practices, and Patterns*

**Architecture Decision Records.**

- Michael Nygard — original article on ADRs (2011)  
- adr.github.io — consolidated pattern and templates

**Working with AI agents.**

- Anthropic — guides on prompt engineering and working with Claude  
- Documentation of tools: Claude Code, OpenCode, Cursor, Aider

---

## Closing

CDAD is born from a pragmatic observation: AI agents are useful but unpredictable, and the only way to obtain sustainable quality when working with them is to introduce structural discipline that does not depend on the consistency of the underlying model. The five foundational principles (spec before code, verifiable contracts, isolated sessions with granular permissions, TDD with the Iron Law, persistent Memory Bank) materialize in a five-stage cycle (discovery, specification, anti-gaming TDD, two-layer review, merge with Memory Bank) applied feature by feature.

The initial discipline is real: configuring tools, writing specs, separating sessions, maintaining the Memory Bank. But the discipline pays growing dividends as the project advances: future features are faster because the context is consolidated, bugs are rarer because the structural barriers detect them early, scope changes are more manageable because the spec is the source of truth. The learning curve is a few days for the concepts and a few weeks for the cycle to feel natural.

The document you are reading is version 1.0 of CDAD. The methodology will evolve with experience and with the evolution of the tools. The foundational principles are robust, but the concrete materialization (which tools, which specific patterns) will be refined. If you use it and discover improvements, it is worth documenting and sharing them.

Good luck with your next project.

---

**About the version.** Document v1.1, written in April 2026\. Revision 1.1 incorporates: the observable activation matrix of CDAD (1.4), manual fallback variants when the orchestrator does not support granular permissions (2.3), grouping of orthogonal postconditions (7.1), an explicit sub-phase of integration / E2E tests (7.6), the Scribe pattern to assist the Memory Bank update (9.2), and a new chapter on adapting CDAD to opinionated frameworks with case studies in Odoo (Python), Django (Python), Rails (Ruby) and Webmin (Perl) (chapter 11). All the examples in the document correspond to free software.  
