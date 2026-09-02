# cdad-005-receiving-feedback — VALIDATION.md

> Materializado por el test-writer (sesión aislada, 2026-09-02) por delegación
> del orquestador, patrón Contrato de roles §5 del skill cdad-cycle.
> Framework documental: los "tests" son checks de estructura (bash+grep/rg)
> definidos en `run-checks.sh` (esta carpeta), corren desde la raíz del repo.
> Cada check falla por contenido ausente (`exit=1`, equivalente
> AssertionError), nunca por error de invocación.

## Test Audit (3.0)

- **Comportamiento que cambia (en la suite existente): NADA.** La feature es
  aditiva: crea `references/receiving-feedback.md` (P1), agrega referencia y
  regla del transmisor en `stage-4-review.md` (P2), agrega AP-16 a
  `anti-patterns.md` (P3), agrega fila/menciones en `SKILL.md` y
  `handoff-prompts.md` (P4). Verdict-tuple gana solo una cita, sin cambio de
  formato (R3).
- **Cobertura previa (verificada empíricamente):**
  - Baseline: `bash tests/validate-odoo-specialization.sh` → **121/121 PASS**
    ("PASS: todas las postcondiciones P1..P6 y el criterio A3 verificados").
  - Grep `receiving-feedback|AP-16|receiving_feedback` sobre
    `tests/validate-odoo-specialization.sh` y
    `docs/specs/cdad-004-lint-gate/VALIDATION.md` → **0 matches**.
  - Grep `receiving` sobre todo `skills/cdad-cycle/` → **0 ocurrencias**.
  - **Conclusión: 0 cobertura previa para P1-P4 de cdad-005.**
  - Nota de riesgo: la suite cdad-003 SÍ tiene asserts sobre
    `skills/cdad-cycle/SKILL.md` (líneas 198-200: tokens `stack` y `odoo`
    deben existir) — ver regression risks.
- **Tests a modificar: 0** — ninguna aserción existente valida el protocolo
  de recepción ni los archivos objetivo. Suite cdad-003 y checks cdad-004
  quedan **untouched** (lista explícita abajo).
- **Tests nuevos: 23** checks de contenido (C1a-C1m, C2a-C2c, C3a-C3c,
  C4a-C4b, C5a-C5b) + 2 checks C6 que se corren post-GREEN (criterio 7).
- **Regression risks:**
  1. Si el implementer destruye tokens `stack`/`odoo` de
     `skills/cdad-cycle/SKILL.md` al editar la tabla de lectura → rompe asserts
     cdad-003 (líneas 198-200). Mitigación: edición aditiva (agregar fila, no
     reescribir). Tras GREEN, `tests/validate-odoo-specialization.sh` debe
     seguir **121/121** (C6a).
  2. `anti-patterns.md` se modifica (agrega AP-16): ningún assert existente lo
     valida; los 15 APs existentes deben permanecer intactos (alcance cerrado
     R5). Los checks cdad-004 no tocan este archivo.
  3. Checks cdad-004 (10/10) deben seguir verdes tras GREEN (C6b, criterio 7).
  4. Riesgo residual de oráculo: los patrones anclan vocabulario del spec
     (`tenés razón`, `parar TODO`, `cláusulas de salida`, `steelman`, etc.).
     Si GREEN usa sinónimos que no matchean, el check falla en GREEN → el
     orquestador lo devuelve a test-writer para ajustar el oráculo (no es
     falso positivo: falla visible, no silencio).
- **Benefit-of-doubt:** ninguno pendiente. Primera feature con checks para el
  protocolo de recepción de feedback.

### Tests untouched (lista explícita)

- `tests/validate-odoo-specialization.sh` — los 121 asserts completos
  (P1-P6 + A3 de cdad-003): validan `skills/odoo-architect/SKILL.md`,
  `skills/odoo-test-writer/SKILL.md`, `skills/odoo-reviewer/SKILL.md`,
  `agents/cdad-*-odoo.md` y el SKILL.md principal de cdad-cycle (solo por
  presencia de tokens `stack`/`odoo`, que P4 no elimina).
