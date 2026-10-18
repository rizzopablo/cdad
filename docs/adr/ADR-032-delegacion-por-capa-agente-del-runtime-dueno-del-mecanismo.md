# ADR-032: La delegación se resuelve por capa — el agente del runtime es dueño del mecanismo, la metodología es neutral, el adaptador sólo cruza runtimes y los modelos los fija la configuración

- **Status**: Accepted
- **Date**: 2026-10-18
- **Deciders**: Pablo (dueño: fijó el **principio de capas** y aprobó las enmiendas 001/002 al plan §8/§9 y
  las dos enmiendas sobre `/tmp`) + orquestador Claude (HITL delegada de epic-006: aprobó spec y plan,
  condujo la corrida de aceptación y la suite de cierre) + architect (spec/plan) + scribe (borrador; **no
  aprueba**)
- **Confidence**: Media
- **Aprobación**: aprobado por Pablo el 2026-10-18 (Memory Bank de 006-002), a partir del borrador del scribe (patrón Scribe; ADR-003/ADR-011). **Evidencia disponible para la decisión:** contrato
  `docs/specs/006-002-delegation-by-layer/spec.md` (PD-1..PD-11, INV-1..INV-8, D-1..D-7; aprobado el
  2026-10-17 bajo la HITL delegada del epic, con **enmiendas 001/002** aprobadas por el dueño) y `plan.md`
  (A-1, A-2); RED→GREEN por unidad (U1 `a2db8f8`→`51ab88d`; U2 `4e17dcc`→`8cf2d75`; U3 `2665d55`→`5ad04e2`
  con testfix `20bb835`; U4 `3c828ad`→`8c05755`; U5 `1125c53`→`8d4b302`; U6 `edc58ae`→`900fa58`; regresiones
  de U1 `7d13a6d`; `/tmp` `b9d9455`→`4c068ea` y `300a05c`→`a3b54e6`); **review formal 1 bloqueante / 4
  opcionales / 4 abstenciones**, con **B-1 cerrado** por review-fix (`5c85d68`→`a25fc20`) y **re-review
  0 bloqueantes / 1 opcional nuevo**; **suite de cierre 1119 passed, 5 skipped**, sin fallas; `make validate`
  **161 PASS / 1 FAIL** (F011 = DT-8, preexistente) y generación determinista. **La confianza es Media**
  porque: (i) la mitad **conductual** de PD-4 descansa en **una** corrida de aceptación —evidencia de
  comportamiento, no prueba— y el resto de las postcondiciones son **de texto** (el oráculo prueba que la
  regla existe, **no** que se obedezca): en esa misma corrida el orquestador **leyó código del CLI** para
  resolver el arranque y **tomó notas de orquestación como mandato**; (ii) el principio de **modelos por
  configuración** queda **declarado**, pero su implementación (instalador `basic` único, plantilla de config,
  verificación de familias) es **006-003**, y `ADR-007` sigue **vigente** hasta entonces; (iii) el consumidor
  **todavía prescribe el adaptador** en su handoff (D-7, fuera de alcance) y **el redespliegue en HOME está
  pendiente**, así que el texto nuevo **no está en uso** donde se midió el problema; (iv) quedan O-1..O-4,
  NF-1 y `sub-agent-strategies.md:49-50` a deuda. No es Baja porque el bloqueante se cerró con RED→GREEN
  verificado por una re-review **independiente** (que reprodujo los 5 ofensores contra el árbol viejo), la
  suite de cierre está **verde** y la aceptación real **midió** el despacho nativo (una sesión hija del rol,
  56 comandos **sin** adaptador, recibo `pending`).

## Contexto y problema

El texto instalable contenía el **mismo mecanismo de runtime en cinco lugares a la vez**
(`skills/cdad-cycle/SKILL.md` §4 y varios puntos del flujo, dos referencias **por runtime** dentro de la
skill, las plantillas de handoff y de estrategias de subagentes y el contrato del adaptador), mientras los
agentes generados llevaban **una sola regla neutral** hardcodeada en el generador
(`docs/specs/006-002-delegation-by-layer/spec.md` §1).

