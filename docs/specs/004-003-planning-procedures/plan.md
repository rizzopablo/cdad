> Materializado por el orquestador desde `architect-draft-001.md` (architect,
> `mofgw/deepseek-v4.1-flash`), verbatim salvo links relativos, con las
> decisiones del dueño aplicadas (D1–D7 en
> [owner-decisions-2026-10-05.md](owner-decisions-2026-10-05.md)) y el plan de
> validación por tarea exigido por `efficient-orchestration-requirements.md` §2.

## Plan — 004-003-planning-procedures

**Feature ID:** `004-003-planning-procedures` · **Epic:** `epic-004-single-source-planning` · **Estado:** aprobado (2026-10-05).

Cada tarea es la unidad mínima con su propio RED, rechazable de forma independiente. D3 decidido: **F4 (T6) no está en el camino feliz de este repo** (`docs/cdad-policy.json` usa `test_roots:["tests"]`; F4 solo muerde layouts co-ubicados) → T6 queda **condicional/fuera del MVP** y F4 se registra como deuda priorizada para el primer consumidor Go o co-ubicado. Camino MVP: T1 → T2 → T3 → T4 → T5 → T7.

### Tareas

| Tarea | Entregable y verificación (RED) | Consume | Depende de |
|---|---|---|---|
| **T1 — Contract-kind de plan borrador (D8)** | El renderer acepta un `contract_kind` distinto para un plan **borrador** con versión + referencia de autoridad y **rechaza** reutilizar `approved-*`; esquema actualizado. RED: `prepare` renderiza un paquete de reviewer con contrato no aprobado; un `approved-*` forjado sobre un borrador se diagnostica rc≠0 sin publicación. Archivos: `cdad_packet.py` (`:50,700-704,869-882,2252-2282`), `assets/active-packet.schema.json`, `tests/test_004_003_t1_draft_contract.py`. | Semántica de `_approved_stage_entry`/`_validate_v2_vigency` (`cdad_packet.py:1220-1231,1284-1288`) | spec/plan aprobados |
| **T2 — Subfase y paquete de revisión de plan** | `ROLE_SUBSTAGES[reviewer]` gana `plan-review`; nuevo `packets/substages/reviewer-plan-review.md`; el paquete del reviewer lleva intención+restricciones+plan (no solo la spec). RED: un producto instalado renderiza un paquete de revisión de plan sin leer el repo fuente. Archivos: `cdad_packet.py:51-57`, `packets/substages/reviewer-plan-review.md`, `handoff-prompts.md`, `tests/test_004_003_t2_plan_review.py`. | T1 | T1 |
| **T3 — Checks de productor/consumidor y dependencias** | Checks mecánicos sobre un fixture de plan: entrada sin productor, dependencia circular, contrato incompatible, paralelismo inválido. RED: cada fixture falla con diagnóstico específico; un plan válido pasa. Archivos: `cdad_packet.py` (validador), `tests/test_004_003_t3_plan_checks.py`, fixtures. | T2 | T2 |
| **T4 — Plan de validación por unidad (PD-8)** | El esquema/sección del plan exige por tarea: pruebas focales, regresiones afectadas, gate de integración, responsable, y comprobaciones observables para ciclos sin código. RED: un plan sin el campo se rechaza; un plan Go/sin-código con comprobación observable pasa. Archivos: `planning-contract-draft.md` §4, `stage-2-specification.md`, `tests/test_004_003_t4_validation_fields.py`. | T3 (formato de plan) | T3 |
| **T5 — Equivalencia y re-entry (G1–G3)** | Regla documentada e instalable: citar una corrida registrada cuando hay equivalencia; forzar corrida nueva cuando falla; reconciliación dos-intentos ↔ sin-progreso. RED: un fixture "mismo árbol, citar corrida previa" pasa sin re-ejecutar; uno de "cambio material" exige corrida nueva; un reintento idéntico sin información nueva dispara revisión de estrategia. Archivos: `references/re-entry.md`, `references/stage-3-tdd.md`, `SKILL.md`, quizá `packets/common.md`; `tests/test_004_003_t5_reentry_equivalence.py`. | T1 (identidad de evidencia) | T1 |
| **T6 — Scopes del test-writer para tests co-ubicados (F4) — CONDICIONAL** | **Solo si** un consumidor Go/co-ubicado entra al camino feliz: `_default_scopes` deriva los scopes del test-writer solo de `test_roots` (`cdad_packet.py:902-907`) → con solo `test_files`/co-ubicados da `write_scope` vacío y rechaza el scope explícito (`debt-second-look.md:11`). RED: una política tipo Go (co-ubicada `_test.go`) produce un write_scope no vacío y aceptado. Archivos: `cdad_packet.py:902-913`, `tests/test_004_003_t6_colocated_scopes.py`. | T1 | Decisión D3 |
| **T7 — Recorrido instalado real sobre 003-002 (PD-13)** | Desde una instalación **aislada**, correr la revisión de plan sobre el trabajo pendiente de 003-002; registrar dictamen + cambios concretos; sin reimplementar 003-002. **Promulgación (F2 de review-t5):** instalar en la raíz aislada y mostrar `install.sh --check` verde como evidencia de que el procedimiento llega a la instalación (los mirrors de `$HOME` quedan fuera de alcance por regla del proyecto). **Ejercicio de AC-4:** el recorrido es el flujo consecutivo real donde la regla de equivalencia se aplica. El RED es la salida observable del recorrido (informe de revisión de plan + cambios registrados), no una suite fabricada. Archivos: `docs/specs/004-003-planning-procedures/evidence/` + plan de 003-002 (solo cambios de plan). | T1–T5 | T1–T5 |

