# Discovery — 011-begin-unpublished-packet-wedge

Borrador del architect (etapa 1); no es spec ni aprobacion. Codigo inspeccionado: `5141f86d`.
Origen: reporte de defecto 2026-10-31 (orquestador de otro proyecto). Rutas relativas a `skills/cdad-cycle/scripts/`; `C`=cdad_continuity.py, `P`=cdad_packet.py, `L`=cdad_lifecycle.py, `R`=cdad_result.py.

## 1. Diagnostico verificado

- `_admit_packet` devuelve `None` si no hay REQUEST ni rastro de publicacion (`C:1228-1259`); el llamador tiene contexto y unidad acreditada pero no los usa para discriminar (`C:1054-1055`, `1113-1118`).
- Un 2do begin divergente de la misma clave se rechaza solo si esa clave es la de la cabeza (`C:1090-1106`; `L:433-460`). Con otro begin intermedio se publica.
- Replay exacto: exito sin mover la cabeza (`C:967-980`, `1101-1104`); no restablece un begin vigente.
- `_detect_split_brain` cuenta todos los cuerpos no-checkpoint/no-reanchor por clave aunque esten enlazados en la cadena (`C:2297-2343`); bloquea `verify-begin`, registro de despacho y withdraw (`C:1380`; `P:4266-4272`, `7622-7627`).
- `reanchor` rechaza cadena demostrable (`C:2136-2139`). `suspend-unit` exige recibo durable para RESULT staged (`P:1030-1040`).

### Correcciones al reporte
1. Antes de crear el duplicado existe salida: emitir el begin legitimo con **attempt nuevo** (reproducido `A/1 -> inexistente/1 -> A/2 -> verify-begin A/2` ok). No recupera despues del duplicado.
2. `receive` no falla universalmente por split-brain: con paquete `prepared` falla por falta de despacho (`R:701-706`); con despacho admisible publico recibo y cierre pese a los dos begins (cierre usa su propia prueba de cadena, `C:1633-1655`, `1733-1768`).
3. Hallazgo nuevo: `begin -> suspend-unit -> resume-unit -> begin divergente` (mismo attempt) tambien produce split-brain; la escritura esta permitida por la excepcion de reanudacion (`L:421-450`).
4. Hallazgo menor confirmado: un salto de linea en el contrato hace fallar `receive` por SHA exacto (`P:1919-1921`; `R:674`). Integridad por bytes, no semantica.

## 2. Evidencia
Python 3.13.5, proyectos sinteticos (`_Project`, `tests/test_007_003_continuity_at_edges.py:490-524`), HOME/XDG temporales. Secuencia: begin A/1 ok; begin inexistente/1 ok; replay A/1 no-op; begin A/1 distinto ok; verify-begin rc1 split-brain; despacho/withdraw rc2; reanchor rc1; suspension con RESULT staged rc2. Regresion focal: 29 passed (cinco archivos). Suite completa no ejecutada.

## 3. Discriminador de ejecucion CDAD v2
`schema_version == 2` del documento de ejecucion (`P:2996-3015`, validado en `P:1303-1344`); continuidad lo conserva (`C:359-379`, `3087-3131`) pero no valida el esquema v2 completo. No sirven `execution_id`, version del state/checkpoint ni existencia de `.cdad/` (tambien aparecen en legacy; `tests/test_003_004_t1_checkpoint.py:114-125`).

## 4. Cobertura existente y huecos
Cubierto: sin REQUEST con rastro (`tests/test_008_004_packet_enforcement.py:692`), legacy sin arbol (`:718`), divergente contra cabeza (`test_003_004_t2_writeahead.py:326`, `test_003_007_t2_checkpoint_vs_begin.py:575`), split-brain/checkpoint legitimo (`test_003_004_t2_reconcile.py:545`, `test_003_007_t2_checkpoint_vs_begin.py:731,777`), withdraw con continuidad invalida (`test_007_006_withdraw_and_republish.py:1195`).
Huecos: begin sin rastro en ejecucion v2; 2do begin con clave en ancestro (no cabeza); interaccion con reanudacion.

## 5. Alcance propuesto
- **Nucleo (011):** rechazar un begin NUEVO en ejecucion v2 sin REQUEST publicado, antes de escribir cuerpo/cabeza, con diagnostico accionable (preparar/verificar el paquete). Conservar replay, admision existente y legacy. Aceptacion: rechazo sin efectos; begin legitimo acreditable despues; legacy intacto. **No repara ejecuciones ya bloqueadas.**
- **Aparte (seguimiento):** arreglo 2 (unicidad de begin por clave; resolver antes la excepcion de reanudacion), 3-4 (recuperacion: autoridad, conservacion de evidencia, efectos staged), 5 (diagnostico de reanchor, parte de 3-4), hash editorial (deuda diagnostica, sin relajar integridad).

## 6. Decisiones para el dueno
1. Aprobar el alcance preventivo (arreglo 1) sin reparar ejecuciones ya bloqueadas.
2. Para el seguimiento 2: tras reanudar, ¿otro attempt obligatorio, o varios begins enlazados bajo la misma clave?
