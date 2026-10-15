# ADR-026: Los roles CDAD se activan en Claude Code por el mecanismo nativo (`Agent`/`subagent_type`), con paquete, I8, `receive` y `reconcile` reusados y el mapa de hooks declarado en su dueño

- **Status**: Proposed
- **Date**: 2026-10-13
- **Deciders**: architect (propuesta) + orquestador OpenCode (HITL delegada epic-005)
- **Confidence**: Media-Alta
- **Aprobación**: orquestador OpenCode bajo la delegación HITL del epic-005
  (`docs/epics/epic-005-real-operation/execution.md`), con evidencia (spec aprobada `5e11f2ef…` y plan `953e4ba5…`
  re-aprobados con las dos enmiendas del orquestador Claude, recorrido real T5 paso a aprobado, review formal
  0 bloqueantes). El architect no aprueba su propia propuesta. **La confianza es Media-Alta porque el paso b
  (confirmación con el CLI instalado) está BLOQUEADO** hasta el despliegue del dueño, y porque el diseño de
  activación comparte el marcador de versión de la raíz con las patas de OpenCode (deuda RD-3).

## Contexto y problema

La fila 10 del plan del epic-005 (`docs/epics/epic-005-real-operation/plan.md:43`) pide **roles CDAD activos en
Claude Code para este proyecto**, sin tocar HOME salvo decisión del dueño, y **un ciclo corto real despachado desde
Claude Code con la versión instalada al empezar**. El discovery dejó tres enunciados del propio producto que **no
eran ciertos** y que un coordinador de Claude Code leería como fuente: la herramienta de despacho declarada por el
adaptador y los derivados (`Task`) no era la que usan los transcripts reales (`Agent`); el adaptador afirmaba que
«the installer STRIPS the model field at install time» cuando el instalador **no transforma** nada; y el
comprobador de versión tenía patas project/agents/CLI donde la pata «agents» resolvía el manifiesto derivado de
**OpenCode**, sin pata para los agentes de Claude Code. Además, bajo el perfil vigente `basic` los agentes no
llevan `model:` y la invariante reviewer≠implementer **no** la garantiza el instalador (la exención vivía solo en
el guard y en ADR-007).

El problema arquitectónico: **cómo** dejar los roles activos y verificables en Claude Code **sin** construir un
runtime paralelo (adaptador, state, ledger, scheduler o UI nuevos) y **sin** tocar HOME, resolviendo a la vez la
coherencia de los enunciados que un consumidor de Claude Code lee.

## Opciones consideradas

### Opción A: adaptador Claude Code (transporte, señal durable y fin de corrida propios)

- Pros: paridad de flujo con la delegación externa de OpenCode.
- Contras: la señal durable candidata (transcript JSONL) **no está verificada en el hecho de fin** ⇒ debería fallar
  cerrado; la identidad del rol a verificar **sin** fallback; `--session-id` exige UUID; el transporte por `stdin`
  en modo no interactivo y los hooks en modo no interactivo **no están verificados**;
  `--permission-mode`/`--dangerously-skip-permissions` **no son sandbox**. Introduce un segundo camino de recepción
  sin necesidad para el resultado de la fila 10. **Descartada como alcance**: queda **incremento nombrado** con sus
  deltas (spec §8 D-3).

### Opción B: artefactos de proyecto para Claude Code (activación por proyecto / copias bajo el proyecto)

- Pros: aislaría la versión por proyecto.
- Contras: `cdad-activate.py --runtime claude-code` existe, pero emite copias de proyecto y `.cdad/activation.json`,
  y **«copias viejas» es reserva explícita del dueño**; la guía vigente pide no introducir activación solo para
  resolver derivados. **Descartada**: queda como **decisión del dueño** (BLOQUEO si se pide).

### Opción C: mecanismo nativo + correcciones de enunciado y verificación mínima (ELEGIDA)

- Pros: es lo que responde a la letra de la fila 10 («despachado **desde** Claude Code», roles activos **en**
  Claude Code **para este proyecto**); ya hay agentes `cdad-*` instalados y llamadas nativas históricas; **reusa**
  paquete, I8, `receive`, `materialize`, `reconcile` y la vista compacta; sin infraestructura nueva.
- Contras: la verificación del guard cubre las **decisiones** del guard, no que Claude Code honre `exit 2` ni que
  los hooks del frontmatter se apliquen a subagentes nativos (quedan `unknown` con causa); la recepción del
  recorrido **no es de intervención cero** (descriptor a mano); el mapa de hooks queda declarado en **dos
  superficies máster** con coherencia test-cerrada.

## Decisión

1. **La activación de los roles CDAD en Claude Code es por el mecanismo nativo:** los agentes `cdad-*` instalados
   se invocan como **subagentes nativos** con la herramienta **`Agent`** y `subagent_type: cdad-<rol>`; el trabajo
   del rol corre **en Claude Code**. Se **reusan** el paquete, el registro I8, `receive`, `materialize`, `reconcile`
   y la vista compacta; **no** hay adaptador CC, state/ledger nuevo, scheduler ni UI.
