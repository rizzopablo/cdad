# RED report — 005-004-claude-code-roles / T2 (test-writer, etapa 3)

- Paquete: `005-004-claude-code-roles-test-writer-red-002` (rol test-writer, subetapa `red`).
- Contrato: `docs/specs/005-004-claude-code-roles/spec.md` (sha256 `79d57e0a…`; §2 tabla, §3 PD-2/PD-5, §5 AC-2/AC-5) + `plan.md` (sha256 `f7c61a59…`, ficha T2 y su bloque `plan-tasks`).
- Commit de los tests: `0964694`.
- Write scope respetado: sólo `tests/`. No se editó implementación.

## 1. Archivos modificados

| Archivo | Tipo |
|---|---|
| `tests/test_005_004_t2_installer_claims.py` | nuevo (focal declarado por el paquete) — 684 líneas |

`git diff --stat` acotado (el commit contiene exactamente ese path):

```
 tests/test_005_004_t2_installer_claims.py | 684 ++++++++++++++++++++++++++++++
 1 file changed, 684 insertions(+)
```

No commiteado por mí (no es mío, pre-existente al despacho): `docs/.cdad-state.json` aparece `M` en `git status --short` porque el orquestador registró el despacho de este paquete. Fuera de mi write scope: no lo toqué.

## 2. Mapa test → postcondición / criterio (un test por afirmación observable)

Todos en `tests/test_005_004_t2_installer_claims.py`:

| Test | PD / criterio | Estado hoy |
|---|---|---|
| `test_pd2_i_sweep_no_declared_surface_claims_the_installer_removes_the_model_field` | PD-2(i) / AC-2 | **ROJO** (AssertionError: `['sources/agents/adapters/claude-code.md:16']`) |
| `test_pd2_ii_adapter_states_the_installer_deploys_staged_bytes_untransformed` | PD-2(ii) / AC-2 (+ coincidencia con `install.sh --help`) | **ROJO** (AssertionError) |
| `test_pd2_ii_adapter_attributes_the_missing_model_line_to_the_generation_profile` | PD-2(ii) / AC-2 | **ROJO** (AssertionError) |
| `test_pd5_adapter_declares_no_model_per_role_under_basic` | PD-5(a) / AC-5 | **ROJO** (AssertionError) |
| `test_pd5_adapter_declares_the_installer_does_not_guarantee_the_anti_bias_invariant` | PD-5(b) / AC-5 | **ROJO** (AssertionError) |
| `test_pd5_adapter_references_the_exemption_source_instead_of_copying_it` | PD-5(c) / PD-9 / AC-5 | **ROJO** (AssertionError) |
| `test_pd2_ii_isolated_install_deploys_staged_cc_agent_bytes_verbatim` | PD-2(ii) / AC-2 (control positivo) | verde |
| `test_pd2_ii_basic_profile_absence_is_produced_by_the_generator` | PD-2(ii), PD-5 / AC-5 (control) | verde |

## 3. Comandos exactos y salida

### 3.1 Focal (RED)

```
python3 -m pytest tests/test_005_004_t2_installer_claims.py -q
```

```
FFFFFF..                                                                 [100%]
…
FAILED tests/test_005_004_t2_installer_claims.py::test_pd2_i_sweep_no_declared_surface_claims_the_installer_removes_the_model_field
FAILED tests/test_005_004_t2_installer_claims.py::test_pd2_ii_adapter_states_the_installer_deploys_staged_bytes_untransformed
FAILED tests/test_005_004_t2_installer_claims.py::test_pd2_ii_adapter_attributes_the_missing_model_line_to_the_generation_profile
FAILED tests/test_005_004_t2_installer_claims.py::test_pd5_adapter_declares_no_model_per_role_under_basic
FAILED tests/test_005_004_t2_installer_claims.py::test_pd5_adapter_declares_the_installer_does_not_guarantee_the_anti_bias_invariant
FAILED tests/test_005_004_t2_installer_claims.py::test_pd5_adapter_references_the_exemption_source_instead_of_copying_it
6 failed, 2 passed in 13.70s
```

**Motivo de cada RED (todos `AssertionError` de comportamiento declarado; ningún `ImportError`/`SyntaxError`/`NameError`, ningún error de entorno):**

1. PD-2(i) @`L303`: el barrido encuentra la afirmación prohibida, con localizador `['sources/agents/adapters/claude-code.md:16']` — exactamente la ocurrencia que el contrato nombra (`spec §9: sources/agents/adapters/claude-code.md:15-17`). Las superficies declaradas se recorren completas (8 archivos de texto en `sources/`, 117 en `skills/`, `install.sh`), y los controles de vacuidad del propio predicado pasan: detecta la frase que el contrato cita («The installer STRIPS the model field at install time»), su forma en castellano («El instalador quita el campo `model`»), y **no** marca la negación («does not strip», «strips nothing»).
2. PD-2(ii) mecanismo @`L373`: el adaptador no enuncia el mecanismo real (copia de los bytes staged sin transformación). El control de coincidencia pasa: `install.sh --help` (rc 0) declara hoy «the installer transforms nothing» y «the deployed bytes are the staged bytes».
3. PD-2(ii) causa @`L397`: el adaptador no atribuye la ausencia de la línea `model:` al perfil de generación (hoy la atribuye al instalador).
4. PD-5(a) @`L423`: el adaptador no declara que bajo `basic` no hay modelo por rol.
5. PD-5(b) @`L445`: el adaptador no declara que el instalador **no** garantiza la invariante reviewer≠implementer.
6. PD-5(c) @`L479`: el adaptador no declara la exención como explícita y visible.

