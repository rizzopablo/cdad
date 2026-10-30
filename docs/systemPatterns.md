# System Patterns

Convenciones técnicas, patrones, y reglas estructurales del proyecto. Este archivo se carga al inicio de cada sesión de agente.

## Decisiones vigentes

Las decisiones que gobiernan este proyecto, una fila por decisión. Es el índice de los ADR: dice cuáles están en vigor, a qué roles gobiernan y dónde vive la regla que implantan.

| Archivo | Estado | Resumen | Roles | Referencia |
|---|---|---|---|---|
| `docs/adr/ADR-001-modelos-por-etapa.md` | `vigente` | Modelo distinto por etapa CDAD (sub-agentes especializados). Su mapa de modelos por agente no tiene efecto operativo desde ADR-033; su retiro formal es una decisión pendiente del dueño. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-002-arquitectura-repo-fuente-e-install-sh.md` | `vigente` | Repo fuente como única fuente de verdad + install.sh para propagación. | `architect`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-003-orquestador-materializa-artefactos.md` | `vigente` | El orquestador materializa los artefactos de los sub-agentes CDAD read-only. | `architect`, `reviewer`, `scribe`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-004-usuario-aprueba-no-solo-humano.md` | `vigente` | "Usuario" = humano o agente autónomo de mayor jerarquía dueño del proceso. | `architect`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-005-modelos-via-mofgw.md` | `vigente` | Modelos de los agentes CDAD vía mofgw (gateway propio). Su mapa de modelos no tiene efecto operativo desde ADR-033; su retiro formal es una decisión pendiente del dueño. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-006-git-ejecutado-por-agentes-aprobacion-del-usuario.md` | `vigente` | La ejecución de git es de la capa de agentes; la aprobación es del usuario. | `test-writer`, `implementer`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-007-perfiles-de-modelos.md` | `obsoleto (reemplazado por ADR-033)` | Perfiles de modelos CDAD (economical, optimus, premium). | `orchestrator` | el propio ADR |
| `docs/adr/ADR-008-claude-code-como-segundo-runtime.md` | `vigente` | Claude Code como segundo runtime objetivo para CDAD. Sigue vigente para hooks, guard de rutas, agentes claude-code, instalación y validación; la parte de perfiles y modelos la reemplaza ADR-033. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-009-politica-rtk-allowlists.md` | `vigente` | Política de allowlists rtk: pares `X*` + `rtk X*` por rol, denies de subcomandos peligrosos. | `architect`, `test-writer`, `implementer`, `reviewer`, `scribe` | el propio ADR |
| `docs/adr/ADR-010-modelo-unico-mvp-epic-003.md` | `vigente` | excepción acotada de modelo único para el MVP del epic 003. Excepción acotada al MVP del epic-003, con su regla de vencimiento. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-011-autonomia-supervisada-limites-proporcionales.md` | `vigente` | Autonomía supervisada y límites proporcionales. | `architect`, `test-writer`, `implementer`, `reviewer`, `scribe`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-013-contrato-plan-borrador-revision-sin-aprobacion.md` | `vigente` | El contrato de plan borrador (`draft-plan`) separa revisión de aprobación. | `architect`, `reviewer`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-014-recepcion-materializacion-aprobacion-separadas.md` | `vigente` | Recepción, materialización y aprobación son hechos distintos; el recibo nunca aprueba. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-015-guard-progreso-analizador-readonly-juicio-orquestador.md` | `vigente` | El guard de progreso es un analizador read-only; el juicio es del orquestador. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-017-activacion-por-proyecto-raiz-aislada.md` | `vigente` | Activación por proyecto hacia una raíz aislada adoptada (nunca las configuraciones del HOME real). | `orchestrator` | el propio ADR |
| `docs/adr/ADR-018-clases-de-referencia-declaradas-por-el-escritor.md` | `vigente` | Las clases de referencia de la continuidad (contrato/vivo) las declara el escritor, nunca la ruta. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-019-aprobacion-por-rol-nombra-el-contrato-reemplazo-conserva-el-encargo.md` | `vigente` | La aprobación de contrato por rol nombra el contrato; el reemplazo de paquete conserva y corrige el encargo anterior. | `test-writer`, `implementer`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-020-politica-unica-de-evidencia-y-procedencia-declarada.md` | `vigente` | Una sola política de evidencia con dueño canónico y la procedencia de la instalación declarada en el artefacto publicado. | `test-writer`, `implementer`, `reviewer`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-021-arranque-guiado-procedimiento-corto-por-referencia.md` | `vigente` | El arranque desde reposo se resuelve con un procedimiento corto que compone por referencia, una entrada de intake y un dueño canónico por objeto de reconocimiento. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-022-mapas-de-permisos-derivados-coherentes-con-el-clasificador.md` | `vigente` | Los mapas de permisos derivados son una proyección coherente del clasificador único: la excepción de tests reabre solo los árboles/archivos declarados y `private` gana por findLast. | `test-writer`, `implementer`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-023-delegacion-externa-interfaz-comun-adaptador-por-destino.md` | `vigente` | La delegación externa entre CLI es una interfaz común con un adaptador por destino que reutiliza el mecanismo existente; rol, CLI y modelo son decisiones independientes, la entrega no aprueba el gate y la delegación no amplía autoridad. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-024-medicion-contexto-instrumento-opcional-readonly-no-gate.md` | `vigente` | La medición de contexto es un instrumento opcional, read-only y no-gate. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-031-seleccion-explicita-de-modo-y-servicio-no-gestionado.md` | `vigente` | El modo de ejecución de la delegación externa es explícito y el servicio de fondo no se gestiona; con el servicio corriendo, un fallo termina en `blocked`. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-032-delegacion-por-capa-agente-del-runtime-dueno-del-mecanismo.md` | `vigente` | La delegación se resuelve por capa — el agente del runtime es dueño del mecanismo, la metodología es neutral, el adaptador sólo cruza runtimes y los modelos los fija la configuración. | `architect`, `orchestrator` | el propio ADR |
| `docs/adr/ADR-033-modelos-por-configuracion-sin-perfiles.md` | `vigente` | Los modelos se resuelven por configuración — sin perfiles en el instalador, fuente única en la delegación externa y sin verificación de familia. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-034-principio-general-antes-especifico.md` | `vigente` | Principio de general antes que específico: una casa canónica en el skill y las obligaciones de architect y reviewer. | `architect`, `reviewer` | `skills/cdad-cycle/references/design-principles.md` |
| `docs/adr/ADR-035-localizador-de-aprobacion-por-indice-no-json-pointer.md` | `vigente` | El localizador del registro de aprobación se emite por `index` 0-based con el historial determinado por `object` (`stage_history` para `feature-spec`, `epic_history` para `epic-plan`), no como JSON Pointer: verifica igual sin emitir el token que PD-1 prohíbe en la vista. | `orchestrator` | el propio ADR |
| `docs/adr/ADR-036-verificador-canonico-del-productor-importado-por-consumidores.md` | `vigente` | La verificación de una decisión registrada la ejerce un único verificador del productor, que los consumidores importan; exige la estructura completa, no un subconjunto con hash válido. | `orchestrator` | el propio ADR |

**Nota.**

- El estado de una fila lo declara quien mantiene la tabla: se escribe en la propia fila y no se re-deriva del texto del ADR.
- La referencia es el lugar donde vive la regla que la decisión implanta: el propio ADR, o el archivo del skill instalable.
- Quedan fuera los ADR que todavía no están en vigor (`Proposed`): ADR-012, ADR-016, ADR-025, ADR-026, ADR-027, ADR-028, ADR-029 y ADR-030. Cada uno recibe su fila al aprobarse, y entonces esta lista se actualiza.

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

## Capas y boundaries

- `agents/*.md` — definición de roles: frontmatter (permisos por path, bash
  allowlist, modelo) + directiva del rol. Thin shells: la lógica vive en
  skills, no en el agente. Desde 004-001 (2026-09-29) son salidas declaradas
  de `scripts/cdad-generate.py`: no se editan a mano, se regeneran desde
  `sources/` (PD-2/5).
- `skills/cdad-cycle/` — el ciclo: `SKILL.md` (contrato mínimo siempre
  cargado) + `references/stage-N-*.md` (profundización por etapa, se carga
  una a la vez).
- `skills/cdad-epic/` — coordinación multi-feature (planning light,
  deliberadamente sin descomposición exhaustiva).
- `skills/odoo-*/` — especialización por stack: variante `cdad-*-odoo` de
  cada agente + skills de conocimiento por rol + contrato make.
- `tests/` — validación estructural del framework (bash asserts).
- `docs/specs/<NNN-id>/` — spec + VALIDATION + review por feature.
- `install.sh` — única vía de instalación (copia, nunca symlink, sin --delete).

## Convenciones de código

### Naming

- Agentes: `cdad-<rol>` y variante `cdad-<rol>-odoo`.
- Skills: kebab-case con prefijo de dominio (`odoo-reviewer`).
- Specs: `NNN-feature-id/` (numeración correlativa).

### Organización de archivos

- Reference nueva vs. extensión: se decide por "¿es una etapa/flujo o una
  profundización?" (ver epic superpowers-gaps para los 5 casos resueltos).
- Todo artefacto de rol read-only lo materializa el orquestador (§5 del
  contrato de roles).

### Errores y excepciones

- Anti-patrones: `references/anti-patterns.md` (AP-N) — toda desviación se
  cita con su código.
- Anti-rationalization table: excusas ya refutadas por escrito; no se
  negocia con la excusa, se aplica la refutación.

## Patrones del framework

- Contrato de roles con invariantes anti-bias: reviewer en familia de modelo
  distinta al implementer; test-writer nunca ve `src/`; mapeo
  test↔postcondición auditado por sesión distinta.
- Delegación por orden de preferencia: sub-agentes nativos → handoff packet →
  inline (último recurso, con caveat de aislamiento registrado).
- Evidencia, no confianza: cada gate se cierra con output pegado.

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

### Ciclo confiable — retiro, republicación y publicación transaccional (epic 007, 2026-10-26)

- **El retiro es una transición terminal con motivo, separada de la disposición.** Retirar declara
  que el encargo **nunca llegó** a despacharse; disponer resuelve un despacho que no volverá. Son
  actos distintos y el vocabulario de `disposition` **no** se amplía para cargar el significado
  contrario. El terminal reutiliza el estado de paquete existente y la distinción semántica viaja en
  la entrada de la transición, no en un estado nuevo: un lector que sólo mira `active_packet.status`
  no distingue un retiro de un fallo, y debe leer la transición. Lugares: `project-execution.md` §10 y
  el contrato de `docs/specs/007-006-withdraw-and-republish/spec.md` (que este archivo **no**
  re-enuncia).
- **Resolver la versión no cuesta un encargo.** La republicación de derivados es un verbo
  independiente del ciclo de paquetes: publica desde la instalación resuelta y deja estado, paquetes,
  política y continuidad idénticos, heredando el modelo instalado en vez de elegirlo. La orientación
  sólo ofrece esa resolución para la pata `project` del `DRIFT`; las otras patas no reciben promesa
  (`references/orientation.md`).
- **Publicación transaccional compartida: el checkpoint de acompañamiento se planifica, no se
  publica.** Quien necesite cerrar la continuidad junto con un cambio propio **no** debe invocar el
  publicador de continuidad por su cuenta: pide el plan (`cdad_continuity.plan_write`, que calcula y
  no escribe) y publica las escrituras en **su** transacción, con rollback que restaura lo reemplazado
  y retira sólo lo creado. Es el patrón por defecto para cualquier verbo futuro que necesite estado y
  continuidad coherentes.
- **Límite declarado:** la transacción cubre el estado y lo que el propio verbo publica; la cabeza de
  continuidad **no** comparte el lock del proyecto (`SUSP-LOCK`, deuda de 007-007), así que no protege
  frente a un escritor de continuidad concurrente.

### Entrega declarada en el sobre — `delivery` y el consumo por ruta (epic 007, 2026-10-26)

- **Terminar no acredita entregar.** Un sobre de delegación declara explícitamente qué existe para
  consumir: `delivery` ∈ `none | staged | received`, con `delivery_ref` única (descriptor preparado,
  recibo durable, o nada). Ni `rc`, ni `termination`, ni la llegada de un archivo prueban recepción,
  cierre de continuidad ni aprobación: **entrega declarada y artefacto validado son hechos distintos**
  (ADR-014). Un `none` honesto **no** prueba ausencia de cambios ni de efectos durables.
- **Dos dueños documentales y nadie más.** La **forma, el vocabulario, la tabla de combinaciones, la
  compatibilidad histórica y el significado de `rc`** viven en
  `skills/cdad-cycle/references/cli-delegation.md`; el **procedimiento de consumo por ruta** vive en
  `skills/cdad-cycle/references/re-entry.md`. `sources/roles/orchestrator.md` y los adaptadores
  **remiten**: copiar la tabla es el defecto que la review de 007-004 encontró como duplicación
  parcial. La llegada **FINAL TEXT sin sobre** conserva su ruta propia (staging → `receive`).
- **Consumo por ruta, sin repetir efectos.** `none` → no se avanza a materialización, transición
  exitosa ni gate (se diagnostica y se reconcilian efectos); `staged` → `receive` existente sobre el
  descriptor y después validación del recibo; `received` → **sólo** `validate-receipt`, sin otra
  recepción ni vuelta a staging. Las obligaciones de continuidad se cumplen antes de efectos
  posteriores, y el **gate se decide por separado**.
- **La validación histórica usa el verificador del productor, no una heurística.** Que un sobre no
  declare `delivery` es la **única** puerta al histórico; el contexto conocido de la operación decide
  la interpretación (nunca el nombre del archivo ni el sufijo `RESULT.json`), y en la llegada externa
  la referencia sólo se acepta si **es** el recibo durable de *ese* encargo — localizado por
  `cdad_result.durable_receipt_path` y verificado por `cdad_result.validate_receipt`, **importados**
  (ADR-036). «El archivo existe» no acredita ni recibo ni vinculación. Corolario: cada artefacto
  durable expone su **localizador** desde el productor; los consumidores lo importan, no lo componen.
- **Las contradicciones se rechazan, no se reparan.** Una combinación fuera de la tabla cerrada, un
  vocabulario desconocido, un tipo incorrecto o una referencia en una terminación que la niega se
  diagnostican como respuesta de protocolo no utilizable (`transport-error + none + null`), sin
  registro, recepción ni materialización, conservando las identidades utilizables del sobre original.
  **Borrar la referencia para que el sobre «cierre» es el antipatrón**: convierte un fallo de
  protocolo en una no-entrega válida. Tampoco se acepta una combinación válida en abstracto que la
  **ruta** no admite (una llegada externa nunca acredita `staged`).
- **Límite declarado (007-004).** La **retransmisión explícita** `completed+received` conserva el
  sobre sin revalidarlo: la verificación es del consumidor, por diseño (el relay no registra ni recibe
  otra vez). Sólo la normalización histórica valida y vincula. Y la protección contra leer `rc` como
  éxito depende de **validar el sobre y seguir la ruta**, no del código de salida, que se conserva.

### Cierre de recibo — la acción prescribe revisar, no re-despachar (epic 007, 2026-10-26)

- **Un hecho nuevo sustituye la proyección heredada, y la corrección vive en el productor.** El cierre
  de recibo acredita un hecho que el cuerpo anterior no conocía (el recibo existe y valida), así que
  **no hereda** la acción que prescribió el despacho: escribe una acción canónica —recibir es mecánico,
  no se repite despacho ni recepción, y revisar **no** presume aprobación (ADR-014)—. Se corrige en el
  **productor común** del cierre, no en `resume`, en la llegada externa ni en la recuperación: el hecho
  que invalida la acción previa es el mismo en las tres entradas. Contrato en
  `docs/specs/007-008-receipt-next-action/spec.md`, que este archivo **no** re-enuncia.
  **Contrapartida asumida:** `resume` proyecta literalmente la cabeza, así que un cierre **histórico**
  conserva su acción obsoleta; la compatibilidad hacia atrás se elige sobre la reescritura de historia.
- **Cuidado con leer el cuerpo como instrucción vigente.** El `next_action` de un checkpoint es la
  orientación de **su** momento; quien decide qué hacer ahora es la vista compacta y `reconcile`, no el
  texto de un cuerpo viejo. Un cierre anterior a esta regla puede seguir prescribiendo re-despachar.
- **Lección de proceso del epic 007 (sin mecanismo todavía):** toda subfase de rol —RED, GREEN,
  review— se despacha con paquete renderizado (`prepare`/`begin`/`verify-begin`/`record`/`receive`).
  Sin paquete, la subfase **no tiene continuidad registrada** y su única evidencia son commits y tests;
  en el epic la excepción se repitió en varias unidades y se declaró en cada cierre. **El ciclo no lo
  verifica hoy**, así que esto es una **exigencia del método**, no una garantía del producto, y queda
  como deuda prioritaria del epic siguiente.

### Suite por capacidad y cierre con evidencia preservada (epic 008, 2026-10-27)

- **Un gate que no ve cambios exclusivamente de tests no sirve para reorganizar la suite.** El gate por
  superficie anterior sólo miraba cambios comprometidos de producto y referencias en `tests/test_*.py`: un
  cambio que tocara únicamente tests podía producir **selección vacía**, es decir, una reorganización
  **invisible**. El selector canónico (`scripts/cdad-suite.py surface`) compara contra `<ref>` incluyendo
  cambios no indexados, resuelve un test trasladado consultando el mapa **de la base** (`--no-renames`), y
  **nunca devuelve selección vacía como éxito**: una dependencia sin clasificar es diagnóstico no cero y sólo
  `--all` explícito selecciona todo. Un gate cuya respuesta ante «no encontré nada» es «pasó» no puede
  acreditar que nada cambió.
- **El cierre reserva un intento exclusivo y la evidencia no se sobrescribe.** Nombrar la evidencia por
  número de corrida es el defecto que se pagó en 008-001 (los intentos fallidos quedaron pisados). La regla
  es por **invocación**: directorio nuevo con nombre único por creación exclusiva (`os.mkdir` sin reintento)
  y **colisión es error** (rc 2), nunca reutilización ni adopción del ajeno. El estado se escribe **antes** de
  arrancar el hijo (`running`) y se reescribe al terminar (`finished`) con `rc`, comando, selección, commit,
  `dirty`, tiempos, salidas y snapshots: una interrupción deja `running` y **no se lee como éxito**. La
  garantía es de creación exclusiva y no reuso, no de inmutabilidad externa.
- **Un límite de tiempo se declara y se neutraliza el entorno del hijo, o el resumen se marca no
  verificable.** Un resumen derivado de la salida de un proceso ajeno no es un dato si el entorno puede
  cambiarla: con `PYTEST_ADDOPTS='-qq'` el cierre declaraba **cero aprobados con `rc=0`** (reproducido por el
  reviewer en 008-002). La regla es doble: neutralizar las variables que alteran la salida y, si aun así no
  se puede parsear, escribir `verified: false` **con diagnóstico** en vez de ceros. Un cero fabricado es peor
  que un «no verificado» honesto.
- **Organizar la suite no es migrar carpetas.** Índice lógico y versionado (inventario por capacidad y
  contrato + mapa obligación→test): permite módulos mixtos y selección exacta sin romper imports, a costa de
  ser una **declaración auditada** que hay que mantener. `validate` la contrasta contra la colección real y
  contra la **baseline registrada** de la unidad, no contra `HEAD`: comparar contra el árbol actual
  convertiría toda consolidación legítima en pérdida.
- **Límites declarados (008-002).** `confidence` explícita y alcance de módulo en los mixtos; el mapa cubre el
  piloto, no la suite entera; `measure` es instrumento; `surface` falla ruidoso bajo `PYTEST_ADDOPTS`; el
  canario cubre las rutas de 008-001, no el árbol del repo. Normativo en
  `docs/specs/008-002-suite-by-capability/{spec.md,closure.md}`; este archivo **no** re-enuncia PC-1..PC-8.

### Admisión de la encomienda — identidad por marcador canónico, integridad por bytes (epic 008, 2026-10-28)

- **La identidad de una encomienda CDAD la da el marcador, no el texto.** El marcador canónico se identifica
  **exactamente una vez, en cualquier posición**; lo que lo precede es preámbulo **transparente y no
  autorizante**. Cero marcadores es una **ausencia explícita** —consulta legacy, que no acredita despacho
  CDAD— y no una ruta de recuperación; más de un marcador, bloque sin cierre o identidad discordante se
  **rechazan, sin fallback silencioso a legacy**. La razón es operativa: el runtime antepone una línea a todo
  prompt de subagente y no está bajo el control del ciclo, así que clasificar por palabras del objetivo o por
  nombre de rol sería una heurística sobre texto libre. Corolario: «legacy» describe la falta de encomienda,
  nunca un paquete dañado.
- **La integridad se mide por bytes contra el render canónico, no por metadatos.** La cadena es `request
  validado → render_packet → igualdad del paquete recibido completo`, desde el marcador hasta el final, sin
  normalizar ni reconstruir. Validar sólo el encabezado deja sin proteger objetivo, instrucciones, contrato,
  entradas, scopes, invariantes y evidencia; la review lo reprodujo: encabezado válido con objetivo alterado
  pasaba el intake textual. No se añade un segundo criterio de hashes: ADR-036 ya fija que el verificador es
  del productor y lo importan los consumidores.
- **Cada frontera invocable verifica su propia precondición antes de sus efectos.** `begin`,
  `prepare --record-dispatch`, `dispatch`, `record` y `delegate` admiten **antes** de publicar continuidad,
  observar el modelo, preparar staging, transmitir o cambiar estado. El preflight del orquestador es
  obligatorio y **no suficiente**: la primera ronda de review encontró `cdad_delegate` lanzando un worker con
  el paquete alterado tras un `begin` válido, porque la comprobación vivía sólo en `dispatch`. El replay
  conserva su precedencia: reconocer una repetición ya acreditada **no** autoriza un despacho nuevo.
- **Coherencia entre referencias y `write_scope` en `begin`.** Una referencia `contract` cubierta por el
  `write_scope` del propio paquete se rechaza **antes de persistir** —diagnosticando referencia y selector—
  reutilizando `_scope_contains`; `living` explícita conserva su semántica (ADR-018) y no hay reclasificación
  automática. Motivo medido: esa referencia se **autoinvalida** por P1 en el `record`; durante el epic 008
  murieron así cuatro registros (contados por 008-003) y hubo además un rechazo por `state incoherent` al
  corregir una spec después del `begin`. La regla gobierna `begin` nuevos y no invalida registros previos.
- **La regla vive en la fuente y en las copias, y eso se verifica.** El intake es compartido por cinco roles y
  dos runtimes: corregir sólo `sources/` deja a los agentes generados e **instalados** con el contrato
  anterior, y esa divergencia es el modo de falla (PC-08: 20 copias generadas y 11 agentes por runtime).
  Comprobar la distribución instalada es parte del contrato, no higiene de despliegue.
- **Límite que no se puede prometer lejos.** Esto es **admisión**, no un sandbox: no intercepta herramientas
  nativas, no impide que un agente ignore sus instrucciones y no acredita los bytes que recibió una sesión
  nativa por validar el paquete en disco. Normativo en `docs/specs/008-004-role-packet-enforcement/`
  (`spec.md` PC-01..PC-08 con D1/D2/D3, `closure.md`); este archivo **no** re-enuncia las PCs.

### Cotas de reloj de pared — miden el host, no el producto (epic 008, 2026-10-28)

- **Un `assertLess(elapsed, …)` es una aserción sobre el entorno.** En el gate de 008-004, los siete fallos
  de las corridas B y C fueron cotas de espera de 2,5–5 s incumplidas por 0,05 a 4,2 s, con el host a
  `loadavg` 5.4–6.9 sobre 8 CPU por agentes de **otras sesiones**; las clases afectadas pasan en aislamiento
  (3/3 dos veces con load 6.5–6.6) y en un worktree del commit previo, y la duración de la suite pasó de 51
  min a 1:43 **sin cambio de código**.
- **Consecuencia de método:** una cota de reloj no puede ser el criterio de verde de un gate que corre en un
  runner compartido, y tres corridas verdes consecutivas no se alcanzan reintentando ni promediando —008-001
  ya había fijado que los intentos se **reinician, nunca se promedian**—. El cierre lo declara en vez de
  presentarlo como verde, aunque el producto de la unidad esté verde.
- **Estado:** deuda **BLOCKING** del criterio «Suite estable» del epic-008 y **primer requisito de 008-005**.
  Este archivo registra la medición y su lectura; **no** decide el remedio.

## Palanca `write: ask` y permisos de bash (cdad-010, ADR-009)

### Palanca `write: ask` (2026-09-12; enmienda de ubicación 2026-09-13)

Los 10 agentes declaran `permission.write: ask` — la clave `write` ANIDADA
dentro del bloque `permission:` del frontmatter (NO top-level: el KNOWN_KEYS
del clasificador no incluye `write` top-level y una palanca top-level es
inerte — el agente colapsa a read-only y `task` lo rechaza; verificado por
probe en cdad-010, enmienda registrada en el spec H1). Doble rol NO obvio: es
la palanca que hace al agente **task-able**. Motivo: el clasificador del
plugin de sub-agentes lee la clave `write` del bloque `permission:` anidado
para decidir si el agente es write-capable o read-only; el runtime NO la
evalúa (el tool `write` pide "edit" — cero evaluaciones `permission=write`
en logs). Mecánica: el agente queda task-able sin generar prompts de permiso.

**REGLA DE VIGILANCIA: si una versión futura de opencode empieza a evaluar
`write` en runtime, la palanca `write: ask` genera prompts de permiso en cada
escritura y hay que revisar los 10 agentes.** Checklist al migrar versión:
(1) grep de logs buscando `permission=write`; (2) si aparece, migrar la
palanca a otra vía y re-probar la clasificación task/delegate con los probes
de cdad-010 como baseline.

### Bloques `permission:` anidados y orden findLast

El clasificador del plugin lee SOLO el bloque anidado `permission:`
(edit/bash/read); las claves top-level caen en `options` — inertes en
runtime. Semántica del matcher: **catch-all primero, específicas después**
(findLast: la última regla que matchea gana). Una regla específica antes del
catch-all es un bug de config. Única excepción documentada de `ask`: la
palanca `permission.write: ask` (anidada).

### Política vigente de diseño — autonomía supervisada (2026-09-24)

[ADR-011](adr/ADR-011-autonomia-supervisada-limites-proporcionales.md) gobierna
los próximos contratos: capacidades suficientes dentro del encargo, principios
explicados y verificación al re-entry. El orquestador acepta decisiones dentro
del mandato, corrige causas de fricción y no cierra gates con evidencia inválida.
Repite solo trabajo afectado; no cada tarea completa por cualquier desvío.
La migración de configuraciones aterrizó en 004-001 (2026-09-29): agentes generados desde fuentes e instalación solo desde staging; los apartados históricos siguientes son referencia de cómo se llegó acá.

La regla histórica de demostrar un problema con una sola invocación no es un
criterio universal de riesgo: usar evidencia adecuada al efecto observado,
explicitar lo no comprobado y evitar probes innecesarios o inseguros. Los textos
siguientes documentan la implementación anterior, no un requisito de conservar
catch-all deny o pares de comandos durante la simplificación.

### Fuente única de agentes — generador determinista + staging (epic 004, 2026-09-29)

- **Agentes como salidas declaradas:** los 22 archivos de `agents/` se
  generan con `scripts/cdad-generate.py` desde `sources/` (Markdown con
  delimitadores); misma entrada produce bytes idénticos (PD-2). Cierre
  verificado en 004-001 (criterio 2): regeneración con stack/perfil
  registrados en el manifest idéntica a los 22 archivos. **Nadie edita un
  agente a mano** (personas ni agentes); cambiar una regla canónica y
  regenerar actualiza a los consumidores (PD-5) y `install.sh --check`
  detecta la copia instalada que difiere de staging.
- **Generación ≠ instalación:** el generador escribe en staging con manifest
  (sha256, fuentes, comando de regeneración, stack/perfil); el instalador
  **nunca lee `sources/`** (PD-18; `tests/test_install_ownership.py`) y
  registra propiedad de archivos: primera instalación sin borrar nada (PD-6),
  conflicto de hash reportado sin sobrescribir (PD-7), uninstall solo lo
  propio (PD-8). El exceso del techo del bloque estático produce error
  explícito, no una salida mezclada (PD-19; `tests/test_static_block_ceiling.py`).
- **Política bash permisiva con barreras por ruta:** la política por rol es
  derivable de la fuente canónica con efecto declarado por regla (PD-1,
  T4, review-4 approved). Las listas FORBIDDEN se retiraron por decisión del
  dueño (`80f9b90`) y el control quedó como comprobación semántica con
  trazabilidad (PD-10; `tests/pd10_permission_semantics.py`, con la
  mutación M6 el checker pasa de 27/27 a 26/27 con el FAIL trazado, verificado
  en la review del orquestador). Las barreras de
  path se prueban en ambas direcciones (PD-12): operación legítima con éxito
  y fuera de rol bloqueada por el mecanismo declarado (`path-guard.sh`
  instalado, exit 2 / 0).
- **Orquestación con construcción delegada y verificación propia:** el
  orquestador delega la construcción a los roles CDAD (sesiones aisladas,
  registro PD-17 por tarea) y no acepta un reporte como evidencia: revisa el
  artefacto y reproduce lo verificable ("reproducido" en closure.md =
  corrido por el orquestador). La review encuentra evidencia engañosa (p. ej.
  mutaciones que no mataban su reemplazo) que el reporte del agente no muestra.
- **Alcance del recorrido vivo:** la prueba de capacidad desde el producto
  instalado (5 roles, 39 llamadas, 0 denegaciones) demuestra capacidad
  operativa por el camino legacy (sin paquetes); el ciclo con paquetes y
  contexto reducido se verifica en 004-002.

### Ejecución por proyecto v2 — política, derivados y guard (epic 004, 2026-10-02)

- **Política única del proyecto:** `docs/cdad-policy.json` (solo
  `schema_version`, `path_policy`, `temporary_roots`). Clasifica raíces,
  archivos exactos, tests co-ubicados, temporales y `private_paths`; ningún rol
  la edita; es la fuente de scopes y derivados (PD-1/2/7).
- **Paquetes v2 e identidad lógica:** `.cdad/executions/<execution-id>/execution.json`
  + `dispatches/<attempt-id>.json`; `execution_id` estable entre roles, runtimes
  y sesiones; runtime/modelo/sesión son observaciones (unknown=`null`).
- **Aplicación por runtime:** OpenCode usa agentes derivados de proyecto
  `.opencode/agents/` (I9, manifiesto `.cdad-derived.json`); Claude Code usa el
  guard dinámico `path-guard.sh` que clasifica con el CLI instalado (I10).
- **Barrera viva por ruta = `read` (OpenCode).** `read` resiste variantes
  absoluta/relativa/`..` y el listado de directorio muestra nombres, no
  contenido. `grep`/`glob` se evalúan por patrón, no por ruta (W-2); `edit`/`write`
  no acotados en vivo en 2.0.16 (W-3). La disciplina de escritura es instrucción
  + auditoría del orquestador (`git diff --name-only` contra `write_scope`) —
  regla general de límites L-1 en los 22 prompts generados.
- **`private_paths`:** la única barrera nueva deliberadamente obvia; deny en
  `read` para todos los roles en OpenCode y bloqueo de herramientas mediadas en
  el guard CC; no sustituye instrucción ni auditoría.
- **R5 aceptado:** el guard cuesta ~252 ms/llamada con política v2 (vs 32 ms
  legacy, N=20), sin caché.

### Autorización por rol pineada y reemplazo con conservación (epic 005, 2026-10-09)

- **La aprobación de contrato es por rol y con la fuente correcta (PD-1..PD-6).** El
  **architect** se habilita con la aprobación del **plan del epic** (`epic_history`
  `{epic|epic_id, stage: "epic-plan", approved_by}`; **sin** pin de hash — D2: el plan es
  mandato vivo, se edita después de aprobado y la autorización sigue vigente).
  **test-writer/implementer/reviewer** exigen una entrada `stage_history` `specification`
  que **nombre el contrato**: `contract_path == contract["path"]` **y**
  `contract_sha256 == sha256` verificado (C1/PD-18; INV-8). El enforcement vive en
  `validate_request` (donde se conoce el `role` y el sha ya está verificado contra el
  archivo); `_validate_v2_vigency` conserva la coherencia de estado (feature/epic/
  delegación). Una entrada histórica no conforme (rectificada, de otro vocabulario, sin pin,
  o con path ajeno) **no habilita** autoridad (INV-6/PD-6/PD-18). Editar la spec deriva su
  sha → la aprobación deja de coincidir (PD-4) y se **re-registra** (el pin anterior queda
  superado).
- **Reemplazo de un paquete preparado y no despachado (PD-7..PD-11, PD-16;
  `--replace-packet`).** Solo el `active_packet` con `status: "prepared"` es reemplazable;
  un `dispatched` exige **reconciliación** (PD-10) y uno terminal no se toca. Exige
  obsolescencia verificable (sha del contrato o revisión de política cambiados; PD-8) y
  `--reason` no vacío (PD-9). Re-resuelve el contrato del día y publica el sucesor **solo**
  con la aprobación vigente (PD-11: nunca inventa autorización). El paquete anterior queda
  **byte a byte idéntico** (INV-3) y se escribe `.superseded.json` durable. Ninguna entrada
  de `stage_history`/`epic_history` se crea o modifica (INV-2).
- **El reemplazo conserva el encargo y admite correcciones explícitas (C2/PD-19..PD-24;
  INV-7; D7).** Sin opciones de corrección, el `REQUEST.json` nuevo conserva campo a campo
  el anterior (`execution_id, role, substage, objective, inputs, read_scope, write_scope,
  invariants, expected_output, evidence_required`); **no** recomputa defaults. Las opciones
  `--input/--read-scope/--write-scope/--invariant/--expected-output/--evidence` reemplazan
  la lista/campo **entero** (el centinela `-` como único valor la deja vacía; `-` mezclado →
  rc=2). Los pisos obligatorios del rol (`DEFAULT_INVARIANTS`/`DEFAULT_EVIDENCE`) se
  re-agregan siempre (PD-21). Las correcciones pasan las **mismas validaciones** que un
  `prepare` normal (PD-22; diagnóstico campo/motivo/opción). El argv mezclado se rechaza
  antes de cualquier lock o escritura (PD-23). `.superseded.json` suma
  `conserved_fields`/`changed_fields` disjuntos y exhaustivos (PD-24).
- **Marcadores de bloqueo distinguibles y accionables (PD-12).** `approval pending` (falta
  la aprobación o su pin no nombra el contrato), `packet obsolete` (contrato o política
  cambiados) y `state incoherent` (el state se contradice: binding, feature/epic, idle) son
  mutuamente excluyentes por condición, salen por stderr con rc=2, nombran el registro/falta
  y la acción legítima siguiente, y no alteran el state ni publican archivos.
- **Reposo legítimo (PD-13..PD-15).** `active_feature == null ⟺ current_stage == "idle"`; se
  tolera `execution` remanente y `active_packet` terminal `completed|failed`; un paquete en
  vuelo (`prepared|dispatched`) con reposo → `state incoherent`. `validate-state` sale rc=0
  `VALID: idle`.
- **Referencia operativa:** `references/project-execution.md` §2 (autoridad) y §8
  (reemplazo); el contrato normativo es la spec de la feature
  (`docs/specs/005-001-idle-and-v7-bootstrap/spec.md`, PD-1..PD-24).

### Coherencia de la adopción — política única de evidencia y procedencia declarada (epic 005, 2026-10-09)

- **Una sola política de evidencia, con dueño canónico y consumidores que remiten
  (INV-6).** La política vive en **un único lugar** editable:
  `skills/cdad-cycle/references/stage-3-tdd.md` §**«Test evidence policy»**
  (regresión proporcional al cambio; suite completa **al cierre** de la feature o
  antes si se toca instalador/staging/renderer; reutilización de evidencia
  equivalente; **la metodología define la evidencia y el proyecto declara los
  comandos**; una condición local se registra y no se vuelve requisito). La regla
  de **equivalencia** conserva su dueño en `references/re-entry.md`
  §«Equivalence of a registered run». Los consumidores (paquetes de
  GREEN/refactor/review-fix, `packets/roles/implementer.md`, `SKILL.md`, las
  referencias de etapa) **referencian** la política y **no copian** su texto; la
  suite completa es gate de **cierre**, nunca «por GREEN».
- **El reemplazo valida el encargo resultante completo (005-005 PD-1..PD-7;
  INV-4).** `--replace-packet` valida **todo** el encargo resultante (conservado +
  corregido): cada `input` existe y cae dentro de algún `read_scope`; scopes
  clasificados por la política; `invariants`/`evidence_required`/`expected_output`
  no vacíos; diagnóstico **campo/motivo/opción**. El **camino normal de `prepare`
  no cambia** (la exigencia de existencia es propia del sub-modo; un `input`
  declarado inexistente en `prepare` normal sigue `rc=0`); una lista `inputs` vacía
  legítima (`--input -`) sigue válida.
- **La procedencia de la instalación se declara y no cambia en silencio (005-005
  PD-12..PD-14; INV-7).** `prepare` resuelve el origen de los agentes de proyecto
  en orden **`CDAD_OPENCODE_AGENTS_DIR` > registro de activación
  (`.cdad/activation.json`) → `<adopted_root>/.config/opencode/agents` > global
  (`$HOME/.config/opencode/agents`)**. Si el origen resuelto difiere del registro o
  del `source_dir` del manifiesto anterior, emite un **diagnóstico por stderr** que
  nombra el registro y las versiones en juego (caso real MIX-V6V7). El manifiesto
  publicado `.opencode/agents/.cdad-derived.json` declara `source_dir` y
  **`source_version`**, y el instalador escribe **`version.txt`** en la raíz
  instalada, de modo que **qué versión cargó una sesión es verificable desde el
  artefacto publicado**. `opencode reload` sobre un servidor ya iniciado queda
  **NO verificado** (se documenta el hecho del dueño y la comprobación aislada; no
  se afirma).
- **El cierre es un test de integración en raíz aislada (005-005 PD-18; INV-8).**
  La versión nueva del repo se instala en una raíz aislada (nunca HOME) y con su
  CLI se corre `prepare` → `--replace-packet` (validación completa) → despacho con
  validación proporcional; sin rodeos manuales y sin tocar HOME (guard estructural).
- **Referencia operativa:** `references/runtime-adoption.md` §«Procedencia de los
  agentes de proyecto»; `references/opencode-delegation.md` §«Reload, version and
  provenance»; contrato normativo en la spec de la feature
  (`docs/specs/005-005-adoption-coherence/spec.md`, PD-1..PD-18).

### Recepción, materialización y evidencia de artefactos (epic 003, 2026-10-06)

- **Herramientas de artefactos:** `skills/cdad-cycle/scripts/cdad_result.py`
  (+ wrapper `scripts/cdad_result.py` + entrypoint instalado equivalente) expone
  `receive`, `validate-receipt`, `materialize`, `run-python-unittest` y
  `validate-run-evidence`. Construyen sobre el runtime v2 (execution context,
  paquete renderizado, binding de autoridad, observación de dispatch I8); no
  redefinen sus esquemas.
- **Store operacional:** `.cdad/runtime/` (aditivo dentro de `.cdad/`,
  gitignored) guarda parts + bundle + receipt por `(execution_id, packet_id)`;
  el inbox de staged parts es `.cdad/inbox/`. Publicación atómica (temp + fsync
  + rename exclusivo); una sola finalización durable por execution/packet; el
  retry idéntico devuelve el receipt byte a byte.
- **Recibo mecánico que NUNCA aprueba:** `semantic_status` siempre `pending`,
  `approval_effect` siempre `false`; recepción, materialización y aprobación
  semántica son hechos distintos y ninguna operación cierra un gate.
- **Un solo escritor del state:** `docs/.cdad-state.json` lo cambia solo el
  orquestador. `receive`/`materialize`/`run-evidence` no lo tocan;
  `state_transition_requested=received` es una transición lógica que el
  orquestador mapea al estado de paquete `completed` (vocabulario de 001). La
  referencia de receipt en `stage_history` la agrega el orquestador (forma
  existente; sin cambio de esquema).
- **Política de artefactos (§7):** tabla cerrada `artifact_kind`/rol-subfase que
  fija la **raíz permitida**; el **target exacto** se declara en la autorización
  (create-only/CAS). Cierre rol↔kind fail-closed (`_allowed_kinds`). Los ADR
  (`docs/adr/`) **no** están en la tabla: su materialización sigue siendo del
  orquestador (ADR-003).
- **Evidencia de runner:** solo `python3 -m unittest` (argv sin shell);
  snapshots before/after calculados por la herramienta (no acepta digests del
  caller); `valid-current` exige exit 0, `tests_run>0`, al menos un test no
  skipped, cero failures/errors/runner exceptions, árbol no mutado y contract
  vigente. La ligadura `argv`↔selecciones es **fail-closed**: lo que no puede
  demostrarse degrada a `unknown` (whitelist cerrada de opciones invariantes).
- **Protocolo canónico:** `skills/cdad-cycle/references/re-entry.md`
  (RECEIVE → RECONCILE → MATERIALIZE → STATE TRANSITION), con el staging del
  TEXTO FINAL como paso mecánico previo del orquestador.

### Continuidad — checkpoint content-addressed + proyección on-demand + `reconcile` como oráculo (epic 003, 2026-10-07)

- **`cdad_continuity.py` es read-only sobre el producto.** `reconcile`, `resume` y
  `trigger` son deterministas y de solo lectura; `begin`/`checkpoint` escriben **solo**
  bajo `.cdad/executions/<id>/continuity/**`. El CLI **nunca** escribe
  `docs/.cdad-state.json`: el single-writer del state sigue siendo el orquestador
  (regla vigente desde 003-002/ADR-003) y el CLI **nunca aprueba**.
- **Checkpoint content-addressed (L2) = autoridad de delegación/decisiones/presupuesto.**
  Cuerpo canónico cuyo `sha256` es el propio digest, más `prev_checkpoint_sha256`, `seq`
  monotónico y `references[]` con digest. `resume`/`reconcile` verifican sha del cuerpo,
  eslabón previo y existencia+digest de cada referencia; cualquier fallo → rc≠0 con el
  delta exacto (sin truncar). `begin` con cuerpo idéntico al head es **no-op (rc 0)**;
  cabezas divergentes o igual-sha-con-cuerpo-distinto ⇒ **escalar** (sin `generation`).
- **Memoria activa = proyección on-demand (L1), no persistida.** No existe `ACTIVE.json`:
  la proyección se reconstruye desde la cabeza L2; su ausencia **no** es error de
  `reconcile` ni de `resume`. La historia es L3: se consulta **por referencia** (state/
  `stage_history`, receipts 002, eventos 003, dispatches I8, Memory Bank), nunca se embebe
  el transcript. `--max-bytes` (default 16 KiB) es un techo que **falla cerrado**, nunca
  trunca.
- **`reconcile` es el oráculo de efectos ya aplicados.** Antes de todo retry/resume
  consulta receipts/journal de 002, dispatch I8 y state: con receipt válido **no** ofrece
  repetir el efecto; una sesión desaparecida es `dispatched-unknown` (≠ fracaso ≠
  autorización de repetir, invariante 3). `continuity` **consume** el receipt de 002; **no
  materializa** (eso sigue siendo del orquestador con autorización explícita). Para
  clasificar `received` el flujo de despacho debe pasar la salida por `cdad_result`
  `receive` (deuda RU-2a).
- **`trigger` es señal, no límite.** Solo devuelve `prepare`/`rotate` con contador **y**
  límite enteros; en cualquier otro caso `trigger: unknown`, `context_*: null` y
  `unknowns[]`. **Prohibido** convertir bytes en tokens o presentar un proxy como límite
  (desconocido permanece desconocido). El presupuesto de intentos es durable (003) keyed
  `execution_id+packet_id+attempt`: reanudar **no** reinicia contadores.
- **Autoridad desde el estado estructurado.** Vigencia y `authority_ref` se leen de
  `hitl_delegation` en `docs/.cdad-state.json`; no se parsea la prosa del archivo de
  autoridad. Autoridad vencida puede reconstruir contexto pero **no** autorizar
  dispatch/materialize.

### Continuidad tolerante a documentos vivos — la clase la declara el escritor (epic 003, 2026-10-08)

- **La clase la declara la referencia, nunca la ruta (D2/P3).** `--update.references[]` acepta
  un string (compat: `class = contract`) o un objeto `{"path", "class", "fields"?}` con
  `class ∈ {contract, living}`. El CLI **no** deriva la clase de rutas fijas:
  ausente/desconocido ⇒ `contract` (**falla cerrado**). La clase resuelta se **estampa** en el
  body del checkpoint.
- **`contract` bloquea; `living` informa y nunca calla (P1/P2/D3).** Cada referencia visible en
  `resume`/`reconcile`/`trigger` se reporta `{path, class, sha256, current_sha256,
  state ∈ unchanged|changed|missing, legacy?}`. Deriva `contract` ⇒ `rc≠0` con `path` y delta
  exacto; deriva `living` ⇒ `rc 0` con `state: changed|missing` (jamás en silencio).
- **Proyección de autoridad del state con `fields` (D1/P4/BL-3).** `fields` (subconjunto de
  claves top-level de un JSON) hace que el digest cubra solo esa proyección; recomendado
  `hitl_delegation`, `approver`, `execution` (el resto —`stage_history`— es progreso, residuo
  **R-2** → deuda). `fields` sobre un archivo **no-JSON** o con **proyección vacía** ⇒ `rc≠0`
  **al escribir** (el digest se congela en el body; nunca un digest constante que dé cero
  integridad en silencio).
- **`checkpoint` ≠ `begin` (P5/P6/T4-CKPT).** El body gana `record` (`begin`|`checkpoint`); un
  `checkpoint` con la clave del head **apendea** un eslabón (`seq+1`, `prev`), no se rechaza
  como split-brain; un `begin` divergente con la misma clave sigue **cerrado**; un checkpoint
  idéntico re-ejecutado es **no-op**. `_detect_split_brain` = **≥2 bodies con
  `record != "checkpoint"` por clave** (huérfanos/legados pre-RU-2).
- **Legado por comparación (P7/D6/R-1).** Un cuerpo pre-003-007 sin `class`: digest igual al
  congelado ⇒ verificado `contract`; distinto/ausente ⇒ `changed` con `legacy: true` y **no
  bloquea**. **Excepción documentada:** la clase de legado **no está congelada**, así que el
  legado **informa** cualquier documento cambiado —incluida una decisión que en un checkpoint
  nuevo sería `contract`— en lugar de bloquearlo.
- **Regla de encargo + wiring en el orquestador (P10/D9/BL-1/R-4).** `sources/roles/orchestrator.md`
  expresa el encargo como **una unidad despachable** (una tarea del plan o una subfase TDD; los
  RED/GREEN como despachos separados la satisfacen), con postcondiciones trazadas a ≥1 test y un
  diff acotado y revisable; el bloque "Continuity wiring" declara explícitamente qué es `living`
  y qué `contract` (o un puntero estricto a la sección de clases de `continuity.md`); `make
  agents` regenera **solo** los dos agentes orquestador.
- **Límites declarados:** **MIX-V6V7** — la v6 leyendo un checkpoint v7 con `fields` digiere el
  archivo completo y falla cerrado ⇒ usar **una sola versión del CLI por ejecución**;
  **T2-R1** — un `begin` idéntico tras un append de su clave da `rc≠0` en lugar de no-op;
  sin detección de forks de checkpoint mismo-key (deuda).

### Activación por runtime — adopción por proyecto hacia una raíz aislada (epic 003, 2026-10-08)

- **Una sola versión operativa, en una raíz aislada versionada.** La versión de CDAD que
  cargan los runtimes se instala con `CDAD_INSTALL_ROOT=~/.cache/cdad-adopted-<rev>
  bash install.sh` y se registra en `docs/runtime-adopted-version.md` (tabla vigente +
  historial) con verificación de consumidor. La identidad se comprueba contra el
  `.cdad-install-manifest.json` de la raíz adoptada. Se adopta **solo en el límite de
  tarea/cierre y tras review independiente**; la versión anterior se conserva.
- **La activación es por proyecto y NUNCA escribe las configuraciones del HOME real
  (I1/I2).** `scripts/cdad-activate.py --project-root R --adopted-root A`
  (+ `references/runtime-adoption.md`) emite archivos **git-ignorados** que apuntan a `A`:
  OpenCode (`.opencode/opencode.jsonc`), Claude Code (`.claude/{agents,skills}`, con el
  `command:` del hook reescrito a `<A>/.claude/cdad-scripts/path-guard.sh <rol>`) y Codex
  (`.agents/skills`). Propiedades exigidas: **determinista** (mismo input → bytes
  idénticos), **`--dry-run` sin efectos**, **no-clobber** (destino divergente → error
  nombrado, nunca sobrescribe) y **contención de ruta** (`realpath` estricto bajo
  `realpath(R)`; un symlink que escapa → conflicto, rc≠0, todo-o-nada).
- **El hook de Claude Code fija el clasificador a la raíz adoptada (RU-1).** Se emite
  `command: CDAD_PACKET_CLI=<A>/…/cdad_packet.py <A>/…/path-guard.sh <rol>`; ningún
  `command:` emitido depende de `$HOME` (`path-guard.sh:134` resolvía la copia vieja de
  HOME → fail-closed). El fail-open de P5 vale solo **sin política o con script ausente
  (`exit 127`)**; con política presente y clasificador inválido, **falla cerrado**.
- **Límites declarados por runtime (no prometer paridad):** OpenCode carga la raíz
  adoptada ✓; **Claude Code** mezcla versiones (las skills de usuario ganan a las de
  proyecto) y los hooks del frontmatter no corren si la carpeta no es de confianza —
  mitigable despachando con `--setting-sources project,local`; **Codex** usa la copia de
  proyecto pero el catálogo también lista la vieja de HOME, sin adaptador de agentes.
- **`receive` en el ciclo y `continuity` cableados (complementa ADR-014/ADR-016).**
  `begin` (write-ahead), `checkpoint` (límite), `reconcile` (antes de retry/resume),
  `resume` (sesión nueva); `trigger` advisory, `classify` fuera (sin lector de sesiones).
  Fricción declarada: **T4-CKPT** (el checkpoint de límite comparte clave con el `begin`)
  y **T4-REF** (reanudación bloqueada si cambia una referencia a documento vivo) — deuda,
  no producto.
- **Activación no commiteada = producto pendiente de decisión del dueño.** Configs de
  activación git-ignoradas (I3); activar/apuntar a la raíz v6 es decisión del dueño. Sin
  CI: el gate es la suite local.

### Delegación externa — señal durable real, modo de carga y directorio del proyecto (epic 005, 2026-10-11)

- **La señal durable la produce el runtime, nunca el fixture.** El adaptador OpenCode espera la
  **base de sesiones SQLite** del runtime (`session_v2` + `session_message`), abierta en **solo
  lectura** (`mode=ro`) en la ruta que declara la config de ejecución (`sessions_db`; **ruta
  configurable, jamás hardcodeada**). Un store ausente/ilegible/no-SQLite/con esquema incompleto
  **falla cerrado** con diagnóstico que nombra el esquema/columna; el `UnicodeDecodeError` deja de
  existir. El esquema **no es contrato público**: se valida por columnas requeridas, no por marcador
  de versión; sin `immutable=1` con el servicio vivo; nunca se escribe el store.
- **Correlación inequívoca por `--session <id>`.** El adaptador **elige** el id y lo pasa; la fila
  durable lleva ese `id`, `agent` e `idle_outcome`; el texto final es el **último** `session_message`
  `assistant`. La terminación se clasifica desde `idle_outcome` (`succeeded→completed` con texto;
  `failed→blocked`; `interrupted→cancelled`; sin idle dentro de la espera acotada → `timeout`),
  **nunca** desde el `rc`; la espera es acotada (`wait.timeout_seconds`; su ausencia falla cerrado
  pre-despacho).
- **`mode: subagent` es entry no interactiva en la versión instalada.** La barrera deja de ser
  `mode: all`; la identidad se verifica desde la fila durable (`session_v2.agent == "cdad-<rol>"`),
  **sin fallback** a un agente no-Cdad. `cdad-generate.py` y la fuente de agentes **no** cambian.
- **OpenCode resuelve el directorio del proyecto desde `PWD`, no desde el cwd.** El adaptador fija
  `PWD` = raíz del proyecto explícito en la invocación. Invocación soportada: paquete byte-idéntico
  por **stdin**; `--standalone` por defecto (servidor privado); `--server <url>` por config como
  alternativa (nunca a la vez); `--auto` por config (activado por defecto, documentado como
  auto-aprobación de permisos **no-sandbox** —los deny-maps de path siguen siendo la barrera—).
- **Higiene del test:** un doble que **fabrica** la señal que el producto espera valida el contrato
  **contra sí mismo**. Los tests deterministas usan un **SQLite real chico** con el esquema observado;
  la aceptación real (instalación y proyecto aislados, runtime real con `--standalone`) es un gate
  **aparte**, omitido por defecto y habilitado por variable de entorno.
- **Referencia operativa:** `references/cli-delegation.md` y `references/opencode-delegation.md`;
  ADR-023 (**enmienda 2026-10-11**); contrato normativo en
  `docs/specs/005-010-real-opencode-delegation/spec.md`.

### Delegación externa — selección de modo explícita y servicio de fondo no gestionado (epic 006, 2026-10-17)

- **El modo de ejecución es explícito y no hay fallback silencioso.** `mode` ∈ {`server`, `service`,
  `standalone`}; con `mode` **sin declarar** rige la **compatibilidad v1** (`server` presente → servidor; si
  no, standalone) y **no** se pasa a `service` por defecto: cambiar a un servidor compartido es decisión del
  consumidor (D-9, ADR-031). Una config inválida (tipo, signo, `mode` fuera del conjunto, `poll_max <
  poll_initial`, `service.require` no booleano) → `blocked` **antes** de invocar nada.
- **CDAD no gestiona el servicio de fondo ni servidores.** La **única** invocación de `service` es `service
  status` (solo lectura, **exactamente una vez**, y sólo en modo servicio); ninguna argv lleva `serve`,
  `service start|stop|restart|get|set|unset` ni `reload` (INV-2). El servicio lo prepara y lo mantiene el
  **dueño/operador**; CDAD tampoco escribe el store (sólo `mode=ro`).
- **La recuperación nunca reconstruye el problema.** El **único** cambio de modo admisible es el **fallback
  declarado y contable** `service` → `standalone` cuando `service status` informa que **no corre**
  (`fallback=service-unavailable`); con el servicio **corriendo**, todo fallo (versión, credencial, respuesta
  inesperada) termina `blocked` y **nunca** standalone (INV-10). Tras un `timeout` en servicio o servidor
  ningún camino re-despacha solo ni abre un `standalone` «para destrabar».
- **La versión del servicio se lee como proyección de una sola clave.** El gate de compatibilidad proyecta
  **solo** `version` del registro del servicio, **sin red, sin contraseña y sin URL**, y **falla cerrado**
  (`blocked` con las dos versiones o «no verificable»); el registro y su esquema **no** son contrato público
  (DT-6). La salida de `service status` se descarta salvo el discriminante: ninguna salida lleva la URL del
  servicio.
- **Lo no observado es `unknown`, también en la recuperación.** El chequeo del intento previo es
  **innegociable**: un store **existente** cuya fila no se puede afirmar (ocupado o ilegible) **bloquea antes
  de cualquier invocación**, espejo del fail-closed de `service status`; un store **inexistente** es un hecho
  determinante distinto y **no** bloquea (§2.7).
- **Referencia operativa:** `skills/cdad-cycle/references/cli-delegation.md` y
  `skills/cdad-cycle/assets/opencode-exec-config.example.json`; **ADR-031**; contrato normativo en
  `docs/specs/006-001-opencode-concurrency-reliability/spec.md` (PD-1..PD-14, INV-1..INV-10).
  **Aviso de cota (actualizado por 008-001):** los fixtures de tiempos nacieron con cotas de **2 s** y son
  frágiles bajo carga del host (**DT-9**); desde 008-001 el fixture compartido usa 5 s y las cotas
  instrumentales 5–10 s **sólo** donde la cota no es el sujeto, mientras los tests en los que la cota **es**
  el sujeto conservan sus aserciones. La regla de producto que salió de ahí está en «La cota del despacho
  pertenece al adaptador», abajo.

### La cota del despacho pertenece al adaptador (epic 008, 2026-10-27)

- **Un solo dueño del tiempo: el adaptador.** El adaptador administra la operación completa —preflight,
  cliente y observación durable—, así que **la cota es suya**. El wrapper (`cdad_delegate.py`) y el
  preflight del adaptador son **redes de seguridad con margen declarado**, no la cota: el wrapper espera
  `cota + ADAPTER_WAIT_GRACE_SECONDS` (5.0 s) y su diagnóstico **nombra el límite efectivo**; sin cota
  declarada no impone límite (comportamiento previo). Esperar el **mismo** `timeout_seconds` que el
  adaptador administra lo mata justo antes de que emita su sobre y convierte un resultado en un `timeout`
  genérico con `session: null` — es lo que PD-11/PD-8 prohíben y lo que el gate de 008-001 midió
  (PC-7). Corolario: **una red de seguridad se declara con margen, no se disfraza de cota**.
- **Sin presupuesto útil no se despacha.** El deadline de preparación del adaptador es **agregado** (no se
  renueva por operación) y debe **reservar** presupuesto positivo para el cliente y la observación durable
  **antes** de ejecutarlo; el mínimo útil de espera es proporcional al presupuesto
  (`max(0.1, 0.2·budget)`). Si la preparación agota el presupuesto, **no se lanza el cliente**, no se
  fabrica sesión ni recibo, y el diagnóstico identifica el **agotamiento preparatorio** en lugar de emitir
  un `bounded wait (0.0 seconds)` sobre un cliente que nunca corrió (PC-8). Un tiempo de espera calculado
  por resta puede llegar a cero: **el cero no es una espera**.
- **Por qué es durable y no un parche de la suite.** Ninguno de los dos defectos era de los tests: ambos
  aparecían sólo cuando la suite se volvió ejecutable en condiciones reales (HOME aislado, host cargado).
  Poner verde la suite no habría cambiado el producto. La regla general es que **un límite de tiempo
  declarado por una interfaz pertenece al componente que lo administra**; los demás lo esperan con margen
  y fallan **nombrando** el límite, nunca reemplazándolo por el suyo.
- **Límite declarado.** PC-7 y PC-8 corrigen los bordes de cota **demostrados**; no prometen que todo host
  cargado responda dentro de cualquier cota. Queda abierto el techo de «no esperar de más»: con el fixture
  en 5 s, distinguir «hecho conocido» de «esperó la cota» tolera hasta 5 s (deuda a 008-002).
- **Referencia:** `docs/specs/008-001-home-xdg-isolation/spec.md` AJ4/PC-7 y AJ5/PC-8, con el detalle en
  el `closure.md` de la misma carpeta; las constantes y los deadlines viven en
  `skills/cdad-cycle/scripts/cdad_delegate.py` y `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`.
  Este archivo **no** re-enuncia el contrato.

### Delegación por capa — el mecanismo lo declara el agente del runtime, la skill es neutral y el adaptador sólo cruza runtimes (epic 006, 2026-10-18)

- **El mecanismo de despacho pertenece a la capa del runtime, no a la skill.** Cada orquestador generado
  declara su mecanismo **nativo** (`task` + `subagent_type: cdad-<rol>` en OpenCode; `Agent` +
  `subagent_type` en Claude Code), el mapeo rol→subagente con sufijo de stack, la **prohibición
  intra-runtime** del adaptador CLI y la declaración de familia (abajo). La regla vive en
  `sources/agents/adapters/{opencode,claude-code}.md` como bloque `<!-- cdad-section:delegation -->` y el
  generador la compone (`REQUIRED_ADAPTER_SECTIONS` en `scripts/cdad-generate.py`); **nadie edita
  `agents/**` a mano** (fuente única de agentes, epic 004).
- **La skill queda neutral: metodología, no herramientas.** `skills/cdad-cycle/SKILL.md` §4 conserva los
  **siete puntos** en abstracto (principio, orden, regla de adaptadores, invariantes de rol, spawn guard,
  recibo, paquete/reentrada independientes del transporte) **sin nombrar runtime ni modelo concreto**;
  `handoff-prompts.md` y `sub-agent-strategies.md` son plantillas. La ausencia se verifica con un oráculo de
  **formas de herramienta** (código en línea `` `task` ``, `` `delegate` ``, `` `Agent` ``; el token
  `subagent_type`; `opencode run`; `sessions_spawn`; `Agent tool`) y de **modelos concretos** — **nunca** con
  la palabra suelta *task* (prosa como «atomic task» no matchea). `references/context-meter.md` es
  **exclusión declarada**: nombra `task`/`subagent` como **datos de medición**, no como instrucción.
- **El adaptador sirve para otro runtime o para uno sin delegación propia.** Sirve para orquestar agentes de
  **otro** runtime o de uno **sin** delegación nativa; en cualquier otro caso se delega con el mecanismo
  nativo. La regla de elección **por transporte** salió de `references/cli-delegation.md`, que queda como
  **contrato del adaptador**; las dos referencias por runtime (`opencode-delegation.md`,
  `claude-code-delegation.md`) **salieron del árbol instalable** y su detalle histórico/verificación vive
  **no instalable** en `docs/evidence/runtime-delegation/` (byte-idéntico salvo el encabezado que declara
  «no instalable; la regla vigente no está aquí»). Nada instalable apunta a esa copia.
- **El modelo lo fija la configuración, nunca el orquestador ni el script.** `SKILL.md` §2 pierde la columna
  de familia de modelo y el párrafo de perfiles; el orquestador **pasa un modelo sólo si viene de la
  configuración del entorno** y **nunca lo elige ni lo inventa**. Con un perfil que **no** fija modelos
  (`basic`) la familia distinta del reviewer **no** está garantizada por construcción: se **declara** y se
  **registra el intento** (`runtime`, `model_configured`, `model_reported`, `session`; `null`/`unknown` lo no
  observado, y el gate de review escribe «invariante no garantizado» en vez de omitirlo). El script de
  comparación de familias, la config de delegación y la sustitución de ADR-007 son de **006-003**.
- **El paquete y el recibo son independientes del transporte.** El **mismo** `receive` cierra cualquier ruta:
  el despacho nativo devuelve **TEXTO FINAL** en la sesión del orquestador, que escenifica los **bytes
  exactos** bajo `.cdad/inbox` + `RESULT.json` y corre `receive` → `validate-receipt` → `materialize` →
  transición; el recibo queda **`semantic_status: pending`** (recibir no aprueba nada). La equivalencia está
  declarada en `references/re-entry.md` (protocolo de materialización) y **enlazada** desde §4 y desde cada
  sección `delegation`.
- **Disciplina de contexto del orquestador: cuatro reglas.** (1) orientarse con la vista compacta `status`
  **primero**, sin volcados de state/ledger/skill; (2) **rotar la sesión** en los bordes de tarea, no a mitad
  de unidad; (3) **no reparar por su cuenta** — re-despachar el rol nombrando el defecto; (4) lo que debe
  durar, dejar evidencia o leer otro proceso o rol va a **rutas estables del workspace** (`.cad/inbox` para el
  recibo). El **Ningún texto instalable nombra `/tmp`**: el dueño lo sacó de la metodología (enmienda 002 — el
  límite era de su servidor, no de la metodología) y el oráculo exige la regla de rutas estables **y** la
  ausencia del literal en `skills/**` y en los agentes generados. `references/orientation.md` §1 sigue siendo
  el **dueño** de «vista primero»: la fuente lo **cita** y no lo duplica.
- **Límite honesto:** el oráculo prueba que la regla **existe**, no que se **obedezca**. La única evidencia de
  comportamiento es el transcript de la corrida de aceptación —una sesión hija `cdad-reviewer` despachada por
  `task`, 56 comandos sin adaptador— y es una **muestra**; en esa misma corrida el orquestador leyó el código
  del CLI para resolver el arranque (contra el espíritu de la regla 1) y tomó notas de orquestación como
  mandato.
- **Referencia operativa:** `sources/agents/adapters/*.md`, `sources/roles/orchestrator.md`,
  `skills/cdad-cycle/SKILL.md` y `skills/cdad-cycle/references/re-entry.md`, `docs/evidence/runtime-delegation/`;
  **ADR-032**; contrato normativo en `docs/specs/006-002-delegation-by-layer/spec.md` (PD-1..PD-11,
  INV-1..INV-8, D-1..D-7, enmiendas 001/002).

### Modelos por configuración, archivos del usuario fuera del ownership y retiro de obsoletos propios (epic 006, 2026-10-18)

- **Los modelos se resuelven por configuración, y CDAD no los elige ni los verifica.** Este bloque **completa** el
  principio que ADR-032 dejó declarado («el modelo lo fija la configuración, nunca el orquestador ni el script»,
  cuyo script de familias y config de delegación eran «de 006-003»): el instalador y el generador **no tienen
  perfiles ni mapa de modelos** (`scripts/cdad-models.sh` retirado, `Makefile` sin `PROFILE`, `cdad-generate.py` sin
  `--profile`, staging sin la clave `profile`, **ningún agente con `^model:`**); los flags de perfil se **rechazan**
  nombrando el lugar donde se elige el modelo, y `--basic`/`CDAD_MODEL_PROFILE` sobreviven un ciclo como **alias
  deprecado sin efecto** (aviso de una línea, INV-7: nada silencioso). En la **delegación interna** el modelo lo fija
  la configuración del runtime; en la **externa**, `delegation.json` v1 —por **destino y rol**— es la **única**
  fuente, **sin fallback**: un rol sin entrada produce el destino **sin `--model`** y `model_configured: null`, y una
  clave `model` heredada en la exec-config se **ignora con aviso**. **El invariante de familia del reviewer no se
  exige ni se verifica** (decisión del dueño, A-5): la observación I8 (`model_configured`/`model_reported`) **solo
  registra** lo ocurrido; los demás invariantes anti-sesgo no cambian.
- **Los archivos de configuración del usuario no son propiedad del instalador.** `delegation.json` y
  `opencode-server.env.example` se crean **solo si no existen** (segunda instalación: bytes idénticos + aviso) y
  **no se registran en el manifiesto**: ni `--uninstall` ni el retiro de obsoletos pueden borrarlos (A-3). Regla
  general: el ownership del instalador cubre **lo que él desplegó**, no la configuración con la que el usuario
  completa el despliegue.
- **El instalador retira sus propios obsoletos, y la regla de retiro es una sola.** Un artefacto registrado,
  **no redesplegado** y con **sha256 igual al registrado** se **retira** del disco y del manifiesto; uno
  **modificado localmente** se **preserva**, se reporta como CONFLICT y **sigue registrado**; uno **no registrado
  nunca se lee**. La misma función decide en la instalación y en `--uninstall` (sin duplicar la regla) y
  `--dry-run` lista las bajas sin escribir. **Un registro con el digest vacío o `null` nunca es removible**
  (veredicto `unverifiable`): solo se retira lo propio **con sha256 sin cambios** (INV-2).
- **Los registros estructurados no se transportan como TSV leído por bash.** Lección medida (B-1 de la re-review de
  006-003): `IFS=$'\t' read` **colapsa las columnas vacías**, así que un registro con un campo vacío se
  reinterpreta como otro registro (y puede **retirar sin comparar el digest**). Los registros del manifiesto viajan
  **NUL-framed** con `read -r -d ''`; los streams que quedan en TSV los parsea **Python** (`split("\t", 2)`), que
  preserva campos vacíos. Un campo vacío que cambia el veredicto de un borrado es un defecto estructural, no un caso
  degenerado.
- **Referencia operativa:** `install.sh` (prune y arranque), `skills/cdad-cycle/scripts/cdad_delegate.py`
  (`delegation_model`, regla única de la base de config) y `cdad_delegate_opencode.py` (credencial),
  `skills/cdad-cycle/references/cli-delegation.md` § Configuration, `skills/cdad-cycle/assets/*`;
  **ADR-033**; contrato normativo en
  `docs/specs/006-003-installer-single-profile-delegation-config/spec.md` (PD-1..PD-8, INV-1..INV-7, D1..D8,
  A-1..A-4, A-5).

### Correlación por transporte, registro write-ahead y barreras que no dependen de la clasificación (epic 006, 2026-10-20)

- **La correlación se demuestra con la evidencia que produce cada transporte, y hay tres resultados, no dos.**
  **La externa**: el módulo **elige** el id de sesión y correlaciona por él («el adaptador, no el cliente, es el
  dueño del id de correlación»); **no hay padre que comparar** y **no** se exige la igualdad `directory == raíz`
  (esa igualdad no prueba el proyecto y rechazaría el recorrido legítimo: coordinador iniciado desde otra
  carpeta, layout anidado). La identidad del rol se corrobora contra la fila durable. **La nativa**: las llaves
  son las **columnas observables** del store de la versión declarada —padre, agente, momento y proyecto **por
  pertenencia** (dentro de la raíz ⇒ coincide; **ancestro ⇒ no evaluable**, no prueba ni contradice; ajeno ⇒
  contradicción)—. **Umbral de discriminación:** la acreditación positiva exige **al menos una llave discriminante
  evaluada y coincidente** (padre, momento o proyecto); **«agente» por sí solo no acredita**, porque dos
  despachos nativos concurrentes del mismo rol comparten agente ⇒ con sólo esa llave el resultado es
  `unknown`. **Tres resultados con consecuencia propia:** *verificada* (se persiste la sesión observada) ·
  *no verificable* (`unknown`, **sin entrega por esa vía**, salvo la garantía menor PD-6: con resultado nativo
  byte-exacto la entrega se persiste con `session: null` y procedencia que declara la identidad no verificada) ·
  *verificada e incorrecta* (**rechazo** que nombra la llave; **nunca** `unknown`, **nunca** entrega aceptada).
  Una llave **expuesta pero no declarada** sigue siendo `unknown**: no se omite para acreditar. Una contradicción
  en cualquier llave evaluable —incluida «agente»— es rechazo. Nunca se compara contra un valor supuesto: sin
  `agent` en el paquete, esa llave es `unknown`, nunca `cdad-<rol>`.
- **El registro del intento se escribe antes de que el cliente pueda producir efectos, y se completa una sola
  vez.** El módulo externo escribe su registro I8 **provisional** (marca legible `write-ahead:` al frente de
  `provenance.session`, `model_reported` en `null`) **antes de lanzar el cliente**: después de cargar el request,
  pasar el chequeo de intento previo y elegir el id de sesión. **Si ese registro falla, el cliente no se
  lanza** y la terminación es `blocked` con el diagnóstico (fail-closed). En **toda** terminación posterior el
  registro se **completa una vez**: se reemplazan la sesión, el modelo reportado y **todos** los pares de
  procedencia de terminación; la **identidad** (ejecución, paquete, intento, rol, subfase, runtime, inicio) **no
  cambia** (si difiere ⇒ rechazo); la compleción **sólo** vale sobre un registro con la marca y produce uno sin
  ella ⇒ una segunda compleción, o una compleción sobre un registro sin marca, es **rechazo**. La regla
  write-once del ledger no cambia: **un registro por despacho**. Secuencia de recuperación, sin autorizar
  repetir efectos: `reconcile` ⇒ `dispatched-unknown`; un re-despacho con la sesión viva ⇒ `blocked` sin
  invocar el cliente; `disposition` ⇒ `failed` con `validate-state` VALID; el siguiente `prepare` procede.
  **Límite declarado:** la vía nativa **no** tiene write-ahead (la sesión la crea la herramienta del runtime) ⇒
  la salida es **procedimental** (el siguiente coordinador ejecuta `record` con `--parent`/`--since`).
- **La barrera del rol prevalece sobre la clasificación de la política.** En el mapa `edit` del agente derivado,
  los `allow` de raíces de implementación se emiten **antes** de las prohibiciones de tests convencionales
  (semántica findLast: gana el `deny`), y el derivado aplica la **barrera del agente generado restringida por la
  política, nunca ampliada**: clasificar una ruta como «implementación» **no** autoriza a editarla cuando es un
  test. La clasificación sigue sirviendo para el alcance y el piso de escritura; **no** es autorización. La
  precedencia se **prueba**, no se declara: el caso que la resuelve es una raíz de implementación con un test
  convencional dentro, y su reemplazo de oráculo va declarado en el RED.
- **Las versiones se comparan por observación, no por lo que dice la configuración.** El control de versión
  compara **observado contra observado** (cliente contra servidor), nunca contra un número escrito en el
  archivo de config; una diferencia se **declara en el diagnóstico** y **no bloquea**. `binary_version` queda
  **opcional e informativo**, y el paso de migración deja de escribirlo. La **compatibilidad del store se
  verifica por capacidad** (si faltan las columnas que la correlación evalúa ⇒ fail-closed nombrándolas), y no
  por un número de versión guardado.
- **Una sonda de store registra tipo y unidad, no sólo nombres de columna.** El precedente medido: una sonda que
  registró los nombres de las columnas dejó que los fixtures **inventaran** la unidad del instante (segundos
  `REAL` donde el runtime guarda milisegundos epoch `INTEGER`), y el resultado fue que la llave **nunca** pudo
  evaluarse contra el store real — con la degradación emitida con las mismas palabras que otro caso, lo que
  escondió la causa. **Tipo y unidad son parte de la observación**; sin ellos, la comparación no se puede hacer y
  el fixture inventa la realidad.
- **Una palanca de permiso anulada por el runtime vacía el mapa de rutas.** Los agentes generados llevaban una
  palanca `write: ask` que la versión instalada **sí evaluaba**: por la precedencia de la última regla, todo
  pasaba a *ask* —la vía externa escribía **fuera de su alcance** y la nativa no interactiva rechazaba **todo**.
  El mapa de rutas sólo es una barrera si **ninguna** regla posterior lo anula; por eso la palanca se retiró del
  generador **y** los derivados dejan de heredarla de una copia instalada vieja (si no, una instalación anterior
  seguiría anulando el mapa derivado y la protección dependería del estado del entorno, no del repo).
- **Referencia operativa:** `skills/cdad-cycle/scripts/cdad_dispatch.py` (entrada, verbos, `record`),
  `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (credencial, agente, kind, `--capabilities`/`--observe`),
  `skills/cdad-cycle/scripts/cdad_delegate.py` (la interfaz que deja de registrar y relaya),
  `skills/cdad-cycle/scripts/cdad_packet.py` (agente en el request, scope `temporary`, permiso del derivado,
  disposición `failed`), `skills/cdad-cycle/scripts/cdad_result.py` (fila del scribe y tabla cerrada),
  `skills/cdad-cycle/references/cli-delegation.md` (configuración, borde de adopción) y `re-entry.md` (protocolo
  por estado de llegada); contrato normativo en
  `docs/specs/006-005-native-path-parity/spec.md` (PD-1..PD-26, INV-1..INV-16, D-1..D-17) y recorrido en
  `docs/specs/006-005-native-path-parity/u6-acceptance.md` y `u6-5-decision.md`.
- **ADR sugerido:** sí — la decisión de arquitectura de esta feature (una entrada con dos vías, correlación por
  transporte con umbral de discriminación y tres resultados, y registro write-ahead con compleción única) es
  candidata a **ADR** (MADR, con campo **Confidence: High**). **La numeración no se asigna aquí** (el
  `ADR-034` está reservado por el plan del epic para el principio de general antes que específico) y la
  **aprobación del ADR es del owner**, no del cierre de la feature.

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

### Medición de contexto — registro neutral opcional, medidor read-only que nunca aprueba (epic 005, 2026-10-11)

- **El formato de medición es neutral respecto del runtime y opcional para la metodología.** El
  **registro neutral** (contrato `context-meter-v1`) vive en
  `skills/cdad-cycle/assets/context-meter.schema.json` y su procedimiento/semántica en
  `skills/cdad-cycle/references/context-meter.md`. **No está enganchado en ningún gate**
  (`prepare`, `validate-state`, `validate-request`, review, merge): el ciclo **sigue** aunque el
  entorno no exponga tokens. El **esquema neutral es el contrato**; el adaptador **solo traduce** y
  es el **único** que conoce los nombres de tablas/columnas del runtime (el registro neutral **no**
  los contiene).
- **El adaptador es canónico con wrapper fino, y lee en solo lectura.** El canónico es
  `skills/cdad-cycle/scripts/cdad_context_meter.py`; `scripts/cdad_context_meter.py` es un **wrapper
  fino** (`runpy.run_path`), convención del repo. El store se abre con **URI de solo lectura**
  (`?mode=ro`), **nunca** se escribe ni se checkpoint-ea, las consultas se **acotan** (sesión/
  ventana) y la salida es **JSON único, stdlib y determinista** (byte-idéntica).
- **Fallo cerrado con diagnóstico que nombra el faltante y sin números.** El esquema de la fuente se
  valida por **columnas/tabla requeridas** (la fuente **no** tiene marcador de versión); si falta
  algo, el medidor **falla cerrado** (`rc != 0`) con un diagnóstico que **nombra el elemento
  faltante** y **ningún número** de métrica. Nunca fabrica métricas (sin conversión bytes→tokens, sin
  límite de contexto inventado).
- **Regla de cubos: observado / estimado / desconocido; desconocido nunca es cero.** Cada métrica
  vive en **exactamente uno** de los tres cubos: `observed` = leído directamente del registro;
  `estimated` = **proxy declarado** (contexto cargado por paso = `input + cache.read + cache.write`,
  **no** la ventana real); `unknown` = nulo/ausente/no reportado **con causa**, **nunca** `0`. El
  input reportado **no** se equipara con consumo facturado ni con capacidad máxima.
- **Límite normativo de 16384 bytes por documento de sesión** (salida compacta con referencias a la
  evidencia original), declarado en `references/context-meter.md`.
- **El medidor NUNCA aprueba nada.** La anotación `application` es **referenciada** (una referencia
  durable —ruta/commit/recibo—, **no** una copia del contenido) y su `limit ∈ {accepted, blocked,
  pending, unknown}` deriva de **hechos observables**, no del juicio del lector; un despacho
  registrado **no** prueba utilidad ni resultado aceptado. El medidor no cierra gates.
- **Referencia operativa:** `references/context-meter.md`; contrato normativo en
  `docs/specs/005-002-session-context-meter/spec.md` (PD-1..PD-16, INV-1..INV-10).

### Orientación acotada — proyección read-only del estado, encargo autosuficiente (epic 005, 2026-10-12)

- **La orientación es una proyección, no una migración.** El subcomando **read-only** `status` de
  `cdad_packet.py` (`compact-view-v1`) emite **un único documento JSON** desde las fuentes **ya
  existentes** (`docs/.cdad-state.json` solo en sus campos operativos, `execution.json`, `REQUEST.json`
  + `active_packet`, `cdad-policy.json`, el `cdad-version-check.py` y la proyección de continuidad).
  **No** se reescribe el formato del estado, **no** se separa el historial, **no** hay segunda memoria
  (INV-2/INV-7). El `stage_history` (**304.075 B = 94,8 %** del estado) **NO se emite**: se consulta
  selectivamente ante una duda concreta.
- **Acotada y determinista, con fallo cerrado.** La vista respeta un **límite normativo de 16.384 B**
  (el mismo número ya normativo para el documento de una sesión); al superarlo **falla cerrado**
  (`rc≠0`) **sin emitir proyección parcial**, con diagnóstico que nombra el límite y la bandera
  `--max-bytes N`. El límite **no crece con el historial** y es el mismo para cualquier tamaño de
  estado (la proyección es función de los campos operativos). Misma entrada → mismos bytes; deja el
  estado **byte-idéntico** (INV-1).
- **La selección de entrada es un mapa explícito, no una inferencia.** El campo `entry` emite
  `continuity-reconcile` | `next-unit` | `diagnosis` según condiciones observadas: **un paquete
  `prepared`/`dispatched` se atiende antes que cualquier inferencia de etapa** (caso real: etapa en
  curso + paquete `prepared` ⇒ `continuity-reconcile`, nunca `next-unit`); reposo sin pendiente ⇒
  `next-unit`; configuración incompleta ⇒ `diagnosis`. **No** depende del literal «inicializar» ni
  agrega campo nuevo al estado.
- **Ausencia ≠ incoherencia en el verdicto de versión.** `UNKNOWN`/`NO-PROJECT-AGENTS` son *ausencia*;
  `DRIFT` es *incoherencia*; cualquier `rc≠0` se lee «no verificado coherente», nunca `ok`. El caso
  **«medidor no instalado»** se trata como **ausencia**, no como `DRIFT`; el despliegue es del dueño.
  Límite declarado: la coincidencia de archivos **no** demuestra lo cargado por una sesión abierta.
- **Evidencia mecánica sin enmascarar el `rc`.** El patrón (en `references/orientation.md`) captura el
  retorno **real** del CLI sin tubería que lo sustituya (`PIPESTATUS[0]`, no `$?`); salida acotada con
  evidencia completa por referencia; errores `ERROR: …` accionables. La **asimetría de raíz relativa**
  entre CLIs se **diagnostica en la salida de la vista** (nombra ambos CLIs y el camino de
  recuperación), no solo en prosa.
- **El encargo de tarea trae su contrato aplicable (`packet-contract-v1`, aditivo).** Con
  `--plan-task <ID>` (y el campo opcional `plan_task`), el paquete emite una sección declarada con los
  **comandos de validación de esa tarea iguales a los del bloque canónico `plan-tasks`** del plan
  aprobado (con `@validation_strategy` resuelto) y la regla de **cuándo ampliar**; una tarea ausente
  **falla cerrado nombrando el id**; emite por referencia las postcondiciones/invariantes/decisiones
  aplicables (ids que resuelven a encabezados) con la referencia del contrato (path + `sha256`).
  **Aditivo:** sin `plan_task` el paquete se emite **byte-idéntico**; el conjunto cerrado de campos se
  extiende con una propiedad declarada (una clave desconocida sigue rechazándose). La **provenance**
  de los valores se afirma contra lo parseado del bloque, no contra texto a mano.
- **Política de la suite: declarada una sola vez, consumidores que referencian.** La instrucción del
  paquete declara, en su parte **común** (`packets/common.md`), que la **suite completa no se corre
  salvo que el paquete lo pida** y que **la corre quien cierra**; los assets de rol/subetapa la
  **referencian** (no la copian) y se corrigieron los que afirmaban lo contrario. El **cierre del
  encargo incluye el commit** (el reporte del rol lo declara; no hay gate automático, la verificación
  es la auditoría del orquestador).
- **Resumen del conjunto aditivo + regla del documento multiplexado (`set-summary-v1` /
  `context-meter-r4-v1`).** Para corridas multi-sesión se emite **primero** un resumen en un
  **documento aditivo separado** (sesiones incluidas hasheadas, cobertura, hitos, magnitudes con cubo
  y cobertura, referencias al detalle); el **detalle por sesión NO se emite por defecto** (se pide con
  `--detail`). El registro neutral **por sesión** de 005-002 queda **byte-congelado** sin la bandera
  (INV-5). La regla R4 (total ≤ N × límite por sesión; límite normativo **por documento de sesión**)
  queda declarada **antes** del primer consumo multi-sesión.
- **D11 — la base real nunca se escribe (regla declarada + ausencia verificable).** La no-escritura se
  verifica sobre una **base temporal controlada**; la **concurrencia** se cubre con un **escritor
  activo** durante la lectura; en la **integración real** se comprueba **solo la lectura y los
  resultados** (sin exigir que la base quede inmóvil); **nunca** se intenta escribir en la base real.
- **Capacidades efectivas ligadas a versión/configuración.** `references/capabilities.md` declara cada
  capacidad como observada/documentada/no disponible/desconocida, con el **fallback portable**
  (archivos/enlaces) demostrado; **no** promete el contrato agente↔superficie de OpenChamber (no
  verificado). Sin dashboard/scheduler/fuente de estado nueva.
- **Referencia operativa:** `references/orientation.md`, `references/capabilities.md`,
  `references/project-start.md` §11, `references/context-meter.md` (R4);
  **ADR-025**; contrato normativo en `docs/specs/005-003-orientation-reduction/spec.md` (§2.1–§2.9,
  PD-1..PD-12, INV-1..INV-10).

### Política histórica (2026-09-13 — decisión de Capa 2 de cdad-010)

1. **Bloquear vectores directos y evidentes**, no bypasses hipotéticos: un
   agente con ganas de saltar las vallas siempre encontrará cómo.
2. **La expectativa se documenta** en skills y archivos de procedimiento:
   qué debe hacer el agente, qué no, y para qué.
3. **El agente debe SABER lo que se espera de él**: si no puede cumplir,
   devuelve la tarea explicando por qué; si cumple sin respetar el protocolo
   y sin motivo válido que pueda explicar, **la tarea se considera NO
   cumplida (fallida)** — aunque el artefacto exista.

**Definición operativa de "vector directo y evidente" (2026-09-13, N3 del
re-review de cdad-010):** un vector es directo y evidente si y solo si es
**demostrable con un probe de una sola invocación con output pegado** (Regla
de Oro). No califican: razonamientos sobre lo que el matcher "debería"
hacer, observaciones narradas sin paste, ni construcciones hipotéticas
multi-paso. Motivo: en el propio ciclo cdad-010, dos sesiones concluyeron
veredictos OPUESTOS sobre el mismo matcher ("compuestos pasan por prefijo"
vs "por segmento") — el que tenía probes pegados tenía razón. Cuando un
hallazgo de seguridad no pueda demostrarse con un probe de una invocación,
se registra como candidato de hardening con la premisa explícita a
verificar, nunca como bloqueante por intuición.

### Pares rtk `X*` + `rtk X*` (ADR-009)

Los modelos del workspace envuelven comandos en `rtk` (proxy CLI), así que
las allowlists por comando llevan SIEMPRE el par (`"pytest*"` y
`"rtk pytest*"`), con los subcomandos peligrosos de rtk denegados en todos
los roles. Matriz completa y razones: `docs/adr/ADR-009-politica-rtk-allowlists.md`.

### Feature de evidencia (2026-10-26, 007-005)

Una unidad de CDAD puede cerrarse **sin cambio de producto** cuando lo que aporta es **evidencia**:
demostrar en uso real un recorrido que el producto ya implementa. Reglas que quedaron observadas:

- **El resultado es un manifiesto verificable, no una narración.** Cada entrada lleva alias estable,
  ruta **parametrizada** (`<consumer>`, `<home>`, `<project>`), `sha256`, bytes, rol, comando
  reproducible, **cobertura de PC** y **límite declarado por entrada** (`cdad-evidence-manifest-v1`).
- **La resolución alias→ruta es privada y separada del manifiesto.** El manifiesto viaja al proyecto
  de proceso; la resolución (rutas reales, identidades de sesión) queda en el consumidor. Verificar
  exige **ambos** → el manifiesto es auditable sin publicar el entorno.
- **Lo no observado se declara, no se rellena.** Fallos de runtime, timeout, cuota, reparación y retiro
  aparecen como límites; un requisito **no observable** (p. ej. un intervalo de reloj que el producto no
  registra) se sustituye **contractualmente y con autorización**, declarando que el original **no se
  cumple** — nunca se repite el recorrido hasta que el registro «encaje».
- **Despacho entre proyectos: la sesión debe ser raíz del proyecto autorizado.** Una sesión creada en
  la raíz de CDAD es **rechazada por identidad** (`blocked` + `delivery=none`, sin registrar el
  intento): es el contrato, no un fallo. El rechazo **no acredita entrega** aunque la sesión haya
  ejecutado el trabajo, y su informe **no se usa como evidencia** (`deviation-2026-10-26.md`).
- **Recibir no aprueba.** El recibo válido deja `semantic_status=pending`; la aprobación del contenido
  y el gate son decisiones separadas.

Normativo en `docs/specs/007-005-serial-reception/{spec.md,closure.md,amendment-pc03.md}`; la
verificación se apoya en el verificador canónico del productor (**ADR-036**), no en un validador propio.

## Convenciones de tests

- **Framework**: bash + grep asserts (`assert_file_has`/`assert_file_not_has`).
- **Estructura**: `tests/*.sh` para invariantes de cdad-003; checks por
  feature en `docs/specs/<id>/VALIDATION.md` (mapeo check↔postcondición).
- Los checks se definen ANTES de editar (RED) y corren desde la raíz del repo.

## Tooling enforcement

- Sin CI aún: gate local = suite bash + checks VALIDATION (deuda registrada).
- Proyectos Odoo gestionados con CDAD: `make lint` (pre-commit-vauxoo,
  pinneado, --no-overwrite, host) + `make test/test-one/test-clean`.

## Anti-patrones del proyecto

- Orquestador escribiendo código/tests inline sin conmutar de modo (AP-10,
  §4). Implementer tocando tests (AP-4). "Verde" sin output (AP-3). Aprobación
  delegada al LLM (indelegable: Memory Bank, specs, priorización de review).

---

Última actualización: 2026-10-28 (008-004)

## Overlay de claves de usuario en artefactos desplegados (009-001)

Cuando un artefacto se despliega pero contiene valores que pertenecen al usuario (el `model` de cada agente),
el despliegue no puede tratar cualquier diferencia como conflicto: se declara la **lista de claves como
dato**, se reinserta sobre la versión nueva y se compara **contra el staging vigente antes** de invocar la
procedencia. La procedencia decide sólo cuando la base no es la versión actual (edición local real o upstream
movido). Ante gramática ambigua: se preserva y se informa — nunca se adivina ni se descarta en silencio.
Una sola definición del overlay, consumida por install, `--check`, la ruta legacy y el validador.

## Frontmatter OpenCode: una sola representación, decidida en el generador

La forma del frontmatter (hoy V2: `permissions:` como lista de `{action, resource, effect}`; `request.body` para `temperature`) la decide `scripts/cdad-generate.py` al generar. El instalador despliega el staging tal cual y `--check` compara el artefacto emitido más el overlay de claves de usuario (009-001): sin derivación en check ni conversor posterior. Cambiar la forma no cambia la política: los tests de equivalencia fijan reglas, globs, efectos y orden. El productor de agentes derivados debe emitir la misma forma; sus oráculos conservan también las reglas no propias y el cuerpo completo.
# Publicación del repositorio

La política operativa de publicación squash, autorizada por el usuario, está en
[`publication-policy.md`](publication-policy.md). Conserva el historial local
detallado y remoto publicado; cada entrega nueva añade un único commit remoto.
