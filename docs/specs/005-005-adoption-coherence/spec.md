> Spec **aprobada** (2026-10-09). Texto del **architect** (subetapa `draft`, stage 2),
> materializado con el flujo (receive + materialize CAS) por el orquestador (ADR-003);
> aprobada por el orquestador OpenCode bajo la delegación HITL de epic-005. Decisiones
> D1–D8 aprobadas tal como se proponen en §7.
> Insumo verificado: `docs/specs/005-005-adoption-coherence/discovery.md` (mapa con
> archivo:línea). Encargo: `docs/epics/epic-005-real-operation/handoff-005-005.md` §3–§4.
> Contrato: `docs/epics/epic-005-real-operation/plan.md` (fila 2 y «Cambios al plan» 2026-10-09).

## Spec — 005-005-adoption-coherence

**Feature ID:** `005-005-adoption-coherence` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobada (2026-10-09, orquestador OpenCode, HITL delegada epic-005). ADR-011 gobierna autoridad, capacidades y límites.

```yaml
feature_id: 005-005-adoption-coherence
feature_name: Coherencia de la adopción — reemplazo que valida lo conservado, una sola política de tests y procedencia de la instalación
created_at: 2026-10-09
status: approved
approved_by: orquestador OpenCode (HITL delegada epic-005)
approved_at: 2026-10-09
```

### 1. Descripción funcional

005-005 es la **continuación correctiva de 005-001**. No agrega roles, sub-modos ni
contratos nuevos: cierra tres incoherencias que quedaron abiertas al cerrar 005-001 y
deja verificable la procedencia de la instalación con la que corre el ciclo. Son tres
trabajos independientes más un cierre:

- **T1 — El reemplazo valida también lo conservado.** `prepare --replace-packet` hoy
  valida sólo los campos presentes en el set `corrected` (`_validate_corrections`,
  `cdad_packet.py:1843-1886`, gates `:1850`/`:1862`/`:1877`): un `input` **conservado**
  que apunta a un archivo inexistente pasa sin diagnóstico, y un alcance conservado
  fuera de la política falla con el mensaje genérico de `validate_request` (que no
  nombra el campo ni la opción). 005-005 fija que el reemplazo valida el **encargo
  resultante completo** (conservado + corregido) y que todo rechazo nombra **campo,
  motivo y opción**, sin publicar nada y dejando el paquete anterior byte a byte
  idéntico. El camino normal de `prepare` **no** cambia.
- **T2 — Una sola política de tests.** Hoy conviven afirmaciones contradictorias:
  `stage-3-tdd.md:153` («the full suite runs **once per GREEN**») y `re-entry.md:149-150`
  («complete suite» por GREEN) **vs.** `stage-3-tdd.md:31` («gates, not for debugging»)
  y el gate del epic (`plan.md:60-61`: focales y módulos tocados; suite completa al
  cierre). Los paquetes canónicos dicen «the required full regression suite»
  (`implementer-green.md:1`), término indefinido. 005-005 fija una **política única de
  evidencia** (regresión proporcional al cambio; suite completa al cierre de la feature;
  reutilización de evidencia registrada equivalente) y alinea los consumidores **sin
  duplicar** el texto de la regla. La metodología define la evidencia; **el proyecto
  declara los comandos**; una condición local/entorno se **registra** en la evidencia y
  **no** se vuelve requisito. Incluye enmendar PD-17 de 005-001 para que su letra
  coincida con el recorrido realmente ejecutado.
- **T3 — Procedencia de la instalación.** `prepare` resuelve el origen de los agentes de
  proyecto de OpenCode desde la variable `CDAD_OPENCODE_AGENTS_DIR` o, sin ella, desde la
  instalación global de HOME (`_derived_source_dir`, `:2454-2457`; `DEFAULT_DERIVED_SOURCE`,
  `:89`); **no consulta** el registro de activación del proyecto (`grep "activation"` sin
  resultados). Una contradicción de versiones (variable vs registro vs global) no se
  diagnostica: el caso MIX-V6V7 real (`dispatch-ledger.md:84-101`) re-derivó los 11
  agentes de **otra versión** sin avisar. 005-005 fija el registro de activación como
  fuente por defecto cuando existe, exige un diagnóstico que nombre el registro y las
  versiones ante una contradicción, y deja **verificable qué versión cargó una sesión**
  (versión/commit en el manifiesto y/o en cada agente publicado). Incluye normalizar
  `docs/specs/005-001-idle-and-v7-bootstrap/review.md` (texto corrupto por un glitch de
  generación; referencia a un PD-27 inexistente que debe ser PD-20) sin repetir la
  revisión, y retirar las rutas personales de los documentos del epic-005.
