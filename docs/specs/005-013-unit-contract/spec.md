> Spec **DRAFT (etapa 2, subetapa `draft`) — SIN APROBAR.** Texto del **architect**
> (`mofgw/deepseek-v4.1-flash`). **Corrección del draft** pedida por la review del orquestador Claude
> (`docs/specs/005-013-unit-contract/review-claude-spec-2026-10-14.md`, versionada en `2d3613a`), por la
> **fila 13** del plan del epic (`plan.md:46`) y por el criterio de review vigente del 2026-10-12
> (`docs/epics/epic-005-real-operation/execution.md:48-59`). **Esta entrega REEMPLAZA la spec aprobada por el
> orquestador OpenCode en `89165d7`:** esa aprobación queda **sustituida** y el contrato vuelve a estar
> **sin aprobar** hasta que el orquestador (HITL delegada del epic) o el dueño re-aprueben esta versión junto
> con el plan corregido. El architect **no** aprueba su propia propuesta (anti-sesgo). Contrato vigente:
> `docs/epics/epic-005-real-operation/plan.md`, **fila 13** (`:46`), sha256
> `63dda3b83561a8763a6b3ab9613f2b26029796921cdede4dfd65e7ab3ad059a6`, más la sección «Ajuste de los ciclos
> pendientes — decisión del dueño, 2026-10-11» (`:48-88`), que **prevalece sobre las filas** (`:57-58`).
> Deriva del discovery ya recibido, materializado y verificado
> (`docs/specs/005-013-unit-contract/discovery.md`, 399 líneas, sha256 `c58a8982…`), que se resuelve **por
> referencia** (§1-§13; no se repite). **Fuente única:** la spec **referencia** las reglas existentes (vista
> compacta de 005-003, planificación/unidad de 005-007, procedencia de 005-005, pin de aprobación y reemplazo
> de 005-001); toda extensión es **aditiva y declarada**; **no** se crea documento nuevo ni se duplica una
> regla. **Sin valores de este VPS ni rutas absolutas del dueño ni ids crudos de sesión** (`<home>`, `<repo>`,
> `<tmp>`, `<ses-…>`); **sin nombres de otros proyectos** (el fixture que imita la forma de planes de otro
> proyecto es **sintético y anónimo**: ids y títulos inventados, `<ID>`, `<otro-proyecto>`, `<ruta>`).

# Spec — 005-013-unit-contract

**Feature ID:** `005-013-unit-contract` · **Epic:** `epic-005-real-operation` · **Estado:** borrador (etapa 2,
**corrección del draft**; la aprobación de `89165d7` queda reemplazada).

## 0. Qué corrige esta versión (trazabilidad de la corrección)

Insumo principal: la review del orquestador Claude (`review-claude-spec-2026-10-14.md`). Se corrigen **dos
bloqueos de uso previsto** y **una precisión**, sin re-litigar las invariantes de la corrección (proyección
generada y pineada por digest, publicada una vez; recepción y resume contra el contrato recibido; clasificación
por identidad y clase de parte, sin juzgar prosa; frontera con 005-012):

| Punto | Qué pedía | Cómo lo resuelve esta spec |
|---|---|---|
| **B1.1** | localizar la unidad **estructuralmente** en cualquier plan (no por el título de la sección ni por igualdad exacta de la celda) | §2.1 **localizador estructural**: la **única fila** de una tabla del plan que contiene el id de la feature **como token completo**, con el **encabezado de esa tabla** (PD-1) |
| **B1.2** | si no se puede localizar sin ambigüedad, **no** fallar cerrado: volver al contrato vigente y informarlo | §2.2 **fallback declarado** a `approved-epic-plan` (plan completo) + informe en el diagnóstico y en `status` (PD-2) |
| **B1.3** | las anclas de historia y de autoridad se reconocen por una **declaración del producto**, no por listas por proyecto; sin ancla → `shared` (conservador); **desaparece la clase `authority`** | §2.3 **anclas declaradas en el activo del producto** (la plantilla del epic) + exclusión de historia + autorización etiquetada **sin efecto de veredicto** (PD-3); `impeded` sólo por autorización retirada (PD-10) |
| **B1.4** | la aceptación cubre **tres formas de plan** (este epic; uno de la plantilla del producto; un fixture anónimo con celda-enlace y sin historia) | §5 **AC-9** (tres formas) + los focales de T1/T2 del plan |
| **B2** | `impeded` necesita **línea base** y **salida** con mecanismos existentes (sin depender de 005-012) | §2.5 **línea base** = la proyección registrada del último paquete de la unidad (PD-7); **salida** = registrar la aprobación `epic-plan` bajo la HITL y el siguiente paquete toma la proyección nueva como línea base (PD-10) |
| **P1** | `status` **informa** y **no escribe**; el registro de impacto lo escribe sólo la operación de veredicto y es **idempotente** | §2.6 (PD-11 + PD-9) |

**Efecto buscado sobre el costo operativo (criterio vigente 2026-10-12).** La corrección **reduce** trabajo y
**no** agrega controles frágiles: (i) el localizador estructural y el fallback hacen que la feature sea
**aditiva con churn de oráculos casi nulo** — los fixtures de los planes de los tests existentes **no declaran
tabla de unidades** (verificado: `PLAN_BYTES = b"# Epic plan fixture …"` en
`tests/test_005_001_t1_role_approval.py:64`, `tests/test_005_001_t4_decisive.py:126`,
`tests/test_005_007_t4_architect_report_materialization.py:104`,
`tests/test_005_006_t5_acceptance.py:522`, `tests/test_004_002_t56_reviewfix.py:37`; `# Contract fixture for
<role>/<substage>` en `tests/test_role_packet_render.py:107`), así que caen en el **fallback** y conservan su
comportamiento; (ii) `impeded` reusa las causas y los marcadores **ya existentes** (`approval pending`,
`state incoherent`) y su salida es una operación que ya existe (registrar la aprobación); (iii) el journal de
impacto reusa la forma de `.superseded.json`; (iv) **no** hay listas de títulos por proyecto ni tests que
decidan el sentido de un párrafo.

## 1. Descripción funcional

El resultado es que **el hash identifique el contrato que recibió el agente** y que **la planificación del
proyecto deje de bloquearse globalmente** por editar el plan del epic.

Hoy el pin que bloquea el trabajo en curso es el **del paquete**: `contract.sha256` del `REQUEST.json` y
`active_packet.contract_sha256`, re-verificados contra los **bytes actuales** del archivo del contrato por
`validate_request` (`cdad_packet.py:824-827`, `:858`), punto único de `prepare`, `render`,
`validate-request`, `validate-packet`, `--resume-packet` y `receive` (`cdad_result.py:513`) — verificado en
el discovery §1, que **no se rehace**. Para el architect ese archivo es **el plan del epic completo**
(`_contract_for`, `:995-1008`; `validate_request`, `:814-819`): cualquier edición del plan —incluida
**agregar una unidad futura independiente**— cambia su sha y deja **irrecibible** una entrega correcta,
mientras `--replace-packet` sólo aplica a un paquete `prepared` y **rechaza** un `dispatched` nombrando la
reconciliación (PD-10, `:1958-1967`). La aprobación del architect **no** pinea hash (`_approved_epic_plan_entry`,
`:1346-1360`, D2) y `plan_sha256` de `epic_history` no tiene consumidores: es histórico/informativo.

La corrección es **una sola palanca**: el **contrato de una unidad** pasa a ser una **proyección generada
del plan** (objetivo, alcance y aceptación de la unidad + las restricciones compartidas que le aplican +
su aprobación y versión de origen), **publicada una vez** con sus bytes y **pineada por su digest**; el sha
del plan queda como **procedencia**. El hash deja de depender de la historia del plan y pasa a depender
**sólo de lo que la unidad recibe**.

Tres cambios, **una palanca por causa**, sobre fuentes que ya existen, **sin documento nuevo y sin segunda
copia**:

- **(a) La proyección de unidad (generada).** `prepare` del architect, con epic activo, **genera**
  determinísticamente la proyección de la unidad activa desde el plan (`docs/epics/<epic_id>/plan.md`):
  el **bloque de origen** + la **fila de la unidad** localizada **estructuralmente** (la única fila de una
  tabla del plan que contiene el id de la feature como token completo, con el **encabezado de esa tabla**) +
  **las secciones compartidas del plan** (todas las secciones de nivel `##` **excepto** las que la
  declaración del producto reconoce como **historia**). Se **publica una vez**, durable, y se **pinea su
  digest**. **No** se re-genera en cada validación (evita el hazard de byte-identidad verificado en el
  discovery §3: `_plan_task_sections` re-resuelve el plan en cada render, `:3225-3227`, y `_resume_packet`
  compara contra el render canónico, `:1839-1840`). Si la unidad **no se puede localizar sin ambigüedad**
  (ninguna fila o más de una), **no falla cerrado**: el contrato vuelve a ser el vigente
  (`approved-epic-plan`, el plan completo) y el motivo se informa en el diagnóstico y en `status`.
- **(b) Consecuencias por tipo de cambio.** Una operación **de lectura** compara la proyección **viva**
  (regenerada) con la **registrada** (los bytes que el paquete recibió, tomada del **último paquete de la
  unidad**) **por parte etiquetada** y emite un veredicto de tres valores: `current` (sin efecto), `impact`
  (registra el impacto durable y el orquestador decide cómo reconciliarlo) o `impeded` (**autorización
  retirada**: impide las acciones afectadas, fallando cerrado, con la salida existente).
- **(c) Recepción y resume contra el contrato recibido.** La validación de un paquete de unidad se hace
  contra la **proyección registrada** (los bytes durables que el paquete recibió), **no** contra el archivo
  vivo del plan. La recepción ya es neutral (`semantic_status: pending`, materialización con
  `approval_effect: false`, transición sólo del orquestador; `re-entry.md:54-63`): **no** se amplía
  autoridad, **no** se aprueba al recibir y **no** se toca el esquema del recibo.

