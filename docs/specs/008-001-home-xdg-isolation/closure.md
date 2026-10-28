# Cierre 008-001-home-xdg-isolation

Fecha: 2026-10-27. Epic: `epic-008-suite-coherence`. Feature 1 de 5.

## Resultado

Cada test de la suite corre con HOME, XDG y temporales propios; sus subprocess heredan ese entorno;
y el producto resuelve el origen de agentes con el HOME vigente, no con el capturado al importar. La
suite deja de depender de la configuración personal del operador.

El gate de estabilidad, además, expuso y dejó corregidos **dos defectos reales de la cota de
despacho** que producían timeouts falsos bajo carga: el wrapper mataba al adaptador justo en la cota
que el adaptador administra (PC-7), y el adaptador despachaba con `0.0s` de espera cuando el preflight
consumía el presupuesto (PC-8). Ninguno de los dos era un problema de la suite: eran fallos del
producto que sólo se veían cuando la suite se volvió ejecutable en condiciones reales.

## Contrato

`docs/specs/008-001-home-xdg-isolation/spec.md`, PC-1..PC-6 y ajustes AJ1–AJ3, más PC-7 (AJ4) y
PC-8 (AJ5) agregadas el 2026-10-27 a partir del gate.

| PC | Qué acredita | Dónde |
|---|---|---|
| PC-1 | raíces exclusivas por test y herencia por subprocess (9 variables) | `tests/test_008_001_home_xdg_isolation.py` |
| PC-2 | resolución lazy del origen de agentes y precedencias por bytes | idem |
| PC-3 | configuración y stores con recursos sintéticos; aceptaciones reales siguen opt-in | idem |
| PC-4 | escrituras confinadas; canario sensible (control negativo en HOME sintético) | idem |
| PC-5 | restauración de entorno y `tempfile.tempdir`, incluso con fallo | idem |
| PC-6 | gate de tres corridas completas consecutivas | `.cdad/local/008-001/run-{1,2,3}.log` |
| PC-7 | el wrapper no preempta el sobre del adaptador (`cota + 5s`) | `tests/test_008_001_pc7_wrapper_margin.py` |
| PC-8a/8b | el adaptador no despacha sin presupuesto útil; agotamiento preparatorio declarado | `tests/test_008_001_pc8_adapter_budget.py` |

## Cambios

Producto:

- `skills/cdad-cycle/scripts/cdad_packet.py`: `Path.home()` deja de capturarse al importar; el
  fallback de agentes se resuelve en cada uso. Precedencia intacta (override → activación → HOME).
- `skills/cdad-cycle/scripts/cdad_delegate.py`: `ADAPTER_WAIT_GRACE_SECONDS = 5.0`; el wrapper espera
  al adaptador `cota + margen` y su diagnóstico nombra el límite efectivo. Sin cota declarada, sin
  límite (comportamiento previo).
- `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`: deadline **agregado** de preparación (no se
  renueva por operación), reserva del write-ahead, mínimo útil de espera proporcional
  `max(0.1, 0.2·budget)`, no despacho con agotamiento preparatorio (sobre `blocked`, `session=null`,
  sin `run`, sin recibo) y corrección de un `KeyError` latente en el corte de `mode: service`.

Tests e infraestructura:

- `tests/conftest.py`: fixture autouse por test (raíz propia, nueve variables, neutralización de los
  tres overrides heredados de AJ2, siembra de agentes canónicos, restauración de entorno y
  `tempfile.tempdir`) y fixture de sesión que aísla también `setUpClass` y fixtures de módulo, y fija
  el `basetemp` de pytest.
- `tests/product_staging.py` + 4 módulos: cachés de corrida fuera del `TMPDIR` por test.
- `tests/test_006_001_*`, `tests/test_006_003_u4`, `tests/test_006_003_u6`, `tests/test_006_005_u6fix5`,
  `tests/test_007_004`: cotas instrumentales de 2s a 5-10s **sólo** donde la cota no era el sujeto;
  los cuatro tests donde la cota **es** el sujeto conservan sus aserciones y ganan la rama honesta de
  agotamiento preparatorio. El fixture compartido `TEST_WAIT_TIMEOUT_SECONDS` sube de 2 a 5.
- `tests/test_005_009_t2`, `005-010`, `007-004` (cachés de corrida) y `test_006_003_u6` (credencial
  de servidor): adaptaciones sin cambios de aserciones.

## Evidencia

Secuencia RED→GREEN:

- RED del aislamiento: `6a116bf` (6 casos por contrato).
- GREEN/infra: `5016b73`, `63ffef7`, `82250ee`, `c32c22a`, `02d3f9e`, `9a7d268`.
- PC-7: `81e0903` (RED) → `c2004eb` (GREEN).
- PC-8: `49ce9ad` (RED) → `e9e27df` (GREEN) → `45d5d99` (mínimo proporcional) → `a519037`
  (oráculos estrictos y corte en service) → `23aa06f` y `e588b17` (cotas instrumentales y oráculo de
  `run` en 006-001/006-003).

Tests nuevos: 8 (aislamiento) + 3 (PC-7) + 6 (PC-8) + 2 (oráculo de `run`).

Review de etapa 4 (read-only, sesiones distintas de las que escribieron):

