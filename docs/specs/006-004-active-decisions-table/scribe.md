I have read all declared inputs and evidence. Here are the three Memory Bank drafts.

---

# BLOQUE 1 — Entrada para `docs/activeContext.md`

*(Se inserta como **primer H2** del archivo, debajo de la introducción; las entradas más recientes van arriba.)*

```markdown
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
```

---

# BLOQUE 2 — Fila para `docs/progress.md`

*(Se inserta como **primer ítem** de la sección `## Done`; la sección `## In progress` queda `_(ninguna)_`.)*

```markdown
- **006-004-active-decisions-table** (2026-10-22, epic 006) — sexta feature de
  `epic-006-opencode-concurrency`: **la tabla de decisiones vigentes del proyecto** y, con ella, la
  **distribución de la decisión que gobierna el trabajo siguiente**. Una decisión aprobada viaja
  **en el encargo** del rol al que gobierna (campo opcional `current_decisions`, declarado con
  `prepare --current-decision <JSON>` repetible; la sección `## Current decisions` se emite **sólo
  con filas** y sin ellas el render es **byte-idéntico** dentro de una misma revisión), y con ella
  el **principio de general antes que específico** (enmienda 005) encuentra su **casa única** en
  `skills/cdad-cycle/references/design-principles.md` y llega al **architect** (considerar
  alternativas generales y específicas y explicar el criterio) y al **reviewer** (evaluar
  consecuencias reales, con el límite de que la falta de una abstracción no es por sí sola un
  defecto) como **deber de rol**, sin re-enunciar el texto. **Contrato:** `spec.md` sha256
  `ee88d426…` (PD-1..PD-13, INV-1..INV-16, DEC-1..DEC-16, L-1..L-7, D-1..D-6) + `plan.md`,
  aprobados el 2026-10-20 por el orquestador bajo la **HITL delegada del epic** tras
  `plan-review-001..004` (B-1..B-4 cerrados). **Producto (rango `86cb942..a815f9b`: 67 commits, 65
  archivos, +14801/−13; de ellos 21 de producto, +435/−4, y `tests/` 7 archivos nuevos, +5301/−0;
  último commit de producto `fc1179b`):** U1 la fila declarada, su **forma cerrada de seis claves**
  y el **tope de 32 fail-closed** (la fila debe **nombrar al rol del paquete**; una fila `obsoleto`
  **no es admisible** en un paquete; `file` debe existir; `roles` en vocabulario cerrado) → U2 la
  sección aditiva del render, entre `## Contract` y el bloque de plan-task → U3 el principio: una
  casa y las dos obligaciones (fuente del rol + bloque estático + agentes regenerados) → U4 la tabla
  y su **upkeep del orquestador** (`stage-5-merge.md` §5.4, **sin** tocar el exit gate), la
  **regla general del CAS por digest base** y la reconciliación por **re-despacho**
  (`re-entry.md`) → U5 la **siembra** de este repo: «Decisiones vigentes» como **primer H2** de
  `docs/systemPatterns.md` con 26 filas (25 `vigente`, 1 `obsoleto`; 8 `Proposed` excluidos) y el
  **ADR-034** materializado con estado aprobado → U7 el **validador permanente de invariantes
  duraderas**, que **no nombra ningún ADR** ni fija ningún conteo (aprobar un ADR nuevo o reemplazar
  cualquiera **no obliga a tocar los tests**) → U6 **recorrido de aceptación real** (proyecto
  descartable, **sin despliegue a HOME**; E1..E7 y V-5 **cumplen**, incluida la **cadena del CAS**
  completa: rechazo por conflicto → re-despacho sobre la base nueva → materialización que conserva
  la fila del orquestador) → **B-1** la **plantilla nace sin decisiones** (fila de ejemplo fuera de
  la tabla, en prosa: un proyecto sin ADR ya no queda bloqueado). **Review formal: 2 bloqueantes /
  3 opcionales / 1 abstención** — **B-1** cerrado por RED/GREEN (`4d71ccc` → `fc1179b`);
  **B-2** resuelto por el **orquestador**, que auditó el diff (una línea) y adoptó la corrección
  bajo su propia autoridad (el upkeep de la tabla es suyo, ADR-003), sin reescribir historia ni
  cambiar el oráculo. **Gates:** `make validate` **Assert PASS: 182 / Assert FAIL: 1** (el único
  FAIL es **F011**, deriva ambiental de la copia instalada, **DT-8** preexistente); **suite de
  cierre: no ejecutada** (la corre una vez quien cierra, política declarada en el paquete).
  **Despliegue: NO hay despliegue en HOME**, por orden del owner (hay una sesión activa en
  OpenCode que no se debe tocar) ⇒ la copia instalada no contiene la feature. **Deuda:** **O-1**
  (la pertenencia a `docs/adr/` se comprueba sólo por prefijo), **O-2** (el ADR-034 conserva marcas
  residuales de borrador), **O-3** (falta el bloque U3 pedido en el validador bash; los tests
  Python sí cubren la fuente única), **W-U6-1** (fidelidad del scribe: el CAS protege la
  concurrencia, no la fidelidad ⇒ la salida es revisar el diff antes de aprobar), **W-U6-2**
  (**a verificar**: el adaptador re-despachó un paquete que ya tenía entrega completa y recibo
  durable; causa no investigada), **W-U6-3** (el adaptador entrega una sola parte `role-report`,
  cuya raíz permitida es la carpeta de la spec ⇒ materializar hacia el Memory Bank exige un
  descriptor propio del orquestador), `scope_validation: unknown` (deuda heredada de 006-005: el
  caso de B-2 es una instancia más) y la deuda declarada de la spec (**L-1** compatibilidad entre
  revisiones, **L-3** completitud de la tabla, **L-4** verificación del `reference`, **L-5** exit
  gate de stage 5, **L-6** esquema del request, **L-7** el producto no verifica la base del CAS).
  **Pendientes de cierre:** suite completa y redespliegue en HOME. **El epic NO se cierra: 6/6**
  features hechas ⇒ no queda ninguna feature en cola; el siguiente trabajo es el **cierre del
  epic**, previa la suite de cierre y el redespliegue.
