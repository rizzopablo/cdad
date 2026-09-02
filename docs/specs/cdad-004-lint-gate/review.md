# cdad-004-lint-gate — Review (Etapa 4)

> **Caveat de aislamiento (registrado):** el runtime de delegación read-only
> (delegate) falló 8/8 por timeout; el review se ejecutó INLINE por el
> orquestador (regla §4 opción 3 del skill cdad-cycle) — mismo contexto que
> quien draftó el spec, garantía anti-bias débil. Los checks mecánicos son
> reproducibles; el juicio, verificable en chat nuevo si se desea.

## Layer 1 — Verificación contra spec

| Postcondición | Estado | Evidencia |
|---|---|---|
| P1 target `make lint` | ✅ | SKILL.md: fila en tabla (:24), reglas 6-8 con `--no-overwrite` (R1), pin `uvx pre-commit-vauxoo==8.3.18` (R2), host (R3), sin autofixes (R4); conteo "3→4 targets" actualizado en principio, procedimiento y frontmatter |
| P2 evidencia lint obligatoria | ✅ | odoo-reviewer: typo `hoo-oca` eliminado (repo-wide grep = 0), evidencia 3→4 ítems, W/C advisory explícito |
| P3 gates en agentes | ✅ | implementer-odoo: lint en verificación GREEN; reviewer-odoo: lint en checklist y evidencia |
| P4 sync instalación | ✅ | `install.sh --check`: 27/27 in sync (perfil basic) |

Restricciones R1-R4 respetadas. Invariante de scope (solo 4 archivos) respetada por el implementer. Criterios de aceptación 1-3 con checks verdes (VALIDATION.md, 10/10), 4 verificado arriba, 5 con output RED pegado.

## Layer 2 — Calidad

- Suite cdad-003: **121/121** (incluye fix POST-AUDIT del assert stale `odoo-dev-methodology` → `assert_file_not_has`, commit 3020a09 — justificado: evita oráculo duplicado con el assert `odoo-expert` y vela la regresión del skill retirado).
- Fix test stale fue el único cambio en `tests/` — autorizado como POST-AUDIT aparte, no parte de GREEN.

## Hallazgos

| # | Severidad | Ubicación | Problema | Sugerencia |
|---|---|---|---|---|
| H1 | **mandatory** | `skills/odoo-make-env/references/odoo-sh.md:3` | Dice "los 3 targets" — drift colateral que contradice el contrato de 4; el spec prohibía tocar references/ y el implementer respetó el scope | Enmienda de 1 línea ("los 4 targets" + nota de que lint corre en host), como cambio menor fuera del spec original — decisión del usuario |
| H2 | advisory | `agents/cdad-reviewer-odoo.md:51` | La reescritura dejó "¿y oca-checks 0 hallazgos?" con sintaxis torpe (corrige el garabato "¿colla" previo, pero quedó medio trunco) | Reescribir la pregunta completa |
| H3 | advisory | Proceso | `make lint` no ha corrido aún contra un addon Odoo real (el contrato existe, la validación de uso pendiente) | Dogfood: primera feature Odoo real que corra `make lint` valida pin/uvx/red; registrar en esa feature |

## Veredicto

`aprobado-con-observaciones` — 1 bloqueante de documentación (H1, decisión de enmienda pendiente del usuario), 2 opcionales.

LISTO. Resumen: 1 bloqueante, 2 opcionales.