- Checks cdad-004 (comandos de `docs/specs/cdad-004-lint-gate/VALIDATION.md`):
  C1a-C1f (`skills/odoo-make-env/SKILL.md`), C2a-C2b
  (`skills/odoo-reviewer/SKILL.md`), C3a-C3b (`agents/cdad-implementer-odoo.md`,
  `agents/cdad-reviewer-odoo.md`). C4 de cdad-004 (install.sh --check, manual)
  no se re-corre en este ciclo.

## Mapeo check ↔ postcondición

| Check   | Postcondición | Qué valida |
| ------- | ------------- | ---------- |
| C1a-C1m | P1 (piezas a-l) | `receiving-feedback.md`: existencia + 12 piezas, una pieza por check |
| C2a-C2c | P2 (R1) | `stage-4-review.md`: protocolo en loop de fixes + regla del transmisor + orden al receptor |
| C3a-C3c | P3 (R5) | `anti-patterns.md`: `## AP-16` + 3 sub-secciones del catálogo + cita a la reference |
| C4a-C4b | P4 (R1) | `SKILL.md` tabla de lectura + `handoff-prompts.md` transmisión íntegra y protocolo |
| C5a-C5b | Invariante reconsideración (criterio 5, R3) | `verdict-tuple.md` cita steelman/reversal; GUARD formato tuple intacto |
| C6a-C6b | Criterio 7 (sin regresión) | cdad-003 121/121 + cdad-004 10/10, post-GREEN |

## Checks (comandos exactos, corren desde la raíz del repo)

Runner re-ejecutable: `bash docs/specs/cdad-005-receiving-feedback/run-checks.sh`
(add `--full` para incluir C6a/C6b post-GREEN). Variables del runner:
`RF=receiving-feedback.md`, `S4=stage-4-review.md`, `AP=anti-patterns.md`,
`HP=handoff-prompts.md`, `SK=SKILL.md`, `VT=verdict-tuple.md`
(todas bajo `skills/cdad-cycle/`).

| id  | Comando | PASS |
| --- | ------- | ---- |
| C1a | `test -f $RF` | archivo existe |
| C1b | `test -f $RF && grep -q 'sin reaccionar' $RF && grep -q 'restatea' $RF && grep -q 'código real' $RF && grep -qi 'de a un fix' $RF` | secuencia 4 pasos del receptor (P1a) |
| C1c | `test -f $RF && grep -q 'tenés razón' $RF && grep -qi 'performativ' $RF` | respuestas prohibidas + reemplazos factuales (P1b) |
| C1d | `test -f $RF && grep -q 'parar TODO' $RF && grep -qiE 'aclaraci(ó\|o)n' $RF` | ítems ambiguos → STOP antes de implementar (P1c) |
| C1e | `test -f $RF && grep -qi 'push-back' $RF && grep -qiE 'rompe funcionalidad\|falta contexto\|legacy\|incorrecto para el stack' $RF && grep -qi 'evidencia' $RF && grep -qiE 'media el usuario\|reconsideraci(ó\|o)n' $RF` | push-back cuándo (casos del spec) + cómo (evidencia) + destino (reconsideración / media usuario) (P1d) |
| C1f | `test -f $RF && grep -q 'YAGNI' $RF && grep -qi 'grep' $RF` | chequeo YAGNI con grep del codebase (P1e) |
| C1g | `test -f $RF && grep -qiE 'correcci(ó\|o)n factual' $RF` | corrección factual del push-back propio (P1f) |
| C1h | `test -f $RF && grep -qi 'matriz' $RF && grep -qi 'trusted' $RF && grep -qiE 'esc(e\|é)ptic' $RF` | matriz de fuentes (trusted / verificar / escéptico) (P1g) |
| C1i | `test -f $RF && grep -qi 'scribe' $RF && grep -q 'systemPatterns' $RF` | persistencia → nota al scribe para systemPatterns, nunca inline (P1h) |
| C1j | `test -f $RF && grep -qiE 'diluci(ó\|o)n' $RF && grep -qi 'fresca' $RF` | ventaja estructural: packet re-invoca (dilución) + sesión fresca (P1i) |
| C1k | `test -f $RF && grep -qiE 'anti-racionalizaci(ó\|o)n' $RF` | tabla anti-racionalización (P1j) |
| C1l | `test -f $RF && grep -qiE 'cu(á\|a)ndo NO aplica' $RF` | sección cuándo NO aplica (P1k/R4) |
| C1m | `test -f $RF && grep -qiE 'cl(á\|a)usulas? de salida' $RF` | prohibición de cláusulas de salida en reglas propias (P1l/R2) |
| C2a | `grep -q 'receiving-feedback' $S4` | protocolo referenciado en stage-4-review.md |
| C2b | `grep -qiE 'íntegr(a\|o)' $S4 && grep -qi 'suaviz' $S4` | regla del transmisor: feedback íntegro, sin editar que suavice |
| C2c | `grep -qiE 'antes de (tocar\|implementar\|editar)' $S4` | packet ordena aplicar el protocolo antes de tocar código |
| C3a | `grep -nE '^## AP-16' $AP` | encabezado `## AP-16` presente |
| C3b | `sed -n '/^## AP-16/,/^## AP-[0-9]/p' $AP \| grep -q 'Síntoma' && (ídem) 'Por qué es malo' && (ídem) 'Corrección'` | 3 sub-secciones del formato del catálogo dentro del bloque AP-16 |
| C3c | `sed -n '/^## AP-16/,/^## AP-[0-9]/p' $AP \| grep -q 'receiving-feedback'` | AP-16 cita la reference |
| C4a | `sed -n '/^## Cómo leer las references/,/^## /p' $SK \| grep -q 'receiving-feedback.md'` | fila en tabla "Cómo leer las references" (scoping al bloque de tabla) |
| C4b | `grep -q 'receiving-feedback' $HP && grep -qiE 'íntegr(a\|o)' $HP` | handoff-prompts.md: transmisión íntegra (R1) + invocación del protocolo |
| C5a | `grep -qiE 'steelman\|reversal\|reconsideraci(ó\|o)n' $VT` | cita de reconsideración presente (criterio 5) |
| C5b | `grep -q '## El tuple (por hallazgo)' $VT && grep -q 'BLOQUEANTE' $VT && grep -q 'ABSTENER' $VT && grep -q 'Provenance' $VT` | GUARD: formato del tuple intacto (R3) — PASS hoy, debe seguirlo tras GREEN |
| C6a | `bash tests/validate-odoo-specialization.sh` (post-GREEN) | 121/121 PASS |
| C6b | checks cdad-004 C1a-C1f + C2a-C2b + C3a-C3b (post-GREEN, vía `run-checks.sh --full`) | 10/10 PASS |

