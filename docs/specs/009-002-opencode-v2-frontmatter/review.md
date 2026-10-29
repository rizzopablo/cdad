I found 1 blocking issue: the last test commit `e3f59bd` (red-008) breaks the test suite. The product side of 009-002 checks out: the static agents, the real OpenCode 2.2.0 runtime and the V1→V2 upgrade all behave as the spec says. The fix is test-side and goes to the test-writer.

# review.md — 009-002 (packet `…-reviewer-review-001`)

**Intake:** route A. `cdad_packet.py render` output is byte-identical to `PACKET.md`, `validate-request` rc=0, and the spec's sha256 is `c62c9e7c…`. The diff reviewed is `9fc90b1..HEAD`, the 7 commits from `ba8d19b` to `e3f59bd`.

## Blocking

**B1 — Changing a shared test helper broke the modules that import it** (Required · Verdict: BLOCKING · Bucket: h)
- **Evidence:** `e3f59bd` deleted `RULE_RE` from `tests/test_opencode_read_map_and_steps.py`. It also changed `frontmatter()`: it used to return the text from the start of the file through the frontmatter, and now returns only the YAML between the `---` lines. Three importers break:
  - `tests/test_004_002_t7_private_paths.py:138` fails with `ImportError: cannot import name 'RULE_RE'`, so the module cannot be collected.
  - `tests/test_004_002_t5_runtime.py:219-220` cuts the body with `agent_text[len(fm):]`, which is now 3 characters off. Result: `2 failed, 45 passed` (`test_pd8_i9_derived_body_is_byte_identical_to_source` and `test_pd8_i9_reconciled_policy_regenerates_deriveds`; the diff shows `mode: allny` vs `mode: allow`).
  - In a `git archive` copy with `RULE_RE` put back, t7 still fails `test_p1_rf2_yaml_valid_and_permission_map_denies_private` with `frontmatter sin delimitador '---' inicial`.
- **Weakened oracle:** t5's `without_maps` now removes the whole `permissions:` block. Before, the non-owned `bash` rules stayed in the compared text. No test now checks that derived agents keep their `shell` rules. Today's effect is small: the runtime default is already allow.
- **Consequence:**
  - Any `pytest tests/` stops with `Interrupted: 1 error during collection`, so the closer cannot run the full suite.
  - `cdad-suite.py validate` cannot collect either, so it fails (rc=1).
  - The private-path control, the "control privado" the objective asks about, is not running.
- **Closure condition:**
  - Migrate every importer as one family. Any of these can return a value derived from what `frontmatter()` now returns: `pd10`, `test_005_004_t4`, t5, t7, `u6fix7`.
  - t7 collects and passes 11/11, and both t5 tests pass.
  - `without_maps` again compares the non-owned rules (shell, `*`).

## Optional

- **O1 — Classifier gaps (m):**
  - In the arena with B1 bypassed, `cdad-suite.py validate` reports `tests/agent_frontmatter.py` as not in the inventory, and the 3 `test_009_002` tests as having no capability or contract.
  - `surface` on the helper fails with `modulo de test sin nodeids recolectados`.
  - `test_opencode_read_map_and_steps.py` is listed as a test, not a helper. When it changes, the classifier selects only its own 4 tests, not t5 or t7. That is how B1 got through.
  - These gaps already existed: 80 entries are listed, including 008-002..008-005 and 009-001.
- **O2 — PC-1/PC-2 tests miss the committed agents (m):** `AGENT_DIRS` points at `agents/opencode`, which does not exist; the committed agents are `agents/*.md`. Only the git-ignored `build/staging` is checked. The rule-order test passes without checking anything if staging is missing. Today staging and `agents/*.md` are byte-identical.
- **O3 — Derived agent from a V1 source loses the reviewer's temperature (l):** `_rewrite_derived_agent` converts only the permissions. It keeps the top-level `temperature`/`edit` lines, and OpenCode 2.2.0 then shows `request.body {}`. This only matters during an upgrade, until the agents are reinstalled.

## FYI

- The spec has not been committed yet (untracked), and its `commit` is null.
- `plan.md:40` adds a table row after a paragraph, outside any table.
- With V1 frontmatter, OpenCode moves `edit: deny` and `temperature` into `request.body`. That supports switching to V2.

## Abstentions

- I could not confirm the spec's starting premise ("with V1 the runtime ignores `model:`"). A V1 agent tested in the project folder (`.opencode/agents`) still resolved `model:`. I did not test a V1 global install with `debug agents`. This is not a finding against the feature.
- I did not measure how the `write` tool applies `edit` rules at runtime; `debug agents` does not show it.

## PC → evidence

| PC | Evidence | Result |
|---|---|---|
| PC-1 | Parsing all 11 agents: no `permission`, no top-level `temperature`, no `edit: deny` | ✅ |
| PC-2 | V1 at `9fc90b1` vs V2 at HEAD: same rules in the same order (2/2/12/12/1/2/2/2/2/36/32 rules); bodies identical | ✅ |
| PC-3 | Only the reviewers carry `request.body.temperature 0.1`; runtime shows `temp 0.1` | ✅ |
| PC-4 | Orchestrator YAML parses, `mode all` | ✅ |
| PC-5 | No changes under `agents/claude-code` | ✅ |
| PC-6 | `make agents` twice: no change; clean arena install: `--check` PASS (393) | ✅ |
| PC-7 | `apply_bash_block` removed, with the reason written in `install.sh` | ✅ |

- **Runtime (OpenCode 2.2.0, `debug agents --standalone`, isolated HOME):** all 11 agents resolve `model` to `provider-x/model-y`. Each agent's rules apply in file order. The runtime adds only browser and skill rules after them.
- **Upgrade V1 (`9fc90b1`) → HEAD:** the user's `model:` survives in all 11 agents, no `permission:` key is left, and `--check` passes.
- **F011 in the arena:** `validate-subagents.sh` PASS and `make validate` rc=0. The F011 failure on the real HOME is the drift from the V1 copy still installed there. The spec expects that drift until a reinstall.

## Commands (excerpt)

```
python3 -m pytest tests/test_004_002_t7_private_paths.py   → ImportError RULE_RE
pytest test_009_002 + read_map + adapters + bash_policy + u6fix7 + u6fix7b + t5   → 2 failed, 45 passed
pytest test_005_004_t4 + test_005_008_t1 + test_004_001_t7   → 21 passed
cdad-suite.py validate (repo)   → rc=1, collection error
env -i HOME=<arena> CDAD_INSTALL_ROOT=<arena> ./install.sh --check   → PASS (393)
```

## Side effects

- I modified no product, test or state files and made no commits; `git status` is unchanged.
- I ran `make agents` in the repo. It rewrote `agents/` with identical bytes and rebuilt the git-ignored `build/staging`.
- My test copies are under `/tmp/opencode/{arena,up}`. The `RULE_RE` probe was edited only in the arena copy.
- The real HOME was not touched, and no OpenCode processes were left running.
