# Closure — 015-002-intake-guards

**Epic:** `epic-015-dispatch-reception` — orden 2/2. **Cerrada:** 2026-11-02. No publicada ni desplegada.
**Contrato:** `docs/specs/015-002-intake-guards/spec.md`, sha256 `a8bafbdd28d14b31f9c126904b2763490721c45e8b7cf769d250696dc3b22f9e`.

## Resultado
Formatos cerrados (observación de despacho, `decisions` de `begin`, `--write-scope`) con diagnóstico del formato
esperado y ejemplo; rechazo `docs=docs` vs `contract` con guía (sin reclasificación automática); `open-unit` omite
unidades `queued` de epics cerrados por pertenencia al plan y bloquea si la atribución es ambigua.

Commits: RED `71d50cad`; GREEN `b4411999`, `74552842`, `737deb57`; review-fix F1/F3 `29a60b51`; POST-AUDIT `7f774032`.

## Evidencia
- `tests/test_015_002_intake_guards.py` 10 passed; `test_015_001_frozen_reception.py` 9 passed; doctrina OK;
  `cdad-suite.py validate` rc=0 tras alta de inventario (015-001 y 015-002, capacidad `dispatch-recovery`).
- Review independiente (`review.md`): 1 bloqueante (F1: atribución por número de línea entre archivos), corregido y
  con verificador sensible (falla contra `737deb57`). **Sin segunda revisión independiente del fix**: límite declarado.
- Suite completa de la feature: no realizada (recomendada); se corre al cierre del epic por el gate.

## Deuda
- F4: la ambigüedad intra-plan depende del texto `"ambiguous"` de `_locate_unit` (preferible retorno estructurado).
- Regresiones del §6 de la spec (008-004, 005-007-t3, despacho/continuidad) solo cubiertas por la suite completa del cierre.
