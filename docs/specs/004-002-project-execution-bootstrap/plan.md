> Materializado por el orquestador desde `architect-draft-002` (Codex gpt-6-astra), verbatim salvo links relativos. Ver `spec-gate-claude-002.md` para las condiciones de aprobación.

## Plan de tareas revisado

Cada tarea de construcción sigue RED → GREEN en sesiones separadas → revisión del delta → verificación del orquestador. Su cierre identifica contrato, cambios reales, snapshot probado y desviaciones con disposición.

| Tarea | Entrega y verificación | Dependencia |
|---|---|---|
| **T1 — Política y clasificación** | PD-1/2/9: propuesta determinista, esquema mínimo, clasificación y exclusiones, temporales, protección de la política. Fixtures de los cuatro layouts. | Spec/plan aprobados. |
| **T2 — Bootstrap e identidad** | PD-3/4/10: contexto v2, autoridad vigente, binding con ubicación, bootstrap sin identidad manual, reanudación y rechazo de v1 sin modificación. Inicio de trazabilidad de fixtures. | T1. |
| **T3 — Consistencia durable** | PD-5/11: snapshot, reconciliación, exclusión y recuperación en los cinco puntos. Publicación coherente de los artefactos derivados que incorpore T5. | T2. |
| **T4 — Intentos de despacho** | PD-6: registro durable, idempotencia, unknown y rechazo de contradicciones. Tests que demuestran que no recibe resultados ni cierra paquetes. | T3. |
| **T5 — Scopes y mecanismos runtime** | PD-7/8: agentes locales OpenCode, guard CC dinámico, protección de política, coherencia semántica y pruebas de activación. Verificación separada de `--standalone` y servicio de fondo. | T1–T4. |
| **T6 — Aterrizaje utilizable** | PD-10/12: instalación aislada, eliminación de dependencia residual de `agents/`, consumidores legacy/standalone, documentación mínima, validadores y resolución trazada de fixtures v1. Revisión independiente del bootstrap instalado. | T5. |
| **C — Único corte operativo** | Cierre del último paquete v1, preservación de evidencia y creación de ejecución v2 nueva mediante el bootstrap instalado. | T6 en verde y revisión conforme. |
| **T7 — Aceptación integral y cierre real** | Test-writer completa la matriz integral de aceptación; implementer realiza la integración pendiente y corrige defectos observables; reviewer revisa el conjunto y scribe entrega cierre/Memory Bank. Todos por paquetes v2. Se completa PD-13 y se dispone la fricción. | Corte C. |

**Regla operativa anterior al corte.** T1–T6 se despachan con el contexto actual `exec-004-002` y una revisión identificada del productor v1. La construcción de v2 se verifica en consumidores aislados; no sustituye prematuramente al productor de la ejecución activa. Se fija también la revisión de sus recursos, para no mezclar el ejecutable anterior con assets nuevos.

**Procedimiento del único corte C:**

1. Terminar y registrar el último paquete v1; no debe quedar un trabajo `prepared` o `dispatched`.
2. Registrar commit de la herramienta anterior, hashes del contexto/paquetes y snapshot del state terminal. Conservar el ledger interino sin convertirlo en intentos v2.
3. Comprobar T6: bootstrap instalado, política materializada por el dueño, autoridad verificable, validadores y pruebas de capacidades.
4. Ejecutar el `prepare` nuevo para el primer encargo de T7. Crear **otro `execution_id`** y su contexto bajo `.cdad/executions/<nuevo-id>/execution.json`, conservando `.cdad/execution.json` v1 intacto.
5. Publicar el nuevo binding y paquete mediante la transacción de PD-11. Registrar la relación entre ejecución anterior y nueva en la evidencia del corte.
6. Desde esa publicación, todos los nuevos encargos de 004-002 utilizan v2. Un fallo previo a completar la publicación se recupera según PD-11; no cuenta como un segundo corte. Un defecto posterior se corrige sobre v2.

