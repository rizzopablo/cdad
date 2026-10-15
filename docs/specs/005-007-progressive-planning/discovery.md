The discovery report is complete. The transport file is written (37,658 B, sha256 `b58b707f412f3e00ef0f3cb2d5db014704832d204fcb28c42b26dc58f33245da`) and the repo is unchanged (`git status --short` clean). Below is the report — **exactly the same bytes** as `/tmp/opencode/discovery-005-007.md`.

---

# Discovery — 005-007-progressive-planning

- **Rol:** architect (etapa 1, subetapa `discovery`) — solo lectura, no edita el repo.
- **Paquete:** `005-007-progressive-planning-architect-discovery-001` (packet_version 1).
- **Contrato:** `docs/epics/epic-005-real-operation/plan.md` (fila 9, `:42`) ·
  sha256 `b22bc687e327c8524ab55f44ae8df65b06076bcc628e373b5e274a54906bec16`.
- **Insumo principal:** `docs/specs/005-007-progressive-planning/discovery-inputs.md`.
- **Alcance:** mapeo técnico y líneas de brainstorm. **No se propone el contrato**
  (eso es la subetapa `draft`); los hechos no verificados se marcan `VERIFY`.
- **Repositorio:** rama `codex/epic-005-real-operation`, árbol limpio
  (`git status --short` sin salida). No se escribió nada en el repo.

---

## 0. Resumen ejecutivo

La mejora que el dueño pide **no es una capacidad nueva**: los tres niveles
(epic/feature/tarea), el bloque canónico `plan-tasks` con `Consumes/Produces` y
dependencias, el modo `plan-review` del reviewer y la regla de reintentos **ya
existen y están instalados**. Lo que falta es: (a) un **hogar canónico** en la
skill instalada para la regla «objetivo y dependencias completos; detalle solo
para la tanda próxima» —hoy vive solo como borrador de diseño en el epic-004—;
(b) **quitar la contradicción mecánica**: el validador de `prepare` exige hoy
el mismo nivel de detalle (validación por tarea) para **todas** las tareas
declaradas, lo que vuelve inválido un plan de detalle progresivo; y (c) alinear
las **plantillas** con el resultado (la spec debe partir del recorrido de uso y
su aceptación debe ser comportamiento, no `%` de cobertura). La medición de
contexto por rol (005-002/005-003) permite **estimar clases y volumen de
entradas sin inventar tokens**; la aceptación de uso es una capa distinta de
TDD/E2E y en esta feature queda mayormente **declarada como pendiente con
responsable** porque requiere despliegue (reservado al dueño).

---

## 1. Entidades verificadas (archivo:línea)

### 1.1 Lo que existe hoy y se reusa

**Los tres niveles, dependencias, Consumes/Produces y plan-review (004-003).**

- Los tres niveles con «qué debe quedar definido / qué no se exige anticipar»:
  `docs/epics/epic-004-single-source-planning/planning-contract-draft.md:30-39`
  (tabla Epic / Feature-ciclo / Tarea). Allí mismo, la regla del borrador:
  «Detallar la próxima tanda y sus contratos exactos» (`:55-56`) y el nivel
  Feature declara «contexto de próxima tanda» (`:33`).
- Procedimiento de planificación en 8 pasos: `planning-contract-draft.md:43-60`.
- Ficha mínima de unidad ejecutable: `planning-contract-draft.md:62-86`
  (ID, resultado, alcance, Consume/Produce, dependencias, archivos, entradas de
  contexto por rol, decisiones autónomas, evidencia al re-entry, estimación,
  verificación, incertidumbres/criterio de replanificación).
- **Bloque canónico `plan-tasks`** (declaración única del formato):
  `planning-contract-draft.md:87-138`. Campos a nivel de plan: `tasks` y
  `validation_strategy`; por tarea: `id`, `produce`, `consume`, `depends_on`,
  `parallel`, `files`, `focal_tests`, `observable_checks`, `regressions`,
  `integration_gate`, `owner` (`:95-101`). Referencia de estrategia común con
  el literal `@validation_strategy` (`:99-101`).
- Criterios de revisión de plan (cobertura, completitud operativa, contexto
  suficiente, frontera útil, contratos compatibles, dependencias honestas,
  paralelismo seguro, aislamiento de roles, verificación independiente,
  viabilidad, supervisión proporcional, **costo de coordinación**, recuperación):
  `planning-contract-draft.md:140-160`.
- **Contrato aprobado 004-003** (lo instalado): `docs/specs/004-003-planning-procedures/spec.md`.
  Superficies: paquete de revisión de plan (`:26`), `contract_kind` `draft-plan`
  (`:27`), chequeo de equivalencia en re-entry (`:28`), plan de validación por
  unidad en el archivo de plan (`:29`). Postcondiciones PD-1..PD-13 (`:31-57`);
  invariantes (`:59-67`); criterios de aceptación (`:69-78`); cambios de
  procedimiento G1–G5 con su fuente canónica única (`:80-91`).
