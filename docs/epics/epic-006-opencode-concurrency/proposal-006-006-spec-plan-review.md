# Propuesta — 006-006 revisión independiente de spec y plan antes de RED

> Investigación del architect (sesión independiente, solo lectura, 2026-10-18). Es una propuesta, no está aprobada; la evaluación del orquestador va al final.

## 1. Diagnóstico breve (verificado)

**a) La capacidad existe, está instalada y funciona.**
- `draft-plan` es un contract-kind de primera clase: `skills/cdad-cycle/scripts/cdad_packet.py:52-53` (`VALID_CONTRACT_KINDS`), con guarda de forja `:797-807` (exige `plan_version`, rechaza `approved-*` con versión de borrador) y pairing bidireccional `:815-829` (`draft-plan` ⇔ `plan-review`, solo rol reviewer).
- El par es reviewer-only y no autoriza implementación: `cdad_packet.py:4367-4377`.
- El borrador **no requiere aprobación**: `cdad_packet.py:1461-1464` y `:1533`; declarado en `skills/cdad-cycle/references/project-execution.md:92-93`.
- El rol/subfase está admitido: `cdad_packet.py:64` (`"reviewer": {"review", "plan-review"}`).
- La recepción/materialización lo soporta: `skills/cdad-cycle/assets/artifact-policy.json:9` (`"plan-review": "docs/specs/<feature>/"`) y `skills/cdad-cycle/scripts/cdad_result.py:699-700` (`_allowed_kinds` devuelve `{substage}` para `review`/`plan-review`).
- El procedimiento es fuente propia: `skills/cdad-cycle/packets/substages/reviewer-plan-review.md:1`; la plantilla de invocación (3 flags obligatorias) en `skills/cdad-cycle/references/handoff-prompts.md:543-568`.
- La skill viaja completa al producto instalado: `install.sh:361-363` (“El árbol cdad-cycle viaja completo —packets, references y scripts—”).
- Registro: `docs/adr/ADR-013-contrato-plan-borrador-revision-sin-aprobacion.md:44,67-69`.

**b) Pero está FUERA del recorrido principal. Esto confirma lo que decía la revisión previa: NO era una suposición.**
- El rol reviewer es “etapa 4 / diff contra la spec aprobada” en su contrato vigente: `sources/roles/reviewer.md:48` y en la tabla del ciclo `skills/cdad-cycle/SKILL.md:74`.
- El mapa del ciclo dice que el gate de Stage 2 es solo “spec.md approved by the user”: `SKILL.md:301`.
- Gate 2→3: solo self-review + aprobación, sin revisión independiente: `SKILL.md:341-348`.
- El recorrido de Stage 2 es brainstorm → spec draft → validación estructural del orquestador → aprobación del dueño: `skills/cdad-cycle/references/stage-2-specification.md:9-14, 42-44`.
- El **único self-review** es del *plan* (cobertura spec→tareas, placeholders, firmas) y vive bajo “Planning for complex features”: `stage-2-specification.md:98, 160-164`. Para una feature mediana (spec sin plan) no hay ni self-review.
- El exit gate de Stage 2 no lo nombra: `stage-2-specification.md:176-185`.
- En re-entry, el spec draft va directo a aprobación: `skills/cdad-cycle/references/re-entry.md:132-156`.
- Los agentes **generados** no lo nombran: `agents/cdad-reviewer.md`, `agents/cdad-architect.md`, `agents/cdad-orchestrator.md` → 0 ocurrencias de `plan-review`/`draft-plan` (grep). La carga legacy del reviewer es `cdad-cycle` only (`sources/roles/reviewer.md:16`), así que un reviewer en el camino legacy —que lee `SKILL.md:74`— nunca sabría que revisa borradores.
- El orquestador lo alcanza solo si ya sabe pasar las 3 flags; su fuente no lo nombra (`sources/roles/orchestrator.md:22-40`), aunque sí tiene la capacidad de orquestar (“preparar encargos, resolver desviaciones y replanificar dentro del mandato”: `:71-73`) y la prohibición correcta de duplicar la revisión (`:68-70`).

