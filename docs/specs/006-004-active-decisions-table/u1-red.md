All work is complete and committed. Here is the role report.

---

# RED de U1 — 006-004-active-decisions-table (test-writer, subfase `red`)

## 1. Archivos modificados

| Archivo | Acción | Líneas |
|---|---|---|
| `tests/test_006_004_u1_decisions_field.py` | **nuevo** | 899 (8 tests) |

Nada fuera de `tests/`. `docs/.cdad-state.json` (modificado por el orquestador), `docs/planning/` y `findings/*.md` (sin trackear) quedaron intactos.

## 2. Mapa test → PD (ficha U1 del plan, §3)

| Test | Postcondición | Qué exige |
|---|---|---|
| `test_pd1_good_row_is_accepted_and_request_carries_the_declared_order` | **PD-1 + PD-6** | la forma buena se acepta; el `REQUEST.json` lleva `current_decisions` con las filas **en el orden declarado** |
| `test_pd1_malformed_rows_are_rejected_without_publication` (8 subcasos) | **PD-1** | clave desconocida · `state` fuera de vocabulario · `superseded_by` ausente con `obsoleto` · `superseded_by` presente con `vigente` · `file` inexistente · `roles` vacío · rol fuera del vocabulario · `summary` con salto de línea → rc≠0, **sin publicación**, state byte-idéntico, árbol sin cambios |
| `test_pd2_row_must_name_the_packet_role` (3 subcasos) | **PD-2** | la fila que no nombra al rol del paquete, la que nombra a otro rol delegado y la que nombra sólo al orquestador se rechazan **nombrando la fila y el rol** |
| `test_pd3_obsolete_row_is_not_admissible` | **PD-3** | la fila `obsoleto` no es admisible; el rechazo nombra la fila y su `superseded_by` |
| `test_pd4_row_cap_fails_closed` | **PD-4** | 32 filas admitidas (y en el request); 33 → rc≠0 nombrando **33** y **32**, sin publicar |
| `test_v1_installed_product_renders_the_same_package_with_rows` | **V-1** | el producto instalado (`install.sh --basic` en un `CDAD_INSTALL_ROOT` temporal) produce el mismo rc, el mismo `REQUEST.json` (con filas) y el mismo `PACKET.md`, **byte a byte** que el CLI del repo |
| `test_v3_receive_revalidates_the_request_with_the_widened_set` | **V-3** | `receive` **recibe** un paquete cuyo request lleva `current_decisions` y **rechaza** uno con una fila malformada (rc≠0, sin recibo publicado) |
| `test_a1_unknown_request_key_is_still_rejected` | **A-1** | control negativo explícito: una clave cualquiera distinta de `current_decisions` **sigue rechazándose** |

**A-1 (declarada, plan §4): esta feature NO reemplaza ningún oráculo vigente.** El conjunto cerrado del request se **extiende** con una propiedad declarada (`current_decisions`) y la clausura **no** se relaja — el RED lo vuelve a comprobar (test A-1) y **sólo añade casos**; no modificó ni invisibilizó ninguna prueba vigente, y no tocó ningún archivo de `tests/` ajeno a este.

**Interfaz declarada por el RED** (dentro de la libertad que deja el contrato): bandera repetible `--current-decision <JSON>`; las filas en `request["current_decisions"]` en orden; la fila se nombra en el diagnóstico por su `file` (el RED comprueba el nombre del archivo); el rol del paquete por su nombre. **Límite declarado**: el RED exige rc≠0 + no publicación en todo negativo, y exige el *nombre del dato culpable* sólo donde el contrato lo pide explícitamente (PD-1, PD-2, PD-3, PD-4); en los negativos restantes (`superseded_by` ausente/presente, `roles` vacío, `summary` con salto de línea) no exige redacción concreta.

## 3. Comandos y salida

### 3.1 Focal — RED declarado (7 fallan por asercion, 1 control verde)

```
$ python3 -m pytest tests/test_006_004_u1_decisions_field.py -q
FAILED ...::TestPd1RowShape::test_pd1_good_row_is_accepted_and_request_carries_the_declared_order
FAILED ...::TestPd1RowShape::test_pd1_malformed_rows_are_rejected_without_publication
FAILED ...::TestPd2RowNamesThePacketRole::test_pd2_row_must_name_the_packet_role
FAILED ...::TestPd3OnlyCurrentRowsTravel::test_pd3_obsolete_row_is_not_admissible
FAILED ...::TestPd4RowCap::test_pd4_row_cap_fails_closed
FAILED ...::TestV1InstalledProduct::test_v1_installed_product_renders_the_same_package_with_rows
FAILED ...::TestV3ReceiveRevalidatesTheRequest::test_v3_receive_revalidates_the_request_with_the_widened_set
7 failed, 1 passed in 17.61s
```

Razones de fallo (todas `AssertionError` de contrato; **ningún** ImportError/sintaxis/traceback):

| Test | Razón medida del fallo |
|---|---|
| PD-1/PD-6 | `2 != 0 : prepare falló: ERROR: cdad_packet.py: unrecognized arguments: --current-decision {...}` |
| PD-1 (8 negativos) | `'unrecognized' unexpectedly found in 'ERROR: … unrecognized arguments: --current-decision {…}'` |
| PD-2 | ídem (el diagnóstico no nombra la fila ni el rol) |
| PD-3 | ídem (el diagnóstico no nombra la fila ni su `superseded_by`) |
| PD-4 | `2 != 0 : prepare falló: … unrecognized arguments: --current-decision {…}` (32 filas) |
| V-1 | `2 != 0 : control del repo: ERROR: cdad_packet.py: unrecognized arguments: --current-decision {…}` |
| V-3 | `2 != 0 : V-3: receive debe aceptar el paquete con filas: ERROR: request fields do not match schema` |

