# cdad-004-lint-gate — VALIDATION.md

> Materializado por el orquestador desde el output del test-writer (sesión
> aislada, 2026-09-02), patrón Contrato de roles §5 del skill cdad-cycle.

## Test Audit (3.0)

- **Comportamiento que cambia:** `odoo-reviewer/SKILL.md` línea 56
  (`pre-commit limpio (hoo-oca...) si el repo lo usa`) es reemplazada por P2;
  la evidencia pasa de 3 a 4 ítems; `odoo-make-env` pasa de 3 a 4 targets
  (P1); los agentes Odoo ganan una exigencia de gate (P3).
- **Cobertura previa:** existe `tests/validate-odoo-specialization.sh`
  (cdad-003, 121 asserts). Grep del suite: `pre-commit` aparece solo en un
  **comentario** sobre la allowlist bash (línea 124) y `pylint-odoo` como
  aserción de contenido cdad-003 (línea 168). **Ningún assert cubre P1-P4 de
  cdad-004.**
- **Tests a modificar: 0** — ninguna aserción valida la línea que P2 elimina
  ni el conteo de ítems. Suite de cdad-003 queda **untouched**.
- **Tests nuevos: 10** automatizados + 1 paso manual (C4).
- **Regression risks:** bajo; el único riesgo es que el implementer toque
  `references/`/agentes genéricos (prohibido por invariante del spec) y rompa
  asserts de cdad-003 → tras GREEN, `tests/validate-odoo-specialization.sh`
  debe seguir 121/121.
- Sin benefit-of-doubt pendiente: primera feature con checks para estos
  skills.

## Mapeo check ↔ postcondición

| Check   | Postcondición | Qué valida                                                                                                                    |
| ------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| C1a-C1f | P1 (+R2, R3)  | `odoo-make-env`: fila `make lint` en tabla + `--no-overwrite` + `--diff` + `--all` + pin `uvx pre-commit-vauxoo==X` + regla host |
| C2a,C2b | P2            | `odoo-reviewer`: 0 ocurrencias "hoo-oca" + ítem 4 de "Evidencia requerida" exige output de lint                                  |
| C3a,C3b | P3            | `cdad-implementer-odoo.md`: lint en gate GREEN; `cdad-reviewer-odoo.md`: lint en checklist                                       |
| C4      | P4            | `install.sh --check` sin drift tras sincronizar (manual)                                                                        |

## Checks (comandos exactos, corren desde la raíz del repo)

| id  | Comando                                                                                                                                | PASS                     |
| --- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| C1a | `grep -nE '^\|.*\`make lint\`.*\|' skills/odoo-make-env/SKILL.md`                                                                        | fila de tabla con `make lint` |
| C1b | `grep -q -- '--no-overwrite' skills/odoo-make-env/SKILL.md`                                                                               | menciona `--no-overwrite` |
| C1c | `grep -q -- '--diff' skills/odoo-make-env/SKILL.md`                                                                                       | menciona `--diff`         |
| C1d | `grep -qE -- '--all\b' skills/odoo-make-env/SKILL.md`                                                                                     | menciona `--all`          |
| C1e | `grep -qE 'uvx pre-commit-vauxoo==[0-9]+\.' skills/odoo-make-env/SKILL.md`                                                               | pin de versión (R2)       |
| C1f | `grep -qiE '(lint\|pre-commit).*host\|host.*(lint\|pre-commit)' skills/odoo-make-env/SKILL.md`                                           | vincula lint con host (R3) |
| C2a | `[ "$(grep -c 'hoo-oca' skills/odoo-reviewer/SKILL.md)" -eq 0 ]`                                                                          | typo corregido            |
| C2b | `sed -n '/[Ee]videncia requerida/,/^## /p' skills/odoo-reviewer/SKILL.md \| grep -qE '^4\..*(\bmake lint\b\|\blint\b)'`                   | ítem 4 exige lint         |
| C3a | `grep -qE 'lint limpio\|make lint' agents/cdad-implementer-odoo.md`                                                                      | gate GREEN exige lint     |
| C3b | `grep -qE 'lint limpio\|make lint' agents/cdad-reviewer-odoo.md`                                                                         | checklist verifica lint   |
| C4  | `bash install.sh` + `bash install.sh --check` (manual, post-fix)                                                                          | output sin drift          |

**Corrección de oráculo (documentada por el test-writer):** C3a/C3b con
`lint` a secas daban falso positivo por "pylint-odoo" (presente por
cdad-003). Se acotó a `lint limpio|make lint` — falso-positivo-imposible,
coherente con la lección de cdad-003 (oráculo demasiado amplio degrada).

## Output RED (estado actual, 2026-09-02)

```
FAIL  C1a fila 'make lint' en tabla del contrato   (exit=1)
FAIL  C1b menciona --no-overwrite   (exit=1)
FAIL  C1c menciona --diff   (exit=1)
FAIL  C1d menciona --all   (exit=1)
FAIL  C1e invocación pinneada uvx pre-commit-vauxoo==X (R2)   (exit=1)
FAIL  C1f regla 'corre en host' (R3)   (exit=1)
FAIL  C2a cero ocurrencias de 'hoo-oca'   (exit=1)
FAIL  C2b ítem 4 de 'Evidencia requerida' exige output de lint   (exit=1)
FAIL  C3a implementer-odoo: lint en gate GREEN   (exit=1)
FAIL  C3b reviewer-odoo: lint en checklist de evidencia   (exit=1)
=== C4 → P4: paso manual (documentado, no automatizado en RED) ===
MANUAL  bash install.sh --check  → PASS: output sin drift tras los cambios
```

Todos fallan por contenido: exit=1 (patrón ausente) en C1a-C1f, C2b, C3a,
C3b; C2a falla porque el typo **está** presente (count=1, línea 56).
**10/10 RED** (criterio de aceptación 5 del spec).

## Estado por criterio de aceptación (RED)

| Criterio                                | Estado                        |
| --------------------------------------- | ----------------------------- |
| 1. odoo-make-env (fila lint + flags)    | 🔴 RED (C1a-C1f)              |
| 2. odoo-reviewer (sin hoo-oca, 4 ítems) | 🔴 RED (C2a-C2b)              |
| 3. agentes (gate GREEN / checklist)     | 🔴 RED (C3a-C3b)              |
| 4. install.sh --check sin drift         | ⏳ paso manual post-fix (C4)   |
| 5. RED definido antes y fallando        | ✅ este output                |
