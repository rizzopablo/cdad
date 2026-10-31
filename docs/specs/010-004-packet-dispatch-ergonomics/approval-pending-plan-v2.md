# 010-004 — plan v2: aprobación del owner pendiente

Estado operativo: **plan-pending-owner-approval**. Este documento **no aprueba nada** y no autoriza tests ni implementación: prepara una decisión del owner.

## Qué se pide aprobar exactamente

Objeto y digest:

- `docs/specs/010-004-packet-dispatch-ergonomics/plan.md`
- SHA-256 `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685` (plan_version 2)
- Spec compañera ya aprobada (no se reabre): `spec.md` `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`

La aprobación pedida es sobre **ese digest exacto**, no sobre una versión futura del plan.

## Revisión independiente que la antecede

- `implementation-plan-review-v2.md` (FINAL TEXT de `cdad-reviewer`, sesión `<session>`), recibido en `.cdad/runtime/results/exec-010-004-packet-dispatch-ergonomics-001/010-004-packet-dispatch-ergonomics-reviewer-plan-review-007/receipt.json` (`a6c8f466…`), recibo `semantic_status: pending`.
- Dictamen: **0 BLOCKING, 1 OPTIONAL (V2-1)**. P-1 cerrado en todas sus condiciones; P-2, P-3 y P-4 tratados y cerrados. N-4/N-5/N-6 siguen abiertos y postergados, sin cambios.
- La revisión `implementation-plan-review.md` (v1) se conserva sin modificar.

## Lo que debe saber quien apruebe (implicación explícita)

Aprobar el plan v2 **tal como está** implica aprobar una **parada conocida en T2**:

- T1 queda libre.
- T2 se detendrá con certeza en su primer despacho POST-AUDIT, porque la plantilla `packets/substages/test-writer-post-audit.md` vigente combina POST-AUDIT **y** RED en una sola invocación, y eso contradice la regla de una subfase por invocación (`spec.md` INV-01).
- La parada es segura y no acredita ningún bypass: el plan prohíbe parchear bytes y devuelve la decisión al owner. El coste es una decisión más.

Aprobar v2 sin resolver V2-1 = aprobar esa parada. Si el owner quiere evitar la parada, debe decidir la vía de POST-AUDIT **junto con** la aprobación.

## V2-1 — opciones de vía (decisión del owner)

| Opción | Qué implica | Coste |
|---|---|---|
| **a) Modificar la plantilla post-audit y su generación, como parte de T4/T2, autorizando un despacho mono-subfase** | La plantilla y su generación dejan de combinar POST-AUDIT + RED; T2 avanza en un solo despacho. Acotado a plantilla y generación, con trazabilidad de hash. | Amplía el alcance del producto en una plantilla de despacho; exige revisar la redacción y no debe ampliar promesas de la spec. |
| **b) Despachar POST-AUDIT solo tras revisar contrato/plantilla en otra unidad** | Se abre una unidad acotada para revisar la vía antes de T2. | Añade una unidad y desplaza T2; no toca la plantilla sin aprobación. |
| **c) Mantener la parada y decidir al llegar** | T2 se detiene en su primer despacho; el owner decide entonces con el contexto del AUDIT ya aprobado. | Ningún producto extra; una decisión diferida. |

**Recomendación (conservadora, no vinculante):** **(a) acotada a la plantilla y su generación**, con trazabilidad explícita y sin ampliar las promesas de la spec. Es la única opción que elimina la parada sin crear una unidad nueva ni dejar el ciclo abierto; su riesgo —tocar una superficie de despacho— queda contenido si el cambio se limita a separar POST-AUDIT de RED y se revisa por el mismo cauce.

## Estado mientras no haya decisión

- Sin aprobación del plan: **no se inicia T1**, no se prepara packet de test-writer, no se ejecuta audit/RED/GREEN, no se toca `plan.md` ni la plantilla.
- No se abre ningún loop nuevo de architect/reviewer por V2-1.
- Nada de lo registrado (recibo, materialización, transición) acredita aprobación.

Siguiente acción: el owner aprueba el digest `2ae8ada3…` (con o sin decisión V2-1). Con la aprobación registrada, el ciclo puede abrir T1.
