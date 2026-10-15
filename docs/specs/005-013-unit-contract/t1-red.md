## Role report — test-writer / RED · T1 de 005-013-unit-contract

### (a) Tests y su mapeo a PD/AC

Focal: `tests/test_005_013_t1_unit_projection.py` — 15 casos (14 rojos por aserción + 1 control declarado).

| Test | PD / AC | Afirmación observable |
|---|---|---|
| `test_pd1_pd4_projection_locates_unit_and_pins_digest` | PD-1, PD-4 / AC-1, AC-3 | Se publica `.cdad/packets/<packet_id>/UNIT-CONTRACT.md`; la parte `unit` es encabezado de la tabla (fila + separador) + la fila de la unidad, verbatim; las filas de otras unidades se remueven; una sección compartida es parte `shared` (clase en el origen); `sha256(UNIT-CONTRACT.md) == contract.sha256 == active_packet.contract_sha256`; `kind=approved-unit-contract`, `commit=null` |
| `test_pd1_locator_accepts_plain_link_and_backtick_cells[texto-plano\|enlace\|backticks]` | PD-1 / AC-1 | La celda de la unidad como TEXTO PLANO, ENLACE `[<ID> — <título>](<ruta>)` y entre BACKTICKS localiza la MISMA fila (sin igualdad exacta de celda) y el pin es coherente |
| `test_pd1_inv10_locator_ignores_section_titles` | PD-1 / INV-10 | Con la tabla en una sección titulada distinto (sin «Entregas») y con tabla señuelo, la unidad se sigue localizando |
| `test_pd12_origin_records_unit_plan_sha_approver_and_policy` | PD-12 / AC-8 | El origen registra `unit`, `plan`, sha del plan al generar, `approved_by` de la entrada `epic-plan` y `policy_sha256` |
| `test_pd2_fallback_when_no_row_contains_the_feature_id` | PD-2 / AC-2 | Cero filas → rc=0, sin `UNIT-CONTRACT.md`, `contract = approved-epic-plan + docs/epics/<epic>/plan.md + sha del plan`, `stdout == PACKET.md == render`, motivo con la ruta del plan en stderr, `status.unit_contract.mode == "fallback"` + `reason` |
| `test_pd2_fallback_when_two_rows_contain_the_feature_id` | PD-2 / AC-2 | Más de una fila con el id → mismo fallback declarado |
| `test_pd3_history_excluded_and_authorization_included_as_shared` | PD-3 | Historia («Cambios al plan») excluida (título y cuerpo ausentes); autorización («Autoridad») incluida verbatim como parte `shared` |
| `test_pd3_plan_without_anchors_is_conservative_and_not_closed` | PD-3 (b)+(c) / AC-2 | Sin anclas: todas las secciones son `shared`, unidad localizada, rc=0, y ninguna sección produce `impeded` |
| `test_b14_three_plan_forms_locator_and_coherent_pin[forma-epic\|forma-plantilla-producto\|forma-anonima]` | PD-1, PD-2 / AC-9 (B1.4) | Las tres formas (epic; plantilla del producto; fixture sintético anónimo con celda enlace y sin historia/autoridad): unidad localizada, rc=0, pin coherente |
| `test_pd6_receive_and_resume_against_the_received_contract` | PD-6 / AC-4 | Paquete despachado + unidad futura independiente agregada al plan (y registrada en historia) → `receive` rc=0 con `packet_validation`/`identity_validation` `passed`, `semantic_status: pending`, sin `contract_sha256` en el recibo; `--resume-packet` re-emite byte a byte |
| `test_pd6_control_receive_does_not_approve_and_status_is_read_only` | PD-6 / PD-11 (CONTROL) | Recibir no aprueba (`pending`) y no escribe el state; dos `status` consecutivos dejan el proyecto byte a byte idéntico y sin `.impact.json` |

### (b) Archivos creados/modificados

- **Creado:** `tests/test_005_013_t1_unit_projection.py` (1016 líneas). Único path tocado; dentro del `write_scope` (`tests`).
- **No tocado:** `skills/**`, `docs/cdad-policy.json`, el esquema del recibo, tests de otras features. `docs/.cdad-state.json` ya estaba modificado en el árbol por el orquestador: **no lo stageé ni lo commiteé**.

### (c) Comando exacto y salida completa del focal

