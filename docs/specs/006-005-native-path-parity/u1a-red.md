## Role report — test-writer RED, 006-005 U1a

### Archivos modificados
- **Nuevo:** `tests/test_006_005_u1a_runtime_config.py` (981 líneas, sha256 `68adaff284c77d16b6be7ab4984331e75baa793b12c055ede4d5b41c250e959c`).
- Nada fuera de `tests/`. No se tocaron `docs/planning/` ni `findings/…` (siguen sin trackear).

### Mapa test → PD

| Test | PD / cláusula |
|---|---|
| `test_pd8_missing_runtime_names_the_flag_on_the_default_verb` | PD-8 (sin flag, verbo por defecto) |
| `test_pd8_missing_runtime_names_the_flag_on_an_explicit_verb` | PD-8 (sin flag, `dispatch` explícito) |
| `test_pd8_runtime_without_a_module_is_rejected_naming_the_value` | PD-8 (valor sin módulo) |
| `test_pd8_valid_runtime_proceeds_to_the_single_source_check` | PD-8 (valor válido ⇒ siguiente comprobación: la sección) |
| `test_pd8_flat_v1_context_runtime_is_never_read` | PD-8 / V-9 (contexto v1 plano que declara `runtime`) |
| `test_pd9_missing_section_diagnostic_names_file_section_and_correspondence` | PD-9 / §2.6 (archivo + sección + correspondencia clave por clave) |
| `test_pd9_section_with_model_is_rejected_naming_delegation_json` | PD-9 / §2.6 (clave `model` en la sección) |
| `test_pd9_derived_section_is_inspected_key_by_key` | PD-9 / §2.6 (documento derivado, clave por clave; sin `runtime`/`model`/credencial) |
| `test_pd9_exec_config_token_is_rejected_before_any_effect_default_verb` | PD-9 / D-11 (dos formas, verbo por defecto, sin escritura) |
| `test_pd9_exec_config_token_is_rejected_before_any_effect_on_migrate_o7` | PD-9 / O-7 (dos formas, `migrate`, sin escritura) |
| `test_pd9_help_never_declares_the_retired_option` | PD-9 (control negativo de `--help`) |
| `test_pd9_legacy_document_is_not_probed_outside_the_migration_step` | PD-9 / D-11 (sin sondeo de ubicaciones heredadas) |
| `test_pd25_migrate_without_section_writes_the_section_key_by_key` | PD-25 / §2.6.1 (escritura clave por clave; sin `model`/credencial) |
| `test_pd25_migrate_with_existing_section_refuses_and_keeps_bytes` | PD-25 / INV-7 (no pisa; bytes idénticos) |
| `test_pd25_migrate_dry_run_does_not_write` | PD-25 / §2.6.1 (`--dry-run` sin escritura + imprime la sección) |
| `test_pd25_migrate_missing_legacy_file_fails_naming_the_path` | PD-25 / §2.6.1 (archivo ausente) |
| `test_pd9_installer_creates_the_runtimes_template_when_missing` | PD-9 / §2.6 (plantilla del instalador) |
| `test_pd9_installer_does_not_register_the_template_in_the_manifest` | PD-9 / §2.6 / INV-7 (no se registra en el manifiesto) |
| `test_pd9_reinstall_does_not_overwrite_the_user_runtimes_section` | PD-9 / §2.6 / INV-7 (no se pisa en reinstalación) |

Fixture: CLI invocada como **proceso** (`sys.executable …/cdad_dispatch.py`) sobre proyecto descartable y `XDG_CONFIG_HOME`/`HOME` temporales; instalador sobre **copia del producto** con staging regenerado y `CDAD_INSTALL_ROOT` redirigido (nunca HOME, nunca repo).

### Comandos y salida

**Focal RED** (`19 failed`, todas por aserción de conducta faltante — ninguna por import/colección):
```
python3 -m pytest -q tests/test_006_005_u1a_runtime_config.py
→ 19 failed in 33.65s
```
Causa de cada fallo, verificada en la salida: el diagnóstico no nombra `--runtime` / el valor sin módulo / `runtimes.json` / `delegation.json` / la ruta ausente; `migrate`/`--help`/`--dry-run` no existen (rc=2, aserción `rc == 0`), y el instalador no crea `.config/cdad/runtimes.json`. Todos son `AssertionError` con el mensaje de la PD; ninguno es `ImportError`/`SyntaxError`.

**Regresiones de la ficha U1a** (verdes hoy):
```
python3 -m pytest -q tests/test_006_003_u2_installer_without_profiles.py \
  tests/test_005_004_t2_installer_claims.py tests/test_006_003_u7_prune_obsolete.py \
  tests/test_install_review5_regressions.py tests/test_006_003_rf_review_fixes.py \
  tests/test_006_003_rf2_review_fixes.py
→ 37 passed in 318.80s
```
`make validate` es gate de unidad en GREEN (lo corre quien implementa/cierra), no se ejecutó en este RED.

### A-1 (tests acoplados)
**Ninguno encontrado.** Las seis regresiones de la ficha U1a pasan con la conducta nueva aún inexistente; no hubo test que reformular. La nota del plan sobre `CONFIG_REL_PATHS` (conjunto abierto) se confirma con la corrida.

### Dependencias / límites declarados (en el docstring del módulo)
- La verificación posterior con `capabilities --runtime X` (PD-10) y la config transitoria que `dispatch` entrega al módulo son superficie **U1b/U2**: marcadas como dependencia, sin test que falle por ellas aquí.
- El «documento derivado inspeccionado clave por clave» de U1a es la **sección que escribe `migrate`** (el mismo documento que §2.6 enumera); el archivo transitorio de `dispatch` no es observable antes de U1b.
- Límite honesto del oráculo «ninguna lectura heredada fuera de migración»: la apertura de archivos no es observable black-box; se fija la **interfaz** (token retirado rechazado en todos los verbos, ausente de `--help`, archivo heredado en rutas plausibles ni adoptado ni modificado, y única lectura = la del archivo pasado a `migrate`).

### Aislamiento
No se leyó código de implementación (`skills/cdad-cycle/scripts/`, `install.sh`, `agents/`, `sources/`, `build/`). Solo se listaron **nombres** de `skills/cdad-cycle/scripts/` para confirmar que `opencode` tiene módulo de runtime. No se leyó `tests/.sensitive-patterns.local`. Sin valores del host.

### Commit
```
5dbc8549c2355295198ff6978fa0edbb03fb898c
test: 006-005 U1a RED — runtime config, explicit runtime, migrate and installer template
 tests/test_006_005_u1a_runtime_config.py | 981 +++++++++++++++++++++++++++++++
```
Un solo archivo, solo `tests/`; sin `--no-verify`, sin stash, sin push.