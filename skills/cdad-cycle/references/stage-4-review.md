# Etapa 4 — Review en dos capas

Capa 1: agente reviewer pasa exhaustivamente con spec en contexto. Capa 2: humano valida la priorización del reporte (no el diff completo).

## Por qué dos capas

Reviewer humano post-hoc se cansa, no recuerda el spec en detalle, y se vuelve cuello de botella. La capa 1 hace el trabajo pesado; la capa 2 aporta el juicio que solo el humano tiene.

## Capa 1 — Agente reviewer

### Setup

Sesión nueva con sub-agente `reviewer`. Permisos: **read-only** sobre todo el repo. Le pasás:

- El diff completo de la feature (`git diff <branch-base>..HEAD`).
- El spec aprobado (`docs/specs/<feat>/spec.md`).
- La interface o contrato que la feature implementa.
- El archivo `.importlinter` o equivalente (boundaries arquitectónicos).
- Convenciones del proyecto (`AGENTS.md`, `CONTRIBUTING.md`, `docs/systemPatterns.md`).

### Modelo distinto al implementer (recomendado)

Si tenés acceso a varios modelos, usá uno **distinto al que implementó**. Distintos modelos tienen blind spots distintos; un modelo diferente da segunda perspectiva real, no eco.

Si solo tenés un modelo, igual hacé el review — perdés diversidad pero mantenés el ojo extra.

### Prompt al reviewer

Pasale algo del estilo:

> *"Revisá este diff contra el spec adjunto. Reportá hallazgos en estas categorías:*
>
> *1. **Divergencias del spec**: el código no implementa lo que el spec pide, o agrega cosas que el spec no pide.*
> *2. **Violaciones de boundaries**: imports prohibidos, capas que no respetan dependencias permitidas.*
> *3. **Riesgos de seguridad**: SQL injection, command injection, secretos hardcodeados, validación faltante.*
> *4. **Inconsistencias de estilo**: el código no sigue convenciones del resto del proyecto.*
> *5. **Sugerencias de simplificación**: oportunidades de hacer el código más simple sin cambiar comportamiento.*
>
> *Para cada hallazgo: marcá **Bloqueante** (debe arreglarse antes del merge) u **Opcional** (sugerencia).*
>
> *Output: markdown estructurado en `docs/specs/<feat>/review.md`."*

### Output esperado

`docs/specs/<feat>/review.md` con estructura:

```markdown
# Review — <feature>

## Bloqueantes

### 1. <título corto>
Ubicación: <archivo:líneas>
Problema: <qué está mal>
Sugerencia: <cómo arreglarlo>

### 2. ...

## Opcionales

### 3. ...
```

## Capa 2 — Validación humana

### Tu rol

Llevá al usuario el reporte. **Que lea el reporte, no el diff**. El reviewer ya filtró y priorizó; el trabajo del usuario es validar la priorización.

### Para cada bloqueante

Preguntar al usuario:

- ¿Es genuinamente bloqueante?
- ¿O hay contexto que el reviewer no tiene? (spec desactualizado, ADR autorizando excepción, etc.)

La mayoría de las veces el usuario va a estar de acuerdo. Cuando no, el usuario lo desestima — y vos registrás el motivo en el review.md como nota.

### Para cada opcional

¿Aplicar ahora o descartar? Heurística:

- **Aplicar**: si es claramente buena, aprovechá el momentum.
- **Descartar**: si es sobre-ingenierización, scope creep, o estilo no crítico.

### Matriz de severidad por defecto

| Tipo de hallazgo | Severidad por defecto | Excepción |
|------------------|----------------------|-----------|
| Divergencia del spec | Bloqueante | Solo si el spec estaba desactualizado y el código tiene razón |
| Violación de boundary | Bloqueante | Solo si hay ADR explícito autorizando |
| Riesgo de seguridad | Bloqueante | Sin excepciones |
| Bug funcional | Bloqueante | Sin excepciones |
| Inconsistencia de estilo | Opcional | Bloqueante si es masiva |
| Oportunidad de simplificación | Opcional | Bloqueante si la complejidad actual es problemática |
| Sugerencia de feature adicional | Descartar | Esto es scope creep |

### Sesgo a vigilar

El usuario va a sentir presión de cerrar y va a estar tentado de marcar bloqueantes como opcionales para no volver a Etapa 3. Si lo detectás, señalalo:

> *"Si dudás de si esto es bloqueante, errate del lado de tratarlo como bloqueante. El costo de una iteración extra es bajo; el costo de mergear un bug es alto."*

## Output de la capa 2

Una **lista priorizada de fixes** que va al implementer en una nueva ronda. Algo del estilo:

> *"Fixes a aplicar al implementer:*
>
> *1. [Bloqueante] <descripción específica>*
> *2. [Bloqueante] <...>*
> *3. [Aceptado opcional] <...>*
>
> *Descartados: <con motivo si fue contraintuitivo>"*

## Loop con Etapa 3

Si hay bloqueantes o opcionales aceptados → volvés a Etapa 3 con la lista. El implementer aplica cambios. La suite debe seguir verde después de cada fix (si los fixes requieren cambio de comportamiento, eso significa que el **spec** necesita actualizarse y volvés a Etapa 2).

Después de los fixes, **otra pasada del reviewer** sobre el nuevo diff. Idealmente sí, en features chicas se puede skipear si los fixes fueron mecánicos y obvios.

## Gate de salida (Etapa 4 → Etapa 5)

- [ ] Existe `docs/specs/<feat>/review.md` con el reporte.
- [ ] Todos los bloqueantes están **resueltos** o **explícitamente desestimados con motivo escrito** en el review.md.
- [ ] El usuario aprobó la priorización (no delegado al LLM).
- [ ] La suite sigue verde después de los fixes.

## Anti-patrón principal

**Skipear el review en features pequeñas.** Resistilo. Aunque sea un review breve sobre 30 líneas de diff: detecta inconsistencias que en el momento parecen menores pero se acumulan a lo largo del proyecto.

## Cierre de la etapa

State file:
```json
{
  "current_stage": "merge",
  "stage_history": [..., {"stage": "review", "completed_at": "..."}]
}
```

Cargá `references/stage-5-merge.md`.