**c) La brecha de routing es una frontera declarada, no un accidente.** 004-003 fijó como fuente canónica de G4 al CLI y listó como consumidores solo `packets/roles/reviewer.md` y la plantilla de handoff —no `stage-2`, `SKILL.md` ni `re-entry`: `docs/specs/004-003-planning-procedures/spec.md:89`. Y declaró: “**cambios de procedimiento, no gates nuevos**” (`:82`). El recorrido real (T7) se ejercitó sobre el plan pendiente de 003-002: `docs/specs/004-003-planning-procedures/closure.md:23`, `.../dispatch-ledger.md:32`. Es decir: **capacidad integrada en el CLI, no en el ciclo.**

**d) El objeto es plan-céntrico.** El procedimiento dice literalmente “Review a PLAN DRAFT … and the plan object — not **only the spec**” (`reviewer-plan-review.md:1`), y el contrato exige `--plan-version` (`cdad_packet.py:797-807`). Una feature **mediana** (spec sin plan) no tiene objeto de esta revisión.

**e) El estado no lo representa.** El vocabulario de etapas es `discovery|specification|tdd|review|merge|idle` (`cdad_packet.py:4685`; `state-detection.md:24`). No hay dónde registrar “spec/plan bajo revisión”. El patrón vigente análogo es el artefacto + gate (como `review.md` en Gate 4→5: `SKILL.md:365`).

**f) Contradicción viva (categoría 4).** El mismo rol es “etapa 4 / diff” en su contrato (`sources/roles/reviewer.md:48`; `SKILL.md:74`) y a la vez tiene subfase `plan-review` con kind propio en el CLI y artefacto en la política de materialización (`cdad_packet.py:64`; `artifact-policy.json:9`; `cdad_result.py:699-700`). Hay regla con dueño en el CLI y sin dueño en el ciclo.

**g) Observación fuera de alcance (no la toco).** La cláusula de familia del reviewer sigue en `SKILL.md:77-89` y `sources/roles/reviewer.md:50-55`, mientras el dueño retiró ese requisito (A-5; `docs/epics/epic-006-opencode-concurrency/plan.md:260,268`). Mi diseño **no** añade exigencia de proveedor/modelo/familia; eso pertenece a 006-003 y queda excluido.

---

## 2. Alcance mínimo y exclusiones

**Entra (delta mínimo sobre CDAD actual):**
1. **Ampliar el objeto** de la revisión inicial (mismo rol, misma subfase, sin nombres nuevos) para que sea el **objeto de especificación**: intención original + restricciones y decisiones aplicables + spec + plan (cuando existe) + contratos/interfaces + capacidades necesarias para ejecutar y obtener evidencia. Deja de ser “plan contra spec”.
2. **Enrutarlo en el recorrido principal**: una subfase en `stage-2-specification.md` (entre la re-entry del draft y la aprobación), y su criterio en Gate 2→3.
3. **Reconciliar los consumidores**: rol reviewer (`sources/roles/*.md` → `make agents`), tabla §2 y §5 de `SKILL.md`, `re-entry.md`, plantilla de handoff.
4. **Cerrar identidad y proporción**: revisión sobre borrador no aprobado; el dictamen no aprueba ni habilita construcción; corrección → nueva versión del borrador → re-review focal; sesión nueva para la revisión final; tarea chica → recorrido chico.

**Exclusiones explícitas:**
- No se crea subfase, agente, stage ni kind nuevos (se reutiliza `plan-review` + `draft-plan`).
- No se toca la autoridad: la aprobación sigue siendo del dueño (o delegada bajo pedido explícito y vigente): `stage-2-specification.md:46-85`.
- No se exige proveedor/modelo/familia (A-5).
- No se cambia el aislamiento del test-writer ni su mecanismo; solo se declara que el dictamen **no** es insumo suyo.
- No se reabren PD-5/PD-6 de 004-003 (equivalencia de corridas) ni el transporte/delegación ni la política de Bash.
- No se toca 006-003 en curso, ni los archivos sin trackear de otro agente.

