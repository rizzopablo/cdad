# Closure — 015-003-closed-set-oracle

**Epic:** `epic-015-dispatch-reception` — orden 3/3. **Cerrada:** 2026-11-03. No publicada ni desplegada.
**Contrato:** `docs/specs/015-003-closed-set-oracle/spec.md`.

## Resultado
El oráculo INV-04 de `tests/test_010_002_documentary_role_properties.py` admite exactamente `agent`,
`execution_context` e `instruction_sources` sobre el conjunto del fixture (igualdad exacta). Commit `9353e3a8`.

## Evidencia
- Test objetivo y archivo completo (7 passed) verdes. Sensibilidad por mutación en copia: campo extra, falta de `agent`
  o de `execution_context` → falla.
- Sin revisión independiente de esta corrección (ajuste de un oráculo, verificado por el orquestador): límite declarado.

## Deuda
- 015-001 añadió un campo al request sin actualizar todos los oráculos de conjunto cerrado; solo la suite completa lo
  reveló. Conviene que un cambio de esquema liste los oráculos dependientes (grep de `execution_context` en tests).