**Frontera de la mejora (no negociable).** Desbloquear la planificación **no** habilita: omitir gates,
aprobar al recibir, declarar válido un contrato cambiado ni reabrir el pin de la spec de los roles de
construcción (I2/PD-18). El veredicto de consecuencia **no** juzga el sentido de un texto: eso lo juzga la
review.

### 1.1 Recorrido de uso objetivo (el caso que hoy se rompe)

1. **Orquestador** despacha al architect: `prepare` (rc=0; el `contract.sha256` queda pineado al **digest
   de la proyección**, no al sha del plan), `validate-*`, `cdad_continuity begin`, `--record-dispatch`
   (`prepared → dispatched`).
2. Se edita el plan para **agregar una unidad futura independiente** (una fila más) y se registra el
   cambio en la sección de historia del plan (la que la declaración del producto reconoce: «Cambios al
   plan» en este epic, «Plan changes» en la plantilla del producto).
3. **Después:** la proyección de la unidad activa **no cambió** (ni su fila, ni las secciones compartidas,
   ni la historia —excluida—) → el paquete despachado sigue válido → `receive` **rc=0** contra el contrato
   que el agente efectivamente recibió (`packet_validation` / `identity_validation` passed,
   `semantic_status: pending`). El veredicto de consecuencia es `current`.
4. **Caso que sí exige reconciliación:** cambiar el **alcance o una dependencia** de la unidad activa
   (su fila) o una **sección compartida** → la proyección **viva** difiere → veredicto `impact` (registro
   durable) y decide el orquestador. **Retirar la autorización** (sin entrada `epic_history` `epic-plan`
   con `approved_by`, o `hitl_delegation` revocada) → veredicto `impeded` (falla cerrado); **registrar la
   aprobación** de nuevo → `prepare` rc=0 y el paquete nuevo toma la proyección nueva como línea base.
5. **Caso de fallback:** un plan cuya unidad no se localiza sin ambigüedad (p. ej. un plan sin tabla de
   unidades) → **no** se publica proyección; el contrato es el plan completo (`approved-epic-plan`) y el
   motivo se informa; `receive`/`resume` se comportan como hoy (validan contra los bytes vivos del plan).

## 2. Contrato observable

### 2.1 (a) La proyección de unidad (`unit-projection-v1`) y su localizador estructural

- **Qué es.** Un documento de texto **generado** (no mantenido a mano) con tres bloques:
  1. **Origen (procedencia; NO es parte de la clasificación).** `unit` (id de la unidad activa),
     `plan` (ruta del plan del epic), `plan_sha256` (sha del plan **al generar**), `approved_by` (de la
     entrada `epic_history` `epic-plan` que autoriza) y `policy_sha256`; la lista de **partes** con su
     **clase** (`unit` | `shared`); y la **traza del localizador** (el encabezado de la tabla usada y el
     título de la sección que la contiene) y de las **anclas** reconocidas. Es **procedencia**: registra de
     dónde salió la proyección, no un pin nuevo.
  2. **Parte `unit`.** El **encabezado** de la tabla que localizó la unidad (su fila de encabezado y su
     separador) y **la fila de la unidad activa** —la **única** fila de cuerpo de una tabla del plan que
     contiene `execution.feature_id` **como token completo**— **verbatim**. Es el objetivo/alcance/aceptación
     de la unidad y sus dependencias (`plan.md:32-46`; la fila 13 es 1 línea / 1485 bytes).
  3. **Partes `shared`.** **Cada** sección de nivel `##` del plan **verbatim** (encabezado + cuerpo),
     **excepto**: (i) las secciones que la **declaración del producto** reconoce como **historia** (se
     excluyen; ver abajo) y (ii) la **tabla que localizó la unidad**, cuyas líneas (encabezado, separador y
     **todas** sus filas de cuerpo) se **remueven** de la sección que la contiene (las demás líneas de esa
     sección quedan verbatim; si no queda cuerpo, la parte es su encabezado). Incluye, entre otras,
     «Ajuste de los ciclos pendientes» (`:48-88`, que **prevalece sobre las filas**, `:57-58`), «Criterios
     de aceptación del epic» (`:90-111`), «Operación» (`:119-126`) y «Autoridad» (`:128-134`). La
     **sobre-inclusión** de las partes `shared` es deliberada (conservador, declarado; ver D-7).
- **Localizador estructural (B1.1).** La unidad se localiza **sin** mirar el título de la sección y **sin**
  exigir igualdad exacta de la celda: se recorren las **tablas** del plan (fila de encabezado + separador +
  filas de cuerpo) y se busca la fila de cuerpo que contiene el id de la feature **como token completo**
  (delimitado por caracteres que no pueden ser parte de un id: `[A-Za-z0-9._-]`). La **única** fila
  encontrada es la unidad, y su **tabla** (encabezado + separador) da el encabezado de la parte `unit`. La
  celda puede ser un **enlace** (`[<ID> — <título>](<ruta>)`), llevar texto alrededor o estar entre
  backticks: la localización no depende de su forma. Esto funciona en las formas reales del producto
  (verificado: `docs/epics/epic-005-real-operation/plan.md:30-32` «Entregas», encabezado
  `| Orden | Feature | … |`; `docs/epics/epic-003-context-efficiency/plan.md:78-80` «Entregas del MVP»;
  `docs/epics/epic-004-single-source-planning/plan.md:111-113` «Descomposición candidata», columna
  «Feature candidata»; `docs/epics/epic-001-superpowers-gaps/plan.md:39-41` y
  `docs/epics/epic-002-cdad-audit-fixes/plan.md:82-84` «Decomposición en features», columna «Feature ID»;
  `skills/cdad-epic/assets/epic-plan-template.md:25-27` «Decomposition into features», columna «Feature
  ID»), y en planes de otros proyectos cuya celda es un enlace y no declaran historia ni autoridad.
- **Ambigüedad → fallback (B1.2).** Si **ninguna** fila o **más de una** fila contiene el id como token
  completo, la proyección **no se genera ni se publica** y el contrato del paquete vuelve al **vigente**
  (`approved-epic-plan`, `docs/epics/<epic_id>/plan.md`, el plan completo y su digest) — §2.2. El motivo
  (cero filas / más de una, con la ruta del plan) se informa en el **diagnóstico** (stderr de `prepare`) y
  en el bloque `unit_contract` de `status` (`mode: "fallback"`). **No** es un error: `prepare` rc=0.
- **Regla determinista; sin listas de palabras.** La selección es **estructural** (por fila de tabla y por
  encabezado de sección contra una **declaración del producto**), no semántica. **No** hay listas de títulos
  por proyecto, ni heurísticas de prosa, ni listas de palabras.
- **Por qué se excluye la historia.** Es el registro de cada edición y de cada cambio de hash; incluirla
  haría que cualquier edición —incluida la propia historia— cambiara la proyección y volviera a invalidar
  todo, que es el problema a resolver.
- **Por qué la tabla se reduce a la fila activa.** Incluir las filas de **otras** unidades haría que
  **agregar una unidad futura independiente** cambiara la proyección → rompería (b)(i). Las demás líneas de
  la sección que contiene la tabla **sí** se conservan (nada relevante se pierde por excluir las filas
  ajenas).
- **El digest se calcula sobre la proyección entera** (origen + partes). El **origen** es procedencia: la
  **clasificación** de (b) compara **sólo las partes** (`unit` + `shared`), de modo que un cambio de plan
  que **no** toca las partes (p. ej. sólo la historia) **no** produce efecto aunque cambie el `plan_sha256`
  del origen.
- **Frontera declarada (no se sigue la dependencia).** La parte `unit` **nombra** las dependencias de la
  unidad (su columna), pero la proyección **no** incluye las filas de las unidades de las que depende
  (serían filas ajenas; ver D-7). Es una frontera declarada de la v1.

### 2.2 (a) Ubicación, pin, kind/path y fallback

- **Ubicación y publicación única.** La proyección se publica **una vez**, durable, en el directorio del
  paquete: `.cdad/packets/<packet_id>/UNIT-CONTRACT.md`. Los directorios de paquete **nunca se reescriben**
  (INV-3 de 005-001: los bytes del paquete anterior quedan byte a byte idénticos), así que la proyección
  registrada es **inmutable** por construcción. Se publica en la **misma generación** que el paquete.
- **Pin.** Cuando la unidad se localiza, el objeto `contract` del paquete del architect es
  `{kind: "approved-unit-contract", path: ".cdad/packets/<packet_id>/UNIT-CONTRACT.md", sha256: <digest de
  esos bytes exactos>, commit: null}`; `state.active_packet.contract_sha256` es **ese** digest. El sha del
  plan **no** es el pin: queda en el bloque de origen.
- **Fallback (B1.2).** Cuando la unidad **no** se localiza sin ambigüedad, el objeto `contract` es el
  **vigente**: `{kind: "approved-epic-plan", path: "docs/epics/<epic_id>/plan.md", sha256: <digest de los
  bytes del plan>, commit: null}`; **no** se publica `UNIT-CONTRACT.md`; `prepare` rc=0 y el aviso va a
  **stderr** (stdout sigue siendo el `PACKET.md` byte a byte, contrato congelado de `prepare`:
  `tests/test_packet_prepare.py:206`, «stdout == `PACKET.md` == render»). Consecuencia: en fallback la
  recepción y el resume validan contra los **bytes vivos** del plan, es decir, el comportamiento de hoy
  (se pierde el beneficio de la proyección, no hay regresión).
- **kind/path.** `VALID_CONTRACT_KINDS` (`:52`) admite `approved-unit-contract` **además** de
  `approved-epic-plan` (que **se conserva**: es el contrato del fallback y el kind declarado histórico, D-2).
  `validate_request` (`:814-819`) acepta, para el architect con epic activo, **exactamente**:
  `kind == "approved-unit-contract"` **y** `path == ".cdad/packets/<document.packet_id>/UNIT-CONTRACT.md"`,
  **o** el par vigente `("approved-epic-plan", "docs/epics/<epic_id>/plan.md")` (el fallback). Un `kind`/`path`
  distinto falla cerrado con el diagnóstico existente `contract kind/path does not match role and execution`.