- **Tareas 004-003** (T1–T7 + plan de validación por unidad y trazabilidad):
  `docs/specs/004-003-planning-procedures/plan.md:15-25,45-56`. El bloque
  `plan-tasks` de 004-003 existe y fue validado por el validador del CLI
  (`plan.md` del epic-004 `:11`).
- Requisitos de orquestación proporcional que 004-003 incorporó:
  `docs/specs/004-003-planning-procedures/efficient-orchestration-requirements.md`
  (citado en `planning-contract-draft.md:185-189`).

**El bloque canónico que consumen los paquetes (implementación real).**

- Tipos de contrato válidos: `skills/cdad-cycle/scripts/cdad_packet.py:52`
  (`{"approved-epic-plan","approved-feature-spec","draft-plan"}`).
- Subfases por rol (incluye `plan-review` en reviewer):
  `cdad_packet.py:53-59`.
- Parseo obligatorio del bloque `plan-tasks` (falla cerrado si falta o está
  malformado): `cdad_packet.py:2883-2942` (regex `:2883-2886`, token `:2889`,
  resolución `:2901-2942`).
- Checks mecánicos productor/consumidor, contrato incompatible, ciclo, y
  paralelismo inseguro: `cdad_packet.py:2945-3060`.
- **Presencia del plan de validación por tarea (PD-8)**: `cdad_packet.py:3063-3105`
  — exige por tarea `focal_tests` (con código) u `observable_checks` (sin
  código), `regressions`, `integration_gate` y `owner`.
- Render del paquete atado a una tarea del plan: `plan_task` (005-003 T6 PD-10):
  `cdad_packet.py:3108-3209`; ruta del plan
  `PLAN_RELPATH_TEMPLATE = "docs/specs/{feature_id}/plan.md"` (`:3114`).
- Subfase instalada del reviewer para revisar un borrador:
  `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` (revisa
  intención + restricciones + plan; separa validación estructural de juicio
  semántico; no aprueba). Invocación con los tres flags de contrato:
  `skills/cdad-cycle/references/handoff-prompts.md:542-567`.
- Tests vigentes que ejercitan el contrato de plan:
  `tests/test_004_003_t1_draft_contract.py`, `test_004_003_t2_plan_review.py`,
  `test_004_003_t3_plan_checks.py`, `test_004_003_t4_validation_fields.py`,
  `test_004_003_t5_reentry_equivalence.py`.

### 1.2 Tamaño de unidad y regla de reintentos vigentes

- **Tamaño de unidad (la regla hoy):** `skills/cdad-cycle/references/stage-2-specification.md:102-104`
  — «the task is the smallest unit that closes in its own mini TDD cycle … and
  that a reviewer could reject without rejecting its neighbor»; setup/config
  dentro de la tarea que lo necesita (`:104`). Estructura de la tarea
  (`Files`, `Consumes/Produces`, `Validation plan`, `TDD steps`): `:106-113`.
  Variantes por tamaño (trivial/medio/complejo → `plan.md`): `:86-92`.
- **Regla de «unidad despachable»** (reconciliación de 003-007): el encargo
  lleva **una** unidad —una tarea del plan **o** una subfase TDD, nunca dos
  subfases— con sus postcondiciones, cada una trazada a ≥1 test y un diff
  acotado; el ejemplo RED/GREEN como despachos separados la satisface:
  `sources/roles/orchestrator.md:84-89`; postcondición P10:
  `docs/specs/003-007-living-continuity/spec.md:140-150`; test:
  `tests/test_003_007_t4_atomic_unit_rule.py` (señales y coherencia fuente↔agentes).
- **Regla de reintentos (fuente canónica única):**
  `skills/cdad-cycle/references/re-entry.md:79` — «a retry responds to a new
  hypothesis or new information; an identical repetition, an absence of
  progress, a blocked environment or a disproportionate cost triggers a strategy
  review, reconciled with the standing two-attempt rule; there are no unlimited
  retries», sin saltar controles ni declarar éxito sin evidencia.
  Consumidores que la referencian (sin copiarla): `skills/cdad-cycle/SKILL.md:288`
  (conducta del orquestador) y `skills/cdad-cycle/references/stage-3-tdd.md:29-39`
  (run budget: máximo 2 corridas sin convergencia → STOP y escalar).
- **Regla de equivalencia de evidencia** (evita repetir suite completa): fuente
  canónica `re-entry.md:67-77`; consumidores `stage-3-tdd.md:46-63`
  (§«Test evidence policy», dueño único) y `stage-4-review.md` (por referencia).
- Dónde el orquestador recibe/reenvía el trabajo:
  `sources/roles/orchestrator.md:127-134` (re-entry wiring) y `:19-58` (intake).
- Adaptadores de runtime (mecanismo, sin copiar el contrato de rol):
  `sources/agents/adapters/opencode.md` y `sources/agents/adapters/claude-code.md`.

### 1.3 Dónde vive —o falta— el texto de «objetivo y dependencias completos; detalle solo para la tanda próxima»

- **Vive hoy como borrador de diseño, no como regla instalada:**
  `planning-contract-draft.md:33` (nivel Feature = «contexto de próxima tanda»),
  `:55-56` (paso 6: «Detallar la próxima tanda y sus contratos exactos»); y
  `docs/epics/epic-004-single-source-planning/plan.md:274-277` («Detalle fino
  solo para la próxima tanda; tareas futuras pueden declarar incertidumbre con
  dueño y condición de resolución, sin entrar así a construcción»).
