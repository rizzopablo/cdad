## Veredicto

**NO APROBADO tal cual / base sólida con ajustes obligatorios.** El draft cumple el encargo en estructura (tabla de reutilización, schema, reconciliación, triggers, matriz, D1–D11, borradores de spec y plan) y la gran mayoría de las citas file:line verificadas son correctas — verifiqué contra el repo: `state-template.json:1-19` ✓, `003-001/spec.md:487-509` ✓ (binding + `expires_on` + "no se parsea la prosa"), `003-002/closure.md:13-19` ✓ (`semantic_status` siempre `pending`), `003-003/spec.md:150-161` ✓ y `:219-225` ✓, `cdad_guard.py:72-83,586-587,645-651` ✓, `re-entry.md:46-63,79` ✓, `progress-guards.md:17` ✓ (sin lector), `runtime-discovery.md:23-29,39-46,60-65` ✓, epic `plan.md:50-51,69-72,75-76,106-107,121-126,165-169,191-197` ✓, `handoff.md:96-98` ✓, `activeContext.md:84-90` ✓, y los stores reales (`receipt.json` con `semantic_status=pending`/`state_transition_requested=received` y dispatches con `model_configured/reported`) ✓. Los tres validadores citados en aceptación existen ✓. Coherencia con 001/002/003: correcta y sin redefinir contratos (la frontera "003-004 consume la promesa de 003" está bien tomada de `003-003/spec.md:157-160`).

Los problemas son de **proporcionalidad MVP** (lo que el encargo pidió vigilar) y dos huecos de contrato.

## Bloqueantes

**BL-1 — La spec borrador declara las decisiones como ya resueltas (registro de proceso falso).**
Evidencia: `architect-draft-001.md:319-323` — sección "Decisiones resueltas (D1–D11)": "Resueltas por el orquestador bajo la delegación HITL del epic, adoptando las recomendaciones… **aún no cerradas al escribir este draft**". El propio draft dice en :136 que el architect no aprueba, y la nota metodológica :517-518 declara D1–D6+D10 como bloqueo de aprobación. Si el orquestador materializa ese texto tal cual, `spec.md` nace con un aserto falso de resolución — exactamente el anti-sesgo que el draft cita (ADR-003/ADR-011).
Cierre verificable: retitular la sección como "Decisiones **pendientes** del dueño (D1–D11)" con `status: pending-owner` y las recomendaciones marcadas como *propuesta del architect*. Verdict: **BLOCKING**, Bucket: h.

**BL-2 — `begin` no define idempotencia ante re-begin idéntico; su propio caso de crash se bloquea.**
Evidencia: `architect-draft-001.md:79` — paso 3: escribir L2 create-only "si existe con bytes distintos → rc≠0, sin overwrite". Y la matriz :124 (fila 1): "Crash antes de dispatch → checkpoint escrito, sin dispatch, sin receipt → `not-started` → re-despacho permitido". Escenario: crash entre checkpoint y dispatch; el re-dispatch exige un nuevo `begin` (write-ahead). Con `--update` idéntico, el cuerpo canónico es idéntico → mismo sha256 → el archivo existe → rc≠0: **la recuperación de la fila 1 de la matriz queda bloqueada por la propia regla create-only**. Si en cambio el cuerpo incluye `seq` auto-incremental, cada reintento encadena un checkpoint nuevo (crecimiento de cadena por ruido, ver R1).
Cierre verificable: una regla en RED — `begin` con cuerpo canónico idéntico al head existente → no-op exitoso (rc 0, devuelve el checkpoint existente); clave de dedupe `(execution_id, packet_id, attempt)`. Verdict: **BLOCKING**, Bucket: h.

## Requeridos

**R1 — Cadena de checkpoints + `verify-checkpoint` dedicado: sobra.** El brief (`remaining-features-handoff.md:250-251`) pide P1 = tampering/references inexistentes; eso se cumple con `sha256(cuerpo canónico)` + digests por `references[]`. `resume` y `reconcile` ya verifican head y cadena (`:94-95`). Remedio: eliminar `verify-checkpoint` como subcomando (los 4 negativos de tamper se prueban vía `resume`/`reconcile`); `prev_checkpoint_sha256` puede quedar como campo escrito opcional o a deuda. Verdict: **BLOCKING**-advisable / trato como **Required**, Bucket: m.

