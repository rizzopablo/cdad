I'll start by validating the packet and reading the approved spec.
Spec + plan read. Now writing the focal RED module with a minimal fixed CLI interface.
# Role report — test-writer / RED · `006-003-installer-single-profile-delegation-config` U5

**Packet:** `006-003-installer-single-profile-delegation-config-test-writer-red-006` · substage `red` · contract `docs/specs/006-003-…/spec.md` **sha256 `32ed55c4…487419` verified** (`sha256sum` matches the packet).
**Scope:** write scope respected — only `tests/`. No implementation source read (only `ls` of `skills/cdad-cycle/{scripts,references}` directory names, no file content). `tests/.sensitive-patterns.local` and `~/.config/cdad/*` never read. No host values.
**Full suite:** not run (packet policy — closer runs it once).

## 1. Files

| File | Kind |
|---|---|
| `tests/test_006_003_u5_model_family.py` | **new** — focal oracle, 10 tests, 540 lines |

## 2. Test → postcondition map

| # | Test | Contract |
|---|---|---|
| 1 | `TestPd4aSameEffectiveModel::test_pd_4a_same_effective_model_is_same_family` | PD-4a / §2.4 (+ provenance echoed) |
| 2 | `TestPd4bDistinctStemsAreGuaranteed::test_pd_4b_distinct_stems_are_guaranteed_by_configuration` | PD-4b (stems distintos) |
| 3 | `TestPd4bSameStemDifferentIdsWarns::test_pd_4b_same_stem_different_ids_warns_same_family` | PD-4b (mismo stem, ids distintos) |
| 4 | `TestPd4cMissingModelIsNotGuaranteed::test_pd_4c_missing_model_is_invariant_not_guaranteed` | PD-4c + PD-4d (flag omitida **y** valor vacío) |
| 5 | `TestPd4cClaudeCodeAliasesAreNotVerifiable::test_pd_4c_claude_code_aliases_are_not_verifiable` | PD-4c (`sonnet` vs `opus`) + PD-4d |
| 6 | `TestPd4dDeclarationIsCopyableIntoReviewMd::test_pd_4d_non_guaranteed_cases_emit_a_single_line_declaration` | PD-4d (declaración copiable, 3 casos) |
| 7 | `TestPd4dReviewGateReferenceMandatesTheCheck::test_pd_4d_review_reference_tells_the_reviewer_to_run_the_script` | PD-4d (referencia del gate, oráculo por conceptos) |
| 8 | `TestPd4eWarningNeverBlocksTheGate::test_pd_4e_every_comparison_outcome_exits_zero` | PD-4e (5 escenarios, los 4 veredictos) |
| 9 | `…::test_pd_4e_invalid_usage_exits_nonzero` | PD-4e (rc≠0 solo uso inválido) |
| 10 | `TestScriptIsRuntimeIndependent::test_script_names_no_provider_and_has_no_model_table` | §2.4 (independiente del runtime) |

**Fixed minimal CLI (declared in the module docstring, as authorized):**
`cdad_model_family.py --implementer M [--implementer-provenance T] [--reviewer M] [--reviewer-provenance T]`; stdout = un único objeto JSON con `verdict` (uno de los cuatro valores declarados) y `declaration` (texto copiable). Omitir `--reviewer` o pasarlo vacío = modelo faltante.

Oracle choices: veredicto machine-readable como oráculo primario; para «nunca garantizada» el test rechaza el token `guaranteed-by-configuration` **y** la frase de reclamo (`garantizada por configuración` / `guaranteed by configuration`), más la etiqueta literal «garantizada» en PD-4c (como pide el paquete). El mismo-stem exige además el concepto «misma familia / same family» en la salida. La independencia del runtime es un grep de tokens de proveedor sobre los bytes del script (los alias CC **no** se prohíben: reconocerlos o tratarlos como no interpretables es legítimo).

## 3. RED evidence

```
$ python3 -m pytest tests/test_006_003_u5_model_family.py -q
10 failed in 0.13s
```
All ten are **AssertionError about missing behaviour** — no ImportError/syntax/fixture error:
- 1,2,3,4,5,6,8,9,10 → `AssertionError: falta el script de verificación de familia: skills/cdad-cycle/scripts/cdad_model_family.py (§2.4/PD-4a..e)`.
- 7 → `AssertionError: PD-4d: ninguna referencia del gate de review indica correr el script de familia y registrar la declaración en review.md; revisado=['stage-4-review.md', 're-entry.md']; detalle=['stage-4-review.md: falta script de familia, declaración', 're-entry.md: falta script de familia, declaración']` — ambas referencias ya tienen «invariante/invariant» y «review.md», confirma que el oráculo es alcanzable.

```
$ python3 -m py_compile tests/test_006_003_u5_model_family.py
compile OK
```

## 4. Notas para el implementador (reglas que el test fija)

- Cuatro veredictos exactos: `same-family`, `guaranteed-by-configuration`, `not-verifiable`, `invariant-not-guaranteed`; cualquier otro valor falla el test 3.
- JSON único en stdout con `verdict` y `declaration`; la procedencia recibida debe aparecer en la salida (test 1).
- Mismo stem / ids distintos ⇒ **no** puede ser `guaranteed-by-configuration` y debe hablar de «misma familia».
- `invariant-not-guaranteed` y `not-verifiable` ⇒ `declaration` **una línea** que contenga «invariante no garantizado» o «invariant not guaranteed», y sin la etiqueta «garantizada».
- rc=0 en los cinco escenarios de comparación; rc≠0 solo con opción desconocida.
- Una de `references/stage-4-review.md` / `re-entry.md` debe nombrar el script, la declaración, el invariante y `review.md`.
- El script no debe contener `deepseek|glm|qwen|minimax|mofgw|openrouter|anthropic|openai|gemini|mistral`.

## 5. Regresiones esperadas

- **Ninguna por este RED:** el único cambio es un archivo nuevo de tests; ningún test existente se tocó ni se reformuló.
- El test 7 se pondrá verde recién cuando U5 edite una referencia del gate; hasta entonces es el único RED independiente del script.
- `scripts/validate-subagents.sh` (guard vacuo con `basic`, plan U5) no se ejerció: declarado, no confiado.

## 6. Declared deviations / honest limits (PD-15)

- Leí solo contrato (`spec.md`, `plan.md` ficha U5, `u4-red.md` como formato de entrega), `tests/conftest.py` y `tests/test_006_003_u1_…` como convención, y listados de directorio. No leí contenido de `skills/cdad-cycle/references/*` ni de ningún script: el oráculo conceptual del test 7 se definió por el paquete, no por el texto actual.
- «Garantizada» se prohíbe literalmente en PD-4c (lectura estricta del paquete); si el implementador quisiera escribir «no garantizada», el test lo rechaza — declarado para que la redacción evite la etiqueta.

## 7. Commit

```
9a103af test: 006-003 U5 RED — verificación de familia del reviewer (PD-4a..e)
 tests/test_006_003_u5_model_family.py | 540 ++++++++++++++++++++++++++++++++++
 1 file changed, 540 insertions(+)
 create mode 100644 tests/test_006_003_u5_model_family.py
```
Solo `tests/` staged. `docs/planning/` y `findings/incremental-construction-…md` siguen sin trackear y sin tocar. Sin `--no-verify`, sin stash, sin push.
