# 006-005-native-path-parity — PLAN (etapa 2, revisión draft-002)

Estado: **BORRADOR no aprobado**, insumo de la review independiente (`plan-review` sobre `draft-plan`, enmienda 006) antes del RED.
Contrato: epic `plan.md` §11/§12/§13. Spec: la de esta carpeta (misma entrega). Base medida: HEAD `9d3b2ea`. Anonimización como en la spec. Es un plan de feature: unidades, archivos, RED y gates.

## 1. Orden y dependencias

`U1 → U2`; `U3` y `U5` son independientes de U2 (tocan `cdad_packet.py`, sin solape de líneas con U1); `U4` al final (toca texto generado); `U6` después de U1–U5. Ninguna unidad empieza sin su RED declarado y sin la review de spec/plan hecha (PD-21).

## 2. Unidades

| Unidad | Resultado | Depende de | PD | Gate |
|---|---|---|---|---|
| **U1** | Entrada única `cdad_dispatch.py` (`dispatch`/`record`/`capabilities`), config por runtime + migración, agente en el paquete, **registro único** (la interfaz deja de registrar) | — | PD-1…PD-9 | RED + focales GREEN + regresiones de delegación/interfaz/instalador + `make validate` |
| **U2** | Módulo de runtime OpenCode: credencial inyectada, agente del paquete, `capabilities`/`--observe`, correlación, fallo cerrado, sin polling | U1 (contrato) | PD-10…PD-14 | RED + focales con store descartable + **binario falso** + regresiones del módulo |
| **U3** | Temporal del test-writer: clase, política, propuesta, `git check-ignore` | — | PD-15…PD-18 | RED + focales de scope + regresiones de política/`prepare`/`receive` |
| **U4** | Entrada única en el mandato + secciones `delegation` + regeneración | U1–U3 (texto final del recorrido) | PD-20 | RED de texto + `make staging` determinista + `make validate` |
| **U5** | Camino mecánico a `failed` y desbloqueo verificado de `prepare` | — | PD-19 | RED + focales + regresiones de transiciones/estado |
| **U6** | Recorrido de aceptación de §11 en proyecto descartable, con las dos vías | U1–U5 | PD-22 | recorrido con evidencia; regla de bloqueo (§3 U6) |

## 3. Fichas por unidad

### U1 — Entrada única, configuración y registro único
- **Archivos:**
  - **nuevo** `skills/cdad-cycle/scripts/cdad_dispatch.py`: los tres verbos (§2.1), la resolución del runtime (PD-8), la lectura/validación de la sección `runtimes.json` y la derivación de la configuración interna del módulo bajo `.cdad/` (PD-9), el cuerpo único de observación/registro/escenificación de `record` (PD-3…PD-6), y la importación de los ayudantes de la interfaz (una sola implementación de cada uno).
  - `skills/cdad-cycle/scripts/cdad_delegate.py`: **se quita su registro** (`_observation`:288, `_register_dispatch`:311, la invocación :396-399) y se **relaya** el `attempt` del módulo; la interfaz conserva su CLI y su `--exec-config` (deuda declarada, §8 item 4).
  - `skills/cdad-cycle/scripts/cdad_packet.py`: `prepare` resuelve y escribe `agent` en el documento de `REQUEST.json` (hoy :4456-4474, sin el campo; `state.stack` hoy sin consumidor: verificado). **Sólo la zona de `prepare`** (sin solape con U3/U5).
  - `install.sh`: plantilla de `runtimes.json` con la disciplina de dato del usuario (`install_user_config`, :1191-1201; precedente :1151-1166 — sólo si no existe, no se registra, no se pisa).
  - `skills/cdad-cycle/references/cli-delegation.md`: la entrada nueva, la sección de config y la migración (el exec-config deja de ser dato del usuario).
