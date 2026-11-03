---
feature_id: 014-001-suite-evidence-defaults
approved_by: Pablo (HITL delegada al orquestador, docs/epics/epic-014-suite-evidence-policy/execution.md)
approved_at: 2026-11-02
source: architect draft (sesión <ses-337>), materializado por el orquestador (ADR-003)
---

# Borrador de spec: 014-001-suite-evidence-defaults

**Estado:** aprobada (2026-11-02, HITL delegada).  
**Producto:** política operativa y consumidores coherentes; no cambio del runner.

## 0. Discovery (base `108bf7743ce2c881c72baed18f7852d39b79046c`)

- La contradicción está localizada: `stage-3-tdd.md:69-75` exige autorización individual incluso al cierre; el plan aprobado autoriza por política la corrida ordinaria de cierre de epic (`docs/epics/epic-014-suite-evidence-policy/plan.md:17-22`).
- No basta cambiar el hogar: paquetes, fuentes de roles, checklists de cierre y documentación Odoo contienen restricciones equivalentes.
- Hay además órdenes de frecuencia incompatibles con la regresión proporcional: `stage-4-review.md:159-163` ordena una corrida completa cuando cambia el árbol; `handoff-prompts.md:701-704` transmite una obligación equivalente.
- El gate existente sirve sin ampliar su interfaz: `scripts/cdad-ci-gate.py:311-313` invoca `cdad-suite.py close --evidence-root … --all`. No existe un subcomando `cdad-ci-gate.py close --all`.
- `Makefile:1-18` declara `sources/` como origen y `make agents` como regeneración para ambos runtimes.
- Los verificadores anteriores contienen expectativas de la política sustituida: `tests/test_005_003_t6_packet_contract.py:648-755` y `tests/test_013_001_criterion_coherence.py:199-230`. AUDIT debe resolverlas explícitamente, sin conservar vocabulario antiguo para satisfacer regex.
- El epic 014 exige una corrida completa atribuible en su propio criterio de aceptación (`plan.md:50-55`). La dispensa genérica nueva no elimina ese compromiso particular sin modificar y aprobar su contrato.

## 1. Objetivo funcional

Que quienes ejecutan CDAD reciban los mismos defaults según el momento del trabajo, tanto por la ruta legacy como mediante paquetes:

| Momento | Default |
|---|---|
| Durante el ciclo | Tests focales y regresión proporcional; sin suite completa como rutina de iteración o depuración. |
| Cierre de feature | Suite completa recomendada. Si se omite, registrar «suite completa no realizada», motivo, selección ejecutada y límites. |
| Cierre de epic | Suite completa obligatoria por defecto. Omitirla requiere dispensa expresa del dueño, registrada con motivo para ese cierre. |

La aprobación de esta política autoriza la corrida ordinaria de cierre de epic; no se exige una nueva autorización individual para esa corrida.

La autorización no equivale a evidencia, ni autoriza publicación, despliegue o reintentos indiscriminados.

## 2. Contrato y fuentes

### Fuentes de aceptación protegidas

- Contrato de unidad validado: `.cdad/packets/014-001-suite-evidence-defaults-architect-draft-001/UNIT-CONTRACT.md`.
- Plan aprobado: `docs/epics/epic-014-suite-evidence-policy/plan.md`, §§ Resumen, Alcance, Criterios de aceptación y Autoridad.
- Propuesta: `docs/planning/test-evidence-and-traceability-proposal-2026-11-02.md`, §3.A, §3bis y §3ter, con las correcciones y exclusiones del plan aprobado.
- Esta especificación, cuando sea aprobada.

La propuesta original no se toma como aprobación de B–D ni de la regularización retroactiva del epic 013.

### Evidencia técnica admitida

Repositorio autorizado, en la revisión indicada en Discovery: consumidores de §5, ADR-041, `Makefile`, generador, gate y verificadores existentes. Estos archivos permiten comprobar el estado previo y las interfaces; su texto previo no sustituye al contrato nuevo como oráculo.

### Producto editable propuesto

- Nuevo ADR bajo `docs/adr/`.
- Los consumidores expresamente enumerados en §5.
- Artefactos derivados de `make agents`.

Propuesta de nombre: `docs/adr/ADR-042-defaults-de-evidencia-por-momento.md`; el orquestador confirmará que el identificador siga disponible al materializar.

