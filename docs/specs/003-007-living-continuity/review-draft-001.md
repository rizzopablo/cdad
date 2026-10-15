# Review del borrador — 003-007 (ronda 1)

Sesión `rev-003-007-draft-a1` · `<ses-265>` (`mofgw/glm-5.3-flash`), texto final transcripto sin cambios.

# Review — borrador spec/plan 003-007-living-continuity (architect-draft-001.md)

**Encargo:** `handoff-review-draft-001.md` · Rama `codex/epic-003-context-efficiency`, HEAD `f17fab4` ✓ (verificado). Solo lectura; nada modificado.

## Veredicto: APROBABLE CON CAMBIOS

El discovery está bien anclado (re-verifiqué las citas contra el código y los stores reales; las cifras de §0 son exactas — reproduje los digests divergentes de ambas ejecuciones por cuenta propia). El diseño D1–D10 es proporcional y la dirección es correcta. Pero hay 3 vacíos que impiden aprobar tal cual: dos huecos de plan que dejarían T4-REF sin resolver **en la práctica** o romperían el gate de T2, y un modo de fallo no especificado en la parte de integridad.

---

## Bloqueantes

### BL-1 — El cableado del orquestador no declara clases en ninguna tarea (O-A: confirmado)
`Verdict: BLOCKING` · `Bucket: m`

**Evidencia.** Confirmado que hoy ni `sources/roles/orchestrator.md:77-82` ("Continuity wiring") ni `continuity.md` (verificado íntegro, 70 líneas) dicen qué se declara `living`. Con P3, string sin clase = `contract`. Los ejemplos de `continuity.md:29-45` pasan solo strings. **El plan no toca `sources/roles/orchestrator.md` más que en T4, y el alcance de T4 lo limita al texto D9** ("reemplazar el paréntesis…"; "Excluido: cualquier cambio de código del CLI"). `continuity.md` sí se documenta en T1, pero la sesión del orquestador carga el cuerpo regenerado; la cadena "el orquestador sigue el puntero a continuity.md" es exactamente la fragilidad que ya produjo T4-REF en 003-006: el orquestador de entonces pasó ledgers como strings porque no había otra forma.

**Consecuencia.** P9 puede pasar (en T3 el orquestador rota sabiendo lo que hace, guiado por el plan) y aun así la **siguiente** feature re-bloquea: el orquestador de esa feature no habrá leído la convención. El objetivo del dueño ("que resuelva en la práctica, no solo en el CLI") queda insatisfecho.

**Cierre.** Añadir al alcance de T4 (mismo archivo, mismo gate de regeneración) una frase explícita en el bloque wiring de `orchestrator.md:77-82`: ledgers/debt/Memory Bank/drafts se declaran `class: living`; spec/plan aprobados, policy y aprobaciones, `contract` (o puntero estricto a la sección de `continuity.md`). Sin eso, D8 solo documenta para quien ya leyó la referencia.

### BL-2 — T2 rompe el test focal `test_003_006_t4_ru2_refused_write.py` sin declararlo (O-D)
`Verdict: BLOCKING` · `Bucket: m`

**Evidencia.** El docstring de `tests/test_003_006_t4_ru2_refused_write.py:1-59` fija como contrato RU-2: *"un `begin`/`checkpoint` RECHAZADO no escribe nada"*, y su escenario 1(a) exige que un `checkpoint` con la MISMA clave y cuerpo distinto sea **rechazado** con el árbol byte-a-byte intacto. P5/D5 redefinen exactamente ese caso como **append legal** (`seq+1`, eslabón). El test cambiará de resultado por diseño. Sin embargo, `plan.md` T2 lista ese archivo como **focal** y su lista de archivos solo contiene el CLI, el schema, `continuity.md` y un test nuevo — no autoriza editarlo.

**Consecuencia.** El implementer llega al GREEN con un focal rojo que no puede tocar: o el gate falla, o edita fuera de `write_scope` (invalidación del despacho).

