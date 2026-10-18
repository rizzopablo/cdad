## Report — implementer (GREEN), `006-003 U2 — instalador sin perfiles`

**Packet:** `006-003-installer-single-profile-delegation-config-implementer-green-002` · contract `docs/specs/006-003-installer-single-profile-delegation-config/spec.md` (§2.1, PD-1a, PD-1g, A-1, INV-3/6/7) · contract sha256 verified `32ed55c4…7419`.

### Modified files (write scope respected — only `install.sh`)

```
$ git show --stat HEAD
 install.sh | 258 +++++++++++++++++++------------------------------------------
 1 file changed, 79 insertions(+), 179 deletions(-)
```

`install.sh` sha256 (committed bytes) = `cf8b650e7c508007709e3366439a125acd28739560395e8c67b15f589ef3eb43`

Nothing else touched: `git status --short` shows only `?? docs/planning/` and `?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md` (pre-existing untracked, deliberately not added). `tests/**` untouched.

### What changed (minimal, per spec §2.1 / D1)

- Removed `PROFILE_FLAG` / `MODEL_PROFILE` / `PROFILE_MARKER`, `resolve_profile`, `write_profile_marker`, the `PROFILE MISMATCH` block, the profile usage text, the premium envs, and the repo-mode `model:` check (`check_agent_file` no longer takes/expects a model; its caller no longer computes `want_model`).
- Retired profile flags now fall through the `--*` arm of `parse_options` → `die` **before any deploy**, rc=1, diagnostic naming the delegation config. The source deliberately does **not** spell the three retired spellings (PD-1a is a literal grep).
- `--basic` and `CDAD_MODEL_PROFILE` are accepted, have no effect, and each emits **one** deprecation line. No `.cdad-models-profile` marker is resolved/written anywhere.
- Ownership manifest no longer writes the `profile` key; header comments about a fixed per-role model corrected.

### Gates — test→result

| Test / command | Result |
|---|---|
| `tests/test_006_003_u2_installer_without_profiles.py` (focal U2) | **7 passed** in 34.40s |
| `tests/test_install_review5_regressions.py` + `tests/test_install_ownership.py` (RED f2c3540 reformulated) | **16 passed** in 248.36s |
| `tests/test_005_004_t2_installer_claims.py` (RED f2c3540 reformulated) | **8 passed** in 8.41s |
| `tests/test_006_003_u1_generator_without_profiles.py` `test_004_001_acceptance_matrix.py` `test_005_004_t1_dispatch_tool_name.py` `test_005_006_t2_intake.py` | **22 passed** in 12.36s |
| `tests/test_004_001_t6.py` `test_003_002_t4_integration.py` `test_004_001_t7_capacity.py` | **21 passed** in 128.73s |
| `tests/test_004_002_t6_landing.py` `test_004_003_t2_plan_review.py` `test_005_005_t4_integration.py` `test_005_008_t3_acceptance.py` | **23 passed** in 102.47s |
| `tests/test_003_003_t2_preflight.py` `test_003_004_t4_real_context.py` `test_003_006_t2_activation.py` `test_003_006_t4_ru2_refused_write.py` `test_004_002_t1_policy.py` `test_004_002_t5_runtime.py` | **70 passed** in 26.57s |
| `tests/test_004_002_t34_reviewfix2.py` `test_004_002_t34_reviewfix3.py` `test_004_002_t7_acceptance.py` `test_004_003_t3_plan_checks.py` `test_005_001_tcorr.py` | **31 passed** in 56.18s |
| `tests/test_005_005_t1_replace_conserved.py` `test_005_005_t3_provenance.py` `test_005_006_t6_owner_reviewfix.py` `test_cdad_adapters_opencode.py` `test_opencode_read_map_and_steps.py` | **21 passed** in 23.63s |
| `tests/test_packet_prepare.py` `test_role_packet_consumers.py` `test_role_packet_render.py` `test_role_packet_review_regressions.py` `test_role_packets.py` | **52 passed** in 166.36s |

Coverage of the gate “todo test que invoque `install.sh`”: all **34** files from `grep -l "install.sh" tests/*.py` were executed (batches above) — **all green**.

| `bash tests/validate-consistency.sh` | **160 PASS / 1 FAIL** — the single FAIL is the declared-environmental `F011: scripts/validate-subagents.sh (active profile)` |
| `make validate` | fails on that same F011 assert (declared); `make:` run stopped at the validator recipe |

Declared failure evidence (pre-existing HOME drift, unrelated to this change — the diff touches no `agents/`, `skills/` or HOME):

```
DRIFT: .../skills/cdad-cycle has 84 file(s), installed has 85
DRIFT: differs <home>/.claude/skills/cdad-cycle/scripts/__pycache__/cdad_packet.cpython-313.pyc
Check: FAIL — drift .claude/agents/cdad-orchestrator.md drift .config/opencode/agents/cdad-orchestrator.md skills .../skills/cdad-cycle ...
```

### Postcondition probes (manual, isolated temporaries only — never HOME)

```
$ bash install.sh --help ; grep -nE -- '--(economical|optimus|premium)|deepseek|glm-|qwen|minimax|sonnet|haiku|opus|mofgw/' help.txt
help rc=0 ; rc=1 (no banned pattern)
```

```
$ CDAD_INSTALL_ROOT=<tmp>/root bash install.sh --basic
basic rc=0 ; deprecation lines = 1 ; marker files = 0 ; 'profile' in manifest = False
```

```
$ CDAD_INSTALL_ROOT=<tmp>/root bash install.sh --economical
reject rc=1 ; deployed files = 0
ERROR: Unknown option: --economical — the installer has no profiles; the model is chosen in the delegation config (delegation.json), not by an installer flag (see --help)
```

```
$ CDAD_MODEL_PROFILE=optimus CDAD_INSTALL_ROOT=<tmp>/root2 bash install.sh
env rc=0 ; deprecation lines = 1 ; marker files = 0
```

```
$ grep -nE -- '--(economical|optimus|premium)' install.sh     -> no output (rc=1)
$ grep -rn 'cdad-models.sh' install.sh scripts/                -> no output (rc=1)
$ grep -rc '^model:' agents/cdad-*.md agents/claude-code/*.md  -> all 0 (rc=1)
$ bash -n install.sh                                            -> SYNTAX OK
```

### Commit

```
44f1561 feat: 006-003 U2 GREEN — instalador sin perfiles (PD-1a/D1/A-1, INV-3/INV-6/INV-7)
```
No `--no-verify`, no `git stash`, no push.

### Notes / conflicts

- No approved oracle was found that still requires profiles — nothing to stop for.
- Deliberately deferred (outside U2): `delegation.json` / `.env.example` creation (U4) and `pending_removal` retirement (U7); a pre-existing `.cdad-models-profile` left by an old install now stays as `pending_removal` until U7 (it is no longer emitted by `uninstall_items`; a manifest-owned one is still retired by `--uninstall`).
- The one failing validator assert is the declared environmental HOME drift; it does not touch `install.sh` behaviour and was neither introduced nor worsened by this diff.
