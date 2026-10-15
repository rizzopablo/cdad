# ADR-029: El registro de una transición es una operación del CLI con identidad por contenido, vigencia por el pin que nombra los bytes actuales y un cierre que comprueba antes de aplicar

- **Status**: Proposed
- **Date**: 2026-10-14
- **Deciders**: orquestador OpenCode (HITL delegada epic-005) + architect (spec/plan) + orquestador Claude (revisión de la spec, declaración de B3 como bloqueante para el uso previsto, suite de cierre y repetición de T8)
- **Confidence**: Media
- **Aprobación**: orquestador OpenCode bajo la delegación HITL del epic-005
  (`docs/epics/epic-005-real-operation/execution.md`), el **2026-10-14**, a partir del borrador del scribe
  (patrón Scribe; ADR-003/ADR-011). Evidencia disponible: contrato `9e34750f…` (spec) y `9abfb894…` (plan)
  aprobados juntos; review formal **2 bloqueantes / 7 opcionales / 3 abstenciones** con los tres bloqueantes
  **corregidos ya** (B1 en código, B2 y B3 con enmienda del contrato + RED/GREEN); gate de aceptación T8
  **aprobado y repetido** sobre el commit final; suite de cierre **1024 passed / 4 skipped** en `6fd515d` y
  `make validate` **155 PASS / 1 FAIL** (F011 preexistente). **La confianza es Media** porque: (i) la operación
  **no existe en la versión instalada** hasta el **despliegue** (D-4, del dueño), de modo que el uso previsto en
  un proyecto real **no** está ejercido todavía; (ii) los tres bloqueantes muestran que el mecanismo tenía
  **huecos reales** (un acto de aprobación sin autoridad, un no-op que **afirmaba** no haber tenido efectos, y una
  reaprobación obligada al registro manual), todos medidos y corregidos, pero con RED **después** de la primera
  implementación; (iii) quedan límites declarados con condición de cierre (**D-12**, **D-16**, **D-13..D-15**,
  **D-10**, **D-11**) y dos datos del proceso abiertos (el commit del heartbeat externo y los dos digests
  escritos a mano y corregidos).

## Contexto y problema

Hoy **10 de las 11** transiciones del ciclo se registran **a mano**: el orquestador corre un script propio que
edita `docs/.cdad-state.json` (append a `stage_history`, `active_packet.status`, `postconditions_status`), y
**`open-unit` es la única operación de transición del CLI** (`docs/specs/005-012-transition-registration/discovery.md`
§1/§9). Ese camino **no exige la evidencia referenciada** (el recibo durable o el artefacto materializado, con su
digest), **no comprueba nada antes de aplicar** en el cierre, **no es idempotente** y **no deja el script como
evidencia durable**: el registro de 005-013 necesitó **6 scripts** propios para un ciclo
(`docs/specs/005-013-unit-contract/debt.md:65-69`). Los tres casos reales que el discovery midió: (1) un
despacho **sin recibo** (el run que no vuelve) que dejaba el cierre sin salida y obligaba a **fabricar** un
`completed` que la evidencia no sostenía (el scribe de 005-011, `docs/specs/005-011-common-entry/closure.md`
§«Precisión posterior al cierre»); (2) una **ejecución huérfana** creada por `prepare --new-execution` sobre un
contexto ya abierto; y (3) una **sustitución de aprobación** cuya única traza durable era **prosa en un `note`**
(decisión del dueño en contra: «no pidas tests que decidan el significado de un párrafo por listas de palabras»).

La pregunta de arquitectura: **¿qué debe hacer el CLI al registrar una decisión del orquestador sobre una
transición, de modo que el trabajo manual baje —sin compensarlo con controles frágiles— y sin que el CLI se
convierta en juez del sentido de un texto?**

## Opciones consideradas

### Opción A: subcomando nuevo `register-transition`, simétrico a `open-unit`, con el escritor único existente (ADOPTADA)

- Pros: la superficie queda **descubrible por `--help`**, con su propio contrato y sus tests; **no** mezcla el
  registro con el productor de paquetes (`prepare` conserva su rol y sus invariantes); usa el **lock y la
  publicación atómica que ya existen** (`_ProjectLock` + `_publish_owned_atomically`/`_publish_generation`, una
  sola serialización).
