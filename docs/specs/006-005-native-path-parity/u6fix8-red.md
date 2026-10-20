The RED is committed. Here is the role report.

---

# Role report — test-writer / RED — 006-005 U6-8

**Packet:** `006-005-native-path-parity-test-writer-red-022` · **substage:** `red` · **execution:** `exec-006-005-native-path-parity-001`
**Contract:** `docs/specs/006-005-native-path-parity/spec.md` (sha256 `3a824be3…`, approved) + `docs/epics/epic-006-opencode-concurrency/execution.md` §hallazgo **U6-8** (decisión del owner).

## 1. Qué se midió antes de escribir (sonda black-box, sin leer implementación)

La entrada y el módulo se invocaron **como proceso** (nunca importados, nunca leídos) contra un fixture desechable, para saber qué falla hoy y por qué:

| Escenario | Comportamiento **medido** hoy |
|---|---|
| `binary_version` configurada `2.0.0`, cliente observado `3.1.4` == servidor observado `3.1.4` | **`blocked`**: `server version '3.1.4' does not match the configured 'binary_version' '2.0.0'` — **el defecto U6-8** |
| sección **sin** `binary_version` | `completed` (el gate no compara) |
| cliente observado `3.1.4` ≠ servidor observado `9.9.9` | `blocked` nombrando **las dos** versiones, **sin** lanzar `run` |
| store sin `session_v2.agent` (columna que la correlación evalúa) | `blocked` nombrando la columna (`missing session_v2.agent`) |
| `migrate` desde un exec-config heredado | **escribe** `binary_version` en la sección |
| `capabilities --runtime opencode` | `version` = la **observada** (`unknown` sólo si el store no existe) |

## 2. Archivos

| Archivo | Acción |
|---|---|
| `tests/test_006_005_u6fix8_version_by_observation.py` | **nuevo** (781 líneas) — RED U6-8 |
| `tests/test_006_005_u1a_runtime_config.py` | **modificado** — reformulación A-1 (3 tests) |

Nada fuera de `tests/`. `docs/.cdad-state.json` (orquestador: paquete `dispatched`), `docs/planning/` y `findings/` quedan intactos y sin commitear.

## 3. Mapa test → PD (docstrings «PD-10/E5 (U6-8)»)

| Test (nuevo) | Postcondición | Hoy |
|---|---|---|
| `test_u68_configured_version_difference_does_not_block_the_dispatch` | **PD-10/E5 (U6-8)** — `binary_version` configurada ≠ observada, cliente == servidor, store con columnas ⇒ **no bloquea**, el encargo se lanza, entrega, y la diferencia se **declara** (diagnóstico o procedencia) con el valor configurado | **RED** (`blocked` != `completed`) |
| `test_u68_dispatch_without_configured_version_proceeds_and_capabilities_report_the_observed_one` | **PD-10/E5 (U6-8)** — sin `binary_version`: despacho normal y `capabilities` informa la versión **observada** | GUARD verde (conservado) |
| `test_u68_observed_client_and_server_versions_that_differ_fail_closed_naming_both` | **PD-10/E5 (U6-8) + PD-12** — cliente ≠ servidor observados ⇒ fail-closed **antes de lanzar**, nombrando las dos | GUARD verde (conservado) |
| `test_u68_store_without_a_correlation_column_fails_closed_naming_the_column` | **PD-10/E5 (U6-8) + PD-12** — store sin la columna que la correlación evalúa ⇒ fail-closed nombrándola (aunque la versión coincida) | GUARD verde (conservado) |
| `test_u68_migrate_does_not_write_the_configured_version` | **PD-10/E5 (U6-8) + PD-25/§2.6.1** — `migrate` no escribe `binary_version` | **RED** (la sección migrada lo contiene) |

