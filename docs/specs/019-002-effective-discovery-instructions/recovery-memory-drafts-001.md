Route C validated before any work. Here is my report and the three drafts.

---

## 0. Intake validation (route C)

| Check | Command | Result |
|---|---|---|
| Spec sha256 vs contracted | `sha256sum docs/specs/019-002-effective-discovery-instructions/spec.md` | `cd61455c…1f0382` — matches |
| Execution context | `.cdad/executions/exec-019-002-effective-discovery-instructions-001/execution.json` | `schema_version: 2` (v2 OK for route C); `exec-019-002-effective-discovery-instructions-001`; `epic-019-discovery-dialogue` |
| Request | `python3 scripts/cdad_packet.py validate-request --execution-context …/execution.json --request …/REQUEST.json` | `rc=0`, no diagnostic |
| Packet | `python3 scripts/cdad_packet.py validate-packet --execution-context … --request … --packet …/PACKET.md` | `rc=0`, no diagnostic |
| Identification match | packet_id, execution_id, contract path, sha256 (`commit: null`) | all match REQUEST.json and PACKET.md |

No inline packet body was supplied; only the identification block — admissible on route C, and nothing stood in for it. Write scope is empty; I edited nothing and committed nothing.

**Inputs read:** the approved spec (PC-1..PC-7, supersession, `deferred-hardening`), `recovery-execution-progress.md`, `recovery-contextual-review-003.md`, `recovery-exercise-review.md`, `recovery-readme-maintenance-decision.md`, plus `recovery-approval.md`, `recovery-delivery-{red,green}.md`, `recovery-orientation-{red,green}.md`, `recovery-semantic-production.md`, `recovery-semantic-fix-001.md`, reviews 001/002, the epic plan/execution, `docs/.cdad-state.json`, and the three current Memory Bank files.

**Declared deviation, stated up front:** the objective asks for FULL replacement text of three files (6 271 / 1 956 / 1 535 lines). I do not re-emit ~9.8 k lines of verbatim unrelated history — doing so by transcription would risk silently corrupting the history the invariant tells me to preserve, and adds no information. Instead each draft below is the exact final text of the **changed region**, with the anchor (file + line numbers verified with `git rev-parse HEAD` = `fa128cea…`) that the orchestrator materializes by insertion/replacement. Nothing else in those files changes.

---

## Draft 1 — `docs/activeContext.md` (FINAL TEXT)

**Insertion:** after line 5 (`---` + blank line, before `## 2026-11-15 — Feature: 019-003-contract-verification-strategy`). Lines 1–5 unchanged; every existing entry unchanged.

