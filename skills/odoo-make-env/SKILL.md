---
name: "odoo-make-env"
description: >
  Make contract for running Odoo tests on CDAD projects (targets test /
  test-one / test-clean / lint) and a guide for implementing the contract in a
  concrete environment (odoo.sh, private staging, local docker, oca-ci). Use when
  an Odoo project must expose its test runner to the CDAD-Odoo agents, or when
  creating the Makefile of a new Odoo project.
---

# odoo-make-env — Odoo test execution contract

**Principle:** CDAD defines WHAT is verified (gates + evidence); the project
defines HOW (Makefile versioned in the repo). The CDAD-Odoo agents invoke
only the 4 targets — never environment-specific commands.

## The contract (mandatory, exact names)

| Target | Semantics | Used by |
|---|---|---|
| `make test` | full suite on the warm DB | test-writer (AUDIT), implementer (GREEN) |
| `make test-one TEST=mod:Class.method` | a single test | test-writer (RED) |
| `make test-clean` | install the module from scratch + suite | implementer (GREEN gate), reviewer |
| `make test-all` | unified multi-module gate: fresh DB + ONE install + all suites (optional in mono-module; condition: dependency graph in a chain, otherwise `-i mod1,mod2`) | implementer (GREEN closure), reviewer |
| `make lint` | addon lint with `pre-commit-vauxoo` — `--diff` in development, `--all` for gate evidence | implementer (GREEN gate), reviewer |

**Rules:**
1. `test-clean` = "install from scratch" — the mechanism is free per
   environment (new DB if possible; reset+`-i` if not).
2. Runs ALWAYS with `--stop-after-init --test-enable` and without workers
   (`workers = 0`): ephemeral jobs, minimal use of connections.
3. **Demo data:** in Odoo 19 the CLI creates DBs WITHOUT demo
   (`--with-demo` default False, `config.py:233`). In environments that do
   load it (odoo.sh builds), `test-clean` exercises the installation with
   demo — but test fixtures are self-contained ALWAYS (see
   `odoo-test-writer`).
4. Evidence = pasted output with the `0 failed, 0 error(s) of N tests` line.
5. The Makefile is versionable and reviewable — it lives in the project repo.
6. `make lint` invokes the pinned lint `uvx pre-commit-vauxoo==8.3.18` and
   ALWAYS with `--no-overwrite`: the bootstrap of pre-commit configs is the
   project's decision, never the agent's. Autofixes disabled
   (tool default).
7. The lint runs on the host, not inside the test environment's runtime; the
   first run requires network (clones the hook repos).
8. Lint evidence = output of `make lint --all` pasted, with `0`
   blocking.

## How to implement a new environment

**Step 0 — is there an already-resolved environment installed?** This skill
does not depend on any in particular, but if one is available, using it is
faster and more reliable than fabricating the Makefile by hand.

Look, in this order:

1. An installed environment skill (convention: `<something>-env`, e.g.
   `odoo-sandbox-env`) — its `description` declares when it applies. If one
   exists and applies to this project, **load it first** and follow its
   guide: it already brings the verified Makefile, twice as fast as
   fabricating your own.
2. If there is none, the environment's binary might still be available
   without the skill (e.g. `command -v odoo-sandbox`). Uncommon, but check it.
3. **None of the above → generic procedure** (what follows). It is the path
   that always works, for any environment, with or without a dedicated
   skill.

### Generic procedure (without a dedicated environment)

1. Copy `assets/Makefile.template` into the project repo.
2. Resolve the 4 variables: odoo binary, config, test DB, "from scratch"
   mechanism.
