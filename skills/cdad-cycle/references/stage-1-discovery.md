# Etapa 1 — Descubrimiento

Destruir suposiciones del LLM sobre el sistema antes de codear.

## Tu rol como orquestador en esta etapa

NO descubrís vos. Coordinás:

1. Detectás si falta `docs/landscape.md` (descubrimiento inicial) o si la feature requiere descubrimiento puntual.
2. Si descubrimiento inicial: el **humano** lo hace manualmente (no delegás al architect; el humano necesita ganar conocimiento de primera mano para evaluar después). Vos lo guiás con preguntas estructuradoras y armás el documento con sus respuestas.
3. Si descubrimiento por feature: emitís handoff packet al **architect** (read-only) que mapea APIs/hooks/módulos relevantes.
4. Validás resultado en re-entry.

## Modalidad A — Descubrimiento inicial

Aplica solo si `docs/landscape.md` no existe Y es la primera feature.

### Tu trabajo

Hacé preguntas al humano (una a tres por turno) para que cubra:

- Entidades/modelos centrales del sistema.
- Hooks o puntos de extensión del framework.
- Convenciones de naming, organización, layering.
- Diferencias entre la versión usada y la documentada.
- Patrones recomendados / desaconsejados.

Estructurás las respuestas en `docs/landscape.md` con secciones claras. Devolvés draft, el humano edita y confirma.

**No emitís handoff a un rol acá.** Esta modalidad es vos + humano directamente.

### Estructura típica

```markdown
# Landscape — <proyecto>

## Contexto del sistema
## Entidades y modelos centrales
## Puntos de extensión
## Convenciones del proyecto
## Diferencias con documentación oficial
## Lo que NO usamos
```

## Modalidad B — Descubrimiento por feature

Modalidad habitual antes de cada feature.

### Tu trabajo

1. Pedile al usuario qué partes del sistema toca la feature (módulos, modelos, endpoints, capas).
2. Cargá `references/handoff-prompts.md` sección "Architect (Etapa 1 — Descubrimiento por feature)".
3. Generá el handoff packet con:
   - La descripción funcional preliminar (una frase).
   - La lista de archivos relevantes que el usuario te dio.
   - El contenido de `docs/landscape.md`, `docs/projectbrief.md`, `docs/systemPatterns.md`.
4. **Entregá el packet y terminá el turno.**

### Re-entry

Cuando el usuario vuelve con el output del architect, cargá `references/re-entry.md` sección "Architect — descubrimiento por feature" y validá.

Si pasa: el output va a la sección "Contexto técnico" del spec en Etapa 2.

## 🛑 Gate de salida (Etapa 1 → Etapa 2)

- [ ] Si primera feature: `docs/landscape.md` con contenido real (no placeholders).
- [ ] Para esta feature: el usuario puede explicar qué APIs/hooks va a tocar sin abrir el código.
- [ ] No quedan suposiciones tipo "yo creo que existe X" pendientes.

Si todos OK: actualizá state file (`current_stage: specification`), anunciá transición, y emití handoff a architect modo brainstorm para Etapa 2.

Si falta algo: identificá qué específicamente y volvé al usuario / al architect.

## Anti-patrones

- **Saltar al spec sin descubrimiento** → garantía de inventos en Etapa 3.
- **Descubrimiento exhaustivo** mapeando proyecto entero (modalidad A para cada feature) → consume tiempo sin ROI.
- **Vos haciendo el descubrimiento** en lugar de coordinarlo → perdés el oráculo independiente del architect y, peor, el humano pierde la oportunidad de aprender de primera mano.
