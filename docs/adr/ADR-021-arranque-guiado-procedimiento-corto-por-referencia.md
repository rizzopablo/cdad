# ADR-021 — El arranque desde reposo se resuelve con un procedimiento corto que compone por referencia, una entrada de intake y un dueño canónico por objeto de reconocimiento

* Estado: **Aceptado** (2026-10-10; orquestador bajo delegación HITL de epic-005)
* Fecha: 2026-10-10
* Decisores: orquestador bajo delegación HITL de epic-005 (aprobación del dueño, `execution.md`)
* Confianza: **Media-Alta**

## Contexto y enunciado del problema

005-006 cierra la fricción del arranque: **una instrucción breve debe bastar para llegar a una
primera delegación útil**. El primer intento real (evidencia `005-006-attempt-1.md`) mostró que
no bastaba, por cinco defectos del producto: (1) el intake del orquestador solo nombraba
`cdad-cycle` como camino *legacy, SECOND*, ambiguo desde reposo; (2) el cableado escribía rutas
del CLI **relativas al proyecto consumidor**, que no existen fuera de este repo; (4) se
prescribía `resume` sin distinguir «arrancar» de «reanudar una ejecución activa»; (5) un cambio
de plan aprobado no se reflejaba en `epic_features` y nadie tenía asignada la sincronización; y
(6) el procedimiento de arranque no existía en un lugar corto: había que deducirlo de cinco
referencias largas, y **tres «inicializaciones» distintas** (Memory Bank, ejecución v2,
adopción por runtime) convivían sin desambiguar.

Las decisiones con consecuencias arquitectónicas son cuatro:

1. **Dónde vive el arranque.** No existía dueño: el conocimiento estaba repartido entre el
   intake, `state-detection`, `project-execution`, `continuity` y `bootstrap`.
2. **Cómo se evita duplicar reglas.** Un procedimiento nuevo podía degenerar en una segunda
   definición del algoritmo de detección o del texto de política/autoridad.
3. **Quién es dueño del reconocimiento.** `state-detection` está duplicado entre `cdad-cycle`
   y `cdad-epic`, y ambos detectan **objetos distintos** (feature/Memory-Bank vs etapa de epic).
4. **Quién sincroniza `epic_features`.** El enforcement existe en el CLI
   (`cdad_packet.py:549-554`: la feature debe figurar exactamente una vez y no estar cerrada),
   pero el procedimiento no asignaba responsable: un cambio de plan aprobado dejaba el state
   desincronizado y el arranque fallaba cerrado sin decir quién debía repararlo.

## Decisión

1. **Un procedimiento corto y único es la entrada del arranque desde reposo.**
   `skills/cdad-cycle/references/project-start.md` es el dueño del paso a paso: reconoce la raíz
   (el **directorio de sesión es pista, no norma**; sin búsqueda global), clasifica
   nuevo/parcialmente inicializado/configuración incompleta, registra cada restricción en su
   lugar canónico y **encadena hasta el primer encargo preparado**.
2. **Compone por referencia, nunca copiando (INV-1).** El procedimiento referencia
   `state-detection`, `project-execution`, `continuity`, `bootstrap` y
   `cdad-epic/state-detection`; no reproduce el algoritmo de detección ni el texto de
   política/autoridad. La no-duplicación es una postcondición verificada por test estructural.
3. **El intake gana una entrada *boot-at-rest*.** `sources/roles/orchestrator.md` ordena
   **cargar la metodología primero** ante una instrucción breve sin ejecución preparada y señala
   el procedimiento; «legacy, SECOND» deja de ser la única vía. Los agentes publicados son
   **byte-parity** de la fuente (salidas declaradas del generador, nunca editadas a mano).
4. **Dueño canónico del reconocimiento, por objeto.** Feature/Memory-Bank →
   `cdad-cycle/references/state-detection.md`; etapa de epic (vocabulario `epic_stage`) →
   `cdad-epic/references/state-detection.md`; la **composición de arranque** →
   `project-start.md`, que **referencia** a ambos y no re-declara ninguno.
