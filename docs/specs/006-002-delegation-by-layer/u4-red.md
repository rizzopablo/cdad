I'll start by reading the approved contract and the relevant test files.
Now let me read the key test files I need to modify and understand.
Let me check the repo state and how the validate script's helpers are structured near F001.
Now I have what I need. Let me write the new focal RED test module.
The spec's discovery names the exact concrete example (`mofgw/qwen3.7-plus`) — my reused oracle misses that form. Let me check the RED detail for test 4 and then strengthen the handoff-prompts oracle.
All 5 fail for the right reason. Let me update the module docstring to match the observed RED state.
Now the coupled u2 edit — remove the temporary §2 exclusion (PD-11 surface).
Now remove the `model_scan_text` neutralization function and its use:
u2 test #1 now passes (U3 is GREEN); let me correct the docstring to the observed state.
Now the F001 reformulation in `tests/validate-consistency.sh`:
The §2 awk extraction returned empty. Let me probe (counts only, no content) which heading form the oracle must accept:
The §2 heading is level 3 (`###`). Let me fix the awk extraction to be level-based:
F001 now fails for the right reason (4 content asserts; orchestrator caveats still pass). Now let me run the focal test plus the coupled/adjacent modules:
All changes confined to `tests/`. Now the commit (only `tests/`):
Commit `3c828ad` done. Let me capture the final evidence output for F001 (new asserts fail; orchestrator caveats pass):
RED de U4 completo. Informe de rol.

## 1. Archivos modificados (solo `tests/`)

| Archivo | Cambio |
|---|---|
| `tests/test_006_002_u4_skill_without_models.py` | **NUEVO** (+285) — oráculo focal de PD-11 |
| `tests/test_006_002_u2_neutral_skill.py` | retirada la neutralización **TEMPORAL de §2 marcada «U4»** del oráculo de modelos; docstrings/mapa al día (acoplado, enmienda A-1) |
| `tests/validate-consistency.sh` | **F001 reformulado, no borrado** (enmienda A-1): exige la frase nueva de §2 de `SKILL.md` + conserva el caveat de `basic` en los orquestadores generados |

`git diff --stat` → `2 files changed, 92 insertions(+), 55 deletions(-)`; `+ tests/test_006_002_u4_skill_without_models.py` (352 líneas totales del commit).

## 2. Mapa test → PD (estado RED observado)

