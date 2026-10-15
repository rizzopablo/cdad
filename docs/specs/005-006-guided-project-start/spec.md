> Spec **aprobada** (2026-10-10) junto con el plan. Texto del **architect** (subetapa `draft`,
> etapa 2), materializado con el flujo (receive + materialize create-only) por el orquestador
> (ADR-003); aprobada por el orquestador OpenCode bajo la delegación HITL de epic-005.
> Decisiones D1–D8 aprobadas tal como se proponen en §7. VERIFY 5 del discovery §12 queda
> **abierto** y se cierra (o se declara) en la corrida real R2 de aceptación.
> Insumo verificado: `docs/specs/005-006-guided-project-start/discovery.md` (mapa con
> archivo:línea; leído antes de proponer). Complementos: `findings/session-guided-start-friction-2026-10-10.md`
> y `docs/epics/epic-005-real-operation/evidence/005-006-attempt-1.md`.
> Contrato: `docs/epics/epic-005-real-operation/plan.md` (fila 3, `:35`; sha256 `4b403b0e…d6c71`).

## Spec — 005-006-guided-project-start

**Feature ID:** `005-006-guided-project-start` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobada (2026-10-10, orquestador OpenCode, HITL delegada epic-005). ADR-011 gobierna autoridad, capacidades y límites.

```yaml
feature_id: 005-006-guided-project-start
feature_name: Arranque guiado de proyectos — una instrucción breve basta para la primera delegación útil
created_at: 2026-10-10
status: approved
approved_by: orchestrator OpenCode (HITL delegada epic-005)
approved_at: 2026-10-10
```

### 1. Descripción funcional

El resultado no es una firma de función ni un controlador nuevo: es que **una instrucción
breve baste para alcanzar una primera delegación útil**. La instrucción breve canónica es la
del contrato (`plan.md:35`):

> «usá CDAD para inicializar este proyecto y comenzar su análisis preliminar».

Hoy esa instrucción **no** basta porque el intake del orquestador solo nombra dos caminos
—*prepared execution* y *legacy = cargar `cdad-cycle`, SECOND*— y ninguno cubre el arranque
desde reposo con un proyecto no reconocido (`discovery §5.1`, `sources/roles/orchestrator.md:19-43`).
El arranque hay que **deducirlo** combinando cinco referencias largas (`discovery §1.2`);
no existe ningún procedimiento corto de arranque (`skills/cdad-cycle/references/` no tiene
archivo de arranque/reconocimiento, verificado). 005-006 **introduce ese procedimiento corto**
y lo conecta al intake, **sin trasladar el prompt largo a una plantilla** (`plan.md:35`, cierre;
`discovery §8`).

La aceptación es el **comportamiento observable** en tres recorridos concretos de uso
(petición inicial → primera entrega), que se validan y refinan a partir de `discovery §9`:

- **R1 — Proyecto nuevo, desde reposo (fixture determinista).** Instrucción breve → el
  orquestador carga la metodología instalada por iniciativa propia (corrige la fricción 1) →
  `state-detection` infiere **bootstrap** (sin Memory Bank) → el procedimiento crea el Memory
  Bank preguntando lo mínimo → registra las restricciones que correspondan → **encadena al
  primer encargo** (a diferencia de hoy, donde el bootstrap de Memory Bank y el bootstrap de
  ejecución v2 no se encadenan, `discovery §9` R1). Fin observable: **un encargo preparado y
  despachable** (no meramente una orientación).
- **R2 — Proyecto existente parcialmente inicializado con epic activo (caso de aceptación
  real; el proyecto lo elige el dueño y se identifica en el registro local, no en este repo).**
  Instrucción breve → reconocer la raíz aunque la sesión abra en un directorio contenedor
  (el directorio de sesión es pista, no norma: `findings:31-35`) → detectar `active_epic`/
  `active_feature` → detectar el **desfase entre el plan aprobado y `epic_features`** (fricción 5)
  y **encaminar su sincronización** (PD-12) → **no** ejecutar `resume` en reposo (fricción 4) →
  preparar el primer encargo con el **CLI instalado** (fricción 2). Fin observable: **primera
  delegación útil** (p. ej. el discovery del architect).