La consecuencia está **medida, no presupuesta**: el orquestador de un consumidor real (1.145 turnos, 6
compactaciones, **ninguna** sesión hija) despachó **todos** sus roles por el **adaptador CLI dentro de su
propio runtime**, porque leyó el handoff y la skill como si **mandaran** el adaptador
(`docs/epics/epic-006-opencode-concurrency/execution.md` §«Hallazgo: por qué el orquestador del consumidor
despacha por bash»). El costo es de contexto —la espera, la recolección y la limpieza de la sesión las paga
el orquestador en vez de su runtime— y de **duplicación de la metodología** en texto instalable.

La pregunta arquitectónica: **¿dónde vive la regla de delegación, para que cada runtime use el mecanismo que
su propio arnés ya tiene, sin que la metodología se acople a un runtime y sin que el adaptador se convierta
en el camino por defecto dentro del mismo runtime?**

## Opciones consideradas

### Opción A: la regla de delegación vive en el agente del runtime, generada desde el adaptador fuente (ADOPTADA)

- Pros: cada runtime declara **su** mecanismo nativo y su mapeo rol→subagente; la skill queda
  **neutral** (metodología); el mecanismo **comparte** la composición ya existente
  (`scripts/cdad-generate.py` desde `sources/`), así que la entrada al proceso sigue siendo la **túnica**
  fuente de agentes; el detalle histórico de cada runtime se conserva **fuera** del árbol instalable.
- Contras: el adaptador fuente pasa a tener una sección más que mantener por runtime; el retiro de las dos
  referencias de la skill obliga a **reapuntar** los tests acoplados que las citaban (hecho en el mismo RED de
  cada unidad, A-1).

### Opción B: una referencia por runtime dentro de la skill

- Contras: **no es instalable hoy**: `install.sh` copia el **mismo** árbol de skill a las tres bases
  (`install.sh:1036-1045`), así que una referencia «por runtime» dentro de la skill llega a todos los
  runtimes. **Descartada con evidencia** (D-1, A2).

### Opción C: dejar el orden y la regla de adaptadores hardcodeados en el generador

- Contras: es el estado que produjo el problema — la regla es **una** y neutral, y no declara el mecanismo
  concreto de ningún runtime; el generador no es el lugar donde vive el conocimiento de un runtime (la capa
  agente sí). **Descartada** (D-1).

### Opción D: prohibir el adaptador dentro del mismo runtime (en vez de mandar el mecanismo nativo)

- Contras: una prohibición sin mecanismo declarado deja al orquestador **sin respuesta** cuando el perfil no
  fija modelos; el problema medido no era «el adaptador existe» sino «el adaptador se lee como **obligatorio**
  dentro del runtime». **Descartada**: se **manda** el mecanismo nativo **y** se prohíbe el adaptador
  intra-runtime (PD-4).

### Opción E: que el orquestador elija o herede un modelo para garantizar la familia distinta del reviewer

- Contras: contradice el principio del dueño (`plan.md` §9: los modelos los fija la configuración, nunca el
  orquestador ni los scripts) y no sería verificable. **Descartada** → D-3: el orquestador **sólo pasa** un
  modelo que venga de la configuración del entorno, **declara** que con `basic` la familia **no** está
  garantizada, **registra el intento** y ofrece la salida legítima (chat nuevo donde **el usuario** elige).

### Opción F: fijar la regla `/tmp` en la metodología (enmienda 001) en vez de sacarla

- Contras: el límite de `/tmp` era **del servidor del dueño**, no de la metodología; prohibirlo o admitirlo en
  texto instalable impone a otros usuarios una restricción que no tienen. **Descartada** por la **enmienda
  002** (reemplaza a la 001): la regla 4 se queda con lo metodológico (**rutas estables del workspace**,
  `.cdad/inbox` para el recibo) y **ningún texto instalable nombra `/tmp`**.

## Decisión

1. **El mecanismo de despacho es del runtime y lo declara su agente (D-1).** Cada orquestador generado
   declara su mecanismo **nativo** con `subagent_type: cdad-<rol>`, el mapeo rol→subagente con sufijo de
   stack, el pase **byte-idéntico** del paquete y el enlace al protocolo de materialización; la sección nace
   en `sources/agents/adapters/{opencode,claude-code}.md` y la **compone** `scripts/cdad-generate.py`, que
   **deja de hardcodear** el orden.
