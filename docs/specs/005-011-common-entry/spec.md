> Spec **DRAFT (etapa 2, subetapa `draft`) — SIN APROBAR.** Texto del **architect**
> (`mofgw/deepseek-v4.1-flash`). Se aprueba **junto con el plan** por el **orquestador OpenCode** bajo la
> HITL delegada del epic-005 (`docs/epics/epic-005-real-operation/execution.md`) o por el **dueño**; el
> architect **no** aprueba su propia propuesta (anti-sesgo). Contrato vigente:
> `docs/epics/epic-005-real-operation/plan.md`, **fila 11** (`:44`), sha256
> `63dda3b83561a8763a6b3ab9613f2b26029796921cdede4dfd65e7ab3ad059a6`, más la sección «Ajuste de los
> ciclos pendientes — decisión del dueño, 2026-10-11» (`:48-88`). Deriva del discovery ya recibido y
> verificado (`docs/specs/005-011-common-entry/discovery.md`, §1-§10), que se resuelve **por referencia**
> (no se repite). **Fuente única:** la spec **referencia** las reglas existentes (vista compacta de
> 005-003, planificación de 005-007, procedencia de 005-005); toda extensión es **aditiva y declarada**;
> **no** se crea documento nuevo ni se duplica la regla de la vista. **Sin valores de este VPS ni rutas
> absolutas del dueño ni ids crudos de sesión** (`<home>`, `<repo>`, `<tmp>`, `<ses-…>`).

# Spec — 005-011-common-entry

**Feature ID:** `005-011-common-entry` · **Epic:** `epic-005-real-operation` · **Estado:** borrador (etapa 2).


> **Enmiendas de la revisión del orquestador Claude (2026-10-13), que prevalecen sobre el resto del texto:**
> (1) el lado Claude Code **se mide** (AC-7): una sesión nueva de Claude Code, lanzada por el orquestador
> Claude, con conteo propio sobre su transcript. Donde el texto lo declara «desconocido por frontera»
> (§1, INV-7, §6 D5, V5, meta), rige AC-7: lo que sigue desconocido es solo la medición **con el
> medidor**, porque no hay adaptador CC.
> (2) el despliegue se pide antes del cierre y AC-6/AC-7 corren como gate (AC-8). Donde el texto
> admite cerrar con AC-6/AC-7 en BLOQUEO (V1, D-1), rige AC-8.
> (3) T2 la ejecuta el implementer (plan). Ver `review-claude-spec-2026-10-13.md`.
> (4) **Ampliación tras AC-6 (2026-10-13, `acceptance.md`):** la entrada común abarca también el **prompt
> del agente orquestador** (`sources/roles/orchestrator.md`, del que se generan los agentes). En OpenCode,
> ese prompt es la primera instrucción del coordinador, y la skill se carga después. El prompt
> debe indicar que la primera acción es la vista `status` (por referencia a `orientation.md` §1).
> `resume` queda como segundo paso, solo con una ejecución activa, y el state completo como ampliación
> ante una necesidad concreta. La regla no se copia: se referencia. Se revierte la exclusión «tocar el
> agente» de D1 y T2. Tarea T2b; después se redespliega y se repite AC-6.

## 1. Descripción funcional

El resultado es que **una sesión nueva entre al proceso por una ruta breve y COMÚN** —`status` primero—
**antes** de leer el state o explorar, en los dos runtimes, y que la vista diga **versión y siguiente
acción claras**: un DRIFT legítimo (agentes derivados del proyecto anteriores a la instalación, que el
próximo `prepare` republica) **dice qué lo resuelve**, en vez de invitar a investigar.

Tres cambios, **una sola palanca por causa**, sobre fuentes que ya existen, **sin documento nuevo y sin
segunda copia**:

- **(a) Entrada común de las skills.** El **Step 1** de `cdad-cycle` y `cdad-epic` consulta **primero** la
  vista `status` (read-only); `state-detection.md` y la documentación extensa pasan a **ampliación ante una
  necesidad concreta** (fila de tabla con gatillo), no al primer paso; `orientation.md` queda **indexado**
  en la tabla de referencias de `cdad-cycle` (hoy **no** figura). La regla se **referencia**
  (`orientation.md` §1 + `project-start.md` §11 como composición canónica), no se re-escribe.
- **(b) Raíz relativa en `cdad_packet.py`.** La resolución de `--project-root` se **unifica** a «resolver
  contra el cwd y exigir `is_dir()`», como `cdad_result.py:1508-1511`; se retira el rechazo especial de
  `status` y el diagnóstico C4. La doctrina «cada CLI resuelve su propia raíz» se conserva.
- **(c) Versión y siguiente acción en la vista.** Ante `DRIFT`, la vista **nombra la pata que diverge** y
  **qué lo resuelve** (sólo lo verificado: el próximo `prepare` republica los derivados del proyecto),
  **sin inventar** y **sin confundir ausencia con incoherencia**; y con un paquete `prepared` la ruta
  nombra la **acción natural —despacharlo—**, con `--replace-packet` como **rama condicional**.

