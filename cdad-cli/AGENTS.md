# CDAD-CLI: Memory Bank & Development Context

## Project Brief

**What**: A pure Python CLI that orchestrates Contract-Driven AI Development workflow without editor dependencies.

**Why**: CDAD requires disciplined, structured development with AI agents. Currently bound to OpenCode. We need a standalone orchestrator that can be developed using CDAD itself (self-hosting).

**Who**: Python developers, especially those in Odoo ecosystem who want to adopt CDAD discipline.

**When**: MVP (Phase 0) by end of week 1. Then iterate with CDAD itself (Phase 1+).

**Constraints**: 
- Must be language-agnostic at orchestration level (work with any language's test frameworks, code structures)
- No dependency on OpenCode or any IDE
- Self-bootstrapping: cdad-cli v0.1 develops cdad-cli v0.2 using CDAD

## Architecture Overview

The CLI has these layers (see `docs/architecture.md` for detailed diagrams):

1. **CLI Interface** (`src/cdad/cli/`) — Typer-based commands (init, discover, spec, red, green, review, merge, status)
2. **Orchestrator** (`src/cdad/orchestrator/`) — Phase management and state tracking
3. **Agents** (`src/cdad/agents/`) — Sub-agents (architect, test-writer, implementer, reviewer, scribe)
4. **Validators** (`src/cdad/validators/`) — Contract validation (spec, test RED/GREEN, postconditions)
5. **Project Model** (`src/cdad/project/`) — Project introspection and Memory Bank navigation
6. **LLM Client** (`src/cdad/llm/`) — Wrapper around Anthropic SDK

Session isolation is achieved via **context narrowing** (limiting visible files per agent role) not sandboxing.

## Architecture Decision Records

### ADR-001: Use Python as Implementation Language

**Decision**: Implement cdad-cli in Python.

**Rationale**: 
- Target audience is Python/Odoo developers who already have Python environments
- Native AST parsing for code analysis without external tools
- Seamless pytest integration for test validation
- Mature Anthropic SDK with excellent documentation
- Tests written by agents are naturally compatible with validation

**Alternatives Rejected**:
- Go: Too much infrastructure for I/O-bound CLI; no native Python analysis
- TypeScript: Good tooling but no Python AST parsing; distribution more complex for Python-centric users
- Rust: Compilation overhead during iterative CDAD development; steep learning curve for agents
- Bash: No abstractions; fragile for complex workflow orchestration

### ADR-002: Use Typer for CLI Framework

**Decision**: Use Typer over Click/argparse.

**Rationale**: Cleaner API, automatic help generation, better type integration, native async support when needed.

### ADR-003: Session Isolation via Context Narrowing

**Decision**: Implement agent isolation by limiting accessible files, not OS-level sandboxing.

**Rationale**: 
- Simpler to implement without external tools
- Leverages agent instruction following (epistemic isolation vs technical isolation)
- More transparent to users (they can inspect what files each agent sees)
- Mitigation against agent "cheating": contract validators catch violations

## Current Phase

**Status**: Phase 0 (Manual Bootstrap)

**Timeline**:
- Day 1-2: Project structure + foundational tests
- Day 3-4: ProjectModel + MemoryBank navigation
- Day 5: Validators (SpecValidator, TestValidator, ContractValidator)
- Day 6: LLMClient + Agent base class
- Day 7: CLI scaffolding + architect agent

## Key Files & Responsibilities

- `src/cdad/validators/spec_validator.py` — Validates specs have verifiable postconditions
- `src/cdad/orchestrator/phase_manager.py` — Detects current phase, suggests next command
- `src/cdad/project/model.py` — Reads project structure, detects framework (generic/odoo/django)
- `src/cdad/llm/client.py` — Wraps Anthropic SDK, manages conversation history
- `src/cdad/agents/base.py` — Base class for all agents (architect, test-writer, etc.)
- `tests/test_spec_validator.py` — TDD tests for validators (RED → GREEN cycle)

## Development Workflow (Phase 1+)

Once MVP is working, development follows strict CDAD:

```bash
cdad discover --feature "Implement test-writer agent for Odoo"
cdad spec
cdad red
cdad green
cdad review
cdad merge
cdad status
```

Each command invokes an isolated agent (no context leakage between test-writer and implementer).

## Notes for Claude Code Initialization

When starting Phase 0 development with Claude Code:

1. Start with **test-first approach** — write tests before implementation
2. Keep validators simple but strict — they're the guarantee that agents stay disciplined
3. ProjectModel must understand Odoo, Django, and generic Python projects (used for code analysis)
4. LLMClient should track conversation history per session (important for agent continuity)
5. Each agent subclass documents its system prompt and access rules in docstrings
6. All tests in `tests/` use pytest fixtures; make heavy use of `tmp_path` for file operations