Los tests son artefactos exclusivos del test-writer, con alcance delegado propio. El implementer no modifica esta spec, el plan aprobado, sus fuentes de autorización ni los verificadores.

## 3. Decisiones de diseño

1. **Regla general por momento, no excepción para CDAD.** El costo se declara por proyecto; no modifica silenciosamente el default del producto.
2. **Un hogar y consumidores por referencia.** Se modifica `stage-3-tdd.md` §"Test evidence policy"; los consumidores aplican su consecuencia local sin reproducir una doctrina paralela.
3. **Reutilizar atribución existente, no crear otro gate.** La herramienta actual ya conserva intentos, resultados y skips. La suficiencia contractual de esos resultados corresponde al cierre y a la revisión independiente.
4. **Supersesión parcial, no reescritura histórica.** El nuevo ADR sustituye autorización/defaults de ADR-041 y sus consecuencias incompatibles; preserva contribución, propiedades, instalación limpia y atribución.

## 4. Promesas y postcondiciones

### Promesa A — Defaults inequívocos y autorización suficiente

**PC-1.** Un nuevo ADR identifica expresamente qué cláusula de autorización/defaults de ADR-041 sustituye. Conserva las decisiones de contribución, propiedades e instalación limpia; no presenta ADR-039 como íntegramente ratificado ni impone su herramienta a todos los proyectos.

**PC-2.** Existe un único hogar operativo titulado "Test evidence policy" en `skills/cdad-cycle/references/stage-3-tdd.md`. Declara los tres defaults de §1 y distingue recomendación, obligación y dispensa.

**PC-3.** El hogar establece que aprobar la política autoriza la corrida ordinaria de cierre de epic. Ninguna instrucción operativa examinada exige autorización adicional para esa corrida ni permite omitirla por simple ausencia de permiso individual.

**PC-4.** Permanecen vigentes la regresión proporcional, los comandos declarados por proyecto y la referencia a `re-entry.md` §"Equivalence of a registered run". El costo, la disponibilidad del comando o la selección producida por una herramienta no autorizan por sí solos otras corridas.

### Promesa B — Cierres honestos ante resultados incompletos o adversos

**PC-5.** Al cerrar una feature sin suite completa se registra la omisión con motivo, selección ejecutada y límites. Al cerrar un epic sin ella se registra, además, una dispensa expresa recuperable del dueño para ese cierre. Ninguna omisión se etiqueta como suite completa verde o gate ejecutado.

**PC-6.** Un fallo, error o resultado no atribuible impide declarar verde la corrida. El cierre conserva el diagnóstico y la evidencia; la dispensa de ejecutar una suite no transforma una corrida roja en verde ni elimina una promesa incumplida.

**PC-7.** Los skips y resultados esperados no ejecutados satisfactoriamente —incluidos `xfail` cuando corresponda— quedan visibles con motivo y efecto sobre las obligaciones comprometidas. No bloquean por mera existencia, pero sí cuando dejan una promesa comprometida sin verificación suficiente. `rc=0` no demuestra por sí solo suficiencia contractual.

**PC-8.** Una inestabilidad no se resuelve repitiendo hasta obtener verde. Se conservan los intentos; otro intento exige hipótesis o información nueva y respeto al presupuesto. Si no puede acreditarse el resultado, se declara el bloqueo y se escala, sin seleccionar únicamente el intento favorable.

### Promesa C — La política llega coherentemente a todas sus entradas

**PC-9.** Cada superficie de §5 referencia el hogar o su fuente de dominio correspondiente y cumple el resultado local indicado. No contiene restricciones u órdenes operativas que contradigan PC-1–PC-8. El informe de aceptación localiza la comprobación de cada fila, incluso cuando se conserve sin cambios.

**PC-10.** Un paquete nuevo, producido mediante el renderer existente desde la parte común actualizada, transmite los mismos defaults y límites que la ruta legacy. Los assets de rol/subfase no introducen excepciones contradictorias. No se alteran paquetes históricos publicados para simular esa coherencia.

**PC-11.** Los cambios de instrucciones de agentes se realizan en `sources/`, seguidos de `make agents`. Los derivados de ambos runtimes corresponden a esas fuentes; una segunda regeneración no cambia sus bytes. No se editan manualmente para obtener verde.

