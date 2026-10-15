# Registro de supervisión PD-17 — 004-003 (orquestador OpenCode)

Formato heredado de 004-001/004-002: por tarea cerrada,
(a) resultado frente al contrato, (b) ámbito de cambios, (c) desviaciones con su
disposición proporcional (ADR-011). Prioridad: registro incremental; no se
repite trabajo de rol.

Modelos acordados (2026-10-05, decisión del dueño):
architect / implementer / scribe = `mofgw/deepseek-v4.1-flash`;
test-writer / reviewer = `mofgw/glm-5.3-flash` (familia distinta al implementer).

## Despachos en curso

_(ninguno)_

## Tareas en curso

_(ninguno)_

## T1 — Contract-kind de plan borrador (PD-1) — cerrada 2026-10-05

- **(a) Resultado vs contrato (RED):** `tests/test_004_003_t1_draft_contract.py`
  (197 líneas, commit `1f51f03`) con 2 tests mapeados a PD-1: positivo
  (`prepare` renderiza un paquete de reviewer con contrato borrador declarado,
  sin aprobación; el binding registra `contract_kind: draft-plan`; `render` y
  `validate-packet` lo aceptan) y negativo (`approved-*` forjado sobre un
  borrador → rc≠0, sin publicación, estado/árbol intactos). Re-ejecutado por el
  orquestador: `2 failed in 1.24s`, ambos por `AssertionError` (no
  `ImportError`). Sin lectura de código de implementación.
- **(b) Ámbito:** solo `tests/test_004_003_t1_draft_contract.py`. El orquestador
  preparó el paquete v2 (`prepare --new-execution` rc=0) y actualizó el state.
- **(c) Desviaciones y disposición:**
  - **Interfaz inventada por el oráculo:** el test define
    `--contract-kind draft-plan --contract-path <rel> --plan-version <ver>` y
    el kind `draft-plan`; la spec (D1) nombra el kind pero no la sintaxis de
    flags. Disposición: el orquestador la **acepta** como interfaz de T1
    (implementación de detalle dentro de un contrato aprobado), la registra, y
    el reviewer de etapa 4 puede desafiarla. Congelada pre-GREEN: el implementer
    no puede editar el test.
  - **Riesgo de acoplamiento:** el implementer debe honrar exactamente esa
    interfaz; si el diseño la hiciera inviable, vuelve al orquestador, no al
    test.
- **(a) Resultado vs contrato (GREEN):** commit `b61f1a2` — `VALID_CONTRACT_KINDS`
  gana `draft-plan`; `validate_request` acepta `plan_version` y exige que el
  borrador lo declare, y **rechaza** un `approved-*` que porte `plan_version`
  (detección del forjado, PD-1); `prepare` gana
  `--contract-kind/--contract-path/--plan-version` (tríada obligatoria, solo en
  modo ordinario). Focal 2/2 re-verificado por el orquestador (`1.36s`); el
  diff de `tests/` entre RED y GREEN está **vacío** (oráculo congelado);
  alcance: 2 archivos de implementación, ninguno de tests.
- **(b) Suite completa:** citada del implementer, **331 passed / 620 s, exit
  0**, sin duplicarla (PD-5): el árbol de código no cambió después de esa
  corrida (solo el `state` del orquestador). Baseline 329 + 2 tests de T1
  ahora verdes.
- **(c) Desviaciones:** `make staging` corrido una vez por el implementer para
  materializar `build/staging/` (gitignored; sin cambio de contenido del repo);
  necesario para las suites basadas en instalación en un checkout limpio —
  hallazgo ya conocido de 004-002 (T6).
- **(d) Review (etapa 4):** `review-t1.md` — **changes-required**; 2 BLOCKING
  (F1 apertura de `draft-plan` a todos los roles → bypass del invariante 4;
  F2 `purpose: "approved contract"` en la emisión del borrador → contradice
  PD-1), 3 opcionales (F3–F5). Ambos bloqueantes **re-verificados por el
  orquestador** contra el código (la rama `is_draft` no restringe rol;
  `cdad_packet.py:2316` hardcodea el purpose). Disposición: review-fix con RED
  focal (test-writer) + GREEN (implementer); F3–F5 a deuda priorizada (MVP).
