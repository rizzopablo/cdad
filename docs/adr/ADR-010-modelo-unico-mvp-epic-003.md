# ADR-010: excepción acotada de modelo único para el MVP del epic 003

- **Status:** Accepted — aprobado por Codex (agent-delegated) el 2026-09-17, por delegación explícita del usuario para el epic 003.
- **Date:** 2026-09-16
- **Deciders:** usuario responsable del epic (modelo único); Codex con HITL delegado (alcance operativo y vencimiento)
- **Relación:** excepción temporal al requisito de diversidad de modelos de ADR-001; no reemplaza sus demás decisiones ni las excepciones existentes de ADR-007.

## Contexto

El usuario decidió usar el mismo modelo para todos los roles del MVP de
eficiencia. Se priorizan contratos, aislamiento de sesiones y continuidad,
evitando comparaciones costosas entre modelos. La diversidad figura como
invariante en skills y documentos: omitirla sin declarar el alcance produce
instrucciones contradictorias y puede extender la relajación a otros trabajos.

El validador actual compara identificadores de modelos en perfiles con modelos
fijos; no demuestra diversidad de familias en ejecución. El perfil `basic`
ya omite esa comprobación conforme a ADR-007. Por tanto, no siempre es necesario
modificar el guard para compartir modelo, pero `basic` por sí solo no delimita
esta decisión por epic, runtime o vigencia.

## Opciones

- Mantener diversidad obligatoria: conserva la política original, pero no
  responde a la decisión del usuario para este MVP.
- Eliminar el requisito globalmente: excede el alcance acordado.
- Declarar una excepción acotada y verificable: opción elegida.

## Decisión y alcance

Permitir un único modelo en todos los roles, incluido orquestador y reviewer,
para las ejecuciones del **epic-003-context-efficiency en OpenCode**, incluidas
validaciones en desarrollos reales expresamente vinculadas a ese MVP.

La ejecución debe identificar epic, runtime, modelo efectivo y autoridad que
habilita la excepción. La pertenencia se registra explícitamente: compartir
máquina, carpeta de instalación o perfil no extiende la autorización. Una
validación en otro proyecto no habilita el modo para todo ese proyecto.

**Construcción en Codex (ampliación aprobada):** el usuario seleccionó
`gpt-5.6-sol` para los subagentes de este epic. Aplicar esa selección a todos
los roles delegados con contexto nuevo; el orquestador conserva el modelo de
su sesión actual. Extender la excepción reviewer/implementer a esta ejecución
de construcción, con el mismo vencimiento y restricciones, sin afirmar que
padre e hijos usan el mismo modelo. La selección de modelo está indicada por
el usuario; el alcance queda aprobado mediante el mandato registrado en el epic.

**Inicio:** activación del epic aprobado y configuración explícita de la
ejecución correspondiente. Este ADR no activa el epic ni cambia instalaciones.

**Vencimiento:** el primero de estos eventos: cierre del epic, cancelación del
epic o revocación del usuario. Una ejecución fuera del alcance tampoco puede
invocar la excepción. Reanudar una sesión no renueva la autorización.

Al vencer, no iniciar nuevas operaciones amparadas en esta excepción; conservar
el checkpoint si queda trabajo pendiente y resolver la configuración aplicable.
Rige la política previa del entorno, incluidas las excepciones documentadas de
ADR-007. Extender el alcance o vigencia requiere una decisión explícita nueva;
el siguiente epic no hereda esta autorización.

## Garantías que permanecen

- Spec y contratos verificables, aprobaciones y autoridad delegada.
- Sesiones separadas, permisos por rol y test-writer sin implementación.
- Auditoría test↔postcondición por otra sesión y review con juicio propio.
- Evidencia vigente, gates y tratamiento de bloqueos.

No se afirma independencia estadística entre ejecuciones del mismo modelo ni
equivalencia demostrada con una configuración de familias distintas.

## Aplicación y verificación

La feature `003-001-role-packets` debe hacer coherentes las instrucciones,
handoffs y validadores aplicables con esta excepción. Reutilizar mecanismos
existentes cuando alcancen; no eliminar globalmente el guard ni desactivar
controles de permisos, evidencia o aislamiento.

La verificación debe cubrir aceptación dentro del alcance y rechazo del uso de
esta excepción fuera de epic/runtime, después del vencimiento y al intentar
heredarla en otra ejecución. Registrar cuándo se aplica y qué modelo se usó;
ningún resultado debe atribuir diversidad de familias a una corrida de modelo
único. Estos controles están pendientes de implementación, no se presentan como
garantías ya desplegadas.

## Consecuencias

La configuración se simplifica y la excepción queda trazable. Se acepta la
ausencia de diversidad de modelos durante el MVP; se mantienen sus demás
controles. El costo adicional es resolver y verificar alcance y vigencia en
la primera entrega, sin construir un sistema general de autorizaciones.

## Referencias

- [Plan del MVP](../epics/epic-003-context-efficiency/plan.md).
- [ADR-001: modelos por etapa](ADR-001-modelos-por-etapa.md).
- [ADR-007: perfiles y excepción basic](ADR-007-perfiles-de-modelos.md).
- [Validador actual](../../scripts/validate-subagents.sh).
