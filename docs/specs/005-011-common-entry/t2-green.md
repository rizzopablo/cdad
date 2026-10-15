# Informe GREEN — 005-011-common-entry · T2 (etapa 3)

**Rol:** implementer · **Subetapa:** GREEN · **Tarea:** T2 (solo documentación)
**Paquete:** `005-011-common-entry-implementer-green-002` (v1) · **Contrato:** `docs/specs/005-011-common-entry/spec.md`
(sha256 `37cd4593…c610bc`) · **Plan:** `docs/specs/005-011-common-entry/plan.md` (sha256 `edcee015…fbbf833`)
**Producto:** `common-entry` (`common-entry-v1`) · **PD cubierta:** PD-1

## 1. Cambio (archivo:línea)

Una sola palanca por causa; sin documento nuevo ni segunda copia. Solo dos `SKILL.md` editados.

- `skills/cdad-cycle/SKILL.md:251` — **Step 1**: la primera acción prescripta pasa a ser la vista compacta
  `<skill-dir>/scripts/cdad_packet.py status` (`references/orientation.md` §1; regla compuesta en
  `references/project-start.md` §11). `state-detection.md` deja de ser el primer paso y pasa a **ampliación
  condicional** (gatillo: un bloqueo o una duda que afecte al siguiente despacho, con motivo registrado). Se
  conserva, en la misma línea, la rama `resume` (solo con ejecución activa) con su negación explícita.
- `skills/cdad-cycle/SKILL.md:453` — tabla «How to read the references»: **nueva fila `orientation.md`**
  (hoy ausente), con puntero a los dueños de la regla (§1 + `project-start.md` §11).
- `skills/cdad-cycle/SKILL.md:454` — fila `state-detection.md` ajustada a su gatillo de ampliación.
- `skills/cdad-epic/SKILL.md:58` — **Step 1**: consulta **primero** la vista `status` (misma regla por
  referencia: `cdad-cycle` `references/orientation.md` §1 + `project-start.md` §11, como entrada común de
  ambos runtimes); `state-detection.md` pasa a ampliación condicional con motivo.
- `skills/cdad-epic/SKILL.md:204` — tabla de referencias: `state-detection.md` indexada con el gatillo de
  ampliación.

No se tocó el agente `cdad-orchestrator` ni el código del CLI ni `tests/**`. No se creó referencia nueva.

## 2. Tabla observable_check → resultado (bloque canónico plan-tasks T2)

| observable_check | resultado | evidencia |
|---|---|---|
| La primera acción prescripta del Step 1 de `cdad-cycle/SKILL.md` y `cdad-epic/SKILL.md` es la vista compacta `status` (referencia a `orientation.md` §1) | CUMPLE | `cdad-cycle/SKILL.md:251` («Consult **first** … `<skill-dir>/scripts/cdad_packet.py status` … `orientation.md` §1»); `cdad-epic/SKILL.md:58` («Consult **first** the read-only compact `status` view … `orientation.md` §1») |
| `state-detection.md` deja de ser el primer paso y pasa a ampliación condicional con gatillo declarado en la tabla (una necesidad concreta, con motivo registrado) | CUMPLE | `cdad-cycle/SKILL.md:454` y `cdad-epic/SKILL.md:204` |
| `orientation.md` aparece como fila en la tabla de referencias de `cdad-cycle` | CUMPLE | `cdad-cycle/SKILL.md:453` |
| La regla se referencia (`orientation.md` §1 + `project-start.md` §11) y no se reescribe | CUMPLE | Ambas referencias citadas en el Step 1 de las dos skills; la fila de tabla cita los dueños en lugar de copiar el procedimiento |
| No se crea documento nuevo | CUMPLE | `git show --name-only`: solo los dos `SKILL.md` |
| La rama `resume` y la fila `project-start.md` se conservan y las guardas por ventana de 005-006/005-010 quedan verdes | CUMPLE | `resume` intacto en `:251`; fila `project-start.md` intacta en `:455`; regresiones verdes (§3) |
| El sentido de los textos lo juzga la review, no una lista de palabras | N/A mecánicamente | Sin test que decida el significado de un párrafo (INV-5); se entrega el texto a la review por sentido |

## 3. Comandos y salida

Comandos exactos y resumen de `pytest` (todos los comandos corren desde el repo; sin `--no-verify`, sin `git stash`).

Regresiones declaradas por el paquete:

