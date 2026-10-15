GREEN de T2 completado y commiteado. Reporte:

## 1. Estado encontrado en el árbol y qué completé

El intento anterior dejó **sin commitear** tres artefactos de producto, con los 10 focales de T2 ya verdes. Los revisé contra la spec §2.3/§2.4/§2.5/§2.9 y el plan §3 (ficha T2):

- `skills/cdad-cycle/assets/orientation-examples.json` (nuevo): traía el **conjunto mínimo** (§2.3) correcto —`dispatch-record` (`docs/attempt.json` con los 6 campos exactos), `continuity-update` (`goal/decisions/uncertainties/next_action` + `packet_id`/`attempt` que el CLI exige) y `status-view` (`cdad_packet.py status --project-root <ABS>`)—, pero **faltaba el ejemplo inválido** que el objetivo exige y que la propia referencia declaraba como parte del asset («its negative cases»). **Completé**: agregué `dispatch-record-invalid` (mismo `attempt.json` sin `runtime`) con su expectativa declarada (`rc_nonzero`, `diagnostic_names_field: "runtime"`).
- `skills/cdad-cycle/references/orientation.md` (modificado): completa (§2.3/§2.5), pero la tabla de operaciones frecuentes no exponía **efectos** como elemento propio (la spec §2.3 los lista). **Completé**: columna `Effect` en la tabla (read-only / falla cerrado / escribe bajo `.cdad/` / mueve a `dispatched` / congela checkpoint), y precisé el ejemplo inválido en la sección del `attempt.json`.
- `skills/cdad-cycle/references/project-start.md` (modificado): ya correcto —§11 consulta **primero** la vista `status`, amplía solo ante necesidad concreta (bloqueo/duda), por referencia y sin copiar la estructura de los dueños (INV-3). Sin cambios míos.

**No toqué** `docs/.cdad-state.json` (queda sin commitear, del orquestador) ni `tests/**`.

## 2. Archivos tocados (diff resumido)

- `skills/cdad-cycle/assets/orientation-examples.json` — nuevo, 75 líneas; 4 ejemplos (`dispatch-record`, `dispatch-record-invalid`, `continuity-update`, `status-view`).
- `skills/cdad-cycle/references/orientation.md` — +75/−9: columna `Effect`, sección `Continuity update`, `Executable examples asset`, `Version disposition and the meter`, `Actionable errors`.
- `skills/cdad-cycle/references/project-start.md` — +19: §11 `Orient first — the compact view, then expand on a concrete need`.

## 3. Comandos y salidas

| Comando | Salida |
|---|---|
| `python3 -m pytest tests/test_005_003_t2_examples_execute.py -q` | **10 passed** |
| `python3 -m pytest tests/test_005_006_t1_start_procedure.py -q` | **15 passed** |
| `python3 -m pytest tests/test_005_003_t1_compact_view.py -q` | **11 passed** |
| `python3 -m pytest tests/ -q -k "packet or state or role_packet or orientation"` | **133 passed**, 695 deselected (baseline medido antes de mis ediciones: **133 passed** → sin fallos nuevos) |

Suite completa: **no corrida** (la corre quien cierra, una sola vez).

## 4. Hash del commit

`181037097862568881345ed406f35d48ffe7636d`
`feat(005-003): T2 - ejemplos ejecutables, referencia operativa y arranque con la vista primero` (3 files changed, 160 insertions(+), 9 deletions(-)). Solo los tres archivos de producto; `docs/.cdad-state.json` fuera del commit.

## 5. Desviaciones declaradas

- Además de committear, agregué al asset el **ejemplo inválido** y a la referencia la **columna de efectos**: ambas son contenido exigido por el objetivo/spec §2.3 que el árbol no traía. No alteran ningún contrato observable ni rompen tests (verificado).
- Ninguna otra. No corrí la suite completa, no desplegué, no hice push, no toqué HOME ni `tests/**`; verifiqué que los archivos committeados no contienen rutas de host, proveedor ni modelo concreto (scan de patrones: limpio).