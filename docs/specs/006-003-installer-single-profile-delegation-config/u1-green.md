I'll start by reading the approved spec and understanding the current state.
Now let me implement. Starting with the generator:
Now remove the model map section:
Now the frontmatter builders:
Now the models note:
Now `compose_role_agent`:
Now `compose_orchestrator_agent`:
Now the assembly/manifest and main:
Now `main()` — remove `--profile` and add the explicit rejection:
Now the Makefile:
Now let me replace the model-map block in `validate-subagents.sh`:
Now remove the model map script and update `install.sh` minimally:
Now the install.sh edits:
Now regenerate the agents and run the focal test:
I'll wait for the regression run to complete before committing.
The regression run confirms the final tree. Now staging explicitly and committing:
Trabajo terminado. Reporte:

---

# Informe — implementer · GREEN de U1 (006-003)

**Commit:** `afcd14f` — `feat: 006-003 U1 GREEN — generador sin perfiles ni mapa de modelos` (31 archivos, +180 / −487; sin `--no-verify`, sin stash, sin push). `docs/planning/` y `findings/…` quedaron sin tocar y fuera del commit (`git status --short` solo los muestra a ellos como `??`).

## 1. Archivos modificados

| Archivo | Cambio |
|---|---|
| `scripts/cdad-generate.py` | sin `--profile` (rechazo explícito con rc=2), sin `validate_profile`/`model_for`/`subprocess`, sin `model:` en frontmatter (OC+CC), `models_note`→`model_note()` sin perfiles ni nombres, §2 sin columna Model ni celdas, manifiesto sin `profile` y sin el mapa entre las fuentes |
| `Makefile` | sin `PROFILE ?= optimus`; receta `staging` sin `--profile` |
| `scripts/cdad-models.sh` | **retirado** (`git rm`) |
| `scripts/validate-subagents.sh` | bloque del mapa retirado → stage de **ausencia** de `model:` en los bytes instalados; sin `SCOPED_MODEL_EXCEPTION` (quedaba muerto) |
| `scripts/cdad-bash-allowlist.sh` | dejaba de funcionar: pasaba `--profile basic` al generador (consumidor de producción) → se quitó |
| `sources/agents/adapters/opencode.md` / `claude-code.md` | **solo** el bullet de frontmatter `model:` |
| `sources/roles/orchestrator.md` | §2 sin celdas de modelo; prosa del anti-sesgo sin el mapa retirado; quitada la línea meta que el generador recortaba |
| `install.sh` | **mínimo** por el `source` retirado: sin `source cdad-models.sh`, sin `validate_profile` (+ sus 2 llamadas), `want_model=""` en el check legado; `--basic` sigue aceptado. El resto (flags/ayuda/marcador) es U2 |
| `agents/**` (22) | regenerados con `make agents` |

## 2. Test → resultado

| Test | Resultado |
|---|---|
| `test_006_003_u1_generator_without_profiles.py` (focal, 6) | ✅ 6 passed |
| `test_cdad_generate.py` (10) | ✅ 10 passed |
| `test_004_001_acceptance_matrix.py` (3) | ✅ 3 passed |
| `test_004_001_t6.py` (9) | ✅ 9 passed |
| `test_005_004_t1_dispatch_tool_name.py` (7) | ✅ 7 passed |
| `test_005_005_t4_integration.py` (5) | ✅ 5 passed |
| `test_005_006_t2_intake.py` (6) | ✅ 6 passed |
| `test_005_009_t3_spawn_reconciliation.py` (19) | ✅ 19 passed |
| `test_bash_policy_selection.py` (2) | ✅ 2 passed |
| `test_cdad_adapters_opencode.py` (3) | ✅ 3 passed |
| `test_opencode_read_map_and_steps.py` (4) | ✅ 4 passed |
| `validate-consistency.sh` F001 (14 asserts) / F008 (3) | ✅ PASS todos |
| Lista de 45 tests que leen agentes/generador (`grep -l "cdad-generate\|agents/" tests/*.py`) | 4 failed / **342 passed** / 1 skipped |
| Regresiones declaradas de otras unidades (no tocadas) | `test_005_004_t2_installer_claims` 2F/6P · `test_install_ownership` 1F/10P · `test_install_review5_regressions` 1F/4P · `test_005_010_t3_references` 1F/4P |
| `bash tests/validate-consistency.sh` | **159 PASS / 2 FAIL** (baseline: 155/6) |