- Contras: crece la interfaz (un subcomando y **seis** clases de decisión) y hay que decidir qué comprueba cada
  clase; el `--stage` sigue siendo etiqueta libre (token plano) porque la historia real tiene **184 valores
  distintos**.

### Opción B: `prepare --record-transition`

- Contras: mezcla el **registro** de transiciones con el **productor** de paquetes y complica los invariantes de
  `prepare` (INV-1). **Rechazada.**

### Opción C: extender sólo `receive`/`materialize`

- Contras: ataca el hueco más caro (la recepción) pero **no** cubre RED/GREEN/review/cierre, que son el resto del
  costo: **AC-1 no sería alcanzable** sin trabajo manual. **Rechazada.**

### Opción D: que la vigencia/sustitución de una aprobación viva en la **prosa** de un `note`

- Contras: es el caso 3, y es **exactamente** la clase de control que el dueño prohíbe. **Rechazada** (se adoptó
  el campo **estructural** `supersedes`, con el lector aditivo que lo consume).

### Opción E: marcar la sustitución **reescribiendo** la entrada vieja

- Contras: rompe la **byte-identidad** de la historia y la aditividad (INV-3). **Rechazada** (la vigencia se
  **deriva** de la declaración de la entrada nueva).

### Opción F: identidad sobre la tupla de campos «de transición», sin los insumos con efecto

- Contras: es el defecto **B2** medido: N `delivery` del mismo paquete con la misma etiqueta —el uso natural para
  registrar las postcondiciones de un GREEN, porque `--postcondition` es **singular** por invocación— producían la
  **misma** clave y la 2ª..Nª devolvían **rc=0 «no-op, no effects» sin registrar y sin fallar**, contra lo que
  promete PD-12. **Rechazada** (la identidad incluye los **insumos con efecto** y su payload se escribe en la
  entrada).

### Opción G: que `--supersedes` sea el **único** predicado del control de exclusión

- Contras: es el defecto **B3** medido: `--supersedes` **sólo puede citar entradas con `transition_key`**, y las
  aprobaciones registradas a mano (todas las anteriores a esta operación y **las tres de esta feature**) son
  **keyless**, así que tras el despliegue **la primera reaprobación de cada feature en curso** habría obligado a
  editar el state a mano —justo lo que la unidad elimina. **Rechazada** (el predicado de vigencia pasa a ser «el
  pin que **nombra los bytes actuales**»: el **mismo** criterio que el cierre ya usaba).

### Opción H: reutilizar `delivery` con una disposición `abandoned`/`superseded`

- Contras: `delivery` significa **recepción** («recibir nunca aprueba») y «entrega abandonada» es un oxímoron;
  además obligaría a **relajar** los controles más fuertes de la unidad (entrega sin recibo → `evidence missing`;
  paquete no `dispatched` → `state incoherent`) para un caso que **no es** una recepción. **Rechazada** (clase
  propia `disposition`).

### Opción I: exigir los digests por argumento

- Contras: pasar un hash para que el CLI lo recalcule es **trabajo y superficie de error sin protección**
  adicional. **Rechazada** (los digests los **deriva** el CLI; afirmarlos es una verificación **opcional** para
  citar exactamente los bytes revisados).

### Opción J: migrar o recomputar las claves históricas para que el no-op también las reconozca

- Contras: reabriría el fail-open que B2 cierra (el state **no** registró la postcondición ni el `current_stage`
  declarado de esas entradas). **Rechazada** (el límite se **declara** como deuda D-12, sin migrar el state).

## Decision

1. **Superficie y escritor único.** `register-transition` es un subcomando de
   `skills/cdad-cycle/scripts/cdad_packet.py`, con **toda** escritura del state por `_ProjectLock` y la
   publicación atómica y la serialización ya existentes. **No** hay un segundo escritor ni una segunda
   serialización, y `prepare` **conserva su rol** de productor de paquetes (no registra transiciones).
2. **Seis clases de decisión, vocabulario cerrado:** `delivery`, `gate`, `advance`, `closure`, `late-delivery` y
   `disposition`. La **forma del registro** es aditiva: las claves ya usadas por la historia más `transition`,
   `transition_key`, `transition_key_payload`, `supersedes`, `approval_effect: false` y —sólo en `disposition`—
   `resolution`, `replaced_by`. **Nunca** se reescribe ni se borra una entrada.
