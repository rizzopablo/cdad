# GREEN report — 005-004 T2 (implementer, substage green)

- **Rol:** implementer · **Subetapa:** green
- **Paquete:** `.cdad/packets/005-004-claude-code-roles-implementer-green-002/PACKET.md`
- **Feature / ejecución:** `005-004-claude-code-roles` / `exec-005-004-claude-code-roles-001` (epic-005)
- **Contrato:** `docs/specs/005-004-claude-code-roles/spec.md` (sha256 `79d57e0a…`)
- **Plan:** `docs/specs/005-004-claude-code-roles/plan.md` ficha T2 (sha256 `f7c61a59…`)
- **Commit GREEN:** `96786de49ecfcc57e5eb8f34a2f783ca92cefc5f` — `feat: reconcile the Claude Code adapter's installer claims — no strip, generation-profile cause, basic model provenance (005-004 PD-2/PD-5)`
- **Tests editados:** ninguno (focal congelado, intacto). `install.sh` y el lado OpenCode: intactos.

## Cambio (mínimo, sobre la fuente única)

No se tocó `agents/**` a mano (salida declarada): `make agents` regeneró y no cambió bytes (idempotente).

| Archivo:línea | Qué |
|---|---|
| `sources/agents/adapters/claude-code.md:15-34` | Se **elimina** la afirmación falsa (`installer STRIPS the model field at install time`) y se **enuncia el mecanismo real**: el instalador despliega los bytes staged como copia, verbatim y sin transformar (`cp -p`; `install.sh --help`: «the deployed bytes are the staged bytes … the installer transforms nothing»). Se **atribuye la ausencia** de la línea `model:` al **perfil de generación** (`cdad_model_claude` vacío bajo `basic` ⇒ el generador omite la línea), no al instalador (PD-2). Se **declara la procedencia bajo `basic`** (PD-5): no hay modelo por rol; el modelo se declara por llamada y se registra con `provenance`; el instalador **no garantiza** la invariante reviewer≠implementer; la exención es **explícita y visible** y se **referencia** por su fuente (`scripts/validate-subagents.sh` / `ADR-007`), sin copiarla (PD-9). |
| `scripts/cdad-generate.py:444-447` | Se corrige la **segunda ocurrencia** de la afirmación falsa (comentario del generador): mismo mecanismo real, misma causa por perfil. `scripts/` queda fuera del barrido declarado, pero está en alcance y AC-2 exige que no quede la afirmación. |

## Comandos exactos y salida

### 1. Focal RED (baseline, antes del cambio)

```
$ python3 -m pytest tests/test_005_004_t2_installer_claims.py -q
6 failed, 2 passed in 16.07s
```
Barrido PD-2(i) — único offender: `['sources/agents/adapters/claude-code.md:16']`.

### 2. Regeneración declarada (idempotente)

```
$ make agents
cdad-generate: 12 files -> build/staging/agents/opencode (+ manifest.json)
cdad-generate: 12 files -> build/staging/agents/claude-code (+ manifest.json)
cp build/staging/agents/opencode/cdad-*.md agents/
cp build/staging/agents/claude-code/cdad-*.md agents/claude-code/
# git status: sin cambios en agents/** ⇒ segunda corrida no cambia bytes (INV-2/INV-4)
```

### 3. Focal RED → GREEN

```
$ python3 -m pytest tests/test_005_004_t2_installer_claims.py -q
........                                                                 [100%]
8 passed in 22.25s
```

### 4. Regresiones declaradas + focal T1 (mismo archivo fuente)

```
$ python3 -m pytest tests/test_install_ownership.py tests/test_install_review5_regressions.py tests/test_005_004_t1_dispatch_tool_name.py -q
.......................                                                  [100%]
23 passed in 294.42s (0:04:54)
```

### 5. Lint / validador del repo (procedencia: pre-existente, delta 0)

```
$ ruff check scripts/cdad-generate.py
Found 2 errors.   # F821 ADAPTER_SECTIONS (inyectado por globals()) — idénticos en HEAD:
                  # `ruff check <(git show HEAD:scripts/cdad-generate.py)` => Found 2 errors. Delta = 0.

$ bash tests/validate-consistency.sh
Assert PASS: 154 / Assert FAIL: 2
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
FAIL: F011: tests/validate-odoo-specialization.sh → FAIL
# Verificado contra HEAD (stash dirigido de los 2 archivos): idéntico 154 PASS / 2 FAIL.
# ⇒ 0 fallos nuevos; los 2 son drift de runtime pre-existente (spec §8 D-6), ajenos a T2.
```

## Tabla test → resultado

| Test | Postcondición/AC | Antes | Después |
|---|---|---|---|
| `test_pd2_i_sweep_no_declared_surface_claims_the_installer_removes_the_model_field` | PD-2(i)/AC-2 | FAIL | PASS |
| `test_pd2_ii_adapter_states_the_installer_deploys_staged_bytes_untransformed` | PD-2(ii)/AC-2 | FAIL | PASS |
| `test_pd2_ii_adapter_attributes_the_missing_model_line_to_the_generation_profile` | PD-2(ii)/AC-2 | FAIL | PASS |
| `test_pd5_adapter_declares_no_model_per_role_under_basic` | PD-5(a)/AC-5 | FAIL | PASS |
| `test_pd5_adapter_declares_the_installer_does_not_guarantee_the_anti_bias_invariant` | PD-5(b)/AC-5 | FAIL | PASS |
| `test_pd5_adapter_references_the_exemption_source_instead_of_copying_it` | PD-5(c)/PD-9/AC-5 | FAIL | PASS |
| `test_pd2_ii_isolated_install_deploys_staged_cc_agent_bytes_verbatim` | PD-2(ii)/AC-2 (control) | PASS | PASS |
| `test_pd2_ii_basic_profile_absence_is_produced_by_the_generator` | PD-2(ii)/PD-5 (control) | PASS | PASS |

Focal: **6 FAIL → 8 PASS**. Los dos controles (instalación en raíz aislada) quedan verdes antes y después.

## `git diff --stat` acotado (HEAD~1..HEAD)

```
 scripts/cdad-generate.py               |  4 +++-
 sources/agents/adapters/claude-code.md | 22 +++++++++++++++++++---
 2 files changed, 22 insertions(+), 4 deletions(-)
```

## Evidencia / invariantes

- **No edité `tests/`** (focal intacto); **no toqué `install.sh`** ni el lado OpenCode.
- **Alcance de escritura respetado:** sólo `sources/` y `scripts/` (raíces de implementación declaradas). `docs/.cdad-state.json` (modificado por el orquestador) **no** se incluyó en el commit.
- **INV-2/INV-4:** `agents/` es salida declarada; regenerada con `make agents`, sin cambios de bytes.
- **PD-9:** la exención se **referencia** (`scripts/validate-subagents.sh`, `ADR-007`), sin corridas verbatim de 12 tokens respecto del dueño (aserción del focal verde).
- **Commit:** `96786de49ecfcc57e5eb8f34a2f783ca92cefc5f` (prefijo `feat:`, sin `--no-verify`).
- **Conflicto contrato/tests:** ninguno.
