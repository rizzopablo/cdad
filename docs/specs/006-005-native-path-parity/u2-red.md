Focal RED is stable and all declared regressions are green. Here is the role report.

## Role report — test-writer, 006-005-native-path-parity, substage **RED** (unit U2)

### 1. Modified files (write scope `tests/` only)

| File | Change |
|---|---|
| `tests/test_006_005_u2_opencode_module.py` | **new** (1442 lines) — U2 focal RED |

Nothing else was touched: `git status` shows the pre-existing untracked `docs/planning/` and `findings/incremental-construction-and-reproducible-validation-2026-10-17.md` (not mine) and no other modification (`git diff --stat` empty). No A-1 replacement was needed (see §5).

### 2. Test → PD map (19 tests; 11 RED + 8 declared anchors)

| Test | PD | Today |
|---|---|---|
| `TestPd11CredentialReachesTheClientProcess::test_pd11_server_mode_injects_the_resolved_credential_into_the_client_env` | PD-11 (D-ADP-1, INV-11) | RED |
| `…::test_pd11_standalone_injects_nothing` | PD-11 | anchor |
| `TestPd14AgentTravelsInThePacket::test_pd14_run_argv_carries_the_agent_of_the_packet` | PD-14 (D-ADP-4, INV-13) | RED |
| `…::test_pd14_unpublished_packet_agent_fails_closed_before_dispatch` | PD-14 | RED |
| `…::test_pd14_packet_without_agent_uses_the_role_agent_and_declares_it` | PD-14 | RED |
| `TestPd5ExternalCorrelationIsTheChosenSession::test_pd5_external_association_is_the_session_the_module_chose` | PD-5 (externa) | anchor |
| `…::test_pd5_external_accepts_a_directory_inside_the_project_and_elsewhere` | PD-5/INV-15 | anchor |
| `…::test_pd5_foreign_agent_row_is_a_rejection_that_names_the_key` | PD-5 | anchor |
| `TestPd12ExternalDoesNotRequireParentNorDirectory::test_pd12_external_accepts_a_store_without_parent_nor_directory` | PD-12 (externa) | anchor |
| `TestPd12Pd13ObserveSurface::test_pd12_observe_returns_the_correlated_row_of_the_installed_schema` | PD-12 | RED |
| `…::test_pd12_observe_fails_closed_naming_the_absent_column` | PD-12 | RED |
| `…::test_pd13_observe_is_one_read_only_access_and_declares_its_counter` | PD-13 (INV-6) | RED |
| `TestPd10Capabilities::test_pd10_installed_schema_accredits_correlation_and_names_columns` | PD-10 (§2.2/§2.3/O-3) | RED |
| `…::test_pd10_only_agent_store_denies_correlation_naming_the_key` | PD-10/O-3 | RED |
| `…::test_pd10_module_without_the_new_surface_does_not_accredit` | PD-10 (§2.2, ventana O-6) | anchor |
| `TestPd23DerivedArtifactKind::test_pd23_plan_review_kind_materializes_with_identical_sha` | PD-23 (§2.8) | RED |
| `…::test_pd23_test_writer_kind_materializes_with_identical_sha` | PD-23 | RED |
| `…::test_pd23_architect_draft_kind_stays_role_report` | PD-23 | anchor |
| `…::test_pd23_scribe_declares_role_report_and_its_row_is_u7` | PD-23 (§2.8.3; fila del scribe = **U7**, declared dependency, no assertion on materialization) | anchor |

### 3. Exact commands and output

```
$ python3 -m pytest tests/test_006_005_u2_opencode_module.py -q
11 failed, 8 passed in 17.57s
```
The 11 failures, all `AssertionError` about missing behaviour (never ImportError/syntax/fixture error), `--tb=line`:
```
AssertionError: 'blocked' != 'completed'                     # PD-11 server: la credencial no llega al proceso cliente
AssertionError: Regex '\bagent\b' not found …                # PD-14 sin campo: la ausencia no se declara
AssertionError: 'cdad-test-writer' != 'cdad-test-writer-odoo'# PD-14 argv: no sale del paquete
AssertionError: 'completed' != 'blocked'                     # PD-14 agente no publicado: despacha igual
AssertionError: Regex 'agent' not found … unrecognized arguments: --observe # PD-12 fallo cerrado no nombra la columna
AssertionError: 2 != 0 : PD-12: `--observe` must return …    # sin superficie --observe
AssertionError: 2 != 0 : PD-13: `--observe` must complete …  # idem
AssertionError: 2 != 0 : PD-10 …: `--capabilities` must answer # sin superficie --capabilities
AssertionError: 2 != 0 : PD-10 sólo agente … `--capabilities`  # idem
AssertionError: Lists differ: ['role-report'] != ['plan-review']
AssertionError: Lists differ: ['role-report'] != ['test-writer-role-report']
```

