# Cierre 007-006-withdraw-and-republish

Fecha: 2026-10-26. Epic: `epic-007-reliable-cycle-operation`. Colección: 5/7.

## Resultado

Un paquete `prepared` que nunca se despachará se retira con motivo y libera `prepare`; los agentes derivados del proyecto se republican sin `prepare`. Ambas cosas dejan de necesitar un rodeo.

- `register-transition --transition withdraw --packet P --note "motivo"`: sólo paquete activo `prepared`, borde de efectos conservador (reutiliza el criterio de reanchor), flags ajenos rechazados, terminal `failed` + entrada `withdraw/withdrawn`, archivos intactos, idempotente por motivo, conflicto rc 1.
- Continuidad del retiro: checkpoint enlazado que conserva evidencia y clasificación; sin `begin`, recibo ni `receipt_checkpoint`.
- `republish-agents --project-root`: publica derivados y manifiesto sin tocar estado/paquetes/política/continuidad; conserva el `model:` instalado; idempotente; falla cerrado; publicación transaccional con rollback.
- `status`: la resolución del DRIFT con única pata `project` nombra `republish-agents`.
- Guarda por unidad suspendida (rc 1) resuelta por la unidad propietaria del paquete.

## Evidencia

- Contrato: `spec.md` + AJ1–AJ4 + notas de implementación.
- Tests: `tests/test_007_006_withdraw_and_republish.py` (61 casos).
- Review: 2 rondas (`ses_e894213beffebC8huMXrjC1Hb8`): ronda 1 NO APTO con 3 bloqueantes (generación parcial en republicación; cuerpo huérfano al fallar la cabeza; guarda AJ1 sobre la unidad activa) → ronda 2 APTO con los tres cerrados y reproducidos.
- **Suite completa (orquestador): 1643 passed, 38 failed — todos del RED de 007-004 (esperados), 5 skipped** (log `.cdad/local/full-007-006.log`).
- Gate por superficie (`dd095bc`): 946 passed, 1 failed (fixture, corregido en `679305d`), 5 skipped.
- `validate-state`: VALID. Specs cerradas 007-001/007-002 byte-idénticas a su aprobación.

## Deudas declaradas

1. La cobertura de PC-13 acredita ausencia de cambios antes del primer reemplazo; el rollback sobrevenido durante los reemplazos está revisado por inspección, no certificado empíricamente.
2. El caso del otro proyecto no se declara «resuelto»: la evidencia es la fixture genérica de AJ4; la composición real se verifica al operar ese proyecto.
3. `SUSP-LOCK`: los escritores de continuidad no comparten el lock del proyecto (preexistente).
4. `SUITE-CONTAMINATION` y demás deudas heredadas de 007-007 siguen abiertas.