- **RED:** `tests/test_006_005_u1_dispatch_entry.py` (nuevo) — PD-1 (un intento por vía; la interfaz no registra), PD-2 (no es segundo escritor), PD-3 (`sha256` byte-exacto), PD-4 (sin texto no hay entrega ni `receive`), PD-5 (las cuatro llaves, una por caso, y el paquete sin `agent`), PD-6 (`session: null` + `provenance`), PD-7 (`agent` = rol+`stack`; sin `agent` sigue despachable), PD-8 (flag / declaración / ninguno / valor inválido), PD-9 (sin sección, con `model`, con exec-config heredado). Fixture: proyecto descartable con `XDG_CONFIG_HOME` redirigido (patrón ya usado por los tests de config de 006-003).
- **Regresiones:** `tests/test_005_009_t1_interface.py`, `tests/test_005_009_t2_opencode_adapter.py`, `tests/test_005_010_t1_durable_signal.py`, `tests/test_005_007_t5_delegation_dispatch.py`, `tests/test_004_002_t4_dispatch.py`, `tests/test_006_002_u5_transport_equivalence.py`, `tests/test_006_001_t1_selection.py`, `tests/test_006_003_u4_delegation_config.py`, `tests/test_006_003_u8_acceptance.py`, `tests/test_005_004_t2_installer_claims.py`, `tests/test_006_003_u2_installer_without_profiles.py`, `tests/test_packet_prepare.py`.
- **A-1 (tests acoplados, ver §4):** `tests/test_005_009_t1_interface.py` (el destino de prueba pasa a **registrar su propio intento** y la interfaz a relayarlo; las aserciones sobre el registro dejan de ser del interfaz).
- **Nota de diseño (sin abstracción nueva):** no se crea `cdad_runtime_<id>.py` (D-2); no se agrega lista de versiones (la declaración sigue siendo `binary_version`).
- **Gate:** RED declarado y failing por la razón correcta; GREEN focal; regresiones verdes; `make validate`.

