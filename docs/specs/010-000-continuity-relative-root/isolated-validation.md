The packet matched byte for byte, and the isolated validation of HEAD `aa0348294692e94f570997b83a326c26f217a876` passed on every step.

**Intake (route A).**
- I validated `REQUEST.json` with the installed CLI (`~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py`, absolute project root, v2 context `execution.json`): `validate-request` returned rc=0.
- `render` returned rc=0. Its sha256 `2f349e96…41c0bf` is the same as `PACKET.md`.
- I wrote the prompt I received, from `---cdad-packet-json` to the end, into a temporary file. `cmp` against the render printed `BYTE-EQUAL`, and `validate-packet` on it returned rc=0. I removed both temporary files from `/dev/shm` afterwards.
- The spec's sha256 matches the contract (`623b15e1…737e2`).

**Evidence.** Everything is in `.cdad/evidence/isolated-validate-010-000-20261029T211209Z-r006/`, which git ignores:
- `run.sh` is the exact script that ran.
- `logs/NN-*.cmd`, `.log` and `.rc` hold the command, output and return code of each step; `logs/summary.txt` lists them all.
- `logs/packet-canonical-render.txt` is a copy of the canonical render.
- `src/` is the `git archive HEAD` copy and `root/` is the isolated install root.

| Step | rc | Result |
|---|---|---|
| 00 HEAD | 0 | `aa03482…` |
| 01 `git archive HEAD \| tar -x` | 0 | only the 1330 tracked files; the private file and caches are not tracked |
| 02 / 07 private file and caches | 0 | the private file is not in the copy and no `__pycache__` or `*.pyc` exists, checked before and after |
| 03 `make staging` | 0 | — |
| 04 `install.sh` | 0 | "Verify: PASS — 11 cdad agents present" |
| 05 `install.sh --check` | 0 | "Check: PASS (393 artifact groups in sync with staging/skills)" |
| 06 `make validate` | 0 | `validate-consistency`: Assert FAIL 0; `validate-odoo-specialization`: Assert FAIL 0, "PASS: all postconditions P1..P6 and the A3 criterion verified." |

Steps 04 to 06 ran with `CDAD_INSTALL_ROOT=<absolute evidence path>/root`, `CDAD_SKILL_EXTRA_DIRS` empty, `CDAD_SENSITIVE_PATTERNS` unset and `PYTHONDONTWRITEBYTECODE=1`.

**Limits.**
- **A3 used only the public check.** The copy has no `tests/.sensitive-patterns.local` and `CDAD_SENSITIVE_PATTERNS` was unset, so A3 checked only the built-in private-IP pattern. Its PASS says nothing about the private patterns. I did not read, copy or send the private file, and I did not change any assertion.
- **Write scope.** The packet's write scope is `[]` and the policy declares no temporary folders (`temporary_roots` is `[]`). I wrote only to `.cdad/evidence/…` because the objective declares it as temporary, plus the two files in `/dev/shm`, now deleted.
- **HOME left as is.** I did not change HOME, as `install.sh` says to do when `CDAD_INSTALL_ROOT` is set.
- **Nothing else touched.** I did not change the real product, the tests or the policy. I did not touch the global HOME, change models or publish anything, and I made no commit. `git status` is the same as at the start: the only untracked file is `discovery.md`.
- **Not run.** I did not run pytest, because the full suite is already running elsewhere.

**Modified files:** none in the product. The only new files are the evidence folder above.

## Abstentions
- I can't judge whether the private-pattern part of A3 would pass, because that check needs the private file, which this clean copy correctly leaves out.