**Frontera de la mejora (no negociable).** Menos preparación **no** habilita: omitir gates, ocultar
bloqueos, declarar válido un contrato cambiado ni delegar un encargo insuficientemente definido. Un primer
despacho más rápido es **señal**, no aceptación (la aceptación usa una **sesión nueva real**).

### 1.1 Recorrido de uso objetivo (de la instrucción breve al primer despacho)

1. **Dueño:** instrucción breve.
2. Las skills se cargan; **Step 1 = la vista `status`** (con raíz relativa aceptada) → proyección acotada
   (**1.690 B** hoy, citado por el discovery) **antes** de leer el state.
3. `entry`/`next` dan la acción: `next-unit` → `open-unit`; ante un `DRIFT` **legítimo**, la salida dice
   **qué lo resuelve**.
4. Con un paquete `prepared`, la ruta nombra la acción natural (**despacharlo**), con `--replace-packet`
   como rama condicional.
5. `prepare` → validaciones → `begin` → `--record-dispatch` → **primer despacho**, **sin** leer el state
   completo ni explorar versiones, manifiestos ni el código del CLI.

En **Claude Code** aplica el mismo paso 2 (las `SKILL.md` son el texto común); la verificación del lado CC
queda **declarada desconocida** por la frontera (sin adaptador CC del medidor).

## 2. Contrato observable

### 2.1 (a) Entrada común de las skills (`common-entry-v1`)

- **Step 1 = la vista primero.** En `skills/cdad-cycle/SKILL.md` (Step 1, `:249-251`) y en
  `skills/cdad-epic/SKILL.md` (Step 1, `:56-58`), la **primera acción prescripta** es consultar la vista
  compacta `cdad_packet.py status` (`orientation.md` §1). `state-detection.md` **no** es el primer paso:
  pasa a **ampliación condicional**, con una fila de tabla cuyo gatillo es «ante una necesidad concreta
  (un bloqueo o una duda que afecte al siguiente despacho)» y **con motivo registrado**
  (`project-start.md:233-240`).
- **Indexación de `orientation.md`.** La tabla «How to read the references» de `cdad-cycle`
  (`SKILL.md:447-469`) incorpora una fila para `orientation.md`. Hoy **no figura** (verificado: grep
  «orientation» en `SKILL.md` = 0 coincidencias). La tabla de `cdad-epic` (`:200-209`) indexa su
  `state-detection.md` con el gatillo de ampliación.
- **Referencia, no copia.** La regla «vista primero, ampliar ante una necesidad concreta» **ya existe** en
  `orientation.md:14-35` (§1) y `project-start.md:223-240` (§11); el Step 1 las **referencia** (composición
  canónica), **no** las re-escribe. **No** se crea una referencia «common entry» nueva ni se duplica la
  regla.
- **Guardas conservadas.** La rama **`resume`** (sólo con ejecución activa; `SKILL.md:251`) y la fila
  `project-start.md` de la tabla **se conservan**: son las guardas por ventana de 005-006
  (`tests/test_005_006_t1_start_procedure.py:535-569` para la rama `resume`; `:188-204` para la fila
  `project-start.md`; `:607-658` para las rutas `<skill-dir>` del cableado) y de 005-006 T6
  (`tests/test_005_006_t6_owner_reviewfix.py`, hallazgos A1/A2). **El sentido de los textos lo juzga la
  review**, no una lista de palabras (criterio del dueño): las comprobaciones mecánicas son las guardas
  existentes (regresiones) más la **pertenencia de la fila** de `orientation.md` a la tabla.

### 2.2 (b) Raíz relativa consistente en `cdad_packet.py` (`project-root-v1`)

- **Unificación.** La resolución de `--project-root` de `cdad_packet.py` pasa a **resolver contra el cwd y
  exigir `is_dir()`**, igual que `cdad_result.py:1508-1511` (`Path(args.project_root).resolve()` + `is_dir()`;
  error sin exigir absoluta). Se sustituye el cuerpo de `_absolute_existing_directory` (`cdad_packet.py:673-677`)
  y se **retira** el helper especial `_status_project_root` (`:3776-3791`) y su **diagnóstico C4**.
- **Efecto.** `cdad_packet.py status --project-root .` → **rc=0** con proyección; y lo mismo para los demás
  subcomandos (`validate-state`, `validate-policy`, `render`, `validate-request`, `validate-packet`,
  `prepare`, `open-unit`, `validate-metric`): **todos** resuelven la raíz relativa contra el cwd. Una raíz
  que **no** es un directorio existente sigue **fallando cerrado** con un diagnóstico que nombra la causa
  (`must be an existing directory`), **sin** proyección parcial.
- **Lo que NO cambia.** No se toca ninguna otra validación: la política (`_project_path`/`classify_path`,
  `:168-320`), el hashing del contrato, la publicación de agentes derivados, el default cwd (`:4297-4298`).
  La doctrina «cada CLI resuelve su propia raíz» se **conserva** (`cdad_continuity.py:623`,
  `cdad_result.py:1508-1511`, `cdad-version-check.py:189-192` siguen resolviendo su propia raíz).
