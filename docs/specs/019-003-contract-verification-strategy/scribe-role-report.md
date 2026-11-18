Validation complete (route C identification + PACKET.md byte-identical to canonical renders; contract sha256 matches). Here is the scribe report.

---

# Scribe report — 019-003-contract-verification-strategy (substage: memory)

**Intake evidence**
```
python3 scripts/cdad_packet.py render --route C --project-root . \
  --execution-context .cdad/executions/exec-019-003-.../execution.json \
  --request .cdad/packets/019-003-...-scribe-memory-002/REQUEST.json     → rc=0; output == the received identification block
python3 scripts/cdad_packet.py render (full)                             → rc=0
diff -u <render> .cdad/packets/.../PACKET.md                             → packet_diff_rc=0
sha256sum docs/specs/019-003-.../spec.md → 969ff8e5...1a3cf (== REQUEST.contract.sha256)
```
Execution context is v2 (`schema_version: 2`), so route C is admissible. Contracts are consistent (feature spec ↔ REQUEST ↔ PACKET). No packet body was rebuilt or normalized.

**Evidence I re-read (not re-run):** `spec.md`, `review-009.md`, `test-audit.md`, `docs/.cdad-state.json`, `docs/progress.md`, `docs/activeContext.md`, `docs/systemPatterns.md`, `docs/adr/*`, the 40-file product diff `0b11b5fb..1dc2e382`, and the closing session's logs under `.cdad/orchestration/epic-019/` (`local-deploy-{staging,dry-run,install,check,verified-check}.log`, `019-003-final-regression.log`, `019-003-inventory-final.log`).

**Deployment facts to keep straight** (`npm`-style summary of what the logs say):
- `local-deploy-install.log` 15:04: `Verify: PASS — 11 cdad agents present after install`; `OWNERSHIP summary: 340 owned file(s), 44 conflict(s)`; conflicts preserved because of user `model:` overlays and locally modified skill copies (`PRESERVED — an overlay does not authorize adopting foreign bytes`).
- `local-deploy-verified-check.log` 15:07: `Check: FAIL`; no agent drift/missing left, only skills-group entries (symlinked runtime paths + the `.agents` tree).
- Observed at draft time (read-only): the 17 changed `skills/…` files compared byte-identical in the installed tree (`SAME=17 DIFF=0 MISS=0`), and both runtimes' `cdad-*` agents carry the new obligations with overlays intact (`~/.config/opencode/agents/cdad-reviewer.md:19 model: openai/gpt-6.1-terra#medium`). This is an observation for fidelity, **not** an accreditation of the install run.
- `019-003-final-regression.log`: 38 passed, `exit_code=0`, `revision=c8fff61b` (three focal files). `019-003-inventory-final.log`: `status: ok`, 2068 nodeids / 248 modules / 31 map entries.
- `review-009.md` abstains from accrediting the 38 as its own green run (its rerun ended 143/timeout) and reports its own 69 distribution comparisons with zero differences. **Full suite: not performed** — recorded below as such.

**Note on language:** the packet orders *English* drafts; the current Memory Bank is in Spanish. I comply with the packet; if the owner prefers continuity with the existing entries, the same blocks are translatable one-to-one without changing content.

**Modified files: none. Commit: none** (drafts as FINAL TEXT; write scope is empty).

---

## Draft 1 — `docs/activeContext.md` (insert as the first entry, right after the `---` on line 5)

