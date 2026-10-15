> Materializado por el orquestador desde `architect-draft-001.md` (architect,
> `mofgw/deepseek-v4.1-flash`), verbatim salvo links relativos. Aprobado por el
> dueño el 2026-10-05; decisiones D1–D7 en
> [owner-decisions-2026-10-05.md](owner-decisions-2026-10-05.md).

## Spec — 004-003-planning-procedures

**Feature ID:** `004-003-planning-procedures` · **Epic:** `epic-004-single-source-planning` · **Estado:** aprobada (2026-10-05). ADR-011 gobierna autoridad, capacidades y límites.

### 1. Descripción funcional

004-003 convierte el contrato de planificación (`planning-contract-draft.md`) y los requisitos de orquestación proporcional (`efficient-orchestration-requirements.md`) en **procedimientos de los roles existentes**, instalados y consumibles, con soporte explícito de contrato para revisar un objeto **borrador** de plan. No crea un planner, una plataforma de métricas ni un caché; edita fuentes canónicas y deriva consumidores de modo que no existan copias competidoras de una regla (fuente editable única + derivación coherente).

Se añaden dos superficies: (a) un procedimiento de **revisión de plan** (el reviewer revisa intención + restricciones + plan, no solo la spec), y (b) un procedimiento de **validación/re-entry** que permite que un resultado completo verificable satisfaga controles consecutivos implementer→orquestador→reviewer **sin tres corridas completas equivalentes** cuando se establece la equivalencia de árbol/política/entorno.

El **recorrido real de aceptación** es este repositorio: el procedimiento se ejercita para replanificar el trabajo pendiente de 003-002, registrando el dictamen y los cambios concretos, sin reimplementar 003-002.

Quedan fuera: agente/planner nuevo; plataforma de métricas, caché universal o restricciones por comando; subsistema de recepción de 003-002, detección de estancamiento de 003-003, renovación de contexto de 003-004; rediseño de entorno limpio de Odoo; migración de contextos v1 (D2 de 004-002).

### 2. Contrato

**Interfaces propuestas para implementar, no existentes:**

| Superficie | Comportamiento |
|---|---|
| Paquete de revisión de plan (subfase `plan-review` en reviewer) | `prepare` renderiza intención + restricciones + el objeto plan + su **versión/identidad** y una referencia de **no aprobación**; el reviewer devuelve hallazgos + dictamen; la aprobación queda separada. |
| Contract-kind para un objeto borrador | Un `contract_kind` distinto (p. ej. `draft-plan`) con `authority_ref` (quién pidió la revisión) y una **versión de plan** declarada. Falsificar `approved-*` queda prohibido. |
| Chequeo de equivalencia en re-entry | Comparación declarada y basada en evidencia (versión del producto, versión de tests incl. cambios sin commitear, selección ejecutada, comando, resultado, entorno/config/dependencias, disponibilidad del original) que acepta citar una corrida previa o exige una nueva. |
| Plan de validación por unidad en el archivo de plan | Cada tarea declara pruebas focales, regresiones afectadas, gate de integración y quién ejecuta cada comprobación; puede referenciar una estrategia común del proyecto. Los ciclos sin código declaran comprobaciones observables adecuadas al artefacto. |

**Postcondiciones:**

1. **PD-1 — La revisión de un plan borrador es un contrato de primera clase y no aprueba.** `prepare` puede renderizar un paquete de reviewer cuyo objeto de contrato es un plan **borrador** con su versión y una referencia de autoridad, sin marcarlo `approved`; la emisión lleva el sha/versión del borrador, no una aprobación. Reutilizar `approved-*` para pasar el guard se detecta y se rechaza. *(Reemplaza el enum de dos tipos en `cdad_packet.py:50,700-704,869-882` y `active-packet.schema.json:16`.)*

2. **PD-2 — La revisión es independiente y semántica.** El reviewer recibe intención original + restricciones + plan (no solo la spec), en una sesión distinta de la del autor. La validación estructural (esquema/referencias/reglas) y el juicio semántico se separan: un plan con todos los campos puede ser rechazado igualmente; una checklist no certifica optimalidad. Solo hallazgos con confianza ≥80%; aplican el verdict-tuple y las abstenciones.

