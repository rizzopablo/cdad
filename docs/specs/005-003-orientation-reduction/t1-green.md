## Report — GREEN T1 (005-003-orientation-reduction)

### (1) Archivos tocados

**`skills/cdad-cycle/scripts/cdad_packet.py`** (+298/-2) — subcomando read-only `status` (`compact-view-v1`):
- Constantes `DEFAULT_VIEW_MAX_BYTES = 16_384` y la vocabulario cerrado `ENTRY_{CONTINUITY_RECONCILE,NEXT_UNIT,DIAGNOSIS}`; `import subprocess`.
- `status_view()`: proyección determinista (`json.dumps(..., sort_keys=True, indent=2)`) de los campos de §2.1 (`project`, `epic`, `feature`, `execution`, `packet`, `authority`, `version`, `next`, `entry`, `unknowns`), **sin** `stage_history`, con **fallo cerrado** por encima del límite (rc≠0, stdout vacío, diagnóstico que nombra el límite y `--max-bytes`).
- Helpers: `_read_optional_document` (fuentes ausentes → causa en `unknowns[]`, nunca valor fabricado, INV-9), `_version_verdict` (reusa el `cdad-version-check.py` canónico; rc≠0 = no verificado, §2.4), `_pending_work` (solo campos/dirs existentes, INV-2), `_entry_selection` (mapa explícito de §2.2, sin inferencia por literal), `_next_route` (ruta + fuente declarada), `_plan_marker`, `_status_project_root`.
- `_status_project_root`: diagnóstico de la **asimetría de raíz relativa** (nombra `cdad_continuity.py`/`cdad_packet.py` y la recuperación «raíz absoluta»), acotado a `status` (C4/PD-5).
- Parser: `status` con `--project-root` y `--max-bytes` (default 16384). `main`: dispatch + resolución de raíz para `status`.
- Read-only: no usa `_ProjectLock` ni escribe archivos (INV-1).

**`skills/cdad-cycle/references/orientation.md`** (nuevo, 79 líneas) — esqueleto operativo exigido por §2.3/§2.5: patrón de captura del `rc` sin enmascarar (`PIPESTATUS[0]`, `pipefail`, o sin tubería), operaciones frecuentes (`prepare` y sub-modos, `validate-*`, `begin`, `--record-dispatch` + `docs/attempt.json`), la asimetría de raíz relativa, y la cita del asset de ejemplos (contenido completo de T2). Sin valores del VPS.

`tests/**` intacto.

### (2) Focal
```
python3 -m pytest tests/test_005_003_t1_compact_view.py -q
→ 11 passed in 6.10s
```

### (3) Regresión del área
```
python3 -m pytest tests/ -q -k "packet or state or role_packet"
```
- **Baseline (antes del cambio):** `3 failed, 128 passed` — los 3 fallos eran exactamente los focales RED de T1 que el selector captura.
- **Después del cambio:** `131 passed, 687 deselected` — **sin fallos nuevos**.

La suite completa **no** se corrió (la corre quien cierra).

### (4) Commit
`2bc159a360eaf19cb417cff8385a6fc5665c0a90` — `feat(005-003): T1 - vista compacta (status) y seleccion de entrada` (2 files changed, 377 insertions(+), 2 deletions(-)). Solo mis dos archivos; `docs/.cdad-state.json` (modificado) y `docs/specs/005-003-orientation-reduction/t1-red.md` (untracked) quedaron **fuera** del commit por estar fuera de mi write scope.

### (5) Desviaciones / conflictos
Ninguno. Los 11 tests aprobados se hicieron pasar sin editarlos. Sin ampliación de validación: el cambio es aditivo (subcomando nuevo + referencia nueva) y no toca un contrato compartido; las regresiones del área quedaron verdes.