- Ronda 1 (estática): 2 bloqueantes **de evidencia** del gate (faltaba el canario sobre el HOME real
  y los motivos de los skips) y 1 vía de escape real (`setUpClass`/fixtures de módulo corrían antes del
  aislamiento). Cerrados en `gate.sh` y `9a7d268`; re-review sin bloqueantes.
- Ronda PC-8: sin bloqueantes; 2 IMPORTANT (piso de espera demasiado bajo y falta de caso service),
  cerrados en `45d5d99` y `a519037`.
- Ronda de cotas (`23aa06f`, `944b2ef`): sin bloqueantes; 1 IMPORTANT (oráculo de `run` débil) y 1
  MINOR (`test_006_003_u6` expuesto), cerrados en `e588b17`.

Gate PC-6 — tres corridas completas consecutivas sobre `944b2ef`, árbol limpio (`dirty=0`):

| Run | Resultado | Canario (`delta`) | Log |
|---|---|---|---|
| 1 | **1741 passed, 5 skipped**, rc=0, 45:19 | 0 | `.cdad/local/008-001/run-1.log` |
| 2 | **1741 passed, 5 skipped**, rc=0, 46:09 | 0 | `run-2.log` |
| 3 | **1741 passed, 5 skipped**, rc=0, 57:15 | 0 | `run-3.log` |

Mismos commit, orden, selección y aserciones en las tres. Los 5 skips conservan su motivo en el log
(`-rs`): dos de `test_005_002_t4_acceptance.py`, uno de `test_005_009_t4_acceptance.py`, uno de
`test_005_010_t4_integration.py` (PD-8) y uno de `test_006_001_t3_integration.py` (PD-6-b); todos son
aceptaciones/integraciones **reales** que exigen variables y credenciales del operador, opt-in por
diseño. Ningún skip sustituye un verde.

Canario del gate: inventario con `mtime_ns` de `~/.config/cdad`, `~/.config/opencode`,
`~/.local/state/cdad` y entradas de primer nivel del HOME, antes y después de cada corrida, sin seguir
symlinks. Delta 0 en las tres. Alcance y exclusiones declarados en el propio `gate.sh`.

## Historial del gate (intentos que no valen como secuencia)

La secuencia válida es la de arriba. Los intentos previos se reiniciaron, nunca se promediaron:

1. **Secuencia previa, run 1:** 1729 passed, 1 failed (`test_006_001_reviewfix.py` B1) — el wrapper
   mataba al adaptador en la cota. Causa de PC-7. Corregida y contrato ampliado (`6f5d594`, `c2004eb`).
2. **Secuencia previa, run 2:** 5 failed en `test_006_003_u4` y `test_006_005_u6fix5` — el adaptador
   respondía `blocked` por agotamiento preparatorio donde el test esperaba despacho: cotas de 2s sin
   presupuesto útil. Causa de PC-8 y del barrido de cotas (`23aa06f`, `944b2ef`).
3. **Secuencia anterior:** interrumpida al detectar que el gate no medía el canario ni los motivos de
   skips (bloqueantes B1/B2 de la review). Reiniciada con `gate.sh` corregido.

**Límite declarado:** `gate.sh` escribe nombres fijos (`run-N.log`), así que los logs de los intentos
fallidos fueron sobrescritos por el reinicio; se conservan sus causas (spec AJ4/AJ5, commits de
corrección) pero no sus archivos. Es un defecto de la herramienta de evidencia, no del producto; queda
como deuda para 008-002 (el gate debe preservar cada intento con nombre propio).

Corrida completa anterior al gate (`attempt-full-1.log`, 19 fallos) sirvió de línea base: los fallos
eran el HOME del operador sin agentes canónicos, corregido en `02d3f9e`.

## Límites declarados

- PC-4 acredita ausencia de **escrituras observadas** en un HOME externo sintético y en las rutas de
  producto del HOME real, y que el control negativo es sensible. **No observa lecturas** ni escrituras
  transitorias revertidas entre snapshots.
- El aislamiento por entorno **no es una sandbox**: rutas absolutas y entornos explícitos pueden
  escapar.
- El canario del gate cubre las rutas nombradas, no todo el HOME. Quedan excluidos
  `~/.local/share/opencode` y el repo, que el propio orquestador escribe en vivo.
- Tres corridas verdes son evidencia **acotada** de estabilidad, no prueba de ausencia universal de
  flakiness.
- Las aceptaciones contra store real siguen opt-in y omitidas por diseño.
- PC-7 y PC-8 corrigen los bordes de cota demostrados; no prometen que todo host cargado responda
  dentro de cualquier cota.

## Deuda observada (para el epic)

- **Techo de «no esperar de más»:** con el fixture en 5s, las aserciones que distinguen «hecho conocido»
  de «esperó la cota» toleran hasta 5s. Conviene un techo propio de 2s en 008-002.
- **Despachos de rol sin paquete:** sólo discovery y draft de architect se despacharon con paquete en
  esta unidad; las subfases de test-writer, implementer y reviewer se despacharon sin él. Es
  `DESPACHO-SIN-PAQUETE`, alcance de 008-004.
- `make validate` F011: preexistente, no relacionado.
- El gate de evidencia debe preservar intentos (ver «Historial»).

## Despliegue

Los tres archivos de producto (`cdad_packet.py`, `cdad_delegate.py`, `cdad_delegate_opencode.py`) se
despliegan en `~/.config/opencode/skills/cdad-cycle/scripts/` con respaldo previo y verificación de
que los agentes de rol conservan su `model:`.
