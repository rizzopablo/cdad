I'll start by reading the failing test, the review finding, and the relevant files.
The delegation section of the CC orchestrator declares the dispatch mechanism and D-3 model-declaration rule, not the frontmatter field syntax — that syntax lives at the agent layer (the model map + generated agents). Let me make my line's pointer accurate rather than claim a false location:
Commit `a25fc20` landed. Final evidence gathering:
# Reporte del implementer — GREEN (review-fix B-1), `006-002-delegation-by-layer`

## Resultado

GREEN del review-fix B-1. Focal en verde con el mínimo cambio de producción: **una línea de texto instalable reescrita**, sin tocar tests, adaptador ni nada fuera de scope.

## Cambio (1 archivo, 1 inserción / 1 borrado)

`skills/cdad-cycle/references/sub-agent-strategies.md:51`

```diff
-- Model: `model:` accepts aliases (`haiku`, `sonnet`, `opus`, `fable`) or a full model ID — there is no `mofgw` gateway.
+- Model: the model of each role is the one configured in the environment; the concrete syntax of the `model:` field is declared by this runtime's agent layer. This skill names no model alias, provider or deployment gateway.
```

Estilo de la vecina `:53`/`:55`: la skill no nombra alias de modelo de ningún runtime, ni proveedores/gateways de un despliegue concreto; el modelo de cada rol lo fija la configuración del entorno y la sintaxis del campo `model:` pertenece a la capa del agente del runtime (el párrafo siguiente ya apunta a la sección `delegation` del orquestador generado).

### Verificación del paso condicional del adaptador (no ejecutado, con evidencia)

El packet pedía añadir la sintaxis al `delegation` de `sources/agents/adapters/claude-code.md` **sólo si hiciera falta y no estuviera**. Verificado: **no hace falta y ya está declarada en la capa del agente** (no en la skill):

- `sources/agents/adapters/claude-code.md:15-23` (§frontmatter): `model:` pinned per `cdad_model_claude`.
- `scripts/cdad-models.sh:107-109`: contrato del helper — `cdad_model_claude … prints "alias or model-id" for Claude Code` (declaración de sintaxis, capa agente).
- `agents/claude-code/cdad-orchestrator.md:181`: la única tabla (`cdad_model_claude`) con los valores que produce, ya en el texto del orquestador.
- La sección `delegation` del adaptador declara el **mecanismo de despacho** + la regla D-3 (el modelo por llamada viene de la config del entorno); el orquestador no redacta frontmatter, así que la sintaxis del campo no es necesaria allí.

⇒ Sin cambio de adaptador, **sin `make agents`** (gate condicional no aplica). Aun así verifiqué idempotencia de la generación (ver comandos).

## Tabla test → resultado

| Test | Resultado |
|---|---|
| `tests/test_006_002_reviewfix.py` (focal, 4 tests) | **4 passed** (antes: 1 failed / 3 passed) |
| `tests/test_006_002_*.py` (u1, u2, u3, u4, u5, u6, reviewfix → 41 tests) | **41 passed** |
| `tests/test_005_005_t2_docs_policy.py` (lee `sub-agent-strategies.md`) + `test_005_010_t3_references.py` + `test_003_002_t1_receive.py` + `test_004_003_t5_reentry_equivalence.py` + `test_static_block_ceiling.py` | **28 passed** |
| `test_cdad_generate.py` + `test_packet_prepare.py` + `test_role_packet_{consumers,render,review_regressions}.py` | **59 passed** |
| `test_005_004_t1_dispatch_tool_name.py` + `t3_version_check_cc` + `t4_cc_guard_decisions` + `test_005_007_t5_delegation_dispatch.py` + `test_005_007_reviewfix_blockings.py` | **28 passed** |
| `make validate` | 161 PASS / **1 FAIL = F011** (baseline DT-8, declarada) |
| `make staging` vs `agents/` | byte-idéntico (⇒ `make agents` no-op) |

## Comandos exactos y salida

```
$ python3 -m pytest -q tests/test_006_002_reviewfix.py
....                                                                     [100%]
4 passed in 0.13s

$ python3 -m pytest -q tests/test_006_002_reviewfix.py tests/test_006_002_u1_delegation_section.py \
    tests/test_006_002_u2_neutral_skill.py tests/test_006_002_u3_runtime_references.py \
    tests/test_006_002_u4_skill_without_models.py tests/test_006_002_u5_transport_equivalence.py \
    tests/test_006_002_u6_context_discipline.py
.........................................                                [100%]
41 passed in 5.12s

$ grep -RniE '\bhaiku\b|\bsonnet\b|\bopus\b|\bfable\b|mofgw' skills/ ; echo "exit=$?"
exit=1                     # 0 coincidencias (condición de cierre de B-1 cumplida)

$ make validate 2>&1 | grep -n "FAIL"
199:FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
231:Assert FAIL: 1
232:FAIL: 1 assert(s) failed.

$ bash scripts/validate-subagents.sh
DRIFT: differs <home>/.claude/skills/cdad-cycle/references/sub-agent-strategies.md
DRIFT: differs <home>/.claude/skills/cdad-cycle/SKILL.md
... Check: FAIL — drift .claude/agents/cdad-orchestrator.md drift .config/opencode/agents/cdad-orchestrator.md skills …
== RESULT: FAIL ==          # instalación HOME stale: DT-8 declarada; el drift de SKILL.md/orquestadores
                            # (archivos que NO toco) prueba que la falla es preexistente, no de este cambio

$ make staging
python3 scripts/cdad-generate.py --runtime opencode --stack odoo --profile optimus --out build/staging
python3 scripts/cdad-generate.py --runtime claude-code --stack odoo --profile optimus --out build/staging
$ diff -r build/staging/agents/opencode agents/ --exclude=claude-code ; echo $?
0
$ diff -r build/staging/agents/claude-code agents/claude-code/ ; echo $?
0                           # generación intacta ⇒ make agents sería no-op (gate condicional satisfecho)
```

## Commit

`a25fc20dd32fe43fd6c6dc423d95696042300820` — `fix: 006-002 review-fix B-1: el detalle de modelo de runtime sale del texto instalable de la skill` (sin `--no-verify`, sin `git stash`, sin push).

```
 skills/cdad-cycle/references/sub-agent-strategies.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

## Cumplimiento de scope / invariantes

- Editado **sólo** `skills/**` (write scope). `tests/**` intacto (no se tocó ningún test, ni siquiera para el GREEN).
- No tocados: `install.sh`, `scripts/cdad-models.sh`, `sources/agents/adapters/claude-code.md`, ADR-007.
- Los untracked preexistentes (`docs/planning/`, `findings/incremental-construction-…md`) quedaron sin tocar; `build/staging` es gitignored (`git status --short` sólo muestra el archivo commiteado + esos untracked ajenos).
- Política de suite completa: no ejecutada (corre el closer); corrí el focal + la regresión proporcional acoplada (156 tests en total, todos verdes).
