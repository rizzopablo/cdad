# Revisión independiente — 019-002

**Resultado: 1 hallazgo bloqueante.** La corrección resolvió la contradicción de cierre y quitó la cuota de preguntas de la guía de descubrimiento de feature. La ruta sin consulta quedó expresada en Stage 2, pero todavía contradice una plantilla efectiva de handoff. No se acredita la aceptación de la feature.

## Hallazgo

### La plantilla de borrador sigue exigiendo un brainstorm que puede no existir

**Required · Verdict: BLOCKING · Bucket: m**

- **Ubicación:** `skills/cdad-cycle/references/handoff-prompts.md:261–269`.
- **Contrato:** PC-1 y PC-6, `docs/specs/019-002-effective-discovery-instructions/spec.md:33,81`; ruta corregida en `stage-2-specification.md:17–19,33–37`.
- **Evidencia y consecuencia:** Stage 2 permite saltar la consulta y preparar el borrador con las decisiones recuperables del diálogo. Sin embargo, la plantilla de handoff todavía ordena producirlo “based on the brainstorm” y exige un “Brainstorm summary”. Es una plantilla efectiva para la delegación manual y la construcción del handoff (`skills/cdad-cycle/SKILL.md:161–165,280`). En una feature sencilla sin consulta, el orquestador recibe instrucciones incompatibles: debe aportar un resumen inexistente o reinterpretar la plantilla para poder despachar.
- **Cierre verificable:** alinear la plantilla de borrador con ambas rutas: resumen de consulta cuando exista y decisiones recuperables del diálogo cuando no. Contrastar de nuevo la plantilla con Stage 2 y reentrada, sin introducir consulta obligatoria ni fabricar un resumen.

## Resolución de los hallazgos anteriores

1. **Cierre `idle`/`null`: resuelto en la guía revisada.** `stage-5-merge.md:187` remite a la transición de cierre existente y ya no ordena escribir `done`/`null`; el handoff de epic reconoce el reposo legítimo (`skills/cdad-epic/references/feature-handoff.md:63`). La regresión ejecutable previa sigue siendo evidencia registrada, no una ejecución nueva de esta revisión.
2. **Consulta opcional: parcialmente resuelto.** Stage 1, Stage 2 y reentrada contemplan la ruta sin consulta, pero permanece la contradicción de la plantilla indicada arriba.
3. **Cuota de preguntas de feature: resuelto en la superficie señalada.** `stage-1-discovery.md:20` orienta la cantidad por utilidad y contexto. La cuota encontrada en `skills/cdad-epic/references/epic-discovery.md:29` corresponde al descubrimiento del epic, fuera del alcance de esta corrección; no la clasifico como nuevo requisito de esta feature.

## F011: clasificación

Ejecuté `bash scripts/validate-subagents.sh`: **exit 1**. El fallo concreto procede de `install.sh --check`, que informa diferencias entre el candidato del repositorio y agentes/skills instalados. La presencia de agentes, los artefactos históricos y el control de modelos instalables pasaron.

Por tanto, F011 es **un fallo real de consistencia de la instalación actual**, no evidencia de que la generación del candidato haya fallado ni de que `5bb788dc` lo haya causado. La corrección anterior reporta el mismo resultado sin sus cambios, pero no reproduje esa comparación. Como el contrato excluye instalación y despliegue, no corresponde repararlo aquí; tampoco debe presentarse como check verde. Para PC-7 sigue siendo necesario demostrar que las sesiones usan las instrucciones candidatas mediante la ruta aislada aprobada.

## Estado de evidencia

- **PC-1/PC-2:** **Failed** para la coherencia contextual de la ruta sin consulta, por el hallazgo.
- **PC-3:** **Supported within declared limits**, reutilizando la revisión previa del ejemplo y sus dos pruebas de reintento; no repetí esas pruebas.
- **PC-4:** **Supported within declared limits**, según los 17 tests GREEN registrados; no los repetí.
- **PC-5:** **Supported within declared limits** para la guía corregida y la evidencia ejecutable registrada; no repetí los 105 tests.
- **PC-6:** **Failed** por la contradicción del handoff; F011 permanece rojo por drift de instalación, con el alcance indicado.
- **PC-7:** **Missing**, pendiente del ejercicio real y su evaluación independiente.

## Evidencia de esta revisión

- Ruta C: `validate-request` y `validate-packet` finalizaron sin error; `render --route C` coincidió con la identificación recibida y `render | cmp - PACKET.md` devolvió `0`. El SHA-256 del spec coincide con el contratado.
- Revisé el delta de instrucciones desde `bc922c04`, el diff completo de la corrección `5bb788dc`, las pruebas focales y los informes RED/GREEN. `git diff --quiet 5bb788dc HEAD -- sources agents skills scripts tests install.sh build CDAD_metodologia.md` devolvió `0`.
- **Commit revisado:** `5bb788dc10a4fa391a588168a6dbef0f654f3dfb`.
- No modifiqué archivos ni creé commits. El estado observado conserva una modificación de `docs/.cdad-state.json` y dos informes de recuperación sin seguimiento.
- No ejecuté la suite completa: corre por separado según el encargo y no se atribuye aquí un resultado.

## Abstentions

- No acredito el ejercicio real PC-7, la carga efectiva del candidato en sus sesiones ni su fidelidad: aún faltan los registros y la evaluación independiente.
- No verifiqué nuevamente las selecciones GREEN completas ni la afirmación de igualdad de F011 antes y después de la corrección.