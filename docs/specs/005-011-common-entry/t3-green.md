# Informe GREEN — 005-011 T3 (`view-action-v1`)

**Rol:** implementer · **Subetapa:** green · **Paquete:** `005-011-common-entry-implementer-green-003`
**Feature:** `005-011-common-entry` · **Task:** T3 · **Contrato:** `docs/specs/005-011-common-entry/spec.md` (sha256 `37cd4593…10bc`)
**Commit:** `860a611b43881bf774e5fd80639f4678eb1f1ea4` — `feat: implement 005-011 T3 view action (diverging leg + verified resolution in version; prepared = dispatch the packet)`

## 1. Cambio (archivo:línea)

Superficie editada: `skills/cdad-cycle/scripts/cdad_packet.py` y `skills/cdad-cycle/references/orientation.md`. `tests/` intacto (oráculo congelado, no editado).

**(1) Bloque `version` — la pata que diverge, leída, y su resolución verificada (PD-4/AC-4).**
- `skills/cdad-cycle/scripts/cdad_packet.py:3800` — `VERSION_LEGS`: las cuatro patas que imprime el chequeo.
- `:3803` — `_version_legs()`: LEE las líneas `project:` / `agents:` / `CLI:` / `claude-code:` que imprime `cdad-version-check.py`; un placeholder entre paréntesis (`(none: …)`, `(no version.txt found)`, `(not detected: …)`) es ausencia (`None`), nunca una versión. Nada se infiere del veredicto ni del rc.
- `:3817` — `_divergent_legs()`: referencia = la pata `CLI` (la instalación que corre el chequeo); diverge toda pata presente cuya versión no es la del `CLI`.
- `:3832` — `_version_verdict()` (extensión ADITIVA; `verdict`/`verified`/`cause` conservados):
  - `:3864` — `divergent_legs`: nombra la(s) pata(s) divergente(s), sólo ante `DRIFT`.
  - `:3870` — `resolution`: se afirma SÓLO cuando la pata divergente es exactamente `["project"]`: «the next `prepare` republishes the project's derived agents from the project source (project-execution.md §143-146)» (la republicación de `prepare` está en `cdad_packet.py:2874`). Con otra pata NO se promete (sería inventar).
  - `:3873-3881` — causa de `DRIFT` (incoherencia) y causa de AUSENCIA (`UNKNOWN`/`NO-PROJECT-AGENTS`) con **forma distinta**; la ausencia NO lleva cláusula de resolución. Los cuatro veredictos, sus rc y `cdad-version-check.py` NO se tocan.

**(2) Ruta de un paquete `prepared` (PD-5/AC-5).**
- `skills/cdad-cycle/scripts/cdad_packet.py:3980` — `_next_route()`: con `active_packet.status == "prepared"` la ruta nombra la ACCIÓN NATURAL («dispatch the prepared packet: validate it, then `begin` and `--record-dispatch`») con `--replace-packet` como RAMA CONDICIONAL. `entry` NO cambia (sigue `continuity-reconcile`); la ruta de `dispatched` (`:3974`) se conserva tal cual.

**(3) Documentación por referencia, sin duplicar la regla.**
- `skills/cdad-cycle/references/orientation.md:32-36` (§1): con un `prepared` la ruta nombra el despacho y `--replace-packet` es la rama condicional.
- `skills/cdad-cycle/references/orientation.md:122-128` (§4): la vista nombra la pata que diverge (leída de las líneas del chequeo) y, sólo con `project`, su resolución verificada; la ausencia no lleva resolución.

## 2. Tabla test → resultado

| Test (focal `tests/test_005_011_t3_view_action.py`) | PD/AC | Antes (RED) | Después (GREEN) |
|---|---|---|---|
| `test_pd4_project_leg_drift_names_leg_and_resolution` | PD-4/AC-4 | FAIL (AssertionError: no nombra la pata ni la resolución) | PASS |
| `test_pd4_non_project_leg_drift_names_leg_without_prepare_promise` | PD-4/AC-4 borde | FAIL (AssertionError: no nombra la pata) | PASS |
| `test_pd4_absence_is_distinguished_from_incoherence_without_resolution` | PD-4/AC-4 | FAIL (AssertionError: forma idéntica ausencia/incoherencia) | PASS |
| `test_pd5_prepared_packet_route_names_dispatch_action` | PD-5/AC-5 | FAIL (AssertionError: ruta «reconcile the pending packet…») | PASS |
| `test_pd5_dispatched_packet_keeps_reconcile_route` | PD-5/AC-5 control | PASS (control) | PASS |

Focal: **5 passed** (4 RED → GREEN + el control de `dispatched` verde). Focal + regresiones declaradas: **35 passed**.

## 3. Comandos exactos y su salida

Comando 1 — focal en el estado RED registrado (antes del cambio):
```
$ python3 -m pytest tests/test_005_011_t3_view_action.py -q
4 failed, 1 passed in 3.30s
```
(4 fallos por `AssertionError` de contrato; el control `test_pd5_dispatched_packet_keeps_reconcile_route` verde; sin `ImportError`/`SyntaxError`/`JSONDecodeError`.)

Comando 2 — focal (GREEN):
```
$ python3 -m pytest tests/test_005_011_t3_view_action.py -q
.....                                                                    [100%]
5 passed in 4.34s
```

Comando 3 — focal + regresiones declaradas por el paquete:
```
$ python3 -m pytest tests/test_005_011_t3_view_action.py tests/test_005_003_t1_compact_view.py tests/test_005_003_t2_examples_execute.py tests/test_005_003_f2_idle_history.py tests/test_005_007_t3_open_unit.py -q
...................................                                      [100%]
35 passed in 19.19s
```

Comando 4 — regresión proporcional extra (la referencia tocada, `orientation.md`, es leída por este archivo):
```
$ python3 -m pytest tests/test_005_005_t2_docs_policy.py -q
......                                                                   [100%]
6 passed in 0.06s
```

`observable_checks`: ninguno declarado (ninguno afectado) → no aplica comando adicional.
Suite completa: NO corrida aquí (política declarada una vez en la parte común: la corre quien cierra).

## 4. `git diff --stat` acotado (commit)

```
$ git show --stat --format="" HEAD
 skills/cdad-cycle/references/orientation.md | 15 +++++-
 skills/cdad-cycle/scripts/cdad_packet.py    | 74 ++++++++++++++++++++++++++---
 2 files changed, 81 insertions(+), 8 deletions(-)
```

Alcance: sólo `skills/**` (implementation root declarado por el paquete). `tests/**` intacto (`git status --short -- tests/` vacío). `docs/.cdad-state.json` ya estaba modificado en el árbol ANTES de esta tarea y NO se incluye en el commit (fuera del write_scope).

## 5. Commit

```
860a611b43881bf774e5fd80639f4678eb1f1ea4
feat: implement 005-011 T3 view action (diverging leg + verified resolution in version; prepared = dispatch the packet)
```
(sin `--no-verify`, sin `git stash`; `git add` explícito de los dos archivos.)

## 6. Invariantes

- **No editar tests:** respetado; el focal congelado pasó sin tocarlo.
- **Extensión aditiva (PD-6):** `verdict`/`verified`/`cause` conservados; `divergent_legs`/`resolution` son campos nuevos.
- **No se toca el chequeo:** `cdad-version-check.py` sin cambios; los cuatro veredictos y sus rc intactos.
- **`entry` no cambia:** sigue `continuity-reconcile` con `prepared`/`dispatched` (verificado por el focal).
- **Sin valores de este VPS, sin rutas absolutas del dueño, sin ids crudos de sesión.**
