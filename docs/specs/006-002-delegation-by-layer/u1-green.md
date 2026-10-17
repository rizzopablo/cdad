Informe de rol — **implementer / GREEN (U1 de `006-002-delegation-by-layer`)**

## 1. Cambios (archivo:línea)

| Archivo | Línea(s) | Cambio |
|---|---|---|
| `sources/agents/adapters/opencode.md` | `59-89` (nuevo) | Bloque `<!-- cdad-section:delegation -->`: mecanismo nativo `` `task` `` + `subagent_type: cdad-<role>` con mapeo rol→subagente, resolución del sufijo de stack, pase byte-idéntico del paquete (`cdad_packet.py render`), prohibición intra-runtime del adaptador CLI, declaración D-3 (`basic` + "not guaranteed" + `model_configured`/`model_reported`/`session`, "nunca elige ni inventa modelo", modelo solo desde la configuración del entorno), enlace al *Orchestrator materialization protocol*. |
| `sources/agents/adapters/claude-code.md` | `81-111` (nuevo) | Idem con mecanismo nativo `` `Agent` ``. |
| `scripts/cdad-generate.py` | `64` | `REQUIRED_ADAPTER_SECTIONS` suma `"delegation"`. |
| `scripts/cdad-generate.py` | `814-816` | `compose_orchestrator_agent` compone `ADAPTER_SECTIONS["delegation"]` bajo `## Delegation (adapter)` y **elimina el bloque hardcodeado** `## Delegation order and spawn guard` (orden + párrafo spawn guard duplicado). El spawn guard/anti-recursión de la fuente (`sources/roles/orchestrator.md:77-79`) queda intacto. |
| `agents/cdad-orchestrator.md` | `172` | Regenerado (`make agents`): sección `## Delegation (adapter)` compuesta. |
| `agents/claude-code/cdad-orchestrator.md` | `177` | Regenerado (`make agents`): ídem. |

No se tocó `tests/**`, ni `install.sh`, ni `scripts/cdad-models.sh`, ni `cdad_delegate*.py`, ni `docs/adr/ADR-007*`.

## 2. Tabla test → resultado

| Test | Antes (RED, `a2db8f8`) | Después |
|---|---|---|
| `test_006_002_u1_…::TestPd2a…::…opencode_adapter…` (PD-2a) | FAIL | PASS |
| `…::TestPd2a…::…claude_code_adapter…` (PD-2a) | FAIL | PASS |
| `…::TestPd2b…::…opencode_source_block…` (PD-2a/b + D-1) | FAIL | PASS |
| `…::TestPd2b…::…claude_code_source_block…` | FAIL | PASS |
| `…::TestPd2cOc…::…native_task_with_subagent_type` (PD-2c) | FAIL | PASS |
| `…::TestPd2cCc…::…agent_with_subagent_type` (control) | PASS | PASS |
| `…::TestPd4IntraRuntimeAdapterProhibition` (PD-4ii) | FAIL | PASS |
| `…::TestPd4BasicFamilyDeclaration::…opencode…` (PD-4iii/iv, D-3) | FAIL | PASS |
| `…::TestPd4BasicFamilyDeclaration::…claude_code…` | FAIL | PASS |
| `…::TestPd2dPacketPassAndReceiptLink` (PD-2d/PD-5b) | FAIL | PASS |

Regresiones proporcionales: `test_cdad_generate.py`, `test_005_004_t1_dispatch_tool_name.py`, `test_005_009_t3_spawn_reconciliation.py`, `test_005_004_t2_installer_claims.py`, `test_005_004_t4_cc_guard_decisions.py`, `test_cdad_adapters_opencode.py`, `test_bash_policy_selection.py`, `test_opencode_read_map_and_steps.py`, `test_005_004_t3_version_check_cc.py`, `test_005_005_t3_provenance.py`, `test_packet_prepare.py`, `test_role_packet_consumers.py`, `test_005_002_t5_role_aggregate.py`, `test_004_001_t7_capacity.py`, `test_005_007_t5_delegation_dispatch.py`, `test_005_009_t2_opencode_adapter.py` → todas verdes.

## 3. Comandos exactos y salida

