All green and committed. Delivering the packet report:

---

# FINAL TEXT — implementer GREEN T6 (017-001-suite-performance), packet `017-001-suite-performance-implementer-green-008`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación única del dispatch (`packet_id` 017-001-suite-performance-implementer-green-008, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `.cdad/packets/…/REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md` → **EXIT 0**.
- `sha256sum docs/specs/017-001-suite-performance/spec.md` = `472bab0…92672e` ✓.
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**. Cero marcadores `---cdad-packet-json` en el prompt → sin mezcla route A/C. **No cargué `cdad-cycle` ni otro skill de ciclo.**
- Solo leí insumos declarados (`spec.md`, `review-T6.md`, `red-T6-fixes.md`, `performance/parallelism.md`, `tests/test_017_001_suite_parallel.py`, `scripts/cdad-suite.py`) y solo edité el write_scope (`scripts/`). **No toqué `tests/` ni el contrato** (`git diff -- tests/` vacío de mis cambios; `M docs/.cdad-state.json` es preexistente a este packet, quedó fuera del commit).

## 2. Implementación (solo `scripts/cdad-suite.py`, commit `cf417722`)

| Bloqueante | Corrección |
|---|---|
| M1 worker vacío | Grupos sin archivos no lanzan pytest; `workers` trae solo lanzados; `workers_launched`/`skipped_empty_workers` declarados |
| M2 paredes/solapamiento | `started_at`/`finished_at` ISO 8601 con zona y microsegundos (`utc_now_fine`), fin real por hijo vía poll (no `wait()` en orden); `total_wall_s` = ventana de ejecución concurrente (los barridos de canario, ~segundos en este árbol, quedan fuera por exigencia de M2: total−max ≤ 1.0 s); pared completa aparte como `command_wall_s` |
| M3 huérfanos + fallo parcial | Barrido real de descendientes en `/proc` con la raíz como marcador (`orphans_checked`, conteo medido nunca fijo); ante fallo de evidencia/lanzamiento se termina y espera a los hijos ya lanzados (`_parallel_reap`) y se sale ≠ 0 con motivo por stderr |
| M4 canario checkout | `checkout_canary` sobre `build/` + `.cdad/` (archivos, bytes totales, mtime máximo, `unchanged`); excluye la propia raíz de evidencia; canario de configuración intacto; recorrido sin `resolve()` por ruta (4.0 s → 0.96 s) |
| M5 preparación medida | `preparation_measured_s` = operaciones no compartidas de preparación (fase `setup` o marca explícita) del propio perfil, nunca resta de paredes; `preparation_source == "per-worker-profiles"`; `duplicated_preparation_s` = suma − referencia `--balance-from`, `null` con motivo sin referencia; perfil por worker construido con `build_profile` (trae `operations`) |
| `close` | Intacto: mismo comportamiento y campos; único agregado aditivo `preparation_measured_s` en `profile.json`, exigido por M5 para la referencia (los tests de perfil usan aserciones de subconjunto) |

## 3. Evidencia (comandos exactos y salidas)

- `python3 -m pytest tests/test_017_001_suite_parallel.py -q -p no:cacheprovider` → **11 passed en 49.32 s**.
- Regresión proporcional + focales T1/T2/T3-T4: `python3 -m pytest tests/test_017_001_suite_parallel.py tests/test_017_001_suite_profile.py tests/test_017_001_suite_operations.py tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py tests/test_017_001_suite_reconcile.py tests/test_017_001_suite_external.py tests/test_008_002_suite_evidence.py -q -p no:cacheprovider` → **59 passed en 106.72 s**.
- `python3 scripts/cdad-suite.py validate` → **rc=0**.
- Demo real `parallel --workers 2` con los dos nodeids de tranche + `--balance-from` (perfil serial): `passed=2 failed=0`, workers con `wall 3.296/7.908 s` (host cargado), `|wall − (fin−ini)| = 0.0000` en ambos, `total−max = 0.005 s`, `overlap = 3.291 s`, canario config y checkout `unchanged == true` (20091 archivos), `preparation_source = per-worker-profiles`, `duplicated = 0.0005 s`, `orphans_checked == true`, `orphans = 0`, barrido `/proc` post-corrida: **none**. `close` de referencia: **rc=0**, perfil `complete`.
- Incidencia de proceso: un run focal en background de la sesión anterior quedó colgado del corte de turno; lo terminé (SIGTERM al pytest + SIGKILL al hijo) y verifiqué **cero procesos pytest/cdad-suite vivos** antes y después de cada corrida.
- **Commit:** `cf417722` — solo `scripts/cdad-suite.py` (+341/−39).

## 4. Límites y declaraciones honestas

- **Suite completa no realizada**: sin autorización para corrida completa (el packet ordena explícitamente NO correrla); selección ejecutada: focal T6 (11) + 8 archivos de regresión/focales (59) + `validate` + 2 corridas cortas reales (serial + parallel con 2 nodeids). Host compartido cargado (paredes demo de 3–8 s para tests de ~1–2 s); no afecta la coherencia verificada.
- `M docs/.cdad-state.json` es preexistente (ya lo registraba review-T6) y quedó fuera del commit.
- Las corridas demo usaron evidencia descartable bajo `.cdad/tmp/`, eliminada tras verificar (el árbol queda sin restos salvo el commit).