- **Vive como contrato de feature en la fila 9 del epic-005:**
  `docs/epics/epic-005-real-operation/plan.md:42` («planificación progresiva
  (objetivo y dependencias completos; detalle solo para la tanda próxima) y
  tamaño de unidad que no pague planificación, sesiones y revisión sin avance
  suficiente») y el ajuste del dueño `:70-76`.
- **NO vive en la skill instalada:** `stage-2-specification.md` no contiene la
  regla; los paquetes (`packets/`), el `SKILL.md` y el validador tampoco la
  enuncian. Búsqueda dirigida: `grep -rni "progresiv|próxima tanda|detalle solo"`
  solo encuentra el plan del epic-005, el epic-004 y el borrador de contrato.
- **Contradicción mecánica verificada:** `cdad_packet.py:3063-3105` exige
  `focal_tests`/`observable_checks` + `regressions` + `integration_gate` +
  `owner` para **cada** tarea del bloque. Un plan de detalle progresivo que
  declare tareas futuras con solo objetivo+dependencias+incertidumbre
  **fallaría `prepare`**; hoy no existe un estado «planificada pero no
  detallada» ni un marcador de «tanda próxima». Esto es el **criterio que
  falta** y su consumidor: el propio validador de paquetes.

### 1.4 Plantillas y rol del architect en la spec

- Plantilla de spec: `skills/cdad-cycle/assets/spec-template/spec.md`. Empieza
  por **Signature** (`:17-21`) y su criterio de aceptación incluye
  «Line coverage … ≥ X%» (`:41`). → Contradice «la spec parte del recorrido de
  uso en vez de una firma de función» y «su aceptación es el comportamiento, no
  un porcentaje de cobertura».
- Plantilla de auditoría de tests: `skills/cdad-cycle/assets/spec-template/test-audit.md`.
- Plantilla de plan **de epic**: `skills/cdad-epic/assets/epic-plan-template.md`
  (decomposition table, cross-feature contracts, acceptance criteria).
- Plantillas de Memory Bank / ADR: `skills/cdad-cycle/assets/memory-bank-templates/`,
  `skills/cdad-cycle/assets/adr-template/ADR.md`.
- **No existe plantilla de plan de feature**: el único `*plan*` de assets es el
  de epic. Los planes de feature reales (005-006/005-008/005-009/005-010) son
  markdown sin asset, con la ficha + el bloque `plan-tasks` escritos a mano
  (ej.: `docs/specs/005-006-guided-project-start/plan.md:31-120,122-187`).
- **Nota de ruta:** el encargo menciona «los templates de `docs/assets`»;
  `docs/assets/` **no existe** (`ls: cannot access`). Las plantillas viven en
  `skills/*/assets/`. Se registra como corrección de superficie.
- **Rol del architect en la spec** (lo que la spec debe respetar): el architect
  es read-only y no aprueba su propuesta; produce spec/plan como TEXTO FINAL y
  el orquestador/usuario los materializa (ADR-003):
  `sources/roles/architect.md:54`; `stage-2-specification.md:90-113`
  (plan.md para features complejas, aprobado junto con la spec).
- El patrón «spec desde el recorrido de uso» ya se usó **una vez** sin
  formalizarse: 005-006 define su aceptación como comportamiento observable en
  recorridos R1/R2/R3 (`docs/specs/005-006-guided-project-start/spec.md:36-60`)
  y su T5 separa checks deterministas del recorrido real
  (`005-006/plan.md:103-120`). Falta generalizarlo en la plantilla/regla.

### 1.5 Límites del epic que la spec debe respetar (verificados)

- Dentro/fuera del epic: `docs/epics/epic-005-real-operation/plan.md:22` (dentro:
  «planificación progresiva») y `:25-27` (fuera: CI, sandbox, plataforma
  universal de jobs, etc.).
- Restricciones duras del encargo: `discovery-inputs.md:128-138` (sin agente
  planner obligatorio, sin perfiles de modelo nuevos, sin aislamiento por repo
  para todos los agentes, sin servicios permanentes, sin OnlyOffice ni UI nueva
  dentro de esta feature; conservar mandato, revisión independiente, contexto
  por rol y validación proporcional; la replanificación mantiene trazabilidad y
  no modifica contratos ya despachados sin reconciliación).
- Criterios de aceptación del epic (incl. aceptación conjunta del consumidor):
  `plan.md:87-108`.
- Fronteras declaradas por la dirección del dueño:
  `findings/agent-operation-strategy-2026-10-11.md:183-195` (005-007: «No
  scheduler, agente planner obligatorio ni plataforma de tests de UX»).

---

## 2. Diagnóstico: qué criterio falta, dónde vive y qué consumidor lo recibe

