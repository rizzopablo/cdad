# ADR-030: La repetición de un cierre se decide por identidad resuelta desde la ejecución ligada, y sin feature activa la operación nunca aplica un cierre

- **Status**: Proposed
- **Date**: 2026-10-14
- **Deciders**: orquestador OpenCode (HITL delegada epic-005) + architect (spec v1 y enmienda 001)
- **Confidence**: Media
- **Aprobación**: orquestador OpenCode bajo la delegación HITL del epic-005
  (`docs/epics/epic-005-real-operation/execution.md`), el **2026-10-14**, a partir del borrador del scribe
  (patrón Scribe; ADR-003/ADR-011). Evidencia disponible: contrato `5c23caa2…` (spec v2, enmienda 001)
  aprobado y **re-aprobado** tras la enmienda; RED `8a969d3` (**4 rojos por aserción**) y GREEN `a4028af`
  (focal **4 passed**; cuatro módulos de 005-012 **47 passed**; `tests/` intacto); gate de aceptación T2 con
  el **CLI real** sobre proyecto descartable (AC-1/AC-2/AC-3); review formal **0 bloqueantes / 4 opcionales /
  3 abstenciones** (reviewer de familia distinta); suite de cierre **1028 passed / 4 skipped** en `2de9747` y
  `make validate` **155 PASS / 1 FAIL** (F011 preexistente). **La confianza es Media** porque: (i) el
  comportamiento **no existe en la versión instalada** hasta el despliegue (del dueño), así que el uso
  previsto en un proyecto real no está ejercido; (ii) el contrato **v1 era internamente contradictorio** en el
  escenario central y hubo que **enmendarlo** —lo expuso el RED, no la review—, señal de que la resolución se
  fijó con una vuelta de más; (iii) quedan límites declarados con condición de cierre (**E-2** el replay tras
  un cambio de feature activa queda fuera; **E-6** la rama «ninguna de las tres» sin caso focal; **E-3**/
  **E-4**) y cuatro opcionales Nit/FYI. No es Baja porque la prueba decisiva se corrió con el **CLI real**
  sobre proyecto descartable, la suite de cierre está verde y la review no encontró bloqueantes.

## Contexto y problema

`register-transition` (**ADR-029**) resuelve la feature de una transición desde `state.active_feature`, con
**una sola** excepción (`late-delivery`). El efecto de `closure` deja `active_feature: null` y **no** limpia
`state.execution`; el guard de feature nula corre **antes** de la búsqueda idempotente por `transition_key`.
Consecuencia medida: **un orquestador interrumpido justo después del cierre no puede reanudar con la misma
orden** (rc=2 con un mensaje que sugiere abrir la unidad) — lo contrario de lo que corresponde cuando la
feature ya está cerrada. La pregunta: **¿cómo reconoce la operación un cierre ya aplicado sin inventar una
búsqueda en la historia y sin que la corrección ensanche lo que la operación puede aplicar?**

## Opciones consideradas

### Opción A: resolver la feature por tres fuentes (con la ejecución ligada como tercera) y decidir por identidad antes del mundo, con el techo «sin feature activa nunca se aplica» (ADOPTADA)

- Pros: la orden repetida **verbatim** resuelve la **misma** feature cerrada y alcanza el no-op de PD-23; la
  tercera fuente es **un único valor** ligado por la ejecución (el mismo que el CLI ya resuelve sin flag), no
  una heurística; el techo (PD-27) impide que la enmienda amplíe el poder de la operación; el marcador del
  rechazo **no** se inventa (reusa `state incoherent`).
- Contras: la resolución tiene una fuente más que explicar y depende de que el efecto del cierre **no** toque
  `state.execution` (acoplamiento declarado); en la rama de feature cerrada el no-op precede a PD-8 y a la
  autoridad, así que un replay legítimo es no-op **aunque el mundo haya cambiado** — consecuencia aceptada y
  declarada.

### Opción B: buscar en la historia la ejecución de la feature, o comparar el payload sin `execution_id`

- Contras: es un cambio de la **identidad** (PD-10), no del orden; convertiría el reconocimiento en una
  búsqueda y afectaría a todas las clases. **Fuera de alcance** por la fila 14 → **deuda E-2** (priorizada).

### Opción C: mantener PD-8 (y la autoridad) antes del no-op y dejar que el replay falle si el mundo cambió

- Contras: la fila promete que repetir un cierre ya aplicado **no falla**, sin condicionarlo; un replay
  legítimo podría ser rechazado por un pin que ya no nombra los bytes, por un recibo ausente o por una
  delegación revocada **aunque la transición ya esté registrada**. **Descartada.**

