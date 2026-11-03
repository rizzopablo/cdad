# Closure — epic-015-dispatch-reception

**Cerrado:** 2026-11-03.

## 1. Resultado
`record-dispatch` y `receive` validan el paquete contra las fuentes congeladas al despachar (`instruction_sources` en
`REQUEST.json`), no contra el árbol vivo; los formatos cerrados explican la forma esperada con ejemplo; `docs=docs`
vs `contract` tiene guía; `open-unit` omite unidades `queued` de epics cerrados y bloquea ante atribución ambigua.
Resuelve el todo `0efea826`.

## 2. Evidencia
Ver `integration.md`: suite completa verde atribuible (1967 passed, 0 failed, 5 skipped).

## 3. Deuda
- F4 de 015-002: la ambigüedad intra-plan depende del texto `"ambiguous"` de `_locate_unit`.
- Sin segunda revisión independiente de los review-fix de 015-002 ni de 015-003 (límite declarado).
- Flaky de temporización: `test_006_005_u6fix5_write_ahead` (fixture con espera de 20 s) falla bajo carga alta.
- Un cambio de esquema del request debería listar los oráculos de conjunto cerrado dependientes.
- Heredada: tests con patrones literales (014), ventanas por número de línea, F011 preexistente.

## 4. Siguiente
Epic de trazabilidad contrato→test y revisión de la suite por tramos del 20%
(`docs/planning/test-evidence-and-traceability-proposal-2026-11-02.md`).
