Route C validada. Implementación GREEN completa. Reporte final:

# FINAL TEXT — 017-001-suite-performance implementer GREEN (T7, packet …-green-013)

## Validación Route C (previa al trabajo)
- Identificación del dispatch (`packet_id` 017-001-suite-performance-implementer-green-013, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`) coincide con `REQUEST.json` y `PACKET.md`.
- `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e` ✅.
- Contexto de ejecución v2 (`schema_version: 2`) ✅. Sin mezcla de rutas (cero marcadores inline en el dispatch) ✅.
- `python3 scripts/cdad_packet.py render --request …/REQUEST.json` → `diff` contra `PACKET.md` = **IDENTICAL** ✅. Procedí por Ruta C.
- Leídos solo inputs declarados + alcance (`docs/specs/017-001-suite-performance`, `scripts`, `tests` solo lectura). Escrito solo `scripts/`.

## Cambio (mínimo, acotado al veredicto)
- Archivo: `scripts/cdad-suite.py` (único modificado, +8/−1). Commit `6645a340` — `feat: implement checkout canary verdict without max_mtime_ns (017-001 T7 GREEN)`.
- `cmd_parallel`: `_checkout_key` deja de comparar `max_mtime_ns`; ahora solo `scope, files, total_bytes, fingerprint, fingerprint_algo`. `max_mtime_ns` sigue en `parallel.json` como información (no se tocó `checkout_canary_snapshot`).
- Justificación escrita como comentario sobre `_checkout_key`: la huella es sha256 por archivo sobre rutas ordenadas; files + total_bytes cubren altas/bajas/cambios de contenido; el mtime de directorios cambia por scratch legítimo bajo `.cdad/tmp` (crear/retirar subdirectorios) sin cambiar un byte, por eso no decide el veredicto.
- No tocado: `tests/`, contrato, canario de configuración, paredes, partición, preparación, familia de procesos, gracia, close.

## Evidencia de tests (comandos exactos)
1. Focal T6 completa (18):
   `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_017_001_suite_parallel.py --basetemp=/tmp/pytest-017-green013` → **18 passed in 195.75 s**, rc 0 ✅ (incluye la트는 nueva Q1 de churn transitorio, antes roja con rc 3).
2. Focales T1/T2/T3/T4:
   `… pytest … tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py tests/test_017_001_suite_profile.py tests/test_017_001_suite_operations.py` → **28 passed in 40.17 s**, rc 0 ✅.
   `… pytest … tests/test_017_001_suite_reconcile.py tests/test_017_001_suite_external.py` → **15 passed in 12.53 s**, rc 0 ✅.
3. Regresión proporcional: cubierta por (2) — archivos 017-001 vecinos del cambio; sin fallos.
4. `python3 scripts/cdad-suite.py validate` → `"status": "ok"`, rc 0 ✅.

## Caso real que hoy fallaba (veredicto acepta churn)
- Selección: 2 nodeids de `tests/test_010_004_t5_e2e.py` en `/tmp/opencode_run/t7-real.nodeids`.
- `python3 scripts/cdad-suite.py parallel --workers 1 --evidence-root /tmp/opencode_run/ev-real --nodeids /tmp/opencode_run/t7-real.nodeids` → **rc 0**, `pared_total=29.68 s, trabajo=28.18 s, passed=2 failed=0 skipped=0, canary_delta_lines=0, veredicto=accepted` ✅.
- `parallel.json`: `verdict: accepted`, `checkout_canary.unchanged: True`, `clean: True`, `max_mtime_ns: 1794126081080893205` informado (no nulo), `files: 20421`, `total_bytes: 450372681`, `fingerprint: 6e50fac3…`, `algo: sha256-per-file-sorted` ✅.

## Rechazo por contenido sigue vivo
- Sonda `/tmp/opencode_run/probe-reject/test_probe_reject_013.py` deja archivo nuevo persistente `.cdad/tmp/canary-reject-013-sentinel.txt`, corrida corta `--workers 1` → **veredicto `rejected: canary detected changes… (checkout unchanged=False)`**, `unchanged: False`, **rc verdadero 3** (el primer RC:0 fue enmascaramiento del pipe a `tail`; re-medido sin pipe) ✅. Sentinel retirado después; sin residuos (`CLEANED:0`).

## Límites
- **Suite completa no realizada**: prohibida por este packet (`no corras la suite completa`); amparo: política declarada en la parte común (focal + regresión proporcional sin completa como rutina). Números de arriba son la selección ejecutada, no una suite verde.
- `docs/.cdad-state.json` figura `M` pero es ajeno (el orquestador actualizó `active_packet` a este packet); no lo toqué ni lo commiteé — mi commit es solo `scripts/cdad-suite.py`.
- Calidad (5 checks): guard clauses y estructura existentes preservadas; estados ilegales no introducidos (veredicto por igualdad de dicts); cambio atómico y predecible; fail-fast intacto (rechazo con rc 3); nombres intencionales sin cambios.
