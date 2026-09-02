# VALIDATION — cdad-007-systematic-debugging

Framework documental: checks de estructura en `run-checks.sh` (patrón
cdad-004/005/006). Corren desde la raíz del repo (`cdad/`):
`bash docs/specs/cdad-007-systematic-debugging/run-checks.sh` (contenido+guard)
y `--full` post-GREEN (criterio 5).

## Desviación detectada en AUDIT (importante para el implementer)

El contrato P1 lista 7 ítems (a–g), pero el ítem (b) "4 fases" engloba cuatro
piezas ortogonales (diagnóstico / minimización / hipótesis / fix único) que
merecen oráculo independiente (una pieza por check). Resolución: **C1a–C1j
(10 checks)** en lugar de C1a–C1g. El mapeo pieza↔check está en la tabla de
abajo; las postcondiciones son las mismas del spec.

Además: el enfoque de `stage-5-merge.md` §5.1 se ancla al texto preexistente
"volv(é|e) a Etapa 3" (l.31 hoy) y C2c exige además **orden**: la mención de
`stage-debugging` debe aparecer ANTES de esa frase (awk). Referencia después
del "volvé" invalidaría el contrato ("stage-debugging ANTES de volver a
Etapa 3", research.md l.40).

## AUDIT (baseline, 2026-09-02)

| Suite | Resultado |
|---|---|
| `bash tests/validate-odoo-specialization.sh` (cdad-003) | **121/121 PASS** |
| `bash docs/specs/cdad-005-receiving-feedback/run-checks.sh` | **23/23 PASS** |
| `bash docs/specs/cdad-006-git-safety-close/run-checks.sh` | **19/19 PASS** |

Grep de cobertura previa (`stage-debugging|AP-18` en `skills/`, `tests/`,
`docs/`): **4 matches, todos en docs/** (research.md l.31/38/40 y
`docs/epics/epic-001-superpowers-gaps/plan.md` l.45 — documentos de research,
no comportamiento). En `skills/`: **0 matches**.
`skills/cdad-cycle/references/stage-debugging.md` **no existe**; no hay
`## AP-18` en anti-patterns.md (último AP: AP-17). Confirma: el comportamiento
nuevo no existe hoy.

Encabezados verificados hoy (para guards C4):

- `stage-3-tdd.md`: `## Sub-fase 3.1 — RED` (l.70), `## Sub-fase 3.2 — GREEN`
  (l.98), `## Sub-fase 3.3 — REFACTOR` (l.113), `## 🛑 Gate de salida (Etapa 3 → Etapa 4)` (l.161).
- `stage-5-merge.md`: `## 5.1 — Verificación CI` (l.15),
  `## 5.6 — Cierre de la branch (git safety)` (l.82, heredado de cdad-006),
  `## 🛑 Gate de salida (Etapa 5 → done)` (l.160).
- `SKILL.md`: tabla de lectura en ~l.268 (`Etapa N → references/stage-N-*.md`).

- **Tests a modificar: 0** — ninguna suite previa (cdad-003/004/005/006) toca
  el comportamiento nuevo; el ciclo light toca ~5 archivos sin reordenar
  estructura existente (guardeado por C4).
- **Tests untouched (explícitos):** los 121 asserts de cdad-003, los 23
  checks de cdad-005, los 19 de cdad-006 (incluye los 6 guards de cdad-006
  sobre 5.1–5.6 y Gate de stage-5) y los 10 de cdad-004 (vía `--full`).
  Verificados AHORA: todos GREEN.
- **Tests nuevos: 23** (16 RED de contenido + 7 GUARD) + C5 post-GREEN.
- **Riesgos de regresión:** bajo. Ediciones en `SKILL.md`,
  `stage-3-tdd.md` (solo dentro de §3.2 GREEN), `stage-5-merge.md` (solo
  dentro de §5.1) y `anti-patterns.md` (append AP-18 al final) podrían
  clobbererear encabezados → mitigado por C4a–C4g (guard que PASA hoy y debe
  seguir en GREEN). Regresión cruzada en suites previas → mitigada por C5
  `--full` post-GREEN.

## Mapa check ↔ postcondición

| Check | Postcondición / pieza | Criterio PASS |
|---|---|---|
| C1a | P1a: stage-debugging.md + ley de hierro (sin causa raíz no hay fix) + tight feedback loop = RED | `test -f` + 4 greps en archivo nuevo |
| C1b | P1b(1): fase diagnóstico: error completo + loop rojo + cambios recientes + evidencia | 4 greps |
| C1c | P1b(2): minimización de repro cut-one-thing | 2 greps |
| C1d | P1b(3): hipótesis rankeadas 3-5 falsables, una variable por vez | 4 greps |
| C1e | P1b(4): fix único sobre causa raíz | 2 greps |
| C1f | P1c: defense-in-depth después del fix + condition-based-waiting + tasa de repro | 3 greps |
| C1g | P1d: regla 3+ fixes → STOP → escalar al usuario con evidencia → ADR | 5 greps |
| C1h | P1e: roles (implementer diagnóstico / test-writer regresión / Five Whys-Fagan stubborn) | 5 greps |
| C1i | P1f: tabla anti-racionalización (encabezado + filas de tabla markdown) | 2 greps |
| C1j | P1g: cuándo NO aplica (infra / flaky puro / plan de monitoreo) | 4 greps |
| C2a | P2: SKILL.md tabla de lectura agrega fila stage-debugging | `test -f` + grep |
| C2b | P2: stage-3 §3.2 GREEN referencia stage-debugging antes de re-delegar | sed scope 3.2→3.3 + 2 greps |
| C2c | P2: stage-5 §5.1 referencia stage-debugging ANTES de "volvé a Etapa 3" | sed scope 5.1→5.2 + grep + awk de orden |
| C3a | P3: encabezado `^## AP-18` | grep anclado a línea |
| C3b | P3: 3 sub-secciones Síntoma/Por qué es malo/Corrección en bloque AP-18 | sed scope bloque AP-18 |
| C3c | P3: AP-18 cita la reference stage-debugging | grep en scope AP-18 |
| C4a–C4g | GUARD: sub-fases 3.1 RED / 3.2 GREEN / 3.3 REFACTOR, Gate etapa-3, `## 5.6`, Gate etapa-5, `## 5.1` intactos | PASS hoy, debe seguir en GREEN |
| C5a–C5d | criterio 5 (post-GREEN, `--full`): suites cdad-003/004+005/005/006 verdes | 121/121 + 10/10 + 23/23 + 19/19 |

Anti-falso-positivo (lecciones cdad-004/005/006): ancla `test -f` en C1a/C2a;
acentos con alternancia `(ó|o)`/`(í|i)`/`(é|e)`; scope de bloque con
`sed -n '/^## AP-18/,$p'` (AP-18 es el último AP: imprime a EOF), scope 3.2
delimitado por el siguiente encabezado `## Sub-fase 3.3`, scope §5.1
delimitado por `## 5.2`; C2c agrega chequeo de ORDEN con awk (mención antes
del "volv(é|e) a Etapa 3"); los guards usan el encabezado completo con `—` para
no confundir con menciones en prosa.

Nota RED: C1a falla con exit=1 (fallo de `test -f`); C1b–C1j fallan con
exit=2 (grep sobre archivo inexistente). Ambos son "razón correcta": el
contenido no existe. En GREEN, si el archivo existe pero falta una pieza, los
greps reportan exit=1 — el check sigue discriminando pieza por pieza.

## RED — output sobre estado actual (2026-09-02)

```
=== C1 -> P1: stage-debugging.md (una pieza por check; ver desviación en VALIDATION.md) ===
FAIL  C1a P1a: encabezado + ley de hierro sin causa raíz no hay fix + tight feedback loop = RED (exit=1)
FAIL  C1b P1b(1): fase diagnóstico: error completo + loop rojo + cambios recientes + evidencia (exit=2)
FAIL  C1c P1b(2): minimización de repro cut-one-thing (exit=2)
FAIL  C1d P1b(3): hipótesis rankeadas 3-5 falsables, una variable por vez (exit=2)
FAIL  C1e P1b(4): fix único sobre causa raíz (exit=2)
FAIL  C1f P1c: defense-in-depth después del fix + condition-based-waiting (tasa de repro) (exit=2)
FAIL  C1g P1d: regla 3+ fixes -> STOP -> escalar al usuario con evidencia -> ADR (exit=2)
FAIL  C1h P1e: roles — diagnóstico implementer / regresión test-writer / Five Whys-Fagan stubborn (exit=2)
FAIL  C1i P1f: tabla anti-racionalización (exit=2)
FAIL  C1j P1g: cuándo NO aplica — infra / flaky puro con plan de monitoreo (exit=2)
=== C2 -> P2: enlaces de entrada (SKILL.md, stage-3 GREEN, stage-5 §5.1) ===
FAIL  C2a P2a: SKILL.md tabla de lectura agrega fila stage-debugging (exit=1)
FAIL  C2b P2b: stage-3 sub-fase GREEN referencia stage-debugging antes de re-delegar (exit=1)
FAIL  C2c P2c: stage-5 §5.1 referencia stage-debugging antes de 'volvé/volvemos a Etapa 3' (exit=1)
=== C3 -> P3: anti-patterns.md AP-18 ===
FAIL  C3a encabezado '^## AP-18' (exit=1)
FAIL  C3b 3 sub-secciones (Síntoma/Por qué es malo/Corrección) en bloque AP-18 (exit=1)
FAIL  C3c AP-18 cita la reference stage-debugging (exit=1)
=== C4 -> GUARD: sub-fases TDD, gates y estructura previa intactos (PASS hoy) ===
PASS  C4a stage-3: Sub-fase 3.1 — RED intacta
PASS  C4b stage-3: Sub-fase 3.2 — GREEN intacta
PASS  C4c stage-3: Sub-fase 3.3 — REFACTOR intacta
PASS  C4d stage-3: Gate de salida (Etapa 3 -> Etapa 4) presente
PASS  C4e stage-5: '## 5.6 — Cierre de la branch (git safety)' intacta (cdad-006, no clobbered)
PASS  C4f stage-5: Gate de salida (Etapa 5 -> done) presente
PASS  C4g stage-5: '## 5.1 — Verificación CI' intacta
---
RESUMEN: PASS=7 FAIL=16 (checks de contenido + guard: 23; C5 corre con --full post-GREEN)
```

Los 16 checks de contenido fallan por la razón correcta (contenido
inexistente: `test -f` falla / grep sin match). C4 guard pasa por diseño.

## Estado por criterio de aceptación

| Criterio | Estado |
|---|---|
| 1. `stage-debugging.md` con las piezas P1a–P1g | **RED** (C1a–C1j fallan) → GREEN al implementar |
| 2. Enlaces de entrada (SKILL.md, stage-3 GREEN, stage-5 §5.1) | **RED** (C2a–C2c fallan) → GREEN al implementar |
| 3. `## AP-18` con 3 sub-secciones + cita | **RED** (C3a–C3c fallan) → GREEN al implementar |
| 4. Sub-fases TDD y gates intactos | **PASS hoy** (C4a–C4g) — guard, debe seguir en GREEN |
| 5. Checks definidos ANTES de editar y fallando hoy | **CUMPLIDO** (output RED arriba) |
| 6. Sin regresión (003/004/005/006 verdes) | Baseline verde hoy; verificar con `--full` post-GREEN |

Pendiente: GREEN por el implementer (edita SOLO SKILL.md, stage-3-tdd.md
§3.2, stage-5-merge.md §5.1, anti-patterns.md y CREA
stage-debugging.md), luego `run-checks.sh` (23/23) y `run-checks.sh --full`.
