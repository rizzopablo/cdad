# Route C validation — PASS (before working)

- Identification block in the dispatch equals the canonical `render --route C` output (byte-identical, verified).
- `validate-request` → rc=0. `validate-packet` → rc=0.
- Full `render` diff vs `PACKET.md` → empty (complete match, not header-only).
- `packet_id`, `execution_id`, contract `path`+`sha256` match `REQUEST.json`; contract sha256 `472bab0c…192672e` matches `docs/specs/017-001-suite-performance/spec.md` on disk.
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture.
- Proceeding on Route C, substage `audit`, inputs/scopes of the packet only. No implementation code read. No test files modified in AUDIT.

---

# FINAL TEXT — `test-audit.md` (AUDIT acotado T1, 017-001-suite-performance)

> Para materializar por el orquestador en `docs/specs/017-001-suite-performance/test-audit.md`. En AUDIT no se altera ningún test y no hay altas de inventario.

- Feature: `017-001-suite-performance` (retoma alcance 013-004). Epic: `epic-017-suite-performance`.
- Packet: `017-001-suite-performance-test-writer-audit-001` (`exec-017-001-suite-performance-001`).
- Contrato: `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e` (cabecera del archivo: "Borrador v3"; el sha fijado por el paquete coincide con el disco; el estado de aprobación es gate del orquestador, no discrepancia de contenido — se deja constancia honesta).
- Plan: `docs/specs/017-001-suite-performance/plan.md` v3, tarea **T1** (`detail: next`).
- Alcance T1: cada intento de `close` conserva sus artefactos actuales y agrega `pytest.xml` + `profile.json` con argv, tiempo del hijo y fases identificadas por intento. Referencias: spec §§4.2–4.3, PC-1 (parte resultados/fases), PC-2, INV-1/INV-6/INV-7. T1 aporta la parte resultados/fases de PC-1 y la conservación de PC-2; **no completa PC-1 ni habilita PC-3** (plan T1).
- Comprobaciones observables T1 (plan): (1) selección sintética → XML+fases corresponden a nodeids/resultados; ausente ≠ duración cero. (2) artefactos+argv recuperables desde el intento reservado; sucesivos intentos no sobrescriben. (3) conserva resultado y registros §4.3 (fallos, skips, interrupciones) según protección existente + carencias. (4) solo-fases no acredita operaciones/base; diagnóstico distingue medición incompleta de rc contractual. (5) el gate sigue con una sola corrida de pytest; la regresión usa entorno sintético, no suite completa real.
- Método: selección por promesa observable (R2 hogar) + contribución respecto de lo existente (PC-1–PC-3). Referencias recuperables: `tests/<módulo>::<test>`. Sin cuota por postcondición/simetría/cobertura. Sin umbrales temporales estrechos como oráculo (spec §4.2; convención 11: duraciones solo como aliveness/consistencia, nunca bound==deadline ni igualdad exacta).

## 1. Inventario y mapeo — `tests/test_008_002_suite_evidence.py` (5/5, Mantener todo)

Módulo de cierre: preservación de intentos, concurrencia de reservas, selección/resultado/skips, interrupciones. **No demuestra la instrumentación nueva** (spec §7: reutilizable, insuficiente para XML/perfil). Todo Mantener exactamente como está; T1 lo reutiliza sin cambios como regresión.