## 3. Comandos y salida (extractos)

```
$ python3 -m pytest tests/test_006_003_u1_generator_without_profiles.py -q
6 passed in 2.12s

$ python3 scripts/cdad-generate.py --runtime opencode --stack odoo --out /tmp/.../gen
cdad-generate: 12 files -> .../gen/agents/opencode (+ manifest.json)      rc=0
$ python3 scripts/cdad-generate.py --runtime opencode --stack odoo --profile optimus --out ...
ERROR: `--profile` (and any profile name) is no longer a generator option: ... delegation configuration
(delegation.json, per destination and role). Run: scripts/cdad-generate.py --runtime <…> --stack <…> --out <…>
rc=2
manifest keys: ['artifacts','generator','manifest_version','runtime','stack','stack_arg']
regenerate:   python3 scripts/cdad-generate.py --runtime opencode --stack odoo --out <staging-dir>

$ make agents  (x2)   → hash de agents/** idéntico: eba2a52d…b9a1   (sin diff)
$ grep -rc '^model:' agents/cdad-*.md agents/claude-code/*.md | grep -v ':0'   → vacío

$ CDAD_INSTALL_ROOT=/tmp/.../root bash install.sh --basic          → rc=0 (Verify: PASS — 11 cdad agents)
$ CDAD_INSTALL_ROOT=/tmp/.../root bash install.sh --basic --check  → rc=0 (Check: PASS, 391 grupos en sync)

$ bash tests/validate-consistency.sh
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
FAIL: F011: tests/validate-odoo-specialization.sh → FAIL
Assert PASS: 159 / Assert FAIL: 2
```

## 4. ⚠️ BLOQUEO — oráculo aprobado que exige el mapa (no lo toqué)

`tests/validate-odoo-specialization.sh:125-137` (**P1.reviewer**, parte de `make validate`, invocado por F011) lee la línea `model:` de `agents/cdad-{implementer,reviewer}-odoo.md` y exige que existan y difieran → `imp='' rev=''`. **Ese oráculo exige exactamente lo que PD-1e/INV-3 prohíbe** y **no fue reformulado en el RED `d5b2ae0`** (la lista de oráculos reformulados no lo incluye). Es el caso previsto por el packet («si otro oráculo aprobado exige el mapa, detenete y reportalo»): no lo edité, no lo rodeé, no reintroduje `model:`. **Decisión requerida del orquestador**: RED del test-writer sobre ese bloque (declarando el reemplazo, A-1) y luego re-corrida de `validate-consistency.sh`. Es la única causa no-ambiental de los 2 FAIL.

## 5. Límites honestos

- **F011/`validate-subagents.sh`** falla por estado del host, preexistente: la instalación real en `$HOME` está stale (`__pycache__/*.pyc` y ahora `cdad-orchestrator.md`). El stage `[models]` nuevo de ese script sí pasa: `✅ models OK (no agent fixes a model; … PD-1e/INV-3)`.
- **Diferido a U2** (no lo toqué, lo declara el packet «el resto de install.sh es U2»): `--economical|--optimus|--premium` siguen **aceptados** por `install.sh`; `--help` aún nombra modelos/perfiles; `resolve_profile`/`write_profile_marker`/`PROFILE MISMATCH` y el marcador `.cdad-models-profile` siguen ahí.
- **Residual declarado (fuera de la lista de cambios del packet):** los 5 `sources/roles/*.md` conservan la línea meta `Model: per profile from \`scripts/cdad-models.sh\` — never a concrete model name here.`, que se compone en 10 agentes. No fija modelo ni la cubre PD-1e/PD-7a (que solo miran `^model:` y los orquestadores), pero referencia un archivo retirado: para decisión de U2/U3/reviewer.
- No corrí la suite completa (política del packet: la corre quien cierra). No subí nada ni reescribí commits.
- Durante la corrida conjunta de 45 archivos vi 3 fallos de `test_005_009_t2_opencode_adapter.py` (`'timeout' != 'completed'/'cancelled'`, fixture de servidor): pasó 8/8 dos veces en aislamiento y 8/8 en la segunda corrida conjunta → contención de carga, no regresión.
