# Mandato de orquestación — epic-010-documentary-specialization

## Fuente y aprobación

El usuario indicó «Listo, avanza como orquestador» y aprobó el plan presentado
con «Aprobado» el 2026-10-29 en esta sesión. El alcance aprobado está en
`docs/epics/epic-010-documentary-specialization/plan.md`.

## Alcance delegado

epic-010-documentary-specialization: registrar el plan aprobado y sus features,
preparar y delegar encargos por rol, verificar gates con evidencia, materializar
resultados de roles read-only y ejecutar git de documentación/estado. Incluye
Discovery de 010-001-documentary-contracts. No hereda mandatos de otras épicas.

Las specs, cambios de alcance, priorización estratégica de reviews, aceptación
funcional y Memory Bank requieren aprobación de Pablo. Esta delegación operativa
no autoriza al orquestador a aprobarlos en su nombre. No hay push, publicación ni
modificación de instalaciones globales autorizados por este mandato.

Vigencia: hasta cierre, cancelación o revocación de esta épica.

## Ampliación explícita del mandato — 2026-10-29

Pablo solicita: «Te delego hitl, eres el dueño del proceso. Continúa orquestando
proactivamente hasta completar las correcciones pendientes y el epic completo».
Se registra la instrucción como mandato de continuidad operativa para las cuatro
features, empezando por 010-000, y la integración y cierre de la épica. No se
relajan severidades, aislamiento, pruebas previas ni evidencia. El orquestador
continúa dentro del contrato vigente: esta instrucción no convierte una recepción
en aprobación ni permite autoaprobar lo que sus instrucciones superiores reservan
al usuario. Cambios reales de alcance y publicación se elevan al dueño. No se
hereda autoridad de otras épicas ni se autorizan cambios de modelos.

## Entrada operativa

La vista compacta inicial informa reposo y DRIFT solo en project. El primer
`republish-agents` rechazó sin republicar: el contexto conservado de 009-002 no
coincide con active_feature null. Se registra la nueva iniciativa y se utiliza
`prepare --new-execution`, que es la vía canónica para reemplazar el contexto de
una iniciativa cerrada; no se modifica ese contexto anterior a mano.
