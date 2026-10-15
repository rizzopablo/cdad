# Contract-Driven AI Development (CDAD)

The deterministic role-packet renderer requires **Python 3** and uses only
the Python standard library (stdlib), with no third-party packages or downloads.
After installation its public entrypoint is
`<skill-dir>/scripts/cdad_packet.py` (`<skill-dir>` is the directory of the
loaded `cdad-cycle` skill, as the runtime reports it when the skill is loaded).
Its companion is
the artifact CLI `<skill-dir>/scripts/cdad_result.py`,
which persists and materializes role outputs and records suite evidence (the
interface is owned by the CLI `--help` and the feature spec; each subcommand has
its own usage):

- `receive` — persists the original result bytes and emits a mechanical receipt.
- `validate-receipt` — re-verifies a durable receipt against its stored payload.
- `materialize` — copies receipt parts to authorized canonical targets.
- `run-python-unittest` — runs the supported `python3 -m unittest` runner and emits evidence.
- `validate-run-evidence` — recomputes current snapshots and classifies the run evidence.

The protocol that integrates a finished read-only role's output (receive →
validate-receipt → materialize → state transition) is documented in
[`skills/cdad-cycle/references/re-entry.md`](skills/cdad-cycle/references/re-entry.md).

**A disciplined methodology for building software with AI agents**

---

## Guided project start

A brief instruction is enough to reach a first useful delegation: ask CDAD to
initialize this project and run its preliminary analysis, and it drives the
start from there. The step-by-step procedure lives in
[`skills/cdad-cycle/references/project-start.md`](skills/cdad-cycle/references/project-start.md);
that reference is the single owner of the guided start and is not reproduced here.

---

## What is CDAD?

CDAD is a software development methodology designed specifically to work with AI agents as implementers. It solves a fundamental problem: language models are brilliant but inconsistent. They can produce excellent or defective code, and the difference is often not predictable.

Instead of relying on post-hoc, exhausting human review, **CDAD inserts structural barriers before and during the implementation process**. These barriers are automated and guarantee that the agent is never the only one responsible for verifying that its work is correct.

---

## The Five Foundational Principles

CDAD rests on five structural principles that form the backbone of the methodology:

### 1. **Spec before code (always)**
Before any agent touches a single line of implementation code, a written document must exist that defines what the feature does, with verifiable contracts included.

### 2. **Verifiable contracts as the guardian**
The contracts between components are defined as formal types (interfaces, protocols, traits) with explicit postconditions, verified automatically through parameterized contract tests.

### 3. **Separate role contexts with supervised autonomy**
Roles work in separate sessions with clear contracts, sufficient capabilities,
and scope appropriate to their task. The orchestrator verifies outcomes and
handles deviations with evidence. Preventive controls protect specific effects
and information boundaries; command allowlists are not a correctness guarantee.

The [supervised-autonomy decision](docs/adr/ADR-011-autonomia-supervisada-limites-proporcionales.md)
defines the target policy. Runtime migration is planned in epic 004; this
principle update does not change installed permissions.

### 4. **TDD with the "Iron Law"**
Implementation code is never written without first having a test that fails for the right reason. No exceptions, no shortcuts, no "I'll add the test later."

### 5. **Persistent Memory Bank**
The project maintains a set of versioned files that capture the current state, the decisions made, the accumulated learnings, and the context for future sessions.

---

## The Cycle: The Five Stages

### 🔍 Stage 1: Discovery
Maps the terrain of the system. Destroys the assumptions the AI model drags along from its training. Generates landscape documentation and technical context.

### 📋 Stage 2: Specification
Socratic brainstorm, spec writing with functional description, contract, invariants and acceptance criteria, and human approval.

### 🧪 Stage 3: Anti-gaming TDD
Separate sub-agents write tests (which fail), implement code (which passes), refactor, and write property tests. All in isolated sessions.

### 👀 Stage 4: Two-Layer Review
A reviewer sub-agent generates a prioritized report of findings. You validate the prioritization before the merge.

### ✅ Stage 5: Merge + Memory Bank
Automated CI validates. You update the Memory Bank with decisions, learnings, and project status.

---

## Complete Documentation

