# Closure — 014-001-suite-evidence-defaults

**Epic:** `epic-014-suite-evidence-policy` — orden 1/1. **Cerrada:** 2026-11-02.
**Contrato:** `docs/specs/014-001-suite-evidence-defaults/spec.md`, sha256
`6403397f4d57abee961d59c69a4d8d7403f7a306b2fdbc2e4785622208b0c2f0`, aprobado por Pablo (HITL delegada).
**Estado:** cerrada en el repositorio; **no publicada ni desplegada**.

## 1. Resultado

Defaults por momento vigentes: ciclo focal; cierre de feature, suite completa recomendada (omisión con motivo);
cierre de epic, obligatoria (omisión solo con dispensa expresa del dueño). La aprobación de la política autoriza
la corrida ordinaria de cierre de epic. ADR-042 supersede solo la cláusula de autorización/defaults de ADR-041.
Hogar `stage-3-tdd.md` y las 24 superficies de §5 alineadas; `make agents` reproducible; doctrina OK.

Commits: RED `c0c5c73f`; GREEN `bda98739`, `08077a6a`, `fbd8a675`; review-fix `e46f5eab`.

## 2. Evidencia

- 4 verificadores nuevos (A–D) verdes; 005-003 t6 + 013-001 (12), 008-005 (19), `validate` rc=0, doctrina OK.
- Review independiente (`review.md`): 1 bloqueante (ci-gate) + 2 menores, corregidos en `e46f5eab`; verificado por
  el orquestador (`autorización expresa` = 0 en `docs/ci-gate.md`; 4+12+19 tests verdes). **Sin segunda revisión
  independiente del fix**: límite declarado.
- Suite completa de la feature: no realizada (recomendada, se corre al cierre del epic por el gate atribuible).
- POST-AUDIT no aplica: #1–#5 de `test-audit.md` siguen verdes (§5 del audit).
- Scribe/Memory Bank: actualizado por el orquestador (`docs/activeContext.md`), sin sesión de scribe (cambio normativo
  pequeño).

## 3. Deuda declarada (deferred-hardening)

- D1: los 4 verificadores usan patrones literales; sobreviven variantes en inglés y «solo se invoca con autorización
  expresa» (mutación en `stage-4-review.md` no detectada). Remedio: patrón semántico `(solo|only)\b.{0,40}autorizaci[oó]n expresa`.
- D2: ~20 consumidores repiten la tabla de defaults en lugar de remitir al hogar (riesgo de deriva).
- D3: F011 (`validate-subagents.sh`) falla desde la base; no investigado.
- D4: tooling de despachos (todo del proyecto `0efea826`): recepción compara contra el árbol vivo; GREEN-002 se cerró
  con `withdraw` pese a haberse despachado y entregado.
- Instalación en HOME desfasada: la norma nueva no está desplegada (decisión del dueño).