T7 contiene aceptación e integración real todavía pendientes; no exige fabricar un RED ni repetir tareas ya cerradas. Las pruebas sintéticas sirven para verificar garantías y no sustituyen los despachos reales.

## Condiciones de aprobación (dueño, 2026-09-29; gate `spec-gate-claude-002.md`)

- **C1** — El trabajo real de T7 es adoptar v2 en este repo. El dueño
  materializa `docs/cdad-policy.json` (implementación: `scripts`, `agents`,
  `skills`, `sources`, `build`, `install.sh`); se generan y publican los
  agentes de proyecto `.opencode/agents/`, y se verifica en vivo que el
  test-writer ya no lee `scripts/`.
- **C2** — T5 media `Grep`/`Glob` en el guard de Claude Code por su forma
  real de entrada (`path`/`pattern`), o las declara como limitación antes del
  despacho. Se prueba con la forma real y en una sesión real.

## Asignación de modelos (decisión del dueño)

Test-writer e implementer: modelos económicos (glm-5.3-flash,
deepseek-v4.1-flash). Review (y architect): gpt-6-astra vía Codex.
Orquestación y gates: Claude.

## Decisiones de interfaz del orquestador

- **I1 (T1):** superficie observable de PD-1/PD-2/PD-9 independiente del
  bootstrap: subcomando de solo lectura
  `cdad_packet.py validate-policy --project-root <raíz> [--classify <ruta>...]`,
  de la misma familia que los `validate-*` existentes. Sin escrituras. rc=0 si
  la política es válida; si no, rc≠0 con diagnóstico por regla. `--classify`
  imprime una línea `<ruta>\t<clase>` por ruta (clases: `test`,
  `colocated-test`, `implementation`, `documentation`, `policy`,
  `temporary`, `unclassified`). `prepare --propose-policy` imprime la
  propuesta por stdout.
- **I2 (T2, autoridad verificable):** la aprobación del contrato se acredita
  con una entrada de `stage_history` que tenga `feature`,
  `stage: "specification"` y `approved_by` no vacío. La delegación se acredita
  con `hitl_delegation` presente, `source` existente, `scope` que nombre el
  epic, epic activo (`active_epic`) y sin `revoked_at`. Un campo `status`, si existe, debe valer
  `active`; su ausencia no invalida el registro (W-1, corte C). Lo mismo vale para
  `epic_id`: si existe, debe coincidir; si falta, decide `scope` (W-1b). En
  `scope`, `:` y paréntesis separan tokens; la coincidencia sigue siendo
  exacta (W-1c). En standalone
  (`active_epic` nulo) basta la aprobación del contrato. Si falta algo, el
  diagnóstico nombra el registro faltante; no se infiere autoridad de
  nombres, textos ni defaults.
- **I3 (T2, bootstrap y ejecución anterior):** sin ningún contexto, `prepare`
  crea la ejecución v2 de forma implícita. Si existe un contexto previo (v1 en
  `.cdad/execution.json` o una v2 activa de otra feature), se exige
  `prepare ... --new-execution`; sin esa opción: diagnóstico, rc≠0, sin
  escrituras. El contexto v2 vive en `.cdad/executions/<execution-id>/execution.json`
  (`schema_version: 2`); `state.execution` lo referencia y `validate-state`
  lo resuelve sin `--execution-context`. `.cdad/execution.json` v1 no se
  modifica nunca.
- **I4 (T2–T6, transición v1):** un `--execution-context` **explícito** que
  apunta a un contexto v1 conserva el comportamiento anterior a 004-002 hasta
  T6. En T6 los tests con fixtures v1 se transforman o se retiran con
  trazabilidad (PD-10) y ese camino se elimina. La resolución implícita (la
  nueva) nunca usa v1: sin `--execution-context`, un v1 presente es solo un
  motivo para exigir `--new-execution` (I3).
