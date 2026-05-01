# CDAD-CLI Architecture

## High-Level Flow

```
User Input (CLI command)
    ↓
CLI Interface (Typer)
    ↓
PhaseManager (detect current state)
    ↓
Agent Invocation (isolated session)
    ↓
LLMClient (Anthropic API)
    ↓
ProjectModel (read/understand codebase)
    ↓
Validators (check constraints)
    ↓
File I/O (write specs, tests, code)
    ↓
User Output (status report)
```

## Layer Responsibilities

### CLI Layer (`src/cdad/cli/`)

- Parses command-line arguments (using Typer)
- Validates input (e.g., feature name must be non-empty)
- Delegates to orchestrator
- Formats output for terminal

### Orchestrator (`src/cdad/orchestrator/`)

- PhaseManager: Detects what phase project is in
- Suggests next command based on current state
- Validates phase transitions

### Agents (`src/cdad/agents/`)

- Base class: Handles common concerns
- Architect: Discovery and spec generation
- TestWriter: Write tests (RED phase)
- Implementer: Write code to pass tests (GREEN phase)
- Reviewer: Compare implementation against spec
- Scribe: Update Memory Bank after merge

Each agent is **isolated**: only sees files relevant to its role.

### Validators (`src/cdad/validators/`)

- SpecValidator: Checks that spec has verifiable postconditions
- TestValidator: Detects RED (tests fail) vs GREEN (tests pass)
- ContractValidator: Generates and runs parametric tests from postconditions

### ProjectModel (`src/cdad/project/`)

- Reads project structure from disk
- Detects framework (generic Python, Odoo addon, Django project)
- Navigates Memory Bank
- Loads and parses specs

### LLMClient (`src/cdad/llm/`)

- Wrapper around Anthropic SDK
- Manages conversation history per session
- Implements retry logic for API calls