- **R3 — Configuración incompleta (fixture determinista).** State presente y
  `docs/cdad-policy.json` ausente → `prepare` falla cerrado (PD-1 de 005-005/004-002); o
  autoridad sin pin → `approval pending` rc=2. El arranque debe **decir qué falta y cómo
  seguir**, sin inventar ni cambiar de versión en silencio (`discovery §9` R3). Fin observable:
  **diagnóstico accionable + parada cerrada** (salida legítima del arnés).

**Refinamientos sobre `discovery §9`** (los tres recorridos se validan; se precisan):
(i) R1 y R3 se declaran como fixtures deterministas y agnósticos del proyecto; R2 es la
aceptación **real** (registro local) — así la aceptación no depende de nombres, carpetas ni
entorno de un proyecto concreto (`plan.md:35`). (ii) El fin observable de R1/R2 se ancla en
**un encargo preparado/despachable**, no en "haber reconocido". (iii) Se agrega la
comprobación empírica de `resume` sin checkpoint (PD-17, cierra el VERIFY 2).

### 2. Contrato

**Contrato bidireccional (el arnés ↔ el rol).** El `plan.md:35` exige que el contrato obligue
en las **dos direcciones**. 005-006 declara:

- **Lo que el arnés da al rol** (insumos y capacidades): la instrucción breve; el intake del
  orquestador con una **entrada de arranque desde reposo** (PD-2) que ordena cargar la
  metodología **primero**; y un **procedimiento corto** (`references/project-start.md`, PD-1)
  que compone —por referencia, nunca copiando— los primitivos ya existentes
  (`state-detection`, `project-execution`, `continuity`, `bootstrap`, `cdad-epic/state-detection`)
  y le indica cómo reconocer, registrar restricciones y preparar el primer encargo.
- **Lo que el rol devuelve** (salida): un **encargo completo y despachable** (PD-8), o un
  **diagnóstico accionable** cuando falta un insumo no inferible (PD-14).
- **Salida legítima ante bloqueo** (la dirección que hoy falta, `discovery §5.1`): ante
  configuración incompleta (R3) o desfase de `epic_features` (R2), el procedimiento **nombra
  qué falta** (campo/archivo/marcador) **y cómo seguir** (quién decide / a dónde volver), y
  **no** inventa autoridad, no cambia de versión en silencio y no prepara un paquete inválido.

**Superficie que 005-006 toca (sin controlador nuevo, sin flags nuevos):**

- **Nuevo:** `skills/cdad-cycle/references/project-start.md` — el procedimiento corto de
  arranque/reconocimiento (referencia, no plantilla de prompt). Es el hueco estructural del
  `discovery §1.2`; resuelto con **referencia nueva + entrada de intake** (ambas).
- **Modificado (fuente canónica):** `sources/roles/orchestrator.md` (intake: entrada de
  arranque desde reposo; cableado de continuidad/re-entry con la ruta del **CLI instalado**).
  Regenera `agents/cdad-orchestrator.md` y `agents/claude-code/cdad-orchestrator.md`.
- **Modificado (referencias de `cdad-cycle`):** `SKILL.md` (fila de la tabla de referencias +
  paso 1 del flujo), `references/state-detection.md` (dueño canónico declarado),
  `references/continuity.md` (ruta del CLI instalado).
- **Modificado (`cdad-epic`):** `references/epic-planning.md` (responsable de sincronizar
  `epic_features`).
- **Modificado (docs):** `README.md` (arranque guiado, puntero corto).
- **Sin cambios de código de producto.** El enforcement de `epic_features` (`cdad_packet.py:549-554`,
  `:1459-1509`) y el comportamiento de `prepare` **no** cambian.

**Postcondiciones (numeradas y verificables):**

**PD-1 (existe un procedimiento corto y es la entrada única del arranque).** Existe
`skills/cdad-cycle/references/project-start.md`: es el procedimiento **corto y directo** del
arranque desde reposo, y la tabla «How to read the references» de `SKILL.md` tiene una fila
para él. Es **una sola lectura**; **referencia** a `state-detection.md`, `project-execution.md`,
`continuity.md`, `bootstrap.md` y `cdad-epic/references/state-detection.md`, y **no reproduce**
sus reglas (no copia el algoritmo de detección ni el texto de política/autoridad). Verificable:
el archivo existe; la fila existe; un barrido no encuentra el algoritmo de detección ni el
texto de política duplicados en él.