**R2 — `generation` es redundante.** `ACTIVE.json` lleva `seq` **y** `generation` (`:46-47`). Con un solo escritor (el CLI, invocado por el orquestador) y heads content-addressed, el split-brain se detecta con cabezas divergentes vía `prev_checkpoint_sha256` — la "generation" mayor no aporta información que `seq`+sha no dé. El brief pide resolver split-brain (`remaining-features-handoff.md:245-246`), no un segundo contador. Remedio: un solo contador monotónico (`seq`); regla = cabeza divergente o igual-sha-con-cuerpo-distinto → escalar. Verdict: **OPTIONAL**→**Required** (fusionar), Bucket: m.

**R3 — Subcomando `budget` duplica 003.** La fila 3 de la propia tabla (`:7`) dice "Reutilizar el presupuesto de 003; no duplicarlo" citando `003-003/spec.md:219-225` — y luego T4 produce `cdad-continuity-budget` + contrato `budget-v1` (`:429-431`) que lee los mismos durables. `cdad_guard budget` ya existe, es read-only y determinista. Remedio: cortar el subcomando y el contrato; el snapshot viaja embebido en el checkpoint (`budget.source`), el orquestador sigue consultando `cdad_guard budget`. Verdict: **OPTIONAL** en fundamento, **Required** en efecto (contradicción interna declarada), Bucket: m.

**R4 — Cap 16 KiB duro con rc≠0: número sin fuente fijado en 4 lugares.** Aparece en `:28, :72, :229, :390` como constante. El brief exige "memoria activa pequeña" pero el encargo (`handoff-architect-001.md:32`) manda "preferir mecanismos simples y ajustables" y el brief (`:240-241`) manda calibrar con uso real. Un cliff fijo obligará a reacotar justo en el camino feliz (feature larga con muchas decisiones). Remedio: `--max-bytes` configurable, default 16 KiB, documentado como calibrable; el fallo-cerrado-sin-truncar se conserva. Verdict: **OPTIONAL** (con ajuste), Bucket: m.

**R5 — Número de tareas: 6 → 4.** T5 se solapa con T3: los "6 estados por fixtures" de la matriz **son** los datos de los tests de `reconcile` que T3 ya exige (`:417`). T5 aporta solo la guía `references/continuity.md` y el test de flujo continuo — absorber en T3/T6. T4 tras cortar `budget` queda como "trigger con unknowns". Propuesta: **T1+T2 fusionadas** (checkpoint + active record/resume son una familia de artefacto), T3 (write-ahead + reconcile + fixtures), T4 (trigger), T6 (adopción). 7 contratos con nombre (`checkpoint/resume/reconcile/budget/trigger/fixtures/adoption-v1`) es ceremonia para un script stdlib; con 2-3 basta. Verdict: **OPTIONAL** (recomendado), Bucket: m.

**R6 — Dos miscitas que no soportan la afirmación.** (a) `:138, :272` citan `remaining-features-handoff.md:35` para "sin servicio ni agente permanente" — la línea 35 es la fila "Receipt/evidencia durable"; el soporte real es `plan.md:50-51` (ya citado): eliminar el ancla falso. (b) `:202` cita `remaining-features-handoff.md:43` para "no se fabrica éxito ni fracaso" — la línea 43 es "menor probe útil / no confundir mocks"; la regla citada vive en `003-003/spec.md:150-151` (ya citada). Son anclas de carga; corregirlas. Verdict: **OPTIONAL** (con corrección), Bucket: l.

**R7 — P4 mezcla dos postcondiciones sin relación.** (`:244-247`) "El presupuesto sobrevive" + "si no hay contador se declara `null` con margen conservador" son contratos distintos (presupuesto de intentos vs. trigger de contexto). Con la convención vigente (cada test → una postcondición), el mapeo RED queda ambiguo. Remedio: separar; la mitad `null` va al contrato del trigger. Verdict: **OPTIONAL** (split), Bucket: l.