- **(e) Review-fix RED:** `1d4a062` — `tests/test_004_003_t1_reviewfix.py`
  (176 líneas, 1 test por bloqueante). Re-verificado por el orquestador:
  `2 failed` por `AssertionError` (el defecto reproducido, no import/syntax) y
  los 2 tests de T1 siguen verdes; implementación intacta entre GREEN y RED.
- **(f) Review-fix GREEN:** `b0acb03` (+13/−1, 1 archivo) — F1: `role !=
  "reviewer"` → `PolicyError` antes de publicar; F2: `purpose = "draft plan for
  review"` con fuente única hacia PACKET.md. Focal 4/4 re-verificado por el
  orquestador (2.11 s); tests intactos RED→GREEN; suite completa citada del rol
  (333 passed / 575 s). Validadores: 2 FAIL **preexistentes** (drift de
  instalación en `validate-subagents`; odoo en estado RED esperado).
- **(g) Re-review focal (etapa 4):** `review-t1-rereview.md` — **F1 y F2
  CERRADOS, sin regresiones, 0 bloqueantes.** Verificación estructural extra del
  reviewer: `_contract_for` nunca devuelve `draft-plan` (la triple flag es la
  única ruta, blindada por rol); el `purpose` no aprobatorio tiene fuente única.
  Sin segunda review completa (PD-5): se acotó a los 4 tests del fix + 52 de
  regresión de paquetes.
- **(h) Cierre:** T1 cerrada. Deuda priorizada (MVP): F3 (`plan_version: null`
  en un kind aprobado se acepta por valor, no por presencia de clave), F4 (path
  validado dos veces en la rama draft), F5 (huecos de cobertura negativa: sin
  `plan_version`, forja con `approved-epic-plan`, kind desconocido). Ninguno
  rompe el camino feliz.
- **Consumo:** 5 despachos (RED, GREEN, review, RED-fix, GREEN-fix) + 1
  re-review; 1 iteración de review-fix; 0 reintentos por repetición idéntica;
  2 corridas completas de suite (una del implementer, una citada en el
  review-fix) — la del orquestador no se duplicó.


## T7 — Recorrido instalado real sobre 003-002 (PD-13) — cerrada 2026-10-05

- **(a) Promulgación (F2 de review-t5):** `make staging` rc=0; install en **raíz
  aislada** rc=0 (`Verify: PASS — 11 cdad agents`); `install.sh --check` **PASS
  (303 grupos)**. El producto instalado contiene T1 (12 hits `draft-plan`), T2
  (`reviewer-plan-review.md`), T4 (14 hits `plan-tasks`) y T5 (5 hits de
  equivalencia). Los mirrors de `$HOME` quedan fuera de alcance por regla del
  proyecto (su deriva es preexistente).
- **(b) Brecha D8 cerrada:** el paquete v2 del **architect**
  (`004-003-planning-procedures-architect-draft-001`, contract
  `approved-epic-plan`) se preparó por primera vez — imposible antes del registro
  I2 y del soporte de contrato de T1. Es el cierre del problema que originó la
  feature.
- **(c) Recorrido real:** el architect replanificó 003-002 al contrato vigente
  (bloque validado con el validador real: `VALIDATOR OK T1-T4`), materializado en
  `docs/specs/003-002-artifact-tools/plan.md`. El paquete de **plan-review**
  (contrato `draft-plan` + `plan_version`) se preparó **rc=0**: la cadena
  T1+T2+T3+T4 validó el plan de punta a punta; el render llevó la instrucción de
  rol generalizada (fix B3 de T2) y el input `draft plan for review` (fix F2 de T1).