**Correcciones de oráculo (documentadas por el test-writer):**

1. **`íntegr(a|o)` CON acento, nunca `integra` a secas** (C2b, C4b):
   "Integración" aparece preexistente en `handoff-prompts.md` (línea 412,
   "Etapa 3 — Integración / E2E") y un patrón `integra` sin acento daría falso
   positivo — exactamente la clase de error de cdad-004 (`lint` matcheaba
   `pylint-odoo`). Con acento, el patrón exige la palabra del protocolo.
2. **Token `receiving-feedback` a secas ya es distintivo**: grep de
   `receiving` sobre todo `skills/cdad-cycle/` → 0 ocurrencias preexistentes.
   No hay colisión posible (equivalente a acotar `make lint` en cdad-004).
3. **C3b/C3c scoped al bloque AP-16** con
   `sed -n '/^## AP-16/,/^## AP-[0-9]/p'`: los marcadores Síntoma/Por qué es
   malo/Corrección de OTROS APs (presentes 15 veces) no producen falso
   positivo; si AP-16 fuera la última sección, el rango corre a EOF.
4. **C1b-C1m anteponen `test -f $RF`**: el fallo RED es `exit=1` por ancla
   ausente (archivo inexistente hoy; pieza ausente mañana), nunca `exit=2`
   (grep sobre archivo inexistente) — el check no puede fallar por error de
   invocación.
5. **C5a usa `-i` y alternación** `steelman|reversal|reconsideraci(ó|o)n`:
   cualquier redacción del spec (G2 "steelman", "reversal counting",
   "reconsideración") es capturada; verifica SOLO presencia de la cita (sin
   cambios de formato se verifica aparte con C5b).
6. **C4a scoping al bloque de la tabla de lectura** (`/^## Cómo leer las
   references/,/^## /p`): evita que una mención futura en otra sección del
   SKILL.md haga pasar el check sin que la tabla exista.

## Output RED (estado actual, 2026-09-02)