- **Cierre — Integración desde una instalación aislada.** Como **test de integración**
  (no despliegue), instalar la versión nueva del repo en una **raíz aislada** (nunca
  HOME) y comprobar que con ella se puede preparar, corregir con `--replace-packet`
  (con la validación completa de T1) y despachar un encargo con la validación
  proporcional (T2), **sin rodeos manuales**.

### 2. Contrato

**Superficie CLI (sin flags nuevos):** 005-005 no agrega flags. El sub-modo
`--replace-packet` (005-001 PD-7..PD-11, PD-19..PD-24) conserva su superficie; cambia su
**semántica de validación** (valida el encargo resultante completo) y la **resolución del
origen** de agentes en `prepare`.

```
prepare --project-root R --replace-packet <id> --reason <t> [--input P=P] \
    [--read-scope C[=S]] [--write-scope C[=S]] [--invariant T] \
    [--expected-output T] [--evidence T]        # validación COMPLETA del encargo resultante
prepare --project-root R --role <rol> --substage <sub> --objective <t>   # camino normal SIN cambios
```

**Registros y artefactos (contrato de datos):**

- **Registro de activación** `.cdad/activation.json` (emitido por `scripts/cdad-activate.py`,
  `build_registry` `:294-313`; contrato en `references/runtime-adoption.md:37-39`):
  `{adopted_root, manifest_sha256, paths}`. La raíz adoptada contiene los agentes del
  runtime en `<adopted_root>/.config/opencode/agents` (layout usado en `dispatch-ledger.md:33`).
- **Manifiesto de agentes derivados** `.opencode/agents/.cdad-derived.json` (`:2706-2712`):
  hoy lleva `schema_version`, `policy_sha256`, `source_dir` y, por agente,
  `source_sha256`/`derived_sha256`. 005-005 agrega la **versión/commit de la instalación
  de origen** (PD-14).
- **Marcadores de diagnóstico** (stderr): se conservan los de 005-001 (`approval pending`,
  `packet obsolete`, `state incoherent`). 005-005 agrega el **diagnóstico de contradicción
  de origen** (PD-13), que nombra `.cdad/activation.json` y las versiones en juego.

**Postcondiciones (numeradas y verificables):**

**PD-1 (el reemplazo valida el encargo resultante completo).** Con un paquete activo
`status == "prepared"` y obsolescencia verificada (PD-8 de 005-001),
`prepare --replace-packet <id> --reason <t>` valida **el encargo resultante completo**
—campos conservados **y** corregidos—: cada `input` **existe** y queda dentro de algún
`read_scope`; `read_scope`/`write_scope` están clasificados por la política; `invariants`
y `evidence_required` son strings no vacíos; `expected_output` no vacío; el contrato y la
política se re-resuelven al día. Si todo es válido → `rc=0` y se publica el sucesor. El
**dominio de validación es el encargo resultante**, no sólo los campos corregidos.

**PD-2 (insumo conservado inexistente rechazado — cierra el hueco de T1).** Con un `input`
**conservado** (no tocado por `--input`) que apunta a un archivo inexistente,
`prepare --replace-packet <id> --reason <t>` → `rc=2`; el stderr nombra el **campo**
(`inputs`/`input.path`), el **motivo** (archivo inexistente) y la **opción** para
corregirlo (`--input`); **no** se publica paquete nuevo; el `REQUEST.json`/`PACKET.md` del
paquete anterior quedan **byte a byte idénticos** y el `state` sin cambios. *(Hoy este caso
pasa sin diagnóstico: el único `is_file()` ligado a inputs está en `_validate_corrections:1858`
y sólo corre si `inputs` está en `corrected`. Es el **VERIFY de ejecución** del discovery
§T1; este PD es el test focal que lo fija.)*