Fixture (declarado en el docstring): `skills/cdad-cycle` **staged** ⇒ el **módulo real** `cdad_delegate_opencode.py` es el que resuelve la sección `opencode`; `runtimes.json` bajo `XDG_CONFIG_HOME`/`HOME` temporales; binario falso que reporta la **versión de cliente configurable** (`--version`) y registra cada invocación; servidor falso `/api/info` que reporta la **versión de servidor configurable** (la superficie que el preflight ya lee); store descartable con la **forma real V-7** (`id, parent_id, agent, model, time_created INTEGER ms, time_idle, idle_outcome, directory` + tabla de mensajes). **Sin valores del host** (credencial, versiones, store, binario y rutas son del tempdir; el agente derivado se publica por adopción, precedente 006-005 U3).

## 4. A-1 — reformulaciones (test reemplazado · PD enmendada · razón)

**Reformulados en `tests/test_006_005_u1a_runtime_config.py`** (los que fijaban el comportamiento viejo: la migración **cargando** `binary_version`):

| Test reemplazado | PD enmendada | Razón |
|---|---|---|
| `test_pd9_derived_section_is_inspected_key_by_key` | PD-25/§2.6.1 — la sección se inspecciona clave por clave **para las claves que la migración escribe**; `binary_version` no es una de ellas | Decisión del owner U6-8: la versión se **observa**; una diferencia con la configurada se declara y **no bloquea**; `migrate` deja de escribirla |
| `test_pd25_migrate_without_section_writes_the_section_key_by_key` | ídem (PD-25/§2.6.1) | ídem |
| `test_pd25_migrate_dry_run_does_not_write` | ídem: la sección que `--dry-run` anuncia es la que **se escribiría** — sin versión | ídem |

Mecánica: nueva constante `MIGRATED_SECTION_KEYS` (= `SECTION_KEYS` sin `binary_version`), `assert_section_key_by_key` exige las claves migradas y **prohíbe** `binary_version` en la sección migrada, y el `--dry-run` no puede anunciar el valor de la versión heredada. El bloque A-1 (test reemplazado, PD enmendada, razón) está en el docstring del módulo y en el de cada test.

**Búsqueda y resultado (medido, `grep -rln "binary_version" tests/`)** — 12 ficheros:
- **Reformulado**: `tests/test_006_005_u1a_runtime_config.py` (los 3 de arriba).
- **Conservados** (fijan la versión **observada**, o un módulo stub, o un sondeo honesto `… --version`; ninguno fija un bloqueo por `binary_version` distinto del observado): `test_005_009_t2_opencode_adapter.py:1096`, `test_005_010_t4_integration.py:334`, `test_006_001_reviewfix.py:420`, `test_006_001_t3_concurrency.py:404`, `test_006_001_t3_integration.py:444`, `test_006_005_u1b_dispatch_entry.py:612` (módulo stub), `test_006_005_u2_opencode_module.py:522,1330`, `test_006_005_u6fix1_capabilities_entry.py:377`, `test_006_005_u6fix4_native_selection.py:401`, `test_006_005_u6fix5_write_ahead.py:591`, `test_006_005_u6fix6_model_parity.py:286`.
- **006-003**: `grep` no encuentra `binary_version` en `tests/test_006_003_*.py` ⇒ nada que reformular; su comparación cliente/servidor (`test_006_003_u6_server_credential.py:103`, `SERVER_BODY` con el semver coincidente) queda **conservada**. Igual en 006-001 (`test_pd2_version_mismatch_names_both_versions`) y 005-010 (`test_005_010_t2_load_mode_invocation.py`): **cliente contra servidor se conserva**.

## 5. Comandos y salida