---

## 3. Decisiones recomendadas y alternativas

| # | Decisión recomendada | Alternativa (y por qué no) |
|---|---|---|
| D1 | **Reutilizar `plan-review`** sobre el rol reviewer (no un agente/subfase nuevos). El CLI ya lo admite (`cdad_packet.py:64`) y 004-003 lo probó (PD-4). | `spec-review`/agente “planner” nuevo: viola “no crear por nombre”; churn de enums + schemas + oráculos. |
| D2 | **Un solo dueño del “qué revisar”**: `packets/substages/reviewer-plan-review.md`, generalizado al objeto de especificación; los demás referencian. | Dos reglas (una para spec-only, otra para spec+plan): dos dueños → deriva. |
| D3 | **Conservar los nombres** `plan-review` y `draft-plan`, generalizando el significado (`plan_version` = versión del borrador revisado). **Deuda de nombre declarada.** | Renombrar `draft-plan`→`draft-specification`: semánticamente más limpio, pero toca el enum cerrado (`cdad_packet.py:52-53,805-829`), 2 enums de schema (`assets/packet-request.schema.json:13`, `assets/result-receipt.schema.json:13`), la plantilla y los oráculos de 004-003 → costo de coordinación por una ganancia nominal. Si el dueño prefiere el nombre exacto, es un cambio acotado y lo hago; por defecto, mínimo. |
| D4 | **Sin stage nuevo**: la revisión vive dentro de `current_stage: specification` y se representa por el artefacto + el recibo del paquete; Gate 2→3 gana un criterio (espejo de `review.md` en Gate 4→5, `SKILL.md:365`). | `specification-review` como stage: expande vocabulario y schema sin ganancia de conducta. |
| D5 | **Revisión sobre borrador no aprobado, sin dependencia circular**: se apoya en el `draft-plan` que ya “no requiere aprobación” (`cdad_packet.py:1461-1464`; `project-execution.md:92-93`). El dictamen **no** es aprobación ni habilita construcción; la construcción sigue exigiendo el pin `stage_history`/`specification` (`re-entry.md:147-155`). | Pedir “aprobación ficticia” para poder revisar: circular y prohibido. |
| D6 | **Identidad y trazabilidad reutilizando lo vigente**: el `REQUEST.json` del borrador congela `contract.sha256` + `plan_version`; la corrección del architect produce versión nueva → la revisión anterior no cubre esos bytes → **re-review focal** que comprueba bloqueantes y consecuencias (calibración, regla 4: `stage-4-review.md:28-32`). Ninguna aprobación previa se atribuye a bytes cambiados (mismo principio que el pin `contract_sha256`, `re-entry.md:148-152`). | Mecanismo de identidad nuevo: duplicaría el vigente. |
| D7 | **Proporcional, no omitible**: profundidad proporcional al riesgo/tamaño; una corrección mecánica no fuerza re-review separada (calibración, regla 6: `stage-4-review.md:37-39`); spec y plan son **un solo objeto**, una sola ronda. | Eximir la revisión en features chicas: reintroduce AP-13 (cascada de basura) justo donde es barato prevenirlo (`SKILL.md:124-128`). |
| D8 | **Revisión final en sesión nueva** (el despacho por paquete ya la da; se declara), sin exigir familia; el reviewer final puede cuestionar insuficiencias del contrato (loop ya existente Stage 4→2: `stage-4-review.md:162`). | Reutilizar la sesión de la revisión inicial: pierde independencia. |
| D9 | **006-006 dentro de epic-006**, vía enmienda 006, después de lo pendiente. | Epic nuevo: ceremonia de plan+autoridad sin necesidad; epic-006 ya absorbió enmiendas de metodología (003/004/005: `plan.md:273-283, 287-309, 311-326`). |
| D10 | **Recepción real** = el inicio de la próxima feature pendiente que se especifique. | Usar 006-005/006-004 si el orden se invierte (ver §8, duda W1). |

