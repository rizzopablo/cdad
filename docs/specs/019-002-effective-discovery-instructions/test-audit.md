# AUDIT — 019-002-effective-discovery-instructions (test-writer, audit)

**Alcance:** solo `tests/` y el spec. No leí código de implementación y no edité ningún test. No corrí `scripts/cdad-suite.py validate`. El encargo dice que no condicione la auditoría a él.

## 0. Intake

- **Ruta C.** Validé el paquete contra su render canónico con `validate-request` y `validate-packet`. Ambos dieron rc=0.
- **Contrato.** El sha256 de `docs/specs/019-002-effective-discovery-instructions/spec.md` coincide con el del paquete (`5cca6fa6…eb0`).
- **Alcance de la auditoría.** Las promesas ejecutables son PC-5, PC-6 y PC-7. PC-1 a PC-4 y PC-8 a PC-11 son de revisión contextual u observación, y no entran aquí.

## 1. Dónde está la protección hoy (referencias recuperables)

| Promesa | Verificadores existentes |
|---|---|
| PC-5, eje rol y tabla cerrada | `test_006_005_u7_scribe_role_report.py`. `TestPd26RoleAxisStaysClosed` (≈l.690-715) rechaza `role-report` para cinco combinaciones, entre ellas `("architect","brainstorm")`. |
| PC-5, derivación nativa del kind | `test_006_005_u1b_dispatch_entry.py::TestPd23NativeDescriptorKind`. Cubre test-writer/red y architect/draft, pero no architect/brainstorm. |
| PC-5, derivación del adaptador OpenCode | `test_006_005_u2_opencode_module.py::TestPd23DerivedArtifactKind`. La tabla `EXPECTED_KINDS` no incluye architect/brainstorm. |
| PC-5, kinds del architect en `draft` | `test_005_007_t4_architect_report_materialization.py`. Protege `architect-spec-draft` y `architect-plan-draft` en `draft`, y el rechazo de kinds de otros roles. |
| PC-5, brainstorm sin otra relación | `test_006_004_u3_principle_single_source.py` y `test_role_packet_render.py` solo listan `("architect","brainstorm")` como combinación de render. No dicen nada sobre kinds. |
| PC-6, paquetes congelados | `test_015_001_frozen_reception.py`: A1 (publicación congelada), A2 y A2b (el sucesor captura lo vigente), B1 (render byte-idéntico tras mutar fuentes vivas), B2, C1, C2, D1 y D2. |
| PC-6, render de paquetes | `test_role_packet_render.py` y `test_003_002_t1_receive.py`. |
| PC-7, cierre | `test_005_012_t3_closure_dispatch_resolution.py::test_pd9_closure_applied_records_evidence_and_rests` (l.626) y su variante B1 (l.858) afirman `current_stage == "idle"` tras el cierre. `test_005_014_closure_replay.py` cubre el replay y el rechazo de un cierre posterior. `test_007_008_receipt_next_action.py` cubre la acción canónica del cierre. |
| PC-7, coherencia de reposo | `test_005_001_t3_idle.py`, PD-12 a PD-15. Cubre el reposo legítimo y los estados incoherentes en `validate-state`. No tiene ningún caso con `done`/`null`. |
| PC-7, status y apertura | `test_005_003_f2_idle_history.py` y `test_007_001_unambiguous_entry.py::test_closed_execution_is_history`. Parten de un reposo `idle`/`null` armado a mano y esperan `open-unit` o `next-unit`. `test_005_007_t3_open_unit.py` y `test_005_012_t6_open_context_guard.py` cubren la apertura. |
| PC-7, distinciones de status | `test_007_001_unambiguous_entry.py`, matriz de situaciones. `test_007_007_suspend_resume_units.py` cubre las unidades suspendidas. |

## 2. Disposición por test

Cada test recibe una sola disposición.

