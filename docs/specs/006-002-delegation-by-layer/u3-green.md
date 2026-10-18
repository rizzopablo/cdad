I'll start by exploring the repository state and the relevant files.
Now I'll implement. First, create the non-installable evidence documents under `docs/`:
Now the SKILL.md edits (reference table rows and the multi-environment pointer):
Now the `cli-delegation.md` transport-choice block (PD-10):
Let me align `cli-delegation.md` strictly with PD-10 (remove the block, not replace it):
## Informe de rol — implementer (stage 3, GREEN) · `006-002-delegation-by-layer` U3

**Commit:** `5ad04e2` — `feat: 006-002 U3 GREEN — retiro de las referencias por runtime y cli-delegation.md como contrato del adaptador` (sin `--no-verify`, sin `git stash`, sin push; árbol limpio).

**Resultado:** PD-9 y PD-10 implementados; 6 de los 7 módulos focales verdes, `make agents` idempotente, `make validate` con el único FAIL ambiental declarado (F011 = DT-8). **1 test queda rojo por un defecto de oráculo ajeno a la unidad** (detalle y evidencia abajo) — no lo resolví porque exige editar `tests/` (fuera de mi alcance) o 5 documentos ajenos a la superficie de U3.

### Cambios (archivo:línea)

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/references/opencode-delegation.md` | **borrado** (194 líneas) → `docs/evidence/runtime-delegation/opencode-delegation.md` |
| `skills/cdad-cycle/references/claude-code-delegation.md` | **borrado** (122 líneas) → `docs/evidence/runtime-delegation/claude-code-delegation.md` |
| `docs/evidence/runtime-delegation/opencode-delegation.md` | **nuevo** — encabezado `:1-16` (evidencia no instalable; historia de 005-004/005-005/005-010; la regla vigente vive en la sección `delegation` del orquestador) + contenido retirado **byte-idéntico** `:17-218` |
| `docs/evidence/runtime-delegation/claude-code-delegation.md` | **nuevo** — encabezado `:1-18` (idem + la prohibición sub-agente→sub-agente (sub-subagent) y su incidente) + contenido retirado **byte-idéntico** `:19-149` |
| `skills/cdad-cycle/SKILL.md` | `:459-460` filas de runtime retiradas de la tabla «How to read the references»; `:493` puntero de §Multi-environment reemplazado por «vive en la sección `delegation` del agente de tu runtime» |
| `skills/cdad-cycle/references/cli-delegation.md` | `:267-276` bloque «Delegating inside OpenCode vs. between CLIs» (regla de elección de transporte) **eliminado**; el contrato del adaptador (`:1-266`, `:267-333`) intacto |
| `skills/cdad-cycle/references/runtime-adoption.md` | `:53-54` puntero a `references/opencode-delegation.md` → «evidencia histórica no instalable bajo `docs/`» |
| `skills/cdad-cycle/references/sub-agent-strategies.md` | `:55` puntero a `references/claude-code-delegation.md` → sección `delegation` del agente + evidencia no instalable |

Verificado: **0 punteros** a los dos nombres en `skills/**`, `agents/**`, `sources/**`, `scripts/**`, `build/**`, `install.sh` (`grep -rn … ; exit 1`). Contenido preservado byte-idéntico al retirado (comparación programática: `orig == body` → `True` en ambos). `git` lo registra como **rename** (`R084`/`R089`): historia conservada.

**Contenido en uso:** no hizo falta tocar los adaptadores. Las secciones `delegation` de `sources/agents/adapters/{opencode,claude-code}.md` (U1 GREEN) ya llevan la regla vigente (mecanismo nativo, mapping `cdad-<role>`, paquete byte-idéntico, prohibición intra-runtime, declaración de modelo D-3, recibo), y el detalle restante (recarga/versión, canal `delegate` muerto, 429, procedencia, `PWD`, incidente de spawn) está clasificado como histórico por spec §1. Por eso `sources/` y `agents/` no cambiaron.

### Test → resultado

| Test | Resultado |
|---|---|
| `tests/test_006_002_u3_runtime_references.py` | **6 passed** |
| `tests/test_006_002_u2_neutral_skill.py` | **4 passed** |
| `tests/test_005_004_t1_dispatch_tool_name.py` | **7 passed** |
| `tests/test_005_005_t3_provenance.py` | **3 passed** |
| `tests/test_005_009_t3_spawn_reconciliation.py` | **19 passed** |
| `tests/test_005_010_t3_references.py` | **5 passed** |
| `tests/test_005_004_t4_cc_guard_decisions.py` | **1 failed / 5 passed** — `TestConsumerReference::test_pd4_exit2_claim_stays_scoped_in_the_preserved_evidence` (BLOCKER, ver abajo) |
| `tests/validate-consistency.sh` | 159 PASS / **1 FAIL** = `F011` (DT-8 ambiental, preexistente) |
| `tests/validate-odoo-specialization.sh` | 67 PASS / 0 FAIL |
| regresión proporcional (U1/U2/U3 + adaptador/interface/acceptance 005-009 + 005-010 reviewfix + docs-policy/start-procedure/intake + 003-004/003-006/004-003/review-regressions/pd10-semantics) | **109 passed, 1 skipped, 1 failed** (el mismo de arriba) |
| 2 fallos preexistentes fuera de la superficie de U3 | `test_005_006_t6…::test_hallazgo_a2_cli_invocations_derived_from_skill_dir` y `test_003_006_t3_receive_wiring…::test_p1_regenerated_agents_reflect_source` — **verificado que fallan igual en `HEAD~1`** (`git archive HEAD~1` en un árbol limpio) ⇒ regresiones introducidas por U1, no por U3 |

### Comandos y salida

```
$ make agents            # 1ª y 2ª corrida
cdad-generate: 12 files -> build/staging/agents/opencode (+ manifest.json)
cdad-generate: 12 files -> build/staging/agents/claude-code (+ manifest.json)
$ git status --short     # tras make agents
(vacío)                  # idempotente: agents/ y build/ sin diff

$ bash tests/validate-consistency.sh | tail -3
Assert PASS: 159
Assert FAIL: 1
FAIL: 1 assert(s) failed.   # FAIL: F011 … (DT-8 ambiental)

$ python3 -m pytest <7 módulos focales> -q
1 failed, 109 passed, 1 skipped in 48.53s
```

`git diff --stat HEAD~1 HEAD`:

```
 .../runtime-delegation}/claude-code-delegation.md  | 27 ++++++++++++++++++++++
 .../runtime-delegation}/opencode-delegation.md     | 24 +++++++++++++++++++
 skills/cdad-cycle/SKILL.md                         |  4 +---
 skills/cdad-cycle/references/cli-delegation.md     | 11 ---------
 skills/cdad-cycle/references/runtime-adoption.md   |  3 ++-
 skills/cdad-cycle/references/sub-agent-strategies.md | 2 +-
 6 files changed, 55 insertions(+), 16 deletions(-)
```

### BLOCKER declarado: `test_pd4_exit2_claim_stays_scoped_in_the_preserved_evidence`

No es satisfacible con cambios de producción. Diagnóstico (replicando el oráculo del propio test):

- `evidence_text()` une **416** documentos vía `framed_evidence_documents()` (todo `docs/**` con un marcador de `EVIDENCE_FRAME`), no la evidencia preservada de U3.
- Sobre esa unión hay **19** bloques con `exit 2` + verbo de confianza; **10** incumplen el alcance exigido, y **ninguno proviene de la evidencia nueva de U3**. Orígenes: `docs/activeContext.md` (×2), `docs/adr/ADR-026-…-mecanismo-nativo.md` (×3), `docs/epics/epic-004-single-source-planning/c0-dispatch-record.md`, `docs/specs/005-004-claude-code-roles/discovery.md`, `docs/specs/005-004-claude-code-roles/spec.md` (×2), `docs/systemPatterns.md`.
- El bloque de `exit 2` de la evidencia nueva (el de `claude-code-delegation.md`, con alcance interactivo / `-p` / desconocido) **sí** cumple.
- Reproducible antes del cambio: neutralizando solo `assert_consumer_withdrawn` (monkeypatch en memoria, sin editar el test) el mismo test ya daba **18 subtest failures** en el árbol previo ⇒ el defecto es del oráculo (join demasiado amplio), no de la implementación.
- Arreglo mínimo propuesto (test-side, U7/test-writer): acotar `evidence_text()` a la evidencia preservada (p. ej. los documentos bajo `docs/evidence/runtime-delegation/`), como ya hace el resto de los asserts de conservación. No lo apliqué: `tests/**` está fuera de mi alcance.

### Desvío de alcance declarado

El `write_scope` del packet lista solo raíces de implementación (`agents`, `skills`, `scripts`, `sources`, `build`, `install.sh`); **no incluye `docs/`**. La adjudicación del orquestador y los propios tests (PD-9: «existe como evidencia no instalable bajo `docs/**`») exigen escribir ahí, y `path_policy.documentation_roots` declara `docs`. Escribí únicamente `docs/evidence/runtime-delegation/` (2 archivos nuevos, sin tocar documentos existentes) y lo reporto para auditoría.

### Límites honestos

- Los 2 fallos preexistentes (`test_005_006_t6` A2 y `test_003_006_t3` P1) son de U1 (la sección `delegation` nombra `cdad_packet.py render` sin el marcador `<skill-dir>` y agrega unidades que divergen de `sources/roles/orchestrator.md`). No los toqué; van al orquestador.
- F011 sigue siendo ambiental (DT-8): el chequeo del perfil activo contra la instalación en HOME.
- No corrí la suite completa (política del packet: la cierra el closer).
