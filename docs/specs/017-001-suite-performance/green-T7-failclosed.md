Route C validated (canonical render IDENTICAL, v2 context, contract sha256 matches) — worked only the declared packet (green, T7, write_scope `scripts`).

FINAL TEXT — Reporte GREEN de cierre fail-closed (017-001-suite-performance, T7)

Hecho en `scripts/cdad-suite.py` (subcomando `parallel`), sin tocar `tests/` ni el contrato, sin cambiar paredes/partición/preparación/close/semántica de la gracia:
- R1: si el subreaper no queda activo o el barrido no está disponible (incluida la costura `CDAD_SUITE_FAULT=no-subreaper` / `no-sweep`, documentada como inyección de fallo solo para pruebas y sin efecto cuando no se define), la corrida NO se declara accepted: sale distinto de 0, el veredicto nombra el motivo (subreaper/sweep/family/familia/fault) y `parallel.json` lo declara (`verdict`, `orphans_note`, `family_verifiable:false`, `fault_injection`).
- R2: canario de configuración y de checkout se toman DESPUÉS de resolver la familia (barrido, ventana de gracia 5 s y limpieza); la escritura residual posterior a pytest queda dentro de la foto; si detecta cambios descarta como ya hacía.
- R3: error de lectura durante el barrido no se sustituye por contenido estable ni se omite en silencio: barrido propio con `incomplete` (rutas, p. ej. `checkout_canary.incomplete`), marcador `unreadable-incomplete`, y con `incomplete` no vacío la corrida NO se declara accepted.
- R4: si el evidence-root ya contiene `parallel.json`/`parallel.md`/canarios/`worker-*/` se rechaza con salida distinta de 0 y motivo por stderr (ocupado/occupied, workers, previous attempt); `worker-<i>/` se crea con `exist_ok=False`; help de `--evidence-root` actualizado a "VACÍO… nunca se reutilizan XML/perfiles/fases".

Evidencia:
- Focal completa (22): `python3 -m pytest tests/test_017_001_suite_parallel.py -p no:cacheprovider -q` → **22 passed in 218.85s**.
- Subconjunto R1–R4 tras el fix: `python3 -m pytest tests/test_017_001_suite_parallel.py -k "unverifiable_family or late_checkout_write or unreadable_sweep or rejects_or_isolates" -p no:cacheprovider -q` → **4 passed, 18 deselected in 53.24s** (pre-fix: 4 failed por la razón esperada).
- Focales T1/T2/T3/T4 (017-001): `tests/test_017_001_suite_profile.py + operations + reconcile + external` → **41 passed in 43.78s**; `tranche1 + tranche2` → **2 passed in 1.07s**.
- Regresión proporcional: `tests/test_008_002_suite_evidence.py + test_008_002_suite_selection.py + test_008_005_ci_gate.py` → **49 passed in 44.75s**.
- `python3 scripts/cdad-suite.py validate` → **rc 0** (`status: ok`).
- Corrida real corta limpia (`--workers 2`, dos nodeids tranche1/2, evidence descartable): **rc 0, veredicto `accepted`**, `canary unchanged:true delta:0`, `checkout unchanged:true` (20578 archivos, 480033458 bytes, huella `b594cb1d…`, `incomplete:[]`, costo ~3.19 s), familia `subreaper:true family_verifiable:true orphans_checked:true orphans:0 found:0 cleaned:0 remaining:0`, paredes worker-0 0.81 s (pgid …) / worker-1 1.89 s, total 1.89 s, overlap 0.80 s, passed 2 failed 0. Sigue accepted en condiciones limpias.
- Suite completa no realizada: prohibida por el packet ("no corras la suite completa"); selección ejecutada arriba con sus límites (focal + regresión proporcional, sin `--all`).

Archivos modificados: solo `scripts/cdad-suite.py` (+208/−57).
Commit: `474064e7` — `feat: implement fail-closed del veredicto del lote paralelo (R1-R4, PC-10)` (1 archivo). `git status --short` limpio tras el commit; `tests/` intacto.
