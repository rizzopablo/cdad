## Packet validation (route C)

| Check | Result |
|---|---|
| `PACKET.md` sha256 vs `packet_sha256` | `1cebb80108f4…26` — **match** |
| `cdad_packet.py validate-packet` (request + state binding + packet) | rc=0 |
| `cdad_packet.py render` vs `PACKET.md` (complete bytes) | **byte-identical** (`diff` empty) |
| contract `spec.md` pin | `fc6b2ccc…5d64` — match |
| plan pin v2 | `2ae8ada3…6685` — match |
| owner decision `plan-v2-1` | `8f1810ba…9c2d` — match |

Validated; executed only that packet.

## Implemented (V2-1 enabling step, T2)

**1. `skills/cdad-cycle/packets/substages/test-writer-post-audit.md`** — now single-subphase: apply only the audited/approved AUDIT changes to EXISTING tests, verify every untouched test still passes, keep updated vs intact evidence separate, then stop. Explicit prohibitions: new tests, RED, implementation, full suite. (Old text: "…verify every untouched test still passes, **then add contract-mapped RED tests**".)

**2. `skills/cdad-cycle/references/handoff-prompts.md`** — three surgical corrections:
- §POST-AUDIT: task is one subphase; `THREE parts` → `TWO`; PART 3 (RED) and the "final run of the ENTIRE suite" replaced by a **STOP** block; expected output keeps PART 1/PART 2 and separate run evidence; orchestrator notes now state the three-dispatch sequence POST-AUDIT → RED → GREEN.
- RED §"If you already completed the POST-AUDIT…" (cross-ref 1): describes the separate dispatch; a feature with no affected tests goes straight to RED.
- RED prompt `IMPORTANT:` line (cross-ref 2): POST-AUDIT is never part of this session; stop and report if the audited tests aren't updated.

No other file changed. `git status --short` on `skills/cdad-cycle/scripts/`, `docs/specs/…/spec.md`, `plan.md`: empty.

## Mechanical composition proof (same order/separator as `render_packet`, `cdad_packet.py:1798-1801`)

`common.md` + `\n` + `roles/test-writer.md` + `\n` + `substages/test-writer-post-audit.md`

```
common.md                             901 bytes  37609c566bf8…
roles/test-writer.md                  282 bytes  5f52650efed9…
substages/test-writer-post-audit.md   583 bytes  d709f82ab040…
composed static block                1768 bytes
(a) "then add contract-mapped RED tests" present: False   | regex \badd\b…\bRED\b: 0 hits | "contract-mapped": 0 | "combined session": 0
(b) apply only the audited+approved changes to EXISTING tests: PRESENT | verify untouched still passes: PRESENT |
    separate updated/intact evidence: PRESENT | "Then stop: this is ONE subphase": PRESENT |
    "Do NOT write new tests": PRESENT | "do NOT start RED": PRESENT | "do NOT implement": PRESENT |
    "do NOT run the full suite": PRESENT
(c) 1768 <= 12000 (CDAD_STATIC_BLOCK_LIMIT default, untouched in the renderer): True
(d) control positivo — test-writer-red.md still demands "fails for the expected assertion": True
    (sha256 3dfd2985df0b3bd1a83e5ed4d082489ae24f094793ee432cb5e737df77ab8859)
```

## Derived outputs — determinism

```
$ make staging
cdad-generate: 12 files -> build/staging/agents/opencode (+ manifest.json)
cdad-generate: 12 files -> build/staging/agents/claude-code (+ manifest.json)
$ make agents        (re-runs staging, then cp build/staging/agents/*.md → agents/)
$ git status --short
 M skills/cdad-cycle/packets/substages/test-writer-post-audit.md
 M skills/cdad-cycle/references/handoff-prompts.md
?? docs/specs/010-000-continuity-relative-root/discovery.md   ← pre-existing, untracked before this task
$ git diff --stat -- build agents      → empty (no derived change)
$ grep -rn "then add contract-mapped RED tests" build/ agents/   → no match (rc=1)
$ grep -rln "contract-mapped" build/ agents/                    → no match (rc=1)
```
No derived copy carries the old instruction; nothing was hand-patched.

## `install.sh` publication (read-only verification)

`install.sh:46` `SOURCE_SKILLS_DIR="$SCRIPT_DIR/skills"`; `install.sh:66` `SKILLS=(cdad-cycle …)`; `sync_skill_to` publishes **per file** via `find "$src" -type f -print0` → `stage_owned_file` per destination runtime (`~/.config/opencode`, `~/.agents`, `~/.claude`). `find skills/cdad-cycle -type f -name test-writer-post-audit.md` → `skills/cdad-cycle/packets/substages/test-writer-post-audit.md` (583 B): included automatically, no `install.sh` change needed. No global installation executed.

## Tests run (focused + proportional, no full suite)

| Command | Output |
|---|---|
| `python3 -m pytest -q tests/test_role_packet_render.py tests/test_006_004_u3_principle_single_source.py tests/test_packet_prepare.py tests/test_role_packet_consumers.py tests/test_role_packets.py tests/test_role_packet_review_regressions.py` | **67 passed** (214.32 s) |
| `python3 -m pytest -q tests/test_005_005_t2_docs_policy.py tests/test_006_002_u4_skill_without_models.py tests/test_006_002_u6_context_discipline.py tests/test_006_006_u3_review_route_and_gate.py tests/test_003_007_t1_reference_classes.py tests/test_005_003_t6_packet_contract.py tests/test_008_004_packet_enforcement.py` | **76 passed** (44.26 s) |
| `make validate` | 182 PASS / **1 FAIL — pre-existing** |

**Honest note on `make validate`:** the single failure is `F011: scripts/validate-subagents.sh → install.sh --check failed (rc=1)`. It is **not caused by this change**: the same check fails on a clean `git worktree add … HEAD` checkout (`❌ install.sh --check failed (rc=1)`), and its drift list includes files this task never touched (installed `cdad_packet.py`, `cdad_continuity.py`, `__pycache__`, agent copies). My two files were byte-in-sync with the installed copies before and now appear as drift, which is the expected consequence of the packet's "no global installation" restriction. Full suite is the closer's gate and was not run.

## Commit

`affd5fea feat: make the POST-AUDIT packet instruction single-subphase (V2-1)` — 2 files, +17/−38; body carries the composition proof, derived determinism, hashes and the spec/plan/renderer pins.

`test-writer-post-audit.md` → `d709f82ab040444426ce2d78630b367b8d083b4a42b189735a5a7896187be4de`
`handoff-prompts.md` → `3262048cb3c98b325a3224243ac526740db67a3f9b0696c824d8dda96e7dff70`

No test file was modified; no push, no publication, no global install.