- **(d) Dictamen real (PD-2/PD-4):** el reviewer (GLM, sesión independiente) emitió
  **2 BLOCKING** (F1: divergencia ficha↔bloque, el bloque omitía
  `skills/cdad-cycle/scripts/cdad_packet.py`; F2: T4 modifica `install.sh` sin
  declarar las regresiones que lo ejercitan) + 4 opcionales (F3–F6) + 4
  abstenciones. **Revisar ≠ aprobar**: el plan sigue `draft`.
- **(e) Cambios aplicados:** F1 y F2 (mecánicos, verificados: el plan re-valida con
  `prepare` rc=0, sha `781994fb…`). F3–F6 quedan **abiertos para el dueño de
  003-002** (epic-003, suspendido) por ser de precisión, no defectos observables.
- **(f) Alcance respetado:** **003-002 no se reimplementó** (no se escribió código
  de ninguna de sus tareas); su plan no se aprobó (esa aprobación pertenece a su
  propio ciclo).
- **(g) Cierre:** T7 cerrada. **Deuda:** F3–F6 de `review-plan-001` (plan de
  003-002); F011 (drift de install en `$HOME` + A3 sobre `test_role_packets.py`).
- **Consumo:** 2 despachos (architect, reviewer) + 1 intervención del orquestador
  (promulgación + F1/F2). 0 reintentos. Evidencia: `evidence/t7-journey.md`.

## T5 — Equivalencia y re-entry (G1–G3, PD-5/6/7/10, D4) — cerrada 2026-10-05

- **(a) RED:** `cf8963a` — 8 tests sobre las fuentes canónicas: PD-5 (la regla de
  equivalencia con sus dimensiones y la cita de corrida registrada), PD-6
  (corrida nueva forzada + incertidumbre declarada), PD-7 (focal vs
  transversal), PD-10/G3 (dos intentos reconciliados, en `re-entry.md` y en
  `SKILL.md`), G2 (el gate de suite completa por GREEN gana la cláusula) y 2
  controles de distribución D4. Re-verificado: 6 `AssertionError` / 2 passed.
  El reviewer verificó contra la base que los marcadores **no existían** (RED
  genuino, no fabricado post-hoc).
- **(b) GREEN:** `b881235` (+20 líneas, 3 archivos de `skills/`): `re-entry.md`
  dueño único de la regla; `SKILL.md` la conducta del orquestador (G3);
  `stage-3-tdd.md` la cláusula en el gate (G2). Suite completa citada 364 passed.
- **(c) Review:** `review-t5.md` — contenido **fiel**, 0 bloqueantes del diff;
  8/8 tests mapeados, sin superfluos; la regla **no está copiada** en los
  consumidores. Desviación PD-15 del test-writer (la salida de los tests fallidos
  expuso fragmentos de los documentos a escribir) **ACEPTADA** por el reviewer:
  el oráculo se fijó antes, ningún hallazgo depende, y la dirección
  test-writer→implementador es TDD clásico.
- **(d) F1/F2 — condiciones de cierre, resueltas por decisión del orquestador:**
  - **F1 (AC-4 "se ejercita"):** el reviewer observó con razón que los 8 tests
    son oráculos de marcadores y **ninguno ejercita un flujo**. Disposición
    (remedio b del reviewer): AC-4 se ejercita por **uso real** — las instancias
    de reutilización de evidencia de este propio ciclo, registradas en el ledger
    y en este record (suites de 331/333/338/340/345/353/356/364 citadas, no
    re-ejecutadas, con verificación de identidad del árbol) — y por **T7**, el
    recorrido consecutivo real. `plan.md` actualizado en el mismo cambio.
    No se inventa un mecanismo ejecutable para PD-5/PD-6: los requisitos de
    orquestación eficiente piden uso real, no una suite que pruebe que un modelo
    obedece.
  - **F2 (PD-12 "llega a la instalación"):** la regla no estaba en el producto
    instalado. Disposición: la promulgación se evidencia con **instalación en
    raíz aislada + `install.sh --check` verde** (paso agregado a T7). Los
    mirrors de `$HOME` están **fuera de alcance por regla del proyecto** (nunca
    instalar CDAD en HOME real); su deriva es preexistente a 004-003 (la copia
    instalada ya carecía de contenido de T1/T2/T4).
