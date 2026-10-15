# Decisión del orquestador sobre review-t1 (2026-10-07)

Review-fix en un ciclo corto (RED → GREEN):
- **B1 (bloqueante):** el render de `resume` declara un id de contrato que su schema rechaza. Se corrige así: el render declara `active-record-v1` y valida contra `active-record.schema.json`. El RED agrega una aserción de validación de schema del render (y del head de `begin`).
- **B2 (requerido; una sola fuente de verdad = la política):** se elimina la heurística del token `impl`. El test-writer mueve el fixture de implementación bajo un root declarado en la política del test, y agrega un control negativo: `docs/impl-decisiones.md` sí es visible para el test-writer. El implementer retira la heurística y corrige el docstring.
- **O2 (barato, se incluye):** `packet_id` debe ser un string no vacío y `attempt` un entero. Si no, rc≠0 con el campo nombrado.
- **O1:** ya planificado para T2 (criterio 3). Debe cerrarse antes de T4.
- **N1:** se documenta que JSON es el único modo; `--json` se mantiene por compatibilidad de firma.
- **F1:** sus límites se declaran en `references/continuity.md` (T3).
- **Gate:** la suite se corre sobre el commit de review-fix (abstención 1).
- **V5:** `resume` no emite un `packet-metric` (sin consumidor en 001). Se registra como no-objetivo.