2. **La skill es neutral: metodología, no herramientas (D-2/PD-1/PD-3).** §4 conserva los siete puntos en
   abstracto —principio, orden, **regla de adaptadores**, invariantes de rol, spawn guard, recibo,
   paquete/reentrada independientes del transporte— **sin nombrar runtime ni modelo concreto**; las
   plantillas de handoff y de subagentes quedan como plantillas; `context-meter.md` es **exclusión
   declarada** (nombra herramientas como **datos de medición**, no como instrucción). La ausencia se
   verifica con un oráculo de **formas de herramienta** y de **modelos concretos**, nunca con la palabra
   suelta *task*.
3. **El adaptador cruza runtimes o cubre uno sin delegación propia (regla de adaptadores).** En cualquier
   otro caso se delega con el mecanismo nativo; el adaptador **no** se usa **intra-runtime**. La regla de
   elección por transporte **sale** de `references/cli-delegation.md`, que queda como **contrato del
   adaptador**; las dos referencias por runtime **salen** del árbol instalable y su detalle histórico queda
   **no instalable** en `docs/evidence/runtime-delegation/`, sin que nada instalable apunte a esa copia.
4. **Los modelos los fija la configuración (D-6, principio de `plan.md` §9).** `SKILL.md` §2 pierde la
   columna de familias y el párrafo de perfiles; el orquestador **nunca elige ni inventa** un modelo y pasa
   uno **sólo** si viene de la configuración del entorno. Con un perfil que **no** fija modelos, la familia
   distinta del reviewer se **declara** y se **registra el intento**
   (`runtime`/`model_configured`/`model_reported`/`session`, con `null`/`unknown` para lo no observado); el
   gate de review escribe «invariante no garantizado» en vez de omitirlo. El script de comparación de
   familias y la plantilla de config de delegación son **006-003**; `install.sh`, `scripts/cdad-models.sh` y
   **ADR-007 no se tocan aquí**.
5. **El paquete y el recibo son independientes del transporte (D-4/PD-5/INV-3).** El despacho nativo
   devuelve **TEXTO FINAL** en la sesión del orquestador; el orquestador escenifica los **bytes exactos**
   bajo `.cad/inbox` + `RESULT.json` y corre `receive` → `validate-receipt` → `materialize` → transición, con
   el recibo en **`semantic_status: pending`** (recibir **no** aprueba nada). La equivalencia se declara en
   `references/re-entry.md` y se enlaza desde §4 y desde cada sección `delegation`; `receive` sigue
   aceptando **sólo** `source.kind="staged-file"`.
6. **Disciplina de contexto del orquestador, cuatro reglas, y `/tmp` fuera de la metodología (D-5,
   enmiendas 001/002).** (1) la vista compacta `status` **primero**, sin volcados de state/ledger/skill;
   (2) **rotar** la sesión en los bordes de tarea, no a mitad de unidad; (3) **no reparar por su cuenta**
   —re-despachar el rol nombrando el defecto—; (4) lo que debe durar, dejar evidencia o leer otro proceso o
   rol va a **rutas estables del workspace**, con `.cad/inbox` para el recibo. **Ningún texto instalable
   nombra `/tmp`** (ni para prohibirlo ni para admitirlo). `references/orientation.md` §1 sigue siendo el
   **dueño** de «vista primero»; la fuente lo **cita** y no lo duplica.
7. **Frontera (D-7/PD-8).** El consumidor queda **fuera**: su handoff **todavía prescribe el adaptador** y lo
   actualiza **su dueño**. La decisión **no** toca `install.sh`, `scripts/cdad-models.sh`, el adaptador
   `cdad_delegate*.py`, `ADR-007*` ni el config/handoff del consumidor, y **no amplía** autoridad ni scope
   (el worker no escribe el state).

## Reasons

