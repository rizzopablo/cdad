Route C work complete. FINAL TEXT report below.

---

# FINAL TEXT — implementer GREEN T6 ventana-de-gracia (017-001-suite-performance), packet `017-001-suite-performance-implementer-green-012`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única en el prompt (`packet_id` 017-001-suite-performance-implementer-green-012, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md --execution-context …/execution.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py render --request … --execution-context …` → **byte a byte igual** a `PACKET.md` (`diff` IDENTICAL, 9115 bytes ambos); el render `--route C` coincide con la identificación del dispatch.
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**, sin switch silencioso. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C. **No se cargó `cdad-cycle` ni otro skill de ciclo**: el packet es el contrato.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.
- Solo leí insumos declarados (`spec.md`, `red-T6-grace.md`, `green-T6-setsid-fingerprint.md`, `performance/parallelism.md`, `tests/test_017_001_suite_parallel.py`, `scripts/cdad-suite.py`) y solo edité el write_scope (`scripts/`). **Nunca edité tests ni el contrato**. Paredes, partición, preparación, huella y `close` intactos (el diff solo toca familia de procesos/veredicto + markdown agregado).

## 2. Cambios (solo `scripts/cdad-suite.py`, commit `e1f368a0`, +205/−39)

**Ventana de gracia T6 (hijo transitorio que muere solo).** Semántica pedida, aplicada igual al fallo parcial de lanzamiento:
- `_parallel_family_snapshot(pgids)`: primer barrido como **unión** pgid + cadena de PPid hasta el runner (cubre reparentados por subreaper, cualquier pgid), excluyendo runner/invocador/ancestros; devuelve detalle acotado por pid (`pid, ppid, pgid, cmdline` truncada a 200, máximo 20 entradas). No mata a nadie. `None` si /proc no disponible.
- `_parallel_grace_wait(pgids)`: espera `PARALLEL_GRACE_WINDOW_S = 5.0 s` sondeando cada `PARALLEL_GRACE_POLL_S = 0.2 s` **sin matar**, cosechando zombies reparentados (`_reap_zombies`) para no contarlos como vivos; corta antes si la familia queda vacía. Si el primer barrido está vacío se salta la espera (las corridas limpias no pagan 5 s).
- Si la familia quedó vacía en la gracia → **aceptada**: `orphans == 0`, `orphans_found >= 1` con detalle, `cleaned = remaining = 0`, sin matar, veredicto `accepted`.
- Si sigue viva al terminar la gracia → **fuga real**: se mata (TERM y luego KILL vía `_parallel_reap_pgrp` + `_parallel_reap_descendants`), se informa `orphans` (vivos al final de la gracia), `orphans_cleaned`, `orphans_remaining` (unión post-limpieza, esperado 0), veredicto `discarded…` y salida 3 (evidencia conservada).
- `parallel.json` agrega: `orphans_detail`, `orphans_found_pids`, `orphans_found_detail`, `grace_window_s`, `grace_poll_s`. Por worker se conservan `orphans_found/cleaned/remaining` (found del primer barrido pgid; 0/0 si la gracia lo resolvió).
- Ruta de fallo parcial (`except Diagnosis/UsageError`): tras `_parallel_reap(children)` hace primer barrido + gracia y solo entonces limpia por grupo/descendientes — misma semántica, sin dejar familia viva.

## 3. Evidencia: comandos, salidas y números

- `python3 -m py_compile scripts/cdad-suite.py` → COMPILE-OK.
- **RED nuevo (P1) primero:** `-k transient_child_within_grace_window` → **1 passed, 16 deselected en 7.92 s** (antes rc=3 `discarded`; ahora rc=0 `accepted`).
- **Focal T6 completa (17/17):** `python3 -m pytest tests/test_017_001_suite_parallel.py -q -p no:cacheprovider -o addopts=` → **17 passed en 162.97 s, RC=0**.
- **Focales T1/T2/T3/T4:** `tests/test_017_001_suite_profile.py` → 17 passed (21.25 s); `tests/test_017_001_suite_operations.py` → 9 passed (10.19 s); `tests/test_017_001_suite_reconcile.py + tests/test_017_001_suite_external.py` → 15 passed (12.82 s).
- **Regresión proporcional:** `tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **49 passed en 45.61 s**.
- **`validate`:** `python3 scripts/cdad-suite.py validate` → **rc 0, `status: pending`** (umbral efectivo/pendiente declarado por el propio validate; sin fallo).
- **Suite completa no realizada** (sin autorización; el packet la prohíbe expresamente). Selección ejecutada: T6 (17) + T1 (17) + T2 (9) + T3/T4 (15) + regresión (49) + validate.

**Corrida real final4 (dos workers sobre los seis archivos más caros):**
`parallel --workers 2 --evidence-root ~/clawd/projects/cdad/evidence/017-001-t6-final4/parallel --nodeids ~/clawd/tmp/017-001-t4b.nodeids --balance-from ~/clawd/projects/cdad/evidence/017-001-t6-final3/serial/attempt-20261108T043131058861Z-1781438-46b5560e/profile.json` → **rc 0, veredicto `accepted`**, `passed=57 failed=0 skipped=0`; `orphans_found=9` con detalle de 9 pids, `orphans=0 cleaned=0 remaining=0` (nueve transitorios reales murieron dentro de la gracia — la ventana funcionó en producción, no solo en sonda); `grace_window_s=5.0 grace_poll_s=0.2`; paredes: worker-0 **562.98 s** (pgid 2344260, found 2/0/0), worker-1 **618.87 s** (pgid 2344261, found 7/0/0), `total_wall_s` **618.87 s**, trabajo **1177.87 s**, `overlap_s` **562.98 s**; canario config limpio (`delta 0`), checkout `unchanged true`, `subreaper: true`, `orphans_checked: true`.

## 4. Límites y declaraciones honestas

- La garantía de familia (incluida la gracia) **requiere Linux** (`prctl` + `/proc`); fuera de Linux el runner lo declara (`subreaper: null/false` + `orphans_note`) en vez de publicar `orphans: 0`. Sin cambios.
- La gracia añade hasta ~5 s solo cuando el primer barrido encuentra familia viva (fugas persistentes sleep 60/120 y corridas con transitorios); las corridas limpias no esperan.
- El detalle de familia está acotado (20 entradas, cmdline 200 chars): suficiente para evidencia, sin volcar `/proc` entero.
- `M docs/.cdad-state.json` es del orquestador (puntero `active_packet` a este packet, estado `prepared`) y **quedó fuera del commit**, como en paquetes previos. Commit `e1f368a0` = solo `scripts/cdad-suite.py`.
- Higiene verificada: `pgrep -x sleep` vacío tras cada fase; sondas de tests viven fuera de `tests/` y se borran en `finally`; evidencia final4 fuera del repo (`projects/cdad/evidence/…`), `git status` limpio salvo el state del orquestador.
- No afirmo equivalencia con la suite completa ni extrapolo paredes de la muestra a `--all`; la acreditación final con `--all` y la regla ≥15 % sigue siendo T7.
