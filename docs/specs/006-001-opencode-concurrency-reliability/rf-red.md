Comienzo leyendo los inputs declarados: la spec aprobada y la review formal, más el estado de los tests existentes para entender la mecánica de fixtures.
La actualización del catálogo no cambia el plan. Continúo: ahora necesito entender la mecánica de fixtures de los focales existentes (lectura permitida: `tests/`). Leo los focales de la feature — T2 (espera/recuperación) y T1b (modo servicio) — para reutilizar la mecánica sin tocarlos.
Continúo con el resto de T2 (PD-11) y luego leo T1b (mecánica del modo servicio).
Ahora leo el focal T1b (modo servicio) para entender la mecánica del fake de `service status` y el registro del servicio (D-11).
Ahora necesito ver la fixture base `Pd600T1Case` en T1 (métodos `fake_runtime`, `dispatch`, `patch_config`, `envelope`, `binary_calls`, etc.).
Tengo la mecánica de T1/T1b/T2. Ahora leo la base `AdapterCase` (test_005_009_t2_opencode_adapter.py) para conocer `fake_runtime`, `envelope`, `binary_calls` y helpers.
La mecánica está clara. Verifico que no exista aún el archivo objetivo y que el árbol esté limpio, y reviso las constantes que importaré (`FAKE_RUNTIME`, `FAKE_MODEL`, `OUTPUT_KEYS`).
La mecánica está clara. Reviso `conftest.py` para saber cómo correr los focales:
Escribo el focal RED propio con su fake propio:
Corro el focal completo y observo qué falla y por qué:
B2 confirmado en rojo por el fallo esperado (`completed != blocked` — fail-open). Ahora verifico que B1 falla por la causa prevista (envelope de la interfaz) y no por otra cosa:
B1 falla en la aserción de sesión (`None != 'ses_…'`) — consistente con el envelope de la interfaz (session null). Para dejar la evidencia completa (el diagnóstico de la interfaz), reordeno las aserciones de B1: primero el discriminador del contrato (origen del envelope), luego la correlación:
Evidencia RED confirmada. Verifico el alcance del diff y commiteo solo `tests/`:
# Informe del rol — test-writer RED (review-fix 006-001-opencode-concurrency-reliability)

**Packet:** `006-001-opencode-concurrency-reliability-test-writer-red-005` · substage `red` · contrato: spec v2 aprobada (`docs/specs/006-001-opencode-concurrency-reliability/spec.md`, sha256 `dac418b9…` verificado contra el árbol) + review formal (`review.md`, B1–B3). No se leyó implementación (`skills/`, `scripts/`, `agents/`, `sources/`, `build/`, `install.sh`); solo inputs declarados (spec, review) y tests existentes (mecánica de fixture). Write scope respetado: solo `tests/`.

## Archivo modificado

- **`tests/test_006_001_reviewfix.py`** (nuevo, 807 líneas). Fake PROPIO autónomo (`opencode-fake-rf`: `--version`, `service status` con escenario/retardo propios, variantes de `run` `succeeded | exit-row-not-idle | hangs`), servidor `/api/info` con retardo propio (`DelayedInfoServer`). Ningún focal existente ni el fake compartido fueron tocados; solo reuso infraestructura publicada por import (`Pd600T1Case`, `T1bServiceCase`, `Pd600T2Case`). Sin valores del host.

## Mapa test → B/PD

| Test | Bloqueante / PD | Aserción central |
|---|---|---|
| `test_b1_medium_cota_slow_preflight_hangs_adapter_envelope_with_session` | **B1 / PD-11 / D-3 / §2.5** | cota 10 s, preflight `/api/info` retardado 4 s (> 25 % de B ≈ 8,8), cliente colgado → envelope del ADAPTADOR (`timeout` + sesión elegida) dentro de la cota; jamás `did not answer within` |
| `test_b2_prior_attempt_unaffirmable_store_blocks_before_dispatch` | **B2 / PD-9 / INV-9 / INV-10 / §2.7** | registro previo del mismo paquete con sesión, fila innegociable (escritor del fixture con `BEGIN EXCLUSIVE` persistente, precondición probe verificada) → `blocked` antes del despacho, sin `run`, diagnóstico «no se puede afirmar … intento previo»; la fila previa es IDLE: legible ⇒ no bloquearía (anti-GREEN-vacuo) |
| `test_b3a_service_mode_row_not_idle_times_out_at_cota_ignoring_settle` | **B3 / PD-7 (dif. enmienda) / §2.4** | modo `service` (URL + versión compatible), fila no idle, settle 0,3 s → `timeout` al vencer la cota (2 s), settle ignorado, sin recibo, PD-8 sesión |
| `test_b3b_service_preflight_bounded_responds_within_cota` | **B3 / PD-11 (dif. enmienda)** | preflight de servicio retardado 1,2 s acotado por presupuesto restante → `completed` dentro de la cota (10 s), envelope del adaptador, `service status` exactamente una vez |

## Comandos y salidas

```
$ timeout 280 python3 -m pytest tests/test_006_001_reviewfix.py -q
```
- **B1 (RED, AssertionError del contrato):** el envelope proviene de la INTERFAZ — `AssertionError: 'did not answer within' unexpectedly found in "destination 'opencode' did not answer within 10.0 seconds"`. El adaptador, con el piso proporcional sin tope (`E=4 s + 0,75·B ≈ 6,6 s + g=0,2 > 10 s`), no respondió a tiempo; `session` quedó `null` (correlación PD-8 perdida). Cierre en la primera corrida (orden original): `AssertionError: None != 'ses_b3d7501a10124b75a14852b4da2234bc'`. El retardo del preflight se verificó como precondición (`served_after ≥ 4 s`, exactamente 1 request).
- **B2 (RED, AssertionError del contrato):** `AssertionError: 'completed' != 'blocked'` — el chequeo de intento previo falló ABIERTO ante el store bloqueado: despachó (`run` invocado, `completed`, diagnosis `None`). Exactamente el doble-escritor que INV-10 prohíbe.
- **B3a, B3b: PASAN hoy** — declarado como **cobertura** (no son falsos verdes: las aserciones pinchan cláusulas nombradas por la enmienda; la review ya documentó que la implementación comparte la rama `!standalone` y acota el preflight por `min(...)`). Un refactor `!= "standalone"` → `== "server"` dejaría B3a en rojo.
- Totales finales: `2 failed, 2 passed in 19.99s` (focal completo ≈ 20 s < 60 s exigidos).

## Commit

```
$ git commit -m "test: 006-001 review-fix RED B1-B3 (cota media con preflight lento y cliente colgado; intento previo innegociable ante store busy; espera y preflight en modo servicio)"
[main 17a7ca1] ... 1 file changed, 807 insertions(+)
$ git status --short   # vacío tras el commit
```
Commit **`17a7ca1`**, solo `tests/test_006_001_reviewfix.py`, sin `--no-verify`, sin stash, sin push.

## Declaraciones honestas (PD-15)

- B1 es sensible al overhead de arranque en la banda de margen (≈1 s de reserva); bajo carga fuerte del host el camino CORRECTO podría avizinar la cota — deuda de fragilidad de cotas ya registrada en el epic; si ocurriera, se reporta como fallo de margen, no se debilita la aserción.
- La suite completa no se corrió (policy del packet: la corre quien cierra).
- No se leyó implementación; los mecanismos RED de B1/B2 provienen del análisis de la review formal, no del código.