| Test (ref. recuperable) | Disp. | Promesa / PCs que protege | Contribución / qué cubre | Sin este test, el usuario… |
|---|---|---|---|---|
| `test_008_002_suite_evidence.py::test_sequential_attempts_preserve_first_bytes` | Mantener | A / PC-2 (§4.3 reserva+artefactos), INV-1 | Dos `close` secuenciales → 2 intentos; bytes del primero intactos (hashes). Faceta *artefactos actuales*. | …puede perder la evidencia de una corrida anterior al cerrar la siguiente. |
| `::test_simultaneous_attempts_are_independent` | Mantener | A / PC-2 (§4.3 reserva exclusiva), INV-1 | Dos `close` concurrentes → 2 intentos `finished` con stdout/stderr, sin colisión. | …puede perder evidencia por colisión de reservas concurrentes. |
| `::test_attempt_records_selection_result_and_skip_reason` | Mantener | A / PC-2 (§4.3 selección, rc, skips, canario, logs), INV-1 | `attempt.json` conserva schema/state/command/selection/commit/dirty/tiempos/rc/`pytest_summary`/canary/artifacts; skip con motivo completo; logs presentes. | …no puede interpretar ni reproducir el cierre (selección, resultado, motivo de skip). |
| `::test_interrupted_attempt_is_never_success` | Mantener | A / PC-2 (§4.3 interrupciones), INV-6 | Intento interrumpido (SIGKILL) queda `running`/`interrupted`, rc None/≠0; nunca éxito. | …puede confundir una interrupción con un cierre exitoso. |
| `::test_measure_does_not_modify_tree` | Mantener | A (guardia) / INV-2, INV-7 | `measure` no modifica el árbol (hashes antes==después) y devuelve dict. | …puede alterar archivos al medir la suite sin detectarlo. |

Operaciones de sustitución: ninguna (Mantener no sustituye).

## 2. Inventario y mapeo — `tests/test_008_002_suite_selection.py` (25/25, Mantener todo)

Módulo de selección por capacidad/archivo/colección (sintético, sin tocar el checkout real). Para T1 es **regresión de la semántica de selección del §4.3** (la instrumentación no redefine selección ni veredicto). No cubre XML/perfil/argv/fases. Todo Mantener.