### U2 — Módulo de runtime OpenCode
- **Archivos:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`:
  - **PD-11:** inyección de la credencial resuelta en el entorno del cliente, sólo en `mode: server`, junto al `PWD` (`_invoke_destination`:426-427); nada en `standalone`/`service`.
  - **PD-14:** el agente sale de `REQUEST.json.agent` (`_entry_agent_name`:298 + `_check_derived_agent_published`:302 aplicados al agente del paquete), con la degradación declarada cuando el campo no está.
  - **PD-10/PD-12/PD-13:** `--capabilities` y `--observe` (una lectura `mode=ro`, acotada, sin polling), exigiendo las columnas de correlación (`parent_id`, `directory`, `time_created` además del subconjunto actual `SESSION_V2_COLUMNS`:182) y fallando cerrado nombrando las ausentes.
  - `attempt` declarado en el sobre (conserva su registro, PD-1).
- **Sonda antes del RED:** V-1/V-7 (cómo se obtiene la sesión hija y columnas reales de la versión instalada); el hallazgo se registra y se declara en `capabilities`.
- **RED:** `tests/test_006_005_u2_opencode_module.py` (nuevo) — **binario falso que exige `OPENCODE_PASSWORD`** y eco de si la vio (PD-11, con el centinela ausente de `argv`, stdout/stderr, registro I8 y recibo); PD-14 (`argv` con el agente del paquete; agente no publicado → fallo cerrado; sin campo → `cdad-<rol>` declarado); PD-5 (las cuatro llaves por caso) y PD-12/PD-13 con store SQLite descartable (receta de aislamiento, `cli-delegation.md`:239+); PD-10.
- **Regresiones:** `tests/test_cdad_adapters_opencode.py`, `tests/test_005_009_t2_opencode_adapter.py`, `tests/test_006_001_t1b_service_mode.py`, `tests/test_006_001_t2_wait_recovery.py`, `tests/test_006_001_t3_concurrency.py`, `tests/test_006_003_u6_server_credential.py`, `tests/test_003_003_t2_preflight.py`.
- **Gate:** focales verdes con store descartable y binario falso; regresiones verdes.

### U3 — Temporal del test-writer
- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — vocabulario de clases (`SCOPE_CLASSES`:67, hoy sin `temporary`), validador único de scopes (`_validate_scope`:694 y el conjunto de escritura del test-writer :727-729), pertenencia de un cambio observado (`_scope_contains`:739, usado por el manifiesto en `cdad_result.py`:370), propuesta (`propose_policy`:1088, hoy :1101) y el paso `git check-ignore` en `prepare`. El detalle de forma es del implementer; el contrato son PD-15…PD-18.
- **RED:** `tests/test_006_005_u3_temporary_scope.py` (nuevo) — PD-15 (política vacía → rechazo nombrando `docs/cdad-policy.json`; con raíz declarada → acepta), PD-16 (`git check-ignore` negativo y positivo, y proyecto no-Git), PD-17 (recibo `scope_validation: passed` con test real + sonda temporal, y rechazo fuera de scope), PD-18 (raíz temporal solapada con producto → rechazo).
- **V-8 / regla A-1:** no se encontró test que fije el valor de la propuesta; si el RED encuentra uno, se cambia **en RED declarando el reemplazo**.
- **Regresiones:** `tests/test_004_002_t1_policy.py`, `tests/test_004_002_t1_reviewfix.py`, `tests/test_004_002_t2_bootstrap.py`, `tests/test_004_002_t6_landing.py`, `tests/test_004_002_t7_acceptance.py`, `tests/test_004_002_t7_private_paths.py`, `tests/test_004_002_t7_limits_rule.py`, `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_packet_prepare.py`, `tests/test_005_005_t2_docs_policy.py`.
- **Gate:** RED + focales; regresiones de política y recepción verdes; `make validate`.

### U4 — Entrada única y secciones `delegation`
- **Archivos:** `sources/roles/orchestrator.md` (intake :22-57 con las cuatro entradas solapadas y la condición stale :24; disciplina de contexto :104-108), `sources/agents/adapters/opencode.md` (§`delegation` :60-94), `sources/agents/adapters/claude-code.md` (§`delegation` :80-116), `skills/cdad-cycle/references/re-entry.md` (si el paso mecánico de escenificación se nombra allí), `scripts/cdad-generate.py`:747 (etiqueta «## Delegation (adapter)», V-4) y los agentes regenerados por `make agents` (salidas declaradas: nunca a mano, `Makefile`:1-24).
- **RED:** `tests/test_006_005_u4_single_entry.py` (nuevo) — PD-20: la fuente tiene el orden de cinco filas sin solapes, **sin** la condición `.cdad/execution.json` y **con** la regla de transporte (mismo runtime ⇒ nativa + `record`; otro ⇒ la entrada externa); el generado recomputado coincide byte a byte; las secciones `delegation` nombran la entrada nueva, el agente del paquete y la credencial del módulo.
- **Regresiones (todo test que lea orquestadores o agentes generados):** `tests/test_005_006_t2_intake.py`, `tests/test_006_002_u1_delegation_section.py`, `tests/test_006_002_u2_neutral_skill.py`, `tests/test_006_002_u3_runtime_references.py`, `tests/test_006_002_u6_context_discipline.py`, `tests/test_006_003_u3_texts_without_profiles.py`, `tests/test_cdad_generate.py`, `tests/test_bash_policy_selection.py`, `tests/test_opencode_read_map_and_steps.py`, `tests/test_005_004_t2_installer_claims.py`, `tests/test_role_packet_render.py`.
- **Gate:** `make staging` determinista (dos corridas, mismos bytes), RED de texto verde, regresiones verdes, `make validate`.

### U5 — Camino mecánico a `failed`
- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — efecto de la clase `disposition` (hoy `pass`:5584-5589) y la coherencia de `validate_state` (:546). No se toca `_dispatched_packet_ids`/`_missing_required_deliveries` (:4855/:4944): leen el **ledger de despachos**, así que el cierre sigue satisfaciendo PD-8(a) por la disposición registrada.
- **RED:** `tests/test_006_005_u5_disposition_failed.py` (nuevo) — PD-19: paquete activo sin recibo → `failed`; `validate-state` VALID; `prepare` bloqueado antes (:4337-4338) y desbloqueado después; con recibo durable ⇒ rechazo que nombra `receive` (:5207-5213); la disposición sigue sin aprobar nada (`approval_effect: false`, sin `approved_by`).
- **A-1 (declarado):** `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830 afirma hoy que el paquete sigue `dispatched` tras la disposición. Reemplazo declarado: «`active_packet.status` pasa a `failed` (terminal); el resto del estado sigue intacto». Se revisa además que el flujo B1 (:835) siga avanzando.
- **Regresiones:** `tests/test_005_012_t1_register_transition_base.py`, `tests/test_005_012_t3_closure_dispatch_resolution.py`, `tests/test_005_012_t4_late_delivery.py`, `tests/test_005_001_t2_replace_packet.py`, `tests/test_005_001_t3_idle.py`, `tests/test_006_003_rf_review_fixes.py`, `tests/test_006_003_rf2_review_fixes.py`, `tests/test_packet_prepare.py`.
- **Gate:** RED + focales; regresiones verdes; `make validate`.