**Cierre.** T2 debe declarar explícitamente la modificación de la faceta checkpoint de `test_003_006_t4_ru2_refused_write.py` (la faceta `begin` divergente sobrevive intacta y sigue siendo el corazón de RU-2), con la trazabilidad de la decisión (P5 sustituye la semántica de rechazo del checkpoint, no la del all-or-nothing). Análogamente, `_detect_split_brain` redefinido deja de detectar forks de checkpoints mismo-key — ya está declarado como límite (D5, `continuity.md:55-58`), aceptable; lo que la redefinición **sigue** detectando (≥2 begins/legados por clave, p. ej. huérfanos pre-RU-2) y lo que los tests RU-2 conservan, debe quedar escrito en T2 para que el test-writer no re-especifique RU-2 de más.

### BL-3 — Modos de fallo de `fields` no especificados (O-E)
`Verdict: BLOCKING` · `Bucket: m`

**Evidencia.** D4 dice "el modo `fields` solo vale para JSON" pero ni D1, ni D4, ni P4 dicen qué pasa (a) si `fields` se declara sobre un archivo no-JSON, ni (b) si ninguna clave declarada existe en el documento. En (b) la proyección es `{}` → digest constante → la referencia da **cero integridad en silencio**, contradiciendo el ethos fail-closed de P3 y el invariante 4 de la spec ("deriva `living` nunca bloquea en silencio: siempre se reporta" — pero aquí es `contract` que no protege nada, en silencio).

**Consecuencia.** El test-writer no puede fijar V2 sin esta semántica; el caso b es exactamente el tipo de escape silencioso que el encargo pregunta ("¿debe fallar cerrado al escribir?").

**Cierre.** Una postcondición (o extensión de P4): declaración de `fields` sobre no-JSON → `rc≠0` al escribir (el digest se congela en el body; la validación es de tiempo de escritura); `fields` que resuelve en proyección vacía → `rc≠0` al escribir (o mínimo, reporte explícito `fields_resolved: 0` en el sobre). Fijar en RED.

---

## Recomendaciones

**R-1 — Puente más estrecho para O-B (legado = vivo).** `Bucket: m` · La resolución blanket "sin `class` → `living`" hace que la spec aprobada de una ejecución cerrada informe en vez de bloquear si algún día se edita. Existe un puente estrictamente más fuerte sin violar D2 (no clasifica por ruta): resolver el legado **por comparación** en lectura — digest coincide → se verifica como `contract`; difiere → se reporta `changed` como vivo (con `legacy: true`). Es determinista respecto del estado del archivo, satisface el punto 4 hoy (verifiqué: en ambas ejecuciones solo divergen `dispatch-ledger.md`, `debt.md` y `closure-amendment-draft.md`; las specs/planes congelados están intactos), y bloquea si mañana editan una spec "cerrada". Coste: la clase deja de estar congelada para cuerpos legados — documentable como excepción del legacy. Si el orquestador prefiere el blanket por simplicidad, es defendible (ambas ejecuciones cerradas + `legacy: true` visible en P2/P7), pero debe quedar como decisión explícita, no implícita en D6.

**R-2 — Residuo de O-C: declararlo, no resolverlo.** `Bucket: l` · Confirmado: las aprobaciones (`approved_by`) viven en `stage_history` (154 entradas; p. ej. la de discovery de 003-007) y D1 la clasifica como progreso. Una aprobación forjada/revocada en `stage_history` pasaría sin aviso bajo la proyección. **No es regresión**: verifiqué que ninguno de los dos checkpoints existentes referencia `docs/.cdad-state.json` (hoy el state no está protegido por referencias en absoluto), y las revocaciones de delegación sí quedan cubiertas porque `_state_authority` (`cdad_continuity.py:265-306`) lee `hitl_delegation.revoked_at`, que sí se digiere. Pediría solo que D1 declare este residuo como deuda (integridad de `stage_history`) junto a los otros ítems de D10, en vez de apoyarse en la generalización "las aprobaciones durables viven en el artefacto" — que es cierta para specs/planes, no para todas las entradas del historial.

**R-3 — P7 no debería tests contra stores reales del repo.** `Bucket: l` · La validación de T1 dice "`resume` rinde sobre las dos ejecuciones existentes". Como test focal, acoplarse a `.cdad/executions/…` del repo real viola la convención de fixtures autocontenidos (un re-anclaje futuro del ledger rompe el test sin relación con el código). Mejor: copiar los stores a un tmp en el fixture y dejar la verificación sobre stores reales como observable de T3 (aceptación), donde ya vive.

