# Plan de implementación — 010-004: ergonomía del despacho

**Estado:** borrador para revisión independiente y aprobación separada de Pablo.  
**Contrato:** `spec.md`, SHA-256 `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`. No modifica la spec ni reabre Discovery.

## Steps

- [ ] T1 — Auditar pruebas y conservar trazabilidad histórica.
- [ ] T2 — Incorporar contexto explícito y preparación nueva exclusivamente v2.
- [ ] T3 — Emitir identificaciones C desde paquetes publicados.
- [ ] T4 — Alinear instrucciones y regenerar distribuibles.
- [ ] T5 — Verificar invariantes y consumidor instalado.
- [ ] T6 — Revisar independientemente y completar los gates de cierre.

## Ejecución y límites

Antes de T1, el orquestador materializa fielmente este borrador, obtiene revisión independiente y aprobación explícita del plan. La aprobación de la spec no acredita estos pasos (`owner-approval-2026-10-30.md:9-11`).

Cada despacho posterior contiene **un rol y una subfase**. T2 exige **POST-AUDIT → RED → GREEN en tres dispatches, sesiones y paquetes separados**, tras aprobar T1. El implementer no modifica tests ni insumos de aceptación. Ejecución secuencial: T2 y T3 comparten superficies, por lo que separarlas en paralelo añadiría coordinación sin independencia real.

Se conserva la resolución compartida comprometida, en lugar de parches por comando; no se generalizan las interfaces de `cdad_result` ni las fronteras históricas de comparación (`spec.md:129-165,319-335`).

Solo T1 constituye la siguiente tanda detallada. T2–T6 conservan `detail: planned`: antes de cada despacho, el paquete declara archivos, pruebas o checks, regresiones explícitas (o ausencia justificada), gate y ejecutor conforme al AUDIT, **sin `--plan-task`**. Se elige esta vía mínima frente a promover tareas a `next`: no se modifica el plan ni se presume otra aprobación; un cambio de contrato o alcance vuelve al owner (`stage-2-specification.md:152-170`; `cdad_packet.py:5161-5204`).

## Unidades y validación

| ID / dependencia | Consume → produce; consumidor | Promesas protegidas y validación |
|---|---|---|
| **T1 / ninguna** — AUDIT, test-writer read-only | Spec aprobada y tests existentes → informe `test-audit.md`, materializado por el orquestador; lo consumen T2–T5. | Inventario test↔promesa/PC, comportamiento existente frente a nuevo, expectativas históricas sustituidas, regresiones pertinentes y comandos focales. Verificación y aprobación del informe contra §7 de la spec antes de POST-AUDIT. |
| **T2 / T1** — POST-AUDIT → RED → GREEN separados | AUDIT aprobado y contrato de §4.1 → tests existentes actualizados, nuevos RED y producto v2; los consumen los tres CLI y T3. | Promesa B: PC-04–07; PC-09 pertinente. POST-AUDIT aplica solo cambios auditados con trazabilidad PD-12 y verifica todos los tests declarados intactos; distingue su evidencia de los actualizados. Otro dispatch RED añade las pruebas conductuales nuevas con controles válidos; otro GREEN implementa y verifica matriz, frontera histórica, ubicación y rechazos sin efectos. |
| **T3 / T2** — RED → GREEN separados | Contexto y validación de T2 → `render --route C` conforme a §4.2; lo consume el orquestador para despachar. | Promesa A: PC-01–02 y diagnósticos PC-09. Verificar identificación determinista, binding publicado, rechazo v1 y paquete íntegro; asignar aquí PC-08a como regresión existente (canónico, cuerpo alterado, CRLF y fronteras de preámbulo), sin fabricar RED. Mantener render completo predeterminado y controles positivos. |
| **T4 / T3** — RED pertinente → GREEN separados | Interfaces verificadas → fuentes coherentes y agentes regenerados; los consumen ambos runtimes y T5. | PC-03, PC-07b, PC-08b, PC-09 documental, PC-10–12. Checks mecánicos pertinentes antes de GREEN; revisión semántica independiente posterior. `make agents` genera los derivados; no se parchean manualmente. |
| **T5 / T4** — subfases separadas | Producto generado y pruebas protegidas → evidencia de invariantes y recorrido instalado; la consume T6. | PROPERTIES e INTEGRATION/E2E en encargos distintos. Generadores solo para invariantes verificables, sembrados y acotados; reutilizar cobertura suficiente. Consumidor aislado: preparar v2 → emitir C → resolver y validar contexto. La auditoría de relevancia corresponde obligatoriamente a T6, no a POST-AUDIT. |
| **T6 / T5** — revisión y cierre separados | Evidencia completa → revisión, aceptación y actualización aprobada del Memory Bank; consumidor: Pablo. | Revisión independiente contra todas las promesas y límites, incluida obligatoriamente la auditoría test↔promesa/PC por el reviewer de Stage 4, en sesión distinta de quien escribió los tests (`stage-3-tdd.md:45-47,270`); correcciones por el rol competente. El responsable del cierre ejecuta la suite completa conforme al paquete y registra evidencia. Scribe devuelve borrador; aprobación y materialización siguen separadas. |