**PD-2 (el intake tiene una entrada de arranque desde reposo).** `sources/roles/orchestrator.md`
(intake, `:19-43`) incorpora una **entrada explícita** para el caso "llega una instrucción
breve, no hay ejecución preparada, el proyecto no está reconocido": **ordenar cargar la
metodología primero** (`cdad-cycle`) y **señalar** `references/project-start.md`. La condición
*«legacy, SECOND»* deja de ser la única vía y deja de ser ambigua en reposo. El agente
generado `agents/cdad-orchestrator.md` (y `agents/claude-code/cdad-orchestrator.md`) refleja
la fuente (regenerados por el generador). Verificable: la entrada existe en la fuente; el
generado coincide con la fuente (contrato del generador); ya no hay un arranque sin camino
definido en el intake.

**PD-3 (reconocimiento sin imponer layout).** El procedimiento reconoce la raíz del proyecto
aunque la sesión abra en un **directorio contenedor** (repo anidado): el directorio de sesión
es **pista, no norma**. Verificable: el texto lo declara; en R2 la sesión abierta en el
contenedor llega al repo anidado **sin** una búsqueda global.

**PD-4 (clasificación en nuevo / parcial / configuración incompleta, por referencia).** El
procedimiento distingue los tres casos **usando los primitivos existentes por referencia**
(`state-detection §Step1/§Step2`; `project-execution §1-§3`; ausencia de
`.cdad/activation.json`), sin re-declarar el algoritmo: *nuevo* = sin Memory Bank; *parcial* =
Memory Bank con `active_epic`/`active_feature`; *incompleta* = state presente y/o política/
autoridad faltante. Verificable: el procedimiento nombra las tres clases y apunta a los
primitivos; no contiene una copia del algoritmo de detección.

**PD-5 (preservar lo existente).** El reconocimiento/inicialización **no pisa** documentación,
planes ni convenciones existentes (nombres de épicas y features). Verificable: el
procedimiento enuncia la regla y referencia los anti-patrones de `bootstrap.md:121-125` y el
no-clobber de `project-execution.md:84-97`; en R2 el `plan.md` existente y la nomenclatura
`<epic-num>-<feat-num>-<slug>` quedan intactos.

**PD-6 (registro de restricciones en su lugar canónico; crear solo lo que falte).** El
procedimiento registra cada restricción descubierta en su **lugar canónico** y **crea solo lo
que falte** (si el lugar ya existe, registra/apunta, no sobrescribe):

| Restricción | Lugar canónico | Cómo se obtiene |
|---|---|---|
| `stack` | `state.stack` | autodetectado por convención `*-architect` (referencia `bootstrap.md:37-64`); ambigüedad → preguntar o registrar la duda |
| privacidad | `docs/cdad-policy.json` → `path_policy.private_paths` | **edición reservada** (`project-execution.md:7-38`) → inferir y **proponer**, no escribir sin decisión |
| entorno de pruebas | `test_roots` de la política + comandos que **declara el proyecto** | metodología define la evidencia (INV-6, `systemPatterns.md:241-246`); Odoo vía `skills/odoo-make-env/` |
| límites operativos | `policy.temporary_roots` + ADR-011 | `project-execution.md:7-17` |
| autoridad | `state.hitl_delegation`/`approver` + `docs/epics/<epic>/execution.md` | **decide el usuario** (no delegable) |
| organización/convenciones | Memory Bank `projectbrief.md`/`systemPatterns.md` | bootstrap pregunta lo mínimo (`bootstrap.md:23-35`) |

Verificable: el procedimiento contiene esta tabla (forma máquina-legible: tabla o lista
canónica) y no inventa un lugar nuevo para ninguna restricción.

