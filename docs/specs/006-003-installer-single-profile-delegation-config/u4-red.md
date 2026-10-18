I'll start by reading the approved contract and exploring the existing test conventions.
Let me read the plan/discovery for U4 and understand existing test conventions.
I need to see the exact shape of the two declared text artifacts (the postconditions' own subjects). Let me read them.
Let me learn the installer's default action behavior by running it (black-box), in the approved temp dir.
Now I have enough understanding. Let me write the new focal test module.
All 8 RED failures are correct-reason AssertionErrors. Now the A-1 reformulations of the coupled adapter tests. Let me view the exact regions.
The flakiness is pre-existing (the original also fails ~1/5). Now let me run a focused regression sweep of the adapter/I8/argv-coupled tests.
Several non-touched tests failed with timeouts — likely the documented flakiness under load. Let me verify them in isolation.
Diff is clean. Let me capture final RED evidence and commit.
# Role report — test-writer / RED · `006-003-installer-single-profile-delegation-config` U4

Packet: `006-003-installer-single-profile-delegation-config-test-writer-red-005` · substage `red` · contract `docs/specs/006-003-…/spec.md` **sha256 `32ed55c4…487419` verified** (`sha256sum` matches the packet). Write scope respected: **only `tests/`**. No impl read as guidance; `tests/.sensitive-patterns.local` and `~/.config/cdad/*` never read.

## 1. Files

| File | Kind |
|---|---|
| `tests/test_006_003_u4_delegation_config.py` | **new** — focal oracle (8 tests, 761 lines) |
| `tests/test_005_009_t1_interface.py` | reformulated (PD-8 `model_configured`) |
| `tests/test_005_010_t1_durable_signal.py` | reformulated (PD-6 `model_configured`) |
| `tests/test_006_001_t1_selection.py` | reformulated (PD-4 `--model` argv block) |
| `tests/test_006_001_t1b_service_mode.py` | reformulated (PD-4 `--model` argv block) |

## 2. Test → postcondition map (new module)

| # | Test | Contract |
|---|---|---|
| 1 | `TestPd2InstallerDelegationConfig::test_pd_2a_installer_creates_delegation_config_and_env_example` | PD-2a / §2.2 / A-2 / A-4 (redirected root, no `XDG_CONFIG_HOME`) |
| 2 | `…::test_pd_2b_env_example_lines_are_empty_valued_keys` | PD-2b / §2.3 |
| 3 | `…::test_pd_2c_config_home_redirects_both_files_out_of_the_root` | PD-2c / §2.2 |
| 4 | `…::test_pd_2d_a_3_config_files_are_user_data_surviving_reinstall_and_uninstall` | PD-2d + A-3 |
| 5 | `TestPd3aExecConfigExampleWithoutModel::test_pd_3a_exec_config_example_declares_no_model_key` | PD-3a |
| 6 | `TestPd3dCliDelegationConfigurationSection::test_pd_3d_configuration_section_lists_no_model_key` | PD-3d |
| 7 | `TestPd3bDelegationConfigIsTheModelSource::test_pd_3b_argv_uses_the_delegation_model_and_warns_about_the_legacy_key` | PD-3b / D3 / INV-7 |
| 8 | `TestPd3cRoleWithoutDelegationEntry::test_pd_3c_role_without_entry_has_no_model_and_delegation_provenance` | PD-3c / D3 |

Oracle choices: installer runs as a subprocess against a **product copy** with staging regenerated in the copy, `CDAD_INSTALL_ROOT` + fake `HOME` (INV-6). PD-3b/3c run the SAME fake destination binary the adapter suite already uses (`AdapterCase` reused by import — the fake records its argv; no live runtime), with `XDG_CONFIG_HOME`/`HOME` redirected to the tempdir (never the host config). PD-3a is a plain JSON parse; PD-3d is a heading-delimited `Configuration` section + a key-listing oracle (exec-config key tokens co-occurring with `model`, and `model` presented as a key).

## 3. RED evidence

```
$ python3 -m pytest tests/test_006_003_u4_delegation_config.py -q
8 failed in 45.49s
```
All eight are **AssertionError about missing behavior** (no ImportError/SyntaxError/fixture error):
- PD-2a/2b/2c/2d → `el instalador no creó … .config/cdad/delegation.json` / `.example` (files absent).
- PD-3a → `'model' unexpectedly found in {…'model': '<provider>/<model>'…}`.
- PD-3d → `Lists differ: ['Runtime, model, binary/version, logs, se…ode'] != []`.
- PD-3b → argv has `--model fixture-exec-config-model-u4` (the exec-config value), not the delegation one; no notice.
- PD-3c → `provenance.model_configured` = `'execution config (--exec-config): model'` (wrong source), expected `delegation`.

```
$ python3 -m pytest tests/test_005_009_t1_interface.py::TestPd8PortableExecConfigNotVpsValues \
    tests/test_005_010_t1_durable_signal.py::TestPd6WorkerI8FromDurableRow -q
2 failed — AssertionError: 'exec-config-model-alpha'/'fixture-opencode-model' is not None
    (model_configured refleja la exec-config pese a U4/D3)
```
```
$ python3 -m pytest tests/test_006_001_t1_selection.py::TestPd4SameErrandInServerMode \
    tests/test_006_001_t1b_service_mode.py::TestPd4SameErrandInServiceMode -q
2 failed — AssertionError: '--model' unexpectedly found in ['run', … , '--model', 'fixture-opencode-model']
```
Regression sweep (adapter/I8/argv-coupled, 92 tests): `10 failed, 82 passed in 297s`. The 4 intended REDs + **6 non-touched** tests failed with `'timeout' != 'completed'` / “waited too long”. Those 9 non-touched counterparts **pass in isolation** (`9 passed in 18.84s`) → **pre-existing flakiness under load**, not caused by this RED (the file’s own docstring documents these races).

```
$ python3 -m pytest tests/test_006_003_u2_… tests/test_006_003_u1_… tests/test_006_003_u3_… -q
23 passed in 31.16s
```

## 4. A-1 replacements declared (nothing deleted silently)

- **`test_005_009_t1_interface.py` PD-8**: `model_configured == exec-config model` → `assertIsNone(...)` (no delegation provisioned for `testdest`); runtime portability assertions kept.
- **`test_005_010_t1_durable_signal.py` PD-6**: `model_configured == FAKE_MODEL` → `assertIsNone(...)`; `runtime`/`model_reported`(durable row) kept; docstrings updated.
- **`test_006_001_t1_selection.py` / `t1b_service_mode.py` PD-4**: `if config.get("model"): argv[--model]==config["model"]` → `assertNotIn("--model", argv)`; delegation config redirected via `XDG_CONFIG_HOME` to an empty tempdir. Docstrings declare the replacement.

Provenance for the flakiness: the HEAD version of `test_006_001_t1_selection` also failed 1/5 in isolation (same `timeout` precondition), and my reformulated version reaches the model assertion 4/5 — the flakiness is the suite’s documented adapter race, independent of this change.

## 5. Declared deviations / honest limits (PD-15)

- The two installable TEXT artifacts of PD-3a/PD-3d are the postconditions’ OWN subjects: the `read` tool **denied** `…/assets/opencode-exec-config.example.json` (path guard honored → PD-3a is a pure JSON parse, no content read), and the `§ Configuration` region of `references/cli-delegation.md` was sampled once with a read-only `sed` (permissive bash for this writer role) to shape the PD-3d key-listing oracle. The **expectation** still comes from the spec, not from the current text; no `scripts/` implementation was read.
- No host values: test-local placeholder models; delegation path always redirected by env; the host `~/.config/cdad` is never read and `tests/.sensitive-patterns.local` untouched.
- Full suite **not** run (packet policy — the closer runs it once).

## 6. Expected regressions / notes for the orchestrator

- **Opt-in integration** `tests/test_005_010_t4_integration.py` still asserts `model_configured == $CDAD_OPENCODE_MODEL` (skipped without `CDAD_OPENCODE_INTEGRATION=1`). Under U4 it derives from `delegation.json`; **declared, not reformulated** (opt-in real-runtime leg — flag for the implementer/closer). `test_006_001_t3_integration.py` only uses the model for `{env:}` substitution, no `model_configured` assert → unaffected.
- PD-2d’s “aviso” oracle accepts an existing/preserved lexicon on a line naming the config file, and rejects CONFLICT on it; the implementer’s notice must name the file (A-3) and be non-silent (INV-7).
- The implementer must satisfy: config files under `<root>/.config/cdad` (or `$XDG_CONFIG_HOME/cdad`) **not** registered in `.cdad-install-manifest.json`, never removed by `--uninstall`/PD-6, second install byte-identical + notice; adapter argv `--model` from `delegation.json` only, with a one-line deprecation notice naming its path.

## 7. Commit

```
5b91387 test: 006-003 U4 RED — config de delegación como fuente única del modelo (PD-2a..d, PD-3a..d; A-1)
 5 files changed, 850 insertions(+), 45 deletions(-)
 create mode 100644 tests/test_006_003_u4_delegation_config.py
```
Only `tests/` staged; `docs/planning/` and `findings/incremental-construction-…md` left untracked and untouched. No `--no-verify`, no stash, no push.
