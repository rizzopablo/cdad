# CDAD repo tooling — declared regeneration entrypoints (004-001 T3).
# The agents/ files are DECLARED OUTPUTS of scripts/cdad-generate.py
# (PD-4/PD-5): never edit them by hand — edit sources/roles/*.md and
# sources/agents/adapters/*.md, then `make agents`.

PY ?= python3

.PHONY: staging agents validate

## staging — generate both runtimes into build/staging/ (reproducible staging)
staging:
	$(PY) scripts/cdad-generate.py --runtime opencode --stack odoo --out build/staging
	$(PY) scripts/cdad-generate.py --runtime claude-code --stack odoo --out build/staging

## agents — promote the staging outputs over the repo agents (declared outputs)
agents: staging
	cp build/staging/agents/opencode/cdad-*.md agents/
	cp build/staging/agents/claude-code/cdad-*.md agents/claude-code/

## validate — the repo validators (epic-002 consistency + odoo specialization)
validate:
	bash tests/validate-consistency.sh
	bash tests/validate-odoo-specialization.sh
