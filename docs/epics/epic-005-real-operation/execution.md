# Ejecución del epic 005

## Mandato y aprobación — 2026-10-08

Se le pidió al dueño, en una misma solicitud, (1) aprobar `plan.md` y (2)
confirmar la delegación propuesta. Respondió: «ok» (Pablo, 2026-10-08).

**Delegado:** orquestador OpenCode (agente `cdad-orchestrator`).

**Alcance:** epic-005-real-operation. Aprueba specs y planes de sus features,
prioriza reviews, valida gates y aprueba los cambios del Memory Bank con
evidencia. La severidad de los defectos no se relaja.

**Vencimiento:** al cerrar, cancelar o revocar el epic. No se hereda a otros
epics ni proviene de delegaciones anteriores.

**Publicación:** sin push automático.

**Reservado al dueño, siempre:**
- activar versiones en el repo real;
- cambios en HOME (`~/.claude`, `~/.agents`, `~/.config/opencode`);
- la confianza de carpeta de Claude Code;
- cambios de alcance o de criterios de aceptación del epic.

## Excepción: 005-010 orquestada por Claude — 2026-10-11

Propuesta al dueño: un ciclo correctivo de 005-009 orquestado por Claude, porque
el recorrido a probar tiene a Claude como coordinador, con los roles despachados a
OpenCode. Respondió: «ok: a» (Pablo, 2026-10-11).

**Delegado para 005-010-real-opencode-delegation:** Claude (sesión de Claude Code
en este repo), con el mismo alcance y las mismas reservas que la delegación del
epic. Mientras dure, el orquestador OpenCode no opera este repo: un solo escritor
del state. Al cerrar 005-010, el resto del epic vuelve al orquestador OpenCode.

**Operación:** el ciclo usa la versión instalada al empezar (`6f4d5db`), nunca el
CLI del repo; los roles corren en OpenCode con los modelos de la sección
Operación del plan; el reviewer es de otra familia que el implementer. La prueba
real se hace en una instalación aislada; el despliegue lo decide el dueño.

**Reapertura por B1 — 2026-10-11.** La verificación posterior de Codex
(`docs/specs/005-010-real-opencode-delegation/review-codex-2026-10-11.md`)
encontró B1. El dueño aprobó corregirla con el mismo esquema («Si, adelante») y
delegó la HITL en Claude por unas horas. Alcance: RED y GREEN focales de B1, con
la versión instalada `c9f4810`. El despliegue espera a que el otro proyecto activo esté en reposo.
Al cerrar B1, la orquestación vuelve al orquestador OpenCode para 005-002.

## Criterio de review vigente — 2026-10-12

Aprobado por el dueño («De acuerdo, adelante») a partir de la verificación de Codex sobre
005-002. Reemplaza el criterio «lo que no rompe el camino feliz va a deuda»:

- **Se bloquea y corrige ya** lo que compromete el resultado, la evidencia o el uso previsto de la
  feature. Por ejemplo, un valor desconocido informado como 0, un límite publicado que no se
  cumple, o una ausencia que no distingue «no ocurrió» de «no reconocido».
- **Va a deuda priorizada** lo que es una mejora o variante sin impacto material.

**Reapertura de 005-002 — 2026-10-12.** Corrección acotada del medidor bajo este criterio. La
orquesta el orquestador OpenCode; el orquestador Claude revisa al cerrar.

**Reapertura de 005-003 por F2 — 2026-10-13.** El dueño aprobó el cambio de contrato
(«Si»). La corrección la orquesta Claude con el mismo esquema que B1 de 005-010; al cerrarla,
el epic vuelve al orquestador OpenCode. El dueño autorizó desplegar con el otro proyecto activo en reposo.

## Pendientes para el cierre del epic — 2026-10-13