```
$ python3 -m pytest tests/test_006_005_u6fix8_version_by_observation.py -v
FAILED …::test_u68_configured_version_difference_does_not_block_the_dispatch
FAILED …::test_u68_migrate_does_not_write_the_configured_version
2 failed, 3 passed in 8.72s
```
Fallo (a) — asercion sobre la conducta ausente, no import/sintaxis:
```
AssertionError: 'blocked' != 'completed'
 : … una `binary_version` CONFIGURADA distinta de la OBSERVADA no bloquea el despacho … la terminación es 'blocked'
   (diagnóstico: "server version '3.1.4' does not match the configured `binary_version` '2.0.0': …")
```
Fallo (e):
```
AssertionError: 'binary_version' unexpectedly found in {… 'binary_version': 'opencode u6fix8 2.0.0' …}
 : PD-10/E5 (U6-8)/PD-25/§2.6.1: la migración NO escribe `binary_version` …
```

```
$ python3 -m pytest tests/test_006_005_u1a_runtime_config.py -v
FAILED …::test_pd9_derived_section_is_inspected_key_by_key
FAILED …::test_pd25_migrate_dry_run_does_not_write
FAILED …::test_pd25_migrate_without_section_writes_the_section_key_by_key
3 failed, 16 passed in 33.16s
```
(las 3 reformuladas fallan por la clave `binary_version` que la migración sigue escribiendo; las otras 16 U1a siguen verdes)

```
$ python3 -m pytest tests/test_006_005_u1a_…u1b_…u1c_…u2_…u3_…u3b_…u4_…u5_.py
3 failed, 84 passed in 88.55s
$ python3 -m pytest tests/test_006_005_u6fix1…u6fix8…u7_scribe_role_report.py
2 failed, 50 passed in 61.74s
$ python3 -m pytest tests/test_006_003_u2_installer_without_profiles.py \
    tests/test_005_004_t2_installer_claims.py tests/test_006_003_u7_prune_obsolete.py \
    tests/test_install_review5_regressions.py tests/test_006_003_rf_review_fixes.py \
    tests/test_006_003_rf2_review_fixes.py
37 passed in 364.16s
$ python3 -m pytest tests/test_006_001_t1_selection.py tests/test_006_001_t3_concurrency.py tests/test_006_001_reviewfix.py
24 passed in 48.66s
$ python3 -m pytest tests/test_005_009_t2_opencode_adapter.py tests/test_005_009_t1_interface.py
12 passed in 23.66s
$ python3 -m pytest tests/test_005_010_t2_load_mode_invocation.py tests/test_006_003_u6_server_credential.py
13 passed in 20.94s
$ ruff check tests/test_006_005_u6fix8_version_by_observation.py tests/test_006_005_u1a_runtime_config.py
All checks passed!
```
Suite completa: **no** ejecutada (política declarada: la corre quien cierra, una vez).

## 6. Commit

```
$ git add tests/test_006_005_u6fix8_version_by_observation.py tests/test_006_005_u1a_runtime_config.py
$ git commit -m "test: 006-005 U6-8 RED — version por observacion, no por config"
c6e61aa test: 006-005 U6-8 RED — version por observacion, no por config
 tests/test_006_005_u1a_runtime_config.py           |  91 ++-
 …/test_006_005_u6fix8_version_by_observation.py     | 781 +++++++++++++++++++++
 2 files changed, 865 insertions(+), 7 deletions(-)
```
Sólo `tests/`; sin `--no-verify`, sin `git stash`, sin push.

## 7. Límites declarados

- **No se leyó implementación**: la entrada y el módulo se invocaron sólo como proceso (código de salida, sobre JSON, registro I8, log del binario falso, `runtimes.json` escrito). No se abrió `skills/cdad-cycle/scripts/`.
- El binario falso reporta la **versión de cliente** y el servidor falso `/api/info` la **versión de servidor**: son las dos superficies que el preflight ya usa (medido) — no se inventa un canal nuevo.
- Los 3 tests marcados GUARD están verdes hoy: la decisión del owner los **conserva**; Becomguards para que el GREEN no sobre-corrija (p. ej. eliminar la comparación cliente/servidor).
- La **suite completa** no se corrió (la corre quien cierra).