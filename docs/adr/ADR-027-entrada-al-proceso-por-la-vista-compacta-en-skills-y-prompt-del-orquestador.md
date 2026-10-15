# ADR-027: La entrada al proceso es la vista compacta `status` —en las skills y en el prompt del agente orquestador— y el state completo es ampliación condicional

- **Status**: Proposed
- **Date**: 2026-10-14
- **Deciders**: orquestador OpenCode (HITL delegada epic-005) + architect (spec/plan) + orquestador Claude (revisión de la spec, T2b, aceptación T4 y decisión del gate)
- **Confidence**: Media
- **Aprobación**: orquestador OpenCode bajo la delegación HITL del epic-005
  (`docs/epics/epic-005-real-operation/execution.md`), con evidencia (spec `a6d05d9d…` con la enmienda 4, review
  formal 0 bloqueantes, aceptación T4 con AC-7 cumplido y AC-6 parcial declarado, suite de cierre 927 passed en
  `8ec574d`). **La confianza es Media** porque AC-7 está **medido y cumplido** en Claude Code mientras AC-6
  (OpenCode) quedó **cumplido en parte y declarado así** (el orden estricto «`status` antes del state» no se
  logra), la evidencia es **una sola sonda por variante** (indicativa, no estadística) y **RD-a** sigue abierta
  (tras un despliegue, la primera sesión de cada proyecto puede arrancar con el derivado viejo).

## Contexto y problema

El gasto previo al primer despacho estaba **medido y atribuido a la entrada al proceso**
(`docs/specs/005-007-progressive-planning/acceptance.md` §7: 70 llamadas previas, 304.054 caracteres, despacho
en la llamada 71): llamadas 1–2 las skills, llamada 3 el **state completo** antes de cualquier operación del
CLI, llamadas 4–19 exploración manual, llamada 20 `status --project-root .` **rechazado** por
`cdad_packet.py` (mientras `cdad_continuity.py` sí resolvía la raíz relativa) y llamadas 22–30 investigando
versiones y manifiestos **guiadas por un `DRIFT` sin acción concreta**. La ruta compacta ya existía (005-003)
pero **competía** con el Step 1 que mandaba leer el state. ¿Cómo hacer que una sesión nueva de **cualquiera** de
los dos runtimes entre por una ruta breve y común, **sin** prohibir la lectura del state y **sin** crear una
segunda copia de la regla?

## Opciones consideradas

### Opción A: la vista primero en los textos que ya existen (las dos skills **y** el prompt del orquestador), por referencia

- Pros: corrige la causa raíz medida; cubre el **texto común** entre runtimes (las `SKILL.md`) **y** el texto
  que realmente manda en OpenCode (el prompt del agente derivado); no crea documento ni segunda copia; el state
  queda como ampliación condicional con motivo registrado.
- Contras: toca prosa **vigilada por ventana** (guardas de 005-006/005-010); exige regenerar derivados y, tras
  un despliegue, la primera sesión de cada proyecto puede seguir usando el derivado viejo (**RD-a**); el orden
  estricto no se logra en OpenCode (AC-6 parcial).

### Opción B: una referencia «common entry» nueva, referenciada por las skills

- Pros: un solo lugar que mantener.
- Contras: **no** corrige la causa (el Step 1 seguiría mandando leer el state), **duplica** una regla que ya
  tiene dueño (`orientation.md` §1, `project-start.md` §11) y agrega mantenimiento documental. **Rechazada**
  (fuente única, INV-2/PD-6).

### Opción C: tocar solo el agente orquestador

- Pros: es la entrada real de OpenCode.
- Contras: no es el texto común entre runtimes; el lado Claude Code seguiría entrando por el state. **Rechazada**
  como única palanca; se adoptó **además** de (A), como T2b.

### Opción D: prohibir la lectura del state en la entrada

- Pros: el orden se cumpliría por prohibición.
- Contras: prohibir la ampliación legítima es más frágil que ordenarla, y el texto se leería como «no leer el
  state» (riesgo R3 de la spec). **Rechazada.**

## Decision

La **entrada al proceso es la vista compacta read-only `status`**, como **primera acción** de una sesión nueva,
**antes** de leer el state o explorar:

- **(a) en las skills:** el **Step 1** de `cdad-cycle` y `cdad-epic` consulta **primero** la vista;
  `state-detection.md` y la documentación extensa pasan a **ampliación condicional con gatillo** (una necesidad
  concreta que afecte al siguiente despacho, con el motivo registrado) y `orientation.md` queda **indexado** en
  la tabla de referencias.
- **(b) en el prompt del agente orquestador** (`sources/roles/orchestrator.md` y sus derivados): la primera
  acción de toda sesión es la vista `status`; `resume` **deja de ser** «the first step of every new session» y
  pasa a ser el paso **siguiente**, solo con una ejecución activa; el state completo es ampliación condicional.

La **regla no se copia: se referencia** a sus dueños (`orientation.md` §1 + `project-start.md` §11). La vista es
el **contrato de orientación** (proyección acotada, determinista y read-only) y el **state es ampliación
condicional**. Como parte del mismo contrato de entrada: `status` acepta **raíz relativa** (`--project-root .`)
como los demás CLI; ante `DRIFT` **nombra la pata que diverge y afirma su resolución solo cuando es la
verificada** (`project` → el próximo `prepare` republica los derivados del proyecto), **sin** confundir ausencia
con incoherencia; y con un paquete `prepared` la ruta nombra la **acción natural (despacharlo)**.

