# Ejecución del epic 003

## Actualización metodológica — 2026-09-24

[ADR-011](../../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md)
establece autonomía supervisada para los próximos contratos. La
[enmienda C0](../epic-004-single-source-planning/c0-amendment-supervised-autonomy-2026-09-24.md)
define el encargo GLM y la transición futura entre epics. Esta actualización
no modifica state, permisos desplegados ni el alcance de las delegaciones.

## Continuación vigente — 2026-09-23

El usuario asigna desarrollo a GLM y análisis profundo/revisión a GPT o Claude.
Consultar el [encargo vigente](../../handoffs/2026-09-23-glm-continuation.md)
y [handoff actual](handoff.md). Se propone preparar primero el epic 004 de
fuente única/bootstrap/planificación; es borrador, no ejecución activa.

Las secciones siguientes conservan el mandato y condiciones de la construcción
inicial. No autorizan automáticamente a GLM como HITL ni extienden ADR-010 al
epic nuevo. El state no se modificó en esta actualización documental.

## Mandato y aprobación — 2026-09-17

El usuario autorizó: «Ok, adelante, orquesta tus agentes cdad, eres el dueño
del proceso, actúa como hitl tomando las mejores decisiones para obtener la
mejor y más efectiva versión de cdad.» Luego indicó continuar.

Codex acepta la delegación para este epic y sus cuatro features: decide alcance,
aprueba specs, prioriza reviews, valida gates y aprueba Memory Bank con evidencia.
La severidad de defectos no se relaja. La delegación vence al cerrar, cancelar
o revocar el epic y no se hereda. No se publica automáticamente.

Plan y ADR-010: aprobados por Codex (agent-delegated) bajo ese pedido. El plan
recoge las prioridades del usuario: contratos, contexto, autonomía durante
horas, validación en trabajo nuevo y ausencia de comparación de modelos.
Estos cambios de metodología son reversibles; no autorizan despliegues en
proyectos ajenos ni alteraciones globales de instalaciones.

## Ejecución y garantías

- Rama de trabajo: `codex/epic-003-context-efficiency`; base `39b48fd`.
- Coordinación epic/feature: misma sesión raíz, con HITL delegado explícito.
- Roles: `gpt-5.6-sol`, sesiones nuevas sin conversación heredada. La raíz
  conserva el modelo del entorno; no se afirma igualdad padre/hijos.
- Aislamiento: sesiones separadas y restricciones conductuales por rol. La
  herramienta nativa no ofrece una política de archivos configurable por hijo;
  no se presenta como sandbox por rol. Debe comprobarse el cumplimiento real.
- La excepción de diversidad es ADR-010; sus verificadores están pendientes.
- No hay CI configurado en la base. La evidencia local se registra por feature;
  el gate de integración del epic debe resolverse explícitamente antes del cierre.
- Métricas no expuestas por el entorno permanecen desconocidas. No se convierten
  tamaños de archivos en tokens ni tiempos observados en ahorros causales.

## Registro

| Feature | Etapa | Evidencia / siguiente acción |
|---|---|---|
| 003-001-role-packets | **Done** (2026-09-18) | Review-4 APROBADO-COMENTARIOS; suite 33/33; validadores PASS en raíz aislada. |
| 003-005-claude-code-packets | **Done** (2026-09-18) | Agregada fuera del plan original: `prepare` + port a Claude Code. Review-2 APROBADO-COMENTARIOS. |
| 003-002-artifact-tools | En cola, drafts persistidos | Base 001/005. Revisar tras la reestructuración propuesta de 004. Discovery/spec/plan son drafts no aprobados bajo `docs/specs/003-002-artifact-tools/`. |
| 003-003-progress-guards | En cola, brief de continuidad | Depende de 001 y 002. Contratos y discovery obligatorio en `remaining-features-handoff.md`. |
| 003-004-context-continuity | En cola, brief de continuidad | Depende de 001, 002 y 003. Contratos y discovery obligatorio en `remaining-features-handoff.md`. |

La aprobación de este plan no equivale a aprobar specs todavía inexistentes
ni a dar por superados gates sin ejecución.

## Observaciones de construcción

Baseline de texto fuente: `cdad-cycle/SKILL.md` 34.700 bytes,
`handoff-prompts.md` 25.324 y agente orquestador 12.881. Son tamaños de archivos,
no contexto efectivo por llamada ni tokens. El límite aprobado para common +
rol + delta es 12.000 bytes por combinación; debe verificarse tras implementar.

Los drafts extensos se devuelven como payloads temporales con hash y el
orquestador materializa el artefacto aprobado. Se evita regenerar su contenido
en el chat. La recepción automática e idempotente sigue pendiente en 002.

CI del repositorio figura en el backlog anterior al epic y es candidata al
desarrollo nuevo de validación. No se ha iniciado ni usado como evidencia de
aceptación del MVP.

Por pedido del usuario, todo handoff actualiza primero `handoff.md` con estado,
commit, rol/modelo delegado, evidencia y próximo paso, para permitir continuar
en otra sesión o runtime sin depender de esta conversación.

## Reactivación — 2026-10-05 (nueva autoridad, no heredada)

Tras el cierre de epic-004, el usuario autorizó en sesión: «reactiva epic-003 y
registra tu mandato de orquestación con criterio HITL para su alcance aprobado. No
heredes silenciosamente delegaciones anteriores.»

| Campo | Valor |
|---|---|
| delegated_to | OpenCode orchestrator (agente `cdad-orchestrator`) |
| requested_by | usuario (Pablo) |
| requested_at | 2026-10-05 |
| scope | epic-003-context-efficiency: alcance del epic aprobado, specs, priorización de reviews, aprobaciones de Memory Bank y gates para sus features pendientes (003-002, 003-003, 003-004) e integración |
| expires | cierre, cancelación o revocación del epic |
| publication | sin push automático |

**No se heredó** la delegación de Codex del snapshot de suspensión (autoridad
distinta, vencida por la suspensión). Se registra como una autorización nueva.

Límites expresos:

- No concede autoridad de publicación ni permisos fuera del alcance del epic.
- No autoriza a modificar instalaciones globales en HOME.
- La aprobación estratégica residual (nuevos alcances, cambios de frontera del
  epic, cierre del epic) sigue siendo del usuario.
- **No se implementan 003-003 ni 003-004 por anticipado.**

Reconciliación y estado de reanudación:
[handoff-resume-2026-10-05.md](handoff-resume-2026-10-05.md).
