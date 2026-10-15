# Informe RED — 005-011-common-entry · T3 (view-action)

- **Rol:** test-writer · **subetapa:** red · **feature:** `005-011-common-entry` · **tarea:** T3
- **Contrato:** `docs/specs/005-011-common-entry/spec.md` (sha256 `37cd4593…`), PD-4/PD-5 y AC-4/AC-5; plan `docs/specs/005-011-common-entry/plan.md` (sha256 `edcee015…`), ficha T3.
- **Archivo focal (nuevo):** `tests/test_005_011_t3_view_action.py`
- **Commit:** `1c207d9` — `test(005-011): T3 RED — pata que diverge y resolución en la vista + ruta de prepared (PD-4/PD-5)` (prefijo `test:`, sólo `tests/`)
- **Oráculo:** el CLI `status` como **subproceso** sobre proyectos fixture en tempdirs (HOME aislado); nunca se importa el módulo ni se lee la implementación.

## Tabla test → postcondición/criterio

| Test | PD / AC | Afirmación observable | Estado hoy |
|---|---|---|---|
| `test_pd4_project_leg_drift_names_leg_and_resolution` | PD-4 / AC-4 | Con la pata `project` divergiendo (derivados del proyecto con la versión anterior a la instalación; `agents`/`CLI` coincidentes): la vista **nombra la pata** y **dice qué lo resuelve** (el próximo `prepare` republica los derivados) | **RED** (AssertionError: no nombra la pata) |
| `test_pd4_non_project_leg_drift_names_leg_without_prepare_promise` | PD-4 / AC-4 (borde) | Con una pata que **no** es `project` (`agents` ≠ `CLI`; `project` = `CLI`): la vista **nombra la pata** y **no** promete la resolución del `prepare` | **RED** (AssertionError: no nombra la pata); control «no promete» verde |
| `test_pd4_absence_is_distinguished_from_incoherence_without_resolution` | PD-4 / AC-4 | `UNKNOWN` (marca faltante) y `NO-PROJECT-AGENTS` son **ausencia**: sin cláusula de resolución y **distinguidas** de `DRIFT` (hoy la causa es idéntica en forma: sólo difieren el veredicto y su `rc`) | **RED** (AssertionError: formas idénticas); controles «ausencia sin resolución» verdes |
| `test_pd5_prepared_packet_route_names_dispatch_action` | PD-5 / AC-5 | Con `active_packet.status == "prepared"`: `next.route` **nombra la acción natural** (despacharlo) con `--replace-packet` como rama condicional, y `entry` sigue `continuity-reconcile` | **RED** (AssertionError: la ruta es el texto anterior, sin despacho) |
| `test_pd5_dispatched_packet_keeps_reconcile_route` | PD-5 / AC-5 (control de no-regresión) | Con `dispatched`: se **conserva** la ruta de reconciliación antes de repetir, `entry` sigue `continuity-reconcile`, y la ruta difiere de la de `prepared` | **verde** (control) |

Cada test apunta a una sola afirmación observable; los `assert` de fixture (p. ej. `verdict == "DRIFT"`) son controles que acreditan que el escenario es el declarado, no la aserción del contrato.

## Comandos exactos y salida

### 1) Focal (RED)

```
$ python3 -m pytest tests/test_005_011_t3_view_action.py -q
FFFF.                                                                    [100%]
...
=========================== short test summary info ============================
FAILED tests/test_005_011_t3_view_action.py::test_pd4_project_leg_drift_names_leg_and_resolution
FAILED tests/test_005_011_t3_view_action.py::test_pd4_non_project_leg_drift_names_leg_without_prepare_promise
FAILED tests/test_005_011_t3_view_action.py::test_pd4_absence_is_distinguished_from_incoherence_without_resolution
FAILED tests/test_005_011_t3_view_action.py::test_pd5_prepared_packet_route_names_dispatch_action
4 failed, 1 passed in 3.19s
```

Motivo de fallo de cada RED (todos **AssertionError** de contrato; ninguno es ImportError, SyntaxError, JSONDecodeError ni error de setup):

- `test_pd4_project_leg_drift_names_leg_and_resolution` →
  `AssertionError: PD-4 violada: con un DRIFT de la pata project la vista no nombra la pata que diverge … version={'cause': 'version not verified as coherent (verdict DRIFT, rc 1); any non-zero rc reads as not verified', 'verdict': 'DRIFT', 'verified': False}`
