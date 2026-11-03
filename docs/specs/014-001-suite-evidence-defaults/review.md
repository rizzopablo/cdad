# review.md — 014-001-suite-evidence-defaults (stage 4)

Reviewer: sesión `<ses-336>`, paquete `014-001-suite-evidence-defaults-reviewer-review-001`
(route C validada). Materializado por el orquestador (ADR-003).

**Veredicto:** funciona pero no pasa tal cual: 1 bloqueante; resto opcional/deuda.

## Verificación

- `pytest tests/test_014_001_suite_evidence_defaults.py` 4 passed; 005-003 t6 + 013-001 → 12 passed.
- `make agents` en worktree limpio: sin cambios. `make validate`: F011 (`validate-subagents.sh`) 1 FAIL; la base
  `c4271693` ya tenía 2 → no empeora.
- INV-2: fuera de 014-001 solo cambió `008-002/suite-inventory.json` (alta aditiva).
- Mutaciones: reintroducir la norma vieja en `common.md`, `epic-closure.md`, `sources/roles/reviewer.md`,
  `run-budget-protocol.md` → detectada; en `stage-4-review.md` en inglés → **sobrevive**.

## Hallazgos

1. **BLOQUEANTE** — `docs/ci-gate.md:3-7` aún exige «autorización expresa suficiente para esa corrida» para todo
   gate; contradice :64-71 y PC-3/PC-9 justo en el gate que cierra el epic 014. Fix: alinear 3-7 con 64-71.
2. Opcional — `docs/systemPatterns.md:1396-1398` describe en presente «solo corre con autorización expresa» sin
   remisión a ADR-042.
3. Opcional — `stage-5-merge.md:32` «With autorización expresa, run the full suite» junto a «recomendada» (:27-28).
4. Opcional (deferred-hardening) — los 4 verificadores son parcialmente sensibles: patrón literal
   (`tests/test_014_001_suite_evidence_defaults.py:68-73`); dejan pasar variantes en inglés y «solo se invoca con
   autorización expresa». Remedio: patrón semántico `(solo|only)\b.{0,40}autorizaci[oó]n expresa` excluyendo «dispensa».
5. Opcional — ~20 consumidores repiten la tabla de defaults en vez de remitir al hogar (riesgo de deriva; 1 y 3 son
   ejemplos).
6. Nota — Mantener #1–#5 sin POST-AUDIT es coherente; la protección de la norma nueva recae en los 4 verificadores.

Filas §5: todas cumplen en sentido salvo ci-gate (hallazgo 1).

Abstenciones: causa de F011 no investigada (preexistente). Suite completa no realizada (selección: 014-001,
005-003, 013-001, `make validate`).

## Decisión del orquestador (HITL delegada)

- Hallazgo 1: review-fix obligatorio. Hallazgos 2 y 3: se corrigen en el mismo review-fix (coste mínimo, misma causa).
- Hallazgo 4: deuda `deferred-hardening` (R3: afecta al gate, no al usuario final directamente).
- Hallazgo 5: deuda para una unidad posterior (consumidores solo remiten al hogar).