```
$ python3 -m pytest tests/test_005_006_t1_start_procedure.py tests/test_005_006_t6_owner_reviewfix.py tests/test_005_005_t2_docs_policy.py tests/test_005_003_t2_examples_execute.py -q
36 passed in 1.99s
```

Guardas de texto de los otros references/skills (instrucciones del dueño para esta etapa):

```
$ python3 -m pytest tests/test_005_010_t3_references.py tests/test_005_010_reviewfix.py tests/test_005_009_t3_spawn_reconciliation.py -q
35 passed in 10.67s
```

Regresión proporcional adicional (tests que leen `SKILL.md` y el cableado de skills):

```
$ python3 -m pytest tests/test_003_006_t1_wiring.py tests/test_005_006_t2_intake.py tests/test_005_006_t3_epic_features.py tests/test_005_004_t1_dispatch_tool_name.py tests/pd10_permission_semantics.py -q
26 passed in 1.45s

$ python3 -m pytest tests/test_install_review5_regressions.py tests/test_role_packet_consumers.py tests/test_role_packet_review_regressions.py tests/test_004_003_t5_reentry_equivalence.py tests/test_003_006_t3_receive_wiring.py -q
41 passed in 115.19s (0:01:55)

$ python3 -m pytest tests/test_003_006_t2_activation.py -q
18 passed in 3.35s
```

La suite completa **no** se corrió aquí: la política de suite completa (declarada una vez en la parte común) la
corre quien cierra. Este GREEN cierra con la regresión proporcional y las guardas verdes.

## 4. `git diff --stat` acotado (del commit)

```
 skills/cdad-cycle/SKILL.md | 5 +++--
 skills/cdad-epic/SKILL.md  | 4 ++--
 2 files changed, 5 insertions(+), 4 deletions(-)
```

## 5. Commit

```
13c68b98837ecf3a5d4f993bfcdc20556ace294c
feat(005-011): T2 GREEN — entrada común por status en cdad-cycle y cdad-epic (Step 1 + tabla de referencias)
```

Prefijo `feat:` según el contrato. Sin `--no-verify`; sin `git stash`. El cambio preexistente en
`docs/.cdad-state.json` (binding de despacho del orquestador) **no** se commiteó: es del orquestador y queda
fuera del alcance de escritura del implementer.

## 6. Sentido del Step 1 y conservación de las guardas

**Cómo quedó el Step 1 (por sentido).** La primera acción prescripta es ahora la vista compacta
(`<skill-dir>/scripts/cdad_packet.py status` en `cdad-cycle`; la misma vista por referencia en `cdad-epic`): de
ella se leen el stage, el feature activo y el subfase (en el epic, el `active_epic` y su `epic_stage`, que la
vista ya proyecta). `state-detection.md` —dueño canónico del reconocimiento feature/Memory-Bank— deja de
encabezar el paso y se convierte en **ampliación condicional**: se carga solo ante una necesidad concreta que
afecte al siguiente despacho, dejando el motivo registrado. La regla «vista primero, ampliar ante una necesidad
concreta» **no** se reescribe: se cita a sus dueños (`orientation.md` §1 y `project-start.md` §11), cumpliendo
INV-2/INV-3 (referencia, no copia; sin documento nuevo). Leído de corrido, el Step 1 dice: orientate con la
vista, y solo si algo concreto lo exige, ampliá con la detección de estado.

**Por qué conserva la guarda del `resume`.** La rama «solo con ejecución activa» es una guarda por ventana de
005-006 (PD-9): arrancar desde reposo no debe reanudar una ejecución inexistente. Por eso la cláusula
`resume` —con su negación explícita «**without an active execution, do not run `resume`**»— se mantiene
íntegra en la misma línea del Step 1: la nueva primera acción de orientación **no** reemplaza ni diluye la
regla de reanudación. El cambio agrega la vista **antes**, sin tocar la rama.

**Por qué conserva la fila `project-start.md`.** `project-start.md` es el dueño del arranque desde reposo y su
fila en la tabla «How to read the references» es otra guarda de 005-006 (PD-1): la tabla debe seguir listándolo.
La fila se dejó **intacta**; la única modificación de la tabla fue agregar `orientation.md` y ajustar la fila de
`state-detection.md` a su gatillo, sin alterar la fila `project-start.md` ni el resto de la tabla.

**Fuera de alcance respetado.** No se creó una referencia «common entry» nueva, no se duplicó la regla de la
vista, y no se tocó el agente `cdad-orchestrator` (no es el texto común entre runtimes).