El único verde es el control A-1 (debe seguir verde).

### 3.2 Regresiones de la ficha U1 — 100/100 verdes

```
$ python3 -m pytest tests/test_packet_prepare.py tests/test_role_packet_render.py \
    tests/test_role_packets.py tests/test_003_002_t1_receive.py tests/test_003_002_t2_materialize.py \
    tests/test_004_003_t1_draft_contract.py tests/test_004_003_t1_reviewfix.py \
    tests/test_004_003_t2_plan_review.py tests/test_004_003_t4_validation_fields.py \
    tests/test_005_012_t1_register_transition_base.py tests/test_static_block_ceiling.py -q
100 passed in 179.62s (0:02:59)
```

### 3.3 `make validate` — 1 fallo **preexistente**, idéntico sin mi archivo

```
$ make validate
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
Assert PASS: 168
Assert FAIL: 1
```

Verificado por conmutación (mi archivo movido fuera de `tests/`): **el mismo** `Assert PASS: 168 / Assert FAIL: 1` con y sin mi archivo. La causa es deriva del entorno, no del RED: `install.sh --check` compara el árbol instalado del HOME (`<home>/.config/opencode/skills/cdad-cycle`, `<home>/.claude/skills/cdad-cycle`, mtimes 2026-10-18/19) contra el staging del repo (2026-10-20 13:52) y detecta `DRIFT` de `.pyc` y agentes faltantes. Mi test no escribe en el HOME (instala con `CDAD_INSTALL_ROOT` temporal y `CDAD_SKILL_EXTRA_DIRS=""`); **no lo corrijo** porque está fuera de `tests/`.

### 3.4 Sondeos de caja negra (para que el RED falle por la razón correcta)

Medidos invocando los CLI, **sin leer la implementación**:

- `prepare --current-decision '<json>'` → `rc=2`, `ERROR: cdad_packet.py: unrecognized arguments: --current-decision {…}`.
- `validate-request` con `current_decisions` → `rc=2`, `ERROR: request fields do not match schema`; con el request publicado → `rc=0`.
- `render` con `current_decisions` → `rc=2` (mismo error).
- `receive` con un request que lleva `current_decisions` → `rc=2`, `ERROR: request fields do not match schema`; con el `objective` cambiado → `rc=2`, `ERROR: packet differs from its canonical rendering (validate-packet)` ⇒ **`receive` re-renderiza y compara** (de ahí que el test V-3 use el render canónico del request con filas, con repliegue al paquete publicado).
- `receive` es **idempotente**: la segunda recepción del mismo proyecto encuentra el recibo durable y no revalida ⇒ el test V-3 usa **un proyecto descartable nuevo por caso** (si no, el caso «malformada» habría pasado en verde falso).

**Trampa de verde falso detectada y cerrada:** el error de argparse vuelca el JSON de la fila, de modo que las aserciones «el diagnóstico nombra el culpable» se satisfacían con el error de bandera desconocida (PD-3 pasaba en verde hoy). Añadí la guarda `assertNotIn("unrecognized", stderr)` en el control de rechazo: sin ella, PD-3 y PD-4 no serían RED reales.

## 4. Commit

```
$ git add tests/test_006_004_u1_decisions_field.py
$ git commit -m "test: 006-004 U1 RED — filas declaradas en el encargo"
[main d9ca66e] test: 006-004 U1 RED — filas declaradas en el encargo
 1 file changed, 899 insertions(+)
```

`git show --stat HEAD`: **sólo** `tests/test_006_004_u1_decisions_field.py`. Sin `--no-verify`, sin `stash`, sin `push`. Estado tras el commit: `M docs/.cdad-state.json` (del orquestador) y los sin-trackear de `docs/planning/` y `findings/` — no míos.

## 5. Límites honestos y desviaciones declaradas

- **Fase de aislamiento**: no leí ningún archivo de implementación (`skills/cdad-cycle/scripts/`, `scripts/`, `sources/`, `agents/`, `install.sh`); sólo invoqué los CLI. Lecturas: `docs/specs/006-004-active-decisions-table/*` (contrato) y `tests/**` (alcance declarado). **Desviación menor declarada**: leí el `Makefile` (23 líneas, objetivos de build, fuera del read scope estricto) para conocer los comandos del runner y `make validate`.
- **Suite completa**: no la corro (política declarada en el paquete: la corre una vez quien cierra).
- **Foco reproducible**: todo RED corre sobre el CLI real como proceso, en proyectos descartables con HOME aislado; sin valores del host ni rutas absolutas en el test (verificado por grep).
- **`make validate`**: el único rojo (F011) es preexistente y de entorno; lo reporto en vez de tocarlo (está fuera de `tests/`).
- **Puente con U2**: el RED de U1 no afirma nada sobre la sección `## Current decisions` del render (esa es U2/PD-5); el test V-3 usa el render canónico del request con filas con repliegue al paquete publicado, de modo que no queda atado a la ausencia ni a la presencia de la sección.