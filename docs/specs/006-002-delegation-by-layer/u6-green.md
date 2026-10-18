I'll start by reading the approved contract and the failing tests.
Now let me read the implementation sources I'll need to modify.
Now let me look at the generator composition and test helpers.
Let me run the focal test to confirm the RED state, and generate staging to inspect.
Let me examine the validators, the coupled tests, and the generator's text handling.
Now I understand the full picture. Let me implement the four context rules in the orchestrator source.
Now regenerate the agents and verify idempotency.
Focal green. Now let me run the full gate list.
Now verify `make agents` idempotency and run `make validate`.
F011 fails due to installed-vs-repo drift. Let me check whether this drift predates my change using a clean worktree at HEAD.
`make validate` reaches the documented baseline (161 PASS / 1 FAIL, F011 = DT-8 environmental drift, pre-existing — proven by the HEAD worktree failing identically). Let me review the final diff.
Now commit (only my files — not the untracked docs/planning or findings).
GREEN de U6 completado. Reporte de rol:

## Cambios (5 archivos, +25 líneas — todos dentro del write_scope)

| Archivo | Cambio |
|---|---|
| `sources/roles/orchestrator.md` | Bloque "Context discipline" con las **4 reglas compactas, una línea cada una**, en la sección de directivas (D-5) |
| `skills/cdad-cycle/references/orientation.md` | §1 declara que **solo es dueño de «vista primero»** y **cita** la rotación (no la duplica) |
| `skills/cdad-cycle/SKILL.md` | §4: **una frase-puntero** a las reglas, sin duplicarlas |
| `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md` | Salidas declaradas regeneradas con `make agents` |

Las 4 reglas (PD-6): (1) orientarse primero con la vista compacta `status`, sin volcar state/ledger/skill completa, **citando `references/orientation.md` §1**; (2) rotar la sesión en bordes de tarea, no a mitad de unidad; (3) no auto-reparar — re-despachar al rol nombrando el defecto; (4) nunca `/tmp` como canal ni workspace (recibo → `.cdad/inbox`, temporales → workspace declarado).

No toqué `tests/`, `install.sh`, `cdad-models.sh`, el adaptador, ADR-007, ni los untracked `docs/planning/` y `findings/…` (siguen untracked).

## Comandos y evidencia

```
$ python3 -m pytest tests/test_006_002_u6_context_discipline.py -q
7 passed in 1.46s

$ python3 -m pytest tests/test_006_002_u{1..6}_*.py \
    tests/test_005_004_t1_*.py tests/test_005_004_t4_*.py \
    tests/test_005_005_t3_*.py tests/test_005_009_t3_*.py \
    tests/test_005_010_t3_*.py -q
78 passed in 10.97s

$ FILES=$(grep -l "cdad-orchestrator\|SKILL.md\|orientation" tests/*.py)   # 42 archivos
$ python3 -m pytest $FILES -q
337 passed, 2 skipped in 301.14s (0:05:01)

$ make agents   # 2ª corrida: sha256 idéntico (IDEMPOTENT)

$ make validate
Assert PASS: 161 / Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
```

**F011 = DT-8 es drift ambiental preexistente, ajeno a este diff** (lo prueban los GREEN previos u1–u4 y lo verifiqué en un worktree limpio en `HEAD`: `validate-subagents.sh` ya fallaba igual por copias stale en HOME: `.claude/agents/*`, `.config/opencode/agents/*`, `skills/…`). `make validate` queda en el baseline declarado **161 PASS / 1 FAIL**. `F001` (PD-11) y el control 005-004 PD-1 pasan.

## Tabla test → resultado

| Test | PD | Resultado |
|---|---|---|
| `rule1_orient_first_…_without_dumps` | PD-6(1) | ✅ |
| `rule2_rotate_…_not_mid_unit` | PD-6(2) | ✅ |
| `rule3_no_self_repair_…_defect` | PD-6(3) | ✅ |
| `rule4_never_tmp_as_channel_or_workspace` | PD-6(4)/INV-4 | ✅ |
| `rule4_declares_the_sanctioned_alternative_to_tmp` | PD-6(4)/INV-4 | ✅ |
| `orchestrators_reference_the_view_first_owner` | PD-6 (cita) | ✅ |
| `no_installable_text_instructs_tmp` | PD-6(4)/INV-4 | ✅ |
| 006_002 U1–U5 + acoplados (005_004_t1/t4, 005_005_t3, 005_009_t3, 005_010_t3) | — | ✅ 78 passed |
| 42 tests que leen orquestadores/SKILL.md/orientation | — | ✅ 337 passed, 2 skipped |

## Commit

```
900fa58 feat: 006-002 U6 GREEN — four context rules in the orchestrators (PD-6/INV-4)
 5 files changed, 25 insertions(+)
```

Sin `--no-verify`, sin `git stash`, sin push.

**Límite honesto (PD-6):** el test prueba que la regla **existe**, no que se **obedezca**; la única evidencia de comportamiento es el transcript de la corrida de aceptación (U8), que es una muestra.
