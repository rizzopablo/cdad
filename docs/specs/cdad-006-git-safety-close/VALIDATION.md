# VALIDATION — cdad-006-git-safety-close

Framework documental: checks de estructura en `run-checks.sh` (patrón cdad-004/005).
Corren desde la raíz del repo (`cdad/`). `bash docs/specs/cdad-006-git-safety-close/run-checks.sh`
(contenido+guard) y `--full` post-GREEN (criterio 5).

## Desviación detectada en AUDIT (importante para el implementer)

El spec (P1) dice que la sección se incorpora como **§5.4 "Cierre de la branch
(git safety)"**, pero `stage-5-merge.md` **ya tiene** `## 5.4 — Decisión sobre
ADR` y `## 5.5 — Merge`. Verificado por grep de encabezados en AUDIT.

Resolución aplicada en los checks: el ancla es **agnóstica al número**
(`^## 5\.[0-9]+ — Cierre de la branch`) y el guard C3d exige que
`## 5.4 — Decisión sobre ADR` siga intacto (no clobbered). El implementer debe
ubicar la nueva sección DESPUÉS de 5.5 (p.ej. `## 5.6 — Cierre de la branch
(git safety)`), lo cual además respeta R2 (cierre existente no se reordena).
Si se prefiere el literal "§5.4" del spec, requiere enmienda del spec — el
check no lo fuerza porque forzar duplicado de numeración rompería la
estructura existente.

## AUDIT (baseline, 2026-09-02)

| Suite | Resultado |
|---|---|
| `bash tests/validate-odoo-specialization.sh` (cdad-003) | **121/121 PASS** |
| `bash docs/specs/cdad-005-receiving-feedback/run-checks.sh` | **23/23 PASS** |
| Checks cdad-004 (C6b del `--full` de cdad-005) | **10/10 PASS** |

Grep de cobertura previa (`5.4|AP-17|discard|worktree` en
`stage-5-merge.md` y `anti-patterns.md`): **0 matches relevantes** — el único
match es `## 5.4 — Decisión sobre ADR` (sección preexistente, sin contenido de
cierre de branch). No hay AP-17, no hay `discard`, no hay cobertura de
worktrees. Confirma: el comportamiento nuevo no existe hoy.

- **Tests a modificar: 0** — ninguna suite previa (cdad-003/004/005) toca el
  comportamiento nuevo; R5 (alcance cerrado) garantiza que ningún archivo
  validado por suites previas cambia.
- **Tests untouched (explícitos):** los 121 asserts de cdad-003, los 23
  checks de cdad-005 (C1a–C1m, C2a–C2c, C3a–C3c, C4a–C4b, C5a–C5b) y los 10
  checks de cdad-004 (C1a–C1f, C2a–C2b, C3a–C3b). Verificados AHORA (PARTE
  baseline): todos GREEN.
- **Tests nuevos: 19** (13 RED de contenido + 6 GUARD).
- **Riesgos de regresión:** bajo. El único riesgo es que la edición de
  `stage-5-merge.md` clobberere encabezados previos → mitigado por C3a–C3f
  (guard que PASA hoy y debe seguir en GREEN). Regresión cruzada en
  cdad-003/004/005 → mitigada por C4 `--full` post-GREEN.

## Mapa check ↔ postcondición

| Check | Postcondición / pieza | Criterio PASS |
|---|---|---|
| C1a | P1: encabezado de sección `## 5.N — Cierre de la branch` | grep encabezado (número agnóstico, ver desviación) |
| C1b | P1a: detección `--git-dir`/`--git-common-dir` + guard `--show-superproject-working-tree` | 3 greps en scope del bloque |
| C1c | P1b: base branch confirmada, nunca asumida | `nunca` + `confirmar|confirmación` en scope |
| C1d | P1c: menú fijo 4 opciones (merge local / PR / keep / discard) | 4 greps en scope |
| C1e | P1d: conflicto STOP sin auto-resolver + re-verificación de suite | `STOP` + `auto-resolver` negado + `re-verificación` |
| C1f | P1f/R4: `discard` palabra literal en el bloque | grep `discard` en scope |
| C1g | P1g/R3: limpieza por provenance, solo worktrees propios | `\.worktrees\|provenance\|propios` |
| C1h | P1g: `prune` | grep `prune` en scope |
| C1i | P1h: orden crítico merge → worktree → branch | `merge primero` (o equivalente) |
| C1j | P1i: anti-racionalización + cuándo NO aplica (squash, monorepo) | 4 greps en scope |
| C2a | P2: encabezado `## AP-17` | grep anclado a línea |
| C2b | P2: 3 sub-secciones Síntoma/Por qué es malo/Corrección | sed scope bloque AP-17 |
| C2c | P2: AP-17 cita §5.4/stage-5 | grep en scope AP-17 |
| C3a–C3f | criterio 3 (GUARD): `## 5.1`/`5.2`/`5.3`/`5.4 ADR`/`5.5 Merge`/Gate presentes | PASS hoy, debe seguir en GREEN |
| C4a–C4c | criterio 5 (post-GREEN, `--full`): suites cdad-003/004/005 verdes | 121/121 + 10/10 + 23/23 |