**PD-3 (alcance conservado fuera de política rechazado con diagnóstico accionable).** Con un
`read_scope` o `write_scope` **conservado** que viola la política (selector no clasificado,
o clase no admitida para el rol), `prepare --replace-packet` → `rc=2`; el stderr nombra el
**campo** (`read_scope`/`write_scope`), el **motivo** de política y la **opción**
(`--read-scope`/`--write-scope`); sin efectos (paquete anterior byte-idéntico, `state`
intacto). *(Hoy el mensaje genérico de `validate_request` —`:690`, `:694`, `:703`, `:816`—
no nombra el campo ni la opción.)*

**PD-4 (recuperación: el reemplazo repetido con la corrección funciona).** Partiendo de PD-2,
un segundo `prepare --replace-packet <id> --reason <t> --input P=P` con un `P` **existente**
y dentro de algún `read_scope` → `rc=0`; publica el sucesor con el contrato del día; el
paquete anterior byte-idéntico; se escribe `.superseded.json` con el `reason`; **sin**
entradas nuevas en `stage_history`/`epic_history` (INV-2 de 005-001).

**PD-5 (el camino normal no suma restricciones).** Un `prepare` **normal** (sin
`--replace-packet`) con un `input` declarado que apunta a un archivo inexistente conserva
el comportamiento de hoy (`rc=0` si el resto es válido; `validate_request` resuelve la ruta
sin exigir existencia, `:814`). 005-005 **no** agrega la exigencia de existencia al camino
normal. *(Coherencia con PD-22 de 005-001: el reemplazo corre **todas** las validaciones de
un `prepare` normal **más** la validación completa del encargo conservado; la exigencia de
existencia es propia del sub-modo de reemplazo, cuyo objeto es dejar un encargo válido, no
del camino normal.)*

**PD-6 (lista de inputs vacía legítima).** `--input -` (lista vacía) en el reemplazo sigue
siendo válido (PD-20/D7 de 005-001): la validación completa de PD-1 **no** rechaza una lista
`inputs` vacía. *(Riesgo de T1 declarado en el discovery §T1.)*

**PD-7 (pisos obligatorios del rol intactos).** Tras cualquier corrección, el
`invariants`/`evidence_required` del sucesor contiene cada elemento obligatorio del rol
(`DEFAULT_INVARIANTS`/`DEFAULT_EVIDENCE`), que **nunca** se eliminan (PD-21 de 005-001, no
se relaja).

**PD-8 (política única de evidencia).** La metodología declara, en un **único** lugar
canónico (`skills/cdad-cycle/references/stage-3-tdd.md`, sección «Test evidence policy»), la
política de evidencia: (i) **regresión proporcional al cambio** (focales + módulos tocados);
(ii) **suite completa al cierre de la feature** (o antes, si un cambio toca instalador,
staging o renderer); (iii) **reutilización de evidencia registrada equivalente**, cuyo dueño
canónico es `skills/cdad-cycle/references/re-entry.md` §«Equivalence of a registered run»
(la política la **referencia**, no copia su texto). La metodología define **qué evidencia**
se exige; **el proyecto declara los comandos** (focales y suite). Una condición
local/entorno se **registra** en la evidencia y **no** se vuelve requisito. Verificable: la
sección existe, es única, y enuncia los cinco puntos.

**PD-9 (sin «suite completa por GREEN» en los consumidores).** Tras la alineación, ningún
consumidor afirma la suite completa **por cada GREEN**: `stage-3-tdd.md:153`,
`re-entry.md` (§«Implementer — GREEN»), `packets/substages/implementer-green.md`,
`implementer-refactor.md`, `implementer-review-fix.md`, `packets/roles/implementer.md`,
`SKILL.md` (gates `:297`/`:299`/`:304`/`:347`/`:357`/`:528`), y `references/handoff-prompts.md`,
`stage-4-review.md`, `stage-5-merge.md`, `sub-agent-strategies.md`, `anti-patterns.md`,
`state-detection.md` **referencian** la política (PD-8) y no duplican su texto. Verificable
por barrido: `grep -rn -iE "once per GREEN|full suite per GREEN|required full regression suite"`
en `references/` y `packets/` no devuelve afirmaciones de **frecuencia por GREEN**; cada
mención de la suite completa queda ubicada en el **cierre** (o remite a la política).

