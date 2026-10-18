Now I'll add the user-config creation to `install.sh`.
Now the shared helpers in `cdad_delegate.py`.
Now the OpenCode adapter.
Now the model resolution in the adapter's `delegate()`.
## Role report — implementer / GREEN, `006-003-installer-single-profile-delegation-config` (packet `...implementer-green-004`)

### Modified files (write scope only, `tests/` untouched)

| File | Change |
|---|---|
| `install.sh` | `+67`: `user_config_dir`, `write_delegation_template`, `write_server_env_example`, `install_user_config`; called in `main()` after `install_guard_script`, before the manifest. Creates `delegation.json` (`version: 1`, `models.opencode: {}`) and `opencode-server.env.example` (comments + `OPENCODE_PASSWORD=`/`OPENCODE_SERVER_PASSWORD=`) under `${XDG_CONFIG_HOME}/cdad` or `<root>/.config/cdad`. Only when missing (notice naming the file, no CONFLICT), never registered as owned, `--dry-run` writes nothing. |
| `skills/cdad-cycle/scripts/cdad_delegate.py` | `+93/−…`: `delegation_config_path()`, `delegation_model(destination, role)` (only source, no fallback, version 1 validated, fail-loud on malformed), `delegation_model_provenance()`, `_warn_legacy_model()` one-line notice naming the path + migration; `_observation(..., model_source=)`; `delegate()` resolves role from the packet and takes the model from the delegation config; a legacy `model` in the exec-config is ignored with exactly one line. |
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` | `+27/−…`: imports `cdad_delegate` (same module convention as `cdad_result`), drops `config.get("model")`, resolves the model from the delegation config after the request's role (a config it cannot parse blocks before dispatch), provenance of `model_configured` → delegation config. |
| `skills/cdad-cycle/assets/opencode-exec-config.example.json` | removed `"model": "<provider>/<model>"` (PD-3a). |
| `skills/cdad-cycle/references/cli-delegation.md` | § Configuration: model no longer an exec-config key; delegation config documented (path for both XDG cases, v1 schema, destination id = runtime id, role w/o entry ⇒ no `--model` + `model_configured: null`, legacy key ⇒ deprecation notice) (PD-3d). |

Not touched: `tests/**` (0 paths in the commit), `docs/planning/`, `findings/…` (pre-existing untracked, not mine).

### Test → result

| Test / set | Command | Result |
|---|---|---|
| **Focal U4** (`PD-2a..d`, `PD-3a..d`) | `python3 -m pytest tests/test_006_003_u4_delegation_config.py -q` | **8 passed** (49.93 s) |
| Reformulados PD-8/PD-6 | `pytest tests/test_005_009_t1_interface.py tests/test_005_010_t1_durable_signal.py -q` | **10 passed** |
| Reformulados PD-4 (selection) | `pytest tests/test_006_001_t1_selection.py` | 33/34 en corrida conjunta; 1 `timeout` (deuda declarada, ver abajo); **pasa aislado** |
| Reformulados PD-4 (service) | `pytest tests/test_006_001_t1b_service_mode.py` | 32/34 conjunta; fallos `timeout` (deuda declarada); las clases `TestPd1ServiceRows`/`TestPd2ServerPreflight` **3/3 corridas verdes** |
| Resto adaptador + I8 (`grep -l "cdad_delegate"`, 7 módulos) | `pytest test_005_007_reviewfix_blockings test_005_007_t4_* test_005_007_t5_delegation_dispatch test_005_009_t2_opencode_adapter test_006_001_t2_wait_recovery test_006_002_u1_delegation_section test_006_002_u5_transport_equivalence -q` | **50 passed** |
| `test_006_003_u1/u2/u3` | `pytest … -q` | **23 passed** |
| Instalador (ownership / review5 / claims) | `pytest test_install_ownership.py test_install_review5_regressions.py test_005_004_t2_installer_claims.py -q` | **24 passed** (251 s; incluye dry-run “no escribe nada”) |
| Aceptación 004-001 + t6 + t7 | `pytest test_004_001_acceptance_matrix.py test_004_001_t6.py test_004_001_t7_capacity.py -q` | **18 passed** |
| Otros que invocan `install.sh` | `pytest test_003_002_t4_integration test_004_002_t6_landing test_004_003_t2_plan_review test_005_005_t4_integration test_005_008_t3_acceptance test_packet_prepare test_role_packet_consumers test_role_packets -q` | **56 passed** |
| Resto con referencia a `install.sh` | `pytest` (18 módulos) | **147 passed** |
| Consistencia | `bash tests/validate-consistency.sh` | **166 PASS / 1 FAIL** → `F011: scripts/validate-subagents.sh` (drift de HOME; ver abajo) |
| `install.sh --check` sobre raíz temporal recién instalada | ver comando abajo | **PASS (390 grupos)** |

### Commands with output (key evidence)

```
$ python3 -m pytest tests/test_006_003_u4_delegation_config.py -q
........                                                                 [100%]
8 passed in 49.93s
```

```
$ python3 -m pytest tests/test_005_009_t1_interface.py tests/test_005_010_t1_durable_signal.py -q
..........                                                               [100%]
10 passed in 19.34s
```

Installation into a temp root (never HOME), first and second run + contents + manifest:

```
[..] User config: /tmp/opencode/u4check/root/.config/cdad/delegation.json (delegation config v1 template — set models.<destination-id>.<role> to choose the delegated model)
[..] User config: /tmp/opencode/u4check/root/.config/cdad/opencode-server.env.example (credential template with no value; copy it to opencode-server.env with mode 600)
--- delegation.json
{ "version": 1, "models": { "opencode": {} } }
--- example (non-comment lines)
OPENCODE_PASSWORD=
OPENCODE_SERVER_PASSWORD=
--- manifest artifacts: 366 | config artifacts: []
--- second install
[..] User config: …/delegation.json already exists — preserved untouched (user data; never overwritten, never owned, never removed)
[..] User config: …/opencode-server.env.example already exists — preserved untouched (…)
```

```
$ XDG_CONFIG_HOME=/tmp/…/xdg python3 - <<'PY'  (delegation: opencode/test-writer → provider/model-y)
path: …/xdg/cdad/delegation.json
model(test-writer): provider/model-y
model(reviewer)   : None
provenance        : delegation config (delegation.json): models.opencode.test-writer
DEPRECATED: the `model` key of the execution configuration is ignored (006-003 D3) — move it to models.opencode.test-writer in …/delegation.json, the only source of the delegated model
```
(one line, names the path + migration, never prints the ignored value.)

```
$ install.sh --check   (temp root)
[..] Check: PASS (390 artifact groups in sync with staging/skills)
```

### Gates / declared debt (honest)

1. **Adapter race (declared in the packet).** Running `test_006_001_t1_selection.py` + `t1b_service_mode.py` **together** intermittently yields `timeout` (`destination 'opencode' did not answer within 2.0 seconds`), a different test each run. Repeated isolated: **green** (classes 3/3 runs; single test 6/6). Control on a copy of **HEAD without my diff** (`/tmp/opencode/u4-baseline`): 3 and 5 failures of the same class on the same two files → **pre-existing**, not introduced here.
2. **`tests/test_005_010_t4_integration.py` (opt-in, skipped by default) still asserts `model_configured == $CDAD_OPENCODE_MODEL`** (`:467`). It is NOT reformulated in this RED and will fail if the real integration run is enabled; declared here as required.
3. **F011 = HOME drift (pre-existing).** `validate-subagents.sh` compares the repo with the owner's HOME installs; failures list `SKILL.md` and all 22 agents plus the asset. The same script against the HEAD copy (no diff) also ends `== RESULT: FAIL`, so the drift predates U4 (the packet also declares F011 = HOME drift).
4. Full suite **not** run (packet policy: the closer runs it once at closure).

### Honest limits

- No install in HOME, no writes outside the redirect roots; the only contact with `~/.config/cdad` was a read-only directory listing to confirm **no `delegation.json`** existed there (hermeticity of the adapter tests); the `.env` content was never read.
- I read tests (contract) and did not edit them; no test was rewritten to pass.

### Commit

```
df90b41 feat: 006-003 U4 GREEN — config de delegación como fuente única del modelo (PD-2a..d, PD-3a..d)
 5 files changed, 205 insertions(+), 25 deletions(-)
   install.sh | skills/cdad-cycle/assets/opencode-exec-config.example.json
   skills/cdad-cycle/references/cli-delegation.md
   skills/cdad-cycle/scripts/cdad_delegate.py
   skills/cdad-cycle/scripts/cdad_delegate_opencode.py
```
No `--no-verify` (hooks ran), no `git stash`, no push; `git show --name-only | grep '^tests/'` → 0.
