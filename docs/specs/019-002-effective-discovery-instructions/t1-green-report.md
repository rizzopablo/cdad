T1 está implementado y commiteado como `3322aaf3`. Los 4 tests focales pasan y las 8 regresiones declaradas también (58 tests en total, sin fallos). No toqué ningún test: `git diff -- tests` queda vacío.

**Qué cambió**
- **Entrega ejecutable (PC-5):** `_allowed_kinds` en `skills/cdad-cycle/scripts/cdad_result.py` admite solo `role-report` para architect/brainstorm. Los kinds de borrador se rechazan en esa subfase y los demás roles no cambian.
- **Roles (PC-1):**
  - `sources/roles/architect.md` redefine el brainstorm como consulta técnica puntual que vuelve al orquestador.
  - `sources/roles/orchestrator.md` suma tres cosas: el diálogo funcional con el dueño, el registro acotado en `discovery.md` (sección Dialogue context) y la excepción única de aprobación. Esta apunta a stage-2 §2.3 en vez de repetirla.
  - Las prohibiciones de rol se mantienen.
- **Registro de decisiones y readiness (PC-2, PC-3):** la sección Dialogue context queda documentada en `stage-1-discovery.md`, `stage-2-specification.md`, `re-entry.md` y `handoff-prompts.md`. `re-entry.md` incluye el chequeo de readiness R1–R5.
- **Revisión independiente (PC-4):** la reentrada del borrador del architect ya no pasa directo a aprobación. Pasa por revisión independiente, o por la exención registrada con sus cuatro campos.
- **Paquetes (PC-1, PC-3):** `packets/roles/architect.md` y `packets/substages/architect-brainstorm.md` describen el viaje de ida y vuelta y el resumen `READY FOR DRAFT`.
- **Consumidores (PC-8, PC-9):**
  - También actualicé `scripts/cdad-generate.py` (la descripción de `ROLE_META`), `skills/odoo-architect/SKILL.md` y `skills/cdad-spec-and-test/SKILL.md`.
  - En `README.md` y `CDAD_metodologia.md` quité el "optional review" y la aislación parcial para trabajo en ciclo normal.
  - Regeneré los agentes con `make agents`: los 6 de `agents/` cambiaron, y `build/staging` está ignorado por git.
- **Paquetes congelados (PC-6):** no reescribí ningún paquete histórico, incluido este. Los paquetes en vuelo siguen con las instrucciones anteriores. Usé el código y los tests de reentrada congelada existentes; `test_015_001` pasa.

**Para el orquestador**
- **Inventario vivo:** `python3 scripts/cdad-suite.py validate` sigue reportando integridad insuficiente. Falta agregar el módulo `tests/test_019_002_discovery_delivery.py` y sus 4 nodeids al inventario. El delta está en `t1-red-report.md`, y esa actualización de `docs/` no entra en mi scope.
- **Fuera del plan:** `skills/cdad-cycle/SKILL.md:69` sigue diciendo "Socratic brainstorm" para el architect. Está en mi scope de escritura pero no en la lista de T1, así que no lo edité. Hace falta decidir si se re-scopea.
- **`make validate`:** falla con 1 assert, `F011: validate-subagents.sh`. Falla igual sin mis cambios.
- **Sin evidencia:** no corrí la suite completa (queda como suite completa no realizada, con la selección de arriba como lo ejecutado). Tampoco hice las rutas observadas PC-4 ni PC-11: son T3. T2 (orientación de reposo) no se tocó.