**PD-10 (paquete canónico de GREEN alineado).** `packets/substages/implementer-green.md`
deja de decir «the required full regression suite» (término indefinido) y remite a PD-8:
corre el test focal y la **regresión que el cambio requiere** (proporcional), con los
comandos que **declara el proyecto**; la suite completa es gate de **cierre**. Idem
`implementer-refactor.md` (mantener verde la regresión afectada) e `implementer-review-fix.md`
(re-correr afectados y regresión).

**PD-11 (enmienda de PD-17 de 005-001).** `docs/specs/005-001-idle-and-v7-bootstrap/spec.md`
PD-17 se **enmienda** para que su letra coincida con el recorrido **realmente ejecutado**
(`closure.md:51-57`, `debt.md:9-18` B2, `dispatch-ledger.md` fila 13): el paquete del
architect se **recibe y completa** (`record-dispatch` → staging → `receive` →
`validate-receipt` → transición) **antes** de preparar al test-writer, y el reemplazo se
prueba sobre un paquete **todavía `prepared` y no despachado**. La enmienda se declara **con
fecha** (2026-10-09) y su autoridad es la instrucción del dueño; **no** cambia el alcance ni
los criterios del epic. Al cambiar los bytes de `spec.md`, su `contract_sha256` deriva
(PD-4 de 005-001) y el pin de aprobación debe **re-registrarse** (o declararse el motivo por
el que no aplica a una feature `done`).

**PD-12 (resolución del origen de los agentes de proyecto).** `prepare` resuelve el origen de
los agentes de proyecto de OpenCode en este orden: (1) **opción explícita** por variable de
entorno `CDAD_OPENCODE_AGENTS_DIR`; (2) **por defecto**, la instalación registrada en el
**registro de activación del proyecto** (`.cdad/activation.json`) cuando existe → su carpeta
de agentes del runtime (`<adopted_root>/.config/opencode/agents`); (3) **sin activación**, el
camino actual (instalación global del runtime / HOME). Verificable: con un
`.cdad/activation.json` presente y **sin** la variable, el `source_dir` del manifiesto es el
de la raíz adoptada **registrada**, no HOME.

**PD-13 (contradicción diagnosticada, sin cambio de versión en silencio).** Cuando el origen
resuelto difiere del registrado en `.cdad/activation.json` (p. ej. variable vs registro) o
del `source_dir` del manifiesto anterior (caso MIX-V6V7), `prepare` emite un **diagnóstico**
que **dice cuál usaría y cómo resolverlo**, y que **nombra el registro de activación y la
versión/commit en juego**. Un aviso que **no** nombre el registro ni la versión **no**
alcanza. Verificable: el caso MIX-V6V7 produce un diagnóstico que nombra `.cdad/activation.json`
y las dos versiones; **nunca** se publican agentes de otra versión sin ese diagnóstico.

**PD-14 (versión verificable por sesión).** Cada agente publicado **y/o** el manifiesto
`.opencode/agents/.cdad-derived.json` declara la **versión/commit** de la instalación de
origen, de modo que sea verificable desde el artefacto publicado **qué versión cargó una
sesión**. Verificable: leer el agente publicado (o el manifiesto) devuelve la versión/commit
de la instalación de origen. *(Hoy el manifiesto sólo lleva `source_dir` + hashes y los
agentes publicados no declaran versión: `grep -i version .opencode/agents/*.md` sólo devuelve
comentarios.)*

