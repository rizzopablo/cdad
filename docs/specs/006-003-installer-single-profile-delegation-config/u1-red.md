I'll start by reading the approved contract and exploring the test scope.
Now I'll write the focal RED test for U1.
Now the reformulations. Starting with `tests/test_cdad_generate.py`:
Now the PD-3c, PD-4 and PD-14 tests in that file:
Now rewrite the acceptance matrix (profile dimension → absence of models):
Now `tests/validate-consistency.sh` (F001 model asserts + F008):
Now F008:
Now the fixtures that pass `--profile` to the generator:
Now `test_005_009_t3_spawn_reconciliation.py`, `test_bash_policy_selection.py`, `test_opencode_read_map_and_steps.py`, `test_cdad_adapters_opencode.py`:
## Informe — test-writer · RED de U1 (006-003)

### 1. Archivos (solo `tests/`)

| Archivo | Cambio |
|---|---|
| `tests/test_006_003_u1_generator_without_profiles.py` | **nuevo** — oráculo focal (6 tests) |
| `tests/test_cdad_generate.py` | reformulado: sin `--profile`, sin mapa, `unknown-profile` retirado, PD-14 → PD-1e/PD-7a |
| `tests/test_004_001_acceptance_matrix.py` | reformulado: eje de perfiles retirado, matriz fija **ausencia** de modelos |
| `tests/validate-consistency.sh` | F001 (2 asserts de celdas de modelo) y F008 (bloque completo que hacía `source cdad-models.sh`) invertidos a ausencia |
| `tests/test_005_004_t1_dispatch_tool_name.py`, `tests/test_005_006_t2_intake.py`, `tests/test_005_005_t4_integration.py`, `tests/test_005_009_t3_spawn_reconciliation.py`, `tests/test_bash_policy_selection.py`, `tests/test_opencode_read_map_and_steps.py`, `tests/test_cdad_adapters_opencode.py`, `tests/test_003_002_t4_integration.py` | se quitó `--profile` + constantes `PROFILE`/`GENERATOR_PROFILE` y la copia del mapa al sandbox |
| `tests/test_004_001_t6.py` | **solo comentario** (oráculo FROZEN intacto): declara que la tupla PD-14 pasa a oráculo negativo |

Ningún archivo de `scripts/`, `install.sh`, `Makefile`, `sources/`, `skills/`, `agents/`, `docs/` fue editado. `install.sh --basic` en recetas queda intacto (alias, D1).

### 2. Mapa test → PD

| Test | PD |
|---|---|
| `test_pd_1b_makefile_has_no_profile_and_staging_recipe_passes_none` | PD-1b |
| `test_pd_1c_model_map_script_is_absent_and_unreferenced` | PD-1c |
| `test_pd_1d_staging_manifest_has_no_profile_key` | PD-1d |
| `test_pd_1e_committed_agents_carry_no_model_line` | PD-1e |
| `test_pd_1f_generator_requires_no_profile_and_rejects_the_flag` | PD-1f |
| `test_pd_7a_generated_agents_fix_no_model` | PD-7a (generado) + INV-3 |
| `test_pd_1e_generated_agents_carry_no_model_line` / `test_pd_7a_generated_orchestrators_name_no_model` (`test_cdad_generate.py`) | PD-1e/PD-7a/INV-3 (**reemplazan** PD-14) |
| `test_postcondition_4_manifest_hashes_sources_and_regeneration_command` (assert invertido) | PD-1d |
| `test_postcondition_3c_unsupported_combinations_fail` (caso `unknown-profile` retirado) | PD-1f |
| `test_acceptance_1_frontmatter_fixes_no_model` (matriz) | PD-1e/INV-3 + §4.1 |
| F001 §2 orquestadores / F008 (`validate-consistency.sh`) | PD-7a/INV-3 · PD-1c/PD-1e |

### 3. Comandos y salida