| Test o módulo | Disposición | Promesa, postcondiciones y contribución |
|---|---|---|
| `test_006_005_u7…::TestPd26RoleAxisStaysClosed::test_pd26_role_axis_role_report_of_other_roles_stays_rejected` | **Extender**: quitar solo la tupla `("architect","brainstorm")` de `cases`. | PC-5 cambia esa expectativa, que ahora es obsoleta. El cambio se declara de forma deliberada y se registra el motivo: el spec 019-002 PC-5 admite `role-report` en architect/brainstorm. Las otras cuatro combinaciones (test-writer/red, test-writer/audit, implementer/green, reviewer/review) siguen protegidas, como exige el spec. |
| Resto de `test_006_005_u7…` (`TestPd26…`, `R3_CROSSINGS`, Memory Bank) | **Mantener** | Protegen la clausura rol↔kind y las raíces permitidas. R3 sigue vigente, no depende del cambio. |
| `test_006_005_u1b::TestPd23NativeDescriptorKind` | **Mantener** | Control de que la derivación sin cambios sigue igual para test-writer/red y architect/draft. El hueco de brainstorm lo cubre un test nuevo (§3). |
| `test_006_005_u2::TestPd23DerivedArtifactKind` (4 tests) | **Mantener** | Control de que la derivación del adaptador sigue igual para plan-review, test-writer/red, architect/draft y scribe/memory. |
| `test_005_007_t4_architect_report_materialization.py` | **Mantener** | Protege el contrato de `draft`: kinds vigentes y rechazo de kinds de otros roles. PC-5 no los toca. |
| `test_006_004_u3_principle_single_source.py` y `test_role_packet_render.py` | **Mantener** | Solo listan brainstorm como combinación de render. |
| `test_015_001_frozen_reception.py` (A1, A2, A2b, B1, B2, C1, C2, D1, D2) | **Mantener** | PC-6: congelado byte-idéntico, la publicación nueva captura los bytes cambiados, y los paquetes históricos se conservan. El spec pide "reuse/extend". No encontré una diferencia de protección que justifique tests nuevos. Si una lectura más fina de A2 y B1 mostrara que no mutan una instrucción de rol, el motivo para extender saldría de ahí. Ante la duda se mantiene. |
| `test_005_012_t3…` (cierre, PD-9 y PD-21) | **Mantener** | PC-7, mitad de cierre: el cierre deja `idle`/`null`. Es el control de que no se rompe. |
| `test_005_014_closure_replay.py` | **Mantener** | Replay de cierre y rechazo de un cierre posterior. |
| `test_007_008_receipt_next_action.py` | **Mantener** | Acción canónica del cierre. |
| `test_005_001_t3_idle.py` | **Mantener** | `validate-state` con reposo legítimo e incoherente. Es el criterio contra el que PC-7 alinea a `status`. |
| `test_005_003_f2_idle_history.py` y `test_007_001…::test_closed_execution_is_history` | **Mantener** | Reposo `idle`/`null` hecho a mano → `at-rest` y `open-unit`. PC-7 exige que ese comportamiento siga igual. |
| `test_005_007_t3_open_unit.py` y `test_005_012_t6_open_context_guard.py` | **Mantener** | Apertura con la coherencia existente. |
| `test_007_001` (matriz y distinciones), `test_007_007` (unidades suspendidas) | **Mantener** | Control de las distinciones active/suspended/pending y de los límites de salida de `status`. |
| Retirar / Consolidar / Sustituir | Ninguno | No hay obligación aprobada que se elimine, ni sustituto físico candidato. No habrá POST-AUDIT por esta vía. |

## 3. Huecos y tests propuestos (Añadir)

Los tests se eligen por promesa observable (R2), sin cuota por postcondición.

