# Decisión del orquestador sobre review-t3 (2026-10-07)

Una ronda, con los patrones que ya usa 002:
- **F1:** `execution_id` y `packet_id` se validan como segmento seguro (la clase `_segment` de 002, sin `..` ni rutas absolutas). Si no pasan: rc≠0, cero escrituras.
- **F2:** el `record` es de creación exclusiva. Si ya existe (packet, attempt, kind), sale con rc≠0 y diagnóstico de conflicto, y los bytes originales quedan intactos. Se eliminan las colisiones de `_slug`: el segmento seguro ya no se slugifica.
- **F3:** `validate_event` se alinea con el schema, en el que `additionalProperties:false` y `action` pertenecen a la tabla cerrada D5. Si una acción de recuperación como `resume-same-session` o `retry` es legítima, se agrega explícitamente a la tabla y se declara en el schema. Lleva un focal que valida un evento válido y uno inválido contra el asset.
- **O1** (se incluye, es barato y es D7): se busca `receipt.json` por nombre.
- **O2** (se incluye, evita retrabajo en T5 y respeta D10): `escalation-v1` lleva `execution_id`, `packet_id` y el fingerprint, para poder derivar el `dedup_key`.
- **O3, O4:** van a deuda baja.

## Re-review y cierre de T3 (2026-10-07)
F1, F2, F3, O1 y O2 quedaron **cerrados**, sin bloqueantes. **T3 cerrada.** Observaciones que se llevan:
- **A1 (para T5):** `execution_id` y `packet_id` son opcionales en el trace, así que la escalada puede emitir `null` y el `dedup_key` debe tolerarlo, o se exigen al grabar. Se decide en T5.
- **FYI:** `budget` con un `execution_id` absoluto lee fuera de la raíz. Es solo lectura y queda en deuda baja.