**PD-7 (inferible vs decide el usuario; preguntar solo lo segundo, acotado).** Para cada
restricción el procedimiento marca **inferible** (autodetectable con evidencia objetiva) vs
**decisión del usuario**; pregunta **solo** las segundas y **acotado** (referencia a la regla
existente «tres o cuatro preguntas concretas», `bootstrap.md:23-35`); sin usuario presente
registra la duda en `activeContext.md` en vez de preguntar. Verificable: la distinción existe;
`stack` es automático (referencia `bootstrap.md §2b`); la autoridad/privacy se listan como
decisión del usuario.

**PD-8 (el arranque termina en un encargo completo — primera delegación útil).** El recorrido
de arranque **encadena** reconocimiento → registro de restricciones → **preparación del primer
encargo**, usando el camino de ejecución preparada (`project-execution.md`), de modo que la
primera delegación sea útil sin una segunda sesión de deducción. Verificable: R1 y R2 alcanzan
un **encargo preparado/despachable** como paso terminal (hoy el bootstrap de Memory Bank y el
bootstrap de ejecución v2 no se encadenan, `discovery §9` R1).

**PD-9 (no `resume` en reposo: rama de arranque).** El procedimiento **distingue** «iniciar
la unidad siguiente / arrancar desde reposo» de «reanudar una ejecución activa»: **sin
ejecución activa no prescribe ni ejecuta `resume`** (`resume` queda para una ejecución activa,
005-003). Corrige la prescripción ambigua `SKILL.md:244` / `orchestrator.md:86` **solo para la
rama de arranque** (agrega la rama «sin ejecución activa → no `resume`»); **no** reduce las
lecturas ni cambia el contrato de `resume` (eso es 005-003). Verificable: el procedimiento y
el texto corregido enuncian la rama; en R2 la sesión no llama `resume` en reposo.

**PD-10 (CLI instalado: sin rutas relativas al proyecto).** El cableado del arranque
(intake + procedimiento + las referencias que apunta) invoca el **CLI instalado**
(`$CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/…`, `README.md:5-10`) y **no** una ruta relativa
al proyecto consumidor (`scripts/…`, `skills/cdad-cycle/…`). El origen de la instalación se
resuelve con el mecanismo de procedencia que **ya fijó 005-005** (renovar por referencia, sin
re-declarar su precedencia). Verificable: un barrido del cableado de arranque no encuentra una
ruta relativa al proyecto para el CLI instalado; `sources/roles/orchestrator.md:80-98`,
`SKILL.md:260-261`/`:451-452` y `continuity.md:31-44` quedan corregidos/marcados como
relativos-a-la-instalación.

**PD-11 (README documenta el arranque guiado).** `README.md` (único `documentation_file` de la
política) incorpora una sección **corta** de arranque guiado que enuncia que una instrucción
breve basta y **referencia** `references/project-start.md`; **no** contiene el prompt largo.
Verificable: la sección existe; remite al procedimiento; no reproduce el prompt.

**PD-12 (responsable de `epic_features` + respuesta del arranque al desfase).**
`skills/cdad-epic/references/epic-planning.md` §«If the plan needs to be updated during the
feature loop» (`:130-143`) **asigna el responsable**: aplicar un cambio de plan aprobado
**incluye sincronizar `epic_features`** (el **coordinador de epic** es el responsable; el
escritor único del state es el orquestador). Y el procedimiento de arranque, al detectar un
desfase (R2), **nombra las entradas faltantes/sobrantes** y **encamina la sincronización**
(volver a `cdad-epic`) — **no** inventa features ni se bloquea en silencio. El enforcement en
código (`cdad_packet.py:549-554`, `:1459-1509`) **no** cambia. Verificable: el texto asigna el
responsable; el procedimiento describe el manejo del desfase.

**PD-13 (dueño canónico del reconocimiento, unificado por referencia).** Se declara el dueño
canónico: **reconocimiento feature/Memory-Bank** → `skills/cdad-cycle/references/state-detection.md`;
**reconocimiento de etapa de epic** (incl. el vocabulario `epic_stage`, ya declarado en
`cdad-epic/references/state-detection.md:16-22`) → `skills/cdad-epic/references/state-detection.md`;
y el **arranque desde reposo** (la composición de ambos) → `references/project-start.md`, que
los **referencia** y **no** re-declara ninguno. Verificable: la declaración existe; ningún
dueño se copia en otro archivo.

