# Inventario de capacidades CDAD para preparar follow-ups inspirados en Superlite

Snapshot de checkout `83a897f` (2026-10-19). Describe fuentes locales, no certifica instalación, adopción global ni conducta de todos los runtimes. “Código” significa que hay implementación en el checkout; “regla” es procedimiento documentado y requiere observar aplicación para acreditar conducta. Ver también [ideas transferibles](../../../findings/superlite-transferable-ideas-2026-10-19.md), [propuesta de epics](plan.md) y [prueba de escritorio sobre decisiones activas](tabletop-active-decisions.md). El tabletop se limita a 006-004 en cola: no altera su contrato.

| Idea / capacidad | Estado en este snapshot | Fuentes | Delta útil / límite |
|---|---|---|---|
| Descomposición de epic | Regla implementada: plan ligero enumera features, orden, dependencias y criterios; aprobación y transición son gates del proceso. | `skills/cdad-epic/references/epic-planning.md:1-18, 108-125` | No confundir roadmap de epic con plan técnico detallado de cada feature. |
| Tamaño, contrato de dependencias y detalle progresivo | Regla definida para features complejas: unidad cierra resultado propio; tareas declaran archivos, Consumes/Produces y verificación; detalle profundo sólo para lote siguiente. | `skills/cdad-cycle/references/stage-2-specification.md:98-146` | Contrastar cuánto se aplica de forma consistente y qué evidencia muestra dependencias reales; no duplicar el formato. |
| Revisión previa de spec/plan | Parcial: CLI, kind, pairing y materialización `plan-review` ya existen. La enmienda 006 del plan está aprobada; su feature 006-006 sigue `queued`. | `docs/epics/epic-006-opencode-concurrency/plan.md:328-352`; `docs/.cdad-state.json:4-14`; `docs/epics/epic-006-opencode-concurrency/proposal-006-006-spec-plan-review.md:75-100` | Separar disponibilidad mecánica de integración al flujo, y ambas de eficacia observada en una revisión real. |
| Aislamiento test-writer / implementer / reviewer | Reglas de roles, paquetes y revisión separada están documentadas; no prueba por sí sola que cada runtime las cumpla. | `skills/cdad-cycle/SKILL.md:65-85`; `skills/cdad-cycle/references/stage-3-tdd.md:77-85`; `skills/cdad-cycle/references/stage-4-review.md:1-21` | Evidencia debe venir de entregas/re-entry de uso real, no de repetir normas. |
| Continuidad | La instrucción del orquestador exige `begin` antes del despacho y `checkpoint` al cerrar unidad; la referencia describe la CLI como opcional y dice que no se invoca automáticamente. | `skills/cdad-cycle/SKILL.md:264-266, 463`; `skills/cdad-cycle/references/continuity.md:1-23, 28-44` | Separar la obligación operativa escrita de la disponibilidad/ejecución de la herramienta. |
| Medición de contexto | Herramienta read-only implementada, explícitamente manual y fuera de gates. | `skills/cdad-cycle/references/context-meter.md:1-14, 61-80` | Métricas observadas, proxies estimados y desconocidos son categorías distintas; no exigir telemetría para mejorar proceso. |
| Dispatch, recibos y validación mecánica | CLI/adaptadores, paquetes, registro de despacho y recibos tienen implementación; existen reportes de operación y fricciones pendientes. | `skills/cdad-cycle/references/cli-delegation.md:27-50, 403-423`; `docs/epics/epic-006-opencode-concurrency/execution.md:156-163, 196-202` | Investigar fallos de recorrido concretos; no diseñar otro bus, recibo o checkpoint sin evidencia de necesidad. |
| Concurrencia y propiedad de archivos | Reglas: paralelizar sólo tareas independientes con contratos; mismo archivo/estado va serial o por ondas; state lo escribe el orquestador. Worktree es opción según runtime, no capacidad universal. | `skills/cdad-cycle/references/stage-3-tdd.md:125-152` | Diferenciar instrucciones de enforcement automático y de aislamiento ofrecido por cada entorno. |
| Epic-006 y delegación OpenCode | En desarrollo: 006-005 es activa; 006-004 y 006-006 siguen en cola según el estado del checkout. | `docs/.cdad-state.json:4-14`; `docs/epics/epic-006-opencode-concurrency/execution.md` | Tratar implementaciones/evidencias de este epic como trabajo en curso hasta reconciliar estado y cierre. |

