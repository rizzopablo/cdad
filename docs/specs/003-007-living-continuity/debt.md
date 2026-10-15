# Deuda — 003-007-living-continuity

| Id | Origen | Prioridad | Descripción |
|---|---|---|---|
| R2-STAGE | review-draft-001 R-2 | media | Las aprobaciones que solo constan en `stage_history` del state no entran en ningún digest. La proyección de autoridad cubre `hitl_delegation`, `approver` y `execution`. |
| POLICY-CLASS | D10 | media | Clases por defecto declaradas en la política. Bloqueado porque el esquema de `docs/cdad-policy.json` es estricto (`cdad_packet.py:406`) y requiere coordinar con el renderer. |
| CKPT-FORK | D5 | baja | Dos checkpoints divergentes con la misma clave (por restauración o concurrencia) no se detectan por conteo. |
| T1-N1 | review-t1 | baja | `fields` sobre un archivo que existe pero no es JSON se informa como `missing`. Bloquea, pero el diagnóstico es impreciso. |
| T1-N2 | review-t1 | baja | Un campo de `fields` que no resuelve protege cero, en silencio; documentarlo en `continuity.md`. |
| T1-N3 | review-t1 | baja | `begin`/`checkpoint` no reverifican las referencias `contract` del head previo. |
| T2-R1 | review-t2 | baja | Re-ejecutar un `begin` idéntico después de un append de su misma clave da rc≠0 (falla cerrado, sin escrituras) en lugar de no-op. Remedio: reconocer el body idéntico de la clave en `bodies/`. |
| T2-N1 | review-t2 | baja | `_canonical_body` etiqueta como `checkpoint` todo comando distinto de `begin`; usar un enum explícito. |
| FLAKY-002-T3 | green-t4 | baja | `tests/test_003_002_t3_run_evidence.py::TestNonReusableRunOutcomes::test_p5_failing_suite_not_valid_current` falló una vez en la suite completa y pasa aislado; investigar la dependencia de orden o de tiempo. |
| T4-F2 | review-t4 | baja | `tests/test_003_007_t4_atomic_unit_rule.py:150`: la señal `r"plan"` no discrimina; anclarla a "plan task". |
| MIX-V6V7 | T3/T4 uso real | media | La v6 leyendo un checkpoint escrito por la v7 con `fields` digiere el archivo completo y falla cerrado (`reconcile` rc 1 por `docs/.cdad-state.json`). Es seguro, pero el orquestador debe usar una sola versión del CLI por ejecución; documentarlo en la adopción de la v7. |
| VALIDATE-IDLE | cierre del epic | baja | `cdad_packet.py validate-state` rechaza un state en reposo (`active_feature` nulo con el bloque `execution` de la última feature). Preexistente: el state en reposo de 003-006 da el mismo error. Debería aceptar el estado `idle` o pedir que se archive `execution`. |
