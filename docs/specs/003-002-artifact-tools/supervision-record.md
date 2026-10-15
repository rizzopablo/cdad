# Supervision record — 003-002-artifact-tools (PD-17)

Registro de supervisión por tarea: verificación del orquestador en límites de
tarea/subfase (ADR-011:104-116), reutilización de evidencia y desviaciones.

## T1 — `receive` atómico e idempotente (P1/P2/P3/P6 base) — cerrada 2026-10-05

- **(a) RED:** `02ebb0e` — `tests/test_003_002_t1_receive.py` (791 líneas, 7 tests).
  Primer despacho de 003-002 con la **versión adoptada** (CLI y agentes de proyecto
  desde la raíz aislada `8cb6580`). Re-verificado: 7 `AssertionError`, 0
  `ImportError`/`SyntaxError`.
- **(b) GREEN:** `3f619c4` — `cdad_result.py` canónico (586 líneas) + wrapper +
  3 esquemas. Reutiliza los validadores públicos de 001 sin redefinir esquemas v2.
  Focal 7/7 re-verificado; suite completa citada 371 passed.
  **Desviación:** el rol dejó el trabajo sin commitear atribuyéndolo a
  `contract.commit: null` (que significa "sin pin de commit", no "no commitear").
  Disposición: se reanudó la misma sesión y commiteó con pathspec (5 archivos, sin
  tests ni state). Lección: `contract.commit: null` es ambiguo para el rol.
- **(c) Review:** `review-t1.md` — **changes-required**: R1 (traversal real en
  `_verify_durable`: un recibo forjado con `name` de traversal lee fuera del project
  root), R2 (la batería focal que el plan T1 declara —interrupción y dos procesos—
  no existía en el RED), R3 (el scope-validation positivo in-scope nunca se
  ejercitaba). Los tres **re-verificados por el orquestador** contra el código y los
  tests antes del fix. R4/R5 opcionales; 6 nits.
- **(d) Review-fix RED:** `980940d` — R1 falla con `AssertionError` (RED no vacuo);
  6 locks (R2 kill/concurrencia, R3 in-scope+renamed, R5 validate-receipt ±) pasan
  con la implementación actual y **también** contra el código pre-fix → locks
  genuinos. La race se probó en vivo (5/5), disolviendo la abstención del reviewer.
- **(e) Review-fix GREEN:** `2106766` — el remedio prescrito, una línea
  (`_segment` sobre el name del recibo durable), cubriendo ambos call sites. Suite
  completa 378 passed. R4 diferido con justificación (rename de ~30 sitios en el
  `cdad_packet.py` compartido con 004-002 + cambio de tipo de excepción).
- **(f) Re-review focal:** `review-t1-rereview.md` — R1 **cerrado** y verificado
  **empíricamente** (el reviewer extrajo el script pre-fix a un espejo y reprodujo el
  RED, en vez de citarlo). Suite completa corrida por el reviewer (378). Sin
  bloqueantes activos.
- **(g) Cierre:** T1 cerrada. **Deuda:** R4 (fachada pública de `scope_contains` /
  `project_path`; T2/T3 consumen el mismo archivo), R5 parcial (el lock lo cubre),
  R6 (6 nits mecánicos), FYI de unicidad de `parts[].name` en recibos forjados.
- **(h) Consumo:** 5 despachos + 1 reanudación de sesión + 1 re-review; 1 iteración
  de review-fix; 2 corridas completas de suite (1 citada + 1 verificada por el
  reviewer) + 2 focales.

## T2 — `materialize` por política de artefactos (P4 + partes de P3/P6) — cerrada 2026-10-05

- **(a) RED:** `0494ab5` — `tests/test_003_002_t2_materialize.py` (897 líneas, 11 tests)
  con guard anti-RED-falsa en cada negativo. Re-verificado: 11 `AssertionError`.
- **(b) GREEN:** `db72fb4` — comando `materialize` (+275) + `artifact-policy.json` +
  `materialize.schema.json`. Focal 11/11; suite completa citada 389 passed.
- **(c) Review:** `review-t2.md` — **changes-required**: R1 (autoridad revocada no
  bloquea `materialize`; **reproducido** por el reviewer con el motor de fixtures),
  R2 (clave extra `test-writer-audit` en la tabla cerrada), R3 (`materialize` no
  consulta `receipt.role/substage`, pese a que §7 dice "un kind de otro rol falla"),
  R4 (el retry no observaba el journal real), R5 (filas de la matriz §7 sin
  cobertura). Los tres primeros **re-verificados por el orquestador** antes del fix.
- **(d) Review-fix RED:** `4250026` — R1/R2/R3 fallan; R4a/R4b/R5 locks.
  **DESVIACIÓN DETECTADA POR EL ORQUESTADOR:** el lock R4a era **flaky** (carrera
  SIGSTOP/SIGKILL; fallaba ~1 de cada 3 — el rol reportó 6/6 pero el re-run del
  orquestador dio 4/4/3/4 failed). Disposición: se reanudó al test-writer
  (`8333649`), que lo reemplazó por el mecanismo **determinista** que la spec §8
  autoriza (pending dir documentada), verificado 10/10 por el rol y 3/3 por el
  orquestador. **Lección: un lock flaky es peor que ninguno; el orquestador debe
  re-correr los locks, no aceptar el reporte del rol.**