### Promesa D — Costo y entorno explícitos sin exenciones implícitas

**PC-12.** La norma exige declarar por proyecto: comando focal y completo, entorno, costo conocido con procedencia —o desconocido expresamente—, presupuesto y estrategia de ejecución. Una suite lenta exige resolver presupuesto/entorno o solicitar dispensa cuando sea admisible; no constituye dispensa implícita.

**PC-13.** Sin CI se admite ejecución local atribuible conforme al mecanismo del proyecto. Para CDAD, `docs/ci-gate.md` conserva la interfaz real y los requisitos de atribución del gate existente; no promete flags ni subcomandos nuevos.

**PC-14.** Odoo conserva instalación limpia y amplitud de suite como dimensiones distintas. La política nueva no elimina `test-clean` cuando sea exigible ni impone evidencias de addon a un producto que no lo modifica. Un runner inseparable se evalúa contra la autorización realmente aplicable; si falta, se reporta el bloqueo sin inventar targets ni omitir la instalación.

## 5. Inventario vinculante de consumidores

Todas las filas quedan cubiertas por PC-9; las referencias a otras PC precisan su comprobación.

| Superficie | Resultado local verificable |
|---|---|
| `skills/cdad-cycle/references/stage-3-tdd.md` | PC-2–PC-8 y PC-12–PC-14, también en Run budget y gates internos. |
| `skills/cdad-cycle/SKILL.md` | Flujo, tablas de evidencia y checklist distinguen iteración de cierre de feature. |
| `skills/cdad-cycle/references/handoff-prompts.md` | Handoffs y bloques de presupuesto no ordenan suite completa automática por GREEN, cambio de árbol o review-fix. |
| `skills/cdad-cycle/references/re-entry.md` | Checklists aplican el momento correcto y preservan la equivalencia registrada. |
| `skills/cdad-cycle/references/anti-patterns.md` | Exige evidencia pertinente, sin prohibición universal que alcance el cierre ordinario de epic. |
| `skills/cdad-cycle/references/stage-4-review.md` | Revisión/cambio de árbol exige evidencia proporcional, no una nueva suite completa automática. |
| `skills/cdad-cycle/references/stage-5-merge.md` | Cierre de feature recomendado con omisión motivada; merge no inventa una frecuencia rival. |
| `skills/cdad-cycle/references/state-detection.md` | Detectar estado no dispara una suite completa incondicional. |
| `skills/cdad-cycle/assets/feature-plan-template.md` | `validation_strategy` refleja el default de feature, no la prohibición universal anterior. |
| `skills/cdad-cycle/packets/common.md` | PC-10; distingue autorización por política de necesidad de evidencia real. |
| `sources/roles/implementer.md` | Iteración proporcional; referencias y delta Odoo compatibles. |
| `sources/roles/reviewer.md` | No introduce autorización individual obligatoria para cierre de epic; mantiene instalación limpia y revisión independiente. |
| `sources/roles/orchestrator.md` | Exige los registros de omisión/dispensa y evidencia correspondientes; delta Odoo coherente. |
| `sources/roles/test-writer.md` | Runner y delta Odoo compatibles; selección y contribución no cambian. |
| `skills/cdad-epic/SKILL.md` | Checklist de cierre exige suite completa por defecto o dispensa expresa registrada. |
| `skills/cdad-epic/references/epic-integration.md` | Distingue evidencia de integración del requisito de cierre; no admite omisión por falta de permiso individual. |
| `skills/cdad-epic/references/epic-closure.md` | Procedimiento y checklist implementan PC-3 y PC-5–PC-8. |
| `skills/odoo-make-env/SKILL.md` | Tabla de targets y presupuesto respetan defaults y PC-14, sin cambiar interfaces. |
| `skills/odoo-test-writer/SKILL.md` | Mantiene iteración focal e instalación; no conserva una prohibición universal sobre cierre. |
| `skills/odoo-reviewer/SKILL.md` | Mantiene evidencias de addon sin confundir amplitud con instalación. |
| `skills/odoo-make-env/references/run-budget-protocol.md` | Presupuestos por momento compatibles; no ordena corrida completa por cada review/cambio de árbol. |
| `docs/ci-gate.md` | PC-12–PC-13; autorización suficiente del cierre de epic, sin automatismo por push. |
| `docs/suite-maintenance.md` | `collect-only` sigue sin ejecutar; selección completa se rige por la nueva política, incluida su autorización de cierre. |
| `docs/systemPatterns.md` | Índice y patrones operativos reconocen supersesión parcial; ninguna descripción histórica se presenta como prohibición vigente. |