**PD-15 (el adaptador de OpenCode documenta recarga y procedencia).**
`skills/cdad-cycle/references/opencode-delegation.md` documenta: (a) si una **sesión nueva**
relee agentes y skills o si hace falta **recargar** el servidor ya iniciado, y cómo; (b) qué
**versión** cargó una sesión. El hecho aportado por el dueño (OpenCode 2.0.22, **proceso
nuevo**: un agente de proyecto en `.opencode/agents/` reemplaza al global del mismo nombre)
se documenta como **dato**. `opencode reload` sobre un servidor **ya iniciado** está
declarado **NO comprobado**: la spec **exige** una **comprobación en aislamiento** (sin tocar
HOME ni el servidor del dueño) y, si no es posible, el **diagnóstico**; **nunca** se afirma
sin evidencia.

**PD-16 (normalización de `review.md` sin repetir la revisión).**
`docs/specs/005-001-idle-and-v7-bootstrap/review.md` se **normaliza** (coherencia,
referencias y ortografía) **sin re-evaluar**: se preservan el **veredicto**
(`changes-required`), los **bloqueantes** (B1), los **opcionales** (B2..B7), la tabla
**PD↔test** y las **abstenciones**. La referencia errónea a un **PD-27** inexistente
(`review.md:16`) se corrige a **PD-20** (opciones de corrección de 005-001). Verificable: no
quedan cadenas ininteligibles; la referencia nombra PD-20; el contenido técnico (veredicto y
buckets) es idéntico.

**PD-17 (rutas personales fuera de los documentos del epic-005).** Se retiran de
`docs/epics/epic-005-real-operation/` las rutas **personales/instalación-específicas**
(criterio en §7 D7), conservando los originales en el **registro local del proyecto**
(`.cdad/local/`, fuera de git). Aplicación por el criterio: son personales y se genericizan
`handoff-opencode.md:32` (`$HOME/.cache/cdad-adopted-ce09ed0/...`) y
`handoff-opencode-2.md:8` (`<repo>`) y `:14`
(`$HOME/.cache/cdad-adopted-ce09ed0/...`); son **convención genérica de runtime** y pueden
permanecer `handoff-opencode.md:63` y `execution.md:21` (`~/.claude`, `~/.agents`,
`~/.config/opencode` como HOME reservado al dueño). Verificable:
`grep -rn -E "/home/|/Users/|ofap|cdad-adopted-[0-9a-f]" docs/epics/epic-005-real-operation/`
no encuentra rutas personales. **VERIFY (dueño):** confirmar si `handoff-opencode.md:63` y
`execution.md:21` también deben retirarse (el encargo los enumera; el criterio los conserva).

**PD-18 (test de integración desde una instalación aislada).** Una versión nueva en el repo
que cumple los requisitos del ciclo; **como test de integración (no despliegue)**, se instala
en una **raíz aislada** (nunca HOME) y se comprueba que con ella se puede: (1) `prepare` un
encargo; (2) corregirlo con `--replace-packet` (con la validación completa de T1, PD-1..PD-4);
(3) despachar el encargo con la **validación proporcional** (T2), **sin rodeos manuales**.
Verificable: la secuencia corre end-to-end con el CLI de la raíz aislada y el paquete
publicado es despachable. **No** se promete ni se ejecuta despliegue en HOME (reservado al
dueño).

### 3. Invariantes (verificables)

- **INV-1.** `prepare` (incluido `--replace-packet`) jamás publica un paquete sin que pase la
  verificación de autorización del rol sobre el contrato del día (INV-1 de 005-001).
- **INV-2.** Ninguna operación de `prepare`/`--replace-packet` **escribe** aprobaciones
  (`stage_history`/`epic_history`) — INV-2 de 005-001.
- **INV-3.** El reemplazo nunca borra ni reescribe los bytes del paquete anterior
  (`REQUEST.json`/`PACKET.md` byte-idénticos) — INV-3 de 005-001.
- **INV-4.** La validación completa del reemplazo (PD-1) **no** cambia el camino normal de
  `prepare` (PD-5): el conjunto de validaciones de un `prepare` sin `--replace-packet` es el
  de hoy.
- **INV-5.** Los pisos obligatorios del rol (`DEFAULT_INVARIANTS`/`DEFAULT_EVIDENCE`) nunca se
  eliminan (PD-21 de 005-001; PD-7).
- **INV-6.** Política única: la regla de **equivalencia** tiene un solo dueño
  (`re-entry.md` §«Equivalence of a registered run»); la **política de evidencia** tiene un
  solo dueño (`stage-3-tdd.md` §«Test evidence policy»). Los consumidores **referencian** y no
  copian el texto de la regla.