3. **PD-3 — La revisión de plan no autoaprueba alcance.** Revisar ≠ aprobar. Artefacto revisado, referencia de autorización y estado de aprobación permanecen separados. Un cambio de frontera/autoridad/contrato va al dueño; un reordenamiento válido o un detalle de implementación permitido no exige re-aprobación completa.

4. **PD-4 — Es procedimiento, no un agente nuevo.** La revisión de plan corre sobre el rol reviewer existente; no se crea un planner permanente ni un sub-agente nuevo. Es invocable desde el producto **instalado** sin leer todo el repo fuente ni convertir el borrador en aprobado.

5. **PD-5 — Validación proporcionada, sin corridas completas duplicadas.** Dado un resultado completo verificable, el mismo árbol/política/entorno puede satisfacer a implementer, orquestador y reviewer con la evidencia registrada citada (ruta+línea+commit), no tres suites completas. La equivalencia registrada cubre versión del producto, versión de tests incl. cambios sin commitear, selección, comando, resultado, entorno/config/dependencias y disponibilidad del original; un cambio de contrato compartido o incertidumbre de entorno fuerza las comprobaciones afectadas.

6. **PD-6 — Se exige una corrida nueva cuando la equivalencia falla.** Si el árbol cambió materialmente, la política/snapshot divergió o el entorno no puede mostrarse equivalente, las comprobaciones afectadas se re-ejecutan antes del cierre; la incertidumbre se declara, no se asume. El mismo commit por sí solo ≠ entorno equivalente.

7. **PD-7 — Focal vs transversal se tratan distinto.** Una corrección local usa pruebas focales; un cambio de contrato compartido o de impacto incierto amplía. El procedimiento no trata ambos casos como idénticos.

8. **PD-8 — El plan de validación por unidad es parte del plan.** Cada tarea declara pruebas focales, regresiones afectadas, gate de integración y responsable de ejecutar; el trabajo sin código declara comprobaciones observables adecuadas al artefacto, sin inventar una suite de software. Puede referenciar una estrategia común una vez.

9. **PD-9 — Encargos suficientes, no exhaustivos.** Un paquete lleva objetivo útil, contrato+versión, entradas pertinentes, alcance, decisiones autónomas, estrategia de validación, salida esperada y disparadores de retorno; referencia fuentes precisas y permite lecturas del alcance del rol; **no** copia historial ni carga toda la metodología; los logs completos quedan fuera del contexto activo. Los paquetes no deben pedir lecturas que la política niega.

10. **PD-10 — Intervención por falta de progreso.** Un reintento responde a una hipótesis o información nueva; repetición idéntica, ausencia de avance, obstáculo del entorno o costo desproporcionado disparan revisión de estrategia, reconciliada con la regla vigente de dos intentos — sin reintentos ilimitados. Ningún límite autoriza saltar controles ni declarar éxito sin evidencia.

11. **PD-11 — Paridad procedimental entre stacks (generalidad).** El procedimiento sirve a Python (`tests/`), a **tests co-ubicados de Go** (`*_test.go`) y a **ciclos sin código** (docs/config/multimedia). Un ciclo sin código produce una comprobación observable adecuada al artefacto, no una suite de código fabricada.

12. **PD-12 — Instalado, fuente única, sin copias competidoras.** El procedimiento llega a la instalación (`skills/` + paquetes + `sources/` + agentes generados) y cada regla tiene una fuente editable con consumidores derivados; sin edición manual de salidas generadas. Las fuentes de rol existentes conservan su propiedad; sin un segundo manual por rol.

13. **PD-13 — Recorrido real sobre 003-002.** El procedimiento se ejercita sobre el trabajo pendiente de 003-002; se registran dictamen y cambios concretos; 003-002 no se reimplementa aquí. Recibo mecánico y aprobación de calidad permanecen distintos (problema de 003-002).

### 3. Invariantes verificables