---

## 4. Ciclo propuesto: unidades, dependencias y aceptación

**Secuencia objetivo (a evaluar):** architect entrega spec (+plan) → **reviewer revisa el objeto de especificación en sesión independiente** → architect corrige bloqueantes pertinentes → re-review focal si corresponde → aprobación del dueño → RED/GREEN → revisión final (sesión nueva).

| Unidad | Contenido | Depende de | Aceptación (observable) |
|---|---|---|---|
| **U1 — Objeto y regla canónica** | Generalizar `packets/substages/reviewer-plan-review.md:1` al objeto de especificación (intención, restricciones/decisiones, spec, plan si existe, contratos/interfaces, capacidades); definir el borrador revisado como “plan si existe, spec si no”; declarar la deuda de nombre `draft-plan`. | — | La fuente dice una sola vez qué se revisa y con qué criterios de juicio; un consumidor la referencia sin copiarla. |
| **U2 — Recorrido principal y gate** | Subfase en `stage-2-specification.md` (tras la re-entry del draft, antes de aprobar): preparar/despachar el paquete `plan-review`, recibir dictamen, rutear bloqueantes al architect, exigir re-review focal, recién entonces aprobar. Criterio en Gate 2→3 (`SKILL.md:341-348`) y mapa del ciclo (`:296-302`); sección “Reviewer — draft review” en `re-entry.md` junto a `:132-156`. | U1 | El recorrido habitual llega a la revisión **antes** de RED; el dictamen no aprueba (`sources/roles/orchestrator.md:68-70` se mantiene). |
| **U3 — Rol, recepción e identidad de cierre** | Reconciliar `sources/roles/reviewer.md:48` (etapas/`Does`) y la tabla §2 de `SKILL.md:74`; generalizar la frase “qué revisar” que ya vive en `packets/roles/reviewer.md`; `make agents`. Verificar materialización del kind `plan-review` con target declarado. Declarar la revisión final en sesión nueva (`stage-4-review.md`) y la proporción del caso chico. | U2 | El producto instalado (agentes generados + skill) contiene la conducta; `prepare`/`receive`/`materialize` cierran el ciclo del artefacto. |

Dependencias: U1 → U2 → U3 (lineal). Nada exige fan-out: **una** ronda de revisión por feature, no una por documento.

---

## 5. Fuentes canónicas y consumidores afectados

| Regla | Dueño único | Consumidores a reconciliar |
|---|---|---|
| Qué se revisa y con qué criterios | `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` | `sources/roles/reviewer.md`; `handoff-prompts.md:543-568` |
| Cuándo ocurre + Gate 2→3 | `skills/cdad-cycle/references/stage-2-specification.md` (§ y exit gate) | `SKILL.md` (mapa `:296-302`, gate `:341-348`, tabla §2 `:74`, materialización §5 `:184-187`); `re-entry.md` |
| Contrato de rol | `sources/roles/reviewer.md` | agentes generados (`make agents`); tabla §2 compuesta |
| Borrador no aprobado + pairing | `skills/cdad-cycle/scripts/cdad_packet.py` (`:52-53,64,797-829,1461-1464`) | enums en `assets/{packet-request,result-receipt,active-packet}.schema.json:13` |
| Recepción/materialización del dictamen | `scripts/cdad_result.py:699-700` + `assets/artifact-policy.json:9` | — |
| Proporcionalidad | `stage-4-review.md:5-54` (dueño canónico único) | reviewer (puntero, ya existente: `:40-42`) |

Nada de esto queda en un ADR o referencia que nadie carga: el criterio llega por el paquete (substage), por la skill instalada (`install.sh:361-363`) y por los agentes regenerados.

---

## 6. Validación y recepción real