```markdown
## 2026-11-16 — Feature: 019-002-effective-discovery-instructions

**Implementación y revisión independiente aceptadas; cierre de feature NO registrado.** Epic 019
(`epic-019-discovery-dialogue`), orden **3/3**, la última. El producto es la activación del diseño
de discovery aprobado en instrucciones canónicas y consumidores efectivos, más la corrección de la
entrega de consulta y del reposo. La aceptación se hizo bajo la HITL delegada del epic
(`docs/epics/epic-019-discovery-dialogue/execution.md`); **el cierre, la suite completa y el
mantenimiento de README siguen pendientes**, y el epic **sigue abierto**.

**Punto de partida y reconstrucción.** El dueño eligió `bc922c04` como baseline de producto y
tests; la restauración se hizo en `e2e67620` (superficies de producto) y `49b3feec` (árbol de
tests), conservando el bundle histórico de Git y los tests retirados. Sobre esa base la
reconstrucción fue mínima y con RED/GREEN independientes: PC-4 en `dbb15fbd` (RED, 4 fallos de
aserción) y `cbd7828a` (GREEN, 17 tests en verde; 4 líneas en `_allowed_kinds` de
`skills/cdad-cycle/scripts/cdad_result.py`); PC-5 en `62224ee7` (RED, 1 fallo y 1 control) y
`02ff945a` (GREEN, 105 tests de regresión de `status`/`open-unit`/idle-history).

**Producción semántica.** `d415cc1b` escribió las instrucciones afectadas —regla "Discovery
dialogue" del orquestador, consulta del architect como `role-report`, reentrada y handoff,
`stage-1/2/5`, `SKILL.md`, `odoo-architect`, `CDAD_metodologia.md` §6.2— y `make agents` regeneró
12 archivos por runtime (+40/−10, sin cambios ajenos no explicados). Dos correcciones: `5bb788dc`
(el cierre mandaba a `done`/`null`, la consulta no era opcional y había cuota de preguntas) y
`54b40d76` (la plantilla de borrador ya no exige un resumen de brainstorm que puede no existir).

**Revisión.** Tres rondas contextuales independientes contra las fuentes de control:
`recovery-contextual-review-001` (3 bloqueantes), `-002` (1 bloqueante) y `-003` (**sin
bloqueantes nuevos en su alcance**; reutilizó los GREEN registrados sin repetirlos y declaró
ausente `recovery-handoff-fix.md` en su checkout). El ejercicio de uso real de PC-7 se corrió en un
proyecto descartable —no es una sandbox— con los hashes de las instrucciones candidatas congelados
antes de ejecutar; la evaluación independiente (`recovery-exercise-review.md`) lo declara
**supported within declared limits**: respuesta parcial, default no aceptado, corrección
autorizada que gobierna, incertidumbre que impide readiness, consulta previa al borrador, borrador
no aprobado y revisión independiente. **No** acredita PC-4/PC-5, el cierre ni el cumplimiento
universal de agentes. Los intentos fallidos se conservan como tales: la consulta que cargó una ruta
como identificador de skill, y el paquete de borrador de 6083 bytes frente a 6084 canónicos,
rechazado antes de redactar.

**Decisiones relevantes.** *La consulta vuelve porque la tabla canónica lo admite*: `role-report`
para architect/brainstorm se resuelve en `_allowed_kinds` y ambas rutas —nativa y OpenCode— derivan
de ella. Precio: hubo que reemplazar la expectativa obsoleta de rechazo en
`tests/test_006_005_u7_scribe_role_report.py`; beneficio: una sola casa y ninguna cardinalidad
global de partes inventada. *La prohibición mínima del orquestador es autoría de producto y tests*:
puede investigar, leer código y ejecutar el producto, y una corrección formal trivial vive solo en
una presentación corregida separada y atribuida, mientras `_apply_copy` conserva el destino
idéntico (`cdad_result.py:971–984`) y rechaza la divergencia, sin tocar el original, su recibo ni
la copia del diario. *El reposo no es un modelo de estado nuevo*: `status` aplica la misma
comprobación de coherencia que `open-unit` antes de recomendar abrir y convierte `done`/`null` en
diagnóstico, y sigue read-only. *La verificación retiene la estrategia de 019-003* (método por
promesa, evidencia por postcondición) y no reinstala lo superado: el registro rígido de diálogo y
las cuotas de escenarios de los PC-4/PC-11 anteriores quedan **superseded**, y sus observaciones
fallidas o incompletas siguen siendo evidencia histórica, no logros.

**Verificación y sus límites.** Suite completa **no realizada** a la fecha de este borrador: el
turno 4 del ejercicio y la corrida de `tests/` quedaron como comandos de fondo finitos y su
resultado no se declara. Selecciones ejecutadas y registradas: 17 tests (`cbd7828a`), 105
(`02ff945a`), 67 + 92 (generación, render, recepción congelada y consumidores), 33 (post-fix
`54b40d76`). **F011 sigue rojo** por drift de instalación global (instalado ≠ candidato): excluido
del alcance aceptado y **no verde**. La igualdad de bytes y la revisión contextual establecen
instrucciones, nunca conducta de agentes reales.

**Deuda detectada.** **(1)** Suite completa de `tests/` pendiente y obligatoria por defecto en el
cierre de epic (se corre contra `tests/`; se excluye `examples/idea_log/tests/test_idea_log.py`,
que exige entorno Odoo). **(2)** Cuatro regresiones **preexistentes** de README que el baseline
restaura, reproducidas en el candidato: `4 failed, 3 passed` sobre `tests/test_005_006_t4_readme.py`
y `tests/test_005_006_t6_owner_reviewfix.py` (log en
`.cdad/orchestration/epic-019/recovery-readme-baseline.log`). La disposición es una asignación
separada y acotada a `README.md` después del snapshot de suite, usando `2de6e72b` como evidencia y
no como instrucción de replay, con revisión independiente y las pruebas de regresión protegidas; no
se cambia producto mientras la corrida esté en curso. **(3)** F011 / `install.sh --check` no verde,
causa no aislada. **(4)** Defecto **procedimental** visible: el registro de recepción de implementer
review-fix-013 se lanzó en segundo plano antes de preparar el paquete de revisión siguiente y falló
con `active_packet mismatch: id`; no se fabricó recibo, no se re-despachó el paquete, el informe
original se conservó (`recovery-handoff-fix.md`) y la revisión cerró el hallazgo sobre el diff real
de `54b40d76`. **(5)** En el proyecto descartable, `projectbrief.md` quedó desactualizado frente a
las decisiones ya resueltas —hallazgo **opcional**, bucket m—: solo importa si ese proyecto se
continúa. **(6)** `deferred-hardening` del spec con su disposición: *cumplimiento universal y
cobertura exhaustiva de escenarios* — fuera de la promesa acotada, se observa solo lo comprometido;
*enforcement semántico o de aprobación automático* — sin necesidad demostrada, reconsiderar ante una
deficiencia concreta; *diagnóstico `--check` de la instalación y despliegue* — trabajo operativo
separado, no prometido acá; *limpieza documental y regresión no relacionadas* — fuera del delta.
Ninguna de las cuatro aplaza una postcondición comprometida.

**Siguiente en la cola.** No hay otra feature abierta: resta el **cierre de `019-002`** (suite
completa de `tests/`, inventario vivo, Memory Bank) y el **cierre del epic 019**, condicionado a esa
suite, al mantenimiento acotado de README y al registro formal. Publicación y despliegue siguen
reservados al dueño.
```