**N1: PC-5, entrega única de consulta.** Un test nuevo, en un archivo nuevo o en uno colocado junto a los de PC-5.
- **Qué hace.** En fixtures desechables recorre tres cosas:
  - La derivación nativa del kind para architect/brainstorm. Debe dar `role-report`, sin los kinds de borrador.
  - La derivación del adaptador OpenCode. Debe dar el mismo kind.
  - `materialize` de un `role-report` en architect/brainstorm. Debe aceptarlo con sha idéntico dentro de `docs/specs/<feature>/`.
- **Rechazo.** `architect-spec-draft` y `architect-plan-draft` en brainstorm se rechazan, sin escribir target ni cambiar state o receipt.
- **Control.** architect/draft sigue aceptando sus kinds de siempre.
- **Postcondiciones.** PC-5 completo.
- **Contribución.** Hoy brainstorm se ve solo como un rechazo fijo, y nada exige que se acepte. Ninguno de los tests existentes verifica la derivación para brainstorm.
- **Si falta.** Un architect de brainstorm devuelve la consulta técnica y la materialización falla o se rechaza. El flujo "dialogar → consultar → registrar" no se completa.
- **RED esperado.** El `role-report` de brainstorm se rechaza hoy, por aserción. No debe fallar por import.

**N2: PC-7, closure → status → open-unit.** Un test nuevo, de caja negra, sin leer el productor.
- **Camino correcto.**
  1. Se cierra una feature por la vía real (`register-transition --transition closure`).
  2. `status` debe recomendar `open-unit`.
  3. `open-unit` debe tener éxito sobre la siguiente unidad en cola.
- **Camino incoherente.**
  1. Un fixture con `current_stage: "done"` y `active_feature: null`.
  2. `status` da diagnóstico. No recomienda `open-unit` ni declara que esté en reposo.
  3. `status` deja `docs/.cdad-state.json` byte a byte igual.
- **Postcondiciones.** PC-7, incluidas las distinciones activa/suspendida/pendiente.
- **Contribución.** Hoy no hay ningún test con `done`/`null`. Los de reposo siempre arman `idle`/`null` a mano, y ninguno encadena cierre real, status y apertura.
- **Si falta.** Un estado `done`/`null` lleva al usuario a un `open-unit` que luego falla. Es la brecha que el spec describe.
- **RED esperado.** El caso incoherente falla por aserción, porque hoy `status` no diagnostica ese estado.
- **Nota.** Si N2 deja de ser distinto de los tests de PC-7 existentes tras la implementación, que el orquestador lo registre como reutilización.

**PC-6.** No propongo test nuevo. Nada identifica una protección faltante. Es una decisión de reutilización, no un hueco.

## 4. Inventario y mapas (no se editan en esta fase)

- **`suite-inventory.json`.** Para N1 y N2, el reentry necesita un delta con nodeid, capability, contract y provenance.
- **`pc-map.json`.** Se necesita un delta de mapa si la Extender de `test_006_005_u7…` cambia el origen o el destino de un mapeo.
- **Integridad.** `python3 scripts/cdad-suite.py validate`. No lo corrí en esta fase.
- **Estado de los archivos.** No hay archivos tocados.

## 5. Evidencia y límites

- **Comandos ejecutados.** `validate-request`, `validate-packet`, `sha256sum` del spec y lecturas de tests con `grep` y `sed`. Todos con rc=0.
- **Archivos modificados:** ninguno. **Commit:** ninguno. Es una auditoría sin cambios.
- **Límites.** No leí el cuerpo completo de `test_015_001`, ni el de A2 y B1. La disposición de PC-6 es Mantener por conservadurismo. No corrí la suite.
- **Sin gates.** No bloqué la auditoría por `validate`, como pidió el encargo.

## 6. Aprobación solicitada

1. Extender `test_006_005_u7…::test_pd26_role_axis_role_report_of_other_roles_stays_rejected`, quitando solo `("architect","brainstorm")`, con el motivo registrado.
2. Añadir N1 y N2 en RED.
3. Mantener todo lo demás.