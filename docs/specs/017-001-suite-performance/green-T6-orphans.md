Route C work complete. FINAL TEXT report below.

---

# FINAL TEXT — implementer GREEN corrección orphans T6 (017-001-suite-performance), packet `017-001-suite-performance-implementer-green-009`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única en el dispatch (`packet_id` 017-001-suite-performance-implementer-green-009, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json --execution-context …/execution.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md --execution-context …` → **EXIT 0**.
- `python3 scripts/cdad_packet.py render --request … --execution-context …` → **byte a byte igual** a `PACKET.md` (diff vacío, `PACKET_MATCH`).
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**, sin switch silencioso. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e` ✓.
- Solo leí insumos declarados (`spec.md`, `red-T6-orphans.md`, `review-T6.md`, `tests/test_017_001_suite_parallel.py`, `scripts/cdad-suite.py`) y solo edité el write_scope (`scripts/`). **Nunca edité tests/**. No cargué `cdad-cycle` ni otro skill de ciclo: el packet es el contrato.

## 2. Cambio (mínimo, solo `scripts/cdad-suite.py`)

**Causa:** `live_pids_with_marker()` contaba todo PID vivo cuya cmdline mencionara la raíz de evidencia, excluyendo solo el pid propio. El invocador, ancestros o un hermano con la raíz en su cmdline elevaban `orphans` a ≥1 con `children_terminated == true`.

**Corrección:**
- Nuevo `_ppid_of(pid)`: PPid desde `/proc/<pid>/status`, `None` si ilegible.
- Nuevo `_is_descendant_of(pid, ancestor)`: camina la cadena de PPid hasta init con guarda de ciclos; `True` solo si el ancestro aparece.
- `live_pids_with_marker()` ahora exige, además de la coincidencia de cmdline, `_is_descendant_of(pid, os.getpid())` — hijos y nietos incluidos, runner excluido, no-descendientes excluidos. Pids con PPid ilegible no se cuentan (no se puede probar descendencia; evita falsos positivos).
- `cmd_parallel()`: si `/proc` no disponible (`live is None`), `orphans_checked=false`, `orphans=null` con motivo aditivo `orphans_note="/proc no disponible: sin barrido de descendientes"`. Semántica de paredes, canario, preparación y close intacta.

**Commit:** `a12ba4c2` — solo `scripts/cdad-suite.py` (+42/−2). (`M docs/.cdad-state.json` es del orquestador —puntero `active_packet`— y quedó fuera del commit.)

## 3. Evidencia: comandos exactos y salidas

- `python3 -m py_compile scripts/cdad-suite.py` → `COMPILE_OK`.
- Focal M6 (el RED): `python3 -m pytest tests/test_017_001_suite_parallel.py::test_parallel_single_worker_reports_zero_orphans_excluding_invoker_and_ancestors -q -p no:cacheprovider` → **1 passed en 3.08 s** (antes: failed con `orphans=1`).
- Focal T6 completa: `python3 -m pytest tests/test_017_001_suite_parallel.py -q -p no:cacheprovider` → **12 passed en 48.12 s** (11 anteriores + M6).
- Focales T1/T2/T3-T4 + regresión proporcional: `python3 -m pytest tests/test_017_001_suite_profile.py tests/test_017_001_suite_operations.py tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py tests/test_017_001_suite_reconcile.py tests/test_017_001_suite_external.py tests/test_008_002_suite_evidence.py -q -p no:cacheprovider` → **48 passed en 47.71 s**.
- `python3 scripts/cdad-suite.py validate` → **rc=0, status ok**.
- Corrida real corta (selección de dos archivos, `--workers 2`, evidencia descartable `~/<workspace>/tmp/cdad-val/real-short`): `python3 scripts/cdad-suite.py parallel --workers 2 --evidence-root ~/<workspace>/tmp/cdad-val/real-short --nodeids ~/<workspace>/tmp/cdad-val/real-short.nodeids` → **rc=0**, `pared_total=1.66 s, trabajo=0.02 s, solapamiento=0.75 s, passed=2 failed=0 skipped=0, canary_delta_lines=0`.
  - `orphans: 0`, `orphans_checked: True`, `orphans_note: None`, `children_terminated: True`.
  - Paredes por worker: worker-0 `wall_s=0.766 s` (prep `0.002 s`, work `0.010 s`, rc=0, 1 passed); worker-1 `wall_s=1.637 s` (prep `0.002 s`, work `0.009 s`, rc=0, 1 passed). `total_wall_s=1.657 s`, `overlap_s=0.745 s`.
  - Canario del checkout: `clean=true, unchanged=true`, alcance `build/` + `.cdad/`, `files=20117`, `total_bytes=426280101`.
  - Preparación medida: `total_preparation_s=0.004 s` (suma por worker desde sus perfiles). Consolidado `{passed: 2, failed: 0, skipped: 0}`.

## 4. Límites honestos

- **Suite completa no realizada**: sin autorización para corrida completa; la política del hogar canónico autoriza focal + regresión proporcional como rutina. Selección ejecutada: T6 (12) + 48 focales/regresión + `validate` + corrida real corta de 2 nodeids. No se afirma suite completa verde.
- El barrido por cadena de PPid no detectaría un nieto reparentado a init tras la muerte de su padre (cadena rota); es la implementación que el packet ordena y cubre el defecto publicado (no-descendientes contados como huérfanos).
- Tiempos informados como medición (`wall_s`, `overlap_s`, `preparación`), nunca como oráculo de corrección; los timeouts de subprocess son guardas de liveness, no cotas.
- `docs/.cdad-state.json` modificado por el orquestador antes de mi trabajo; no lo toqué ni lo commiteé.