```
$ python3 -m pytest tests/test_cdad_adapters_opencode.py tests/test_005_009_t2_opencode_adapter.py \
    tests/test_006_001_t1b_service_mode.py tests/test_006_001_t2_wait_recovery.py \
    tests/test_006_001_t3_concurrency.py tests/test_006_003_u6_server_credential.py \
    tests/test_003_003_t2_preflight.py -q
51 passed in 80.56s

$ python3 -m pytest tests/test_005_007_t4_architect_report_materialization.py \
    tests/test_003_002_t2_materialize.py tests/test_003_002_t2_reviewfix.py \
    tests/test_003_002_t1_receive.py -q
37 passed in 51.46s

$ python3 -m pytest tests/test_006_005_u1a_runtime_config.py tests/test_006_005_u1b_dispatch_entry.py \
    tests/test_006_005_u1c_packet_agent.py -q          # extra: mi fichero no perturba los focales hermanos
37 passed in 57.80s

$ python3 -m pytest tests/test_005_010_t2_load_mode_invocation.py tests/test_005_009_t4_acceptance.py -q
9 passed, 1 skipped in 12.61s                            # extra: el valor del agente que fija 005-010 T2 no cambia (ver §5)
```
No flakiness of the waiter was observed: 4 full runs of the focal file, all `11 failed, 8 passed` in ~17.6 s.

```
$ git commit -m "test: 006-005 U2 RED — modulo OpenCode: credencial al cliente, agente del paquete, \
capabilities/observe acotado, kind derivado (11 RED / 8 anclas declaradas)"
[main 9a260c4] 1 file changed, 1442 insertions(+)
```

### 4. Oracle design (independent, black-box) and measured RED anchor

Fixture: module run **as a process** (`cdad_delegate_opencode.py --project-root R --packet-id P --exec-config C [--capabilities|--observe --session S]`, published `PACKET.md` on stdin); own declarative fake runtime binary (records argv/PWD/`credential_env_present` boolean/session/agent; writes the SQLite store declared by the fixture; `require-credential` refuses the `run` errand without `OPENCODE_PASSWORD`); disposable SQLite stores; `HOME`/`XDG_CONFIG_HOME` redirected in the tempdir and both credential variables stripped from every child; loopback `FakeInfoServer` for `mode: server`; `materialize` from `scripts/cdad_result.py`. Sentinels invented by the file; no host value.

Measured today on HEAD `4ad5d00` (probe, not assumed): the durable `receipt.json` part of a test-writer/`red` dispatch carries `artifact_kind: role-report` and `materialize` answers `rc=2` — *"artifact_kind 'role-report' is not permitted for role 'test-writer'/substage 'red': a kind of another role fails in the closed §7 table"*. That measurement is what makes the two PD-23 RED tests the sharpest oracles of this unit.

### 5. A-1 (regla de tests acoplados): **no hay reemplazo**

Ninguna regresión de la ficha U2 fija (a) la constante `role-report` para todo rol, (b) la falta de credencial en el entorno del cliente, ni (c) el agente `cdad-<rol>` fijo, de modo que este RED **no reformula ningún test**: no se declara test reemplazado ni PD nueva. Verificado: las únicas menciones de la constante del módulo están en `tests/test_005_007_t4_architect_report_materialization.py` (fixture de recibo construido a mano — nunca despacha el módulo) y en este focal; `tests/test_006_003_u6_server_credential.py` fija la **precedencia de resolución** de la credencial (entorno antes que archivo) y no la inyección en el cliente — mi caso positivo usa el archivo como única fuente y mi ancla `standalone` protege esa precedencia; y `tests/test_005_010_t2_load_mode_invocation.py:141` fija el agente de su paquete, que con `stack: None` es `cdad-test-writer` y sigue valiendo tras PD-14 (corrido: verde).

### 6. Declared assumptions/limits (honest)

- **Superficie invocada.** El módulo se invoca como proceso con su argv ya vigente (`--project-root/--packet-id/--destino/--exec-config`, sonda `--help`) más la superficie nueva de §2.2 (`--capabilities`, `--observe`). No usé el staging de la interfaz porque el unit bajo prueba es el módulo y su contrato con la interfaz es `--exec-config` (mecanismo interno declarado en §2.6).
- **`store_reads` en el documento de `--observe`**: PD-13 nombra el contador `store_reads`; el RED lo exige en la salida de `--observe` (≤1) además de la invariante de no-escritura del store. Si el implementer declarara el contador sólo en la procedencia del registro I8 de `record`, el test lo dirá (no se afloja el oráculo en verde).
- **Raíz permitida de `plan-review`**: el oráculo materializa hacia `docs/specs/<feature>/` (misma raíz declarada para `role-report` en §2.8 y usada por U6). Si la tabla de materialización fijara otra raíz para ese kind, el RED lo expondrá en vez de silenciarlo.
- **Lecturas**: no leí código de implementación (`skills/**`). La receta de aislamiento la derivé de los tests existentes (una lectura de `skills/cdad-cycle/references/cli-delegation.md` fue **denegada** por el guard; no la evité por otra vía). Lo que sí ejecuté es el comportamiento del CLI (`--help`, invocaciones, árboles descartables) y el esquema de la versión instalada lo tomé de la sonda V-7 que el orquestador declara en el encargo.
- **Flakiness**: no apareció margen del waiter bajo carga en 4 corridas completas; queda declarada en el docstring del fichero por si el GREEN la encuentra.