- **Texto que quedaría falso (se corrige).** `skills/cdad-cycle/references/orientation.md:68-75`
  («Root-relative asymmetry (diagnosed in the view)») y `skills/cdad-cycle/references/project-execution.md:49`
  («which must be an absolute existing directory»). El asset `assets/orientation-examples.json` usa el
  placeholder `--project-root <ABS>` en los ejemplos `status-view`/`open-unit`: **se conserva** (un ejemplo
  puede usar una raíz absoluta; no afirma la asimetría).
- **Cambio AUTORIZADO y DECLARADO del comportamiento C4 de 005-003 (bajo la autoridad de la fila 11).** La
  fila 11 (aprobada el 2026-10-13) **supersede** C4 de 005-003 («la vista diagnostica la asimetría de raíz
  relativa»). Comportamiento **nuevo esperado**: raíz relativa **aceptada** → **hay proyección** (rc=0). El
  **oráculo que cambia** es `tests/test_005_003_t1_compact_view.py:414-441`
  (`test_pd5_relative_root_asymmetry_diagnosed_in_view`), con su justificación: afirma rc≠0 + diagnóstico con
  raíz relativa; el contrato nuevo lo vuelve **obsoleto**, y el test se **reemplaza** por el oráculo del
  comportamiento nuevo (raíz relativa aceptada → proyección). **No** es debilitamiento silencioso de un test
  congelado: la autoridad es la fila 11 y el cambio se verifica con el comportamiento nuevo.
  - **Hallazgo del draft (declarado; requiere la misma autorización):** **un segundo oráculo** depende del
    rechazo de raíz relativa: `tests/test_005_003_t2_examples_execute.py:545-656`
    (`test_pd5_reference_declares_real_rc_capture_and_repro`) usa `validate-state --project-root .` (`:581`)
    como la **invocación que falla** del patrón de captura del `rc` (PD-5 de 005-003). El grep de V4 (por el
    **mensaje** literal) **no** lo detectó porque el test **no** cita el mensaje: depende del
    **comportamiento** (rc≠0 con raíz relativa). Bajo (b) ese fixture deja de fallar; el **oráculo de PD-5 se
    conserva** (rc capturado sin enmascarar ≠ 0, formato `ERROR: …`, prohibiciones en `orientation.md`), y
    **cambia sólo el fixture de fallo** (una raíz inexistente) y la aserción del camino de recuperación
    (`existing directory`). Este cambio se declara aquí y **se somete a la autorización explícita** que el
    paquete ya dio para el oráculo C4; **no** se ejecuta en silencio.

### 2.3 (c) Versión y siguiente acción en la vista (`view-action-v1`)

**(c1) Versión: la pata que diverge y su resolución.**

- **Distinguir la pata.** Cuando el veredicto es `DRIFT`, la vista emite **qué pata diverge**, **leída** de
  las líneas del chequeo (`cdad-version-check.py:214-236`: `project` / `agents` / `CLI` / `claude-code`),
  **nunca inferida**. El veredicto y la resolución se proyectan en el bloque `version` (extensión
  **aditiva** de la vista de 005-003; los campos existentes `verdict`/`verified`/`cause` se conservan).
- **Qué lo resuelve (sólo lo verificado).** La resolución **se afirma sólo** cuando la pata que diverge es
  **`project`** (los agentes derivados del proyecto quedaron con el `source_version` de la instalación
  anterior): el próximo **`prepare` republica** los agentes derivados del proyecto (`cdad_packet.py:2874`,
  `source_version = _installation_version(source_dir)`), documentado en `project-execution.md:143-146` y
  observado en `docs/specs/005-004-claude-code-roles/t5-acceptance.md:102-105`. Cuando la divergencia **no**
  es la pata `project` (p. ej. `agents` vs `CLI`), la vista **no** afirma esa resolución (sería inventar):
  nombra la pata y **no** promete el `prepare`.
- **Ausencia ≠ incoherencia.** `UNKNOWN`(rc 3) y `NO-PROJECT-AGENTS`(rc 4) son **ausencia** (versión **no**
  verificada) y se distinguen de `DRIFT`(rc 1) (**incoherencia**), conforme a 005-003 §2.4. La causa de
  ausencia **no** lleva cláusula de resolución.

**(c2) Siguiente acción: paquete `prepared` = despacharlo.**

- Con `active_packet.status == "prepared"`, la ruta `next.route` nombra la **acción natural —despacharlo—**
  (validar → `begin` → `--record-dispatch`), con `--replace-packet` como **rama condicional** (contrato
  cambiado). Hoy dice «reconcile the pending packet (--replace-packet if the contract changed)»
  (`cdad_packet.py:3936-3939`), que **no** es la acción natural de un `prepared` (`project-start.md:74-128`:
  un `prepared` es el que está listo para despacharse; `--replace-packet` es **sólo** para un `prepared`
  nunca despachado y **genuinamente obsoleto**, `project-execution.md:164-182`).
