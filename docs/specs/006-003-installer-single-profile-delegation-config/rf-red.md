Now I have the pieces I need. Let me write the RED test file.
The O-5 behavior observed contradicts my expectation — the reinstall **preserved** the empty-sha record (as CONFLICT) and returned rc=1. Let me probe the product's published behavior more precisely before concluding.
Two decisive probes were inconclusive against the review's O-5 claim. Let me probe two more surfaces (dry-run preview, and the clean-flow carry-forward record) before reporting.
The O-5 requirement is **already satisfied** by the current tree (probes in every path). Let me now verify O-2 is RED for the right reason.
O-2 g1 fails for exactly the right reason (no `--model` at all). Now let me remove the O-5 test (which cannot be RED — the requirement already holds) and document that mismatch in the artifact.
Now remove the O-5 test class:
Now let me read the final file to verify it is clean and coherent:
## Role report — test-writer / RED · `006-003-installer-single-profile-delegation-config` (review-fix round)

**Resultado:** RED entregado para **O-1, O-2 y O-4** (4 tests, `4 failed` por `AssertionError` de comportamiento, determinista en 3 corridas). **O-5 NO se testeó: no es reproducible contra el árbol** — el escenario que pide la disposición ya se cumple; reporto el mismatch con evidencia y pido disposición (no inventé postcondición sustituta).

### 1. Archivos modificados
```
tests/test_006_003_rf_review_fixes.py  (nuevo, 398 líneas)
```
Commit **`c57fc79`** `test: 006-003 review-fix RED — O-1/O-2/O-4 por aserción (O-5 reportado no reproducible)` — `1 file changed, 398 insertions(+)`, **solo `tests/`**. `docs/planning/` y `findings/…` (untracked ajenos) intactos; sin `--no-verify`, sin stash, sin push.

### 2. Mapa test → O-n (la review ES la postcondición)
| Test | Hallazgo · contrato | Oráculo |
|---|---|---|
| `TestO1EmptyEnvCredentialIsAbsent::test_o1_empty_environment_value_is_absent_and_the_file_is_used` | **O-1 · §2.3 (`spec.md:44`)** + PD-5e | `OPENCODE_PASSWORD=""` exportado + archivo 0600 con el valor ⇒ `completed`, el fixture recibe la credencial **del archivo** y **nunca** `Basic("")` (fixture HTTP local, header observable) |
| `TestO4IncorrectEnvCredentialDiagnosis::test_o4_401_diagnosis_omits_none_and_names_the_environment` | **O-4 · §2.3 (`spec.md:48`)** | 401 con credencial de entorno incorrecta ⇒ `blocked`, diagnóstico **sin `None`** como ruta y con el **entorno** nombrado como fuente |
| `TestO2RedirectedRootIsTheReaderBase::test_o2_g1_model_configured_in_the_redirected_root_reaches_the_argv` | **O-2 · §2.2 (`spec.md:28`) + D3** | `CDAD_INSTALL_ROOT=<root>`, XDG sin definir, `HOME` en OTRO tempdir ⇒ el modelo configurado en `<root>/.config/cdad/delegation.json` (el que crea el instalador, verificado como precondición) **llega al argv** del destino |
| `TestO2RedirectedRootIsTheReaderBase::test_o2_g2_default_credential_file_is_read_from_the_redirected_root` | **O-2 · §2.3 (default `<config-dir>/cdad/opencode-server.env`)** | mismo escenario con la credencial por defecto bajo la raíz ⇒ `completed` + Basic recibido |

Fixture: `RedirectedRootReaderCase(InstallerHarness, ServerCredentialCase)` — copia de producto con staging regenerado (el instalador **escribe** la config) + adaptador stageado/binario falso (el **lector** se observa por argv y por el fixture HTTP). Cotas: `FAST_WAIT` y tope de 300 s sin retocar (la carrera conocida de `test_pd2_connection_refused…` no aplica: todos mis fixtures son alcanzables).