- **I5 (T3, interrupciones y exclusión):** gancho de prueba inerte
  `CDAD_TEST_FAIL_AT=<punto>`, con puntos `reserved-id`, `context-written`,
  `packet-written`, `before-state`, `after-state`. En ese punto el proceso
  termina de inmediato (código 97, sin limpieza). Sin la variable no hay
  efecto. Exclusión: `fcntl.flock` sobre `.cdad/.lock` durante resolución,
  reserva y publicación. Un segundo escritor recibe diagnóstico de ocupación
  y rc≠0 sin esperar. El lock no sobrevive a la muerte del proceso.
- **I6 (T3, reconciliación):** `prepare --reconcile-policy <sha256>
  --decision-ref <ruta>` exige que la ruta sea un archivo existente dentro del
  proyecto y que contenga literalmente ese sha256. También que el sha256
  coincida con los bytes actuales de `docs/cdad-policy.json` y que no haya
  paquete `prepared`/`dispatched`. La revisión aceptada se agrega al historial
  de la ejecución y la anterior se conserva.
  - *Refinamiento de I4 (T2, aceptado por el orquestador):* la adopción la
    señala la política. Con `docs/cdad-policy.json` presente, un v1 implícito
    exige `--new-execution`; sin política, un proyecto legacy con
    `.cdad/execution.json` v1 conserva su camino implícito anterior (D2: los
    proyectos legacy conservan su funcionamiento).
- **I7 (T2 review-fix, reanudación):** `prepare --resume-packet <id>` no
  acepta **ninguna** opción de preparación ordinaria (`--role`,
  `--substage`, `--objective`, scopes, inputs, invariants, evidence,
  expected-output, out-dir, execution-context). Reanudar es reemitir los
  bytes verificados del paquete, no reconfigurarlo. Cualquier opción
  ordinaria presente da rc≠0 sin escrituras, con el paquete activo o sin él.
  Oráculo firmado por el orquestador: el test positivo de reanudación de T2
  se ajusta para no pasar `--objective` (hallazgo F3 de review-t2).
- **I8 (T4, registro de intento):** el documento `--input` de
  `--record-dispatch` es un JSON con claves cerradas: `runtime`,
  `model_configured`, `model_reported`, `session`, `started_at` (cada una
  texto o `null`; `multi-runtime` no es un runtime válido) y `provenance`
  (objeto campo → fuente, p. ej. `"reported by runtime"` u `"orchestrator"`;
  opcional por campo). Se guarda en
  `.cdad/executions/<execution-id>/dispatches/<attempt-id>.json` con
  `execution_id`, `packet_id`, `role` y `substage` tomados del paquete
  (nunca del documento). `attempt-id` es un nombre plano. Repetir un
  registro idéntico es idempotente (rc=0, bytes iguales); reutilizarlo con
  otros datos da rc≠0 sin sobrescribir. El registro puede pasar el paquete
  activo de `prepared` a `dispatched`, nunca a `completed`/`failed`. Queda
  bloqueado igual que prepare si la política cambió sin reconciliar (PD-5).
- **I9 (T5, agentes OpenCode por proyecto):** los derivados se construyen a
  partir de los agentes OpenCode **instalados** (salidas del generador; el
  producto instalado no trae `sources/`, PD-18) y de la política del
  proyecto. Solo se reescriben los mapas `read`, `grep`, `glob` y `edit`
  según la clasificación:
  - test-writer: deniega lectura y búsqueda sobre implementación salvo los
    tests co-ubicados; edita solo tests.
  - implementer: edita todo menos los tests.
  - lectores: `edit` deny.
  - Todos: `docs/cdad-policy.json` con edit deny.

  El resto del agente queda byte a byte. La ubicación de origen es
  `CDAD_OPENCODE_AGENTS_DIR` o, si no está, `~/.config/opencode/agents`. La
  publicación es parte de `prepare`, dentro de la misma transacción y lock
  de T3: `.opencode/agents/cdad-*.md` más `.opencode/agents/.cdad-derived.json`
  (hash de la política aceptada y hash de cada agente de origen y
  derivado). Si el manifiesto no corresponde a la política aceptada, se
  regeneran antes del próximo paquete. Un derivado modificado a mano da
  rc≠0 sin sobrescribir. Nunca se tocan archivos ajenos en
  `.opencode/agents/`.
