- Dispatch ledger: T1–T4 closed (T4 `approved`, 0 blockers, 4 mutations killed); T5 = orchestrator adoption; last full suite cited **475 passed / 1202 s @ `43c9deb`** (product frozen since; T4 diff tests-only).

**Draft 1 — `docs/activeContext.md`** (new entry, insert immediately after the `---` that follows the intro, before the 2026-10-06 entry)

```
<<<FILE:docs/activeContext.md — nueva entry (más reciente arriba)>>>
## 2026-10-07 — Feature: 003-003-progress-guards (epic 003)

Cerrada el 2026-10-07. Entrega el CLI **determinista y read-only** `cdad_guard.py`
(stdlib) sobre las señales ya existentes de 001/002: **`classify`** (repetición sin
progreso P1 y polling legítimo P2/P7 sobre trazas `trace-v1` grabadas), **`preflight`
consultivo** (prevalida una operación contra `docs/cdad-policy.json` + scopes del rol
antes de despachar; P3/D6/O2, solo lee la política), **`record`/`budget` durables**
(eventos y presupuesto bajo `.cdad/executions/<id>/guards/**`, keyed por
`execution_id+packet_id+attempt`; P4) y el **canal de escalado con tabla cerrada
evento→acción** (P5/D5). El juicio semántico queda en el orquestador; el guard nunca
cambia spec/autoridad/prioridad, no concede ni endurece permisos, no repite efectos
(reconcilia receipts de 002) y **nunca escribe `docs/.cdad-state.json`**.

T1–T3 cerradas con review-fix (T1: 3 bloqueantes de una familia → remedio de clase;
T2: F1 en 5 puntos; T3: F1/F2/F3). La review de T2 incorporó la **enmienda del dueño**:
salir de la raíz del proyecto queda **habilitado por defecto** (`allow` con motivo
honesto; `deny` solo ante regla explícita de política/rol; herramienta sin destino
resoluble ⇒ `unknown`, nunca un `deny` fabricado) y la **calibración de severidad**
del preflight/`read_scope` se difirió al uso real. T4 aprobada sin bloqueantes (12/12
focales; **4 mutaciones semánticas eliminadas**, M1–M4; fixtures etiquetados
`simulation`/`reconstruction-of-real-incident` con cita verbatim verificada). Morfg.

Versión operativa **`939f501`** (raíz aislada `<home>/.cache/cdad-adopted-939f501`);
consumo verificado: un agente nuevo cargó `cdad-cycle` desde esa raíz y vio
`scripts/cdad_guard.py`. Evidencia: suite completa **475 passed** (1202 s) en `43c9deb`
(producto inmóvil desde entonces; T4 tocó solo tests); validadores con los **2 FAIL
preexistentes** (install del host; A3 de 004-003). Registro de uso:
`guards-ledger.md`, `guards-incidents-observed.md`, `debt.md`, `evidence/t5/`.

**Uso real — resultado honesto (T5).** Sobre cuatro sesiones reales de esta misma
feature, con un grabador **desechable fuera del producto** (`evidence/t5/recorder.py`,
trabajo del orquestador/deepseek): el guard **no** detectó los incidentes reales C1/C2;
los detectó el seguimiento del orquestador (PID real + `.rc` + inactividad
DONE/GONE/STALLED + cola de la salida). Las dos alertas que emitió fueron **falsas
alarmas** (×5 y ×7 `repetition-without-progress` sobre ediciones distintas del mismo
archivo), causadas por medir el progreso con el **digest del conjunto de rutas** (grano
grueso: no ve cambios de contenido). Costo: una corrida deepseek (grabador) + 4
`classify`, <1 s cada uno.

**Corrección del dueño (2026-10-07).** Los C1/C2 «reales» son, con alta probabilidad,
**artefactos del modo de despacho del orquestador** (`opencode run`, que mata el
proceso al terminar el turno) y no del entorno nativo (en OpenCode nativo
`background: true` notifica y el agente sigue); no se comprobó dentro de una sesión
nativa. Consecuencias: **G1** (grabador de producto desde la DB) baja a **media**;
**G2 se retira** (`launch.sh`/`watch.sh` son herramientas de este modo de orquestación,
no producto); las falsas alarmas por progreso de grano grueso **siguen siendo un
hallazgo válido** (deuda media).

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **Analizador read-only; el juicio es del orquestador (D1/D5).** El guard lee señales
  existentes y emite incidentes/decisiones; toda acción sale de una **tabla cerrada**
  (backoff-poll, retry-with-change, repackage, new-session-from-checkpoint, escalate,
  recommend-block, resume-same-session, retry) y la ambigüedad vuelve en un paquete
  breve. Trade-off: la utilidad depende de que el orquestador consuma el canal; el
  guard no decide por él ni cierra gates.
- **Preflight consultivo + raíz habilitada por defecto (enmienda del dueño).**
  Contexto: el preflight de T2 fabricaba `allow` «within the declared scope» y el
  dueño sospechó permisos demasiado estrictos. Razón: informar sin impedir trabajo
  legítimo; `deny` solo desde regla explícita, `unknown` cuando no hay destino
  resoluble. Trade-off: `WRITE_TOOLS` es un conjunto genérico sin mapa por rol (D6
  parcial) — O-D declarada; la calibración de severidad se difiere al uso real.
- **Presupuesto durable keyed por `execution_id`, fuera del state (D4).** Los eventos
  viven bajo `.cdad/executions/<id>/guards/**`; reanudar **no** reinicia contadores y
  el guard **no** escribe `docs/.cdad-state.json` (single-writer = orquestador). El
  `record` es **create-exclusive** (segmentos seguros de 002; repetición de clave =
  conflicto rc≠0, bytes originales intactos). Trade-off: interfaces keyed por
  `execution_id` sin truncar, para no obstaculizar 003-004 (D10).
- **Huella canónica por referencia; canonicalización = responsabilidad del grabador
  (D2/B3b).** El guard hashea `tool + args + result_class` tal como se grabó y **no**
  canonicaliza; un `progress_token` ausente/no-string es señal **no observada** y
  nunca produce un incidente de progreso congelado (fail-closed al lado no-alarma).
  Trade-off: el lector en vivo (recorder) es deuda G1, no producto aún.
- **No-alarma y dedup por token de relevancia (P7/O3).** Un trabajo legítimo y
  progresivo no recibe intervención; el mismo incidente sin cambio relevante no
  re-alerta (clave `canon(kind, fingerprint, execution_id, packet_id)`). Trade-off:
  el dedup se comprobó con fixtures (T4) y con packets distintos en uso real; la
  agrupación de ≥2 `unknown` de huellas distintas queda descubierta (F1 de `review-t4`).

Deuda y hallazgos (no bloquean el cierre) — consolidada en `debt.md`:

- **Media:** G1 grabador de producto desde la DB de OpenCode (marcar lanzamientos
  desacoplados como `unknown`; señal de fin de sesión sin entrega; digest de progreso
  por **contenido**); calibración de severidad del preflight/`read_scope` con uso real;
  T1 F1 (traceback ante archivo no-UTF-8, fail-closed).
- **Baja:** T1 F2/O2/O3a-c · T2 O-A/O-C/O-D (D declarada) · T3 O3/O4 y `budget` con id
  absoluto (solo lectura) · T4 O1–O3/N1–N3 · 2 FAIL preexistentes de validadores
  (install del host; A3 de 004-003).
- **Evidencia regularizada:** E1 de T2 (filas 15a/15b del dispatch-ledger) quedó
  registrada; el dedup en uso se separa por `packet_id` como corresponde.

**Lecciones de proceso**

1. **Un guard que solo mira señales ya existentes hereda sus límites.** C1 (cierre de
   turno sin entrega) y C2 (lanzamiento desacoplado `&`/`nohup`) no eran observables;
   el detector fue el seguimiento del orquestador, no el guard. La capacidad de
   observación es una deuda del grabador (G1), no del clasificador.
2. **El progreso por conjunto de rutas es demasiado grueso.** Medir el digest de las
   rutas (no del contenido/diff) fabricó dos falsas alarmas sobre trabajo sano; la
   señal de progreso se define por contenido, no por nombre de archivo.
3. **Adopción ≠ fixtures verdes.** Con 12/12 focales y 4 mutaciones muertas, el primer
   uso real no detectó ningún incidente real: la medición honesta es el uso
   (`guards-ledger.md`), con falsas alarmas registradas y su causa.
4. **Un techo mecánico no ejercitado no se reimplementa.** `steps:300` (V5) sigue sin
   enforcement probado en vivo; el guard observa y registra, no lo duplica.
5. **La dedup necesita un token de relevancia, no solo una huella.** Sin cambio de
   progreso o de clase de huella, el mismo incidente no vuelve a alertar.

**Next feature in queue:** `003-004-context-continuity` (epic 003; **queued**, no se
implementa por anticipado). epic-003 sigue abierto; epic-004 está cerrado (2026-10-05).
<<<FILE:docs/activeContext.md>>>
```

**Draft 2 — `docs/progress.md`**

```
<<<FILE:docs/progress.md — reemplaza el bullet de epic-003 en ## In progress>>>
- **epic-003-context-efficiency** — **reactivado** (2026-10-05; mandato HITL
  re-registrado en
  [handoff-resume-2026-10-05.md](epics/epic-003-context-efficiency/handoff-resume-2026-10-05.md),
  reconciliación —no restauración ciega— del snapshot de suspensión).
  `003-002-artifact-tools` cerrada (2026-10-06) y `003-003-progress-guards` cerrada
  (2026-10-07). Pendiente: **`003-004-context-continuity`** (queued; no se implementa
  por anticipado).
<<<FILE:docs/progress.md>>>
```

```
<<<FILE:docs/progress.md — nuevo bullet al inicio de ## Done>>>
- **003-003-progress-guards** (2026-10-07, epic 003) — guard **determinista read-only**
  `skills/cdad-cycle/scripts/cdad_guard.py` (+ wrapper + `guard-trace`/`guard-event`
  schemas): `classify` (repetición sin progreso P1 y polling P2/P7 sobre `trace-v1`),
  `preflight` **consultivo** (P3/D6/O2; enmienda del dueño: salir de la raíz habilitado
  por defecto, `deny` solo explícito, `unknown` sin destino resoluble),
  `record`/`budget` **durables** bajo `.cdad/executions/<id>/guards/**` (P4, create-
  exclusive) y **escalado con tabla cerrada evento→acción** (P5/D5). El juicio queda en
  el orquestador; nunca escribe `docs/.cdad-state.json` ni repite efectos (reconcilia
  receipts de 002). T1–T3 con review-fix (T1 familia de 3 bloqueantes; T2 F1 5 puntos;
  T3 F1/F2/F3), T4 `approved` (0 bloqueantes; 4 mutaciones eliminadas). **T5 — uso real
  honesto:** el guard **no** detectó los C1/C2 reales (los detectó el orquestador); 2
  falsas alarmas por digest de progreso de **grano grueso** (conjunto de rutas). El
  dueño corrigió (2026-10-07): C1/C2 = **artefactos del despacho con `opencode run`**,
  no del entorno nativo → **G2 retirada**, **G1 a media**; las falsas alarmas siguen
  siendo deuda media. Versión operativa **`939f501`** (raíz aislada
  `<home>/.cache/cdad-adopted-939f501`). Evidencia: suite **475 passed** (1202 s) en
  `43c9deb` (producto inmóvil desde entonces; T4 solo tests), focales T4 12/12;
  `guards-ledger.md`, `guards-incidents-observed.md`, `debt.md`, `evidence/t5/`,
  `dispatch-ledger.md`. Deuda: ver "Queued".
<<<FILE:docs/progress.md>>>
```

```
<<<FILE:docs/progress.md — reemplaza el pie>>>
Última actualización: 2026-10-07

- 2026-10-07 — 003-003-progress-guards cerrada (epic 003): guard determinista
  read-only (`classify`/`preflight` consultivo/`record`/`budget` durables/escalado con
  tabla cerrada); el juicio en el orquestador; nunca escribe el state. T1–T4 con
  review-fix y T4 aprobada (0 bloqueantes, 4 mutaciones). Uso real honesto: no detectó
  los C1/C2 reales; 2 falsas alarmas por progreso de grano grueso; corrección del
  dueño → C1/C2 artefactos del despacho con `opencode run`, G2 retirada, G1 a media.
  Versión operativa `939f501`; suite 475 passed (`43c9deb`); sin CI. Siguiente:
  003-004-context-continuity (epic 003).
<<<FILE:docs/progress.md>>>
```

And in `## Queued`, add the prioritized debt of 003-003:
```
<<<FILE:docs/progress.md — agrega al final de ## Queued>>>
- **003-003 — deuda priorizada:** G1 (media) grabador de producto desde la DB de
  OpenCode (lanzamientos desacoplados ⇒ `unknown`; señal de fin de sesión sin entrega;
  digest de progreso por contenido); calibración de severidad del preflight/`read_scope`
  con uso real (decisión del dueño); T1 F1 (traceback no-UTF-8, fail-closed); T1
  F2/O2/O3a-c, T2 O-A/O-C/O-D, T3 O3/O4 + `budget` con id absoluto, T4 O1–O3/N1–N3;
  2 FAIL preexistentes de validadores (ajenos a la feature).
<<<FILE:docs/progress.md>>>
```

**Draft 3 — `docs/systemPatterns.md`** (new subsection after "Recepción, materialización y evidencia de artefactos (epic 003, 2026-10-06)")

```
<<<FILE:docs/systemPatterns.md — nueva subsección (dentro de ## Patrones del framework)>>>
### Guards de progreso — analizador read-only, juicio en el orquestador (epic 003, 2026-10-07)

- **`cdad_guard.py` es analizador, nunca orquestador.** Determinista, stdlib y
  read-only salvo `record` (escribe solo bajo `.cdad/executions/<id>/guards/**`).
  Expone `classify` (repetición sin progreso + polling sobre `trace-v1`), `preflight`
  (prevalidación **consultiva**), `record`/`budget` (durables) y el canal de escalado.
  El juicio semántico es del orquestador; el guard **nunca** cambia spec, autoridad ni
  prioridad y **nunca** escribe `docs/.cdad-state.json` (single-writer = orquestador,
  regla ya vigente desde 003-002).
- **Preflight consultivo (enmienda del dueño, 2026-10-06).** Salir de la raíz del
  proyecto está **habilitado por defecto** (`allow`, motivo honesto `outside project
  root: not governed by project policy`); `deny` **solo** con regla explícita de la
  política o del rol; herramienta sin destino resoluble ⇒ `unknown`, nunca un `deny` ni
  un `allow` fabricado. Lee `docs/cdad-policy.json`, no lo escribe.
- **Presupuesto/eventos durables keyed por `execution_id`.** Bajo
  `.cdad/executions/<id>/guards/**`, keyed por `execution_id+packet_id+attempt`; el
  `record` es create-exclusive (reescribir la misma clave = conflicto, bytes intactos);
  reanudar **no** reinicia contadores. Interfaces pensadas para no obstaculizar 003-004.
- **Frontier de honestidad:** un `progress_token` ausente/no-string es señal **no
  observada** (nunca fabrica un incidente); el guard **no** canonicaliza args (lo hace
  el grabador, declarado en el schema `trace-v1`); no repite efectos (reconcilia
  receipts de 002 y solo señaliza).
- **Cuidado de adopción (uso real T5):** el digest de progreso **por conjunto de rutas
  es demasiado grueso** → falsas alarmas; el registro de progreso debe ser por
  **contenido/diff** (deuda G1). Y un lanzamiento desacoplado (`&`/`nohup`/redirección)
  vuelve `ok` en la traza: es `unknown`, no éxito. Versión operativa adoptada para el
  uso: `939f501` (raíz aislada); el lector en vivo es deuda, no producto.
<<<FILE:docs/systemPatterns.md>>>
```

```
<<<FILE:docs/systemPatterns.md — reemplaza el pie>>>
Última actualización: 2026-10-07 (003-003)
<<<FILE:docs/systemPatterns.md>>>
```

**Draft ADR (only architectural decision present → yes, suggested)**

An architectural decision exists (the approved spec resolves D1–D11 and the owner amended the preflight boundary); recommend one MADR:

```
<<<FILE:docs/adr/ADR-015-guard-progreso-analizador-readonly-juicio-orquestador.md>>>
# ADR-015 — El guard de progreso es un analizador read-only; el juicio es del orquestador

## Estado
Propuesto (borrador del scribe; materializa el orquestador bajo ADR-003; aprueba el dueño). 2026-10-07.

## Contexto
El desarrollo real sufre interrupciones y repeticiones improductivas (2.073 reintentos
idénticos en un caso, ~20 h). Un supervisor que consuma más que el trabajo que evita, o
que decida semánticamente, agrava el problema. La spec de 003-003 resolvió D1–D11 y el
dueño enmendó la frontera del preflight (2026-10-06): un rechazo no es mala conducta y
salir de la raíz del proyecto se habilita por defecto.

## Decisión
`skills/cdad-cycle/scripts/cdad_guard.py` es un **analizador determinista read-only**
sobre señales ya existentes (DB de sesiones, artefactos 001/002):
1. `classify` detecta repetición sin progreso y polling legítimo sobre trazas grabadas
   (`trace-v1`), con dedup por token de relevancia.
2. `preflight` es **consultivo**: solo `deny` con regla explícita; fuera de la raíz ⇒
   `allow`; sin destino resoluble ⇒ `unknown`.
3. `record`/`budget` persisten eventos/presupuesto **durables** bajo
   `.cdad/executions/<id>/guards/**`, keyed por `execution_id+packet_id+attempt`; el
   guard **nunca** escribe `docs/.cdad-state.json` ni repite efectos.
4. El canal de escalado usa una **tabla cerrada evento→acción** (solo acciones
   reversibles); la ambigüedad vuelve al orquestador.
El guard nunca cambia spec, autoridad ni prioridad, y no concede/endurece permisos.

## Alternativas consideradas
- **Controlador/supervisor LLM permanente:** descartado (consume más de lo que ahorra;
  prohibido por el epic y el handoff del architect).
- **Techo mecánico nuevo / auto-bloqueo duro:** descartado; `steps:300` sigue siendo el
  único techo y su enforcement no está probado en vivo (V5).
- **Hash del output completo para equivalencia:** descartado por frágil; la huella es
  `tool + args canonicalizados + clase de resultado`, evidencia por referencia.

## Consecuencias
- (+) Supervisor barato y auditable; juicio humano/de orquestador preservado; interfaces
  durables keyed por `execution_id` no obstaculizan 003-004.
- (−) Su utilidad depende de que el orquestador consuma el canal; el lector en vivo
  (grabador) es deuda (G1) y en el primer uso real el guard no detectó los incidentes
  reales C1/C2; el digest de progreso por rutas es de grano grueso (deuda media).
- (−) El mapa de capacidades por rol del preflight (D6) queda parcial (conjunto genérico
  `WRITE_TOOLS`, O-D declarada).

## Confianza
**Media.** La separación analizador/orquestador y el presupuesto durable están
verificados por tests y por uso (consistente con ADR-003/ADR-011/ADR-014); la **utilidad
medida** del guard es baja en su primer uso real honesto y la calibración de severidad
(contenido vs rutas, preflight) queda como deuda con uso real.
<<<FILE:docs/adr/ADR-015-guard-progreso-analizador-readonly-juicio-orquestador.md>>>
```