### 3.2 Regresiones declaradas por el paquete

```
python3 -m pytest tests/test_install_ownership.py tests/test_install_review5_regressions.py -q
```

```
................                                                         [100%]
16 passed in 446.39s (0:07:26)
```

### 3.3 Lint del archivo nuevo

```
python3 -m ruff check tests/test_005_004_t2_installer_claims.py
```

```
All checks passed!
```

## 4. Qué verifica cada control verde (no-regresión)

- **Instalación en raíz aislada, perfil que SÍ fija modelos** (control positivo, verde hoy): en una copia temporal del repo se genera el staging con `make staging PROFILE=optimus` y se instala con `CDAD_INSTALL_ROOT` a un directorio temporal. Los **11** agentes de Claude Code desplegados (mapeados por el manifiesto de propiedad `<root>/.cdad-install-manifest.json`, `source` → `agents/claude-code/*.md`) son **byte a byte** los bytes staged; el manifiesto no reporta conflictos; y la línea `model:` **viaja a la salida** (todos los staged la llevan y los desplegados también). Es la evidencia de que el instalador **no** quita nada, contra lo que hoy afirma el adaptador.
- **Instalación en raíz aislada, perfil `basic`** (control, verde hoy): con `make staging PROFILE=basic`, **ningún** agente de Claude Code staged lleva la línea `model:` — la ausencia es del **generador**— y la salida desplegada tampoco la lleva y sigue siendo copia verbatim de los bytes staged; el manifiesto de propiedad registra `profile: basic`.
- **Vacuidad del barrido** (dentro del RED 1): el predicado se prueba contra la afirmación que el contrato cita (EN y ES) y contra sus negaciones; el corpus declarado se exige no vacío (suelos 5 archivos en `sources/`, 50 en `skills/`, `install.sh` presente) para que un glob roto no pase en verde.
- **Reuso del patrón existente (PD-9):** la instalación aislada y los lectores de manifiesto se **importan** de la regresión declarada `tests/test_install_ownership.py` (`run_installer`, `load_staging_manifest`, `load_install_manifest`), sin duplicar el patrón.

## 5. Bloqueos / límites honestos (declarados, no silenciosos)

1. **Superficie del barrido = la declarada por PD-2(i) y por el paquete**: `sources/`, `skills/`, `install.sh`. La **segunda ocurrencia** que el contrato nombra (`scripts/cdad-generate.py:443-446`, comentario `strip`) queda **fuera** de esa superficie declarada y **no** se barre aquí: su corrección está en el alcance de T2 (plan §4) pero **no** la fuerza este focal, y no se amplió el barrido por iniciativa propia (límite declarado, no silencioso).
2. **Costo del focal ≈ 14 s** (dos instalaciones aisladas del set staged completo, dominadas por las copias de los árboles de skill). Las regresiones declaradas tardaron 7m26s.
3. **El chequeo anti-copia es un heurístico declarado**: cuenta corridas de 12 tokens del adaptador que aparecen literalmente en el dueño (`scripts/validate-subagents.sh`). Detecta una oración copiada; una paráfrasis por debajo de 12 tokens no se detecta.
4. **Los enunciados de prosa se verifican por co-ocurrencia de conceptos** en ventanas de 45-55 palabras (los grupos de alternativas cubren las formas razonables). El contrato fija el **contenido** del enunciado, no su redacción: si el GREEN lo redacta con otro vocabulario, la aserción falla y se resuelve en el contrato (no se relaja el oráculo desde el rol).
5. **No se leyó código de implementación** al escribir los tests: no se abrieron `scripts/*.py`, `skills/**`, `sources/**` ni `install.sh`. Lecturas declaradas durante la autoría (no son implementación): la **ayuda publicada** por `install.sh --help` (superficie observable con la que PD-2/AC-2 exige que el enunciado coincida), los **artefactos generados** `build/staging/manifest.json` y los bytes staged de `build/staging/agents/claude-code/**` (salida declarada del generador, mismo precedente que T1), y el `Makefile` (citado por `spec §9` y por `tests/test_cdad_generate.py`; leído para conocer el entrypoint declarado `make staging PROFILE=`, fuera de mi read scope declarado). Las líneas de `sources/`/`scripts/` que un fallo pudiera exponer **no** se volcaron: las aserciones comparan booleanos y los mensajes nombran path:línea, nunca el texto.
6. **Nunca HOME**: la instalación del focal corre con `CDAD_INSTALL_ROOT` en un directorio temporal y el fixture **afirma** que la raíz está bajo el directorio temporal y **no** bajo HOME; no se ejecuta `--check` contra la instalación del dueño. El fixture nunca escribe en el checkout real (copia temporal + `make staging` dentro de la copia).
7. **La suite completa no se corrió** (política del paquete: la corre una vez quien cierra). Sólo focal + regresiones declaradas + lint.
8. **`make agents` no se ejecutó** en el repo (escribiría `agents/`, fuera de `tests/`): el focal usa el generador de staging dentro de copias temporales.
9. Sin `--no-verify`, sin push, sin desplegar, sin tocar HOME, sin leer `tests/.sensitive-patterns.local`.

## 6. Evidencia de commit

```
0964694 test: 005-004 T2 RED — el instalador despliega los bytes staged y la ausencia de model viene del perfil (PD-2/PD-5)
 tests/test_005_004_t2_installer_claims.py | 684 ++++++++++++++++++++++++++++++
 1 file changed, 684 insertions(+)
```