```

---

# BLOQUE 3 — Patrones nuevos para `docs/systemPatterns.md`

*(Texto **fuera** de la tabla «Decisiones vigentes»: **no se agrega ni se cambia ninguna fila** — la
tabla es del orquestador. Se propone un H2 nuevo **después** de la sección `## Decisiones vigentes`
(tras su bloque `**Nota.**`) y **antes** de `## Capas y boundaries`.)*

```markdown
## Decisiones vigentes: la tabla y su distribución

La sección «Decisiones vigentes» de este archivo (en la plantilla del Memory Bank,
`## Current decisions`) es el **índice de las decisiones del proyecto**: una fila por decisión, con
su archivo, su estado, un resumen de una línea, los roles que deben consumirla y la referencia
donde vive su regla. Este bloque describe **cómo se mantiene, cómo viaja y qué la valida**; la
tabla en sí la mantiene el orquestador.

### La fila y su forma

- **Forma cerrada de seis claves**: `file` (ruta relativa al proyecto, **debe existir**), `state`
  (`vigente` | `obsoleto`), `summary` (**una línea**), `roles` (**no vacío**, vocabulario cerrado:
  los cinco roles delegados más `orchestrator`), `reference` (dónde vive la regla que la decisión
  implanta) y `superseded_by` (**condicional**: exigido si `state` es `obsoleto`, prohibido si es
  `vigente`). Cualquier otra clave se rechaza nombrando la clave. La **misma** forma sirve para el
  documento y para el request ⇒ el orquestador construye el request desde la tabla **sin
  traducción**.
- **El estado lo declara quien mantiene la tabla.** No se re-deriva del texto del ADR: el estado de
  un ADR **no es derivable** (varios vocabularios y formatos, reemplazos parciales). La columna es
  una **declaración**, y el upkeep es **procedimiento**, no una operación de producto.