---

## Draft 2 — `docs/progress.md` (FINAL TEXT)

**Replacement:** lines **5–15** (the `## In progress` block), keeping line 16 (blank) and everything from line 17 (`Historical note retained below…`) untouched, including `## Despliegue`, `## Done`, `## Queued`, `## Blocked` and the dated log.

```markdown
## In progress

**Active epic: `epic-019-discovery-dialogue` — plan approved by <owner>, 2026-11-15.**
`019-001-discovery-dialogue-contract` y `019-003-contract-verification-strategy` **cerradas el
2026-11-15** (detalle en `## Done`). `019-002-effective-discovery-instructions` (orden **3/3**, la
última) tiene **implementación y revisión independiente aceptadas** bajo la HITL delegada del epic,
y su **cierre de feature todavía no está registrado**: quedan la suite completa de `tests/` (corrida
de fondo finita), las cuatro regresiones preexistentes de README y el cierre formal del epic. **No
se declara** suite verde, coherencia de instalación (`F011` sigue rojo), despliegue, publicación ni
cierre de epic; publicar y desplegar siguen reservados al dueño. Detalle en el entry del 2026-11-16
de `activeContext.md` y en los documentos de recuperación de
`docs/specs/019-002-effective-discovery-instructions/`. Plan:
`docs/epics/epic-019-discovery-dialogue/plan.md`.
```

*Note on the transition:* the feature is **not** moved to `## Done` — its closure is not registered. What changes is the premise of the paragraph (before: "suspendida y a reanudar"; now: accepted, closure pending). When the closure is actually registered, the `## Done` bullet must be built from that materialized closure, not from this draft.

---

## Draft 3 — `docs/systemPatterns.md` (FINAL TEXT)

### 3.a New framework-pattern subsection

**Insertion:** after line 641 (end of `### Suite instrumentada y lote paralelo fail-closed (epic 017, 2026-11-08)`), immediately before `## Palanca \`write: ask\` y permisos de bash (cdad-010, ADR-009)`.

```markdown
### Diálogo de discovery efectivo — consulta entregable y reposo coherente (epic 019, 2026-11-16)

- **La consulta del architect vuelve porque la tabla canónica lo admite, no porque un adaptador lo
  permita.** `architect`/`brainstorm` entrega un `role-report` resuelto en `_allowed_kinds` de
  `skills/cdad-cycle/scripts/cdad_result.py`, y las dos rutas —nativa y OpenCode— derivan de esa
  tabla; los kinds de borrador quedan rechazados en esa subfase. Motivo: sin un kind entregable la
  consulta no puede regresar y el descubrimiento se interrumpe. Precio declarado: se reemplazó la
  expectativa obsoleta de rechazo en `tests/test_006_005_u7_scribe_role_report.py`, y no se impuso
  cardinalidad global de partes. Base: `019-002` PC-4, `cbd7828a`.
- **La prohibición del orquestador es autoría de producto y tests; la corrección formal trivial va
  aparte.** El orquestador conduce el diálogo, investiga, lee código y ejecuta el producto; puede
  mostrar una corrección de forma en una **presentación corregida** nombrada aparte, con autoría
  original y atribución de la corrección, mientras `_apply_copy` conserva un destino idéntico
  (`skip`) y rechaza la divergencia (`cdad_result.py:971–984`). El original, su recibo y la copia
  del diario quedan intactos; un defecto sustantivo vuelve al rol responsable. Base: `019-002`
  PC-3, `spec.md:39–41`.
- **El reposo se comprueba antes de recomendar, con el chequeo que ya existía.** `status` aplica la
  misma validación de coherencia de reposo que `open-unit` antes de devolver `next-unit`; un estado
  `done`/`null` produce `diagnosis` con el texto del error y ninguna recomendación de abrir ni
  afirmación de reposo, y `status` sigue read-only, sin vocabulario de estado nuevo. Base: `019-002`
  PC-5, `02ff945a`.
- **La verificación retiene la estrategia por promesa y no reinstala obligaciones superadas.** El
  método por promesa de `019-003` gobierna la evidencia de esta feature (contextual, ejecutable o
  combinada, por postcondición). El registro rígido de diálogo y las cuotas de escenarios de los
  PC-4/PC-11 anteriores quedan **superseded**; sus observaciones fallidas o incompletas siguen
  siendo evidencia histórica y no se reescriben como éxito. Base: `spec.md` §Supersession.
- **Límites que esta convención no convierte en garantías.** La igualdad de bytes y la coherencia
  contextual no demuestran conducta de agentes reales ni cumplimiento universal; el ejercicio PC-7
  es evidencia acotada de candidato en un proyecto descartable, no despliegue ni benchmark; `F011` /
  `install.sh --check` sigue rojo por drift de instalación y no se declara verde. Normativo en
  `docs/specs/019-002-effective-discovery-instructions/spec.md` (PC-1..PC-7) y sus documentos de
  recuperación; este archivo no re-enuncia postcondiciones.
```