2. **La herramienta de despacho declarada es la real observada (`Agent`)**, declarada **una vez** en el generador
   de agentes y enunciada por el adaptador fuente; los derivados la llevan y el validador del repo **falla** si
   algún agente CC declara `Task` como herramienta de despacho. El lado **OpenCode conserva** su nombre. Es
   **corrección de texto y de verificación**, no de arquitectura.
3. **El enunciado del instalador se corrige, no el instalador:** el instalador **despliega los bytes staged sin
   transformarlos** (`cp -p`) y la ausencia de la línea `model:` bajo `basic` la produce el **generador** (perfil ⇒
   `cdad_model_claude` vacío ⇒ línea omitida). La verificación es en **raíz aislada** (`CDAD_INSTALL_ROOT`, nunca
   HOME), con control positivo de perfil y control del caso `basic`.
4. **El chequeo de versión gana una pata Claude Code declarada y aditiva:** lee el marcador de la raíz de
   instalación **detrás de los agentes CC** (registro de activación si existe; si no, el directorio global de
   agentes del runtime), **participa en el veredicto solo cuando una instalación CC es detectable**, **nunca** cruza
   una frontera de instalación, **nunca** lee el manifiesto derivado de OpenCode para inferir el lado CC, y **no
   altera** los cuatro veredictos ni el `rc` existentes. Una marca faltante es `unknown` **con causa**, nunca `0`
   ni una versión prestada.
5. **El mapa de hooks de CC se declara una sola vez en su dueño** (adaptador fuente + `CC_GUARDS` del generador) y
   el consumidor lo **referencia**; las **decisiones del guard** por rol se verifican **sin una sesión CC viva**,
   alimentando cargas PreToolUse sintéticas sobre un proyecto fixture. **Declarado:** eso verifica las decisiones
   del guard, **no** que Claude Code honre `exit 2` ni que los hooks del frontmatter se apliquen a los subagentes
   nativos. No se habilita ningún hook `Bash`.
6. **Procedencia de modelo bajo el perfil vigente:** bajo `basic` no hay modelo por rol, así que el modelo del
   despacho crítico se **declara por llamada** y el despacho registra `model_configured`/`model_reported` con
   `provenance` (`null`/`unknown` **con causa** cuando no se observó); la invariante reviewer≠implementer **no** se
   presenta como garantizada por el instalador y su exención es **explícita y visible** (ADR-007;
   `scripts/validate-subagents.sh`, por referencia).
7. **Frontera y reservas:** el recorrido corre desde un **directorio ya confiable** con `--project-root` explícito;
   **no** se escribe en HOME y los **cuatro cruces reservados al dueño** (confiar la carpeta de este proyecto,
   copias/despliegue en HOME, emitir la activación de proyecto para CC, activar versiones en el repo real) quedan
   **BLOQUEO declarado**, nunca verdes por proximidad. Quedan **fuera**: el adaptador CC (incremento nombrado), el
   **registro automático de transiciones** (unidad 005-012) y la **medición de contexto del lado CC** (no hay
   adaptador CC del medidor).

## Reasons

1. Es lo que responde a la letra del resultado buscado: el ciclo se **despacha desde** Claude Code y los roles
   quedan activos **en** Claude Code para el proyecto, con los agentes ya instalados.
2. **No se construye un runtime paralelo.** Reusar paquete, I8, `receive`, `materialize`, `reconcile` y la vista
   compacta mantiene una sola fuente de recepción y de transición del state (escritor único = coordinador), en
   lugar de un segundo camino que habría que reconciliar.
3. Los tres enunciados falsos **se corrigen en su dueño** en vez de compensarlos con código: declarar la
   herramienta real, describir el mecanismo real del instalador y dar al comprobador de versión una pata propia
   evita que un consumidor de Claude Code opere con una imagen errónea del sistema.
4. La extensión del comprobador es **aditiva y declarada** porque su regresión (sin agentes CC, veredicto y `rc`
   idénticos) es verificable; un quinto veredicto o un cambio de los existentes habría reabierto el contrato de
   005-005.
5. La verificación del guard **sin sesión viva** es posible porque el guard es un programa autónomo que lee JSON
   por `stdin` y exporta sus decisiones por `rc`; el patrón de prueba ya existía.
6. La honestidad de la frontera (HOME intacto, cruces del dueño como BLOQUEO, desconocidos con causa) es parte de
   la decisión: la feature **no** promete lo que no puede observar.

## Consequences

**Positivas:**

- Un ciclo corto real de CDAD corre **desde una sesión de Claude Code** de punta a punta con la versión instalada
  al empezar, con evidencia durable (I8 `runtime: claude-code`, recibo `pending`, `reconcile: received`) y con el
  coordinador como escritor único del state.