1. **Detalle progresivo — criterio ausente del producto instalado y contradicho
   por el validador.** La regla vive solo en el borrador del epic-004
   (`planning-contract-draft.md:33,55-56`) y en la fila del epic-005; el
   validador instalado (`cdad_packet.py:3063-3105`) obliga a detalle uniforme.
   **Consumidores que deben recibirlo:** el validador de `prepare`, el reviewer
   `plan-review`, el architect (draft) y el orquestador (intake).
2. **Tamaño de unidad — criterio cualitativo sin costo total.** La regla vigente
   (`stage-2-specification.md:102-104`) cierra en «mini TDD cycle»; no incorpora
   el criterio de costo total (planeación+sesión+review+integración) que pide
   `discovery-inputs.md:50-52`. El borrador del epic-004 (criterio «Costo de
   coordinación», `planning-contract-draft.md:155`) ya lo enuncia para revisión,
   pero no está conectado a la decisión de tamaño.
3. **Plantillas desalineadas.** `assets/spec-template/spec.md:17-21,41` ancla en
   firma + cobertura; falta una plantilla de plan de feature. **Consumidor:**
   el architect (draft) y los paquetes.
4. **Regla de reintentos: ya existe y es correcta; el trabajo es de coherencia,
   no de redacción nueva.** Fuente única `re-entry.md:79`, consumidores
   `SKILL.md:288` y `stage-3-tdd.md:29-39`. Debe evitarse una segunda copia
   (invariante de fuente única, 004-003 `spec.md:55`). El delta útil: ligarla a
   la **unidad** (un reintento sin información nueva sobre una unidad →
   replantear la unidad), que hoy no se dice a nivel de plan.
5. **Aceptación de uso sin receta ni responsable.** `discovery-inputs.md:82-102`
   pide una receta mínima; el repo tiene precedentes de recorrido instalado
   (`docs/specs/004-003-planning-procedures/plan.md:23` T7; 005-009 PD-10) pero
   no una plantilla de aceptación de uso con actor, punto de partida y evidencia.

No se agrega otra copia de reglas: la fuente de cada regla debe quedar en un
único lugar y los consumidores referenciarla (invariante 6 de 004-003,
`spec.md:55`).

---

## 3. Recorrido de uso concreto (petición inicial → primer resultado útil)

**Actor:** el dueño/coordinador con un objetivo amplio y una unidad real pendiente.
**Punto de partida legítimo:** repo CDAD con el epic aprobado y una feature en
cola; sin explicación oral previa.

1. **Petición inicial (una frase):** «transformá este objetivo amplio en el
   próximo trabajo, sin perder el alcance global ni inflar el contexto».
2. El architect (o el coordinador de epic) reconstruye intención y restricciones
   desde fuentes vigentes (`planning-contract-draft.md:43-44`): fila del epic,
   discovery-inputs, decisiones del dueño.
3. **Dibuja el recorrido consumidor** de punta a punta y sus fallos relevantes
   (`planning-contract-draft.md:45-46`): petición → primera porción integrable →
   validación → trabajo dependiente.
4. **Mapa de alcances en voz de unidad**: una unidad que entregue un resultado
   verificable (no una capa horizontal), con su consumidor y su comprobación de
   integración; las unidades habilitadoras nombran explícitamente a quién
   habilitan.
5. **Detalle solo de la próxima tanda**: objetivo y dependencias completos para
   todas; contrato/firma/pruebas solo de lo ejecutable próximo
   (`planning-contract-draft.md:55-56`); las tareas futuras declaran
   incertidumbre con dueño y condición de resolución (`epic-004/plan.md:275-277`).
6. **Reparto de detalle por rol**: qué entradas recibe cada rol y por qué
   (`planning-contract-draft.md:74`), sin filtrar implementación al test-writer.
7. **Primer resultado útil (corte del recorrido):** un **primer encargo
   despachable** —una unidad con resultado, dependencias y aceptación— listo
   para `prepare`, más el mapa de cobertura global con las próximas unidades e
   incógnitas con dueño. Eso es «alcanzar el primer resultado útil» sin haber
   gastado el contexto de todo el proyecto.

**Fricciones observables del recorrido hoy:** el validador rechaza el detalle
progresivo (contradicción §1.3); la plantilla empuja a firma+cobertura
(§1.4); no hay una salida canónica «plan legible por humano» (§5 de
discovery-inputs) distinta del bloque JSON `plan-tasks`.

---

## 4. Comparación de enfoques (problema / fuentes / límites) y propuesta mínima

Fuentes externas consultadas (2026-10-13): Shape Up cap. 11 «Get One Piece
Done» y cap. 12 «Map the Scopes» (`basecamp.com/shapeup/3.2-chapter-11`,
`.../3.3-chapter-12`); NN/g «Usability Testing 101» (citada por el dueño,
`discovery-inputs.md:76-80`). Enfoques listados por el dueño:
`discovery-inputs.md:36-48`.

