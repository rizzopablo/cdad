# Progreso de 017-001-suite-performance

Registro operativo del avance por tareas. El plan aprobado (`plan.md`, SHA-256
`781dd61ca268f36979778d34a2083432c05c279f2862acb31e21a1bc3a890ca1`) queda
intacto como documento aprobado: este archivo registra el estado de ejecución de
sus tareas sin alterar su digest.

## Contrato aprobado

- Gate de Specification registrado el 2026-11-07 (`transition_key`
  `d4c7eadc5f9f6b1a1cf514105a7b9e4a467aca50fe3ad05b85ffbcc78071d0ae`).
- Aprobado por <owner> mediante la delegación HITL del 2026-11-07 («eres el dueño
  del proceso»); el orquestador ejerció la aprobación en su nombre.
- Spec fijada: `docs/specs/017-001-suite-performance/spec.md`, SHA-256
  `472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e`
  (el banner interno «Borrador v3. No aprobado» quedó del borrador; la
  aprobación vive en el gate y en `docs/.cdad-state.json`, y no se editó la spec
  para no romper el digest fijado).

## T1 — XML y fases sin cambiar el cierre · HECHA (2026-11-07)

- Implementación: commits `b3c9770e` (artefactos), `7b0b0b32` (H1–H3 del primer
  review), `869b2825` (rama skip), `32904c2a` (regla general por resultado de
  setup).
- Tests: `tests/test_017_001_suite_profile.py`, 17 nodeids (9 tests + 8 casos
  parametrizados de la matriz de fases), todos verdes.
- Regresión proporcional: 49 passed (`test_008_002_suite_evidence`,
  `test_008_002_suite_selection`, `test_008_005_ci_gate`).
- `python3 scripts/cdad-suite.py validate`: rc 0, 0 nodeids sin capacidad.
- Revisiones: `review-T1.md` (3 bloqueantes), `review-T1-002.md` (1),
  `review-T1-003.md` (1), `review-T1-004.md` (aprobado, sin bloqueantes).
- Inventario vivo: `suite-inventory.json` con el módulo nuevo (17 nodeids) y
  `live-inventory-delta-T1.md` con el detalle de altas.
- Desviación registrada: el implementer del fix `32904c2a` dejó el cambio sin
  commitear; el orquestador lo commiteó con el mensaje que lo atribuye.

## T2 — Operaciones comprometidas y calibración previa · ABIERTA

Hecho:

- Mapeo del arquitecto (`operation-scope-mapping.md`) y registro
  `performance/operation-scope.json` (9 familias, 9 selecciones).
- Costura de marcas bajo `tests/` (`suite_operation_markers.py`) y oráculo de
  transporte/contexto/anidamiento/captura faltante
  (`tests/test_017_001_suite_operations.py`, 4 pruebas, verdes).
- Consumo en el observador y el runner (commit `613b3722`): sumidero de marcas,
  `operations`, `operation_errors`, `operation_scope` con path/sha256/status y
  `--operation-scope` con default al repositorio del CLI.
- `review-T2.md` encontró dos bloqueantes.

Hecho además:

- Marcas reales en las fronteras del mapeo (conftest, product_staging, 007_002,
  007_003, U1, U3, U4 y documental), sin cambiar aserciones.
- Diagnóstico por selección de operación (P5) y captura en el layout ambiguo
  bare/paquete (P6), que la calibración real destapó.
- Calibración de seis selecciones (`C-R`, `C-E`, `C-U1`, `C-U3`, `C-U4`, `C-D`):
  todas completas, con conteos esperados coincidentes, anidamiento correcto y
  cero errores de operación. `performance/calibration.md` con el contraste.
- Corrección de entorno: `_temp_root` exige writability (fallo preexistente que
  bloqueaba U3 y documental).

Cierre de T2 (2026-11-07): aprobada por `review-T2-004`. Se agregaron los
verificadores C-P (fría y manifiesto presente), el helper pasó a sumideros
múltiples (P7) y el registro quedó `calibrated: true` con la atribución de
volumen por selección corregida.

**T3 cerrada** (2026-11-07): aprobada por `review-T3-003` tras tres rondas
(vinculación selección↔intento, resolución de 1 s del reloj exterior y rechazo
de selección ausente o irresoluble). `reconcile` y `entry-check` implementados y
probados (12 tests); la condición de entrada a la base queda **satisfecha** con
las ocho selecciones calibradas.

**T4 con base medida** (2026-11-07): corrida completa instrumentada
`7426438b`, 4994.27 s (83.2 min), 2029 passed / 0 failed / 5 skipped,
3097 operaciones capturadas. Preparación medida 186.2 s (3.73 %). El 96.27 %
restante es **resto no desglosado (desconocido)**: no se clasifica por
complemento ni se atribuye a trabajo propio de los tests (§4.4). Contraste de alcance completo
incorporado (`all-selection`): sin faltantes; `product.copy`/`product.generate`
no ejercitadas por la rama de manifiesto presente, declaradas de antemano.
Artefactos: `performance/baseline.json`, `performance/baseline.md`.
Primer intento descartado por 7 fallos ambientales (temporal de host).