- **`entry` NO cambia.** Con un `prepared` la entrada sigue siendo `continuity-reconcile` (hay trabajo
  pendiente; el mapa de `entry` de 005-003 §2.2 es correcto). Cambia **sólo el texto de la ruta**
  (`next.route`).
- **`dispatched` conserva su ruta** («reconcile the dispatched packet before repeating (resume)»,
  `cdad_packet.py:3933-3935`).

## 3. Postcondiciones (numeradas y verificables)

**PD-1 (entrada común: la vista primero en las dos skills).** El **Step 1** de `cdad-cycle` y `cdad-epic`
consulta **primero** la vista `status`; `state-detection.md` pasa a **ampliación condicional** con gatillo
declarado en la tabla de referencias; `orientation.md` queda **indexado** en la tabla de `cdad-cycle`. La
regla se **referencia** (`orientation.md` §1 + `project-start.md` §11), **no** se re-escribe; **no** se crea
documento nuevo. La rama `resume` y la fila `project-start.md` **se conservan**. Borde: las guardas por
ventana de 005-006/005-010 quedan verdes.

**PD-2 (raíz relativa consistente; sin otra validación tocada).** `cdad_packet.py status --project-root .`
→ **rc=0** con proyección; los **demás subcomandos** resuelven la raíz relativa contra el cwd; una raíz
inexistente **falla cerrado** nombrando la causa, **sin** proyección parcial; **ninguna** otra validación
(política, hashing, publicación, default cwd) cambia. Borde: sin bandera se sigue usando el cwd
(`:4297-4298`); con bandera relativa se resuelve contra el cwd.

**PD-3 (cambio autorizado de C4, declarado y con sus oráculos).** El comportamiento C4 de 005-003
(asimetría **diagnosticada** por la vista) queda **superseded** por la fila 11; el comportamiento nuevo es
«raíz relativa aceptada → hay proyección». Los oráculos que cambian se **declaran**: (i)
`tests/test_005_003_t1_compact_view.py:414-441` (reemplazado por el oráculo del comportamiento nuevo); (ii)
`tests/test_005_003_t2_examples_execute.py:545-656` (fixture de fallo + camino de recuperación; su oráculo
de captura del `rc` se **conserva**). Borde: ningún otro consumidor depende del rechazo (verificado: el grep
de V4 no halla consumidor del **mensaje**; el consumidor del **comportamiento** es el oráculo (ii)).

**PD-4 (versión: la pata que diverge, leída y con su resolución sólo si es la verificada).** Ante `DRIFT`,
la vista emite la **pata que diverge**, **leída** de las líneas del chequeo (no inferida); afirma la
resolución (el próximo `prepare` republica los derivados del proyecto) **sólo** cuando la pata es `project`;
con otra pata **no** la promete. `UNKNOWN`/`NO-PROJECT-AGENTS` (ausencia) **no** llevan cláusula de
resolución y **no** se confunden con `DRIFT`. Borde: con la pata `project` divergiendo y `agents`/`CLI`
coincidentes → DRIFT con resolución; con `agents`≠`CLI` → DRIFT sin la resolución del `prepare`.

**PD-5 (siguiente acción: `prepared` = despacharlo).** Con `active_packet.status == "prepared"`,
`next.route` nombra la acción natural (**despacharlo**), con `--replace-packet` como **rama condicional**;
`entry` **sigue** siendo `continuity-reconcile`; con `dispatched` se conserva la ruta de reconciliación
antes de repetir. Borde: la ruta de `prepared` **difiere** de la de `dispatched` y del texto anterior
«reconcile the pending packet…».

**PD-6 (fuente única y extensión aditiva).** La spec **no** agrega una segunda copia de una regla
existente: **referencia** la vista compacta (005-003), la planificación (005-007) y la procedencia (005-005).
Toda extensión (campos de `version`, texto de `next.route`) es **aditiva y declarada**: los campos
existentes de la vista se conservan; **no** se crea documento nuevo ni se duplica la regla de la vista.

## 4. Invariantes (verificables)

- **INV-1 (read-only).** La vista y la spec no escriben el estado: `status` deja el state byte-idéntico.
- **INV-2 (sin documento nuevo; sin segunda copia).** No se crea una referencia «common entry» ni un
  documento nuevo; la regla «vista primero» se **referencia** desde sus dueños (`orientation.md` §1,
  `project-start.md` §11). No hay segunda copia de la regla de la vista compacta, de la planificación ni de
  la procedencia.
- **INV-3 (frontera con 005-006).** Se **reutiliza** el procedimiento de arranque (`project-start.md`, que
  compone los dueños) y **no** se crea otro bootstrap; `state-detection.md` sigue siendo el dueño canónico
  del reconocimiento feature/Memory-Bank. El paso de orientación se agrega **por referencia**, sin copiar la
  estructura de los dueños.
- **INV-4 (frontera con 005-003/005-007/005-005).** **No** se reescriben sus contratos; la extensión de la
  vista es **aditiva y declarada** (campos nuevos de `version`; texto de `next.route`); **no** se cambia el
  mapa de `entry` ni el tamaño de unidad (005-007) ni la procedencia (005-005).