### U6 — Recorrido de aceptación (no es unidad de código)
- **Escenario (PD-22):** proyecto **descartable** con layout anidado; el coordinador iniciado **desde otra carpeta**; agente **global** y configuración de **proyecto** declarados distintos (garantía menor declarada); un auxiliar temporal necesario; **un test real escrito y recibido** (recibo `pending`, `scope_validation: passed`); **una entrega por la vía externa** con la entrada nueva (con su intento = el del módulo) y **una por la vía nativa** (`task` + `record`, con el mismo paquete y el mismo texto final esperado); **un intento interrumpido** registrado sin entrega y llevado a `failed` **por comando**; y la sonda V-11 (`--agent cdad-<rol>-odoo` con `stack: odoo`).
- **Evidencia:** los archivos de intento I8, los recibos, el estado resultante, los sobres de los dos verbos y la versión/configuración observadas. Sin generalizar (spec §7). Se entrega como documento de evidencia en la carpeta de la spec (no en `tests/`).
- **Regla de bloqueo por ambiente:** si el ambiente no puede ejecutar el recorrido (runtime ausente, versión fuera de la declarada, store no disponible, agente `-odoo` no publicado), la unidad se declara **BLOQUEADA** con el motivo y la evidencia del intento; **no** se sustituye por una corrida simulada, por un éxito inventado ni por «debería funcionar». Decide el dueño/orquestador (autorizar, re-scopear o re-rutear).

## 4. Regla A-1 (tests acoplados)

Un test acoplado a la superficie que cambia se modifica **sólo en el RED de su unidad**, declarando en el propio RED: (1) el test que se reemplaza, (2) la postcondición nueva que lo reemplaza, (3) la razón. Nunca en GREEN, nunca por invisibilizar un fallo. Aplica a:

| Unidad | Test | Reemplazo declarado |
|---|---|---|
| U1 | `tests/test_005_009_t1_interface.py` (las aserciones donde la **interfaz** es quien registra) | la interfaz **relaya** el `attempt` del módulo y **no** registra; el destino de prueba del fixture registra su propio intento; el único registro del despacho es el del módulo (PD-1/D-ADP-2). El resto del contrato de la interfaz (transporte byte-idéntico, sobre, fallo cerrado) no cambia. |
| U3 | — (V-8: ningún test encontrado hoy que fije el valor de la propuesta) | si el RED encuentra uno, se declara aquí antes de tocarlo |
| U5 | `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830 | `active_packet.status` pasa a `failed` (terminal); el resto del estado intacto |

## 5. Cierre

Review independiente de spec/plan **antes** del RED (PD-21; `plan-review` sobre `draft-plan`, sin subfase nueva). Al cerrar el código: `make validate` y la **suite completa una vez**, corrida por quien cierra (política declarada; se repite sólo si cambios o evidencia invalidada lo justifican). Review formal del resultado en sesión independiente; el recorrido real de U6 (AC-7) queda declarado con su estado, y no se acredita aceptación real por pruebas aisladas.

## 6. Tareas declaradas (`plan-tasks`)

Derivado por el orquestador, sin contenido nuevo, de las fichas de §3 (archivos, RED, regresiones y A-1) para que el CLI admita el plan como `draft-plan`. Si difiere de §3, manda §3 y el bloque se corrige.

```plan-tasks
{
 "validation_strategy": "Por unidad: RED declarado y failing por la razon correcta, focales GREEN y las regresiones listadas en su ficha; make validate en U1, U3, U4 y U5; make staging determinista en U4. La suite completa la corre una vez quien cierra (PD-21); se reutiliza evidencia equivalente con procedencia verificada (re-entry.md, Equivalence of a registered run).",
 "tasks": [
  {
   "id": "U1",
   "objective": "Entrada unica cdad_dispatch.py (dispatch/record/capabilities), config por runtime + migracion, agente en el paquete y registro unico (la interfaz deja de registrar).",
   "produce": [],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_dispatch.py",
    "skills/cdad-cycle/scripts/cdad_delegate.py",
    "skills/cdad-cycle/scripts/cdad_packet.py",
    "install.sh",
    "skills/cdad-cycle/references/cli-delegation.md",
    "tests/test_005_009_t1_interface.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u1_dispatch_entry.py"
   ],
   "regressions": [
    "tests/test_005_009_t1_interface.py",
    "tests/test_005_009_t2_opencode_adapter.py",
    "tests/test_005_010_t1_durable_signal.py",
    "tests/test_005_007_t5_delegation_dispatch.py",
    "tests/test_004_002_t4_dispatch.py",
    "tests/test_006_002_u5_transport_equivalence.py",
    "tests/test_006_001_t1_selection.py",
    "tests/test_006_003_u4_delegation_config.py",
    "tests/test_006_003_u8_acceptance.py",
    "tests/test_005_004_t2_installer_claims.py",
    "tests/test_006_003_u2_installer_without_profiles.py",
    "tests/test_packet_prepare.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U2",
   "objective": "Modulo de runtime OpenCode: credencial inyectada solo en el cliente en mode server, agente del paquete, --capabilities/--observe, correlacion de cuatro llaves, fallo cerrado, sin polling.",
   "produce": [],
   "consume": [],
   "depends_on": [
    "U1"
   ],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_delegate_opencode.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u2_opencode_module.py"
   ],
   "regressions": [
    "tests/test_cdad_adapters_opencode.py",
    "tests/test_005_009_t2_opencode_adapter.py",
    "tests/test_006_001_t1b_service_mode.py",
    "tests/test_006_001_t2_wait_recovery.py",
    "tests/test_006_001_t3_concurrency.py",
    "tests/test_006_003_u6_server_credential.py",
    "tests/test_003_003_t2_preflight.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U3",
   "objective": "Temporal del test-writer: clase temporary, politica, propuesta y git check-ignore en prepare.",
   "produce": [],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u3_temporary_scope.py"
   ],
   "regressions": [
    "tests/test_004_002_t1_policy.py",
    "tests/test_004_002_t1_reviewfix.py",
    "tests/test_004_002_t2_bootstrap.py",
    "tests/test_004_002_t6_landing.py",
    "tests/test_004_002_t7_acceptance.py",
    "tests/test_004_002_t7_private_paths.py",
    "tests/test_004_002_t7_limits_rule.py",
    "tests/test_003_002_t1_receive.py",
    "tests/test_003_002_t2_materialize.py",
    "tests/test_packet_prepare.py",
    "tests/test_005_005_t2_docs_policy.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U4",
   "objective": "Entrada unica en el mandato del orquestador + secciones delegation + regeneracion de los generados.",
   "produce": [],
   "consume": [],
   "depends_on": [
    "U1",
    "U2",
    "U3"
   ],
   "parallel": [],
   "files": [
    "sources/roles/orchestrator.md",
    "sources/agents/adapters/opencode.md",
    "sources/agents/adapters/claude-code.md",
    "skills/cdad-cycle/references/re-entry.md",
    "scripts/cdad-generate.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u4_single_entry.py"
   ],
   "regressions": [
    "tests/test_005_006_t2_intake.py",
    "tests/test_006_002_u1_delegation_section.py",
    "tests/test_006_002_u2_neutral_skill.py",
    "tests/test_006_002_u3_runtime_references.py",
    "tests/test_006_002_u6_context_discipline.py",
    "tests/test_006_003_u3_texts_without_profiles.py",
    "tests/test_cdad_generate.py",
    "tests/test_bash_policy_selection.py",
    "tests/test_opencode_read_map_and_steps.py",
    "tests/test_005_004_t2_installer_claims.py",
    "tests/test_role_packet_render.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U5",
   "objective": "Camino mecanico a failed por disposition sin recibo y desbloqueo verificado de prepare.",
   "produce": [],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py",
    "tests/test_005_012_t3_closure_dispatch_resolution.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u5_disposition_failed.py"
   ],
   "regressions": [
    "tests/test_005_012_t1_register_transition_base.py",
    "tests/test_005_012_t3_closure_dispatch_resolution.py",
    "tests/test_005_012_t4_late_delivery.py",
    "tests/test_005_001_t2_replace_packet.py",
    "tests/test_005_001_t3_idle.py",
    "tests/test_006_003_rf_review_fixes.py",
    "tests/test_006_003_rf2_review_fixes.py",
    "tests/test_packet_prepare.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U6",
   "objective": "Recorrido de aceptacion de §11 en proyecto descartable con las dos vias (PD-22), incluida la sonda V-11; no es unidad de codigo; regla de bloqueo por ambiente.",
   "produce": [],
   "consume": [],
   "depends_on": [
    "U1",
    "U2",
    "U3",
    "U4",
    "U5"
   ],
   "parallel": [],
   "files": [],
   "integration_gate": "@validation_strategy",
   "owner": "orquestador (recorrido real) con evidencia",
   "observable_checks": [
    "intento I8 por cada via (externa con la entrada nueva; nativa con task + record) en .cdad/executions/<exec>/dispatches/",
    "recibo pending con scope_validation: passed para un test real y una sonda temporal",
    "intento interrumpido llevado a failed por register-transition disposition, validate-state VALID",
    "sonda V-11: session_v2.agent == cdad-<rol>-odoo en proyecto descartable con stack: odoo, o BLOQUEADA con motivo"
   ],
   "regressions": []
  }
 ]
}
```
