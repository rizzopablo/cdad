Evidence gathered. Below are the three Memory Bank drafts (read-only; nothing written to the repo).

---

# BLOCK 1 — `docs/activeContext.md` (new entry, to be inserted after the `---` on line 5, before the 006-005 entry)

```markdown
---

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
instalada, clase **DT-8** preexistente). **Suite completa: NO ejecutada** — la política declarada en el paquete
la corre **una vez quien cierra**. Es el gate que falta para el cierre formal.

**Desplegado.** El owner autorizó el despliegue en HOME de esta feature el 2026-10-20 («cuando necesites hacer
despliegue hazlo») y existe el script de despliegue de la feature (`.cdad/local/deploy-006-006-u4.sh`:
respaldo previo, `make staging`, `install.sh --force`, `install.sh --check`). La evidencia de U6 declara que el
producto probado fue **la copia de HOME desplegada desde HEAD `a276531`** (U1–U5 incluidas). El fix **W-1**
(`de629b8`, último commit de producto) es **posterior** a esa instalación ⇒ **su redepliegue no está registrado**
en el repo (la fila E4 cita un «despliegue del cierre» cuya sección **no** existe en `u6-acceptance.md`): queda
**pendiente de verificar y registrar** antes de dar la capacidad por disponible en el entorno instalado.

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
```

---

# BLOCK 2 — `docs/progress.md` (row for 006-006)

*Insert as the **first** bullet of the `## Done` section (the section is reverse-chronological). The `## In progress` section stays `_(ninguna)_`.*

```markdown
- **006-006-spec-plan-review** (2026-10-20, epic 006) — quinta feature de
  `epic-006-opencode-concurrency`: la **revisión independiente de un borrador de especificación antes del RED**,
  como capacidad de primera clase del recorrido y no como rodeo. La forma del objeto se **declara** en el
  encargo (`contract.object_kind`); la revisión entra en el **gate 2→3** (supervisado, con
  `docs/specs/<feature>/plan-review.md`); el dictamen **nombra el objeto y su digest** y se materializa en la
  carpeta de la **feature activa**; y la **exención** del owner se registra en la misma entrada de aprobación y
  entra en la identidad **sólo cuando se declara**. **Contrato:** `spec.md` sha256 `4d029a11…` (PD-1..PD-16,
  INV-1..INV-13, D-1..D-15, V-1..V-8) + `plan.md` sha256 `1abe9e7b…`, aprobados el 2026-10-20 por el
  orquestador bajo la **HITL delegada del epic** (el owner la mantuvo ese día), tras `plan-review-001..004`
  (B-1..B-4 cerrados) y con la **errata B-5** aceptada en la aprobación. **Producto (rango `7f39e24..HEAD`:
  59 commits, 46 archivos, +11745/−61; de ellos 14 de producto, +499/−53, y `tests/` 6 archivos nuevos,
  +5030/−0; último commit de producto `de629b8`):** U1 el objeto declarado en el contrato (`--object-kind`,
  `--spec-path`, `--spec-version`; los checks del plan **sólo** sobre el documento de forma `plan`; por omisión
  la forma es `plan` ⇒ el comportamiento vigente no cambia) → U5 la exención registrada e **incluida en la
  identidad de la transición, pero sólo cuando se declara** (bloque `exemption` condicional ⇒ sin exención el
  payload es byte-idéntico al vigente y **las identidades históricas se conservan**, sin enmienda de 005-012
  PD-11, 005-014 PD-23 ni 006-005 PD-19(b); el **replay histórico** se distingue del **intento de sustituir la
  aprobación vigente**, que se rechaza explícitamente) → U2 la fuente canónica de «qué se revisa» (el substage
  generalizado al objeto de especificación, la regla de rol sin plan-centrismo) → U3 el recorrido principal
  (subfase y exit gate de la etapa 2, criterio en el gate 2→3, re-entry del dictamen, **política de
  compatibilidad** declarada) → U4 el rol y los agentes generados (el reviewer declara la etapa 2, el artefacto
  `plan-review.md` y la revisión de borrador) → U6 **recorrido de aceptación real** (proyecto descartable;
  E1..E7 **cumplen**: spec sin plan, spec+plan con los dos digests fijados, borrador de **otra** feature con el
  dictamen en la carpeta de la feature activa, re-review por digest, el dictamen que **no** aprueba, el juicio
  semántico que declara el bloqueante, y el caso de compatibilidad entre revisiones) → **W-1** el arreglo del
  recorrido: `prepare --replace-packet` **reemplaza un paquete de borrador preparado** y recalcula los digests
  desde los bytes actuales (la ruta del contrato aprobado queda byte a byte idéntica). **Review formal: apta
  para cierre, 0 bloqueantes / 2 opcionales** (O-1 la selección de vigencia de la errata B-5 **no** está
  automatizada ⇒ deuda; O-2 la evidencia de aceptación tras W-1 **aplicado** en la misma ronda). **Gates:**
  `make validate` **168 PASS / 1 FAIL = F011** (deriva ambiental de la copia instalada, **DT-8** preexistente);
  **suite completa NO ejecutada** (política del paquete: la corre **una vez quien cierra**) ⇒ **gate de cierre
  pendiente**. **Desplegado** en HOME por orden del owner (script de despliegue de la feature; la evidencia de
  U6 declara la copia desplegada desde HEAD `a276531`, U1–U5): el **fix W-1 es posterior a esa instalación y su
  redespliegue no está registrado** ⇒ pendiente de verificar y registrar. **Deuda:** **O-1** (automatizar el
  selector de vigencia B/C: verificado por separado con las transiciones reales, sin defecto observado), **W-2**
  (el adaptador termina con rc=0 aunque el resultado sea `blocked`; observación), la **deuda declarada de la
  spec** (nombre `draft-plan`/`plan-review`/`plan_version`/`plan-tasks`; ADR-013 O-C; ambientación del dictamen;
  exención como acto de autoridad, no firma; compatibilidad entre revisiones; identidad de la retirada) y la
  **deuda heredada de 006-005 sin cambios** (U6-2, O-2, D-U65-4, D-U65-5, O-2/O-3 de sus reviews, el límite de
  transporte del paquete nativo, DT-8 y el flake DT-9). **El epic NO se cierra: 5/6** — queda
  **006-004-active-decisions-table** (enmienda 003 + 005 ⇒ ADR-034), en el orden del owner
  (**006-005 → 006-006 → 006-004**). **Siguiente:** `006-004-active-decisions-table`.
```

