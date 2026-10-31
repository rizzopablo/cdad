## Propuesta — solo `plan.md`

Pendiente de revisión y aprobación de Pablo. No modifica la spec.

```text
base_sha256:     9deee470f708a26d3e9418fcf0df5710693a510e7557d8e289494bcc349edd23
proposed_sha256: 2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685
```

```diff
--- a/docs/specs/010-004-packet-dispatch-ergonomics/plan.md
+++ b/docs/specs/010-004-packet-dispatch-ergonomics/plan.md
@@ -9,31 +9,33 @@
 - [ ] T2 — Incorporar contexto explícito y preparación nueva exclusivamente v2.
 - [ ] T3 — Emitir identificaciones C desde paquetes publicados.
 - [ ] T4 — Alinear instrucciones y regenerar distribuibles.
-- [ ] T5 — Verificar invariantes, consumidor instalado y relevancia.
+- [ ] T5 — Verificar invariantes y consumidor instalado.
 - [ ] T6 — Revisar independientemente y completar los gates de cierre.
 
 ## Ejecución y límites
 
 Antes de T1, el orquestador materializa fielmente este borrador, obtiene revisión independiente y aprobación explícita del plan. La aprobación de la spec no acredita estos pasos (`owner-approval-2026-10-30.md:9-11`).
 
-Cada despacho posterior contiene **un rol y una subfase**. RED y GREEN se realizan en sesiones y paquetes separados; el implementer no modifica tests ni insumos de aceptación. Ejecución secuencial: T2 y T3 comparten superficies, por lo que separarlas en paralelo añadiría coordinación sin independencia real.
+Cada despacho posterior contiene **un rol y una subfase**. T2 exige **POST-AUDIT → RED → GREEN en tres dispatches, sesiones y paquetes separados**, tras aprobar T1. El implementer no modifica tests ni insumos de aceptación. Ejecución secuencial: T2 y T3 comparten superficies, por lo que separarlas en paralelo añadiría coordinación sin independencia real.
 
 Se conserva la resolución compartida comprometida, en lugar de parches por comando; no se generalizan las interfaces de `cdad_result` ni las fronteras históricas de comparación (`spec.md:129-165,319-335`).
 
-Solo T1 constituye la siguiente tanda detallada. Las restantes tienen objetivo y dependencia completos; su selección exacta de tests y archivos se concreta con el AUDIT, antes del despacho correspondiente, sin añadir promesas.
+Solo T1 constituye la siguiente tanda detallada. T2–T6 conservan `detail: planned`: antes de cada despacho, el paquete declara archivos, pruebas o checks, regresiones explícitas (o ausencia justificada), gate y ejecutor conforme al AUDIT, **sin `--plan-task`**. Se elige esta vía mínima frente a promover tareas a `next`: no se modifica el plan ni se presume otra aprobación; un cambio de contrato o alcance vuelve al owner (`stage-2-specification.md:152-170`; `cdad_packet.py:5161-5204`).
 
 ## Unidades y validación
 
 | ID / dependencia | Consume → produce; consumidor | Promesas protegidas y validación |
 |---|---|---|
-| **T1 / ninguna** — AUDIT, test-writer read-only | Spec aprobada y tests existentes → informe `test-audit.md`, materializado por el orquestador; lo consumen T2–T5. | Inventario test↔promesa/PC, comportamiento existente frente a nuevo, expectativas históricas sustituidas, regresiones pertinentes y comandos focales. Verificación del informe contra §7 de la spec antes de abrir RED. |
-| **T2 / T1** — RED → GREEN separados | AUDIT y contrato de §4.1 → preparación nueva v2, localizador y resolución compartida; los consumen los tres CLI y T3. | Promesa B: PC-04–07; PC-09 en esas superficies. RED conductual con controles válidos, seguido de GREEN y regresión focal: matriz completa, frontera histórica, ubicación según consumidor y ausencia de efectos en rechazos. |
-| **T3 / T2** — RED → GREEN separados | Contexto y validación de T2 → `render --route C` conforme a §4.2; lo consume el orquestador para despachar. | Promesa A: PC-01–02 y diagnósticos PC-09. Verificar identificación determinista, binding al request publicado, rechazo explícito v1 y paquete íntegro; mantener render completo predeterminado y controles positivos. |
+| **T1 / ninguna** — AUDIT, test-writer read-only | Spec aprobada y tests existentes → informe `test-audit.md`, materializado por el orquestador; lo consumen T2–T5. | Inventario test↔promesa/PC, comportamiento existente frente a nuevo, expectativas históricas sustituidas, regresiones pertinentes y comandos focales. Verificación y aprobación del informe contra §7 de la spec antes de POST-AUDIT. |
+| **T2 / T1** — POST-AUDIT → RED → GREEN separados | AUDIT aprobado y contrato de §4.1 → tests existentes actualizados, nuevos RED y producto v2; los consumen los tres CLI y T3. | Promesa B: PC-04–07; PC-09 pertinente. POST-AUDIT aplica solo cambios auditados con trazabilidad PD-12 y verifica todos los tests declarados intactos; distingue su evidencia de los actualizados. Otro dispatch RED añade las pruebas conductuales nuevas con controles válidos; otro GREEN implementa y verifica matriz, frontera histórica, ubicación y rechazos sin efectos. |
+| **T3 / T2** — RED → GREEN separados | Contexto y validación de T2 → `render --route C` conforme a §4.2; lo consume el orquestador para despachar. | Promesa A: PC-01–02 y diagnósticos PC-09. Verificar identificación determinista, binding publicado, rechazo v1 y paquete íntegro; asignar aquí PC-08a como regresión existente (canónico, cuerpo alterado, CRLF y fronteras de preámbulo), sin fabricar RED. Mantener render completo predeterminado y controles positivos. |
 | **T4 / T3** — RED pertinente → GREEN separados | Interfaces verificadas → fuentes coherentes y agentes regenerados; los consumen ambos runtimes y T5. | PC-03, PC-07b, PC-08b, PC-09 documental, PC-10–12. Checks mecánicos pertinentes antes de GREEN; revisión semántica independiente posterior. `make agents` genera los derivados; no se parchean manualmente. |
-| **T5 / T4** — subfases separadas | Producto generado y pruebas protegidas → evidencia de invariantes, recorrido instalado y auditoría de relevancia; la consume T6. | PROPERTIES, INTEGRATION/E2E y POST-AUDIT en encargos distintos. Generadores solo para invariantes verificables, sembrados y acotados; reutilizar cobertura suficiente. Consumidor aislado: preparar v2 → emitir C → resolver y validar contexto. POST-AUDIT independiente de quien escribió los tests. |
-| **T6 / T5** — revisión y cierre separados | Evidencia completa → revisión, aceptación y actualización aprobada del Memory Bank; consumidor: Pablo. | Revisión independiente contra todas las promesas y límites; correcciones por el rol competente. El responsable del cierre ejecuta la suite completa conforme al paquete y registra evidencia. Scribe devuelve borrador; aprobación y materialización siguen separadas. |
+| **T5 / T4** — subfases separadas | Producto generado y pruebas protegidas → evidencia de invariantes y recorrido instalado; la consume T6. | PROPERTIES e INTEGRATION/E2E en encargos distintos. Generadores solo para invariantes verificables, sembrados y acotados; reutilizar cobertura suficiente. Consumidor aislado: preparar v2 → emitir C → resolver y validar contexto. La auditoría de relevancia corresponde obligatoriamente a T6, no a POST-AUDIT. |
+| **T6 / T5** — revisión y cierre separados | Evidencia completa → revisión, aceptación y actualización aprobada del Memory Bank; consumidor: Pablo. | Revisión independiente contra todas las promesas y límites, incluida obligatoriamente la auditoría test↔promesa/PC por el reviewer de Stage 4, en sesión distinta de quien escribió los tests (`stage-3-tdd.md:45-47,270`); correcciones por el rol competente. El responsable del cierre ejecuta la suite completa conforme al paquete y registra evidencia. Scribe devuelve borrador; aprobación y materialización siguen separadas. |
 
 Las pruebas focales y regresiones se ejecutan con selección proporcional, no con una suite completa por despacho. Cada resultado registra comando, salida, revisión del árbol y efectos observados. Un fallo de fixture o importación no acredita RED.
+
+Prevalece la unidad por invocación de `sources/roles/orchestrator.md:126-131`: no copiar la combinación POST-AUDIT+RED de `handoff-prompts.md:220-225,334,347` ni de `packets/substages/test-writer-post-audit.md:1`. Un render que aún combine subfases se devuelve al orquestador para resolver la contradicción antes de despachar; no se parchean sus bytes.
 
 ## T1: alcance inmediato
 
@@ -46,18 +48,18 @@
 1. Inventariar las pruebas afectadas, distinguiendo expectativas vigentes de las sustituidas por PC-04. Como puntos de partida verificados:
    - `tests/test_004_002_t6_landing.py::test_pd12_legacy_without_policy_keeps_legacy_intake`;
    - `tests/test_packet_prepare.py::test_p2_default_execution_context_and_out_dir_under_project_cdad`.
-2. Trazar cada actualización histórica: expectativa anterior → `004-002` PD-12 → decisión owner → `010-004` §7/PC-04. La spec histórica queda intacta; el test-writer actualiza expectativas en RED, no el implementer ni el cierre.
+2. Trazar cada actualización histórica: expectativa anterior → `004-002` PD-12 → decisión owner → `010-004` §7/PC-04. La spec histórica queda intacta; el test-writer actualiza expectativas en POST-AUDIT aprobado, antes del dispatch RED separado, no el implementer ni el cierre.
 3. Separar **PC-08a, regresión existente**, de **PC-08b, instrucciones nuevas revisables**. Reutilizar controles de cuerpo alterado y CRLF; no fabricar un RED para una garantía ya verde. Las referencias iniciales son `test_role_packet_render.py:350` y `test_role_packet_review_regressions.py:468`.
 4. Declarar selección focal, regresiones, controles positivos, comandos y límites de evidencia para la siguiente tanda.
 
-**Gate:** el orquestador comprueba trazabilidad y registra la consecuencia de usuario exigida por R4 para cada prueba seleccionada (`sources/roles/orchestrator.md:274-281`). No hay cuota por PC ni variantes equivalentes obligatorias; tampoco se difiere una promesa comprometida.
+**Gate:** el orquestador comprueba trazabilidad y registra la consecuencia de usuario exigida por R4 para cada prueba seleccionada (`sources/roles/orchestrator.md:274-281`). Antes de POST-AUDIT exige aprobación de Pablo del AUDIT o un mandato explícito vigente que autorice aprobar ese informe, verificado y citado. La delegación operativa de `execution.md:25-33` y un precedente no bastan: no hay autoaprobación; sin autoridad inequívoca se solicita decisión a Pablo (`packets/substages/test-writer-audit.md:1`). No hay cuota por PC ni variantes equivalentes obligatorias; tampoco se difiere una promesa comprometida.
 
 ## Superficies previstas
 
 Tras el AUDIT, cada paquete concreta su alcance:
 
 - **T2–T3, Modify:** `skills/cdad-cycle/scripts/cdad_packet.py`. El wrapper `scripts/cdad_packet.py` conserva su función de entrada.
-- **RED, Test:** pruebas existentes auditadas y nuevas pruebas conductuales necesarias bajo `tests/`; no se fijan nombres especulativos antes del inventario.
+- **POST-AUDIT, Test:** solo cambios aprobados en tests existentes bajo `tests/`, con evidencia separada de actualizados e intactos. **RED, Test:** nuevas pruebas conductuales necesarias bajo `tests/`, en otro dispatch; no se fijan nombres especulativos antes del inventario.
 - **T4, Modify:** `sources/roles/{architect,orchestrator}.md`, `sources/agents/adapters/{opencode,claude-code}.md` y las referencias pertinentes de handoff, preparación y re-entry.
 - **T4, Generate:** `build/staging/`, `agents/` y `agents/claude-code/`, mediante los entrypoints de `Makefile:10-18`.
 
@@ -69,7 +71,7 @@
 - La revisión de PC-07b comprueba requisitos por rol y límites reales; no inventa migración ni una salida CLI inexistente.
 - PC-08a mantiene las fronteras de preámbulo; PC-08b no se presenta como prueba de obediencia del modelo.
 - PC-10–11 conservan I-4/I-5: falta de observabilidad no obliga por sí sola a repetir; divergencia conocida no se rescata cambiando a C.
-- La suite completa se reserva al cierre conforme al contrato del paquete. Entry point verificado: `python3 scripts/cdad-suite.py close --all --evidence-root <directorio-autorizado>`.
+- Se elige **T4 como gate transversal anticipado**, tras consolidar renderer T2–T3 y staging T4 y antes de T5 (`stage-3-tdd.md:61-79`). Su paquete solicita explícitamente la suite completa al responsable de integración; T2–T3 usan focales y regresiones proporcionales. Se agrupan esos disparadores, no se exige full por unidad ni por subfase. T6 conserva la suite de cierre por su responsable; solo se cita una corrida registrada en vez de repetirla si se demuestra equivalencia conforme a `re-entry.md:157-167`. Entry point verificado: `python3 scripts/cdad-suite.py close --all --evidence-root <directorio-autorizado>`.
 - Revisión independiente, aceptación funcional y aprobación del Memory Bank no se sustituyen por tests verdes, recibos ni materialización.
 
 ## Incertidumbres y deferred-hardening
@@ -80,7 +82,7 @@
 
 ```plan-tasks
 {
-  "validation_strategy": "AUDIT antes de RED; RED y GREEN separados; pruebas focales y regresiones proporcionales; revisión independiente de instrucciones y relevancia; consumidor instalado aislado; suite completa por el responsable del cierre conforme al paquete.",
+  "validation_strategy": "AUDIT aprobado; POST-AUDIT, RED y GREEN en tres dispatches separados; detalle y regresiones explicitos en paquetes sin --plan-task para planned; focales proporcionales; suite anticipada en T4 por renderer/staging y gate de cierre T6 conforme a equivalencia registrada; relevancia independiente obligatoria en T6; consumidor instalado aislado.",
   "tasks": [
     {
       "id": "T1",
@@ -94,22 +96,22 @@
         "PC-08a existente separada de PC-08b y ambiguedades funcionales escaladas"
       ],
       "regressions": [],
-      "integration_gate": "Orquestador valida el AUDIT y registra seleccion y consecuencia de usuario R4 antes de RED",
-      "owner": "test-writer AUDIT read-only; orquestador materializa y valida"
+      "integration_gate": "Orquestador valida trazabilidad y R4; Pablo aprueba el AUDIT o se verifica mandato explicito vigente para aprobarlo antes de POST-AUDIT",
+      "owner": "test-writer AUDIT read-only; orquestador materializa y valida; Pablo aprueba salvo mandato explicito verificado"
     },
     {
       "id": "T2",
       "detail": "planned",
-      "objective": "Cerrar PC-04 a PC-07 y PC-09 pertinente: contexto explicito, resolucion compartida y toda preparacion nueva v2; RED y GREEN separados",
+      "objective": "Cerrar PC-04 a PC-07 y PC-09 pertinente: contexto explicito, resolucion compartida y preparacion nueva v2; POST-AUDIT, RED y GREEN separados",
       "depends_on": ["T1"],
       "uncertainty": "Inventario completo de expectativas y fixtures afectados",
-      "owner": "test-writer RED; implementer GREEN; orquestador valida gates",
-      "resolves_when": "AUDIT aceptado y siguiente tanda detallada con archivos, pruebas y regresiones trazadas"
+      "owner": "test-writer POST-AUDIT y test-writer RED en sesiones separadas; implementer GREEN; orquestador valida gates",
+      "resolves_when": "AUDIT aprobado y paquete detallado sin --plan-task, con archivos, pruebas, regresiones y gates trazados"
     },
     {
       "id": "T3",
       "detail": "planned",
-      "objective": "Cerrar PC-01 y PC-02 y diagnosticos pertinentes mediante emision C publicada v2-only; RED y GREEN separados",
+      "objective": "Cerrar PC-01 y PC-02 y diagnosticos pertinentes mediante emision C publicada v2-only; verificar PC-08a existente sin RED artificial; RED nuevo y GREEN separados",
       "depends_on": ["T2"],
       "uncertainty": "Seleccion focal reutilizable tras el cambio de contexto",
       "owner": "test-writer RED; implementer GREEN; orquestador valida gates",
@@ -127,11 +129,11 @@
     {
       "id": "T5",
       "detail": "planned",
-      "objective": "Acreditar invariantes aplicables, PC-12 instalado y relevancia independiente en subfases separadas",
+      "objective": "Acreditar invariantes aplicables y PC-12 instalado en subfases separadas; relevancia independiente obligatoria en T6",
       "depends_on": ["T4"],
       "uncertainty": "Cobertura reutilizable y raiz aislada autorizada para el recorrido instalado",
-      "owner": "test-writer en PROPERTIES, E2E y POST-AUDIT mediante encargos separados e independientes cuando corresponda",
-      "resolves_when": "Producto regenerado y seleccion acotada de invariantes, recorrido instalado y auditoria independiente declarados"
+      "owner": "test-writer PROPERTIES y test-writer E2E mediante sesiones y paquetes separados",
+      "resolves_when": "Producto regenerado, gate anticipado T4 verificado y seleccion acotada de invariantes y recorrido instalado declarados"
     },
     {
       "id": "T6",
@@ -139,7 +141,7 @@
       "objective": "Completar revision independiente, suite de cierre, aceptacion y Memory Bank sin presuponer aprobaciones",
       "depends_on": ["T5"],
       "uncertainty": "Hallazgos de revision y evidencia final del arbol",
-      "owner": "reviewer; responsable del cierre; scribe; orquestador; Pablo, cada uno en su cometido",
+      "owner": "reviewer Stage 4 audita obligatoriamente relevancia en sesion distinta del autor de tests; responsable del cierre; scribe; orquestador; Pablo, cada uno en su cometido",
       "resolves_when": "Evidencia T1 a T5 completa y paquetes separados de revision y cierre preparados conforme a gates"
     }
   ]
@@ -148,7 +150,7 @@
 
 ---
 
-**Evidencia del encargo**
+**Evidencia histórica no normativa del encargo anterior**
 
 - Ruta C validada: identificación concordante, REQUEST válido, digest del contrato correcto y `PACKET.md` completo byte-idéntico a `cdad_packet.py render`.
 - Método: Python `3.13.5`, comparación en memoria, sin temporales.
```

## Evidencia de esta ejecución

- **Intake C válido:** `validate-request` y `validate-packet` finalizaron con código 0, sin salida. Comparación completa contra stdout de `render`: **7807 bytes idénticos**, SHA-256 `14dfbe0ec306eb265789425eb3002afd6fe4cd514b2726f3a7d5d81142ad0b20`. Metadatos y digest del contrato concordantes.
- **Comprobación documental:** Python **3.13.5**, exclusivamente en memoria; 24 sustituciones exactas, un bloque JSON válido, seis tareas únicas, cinco dependencias lineales, una tarea `next` y cinco `planned`. Comprobadas la asignación PC-08a/T3, separación de owners y conservación de N-4/N-5/N-6.
- **Referencias verificadas:** `sources/roles/orchestrator.md:123-131`; `skills/cdad-cycle/references/stage-3-tdd.md:45-79,270`; `stage-2-specification.md:152-170`; `re-entry.md:157-167`; `skills/cdad-cycle/scripts/cdad_packet.py:5161-5204`. `execution.md` refiere a `docs/epics/epic-010-documentary-specialization/execution.md:25-33`.
- **Límite operativo explícito:** la plantilla POST-AUDIT vigente todavía combina subfases. La propuesta exige resolver esa contradicción antes de despachar; no autoriza parchear paquetes.
- **Árbol intacto:** `git diff --exit-code` y `git diff --cached --exit-code` terminaron con código 0, sin salida. HEAD inicial/final: `d00f7349ed98519d702e5fd20044eace82ff1b7e`. Los hashes finales del plan y spec coinciden con sus pins.
- **Archivos modificados:** ninguno. **Commit creado:** ninguno. El untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md` quedó intacto.
- Comandos exactos, comparador en memoria y salidas constan en las llamadas de herramientas. Una consulta inicial a `validate --help` devolvió código 2: ese subcomando no existe; se utilizaron después los validadores correctos.
- **No ejecuté tests, suite, implementación, generación, instalación ni push. No otorgué aprobación.**