- **(e) Cierre:** T5 cerrada. **Deuda priorizada:** F3 (F011: drift de install +
  A3 marcando `PROPONE` con un patrón local no acotado y ruido de `__pycache__`),
  F4/F5 (etiqueta y puntero de `SKILL.md` como co-dueño; riesgo de que un
  mantenedor borre el párrafo co-canónico), F6 (anclar comparadores concretos de
  equivalencia). F1/F2 resueltos y trazados.
- **Consumo:** 3 despachos + 1 decisión del orquestador; 0 iteraciones de
  review-fix; 1 corrida completa citada.

## T4 — Plan de validación por unidad (PD-8, PD-11) + deuda F1/F2 de review-t3 — cerrada 2026-10-05

- **(a) RED:** `5126c75` — 8 tests: PD-8 (bloque obligatorio; campos por tarea;
  variante sin código con `observable_checks`; Go co-ubicado) + F1 (5 variantes
  de fence malformado) + F2 (hogar canónico). Re-verificado: 5 `AssertionError`
  / 3 passed.
- **(b) Efecto de alcance anticipado y tratado:** al volver obligatorio el
  bloque, los fixtures de plan draft de T1/T2/T3 dejaban de ser válidos.
  Verifiqué que el parser de T3 ignora claves desconocidas → **pre-migré** los
  fixtures (commits `2461bed`, `b67a5ee`) para evitar un round trip. El
  test-writer completó 4 archivos y **flaggeó correctamente** un 5º fuera de su
  lista; amplié el alcance en la misma sesión. Ninguna aserción cambiada.
  El reviewer confirmó que la migración **fortaleció** las garantías: los
  fixtures pasaron de saltarse los checks (sin bloque) a ejercitarlos completos.
- **(c) GREEN:** `37911a2` (+96/−20, 1 archivo): bloque obligatorio, F1
  fail-loud sin camino de skip, `_check_plan_validation_plan`. Suite completa
  citada 353 passed.
- **(d) F2 y el registro canónico:** el test F2 exige el formato en
  `planning-contract-draft.md` §4, que está en `docs/**` (write scope del
  orquestador, **no** del implementer). Lo materialicé yo: §4.1 con el bloque
  canónico y los nombres de campo. **Declarado como intervención del
  orquestador en docs**, verificada después por el reviewer (que además ejecutó
  el ejemplo contra el validador real: schema-VALID).
- **(e) Review:** `review-t4.md` — **changes-required**: F-A (el consumidor
  `stage-2-specification.md`, nombrado por la spec G5 y por el plan, sin
  reconciliar: cero menciones) y F-B (§4.1 sin los nombres de parámetro que el
  esquema acepta). Ambos re-verificados por mí antes del fix.
- **(f) Review-fix:** RED `4def0de` (fortalece F2 con tokens de parámetro, test
  de distribución/consumo desde stage-2, lock de `@validation_strategy` en
  regressions) + GREEN `afbb776` (+1 línea en stage-2) + mi extensión de §4.1.
- **(g) Re-review focal:** `review-t4-rereview.md` — F-A y F-B **CLOSED**, sin
  debilitamiento; suite completa **verificada por el reviewer** (356/356), no
  citada.
- **(h) ERROR DEL ORQUESTADOR (R1), detectado por el reviewer:** registré
  `review-t4.md` como evidencia en `stage_history` **sin materializarlo**.
  Disposición: materializados `review-t4.md` y `review-t4-rereview.md`; el gate
  de evidencia se restablece. Causa: salteé la materialización al pasar directo
  al review-fix. Refuerzo: materializar el artefacto del rol **antes** de
  registrar la transición de estado que lo cita.
- **(i) Cierre:** T4 cerrada. **Deuda priorizada:** F-C (asimetría de
  `@validation_strategy` en `regressions`; el lock lo cubre a nivel de test),
  F-D (el ejemplo de §4.1 ya declara T0 — atendido), F-E (`__pycache__` en el
  escáner A3). F1 y F2 cerrados.