- **INV-7.** Ninguna operación cambia de versión de instalación **en silencio**: un cambio de
  origen (variable vs registro vs global vs manifiesto anterior) siempre produce un
  diagnóstico que nombra el registro y las versiones (PD-13).
- **INV-8.** El test de integración de cierre **no** instala ni activa nada en HOME (PD-18).

### 4. Criterios de aceptación

- [ ] Un test por postcondición (PD-1..PD-18), con **control positivo interno** donde haya
  negativo.
- [ ] **Test focal del hueco de T1** (PD-2): un `input` conservado inexistente → `rc=2` con
  diagnóstico **campo/motivo/opción**, sin efectos; control positivo (la misma corrección
  válida → `rc=0`).
- [ ] **Test focal de recuperación** (PD-4) y de **no-regresión del camino normal** (PD-5);
  lista `inputs` vacía sigue válida (PD-6); pisos del rol intactos (PD-7).
- [ ] **Comprobación documental de T2**: barrido de «suite/regression» en `references/` y
  `packets/` sin afirmaciones de frecuencia **por GREEN**; la política única (PD-8) existe y
  los consumidores la referencian (PD-9/PD-10).
- [ ] **Enmienda de PD-17** (PD-11) registrada con fecha y decisión explícita sobre el pin.
- [ ] **T3**: test focal (PD-12) — con `.cdad/activation.json` presente y **sin** la variable,
  `source_dir` del manifiesto = raíz adoptada **registrada**; contradicción **diagnosticada**
  (PD-13); versión declarada (PD-14); adaptador documenta recarga y no afirma `opencode reload`
  sin comprobación aislada (PD-15).
- [ ] **Documentación**: `review.md` normalizado sin cambiar el veredicto y con PD-27→PD-20
  (PD-16); `grep` de rutas personales en `docs/epics/epic-005-real-operation/` sin resultados
  (PD-17).
- [ ] **Test de integración de cierre** (PD-18) verde desde la raíz aislada.
- [ ] **Suite completa verde** (la feature toca el renderer/CLI `cdad_packet.py`, el
  instalador/staging y docs → suite completa al cierre) y `make validate` sin fallos nuevos
  (los 2 FAIL F011 preexistentes no se atribuyen a este diff).

### 5. Fuera de alcance

- Activar/instalar versiones en el repo real ni **desplegar en HOME** (reservado al dueño).
- Cambios en el **alcance o los criterios** del epic-005; la enmienda de PD-17 (T2) es
  documental y no los cambia.
- Roles en Claude Code (005-004); medición de contexto (005-002); reducción de orientación
  (005-003).
- El resto de la deuda de 003-007 (`R2-STAGE`, `POLICY-CLASS`, `CKPT-FORK`, …).
- Repetir la review formal de 005-001 (PD-16 es **normalización**, no re-revisión).
- Tests por frases; tests de cobertura no derivados de un PD.
- Afirmar el comportamiento de `opencode reload` sin la comprobación en aislamiento (PD-15).

### 6. Contexto técnico

**T1 — reemplazo que valida lo conservado (`skills/cdad-cycle/scripts/cdad_packet.py`).**

- `_validate_corrections` (`:1843-1886`): hoy valida **sólo** si el campo está en `corrected`
  (`inputs` `:1850`, `read_scope` `:1862`, `write_scope` `:1877`). El único chequeo de
  existencia de inputs es `candidate.is_file()` (`:1858`).
- `validate_request` (`:723-828`) corre **después** en `_replace_packet` (`:2034`) y valida
  el documento completo, pero `_project_path` **no exige existencia** (`:814`) y sólo
  comprueba contención de scope (`:815`); los mensajes de política son genéricos
  (`:690`/`:694`/`:703`/`:816`). Por eso un `input` conservado inexistente **hoy pasa**.