```markdown
## 2026-11-15 — Feature: 019-003-contract-verification-strategy

**Closed and locally deployed; not published.** Epic 019, order **2/3** (inserted before
`019-002` by the owner-approved amendment). The product is *canonical instruction*: what a
promise's verification is, where each rule lives, how production is routed, and how closure
evidence is categorised.

**What was delivered — one method per promise, one canonical home per object.**
`stage-2-specification.md` §"Verification strategy per promise" (PC-1: property, numbered
postconditions, method — `executable` / `contextual review` / `combined` —, acceptance criterion,
expected evidence, limits; no new schema, prose or promise-table cells) plus its sufficiency
check in the draft review (PC-2: an insufficient commitment returns before approval, and a
registered exemption is not an executed review nor a claim of sufficiency); the spec template's
per-promise row; `stage-3-tdd.md` §"Routing by verification method" (PC-3: pending executable
behaviour → independent test-writer then GREEN; semantic-only → production then contextual
review, no manufactured RED; mixed → both, neither substituting) and "acceptance is fixed before
production" (PC-4); `stage-4-review.md` §"Closure evidence categories" (PC-5: supported within
declared limits / failed / missing / contradictory / unable to verify, and a declared limitation
never upgrades a category) plus §"Semantic-only and mixed promises at review". Conditioned
consumers: `re-entry`, `handoff-prompts`, `state-detection`, `anti-patterns` (AP-5),
`documentary-contracts`, `cdad-cycle/SKILL.md` (gates and diagram), `cdad-spec-and-test/SKILL.md`
(lightweight path), `sources/roles/{architect,implementer,orchestrator,reviewer,test-writer}.md`,
and the generated agents of both runtimes (12 staging files per runtime).

**Relevant decisions.** *A method chosen by what the promise is, declared before production*:
observable behaviour is verified executably, textual/configuration fidelity by contextual
independent review, and a mixed commitment keeps both families; the trades are an extra field in
every spec and the need to keep method and routing in one home each. *Citing, never restating*:
each rule has exactly one owning file and every consumer points at it, so the cost is more
pointers and the benefit is that a fix lands once — the eight review rounds of this feature were
mostly pointer and conditionality defects, not doctrine defects. *Invariants stop being an
automatic property-test demand*: property tests run only for invariants the approved contract
selects as executable; invariants kept as reviewable restrictions go to Stage 4, and a selected
property campaign that proves infeasible returns to contract review instead of being waived
silently (the exclusion wording that review-007 and review-008 rejected). *A limit never becomes
a success*: the closure categories are exclusive and byte equality is explicitly not semantic
fidelity, favourable review is not a runtime observation, and observed success is not unexamined
behaviour. *This supersedes the 019-001 framing only in generality*: "the test is the review" was
an owner decision for documentary units; 019-003 turns it into the general per-promise rule
without touching 019-001's evidence.

**Verification and its limits.** Nine independent review rounds, eight fix rounds;
`review-009`: **no blockers**, PC-1..PC-6 satisfied on the surfaces examined, both review-008
findings addressed. Test audit (AUDIT-003): all examined verifiers kept, **no test added** —
existing controls are adjacent protection and none accredits semantic sufficiency per se.
Executed selection: `pytest -q tests/test_cdad_generate.py tests/test_010_001_documentary_contracts.py
tests/test_role_packet_render.py` → **38 passed, rc=0** on `c8fff61b`; inventory
`scripts/cdad-suite.py validate` → `status: ok` (2068 nodeids, 248 modules, 31 map entries);
distribution: the reviewer's **own** comparison against the recorded isolated install, **69
comparisons, zero differences**. **Full suite not performed** (feature closure: recommended, not
mandatory; motive: bounded instruction change with the affected files covered by the three
files above; selection and limits as stated). Abstentions to keep visible: the reviewer did **not**
accredit the 38 as its own green run (its rerun ended on timeout, 143) — the 38 rest on the
recorded run, not on a reproduced one; byte equality and contextual review establish the
instructions, never universal agent compliance.

**Local deployment — actual state.** Publication and deployment sit outside the epic's delegated
mandate; the owner **expressly authorised local deployment** and it was performed on 2026-11-15
(15:04–15:07) from the tree at `1dc2e382`. `make staging` then `install.sh` (`Verify: PASS — 11
cdad agents present after install`); **44 installer conflicts preserved** rather than overwritten —
the user-owned `model:` overlays and locally modified skill copies (e.g. opencode `cdad-reviewer`
keeps `openai/gpt-6.1-terra#medium`). At draft time the 17 changed `skills/…` files compared
byte-identical in the installed tree and both runtimes' `cdad-*` agents carry the new obligations.
`install.sh --check` **still exits 1** (15:07 run: skills-group drift on the symlinked runtime
paths and the `.agents` tree; agent drift/missing gone). **The check is not green and is not
claimed green**; its exact cause was not isolated. Logs:
`.cdad/orchestration/epic-019/local-deploy-*.log`.