| Enfoque | Problema que resuelve | Fuente | Límite / costo a contrastar (CDAD) |
|---|---|---|---|
| Unidades verticales / mapa de alcances | Integrar una porción utilizable antes de completar capas; algo tangible temprano | Shape Up 11-12 (`integrate one slice`, `scopes`) | Shape Up dice que **los scopes se descubren al recorrer el terreno, no planificando**; CDAD aprueba el plan antes de construir → no se importa entero. Riesgo: una unidad con UI/integración deja infraestructura compartida sin consumidor → requiere **unidad habilitadora** con consumidor explícito (`discovery-inputs.md:42`). |
| Planificación por dependencias / camino crítico | Separar listo/bloqueado/pendiente; adelantar trabajo independiente | `planning-contract-draft.md:47-48,149-150`; Shape Up (`interdependencies`) | «Más workers no reduce tiempo si comparten decisiones» (`discovery-inputs.md:43`); el grafo ya lo valida `cdad_packet.py:2945-3060`. El costo es de integración, no de path. |
| Reducción temprana de incertidumbre (sonda) | Probar la hipótesis/frontera más riesgosa antes de construir grande | Shape Up (`rabbit holes`, `start in the middle`); `planning-contract-draft.md:51-54` | La sonda debe contestar una pregunta y tener condición de fin (`discovery-inputs.md:44`). Precedente sano en CDAD: 005-010 corrigió un doble que modelaba un protocolo inexistente. |
| Descomposición jerárquica progresiva | Alcance global estable, detalle local revisable, razones recuperables | `planning-contract-draft.md:30-39,55-56`; epic-004 `plan.md:275-277` | No generar árbol exhaustivo de microtareas ni ontología (`discovery-inputs.md:45`). **Bloqueado hoy** por el validador (§1.3). |
| Partición por contexto y acoplamiento | Minimizar contexto duplicado entre sesiones conservando unidades completas | 005-002 (medición), 005-003 (reducción) | Estimaciones imperfectas; fragmentar también cuesta tokens y revisiones (`discovery-inputs.md:46`). |
| Planes alternativos pequeños | Comparar 2 particiones cuando hay decisión material | `planning-contract-draft.md:52-54` | No exigir alternativas para tareas obvias ni repetir implementaciones (`discovery-inputs.md:47`). |
| Valor de información / decisiones reversibles | Resolver pronto lo que invalida trabajo; diferir detalle de bajo riesgo | `planning-contract-draft.md:59-60`; Shape Up (`uphill/downhill`) | No sustituir juicio por una puntuación opaca con números inventados (`discovery-inputs.md:48`). |

**Lectura de los límites de Shape Up respecto de CDAD:** Shape Up propone
descubrir scopes *caminando*, con «imagined vs discovered tasks» y una
«hill chart» (uphill=incógnita, downhill=ejecución). CDAD, en cambio, **aprueba
el plan antes de construir** (gate 2→3). Por eso lo trasladable no es «descubrir
todo al andar», sino: (a) **una porción integrada primero**, (b) **programar
solo lo suficiente para el próximo paso** (≡ detalle solo de la próxima tanda),
(c) **declarar la incertidumbre con dueño y condición de resolución** en lugar
de detalle falso, y (d) **criterio de tamaño por costo total**, no por número de
tareas ni de archivos. NN/g aporta la receta de la capa de uso (tarea
representativa, actor, evidencia), sin volverla un evaluador de usabilidad
general (`discovery-inputs.md:122-126`).

**Propuesta mínima elegida (aún SIN contrato; se formaliza en el `draft`):**
una mejora acotada que (1) reubica la regla de detalle progresivo en un **único
hogar canónico** dentro de la skill instalada, referenciada por los
consumidores; (2) **reconcilia el validador** para que un plan de detalle
progresivo sea válido (estado/marcador «planificada-no-detallada» o alcance del
bloque a la próxima tanda, preservando la cobertura global); (3) incorpora el
**criterio de tamaño por costo total** y el disparador de replanteo por unidad
sin información nueva; (4) crea/ajusta **plantillas** (spec desde recorrido de
uso sin `%`; plantilla de plan de feature con ficha + `plan-tasks`); y (5) fija
una **receta mínima de aceptación de uso** separada de TDD/E2E. Se descarta:
planner nuevo, scheduler, UI, plataforma de usabilidad, perfiles de modelo.

---

## 5. Aplicación a la próxima unidad real pendiente

**Unidad real pendiente del epic:** `005-004-claude-code-roles` (estado `queued`,
`docs/.cdad-state.json`), dependencia `005-005` (done). Contrato:
`docs/epics/epic-005-real-operation/plan.md:43` («Roles CDAD activos en Claude
Code para este proyecto… Un ciclo corto real despachado desde Claude Code con la
versión instalada al empezar el ciclo»).

Descomposición propuesta (formato §4 de `planning-contract-draft.md`, sin
inventar detalle futuro):

- **U1 — Reconocimiento de capacidades efectivas de Claude Code (habilitadora).**
  Resultado: mapa verificado de qué carga una sesión CC en la versión instalada
  (rol, skills, hooks, modelo, confianza de carpeta). Dependencias: 005-005;
  decisión del dueño sobre confianza de carpeta. Incertidumbre: mecanismo real
  de carga de rol en CC (no asumir paridad con OpenCode). Insumo/contexto: la
  instalación vigente, `sources/agents/adapters/claude-code.md`, el registro
  local de la instalación. Aceptación: mapa con archivo:línea y VERIFY abiertos.
  **Consumidor nombrado: U3** (el ciclo real). **Comprobación de integración:**
  un rol CC arranca y declara su contrato sin fallback silencioso.