```
$ python3 -m pytest tests/test_006_003_u1_generator_without_profiles.py
6 failed in 0.55s          # todas por AssertionError, ninguna por ImportError
  PD-1b: ['PROFILE ?= optimus'] != []
  PD-1c: scripts/cdad-models.sh still exists
  PD-1d: rc=2 != 0 (el generador exige --profile)
  PD-1e: 21 archivos con model: (línea 5)
  PD-1f: rc=2 != 0 sin --profile
  PD-7a: rc=2 != 0 (idem)

$ python3 -m pytest tests/test_cdad_generate.py -q
9 failed, 1 passed          # todas las corridas mueren en "--profile is required"

$ python3 -m pytest tests/test_004_001_acceptance_matrix.py -q
3 failed                    # generador sin perfil: rc=2

$ python3 -m pytest tests/test_005_004_t1_dispatch_tool_name.py tests/test_005_006_t2_intake.py tests/test_005_009_t3_spawn_reconciliation.py -q
4 failed, 28 passed

$ python3 -m pytest tests/test_005_005_t4_integration.py tests/test_003_002_t4_integration.py tests/test_004_001_t6.py -q
11 failed, 9 passed

$ python3 -m pytest tests/test_cdad_adapters_opencode.py tests/test_opencode_read_map_and_steps.py tests/test_bash_policy_selection.py -q
5 failed, 2 passed, 2 errors (AssertionError de precondición del fixture, no ImportError)

$ bash tests/validate-consistency.sh
Assert PASS: 155 / Assert FAIL: 6
  FAIL F001 §2 CC names a model · FAIL F001 §2 OC names a model
  FAIL F008 mapa retirado · FAIL F008 agent con model: · FAIL F008 consumidores del mapa
  FAIL F011 scripts/validate-subagents.sh  ← PRE-EXISTENTE/ambiental (ver §5)
```

### 4. Regresiones esperadas post-U1 (declaradas, no barridas)

Couplings de perfil **fuera del alcance de este packet** (los toqué: no), que quedarán rojos hasta que su unidad los reformule:
- `tests/test_005_004_t2_installer_claims.py` — usa `make staging PROFILE=`, instala `--optimus`/`--basic` y asserta `manifest["profile"]` (unidad de flags del instalador / PD-1a-PD-2 de 005-004).
- `tests/test_install_ownership.py:281-308` — clave `profile` del manifiesto de ownership (la spec §6.3 la nombra explícitamente; unidad del manifiesto).
- `tests/test_install_review5_regressions.py` — marcador `.cdad-models-profile` y `CDAD_MODEL_PROFILE`.
- `tests/test_005_010_t3_references.py` — asserta que la referencia instalable **nombra** `scripts/cdad-models.sh` (PD-7b / textos de skills).
- `validate-consistency.sh` F001 restante: asserts de `--basic` y de la prosa de §2 del SKILL (PD-7b).

### 5. Límites honestos

- F011 de `validate-consistency.sh` falla por estado del **host** (la copia instalada en el HOME del usuario reporta DRIFT sobre un `__pycache__/*.pyc` obsoleto). No depende de este cambio (mi diff es solo `tests/`) — lo declaro, no lo arreglo.
- No leí código de implementación ni `tests/.sensitive-patterns.local`. Solo sondeé el CLI del generador black-box (`--help`) y conté ocurrencias (`grep -c '^model:'`), nunca contenido.
- Secuenciación declarada en el docstring focal: mientras el generador exija `--profile` (PD-1f), PD-1d y PD-7a se detienen en esa precondición y lo dicen en el mensaje.

### 6. Commit

```
d5b2ae0 test: 006-003 U1 RED — generador sin perfiles ni mapa de modelos
13 files changed, 610 insertions(+), 342 deletions(-)
```
`docs/planning/` y `findings/…` siguen sin trackear y fuera del commit. Sin `--no-verify`, sin stash, sin push.
