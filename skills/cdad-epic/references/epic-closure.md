# Etapa E4 — Closure del epic

Cierre del epic: consolidación del Memory Bank, retrospectiva breve, ADRs pendientes (si surgieron decisiones del epic que aún no están documentadas), commit de cierre.

## Tu rol

Coordinás. Emitís handoff a **scribe modo epic** para drafts. El usuario (humano o agente autónomo de mayor jerarquía) aprueba; el orquestador commitea.

## Pasos

### Paso 1 — Handoff al scribe

Es similar al scribe de feature (`cdad-cycle`) pero con scope ampliado: cubre el epic completo.

Generá packet con:

- `docs/epics/<id>/plan.md` (aprobado).
- `docs/epics/<id>/integration.md`.
- Los specs de todas las features del epic.
- Memory Bank actual: `projectbrief.md`, `activeContext.md`, `progress.md`, `systemPatterns.md`, `docs/adr/`.
- Diff agregado del epic (si tu entorno lo permite, generá un diff cumulativo entre el commit base del epic y HEAD).

```
Sos un sub-agente scribe en CDAD modo cierre de epic.

Tarea: producir cuatro drafts para el cierre del epic:
1. Entry de cierre del epic en activeContext.md.
2. Update de progress.md (mover epic completo a "done").
3. ADR(s) si detectás decisiones arquitectónicas del epic que aún no están 
   documentadas en docs/adr/. Por feature pueden ya estar; acá buscás las 
   transversales al epic.
4. Draft de docs/epics/<id>/closure.md con resumen, retrospectiva breve, 
   deuda técnica que se llevó.

Contexto:
1. Plan del epic: <pegar plan.md>
2. Integration report: <pegar integration.md>
3. Specs de features: <pegar todos>
4. Memory Bank actual
5. ADRs ya creados durante features del epic: <listar nombres>

Reglas estrictas:
- Permisos: read-only.
- NO commiteás. Generás drafts; el usuario aprueba; el orquestador commitea.
- Para ADRs nuevos: solo si la decisión es claramente del epic (transversal a 
  varias features) y aún no está documentada. Marcá confianza Alta/Media/Baja.

Output esperado, cuatro bloques:
[Draft 1: activeContext entry de cierre]
[Draft 2: progress.md changes]
[Draft 3: ADRs nuevos | "Sin ADRs nuevos"]
[Draft 4: closure.md]

Cuando termines:
"LISTO. Cuatro drafts: <bloques>"
```

Entregás packet, terminás turno.

### Paso 2 — Re-entry

Validá los cuatro drafts presentes. Pasá al usuario para aprobación; vos commiteás tras la aprobación.

### Paso 3 — Validación del usuario (indelegable)

Decile al usuario:

> *"Scribe terminó. Cuatro drafts:*
>
> *1. activeContext entry: <pegar>*
> *2. progress changes: <pegar>*
> *3. ADRs nuevos: <pegar | 'sin ADRs', con confianza>*
> *4. closure.md: <pegar>*
>
> *Editá lo que el scribe entendió mal. Cuando estés conforme, aprobá; el orquestador commitea con prefijo `docs(memory): close epic <id>`. Avisame cuando esté."*

### Paso 4 — Decisión sobre ADRs nuevos

Si el scribe propuso ADRs nuevos:

- **Confianza Alta**: típicamente merece ADR si es transversal al epic. Pasá al usuario para que lo expanda.
- **Confianza Media**: preguntale al usuario si vale.
- **Confianza Baja**: descartar por defecto.

Heurística: ¿la decisión afectó cómo se diseñaron varias features? ¿alguien dentro de 6-12 meses podría preguntar "por qué este epic se hizo así"? Si sí → ADR. Si no → descartar.

ADRs surgidos durante features individuales **ya deberían estar** en `docs/adr/` (escritos en E5 de `cdad-cycle`). El scribe del epic NO duplica esos; solo agrega los que son específicamente del epic y aún no están documentados.

### Paso 5 — Closure final

Una vez:

- CI verde completo.
- Cuatro drafts aprobados por el usuario y commiteados por el orquestador.
- ADRs (si los hay) commiteados.

Mergeás el branch del epic a main (o lo que el flujo del proyecto indique). Estrategia según convención del proyecto.

## 🛑 Gate de salida (E4 → epic done)

- [ ] CI verde completo.
- [ ] `docs/epics/<id>/closure.md` existe con resumen, retrospectiva, deuda llevada.
- [ ] `docs/activeContext.md` con entry de cierre del epic.
- [ ] `docs/progress.md` movió epic a "done".
- [ ] ADRs nuevos del epic (si los hay) commiteados.
- [ ] Commit con prefijo `docs(memory): close epic <id>` — aprobado por el usuario, ejecutado por el orquestador.
- [ ] Epic mergeado.

Cuando todos OK: actualizá state file:

```json
{
  "active_epic": null,
  "epic_stage": null,
  "epic_features": [],
  "epic_history": [..., {"stage": "epic-closure", "completed_at": "..."}]
}
```

Y cerrá:

> *"Epic `<id>` cerrado. <X features> entregadas. Memory Bank consolidado. ¿Próximo epic, próxima feature standalone, o cerramos por hoy?"*

## Estructura de `closure.md`

Template en `assets/epic-closure-template.md`. Estructura:

```markdown
# Epic <id> — Closure

Cerrado: <YYYY-MM-DD>

## Resumen

<2-3 líneas: qué se entregó, contra qué problema>

## Features entregadas

<lista con id, nombre, fecha de cierre individual>

## Criterios de aceptación

<cada criterio del plan + ✅ verificado / ❌ no cumplido (con motivo)>

## Retrospectiva breve

### Lo que funcionó bien
<1-3 puntos>

### Lo que se complicó
<1-3 puntos>

### Aprendizajes para futuros epics
<1-3 puntos>

## Deuda técnica que se llevó

<lista corta: cosas que decidimos no hacer en este epic y por qué>

## Decisiones arquitectónicas tomadas

<lista de ADRs creados durante el epic, con link>
```

Mantenelo corto. Una página, máximo dos. Si el epic fue chico, una sola sección de "Resumen" y "Deuda" alcanza.

## Anti-patrones

- **EAP-3**: ADRs especulativos al cierre. Solo ADRs que documentan decisiones reales tomadas durante el epic. No "vamos a usar X en el futuro".
- **Closure exhaustivo**: closure de 10 páginas no se lee. Una página, dos máximo.
- **Saltar el closure** porque "ya está mergeado". Sin closure, en 6 meses nadie recuerda qué se hizo y por qué. Es deuda invisible.

## Después del cierre

El epic está done. Vuelta al estado inicial: el usuario puede arrancar otro epic, una feature standalone, o cerrar la sesión.