**R8 — Clave del presupuesto:** P4/§2.4 dicen `execution_id+packet_id`; D4 de 003 la declara `execution_id+packet_id+attempt` (`003-003/spec.md:219`). Usar la clave exacta de 003. Verdict: **OPTIONAL** (nit), Bucket: l.

## Opcionales-Consider

- **O1:** `ACTIVE.json` como caché pura — puede no existir; rehidratación on-demand desde L2-head. Elimina una clase de crash (entre L2 y L1) y un escritor. Dejar explícito que ACTIVE ausente **no** es error de `reconcile`.
- **O2:** T6 `depends_on: [T5]` innecesario — la adopción no necesita los fixtures de fallo; puede depender de T3/T4 y arrancar antes.
- **O3:** Resolver V4 (`--allow-stale`) **antes** de RED para no pagar un flag muerto.
- **O4:** La "prueba de no-regresión de continuidad (global)" (`:471-476`) duplica la validación de T5/T6 — un solo escenario.

## Opinión sobre D1–D11

- **D1 (CLI nuevo `cdad_continuity.py`):** correcto. `cdad_guard.py` ya es grande; mezclar una segunda preocupación empeoraría. Read-only + escritura acotada a `continuity/**` alinea con 002/003. **De acuerdo.**
- **D2 (L2 autoridad, L1 caché derivada, L3 referencias):** la precedencia declarada (`:32`) es sana. **De acuerdo.**
- **D3 (CLI nunca escribe state):** obligado por 002/003; correcto. **De acuerdo.**
- **D4 (autoridad desde state, no desde prosa):** coincide exactamente con `003-001/spec.md:494-495` ("No se parsea la prosa"). **De acuerdo.**
- **D5 (trigger = señal, no límite):** es la lectura correcta de `runtime-discovery.md:39-41` y del V4 de 003. **De acuerdo.**
- **D6 (write-ahead + receipts como oráculo):** el corazón de la feature y lo mejor anclado del draft. **De acuerdo.**
- **D7 (split-brain por generation):** el objetivo sí (brief lo exige), el mecanismo sobra — ver R2. Simplificar a divergencia de cabezas. **De acuerdo en el objetivo, en desacuerdo con el mecanismo.**
- **D8 (OpenCode MVP, sin paridad prometida):** coincide con `plan.md:69-72` y el encargo. **De acuerdo.**
- **D9 (adopción en límite natural, ledger):** es literalmente `remaining-features-handoff.md:265-270` y `plan.md:165-169`. **De acuerdo.**
- **D10 (consume receipts, no materializa):** correcto y coherente con `re-entry.md:46-63`. **De acuerdo.**
- **D11 (decisiones congeladas en checkpoint, historia en L3):** de acuerdo; evita duplicar ADRs.

## FYI

- La nota metodológica (`:516`) declara "HEAD = c643390; directorio no trackeado". Hoy HEAD es `a81ca20` y el directorio ya está commiteado (`docs(003-004): handoff y borrador del architect`). Es foto fiel del momento de redacción — sin acción, solo constancia.
- La cita `plan.md:124-126` soporta "no truncar silenciosamente", no el rc≠0/16 KiB específico (esa es decisión propia del draft, legítima pero sin ancla externa) — no la cuentes como verificación externa.

## Abstentions

- **No ejecuté** la suite ni validadores: la review es documental (no hay código de la feature todavía); el criterio de aceptación 7 del draft se validará en GREEN, no aquí.
- **V1** (¿tokens de `step-finish` por paso o acumulados?): no verificable por lectura de repo sin probe; confirmo solo que `runtime-discovery.md` no lo resuelve — el draft lo declara VERIFY y me abstengo de confirmarlo.
- **V2** (¿`status` distingue "viva estancada" de "terminada"?): igual — solo confirmo la ausencia de prueba en `runtime-discovery.md`; el draft lo maneja bien con VERIFY.
- No verifiqué en vivo `cdad_packet.py validate_state` (solo su contrato en `003-001/spec.md`); la precondición del paso 1 de `begin` se apoya en esa lectura.

— Fin del reporte. El orquestador decide qué es bloqueante; no apruebo ni materializo.