- **Saneamiento antes de publicar (gate de cierre).** En 2026-10-13, 76 archivos versionados
  contenían rutas personales absolutas o ids crudos de sesión, entre ellos `docs/.cdad-state.json`
  y logs de evidencia. No bloquea mientras el repo no se publique, pero el epic no se cierra hacia
  un repo público sin un barrido: placeholders (`<home>`, `<repo>`, `<tmp>`, `<ses-…>`) y el mapa
  de ids en `.cdad/local/`. Ya se corrigieron `005-007/acceptance.md` y `005-004/discovery.md`.
  Regla para los encargos: no escribir rutas absolutas del dueño ni ids crudos en documentos
  versionados.
  **Hecho en el contenido actual (2026-10-14, orquestador Claude):** `a367b8c` (rutas e ids en 76
  archivos, 4 renombrados) y `29a4805` (nombres de otros proyectos en 14 archivos), con un barrido
  determinista e idempotente fuera del repo. `validate-state` VALID; suite con el barrido (sobre `e0bd96c`,
  antes del focal de 005-014): 1024 passed / 4 skipped. Esto explica la diferencia de 4 con la corrida
  del cierre del epic (1028, que `closure.md` declara sin explicar). A3 queda solo con falsos positivos del patrón local no acotado (lo acota el dueño).
  **Historial (decisión del dueño, 2026-10-14):** antes de publicar se publica con **historial nuevo**;
  el historial actual no se publica.
- **Despliegue (2026-10-14, autorizado por el dueño, el otro proyecto activo en reposo).** HOME en
  `29a4805` (005-012, 005-013, 005-014 y el saneamiento); `install.sh --check` PASS. Recorrido con el
  CLI instalado: repetir el cierre de 005-014 sobre este repo → no-op, rc=0, state intacto. El
  `status` marca la pierna del proyecto como DRIFT (agentes derivados de la versión anterior): lo
  resuelve el próximo `prepare`.
- **Entrada y transiciones (propuesta de enmienda pendiente de aprobación del dueño).** La medición
  D-1 de 005-007 (`acceptance.md` §7) atribuye el gasto previo al primer despacho a la entrada al
  proceso, no al registro posterior. Propuesta: dos unidades correctivas, primero la entrada común y
  después el registro de transiciones.
  **RESUELTO (2026-10-14):** el dueño aprobó la enmienda y las dos unidades se implementaron y
  cerraron. La **entrada común** es `005-011-common-entry` (cerrada el 2026-10-14) y el **registro de
  transiciones** es `005-012-transition-registration` (cerrada el 2026-10-14); la enmienda del plan
  sumó además `005-013-unit-contract` y `005-014-closure-replay` (unidad correctiva del uso previsto
  de 005-012). Registro: `plan.md` filas 11–14 y «Cambios al plan»; `epic_history`. La nota original
  se conserva: describe la propuesta, no el estado.
- **Mejora futura, sin unidad ni prioridad (decisión del dueño, 2026-10-13).** Un adaptador
  `cdad_delegate` → Claude Code: `claude -p --agent cdad-<rol>`, con el paquete por stdin y
  `--output-format json`. Antes de usarlo hay que verificar el aislamiento del test-writer bajo
  `-p --agent` (hooks o reglas de permiso por ruta); si no se verifica, el adaptador falla cerrado.
  Coincide con D-3 de `005-004/spec.md`.