- **Una fila `obsoleto` conserva su sitio** (la historia) y **no se distribuye**: la decisión
  reemplazada gobierna a nadie.
- **El CLI no parsea este documento.** El producto valida la **forma** de la fila; el proyecto
  decide **qué** filas existen y **qué** dice cada una. Acoplar el CLI al formato del documento
  ataría el byte del paquete al estado de la tabla.

### La fila viaja en el encargo, no por el alcance

- `prepare --current-decision <JSON>` (**repetible**) declara filas; quedan en
  `request.current_decisions`, en el **orden declarado**, y el render emite la sección
  `## Current decisions` **sólo** si hay filas (entre `## Contract` y el bloque de plan-task).
  Sin el campo —o con la lista vacía— el render es **byte-idéntico** al vigente **dentro de una
  misma revisión** (garantía intra-revisión).
- **Toda fila declarada debe nombrar al rol del paquete** (fail-closed, nombrando la fila y el
  rol): una fila que no concierne al rol **no viaja**, ni por descuido. Un rol sin filas aplicables
  recibe un paquete byte-idéntico al de hoy.
- **Tope de 32 filas por paquete, fail-closed**, con salida: el diagnóstico nombra el número
  declarado y el tope. El 32 es un **número declarado**, no un tope atado al inventario ni
  derivado de él.
- **Las filas no aprueban nada**: viajan con `semantic_status: pending` y `approval_effect: false`.
  Una decisión vigente **no** es una aprobación (son hechos distintos).
- **El alcance por defecto no cambia**: el test-writer **sigue** sin poder leer `docs/`; las
  decisiones le llegan **dentro** del paquete.

### Las dos responsabilidades sobre la tabla

- **El orquestador la mantiene** (`references/stage-5-merge.md` §5.4): al aprobarse un ADR, agrega
  la fila (con prefijo `docs(memory):`); si el ADR reemplaza a otro, marca la fila anterior como
  `obsoleto` **conservándola** con su reemplazo. El **exit gate de stage 5 no cambia**: el upkeep
  es un paso de la decisión, no una casilla nueva del gate.
- **El reviewer la revisa** (`references/stage-4-review.md` es el **dueño canónico** de esa
  comprobación; la fuente del rol y su bloque estático la referencian y no la copian): **alineación**
  —cada fila apunta a un archivo que existe en `docs/adr/` y el conjunto de filas es coherente con
  el directorio— y **respeto** —el cambio respeta las decisiones vigentes que gobiernan su rol, las
  filas que el paquete le lleva—. Una fila desalineada es un **hallazgo** con `file:line`,
  veredicto y condición de cierre verificable, **no** una puerta.

### El CAS es contra la base, y reconciliar es re-despachar

- El digest declarado en la autorización (`expected_previous_sha256`) es **siempre el digest
  base**: la versión del destino sobre la que el rol preparó la propuesta, **nunca** el digest
  actual del destino. Comparar contra el actual **no** detecta una propuesta obsoleta: **pisa** el
  cambio del otro escritor.
- Ante conflicto («current digest does not match expected_previous_sha256 (CAS): refusing to
  overwrite») **no** se sobrescribe, **no** se fusiona a mano y **no** se actualiza el digest
  esperado para forzar el paso (eso borra el cambio del otro escritor). La salida es
  **re-despachar al rol con un paquete nuevo sobre la base nueva**, para que la propuesta se rehaga
  sobre lo que ahora existe; el documento final conserva lo escrito por los dos escritores y la
  evidencia identifica los bytes aplicados.
- **La tabla tiene dos escritores**: el orquestador (que escribe sus filas directamente en `docs/`
  con su commit y no pasa por el CAS) y el scribe (cuya propuesta llega por materialización, sobre
  la base que el orquestador registró al preparar su paquete).

### El validador permanente lleva invariantes duraderas