- **No re-generación en la validación.** Ninguna validación regenera la proyección: `validate_request`
  lee el archivo en `contract.path` y compara su digest (`:824-827`), como hoy. Ese archivo es la
  proyección registrada (o, en fallback, el plan).

### 2.3 (a) Las anclas: declaración del producto, no listas por proyecto (B1.3)

- **Una sola declaración, del producto.** El producto **declara** en su **plantilla del plan de epic**
  (`skills/cdad-epic/assets/epic-plan-template.md`, el activo que `epic-planning.md` manda cargar y
  completar, `:73`) y en **forma legible por máquina**, los títulos que sus planes usan para dos anclas:
  **historia** (el registro de cambios del plan) y **autorización** (la sección que declara la autoridad del
  epic). La declaración cubre las convenciones que el **propio producto** usa: el título inglés de la
  plantilla y la forma en español de los planes del producto («Plan changes» / «Cambios al plan»;
  «Stakeholders» / «Autoridad»). **No** hay listas por proyecto: un plan que no declara ninguna de las anclas
  no aporta nada a la lista, y su contenido cuenta como `shared` (conservador).
- **Reconocimiento.** Una sección `##` **es** el ancla cuando su título, normalizado (minúsculas, espacios
  colapsados), **es igual** al título declarado **o empieza por él seguido de un separador no alfanumérico**
  (así `Autoridad (decisión del dueño)` reconoce el ancla `Autoridad`). Determinista y estructural.
- **Efecto de cada ancla.**
  - **Historia** → sus secciones **se excluyen** de la proyección (incluirlas haría que cualquier edición
    cambiara la proyección).
  - **Autorización** → su sección **se incluye** como parte `shared` (conservador: una edición produce
    `impact` y **no** bloquea) y se **etiqueta** en el origen como la parte de autorización (procedencia).
    **No tiene efecto de veredicto**: la **clase `authority` desaparece** y lo único que produce `impeded`
    es **retirar la autorización** (PD-10).
- **Si un plan no declara las anclas.** No es un error y **no** falla cerrado: sin ancla de historia, todas
  las secciones del plan son partes `shared` (una edición de la historia produce `impact`, conservador); la
  ausencia del ancla de autorización no cambia nada (la autorización vive en el **state**, no en el plan).
- **Si la declaración del producto no se puede leer** (activo ausente o ilegible): **no** se reconoce
  ninguna ancla (conservador; el localizador de la unidad sigue funcionando y `prepare` rc=0). No se agrega
  un camino de falla cerrada nuevo.

### 2.4 (b) Consecuencias por tipo de cambio (`change-consequence-v1`)

- **Veredicto de tres valores, por parte.** La operación **regenera** la proyección viva (de sólo lectura)
  y la compara con la **registrada** **parte por parte** (`unit` + cada `shared`), **ignorando el origen**:
  - **`current` (sin efecto).** Ninguna parte difiere. Cubre **agregar una unidad futura independiente**,
    **modificar otra** unidad sin dependencias compartidas y **editar la historia** del plan: no registra
    impacto ni impide nada.
  - **`impact` (registra el impacto y decide el orquestador).** Alguna parte `unit` o `shared` difiere
    (alcance/dependencia de la unidad activa, o una sección compartida —incluida la de autorización—). Se
    **registra** un **registro durable de impacto** con la forma del journal `.superseded.json`
    (`:2078-2086`): `reason`, `contract_sha256_old`, `contract_sha256_new` y `changed_parts` (las partes que
    difieren). El registro **no** aprueba, **no** cambia `semantic_status` y **no** bloquea la recepción del
    paquete ya despachado (2.6). La **decisión** de reconciliación la registra el **orquestador** en el
    campo `note` de `stage_history` (no la escribe el CLI; INV-2 de 005-001).
  - **`impeded` (impide las acciones afectadas).** Falla cerrado (rc=2, sin efectos) cuando **se retiró la
    autorización**: no existe la entrada `epic_history` `epic-plan` con `approved_by` para el epic activo
    —el caso ya cubierto por `approval pending`, `:1406-1411`—, o la `hitl_delegation` está revocada o
    vencida —el caso ya cubierto por `state incoherent`/vigencia—. La acción afectada (preparar/despachar
    bajo la unidad) **no procede** hasta que la autorización se restituya (2.5). **Ninguna** sección del plan
    produce `impeded` por sí sola.
- **Dónde se etiqueta «aplicación inmediata» (VERIFY del discovery §4, resuelto).** La etiqueta **vive en
  la proyección**: cada parte lleva su **clase** (`unit` | `shared`) en el bloque de origen, y la parte de
  autorización —reconocida por la **declaración del producto** (§2.3)— queda **etiquetada** allí. El CLI
  **no** decide el significado de un párrafo por listas de palabras: clasifica por **identidad de parte** y
  **clase de parte**. La inmediatez de una **restricción** es un **juicio humano** (review/orquestador), que
  se registra en la nota de impacto; el CLI aporta el registro durable y los marcadores, no el juicio.
- **Vocabulario de marcadores (reusado).** `approval pending` (autorización retirada), `state incoherent`
  (delegación revocada), `packet obsolete` (nombra la reconciliación de un paquete `dispatched`). No se
  inventa un vocabulario nuevo para las causas ya cubiertas.

### 2.5 (b) Línea base del veredicto y salida del impedimento (B2)

- **Línea base declarada.** La proyección **registrada** con la que se compara la viva es la del **último
  paquete de la unidad**: el paquete de la feature activa cuyo `UNIT-CONTRACT.md` se publicó **más
  recientemente** (orden por la fecha de publicación del archivo; empate → el id de paquete mayor; el
  `active_packet` del state cuenta como candidato). Si la unidad **no tiene** ningún paquete con proyección
  registrada, **no hay** línea base: el veredicto es `current` (no hay nada que comparar) y el `prepare`
  publica la proyección, que pasa a ser la línea base de los siguientes.
- **Salida del `impeded` con mecanismos existentes (sin depender de 005-012).** El impedimento lo levanta
  **registrar una nueva aprobación `epic-plan`** en `epic_history` para el epic activo (con `approved_by`),
  bajo la **HITL** vigente del epic —la misma operación que hoy habilita al architect (D1/D2,
  `:1346-1360`)— o **restituir** la `hitl_delegation`. Con la autorización restituida, `prepare` → **rc=0**
  y el **paquete nuevo publica la proyección nueva**, que pasa a ser la línea base del siguiente veredicto.
  **No** se define acá ninguna operación de reconciliación de un paquete `dispatched` (territorio de
  005-012; no se inventa).
- **Por qué alcanza.** El `impeded` no depende de una comparación de bytes ni de un juicio sobre prosa: es
  la **ausencia/revocación de la autorización**, un hecho del state que ya tiene marcador y que ya tiene una
  operación de registro. Así, editar legítimamente una sección del plan (incluida la de autorización)
  **nunca** deja la unidad bloqueada sin salida: da `impact` y decide el orquestador.

### 2.6 (c) Recepción y resume contra el contrato recibido

- **Validación contra la proyección registrada.** `render`, `validate-request`, `validate-packet`,
  `prepare --resume-packet` y `receive` validan el paquete del architect contra los **bytes registrados en
  `contract.path`** (la proyección durable), **nunca** contra el archivo vivo del plan. Como el
  `contract.path` **es** la proyección registrada, esto se logra **por la ubicación/pin** (2.2), sin cambiar
  la lógica de `receive`. En **fallback**, `contract.path` es el plan: se valida contra sus bytes vivos
  (comportamiento de hoy).
- **Efecto observable.** Tras **agregar una unidad futura independiente** (o editar la historia),
  `receive` de un paquete despachado del architect → **rc=0**, con `packet_validation` e
  `identity_validation` `passed` y `semantic_status: pending`; el recibo es **idéntico en esquema**
  (`cdad_result.py:550-578`) y **no** guarda `contract_sha256`.
- **Neutralidad conservada.** Recibir **no** aprueba (`semantic_status` siempre `pending`, `:575-576`);
  la materialización es CAS con `approval_effect: false`; la transición del state es **sólo** del
  orquestador (`re-entry.md:57-63`). No se amplía autoridad; no se toca el esquema del recibo.

### 2.7 (a) Origen y aprobación de la proyección

- **Origen registrado.** El bloque de origen (2.1) registra: **id de la unidad**, **path del plan**,
  **sha del plan al generar**, la **entrada `epic_history` `epic-plan` aprobadora** (`approved_by`) y
  **`policy_sha256`** (de la ejecución), más la traza del localizador y las anclas. Las entradas
  `epic_history` `epic-plan` de epic-005 ya llevan `plan_path`, `plan_sha256`, `evidence` y `note`: se
  **reutilizan como origen**, no como pin.
- **No re-aprobación por unidad si la proyección no cambió.** La autorización del architect **sigue** siendo
  la entrada `epic_history` `epic-plan` con `approved_by` (**sin** pin de hash; D1/D2, `:1346-1360`;
  `project-execution.md:60-63`). Si la proyección **no** cambió, **no** se re-aprueba nada. Si **cambió**,
  **no** se re-aprueba automáticamente: decide el orquestador (2.4, `impact`).
- **Frontera.** El **pin de la spec** de los roles de construcción (I2/PD-18; `specification` con
  `contract_path` + `contract_sha256`, `_contract_approval_for` `:1425-1430`) **no se toca**. Esta feature
  es sobre el plan/unidad y su architect.

### 2.8 (b) Superficie del veredicto: `validate-unit-contract` y el bloque `unit_contract` de `status` (P1)