- **INV-5 (el sentido de los textos lo juzga la review).** La spec **no** pide tests que decidan el
  significado de un párrafo por listas de palabras; las comprobaciones mecánicas son las guardas existentes
  (regresiones) y las aserciones **estructurales** de la salida del CLI (pata que diverge, ruta, `entry`),
  no el sentido de una prosa.
- **INV-6 (sin valores de este VPS).** Ni rutas absolutas del dueño, ni ruta del store, ni proveedor/modelo
  concreto, ni servidor, ni ids crudos de sesión, en spec, plan ni producto; las magnitudes ya publicadas se
  citan **por referencia**.
- **INV-7 (unknown con causa, nunca 0).** Lo no observable (el lado CC, el hito «primera acción» en el
  medidor) queda `unknown` con causa, **nunca 0**; la meta numérica distingue **medido** de **derivado**.
- **INV-8 (gate por despliegue).** La aceptación de uso requiere la **versión desplegada** (acción del
  dueño); sin desplegar, devuelve **BLOQUEO declarado**, nunca verde por proximidad.

## 5. Criterios de aceptación (medibles)

La meta es la de la **fila 11**: una **sesión nueva de cada runtime**, sin contexto previo, **consulta
`status` ANTES de leer el state** y **llega al primer despacho sin explorar versiones, manifiestos ni
código del CLI**. La meta numérica sale de las líneas base como **orientación, no umbral automático**.

- [ ] **AC-1 (a).** El Step 1 de `cdad-cycle` y `cdad-epic` consulta primero la vista; `state-detection.md`
      es ampliación condicional con gatillo; `orientation.md` está indexado; la regla se referencia; las
      guardas por ventana de 005-006/005-010 quedan **verdes**.
- [ ] **AC-2 (b).** `status --project-root .` → rc=0 con proyección; los demás subcomandos aceptan la raíz
      relativa; una raíz inexistente falla cerrado nombrando la causa; **ninguna** otra validación cambia.
- [ ] **AC-3 (b/C4).** El comportamiento C4 está **superseded y declarado**; los **dos** oráculos que
      cambian están **nombrados** y actualizados al comportamiento nuevo (uno reemplazado, el otro con el
      fixture de fallo corregido y su oráculo de captura conservado).
- [ ] **AC-4 (c).** Ante un `DRIFT` con la pata `project` divergiendo, la vista dice **qué lo resuelve** y
      **nombra la pata**, leída del chequeo; con otra pata **no** lo promete; la ausencia
      (`UNKNOWN`/`NO-PROJECT-AGENTS`) se distingue de la incoherencia.
- [ ] **AC-5 (c).** Con un paquete `prepared`, `next.route` nombra la acción natural (despacharlo), con
      `--replace-packet` como rama condicional; `entry` sigue `continuity-reconcile`; `dispatched` conserva
      su ruta.
- [ ] **AC-6 (aceptación de uso, OpenCode).** Una **sesión nueva real** de OpenCode, en reposo y sin
      contexto previo, consulta `status` **antes** de leer el state completo y llega al primer despacho
      **sin** explorar versiones, manifiestos ni el código del CLI; se mide con el **medidor de 005-002**
      sobre el **store de OpenCode**, con `--delegation-dispatch`, **per sesión y per rol**, con
      **instrumento y procedencia** declarados; los valores se comparan **like-for-like** con la línea base
      (`docs/specs/005-007-progressive-planning/acceptance.md` §7: 70 llamadas, 304.054 car.) como
      **orientación**.
- [ ] **AC-7 (aceptación de uso, Claude Code; enmienda de la revisión del orquestador Claude, 2026-10-13).**
      Una **sesión nueva** de Claude Code (`claude -p`), lanzada por el **orquestador Claude** desde un
      directorio confiable sin la memoria de este proyecto y con una instrucción breve, consulta `status`
      **antes** de leer el state y llega al primer despacho sin explorar versiones, manifiestos ni el código
      del CLI. Se mide con **conteo propio** sobre el transcript (otro instrumento, declarado; sin adaptador
      CC del medidor, D-4 de 005-004) y se compara como **orientación** con
      `docs/specs/005-004-claude-code-roles/t5-acceptance.md` §7 (llamada 23, 105 mil car.). No se declara
      `unknown`: las skills son comunes a los dos runtimes y el lado CC es parte del resultado.
- [ ] **AC-8 (cierre).** Suite completa **una vez**, por quien cierra, en un worktree fijado al commit de
      cierre; `make validate` sin fallos nuevos. **Secuencia (enmienda de la revisión):** con T1..T3 verdes,
      el orquestador pide al dueño el despliegue (lo decide el dueño, con el otro proyecto activo en reposo); AC-6 y AC-7 corren
      sobre la versión desplegada **antes** de cerrar. La feature **no** se cierra con AC-6/AC-7 en BLOQUEO:
      su resultado es el comportamiento de entrada en sesiones reales.

