## Report — implementer / GREEN (006-005 U4)

### Files modified (committed in `014bf2d`, 8 files, +220/−87)
| File | Change |
|---|---|
| `sources/roles/orchestrator.md` | Intake replaced: the five D‑6 rows in order, one condition per row, driven from `status.entry`/`next`; the stale `.cdad/execution.json` condition removed; the transport rule (same runtime ⇒ native tool + `record`; other ⇒ `<skill-dir>/scripts/cdad_dispatch.py --project-root R --runtime X` → `receive`); the renderer instructions kept as "Packet rendering" (not a condition). |
| `sources/agents/adapters/opencode.md`, `…/claude-code.md` | `delegation` section: new entry bullet with `--runtime`, agent travelling in the packet (`REQUEST.json.agent`), credential resolved/injected by the runtime module; the retired `--exec-config` named only as "NOT an option of the entry". |
| `skills/cdad-cycle/references/cli-delegation.md` | Adoption border (migrate → `capabilities` → dispatch with `--runtime`, one source: the `runtimes.json` section); every `--exec-config` mention now explicitly **internal** (interface) and never the orchestrator's path; `Configuration` + "Procedure for another coordinator" repointed to the entry. |
| `skills/cdad-cycle/references/re-entry.md` | Staging step (which the file names) now states that on the native path the entry's `record` verb performs it mechanically and byte‑exact. |
| `scripts/cdad-generate.py` | `"## Delegation (adapter)"` → `"## Delegation"` (V‑4). |
| `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md` | **Regenerated with `make agents`**, never edited by hand. |

Untracked `docs/planning/` and `findings/…` were left alone; nothing installed in HOME; no test file touched; no `--no-verify`, no stash, no push.

### Test → result (final tree, post‑commit)
| Test | Result |
|---|---|
| `test_006_005_u4_single_entry.py` (7 focales, all PD‑20 facts) | **7 passed** |
| all `tests/test_006_005_*.py` (9 files, U1a…U7) | **89 passed** |
| 11 U4 regressions (intake, delegation section, neutral skill, runtime references, context discipline, texts-without-profiles, cdad_generate, bash policy, opencode read map/steps, installer claims, role packet render) | **83 passed** |
| proportional extra regression (24 files reading orchestrators/agents/references/generator: `test_003_006_t3_receive_wiring`, `test_005_006_t6_owner_reviewfix`, `test_004_003_t5_reentry_equivalence`, `test_005_004_t1_dispatch_tool_name`, `test_006_002_u5_transport_equivalence`, `test_006_003_u*`, `test_cdad_adapters_opencode`, …) | **174 passed** |
| `make validate` | **168 PASS / 1 FAIL — F011, ambiental (declared below)** |

Two pre-existing oracles outside the U4 ficha caught the first draft and drove the final shape (both now green): `test_005_006_t6` (A2: CLI invocations must carry the `<skill-dir>` marker) and `test_003_006_t3` (P1/§2.1: the orchestrator body must not copy CLI flags — `--packet` was removed from the mandate and the adapter bullet, keeping only the allowed transversal `--project-root` and `--runtime`).

### Commands and output
1. `python3 -m pytest tests/test_006_005_u4_single_entry.py -q` → `7 passed in 2.05s`
2. `python3 -m pytest <9 focal 006-005 files> -q` → `89 passed in 142.05s`
3. `python3 -m pytest <11 U4 regressions> -q` → `83 passed in 102.69s`
4. `python3 -m pytest <24-file proportional set> -q` → `174 passed in 348.80s`
5. `make staging` twice, `find build/staging -type f | sort | xargs sha256sum | sha256sum` → `2e913b88…83e65` both runs (**deterministic; identical bytes**), staging tree byte-identical to the committed `agents/**` (asserted by focal test 7 and `test_cdad_generate`).
6. `make validate` → `Assert PASS: 168 / Assert FAIL: 1`; the single failure is **F011 (ambiental)**: `scripts/validate-subagents.sh` → `install.sh --check` reports drift against the stale installs in HOME (`~/.claude`, `~/.config/opencode/skills`, `~/.agents/skills`); installing in HOME is forbidden by this packet. Proven pre-existing: a pristine `git archive HEAD` copy (`/tmp/cdad-head`, `make staging` generated there) fails the same check → `❌ install.sh --check failed (rc=1)`. No repo-level assert failed.
7. `git commit` → `014bf2d feat: 006-005 U4 GREEN entrada unica en el mandato, secciones delegation y borde de adopcion`; `git status --short` after commit shows only the two untracked artifacts that are not mine.

### Honest limits
The oracles prove the declared facts are present/co-located (five rows in order without overlap, no stale condition, transport rule, delegation facts, adoption border, label) and that the staging is deterministic and in parity with the sources; they do not prove the model obeys the mandate (that is U6/PD‑22) and prose quality is stage‑4 review's call. `make staging` output lives in git‑ignored `build/`; the full suite belongs to the closer (PD‑21).