- **Operación de veredicto.** `python3 <skill-dir>/scripts/cdad_packet.py validate-unit-contract
  --project-root <ABS>`: operación **de lectura** que regenera la proyección viva, la compara con la
  **línea base** (2.5) por parte y emite el veredicto (`current` | `impact` | `impeded`) con las partes que
  difieren. `rc=0` para `current`/`impact`; `rc=2` para `impeded` (falla cerrado, sin efectos).
- **El registro de impacto lo escribe sólo esta operación, y es idempotente.** Sólo
  `validate-unit-contract` escribe el **registro durable de impacto** (y sólo en el caso `impact`), en el
  directorio del **paquete de la línea base** (`.cdad/packets/<baseline_packet_id>/.impact.json`), con la
  forma del journal `.superseded.json` (precedente exacto de un registro durable por cambio de contrato,
  `:2078-2086` y su publicación como archivo nuevo en el directorio del paquete, `:2103`). Es
  **idempotente**: un registro cuyo par `(contract_sha256_old, contract_sha256_new)` ya está presente **no
  se duplica** (correr la operación dos veces con el mismo par deja los bytes del journal idénticos).
- **`status` es de SOLO LECTURA y sólo informa (P1).** El bloque **aditivo** `unit_contract` de la vista
  compacta (`status`) **informa** el veredicto y **no escribe nada**: no publica la proyección, no escribe
  el state ni el journal. Es el contrato de sólo lectura de 005-003 (`compact-view-v1`, «read-only: no
  escribe el estado ni ningún archivo», PD-1/INV-1 de 005-003) y de 005-011 (INV-1: `status` deja el state
  byte-idéntico). El bloque es **aditivo** (no relaja ningún campo existente de la vista; INV-4 de 005-011)
  y acotado (ids, digests, veredicto, motivo y partes que difieren; **no** incluye los bytes de la
  proyección, así que no compromete el límite de bytes de la vista).
- **Forma del bloque (fijada para que sea testeable; ajustable por el orquestador sin cambiar el
  comportamiento observable):**
  `unit_contract: {mode: "projection"|"fallback", unit, registered: {packet_id, sha256}|null,
  live: {sha256}|null, verdict: "current"|"impact"|"impeded"|null, changed_parts: [...], reason}`.

## 3. Postcondiciones (numeradas y verificables)

**PD-1 (proyección generada, determinista, con localizador estructural).** Con epic activo `E` y una unidad
activa `F`, `prepare --role architect` (cualquier subetapa válida) **genera** la proyección de unidad de `F`
desde `docs/epics/E/plan.md` según 2.1: bloque de origen + parte `unit` (el **encabezado de la tabla que
contiene el id de `F` como token completo** + la **única** fila de cuerpo que lo contiene, verbatim) +
partes `shared` (todas las `##` menos las de historia y con las líneas de esa tabla removidas). Los
**mismos** bytes de plan + unidad + insumos de origen producen los **mismos** bytes de proyección. La
localización **no** depende del título de la sección ni de la igualdad exacta de la celda (funciona con la
celda como enlace, con texto alrededor y entre backticks).

**PD-2 (ambigüedad → fallback declarado, sin falla cerrada).** Si **ninguna** fila o **más de una** fila de
una tabla del plan contiene el id de `F` como token completo, `prepare --role architect` → **rc=0**; **no**
se publica `UNIT-CONTRACT.md`; el `contract` del paquete es
`{kind: "approved-epic-plan", path: "docs/epics/E/plan.md", sha256: <sha del plan>, commit: null}`; el
**motivo** (cero o más de una fila, con la ruta del plan) se informa en el diagnóstico (stderr; stdout sigue
siendo el `PACKET.md` byte a byte) y en `status` (`unit_contract.mode == "fallback"` + `reason`). En
fallback, `receive`/`resume` validan contra los bytes vivos del plan (comportamiento de hoy).

**PD-3 (anclas por declaración del producto; sin clase `authority`).** Las anclas de **historia** y de
**autorización** se reconocen contra la **declaración legible por máquina del producto** en la plantilla del
plan de epic (`skills/cdad-epic/assets/epic-plan-template.md`), **nunca** contra una lista por proyecto. Las
secciones de historia **se excluyen** de la proyección; la sección de autorización **se incluye** como parte
`shared` y **etiquetada** en el origen, **sin** efecto de veredicto (la clase `authority` **no** existe). Un
plan sin anclas → ninguna exclusión (conservador: sus secciones son `shared`); una declaración ilegible →
ninguna ancla reconocida; ninguno de los dos casos falla cerrado.

**PD-4 (publicación única y pin por digest).** `prepare --role architect` publica la proyección en
`.cdad/packets/<packet_id>/UNIT-CONTRACT.md` en la **misma** generación que el paquete; el `contract` del
paquete es `{kind: "approved-unit-contract", path: <esa ruta>, sha256: sha256(<esos bytes>), commit: null}`
y `active_packet.contract_sha256` es ese digest. **Ninguna** operación posterior reescribe la proyección;
una segunda generación para `F` crea **otro** paquete (otra ruta) y **no** toca los bytes del anterior.
**Borde:** `sha256(UNIT-CONTRACT.md) == contract.sha256 == active_packet.contract_sha256`.

**PD-5 (kind/path reconocido por rol; sin romper la verificación).** `approved-unit-contract` ∈
`VALID_CONTRACT_KINDS` (`:52`) y `approved-epic-plan` **se conserva**. `validate_request` acepta para el
architect el par exacto `("approved-unit-contract", ".cdad/packets/<packet_id>/UNIT-CONTRACT.md")` **o** el
par vigente `("approved-epic-plan", "docs/epics/<epic_id>/plan.md")`, y **rechaza** cualquier otro par con
`contract kind/path does not match role and execution` (rc=2, sin efectos). La verificación del digest
(`:824-827`) y del binding de `active_packet` (`:851-859`) **no** cambian.

**PD-6 (recepción y resume contra el contrato recibido).** Con un paquete del architect `dispatched` cuyo
`contract.path` es la proyección registrada, tras **agregar una unidad futura independiente** al plan (y
registrar el cambio en la sección de historia), `receive` → **rc=0** (`packet_validation`/
`identity_validation` `passed`, `semantic_status: pending`), y `prepare --resume-packet <id>` re-emite el
paquete **byte a byte** si no cambió su render canónico. La recepción **no** aprueba y el esquema del recibo
**no** cambia. **Control interno:** editar el **alcance de la unidad activa** **no** altera la recepción
(valida los bytes registrados) pero **sí** cambia el veredicto de PD-9.

**PD-7 (línea base del veredicto).** La comparación de PD-8/PD-9 usa como **registrada** la proyección del
**último paquete de la unidad** (publicación más reciente de `UNIT-CONTRACT.md` de la feature activa;
empate → id de paquete mayor; el `active_packet` cuenta como candidato). Sin paquete previo con proyección,
**no** hay línea base y el veredicto es `current`. La línea base **se declara** en el veredicto
(`registered.packet_id` + `registered.sha256`).

**PD-8 ((b)(i) sin efecto → `current`).** El veredicto compara la proyección viva con la registrada **por
parte** (ignorando el origen). Cuando **sólo** cambió contenido excluido o no incluido (otra fila de la
tabla de unidades, la historia del plan) o el `plan_sha256` del origen, el veredicto es **`current`**: **no**
se registra impacto, **no** se impide nada y la recepción (PD-6) procede. **Borde:** agregar una fila a la
tabla de unidades deja la parte `unit` y todas las `shared` **idénticas**.

**PD-9 ((b)(ii) registra el impacto; idempotente).** Cuando difiere la parte `unit` o alguna `shared`, el
veredicto es **`impact`**: `validate-unit-contract` escribe un **registro durable de impacto** en
`.cdad/packets/<baseline_packet_id>/.impact.json` (forma de `.superseded.json`, `:2078-2086`: `reason`,
`contract_sha256_old`, `contract_sha256_new`, `changed_parts`) y se nombra la decisión del orquestador; el
registro **no** aprueba, **no** cambia `semantic_status` y **no** bloquea la recepción del paquete ya
despachado. Es **idempotente**: con el **mismo par de digests**, correr la operación de nuevo **no** duplica
el registro (journal byte a byte idéntico). La decisión se registra en `stage_history.note` (orquestador; el
CLI no escribe el state). **Borde:** el veredicto nombra las **partes** que difieren, nunca el sentido de un
texto.

**PD-10 ((b)(iii) `impeded` = autorización retirada, con salida).** El veredicto es **`impeded`** (rc=2,
sin efectos) **sólo** cuando se **retiró la autorización**: no hay entrada `epic_history` `epic-plan` con
`approved_by` para el epic activo (`approval pending`, `:1406-1411`) o la `hitl_delegation` está revocada o
vencida (`state incoherent`/vigencia). La acción afectada —preparar un paquete nuevo para la unidad— **no**
procede; el diagnóstico nombra la autorización retirada y la **salida**: **registrar la aprobación
`epic-plan`** en `epic_history` bajo la HITL (o restituir la delegación). Con la autorización restituida,
`prepare` → **rc=0** y el paquete nuevo **publica la proyección nueva**, que pasa a ser la línea base
(PD-7). Ninguna sección del plan produce `impeded`. **Control interno:** con la autorización vigente y sin
cambio en las partes, `prepare` → rc=0.

**PD-11 (`status` informa y no escribe; el journal sólo por la operación de veredicto).** El bloque
`unit_contract` de la vista compacta **informa** `mode` (`projection` | `fallback`), la línea base, el
digest vivo, el veredicto, las partes que difieren y el motivo, y **no escribe nada** (state byte-idéntico,
sin proyección nueva, sin journal). El registro de impacto lo escribe **sólo** `validate-unit-contract`
(PD-9). **Borde:** dos `status` consecutivos dejan el proyecto **byte a byte** idéntico; `status` nunca crea
`.impact.json`.

