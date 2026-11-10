Route C work complete. FINAL TEXT report below.

---

# FINAL TEXT — test-writer RED T6 ventana-de-gracia (017-001-suite-performance), packet `017-001-suite-performance-test-writer-red-028`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única en el prompt (`packet_id` 017-001-suite-performance-test-writer-red-028, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json --execution-context …/execution.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md --execution-context …` → **EXIT 0**.
- `python3 scripts/cdad_packet.py render --request … --execution-context …` → **byte a byte igual** a `PACKET.md` (`diff` IDENTICAL); el render `--route C` coincide con la identificación del dispatch.
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**, sin switch silencioso. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C. **No se cargó `cdad-cycle` ni otro skill de ciclo**: el packet es el contrato.
- Contrato: `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.
- Solo leí insumos declarados (`spec.md`, `green-T6-setsid-fingerprint.md`, `performance/parallelism.md`, `tests/test_017_001_suite_parallel.py`) y solo edité el write_scope (`tests/`). **Nunca leí implementación**: la CLI se ejercitó como caja negra y solo leí sus artefactos de evidencia (`parallel.json`, stderr) para precisar el motivo del rojo. `scripts/` intacto. Temporal propio de validación (`tmp-packet-check/`) borrado antes del commit.

## 2. Pre-RED

Búsqueda en `tests/` + contrato + insumos autorizados: ningún verificador cubre al hijo transitorio que muere solo poco después de pytest. N1 cubre hijo sin marcador que **sigue vivo** (sleep 60); O1 cubre hijo con nueva sesión que **sigue vivo** (sleep 120); M6 cubre conteo cero excluyendo invocador y ancestros; nada sobre hijo de ~1.5 s **sin** `start_new_session` que sigue vivo al salir pytest y muere solo dentro de la ventana. Protección faltante → **extensión justificada del archivo existente**, sin tocar los dieciséis tests (`git diff --numstat`: `231+/0-`).

## 3. Resultado RED

**Archivo:** `tests/test_017_001_suite_parallel.py` (+231/−0). 1 test nuevo, una promesa observable → **PC-10 (promesa E)**. Sonda creada por el test fuera de `tests/` (árbol temporal) y pasada a `--nodeids`; **nunca** entra en `--all` ni en la suite completa; se borra en `finally` (verificado: sin restos). El hijo vive ~1.5 s, barato.

| Test | Corrección | Falla hoy con |
|---|---|---|
| `test_parallel_transient_child_within_grace_window_is_accepted` (P1) | ventana de gracia: hijo transitorio aceptado | AssertionError: "debe terminar con exito (rc 0), no descartar la corrida; rc=3" — stderr: `veredicto=discarded: orphaned process family found and cleaned (familia de procesos viva tras el lote: encontrados=2 limpiados=1 restantes=1)` |

La promesa exige: `--workers 1` con rc 0 y veredicto `accepted`, `orphans_found >= 1` con detalle de pids, `orphans == 0` al final, sin descarte por un hijo que termina dentro de la ventana.

**Comandos exactos y salidas:**
- `python3 -m py_compile tests/test_017_001_suite_parallel.py` → COMPILE-OK.
- `python3 -m pytest tests/test_017_001_suite_parallel.py -q -p no:cacheprovider -k "transient_child_within_grace_window"` → **1 failed, 16 deselected en ~15.6 s**. Falla por `AssertionError` de promesa ausente (`assert 3 == 0`). Cero `ImportError`/errores de colección.
- Higiene post-corrida: `sleep 1.5` vivos → 0; sondas fuera de `tests/` borradas.
- `git diff --numstat -- tests/test_017_001_suite_parallel.py` → `231 0` (puro agregado); `grep -c "^def test_"` → 17 (16 intactos + 1 nuevo).

**Commit:** `965fe076` — solo `tests/test_017_001_suite_parallel.py`. (`M docs/.cdad-state.json` es preexistente al packet y quedó fuera del commit.)

## 4. Delta de inventario vivo (como texto)

```
+ tests/test_017_001_suite_parallel.py::test_parallel_transient_child_within_grace_window_is_accepted (017-001 T6-P1, PC-10): sonda fuera de tests/ que lanza /bin/sleep 1.5 sin start_new_session justo antes de terminar (hijo vivo al salir pytest, muerto solo ~1.5 s despues); con solo esa sonda y --workers 1 el lote termina rc 0 con veredicto accepted, registra orphans_found >= 1 con detalle de pids y orphans == 0 al final, sin descartar por el hijo transitorio. Estado: RED (rc 3, veredicto discarded, encontrados=2 limpiados=1 restantes=1).
```

## 5. Declaraciones honestas

- Timeout de `_run` (120 s) es guarda de liveness, no oráculo de duración (convención 11).
- Suite completa no realizada: sin autorización para corrida completa; selección ejecutada: el test nuevo (focal RED) con los 16 existentes intactos y deseleccionados; límites: evidencia descartable en temporales, un `sleep 1.5` por corrida, limpiado (0 vivos tras la corrida).