```
$ python3 -m pytest tests/test_005_013_t1_unit_projection.py -q --tb=line
FFFFFFFFFFFFFF.                                                          [100%]
=================================== FAILURES ===================================
…/tests/test_005_013_t1_unit_projection.py:507: AssertionError: PD-4 violada: `prepare` del architect debe publicar la proyección de unidad en .cdad/packets/999-001-fixture-unit-architect-discovery-001/UNIT-CONTRACT.md; no existe (hoy el contrato sigue siendo el plan completo)
   [× 6 líneas idénticas — test_pd1_pd4, test_pd1_locator[3 formas], test_pd1_inv10, test_pd12, test_pd3_history, test_pd3_sin_anclas, test_b14×3 → misma prima de proyección ausente]
…:741: AssertionError: PD-2 violada: el motivo del fallback debe informarse en el diagnóstico (stderr) nombrando la ruta del plan ('docs/epics/epic-999-fixture/plan.md'): 'CDAD prepare: OpenCode agents source directory not found; …'
…:780: AssertionError: PD-2 violada: el motivo (más de una fila, con la ruta del plan) debe informarse en stderr: 'CDAD prepare: OpenCode agents source directory not found; …'
…:947: AssertionError: PD-6 violada: `receive` de un paquete despachado debe validar contra el contrato REGISTRADO (la proyección durable), no contra el plan vivo: agregar una unidad futura independiente no lo invalida. rc=2 stdout='' stderr='ERROR: contract sha256 does not match exact content\n'
=================================== short test summary info ===================================
FAILED tests/test_005_013_t1_unit_projection.py::test_pd1_pd4_projection_locates_unit_and_pins_digest
FAILED tests/test_005_013_t1_unit_projection.py::test_pd1_locator_accepts_plain_link_and_backtick_cells[texto-plano]
FAILED tests/test_005_013_t1_unit_projection.py::test_pd1_locator_accepts_plain_link_and_backtick_cells[enlace]
FAILED tests/test_005_013_t1_unit_projection.py::test_pd1_locator_accepts_plain_link_and_backtick_cells[backticks]
FAILED tests/test_005_013_t1_unit_projection.py::test_pd1_inv10_locator_ignores_section_titles
FAILED tests/test_005_013_t1_unit_projection.py::test_pd12_origin_records_unit_plan_sha_approver_and_policy
FAILED tests/test_005_013_t1_unit_projection.py::test_pd2_fallback_when_no_row_contains_the_feature_id
FAILED tests/test_005_013_t1_unit_projection.py::test_pd2_fallback_when_two_rows_contain_the_feature_id
FAILED tests/test_005_013_t1_unit_projection.py::test_pd3_history_excluded_and_authorization_included_as_shared
FAILED tests/test_005_013_t1_unit_projection.py::test_pd3_plan_without_anchors_is_conservative_and_not_closed
FAILED tests/test_005_013_t1_unit_projection.py::test_b14_three_plan_forms_locator_and_coherent_pin[forma-epic]
FAILED tests/test_005_013_t1_unit_projection.py::test_b14_three_plan_forms_locator_and_coherent_pin[forma-plantilla-producto]
FAILED tests/test_005_013_t1_unit_projection.py::test_b14_three_plan_forms_locator_and_coherent_pin[forma-anonima]
FAILED tests/test_005_013_t1_unit_projection.py::test_pd6_receive_and_resume_against_the_received_contract
14 failed, 1 passed in 5.48s
```

Salida cruda completa (33 líneas, sin abreviar) en `/tmp/opencode/red_run.txt`. Chequeo mecánico del tipo de fallo sobre esa salida: `grep -cE "ImportError|JSONDecodeError|SyntaxError|Traceback|AttributeError|ModuleNotFound|unrecognized|invalid choice"` → **0**; las 14 fallas son `AssertionError` de contrato (el `.` es el control declarado).

Las precondiciones del fixture (política, plan, autoridad, state con `epic_history` `epic-plan` + `approved_by` y HITL activa; `prepare` rc=0; `--record-dispatch` → `dispatched`) **se cumplen hoy**: por eso los fallos ocurren en la aserción del contrato y no en el armado del fixture.

### (d) Commit

```
9785423 test: 005-013 T1 RED — focal de la proyección de unidad (PD-1..PD-6, PD-12)
 tests/test_005_013_t1_unit_projection.py | 1016 ++++++++++++++++++++++++++++++
 1 file changed, 1016 insertions(+)
```
Rama `codex/epic-005-real-operation`; sin `--no-verify`, sin push, sin despliegue.

### (e) Puntos donde me detuve / declaraciones honestas

1. **No me detuve por el contrato:** cada punto de la consigna pudo escribirse sin leer implementación y sin fabricar state inválido. El RED confirma el hecho declarado por la spec §1 (`receive` falla con `contract sha256 does not match exact content` contra el plan vivo tras agregar la unidad futura).
2. **Alcance de lectura:** leí el contrato aprobado (`spec.md`, `plan.md`) y `tests/**` (patrones de fixture: `test_004_002_t2_bootstrap.py`, `test_005_007_t3_open_unit.py`, `test_005_007_t4_architect_report_materialization.py`, `test_003_002_t1_receive.py`, `test_packet_prepare.py`). **No leí código de implementación.** Única excepción declarada: `ls -la` (solo metadatos de tamaño/tipo) sobre `scripts/cdad_packet.py`, `scripts/cdad_result.py` y `skills/cdad-cycle/scripts/cdad_packet.py` para localizar el entrypoint correcto — sin leer contenido.
3. **Dos decisiones de oráculo que conviene que el reviewer conozca** (derivadas del texto del contrato, no de la implementación):
   - la parte `unit` se verifica por **aparición contigua** de `encabezado\nseparador\nfila\n` y por **conteo == 1** de la fila (el conteo es lo que verifica que la tabla se removió de la sección compartida; el contrato §2.1 define la traza del localizador como «el encabezado de la tabla usada y el título de la sección», por eso NO se cuenta el encabezado —aparecería dos veces si la traza lo cita— sino la fila de cuerpo);
   - el bloque de origen se lee como el texto **anterior** a la parte `unit` (orden de bloques declarado en §2.1: origen → unit → shared).
4. **Control que pasa hoy:** `test_pd6_control_...` (neutralidad: recibir no aprueba; `status` de solo lectura) — pasa hoy y debe seguir pasando; declarado en el docstring. No se declara rojo.
5. **`status` en T1:** PD-2 exige que `status` informe el fallback (`mode: "fallback"` + `reason`), así que los dos casos de fallback lo afirman; no se afirman campos del bloque que la spec deja a T2 (veredicto, `changed_parts`).
6. **Anonimización:** fixtures sintéticos (`epic-999-fixture`, `999-00x-fixture-*`), tempdirs con `HOME` aislado, sin rutas absolutas del dueño ni ids de sesión reales; la sesión del documento de observación es el placeholder `ses-fixture-0001`.
7. **No corrí la suite completa** (política: la corre una vez quien cierra) ni las regresiones declaradas — el focal es lo único que el RED exige y solo agregué un archivo de tests.