**Pruebas ejecutables (comportamiento ejecutable)**
- **E1:** render de un paquete `reviewer/plan-review` con `--contract-kind draft-plan` sobre un **spec borrador sin plan** (producto instalado, sin repo fuente) → rc=0, sin marca de aprobación, con el procedimiento del substage en el render. Extiende el test de render instalado existente (`tests/test_004_003_t2_plan_review.py`).
- **E2:** materialización del recibo kind `plan-review` para reviewer/plan-review en el target declarado → aceptado; el mismo recibo para otro rol/subfase → rechazado (`cdad_result.py:681-700`, tabla cerrada).
- **E3 (regresión):** negativos de pairing vigentes (draft fuera de plan-review; plan-review sobre aprobado; draft reviewer-only) siguen verdes (`cdad_packet.py:815-829,4367-4377`).
- **E4:** identidad — el `REQUEST.json` congela el sha/versión del borrador revisado; una versión posterior del mismo path no se considera revisada (fuerza re-review).

**Drift (solo frases, para detectar deriva documental)**: que `stage-2-specification.md` declare la subfase y el criterio del exit gate; que Gate 2→3 lo incluya; que `sources/roles/reviewer.md` nombre la revisión de borrador y que el agente generado la contenga tras `make agents`.

**No ejecutable (declarar honestamente)**: “el orquestador realmente prepara el paquete en sesión viva” y “la revisión fue proporcional en una tarea chica” son criterios de conducta que se verifican por **revisión de la recepción real**, no por suite. No inventar una suite de frases para simularlo.

**Recepción real**: el **inicio de la próxima feature pendiente** que se especifique (spec+plan borrador). Registrar: paquete, dictamen, bloqueantes, correcciones y la re-review sobre la versión corregida. Distinguir explícitamente **implementación disponible** (hoy: render, pairing, materialización) de **eficacia observada** (una spec/plan real que atrapó un defecto material antes de RED). **Criterio de éxito**: el defecto habría costado ≥1 ciclo RED/GREEN si pasaba; si no atrapa nada, se declara igual (la revisión confirmada barato también vale).

**Regresión proporcional**: focales de la familia plan-review + packet/receipt; **una** suite completa al cierre de código, reutilizando la evidencia registrada cuando el árbol no cambió (`stage-4-review.md:139-154`).

---

## 7. Ubicación en la planificación vigente

- Backlog real: `.cdad-state.json` → `epic_features` = 006-001 `done`, 006-002 `done`, 006-003 `in-progress`, **006-005 `queued`**, **006-004 `queued`**. `git grep "006-00[6-9]"` → **0 resultados**: el identificador **006-006 está libre** y no presupongo nada.
- El plan del epic ya admite enmiendas de metodología: 003 (decisiones vigentes, `plan.md:273-283`), 004 (paridad del recorrido nativo, `:287-309`), 005 (principio general antes que específico, `:311-326`).
- **Recomendación:** **feature `006-006` dentro de epic-006**, vía **enmienda 006** que declare el cambio de procedimiento (sin gates nuevos más allá del criterio añadido a Gate 2→3), ordenada **después** de 006-005 y 006-004 como pide el dueño. Alternativa: epic nuevo (007) si el dueño prefiere no seguir ampliando la temática de epic-006; costo: plan + autoridad propios.
- El ciclo **no concede autoridad nueva**: la aprobación sigue siendo del dueño (`stage-2-specification.md:46-85`) y el dictamen es técnico.

---

## 8. Dudas materiales