| Test | Disp. | Promesa / PCs | Contribución | Sin este test, el usuario… |
|---|---|---|---|---|
| `::test_pc1_validate_ok_with_complete_inventory` | Mantener | A / PC-2 (selección válida aceptada) | Inventario completo → `validate` rc 0. | …no distingue un inventario seleccionable de uno roto. |
| `::test_pc1_validate_rejects_omitted_module` | Mantener | A / PC-2 | Módulo omitido → `validate` ≠0 nombrando `test_c.py`. | …puede cerrar con un módulo silently fuera de la selección. |
| `::test_pc1_validate_rejects_nonexistent_nodeid` | Mantener | A / PC-2 | Nodeid fantasma → ≠0 (`test_ghost`). | …puede acreditar nodeids que no existen. |
| `::test_pc1_validate_rejects_unknown_capability` | Mantener | A / PC-2 | Capacidad desconocida → ≠0 (`teleportation`). | …puede seleccionar por una capacidad inventada. |
| `::test_pc2_list_returns_exact_sorted_unique_selection` | Mantener | A / PC-2 (§4.3 selección) | `list --capability` devuelve selección exacta, ordenada, única. | …no puede confiar en qué va a correr el cierre. |
| `::test_pc2_run_executes_only_selection` | Mantener | A / PC-2 | `run --capability continuity` ejecuta solo a,b (marcadores). | …puede ejecutar fuera de la selección declarada. |
| `::test_pc2_run_propagates_selected_failure` | Mantener | A / PC-2 (rc) | Fallo seleccionado → rc ≠0 y `c` no corre. | …puede ver verde aunque la selección falló. |
| `::test_pc3_validate_rejects_missing_target` | Mantener | A / PC-2 (conservación estructural) | Target fusionado inexistente → ≠0. | …puede perder un destino de fusión sin aviso. |
| `::test_pc3_validate_rejects_disappeared_accredited_obligation` | Mantener | A / PC-2 | Obligación acreditada desaparecida vs HEAD → ≠0. | …puede podar una obligación acreditada. |
| `::test_pc3_validate_rejects_elimination_with_pending_verify` | Mantener | A / PC-2 | Eliminar con `VERIFY` pendiente → ≠0. | …puede eliminar con verificación pendiente. |
| `::test_pc5_surface_selects_uncommitted_test_only_change` | Mantener | A / PC-2 (superficie) | Cambio solo en b → surface corre solo b, rc ≠0. | …paga superficie completa por un cambio puntual. |
| `::test_pc5_surface_base_without_inventory_fails` | Mantener | A / PC-2 | Base sin inventario → ≠0 nombrando inventario/pc-map. | …puede superficializar sin mapa aplicable. |
| `::test_pc5_surface_all_explicit_selects_everything` | Mantener | A / PC-2 | `--all` corre todo (a,b,c) con rc del fallo. | …no tiene escape explícito `--all` cuando lo necesita. |
| `::test_pc7_validate_rejects_missing_timing_disposition` | Mantener | A / PC-2 (guarda timing) | Sin `timing-disposition` → ≠0. | …puede validar sin disposición temporal declarada. |
| `::test_pc7_validate_rejects_resolved_without_evidence` | Mantener | A / PC-2 | `resolved` sin evidencia → ≠0. | …puede dar por resuelto un techo sin evidencia. |
| `::test_pc1_validate_rejects_incomplete_mixed_assignment` | Mantener | A / PC-2 (nodeids mixtos) | Asignación mixta incompleta → ≠0 (`test_m2`). | …puede dejar medio módulo sin capacidad. |
| `::test_pc1_validate_rejects_nonexistent_inventory_nodeid` | Mantener | A / PC-2 | Nodeid fantasma en inventario → ≠0. | …puede inventariar nodeids inexistentes. |
| `::test_pc2_mixed_module_selects_exact_nodeids` | Mantener | A / PC-2 | Módulo mixto lista nodeids exactos por capacidad. | …mezcla capacidades en la selección. |
| `::test_pc3_validate_rejects_committed_disappearance_vs_baseline` | Mantener | A / PC-2 (baseline) | Desaparición comprometida vs baseline → ≠0. | …puede borrar obligación acreditada contra baseline. |
| `::test_pc5_surface_selects_new_untracked_test` | Mantener | A / PC-2 | Test nuevo untracked → surface lo corre (d, no a), rc ≠0. | …no cubre tests nuevos en la superficie. |
| `::test_pc5_surface_deleted_test_selects_declared_substitute` | Mantener | A / PC-2 | Test eliminado → corre sustituto declarado (a). | …pierde cobertura al eliminar un test. |
| `::test_pc5_surface_moved_test_selects_base_map_targets` | Mantener | A / PC-2 | Test movido → surface usa targets del mapa base. | …pierde cobertura al mover un archivo. |
| `::test_pc5_surface_helper_change_selects_declared_consumers` | Mantener | A / PC-2 | Cambio en helper → solo consumidores declarados (b). | …corre de más o de menos ante cambio de helper. |
| `::test_pc5_surface_product_change_selects_surface_assignments` | Mantener | A / PC-2 | Cambio de producto → asignaciones de superficie (c). | …no asocia cambio de producto con su superficie. |
| `::test_pc5_surface_selector_change_selects_everything` | Mantener | A / PC-2 | Cambio del selector → todo (a,b,c). | …puede infraseleccionar tras cambiar el selector. |

## 3. Inventario y mapeo — `tests/test_008_005_ci_gate.py` (11 funciones / 19 ejecuciones, Mantener todo)

Gate como caja negra por CLI (repos sintéticos + CLIs grabadoras). Para T1 es **regresión de §4.3 a nivel gate**: orden, una sola corrida, atribución fail-closed, diagnóstico rojo, hermeticidad, preservación de raíces. No cubre XML/perfil nuevos. Todo Mantener.