**PD-14 (salida legítima ante bloqueo: diagnóstico accionable, sin inventar).** Ante un insumo
faltante (política ausente, autoridad sin pin), el arranque produce un **diagnóstico** que
nombra **qué falta** y **cómo seguir**, reusando los marcadores existentes (`approval pending`,
`state incoherent`; referencia, no re-implementación), y **no** fabrica autoridad, no cambia de
versión en silencio y no publica un paquete inválido. Verificable: R3 produce el diagnóstico y
se detiene en cerrado; no hay autoridad fabricada.

**PD-15 (sin plantilla del prompt largo).** La solución es un **procedimiento operativo corto**;
el prompt largo **no** se traslada a una plantilla/documento. Verificable: no se agrega bajo
`assets/` ninguna plantilla que reproduzca el prompt; el procedimiento referencia las reglas
existentes.

**PD-16 (la aceptación es el comportamiento observable en los recorridos).** La aceptación se
declara como **comportamiento observable** en R1/R2/R3; R2 es el arranque **real** del proyecto
elegido por el dueño (identificado en el registro local, `.cdad/local/`, fuera de git). El
criterio es **funcional** (cada comprobación resuelve una duda que afecta el próximo despacho y,
una vez satisfecha, el proceso avanza), **no** un tope de lecturas ni de llamadas
(`findings:188-192`). Verificable: la checklist de aceptación mapea cada recorrido a un estado
final observable.

**PD-17 (`resume` sin checkpoint: rc=0, verificado empíricamente).** El comportamiento
documentado —`resume` sin checkpoint rinde la proyección vacía `no-checkpoint` con `rc=0`
(`continuity.md:19`; `cdad_continuity.py:1252`)— se **fija con un test focal** contra el CLI
(instalado/repo). Verificable: el test afirma `rc=0` y la proyección vacía; si el CLI discrepa,
se **reporta el defecto** (no se asume).

### 3. Invariantes (verificables)

- **INV-1.** El arranque es un **procedimiento corto único** que **referencia** las reglas
  existentes y **nunca** las copia (no hay segunda definición del algoritmo de detección ni de
  la política/autoridad).
- **INV-2.** El reconocimiento/inicialización **nunca** pisa documentación, planes ni
  convenciones existentes (`bootstrap.md:121-125`; `project-execution.md:84-97`).
- **INV-3.** Solo el **usuario** decide lo no inferible (autoridad; edición de privacidad; alcance);
  el arranque pregunta **solo** eso y, sin usuario, **registra la duda** — nunca inventa.
- **INV-4.** El arranque **nunca** ejecuta `resume` sin ejecución activa, **nunca** fabrica
  autoridad y **nunca** cambia de versión en silencio.
- **INV-5.** Se opera con el **producto instalado**: el cableado del arranque **no** usa rutas
  relativas al proyecto para el CLI instalado y reusa la procedencia de 005-005.
- **INV-6.** **No** se traslada el prompt largo a una plantilla (`plan.md:35`).
- **INV-7.** **No** cambian el alcance ni los criterios de aceptación del epic-005; la
  activación de versiones, los cambios en HOME y la confianza de carpeta de Claude Code siguen
  **reservados al dueño** (`execution.md:19-23`).
- **INV-8.** La **medición** de contexto es de 005-002; 005-006 define comportamiento
  observable, no presupuestos de tokens ni topes de llamadas (`findings:188-192`).

### 4. Criterios de aceptación

- [ ] **PD-1/PD-13**: `references/project-start.md` existe, es corto, y **referencia** (no
  copia) los dueños canónicos; la fila de la tabla de `SKILL.md` existe.
- [ ] **PD-2**: la fuente del intake tiene la entrada de arranque desde reposo; el generador
  produce los agentes y el generado coincide con la fuente.
- [ ] **PD-3/PD-4/PD-5/PD-6/PD-7/PD-8**: el procedimiento declara —sin imponer layout— la
  clasificación (nuevo/parcial/incompleta) por referencia, la preservación, la tabla
  restricción→lugar canónico, la distinción inferible/decide-el-usuario (preguntas acotadas) y
  el encadenado hasta el primer encargo.
