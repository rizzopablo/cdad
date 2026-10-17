Empiezo el packet test-writer-red-004 (substage RED). Primero leo el contrato aprobado y el plan (ficha T3), dentro del read scope declarado.
Continúo el packet. Ya tengo spec y plan (ficha T3). Ahora leo los tests existentes para reutilizar convenciones y los helpers de integración (líneas 169-342 de test_005_010_t4_integration.py).
Ahora estudio las convenciones del fixture: `AdapterCase` en test_005_009_t2_opencode_adapter.py y los fakes propios de T1b y T2.
Ahora leo la jerarquía de fixtures de T1b (fake propio) y las partes clave del fixture base.
Ahora leo el fixture base de T1 (Pd600T1Case): dispatch, fake_runtime, exec-config y FakeInfoServer.
Necesito entender `AdapterCase` y su setUp para poder construir DOS proyectos descartables en un mismo test. Leo el fixture base.
Necesito ver el fake binario compartido (cómo escribe el store) y el `DelegateCase` base.
Leo las piezas que me faltan: `DelegateCase` (staged_interface, envelope), el esquema del store del fake compartido y el conftest.
Diseño listo. Antes de escribir, verifico empíricamente cómo pytest colecciona clasesTestCase auxiliares (necesito instanciar un segundo proyecto dentro de un test) y confirmo firmas de helpers.
Collection: solo se coleccionan clases `Test*` propias del módulo (16 y 8 items) — las clases auxiliares no se duplican. Verifico un último detalle del fixture y escribo los dos archivos.
Escribo el focal T3 con su fake propio.
Corrijo problemas de diseño en el archivo (helpers con firma inconsistente, variables muertas).
Compila y colecciona exactamente los 2 tests del focal. Corro el focal (primera corrida, con timing).
Falta `import os`. Lo agrego y vuelvo a correr.
Dos arreglos: el fake debe escribir la sesión elegida por el adaptador (`--session`), y los tests deben convertir `CompletedProcess` → envelope con `project.envelope()`.
Dos puntos: el fake no registra las invocaciones `service status` (falta `_append_call` en esa rama) y mi expectativa del par `session=` en `provenance.session` no coincide con la forma real. Verifico cómo assertiona T1 la procedencia de sesión.
Confirmado: `provenance.session` no lleva par `session=` (la correlación va por el envelope, PD-8) y `store_reads` admite entero o `unknown` (INV-9). Ajusto el oráculo a la forma de §2.6 y hago que el fake registre `service status`.
El focal pasa (4.65 s ≤ 30 s) — como anticipé, pasa hoy por el GREEN previo de T1/T1b/T2. Para probar que el oráculo es sensible (falsificable) sin tocar implementación, hago una mutación TEMPORAL de mi propio fake (correlación rota + flag prohibido), corro, y restauro.
La mutación demuestra que el oráculo falla por AssertionError de contrato (correlación rota → fila durable ausente → `unknown != completed`). Restauro el original y confirmo verde.
Focal listo y estable. Ahora escribo el test de integración con opt-in (reutilizando los helpers de `test_005_010_t4_integration.py:169-342` vía herencia de `TestPd8RealOpenCodeIntegration`).
3 skips en vez de 1 — algo extra se está coleccionando (probablemente el test heredado `test_pd8` de la clase base). Verifico.
Causa clara: la clase base importada (`TestPd8RealOpenCodeIntegration`) se colecciona en mi módulo y mi subclase hereda su método `test_pd8`. Lo arreglo con alias de importación + enmascarado local del método heredado.
La clase TestCase se colecciona sin importar el nombre; la solución es importar el módulo y usar una base intermedia sin métodos de test (misma convención que las bases del resto de la suite).
Ahora colecciona exactamente 1 y se omite por defecto. Verifico que el motivo del skip nombre la variable de control, y hago una verificación estática del camino opt-in (sin despachar) para validar que el entorno requerido también se comporta como skip nombrando cada variable.
El skip por defecto es correcto. Reintento la verificación estática con sys.path explícito.
El camino opt-in omite correctamente en cada variable faltante. Ahora corro las regresiones declaradas del packet (mis archivos solo se suman, pero importan módulos de esos focales).
Regresiones verdes (53 passed, 1 skipped — el skip preexistente es el test opt-in de 005-009 T4). Corro la evidencia final de los dos archivos T3 juntos y commiteo solo `tests/`.
# Reporte del rol — test-writer RED T3 (packet 006-001-opencode-concurrency-reliability-test-writer-red-004)

## Archivos modificados (write scope: `tests/` únicamente)

| Archivo | Contenido |
|---|---|
| `tests/test_006_001_t3_concurrency.py` (nuevo) | Focal T3 con **fake propio** (`T3_FAKE_BINARY_SOURCE`, plan §3 oráculo 4): dos proyectos descartables por test (maquinaria de fixture instanciada dos veces, sin tocar los focales de T1/T1b/T2) despachando **en paralelo** contra el **mismo store** SQLite (INSERT transaccional real, escrituras concurrentes serializadas por SQLite) y el **mismo servidor de fixture** `/api/info` en loopback/puerto libre. Variantes modo `server` y modo `service` (fake de `service status` + registro D-11 compatible). Esperas chicas (`timeout 4 s` + `FAST_WAIT`): focal entero **4.46–4.75 s** (≤ 30 s). |
| `tests/test_006_001_t3_integration.py` (nuevo) | Recorrido **REAL** con opt-in por entorno (spec §5): omitido por defecto; reutiliza los helpers de `test_005_010_t4_integration.py:169-342` por herencia (base intermedia `_T3RealFixtureBase` que enmascara el test de esa ficha para no coleccionarlo dos veces). Servidor real descartable en loopback (lo lanza/detiene el test: SIGTERM→SIGKILL al grupo), contraseña aleatoria, XDG bajo `<ROOT>`, **guarda `debug paths`** que falla **sin despachar** si `db`/`data`/`state`/`log` no quedan bajo `<ROOT>`, credencial por `{env:<VAR>}` (el test nunca lee el valor), dos delegaciones concurrentes + complemento standalone; observaciones VERIFY por stdout (`T3-VERIFY-OBSERVATIONS`). Nunca arranca, reinicia ni reconfigura el servicio del host. |

