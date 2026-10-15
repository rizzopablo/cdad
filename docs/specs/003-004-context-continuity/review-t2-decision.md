# Decisión del orquestador sobre review-t2 (2026-10-07)

Sin bloqueantes duros. Se cierran antes de T3 en un ciclo corto de review-fix, porque son baratos y protegen T4:

- **A:** `expired-authority` sigue siendo la clasificación dominante, pero el envelope agrega `signals` con el estado del receipt, de la materialización y del dispatch. Los `unknowns` se preservan siempre. Test: autoridad vencida + receipt + materialización → `signals` lo reporta; rc 0.
- **B (tratado como requerido, por coherencia con B1 de T1):** ningún render de `resume`, frío o caliente, reclama `continuity-checkpoint-v1`.
  - El render declara solo `record: active-record-v1`.
  - El arranque en frío (sin head) devuelve un envelope que valida contra su schema, o un estado explícito `no-checkpoint`.
  - Test con `jsonschema.validate` o, si no hay dependencia, con aserciones de forma.
- **C:** `--packet` y `update.packet_id` pasan por la validación de segmento seguro. `--packet "../../x"` → rc≠0.
- **D:** `fsync` del archivo y del directorio en `_write_synced`, como en `cdad_result.py`. Se verifica por lectura en la re-review, sin test de crash.
- **E1:** `decision` no vacía.
- **E2:** un focal de `reconcile` para cadena rota, referencia inexistente y digest de referencia alterado.
- **E3:** se mantiene la pauta: el state se commitea solo en commits `chore` del orquestador.
- **F1/F2:** FYI. Se documentan en `references/continuity.md` (T3).
- **Validadores F011 / A3:** son preexistentes y ajenos a 003-004. Se tratan al cierre.
