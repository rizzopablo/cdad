# Revisión de rol — informe (etapa 4)

**Packet:** 003-006-runtime-adoption-reviewer-report-001 · **Role:** reviewer · **Object:** `git diff 52b10f5..a0f2335` (solo `skills/cdad-cycle/SKILL.md`) vs aprobado `docs/specs/003-006-runtime-adoption/spec.md` (P1 mitad SKILL + P10)
**Contract SHA:** `dc485e80…d7cb7` ✓ verificado · **Policy SHA:** `f508ab1e…2711` ✓ verificado

---

## Verdict: PASS (sin bloqueantes)

El diff implementa el cableado P1-mitad-SKILL con fidelidad a §2.1: cada comando en su paso, sin duplicar interfaces. 9/9 aserciones del test focal en GREEN, y RED honesto demostrado (8 fallos contra la pre-imagen). Un hallazgo de puntero impreciso y una debilidad del test van a deuda según la proporcionalidad MVP del orquestador.

## Evidencia de verificación (comandos exactos + salida)

```
sha256sum docs/specs/003-006-runtime-adoption/spec.md docs/cdad-policy.json
→ dc485e80aa86b545c75c86f71a3fa590321c1ca6a66221e1115c69b75a7d7cb7 … (coincide)
git diff 52b10f5..a0f2335 --name-only         → solo skills/cdad-cycle/SKILL.md ✓
python3 tests/test_003_006_t1_wiring.py       → Ran 9 tests … OK
Pre-imagen 52b10f5 (mismo suite, SKILL.md@52b10f5): run=9 failures=8 errors=0
  RED honesto en: classify, begin, checkpoint, receive, reconcile,
  tabla-references, resume, trigger
```

## Bloqueantes

Ninguno.

## Opcionales (deuda)

**F1 — Puntero de contrato impreciso para `receive` (Optional · Bucket: m)**
`skills/cdad-cycle/SKILL.md:278`. La frase «Materialize and `receive` the role's final result … (contracts in `references/continuity.md`)» remite la mitad `receive` a continuity.md, pero ese archivo **no menciona `receive`** (grep: 0 coincidencias). El contrato de materialización vive en `references/re-entry.md:15-45` y su CLI es `cdad_result.py` (consistente con spec §2.1, que asocia `receive` con re-entry). **No rompe el camino feliz**: el mismo Step 6 carga `re-entry.md` explícitamente, donde el lector nuevo encuentra el script y el protocolo. Pero es exactamente el anti-patrón que el orquestador marcó (check 1). Cierre sugerido: en T3, al cablear el cuerpo del orquestador, partir el paréntesis («receive: ver `re-entry.md`; receipt/continuity: `continuity.md»`) o absorber la misma corrección aquí. Rationale grounded: verificado por lectura directa de ambos references.

**F2 — El test se satisface por la fila de la tabla en 5 de 6 comandos (Optional · Bucket: h)**
`tests/test_003_006_t1_wiring.py:87-98,183-192` (aserciones de sección b). Demostrado empíricamente: simulando un SKILL.md que SOLO contenga la fila `| continuity.md | …` de `SKILL.md:452`, las aserciones de `resume`, `begin`, `checkpoint`, `reconcile` y `trigger` pasan (solo `receive` es robusta: requiere «re-entry/materializ/rol» que la tabla no contiene). Las keywords son significativas, pero la fila de la tabla las contiene incidentalmente al resumir el CLI. Consecuencia: el anti-gaming de P1-mitad-SKILL recae casi por completo en la aserción de la tabla; la cobertura de «cada comando en SU paso» no tiene guardia efectiva para 5/6 comandos. **Hoy no es un falso GREEN** (verifiqué que el cableado real existe en las líneas 244/258/278/280 del cuerpo), así que conforme a proporcionalidad MVP va a deuda. Cierre sugerido: exigir para cada comando una mención fuera de la tabla de referencias (excluir líneas que empiezan con `| ` del matching, o una aserción por-step-por-sección).

**F3 — Aserción anti-duplicación trivialmente pre-satisfecha (Optional · Bucket: l)**
`tests/test_003_006_t1_wiring.py:224-238`. En la pre-imagen pasó (9−8=1): es una aserción negativa (no hay filas de tabla con flags) sin comportamiento RED al que responder. El docstring declara honestidad GUARD para este caso, y es un guard razonable contra regresión futura, pero no aporta evidencia GREEN de T1. FYI/consistencia con su propio principio "RED honesto" declarado en el docstring:11-31.

## Coherencia con los checks del orquestador

- **(1) Referencias correctas:** ✓ salvo F1. `begin/checkpoint/reconcile/resume/trigger` → `continuity.md` (correcto: `cdad_continuity.py` documentado en `references/continuity.md:3-43`). `classify` → límite en `progress-guards.md` (correcto: `references/progress-guards.md:17-21` declara «no product reader exists» — coincide con el texto de `SKILL.md:280`). `receive` → ver F1.
- **(2) Script nombrado sin copiar flags:** ✓ vía la cadena de referencias (continuity.md, re-entry.md → `cdad_result.py --help`, progress-guards.md). El cuerpo de SKILL.md no copia ninguna firma de CLI; `cdad_continuity.py` / `cdad_result.py` / `cdad_guard.py` son alcanzables en un salto. Lector nuevo puede ejecutar cada comando sin adivinar el script, salvo el caso F1.
- **(3) Tabla de referencias / `optional`:** ✓. Fila añadida en `SKILL.md:452` («optional continuity CLI»), coherente con el carácter **optional** declarado en `continuity.md:4` y `progress-guards.md:3`; lista de comandos de la fila coincide 1:1 con §2.2/§2.4 de la spec.
- **(4) Test robusto:** parcial — ver F2. Sin keywords sin sentido (todas mapean §2.1), pero el matching no discrimina tabla vs cuerpo.

## FYI

- El árbol de trabajo tiene `docs/.cdad-state.json` modificado (no commiteado) — fuera del diff revisado y territorio del orquestador; impact 史料 nulo para este dictamen.
- Alcance del diff respetado: el commit `a0f2335` toca solo `skills/cdad-cycle/SKILL.md` (T1), sin tocar el cuerpo del orquestador ni agentes regenerados (correctamente dejados a T3).

## Abstentions

Ninguna — todos los observables declarados por el contrato fueron verificados con lectura directa y ejecución del test focal contra pre-imagen y post-imagen. Nota de alcance: el criterio de aceptación 1 (suite completa del repo) corresponde al gate de cierre, no a esta revisión focal T1; no ejecutado ni juzgado aquí.
