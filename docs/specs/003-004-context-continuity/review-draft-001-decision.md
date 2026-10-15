# Decisión del orquestador sobre review-draft-001 (2026-10-07)

Bajo la delegación HITL del epic 003. Se aceptan todos los hallazgos:
- **BL-1:** la spec final declara D1–D11 como decisiones del orquestador (abajo), no autoaprobadas por el architect.
- **BL-2:** `begin` idempotente. Un cuerpo canónico idéntico al head da no-op (rc 0). Clave de dedupe `(execution_id, packet_id, attempt)`.
- **R1:** sin subcomando `verify-checkpoint`. Tamper/references se verifican en `resume`/`reconcile`. `prev_checkpoint_sha256` se mantiene como campo.
- **R2:** solo `seq`. Cabezas divergentes → escalar (D7 modificada).
- **R3:** sin `budget` propio. El checkpoint embebe un snapshot con `source`; la fuente sigue siendo `cdad_guard budget`.
- **R4:** `--max-bytes`, default 16 KiB, calibrable; falla cerrado sin truncar.
- **R5:** 4 tareas: T1 checkpoint + active record/resume; T2 write-ahead + reconcile + fixtures de la matriz; T3 trigger con unknowns + referencia `continuity.md`; T4 adopción real. 2–3 contratos con nombre.
- **R6, R7, R8, O1, O2, O4:** aplicar. O3: resolver `--allow-stale` en la spec (recomendación: eliminarlo; stale → rc≠0 con delta).
- **D1–D6, D8–D11:** aprobadas según la recomendación del architect. D7, según R2.
