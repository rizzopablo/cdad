# Etapa 3 — TDD anti-trampa con sesiones aisladas

La etapa más larga. La trampa principal: que un solo agente escriba test e implementación en la misma sesión. Tu rol como orquestador es justamente prevenir eso emitiendo handoffs separados.

## Convención de tests: contrato, no implementación

Los tests de feature verifican **postcondiciones de comportamiento (el contrato)**, no detalles de implementación. La etapa GREEN necesita libertad de diseño real: el *cómo* se implementa lo decide el implementer; el *qué* se cumple lo define el test. Esta convención rige el packet de RED y el criterio de aceptación de toda la etapa.

**Prohibido en RED**: tests que dependan de estructura interna — orden de llamadas de middleware, nombres de funciones internas, mocks sobre plumbing. Un mock sobre un detalle interno congela una decisión de implementación antes de que exista implementación: invierte el flujo (el test-writer "implementa mentalmente" y el implementer solo traduce), que es exactamente lo que las sesiones aisladas buscan evitar.

**Permitido en RED**: tests que verifican el contrato observable — mensajes wire, resultados de commands, eventos emitidos, auth rechazada, o en general cualquier efecto que cruza un límite que un consumidor externo del sistema (otro proceso, otro servicio, el usuario) puede ver. Un evento interno de coordinación entre dos módulos que nunca sale del sistema **no** es observable a este efecto, aunque técnicamente sea "un evento emitido" — es plumbing disfrazado de contrato. Si dudás si algo es observable, preguntá: *¿un consumidor externo del sistema lo percibiría si cambiara?*

**La cobertura exhaustiva, load/perf y edge cases no derivados del spec no pertenecen al ciclo de feature.** Es responsabilidad de una etapa/epic de hardening separada, posterior. Mezclar ambas preguntas en el mismo gate hace que la más fácil de medir (coverage %) devore el tiempo de la más difícil de razonar (¿es correcto el contrato?).

**Property tests NO son la misma pregunta que cobertura exhaustiva** — cuando el spec marca invariantes explícitos (sub-fase 3.4), el property test verifica ESE invariante puntual, no maximiza casos. La contradicción a evitar: leer la frase de arriba como "no hay property tests en el ciclo de feature" choca de frente con la sub-fase 3.4 de más abajo, que sí los tiene con su propio gate. Lo que queda fuera del ciclo es generar property tests por generar cobertura (sin invariante del spec detrás), no los que el spec explícitamente pide.

**RED verifica el requerimiento, no maximiza cobertura.** Un test-writer que ante una postcondición escribe una batería de edge cases no pedidos, o un property test con generadores que exceden lo que el spec exige, produce dos daños: tests extremadamente difíciles o imposibles de satisfacer que consumen tiempo y tokens en iteraciones GREEN sin llegar a resultado, y un criterio de "hecho" que ya no es el spec sino la imaginación del test-writer. Cada test de RED (y cada property test) debe poder señalar la postcondición numerada exacta que verifica; si no puede, sobra — es la misma regla de "Relevancia" de más abajo, aplicada también hacia arriba: ninguna postcondición dispara más test del que ella misma pide.

**Criterio de aceptación de una feature**: su postcondición verificada por tests de comportamiento, no un porcentaje de coverage.

**Relevancia de los tests**: cada test escrito debe mapear a una postcondición del spec. No se escriben tests por completitud ni por coverage; se escriben porque verifican un objetivo declarado. Si un test no mapea a una postcondición, sobra — regístralo en un audit de trazabilidad test↔postcondición (ver "Auditoría de relevancia" más abajo).

**Contrapartida obligatoria**: como no hay tests exhaustivos, la carga de precisión se mueve al spec, no desaparece. Los objetivos funcionales, especificaciones y requerimientos deben estar **máximamente claros** — postcondiciones numeradas y testeables — antes de abrir RED (ver Etapa 2). Un spec ambiguo produce tests ambiguos y una implementación incorrecta que igual pasa la suite (AP-13, Garbage Cascade).

### Auditoría de relevancia (evitar auto-servicio)

El mapeo test→postcondición (`test-audit.md` o equivalente) **no lo audita la misma sesión que escribió los tests**. Si el test-writer certifica su propia relevancia, el criterio "si un test no mapea, sobra" queda auto-servido. Usá una tercera sesión aislada (o el reviewer de Etapa 4) para esa auditoría, igual que test-writer e implementer están aislados entre sí.

