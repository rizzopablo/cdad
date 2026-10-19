## Role report — implementer, GREEN, `006-005-native-path-parity` / U1a

### Modified files (commit `4052939`, no `--no-verify`, no stash, no push)

| File | Change |
|---|---|
| `skills/cdad-cycle/scripts/cdad_dispatch.py` | **new** (391 lines) — the execution-configuration layer + the bounded migration step |
| `install.sh` | `+write_runtimes_template` + its call in `install_user_config` |
| `skills/cdad-cycle/references/cli-delegation.md` | new entry section, the runtime section of the config, the migration step and its adoption border |

`git show --name-status HEAD` → `M install.sh`, `M skills/.../cli-delegation.md`, `A skills/.../cdad_dispatch.py`. Nothing under `tests/**`; `docs/planning/` and `findings/...` left untracked and untouched. Contract `docs/specs/006-005-native-path-parity/spec.md` sha256 = `3a824be31e45cd8e6122b7d6f23d3f4d3e6af847ab73f7babef8aa90ce20df01` (matches the packet).

### What the code does (minimum for the approved contract)

- **PD-8** — `--runtime` mandatory in every verb (argparse `required`); resolution delegates to `cdad_delegate._adapter_path` (the existing module convention, INV-12); an id with no `cdad_delegate_<id>.py` fails closed **naming the value**. No project document is ever read for the runtime.
- **PD-9** — the runtime section of `runtimes.json` under `cdad_delegate.cdad_config_dir()` (location rule reused, not re-derived). Absent file/section ⇒ one fail-closed diagnostic naming the file, the section, the section key ids and the full key-by-key correspondence (`runtime`, `binary`, `binary_version`, `mode`, `server`, `service`, `auto`, `sessions_db`, `wait`, `model` → `delegation.json`, credential → `delegation.json.credential_env_file` / `opencode-server.env`). `model` and `credential_env_file` inside the section ⇒ rejected naming where they live. `--exec-config` is rejected by an **exact-token `argv` sweep before the verb is parsed** (D-11/O-10; `--legacy-exec-config` is a different token), with the same diagnostic; `--help` never declares it.
- **PD-25/§2.6.1** — `migrate --runtime X --legacy-exec-config FILE [--dry-run]`: moves only the correspondence keys, writes the section **only if absent** (existing section ⇒ rc≠0, bytes intact), `--dry-run` writes nothing and prints the section key/value by key/value, a missing legacy file fails closed naming its path; the model/credential are only reported.
- **U1b extension points** — `dispatch` reaches the runtime resolution + section check, then fails closed on the packet it would consume; `record`/`capabilities` are declared and fail closed with a named diagnostic (no pretending).
- **Installer** — template written only when missing, not registered in the ownership manifest, never overwritten (INV-7).

### Evidence — test → result

| Command | Result |
|---|---|
| `python3 -m pytest -q tests/test_006_005_u1a_runtime_config.py` (pre-change, RED) | **19 failed** (declared RED, commit `5dbc854`) |
| `python3 -m pytest -q tests/test_006_005_u1a_runtime_config.py` (focals) | **19 passed** |
| Declared U1a regressions (`test_006_003_u2_installer_without_profiles`, `test_005_004_t2_installer_claims`, `test_006_003_u7_prune_obsolete`, `test_install_review5_regressions`, `test_006_003_rf_review_fixes`, `test_006_003_rf2_review_fixes`) | **37 passed** (293.28s) |
| Every test file invoking `install.sh` — `pytest $(grep -l "install.sh" tests/*.py)` | **313 passed** (1121.96s) |
| Doc-contract tests of the touched reference (`test_005_010_t3_references`, `test_006_002_u3_runtime_references`, `test_006_003_u4_delegation_config`) + focals | **38 passed** |
| `make validate` | 168 PASS / **1 FAIL** → F011 |

**F011 declared (environmental, pre-existing).** `make validate` fails only on `scripts/validate-subagents.sh (active profile)`, which compares the repo against the operator's **real HOME installs** (`~/.config/opencode`, `~/.agents`, `~/.claude`) and already reported drift (`skills/cdad-cycle has 82 file(s), installed has 86`). Proven pre-existing: `git worktree add --detach <base 8f23ffd>` + `make staging` + `bash scripts/validate-subagents.sh` → `❌ install.sh --check failed (rc=1)` / `== RESULT: FAIL ==`. My change adds no new cause; I did not install in HOME (forbidden), so the new script cannot be mirrored there.

### Commit

```
4052939 feat: 006-005 U1a GREEN — runtime execution config, migrate step and installer template
 3 files changed, 469 insertions(+), 1 deletion(-)
```

### Notes for the orchestrator

- No test was edited; `git log -1 -- tests/test_006_005_u1a_runtime_config.py` is still the RED `5dbc854`.
- I used the RED's declared permissive interface: `dispatch`/`record`/`capabilities` are declared (so argv is parsed as the final CLI) but only the U1a surface is implemented — the U1b RED adds the per-verb `--exec-config` cases and the transport.
- Full-suite policy respected: only the proportional battery required by the change was run; the full suite is for the closer.