**Technical debt detected.** **(1)** `install.sh --check` rc=1 after deployment: not green, cause
unresolved, and the installer's "preserved for explicit resolution" conflicts need explicit
re-registration of digests. **(2)** Full suite not run at feature closure (motive, selection and
limits above); the epic closure remains obliged to it by default. **(3)** The 38-test run has a
synthesised `tests.log`, not a pasted pytest session, and the reviewer's independent rerun timed
out — no reproduced green exists for this feature. **(4)** `systemPatterns.md` index note is
stale: it excludes ADR-012/016/025–030 as `Proposed`, but ADR-037/038/039 are also `Proposed` and
absent from the table (review-009's optional FYI; **no material defect** for 019-003 — the note,
not the table, needs updating). **(5)** 019-001 debt cleared by this feature: the draft-review
exemption now exists in `stage-2-specification.md` and in the 2→3 gate; still carried by 019-002:
the readiness events-table nit and PC-11's real-agent observation. **(6)** `deferred-hardening`
of the spec, with its disposition: *universal workflow or agent-compliance benchmark* — not
promised, observation only where explicitly committed; *automated semantic oracle or new
mechanical enforcement* — unjustified by the examined need, reconsider only on concrete
deficiencies; *unrelated consumer cleanup and exhaustive regression* — outside this bounded
change, relevant distribution protection and the existing test-evidence policy retained. No
deferral postpones PC-1..PC-6.

**Next feature in queue.** `019-002-effective-discovery-instructions` (order **3/3**; suspended,
to be resumed — it depends on 019-001 and 019-003, both now closed): coherent activation of the
019-001 design in canonical instructions and effective consumers, distribution verification,
observed five-case run of PC-11, and the permanent idle/done and orientation-view correction.
Publishing remains reserved to the owner.
```

## Draft 2 — `docs/progress.md` (three replacements)

**2a — replace the `## In progress` block (lines 5–14) with:**

```markdown
## In progress

**Active epic: `epic-019-discovery-dialogue` — plan approved by Pablo, 2026-11-15.**
`019-001-discovery-dialogue-contract` and `019-003-contract-verification-strategy` **cerradas el
2026-11-15** (detalle en `## Done`). Queda `019-002-effective-discovery-instructions` (orden
**3/3**, suspendida y **a reanudar**: depende de 019-001 y 019-003, ambas cerradas): activación
coherente del diseño en instrucciones canónicas y consumidores efectivos, verificación de
distribución, recorrido real con evidencia observada de los cinco casos de PC-11, y corrección
permanente de idle/done y de la vista de estado. No hay otra feature abierta. Publicar sigue
reservado al dueño; el despliegue local de 019-003 se hizo con autorización expresa (ver
`## Despliegue`). Plan: `docs/epics/epic-019-discovery-dialogue/plan.md`.
```

**2b — insert as the first bullet of `## Done` (before the `019-001` bullet):**

