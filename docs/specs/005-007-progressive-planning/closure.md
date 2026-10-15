# Cierre — 005-007-progressive-planning

Fecha: 2026-10-13. Epic: `epic-005-real-operation` (fila 9). Ejecución: `exec-005-007-progressive-planning-001`.
Contrato aprobado: `spec.md` (`54877103…`) y `plan.md` (`1f636260…`), con el delta del dueño
`draft-inputs-2026-10-13.md` y la revisión entre tramos `review-claude-spec-2026-10-13.md`.

## Resultado

La feature convierte un objetivo amplio en **el próximo trabajo ejecutable con contexto suficiente**: la
**regla de detalle progresivo** (marcador cerrado `detail` `"next"`/`"planned"`, con `objective`, `depends_on`,
`uncertainty`, `owner` y `resolves_when` para la planificada, sin plan de validación por tarea) vive **una sola
vez** en `stage-2-specification.md` y el validador la acepta sin debilitar el fallo cerrado; el **tamaño de unidad
por costo total** y el **replanteo de la unidad** ante un reintento sin información nueva están declarados en sus
fuentes canónicas (`stage-2-specification.md`, `re-entry.md`); las **plantillas** parten del recorrido de uso
(plantilla de plan de feature nueva, validada por el producto); y los **tres puntos del delta** quedaron cubiertos:
`open-unit` abre la unidad siguiente **sin editar el state a mano** (1 operación del CLI, 0 ediciones manuales),
el **informe del architect** se materializa por el camino legítimo (`role-report` admitido en la tabla cerrada) y
el **medidor** reconoce el despacho por la interfaz común por hecho material (invocación real, incluidas las
envueltas tras el review-fix).

## Gates con números

- **Etapa 3 (T1..T7):** 7 oráculos congelados, **37 passed** en la corrida del orquestador; cada unidad con su RED
  por `AssertionError` (commits `16a89ad`, `07abeb2`, `47cd7cc`, `852d3be`, `b3044b1`, `95516ef`, `4462a9a`) y su
  GREEN por el implementer (`7ff19c1`, `09567cd`, `54eeed6`, `512d913`, `8ac41d6`, `594da73`, `a59101d`), más las
  regresiones de área registradas por unidad.
- **Gate T8 (`acceptance.md`):** AC-1..AC-6 verificados; AC-7 medido con el artefacto del repo (apertura: 1
  operación del CLI vs 3 escrituras manuales + lectura completa de 397 KB antes; cierre: 19 operaciones de estado
  → deuda D-3) y la parte **desplegada en BLOQUEO declarado** (acción del dueño); AC-8: suite completa **una vez**
  en worktree fijado a `a5cd0c8` = **871 passed / 9 skipped / 4 failed + 6 errors**, idénticos al commit base
  `99e2f2e` (pre-existentes, verificados); `make validate` **141 PASS / 2 FAIL** (F011 preexistente).
  > **Conclusión vigente (2026-10-13, verificación del orquestador Claude):** los 4 failed + 6 errors
  > se deben a que el worktree de cierre no corrió `make staging`; no provienen de la instalación de
  > HOME ni de F011. Con `make staging` la suite da **887 passed / 1 failed / 4 skipped**, y el único
  > fallo es la cota de 2 s del doble de OpenCode (inestabilidad conocida; aislado pasa 3 de 3). La
  > conclusión «sin regresiones» se mantiene; solo cambia la causa
  > (`review-claude-spec-2026-10-13.md`, «Verificación del cierre»).
- **Review formal:** **2 blocking / 4 optional / 2 abstenciones**. B1 (`depends_on` exigido a la tarea `planned`)
  y B2 (falso negativo del medidor ante invocaciones envueltas) **corregidos ya** (testfix `e3375e4`, fixes
  `a86278e` y `282c70a`; 24 passed de verificación). O1..O4 y las abstenciones **a deuda** (`debt.md`).

## Incidentes y datos del proceso (declarados)

- **Timeout** de un despacho del RED de review-fix (cota 1800s): sin entrega, `reconcile` = `dispatched-unknown`,
  verificación de ausencia de efectos y **reintento con cota mayor** (3000s) que sí entregó.
- **Tres defectos de oráculo** detectados por el gate del orquestador (fixture de T2 que no omitía el campo; helper
  de T5 que recibía el documento; la bandera `--delegation-dispatch` fijada por el oráculo y no nombrada en la
  spec) → deuda D-8.
- **Contradicción de alcance** en el encargo de B1 (mi encargo ampliaba B1 a todas las tareas contra PD-2/INV-5): el
  implementer la probó con evidencia y **no rompió un oráculo congelado**; se adjudicó acotando el fix al alcance de
  la review, sin cambiar el contrato aprobado.

## Deuda y bloqueo que la feature deja

`docs/specs/005-007-progressive-planning/debt.md`: D-1 (medición desplegada — **BLOQUEO del dueño**), D-2 (envolturas
ya corregidas; queda el refuerzo por ledger), D-3 (cierre aún manual), D-4 (draft de una sola parte por la interfaz),
D-5..D-7 (heredadas/citadas), D-8 (proceso de oráculos). Pre-existencias declaradas: F011 en `make validate` y los
4+6 casos de la suite idénticos al base.

## Estado final

Feature **cerrada** en el estado (`epic_features: done`, `closed_at: 2026-10-13`, evidencia este archivo).
Memory Bank actualizado (borradores del scribe aprobados por el orquestador bajo la HITL delegada del epic-005).
Sin push, sin despliegue, sin tocar HOME. El epic vuelve al bucle de features: siguiente en el plan,
`005-004-claude-code-roles`; la recomendación al dueño es **desplegar** antes de la aceptación de uso de esta
feature (D-1) y de la confirmación del consumidor.

## Despliegue (2026-10-13)

El dueño autorizó desplegar con el otro proyecto activo en reposo («Está en reposo, despliega»).
`.cdad/local/deploy-005-003-home.sh 9d89a4b` instaló el HEAD que incluye 005-007, y
`<home>/version.txt` quedó en `9d89a4b…`. El chequeo dio DRIFT solo por dos `.pyc` de
`__pycache__`. El contenido de `cdad-cycle` es idéntico al repo en las tres instalaciones. El
respaldo completo quedó fuera del repo. Queda pendiente la medición de uso de D-1 con una sesión
nueva.
