# Cierre de 005-013-unit-contract

**Feature:** `005-013-unit-contract` · **Epic:** `epic-005-real-operation` (fila 13 del plan) · **Cerrada:**
2026-10-14.

## Qué cerró

La fila 13 del plan del epic: **el hash identifica el contrato que recibió el agente y deja de bloquear
globalmente la planificación del proyecto.** El **contrato de una unidad** es una **proyección generada del
plan** —objetivo, alcance y aceptación de la unidad; las restricciones compartidas que le aplican; su
aprobación y versión de origen— **publicada una vez** junto al paquete y **pineada por su digest**; el sha del
plan queda como **procedencia**. Las **consecuencias dependen del tipo de cambio**: `current` (sin efecto),
`impact` (registro durable e idempotente; decide el orquestador) e `impeded` (**sólo** por autorización
retirada, con la salida nombrada). La **recepción y el resume** validan contra el contrato que el agente
efectivamente recibió, no contra el plan vivo. Sin documento nuevo y sin segunda copia: las reglas se
**referencian**.

## Evidencia de cierre

- **Contrato aprobado:** `spec.md` sha256 `4369822e…` y `plan.md` sha256 `89d5d8cf…`, aprobados juntos en una
  sola acción bajo la HITL delegada del epic, tras la corrección del draft pedida por la review del
  orquestador Claude (`review-claude-spec-2026-10-14.md`: B1.1..B1.4, B2 y P1).
- **Discovery:** `discovery.md` (mapeo con archivo:línea; el pin que bloqueaba es el **del paquete**, no el de
  la aprobación; 6 cambios de hash del plan en el epic).
- **TDD:** focales **T1 14 RED por aserción + 1 control → 15 verdes** (`9785423`/`021a491`), **T2 15 RED → 15
  verdes** (`c61db34`/`da3ced5`), **T3 docs-only** con comprobaciones observables (`b3cb88c`); regresiones
  declaradas por ficha **77 / 59 / 21 verdes**; review-fix de B1 con **3 casos nuevos** y el focal de T1 en
  **18 verdes** (`4bf688c`/`f41025f`); `tests/` sin tocar en los GREEN.
- **Review formal única (etapa 4):** **1 bloqueante / 5 opcionales / 1 abstención** (`review.md`), con
  reviewer de **familia distinta** a la del implementer y solo lectura. **B1** (`prepare` con `--out-dir`
  custom reescribía una proyección publicada y rompía el pin del paquete viejo, INV-3/PD-4) fue
  **reproducido y medido** por el reviewer (`2237d30d… → cec98be9…`) y **corregido ya** con escritura
  create-only que falla cerrada nombrando el paquete en conflicto; **O1** corregido como errata declarada en
  `t1-green.md`; **O2..O5** a deuda; la **abstención** (AC-9/T4) se resolvió corriendo T4.
- **Gate de aceptación (T4):** prueba decisiva con el **CLI real del repo** como subproceso sobre proyectos
  **descartables** en `<tmp>` con `HOME` del subproceso aislado (nunca este repo, nunca HOME), en las **tres
  formas de plan** (este epic; la plantilla del producto; un fixture sintético y anónimo con celda-enlace y
  sin historia ni autoridad). **AC-1..AC-9 verificados en las tres** (`acceptance.md`), incluidos los dos
  tramos: agregar una unidad futura independiente → `receive` rc=0 y veredicto `current`; el cambio relevante
  → `impact` con journal durable; la autorización editada → `impact` (nunca `impeded`); la autorización
  retirada → `impeded` rc=2 con la salida nombrada y, al registrarla, `prepare` rc=0 con línea base nueva.
- **Suite de cierre:** una vez, en un worktree fijado a `7ab16ba` (`closure-suite.md`): **960 passed / 4
  skipped, sin fallos**; `make validate` **155 PASS / 1 FAIL**, con el único fallo en **F011, preexistente**.
  Los dos FAIL que informó el implementer de T2 (drift de los agentes instalados y A3) **no aparecen** en el
  worktree de cierre: son del entorno del árbol de trabajo, como adjudicó la review.
- **Memory Bank:** aprobado con evidencia y commiteado (`docs(memory):`, `868d236`): entrada de
  `activeContext.md`, `progress.md` con la feature en `done`, y **ADR-028** (Confianza Media, con su motivo).
  La entrega del scribe **pasó por `receive` antes de cualquier transición** —la desviación que tuvo 005-011
  no se repitió—; llegó como **deltas con anclas** (declarado por el rol para no corromper los archivos
  completos) y el orquestador compuso los archivos aplicando esas inserciones de forma mecánica, con la
  cabecera y la cola de `activeContext.md` preservadas **byte a byte**.

## Deuda

Consolidada en `debt.md` con condición de cierre: **O2..O5** de la review, **D-1..D-3** de la spec §8, el
**acotamiento de la fila 13 (b)** (cambiar una restricción da `impact` y lo decide el orquestador), los
**datos para 005-012** (la ejecución huérfana que dejó `prepare --new-execution` después de `open-unit`; los
registros del state hechos con scripts del orquestador) y la **necesidad de desplegar** para que el generador
lea la declaración de anclas del activo instalado. **Ningún ítem bloqueaba el cierre.**

## Límites honestos (lo medido se dice como medido; lo inferido, como hipótesis)

- **Medido:** los focales y sus números, las regresiones declaradas, la prueba decisiva de T4 en las tres
  formas, la suite de cierre y `make validate`, la medición del reviewer de B1 (los dos digests), y las
  mediciones del discovery (plan 257 líneas / 31.396 B; fila 13 1.485 B; secciones compartidas 5.132 B;
  proyección estimada ≈ 6.617 B, ~21 % del plan).
- **Hipótesis (inferido, declarado):** las tres inferencias del focal de T2 que la spec no fija literalmente
  (`changed_parts` = `unit` / título de sección; el veredicto en stdout; el marcador `state incoherent`); el
  `mtime` como aproximación de la fecha de publicación (juzgado **nominal** por la review); la atribución de
  la diferencia de la suite (960 − 927 = 33 = 18 + 15) a los focales nuevos, consistente con la aritmética
  pero **no re-medida por separado**.
- **Desconocido (no se completa):** cuántas veces el pin bloqueó efectivamente una recepción en el epic (el
  state no lo registra de forma agregada); la operación exacta de reconciliación de un paquete `dispatched`
  (005-012); el comportamiento de la **versión instalada** una vez desplegada; el juicio de «restricción de
  aplicación inmediata» (es humano).
- **Fidelidad del informe del reviewer:** trae **segmentos corruptos por el modelo**; se materializó verbatim
  con un addendum del orquestador marcado como **no texto del rol** y no se reconstruyó ni se le atribuyó
  contenido.

## Estado del epic

`epic-005-real-operation` sigue en **`features-loop`**: **12/13 unidades cerradas** (filas 1..13; 12 features).
**005-013 queda `done`.** Queda en cola **`005-012-transition-registration`** (orden acordado **005-013 →
005-012**), **sin abrir**: el proyecto queda **en reposo** con la unidad abierta por el próximo ciclo. El
**despliegue** es del dueño (reservado). Sin push.
