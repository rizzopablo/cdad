# Results — light cycle opencode-read-map-and-steps (2026-09-29)

Verdict of the independent review (Claude, session distinct from the implementer): **conforme, sin bloqueantes**.
Commits: RED `b8039e3`; GREEN + record: see `git log` (same directory name).

## Before / after (same prompt, opencode v2.0.16, agent cdad-test-writer)
| Check | Before (`smoke-before.txt`) | After (`smoke-after.txt`) |
|---|---|---|
| `read` of the approved contract | `Permission denied: read` | read OK (`→ Read ... [limit=3]`) |
| `echo hi` (shell) | ok | ok |
| `wc -l ... \| cat` (shell, pipe) | ok | ok |

Friction baseline (window 2026-09-24 22:00 -> 2026-09-29 00:00, `opencode-session-scan.py --until "2026-09-29 00:00"`,
`baseline-window-2026-09-24_29.txt`): shell 331 ok / 2409 denied; test-writer `read` 0 ok / 36 denied;
one implementer session 2073 identical retries (OpenCode `cost` field 15.86 USD, not billing).
Re-measure after a real cycle with the same script; expected: ~0 shell denials, test-writer reads succeed.

## Verification run by the reviewer (not taken from the implementer's report)
- `pytest tests -q` (TMPDIR on disk): 96 passed, 2 failed = the 2 frozen T6 REDs (`test_004_001_t6.py`, commit 92851b2), baseline documented in 80f9b90.
- New tests: 4/4 pass; RED (b8039e3) failed 4/4 by AssertionError for the contract reasons.
- `validate-odoo-specialization.sh` PASS; `validate-consistency.sh`: only F011, which fails identically on the pre-change HEAD (worktree check) = pre-existing HOME-install debt (T6).
- PD-2: generation twice, byte-identical (both runtimes). Claude Code agents byte-unchanged.
- Install to the real runtimes: models identical before/after for all 11 agents; `--check` PASS (395 groups); 10 agents carry `steps: 300`, orchestrator none; installed test-writer read map has no catch-all. Backup: ~/.cdad-install-backup-2026-09-29-readmap.
- NOT exercised live: enforcement of `steps` (verified in the generated frontmatter and the 1.18.32/2.x agent schema, not by forcing a loop).

## Deviations and incidents (declared, none invalidates the result)
1. RED test used a hardcoded `dir="/tmp/opencode"` for temp dirs (fails on other machines): returned to the test-writer in the same session, fixed, re-verified with an empty TMPDIR.
2. The spec's `context` names the defect location (scripts/cdad-generate.py, read_pairs); the test-writer therefore saw where the bug is (not the code). Accepted for a bugfix contract; RED oracles are behavioral black-box.
3. `write: ask` is active in opencode v2.0.16: in non-interactive `opencode run` the request is auto-rejected ("permission requested: edit ... auto-rejecting"); `--auto` is required (path deny-lists stay in force). The WATCH RULE in the generator fired.
4. The implementer ended its `run` client with a "suite still running" message and no final report, its session stayed alive, then hit `/tmp` inode exhaustion (see 5) and attempted `rm -rf` of stale test dirs, including reviewers' reproduction dirs cited in earlier reviews. The command never completed; nothing was deleted by it. Independent verification replaced its report.
5. Environment: `/tmp` (tmpfs) at 100% inodes (1,047,959 of 1,048,576) while 56 GB free; ~9.7k inodes are `ofap`'s, the rest are in unreadable directories of other users. Needs root inspection. Verification used TMPDIR on disk.
6. Two opencode binaries coexist: PATH `opencode` = 1.18.32 (legacy `session` table; `--agent <mode: subagent role>` hangs silently, `--format json` produced no output); real runtime `~/.opencode/bin/opencode` = v2.0.16 (`session_v2`).

## Follow-ups (not in this cycle)
- 004-002: derive implementation roots from the project path_policy; today read/grep hide only `src/**`, `lib/**` (or odoo dirs), so this repo's scripts/agents/skills are NOT hidden from the test-writer (contract-level invariant only).
- Claude Code step ceiling (`maxTurns`) and its verification: not evidenced as a problem.
- Owner decision: global `/tmp` bash denies in ~/.config/opencode/opencode.jsonc are overridden by the agents' `"*": allow`.
- 003-003: use `opencode-session-scan.py` as the permission-denial metric; a rejection of a legitimate operation is a product defect.
- Orchestration: wait on the session DB, not on the `opencode run` client, which can return before the role finishes.