- **U2 — Ciclo corto real en Claude Code (porción integrada).** Resultado: una
  feature pequeña corre punta a punta con la versión instalada, con commit e
  imperfecciones registradas. Depende de U1. Incertidumbre: disponibilidad de la
  cuenta/cuota y de la confianza de carpeta (reservado al dueño). Aceptación: el
  ciclo real corre y se registra la evidencia; las ausencias se declaran.
- **U3 — Cierre: roles activos + evidencia de paridad.** Resultado: la lista de
  roles activos en CC para este proyecto, sin tocar HOME salvo decisión del
  dueño. Depende de U1,U2. Aceptación: un ciclo real despachado desde CC.

Cada unidad declara incertidumbre **sin entrar a construcción**; el detalle
(signaturas/tests) queda para la próxima tanda (regla progresiva). Las unidades
habilitadoras (U1) nombran consumidor (U3) y comprobación de integración.

**Criterio de independencia (más que paths):** U1 y U2 no son independientes
(mismo consumidor y decisiones compartidas); se serializan. No hay paralelismo
seguro dentro de esta feature. Se consideran **decisiones, datos, archivos,
entorno de pruebas, recursos y forma de integrar** —no solo rutas
(`discovery-inputs.md:29-30`).

> Nota: 005-004 aún no tiene spec/discovery; este mapa es una **ilustración del
> método aplicado a trabajo real**, no una spec de 005-004.

---

## 6. Medición disponible y contexto por unidad

**Qué se puede medir hoy (005-002 + 005-003), verificado.**

- Superficie del medidor: `skills/cdad-cycle/scripts/cdad_context_meter.py` +
  wrapper `scripts/cdad_context_meter.py`; flags `--store`, `--session`
  (repetible), `--limit` (default 20), `--idle-threshold` (default 60), `--steps`,
  `--set-summary [--detail]`, `--application-ref/--application-limit`, `--json`
  (no-op): `docs/specs/005-002-session-context-meter/spec.md:161-186`;
  `skills/cdad-cycle/references/context-meter.md:16-52`.
- Registro neutral `context-meter-v1` con cubos `observed`/`estimated`/`unknown`,
  `milestones {first_resume, first_dispatch}`, `measures` (8 claves mínimas),
  agregado `roles[]` con cobertura: `spec.md:99-150`, `:380-387`;
  `context-meter.md:54-147`.
- **Por sesión/rol se pueden medir**: llamadas a herramientas, lecturas
  (`previous_reads`), volumen de salida (`total_output`/`max_output`), input por
  paso / acumulado / `cache.read`, hitos (si existen), costo (o `unknown`); el
  agregado por rol con `sessions_reporting/total`.
- **Observación real de contexto por rol** (005-003): 12 sesiones de rol
  (6 test-writer, 6 implementer; documento de 96.552 B, media 8.046 B/sesión);
  por sesión `session_reads`, `total_output`, `tool_calls`:
  `docs/specs/005-003-orientation-reduction/acceptance.md:36-54`. La vista compacta
  `status` emitió 1.679 B frente a 215.292 caracteres de la lectura completa del
  state en S-BOOT-04 (`acceptance.md:22-34`).
- **Muestras de sesión pinneadas** (005-001 primera sesión, sonda 2 de 003-007,
  S-BOOT-04 opcional): `spec.md de 005-002:509-521`.
- **Observación de despacho**: `record-dispatch` con `docs/attempt.json`
  (`runtime`, `model_configured`, `model_reported`, `session`, `started_at`,
  `provenance`): `skills/cdad-cycle/references/project-execution.md:109-119`.

**Qué queda desconocido (se conserva, no se fabrica).**

- En sesiones de rol, `previous_*` y `time_to_first_*` salen **`unknown` con
  causa** (proxy de tramo completo, no corte pre-acción):
  `005-003/acceptance.md:40-42`.
- `cache.write` no lo reporta el proveedor → `unknown`, nunca `0`:
  `005-002/spec.md:81-83,233-239`; `context-meter.md:77-79`.
- Costo facturado, ventana real, atención humana y retrabajo de integración:
  **no observables** con el instrumento actual (`discovery-inputs.md:117-120`).
- El hito de «primera acción del encargo» es **PROPUESTA**, no asumida:
  `005-003/acceptance.md:54`.

**Estimación de clases/volumen de entradas por unidad, sin inventar precisión
de tokens** (las clases se declaran; el volumen se mide con el medidor o queda
`unknown`): (i) instrucción de rol + encargo; (ii) contrato aplicable (spec +
bloque `plan-tasks` de la tarea); (iii) ficha de la tarea (validación + PD/INV/D
aplicables, `cdad_packet.py:3161-3209`); (iv) archivos referenciados del
alcance; (v) evidencia/logs citados **por referencia**. No se convierte
bytes→tokens (`cdad_continuity.py:29-31`, citado en `005-002/spec.md:78-80`).

---