### Opción D: resolver la feature sólo por `--feature` (el modelo de `late-delivery`)

- Contras: exige que el operador **vuelva a nombrar** la feature en la orden repetida, así que la reanudación
  **verbatim** —el escenario del dueño— seguiría fallando. **Descartada.**

### Opción E: extender el arreglo a todas las clases (el `--feature` ignorado en `gate`)

- Contras: no es el mismo arreglo (el replay legítimo de las demás clases ocurre con la feature **abierta**,
  donde el no-op ya opera) y la fila manda a deuda lo que no lo es. **Descartada** → **deuda E-1**
  (priorizada).

### Opción F: reabrir la feature o crear una vía de re-cierre cuando la feature ya está cerrada

- Contras: el cierre es un efecto consumado; la vía de lo que llega tarde ya está declarada (`receive --late`
  + `late-delivery`) y **no** reabre ni aprueba nada. **Descartada.**

## Decision

1. **Resolución de la feature de `closure` por tres fuentes, en orden:** `--feature` → `state.active_feature`
   (string no vacío) → la feature ligada por la **ejecución activa** (`state.execution.feature_id`). Si
   ninguna existe → rc=2 `state incoherent`, el mensaje **nombra** la situación, **no** contiene `open-unit`
   ni `open the unit`, y ofrece `--feature <feature-id>`; el state queda byte a byte idéntico.
2. **La tercera fuente no es un desvío silencioso:** es **un único valor** ligado por la ejecución activa
   —el mismo que el CLI ya resuelve sin flag—, escrito en cada `prepare` y cada `open-unit`; el efecto del
   cierre **no** toca esa clave, así que tras cerrar la repetición verbatim resuelve **exactamente** la
   feature que el primer cierre resolvió desde `active_feature`.
3. **Techo (PD-27): sin feature activa la operación nunca aplica un cierre.** Sólo puede (a) reconocer el ya
   registrado (no-op rc=0 sin escritura), (b) rechazar cerrado si la feature resuelta ya está cerrada (rc=2
   `state incoherent`, nombrando feature y estado, sin `open-unit`, ofreciendo la salida legítima) o (c)
   rechazar cerrado si la clave no está registrada y la feature resuelta no está cerrada (rc=2, nombrando la
   situación y ofreciendo `--feature`). El camino de la **primera** aplicación (feature abierta **y** activa)
   conserva su orden y sus reglas sin cambios.
4. **Orden: en la rama de feature cerrada la identidad decide antes que el mundo.** La resolución del
   documento de cierre (con su digest) y la búsqueda de identidad **preceden** a PD-8(a)/(b), al requisito de
   `--closure-path` y al control de autoridad; los chequeos de **nivel de argumento** (insumos de la
   identidad) siguen en la cabeza de la operación. Un replay legítimo es no-op **aunque el mundo haya
   cambiado** después del cierre; **límite declarado:** la identidad lleva el digest **resuelto**, así que el
   documento citado debe seguir existiendo (si falta, la resolución falla cerrado con `evidence missing`).
5. **Coherencia de `--feature` (PD-24):** si difiere de la feature **resuelta** → rc=2 nombrando las dos; si
   nombra una feature desconocida → rc=2; igual a la resuelta → se acepta; ausente → la resuelta. **Nunca**
   desvío silencioso.
6. **Alcance y marcador:** el arreglo toca **sólo** la clase `closure`; el rechazo **reusa** el marcador
   `state incoherent` ya declarado por PD-12(i) de 005-012 y **no** crea una vía de re-cierre. La identidad
   (PD-10), las reglas del pin, el efecto del cierre (PD-9) y las demás clases quedan intactos.

## Reasons

1. **El escenario del dueño se cumple sin inventar mecanismo:** la orden repetida verbatim vuelve a resolver
   la **misma** feature porque la ejecución ligada sobrevive al cierre; el reconocimiento sigue siendo **por
   identidad** (ADR-029), no por prosa ni por búsqueda.
2. **La corrección no ensancha la operación:** el techo de PD-27 mantiene la aplicación de un cierre atada a
   `active_feature`, exactamente como antes; la fuente nueva sólo sirve para **resolver** un cierre ya
   aplicado (no-op o rechazo cerrado).
3. **El rechazo enseña la salida legítima:** sin `open-unit`, nombrando la feature y su estado, y ofreciendo
   la vía declarada para lo que llega después del cierre — el mensaje deja de contradecir el estado del
   proyecto.