- **Consumo:** 7 despachos; 1 iteración de review-fix; 1 migración de fixtures
  en 2 commits; 1 intervención del orquestador en `docs/**`; 3 corridas
  completas de suite (2 citadas + 1 verificada por el reviewer).

## T2 — Subfase y paquete de revisión de plan (PD-2/PD-3/PD-4/PD-9) — cerrada 2026-10-05

- **(a) RED:** `821d50b` — `tests/test_004_003_t2_plan_review.py` (352 líneas, 5
  tests): par (reviewer, plan-review) válido con composición
  `common.md + roles/reviewer.md + substages/reviewer-plan-review.md` fijada por
  sha dinámico y **nunca** el substage de diff-review; el paquete lleva el plan
  (`draft-plan` + `plan_version`); sin marca de aprobación; solo rol reviewer; y
  un test de **producto instalado** que renderiza sin repo fuente. Re-verificado:
  5 `AssertionError`.
- **(b) GREEN:** `019eee6` (5 archivos: `VALID_SUBSTAGES`, `ROLE_SUBSTAGES`,
  ambos enums de esquema, `handoff-prompts.md`, y el nuevo
  `packets/substages/reviewer-plan-review.md`). Focal 9/9 re-verificado; suite
  completa citada 338 passed. **Incidente:** el primer turno del implementer
  cerró con la suite en background y el proceso murió con la sesión (patrón ya
  visto en 004-001); reanudado en la misma sesión con suite en primer plano.
- **(c) Review (etapa 4):** `review-t2.md` — **changes-required**: B1
  (`reviewer/review` + `draft-plan` aceptado), B2 (`plan-review` sobre
  `approved-*`), B3 (`packets/roles/reviewer.md` no reconciliado, G4). Los tres
  **re-verificados por el orquestador** (el guard de T1 es por rol, no por
  subfase; sin chequeo substage↔kind; `packets/roles/reviewer.md` es fuente a
  mano y el oráculo calcula su sha dinámicamente).
- **(d) Review-fix RED:** `5286be2` — 2 negativos black-box del pairing
  bidireccional, con control honesto previo y garantías de no-publicación. B3
  **sin test de frases** (los requisitos de orquestación eficiente prohíben
  suites que busquen frases del prompt): se verifica por review.
- **(e) Review-fix GREEN:** `f12b478` — pairing en un punto único
  (`validate_request`), antes de publicar; reconciliación G4 en la fuente
  editable única. Suite completa 340 passed.
- **(f) DESVIACIÓN MATERIAL — conflicto de oráculo:** el implementer **se detuvo
  y reportó** (sin editar tests, como corresponde) que 4 controles honestos de
  T1 usaban `reviewer/review` + `draft-plan`, que el pairing aprobado invalida:
  ningún cambio de implementación puede satisfacer ambos oráculos. Disposición
  del orquestador (HITL delegada por el dueño): **enmienda firmada de oráculo**
  por el test-writer (`1cb2732`, 3 líneas: solo el substage del control; ninguna
  otra aserción ni fixture), con el precedente de 004-001 (T6). Fundamentación
  verificada: la spec §2 asigna el objeto borrador a la subfase `plan-review`
  (G4), así que los controles T1 quedaron stale respecto de la spec aprobada, no
  respecto de la implementación; y la enmienda **fortalece** el oráculo (antes
  testificaba un escape). El re-review la evaluó explícitamente: sin pérdida de
  garantías.
- **(g) Re-review focal (etapa 4):** `review-t2-rereview.md` — **approved**,
  B1/B2/B3 cerrados, 0 bloqueantes nuevos. Nuevo Nit O3 (redundancia estilística
  en la frase de `reviewer.md`) a deuda.
- **(h) Cierre:** T2 cerrada. **Deuda priorizada:** O1 (newline final faltante),
  O2 (`handoff-prompts.md` invoca `plan-review` sin las 3 flags obligatorias),
  O3 (redundancia estilística). Ninguna rompe el camino feliz.