- [ ] **PD-9/PD-10**: la rama «sin ejecución activa → no `resume`» está enunciada; el cableado
  del arranque no usa rutas relativas al proyecto para el CLI instalado.
- [ ] **PD-11**: `README.md` tiene la sección de arranque guiado que referencia el
  procedimiento y no reproduce el prompt.
- [ ] **PD-12**: `epic-planning.md` asigna el responsable de `epic_features`; el procedimiento
  describe el manejo del desfase; el enforcement de código sin cambios.
- [ ] **PD-14**: R3 produce diagnóstico accionable y parada cerrada; sin autoridad fabricada.
- [ ] **PD-15**: no hay plantilla nueva con el prompt largo.
- [ ] **PD-16**: **arranque real de R2** (proyecto del dueño, registro local) hasta una primera
  delegación útil, con evidencia; R1 y R3 como fixtures deterministas verdes.
- [ ] **PD-17**: test focal verde de `resume` sin checkpoint (`rc=0`, proyección vacía) contra el CLI.
- [ ] **Suite completa verde al cierre** y `make validate` sin fallos nuevos (los 2 FAIL F011
  preexistentes no se atribuyen a este diff).

### 5. Fuera de alcance

- **Medición** de contexto y su herramienta (005-002); presupuestos de tokens o topes de
  llamadas como criterio (`findings:188-192`).
- **Orientación al retomar y selección del camino de continuidad** (005-003): la lectura
  compacta y la **reducción** de lecturas previas al `resume` (base 18 de la sonda 2).
- Roles en **Claude Code** (005-004); planificación progresiva / tamaño de unidad (005-007).
- CI, ANON-1, R2-STAGE, POLICY-CLASS y el resto de la deuda de 003-007.
- **Activar versiones** en el repo real, **cambios en HOME**, **confianza de carpeta de Claude
  Code** y cambios de alcance/criterios del epic (reservado al dueño).
- Cambiar el comportamiento de `prepare` o el enforcement de `epic_features` en código.
- Redefinir la precedencia de procedencia de la instalación (dueño canónico: 005-005).

### 6. Contexto técnico (verificado)

**Hueco estructural (`discovery §1.2`).** `skills/cdad-cycle/references/` **no** contiene
ningún archivo de arranque/reconocimiento (verificado: `ls` solo lista
`anti-patterns, bootstrap, claude-code-delegation, continuity, handoff-prompts,
opencode-delegation, progress-guards, project-execution, receiving-feedback, re-entry,
runtime-adoption, stage-1..5, stage-debugging, state-detection, sub-agent-strategies,
verdict-tuple`); la tabla de carga (`SKILL.md:443-460`) no tiene fila para arrancar desde
reposo. Tres «inicializaciones» conviven sin desambiguar en un lugar corto
(`discovery §1.2`): Memory Bank (`bootstrap.md:66-102`), ejecución v2
(`project-execution.md:84-97`; `cdad_packet.py:1571`, `:1650-1659`), adopción/activación por
runtime (`runtime-adoption.md:9-39`, `scripts/cdad-activate.py`).

**Intake (fricción 1).** `sources/roles/orchestrator.md:19-43` (idéntico
`agents/cdad-orchestrator.md:11-37`): «Prepared execution path» + «Legacy path (fallback,
SECOND)». `legacy-loads: cdad-cycle only` (`:46-48`). El disparador vive en la `description`
del SKILL (`SKILL.md:3`), no en una orden operativa. `discovery §5.1`: no hay camino para
arranque desde reposo con proyecto no reconocido.

**Rutas relativas al proyecto (fricción 2).** `sources/roles/orchestrator.md:80-82`
(`skills/cdad-cycle/references/continuity.md`, `scripts/cdad_continuity.py`), `:97-98`
(`…/re-entry.md`, `scripts/cdad_result.py`); `SKILL.md:260-261` (`scripts/cdad_packet.py
render`), `:451-452`; `continuity.md:31-44`
(`python3 skills/cdad-cycle/scripts/cdad_continuity.py …`). Producto instalado:
`install.sh:47-52` (`$INSTALL_ROOT/.config/opencode/{agents,skills}`, `.agents/skills`,
`.claude/skills`); `README.md:5-10` fija
`$CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/cdad_packet.py`; `runtime-adoption.md:37-39`
registra la raíz adoptada. En otro proyecto esas rutas relativas al consumidor **no existen**
(`discovery §4.2`).