## Límites para follow-ups

No duplicar en un ciclo nuevo el contrato Consumes/Produces, detalle progresivo, checkpoint/resume, recibos, revisión proporcional ni la política de ownership: ya tienen fuente canónica. Para cada propuesta, identificar primero qué código existe, qué regla está escrita, qué está en desarrollo (especialmente 006-005) y qué evidencia falta. La oportunidad más plausible es una **clasificación formal y compacta de dependencias entre tareas**, con su contrato y evidencia de revisión/uso: confirmar si el plan actual la expresa suficientemente antes de proponer formato o maquinaria nuevos. No convertir ausencia de medición en cero, ni usar desarrollo ya completado como benchmark.

No comparar familias de modelos ni imponer perfiles: dentro del runtime rige su configuración; en delegación externa, la configuración de CDAD. Ver `docs/adr/ADR-033-modelos-por-configuracion-sin-perfiles.md:1-8, 40-44`.

Este inventario no afirma qué capacidades están desplegadas globalmente. Tampoco convierte una propuesta, una skill o una prueba de CLI en evidencia de que un orquestador futuro aplicará la conducta.

## Adenda 2026-10-21 — capacidades del sistema y consumo de evidencia

La fotografía anterior se conserva como histórica: su estado de features y
números de línea no representan automáticamente el checkout o despliegue actual.
Por instrucción del dueño, [S-SYS-01](../../../findings/system-capability-planning-evidence-2026-10-21.md)
y los antecedentes enlazados son **entrada necesaria** de la continuación
propuesta en [el plan](plan.md), primero en A1–A3. No se activa trabajo por ello.

| Dimensión | Qué existe o se observó | Brecha a evaluar |
|---|---|---|
| Capacidades consumibles | Stage 2 ya exige resultado con consumidor, `Consumes/Produces` y comprobaciones; el caso documenta decisiones implementadas sin la acción operativa necesaria. | Hacer que las dependencias y el criterio de cierre distingan trabajo parcial y capacidad integrada; no repetir la frase en otra fuente. |
| Recorrido operativo | El consumidor elaboró una referencia con actores, identidades, estado, configuración y uso. | Considerar esos encuentros temprano en el epic y la feature, con profundidad proporcional; no convertir un documento en garantía de aplicación. |
| Revisión previa | En el checkout revisado el procedimiento de Stage 2 ya contiene revisión independiente de spec/plan. | Reconciliar la implementación y evidencia de 006-006 al iniciar. Revisar supuestos del sistema, sin confiar sólo en consistencia interna de documentos. |
| Transferencia de aprendizaje | El caso registra conocimiento experimental que no llegó al artefacto consumido. | Fuente, vigencia, consumidor y evidencia de incorporación; no confundir una nota o ADR registrado con capacidad del producto. |
| Evidencia y éxito | Instrumentos locales aportaron resultados parciales; un rechazo permanente podía cumplir una implicación defensiva. | Diferenciar decisión, ejecución, integración y uso; exigir evidencia adecuada del resultado positivo cuando el contrato lo pide. |
| Entorno y continuidad | Propuesta incremental y antecedentes de laboratorio persistente ya documentados. | Coordinar A/B con esa propuesta, sin una tercera iniciativa ni reconstrucciones rituales. |

El marco de estas mejoras es **contratos, garantías y evidencia**. Los tests de
código son instrumentos posibles; porcentajes de cobertura o cantidad de tests
no acreditan las obligaciones del sistema. No se altera retrospectivamente el
vocabulario de fuentes históricas ni el contrato del trabajo activo.
