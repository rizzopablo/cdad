Now I have enough black-box understanding. Let me write the RED test module.
Now let me review the full file and run it.
# Role report — test-writer / RED · `006-003-installer-single-profile-delegation-config` U7

**Packet** `006-003-installer-single-profile-delegation-config-test-writer-red-010` · substage `red` · contract `docs/specs/006-003-…/spec.md` **sha256 `c25ebf0e…d18890` verified** (`sha256sum` matches the packet). Write scope respected: **only `tests/`** (one new file). No implementation read: `install.sh` was never opened/grepped — all knowledge about it came from *running* it black-box in `/tmp/opencode/u7exp` (temp dir, removed at the end) and from its published `--help`/manifest/output. `tests/.sensitive-patterns.local` never read. `docs/planning/` and `findings/` (pre-existing untracked) untouched; no `--no-verify`, no stash, no push.

## 1. Files

| File | Kind |
|---|---|
| `tests/test_006_003_u7_prune_obsolete.py` | **new** — focal oracle, 675 lines, 6 tests. Commit **`3a04ad1`** (diff limited to `tests/`) |

## 2. Map test → postcondition

| # | Test | Contract | Oracles (observable) |
|---|---|---|---|
| 1 | `test_pd_6a_intact_retired_own_file_is_removed_from_disk_and_manifest` | **PD-6a** / D6 / INV-2 | install #1 (full) → source retired → install #2: every path the manifest registered from the retired source is **gone from disk** and **absent from `artifacts` + `pending_removal`**; `install.sh --check` prints **no `PENDING-REMOVAL` line**, **rc=0** and **PASS** |
| 2 | `test_pd_6b_locally_modified_retired_own_file_is_preserved_and_conflicted` | **PD-6b** / INV-2 | same case, `.agents/**` copy modified locally: bytes **preserved**, disclosed as **CONFLICT** (output line with the path, or `manifest.conflicts`), **still registered**; **non-vacuity control**: the untouched sibling deployments of the same source **are** retired |
| 3 | `test_pd_6c_unregistered_file_inside_the_installed_tree_is_never_touched` | **PD-6c** / INV-2 | a file inside the installed tree that the manifest does not register survives the prune **byte for byte** and is never registered |
| 4 | `test_pd_6d_dry_run_lists_the_bajas_without_deleting_anything` | **PD-6d** | `--dry-run` output **names the baja**; tree snapshot and manifest sha **unchanged**; all retired paths still present |
| 5 | `test_pd_6e_manifest_paths_are_resolved_against_the_redirected_root` | **PD-6e** | manifest rewritten (hand-edit, declared) so the retired own file is recorded under **absolute** paths → install #2 removes them from the **redirected root** and drops every absolute/relative key; relative half exercised by PD-6a in an equally redirected root |
| 6 | `test_a_3_config_files_are_never_owned_removed_nor_registered` | **A-3** | `delegation.json` + `opencode-server.env.example`: **never in the manifest**, byte-identical after reinstall (prune active) **and** after `--uninstall --force` |

**Fixture (black-box, never HOME/repo):** product copy in a temp dir + staging generated **in the copy** for both runtimes; `CDAD_INSTALL_ROOT`+fake `HOME` per test; two **real** installations (the retired source is removed from the *product copy* and restored by context manager — no manifest hand-editing anywhere except test 5, declared in its docstring). Deployed paths are read **from the manifest install #1 publishes**, never hardcoded.

## 3. RED evidence

```
$ python3 -m pytest tests/test_006_003_u7_prune_obsolete.py --collect-only -q
6 tests collected in 0.05s

$ python3 -m pytest tests/test_006_003_u7_prune_obsolete.py -q
4 failed, 2 passed in 162.51s          (repeated run: identical 4 failed, 2 passed — deterministic)
```
All four are **AssertionError about missing behaviour** (no ImportError/SyntaxError/fixture error):
- **PD-6a** → `Lists differ: ['.agents/…/ADR.md', '.claude/…/ADR.md', '.config/opencode/…/ADR.md'] != []` — the retired own file stays on disk (and in the manifest; `--check` still FAILs with 3 `PENDING-REMOVAL` lines in the re-run).
- **PD-6b** → `False is not true : … no se reportó como CONFLICT` — the re-run publishes `OWNERSHIP summary: 369 owned file(s), 0 conflict(s)`, `conflicts: []`.
- **PD-6d** → `AssertionError: 'cdad-cycle/assets/adr-template/ADR.md' not found in '<dry-run output>'` — `--dry-run` never lists the baja (only `DRY-RUN COPY/SYNC` lines).
- **PD-6e** → `Lists differ: [3 paths] != []` — the absolute-keyed entries are carried into `pending_removal` instead of pruned.

**Declared GREEN controls today** (not evidence U7 is done): **PD-6c** (unregistered files already survive) and **A-3** (both config files already survive re-install and `--uninstall`).

## 4. Focused regression baseline

```
$ python3 -m pytest tests/test_install_ownership.py tests/test_install_review5_regressions.py -q
16 passed in 195.69s        (ownership 11 tests incl. --uninstall/--dry-run/--check; review5 5 tests)
$ python3 -m pytest tests/test_006_003_u7_prune_obsolete.py tests/test_install_ownership.py tests/test_install_review5_regressions.py -q
4 failed, 18 passed in 356.76s   (4 failed = the new RED module; no regression)
```
No pre-existing test was touched, so no A-1 reformulation was needed for U7. Expected regression surface for the GREEN step: `test_install_ownership.py::TestT5UninstallAndForeign::test_t5_case7_uninstall_removes_only_manifest_entries`, `test_t5_case9_dry_run_announces_exactly_the_staged_set`, `test_t5_case3/10_check_*` (same sha256 rule + `--dry-run`/`--check` surfaces) and `test_install_review5_regressions.py` (installer CLI surface). **Full suite not run** (packet policy: the closer runs it once).

## 5. Commit

```
$ git commit -m "test: 006-003 U7 RED — retiro de obsoletos propios en la instalación (PD-6a..e, INV-2, A-3)"
[main 3a04ad1] 1 file changed, 675 insertions(+)
$ git diff --name-only HEAD~1 HEAD
tests/test_006_003_u7_prune_obsolete.py
```

**Honest notes / limits:** (1) the scenario is synthetic-but-real: the retired file leaves the product because its *source* is deleted in the copied tree, not by an upstream rename — declared in the module docstring; (2) test 5's manifest rewrite is the only hand-edit and it is declared there; (3) `--uninstall` is invoked with `--force` (the help says it otherwise prompts); (4) the module needs ~3 min (two real installs per test) and runs subprocesses sequentially.
