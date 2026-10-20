GREEN de U4 completo. Informe de la unidad:

## Archivos modificados (7, todos en el write scope)

| Archivo | Cambio |
|---|---|
| `sources/roles/reviewer.md` | **Fuente editable** (única fuente tocada): fila de la tabla de contrato + párrafo de directiva |
| `agents/cdad-reviewer.md` | salida declarada de `make agents` (nunca a mano) |
| `agents/cdad-reviewer-odoo.md` | idem |
| `agents/claude-code/cdad-reviewer.md` | idem |
| `agents/claude-code/cdad-reviewer-odoo.md` | idem |
| `agents/cdad-orchestrator.md` | fila §2 **compuesta** por el generador (cambia sola) |
| `agents/claude-code/cdad-orchestrator.md` | idem |

**Qué cambia en la fuente** (el resto —calibración, taxonomía, veredicto, aislamiento— intacto):
- **Fila de contrato**: `Stages` = `2 Spec, 4 Review`; `Does` = «…against the approved spec, and of an **unapproved draft** (spec or plan)»; `Artifact` = `` `review.md` as FINAL TEXT (orchestrator materializes — ADR-003); `plan-review.md` for the draft review (orchestrator materializes) `` (el dictamen de borrador **se suma**, no sustituye).
- **Directiva**: párrafo nuevo `Scope (2 and 4): the assignment includes the review of an UNAPPROVED draft — the spec or plan draft of stage 2 — as well as the review of the result of stage 4. The draft review is a review, not an approval: you report the findings on the draft and the user decides the blockers.`

`docs/.cdad-state.json` (modificado por el orquestador al despachar este paquete), `docs/planning/` y `findings/*.md` (sin trackear, ajenos) **no** se tocaron ni se commitearon. `tests/**` intacto (0 archivos de test en el commit). La instalación del HOME no se leyó ni se escribió.

## Test → resultado

| Suite | Resultado |
|---|---|
| `tests/test_006_006_u4_reviewer_role_agents.py` (focal, 13 tests) | **13 passed** |
| Focales `tests/test_006_006_u{1,2,3,4,5}_*.py` + 11 regresiones de la ficha U4 | **150 passed in 170.17s** |
| `make validate` | `Assert PASS: 168 / Assert FAIL: 1` — único FAIL: `F011: scripts/validate-subagents.sh (active profile) → FAIL` (**ambiental**, ver abajo) |
| Determinismo (V-2) | dos corridas de `make staging` → sha256 idénticos en los 4 agentes |
| Generador sin diff pendiente | segunda corrida de `make agents` → archivos byte-idénticos, `git status` sin cambios nuevos |

## Comandos y salida

```
$ python3 -m pytest tests/test_006_006_u4_reviewer_role_agents.py -q -p no:cacheprovider
13 passed in 1.89s

$ python3 -m pytest tests/test_006_006_u1_draft_object_form.py tests/test_006_006_u2_review_procedure.py \
    tests/test_006_006_u3_review_route_and_gate.py tests/test_006_006_u4_reviewer_role_agents.py \
    tests/test_006_006_u5_exemption_record.py tests/test_cdad_generate.py tests/test_role_packets.py \
    tests/test_role_packet_render.py tests/test_005_006_t2_intake.py tests/test_bash_policy_selection.py \
    tests/test_opencode_read_map_and_steps.py tests/test_005_004_t2_installer_claims.py \
    tests/test_006_002_u1_delegation_section.py tests/test_006_002_u3_runtime_references.py \
    tests/test_006_003_u3_texts_without_profiles.py tests/test_006_005_u4_single_entry.py -q -p no:cacheprovider
150 passed in 170.17s (0:02:50)

$ make agents
cdad-generate: 12 files -> build/staging/agents/opencode (+ manifest.json)
cdad-generate: 12 files -> build/staging/agents/claude-code (+ manifest.json)
cp build/staging/agents/opencode/cdad-*.md agents/
cp build/staging/agents/claude-code/cdad-*.md agents/claude-code/

$ make staging && sha256sum ...(4 agentes) > s1 && make staging && sha256sum -c s1
build/staging/agents/opencode/cdad-reviewer.md: OK
build/staging/agents/opencode/cdad-reviewer-odoo.md: OK
build/staging/agents/claude-code/cdad-reviewer.md: OK
build/staging/agents/claude-code/cdad-reviewer-odoo.md: OK

$ make validate
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
Assert PASS: 168
Assert FAIL: 1
```

## F011 — declarado, no oráculo (ambiental)

El único FAIL de `make validate` es el bloque F011, que contrasta la instalación **activa del HOME** (`install.sh --check`): la copia instalada va por detrás de este árbol. **Es preexistente y ajeno a U4**, y lo medí en el HEAD sin mis cambios (`git archive HEAD` → `/tmp/opencode/cdad-head` + `make staging` → `install.sh --check`): ya fallaba entonces, con deriva en `~/.claude/skills/cdad-cycle/packets/roles/reviewer.md` (U2) y `SKILL.md` (U3) más el `❌ cdad-reviewer.md declares model:` de la copia vieja. Mi unidad **extiende** esa misma deriva preexistente a los 4 agentes del reviewer y a los 2 orquestadores (no se reinstala el HOME: el paquete lo prohíbe), sin cambiar el recuento de asserts (168/1). No se puede corregir sin salir del write scope → queda declarado para el orquestador.

## Oráculos cubiertos (PD-11)

O-S1 (etapas 2 y 4) · O-S2 (`plan-review.md` **además** de `review.md`) · O-S3 (el borrador es parte del rol) · O-S4 (directiva: borrador **no aprobado**) · O-A1 (4 agentes generados, generación real como proceso) · O-A2 (4 agentes promovidos) · O-D1/V-2 (determinismo de `make staging`).

## Commit

```
a276531 feat: 006-006 U4 — el rol reviewer declara la revision de borrador
 7 files changed, 37 insertions(+), 17 deletions(-)
 sources/roles/reviewer.md
 agents/cdad-reviewer.md, agents/cdad-reviewer-odoo.md
 agents/claude-code/cdad-reviewer.md, agents/claude-code/cdad-reviewer-odoo.md
 agents/cdad-orchestrator.md, agents/claude-code/cdad-orchestrator.md
```

Sin `--no-verify`, sin `git stash`, sin `push`. La suite completa **no** se ejecutó (política del paquete: la corre una vez quien cierra).