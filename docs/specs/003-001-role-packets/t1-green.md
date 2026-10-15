# 003-001 Task 1 — GREEN implementer report

## Result

Task 1 is GREEN in its focal public suite. No tests, test runners, specs, epic/state documents, or git history were modified by the implementer.

## Implementation

- `install.sh`
  - Honors an optional `CDAD_INSTALL_ROOT` for every managed OpenCode, Agents, and Claude destination while leaving `HOME` unchanged.
  - Rejects an explicit root unless it is absolute and already exists, before installation writes.
  - Applies the root to install, dry-run, check, and the existing uninstall paths.
- `skills/cdad-cycle/scripts/cdad_packet.py`
  - Adds the canonical stdlib-only `validate-state` command.
  - Validates exact execution/state bindings, active epic/feature membership, allowed stages, structured HITL authority, required expiry events, authority path containment/existence, authorized runtime/scope pairs, and nullable/exhaustive active packet state.
  - Validates the Task 1 path-policy shape, including the newly approved optional exact-file lists, and exposes mechanical classification with test precedence over implementation.
  - Validates the scoped ADR-010 exception before ordinary compatibility and reports configured/reported model observations separately.
- `scripts/cdad_packet.py`
  - Thin repository wrapper over the installable canonical CLI.
- `scripts/validate-subagents.sh`
  - Accepts `--project-root` and `--execution-context`.
  - Uses the canonical policy rather than duplicating execution/authority validation.
  - Honors `CDAD_INSTALL_ROOT` and only bypasses legacy diversity guards after a valid scoped exception.
- `skills/cdad-cycle/assets/state-template.json`
  - Adds `execution`, `active_packet`, and `hitl_delegation` slots.
- Public Task 1 schemas:
  - `skills/cdad-cycle/assets/execution-context.schema.json`
  - `skills/cdad-cycle/assets/active-packet.schema.json`

## Evidence

- Focal suite: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_role_packets` → 2/2 PASS.
- Shell syntax, CLI help, and `git diff --check` → PASS.
- Explicit relative install root → rejected with a nonzero status before creating a destination.
- Isolated install root `<isolated-install>`, with `CDAD_SKILL_EXTRA_DIRS` cleared:
  - `install.sh --basic` → PASS, 11/11 agents present.
  - `install.sh --check` → PASS, 27/27 in sync.
  - `validate-subagents.sh` legacy/basic path → PASS.
  - Installed canonical CLI `validate-state` against `<fixture-project>` → PASS, scoped exception identified with configured model and `reported_model=None` kept distinct.
  - `validate-subagents.sh --project-root ... --execution-context ...` → PASS through the shared policy.
- Legacy baseline `tests/validate-consistency.sh` → known 123 PASS / 1 FAIL (F011 real installation drift), unchanged from the approved baseline.
- `tests/validate-odoo-specialization.sh` → 141 PASS / 0 FAIL.

Logs:

- `<isolated-install>`
- `/tmp/cdad-t1-check.log`
- `/tmp/cdad-invalid-root.out`

## Changed implementation files

- `install.sh`
- `scripts/validate-subagents.sh`
- `scripts/cdad_packet.py`
- `skills/cdad-cycle/scripts/cdad_packet.py`
- `skills/cdad-cycle/assets/state-template.json`
- `skills/cdad-cycle/assets/execution-context.schema.json`
- `skills/cdad-cycle/assets/active-packet.schema.json`

## Diagnostics and limits

- This is Task 1 only. Renderer/templates, request/packet/metric validation, consumer migration, and Task 2/3 behavior are intentionally absent.
- The real user installation was not changed. All writes were confined to the explicit `/tmp` install root.
- `tests/__pycache__/` was already present as an untracked artifact from the orchestrator/test run and was not modified or removed by this role.
- No commit was created because the handoff explicitly prohibited git mutation.

Gate T1 verificado por Codex: focal repetido 2/2 PASS, salida exacta en
`evidence/t1-green.log`; check aislado 27/27 PASS. No hay cambios a tests.
P1–P6 de la feature todavía no están completos: resta T2, T3 y review.