## 7. Aceptación de uso diferenciada de TDD/E2E (contrato / integración / uso)

Base: `discovery-inputs.md:61-102`; criterio de review vigente
(`docs/epics/epic-005-real-operation/execution.md:56-62`).

| Pregunta | Evidencia apropiada | Productor del insumo | Actor evaluador | Qué NO permite afirmar sola |
|---|---|---|---|---|
| ¿Cumple el comportamiento contratado? | Tests derivados del contrato + review independiente + evidencia técnica | test-writer (RED), implementer (GREEN), reviewer | reviewer (familia ≠ implementer) | Que el contrato resuelva la necesidad correcta |
| ¿Se conectan las piezas reales? | Recorrido **instalado** con el runtime/adaptador y entradas reales o representativas | implementer/orquestador, sobre instalación aislada | orquestador (+dueño para el despliegue) | Que el consumidor entienda la interfaz sin asistencia |
| ¿Se logra el objetivo con esfuerzo razonable? | Tarea representativa con la documentación del consumidor, en **sesión fresca**; registra ayudas/errores/recuperación | orquestador (prepara la tarea y el punto de partida) | agente consumidor en sesión fresca (proxy declarado, no persona) | Usabilidad humana validada si solo participó un agente |
| ¿Sirve en su contexto? | Confirmación/evidencia del consumidor identificado y sus limitaciones | consumidor | consumidor/dueño | Generalización a todos los usuarios/entornos |

**Receta mínima verificable con los recursos del repo** (a fijar en el `draft`):
actor (agente en sesión fresca), objetivo, punto de partida legítimo, entorno/
versión, evidencia de éxito; un recorrido representativo con la documentación
que recibirá el consumidor; camino principal + un bloqueo/recuperación; separar
comprobación automática repetible de observación exploratoria. Precedentes:
recorrido instalado en raíz aislada
(`docs/specs/004-003-planning-procedures/plan.md:23`,
`docs/specs/005-009-cli-delegation/`), y separación checks deterministas vs
recorrido real (`docs/specs/005-006-guided-project-start/plan.md:103-120`).

**Parte que queda declarada como pendiente (con responsable):** cualquier
aceptación que requiera **desplegar** la versión nueva toca una acción
**reservada al dueño** (`execution.md:17-22`; precedente de bloqueo declarado en
`005-003/acceptance.md:90-108`). Se declara `BLOQUEO` con responsable, no se
declara verde por proximidad. NO se exige una prueba humana por cada tarea
interna (`discovery-inputs.md:98-102`).

---

## 8. Plan legible por el humano (objetivo → recorrido → unidades/orden → decisiones y riesgos)

**Objetivo.** Contratos claros y tareas ejecutables con contexto suficiente,
evitando la especificación excesiva y la fragmentación; tamaño de unidad que no
pague planeación/sesión/review sin avance; plantillas que acompañen; regla de
reintentos con hipótesis nueva y replanteo ante repetición sin progreso.

**Recorrido.** Petición amplia → mapa de alcances → detalle solo de la próxima
tanda → primer encargo despachable (ver §3).

**Unidades y orden (ilustrativo; el `draft` fija las definitivas).**

1. **Regla de detalle progresivo, hogar único** (reemplaza/relocaliza la regla
   del borrador). Consumidores: validador, `plan-review`, architect, intake.
2. **Reconciliar el validador de `plan-tasks`** con el detalle progresivo,
   preservando cobertura/dependencias y el fail-closed ante bloques malformados.
   Depende de 1.
3. **Criterio de tamaño de unidad por costo total + disparador de replanteo por
   unidad** (sin duplicar la regla de reintentos; referenciarla). Depende de 1.
4. **Plantillas**: spec desde recorrido de uso (sin `%` de cobertura) y
   plantilla de plan de feature con ficha + `plan-tasks`. Depende de 1.
5. **Receta mínima de aceptación de uso** (contrato/integración/uso) con
   productor, evaluador y evidencia. Depende de 1.

**Decisiones a resolver (propuestas, no adoptadas):** dónde vive la regla
progresiva (¿`stage-2-specification.md`? ¿nueva reference?); cómo representa el
bloque la tarea «planificada-no-detallada» sin crear ontología; si el criterio
de tamaño usa bandas cualitativas o una señal declarada (evitar números
inventados); alcance exacto de la receta de uso y su punto de bloqueo por
despliegue.

**Riesgos.** (a) Duplicar la regla en dos fuentes (viola fuente única,
004-003 `spec.md:55`) → mitigación: hogar único + consumidores por referencia;
(b) «mejorar templates» sin cambiar el resultado (rechazado por el dueño,
`discovery-inputs.md:9-13`) → mitigación: la mejora debe tocar el criterio y el
validador, no solo el texto; (c) convertir la aceptación de uso en gate rígido →
mitigación: receta mínima + pendiente declarado con responsable; (d) fragmentar
en microtareas → mitigación: criterio de costo total y unidades habilitadoras
con consumidor.

---

## 9. Plan de aceptación proporcional (productor / evaluador / evidencia de cierre)

