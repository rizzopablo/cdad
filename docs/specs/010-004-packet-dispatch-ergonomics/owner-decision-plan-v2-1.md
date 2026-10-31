# Decisión owner V2-1: plantilla POST-AUDIT mono-subfase

2026-10-30 (UTC, reloj del entorno verificado antes de registrar). Autor: **Pablo**. Fuente: instrucción explícita del owner, transmitida por el orquestador supervisor a esta sesión subagente: «Corregir plantilla en el plan», que corresponde a la **opción (a) recomendada** de `approval-pending-plan-v2.md` §V2-1. La misma instrucción aprueba el plan v2 en el digest `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685`.

Esta decisión resuelve el OPTIONAL V2-1 de `implementation-plan-review-v2.md` (0 BLOCKING, 1 OPTIONAL) y acompaña —por referencia— a la aprobación del plan v2. **No edita `plan.md`**: el pin del plan permanece íntegro y la enmienda viaja como decisión del owner, igual que la aprobación de la spec viajó por referencia sobre su digest.

## Decisión

Opción **(a)**: modificar la plantilla post-audit y su generación, como parte de T2/T4, para que exista un despacho POST-AUDIT de **una sola subfase**.

Hoy la plantilla `skills/cdad-cycle/packets/substages/test-writer-post-audit.md` combina POST-AUDIT **y** RED en una sola invocación (`…then add contract-mapped RED tests`), y el renderer compone siempre esa plantilla para el substage `post-audit` (`skills/cdad-cycle/scripts/cdad_packet.py` `render_packet`). Eso contradice INV-01 (`spec.md`) y obliga a una parada segura en el primer despacho de T2. La opción (a) elimina la parada corrigiendo la fuente, sin parchear bytes de paquetes ya renderizados.

## Alcance exacto autorizado

- Modificar `skills/cdad-cycle/packets/substages/test-writer-post-audit.md` para que la instrucción de POST-AUDIT aplique **solo** los cambios aprobados del AUDIT sobre los tests existentes, verifique que los tests declarados intactos siguen pasando y se detenga ahí.
- Ajustar su **generación** —la publicación de la skill instalada (`install.sh`, copias por archivo a los runtimes) y la composición del renderer en cuanto consumidor de la plantilla— en lo que sea necesario para que el paquete POST-AUDIT emitido contenga esa instrucción mono-subfase y no la combinación POST-AUDIT + RED.
- Incluir ese ajuste en **T2** (como paso habilitante antes del dispatch POST-AUDIT que lo consume) y reflejarlo en **T4** en la alineación documental y verificación de instrucciones que corresponda según el plan.
- Mantener trazabilidad de hash de la plantilla modificada y de los paquetes que la rendericen; el cambio se limita a separar POST-AUDIT de RED y a conservar la verificación de tests intactos.

## Qué NO autoriza

- **No cambia las promesas de la spec**: `spec.md` conserva su pin `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`; no se edita.
- **No toca `plan.md`**: conserva su pin `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685`; no se edita ni se re-revisa el plan completo.
- **No añade subfases por invocación**: no autoriza despachar POST-AUDIT + RED juntos; al contrario, el objetivo es que POST-AUDIT sea una subfase única y RED siga en su propio dispatch.
- **No relaja gates**: el AUDIT sigue exigiendo aprobación de Pablo o mandato explícito verificado; RED sigue exigiendo fallo por `AssertionError`; no hay autoaprobación.
- **No amplía el producto** más allá de la plantilla post-audit y su generación; no autoriza implementación nueva en T2/T4 fuera de ese ajuste.
- **No reabre** N-4/N-5/N-6, la tensión plan/observations ni la spec histórica `004-002`; la sustitución PD-12 se traza sin modificar esa spec.
- **No permite parchear bytes** de paquetes ya emitidos; la corrección se hace en la fuente y se publica por el cauce normal.
- **No cambia** autoridad, ejecución ni HITL: la autoridad vigente sigue siendo `docs/epics/epic-010-documentary-specialization/execution.md`.

## Trazabilidad

- Revisión que abre V2-1: `implementation-plan-review-v2.md`, digest `46744d065fdac0bfad1ba0851b1eaae21aac2d65c0511c3b4b573a19379893c2`; packet `010-004-packet-dispatch-ergonomics-reviewer-plan-review-007`; receipt `a6c8f466d77cd5e450f06adfb596a37bb0737d3b5f69b3925326e4e6c44a501a` (`semantic_status: pending`, no acredita aprobación).
- Pregunta y opciones: `approval-pending-plan-v2.md` §V2-1.
- Aprobación del plan: registro de gate 2→3 en `docs/.cdad-state.json`, pinneado al digest del plan, con esta decisión citada como enmienda por referencia.
- Estado operativo mientras se despacha T1: AUDIT abierto; POST-AUDIT y RED **no** preparados todavía.
