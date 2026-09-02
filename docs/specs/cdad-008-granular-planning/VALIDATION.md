# VALIDATION — cdad-008-granular-planning

Framework documental: checks de estructura en `run-checks.sh` (patrón
cdad-004/005/006/007). Corren desde la raíz del repo (`cdad/`):
`bash docs/specs/cdad-008-granular-planning/run-checks.sh` (contenido+guard)
y `--full` post-GREEN (criterio sin-regresión). Contrato: research.md de
`docs/epics/research-tema4-planning/` § "Propuesta adaptada". Formato: cycle
light (mismo patrón que cdad-007: AUDIT+RED y frenar).

## AUDIT (baseline, 2026-09-02)

| Suite | Resultado |
|---|---|
| `bash tests/validate-odoo-specialization.sh` (cdad-003) | **121/121 PASS** |
| `bash docs/specs/cdad-005-receiving-feedback/run-checks.sh` | **23/23 PASS** |
| `bash docs/specs/cdad-006-git-safety-close/run-checks.sh` | **19/19 PASS** |

Grep de cobertura previa (`plan\.md|placeholder|Consumes` en
`stage-2-specification.md` y `agents/cdad-architect.md`):

- `stage-2-specification.md:90` — **la línea exacta**: `- **Compleja**
  (múltiples componentes): dividir en \`spec.md\`, \`plan.md\`, \`tasks.md\`.`
  (dentro de `## Variantes según tamaño`, l.86). Es la ÚNICA mención de
  `plan.md` en el archivo.