- **Insumos para la planificación siguiente (review de Codex, 2026-10-14; sin unidad ni sha del plan
  hasta que 005-013 permita editarlo sin invalidar trabajo en curso).**
  - **005-012 (alcance):** el cierre debe comprobar las entregas requeridas y sus aprobaciones antes de
    aplicar la transición, y ofrecer una salida explícita para registrar una entrega tardía sin reabrir
    ni aprobar automáticamente una feature cerrada. Caso real: el scribe de 005-011 (`closure.md`,
    precisión posterior).
    **RESUELTO (2026-10-14):** lo entregó `005-012-transition-registration` (el cierre comprueba las
    entregas requeridas y la aprobación vigente **antes** de aplicar, y ofrece la salida
    `receive --late` + `--transition late-delivery`). Evidencia: su `closure.md`, `acceptance.md`
    (AC-1..AC-4).
  - **Candidata — adopción de versión entre ciclos (RD-a de 005-011):** cada proyecto adopta una versión
    elegida entre ciclos, prepara y comprueba sus derivados antes de abrir la sesión; nada de republicar
    todos los proyectos en cada despliegue.
  - **Candidata — estado operativo compacto con historia durable (RD-b de 005-011):** al cierre de 005-011
    el state pesa ~530 KB, ~486 KB en `stage_history`. Separar el estado operativo acotado de un historial
    que puede crecer, conservando accesibles las autorizaciones vigentes (hoy el CLI las busca en
    `stage_history`), contratos, trabajo pendiente y la evidencia para reconciliar una interrupción.
  - Las dos candidatas se miden con los próximos desarrollos reales, no con sondas sintéticas.
  - **ABIERTAS al cierre (2026-10-14):** las dos candidatas (RD-a, RD-b) y la condición de medición son
    **prioridades de la planificación siguiente** en `closure.md` §Planificación siguiente, no unidades
    de este epic. La condición que las difería («sin sha del plan hasta que 005-013 permita editarlo»)
    quedó resuelta al cerrar `005-013-unit-contract`.

## Reconciliación documental al cierre — 2026-10-14

Notas vencidas actualizadas para que el próximo agente no reconstruya decisiones ya tomadas. **No se
reescribe la historia:** cada nota original se conserva y se marca qué quedó resuelto y dónde.

| Nota del epic | Estado al cierre | Dónde quedó registrado |
|---|---|---|
| «Entrada y transiciones» — propuesta pendiente del dueño (2026-10-13) | **Resuelto**: la entrada común es 005-011 y el registro de transiciones es 005-012, más 005-013 y 005-014 | §«Pendientes para el cierre», marcado en su lugar; `plan.md` filas 11–14; `epic_history` |
| «Insumos para la planificación siguiente» — alcance de 005-012 | **Resuelto** por 005-012 (comprueba antes de aplicar; salida `receive --late` + `late-delivery`) | `specs/005-012-transition-registration/{closure,acceptance}.md` |
| «Insumos…» — candidatas RD-a y RD-b | **Abiertas**: son las prioridades de la planificación siguiente, no unidades del epic | `closure.md` §Planificación siguiente; `specs/005-011-common-entry/debt.md` |
| «Mejora futura»: adaptador `cdad_delegate` → Claude Code (2026-10-13) | **Abierta**, sin unidad ni prioridad (decisión del dueño); coincide con D-3 de 005-004 | Esta sección; `specs/005-004-claude-code-roles/spec.md` |
| «Saneamiento antes de publicar» (2026-10-13) | **Hecho en el contenido** (`a367b8c`, `29a4805`); A3 queda con falsos positivos del patrón local no acotado, que acota el dueño; el historial privado se conserva y no se publica | `closure.md` §Finalización y publicación |
| «Despliegue» (2026-10-14) | **Hecho**: HOME en `29a4805`, `install.sh --check` PASS, recorrido instalado no-op rc=0; la pierna del proyecto sigue en DRIFT hasta el próximo `prepare` | `closure.md` §Versión de referencia |
| `docs/runtime-adopted-version.md` declaraba `35062b0` | **Actualizado** a `29a4805` (despliegue del 2026-10-14) | `docs/runtime-adopted-version.md` |
| Criterio 5 del epic (aceptación conjunta del consumidor) | **No ejecutado**: depende del dueño del consumidor («el otro proyecto activo») y se registra así, sin convertirlo en verde | `closure.md` §Criterios de aceptación |

El cierre del epic queda consolidado en `closure.md`. Lo que **no** cierra este epic (publicación con
historial nuevo, aceptación conjunta del consumidor, prioridades de la planificación siguiente) está
declarado ahí, no resuelto por omisión.
