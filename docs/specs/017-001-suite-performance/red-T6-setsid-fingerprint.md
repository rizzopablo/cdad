Route C work complete. FINAL TEXT report below.

---

# FINAL TEXT — test-writer RED T6 review-T6-003 (017-001-suite-performance), packet `017-001-suite-performance-test-writer-red-027`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única en el prompt (`packet_id` 017-001-suite-performance-test-writer-red-027, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md` → **EXIT 0**.
- `python3 scripts/cdad_packet.py render --request …` → **byte a byte igual** a `PACKET.md` (`diff` IDENTICAL).
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**, sin switch silencioso. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C. **No se cargó `cdad-cycle` ni otro skill de ciclo**: el packet es el contrato.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.
- Solo leí insumos declarados (`spec.md`, `review-T6-003.md`, `performance/parallelism.md`, `red-T6-family-canary.md`, `tests/test_017_001_suite_parallel.py`) y solo edité el write_scope (`tests/`). **Nunca leí implementación**: la CLI se ejercitó como caja negra y solo leí sus artefactos de evidencia (`parallel.json`, stderr) para precisar el motivo del rojo. `scripts/` intacto. Archivo temporal propio de validación (`.cdad/tmp-canon.md`) borrado.

## 2. Pre-RED

Búsqueda en `tests/` + contrato + insumos autorizados: ningún verificador cubre los dos bloqueantes nuevos. N1 cubre hijo sin marcador que **sigue en el grupo** (el barrido por pgid lo vería); nada sobre hijo que **abandona grupo y sesión**. N2 cubre centinela **agregado** en `build/` (el conteo lo delata); nada sobre reescritura del **mismo tamaño con mtime restaurado** (conteo, bytes y mtime máximo intactos). Protección faltante → **extensión justificada del archivo existente**, sin tocar los catorce tests (`git diff --numstat`: `289+/0-`).

## 3. Resultado RED

**Archivo:** `tests/test_017_001_suite_parallel.py` (+289/−0). 2 tests nuevos, uno por promesa observable, ambos → **PC-10 (promesa E)**. Sondas creadas por el test fuera de `tests/` (árbol temporal) y pasadas a `--nodeids`; **nunca** entran en `--all` ni en la suite completa; se borran en `finally` (verificado: sin restos).

| Test | Bloqueante | Falla hoy con |
|---|---|---|
| `test_parallel_detects_session_escaped_descendant_and_discards_run` (O1) | 1, descendiente fuera de sesión | AssertionError: "debe reportar honestamente … informa orphans=0 cleaned=0, familia viva [{'pid': 1763472, 'family': (423, 1763472, …)}]" — hijo reparentado (ppid 423) con pgid propio (nueva sesión), invisible al barrido por grupo |
| `test_parallel_checkout_fingerprint_detects_same_size_same_mtime_rewrite` (O2) | 2, huella ciega a igual-tamaño/igual-mtime | AssertionError: "debe salir distinto de 0 … rc=0" sobre `build/probe_contract.py` reescrito con mismo tamaño y mtime restaurado (stderr: `veredicto=accepted`) |

**Comandos exactos y salidas:**
- `python3 -m py_compile tests/test_017_001_suite_parallel.py` → COMPILE-OK.
- `python3 -m pytest tests/test_017_001_suite_parallel.py -q -p no:cacheprovider -k "session_escaped_descendant or same_size_same_mtime"` → **2 failed, 14 deselected en ~11 s**. Ambas fallan por `AssertionError` de promesa ausente. Cero `ImportError`/errores de colección.
- Higiene post-corrida: `sleep 120` vivos → 0; `git status -- build/` limpio (`build/probe_contract.py` restaurado con bytes y mtime originales); sondas fuera de `tests/` borradas.
- `git diff --numstat -- tests/test_017_001_suite_parallel.py` → `289 0` (puro agregado); `grep -c "^def test_"` → 16 (14 intactos + 2 nuevos).

**Commit:** `3e9191b4` — solo `tests/test_017_001_suite_parallel.py`. (`M docs/.cdad-state.json` es preexistente al packet y quedó fuera del commit.)

## 4. Delta de inventario vivo (como texto)

```
+ tests/test_017_001_suite_parallel.py::test_parallel_detects_session_escaped_descendant_and_discards_run (017-001 T6-O1, PC-10): sonda que lanza /bin/sleep 120 con start_new_session=True sin marcador; con solo esa sonda y --workers 1 el lote informa orphans>=1 (o limpieza equivalente), marca veredicto de descarte, sale !=0 y no deja viva la familia (barrido /proc por marca de sonda con ppid/pgid/sid, no por grupo). Estado: RED (orphans=0, hijo vivo reparentado).
+ tests/test_017_001_suite_parallel.py::test_parallel_checkout_fingerprint_detects_same_size_same_mtime_rewrite (017-001 T6-O2, PC-10): sonda lenta (~5 s); reescritura a mitad del lote de build/probe_contract.py (declarado; si no reescribible se elige otro bajo build/, nunca fuera de build/) con MISMO tamaño y contenido distinto restaurando el mtime original; el comando sale !=0 y parallel.json trae veredicto explícito de descarte conservando la evidencia; original siempre restaurado. Estado: RED (rc=0, veredicto=accepted).
```

## 5. Declaraciones honestas

- Timeouts de subprocess/`communicate` (120 s) y `sleep(2)` de arranque son guardas de liveness, no oráculos de duración (convención 11).
- Archivo mutado declarado: `build/probe_contract.py` (primer candidato reescribible 1 B–64 KiB bajo `build/`); ningún otro archivo del checkout tocado.
- Suite completa no realizada: sin autorización para corrida completa; selección ejecutada: los 2 tests nuevos (focal RED) con los 14 existentes intactos y deseleccionados; límites: evidencia descartable en temporales, un `sleep 120` y una reescritura `build/` por corrida, ambos limpiados.