Anti-falso-positivo (lecciones cdad-004/005): ancla `test -f` en todo check de
contenido; acentos con alternancia `(ó|o)`/`(á|a)`; scope de bloque con
`sed -n '/^## AP-17/,/^## AP-[0-9]/p'`; scope de la nueva sección con el
título completo "Cierre de la branch" (evita falsos positivos de `## 5.4`
preexistente).

## RED — output sobre estado actual (2026-09-02)

```
=== C1 -> P1: stage-5-merge.md sección Cierre de la branch (una pieza por check) ===
FAIL  C1a encabezado '## 5.N — Cierre de la branch (git safety)' (exit=1)
FAIL  C1b detección git-dir/git-common-dir + guard submodule (P1a) (exit=1)
FAIL  C1c base branch confirmada, nunca asumida (P1b) (exit=1)
FAIL  C1d menú fijo 4 opciones (P1c) (exit=1)
FAIL  C1e conflicto STOP sin auto-resolver + re-verificación de suite (P1d) (exit=1)
FAIL  C1f discard palabra literal (P1f/R4) (exit=1)
FAIL  C1g limpieza por provenance, solo worktrees propios (P1g/R3) (exit=1)
FAIL  C1h prune (P1g) (exit=1)
FAIL  C1i orden crítico merge -> worktree -> branch (P1h) (exit=1)
FAIL  C1j anti-racionalización + cuándo NO aplica squash/monorepo (P1i) (exit=1)
=== C2 -> P2: anti-patterns.md AP-17 ===
FAIL  C2a encabezado '^## AP-17' (exit=1)
FAIL  C2b 3 sub-secciones (Síntoma/Por qué es malo/Corrección) en bloque AP-17 (exit=1)
FAIL  C2c AP-17 cita §5.4 / stage-5 (exit=1)
=== C3 -> criterio 3: GUARD encabezados previos intactos (PASS hoy) ===
PASS  C3a 5.1 CI presente
PASS  C3b 5.2 Handoff al Scribe presente
PASS  C3c 5.3 Validación del usuario presente
PASS  C3d 5.4 — Decisión sobre ADR intacta (no clobbered)
PASS  C3e 5.5 — Merge intacto
PASS  C3f Gate de salida presente
=== C4 -> criterio 5 (post-GREEN) ===
POST-GREEN  C4a bash tests/validate-odoo-specialization.sh -> 121/121
POST-GREEN  C4b checks cdad-004 -> 10/10  (correr: run-checks.sh --full)
POST-GREEN  C4b' checks cdad-005 -> 23/23
---
RESUMEN: PASS=6 FAIL=13 (checks de contenido + guard: 19; C4 corre con --full post-GREEN)
```

Los 13 checks de contenido fallan por la razón correcta (grep exit=1:
contenido inexistente, no errores de script). C3 guard pasa por diseño.

## Estado por criterio de aceptación

| Criterio | Estado |
|---|---|
| 1. `## 5.4`/sección con 9 piezas de P1 | **RED** (C1a–C1j fallan) → GREEN al implementar |
| 2. `## AP-17` con 3 sub-secciones | **RED** (C2a–C2c fallan) → GREEN al implementar |
| 3. Encabezados previos intactos | **PASS hoy** (C3a–C3f) — guard, debe seguir en GREEN |
| 4. Checks definidos ANTES de editar y fallando hoy | **CUMPLIDO** (output RED arriba) |
| 5. Sin regresión (003/004/005 verdes) | Baseline verde hoy; verificar con `--full` post-GREEN |

Pendiente: GREEN por el implementer (edita SOLO stage-5-merge.md y
anti-patterns.md), luego `run-checks.sh` (19/19) y `run-checks.sh --full`.