## Presupuesto de corridas (evitar que el runtime devore el ciclo)

La suite completa es de **gate, no de depuración**. En proyectos con suite
lenta (típico en Odoo: el setup desde cero domina el costo, no la cantidad de
tests), la iteración usa corridas mínimas con ciclo anti-loop: leer el fallo
completo → hipótesis escrita → UN cambio → UNA corrida; máximo 2 corridas sin
convergencia → STOP y escalar, nunca re-correr "a ver si pasa". Presupuesto
duro por etapa con regla de STOP; excederlo es señal de escalada, no
justificación para "una corrida más". En proyectos Odoo el protocolo completo
vive en `odoo-make-env/references/run-budget-protocol.md`; en otros stacks,
adaptarlo a la misma estructura (depuración barata, gate completo único).

## Ancla conceptual: el loop TDD es inducción, no abducción

Referencia: "Position: LLMs Can't Jump" (Zahavy, https://tomzahavy.com/files/llms-cant-jump.pdf). El propio paper usa como ejemplo de **Inducción** "generar una función que satisfaga unit tests" — es decir, el loop RED→GREEN de CDAD es inducción guiada por señal de error. Implicaciones para este ciclo:

- **La separación architect (spec) vs implementer (tests) no es burocracia**: la especificación con postcondiciones numeradas es la axiomatización previa; los tests son la señal de error que dirige la búsqueda inductiva. Sin spec clara, el implementer no tiene gradiente (AP-13, Garbage Cascade).
- **Lo que CDAD NO hace es abducción**: generar hipótesis/axiomas nuevos (el "salto" del paper) no emerge del loop de tests — emerge en Etapa 1-2 (Discovery/Planning) o en review externo. Si una feature requiere un salto conceptual, el ciclo no lo va a producir por más GREEN que esté; hay que señalarlo explícitamente al orquestador.
- **El gate de salida mide inducción, no juicio**: suite verde valida consistencia con el contrato, no que el contrato sea el correcto. La corrección del contrato se audita en Etapa 4 (reviewer) y en la validación externa.

## Tu rol como orquestador

NO escribís tests, NO implementás, NO refactorizás. Coordinás:

1. Identificás qué postcondición toca (la primera pendiente, o agrupación ortogonal si el spec lo permite).
2. Emitís handoff a **test-writer** (RED).
3. Validás test rojo en re-entry.
4. Emitís handoff a **implementer** (GREEN).
5. Validás suite verde en re-entry.
6. Opcionalmente: handoff a **refactorer** si hay fricción evidente.
7. Loop hasta cubrir todas las postcondiciones.
8. Si spec marca invariantes: handoff a **test-writer modo properties**.
9. Si spec marca criterios E2E: handoff a **test-writer modo E2E**.
10. Cierre de etapa cuando todos los gates pasan.

## Sub-fases

| Sub-fase | Rol | Cuándo |
|----------|-----|--------|
| RED | test-writer | Postcondición pendiente |
| GREEN | implementer | Tras RED válido |
| REFACTOR | refactorer | Opcional, si hay fricción |
| PROPERTIES | test-writer modo properties | Spec marca invariantes |
| INTEGRATION/E2E | test-writer modo E2E | Spec marca criterios E2E |

## Sub-fase 3.1 — RED

Cargá `references/handoff-prompts.md` sección "Test-writer (Etapa 3 — RED)".

Antes de generar el packet, decidí qué postcondición tocar:

- La primera pendiente del spec.
- O agrupación de postcondiciones **ortogonales** (paths de código independientes que no se pisan). Si están acopladas, una por ciclo.

Generá packet con:
- Spec aprobado completo.
- Interface / firma del módulo.
- Convenciones de testing (`docs/systemPatterns.md`).
- Postcondición específica a verificar.
- Recordatorio explícito: test de contrato observable, no de estructura interna — sin mocks sobre plumbing (ver "Convención de tests" arriba).

Entregás packet, terminás turno.

### Re-entry

Cargá `references/re-entry.md` sección "Test-writer — RED". Verificaciones críticas:

- El test falla por **AssertionError**, no por ImportError ni syntax error.
- El test verifica contrato observable, no estructura interna (sin mocks sobre plumbing, sin asserts sobre orden de llamadas o nombres de funciones internas).

Si pasa: actualizá state, emití handoff a implementer.
Si falla por razón equivocada, o si viola la convención de contrato: handoff de vuelta al test-writer con info del motivo.

## Despacho paralelo

El packet ortogonal (un test-writer, N postcondiciones) sigue siendo el **default**: una sola sesión RED, un solo handoff GREEN. El despacho paralelo —varias sesiones del mismo rol corriendo a la vez— es la excepción que se justifica solo cuando el packet es demasiado grande o las tareas son dominios genuinamente disjuntos.

**Árbol de decisión**:

- ¿2+ (dos o más) tareas **genuinamente independientes** — sin estado compartido y sin archivos en común? → despacho paralelo.
- ¿Comparten archivo o estado? → secuencial, o **wave dispatch** (turnos: la sesión 1 termina y consolida, recién entonces entra la 2). Mismo archivo = serial, siempre.

**Precondición (obligatoria)**: el paralelismo seguro requiere **contrato de interfaz** — los Consumes/Produces del plan (ver "Planning de features complejas" en `references/stage-2-specification.md`). Ese contrato es lo que hace independientes las tareas: define qué produce cada sesión y qué consume la siguiente. Sin él, no hay despacho paralelo: las sesiones se serializan. "Hoy no se pisan" no es un contrato; se rompe mañana sin que nadie lo sepa.

**Reglas de despacho**:

1. **Prompt autocontenido por sesión** (regla §6 de state-passing): cada packet incluye los **owned files** (archivos que esa sesión puede tocar) y una **do-not-touch list** (todo lo demás, explícito).
2. **Scope disjunto verificado**: ante la duda, `git diff --name-only` sobre las branches/dominios planificados antes de despachar, y `comm -12` entre los conjuntos para detectar overlap. El análisis de independencia es lo que habilita el paralelismo, no lo que lo frena.
3. **Mismo rol, sesiones distintas**: cada sesión sigue sin ver el trabajo de las otras — el aislamiento de sesión no se relaja porque haya paralelismo. Lo único que comparten es el handoff del orquestador.

**Integración final (SOLO el orquestador)**: cuando todas las sesiones volvieron —

1. Revisar cada resumen (el resumen del agente **no es evidencia** de que salió bien).
2. Chequear overlap de archivos entre dominios: `git diff --name-only` + `comm` (o equivalente) sobre lo tocado por cada sesión.
3. Correr la suite **COMPLETA** una sola vez al final (AP-3: sin verificación empírica no hay verde).

Los conflictos los resuelve el orquestador, **nunca los subagentes** — un subagente resolviendo un conflicto está tocando dominio ajeno, con vista parcial y sin contrato. Si la integración falla, el orquestador diagnostica y re-delega con el alcance corregido.

**State file**: SOLO el orquestador lo escribe, SIEMPRE. Las sesiones paralelas nunca lo tocan — escrituras concurrentes sobre el state file producen estado indefinido. El orquestador lo consolida en cada re-entry, igual que en el flujo secuencial.

**Wave dispatch como default conservador**: CDAD corre sesiones aisladas sobre el mismo árbol de trabajo, así que los turnos (waves) con dominios disjuntos son el modo conservador por defecto. **Worktree-per-agent** (una branch + un worktree por sesión, merge orquestado) queda documentado como opción para entornos con soporte nativo de worktrees; el cleanup de esos worktrees sigue §5.6 — limpieza por provenance.

### Tabla anti-racionalización

| Racionalización | Realidad |
|---|---|
| "Los archivos no se pisan, no necesito análisis" | El análisis de independencia es lo que habilita el paralelismo, no lo que lo frena; sin contrato de interfaz, "no se pisan hoy" se rompe mañana. |
| "Es una sola tarea, básicamente secuencial" | Sí, y entonces va secuencial — el árbol de decisión no lo presenta como opción paralela. |
| "El resumen del agente dice que salió bien" | El resumen no es evidencia: suite COMPLETA al consolidar (AP-3). |
| "El conflicto es chico, lo resuelvo en mi sesión de fix" | Los conflictos entre dominios los resuelve el orquestador con contexto completo, nunca un subagente con vista parcial. |
| "Mismo archivo en 2 tareas, lo mando en paralelo igual" | Wave dispatch: mismo archivo = serial. |
| "El state file lo puede actualizar cada sesión" | Solo el orquestador: escrituras concurrentes = estado indefinido. |

## Sub-fase 3.2 — GREEN

Handoff a implementer con: spec, test que tiene que pasar, interface, systemPatterns.

### Re-entry

Cargá `re-entry.md` sección "Implementer — GREEN". Verificaciones críticas:

- Suite **completa** verde (no solo el test nuevo).
- Implementer NO modificó tests/.

Si modificó tests: AP-4. Pedí revertir.

Si pasa: actualizá `postconditions_status: { "<N>": "green" }`. Preguntá si refactor o siguiente.

Si la suite sigue roja tras el fix: **ANTES de re-delegar otro GREEN**, el orquestador hace activar `references/stage-debugging.md` (debugging sistemático: loop rojo primero, hipótesis rankeadas, fix único sobre causa raíz). El próximo handoff de fix viaja con el protocolo de diagnóstico — re-delegar sin diagnóstico es thrashing (AP-18).

## Sub-fase 3.3 — REFACTOR (opcional)

**Solo si hay fricción evidente** (duplicación, naming pobre, complejidad accidental). Si código limpio, saltá. Refactor por ritualismo no aporta.

Handoff a refactorer.

### Re-entry

Suite verde EN TODO MOMENTO. Si rojo: AP-11.

## Sub-fase 3.4 — PROPERTIES

Solo si spec marca invariantes verificables. No aplica para código con muchos side effects ni UI.

Handoff a test-writer modo properties.

### Re-entry

Properties verdes con seed fijo, ≥100 inputs.

Si una property falla con input específico: ese input es bug. Handoff a implementer con contraejemplo.

## Sub-fase 3.5 — INTEGRATION / E2E

Solo si spec marca criterios de aceptación E2E o feature toca múltiples capas.

### Modalidades

- **A — outside-in**: E2E primero, queda rojo durante todo el ciclo, va pasando a medida que las piezas se conectan.
- **B — cierre**: E2E al final, después de unidades verdes.

Decidilo con el usuario al inicio de Etapa 3. Para flujo central claro: A. Para agregados a flujos existentes: B.

Handoff a test-writer modo E2E.

### Re-entry

Si modalidad B y E2E rojo: problema de ensamblaje. Handoff a implementer.

## Loop entre postcondiciones

Cada vez que cierra GREEN (+ REFACTOR opcional) de una postcondición, decidís:

- ¿Quedan postcondiciones pendientes? → handoff a test-writer (RED) con la siguiente.
- ¿Todas verdes y spec marca invariantes? → handoff a properties.
- ¿Properties verdes y spec marca E2E? → handoff a E2E (modalidad B) o verificar E2E que ya estaba (modalidad A).
- ¿Todo verde? → cierre de etapa.

## 🛑 Gate de salida (Etapa 3 → Etapa 4)

- [ ] Test Audit completado y aprobado (existe `test-audit.md` con beneficio de duda resuelto, si aplica).
- [ ] Cada test modificado tiene justificación explícita en spec.md.
- [ ] Toda postcondición del spec tiene al menos un test que la verifica.
- [ ] Todo test escrito mapea a una postcondición (sin tests "por completitud").
- [ ] Ningún test depende de estructura interna (sin mocks sobre plumbing).
- [ ] Mapeo test↔postcondición auditado por una sesión distinta a la que escribió los tests.
- [ ] Suite verde (verificado empíricamente con output del run pegado por usuario).
- [ ] Si spec marca invariantes → property tests verdes.
- [ ] Si spec marca criterios E2E → tests E2E verdes.
- [ ] Commits granulares (RED, GREEN, REFACTOR separados).

Cuando todos OK: actualizá state (`current_stage: review`, `tdd_substage: null`). Anunciá transición. Emití handoff a reviewer.

## Anti-patrones a vigilar

- **AP-1**: single session para test + implementación.
- **AP-2**: test escrito después del código.
- **AP-3**: test "verde" sin verificación empírica.
- **AP-4**: implementer modifica tests.
- **AP-11**: refactor que rompe tests.
- **AP-12**: property tests con seed aleatorio.
- **AP-13**: Garbage Cascade — spec ambiguo + tests no exhaustivos = implementación incorrecta que pasa la suite.
- **AP-14**: mock sobre plumbing — test acoplado a estructura interna en vez de contrato observable.

Cargá `references/anti-patterns.md` si detectás señales.
