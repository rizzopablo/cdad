# Informe GREEN (con BLOQUEO PARCIAL declarado) — 005-011-common-entry T1 (etapa 3, subetapa `green`)

**Paquete:** `005-011-common-entry-implementer-green-001` · **Rol:** implementer · **Tarea:** T1
**Contrato:** `docs/specs/005-011-common-entry/spec.md` (sha256 `37cd4593…`), con las enmiendas del
orquestador Claude; plan `docs/specs/005-011-common-entry/plan.md` (sha256 `edcee015…`), fila 11 del
plan del epic-005 (autoridad que supersede el comportamiento C4 de 005-003).
**Producto:** `project-root-resolution` (`project-root-v1`).
**Commit:** `53413b39c037b08547d549bd3b4fea2e61fe9a76` (`feat(005-011): T1 GREEN — resolución unificada de --project-root en cdad_packet.py`).

**Resultado global: 4/5 focales verdes + los 2 oráculos declarados de PD-3 verdes + las 5 regresiones del
paquete verdes. El focal `test_pd2_relative_root_consistent_across_subcommands` es INSATISFACIBLE con el
oráculo congelado por un defecto de fixture (ver §5). Se detiene y se reporta conforme al contrato
(`implementer`: «si un test te parece incorrecto, detenete y reportalo») y a la cláusula de detención del
plan T1 («si la unificación exigiera cambiar una validación distinta de la resolución de la raíz,
detener»).**

---

## 1. Cambio (archivo:línea)

1. `skills/cdad-cycle/scripts/cdad_packet.py:673-677` — **`_absolute_existing_directory`**: el cuerpo pasa
   de «exigir absoluta + `is_dir()`» a «resolver contra el cwd + `is_dir()`», igual que
   `cdad_result.py:1508-1511`. Diagnóstico de fallo cerrado: `"{label} must be an existing directory: {raw}"`
   (nombra la causa `existing directory`, ya no `absolute`).
2. `skills/cdad-cycle/scripts/cdad_packet.py:3776-3791` — **retirado** el helper especial
   `_status_project_root` (C4: la vista diagnosticaba la asimetría de raíz relativa).
3. `skills/cdad-cycle/scripts/cdad_packet.py:4294-4300` — **retirada** la rama `elif args.command ==
   "status"` de `main`; **todos** los subcomandos resuelven la raíz por la misma vía
   (`Path.cwd().resolve()` sin bandera; `_absolute_existing_directory` con bandera).
4. `skills/cdad-cycle/references/orientation.md:68-75` — la sección «Root-relative asymmetry (diagnosed in
   the view)» se corrige a «Project root resolution»: la raíz relativa **se acepta** y la regla se
   **referencia** (`project-execution.md` §1); ya no se diagnostica ninguna asimetría.
5. `skills/cdad-cycle/references/project-execution.md:49` — la nota deja de afirmar «must be an absolute
   existing directory» y pasa a «resolved against the current working directory and must be an existing
   directory».

**No tocado (invariante PD-2):** la política (`_project_path`/`classify_path`), el hashing del contrato,
la publicación de agentes derivados, el default cwd sin bandera (`Path.cwd().resolve()`), y los CLIs
`cdad_continuity.py`, `cdad_result.py`, `cdad-version-check.py`, `cdad_guard.py` (cada uno sigue
resolviendo su propia raíz). `tests/**` intacto.

---

## 2. Tabla test → resultado

| Test | Archivo | Antes (RED) | Después (GREEN) |
|---|---|---|---|
| `test_pd2_status_accepts_relative_root_with_projection` | `tests/test_005_011_t1_relative_root.py` | RED (AssertionError) | **verde** |
| `test_pd2_relative_root_consistent_across_subcommands` | `tests/test_005_011_t1_relative_root.py` | RED (AssertionError) | **ROJO — oráculo insatisfacible (defecto de fixture, §5)** |
| `test_pd2_nonexistent_root_fails_closed_naming_cause` | `tests/test_005_011_t1_relative_root.py` | verde (control) | **verde** |
| `test_pd2_status_without_flag_still_uses_cwd` | `tests/test_005_011_t1_relative_root.py` | verde (control) | **verde** |
| `test_pd2_other_validations_unchanged_with_relative_root` | `tests/test_005_011_t1_relative_root.py` | RED (AssertionError) | **verde** |
| `test_pd5_relative_root_accepted_projects_view` (reemplaza C4) | `tests/test_005_003_t1_compact_view.py` | RED (AssertionError) | **verde** |
| `test_pd5_reference_declares_real_rc_capture_and_repro` (fixture corregido) | `tests/test_005_003_t2_examples_execute.py` | verde (control) | **verde** |
| Regresiones del paquete (`test_packet_prepare.py`, `test_005_003_f2_idle_history.py`, `test_005_005_t1_replace_conserved.py`) | — | — | **28 verdes** |
| Guardas de texto que leen los dos references (`test_005_006_t1_start_procedure.py`, `test_005_006_t6_owner_reviewfix.py`, `test_004_002_t7_limits_rule.py`) | — | — | **23 verdes** |
| Oráculo verde que fija `validate-state` (evidencia del conflicto, §5) | `tests/test_005_001_t3_idle.py` | — | **4 verdes** |

---

## 3. Comandos exactos y su salida

Ejecutados desde `<repo>` (`python3` = 3.13.5). Rutas de este host anonimizadas a `<repo>` / `<tmp>`.

### 3.1 Focal (GREEN)

```
$ python3 -m pytest tests/test_005_011_t1_relative_root.py -q
tests/test_005_011_t1_relative_root.py:185: AssertionError
=========================== short test summary info ============================
FAILED tests/test_005_011_t1_relative_root.py::test_pd2_relative_root_consistent_across_subcommands
1 failed, 4 passed in 3.45s
```