5. **`resume` solo con ejecución activa.** La rama de arranque enuncia «sin ejecución activa →
   no `resume`». La **reducción** de lecturas y la selección fina del camino de continuación
   quedan en 005-003 (frontera explícita).
6. **El cableado usa el CLI instalado** (`$CDAD_INSTALL_ROOT/…`) y **reusa la procedencia que
   fijó 005-005** (ADR-020) sin re-declarar su precedencia.
7. **`epic_features` se sincroniza al aplicar un cambio de plan aprobado.** El responsable es el
   **coordinador de epic**; el **escritor único del state sigue siendo el orquestador** (INV-3).
   Ante un desfase, el arranque **nombra faltantes/sobrantes** y **encamina** la sincronización a
   `cdad-epic`, sin inventar features ni bloquearse en silencio. El enforcement del CLI **no**
   cambia.

## Consecuencias

* **Positivas.** El arranque es una sola lectura corta; las reglas siguen teniendo un único
  dueño; el reconocimiento queda desambiguado por objeto sin fusionar dos detectores que miran
  cosas distintas; y un cambio de plan aprobado tiene responsable explícito de sincronización.
* **Negativas / costos.** Hay más punteros que mantener coherentes (procedimiento + intake +
  tabla de referencias + README); el texto pasa a depender de `$CDAD_INSTALL_ROOT`; y el
  **doble bootstrap** (Memory Bank vs ejecución v2) sigue siendo **dos procedimientos
  distintos** que el arranque **encadena**, no fusiona.
* **Riesgo aceptado.** El procedimiento puede degenerar en copia: se mitiga con el test
  estructural de no-duplicación (INV-1).
* **Sin cambios de producto en el CLI.** `cdad_packet.py` y `prepare` no cambian: el enforcement
  de `epic_features` se preserva como lock verde.
* **Límite de aceptación.** La aceptación real (arranque de un proyecto existente parcialmente
  inicializado elegido por el dueño) **no** es automatizable: es un gate de integración
  orquestador + dueño, y requiere la activación de la versión nueva en HOME (reservada al dueño).

## Alternativas consideradas

* **Fusionar los dos `state-detection.md` en uno.** Rechazada: detectan objetos distintos y la
  fusión arriesgaba el vocabulario de `epic_stage`.
* **Solo un procedimiento nuevo, sin entrada en el intake.** Rechazada: la referencia sola no se
  carga por iniciativa propia (fricción 1).
* **Solo la entrada de intake, sin procedimiento.** Rechazada: obliga a seguir deduciendo el
  arranque de cinco referencias largas (fricción 6).
* **Trasladar el prompt largo a una plantilla.** Prohibida por el plan: la solución es un
  procedimiento operativo corto (INV-6).

## Enmienda por decisión del dueño (2026-10-10)

El marcador de la ruta del CLI que esta ADR describe originalmente como
`$CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/…` quedó **superado**: esa variable es de
**instalación** y no existe en runtime (con una instalación global resuelve a `~/skills/cdad-cycle`,
que no existe). El marcador vigente es **`<skill-dir>`**: el directorio de la skill cargada, que el
runtime informa al cargarla. La decisión y su verificación están en
`docs/specs/005-006-guided-project-start/closure.md` §8 (review-fix del dueño). La spec aprobada
(PD-10/§6) conserva su sha como pin vigente; se lee con esta nota.

## Referencias

* Contrato: `docs/specs/005-006-guided-project-start/spec.md` (PD-1..PD-17, INV-1..INV-8; D1–D8)
  y `plan.md` (T1–T5).
* Insumo: `docs/epics/epic-005-real-operation/evidence/005-006-attempt-1.md` y
  `findings/session-guided-start-friction-2026-10-10.md`.
* Revisión: `docs/specs/005-006-guided-project-start/review.md` (0 bloqueantes).
* Fronteras: `plan.md:35` (005-006 arranque; 005-003 orientación al retomar; procedimiento de
  reconocimiento compartido) y `plan.md:36` (005-002 mide; 005-006 no fija presupuestos).