| Test | Disp. | Promesa / PCs | Contribución | Sin este test, el usuario… |
|---|---|---|---|---|
| `::test_pc1_un_comando_orden_fijo_y_una_sola_corrida_de_pytest` | Mantener | A / PC-2 (una sola corrida; orden fijo) | Orden `validate-state,surface,doctrine,odoo,close`; `surface --collect-only --base`; un solo `close --all`; `gates[]` refleja orden; sin pytest fuera de close (sentinel). | …paga dos suites por push y no sabe de dónde salió el veredicto. |
| `::test_pc2_atribucion_fail_closed` [8 casos: verde-atribuible, commit-nulo, dirty-no-cero, intento-no-finished, summary-no-verified, cero-intentos, intentos-multiples, close-rc] | Mantener | A / PC-2 (atribución), INV-1 | Verde solo si finished+verified+rc0+commit+dirty0+1 intento; cada causa no atribuible → rojo fail-closed con causa nombrada. | …puede recibir un verde no atribuible como si el commit hubiera pasado. |
| `::test_pc3_rojo_nombra_fallos_y_skips_completos_sin_repetir_suite` | Mantener | A / PC-2 (rojo nombra, skips completos) | Fallos por nodeid con motivo (alpha-boom/gamma-boom), skips con motivo completo incl. 678 chars, un solo close, sin re-ejecución. | …no sabe qué contrato se rompió ni lee skips largos; paga 2ª suite para explicarlo. |
| `::test_pc3_error_de_coleccion_se_nombra_y_referencia_stdout_log` | Mantener | A / PC-2 | ERROR colección sin `::` → nodeid=ruta, reason null + referencia stdout.log, errors==1, un solo close. | …deja un error de colección sin nombrar ni log. |
| `::test_pc4_cambio_solo_documentacion_no_ejecuta_superficie` [docs-only, readme-only] | Mantener | A / PC-2 | Solo-docs → sin paso surface; `change.kind=solo-documentacion`; surface no-aplica con motivo. | …bloquea doc por superficie inaplicable. |
| `::test_pc4_cambio_de_producto_sin_superficie_es_rojo_y_nombra_ruta` | Mantener | A / PC-2 | Producto sin superficie → rojo `surface-rc` nombrando `app/module.py`; close igual corre (D1). | …pasa como verde un producto sin superficie clasificada. |
| `::test_pc5_hermetico_sin_home_sin_red_y_sin_escrituras_fuera` | Mantener | A / PC-2 (hermeticidad) | Con HOME vacío/PATH sin red: rc 0; solo escribe bajo `evidence/`; repo y HOME intactos; sin red; verde. | …sufre gate dependiente de HOME/red o que escribe fuera. |
| `::test_pc7_dos_corridas_dos_raices_y_gate_json_aun_fallando` | Mantener | A / PC-2, INV-1 | Dos corridas → 2 raíces, primera intacta, 1 intento por raíz, schema 1; base inválida → raíz con rojo `base-invalida`, `change.kind=desconocido`, 4 gates siempre no-aplicables con motivo. | …pierde evidencia del push pasado o no puede auditar un fallo pre-close. |
| `::test_pc8_canario_y_carga_visibles_y_no_decisorios` | Mantener | A / PC-2 | Delta canario (0/450) visible en gate.json y reporte + loadavg; nunca cambia rc. | …convierte interferencia/carga en rojo o la deja invisible. |
| `::test_exit2_sin_base_es_error_de_uso_y_no_abre_raiz` | Mantener | A (uso) | Sin `--base` → salida 2 con diagnóstico, sin raíz, sin pasos. | …recibe veredicto sobre base inventada. |
| `::test_exit2_repo_root_archivo_es_error_de_uso` | Mantener | A (uso) | `--repo-root` archivo → salida 2 con diagnóstico. | …corre sobre un árbol inexistente o falla interno. |

## 4. Reutilización por T1 sin cambios