**T4 cerrada** (2026-11-07): aprobada por `review-T4-002` tras dos bloqueantes
reales (el resto se presentaba como trabajo contractual por descarte, prohibido
por §4.4; y la identidad contable no cerraba por precision del agregador). El
agregador publica ahora totales de corrida desde valores sin redondear y la
cota de redondeo. Falta fijar el objetivo de reduccion con el dueño (decision
reservada) antes de T5.

**T4B — medición adicional del resto** (2026-11-07, decisión del dueño «medir
el resto primero»): los seis archivos más caros (57 tests, 22.5 % del suite) se
instrumentaron con marcas `external.*` y se midieron. Resultado: 837.2 s de
fases, de los cuales **626.6 s (75 %) son proceso externo** — 76 ejecuciones de
`install.sh` (493.5 s), 301 invocaciones de CLI (118.2 s) y 2 del validador —
y 210.6 s in-process. El único archivo in-process es
`test_010_002_documentary_role_properties.py` (93 %). Informe:
`performance/remainder-measurement.md`. La muestra no se extrapola al 78 %
restante del suite.

Después: T3 (agregación sin doble conteo y condición de entrada), T4 (línea base
completa instrumentada), T5 (optimización serial), T6 (decisión de paralelismo),
T7 (corrida final y conciliación).


## Deuda registrada

- `docs/systemPatterns.md`: la tabla de decisiones no incluye ADR-037..ADR-042.
  Es preexistente y ajena a T1; se resolverá en el cierre del epic.

## T2 — mapeo recibido (2026-11-07)

- `operation-scope-mapping.md`: mapeo del arquitecto con fronteras archivo:linea,
  clasificacion por proposito, familias obligatorias de spec §4.2, seleccion
  focal por intervalo comprometido y los desconocidos con su regla de decision.
- `performance/operation-scope.json`: registro previo materializado desde el
  borrador del mapeo (9 familias, 9 selecciones; `calibrated: false`).
- Volumen medido del `.cdad` actual: 19.141 archivos regulares, 386.679.228
  bytes y 49 symlinks (dentro, `evidence` 4.877 archivos/148 MB y `local` 4.258
  archivos/162 MB). Es volumen de entrada, no tiempo de copia.
- Esperas deliberadas: familia declarada desconocida con regla de decision; no se
  compromete un intervalo de espera pura sin una observacion multiproceso
  calibrada.
- Siguiente: costura de marcas bajo `tests/` y oraculo de transporte/contexto/
  anidamiento; luego consumo en el observador y calibracion focal.

**Auditoría de instalaciones (2026-11-07, pedido del dueño):** de las 76
ejecuciones de `install.sh` medidas, **0 son preparación pura compartible**;
47 son acción bajo prueba y 29 mixtas (también evaluadas). Cachear cualquiera
dejaría sin ejecutar una transición verificada. Informe:
`installer-calls-audit.md`. Queda demostrado que el costo externo medido no es
duplicación eliminable; el techo serial no incluye esas ejecuciones.

**T6 en corrección** (2026-11-08): `review-T6` bloqueó el lote con cinco
defectos reales —worker sin archivos lanzaba pytest sin selección, paredes por
worker medidas en `wait()` secuencial, `orphans: 0` fijo sin limpieza en fallo
parcial, inventario y canario del checkout ausentes, y costo de preparación
atribuido por resta—. Se escribieron cinco protecciones nuevas (RED) y el
implementer las corrigió en `scripts/cdad-suite.py` (verde 11/11, focales y
regresión 59 passed, `validate` rc=0). El inventario de consumidores de puertos
y la copia de evidencia al repo quedaron registrados por el orquestador.
Pendiente: remedición serial/paralela sobre la misma revisión y re-review.
Contrato de la corrida final: `t7-final-run-contract.md`.

**T6 cerrada — gate superado** (2026-11-08, `review-T6-005.md`). Los dos
bloqueantes de `review-T6-003` cierran con sondas ejecutadas por el revisor
mismo: un descendiente que hace `setsid` se detecta (subreaper + cadena de
PPID), se limpia y descarta el lote (`rc 3`, `orphans_found 1`, `remaining 0`,
cero procesos vivos); un hijo transitorio dentro de la ventana de gracia de 5 s
no descarta (`rc 0`, `accepted`, `orphans_found 1`, `orphans 0`); y la huella
del checkout por contenido detecta la reescritura de igual tamaño y `mtime`
(`rejected`, `unchanged false`), validada sobre la evidencia cruda de la sonda
del orquestador. El revisor contrastó además las cifras de la muestra
(873.0 s → 546.36 s, 37.4 %, paredes 546.4/493.8, 57/57 idénticos por nodeid),
re-ejecutó 107 tests (oráculo T6 + focales T1–T4 + regresión, rc 0) y `validate`
(2054 nodeids, `status: ok`), y confirmó que `cmd_close` no cambió por
comparación AST. `--workers 2` queda acreditado para **intentar** la corrida
final bajo las garantías registradas; T7 debe demostrar el ≥15 % y la
equivalencia exacta sobre `--all` en una única revisión.

