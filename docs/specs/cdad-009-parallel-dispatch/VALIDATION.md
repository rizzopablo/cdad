# VALIDATION — cdad-009-parallel-dispatch

Framework documental: checks de estructura en `run-checks.sh` (patrón
cdad-004..008). Corren desde la raíz del repo (`cdad/`):
`bash docs/specs/cdad-009-parallel-dispatch/run-checks.sh` (contenido+guard)
y `--full` post-GREEN (criterio sin-regresión, ahora incluye 008). Contrato:
research.md de `docs/epics/research-tema5-parallel/` § "Propuesta adaptada".
Formato: cycle light (mismo patrón que cdad-007/008: AUDIT+RED y frenar).

## AUDIT (baseline, 2026-09-02)

| Suite                                                       | Resultado    |
| ----------------------------------------------------------- | ------------ |
| `bash tests/validate-odoo-specialization.sh` (cdad-003)       | **121/121 PASS** |
| `bash docs/specs/cdad-005-receiving-feedback/run-checks.sh`   | **23/23 PASS**   |
| `bash docs/specs/cdad-006-git-safety-close/run-checks.sh`     | **19/19 PASS**   |
| `bash docs/specs/cdad-007-systematic-debugging/run-checks.sh` | **23/23 PASS**   |
| `bash docs/specs/cdad-008-granular-planning/run-checks.sh`    | **17/17 PASS**   |

Grep de cobertura previa (`paralel|wave|owned files|worktree|despach` en
`stage-3-tdd.md`, `sub-agent-strategies.md` y `SKILL.md`): **0 matches** —
re-verificado hoy; el gap del research es real.

Anclas verificadas hoy (para scopes y guards):

- `stage-3-tdd.md`: packet ortogonal en l.77 ("agrupación de postcondiciones
  **ortogonales** (paths de código independientes que no se pisan)", dentro
  de `## Sub-fase 3.1 — RED`, l.70). `## Sub-fase 3.2 — GREEN` en l.98 → la
  sección "Despacho paralelo" se inserta ENTRE ambas (tras el re-entry de
  3.1, antes de 3.2). El check C1a fija la posición por comparación de
  números de línea (l.77 < l(nueva) < l.98), no por línea absoluta.
- `sub-agent-strategies.md`: 6 encabezados `##` existentes (l.5, 9, 97, 107,
  131, 144). La subsección `### Sesiones paralelas del mismo rol` es
  aditiva (el scope awk corta en el próximo `## ` o EOF).
