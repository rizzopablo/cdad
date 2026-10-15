# test-audit — 004-003-planning-procedures

> Auditoría de relevancia test↔postcondición, en **sesión distinta** de la que
> escribió los tests (gate de salida de la etapa 3). Materializada por el
> orquestador desde el TEXTO FINAL del reviewer (ADR-003). Sesión:
> `<ses-28>` (paquete
> `004-003-planning-procedures-reviewer-review-009`). Árbol: `287f6c7`.

**Resultado: 35/35 tests mapeados a una postcondición o criterio de aceptación.
Superfluos: ninguno (confianza ≥80%). No mapeados: ninguno.**

| Archivo (#tests) | → Postcondición / criterio |
|---|---|
| `test_004_003_t1_draft_contract.py` (2) | PD-1 positivo (emisión con sha/versión, sin marca de aprobación; state + `validate-packet` ✓) · PD-1 negativo (forja `approved-*` + `plan_version`, sin publicación) |
| `test_004_003_t1_reviewfix.py` (2) | PD-1 + invariante 4 (solo-reviewer; 2 roles sondeados) · PD-1 (`purpose` sin wording de aprobación; REQUEST↔PACKET) |
| `test_004_003_t2_plan_review.py` (5) | PD-2 (composición sha-pinned `common+reviewer+reviewer-plan-review`, nunca `review`) · PD-3 (kind no `approved-*`) · PD-4 (rol único; sonda `test-writer`) · PD-9 (encargo completo) · PD-4 instalado (render byte-idéntico sin repo fuente) |
| `test_004_003_t2_reviewfix.py` (2) | PD-2/AC-1 negativos ×2 (pairing bidireccional B1/B2, con controles honestos) |
| `test_004_003_t3_plan_checks.py` (5) | AC-3: control válido + 4 defectos con diagnóstico tokenizado (PD-2 estructural) |
| `test_004_003_t4_validation_fields.py` (11) | PD-8 ×5 (bloque obligatorio; campos por tarea; forma A + estrategia común una vez; sin código sin checks rechazado) · PD-11/AC-5 ×2 (observables sin código; Go co-ubicado) · deuda F1 de review-t3 (5 variantes de fence fail-loud) · PD-12/inv.6/G5 ×3 (hogar canónico §4; §4.1 con nombres de esquema; consumidor stage-2 refiere una vez) · F-C (ref de estrategia en regressions) |
| `test_004_003_t5_reentry_equivalence.py` (8) | PD-5 (equivalencia + dimensiones + evidencia path/line/commit) · PD-6 (corrida nueva + incertidumbre declarada + mismo-commit≠entorno + antes del cierre) · PD-7 · PD-10 ×2 (re-entry + SKILL co-dueño) · G2 · PD-12/inv.6 ×2 (distribución D4) |

## Debilidades residuales de relevancia (con disposición)

1. **Oráculos de T5 por marcadores textuales** con regexes permisivas — la
   protección real depende de la revisión semántica. *Disposición:* aceptado; el
   hueco de flujo (AC-4) lo absorben la disposición F1 de `review-t5.md` y el
   recorrido de T7.
2. **Tests de distribución D4** fijan solo la palabra `re-entry`. *Disposición:*
   aceptado (control de no-degradación, no de contenido).
3. **F2 de T4 testea prosa por regex** (frágil). *Disposición:* aceptado; el
   reviewer de T4 ejecutó además el ejemplo de §4.1 contra el validador real.

Ninguno constituye test superfluo ni sin mapeo. La convención del proyecto se
respeta: comportamiento observable, sin mocks sobre plumbing, y un fallo RED por
`AssertionError` (verificado en cada tarea contra la base).