- `placeholder`: solo l.101 ("Cuatro secciones mínimas presentes y no son
  placeholders", en el Gate 2→3) — sobre el spec, no sobre planes. Sin
  relación con el comportamiento nuevo; el gate pasa a referenciar plan.md
  además (C1a lo guarda en scope G23).
- `Consumes`: **0 matches** en ambos archivos. `agents/cdad-architect.md`:
  **0 matches** de "plan" (scope actual = brainstorm + draft de spec).
- `anti-patterns.md`: último AP es `## AP-18 — Fix sin diagnóstico
  (thrashing)` (l.166, cdad-007). **No existe AP-19** → AP-19 se agrega al
  final y el scope `sed -n '/^## AP-19/,$p'` imprime a EOF (ancla válida).
- `cdad-epic/SKILL.md`: menciona `plan.md` 3 veces pero TODO a nivel epic
  (plan corto de epic); **0 matches de "granular"** → ancla del guard C4e.

Encabezados verificados hoy (para guards C4, en `stage-2-specification.md`):
`## Variantes según tamaño` (l.86), `## Por qué la claridad del spec no es
negociable` (l.94), `## 🛑 Gate de salida (Etapa 2 → Etapa 3)` (l.98),
`## Si surge algo no contemplado en spec durante implementación` (l.108).

- **Tests a modificar: 0** — ninguna suite previa (003/004/005/006/007) toca
  planning de features complejas; la línea 90 se expande en una sección nueva
  SIN reordenar encabezados existentes (guardado por C4a–C4d).
- **Tests untouched (explícitos):** los 121 asserts de cdad-003, los 23
  checks de cdad-005, los 19 de cdad-006 y los 23 de cdad-007 (incluye sus
  guards sobre stage-3/stage-5/SKILL.md, que esta feature no toca). Todos
  verificados AHORA: GREEN (tabla baseline).
- **Tests nuevos: 17** (12 RED de contenido: C1a–C1g, C2a–C2b, C3a–C3c; +
  5 GUARD C4a–C4e) + C5 post-GREEN.
- **Riesgos de regresión:** bajo. Ediciones en `stage-2-specification.md`
  (reemplazo de línea 90 por sección dentro de "Variantes según tamaño" +
  un bullet en el Gate 2→3), `agents/cdad-architect.md` (sección aditiva) y
  `anti-patterns.md` (append AP-19 al final) podrían clobbererear encabezados
  → mitigado por C4a–C4d. Expansión de scope colateral hacia `cdad-epic`
  (duplicar planning light) → guardado por C4e. Regresión cruzada en suites
  previas → C5 `--full` post-GREEN.

## Mapa check ↔ postcondición

| Check | Postcondición / pieza | Criterio PASS |
|---|---|---|
| C1a | P1a: sección "Planning de features complejas" + disparador (múltiples componentes) + architect produce plan.md + gate 2→3 lo incluye | `test -f` + encabezado + 3 greps en scope PLN + grep en scope Gate 2→3 |
| C1b | P1b: tamaño de tarea — unidad más chica con mini-ciclo TDD propio, reviewer podría rechazar sin rechazar la vecina, setup plegado | 5 greps en scope PLN |
| C1c | P1c: estructura — Files exactos + Consumes/Produces (firmas exactas, apto test-writer) + pasos TDD | 6 greps en scope PLN |
| C1d | P1d: regla central — plan define CONTRATO (aserciones reales, comandos exactos) + comportamiento observable 3-5 bullets verificables + nunca impl especulativa ("escribir la impl dos veces revierte TDD") + test-writer puede ver el plan | 6 greps en scope PLN |
| C1e | P1e: no placeholders — TBD/TODO/"similar a la Tarea N" = falla del plan; vagueza con contrato NO es placeholder | 5 greps en scope PLN |
| C1f | P1f: auto-revisión — cobertura del spec (cada postcondición → ≥1 tarea) + escaneo placeholders + consistencia de firmas | 5 greps en scope PLN |
| C1g | P1g: global constraints del spec verbatim en el header | 3 greps en scope PLN |
| C2a | P2a: cdad-architect.md tiene sección de planificación (produce plan.md cuando el spec es complejo) | `test -f` + encabezado `^#+ .*Planificaci(ó|o)n` + grep disparador |
| C2b | P2b: cdad-architect.md menciona plan.md con las reglas (CONTRATO / comportamiento observable) | 2 greps |
| C3a | P3: encabezado `^## AP-19` | grep anclado a línea |
| C3b | P3: 3 sub-secciones Síntoma/Por qué es malo/Corrección en bloque AP-19 | sed scope bloque AP-19 |
| C3c | P3: AP-19 cita la sección "Planning de features complejas" | grep en scope AP-19 |
| C4a–C4d | GUARD: 4 encabezados de stage-2-specification.md intactos | PASS hoy, deben seguir en GREEN |
| C4e | GUARD: cdad-epic/SKILL.md SIN mención de "granular" (planning light intacto, no-expansión) | grep negado; PASS hoy, debe seguir en GREEN |
| C5a–C5d | post-GREEN (`--full`): suites 003/005/006/007 verdes | 121/121 + 23/23 + 19/19 + 23/23 |

Anti-falso-positivo (lecciones cdad-004..007): ancla `test -f` en C1a/C2a/
C2b/C4e; acentos con alternancia `(ó|o)`/`(ú|u)`/`(á|a)`/`(é|e)`/`(ñ|n)`;
scope de la sección nueva delimitado por el siguiente `## ` no-Planning
(`/^## Planning de features complejas/,/^## [^P]/p`) para que los greps no
 leakage a "Por qué la claridad..."; scope del Gate 2→3 delimitado por
`## Si surge`; scope AP-19 `sed -n '/^## AP-19/,$p'` (AP-19 es el último AP);
guards C4a–C4d usan el encabezado completo con `—`/`🛑` para no confundir con
menciones en prosa; C4e niega el grep (`! grep -qi granular`) sobre la
mención técnica "granular" y NO sobre "plan.md", que cdad-epic usa
legítimamente a nivel epic.

Nota RED: todos los checks de contenido (C1–C3) fallan con exit=1 (grep sin
match porque la sección/sección-architect/AP-19 no existen). En GREEN, si el
contenido existe pero falta una pieza, el grep específico reporta exit=1 —
cada check sigue discriminando pieza por pieza.

## RED — output sobre estado actual (2026-09-02)

```
=== C1 -> P1: stage-2-specification.md sección 'Planning de features complejas' (7 piezas) ===
FAIL  C1a P1a: disparador (spec complejo) + rol (architect produce plan.md además del spec) + gate 2->3 lo incluye si existe (exit=1)
FAIL  C1b P1b: tamaño de tarea — unidad más chica con mini-ciclo TDD propio que un reviewer podría rechazar sin rechazar la vecina + setup plegado (exit=1)
FAIL  C1c P1c: estructura de tarea — Files exactos + Consumes/Produces (contrato público, firmas exactas, apto test-writer) + pasos TDD (exit=1)
FAIL  C1d P1d: regla central — plan define el CONTRATO (aserciones reales, comandos exactos) + comportamiento observable 3-5 bullets verificables + NUNCA impl especulativa (escribir la impl dos veces revierte TDD) + test-writer puede ver el plan entero (exit=1)
FAIL  C1e P1e: no placeholders — lista de frases prohibidas (TBD/TODO/similar a la Tarea N) = falla del plan; vagueza con contrato NO es placeholder (exit=1)
FAIL  C1f P1f: auto-revisión — cobertura del spec (cada postcondición -> >=1 tarea) + escaneo de placeholders + consistencia de firmas entre tareas (exit=1)
FAIL  C1g P1g: global constraints del spec copiadas verbatim en el header (exit=1)
=== C2 -> P2: agents/cdad-architect.md extensión de scope (aditiva) ===
FAIL  C2a P2a: cdad-architect.md tiene sección de planificación (produce plan.md cuando el spec es complejo) (exit=1)
FAIL  C2b P2b: cdad-architect.md menciona plan.md con las reglas (contrato, no implementación) (exit=1)
=== C3 -> P3: anti-patterns.md AP-19 — Plan placeholder ===
FAIL  C3a encabezado '^## AP-19' (exit=1)
FAIL  C3b 3 sub-secciones (Síntoma/Por qué es malo/Corrección) en bloque AP-19 (exit=1)
FAIL  C3c AP-19 cita la sección 'Planning de features complejas' de stage-2-specification.md (exit=1)
=== C4 -> GUARD: encabezados stage-2 intactos + cdad-epic planning light intacto (PASS hoy) ===
PASS  C4a stage-2: '## Variantes según tamaño' intacta
PASS  C4b stage-2: '## Por qué la claridad del spec no es negociable' intacta
PASS  C4c stage-2: '## 🛑 Gate de salida (Etapa 2 → Etapa 3)' intacta
PASS  C4d stage-2: '## Si surge algo no contemplado en spec durante implementación' intacta
PASS  C4e cdad-epic/SKILL.md SIN mención de granular-planning (planning light intacto, no-expansión)
---
RESUMEN: PASS=5 FAIL=12 (checks de contenido + guard: 17; C5 corre con --full post-GREEN)
```

Los 12 checks de contenido fallan por la razón correcta (contenido
inexistente: grep sin match). Los 5 guards C4 pasan por diseño.

## Estado por criterio de aceptación

| Criterio | Estado |
|---|---|
| 1. P1: sección "Planning de features complejas" (7 piezas a–g) | **RED** (C1a–C1g fallan) → GREEN al implementar |
| 2. P2: cdad-architect.md con sección de planificación | **RED** (C2a–C2b fallan) → GREEN al implementar |
| 3. P3: AP-19 con 3 sub-secciones + cita | **RED** (C3a–C3c fallan) → GREEN al implementar |
| 4. Invariantes: encabezados stage-2 + cdad-epic intactos | **PASS hoy** (C4a–C4e) — guard, debe seguir en GREEN |
| 5. Checks definidos ANTES de editar y fallando hoy | **CUMPLIDO** (output RED arriba) |
| 6. Sin regresión (003/005/006/007 verdes) | Baseline verde hoy; verificar con `--full` post-GREEN |

Pendiente: GREEN por el implementer (edita SOLO stage-2-specification.md
[reemplazo de l.90 por la sección + bullet en Gate 2→3],
agents/cdad-architect.md [sección aditiva] y anti-patterns.md [append
AP-19]), luego `run-checks.sh` (17/17) y `run-checks.sh --full`.