- **I10 (T5, guard CC dinámico, C2):** con política presente,
  `path-guard.sh` obtiene la clase de cada ruta ejecutando el `cdad_packet.py`
  instalado junto a él (`validate-policy --classify`): un solo clasificador.
  Media `Read`/`Edit`/`Write` por `file_path`, `Grep` por `path` y `Glob`
  por `path` + `pattern`. Para el test-writer, un `Grep`/`Glob` sin `path`
  (todo el proyecto) cuando existen raíces de implementación se bloquea con
  un mensaje que pide acotar la búsqueda a tests/docs. Con una política
  inválida bloquea: sin fallback a los globs globales. Sin política,
  conserva el comportamiento actual (legacy).
- **I5b (T3 review-fix):** `CDAD_TEST_PAUSE_AT=<punto>` junto con
  `CDAD_TEST_PAUSE_FILE=<ruta>`. Al llegar al punto, el proceso crea
  `<ruta>.reached` y espera a que exista `<ruta>` (tope de 30 s). Es inerte
  sin la variable. `.cdad/.lock` es permanente: el `flock` se libera, el
  archivo no se borra.
  - *Detalle de I10:* el guard localiza el clasificador por `CDAD_PACKET_CLI`
    y, si no está, usa `$HOME/.claude/skills/cdad-cycle/scripts/cdad_packet.py`
    (la skill instalada). Si no encuentra el CLI y existe una política,
    bloquea con un diagnóstico: sin fallback.
- **I5c (T3 review-fix, decisión del orquestador):** `.cdad/.lock` es
  permanente cuando la operación publica algo.
  - En el camino de fallo, si la invocación creó `.cdad/.lock` (y `.cdad`),
    los retira como último paso, todavía con el `flock` tomado y sin trabajo
    crítico pendiente. Así un rechazo no deja rastro (PD-3: "ninguna
    publicación").
  - Adquisición: tras obtener el `flock`, se verifica `fstat(fd).st_ino ==
    stat(ruta).st_ino`. Si no coincide, cuenta como ocupado. Esto cierra la
    carrera de un inodo huérfano cuando el archivo se retiró entre el
    `open` y el `flock`.
  - Enmienda de oráculo: p1 admite `.cdad` y `.cdad/.lock` en un éxito
    sobre un proyecto sin `.cdad` previo.
- **I11 (T6 review, decisión del orquestador):** `--resume-packet` solo
  reanuda paquetes renderizados bajo la revisión de política aceptada vigente.
  Un paquete de una revisión anterior falla con un diagnóstico que nombra ambas
  revisiones y pide preparar un paquete nuevo, sin escrituras. Sus bytes se
  conservan en disco (PD-5: la reconciliación no altera paquetes). No se
  re-renderiza contra la revisión vieja: re-despachar ámbitos de una política
  superada anularía la reconciliación.
- **I5d (T3/T4 review-fix 2):** punto de pausa `before-lock-open` en I5b,
  después de decidir si hay que crear el archivo y antes de abrirlo. Solo
  una adquisición verificada (flock obtenido e inodo coincidente) puede
  retirar `.lock` al salir, y el camino de fallo de la adquisición nunca
  borra. Reconciliar admite solo `--decision-ref`; `--attempt-id` fuera de
  `--record-dispatch` se rechaza. El registro de despacho publica el intento
  y el state en una sola transacción; un reintento idéntico completa la
  transición pendiente.
