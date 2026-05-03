# Etapa 5 — Merge y Memory Bank

CI completo + actualización del Memory Bank con patrón Scribe. Cierre de la feature.

## 5.1 — Verificación CI antes del merge

**No es opcional. No se skipea.**

### Verificaciones obligatorias

- **Linter completo**: sobre todos los archivos modificados, no solo el diff.
- **Type checker**: si el lenguaje lo soporta (mypy, tsc, etc.). Modo strict en interfaces y contratos.
- **Import-linter (o equivalente)**: boundaries arquitectónicos no violados.
- **Tests unitarios** y **de integración**: suite completa, no solo nuevos.
- **Contract tests parametrizados**: si la feature agrega una implementación de un Protocol/contrato.
- **Property tests**: con seed configurado, invariantes se cumplen.
- **Verificaciones específicas del proyecto**: cualquier check custom (manifest, TODOs sin issue, etc.).

### Cómo verificarlo

Si tenés bash, corré la suite. Si no, pedile al usuario:

> *"Corré la suite completa (`<comando del proyecto>`). Necesito ver: linter, type checker, import-linter, tests, property tests. Si alguno falla, volvemos a Etapa 3."*

### Si CI falla

**Volvés a Etapa 3** con el output del fallo. No mergeás bajo ningún concepto. La tentación de "es solo el linter, lo arreglo después" no se cede: lo arreglás antes.

## 5.2 — Patrón Scribe para Memory Bank

### Por qué este patrón

Actualizar el Memory Bank desde cero después de cada feature toma 15-20 minutos. Bajo presión, es lo primero que se salta. Resultado: Memory Bank desactualizado. La solución es **draft asistido + aprobación humana indelegable**.

### Setup del Scribe

Sub-agente `scribe` con permisos **read-only**. Le pasás:

- El spec aprobado (`docs/specs/<feat>/spec.md`).
- El diff completo del PR (`git diff <base>..HEAD`).
- El reporte del reviewer (`docs/specs/<feat>/review.md`).
- Los archivos actuales del Memory Bank (`docs/projectbrief.md`, `docs/activeContext.md`, `docs/progress.md`, `docs/systemPatterns.md`, `docs/adr/`).

### Tarea del Scribe

Producir tres outputs:

1. **Draft de entrada para `activeContext.md`** con la fecha, qué feature se cerró, decisiones técnicas relevantes, deuda técnica detectada.
2. **Modificaciones para `progress.md`**: mover feature de "in progress" a "done", actualizar estado general.
3. **Draft de ADR si detecta decisión arquitectónica relevante**, con campo "confianza" indicando qué tan seguro está de que merece ADR.

### Formato de la entrada en activeContext.md

```markdown
## <YYYY-MM-DD> — Feature: <nombre corto>

Cerrada feature de <descripción de una línea>.

Decisiones relevantes:
- <decisión 1, con trade-off si aplica>
- <decisión 2>

Deuda técnica detectada:
- <punto 1, con out-of-scope si quedó así por decisión>

Próxima feature en cola: <si la sabe>.
```

### Validación humana

Pasale el draft al usuario. **No commitees por él**. El usuario:

1. Lee el draft.
2. Corrige lo que el Scribe entendió mal.
3. Agrega lo que el Scribe no podía saber (contexto del cliente, decisiones de producto fuera del PR).
4. Decide sobre el ADR draft: descartar, expandir, o aceptar tal cual.
5. **Commitea** con prefijo `docs(memory):` y autoría humana.

### Si el Scribe propone ADR

Solo aceptalo si la decisión es arquitectónica de verdad. Heurística: ¿alguien dentro de 6 meses podría preguntar "¿por qué hicimos X de esta forma?"? Si sí, ADR. Si no, descartá.

Template de ADR en `assets/adr-template/ADR.md`. Formato MADR-like.

## 5.3 — Merge

Una vez:

- CI verde.
- Memory Bank actualizado y commiteado.
- Si hay ADR nuevo, también commiteado.

Mergeás a main (o a la rama base del flujo del proyecto). Estrategia (squash, merge commit, rebase) según convención del proyecto — **no es decisión del skill**, es del proyecto.

## Gate de salida (Etapa 5 → done)

- [ ] CI completo verde (linter, type checker, import-linter, unit, integration, contract, property).
- [ ] `docs/activeContext.md` tiene entrada nueva con fecha y resumen.
- [ ] `docs/progress.md` movió la feature de "in progress" a "done".
- [ ] Si la feature involucró decisión arquitectónica → existe ADR nuevo en `docs/adr/`.
- [ ] Commit del Memory Bank usa prefijo `docs(memory):` con autoría humana.
- [ ] Feature mergeada a main.

## Anti-patrones

- **Saltarse el CI** porque "tengo confianza". Garantía de regresión.
- **Delegar el commit del Memory Bank al LLM sin que el humano lea**. Pierde calidad gradualmente.
- **Crear ADRs especulativos** para "documentar" cosas que no son decisiones arquitectónicas. Inflación de ADRs es ruido.
- **No actualizar `progress.md`**. Después no sabés qué está done y qué no.

## Cierre del ciclo

State file:
```json
{
  "current_stage": "done",
  "active_feature": null,
  "tdd_substage": null,
  "postconditions_status": {},
  "stage_history": [..., {"stage": "merge", "completed_at": "..."}]
}
```

Cierre con el usuario:

> *"Feature `<X>` cerrada. Memory Bank actualizado. ¿Próxima feature, o cerramos por hoy?"*

Si dice "próxima feature", volvés a Etapa 1 (Descubrimiento) con la nueva.
