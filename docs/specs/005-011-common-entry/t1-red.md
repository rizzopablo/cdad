# Informe RED — 005-011-common-entry T1 (etapa 3, subetapa `red`)

**Paquete:** `005-011-common-entry-test-writer-red-001` · **Rol:** test-writer · **Tarea:** T1
**Contrato:** `docs/specs/005-011-common-entry/spec.md` (sha256 `37cd4593…`), con las enmiendas del
orquestador Claude; plan `docs/specs/005-011-common-entry/plan.md` (sha256 `edcee015…`), fila 11 del
plan del epic-005 (autoridad que supersede el comportamiento C4 de 005-003).
**Producto RED:** `project-root-resolution` (`project-root-v1`) — raíz relativa consistente en
`cdad_packet.py`.

**Aislamiento de fase (declarado).** No se leyó código de implementación
(`skills/cdad-cycle/scripts/`, `skills/cdad-cycle/references/`): el oráculo es el CLI invocado como
**subproceso** (caja negra) sobre proyectos fixture en tempdirs, leyendo su salida y su `rc`. Alcance
leído: la spec/plan del contrato y `tests/`. Alcance escrito: solo `tests/` (3 archivos).

## 1. Tabla test → postcondición/criterio

| Test | Archivo | Postcondición / criterio | Estado RED |
|---|---|---|---|
| `test_pd2_status_accepts_relative_root_with_projection` | `tests/test_005_011_t1_relative_root.py` | PD-2 / AC-2: `status --project-root .` (cwd = fixture) → rc=0 CON proyección | **RED** (AssertionError) |
| `test_pd2_relative_root_consistent_across_subcommands` | `tests/test_005_011_t1_relative_root.py` | PD-2 / AC-2: `validate-state` y `validate-policy` con `.` resuelven contra el cwd (rc=0) | **RED** (AssertionError) |
| `test_pd2_nonexistent_root_fails_closed_naming_cause` | `tests/test_005_011_t1_relative_root.py` | PD-2 borde: raíz inexistente → fallo cerrado, nombra `existing directory`, sin proyección parcial | verde (control de no-regresión) |
| `test_pd2_status_without_flag_still_uses_cwd` | `tests/test_005_011_t1_relative_root.py` | PD-2 borde: sin bandera se sigue usando el cwd (`:4297-4298`) | verde (control de no-regresión) |
| `test_pd2_other_validations_unchanged_with_relative_root` | `tests/test_005_011_t1_relative_root.py` | PD-2 / AC-2 control: política, hashing del contrato y validación del paquete con raíz relativa ≡ raíz absoluta | **RED** (AssertionError) |
| `test_pd5_relative_root_accepted_projects_view` (reemplaza C4) | `tests/test_005_003_t1_compact_view.py` | PD-3 (i): el oráculo C4 se reemplaza por el comportamiento nuevo (raíz relativa aceptada → proyección, rc=0) | **RED** (AssertionError) |
| `test_pd5_reference_declares_real_rc_capture_and_repro` (fixture corregido) | `tests/test_005_003_t2_examples_execute.py` | PD-3 (ii): oráculo de captura del `rc` CONSERVADO; solo cambian la invocación que falla (raíz inexistente) y la aserción de recuperación (`existing directory`) | verde (oráculo conservado) |

Cada test apunta a una sola afirmación observable; los tres RED fallan por **AssertionError** sobre el
comportamiento observable (rc / proyección / consistencia), no por ImportError, sintaxis ni error de
entorno. Los dos controles de no-regresión quedan verdes.

## 2. Comandos exactos y su salida

Ejecutados desde `<repo>` (`python3` = 3.13.5). Rutas de este host y de los tempdirs anonimizadas.

### 2.1 Focal (RED)

```
$ python3 -m pytest tests/test_005_011_t1_relative_root.py -q
FF..F                                                                    [100%]
=================================== FAILURES ===================================
<repo>/tests/test_005_011_t1_relative_root.py:138: AssertionError: PD-2 violada: con raíz relativa la vista `status` debe aceptarla y emitir la proyección (rc=0); hoy rc=2; stderr='ERROR: --project-root must be an absolute existing directory: . — root-relative asymmetry between CLIs: cdad_continuity.py resolves a relative --project-root against the cwd (e.g. `resume --project-root .` returns rc=0), while cdad_packet.py rejects it; recovery: pass an absolute --project-root'
<repo>/tests/test_005_011_t1_relative_root.py:185: AssertionError: PD-2 violada: `validate-state --project-root .` debe resolver la raíz relativa contra el cwd (rc=0); hoy rc=2; stderr='ERROR: --project-root must be an absolute existing directory: .'
<repo>/tests/test_005_011_t1_relative_root.py:275: AssertionError: PD-2 violada: `validate-policy` con raíz relativa cambió su veredicto respecto de la raíz absoluta (rc 2 != 0); stderr='ERROR: --project-root must be an absolute existing directory: .'
=========================== short test summary info ===========================
FAILED tests/test_005_011_t1_relative_root.py::test_pd2_status_accepts_relative_root_with_projection
FAILED tests/test_005_011_t1_relative_root.py::test_pd2_relative_root_consistent_across_subcommands
FAILED tests/test_005_011_t1_relative_root.py::test_pd2_other_validations_unchanged_with_relative_root
3 failed, 2 passed in 2.11s
```

