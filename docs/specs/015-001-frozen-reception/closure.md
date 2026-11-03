# Closure — 015-001-frozen-reception

**Epic:** `epic-015-dispatch-reception` — orden 1/2. **Cerrada:** 2026-11-02.
**Contrato:** `docs/specs/015-001-frozen-reception/spec.md`, sha256
`f0493229b569775143643c452c0939082b3c1868f378f0de7e9298baa9fb63ce`, aprobado por Pablo (HITL delegada; D1+D2 aprobados expresamente).
**Estado:** cerrada en el repositorio; **no publicada ni desplegada**.

## 1. Resultado

`prepare`/`render`/`validate`/`record-dispatch`/`receive` operan desde el respaldo congelado `instruction_sources`
(`path/sha256/snapshot`) cuando el request lo porta; históricos sin el campo conservan la validación estricta viva
(D2/PC-05); replay durable intacto (PC-06). El esquema publicado admite la quinta opcional. La vía
`--replace-packet` captura instrucciones vigentes (A2b).

Commits: RED `15051d35` (8 Añ, 7 rojos + guarda D2); GREEN `92e4c4a0` (+147/−5 en `skills/cdad-cycle/scripts/cdad_packet.py`);
RED-002 `efa78384` (fixtures C1/C2/D1); POST-AUDIT `855afd42` (P1/P2); review-fix F-1 `689557d5` (esquema);
POST-AUDIT-002 `daa4eb8f` (A2b + F-3).

## 2. Evidencia

- 9 verificadores 015-001 verdes; falsificación base+tests HEAD: 9 failed/18 passed (D2 guarda).
- Mutantes: M1 muere (B1/B2/C1); M2 muere (C1+8 de 008-004); M6 muere (A2b); M3 sobrevive no observable (borde `receive --late` diferido en §7).
- Regresión proporcional: 008-004 27, render 17, review_regressions 8, packet_prepare 19, 005-003_t6 7, 010_004_* 22, TestRequestSchema 3, doctrina OK, `make agents` sin cambios.
- Review independiente (`review.md`): 2 bloqueantes F-1/F-2 cerrados y verificados por el orquestador (TestRequestSchema 3 passed; 015-001 9 passed; packet_prepare 19 passed; doctrina rc=0). **Sin segunda revisión independiente del fix**: límite declarado.
- Suite completa de la feature: no realizada (momento «durante el ciclo»; se corre al cierre del epic por el gate).
- Incidentes del ciclo: GREEN-001 entregó interino incompleto (5/8, sin commit) con fixtures RED que presumían lo viejo → red-002 los reparó; el primer despacho del reviewer lo armó el orquestador a mano con `packet_id` ajeno → el reviewer lo rechazó (INVALID PACKET) y el re-despacho con el render exacto pasó. Ambos registrados como deuda de tooling en el epic.

## 3. Deuda declarada
- F-4 (traza `.superseded.json`/ASSIGNMENT_UNIVERSE) → 015-002 o deuda del epic.
- M3/`receive --late` con congelado no ejercitado e2e (spec §7).
- Ventanas por número de línea en oráculos (deuda heredada de 014-002).

## 4. Siguiente
015-002-intake-guards (diagnósticos de formatos cerrados, `docs=docs` vs `contract`, `open-unit` sobre queued de epics cerrados), luego suite completa de cierre del epic.