- 📖 **[CDAD_metodologia.md](./CDAD_metodologia.md)** — Complete document with 13 chapters
- 🧑‍🎓  **[NotebookLM CDAD](https://notebooklm.google.com/notebook/c4a9bab2-d26d-49bd-9ec7-50d256ed1dec)** — Resources to facilitate the study of CDAD
- 🎯 **[docs/specs/](./docs/specs/)** — Specification structure
- 🏗️ **[docs/adr/](./docs/adr/)** — Architecture Decision Records
- 📝 **[docs/projectbrief.md](./docs/projectbrief.md)** — Project brief

---

## When is CDAD Worth It?

CDAD has an operational cost. It is not for everything. It is worth it when at least **two of these conditions** are met:

- The code will live a long time (months or years) and will evolve
- Code correctness matters beyond "it compiles and passes tests"
- The project is large enough that no human can keep all the context in mind
- The team will use AI agents as a regular part of the workflow
- Quality must be sustainable in the long run

### Decision Matrix

| Score | Recommended Mode | Application |
|---------|------------------|-----------|
| 3-4 | **Vibe Coding** | No spec, no isolated sessions, no Memory Bank |
| 5-6 | **CDAD Light** | Brief spec, anti-gaming TDD with isolated sessions on critical components |
| 7-9 | **Full CDAD** | All five stages complete, no shortcuts |

---

## Structure of a CDAD Project

```
proyecto/
├── docs/
│   ├── projectbrief.md          # What the project is
│   ├── landscape.md             # Terrain mapping
│   ├── systemPatterns.md        # Technical patterns
│   ├── activeContext.md         # Current state
│   ├── progress.md              # Feature status
│   ├── adr/                     # Architecture Decision Records
│   │   ├── 001-decisión.md
│   │   └── 002-decisión.md
│   └── specs/                   # Versioned specifications
│       ├── 001-feature-a/
│       │   ├── spec.md
│       │   ├── plan.md
│       │   └── tasks.md
│       └── 002-feature-b/
├── src/                         # Implementation
├── tests/                       # Tests
└── .aiignore                    # Permission control for sub-agents
```

---

## Spec: Minimal Structure

Each feature has a spec that follows this structure:

```markdown
# Spec: [feature name]

## Functional description
What it does, in non-technical language.

## Contract (signature and invariants)
Formal types with explicit postconditions.

## Verifiable invariants
That will become property tests.

## Acceptance criteria
Measurable metrics to consider the feature done.

## Out of scope
What it does NOT do, to avoid scope creep.
```

---

## Comparison with Other Methodologies

| Aspect | Vibe Coding | Classic TDD | BDD | DDD | CDAD |
|---------|-------------|-------------|-----|-----|------|
| **Who implements** | Unrestricted agent | Human dev | Human dev | Human dev | Limited sub-agents |
| **Spec before code** | No | Implicit | Yes (Gherkin) | Yes (model) | Yes (markdown) |
| **Tests first** | Sometimes | Yes | Yes | Non-prescriptive | Yes |
| **Formal contracts** | No | Optional | Not central | Yes | Yes |
| **Persistent memory** | No | No | No | Yes (model) | Yes |
| **Long-term quality** | Variable | High with discipline | High | High | Consistently high |
| **Designed for AI agents** | No | Partial | Partial | No | Yes |

---

## Key Operational Rules

✅ **Never skip stages.** Features that look simple frequently reveal ambiguities.

✅ **If a stage fails, you go back to the previous stage.** No further back.

✅ **Human approval at key moments is non-delegable.** You approve the spec, validate the review, evaluate the Memory Bank.

---

## Use Cases

**✅ Use CDAD when:**
- You will use AI agents as the primary implementers
- The code will live months/years and will evolve
- Sustainable quality matters more than initial speed
- You need persistent documentation of decisions

**❌ Do not use CDAD when:**
- You are in pure exploration or prototyping something disposable
- It is a one-off script headed for the trash
- The code has less than a month of expected useful life

---

## Key Differences from Alternatives

### vs. Vibe Coding
CDAD brings structure and quality guarantees that vibe coding does not offer. With agents, no structure = unpredictable code.

### vs. Classic TDD
CDAD + TDD, but with agent separation. The test-writer does not see the implementation. This eliminates the internal-coherence bias that agents naturally have.

### vs. BDD
CDAD is more technical and agent-specific. BDD focuses on communication with non-technical stakeholders.

### vs. DDD
CDAD does not exclude DDD. They can be combined perfectly. CDAD focuses on *how* to implement with agents; DDD focuses on *what* to model.

---

## Next Steps

1. **Read the full document** (`CDAD_metodologia.md`) to understand each stage in depth
2. **Start with CDAD Light** if it is your first project
3. **Set up your Memory Bank** with the structural documents
4. **Set up sub-agents** with clear role contracts, appropriate context and sufficient scoped capabilities
5. **Apply the discipline:** specs before code, always

---

## Per-deploy configuration

The `agents/cdad-*.md` agents are machine-agnostic in the machine they run on:
they do not declare `permission.external_directory` in the repo. Access to directories
outside the workspace (for example, the runtime's skill directories) is
**configuration of each deployment** and is declared in the runtime's
`opencode.jsonc` under `agent.<name>.permission.external_directory`:

```jsonc
{
  "agent": {
    "cdad-architect": {
      "permission": {
        "external_directory": {
          "<abs path to the runtime's skill dir>/**": "allow",
          "<another external dir>/**": "allow",
          "/tmp/opencode/*": "allow"
        }
      }
    }
  }
}
```

Each deployment adds its own `external_directory` (real paths of that
machine) via `opencode.jsonc`; that local config layer is not versioned in the
repo. Note: opencode **does not expand** `${HOME}` nor environment variables in the
`external_directory` patterns — use absolute paths.

---

## License

This repository contains open documentation and methodology for building software with AI agents.

---

**CDAD: Contract-Driven AI Development** — Structural discipline for AI agents that pays off.
