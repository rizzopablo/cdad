# Aprobación de spec y plan — 010-002-documentary-role-integration — 2026-10-31

Aprobación del contrato y del plan de la unidad, **ejercida por el orquestador en
nombre de Pablo** bajo el mandato HITL del 2026-10-30
(`docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md`
§1 y §3), que autoriza al orquestador a aprobar los gates operativos del ciclo y
continuar el epic mientras se implemente la descomposición y el alcance ya
aprobados. Esta aprobación **no** publica, no hace push, no actualiza la
instalación global y no cierra el epic.

## Objeto aprobado

| Documento | Versión | SHA-256 |
|---|---|---|
| `docs/specs/010-002-documentary-role-integration/spec.md` | 4 | `0d630c49cfd4c8b0f671026437000617b96bf1bc44b2383dd2914bc7e5581abc` |
| `docs/specs/010-002-documentary-role-integration/plan.md` | 4 | `3ead624c39a2436d6629afa11883f9cbffde885b548bbecff14f8c9500671190` |

El contrato declara 13 postcondiciones (PC-01..PC-13, con PC-12 desdoblada en
12.a y 12.b), ocho invariantes (INV-01..INV-08) y siete evidencias de aceptación
(EV-01..EV-07). El plan declara nueve tareas (T1..T9) con su bloque
`plan-tasks`, RED y GREEN separados y gates por tarea.

## Con qué autoridad y con qué evidencia

1. **Descomposición aprobada.** La unidad es la orden 3 del plan del epic
   (`docs/epics/epic-010-documentary-specialization/plan.md`), con resultado
   observable y dependencia de `010-001` ya satisfecha.
2. **Decisiones del orquestador registradas.**
   `discovery-decisions-2026-10-31.md` fija D-1 (especialización por contrato con
   los agentes existentes), D-2 (aplicabilidad Odoo por producto y por rol), D-3
   (coherencia del destinatario), D-4 (variante no publicada) y D-5 (esquema del
   request), más las precisiones P-1..P-4.
3. **Cuatro pasadas de revisión independiente**, todas con intake de ruta C
   validado y hashes coincidentes:

| Pasada | Objeto | Resultado |
|---|---|---|
| `plan-review.md` | v1 | **Dos bloqueantes**: B1 (aplicabilidad Odoo fuera de los roles que no escriben el producto) y B2 (promesa contradictoria de selección fuera del alcance de T4); más O1..O6. |
| `plan-review-002.md` | v2 | **Sin bloqueantes**; B1 y B2 cerrados, O1..O6 adoptados; N1..N4 nuevos, no bloqueantes. |
| `plan-review-003.md` | v3 | **Un bloqueante nuevo**: B1 (el reemplazo de paquete copiaba el agente del predecesor, contra la garantía por construcción); N5 y N6 no bloqueantes. |
| `plan-review-004.md` | v4 | **Sin bloqueantes**; B1, N5 y N6 cerrados; **recomendación explícita de aprobación**; N7 no bloqueante. |

4. **Resolución de N7, registrada aquí y no oculta.** Un cambio de `stack` sin
   otra obsolescencia deja un paquete `prepared` sin salida directa por
   `--replace-packet` (PD-8 exige obsolescencia) ni por preparación ordinaria (el
   paquete activo publicado la bloquea). Falla cerrado: **ningún trabajo llega a
   un rol equivocado**. Las salidas legítimas son: (i) restituir el `stack`
   vigente al valor que corresponde al encargo; (ii) producir la obsolescencia
   legítima del paquete por cambio de contrato o de política y reemplazarlo
   entonces; (iii) retirar el paquete `prepared` con la clase `withdraw` y volver
   a prepararlo. Este cierre **no** relaja PD-8 ni la comprobación de coherencia, y
   deja el caso declarado en el backlog del epic.

## Criterio de aceptación del contrato

Se aprueba porque el contrato:

- expresa la promesa del epic —«el orquestador puede encargar trabajo documental
  al rol correspondiente por el flujo canónico, sin perder su dominio ni ampliar
  permisos»— sin agregar agentes, campos del estado, etapas ni selectores;
- define la aplicabilidad Odoo **por rol y por diff real**, de modo que un
  encargo documental no queda bloqueado por una batería de addon que no modifica
  y un cambio de addon no se cobija bajo la etiqueta documental;
- cierra la coherencia del destinatario en dos niveles (estático por rol,
  contextual por stack) sin invalidar retrospectivamente un despacho ya hecho, y
  extiende la garantía a las **dos** vías públicas de publicación;
- conserva la compatibilidad histórica de los requests sin `agent` y no promete
  protección mecánica que no existe;
- separa en el cierre la evidencia estructural de la revisión semántica.

## Límites

No autoriza publicar, hacer push ni actualizar la instalación global: la deriva
declarada en `010-001/closure.md` §5 sigue abierta y publicar es decisión del
dueño. No autoriza ampliar permisos por defecto ni tocar el alcance por defecto
del implementer. No cierra el epic: `010-003` sigue pendiente y es donde se
acredita la detección de defectos semánticos en un entregable real.