## 6. Invariantes

- **INV-1:** Se mantienen separación de roles y aprobación del dueño; esta propuesta no se autoaprueba.
- **INV-2:** No se reescriben contratos cerrados de 005-013, 008-002, 008-006 ni 013-*.
- **INV-3:** No hay regularización retroactiva del epic 013.
- **INV-4:** No cambian contribución, disposiciones de tests, POST-AUDIT ni presupuestos de propiedades.
- **INV-5:** No se añade runner, flag, workflow, campo de estado o mecanismo de autorización.
- **INV-6:** No se modifica el significado técnico de verde atribuible; suficiencia semántica y veredicto mecánico permanecen distinguibles.
- **INV-7:** No se publica, instala ni despliega el producto.

## 7. Verificación y aceptación

### Control automático

El test-writer:

- Audita primero los verificadores existentes afectados por la supersesión y propone sus disposiciones.
- Deriva verificadores de esta spec aprobada, agrupados por promesa, no por cantidad de archivos o PC.
- Comprueba estructura, referencias, ausencia de restricciones contradictorias y coherencia de paquetes/derivados.
- Acredita RED pertinente antes de GREEN para el comportamiento nuevo.

No se conserva un oráculo obsoleto ni se altera su contrato histórico: se registra qué expectativa vigente sustituye esta unidad.

### Revisión semántica independiente

El reviewer contrasta todas las filas de §5 contra esta spec y las fuentes aprobadas. Examina especialmente: obligatoria frente a recomendada; autorización por política frente a permiso adicional; dispensa frente a verde; skips e inestables frente a promesas verificadas; instalación limpia frente a amplitud; texto histórico frente a instrucción vigente.

La presencia de palabras o un grep negativo no acredita por sí sola esa coherencia.

### Criterio medible de aceptación

- PC-1–PC-14 acreditadas, con localizador y resultado por cada superficie de §5.
- Sin pendiente bloqueante ni contradicción semántica pendiente.
- Tests focales y regresión pertinente verdes.
- `make agents` reproducible y doctrina sin deriva.
- Diff dentro de los alcances autorizados; contratos históricos protegidos intactos.
- Aprobación funcional del dueño tras la evidencia y revisión independiente.

El cierre de esta feature aplica su default recomendado. El cierre del epic 014 conserva su compromiso específico de suite completa mediante el gate atribuible existente.

### Límites de verificación

Se acredita el producto normativo y su propagación, no que todos los agentes futuros lo obedezcan. No se promete validación operativa de instalaciones desplegadas, disponibilidad de entornos Odoo ni suficiencia de toda la suite histórica.

## 8. deferred-hardening

- Trazabilidad contrato→test y backfill: excluidos expresamente del epic.
- Redundancia, mutación de la suite y poda: requieren otro contrato y presupuesto.
- Despliegue y prueba con agentes instalados: reservados a decisión posterior del dueño.
- Enforcement automático nuevo de dispensa/skips: no se modifica el runner; esta unidad compromete norma, evidencia y revisión.
- Mediciones nuevas en otros proyectos o entornos Odoo: se exige declaración honesta del costo, no ejecutar campañas ajenas para completar esta unidad.

Ninguna exclusión difiere una promesa de PC-1–PC-14.

## Secuencia propuesta

1. Aprobar la spec y efectuar AUDIT de expectativas antiguas afectadas.
2. RED → actualización del hogar, ADR, consumidores y fuentes → regeneración y regresión focal.
3. Revisión independiente → cierre de feature → corrida completa atribuible comprometida para cerrar el epic.

## Evidencia de la intervención del architect

Sesión `<ses-337>`. Archivos modificados: ninguno. Commit: ninguno. Suite completa: no realizada. `validate-request` y `validate-packet` rc=0; render y route C coinciden. Manifiesto de 24 rutas: `d9d071c07656649bfd9d3be59c7556ff0e9d99b42c0cddaed5fe6f9cd80f8bee`.