- Los agentes de Claude Code declaran la herramienta que realmente usan, y el validador del repo impide que vuelva
  la declaración errónea.
- El chequeo de versión informa el lado Claude Code **sin** confundir perfil con versión y **sin** reabrir el
  contrato de 005-005; una instalación CC ausente no aporta un veredicto favorable.
- Las decisiones del guard por rol se pueden **ejecutar** en la suite, sin una sesión de Claude Code viva.

**Negativas / trade-offs:**

- El mapa de hooks queda en **dos superficies máster editables** (tabla del adaptador + `CC_GUARDS`): es la tensión
  más directa con la fuente única (PD-9). El drift **no** queda silencioso —lo persigue una aserción bidireccional
  del focal congelado—, pero reducirlo a una sola fuente exige **enmienda de contrato** (deuda RD-1).
- La pata CC **comparte el marcador de la raíz** con las patas de OpenCode (el instalador instala los dos runtimes
  juntos): no detecta agentes CC con otra versión **dentro de una misma raíz** (deuda RD-3; hoy ese escenario no
  existe en ninguna instalación declarada).
- La verificación del guard cubre **decisiones**, no la aplicación efectiva en Claude Code; `exit 2` en modo no
  interactivo, la aplicación de los hooks del frontmatter a subagentes nativos y la herencia de modelo quedan
  `unknown` **con causa**.
- La recepción del recorrido **no es de intervención cero** (buzón y descriptor `staged-file` escritos a mano; la
  transición del state, a mano): es deuda declarada, con la unidad **005-012** como cierre.
- El paquete viaja **tipeado en el prompt de `Agent`** y pierde el salto de línea final: la integridad del
  transporte depende del coordinador (deuda F-7).

**Neutrales:**

- El **paso b** (confirmación con el CLI instalado) queda **BLOQUEADO** hasta el despliegue del dueño; **no** es
  gate de cierre.
- El **despliegue** de la versión nueva y la limpieza de copias viejas de HOME siguen siendo del dueño (spec §8 D-1).
- El `README.md` sigue sin mencionar la instalación de Claude Code: **ausencia declarada**, no coherencia (spec §8 D-5).

## Notas

- Contrato normativo: `docs/specs/005-004-claude-code-roles/spec.md` (PD-1..PD-11, INV-1..INV-8, D-1..D-12;
  `5e11f2ef…`) y `plan.md` (T1..T5, bloque `plan-tasks`; `953e4ba5…`), aprobados el 2026-10-13 por el orquestador
  OpenCode bajo la HITL delegada del epic-005, con las dos enmiendas del orquestador Claude (alcance del focal de
  T4; coordinador del recorrido y paso a/paso b).
- Evidencia del recorrido: `docs/specs/005-004-claude-code-roles/t5-acceptance.md` (11 pasos, fricciones F-1..F-7,
  frontera de HOME, desconocidos); revisión del gate y medición propia del orquestador Claude en su §7. Review
  formal: `review.md` (0 bloqueantes / 3 opcionales / 2 abstenciones). Suite de cierre: `closure-suite.md`.
  Commits: T1 `34703b6`/`cc6e5a5`, T2 `0964694`/`96786de`, T3 `4828c0c`/`b05c5c1`, T4 `0cdec77`/`65a0de9`;
  recorrido `c8ab21f`; corrección de la regresión `5d6f667`; evidencia de la suite `9980829`.
- Fronteras: **ADR-008** (Claude Code como segundo runtime y delegación por `Agent`; aquí se registra el **diseño de
  activación** de los roles, no el arreglo del nombre de la herramienta), **ADR-007** (perfiles de modelos y
  exención de `basic`), **ADR-009** (allowlists; el lado OpenCode conserva su vocabulario), **ADR-020/005-005**
  (procedencia declarada; la pata CC es aditiva y no reabre su contrato), **ADR-023/005-009/005-010** (interfaz de
  delegación; el adaptador CC queda incremento nombrado), **ADR-024** (instrumento read-only no-gate) y **ADR-025**
  (proyección read-only; la vista compacta que el recorrido usa para orientarse).
- **Deuda asociada:** `docs/specs/005-004-claude-code-roles/debt.md` (RD-1..RD-6, con condición de cierre) y las
  fricciones F-3/F-5/F-7 de `t5-acceptance.md` §7; la deuda de proceso de `closure-suite.md` (regresiones de una
  tarea que edita un reference; fijar el perfil de staging en el procedimiento de cierre); y la deuda de la spec
  §8 D-1..D-7.
- **Límite honesto:** el **paso b de PD-6** está **BLOQUEADO** hasta el despliegue del dueño y los cuatro
  desconocidos de PD-8 se conservan `unknown` con causa; la aceptación **no** se declara por proximidad y **no** se
  prometen cifras de ahorro.