3. **Identidad por contenido:** `transition_key = sha256(payload canónico)`, donde el payload es la tupla de
   identidad **más los insumos con efecto** (la postcondición resuelta con su `outcome`, el `current_stage`
   declarado, los `artifacts` citados —ordenados por `path`, porque la entrada los guarda como *mapping*— y los
   campos propios de cada clase: `replaced_by`, `approved_by`, `contract`/`plan`, `closure`), con **una sola**
   normalización y la serialización canónica (`json.dumps(..., ensure_ascii=False, sort_keys=True,
   separators=(",",":"))`). El payload se **escribe** en la entrada (`transition_key_payload`), de modo que la
   identidad es **comprobable desde el state** (frontera de versión explícita: una entrada sin esa clave está
   registrada bajo la fórmula anterior). `note` y `by` **no** entran en el payload: son anotación, y la salida
   del no-op **declara** que no se escribieron en vez de afirmar un no-op mudo.
4. **Repetición y exclusión.** Misma clave → **no-op** (rc=0, sin segunda entrada, state **byte a byte
   idéntico**, salida que **nombra la entrada existente**) e **independiente de la cabeza** (no depende de la
   continuidad: la idempotencia de `begin`/`checkpoint` sí depende de la cabeza y esa diferencia se declara).
   Clave distinta → **entrada nueva** (append; el ciclo repite etapas por tarea). Transición **estructuralmente
   excluyente** → rc=2 `state incoherent`, sin efectos.
5. **Vigencia estructural y única de la aprobación.** Una aprobación `specification` cuyo **pin ya no nombra los
   bytes actuales** del contrato **no compite** como vigente: es **el mismo** predicado que el cierre ya usaba
   (PD-8(b)), aplicado **también** al registrar (PD-14) — **un solo** criterio, no dos. La sustitución se marca
   con el campo **estructural** `supersedes` en la entrada **nueva**; `--supersedes` queda para reaprobar los
   **mismos** bytes. La vigencia **nunca** se decide por prosa.
6. **El cierre comprueba ANTES de aplicar y tiene salida.** Dos comprobaciones mecánicas previas a cualquier
   escritura: (a) **entregas requeridas** —todo paquete de la ejecución activa con **registro de despacho** (los
   despachos repetidos se cuentan **una vez**) debe tener **recibo durable O disposición registrada**— y (b) la
   **aprobación vigente** pinneada. Si falta algo → rc=2 con el marcador (`evidence missing` / `approval
   pending`), **nombrando** el paquete o la aprobación, y **ofreciendo las dos salidas legítimas**: recibir por el
   camino normal, o **disponer** el despacho. El cierre mira **sólo** la ejecución activa.
7. **`disposition`: la decisión del orquestador sobre un despacho que no vuelve, con la feature abierta.** Clase
   propia con vocabulario cerrado (`--resolution abandoned|superseded`, con `--replaced-by` obligatorio en
   `superseded`): comprueba antes de escribir que el paquete **pertenece** a la ejecución activa, está
   `dispatched`, **no** tiene recibo durable y la feature está **abierta**; escribe **sólo** la traza estructural,
   **no** aprueba (sin `approved_by`), **no** toca `active_packet` (no fabrica un `completed`) ni ningún campo
   derivado de la feature, y es idempotente por su clave. **El CLI no juzga si el despacho debe disponerse**: eso
   es del orquestador.
8. **Recepción y entrega tardía.** Recibir **nunca aprueba** (`semantic_status: "pending"`, `approval_effect:
   false`; la autorización de un rol sigue dependiendo **exclusivamente** de la entrada `specification`
   pinneada). La entrega tardía usa el **buzón como entrada** con un modo **declarado** `receive --late` que
   **reusa** la máquina de recibos (identidad, partes, digests, esquema del recibo) e **invierte sólo** la
   precondición de vigencia (la feature destino **está** cerrada), más la clase `late-delivery` que deja sólo la
   traza: la feature sigue `done`, no se reabre y no aprueba nada.
