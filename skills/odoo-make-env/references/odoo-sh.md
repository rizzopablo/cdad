# odoo.sh variant of the make contract (public reference — verified 2026-08-28)

> Implementation of the 4 targets on an odoo.sh dev instance. `make lint`
> runs on the host (not inside the instance's runtime — see Lint section).
> No account identifiers: placeholders `<instance>` / `<project>`.

## Environment characteristics (official FAQ + empirical verification)

- A single DB per build: `$PGDATABASE` (PG preconfigured via env vars).
  **No DBs can be created** (`CREATE DATABASE` → permission denied).
- Dev builds **always** include demo data (official policy) → the demo gate
  is exercised without extra configuration.
- No apt; Python deps via `requirements.txt` (installed by the build).
- Dev/staging builds = 1 worker; long-running processes not supported.
- `~/src/user` = worktree of the project's GitHub repo. `scp` fails; use
  `tar` over stdin/SSH. Direct changes are lost on rebuild if not pushed.
- Schema drift possible in dev builds (NOT NULL ghost column):
  the antidote is the platform rebuild.

## Verified Makefile

```makefile
MODULE ?= <module>
DB ?= $(PGDATABASE)

.PHONY: test test-one test-clean lint

test:
	odoo-bin -d $(DB) -u $(MODULE) --test-enable --stop-after-init --workers 0 --max-cron-threads 0 --log-level=test

test-one:
	@test -n "$(TEST)" || (echo "Required: TEST=module:Class.method" && exit 1)
	odoo-bin -d $(DB) -u $(MODULE) --test-enable --test-tags $(TEST) --stop-after-init --workers 0 --max-cron-threads 0 --log-level=test

test-clean:
	psql -q -c "UPDATE ir_module_module SET state='to install' WHERE name='$(MODULE)';"
	odoo-bin -d $(DB) -i $(MODULE) --test-enable --stop-after-init --workers 0 --max-cron-threads 0 --log-level=test

# make lint runs on the HOST (not on the instance): lint is static, no
# platform deps. Pin per the odoo-make-env contract; --all for gate evidence.
lint:
	uvx pre-commit-vauxoo==8.3.18 run --no-overwrite --diff
```

Notes:
- `test-clean` here does NOT create a DB (impossible): "from scratch" =
  state reset + reinstall. The full clean (new DB) is provided by the
  **platform rebuild** on every push.
- It does not use `-c`: the platform's `odoo-bin` wrapper resolves the config.

## Two verification paths

1. **Fast loop (shell)**: write into `~/src/user` (tar|ssh), run the 3
   targets.
2. **Real flow (platform)**: push to the GitHub repo → the build runs its
   automatic battery → result in the project UI. Requires push access to the
   repo (deploy keys/submodules per the official FAQ).

## Lint (pylint-odoo / oca-checks)

Not available on the instance (no apt; the instance's pip does not persist).
Verified decision: run them on the **developer's machine** (tooling venv) —
lint is static and environment-independent. The lint evidence travels with
the feature (pasted output), not with the environment.
