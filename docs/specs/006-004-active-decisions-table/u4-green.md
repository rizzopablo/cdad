Everything is green except the one pre-existing environmental assert. Here is my report.

---

# CDAD — implementer GREEN, U4 (006-004-active-decisions-table)

**Packet**: `006-004-active-decisions-table-implementer-green-004` · **Ejecución**: `exec-006-004-active-decisions-table-001`
**Contrato**: `docs/specs/006-004-active-decisions-table/spec.md` (sha256 `ee88d426…43e3`) · **Plan**: `docs/specs/006-004-active-decisions-table/plan.md` §3 ficha U4
**RED de partida**: `docs/specs/006-004-active-decisions-table/u4-red.md` (commit `26b05ed`) — 6 fallos de contrato, 3 controles verdes.

## Archivos modificados (3, todos del write scope `skills/`)

| Archivo | Cambio | Líneas |
|---|---|---|
| `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md` | sección `## Current decisions` como **primer H2** (tras la introducción): forma de la fila (file · state · summary · roles · reference) + la nota (exclusiones y *el estado lo declara quien mantiene la tabla*) | +27 |
| `skills/cdad-cycle/references/stage-5-merge.md` | **§5.4**: el *upkeep* (al aprobarse un ADR el orquestador **agrega la fila**; al reemplazarse, **marca la anterior como obsoleta** conservándola con su reemplazo) — **el exit gate no cambia** | +9 |
| `skills/cdad-cycle/references/re-entry.md` | **paso 3 (MATERIALIZE)**: la **regla general del CAS** (digest base, nunca el actual; re-despacho con paquete nuevo sobre la base nueva; sin fusión a mano ni actualizar el digest esperado) + **§Scribe**: el caso de la tabla (dos escritores; el orquestador escribe sus filas directo en `docs/` con su commit; el del scribe llega por materialización) | +18 |

**Nada fuera del alcance**: no se tocó `tests/`, ni `docs/`, ni `sources/`, ni el generador. `docs/.cdad-state.json` (del orquestador), `docs/planning/` y `findings/` quedan sin tocar y **sin commitear**.

## Tabla test → resultado

| Test / gate | Resultado |
|---|---|
| `tests/test_006_004_u4_decisions_table.py` (focal, 9 tests) | **9 passed** (antes: 6 failed, 3 passed) |
| ↳ #1 plantilla: sección como primer H2 | ✅ |
| ↳ #2 plantilla: forma de la fila + nota | ✅ |
| ↳ #3 **control negativo**: el exit gate no ganó casillas (7) | ✅ (verde antes y después) |
| ↳ #4 `stage-5-merge.md` §5.4 nombra el upkeep | ✅ |
| ↳ #5 `re-entry.md` paso 3: regla general del CAS (6 conceptos) | ✅ |
| ↳ #6 `re-entry.md` §Scribe: caso de la tabla (5 conceptos) | ✅ |
| ↳ #7 el bloque de texto de la unidad pasa | ✅ |
| ↳ #8 **control negativo** (B-1): el bloque no exige la tabla viva ni el ADR-034 | ✅ |
| ↳ #9 **control negativo** (B-1): el bloque da el mismo resultado con y sin la semilla | ✅ |
| regresiones de la ficha U4 (`005_006_t2_intake`, `005_006_t5_acceptance`, `004_002_t1_policy`, `003_002_t2_reviewfix`, `006_005_u7_scribe_role_report`, `role_packets`) | **54 passed** |
| focales 006-004 U1/U2/U3 + ampliada de contrato compartido (`static_block_ceiling`, `006_002_u5_transport_equivalence`, `005_007_t7_unit_size_and_retries`, `003_006_t3_receive_wiring`, `005_005_t2_docs_policy`) | **62 passed** |
| `make validate` | **Assert PASS: 175 / Assert FAIL: 1** → el único FAIL es **F011 ambiental** (ver abajo) |
| `make staging` vs `agents/` | **diff vacío** en los 20 agentes (U4 no toca `sources/` ni el generador ⇒ no hay diff pendiente; no hizo falta `make agents`) |
| bloque estático (medición, no pedida por la ficha U4) | máx **3395 bytes** (`reviewer/plan-review`), techo 12000 — **sin cambio**: el bloque se compone de `packets/`, que U4 no toca |

