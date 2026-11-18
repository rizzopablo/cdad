Corregí el bloqueo de `review-004.md`, y las pruebas focales y los tres packets de prueba salieron bien.

**Qué cambió**
- `skills/cdad-cycle/packets/substages/reviewer-plan-review.md`: la exigencia del `Dialogue context` ya no depende de que la forma principal sea `spec`. Rige para toda revisión que incluya una spec, sea la principal o la acompañante de un plan.
- La instrucción mantiene que, si el input falta o es ilegible, se informa en `## Abstentions` y como hallazgo BLOCKING.
- Un plan sin spec acompañante se revisa sin ese input.
- `skills/cdad-cycle/references/handoff-prompts.md`: documenta la misma regla (principal, acompañante, o plan solo).

**Verificación**
- **Intake ruta C:** la REQUEST y el PACKET coinciden, byte a byte, con el render canónico.
- **Packets nuevos:** los preparé con `cdad_packet.py prepare` en fixtures descartables, sobre copias del repo con las fuentes ya corregidas.

| Caso | rc | Resultado |
|---|---|---|
| spec principal | 0 | Incluye `- docs/specs/f/discovery.md: Dialogue context` y la nueva instrucción |
| plan con spec acompañante (`--spec-path`) | 0 | Incluye el input y la nueva instrucción |
| plan sin spec ni contexto | 0 | Se prepara sin el input y la instrucción lo admite |

- **Pruebas:** las 5 pruebas focales del review pasaron (`30 passed in 19.16s`), y `git diff --check` salió limpio. No corrí la suite completa.
- **Alcance:** no toqué paquetes históricos, tests ni despliegue. `docs/.cdad-state.json` ya estaba modificado y no lo incluí.
- **Commit:** `db42e2e5`.

**Límites**
- Verifiqué lo que dice el packet generado, no el comportamiento de un reviewer real ni un bloqueo automático del CLI.
- Los puntos PC-4, PC-6 y PC-11 del review siguen pendientes y no son de este arreglo.