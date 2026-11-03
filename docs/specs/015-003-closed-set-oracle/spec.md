---
feature_id: 015-003-closed-set-oracle
approved_by: Pablo (HITL delegada, docs/epics/epic-015-dispatch-reception/execution.md)
approved_at: 2026-11-03
source: redactada por el orquestador (corrección mínima de un oráculo, ADR-003); sin sesión de architect
---

# 015-003 — Oráculo de conjunto cerrado de 010-002 y `instruction_sources`

## Contexto (evidencia)
Suite completa de cierre del epic 015 (`.cdad/local/epic015/gate-20261103T003948606155Z-310588-3341a790`, commit
`8acccc41`): 1966 passed, **1 failed**, 5 skipped. Falla
`tests/test_010_002_documentary_role_properties.py::TestInv04Properties::test_publication_conserves_the_admitted_request_and_render_fields`
(~:615): el conjunto de campos del request publicado debe ser el del fixture más `{agent, execution_context}`;
ahora incluye `instruction_sources`, campo opcional añadido por 015-001 (esquema `packet-request.schema.json`).

## Promesa
El oráculo INV-04 sigue garantizando que la publicación conserva el request admitido y que no crece con campos no
previstos, admitiendo exactamente el campo que 015-001 aprobó.

**PC-1.** El conjunto admitido pasa a ser fixture ∪ {`agent`, `execution_context`, `instruction_sources`}; no se
relaja la igualdad exacta (no `issubset`).
**PC-2.** Sensibilidad: un campo extra distinto (p. ej. `foo`) en el request publicado sigue haciendo fallar el
test; la ausencia de `agent` o `execution_context` también.

## Invariantes
Solo cambia `tests/test_010_002_documentary_role_properties.py` (test-writer). Sin cambios de producto ni de contratos
cerrados (010-002, 015-001).

## Aceptación
El test verde; PC-2 por mutación en copia; el cierre del epic repite la suite completa.
