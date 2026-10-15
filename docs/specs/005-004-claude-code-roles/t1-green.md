# Informe GREEN — 005-004-claude-code-roles, T1 (subetapa implementer-green)

**Rol:** implementer · **Feature:** 005-004-claude-code-roles · **Tarea:** T1
**Contrato:** docs/specs/005-004-claude-code-roles/spec.md (sha256 79d57e0a…)
**Focal congelado (oráculo, no editado):** tests/test_005_004_t1_dispatch_tool_name.py
**Commit:** cc6e5a57205bc5e0941c5e571015d4c113f3fcc2 (`feat:`)

## 1. Cambio (archivo:línea)

Declaración de la herramienta de despacho real de Claude Code (`Agent`) en la
fuente única (generador) y en el enunciado del adaptador, con la salida declarada
regenerada:

| Archivo:línea | Antes | Después |
|---|---|---|
| scripts/cdad-generate.py:453 | `tools += ["Edit", "Write", "Task"]` | `tools += ["Edit", "Write", "Agent"]` |
| sources/agents/adapters/claude-code.md:13 | `... writer roles; Task` | `... writer roles; Agent` |
| agents/claude-code/cdad-orchestrator.md:4 | `tools: Read, Grep, Glob, Bash, Edit, Write, Task, Skill` | `tools: Read, Grep, Glob, Bash, Edit, Write, Agent, Skill` |

Notas de alcance:
- La declaración vive UNA VEZ en el generador (`cc_tools`, única fuente editable
  por INV-2/PD-9); el adaptador solo la enuncia; el derivado es salida declarada
  regenerada con `make agents` (nunca editada a mano).
- El lado OpenCode CONSERVA su nombre (`Task`): no se tocó.
- No se tocaron los `tools:` de los otros diez agentes CC con/sin guard (control
  del focal `test_pd1_iv_ten_cc_agents_keep_their_tools_lines`).
- No se tocó `tests/`. `docs/.cdad-state.json` (binding de despacho del
  orchestrator) quedó fuera del commit por estar fuera del write scope.

## 2. Tabla test → resultado (focal RED → GREEN)

| Test | Antes (RED) | Después |
|---|---|---|
| test_pd1_i_cc_orchestrator_declares_agent_dispatch_tool | FAIL (AssertionError) | PASS |
| test_pd1_ii_no_cc_agent_declares_task_as_dispatch_tool | FAIL (AssertionError) | PASS |
| test_pd1_ii_opencode_side_keeps_its_tool_name | PASS (control) | PASS |
| test_pd1_iii_adapter_owns_the_cc_dispatch_tool_name | FAIL (AssertionError) | PASS |
| test_pd1_iii_reference_and_skill_name_the_same_tool | PASS (control) | PASS |
| test_pd1_iv_generator_staging_is_idempotent | PASS (control) | PASS |
| test_pd1_iv_ten_cc_agents_keep_their_tools_lines | PASS (control) | PASS |

Focal: **3 failed → 7 passed**. Ningún fallo por ImportError/SyntaxError/NameError.

## 3. Comandos exactos y su salida

### 3.1 Focal ANTES (RED congelado, sin cambios)

```
$ python3 -m pytest tests/test_005_004_t1_dispatch_tool_name.py -q
FAILED tests/test_005_004_t1_dispatch_tool_name.py::test_pd1_i_cc_orchestrator_declares_agent_dispatch_tool
FAILED tests/test_005_004_t1_dispatch_tool_name.py::test_pd1_ii_no_cc_agent_declares_task_as_dispatch_tool
FAILED tests/test_005_004_t1_dispatch_tool_name.py::test_pd1_iii_adapter_owns_the_cc_dispatch_tool_name
3 failed, 4 passed in 1.01s
```

### 3.2 Focal DESPUÉS (GREEN)

```
$ python3 -m pytest tests/test_005_004_t1_dispatch_tool_name.py -q
.......                                                                  [100%]
7 passed in 1.04s
```

### 3.3 Regeneración de salidas declaradas + idempotencia

```
$ make agents
python3 scripts/cdad-generate.py --runtime opencode --stack odoo --profile optimus --out build/staging
cdad-generate: 12 files -> build/staging/agents/opencode (+ manifest.json)
python3 scripts/cdad-generate.py --runtime claude-code --stack odoo --profile optimus --out build/staging
cdad-generate: 12 files -> build/staging/agents/claude-code (+ manifest.json)
cp build/staging/agents/opencode/cdad-*.md agents/
cp build/staging/agents/claude-code/cdad-*.md agents/claude-code/
```