9. **Los digests los deriva el CLI.** Si se omiten, el CLI los **calcula de los bytes actuales**, los **escribe**
   y los **imprime**; si se afirman, los **verifica** y una diferencia falla cerrado. El único caso declarado para
   afirmarlos es **citar exactamente los bytes revisados**.
10. **Autoridad del gate en tres casos:** con delegación registrada, se verifica su **vigencia** (revocada o
    vencida **falla cerrado**); **sin** delegación, se registra el **aprobador declarado** y la salida declara que
    **no hubo delegación que verificar** (el dueño es la autoridad **original** y **no** se bloquea); con
    `active_epic: null`, igual. El CLI **no** verifica identidades (deuda D-6).
11. **Aditividad declarada: dos extensiones y sólo dos.** El vocabulario de marcadores de 005-001 PD-12 suma
    **`evidence missing`** («la evidencia referenciada por la transición no existe o no coincide con su digest») y
    la selección de entradas `specification` de 005-001 D3/PD-18 suma el predicado **vigente**. Ninguna regla
    ajena se re-declara y **ninguna** validación nueva se aplica a las entradas históricas; el state **no** se
    migra.

## Reasons

1. **El trabajo manual baja en el punto exacto donde estaba y sin controles nuevos frágiles:** el único control
   que la unidad agrega es la **comprobación del cierre** —y es el que **elimina** el `completed` fabricado del
   caso 1 y el que **tiene salida** cuando el despacho no vuelve—. Los digests derivados **quitan** argumentos al
   operador, y la autoridad sin delegación **quita** un bloqueo que habría devuelto al state editado a mano.
2. **La contabilidad se automatiza y el juicio se conserva:** el CLI comprueba **estructura, digests, vocabulario
   de etapas, existencia de la autoridad vigente y de las entregas requeridas** y **no** decide el significado de
   un texto, la calidad de una entrega, si un bloqueante es bloqueante, si una deuda se acepta, la priorización de
   una review **ni si un despacho debe disponerse**. La entrada no es una evaluación: es la **decisión del
   orquestador transcrita a estructura**.
3. **La identidad tiene que distinguir invocaciones, no efectos:** sin los insumos con efecto, el no-op se volvía
   un **fail-open afirmativo** (B2) —afirmaba no haber tenido efectos y los tenía—. Con el payload, «invocación
   idéntica» y «misma clave» vuelven a ser equivalentes, y el límite se declara (una invocación que declara un
   insumo que su clase no aplica también entra en el payload: la clave distingue **invocaciones**).
4. **Un solo predicado de vigencia, el que el cierre ya usaba:** la reaprobación tras una **enmienda** del
   contrato no necesita `--supersedes` —la entrada vieja **ya no habilitaba nada** porque el lector exige que el
   pin coincida— y el caso raro de los **mismos** bytes desde una entrada **sin clave** se declara como límite
   (D-16) en vez de inventar un mecanismo o migrar la historia.
5. **La anulación de un despacho es una decisión, no un resultado:** una clase propia que registra la decisión
   como **dato estructural** (sin `approved_by`, sin `completed` fabricado, sin habilitar roles) evita relajar los
   controles de `delivery` y mantiene el vocabulario de marcadores intacto (reusa `state incoherent`/`evidence
   missing`).
6. **La recepción no aprueba y la entrega tardía no reabre:** la autorización sigue teniendo **un solo** dueño (la
   aprobación pinneada) y una entrega que llega después del cierre deja **traza durable** sin tocar el estado de
   la feature — la propiedad que el «caso 1» del cierre exigía (una salida explícita, sin reabrir ni aprobar).
7. **Fuente única y aditividad:** cada regla reusada tiene dueño y se **referencia** por ruta/sección; la
   operación no re-declara la regla del pin, ni la del escritor único, ni la de idempotencia, ni la forma del
   state.

## Consequences

**Positivas (medidas):**

- **El ciclo representativo corre entero con la operación (AC-1):** **8 invocaciones, todas rc=0**, **7 entradas**
  de la operación (`advance`, `gate` de etapa 2, tres `delivery`, `gate` de T4, `closure`) sobre un proyecto
  descartable en `<tmp>`, con el `HOME` del subproceso aislado, los digests **derivados** por el CLI en las tres
  entregas y **cero** ediciones manuales del state (el state final es **byte a byte** el que produjo el CLI).
