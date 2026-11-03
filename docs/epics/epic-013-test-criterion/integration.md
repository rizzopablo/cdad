# Epic 013 — Integración (E3)

**Revisión:** `57a68a84`. **Medición del orquestador, selección focal; suite completa no realizada.**

| # | Criterio del plan | Estado | Evidencia |
|---|---|---|---|
| 1 | Rutas legacy y por paquetes transmiten el mismo criterio | **cubierto (test + review)** | `tests/test_013_001_criterion_coherence.py` (5), `test_005_003_t6` pd10, `test_004_003_t5` G2; revisiones de 013-001 (B1–B6, R1–R3 cerrados). Falta tercera revisión independiente (declarado). |
| 2 | `cdad-suite.py validate` rc=0 | **cubierto** | `validate` rc=0: 1949 nodeids, 232 módulos, 31 registros (013-002). |
| 3 | Piloto con decisiones acreditadas por revisión independiente; «mantener» válido | **cubierto con límite** | 013-003: Mantener A/B/C, review F1–F3. Mutación «no realizada», viabilidad inconclusa. |
| 4 | Ninguna promesa pierde verificación; sin cuotas | **cubierto con límite** | Piloto sin retiros; no hay conteos como objetivo. Deuda O1 de 013-001: los tests no detectan regresiones semánticas en Odoo. |
| 5 | Cambios en `sources/` y regeneración | **cubierto** | `make agents` rc=0 sin deriva; `cdad-doctrine-check` OK. |

Selección ejecutada: 013-001 (5), 013-002 (7), B1 A/B/C (3), `test_005_003_t6`, `test_004_003_t5`, `test_cdad_generate` → **40 passed**.
No ejecutado: suite completa, gate de CI, `surface` completo.
