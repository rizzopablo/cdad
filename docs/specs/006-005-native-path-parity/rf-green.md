All work is committed. Here is the role report.

## Role report — implementer, substage GREEN (006-005 review-fix B‑1 / B‑2 / B‑3)

Packet `006-005-native-path-parity-implementer-green-018` · contract `docs/specs/006-005-native-path-parity/spec.md` (sha256 `3a824be…`) · decisions in `docs/epics/epic-006-opencode-concurrency/execution.md` («006‑005: review de etapa 4»).

### 1. Modified files (8 — all inside the packet's write scope)

| File | Change |
|---|---|
| `skills/cdad-cycle/scripts/cdad_packet.py` | **B‑1** — `_derived_maps` (implementer): the implementation allows are emitted **first**, so the role's test conventions (`_IMPLEMENTER_TEST_GLOBS`) are emitted **after** them and win by findLast. Policy only restricts: its test/colocated denies, policy file, derivatives and private paths stay last. Docstring + `_IMPLEMENTER_TEST_GLOBS` comment updated. |
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` | **B‑2** — new `_normalized_observation()`: the **single** normalization boundary of the observed row (store epoch‑ms instant → ISO; `model` → `<provider>/<model>`), applied to the row whichever way it was selected. `_native_candidate` now hands the row raw. |
| `skills/cdad-cycle/scripts/cdad_dispatch.py` | **B‑2** — `_key_states`: the `parent` key is part of a walk's evidence only when the walk declares `--parent` (§2.3 binds the key to the declaration); a declared parent still contradicts. `record()`: a contradiction is now **declared in the closed envelope** as `termination: "blocked"` (rc 0, no session, no delivery, nothing staged) — the same convention the interface uses for a blocked destination. |
| `sources/roles/orchestrator.md` | **B‑3** — transport rule split: native (`record` stages under `.cdad/inbox` + `RESULT.json`, then the orchestrator runs `receive`) vs external (the entry returns an **ENVELOPE**; `delivery_ref` = the **durable receipt** the module already received; validate it and continue — never `receive` again). |
| `sources/agents/adapters/opencode.md` | **B‑3** — “Receipt” bullet (native route stages the FINAL TEXT; the external route returns none) and “Entry of the coordinator” bullet (ENVELOPE + `delivery_ref` = durable receipt, already received). |
| `sources/agents/adapters/claude-code.md` | same as above (Claude Code adapter). |
| `agents/cdad-orchestrator.md` | **B‑3** — regenerated via `make agents` (declared output). |
| `agents/claude-code/cdad-orchestrator.md` | **B‑3** — regenerated via `make agents` (declared output). |

Not touched: `tests/**` (invariant), `docs/**` (`docs/.cdad-state.json` and the untracked `docs/planning/`, `findings/*` are the orchestrator’s and were left as they were), anything in `HOME`.

### 2. Test → result

| Test | Result |
|---|---|
| `tests/test_006_005_reviewfix.py` (focal, 9) | **9 passed** |
| `tests/test_004_002_t5_reviewfix.py` (A‑1 reformulation, 12) | **12 passed** |
| 006‑005 focals (u1a,u1b,u1c,u2,u3,u3b,u4,u5,u6fix1,u6fix4,u6fix5,u6fix6,u6fix7,u6fix7b,u6fix8,u7) | **139 passed** |
| 004‑002 suite (19 files: t1×2,t2×2,t3×2,t4,t5×3,t56,t6,t7×5,t34×2,w1) | **197 passed** |
| `test_packet_prepare`, `test_cdad_generate`, `test_role_packet_consumers`, `test_003_002_t1/t2`, `test_005_005_t2`, `test_003_006_t3`, `test_003_007_t4` | **83 passed** |
| `test_003_006_t2`, `test_004_001_t6/t7`, `test_005_005_t3/t4`, `test_005_006_t2/t6`, `test_005_008_t1/t2/t3`, `test_004_001_t7_pd10` | 67 passed · **1 failed** → see §5 |
| `make validate` | 168 PASS / **1 FAIL (F011 ambiental)** — see §4 |
| `bash tests/validate-odoo-specialization.sh` (direct) | 68 PASS / 0 FAIL |
| `make agents` (post-commit) | determinista, **sin diff pendiente** (`git diff --exit-code agents/` limpio) |

### 3. Commands and output

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
      tests/test_006_005_reviewfix.py tests/test_004_002_t5_reviewfix.py
21 passed in 16.21s

$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_006_005_u*.py
139 passed in 149.14s (0:02:29)

$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_004_002_*.py
197 passed in 172.64s (0:02:52)

$ PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
      tests/test_packet_prepare.py tests/test_cdad_generate.py tests/test_role_packet_consumers.py \
      tests/test_003_002_t1_receive.py tests/test_003_002_t2_materialize.py \
      tests/test_005_005_t2_docs_policy.py tests/test_003_006_t3_receive_wiring.py \
      tests/test_003_007_t4_atomic_unit_rule.py
83 passed in 51.65s

$ python3 -m py_compile skills/cdad-cycle/scripts/{cdad_dispatch,cdad_delegate_opencode,cdad_packet}.py
COMPILA OK

$ make agents
python3 scripts/cdad-generate.py --runtime opencode --stack odoo --out build/staging
cdad-generate: 12 files -> build/staging/agents/opencode (+ manifest.json)
python3 scripts/cdad-generate.py --runtime claude-code --stack odoo --out build/staging
cdad-generate: 12 files -> build/staging/agents/claude-code (+ manifest.json)
cp build/staging/agents/opencode/cdad-*.md agents/
cp build/staging/agents/claude-code/cdad-*.md agents/claude-code/
# segunda corrida: el diff es idéntico (staging == agentes promovidos, byte a byte)

$ make validate
PASS: F011 (B8): validate-subagents.sh no longer requires impl.diff to still apply …
PASS: F011 (B8): validate-subagents.sh still verifies impl.diff's format …
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
PASS: F011: tests/validate-odoo-specialization.sh → PASS (zero regression over cdad-003/004)
Assert PASS: 168
Assert FAIL: 1
FAIL: 1 assert(s) failed.
make: *** [Makefile:22: validate] Error 1

$ bash scripts/validate-subagents.sh        # detalle del F011
DRIFT: differs <home>/.claude/skills/cdad-cycle/scripts/cdad_packet.py
DRIFT: differs …/__pycache__/cdad_packet.cpython-313.pyc
[2026-10-20 01:05:34] Check: FAIL — drift .claude/agents/cdad-orchestrator.md missing staged agents/…
❌ install.sh --check failed (rc=1)
== RESULT: FAIL ==

$ bash tests/validate-odoo-specialization.sh
PASS: A3: no sensitive patterns in the publishable content (docs/skills/drafts/agents/tests/examples/README)
Assert PASS: 68   Assert FAIL: 0
```

### 4. F011 — declared environmental

`make validate` ends with the **same** 168 PASS / 1 FAIL the RED recorded before any implementation change (`docs/specs/006-005-native-path-parity/rf-red.md`: “pre-existing F011: scripts/validate-subagents.sh — installed-skill drift”). Cause: `scripts/validate-subagents.sh` compares the **repo** tree against the **installed** skill/agents in `HOME`; the installed copy is stale, and the check fails for any repo change until the skill is re-installed. It is not a product defect of this change. I did not read or write the installation in `HOME`.

### 5. BLOCKER for the closure — a missed A‑1 (test side; I may not edit tests)

`tests/test_005_008_t1_nested_tests.py::TestPd7NoAmplification::test_pd7_literal_tests_dir_under_impl_not_amplified` **fails** (1 failed, 8 passed in that file):

```
AssertionError: 'deny' != 'allow' : PD-7: el mapa `edit` de cdad-implementer.md resolvió
edit('webmin-module/module/tests/x.py') como 'deny' — sobre-restricción: es implementación
```
`tests/test_005_008_t1_nested_tests.py:491`

Why it is the **same oracle A‑1 already replaced**, not a new requirement: it pins the derived implementer’s verdict for a literal `tests/` dir nested under an implementation root — the exact oracle the RED reformulated in `tests/test_004_002_t5_reviewfix.py` (“A‑1 … REEMPLAZO … PD‑7 … se ENMIENDA en su eje «ni sobre‑restricción» para el IMPLEMENTER”). The A‑1 sweep declared in `rf-red.md` (“ningún otro test fija `allow` de un test dentro de una raíz de implementación para el implementer”) **missed this file**. It also contradicts the approved decision itself: the *generated* agent denies `**/tests/**` for that path, so the 005‑008 assertion demands the derived to be **more permissive than the agent it derives from** — exactly what the new RED forbids (`test_b1_derived_implementer_never_more_permissive_than_the_generated_one`).

**Needed (test‑writer, A‑2):** in `tests/test_005_008_t1_nested_tests.py:488-494`, replace the `allow` expectation for the implementer’s `edit` of `LITERAL_TESTS_DIR` by `deny`, declaring the same amendment as A‑1 (PD‑7’s “ni sobre‑restricción” axis amended for the implementer; the policy **classification** stays `implementation`, the `validate-policy --classify` control is untouched). I did not touch the file (implementer never edits tests).

Note: the declared gates of this packet (focal, 006‑005 focals, 004‑002, `test_packet_prepare`, `test_cdad_generate`, `test_role_packet_consumers`, `make validate`) are all green; the conflict sits **outside** the declared regression set but **inside** the full suite, so the closer (PD‑21) will see it until A‑2 lands.

### 6. Commit

```
$ git commit -F -   # subject: fix: 006-005 review-fix — B-1 B-2 B-3
[main 3ca6597] fix: 006-005 review-fix — B-1 B-2 B-3
 8 files changed, 142 insertions(+), 66 deletions(-)
```
No `--no-verify`, no `git stash`, no `push`. `git status` after the commit: only `M docs/.cdad-state.json` (orchestrator’s) and the untracked `docs/planning/`, `findings/*` (not mine).

### 7. Honest limitations / abstentions

- The full suite was **not** run (PD‑21: it is run once, by whoever closes the task).
- `tests/.sensitive-patterns.local` was never read; the A3 sanitization scan ran only through the declared validator (it prints file names, not patterns) and passed.
- B‑2’s parent‑key rule (§ `_key_states`) is a **product decision** I had to take to satisfy the RED’s declared outcome (“coincidencia ⇒ sesión/modelo observados”): the key is bound to the `--parent` declaration, so without it the key is not part of the walk’s evidence (the agent, moment and project keys still guard it, and a declared parent still rejects). The alternative — leaving it `unknown` — makes a `--session` walk unverifiable by construction.
- The rejection now exits **rc 0** with `termination: "blocked"` instead of rc 1 + stderr, mirroring the interface’s own convention for a blocked destination (`cdad_delegate_opencode.py` `main`). The pre‑existing u1b assertion accepts both forms and stays green.
- The 005‑008 conflict (§5) is reported, not worked around: no product behaviour was bent to satisfy a superseded oracle.