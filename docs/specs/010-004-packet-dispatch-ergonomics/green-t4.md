GREEN T4 complete. Report follows.

## 1. Promise → file:line (sources and regenerated orchestrators)

**(a) stable token `--route C`, invoked as `render --route C` on the published request**

| Surface (source) | Line |
|---|---|
| `sources/roles/orchestrator.md` | `:63` block opens; token at `:65` — `` `<skill-dir>/scripts/cdad_packet.py render --route C` (`--request .cdad/packets/<packet_id>/REQUEST.json`, inside the project root) `` |
| `sources/agents/adapters/opencode.md` | `:79` block; token `:81` |
| `sources/agents/adapters/claude-code.md` | `:93` block; token `:95` |
| `skills/cdad-cycle/references/handoff-prompts.md` | `:17-22` bullet “Route C — explicit file backup”; token `:18-19` |

**(b) identification travels alone, never recomposed/retranscribed/with body**
orchestrator `:66-67` (“moved exactly as emitted, never recomposed, retranscribed or accompanied by the packet body”); opencode adapter `:82-83`; cc adapter `:96-97`; handoff `:20-22`.

**(c) fallback preserved without contradiction**
- route A valid and transferred unaltered: orchestrator `:68-69`, opencode `:85`, cc `:99`, handoff `:23-24`.
- A+C rejected even when the inline coincides; divergent inline not rescued by C: orchestrator `:69-71`, opencode `:86-87`, cc `:100-101`, handoff `:25-26`.
- no invented routes/markers/fallbacks, none removed: orchestrator `:71-72`, opencode `:87-88`, cc `:101-102`, handoff `:26-27`.

**Regenerated orchestrators (full regeneration, never hand-patched)**
| Derived agent | from role source | from adapter |
|---|---|---|
| `agents/cdad-orchestrator.md` | `:60` block, token `:62`, A+C `:67` | `:287` block, token `:289`, A+C `:294` |
| `agents/claude-code/cdad-orchestrator.md` | `:61`, token `:63`, A+C `:68` | `:288`, token `:290`, A+C `:295` |
| `build/staging/agents/opencode/cdad-orchestrator.md` | `:60`, token `:62` | `:287`, token `:289` |
| `build/staging/agents/claude-code/cdad-orchestrator.md` | `:61`, token `:63` | `:288`, token `:290` |

**Same-section contradiction corrected (cited as required):** `handoff-prompts.md:5` presented `.cdad/execution.json` as the universal preparation entry — replaced by the v2-only condition (`:5`, “Every new preparation runs on a v2 execution”); the stale `schema_version: 1` context example in that section was replaced by a pointer to the canonical `.cdad/executions/<execution_id>/execution.json` and to `project-execution.md` §3 as its owner (`:34-39`), against §4.6 / PC-04 / PC-12.

**Already compliant, not touched:** `sources/roles/architect.md:35-43` (intake declaration, control positive) and both adapters' “Byte-identical packet” bullet; no other file audited or rewritten.

## 2. Commit scope

`git show --name-status` / `--numstat` of `8958c366e701f784df84b3c68317c04d63c33d94` (`feat(010-004): GREEN T4 - despacho por ruta C en las cuatro superficies y derivados regenerados`):

```
M  23  0   agents/cdad-orchestrator.md
M  23  0   agents/claude-code/cdad-orchestrator.md
M  21 13   skills/cdad-cycle/references/handoff-prompts.md
M  11  0   sources/agents/adapters/claude-code.md
M  11  0   sources/agents/adapters/opencode.md
M  12  0   sources/roles/orchestrator.md
6 files changed, 101 insertions(+), 13 deletions(-)
```

All six paths are inside the write scope. `git diff --stat HEAD~1 HEAD -- tests docs scripts install.sh skills/cdad-cycle/scripts skills/cdad-cycle/SKILL.md` → empty.

## 3. Regeneration and determinism (real output, two runs)