```
=== C1 -> P1: receiving-feedback.md (una pieza por check) ===
FAIL  C1a existe receiving-feedback.md (exit=1)
FAIL  C1b secuencia 4 pasos (P1a) (exit=1)
FAIL  C1c respuestas prohibidas (P1b) (exit=1)
FAIL  C1d ítems ambiguos -> STOP (P1c) (exit=1)
FAIL  C1e push-back cuándo+cómo+destino (P1d) (exit=1)
FAIL  C1f chequeo YAGNI con grep (P1e) (exit=1)
FAIL  C1g corrección factual (P1f) (exit=1)
FAIL  C1h matriz de fuentes (P1g) (exit=1)
FAIL  C1i persistencia -> scribe/systemPatterns (P1h) (exit=1)
FAIL  C1j ventaja estructural: dilución + sesión fresca (P1i) (exit=1)
FAIL  C1k tabla anti-racionalización (P1j) (exit=1)
FAIL  C1l sección cuándo NO aplica (P1k/R4) (exit=1)
FAIL  C1m prohibición cláusulas de salida (P1l/R2) (exit=1)
=== C2 -> P2: stage-4-review.md (regla del transmisor) ===
FAIL  C2a menciona receiving-feedback (exit=1)
FAIL  C2b regla del transmisor: íntegro sin suavizar (exit=1)
FAIL  C2c orden al receptor: aplicar protocolo antes de tocar código (exit=1)
=== C3 -> P3: anti-patterns.md AP-16 ===
FAIL  C3a encabezado '^## AP-16' (exit=1)
FAIL  C3b 3 sub-secciones (Síntoma/Por qué es malo/Corrección) en bloque AP-16 (exit=1)
FAIL  C3c AP-16 cita la reference receiving-feedback (exit=1)
=== C4 -> P4: mapa de lectura + handoff ===
FAIL  C4a SKILL.md tabla de lectura menciona receiving-feedback.md (exit=1)
FAIL  C4b handoff-prompts.md: transmisión íntegra + invocación del protocolo (exit=1)
=== C5 -> invariante reconsideración (verdict-tuple.md) ===
FAIL  C5a cita steelman/reversal/reconsideración (exit=1)
PASS  C5b GUARD formato intacto (R3): tuple de 4 campos
=== C6 -> criterio 7 (post-GREEN, NO se corren en RED) ===
POST-GREEN  C6a bash tests/validate-odoo-specialization.sh -> 121/121
POST-GREEN  C6b checks cdad-004 (C1a-C1f, C2a-C2b, C3a-C3b) -> 10/10  (correr: run-checks.sh --full)
---
RESUMEN: PASS=1 FAIL=22 (checks de contenido: 23; C6 corre post-GREEN)
```

Todos los checks de contenido fallan por contenido ausente: `exit=1` (ancla
ausente o archivo inexistente) — equivalente AssertionError, nunca error de
invocación. C5b es GUARD y pasa hoy por diseño (el formato del tuple está
intacto ANTES de tocar nada; su valor es seguir en PASS tras GREEN). No hay
ninguna parte de P1-P4 ya satisfecha hoy (grep `receiving` = 0 en todo
`skills/cdad-cycle/`; verdict-tuple sin steelman/reversal). **22/23 RED**
(criterio de aceptación 6 del spec).

## Estado por criterio de aceptación (RED)

| Criterio | Estado |
| -------- | ------ |
| 1. receiving-feedback.md con las 12 piezas de P1 | 🔴 RED (C1a-C1m) |
| 2. stage-4-review.md: protocolo + regla del transmisor | 🔴 RED (C2a-C2c) |
| 3. anti-patterns.md: AP-16 con 3 sub-secciones | 🔴 RED (C3a-C3c) |
| 4. SKILL.md (tabla lectura) + handoff-prompts.md mencionan protocolo | 🔴 RED (C4a-C4b) |
| 5. verdict-tuple.md cita reconsideración sin cambiar formato | 🔴 RED cita (C5a) + ✅ guard formato (C5b) |
| 6. RED definido ANTES de editar y fallando | ✅ output arriba (22/23; C5b guard PASS por diseño) |
| 7. Sin regresión (cdad-003 121/121 + cdad-004 10/10) | ⏳ C6a-C6b se corren post-GREEN |