3. See the variance table (below) for known environments.
4. Add retry if the postgres is shared (`run_odoo` pattern from the private
   staging template, in that environment's private references).
5. Verify the 4 targets with a minimal module (suggested: `idea_log`).

## Variance per environment (verified empirically)

| Aspect | odoo.sh | private staging | local docker (pattern) | odoo-sandbox (if installed) |
|---|---|---|---|---|
| Create DBs | ❌ only the build's | ✅ CREATEDB | ✅ postgres container | ✅ CREATEDB (or `odoo-bin` creates it itself) |
| `test-clean` | reset `to install` + `-i` | dropdb+createdb+`-i` | dropdb+createdb+`-i` | dropdb+`-i` (Makefile provided) |
| Demo data | always in dev builds | fresh DB initialization | fresh DB initialization | fresh DB initialization |
| Binary | `odoo-bin` wrapper | venv + `odoo-bin -c conf` | `docker compose exec` | `odoo-sandbox exec ... -- odoo-bin` (host) or direct `odoo-bin` (inside an instance) |
| Postgres | dedicated | **shared: retry + low `db_maxconn`** | dedicated | typically shared: connection preflight included |

Details of the odoo.sh variant: `references/odoo-sh.md`. odoo-sandbox brings
its own guide in its own skill (`odoo-sandbox-env`, if installed) —
deliberately it does not live here: it is one environment among several
possible, and CDAD/this skill do not depend on it.

## Known traps (verified 2026-08-28)

1. `-i` on an installed module = no-op (0 tests) → the "from scratch"
   mechanism is mandatory in `test-clean`.
2. Managed dev builds can have schema drift (ghost column) → the antidote is
   a new DB/rebuild; a real `test-clean` detects it.
3. On odoo.sh, `scp`/`sftp` fail: transfer with `tar` over stdin/SSH.
4. `--workers 0` avoids consuming slots from the shared postgres of other
   tenants.
5. **Fresh DB + `-i` runs the at_install tests of ALL dependencies
   (including those of `base`, like `HttpCase`, which open additional HTTP
   connections).** On shared postgres those tests hang. Fix: scope
   `test-clean` with `--test-tags $(MODULE)` to run only the module's tests
   (the dependency installation still happens; only their tests are
   filtered).
6. **Orphan odoo-bin processes retain postgres connections** and can be the
   real cause of "no slots" (a `make` that timed out leaves the `odoo-bin`
   stuck in `connect`). Before retrying: `ps -eo pid,cmd | grep odoo` and
   kill the runner's orphans (NEVER the platform instance's).
   A stuck orphan is worse than a fresh retry.
7. **Avoid a retry macro over `odoo-bin`**: it adds complexity (and `$$`
   escaping bugs) without solving the root cause. Prefer direct commands;
   the slot retry, if any, must be minimal (only `createdb`).
8. **The comma in `--test-tags` separates COMPLETE specs**: `mod:A,mod:B`
   runs both classes; `mod:A,B` runs fewer tests, without error. Repeat the
   prefix per spec and verify the `of N tests` line against the expected
   count (source: `odoo/tests/tag_selector.py`).
9. **Anti-false-green guards are mandatory** (`require-installed` /
   `require-module`): `-u` of a non-installed module and `-i` of a
   non-existent module report `0 failed ... of 0 tests` with rc=0 — pure
   false green.

## Run budget (mandatory protocol)

The full suite is for the gate, not for debugging: iteration uses `test-one`
on the warm DB with the anti-loop cycle (read failure → hypothesis → one
change → one run; max 2 without convergence → STOP); the gate is closed with
ONE `test-all` on a fresh DB. Hard budget per stage, default 2 full runs +
~15 `test-one` per feature (adjustable per project by the owner in
`systemPatterns.md`). Full detail: `references/run-budget-protocol.md`.

## References

- `assets/Makefile.template` — contract base (placeholders).
- `assets/odoo-test.conf.template` — own test conf (do not touch the
  platform's in managed environments).
- `references/odoo-sh.md` — public reference implementation.
- `references/odoo-19-traps.md` — verified Odoo 19 API traps
  (`res.groups.privilege` / `<list>` and their relation to schema drift).
- `references/run-budget-protocol.md` — per-stage run budget protocol
  (warm test-one for iterating, test-all for the gate, budget 0 in review
  with tree identity, N of property tests as calibration).