- `_replace_packet` (`:1888-2070`): construcción del `assignment` conservado (`:1972-1983`),
  set `corrected` (`:1986-2011`), call sites (`:2022-2025`, `:2034`), publicación
  (`_publish_generation`, `:2058`). `ASSIGNMENT_UNIVERSE` (`:1809-1812`), `_sentinel_list`
  (`:1815-1830`), `_with_role_floor` (`:1833-1840`).
- Puntos de extensión: quitar el gate `if "X" in corrected` (validar también los conservados)
  o invocar `_validate_corrections` con el universo completo; extraer el chequeo de existencia
  (`:1858`) para aplicarlo a **todo** `inputs`; reusar los textos campo/motivo/opción
  (`:1854-1885`) para los campos conservados.

**T2 — una sola política de tests (docs).**

- Contradicciones verificadas: `stage-3-tdd.md:153` («once per GREEN») vs `:31`
  («gates, not for debugging»); `re-entry.md:149-150` («complete suite» por GREEN);
  `implementer-green.md:1` («the required full regression suite», indefinido);
  `SKILL.md:528`; gate del epic `plan.md:60-61`. Dueño canónico de la equivalencia:
  `re-entry.md:67-79` §«Equivalence of a registered run» (declarado «single canonical owner»
  en `:69`).
- Inventario del barrido (completo en el discovery §T2 y en el paquete): `references/` —
  `stage-3-tdd.md` (`:31`,`:57`,`:123`,`:137`,`:150`,`:153`,`:169`,`:217`), `re-entry.md`
  (`:67-79`,`:149-150`,`:158`,`:169`,`:173`), `handoff-prompts.md` (`:249`,`:265`,`:287`,
  `:304`,`:349`,`:377`,`:406`,`:411`,`:618`,`:639`), `stage-4-review.md` (`:144`,`:159`),
  `stage-5-merge.md` (`:24`,`:27`,`:84`,`:123`,`:147`,`:165`), `sub-agent-strategies.md`
  (`:36`,`:138`), `anti-patterns.md` (`:25`,`:29`,`:124`,`:170`), `state-detection.md`
  (`:57`,`:59`,`:90`), `receiving-feedback.md` (`:44`), `stage-2-specification.md` (`:112`),
  `stage-debugging.md` (`:91`,`:116`); `packets/` — `substages/implementer-green.md:1`,
  `implementer-refactor.md:1`, `implementer-review-fix.md:1`, `test-writer-audit.md:1`,
  `roles/implementer.md:1`; `SKILL.md` (`:70`,`:73`,`:120`,`:292`,`:297`,`:299`,`:304`,
  `:347`,`:357`,`:364`,`:527-531`,`:537`,`:571`,`:577`).
- PD-17 de 005-001 (`spec.md:109-115`) vs recorrido ejecutado (`closure.md:51-57`); deuda
  B2 (`debt.md:9-18`); registro (`dispatch-ledger.md` fila 13).

**T3 — procedencia de la instalación.**

- `_derived_source_dir` (`:2454-2457`): `os.environ.get(DERIVED_AGENTS_ENV)` (`:88`) o
  `DEFAULT_DERIVED_SOURCE` = `Path.home()/".config"/"opencode"/"agents"` (`:89`). **No**
  consulta activación (`grep "activation"` sin resultados).
- `_build_derived_payloads` (`:2680-2716`) escribe el manifiesto (`:2706-2712`) con
  `source_dir` + hashes + `policy_sha256`; `_publish_generation` (`:2976-2985`) imprime un
  aviso a stderr (rc 0) sin publicar derivados cuando no hay fuente, y **no** nombra el
  registro ni la versión.
- Registro de activación: `.cdad/activation.json` (`scripts/cdad-activate.py:294-313`;
  `references/runtime-adoption.md:37-39`); layout `<adopted_root>/.config/opencode/agents`
  (`dispatch-ledger.md:33`). Este repo **no** tiene `.cdad/activation.json` (`find` sin
  resultados) y su manifiesto apunta a HOME (`source_dir: <home>/.config/opencode/agents`).
- MIX-V6V7 real: `dispatch-ledger.md:84-101` (re-derivación de otra versión sin avisar).
- `references/opencode-delegation.md` no documenta recarga ni procedencia (`:1-119`).

### 7. Decisiones propuestas (a resolver al aprobar)

