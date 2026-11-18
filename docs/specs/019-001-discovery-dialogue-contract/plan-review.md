## Dictamen

Revisé el borrador `docs/specs/019-001-discovery-dialogue-contract/spec.md`, SHA-256 `ebeed5e09a2ddd54424a5db03a8bfc507cb9106b6d0cfbab250a480de351b471`. La revisión no constituye aprobación ni autoriza su implementación.

### Required — La aceptación futura no exige observar los casos que exige el epic

**Verdict: BLOCKING · Bucket: h**

El plan aprobado exige que los casos observados cubran respuesta parcial, propuesta por defecto no aceptada, corrección, decisión conductual pendiente e incertidumbre técnica (`docs/epics/epic-019-discovery-dialogue/plan.md:102–112`). Sin embargo, el contrato del borrador exige esos comportamientos en **ejemplos ilustrativos** (`spec.md:171`), mientras que el protocolo para el ejercicio real solo exige el recorrido general, insumos protegidos, criterios y reporte (`spec.md:173`). No exige que ese ejercicio, ni otros casos observados, incluyan los supuestos específicos del epic.

**Consecuencia:** 019-002 podría demostrar el recorrido completo con una conversación sencilla y declararlo satisfactorio sin observar si el agente inventa acuerdos o cierra prematuramente en los casos de riesgo que motivaron el epic. Los ejemplos ilustrativos no compensan esa falta: el propio borrador reconoce que no prueban cumplimiento.

**Cierre verificable:** exigir en el handoff de aceptación de 019-002 evidencia observada para cada uno de los casos del epic, vinculada a transcripciones o artefactos y con sus resultados o limitaciones. No es necesario imponer una cantidad fija de escenarios: una misma ejecución puede cubrir varios casos.

## Abstentions

- No dictamino sobre la fidelidad del producto final ni la conducta efectiva de los agentes: el diseño aún no está construido ni activado.
- No completé el contraste de la tabla de decisiones vigentes con todos los ADR aplicables; no afirmo ausencia de conflictos con ellos.
- No ejecuté la suite: esta revisión es de un borrador documental, no de una implementación.

## Evidencia de la revisión

- **Archivos modificados por esta sesión:** ninguno.
- **Commit creado:** ninguno. HEAD observado: `d5649196aa1bfdf890fd6ae31a19f6ad1d63a22c`.
- **Validación del paquete:** ejecuté `python3 scripts/cdad_packet.py validate-request` y `validate-packet` sobre el request, paquete y contexto identificados; ambos terminaron sin diagnóstico. `render --route C` reprodujo la identificación recibida.
- **Comprobación del objeto:** `sha256sum docs/specs/019-001-discovery-dialogue-contract/spec.md` devolvió el digest indicado arriba.
- **Test existente consultado:** `sed -n '694,723p' tests/test_006_005_u7_scribe_role_report.py` confirmó la expectativa actual de rechazo de `architect/brainstorm` con `role-report`; no ejecuté ese test.
- **Estado observado:** `git status --short` mostró una modificación de `docs/.cdad-state.json` y un archivo no seguido `docs/epics/epic-019-discovery-dialogue/review-begin.json`; no fueron modificados por esta sesión.