**PD-12 (origen y no re-aprobación por unidad).** El bloque de origen registra `unit`, `plan`,
`plan_sha256` (al generar), `approved_by` (de la entrada `epic-plan` aprobadora) y `policy_sha256`, más la
traza del localizador y las anclas. La autorización del architect **sigue** siendo la entrada
`epic_history` `epic-plan` **sin** pin (D1/D2). Si la proyección no cambió, **no** se re-aprueba por unidad;
si cambió, decide el orquestador (PD-9), sin re-aprobación automática. **Frontera:** el pin `specification`
de los roles de construcción (I2/PD-18) **no** se toca (INV-5).

**PD-13 (fuente única y extensión aditiva).** La spec **no** agrega una segunda copia de una regla
existente: **referencia** la vista compacta (005-003), la planificación/unidad (005-007), la procedencia
(005-005) y el pin/reemplazo (005-001). **No** se crea un bloque `plan-tasks` **mantenido a mano** dentro
del plan del epic (sería una segunda declaración de datos que la tabla ya contiene): la proyección se
**genera**. Toda extensión (el kind `approved-unit-contract`, el bloque `unit_contract` de la vista, la
declaración de anclas del producto, el journal de impacto) es **aditiva y declarada**; los campos, kinds y
reglas existentes se conservan.

## 4. Invariantes (verificables)

- **INV-1 (el CLI no escribe aprobaciones).** Ninguna operación de esta feature escribe
  `epic_history`/`stage_history`; el registro de impacto es un journal durable, no una aprobación (reusa la
  disciplina de 005-001 INV-2).
- **INV-2 (determinismo de la proyección).** Los mismos bytes de plan + unidad + insumos de origen
  producen los mismos bytes de proyección (mismo digest).
- **INV-3 (inmutabilidad del pin).** Una proyección publicada **nunca** se reescribe; una nueva generación
  para la misma unidad crea un paquete/proyección nuevos y los bytes del anterior quedan **byte a byte
  idénticos**. El journal de impacto es un **archivo nuevo** en el directorio del paquete de la línea base
  (precedente `.superseded.json`, `:2103`), no una reescritura de los bytes del paquete.
- **INV-4 (fuente única; sin mantenimiento documental).** No hay segunda copia de una regla existente ni un
  bloque `plan-tasks` mantenido a mano en el plan del epic; la proyección se **genera** y las reglas se
  **referencian**. La declaración de anclas vive **una sola vez**, en el activo del producto.
- **INV-5 (frontera con el pin de la spec).** El pin `specification` (path+sha, PD-18 de 005-001) **no** se
  relaja ni se toca; la frontera del discovery §6 se conserva.
- **INV-6 (sin paralelismo).** La feature **no** habilita varias unidades a la vez sobre el mismo state:
  `active_packet` sigue siendo único (fuera de alcance de la fila 13).
- **INV-7 (sin valores de este VPS; anonimización).** Sin rutas absolutas del dueño, sin rutas de HOME,
  sin ids crudos de sesión, sin servidores ni configuración local del host y **sin nombres de otros
  proyectos**, en el **contenido del contrato** (spec, plan y producto). El fixture que imita la forma de
  planes de otro proyecto es **sintético y anónimo**. La cabecera de la entrega nombra el modelo que
  entrega, como en los drafts anteriores del epic (registro de la entrega, no parte del contrato).
- **INV-8 (el CLI no juzga prosa).** El veredicto de consecuencia es por **identidad y clase de parte**; el
  significado de un texto lo juzga la **review** (criterio del dueño). No se piden tests que decidan el
  sentido de un párrafo por listas de palabras, ni listas de títulos por proyecto.
- **INV-9 (read-only salvo su propio journal).** `status` **nunca** escribe (PD-11). La operación de
  veredicto **no** escribe el state ni un paquete; sólo, en el caso `impact`, su registro durable de impacto
  (idempotente).
- **INV-10 (portabilidad de la proyección).** La selección de la unidad y de las anclas **no** depende de
  títulos propios de este plan ni de una lista por proyecto: la unidad se localiza **estructuralmente** y
  las anclas por una **declaración del producto**; un plan que no las declara se trata de forma
  **conservadora** (`shared`), nunca fallando cerrado.

## 5. Criterios de aceptación (medibles)

La meta es la de la **fila 13** (`plan.md:46`): **despachar un architect, agregar una feature independiente
al plan y recibir su entrega normalmente; después comprobar que un cambio relevante sí exige
reconciliación.** Con el **CLI REAL** sobre un **proyecto descartable** (nunca este repo, nunca HOME).

- [ ] **AC-1 (PD-1/PD-3).** Un `prepare --role architect` real produce la proyección (`UNIT-CONTRACT.md`)
      con el bloque de origen, la parte `unit` localizada **estructuralmente** (encabezado de la tabla + la
      única fila con el id como token completo) y las secciones compartidas; su digest coincide con
      `contract.sha256` y con `active_packet.contract_sha256`; las anclas se reconocen contra la
      **declaración del producto** y la historia queda excluida. En un plan cuya celda de unidad es un
      **enlace** (`[<ID> — <título>](<ruta>)`) la localización funciona igual.
- [ ] **AC-2 (PD-2).** Un plan cuya unidad no se localiza sin ambigüedad (cero filas, o dos filas con el id)
      → `prepare` **rc=0** con `kind`/`path` = `approved-epic-plan` / `docs/epics/<epic>/plan.md`, **sin**
      `UNIT-CONTRACT.md` en el directorio del paquete, con el motivo en el **diagnóstico** (stderr) y en
      `status` (`mode: "fallback"`). **PD-3:** un plan sin anclas declaradas no falla cerrado (sus secciones
      son `shared`).
- [ ] **AC-3 (PD-4/PD-5).** La proyección se publica una vez, en la misma generación; `sha256(UNIT-CONTRACT.md)
      == contract.sha256 == active_packet.contract_sha256`; el par exacto `approved-unit-contract` +
      `.cdad/packets/<packet_id>/UNIT-CONTRACT.md` es aceptado y cualquier otro par es rechazado con
      `contract kind/path does not match role and execution`; una segunda generación no toca los bytes de la
      primera.
- [ ] **AC-4 (PD-6; tramo 1 de la prueba decisiva).** Con el paquete del architect **despachado**, se
      **agrega una unidad futura independiente** al plan (y el cambio en la sección de historia) → `receive`
      **rc=0** con `packet_validation`/`identity_validation` `passed` y `semantic_status: pending`; el
      `REQUEST.json` y el recibo quedan durables; el esquema del recibo no cambió.
- [ ] **AC-5 (PD-7/PD-8/PD-9; tramo 2).** El veredicto **declara la línea base** (el último paquete de la
      unidad); agregar la unidad independiente deja el veredicto en **`current`** (sin registro de impacto);
      un cambio en el **alcance o una dependencia** de la unidad activa (o una sección compartida, incluida
      la de autorización) lo deja en **`impact`** con el **registro durable** (los dos digests + las partes
      que difieren) y la decisión del orquestador nombrada.
- [ ] **AC-6 (PD-10; focal de B2).** Con la autorización retirada (sin entrada `epic_history` `epic-plan`)
      → veredicto **`impeded`**, rc=2, la acción afectada no procede, con el marcador existente y la
      **salida** nombrada; **registrar la aprobación `epic-plan`** → `prepare` **rc=0** y el paquete nuevo
      toma la **proyección nueva** como línea base. **Ninguna** edición de una sección del plan produce
      `impeded`.
- [ ] **AC-7 (PD-9/PD-11; focal de P1).** Dos `status` consecutivos dejan el proyecto **byte a byte**
      idéntico (state, paquetes y ausencia de `.impact.json`), y el bloque `unit_contract` **informa** el
      veredicto; dos `validate-unit-contract` con el **mismo par de digests** dejan el journal **byte a
      byte** idéntico (idempotencia, sin registro duplicado).
- [ ] **AC-8 (PD-12/PD-13).** El origen registra unidad, path, sha del plan, `approved_by` y
      `policy_sha256` (más la traza del localizador y las anclas); no hay re-aprobación por unidad si la
      proyección no cambió; no se crea documento nuevo ni segunda copia (la declaración de anclas vive una
      sola vez); el pin de la spec de los roles de construcción sigue intacto.
- [ ] **AC-9 (PD-1..PD-11; prueba decisiva, CLI real, proyecto descartable, TRES formas de plan).** El
      recorrido de §1.1 completo con evidencia, sobre **tres** formas de plan: **(i)** la de este epic
      («Entregas», columna `Feature`, historia «Cambios al plan»); **(ii)** una generada desde la plantilla
      del producto (`skills/cdad-epic/assets/epic-plan-template.md`: «Decomposition into features», columna
      «Feature ID», historia «Plan changes»); **(iii)** un **fixture sintético y anónimo** con la forma de
      los planes de otro proyecto (celda de unidad como **enlace**, **sin** sección de historia ni de
      autoridad; ids y títulos inventados). En las **tres**: agregar una unidad independiente da `current` y
      `receive` **rc=0** (o el fallback declarado de PD-2), y el cambio relevante da `impact`. Evidencia:
      salidas del CLI (rc y diagnósticos), `REQUEST.json` y recibo durables, diff del plan con su medición
      de líneas/bytes, comparación de digests. **Nunca** este repo, **nunca** HOME.
- [ ] **AC-10 (cierre).** Suite completa **una vez**, por quien cierra, en un worktree fijado al commit de
      cierre; `make validate` sin fallos nuevos.

**Instrumento y procedencia (AC-9).**
- **Instrumento:** el **CLI del producto** (el del repo en el commit de cierre; y/o el **instalado**, una
  vez el dueño despliegue), corrido como **subproceso** sobre un **proyecto descartable** en `<tmp>`, con
  `HOME` del subproceso en un tempdir vacío. El discovery §12 fija el entorno mínimo y el patrón de fixture
  existente (`tests/test_004_002_t2_bootstrap.py:198-214` `build_project` + `prepare` real;
  `tests/test_005_007_t3_open_unit.py`); la spec **no** repite ese detalle (referencia).