1. `prepare` sigue siendo el **único** productor de paquetes; sin productor paralelo, sin parchear a mano un paquete rechazado.
2. Aprobación, recibo mecánico y cumplimiento semántico permanecen distintos; la revisión nunca autoaprueba alcance.
3. Anti-sesgo: familia del reviewer ≠ familia del implementer; el test-writer nunca ve implementación; el mapeo test↔postcondición lo audita otra sesión.
4. Fronteras de rol sin cambios; la revisión de plan **no** concede permiso de implementación.
5. Bash sigue permisiva; mapas/hooks no son sandbox para procesos lanzados (ADR-012).
6. Una fuente editable por regla; las salidas generadas nunca se editan a mano.
7. UNKNOWN permanece explícito; las métricas ausentes no se fabrican.

### 4. Criterios de aceptación

1. PD-1–PD-13 trazadas a pruebas de comportamiento; los casos negativos verifican que no se fabrica una aprobación y que no se produce un paquete para un contrato no soportado.
2. Un plan borrador se revisa **sin** volverse aprobado, desde una sesión distinta de la del autor, sobre producto instalado.
3. Fixtures de un plan con entrada sin productor, dependencia circular, contrato incompatible y paralelismo inválido ejercitan los **checks realmente implementados**; un esquema no decide la calidad semántica.
4. La regla de equivalencia se ejercita con al menos un caso de flujo consecutivo donde se cita una corrida previa y uno donde un cambio material fuerza una corrida nueva (PD-5/PD-6).
5. Go co-ubicado y un ciclo sin código tienen cada uno una comprobación observable declarada (PD-11), aunque sea mínima.
6. La sesión de replanificación de 003-002 produce un dictamen registrado y cambios concretos sin reimplementar 003-002 (PD-13).
7. Los validadores pasan; toda aserción o fixture retirada/reemplazada tiene justificación trazada.
8. Las limitaciones aceptadas se declaran; UNKNOWN permanece UNKNOWN.

### 5. Cambios de gates explícitos (para aprobación del dueño) y armonización

Se proponen **cambios de procedimiento, no gates nuevos**, cada uno armonizado con la fuente canónica que lo posee:

| # | Cambio de gate/procedimiento | Fuente canónica que lo posee (edición única) | Consumidores derivados a reconciliar (sin copia nueva) |
|---|---|---|---|
| G1 | El re-entry puede **citar** una corrida registrada cuando se muestra equivalencia de árbol/política/entorno; corrida nueva solo si falla | `skills/cdad-cycle/references/re-entry.md` | `stage-4-review.md` (generaliza la regla solo-reviewer); `SKILL.md` gate 3→4 |
| G2 | "Suite completa una vez por GREEN / suite completa verde" gana la cláusula de equivalencia | `skills/cdad-cycle/references/stage-3-tdd.md` | `SKILL.md` tabla de evidencia |
| G3 | Regla de dos intentos reconciliada con el criterio de información nueva / sin progreso | `SKILL.md` (conducta del orquestador) + `re-entry.md` | `efficient-orchestration-requirements.md:63-69` |
| G4 | Subfase de revisión de plan + contract-kind de borrador | `cdad_packet.py` (`VALID_CONTRACT_KINDS`, `ROLE_SUBSTAGES`, `_contract_for`) + `active-packet.schema.json` + nuevo `packets/substages/reviewer-plan-review.md` | `packets/roles/reviewer.md`; template de reviewer en `handoff-prompts.md` |
| G5 | Campo de plan de validación por unidad en el archivo de plan | `planning-contract-draft.md` §4 y `stage-2-specification.md` | `plan.md` del epic (procedimiento, ya referenciado) |

Regla de propiedad: cada regla se edita **una vez** donde ya vive; las demás superficies la referencian. La fuente del orquestador ya declara supervisión proporcional, así que G1–G3 **hacen ejecutable el procedimiento**, no añaden una segunda política. No se inventa ningún gate nuevo; donde un cambio retira una aserción vieja, se reemplaza por una comprobación de garantía equivalente en el mismo cambio coherente.
