---
epic_id: epic-018-orchestrator-start
epic_name: Arranque directo y verificable del orquestador
created_at: 2026-11-12
approved_by: Pablo
approved_at: 2026-11-12
---

<!-- cdad:plan-anchors
{"history": ["Cambios al plan"], "authorization": ["Autoridad"]}
-->

# Epic 018: Arranque directo y verificable del orquestador

## Resumen y alcance

Reducir la fricción observada al iniciar un ciclo CDAD mediante la conexión de
la orientación compacta existente, instrucciones coherentes, ayudas accionables
y ejemplos ejecutables, preservando autoridad, continuidad y separación de roles.

Entra el diseño aprobado y revisado «Arranque CDAD directo y verificable», con
las precisiones de su revisión independiente; la enmienda de ADR-021 ya fue
aprobada por Pablo y registrada en `0c83f2dd`. Las tareas T1–T4 forman una
única unidad de entrega: entrada y encargo coherentes (T1), ayudas y diagnósticos
(T2), ejemplos y captura fiables (T3), revisión y ensayo (T4).

No entran un nuevo framework, macro de despacho, cambios de modelos o políticas,
reapertura de epics cerrados ni publicación o despliegue sin autorización. La
documentación orienta al modelo, pero no garantiza sus lecturas ni su latencia.

## Features

| # | Feature | Resultado | Depende de |
|---|---|---|---|
| 1 | `018-001-orchestrator-start` | Ejecutar T1–T4 del diseño aprobado: entrada compacta, ayudas CLI, ejemplos verificables y ensayo independiente | ADR-021 enmendada |

## Criterios de aceptación

- La especificación de la unidad expresa las promesas y las precisiones de
  revisión sin omitir restricciones del diseño aprobado.
- La entrada diferencia proyecto reconocido, procedencia conocida, legacy,
  reposo y trabajo activo, sin convertir `status` en autorización.
- Las ayudas y ejemplos cubren las operaciones y errores identificados; las
  condiciones de reemplazo y retirada no se debilitan.
- Un caso sintético protegido comprueba la transmisión del encargo y detecta
  la omisión intencional de un requisito; la evidencia conserva códigos y bytes.
- Revisión independiente, pruebas proporcionales, integridad del inventario y
  evidencia de cierre según la política vigente; el ensayo de arranque declara
  entorno, mediciones y límites, sin prometer latencia.
- Las cuatro tareas se completan sin desplegar ni modificar modelos o permisos.

## Autoridad

Pablo aprobó el diseño y autorizó dar de alta una unidad nueva para ejecutar
T1–T4. El mandato operativo y sus límites constan en `execution.md`. La
aprobación del plan no equivale por sí sola a una aprobación de especificación,
priorización de revisión, Memory Bank, publicación o despliegue.

## Cambios al plan

- 2026-11-12 — Alta de la unidad nueva por instrucción de Pablo, sin reabrir
  las unidades históricas de epics cerrados.

Status: Approved by Pablo on 2026-11-12.