| Id | Propuesta del architect | Rationale |
|---|---|---|
| **D1** | **Dominio de validación del reemplazo: el encargo resultante completo** (conservado + corregido), incluida la existencia de `inputs`; el **camino normal no cambia** (PD-1/PD-5) | Cierra el hueco real (input conservado inexistente) sin sumar restricciones a `prepare`. Coherente con PD-22 de 005-001: el reemplazo corre **todas** las validaciones de un `prepare` **más** la validación completa del encargo conservado; la exigencia de existencia es propia del sub-modo de reemplazo (debe dejar un encargo válido), no del camino normal. |
| **D2** | **Diagnóstico accionable también para campos conservados**: nombrar **campo/motivo/opción** (reusar los textos de `_validate_corrections`) en vez del mensaje genérico de `validate_request` | El dueño debe poder corregir el encargo; reusar los textos existentes evita duplicar lógica (discovery §T1, puntos de extensión). |
| **D3** | **Dueño canónico de la política de evidencia**: `stage-3-tdd.md` §«Test evidence policy» (i/ii/iv/v); la **equivalencia** (iii) sigue en `re-entry.md` §«Equivalence of a registered run». Los consumidores **referencian** (PD-8/PD-9) | Una sola definición editable por regla; evita el drift que hoy produce las contradicciones (discovery §T2). |
| **D4** | **Origen de agentes: variable > registro de activación > global** (PD-12), con **contradicción diagnosticada** que nombra registro y versiones (PD-13) | El registro **nombra la instalación**; la variable queda como **opción explícita** (el dueño usa una GUI con servidor permanente: el entorno no puede ser el mecanismo normal). `prepare` no debe cambiar de versión en silencio (caso MIX-V6V7). |
| **D5** | **Versión verificable**: declararla en el manifiesto **y/o** en cada agente publicado (PD-14) | Hoy no es verificable desde el artefacto qué versión cargó una sesión (discovery §T3). |
| **D6** | **`opencode reload` no se afirma sin comprobación aislada**; si no es posible, diagnóstico (PD-15) | Declarado **no comprobado** por el dueño; la spec no puede afirmarlo sin evidencia (honestidad de evidencia). |
| **D7** | **Criterio de «ruta personal»**: es personal/instalación-específica una ruta que nombra **identidad de instalación/máquina/usuario** (absoluta bajo un home, `cdad-adopted-<sha>`, `/tmp` de corridas) → fuera del repo, al **registro local** `.cdad/local/` (git-ignorado). Es **convención genérica de runtime** (`~/.claude`, `~/.agents`, `~/.config/opencode` = HOME reservado al dueño) → permanece por ser regla de metodología. **VERIFY (dueño):** `handoff-opencode.md:63` y `execution.md:21` | Distingue lo portable de lo instalación-específica; `.cdad/local/` ya es el patrón local (`handoff-005-005.local.md`) y `.cdad/` está git-ignorado (`.gitignore:11`). El encargo enumera `:63`/`:21`; el criterio los conserva → confirmar con el dueño. |
| **D8** | **Cierre como test de integración en raíz aislada, no despliegue** (PD-18) | Plan fila 2 y handoff §4; el despliegue en HOME está reservado al dueño (`execution.md:19-23`). |

### 8. Aprobación

- **Estado: aprobada** (2026-10-09) por el **orquestador OpenCode** (HITL delegada epic-005,
  `docs/epics/epic-005-real-operation/execution.md`).
- Se registró la entrada `stage_history` `specification` con **pin** (`contract_path` =
  `docs/specs/005-005-adoption-coherence/spec.md` y `contract_sha256` del archivo materializado),
  según PD-3/PD-18 de 005-001. El `sha256` del archivo vive en el `state`, no dentro del archivo.
- Las **decisiones D1–D8** de §7 se aprobaron tal como se proponen.
- **VERIFY (dueño), abierto:** D7 conserva `~/.claude`/`~/.agents`/`~/.config/opencode` como
  convención genérica de runtime y retira las rutas instalación-específicas; el encargo enumeraba
  `handoff-opencode.md:63` y `execution.md:21` → confirmar si también deben retirarse.
