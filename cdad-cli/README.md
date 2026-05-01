# CDAD-CLI: Contract-Driven AI Development Command-Line Interface

A pure Python CLI that orchestrates the CDAD workflow without any editor or IDE dependency.

**Status**: MVP (Phase 0 - Bootstrap)

## What is CDAD-CLI?

CDAD-CLI implements Contract-Driven AI Development: a disciplined methodology for working with AI agents to build software iteratively using specs, tests, and automated validation.

## Installation

```bash
pip install -e ".[dev]"
pre-commit install
```

## Usage

```bash
cdad init --name my-feature
cdad discover --feature "Add user authentication"
cdad spec
cdad red
cdad green
cdad review
cdad merge
cdad status
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