Run 1: `make staging` → `cdad-generate: 12 files -> build/staging/agents/opencode (+ manifest.json)` / `… claude-code …`, rc=0. `make agents` → same two lines plus `cp build/staging/agents/opencode/cdad-*.md agents/` and `cp … claude-code …`, rc=0.

Commit `8958c366` was made on that tested tree; **run 2** then repeated both entrypoints (`make staging` rc=0, `make agents` rc=0, same four lines each).

```
git status --porcelain -- build/staging agents     → (empty)
git diff --stat -- build/staging agents            → (empty)
```

Honest caveat: `build/` is gitignored (`.gitignore:12`), so both git commands are trivially empty for staging. Real staging proof, `find build/staging -type f | sort | xargs sha256sum | sha256sum`:

- after run 1: `c394a0c7d9584c4202c99c2a7147be13297549a8f17ad1102b5e8655ee7d3d7f`
- after run 2: `c394a0c7d9584c4202c99c2a7147be13297549a8f17ad1102b5e8655ee7d3d7f` (identical)

## 4. Verification

| Command | Result |
|---|---|
| `pytest tests/test_010_004_t4_red.py -q` (before) | `2 failed in 0.41s`, rc=1 |
| `pytest tests/test_010_004_t4_red.py -q` (final tree) | `2 passed in 0.42s`, rc=0 |
| `pytest tests/test_cdad_generate.py -q` | `10 passed in 2.59s`, rc=0 |
| `pytest tests/test_005_006_t6_owner_reviewfix.py -q` | `5 passed in 0.10s`, rc=0 |
| `make validate` | `Assert PASS: 182` / `Assert FAIL: 1`, rc=2 — see block below |
| `python3 scripts/cdad-suite.py close --all --evidence-root .cdad/evidence/t4-full-suite` | `1864 passed, 5 skipped in 3373.26s (0:56:13)`, **rc=0**, `canary_delta_lines=0`, evidence `…/attempt-20261030T233338118253Z-1859495-e7d718fd` |

**Block to report (not worked around):** `make validate` cannot reach rc=0 here. Its single failure is F011 (`scripts/validate-subagents.sh` → `install.sh --check` drift against the stale **global** installation). I measured the same script at `HEAD` (`0d015234`) in a throwaway detached worktree outside the repo: `Assert PASS: 182` / `Assert FAIL: 1`, same F011, and the drift set includes files I never touched (`…/skills/cdad-cycle/packets/substages/test-writer-post-audit.md`). Fixing it would require updating the installed copy / global install, which this packet forbids. All repo-internal assertions pass; F011 is pre-existing environmental drift (D-1).

**Disclosure — first full-suite run:** it returned rc=1 (`attempt-20261030T223309058329Z-1195400-a2422c4e`, `1 failed, 1863 passed`) on HALLAZGO A2 in **my own** text (`cdad_packet.py render --route C` without the `<skill-dir>` marker, `tests/test_005_006_t6_owner_reviewfix.py:157`). I fixed the wording to `<skill-dir>/scripts/cdad_packet.py render --route C`, regenerated, re-ran the affected oracle (5 passed), and re-ran the full suite once after the change — the closure evidence above is the post-fix run. The failed attempt is retained in the evidence root, not deleted.

## 5. Declarations

- No edits to `tests/**` (the RED guard is byte-identical), `docs/**`, `skills/cdad-cycle/scripts/**`, `scripts/cdad_packet.py`, `install.sh`, or `~/.config/opencode/**`; no global install; no push.
- No new files created; no CLI or product behavior changed (T4 is documentary). Both edits are text in the four declared surfaces.
- No model names and no sandbox promises in sources or derivados (PD-1e/PD-7a/PD-15); `test_cdad_generate.py` green.
- No T5/T6 work. Working tree clean outside the write scope; the only untracked path is the pre-existing `docs/specs/010-000-continuity-relative-root/discovery.md`, untouched.
- Packet itself: route C validation passed before working — `validate-request` rc=0, `validate-packet` rc=0, `PACKET.md` byte-identical to the canonical full render, and the received identification matched `render --route C` on all seven fields; spec pin `fc6b2ccc…` confirmed.