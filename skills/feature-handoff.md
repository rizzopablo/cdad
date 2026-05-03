# Feature Handoff — Delegación a `cdad-cycle`

Cómo el coordinador del epic emite el handoff para que el usuario arranque una feature delegando al skill `cdad-cycle`.

## Cuándo emitir handoff de feature

En el loop de features (etapa entre E2 y E3 del epic), después de que una feature cierra, identificás la próxima feature `queued` que tiene sus dependencias `done`.

Lógica:

1. Filtrá `epic_features` por `status: queued`.
2. Para cada queued, verificá que todas las features en su columna "Dependencias" estén `done`.
3. Si hay varias candidatas (paralelizables), preguntale al usuario cuál arrancar.
4. Si hay una sola, esa es la próxima.

## Formato del handoff packet

```
🔀 HANDOFF: Próxima feature del epic

Feature: <id>
Descripción: <1 línea del plan>
Dependencias: <lista, todas marcadas done>

──────────────────────────────────────────
Para arrancarla (recomendado: chat nuevo):

1. Abrí chat nuevo.
2. Invocá el skill `cdad-cycle` con esta frase:

   "Arranquemos la feature `<feat-id>` del epic `<epic-id>` siguiendo CDAD."

3. El coordinador de feature va a:
   - Leer el state (verá que pertenece al epic <epic-id>)
   - Cargar contexto del epic (plan.md, contratos cross-feature)
   - Arrancar Etapa 1 (Descubrimiento por feature)

4. Cuando la feature cierre (Memory Bank actualizado, mergeada), 
   volvé acá a `cdad-epic` con: "Feature <feat-id> done."

──────────────────────────────────────────

Mientras tanto, yo (coordinador del epic) espero. State actual:

- Epic: <epic-id>, etapa: features-loop
- Features done: <lista>
- En progreso ahora: <feat-id>
- Queued restantes: <lista>
```

Después del packet, **terminás turno**.

## Re-entry — feature done

Cuando el usuario vuelve diciendo *"Feature `<id>` done"* o equivalente:

### Validaciones

1. **Verificá en `progress.md`** que la feature aparece bajo "Done".
2. **Verificá en el state file** que `current_stage` es `done` y `active_feature` es null o cambió.
3. **Verificá en `activeContext.md`** que hay entry reciente con la feature cerrada.

Si algo falta:

> *"Antes de marcarla done en el epic, falta `<X>`. ¿Lo completaste o querés que lo revisemos?"*

Si todo OK:

1. Actualizá `epic_features[<feat>].status: done` y `completed_at`.
2. Identificá próxima feature elegible.
3. Si quedan features queued: emitir handoff de próxima feature.
4. Si TODAS están done: cerrar loop y avanzar a Etapa E3 (integración).

## Caso especial — feature in-progress en paralelo

Si el usuario está trabajando dos features del epic en paralelo (en branches distintos), `active_feature` en el state file no captura ambas. Opciones:

**Opción A — pista única**: una feature por vez en el state file. Si arrancan paralela, la segunda no se trackea por el state hasta que la primera cierra.

**Opción B — campo extendido**: agregar `parallel_features: [<id1>, <id2>]` al state.

Por defecto: **opción A**. Es más simple y la mayoría de los proyectos no necesitan parallel real con CDAD (la disciplina de sesiones aisladas es más fácil con una feature en foco).

Si el usuario insiste en paralelo: agregá el campo `parallel_features` al state y trackeá ambos. Cuando uno cierra, lo movés a `done` y queda el otro como activo único.

## Caso especial — feature del epic falla y vuelve para atrás

Si durante una feature el usuario detecta que el plan del epic está mal (ej. dependencia no contemplada, contrato cross-feature insuficiente), hay que volver al plan del epic.

El usuario vuelve a `cdad-epic` diciendo *"el plan necesita ajuste por X"*. Vos:

1. Pausás la feature en el state (`epic_features[<feat>].status: paused`).
2. Cargás `epic-planning.md` y aplicás el cambio al plan.
3. Reaprobación si el cambio toca scope o criterios. Si solo es decomposición (split de feature, reordenamiento), basta commit del cambio.
4. Cuando el plan está actualizado, volvés a la feature: cambio status a `in-progress` y emitís handoff de continuación al usuario.

## Caso especial — feature standalone que no pertenece al epic

Si el usuario arranca una feature standalone (sin prefijo del epic) mientras el epic está activo, está bien. CDAD no obliga a pausar el epic para hacer una feature standalone (un fix de bug urgente, por ejemplo).

En ese caso:

- `cdad-cycle` corre normal con la feature standalone.
- `cdad-epic` no se involucra.
- El state file refleja: `active_epic` sigue activo, pero `active_feature` apunta a la standalone (no del epic).
- Cuando la standalone cierra, `cdad-epic` puede retomar el loop del epic.

## Recordatorio operativo

El handoff a `cdad-cycle` es la **única vez** que emitís algo "de" un rol externo. No estás generando un prompt para un sub-agente; estás indicándole al usuario que use otro skill. La diferencia importa: el otro skill tiene su propia inteligencia y va a coordinar sus propios sub-agentes (test-writer, implementer, etc.).

Por eso el handoff es más simple que los handoffs internos de `cdad-cycle`: solo le decís al usuario "arrancá `cdad-cycle` con esta feature".
