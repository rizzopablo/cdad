Route C work complete. FINAL TEXT report below.

---

# FINAL TEXT — implementer GREEN T6 review-T6-003 (017-001-suite-performance), packet `017-001-suite-performance-implementer-green-011`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única en el prompt (`packet_id` 017-001-suite-performance-implementer-green-011, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …` → **EXIT 0**.
- `python3 scripts/cdad_packet.py render --request …` → **byte a byte igual** a `PACKET.md` (`diff` IDENTICAL); el render `--route C` coincide con la identificación del dispatch.
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**, sin switch silencioso. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C. **No se cargó `cdad-cycle` ni otro skill de ciclo**: el packet es el contrato.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.
- Solo leí insumos declarados (`spec.md`, `review-T6-003.md`, `red-T6-setsid-fingerprint.md`, `performance/parallelism.md`, `tests/test_017_001_suite_parallel.py`, `scripts/cdad-suite.py`) y solo edité el write_scope (`scripts/`). **Nunca edité tests ni el contrato**. Paredes, partición, preparación y `close` intactos (diff solo toca canario del checkout, familia de procesos, veredicto y markdown agregado).

## 2. Cambios (solo `scripts/cdad-suite.py`, commit `0c5e4ab0`, +203/−11)

**O1 — descendientes que abandonan grupo y sesión.**
- `_ensure_child_subreaper()`: el runner se vuelve subreaper vía `prctl(PR_SET_CHILD_SUBREAPER)` por ctypes (`libc.so.6`, repliegue a `CDLL(None)`), **antes** de lanzar workers. Todo huérfano —incluido el que hizo `setsid`— vuelve a colgar del runner. Fuera de Linux devuelve `None`; si `prctl` falla, `False` con nota en `parallel.json`. **La garantía de familia requiere Linux** (campo `family_requires_linux: true`, `subreaper` registrado).
- `_live_descendant_pids()` + `_parallel_reap_descendants()`: barrido por **cadena de PPid hasta el runner** (cualquier pgid), que encuentra reparentados; limpieza TERM→KILL con espera, más `_reap_zombies()` (`waitpid(-1, WNOHANG)` en bucle: sin esto los huérfanos cosechados quedaban como zombies del runner y el barrido los contaba como `restantes=1` —detectado en demo y corregido).
- `cmd_parallel`: la cuenta de huérfanos es la **unión** del barrido por pgid existente + el de descendientes; por worker se conservan los campos `orphans_found/cleaned/remaining`. Corrida limpia: `orphans 0`, `accepted`. Con familia viva: veredicto de descarte, `rc != 0` (3 si pytest estaba en 0), evidencia conservada. **Aplica igual al fallo parcial de lanzamiento** (`except Diagnosis/UsageError`: `_parallel_reap` + pgid + descendientes).

**O2 — huella del checkout por contenido.**
- `checkout_canary_snapshot()` ahora calcula `fingerprint` = sha256 global sobre rutas ordenadas de `relativo + sha256(contenido)` de `build/` + `.cdad/` (excluyendo la raíz de evidencia), algoritmo `sha256-per-file-sorted`. Conserva `files/total_bytes/max_mtime(_ns)` como información; agrega `fingerprint_cost_s` medido. La comparación `unchanged` excluye el costo (tiempo) e incluye la huella: una reescritura del mismo tamaño con mtime restaurado cambia la huella y **descarta la corrida** igual que el canario de configuración.

## 3. Evidencia: comandos, salidas y números

- `python3 -m py_compile scripts/cdad-suite.py` → COMPILE-OK.
- **Focal T6 completa (16/16):** `python3 -m pytest -q -p no:cacheprovider -o addopts= tests/test_017_001_suite_parallel.py` → **16 passed en 144.72 s** (corrida final sobre el código commiteado; una corrida previa de 167.30 s fue antes del fix de zombies; tras el fix se re-ejecutaron los 4 tests de familia/huella → 4 passed — y luego la T6 completa de 16).
- **Focales T1/T2/T3-T4:** `tests/test_017_001_suite_profile.py` → 17 passed (23.07 s); `tests/test_017_001_suite_operations.py` → 9 passed (10.38 s); `tests/test_017_001_suite_reconcile.py + tests/test_017_001_suite_external.py` → 15 passed (13.23 s).
- **Regresión proporcional:** `tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **49 passed en 46.14 s**.
- **`validate`:** `python3 scripts/cdad-suite.py validate` → **rc 0, `status: pending`** (umbral efectivo/pendiente declarado por el propio validate; sin fallo).
- **Suite completa no realizada** (sin autorización; el packet la prohíbe expresamente). Selección ejecutada: T6 (16) + T1 (17) + T2 (9) + T3/T4 (15) + regresión (49) + validate.

**Corrida real corta (dos archivos, `--workers 2`):**
`parallel --workers 2 --evidence-root build/tmp-green-011 --nodeids build/tmp-green-011.nodeids` (tranche1+tranche2) → **rc 0, veredicto `accepted`**, `orphans 0` (`checked: true`, 0/0/0), `subreaper: true`, huella `sha256-per-file-sorted b19982ce36084fcf` sobre **20285 archivos / 442 242 385 bytes, costo 3.074 s, unchanged true**; paredes: worker-0 **0.710 s** (pgid 1777891), worker-1 **1.799 s** (pgid 1777892), `total_wall_s` **1.802 s**, `command_wall_s` 8.729 s (incluye canarios), `overlap_s` 0.706 s.

**Sonda setsid re-ejecutada (detección y limpieza):** sonda fuera del checkout (`start_new_session=True`, `/bin/sleep 120`), `parallel --workers 1` → **rc 3**, veredicto `discarded: orphaned process family found and cleaned (encontrados=1 limpiados=1 restantes=0)`, `orphans 1` (1/1/0), canario limpio (descarte puro por familia), **`pgrep -x sleep` vacío tras la corrida: limpieza OK**. (Una primera demo con la sonda bajo `build/` mostró correctamente el canario alterado por la sonda misma —las sondas deben vivir fuera de `build/`/`.cdad/`, como hacen los tests— y expuso el caso zombie que motivó `_reap_zombies()`.)

## 4. Límites y declaraciones honestas

- Costo de la huella por contenido: **~3 s por barrido** (×2 por corrida) sobre 20 285 archivos / ~442 MB en este árbol; medido (`fingerprint_cost_s`) y declarado en `parallel.json` + `parallel.md`. En árboles mayores el costo crece linealmente con el contenido leído.
- La garantía de familia (setsid) **requiere Linux** (`prctl` + `/proc`); fuera de Linux el runner lo declara (`subreaper: null/false` + `orphans_note`) en vez de publicar `orphans: 0`.
- `M docs/.cdad-state.json` es del orquestador (puntero `active_packet` a este packet, estado `prepared`) y **quedó fuera del commit**, como en el RED previo. Commit `0c5e4ab0` = solo `scripts/cdad-suite.py`.
- Artefactos de demo bajo `build/` (`tmp-green-011`, `tmp-setsid-*`) y la sonda fuera del repo fueron **borrados** tras registrar los números; `git status` solo muestra el state del orquestador.
- No afirmo equivalencia con la suite completa ni extrapolo las paredes de la muestra (2 tests) a `--all`; la acreditación final con `--all` y la regla ≥15 % sigue siendo T7.