## Mapa test → PD

| Test | PD / INV / D |
|---|---|
| `test_pd6_two_concurrent_server_mode_dispatches_complete_without_cross_correlation` | **PD-6** (pierna (a) fixture, topología servidor): 2×`completed`, sesión propia y distinta por proyecto, `session_v2.directory` = su proyecto, nonce propio solo en sus resultados (entrega, fila durable, archivos cambiados dentro de `.cdad/` y `docs/.cdad-state.json`), adaptador sin escrituras al store (hash final ∈ estados post-commit del fake), procedencia **por intento** (§2.6 con `store_reads`/`prior_check_reads` enteros), recibo `pending` (INV-5); **INV-6** (URL solo en argv de `run --server`); **INV-2**; **D-7/D-8** |
| `test_pd6_two_concurrent_service_mode_dispatches_complete_without_cross_correlation` | **PD-6** (enmienda: modo `service`, despacho **sin flags**): ídem + argv sin `--server`/`--standalone`, `service status` exactamente 1× por despacho, `mode_requested=service; mode_effective=service; dispatch_flags=none; service_status=running; fallback=none`, `server_version` del registro D-11; **INV-2/INV-10** (sin `serve`/`reload`/gestión); **INV-6** (contraseña centinela y URL del servicio fuera de todas las salidas) |
| `test_pd6_real_server_two_concurrent_and_standalone_complement` | **PD-6 pierna (b)** + **D-8**: recorrido real (la corre el orquestador; una omisión por falta de credencial queda como skip con motivo → **BLOQUEO declarado**, no es un pase) |

## Comandos y salidas (líneas finales)

```
python3 -m pytest tests/test_006_001_t3_concurrency.py -q -p no:cacheprovider
  → 2 passed in 4.46s        (focal, tras iteración de fixture)

# Sensibilidad del oráculo (mutación TEMPORAL de mi propio fake, revertida, no commiteada):
# correlación rota (fake ignora --session) →
  → AssertionError: 'unknown' != 'completed' : PD-6: la delegación concurrente no terminó completed
# (fallo por aserción de contrato, no import/sintaxis/fixture)

python3 -m pytest tests/test_006_001_t3_integration.py -q -p no:cacheprovider -rs
  → 1 skipped in 0.06s
  → SKIPPED [1]: "PD-6 pierna (b) omitida por defecto: el recorrido REAL en modo servidor
     se habilita con CDAD_OPENCODE_INTEGRATION=1 ... la omisión NO es un pase: PD-6 queda
     en BLOQUEO declarado."

# Validación estática del camino opt-in (sin despachar): cada variable faltante omite
# nombrándola; KEY_ENV con nombre que apunta a variable indefinida → omisión con motivo.
# También: guarda debug paths falla SIN DESPACHAR si db/state/log no caen bajo <ROOT>
# (verificada por construcción de la aserción, requiere opt-in real para ejecutarse).

python3 -m pytest tests/test_006_001_t3_concurrency.py tests/test_006_001_t3_integration.py -q -p no:cacheprovider -rs
  → 2 passed, 1 skipped in 4.75s

# Regresiones declaradas del packet:
python3 -m pytest tests/test_005_010_t3_references.py tests/test_006_001_t1_selection.py \
  tests/test_006_001_t1b_service_mode.py tests/test_006_001_t2_wait_recovery.py \
  tests/test_005_009_t4_acceptance.py -q -p no:cacheprovider
  → 53 passed, 1 skipped in 82.52s   (el skip es el opt-in preexistente de 005-009 T4)
```

## Commit

```
5e5828a test: 006-001 T3 RED concurrencia con fixture (PD-6, fake propio, dos proyectos
         vs mismo store/servidor, server y service) y recorrido real opt-in por entorno (spec 5)
2 files changed, 1438 insertions(+)
```
Sin `--no-verify`, sin stash, sin push; `git status` limpio tras el commit (solo `tests/`).

## Declaraciones honestas

1. **Los dos tests focales PASAN hoy por el GREEN previo (T1/T1b/T2, `ddba831`)** — declarado con la PD que cubre cada uno (el packet lo prevé). El RED de T3 entrega el **oráculo**: se demostró que falla por **AssertionError de contrato** cuando el comportamiento concurrente se rompe (mutación temporal del fake propio: correlación rota → `'unknown' != 'completed'`), y que detectaría cruces de nonce, escrituras del adaptador al store, flags prohibidos y gestión del servicio por las aserciones correspondientes. La mutación se revertió; lo commiteado es el original verde.
2. **No leí implementación** (skills/, scripts/, agents/, sources/, build/, install.sh). Solo leí spec/plan (contrato) y `tests/`. Los fixtures copian el árbol canónico sin inspección, mecanismo estándar de la suite.
3. **PD-12** (config de ejemplo) no lleva test aquí: su verificación es del implementer/review (leer el asset sería leer implementación); queda para el gate de cierre (`make validate`, recorrido real, suite completa por quien cierra).
4. El recorrido real en modo **servicio contra el servicio VIVO** (spec §5.5, pierna (c) de PD-6) no se ejecuta aquí por diseño: lo corre el orquestador o el dueño aparte.