4. **La frontera del juicio no se mueve:** el CLI no decide el significado de un texto ni la calidad de una
   entrega; resuelve una feature por valores del state, compara una identidad y falla cerrado.

## Consequences

- **Positivas.** Un orquestador interrumpido justo después del cierre **reanuda con la misma orden** (no-op
  rc=0 que lo dice y nombra la entrada, state byte a byte idéntico, una sola entrada de cierre); la repetición
  con otro payload **rechaza** sin efectos y sin sugerir abrir la unidad; el cierre distinto de una feature ya
  cerrada deja de ser posible (el guard por estado cubre D-14 acotada a `closure`); la coherencia de
  `--feature` deja de ser un desvío silencioso.
- **Negativas / límites declarados.** (a) Un replay **legítimo** es no-op aunque el mundo haya cambiado
  después del cierre (contrato editado, recibo borrado, delegación revocada): consecuencia de poner la
  identidad antes que PD-8 y la autoridad en esa rama. (b) Si el documento de cierre citado **falta** o
  cambió, la identidad no se puede recomputar y el replay falla cerrado (`evidence missing`) en vez de ser
  no-op. (c) La resumibilidad **verbatim** depende de que la ejecución ligada siga siendo la misma: el replay
  tras un **cambio** de feature activa queda fuera (**E-2**). (d) El arreglo **no** cubre el `--feature`
  ignorado en `gate` (**E-1**), ni D-12/D-13/D-16 de 005-012. (e) La rama «ninguna de las tres» de la
  resolución es un fallback defensivo sin caso focal propio (**E-6**). (f) Cuatro opcionales Nit/FYI de la
  review (O-1..O-4) quedan a deuda.
- **No cambia.** El payload de identidad y su serialización (INV-13), la recepción (`receive` no aprueba), el
  efecto del cierre (PD-9), las reglas del pin (PD-8(b)/PD-14), el camino de la primera aplicación (PD-26) y
  las demás clases.

## Notas

- **Contrato normativo:** `docs/specs/005-014-closure-replay/spec.md` (v2, enmienda 001, sha256 `5c23caa2…`;
  §1, §2 PD-22..PD-27, §3 INV-10..INV-13, §4 AC-1..AC-4, «Enmienda 001», §6 E-1..E-6) y la fila 14 del plan
  del epic (`docs/epics/epic-005-real-operation/plan.md:47`; alta de la fila `:144-157`). **Sin** `plan.md`
  propio (forma liviana decidida por el dueño).
- **Código:** `skills/cdad-cycle/scripts/cdad_packet.py` (+134/−13 en `a4028af`: `_resolve_closure_feature`,
  `_transition_noop_message` y la rama `closure`).
- **Evidencia:** `discovery.md` (defecto medido con línea; orden de chequeos por clase), `t1-red.md` (4 rojos
  por aserción; señal de contrato declarada), `t1-green.md` (comandos, conteos, commit), `acceptance.md`
  (AC-1..AC-3 con el CLI real sobre proyecto descartable), `review.md` (0 bloqueantes / 4 opcionales /
  3 abstenciones, con cinco sondas propias), `closure-suite.md` (worktree `2de9747`; 1028 passed / 4 skipped;
  `make validate` 155 PASS / 1 FAIL F011 preexistente).
- **Commits:** RED `8a969d3`; enmienda 001 del contrato `ec30d07`; GREEN `a4028af`; los registros de la unidad
  (discovery, aceptación, review) por la operación.
- **Relación con otros ADR:** **amplía ADR-029** (identidad por contenido, vigencia por el pin que nombra los
  bytes actuales, el cierre comprueba antes de aplicar) **sin re-declararlo**, y reusa el escritor único y la
  separación recepción/materialización/aprobación (ADR-003/ADR-014). No toca el guard de progreso (ADR-015)
  ni la política de evidencia (ADR-020). Si el orquestador prefiere registrarlo como **enmienda de ADR-029**
  en lugar de un ADR nuevo, el contenido es el mismo.
- **Límites honestos de este registro:** el comportamiento nuevo **no** está ejercido en un proyecto real (no
  existe en la versión instalada; el despliegue es del dueño); la medición de AC-1/AC-3 es **una corrida
  representativa**, no estadística; la mitad «árbol» de INV-7 no se asertó (sólo el state byte a byte); el
  foco de la rama «ninguna de las tres» no existe (E-6) y el replay tras un cambio de feature activa no se
  arregló (E-2).