```markdown
- **019-003-contract-verification-strategy** (2026-11-15, epic 019 — orden **2/3**; **cerrada y
  desplegada en local con autorización expresa del dueño; no publicada**) — cada promesa declara
  su método de verificación **antes** de producir, y el ciclo enruta y cierra por ese método.
  **Producto:** `stage-2-specification.md` §"Verification strategy per promise" (propiedad, PCs,
  método `executable`/`contextual review`/`combined`, criterio de aceptación, evidencia esperada,
  límites; sin esquema nuevo) con la suficiencia en la revisión del borrador (PC-2: la exención
  registrada no es revisión ejecutada); plantilla de spec con la fila por promesa;
  `stage-3-tdd.md` §"Routing by verification method" (PC-3) y aceptación fijada antes de producir
  (PC-4); `stage-4-review.md` §"Closure evidence categories" (PC-5: dentro de límites declarados,
  fallida, faltante, contradictoria, no verificable — una limitación nunca asciende de categoría) y
  §"Semantic-only and mixed promises at review". Consumidores condicionados: `re-entry`,
  `handoff-prompts`, `state-detection`, `anti-patterns` (AP-5), `documentary-contracts`,
  `SKILL.md` del ciclo, `cdad-spec-and-test`, los cinco `sources/roles` afectados y los agentes
  generados de ambos runtimes. **Verificación:** nueve rondas independientes y ocho de corrección;
  `review-009` **sin bloqueos** (PC-1..PC-6; los dos hallazgos de `review-008` atendidos).
  Audit: verificadores examinados **conservados, sin tests nuevos** (protección adyacente, no
  oráculo semántico). Selección ejecutada: `pytest -q tests/test_cdad_generate.py
  tests/test_010_001_documentary_contracts.py tests/test_role_packet_render.py` → **38 passed,
  rc=0** (`c8fff61b`); `scripts/cdad-suite.py validate` → `status ok` (2068 nodeids, 248 módulos,
  31 entradas de mapa); distribución: **69 comparaciones, cero diferencias** (comparación propia
  del revisor contra la instalación aislada registrada). **Suite completa no realizada**
  (motivo: cambio acotado de instrucciones con sus superficies cubiertas por esos tres archivos;
  selección y límites arriba). **Límites declarados:** el revisor **no** acredita los 38 como
  corrida propia verde (su repetición terminó en timeout 143) y la igualdad de bytes no demuestra
  fidelidad semántica ni cumplimiento de agentes reales. **Despliegue local:** autorizado
  expresamente por el dueño (fuera del mandato delegado del epic); `install.sh` con
  `Verify: PASS — 11 cdad agents`, **44 conflictos preservados** (overlays `model:` del usuario y
  copias locales de skills); `install.sh --check` **sigue rc=1** por drift del grupo de skills —
  **no verde, no declarado verde**. **Deuda:** conflicto de digests sin resolución explícita;
  `tests.log` sintetizado (sin salida completa de pytest) y sin verde reproducido; nota de
  exclusión del índice de ADR en `systemPatterns` desactualizada (ADR-037/038/039 también
  `Proposed`; FYI opcional de `review-009`, sin defecto material); `deferred-hardening` del spec
  conservado con su disposición en el `closure.md` (benchmark universal de conducta, oráculo
  semántico automatizado, limpieza y regresión exhaustiva), sin aplazar PC-1..PC-6. **Cierra
  deuda de 019-001:** la exención de revisión del borrador ya está en `stage-2-specification.md`
  y en el gate 2→3. **Siguiente:** `019-002-effective-discovery-instructions` (reanudar).
```

**2c — insert as the first bullet of `## Despliegue` (before the `cbeab5f0` bullet):**

```markdown
- **019-003 desplegado en local el 2026-11-15, con autorización expresa del dueño** (publicar y
  desplegar están fuera del mandato delegado del epic 019; el dueño lo autorizó para esta feature).
  Origen: árbol local `1dc2e382`. `make staging` (12 archivos por runtime) y luego `./install.sh`:
  `Verify: PASS — 11 cdad agents present after install`, **340 archivos propios y 44 conflictos
  preservados** — los overlays `model:` del usuario y las copias locales de skills no se
  adoptaron (`PRESERVED — an overlay does not authorize adopting foreign bytes`), así que los
  modelos configurados siguen intactos. Observado en el borrador de cierre: los 17 archivos de
  `skills/` tocados por 019-003 están byte-idénticos en el árbol instalado y los agentes `cdad-*`
  de ambos runtimes llevan las obligaciones nuevas. **`./install.sh --check` sale rc=1**: el
  run de verificación (15:07) ya no reporta drift ni faltantes de agentes, solo drift del grupo de
  skills (rutas symlinkeadas de los runtimes y el árbol `.agents`); **la comprobación no está
  verde y no se declara verde**, y su causa exacta no quedó aislada. Consecuencia honesta: la
  instalación sirve el producto, pero el chequeo oficial sigue siendo un fallo abierto. Logs:
  `.cdad/orchestration/epic-019/local-deploy-{staging,dry-run,install,check,verified-check}.log`.
  Publicación: **no realizada**.
```