- **Procedencia del CLI:** el discovery verificó que el CLI del repo era **byte-idéntico** al instalado en
  `7212ead` (`git diff --name-only 7212ead..HEAD` → sólo rutas bajo `docs/`). Esa es la **procedencia**
  citada, **no** la versión bajo prueba: el comportamiento nuevo **no existe** en `7212ead`.
- **Productor de cada insumo:** el **test-writer** produce el arnés/fixture descartable, los focales y el
  **fixture anónimo de la tercera forma de plan**; el **orquestador** produce la edición del plan de cada
  forma (agregar la unidad independiente; el cambio relevante) y corre el CLI real; el **implementer** el
  código de T1/T2; el **architect** (lectura) la lectura del informe.
- **Actor evaluador:** el **orquestador OpenCode** bajo la **HITL delegada** del epic
  (`execution.md:8-23`), o el **dueño**. La **review** del orquestador Claude juzga el **sentido** de los
  textos (INV-8), no un test.
- **Evidencia de cierre:** informe con las salidas del CLI de los tramos y de las **tres** formas (rc y
  diagnósticos), `REQUEST.json` y recibo durables, diff del plan (con su medición de líneas/bytes),
  comparación de digests, la salida de `status` **antes y después** (byte-identidad) y el journal de impacto
  **repetido** (idempotencia).
- **Lo declaradamente desconocido:** la **operación exacta de reconciliación** de un paquete `dispatched`
  (territorio de 005-012; **no** se inventa acá); el número de veces que el pin bloqueó **efectivamente**
  una recepción en el epic (el state no lo registra de forma agregada; discovery §13).

## 6. Decisiones (D-n) con fundamento y trade-off

| Id | Decisión | Fundamento / trade-off |
|---|---|---|
| **D-1** | **Proyección generada, publicada UNA vez y pineada; NO re-generada en cada validación.** Los bytes viven durables junto al paquete (`.cdad/packets/<packet_id>/UNIT-CONTRACT.md`); el digest se calcula sobre esos bytes. | Es la dirección de la fila 13 (a) y del discovery §10. **Trade-off:** el riesgo verificado del discovery §3 (`_plan_task_sections` re-resuelve el plan en cada render, `:3225-3227`; `_resume_packet` compara contra el render canónico, `:1839-1840`) exige **persistir** los bytes; re-generar en cada validación reintroduciría el hazard. Ubicación junto al paquete ⇒ inmutable (INV-3 de 005-001). **Rechazado** generar por unidad con ruta fija: la sobreescribiría una segunda generación (dos paquetes del architect por unidad: discovery y draft). |
| **D-2** | **kind nuevo `approved-unit-contract`** en `VALID_CONTRACT_KINDS` (`:52`); `approved-epic-plan` **se conserva** y es el contrato del **fallback**. | El contrato de una unidad **se puede nombrar**: el diagnóstico y el `PACKET.md` dicen qué contrato es. **Trade-off:** una pieza nueva (un nombre en un set + el mapeo rol→kind/path en `:814-819`). **Rechazado** reusar `approved-epic-plan` con path nuevo: un `kind` que miente sobre su `path` (peor diagnóstico). |
| **D-3** | **Consecuencia por IDENTIDAD DE PARTE y CLASE, no por prosa.** Tres veredictos (`current` / `impact` / `impeded`); `impact` escribe un registro durable con la forma de `.superseded.json` (`:2078-2086`); `impeded` **sólo** por autorización retirada, con el vocabulario existente. **La clase `authority` desaparece.** | Fila 13 (b) pide distinguir los tres casos; hoy **no existe** clasificación (discovery §4). **Trade-off:** el CLI **no** puede juzgar si una restricción es «de aplicación inmediata» sin parsear prosa (prohibido y frágil); por eso la etiqueta vive como **clase de parte** (`unit` \| `shared`) y el juicio de una **restricción** queda en la review (review B1.3). La **sobre-inclusión** de partes `shared` (D-7) hace que una edición de una sección compartida registre `impact` — conservador y **declarado** —, nunca un bloqueo. |
| **D-4** | **Recepción/resume contra la proyección registrada**, no contra el plan vivo; **sin** tocar el esquema del recibo. | Fila 13 (c): el paquete se recibe contra el contrato que **efectivamente recibió** el agente. Con el `contract.path` apuntando a la proyección durable (D-1/D-2), `validate_request` (`:824-827`) valida los bytes registrados **sin** cambiar `receive` (`cdad_result.py:493-589`). **Trade-off:** ninguno material; la recepción ya es neutral (`semantic_status: pending`, `:575-576`) y no se amplía autoridad. En **fallback** se valida contra el plan vivo (comportamiento de hoy). |
| **D-5** | **Origen registrado; no re-aprobación por unidad si la proyección no cambió; frontera con I2/PD-18 intacta.** | Fila 13 (a), último ítem; D1/D2 ya dan la autorización del architect **sin** pin (`:1346-1360`); `plan_sha256` de `epic_history` se reutiliza como **origen**, no como pin. **Trade-off:** el origen incluye el sha del plan, así que **cualquier** edición del plan cambia el `plan_sha256`; por eso la **clasificación ignora el origen** (D-3/PD-8) y el veredicto de «agregar una unidad independiente» es `current`. El pin de la spec de los roles de construcción **no** se relaja (INV-5). |
| **D-6** | **Fuente única:** la spec **referencia** las reglas existentes (005-003/005-007/005-005/005-001); toda extensión **aditiva y declarada**; **sin** documento nuevo ni bloque `plan-tasks` mantenido a mano. | Criterio del dueño (reducir trabajo operativo sin controles frágiles ni mantenimiento documental). Un bloque `plan-tasks` a mano en el plan del epic sería una **segunda declaración** de datos que la tabla ya contiene (violaría la regla de fuente única citada por el discovery §3). |
| **D-7** | **Selección ESTRUCTURAL, sobre-inclusiva y con fallback:** la unidad se localiza como la **única fila** de una tabla del plan que contiene el id de la feature **como token completo** (con el **encabezado de esa tabla**); la proyección incluye **todas** las secciones `##` excepto las de **historia** (excluidas por la declaración del producto) y con las líneas de esa tabla **removidas** de su sección. Si la unidad no se localiza sin ambigüedad → **fallback** al contrato vigente. | **Reemplaza** la selección por título de sección/igualdad exacta de celda, que **se rompe** en la práctica: la plantilla del producto usa «Decomposition into features»/«Feature ID»/«Plan changes» (`epic-plan-template.md:25-27,69`); los planes de este mismo repo usan «Entregas del MVP» (`epic-003:78`), «Descomposición candidata» con columna «Feature candidata» (`epic-004:111-113`), «Decomposición en features» con «Feature ID» (`epic-001:39-41`, `epic-002:82-84`); otros proyectos usan la celda como enlace y no declaran historia. **Trade-off:** sobre-inclusión ⇒ una edición de una sección compartida irrelevante registra `impact` (conservador, declarado); el **fallback** pierde el beneficio de la proyección pero **no** regresiona (y hace la feature aditiva: los fixtures de plan de los tests existentes no declaran tabla → caen en el fallback y conservan su comportamiento). **Frontera declarada:** no se siguen las dependencias (las filas ajenas se excluyen por diseño). |
| **D-8** | **Superficie del veredicto:** operación de lectura `validate-unit-contract` (reporta el veredicto; en `impact` escribe su registro durable; en `impeded` rc=2) + bloque **aditivo** `unit_contract` en la vista compacta (`status`), que **informa y no escribe** (P1). | Reduce trabajo: el orquestador **ve** el veredicto en la primera consulta (`status`), sin reconstruir nada (criterio del dueño). **Trade-off:** un subcomando nuevo y un bloque aditivo; se declara y no relaja campos existentes de la vista (INV-4 de 005-011); el bloque es acotado (no incluye los bytes de la proyección, no compromete el límite de bytes de 005-003). Nombre fijado para que sea **testeable**; ajustable por el orquestador sin cambiar el comportamiento observable. |
| **D-9** | **Fallback declarado** (B1.2): sin localización sin ambigüedad, el contrato es el vigente (`approved-epic-plan`, plan completo) y el motivo se informa en el diagnóstico (stderr) y en `status`. | La review B1.2: se pierde el beneficio de la proyección, pero **no** hay regresión. **Trade-off:** dos formas de contrato vivas (proyección y plan) ⇒ `validate_request` acepta dos pares y la vista distingue `mode`; a cambio, la feature es **aditiva** con churn de oráculos casi nulo (verificado: los fixtures de plan de los tests existentes no declaran tabla). **Rechazado** fallar cerrado (era la regresión de B1) y **rechazado** publicar una proyección del plan completo (mentiría sobre el `kind` y forzaría el churn de oráculos). |
| **D-10** | **Las anclas son una declaración del PRODUCTO**, en la plantilla del plan de epic (legible por máquina), no una lista por proyecto. Historia ⇒ excluida; autorización ⇒ `shared` etiquetada, **sin** efecto de veredicto. | Review B1.3: la declaración vive en el activo que el propio producto manda cargar y completar (`epic-planning.md:73`), en **un solo lugar**; un plan sin anclas se trata conservadoramente. **Trade-off:** una lectura del activo del producto desde el generador (una pieza nueva, declarada) y un reconocimiento por título normalizado (igualdad o prefijo en frontera no alfanumérica); si el activo falta, **no** hay ancla (conservador, sin falla cerrada nueva). **Rechazado** mantener títulos por proyecto (era la fragilidad de B1) y **rechazado** una marca estructural que hubiera exigido editar todos los planes existentes (regresión). |
| **D-11** | **Línea base del veredicto** = la proyección registrada del **último paquete de la unidad** (publicación más reciente; empate → id mayor; el `active_packet` cuenta); sin paquete previo → `current`. **Salida del `impeded`** = registrar la aprobación `epic-plan` (HITL) o restituir la delegación; el siguiente paquete toma la proyección nueva como línea base. | Review B2: sin línea base declarada y sin salida, editar el plan deja la unidad bloqueada **sin salida dentro del producto**. La salida reusa **mecanismos existentes** (el registro de la aprobación es la operación que hoy habilita al architect, `:1346-1360`) y **no** depende de 005-012. **Trade-off:** la línea base se ordena por publicación (no por el contador de `packet_id`, que es por prefijo rol/subetapa: `_next_packet_id`, `:1041-1045`); se declara el desempate por id. |
| **D-12** | **El registro de impacto es idempotente** (mismo par de digests ⇒ no se duplica) y lo escribe **sólo** `validate-unit-contract`; `status` nunca escribe. | P1: `status` conserva el contrato de sólo lectura de 005-003/005-011; el journal deduplica por par de digests, así una repetición tras una interrupción no duplica efectos (misma disciplina que el reemplazo de 005-001 y que el registro de transiciones de 005-012, sin anticiparlo). **Trade-off:** un archivo durable más por unidad (en el directorio del paquete de la línea base, precedente `.superseded.json`); a cambio, el veredicto es reproducible sin efectos laterales. |
| **D-13** | **El aviso del fallback va a stderr**; stdout de `prepare` sigue siendo el `PACKET.md` byte a byte. | Contrato congelado de `prepare` (stdout == `PACKET.md` == render; `tests/test_packet_prepare.py:206`) y precedente del propio CLI (aviso a stderr en `_publish_generation`, `:3299-3303`). **Trade-off:** el motivo no viaja en el `PACKET.md`; viaja en el diagnóstico y en `status`, que es donde el orquestador lo consume. |

