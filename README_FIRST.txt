CDAD-CLI Bootstrap Package
==========================

This ZIP contains the complete initial structure for cdad-cli MVP Phase 0.

EXTRACTION:
1. Extract this ZIP to a directory (e.g., "cdad-cli" or a custom name)
2. cd into that directory
3. Follow the setup instructions below

QUICK START:
1. pip install -e ".[dev]"
2. pre-commit install
3. pytest  (should pass placeholder tests)
4. Open the project in Claude Code with CLAUDE_CODE_PROMPT.md

Or, if you prefer using the bash script:
1. bash init-cdad-cli.sh cdad-cli
2. cd cdad-cli
3. pip install -e ".[dev]"
4. pre-commit install

DIRECTORY STRUCTURE:
- src/cdad/         → Main package
- tests/            → Test files
- docs/             → Documentation
- pyproject.toml    → Project configuration
- AGENTS.md         → Memory Bank for development
- README.md         → Project documentation

For Claude Code initialization, see the CLAUDE_CODE_PROMPT.md file included
separately (not in this ZIP, as it's provided as a separate file).

Good luck with CDAD-CLI development!
