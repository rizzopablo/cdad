I'll start by reading the approved contract and the current test tree.
Let me examine the other tests that mention family/not-guaranteed, to identify which actually require the retired requirement.
Now I have a clear picture. Let me write the new focal test.
The oracle works. Now let me restructure: the shared absence oracle lives in U3 (single definition), and U5' focal imports it (avoids an import cycle).
Now the U3 reformulation: move the A-5 absence oracle there and invert the three family tests.
Now I'll replace the family-presence concepts with the A-5 absence oracle.
Now the three family tests in U3:
Moving the shared A-5 oracle into U2 (the suite's absence-oracle home) to avoid an import cycle with U1.
Now remove the duplicated block from U3 and import it from U2:
Now the U1 header docstring and import:
RED complete and committed. Final report:

## Files (commit `0629ae0`, only `tests/`)

| Path | Action |
|---|---|
| `tests/test_006_003_u5_model_family.py` | **retirado** (`git rm`) — PD-4a..e/D4/§2.4 retirados por A-5; declarado en el commit |
| `tests/test_006_003_u5p_no_family_requirement.py` | **nuevo focal** (oráculo de ausencia por conceptos + positivo conservado + auto-test del clasificador) |
| `tests/test_006_002_u2_neutral_skill.py` | **definición única** del oráculo de ausencia (`all_offenders`, patrones, clasificador de usos ajenos) |
| `tests/test_006_003_u3_texts_without_profiles.py` | reformulado (presencia → ausencia; filas 4/6/8) |
| `tests/test_006_002_u1_delegation_section.py` | `TestPd4FamilyConfigurationDeclaration` → `TestPd4DelegationRegistrationWithoutFamilyRequirement` |
| `tests/test_006_002_u4_skill_without_models.py` | conceptos 4/5/6'/7'/8' → ausencia |
| `tests/test_005_004_t2_installer_claims.py` | PD-5(b) reformulado (el reclamo reviewer≠implementer se retira con el requisito) |
| `tests/validate-consistency.sh` | F001 (mitad familia) invertida a ausencia |
| `tests/validate-odoo-specialization.sh` | P1.reviewer: comentario/mensajes (el assert `^model:` se conserva) |

`git show --name-only HEAD | grep -v '^tests/'` → **OK: only tests/**. `docs/planning/` y `findings/…` siguen sin trackear e intactos.

## Mapa test → enmienda A-5 (§9 de la spec)

| Test | Enmienda / postcondición |
|---|---|
| `test_u5p_skill_tree_has_no_reviewer_family_requirement` | INV-5 reformulada / PD-7b — `skills/**` sin el requisito |
| `test_u5p_role_sources_have_no_reviewer_family_requirement` | íd. — `sources/roles/*.md` |
| `test_u5p_adapters_have_no_reviewer_family_requirement` | íd. — `sources/agents/adapters/*.md` |
| `test_u5p_generated_agents_have_no_reviewer_family_requirement` | íd. — `agents/**` (composición) |
| `test_u5p_adapters_have_no_profile_wording` | A-5: «restos de la redacción por perfiles (`basic`, «profile») en los adaptadores se retiran» |
| `test_u5p_section2_keeps_the_other_anti_bias_invariants` | A-5 «se conservan»: test-writer sin implementación, implementer sin tests, reviewer read-only y en sesión separada |
| `test_u5p_family_classifier_separates_declared_unrelated_uses` | A-5 §9: exclusiones declaradas («failure family», «split-brain family», «family of failures») |
| u3 `…_has_no_family_requirement` ×3 | §2 / bloques `delegation` / orquestadores |
| u4 `test_pd11_section2_has_no_family_requirement` | §2 de SKILL.md |
| u1 `…_opencode` / `…_claude_code` | compuesto generado (I8 conservado) |
| 005-004 T2 `test_pd5_adapter_does_not_declare_the_retired_reviewer_family_invariant` | PD-5(b) |

**Exclusiones declaradas:** `skills/cdad-cycle/references/context-meter.md` (INV-8) y `skills/cdad-cycle/references/verdict-tuple.md` ("+1 por familia distinta" = criterio de confianza del veredicto → **no se fija en ningún sentido**).

## Comandos y salida resumida

```
$ python3 -m pytest tests/test_006_003_u5p_no_family_requirement.py -q --tb=no
5 failed, 2 passed        # 4 ausencia + perfiles en adaptadores ROJO; conservación y auto-test VERDE

$ python3 -m pytest tests/test_006_003_u3_texts_without_profiles.py \
      tests/test_006_002_u4_skill_without_models.py \
      tests/test_006_002_u1_delegation_section.py -q --tb=no
6 failed, 20 passed       # los 6 reformulados ROJO por AssertionError de contenido

$ python3 -m pytest tests/test_005_004_t2_installer_claims.py -k pd5 -q --tb=line
1 failed, 2 passed        # el adaptador todavía declara "Family verification (D-3/INV-5)"
                          # en sources/agents/adapters/claude-code.md:96

$ bash tests/validate-consistency.sh   → Assert PASS: 160 / FAIL: 9
  8 FAIL son F001 (006-003 A-5) SKILL.md §2 y ambos orquestadores
  1 FAIL es F011 (pre-existente, ver abajo)

$ bash tests/validate-odoo-specialization.sh → PASS: 68 / FAIL: 0

$ python3 -m ruff check <9 archivos tocados>  → All checks passed
$ bash -n validate-consistency.sh / validate-odoo-specialization.sh → OK
$ python3 -m pytest … --collect-only (u5, u6, reviewfix, t2, u3_refs, t3_refs) → 35 collected (sin ImportError)
```

**Ofensores medidos (ubicaciones, sin citar producto):** `skills/**` = 8 (SKILL.md 78,79,82,86 **y** 170,584; stage-4-review.md 23,24) · `sources/roles` = 3 · adapters = 2 familia + 3 perfiles · `agents/**` = 16.

Cortes de fase: sólo leí `docs/specs/006-003-…/spec.md` y `tests/`; ningún archivo de implementación (`skills/`, `sources/`, `agents/`, `scripts/`, `install.sh`) se leyó para derivar aserciones (`model_offenders`, `offenders_in` y `all_offenders` corren al ejecutarse los tests).

## Regresiones esperadas / notas para el GREEN y el orquestador

1. **GREEN debe retirar** los textos de familia en: `skills/cdad-cycle/SKILL.md` (§2 **y** líneas 170/584, fuera de §2 — son los «invariantes de rol» que A-5 §9 nombra), `skills/cdad-cycle/references/stage-4-review.md`, `sources/roles/{reviewer,orchestrator}.md`, `sources/agents/adapters/{opencode,claude-code}.md` (línea de familia **y** restos de perfil en `:16`/`:28`), y regenerar `agents/**` (orquestadores + `cdad-reviewer*`). Nada de eso toca `verdict-tuple.md`.
2. **F011 de `validate-consistency.sh`** (`scripts/validate-subagents.sh` → FAIL) es **preexistente y ajeno a este RED**: no toqué ese script ni sus fuentes; la mitad F001 introduce exactamente los 8 FAIL esperados.
3. Puntos de precisión del oráculo, con auto-test propio: `«failure family»`/`«failure-family»`/`«family of failures»`/`«familia de fallos»`/`«split-brain family»` no cuentan (`anti-patterns.md` sale limpio); sólo cuentan las ocurrencias relacionadas.
4. Límite honesto (PD-15): el barrido es un oráculo de conceptos por ventana (±3 líneas) sobre texto publicado; la forma final de la prosa la juzga el review de stage 4. HEAD se movió durante la sesión (`31d887c`, commit ajeno de `docs/epic`): mi commit quedó encima y contiene sólo `tests/`.