## Draft 3 — ADR: **yes, justified** (a new architectural rule with durable consequences)

Proposed file: `docs/adr/ADR-044-verificacion-por-promesa-metodo-declarado-rutas-y-categorias-de-cierre.md`

```markdown
# ADR-044: La verificación se declara por promesa, se enruta por su método y se cierra por categorías

- **Status**: Accepted (decisión delegada del dueño, epic-019, 2026-11-15; contrato aprobado
  `docs/specs/019-003-contract-verification-strategy/spec.md`, sha256 `969ff8e5…1a3cf`).
- **Date**: 2026-11-15
- **Confidence**: **Alta** en las instrucciones —nueve rondas de revisión independiente, la última
  sin bloqueos, con la distribución comparada—; **ninguna** sobre cumplimiento observado de
  agentes reales, que esta decisión no promete y que 019-002 debe observar por separado.
- **Origen**: `docs/specs/019-003-contract-verification-strategy/` (`spec.md` PC-1..PC-6,
  `review-009.md`, `test-audit.md`) y el cierre de 019-003.
- **Alcance**: instrucciones canónicas y sus consumidores efectivos. **No** reemplaza ADR-040
  (especialización documental por contrato) ni ADR-039 (verde atribuible): generaliza el criterio
  de ADR-040 de «unidad documental» a «cada promesa», y conserva de ADR-042 los defaults de
  evidencia por momento.
- **Supersede**: la lectura de que la revisión semántica es una excepción de las unidades
  documentales, fijada por la decisión directa del dueño registrada en
  `docs/epics/epic-019-discovery-dialogue/execution.md` §"Owner decision — verification of purely
  documentary products". Esa decisión sigue siendo historia válida de 019-001; su regla general
  pasa a ser la de este ADR.

## Contexto

El ciclo medía la aceptación con una sola vara: cada promesa verificada «por comportamiento»
antes de aceptar. Esa vara funciona cuando lo prometido es conducta observable y falla cuando el
producto es texto, documento o configuración: no hay comportamiento ejecutable que falle primero,
y fabricar un RED para simularlo produce evidencia de una verificación que no ocurrió. Al mismo
tiempo, las propiedades se leían como demanda automática ante cualquier invariante, y el cierre no
tenía categorías: faltaba, sobraba o se mezclaba evidencia, y una limitación declarada podía leerse
como logro. El dueño aprobó insertar 019-003 antes de la construcción de 019-002 para fijar la
regla antes de activar el diseño.

## Decisión

1. **El método se declara en el contrato, por promesa, antes de producir** (PC-1). Cada promesa
   observable declara su propiedad, sus postcondiciones numeradas, su método —`executable`,
   `contextual review` o `combined`—, su criterio de aceptación, la evidencia esperada y los
   límites de esa verificación. Sin esquema nuevo: prosa o celdas de la tabla de promesas. Hogar
   canónico: `skills/cdad-cycle/references/stage-2-specification.md` §"Verification strategy per
   promise"; la plantilla del spec sólo lo refleja.
2. **La suficiencia se revisa antes de aprobar y la exención no es revisión** (PC-2). La revisión
   independiente del borrador comprueba, por promesa, que la verificación propuesta puede
   establecer su aceptación. Una exención del dueño se registra con `exempted_by`, `delegated`,
   `requested_by` y `reason`, y no es una revisión ejecutada ni una afirmación de suficiencia.
3. **La producción se enruta por método** (PC-3). Comportamiento ejecutable pendiente: test-writer
   independiente primero y luego GREEN. Producción exclusivamente semántica: el implementador
   produce contra el contrato y las fuentes, y la promesa recibe revisión contextual independiente
   en Stage 4; ningún test se fabrica para sustituirla. Compromisos mixtos: ambas familias, cada
   una en su parte, sin sustitución. Hogar canónico: `stage-3-tdd.md` §"Routing by verification
   method".
4. **La aceptación se fija antes de producir** (PC-4). El productor no edita el criterio; un
   cambio necesario detiene el trabajo afectado y vuelve al procedimiento de aprobación.
5. **El cierre se informa por categorías excluyentes** (PC-5): dentro de los límites declarados,
   fallida, faltante, contradictoria o no verificable. Evidencia requerida ausente o compromiso
   incumplido impide acreditar; declarar una limitación no la convierte en éxito. Ningún método
   prueba más allá de su alcance: la igualdad de bytes no establece fidelidad semántica, una
   revisión favorable no reemplaza observaciones de ejecución comprometidas, y el éxito observado
   no establece conducta no examinada. Hogar canónico: `stage-4-review.md` §"Closure evidence
   categories".
6. **Los invariantes dejan de ser una demanda automática de propiedades.** Las campañas de
   propiedades corren sólo para los invariantes que el contrato aprueba como ejecutables; los
   invariantes conservados como restricciones revisables van a la revisión contextual. Si una
   campaña seleccionada resulta inviable, se detiene y vuelve a revisión y aprobación del
   contrato; nunca se dispensa en silencio.
7. **Una casa por regla, citada y no repetida** (PC-6). Cada regla tiene un archivo dueño y los
   consumidores —normal, ligero, paquetes, handoffs legacy y agentes generados— la citan por
   puntero. Una corrección aterriza una vez.

## Consecuencias

- Toda spec gana una columna de método por promesa; el costo es una fila más y el beneficio es que
  la aceptación deja de depender de la imaginación del test-writer o del criterio del productor.
- Un producto documental ya no necesita un RED ficticio, y un producto ejecutable no puede
  cerrarse con una revisión favorable.
- El productor pierde la posibilidad de ajustar el criterio a su salida; el cambio pasa por Stage 2.
- Los cierres honestos quedan obligados a nombrar la categoría y el límite; no declarar una
  limitación como logro es ahora la regla, no una cortesía.
- Límite declarado de esta decisión: verifica fidelidad, coherencia y entrega pertinente de las
  instrucciones, **no** cumplimiento universal de agentes. El benchmark observado, el oráculo
  semántico automatizado y la regresión exhaustiva quedan fuera como `deferred-hardening` del
  spec; observaciones de conducta sólo donde un compromiso explícito las exige (019-002).
- La verificación de distribución de este cambio se conserva (69 comparaciones, cero diferencias
  contra la instalación aislada registrada) sin convertirla en prueba de significado.
```