### 3.b Included correction to the ADR index note (attributable, droppable)

This closes the stale note already recorded as debt of `019-003` (`review-009`, FYI opcional, sin defecto material). **Replacement** of the third bullet of the `**Nota.**` block (currently one line listing `ADR-012, ADR-016, ADR-025…ADR-030`):

```markdown
- Quedan fuera los ADR que todavía no están en vigor (`Proposed`): ADR-012, ADR-016, ADR-025,
  ADR-026, ADR-027, ADR-028, ADR-029, ADR-030, ADR-037, ADR-038 y ADR-039. Cada uno recibe su fila
  al aprobarse, y entonces esta lista se actualiza. ADR-037/038/039 conservan `Proposed` en su
  propio archivo; ADR-012, ADR-016, ADR-027 y ADR-028 no declaran `Status` y su exclusión no se
  re-deriva acá.
```

If the owner prefers 019-002 not to touch 019-003's debt, drop 3.b — 3.a stands alone.

---

## ADR — **No ADR suggested**

The final work contains no new architectural decision that needs its own record: `role-report` for architect/brainstorm is a row in the existing canonical kind table (both adapters already derive from it), and the resting coherence reuses `_validate_idle_coherence` with no new state vocabulary, no new mechanism, no new gate, no permission change. The two decisions are normative where they live (`cdad_result.py` table, `cdad_packet.py status_view`, and the spec), consistent with the packet objective ("no need new policy/ADR") and with this project's rule that a rule has one home and consumers point at it. If the owner prefers a record anyway, the candidate would be a single ADR titled "La consulta del architect se entrega como `role-report` de la tabla canónica y el reposo se comprueba antes de recomendar", with Confidence **Medium** — the mechanism is demonstrated by focused tests and contextual review, not by live agent behaviour.

---

## R6 — `deferred-hardening` and its dispositions (not omitted)

Carried verbatim in Draft 1's "Deuda detectada (6)" and to be carried into the `closure.md` the orchestrator materializes:

| `deferred-hardening` | Disposición registrada |
|---|---|
| Cumplimiento universal y cobertura exhaustiva de runtime/escenarios | Fuera de la promesa acotada; se observa solo lo comprometido (PC-7 acotado) |
| Enforcement semántico o de aprobación automático | Sin necesidad demostrada; reconsiderar solo ante una deficiencia concreta |
| Diagnóstico `--check` de la instalación y despliegue | Trabajo operativo separado; no prometido ni ejecutado acá (F011 rojo) |
| Limpieza documental y regresión no relacionadas | Fuera de este delta; incluye las cuatro regresiones de README, con asignación propia |

None postpones a committed postcondition. No new policy is required by any of them.

---

## Limits of this report (PD-15)

- **Drafts only.** Zero files modified, zero commits (`git status --porcelain` shows only the pre-existing ` M docs/.cdad-state.json`). Strategic approval is the owner's; materialization and git are the orchestrator's.
- I did **not** verify runtime behaviour: no test was run by me, and I credit no green of my own. Every count above is attributed to the document that recorded it.
- I did not claim, and the drafts do not claim: full-suite green, installation coherence, deployment, publication or epic completion.
- One observation I deliberately did **not** draft: the table row for `ADR-009` reads `vigente` while ADR-009's own file still says `Proposed`. It is outside 019-002's evidence and outside my mandate; flagged here only so it is not lost.
- Two anchored edits (3.a, 3.b) instead of a verbatim full-file replay — the deviation is declared above and its reason is the preservation of unrelated history, not convenience.