- El bloque que mira la tabla viva comprueba **propiedades de coherencia**: cada fila apunta a un
  archivo que **existe bajo `docs/adr/`**; toda fila `obsoleto` nombra un reemplazo que **existe**;
  todo `roles` está en el vocabulario cerrado; **ningún** archivo apuntado por una fila re-enuncia
  el texto normativo del principio; y la nota declara que el estado lo declara quien mantiene la
  tabla.
- El bloque **no contiene ningún conteo** (ni de filas, ni de vigentes, ni de obsoletas, ni de
  excluidas) **ni ninguna comprobación por identidad**: **no nombra ningún ADR** y no exige el
  estado, los roles ni la referencia de ninguna fila en particular ⇒ **aprobar un ADR nuevo o
  reemplazar cualquiera de ellos no obliga a tocar los tests**. El inventario sembrado (26 filas, 8
  `Proposed` excluidos) y la ficha de una fila concreta son **evidencia puntual**, no un oráculo
  permanente.
- El **cierre verificable** del comprobador es un caso descartable de tres, **con el mismo
  comprobador y sin editarlo**: **agregar** un ADR aprobado **pasa**; **reemplazar** una decisión
  (fila `obsoleto` + fila sucesora `vigente`) **pasa**; una fila con archivo **inexistente**
  **falla**.

### El principio de general antes que específico: una casa, dos deberes

- El texto normativo del principio **y su límite** viven en **un único archivo** del skill
  instalable: `skills/cdad-cycle/references/design-principles.md`. Quien necesite el texto exacto,
  lo lee ahí; el resto de las superficies lo **referencian** y **no lo re-enuncian**.
- El **deber del architect** y el **criterio del reviewer** son *duty*, no principio: viven en la
  fuente de cada rol y en su bloque estático de paquete, con un **puntero** al archivo canónico
  (el bloque estático también los lleva porque, en la ruta de paquete, el rol **no** carga el
  skill). El procedimiento del deber del reviewer sobre la tabla vive en su referencia canónica.
- El **límite** del principio es parte del principio: está escrito **junto a él**, en el mismo
  archivo, y se cita en las dos superficies del reviewer. La falta de una abstracción **no es, por
  sí sola, un defecto**.
- El ADR que registra la decisión **no re-enuncia** el texto del principio: lo referencia, igual que
  lo referencia la fila de la tabla.

### La plantilla nace sin decisiones

- La sección de la plantilla tiene encabezado y separador y **cero filas de datos**; la forma de la
  fila se explica **en prosa, fuera de la tabla** (una línea que empieza por `|` la leería el
  comprobador como una decisión y fallaría por archivo inexistente).
- Un proyecto **sin** `docs/adr/` **no queda bloqueado**: `prepare` de cualquier rol da rc=0 y sin
  sección, y el render con la lista vacía es byte-idéntico. La sección vacía **no** es una fila.
