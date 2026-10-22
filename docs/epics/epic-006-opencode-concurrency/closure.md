# Epic 006 — cierre

Status: cerrado el 2026-10-22 por el orquestador bajo la delegación HITL amplia del owner, **con AC-7 pendiente del owner** (plan §7: no se acredita aceptación total sin esa comprobación). Desplegado en HOME en `adb7c31`. Sin push (a la orden del owner).

## Resumen

| Feature | Qué deja |
|---|---|
| 006-001 | modo de ejecución explícito (`server`/`service`/`standalone`), preflight, espera proporcional, intento previo que falla cerrado (ADR-031) |
| 006-002 | delegación por capa: cada orquestador declara su mecanismo nativo; la skill queda neutral; el adaptador CLI solo cruza runtimes (ADR-032) |
| 006-003 | modelos por configuración, sin perfiles; instalador de perfil único (ADR-033) |
| 006-005 | paridad del recorrido nativo: correlación verificada, write-ahead y permisos sin la palanca `write` |
| 006-006 | revisión independiente de spec y plan antes del RED, como capacidad de primera clase |
| 006-004 | tabla de decisiones vigentes que viaja en el encargo del rol; principio de general antes que específico (ADR-034) |

Integración entre features: `integration.md`.

## Retrospectiva breve

- **Funcionó:** despachar todos los roles por el adaptador instalado (dogfooding) sacó a la luz defectos reales. Algunos ejemplos: W-1 de 006-006, U6-1..U6-8 de 006-005, B-1 de 006-004. Las reviews de borradores antes del RED cortaron bloqueos caros: 006-004 necesitó 4 rondas, ninguna después de construir.
- **Costó:** la deriva entre la copia de HOME y el repo (F011, agentes personalizados por el owner). Los timeouts y las flakes de la suite bajo carga. Los errores del propio orquestador al despachar a mano (W-U6-2).

## Deuda que se lleva

- **AC-7:** pendiente del owner (ver `integration.md`).
- **006-006:** O-1 (automatizar el selector B/C) y W-2 (rc=0 del adaptador con `blocked`).
- **006-004:** O-1..O-3, W-U6-1 (fidelidad del scribe), W-U6-2 (re-despacho de un paquete ya entregado, a reproducir) y W-U6-3 (el adaptador solo entrega `role-report` hacia el Memory Bank).
- **Heredada:** `scope_validation: unknown` (falta un productor de `observed_changes`); D-U65-4/5; DT-8/DT-9; las flakes de la suite (`test_pd13_no_management_invocations_in_any_mode`, entre otras).
- **F011:** deriva ambiental de la copia instalada.
- **Post-cierre (2026-10-22):** (a) el cuerpo instalado de `cdad-orchestrator` (OpenCode y Claude) dice «consultar la vista `status`» y nombra como CLI instalado sólo `cdad_continuity.py`, que no tiene `status`; la vista vive en `cdad_packet.py status` (sí nombrado en `SKILL.md:252` y `orientation.md` §1). Un agente que no carga el skill antes queda mal orientado. (b) W-2 tiene consumidor real: el envoltorio local de despacho registra el `rc` del adaptador como señal de término. (c) El estado conserva `execution` 006-004, `tdd_substage: red` y `hitl_delegation: active` con el epic cerrado; la delegación termina con el push de epic-006. (d) `status` informa `DRIFT` en la pata `project`; se resuelve con el próximo `prepare`.

## ADR

ADR-031, ADR-032, ADR-033 y ADR-034, todos materializados. No quedan decisiones de arquitectura del epic sin documentar.