- **W1 — Orden vs recepción.** El encargo dice “después de lo pendiente” (006-005 y 006-004) y a la vez propone la recepción en “el inicio de 006-005 o 006-004”. Ambas no pueden cumplirse. Recomiendo: si se quiere recepción barata sobre trabajo real, ubicar 006-006 **inmediatamente después de 006-003** y recibir sobre el inicio de 006-005; si se respeta “después de lo pendiente”, la recepción espera a la próxima feature y se registra como “disponible, eficacia no observada”. **Necesito tu decisión.**
- **W2 — Nombre.** ¿Se conserva `draft-plan` con deuda declarada (mínimo) o se renombra a `draft-specification` (limpio, con churn en enums/schemas/oráculos de 004-003)?
- **W3 — Caso trivial.** ¿La revisión inicial es siempre obligatoria con profundidad proporcional (mi recomendación), o admite exención explícita del dueño, registrada?
- **W4 — Familia vs A-5.** La cláusula de familia sigue en `SKILL.md:77-89` y `sources/roles/reviewer.md:50-55`. ¿006-003 la elimina (y este ciclo solo evita añadirla), o hay que coordinarlo para no dejar dos enunciados?
- **W5 — Nombre del artefacto.** ¿`plan-review.md` en `docs/specs/<feature>/` (coherente con el kind y con `review.md`)? Hay que fijarlo con el target declarado en la autorización de materialización.
- **W6 — Criterio del gate.** ¿Gate 2→3 exige “existe revisión y no hay bloqueantes sin resolver o descartados con razón” (espejo de `SKILL.md:366`)? Y si el mecanismo de revisión no está disponible en un runtime, ¿el gate falla cerrado o admite exención declarada?

---

## Recomendación concreta (lista para revisar, sin abrir TDD)

Abrir **`006-006-revision-independiente-de-spec-y-plan`** dentro de **epic-006** (enmienda 006, `plan.md`), **después de 006-005 y 006-004**, con **tres unidades** (objeto → recorrido/gate → rol/recepción) y **sin** subfase, agente, stage ni kind nuevos:

1. Generalizar el objeto en `packets/substages/reviewer-plan-review.md` al **objeto de especificación** (incluye la spec siempre; el plan cuando existe).
2. Enrutarlo en `stage-2-specification.md` (subfase + exit gate) y en Gate 2→3, reconciliando `SKILL.md`, `re-entry.md` y `handoff-prompts.md`.
3. Reconciliar el rol reviewer (`sources/roles/*.md` → `make agents`) y verificar recepción/materialización del kind `plan-review`.

Conservando: aprobación del dueño, revisión ≠ aprobación, borrador no aprobado sin circularidad, re-review focal sobre la versión corregida, revisión final en sesión nueva, proporcionalidad por calibración vigente, y **ninguna** exigencia de proveedor/modelo/familia (A-5).

**Criterio principal cumplido:** es el delta mínimo que lleva una capacidad ya construida, ya probada y ya instalada al recorrido habitual, donde previene AP-13 antes de RED —menos retrabajo, sin rondas extra por documento y sin tocar el trabajo en curso.

**Antes de convertirlo en feature necesito W1 (orden/recepción) y W2 (nombre).** Con eso, el siguiente paso es que el architect redacte la spec de 006-006 y su plan (si resulta compleja), y que **esa misma spec pase por la revisión independiente que la feature introduce** — la primera recepción posible.

---

## Evaluación del orquestador (2026-10-18)

De acuerdo con el diagnóstico y con el delta mínimo: la capacidad existe (`plan-review` + `draft-plan`), pero quedó fuera del recorrido principal. Precisiones:

- **Spec sin plan.** Hoy `draft-plan` exige `--plan-version` y el procedimiento revisa un *plan*. Que una spec sin plan sea objeto de revisión es un cambio de comportamiento del CLI, no solo de texto. U1/U3 deben incluirlo con prueba ejecutable (E1 ya lo cubre).
- **W1 (orden/recepción).** Propuesta: mantener 006-005 primero, porque es urgente, y revisar su spec y plan con la capacidad vigente tal como está (`plan-review` sobre `draft-plan`; 006-005 tiene plan). Eso da recepción real y datos para diseñar 006-006 sin invertir el orden. 006-006 va después de 006-004.
- **W2.** Conservar `draft-plan`/`plan-review`, con la deuda de nombre declarada.
- **W3.** Obligatoria y proporcional; la exime solo el dueño, de forma explícita y registrada.
- **W4.** La retira 006-003 (U5', en curso); este ciclo solo evita reintroducirla.
- **W5.** `plan-review.md` en `docs/specs/<feature>/`.
- **W6.** El gate exige revisión existente y bloqueantes resueltos o descartados con razón. No hay exención por runtime: el handoff a sesión nueva está siempre disponible.
