All gates are green. Here is the role report.

---

# Role report — implementer / GREEN — 006-005 U6-8

**Packet:** `006-005-native-path-parity-implementer-green-017` · **substage:** `green` · **execution:** `exec-006-005-native-path-parity-001`
**Contract:** `docs/specs/006-005-native-path-parity/spec.md` (sha256 `3a824be3…`, approved) + decisión del owner `docs/epics/epic-006-opencode-concurrency/execution.md`:353 (§hallazgo **U6-8**).

## 1. Archivos modificados (2 — ninguno de tests/)

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` | `_preflight_server`: el `binary_version` **configurado** que difiere de lo **observado** ya **no bloquea**; la diferencia se **declara** en una `note` que el llamador adjunta al diagnóstico del intento (`dispatch_note`). El control que queda es **cliente observado vs servidor observado** (fail-closed antes de lanzar). El fail-closed por **capacidad del store** (columna ausente → se nombra) queda intacto. |
| `skills/cdad-cycle/scripts/cdad_dispatch.py` | `migrate` mueve `MIGRATED_SECTION_KEYS` (= `SECTION_KEYS` **sin** `binary_version`) y el informe `--dry-run` anuncia ese mismo conjunto. `binary_version` **sigue** en el vocabulario de la sección y en la correspondencia clave por clave del diagnóstico de sección ausente (intactos). |

La nota declarada (viaja en el `diagnosis` del sobre):

> `the configured 'binary_version' 'opencode u6fix8 2.0.0' differs from the observed runtime version '3.1.4': the version is OBSERVED, never read from the configuration — the difference is declared and does not block (the compatibility of the store is verified by capacity, not by this number)`

## 2. Tabla test → resultado

| Test | Postcondición | Resultado |
|---|---|---|
| `test_u68_configured_version_difference_does_not_block_the_dispatch` | PD-10/E5 (U6-8) | **GREEN** (antes RED: `blocked` != `completed`) |
| `test_u68_dispatch_without_configured_version_proceeds_and_capabilities_report_the_observed_one` | PD-10/E5 (U6-8) — GUARD | GREEN (conservado) |
| `test_u68_observed_client_and_server_versions_that_differ_fail_closed_naming_both` | PD-10/E5 + PD-12 — GUARD | GREEN (conservado) |
| `test_u68_store_without_a_correlation_column_fails_closed_naming_the_column` | PD-10/E5 + PD-12 — GUARD | GREEN (conservado) |
| `test_u68_migrate_does_not_write_the_configured_version` | PD-10/E5 + PD-25/§2.6.1 | **GREEN** (antes RED) |
| `test_pd9_derived_section_is_inspected_key_by_key` (A-1) | PD-25/§2.6.1 | **GREEN** (antes RED) |
| `test_pd25_migrate_without_section_writes_the_section_key_by_key` (A-1) | PD-25/§2.6.1 | **GREEN** (antes RED) |
| `test_pd25_migrate_dry_run_does_not_write` (A-1) | PD-25/§2.6.1 | **GREEN** (antes RED) |
| `test_pd9_missing_section_diagnostic_names_file_section_and_correspondence` | PD-9 (§2.6) | GREEN (conservado: la correspondencia sigue nombrando `binary_version`) |

## 3. Comandos y salida

```
$ python3 -m pytest tests/test_006_005_u6fix8_version_by_observation.py -v     # ANTES (RED)
FAILED …::test_u68_configured_version_difference_does_not_block_the_dispatch
FAILED …::test_u68_migrate_does_not_write_the_configured_version
2 failed, 3 passed in 8.69s

$ python3 -m pytest tests/test_006_005_u6fix8_version_by_observation.py -v     # DESPUÉS
5 passed in 9.96s

$ python3 -m pytest tests/test_006_005_u1a_runtime_config.py -v
19 passed in 32.24s

$ python3 -m pytest tests/test_006_005_u6fix8_version_by_observation.py tests/test_006_005_u1a_runtime_config.py   # post-commit
24 passed in 40.27s

$ python3 -m pytest tests/test_006_005_*.py
139 passed in 148.17s (0:02:28)

$ python3 -m pytest tests/test_006_001_t1_selection.py tests/test_006_001_t1b_service_mode.py \
    tests/test_006_003_u6_server_credential.py tests/test_005_010_t2_load_mode_invocation.py \
    tests/test_005_009_t2_opencode_adapter.py