## 7. Alcance y fuera de alcance

**Dentro.** (a) la proyección de unidad generada con **localizador estructural**, **fallback declarado** y
**anclas por declaración del producto** + publicación + pin + kind/path (`approved-unit-contract`) + origen;
(b) el veredicto de consecuencia por parte (current/impact/impeded) + **línea base** + registro durable
**idempotente** + **salida del impedimento**; (c) recepción y resume contra la proyección registrada;
(d) la superficie de lectura (`validate-unit-contract`) y el bloque aditivo de `status` **sin escritura**;
la **prueba decisiva** (CLI real, proyecto descartable, **tres formas de plan**) como gate.

**Fuera.** Varias unidades ejecutándose a la vez sobre el mismo state (`active_packet` único) — fuera
explícito de la fila 13. La **operación de reconciliación** de un paquete `dispatched` (territorio de
005-012; no se anticipa). Las candidatas de `execution.md:89-96` (adopción de versión entre ciclos; estado
operativo compacto). **No** se reabren los contratos de 005-003/005-005/005-007/005-011 ni el pin de la
spec de los roles de construcción (005-001 I2/PD-18). Sin CI, sin sandbox, sin plataforma de jobs, sin
tocar HOME, sin desplegar, sin push. **No** se escriben listas de títulos por proyecto ni tests que decidan
el sentido de un párrafo.

## 8. Deuda con condición de cierre

- **D-1 (oráculos: churn reducido por el fallback).** Los tests que **hardcodean** el contrato del architect
  cambian **sólo** si su plan fixture declara una **tabla con la fila de la unidad**. **Verificado:** los
  fixtures de los tests hoy nombrados no declaran tabla
  (`tests/test_005_001_t1_role_approval.py:64`, `tests/test_005_001_t4_decisive.py:126`,
  `tests/test_005_007_t4_architect_report_materialization.py:104`,
  `tests/test_005_006_t5_acceptance.py:522`, `tests/test_004_002_t56_reviewfix.py:37`:
  `# Epic plan fixture …`; `tests/test_role_packet_render.py:107`: `# Contract fixture for <role>/<substage>`;
  `tests/test_packet_prepare.py` usa `PacketFixture`), así que caen en el **fallback** y **conservan** su
  comportamiento. La **lista de vigilancia** (oráculos declarados que podrían cambiar si su fixture
  declarara una fila): `tests/test_packet_prepare.py`, `tests/test_role_packet_render.py`,
  `tests/test_005_001_t1_role_approval.py`, `tests/test_005_001_t4_decisive.py`,
  `tests/test_005_001_tcorr.py`, `tests/test_005_005_t1_replace_conserved.py`,
  `tests/test_005_005_t3_provenance.py`, `tests/test_005_006_t5_acceptance.py`,
  `tests/test_005_007_t4_architect_report_materialization.py`, `tests/test_004_002_t56_reviewfix.py`.
  **Condición de cierre:** los focales de T1/T2 verdes y las **regresiones declaradas** (T1/T2, bloque
  `plan-tasks`) corridas, sin debilitamiento silencioso de tests congelados; si alguno cambia, se actualiza
  al contrato nuevo y se declara (la autoridad es la **fila 13**).
- **D-2 (reconciliación de un paquete `dispatched`).** La operación exacta de reconciliación **no** es de
  esta feature (005-012). **Condición de cierre:** el veredicto `impact`/`impeded` **nombra** la decisión
  del orquestador y registra el impacto; la reconciliación queda para 005-012. La **salida** del `impeded`
  (registrar la aprobación) **sí** queda dentro de esta feature (PD-10).
- **D-3 (juicio de «restricción de aplicación inmediata»).** El CLI no juzga la inmediatez de una
  restricción (no parsea prosa) ni la clasifica por listas de títulos. **Condición de cierre:** la parte de
  autorización se reconoce por la **declaración del producto** y se etiqueta; una restricción cuya
  inmediatez se quiera hacer mecánica exigiría una **marca estructural declarada** (no se inventa acá).
- **D-4 (dependencias de la unidad).** La proyección **nombra** las dependencias (columna de la fila) pero
  **no** incluye las filas de las unidades de las que depende. **Condición de cierre:** la parte `shared`
  sobre-inclusiva cubre las restricciones compartidas; incluir filas ajenas rompería (b)(i) y queda como
  frontera declarada (D-7).

## 9. Referencias (archivo:línea) al contrato y a las reglas que reusa

- **Contrato vigente:** `docs/epics/epic-005-real-operation/plan.md`, fila 13 (`:46`), sha256
  `63dda3b8…059a6`; «Ajuste de los ciclos pendientes» (`:48-88`, prevalece, `:57-58`); criterios del epic
  (`:90-111`); «Operación» (`:119-126`); «Autoridad» (`:128-134`); «Cambios al plan» (`:141-257`).
- **Review que origina la corrección:** `docs/specs/005-013-unit-contract/review-claude-spec-2026-10-14.md`
  (B1 `:11-41`; B2 `:43-54`; P1 `:56-61`; deuda/datos `:63-77`; disposición `:79-82`), versionada en
  `2d3613a`.
- **Criterio de review vigente:** `docs/epics/epic-005-real-operation/execution.md:48-59` (2026-10-12),
  HITL delegada (`:8-23`), insumos de planificación (`:83-96`).
- **Discovery (insumo):** `docs/specs/005-013-unit-contract/discovery.md` §1 (pin), §2 (fuente de la
  proyección), §3 (piezas que ya existen y hazard de byte-identidad), §4 (consecuencias), §5 (recepción),
  §6 (origen), §10 (propuesta mínima), §12 (aceptación), §13 (medidas y desconocido).
- **Formas de plan (evidencia del localizador y de las anclas):**
  `docs/epics/epic-005-real-operation/plan.md:30-46,141-257`;
  `docs/epics/epic-003-context-efficiency/plan.md:78-93,209`;
  `docs/epics/epic-004-single-source-planning/plan.md:111-123`;
  `docs/epics/epic-001-superpowers-gaps/plan.md:39-51,95,101`;
  `docs/epics/epic-002-cdad-audit-fixes/plan.md:82-97,162,169`;
  `skills/cdad-epic/assets/epic-plan-template.md:25-31,63-77` (plantilla del producto);
  `skills/cdad-epic/references/epic-planning.md:73-100,131-136` (la plantilla se carga y completa; la
  sección de historia del producto).
- **CLI (lo que cambia):** `skills/cdad-cycle/scripts/cdad_packet.py:52` (`VALID_CONTRACT_KINDS`),
  `:469-498` (`_validate_active_packet`), `:748-860` (`validate_request`; `:814-819` rol→kind/path;
  `:824-827` digest vs bytes; `:828-832` aprobación; `:851-859` binding), `:995-1008` (`_contract_for`),
  `:1041-1045` (`_next_packet_id`), `:1346-1360` (`_approved_epic_plan_entry`, D2), `:1378-1451`
  (`_contract_approval_for`; `:1425-1430` pin C1), `:1772-1841` (`_resume_packet`; `:1811-1836`
  `packet obsolete`; `:1837-1840` render canónico), `:1846-1849` (`ASSIGNMENT_UNIVERSE`), `:1923-2105`
  (`_replace_packet`; `:1958-1967` PD-10; `:2062-2065` binding nuevo; `:2078-2086` `.superseded.json`;
  `:2103` publicación del journal), `:2883-2952` (`_plan_tasks_from_contract`), `:3072-3147`
  (`_check_plan_validation_plan`), `:3150-3260` (`_plan_task_sections`; `:3156` `PLAN_RELPATH_TEMPLATE`),
  `:3263-3345` (`_publish_generation`; `extra_writes` `:3274`, aviso a stderr `:3299-3303`),
  `:3510-3600` (`prepare`: `_contract_for` `:3517`, `contract_object` `:3518-3520`, digest `:3557-3559`,
  `packet_id` `:3573`, `request` `:3575-3593`), `:3900-3995` (`_entry_selection`/`_next_route`),
  `:3996-4006` (`_plan_marker`), `:4042-4115` (vista `status`; `:4086-4090`
  `authority.approval.contract_sha256`).