Trazabilidad: cada PD mapea a ≥1 tarea (PD-1→T1; PD-2/3→T2/T7; PD-4→T2; PD-5/6→T5; PD-7→T5; PD-8→T4; PD-9→T2; PD-10→T5; PD-11→T4/T6; PD-12→T7; PD-13→T7).

**Trazabilidad de criterios de aceptación (reconciliada 2026-10-05 por F1/F2 de `review-t5.md`):**

- **AC-4 ("la regla de equivalencia se ejercita con un caso de flujo consecutivo")** no se
  demuestra con oráculos de marcadores: T5 entrega la **declaración** de la regla
  (PD-5/6/7/10 en `re-entry.md` + G2/G3 en sus consumidores) y su ejercicio real
  ocurre en dos lugares verificables: (i) **el propio ciclo de 004-003**, donde el
  orquestador reutilizó evidencia vigente en lugar de duplicar corridas
  (instancias registradas en `dispatch-ledger.md` y `supervision-record.md`: las
  suites de 331/333/338/340/345/353/356/364 se citaron, no se re-ejecutaron, con
  verificación de identidad del árbol), y (ii) **T7**, el recorrido instalado
  sobre 003-002, donde la regla se aplica a un flujo consecutivo real. No se
  inventa un mecanismo ejecutable para PD-5/PD-6: la mejora operativa se
  comprueba por uso real (requisitos de orquestación eficiente §"Aceptación").
- **PD-12 ("llega a la instalación")** se evidencia con la instalación en **raíz
  aislada** y `install.sh --check` verde allí (paso agregado a T7). Los mirrors
  de `$HOME` están **fuera de alcance por regla del proyecto** (nunca instalar
  CDAD en HOME real): su deriva es preexistente a 004-003 y no se resuelve acá.

### Plan de validación por unidad (procedimiento del propio 004-003)

| Tarea | Pruebas focales | Regresiones afectadas | Gate de integración | Responsable |
|---|---|---|---|---|
| T1 | `tests/test_004_003_t1_draft_contract.py` + negativos (borrador `approved-*` forjado) | Paquetes de 003-001/003-005 que validan `contract_kind` (`test_packet_prepare.py`, `test_cdad_adapters_opencode.py`) | Suite completa una vez por GREEN (implementer) | RED: test-writer; GREEN: implementer; suite: implementer (orquestador solo al cierre) |
| T2 | `tests/test_004_003_t2_plan_review.py` | `ROLE_SUBSTAGES` y validadores de consistencia (`validate-consistency`) | Igual que T1 | RED: test-writer; GREEN: implementer |
| T3 | `tests/test_004_003_t3_plan_checks.py` + fixtures de plan | Validador de paquetes | Igual que T1 | RED: test-writer; GREEN: implementer |
| T4 | `tests/test_004_003_t4_validation_fields.py` | `planning-contract-draft.md` §4 y `stage-2-specification.md` (documental: sin suite) | Regeneración determinista (PD-2 de 004-001) + `make validate` | RED: test-writer; GREEN: implementer |
| T5 | `tests/test_004_003_t5_reentry_equivalence.py` | Gates 3→4 de `SKILL.md`; validadores | Igual que T1 | RED: test-writer; GREEN: implementer |
| T6 (cond.) | `tests/test_004_003_t6_colocated_scopes.py` | `_default_scopes` de todos los roles | Igual que T1 | RED: test-writer; GREEN: implementer |
| T7 | Informe de revisión de plan + cambios registrados (sin suite nueva) | Ninguna (solo lectura del plan de 003-002) | Recorrido instalado en raíz aislada | reviewer (GLM) + orquestador |

Roles y modelos (decisión del dueño): RED/test-audit → test-writer `mofgw/glm-5.3-flash`; GREEN → implementer `mofgw/deepseek-v4.1-flash`; review → reviewer `mofgw/glm-5.3-flash` (familia ≠ implementer); scribe → `mofgw/deepseek-v4.1-flash`.