- **(e) Review-fix GREEN:** `92b60cf` (+41/−1) — R1 lee el state y llama
  `validate_state` **antes de cualquier escritura**; R2 tabla con un único kind de
  auditoría; R3 `_allowed_kinds(role, substage)` cerrado. Suite completa 401 passed.
- **(f) Re-review focal:** `review-t2-rereview.md` — R1/R2/R3 **cerrados** (R1 con
  cierre empírico), 0 bloqueos nuevos, locks verdes.
- **(g) Cierre:** T2 cerrada. **Deuda:** O1 (target fijo no aplicado en las filas con
  nombre), O2 (journal indexado por string crudo), O3 (el esquema no se carga), FYI-1
  (rama v1-ordinary del validador), FYI-2 (nombre editorial en la spec de 003-001).
- **(h) Consumo:** 6 despachos + 1 reanudación; 1 iteración de review-fix; 2 corridas
  completas citadas (389, 401) + 3 focales re-corridos por el orquestador.

## T3 — evidencia de runner (P5, §8) — cerrada 2026-10-05

- **(a) RED:** `ed71c50` — 13 tests (P5 completo). Re-verificado: 13 `AssertionError`.
- **(b) GREEN:** `84e3366` — `run-python-unittest` + `validate-run-evidence` (+353) + 2
  esquemas. 12/13; la falla restante era un **defecto del test** (`append_to`
  inexistente), reportado por el implementer sin editar tests. Disposición: reanudado el
  test-writer (`27c2a39`), que agregó el helper y **re-verificó las 13 fallas RED una por
  una** contra el código pre-GREEN.
  **LECCIÓN DE VERIFICACIÓN (del orquestador):** contar «N failed» no alcanza; hay que
  revisar que **cada** falla sea por la razón esperada. Se aplicó en todas las
  verificaciones posteriores.
- **(c) Review:** `review-t3.md` — **changes-required**: R1 (el runner fija su propio
  alcance: Exp-A/C reproducidos), R2 (`validate` no re-deriva log/conteos/selections;
  Exp-B/D), R3 (descubrimiento por aproximación de `.gitignore`).
- **(d) Review-fix r1:** RED `e045fb4` (8 tests) → GREEN `81a585a`. R2 cerrado limpio;
  R1/R3 con **residuales** (F1 argv sin `discover`; F2 `ls-files` sin `-z`).
- **(e) Review-fix r2:** RED `feed7e1` (5 tests) → GREEN `32d290c`. F1/F2 cerrados; la
  sospecha de flakiness de `test_p5_failing_suite_not_valid_current` quedó **degradada a
  ruido** (40 corridas limpias, 25 aisladas + 15 bajo carga concurrente; mecanismo
  pyc/mtime refutado). **Persistieron 2 residuales** (R-F1a: opción antes del módulo;
  R-F1b: paquete de un segmento).
- **(f) INTERVENCIÓN DEL DUEÑO (calibración):** «el reviewer no debería ser infinitamente
  detallista… pero no debe perder el objetivo de usabilidad del sistema». Disposición del
  orquestador: **remedio de CLASE fail-closed en una ronda** (`5c76fee`: whitelist cerrada
  de opciones invariantes + única forma plenamente ligable + degradación por defecto a
  `unknown`), cerrando R-F1a/b/c **juntos** en vez de seguir enumerando variantes. La
  regla se escribió en el proyecto (`675c18e`: dueño canónico
  `references/stage-4-review.md` + referencia desde `sources/roles/reviewer.md`).
- **(g) Re-review final (calibrada):** `review-t3-rereview.md` — **CLOSED**: la clase
  cerrada (verificada por 2 vías), caso canónico intacto, usabilidad preservada, 69/69 y
  433/433 sin regresión. 0 bloqueantes.
- **(h) Cierre:** T3 cerrada. **Deuda:** whitelist más estricta de lo necesario
  (`--locals`, `-c`), doble motivo de diagnóstico, `_module_tree` sobre nombre imposible —
  todas opcionales, sin camino de falso verde. Más las deudas de O1–O3 de `review-t3.md`.
- **(i) Consumo:** 10 despachos + 2 reanudaciones + 1 unidad de calibración; 3 rondas de
  review-fix (la 3ª forzada por la instrucción de clase); 3 corridas completas citadas
  (401, 427, 433).

## T4 — integración (P6) — review final 2026-10-05

- **(a) RED:** `41b1663` — `tests/test_003_002_t4_integration.py` (768 líneas, 6 tests).
  El test-writer declaró **honestamente GUARDS RED**: 6/6 pasan hoy porque T1–T3 ya
  entregaron el producto. No fabricó ninguna falla. Re-verificado por el orquestador:
  6 passed / 31.94 s; el commit toca sólo el archivo de tests.
  **Lección de oráculo:** para una tarea de *integración* cuyas unidades ya existen, el
  RED honesto es de guards + evidencia de aceptación, no un fallo artificial.
