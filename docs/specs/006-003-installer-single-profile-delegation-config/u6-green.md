I'll start by reading the spec, the RED test, and the implementation files.
Now let me implement. First, the delegation-side helpers in `cdad_delegate.py`:
Now update `_preflight_server` to use the credential document:
Now let's run the focal test:
Now the proportional regression — adapter + I8 tests, and the 006-003 suite:
Now document the credential load in the reference (§ Configuration):
Let me capture direct evidence of the rewritten diagnosis (temp-only config dir, sentinel-free):
Re-running the full gate list after the documentation edit:
All gates pass. Committing:
# Implementer report — `006-003` U6 GREEN (credencial del servidor OpenCode)

**Packet**: `006-003-installer-single-profile-delegation-config-implementer-green-007` · role `implementer` / substage `green` · contract `docs/specs/006-003-installer-single-profile-delegation-config/spec.md` @ `c25ebf0e…d18890` (leído y verificado).

## 1. Cambios (3 archivos, todos dentro del write scope `skills/**`)

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` | +166: `_credential_file_path()`, `_credential_file_value()`, `_read_credential_file()`, `_os_error_text()`, `_preflight_credential()`, `_unauthorized_diagnosis()`; `_preflight_server()` consume el documento de credencial; docstring del módulo (ítem 6) y de `_preflight_password` |
| `skills/cdad-cycle/scripts/cdad_delegate.py` | +32: `DELEGATION_ENV_FILE_NAME`, `delegation_env_file_path()` (default `<config-dir>/cdad/opencode-server.env`, misma regla XDG/§2.2 que `delegation.json`) y `delegation_credential_env_file()` (lectura tolerante del documento de config) |
| `skills/cdad-cycle/references/cli-delegation.md` | +16 en § *Configuration*: carga de la credencial (entorno → `credential_env_file`/default, `KEY=value`+`#`, vacío = ausente, permisos sobre el fd, diagnóstico 401/403) — **sin valores** |

Decisiones de implementación (mínimas, contra la spec §2.3/PD-5/D5):
- **Solo modo `server`**: `_preflight_credential()` sólo se alcanza desde `_preflight_server` (único consumidor de la credencial).
- **Entorno primero**: si `OPENCODE_PASSWORD` o `OPENCODE_SERVER_PASSWORD` está presente, el archivo no se lee. Dentro del archivo, misma precedencia → primer valor no vacío de `OPENCODE_PASSWORD`, luego `OPENCODE_SERVER_PASSWORD` (PD-5e).
- **Permisos sobre el fd abierto** (`os.open` + `os.fstat`, nunca `os.stat(path)`): patrón TOCTOU de `cdad_packet.py:_ProjectLock`; se rechaza `S_IMODE & 0o077` (0600/0400 aceptados).
- **INV-1**: el valor sólo viaja al header Basic; no se imprime, registra, ni entra en argv/diagnóstico (el diagnóstico lo declara explícitamente).
- **Diagnóstico 401/403** autosuficiente: ambas variables con su orden, ruta resuelta, procedencia (`opencode serve` en uso, en el entorno del proceso que despacha) y, si fue rechazado, **ruta + modo** (`0o644 (-rw-r--r--)`) — nunca el valor.
- Lectura del `delegation.json` **tolerante** para la clave opcional (`credential_env_file`): un documento ausente/ilegible/no-string cae al default en vez de bloquear; la validación estricta v1 de `delegation_model` sigue guardando la clave contractual (el modelo).

## 2. Tabla test → resultado

| Test | PD | Antes (RED) | Ahora |
|---|---|---|---|
| `…u6…::TestPd5aMissingCredential::test_pd_5a_401_diagnosis_names_vars_path_and_provenance` | PD-5a | FAIL (`assert_names_path`) | **PASS** |
| `…::TestPd5bInsecurePermissions::test_pd_5b_world_readable_file_rejected_naming_path_and_mode` | PD-5b | FAIL (`assert_names_path`) | **PASS** |
| `…::TestPd5cSecureFileUsed::test_pd_5c_0600_file_credential_is_used_and_never_leaks` | PD-5c/INV-1 | FAIL (`'blocked' != 'completed'`) | **PASS** |
| `…::TestPd5dEnvWinsOverFile::test_pd_5d_environment_wins_over_file` | PD-5d | PASS (ancla) | **PASS** (no-regresión) |
| `…::TestPd5eEmptyValueIsAbsent::test_pd_5e_empty_value_is_absent_never_an_empty_header` | PD-5e | FAIL (`'blocked' != 'completed'`) | **PASS** |
| `…::TestPd5CredentialEnvFileRedirect::test_pd_5_credential_env_file_redirects_the_source` | §2.2/§2.3/D5 | FAIL (`'blocked' != 'completed'`) | **PASS** |

## 3. Comandos y salidas (exactos, preservados)

