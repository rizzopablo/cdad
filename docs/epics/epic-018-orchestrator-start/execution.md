# Epic 018 — autorización de ejecución

## Decisión del dueño

<owner> aprobó el diseño «Arranque CDAD directo y verificable» y ordenó: «Da de
alta una unidad nueva con autoridad vigente para ejecutar las tareas T1–T4 sin
reabrir el epic cerrado». También aprobó expresamente la enmienda de entrada
compacta de ADR-021, registrada en `0c83f2dd`.

## Mandato operativo

El orquestador puede abrir la nueva unidad, preparar y delegar cada fase a su
rol, materializar resultados, registrar transiciones y verificar la evidencia
necesaria para ejecutar T1–T4 dentro del plan aprobado. El mandato comprende
la coordinación del trabajo, no una delegación genérica de aprobaciones.

<owner> conserva la aprobación de la especificación vinculada a sus bytes, la
priorización de la revisión, la aprobación del Memory Bank, la autorización
del ámbito del ensayo y cualquier publicación o despliegue. La aprobación
del diseño y del alta no se registra como aprobación de una especificación que
todavía no existe. No hay autorización para cambiar modelos ni políticas.

La vigencia corresponde exclusivamente a `epic-018-orchestrator-start` hasta
su cierre, cancelación o revocación. No reabre epics cerrados ni hereda el
mandato vencido del epic 017. Las sesiones y roles conservan sus límites y un
recibo no constituye una aprobación.