| Test | PD | Estado |
|---|---|---|
| `u4::TestPd11Section2WithoutModels::test_pd11_section2_drops_the_model_family_column` | PD-11 / D-6 | **FAIL** — ofensores `SKILL.md:67`, `:79` «Model family» (§2 = líneas 65-83) |
| `…::test_pd11_section2_drops_the_profiles_paragraph` | PD-11 / D-6 | **FAIL** — ofensor `SKILL.md:77` `--basic` (**la línea exacta que el spec declara**) |
| `…::test_pd11_section2_has_no_concrete_model_identifier` | PD-11 / INV-2 | **FAIL** — 12 ofensores: `deepseek-v4-pro`, `deepseek-v4-flash`, `glm-5.2`, proveedor `deepseek` |
| `…::test_pd11_section2_declares_the_configured_model_sentence` | PD-11 / INV-7 | **FAIL** — faltan los conceptos 1 «modelo configurado en el runtime», 2 «la skill no nombra modelos», 6 «garantizada por configuración», 7 «declarada» |
| `u4::TestPd11HandoffPromptsWithoutModelExamples::test_pd11_handoff_prompts_has_no_concrete_model_example` | PD-11 / INV-2 | **FAIL** — `qwen3.7-plus` (el ejemplo declarado por discovery §1 #18: `mofgw/qwen3.7-plus`) |
| `u2::TestPd1SkillWithoutRuntimeTools::test_pd1_no_concrete_model_in_delegation_context` (acoplado) | PD-1 / INV-2 (+PD-11) | **FAIL** — los 12 ofensores de §2, ahora dentro del alcance del oráculo |
| `validate-consistency.sh` F001 (acoplado, 4 asserts nuevos) | PD-11 | **4 FAIL** de contenido (frase nueva ausente) + **4 PASS** conservados (caveat de `basic` en ambos orquestadores) |
| `005-010 T3 #5` (revisado) | — | **sin cambios**: su `DOCUMENTS = (cli-delegation.md,)` — no fija nada de §2; verde |

## 3. Comandos y salida (resumida)

```
python3 -m pytest tests/test_006_002_u4_skill_without_models.py -q
→ 5 failed in 0.09s          # 5/5 AssertionError de CONTENIDO; 0 ImportError/SyntaxError/NameError
```
```
python3 -m pytest tests/test_006_002_u2_neutral_skill.py -q
→ 1 failed, 3 passed           # el FAIL es el oráculo de modelos (acoplado); #1 (formas de tool) y los 2 de §4 verdes
```
```
python3 -m pytest tests/test_006_002_u4_skill_without_models.py tests/test_006_002_u2_neutral_skill.py \
  tests/test_006_002_u3_runtime_references.py tests/test_006_002_u1_delegation_section.py \
  tests/test_005_010_t3_references.py tests/test_005_005_t2_docs_policy.py -q
→ 6 failed, 30 passed in 2.93s  # los 6 son exactamente los RED de arriba; u3/u1/005-010/005-005 verdes
```
```
bash tests/validate-consistency.sh
→ FAIL: F001 (006-002 PD-11): SKILL.md §2 lacks the 'model of each role = the one configured in the runtime' sentence
→ FAIL: F001 (006-002 PD-11): SKILL.md §2 lacks the 'the skill names no models' declaration
→ FAIL: F001 (006-002 PD-11): SKILL.md §2 lacks the 'guaranteed by configuration' half of the reviewer-family invariant
→ FAIL: F001 (006-002 PD-11): SKILL.md §2 lacks the 'declared' half of the reviewer-family invariant
→ PASS: F001: agents/cdad-orchestrator.md mentions the --basic profile … (×2 orquestadores)
→ PASS: F001: agents/{,claude-code/}cdad-orchestrator.md caveats the anti-bias invariant for the basic profile
→ PASS: F001: CC/OC orchestrator §2 composed/free-of-foreign-models (PD-14/D7, sin cambios)
→ FAIL: F011: scripts/validate-subagents.sh (active profile)      # preexistente y ambiental (U1/U2/U3)
→ Assert PASS: 157 / Assert FAIL: 5
```
```
bash -n tests/validate-consistency.sh            → OK
python3 -m py_compile tests/test_006_002_u4_….py tests/test_006_002_u2_….py → OK
```

## 4. Commit

`3c828ad  test: 006-002 U4 RED — SKILL.md §2 sin modelos (PD-11) y F001 reformulado` — 3 archivos, todos bajo `tests/` (+392/−55); sin `--no-verify`, sin `git stash`, sin push. `docs/planning/` y `findings/incremental-construction…md` (sin trackear, no míos) quedaron intactos y **fuera** del commit (`git status` limpio salvo esos dos).

## 5. Justificación de cada cambio acoplado (por PD)

- **u2 (PD-11, enmienda A-1)** — la neutralización de §2 era deuda declarada con dueño U4; su RED la retira. La mitad de modelos pasa a medir el árbol instalable completo salvo `context-meter.md` (INV-8). Sin cambio semántico para las formas de herramienta.
- **F001 (PD-11/D-6)** — la nota de perfiles (`--basic` + caveat de la invariante) sale de §2; su cobertura **no se pierde**: se repunta a los orquestadores generados, cuya sección `delegation` declara la familia no garantizada (PD-4/D-3, U1). Se agrega la exigencia de la frase nueva de §2. Todo reformulado en el RED, nunca en el GREEN.
- **#5 revisado** — `test_005_010_t3_references.py` no fija §2 (su superficie es `cli-delegation.md`); no se toca.

## 6. Límites y riesgos declarados (honestos)

1. **Sin lecturas de implementación para derivar aserciones**: no abrí ni leí `skills/`, `sources/`, `scripts/`, `agents/`. Los ofensores que cito salen de los **mensajes de falla de mis propios tests** (el test lee el producto por diseño). **Desvío declarado (menor)**: ejecuté **dos sondas estructurales de solo-conteo** sobre `skills/cdad-cycle/SKILL.md` (`grep -c` de patrones de encabezado y conteo de niveles `#`) para saber a qué nivel está delimitado §2 y escribir el extractor awk de F001 — la salida fueron **conteos, nunca líneas ni contenido**. Además leí `discovery.md` (en `read_scope`) para el ejemplo concreto `mofgw/qwen3.7-plus`.
2. **El oráculo compartido no captura la forma del ejemplo retirado**: `CONCRETE_MODEL_ID_RE` exige el guion pegado a la familia, y `\bqwen\b` falla con la versión embebida (`qwen3.7-plus`). Declaré `EMBEDDED_VERSION_MODEL_RE` en u4 (por el ejemplo que el contrato nombra). Consecuencia declarada: **u2 sigue ciego a esa forma exacta** para `handoff-prompts.md`; el guard vive en u4, que es la unidad dueña de ese archivo (PD-11). No lo "arreglé en silencio" en u2.
3. **Observable del «párrafo de perfiles»**: lo operacionalicé como la ausencia de sus dos marcas en §2 (`--basic` y el caveat bajo `basic`) — las marcas que F001 fijaba. Hoy el flag está en §2:77, la línea que el spec declara. Si el implementer conservara `--basic` dentro de §2 en la frase nueva, el test lo bloquearía: lo declaro para que el orquestador adjudique (la spec no lo pide; F001 mueve ese caveat a los orquestadores).
4. **No renombré** `test_pd1_no_concrete_model_in_delegation_context` en u2, aunque su alcance ya es todo el texto instalable, para no invalidar los artefactos históricos `u2-red.md`/`u2-green.md`; el docstring y el mensaje declaran el alcance ampliado (sobre-cubrir no genera falsa confianza).
5. **F011 es preexistente y ambiental** (`scripts/validate-subagents.sh`, perfil activo, drift de la instalación en HOME — reportado desde U1/U2/U3); ajeno a `tests/`. Mi diff de F001 aporta exactamente 4 FAIL nuevos y retira 3 PASS de `SKILL.md` (reemplazados por los 4 asserts nuevos) + conserva los 4 de orquestadores.
6. **Suite completa no corrida** (política del packet: la cierra el closer). `make validate` incluye `validate-odoo-specialization.sh`, no tocado.
7. Ningún fallo RED es `ImportError`/`SyntaxError`; los 5 focales y el acoplado de u2 son `AssertionError` sobre contenido.