Las pruebas focales y regresiones se ejecutan con selección proporcional, no con una suite completa por despacho. Cada resultado registra comando, salida, revisión del árbol y efectos observados. Un fallo de fixture o importación no acredita RED.

Prevalece la unidad por invocación de `sources/roles/orchestrator.md:126-131`: no copiar la combinación POST-AUDIT+RED de `handoff-prompts.md:220-225,334,347` ni de `packets/substages/test-writer-post-audit.md:1`. Un render que aún combine subfases se devuelve al orquestador para resolver la contradicción antes de despachar; no se parchean sus bytes.

## T1: alcance inmediato

**Lecturas:** contrato aprobado y tests pertinentes, sin fuentes de implementación. Los contratos documentales necesarios deben llegar como entradas expresas del paquete del test-writer.

**Ediciones del rol:** ninguna. **Crear por materialización del orquestador:** `docs/specs/010-004-packet-dispatch-ergonomics/test-audit.md`.

El informe debe:

1. Inventariar las pruebas afectadas, distinguiendo expectativas vigentes de las sustituidas por PC-04. Como puntos de partida verificados:
   - `tests/test_004_002_t6_landing.py::test_pd12_legacy_without_policy_keeps_legacy_intake`;
   - `tests/test_packet_prepare.py::test_p2_default_execution_context_and_out_dir_under_project_cdad`.
2. Trazar cada actualización histórica: expectativa anterior → `004-002` PD-12 → decisión owner → `010-004` §7/PC-04. La spec histórica queda intacta; el test-writer actualiza expectativas en POST-AUDIT aprobado, antes del dispatch RED separado, no el implementer ni el cierre.
3. Separar **PC-08a, regresión existente**, de **PC-08b, instrucciones nuevas revisables**. Reutilizar controles de cuerpo alterado y CRLF; no fabricar un RED para una garantía ya verde. Las referencias iniciales son `test_role_packet_render.py:350` y `test_role_packet_review_regressions.py:468`.
4. Declarar selección focal, regresiones, controles positivos, comandos y límites de evidencia para la siguiente tanda.

**Gate:** el orquestador comprueba trazabilidad y registra la consecuencia de usuario exigida por R4 para cada prueba seleccionada (`sources/roles/orchestrator.md:274-281`). Antes de POST-AUDIT exige aprobación de Pablo del AUDIT o un mandato explícito vigente que autorice aprobar ese informe, verificado y citado. La delegación operativa de `execution.md:25-33` y un precedente no bastan: no hay autoaprobación; sin autoridad inequívoca se solicita decisión a Pablo (`packets/substages/test-writer-audit.md:1`). No hay cuota por PC ni variantes equivalentes obligatorias; tampoco se difiere una promesa comprometida.

## Superficies previstas

Tras el AUDIT, cada paquete concreta su alcance:

- **T2–T3, Modify:** `skills/cdad-cycle/scripts/cdad_packet.py`. El wrapper `scripts/cdad_packet.py` conserva su función de entrada.
- **POST-AUDIT, Test:** solo cambios aprobados en tests existentes bajo `tests/`, con evidencia separada de actualizados e intactos. **RED, Test:** nuevas pruebas conductuales necesarias bajo `tests/`, en otro dispatch; no se fijan nombres especulativos antes del inventario.
- **T4, Modify:** `sources/roles/{architect,orchestrator}.md`, `sources/agents/adapters/{opencode,claude-code}.md` y las referencias pertinentes de handoff, preparación y re-entry.
- **T4, Generate:** `build/staging/`, `agents/` y `agents/claude-code/`, mediante los entrypoints de `Makefile:10-18`.

El consumidor de T5 utiliza una raíz de instalación aislada y el CLI instalado, no el wrapper del checkout como sustituto. Se controlan `HOME`, `CDAD_INSTALL_ROOT` y destinos extra; no se actualiza la instalación global.

## Gates de aceptación

- Todas las promesas tienen evidencia trazada, distinguiendo comportamiento mecánico de revisión de instrucciones.
- La revisión de PC-07b comprueba requisitos por rol y límites reales; no inventa migración ni una salida CLI inexistente.
- PC-08a mantiene las fronteras de preámbulo; PC-08b no se presenta como prueba de obediencia del modelo.
- PC-10–11 conservan I-4/I-5: falta de observabilidad no obliga por sí sola a repetir; divergencia conocida no se rescata cambiando a C.
- Se elige **T4 como gate transversal anticipado**, tras consolidar renderer T2–T3 y staging T4 y antes de T5 (`stage-3-tdd.md:61-79`). Su paquete solicita explícitamente la suite completa al responsable de integración; T2–T3 usan focales y regresiones proporcionales. Se agrupan esos disparadores, no se exige full por unidad ni por subfase. T6 conserva la suite de cierre por su responsable; solo se cita una corrida registrada en vez de repetirla si se demuestra equivalencia conforme a `re-entry.md:157-167`. Entry point verificado: `python3 scripts/cdad-suite.py close --all --evidence-root <directorio-autorizado>`.
- Revisión independiente, aceptación funcional y aprobación del Memory Bank no se sustituyen por tests verdes, recibos ni materialización.

## Incertidumbres y deferred-hardening

N-4/N-5/N-6 permanecen **OPTIONAL abiertos/postergados**. No se introduce precedencia diagnóstica ni interpretación legacy nueva. Si el AUDIT demuestra ambigüedad funcional, se detiene esa expectativa y se escala al owner con evidencia; no se elige silenciosamente una solución.

Se mantienen las exclusiones de `spec.md:513-524`: no se añaden benchmarks, negociación entre instalaciones antiguas, exportación independiente del prompt, conectores ni unificación de preámbulos. Ninguna exclusión aplaza una promesa aprobada.