**Instrumento y procedencia (AC-6).** `skills/cdad-cycle/scripts/cdad_context_meter.py` del repo, en solo
lectura (`--store <store>` `mode=ro`, `--delegation-dispatch`), contrato en
`skills/cdad-cycle/references/context-meter.md`; `first_resume`/`first_dispatch`, `previous_calls`,
`previous_reads`, `tool_calls`, `session_reads`, `total_output`, `time_to_first_dispatch`, con **cobertura
declarada**. El **hito «primera acción de orientación»** **no** es un hito del medidor (propuesta de
005-003, no asumida): la primera acción se observa con **conteo propio** sobre el transcript (partes `tool`).
**Lo declaradamente desconocido:** el lado CC (sin adaptador), el hito de la primera acción en el medidor, y
`cache_write`/`cost` si el proveedor no los reporta (unknown con causa, nunca 0).

## 6. Decisiones (D-n) con fundamento y trade-off

| Id | Decisión | Fundamento / trade-off |
|---|---|---|
| **D1** | **(a) → A1:** reescribir el Step 1 de las dos `SKILL.md` (y las filas de tabla) para que la primera acción sea la vista, e **indexar `orientation.md`**; conservar las guardas de 005-006/005-010 y la rama `resume`. | Es la **causa raíz medida** (el Step 1 manda leer el state; `SKILL.md:249-251`, `state-detection.md:16-18`). **Trade-off:** toca texto vigilado por ventana; mitigado conservando la rama `resume` y la fila `project-start.md`. **Rechazado A2** (referencia nueva: mantenimiento documental sin corregir la causa + duplica una regla → viola «fuente única») y **A3** (sólo el agente: no es el texto común entre runtimes). |
| **D2** | **(b) → B1:** **unificar** la resolución de `--project-root` en `cdad_packet.py` (cwd + `is_dir()`, como `cdad_result.py:1508-1511`); retirar el rechazo especial de `status` y el diagnóstico C4; corregir el texto que quedaría falso. | Resuelve la llamada 20 y la asimetría; deja `cdad_packet.py` resolviendo **su propia** raíz como los demás (doctrina conservada). **Trade-off:** supersede C4 de 005-003 y vuelve obsoletos **dos** oráculos (el C4 nombrado por el paquete y el fixture de PD-5 hallado en el repo), **declarados**. **Rechazado B2** (sólo mejorar el mensaje: no resuelve la llamada 20 ni la asimetría). |
| **D3** | **(c1) → C1:** enriquecer la proyección de versión para que, ante `DRIFT`, diga **qué lo resuelve** distinguiendo la pata que diverge. | Resuelve las llamadas 22-30 (investigación guiada por un DRIFT sin acción). **Trade-off:** hay que **no inventar** (afirmar sólo lo verificado) y **no confundir ausencia con incoherencia**; mitigado leyendo la pata del chequeo y afirmando la resolución sólo para la pata `project`. |
| **D4** | **(c2) → C2:** la ruta de `prepared` nombra la **acción natural (despacharlo)**, con `--replace-packet` como **rama condicional**; `entry` **no** cambia. | `prepared` es el que está listo para despacharse (`project-start.md:74-128`); `--replace-packet` es sólo para obsoleto genuino (`project-execution.md:164-182`). **Trade-off:** es **texto** de la vista, no cambia el mapa de `entry`; no hay test que afirme la cadena literal de `next` (verificado). |
| **D5** | **Aceptación:** instrumento = medidor de 005-002 sobre el store de OpenCode, `--delegation-dispatch`, per sesión y per rol; **lado CC declarado DESCONOCIDO** por frontera; meta numérica de las líneas base como **orientación**. | Fila 11; contrato del medidor (005-002 PD-6/PD-15). **Trade-off:** una sola sonda por variante → **indicativa, no estadística**; el hito «primera acción» no es del medidor → **conteo propio**. |
| **D6** | **Fuente única:** la spec **referencia** las reglas existentes (005-003, 005-007, 005-005); toda extensión **aditiva y declarada**; **sin** documento nuevo ni segunda copia. | Criterio del dueño (reducir trabajo operativo sin controles frágiles ni mantenimiento documental); INV-2/PD-6. |

## 7. Alcance y fuera de alcance

**Dentro.** (a) entrada común de las dos skills que orientan + indexación de `orientation.md`; (b) raíz
relativa consistente en `cdad_packet.py` + corrección del texto que quedaría falso + los **dos** oráculos
declarados; (c) versión (pata que diverge + resolución verificada) y siguiente acción (`prepared` =
despacharlo) en la vista; la aceptación de uso con el medidor.

**Fuera.** 005-012 (registro de transiciones) y 005-013 (contrato por unidad): **no** se anticipan. El
**adaptador Claude Code** y la **medición del lado CC** siguen fuera (D-4 de 005-004). **No** se reabren los
contratos de 005-003/005-004/005-007 (sólo se **corrige** lo que la fila 11 manda, con sus oráculos
declarados). Sin CI, sin WebUI, sin sandbox, sin plataforma de jobs; **sin tocar HOME** (reservado al dueño,
`execution.md:19-23`); **sin desplegar**; **sin push**.

## 8. Deuda con condición de cierre