Motivo de cada RED: el CLI vigente rechaza la raíz relativa con
`ERROR: --project-root must be an absolute existing directory: .` (rc=2, sin proyección). Los tres
dependen del cambio (aceptación de la raíz relativa) y fallan en la aserción sobre el `rc`/la
proyección. Los 2 verdes son los controles (raíz inexistente falla cerrado; sin bandera usa el cwd).

### 2.2 Oráculo declarado (i) — C4 reemplazado

```
$ python3 -m pytest tests/test_005_003_t1_compact_view.py -q
.........F.                                                              [100%]
=================================== FAILURES ===================================
<repo>/tests/test_005_003_t1_compact_view.py:160: AssertionError: PD-1 violada: la vista `status` debe emitir la proyección (rc=0); hoy rc=2; stderr='ERROR: --project-root must be an absolute existing directory: . — root-relative asymmetry between CLIs: cdad_continuity.py resolves a relative --project-root against the cwd (e.g. `resume --project-root .` returns rc=0), while cdad_packet.py rejects it; recovery: pass an absolute --project-root'
=========================== short test summary info ===========================
FAILED tests/test_005_003_t1_compact_view.py::test_pd5_relative_root_accepted_projects_view
1 failed, 10 passed in 6.48s
```

El oráculo C4 reemplazado (`test_pd5_relative_root_accepted_projects_view`, docstring y nombre declaran
que supersede C4 por la fila 11 del plan) falla hoy por aserción: el comportamiento nuevo espera rc=0
con proyección y hoy el CLI rechaza la raíz relativa (rc=2). Los otros 10 oráculos del archivo quedan
verdes (ninguna otra validación tocada).

### 2.3 Oráculo declarado (ii) — fixture de PD-5 corregido

```
$ python3 -m pytest tests/test_005_003_t2_examples_execute.py -q
..........                                                               [100%]
10 passed in 1.78s
```

El oráculo de captura del `rc` se conserva (rc real ≠ 0 sin enmascarar, formato `ERROR: …`,
prohibiciones en `orientation.md`); solo cambió la invocación que falla (de `--project-root .` a una
raíz inexistente) y la aserción del camino de recuperación (`absolut` → `existing directory`). Queda
verde: es un control conservado, no un RED (no depende del cambio).

### 2.4 Regresiones declaradas restantes

```
$ python3 -m pytest tests/test_packet_prepare.py tests/test_005_003_f2_idle_history.py tests/test_005_005_t1_replace_conserved.py -q
............................                                             [100%]
28 passed in 24.00s
```

La suite completa **no** se corrió (política de suite completa: la corre quien cierra).

## 3. `git diff --stat` acotado y hash del commit

`git diff --stat` (antes del commit, solo `tests/`):

```
 tests/test_005_003_t1_compact_view.py     | 45 +++++++++++--------------------
 tests/test_005_003_t2_examples_execute.py | 18 ++++++++-----
 2 files changed, 28 insertions(+), 35 deletions(-)
```

`git show --stat` del commit (incluye el focal nuevo):

```
 tests/test_005_003_t1_compact_view.py     |  45 ++---
 tests/test_005_003_t2_examples_execute.py |  18 +-
 tests/test_005_011_t1_relative_root.py    | 288 ++++++++++++++++++++++++++++++
 3 files changed, 316 insertions(+), 35 deletions(-)
```

- **Commit:** `00dd36e807609c5874da45e5f037cf6b524f61ee`
- **Mensaje:** `test(005-011): T1 RED — raíz relativa consistente en cdad_packet.py (focal + los dos oráculos declarados de PD-3)`
- **Archivos:** `tests/test_005_011_t1_relative_root.py` (nuevo, focal), `tests/test_005_003_t1_compact_view.py` (oráculo C4 reemplazado), `tests/test_005_003_t2_examples_execute.py` (fixture de PD-5 corregido). Solo `tests/`; ninguna implementación tocada. El `docs/.cdad-state.json` modificado por el orquestador quedó **fuera** del commit.

## 4. Notas para el GREEN / la review

- El implementer debe unificar la resolución de `--project-root` (cwd + `is_dir()`) y retirar el
  rechazo especial de `status`/C4. Diagnóstico esperado para raíz inexistente: nombra
  `existing directory` (spec §2.2) — es lo que asertan el focal y el oráculo (ii).
- El oráculo (i) prueba el comportamiento nuevo sobre `status` con raíz relativa; el focal prueba
  además `validate-state`, `validate-policy`, `validate-request` y `validate-packet`.
- Ninguna otra validación debe cambiar: el focal compara el veredicto con raíz relativa contra el de
  raíz absoluta (mismo `rc` y misma salida) para política, estado, request y paquete.