1. **El arnés nativo es el dueño del ciclo de vida.** Cuando el runtime es dueño del spawn, la espera, la
   recolección y la limpieza, el orquestador sólo valida el resultado; cuando el ciclo lo lleva el adaptador,
   lo **paga el contexto del orquestador** (criterio de fondo aportado con el insumo del consumidor). Poner
   la regla en la capa del runtime es lo que hace que esa verdad sea accionable por el rol correcto.
2. **La metodología debe servir a todos los runtimes.** Una regla de delegación con nombres de herramienta
   dentro de la skill acopla la metodología a un runtime y envejece con él: el mismo texto se instala en las
   tres bases. Neutralizarlo es condición de que la skill siga siendo **la metodología, general y única**.
3. **El adaptador conserva su valor donde es insustituible.** Para orquestar **otro** runtime —o uno **sin**
   delegación propia— el adaptador es lo que existe; dentro del mismo runtime, en cambio, agrega un ciclo de
   vida paralelo y un costo de contexto que el arnés nativo no cobra.
4. **Elegir modelo no es una decisión de orquestación.** El contrato (PD-4/D-3) hace que el orquestador
   **jamás** tenga que elegir o inventar: pasa lo configurado, **declara** cuando la garantía no existe y lo
   **registra**, en vez de esconder la brecha detrás de una elección propia.
5. **El recibo no puede depender del transporte.** Si el paquete y la reentrada fueran distintos por
   mecanismo, cada camino tendría su propia noción de «entregado»: la equivalencia de transporte con el
   **mismo** `receive` y el recibo `pending` mantienen una sola puerta de entrada a la evidencia.
6. **Una regla que no se puede observar no se puede mantener.** El oráculo de ausencia (formas de
   herramienta + modelos concretos, y el literal `/tmp`) convierte cada uno de estos puntos en algo
   **verificable** en el árbol generado; sin él, B-1 (alias y gateway en la skill) habría pasado inadvertido
   otra vez.

## Consequences

- **Positivas.** Cada runtime tiene **una** respuesta para su despacho, declarada en su agente y generada
  desde su adaptador fuente; la skill vuelve a ser metodología (sin herramientas, sin modelos, sin `/tmp`); el
  retiro de las dos referencias por runtime deja el árbol instalable **sin reglas de un runtime ajeno** y
  conserva su detalle histórico como evidencia **no instalable**; el recibo sigue siendo **uno solo** para
  todos los transportes; `make agents` es determinista y `make validate` queda verde salvo el F011
  preexistente.
- **Negativas / límites declarados.** (a) La mitad **conductual** de PD-4 se apoya en **una** corrida de
  aceptación en un worktree aislado: es **evidencia de comportamiento, no prueba**, y los tests de texto
  prueban que las reglas **existen**, no que se **obedezcan**. (b) En esa misma corrida el orquestador
  **leyó código del CLI** para resolver el arranque (contra el espíritu de la regla 1) y **tomó notas de
  orquestación como mandato**: la contaminación de contexto entre el orquestador del epic y el de una
  corrida queda como observación de uso real. (c) Los agentes que `prepare` publica en el proyecto salen de la
  **versión instalada en HOME**, no del repo: la aceptación del texto nuevo **exige desplegar** o aislar a
  mano. (d) Un `opencode.json` de proyecto con `agent.<name>.model` **dejó la lista de agentes vacía**
  (observación registrada, **no investigada**). (e) El principio de **modelos por configuración** queda
  **declarado pero no implementado** (`ADR-007` sigue vigente hasta **006-003**). (f) El **consumidor todavía
  prescribe el adaptador** en su handoff (D-7). (g) El **redespliegue en HOME está pendiente** de la orden del
  dueño (lo instalado es `6978709`, 006-001 completo, y no incluye esta feature), así que el texto nuevo
  **no está en uso** donde se midió el problema. (h) A deuda: **O-1** (título «Delegation (adapter)»), **O-2**
  (línea del canal muerto del CLI en el cuerpo compuesto), **O-3** (dirección de la cita con
  `orientation.md` §1 invertida respecto del plan), **O-4** (ruido cross-runtime en el cuerpo compartido de
  «Bash policy»), **NF-1** (oráculo del gateway **de instancia**, no de clase) y `sub-agent-strategies.md:49-50`
  (sintaxis de frontmatter de permisos y hooks del otro runtime en la skill: **enforcement**, no despacho).
