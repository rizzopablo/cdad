# Etapa E2 — Planning del epic (light)

Producir un `plan.md` corto con la decomposición en features, contratos cross-feature, y criterios de aceptación del epic. Output aprobado por humano.

## Tu rol

Coordinás. Hacés draft del plan basado en el discovery + tus preguntas, el humano edita y aprueba.

## Filosofía light (recordatorio)

- Plan de 1-3 páginas.
- Lista de features con orden y dependencias, no especificación detallada de cada una (eso es trabajo de la feature en `cdad-cycle`).
- Contratos cross-feature solo para interfaces que varias features comparten.
- Sin ADRs especulativos. ADRs surgen feature por feature cuando son necesarios.
- Sin RFC formal ni gobernanza pesada.

Si el plan supera 3 páginas y no es porque el epic es genuinamente grande (10+ features), está pesado.

## Pasos

### Paso 1 — Decomposición en features

Conversación con el usuario. No emitís handoff a un rol; lo hacés vos + humano directamente, similar al brainstorm socrático en `cdad-cycle`.

Hacé preguntas:

- ¿Qué unidades funcionales vas a entregar? (cada una es una feature)
- ¿En qué orden tienen sentido?
- ¿Cuáles dependen de cuáles?
- ¿Cuáles podrían hacerse en paralelo?

Capturás la decomposición como tabla:

| # | Feature | Descripción (1 línea) | Dependencias | Paralelizable |
|---|---------|-----------------------|--------------|---------------|
| 001 | validar-cuit | Validador de formato CUIT con dígito verificador | — | Sí |
| 002 | generar-xml | Generación del XML AFIP a partir de objeto factura | 001 | No |
| 003 | enviar-ws | Envío al webservice AFIP con manejo de timeouts | 002 | No |
| 004 | cola-reintentos | Cola persistente para reintentar envíos fallidos | 003 | No |
| 005 | respuestas | Parseo de respuestas AFIP y mapeo a estados | 003 | Con 004 |

Naming: cada feature usa el prefijo `<epic-num>-<feat-num>-<slug>`. Ej: `001-002-generar-xml`.

### Paso 2 — Identificar contratos cross-feature

Si hay interfaces compartidas entre features (ej. una clase `Invoice` que tres features manipulan), documentá las firmas mínimas. NO el detalle implementacional, solo el contrato:

> *"Contrato `Invoice`: dataclass con campos cuit (str), fecha (date), items (list[Item]), total (Decimal). Usado por: 002, 003, 004."*

Si NO hay contratos cross-feature evidentes (cada feature es independiente con interfaces propias), saltás esta sección.

### Paso 3 — Criterios de aceptación del epic completo

Criterios medibles, igual que en specs de feature, pero sobre el epic:

> *"El epic está done cuando:*
> *1. Las 5 features están done individualmente (cada una con su gate de Etapa 5 cerrado).*
> *2. Test E2E cross-feature: dado una factura válida, se genera XML, se envía al WS de testing, se recibe respuesta, se persiste estado. Pasa.*
> *3. Test E2E de fallo: dado un envío fallido, la cola de reintentos lo levanta y reintenta hasta éxito o timeout. Pasa.*
> *4. Cobertura del módulo `facturacion/` ≥ 90%."*

### Paso 4 — Riesgos y deuda técnica esperada (opcional, breve)

Una sección corta:

> *"Riesgos: latencia del WS AFIP en producción puede ser variable; mitigación: timeouts configurables.*
> *Deuda esperada: el XML generation usa lxml; si el equipo prefiere stdlib, considerar refactor en epic posterior."*

Si no tenés nada relevante, omitir esta sección.

### Paso 5 — Producir `plan.md`

Cargá `assets/epic-plan-template.md` y rellenalo con lo trabajado. Estructura mínima:

```markdown
# Epic <id>: <nombre>

## Resumen
<1-3 líneas: problema, resultado>

## Scope
- In: <lista>
- Out: <lista>

## Decomposición
<tabla de features con orden y dependencias>

## Contratos cross-feature
<si aplica>

## Criterios de aceptación del epic
<lista medible>

## Riesgos / deuda esperada
<si aplica>

## Stakeholders
- Aprobador del plan: <nombre>
- Aprobador de specs de features: <nombre>
- Operador del resultado: <nombre>

---

Status: <Pending approval | Approved by <X> on <YYYY-MM-DD>>
```

### Paso 6 — Aprobación humana (indelegable)

> *"Plan en `docs/epics/<id>/plan.md`. Revisalo: (a) decomposición correcta y completa, (b) orden y dependencias bien definidos, (c) criterios de aceptación medibles. Si está OK, agregá la marca de aprobación al final. Avisame cuando esté."*

**Si el usuario te pide aprobar vos**: declinás amablemente.

> *"La aprobación del plan requiere tu juicio sobre prioridades y compromiso de entrega. Yo te puedo proponer cambios si querés, pero la marca va con tu nombre."*

## 🛑 Gate de salida (E2 → Loop de features)

- [ ] Existe `docs/epics/<epic-id>/plan.md`.
- [ ] Plan contiene: scope, decomposición con orden y dependencias, criterios de aceptación medibles.
- [ ] Marca de aprobación humana inequívoca.
- [ ] State file actualizado con `epic_features` (lista derivada de la decomposición).

Cuando todos OK: actualizá state (`epic_stage: features-loop`, populá `epic_features` desde el plan). Anunciá transición. Cargá `references/feature-handoff.md` para preparar el delegado a `cdad-cycle` para la primera feature.

## Anti-patrones

- **EAP-1**: plan kilométrico que nunca cierra. Si llevás más de 90 minutos en planning, el plan está pesado: cortá donde estás, marcá el resto como TBD a definir cuando arranquen las features correspondientes.
- **EAP-2**: cada feature en el plan tiene su mini-spec adentro. Eso duplica el trabajo de `cdad-cycle`. En el plan: descripción de 1 línea por feature. La spec real se hace cuando la feature se arranca.
- **EAP-3**: ADRs especulativos en el plan. Si el plan tiene una sección "Decisiones arquitectónicas", probablemente sea overkill. ADRs surgen feature por feature.

## Si el plan necesita actualizarse durante el loop de features

Es esperable. A medida que se implementan features, aparece info nueva: orden óptimo cambia, alguna feature se subdivide, otra se elimina, surge una nueva.

Cuando pase: actualizás `plan.md`, registrás el cambio en una sección "Cambios al plan" con fecha y motivo, y commiteás:

```
docs(epic): update plan — split feature 003 into 003a/003b

Motivo: durante implementación se detectó que enviar-ws tiene 
dos responsabilidades distintas que conviene separar.
```

NO requiere reaprobación formal salvo que el cambio modifique scope o criterios de aceptación del epic. Si lo hace, sí: reaprobación humana.