## Draft 4 — `docs/systemPatterns.md`: **yes, justified, one row only**

Insert as the last row of the "Decisiones vigentes" table (after the ADR-043 row):

```markdown
| `docs/adr/ADR-044-verificacion-por-promesa-metodo-declarado-rutas-y-categorias-de-cierre.md` | `vigente` | La verificación se declara por promesa en el contrato (método `executable`/`contextual review`/`combined`, aceptación, evidencia y límites), el ciclo enruta la producción por ese método y el cierre informa una categoría excluyente; las propiedades corren sólo para invariantes que el contrato aprueba como ejecutables y una limitación nunca asciende de categoría. | `architect`, `implementer`, `orchestrator`, `reviewer`, `test-writer`, `scribe` | `skills/cdad-cycle/references/stage-2-specification.md` §"Verification strategy per promise", `stage-3-tdd.md` §"Routing by verification method", `stage-4-review.md` §"Closure evidence categories" |
```

---

## Notes for the orchestrator (not part of the drafts)

1. **State file**: `docs/.cdad-state.json` carries `019-003` as `in-progress` and is dirty (`M`) — flipping it to `done` with `closed_at` + `closure_evidence` is yours, not mine; `019-002` should go back to active on resume.
2. **Closure content**: Draft 2b is the closure substance in Memory Bank form; the `deferred-hardening` block (debt item 6 in Draft 1) is the R6 carry the `closure.md` must materialise — none of the three deferrals postpones PC-1..PC-6.
3. **Two things I deliberately did not soften**: `install.sh --check` is a **failing** check after deployment (not green, cause not isolated), and the reviewer's abstention on the 38 tests stands as written.
4. **Language**: drafts are English per the packet; the surrounding entries are Spanish. Say the word and I re-emit them translated without changing a claim.
5. **No approval, no commit** — these are drafts. Strategic approval is the owner's; git execution is yours.