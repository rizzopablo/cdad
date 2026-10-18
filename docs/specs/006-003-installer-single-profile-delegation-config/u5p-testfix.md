Now update the focal oracle (docstring + declared negatives):
## Role report — test-writer, substage `red` (testfix de U5')

Packet: `006-003-…-test-writer-red-008` · contrato `docs/specs/006-003-…/spec.md` (§9, enmienda A-5) · write scope `tests/` · commit de este testfix: **`113c777`**.

### 1. Cambio (solo `tests/`)

| Archivo | Cambio |
|---|---|
| `tests/test_006_002_u2_neutral_skill.py` (definición única del oráculo) | `has_related_family` exige ahora la **conjunción** del token «familia» con un rol o un modelo, vía `_family_is_role_qualified`: (1) calificador antecedente (`the reviewer's family`, `model family`), (2) complemento (`family of the reviewer`, `family from the implementer's`, `familia del reviewer`), (3) rol/modelo en la **misma cláusula** antes del token (`reviewer ≠ implementer in family`). Una «familia» suelta sin rol/modelo ligado ya no cuenta. Se agregan `FAMILY_ROLE_WORD_RE`, `FAMILY_QUALIFIER_PREFIX_RE`, `FAMILY_QUALIFIER_SUFFIX_RE`, `CLAUSE_BOUNDARY_RE` y se actualiza el comentario de contrato del bloque. |
| `tests/test_006_003_u5p_no_family_requirement.py` (focal) | Negativos nuevos en el auto-test del oráculo: las dos líneas **literales** de `stage-4-review.md:23-24` («A failure family is fixed as a family…» / «reveal a family (not a single case), the reviewer asks…») y el párrafo sintético completo (rol + mood + dos «family» sueltas) → `all_offenders(...) == []`. Cabecera: declaración del falso positivo y del **inventario auditado** del barrido (ofensores reales por superficie + todos los usos ajenos declarados). |

### 2. Comandos y salidas

```
$ python3 -m pytest tests/test_006_003_u5p_no_family_requirement.py -q | tail -7
FAILED …TestU5pNoReviewerFamilyRequirement::test_u5p_skill_tree…
FAILED …::test_u5p_role_sources…
FAILED …::test_u5p_adapters…
FAILED …::test_u5p_generated_agents…
FAILED …TestU5pNoProfileWordingInAdapters::test_u5p_adapters_have_no_profile_wording
5 failed, 2 passed in 0.24s

$ python3 -m pytest tests/test_006_003_u5p_no_family_requirement.py -q | grep -c "stage-4-review"
0                      # GATE: stage-4-review.md ya no aparece

# inventario de ofensores por superficie (helper del propio oráculo, precorrección → post)
skills/**:       8 → 6   (SKILL.md :78,:79,:82,:86,:170,:584; las 2 de stage-4-review eliminadas)
sources/roles:   3       (orchestrator.md:172; reviewer.md:50,:53)
adapters:        2       (claude-code.md:96; opencode.md:77)
agents/**:      16       (orchestrators/reviewers generados, agents/ y agents/claude-code/)

$ python3 -m pytest tests/test_006_002_u1_delegation_section.py tests/test_006_002_u2_neutral_skill.py \
    tests/test_006_002_u4_skill_without_models.py tests/test_006_003_u3_texts_without_profiles.py \
    tests/test_005_004_t2_installer_claims.py -q | tail -3
7 failed, 31 passed in 10.78s     # idéntico al baseline pre-fix: RED preservado, 0 regresiones
```

`git status --porcelain` antes/después del commit: solo ` M tests/…` (los dos archivos) → `?? docs/planning/`, `?? findings/incremental-…md` **sin tocar** (no son míos). Sin `--no-verify`, sin `stash`, sin push. Suite completa: **no corrida** (política del paquete: la corre quien cierra).

```
$ git log --oneline -1
113c777 test: 006-003 U5' testfix falso positivo «failure family» en stage-4-review
$ git show --stat --oneline HEAD
 tests/test_006_002_u2_neutral_skill.py          | 73 +++++++++++++++++++++----
 tests/test_006_003_u5p_no_family_requirement.py | 73 +++++++++++++++++++++++--
 2 files changed, 132 insertions(+), 14 deletions(-)
```

### 3. Auditoría del resto del barrido (declarada, como pide el encargo)

Se re-escaneó con el oráculo y se listaron **todas** las líneas con «familia» que no son ofensores; ninguna era ofensor antes del ajuste, así que la detección real no se relajó:

- **Familias de fallos** (ajenas a A-5, correctamente fuera): `stage-4-review.md:23-24` (falso positivo corregido) y `:72`; `anti-patterns.md:184,:188`; `continuity.md:121` (split-brain/divergent-heads); `handoff-prompts.md:508`.
- **Puntaje del verdict-tuple**: `handoff-prompts.md:499` «family different from implementer +1» — puntaje de CONFIANZA, no requisito de despacho (misma conducta declarada para `verdict-tuple.md`).
- **Limitación honesta / prosa**: `cli-delegation.md:333-335` («changing CLI does not guarantee another model family (INV-8)»), `SKILL.md:148`, `sources/roles/orchestrator.md:102`, `agents/**` equivalentes.
- **Uso interno de helper**: `skills/cdad-cycle/scripts/cdad_context_meter.py:1718` («Coordinator/worker families (PD-9)»).
- **Exclusiones declaradas vigentes**: `context-meter.md`, `verdict-tuple.md` (siguen fuera de la superficie del focal).

### 4. Límites y aislamiento (PD-15, honesto)

- **No leí implementación para diseñar el fix.** El diseño salió de la semántica del oráculo y del enunciado del packet. Para la auditoría de falsos positivos usé la **salida del propio oráculo** (helpers `has_related_family`/`all_offenders` de `tests/`, que leen los artefactos publicados al ejecutarse) — imprimí líneas de producto a través de ella (p. ej. `cli-delegation.md:331-337`, `handoff-prompts.md:496-510`); no abrí esos archivos para derivar los tests.
- No leí `tests/.sensitive-patterns.local`. No edité nada fuera de `tests/`.
- Ningún fallo es ImportError/SyntaxError: los 5 rojos son AssertionError de contenido. Los "conservados" (6) y el auto-test del oráculo (7) pasan.

**Pendiente del orquestador:** que el GREEN retire los textos de familia/perfiles en las superficies reales (SKILL.md 6 líneas, `sources/roles/{reviewer,orchestrator}.md`, los 2 adaptadores, `agents/**`) — este testfix no toca producto ni el inventario de ofensores reales.