- **Recepción (se reusa):** `skills/cdad-cycle/scripts/cdad_result.py:493-589` (`receive`; `:513`
  `validate_request`; `:527-531` `dispatched`; `:550-578` claves del recibo; `:575-576`
  `semantic_status: pending`).
- **Reglas reusadas (por referencia):** `skills/cdad-cycle/references/project-execution.md:52-84`
  (autoridad I2; architect por `epic-plan`, sin pin), `:100-141` (resume y reconciliación de política),
  `:165-233` (`--replace-packet`, PD-7..PD-24); `skills/cdad-cycle/references/re-entry.md:54-63`
  (materialización/transición), `:67-79` (equivalencia de corrida), `:83-87` (replanteo de la unidad).
- **Contratos referenciados:** `docs/specs/005-001-idle-and-v7-bootstrap/spec.md` PD-7..PD-11 (`:89-97`),
  PD-16 (`:107`), PD-18 (`:130`), PD-19..PD-24 (`:132-142`); vista compacta 005-003 (`spec.md:70-130`,
  read-only y límite de bytes; PD-1 `:349-357`; INV-1 `:460-462`); planificación/unidad 005-007;
  procedencia 005-005; entrada común 005-011 (INV-1 `:218-220`, INV-4 `:227-229`).
- **Entorno de aceptación (se referencia):** `tests/test_004_002_t2_bootstrap.py:198-214` (`build_project`),
  `tests/test_005_007_t3_open_unit.py` (proyecto fixture + CLI real).

## 10. VERIFY (resueltos o declarados)

| # | VERIFY (del discovery o de la corrección) | Estado en el draft | Dueño / cuándo |
|---|---|---|---|
| **V1** | Forma y ubicación de la proyección; riesgo de re-generación. | **RESUELTO:** generada, publicada **una vez** junto al paquete y **pineada**; no re-generada en validación (D-1). | Implementer (T1). |
| **V2** | ¿Basta un path nuevo bajo `approved-epic-plan` o hace falta un kind nuevo (`:52`)? | **RESUELTO:** kind nuevo `approved-unit-contract`; `approved-epic-plan` se conserva (es el contrato del fallback) (D-2/D-9). | Implementer (T1). |
| **V3** | Dónde se etiqueta «aplicación inmediata». | **RESUELTO (corregido):** en la proyección, como **clase de parte** (`unit` \| `shared`) y **ancla de autorización** declarada por el producto; **no** produce `impeded` (PD-3/PD-10/D-3/D-10). La inmediatez de una restricción queda en la review. | Implementer (T1/T2); review (sentido). |
| **V4** | Qué queda del `commit` del contrato (hoy `null`). | **DECLARADO:** se conserva `null` en las dos formas de contrato (el `contract` del request no lleva el sha del plan; el sha del plan vive en el origen). | Implementer (T1). |
| **V5** | ¿El origen (que incluye `plan_sha256`) rompe (b)(i)? | **RESUELTO:** la clasificación **ignora el origen**; compara sólo partes (PD-8/D-5). | Implementer (T2). |
| **V6** | Orden de generación vs. `validate_request` (el archivo debe existir al validar). | **DECLARADO (implementación):** la proyección se publica **antes** de validar (determinista e idempotente) o se valida contra los bytes staged en la transacción; el comportamiento observable lo fija PD-4/PD-5. | Implementer (T1); nota en el plan. |
| **V7** | Operación de reconciliación de un paquete `dispatched`. | **DECLARADO DESCONOCIDO (frontera):** territorio de 005-012; no se inventa (deuda D-2). La **salida del `impeded`** sí queda dentro (PD-10). | Fuera de alcance. |
| **V8** | Versión exacta del CLI en la aceptación. | **DECLARADO:** el CLI **real** (repo en el commit de cierre; y/o el instalado tras el despliegue del dueño). El discovery verificó que el CLI del repo era byte-idéntico al instalado (`7212ead`); esa es la **procedencia** citada, no la versión bajo prueba. | Orquestador; al correr la aceptación. |
| **V9** | **Dónde vive la declaración de las anclas** (B1.3) y cómo se reconoce sin listas por proyecto. | **RESUELTO:** declaración legible por máquina en el activo del producto (`skills/cdad-epic/assets/epic-plan-template.md`), leída por el generador; reconocimiento por título normalizado (igualdad o prefijo en frontera no alfanumérica); declaración ausente ⇒ ninguna ancla (conservador, sin falla cerrada) (D-10/PD-3). | Implementer (T1); review (sentido del activo). |
| **V10** | **Cómo se ordena la línea base** del veredicto (B2) sin un orden cronológico en el `packet_id`. | **RESUELTO:** por la **publicación** del `UNIT-CONTRACT.md` (más reciente primero; empate → id mayor; el `active_packet` cuenta como candidato); sin paquete previo ⇒ `current` (D-11/PD-7). | Implementer (T2). |
| **V11** | **Dónde y cómo se registra el impacto** de forma idempotente (P1). | **RESUELTO:** `.cdad/packets/<baseline_packet_id>/.impact.json` (forma de `.superseded.json`, publicación como archivo nuevo, `:2103`), escrito **sólo** por `validate-unit-contract`, deduplicado por el par `(old, new)` (D-12/PD-9/PD-11). | Implementer (T2). |
| **V12** | **Cómo se informa el fallback** sin romper el contrato de `prepare` (stdout == `PACKET.md`). | **RESUELTO:** aviso a **stderr** + bloque `unit_contract.mode == "fallback"` en `status` (D-13/PD-2). | Implementer (T1/T2). |

## 11. Riesgos con mitigación

- **R1 — la proyección cambia por una edición irrelevante** (sobre-inclusión de D-7). **Mitigación:** el
  veredicto distingue `current` de `impact` por parte; la sobre-inclusión es **conservadora y declarada**;
  no se pierde una edición relevante y **no** bloquea nada.
- **R2 — regresión por la selección atada a los títulos de este plan** (el bloqueo B1). **Mitigación:**
  localizador **estructural** (PD-1) + **fallback** (PD-2) + anclas por **declaración del producto** (PD-3);
  la aceptación cubre **tres formas de plan** (AC-9). Verificado contra los planes reales del repo y la
  plantilla.
- **R3 — `impeded` sin salida** (el bloqueo B2). **Mitigación:** `impeded` = autorización retirada, con la
  **salida existente** declarada (PD-10) y la **línea base** explícita (PD-7); ninguna sección del plan
  produce `impeded`.
- **R4 — el veredicto promete de más.** **Mitigación:** clasifica por **identidad y clase de parte**;
  afirma `impeded` sólo por autorización retirada; la inmediatez de una restricción la juzga la review
  (INV-8/PD-3).
- **R5 — `status` deja de ser de sólo lectura.** **Mitigación:** PD-11/INV-9 + AC-7 (byte-identidad del
  proyecto entre dos `status`); el journal lo escribe sólo `validate-unit-contract` y es idempotente.
- **R6 — churn de oráculos.** **Mitigación:** el **fallback** lo reduce casi a cero (los fixtures de plan de
  los tests existentes no declaran tabla — verificado); la lista de vigilancia está declarada (deuda D-1).
- **R7 — orden de generación vs. validación** (V6). **Mitigación:** publicación antes de validar
  (determinista e idempotente) o validación contra los bytes staged; se prueba con el focal de T1.
- **R8 — el pin de la spec de los roles de construcción.** **Mitigación:** INV-5/PD-12; el `specification`
  pin (path+sha) no se toca.
- **R9 — privacidad y anonimización.** **Mitigación:** INV-7; el fixture de la tercera forma de plan es
  **sintético y anónimo** (ids y títulos inventados, `<ID>`, `<otro-proyecto>`, `<ruta>`), sin nombres de
  otros proyectos, sin rutas del dueño ni ids crudos de sesión.
- **R10 — la lectura del activo del producto** (declaración de anclas) podría fallar o cambiar de forma.
  **Mitigación:** declaración ausente/ilegible ⇒ ninguna ancla (conservador, sin falla cerrada nueva);
  el localizador de la unidad no depende de ella.

## 12. Aprobación

**Estado: APROBADO.** Esta spec **reemplaza** la versión aprobada por el orquestador OpenCode en `89165d7`
(aprobación **sustituida**). Se aprobó **junto con el `plan.md`**, en una sola acción, por el **orquestador
OpenCode** el **2026-10-14**, bajo la **HITL delegada del epic-005**
(`docs/epics/epic-005-real-operation/execution.md`); el **architect** no aprobó su propia propuesta
(entregó este texto como DRAFT, y su cabecera DRAFT se conserva como registro de la entrega). Gate 2→3
validado con verificación propia del orquestador: los cuatro bloques mínimos, PD-1..PD-13 numeradas,
INV-1..INV-10, AC-1..AC-10 medibles, sin marca de aprobación en la entrega del rol, anonimización limpia
(0 rutas del dueño, 0 ids de sesión, 0 nombres de otros proyectos, fixture de la tercera forma de plan
sintético y anónimo) y el bloque canónico `plan-tasks` del plan **revalidado con las funciones del propio
CLI** (`_plan_tasks_from_contract`, `_check_plan_tasks`, `_check_plan_validation_plan`): OK, T1..T4,
estrategia declarada. Se verificó además que la corrección cubre B1.1..B1.4, B2 y P1 de la review
(`review-claude-spec-2026-10-14.md`). La firma y los hashes están en `docs/.cdad-state.json`
(`stage_history`, `stage: specification`, con `contract_path`/`contract_sha256` y
`plan_path`/`plan_sha256`). Este contrato **no arranca TDD**: el **orquestador Claude revisa** antes de la
etapa 3.

Status: Approved by orchestrator OpenCode (epic-005 delegated HITL) on 2026-10-14
