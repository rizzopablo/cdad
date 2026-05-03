---
feature_id: <NNN-feature-id>
feature_name: <nombre corto>
created_at: <YYYY-MM-DD>
approved_by: <pendiente>
approved_at: <pendiente>
---

# Spec: <nombre de la feature>

## Descripción funcional

<Descripción en lenguaje cercano al usuario final. Qué hace la feature, para qué sirve, en qué contexto se usa. 2-5 líneas.>

## Contrato (firma e invariantes)

**Firma:**

```<lenguaje>
<firma de la función / método / endpoint, con tipos>
```

**Postcondiciones (numeradas y verificables):**

1. <Si <input válido>, retorna <output esperado con propiedades específicas>.>
2. <Si <caso de error>, lanza/retorna <comportamiento específico>.>
3. <...>

## Invariantes verificables

<Propiedades que se cumplen para todo input válido. Base de property tests. Si la feature no tiene invariantes claras, eliminá esta sección.>

- ∀ <variable> válido: <propiedad>
- <...>

## Criterios de aceptación

<Métricas medibles, no adjetivos vagos.>

- [ ] Test unitario para cada postcondición pasa.
- [ ] Cobertura de líneas en `<archivo principal>` ≥ <X>%.
- [ ] Property test con <N> inputs random pasa.
- [ ] <Test E2E si aplica: descripción del flujo completo>.

## Out of scope

<Qué NO hace la feature, para evitar scope creep.>

- <Caso 1 explícitamente fuera>
- <Caso 2>

## Notas de implementación (opcional)

<Decisiones técnicas tomadas durante el brainstorm que aclaran el cómo sin imponerlo. Pueden ir aquí trade-offs, alternativas descartadas, etc.>

## Contexto técnico

<Output del descubrimiento por feature: qué APIs/hooks/módulos toca, convenciones específicas que aplican, gotchas conocidos.>

---

Status: <Pending approval | Approved by <nombre> on <YYYY-MM-DD>>
