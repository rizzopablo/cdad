# Active Context

Estado actual del proyecto. Cada feature cerrada agrega una entry. Las entries más recientes arriba.

---

## 2026-10-22 — Feature: 006-004-active-decisions-table (epic 006)

**Cerrada el 2026-10-22 (ciclo técnico completo; la suite de cierre la corre quien cierra, política
declarada en el paquete).**
Sexta y última unidad de `epic-006-opencode-concurrency`: **la tabla de decisiones vigentes del
proyecto** y, con ella, **la distribución de la decisión que gobierna el trabajo siguiente**. La
feature encadena dos cosas: (a) **la decisión que el dueño aprueba viaja en el encargo** del rol al
que gobierna, y (b) **el principio de general antes que específico** (enmienda 005 del plan del epic)
encuentra su casa canónica y llega al architect y al reviewer **por el mismo mecanismo de las filas**.
**Contrato:** `spec.md` sha256 `ee88d426…` (PD-1..PD-13, INV-1..INV-16, DEC-1..DEC-16, L-1..L-7,
D-1..D-6) + `plan.md`, aprobados el 2026-10-20 por el orquestador bajo la **HITL delegada del epic**
(el owner la mantuvo ese día), tras `plan-review-001..004` (B-1..B-4 cerrados). **El epic NO se
cierra** con la feature: el cierre del epic es un acto aparte.

**Problema medido (no presupuestado).** El proyecto tenía **33 ADR** y **ningún índice de
decisiones**: `grep -rn "Decisiones vigentes\|Current decisions" skills/ sources/ agents/ tests/
install.sh` → **0**. La sección es **nueva**, no una reorganización. Y el paquete de un rol **no
podía** llevar las filas por alcance: el alcance de lectura por defecto del test-writer es `contract`
+ `tests` ⇒ `docs/systemPatterns.md` quedaba fuera ⇒ las filas tienen que **viajar en el paquete**,
no en un archivo que el rol debe abrir. El estado de un ADR **no es derivable** (cuatro vocabularios
y tres formatos de estado, reemplazos parciales) ⇒ la columna de estado **la declara quien mantiene
la tabla**, no se re-deriva.

**Qué cambió en el uso real.**
- **Una decisión vigente puede viajar en el encargo.** Campo **opcional** `current_decisions` del
  request, declarado con `prepare --current-decision <JSON>` (**repetible**: cada valor es una fila
  JSON, y las filas quedan en el **orden declarado**). Sin el campo, el paquete es **byte-idéntico**
  al vigente **dentro de una misma revisión** (INV-2): la aditividad es intra-revisión y así se
  declara.
- **La forma de la fila la valida el producto; el contenido, el proyecto.** Conjunto **cerrado** de
  seis claves (`file`, `state`, `summary`, `roles`, `reference` y `superseded_by` **condicional**:
  exigido si `obsoleto`, prohibido si `vigente`): `file` debe **existir en el proyecto**; `state` ∈
  {`vigente`, `obsoleto`}; `summary` de **una línea**; `roles` no vacío dentro del vocabulario
  cerrado (los cinco roles delegados **más `orchestrator`**). El CLI **no** parsea el documento del
  proyecto: acoplar el producto a un formato de un markdown ataría el byte del paquete al estado de
  la tabla.
- **La fila debe nombrar al rol del paquete** (fail-closed, nombrando la fila y el rol): una fila
  que no concierne al rol **no viaja**, ni siquiera por descuido. Y **una fila `obsoleto` no es
  admisible en un paquete**: la decisión reemplazada **conserva su sitio en la tabla** (la historia
  importa) y **no se distribuye** — la distinción es del producto, no de la disciplina.
- **Tope de 32 filas por paquete, fail-closed.** 33 filas se rechazan nombrando el número declarado
  y el tope, **sin publicar nada**. El 32 es un **número declarado**, no un tope atado al inventario
  (que no sería un tope) ni derivado de él en ningún momento.
- **Sección `## Current decisions` sólo con filas.** Se emite entre `## Contract` y el bloque de
  plan-task, una entrada por fila, con sus cinco campos. Sin filas (o con la lista vacía) **no hay
  diferencia de bytes**; un rol sin filas aplicables recibe un paquete byte-idéntico al de hoy. El
  **test-writer no gana acceso a `docs/`**: las decisiones le llegan **dentro** del paquete, no por
  el alcance.
- **La tabla del proyecto es el índice, y su dueño es el orquestador.** «Decisiones vigentes» es el
  **primer H2** de `docs/systemPatterns.md` (en la plantilla del Memory Bank: `## Current
  decisions`), una fila por decisión. El **upkeep** —agregar la fila al aprobarse un ADR y marcar la
  anterior `obsoleto` **conservándola** con su reemplazo— vive en `references/stage-5-merge.md`
  §5.4 y **no agrega casillas al exit gate de stage 5**. El **reviewer** la revisa con dos
  comprobaciones (**alineación** con `docs/adr/` y **respeto** de las decisiones vigentes de su rol),
  cuyo procedimiento está en su dueño canónico `references/stage-4-review.md`; una fila desalineada
  es un **hallazgo** con `file:line`, veredicto y condición de cierre, **no** una puerta.
- **El principio de general antes que específico tiene una casa y dos obligaciones.** El texto
  normativo **y su límite** viven en **un único archivo** del skill instalable
  (`skills/cdad-cycle/references/design-principles.md`); el **architect** debe considerar las
  alternativas generales y específicas y explicar el criterio elegido; el **reviewer** debe evaluar
  consecuencias reales —duplicación que puede divergir, complejidad innecesaria, pérdida de
  capacidades y acoplamiento— con el límite explícito de que **la falta de una abstracción no es,
  por sí sola, un defecto**. El deber de cada rol es **duty**, no una copia: viaja **completo** por
  la fuente del rol y por el bloque estático del paquete (en la ruta de paquete el rol **no** carga
  el skill) y **nadie re-enuncia** el texto del principio.
- **El CAS se hace contra el digest base, y reconciliar es re-despachar.** Ante conflicto
  («current digest does not match expected_previous_sha256 (CAS): refusing to overwrite») la salida
  es **re-despachar al rol con un paquete nuevo sobre la base nueva**: **no** se fusiona a mano ni
  se **actualiza el digest esperado** para forzar el paso (eso borraría el cambio del otro escritor).
  El orquestador, que mantiene la tabla, escribe sus propias filas **directamente en `docs/`** con
  su commit y no comparte base con el scribe. La regla es **general** (afecta a toda
  materialización con CAS) y vive en el protocolo de materialización, no en el caso de la tabla.
- **El validador permanente lleva invariantes duraderas, no fotografías.** El bloque de
  `tests/validate-consistency.sh` comprueba **propiedades de coherencia** (cada fila apunta a un
  archivo que existe bajo `docs/adr/`; toda fila `obsoleto` nombra un reemplazo que existe; todo
  `roles` está en el vocabulario cerrado; ninguna fila re-enuncia el texto del principio; la nota
  declara que el estado lo declara quien mantiene la tabla) y **no nombra ningún ADR** ni fija
  ningún conteo ⇒ **aprobar un ADR nuevo o reemplazar cualquiera de ellos —ADR-034 incluida— no
  obliga a tocar los tests**. El inventario sembrado (26 filas, 8 `Proposed` excluidos) es
  **evidencia puntual** de la siembra, no una aserción permanente.
- **La plantilla nace sin decisiones.** La sección de la plantilla tiene encabezado y separador y
  **cero filas de datos**; la forma de la fila se explica **en prosa**, fuera de la tabla (una
  línea que empieza por `|` la leería el comprobador como una decisión). Un proyecto **sin**
  `docs/adr/` **no queda bloqueado**: `prepare` da rc=0 y sin sección, y el render con la lista
  vacía es byte-idéntico.

**Producto (U1 → U2 → U3 → U4 → U5 → U7 → U6 + el arreglo B-1).** Rango `86cb942..a815f9b`:
**67 commits, 65 archivos, +14801/−13**; de ellos **21 archivos de producto, +435/−4**
(`cdad_packet.py`, `design-principles.md` **nuevo**, las tres referencias de procedimiento, la
plantilla del Memory Bank, el esquema del request, los dos bloques estáticos, las dos fuentes de
rol y los **8 agentes regenerados** por el generador) y `tests/` suma **7 archivos nuevos,
+5301/−0**. Orden real: **U1** (la fila declarada, su forma y el tope) → **U2** (la sección aditiva
del render) → **U3** (el principio: una casa y las dos obligaciones) → **U4** (la tabla y su upkeep:
sólo plantilla y procedimiento) → **U5** (la siembra de este repo, materializada por el
orquestador con la aprobación del ADR-034 registrada) → **U7** (la verificación duradera de la
siembra) → **U6** (recorrido real) → **B-1** (la plantilla nace sin decisiones). Último commit de
producto: `fc1179b`.

**Aceptación real (U6, PD-12) — proyecto descartable, sin despliegue a HOME.** **E1..E7 y V-5
cumplen**: la fila llega al rol nombrado y una fila ajena se rechaza nombrando el rol; la fila
reemplazada queda `obsoleto` en la tabla y fuera del paquete; sin filas aplicables el render es
byte-idéntico (mismo digest a los dos lados); una fila que apunta a un ADR inexistente se rechaza y
el reviewer la reporta como **hallazgo**; un proyecto sin `docs/adr/` funciona sin cambios; el
principio está en el árbol instalable y lo nombran los dos roles; y la **cadena del CAS** corre
completa (base D0 → propuesta → D1 con la fila del orquestador → materialización **rechazada** por
conflicto → **re-despacho** con paquete nuevo sobre D1 → materialización correcta → documento final
que **conserva la fila del orquestador** y trae los cambios del rol, con los bytes aplicados
identificados). **V-5**: un paquete publicado antes de un cambio de las fuentes de instrucción **no
es recibible después** («packet differs from its canonical rendering»); la salida es terminarlo bajo
la revisión con la que se publicó o preparar uno nuevo bajo la vigente.

**Review (etapa 4) — 2 bloqueantes / 3 opcionales / 1 abstención.** **B-1** (la plantilla nacía
declarando una decisión ficticia en proyectos sin ADR): cerrado con **RED/GREEN** (`4d71ccc` →
`fc1179b`) — la plantilla copiada literalmente a un proyecto sin ADR ahora pasa el comprobador
permanente. **B-2** (el GREEN de U7 escribió fuera del alcance autorizado: `docs/**` no estaba en
su paquete y el recibo declaraba `scope_validation: unknown`): resuelto por el **orquestador**, que
auditó el diff (**una sola línea**: las barras crudas de una celda partían la fila en columnas
espurias) y **adoptó la corrección bajo su propia autoridad** (el upkeep de la tabla es suyo,
ADR-003), **sin reescribir historia ni cambiar el oráculo**.

**Gates y despliegue.** `make validate`: **Assert PASS: 182 / Assert FAIL: 1**, y el único FAIL es
**F011** —deriva entre el árbol instalado y el repo, clase **DT-8**, preexistente y ya declarada.
**La suite de cierre no se ejecutó**: la corre **una vez quien cierra** (política declarada en el
paquete). **NO hay despliegue en HOME**: el recorrido se hizo sin tocar la instalación, **por orden
del owner** (hay una **sesión activa en OpenCode** que no se debe tocar) ⇒ el redespliegue queda
pendiente de esa orden, y la copia instalada **no** contiene la feature.

**Decisiones relevantes.**
- **DEC-1** — un **campo opcional del request** más una **sección aditiva del render**; el CLI
  **no** lee la tabla del proyecto (acoplaría el producto a un formato de documento) y el
  contenido no viaja como texto libre (no sería verificable).
- **DEC-2** — la fila tiene una **forma cerrada de seis claves** con `superseded_by` condicional: la
  **misma** forma sirve al documento y al request ⇒ el orquestador construye el request desde la
  tabla sin traducción.
- **DEC-3** — el estado de la fila es `vigente` | `obsoleto`, y **sólo lo vigente viaja**; el
  binario del plan se respeta y se hace verificable.
- **DEC-5** — el vocabulario de consumidores incluye `orchestrator` (gobierna el ciclo aunque no sea
  un rol despachado por paquete; una fila que lo nombra sólo no viaja).
- **DEC-6** — el tope es **32**, fail-closed y con salida; un tope atado al inventario no sería un
  tope y uno por bytes no sería determinista.
- **DEC-7** — el `reference` **no lo verifica el CLI** (puede apuntar al árbol instalado, que el CLI
  no resuelve) ⇒ esa comprobación es del reviewer; el `file` sí se comprueba.
- **DEC-9 / DEC-10** — el principio vive en una **referencia nueva** del skill, no en `SKILL.md`
  (una regla de diseño para dos roles no puede cargar a todos) ni en la referencia del reviewer
  (mezclar dos dueños crea dos fuentes); el deber del reviewer vive en su referencia canónica.
- **DEC-11** — la tabla se mantiene en el **evento «ADR aprobado»**, no en el cierre de cada
  feature: atarla al cierre la deja envejecer sin evento que la mueva. El **exit gate de stage 5 no
  cambia**.
- **DEC-13** — el **CAS contra el digest base** y la reconciliación por **re-despacho**; nunca
  fusionar a mano ni subir el digest esperado. Es **general antes que específica**: vive en el
  protocolo general de materialización, no como parche de esta tabla.
- **DEC-15 / DEC-16** — el validador permanente lleva **invariantes duraderas** y **ninguna
  excepción por identidad**: el inventario y la ficha de una decisión concreta son **evidencia
  puntual**, no un oráculo.

**Deuda detectada (abierta).**
- **O-1** (review): la pertenencia a `docs/adr/` se comprueba **sólo por prefijo** ⇒ una ruta con
  `..` que apunta a un archivo existente en `docs/` pasa el comprobador. No afecta las filas
  sembradas ni el CLI (que resuelve rutas); queda como deuda del comprobador. *Cierre*: comprobar
  contención sobre la ruta resuelta, con su negativo.
- **O-2** (review): el **ADR-034 conserva marcas contradictorias de borrador** (encabezado
  `Accepted` y a la vez «aprobación pendiente» y `Status: Proposed`). La aprobación separada sí
  está registrada ⇒ no falta aprobación, sobran marcas residuales. *Cierre*: limpiarlas y
  describir el borrador como fase histórica.
- **O-3** (review): falta el **bloque U3** que el plan pedía en `tests/validate-consistency.sh` (los
  tests Python sí comprueban fuente única, obligaciones y límite) ⇒ discrepancia de superficie de
  validación. *Cierre*: incorporar la comprobación equivalente o registrar una enmienda que adopte
  el oráculo Python.
- **W-U6-1** — **fidelidad del rol**: en las dos propuestas del recorrido el scribe cambió líneas
  **fuera de lo encargado** (negrita, una palabra, un espacio final) ⇒ el CAS protege la
  concurrencia, **no** la fidelidad. La salida existente es la **revisión del diff del Memory Bank
  antes de aprobarlo**.
- **W-U6-2** (**a verificar**) — el adaptador **volvió a despachar un paquete que ya tenía entrega
  completa y recibo durable** (el script del recorrido re-despachó el paquete viejo porque `prepare`
  había fallado, dos veces; dos sesiones huérfanas, de sólo lectura). **Causa no investigada** ⇒ se
  registra como deuda. *Cierre*: reproducción descartable con argumentos, estado previo, recibo y
  registro del nuevo despacho, sin tocar las sesiones activas.
- **W-U6-3** — **ergonomía del CAS hacia el Memory Bank**: el adaptador entrega **una sola parte
  `role-report`**, cuya raíz permitida es la carpeta de la spec ⇒ materializar hacia el Memory Bank
  exige que el orquestador reciba la misma entrega con un descriptor propio de clase ya existente
  en la política cerrada. Las clases existen; lo que falta es que el adaptador las declare.
- **`scope_validation: unknown`** (deuda heredada de 006-005, ya declarada): ningún productor de
  `observed_changes` ⇒ el recibo sale siempre en `unknown` y el control mecánico «el rol con
  escritura no salió de su alcance» **nunca corre**; quedan el mapa de permisos del agente y la
  revisión del diff. El caso de B-2 es **una instancia más** de esta deuda.
- **Deuda declarada por la spec**: **L-1** compatibilidad entre revisiones (un paquete publicado
  antes de un cambio de las fuentes de instrucción no es recibible después; el renderer no se
  corrige) · **L-3** la **completitud** de la tabla no está garantizada mecánicamente (el producto
  garantiza la forma, no que toda fila vigente fuera declarada) · **L-4** la verificación del
  `reference` es del reviewer · **L-5** el exit gate de stage 5 no menciona la tabla ⇒ el kind
  `scribe-systemPatterns` queda como capacidad latente · **L-6** el esquema del request ya no
  describe el request vigente (brecha de `agent`, no corregida aquí) · **L-7** el producto **no
  verifica la base** del CAS: la disciplina es del procedimiento.
- **Pendientes de cierre**: **suite completa** (la corre quien cierra) y **redespliegue en HOME**
  (orden del owner). Heredadas y sin cambio: **DT-8** (F011 por deriva de la copia instalada) y el
  **flake conocido del margen de la espera bajo carga** (clase DT-9).

**Estado del epic y siguiente trabajo en cola.** `epic-006-opencode-concurrency` queda con **6/6
features cerradas** (006-001, 006-002, 006-003, 006-004, 006-005, 006-006) ⇒ **no queda ninguna
feature en cola** en el epic. El siguiente trabajo **no es una feature**: es el **cierre del epic**
(acto de nivel epic, con su propia evidencia) y, antes, los **dos pendientes de cierre** de esta
feature: la **suite completa** y el **redespliegue en HOME**, que espera la orden del owner.

## 2026-10-20 — Feature: 006-006-spec-plan-review (epic 006)

**Cerrada el 2026-10-20 (ciclo técnico completo; el gate de suite completa lo corre quien cierra, política
declarada en el paquete).**
Quinta unidad de `epic-006-opencode-concurrency`: la **revisión independiente de un borrador de especificación
antes del RED**, como capacidad de primera clase del recorrido y no como rodeo. **Contrato:** `spec.md` sha256
`4d029a11…` (PD-1..PD-16, INV-1..INV-13, D-1..D-15, V-1..V-8) + `plan.md` sha256 `1abe9e7b…`, aprobados el
2026-10-20 por el orquestador bajo la **HITL delegada del epic** (el owner la mantuvo ese día), tras
`plan-review-001..004` (B-1..B-4 cerrados) y con la **errata B-5** aceptada en la aprobación. **El epic NO se
cierra.**

**Problema medido (no presupuestado).** En **otro proyecto activo** no se pudo pedir la review de un borrador de
spec: el reviewer rechazó dos paquetes con razón — el contrato por defecto del reviewer es la spec **aprobada**,
el plan de la épica no es admisible para el reviewer, y `draft-plan` **exige `plan-tasks`**. El hallazgo central
del discovery: el CLI **no exige tareas, exige la forma** («el objeto está modelado como un plan»). Medido:
`{"tasks": []}` pasa las tres validaciones ⇒ la puerta no exige tareas, exige la *forma de plan*. Tres rechazos
mecánicos y correctos, no un error de uso. La capacidad ya existía (`plan-review` + `draft-plan`) pero **no
estaba en el recorrido principal** (0 ocurrencias en `agents/`, `sources/` y `SKILL.md`; el gate 2→3 y el exit
gate de la etapa 2 no la nombraban) y **sólo admitía planes**.

**Qué cambió en el uso real.**
- **El reviewer revisa un borrador de spec sin plan, de spec+plan o de otra feature**, con la forma **declarada**
  en el encargo: `prepare --object-kind {spec,plan}`, más `--spec-path` y `--spec-version` cuando la revisión
  cubre los dos documentos. La forma **nunca se infiere** (ni por el contenido, ni por la ruta, ni por el nombre
  del kind) y **por omisión es `plan`**, con lo que el comportamiento vigente no cambia: olvidar la bandera
  produce el rechazo de siempre, nunca una aceptación silenciosa. Una spec se revisa **sin tareas artificiales**
  (no se inyecta un bloque `plan-tasks` en la spec); los checks del plan se aplican **sólo** al documento cuya
  forma es `plan`.
- **El dictamen nombra el objeto y su digest y se materializa en la carpeta de la feature activa.** Con un
  borrador de **otra** feature, el paquete deja visible que la feature activa es una y el objeto es de otra; el
  dictamen aterriza **sólo** en `docs/specs/<feature activa>/plan-review.md` (la tabla de destinos no se amplía) y
  nombra el objeto y su digest. La **identidad doble** es por digest: con spec+plan, el plan es el principal y
  la spec el acompañante, con **ambos** digests calculados de los bytes; una corrección en cualquiera de los dos
  invalida la cobertura de la revisión anterior (re-review **focal**, no ronda nueva).
- **Nada aprueba.** El dictamen no lleva marca de aprobación, el recibo queda `pending`, la autorización de
  materialización exige `approval_effect: false`, el estado no registra aprobación y el test-writer sigue
  bloqueado sin el pin de la aprobación de la spec. La revisión del **resultado** (etapa 4) no se toca.
- **La exención entra en la identidad sólo si se declara.** El owner puede eximir la revisión; la exención es
  explícita y viaja **en la misma entrada de `stage_history` que la aprobación** (clase `gate`, con
  `--exempted-by`, `--exemption-reason`, `--requested-by`, `--delegated`). Sus cuatro campos entran en el
  payload de identidad **sólo en las invocaciones que los declaran**, como **un** bloque `exemption` condicional:
  sin exención declarada, el payload y la `transition_key` son **byte-idénticos** a los del producto vigente ⇒
  **las identidades históricas se conservan** y **no hay enmienda** de 005-012 PD-11, 005-014 PD-23 ni
  006-005 PD-19(b) (sus oráculos siguen verdes sin cambio de oráculo). Repetir la misma orden es **no-op**;
  **volver a un valor anterior** (A→B→A) **no** puede perderse en silencio: la invocación que colisiona con una
  entrada histórica que **no** es la vigente se **rechaza explícitamente** (nombra la clave que colisiona, la de
  la vigente y las dos salidas), nunca un no-op que deje la anterior vigente.
- **Gate 2→3 supervisado, con `plan-review.md`.** El gate 2→3 y el exit gate de la etapa 2suman un criterio: el
  artefacto `docs/specs/<feature>/plan-review.md` existe y cada bloqueante está resuelto o descartado con razón
  escrita. **Ninguna de esas superficies es un bloqueo del CLI**: medido, con aprobación vigente y **sin**
  dictamen, `prepare` de un rol de construcción **se acepta** (rc=0) — el gate es **supervisado**; y **sin**
  aprobación, el mismo `prepare` **se rechaza** con `approval pending`. La re-entry del dictamen y la política
  de compatibilidad quedan declaradas en `re-entry.md`.
- **Política de compatibilidad entre revisiones.** Los digests de las fuentes de instrucción **son parte de la
  identidad del paquete** y la recepción re-renderiza y compara ⇒ un paquete publicado antes de un cambio de esas
  fuentes **no es recibible después** (rechazo ruidoso y recuperable: «packet differs from its canonical
  rendering»). La **salida** está declarada donde el orquestador consulta: **terminarlo bajo la revisión con la
  que se publicó, o preparar uno nuevo bajo la vigente**. El CLI **no** distingue la causa ni ofrece la salida:
  es **declaración de procedimiento**, no un cambio del renderer.
- **Reemplazo de un paquete de borrador preparado (W-1, corregido).** Antes, un paquete `plan-review`
  **preparado y nunca despachado** no se podía reemplazar (`prepare` rechazaba por paquete activo `prepared`;
  `disposition` sólo admite paquetes despachados; `--replace-packet` validaba contra el contrato aprobado y
  rechazaba el `draft-plan`): tras corregir el borrador, el usuario quedaba **sin salida** para la re-review.
  Ahora `prepare --replace-packet` **reemplaza un paquete de borrador preparado**, conserva la **forma**
  (`kind`, `path`, `plan_version`, `object_kind`, `spec_path`/`spec_version`) y **recalcula sólo los digests**
  desde los bytes actuales; la ruta del contrato aprobado queda **byte a byte idéntica** a la de antes.

**Producto (U1, U5, U2, U3, U4 + el arreglo W-1).** Rango `7f39e24..HEAD`: **59 commits, 46 archivos, +11745/−61**;
de ellos **14 archivos de producto, +499/−53** (`cdad_packet.py` +410/−… , `SKILL.md`, los tres references de
procedimiento, el substage y la regla de rol, la fuente del rol y los seis agentes regenerados) y `tests/` suma
**6 archivos nuevos, +5030/−0**. **Último commit de producto: `de629b8`** (W-1). Orden real:
**U1** (el objeto declarado en el contrato) → **U5** (la exención registrada e identificada) → **U2** (la fuente
canónica de «qué se revisa») → **U3** (el recorrido principal, el gate 2→3 y la política de compatibilidad) →
**U4** (el rol y los agentes generados) → **U6** (recorrido de aceptación) → **W-1** (arreglo del recorrido).

**Aceptación real (U6, proyecto descartable; nunca HOME, nunca el proyecto activo).** Los siete escenarios
**cumplen**: **E1** spec sin plan (rc=0, paquete con `form: spec` y purpose «draft spec for review», recibo
`pending`, dictamen materializado con sha idéntico al del part, digest nombrado) · **E2** spec+plan (los checks
del plan aplican al plan; los dos digests fijados coinciden con `sha256sum`; el dictamen nombra los dos) · **E3**
borrador de otra feature (rc=0, `feature_id` ≠ carpeta del `contract.path`, un target en la carpeta del objeto ⇒
rc=2 «outside the allowed root…», el dictamen nombra el objeto y su digest) · **E4** re-review por digest (digest
fijado ≠ `sha256sum` tras la edición ⇒ la revisión anterior no cubre los bytes nuevos; con bytes sin cambiar
coincide) — **con el hallazgo W-1 y su corrección** · **E5** el dictamen no aprueba (sin `approved_by` en el
estado, recibo `pending`, `prepare --role test-writer` con el borrador ⇒ rc=2 «draft-plan contract is
reviewer-only», `approval_effect: false`) · **E6** coherente que no alcanza la intención (juicio semántico: el
dictamen declara «BLOCKING · Bucket: h…» y propone un remedio estructural) · **E7** compatibilidad entre revisiones
(el caso de dos fases: publicación con las fuentes de entonces, recepción con la copia ya cambiada ⇒
`termination: blocked` con el diagnóstico de la diferencia con el render canónico; la salida declarada en
`re-entry.md` **no** la ejecuta el producto). El recorrido de **dos revisiones** y el **A→B→A** de U5 se
ejecutaron con el CLI real en proyectos sintéticos dentro del focal (5 casos de recorrido verdes; el focal
completo, 14 passed).

**Review (etapa 4) — apta para cierre, 0 bloqueantes / 2 opcionales.** El reviewer (familia distinta a la del
implementer) verificó los hashes del contrato, la política y las tres fuentes; reprodujo los focales (**72
passed**) y las regresiones declaradas (**62 passed**); no encontró bloqueantes observables. **O-1** (automatizar
la selección de vigencia exigida por la errata B-5) ⇒ **deuda**. **O-2** (actualizar la evidencia de aceptación
tras W-1) ⇒ **aplicado** en la misma ronda (la fila E4 y el estado de W-1 quedaron actualizados). El reviewer
**no** certificó `make validate` (los informes registran **168 PASS / 1 FAIL**, atribuido a F011 ambiental) y **no**
ejecutó la suite completa (corresponde a quien cierra).

**Gates.** `make validate` en el GREEN de cierre: **168 PASS / 1 FAIL = F011** (deriva ambiental de la copia
instalada, clase **DT-8** preexistente). **Suite de cierre: 1404 passed, 5 skipped**, corrida por quien cierra.

**Desplegado.** El owner autorizó el despliegue en HOME de esta feature el 2026-10-20 («cuando necesites hacer
despliegue hazlo») y existe el script de despliegue de la feature (`.cdad/local/deploy-006-006-u4.sh`:
respaldo previo, `make staging`, `install.sh --force`, `install.sh --check`). La evidencia de U6 declara que el
producto probado fue **la copia de HOME desplegada desde HEAD `a276531`** (U1–U5 incluidas). Al cierre se **redesplegó en `86cb942`** (código `de629b8`, con W-1; respaldo en `archive/`), y W-1 se verificó con el CLI desplegado (`u6-acceptance.md`, sección «W-1 tras el despliegue del cierre»).

**Decisiones relevantes.** **D-1** la forma la **declara el encargo** (`contract.object_kind`), nunca el objeto:
se rechazaron la inferencia por el contenido, por la ruta y el bloque `plan-tasks` vacío dentro de la spec (que
deja el `purpose` mintiendo y conserva el modelo mental que el rodeo repite). **D-2** por omisión la forma es
`plan` ⇒ los 11 archivos de test que comparten el fixture de borrador **no se tocan** y el oráculo vigente de la
puerta `plan-tasks` se conserva sin cambio. **D-3** la identidad doble viaja como **dos documentos fijados por
digest**, no como una cadena de versiones (el digest es lo comparable con `sha256sum`). **D-4** los checks del
plan se aplican **al documento cuya forma es `plan`**, sin excepciones ni listas de excepciones. **D-5** la
revisión es **siempre obligatoria**, con profundidad proporcional; **no hay exención por defecto**. **D-6** la
exención se registra **en la entrada que abre el gate** (se rechazaron la entrada libre, la clase de transición
nueva, el texto en la `note` y el `approved_by`). **D-8** el dictamen de un borrador de otra feature **vive en la
carpeta de la feature activa** y nombra el objeto; ampliar la tabla cerrada de destinos quedó fuera de alcance.
**D-9** «el dictamen nombra el digest» es **obligación de procedimiento**, no un enforcement nuevo en
`materialize` (el CAS protege el destino, no el objeto; atar texto libre a un digest haría frágil la recepción).
**D-10** el gate 2→3 es **supervisado**: un bloqueo duro en el CLI estaba excluido. **D-11** se conservan los
nombres (`draft-plan`, `plan-review`, `plan_version`, `plan-tasks`), con la **deuda de nombre declarada** (cambiar
el enum cerrado de kinds, los enums de schema, la plantilla y los oráculos de 004-003 es un trabajo acotado pero
de coordinación). **D-12** la compatibilidad se **acota a una revisión del producto** y su consecuencia **se
declara, no se corrige** (mismo precedente que 005-003 T6/F3: consequence inherente al contrato de paquete,
ruidosa y recuperable). **D-13/D-14** la exención entra en la identidad **sólo cuando se declara** (forma
condicional): es el precio de conservar las identidades ya registradas, y por eso **no hay enmienda** de ninguna
garantía anterior. **D-15** la colisión con una entrada histórica que **no** es la vigente **se rechaza**: escribir
una segunda entrada con esa clave la dejaría inerte para la vigencia y la búsqueda por clave seguiría resolviendo
a la vieja ⇒ la pérdida en silencio, otra vez. **Trade-offs declarados:** el gate 2→3 puede saltarse (el CLI no
verifica el dictamen; la mitigación es la disciplina del gate, no el enforcement); la exención es un **acto de
autoridad registrado, no una firma**; la retirada de la exención **no tiene fórmula de identidad propia** y se
registra con un **valor distinguible**; el payload de identidad **deja de ser uniforme** (la regla vigente «toda
clave presente; un insumo ausente vale `null`»).

**Deuda detectada (abierta).**
- **O-1 (review, opcional)** — **automatizar la selección de vigencia** exigida por la errata B-5: los tests
  comprueban que `prepare` acepta el contrato, pero eso **no demuestra** que el selector devuelva **sólo B** y
  después **sólo C**, excluyendo las entradas sustituidas (comparten pin). El reviewer lo verificó **por
  separado** con las transiciones reales (`selected_only_B=True excludes_A=True`; `withdrawal_rc=0
  selected_only_C=True excludes_A_and_B=True`) ⇒ **no se observó defecto de vigencia; falta conservar esa
  comprobación como regresión automática**. Remedio: añadir las aserciones del selector al recorrido, manteniendo
  `prepare` como comprobación adicional de habilitación.
- **W-2 (observación)** — el adaptador termina con **rc=0** aunque el resultado sea `termination: blocked` (E7);
  el diagnóstico va en la salida JSON. Observación, **no se cambia**.
- **Pendientes de cierre de esta feature** — **suite completa** (la corre quien cierra) y **redespliegue del fix
  W-1** (no registrado en el repo; la fila E4 apunta a un «despliegue del cierre» cuya sección no existe).
- **Deuda declarada por la spec (§10)**: **deuda de nombre** (`draft-plan`/`plan-review`/`plan_version`/
  `plan-tasks` siguen diciendo «plan» aunque el objeto sea una spec) · **deuda de la puerta `plan-tasks`** (el
  nombre del token) · **ADR-013 O-C** (el `contract.path` de un borrador puede ser cualquier ruta del proyecto;
  fuera de alcance) · **deuda de la ambientación** (el dictamen de otra feature no puede vivir en su carpeta) ·
  **deuda de la exención en el CLI** (el nombre del owner viaja como texto declarado, no como identidad
  criptográfica) · **deuda de la compatibilidad entre revisiones** (declarada, no defecto) · **deuda de la
  identidad de la retirada** (se registra con un valor distinguible). **La frontera de 005-014 E-4 no se amplía**:
  sigue REFERIDA a las entradas sin `transition_key_payload`.
- **Heredada de 006-005, sin cambios**: **U6-2** (ningún productor de `observed_changes` ⇒ `scope_validation`
  queda `unknown`) · **O-2** (coordinador fuera de la raíz ⇒ copia global de los agentes) · **D-U65-4** (sin
  write-ahead nativo) · **D-U65-5** (recuperar del store la salida del huérfano como entrega tardía) · **O-2 y O-3
  de las reviews de 006-005** · el **límite de transporte del paquete nativo** (la cabecera JSON de `PACKET.md`
  supera 2000 caracteres y la herramienta de lectura del runtime la trunca) · **DT-8** (F011 por deriva de la
  copia instalada) y el **flake conocido del margen de la espera bajo carga** (clase DT-9).

**Lecciones de proceso.**
(1) **Una puerta puede exigir la forma y no el contenido**: el CLI no exigía tareas, exigía el token `plan-tasks`
— y el rodeo del consumidor nacía de modelar el objeto como un plan, no de una regla unreasonable. (2) **Un no-op
que responde antes de examinar el estado pierde cambios en silencio**: la rama de no-op decidía por la clave y
respondía **antes** de mirar `--supersedes` y la aprobación vigente, de modo que el recorrido A→B→A devolvía
éxito **dejando vigente la aprobación anterior**; la corrección **califica** la rama (replay histórico ≠ intento
de sustituir la vigente) en vez de eliminarla. (3) **Una identidad uniforme no es gratis**: cuatro claves `null`
cambian la clave **también** de las invocaciones sin exención y de las demás clases ⇒ la forma **condicional**
(una clave, sólo cuando se declara) es el precio de conservar las identidades ya registradas. (4) **Un oráculo
puede ser cierto y el consumidor no poder distinguirlo**: `prepare` recibe el contrato, **no la clave de la
aprobación** (A y B comparten contrato y pin), así que la vigencia se comprueba con el **selector real**, no con
`prepare` — de ahí la errata B-5.

**Estado del epic.** `epic-006-opencode-concurrency` sigue **abierto** (`features-loop`): **006-001, 006-002,
006-003, 006-005 y 006-006 `done`, 5/6**. Queda **006-004-active-decisions-table** (enmienda 003, que también
vehiculiza el principio de general antes que específico, enmienda 005 ⇒ **ADR-034**), en el **orden que fijó el
owner** (**006-005 → 006-006 → 006-004**). **Siguiente:** `006-004-active-decisions-table`.

---

## 2026-10-20 — Feature: 006-005-native-path-parity (epic 006)

**Cerrada el 2026-10-20 (ciclo técnico completo; el gate de suite completa lo corre quien cierra, PD-21).**
Cuarta unidad de `epic-006-opencode-concurrency`: la **paridad del camino nativo**. El orquestador deja de
reconstruir el protocolo a mano: hay **una entrada operativa** (`cdad_dispatch.py`) con **dos vías** (externa y
nativa), **un solo registro de intento por despacho**, **el kind de la parte entregada derivado del rol y la
subfase** (en las dos vías), **el temporal del test-writer escribible de verdad** y **camino mecánico a `failed`**.
**Contrato:** `spec.md` sha256 `3a824be3…` (PD-1..PD-26, INV-1..INV-16, D-1..D-17) + `plan.md` sha256
`21d6954e…`, aprobados el 2026-10-18 bajo la **HITL delegada del epic** (PD-19, runtime explícito, modelo y
credencial fuera de `runtimes.json`: decisiones del owner). **El epic NO se cierra.**

**Problema medido (seis brechas, contadas una a una).** La delegación nativa ejecutaba el encargo pero **no
trasladaba la preparación** que el adaptador externo sí hace: nadie registraba el intento (sin eso `receive`
rechaza), ningún encargo concedía un temporal que el test-writer pudiera **escribir**, y un intento que no
volvía **no tenía camino mecánico a `failed`** (la disposición lo dejaba en `pass`). A eso se sumaban, ya medidas
en uso real, la **entrada del orquestador sin configuración declarada** (con un exec-config local y un rodeo de
entorno) y el **agente por stack** que nunca se resolvía. Sexta brecha: el **orquestador que reconstruyó el
protocolo a mano**. **Todos los deliveries del reviewer de esta feature llegaron copiados a mano** porque el
kind fijo (`role-report`) no lo admitía: el rodeo ya medido, escalado a defecto real.

**Producto (U1a–U5, U7 + ocho amendments de la aceptación + dos rondas de review-fix).** Rango `43986e2..HEAD`:
**194 commits, 122 archivos, +30663/−654**; de ellos **24 archivos de producto, +2769/−435** y `tests/` suma
**32 archivos, +16451/−209**. **Último commit de producto: `88491b2`.**

- **U1a** — `skills/cdad-cycle/scripts/cdad_dispatch.py` (**nuevo**, 1216 líneas): la capa de configuración;
  `--runtime` **obligatorio en todos los verbos** (la entrada no resuelve runtime de ningún documento), la
  sección por runtime en `runtimes.json` (**fuente única**), el **barrido de `--exec-config` por token exacto,
  previo al parseo del verbo** (error de uso con la correspondencia clave por clave) y el **paso acotado de
  migración** (`migrate`, escribe la sección **sólo si no existe**; `--dry-run` no escribe); plantilla de
  `runtimes.json` en `install.sh` (**sólo si no existe**, fuera del manifiesto). RED `5dbc854` → GREEN `4052939`.
- **U1b** — la entrada única con los cuatro verbos (`dispatch` por defecto, `record`, `capabilities`, `migrate`);
  `record` = **cuerpo único** de observación + registro + escenificación; la **interfaz común deja de registrar**
  y **relaya** el `attempt` del módulo (un registro por despacho). RED `27b85a4` → GREEN `3af53f1` (con dos
  testfix declarados: `8bbbdd4`, `b28be34`).
- **U1c** — el **agente viaja en el paquete**: `prepare` resuelve rol+`stack` y escribe `agent` en
  `REQUEST.json`; el conjunto cerrado del request lo admite como propiedad opcional; **el render no cambia**
  (`PACKET.md` byte-idéntico). RED `eab7e2f` → GREEN `e958a0c` (testfix `12e710a`).
- **U2** — el módulo de runtime: **credencial inyectada** en el entorno del cliente (sólo `mode: server`, nunca en
  `argv`/logs/registro), **agente del paquete**, **kind derivado de rol+subfase** (deja de ser la constante
  fija), `--capabilities` y `--observe` (una lectura `mode=ro`, acotada, sin polling), **correlación por la
  evidencia de su vía** y **fallo cerrado** ante un módulo sin la superficie nueva. RED `9a260c4` → GREEN `eb677a9`.
- **U3** — el temporal: clase `temporary` validada contra la política, `git check-ignore` en `prepare` y
  **permiso de edición del agente derivado** para las raíces declaradas, emitido **antes** de las barreras
  (con las dos colisiones probadas: ruta privada y directorio de derivados). RED `0b38f07` → GREEN `a7f1bea`.
- **U5** — **camino mecánico a `failed`**: la disposición con las condiciones aprobadas por el owner, idempotente,
  con `validate-state` VALID y el siguiente `prepare` desbloqueado. RED `43ee3a0` → GREEN `0a260ab`.
- **U7** — la **fila del scribe** de la tabla cerrada admite `role-report`: el informe del rol se materializa
  **dentro de `docs/specs/<feature>/`** y el **Memory Bank queda fuera de su alcance** (se rechaza nombrando la
  raíz permitida). RED `ba95af5` → GREEN `a2139c5`.
- **U4** — el **mandato con una sola entrada**: intake por el `entry`/`next` que el CLI ya calcula, secciones
  `delegation`, **borde de adopción** de la migración y referencia de re-entry por estado de llegada; agentes
  regenerados con `make agents` (nunca a mano). RED `3d23ad6` → GREEN `014bf2d` (testfix de oráculos `b76aa5d`).

**Aceptación real (U6, PD-22) — proyecto descartable, layout anidado, coordinador fuera de la raíz.** Los cinco
escenarios y la sonda **cumplen**: **E5** (migrar + `capabilities`; repetir la migración da rc≠0 sin pisar) ·
**E3** (externa con **sólo paquete y `--runtime`**: un registro I8 —el del módulo— con `model_reported` del
store, parte con kind derivado, `materialize` rc=0 con bytes idénticos; el informe del scribe como `role-report`
dentro de la carpeta de la spec y **rechazado** hacia el Memory Bank) · **E2** (el auxiliar **escrito con la
herramienta del rol** en las dos vías tras U6-7: la externa deniega `docs/` y escribe el temporal y `tests/`; la
nativa, desde la raíz, escribe el auxiliar y su test, el test pasa y el commit toca sólo `tests/`) · **E1**
(nativa verificada por (parent, moment) desde la carpeta contenedora y por (parent, moment, project) desde la
raíz; el registro es el del hijo real) · **E4** (intento que no vuelve) · **V-11** (`stack: odoo` de punta a
punta: `REQUEST.json.agent` = `cdad-test-writer-odoo`, `session_v2.agent` igual, un registro final, entrega
recibida). **`scope_validation` queda `unknown` en las dos vías** (U6-2, deuda): el recibo no puede probar la
escritura porque lo ignorado no aparece en el manifiesto.

**Enmiendas del recorrido (U6-1..U6-8), cada una con su RED/GREEN.** **U6-1**: `capabilities` no pasaba la
sección al módulo ⇒ el paso «migrar → verificar» no verificaba nada (`ed64092`→`caaab97`). **U6-3**: la llave
proyecto rechazaba al coordinador iniciado en la carpeta contenedora ⇒ pasa a **tres valores** (dentro ⇒ coincide;
**ancestro ⇒ no evaluable**; ajeno ⇒ contradicción) (`f6054ce`→`e7c39a5`). **U6-4**: el momento nunca era
evaluable contra el store real y la selección del hijo era arbitraria ⇒ unidades y **candidatos** explícitos
(`8fe0d8c`→`b06bd2f`). **U6-5 (decisión con dos reviews)**: el registro externo se escribía **al terminar** ⇒
una muerte del coordinador dejaba un callejón sin salida (`reconcile` decía que repetir era seguro y la
disposición se negaba) ⇒ **registro write-ahead** (`a0d96b5`+testfix `569682d`→`471db74`). **U6-6**:
`model_reported` con forma distinta entre vías ⇒ **paridad** (`12c29a7`→`ef88817`). **U6-7**: los agentes
generados llevaban la palanca `write: ask`, que la versión instalada **sí evalúa** ⇒ la externa escribía fuera
de alcance y la nativa no interactiva rechazaba todo ⇒ **palanca retirada del generador** (`8506674`→
`028cd79`); **U6-7b** además, los derivados **no heredan** la palanca de una copia instalada vieja
(`14c2b3c`+testfix `e58c0a8`→`58af287`). **U6-8**: el control comparaba la versión **escrita en la config**
contra el servidor ⇒ **versión por observación** (`c6e61aa`→`cca7e5d`).

**Review (etapa 4) — 3 bloqueantes / 2 opcionales**, y dos rondas de review-fix con sus re-reviews. **B-1**: los
allows de implementación **reabrían tests convencionales** dentro de esas raíces ⇒ **gana la barrera del rol**
(`3ca6597`, con la enmienda A-1 declarada en dos tests de la familia 004-002/005-008). **B-2**: `--session`
evitaba la normalización del momento y convertía contradicciones observables en `unknown` ⇒ **frontera común de
normalización** (momento y modelo). **B-3**: las instrucciones pedían un FINAL TEXT que la entrada no devuelve ⇒
**la externa consume el recibo de `delivery_ref`; la nativa escenifica con `record` y luego `receive`**. **Re-review**:
B-1 cerrado, B-2 cerrado **con un bloqueante nuevo (B-4)**: se había eliminado una llave no declarada y se acreditaba
identidad donde el contrato exige `unknown` ⇒ la llave expuesta sin declaración vuelve a ser `unknown`
(`88491b2`). **Re-review focal 2**: **sin bloqueantes nuevos; B-3 y B-4 cerrados**; único opcional (O-3, el focal
externo compara longitud y no identidad de bytes) queda como nit. Dictamen: *apta para cierre respecto de esa
re-review focal; quedan los gates propios del cierre*.

**Gates.** `make validate` en el GREEN de cierre: **168 PASS / 1 FAIL = F011** (deriva ambiental de la copia
instalada, clase **DT-8** preexistente; los validadores del repo pasan 168/169). **Suite completa: no ejecutada**
—PD-21: la corre **una vez quien cierra**. Es el gate que falta para el cierre formal.

**Despliegue.** Por orden del owner se desplegó en el entorno de instalación el fix **U6-7 + U6-7b + U6-8**
(`b69bbac`, Verify PASS, scripts instalados iguales al repo; los agentes instalados ya no llevan la clave
`write`). **Los review-fix (B-1..B-4) son posteriores a ese despliegue** ⇒ la copia instalada **no** los contiene:
el **redespliegue** queda pendiente y es operación de entorno, que **espera orden del owner**. Los derivados de
cada proyecto se rehacen desde la copia instalada en su próximo `prepare`.

**Decisiones relevantes.**
**D-1** una sola entrada con dos vías y **regla de transporte declarada**: mismo runtime que el orquestador ⇒
herramienta nativa + `record`; otro ⇒ despacho externo. **D-2** la integración se **extiende** al módulo por
destino que ya existe (no hay un módulo nuevo por runtime). **D-3** la correlación la produce **cada transporte**:
la externa por el **id de sesión que el módulo elige** (sin padre comparable, sin igualdad `directory == raíz`);
la nativa por **padre + agente + momento + proyecto por pertenencia**, con **umbral de discriminación** (la
acreditación positiva exige **al menos una llave discriminante**: padre, momento o proyecto; «agente» sólo no
acredita, porque dos despachos nativos concurrentes del mismo rol lo comparten) y **tres resultados con
consecuencia propia**: *verificada*, *no verificable* (`unknown`; entrega sólo con la garantía menor PD-6) y
*verificada e incorrecta* (**rechazo** que nombra la llave; nunca `unknown`, nunca entrega aceptada). **D-4** el
`kind` de la parte lo fijan rol y subfase en las dos vías (y la fila del scribe admite `role-report` con el
Memory Bank fuera de alcance). **D-5** el temporal es una clase de scope **escribible**, y su legitimidad se
prueba con una **escritura real** con la herramienta del rol, no con `scope_validation`. **D-6** la clave del
`agent` se completa en `REQUEST.json` y **no** entra al render. **D-7** el write-ahead: **provisional antes de
lanzar el cliente**, fail-closed, y **completado una sola vez** en toda terminación. **D-8** las versiones se
comparan **por observación** (cliente contra servidor), nunca contra un número escrito en la config;
`binary_version` queda **informativo** y `migrate` deja de escribirlo. **D-9** el runtime es **explícito** en
cada despacho. **D-10** el modelo y la credencial **no viven** en `runtimes.json` (el modelo en
`delegation.json`, la credencial donde ADR-033 punto 6 la puso). **D-11** el `--exec-config` retirado se
rechaza por **token exacto, antes del parseo del verbo**, en todos los verbos.

**Deuda detectada (abierta).**
- **U6-2** (preexistente, transversal): **ningún productor de `observed_changes`** ⇒ el recibo sale siempre con
  `scope_validation: unknown` y el control mecánico «el rol con escritura no salió de su alcance» **nunca corre**;
  quedan los mapas de permiso del agente y la revisión del diff.
- **O-2**: con el coordinador **fuera de la raíz**, el runtime aplica la **copia global** de los agentes, cuyos
  mapas son relativos a otra carpeta ⇒ el camino nativo no puede escribir. **Límite declarado**, con su
  disparador (la vía nativa recomendada inicia el coordinador en la raíz; la escritura temporal queda cubierta
  por la vía externa, que fija `PWD` a la raíz). No invalida U3.
- **D-U65-4**: **sin write-ahead nativo** (por construcción: la sesión la crea la herramienta del runtime); la
  salida es **procedimental** (el siguiente coordinador ejecuta `record` con `--parent`/`--since`).
- **D-U65-5**: recuperar del store la salida del huérfano (que llegó a commitear) como **entrega tardía**.
- **O-2 de la review** (deuda aceptada): la derivación del `kind` tiene **dos implementaciones** (núcleo y
  módulo) y el módulo conserva un *fallback* del scribe ya innecesario.
- **O-3 de la re-review focal 2** (nit): el focal externo compara longitud, no identidad de bytes.
- **Transporte del paquete en la vía nativa**: la línea JSON de cabecera de `PACKET.md` mide **más de 2000
  caracteres** (2378 en el recorrido) y la herramienta de lectura del runtime **la trunca**; un orquestador que
  copie el paquete leyéndolo puede no lograr bytes idénticos. La ruta documentada (`cdad_packet.py render` con su
  stdout pasado sin cambios) despacha bien. Queda como observación para la guía del orquestador nativo.
- **Pendientes de cierre:** **suite completa** (PD-21, la corre quien cierra) y **redespliegue** de los
  review-fix (orden del owner). Heredadas y sin cambio: **DT-8** (F011 por deriva de la copia instalada) y el
  **flake conocido del margen de la espera bajo carga** (clase DT-9), reproducido verde en aislamiento.

**Lecciones de proceso.**
(1) **Una sonda que registra sólo nombres inventa las unidades**: V-7 registró nombres de columna y no tipos, los
fixtures supusieron segundos `REAL` y el momento **nunca fue evaluable contra el store real** — la degradación
salió con las mismas palabras que otro caso. Una sonda de store registra **tipo y unidad**.
(2) **La clasificación no es autorización**: un `allow` de raíces de implementación reabre tests convencionales
dentro de ellas (B-1); la **barrera del rol prevalece** sobre la clasificación de la política.
(3) **Un registro que sólo existe al final deja un callejón sin salida**: la vía externa lo escribía al
terminar, y una muerte del coordinador producía un paquete que parecía no haber sido despachado — con
`reconcile` autorizando repetir. El **write-ahead** con **compleción única** cierra el hueco sin abrir un
segundo escritor.
(4) **Las instrucciones son parte del contrato**: el texto generado pedía un FINAL TEXT que la entrada no
devuelve (B-3); el procedimiento referenciado tenía que distinguir **por estado de llegada** (texto pendiente /
descriptor ya escenificado / recibo ya durable) y **ambos caminos comprobarse** de punta a punta.
(5) **«El mismo escenario en las dos vías» no puede ser el mismo paquete**: el recibo durable admite **una sola
finalización por (ejecución, paquete)**; el recorrido se hace sobre **dos paquetes de la misma ejecución**.
(6) **Una credencial no viaja por `argv` ni por el entorno del orquestador**: la resuelve y la inyecta el módulo
en el entorno del proceso cliente; el rodeo de entorno que hacía el despachador deja de ser necesario.

**Estado del epic.** `epic-006-opencode-concurrency` sigue **abierto** (`features-loop`): **006-001, 006-002,
006-003 y 006-005 `done`, 4/6**. Quedan **006-006-spec-plan-review** (revisión independiente de spec y plan
antes del RED, enmienda 006) y **006-004-active-decisions-table** (enmienda 003, que también vehiculiza el
principio de general antes que específico, enmienda 005 ⇒ **ADR-034**), en el **orden que fijó el owner**:
**006-005 → 006-006 → 006-004**. **Siguiente:** `006-006-spec-plan-review`.

---

## 2026-10-18 — Feature: 006-003-installer-single-profile-delegation-config (epic 006)

**Cerrada el 2026-10-18 (ciclo técnico completo).** Tercera unidad de `epic-006-opencode-concurrency`. El instalador
y el generador quedan **sin perfiles y sin mapa de modelos**; la delegación externa toma el modelo de un **único
archivo de configuración**; el instalador **retira sus propios obsoletos**; y la credencial del servidor se carga
de un archivo con permisos verificados. **Contrato:** `spec.md` sha256 `c25ebf0e…` (PD-1..PD-8, INV-1..INV-7,
D1..D8; **§8 A-1..A-4** del orquestador y **§9 A-5** del dueño) y `plan.md` con **A-6**; aprobados el **2026-10-18**
por el orquestador Claude bajo la **HITL delegada del epic** (A-5 lo aprobó **Pablo**). **El epic NO se cierra.**

**Problema medido (no presupuestado).** Dos hechos: (i) el despliegue de 006-002 dejó en HOME las dos referencias
retiradas como `pending_removal` — el instalador **no borra** lo que dejó de desplegar y un orquestador puede seguir
leyéndolas (`docs/epics/epic-006-opencode-concurrency/execution.md` §«Despliegue y push tras 006-002»); (ii) el
principio del dueño (`plan.md` §9): **los modelos los fija la configuración, nunca el orquestador ni los scripts**.
Con eso, el mapa de perfiles de `scripts/cdad-models.sh` y la línea `model:` de los agentes dejan de tener sentido.

**Producto (U1 → U8 + dos rondas de review-fix).** Rango `2b43516..HEAD` (HEAD = `2798a9a`): **111 archivos,
+12653/−1771**, de los cuales **41 son producto, +1163/−860** — `install.sh` es el grueso, `scripts/cdad-models.sh`
**retirado** (−177), `scripts/cdad-generate.py`, `scripts/validate-subagents.sh`, `Makefile`, `sources/agents/adapters/*`,
`sources/roles/*`, `skills/cdad-cycle/SKILL.md`, `references/cli-delegation.md`, `scripts/cdad_delegate.py`,
`scripts/cdad_delegate_opencode.py`, `assets/opencode-exec-config.example.json` y los agentes regenerados;
`tests/` suma **37 archivos, +7338/−900**. **Último commit de producto: `738a380`** (todo lo posterior es docs/estado).

- **U1** — generador sin `--profile` ni mapa: `cdad-models.sh` retirado, `Makefile` sin `PROFILE`, manifiesto de
  staging sin la clave `profile`, `^model:` a **0** en los 21 agentes. RED `d5b2ae0` → GREEN `afcd14f`; **testfix**
  `bb674b4` (`P1.reviewer` de `validate-odoo-specialization.sh` pasa de exigir `model:` distinto a exigir su
  ausencia, declarado).
- **U2** — instalador sin perfiles: `--economical|--optimus|--premium` **rechazados** con diagnóstico que nombra
  la config de delegación; `--basic` y `CDAD_MODEL_PROFILE` **aceptados, deprecados y sin efecto** (A-1: nada
  silencioso, INV-7). RED `f2c3540` → GREEN `44f1561`.
- **U3** — textos instalables sin perfiles ni modelos concretos: §2 de `SKILL.md`, sección `delegation` de los
  adaptadores, agentes regenerados; oráculo de PD-7a vacío. RED `54c6ac6` → GREEN `2b1b597`.
- **U4** — `delegation.json` **versión 1** (por destino y rol) como **única fuente** del modelo de la delegación
  externa; la clave `model` de la exec-config se **ignora con un aviso de una línea** que nombra la ruta y cómo
  migrar; rol sin entrada → sin `--model` y `model_configured: null`; el instalador crea `delegation.json` +
  `opencode-server.env.example` (sin valor) y **no los registra como suyos** (A-3). RED `5b91387` → GREEN `df90b41`.
- **U5/U5'** — ver **A-5** abajo.
- **U6** — credencial del servidor: variables de entorno primero y si no el archivo (`credential_env_file` o el
  default); permisos sobre el **fd abierto** (`os.fstat`, acepta 600/400, rechaza bits 077); `401/403` con
  diagnóstico autosuficiente (variables, ruta resuelta, procedencia) y **nunca el valor**. RED `e2eba98` → GREEN `797b935`.
- **U7** — el instalador **retira sus obsoletos propios**: intacto por sha256 → retirado del disco **y** del
  manifiesto; modificado → preservado + CONFLICT + **sigue registrado**; no registrado → nunca se lee; `--dry-run`
  lista sin borrar; el python del manifiesto recibe `INSTALL_ROOT`. RED `3a04ad1`; **GREEN detenido** (`ef78451`,
  sin commit, árbol devuelto) porque **review-5 B3** fijaba lo contrario; **A-6** reformula B3 y deriva la cuenta
  del `Verify` del staging; **testfix** `12a859b` → GREEN `516149b`.
- **U8** — aceptación end-to-end en **raíz redirigida** (HOME falso, XDG propio): install → `--check` PASS →
  `make validate` sobre la instalación de aceptación → despacho `mode: server` con la config del instalador →
  reinstalación que retira el obsoleto; **HOME byte a byte intacto** (INV-6). Test `1bc7645` (797 líneas) + T4 de
  005-010 reformulada por D3/U4.

**A-5 (decisión del dueño, en mitad de camino): se retira la verificación de familia.** Mientras corría el GREEN de
U5, Pablo retiró el requisito: para la delegación **externa** el modelo se configura en `delegation.json`; para la
**interna**, en la config de cada agente según lo que el runtime permita; y **no** se exige al orquestador despachar
controlando familia ni modelo. Se retiran PD-4a..e, D4, §2.4, el script `cdad_model_family.py` (**no se construyó**) y
**INV-5 se reemplaza**; se conservan la observación I8 (`model_configured`/`model_reported`, que solo registra) y los
demás invariantes anti-sesgo (el test-writer no ve implementación, el implementer no edita tests, el reviewer es
read-only y de sesión separada). El GREEN `-005` quedó **abandonado sin cambios** y U5' lo reemplazó: RED `0629ae0`
(+ **testfix** `113c777`, un **falso positivo** del oráculo: «failure family» de `stage-4-review.md` no es requisito
de despacho) → GREEN `0230156`.

**Review (etapa 4, reviewer en sesión independiente) — 0 bloqueantes / 7 opcionales / 3 abstenciones**,
sobre `2b43516..401d951`. **Disposición:** una ronda de review-fix para los opcionales que contradicen la letra de la
spec o confunden el diagnóstico (**O-1** credencial de entorno vacía tratada como presente, **O-2** el lector de
`delegation.json` y de la credencial debía resolver la **misma base** que el instalador, **O-4** el 401 imprimía
«credential file None», **O-5** un registro con sha vacío no debía retirarse). **O-3** (precedencia de
`XDG_CONFIG_HOME` del host frente a la raíz redirigida) y **O-6** (XDG relativo) pasan a **deuda**; **O-7** se cierra
con la suite. RED `c57fc79` —que **declaró que O-5 no era reproducible** en vez de inventar una postcondición
sustituta— → GREEN `ef8d2f8`.

**Re-review focal 1 — 1 BLOQUEANTE.** **B-1: la afirmación del RED sobre O-5 era falsa.** El reviewer sondeó
black-box y mostró que un registro con sha `""` **sí se retira** en dos representaciones alcanzables: el TSV del
manifiesto leído con `IFS=$'\t' read` de bash **colapsa columnas vacías**, así que con sha y source vacíos el
registro da `removable`; con source presente la columna colapsada se rellena con el source y el registro queda
**permutado** («registered hand-edit»). El remedio fue **estructural**: veredicto `unverifiable` (sha vacío o `null`
**nunca** `removable`) y los registros del manifiesto viajan **NUL-framed** con `read -r -d ''`; los streams que
quedan en TSV los parsea **Python** (`split("\t", 2)`), que preserva campos vacíos. **OPT-1** (la rama de entorno del
401 ya no nombraba ninguna ruta candidata) se corrigió en la misma ronda. RED `26667b5` → GREEN `738a380`; la
afirmación de `rf-red.md` §4 quedó **refutada por escrito** con la disposición.

**Re-review focal 2 — 0 bloqueantes / 1 opcional / 3 abstenciones.** B-1 cerrado **5/5** puntos de su condición
(remedio estructural verificado por lectura + test + sonda propia: `--dry-run` con registro degenerado **no borra
nada**); OPT-1 cerrado. **OPT-2** (el comentario de symlinks de `install.sh` declara un veredicto que el orden real
del código —más conservador— ya no entrega con digest vacío) pasa a **deuda**: no cambia comportamiento, no pierde
datos y solo se alcanza con un manifiesto editado a mano.

**Suite de cierre (una vez, por quien cierra).** `pytest tests/` sobre `8638d06` → **1177 passed, 5 skipped,
0 failed** (**PD-8c cumplida**); la falla ambiental de la corrida previa (carrera de fixtures del adaptador bajo la
carga de la suite) **no se reprodujo**. `make validate` en este checkout: **168 PASS / 1 FAIL = F011**, la deriva de
la instalación de HOME (**DT-8**, preexistente); **redirigido a la instalación de aceptación de U8 → 169 PASS / 0 FAIL**.

**Decisiones relevantes.** **D-1** el instalador y el generador **no tienen perfiles**; `--basic`/`CDAD_MODEL_PROFILE`
sobreviven un ciclo como **alias deprecado sin efecto** (≥6 recetas de test los usan) y los flags de perfil se
**rechazan** nombrando el lugar donde ahora se elige el modelo. **D-3 (dueño)** `delegation.json` es la **única**
fuente del modelo externo, **sin fallback silencioso**, con aviso de deprecación para la clave heredada;
**trade-off declarado:** una exec-config existente cambia de modelo efectivo (pasa al default del destino) y el
registro lo declara. **D-5** la credencial se verifica sobre el **fd abierto** (patrón TOCTOU ya existente) y el
diagnóstico nombra variables/ruta/procedencia **nunca el valor**. **D-6 (dueño)** el retiro de obsoletos es **unidad
propia**, reutiliza la regla owned+sha256 de `--uninstall` (**una sola función compartida, sin duplicar**) y **no toca
lo no registrado**; **A-3** deja `delegation.json` y el `.example` **fuera del manifiesto** (son datos del usuario:
ni `--uninstall` ni el prune los borran nunca). **D-7** los tests acoplados se **reformulan declarando el reemplazo**
(A-1 del plan), nunca se borran en silencio. **A-5 (dueño)** quita la verificación de familia; **A-6 (orquestador,
HITL)** resuelve el choque B3↔PD-6a de forma **general** —no acota el retiro a «lo que no sea agente»— y hace que la
cuenta del `Verify` **salga del staging** por runtime, conservando su poder de detectar una instalación incompleta.

**Deuda detectada (abierta, con condición de cierre).** **O-3** — con raíz redirigida y `XDG_CONFIG_HOME` definida en
el host, los dos archivos de config se crean en el XDG real: **INV-6 al pie de la letra se rompe** en esa
configuración (la implementación sigue PD-2c fielmente y los tests evitan el caso redirigiendo XDG). **Decisión del
dueño** (que PD-2c gane por diseño, o que se ignore XDG con aviso cuando hay raíz redirigida) + test que la fije.
**O-6** — un `XDG_CONFIG_HOME` **relativo** (inválido por la spec XDG) resuelve rutas relativas al cwd de cada
proceso; validar absolutidad con diagnóstico (patrón ya usado para `CDAD_INSTALL_ROOT`). **OPT-2** — comentario de
symlinks de `install.sh` contra el orden real del código. **DT-8** — `__pycache__` en el staging (causa única del
F011): sigue **fuera de alcance** y el retiro de PD-6 **no promete** árbol «limpio». **Desconocidos conservados:**
si el runtime honra `agent.<name>.model` sobre el frontmatter de un agente custom (no verificable desde el repo;
CDAD no depende de ello) y la relación exacta de la contraseña con el runtime del dueño (afirmada por el plan, no
verificable en el repo). Y **evidencia para 006-005**: abandonar un paquete despachado **no lo libera** —
`disposition --resolution abandoned` registra la decisión pero el paquete queda `dispatched`; `prepare` rechaza todo
paquete nuevo, `--replace-packet` solo acepta lo nunca despachado y `reconcile` es de solo lectura: **ningún comando
lleva un paquete despachado a `failed`** (se cambió un campo a mano, con la disposición como autoridad, y
`validate-state` dio VALID).

**Lecciones de proceso (las cuatro medidas).** (1) **Un oráculo aprobado antes puede contradecir una decisión nueva y
el discovery no listarlo**: review-5 **B3** fijaba lo contrario de PD-6a y `discovery.md` §1.6/R1 solo había declarado
acoplado a **B4**; el implementer **se detuvo** en vez de acotar la regla a lo que dejara el test verde —lo que
habría sido gaming—. (2) **Un RED puede dar por cumplido un hallazgo con sondas incompletas**: el RED de O-5 reportó
«ya se cumple» con siete variantes y la re-review lo **refutó black-box** en dos representaciones alcanzables; la
lección operativa es que **un registro estructurado no se lee con `read` de bash cuando puede haber campos vacíos**.
(3) **Abandonar no libera**: el vocabulario cerrado de la disposición es `abandoned|superseded` y la enmienda 004 ya
le encargó a 006-005 el «intento interrumpido sin entrega» con camino mecánico. (4) **La carrera conocida de los
fixtures del adaptador bajo la carga de la suite volvió a aparecer** (una instancia de la clase DT-9: cota de 2 s;
el caso pasa en aislamiento): no es regresión de esta feature y hay que seguir teniéndola en cuenta.

**Estado del epic.** `epic-006-opencode-concurrency` sigue **abierto** (`features-loop`): **006-001, 006-002 y 006-003
`done`, 3/6**, y **en cola** —cada una con su enmienda al plan aprobada por el dueño— **006-005-native-path-parity**
(paridad del recorrido nativo: núcleo común, registro mecánico del intento, capacidades del encargo; enmienda 004) y
**006-004-active-decisions-table** (la sección «Decisiones vigentes», enmienda 003, que además vehiculiza el
principio de general antes que específico, enmienda 005). Y **006-006-spec-plan-review** (revisión independiente de spec y plan antes de RED, enmienda 006, aprobada por el dueño el 2026-10-18), ordenada **después** de 006-004; la spec y el plan de 006-005 los revisa el reviewer con el procedimiento actual. **El epic NO se cierra.** **Redespliegue en HOME ordenado por el dueño el 2026-10-18** (antes: `e4d17e3`, 006-002 con perfil `basic`); receta — `make staging && bash install.sh --force &&
bash install.sh --check` (el flag de perfil ya no hace falta; se acepta con aviso de deprecación); se esperan el
CONFLICT preservado del reviewer del dueño y DT-8. **ADR:** borrador **ADR-033** (reemplaza ADR-007 y la parte de
perfiles de ADR-008), **aprobado por el dueño**; numeración ajustada en `plan.md` §12: el ADR del principio de general antes que
específico pasa de `ADR-033` a **`ADR-034`**. **Siguiente:**
`006-005-native-path-parity`.

## 2026-10-18 — Feature: 006-002-delegation-by-layer (epic 006)

**Cerrada el 2026-10-18 (ciclo técnico completo).** Segunda unidad de `epic-006-opencode-concurrency`.
Corrige la **regla** que llevó al orquestador de un consumidor real a delegar **por el adaptador CLI
dentro de su propio runtime** —1.145 turnos, 6 compactaciones y ninguna sesión hija; todos sus
despachos por el adaptador con `--destination opencode`
(`docs/epics/epic-006-opencode-concurrency/execution.md` §«Hallazgo: por qué el orquestador del
consumidor despacha por bash»)—. El texto instalable tenía el **mismo mecanismo de runtime en cinco
lugares a la vez** mientras los agentes generados llevaban una regla neutral
(`docs/specs/006-002-delegation-by-layer/spec.md` §1). **Contrato:** `spec.md` (PD-1..PD-11,
INV-1..INV-8, D-1..D-7) y `plan.md` (con **A-1/A-2**), aprobados el **2026-10-17** por el orquestador
Claude bajo la **HITL delegada del epic**; **dos enmiendas del dueño** sobre `/tmp` (001 y 002)
agregadas al `spec.md`. **El epic NO se cierra:** quedan **006-003** y **006-004**.

**Principio de capas (del dueño, `plan.md` §8).** **skills** = la metodología, general y única;
**agentes** = el comportamiento por runtime; **scripts** = independientes del runtime y dependientes
del SO; **adaptadores** = sólo para orquestar agentes de **otro** runtime o de un runtime **sin**
delegación propia; en cualquier otro caso se delega con el mecanismo nativo. Y el principio de
`plan.md` §9: **los modelos los fija la configuración, nunca el orquestador ni los scripts**.

**Producto (U1 → U2 → U3 → U4 → U5 → U6, más dos arreglos).** Rango completo de la feature
`git diff f1292fb..HEAD` = **54 archivos, +6794/−328** (**72 commits**, 20 de ellos de producto/tests,
todos bajo `skills/`, `sources/`, `scripts/`, `agents/`, `tests/`, `docs/`). Producto: **16 archivos,
+255/−435** (la merma neta es el retiro de las dos referencias instalables).
- **U1** — sección `<!-- cdad-section:delegation -->` en `sources/agents/adapters/{opencode,claude-code}.md`
  (bloque único; `REQUIRED_ADAPTER_SECTIONS` suma `"delegation"` en `scripts/cdad-generate.py`), y el
  generador la compone en el orquestador y **elimina el bloque hardcodeado** del orden; los agentes se
  regeneran (`agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`). RED `a2db8f8`
  (**9 failed / 1 passed**, todos por aserción) → GREEN `51ab88d`.
- **U2** — §4 neutral y skill sin herramientas de runtime. RED `4e17dcc` → GREEN `8cf2d75`.
- **U3** — retiro de las dos referencias por runtime del árbol instalable y `cli-delegation.md` como
  **sólo contrato del adaptador**. RED `2665d55` → GREEN `5ad04e2`.
- **U4** — `SKILL.md` §2 sin modelos; **F001 reformulado, no borrado**. RED `3c828ad` → GREEN `8c05755`.
- **U5** — equivalencia de transporte en `references/re-entry.md` + enlaces. RED `1125c53` → GREEN `8d4b302`.
- **U6** — las cuatro reglas de contexto del orquestador (`sources/roles/orchestrator.md`; el 4º
  condicionado a las enmiendas). RED `edc58ae` → GREEN `900fa58` (focal 7; 337 passed / 2 skipped en
  los tests que leen orquestadores).
- **Arreglo de regresiones de U1** (`7d13a6d`, detectadas por módulos ajenos a la ficha): **A2** — toda
  invocación del CLI en la sección lleva la ruta derivada `<skill-dir>`; **P1** — el recibo **deja de
  restatar** los pasos y apunta al cableado del orquestador y a «Orchestrator materialization
  protocol» (así el párrafo compuesto vuelve a converger con la fuente). 80 passed + 191 passed / 2 skipped.
- **Testfix de U3** (`20bb835`, sólo `tests/`): el selector de evidencia devolvía **416** documentos de
  `docs/**`; ahora selecciona por **autodeclaración** → **2** copias preservadas. Las aserciones **no**
  cambiaron.
- **Enmiendas del dueño sobre `/tmp`.** **001** (`b9d9455` → `4c068ea`, relativizar la regla 4) quedó
  **reemplazada** por la **002** (`300a05c` → `a3b54e6`): el límite de `/tmp` era **de su servidor**, no
  de la metodología; la regla 4 queda como **rutas estables del workspace** (`.cdad/inbox` para el
  recibo) y **ningún texto instalable nombra `/tmp`** — ni para prohibirlo ni para admitirlo.

**Aceptación real U8 — despacho nativo medido (PD-4).** Worktree descartable con `.cdad` copiado; los
agentes de `make staging PROFILE=basic` puestos en **`.opencode/agents/` del proyecto** y la skill del
repo en `.opencode/skills/`; **HOME no se tocó**. Encargo de **una línea** («despachar el reviewer de
este paquete»). **Evidencia (session_v2 en sólo lectura):** sesión padre `succeeded`; **una** sesión
hija `cdad-reviewer` (familia **glm**) `succeeded`, **despachada por `task`**; **56 comandos bash,
ninguno** invoca el adaptador ni un `run` del CLI; el texto final se escenificó **tal cual** en
`.cdad/inbox` y `receive` cerró con recibo **`pending`**. El paquete pasó al repo principal
**byte-idéntico**, despacho registrado como intento `at-006-002-u8-001` y recibo emitido con los
mismos bytes (`execution.md` §«006-002 U8»). Es **evidencia de comportamiento, no prueba**.

**Lo medido y lo aprendido de U8 (tres observaciones, ninguna investigada a fondo).**
1. **Los agentes que `prepare` publica en `.opencode/agents/` del proyecto salen de la versión
   instalada en HOME, no del repo** (coincide con lo que declara
   `docs/runtime-adopted-version.md` §«Agentes de proyecto»). Para la corrida hubo que poner ahí los
   de `make staging PROFILE=basic`; OpenCode **prefiere los de proyecto sobre los globales del mismo
   nombre** (verificado con `opencode debug agents`). Consecuencia práctica: la aceptación del texto
   nuevo **no** se puede hacer contra HOME sin desplegar.
2. **Un `opencode.json` de proyecto con `agent.<name>.model` dejó la lista de agentes vacía**
   (observación registrada, **no investigada**). El modelo del reviewer se configuró entonces en el
   **frontmatter de su agente** en ese proyecto, que es lo que el registro del intento declara como
   `model_configured`.
3. **El orquestador de la corrida leyó código fuente del CLI** (`sed`/`grep` sobre los scripts) para
   resolver el uso de `begin` y del descriptor — **contra el espíritu de la regla 1** (orientarse con
   la vista compacta, sin volcados) — y **tomó las notas de orquestación de `execution.md` como
   mandato**, razonando que el epic prescribía la herramienta nativa de Claude Code. Las dos van a la
   review como **uso real**: una regla escrita **no** es una regla obedecida (es exactamente el límite
   honesto que declara PD-6), y **las notas dirigidas al orquestador del epic no son instrucciones
   para el orquestador de una corrida**.

**Review formal (etapa 4) — 1 bloqueante / 4 opcionales / 4 abstenciones** (`review.md`; diff
`f1292fb..8c4ead5`, 49 archivos +6130/−327; reviewer de familia **glm**, distinta a la del implementer,
familia **deepseek**). **B-1 (BLOQUEANTE):** `sub-agent-strategies.md:51` nombraba **alias de modelo de
runtime y el nombre del gateway de despliegue** en texto instalable — viola PD-1/INV-2 y **escapa al
oráculo declarado** (alias sin dígito y gateway fuera de `PROVIDER_RE`; el reviewer lo probó
mecánicamente). El árbol **se contradecía con su propia frase nueva** de §2. Opcionales a deuda:
**O-1** el título «Delegation (adapter)» se lee como si el adaptador fuera el sujeto; **O-2** sobrevive
en el cuerpo compuesto una línea del canal muerto del CLI; **O-3** la cita entre `orchestrator.md` y
`orientation.md` §1 quedó **invertida** respecto de lo declarado en el plan (un dueño por regla, sin
duplicación: PD-6 cumplido); **O-4** ruido cross-runtime/deployment en el cuerpo compartido de «Bash
policy».

**Review-fix y re-review (sólo B-1)** — RED `5c85d68` (**1 failed / 12 passed**; el oráculo
extendido, autocontrolado con 3 guards) → GREEN `a25fc20` (**1 archivo, 1 línea**;
`grep -RniE 'haiku|sonnet|opus|fable|<gateway>' skills/` → **0**). `rereview.md`: **B-1 CERRADO**
(reproducido mecánicamente contra el árbol viejo: **5 ofensores** en esa línea; U2/U4 intactos 13
passed; focal 006-002 **41 passed**), **0 bloqueantes**, **NF-1** nuevo (el token del gateway en el
oráculo es **de instancia, no de clase** → deuda de generalización, no defecto del cierre) y juicio
separado sobre `sub-agent-strategies.md:49-50` (frontmatter de permisos y hooks del otro runtime:
**enforcement**, no despacho ni modelo → deuda de capas, no bloqueo).

**Suite de cierre (una vez, por quien cierra).** `1119 passed, 5 skipped` (2026-10-18), **sin fallas**.
`make validate`: **161 PASS / 1 FAIL = F011** (`validate-subagents.sh`), **drift de la instalación de
HOME, preexistente y declarado (DT-8)**, reproducido por el reviewer. `make staging PROFILE=basic &&
make agents` **determinista** (segundo `make agents` → `git diff` vacío; `diff -r` staging↔`agents/` = 0)
y con **0 ocurrencias del prefijo de gateway** en los orquestadores bajo `basic`. **Frontera PD-8
limpia:** sin `install.sh`, sin `scripts/cdad-models.sh`, sin el adaptador `cdad_delegate*.py`, sin
`ADR-007*`, sin el handoff/config del consumidor.

**Decisiones relevantes.** **D-1** cada regla de delegación por runtime vive en **su agente
orquestador**, generado desde una sección nueva del **adaptador fuente**; la alternativa «referencia
por runtime dentro de la skill» se **descartó con evidencia** (`install.sh` copia el **mismo** árbol de
skill a las tres bases). **D-2** §4 conserva los siete puntos **sin nombrar runtime ni herramienta**.
**D-3** declaración en tres partes: (1) por perfil — con un perfil que **no** fija modelos la familia
distinta **no** está garantizada, y el orquestador **ni elige ni inventa** modelo (pasa uno **sólo** si
viene de la configuración del entorno); (2) registro
`runtime`/`model_configured`/`model_reported`/`session` con `null`/`unknown` lo no observado, y el gate
de review **declara** «invariante no garantizado» en vez de omitirlo; (3) salida legítima = handoff a
chat nuevo donde **el usuario** elige. El **script** de comparación de familias es **006-003**, no
esta feature. **D-4** equivalencia de transporte en `re-entry.md`, enlazada desde §4 y desde cada
sección `delegation`. **D-5** las 4 reglas de contexto en la fuente del orquestador, con
`orientation.md` §1 como dueño de «vista primero». **D-6** la columna de familias y el párrafo de
perfiles salen de `SKILL.md` §2; **F001 reformulado**; `install.sh`, `scripts/cdad-models.sh` y
**ADR-007 no se tocan** (son de 006-003). **D-7** el consumidor queda **fuera de alcance**: su handoff
**todavía prescribe el adaptador** y lo actualiza **su dueño**.

**Deuda detectada (abierta, con condición).** **O-1..O-4** de la review (título de la sección; línea
del canal muerto del CLI en el cuerpo compuesto; dirección de la cita con `orientation.md` §1; ruido
cross-runtime en el cuerpo compartido de «Bash policy»). **NF-1**: el oráculo del gateway es **de
instancia** (fija el literal) — migrarlo a una lista configurada o documentar la frontera.
**`sub-agent-strategies.md:49-50`**: sintaxis de frontmatter de permisos y hooks del otro runtime en la
skill — aceptable como referencia por el criterio vigente, pero **idealmente va a la capa agente**.
**Despacho erróneo detenido** (2026-10-17): al despachar un RED, `prepare` falló y el helper local
lanzó igual el paquete anterior; el orquestador lo detuvo a los 5 s **sin cambios en el árbol ni
commits**, y queda **un registro de despacho sin recibo** (intento `at-006-002-u6b-red-001`); el helper
`prep-dispatch.sh` **aborta si `prepare` falla**. **DT-8** (`__pycache__` en el staging del instalador;
es también la causa única del `install.sh --check` FAIL). Y **el consumidor todavía prescribe el
adaptador en su handoff** (fuera de alcance, D-7; lo actualiza su dueño).

**Lecciones de proceso.** (1) **El oráculo declarado puede tener un agujero y la review lo encontró**:
B-1 vivía en la superficie que U2 **ya había declarado** cubierta, y sólo salió al probar el oráculo
contra la clase (alias + gateway), no contra el caso. (2) **Test y texto no comparten commit**: por eso
A-1 **disolvió U7** — cada unidad reformula en su RED las aserciones acopladas de su superficie y su
GREEN mueve el texto sin tocar `tests/`. (3) **Una regla escrita no es una regla obedecida**: la
corrida real **midió** el despacho nativo (56 comandos, 0 adaptador) y a la vez mostró al orquestador
**leyendo el código del CLI** y tomando **notas de orquestación como mandato**. (4) **`prepare`
publica agentes de HOME, no del repo**: para aceptar texto nuevo hay que **desplegar** o aislar a mano.

**Estado del epic.** `epic-006-opencode-concurrency` sigue **abierto** (`features-loop`): **006-001 y
006-002 `done`** (**2/4**), y **en cola** —cada una con su enmienda al plan aprobada por el dueño el
2026-10-17— **006-003-installer-single-profile-delegation-config** (instalador **siempre `basic`**, sin
mapa de modelos —**reemplaza ADR-007**—, plantilla de config de delegación y credencial del servidor, y
el invariante del reviewer de otra familia como **verificación de configuración**) y
**006-004-active-decisions-table** (la sección «Decisiones vigentes» del Memory Bank). **El epic NO se
cierra.** **Redespliegue en HOME pendiente de la orden del dueño:** lo instalado es `6978709` (006-001 completo, redesplegado el 2026-10-17) y **no** incluye 006-002; receta
`make staging PROFILE=basic && bash install.sh --force --basic && bash install.sh --check`.
**Siguiente:** `006-003-installer-single-profile-delegation-config`.

---

## 2026-10-17 — Feature: 006-001-opencode-concurrency-reliability (epic 006)

**Cerrada el 2026-10-17 (ciclo técnico completo).** Primera unidad de `epic-006-opencode-concurrency`, nacida
de un problema **medido**, no presupuestado: **dos despachos reales del implementer terminaron `failed` por
contención en la base de sesiones compartida** (`LockTimeoutError` / `database is locked`, ≈89 s y ≈487 s, el
segundo con fallo al persistir un evento del LLM) (`docs/epics/epic-006-opencode-concurrency/plan.md` §2).
Cierra la **fila 1** del plan del epic (`:22`): **selección de ejecución explícita y verificable** —`server`,
`service` y `standalone`—, **procedencia por intento**, **espera proporcional** y **recuperación que conserva
la correlación**. Contrato **spec v2** (PD-1..PD-14, sha256 `dac418b9…`) y **plan v2** (sha256 `2726744…`),
**aprobados juntos el 2026-10-16** por el orquestador Claude bajo la **HITL delegada del epic**
(`docs/epics/epic-006-opencode-concurrency/execution.md`). **PD-6 queda en BLOQUEO declarado** y **AC-7
pendiente del dueño**; **el epic NO se cierra**. Decisión propuesta para registro en **ADR-031** (borrador del
cierre).

**Enmienda 001 — modo `service` (aprobada por el dueño el 2026-10-16).** Cambio de alcance
(`execution.md` §«Cambio de alcance aprobado por el dueño — 2026-10-16»): el **servicio de fondo** es dueño
del store, así que CDAD gana un modo `service` **configurado** que pasa a ser el camino normal —
`opencode service status` se comprueba antes de despachar y **CDAD nunca gestiona el servicio** (no lo
arranca, no lo reinicia, no lo detiene, no lo configura). La enmienda **reescribe INV-2** («nunca el modo por
defecto» → «nunca arrancar ni gestionar el servicio»), suma **INV-10** (con el servicio vivo ningún camino
abre un `standalone` ni re-despacha solo) y agrega **PD-13/PD-14**, conservando PD-1..PD-12 con un diff
conceptual por PD (§14) y sumando la unidad **T1b**. El orquestador **ratificó D-11 (A)** —un lector que
proyecta **solo** la clave `version` del registro del servicio, **sin red, sin contraseña y sin URL**, que
falla cerrado— y **confirmó D-9** (con `mode` sin declarar rige la **compatibilidad v1**).

**Producto (T1 → T1b → T2 → T3 → review-fix).** Adaptador
`skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (**+1333/−124**; 2138 líneas finales), referencia
`skills/cdad-cycle/references/cli-delegation.md` (+170/−19) y
`skills/cdad-cycle/assets/opencode-exec-config.example.json` (**nuevo**). El rango completo de la feature
(`git diff f537aa5..HEAD -- skills/ tests/`) son **11 archivos, +7563/−153**.

- **T1 — selección de modo, preflight del servidor, procedencia y secretos.** RED `91f7e98` (**14 failed /
  4 passed**, 18 tests; los 4 verdes **declarados**, no ocultos) → GREEN `4bc8934` + `a96c2d8` (**focal 18
  passed**; regresiones 36 passed). Únicos oráculos ajustados, autorizados por el plan §3: el de modo servidor
  de `test_005_010_t2_load_mode_invocation.py` (fixture `/api/info` en loopback con la versión del fake) y el
  `--version` del fake compartido de `test_005_009_t2_opencode_adapter.py`.
- **T1b — modo servicio.** RED `7ccedb4` (**16 failed / 0 passed**, todas por aserción de contrato, cero
  import/syntax/fixture) → GREEN `b949849` (**focal 16 passed**; regresiones 54 passed). `service status` se
  invoca **exactamente una vez** y es la **única** invocación de `service`; interpretación cerrada: URL
  `http(s)` con host y sin userinfo → **corre**; literal `stopped` → **no corre**; cualquier otra respuesta →
  **`blocked`**, **nunca** standalone.
- **T2 — espera, clasificación, correlación, terminación ordenada e intento previo.** RED `8447443` (**8
  failed / 4 passed**, las 8 por aserción) → GREEN `ddba831` (**focal 12 passed**; tres corridas combinadas de
  regresiones **93 passed / 1 skipped**). El RED **no cambió** con la enmienda. *(Incidente de tramo: el
  intento 1 del GREEN se cortó a los 90 min sin commit; el reconcile no encontró efectos.)*
- **T3 — concurrencia con fixture, referencia y config de ejemplo.** RED `5e5828a` (el focal **ya pasaba** por
  el GREEN previo de T1/T1b/T2: el oráculo se probó **por mutación** del fake propio —correlación rota →
  `'unknown' != 'completed'`— y se revirtió) → GREEN `d0a7963` (**focal 2 passed**; regresiones 53 passed /
  1 skipped; `make validate` **155 PASS / 1 FAIL**, el **F011 preexistente** de drift contra las copias
  instaladas). El adaptador **no necesitó cambios**: T3 entrega la referencia y el asset.
- **Review-fix (B1, B2, B3, O1).** RED `17a7ca1` (**2 failed / 2 passed**; B1 y B2 rojos por aserción, B3
  declarado como **cobertura**, no como falso verde) → GREEN `161c9ff` (**+79/−14** en los dos archivos de
  producto, `tests/` intacto; focal 4 passed; consolidado 81 passed / 1 skipped). **B1** acota el piso del
  cliente (`CLIENT_MIN_BUDGET_SHARE` con `COMPLETION_MARGIN_SECONDS = 0.8`) para que
  `E + cota_cliente + gracia + margen ≤ cota de la interfaz` valga **siempre**: el piso solo puede gastar el
  *slack* de la reserva y **PD-11 manda** (con la gracia de los defaults el tope da 0 extra; declarado).
  **B2** vuelve **innegociable** el intento previo: un store **existente** cuyo estado no se puede afirmar
  (ocupado/ilegible) → `blocked` **antes** de cualquier invocación, con la **nuance declarada** de que un store
  **inexistente** es un hecho determinante distinto y **no** bloquea (§2.7). **O1** saca `logs_dir` del asset
  (PD-12 literal).

**Review formal (etapa 4) — 3 bloqueantes / 5 opcionales / 3 abstenciones** (`review.md`; reviewer en OpenCode
de familia **glm**, **distinta** a la del implementer, familia **deepseek**). Los tres bloqueantes se
**aceptaron** y abrieron el review-fix: **B1** (banda de cota media: con el piso del cliente **sin tope** y un
preflight lento, el adaptador podía responder **después** de la cota de la interfaz —envelope
`did not answer within` y `session: null`, perdiendo además la correlación de PD-8—), **B2** (el chequeo del
intento previo **fallaba abierto** con el store ocupado o ilegible: podía despachar un **segundo worker vivo
del mismo paquete**, exactamente el doble-escritor que INV-10 prohíbe) y **B3** (sin focal de la cláusula de la
enmienda «fila no idle en modo **servicio** → `timeout`», ni del preflight de servicio acotado por el
presupuesto restante). Opcionales: **O1** entró en el GREEN; **O2** se corrigió (la etiqueta duplicada del flake
es **DT-9**, no DT-7); **O3** (anonimización: nombre de modelo/proveedor en la **spec aprobada** y nombre del
**otro proyecto activo** en la evidencia del epic), **O4** (celda indefinida de la matriz §2.2: `mode` sin
declarar + `server` presente pero **inválida**, que el código resuelve fail-closed **sin base textual**) y
**O5** (legibilidad: `delegate()` de ~450 líneas, docstring ambiguo de la terminación del grupo propio, fixtures
importados entre focales) **van a deuda**.

**Re-review (sólo bloqueantes) — 5 de 5 cerrados, 0 bloqueantes, 1 opcional nuevo, 4 abstenciones**
(`rereview.md`): **B1, B2, B3a, B3b y O1 cerrados**, con la mecánica verificada en el código por el reviewer
(el guard de B2 queda **después** del bloqueo por fila no-idle y **antes** de cualquier preflight; la rama de
B3a pincha `_settle_decides` —un refactor a `== "server"` la dejaría en rojo—; el clamped
`min(configured, remaining)` existe también para el preflight de servicio). **Opcional nuevo (O5-RF):** el
focal de B3b **no discrimina** el tope *por presupuesto restante* del preflight de servicio frente al valor
**configurado** (espejo del focal de servidor aceptado) → **a deuda**.

**Suite de cierre (una vez, por quien cierra).** `python3 -m pytest tests -q -p no:cacheprovider` →
**1 failed / 1079 passed / 5 skipped** (22:52). La falla es
`test_b3a_service_mode_row_not_idle_times_out_at_cota_ignoring_settle` con la **carga de la suite**; aislado
**5 de 5 verdes** a ≈2,08 s contra la cota de 2 s del fixture ⇒ **instancia de DT-9** (margen de los fixtures
de 2 s bajo carga), con la nota de que ese caso tiene **poco margen** y la próxima feature que toque el
adaptador lo tiene que tener en cuenta. Corrida anterior sobre `c9adace`: **1074 passed / 2 failed / 5
skipped**, ambos fallos **ambientales** (uno por DT-9; el otro porque exigía un staging con el perfil por
defecto y el orquestador lo había regenerado con `basic` para desplegar). El **commit de la corrida de cierre
no queda citado** en la evidencia del epic; el **último commit de producto es `161c9ff`** y todo lo posterior
es **sólo docs** (verificado: `git log 161c9ff..HEAD -- skills/ tests/` **sin salida**). `make validate`
**no** se re-corrió después del review-fix (último resultado: 155 PASS / 1 FAIL F011 preexistente, en el GREEN
de T3) ⇒ queda como **no verificado post-fix**.

**Recorridos reales (PD-6) — 2 de 3 piernas no se pueden cerrar.** Contra el **servicio vivo** (2.0.22) y con
el cliente 2.0.27, el despacho real terminó **`blocked` en 1,3 s** por el **gate de versión de D-11**, **sin
fallback** y **sin consumir tokens**: buena evidencia del invariante funcionando en la topología real (INV-10)
y, a la vez, prueba de que esa pierna **no se completa** así. Después el dueño **detuvo el servicio**, y los
recorridos con el servicio detenido dieron exactamente lo declarado: `mode: service` con `require: false` →
**`completed` en 33,9 s** con **fallback declarado** `service` → `standalone` (fila durable con
`agent cdad-test-writer`, `idle_outcome succeeded`, `version 2.0.27`, un solo servidor privado durante el
despacho), y `require: true` → **`blocked` en 1,1 s**, sin despacho. **La concurrencia real en `mode: server`
contra el servidor único del otro proyecto activo sigue pendiente de una credencial que el orquestador no
tiene** (sin contraseña el servidor responde 401) ⇒ **PD-6 = BLOQUEO declarado**. El único `completed` real
fue en **modo efectivo standalone** y **no** prueba la topología con servicio.

**Despliegue en HOME (2026-10-17, orden del dueño).** Se instaló con **perfil `basic`**. El primer intento usó
el **staging por defecto** —error del orquestador: `--basic` de `install.sh` solo deja la marca y no cambia el
staging— y se rehízo; **receta declarada:** `make staging PROFILE=basic && bash install.sh --force --basic &&
bash install.sh --check`. `install.sh --check` **PASS** (391 grupos) y **ningún agente instalado declara
`model:`**. `install.sh` termina **rc=1 por dos razones ajenas a la feature**: un **CONFLICT preservado** en
`~/.config/opencode/agents/cdad-reviewer.md` (contenido del dueño editado el 2026-10-15; el instalador **no**
lo sobrescribe, que es lo correcto) y el **bytecode `__pycache__`** que el staging copiaba del árbol de la
skill. **El despliegue es anterior al review-fix** (`git log b6c2193..HEAD -- skills/ tests/` = `17a7ca1`,
`161c9ff`) ⇒ **lo instalado no incluye B1/B2** y el **redespliegue queda pendiente de la orden del dueño**.
Rollback: restaurar el respaldo previo o reinstalar desde `29a4805`. **Observación declarada:**
`docs/runtime-adopted-version.md` **sigue declarando `29a4805`** (no se actualizó en esta feature): lo que
prueba el despliegue es la evidencia del epic, no ese registro.

**Decisiones relevantes.** **D-9** `mode` sin declarar **conserva la compatibilidad v1**: un cambio de
topología hacia un servidor **compartido** es decisión del consumidor y debe ser explícita; **costo
declarado:** las configs que hoy omiten `server`/`mode` siguen abriendo un servidor privado por despacho hasta
que declaren `mode: "service"` (**acción de la recepción, AC-7**). **D-10** el fallback `service` →
`standalone` es **declarado y contable** (`fallback=service-unavailable` en la procedencia) y existe **solo**
si `service status` informa `stopped`; la variante estricta es `service.require: true` → `blocked`. **D-11 (A)**
la versión del servicio se observa proyectando **una sola clave** del registro: sin red, sin contraseña, sin
URL y **fallando cerrado**; **trade-off declarado:** CDAD abre un archivo que **también contiene la
contraseña** (mitigado por la proyección; **DT-6**: ruta y esquema **no** son contrato público). **D-13** la
**ventana de carrera** (el servicio se cae entre la comprobación y el despacho y el cliente lo arranca) **no
tiene forma soportada de impedirse** en el runtime (no hay flag, variable de entorno ni setting que lo
controle): se declara **riesgo residual**, con la mitigación de comprobar lo más tarde posible. **Procedencia
sin tocar el esquema I8:** modos, causa del fallback y modo de despacho van como pares `clave=valor` **al
final** del texto libre de `provenance.runtime`, así el fallback es **auditable por intento** sin romper el
parseo existente. **La contención NO se elimina:** la feature **no** promete eliminar el bloqueo del store
compartido (siguen N≥3 escritores de larga vida y un `busy_timeout` fijo en el runtime); un único éxito real es
**observación**, no prueba.

**Deuda detectada (abierta, con condición de cierre).** **PD-6 (BLOQUEO declarado):** concurrencia real en
`mode: server` contra el servidor único ⇒ requiere **credencial del dueño**; y un servicio en la versión del
cliente ⇒ **decisión del dueño**. **AC-7 (pendiente del dueño):** recepción real sobre una unidad del
consumidor, **declarar `mode: "service"` en sus configs** y observar la convivencia; un éxito **no** prueba la
eliminación de la contención. **DT-8** `__pycache__` en el staging del instalador (bytecode marcado
*pending-removal*; excluirlo del staging). **DT-9** cotas de **2 s** de los fixtures: margen insuficiente bajo
carga del host; el caso de B3a tiene **poco margen** y hay que tenerlo en cuenta al tocar el adaptador.
**DT-6** (registro del servicio como hecho observado, no contrato), **DT-7** (el fallback como camino
habitual: se vigila con el contador de la procedencia) y **DT-3** (el intento previo solo ve los registros del
mismo paquete en el ledger) quedan abiertos en la spec §8, junto con DT-1/DT-2/DT-4/DT-5. **Deuda del CLI
detectada dos veces en esta feature:** `receive` **finaliza el recibo con un `kind` que la tabla cerrada de
tipos de artefacto rechaza** (`skills/cdad-cycle/assets/artifact-policy.json`, la que aplica `materialize`);
como el recibo es **inmutable**, el orquestador copió los bytes recibidos a `review.md` (sha `6f7cd682…`,
idéntico al recibo) y a `rereview.md` — debería validar el tipo contra la tabla **antes** de finalizar. Y **no
hay vía CLI para *fallar* un paquete despachado**: el vocabulario cerrado de la disposición es
`abandoned|superseded`, así que los **dos intentos** del GREEN que murieron por la **caída del proveedor**
(`chain exhausted`, sin efectos, reconcile limpio) no tuvieron marcador propio y el reintento fue el **intento
3 del mismo paquete**. Opcionales de la review a deuda: **O3** (anonimización), **O4** (celda indefinida de
§2.2) y **O5** (legibilidad de `delegate()`, docstring y aislamiento de fixtures), más el **opcional nuevo de
la re-review (O5-RF)**.

**Lecciones de proceso.** (1) **La review adversarial encontró lo que el GREEN no:** B2 era un
**fail-open** en el corazón de la invariante central (la recuperación podía reconstruir el problema) y B1 una
**banda aritmética** que ningún focal tocaba; ambos se cerraron con **RED primero** y la re-review verificó la
mecánica **en el código**, no en el informe del implementer. (2) **Declarar en vez de fabricar un rojo:** el RED
de T3 declaró que su focal **ya pasaba** y probó la sensibilidad del oráculo **por mutación**; el review-fix
declaró B3 como **cobertura**. (3) **El despliegue puede quedar por detrás de la corrección:** lo instalado es
anterior al review-fix; la receta `make staging PROFILE=basic` (y no `--basic` sin staging) queda como la forma
correcta de desplegar.

**Estado del epic.** `epic-006-opencode-concurrency` sigue **abierto** (`features-loop`): **006-001 `done`** y
tres features **en cola**, cada una con su enmienda al plan aprobada por el dueño el **2026-10-17**:
**006-002-delegation-by-layer** (la delegación por capas —`skills` metodología, `agentes` comportamiento por
runtime, `scripts` dependientes del SO—, con el principio de que **los modelos los fija la configuración y
nunca el orquestador ni los scripts**), **006-003-installer-single-profile-delegation-config** (instalador
**siempre `basic`**, sin mapa de modelos —reemplaza **ADR-007**—, más la config de delegación y la invariante
del reviewer de otra familia como **verificación de configuración**) y **006-004-active-decisions-table** (la
sección «Decisiones vigentes» del Memory Bank, que el orquestador mantiene y el reviewer revisa). **El epic NO
se cierra.** **Siguiente:** `006-002-delegation-by-layer`, que se abre al cerrar 006-001; y el **redespliegue
post-fix** de 006-001 en HOME, pendiente de la orden del dueño.

---

## 2026-10-14 — Cierre del epic: epic-005-real-operation

**Epic cerrado el 2026-10-14** con **14/14 unidades en `done`**, cada una con su cierre y su evidencia
(`docs/epics/epic-005-real-operation/closure.md` §Features entregadas). Atacó un problema medido, no
presupuesto: poner en uso real la versión instalada, hacer que un proyecto arranque con una instrucción
breve, medir el contexto por rol y recortar la orientación del orquestador **con datos medidos**
(`plan.md` §Resultado buscado). La **HITL delegada al orquestador OpenCode** (`execution.md` §Mandato y
aprobación) **vence al cerrar el epic y no se hereda** (`execution.md`:14-15).

**Versión de referencia.** Producto del repo al cierre: **`d3b9ccd`** (rama `codex/epic-005-real-operation`).
Instalación de HOME: **`29a4805`** (`install.sh --check` PASS, desplegada por el dueño el 2026-10-14).
`git diff --name-only 29a4805..d3b9ccd` = **solo** `docs/epics/epic-005-real-operation/execution.md` →
**cero diferencias de producto**. Último commit que toca producto: **`a4028af`** (005-014 T1 GREEN),
precedido por **`6fd515d`** (005-012, commit final revisado). La instalación nueva **está disponible pero
el servidor de OpenCode no se reinició**; los derivados de este repo todavía declaran la versión anterior
y el `status` lo da como **DRIFT en la pierna del proyecto** (`docs/runtime-adopted-version.md` §Versión
vigente; `execution.md` §Pendientes para el cierre).

**El cierre NO implica publicar.** El saneamiento de contenido está hecho (`a367b8c`, `29a4805`) y la
decisión del dueño es publicar con **historial nuevo**; el historial privado se conserva para la
trazabilidad de la evidencia (`execution.md`:74-79). A3 queda solo con falsos positivos del patrón local
no acotado, y **lo acota el dueño**.

**Criterios del epic** (`plan.md` §Criterios de aceptación del epic): 1 ✅ · 2 ✅ en la parte
verificable, con límites declarados (RD-a; D6 de 005-002; MIX-V6V7 de 003-007) · 3 ✅ como las secciones
citadas (005-003 §9 «antes»; 005-007 §7 y 005-011 AC-6/AC-7 «después»), **sin documento consolidado
aparte** · 4 ✅ (suite de cierre corrida por el orquestador en un worktree fijado al commit de cierre) ·
5 **❌ no ejecutado** (aceptación conjunta del consumidor, depende del dueño del consumidor).

**Estado:** las 14 unidades en `done` y **ninguna en cola**; el proyecto queda **en reposo**. Detalle,
deuda priorizada y prioridades de la planificación siguiente: `docs/epics/epic-005-real-operation/closure.md`.

**Reconciliación de notas vencidas (breve, sin reescribir la historia).** Las entradas de 005-003,
005-006, 005-007, 005-012 y 005-013 declaran bloqueos del tipo «requiere desplegar la versión nueva»: el
**despliegue ocurrió el 2026-10-14** (`29a4805`, `install.sh --check` PASS), así que esa condición dejó de
ser el bloqueo. Las corridas de aceptación que dependían de él (005-003 A1/A2/A6 y la observación de
A8/A9; 005-007 D-1; la R2 real de 005-006) **no se repitieron en este cierre** y siguen pendientes del
dueño: se registran aquí como pendientes, **no** como verdes. Lo único corrido con la instalación nueva
está en `execution.md` §Pendientes para el cierre (repetir el cierre de 005-014 sobre este repo: no-op,
rc=0, state intacto). La **observación de redacción de PD-1** (contradicción PD-1 vs PD-2/INV-5, anotada
en el cierre de 005-007 «para el cierre del epic») **no** se incorporó al cierre del epic: sigue como
deuda de redacción, sin unidad.

## 2026-10-14 — Feature: 005-014-closure-replay (epic 005)

**Cerrada el 2026-10-14 (ciclo técnico completo).** Decimocuarta unidad de epic-005 y **unidad correctiva
pequeña** pedida por el dueño sobre un defecto del **uso previsto de 005-012**. Cierra la **fila 14** del plan
del epic (`docs/epics/epic-005-real-operation/plan.md:47`; alta de la fila el 2026-10-14, `:144-157`):
**repetir un cierre ya aplicado no falla ni sugiere abrir la unidad**. Dependencia declarada
`005-012-transition-registration`, verificada `done`. Decisión propuesta para registro en **ADR-030** (borrador
del cierre).

**El defecto medido.** Con la feature cerrada, el efecto de `closure` deja `active_feature: null`
(`skills/cdad-cycle/scripts/cdad_packet.py:5460-5462`) y el **guard de feature nula** (`:5062-5065`, mensaje
que sugiere `open the unit first (open-unit)`) corre **antes** de la búsqueda idempotente por `transition_key`
(PD-11, `:5310-5324`): un orquestador interrumpido justo después del cierre no podía reanudar con la misma
orden y recibía un error que sugería abrir la unidad. La vía análoga ya declarada —`late-delivery` resuelve la
feature por `--feature` cuando no hay activa (`:5061`)— fija la forma del arreglo. El discovery lo confirmó con
el mapeo de superficie, el orden de chequeos por clase y los límites (`discovery.md`, 17729 B, sha256
`7eb84a26…`); el **gate 1→2** se validó con verificación propia de las cinco afirmaciones portantes (orden
guard/no-op; `args.feature` leído una sola vez; `CLOSED_FEATURE_STATUSES` `:114` usado en `:5142`/`:5161` y
nunca en `closure`; identidad con `execution_id` `:4721`; acotamiento a `closure`).

**Apertura.** `open-unit` sobre el reposo legítimo posterior al cierre de 005-012 (única unidad en cola del
plan); el despacho del architect reusó la ejecución que creó `open-unit` (sin `--new-execution`), con
`validate-state`/`validate-request`/`validate-packet` rc=0 y checkpoint de continuidad previo.

**Contrato y enmienda 001.** Spec **corta y sin plan aparte** (forma liviana decidida por el dueño). v1
aprobada por el orquestador OpenCode bajo la HITL delegada del epic-005 (`spec.md`, 20517 B, sha256
`655a85bc…`). **Enmienda 001 (v2, 31159 B, sha256 `5c23caa2…`)**, materializada por CAS sobre la v1 y
**re-aprobada** (el pin v1 dejó de nombrar los bytes actuales; sin `--supersedes`, por el predicado que fijó
B3 de 005-012). **Motivo:** el **RED de T1 expuso una contradicción interna del v1** en el escenario central
del dueño —PD-22 resolvía la feature de `closure` sin la ejecución ligada, así que la orden repetida
**verbatim** no resolvía ninguna feature y el no-op de PD-23 era **inalcanzable**. La enmienda toca **tres
puntos**: PD-22 con **tres fuentes** de resolución (`--feature` → `active_feature` →
`state.execution.feature_id`), **PD-27 nueva** (sin feature activa la operación **nunca aplica** un cierre) y
PD-24 comparando contra la feature **resuelta**; agrega E-6. El resto se conserva en sustancia (PD-23/PD-25/
PD-26, INV-10..INV-13, AC-1..AC-4, E-1..E-5, anonimización).

**Producto (T1: RED → GREEN; T2: gate de aceptación).**

- **RED — focal `tests/test_005_014_closure_replay.py` (nuevo, +446, 0 borrados; ningún test existente
  tocado).** Commit `8a969d3`; `4 failed in 4.08s`, **4 rojos por aserción** (0 por import/colección):
  PD-23/PD-25/PD-22 mueren en el guard de feature nula (el mensaje que sugiere `open-unit`, el defecto medido)
  y PD-24 cierra la feature **equivocada** con rc=0 (`--feature` ignorado en silencio). No-regresión declarada
  y verificada: los focales de 005-012 que tocan la operación, **47 passed**. El test-writer **declaró** en su
  informe la señal de contrato (los casos PD-23/PD-25 repiten la orden **sin** `--feature` como los escribía la
  v1, mientras PD-22 exige nombrar la feature) en vez de ocultarla.
- **GREEN — `cdad_packet.py` (+134/−13; cinco hunks: `_resolve_closure_feature`, `_transition_noop_message` y
  la rama `closure`).** Commit `a4028af`; **focal 4 passed** (4.30 s), **los cuatro módulos de 005-012 47
  passed** (79.19 s), `git diff a4028af~1..a4028af -- tests/` **vacío**, `validate-state` rc=0. La identidad
  (PD-10), el efecto del cierre (PD-9) y el camino de la primera aplicación (PD-26) quedan intactos.
- **T2 — aceptación con el CLI real sobre proyecto descartable** (`acceptance.md`; arnés fuera de git
  `.cdad/local/005-014-replay-acceptance.py`; crudo `.cdad/local/runs/005-014-acceptance.json`; HOME del
  subproceso en tempdir vacío; nunca este repo ni HOME). Ciclo representativo registrado **sólo con la
  operación** (`open-unit` → `gate specification` → `prepare`/`record-dispatch`/`receive` → `closure`), sin
  edición manual del state. **AC-1/AC-3:** la «interrupción» (repetir la **misma** orden) → **rc=0**, no-op
  que lo dice y **nombra** la entrada, state **byte a byte igual**, **1** entrada de cierre, `validate-state`
  rc=0 (`VALID: idle`). **AC-2:** repetición con otro payload (otro `--stage`) → **rc=2**, marcador
  `state incoherent`, **nombra** la feature y su estado `done`, **sin** `open-unit`, state byte a byte igual,
  sin re-cierre.

**Review formal (etapa 4) — 0 bloqueantes / 4 opcionales / 3 abstenciones** (`review.md`, sha256 `f61c2900…`;
reviewer `mofgw/glm-5.3-flash`, **familia distinta** a la del implementer `mofgw/deepseek-v4.1-flash`; diff
`a4028af~1..a4028af` de un archivo, `tests/` vacío, sha del contrato recalculado = pin del paquete). El
reviewer reprodujo por su cuenta el focal (4), los cuatro módulos PD-26 (47) y el arnés de aceptación
(AC-1..AC-3), cubrió PD-22..PD-27 e INV-10..INV-13 con procedencia `archivo:línea` y corrió **cinco sondas
adversariales propias** (rama «ninguna de las tres» de PD-22; replay sin `--closure-path`; `--feature ''`;
documento de cierre borrado; `--artifact` inexistente), todas **fail-closed** con el state idéntico. **Los 4
opcionales son Nit/FYI sin impacto material y van a deuda por el criterio vigente 2026-10-12:** O-1 (la rama
cerrada no exige `--closure-path`: la omisión cae en PD-25/PD-27(c) en vez del mensaje de PD-9; ambos rc=2
fail-closed), O-2 (`--feature ''` se trata como ausente, consistente con la convención preexistente), O-3 (el
límite declarado de PD-23 se extiende a los `--artifact` citados) y O-4 (el mensaje de PD-25 no nombra el paso
`receive --late`). **Abstenciones (3):** la suite completa (reservada a quien cierra), INV-7 a nivel de árbol
completo y la estabilidad del digest del documento de cierre bajo edición posterior (afirmada por lectura del
código, no sondeada).

**Suite de cierre (una vez, por quien cierra)** — `closure-suite.md`: worktree aparte en `--detach` sobre
**`2de9747`** (incluye el código de T1 y toda la documentación de la unidad), armado con `make staging` en el
perfil por defecto. `python3 -m pytest tests -q -p no:cacheprovider` → **1028 passed / 4 skipped, sin fallos**
(19 min 42 s; incluye los 4 focales nuevos). `make validate` → **155 PASS / 1 FAIL**, el fallo **F011**
(`scripts/validate-subagents.sh`, drift de copia instalada) **preexistente y declarado** (D-6 de 005-011), el
mismo resultado que la suite de cierre de 005-012. El código de producto del worktree es byte a byte el de
`a4028af`.

**Decisiones relevantes.** **D-1** el arreglo se **acota a `closure`**: las demás clases no comparten el mismo
arreglo (su replay legítimo ocurre con la feature **abierta**, donde el no-op ya opera) y `late-delivery` es el
modelo ya declarado; **trade-off declarado:** el `--feature` silenciosamente ignorado en `gate` (E-1) y el
replay tras un **cambio** de feature activa (E-2) van a deuda priorizada. **D-2** la feature de `closure` se
resuelve por **tres fuentes en orden** y la tercera —la ligada por la **ejecución activa**, que el cierre no
limpia— es lo que hace reanudable la orden verbatim; **razón:** es **un único valor** ligado por la ejecución
(el mismo que el CLI ya resuelve sin flag), no una búsqueda en la historia. **D-3** **techo de PD-27:** sin
feature activa la operación **nunca aplica** un cierre (sólo reconoce el ya registrado o rechaza cerrado), que
es lo que impide que la enmienda ensanche el comportamiento. **D-4** en la rama de feature cerrada la
**identidad decide antes que el mundo** (PD-23: resolución del documento de cierre y búsqueda de identidad
**antes** de PD-8(a)/(b), del requisito de `--closure-path` y de la autoridad); **consecuencia declarada:** un
replay legítimo es no-op **aunque el mundo haya cambiado** después del cierre, con el **límite** de que la
identidad lleva el digest resuelto (PD-20) y el documento citado debe seguir existiendo. **D-5** el rechazo
**no inventa marcador**: reusa `state incoherent`, ya declarado por PD-12(i) de 005-012, y **no** abre una vía
de re-cierre.

**Deuda detectada (abierta, con condición de cierre; la unidad no tiene `debt.md` propio — la deuda declarada
vive en la spec §6 y en la review).** **E-1** (`gate` ignora `--feature`: desvío silencioso, la entrada queda
huérfana) y **E-2** (replay tras un cambio de feature activa: la identidad incluye `execution_id` y `open-unit`
acuña una ejecución nueva ⇒ otra clave ⇒ no hay no-op) **priorizadas**; **E-3** (el chequeo feature↔ejecución
de `validate-state` no se replica), **E-4** (una entrada `closure` con la fórmula anterior de la clave no se
reconoce como no-op y, con la feature cerrada, PD-25 la rechaza; no se migra el state), **E-5**
(`_packet_has_receipt` directorio vs `_durable_receipt` archivo, anotada por el discovery §3.6) y **E-6** (la
rama «ninguna de las tres» de PD-22 **no** tiene caso propio en el focal: fallback defensivo declarado; la
review comprobó que **funciona**, lo que no la convierte en cubierta). Review: **O-1..O-4** (Nit/FYI, sin
impacto material bajo el criterio 2026-10-12). **Despliegue pendiente (del dueño):** el comportamiento nuevo
**no existe en la versión instalada**; el despliegue lleva juntas 005-013, 005-012 y esta corrección.

**Lecciones de proceso.** (1) **El RED puede refutar el contrato:** el v1 aprobado era **internamente
contradictorio** en el escenario central del dueño y lo expuso el focal escrito por un test-writer aislado; la
**enmienda precedió al GREEN** (enmienda aprobada → RED → GREEN), conservando el orden de roles y el
anti-sesgo. (2) **Declarar la señal de contrato es parte del rol:** el test-writer **nombró** la contradicción
que encontró en vez de forzar la implementación a satisfacer un contrato contradictorio. (3) **Una unidad
correctiva chica no baja las garantías:** 4 focales + 47 de regresión + aceptación con el CLI real + suite de
cierre, sin plan aparte; la review reprodujo todo y agregó cinco sondas propias. (4) **La unidad se cierra con
la operación que ella misma corrige:** el cierre se registra con `register-transition --transition closure` (la
misma orden que la fila promete reanudable) y la repetición idéntica es el no-op medido en AC-1/AC-3
(evidencia de cierre: `docs/specs/005-014-closure-replay/closure.md`).

**Estado del epic.** `epic-005-real-operation` sigue en **`features-loop`**: **14/14** unidades cerradas (las
filas 1..14). **005-014 queda `done`** y **no queda ninguna unidad en cola**. El epic **NO se cierra** en este
tramo: quedan el **gate de saneamiento antes de publicar** (rutas personales absolutas e ids crudos en
archivos versionados; `execution.md:65-73`) —lo hace el **dueño** en un worktree aparte— y el **despliegue**,
que **decide el dueño**. El proyecto queda **en reposo**.

## 2026-10-14 — Feature: 005-012-transition-registration (epic 005)

**Cerrada el 2026-10-14 (ciclo técnico completo).** Decimotercera y **última** feature de epic-005 (tras 005-001, 005-005, 005-006, 005-008, 005-009, 005-010, 005-002, 005-003, 005-007, 005-004, 005-011 y 005-013). Cierra la **fila 12** del plan del epic (`docs/epics/epic-005-real-operation/plan.md:45`): **una operación del CLI que registra la decisión explícita del orquestador sobre una transición** —recepción de una entrega, aprobación de un gate, avance de etapa, cierre de feature y, por B1, **disposición de un despacho sin recibo**—, **comprueba sus requisitos mecánicos** y **la aplica sin edición manual del state**, con las tres propiedades de la fila: (a) exige la **evidencia referenciada** y que el gate lo apruebe la **autoridad vigente**; (b) **recibir nunca aprueba**; (c) repetirla **no duplica efectos**; (d) **automatiza la contabilidad y conserva el juicio**. Decisión propuesta para registro en **ADR-029** (borrador del cierre).

**Contrato y plan.** `spec.md` sha256 `9e34750f…` (draft-004) y `plan.md` sha256 `9abfb894…`, aprobados **juntos, en una sola acción**, por el **orquestador OpenCode** el **2026-10-14** bajo la **HITL delegada del epic-005**, con **dos enmiendas del contrato** en el tramo: (1) por **B2** (PD-10: la **identidad** de la transición incluye los **insumos con efecto** y su payload canónico se escribe en la entrada como `transition_key_payload`) y (2) por **B3** (PD-14/D-8: la **vigencia** de una aprobación la decide **el pin que nombra los bytes actuales**, el mismo criterio que el cierre ya usaba en PD-8(b)). Cada aprobación **sustituye** la anterior —draft-001 `89ba8ea1…`, draft-002 `6504e655…`, draft-003 `56d0be4b…`—, todas **inoperantes por el pin** además de sustituidas; el architect entregó DRAFT y **no aprobó su propia propuesta** (anti-sesgo, ADR-003/ADR-011). **Producto y contratos nombrados:** `transition-registration-v1`, `stage-gate-registration-v1`, `approval-vigency-v1`, `closure-required-check-v1`, `late-delivery-v1`, `open-context-guard-v1`, `registration-docs-v1`, `acceptance-report-v1`.

**Producto (T1..T7 con RED→GREEN por ficha, T8 = gate; el reparto es el del plan §4).**

- **T1 — superficie `register-transition` + escritor único + digests derivados + identidad + forma mínima (`delivery`, `advance`).** `skills/cdad-cycle/scripts/cdad_packet.py` (+312): el subcomando nuevo entra en `build_parser`/`main`, escribe por el **lock y la publicación atómica existentes** (`_ProjectLock`, `_publish_owned_atomically`/`_publish_generation`, `_serialize_document`), estrena el marcador **`evidence missing`**, resuelve los **digests derivados** (si se omiten, el CLI los calcula de los bytes actuales, los escribe y los imprime; si se afirman, los verifica y una diferencia falla cerrado) y calcula la clave de identidad con su payload. **Gate:** RED 15/15 por **aserción** (0 por import/sintaxis) `878091b` → GREEN **15 verdes** `401f966`, con regresiones declaradas **56 verdes** y `git diff -- tests/` **vacío**.
- **T2 — `gate`: pin verificado contra los bytes + autoridad en tres casos (PD-5/PD-6).** `cdad_packet.py` (+152/−4): `approved_by` no vacío; pin de contrato y de plan **derivado** o verificado; autoridad con delegación vigente (revocada o vencida **falla cerrado**), **sin** delegación (se registra el aprobador declarado y la salida lo declara: el dueño **no** se bloquea) y sin epic. *(RED 14/14 por aserción `112ce91` → GREEN **14 verdes** `21bada6`; regresiones 33.)*
- **T5 — vigencia estructural de la aprobación (`supersedes` + lector aditivo), PD-14/PD-15.** `cdad_packet.py` (+62/−2): una sola aprobación vigente por `(feature, contract_path)`, marca **estructural** en la entrada nueva, lector aditivo que la ignora, y la exigencia de `--supersedes` sólo cuando **compite** una entrada **vigente**. *(RED 5/5 por aserción `9669c0a` → GREEN **5 verdes** `c164b30`; regresiones 42; `validate-state` rc=0 sobre el state real, aditividad.)*
- **T3 — `closure` (comprobación ANTES de aplicar) + `disposition` (la salida del despacho sin recibo, B1).** `cdad_packet.py` (+269/−2): el cierre comprueba **entregas requeridas** (todo paquete despachado de la ejecución activa con recibo durable **o** disposición registrada) y la **aprobación vigente** pinneada **antes de cualquier escritura**, falla cerrado **nombrando** lo que falta con su marcador (`evidence missing` / `approval pending`) y **ofrece las dos salidas legítimas** (recibir, o **disponer**); `--transition disposition --packet <id> --resolution <abandoned|superseded>` registra **sólo** una traza estructural (`resolution`, `replaced_by`, `approval_effect: false`, sin `approved_by`, **sin** fabricar un `completed`), con la feature **abierta**. **Incidente del tramo:** el GREEN **se detuvo y bloqueó** con **7/8** focales (el octavo exigía un documento de cierre que su fixture nunca escribía: defecto **del fixture**, no del producto), **sin editar tests ni fabricar digests** —la conducta que el contrato manda—; la ronda de corrección del test (`016405f`, +14 líneas de **precondición**, 0 aserciones tocadas) cerró el focal **8/8** y el gate se aprobó **después** de la entrega (separación entrega/gate ejercida de verdad, PD-4). *(RED 8/8 por aserción `99b65e6`; GREEN `0057a50`; gate `2920b3e`; regresiones 20.)*
- **T4 — entrega tardía: `receive --late` + `late-delivery`.** `cdad_result.py` + `cdad_packet.py` (+130/−7): un modo **declarado** de `receive` que **reusa** la máquina de recibos (identidad, partes, digests, esquema del recibo, `semantic_status: "pending"` siempre) e **invierte sólo la precondición de vigencia** (la feature destino **está** cerrada), y la clase `late-delivery` que exige el recibo durable y deja **sólo** la traza, sin reabrir la feature ni aprobar nada. *(RED 7/7 por aserción `f8fd4fb` → GREEN **7 verdes** `f5e0fc2`; regresiones 25.)*
- **T6 — `prepare --new-execution` rechaza el contexto abierto y sin uso (PD-16).** `cdad_packet.py` (+72): cierra la deuda que 005-013 dejó a esta unidad (la **ejecución huérfana**): rechaza con `state incoherent` **nombrando** el contexto abierto y cómo seguir, sin acuñar un segundo id; el uso legítimo sin contexto previo sigue funcionando. *(RED 3 casos `4b8bf5c` —el del contrato rojo por aserción con el motivo correcto— → GREEN **3 verdes** `721990f`; regresiones 42.)*
- **T7 — documentación por referencia (PD-19/INV-4), docs-only.** `skills/cdad-cycle/references/re-entry.md` (paso 4 **nombra** la operación, conservando que el recibo liga las partes y **no** aprueba) y `project-execution.md` (**sección nueva** contigua a las operativas §5-§8, con la referencia a la spec, sin re-declarar la regla del pin ni la del escritor único). *(Comprobaciones observables; el sentido del texto lo juzgó la review. `7b10325`.)*

**Review formal (etapa 4) — 2 bloqueantes / 7 opcionales / 3 abstenciones** (`review.md`, diff `74b0f4e..HEAD`: 25 archivos, +7448/−20; reviewer `mofgw/glm-5.3-flash`, **familia distinta** a la del implementer `mofgw/deepseek-v4.1-flash`, sesión independiente y sólo lectura; 52 focales corridos por el reviewer). **Los dos bloqueantes eran escapes del contrato numerado que la ficha no revelaba** y los dos se corrigieron con **RED primero**:

- **B1 — la comprobación de autoridad de PD-6 no se aplicaba a `closure`** (una sola call-site de `_gate_authority`, en la rama `gate`): un cierre bajo delegación **revocada o vencida** prosperaba escribiendo `approved_by` y marcando `done`. **CORREGIDO YA:** RED de 3 casos (`331566c`) → GREEN reusando el diagnóstico existente (`724ca3c`, +28/−13; focal del B1 **11 verdes**, el de T2 sin cambio).
- **B2 — `transition_key` omitía los insumos con efecto**, así que N `delivery` del mismo paquete con la misma etiqueta (el uso natural para registrar las postcondiciones de un GREEN) devolvían rc=0 «no-op» **sin registrar y sin fallar**. **CORREGIDO con enmienda del contrato** (draft-003: PD-10 con el payload canónico y `transition_key_payload`; PD-11 con el no-op **honesto**) y después RED de 5 casos (`f7fcbcc`) → GREEN (`64a32d3`, +91/−16; focal **21 verdes**). **Consecuencia declarada, sin migrar el state: deuda D-12.**
- **B3 — la reaprobación de una enmienda del contrato estaba obligada al registro manual** porque el control de exclusión de PD-14 exigía `--supersedes` ante una entrada `specification` vigente, y `--supersedes` **sólo puede citar entradas con `transition_key`**, mientras que todas las aprobaciones registradas a mano (las de todas las features anteriores y **las tres de ésta**) son **keyless**. Hallazgo del **orquestador** al reaprobar la enmienda de B2 (**medido, no supuesto**: la nota de esa entrada transcribe las **dos** respuestas del CLI), declarado **bloqueante para el uso previsto** por el orquestador Claude. **CORREGIDO con enmienda del contrato** (draft-004: PD-14 pasa a «el pin que **nombra los bytes actuales**», el mismo criterio de PD-8(b); el caso raro de los **mismos** bytes con una entrada vigente **sin clave** va a **deuda D-16**, sin inventar mecanismo) y después RED de 3 casos (`dc13903`) → GREEN (`ffb7abd`, +13/−1; focal de T5 **8 verdes**).
- **Opciónales:** **O1..O4** (texto de AC-4/ficha T3, paréntesis de `--stage`, la «tabla» que no existe, el mecanismo del control de fecha) se corrigieron **en la misma enmienda** del contrato; **O5/O6/O7** van a deuda (**D-13..D-15**). **Abstenciones (3):** la evidencia de T8 (gate del orquestador — **resuelta** corriéndolo), la suite completa (reservada a quien cierra — **resuelta** en el cierre) y la auditoría recibo-por-recibo de las transiciones ya registradas (material del audit del orquestador). El reviewer juzgó **correcta** la divergencia de `gate` frente a `validate-state`/`prepare` ante delegación vencida **por fecha** (PD-6 lo exige; `_validate_v2_vigency` no lee `expires_on`) y verificó que la limitación de `tdd_substage` **no** obliga a editar el state a mano (ningún validador lo lee).

**Aceptación (T8) — APROBADA, y repetida sobre el commit final.** `acceptance.md` (sha256 `da6e3d59…`): **CLI real del repo** como subproceso sobre **proyectos descartables en `<tmp>`** con el `HOME` del subproceso en un tempdir **vacío** (nunca este repo, nunca HOME), fixture sintético y anónimo. **AC-1** (ciclo representativo registrado **sólo** con la operación, en la **forma mínima sin pasar ningún digest**): **8 invocaciones, todas rc=0**, **7 entradas** de la operación (`advance`, `gate` de etapa 2, `delivery` RED, `delivery` GREEN, `delivery` del Memory Bank, `gate` de T4, `closure`), feature `done`/`active_feature: null`/`idle`, con los digests **derivados** por el CLI y **cero** ediciones manuales del state. **AC-2** (entrega tardía sobre feature cerrada): `receive` normal sigue fallando cerrado, `receive --late` rc=0 con recibo durable y `semantic_status: pending`, `late-delivery` rc=0, la feature **no se reabre** y no aprueba nada. **AC-3** (repetición): idéntica → no-op **byte-idéntico** nombrando la entrada; distinta (otro `--current-stage`) → entrada nueva; estructuralmente excluyente → rc=2 `state incoherent` sin efectos. **AC-4** (B1): cierre sin aprobación → `approval pending`; con un despacho **sin recibo** → `evidence missing` **nombrando el paquete**, state intacto, **ofreciendo las dos salidas legítimas y ya no `late-delivery`**; registrada la disposición, el cierre **avanza**. T8 se **repitió sobre `6fd515d`** (después de B3) con los mismos resultados, y ese gate quedó registrado con la operación.

**Suite de cierre (una vez, por quien cierra)** — `closure-suite.md`: worktree fijado a **`6fd515d`** (incluye T1–T7, los review-fix **B1, B2 y B3** y la evidencia de T8). `python3 -m pytest tests -q -p no:cacheprovider` → **1024 passed / 4 skipped, sin fallos** (20 min); `make validate` → **155 PASS / 1 FAIL**, el fallo **F011 preexistente** (D-6 de 005-011). Entre `6fd515d` y este registro sólo cambia documentación de cierre.

**El dato de la unidad (la primera feature que se cierra con la operación que ella misma entrega).** En el `stage_history` de esta feature hay **30 entradas del tramo (2026-10-14)**: **24 registradas con la operación** (20 `delivery` + 4 `gate`) y **6 a mano**, cada una con su motivo declarado en su nota —el **discovery**, las **cuatro aprobaciones `specification`** (registradas por el procedimiento propio del orquestador, **keyless**) y el **RED de T1**—. De las manuales, **dos** son las que el encargo del cierre nombra: el **RED de T1** (la operación **todavía no existía**: la introduce su GREEN) y la **reaprobación de la enmienda B3** (el arreglo **todavía no estaba implementado**, así que la operación habría rechazado esa misma invocación; declarada como **última transición manual por esta causa**). Y hay una tercera que la medición agrega: la **reaprobación de la enmienda B2**, donde **la operación no pudo registrar** la transición —respondió `state incoherent` nombrando `transition_key None` y `--supersedes` con cualquier clave falló `does not name an existing specification approval`—: ése es **el defecto B3 medido, y es lo que B3 corrige**. Dato de frontera de versión declarado por el contrato y sin migración (**D-12**): de las 24 entradas de la operación, **18** llevan la **fórmula anterior** de la clave (sin `transition_key_payload`, 20 `delivery`/`gate` anteriores al GREEN de B2) y **6** el payload canónico nuevo; ninguna queda invalidada y ninguna se reescribe.

**Decisiones relevantes.** **D-1** la superficie es un **subcomando nuevo**, simétrico a `open-unit`, con el **escritor único** existente; `prepare` **conserva su rol** de productor de paquetes y no registra transiciones. **D-2** el alcance cubre **seis clases** (`delivery`, `gate`, `advance`, `closure`, `late-delivery`, `disposition`): es el **límite duro** que hace AC-1 alcanzable (lo único que queda con camino propio es el staging del buzón + `receive` + `materialize`, que no es una edición del state). **D-3** la **frontera del juicio** es explícita: el CLI comprueba estructura, digests, vocabulario, existencia de la autoridad vigente y de las recibos/disposiciones; **no** juzga el significado de un texto, la calidad de una entrega, si un bloqueante es bloqueante, si una deuda se acepta **ni si un despacho debe disponerse**. **D-4** el **cierre comprueba antes de aplicar** (entregas requeridas + aprobación vigente) y **tiene salida** cuando el despacho no vuelve. **D-7/D-10** la **identidad es por contenido**: `transition_key = sha256(payload canónico)` con los insumos con efecto, escrito en la entrada —la repetición idéntica es no-op **independiente de la cabeza**, la distinta es entrada nueva y la estructuralmente excluyente falla cerrado—. **D-8/D-14 (B3)** la **vigencia** es **estructural y única**: el pin que **nombra los bytes actuales** (el mismo criterio del cierre), marcada por el campo `supersedes` en la entrada nueva, nunca por prosa (`PD-15`). **D-13 (B1)** la **disposición** de un despacho sin recibo es una **clase propia** (no una reutilización de `delivery`): registra la **decisión** como dato estructural, **no** aprueba y **no** fabrica un `completed`. **D-14 (P1)** los **digests los deriva el CLI**; afirmarlos es una verificación **opcional** para citar exactamente los bytes revisados. **D-6 (P2)** la autoridad del gate tiene **tres casos** y **no bloquea al dueño** sin delegación. **D-5** la entrega tardía usa el **buzón como entrada** con `receive --late` y marcador propio, sin reabrir ni aprobar.

**Deuda detectada (abierta, con condición de cierre; se consolida en `debt.md` del cierre).**

- **`D-1..D-16` de la spec §7** (la **D-9 quedó RETIRADA**: la anulación de un despacho ya no es deuda, su salida es la disposición). Las nuevas del tramo: **D-12** (las entradas con la fórmula anterior de la clave dejan de reconocerse como no-op candidato; **sin** migrar el state), **D-13/D-14/D-15** (los opcionales **O5**, **O6** y **O7** de la review) y **D-16** (reaprobar los **mismos** bytes desde una aprobación vigente **sin clave** no tiene salida; **no** se le inventa mecanismo). Se citan además **D-1** (veredicto fino de `reconcile` a nivel de ejecución), **D-2** (`review_status` sigue apuntando a 005-013 con `active_feature` 005-012: campo derivado **sin dueño**), **D-3** (tamaño del state), **D-5** (contexto abierto por otra vía), **D-6** (identidad de quien aprueba), **D-8** (staging del buzón y `RESULT.json`, deuda D-10 de 005-004), **D-10** (la vigencia **del state** sigue exigiendo delegación con epic activo) y **D-11** (despachos sin recibo de ejecuciones **cerradas**).
- **Review:** las **3 abstenciones** (la de T8 y la de la suite **quedaron resueltas**; la auditoría recibo-por-recibo de las transiciones registradas queda como material del audit del orquestador) y **O5/O6/O7** → deuda **D-13..D-15**.
- **El commit del heartbeat externo `da3612a`** (`state: sync .cdad-state.json checkpoint (HB 14 Oct)`): escribió el state **fuera del flujo del ciclo** (movió `active_packet` del RED de T1 al GREEN de T1 antes de que el orquestador registrara la transición). El state quedó válido y la transición se registró después; el dato queda como **evidencia de la clase de escritura que esta unidad reemplaza** (un escritor externo con acceso al state, sin transición de la operación). *Cierre:* el `active_packet` pasa a tener un único camino de escritura por transición registrada.
- **Los dos digests escritos mal a mano y corregidos** (declarados por el encargo de cierre como **evidencia de por qué existe esta unidad**): el registro manual obliga a **transcribir digests a mano** y esa transcripción se equivocó y hubo que corregirla; el precio de calcular y copiar digests a mano en una edición del state es exactamente lo que PD-20 (digests **derivados** por el CLI) elimina. Queda como dato declarado del cierre, consolidado en `debt.md`.
- **Despliegue pendiente (del dueño).** La operación **no existe en la versión instalada** (**D-4**, compartida con el despliegue de **005-013**): el próximo despliegue lleva **las dos features juntas**, y hasta entonces el registro de transiciones sigue siendo manual en cualquier proyecto que use el CLI instalado. **Bloqueo declarado con responsable (dueño)**, no verde por proximidad.
- **Pendientes del cierre del epic** (no de esta feature): el **saneamiento antes de publicar** (`execution.md:65-73`) y la decisión del dueño.

**Lecciones de proceso.** (1) **La review ve lo que los focales verdes no ven:** los dos bloqueantes eran **escapes del contrato numerado** que la ficha de la tarea no revelaba (PD-6 no aplicada a `closure`; una identidad que **tragaba** invocaciones distintas como no-op **afirmativo**), y el tercero (**B3**) lo destapó el **uso previsto** —el orquestador al reaprobar—, no un test. (2) **Un bloqueante *del contrato* exige enmendarlo antes del RED/GREEN:** B2 se corrigió en el contrato (draft-003) y **después** en el código; B3 igual (draft-004). Ese patrón —enmienda aprobada, RED, GREEN— mantuvo el orden de roles y el anti-sesgo. (3) **El rol que se detiene cuando debe es evidencia, no un fallo:** el implementer de T3 bloqueó con 7/8 focales y **no editó el test** ni fabricó digests; la corrección fue una ronda del test-writer que tocó **sólo** la precondición del fixture, y el gate se aprobó **después** de la entrega. (4) **Una unidad que reemplaza el trabajo manual puede medirse a sí misma:** el defecto que B3 corrige se midió **con la operación nueva rechazando su propia reaprobación**, y de sus 30 entradas de tramo, 24 ya las registró la operación.

**Estado del epic.** `epic-005-real-operation` sigue en **`features-loop`**: **13/13** unidades cerradas (las filas 1..13, 13 features) — **última unidad**. **005-012 queda `done`** y **no queda ninguna en cola**. El epic **no se cierra** en este tramo: quedan el **gate de saneamiento antes de publicar** (rutas personales absolutas e ids crudos en archivos versionados, `execution.md:65-73`), el **despliegue** de 005-013 y 005-012 (dueño) y la decisión del dueño. El proyecto queda **en reposo**.


## 2026-10-14 — Feature: 005-013-unit-contract (epic 005)

**Cerrada el 2026-10-14 (ciclo técnico completo).** Duodécima feature de epic-005 (tras 005-001, 005-005, 005-006, 005-008, 005-009, 005-010, 005-002, 005-003, 005-007, 005-004 y 005-011). Cierra la **fila 13** del plan del epic (`docs/epics/epic-005-real-operation/plan.md:46`): **el hash identifica el contrato que recibió el agente y deja de bloquear globalmente la planificación del proyecto.** La corrección es **una sola palanca**: el **contrato de una unidad** pasa a ser una **proyección GENERADA del plan** (objetivo, alcance y aceptación de la unidad + las secciones compartidas que le aplican + su aprobación y versión de origen), **publicada una vez** junto al paquete y **pineada por su digest**; el sha del plan queda como **procedencia** (bloque de origen). La unidad se localiza **estructuralmente** (la **única** fila de una tabla del plan que contiene el id de la feature **como token completo**, con el encabezado de esa tabla) y, si no se puede localizar sin ambigüedad (cero o más de una fila), hay **fallback declarado** al contrato vigente (plan completo, `approved-epic-plan`), informado en el diagnóstico (stderr) y en `status` (`mode: "fallback"`). **Las consecuencias dependen del tipo de cambio:** `current` (sin efecto), `impact` (registro durable e idempotente; decide el orquestador) o `impeded` (**sólo** por autorización retirada, rc=2, con la salida existente nombrada). **La recepción y el resume validan contra la proyección registrada** (los bytes que el paquete recibió), **no** contra el plan vivo. Sin documento nuevo y sin segunda copia: las reglas se **referencian** (005-003, 005-005, 005-007, 005-001). Decisión propuesta para registro en **ADR-028** (borrador del cierre).

**Contrato y plan.** `spec.md` sha256 `4369822e…` y `plan.md` sha256 `89d5d8cf…`, aprobados **juntos, en una sola acción**, por el **orquestador OpenCode** el **2026-10-14** bajo la **HITL delegada del epic-005**, tras la corrección del draft pedida por la **review del orquestador Claude** (`review-claude-spec-2026-10-14.md`: B1.1..B1.4, B2 y P1). El architect entregó DRAFT y **no aprobó su propia propuesta** (anti-sesgo); el pin `specification` de los roles de construcción (005-001 I2/PD-18) **no** se tocó (verificado por T3: digests de `spec.md`/`plan.md` idénticos antes y después). **Producto y contratos nombrados:** `unit-projection-v1`, `change-consequence-v1`, `unit-contract-references-v1`, `acceptance-report-v1`.

**Producto (T1, T2, T3, T4; RED/GREEN por ficha; el gate con números).**

- **T1 — proyección de unidad, localizador estructural, fallback y anclas por declaración del producto (PD-1..PD-6).** `skills/cdad-cycle/scripts/cdad_packet.py` (+397/−15) y `skills/cdad-epic/assets/epic-plan-template.md` (+11, la declaración **legible por máquina** de las anclas: historia `["Plan changes", "Cambios al plan"]`, autorización `["Stakeholders", "Autoridad"]`). Publica `.cdad/packets/<packet_id>/UNIT-CONTRACT.md` en la misma generación, con `contract = {kind: approved-unit-contract, path, sha256, commit: null}` y `active_packet.contract_sha256` = ese digest; `validate_request` acepta **exactamente** los dos pares (proyección o fallback). **Gate focal:** RED **14 rojos por aserción + 1 control declarado** (`14 failed, 1 passed`; todas `AssertionError` de contrato, 0 por import/sintaxis; entre ellos `receive` rc=2 «contract sha256 does not match exact content» contra el plan vivo tras agregar la unidad futura); GREEN **15 verdes**; **regresiones declaradas 77 verdes** (+ 82 proporcionales). (`9785423` RED / `021a491` GREEN.)
- **T2 — veredicto de consecuencias (PD-7..PD-11).** `skills/cdad-cycle/scripts/cdad_packet.py` (+430/−20): operación **de lectura** `validate-unit-contract` (regenera la proyección viva, resuelve la **línea base** —el `UNIT-CONTRACT.md` publicado más recientemente de la unidad, empate → id mayor; el `active_packet` cuenta— y clasifica **por parte**, ignorando el origen), journal durable `.cdad/packets/<baseline_packet_id>/.impact.json` **idempotente por par de digests**, `impeded` **sólo** por autorización retirada (`approval pending` / `state incoherent`, con la salida nombrada), y bloque **aditivo y de solo lectura** `unit_contract` en `status`. **Gate focal:** RED **15 rojos** (todos por aserción; el subcomando no existía → `invalid choice`), GREEN **15 verdes**; **regresiones declaradas 59 verdes** (+ focal T1 15 verdes). (`c61db34` RED / `da3ced5` GREEN.)
- **T3 — referencias y fronteras documentales (PD-12/PD-13; docs-only).** `skills/cdad-cycle/references/project-execution.md` (+21): la autoridad del architect **nombra por referencia** (sin copiar el mecanismo) el contrato de unidad, su origen y la salida del impedimento. **Comprobaciones observables:** 0 bloques `plan-tasks` a mano en el plan del epic, 0 listas de títulos por proyecto (la declaración vive **una sola vez**, en el activo del producto), digests de `spec.md`/`plan.md` sin cambios. **Regresiones declaradas 21 verdes** (+ 29 proporcionales). (`b3cb88c`.)
- **T4 — gate de aceptación (AC-1..AC-10).** Prueba decisiva con el **CLI real del repo** como subproceso sobre **proyectos descartables en `<tmp>`** (HOME del subproceso en un tempdir vacío; **nunca** este repo, **nunca** HOME), en las **tres formas de plan** de B1.4: **(i)** la de este epic; **(ii)** una generada desde la **plantilla del producto**; **(iii)** un **fixture sintético y anónimo** con la celda de la unidad como **enlace** y sin historia ni autoridad. **En las tres, sin fallback:** AC-1/AC-3 (publicación y pin: `sha256(archivo) == contract.sha256 == active_packet.contract_sha256`; la parte `unit` verbatim) **4/4**; AC-2 (fallback declarado cuando el plan no tiene fila de la unidad: rc=0, `kind=approved-epic-plan`, sin `UNIT-CONTRACT.md`, motivo en el diagnóstico, `mode: fallback` en `status`); AC-4 (tramo 1: despacho real → agregar una unidad futura independiente → `receive` **rc=0** con `packet_validation`/`identity_validation` `passed`, `semantic_status: pending`, veredicto **`current`**); AC-5 (tramo 2: editar el alcance de la unidad → **`impact`** con journal `changed_parts = ["unit"]` y los dos digests, sin bloquear la recepción); AC-6 (editar la sección de autorización → **`impact`, nunca `impeded`**; autorización retirada → **rc=2 `impeded`** con `approval pending` y la salida nombrada; registrarla → `prepare` rc=0 y la proyección nueva como línea base); AC-7 (dos `status` dejan el proyecto **byte a byte idéntico** y sin journal; dos `unit-contract` con el mismo par dejan el journal **byte a byte idéntico**); AC-8 (origen 5/5 en las tres formas). **AC-10 declarado para el cierre.** (`7ab16ba`.)

**Review formal (etapa 4) — 1 bloqueante / 5 opcionales / 1 abstención** (`review.md`, diff `7b0be10..HEAD` hasta el registro de T3: 11 commits, 11 archivos, +3232/−20; reviewer de **familia distinta** a la del implementer, sesión independiente y solo lectura; el informe del rol trae **segmentos corruptos por el modelo** que no cambian la sustancia —el veredicto y su evidencia son legibles y están resumidos en el addendum del orquestador). **Disposición:**

- **B1 (bloqueante, `Bucket: h`) — CORREGIDO YA.** `prepare` con `--out-dir` custom podía **reescribir** el `UNIT-CONTRACT.md` de un paquete ya publicado en el directorio por defecto (el `packet_id` se acuña contra el `out_dir` custom mientras la proyección se publica en la ruta canónica, con `os.replace` ciego), rompiendo el pin del paquete viejo (INV-3/PD-4) y dejándolo irrecebible. **Medido por el reviewer:** el `sha256` de la proyección del paquete viejo pasó de `2237d30d…` a `cec98be9…` y su `contract.sha256` durable dejó de coincidir. **Review-fix:** RED con **3 casos nuevos** (colisión → falla cerrada nombrando el paquete en conflicto y bytes del paquete viejo **byte-idénticos**; el paquete viejo sigue recebible; control sin colisión publica creando el padre canónico), GREEN con el **focal T1 en 18 verdes** (15 originales + 3 nuevos) y **regresiones 77 verdes**, `tests/` intactos. (`4bf688c` RED / `f41025f` GREEN.)
- **O1 (nit) — CORREGIDO como errata declarada.** El informe de T1 GREEN afirmaba «con un `--out-dir` custom la publicación no procede»: es **falso** (procede a la ruta por defecto y pisando). El texto original se conserva como registro de la entrega y la **fe de errata** del orquestador es la declaración vigente.
- **O2..O5 — A DEUDA** (ver «Deuda detectada»).
- **Abstención (1) — RESUELTA corriendo T4.** El reviewer se abstuvo sobre AC-9/T4 (la ficha estaba abierta y no estaba en el diff; correcto: se corre después de la review). T4 se corrió después (`acceptance.md`).
- El reviewer adjudicó los **dos FAIL** que informó el implementer de T2 (`scripts/validate-subagents.sh` por drift de los agentes instalados en `<home>` y `tests/validate-odoo-specialization.sh` A3 por patrones sensibles pre-existentes) como **preexistentes/ambientales y ajenos al diff**; en el worktree de cierre con staging **no aparecen**.

**Suite de cierre (una vez, por quien cierra)** — `closure-suite.md`: worktree fijado a **`7ab16ba`** (incluye T1–T3, el review-fix de B1 y la evidencia de T4), armado con `make staging` en el perfil por defecto. `python3 -m pytest tests -q -p no:cacheprovider` → **960 passed / 4 skipped, sin fallos** (18 min); `make validate` → **155 PASS / 1 FAIL**, el fallo **F011 preexistente** (D-6 de 005-011). Al cierre de 005-011 eran 927; la diferencia (33) coincide con los focales nuevos de la unidad (18 de T1 + 15 de T2). El código no cambió entre `7ab16ba` y este registro (solo documentación de cierre).

**Decisiones relevantes.** **D-1** el contrato de la unidad es una **proyección generada**, publicada **una vez** junto al paquete y **pineada por digest**; **no** se re-genera en cada validación (evita el hazard de byte-identidad verificado en el discovery §3). **D-2** kind nuevo `approved-unit-contract`; `approved-epic-plan` se conserva (es el contrato del fallback). **D-3** consecuencia por **identidad y clase de parte** (`unit` | `shared`), **nunca por prosa**: el CLI **no** juzga el sentido de un texto (INV-8); la clase `authority` **desaparece** y lo único que produce `impeded` es **retirar la autorización**. **D-4** recepción y resume contra la **proyección registrada**, sin tocar el esquema del recibo ni ampliar autoridad (recibir **no** aprueba). **D-5** el origen registra unidad, plan, sha del plan al generar, `approved_by` y `policy_sha256`; **no** hay re-aprobación por unidad si la proyección no cambió. **D-6** fuente única: se referencia, no se copia; sin documento nuevo ni bloque `plan-tasks` a mano. **D-7** selección **estructural**, sobre-inclusiva (todas las `##` menos historia, con las líneas de la tabla localizada removidas) y **con fallback**; la sobre-inclusión es conservadora y declarada. **D-8** superficie del veredicto: `validate-unit-contract` (lectura) + bloque **aditivo** `unit_contract` de `status` que **informa y no escribe**. **D-9** fallback declarado (no falla cerrado). **D-10** anclas por **declaración del producto**, no por listas por proyecto. **D-11** línea base = la proyección del último paquete de la unidad; salida del `impeded` con mecanismos existentes (registrar la aprobación `epic-plan`). **D-12** journal de impacto **idempotente**; lo escribe **sólo** `validate-unit-contract`. **D-13** el aviso del fallback va a **stderr** (stdout de `prepare` sigue siendo el `PACKET.md` byte a byte).

**Deuda detectada (abierta, con condición de cierre).**

- **O2 (nit) — copia inerte de la declaración de anclas.** Cualquier plan completado desde la plantilla lleva una copia **inerte** del comentario `cdad:plan-anchors`; el generador lee la declaración del **activo del producto**, nunca del plan, así que la copia no tiene efecto. **No** es una segunda copia de la regla (la fuente de verdad sigue siendo una: el activo), pero **no está declarado** que los planes nuevos heredan la copia. *Cierre:* una frase en el propio comentario del template («copia inerte; el activo es la autoridad») o un caso PD-3 que lo declare.
- **O3 (opcional, `m`) — lectura del activo INSTALADO.** El generador resuelve la declaración de anclas desde el activo **co-ubicado con el script** (`.resolve().parents[2]`): el CLI del repo lee el activo del repo (que declara las anclas) y el CLI **instalado** lee el activo **instalado**. La review midió que las tres raíces instaladas tienen la plantilla **byte-idéntica a base** y **sin** la declaración (`grep "cdad:plan-anchors"` → **0**): con el CLI instalado el efecto es el **conservador** que PD-3 declara (ninguna ancla ⇒ todas las secciones `shared` ⇒ una edición da `impact`, **nunca** una falsa autorización). El riesgo de drift silencioso requiere un re-despliegue **parcial**. *Cierre opcional post-despliegue:* un `grep` del comentario en el activo de las raíces instaladas, o un `schema_version` dentro de la declaración.
- **O4 (nit) — límite de bytes de la vista.** El bloque `unit_contract` de `status` podría acercar la vista a su límite (`DEFAULT_VIEW_MAX_BYTES`, 16.384 B) si el plan es grande y **todos** los títulos cambian (`changed_parts` arrastra todos). La vista **falla cerrada** ante el límite (INV de 005-003), sin truncamiento adaptativo dentro del bloque. *Cierre:* respetar `--max-bytes` truncando `changed_parts`/`reason` con `+N more`.
- **O5 (nit) — `mtime` como aproximación de la fecha de publicación.** La línea base usa `st_mtime` + desempate por id; el reviewer lo juzgó **equivalente** a lo declarado en PD-7/D-11 (**nominal**).
- **D-1 (spec §8) — oráculos vigilados.** El churn de oráculos se reduce por el fallback: los fixtures de plan de los tests existentes **no declaran tabla de unidades** (verificado) y caen en el fallback conservando su comportamiento. *Condición de cierre:* focales de T1/T2 verdes (cumplido) y las regresiones declaradas corridas (cumplido), sin debilitamiento silencioso de tests congelados; la **lista de vigilancia** está declarada en la spec.
- **D-2 (spec §8) — reconciliación de un paquete `dispatched`.** **Fuera de alcance** (territorio de **005-012**); el veredicto `impact`/`impeded` la **nombra**, no la implementa. La **salida** del `impeded` (registrar la aprobación) **sí** queda dentro de esta feature.
- **D-3 (spec §8) — juicio de «restricción de aplicación inmediata».** El CLI **no** juzga la inmediatez de una restricción (no parsea prosa) ni la clasifica por listas de títulos; la parte de autorización se reconoce por la **declaración del producto** y se etiqueta. Una inmediatez mecánica exigiría una **marca estructural declarada** (no se inventa acá).
- **Acotamiento de la fila 13 (b) — declarado.** La fila 13 pide que «cambiar una restricción de aplicación inmediata» **impida** las acciones afectadas. La implementación lo **acota**: cambiar una restricción da **`impact`** y lo decide el orquestador (el CLI no puede juzgar la inmediatez sin una marca estructural). Lo aceptó la review del orquestador Claude en la segunda vuelta; queda como D-3. Nada se aprueba solo y el orquestador ve el impacto en `status`.
- **Datos para 005-012.** (1) La **ejecución huérfana** `exec-005-013-unit-contract-001`: no está versionada ni referenciada; es un dato de que, tras `open-unit`, `prepare --new-execution` debería **rechazarse** con un diagnóstico, no crear un segundo contexto. (2) Los **registros del state** de este ciclo (discovery y aprobación) se hicieron con **scripts sueltos en un directorio temporal**: el state queda bien y valida, pero el script que lo editó no queda como evidencia — otro caso del **registro manual de transiciones** que resuelve 005-012.
- **Despliegue pendiente (del dueño).** El comportamiento nuevo **no existe en la versión instalada** (el discovery verificó que el CLI del repo era byte-idéntico al instalado en `7212ead`; esa es la **procedencia** citada, **no** la versión bajo prueba). Hasta el despliegue, el generador del CLI instalado lee un activo **sin** la declaración de anclas (O3) y el pin de la unidad no existe en producción. El despliegue es del dueño (reservado).

**Lecciones de proceso.** (1) **El review encuentra lo que los focales verdes no ven:** B1 (la reescritura silenciosa de una proyección publicada por una colisión de `--out-dir`) fue un defecto real que el GREEN declaró **incorrectamente** como «no-op» —la declaración del rol decía «la publicación no procede» y la review la **reprodujo** y la refutó—; el GREEN se corrigió con **escritura create-only** y 3 casos nuevos, sin relajar ningún test. (2) **Una decisión de contrato que el CLI no puede tomar se declara, no se simula:** el veredicto clasifica por identidad y clase de parte; la inmediatez de una restricción queda en la review/orquestador (D-3). (3) **El fallback hace la feature aditiva:** los fixtures de plan existentes no declaran tabla → caen en el fallback y conservan su comportamiento (churn de oráculos casi nulo, verificado).

**Estado del epic.** `epic-005-real-operation` sigue en **`features-loop`**: **12/13** unidades cerradas (las filas 1..13, 12 features). **005-013 queda `done`.** **Restante en cola: `005-012-transition-registration`**, en el orden acordado **005-013 → 005-012**, **sin abrir** (`epic_features` con `005-012` en `queued`, `depends_on: 005-011-common-entry`). El **despliegue** sigue siendo del dueño; quedan como pendientes del cierre del epic el **saneamiento antes de publicar** y la segunda mitad de la propuesta «entrada y transiciones» (la **entrada común** la entregó 005-011; el **registro de transiciones** es 005-012).

## 2026-10-14 — Feature: 005-011-common-entry (epic 005)

**Cerrada el 2026-10-14 (ciclo técnico completo; la aceptación de uso corrió con la versión desplegada por el dueño).** Undécima feature de epic-005 (tras 005-001, 005-005, 005-006, 005-008, 005-009, 005-010, 005-002, 005-003, 005-007 y 005-004). Cierra la **fila 11** del plan del epic (`docs/epics/epic-005-real-operation/plan.md:44`): **una sesión nueva entra al proceso por una ruta breve y COMÚN —la vista `status`— antes de leer el state o explorar**, en los dos runtimes; la vista **nombra la pata que diverge y su resolución verificada**; y con un paquete `prepared` nombra la **acción natural (despacharlo)**. **Sin documento nuevo y sin segunda copia:** la regla se **referencia** a sus dueños (`orientation.md` §1 + `project-start.md` §11). Decisión registrada en **ADR-027**.

**Contrato y plan, con la enmienda 4.** `spec.md` sha256 `a6d05d9d…` y `plan.md`, aprobados por el orquestador OpenCode bajo la **HITL delegada del epic-005**, con la **autorización explícita de los dos oráculos** de PD-3 (spec §12). La revisión del orquestador Claude dejó tres enmiendas y, **tras AC-6**, se agregó la **enmienda 4**: la entrada común abarca también el **prompt del agente orquestador** → tarea **T2b**.

**Producto (T1, T2, T2b, T3; RED/GREEN por tarea).**

- **T1 — raíz relativa consistente en `cdad_packet.py` (PD-2/PD-3).** La resolución de `--project-root` se **unifica** a «resolver contra el cwd y exigir `is_dir()`», como `cdad_result.py`; se **retira** el rechazo especial de `status` y su diagnóstico **C4**, y se corrigen los textos que quedaban falsos (`orientation.md` §3 reescrito como «Project root resolution»; `project-execution.md:49`). **Los dos oráculos declarados** de PD-3 quedan actualizados: el C4 de 005-003 se **reemplaza** por el oráculo del comportamiento nuevo (raíz relativa aceptada → hay proyección) y el fixture de PD-5 cambia **solo** su invocación de fallo, **conservando** el oráculo de captura del `rc`. (RED `00dd36e`, testfix del oráculo `4ea82ea`, GREEN `53413b3`.)
- **T2 — entrada común en las dos `SKILL.md` (PD-1).** El **Step 1** de `cdad-cycle` y de `cdad-epic` consulta **primero** la vista `status`; `state-detection.md` pasa a **ampliación condicional** con gatillo en la tabla de referencias; `orientation.md` queda **indexado** en la tabla de `cdad-cycle` (antes no figuraba); se **conservan** la rama `resume` y la fila `project-start.md`. (GREEN `13c68b9`.)
- **T2b — la misma entrada en el prompt del agente orquestador (enmienda 4).** `sources/roles/orchestrator.md:107-112` gana el bullet **Session entry (every new session)**: la primera acción es cargar la skill `cdad-cycle` y consultar su vista `status`, **por referencia**; el state completo pasa a **ampliación condicional** con motivo registrado; `resume` deja de ser «the first step of every new session» y queda como **paso siguiente, solo con una ejecución activa** (se conserva literal la rama «start from rest»). Derivados regenerados con `make agents` **idempotente** (`agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`). (GREEN `68044cb`; el puntero al inicio del prompt, `8ec574d`, es **desviación declarada** del orquestador Claude.)
- **T3 — versión y siguiente acción en la vista (PD-4/PD-5).** Ante `DRIFT` la vista emite la **pata que diverge**, **leída** del chequeo (`project`/`agents`/`CLI`/`claude-code`), y afirma la **resolución** (el próximo `prepare` republica los derivados del proyecto) **solo** si la pata es `project`; la **ausencia** (`UNKNOWN`/`NO-PROJECT-AGENTS`) **no** lleva cláusula de resolución y no se confunde con la incoherencia. Con `active_packet.status == "prepared"`, `next.route` nombra la **acción natural (despacharlo)** con `--replace-packet` como **rama condicional**, sin cambiar `entry` ni la ruta de `dispatched`. (RED `1c207d9`, GREEN `860a611`.)

**Review formal (etapa 4) — 0 bloqueantes / 5 opcionales / 2 abstenciones** (`review.md`, con el sha del contrato verificado por el reviewer, de familia distinta a la del implementer). Corridas propias: focales **T1 5/5** y **T3 5/5**, los **dos oráculos de 005-003 21 passed**, guardas de texto de 005-005/005-006/005-009/005-010 **61 passed**; los tres GREEN **sin tocar `tests/`**; **falsificación** del oráculo corregido contra el CLI pre-fix en un worktree propio (falla por el motivo correcto, no por binding ni setup); anonimización verificada con grep. **OP-1** (afirmación vieja remanente en `orientation.md:69`) y **OP-2** (los dos «first» del Step 1 competían y el segundo se auto-describía con la situación de un coordinador nuevo) se **corrigieron antes del despliegue** por el orquestador Claude (`362ce3a`, desviación declarada; guardas de texto **72 passed**). **OP-3..OP-5** quedan como deuda. Abstenciones: **AB-1** (AC-6/AC-7/AC-8 fuera del alcance del paquete) y **AB-2** (la frecuencia real del misreading de OP-2 no es observable con el instrumento disponible).

**Aceptación de uso (T4) — gate APROBADO con AC-6 parcial declarado** (`acceptance.md`; la corrió el orquestador Claude con la HITL delegada, en clones descartables; la huella de la instalación global quedó igual antes y después).

- **AC-7 (Claude Code): CUMPLIDO.** Con la instalación de `7212ead`: `status` es la primera acción después de la skill (llamada 2), el primer `Agent` baja de la **llamada 23 a la 14** y la salida previa de **105 mil a 54 mil caracteres (−49 %)**; duración total 8,7 → 3,0 min. (1.ª corrida, `c2c04b4`: despacho en la 22, 80 mil car., −24 %.)
- **AC-6 (OpenCode): CUMPLIDO EN PARTE, Y SE DECLARA ASÍ.** Con los agentes del proyecto ya republicados en `7212ead`: la skill se carga en la **llamada 1** y `status` llega en la **llamada 3** (antes, llamada 21); el primer despacho baja de la **llamada 71 a la 59 (−17 %)** y el tiempo de 5,8 a 4,7 min (−20 %). **La brecha declarada:** no se cumple el orden estricto «`status` antes del state completo» — el modelo hace `cat` del state en la **llamada 2** (53 mil caracteres) inmediatamente antes. **Su causa:** es una lectura por costumbre del modelo y el costo lo pone el **tamaño del state** (unos 490 KB, en su mayor parte historia); otro ajuste del prompt da cada vez menos retorno (deuda estructural **RD-b**). La salida previa queda en 296 mil caracteres (−3 %).
- **Causa medida de la primera corrida fallida (corregida por T2b).** En OpenCode la **entrada real es el prompt del agente `cdad-orchestrator`, no la skill**: ese prompt decía que `resume` era «the first step of every new session» y no nombraba `status` (hoy corregido); por eso la corrección de T2 no llegó a OpenCode, mientras en Claude Code la skill se carga primero y ahí ya había mejorado. Se declara además la **fricción del medio de despacho** (llamadas 50–77), la misma que RD-9 de 005-004.
- **Límite de la evidencia (declarado).** **Una sola sonda por variante** → las cifras son **indicativas, no estadísticas**, y se comparan **like-for-like** con la línea base de `docs/specs/005-007-progressive-planning/acceptance.md` §7 (**70 llamadas previas / 304.054 caracteres**, despacho en la llamada 71) como **orientación, no umbral**. No se promete ningún ahorro fuera de lo medido.

**Suite de cierre (una vez, por quien cierra)** — `closure-suite.md`: worktree fijado a **`8ec574d`** (incluye T1–T3, la corrección de OP-1/OP-2 y T2b), `python3 -m pytest tests` → **927 passed y 4 skipped, sin fallos** (17 min); `make validate` **155 PASS / 1 FAIL**, el fallo **F011 preexistente** (D-6). La corrida anterior en `d862056` queda **reemplazada** como suite de cierre porque T2b cambió producto.

**Decisiones relevantes.** **D-1** la entrada al proceso es la vista compacta `status`, **en las skills y en el prompt del agente orquestador**, y el state completo es ampliación condicional (causa raíz medida; cubre las dos superficies; el orden estricto no se logra en OpenCode → AC-6 parcial). **D-2** la raíz relativa se unifica en `cdad_packet.py` y el comportamiento C4 de 005-003 queda superseded, con sus **dos oráculos declarados y autorizados** por la fila 11 (uno reemplazado; el otro con el fixture de fallo corregido y su oráculo de captura conservado); la doctrina «cada CLI resuelve su propia raíz» se conserva. **D-3** la vista afirma solo lo verificado: nombra la pata que diverge y su resolución solo si es `project`; la ausencia se distingue de la incoherencia. **D-4** con un paquete `prepared`, la ruta nombra la acción natural (despacharlo) y `--replace-packet` queda como rama condicional, sin cambiar `entry` ni la ruta de `dispatched`. **D-5** fuente única: se referencia, no se copia; sin documento nuevo ni segunda copia.

**Deuda detectada (consolidada en `debt.md`, cada entrada con condición de cierre).** **OP-3** el Step 1 de `cdad-epic` nombra `cdad_packet.py` sin ruta (el reviewer juzgó que **alcanza** por referencia al skill dueño): incluir la invocación o `<skill-dir>` explícitos. **OP-4** cobertura focal parcial de PD-2: `render`, `open-unit`, `validate-metric` y `prepare` no tienen aserción directa con raíz relativa (todos van por la misma rama unificada; riesgo real bajo, no cero): agregar las sondas o declarar por qué el subconjunto basta. **OP-5** fallback no determinista en `_divergent_legs` cuando falta la pata `CLI` (rama hoy inalcanzable): retirarlo o hacerlo determinista. **RD-a — agentes derivados viejos tras un despliegue:** la primera sesión de cada proyecto arranca con el orquestador derivado anterior; el `DRIFT` de la pata `project` lo anuncia, pero **la entrada ya ocurrió** antes del `prepare` que lo resuelve. *Cierre:* que la primera sesión después de un despliegue use el orquestador nuevo (que el despliegue republique los derivados de los proyectos registrados, o que el orquestador no se derive al proyecto). **RD-b — compactación del state:** leerlo completo cuesta 53 mil caracteres por costumbre y el costo lo pone su tamaño (~490 KB, mayormente historia). *Cierre:* que leer el state completo cueste un orden de magnitud menos sin perder la historia (archivada y referenciada); **candidata para el plan**. Se citan además la deuda de la spec §8 (D-1 despliegue —**cumplido** en esta feature—, D-2 hito «primera acción» en el medidor, D-3 adaptador CC) y la **preexistente F011** (D-6), ajena a la feature.

**Lecciones de proceso.** (1) **El texto que manda en un runtime no es siempre el texto común:** corregir las dos `SKILL.md` no llegó a OpenCode porque su entrada real es el prompt del agente derivado; medirlo lo destapó (AC-6 fallido → T2b). (2) **Después de un despliegue, la medición puede estar midiendo el producto viejo:** una corrida de OpenCode no midió T2b porque el agente derivado del proyecto era anterior (RD-a). (3) **Un «first» de más compite con la primera acción prescripta** (OP-2): la prosa vigilada por ventana también es superficie del contrato.

**Estado del epic.** `epic-005-real-operation` sigue en **`features-loop`**: **11/13** unidades cerradas (las filas 1..11). **005-011 queda `done`.** **Siguiente unidad en cola: `005-013-unit-contract`**, en el orden acordado **005-013 → 005-012**, **sin abrir** (`epic_features` con ambas `queued` y `depends_on: 005-011-common-entry`). El **despliegue** sigue siendo del dueño; quedan como pendientes del cierre del epic el **saneamiento antes de publicar** y la segunda mitad de la propuesta «entrada y transiciones»: la **entrada común** ya está entregada por esta feature y el **registro de transiciones** es 005-012.

---

## 2026-10-13 — Feature: 005-004-claude-code-roles (epic 005)

**Cerrada el 2026-10-13 (ciclo técnico completo; el paso b del recorrido queda BLOQUEADO hasta el despliegue del dueño).** Décima feature de epic-005 (tras 005-001, 005-005, 005-006, 005-008, 005-009, 005-010, 005-002, 005-003 y 005-007). Cierra la **fila 10** del plan del epic (`docs/epics/epic-005-real-operation/plan.md:43`): los **roles CDAD quedan activos en Claude Code para este proyecto** por el **mecanismo nativo** —`Agent` con `subagent_type: cdad-<rol>`, subagentes `cdad-*` instalados— y **un ciclo corto real despachado desde una sesión nueva de Claude Code, con la versión instalada al empezar, se recibe por el flujo CDAD** (I8 `runtime: claude-code` → rol nativo → `receive` → `reconcile`). **Sin infraestructura nueva:** se reusan paquete, I8, `receive`, `materialize`, `reconcile` y la vista compacta; el **adaptador Claude Code** (enfoque A), la **activación de proyecto CC**, el **registro automático de transiciones** y la **medición de contexto del lado CC** quedan **fuera** (incremento nombrado y deudas, spec §7/§8). Decisión registrada en **ADR-026**.

**Contrato y plan re-aprobados, con las dos enmiendas del orquestador Claude (2026-10-13).** `spec.md` sha256 `5e11f2ef…` y `plan.md` sha256 `953e4ba5…`; los aprobó el **orquestador OpenCode** bajo la HITL delegada del epic-005. Enmiendas: **(1)** el **alcance del focal de T4** se acota a lo que la cobertura existente no tenía (rol desconocido con fail-open, roles sin hooks y paridad del frontmatter de hooks con `CC_GUARDS`), referenciando lo ya cubierto por `tests/test_004_002_t5_runtime.py` y `tests/test_005_008_t1_nested_tests.py`; **(2)** el **coordinador del recorrido es una sesión nueva de Claude Code** (sin el contexto del orquestador Claude; éste la lanza, mide y revisa) y el gate se parte en **paso a** (versión instalada al empezar, pata CC corrida desde el artefacto del repo en el commit de cierre) y **paso b** (confirmación con el CLI instalado tras el despliegue del dueño, no gate).

**Producto (T1..T4 + focales; diff acotado a 6 archivos, `review.md` V6).**

- **T1 — la herramienta de despacho declarada es la real (`Agent`).** El derivado `agents/claude-code/cdad-orchestrator.md` declaraba `Task`; pasa a declarar `Agent`, declarado **una vez** en el generador (`scripts/cdad-generate.py`, `cc_tools`) y enunciado por el adaptador fuente; `tests/validate-consistency.sh` gana una aserción que falla si algún agente CC declara `Task`. El lado **OpenCode conserva** su nombre. (RED `34703b6` / GREEN `cc6e5a5`.)
- **T2 — el enunciado del instalador se corrige, no el instalador.** Se elimina la afirmación falsa del `strip` (en el adaptador y en el comentario del generador) y se enuncia el mecanismo real: el instalador **despliega los bytes staged sin transformarlos** (`cp -p`; `install.sh:388-396`) y la ausencia de la línea `model:` bajo `basic` la produce el **generador**. Además declara la **procedencia de modelo bajo `basic`** (modelo por llamada en el despacho crítico; exención **explícita** de la invariante reviewer≠implementer, por referencia a ADR-007 y `scripts/validate-subagents.sh`). (RED `0964694` / GREEN `96786de`.)
- **T3 — pata Claude Code aditiva del chequeo de versión.** `skills/cdad-cycle/scripts/cdad-version-check.py` lee el marcador de la raíz de instalación detrás de los agentes CC (registro de activación si existe; si no, el directorio global del runtime), **participa en el veredicto solo cuando una instalación CC es detectable**, nunca cruza una frontera de instalación ni lee el manifiesto de OpenCode, **no altera los cuatro veredictos ni el `rc`** existentes, y una marca faltante es `unknown` **con causa**. `references/project-start.md` §10 lo referencia. **Cierra la deuda D-3 de 005-007** en su parte de comprobación. (RED `4828c0c` / GREEN `b05c5c1`.)
- **T4 — mapa de hooks declarado una vez y decisiones del guard verificables sin sesión viva.** El mapa por rol vive en su dueño (adaptador fuente + `CC_GUARDS` del generador) y el consumidor `claude-code-delegation.md` lo **referencia** (se retiran los globs legacy `src/**`/`lib/**` como mecanismo vigente: el guard v2 clasifica con la política del proyecto, acota `Grep`/`Glob` y **falla cerrado** sin clasificador). El focal **ejecuta** el guard con cargas PreToolUse sintéticas sobre un proyecto fixture: rol desconocido → **fail-open**, roles sin hooks → sin barrera de ruta, y paridad del frontmatter de hooks con `CC_GUARDS`. **Declarado:** verifica las **decisiones del guard**, no que Claude Code honre `exit 2` ni que los hooks del frontmatter se apliquen a subagentes nativos (VERIFY conservados, PD-8). Sin hook `Bash`. (RED `0cdec77` / GREEN `65a0de9`.)

**Recorrido real T5 — paso a APROBADO; paso b BLOQUEADO** (`t5-acceptance.md`). Coordinador: **sesión nueva de Claude Code** con la skill `cdad-cycle` y los agentes `cdad-*` de la instalación global, `--project-root` explícito, HEAD `6afa238`. Once pasos: orientación con la **vista compacta**; veredicto de versión del CLI instalado (`9d89a4b8…`, COHERENT rc 0) y **con la pata CC** desde el artefacto del repo (COHERENT rc 0); registro **I8** con `runtime: claude-code`, `model_configured: sonnet`, `model_reported: null` **con causa** en `provenance`; despacho **nativo** con la herramienta **`Agent`**, `subagent_type: cdad-reviewer`, `model: sonnet`; señal durable del rol en el transcript sidechain (identidad `cdad-reviewer` **sin** fallback a un agente genérico); **recepción** con `receive` (parte `review`, 2223 bytes, sha256 `d5b5f1d0…`, extraída **byte a byte** del transcript) con `identity_validation`/`packet_validation: passed` y **`semantic_status: pending`** (`validate-receipt` → `VALID`); **re-entry** `reconcile` (`received`, `repeat_effect: false`, contrato `unchanged`); **transición del state** por el coordinador (**escritor único**), a mano. **Gate:** el orquestador Claude, con la HITL delegada por el dueño, **aprobó el paso a** y declaró el **paso b BLOQUEADO** hasta el despliegue. El oráculo del paquete **rechazó** el ítem (2) como error de contenido del rol (informó `PD-1..PD-13`; la spec define `PD-1..PD-11`), sin reintento y **sin presentarlo como verde**. **Medición declarada** (conteo propio del orquestador Claude sobre el transcript; no comparable con OpenCode porque no hay adaptador CC del medidor): 47 llamadas, primer `Agent` en la llamada 23, 105 mil caracteres de salida antes del despacho, 8,7 minutos y costo informado por el harness de 3,88 USD.

**Review formal (etapa 4) — 0 bloqueantes / 3 opcionales / 2 abstenciones** (`review.md` §4). Reviewer `glm-5.3-flash` (mofgw), **familia distinta** a la del implementer (`deepseek-v4.1-flash`), sesión independiente y solo lectura; alcance T1..T4 (T5 fuera). Verificaciones propias: focales **29 passed**; validador del repo **154 PASS / 2 FAIL** con los 2 FAIL **preexistentes y delta 0** probados en un árbol pre-feature; los 4 GREEN **sin tocar `tests/`**; focales **no relajados** (un solo commit RED por foco; diff RED→HEAD solo agregados); diff de producto acotado a **6 archivos**; barrido de `strip` sin afirmaciones ligadas al instalador; `make agents` **byte-idéntico** a una regeneración fresca y 0/12 archivos CC con `model:` bajo `basic`; regresiones re-corridas. Los **tres encargos del orquestador** quedaron: adjudicación del mapa de hooks **correcta** (el focal sujeta el drift en ambas direcciones), `git stash` sobre el árbol compartido **opcional de proceso** y observación de la pata CC **opcional de deuda**. Abstenciones: PD-6..PD-11/AC-6..AC-8 (fuera del alcance del paquete) y `exit 2` en modo no interactivo (conservado `unknown`).

**Suite de cierre (una vez, por quien cierra)** — `closure-suite.md`. Worktree fijado a `c8ab21f` con `make staging PROFILE=basic`: **915 passed, 2 failed, 4 skipped** (17 min). **(1)** una **regresión real de T4** (`test_005_009_t3_spawn_reconciliation.py::test_inv8_…[claude-code-delegation]`: el texto reformateado dejó la negación de INV-8 en otra línea y ese oráculo trabaja línea por línea; las regresiones declaradas de T4 no incluían ese módulo), **corregida en `5d6f667`** con un cambio de una línea de documentación, sin tocar el test; **(2)** un **error del lanzador** (staging con `PROFILE=basic` en vez del perfil por defecto), **no del producto**. **Verificación en `5d6f667`**: los 4 focales + los dos módulos → **55 passed**; **`make validate` 155 PASS / 1 FAIL** (F011 preexistente). El resto de la suite por **equivalencia** (`references/re-entry.md`, *Equivalence of a registered run*).

**Decisiones relevantes.** **D-1** el cuerpo es el mecanismo nativo (enfoque B): reusa paquete/I8/`receive`/`materialize`/`reconcile`; el **adaptador CC** queda incremento nombrado con sus deltas a verificar y **fallar cerrado**. **D-2** la herramienta de despacho real es `Agent` (corrección de texto y verificación, no de arquitectura; ADR-008 ya registra Claude Code como segundo runtime). **D-3** se corrige el enunciado del instalador, no el instalador; verificación en **raíz aislada** (`CDAD_INSTALL_ROOT`, nunca HOME). **D-4** la pata CC es **aditiva y declarada**; comparte el marcador de la raíz con las patas de OpenCode (deuda RD-3). **D-5** el mapa de hooks se declara en su dueño y se verifica **ejecutando el guard** sin sesión viva; el dato queda en dos superficies máster **test-cerradas** (deuda RD-1). **D-6** bajo `basic` no hay modelo por rol: se declara por despacho y la exención de la invariante es explícita y visible (nunca presentada como satisfecha). **D-7** el recorrido corre desde un directorio ya confiable con `--project-root`; la confianza de carpeta de este proyecto queda **reservada al dueño**.

**Bloqueo declarado (lo que NO se puede afirmar).** El **paso b de PD-6** requiere el **despliegue del dueño** → **BLOQUEO con responsable (dueño)**, no verde por proximidad. Los **cuatro cruces reservados** quedan declarados **BLOQUEO** y **no ejecutados**: confiar la carpeta de este proyecto, copias viejas/despliegue en HOME, emitir la activación de proyecto para CC, activar versiones en el repo real. **Cuatro desconocidos conservados `unknown` con causa** (PD-8): si Claude Code honra `exit 2` de un hook en modo no interactivo; si los hooks del frontmatter se aplican a los subagentes nativos; qué modelo hereda un subagente sin `model:`; y la medición de contexto por rol del lado CC (no hay adaptador CC del medidor). La **frontera de HOME** se cubrió con tres coberturas declaradas por separado: 107 archivos comparados **idénticos** (digest `9cfa2717…`, excluye `__pycache__`); marcador de versión y manifiesto de propiedad por **mtime anterior** al inicio; y un barrido por mtime que expone, además de dos archivos de sincronización del harness (ajenos a CDAD), un **`.pyc` de `__pycache__`** de la skill instalada (F-4: caché del intérprete, pero **escritura en HOME declarada**). El harness escribe los transcripts bajo `<home>/.claude/projects/` (de ahí sale la evidencia): no son escrituras del coordinador, pero se declaran. La confianza de carpeta está **ausente** antes y después.

**Fricciones declaradas — el recorrido NO es de intervención cero** (`t5-acceptance.md` §5): **F-1** el state de partida tenía un cambio sin commitear que devolvía el paquete del reviewer a `prepared` (el coordinador lo tomó como preparación del lanzador y no lo revirtió); **F-2** buzón, copia byte a byte y descriptor `staged-file` **a mano**; **F-3** la pata CC desde el checkout necesita `--install-root`; **F-4** el `.pyc` en la skill instalada; **F-5** PD-10 nombra `role-report` pero para el reviewer la tabla cerrada admite `review`; **F-6** la transición del state, a mano (no hay CLI que la registre); **F-7** el paquete viaja **tipeado en el prompt de `Agent`** y pierde el salto de línea final.

**Deuda (consolidada en `debt.md`, con condición de cierre).** **RD-1** el mapa de hooks en dos superficies máster (tensión con PD-9, drift test-cerrado; cerrar con enmienda de contrato). **RD-2** `git stash` sobre el árbol compartido dos veces, prohibido por el plan §7, sin efecto material (cerrar exigiendo worktree/nunca-stash; el GREEN de T4 ya usó el patrón correcto). **RD-3** la pata CC comparte el marcador de la raíz y no detecta agentes CC con otra versión dentro de una misma raíz (cerrar con el manifiesto de propiedad o el paso b). **RD-4** la rama del registro de activación de la pata CC no la atrapa ningún focal congelado. **RD-5** el barrido de enunciados de T2 no cubre `scripts/`. **RD-6** el adaptador dice «references this map» cuando la emisión es directa desde `CC_GUARDS`. **Fricciones F-3/F-5/F-7** de T5 y la **deuda de proceso de `closure-suite.md`** (las regresiones de una tarea que edita un reference deben incluir los oráculos de texto que lo cubren; el procedimiento de la suite de cierre debe fijar el perfil de staging). Se citan además la deuda de la spec §8 D-1..D-7 (D-2 → unidad 005-012) y la **preexistente F011** (D-6), con delta 0 probado.

**Lecciones de proceso.** (1) La suite de cierre ve lo que las regresiones declaradas no incluían (la regresión real de T4 la destapó la suite, no las regresiones de T4). (2) El `git stash` sobre el árbol compartido reincidió: es deuda de proceso, no de producto. (3) Cuando el transporte del paquete es el prompt tipeado, su integridad depende del coordinador y la recepción no es de intervención cero (F-7/F-2, deuda D-10 → 005-012).

**Estado del epic.** `epic-005-real-operation` sigue en **`features-loop`**: **10/13** unidades cerradas (las filas 1..10). Restan `005-011-common-entry`, `005-013-unit-contract` y `005-012-transition-registration` (las dos últimas `depends_on: 005-011`), **en cola y sin abrir**. Orden de ejecución acordado: **005-011 → 005-013 → 005-012**. El **despliegue** (paso b, copias/despliegue en HOME, activar versiones en el repo real) sigue siendo del dueño.

---

## 2026-10-13 — Feature: 005-007-progressive-planning (epic 005)

**Cerrada el 2026-10-13 (ciclo técnico completo; la aceptación de uso con la versión desplegada queda en BLOQUEO declarado, del dueño).** Novena feature de epic-005 (tras 005-001, 005-005, 005-006, 005-008, 005-009, 005-010, 005-002 y 005-003). Transforma un objetivo amplio (una fila del plan del epic) en **el próximo trabajo ejecutable con contexto suficiente**, sin inflar el contexto ni fragmentar el avance: **planificación progresiva** con detalle solo de la próxima tanda, **tamaño de unidad por costo total**, **plantillas** que acompañan (spec desde el recorrido de uso; aceptación = comportamiento) y un **vínculo reintentos↔unidad**. Tres deltas del dueño entran como alcance: (1) **abrir la unidad siguiente por el CLI** sin editar el state a mano; (2) **materializar el informe del architect** por el camino legítimo; (3) que el **medidor** reconozca como despacho la interfaz común de delegación.

**Producto (documental + código acotado).**

- **Regla de detalle progresivo** con hogar canónico único `skills/cdad-cycle/references/stage-2-specification.md` (subsección «Progressive detail»): para TODAS las unidades, objetivo y dependencias completos; el detalle (contrato/firmas/pruebas) solo de la tanda próxima; marcador por tarea **`detail`** con conjunto cerrado `"next"` (default) / `"planned"`; una tarea `"planned"` declara `objective`, `depends_on`, `uncertainty`, `owner`, `resolves_when` y **no** declara plan de validación por tarea. El **formato** del campo se declara una sola vez en `planning-contract-draft.md` §4.1 (por referencia); el consumidor `reviewer-plan-review.md` lo consume por referencia. (T1, `7ff19c1`.)
- **Reconciliación del validador** `skills/cdad-cycle/scripts/cdad_packet.py` (`_check_plan_validation_plan`): trata la tarea `"planned"` por sus campos propios y exige el plan de validación solo a `"next"`/sin marcador, sin debilitar el fail-closed ni los checks mecánicos; un `detail` fuera del conjunto cierra. (T2, `09567cd`.)
- **`open-unit`** (subcomando nuevo de `cdad_packet.py`): abre la primera `queued` (o `--feature <ID>`) con escritura atómica y bajo el mismo lock; escribe `active_feature`, `in-progress`+`opened_at` y `current_stage`; reusa `_bootstrap_v2_execution`; la ruta `next-unit` de `status` la nombra; `project-start.md` §6 la documenta por referencia. (T3, `54eeed6`.)
- **Materialización legítima del informe del architect** `skills/cdad-cycle/scripts/cdad_result.py` + `assets/artifact-policy.json`: la tabla cerrada admite el kind `role-report` de la interfaz (y el del informe del architect), conservando la clausura del eje rol y el binding de autorización; el informe de discovery se materializa vía `receive`+`materialize` con sha idéntico y sin `cp`. (T4, `512d913`.)
- **Detección de despacho por el medidor** `skills/cdad-cycle/scripts/cdad_context_meter.py` + `references/context-meter.md`: reconoce como despacho una llamada `shell` que invoca **realmente** `cdad_delegate.py` (misma clase de hecho material que la regla de `resume`), excluye ayuda y meras menciones, y declara el método. (T5, `8ac41d6`.)
- **Plantillas**: `assets/spec-template/spec.md` abre por el recorrido de uso y su aceptación es comportamiento (sin «Line coverage ≥ X%»); `assets/feature-plan-template.md` (nuevo) con ficha + bloque `plan-tasks` como consumidor del formato. (T6, `594da73`.)
- **Tamaño de unidad por costo total** (`stage-2-specification.md`, «Task size»: cuatro condiciones cualitativas, sin números) y **vínculo reintentos↔unidad** (`re-entry.md`, fuente única: un reintento sin información nueva dispara replanteo de la unidad; el número de intentos es señal, no criterio). (T7, `a59101d`.)

**Aceptación y gates (evidencia verificada por el orquestador).**

- **RED→GREEN por unidad** (T1..T7) con commit `test:` y `feat:` por unidad y regresión proporcional; **7 oráculos, 37 passed** al cerrar T7 (re-corrido por el reviewer: 37 passed in 22.11s). (T8, `acceptance.md` §1.)
- **Gate T8** declarado **BLOQUEO PARCIAL**: lo verificable en el repo está verde; la medición con la **versión desplegada** es del dueño (ver Bloqueo).
- **Suite completa** corrida una vez en worktree fijado a `a5cd0c8`: **4 failed, 871 passed, 9 skipped, 6 errors** — **IDÉNTICOS** al commit base `99e2f2e` (familia F011/instalados, preexistentes, no regresiones). `make validate` **141 PASS / 2 FAIL** (F011 preexistente).
- **Review formal (etapa 4):** **2 blocking / 4 optional / 2 abstenciones**, reviewer de familia distinta (`glm-5.3-flash`) a la del implementer (`deepseek-v4.1-flash`); verificó los focales (37 passed) y la igualdad base↔HEAD de los fallos de la suite.
- **Bloqueantes del review-fix:** **B1** (la tarea `planned` sin `depends_on` pasaba el validador) y **B2** (falso negativo del medidor ante invocaciones envueltas por prefijos `time`/`env`/`nohup`/…) **CORREGIDOS YA** (commits `282c70a` y `a86278e`; 24 passed + el oráculo de review-fix 2 passed). Los **4 optional y las 2 abstenciones → a deuda** (`debt.md` D-2..D-8 y las O*).
- **Incidente declarado del RED de review-fix:** el primer despacho (intento 1) no volvió dentro de la cota (1800s) — **sin entrega y sin efectos en el árbol**; se reintentó (test-writer en sesión aislada, commit `2cd13a6`). (Estado: `reviewfix-red-incident`.)
- **Tres defectos de oráculo** detectados por el gate del orquestador (no de la implementación): fixture de T2 que no omitía el campo; helper de T5 que recibía el documento en vez de la sesión; y la bandera `--delegation-dispatch` que el oráculo fija y la spec no nombra literalmente. El implementer **no commiteó un GREEN no validado**; se resolvió con testfix + fix-loop (par RED/GREEN verificado en worktree fijado al HEAD sin la implementación).

**Bloqueo declarado (lo que NO se puede afirmar).** La **medición like-for-like con la versión desplegada en una sesión nueva** (PD-11/AC-7) requiere **desplegar** (acción reservada al dueño) → **BLOQUEO declarado**, no verde por proximidad. En la traza real de esta sesión el medidor reportó `first_dispatch: absent` **con causa**, pero el despacho **existió** (ledger `dispatches/delegate-opencode-2ac2addcb404.json`) envuelto en un prefijo → **falso negativo** (deuda D-2). La confirmación del consumidor (usar la mejora en el arranque de la próxima unidad) también depende del despliegue.

**Deuda declarada (con condición de cierre) — `debt.md` D-1..D-8.** D-1 medición con la versión desplegada (BLOQUEO, del dueño); D-2 detección de despacho con prefijos de envoltura; D-3 el cierre de unidad sigue siendo manual (simetría de `open-unit`); D-4 un draft del architect llega como UNA parte (`role-report`), no como `spec.md`+`plan.md`; D-5 refuerzo por ledger; D-6 formato como asset `plan-tasks.schema.json`; D-7 VERIFY 6/7 heredados; D-8 los tres defectos de oráculo. **Preexistente, no de esta feature:** `make validate` 141/2 (F011) y la suite 871/9/4+6 idéntica al base.

**Contradicción de contrato declarada (anotada para el cierre del epic).** PD-1 («toda tarea declara siempre objective y depends_on») vs PD-2/INV-5 («sin marcador idéntico a hoy»): el review-fix de B1 se acotó al camino `planned` **sin cambiar el contrato aprobado**; queda como observación de redacción de PD-1 para el cierre del epic.

**Commits del ciclo (rango `99e2f2e..92ddd06`).** Etapa 2: `e1b792a` (spec+plan), `9116675` (revisión entre tramos). T1 `16a89ad`/`7ff19c1`; T2 `07abeb2`/`09567cd` (testfix `7d683c9`); T3 `47cd7cc`/`54eeed6`; T4 `852d3be`/`512d913`; T5 `b3044b1`/`8ac41d6` (testfix `c8e766d`); T6 `95516ef`/`594da73`; T7 `4462a9a`/`a59101d`; T8 `c328180`; review `98b3b6a`; review-fix RED `2cd13a6` (incidente `2e3d33e`), GREEN B2 `a86278e`, testfix B1 `e3375e4`, B1 fix `282c70a`, registro `92ddd06`. Contrato: `spec.md` sha256 `54877103…`; `plan.md` `1f636260…`.

**Próxima feature en la cola:** `005-004-claude-code-roles` (epic-005); el epic-005 sigue en `features-loop` (9/10 features cerradas). La **medición desplegada** (D-1) y el **despliegue** siguen siendo del dueño.

## 2026-10-12 — Feature: 005-003-orientation-reduction (epic 005)

**Cerrada el 2026-10-12 (ciclo técnico completo).** Octava feature de epic-005 (tras 005-001,
005-005, 005-006, 005-008, 005-009, 005-010 y 005-002). Entrega **orientación acotada al primer
despacho legítimo**: el orquestador llega a la próxima unidad con **contexto chico** y **sin
reconstruir preventivamente** ni la historia del proyecto ni la implementación del CLI,
conservando autoridad, contratos, evidencia y capacidad de orquestar. La mejora se apoya en
**cuatro piezas generadas por código desde fuentes existentes** (vista compacta; selección
explícita de entrada; interfaz operativa con ejemplos que se ejecutan; disposición de
versión/medidor + resumen del conjunto) **más** dos elementos que la **fila 8 enmendada** del
plan del epic asignó a esta feature (contrato aplicable del encargo; cierre de D11 y R4 dentro de
la feature).

**Estado del gate de aceptación: PARCIAL, con bloqueo declarado.** La parte de unidad está
satisfecha y verificada; la **aceptación de uso real** (A1/A2/A6 y la observación de A8/A9)
**requiere desplegar la versión nueva**, acción reservada al dueño y prohibida en el tramo →
**BLOQUEO declarado** (`acceptance.md` §7), **no** fallo ni éxito. No se simula ni se declara
satisfecha por proximidad.

**Producto (5 archivos nuevos/modificados + 5 de tests).**

- `skills/cdad-cycle/scripts/cdad_packet.py` — subcomando **read-only** `status`
  (`compact-view-v1`): proyección determinista del estado operativo; **no** emite `stage_history`;
  límite normativo **16.384 B con fallo cerrado** (sin proyección parcial); `entry` como mapa
  explícito; diagnóstico de la asimetría de raíz relativa en la salida. (T1, +298/−2; T6, +159.)
- `skills/cdad-cycle/references/orientation.md` — referencia operativa corta (patrón de captura
  del `rc` sin enmascarar; operaciones frecuentes con efectos; cita del asset de ejemplos).
  (T1, nuevo, 79 líneas; T2, +75/−9.)
- `skills/cdad-cycle/assets/orientation-examples.json` — asset canónico de **ejemplos
  ejecutables** (`dispatch-record`, `dispatch-record-invalid`, `continuity-update`, `status-view`).
  (T2, nuevo, 75 líneas.)
- `skills/cdad-cycle/references/project-start.md` — §11: el procedimiento de arranque/reentrada
  **consulta primero la vista `status`** y amplía solo ante necesidad concreta, **por referencia**
  (sin copiar la estructura de los dueños). (T2, +19.)
- `skills/cdad-cycle/scripts/cdad_context_meter.py` — bloque aditivo de **resumen del conjunto**
  (`set-summary-v1`) y regla del documento multiplexado; el registro neutral por sesión queda
  **byte-congelado** sin la bandera. (T3, +227/−2.)
- `skills/cdad-cycle/references/context-meter.md` — regla R4 (total ≤ N × límite por sesión;
  límite normativo **por documento de sesión**) y párrafo «la base real **nunca** se escribe».
  (T3, +44/−2.)
- `skills/cdad-cycle/references/capabilities.md` — inventario de capacidades efectivas
  (observada/documentada/no disponible/desconocida) + fallback portable.
  (T4, nuevo, 114 líneas.)
- T6 además: `assets/packet-request.schema.json` (propiedad opcional declarada),
  `packets/common.md` (declaración única de la política de suite),
  `packets/roles/implementer.md` y `packets/substages/implementer-green.md` (corrección de la
  contradicción) y `scripts/cdad_result.py`.
- Tests: `tests/test_005_003_t1_compact_view.py` (11), `…t2_examples_execute.py` (10),
  `…t3_set_summary.py` (9), `…t4_capabilities_inventory.py` (6), `…t6_packet_contract.py` (7);
  **corrección** de D11-3 en `tests/test_005_002_t4_acceptance.py`.

**Sin cambios:** `install.sh`, `agents/`, `sources/`, `build/` (no tocados; `review.md` §1). No se
creó dashboard, scheduler, fuente de estado nueva ni otro bootstrap (INV-3/INV-7).

**Decisiones relevantes (decisión + contexto + razones + trade-offs):**

- **D-1 — Vista compacta = proyección read-only por código; NO migrar el formato del estado.**
  Contexto: el `stage_history` es **304.075 B = 94,8 %** del estado (**320.880 B**; línea base).
  Razón: el coste lo paga el agente que lee el estado a contexto, no el CLI; una proyección lo
  resuelve sin tocar todos los consumidores (`prepare`, `validate-state`, continuidad) ni mover
  bytes fuera del pin del checkpoint. Trade-off: el historial se consulta **selectivamente** por
  referencia; el estado sigue grande en disco.
- **D-2 — Selección de entrada = mapa explícito, no inferencia por `current_stage` ni por
  «inicializar».** Contexto real: hoy `current_stage=discovery` **y** `active_packet.status=prepared`;
  una inferencia ingenua perdería un paquete preparado. Razón: la selección es el producto central;
  se apoya en campos/directorios existentes, **sin campo nuevo** (INV-2). Trade-off: ver deuda **F2**
  (el calificador «estado distinto de `completed`» **no** es implementable con las fuentes declaradas;
  la implementación eligió la aproximación conservadora y se propone al dueño).
- **D-3 — Ejemplos EJECUTABLES localizados por asset canónico, nunca por prosa de Markdown.**
  Razón: la utilidad no se verifica buscando frases. Trade-off: exige un asset adicional mantenido
  por contrato, y una enmienda de oráculo firmada en T2 (el `UPDATE` de continuidad exige además
  `packet_id`/`attempt` de idempotencia).
- **D-4 — Ausencia ≠ incoherencia en el verdicto de versión; «medidor no instalado» = ausencia.**
  Contexto: el medidor de 005-002 **no** está en ninguna instalación; el CLI del repo da `UNKNOWN`.
  Razón: no convertir una ausencia en un `DRIFT` falso. Trade-off: la coincidencia de archivos **no**
  demuestra lo cargado por una sesión abierta (límite declarado).
- **D-5 — El encargo de tarea trae su contrato aplicable, derivado del bloque canónico del plan.**
  `--plan-task <ID>` aditivo + `plan_task` opcional; `## Task validation plan` con valores **iguales**
  a los del bloque `plan-tasks` (provenance); `## Applicable contract` por referencia; **sin**
  `plan_task` el paquete se emite **byte-idéntico**. Razón: no obligar a releer la spec entera.
  Trade-off: **F3** — cambiar un asset de instrucción invalida los paquetes publicados antes del
  cambio (consecuencia inherente al contrato de paquete, declarable).
- **D-6 — La suite completa se declara una sola vez y la corre quien cierra.** Vive en
  `packets/common.md`; los assets de rol/subetapa **referencian** (no copian); se corrigen los dos
  que afirmaban lo contrario. Trade-off: la frase persiste en `references/` (nota F6).

**Aceptación y gates (evidencia).**

- **RED/GREEN por tarea** (focales del repo): T1 11 failed → **11 passed** (regresión del área 131
  passed); T2 10 failed → **10 passed** (testfix firmado entre medio; regresión 005-006 15 passed);
  T3 5 failed/4 passed → **9 passed**; T4 6 failed → **6 passed**; T6 6 failed (+1 ya satisfecho) →
  **7 passed**. Total focales de la feature: **43 passed** (corrida propia del reviewer).
- **Gate de aceptación (INV-8):** **D11** cerrado en T3 en sus cuatro partes — (1) no-escritura
  sobre **base temporal controlada** (`test_d11_1_*`), (2) **concurrencia** con otro escritor activo
  (`test_d11_2_*`), (3) la aserción de `(tamaño, mtime)` de la base **viva** se retiró
  (`tests/test_005_002_t4_acceptance.py`, commit `8b5673d`), (4) la regla «la base real nunca se
  escribe» está declarada. **R4** cerrado: `context-meter.md` declara los **dos elementos**.
- **Uso real observado (parcial, sin desplegar):** la vista `status` sobre el proyecto real emitió
  **1.679 B** (límite 16.384 B), con exactamente las claves declaradas y **sin** `stage_history`;
  `entry=continuity-reconcile`; `version=UNKNOWN` **con causa** (ausencia); estado intacto.
  Contraste: la lectura del estado completo en S-BOOT-04 fue **215.292 caracteres** → dos órdenes de
  magnitud.
- **Observación del proxy de reorientación de rol (A8, tramo completo, NO garantía):** 12 sesiones
  de rol (6 implementer / 6 test-writer); documento de la corrida 96.552 B. En toda sesión de rol
  `previous_*` y `time_to_first_*` salen `unknown` con causa. **11 de 12** sesiones de rol
  commitearon su producto; la excepción (GREEN de T2, primer intento) **bloqueó legítimamente** por
  un oráculo mutuamente insatisfacible, **paró sin tocar tests ni commitear**, y se resolvió con un
  testfix firmado + re-despacho que commiteó.
- **Review formal (etapa 4):** **0 blocking / 6 optional / 7 abstenciones**, reviewer de **familia
  distinta** a la del implementer. Sondas propias: con estado de **12,1 MB** la proyección es
  **byte-idéntica** (el límite **no crece** con el historial); el borde exacto del límite falla
  cerrado sin proyección parcial; el registro neutral del medidor es **byte-idéntico** sin
  `--set-summary`; el resumen del conjunto deja lo no observado como `unknown`/`null` con causa;
  `--replace-packet` con tarea declarada conserva y **re-resuelve** (sonda, sin oráculo de test).
- **Suite completa:** **NO corrida todavía** — se corre **una sola vez al cierre** (la corre quien
  cierra, en un worktree fijado al commit de cierre). `make validate` no se reporta para esta
  feature.

**Deuda priorizada (disposición real).** De la review formal: **F1** (el plan declaraba un focal
inexistente) → **CORREGIDO** (plan alineado a la spec, con nota de reconciliación; el plan cambió de
sha y el state re-registró su pin). **F4** (identificador crudo de sesión en `acceptance.md`) →
**CORREGIDO** (referencia hasheada). **F2** (la selección no aplica el calificador de «trabajo
pendiente» → `entry` falso en reposo con directorios de paquete históricos) → **A DEUDA + PROPUESTO
al dueño** (dos opciones: reconciliar §2.2 declarando la regla implementada, o abrir una fuente de
estado por paquete). **F3** (cambiar un asset de instrucción invalida paquetes publicados antes del
cambio) → **A DEUDA** con condición de cierre (declarar la consecuencia y el camino legítimo en un
reference). **F4-bis** (la cobertura del oráculo de INV-6 escanea solo `capabilities.md`) → **A
DEUDA**. **F5/F6** (notas FYI: verdicto con el `cdad-version-check.py` hermano del CLI; la frase
«the complete suite is the closure gate» persiste en `references/`) → **A DEUDA** (sin defecto
material). **F7** (`--replace-packet` con `plan_task` sin oráculo de test) → **A DEUDA**.

**Bloqueo declarado (lo que NO se puede afirmar):** A1, A2, A6 y la observación de A9 exigen **una
sesión real nueva con la versión nueva cargada** → **pendiente del despliegue** (reservado al dueño).
Las bandas de A1/A7/A9 y el proxy de A8 son **orientación derivada** de la línea base medida, **no**
medidas y **no** umbrales que acepten o rechacen por sí solos. **No** se afirma «sin aumento» de
lecturas de rol.

**Próxima feature en la cola:** `005-007-progressive-planning` (epic-005), luego `005-004-claude-code-roles`;
el epic-005 sigue en `features-loop` (8/10 features cerradas).

## 2026-10-11 — Feature: 005-002-session-context-meter (epic 005)

**Cerrada el 2026-10-11 (ciclo técnico completo).** Séptima feature de epic-005 (tras 005-001,
005-005, 005-006, 005-008, 005-009 y 005-010). Entrega un **formato de medición neutral respecto
del runtime y opcional para la metodología** —distingue **observado / estimado / desconocido**— y
su **primer adaptador**: un lector de **solo lectura** de las sesiones de OpenCode que informa, por
sesión y por rol, tokens, lecturas, llamadas de herramienta y el momento del primer `resume`. **No
es** un motor de evaluación de sesiones, ni un dashboard, ni un scheduler (INV-8/INV-10). El delta
del dueño (2026-10-11) amplió el resultado con **orientación y resultado**: además del volumen de
tokens, expone dos hitos separados (**primer `resume`** y **primer despacho de rol**), las medidas
de orientación y **tres magnitudes** (contexto cargado por paso / procesamiento acumulado / costo),
vinculadas por un **informe de aplicación** referenciado que **no aprueba** nada.

**Producto (nuevo: 4 archivos + 4 de tests).**

- `skills/cdad-cycle/scripts/cdad_context_meter.py` — adaptador canónico: lector SQLite `?mode=ro`,
  detección de esquema por **columnas/tabla requeridas** (la fuente no tiene `schema_version`),
  **fallo cerrado** con diagnóstico que **nombra el faltante y sin números**, registro neutral por
  stdout, hitos separados, corte con borde fijado, medidas de orientación, tres magnitudes,
  anotación de aplicación referenciada, familias sin doble conteo y privacidad.
- `scripts/cdad_context_meter.py` — **wrapper fino** (`runpy.run_path`), convención del repo.
- `skills/cdad-cycle/assets/context-meter.schema.json` — contrato neutral `context-meter-v1`
  (draft 2020-12): cubos y regla de asignación, claves requeridas y obligatoriedades.
- `skills/cdad-cycle/references/context-meter.md` — procedimiento, semántica de cubos, anotación de
  aplicación, privacidad y **límite normativo de 16384 bytes** por documento de sesión; **no
  enganchado en ningún gate** (medición opcional, PD-13/INV-5).
- `tests/test_005_002_t1_neutral_record.py` … `t4_acceptance.py` — 4 archivos (RED/GREEN por tarea,
  fixtures sintéticos).

**Sin cambios:** los gates, el state, el esquema I8, el CLI de continuidad, el generador,
`install.sh` (el directorio de la skill viaja con `install_skills()`) y `docs/cdad-policy.json`.

**Decisiones relevantes (D1–D12, aprobadas tal como se proponen; decisión + contexto + razones +
trade-offs):**

- **D1 — El registro neutral vive en un schema asset + un reference; no se engancha en gates.** El
  registro es el **contrato**; el adaptador **solo traduce** y es el único que conoce los nombres de
  tablas/columnas del runtime (neutralidad, R6). Razón: la medición es **opcional** (plan fila 7); el
  ciclo sigue aunque el entorno no exponga tokens. Trade-off: el contrato neutral y el adaptador
  evolucionan por separado.
- **D2 — Adaptador canónico `skills/cdad-cycle/scripts/` + wrapper fino `scripts/` (`runpy`).** Razón:
  convención verificada del repo; `install_skills()` despliega el directorio completo sin cambio de
  instalador. Trade-off: dos rutas a mantener coherentes (el wrapper solo resuelve y ejecuta el
  canónico).
- **D3 — Fallo cerrado por columnas/tabla requeridas (no hay marcador de versión).** Contexto: la
  deriva de esquema **ya ocurrió** y un lector que asuma una forma fija se rompe en silencio. Razón:
  el esquema del store **no es contrato público**. Trade-off: se nombra el esquema/columna faltante
  en vez de adaptarse a variantes.
- **D4 — Corte explícito con el borde fijado.** La ventana es el **primer tramo contiguo** cortado en
  la primera brecha > `--idle-threshold` (default `60` min); el «último paso» es el mensaje
  `assistant` que **cierra** el tramo (sin llamada de herramienta propia); las métricas son **por
  tramo, sin promediar**. Razón: la muestra 1 fue continuada (~66,4 h) y la elección del borde
  **cambia el número** (12,55 vs 12,40 min); el borde alternativo se declara **NO usado**.
- **D5 — Detección de hitos.** `resume` = `shell` que invoca el subcomando `resume` del CLI de
  continuidad, **excluyendo** ayuda (`--help`/`-h`); `dispatch` = primer evento de despacho de rol
  observable (herramienta que abre sesión worker, p. ej. `subagent`); ausente → `unknown`, nunca
  inventado. Un despacho **no** prueba utilidad ni resultado aceptado (INV-9).
- **D6 — Tres magnitudes con unidad/procedencia.** Contexto cargado por paso = **proxy declarado**
  (`input + cache.read + cache.write`, marcado `estimated`; **no** la ventana real); procesamiento
  acumulado (suma de pasos, `observed`); costo (`observed` o `unknown`).
- **D7 — Desconocido ≠ cero.** Un valor nulo/ausente/no reportado (p. ej. `cache_write`, que el
  proveedor no reporta) es `unknown` con causa, **nunca** `0` ni «gratuito»; el input reportado **no**
  se equipara con consumo facturado ni con capacidad máxima (extiende `cdad_continuity.py:29-31`).
- **D8 — Informe de aplicación = anotación referenciada.** Forma fijada `{ ref (referencia durable,
  no copia), limit ∈ {accepted, blocked, pending, unknown} desde hechos observables, basis }`; el
  lector **nunca** aprueba; declara sesiones incluidas y relaciones; sin doble conteo
  coordinador+workers; enlaces no verificables `unknown`.
- **D9 — Privacidad.** Omitir/hashear rutas e identificadores; nunca prompts crudos ni salidas de
  herramientas; resolver ids reales en registros locales y **no** copiarlos a contratos publicables
  (sin rutas del host, ruta del store, proveedor, modelo ni identificadores de sesión).
- **D10 — Salida:** `?mode=ro`, acotada por sesión/ventana, **solo stdlib**, JSON único, determinista
  (byte-idéntica); nunca checkpoint-ea el store.
- **D11 — Superficie de invocación mínima.** `--store`/`--session`/`--limit`/`--idle-threshold`/
  `--json`; JSON por stdout; `rc != 0` con diagnóstico por stderr en fallo cerrado; sin store ni
  variable de entorno, el diagnóstico **nombra el insumo faltante**; ninguna ruta hardcodeada.
- **D12 — Claves requeridas del registro neutral** (`milestones`/`measures`/`buckets`) con
  obligatoriedades y **regla de cubos** (una métrica en **exactamente uno** de
  `observed`/`estimated`/`unknown`).

**Aceptación y gates (evidencia verificada por el orquestador).**

- **RED/GREEN por tarea:** T1 RED **7 failed / 0 passed** (todas AssertionError del contrato) → GREEN
  focal **7 passed** + regresiones de los módulos tocados **10 passed**. T2 RED **5 failed / 0
  passed** → GREEN focales T2+T1 **12 passed** (registro validado ad-hoc contra el asset con
  jsonschema, 2 fixtures). T3 RED **5 failed / 2 passed** (los 2 pre-satisfechos por el GREEN de T2,
  declarado por el rol y confirmado por el reviewer) → GREEN tres focales **19 passed**. T4 RED **3
  passed / 2 skipped** (la integración real y S-BOOT-04 omitidas por defecto, con diagnóstico de
  habilitación) → GREEN cuatro focales **22 passed / 2 skipped**.
- **Gate de integración (real, no unitario):** reproducción de las **dos muestras sobre la base real
  en solo lectura** (store + ids por variables de entorno) **1 passed**; **S-BOOT-04** **1 passed**;
  el store queda intacto (aserciones de tamaño/mtime del propio test).
- **Mapeo test↔postcondición:** auditado por una sesión **distinta** de la que escribió los tests
  (el reviewer): sin PD sin test salvo PD-14 (documental, por contrato), sin tests huérfanos, sin
  mocks sobre plumbing ni aserciones sobre nombres internos.
- **Review formal (etapa 4):** **0 blocking · 10 optional · 0 abstenciones**, reviewer de **familia
  distinta** a la del implementer; trajo el diff completo (13 commits, 9 archivos, +5774/−6),
  verificó el pin del contrato y corrió los focales (**22 passed / 2 skipped**). Los 10 hallazgos no
  rompen el camino feliz → `debt.md` con condición de cierre verificable.
- **Suite completa de cierre:** worktree **fijado a `b1a8add`** (último commit que toca producto o
  tests; los posteriores son docs-only) → `make staging` OK (12 + 12 agentes); **787 passed /
  4 skipped, exit 0, 939,85 s**. `make validate`: **142 PASS / 1 FAIL** (F011, drift de las copias
  instaladas en HOME; ver deuda).

**Defecto detectado durante el ciclo (gate de integración).** El gate de integración encontró que los
tests de T2/T4 pineaban `total_output` del tramo en **51.243**, que es el **`max_output`** (lo único
que la spec pinea). El orquestador verificó con sonda propia read-only que el tramo real tiene total
**317.170** y máximo **51.243**; la corrección volvió al test-writer (`49d27ad`) y el fixture pasó a
ser fiel (**100 de 101** llamadas con salida; la #1 vacía es métricamente equivalente). **No se
relajó ningún gate ni se tocó la spec aprobada.** Es la misma lección de 005-010: lo que ningún
fixture ve lo ve la corrida real.

**Incidente de orquestador (transporte).** El descriptor del review se armó con el `artifact_kind`
equivocado (`reviewer-report` en lugar de `review`); `receive` lo aceptó y `materialize` lo rechazó.
Se conservó copia del recibo/bundle inválidos en `.cdad/local/incident-review-kind/`, se re-recibió
el **mismo** texto final del rol (digest verificado **idéntico**) con el kind correcto y se
materializó. **Sin cambio en los bytes del rol.**

**Commits** (rango `7be52d4..HEAD`): T1 RED `dc6b454`, T1 GREEN `eac25ac`; T2 RED `c192c2d`, T2 GREEN
`b153cb3`; T3 RED `9cc1c40`, T3 GREEN `fd58199`; T4 RED `2884f67`; corrección de tests `49d27ad`;
PD-14 en el reference `1dc4e9c`; cierre `c50d8f3`; review `b1a8add` (más los commits de registro del
orquestador). Contrato: `spec.md` sha256 `a70f6d50…`; `plan.md` `d373fc4f…`.

**Deuda detectada (priorizada en `debt.md`).** Los 10 hallazgos OPTIONAL de la review, con condición
de cierre verificable. **D1** (producto, el primero): el `time_relative: 0.0` **fabricado** cuando el
tiempo del hito no es observable (viola el invariante «desconocido ≠ cero» en un caso de borde
válido; cierre: emitir `unknown` con causa + test). Luego D2 (el límite de 16384 bytes no está
**garantizado** por la implementación más allá de las muestras), D3 (`len(input_per_step) == 102`
sobre la base real: oráculo más estricto que el contrato), D4 (el detector de despacho reconoce solo
`subagent`), D5 (`--session` parcialmente casado se mide como subconjunto silencioso), y D6–D10
(proceso/documentación). **Deuda declarada por el contrato:** la sesión de cierre de 005-001 (V6/
PD-14) queda **`unknown` con causa** (ninguna candidata de la ventana cumple el criterio de 13
sesiones hijas; el criterio reproducible queda documentado en el reference); **V3/V11** (ruta exacta
del CLI; campo de ruta de `read` por versión) y **V4** (`resume_attempts`/`time_idle`/`idle_outcome` →
`unknown` con causa) siguen abiertos o declarados. **Sin CI:** el gate es la suite local en el
worktree fijado. **Sin despliegue y sin push:** la activación de la versión en HOME (que resuelve
F011 y habilita el medidor desde la instalación) queda reservada al dueño (el plan del epic la sitúa
entre ciclos).

**Lecciones de proceso.**

1. **El gate de integración ve lo que el fixture no.** El único defecto de producto del ciclo
   (pinneación de `total_output` = `max_output`) lo destapó la corrida sobre la base real; la
   corrección volvió al test-writer sin relajar ningún gate ni tocar la spec.
2. **El `artifact_kind` de un descriptor es parte del contrato de transporte.** `receive` acepta lo
   que `materialize` rechaza: el kind equivocado no pierde bytes (digest idéntico) pero exige
   re-recepción; se conservó la evidencia del incidente en el registro local.
3. **Un rol no cierra su unidad con la suite en segundo plano.** En el GREEN de T2 el implementer
   dejó la suite completa corriendo y terminó su turno; el orquestador mató el proceso huérfano y
   corrió él mismo la suite de cierre en el worktree fijado (patrón ya visto en
   005-006/005-008/005-009/005-010).

**Next feature in queue:** `005-003` (reducción de orientación), que **consume este instrumento** (su
entrada de discovery ya está en el repo; la meta numérica se fija allí con estos datos); luego
`005-007` y `005-004`. El epic-005 sigue en **`features-loop`** (cerradas: 005-001, 005-002,
005-005, 005-006, 005-008, 005-009 y 005-010; restantes: 005-003, 005-007, 005-004). El
**despliegue** de la versión de cierre (que resuelve F011) y la revisión de la **deuda priorizada**
siguen siendo del dueño.

## 2026-10-11 — Feature: 005-010-real-opencode-delegation (epic 005)

**Cerrada el 2026-10-11 (ciclo técnico completo).** Sexta feature de epic-005 y **continuación
correctiva de 005-009**: el adaptador OpenCode de la delegación externa **completa un recorrido
real** en vez de operar solo contra el doble de test. No agrega motor, state ni ledger: reutiliza
la interfaz común, el registro I8, el recibo (`receive`) y la reconciliación, y **no** modifica la
interfaz común (`cdad_delegate.py`), el generador (`cdad-generate.py`) ni la fuente canónica de
agentes (INV-1/INV-2). El cambio vive solo en el adaptador OpenCode, sus tests y dos referencias.

**El defecto que corrige.** Contra el runtime instalado (OpenCode v2.0.26), el adaptador de 005-009
era **inoperable**: (a) bloqueaba todo despacho porque los roles se publican `mode: subagent` y el
adaptador exigía `mode: all`; (b) esperaba una **señal durable que solo escribía el binario falso
del fixture** (un JSON `sessions.json`) y que el runtime real **no produce** —persiste sesiones en
una base SQLite—, y contra esa base lanzaba `UnicodeDecodeError` **no capturado** (ni fallaba
cerrado con diagnóstico); (c) la invocación se acoplaba al servicio de fondo del dueño (sin
`--standalone`), no correlacionaba la sesión (`--session`), no habilitaba permisos no interactivos
(`--auto`) ni registraba el modelo observado.

**Tres hechos verificados del discovery** definen el diseño: la señal durable real es la **base
SQLite** del runtime (`session_v2` + `session_message`), correlacionable sin ambigüedad por
`--session <id>` elegido y legible en **solo lectura**; en la versión instalada
`opencode run --agent <mode:subagent>` **sí** es una entrada no interactiva (la premisa «cuelga»
provenía del binario legacy en PATH); y **stdin** transporta el paquete. La terminación del proceso
y la suficiencia de la entrega siguen siendo hechos distintos: «completado» ≠ «gate aprobado».

**Producto.** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` **+477/−139**: lector de la
base SQLite del runtime en **solo lectura** (`mode=ro`) + correlación por `--session <id>`;
clasificación por `idle_outcome`; modo de carga por la versión instalada + identidad desde la fila
durable; invocación con `--standalone`/`--server`/`--auto`; `PWD` del destino = raíz del proyecto;
observación I8 con `model_reported`/`session` desde la fila durable. **Referencias:**
`references/cli-delegation.md` (+51/−10, contrato de la señal durable y de servidor/permisos) y
`references/opencode-delegation.md` (+44/−17; sección de modo de carga actualizada y **tabla de
modelos obsoleta** reemplazada por el puntero a la única tabla). **Sin cambios:** la interfaz común,
el generador y `sources/agents/adapters/opencode.md` (`git diff` = 0 bytes). **Tests:** el doble
JSON se **reemplaza** por un **SQLite real chico** con el esquema observado y sus variantes
(`tests/test_005_009_t2_opencode_adapter.py` +800/−212; `test_005_009_t4_acceptance.py` +13/−8);
nuevos `test_005_010_t{1,2,3,4}_*.py` (533/505/361/494) + `test_005_010_reviewfix.py` (576).

**Decisiónes (D1–D10, aprobadas tal como se proponen; decisión + contexto + razones + trade-offs):**

- **D1 — Señal durable = store SQLite del runtime, abierto en solo lectura, correlacionado por
  `--session <id>` elegido.** Contexto: la señal de 005-009 era un JSON que solo producía el
  fixture. Razón: superficie material e inequívoca; el `sessions_db` de la config declara la ruta
  (**configurable, nunca hardcodeada**); campo `store` opcional (por defecto `sqlite`). Trade-off:
  el esquema **no es contrato público** → hay que validarlo por columnas y fallar cerrado.
- **D2 — Fallo cerrado por esquema/contenido.** Store ausente/ilegible/no-SQLite/sin
  tablas-columnas esperadas/JSON que no parsea → `blocked` con diagnóstico accionable, sin entrega
  ni recibo; el `UnicodeDecodeError` deja de ser excepción no capturada. Trade-off: se nombra el
  esquema/columna en vez de intentar adaptarse a variantes.
- **D3 — Modo de carga por la versión instalada; sin fallback.** Deja de exigir `mode: all`; exige
  el derivado `cdad-<rol>` publicado y **verifica la identidad desde la fila durable**
  (`session_v2.agent == "cdad-<rol>"`); sin fila o con otro agente → fallo cerrado. `cdad-generate.py`
  no se toca. Razón: alinea con la versión instalada sin cambiar la generación. Trade-off: la
  garantía pasa a ser material (la fila), no declarativa.
- **D4 — Transporte e invocación realmente soportados.** Paquete **byte-idéntico por stdin**;
  `--standalone` por defecto; `--server <url>` por config como alternativa (nunca a la vez);
  `--auto` configurable (activado por defecto) y **documentado como auto-aprobación de permisos
  no-sandbox**. Razón: evita operar el servicio del dueño y habilita permisos no interactivos.
- **D5 — Clasificación desde `idle_outcome`, no desde el `rc`.** `succeeded→completed` (con texto
  final; si falta, `blocked`), `failed→blocked`, `interrupted→cancelled`, sin idle dentro de la
  espera acotada → `timeout`; `completed` es la **única** terminación que persiste entrega; el
  recibo queda `semantic_status: "pending"` (entrega ≠ gate).
- **D6 — Observación I8 del worker desde la fila durable.** `model_reported`/`session` de
  `session_v2.model`/`.id` con provenance; la interfaz **no** cambia (su `model_reported` sigue
  honestamente `null`).
- **D7 — Doble de test fiel.** SQLite real chico con el esquema observado y variantes
  (`succeeded/failed/interrupted/no-idle/unknown-schema/transport-error`); reemplaza al JSON.
- **D8 — Prueba de integración opcional** contra el binario real: marcada y omitida por defecto,
  habilitada por variable de entorno; **lo aislado es CDAD** (instalación y proyecto), el runtime es
  el real con `--standalone` (nunca el servicio de fondo). **Enmienda al aprobar:** el draft pedía
  credencial aislada, pero la credencial vive en la base del runtime; el dueño confirmó («no es
  necesario ni deseable credencial aislada; yo configuro cada agente y luego entre sí se van
  llamando por CLI»).
- **D9 — Aceptación PD-10 en dos pasos** (a: recorrido real aislado orquestado por Claude;
  b: confirmación corta desde la instalación global tras el despliegue del dueño).
- **D10 — Documentación:** `cli-delegation.md` (señal durable real + servidor/permisos) y
  `opencode-delegation.md` (modo de carga; tabla de modelos → puntero a la única tabla), sin valores
  de este VPS.

**Aceptación y review.** 4 tareas (T1 señal durable/correlación/clasificación/observación;
T2 modo de carga e invocación; T3 referencias; T4 integración opcional). El comportamiento se
verifica sobre artefactos durables (base SQLite, argv del binario falso, registro I8, recibo,
terminación). **Aceptación PD-9(a)/PD-10:** recorrido real **Claude → `cdad_delegate.py` →
OpenCode → `receive` → re-entry** desde una **instalación aislada** de `3c9d3ee` sobre un proyecto
temporal: `termination: completed`, recibo `pending`, `reconcile: received`, re-entry `VALID`
(`evidence/pd10-acceptance.md`), repetido con la versión de cierre `3e556a8`. Suite completa de
cierre: **763 passed / 2 skipped** (worktree fijado a `3e556a8`). **Review formal única**, read-only, con **modelo de familia
distinta** a la del implementer: **1 BLOCKING + 6 OPTIONAL**; verificó por sí misma el contrato
(sha256 = pin), los focales y la regresión de 005-009, y que los tests no se debilitaron.

**Defectos detectados durante el ciclo.**

1. **La señal JSON no existía en el runtime real (defecto que ningún fixture podía ver).** El doble
   de 005-009 escribía `sessions.json`, así que la suite determinista validaba un contrato **contra
   sí mismo**. La corrida real mostró que OpenCode persiste en SQLite: se migró el lector (solo
   lectura) y el doble a un SQLite real chico. (Orquestado por T1; confirmado en T4.)
2. **OpenCode toma el directorio del proyecto de `PWD`, no del cwd del proceso (defecto que ningún
   fixture podía ver).** La primera corrida habilitada de T4 ejecutó el rol en el directorio del
   **coordinador**, no en el proyecto temporal: el adaptador heredaba `PWD` (violaba PD-3 de 005-009).
   Se corrigió fijando `PWD` = raíz del proyecto en la invocación (`3c9d3ee`) con test dedicado
   (`TestPd4PwdProjectDirectory`). El rol real se bloqueó por paquete ajeno y no escribió nada.
3. **(Postura del rol) El implementer cerró un turno esperando la suite sin commitear.** En el
   review-fix (GREEN de R1/R2/R4), el implementer terminó su turno con la suite en segundo plano y
   sin commit; el orquestador **commiteó** (`3e556a8`) tras verificar el gate (41 passed / 1 skipped).

**Commits** (base `06d0e98`): T1 RED `bfaa338`, T1 GREEN `86fedb1`, T1 testfix `ae600eb`;
T2 RED `846f079`, T2 GREEN `e268726`, T2 testfix `e6479b5`; T3 RED `9c467d6`, T3 GREEN `15d9f14`;
T4 RED `8b4b518`; T2b RED `fff8b04`, T2b GREEN `3c9d3ee`; aceptación PD-10(a) `ea4b915`; review
`707456e`; review-fix RED `b783044`, GREEN `3e556a8`; T4 testfix `890ece2`/`bc056d7`; registro de la
integración real `49229be`. Contrato: `spec.md` sha256 `baf195a3…891b`; `plan.md` sha256 `4a0d5b2a…9e72`.

**Reapertura por B1 (2026-10-11).** La verificación posterior de Codex encontró que, si el último
mensaje `assistant` no tenía texto, el adaptador tomaba el de un mensaje anterior y clasificaba
`completed` (contra PD-1/PD-5). Corregida: RED `1b62f5d`, GREEN `7a2ed0a` (solo el último
`assistant`, `LIMIT 1`; resuelve también R5). Suite completa 765 passed / 2 skipped; integración
real 1 passed. **Sin desplegar:** el despliegue espera a que el otro proyecto activo esté en reposo. Detalle en
`closure.md` §6.

**Deuda detectada.**

- **R6–R7 de la review** (optativas, sin efecto en el camino feliz): numeración del docstring
  ambigua entre PD de 005-009 y de 005-010; URI SQLite sin **encoding** del path (`?#` rompería el
  parse; input del dueño, riesgo bajo). R5 (`fetchall`) quedó resuelta con B1 (`7a2ed0a`).
- **Resuelto el 2026-10-11:** el paso b de PD-9/PD-10 (`evidence/pd10-acceptance.md` §7) y la
  aprobación de la versión vigente del plan del epic (`fbb0770b…`, registrada en `epic_history` en
  `0eaf045`). **No volver a registrar esa aprobación.**
- **B1 sin desplegar:** la instalación global (`c9f4810`) conserva B1. Solo afecta al adaptador
  de la delegación externa, así que 005-002 no se ve afectada. El despliegue lo decide el dueño
  cuando el otro proyecto activo esté en reposo.
- **Oráculo de T4 dependiente del modelo:** en 4 corridas reales sobre `7a2ed0a`, 2 veces el modelo
  se negó a repetir el token fijo (lo tomó como inyección); la tubería y la entrega funcionaron.
- **F1 (no atribuible):** los 2 FAIL de `make validate` (F011 drift de HOME y A3) son
  preexistentes; verificado que los archivos que matchean **no** están en el diff (falso positivo
  del patrón de A3 sobre prosa, deuda ya documentada del check). Sin CI.
- **Desvío del discovery (menor):** las sondas con `--standalone` usaron el directorio de datos del
  dueño (la instalación aislada pierde la credencial, que vive en la base) y dejaron sesiones de
  prueba en su base; no se tocó su configuración ni su servidor.

**Lecciones de proceso.**

1. **Un doble que fabrica la señal no verifica el contrato del runtime.** El JSON `sessions.json` de
   005-009 lo escribía solo el binario falso: la suite validaba el contrato **contra sí mismo**. Un
   fixture fiel debe reproducir la superficie **observada**, no una inventada.
2. **Lo que ningún fixture puede ver lo ve la corrida real.** La prueba real (PD-9a + T4 habilitada)
   encontró los dos defectos materiales (señal JSON inexistente; proyecto tomado de `PWD`). La
   aceptación real es un gate **aparte**, no un test determinista.
3. **Un rol no cierra su unidad con el gate en segundo plano.** El implementer del review-fix
   terminó el turno esperando la suite sin commitear (patrón ya visto en 005-006/005-008); el
   orquestador verificó y commiteó. La suite de cierre la corre el orquestador.

**Próxima unidad.** Retomar **005-002-session-context-meter** (pausada, discovery intacto; próxima
subetapa `draft`), luego **005-003**, **005-007** y **005-004**. **Bloqueo previo:** registrar la
aprobación de la versión actual del plan del epic (pin `996dd7e0…` desactualizado frente a
`fbb0770b…`). El **paso b** de PD-10 y el **despliegue** siguen siendo del dueño. El epic-005 sigue
en **`features-loop`** (cerradas: 005-001, 005-005, 005-006, 005-008, 005-009 y 005-010).

## 2026-10-11 — Feature: 005-009-cli-delegation (epic 005)

Cerrada el 2026-10-11. Quinta feature de epic-005 (tras 005-001, 005-005, 005-006 y 005-008).
Un agente autorizado (coordinador) puede **encargar un paquete CDAD ya preparado a una sesión de
rol en OTRO CLI** y recibir su entrega por el flujo CDAD existente, con proyecto, rol,
configuración, entrega y re-entry verificables. La pieza nueva es una **interfaz común de
delegación con un adaptador por destino** (el primero, OpenCode), que **reutiliza** `prepare`, el
registro I8, el ledger, los recibos y la reconciliación y **no crea otro state del ciclo**. Primer
recorrido real: **Claude (coordinador) → OpenCode (worker) → recepción CDAD**. No se construyó
scheduler, ni instalación automática de CLI, ni sandbox; no se implementaron todos los destinos
(INV-9).

**Producto.** Nuevos: `skills/cdad-cycle/scripts/cdad_delegate.py` (+298, la interfaz agnóstica del
destino, que resuelve el adaptador por **convención de módulo**), `cdad_delegate_opencode.py`
(+589, el adaptador OpenCode), `scripts/cdad_delegate.py` (+11, wrapper `runpy`) y
`references/cli-delegation.md` (+142, el contrato de la interfaz). Modificados (reconciliación del
SPAWN GUARD): `SKILL.md` (+7), `sources/roles/orchestrator.md` (+6),
`references/claude-code-delegation.md` (+4) y los dos orquestadores generados (+6 c/u,
regenerados por `make agents`, nunca a mano). **Sin cambios:** `prepare`, el esquema cerrado de I8,
`cdad_result.py`, `cdad_continuity.py`, el clasificador, el guard CC y la publicación atómica.
Tests nuevos: `test_005_009_t{1,2,3,4}_*.py`. Producto+tests: 13 archivos, +3956.

**Decisiones (D1–D10).** D1 interfaz común como CLI nuevo con adaptadores por convención de
módulo —agregar un destino **no** edita la interfaz—; D2 reutilizar `prepare`/I8/ledger/`receive`/
`reconcile` sin otro state; D3 alimentar I8 con el esquema cerrado y registrar
configurado/observado/`unknown`; D4 vocabulario de terminación con **entrega ≠ gate**; D5
verificación del modo de carga con **fail-closed** y sin fallback genérico; D6 espera sobre señal
durable, no sobre el `rc`; D7 configuración portable sin valores del VPS; D8 reconciliación del
SPAWN GUARD; D9 el recorrido real como gate de integración; D10 frontera explícita. El detalle
arquitectónico queda en **ADR-023**; el contrato operativo, en `references/cli-delegation.md`.

**Aceptación y review.** T1 (4 tests ↔ PD-1/PD-2/PD-3/PD-8), T2 (6 ↔ PD-4..PD-7), T3 (21 ↔ PD-9 +
INV-1/INV-4/INV-8), T4 (2 + 1 skip ↔ PD-6/PD-10): comportamiento observable sobre artefactos
durables y consistencia estructural (T3). Focales **33 passed / 1 skipped** (el skip es PD-10,
declarado con mensaje explícito, sin verde fabricado). RED genuino confirmado por worktrees en los
commits de RED. Review formal **única**, read-only, con **modelo de familia distinta** a la del
implementer: **OK, sin bloqueantes**; verificó por sí misma la suite completa **734 passed / 1
skipped**, `make validate` 141/2 con los 2 FAIL de familias **preexistentes** (comprobadas en un
worktree sobre la base), paridad de los **22 agentes generados byte-idéntica** a su regeneración,
estabilidad del focal de T2 en 5 corridas, y tests **no debilitados** entre RED y HEAD.

**Defectos detectados durante el ciclo (el valor estuvo en los tres).**

1. **El adaptador resolvía el árbol de la skill desde el directorio del coordinador**
   (`os.environ["PWD"]`). Detectado por el orquestador al verificar el primer GREEN de T2 (el rol lo
   había reportado como nota, no como bloqueante). Riesgo real: en una delegación real podía
   resolver **otra versión** del producto. Se corrigió en dos pasos: la fixture pasó a stagear el
   **árbol completo** de la skill (causa próxima) y el adaptador ahora resuelve todo **co-ubicado al
   artefacto**, fallando cerrado si el árbol está incompleto (`d413c0c`).
2. **Una aserción del test nuevo era insatisfacible:** el mensaje del `assertIsNone` evaluaba
   `hit.group(0)` dentro de un f-string **antes** de la aserción, así que con el arreglo presente
   reventaba con `AttributeError` y sin él fallaba por `AssertionError`. El implementer **se detuvo
   y lo reportó** en vez de forzar el verde; el test-writer la corrigió con **formateo perezoso**
   sin debilitar la garantía (`8f6b812`).
3. **Carrera de tiempos preexistente** (medida: ~10-11 de 40 invocaciones, también en la base): el
   adaptador agotaba su presupuesto interno y la **interfaz** lo mataba por exceder la cota,
   clasificando `timeout` en vez de `transport-error`. Se corrigió **en el producto** —un fallo de
   transporte observable se clasifica desde el hecho material sin agotar el presupuesto, y el
   adaptador responde siempre dentro de la cota que recibe—, **no** subiendo la cota del fixture
   (`15c8dab`).

**Commits** (base `9f11b4f`): T1 `1d5c946`, T3 `896637b`, T2 `b483c05`, review-fix del test
`6fc958d`/`8f6b812`, review-fix del producto `d413c0c`/`15c8dab`, T4 `29c8480`; tests RED
`6d367e8`/`5fd859d`/`aca65c1`; review `1a111ab` + saneo `6f4d5db`; despliegue `a47ed17`. Contrato:
`spec.md` sha256 `bc8777a2…`.

**Despliegue (por instrucción directa del dueño).** Sucesora que incluye 005-008 y 005-009: commit
`6f4d5db`, perfil `basic`, en las tres bases, con respaldo previo en
`archive/20261011-opencode-agents-pre-005-009`. Verificado: `version.txt` y `source_version` del
manifiesto iguales al commit; 343 archivos propios y **0 conflictos**; 11/11 agentes presentes; los
CLI de delegación y la referencia instalados. El único FAIL de `install.sh --check` es la deuda
conocida de `__pycache__`. La familia **F011** que la review atribuía a este diff **quedó cerrada**
con el despliegue; los derivados del proyecto se republicaron con el primer `prepare` legítimo y
`cdad-version-check.py` da **COHERENT**.

**Deuda.** Cinco opcionales de la review (ponderados por efecto real): cota de espera ausente →
invocación sin cota si falta `wait.timeout_seconds` (contra PD-5; cierre: envelope `blocked`
fail-closed + test negativo); falso positivo del barrido A3 en la prosa del fixture de T1 (familia
preexistente, sin fuga real); presupuesto nulo si la cota ≤ reserva de 1 s; «no polling loop» en la
referencia frente al sondeo acotado a 50 ms; `--packet-id` sin validar en el adaptador (la interfaz
sí valida). `install.sh --check` sigue siendo sensible a los `__pycache__`. La estabilidad medida
del focal de T2 depende de la carga del host. El paquete no inyecta fuentes de dominio por encargo.
Preexistentes ajenos: A3 (F011 cerrada por el despliegue). Sin CI. Del dueño: **VERIFY-3** (entry
soportada contra la versión vigente) y **PD-10** (recorrido real).

**Lecciones de proceso.**

1. **Un defecto reportado como «nota» puede ser material.** El primer GREEN de T2 traía la
   resolución por `PWD` como nota; la verificación del orquestador sobre el reporte del rol es lo
   que lo convirtió en corrección.
2. **Un test insatisfacible se corrige sin debilitar la garantía.** El implementer se detuvo ante
   el f-string que reventaba **antes** de la aserción; el test-writer usó formateo perezoso y la
   garantía quedó intacta.
3. **La flakiness se arregla en el producto, no en el fixture.** La carrera `timeout`/
   `transport-error` era preexistente; se corrigió clasificando desde el hecho material y acotando
   la invocación al presupuesto recibido.
4. **Un paquete sin cota degrada un invariante.** La falta de `wait.timeout_seconds` convierte
   «espera acotada» (PD-5) en espera indefinida; queda como deuda con condición de cierre.
5. **La paridad fuente↔generado se verifica por regeneración, no por inspección de prosa.**

**Próxima unidad.** Retomar **005-002-session-context-meter** (pausada, discovery intacto; próxima
subetapa `draft`), luego **005-003**, **005-007** y **005-004**. El **recorrido real** y la
**aceptación conjunta del consumidor** siguen siendo del dueño. El epic-005 sigue en
**`features-loop`** (cerradas: 005-001, 005-005, 005-006, 005-008 y 005-009).

## 2026-10-10 — Feature: 005-008-project-path-capabilities (epic 005)

Cerrada el 2026-10-10. Cuarta feature de epic-005 (tras 005-001, 005-005 y 005-006). No agrega roles,
sub-modos ni contratos nuevos: **alinea las capacidades mediadas por ruta de los agentes con el
clasificador único** para un proyecto cuya política declara una **raíz de tests anidada dentro de una
raíz de implementación** (primer consumidor real: Perl/Webmin, implementación `webmin-module/module/` y
tests en `webmin-module/module/t/`). Producto: `skills/cdad-cycle/scripts/cdad_packet.py` **+19/−2** (3
hunks: `_validate_policy_document`, `_test_patterns`, `_derived_maps` rama `read`), 3 tests nuevos
(T1/T2/T3) y `review.md`; **sin cambios** en el clasificador, el guard CC, el esquema del manifiesto ni la
publicación atómica. Gate: suite completa **700 passed / 1 failed** (falla **preexistente/ambiental**,
`review5_b4`), focales **16/16** (T1 9, T2 2, T3 5), `make validate` **141 PASS / 2 FAIL F011
preexistentes**. Review formal **única** PASS (0 bloqueantes). HOME intacto (`~/version.txt` = `35062b0`,
anterior al ciclo).

**El defecto (reproducido en el discovery §2).** En `_derived_maps`, la rama `read` del `test-writer`
concatenaba el deny de implementación + los allows de tests co-ubicados + `private`, **sin** el allow del
árbol de tests declarado (`_test_patterns`); el `edit` del mismo rol **sí** lo incluía. Con la política
Perl, el test-writer **podía editar** `t/basic.t`/`t/helper.pl` pero **no leerlos** (el `read` resolvía
deny). Además `_test_patterns` **ignoraba `test_files`**: con un `test_files` bajo implementación, el
clasificador lo daba `tests` (`exact("test_files")`) pero los mapas derivados lo **denegaban** (caso focal
PD-5). La clasificación **ya era correcta** (tests > implementación por precedencia) y el guard de Claude
Code **ya era correcto** (bloquea solo si la clase es `implementation`): el defecto era **exclusivo del
mapa OpenCode**.

**Decisiones (D1–D7, aprobadas tal como se proponen).** D1 extender la fuente única de patrones de tests
para incluir `test_files` (no un helper solo-read): mantiene una sola verdad y la paridad
clasificador/`read`/`edit`. D2 orden del mapa `read`: deny de implementación → allow de tests declarados
(+ co-ubicados) → **`private` al final** (findLast: el allow reabre tests y `private` conserva su
precedencia; el orden es *load-bearing*). D3 sin convenciones globales (`**/t/**`, `**/*.t`): solo
árboles/archivos declarados. D4 los comandos del proyecto viven en su lugar canónico
(Makefile/systemPatterns), **nunca** en `docs/cdad-policy.json`. D5 aceptación por comportamiento
observable sobre los derivados publicados (oráculo findLast único reutilizado por import) **más** el
recorrido del producto instalado; la prosa se verifica por review. D6 T1 es el único cambio de producto;
T2 reusa 005-006 sin duplicar el bootstrap; T3 es la aceptación. D7 frontera explícita: no se implementa
el consumidor ni se crean agentes/sistema de políticas paralelo.

**Cambio de producto (3 hunks).** (D1) `_test_patterns` incluye `path_policy["test_files"]` literales;
(D2) la rama `read` del test-writer inserta el allow de `_test_patterns` después del deny de
implementación y antes de `private`; (PD-10b) `_validate_policy_document` **nombra** el campo extra o
faltante (`unknown field(s): X` / `missing field(s): Y`) conservando el fail-closed y el esquema exacto de
tres campos.

**Aceptación y review.** T1 (9 tests ↔ PD-1..PD-9) y T2 (2 tests ↔ PD-10a/b) por comportamiento
observable sobre los derivados publicados (subprocess `prepare` + oráculo findLast reutilizado por import
+ guard CC forma-real como control; sin nombres de funciones internas ni mocks de plumbing). T3 (5 tests ↔
PD-11 + W-2) construye una **instalación aislada** (`install.sh --basic` con `CDAD_INSTALL_ROOT` en un
tempdir) y ejercita el **CLI instalado**. RED genuino verificado por worktrees en los commits de RED (T1:
3 AssertionError de comportamiento; T2: AssertionError del diagnóstico genérico) y tests **byte-idénticos**
entre RED y HEAD. Review formal única PASS, 0 bloqueantes; opcionales O-1/O-2/O-3 y 4 abstenciones.

**Commits.** T1 RED `17d5f9c`, T1 GREEN `17e6184`, T2 RED `aff3a20`, T2 GREEN `8500bf4`, T3 `54fb376`,
review `7928650`. Contrato: `spec.md` sha256 `849c6201…62`.

**Deuda y hallazgos.** O-1 (dueño): el cierre **no** cierra los VERIFY 1/3/5/6 (layout/política reales
del consumidor, mediación viva, dominio, comandos Perl) — pertenecen al dueño y a la aceptación conjunta
con 005-009. O-2: la superficie de T2 no listaba `_validate_policy_document` (errata en `closure.md`
§4.3, sin cambio de código). O-3: `build/staging` (gitignored) quedó con `profile=basic` y mantiene en
rojo 1 test de instalación, fuera del diff. `install.sh --check` sigue siendo sensible a los `__pycache__`
junto al CLI instalado. El paquete no inyecta fuentes de dominio por encargo (VERIFY 5). Preexistentes
ajenos: F011 (drift de mirrors de HOME) y A3 (patrones sensibles). Sin CI.

**Lecciones de proceso.**

1. **El objetivo de un paquete no es un campo libre frente al shell.** El primer paquete de GREEN de T1
   (`-green-001`) perdió las palabras entre backticks porque el shell las interpretó como sustitución de
   comando al construir el comando; se marcó `failed` **sin despacharse** y se preparó `-green-002`.
   `--replace-packet` **no** corrige el objetivo (conserva el encargo anterior y solo admite
   insumos/alcances/invariantes/entrega/evidencia).
2. **Una suite en background no sobrevive entre turnos.** El primer turno del reviewer devolvió control
   con la suite en background y el proceso murió con la sesión (patrón ya visto en 004-001/004-003/005-006);
   se **reanudó la misma sesión** y entregó el informe en primer plano.
3. **Un RED honesto puede ser un LOCK.** T3 no tiene producto nuevo (el plan lo declara); sus tests pasan
   de inmediato contra el producto instalado. Es un lock del recorrido, con el RED de sus postcondiciones
   registrado en T1. No se fabricó ninguna falla.
4. **El plan puede omitir un archivo que el PD exige.** La superficie de T2 no enumeraba
   `_validate_policy_document`, que PD-10(b) —aprobada en el contrato— exige; el cambio implementa
   exactamente la postcondición aprobada y la suite la verifica (errata declarada).
5. **Un worktree limpio no reproduce el entorno de la suite.** Los tests de instalación dependen del build
   de staging (`build/`, gitignored): sin él dan 4F/6E que **no** son regresiones (los mismos 15 tests
   pasan en el árbol con staging). La corrida de cierre exige preparar el entorno en el worktree.

**Próxima unidad.** `005-009-cli-delegation` (epic-005, orden 5) — interfaz común de delegación externa y
primer recorrido real Claude → OpenCode, con rol, proyecto, entrega y re-entry verificables; **depende de
005-008 para la aceptación conjunta del consumidor** (aporta la R2 pendiente de 005-006 y la de
interoperabilidad). Después: `005-002-session-context-meter` (pausada, discovery intacto), `005-003`,
`005-007` y `005-004`. El epic-005 sigue en **`features-loop`** (cerradas: 005-001, 005-005, 005-006 y
005-008).

## 2026-10-10 — Feature: 005-006-guided-project-start (epic 005)

**Cerrada y desplegada el 2026-10-10 por instrucción del dueño** (ver «Cierre y despliegue»). El ciclo técnico quedó completo y,
tras un review-fix del dueño (tres defectos materiales, §8), la versión se desplegó en HOME. La corrida R2 de sesión nueva en el
proyecto de aceptación queda como verificación del dueño: si fallara, la feature se reabre. Tercera feature de epic-005 (tras 005-001 y
005-005). Cierra la fricción del arranque: **una instrucción breve basta para una primera
delegación útil**. Entrega: un **procedimiento corto de arranque**
(`skills/cdad-cycle/references/project-start.md`, referencia nueva) **y** su **entrada en el
intake** del orquestador (camino *boot-at-rest*), más el cableado con el **CLI instalado**, el
**dueño canónico** del reconocimiento y el **responsable de sincronizar `epic_features`**.
**Sin código de producto nuevo:** el enforcement (`cdad_packet.py`) y `prepare` **no** cambian
(lock de T3). Cinco tareas (T1–T5) + un review-fix (F1). Diff `ce67a6e..HEAD`: 16 archivos,
+3243/−39 (producto: 6 archivos + tests + state + review). Gate: suite completa **680 passed /
0 failed** (12m23s, corrida del reviewer), focales **31**; `make validate` **141 PASS / 2 FAIL
F011 preexistentes** (ajenos al diff). Review formal **única** `approved-with-conditions`
(0 bloqueantes).

**Decisiones relevantes** (D1–D8, aprobadas tal como se proponen; decisión + contexto +
razones + trade-offs):

- **D1 — La salida del hueco es referencia nueva + entrada de intake (ambas).** Contexto: la
  referencia sola no se carga por iniciativa propia (fricción 1) y el intake solo, sin
  procedimiento corto, obliga a deducir el arranque (fricción 6). Razón: cubrir las **dos
  direcciones** del contrato (el arnés da un procedimiento corto; el intake ordena cargarlo).
  Trade-off: dos lugares a mantener coherentes (la referencia es el dueño del paso a paso; el
  intake solo la señala).
- **D2 — `resume` no aplica en reposo (solo en la rama de arranque).** Contexto:
  `SKILL.md:244` y `orchestrator.md:86` prescribían `resume` sin matizar, y sin ejecución
  activa no hay checkpoint (fricción 4). Razón: distinguir «arrancar / iniciar la unidad
  siguiente» de «reanudar una ejecución activa». Trade-off: la **reducción** de lecturas y la
  selección fina del camino de continuación quedan en **005-003** (no se tocan aquí).
- **D3 — El cableado usa el CLI instalado, por la procedencia de 005-005.** Contexto: el
  cableado nombraba rutas relativas al proyecto (`scripts/…`, `skills/cdad-cycle/…`), que no
  existen en un consumidor (fricción 2). Razón: operar con el producto instalado
  (`$CDAD_INSTALL_ROOT/…`), reusando la procedencia ya fijada por 005-005 **sin re-declarar su
  precedencia**. Trade-off: el texto pasa a depender de `$CDAD_INSTALL_ROOT` (variable /
  registro de activación).
- **D4 — Dueño canónico del reconocimiento, por objeto.** Feature/Memory-Bank →
  `cdad-cycle/references/state-detection.md`; etapa de epic → `cdad-epic/references/
  state-detection.md`; la **composición de arranque** → `project-start.md` (que **referencia**
  a ambos, no re-declara). Razón: cerrar el VERIFY 1 sin un merge riesgoso de dos archivos que
  detectan **objetos distintos**. Trade-off: tres punteros a mantener; ningún algoritmo se
  duplica.
- **D5 — El responsable de sincronizar `epic_features` es el coordinador de epic.** Contexto:
  `epic-planning.md:130-143` no asignaba responsable y `prepare` exige la entrada en
  `epic_features` (fricción 5: sin sync el arranque falla cerrado). Razón: asignar el dueño
  único ya implícito; el **escritor único del state sigue siendo el orquestador** (INV-3).
  Trade-off: el ciclo no muta el plan del epic por su cuenta; el arranque **encamina** el
  desfase a `cdad-epic` en vez de parchear el state.
- **D6 — `README.md` gana una sección corta de arranque guiado** que remite a
  `project-start.md` (PD-11), sin reproducir el prompt. Razón: `README.md` es el único
  `documentation_file` de la política. Trade-off: puntero, no duplicación.
- **D7 — La aceptación es comportamiento en R1/R2/R3**, con R2 real (proyecto del dueño) y
  R1/R3 por fixtures deterministas; el criterio es **funcional**, no un tope de lecturas.
  Razón: `findings/session-guided-start-friction-2026-10-10.md:188-192`; la **medición** es de
  005-002 (INV-8). Trade-off: R1/R3 no verifican el bootstrap del Memory Bank por fixture (el
  oráculo de R1 se ancla al fin observable que el producto sí garantiza).
- **D8 — Sin plantilla del prompt largo** (PD-15/INV-6). Razón: límite explícito del plan; la
  solución es un procedimiento operativo corto.

**Aceptación y review:**

- **T5 (comportamiento, caja negra, contra el CLI):** R1 (proyecto nuevo → paquete
  **preparado y despachable**), R3(a) (política ausente → cierre con diagnóstico accionable,
  sin publicar), R3(b) (autoridad sin pin → `rc=2 approval pending`, nombra el registro
  contradicho y cómo seguir) y PD-17 (`resume` sin checkpoint → `rc=0`, proyección vacía
  `no-checkpoint`). **4/4 verdes hoy por diseño** (el producto lo entregaron T1–T4; precedente
  003-002 T4): son **locks de regresión anclados a precondiciones verificadas**, no verdes
  vacíos.
- **R2 (arranque real) NO se simula:** es el **gate de integración** orquestador + dueño (ver
  «Condición de cierre»); cierra o deja abierto el **VERIFY 5** del discovery.
- **Review formal única** (`review.md`): **0 bloqueantes** sobre el diff; verifica por sí
  misma la suite completa **680/0**, `make validate` sin fallos nuevos, `git diff` de
  `scripts/` **vacío** (enforcement intacto), `make agents` sin delta (**byte-parity**),
  plan/execution del epic sin tocar, y los RED reales (25 fallos al revertir el producto).
  **F1** (opcional: `SKILL.md:278` con ruta relativa del CLI sin marcar) **cerrado como
  review-fix** (`19d561e` + tests `934527f`; 1 línea + barrido de los Pasos 5–8 de `SKILL.md`).
  **F2/F3/F5** → deuda. **F4** → condiciones de cierre del dueño.

**Versiones y evidencia:**

- Commits de producto: T1 `421ddf2`, T2 `4d96905` (agentes regenerados), T3 `8dd8c09`,
  T4 `fe8d742`, F1 `19d561e`. De tests: `0c7d951`, `91eaaaf` (enmienda de oráculo),
  `b2740a0`, `485503f`, `3c4b2be`, `2b69074`, `934527f`. Cierres/registros: `60850bf`,
  `b73a182`, `505f7cf`, `5d71f45`, `93104bf`, `43a16e8`, `5527c3e`, `a085a4c`, `e0ca829`,
  `95a9a3b`, `dc6f77f`, `012bedf`.
- Gate de cierre: suite completa **680 passed / 0 failed** (pytest, 12m23s; corrida del
  reviewer) — consistente con lo declarado (676 de T4 + 4 de T5); focales **31**;
  `make validate` **141 PASS / 2 FAIL F011 preexistentes** (drift de la instalación en HOME
  pendiente de activación del dueño; A3 solo donde existe `tests/.sensitive-patterns.local`,
  con **0** archivos del diff). Sin CI (gate local).
- Contrato: `spec.md` sha256 `f6b28af8…` (PD-1..PD-17, INV-1..INV-8); `plan.md` (T1..T5).
  VERIFY 1/2/3/4/6 del discovery §12 **cerrados**; **VERIFY 5 abierto** (activación del
  proyecto de aceptación).
- Evidencia: `spec.md`/`plan.md`, `discovery.md`, `review.md`, tests
  `tests/test_005_006_t{1..5}_*.py`.

**Deuda y hallazgos (no bloquean el cierre):**

- **F2 (opcional):** INV-7/INV-8 sin test dedicado → un diff futuro podría pisar la fila 3 del
  plan del epic o sus criterios de aceptación sin que la suite proteste (misma clase que el
  lock de T3 cerró para `cdad_packet.py`); cierre sugerido: lock estructural de ~10 líneas.
- **F3 (FYI):** desviación de T3 (tocó `project-start.md` además de `epic-planning.md`, efecto
  directo de PD-12(b); autorizada y registrada). Nota de orden: **T1 y T3 corrieron en
  paralelo** tocando `project-start.md` (sin conflicto en esta corrida; recordatorio para el
  planificador — tamaño de unidad / `files` por tarea, **005-007**).
- **F5 (opcional-considerar):** aserciones con **ventanas absolutas** (`test_pd9`, ventana
  230-300) y marcadores laxos (`PD10_INSTALL_MARKERS` incluye «installation» genérico) —
  tolerantes por diseño declarado, sin efecto hoy; revisitar si otra feature desplaza las
  ventanas.
- **Preexistentes, ajenos a la feature:** **F011** (drift de mirrors de HOME) y **A3**
  (patrones sensibles); **sin CI**.
- **Deuda del discovery que NO entra (fuera de alcance, spec §5/§9):** medición de contexto
  (005-002), orientación al retomar y reducción de lecturas (005-003), roles en Claude Code
  (005-004), planificación progresiva (005-007), y CI / ANON-1 / R2-STAGE / POLICY-CLASS
  (deuda de 003-007). Límite declarado: el **doble bootstrap** (Memory Bank vs ejecución v2)
  sigue siendo **dos procedimientos distintos**; el arranque corto los **encadena**, no los
  fusiona.

**Lecciones de proceso:**

1. **El defecto del test se corrige con una enmienda firmada de oráculo, no bajando la
   aserción.** El implementer de T1 alcanzó 14/15 y **se detuvo** ante un rojo insatisfacible:
   `test_pd9` acumulaba `window_hits` como strings pero los recorría como `(lineno, _)`
   (`ValueError`). La enmienda `91eaaaf` (solo tests, 3+/1−) pasó a tuplas, **misma ventana**
   230-300, **ninguna aserción debilitada**; el RED se preservó.
2. **Una regresión en background no sobrevive entre turnos: el rol no puede cerrar su unidad
   con el gate en segundo plano.** En T2 GREEN el implementer **devolvió dos veces sin
   cerrar** (la regresión en background moría con la sesión; la suite llegó a ~76% antes de
   cortarse); se **reanudó en la misma sesión**, commiteó y reportó. La suite completa del
   cierre la corre el orquestador.
3. **El plan puede omitir un archivo que el PD exige (hallazgo de plan de T3).** T3 debía tocar
   también `project-start.md`, que la lista de `Files` de §T3 no enumeraba; el orquestador lo
   autorizó como **consecuencia directa de PD-12(b)** (desvío de alcance nulo: el archivo ya
   estaba en el write scope) y lo registró. Además, **T1 y T3 corrieron en paralelo** sobre
   `project-start.md`.
4. **El esquema cerrado de la observación de despacho cambia entre versiones (v9).** El CLI v9
   (`7f66619`) exige en la observación de despacho **exactamente**
   `runtime/model_configured/model_reported/session/started_at/provenance`; los registros de
   005-005 traían además `execution_id/packet_id/role/substage` — forma que el v9 **rechaza
   fail-closed sin efectos**. `model_reported` queda en `null` (no hubo reporte independiente
   del modelo efectivo). Lección: los esquemas cerrados del CLI son sensibles a la versión; una
   observación no es un campo libre.

**Condición de cierre (dueño, F4):**

La aceptación real **R2** (arranque de un proyecto parcialmente inicializado del dueño hasta
una primera delegación útil) **no** se corrió en el ciclo: el producto **instalado en HOME**
todavía **no** contiene los textos nuevos (la **activación de versiones** es reservada al
dueño). Correr R2 sobre la instalación vigente sería correr con la versión vieja (viola el
criterio 2 del epic: versión estable sin mezclas). Condiciones de cierre: (1) **activación del
dueño** → `bash install.sh --check` rc=0; (2) **R2 real** registrada como evidencia → cierra
**VERIFY 5**; (3) opcionalmente, concentrar **F1** (ya cerrado) en ese mismo viaje de
regeneración. Sin (1)+(2), la feature **no** está cerrada en aceptación.

**Next feature in queue:** `005-002-session-context-meter` (epic-005, queued; 4.º en el plan
por prioridad) — formato de medición neutral del runtime + lector read-only de sesiones de
OpenCode (tokens / lecturas / herramientas y momento del primer `resume`, por sesión y rol).
Depende de la adopción/activación de la versión nueva (decisión del dueño, la misma que
desbloquea la R2 de esta feature). `005-007-progressive-planning` (que **depende de 005-006**)
queda queued, con la nota de F3 (tamaño de unidad / `files` por tarea) como insumo.

## 2026-10-09 — Feature: 005-005-adoption-coherence (epic 005)

Cerrada el 2026-10-09. Segunda feature de epic-005: **continuación correctiva de
005-001**. No agrega roles, sub-modos ni contratos nuevos: cierra tres
incoherencias que quedaron abiertas al cerrar 005-001 y deja verificable la
procedencia de la instalación con la que corre el ciclo. Cuatro tareas (T1–T4;
T4 = test de integración de cierre). Gate de cierre: suite completa **649 passed
/ 0 fallos** (pytest), focales y regresiones OK, `make validate` con los **2 FAIL
F011 preexistentes** (R6). Review formal **única** `changes-approved`, sin
bloqueantes, con 5 observaciones opcionales. Diff `f148304..HEAD` (vida completa
de la feature): 31 archivos, +3904/−107.

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **El reemplazo valida el encargo resultante completo (T1; PD-1..PD-7; D1/D2;
  INV-4).** Contexto: `--replace-packet` validaba **sólo** los campos presentes en
  el set `corrected` (`_validate_corrections`, gates por campo): un `input`
  **conservado** que apuntaba a un archivo inexistente pasaba sin diagnóstico, y
  un alcance conservado fuera de política fallaba con el mensaje genérico de
  `validate_request` (que no nombra campo ni opción). Razón: el dominio de
  validación del reemplazo es el **encargo resultante** (conservado + corregido),
  no sólo lo corregido; se quitó el set `corrected` y `_validate_corrections`
  valida **todo** `inputs`/`read_scope`/`write_scope`, reusando los textos
  campo/motivo/opción. Trade-off: la exigencia de existencia de `inputs` es propia
  del sub-modo de reemplazo (debe dejar un encargo válido) — **el camino normal de
  `prepare` no cambia** (PD-5/INV-4, con test focal: un input declarado
  inexistente sigue `rc=0`); una lista `inputs` vacía (`--input -`) sigue válida
  (PD-6).
- **Una sola política de evidencia, con dueño canónico y consumidores que remiten
  sin copiar (T2; PD-8..PD-10; D3; INV-6).** Contexto: convivían afirmaciones
  contradictorias sobre la frecuencia de la suite completa (`stage-3-tdd.md:153`
  «once per GREEN» y `re-entry.md:149-150` **vs.** `stage-3-tdd.md:31` y el gate
  del epic), y los paquetes canónicos decían «the required full regression suite»
  (término indefinido). Razón: `stage-3-tdd.md` gana la sección **«Test evidence
  policy»** como dueño único (regresión proporcional al cambio; suite completa
  **al cierre** de la feature o antes si se toca instalador/staging/renderer;
  **reutilización** de evidencia equivalente, cuyo dueño sigue siendo
  `re-entry.md` §«Equivalence of a registered run»; **la metodología define la
  evidencia y el proyecto declara los comandos**; una condición local se registra
  y **no** se vuelve requisito); los 13 consumidores (paquetes de
  GREEN/refactor/review-fix, `roles/implementer.md`, `SKILL.md`, referencias)
  **referencian** la sección y no copian su texto. Trade-off: los comandos focales
  y de suite pasan a ser declaración del proyecto (Makefile/systemPatterns); el
  barrido debe mantenerse (sin afirmaciones de frecuencia por GREEN).
- **La procedencia de la instalación se declara y no cambia en silencio (T3a;
  PD-12..PD-15; D4/D5; INV-7).** Contexto: `prepare` resolvía el origen de los
  agentes de proyecto de OpenCode desde `CDAD_OPENCODE_AGENTS_DIR` o, sin ella,
  desde la instalación global de HOME (`_derived_source_dir`); **no** consultaba
  el registro de activación, y una contradicción de versiones (variable vs
  registro vs global; caso real MIX-V6V7) re-derivaba los 11 agentes de **otra
  versión** sin avisar. Razón: el orden es **variable > registro de activación
  (`.cdad/activation.json`) > global**; cuando el origen resuelto difiere del
  registro o del `source_dir` del manifiesto anterior, `prepare` emite un
  diagnóstico por **stderr** que **nombra `.cdad/activation.json` y las versiones
  en juego**; el manifiesto publicado `.opencode/agents/.cdad-derived.json` declara
  `source_dir` y `source_version`. Trade-off: el registro pasa a ser la fuente por
  defecto cuando existe (este repo **no** tiene activación: el manifiesto apunta a
  HOME); `opencode reload` sobre un servidor ya iniciado queda **NO verificado**
  (PD-15: se documenta el hecho del dueño y la comprobación aislada de que un
  agente de proyecto sombrea al global en proceso nuevo; **no** se afirma el
  `reload`).
- **El instalador declara su versión en la raíz (T4; PD-14; D5).** Contexto: el
  T4 RED destapó que una instalación aislada **no** declaraba qué versión cargó
  (el manifiesto sólo llevaba `source_dir` + hashes). Razón: `install.sh` resuelve
  `installation_version` (commit del checkout, o sha256 del manifest de staging en
  copias portables) y escribe **`version.txt`** en la raíz instalada +
  `source_version` en el manifiesto de propiedad; el renderer lee ese marcador para
  publicar `source_version`. Trade-off: la instalación **v8 vigente** (anterior al
  marcador) sigue con `source_version: null` — su despliegue es tarea del dueño
  (O5); la versión nueva del repo sí lo declara (verificado in situ por T4).
- **La enmienda de PD-17 de 005-001 es documental y fechada (T2; PD-11; R1).**
  Contexto: PD-17 literal describía un recorrido (editar el plan del epic y
  reemplazar el paquete del architect) distinto del realmente ejecutado. Razón: se
  enmienda con fecha (2026-10-09) para que su letra coincida con el recorrido (el
  paquete del architect se **recibe y completa** antes de preparar al test-writer;
  el reemplazo se prueba sobre un paquete **todavía `prepared` y no despachado**);
  no cambia alcance ni criterios del epic. Trade-off: al cambiar los bytes de
  `spec.md` de 005-001 deriva su `contract_sha256` (PD-4) → el pin se
  **re-registra** con los bytes nuevos (`8ba37ce2…`, verificado por la review).
- **Normalización de `review.md` de 005-001 y rutas personales fuera del epic-005
  (T3b; PD-16/PD-17; D7).** Contexto: `review.md` de 005-001 tenía texto corrupto
  (glitch de generación) con una referencia a un PD-27 inexistente; y los
  documentos del epic-005 traían rutas instalación-específicas. Razón:
  normalización **sin repetir la revisión** (veredicto `changes-required`, B1,
  B2..B7, tabla PD↔test y abstenciones preservados; PD-27→**PD-20**); se
  genericizan las rutas personales (`handoff-opencode.md:32`,
  `handoff-opencode-2.md:8,14`) y se conservan los originales en el **registro
  local** `.cdad/local/` (git-ignorado); `~/.claude`/`~/.agents`/`~/.config/opencode`
  permanecen por ser convención genérica de runtime. Trade-off: el criterio
  (identidad de instalación/máquina/usuario → fuera; convención de runtime → queda)
  conserva `handoff-opencode.md:63` y `execution.md:21`, que el encargo enumeraba
  → **VERIFY (dueño) abierto**.
- **El cierre es un test de integración en raíz aislada, no un despliegue (T4;
  PD-18; D8; INV-8).** Contexto: había que comprobar que con la versión nueva se
  puede operar el ciclo sin rodeos manuales, sin tocar HOME. Razón: la secuencia
  `prepare` → `--replace-packet` (validación completa de T1) → despacho con
  validación proporcional corre end-to-end con el **CLI instalado en una raíz
  aislada** (nunca HOME), con guard estructural que rechaza cualquier corrida cuyo
  HOME sea el real. Trade-off: el despliegue/activación en HOME queda reservado al
  dueño.

**Prueba decisiva (PD-18) y review:**

- **Walk-through verde end-to-end** (`test_t4_pd18_walkthrough`): con el CLI
  instalado en raíz aislada, `prepare` → replace con validación completa (insumo
  conservado inexistente `rc=2` campo/motivo/opción, sin efectos; corrección
  explícita `rc=0`) → `record-dispatch` `rc=0`; paquete publicado despachable.
- **El T4 RED destapó un defecto real:** la instalación aislada **no** declaraba
  su versión/commit (PD-14); se cerró en T4 GREEN (`9e5215f`) con `version.txt` +
  `source_version`. El RED-FIX del oráculo (`_is_versionish`, commit `eda293c`)
  fue de **test**, no de producto.
- **Review formal única** (`review.md`): **`changes-approved`, sin bloqueantes**;
  confirma el pedido del dueño (elimina contradicciones y trabajo manual **sin**
  sumar restricciones al camino normal, PD-5/INV-4 con test focal) y separa
  principio de CDAD / decisión del proyecto / particularidad del entorno.
  Verificación propia: suite completa **649 passed / 0 fallos**, focales y
  regresiones OK, `make validate` con los 2 FAIL F011 preexistentes.
- **5 opcionales (no bloqueantes, no extienden el ciclo):** O1 registro de
  activación ilegible → caída silenciosa a global (hueco delgado de INV-7); O2
  «versión desconocida» sin marcador explícito en el diagnóstico; O3 PD-1 sin test
  de sus rebanadas no-input; O4 `CDAD_OPENCODE_AGENTS_DIR` no esterilizada en el
  env de los tests T1; O5 la instalación v8 vigente con `source_version: null`
  (anterior al marcador). **5 abstenciones** (MIX-V6V7 real no reproducido;
  `opencode reload` 2.0.22 no verificable; D7 VERIFY del dueño abierto; O1 no
  ejecutado; 6 errors de `unittest discover` clasificados como artefacto del
  runner — el suite canónico es pytest/conftest).

**Versiones y evidencia:**

- Commits de producto: T1 GREEN `65e887f`, T2 GREEN + enmienda `4b990bb`, T3a
  GREEN `6f7363c`, T3b `b4ce4d9` + `1f1cc63`, T4 GREEN `9e5215f`; de tests:
  `dc66cb2`, `3d9e854`, `fd1aaa3`, `012ccac`, `eda293c`. Diff `f148304..HEAD`
  (24 commits, 31 archivos, +3904/−107).
- Gate de cierre: suite completa **649 passed** (pytest; 16:41), focales y
  regresiones OK (62 + 11 tests), `make validate` **141 PASS / 2 FAIL F011
  preexistentes** (R6). Sin CI (gate local). El suite bajo `unittest discover` da
  584/6 errors por un artefacto del runner (`No module named 'tests'`), no del
  diff.
- Contrato: `spec.md` sha256 `9349b0c1…` (verificado contra los bytes reales);
  `plan.md` aprobado; enmienda de PD-17 → `spec.md` de 005-001 sha256 `8ba37ce2…`
  (pin re-registrado en `stage_history`).
- Evidencia: `spec.md`/`plan.md`, `discovery.md`, `review.md`, `dispatch-ledger.md`,
  tests `tests/test_005_005_t{1,2,3,4}*`.

**Deuda y hallazgos (no bloquean el cierre):**

- **O1..O5** (arriba; a `debt.md`/decisión del dueño). O1 (registro de activación
  ilegible → caída silenciosa a global) y O5 (v8 vigente sin `source_version`) son
  los de mayor valor de seguimiento; el despliegue de la versión nueva es tarea
  aparte del dueño.
- **VERIFY (dueño) abierto — D7:** confirmar si `handoff-opencode.md:63` y
  `execution.md:21` (`~/.claude`, `~/.agents`, `~/.config/opencode`) también deben
  retirarse (el encargo los enumeraba; el criterio aprobado los conserva).
- **Dependencia del epic:** este repo **no** tiene `.cdad/activation.json`; el
  manifiesto apunta a HOME. La activación de la versión nueva es decisión del
  dueño.
- Preexistentes, ajenos a la feature: **F011** (drift de mirrors de HOME) y **A3**
  (patrones sensibles). **Sin CI**.

**Lecciones de proceso:**

1. **El dominio de validación de una corrección es el resultado, no el diff.** Un
   reemplazo que valida sólo lo corregido deja pasar el hueco en lo conservado; el
   encargo resultante completo es la unidad que debe quedar válida.
2. **Una regla con dos dueños deriva en contradicción.** Fijar la política de
   evidencia en un solo lugar canónico y hacer que los consumidores **remitan** (en
   vez de copiar) elimina la clase de contradicción, no la instancia.
3. **El RED destapa el hueco que el fixture no ve.** El test de integración en
   raíz aislada encontró que la instalación no declaraba su versión; la corrección
   fue de producto (`install.sh`), con el RED preservado.
4. **Nunca cambiar de versión en silencio.** La procedencia resuelta debe nombrar
   el registro y las versiones; un aviso que no los nombre no alcanza (INV-7).
5. **Lo no comprobado se declara, no se afirma.** `opencode reload` sobre un
   servidor iniciado quedó documentado como **NO verificado** (sin sub-comando en
   la versión aislada; servidor con 401), con el hecho del dueño como dato.

**Next feature in queue:** `005-002-session-context-meter` (epic-005, queued) —
formato de medición neutral del runtime + lector read-only de sesiones de OpenCode
(tokens/lecturas/herramientas y momento del primer `resume`, por sesión y rol),
sobre las sesiones de 005-001 y la sonda 2 de 003-007. Depende de 005-005 y de la
adopción de su versión (la activación es decisión del dueño).

## 2026-10-09 — Feature: 005-001-idle-and-v7-bootstrap (epic 005)

Cerrada el 2026-10-09. Primera feature de epic-005. Corrige la **circularidad I2**
del arranque de una feature y habilita la **operación real con v7**: el CLI deja de
tratar la spec como precondición para producir la spec. Entrega: (b) **aprobación de
contrato por rol** — el **architect** se habilita con la aprobación del **plan del
epic** (`epic_history` `stage: "epic-plan"`, sin pin de hash, D2); **test-writer,
implementer y reviewer** exigen la aprobación de la **spec concreta** pineada por
`contract_path` + `contract_sha256`; (c) **reemplazo** de un paquete preparado y no
despachado cuyo contrato cambió (`--replace-packet --reason`), conservando el anterior
y sin aprobar el contrato nuevo; (d) **marcadores de bloqueo distinguibles**
`approval pending` / `packet obsolete` / `state incoherent`; (e) `validate-state` acepta
el **reposo legítimo** (`VALID: idle`) y rechaza el incoherente. El punto (a) ya cumplido
(el primer `prepare` del epic publicó los agentes de proyecto v7, `source_dir` + 11/11
hashes) se registra como evidencia. La **enmienda T-CORR** (2026-10-09, instruida por el
dueño) agrega C1 (el pin **nombra** el contrato) y C2 (el reemplazo **conserva y
corrige** el encargo). 4 tareas (T1–T4) + T-CORR; suite completa **629 passed**;
`make validate` con los 2 FAIL F011 preexistentes.

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **La autorización es por rol y con la fuente correcta (T1; PD-1..PD-6; D1/D2/D3).**
  Contexto: el primer `prepare` del epic falló porque el **architect** —que redacta la
  spec— necesitaba una spec aprobada (**I2 circular**); el orquestador lo esquivó con una
  entrada provisional `specification` que también habilitaba a test-writer/implementer
  (atajo). Razón: mover el enforcement de la aprobación de `_validate_v2_vigency` a
  `validate_request` (donde se conoce el `role` y ya está verificado el `sha256` del
  contrato contra el archivo); el architect se habilita por `epic_history`
  `{epic, stage: "epic-plan", approved_by}` **sin pin** (D2: el plan del epic es un
  mandato vivo, se editó después de aprobado y la autorización sigue vigente); los roles
  de construcción exigen una entrada `stage_history` `specification` con `contract_path` +
  `contract_sha256` pineados (D3: sin pin, editar la spec no invalida nada → atajos).
  Trade-off: pinear la spec obliga a **re-registrar la aprobación** cada vez que sus bytes
  cambian (pasó con la enmienda T-CORR, PD-4) y a migrar los fixtures D3;
  `_validate_v2_vigency` conserva la coherencia de estado (feature/epic/delegación) que
  exigen los negativos de `validate-state`.
- **Una entrada histórica no conforme no habilita nada (PD-6/INV-6).** Contexto: el
  `stage_history[161]` real (creado para el primer `prepare` como
  `specification`/`approved_by: Pablo`) se **rectificó** a `discovery-authorization` /
  `authorized_by` con `rectified_at`. Razón: una entrada de otro vocabulario o sin pin no
  debe habilitar autoridad; el test PD-6 reproduce ese caso exacto. Trade-off: el
  vocabulario histórico de `epic_history` de epics viejos no se unifica (fuera de alcance).
- **El pin debe NOMBRAR el contrato (C1, T-CORR; PD-18/INV-8).** Contexto: un `sha256`
  correcto con otro `contract_path` (o sin path) habilitaba —caso de una aprobación copiada
  de otra feature cuyo contenido coincidía por casualidad. Razón: `_contract_approval_for`
  exige además `entry["contract_path"] == contract["path"]`; el diagnóstico nombra el path
  **registrado** vs el **esperado**. Trade-off: endurece el registro (una entrada sin
  `contract_path` deja de autorizar); el mensaje conserva los tokens
  `stage_history|specification|approved` y la ruta (R2).
- **Reemplazo de un paquete preparado y no despachado (T2; PD-7..PD-11, PD-16; D4).**
  Contexto: al editar el plan del epic después de preparar el paquete del architect, este
  quedó obsoleto y el CLI no ofrecía reemplazarlo; `--resume-packet` lo rechazaba
  (correcto). Razón: `--replace-packet <id> --reason` re-resuelve el contrato del día y
  publica un sucesor **solo** si la aprobación vigente lo habilita (PD-11: no inventa
  autorización); exige obsolescencia verificable (PD-8: `sha256` del contrato o revisión de
  política cambiados); un `dispatched` sigue exigiendo **reconciliación** (PD-10); conserva
  byte a byte el paquete anterior (INV-3) y deja `.superseded.json` durable. Trade-off: el
  reemplazo **no** es un atajo para saltar PD-4 —sin deriva genuina da rc=2 sin efectos— y
  `--reason` es obligatorio.
- **El reemplazo CONSERVA y CORRIGE el encargo (C2, T-CORR; PD-19..PD-24/INV-7; D4
  enmendada/D7).** Contexto: la versión previa («sin flags ordinarios») conservaba solo
  identidad/subetapa/objetivo y **recomputaba** los defaults, de modo que no se podía
  corregir el encargo de un paquete obsoleto. Razón: `_replace_packet` conserva campo a
  campo el `REQUEST.json` anterior (`execution_id, role, substage, objective, inputs,
  read_scope, write_scope, invariants, expected_output, evidence_required`) y admite las 6
  opciones de corrección `--input/--read-scope/--write-scope/--invariant/--expected-output/
  --evidence` (cada una, si se da, reemplaza esa lista/campo **entero**; centinela `-` como
  único valor la deja vacía; `-` mezclado → rc=2); los pisos obligatorios del rol
  (`DEFAULT_INVARIANTS`/`DEFAULT_EVIDENCE`) se re-agregan siempre (PD-21); las correcciones
  pasan las **mismas validaciones** que un `prepare` normal (PD-22, diagnóstico
  campo/motivo/opción); el argv mezclado se rechaza (PD-23); `.superseded.json` suma
  `conserved_fields`/`changed_fields` disjuntos y exhaustivos (PD-24). Trade-off: superficie
  de corrección más rica (más casos de validación) a cambio de mantener el encargo atómico
  pero corregible, sin reabrir identidad ni contrato.
- **El reposo legítimo es un estado válido (T3; PD-13..PD-15; D5).** Contexto:
  `validate-state` rechazaba un state con `active_feature: null` que conservaba el bloque
  `execution` de la última feature y/o un `active_packet` terminal. Razón:
  `active_feature == null ⟺ current_stage == "idle"`; se tolera `execution` remanente y un
  `active_packet` terminal `completed|failed`; un paquete en vuelo (`prepared|dispatched`)
  con reposo → `state incoherent` (PD-15). Trade-off: `_validate_idle_coherence` no valida
  `state.version`/`epic_features` del reposo (tolerancias congruentes, FYI sin acción).
- **Los bloqueos dicen qué falta y cómo seguir (PD-12).** Los tres marcadores (`approval
  pending` / `packet obsolete` / `state incoherent`) son **mutuamente excluyentes** por
  condición, salen por stderr con rc=2, nombran el registro/falta concreto y la acción
  legítima siguiente, y **no** alteran el state ni publican archivos.

**Prueba decisiva (PD-17) y uso real (T4):**

- **Un solo escenario secuencial end-to-end** (caja negra, subprocess; sin mocks de
  producto): (1) architect/discovery **rc=0 sin spec**; (2) test-writer **rc=2 `approval
  pending`** sin paquete en disco; (3) tras crear y **pinear** la spec, test-writer rc=0
  (paquete P1); (4) `--resume-packet` de un paquete obsoleto → `packet obsolete`;
  (5) `--replace-packet` → paquete nuevo, bytes del anterior intactos, `.superseded.json`
  con el motivo, sin tocar `stage_history`/`epic_history`; (6) negativo: reemplazo de un
  paquete no obsoleto → rc=2 sin efectos. **Verde end-to-end** (commit `70df141`).
- **El RED destapó un defecto real** (T4 RED, `bd65cd6`): con el archivo de la spec ausente
  y sin aprobación, `prepare` daba el error genérico «cannot read contract» en vez de
  `approval pending`; el GREEN agregó `_reject_absent_contract_without_approval`
  (PD-3/PD-12/PD-17 paso 2).
- **Escenario ajustado (declarado, no silencioso).** PD-17 literal edita el plan del epic y
  reemplaza el paquete del **architect**; el test edita la **spec** y reemplaza **P1
  (test-writer)** — porque el paquete del architect se recibe y completa antes de preparar
  al test-writer (instrucción del dueño 2026-10-09). El ajuste está en `dispatch-ledger.md`
  (fila 13) y `debt.md` (B2). Queda sin test la semántica específica del architect (contrato
  `approved-epic-plan` sin pin de hash, D2); riesgo conductual bajo (mismo code path).
- **Higiene del RED verificada:** 3 ciclos RED→GREEN interrumpidos por defectos del **test**
  (no del producto), con derivación al test-writer y re-RED verificado con `git stash`
  (ledger filas 6/9/14).

**Versiones y evidencia:**

- **Versión operativa:** v7 `ce09ed0` (activada por el dueño el 2026-10-08;
  `docs/runtime-adopted-version.md`). Primer `prepare` del epic: agentes de proyecto v7
  publicados desde `<adopted-root>/.config/opencode/agents` (`source_dir` + 11/11 hashes,
  manifiesto OK).
- Commits de producto: T1 `c885f02`, T2 `0e77e49`, T3 `11e1454`, T-CORR `bfe8edb`, T4
  `70df141`; de tests: `e49a1ce`, `7941007`, `66b880a`, `d7355b7`, `3b5c5ec`, `bd65cd6`,
  `ec8bd48`; review-fix B1 `9468027` + familia `1faef04`. Spec/plan `71520dd`; enmienda
  T-CORR `d1b36c2`. Diff `c78a0e4..HEAD`.
- Gate de cierre: suite completa **629 passed** (3 segmentos, sin fallos), focales de la
  feature **30 passed**, `make validate` **141 PASS / 2 FAIL F011 preexistentes** (drift de
  mirrors de HOME; A3 patrones sensibles → ANON-1). Sin CI (gate local).
- Review formal **única** (`review.md`, veredicto `changes-required`): 1 bloqueante **B1** +
  6 opcionales (B2..B7) a deuda. `sha256(spec.md)` = `9b92b8f4…` verificado contra los bytes
  reales; la entrada superada del 2026-10-08/hash `a793522a…` no otorga autoridad (PD-4).
- **Enmienda T-CORR:** al editar `spec.md` su `contract_sha256` derivó; el pin se
  **re-registró** con los bytes nuevos y la entrada previa quedó superada. El plan del epic
  también cambió de hash (apartado «Cambios al plan», 2026-10-09).
- Evidencia: `spec.md`/`plan.md`, `review.md`, `debt.md`, `dispatch-ledger.md`,
  `handoff-architect-001.md`, `architect-draft-001.md`.

**Bloqueante B1 y su cierre:**

- **B1 (único bloqueante, doc declarado por el plan):** la sección **«Reemplazo»** de
  `skills/cdad-cycle/references/project-execution.md`, declarada por el plan (T2 y T-CORR),
  **nunca fue escrita** (grep `Reemplazo|replace-packet` → rc=1). El sub-modo estaba
  verificado en el código (todas las postcondiciones de runtime cumplidas) pero el techo
  referencial del operador no lo describía.
- **Cierre verificado:** commit `9468027` agrega «## 8. Reemplazo (`--replace-packet`)»
  (+75/−1), fiel a PD-7..PD-11/PD-16/PD-19..PD-24 y D4/D7, apuntando a la spec como
  contrato normativo; la **familia** se cerró como familia (calibración): `1faef04` agrega
  «replacement» a la línea del índice de `SKILL.md` que describe `project-execution.md`.
  Cierre comprobado por el orquestador con grep (rc=1→rc=0) y `git diff --stat`. Cambio
  doc-only (no toca el techo del bloque estático: aplica a `packets/`, no a `references/`).

**Deuda y hallazgos (no bloquean el cierre)** — consolidada en `debt.md`:

- **B3 (media, decisión del dueño) — la raíz v7 viva quedó fuera de sync para
  `cdad_packet.py`.** `sha256(repo)` ≠ `sha256($HOME/.config/opencode/…/cdad_packet.py)` ≠
  el de la raíz adoptada (`$HOME/.cache/cdad-adopted-ce09ed0/…`, sin `--replace-packet`);
  los otros scripts (`cdad_continuity`/`cdad_result`/`cdad_guard`) sí coinciden y el
  manifiesto de agentes está OK (11/11). El próximo `prepare` despachado por la raíz v7
  usaría un CLI **sin** C1 ni `--replace-packet` (reintroduce la circularidad I2).
  **Re-sincronizar/activar la raíz es reservado al dueño** (spec §5, R3); cierre propuesto:
  registrar los dos shas (hecho) y re-sincronizar antes de 005-002.
- **B2 (m, deuda):** PD-17 literal vs. escenario ajustado (arriba). Cierre si el dueño
  quiere: bloque S5-arch en `test_005_001_t4_decisive.py` o enmienda de PD-17.
- **B4 (l):** contrato con pin de path correcto pero archivo **borrado** → diagnóstico
  genérico «cannot read contract» en vez de `approval pending` (rc=2 sin efectos).
- **B5 (l):** el test de PD-23 estresa 7/15 flags foráneos (el mecanismo `_reject_mode_mix`
  cubre los 15 en runtime, verificado por lectura).
- **B6 (l):** oráculo débil en PD-22 (la regex de motivo se satisface con el texto del
  wrapper).
- **B7 (l):** mensajes de test heredados de la época RED que hoy describen un defecto ya
  corregido.
- **Observación de gate — agentes derivados de una fuente no-v7:** al retomar, el manifiesto
  apuntaba a `~/.config/opencode/agents` (instalación de HOME) por algún `prepare` sin
  `CDAD_OPENCODE_AGENTS_DIR`; corregido en la sesión. Candidato de mejora de producto: que
  `prepare` resuelva la raíz adoptada sola (criterio 2 del epic).
- **T3 «state-detection.md» sin modificar:** desviación declarada y correcta (:27-30 ya
  documentaba la invariante). **Considerado y descartado** en `review.md`.
- Preexistentes, ajenos a la feature: **F011** (drift de mirrors de HOME) y **A3** (patrones
  sensibles). **Sin CI**.

**Lecciones de proceso:**

1. **Una aprobación que no nombra lo que aprueba no aprueba nada.** C1: el `sha256` correcto
   con `contract_path` ajeno (o ausente) habilitaba autoridad; el pin debe **nombrar** el
   contrato — hash **y** ruta.
2. **Reemplazar no es recomputar.** C2: conservar campo a campo el encargo anterior y
   aplicar correcciones explícitas mantiene el encargo atómico **y** corregible; recomputar
   los defaults perdía el encargo.
3. **El diagnóstico es parte del contrato.** Los tres marcadores mutuamente excluyentes
   (`approval pending`/`packet obsolete`/`state incoherent`) con la acción siguiente
   convirtieron un bloqueo mudo en recuperación guiada.
4. **Un defecto de clase se cierra como clase (B1).** El bloqueante de doc se cerró con la
   sección **y** su mención en el índice de `SKILL.md` (familia), no enumerando variantes.
5. **El RED honesto destapa defectos de producto.** El escenario decisivo (T4) encontró el
   diagnóstico ausente («cannot read contract» en vez de `approval pending`); el test se
   corrigió por derivación (nunca en GREEN), con RED preservado verificado por `git stash`.
6. **La revisión de gate del plan puede quedar sin escribir.** El bloqueante B1 existió
   porque una referencia declarada por el plan no se materializó; el gate de cierre debe
   **grep-verificar** que todo artefacto declarado existe.

**Next feature in queue:** `005-002-session-context-meter` (epic-005, queued) — herramienta
read-only sobre `opencode.db` que mide contexto por sesión/rol (línea base a reproducir
sobre la primera sesión de 005-001). Depende de 005-001. Antes: re-sincronizar la raíz v7
viva (B3, decisión del dueño).

## 2026-10-08 — Feature: 003-007-living-continuity (epic 003)

Cerrada el 2026-10-08. Extiende `cdad_continuity` para **tolerar la evolución normal del
trabajo**: distingue dos clases de referencia **declaradas por el escritor** (nunca
derivadas de la ruta) — `contract` (spec/plan aprobados, `docs/cdad-policy.json`, state
con proyección de autoridad, aprobaciones, delegación HITL) que **bloquea** (`rc≠0`) al
cambiar, y `living` (ledgers, `debt.md`, Memory Bank, adoption/continuity ledgers,
borradores de cierre/enmienda) que solo **informa** (`state: changed|missing`,
`current_sha256`) y **no** bloquea. Resuelve las dos fricciones altas que dejó 003-006:
**T4-REF** (la deriva de un documento vivo bloqueaba `resume`/`reconcile`/`trigger`) y
**T4-CKPT** (un checkpoint de límite se confundía con un `begin` duplicado). Además
reconcilia la regla de encargo del orquestador (unidad despachable) y declara las clases
del bloque "Continuity wiring". **Última feature de epic-003.** 4 tareas (T1–T4); suite
completa 599 passed en `1f5fdac`.

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **La clase la declara la referencia, no la ruta (D2/P3).** Contexto: antes de 003-007 no
  había clases: toda referencia del checkpoint bloqueaba ante cualquier cambio, y el
  progreso normal (ledgers, deuda) impedía reanudar (T4-REF). Razón: `--update.references[]` acepta
  un string (compat, `class = contract`) o un objeto `{path, class, fields?}`; ausente o
  desconocido → `contract` (**falla cerrado**); el CLI nunca clasifica por ruta y la clase
  resuelta se **estampa** en el body. Trade-off: el escritor debe declarar la clase (los
  checkpoints nuevos la congelan); los cuerpos legados quedan a la resolución por
  comparación (P7).
- **`contract` bloquea; `living` informa y nunca calla en silencio (P1/P2/D3).** Razón:
  cada referencia visible en `resume`/`reconcile`/`trigger` se reporta
  `{path, class, sha256, current_sha256, state ∈ unchanged|changed|missing, legacy?}`; una
  deriva `contract` → `rc≠0` con path y delta exacto; una deriva `living` → `rc 0` con
  `state: changed|missing`. Trade-off: la tolerancia es observable, no muda — el
  orquestador decide con el `changed` reportado.
- **Proyección de autoridad del state con `fields` (D1/P4/BL-3).** Contexto: el state
  cambia por progreso en cada paso, pero su autoridad no. Razón: `fields` (subconjunto de
  claves top-level de un JSON) hace que el digest cubra solo esa proyección; recomendado
  `hitl_delegation`, `approver`, `execution`; `stage_history` es progreso (residuo **R-2**
  → deuda). `fields` sobre un archivo **no-JSON** o con **proyección vacía** → `rc≠0` **al
  escribir** (el digest se congela en el body; nunca un digest constante que dé cero
  integridad en silencio). Trade-off: la validación es de tiempo de escritura, no de
  lectura.
- **`checkpoint` ≠ `begin` (P5/P6/D5/T4-CKPT).** Contexto: un checkpoint de límite con la
  clave de su `begin` se rechazaba como split-brain y obligaba a no escribir entre el
  `begin` y la reanudación. Razón: el body gana `record` (`begin`|`checkpoint`); un
  `checkpoint` con la clave del head **apendea** un eslabón nuevo (`seq+1`,
  `prev = body del head`); un `begin` divergente con la misma clave sigue **cerrado**
  (despacho duplicado); un checkpoint idéntico re-ejecutado es **no-op** (P6).
  `_detect_split_brain` pasa a **≥2 bodies con `record != "checkpoint"` por clave**
  (huérfanos/legados pre-RU-2). Trade-off: la faceta `checkpoint` del test RU-2 de 003-006
  se reespecificó (declarado en la spec; la faceta `begin` y el all-or-nothing quedaron
  intactos).
- **Legado por comparación (P7/D6/R-1).** Contexto: los checkpoints pre-003-007 no traen
  `class`. Razón: una referencia sin `class` en un cuerpo legado se resuelve en lectura:
  digest igual al congelado → verificado `contract`; distinto o ausente → `changed`/`missing`
  con `legacy: true` y **no bloquea**. Trade-off / límite declarado: la clase de legado **no
  está congelada** (se deriva del estado actual del archivo), de modo que el legado
  **informa** cualquier documento cambiado — incluida una decisión que en un checkpoint
  nuevo sería `contract` (caso `t2-record-decision.md`) — en lugar de bloquear.
- **Regla de encargo reconciliada + clases del wiring (P10/D9/BL-1/R-4).** Contexto: el
  paréntesis viejo del orquestador ("no agrupar subfases") era demasiado estrecho frente a
  la delegación real, y el wiring no decía qué era `living` y qué `contract`. Razón:
  `sources/roles/orchestrator.md` expresa el encargo como **una unidad despachable** (una
  tarea del plan o una subfase TDD; una tarea cuyos RED y GREEN son despachos separados la
  satisface), con postcondiciones trazadas a ≥1 test y un diff acotado y revisable; el
  bloque "Continuity wiring" declara explícitamente las clases (o un puntero estricto a
  `continuity.md`); `make agents` regenera solo los dos agentes orquestador. Trade-off: la
  corrección vive en la fuente del rol y se propaga por el generador (nadie edita agentes a
  mano).

**Uso real (T3, aceptación P9)** (`continuity-ledger.md`, marcadores `<adopted-root>`/
`<project-root>`, sin rutas absolutas locales):

- **v6 bloqueaba por vivos; v7 reanuda.** Sobre el store real de 003-007, `t2-record-decision.md`
  fue enmendada después del último `begin` (escrito por v6, sin clases): `resume` v6 → `rc 1`
  (digest mismatch); `resume` v7 → `rc 0`, `changed` + `legacy: true`. Sobre los stores
  cerrados de 003-004 y 003-006: v6 bloquea ambos por ledgers/deuda/borrador; v7 reanuda los
  dos e informa solo los vivos `changed` (specs y planes `unchanged`).
- **T4-CKPT resuelto en uso real:** un `begin` v7 con clases declaradas (8 referencias: 6
  `contract` —una con `fields` de autoridad del state— y 2 `living`; 3020 B de 16384) → seq 8;
  un checkpoint de límite con la misma clave → **append** seq 9 (`record: checkpoint`, `prev`
  = body del `begin`), ya no split-brain.
- **Bloqueos verificados en copia controlada (sin tocar la spec del repo):** spec editada en
  la copia → `rc 1` con path y digests; `hitl_delegation` alterada → `rc 1`; un cambio de
  `stage_history`/`current_stage` → `rc 0`.
- **Rotación real:** sesión nueva, solo `resume` v7 → reconstruyó objetivo, 14 decisiones con
  su razón, autoridad y próxima acción; informó 1 `living` `changed` y 6 `contract`
  `unchanged`; "no impide continuar"; **cero escrituras**. **P9 cumplida.**
- **Sonda 2 (observable de cierre de P10/(d)):** sesión desechable con el orquestador
  regenerado por T4, prompt idéntico a la sonda 1, **sin nombrar `resume` ni el CLI**:
  **pasa** — invocó `resume` y `reconcile` por su cuenta (llamadas 19–22 de 27) y no escribió
  nada. **Matiz honesto:** lo hizo tras **18 lecturas de orientación** (git, globs, plan,
  ledgers, ayuda del CLI), no como paso literal 1.

**Versiones y evidencia:**

- Gate de cierre: desde la suite completa de `1f5fdac` (**599 passed**, 930 s, 2.ª corrida;
  la 1.ª fue 598/1 por un flaky de `test_003_002_t3_run_evidence` que pasa aislado) solo
  cambió documentación (`continuity.md` + `docs/`). Gate de cierre = tests que leen
  `continuity.md` + `test_003_007_*`: **66 passed**; validadores **141 PASS / 2 FAIL**
  preexistentes (**F011** drift de mirrors de HOME y **A3** patrones sensibles → ANON-1).
- Commits de producto: T1 GREEN `b1e56e9` (+201/−31) y fix de test `4e82ca4`; T2 GREEN
  `f466ed9`; T4 GREEN `1f5fdac` y review-fix F-1 `42f9904`; cierre de T4 `ce09ed0`. Spec/plan
  aprobados el 2026-10-08.
- **Versión operativa:** la versión nueva (v7; probada en T3 como `2ed4c8d`, y el árbol final
  `ce09ed0` usado por la sonda 2) se instaló en **raíz aislada** (`install.sh --optimus`,
  Check PASS de 363 grupos, HOME sin tocar) y se invocó **por ruta explícita**, sin reactivar
  el repo. **El repo sigue activado en v6 (`abcd4d3`)** (`.cdad/activation.json`); **la
  activación de la v7 es decisión del dueño** (pendiente).
- Evidencia: `spec.md`/`plan.md`, `dispatch-ledger.md`, `continuity-ledger.md`, `debt.md`,
  `evidence/t3/` (`v6`/`v7-resume.out`, `rotation.md`, `contract-block-copy.txt`,
  `authority-block-copy.txt`), `evidence/discovery-probe-2.md`, `review-t1..t4*.md`.

**Deuda y hallazgos (no bloquean el cierre)** — consolidada en `debt.md`:

- **MIX-V6V7 (media):** la v6 leyendo un checkpoint escrito por la v7 con `fields` digiere el
  archivo completo y **falla cerrado** (`reconcile` rc 1 por `docs/.cdad-state.json`). Es
  seguro, pero obliga a usar **una sola versión del CLI por ejecución**; documentarlo en la
  adopción de la v7.
- **R2-STAGE (media):** las aprobaciones que solo constan en `stage_history` del state no
  entran en ningún digest (la proyección de autoridad cubre `hitl_delegation`, `approver`,
  `execution`). **POLICY-CLASS (media):** clases por defecto en la política, bloqueado por el
  esquema estricto de `docs/cdad-policy.json` (`cdad_packet.py:406`).
- **T2-R1 (baja):** re-ejecutar un `begin` idéntico después de un append de su misma clave da
  `rc≠0` (falla cerrado, sin escrituras) en lugar de no-op. **CKPT-FORK (baja):** no se
  detectan dos checkpoints divergentes con la misma clave. **T1-N1/N2/N3, T2-N1, T4-F2
  (baja)**, **FLAKY-002-T3 (baja):** flaky de `test_003_002_t3_run_evidence` en la suite
  completa (pasa aislado).
- Preexistentes, ajenos a la feature: **F011** (drift de mirrors de HOME) y **A3** (patrones
  sensibles). **Sin CI** (gate = suite local).

**Lecciones de proceso**

1. **Una distinción declarada por el escritor convierte un bloqueo en información.** Declarar
   `contract`/`living` en la referencia (no inferirlas de la ruta) hizo que la evolución normal
   del trabajo dejara de bloquear la reanudación sin perder la integridad del contrato.
2. **El legado se tolera por comparación, y su límite se declara.** El puente blanket se
   reemplazó por "igual → verificado `contract`; distinto → `changed` con `legacy: true`"; el
   costo honesto es que la clase de legado no está congelada y por eso informa.
3. **Reconciliar el contrato de proceso, no parchear el texto.** El paréntesis "no agrupar
   subfases" se reemplazó por la regla de **unidad despachable** con el ejemplo explícito de
   RED/GREEN como despachos separados, y el wiring pasó a declarar las clases.
4. **La sonda de descubrimiento verifica lo que el fixture no ve.** La sonda 2 confirmó que un
   orquestador regenerado invoca `resume`/`reconcile` **sin que se los nombren**; el matiz (18
   lecturas antes de `resume`) queda registrado, honesto.

**Next feature in queue:** ninguna. **epic-003 cerrado el 2026-10-08** como fase de
infraestructura con enmienda (aprobación del dueño; enmienda actualizada después con 003-007; se
reabre si el dueño no está de acuerdo). Suite de cierre del orquestador: 599 passed en `350a93c`.
Pendiente del dueño: activar la v7 (`ce09ed0`, un comando verificado), Claude Code (confianza de
carpeta y copias de HOME) y la prioridad de la deuda para el próximo epic.

## 2026-10-08 — Feature: 003-006-runtime-adoption (epic 003)

Cerrada el 2026-10-08. Cablea, activa y comprueba las herramientas del epic que ya
existían y no se descubrían: enlaza la continuidad en `skills/cdad-cycle/SKILL.md`,
introduce el generador de activación **por proyecto** `scripts/cdad-activate.py`
(+ `references/runtime-adoption.md`), adopta `receive` en el flujo de despacho y
re-adopta la versión operativa. **No agrega funcionalidad nueva** (el endurecimiento va
a deuda). Entrega: activación determinista **nunca sobre las configuraciones del HOME
real**; `receive` como paso normal (re-entry); `begin`/`checkpoint`/`reconcile`/`resume`
en el ciclo (`trigger` advisory, `classify` fuera); re-adopción **v5** (`d958672`,
cierre T1–T3) y **v6** (`abcd4d3`, +RU-1/RU-2), registradas con verificación de
consumidor. 4 tareas (T1–T3 con review-fix/re-review; T4 = recorrido real).

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **La adopción es por proyecto hacia una raíz aislada versionada; las configuraciones
  del HOME real no se escriben (I1/I2).** Contexto: cada runtime cargaba versiones
  distintas de skills/agentes (OpenCode, Claude Code, Codex) y las copias globales de
  HOME derivan. Razón: `cdad-activate.py --project-root R --adopted-root A` emite
  archivos git-ignorados que apuntan a `A`; **determinista** (mismo input → bytes
  idénticos), **no-clobber** (destino divergente → error, nunca sobrescribe) y con
  **contención de ruta** (todo destino/componiente resuelto con `realpath` debe quedar
  estrictamente bajo `realpath(R)`; un symlink que escapa → conflicto nombrado, rc≠0,
  todo-o-nada). Trade-off: la activación no se commitea (producto = generador,
  procedimiento y tests); la raíz bajo `~/.cache` es la **excepción declarada**; activar
  es decisión del dueño.
- **El hook de Claude Code fija el clasificador a la raíz adoptada (RU-1, defecto de
  integración real).** Contexto: `path-guard.sh:134` resolvía el clasificador en
  `$HOME/.claude/skills/cdad-cycle/scripts/cdad_packet.py` (copia vieja); con política de
  proyecto el guard salía rc=2 y **bloqueaba toda escritura del rol** — fail-**closed**,
  no fail-open como decía P5; los fixtures no lo veían porque la raíz sintética no tenía
  un `path-guard.sh` real. Razón: la activación emite
  `command: CDAD_PACKET_CLI=<A>/…/cdad_packet.py <A>/…/path-guard.sh <rol>`; ningún
  `command:` emitido depende de HOME. Trade-off: corrección de redacción adoptada — el
  fail-open vale solo sin política o con script ausente (`exit 127`).
- **`receive` entra al flujo normal, con un solo escritor del state.** Contexto:
  `reconcile` no podía dar `received` porque el despacho no pasaba la salida por
  `cdad_result` (deuda RU-2a de 003-004). Razón: el orquestador **stagea** el FINAL TEXT
  bajo `.cdad/inbox` (+`RESULT.json`), ejecuta `receive`, valida el receipt y registra la
  transición **única** de state. Trade-off: `receive` no aprueba (`semantic_status`
  `pending`) y el state lo escribe solo el orquestador (extiende ADR-014).
- **Continuidad en el ciclo; `trigger` advisory y `classify` fuera.** `begin`
  (write-ahead), `checkpoint` (límite), `reconcile` (antes de todo retry/resume),
  `resume` (sesión nueva); `trigger` es señal casi siempre `unknown`; `classify` queda
  fuera por falta de lector de sesiones. Trade-off: fricción real de claves
  (T4-CKPT) y de referencias selladas (T4-REF, deuda alta).
- **La versión operativa se adopta en el límite de tarea/cierre, tras review
  independiente.** Razón: v5 (`d958672`) = cierre T1–T3; v6 (`abcd4d3`) = +RU-1/RU-2;
  instaladas en raíz aislada bajo `~/.cache` (`--check` PASS, 363 grupos) y registradas
  en `docs/runtime-adopted-version.md` (tabla vigente + historial). Trade-off: **v6 no
  está activada en el repo** — el clasificador de permisos denegó la activación; la
  decide el dueño. Hasta entonces la configuración del repo sigue apuntando a v4 (`818f12a`); v5 se usó en el recorrido de T4 desde un worktree desechable.

**Uso real (T4)** (`adoption-ledger.md`, marcadores `<adopted-root>`/`<project-root>`,
sin rutas absolutas locales):
- **Identidad por runtime (P4/P5/P6):** OpenCode carga las skills v5 ✓ (en el worktree desechable; el repo real sigue en `818f12a` hasta la activación). Que una sesión nueva descubra `resume`/`receive` por su cuenta **no se demostró**: todas las sondas recibieron los comandos; **Claude Code = mezcla de
  versiones** (las skills de usuario ganan a las de proyecto; los hooks del frontmatter no
  corren si la carpeta no es de confianza; se mitiga con `--setting-sources
  project,local`, verificado); **Codex = ambiguo** (usa la copia de proyecto, verificado
  por contenido, pero el catálogo también lista la vieja de HOME; sin adaptador).
- **RU-1:** defecto y cierre (`5c09770`); la línea emitida, pasada por `bash -c`, bloquea
  `tests/zz.txt` (rc=2) y permite `scripts/zz.py` (rc=0).
- **`receive` real:** staging byte a byte → `receive` rc=0 (`semantic_status: pending`,
  `state_transition_requested: received`); **el reintento idéntico deja receipt y stdout
  byte a byte iguales**; `reconcile` = **`received`** (P7/P8); transición única en state.
- **RU-2:** un `begin`/`checkpoint` rechazado dejaba escrito su cuerpo → bloqueo
  permanente de `reconcile`; cerrado como **todo o nada** (`abcd4d3`), con enmienda del
  test O1 de 003-004. El cuerpo huérfano `2aee8d80…` lo retiró el orquestador (sha en el
  ledger).
- **Rotación (P9):** intento 1 **bloqueado** por integridad de referencias (T4-REF);
  intento 3 **correcto** en sesión nueva, sin escrituras desde el `begin`: `resume`
  reconstruyó objetivo/autoridad/8 decisiones/con razón y `reconcile` dio
  `already-closed` (review-005) y `not-started` (review-006) **sin preguntar al usuario**.

**Versiones y evidencia:**
- Producto congelado en `abcd4d3`; suite **567 passed (926 s)** en `abcd4d3` (gate del implementer)
  y suite de cierre en un worktree fijado a `ea095d5` (ver `closure.md`).
  Focales: T1 9/9, T2 16/16 (+RU-1 18/18), T3 15/15, RU-2 6/6.
- Validadores `make validate` **141 PASS / 2 FAIL preexistentes**: F011 (drift de mirrors
  de HOME) y A3 (patrones sensibles en docs de 004-003 y `test_role_packets.py`) →
  ANON-1.
- Versiones: **v5 `d958672`** (T1–T3) y **v6 `abcd4d3`** (RU-1/RU-2), instaladas en raíz
  aislada; registradas en `docs/runtime-adopted-version.md`. **Activación v6 pendiente del
  dueño.**
- Commits de producto: T1 `a0f2335`; T2 `04ba3d8` + review-fix `7ccea01`; T3 `d958672`;
  RU-1 `5c09770`; RU-2 `abcd4d3`. Spec/plan aprobados en `2c36773`. Ledger/evidence:
  `adoption-ledger.md`, `dispatch-ledger.md`, `evidence/t4/`.
- Deuda en `specs/003-006-runtime-adoption/debt.md` (alta: **T4-REF**; media: T4-CKPT,
  T2-O1, T3-O1, ANON-1, T2-SCOPE).

**Deuda y hallazgos (no bloquean el cierre):**
- **T4-REF (alta):** `resume`/`reconcile`/`trigger` fallan cerrados si cambia cualquier
  referencia del checkpoint; los ledgers/debt cambian en cada paso. Sumado a **T4-CKPT**
  (el checkpoint de límite comparte clave con el `begin` y se rechaza), hoy la rotación
  exige no escribir entre el último `begin` y la reanudación. Opciones: referenciar solo
  artefactos inmutables (commits/receipts/specs) o fijar `path@sha`.
- T2-O1..O3/TOCTOU, T1-F2, T3-O1/O3/O4, RU1-H4/H5, RU2-F4/F6, T2-SCOPE (ver `debt.md`).
- **Sin CI** (gate = suite local).
- **Decisiones del dueño pendientes** (`closure-amendment-draft.md`): cerrar epic-003 con
  la enmienda (fase de infraestructura vs. autonomía prolongada); activar v6
  (`--runtime opencode --runtime codex`); Claude Code (confianza de carpeta +
  retiro/actualización de copias viejas de HOME); priorizar deuda (lector de sesiones,
  medición de contexto, CI, ANON-1).

**Lecciones de proceso**
1. **Los fixtures sintéticos no ven la raíz real.** RU-1 (rc=2 fail-closed) se detectó
   solo en el recorrido real: la raíz de test no tenía `path-guard.sh` real y ocultaba el
   fallback a HOME. El rehearsal real es la evidencia que los fixtures no dan.
2. **Un rechazo que escribe deja estado incoherente.** RU-2: validar **antes** de
   escribir (todo o nada); un error de uso no debe convertirse en bloqueo permanente.
3. **Las referencias selladas a documentos vivos bloquean la reanudación.** T4-REF: la
   rotación funciona solo si no hay escrituras intermedias (003-004 RU-2 pasó por eso).
4. **`prepare … && <launch>` encadenados.** El despacho #26 repitió el defecto de la fila
   22 de 003-004: `prepare` falló y se lanzó con el `PACKET.md` anterior (cortado sin
   cambios). El paquete es del orquestador: si contradice la política, el rol se detiene y
   reporta.
5. **La suite se corre en primer plano.** El implementer de `green-t2rf` la lanzó en
   segundo plano y murió con la sesión, sin evidencia ni commit (se reanudó).

**Next feature in queue:** 003-006 es la **última feature de epic-003** (003-001,
003-005, 003-002, 003-003, 003-004, 003-006 cerradas). Siguiente: **cierre/integración de
epic-003** — la aprobación estratégica es del **dueño** (`closure-amendment-draft.md`,
4 decisiones). El epic-004 ya estaba cerrado; **epic-003 no se cierra acá.**

## 2026-10-07 — Feature: 003-004-context-continuity (epic 003)

Cerrada el 2026-10-07. Entrega `skills/cdad-cycle/scripts/cdad_continuity.py`
(+ wrapper `scripts/cdad_continuity.py`), un CLI **determinista y read-only** sobre
el producto, con cinco comandos: `begin`/`checkpoint` (write-ahead, escriben **solo**
bajo `.cdad/executions/<id>/continuity/**`), `reconcile` y `resume` (read-only,
deterministas) y `trigger` (señal, no límite). Tres contratos con nombre:
`continuity-checkpoint-v1`, `reconcile-v1`, `trigger-v1`. La memoria activa es una
**proyección on-demand** desde la cabeza L2 (no existe `ACTIVE.json` persistido). El
juicio semántico y la escritura de `docs/.cdad-state.json` siguen siendo del
orquestador.

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **CLI read-only sobre el producto; un solo escritor del state (D1/D3).** Contexto:
  la reanudación no debe mutar el ciclo ni heredar la propiedad del estado. Razón:
  `begin`/`checkpoint` escriben solo bajo `.cdad/executions/<id>/continuity/**`;
  `reconcile`/`resume`/`trigger` son read-only; el orquestador es el único escritor de
  `docs/.cdad-state.json`. Trade-off: la reconciliación del estado queda del lado del
  orquestador; el CLI nunca aprueba.
- **Tres capas sin log ni schema de estado nuevos (D2/O1).** Contexto: cargar el
  historial completo contradice el objetivo de contexto reducido. Razón: L2 = checkpoint
  inmutable content-addressed (autoridad de delegación, decisiones y presupuesto); L1 =
  proyección de memoria activa on-demand (**no persistida**); L3 = referencias a la
  historia existente (state/`stage_history`, receipts 002, eventos 003, dispatches I8,
  Memory Bank). Trade-off: `reconcile`/`resume` no dependen de un `ACTIVE.json` (su
  ausencia no es error).
- **Autoridad y vigencia desde el estado estructurado; autoridad vencida reconstruye
  contexto pero no autoriza efectos (D4/P2).** Contexto: la prosa del archivo de
  autoridad no se parsea (`003-001/spec.md:500-501`). Razón: leer `hitl_delegation` +
  `authority_ref`; una delegación vencida puede reanudar la lectura pero **no** autorizar
  dispatch/materialize. Trade-off: la vigencia depende de campos estructurados, no de la
  narrativa del handoff.
- **`trigger` es señal, nunca límite fabricado (D5/P6).** Contexto: no hay límite duro
  de contexto observable (V1/V3). Razón: `prepare`/`rotate` solo si `context_used_tokens`
  **y** `context_limit` son enteros; en cualquier otro caso `trigger: unknown` con
  `context_*: null` y `unknowns[]`. Prohibido convertir bytes en tokens o presentar un
  proxy como límite. Trade-off: en la práctica `trigger` es casi siempre `unknown` hasta
  calibrar con uso real.
- **Write-ahead + `reconcile` antes de todo retry; sin doble efecto (D6/P3, invariante 3).**
  Contexto: un efecto ya recibido/materializado (receipts/journal de 002) no debe
  repetirse. Razón: `begin` antes de despachar y `reconcile` antes de todo retry/resume;
  los receipts de 002 deciden; una sesión desaparecida **≠** fracaso **≠** autorización de
  repetir (`dispatched-unknown`). Trade-off: para clasificar `received` el flujo de
  despacho debe pasar la salida de cada rol por `cdad_result receive` (deuda RU-2a).
- **`begin` idempotente y split-brain escalado (D7/P3).** Contexto: un crash no debe
  duplicar la cadena ni sobrescribir un checkpoint. Razón: cuerpo canónico idéntico al
  head → **no-op exitoso (rc 0)**, clave `(execution_id, packet_id, attempt)`; sin
  contador `generation`, un solo `seq` monotónico; cabezas divergentes o
  igual-sha-con-cuerpo-distinto → **escalar**. Trade-off: no se sobrescribe ni se duplica
  la cadena; el conflicto vuelve al orquestador.
- **MVP OpenCode + artefactos portables (D8) y `continuity` consume el receipt 002 como
  oráculo sin materializar (D10).** Contexto: sin servicio ni agente permanente. Razón:
  OpenCode primero (subagentes nativos, un nivel); Claude Code posterior sin prometer
  paridad; la materialización sigue siendo del orquestador con autorización explícita.
  Trade-off: la portabilidad se declara como artefacto, no como garantía de paridad.

**Uso real (T4):**
- **RU-1:** el primer `begin` real (ejecución `exec-003-004-context-continuity-001`)
  falló con rc 1 (`execution_id must be a safe path segment … None`): el contexto real de
  001 trae `execution.id` (no un `execution_id` plano) y la delegación vive en
  `docs/.cdad-state.json`. **Defecto de integración real que los fixtures no detectaron**;
  se corrigió con review-fix (`0005128`, D4).
- **RU-1b:** tras el fix, `begin` real rc 0 (`seq 1`, `body 58c1df54…`); repetir el mismo
  cuerpo → `no_op: true` sin escritura (`evidence/t4/begin-*.json`). El write-ahead es
  idempotente sobre datos reales.
- **RU-2 (rotación real T3→cierre):** una sesión nueva de `cdad-orchestrator` (OpenCode,
  `mofgw/deepseek-v4.1-flash`, sin historial, solo con `resume`/`reconcile`/`trigger`)
  reconstruyó objetivo, autoridad y su fuente, las 5 decisiones con su razón, las
  incertidumbres y la próxima acción **sin preguntar nada al usuario**; `reconcile` =
  `dispatched-unknown` con `repeat_effect: false` (invariante 3). **P2 y P3 demostradas
  en uso real.** El `dispatched-unknown` es correcto: en el modo de despacho de esta
  sesión no se recibe la salida con `cdad_result` (sin receipt).

**Versiones y evidencia:**
- Gate de cierre: 523 passed (786 s) en worktree fijado a `6110e07`, stdin cerrado; `validate-consistency.sh` 142 PASS / 1 FAIL (F011 `validate-subagents.sh`, preexistente: `install.sh --check` contra copias instaladas; `validate-odoo-specialization.sh` PASS en árbol limpio); validadores sin
  regresiones nuevas (los 2 FAIL de `validate-consistency.sh` son preexistentes, F011).
- Commits de producto: T1 `9705aec`/`209643f` (+ test `071b61b`); T2 `02bc021`/`00dd557`;
  T3 `6c03533`; RU-1 `0005128`; evidencia T4 `6110e07`. Spec/plan aprobados en `9e3a7c5`.
- Deuda en `specs/003-004-context-continuity/debt.md` (alta: ninguna; media: T3-O1/O2,
  V1/V3, rollback/tamper autoconsistente, validadores preexistentes F011/A3, RU-2a).
  ADR-016. Uso real en `continuity-ledger.md`.

**Lecciones de proceso**

1. **Los fixtures pueden no ver la forma real de 001.** RU-1 (rc 1) se detectó recién con
   `begin` sobre el contexto real; el contexto sintético ocultaba `execution.id` anidado
   y la autoridad en el state.
2. **Encadenar el lanzamiento de un rol a `prepare` con rc=0.** El despacho RU-1-a1 usó
   el `PACKET.md` del reviewer anterior porque `prepare` había fallado; el intento se
   cortó sin cambios. Lección registrada: `prepare … && <launch>`.
3. **`install.sh --check` lee stdin.** La suite en primer plano se colgó (timeout rc 124)
   por stdin abierto; el gate equivalente se corrió con stdin cerrado (`< /dev/null`).

**Next feature in queue:** 003-004 es la **última feature de epic-003**
(003-001/002/003/004). Siguiente: **cierre/integración del epic-003** — la aprobación
estratégica del cierre es del **dueño**.

## 2026-10-07 — Feature: 003-003-progress-guards (epic 003)

Cerrada el 2026-10-07. Entrega `skills/cdad-cycle/scripts/cdad_guard.py`, un CLI **opcional**, determinista y de solo lectura, con cuatro comandos:
- `classify`: detecta repetición sin progreso y polling legítimo sobre una traza `trace-v1`.
- `preflight`: prevalidación **consultiva** contra la política y el scope del rol.
- `record`/`budget`: intentos y causas **durables** bajo `.cdad/executions/<id>/guards/`, que se conservan al reanudar.
- Escalado con una tabla cerrada evento→acción.

El juicio queda en el orquestador. El guard nunca escribe el state, no concede ni endurece permisos y no fabrica éxito ni fracaso. Nada lo invoca automáticamente. Cuándo aplica y cuándo no, según el entorno, está en `references/progress-guards.md`: `classify` necesita un lector de sesiones por entorno, que hoy no existe.

**Decisiones del dueño:**
- Salir de la raíz del proyecto está habilitado por defecto: `deny` solo ante una regla explícita.
- La severidad se calibra con uso real, una vez integrada la feature.
- Los C1/C2 observados el 2026-10-07 son artefactos del despacho con `opencode run` (el `background:true` muere con el turno), no del entorno nativo.
- El seguimiento del orquestador por PID no es producto.

**Uso real (T5):** se usaron cuatro sesiones reales, procesadas con un grabador desechable.
- El guard no detectó los C1/C2; vistos como artefactos, no eran incidentes nativos.
- Hubo 2 falsas alarmas, porque el progreso se mide por conjunto de rutas (grano grueso).
- La conclusión está en `guards-ledger.md`.

T1–T3 tuvieron review-fix de una ronda cada una, más la re-review focal; T4 se aprobó, con 4 mutaciones detectadas por los tests.

**Versiones y evidencia:**
- Versión operativa `939f501`, en una raíz aislada, con el consumo verificado.
- Suite de cierre 487 passed en `87d91b2`.
- Validadores: los 2 FAIL preexistentes, ajenos a esta feature.
- Deuda en `specs/003-003-progress-guards/debt.md` (alta: ninguna; media: el lector por runtime y el progreso por contenido, la calibración y T1 F1). ADR-015.

---

## 2026-10-06 — Feature: 003-002-artifact-tools (epic 003)

Cerrada el 2026-10-06. Entrega el **CLI de recepción, materialización y evidencia**
(`receive`, `validate-receipt`, `materialize`, `run-python-unittest`,
`validate-run-evidence`) sobre el runtime de paquetes v2 de 001/004-002: persiste los
bytes originales de un rol con un recibo mecánico **que nunca aprueba**, materializa
artefactos a targets permitidos por una política de artefactos (create-only/CAS) y
emite/valida evidencia de `python3 -m unittest` con snapshots before/after. T1–T4
cerradas con **review-fix en las cuatro tareas** (T1 y T2: 1 ronda cada una; T3: 3
rondas hasta el **remedio de clase fail-closed**; T4: 1 ronda), incluida la
**calibración de la review** decidida por el dueño. **Primer uso real del flujo en
este repo**: `receive` + `materialize` del TEXTO FINAL del reviewer de T4 con
**bytes idénticos** (sha256 `82a63fcb…`) e **idempotencia** en retry, más el smoke
desde el producto instalado en raíz aislada. La **propiedad del estado** quedó
resuelta (un solo escritor: el orquestador) y el protocolo de materialización vive en
`references/re-entry.md`. Suite completa **439 passed** (`d7ffbcc`); los commits
posteriores de review-fix (`aabb614`, `b0f9ade`) son docs-only. Evidencia:
`specs/003-002-artifact-tools/{spec,plan}.md`, `review-t1..t4*.md`,
`supervision-record.md`, `dispatch-ledger.md`; evidencia de utilidad en
`epics/epic-003-context-efficiency/evidence-utility-2026-10-05.md`.

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **Recepción, materialización y aprobación son hechos distintos; el recibo nunca
  aprueba.** Contexto: ADR-003 dejaba la materialización de los artefactos read-only
  en manos del orquestador, transcribiendo el output del rol. Razón: separar la
  persistencia exacta de bytes (recepción), la copia autorizada a destinos canónicos
  (materialización) y la aprobación semántica (externa); `semantic_status` siempre
  `pending`, `approval_effect` siempre `false`, ningún recibo cierra un gate.
  Trade-off: cada materialización exige una autorización explícita
  (`MATERIALIZE.json`); la aprobación sigue siendo del dueño y no se automatiza.
- **Un solo escritor del state: el orquestador.** Contexto: `receive`/`materialize`/
  `run-evidence` operan sobre el store `.cdad/runtime` y targets autorizados, pero no
  `docs/.cdad-state.json`. Razón: preservar la propiedad del estado y evitar que una
  herramienta mute el ciclo; `state_transition_requested=received` es una transición
  **lógica** que el orquestador mapea al estado de paquete `completed` (vocabulario de
  001). Trade-off: la reconciliación del state es del orquestador; ante retry, primero
  se reconcilia el receipt durable y no se repite un cambio ya reflejado en state.
- **Política de artefactos: raíz permitida por `artifact_kind`, target exacto
  declarado en la autorización.** Contexto: la tabla cerrada `artifact_kind -> target`
  no cabía en un único target por kind (`review-t1.md`, `review-t2.md`,
  `review-second-look.md` de 004-003). Razón: la tabla fija la **raíz permitida** por
  kind y la autorización declara el **target exacto** (create-only/CAS); el cierre
  rol↔kind se enforcea por copia (`_allowed_kinds(role, substage)`, fail-closed).
  Trade-off: los ADR (`docs/adr/`) **no** entran en la tabla — su materialización
  sigue siendo del orquestador (ADR-003) y ampliarla quedó fuera de alcance.
- **La vigencia de la autoridad también bloquea `materialize` (R1 de T2).**
  Contexto: `materialize` no leía el state; el reviewer **reprodujo** que una
  delegación revocada no impedía la copia (rc=0 con la copia aplicada). Razón: §5
  exige que la autoridad vencida impida nuevas materializaciones; leer el state está
  permitido (escribirlo, no). Trade-off: el pre-flight reutiliza `validate_state`
  (misma superficie que `receive`); deuda FYI-1: la rama v1-`ordinary` del validador
  no consulta `hitl_delegation`, preexistente y compartida con `receive`.
- **Remedio de clase fail-closed + calibración de la review (decisión del dueño).**
  Contexto: en T3 el reviewer encontró variantes sucesivas del mismo defecto de
  ligadura `argv`↔selecciones (`R1` → `F1` → `R-F1a/b` → `R-F1c`), cada una correcta y
  ninguna cerrando la familia; 3 rondas de RED/GREEN/re-review sobre el mismo eje.
  Razón: instrucción del dueño — «el reviewer no debería ser infinitamente detallista…
  pero no debe perder el objetivo de usabilidad del sistema»; un defecto de **clase**
  se corrige como clase en **una** ronda (whitelist cerrada de opciones invariantes +
  única forma plenamente ligable + degradación por defecto a `unknown`), y la
  usabilidad es criterio de aceptación. Trade-off: la calibración se incorporó a la
  fuente canónica (`references/stage-4-review.md` + `sources/roles/reviewer.md`;
  commits `675c18e`/`64362f8`) como **enmienda declarada, no adoptada** en la versión
  operativa `8cb6580`: viaja como entrada declarada del encargo del reviewer. Deuda: la
  whitelist quedó **más estricta que lo necesario** (`--locals`, `-c` degradan a
  `unknown`; efecto real ≈ nulo, falla del lado conservador).
- **El flujo se validó en uso real, no solo por lectura.** Contexto: la re-review de
  T4 se materializó **a través de 003-002** (`prepare --record-dispatch` → staging del
  TEXTO FINAL + `RESULT.json` + manifest → `receive` → `materialize`). Razón: el
  staging que se ejecutó era **exactamente la cláusula F1.1** que el review-fix
  acababa de escribir en `re-entry.md` — el fix se comprobó en uso. Trade-off:
  quedaron **sin ejercitar** `observation_status=unknown` (el manifest fue `trusted`
  con `changes: []`) y el **CAS de Memory Bank** (el primer uso fue create-only).
- **`README.md` fuera del alcance de T4 (decisión del dueño).** Contexto: el plan T4
  listaba `README.md`, pero `docs/cdad-policy.json` **no lo clasifica** (no es
  `implementation_file` ni cae en `documentation_roots`): ningún rol puede escribirlo.
  Razón: revisar la política está fuera de alcance de 003-002 y cambiarla a mitad de
  ciclo altera `policy_sha256` e invalida el contexto de ejecución y la evidencia
  vigente (desproporcionado). Trade-off: la desviación deja de ser silenciosa y
  registra la **brecha de política** (clasificar `README.md`) como decisión del dueño;
  el front-door queda desactualizado respecto del segundo CLI público.

Deuda y hallazgos (no bloquean el cierre) — consolidada en `supervision-record.md`:

- **`README.md` sin clasificar** por la política (brecha, decisión del dueño); el
  front-door no descubre `scripts/cdad_result.py` (segundo CLI público).
- **No ejercitados:** `observation_status=unknown` (el manifest declarado fue
  `trusted` con `changes: []`) y el **CAS de Memory Bank** (el primer uso fue
  create-only).
- **T3:** whitelist de `argv` más estricta de lo necesario (`--locals`, `-c` degradan
  a `unknown`), doble motivo de diagnóstico en `discover -s tests -k X`, `_module_tree`
  sobre nombre imposible — opcionales, sin camino de falso verde; más O1–O3 de
  `review-t3.md`.
- **T2:** O1 (target fijo no aplicado en las filas con nombre), O2 (journal indexado
  por string crudo, no por path normalizado), O3 (`materialize.schema.json` no se
  carga), FYI-1 (rama v1-`ordinary`), FYI-2 (nombre editorial en la spec de 003-001).
- **T1:** R4 (fachada pública de `scope_contains`/`project_path`; `_project_path`
  copiado literalmente del CLI compartido), R6 (6 nits mecánicos: fsync de dir
  silencioso, fsync del parent tras rename, límite 1 MiB chequeado tras leer en
  memoria, `baseline_sha256` acepta un int de 64 dígitos, tmp dirs de procesos
  matados, args ignorados en retry), FYI (unicidad de `parts[].name` en recibos
  forjados).
- **F3 de T4** (la clase de smoke no ejecuta el entrypoint instalado; el «funciona» lo
  cubre el guard 2) — diferido, desproporcionado. **F2 de T4** (familia
  `handoff-prompts.md`) — **cerrada 3/3** en la misma pasada de F1.1 (punteros al
  protocolo canónico).
- **2 FAIL preexistentes** de los validadores (`validate-consistency.sh` = **141 PASS
  / 2 FAIL**): F011-A (drift de los mirrors de `$HOME`; irresoluble por la regla que
  prohíbe instalar CDAD en HOME real) y F011-B (A3 marcando una palabra contenida en
  un identificador + ruido de `__pycache__`). Ajenos al diff.
- **Ausencia de CI** (deuda de bootstrap; el gate es la suite local).
- **Desviación de proceso:** `contract.commit: null` se interpretó como «no
  commitear» (significa «sin pin de commit»); se reanudó la sesión para commitear con
  pathspec. Un lock `R4a` flaky (carrera SIGSTOP/SIGKILL) detectado por el orquestador
  al re-correr (el rol reportó 6/6); reemplazado por el mecanismo determinista que la
  spec §8 autoriza (pending dir documentada).

**Lecciones de proceso**

1. **Un defecto de clase se cierra como clase, no enumerando variantes.** El remedio
   fail-closed de T3 (`5c76fee`) cerró `R-F1a/b/c` juntos en una ronda; la calibración
   del dueño quedó en la fuente canónica de la review (`stage-4-review.md`).
2. **Verificar la razón de cada falla, no el conteo.** El RED de T3 tenía 13 fallas
   «correctas», pero una era un `AttributeError` por un helper inexistente
   (`append_to`); se detectó recién en el GREEN.
3. **Un lock flaky es peor que ninguno.** El orquestador debe re-correr los locks, no
   aceptar el reporte del rol (R4a: el rol reportó 6/6; el re-run dio 3/3/3/4 fallas).
4. **La reutilización de evidencia exige equivalencia de producto + tests + selección
   + entorno.** 10 citas válidas en el ciclo; el cambio de producto
   (`32d290c`/`5c76fee`) invalida la suite previa, el cambio de `docs/.cdad-state.json`
   no.
5. **El RED de una tarea de integración cuyas unidades ya existen es de guards +
   evidencia de aceptación, no una falla fabricada.** El test-writer declaró
   honestamente 6/6 GUARDS RED en T4.
6. **La suite en background muere con la sesión del subagente** (5 veces en el ciclo):
   pedirla en primer plano; al reanudar, citar la corrida vigente por PD-5.

**Next feature in queue:** `003-003-progress-guards`, luego
`003-004-context-continuity` (ambas **queued**; no se implementan por anticipado).
epic-003 reactivado (2026-10-05, mandato HITL re-registrado en
`handoff-resume-2026-10-05.md`); epic-004 **cerrado** (2026-10-05,
`epics/epic-004-single-source-planning/closure.md`).

## 2026-10-05 — Feature: 004-003-planning-procedures (epic 004)

Cerrada el 2026-10-05. Convierte el contrato de planificación y los requisitos de
orquestación proporcional (`efficient-orchestration-requirements.md`) en
**procedimientos de roles existentes** (no un planner nuevo): contrato de primera
clase para un plan **borrador**, subfase de revisión de plan, plan de validación
por unidad y regla de equivalencia/re-entry. T1–T5 y T7 cerradas; **T6 condicional**
(F4 fuera del camino feliz de este repo). **Brecha D8 cerrada**: primer paquete v2
del architect (`approved-epic-plan`). Suite completa **364 passed** en el worktree
fijado `287f6c7`; instalación aislada `install.sh --check` **PASS (303 grupos)**.
**AC-7 eximido por decisión del dueño** (HITL delegada). Cierre:
[closure.md](specs/004-003-planning-procedures/closure.md); supervisión PD-17 en
`specs/004-003-planning-procedures/supervision-record.md`.

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **`draft-plan` como contract-kind de primera clase que NO aprueba (D1, PD-1).**
  Contexto: el renderer solo soportaba `reviewer/review` contra
  `approved-feature-spec`; revisar un plan **antes** de aprobación no cabía
  honestamente en ese contrato (plan.md:284-289 del epic). Razón: separar el
  artefacto revisado del estado de aprobación; la emisión lleva el sha/versión del
  borrador y un guard detecta la forja (`approved-*` + `plan_version` → rc≠0, sin
  publicación). Trade-off: la sintaxis de flags
  (`--contract-kind/--contract-path/--plan-version`) la fijó el oráculo del
  test-writer (T1) y el orquestador la **aceptó** como detalle de implementación
  dentro del contrato aprobado, congelada pre-GREEN; el reviewer de etapa 4 la
  desafió y la restringió a `role=="reviewer"` (F1 de `review-t1.md`). La brecha
  D8 que originó la feature se cierra acá (primer paquete v2 del architect,
  `evidence/t7-journey.md` §2).
- **La revisión de plan es procedimiento del reviewer existente, no un agente
  nuevo (PD-4).** Contexto: se necesitaba que el reviewer recibiera intención +
  restricciones + plan (no solo la spec). Razón: no crear planner permanente ni
  sub-agente; corre sobre el rol reviewer en sesión independiente. Trade-off: el
  pairing `draft-plan`⇔`plan-review` (solo reviewer) se enforce en un punto único
  (`validate_request`), en ambas direcciones (B1/B2 de `review-t2.md`); la fuente
  de rol compartida `packets/roles/reviewer.md` se generalizó una vez (B3).
- **`re-entry.md` dueño único de la regla de equivalencia (D4, G1–G3,
  PD-5/6/7/10).** Contexto: la re-ejecución rutinaria de suites completas duplicaba
  trabajo. Razón: citar una corrida registrada cuando hay equivalencia de
  árbol/política/entorno; forzar corrida nueva solo si falla; declarar la
  incertidumbre. Trade-off: **PD-5/PD-6 no tienen enforcement ejecutable** — son
  disciplina del orquestador verificada por revisión, no un mecanismo (límite
  declarado en closure.md); `SKILL.md` quedó como co-dueño de la regla de dos
  intentos con etiqueta imperfecta (deuda T5-F4/F5).
- **Plan de validación por unidad obligatorio en el plan (PD-8, PD-11, G5).**
  Cada tarea declara pruebas focales, regresiones afectadas, gate de integración y
  responsable; los ciclos sin código declaran comprobaciones observables. Fuente
  canónica `planning-contract-draft.md` §4.1, **referenciada** (nunca copiada) por
  `stage-2-specification.md` (F-A de `review-t4.md`, cerrado en `afbb776`).
  Trade-off: volver obligatorio el bloque migró fixtures de T1/T2/T3, lo que el
  reviewer confirmó que **fortaleció** las garantías (los fixtures pasaron de
  saltarse los checks a ejercitarlos completos).
- **F4 (scopes co-ubicados) fuera del camino feliz de este repo (D3, T6
  condicional).** `docs/cdad-policy.json` usa `test_roots:["tests"]`; F4 solo
  muerde layouts Go/co-ubicados. Razón: no forzar una tarea que este repo no puede
  ejercitar honestamente. Trade-off: T6 **no ejecutada**; F4 queda deuda priorizada
  para el primer consumidor Go.
- **AC-7 eximido por decisión del dueño (HITL delegada).** `make validate` en
  `287f6c7` = **141 PASS / 2 FAIL**, ambos **preexistentes** al feature y no
  implicados por su diff: F011-A (drift de los mirrors de `$HOME`; irresoluble por
  regla del proyecto, que prohíbe instalar CDAD en HOME real) y F011-B (A3 marcando
  una palabra contenida en un identificador de `tests/test_role_packets.py` +
  ruido de `__pycache__`). Evidencia de promulgación válida = instalación en raíz
  aislada + `install.sh --check` PASS (303 grupos). Se descartó fabricar un verde
  local que no corresponda al medidor real.
- **AC-4 satisfecho por disposición documentada, no por caso de flujo ejecutable.**
  La regla de equivalencia se ejercita por **uso real** (suites 331/333/338/340/345/
  353/356/364 citadas, no re-ejecutadas, con verificación de identidad del árbol) y
  por **T7**; residual declarado: PD-5/PD-6 sin enforcement ejecutable.

Deuda y hallazgos (no bloquean el cierre) — consolidada en
`specs/004-003-planning-procedures/closure.md` y `review-second-look.md`:

- T1: F3 (`plan_version: null` aceptado por valor, no por presencia de clave), F4
  (path validado dos veces en la rama draft), F5 (huecos de cobertura negativa).
- T2: O1 (newline final faltante en `reviewer-plan-review.md`), O2 (=O-D:
  `handoff-prompts.md:543` invoca `plan-review` sin las 3 flags obligatorias), O3
  (redundancia estilística en `reviewer.md`).
- T4: F-C (`@validation_strategy` asimétrico en `regressions`, cubierto a nivel de
  test), F-E (`__pycache__` en el escáner A3).
- T5: F4/F5 (etiqueta y puntero de `SKILL.md` como co-dueño de la regla de dos
  intentos), F6 (comparadores concretos de equivalencia sin anclar).
- Segunda mirada: O-A (negativos T1/T2 sin tokens de diagnóstico), O-B (paridad
  instalada solo testeada para el render `plan-review`), O-C (`--contract-path`
  acepta cualquier archivo del proyecto), O-D…O-H.
- T7→003-002: F3–F6 de `review-plan-001` abiertos al dueño de 003-002 (epic-003,
  suspendido) por ser de precisión, no defectos observables.
- T6/F4 condicional para el primer consumidor Go · F011-A/B (deuda priorizada con
  dueño asignado).
- **Límite declarado:** PD-5/PD-6 (equivalencia y re-entry) no tienen enforcement
  ejecutable; la propuesta de un mecanismo futuro pertenece a 003-002/003-003.

**Lecciones de proceso**

1. **La brecha se cierra con el contrato, no con un parche.** El handoff legacy del
   architect (D8) era `prepare` rc=2 por I2; solo tras T1 (contract-kind de
   borrador) fue posible preparar el **primer paquete v2 del architect**
   (`approved-epic-plan`) y replanificar 003-002 (`evidence/t7-journey.md`).
2. **El reviewer encontró lo que el orquestador dejó pasar, y cada bloqueante tuvo
   remedio estructural localizado.** `draft-plan` abierto a todos los roles (bypass
   del invariante 4), `purpose: "approved contract"` en la emisión del borrador, y
   `packets/roles/reviewer.md` sin reconciliar (G4) — los tres reproducidos por el
   orquestador contra el código y cerrados con RED focal + GREEN.
3. **Un conflicto de oráculo se resuelve deteniéndose y reportando, no editando
   tests.** En T2 el implementer se detuvo: 4 controles honestos de T1 usaban
   `reviewer/review` + `draft-plan`, par que el pairing aprobado invalida; el
   test-writer firmó una **enmienda de oráculo** de 3 líneas (`1cb2732`) que
   **fortaleció** el oráculo (antes testificaba un escape) sin pérdida de garantías.
4. **Materializar el artefacto del rol antes de citarlo en el state.** Error R1
   (T4): `review-t4.md` se registró en `stage_history` sin materializarse; el
   re-review lo detectó como bloqueante de evidencia. Refuerzo adoptado.
5. **La reutilización de evidencia es real y verificable en este ciclo.** El
   orquestador citó suites vigentes en lugar de duplicarlas (331/333/338/340/345/
   353/356/364) con verificación de identidad del árbol — el uso que satisface AC-4.
6. **La interfaz de una superficie nueva la fija el oráculo; el orquestador la
   acepta o la desafía, no la improvisa en GREEN.** La tríada de flags de T1 se
   congeló pre-GREEN y el reviewer la restringió por rol.

**Next feature in queue:** `004-003` es la **última feature de epic-004**
(004-001/004-002/004-003). Siguiente: **cierre/integración de epic-004** (la
aprobación estratégica residual del cierre de epic es del dueño). Queda pendiente,
en el **epic-003 suspendido**, la aprobación del plan replanificado de 003-002
(su F3–F6 abiertos) y las features 003-002/003/004 — no pertenecen a este ciclo.

## 2026-10-02 — Feature: 004-002-project-execution-bootstrap (epic 004)

Cerrada el 2026-10-03. La segunda mirada (Codex) dejó 6 hallazgos registrados como deuda (`specs/004-002-project-execution-bootstrap/debt-second-look.md`; F4, alta: tests co-ubicados). La feature pasa de construir con el contexto v1 a una ejecución v2
durable y verifica el recorrido CDAD completo sobre trabajo real (PD-13):
spec.md:117-122. Suite final 329 passed (`9c92350`); el cierre cierra T7 con el
review del conjunto (review-014) y el fix de una línea F-SET-3 (`c596e7a`).
Aprobación de Memory Bank por Pablo.

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **Política de proyecto como única fuente editable de límites.** `prepare`
  resuelve la clasificación solo desde `docs/cdad-policy.json`; si falta o es
  inválida en v2, no hay defaults silenciosos (spec.md:61). Contexto: la
  clasificación dispersa entre agentes y guard hacía que scopes y reglas
  divergieran. Razón: una superficie, un hash (`policy_sha256`) y
  reconciliación explícita por decisión del dueño (PD-5); ningún rol edita la
  política (D1, PD-7). Trade-off: cada cambio de política exige reconciliar
  (bloquea prepare/resume/registro hasta hacerlo) — costo aceptado por
  auditabilidad.
- **Identidad lógica separada de las observaciones de runtime.** `execution_id`
  se conserva al cambiar rol/runtime/modelo/sesión; el intento registra
  observaciones con unknown=`null` (PD-4, PD-6; D3). Contexto: el esquema v1
  admitía un solo runtime/modelo por ejecución. Razón: la operación usa un
  runtime/modelo por rol. Trade-off: la ejecución declara `model_policy:
  ordinary` y el modelo real vive en `.cdad/executions/<id>/dispatches/`
  (dispatch-ledger.md:1-8).
- **Aplicación de la política por runtime, con alcance declarado (D5).** En
  OpenCode, agentes derivados en `.opencode/agents/` (no copias editables; I9);
  en Claude Code, el guard instalado carga la política al ejecutarse (I10). La
  evidencia separa derivación, activación por runtime y fronteras (PD-8;
  t7-live-walk.md §2–§6). Trade-off: las barreras varían por runtime y las
  diferencias se declaran antes del despacho.
- **Límites mecánicos solo cuando son obvios (decisión del dueño).** Con W-3 se
  decidió **no** perseguir una barrera mecánica de escritura en OpenCode: la
  garantía de escritura es instrucción + auditoría del orquestador
  (`git diff --name-only` contra `write_scope`). Razón: restringir de más
  bloquea trabajo legítimo (Go co-ubicado; ciclos sin código) y los tests y el
  código no siempre se separan por ruta. `private_paths` es la única barrera
  nueva, obvia y no restrictiva (owner-decision-p1-2026-10-02.md:5-12).
- **Corte C único y adopción hacia adelante (D2).** 69 paquetes v1 se congelan
  (`evidence/cut-c-v1-packets.sha256`, manifiesto `6e705726…`); la ejecución v2
  nueva es `exec-004-002-project-execution-bootstrap-001`; no hay
  `--migrate-execution` (spec.md:100-105; cut-c.md). Trade-off: dos ejecuciones
  lógicas, continuidad solo dentro de cada una.
- **Autoridad desde los registros vigentes, sin campos retroactivos.** W-1,
  W-1b y W-1c (cut-c.md §4): sin `status` deciden las condiciones de I2; sin
  `epic_id` decide `scope`; `:` y paréntesis separan tokens; coincidencia exacta
  (plan.md I2). Razón: no exigir retrospectivamente campos exclusivos de otro
  epic.

Deuda y hallazgos (no bloquean el cierre):

- W-2 (grep/glob no acotados por ruta en OpenCode) — generador global a 003-003;
  W-3 (edit/write no acotados en OpenCode 2.0.16); en Claude Code sin guard:
  architect, reviewer y scribe; `Grep` sobre carpeta padre; glob best-effort;
  bash sin acotar. Todas declaradas (guía §1 y §7; t7-live-walk.md §3,§6).
- R5: ~252 ms por llamada del guard con política v2 (N=20), aceptado sin caché
  (owner-decision-p1-2026-10-02.md:14-16).
- F-1 (FYI, review-010) y la disposición del review-014 (F-SET-1/2/4) quedan
  registradas en supervision-record.md:272-280; F-SET-3 corregido (`c596e7a`).
- Desviaciones de proceso en el ledger: intento de scribe mal despachado por
  `prepare` rc≠0 (dispatch-ledger.md:102); lectura por `bash` de `agents/**`
  denegado a `read` (supervision-record.md:254).

**Lecciones de proceso**

1. **Los límites mecánicos son moderados: más instrucción y auditoría, no más vallas.** Se cierran solo los vectores obvios; restringir de más bloquea trabajo legítimo (Go co-ubicado, ciclos sin código) — owner-decision-p1-2026-10-02.md:10-12; supervision-record.md:239.
2. **Los paquetes no deben pedir lecturas que la política deniega.** El test-writer, ante un paquete que le pedía `agents/**` denegado a `read`, leyó con `bash cat` en vez de detenerse y reportar (dispatch-ledger.md:90; supervision-record.md:254). El paquete es del orquestador: si contradice la política, el rol se detiene y reporta.
3. **Los reviewers no hacen cadenas de sondas anidadas.** El review-011 no dio dictamen porque se cortó por transporte en una cadena de `opencode run` anidadas (dispatch-ledger.md:97; supervision-record.md:268); se les pide revisar leyendo código y tests.
4. **Los ids de intento son únicos por paquete/ejecución.** I8 reutilizar un `attempt-id` con datos distintos falla sin sobrescribir; el id debe incluir el paquete (handoff-opencode-2026-10-01.md:78; plan.md I8).
5. **Las suites se corren en primer plano.** Un implementer dejó la suite en segundo plano y su turno terminó sin resultado; el orquestador esperó el `EXIT=` y lo retomó (supervision-record.md:151-152; handoff-opencode-2026-10-01.md:106-107).
6. **El orquestador valida los oráculos contra el código.** Tres defectos de oráculo los detectó así (T1:32-34, T2:86-94, T5:186-188, T6:218-221); un oráculo defectuoso es un fallo del paquete, no del rol que se detiene.
7. **Se despacha solo si `prepare` terminó con rc=0.** `prepare` del scribe falló (substage inválido `memory-bank`; el válido es `memory`) y el script despachó igual el agente con el `PACKET.md` anterior, registrando un intento inválido (dispatch-ledger.md:102).
8. **La autoridad se lee de los registros reales, sin exigir campos de otro epic.** W-1/W-1b/W-1c: `status`/`epic_id` opcionales y tokenización de `scope` (cut-c.md §4; plan.md I2).

**Next feature in queue:** `004-003-planning-procedures` (epic-004). La segunda
mirada de 004-002 (Codex `gpt-6-astra` desde 2026-10-03, o Claude Opus) sigue
pendiente (handoff-opencode-2026-10-01.md:56-58).

## 2026-09-29 — Feature: 004-001-canonical-runtime-artifacts (epic 004)

Cerrada: los 7 criterios de aceptación del spec §4 en ✅ (1–3 reproducidos
por el orquestador; 4–7 con evidencia verificada por el orquestador)
([closure.md](specs/004-001-canonical-runtime-artifacts/closure.md)). Suite
completa: 132 passed tras `5e12c0f` (corrida del test-writer; la del orquestador, 120/120 antes de la matriz); reviews 1–6 (GPT/Codex), review-7
(Claude, T6) y review externa GPT de T7 con todos los bloqueantes cerrados.
Merge y Memory Bank aprobados por Pablo (2026-09-29).

**Decisiones relevantes** (decisión + contexto + razones + trade-offs):

- **Agentes como salidas declaradas de un generador determinista.** Los 22
  archivos de `agents/` dejaron de ser copias mantenidas a mano y pasan a
  salidas de `scripts/cdad-generate.py` (stdlib) desde fuentes canónicas
  editables en `sources/` (Markdown con delimitadores), generados en staging
  con manifest por artefacto (sha256, fuentes, comando de regeneración,
  stack/perfil). Contexto: ADR-011 (capacidades por rol) y enmienda C0
  ("simplificar antes de generar"). Verificado: regenerar (optimus, odoo,
  ambos runtimes) produce salidas idénticas a los 22 archivos (criterio 2).
  Trade-off de mantenimiento (D2 del informe C0, sustituido por la enmienda
  C0: los conteos son diagnóstico, no gate): superficie editable hoy = 765
  líneas de `sources/` + 1.088 del generador = 1.853, frente a 2.697 de las 22
  copias a mano de la baseline — la baseline PD-13 (medida antes de la
  primera generación, con `rtk rg -c` mecánico porque `rtk wc` estaba
  bloqueado; contraste externo coincidió dígito a dígito; dispuesto en el
  PD-17 de T1) y el techo de bytes del bloque estático (PD-19, 12.000,
  parametrizado) quedan registrados para vigilar ese costo.
- **Separación generación/instalación real:** el instalador despliega solo
  desde staging y **nunca lee `sources/`** (PD-18; `tests/test_install_ownership.py`),
  con manifest de propiedad (PD-6 primera instalación no borra nada, PD-7
  conflicto de hash reportado en dry-run, PD-8 uninstall borra solo lo propio).
- **Política bash permisiva con barreras por ruta:** la política por rol se
  deriva de la fuente canónica con efecto declarado por regla (PD-1,
  aterrizaje A, review-4 approved); las listas FORBIDDEN se retiraron por
  decisión del dueño (`80f9b90`) y las assertions por texto se sustituyeron
  por comprobaciones semánticas con tabla de trazabilidad (PD-10, T7a:
  `33bf757`, `c9f1448`, `tests/pd10_permission_semantics.py`). Las barreras
  de path se retienen y se prueban en ambas direcciones (PD-12; ejecución
  real del `path-guard.sh` instalado: exit 2 / 0).
- **Orquestación con construcción delegada y verificación propia:** las 7
  tareas (T1–T7) se construyeron por roles CDAD en sesiones aisladas con
  registro de supervisión PD-17 en
  `epics/epic-004-single-source-planning/c0-dispatch-record.md` (incluida la
  consolidación de T4/T5); los tres validadores quedaron en PASS o sus
  assertions migradas con trazabilidad (criterio 3).

Deuda y hallazgos (no bloquean el cierre):

- Deuda técnica con foco en 004-002 (closure §Observaciones): `install.sh`
  exige un directorio `agents/` junto al script aunque despliega solo desde
  staging (PD-18 intacto); derivar las raíces de implementación desde
  `path_policy` (hoy read/grep del test-writer solo ocultan `src/**` y
  `lib/**`); `steps: 300` no se probó forzando un bucle.
- Desviaciones de disposición registrada (PD-17): salidas de ámbito para
  esquivar obstáculos (instalación en el HOME real en T6; `git stash` sobre
  estado compartido en T7 — sin pérdida) dispuestas con principio explícito
  en los paquetes + árbol limpio antes de despachar + verificación posterior,
  sin barreras nuevas; incidente de bucle del orquestador en T2 (~60
  reintentos de `rtk pytest`, causa raíz de invocación) registrado como
  insumo de 003-003; log vivo saneado por identidad del dueño (`61a6af3`).
- **Advertencia de alcance:** el recorrido vivo de capacidad (5 roles, 39
  llamadas, 0 denegaciones, `evidence/t7-live-walk.md`) demuestra capacidad
  operativa por el **camino legacy** (sin paquetes); el ciclo con paquetes y
  contexto reducido se comprueba en 004-002 sobre trabajo real
  (closure.md §Observaciones).

Próxima feature en cola: **004-002** — verificación del recorrido CDAD
completo con paquetes y contexto reducido, sobre trabajo real. Consume la
fricción medida y entregada a 003-003 por 004-001 (criterio 6:
`epics/epic-003-context-efficiency/friction-intake-004-001.md`, `95a5a62`).

## 2026-09-29 — Ciclo liviano: mapa `read` del test-writer + techo `steps` (OpenCode)

Revisión de sesiones OpenCode (24→29/09): shell denegado 2409/2740 llamadas, `read` del
test-writer 0 ok/36 denegadas, un bucle de 2073 reintentos idénticos. Bash permisivo
(80f9b90) ya estaba; este ciclo quita el catch-all deny del `read` y agrega `steps: 300`
(declarado en `sources/agents/adapters/opencode.md`, leído por el generador). Detalle,
evidencia antes/después y follow-ups en
`docs/specs/opencode-read-map-and-steps-2026-09-29/`. Pendiente fuera de este ciclo:
`/tmp` sin inodos en la máquina (requiere root) y derivar las raíces de implementación
desde `path_policy` (004-002).

## 2026-09-24 — Autonomía supervisada y enmienda C0

Por instrucción del usuario se adoptó
[ADR-011](adr/ADR-011-autonomia-supervisada-limites-proporcionales.md):
encargos claros, capacidades suficientes, límites proporcionales y verificación
al re-entry. Cambia la política objetivo, no los permisos instalados.

La [enmienda C0](epics/epic-004-single-source-planning/c0-amendment-supervised-autonomy-2026-09-24.md)
incorpora R1–R3 del dictamen y contiene el siguiente encargo para GLM: spec/plan
004-001 que simplifica antes de generar. Tres ciclos, sin nuevo epic/agente.
003-002/003/004 reciben ajustes de evidencia, fricción/incidentes y continuidad.
La metodología, README y systemPatterns distinguen la decisión vigente de
las configuraciones pendientes de migración. No se modificaron skills/agentes,
código, tests, instalaciones ni state. 003 sigue activo sin feature; 004 es
propuesta. No se volvió a probar runtime ni se declara una suite nueva verde.

---

## 2026-09-23 — Handoff a GLM y propuesta de reestructuración

El usuario quiere continuar el desarrollo con GLM y reservar GPT/Claude para
análisis profundo y revisión. Se documentó el
[punto de entrada](handoffs/2026-09-23-glm-continuation.md), con autoridad,
restricciones, lectura gradual y checkpoints. No se implementó ni instaló nada.

Propuesta pendiente de revisión/aprobación:
[epic 004](epics/epic-004-single-source-planning/plan.md), antes de 003-002,
con tres ciclos candidatos: fuentes/artefactos por runtime, política del
proyecto/bootstrap de ejecución y procedimientos de planificación/revisión.
No se propone un planner nuevo de entrada. Su
[contrato de procedimiento](epics/epic-004-single-source-planning/planning-contract-draft.md)
define cobertura global, productores/consumidores, contexto, dependencias e
integración; se aplicará sobre trabajo pendiente, sin repetir desarrollos.

003-001 y 003-005 siguen cerradas; 003-002/003/004 pendientes. Se corrigieron
handoffs que presentaban 001 abierta y Sol como selección futura obligatoria;
el handoff previo se conserva como historia. El state sigue en epic 003,
sin feature activa. El nuevo epic no está activado ni aprobado.

Próxima acción: GLM verifica entorno/estado y prepara inventario + paquete C0
para revisión GPT o Claude. Antes de construir, registrar la autoridad del
nuevo proceso; no copiar la delegación histórica de Codex como si nombrara GLM.
La política de aceptación de modelo único de 003 requiere reconciliación
explícita con el reparto actual de construcción antes del recorrido final.

---

## 2026-09-18 — Feature: 003-005-claude-code-packets (epic 003)

Los paquetes de 003-001 pasan a ser utilizables. `cdad_packet.py prepare`
arma en una sola llamada REQUEST.json, PACKET.md y el binding del state
(`execution` + `active_packet`), y su stdout es el prompt de Task. Los 10
agentes de rol de Claude Code aceptan el camino de paquete; los odoo siguen
cargando sus skills de dominio. `handoff-prompts.md` documenta el template de
`.cdad/execution.json` (modo `ordinary`, una vez por feature).

Lecciones:
- **Un contrato sin productor no se usa.** 003-001 validaba paquetes que nadie
  generaba: `validate-state` fallaba contra el state real de este repo. Una
  feature de contrato necesita un smoke contra el state real, no solo fixtures.
- **Rollback solo sobre lo propio.** La review encontró que el rollback borraba
  el directorio de otro proceso y que un fallo de serialización dejaba
  archivos a medias. Regla: serializar todo antes de la primera escritura y
  deshacer solo lo que creó la propia invocación.
- **Los ids que se usan como componentes de path deben ser nombres planos**
  (`feature_id` → packet_id → directorio).

Pendiente (hardening): el hook `test-writer-bash` bloquea todo comando que
empiece con `python3` (hay que invocar `pytest` directo); `mkdir(parents=True)`
puede dejar directorios intermedios vacíos; los paquetes de architect exigen
el plan de un epic; las transiciones de `active_packet` después de `prepared`
siguen siendo manuales.

Instalación real (2026-09-19): `install.sh` sin `CDAD_INSTALL_ROOT` también
copia a `$HOME/agents` y `$HOME/skills` (el layout público de 003-001 pensado
para fixtures), carpetas que ningún runtime lee. Workaround usado: instalar en
una raíz aislada y copiar solo a los destinos de cada runtime. Además, al no
usar `--delete`, quedan archivos renombrados por la traducción
(`odoo-expert/references/evidencia-y-calidad.md`). Ambos van al bucket de hardening.

---

## 2026-09-18 — Feature: 003-001-role-packets (epic 003)

Cerrada la primera feature del epic de eficiencia de contexto: paquetes
canónicos por rol/subfase (renderer y validador `scripts/cdad_packet.py`,
13 parejas rol/subfase, schemas de state/execution, métricas) y entrypoints
instalados. Ciclo largo: 3 POST-AUDIT (el último aprobado) y 4 reviews; el
bloqueante B4 (el instalador no debe poder usar como destino su propio repo
fuente) necesitó tres iteraciones RED/GREEN: destino directo, luego
`CDAD_SKILL_EXTRA_DIRS` y por último la invocación por symlink.

Decisiones y lecciones:
- **Comparar solo rutas canónicas:** un guard de solapamiento que canonicaliza
  un lado y deja el otro lógico se puede evadir con symlinks.
  `SCRIPT_DIR` usa `pwd -P`, y el comentario en install.sh:19 lo marca como
  requisito de seguridad.
- **Los validadores corren con `CDAD_INSTALL_ROOT` aislado:** contra la
  instalación real, `install.sh --check` falla (F011, preexistente). No se
  repara la instalación real para ocultarlo.
- **Cambio de runtime:** 001 empezó con Codex (roles `gpt-5.6-sol`, HITL
  delegado) y el cierre (GREEN, review focal y Memory Bank) se hizo en Claude
  Code con los sub-agentes `cdad-*`. Para 002–004 hay que decidir el runtime al
  abrirlas.

Estado final: suite `pytest tests` 33/33, 3 validadores en PASS en raíz
aislada, review-4 APROBADO-COMENTARIOS (0 bloqueantes). Commits: RED B4 final
`da48f3c`, GREEN `641f3b8`.

Pendiente (bucket de hardening):
- Invocar `install.sh` por symlink al archivo falla de forma segura
  (`cdad-models.sh` missing) pero no está soportado; se resolvería con
  `readlink -f` sobre `BASH_SOURCE`, más un test.
- No se verificó `pwd -P` en macOS/BSD.

---

## 2026-09-13 — Feature: cdad-010-opencode-permissions

Cerrada la feature que reparó la delegación a los sub-agentes `cdad-*` en
OpenCode (rota por interacción de 3 capas: clasificador del plugin que ignora
allows específicas, huecos de allowlist + wrapper rtk, y el hack `write: ask`
top-level inerte). 10 agentes task-ables (5 base + 5 odoo), bloques de
permisos autocontenidos (catch-all primero, específicas después — semántica
findLast), cero `ask` en runtime (fail-fast deny), allowlists bash por rol con
pares `X*`/`rtk X*` derivadas del stack detectado (`scripts/cdad-bash-allowlist.sh`
+ `install.sh`, P5), docs de delegación corregidos (P6) y ADR-009. Copia
huérfana `cdad-test-writer-local.md` (fuera del repo, filtraba a `src/`)
eliminada.

Decisiones clave:
- **Palanca anidada, no top-level (enmienda P1):** `permission.write: ask`
  dentro del bloque `permission:` — el KNOWN_KEYS del clasificador no incluye
  `write` top-level (probe: palanca top-level inerte, agente colapsa a
  read-only y `task` lo rechaza); anidada, el clasificador la lee y el runtime
  NO la evalúa (cero `permission=write` en 124MB de logs). La enmienda nace de
  una desviación registrada: el commit `5f9f4d2` mezcló el fix de agentes con
  la edición del assert A1 de run-checks.sh fuera de rol (AP-4) — bajo la
  política del dueño queda como precedente: violación así futura = tarea NO
  cumplida.
- **Eliminación de `"find *": allow` (H3):** vector directo de
  escritura/ejecución (`find -delete`, `-exec sh`) en los 6 roles read-only
  cuya allowlist declara "solo lectura". Navegación preservada (`ls *`, `wc *`,
  `pwd`, `cd *`, pares `rtk find*` en lectores).
- **Política de enforcement del dueño (Capa 2, Pablo):** bloquear vectores
  directos y evidentes, no bypasses hipotéticos; la expectativa se documenta en
  skills/procedimientos; agente que cumple violando el protocolo sin motivo
  válido = tarea NO cumplida. Definición operativa (N3): "vector directo y
  evidente" = demostrable con un probe de una sola invocación con output
  pegado (Regla de Oro) — el episodio N1 lo demostró: dos sesiones dieron
  veredictos opuestos sobre el mismo matcher y el que tenía probes pegados
  tenía razón.

Estado final: run-checks.sh 217 PASS / 0 FAIL (RED 42/132 → 174/0 → 184/31 →
215/0 → 217/0 con assert de orden findLast N2), 3 validadores en PASS
simultáneo, matriz de probes G1-G16 ejecutada post-restart desde sesión
primaria con evidencia pegada (G9 con enmienda justificada: `go version`
DENEGADO es diseño correcto; G14 con re-test tras misreport del modelo), cero
prompts `ask` y cero `permission=write` en logs, review APROBADO-COMENTARIOS
(2 pasadas). Commits: rango `b352bf6..a1d37a7` (27 commits; highlights:
`f36f8c7` P1-P4, `b0027bd` P5, `5f9f4d2` palanca anidada, `a45219c` fixes
H3/H4, `a1d37a7` N2).

Pendiente (bucket de hardening, NO fixeado acá):
- Re-evaluación de matching de comandos compuestos con la premisa corregida
  (N1: el matcher evalúa por segmento — `cd X && <arbitrario>` NO bypassa; el
  "hardening de matching" original probablemente ya no es necesario).
- `"find *": allow` en la config global del usuario (`opencode.jsonc`) —
  misma clase que H3, fuera de alcance por invariante de no-modificación (N4).
- Solape de globs de dominio Odoo (intersección entre globs odoo y globs
  genéricos de tests colocados en las variantes) — revisar en hardening.

---

## 2026-09-04 — Fix: path-guard reconoce tests colocados (sin ciclo formal)

Fix en `scripts/claude-code-path-guard.sh` (commit `0fd023f`), detectado en
un proyecto cliente (backend Go + extensión JS) y reportado por Pablo. El
guard asumía tests en
`tests/**` dedicado, pero Go EXIGE tests en el mismo paquete/directorio
(`*_test.go`, requisito del compilador) y JS/TS coloca `*.test.{js,ts}`
junto al módulo. Consecuencias corregidas en AMBOS lados:

- **test-writer-write / test-writer-odoo-write**: la allowlist de escritura
  ahora acepta tests colocados (`**/*_test.go`, `**/*.test.{js,ts,mjs,cjs}`,
  `**/*.spec.{ts,js}`, `**/test_*.py`), además de `tests/**` y `**/tests/**`.
  Sin esto, el rol quedaba sin NINGÚN path escribible en un repo Go.
- **implementer / implementer-odoo** (lado inverso, no reportado — detectado
  en revisión): la blocklist ahora incluye los mismos patrones. Sin esto, el
  implementer podía editar tests colocados y romper silenciosamente el gate
  anti-trampa.
- **test-writer-read**: excepción de lectura para tests colocados bajo
  `src/**`/`lib/**` (el test-writer debe poder leer la suite que edita).
- **Factorización**: array `TEST_FILE_GLOBS` + `is_test_file()` como fuente
  única usada por ambos lados.

Verificación: batería de 19 casos por rol (bloqueos/permisos, ambos layouts,
variantes Odoo) — 19/19 PASS. Copia instalada (`~/.claude/cdad-scripts/`)
redesplegada e idéntica a la canónica.

**Deuda de proceso (documentada, no oculta):** el fix se aplicó inline y
antes del spec — bypass del ciclo CDAD (Pablo pidió ciclo light a mitad de
camino; se decidió no retroactivar y solo documentar). La batería de 19
casos no vive como test permanente en `tests/` — si el guard vuelve a
tocarse, incorporarla como RED formal de esa feature.

## 2026-09-02 — Epic: epic-002-cdad-audit-fixes (12 features, cerrado)

Cerrado el epic que corrige los hallazgos de
`findings/audit-consistencia-2026-09-02.md` (auditoría completa de
metodología, agentes OpenCode/Claude Code y skills, pedida por Pablo).
Delegación HITL explícita para todo el epic (spec approval, priorización,
Memory Bank) — ver `docs/.cdad-state.json` campo `hitl_delegation`.

Decisiones relevantes:
- **B1 (bash como fuga del aislamiento)**: calibrado como defensa en
  profundidad, no reescritura estricta — decisión explícita de Pablo antes
  de ejecutar: *"la combinación de barrera estructural parcial + conductual
  está funcionando bastante bien"*. La allowlist de bash cierra la fuga de
  contenido (cat/head/tail/rg) preservando TODO lo legítimo (tests, lint,
  git commit propio, navegación) — ningún rol perdió capacidad real.
- **Perfil `basic`**: es el más usado por Pablo (costo de tokens) y su
  comportamiento NO cambió — el fix fue puramente documental (dejar de
  afirmar el anti-bias como garantizado ahí, cuando ADR-007 ya documentaba
  la excepción).
- **RED verifica requerimiento, no cobertura**: refuerzo explícito pedido
  por Pablo — un test-writer no debe sobre-especificar más allá del spec
  (tests carísimos/imposibles de satisfacer, tiempo y tokens perdidos).
  Agregado a SKILL.md, stage-3-tdd.md, y a los 4 agentes test-writer.

Deuda técnica detectada:
- Esta misma entry es la primera desde cdad-004 (2026-09-02) —
  activeContext.md no tenía entries para cdad-005..009 pese a estar `done`
  en progress.md. No se backfillea acá (fuera del scope de este epic); si
  hace falta detalle de esas 5 features, está en sus commits y en
  `docs/epics/epic-001-superpowers-gaps/closure.md`.
- Deuda ya registrada sin cambios: CI del repo, dogfood pendiente de varias
  features (ver progress.md Queued).

Próxima feature en cola: ninguna decidida — Pablo define.

## 2026-09-02 — Feature: cdad-004-lint-gate

Cerrada feature que incorpora `make lint` (pre-commit-vauxoo) como 4º target
del contrato odoo-make-env y como evidencia obligatoria en review/gates Odoo.

Decisiones relevantes:
- Lint con `uvx pre-commit-vauxoo==8.3.18`, SIEMPRE `--no-overwrite` (la
  bootstrap de configs es del proyecto, nunca del agente), corre en host,
  autofixes deshabilitados.
- El lint es evidencia mandatory en review Odoo; los hallazgos W/C siguen
  advisory (split mandatory/advisory intacto).
- Fix colateral: assert stale de cdad-003 (odoo-dev-methodology retirado en
  d9dc599, test nunca actualizado) → `assert_file_not_has`.

Deuda técnica detectada:
- CI inexistente en este repo (suite bash local hace de gate) — registrar en
  progress.
- H3/dogfood: `make lint` sin validar end-to-end contra un addon Odoo real.
- Runtime `delegate` (read-only) falló 8/8 por timeout en esta sesión —
  revisar infraestructura antes del próximo epic.

Próxima feature en cola: epic `superpowers-gaps` (5 features, orden
propuesto: G1 recepción de feedback → G5 git safety → G3 debugging → G4
planning → G2 despacho paralelo).

## 2026-09-02 — Bootstrap del proyecto

Memory Bank inicializado durante el cierre de cdad-004-lint-gate (primera
feature del repo con ciclo CDAD completo: spec → RED 10/10 → GREEN → review
two-layer → merge).

Pendientes para completar manualmente:
- CI del repo (GitHub Actions) — deuda registrada en progress.md.