```
# RED previo (confirmado antes de tocar implementación)
python3 -m pytest tests/test_006_003_u6_server_credential.py -q
→ 5 failed, 1 passed in 11.88s   (fallas: 2×assert_names_path, 3×'blocked' != 'completed')

# GATE 1 — focal
python3 -m pytest tests/test_006_003_u6_server_credential.py -q
→ ......  6 passed in 12.36s

# GATE 2 — adaptador + consumidores de I8 (grep -l "cdad_delegate" tests/*.py, 10 ficheros)
python3 -m pytest tests/test_005_007_reviewfix_blockings.py tests/test_005_007_t4_…py \
  tests/test_005_007_t5_delegation_dispatch.py tests/test_005_009_t1_interface.py \
  tests/test_005_009_t2_opencode_adapter.py tests/test_005_010_t1_durable_signal.py \
  tests/test_006_001_t1_selection.py tests/test_006_001_t2_wait_recovery.py \
  tests/test_006_002_u1_delegation_section.py tests/test_006_002_u5_transport_equivalence.py -q
→ 78 passed in 128.03s     (sin ningún `'timeout' != 'completed'`: la deuda de carga no se manifestó)

# GATE 3 — oráculo de secretos, aislado
python3 -m pytest "tests/test_006_001_t1_selection.py::TestPd5NoSecretsInOutputs" -q
→ ..  2 passed in 4.12s

# GATE 4 — suite 006-003 (incluye focal)
python3 -m pytest tests/test_006_003_u1_… tests/test_006_003_u2_… tests/test_006_003_u3_… \
  tests/test_006_003_u4_… tests/test_006_003_u5p_… tests/test_006_003_u6_… -q
→ 44 passed in 94.30s

# GATE 5 — consistencia
bash tests/validate-consistency.sh
→ Assert PASS: 168 / Assert FAIL: 1
  FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
  (detalle: `install.sh --check failed` por drift de HOME: diff contra
   ~/.claude/agents/*.md, ~/.config/opencode/skills/cdad-cycle, ~/.agents/skills/cdad-cycle,
   ~/.claude/skills/cdad-cycle — ficheros que no toqué ni genero; declarado como drift de HOME)

# Referencias que grepean cli-delegation.md (por haber editado el doc)
python3 -m pytest tests/test_005_010_t3_references.py tests/test_006_002_u2_… tests/test_006_002_u3_… \
  tests/test_006_002_u4_… tests/test_006_002_u6_… tests/test_006_002_reviewfix.py -q
→ 31 passed in 2.92s

# Evidencia directa del diagnóstico (sólo temporales; ningún valor real)
XDG_CONFIG_HOME=<tmp> HOME=<tmp>/home python3 -c '<carga del módulo y _unauthorized_diagnosis>'
→ PD-5a: "…must be available to the PROCESS that dispatches: in its ENVIRONMENT under
  OPENCODE_PASSWORD (first), then OPENCODE_SERVER_PASSWORD, or in the credential file
  <tmp>/cdad/opencode-server.env … mode 0600 or 0400. The value is never shown here."
→ PD-5b: "… the credential file <tmp>/cdad/opencode-server.env is group/world accessible:
  found mode 0o644 (-rw-r--r--), refused, no credential was sent"  | header enviado: None
→ 0600/0400 → credencial usada; vacío ⇒ ausente; `leak: False`

# calidad: sin líneas >88 en lo agregado; py_compile OK en ambos scripts
```

## 4. Commit

```
797b935 feat: 006-003 U6 GREEN — credencial del servidor OpenCode (PD-5a..e, INV-1)
 skills/cdad-cycle/references/cli-delegation.md     |  16 ++
 skills/cdad-cycle/scripts/cdad_delegate.py         |  32 ++++
 skills/cdad-cycle/scripts/cdad_delegate_opencode.py| 173 ++++++++++++++++++-
 3 files changed, 214 insertions(+), 7 deletions(-)
```
Sin `--no-verify`, sin `git stash`, sin push. `git status`: sólo los 3 modificados; `docs/planning/` y `findings/incremental-…md` siguen **untracked e intactos**.

## 5. Límites honestos (PD-15)

- **No corrí la suite completa**: política del paquete (la corre quien cierra, una vez). Corrí el focal + la regresión proporcional declarada.
- **F011 sigue rojo y es pre-existente** (drift de HOME, ficheros que no toqué: lista de fallo incluye agentes sin relación con este cambio). No lo "arreglé" ni lo silencié.
- **Riesgo residual declarado** (ya anunciado en el RED): en modo `server` sin `XDG_CONFIG_HOME` definida, el default se resuelve bajo `~/.config/cdad/` (regla de `delegation.json`, §2.2 vía `delegation_config_path()`), igual que ya hacía la config de delegación; los tests que no redirigen XDG podrían leer un `opencode-server.env` homónimo del host. No observé impacto (78/78 verdes) y no relajé ningún oráculo; el dueño/cierro decide si corresponde alinear `delegation_config_path()` con `<install-root>/.config` (fuera de la ficha U6).
- El valor de la credencial lo consume sólo el header Basic del preflight; no hay ruta nueva a argv/stdout/stderr/I8 (verificado por el oráculo de ausencia con centinela de PD-5c y por inspección del diff).
- No leí `~/.config/cdad/*` ni credenciales reales (sólo directorios temporales creados por mí). No toqué `tests/**` ni `install.sh`.