```plan-tasks
{
  "validation_strategy": "AUDIT aprobado; POST-AUDIT, RED y GREEN en tres dispatches separados; detalle y regresiones explicitos en paquetes sin --plan-task para planned; focales proporcionales; suite anticipada en T4 por renderer/staging y gate de cierre T6 conforme a equivalencia registrada; relevancia independiente obligatoria en T6; consumidor instalado aislado.",
  "tasks": [
    {
      "id": "T1",
      "detail": "next",
      "depends_on": [],
      "parallel": [],
      "files": [],
      "observable_checks": [
        "Inventario test-promesa-PC y comandos focales reproducibles",
        "Sustitucion historica PD-12 trazada sin modificar la spec historica",
        "PC-08a existente separada de PC-08b y ambiguedades funcionales escaladas"
      ],
      "regressions": [],
      "integration_gate": "Orquestador valida trazabilidad y R4; Pablo aprueba el AUDIT o se verifica mandato explicito vigente para aprobarlo antes de POST-AUDIT",
      "owner": "test-writer AUDIT read-only; orquestador materializa y valida; Pablo aprueba salvo mandato explicito verificado"
    },
    {
      "id": "T2",
      "detail": "planned",
      "objective": "Cerrar PC-04 a PC-07 y PC-09 pertinente: contexto explicito, resolucion compartida y preparacion nueva v2; POST-AUDIT, RED y GREEN separados",
      "depends_on": ["T1"],
      "uncertainty": "Inventario completo de expectativas y fixtures afectados",
      "owner": "test-writer POST-AUDIT y test-writer RED en sesiones separadas; implementer GREEN; orquestador valida gates",
      "resolves_when": "AUDIT aprobado y paquete detallado sin --plan-task, con archivos, pruebas, regresiones y gates trazados"
    },
    {
      "id": "T3",
      "detail": "planned",
      "objective": "Cerrar PC-01 y PC-02 y diagnosticos pertinentes mediante emision C publicada v2-only; verificar PC-08a existente sin RED artificial; RED nuevo y GREEN separados",
      "depends_on": ["T2"],
      "uncertainty": "Seleccion focal reutilizable tras el cambio de contexto",
      "owner": "test-writer RED; implementer GREEN; orquestador valida gates",
      "resolves_when": "T2 validada y tanda C detallada conforme al AUDIT y al contrato de spec seccion 4.2"
    },
    {
      "id": "T4",
      "detail": "planned",
      "objective": "Cerrar instrucciones PC-03, PC-07b, PC-08b, PC-09 documental y PC-10 a PC-12; regenerar ambos runtimes",
      "depends_on": ["T3"],
      "uncertainty": "Referencias y comprobaciones mecanicas afectadas segun AUDIT",
      "owner": "test-writer RED pertinente; implementer GREEN; reviewer revisa semantica",
      "resolves_when": "Interfaces T2 y T3 verificadas y superficies exactas delimitadas para la tanda"
    },
    {
      "id": "T5",
      "detail": "planned",
      "objective": "Acreditar invariantes aplicables y PC-12 instalado en subfases separadas; relevancia independiente obligatoria en T6",
      "depends_on": ["T4"],
      "uncertainty": "Cobertura reutilizable y raiz aislada autorizada para el recorrido instalado",
      "owner": "test-writer PROPERTIES y test-writer E2E mediante sesiones y paquetes separados",
      "resolves_when": "Producto regenerado, gate anticipado T4 verificado y seleccion acotada de invariantes y recorrido instalado declarados"
    },
    {
      "id": "T6",
      "detail": "planned",
      "objective": "Completar revision independiente, suite de cierre, aceptacion y Memory Bank sin presuponer aprobaciones",
      "depends_on": ["T5"],
      "uncertainty": "Hallazgos de revision y evidencia final del arbol",
      "owner": "reviewer Stage 4 audita obligatoriamente relevancia en sesion distinta del autor de tests; responsable del cierre; scribe; orquestador; Pablo, cada uno en su cometido",
      "resolves_when": "Evidencia T1 a T5 completa y paquetes separados de revision y cierre preparados conforme a gates"
    }
  ]
}
```

---

**Evidencia histórica no normativa del encargo anterior**

- Ruta C validada: identificación concordante, REQUEST válido, digest del contrato correcto y `PACKET.md` completo byte-idéntico a `cdad_packet.py render`.
- Método: Python `3.13.5`, comparación en memoria, sin temporales.
- `sha256sum docs/specs/010-004-packet-dispatch-ergonomics/spec.md` confirmó el pin indicado.
- `git rev-parse HEAD`: `a892fc26b7794f63d226ea7d5a0a4772cd17066c`, sin cambios entre comprobaciones.
- `git diff --exit-code` y `git diff --cached --exit-code`: satisfactorios, sin salida.
- Archivos modificados: ninguno. Commit creado: ninguno. El único untracked observado, `docs/specs/010-000-continuity-relative-root/discovery.md`, quedó intacto.
- Comandos exactos y salidas de validación, render, comparación, ayuda CLI y git constan en las llamadas de herramientas. Dos consultas a rutas inexistentes no aportaron evidencia.
- No ejecuté tests, generación, instalación ni suite. Esta validación acredita los archivos publicados, no una exportación independiente del mensaje recibido.