55 passed in 90.61s (0:01:30)

$ python3 -m pytest tests/test_006_003_u2_installer_without_profiles.py tests/test_005_004_t2_installer_claims.py \
    tests/test_006_003_u7_prune_obsolete.py tests/test_install_review5_regressions.py \
    tests/test_006_003_rf_review_fixes.py tests/test_006_003_rf2_review_fixes.py
37 passed in 343.02s (0:05:43)

$ python3 -m pytest tests/test_006_001_t3_concurrency.py tests/test_006_001_reviewfix.py \
    tests/test_005_009_t1_interface.py tests/test_005_010_t4_integration.py tests/test_006_001_t3_integration.py
10 passed, 2 skipped in 28.34s

$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL      ← ambiental, ver §5

$ ruff check skills/cdad-cycle/scripts/cdad_delegate_opencode.py skills/cdad-cycle/scripts/cdad_dispatch.py
Found 3 errors (F541)  → los MISMOS 3 en HEAD (verificado con `git show HEAD:<file> | ruff check -`): ninguno nuevo
```

Suite completa **no** ejecutada (política declarada: la corre quien cierra, una vez).

## 4. Commit

```
$ git add skills/cdad-cycle/scripts/cdad_delegate_opencode.py skills/cdad-cycle/scripts/cdad_dispatch.py
$ git commit -m "fix: 006-005 U6-8 — version por observacion, no por config"
[main cca7e5d] fix: 006-005 U6-8 — version por observacion, no por config
 2 files changed, 47 insertions(+), 24 deletions(-)
```
Sin `--no-verify`, sin `git stash`, sin push. `tests/` intacto (0 archivos del commit son de tests). `docs/.cdad-state.json` (estado del paquete, del orquestador), `docs/planning/` y `findings/` quedan **sin commitear** (no son míos).

## 5. Límites y hechos declarados

1. **F011 ambiental (NO lo introduce este cambio).** `make validate` falla 1 de 169. Causa: la instalación en HOME está más vieja que el repo — `install.sh --check` reporta `DRIFT` en `cdad_packet.py` + sus `.pyc` (**ajenos a este cambio**) y `MISSING (staged but not installed)` para `agents/opencode/cdad-orchestrator.md` y `cdad-reviewer.md`. Prueba de que el drift de mis dos archivos es sólo "no desplegado todavía": las copias instaladas en HOME de `cdad_delegate_opencode.py` y `cdad_dispatch.py` son **byte-idénticas a HEAD** (`sha256 9aeb2d08…` / `bdc23c73…`); el despliegue en HOME es orden del owner (`execution.md`:352). El cambio no toca `agents/`, `sources/` ni el manifiesto de instalación.
2. **Flakiness conocida del margen del waiter bajo carga — reproducida y NO es regresión.** Con 4 procesos pytest concurrentes: `test_006_001_t3_concurrency.py` falla 2/2 con `'timeout' != 'completed'` (`"destination 'opencode' did not answer within 4.0 seconds"`) — el límite de 4 s del bound de respuesta, por saturación de CPU. **Corrida aislada** (sin carga): `2 passed in 4.49s`. **Reproducido igual en HEAD** (worktree detached en `7b661b7`, sin mi cambio): 4/4 corridas con los mismos 2 fallos y la misma aserción. El focal U6-8 bajo la misma carga: 3/3 corridas verdes. Worktree temporal removido.
3. **El contrato aprobado aún describe el gate viejo** — `spec.md` §2.2: *"La versión declarada […] sigue siendo `binary_version` de la configuración, con el gate ya existente del preflight"*. La decisión U6-8 lo enmienda. **No toqué el spec aprobado** (no es del implementer): queda para el arquitecto/orquestador la enmienda Δ.
4. **No se tocaron** `tests/`, ni la config, el store, el runtime ni la instalación en HOME (todo el fixture es temporal: `XDG_CONFIG_HOME`/`HOME` redirectados, store y binario desechables, credencial centinela inventada).
5. `binary_version` **sigue** en el vocabulario de la sección y en la correspondencia clave por clave del diagnóstico de sección ausente (el RED lo declara así y `test_pd9_missing_section_diagnostic_names_file_section_and_correspondence` queda verde).