- **No-sobrescritura y reserva** (check 2, faceta artefactos actuales): `test_sequential_attempts_preserve_first_bytes`, `test_simultaneous_attempts_are_independent`, `test_pc7_dos_corridas_dos_raices…`. Se reutilizan tal cual; la carencia es solo la faceta *nuevos artefactos* (XML/perfil del 2º intento no pisan al 1º).
- **Selección/resultado/skips/canario/logs** (checks 3 y 5, faceta actual): `test_attempt_records_selection_result_and_skip_reason`, todo `test_008_002_suite_selection.py`, `test_pc3_*`, `test_pc4_*`. Se reutilizan; la carencia es la *correspondencia de los nuevos artefactos* con esa misma selección/resultado.
- **Fallos/skips/interrupciones** (check 3, faceta actual): `test_interrupted_attempt_is_never_success`, `test_pc3_*`. Se reutilizan; la carencia es la *coherencia XML/perfil bajo esos desenlaces* + no-sustitución del rc.
- **Una sola corrida en el gate** (check 5, faceta orden): `test_pc1_un_comando_orden_fijo…` (orden + un solo `close --all` + sentinel). Se reutiliza; la carencia es la faceta *close instrumentado ejecuta un solo hijo y registra su argv/wall* (nivel attempt, no cubierto por las grabadoras).
- **Higiene**: `test_measure_does_not_modify_tree`, `test_pc5_hermetico…`, `test_pc8_canario…`, `test_exit2_*`. Regresión pura; la instrumentación no debe romperlos.

## 5. Carencias → protección RED propuesta (módulo nuevo `tests/test_017_001_suite_profile.py`, futura disposición Añadir)

Cada propuesta declara postcondiciones y consecuencia ("sin este test, el usuario…"). Un test puede proteger varias postcondiciones (trazabilidad, no cuota). Sin duraciones-bound (conv. 11): solo presencia, correspondencia, monotonía/consistencia gruesa y diagnóstico; jamás umbrales estrechos.

- **C1+R1 — XML y fases corresponden a lo realmente emitido; ausente ≠ cero** (check 1; PC-1 parte resultados/fases, INV-1, INV-6). RED `test_close_emits_xml_and_pha<session>_emitted_selection`: selección sintética conocida (pass+fail+skip) por `close` real → intento con `pytest.xml` + `profile.json` recuperables; testsuite/testcase ↔ nodeids+resultados; `phases[]` ↔ fases emitidas (nodeid/when/outcome); fase no emitida ausente (no fila con `duration_s==0` inventada). *Sin este test, el usuario recibe XML/perfil que nombran otros tests o inventan fases cero y calibra sobre ficción.*
- **C2+R2 — argv y artefactos recuperables desde el intento reservado; sucesivos no sobrescriben lo nuevo** (check 2; PC-1 parte, PC-2 reserva, INV-1). RED `test_attempt_preserves_argv_and_new_artifacts_across_attempts`: `profile.pytest_argv` == argv efectivo del hijo; `pytest.xml`+`profile.json` referenciados desde el intento; 2º close → 2 intentos, hashes del 1º (incl. nuevos) intactos. *Sin este test, el usuario pierde el XML/perfil del primer intento o no puede reconstruir el comando medido.*
- **C3+R3 — conservación de fallos/skips/interrupciones con instrumentación** (check 3; PC-2, INV-6). RED `test_profile_preserves_failures_skips_and_interruptions_without_substituting_rc`: fallo → rc≠0 y XML lo nombra; skip → motivo completo en summary y XML; interrupción → state running/interrupted, rc None/≠0 aunque haya perfil parcial; perfil incompleto nunca convierte rc contractual en éxito. *Sin este test, la instrumentación puede enmascarar un fallo/skip/interrupción o blanquear un rojo contractual.*
- **C4+R4 — diagnóstico distingue medición incompleta de resultado contractual; solo-fases no acredita base** (check 4; PC-1 parte, INV-6). RED `test_incomplete_measurement_is_diagnosed_not_presented_as_contract`: perfil `status:incomplete` + `diagnosis` no vacía ante captura faltante/parcial; rc de pytest intacto; aserción explícita de que fases-sin-operaciones / perfil-incompleto no satisfacen calibración ni base (entrega parcial T1). *Sin este test, el usuario confunde fases parciales con medición válida y consume la base sobre evidencia rota.*
- **C5+R5 — el close instrumentado invoca una sola corrida pytest y registra su pared** (check 5; PC-2 §4.3 sin 2º pytest, INV-7). RED `test_instrumented_close_runs_single_pytest_and_records_wall_argv`: close con selección sintética → exactamente un hijo pytest; `pytest_wall_s` presente y consistente (pared ≥ 0, sin igualdad exacta ni techo); `pytest_argv` fijado, `PYTEST_ADDOPTS`/addopts neutralizados según §4.3; a nivel gate se reutiliza el PC-1 existente (sin duplicarlo). *Sin este test, el gate puede pagar dos suites o acreditar una ruta distinta de la medida.*