```

*(Además, fuera de la tabla: actualizar la línea final del archivo —`Última actualización: 2026-10-20 (006-005)`— a `Última actualización: 2026-10-22 (006-004)`.)*

---

# Informe de rol (evidencia)

**Rol:** scribe · subfase `memory` · paquete `006-004-active-decisions-table-scribe-memory-001` · contrato `approved-feature-spec` sha256 `ee88d4263e880553292aeffd1a07b877c20c6c4f1cfb63866a0f5bf4278e43e3` (coincide con `docs/specs/006-004-active-decisions-table/spec.md`).

**Archivos modificados por este rol: ninguno.** `write_scope: []` — no escribí en el repo; los tres bloques anteriores son texto de borrador para que el orquestador los materialice tras la aprobación del usuario.

**Comandos ejecutados (sólo lectura):**

```sh
ls -la docs/specs/006-004-active-decisions-table/ ; ls -la docs/adr/ ; ls -la docs/epics/epic-006-opencode-concurrency/
git status --short ; git branch --show-current ; git log --oneline -15
head -80 docs/activeContext.md ; grep -n "^## " docs/activeContext.md | tail -40
sed -n '190,464p' docs/activeContext.md
head -60 docs/progress.md ; grep -n "006-00" docs/progress.md | head -30
head -80 docs/systemPatterns.md ; grep -n "^## " docs/systemPatterns.md ; sed -n '84,125p' docs/systemPatterns.md ; tail -30 docs/systemPatterns.md
grep -n "^#\{1,3\} " docs/specs/006-004-active-decisions-table/spec.md ; sed -n '42,344p' docs/specs/006-004-active-decisions-table/spec.md
grep -n "^#\{1,4\} " docs/specs/006-004-active-decisions-table/plan.md ; sed -n '52,121p;214,243p' docs/specs/006-004-active-decisions-table/plan.md
cat docs/adr/ADR-034-principio-general-antes-especifico.md
cat docs/specs/006-004-active-decisions-table/review.md ; cat docs/specs/006-004-active-decisions-table/u6-acceptance.md
cat docs/specs/006-004-active-decisions-table/b1-red.md ; cat docs/specs/006-004-active-decisions-table/b1-green.md
for f in u1-green.md u2-green.md u3-green.md u4-green.md u7-green.md u5-seeding.md; do sed -n '1,40p' docs/specs/006-004-active-decisions-table/$f; done
sed -n '355,427p' docs/epics/epic-006-opencode-concurrency/execution.md
git log --oneline 86cb942..HEAD ; git diff --stat 86cb942..HEAD
git diff --shortstat 86cb942..HEAD -- skills sources agents build install.sh scripts   # 21 archivos, +435/-4
git diff --shortstat 86cb942..HEAD -- tests                                     # 7 archivos, +5301/-0
git diff 86cb942..HEAD -- skills/cdad-cycle/references/re-entry.md skills/cdad-cycle/references/stage-5-merge.md skills/cdad-cycle/references/stage-4-review.md
cat skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md ; cat skills/cdad-cycle/references/design-principles.md
awk 'NR>10 && /^\| `docs\/adr\// {c++} END{print c}' docs/systemPatterns.md   # 26
```

**Salidas usadas (verificadas, no estimadas):** 26 filas en la tabla (25 `vigente`, 1 `obsoleto`); `## Decisiones vigentes` es el primer H2 de `docs/systemPatterns.md`; `make validate` en el GREEN de B-1 → **Assert PASS: 182 / Assert FAIL: 1** (F011, deriva ambiental preexistente DT-8); revisión de etapa 4 → **2 bloqueantes / 3 opcionales / 1 abstención**; B-1 cerrado por `4d71ccc` → `fc1179b`; B-2 resuelto por el orquestador con audited diff de una línea (registrado en `execution.md`, §«006-004 review de etapa 4: resolución de B-2»); U6 sin despliegue a HOME por orden del owner (sesión activa en OpenCode).

**Commit: ninguno.** El scribe no comitea (patrón Scribe); la materialización de los tres bloques y el commit son del orquestador, **tras** la aprobación del usuario.

**Sin ADR nuevo sugerido:** la decisión arquitectónica de esta feature ya está registrada y materializada como **ADR-034** (`Status: Accepted`, con la aprobación separada registrada en `execution.md`); lo que queda pendiente es la **limpieza de marcas residuales de borrador** (O-2 de la review), no un ADR adicional. Confianza declarada en el propio ADR-034: **Alta**.

**Fidelidad y límites:** los borradores no contienen valores del host, ni identificadores de sesión, ni nombres de otros proyectos (el contexto de «otro proyecto activo» se nombra así). No se afirma que la suite completa se haya ejecutado: no lo fue (la corre quien cierra). No se afirma despliegue en HOME: no lo hay.

**Nota de la revisión de etapa 4 aplicada a este mismo rol:** W-U6-1 (cambios no pedidos del scribe) y W-U6-3 (el adaptador sólo entrega `role-report` hacia el Memory Bank) quedan **registrados como deuda** en el Bloque 1; este borrador no intenta resolverlos ni modify nada fuera del `write_scope` declarado (vacío).