- `SKILL.md`: regla §6 en l.184 (`### 6. Regla de state-passing` + "No
  asumas que recuerda nada"); tabla de lectura l.415 con la fila agrupada
  `stage-1-discovery.md ... stage-5-merge.md` que ya cubre stage-3-tdd.md.
- Cita §5.6 verificada: `stage-5-merge.md:82` ("Cierre de la branch — git
  safety"), con "Limpieza por provenance" en l.128 — base de la referencia
  de cleanup de P1g.

**Decisión P3 (documentada):** la tabla de lectura de SKILL.md ya cubre
`stage-3-tdd.md` con la fila agrupada (`stage-1-discovery.md ... stage-5-
merge.md` → "Cuando estás en esa etapa"). NO requiere fila nueva: la sección
"Despacho paralelo" vive en stage-3 y es descubrible por esa fila. P3 se
valida con C3a (la fila agrupada existe y cubre stage-3 — guard, PASS hoy)
y C3b (no-expansión: SKILL.md no duplica la sección — guard, PASS hoy). La
presencia del contenido en stage-3 la chequea C1a. El implementer NO toca
SKILL.md en esta feature.

- **Tests a modificar: 0** — ninguna suite previa (003..008) toca despacho
  paralelo; las ediciones son aditivas (sección nueva entre l.96 y l.98 de
  stage-3; subsección `###` nueva en sub-agent-strategies) sin reordenar
  encabezados existentes (guardado por C4a–C4d).
- **Tests untouched (explícitos):** los 121 asserts de cdad-003 y los checks
  de cdad-005 (23), 006 (19), 007 (23) y 008 (17) — incluidos sus guards
  sobre stage-2/stage-3/SKILL.md/anti-patterns que esta feature no toca.
  Todos verificados AHORA: GREEN (tabla baseline).
- **Tests nuevos: 15** (9 RED de contenido: C1a–C1g, C2a–C2b; + 6 guard
  PASS hoy: C3a, C3b, C4a–C4d) + C5 post-GREEN (003–008, ahora 5 suites).
- **Riesgos de regresión:** bajo. Ediciones aditivas en dos references;
  riesgo de clobber de encabezados/packet ortogonal mitigado por C4a–C4d.
  Riesgo de duplicación en SKILL.md mitigado por C3b. Regresión cruzada en
  suites previas → C5 `--full` post-GREEN (incluye 008 por primera vez).

## Mapa check ↔ postcondición

| Check   | Postcondición / pieza                                                                                                                                               | Criterio PASS                                                                 |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| C1a     | P1a: encabezado `## Despacho paralelo` + posición (tras packet ortogonal l.77, antes de Sub-fase 3.2 l.98) + árbol (2+ tareas genuinamente independientes → paralelo) | `test -f` + encabezado + comparación de números de línea + 2 greps en scope PAR |
| C1b     | P1b: árbol — comparten archivo/estado → secuencial o wave dispatch; packet ortogonal sigue siendo el default                                                        | 5 greps en scope PAR                                                          |
| C1c     | P1c: precondición — contrato de interfaz Consumes/Produces (ver stage-2 "Planning de features complejas"); sin él no hay despacho paralelo                          | 5 greps en scope PAR                                                          |
| C1d     | P1d: reglas de despacho — prompt autocontenido (§6) con owned files + do-not-touch list; scope disjunto `git diff --name-only`; mismo rol, sesiones distintas         | 6 greps en scope PAR                                                          |
| C1e     | P1e: integración final solo orquestador — resúmenes → overlap (`git diff --name-only` + `comm`) → suite COMPLETA una vez; conflictos nunca los subagentes               | 6 greps en scope PAR                                                          |
| C1f     | P1f: state file SOLO el orquestador, siempre; sesiones paralelas nunca lo tocan                                                                                     | 3 greps en scope PAR                                                          |
| C1g     | P1g: wave dispatch default conservador + worktree-per-agent opción (cita §5.6 provenance) + tabla anti-racionalización (4-6 filas)                                  | 7 greps en scope PAR                                                          |
| C2a     | P2a: subsección `### Sesiones paralelas del mismo rol` + aislamiento se mantiene + orquestador despacha/consolida                                                     | `test -f` + encabezado + 3 greps en scope SUBPAR                                |
| C2b     | P2b: state file solo lo escribe el orquestador (en la subsección)                                                                                                   | 3 greps en scope SUBPAR                                                       |
| C3a     | P3: fila agrupada de la tabla de lectura cubre stage-3-tdd.md (decisión audit, guard)                                                                               | grep fila agrupada; PASS hoy                                                  |
| C3b     | P3 no-expansión: SKILL.md sin encabezado propio de despacho paralelo                                                                                                | grep negado; PASS hoy                                                         |
| C4a     | GUARD: packet ortogonal en stage-3 intacto (l.77)                                                                                                                   | grep frase exacta                                                             |
| C4b     | GUARD: `## Sub-fase 3.2 — GREEN` + `## 🛑 Gate de salida (Etapa 3 → Etapa 4)` intactos                                                                                  | 2 greps con encabezado completo (—/🛑)                                        |
| C4c     | GUARD: 4 encabezados de sub-agent-strategies.md intactos                                                                                                            | 4 greps con encabezado completo                                               |
| C4d     | GUARD: regla §6 de SKILL.md intacta                                                                                                                                 | 2 greps                                                                       |
| C5a–C5e | post-GREEN (`--full`): suites 003/005/006/007/008 verdes                                                                                                              | 121/121 + 23/23 + 19/19 + 23/23 + 17/17                                       |

Anti-falso-positivo (lecciones cdad-004..008): ancla `test -f` en C1a/C2a/
C3a/C3b/C4d; acentos con alternancia `(ó|o)`/`(ú|u)`/`(á|a)`/`(é|e)`; scope
PAR delimitado por el próximo `## ` vía awk (la sección puede crecer sin
romper los scopes); posición de C1a por comparación de números de línea (no
línea absoluta — robusta a ediciones previas); frases multi-palabra exactas
("genuinamente independiente", "owned files", "do-not-touch", "nunca los
subagentes", "default conservador") difíciles de falsificar con prosa
vecina; `git diff --name-only` con grep -qF (string literal); guards C4a–
C4d usan encabezados completos con `—`/`🛑` para no confundir con menciones
en prosa; C3b niega el grep solo sobre encabezado (`^#+ .*Despacho
paralelo`), NO sobre menciones en prosa.

## RED — output sobre estado actual (2026-09-02)

```
=== C1 -> P1: stage-3-tdd.md sección 'Despacho paralelo' (7 piezas) ===
FAIL  C1a P1a: ... (exit=1)
FAIL  C1b P1b: ... (exit=1)
FAIL  C1c P1c: ... (exit=1)
FAIL  C1d P1d: ... (exit=1)
FAIL  C1e P1e: ... (exit=1)
FAIL  C1f P1f: ... (exit=1)
FAIL  C1g P1g: ... (exit=1)
=== C2 -> P2: sub-agent-strategies.md subsección aditiva 'Sesiones paralelas del mismo rol' ===
FAIL  C2a P2a: ... (exit=1)
FAIL  C2b P2b: ... (exit=1)
=== C3 -> P3: SKILL.md tabla de lectura ===
PASS  C3a (guard, PASS hoy)
PASS  C3b (guard, PASS hoy)
=== C4 -> GUARD ===
PASS  C4a-C4d (4/4, PASS hoy)
---
RESUMEN: PASS=6 FAIL=9 (checks de contenido + guard: 15; C5 corre con --full post-GREEN)
```

Los 9 checks de contenido fallan por la razón correcta (grep sin match —
la sección/subsección no existen). Los 6 guards pasan por diseño.

## Estado por criterio de aceptación

| Criterio                                                                 | Estado                                                     |
| ------------------------------------------------------------------------ | ---------------------------------------------------------- |
| 1. P1: sección "Despacho paralelo" (7 piezas a–g)                        | **RED** (C1a–C1g) → GREEN al implementar                       |
| 2. P2: subsección "Sesiones paralelas del mismo rol"                     | **RED** (C2a–C2b) → GREEN al implementar                       |
| 3. P3: SKILL.md — fila agrupada existente alcanza (decisión documentada) | **PASS hoy** (C3a–C3b guard) — el implementer no toca SKILL.md |
| 4. Invariantes: packet ortogonal + encabezados + §6 intactos             | **PASS hoy** (C4a–C4d) — guard, debe seguir en GREEN           |
| 5. Checks definidos ANTES de editar y fallando hoy                       | **CUMPLIDO** (output RED arriba)                               |
| 6. Sin regresión (003/005/006/007/008 verdes)                            | Baseline verde hoy; verificar con `--full` post-GREEN        |

Pendiente: GREEN por el implementer (edita SOLO
skills/cdad-cycle/references/stage-3-tdd.md [sección "Despacho paralelo"
entre l.96 y l.98] y skills/cdad-cycle/references/sub-agent-strategies.md
[subsección `### Sesiones paralelas del mismo rol` aditiva]), luego
`run-checks.sh` (15/15) y `run-checks.sh --full`.
