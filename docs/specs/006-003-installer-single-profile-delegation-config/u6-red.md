I'll start by reading the approved contract and the existing tests (read scope only).
Now let me find the existing test patterns — especially the 006-001 server-mode fixture and any 006-003 tests.
Let me examine the server fixture patterns used in tests (without reading implementation).
Let me check the current test behavior (running tests is allowed) and the state file.
Let me read the adapter test harness (`AdapterCase`) to reuse its fixture correctly.
Let me check how existing tests pass a credential via env and observe the server header (to confirm the observable).
Now I'll write the RED test file.
Now let me run the new test file to prove RED and check each failure is an AssertionError about missing behavior.
RED confirmed (5 failed, 1 passed). Let me verify each failure is the intended assertion and not a fixture error.
All five failures are the intended assertion misses. Let me slightly broaden the "proceso que despacha" concept regex so it stays a concept oracle without over-constraining the GREEN wording.
Let me confirm determinism (run twice) and check the shared 006-001 base suite still behaves (regression baseline).
Deterministic RED and green baseline unchanged. Now commit only the test file.
# test-writer report — RED de U6 (006-003): credencial del servidor OpenCode

## Packet / contract
- **path**: `docs/specs/006-003-installer-single-profile-delegation-config/spec.md` — sha256 verificado en lectura (`c25ebf0e…d18890`).
- **substage**: `red`; write scope `tests/**`; sin tocar implementación (`install.sh`, `scripts/`, `agents/`, `skills/`, `sources/`, `build/`).
- **Enmienda A-4 respetada**: U6 no toca `install.sh` (los archivos de config los crea U4). Sólo tests.

## Archivos
- **Nuevo (único)**: `tests/test_006_003_u6_server_credential.py` (500 líneas) — commit `e2eba98`.

## Mapa test → PD
| Test | PD | Oráculo |
|---|---|---|
| `TestPd5aMissingCredential::test_pd_5a_401_diagnosis_names_vars_path_and_provenance` | PD-5a | fixture 401 sin credencial → `blocked`; diagnóstico nombra ambas vars, **la ruta resuelta** `<config>/cdad/opencode-server.env`, y la procedencia por conceptos (`entorno`/`environment`, proceso que `despacha|dispatch|proceso`, `serve`) |
| `TestPd5bInsecurePermissions::test_pd_5b_world_readable_file_rejected_naming_path_and_mode` | PD-5b | `.env` 0644 → `blocked`, diagnóstico con ruta + modo (`0?644`); fixture **sin** header `Authorization` |
| `TestPd5cSecureFileUsed::test_pd_5c_0600_file_credential_is_used_and_never_leaks` | PD-5c | `.env` 0600 (con comentario `#`) → `completed`, fixture recibe `basic(FILE_PASSWORD)`; centinela **ausente** en stdout/stderr/diagnóstico, argv del destino y registro I8 |
| `TestPd5dEnvWinsOverFile::test_pd_5d_environment_wins_over_file` | PD-5d | env + archivo con valores distintos → `completed` con el valor de **env**, nunca el del archivo |
| `TestPd5eEmptyValueIsAbsent::test_pd_5e_empty_value_is_absent_never_an_empty_header` | PD-5e | `OPENCODE_PASSWORD=` vacío + `OPENCODE_SERVER_PASSWORD=<centinela>` → `completed` con el centinela y **nunca** header vacío |
| `TestPd5CredentialEnvFileRedirect::test_pd_5_credential_env_file_redirects_the_source` | §2.2/§2.3/D5 | `credential_env_file` apunta a otra ruta (default con valor distinto) → se usa la ruta configurada |

**Formato de archivo**: `KEY=value` + comentarios `#` ejercitados en PD-5c/5e. **Invariante INV-1** cubierto por el oráculo de ausencia de PD-5c.

## Fixture (black-box, nunca host)
- Adaptador OpenCode en modo `server` contra `FakeInfoServer` (loopback HTTP propio del test, reutilizado por import de `test_006_001_t1_selection`) exigiendo **Basic auth**; el harness `Pd600T1Case.dispatch` ya **stripea** `OPENCODE_PASSWORD`/`OPENCODE_SERVER_PASSWORD` del entorno del hijo.
- `XDG_CONFIG_HOME` y `HOME` redirigidos a un temporal del test; sólo **centinelas** (nunca la config del host, nunca `~/.config/cdad`). Base reutilizada por import: `Pd600T1Case`, `FakeInfoServer`, `basic_auth_header`, `FAST_WAIT`, `MATCHING_CLIENT_SEMVER`, `dispatch_records`.

## Comandos y salida resumida
```
python3 -m pytest tests/test_006_003_u6_server_credential.py --collect-only -q
  → 6 tests collected (sin tests foráneos importados)

python3 -m pytest tests/test_006_003_u6_server_credential.py -q
  → 5 failed, 1 passed in 9.94s      (repetido 2×: 5 failed, 1 passed — determinista)

python3 -m pytest tests/test_006_001_t1_selection.py -q
  → 18 passed in 33.94s              (baseline del fixture compartido sin regresión)

git commit → e2eba98 test: 006-003 U6 RED — credencial del servidor OpenCode (PD-5a..e)
  git show --stat: 1 file changed, 500 insertions(+)
```

**Motivo de cada falla (todas `AssertionError` de comportamiento ausente, nunca Import/sintaxis):**
- PD-5a → falla en `assert_names_path`: diagnóstico actual = `"…the password is read from OPENCODE_PASSWORD, then OPENCODE_SERVER_PASSWORD (never its value)"` (nombra las dos vars, **no** la ruta ni la procedencia).
- PD-5b → falla en `assert_names_path` (mismo diagnóstico; sin ruta ni modo).
- PD-5c / PD-5e / `credential_env_file` → `'blocked' != 'completed'` (hoy el archivo no se lee → sin header → 401).

## Declaración honesta (PD-15)
- **PD-5d puede PASAR hoy** (declarado, no oculto): el adaptador vigente ya resuelve por entorno y no lee el archivo, así que "gana env" ya se cumple trivialmente. Queda como ancla de no-regresión para el camino de lectura de archivo; es el único de los 6 tests verde en rojo (5/6 fallan por aserción).
- El archivo `tests/` sigue la disciplina de oráculo por comportamiento; no se leyó código de implementación (`scripts/`, `install.sh`, adaptador). Sólo se leyeron tests existentes y la spec.
- No se leyó `tests/.sensitive-patterns.local`; no se tocó ningún archivo fuera de `tests/`; no se usó `--no-verify`, `git stash` ni `push`. Los untracked ajenos (`docs/planning/`, `findings/…`) quedan intactos.

## Regresiones esperadas / deuda reportada
- **Baseline verde**: `test_006_001_t1_selection.py` 18/18 PASS tras agregar el focal (el fixture compartido no se modificó).
- **Riesgo declarado para GREEN/U6**: si el adaptador deriva el default `<install-root>/.config/cdad/opencode-server.env` por defecto, tests de servidor existentes que no redirigen `XDG_CONFIG_HOME` podrían pasar a leer un archivo homónimo bajo la raíz del producto — hoy inexistente, sin impacto observado. A vigilar en el cierre.
- **Deuda conocida de carrera del fixture HTTP** (declarada en la ficha): no se relajó ningún oráculo; se mantuvieron las cotas default y el resultado fue determinista en 2 corridas.