- **D-1 (despliegue).** La aceptación de uso corre con la **versión desplegada**; el despliegue es del dueño.
  **No es deuda de cierre** (enmienda de la revisión): el despliegue se pide antes del cierre y AC-6/AC-7
  corren sobre la versión desplegada como gate (AC-8).
- **D-2 (hito «primera acción» en el medidor).** El medidor **no** tiene un hito de «primera acción de
  orientación». **Condición de cierre:** extender el medidor con ese hito (propuesta de 005-003 §10, **no**
  asumida); hasta entonces, AC-6 usa **conteo propio** sobre el transcript.
- **D-3 (adaptador CC del medidor).** Sin adaptador CC, el lado CC no se mide con el instrumento.
  **Condición de cierre:** un adaptador CC del medidor (D-4 de 005-004), fuera de esta feature.

## 9. Referencias (archivo:línea) al contrato y a las reglas que reusa

- **Contrato vigente:** `docs/epics/epic-005-real-operation/plan.md`, fila 11 (`:44`), sha256
  `63dda3b8…059a6`; sección «Ajuste de los ciclos pendientes» (`:48-88`); cambios 2026-10-13 (`:143-154`).
- **Discovery (insumo):** `docs/specs/005-011-common-entry/discovery.md` §1-§10 (Eje 1: entrada de las
  skills; Eje 2: raíz relativa; Eje 3: versión y siguiente acción; Eje 4: qué carga una sesión nueva; Eje 5:
  frontera; Eje 6: aceptación y medición).
- **Skills (lo que cambia):** `skills/cdad-cycle/SKILL.md:249-251` (Step 1), `:447-469` (tabla);
  `skills/cdad-epic/SKILL.md:56-58` (Step 1), `:200-209` (tabla).
- **Reglas reusadas (por referencia):** `skills/cdad-cycle/references/orientation.md:14-35` (§1 vista
  primero), `:57-66` (tabla de operaciones), `:68-75` (asimetría — se corrige), `:102-128` (§4 versión);
  `skills/cdad-cycle/references/project-start.md:223-240` (§11 vista primero), `:74-128` (§6 primera
  comisión), `:184-211` (§10 versión); `skills/cdad-cycle/references/project-execution.md:49` (texto — se
  corrige), `:113-116` (registro de despacho), `:143-146` (republicar), `:164-182` (`--replace-packet`).
- **Vista compacta (005-003, se referencia):** `docs/specs/005-003-orientation-reduction/spec.md:70-107`
  (§2.1 forma), `:109-138` (§2.2 mapa de `entry`), `:166-204` (§2.4 versión/medidor), `:347-457`
  (PD-1..PD-5).
- **CLI (lo que cambia):** `skills/cdad-cycle/scripts/cdad_packet.py:673-677`
  (`_absolute_existing_directory`), `:3776-3791` (`_status_project_root`, C4), `:3815-3842`
  (`_version_verdict`), `:3911-3927` (`_entry_selection`), `:3930-3949` (`_next_route`), `:3965-4087`
  (`status_view`), `:4294-4304` (`main`). Chequeo de versión: `cdad-version-check.py:211-236` (veredicto y
  patas). Contraste de raíz: `cdad_result.py:1508-1511`, `cdad_continuity.py:623`.
- **Oráculos que cambian (declarados):** `tests/test_005_003_t1_compact_view.py:414-441` (C4);
  `tests/test_005_003_t2_examples_execute.py:545-656` (fixture PD-5).
- **Guardas que se conservan:** `tests/test_005_006_t1_start_procedure.py:188-204, 535-569, 607-658`;
  `tests/test_005_006_t6_owner_reviewfix.py` (hallazgos A1/A2); `tests/test_005_005_t2_docs_policy.py:136`.
- **Líneas base (citadas):** `docs/specs/005-007-progressive-planning/acceptance.md:107-151` (§7, OpenCode);
  `docs/specs/005-004-claude-code-roles/t5-acceptance.md:68-93` (§7, Claude Code).
- **Medidor (005-002, se cita):** `docs/specs/005-002-session-context-meter/spec.md:271-280` (PD-6 hitos),
  `:370-378` (PD-15 superficie); `skills/cdad-cycle/references/context-meter.md`.

## 10. VERIFY (resueltos o declarados)