### 3. Comandos y salida (RED probado)
```
$ python3 -m py_compile tests/test_006_003_rf_review_fixes.py      → COMPILE_OK
$ python3 -m pytest tests/test_006_003_rf_review_fixes.py --collect-only -q  → 4 tests collected
$ python3 -m pytest tests/test_006_003_rf_review_fixes.py -q --tb=line
FFFF                                                                     [100%]
case.py:732: AssertionError: 'blocked' != 'completed'                   ← O-1 (header vacío ⇒ 401)
case.py:732: AssertionError: 'None' unexpectedly found in "… credential file None …"  ← O-4
case.py:744: AssertionError: False is not true : O-2/§2.2/D3 … argv:
   ['run','--agent','cdad-test-writer','--session','ses_…','--standalone','--auto']      ← O-2 g1 (sin --model)
case.py:732: AssertionError: 'blocked' != 'completed'                   ← O-2 g2 (diagnóstico cita $HOME/.config/cdad/…)
4 failed in 18.79s
```
Repetido 2 veces más: `4 failed in 19.10s` / `18.80s` — mismo conjunto, mismas aserciones (sin ImportError/sintaxis/fixture).

### 4. O-5 — mismatch del pedido, con evidencia (no testeado)
El pedido: «un registro del manifiesto con sha256 vacío, cuyo archivo ya no se despliega, NO se retira en la reinstalación (se conserva y se reporta)».

Probé black-box sobre **esta misma revisión** (`git log/diff 401d951..HEAD`: `install.sh` **byte-idéntico** al HEAD revisado; solo cambió `docs/`), copia de producto desechable, raíces redirigidas, editando a mano el manifiesto publicado (`sha256` vacío / `null` / espacios / digest erróneo / clave ausente; en `artifacts` y en `pending_removal`):
```
reinstalación → archivo INTACTO + "CONFLICT: <ruta> — preserved (obsolete own file … modified
                locally since the recorded install …)", rc=1, registro conservado en pending_removal,
                y los hermanos intactos del mismo origen SÍ se retiran (el prune corrió)   [7 variantes]
--uninstall   → "… modified locally since the recorded install; PRESERVED for explicit resolution"
--dry-run     → "DRY-RUN CONFLICT … preserved" (no borra nada)
--check       → PENDING-REMOVAL sobre la ruta preservada
```
Es decir: el requisito que la disposición pide para O-5 **ya se cumple** en todas las superficies y representaciones probadas; una aserción RED sería un fallo fabricado. La cita de la review (`install.sh:654`, `[ -z "$recorded" ] → removable`) no se corresponde con el comportamiento observado (el sha no verificable se trata como `modified`, que es lo que pide INV-2). **Decisión pedida al orquestador:** dar O-5 por deuda/cerrado, re-scopear, o nuevo packet.

**Observación lateral del mismo probe (NO asertada aquí, no es postcondición de este packet):** con el sha registrado **vacío**, el registro preservado se publica en `pending_removal` con los campos **permutados** (`{"sha256": "<ruta del source>", "source": ""}`); el flujo limpio PD-6b publica el registro coherente. Es un defecto de coherencia del manifiesto (el slot del digest queda con una ruta) — candidato a finding propio, no lo convertí en test sin contrato.

### 5. Límites honestos
- **Nunca leí implementación**: `install.sh`, `scripts/*` y `sources/` nunca abiertos; la forma del manifiesto se observó *ejecutando* el instalador y leyendo su salida publicada. No leí `tests/.sensitive-patterns.local`.
- Nunca se tocó `HOME` real ni `~/.config/cdad/*` (todo `CDAD_INSTALL_ROOT`/`HOME` temporales, INV-6); solo centinelas locales.
- Reutilicé fixtures por import declarado (`InstallerHarness`, `ServerCredentialCase`, `AdapterCase`/`FakeInfoServer`): ninguna base importada aporta métodos de test (collect-only: 4).
- Suite completa **no** corrida (política del paquete: la corre quien cierra).
- Modelo reportado por el runtime: `deepseek-v4.1-flash` (mofgw) — observación, `model_policy: ordinary`, sin efecto sobre permisos.

---

> **Corrección del orquestador (2026-10-18):** la afirmación del §4 de que O-5 «ya se cumple» quedó refutada por la re-review (`rereview.md`, B-1). Con sha y source vacíos, el registro se retira sin comparar bytes, porque el TSV que lee `read` de bash colapsa las columnas vacías. Las 7 variantes probadas no incluían ese caso.