- **Consumo:** 6 despachos + 1 reanudación de sesión + 1 enmienda; 1 iteración
  de review-fix; 1 conflicto de oráculo resuelto por enmienda; 2 corridas
  completas de suite (citadas).

## Cierre de discovery y spec

### D-001 — Discovery + borradores de spec/plan (architect) — cerrada 2026-10-05

- **(a) Resultado vs contrato:** el encargo (`handoff-architect-001.md` +
  `efficient-orchestration-requirements.md`) se cumplió completo: los 5
  entregables pedidos (discovery, borrador de spec, borrador de plan,
  decisiones del dueño, riesgos) más las limitaciones a resolver antes de
  materializar. Read-only respetado: sin escrituras del rol; no leyó
  `tests/.sensitive-patterns.local`; no hubo accesos denegados. Afirmaciones
  citadas `archivo:línea` (verificables).
- **(b) Ámbito de cambios:** ninguno por el rol. El orquestador materializó el
  texto final en `architect-draft-001.md` (ADR-003).
- **(c) Desviaciones y disposición:**
  - **Sin paquete v2 (esperado, D8):** `prepare` rc=2 por I2
    (`cdad_packet.py:1281`). Despacho legacy identificado, registrado en
    `dispatch-ledger.md`. Disposición: la brecha es el objeto de T1 de
    `architect-draft-001.md`.
  - **Árbol sucio:** `docs/epics/.../plan.md`, `planning-contract-draft.md`,
    `handoff-architect-001.md` modificados y
    `efficient-orchestration-requirements.md` sin trackear, previos a este
    traspaso. Disposición: diffs revisados y aprobados por el dueño; commiteados
    con pathspec en `0713fd5`, sin push.
  - **Ambigüedad detectada por el rol:** el `plan.md` del epic declara
    `Status: Draft ... pendiente de aprobación` (`plan.md:357`). Disposición:
    resuelta por evidencia — el frontmatter declara `status: active`
    (`plan.md:4`) y el archivo marca lo posterior como historia pre-activación
    (`plan.md:10-17,26-31`); `_contract_for` no valida estado de aprobación.
    Sin cambios.
  - **Consumo:** 1 despacho, 1 sesión, 0 reintentos (sin repetición idéntica).
    Sin ejecución de suite (trabajo sin código).

### Materialización y aprobación de spec/plan (orquestador) — 2026-10-05

- **Resultado:** `spec.md` (PD-1…PD-13, 7 invariantes, 8 criterios, G1–G5) y
  `plan.md` (T1–T7) materializados desde `architect-draft-001.md` con D1–D7
  aplicadas; `owner-decisions-2026-10-05.md` registra la aprobación del dueño.
  Estado avanzado: `stage_history` + `current_stage` = `specification`,
  `approved_by` = Pablo.
- **Verificación proporcional (ADR-011):** 6 citas de carga del borrador
  confirmadas contra el código — `cdad_packet.py:50` (2 contract-kinds),
  `:700-704`/`:869-882` (`_contract_for`), `:1220-1231`
  (`_approved_stage_entry`), `:902-907` (`_default_scopes` solo `test_roots`),
  `active-packet.schema.json:16`, ausencia de `reviewer-plan-review.md` en
  `packets/substages/`, `debt-second-look.md:11` ("no afecta a este repo") y
  `docs/cdad-policy.json` (`test_roots:["tests"]`). No se re-ejecutó suite
  (trabajo sin código).
- **Decisiones aplicadas:** D3 → F4 fuera del camino feliz de este repo, T6
  condicional y F4 a deuda priorizada; D1 → `draft-plan` nativo en T1; D4 →
  `re-entry.md` dueño único de la regla de equivalencia; D5 → métricas en
  artefactos existentes.
- **Commits:** `0713fd5` (referencias cruzadas de la enmienda) y `6525c1c`
  (discovery + spec/plan + state). Sin push.
