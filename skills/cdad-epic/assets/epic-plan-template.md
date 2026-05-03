---
epic_id: <NNN-epic-id>
epic_name: <nombre corto>
created_at: <YYYY-MM-DD>
approved_by: <pendiente>
approved_at: <pendiente>
---

# Epic <NNN>: <nombre>

## Resumen

<2-3 líneas: qué problema resuelve, qué se entrega cuando esté done.>

## Scope

**In scope:**
- <punto 1>
- <punto 2>

**Out of scope:**
- <punto 1>
- <punto 2>

## Decomposición en features

| # | Feature ID | Descripción (1 línea) | Dependencias | Paralelizable |
|---|-----------|------------------------|--------------|---------------|
| 1 | <epic-num>-001-<slug> | <descripción> | — | Sí |
| 2 | <epic-num>-002-<slug> | <descripción> | 001 | No |
| 3 | <epic-num>-003-<slug> | <descripción> | 002 | No |

## Contratos cross-feature

<Si aplica: interfaces compartidas entre features. Mantener mínimo, solo firmas.>

```<lenguaje>
<firma del contrato compartido>
```

Usado por: <lista de features>.

<O eliminar esta sección si no aplica.>

## Criterios de aceptación del epic

<Medibles, cubren el flujo cross-feature completo.>

- [ ] Las <N> features están done individualmente.
- [ ] Test E2E cross-feature: <descripción del flujo principal>. Pasa.
- [ ] Test E2E de fallo: <descripción del path de error>. Pasa.
- [ ] <Otros criterios específicos del epic>.

## Riesgos / deuda esperada

<Opcional. Riesgos identificados al planificar, mitigaciones previstas, deuda que se sabe que va a quedar.>

- Riesgo: <...>. Mitigación: <...>.
- Deuda esperada: <...>.

<O eliminar esta sección si no aplica.>

## Stakeholders

- **Aprobador del plan del epic**: <nombre>
- **Aprobador de specs de features**: <nombre>
- **Operador del resultado**: <nombre>

## Cambios al plan

<Sección que se actualiza durante el loop de features si el plan cambia. Inicialmente vacía.>

<!-- Ejemplo de entry:
### YYYY-MM-DD — Split feature 003
Motivo: durante implementación detectamos que enviar-ws tiene dos responsabilidades que conviene separar.
Cambio: feature 003 se divide en 003a (envío) y 003b (manejo de respuestas síncronas).
-->

---

Status: <Pending approval | Approved by <nombre> on <YYYY-MM-DD>>