Cobertura de la lista del objetivo: XML↔nodeids (R1), ausente≠cero (R1), argv+artefactos desde intento (R2), sucesivos sin sobrescritura —faceta nueva— (R2), fallos/skips/interrupciones —faceta nueva— (R3), diagnóstico incompleto-vs-contractual (R4), una sola pytest —faceta attempt— (R5; faceta gate reutilizada sin duplicar).

## 6. Selección focal (T1)

- RED + GREEN focal (test-writer RED, implementer GREEN): `python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py`
- Regresión proporcional (GREEN): `python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py`
- Gate de integración: reviewer independiente contrasta artefactos+preservación §4.3, revisa evidencia focal y regresión, ejecuta `python3 scripts/cdad-suite.py validate` sobre revisión con deltas materializados; orquestador comprueba alcance/evidencia/hallazgos. **No** ejecutar `scripts/cdad-ci-gate.py` como comprobación rutinaria de T1.
- `deferred-hardening`: nada nuevo desde AUDIT. Rigen los diferimientos de spec §9 (estadística multihost, profiler universal, migración masiva de cachés, recorte de presupuestos por intuición, confinamiento universal, poda/publicación). Cobertura exhaustiva, carga/perf y bordes no exigidos por PC-1(parte)/PC-2 no pertenecen al ciclo de T1.

## 7. Delta de inventario vivo

En AUDIT no hay altas, bajas ni modificaciones: 41 funciones existentes todas **Mantener** (5 evidencia + 25 selección + 11 gate); 0 Extender/Sustituir/Consolidar/Añadir/Retirar materializados. El archivo propuesto `tests/test_017_001_suite_profile.py` (R1–R5) es **propuesta RED futura con disposición prevista Añadir**, no alta de inventario. Incertidumbre: ninguna que obligue a conservar de más — todo lo inventariado se conserva con Mantener.

## 8. Evidencia del rol

- Implementación leída: **ninguna** (aislamiento de fase preservado; oráculo solo desde spec/plan/tests declarados).
- Archivos modificados: **ninguno** (AUDIT no altera tests).
- Comandos exactos ejecutados (solo lectura + ejecución black-box por runner acordado, sin importar producto):
  - `python3 scripts/cdad_packet.py validate-request --request .cdad/packets/017-001-suite-performance-test-writer-audit-001/REQUEST.json --project-root <repo> --execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json` → rc=0
  - `python3 scripts/cdad_packet.py validate-packet --request … --packet .cdad/packets/017-001-suite-performance-test-writer-audit-001/PACKET.md --project-root … --execution-context …` → rc=0
  - `python3 -m pytest -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_evidence.py -q` → **5 passed in 4.35s**
  - `python3 -m pytest -rs -o addopts= -p no:cacheprovider tests/test_008_005_ci_gate.py -q` → **19 passed in 10.98s** (11 funciones, 8+2 parametrizadas)
  - `python3 -m pytest -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_selection.py -q` → **25 passed in 31.28s**
  - Suite completa **no realizada** (ciclo focal; sin autorización para completa; límites: solo los 3 módulos de regresión T1).
- Commit: **ninguno** (AUDIT no produce diff; informe como FINAL TEXT para materialización del orquestador).