---

# BLOCK 3 — `docs/systemPatterns.md` (new section)

*Insert as a new `###` section immediately **after** the section «Correlación por transporte, registro write-ahead y barreras que no dependen de la clasificación (epic 006, 2026-10-20)» and **before** «### Medición de contexto…».*

```markdown
### Forma declarada del objeto, identidad condicional y gate supervisado (epic 006, 2026-10-20)

- **La forma del objeto se declara en el encargo; no se infiere, y por omisión falla cerrado.** El contrato
  declara la forma (`contract.object_kind`: `spec` | `plan`) como **extensión aditiva** del conjunto cerrado de
  claves (el mismo patrón que `plan_version`), con la **forja** ampliada: un kind `approved-*` que declare las
  claves nuevas se rechaza **antes de publicar nada**. **Ausente ⇒ `plan`**: el comportamiento vigente no cambia,
  el oráculo de la puerta `plan-tasks` se conserva sin cambio y **olvidar la bandera produce un rechazo, nunca
  una aceptación silenciosa**. Se rechazaron y quedaron documentadas las tres inferencias que parecían
  equivalentes: por el **contenido** (el token `plan-tasks`), por la **ruta** (`spec.md`/`plan.md`) y el
  **bloque vacío dentro de la spec** (que deja el `purpose` mintiendo y conserva el modelo mental que el rodeo
  repite). Consecuencia operativa: **una puerta puede exigir la forma y no el contenido**, y los **checks
  estructurales de un tipo se aplican al documento de ese tipo** (una spec nunca se juzga por las reglas del
  plan; un plan nunca se juzga por las de una spec).
- **La identidad doble es por digest, no por cadena de versiones.** Cuando la revisión cubre spec **y** plan, el
  **principal es el documento más estructurado** (el plan) y la spec es el **acompañante**, y el contrato fija
  **los dos por digest calculado de los bytes** (nunca afirmado desde fuera: un digest que no coincide con el
  archivo se rechaza nombrando la divergencia). El digest es lo comparable con `sha256sum`; una cadena de
  versiones puede coincidir mientras los bytes no. Corolario operativo: **una corrección en cualquiera de los
  dos documentos invalida la cobertura de la revisión anterior** (re-review **focal**, no ronda nueva), y el
  objeto revisado **siempre** está fijado por digest: una revisión sin digest fijado no es una revisión.
- **La identidad de una transición se extiende de forma condicional, para conservar las históricas.** Cuando una
  invocación **declara** un dato nuevo que debe participar en la identidad, el payload canónico recibe **una**
  clave **condicional** con **exactamente** los campos declarados (no como `null`: no están). **Sin** la
  declaración, el payload y la `transition_key` son **byte-idénticos** a los del producto vigente ⇒ las
  identidades ya registradas siguen reconociéndose como la misma transición y **no hay enmienda** de las
  garantías aprobadas por otras features (sus oráculos siguen verdes sin cambio de oráculo, y sus archivos de
  test se **ejecutan** como regresión, para que una forma uniforme futura no pueda colarse en silencio). La regla
  uniforme vigente («toda clave presente; un insumo ausente vale `null`») **deja de ser la regla**: el precio de
  conservar las identidades históricas es un payload **condicional**, y esa es una forma de deuda explícita, no
  un descuido. En la misma línea, **la rama de no-op se califica en vez de eliminarse**: el **replay histórico**
  (la entrada nombrada **es** la vigente, o no hay vigente que compita) sigue siendo no-op, y la invocación que
  **colisiona con una entrada histórica que no es la vigente** se **rechaza explícitamente** nombrando la clave
  que colisiona, la clave de la vigente y **las dos salidas** — nunca un no-op exitoso que deje vigente la
  aprobación anterior. Escribir una segunda entrada con la clave colisionada **no** es la salida: esa clave ya
  está en el conjunto de claves sustituidas ⇒ la entrada nueva quedaría inerte para la vigencia y la búsqueda por
  clave seguiría resolviendo a la vieja ⇒ **la pérdida en silencio, otra vez**. Y una retirada de un valor
  anterior **no tiene fórmula de identidad propia**: se registra con un **valor distinguible** (un insumo que
  entra en la identidad y difiere del histórico), porque **añadir una clave de «retirada» volvería a cambiar la
  identidad de todo lo registrado**.
- **Un gate supervisado se distingue de un bloqueo del CLI, y la diferencia se mide con un control negativo.**
  El gate 2→3 (y el exit gate de la etapa que lo contiene) **gana un criterio** —el artefacto del dictamen
  existe y cada bloqueante está resuelto o descartado con razón escrita— y **ninguna** de esas superficies es
  un bloqueo del CLI. La prueba de que el gate **no** es un bloqueo es un caso **positivo**: con una aprobación
  vigente y **sin** dictamen, `prepare` de un rol de construcción **se acepta** (rc=0); el caso **distinto** (sin
  aprobación) **se rechaza** con `approval pending`. Confundir los dos casos —probar el control negativo contra
  el punto equivocado— es lo que hace que un gate supervisado se documente como si fuera duro. Y el artefacto
  del dictamen **nunca** habilita construcción: la habilitación sigue siendo el **pin** de la aprobación.
- **La compatibilidad de paquetes vale dentro de una revisión del producto, y entre revisiones la consecuencia
  se declara en vez de corregirse.** Los **digests de las fuentes de instrucción son parte de la identidad del
  paquete** y la recepción **re-renderiza y compara** ⇒ un paquete publicado antes de un cambio de esas fuentes
  **no es recibible después**: el rechazo nombra la diferencia con el render canónico. Ese rechazo es **ruidoso
  y recuperable**, no un defecto: es una **consecuencia inherente** al contrato de paquete, ya juzgada como tal
  en 005-003 T6 (dictamen F3) con disposición de **deuda declarable** y **sin corregir el renderer**. Corolario
  de diseño: **una feature que toca una fuente de instrucción se invalida a sí misma** en vuelo ⇒ la salida
  legítima se **declara donde el orquestador consulta** (`re-entry.md`): **terminarlo bajo la revisión con la que
  se publicó, o preparar uno nuevo bajo la revisión vigente**. El CLI **no** distingue la causa concreta ni
  ofrece la salida: es **declaración de procedimiento**, y por eso se verifica por **derivación textual** sobre
  el reference, no por un comando. Y la garantía de render byte-idéntico (sin las claves nuevas) vale **dentro
  de una misma revisión**, no entre revisiones.
- **Referencia operativa:** `skills/cdad-cycle/scripts/cdad_packet.py` (conjunto cerrado del contrato, forja,
  `prepare` y sus banderas de forma, checks condicionales al documento de forma `plan`, `inputs` por documento,
  render aditivo, `register-transition` con las tres banderas de exención y el bloque condicional de identidad,
  rama de no-op calificada y reemplazo de un paquete de borrador preparado),
  `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` (dueño único de «qué se revisa»),
  `skills/cdad-cycle/packets/roles/reviewer.md` y `sources/roles/reviewer.md` (el rol y los agentes generados, que
  **nunca** se editan a mano), `skills/cdad-cycle/SKILL.md` (criterio del gate 2→3 y mapa del ciclo),
  `skills/cdad-cycle/references/stage-2-specification.md` (subfase de revisión del borrador y exit gate),
  `references/handoff-prompts.md` (invocación con la forma y la identidad doble) y `references/re-entry.md`
  (re-entry del dictamen y política de compatibilidad); contrato normativo en
  `docs/specs/006-006-spec-plan-review/spec.md` (PD-1..PD-16, INV-1..INV-13, D-1..D-15) y recorrido en
  `docs/specs/006-006-spec-plan-review/u6-acceptance.md`.
- **ADR sugerido:** sí — la decisión de arquitectura de esta feature (la forma del objeto **declarada** en el
  contrato con fallo cerrado por omisión, la identidad doble por digest, la **extensión condicional** de la
  identidad de una transición que conserva las identidades históricas, el gate 2→3 **supervisado** y la
  compatibilidad acotada a una revisión del producto con la salida **declarada**) es candidata a **ADR** (MADR,
  con campo **Confidence: High**). **La numeración no se asigna aquí** (el `ADR-034` está reservado por el plan
  del epic para el principio de general antes que específico) y la **aprobación del ADR es del owner**, no del
  cierre de la feature.
```