| Capa | Insumo | Productor | Actor evaluador | Evidencia de cierre |
|---|---|---|---|---|
| Contrato | Tests derivados de la spec; trazas RED/GREEN; review independiente | test-writer / implementer / reviewer | reviewer (familia ≠ implementer) | commits + salida de tests + `review.md` |
| Integración | Recorrido instalado (raíz aislada) que ejercita la regla y el validador | implementer/orquestador | orquestador | informe del recorrido + captura del validador aceptando un plan progresivo |
| Uso | Tarea representativa con la documentación del consumidor, sesión fresca | orquestador | agente consumidor (sesión fresca) — **proxy declarado** | registro de ayudas/errores/recuperación; desconocido conservado |
| Cierre | Suite completa una vez, por el que cierra | orquestador | orquestador | suite verde + commit fijado |

La aceptación de uso con artefacto **desplegado** queda **pendiente con
responsable (dueño)** mientras no se despliegue (acción reservada).

---

## 10. Medidas de seguimiento disponibles (desconocido se conserva)

- **Tiempo al primer resultado útil**: contable por hito (`first_dispatch`) si
  está observado; en sesiones de rol puede ser `unknown` con causa
  (`005-003/acceptance.md:40-42`).
- **Bloqueos**: declarados (precedente `005-003/acceptance.md:74-79,90-108`).
- **Retrabajo de integración**: **no observable** hoy; se conserva `unknown`
  (`discovery-inputs.md:117-119`).
- **Contexto por rol**: medible con el medidor (005-002) — llamadas, lecturas,
  volumen de salida, input por paso/acumulado/caché con cobertura declarada.
- **Atención humana**: interrupciones/gates registrados; **sin métrica** de
  esfuerzo humano en el instrumento actual (`005-002/spec.md:90-95`).
- **Comparación con trazas históricas:** citar por referencia, sin atribuir
  causalidad fuerte a tareas distintas (`discovery-inputs.md:119-120`). Meta
  numérica como **orientación**, no demostración automática
  (`005-003/acceptance.md:56-62`).

---

## 11. VERIFY abiertos (se declaran; no se resuelven como hecho)

1. **Representación de la tarea «planificada-no-detallada»** en el bloque
   `plan-tasks` sin romper el fail-closed ni crear una ontología nueva —
   decisión de arquitectura para el `draft`.
2. **Punto exacto de reconciliación del validador** (`cdad_packet.py:3063-3105`)
   y su test de regresión — a fijar en el `draft`.
3. **Alcance de la receta de aceptación de uso** y qué parte queda pendiente por
   depender del despliegue (reservado al dueño).
4. **Criterio de tamaño por costo total**: forma verificable sin números
   inventados (bandas declaradas vs señal cualitativa).
5. **Plantilla de plan de feature**: crear asset o formalizar el formato usado
   por 005-006/005-008/005-009/005-010.
6. **Sesión de cierre de 005-001** (muestra de medición) sigue `unknown` con
   causa en el medidor (`005-002/references/context-meter.md:367-383`): no afecta
   a 005-007, pero se cita como desconocido conservado.
7. **Ruta del CLI en Claude Code** para el ciclo real de 005-004 — fuera de esta
   feature, pero condiciona la aplicación real.

---

## 12. Evidencia de esta subetapa (read-only)

- **Archivos modificados en el repo:** ninguno. `git status --short` sin salida.
- **Archivo de transporte (fuera del repo):**
  `/tmp/opencode/discovery-005-007.md` (estos mismos bytes).
- **Comandos de verificación ejecutados** (lectura):
  - `git log --oneline -5` → HEAD `8cbb23c`; `git branch --show-current` →
    `codex/epic-005-real-operation`.
  - `grep -rn "plan-tasks" skills/ sources/ docs/ scripts/` → declaración única
    en `planning-contract-draft.md` + validador `cdad_packet.py:2883-3209`.
  - `grep -rni "progresiv|próxima tanda|detalle solo"` → solo epic-005, epic-004
    y el borrador de contrato (la regla **no** está en la skill instalada).
  - `grep -rni "intento|retry|dos intentos"` → fuente única
    `re-entry.md:79`; consumidores `SKILL.md:288`, `stage-3-tdd.md:29-39`.
  - `ls docs/assets` → no existe (corrección de la superficie de plantillas).
  - `find skills -iname "*template*"` → no hay plantilla de plan de feature.
- **Lecturas de insumo (declaradas):** plan del epic-005; discovery-inputs de
  005-007; dirección del dueño; spec y plan de 004-003; acceptance de 005-003;
  spec de 005-002; `planning-contract-draft.md`; plan y spec de 005-006 y 005-003
  discovery-inputs; `stage-1/2/3`, `re-entry.md`, `handoff-prompts.md`,
  `project-execution.md`, `context-meter.md`, `SKILL.md`, `sources/roles/*`,
  adaptadores, substages `architect-discovery/draft`, `reviewer-plan-review.md`,
  plantillas de assets y el estado `.cdad-state.json`.

**Estado:** mapa técnico y líneas de brainstorm completos. **No se propone el
contrato** (subetapa `draft`). Los VERIFY quedan explícitos para esa subetapa.