| # | VERIFY | Estado en el draft | Dueño / cuándo |
|---|---|---|---|
| **V1** | Que la versión desplegada al momento de la aceptación incluya (a)(b)(c). | **DECLARADO DESCONOCIDO (bloqueo por frontera):** el despliegue es del dueño; sin desplegar, AC-6/AC-7 quedan BLOQUEO declarado. | Dueño; al correr la aceptación. |
| **V2** | El orden exacto de carga de la skill y sus referencias **en Claude Code**. | **DECLARADO DESCONOCIDO por frontera** (la ruta de carga de CC no es la de OpenCode; sin adaptador CC). | Fuera de alcance (frontera). |
| **V3** | Qué pata exacta produce el `DRIFT` en la corrida real de aceptación. | **RESUELTO como requisito de producto:** la vista **lee** la pata de las líneas del chequeo (`cdad-version-check.py:214-236`), **no** la infiere; la aceptación **declara** la pata observada. | Implementer (T3); aceptación (T4). |
| **V4** | Si algún consumidor fuera de `tests/test_005_003_t1_compact_view.py` depende del rechazo de raíz absoluta. | **RESUELTO desde el repo (hallazgo del draft):** el grep por el **mensaje** literal no halla consumidor de código; **sí** hay un consumidor del **comportamiento**: `tests/test_005_003_t2_examples_execute.py:581` (fixture de PD-5). Se declara y se actualiza. | Implementer (T1); autorización (orquestador/dueño). |
| **V5** | El efecto de (a) sobre la línea base de Claude Code. | **DECLARADO DESCONOCIDO:** no se puede medir con el medidor actual (sin adaptador CC); sólo con conteo propio si el dueño corre la sesión CC. | Fuera de alcance; deuda D-3. |

## 11. Riesgos con mitigación

- **R1 — tocar el Step 1 de `cdad-cycle` rompe guardas por ventana** de 005-006/005-010. **Mitigación:**
  conservar la rama `resume` y la fila `project-start.md`; correr esos focales en T2 (regresiones).
- **R2 — el texto de la vista promete de más.** **Mitigación:** la causa de `DRIFT` afirma **sólo** lo
  verificado (el próximo `prepare` republica los derivados del proyecto) y **sólo** para la pata `project`;
  distingue ausencia de incoherencia.
- **R3 — (a) se lee como «prohibido leer el state».** **Mitigación:** la regla es «vista primero, ampliar
  ante una necesidad concreta **con motivo registrado**» (`project-start.md:233-240`), no una prohibición.
- **R4 — el cambio de (b) toca dos tests congelados.** **Mitigación:** ambos **declarados** (PD-3), con su
  justificación; el oráculo de captura de `rc` de PD-5 se **conserva**; el C4 se **reemplaza** por el
  comportamiento nuevo. La autoridad es la fila 11; la autorización explícita se registra.
- **R5 — privacidad.** **Mitigación:** INV-6; magnitudes ya publicadas citadas **por referencia**.
- **R6 — una sola sonda por variante → indicativa, no estadística** (riesgo del epic). **Mitigación:** la
  meta numérica es **orientación, no umbral** (AC-6); sin promediar cortes distintos.

---

## 12. Aprobación

**Estado: APROBADA.** El **architect** no aprueba su propia propuesta (anti-sesgo: entregó esta spec como DRAFT). La **aprobó el orquestador OpenCode** el **2026-10-13** bajo la **HITL delegada del epic-005** (`docs/epics/epic-005-real-operation/execution.md`), **junto con el `plan.md` y en una sola acción**. La cabecera DRAFT del rol se conserva como registro de la entrega; el estado vigente es el de esta sección. Rige el **criterio de review vigente del 2026-10-12**. El **orquestador Claude revisa** antes de la etapa 3: en este tramo **no se arranca TDD**.

**Autorización explícita de los dos oráculos (PD-3).** Bajo la autoridad de la **fila 11 del plan** (aprobada el 2026-10-13), que supersede el comportamiento C4 de 005-003, se autoriza: (i) el **reemplazo** del oráculo C4 (`tests/test_005_003_t1_compact_view.py:414-441`) por el del comportamiento nuevo (raíz relativa aceptada → hay proyección); y (ii) la **actualización del fixture de fallo** del oráculo de PD-5 de 005-003 (`tests/test_005_003_t2_examples_execute.py:545-656`, hallazgo del draft), **conservando** su oráculo de captura del `rc` sin enmascarar y cambiando sólo la invocación que falla y la aserción del camino de recuperación. Ambos cambios quedan **declarados** y se verifican con el comportamiento nuevo; no son debilitamiento silencioso de tests congelados.

**Meta de aceptación de la feature (fijada en el contrato, no re-enunciada aquí).** Una **sesión nueva de cada runtime**, sin contexto previo, **consulta `status` antes de leer el state** y **llega al primer despacho sin explorar versiones, manifiestos ni código del CLI**: AC-1..AC-5 sobre los productos de T1..T3, **AC-6** con una sesión nueva real de OpenCode medida por el **medidor de 005-002** (store de OpenCode, `--delegation-dispatch`, per sesión y per rol, instrumento y procedencia declarados) y **AC-7** declarando el lado **Claude Code DESCONOCIDO** por frontera (sin adaptador CC). La **meta numérica** sale de las líneas base (`005-007/acceptance.md` §7: 70 llamadas / 304.054 caracteres; `005-004/t5-acceptance.md` §7: llamada 23 / 105 mil caracteres) como **orientación, no umbral**. Sin cifras de ahorro prometidas; lo no observable se conserva `unknown` con causa.

La firma de la aprobación y sus hashes están registrados en `docs/.cdad-state.json` (`stage_history`, `stage: specification`, con `contract_path`/`contract_sha256` y `plan_path`/`plan_sha256`).

Status: Approved by orchestrator OpenCode (epic-005 delegated HITL) on 2026-10-13