---

## Role report (evidence)

**Rol:** scribe · substage `memory` · packet `006-006-spec-plan-review-scribe-memory-001` · **read-only**: `write_scope` vacío, no escribí ni un archivo del repo.

**Fuentes leídas** (todas dentro del repo, `read_scope: repository-read`): `docs/specs/006-006-spec-plan-review/{spec.md, plan.md, plan-review-004.md, u6-acceptance.md, review.md, w1-green.md, discovery.md}`, `docs/epics/epic-006-opencode-concurrency/execution.md` (§«006-006», líneas 362-388), `docs/activeContext.md`, `docs/progress.md`, `docs/systemPatterns.md`, `docs/.cdad-state.json`, `docs/adr/` (numeración vigente), y el diff completo `7f39e24..HEAD`.

**Comandos exactos y salida**

| Comando | Salida |
|---|---|
| `git log --oneline 7f39e24..HEAD -- skills/ sources/ agents/ scripts/ assets/` | 6 commits de producto: `0a6e7fa` (U1), `1cbccd5` (U5), `95d9e11` (U2), `06f76bb` (U3), `a276531` (U4), `de629b8` (W-1) |
| `git rev-list --count 7f39e24..HEAD` | `59` |
| `git diff --shortstat 7f39e24..HEAD` | `46 files changed, 11745 insertions(+), 61 deletions(-)` |
| `git diff --stat 7f39e24..HEAD -- skills/ sources/ agents/ scripts/ assets/` | `14 files changed, 499 insertions(+), 53 deletions(-)` |
| `git diff --stat 7f39e24..HEAD -- tests/` | `6 files changed, 5030 insertions(+)` |
| `sha256sum docs/specs/006-006-spec-plan-review/{spec.md,plan.md}` | `4d029a1178d4dbec6f589b69426402fb46ea7a49f324596837eba82bcd0ad298` · `1abe9e7bf242b223ea312770a064f1a283e1fc46526ae3202299bbdcad28ea58` (coinciden con el contrato del paquete y con el `stage_history` del gate) |
| `git status --porcelain` | `M docs/.cdad-state.json` · `?? docs/planning/` · `?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md` · `?? findings/superlite-transferable-ideas-2026-10-19.md` |
| `git diff docs/.cdad-state.json` | 1 línea: el mark de mi paquete `prepared` → `dispatched` (lo hizo el orquestador al despacharme; **no** es mío) |

**Archivos modificados por mí:** ninguno. **Commit creado:** ninguno. **Suite completa:** no ejecutada (la política declarada en el paquete la corre una vez quien cierra; el reviewer de etapa 4 también lausstió). **Borradores pendientes de aprobación del usuario** (no apruebo, no materializo, no comiteo).

**Dos puntos que el orquestador debe resolver antes de materializar** (declarados, no resueltos por mí):
1. **Redespliegue del fix W-1** — la evidencia de U6 declara probado el producto de la copia de HOME desplegada desde `a276531` (U1–U5); `de629b8` es posterior y su redepliegue **no está registrado** en el repo. La fila E4 de `u6-acceptance.md` cita un «despliegue del cierre» cuya sección **no existe** en ese documento.
2. **ADR** — la feature tiene decisión de arquitectura (forma declarada, identidad condicional, gate supervisado, compatibilidad acotada a una revisión): el bloque 3 la propone con **Confidence: High**, **sin numerar** (ADR-034 está reservado por el plan del epic) y **sin aprobar** — la aprobación del ADR es del owner.