- **El cierre deja de fabricar evidencia y gana su salida (AC-4):** con un despacho **sin recibo** el cierre
  rechaza **nombrando el paquete** (`evidence missing`), state intacto, **ofreciendo las dos salidas legítimas** y
  **ya no `late-delivery`** (que es de feature cerrada); registrada la **disposición**, el cierre **avanza**.
- **Repetición y distinción (AC-3):** la invocación idéntica es **no-op byte-idéntico** que **nombra la entrada**
  existente; una transición distinta (otro `--current-stage`, otra postcondición del mismo paquete) **anexa** una
  entrada; una estructuralmente excluyente falla cerrado **sin efectos**.
- **Entrega tardía (AC-2):** `receive` normal sigue fallando cerrado sobre la feature cerrada; `receive --late` y
  `late-delivery` dan rc=0 con recibo durable, `semantic_status: pending`, la feature sigue `done` y la traza no
  lleva `approved_by`.
- **La unidad se mide a sí misma:** de las **30 entradas** de su propio tramo, **24 las registró la operación**
  (20 `delivery` + 4 `gate`) y **6** quedaron manuales con motivo declarado (el discovery, las cuatro
  aprobaciones `specification` y el RED de T1); **la operación no pudo** registrar la reaprobación de la enmienda
  B2 —respondió `state incoherent` nombrando `transition_key None`— y eso es **el defecto B3 medido**, corregido
  después por su propia enmienda.
- **Aditividad verificada:** `validate-state` rc=0 sobre el state vivo **antes y después**, sin migrar ni
  reescribir ninguna entrada histórica (los focales de la unidad y la comprobación de cierre lo verifican).
- **Suite de cierre:** **1024 passed / 4 skipped, sin fallos** (worktree fijado a `6fd515d`); `make validate`
  **155 PASS / 1 FAIL** (F011 preexistente).

**Negativas / trade-offs:**

- **La operación no existe en la versión instalada** hasta el **despliegue** (D-4, del dueño, compartida con
  005-013): el uso previsto en un ciclo real de un proyecto **todavía no está ejercido**.
- **Frontera de versión de la identidad (D-12):** las entradas registradas con la **fórmula anterior** del payload
  conservan su `transition_key` y **no** se invalidan, pero **no** se reconocen como no-op candidato: repetir una
  de esas invocaciones **anexa** una entrada nueva. Es la decisión conservadora (reconocerlas reabriría el
  fail-open de B2) y **no** se migra el state. Medido al cierre: **18** de las 24 entradas de la operación llevan
  la fórmula anterior y **6** el payload canónico.
- **Límite declarado (D-16):** reaprobar los **mismos** bytes desde una aprobación vigente **sin `transition_key`**
  no tiene salida por la operación (`--supersedes` no puede citarla); **no** se le inventa mecanismo. **No** alcanza
  al caso de la **enmienda** (bytes cambiados), que sí tiene salida.
- **La vigencia del state no cambia (D-10):** `_validate_v2_vigency` (consumida por `validate-state`, `prepare` y
  `receive`) **sigue** exigiendo `hitl_delegation` con epic activo; P2 quita el bloqueo **de la operación**, no esa
  condición del estado.
- **Alcance declarado:** los despachos sin recibo de ejecuciones **cerradas** (D-11), el contexto abierto por otra
  vía (D-5), la identidad de quien aprueba (D-6), el staging del buzón + `RESULT.json` (D-8 → deuda D-10 de
  005-004), el veredicto fino de `reconcile` a nivel de ejecución (D-1), el campo derivado sin dueño
  `review_status` (D-2) y el tamaño del state (D-3) quedan **fuera** con condición de cierre.
- **Costo declarado:** +6 clases en el vocabulario de decisiones, +4 campos aditivos en la entrada
  (`transition`, `transition_key`, `transition_key_payload`, `supersedes`) y una comprobación mecánica **nueva**
  (la del cierre); a cambio, el registro a mano desaparece del camino previsto.
- **Tres bloqueantes reales en la primera implementación** (B1: PD-6 no aplicada a `closure`; B2: identidad que
  tragaba invocaciones distintas; B3: reaprobación obligada al registro manual), los tres **medidos** y
  corregidos —dos de ellos con **enmienda del contrato** antes del RED/GREEN—.

