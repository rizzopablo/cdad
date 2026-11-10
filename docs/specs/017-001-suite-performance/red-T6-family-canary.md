Route C work complete. FINAL TEXT report below.

---

# FINAL TEXT — test-writer RED T6 review-T6-002 (017-001-suite-performance), packet `017-001-suite-performance-test-writer-red-026`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única en el prompt (`packet_id` 017-001-suite-performance-test-writer-red-026, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md` → **EXIT 0**.
- `python3 scripts/cdad_packet.py render --request …` → **byte a byte igual** a `PACKET.md` (`diff` IDENTICAL).
- `python3 scripts/cdad_packet.py render --route C --request …` → identificación canónica **igual** a la del dispatch.
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**, sin switch silencioso. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C. **No se cargó `cdad-cycle` ni otro skill de ciclo**: el packet es el contrato.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.
- Solo leí insumos declarados (`spec.md`, `review-T6-002.md`, `performance/parallelism.md`, `red-T6-fixes.md`, `tests/test_017_001_suite_parallel.py`) y solo edité el write_scope (`tests/`). **No toqué `scripts/` ni el contrato. Nunca leí implementación**: la CLI se ejercitó como caja negra y solo leí sus artefactos de evidencia (`parallel.json`, stderr) para precisar el motivo del rojo.

## 2. Pre-RED

Búsqueda en `tests/` + contrato + insumos autorizados: ningún verificador cubre los dos bloqueantes nuevos. M3/M6 cubren huérfanos por coincidencia de cmdline (con y sin falso positivo del invocador), pero nada sobre descendiente vivo **sin** la raíz en su cmdline con familia registrada por pgid, ni sobre canario que **descarte** la corrida. Protección faltante → **extensión justificada del archivo existente**, sin tocar los doce tests (`git diff --numstat`: `273+/0-`).

## 3. Resultado RED

**Archivo:** `tests/test_017_001_suite_parallel.py` (+273/−0). 2 tests nuevos, uno por promesa observable, ambos → **PC-10 (promesa E)**. Sondas creadas por el test fuera de `tests/` (árbol temporal) y pasadas a `--nodeids`; **nunca** entran en `--all` ni en la suite completa; se borran en `finally` (verificado: sin restos).

| Test | Bloqueante | Falla hoy con |
|---|---|---|
| `test_parallel_cleans_process_family_without_cmdline_marker` (N1) | 1, familia sin cmdline | AssertionError: "debe reportar honestamente que encontró y limpió descendientes vivos (orphans >= 1 o campo equivalente); informa orphans=0 cleaned=None (el conteo por cmdline no ve al hijo y publica orphans=0)" |
| `test_parallel_altered_checkout_canary_rejects_run` (N2) | 2, canario que descarta | AssertionError: "debe salir distinto de 0 (descarte/fallo), no con éxito limpio; rc=0" (stderr: `passed=1 failed=0 skipped=0, canary_delta_lines=0`) |

**Comandos exactos y salidas:**
- `python3 -m py_compile tests/test_017_001_suite_parallel.py` → COMPILE-OK.
- `python3 -m pytest tests/test_017_001_suite_parallel.py -q -p no:cacheprovider -k "without_cmdline_marker or altered_checkout_canary"` → **2 failed, 12 deselected en 11.04 s**. Ambas fallan por `AssertionError` de promesa ausente. Cero `ImportError`/errores de colección.
- Higiene post-corrida: `sleep 60` vivos → 0; centinelas `build/.canary_probe_*` → ninguno.
- `git diff --numstat -- tests/test_017_001_suite_parallel.py` → `273 0` (puro agregado); `grep -c "^def test_"` → 14 (12 intactos + 2 nuevos).

**Commit:** `c7a90992` — solo `tests/test_017_001_suite_parallel.py`. (`M docs/.cdad-state.json` es preexistente al packet y quedó fuera del commit.)

## 4. Delta de inventario vivo (como texto)

```
+ tests/test_017_001_suite_parallel.py::test_parallel_cleans_process_family_without_cmdline_marker (017-001 T6-N1, PC-10): sonda que deja hijo sleep 60 sin marcador y sobreviviente a pytest; con solo esa sonda y --workers 1 el lote registra pgid por worker, informa orphans>=1 (o limpieza equivalente), sale !=0 y no deja viva la familia (barrido /proc por pgid, no por cmdline). Estado: RED (orphans=0).
+ tests/test_017_001_suite_parallel.py::test_parallel_altered_checkout_canary_rejects_run (017-001 T6-N2, PC-10): sonda lenta (~5 s); centinela único en build/ a mitad del lote; el comando sale !=0 y parallel.json trae veredicto explícito de rechazo/descarte conservando la evidencia; centinela siempre borrado. Estado: RED (rc=0, solo avisa).
```

## 5. Declaraciones honestas

- Timeouts de subprocess/`communicate` (120 s) y `sleep(2)` de arranque son guardas de liveness, no oráculos de duración (convención 11).
- Canario de configuración: **no forzado**; queda declarado cubierto por el mismo código de veredicto que N2 verifica (el packet lo permite).
- Suite completa no realizada: sin autorización para corrida completa; selección ejecutada: los 2 tests nuevos (focal RED) con los 12 existentes intactos y deseleccionados; límites: evidencia descartable en temporales, un sleep 60 y un centinela `build/` por corrida, ambos limpiados.