**`resume` en reposo (fricción 4).** `SKILL.md:244` («rebuild the carried context first with
`resume`»), `sources/roles/orchestrator.md:86`, `continuity.md:19` (sin checkpoint rinde
proyección vacía `no-checkpoint` rc 0). `cdad_continuity.py:1252` (`"state": "no-checkpoint"`).

**`epic_features` (fricción 5).** `cdad_packet.py:549-554`, `:1459-1509` exigen la entrada en
`epic_features` (exactamente una vez, no cerrada) y `active_feature` coincidente. El
procedimiento no asigna responsable: `epic-planning.md:120-122` (gate E2→features, único punto
que puebla `epic_features`), `:130-143` («If the plan needs to be updated during the feature
loop», no menciona `epic_features`), `feature-handoff.md:89-98` (feature falla, no alta de
features nuevas).

**Registro de restricciones (`discovery §3`).** stack `bootstrap.md:37-64`, activación
`SKILL.md:125-132`; privacidad `project-execution.md:21-38`; entorno de pruebas
`systemPatterns.md:241-246` (INV-6) + `execution.json.test_roots`; límites operativos
`project-execution.md:7-17`+ADR-011; autoridad `plan.md:68-79`+`execution.md`, enforcement
`project-execution.md:74-82`.

**Dueños canónicos.** `state-detection.md` feature (canónico) y `cdad-epic/references/state-detection.md`
etapa de epic (canónico del vocabulario `epic_stage`, `:16-22`).

**Reconocimiento compartido con 005-003.** `plan.md:35` (frontera): «comparten el mismo
procedimiento de reconocimiento del proyecto». `plan.md:37`: 005-003 reduce lecturas previas
al `resume` (base 18) y se acepta con sonda medida por 005-002.

### 7. Decisiones propuestas (a resolver al aprobar)

| Id | Propuesta del architect | Rationale |
|---|---|---|
| **D1** | **Salida del hueco = referencia nueva + entrada de intake (ambas)**: `references/project-start.md` (procedimiento corto) **y** una entrada de arranque en el intake (`sources/roles/orchestrator.md`) | La referencia sola no se carga por iniciativa propia (fricción 1: falta *orden operativa*); el intake solo, sin procedimiento corto, obliga a deducir (fricción 6). Ambas direcciones del contrato. |
| **D2** | **`resume` no aplica en reposo**: el arranque distingue «iniciar siguiente / arrancar» de «reanudar ejecución activa» (PD-9) | Cierra la fricción 4 del lado del arranque; la reducción de orientación/lecturas y la selección fina del camino de continuación quedan en 005-003. |
| **D3** | **CLI instalado por procedencia de 005-005** (PD-10): el cableado de arranque no usa rutas relativas al proyecto | Fricción 2; usa el registro de activación/`$CDAD_INSTALL_ROOT` ya fijado por 005-005 sin re-declarar precedencia. |
| **D4** | **Dueño canónico del reconocimiento** (PD-13): feature/Memory-Bank → `cdad-cycle/state-detection.md`; etapa de epic → `cdad-epic/state-detection.md`; composición de arranque → `project-start.md` (referencia) | Cierra el VERIFY 1 sin un merge riesgoso de dos archivos que detectan **objetos distintos**. No absorbe 005-003. |
| **D5** | **Responsable de `epic_features` = coordinador de epic** (PD-12), y el arranque **encamina** el desfase sin inventar | Cierra el VERIFY 6 con un dueño único ya implícito (`epic-planning.md:120-122`); evita que el ciclo mute el plan del epic por su cuenta. |
| **D6** | **README gana una sección corta de arranque guiado** que referencia el procedimiento (PD-11) | Cierra el VERIFY 4 sin duplicar el prompt (INV-6); `README.md` es el único `documentation_file` de la política. |
| **D7** | **Aceptación = comportamiento en R1/R2/R3**, con R2 real y R1/R3 por fixtures; el criterio es **funcional**, no un tope de lecturas (PD-16) | `plan.md:35` y `findings:188-192`; evita fijar un presupuesto que no se midió (medición = 005-002). |
| **D8** | **Sin plantilla del prompt largo** (PD-15, INV-6) | Límite explícito del plan (`plan.md:35`, cierre); la solución es procedimiento operativo. |