**Neutrales:**

- **El vocabulario de `--stage` sigue siendo libre** (token plano; canónico sólo para `disposition` y
  `late-delivery`): la historia real tiene 184 etiquetas distintas y un vocabulario cerrado la invalidaría. Lo
  **cerrado** es la decisión (`--transition`), la disposición (`--resolution`) y los campos **operativos**.
- **`prepare` no cambia de rol:** sigue siendo el productor de paquetes; un `prepare` posterior a una transición
  registrada produce los mismos bytes que sin ella (mismos insumos).
- **Sin paralelismo:** `active_packet` sigue siendo único (fuera de alcance).

## Notas

- **Contrato normativo:** `docs/specs/005-012-transition-registration/spec.md` (sha256 `9e34750f…`; §2.1–§2.4,
  **PD-1..PD-21**, **INV-1..INV-9**, **AC-1..AC-4**, §5 **D-1..D-14**, §7 **D-1..D-16** con D-9 retirada) y
  `plan.md` (sha256 `9abfb894…`; fichas T1..T8 y bloque canónico `plan-tasks`); contrato de la **fila 12** del
  plan del epic (`docs/epics/epic-005-real-operation/plan.md:45`) y «Ajuste de los ciclos pendientes»
  (`:48-88`).
- **Código:** `skills/cdad-cycle/scripts/cdad_packet.py` (subcomando, clases, identidad, vigencia, cierre,
  disposición) y `skills/cdad-cycle/scripts/cdad_result.py` (modo declarado `receive --late`); documentación
  operativa por referencia en `skills/cdad-cycle/references/re-entry.md` (paso 4) y
  `skills/cdad-cycle/references/project-execution.md` (sección nueva contigua a las operativas §5-§8).
- **Evidencia:** `discovery.md` (inventario de las 11 transiciones y los tres casos reales),
  `review-claude-spec-2026-10-14.md` (B1/P1/P2 sobre la spec), `review.md` (2 bloqueantes / 7 opcionales /
  3 abstenciones), `acceptance.md` (T8, sha256 `da6e3d59…`), `closure-suite.md` (sha256 `a39aa0dc…`) e informes
  por tarea `t1..t7`, `b1-red/b1-green`, `b2-red/b2-green`, `b3-red/b3-green`, `t3-testfix`.
- **Commits:** producto — `401f966` (T1), `21bada6` (T2), `c164b30` (T5), `0057a50` (T3), `f5e0fc2` (T4),
  `721990f` (T6), `7b10325` (T7); RED — `878091b`, `112ce91`, `9669c0a`, `99b65e6`, `f8fd4fb`, `4b8bf5c`;
  review-fix — `724ca3c` (B1 GREEN), `64a32d3` (B2 GREEN), `ffb7abd` (B3 GREEN) con sus RED `331566c`,
  `f7fcbcc`, `dc13903`; cierre — worktree y commit final **`6fd515d`**.
- **Relación con otros ADR:** **reusa sin re-declarar** el escritor único y la separación
  recepción/materialización/aprobación (**ADR-003**, **ADR-014**), la autorización por rol con el pin
  (**005-001 D3/PD-18**, y **ADR-019** para la forma de la aprobación), la proyección read-only de la orientación
  (**ADR-025**, **ADR-027**) y el contrato de unidad pineado por digest (**ADR-028**). **Amplía** el vocabulario
  de marcadores de 005-001 PD-12 con `evidence missing`. No toca la continuidad (003-004), ni el guard de
  progreso (ADR-015), ni la política de evidencia.
- **Límites honestos de este registro:** el número de invocaciones del recorrido **real** de un ciclo de producto
  no se midió (el de **AC-1 es un fixture**: 8); la magnitud del ahorro no se mide con una sonda sintética sino
  sobre el próximo ciclo real (declarado como desconocido en el contrato); la mitad «árbol» de INV-7 (snapshot
  completo, más allá del state byte a byte idéntico) no se asertó; la consecuencia de D-12 no es reproducible en un
  fixture nuevo; y este registro **no** identifica los valores de los **dos digests escritos a mano y corregidos**
  que el cierre cita como evidencia del problema (ver el informe del scribe).
