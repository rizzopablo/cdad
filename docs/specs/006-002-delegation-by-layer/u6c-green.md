I'll start by reading the contract and the RED test to understand the exact requirements.
Now let me find all `/tmp` mentions in the installable tree.
Now I'll apply the three edits.
Now regenerate the agents and run the focused test.
Focal green. Now the proportional regression: all `test_006_002_*` and tests referencing those artifacts.
All regression groups green. Now verify `make agents` idempotency and `make validate`.
F011 is the documented pre-existing environmental drift (DT-8). Let me confirm the baseline and verify no `/tmp` remains in the repo's `build/staging`.
Baseline confirmed (161 PASS / 1 FAIL = documented DT-8). Now review the diff and commit.
Diff is minimal and scoped. Committing the five files (excluding untracked docs/planning and findings).
Committed. Here is the role report.

## Resultado: GREEN ✅

`tests/test_006_002_u6_context_discipline.py` (RED `300a05c`) pasa con el cambio mínimo; los 4 guards pre-satisfechos siguen verdes y el oráculo de ausencia queda satisfecho.

## Cambios (implementación, fuera de tests/)

| Archivo | Cambio |
|---|---|
| `sources/roles/orchestrator.md` | Regla 4 (línea 108) reescrita en una línea, sin `/tmp`: `- **Stable workspace paths for what must last.** Anything that must last, leave evidence or be read by another process or role (artifacts, receipts, run logs) goes to stable paths of the declared workspace — `.cdad/inbox` for the receipt and the declared workspace for everything else.` |
| `skills/cdad-cycle/SKILL.md` | Puntero de disciplina de contexto (línea 174): se retira la frase «relativized `/tmp` rule»; queda «stable workspace paths for what must last, leave evidence or be read by another process or role (`.cdad/inbox` for the receipt)». |
| `skills/cdad-cycle/references/handoff-prompts.md` | Run logs (línea 628): «named under stable paths of the declared workspace so the evidence is referenceable» (antes `~/tmp/ (never /tmp/)`). |
| `agents/cdad-orchestrator.md` | Regenerado por `make agents` (output declarado). |
| `agents/claude-code/cdad-orchestrator.md` | Regenerado por `make agents` (output declarado). |

No toqué `tests/`, `install.sh`, `cdad-models.sh`, el adaptador, ADR-007 ni los untracked `docs/planning/` y `findings/`.

## Tabla test → resultado

| Comando | Resultado |
|---|---|
| `python3 -m pytest tests/test_006_002_u6_context_discipline.py -q` | **6 passed** |
| `pytest tests/test_006_002_{u1..u6}*.py -q` (suite 006-002) | **37 passed** |
| `pytest tests/test_003_006_{t1,t2,t3}*.py test_003_007_t4… test_004_002_{t5,t7} test_004_003_t5 test_005_004_{t1,t4} test_005_006_{t1,t6} test_005_007_t5 test_005_009_t3 test_cdad_generate.py -q` | **157 passed** |
| `pytest tests/test_005_002_* test_005_003_* test_005_005_t2_docs_policy test_005_006_t2_intake test_005_009_{t1,t2} test_install_review5_regressions test_opencode_read_map_and_steps test_packet_prepare test_role_packet_{consumers,review_regressions} tests/pd10_permission_semantics.py -q` | **115 passed, 2 skipped** |
| `bash tests/validate-consistency.sh` | **161 PASS / 1 FAIL** (F011 = DT-8 baseline) |
| `bash tests/validate-odoo-specialization.sh` | **67 PASS / 0 FAIL** |
| `make validate` | 161 PASS / **1 FAIL (F011 = DT-8)** — baseline declarado |
| `make agents` ×2 (idempotencia) | diff vacío (checksums idénticos) |

## Comandos con salida

```
$ make agents
python3 scripts/cdad-generate.py --runtime opencode --stack odoo --profile optimus --out build/staging
cdad-generate: 12 files -> build/staging/agents/opencode (+ manifest.json)
python3 scripts/cdad-generate.py --runtime claude-code --stack odoo --profile optimus --out build/staging
cdad-generate: 12 files -> build/staging/agents/claude-code (+ manifest.json)
cp build/staging/agents/opencode/cdad-*.md agents/
cp build/staging/agents/claude-code/cdad-*.md agents/claude-code/

$ grep -rn "/tmp" skills/ agents/ sources/ | grep -E '\.(md|json|sh|py|yaml|yml):'
NO /tmp in skills/agents/sources
$ grep -rn "/tmp" build/staging/ | grep -E '\.(md|json|sh|py|yaml|yml):'
NO /tmp in build/staging

$ python3 -m pytest tests/test_006_002_u6_context_discipline.py -q
......                                                                   [100%]
6 passed in 1.52s

$ sha256sum agents/*.md ... (antes) ; make agents ; sha256sum (después)
IDEMPOTENT: same checksums after 2nd make agents

$ make validate | grep -E '^(Assert PASS|Assert FAIL|FAIL)'
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
Assert PASS: 161
Assert FAIL: 1
```

**F011 = DT-8** es el drift ambiental preexistente y documentado (el validador compara contra las copias instaladas en HOME: `.claude/agents/*`, `.config/opencode/agents/*`, `skills/…` stale), ajeno a este diff. `make validate` queda en el baseline declarado **161 PASS / 1 FAIL**; **F001 (PD-11) y el control 005-004 PD-1 pasan**.

## Commit

```
a3b54e6084f56f811366fcda8d2a4cedfb8c459b
feat: 006-002 enmienda 002 GREEN — /tmp fuera del texto instalable

 agents/cdad-orchestrator.md                     | 2 +-
 agents/claude-code/cdad-orchestrator.md         | 2 +-
 skills/cdad-cycle/SKILL.md                      | 2 +-
 skills/cdad-cycle/references/handoff-prompts.md | 4 ++--
 sources/roles/orchestrator.md                   | 2 +-
 5 files changed, 6 insertions(+), 6 deletions(-)
```

Commit sin `--no-verify`, sin `git stash`, sin push. Ningún test editado.