## Reasons

1. La causa medida era el **texto** de la entrada, no la falta de instrumentos: la vista compacta ya existía
   (005-003) y **competía** con el Step 1 que mandaba leer el state.
2. En OpenCode el texto que manda es el **prompt del agente derivado**, no la skill (medido: AC-6 falló con la
   corrección de las skills ya desplegada); en Claude Code la skill se carga primero. La palanca tiene que cubrir
   **las dos superficies**.
3. **Referenciar** en vez de copiar mantiene la fuente única de la regla (`orientation.md` §1,
   `project-start.md` §11) y no agrega mantenimiento documental.
4. La **ampliación condicional** (en vez de prohibición) conserva la lectura del state ante una necesidad
   concreta con motivo registrado; las guardas por ventana (`resume` sin ejecución activa, fila
   `project-start.md`) se conservan y quedan verdes.
5. Un `DRIFT` **sin acción concreta** es lo que empuja la investigación de versiones y manifiestos: afirmar
   **solo** lo verificado lo corta sin inventar.

## Consequences

**Positivas:**

- **Claude Code (AC-7, medido):** `status` es la primera acción; el primer `Agent` baja de la llamada **23 a la
  14** y la salida previa de **105 mil a 54 mil caracteres (−49 %)**.
- **OpenCode (AC-6, medido y declarado parcial):** la skill se carga en la llamada 1 y `status` en la llamada
  **3** (antes, 21); el primer despacho baja de la llamada **71 a la 59 (−17 %)** y el tiempo de 5,8 a 4,7 min
  (−20 %).
- `status --project-root .` deja de ser un callejón sin salida, y la vista da la acción siguiente ante un
  `DRIFT` legítimo y ante un paquete `prepared`.

**Negativas / trade-offs:**

- **Brecha declarada de AC-6:** no se cumple el orden estricto «`status` antes del state completo» — el modelo
  lee el state completo en la llamada 2 (53 mil caracteres) —la causa de ese orden no está demostrada—, y el costo lo pone el **tamaño del
  state** (~490 KB, mayormente historia): deuda estructural **RD-b** (compactar el state), con condición de
  cierre.
- **RD-a:** tras un despliegue, la primera sesión de cada proyecto puede arrancar con el **orquestador derivado
  viejo**; el `DRIFT` de la pata `project` lo anuncia, pero la entrada ya ocurrió antes del `prepare` que lo
  resuelve.
- La prosa de la entrada está **vigilada por ventana**: dos «first» compitiendo en el Step 1 fue un hallazgo
  real de la review (**OP-2**), corregido antes del despliegue.
- La evidencia es **una sola sonda por variante** (indicativa, no estadística); las líneas base se usan como
  **orientación, no umbral**. **No** se prometen ahorros fuera de lo medido.

**Neutrales:**

- La doctrina «cada CLI resuelve su propia raíz» se conserva; el comportamiento **C4** de 005-003 queda
  **superseded** por la fila 11, con sus **dos oráculos declarados** (uno reemplazado; el otro con el fixture de
  fallo corregido y su oráculo de captura del `rc` conservado).
- Sin documento nuevo, sin segunda copia y sin campo nuevo en el estado.

## Notas

- Contrato normativo: `docs/specs/005-011-common-entry/spec.md` (`a6d05d9d…`; §2.1–§2.3, PD-1..PD-6,
  INV-1..INV-8, con la **enmienda 4**) y `plan.md` (fichas T1, T2, T2b, T3, T4); contrato de la **fila 11** del
  plan del epic (`docs/epics/epic-005-real-operation/plan.md:44`).
- Evidencia: `docs/specs/005-011-common-entry/acceptance.md` (T4 y decisión del gate), `closure-suite.md`
  (927 passed / 4 skipped en `8ec574d`; `make validate` 155 PASS / 1 FAIL, F011 preexistente), `review.md`
  (0 bloqueantes / 5 opcionales / 2 abstenciones), `debt.md` (OP-3..OP-5, RD-a, RD-b). Commits de producto:
  `53413b3` (T1), `13c68b9` (T2), `68044cb` (T2b), `860a611` (T3); corrección de OP-1/OP-2 `362ce3a`.
- Análogo a **ADR-021** (arranque guiado por referencia) y **ADR-025** (la orientación es una proyección
  read-only): ADR-025 decide **qué** se sirve como orientación; este ADR decide **cuándo** se entra por ella y
  **en qué superficies**. Frontera con ADR-019/ADR-020 (aprobación por rol, política de evidencia).
- **Por qué una sola decisión arquitectónica:** (b) raíz relativa y (c) textos de la vista son correcciones de
  contrato declaradas (D-2/D-3/D-4 de la spec), no arquitectura nueva; el único cambio de arquitectura es **cuál
  es la entrada al proceso y en qué superficies vive**.
- **Límite honesto:** AC-6 es **parcial y declarado** (una sonda por variante); el lado Claude Code se midió con
  **conteo propio** sobre el transcript (sin adaptador CC del medidor; D-3/D-4 de 005-004).