### F011 — declarado, no oculto

`FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL`. Es **preexistente y ambiental**: deriva entre el árbol instalado en HOME y el repositorio. Ya fallaba antes de esta unidad (el RED midió `Assert PASS: 168 / Assert FAIL: 1` en el árbol previo al RED, con el mismo assert) y la deriva lista archivos de U1/U3 que esta unidad no tocó (`assets/packet-request.schema.json`, `agents/cdad-{architect,reviewer}*`). **No lo corrijo**: el encargo prohíbe leer o escribir la instalación de HOME. Se corrige re-instalando (`install.sh`), no desde esta unidad.

## Comandos y salida

```
$ python3 -m pytest tests/test_006_004_u4_decisions_table.py -q
9 passed in 3.03s

$ python3 -m pytest tests/test_005_006_t2_intake.py tests/test_005_006_t5_acceptance.py \
    tests/test_004_002_t1_policy.py tests/test_003_002_t2_reviewfix.py \
    tests/test_006_005_u7_scribe_role_report.py tests/test_role_packets.py -q
54 passed in 66.63s (0:01:06)

$ python3 -m pytest tests/test_006_004_u1_decisions_field.py tests/test_006_004_u2_decisions_section.py \
    tests/test_006_004_u3_principle_single_source.py tests/test_static_block_ceiling.py \
    tests/test_006_002_u5_transport_equivalence.py tests/test_005_007_t7_unit_size_and_retries.py \
    tests/test_003_006_t3_receive_wiring.py tests/test_005_005_t2_docs_policy.py -q
62 passed in 25.27s

$ make validate
PASS: 006-004 U4 PD-7-SECTION: the Memory Bank template carries the decisions section as its first H2
PASS: 006-004 U4 PD-7-SHAPE: the section of the template declares the row shape
PASS: 006-004 U4 PD-7-NOTE: the section of the template declares the note (the exclusions, and who declares the state)
PASS: 006-004 U4 PD-8-UPKEEP: section 5.4 names the upkeep of the table (add the row when an ADR is approved; mark the previous one obsolete)
PASS: 006-004 U4 PD-9-CAS: step 3 (MATERIALIZE) declares the general CAS rule (the base digest, never the current one, re-dispatch on the new base, no manual merge, no retouched digest)
PASS: 006-004 U4 PD-9-SCRIBE: the Scribe section declares the case of the table (two writers; the orchestrator writes its rows directly in docs/; the scribe's arrive by materialization)
PASS: 006-004 U4 PD-7-GATE: the exit gate of stage 5 keeps its 7 checkboxes and gained none about the decisions table
Assert PASS: 175
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
```

## Commit

```
38bf8d3 feat: 006-004 U4 — tabla y upkeep en plantilla y procedimiento
 skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md | 27 ++++++++++++++++++++++++++
 skills/cdad-cycle/references/re-entry.md                     | 18 +++++++++++++++
 skills/cdad-cycle/references/stage-5-merge.md                |  9 ++++++++
 3 files changed, 54 insertions(+)
```

Sin `--no-verify`, sin `git stash`, sin `push`. `git diff --stat 26b05ed..HEAD -- tests/` → **vacío** (los tests aprobados intactos).

## Límites y desviaciones declaradas

1. **Suite completa: no ejecutada** — la corre una vez quien cierra (política declarada en el paquete). Corrí el focal, las regresiones de la ficha, la ampliada de contrato compartido y `make validate`.
2. **F011 no se corrige** (ambiental, HOME intocable por encargo) —唯一的 `make validate` rojo, y **preexistente**.
3. **Nada de U5/U7**: no toqué `docs/systemPatterns.md` ni `docs/adr/` (son el producto de U5, materializado por el orquestador) — el bloque de texto de U4 no los exige (B-1), verificado por los controles #8 y #9.
4. **A-1**: ninguna oráculo vigente reemplazado; el exit gate de stage 5 conserva sus 7 casillas; la subfase del reviewer no se toca; los agentes no se regeneraron (no hubo cambio en `sources/`).
5. **Bloque estático**: la ficha de U4 no pide la medición (es de U3); la registré igual y no cambia (U4 no toca `packets/`).