**T7, primer intento — descartado por el canario** (2026-11-08). La corrida
completa `--all` sobre `1cc39d3e` dio 2049 passed + 5 skipped en ambos
regímenes (serial 4354 s, paralela 2828.2 s), pero el lote paralelo salió
`rejected: canary detected changes`. Causa raíz reproducida con un solo archivo
(`test_010_004_t5_e2e.py`, 30 s): la huella de contenido, el conteo de archivos
y los bytes totales quedan **idénticos**; sólo cambia `max_mtime_ns` porque el
scratch declarado bajo `.cdad/tmp` mueve el mtime de los directorios. El
veredicto compara `max_mtime_ns` pese a que la función lo documenta como
información y no como huella. Corrección pendiente (RED/GREEN) antes de repetir
el par completo; la corrida descartada no se usa como evidencia.

**T7, par de `83674246` — HISTÓRICO, SUPERADO** (2026-11-08). No es evidencia:
se midió con un runner anterior a las correcciones *fail-closed*. Corrida final
`--all` sobre `83674246`, misma revisión en ambas pasadas y árbol limpio:
serial 4235 s (2050 passed + 5 skipped) y paralela 2925.34 s (idénticos),
reducción observada 30.92 % y equivalencia exacta por nodeid (2055 nodeids,
0 diferencias). Cifras conservadas solo como historia del diagnóstico. `reconcile`: preparación 445.64 s (10.5 %),
resto 3779.79 s publicado como desconocido, `R_pytest` 7.54 s y cota de
redondeo 1.03 s. Canario de configuración y del checkout limpios; 0 huérfanos
con 20 transitorios gestionados; preparación duplicada 23.28 s informada
aparte. Sus crudos están en `evidence/017-001-final3/{serial,parallel}` y su
detalle histórico en la sección «Corrida final anterior» de
`performance/parallelism.md`; **no** en `comparison.json` ni en
`.cdad/tmp/017-001-final-evidence/`, que contienen el par vigente.

**Review final, unidad 2 (producto) — cuatro bloqueantes** (2026-11-08,
`review-final-product.md`). Los cuatro son de integridad del veredicto, no de
rendimiento: (1) si falla la activación del subreaper o el barrido de `/proc`
no está disponible, el lote puede salir `accepted` sin acreditar la familia de
procesos; (2) el canario final se toma **antes** del barrido y la limpieza de
la familia, así que un descendiente residual puede escribir en el checkout
después de la fotografía; (3) un error de lectura se sustituye por el literal
`unreadable`, tratándolo como contenido estable, y un directorio inaccesible se
omite en silencio; (4) `parallel` acepta un directorio de evidencia ya poblado
(`exist_ok=True`), de modo que un fallo temprano podría leer XML o perfiles de
la corrida anterior. Corrección pendiente antes de aceptar; el par histórico de
`83674246` queda **no aceptado** hasta entonces.

**Los cuatro bloqueantes de integridad cierran** (2026-11-08,
`review-final-product-002.md`), verificados con sondas independientes del
revisor: con `CDAD_SUITE_FAULT=no-subreaper` y `no-sweep` el lote sale `rc 3`
con `family_verifiable: false`; un hijo que escribe en `build/` después de que
su worker termina y muere en la gracia hace que el canario posterior descarte
(`rejected`, `unchanged: false`); un subdirectorio ilegible produce `rejected`
con `checkout_canary.incomplete` nombrando la ruta; y una segunda invocación
sobre evidencia poblada sale `rc 2` con motivo, sin reportar los tests del
intento anterior. Focal del oráculo: 22 passed; `validate` ok (2059 nodeids).
El runner cambió respecto del par histórico de `83674246`, así que el par T7 se
repite sobre la revisión corregida.

**T7 definitiva** (2026-11-08, revisión `bf0e7483`). Con el runner ya
*fail-closed*: serial 4459 s y paralela 2593.15 s, **reducción 41.84 %**,
2054 passed + 5 skipped idénticos y 2059 nodeids sin una sola diferencia.
`reconcile`: preparación 448.90 s (10.1 %) y resto 4002.51 s publicado como
desconocido. `family_verifiable: true`, 0 huérfanos con 20 transitorios,
canario del checkout limpio con `incomplete: []` y preparación duplicada
16.34 s informada aparte. El par de `83674246` queda superado y no se usa.
