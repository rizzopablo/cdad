---
epic_id: epic-015-dispatch-reception
epic_name: Recepción de despachos contra fuentes congeladas
created_at: 2026-11-02
approved_by: Pablo
approved_at: 2026-11-02
---

<!-- cdad:plan-anchors
{"history": ["Cambios al plan"], "authorization": ["Autoridad"]}
-->

# Epic 015: Recepción de despachos contra fuentes congeladas

## Resumen

`record-dispatch`/`receive` rechazan con «packet differs from the canonical rendering» (008-004 PC-03) cuando las
fuentes de instrucciones cambian entre `prepare` y `receive`: la unidad que edita `packets/common.md` o fuentes de
rol (pasó en 014-001 GREEN-002, cerrado con `withdraw` pese a haberse despachado y entregado), commits concurrentes
o redespliegue a mitad de unidad. La recepción compara contra el árbol vivo en vez de contra lo despachado.

Fix: validar contra los sha256 congelados en `REQUEST.json` (`instruction_sources`) y el `PACKET.md` publicado, no
re-renderizar desde el árbol vivo. De paso: mensajes de error con el formato esperado, choque `docs=docs` vs
referencias `contract`, y `open-unit` que abre unidades queued de epics cerrados (abrió 013-004).

Insumo: todo del proyecto `0efea826` («CDAD: fix de recepción de despachos», pedido por Pablo 2026-11-02).

## Alcance

Entra:
- Recepción/`record-dispatch` contra fuentes congeladas (REQUEST.json + PACKET.md publicado).
- Diagnósticos accionables en formatos cerrados (observación de despacho, `decisions` de `begin`, `--write-scope`).
- Regla `docs=docs` vs referencias `contract` (008-004 PC-06): resolución o guía sin reescribir contratos cerrados.
- `open-unit` salta unidades queued de epics cerrados.

No entra:
- Trazabilidad contrato→test ni revisión de suite por tramos (epic posterior).
- Reescribir contratos cerrados (005-013, 008-002, 008-006, 013-*, 014-*).
- Publicar y desplegar (reservado al dueño).

## Features

| # | Feature | Resultado | Depende de |
|---|---|---|---|
| 1 | `015-001-frozen-reception` | `record-dispatch`/`receive` aceptan el paquete despachado aunque las fuentes vivas cambien; oráculo anclado a `instruction_sources` + PACKET.md | — |
| 2 | `015-002-intake-guards` | Formatos cerrados con diagnóstico del formato esperado; `docs=docs` vs `contract` resuelto o guiado; `open-unit` ignora queued de epics cerrados | 1 |
| 3 | `015-003-closed-set-oracle` | Corrige el único rojo de la suite completa de cierre: el oráculo de conjunto cerrado de 010-002 no admite el campo `instruction_sources` que 015-001 añadió al request | 1 |

## Criterios de aceptación del epic

- Una unidad que edita sus propias fuentes de instrucciones (p. ej. `packets/common.md`) se despacha, entrega y recibe sin `withdraw` forzado.
- Commits concurrentes sobre fuentes entre `prepare` y `receive` no rompen la recepción del paquete ya despachado.
- `make agents` reproducible; doctrina sin deriva.
- Cierre del epic con suite completa (gate atribuible).

## Autoridad

Aprueba el dueño: «De acuerdo, adelante» (2026-11-02) + mandato HITL «Todo salvo publicar». Publicar y desplegar
reservados al dueño.

## Cambios al plan

- 2026-11-03: la suite completa de cierre (1966 passed, 1 failed, 5 skipped; commit 8acccc41) mostró una regresión de
  015-001: `tests/test_010_002_documentary_role_properties.py::TestInv04Properties::test_publication_conserves_the_admitted_request_and_render_fields`
  exige que el request publicado solo crezca con `agent`/`execution_context`. Se añade la feature 3; la suite se repite.
  Aprobado por HITL delegada.