- **No cambia.** El paquete canónico y su pase byte-idéntico, el registro I8, el ledger, `receive`, el
  esquema de identidad durable, el single-writer del state, el clasificador y `install.sh` (fuera de alcance:
  006-003). La delegación **no** amplía autoridad ni scope.

## Notas

- **Contrato normativo:** `docs/specs/006-002-delegation-by-layer/spec.md` (PD-1..PD-11, INV-1..INV-8,
  D-1..D-7; **enmiendas 001/002** del dueño sobre `/tmp`) y `plan.md` (unidades U1..U8, con A-1 y A-2);
  enmiendas al plan del epic: `docs/epics/epic-006-opencode-concurrency/plan.md` §8 (006-002) y §9 (006-003).
- **Código y documentos de producto:** `sources/agents/adapters/{opencode,claude-code}.md` (sección
  `delegation`), `scripts/cdad-generate.py` (composición; sin bloque hardcodeado),
  `agents/{,claude-code/}cdad-orchestrator.md` (regenerados), `sources/roles/orchestrator.md` (4 reglas),
  `skills/cdad-cycle/SKILL.md` (§2, §4, tabla de referencias), `skills/cdad-cycle/references/re-entry.md`
  (equivalencia de transporte), `references/cli-delegation.md` (sólo contrato del adaptador),
  `docs/evidence/runtime-delegation/{opencode,claude-code}-delegation.md` (copias no instalables).
- **Evidencia:** `discovery.md`; `u1..u6-{red,green}.md`; `u1-fix.md`; `u3-testfix.md`; `u6b-*`, `u6c-*`
  (enmiendas sobre `/tmp`); `review.md` (1 bloqueante / 4 opcionales / 4 abstenciones); `rf-red.md` /
  `rf-green.md` (RED `5c85d68` → GREEN `a25fc20`); `rereview.md` (B-1 cerrado; 0 bloqueantes; NF-1);
  `docs/epics/epic-006-opencode-concurrency/execution.md` (§«006-002 U8», §«despacho erróneo detenido»,
  §«re-review y suite de cierre»).
- **Commits:** RED/GREEN `a2db8f8`→`51ab88d`, `4e17dcc`→`8cf2d75`, `2665d55`→`5ad04e2` (`20bb835` testfix),
  `3c828ad`→`8c05755`, `1125c53`→`8d4b302`, `edc58ae`→`900fa58`, `7d13a6d` (regresiones de U1),
  `b9d9455`→`4c068ea` y `300a05c`→`a3b54e6` (`/tmp`), `5c85d68`→`a25fc20` (review-fix B-1). Último commit de
  producto de la feature: **`a25fc20`**; el resto del rango son docs/estado.
- **Relación con otros ADR:** **acota y precisa ADR-023** (delegación externa: interfaz común + adaptador por
  destino) en el caso **intra-runtime**, que ADR-023 no fijaba — el adaptador sirve para **otro** runtime o
  para uno **sin** delegación propia, y el mecanismo nativo es el camino dentro del propio—. **Anticipa la
  sustitución de ADR-007** que anuncia **006-003** (instalador `basic` único, config de delegación y modelos
  por configuración), sin reemplazarlo aquí. Convive con **ADR-026** (roles en Claude Code por mecanismo
  nativo): aquél habilita el mecanismo, éste declara la regla de elección. Reusa el patrón Scribe y la
  separación recepción/materialización/aprobación (ADR-003/ADR-014) y la política única de evidencia
  (ADR-020); **no** toca el guard de progreso (ADR-015).
- **Límites honestos de este registro:** el despacho nativo real se midió **una vez** (worktree aislado, una
  sesión hija del reviewer); el resto son postcondiciones **de texto** con oráculos que probaron poder fallar
  (RED genuino, reproducido por la re-review); `make validate` arrastra el F011 preexistente (**DT-8**); el
  despliegue en HOME está **pendiente**; y el consumidor **todavía** prescribe el adaptador en su handoff.