```
$ python3 -m pytest tests/test_006_002_u1_delegation_section.py -v
… (10 líneas PASSED) …
============================== 10 passed in 1.38s ==============================
```

```
$ python3 -m pytest tests/test_cdad_generate.py tests/test_005_004_t1_dispatch_tool_name.py \
    tests/test_005_009_t3_spawn_reconciliation.py -q
......................................                                   [100%]
38 passed in 4.90s
```

```
$ python3 -m pytest tests/test_005_004_t2_installer_claims.py tests/test_005_004_t4_cc_guard_decisions.py \
    tests/test_cdad_adapters_opencode.py tests/test_bash_policy_selection.py \
    tests/test_opencode_read_map_and_steps.py -q
.......................                                                  [100%]
23 passed in 25.87s

$ python3 -m pytest tests/test_005_004_t3_version_check_cc.py tests/test_005_005_t3_provenance.py \
    tests/test_packet_prepare.py tests/test_role_packet_consumers.py \
    tests/test_005_002_t5_role_aggregate.py tests/test_004_001_t7_capacity.py -q
.............................................                            [100%]
45 passed in 50.84s

$ python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py \
    tests/test_005_009_t2_opencode_adapter.py -q
.............                                                            [100%]
13 passed in 22.21s
```

```
$ make validate
…
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
Assert PASS: 155
Assert FAIL: 1
```

```
$ bash scripts/validate-subagents.sh   # desglose de F011
DRIFT: differs /home/<user>/.claude/skills/cdad-cycle/scripts/__pycache__/cdad_packet.cpython-313.pyc
[2026-10-17 …] Check: FAIL — drift .claude/agents/cdad-*.md … drift .config/opencode/agents/cdad-*.md skills …/.claude/skills/cdad-cycle
❌ install.sh --check failed (rc=1)
```

**F011 es el drift ambiental preexistente (DT-8/D-6)**: `install.sh --check` compara contra las copias instaladas en HOME (todos los agentes + `__pycache__/cdad_packet.cpython-313.pyc`), ajeno a este diff; `make validate` queda en el estado documentado **155 PASS / 1 FAIL**.

```
$ make agents; git diff | sha256sum   # idempotencia (dos corridas consecutivas)
515065e51065f703f3e1500f2e73c015f14110247c4a89490feae59203a502a6  -
515065e51065f703f3e1500f2e73c015f14110247c4a89490feae59203a502a6  -
```
Sin cambio de diff en la segunda corrida (idempotente).

## 4. `git diff --stat`

```
 agents/cdad-orchestrator.md             | 39 ++++++++++++++++++++++++++-------
 agents/claude-code/cdad-orchestrator.md | 39 ++++++++++++++++++++++++++-------
 scripts/cdad-generate.py                | 18 +++------------
 sources/agents/adapters/claude-code.md  | 32 +++++++++++++++++++++++++++
 sources/agents/adapters/opencode.md     | 32 +++++++++++++++++++++++++++
 5 files changed, 129 insertions(+), 31 deletions(-)
```

## 5. Commit

`51ab88d  feat: 006-002 U1 GREEN delegation sections in adapters + generator composition` (5 files, +129/−31). Sin `--no-verify`, sin `git stash`, sin push; árbol limpio tras el commit.

## 6. Notas de fidelidad al contrato

- **U1 no movió texto de skill** (`skills/**` sin cambios): U2–U6 intactas.
- Al retirar el bloque hardcodeado el orquestador pierde el literal `resolve the stack` que exige **F007** de `tests/validate-consistency.sh` (test que A-1 permite reformular **solo en un RED**, no en este GREEN). Resolución *dentro del GREEN y sin editar tests*: la resolución del sufijo de stack se declara ahora en la **sección `delegation` del adaptador fuente** (dueña del contenido según D-1) y se compone; F007 vuelve a verde y `make validate` queda en 155/1. Se reporta por transparencia: el oráculo F007 no figuraba en la lista de regresiones acopladas de la ficha U1 (§1.5), pero su aserción se preservó sin tocarlo.
- Límite honesto: los tests prueban que la regla **existe** en el artefacto generado (texto), no que se obedezca; la evidencia conductual es la unidad de aceptación U8.