La aserción que falla (línea 185) NO es la resolución de la raíz (que ya funciona) sino el veredicto de
`validate-state` sobre el fixture:

```
E       AssertionError: PD-2 violada: `validate-state --project-root .` debe resolver la raíz
relativa contra el cwd (rc=0); hoy rc=2; stderr='ERROR: no active execution binding in state:
state.execution is empty'
E       assert 2 == 0
```

### 3.2 Los DOS oráculos declarados de PD-3

```
$ python3 -m pytest tests/test_005_003_t1_compact_view.py tests/test_005_003_t2_examples_execute.py -q
.....................                                                    [100%]
21 passed in 7.96s
```

### 3.3 Regresiones declaradas del paquete

```
$ python3 -m pytest tests/test_packet_prepare.py tests/test_005_003_f2_idle_history.py tests/test_005_005_t1_replace_conserved.py -q
............................                                             [100%]
28 passed in 23.44s
```

### 3.4 Regresión proporcional por los dos references corregidos

```
$ python3 -m pytest tests/test_005_006_t1_start_procedure.py tests/test_005_006_t6_owner_reviewfix.py tests/test_004_002_t7_limits_rule.py -q
.......................                                                  [100%]
23 passed in 0.14s
```

### 3.5 Evidencia del conflicto: un oráculo verde fija el rechazo de `execution` vacío

```
$ python3 -m pytest tests/test_005_001_t3_idle.py -q
....                                                                     [100%]
4 passed in 7.67s
```

`tests/test_005_001_t3_idle.py:48-53` declara y fija el comportamiento vigente: «`validate-state` exige
un binding de ejecución activo — … con execution vacío rechaza `state.execution is empty`».

**La suite completa NO se corrió** (política de suite completa: la corre una vez quien cierra).

---

## 4. `git diff --stat` acotado y hash del commit

`git diff --stat HEAD~1 HEAD` (solo los archivos del alcance de escritura del paquete):

```
 skills/cdad-cycle/references/orientation.md       | 16 ++++++------
 skills/cdad-cycle/references/project-execution.md |  3 ++-
 skills/cdad-cycle/scripts/cdad_packet.py          | 30 +++--------------------
 3 files changed, 14 insertions(+), 35 deletions(-)
```

- **Commit:** `53413b39c037b08547d549bd3b4fea2e61fe9a76`
- **Mensaje:** `feat(005-011): T1 GREEN — resolución unificada de --project-root en cdad_packet.py`
- **Archivos:** los 3 del alcance (`cdad_packet.py`, `orientation.md`, `project-execution.md`). El
  `docs/.cdad-state.json` modificado por el orquestador quedó **fuera** del commit. Sin `--no-verify`;
  sin `git stash`.

---

## 5. BLOQUEO PARCIAL declarado — el focal #2 es insatisfacible con el oráculo congelado

**Diagnóstico (caja negra, reproducido).** El fixture `_Fixture` del focal llama a `build_project(self.root)`
de `tests/test_004_002_t2_bootstrap.py`, cuyo `state_document()` deja **`execution: None`** (línea 182) con
`active_feature` fijado. `validate-state` sin `--execution-context` exige un binding activo y falla cerrado
con `ERROR: no active execution binding in state: state.execution is empty` (rc=2). Esto ocurre **igual**
con raíz relativa (`--project-root .`) y con raíz absoluta:

```
$ python3 <repo>/skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root <ABS>
ERROR: no active execution binding in state: state.execution is empty   (rc=2)

$ python3 <repo>/skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root .   # cwd = fixture
ERROR: no active execution binding in state: state.execution is empty   (rc=2)
```

Por lo tanto la aserción `state.returncode == 0` del focal #2 **no depende de la resolución de la raíz**:
no puede satisfacerse con el cambio declarado, y satisfacerla exigiría **cambiar una validación distinta**
de la resolución de la raíz (que `validate-state` acepte un estado sin binding de ejecución). Eso lo
**prohíbe PD-2** («NO cambies ninguna otra validación») y lo **prohíbe el plan T1** («si la unificación
exigiera cambiar una validación distinta de la resolución de la raíz, detener (fuera de alcance)»).
Además, contradiría el oráculo **verde** `tests/test_005_001_t3_idle.py` (§3.5), que fija exactamente el
rechazo.

**Causa raíz:** defecto del oráculo congelado — el focal #2 prueba `validate-state` sobre un fixture que no
tiene ejecución; el RED lo atribuyó al rechazo de raíz relativa (`docs/specs/005-011-common-entry/t1-red.md`
§2.1) sin notar que, resuelta la raíz, el fixture seguía sin binding.

**Corrección mínima pedida al test-writer (no la aplico: el oráculo es suyo y `tests/**` no se edita).**
En `test_pd2_relative_root_consistent_across_subcommands`, preparar el fixture antes de probar
`validate-state` (el propio fixture ya expone `prepare()`, como hace
`test_pd2_other_validations_unchanged_with_relative_root`), o pasar `--execution-context`; la aserción
sobre `validate-policy` (que sí da `VALID` sobre el fixture desnudo) queda como está.

**Estado del trabajo:** el cambio de producto está completo, es el declarado por el contrato, y queda
commiteado para su auditoría. Los 2 oráculos declarados de PD-3, las 5 regresiones del paquete y las
guardas de los dos references corregidos quedan verdes. Se **detiene** la subetapa GREEN a la espera de la
decisión del orquestador (corregir el oráculo vía test-writer y re-verificar el focal).
