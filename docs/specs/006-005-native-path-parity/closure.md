# Cierre de 006-005-native-path-parity

**Feature:** 006-005-native-path-parity · **Epic:** `epic-006-opencode-concurrency` · **Cerrada:** 2026-10-20 · **Contrato:** `spec.md` sha256 `3a824be31e45cd8e6122b7d6f23d3f4d3e6af847ab73f7babef8aa90ce20df01`, `plan.md` aprobados el 2026-10-18 · **Aprobación:** orquestador Claude bajo la HITL delegada del epic-006 (`execution.md`, «Delegación HITL amplia»), con el owner presente y las decisiones de despliegue y orden tomadas por él.

## Qué entrega

- Una entrada operativa única, `cdad_dispatch.py` (`dispatch`/`record`/`capabilities`/`migrate`), con vía externa y vía nativa, y un registro I8 por despacho.
- Correlación por transporte con tres resultados.
- Registro write-ahead con compleción única.
- Kind derivado de rol y subfase.
- Temporal del test-writer escribible.
- Disposición a `failed` por comando.
- Agentes OpenCode sin la palanca `write`, con derivados que no la heredan.
- Barrera del rol por encima de la clasificación de la política.
- Versión del runtime verificada por observación.

## Gates

| Etapa | Evidencia |
|---|---|
| U1a–U7 | RED→GREEN por unidad (`u*-red.md`, `u*-green.md`) |
| U6, recorrido real | `u6-acceptance.md`: E1–E5 y V-11. Hallazgos U6-1..U6-8 corregidos o declarados como deuda; U6-5 por enmienda con dos reviews (`u6-5-decision*.md`) |
| Review | `review.md`: 3 B ⇒ review-fix ⇒ `rereview.md` (B-3 parcial, B-4) ⇒ review-fix 2 ⇒ `rereview2.md`, apta para cierre |
| Suite de cierre | sobre `c58d802`: 1 failed, 1331 passed, 5 skipped. La falla es la flakiness conocida del margen del waiter (`timeout` contra la cota de 2 s del fixture bajo carga concurrente); pasa en aislado |
| Despliegue | HOME en `c58d802`, por orden del owner (`execution.md`) |
| Memory Bank | borradores del scribe (`scribe.md`) aplicados, con una corrección de texto corrupto («sin declaración») |

## Deuda declarada

- U6-2: no hay productor de `observed_changes`, así que `scope_validation` sale `unknown`. El oráculo `passed` de PD-22 queda pendiente.
- O-2: copia global con el coordinador fuera de la raíz.
- D-U65-4 y D-U65-5.
- O-2 y O-3 de las reviews.
- Transporte del paquete nativo con líneas de más de 2000 caracteres.
- Enmiendas al texto de la spec (fila E4, §9, llave proyecto, momento y selección, write-ahead, la barrera del implementer de B-1) registradas en `execution.md` y en los documentos de decisión; el re-pin del texto queda para el próximo cambio de la spec.
