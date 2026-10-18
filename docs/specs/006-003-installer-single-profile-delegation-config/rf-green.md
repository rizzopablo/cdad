Now O-4, the diagnosis:
## Implementer report — GREEN de review-fix 006-003 (O-1, O-2, O-4)

### Resultado
Los 4 tests del RED `tests/test_006_003_rf_review_fixes.py` (commit `c57fc79`) pasan con el cambio mínimo de producción. Escribí **solo** en `skills/` (2 scripts + 1 referencia); `tests/` e `install.sh` intactos. No toqué los untracked ajenos (`docs/planning/`, `findings/…`) ni el HOME real ni `~/.config/cdad/*`.

### Cambios (3 archivos, +68/−37)
| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/scripts/cdad_delegate.py` | **O-2.** Nueva `cdad_config_dir()`: **una sola** función de ubicación (§2.2): `$XDG_CONFIG_HOME/cdad/` si XDG está definida y no vacía; si no `<base>/.config/cdad/` con `<base>` = `CDAD_INSTALL_ROOT` cuando está definida y no vacía, y HOME si no. `delegation_config_path()` (delegation.json) y `delegation_env_file_path()` (credencial por defecto) derivan **ambas** de ella (antes la credencial derivaba de la config, pero la base era `Path.home()`). |
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` | **O-1.** `_preflight_password()` recorre `OPENCODE_PASSWORD` → `OPENCODE_SERVER_PASSWORD` aceptando solo valor **no vacío**; `""` ⇒ ausente (§2.3), nunca header vacío, se sigue al archivo. **O-4.** `_unauthorized_diagnosis()` ahora ramifica por `credential["source"]`: fuente `environment` ⇒ «the value in use came FROM the ENVIRONMENT above (source: environment) and was rejected; no credential file was consulted»; cualquier otra ⇒ nombra el archivo con su ruta resuelta. Nunca interpola `None`. Se corrigieron los docstrings de `_preflight_credential`/`_unauthorized_diagnosis` (el `path` es `None` en la rama entorno). |
| `skills/cdad-cycle/references/cli-delegation.md` (§ Configuration) | Documenta la regla única (XDG → `CDAD_INSTALL_ROOT` → HOME), el valor vacío como ausente en entorno y que el diagnóstico 401/403 nombra la fuente usada (nunca `None`). |

`install.sh` no requería cambios: fue el **lector** el que divergía (`printf '%s/cdad' "${XDG_CONFIG_HOME:-$INSTALL_ROOT/.config}"` ya honraba `CDAD_INSTALL_ROOT`). **O-5 no se tocó** (el RED lo reportó no reproducible; sigue igual).

### Tabla test → resultado
| Test | Punto | RED (antes) | GREEN (después) |
|---|---|---|---|
| `TestO1EmptyEnvCredentialIsAbsent::test_o1_empty_environment_value_is_absent_and_the_file_is_used` | O-1 | FAIL `'blocked' != 'completed'` (header Basic vacío → 401) | **PASSED** |
| `TestO4IncorrectEnvCredentialDiagnosis::test_o4_401_diagnosis_omits_none_and_names_the_environment` | O-4 | FAIL (diagnóstico «credential file None») | **PASSED** |
| `TestO2RedirectedRootIsTheReaderBase::test_o2_g1_model_configured_in_the_redirected_root_reaches_the_argv` | O-2 | FAIL (sin `--model`: leía `Path.home()/.config`) | **PASSED** |
| `TestO2RedirectedRootIsTheReaderBase::test_o2_g2_default_credential_file_is_read_from_the_redirected_root` | O-2 | FAIL (401 → `blocked`) | **PASSED** |

### Comandos y salida (exactos, en `<repo>`)
```
$ python3 -m pytest tests/test_006_003_rf_review_fixes.py -x -q        # RED, árbol previo
E  AssertionError: 'blocked' != 'completed'  … diagnosis "…, or in the credential file None (…)"
FAILED …test_o1_empty_environment_value_is_absent_and_the_file_is_used ; 1 failed

$ python3 -m py_compile skills/cdad-cycle/scripts/cdad_delegate.py skills/cdad-cycle/scripts/cdad_delegate_opencode.py
COMPILE-OK

# 1ª corrida completa del focal bajo carga: 3 passed / 1 failed ('timeout')
AssertionError: 'timeout' != 'completed' … "destination 'opencode' did not answer within 2.0 seconds"

$ python3 -m pytest "tests/test_006_003_rf_review_fixes.py::TestO2…::test_o2_g2_default_credential_file_is_read_from_the_redirected_root" -q
1 passed in 8.87s

$ python3 -m pytest tests/test_006_003_rf_review_fixes.py -q
4 passed in 20.11s

$ python3 -m pytest tests/test_006_003_rf_review_fixes.py -v     # evidencia final
4 passed in 20.51s

$ python3 -m pytest tests/test_006_003_*.py -q
59 passed in 278.27s (0:04:38)

$ grep -l "cdad_delegate" tests/*.py
tests/test_005_007_reviewfix_blockings.py … tests/test_006_002_u5_transport_equivalence.py   (10 archivos)
$ python3 -m pytest <esos 10 archivos> -q
78 passed in 134.59s (0:02:14)
```
Nota de fidelidad (deuda conocida, declarada en el pedido): la 1ª corrida del focal dio **1 `'timeout'` bajo carga** en `test_o2_g2` (`destination 'opencode' did not answer within 2.0 seconds`, no un assert de comportamiento); aislado pasó de inmediato y las dos corridas completas posteriores pasaron 4/4. No retuné ningún timeout ni fixture.

### GATES
- focal verde ✅ (4/4, ×2) · `tests/test_006_003_*.py` ✅ 59/59 · adaptador (`grep -l "cdad_delegate"`) ✅ 78/78.
- Suite completa: **no** corrida (política del paquete: la corre quien cierra).

### Commit
```
ef8d2f868b4541ba5cda2a4fdccfd753174824de
fix: 006-003 review-fix GREEN — O-1 env vacío ausente, O-2 base única de config, O-4 diagnóstico nombra la fuente
 3 files changed, 68 insertions(+), 37 deletions(-)
```
Sin `--no-verify`, sin `git stash`, sin `push`. `git status` posterior: solo los untracked ajenos.

### Calidad y honestidad
- 5 checks: guard clauses/early exit (`cdad_config_dir`, loop con `return` temprano); estado ilegal irrepresentable (una sola función de ubicación ⇒ lector y escritor no pueden divergir); predecible/atómico (funciones puras sobre el entorno); fail-fast intacto (config malformada sigue fallando antes de despachar); naming intencional (`cdad_config_dir`, fuente explícita en el diagnóstico).
- Límites: mi cambio afecta la resolución de la config del proceso que lee (`XDG_CONFIG_HOME`/`CDAD_INSTALL_ROOT`/HOME de ese proceso); no medié ni verifiqué efectos de terceros. O-3 y O-6 quedan como deuda (por disposición); O-5 no se tocó. Si el orquestador necesita una corrida del focal sin la deuda de `'timeout'` bajo carga, la evidencia aislada ya está arriba.
