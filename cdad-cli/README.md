# CDAD-CLI: Contract-Driven AI Development Command-Line Interface

A pure Python CLI that orchestrates the CDAD workflow without any editor or IDE dependency.

**Status**: MVP (Phase 1 - Core agents + CLI)

## What is CDAD-CLI?

CDAD-CLI implements Contract-Driven AI Development: a disciplined methodology for working with AI agents to build software iteratively using specs, tests, and automated validation.

## Installation

```bash
pip install -e ".[dev]"
pre-commit install
```

## MVP Commands

The four core commands for Contract-Driven Development:

```bash
# 1. Initialize a CDAD project
cdad init --name my-project

# 2. Generate a spec from a feature description
cdad discover --feature "Add user authentication"
cdad spec --name user-auth

# 3. Analyze existing code and get recommendations
cdad architect src/auth.py

# 4. Generate failing tests from a spec
cdad test user-auth
```

## Full Workflow

```bash
# Discovery & Spec phases
cdad discover --feature "Feature description"
cdad spec --name feature-name

# RED phase: Write/generate failing tests
cdad test feature-name
cdad red

# GREEN phase: Implement to make tests pass
# (edit implementation files)
cdad green

# Architecture review (optional)
cdad architect src/module.py

# Status & management
cdad status
cdad review
cdad merge
```

## Development

This project itself is developed using CDAD. See `AGENTS.md` for development workflow and memory bank context.

## Architecture

See `docs/architecture.md` for detailed design and `docs/extending-agents.md` for how to add new agents.

## Testing

```bash
pytest
pytest --cov=src/cdad
```

## Code Quality

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Quick Start After Extraction

1. Extract this ZIP file
2. `cd cdad-cli` (or whatever directory name you used)
3. `pip install -e ".[dev]"`
4. `pre-commit install`
5. Open the project in Claude Code with the provided `CLAUDE_CODE_PROMPT.md`