- `test_pd4_non_project_leg_drift_names_leg_without_prepare_promise` →
  `AssertionError: PD-4 violada: con un DRIFT de la pata agents la vista no nombra la pata que diverge: version={'cause': '…(verdict DRIFT, rc 1)…', 'verdict': 'DRIFT', 'verified': False}`
- `test_pd4_absence_is_distinguished_from_incoherence_without_resolution` →
  `AssertionError: PD-4 violada: la vista no distingue la AUSENCIA (UNKNOWN) de la INCOHERENCIA: ambas causas son idénticas en forma (sólo cambian el veredicto y su rc) — ausencia={…'verdict': 'UNKNOWN', rc 3…} drift={…'verdict': 'DRIFT', rc 1…}`
- `test_pd5_prepared_packet_route_names_dispatch_action` →
  `AssertionError: PD-5 violada: la ruta de un paquete prepared no nombra la acción natural (despacharlo: validar → begin → --record-dispatch): 'reconcile the pending packet (--replace-packet if the contract changed)'`

### 2) Regresiones declaradas por el paquete

```
$ python3 -m pytest tests/test_005_003_t1_compact_view.py tests/test_005_003_t2_examples_execute.py tests/test_005_003_f2_idle_history.py tests/test_005_007_t3_open_unit.py -q
..............................                                           [100%]
30 passed in 16.00s
```

### 3) Diff acotado y commit

```
$ git show --stat --oneline HEAD
1c207d9 test(005-011): T3 RED — pata que diverge y resolución en la vista + ruta de prepared (PD-4/PD-5)
 tests/test_005_011_t3_view_action.py | 529 +++++++++++++++++++++++++++++++++++
 1 file changed, 529 insertions(+)
```

`git status --porcelain` al cerrar: sólo `?? tests/test_005_011_t3_view_action.py` (commiteado) y `M docs/.cdad-state.json` (**cambio previo del árbol, ajeno a este encargo: no se tocó ni se commiteó**). No se corrió la suite completa (política declarada: la corre quien cierra).

## Método del fixture (declarado)

- **Proyectos sintéticos** en tempdirs (`build_project`), `HOME` = tempdir vacío, sin datos de demo ni base real de sesiones; el repo nunca se escribe.
- **Instalación simulada:** para los casos de `DRIFT` el fixture copia el árbol `skills/` a un tempdir, escribe su marcador `version.txt` y sus agentes derivados, e invoca el CLI **copiado** de esa instalación. Es necesario porque el chequeo de versión lee el marcador de la instalación **del árbol donde vive el CLI** y el checkout del repo no tiene marcador (daría `UNKNOWN` siempre).
  - pata `project` divergiendo → manifiesto derivado con `source_version` anterior + instalación/`agents`/`CLI` coincidentes;
  - pata `agents` divergiendo → `source_dir` apuntando a **otra** instalación (`agents` ≠ `CLI`, `project` = `CLI`);
  - `UNKNOWN` → instalación **sin** marcador (con guarda de setup: ningún ancestro del tempdir trae `version.txt` ajeno);
  - `NO-PROJECT-AGENTS` → instalación con marcador y **sin** manifiesto derivado.
- **Anclas estructurales** (INV-5): la pata se lee como token aislado en el bloque `version` (excluyendo la clave `verdict`, cuyos literales contienen nombres de pata: `NO-PROJECT-AGENTS`); la resolución es el token `prepare`; la acción natural es un token de despacho (`--record-dispatch` / `dispatch*`); la ruta de `dispatched` conserva `reconcil*` + (`repeat`|`resume`). **El sentido de la prosa lo juzga la review**, no una lista de palabras.

## Límites honestos

- La spec fija el **comportamiento** («nombra la pata», «dice qué lo resuelve») pero **no los nombres de campo** de la extensión aditiva del bloque `version`; por eso las aserciones son estructurales sobre el bloque (token de pata / token de resolución / diferencia de forma), no sobre una clave concreta. Un campo nuevo con cualquiera de las formas razonables satisface el oráculo.
- El test de ausencia es el único que exige un **diferencial de forma** entre ausencia e incoherencia (más allá del veredicto y su `rc`): es la parte que falla hoy por aserción; las ausencias «sin resolución» son controles (verdes antes y después).
- Dentro del focal hay **1 control verde** (`dispatched`): el paquete lo declara como control de no-regresión de PD-5.
- No se leyó código de implementación (`skills/cdad-cycle/scripts/cdad_packet.py` ni las referencias) ni se escribió fuera de `tests/`. La observación del comportamiento del CLI (incluido el chequeo de versión y el `--help` de los subcomandos) se hizo **como subproceso**, que es el oráculo declarado por el paquete.
