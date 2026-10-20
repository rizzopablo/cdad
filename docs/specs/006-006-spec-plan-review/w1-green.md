# Informe de rol — implementer, substage GREEN (006-006 W-1 / E4)

## Archivos modificados

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/scripts/cdad_packet.py` | **+80 / −6** — ruta de borrador en `prepare --replace-packet` |

**Nada más tocado.** `tests/` intacto (verificado: `git diff HEAD~1 HEAD --name-only` → un solo fichero, la implementación). `docs/.cdad-state.json` (mark `dispatched` de mi paquete), `docs/planning/` y `findings/` quedan como estaban: ajenos, sin trackear, fuera del commit.

## Qué cambia (mínimo)

`skills/cdad-cycle/scripts/cdad_packet.py`, modo `prepare --replace-packet`:

1. **Helper nuevo `_draft_contract_of_the_day()`** (`:2288`): construye el contrato del día a partir del `REQUEST` del paquete a reemplazar, conservando la **FORMA** (`kind`, `path`, `plan_version`, `object_kind`, `spec_path`/`spec_version`) y **recalculando sólo los digests** desde los bytes actuales del archivo (principal y acompañante).
2. **La revalidación del sucesor** (`:2415`): si el paquete a reemplazar declara un contrato `draft-plan` (el par `reviewer`/`plan-review`), el sucesor se valida **con la ruta de borrador vigente**; si no, sigue la ruta vigente `_contract_for(role, execution)` — **idéntica byte a byte** a la de hoy (contrato aprobado: `{kind, path, sha256, commit}`).
3. **Los checks del plan** que un `prepare` nuevo aplicaría se aplican al sucesor **sólo** si la forma declarada es `plan` (INV-5: una spec nunca se juzga por las reglas del plan).
4. **Obsolescencia (PD-8)**: se añade la deriva del **acompañante** (`spec_path`), que es parte del objeto revisado (R-8). Sin esto, una corrección que tocara sólo la spec acompañante dejaría al usuario sin salida — el mismo defecto W-1 en su caso estrecho. **No toca la ruta de contrato aprobado** (allí no hay acompañante).

**No tocado:** el guard PD-2 de `prepare` (prepare nuevo → rechazo igual); los rechazos vigentes del reemplazo (despachado / sin razón); la ruta de reemplazo sobre contrato aprobado; `validate_request`; el render.

## Test → resultado

| Test (fichero) | Resultado |
|---|---|
| `tests/test_006_006_w1_replace_draft_packet.py` (focal W-1) | 🟢 **5 passed** (antes: 3 failed, 2 passed) |
| regresiones del informe RED (`005_001_t2`, `tcorr`, `t3_idle`, `t4_decisive`, `005_005_t1`, `005_005_t4`, `006_006_u1`, `004_003_t2`) | 🟢 **60 passed** |
| focales `006_006_u1…u5` + `w1` (6 ficheros) | 🟢 **72 passed** |
| regresiones declaradas del paquete (15 ficheros: 004-003 T1–T4, 005-007 ×3, 003-002 ×3, 006-005 u2, packet_prepare, role_packet_render) | 🟢 **124 passed** |
| `tests/test_005_011_t3_view_action.py` (superficie del reemplazo) | 🟢 **5 passed** |
| `make validate` | 🟡 **168 PASS / 1 FAIL** — F011 **ambiental**, declarado (ver abajo) |

## Comandos y salida

```
$ python3 -m pytest tests/test_006_006_w1_replace_draft_packet.py -v
5 passed in 3.92s          (tras el cambio; antes: 3 failed, 2 passed — rc 2 != 0,
                            "plan-review subphase requires a draft-plan contract … (PD-2)")

$ python3 -m pytest tests/test_005_001_t2_replace_packet.py tests/test_005_001_tcorr.py \
    tests/test_005_001_t3_idle.py tests/test_005_001_t4_decisive.py \
    tests/test_005_005_t1_replace_conserved.py tests/test_005_005_t4_integration.py \
    tests/test_006_006_u1_draft_object_form.py tests/test_004_003_t2_plan_review.py
60 passed in 74.65s

$ python3 -m pytest <6 focales 006-006> <15 regresiones declaradas> tests/test_005_011_t3_view_action.py
196 passed in 237.66s

$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
```

**F011 ambiental — declarado, no lo causa este commit.** Es la deriva entre el repo y la copia del producto instalada en el `HOME` (`~/.claude/skills/cdad-cycle/scripts/cdad_packet.py` está en un HEAD previo; `install.sh --check` ⇒ DRIFT + "missing staged agents/…"). Reproducido **idéntico sobre el HEAD prístino** (sin mi cambio), vía `git archive HEAD`:

```
$ git archive HEAD | tar -x -C /tmp/opencode/head-baseline && cd /tmp/opencode/head-baseline && make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
```

Mismo número y mismo assert que el medido por el test-writer en `w1-red.md` antes de mi sesión. **No leí ni escribí la instalación de HOME**; la evidencia viene del comando declarado `make validate` y de la copia de HEAD.

## Commit

```
de629b832240d518fe892f77a6de2c6b9d77ca63
fix: 006-006 W-1 — reemplazo de un paquete de revision de borrador
 skills/cdad-cycle/scripts/cdad_packet.py | 86 +++++++++++++++++++++++++++++---
 1 file changed, 80 insertions(+), 6 deletions(-)
```

Sin `--no-verify`, sin `git stash`, sin `push`.

## Notas para el orquestador

- **Sin contradicción entre oráculos**: el control del RED (reemplazo sobre contrato aprobado y guard PD-2 de `prepare`) sigue verde por su efecto, no por su texto (A-1 respetado: no congelé el texto del diagnóstico).
- **Declaro una decisión dentro de la ruta de borrador** (la ruta aprobada queda intacta): la obsolescencia también la produce la deriva del documento acompañante. Sin ella, la re-review focal seguía inalcanzable cuando la corrección tocaba sólo la spec acompañante — el mismo hueco de W-1. Si el owner prefiere la lectura mínima literal, es una eliminación de 8 líneas (`companion_drifted`).
- **Suite completa**: no la corrí — la política del paquete la reserva a quien cierra (esta tarea).
- La **ruta de borrador** deja el `stage_history`/`epic_history` intactos (INV-2): el sucesor no autoriza nada, el `kind` sigue siendo `draft-plan`.