- **(b) GREEN:** `d7ffbcc` — +38 líneas en `skills/cdad-cycle/references/re-entry.md`:
  protocolo canónico del orquestador (RECEIVE → RECONCILE → MATERIALIZE → STATE
  TRANSITION; un solo escritor del state; el recibo nunca aprueba; el dueño de la
  interfaz es el CLI + la spec, sin duplicarla). **Declaró fundadamente** que
  `install.sh` y `cdad_packet.py` **no** requieren cambio, con la evidencia. Verificado
  por el orquestador: el commit toca sólo `re-entry.md`; 0 cambios en `tests/`;
  `test_packet_prepare` 19/19; suite **439 passed / 601 s**.
- **(c) Review final:** `review-t4.md` — **changes-required**: **F1 BLOCKING** (familia,
  una pasada de documentación): **F1.1** el paso RECEIVE no define cómo el TEXTO FINAL
  se vuelve recibible (`receive` exige `staged-file` + descriptor bajo `.cdad/inbox`;
  el TEXTO FINAL es el caso dominante → la instrucción es incompleta para su caso
  primario); **F1.2** `README.md` listado en el plan T4, no tocado, desviación no
  documentada. **F2/F3 OPTIONAL** (F2: `handoff-prompts.md` describe el mecanismo
  manual; F3: la clase de smoke no ejecuta el entrypoint). Conformidad verificada:
  protocolo ✓ contra §9/§6, claim de no-cambio ✓, guards observables ✓, sin regresión ✓;
  auditoría test↔postcondición CUMPLE (AP-14).
- **(d) Verificación del orquestador:** el fundamento de F1 se confirmó contra el código
  (`cdad_result.py:232-234`, `:249-272`) y la spec (§3, `:172-174`) — **el bloqueante es
  real**. La abstención 2 del reviewer (validate-state sobre un state reconciliado con la
  referencia nueva) se cerró **empíricamente** por el orquestador:
  `validate-state` → `VALID … rc=0`.
- **(e) Disposición de F1.2:** diferido con razón (la política no clasifica `README.md` y
  revisarla está fuera de alcance) + brecha de política registrada como decisión del
  dueño — ver "Desviaciones registradas de T4" en `plan.md`.
- **(f) Disposición de F2/F3:** F2 se incluye en la MISMA pasada del arreglo de F1.1
  (puntero de una línea en el mismo cuerpo documental; costo marginal ≈ 0; evita una
  ronda futura por la misma incoherencia). F3 se difiere: exige ronda de test-writer y el
  criterio ya está cubierto por el guard 2 → desproporcionado.
- **(g) Pendiente:** arreglo de F1.1 (+F2), re-review focal y cierre.

## T4 — cierre de la integración y PRIMER USO REAL del flujo (2026-10-06)

- **Re-review focal:** `review-t4-rereview.md` — **F1.1 CIERRA** (cláusula de staging
  correcta, verificada contra spec §3/§4, sin duplicar la interfaz), **F1.2 CIERRA** por la
  opción (ii) (desviación registrada con razón fundada y verificada: `docs/cdad-policy.json`
  no clasifica `README.md`), **F2 cerrada 3/3**. Sin regresiones, sin hallazgos nuevos.
- **Primer uso real del flujo (orquestador, en este repo):**
  1. `prepare --record-dispatch … --attempt-id rev-010-a1` (observación I8) → `dispatched`.
  2. Staging del TEXTO FINAL del reviewer bajo `.cdad/inbox` + `RESULT.json` + manifest
     (baseline declarado `git:<HEAD>`, `changes: []`) — **exactamente la cláusula F1.1 que
     el review-fix acababa de escribir**: el fix se validó en uso, no solo por lectura.
  3. `receive` → **rc=0**; receipt con `packet_validation=passed`,
     `identity_validation=passed`, `scope_validation=passed`, `semantic_status=pending`,
     `state_transition_requested=received`.
  4. `materialize` (create-only) → **rc=0**; target
     `docs/specs/003-002-artifact-tools/review-t4-rereview.md` con **bytes idénticos**
     (sha256 `82a63fcb…` = el staged).
  5. Idempotencia en uso: retry de `materialize` sin doble efecto; retry de `receive`
     converge al **mismo receipt byte a byte**.
  6. El state **no** fue tocado por las herramientas; el orquestador registró la
     transición y la referencia al recibo (`receipt_sha256`, `bundle_sha256`, partes) en
     `stage_history` — el ítem que el plan T4 asigna al orquestador.
- **Qué queda comprobado y qué no:** comprobado el recorrido real (arriba) y el recorrido
  desde el producto instalado en raíz aislada (guards de T4). **No** comprobado: el caso
  `observation_status=unknown` (no se ejercitó: el manifest declarado fue `trusted` con
  `changes: []`), y la materialización de un Memory Bank por CAS (no se ejercitó; el
  primer uso fue create-only).
