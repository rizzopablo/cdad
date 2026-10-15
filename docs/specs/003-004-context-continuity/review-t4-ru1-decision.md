# Decisión del orquestador — RU-1 (uso real, 2026-10-07)

Defecto de integración hallado en la adopción real (`continuity-ledger.md` RU-1). Se corrige con un ciclo corto:

- **Identidad:** el CLI acepta el contexto de ejecución real que publica 001 (`.cdad/executions/<id>/execution.json`, con `execution.id`). Conserva compatibilidad con el `execution_id` plano de los fixtures. Si faltan ambos, falla cerrado.
- **Autoridad (D4):** si el contexto no trae `hitl_delegation`, la autoridad se lee de `docs/.cdad-state.json` (`hitl_delegation`), solo de campos estructurados:
  - `revoked_at` presente, o `status` presente y distinto de `active` → `expired`;
  - `expires_on` con una fecha ISO pasada → `expired`;
  - delegación presente con `source` y sin fecha → `active` (vence por eventos y la valida 001 en `prepare`);
  - sin delegación → `unknown`.
  `authority_ref` = `source`. Nunca se parsea prosa.
- **Tests (RED):** un focal con la forma real de 001 y un state con delegación por eventos. `begin` da rc 0; `resume` reporta la autoridad `active` con su `authority_ref`. Con un state revocado, `begin` falla cerrado (D4) y `reconcile` clasifica `expired-authority`.