Idempotencia (segunda corrida, comparación de bytes):

```
$ before=$(sha256sum agents/claude-code/*.md build/staging/agents/claude-code/*.md | sha256sum) \
  && make agents >/dev/null 2>&1 \
  && after=$(sha256sum agents/claude-code/*.md build/staging/agents/claude-code/*.md | sha256sum) \
  && echo "before=$before" && echo "after =$after" && [ "$before" = "$after" ] && echo "IDEMPOTENT: identical bytes"
before=5e8595ca7e1e82961218a570e703a0dcdcb5a4333339b79387d5bb1b2fe3eaa3  -
after =5e8595ca7e1e82961218a570e703a0dcdcb5a4333339b79387d5bb1b2fe3eaa3  -
IDEMPOTENT: identical bytes
```

### 3.4 Regresiones declaradas (pytest)

```
$ python3 -m pytest tests/test_packet_prepare.py tests/test_cdad_generate.py \
    tests/test_003_006_t3_receive_wiring.py tests/test_003_007_t4_atomic_unit_rule.py -q
......................................................                   [100%]
54 passed in 23.41s
```

### 3.5 Regresión declarada (validador)

```
$ bash tests/validate-consistency.sh
...
PASS: 005-004 PD-1: agents/claude-code/cdad-architect.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-architect-odoo.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-implementer.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-implementer-odoo.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-orchestrator.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-reviewer.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-reviewer-odoo.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-scribe.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-scribe-odoo.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-test-writer.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-test-writer-odoo.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: the CC orchestrator declares the real dispatch tool 'Agent' (agents/claude-code/cdad-orchestrator.md contains '^tools:.*\bAgent\b')
PASS: 005-004 PD-1 (control): the OpenCode side keeps its own dispatch tool name (skills/cdad-cycle/references/opencode-delegation.md contains '\bTask\b')
...
Assert PASS: 154
Assert FAIL: 2
FAIL: 2 assert(s) failed.
```

Los 2 `FAIL` restantes son **preexistentes y ajenos a T1** (deuda declarada D-6
de la spec §8: `install.sh --check` con drift explicado por perfil del staging +
`__pycache__`, y el validador Odoo). Verificación de procedencia — el mismo
validador en el árbol sin el cambio de T1 (`git stash` de los 3 archivos)
devuelve 4 fallos, incluidos los 2 preexistentes:

```
$ git stash push -- scripts/cdad-generate.py sources/agents/adapters/claude-code.md agents/claude-code/cdad-orchestrator.md
$ bash tests/validate-consistency.sh
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
FAIL: F011: tests/validate-odoo-specialization.sh → FAIL
FAIL: 005-004 PD-1: agents/claude-code/cdad-orchestrator.md declares 'Task' as a dispatch tool (the real one is 'Agent')
FAIL: 005-004 PD-1: the CC orchestrator declares the real dispatch tool 'Agent' (agents/claude-code/cdad-orchestrator.md does NOT contain '^tools:.*\bAgent\b')
Assert PASS: 152
Assert FAIL: 4
$ git stash pop
```

Es decir: T1 lleva el validador de **4 fallos → 2 fallos**; los 2 que quedan ya
fallaban antes del cambio (F011/D-6) y no se atribuyen a T1.

## 4. `git diff --stat` acotado (commit)

```
$ git diff --stat HEAD~1 HEAD
 agents/claude-code/cdad-orchestrator.md | 2 +-
 scripts/cdad-generate.py                | 2 +-
 sources/agents/adapters/claude-code.md  | 2 +-
 3 files changed, 3 insertions(+), 3 deletions(-)
```

## 5. Commit

- Hash: **cc6e5a57205bc5e0941c5e571015d4c113f3fcc2**
- Mensaje: `feat: declare the real Claude Code dispatch tool (Agent) in the generator and adapter (005-004 PD-1/T1)`
- Sin `--no-verify`; sin tocar `tests/`; sin push.
- Árbol de trabajo tras el commit: sólo `docs/.cdad-state.json` (binding del
  orchestrator, fuera del write scope) queda modificado.

## 6. Invariantes respetadas

- No se editó ningún test (oráculo congelado intacto).
- Fuente única (INV-2/PD-9): la regla se declara en el generador y el adaptador
  la enuncia; el derivado se regenera, no se edita a mano.
- Compatibilidad (INV-4): los `tools:` de los diez agentes CC con/sin guard no
  cambiaron; el lado OpenCode conserva `Task`; `make agents` es idempotente.