**R-4 — Ambigüedad menor en el texto D9 (O-F).** `Bucket: l` · El texto protege lo esencial: no agrupar subfases ✓, trazabilidad test↔postcondición (≥1 test por postcondición) ✓, diff acotado ✓. Pero "one plan task, **or** one TDD sub-phase — never two sub-phases" deja sin resolver qué pasa cuando una tarea del plan contiene 2+ subfases TDD (¿una invocación o dos?). En la práctica 003-002..006 RED y GREEN son despachos separados por rol; sugeriría cerrar la ambigüedad en el RED de T4 con un ejemplo ("a plan task whose RED and GREEN are separate dispatches satisfies this"), antes de que el agente regenerado congele la duda.

**R-5 — Nit:** D7 dice `bash install.sh --optimus` — verifiqué que la flag existe (`install.sh:329`, marcador de perfil por defecto de diseño) y que `CDAD_INSTALL_ROOT` es el mecanismo correcto (`install.sh:45,382`); solo sugiero quitar `--optimus` del ejemplo si el marcador ya existe en el repo, para no sobrescribir el perfil del dueño sin decisión.

---

## Restricciones del dueño — verificadas

- **Nunca HOME real:** D7/D8 usan raíz aislada bajo `~/.cache` con `CDAD_INSTALL_ROOT` ✓ (es la raíz aislada, no el HOME del proyecto).
- **Sin push / anonimizar:** plan exige marcadores `<adopted-root>`/`<project-root>` en ledgers ✓; nada del plan pushea ✓.
- **No endurecer permisos:** invariante 6 de la spec ✓; fuera de alcance explícito ✓.
- **Gate de tests vigente:** focales nombrados por tarea ✓ (V6); T4 dispara suite completa por `make agents` (staging/renderer) ✓; T1–T3 solo focales + módulos tocados, correcto según el gate.
- **Scope creep:** no detecté ninguno. Lo que no rompe el camino feliz (defaults por policy, detección de forks, lector de sesiones) está correctamente en deuda (D10, §6). P8 es verificación, no alcance nuevo.

## Qué pasa a deuda (además de lo ya declarado en D10)

1. **Defaults de clase por policy** (ya declarada, con la causa correcta: `cdad_packet.py:406` exige `set(document) == POLICY_KEYS` — verificado).
2. **Detección de forks de checkpoints mismo-key** (ya declarada).
3. **Nueva — integridad de `stage_history`** (R-2): aprobaciones registradas solo en el historial del state quedan fuera de todo digest.
4. **Nueva — huérfanos pre-RU-2 y `_detect_split_brain` casi-muerto:** con P5, la detección solo dispara con cuerpos legados/huérfanos; mantener el límite de orfans documentado en `continuity.md:65-67`.

## Verificación del autor (qué corrió el architect)

Nada ejecutable que reproducir: es un entregable de solo lectura y lo verifiqué como documento — citas file:line (todas las que contrasté son correctas, incluidas `cdad_continuity.py:369-381,463-483,499-524,533-582,647-742,831-835,950-952,1087-1089`, `continuity-checkpoint.schema.json` items `additionalProperties:false`, `orchestrator.md:69-72`, `debt.md:17-18`, `rotation-1-blocked.md`, `checkpoint-after-ru1-REFUSED.txt`), y los digests divergentes de §0 los recalculé yo mismo contra los stores reales con resultado idéntico. V8 (único consumidor de `references[]` = el CLI) la reproduje por grep: confirmada.

## Abstenciones

- **V5 (headroom de 16 KiB):** no medí el tamaño de un update realista con `record`+`class`; el margen es casi seguro suficiente (≈30 bytes/referencia extra) pero no lo presento como medido. Queda para el RED.
- **Que `resume` de las dos ejecuciones reales rinda bajo el diseño nuevo:** es una afirmación de comportamiento futuro; la juzgaste solo a nivel de diseño (D6 puente válido sobre los digests actuales), no la validé ejecutando nada.
- **Comportamiento de `reconcile` bajo P5 con clave del packet viejo tras un append:** no tracé exhaustivamente `_run_reconcile` contra todos los órdenes de eslabones nuevos; el plan debería cubrirlo en el RED de T2 (escenario: reconcile de un packet cuya clave ya no es el head).