### 8. VERIFY del discovery §12 — estado y cierre

| # | VERIFY | Estado | Resolución / dueño y cuándo |
|---|---|---|---|
| 1 | Dueño canónico del reconocimiento compartido | **CERRADO** | PD-13/D4: dueño declarado por objeto; `project-start.md` referencia. |
| 2 | `resume` rc=0 sin checkpoint | **CERRADO (empírico)** | PD-17: test focal contra el CLI; si discrepa, **test-writer** reporta el defecto en stage 3 (RED). |
| 3 | Camino de invocación del CLI instalado | **CERRADO** | PD-10/D3: se usa el producto instalado; procedencia de 005-005 (referencia). |
| 4 | `README.md` no documenta el arranque guiado | **CERRADO** | PD-11/D6: sección corta de puntero. |
| 5 | Activación del proyecto de aceptación | **ABIERTO** | No es afirmable desde este repo (depende de su entorno). **Lo cierra el orquestador con el dueño, durante la corrida de aceptación R2 de 005-006** (la spec no asume activación/global/variable). |
| 6 | Responsable de sincronizar `epic_features` | **CERRADO** | PD-12/D5: responsable = coordinador de epic; el arranque encamina el desfase. |

### 9. Fronteras y no-cambio de alcance

- **Frontera con 005-003** (`plan.md:35`, `:37`; `findings:100-105`). **Dentro de 005-006:**
  el **arranque** desde reposo (reconocimiento de entrada, registro de restricciones, primer
  encargo) y la **rama de arranque** de la fricción 4 («sin ejecución activa → no `resume`»,
  PD-9). **Diferido a 005-003:** la **orientación al retomar** y la **selección del camino de
  continuidad** con ejecución activa, la **lectura compacta** y la **reducción** de lecturas
  previas al `resume` (base 18 de la sonda 2), aceptada con sonda medida por 005-002.
  *Motivo:* 005-006 resuelve la **entrada**; 005-003 optimiza la **reanudación**. El
  procedimiento de reconocimiento es **compartido** y por eso PD-13 fija su dueño (VERIFY 1).
- **Frontera con 005-002** (`plan.md:36`). **Dentro de 005-006:** la **fricción 6** en su parte
  de **comportamiento observable** (existe un procedimiento corto; el arranque llega a un
  encargo completo). **Diferido:** la **medición** del contexto (tokens, lecturas, primer
  `resume`) con la herramienta de 005-002. *Motivo:* 005-006 no introduce telemetría ni fija
  presupuestos; su aceptación es funcional (PD-16, INV-8).
- **No cambia el alcance ni los criterios del epic-005** (INV-7); no cambia el objetivo del
  epic (`plan.md:137-138`). La **activación de versiones**, los **cambios en HOME** y la
  **confianza de carpeta de Claude Code** siguen **reservados al dueño** (`execution.md:19-23`).

### 10. Aprobación

- **Estado: aprobada (2026-10-10)** por el **orquestador OpenCode** bajo la delegación HITL
  del epic-005 (`execution.md`), con la autoevaluación de `stage-2-specification.md §2.3` y las
  decisiones D1–D8 aprobadas tal como se proponen en §7 (VERIFY 5 abierto, a cerrar en R2).
  La aprobación de la spec es **no delegable por defecto**;
  bajo la delegación HITL del epic-005 (`execution.md`), la ejerce el **orquestador OpenCode**
  con la autoevaluación de `stage-2-specification.md §2.3`. El `sha256` del archivo materializado
  vive en el `state` (pin `contract_path` + `contract_sha256`), no dentro del archivo.
- **Pendiente de decisión:** las **D1–D8** (§7) y el **VERIFY 5 abierto** (§8).
