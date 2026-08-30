---
name: "odoo-architect"
description: >
  Guía de implementación de proyectos Odoo para el rol architect de CDAD.
  Modelo de fases GAP Analysis→Kick-Off→Implementation→Go-Live (con pesos de
  esfuerzo), roles PL/SPoC/Developer, principio "configuración primero, custom
  solo si hay gap justificado", inventario de módulos OCA/core antes de
  especificar, y formato de output de Discovery (mapeo proceso→módulo). Usar
  en las etapas 1 (Discovery) y 2 (Spec) de cualquier feature sobre un
  proyecto Odoo.
---

# odoo-architect — metodología de implementación de proyectos Odoo

> Fuente: metodología de implementación publicada por Odoo
> (PDF accesible vía https://www.odoo.com/web/content/17936384).
> El modelo de fases de consultoría y los roles PL/SPoC/Developer son el marco
> de referencia del documento. Los PORCENTAJES de esfuerzo por fase son
> HEURÍSTICA de este skill — pesos indicativos, no parte del documento citado.
> La base técnica son prácticas de implementación Odoo estándar exigidas por
> la industria y verificadas en OCA/core; citá el documento como referencia al
> fundamentar el estado de una implementación.

## Detección automática (`stack: odoo`)

Este skill es la especialización Odoo de CDAD (ver `cdad-cycle` §3.1 y
`references/bootstrap.md` Paso 2b, en el skill genérico). Un proyecto es
candidato a `stack: odoo` cuando hay evidencia objetiva en el repo:

- existe algún `__manifest__.py` (marcador inequívoco de un módulo Odoo), o
- `docs/projectbrief.md` o la especificación inicial del usuario mencionan
  "Odoo", "módulo"/"addon" en ese sentido, o un framework de otro dominio
  (Django, Rails…) no aparece.

Con evidencia clara, bootstrap setea `stack: odoo` sin preguntar. Con
ambigüedad, es una pregunta al usuario (si hay uno presente) — nunca una
asunción.

## Antes de avanzar a la Etapa 2 (Spec): ¿hay con qué correr tests?

La Etapa 1 (Discovery) no debería cerrar sin saber esto — si se descubre
recién en Etapa 3 (TDD), la feature ya tiene spec aprobado y el problema
bloquea más tarde y más caro.

Cargá el skill `odoo-make-env` y seguí su procedimiento de detección de
entorno **una vez, al principio del proyecto** (no por feature). Si no hay
ningún entorno de ejecución resuelto todavía, es un tema a resolver antes de
cerrar Discovery, no una sorpresa en TDD.

## Principio rector

**"Configuración primero; custom solo si hay un gap justificado."** La regla de
la implementación Odoo es resolver el proceso con la configuración nativa
(standard apps, campos, vistas, derechos de acceso) y recurrir a desarrollo
custom (módulos propios) únicamente cuando el requerimiento no puede
satisfacerse de forma mantenible con la funcionalidad de fábrica. Un "gap"
es un requerimiento que la configuración nativa no cubre y que el dueño del
proceso acepta como necesario, no un deseo de "lo hacemos custom" por defecto.

## Modelo de fases (proyecto de implementación)

La implementación sigue un modelo de fases iterativas, con pesos de esfuerzo
que orientan el plan. Los pesos son HEURÍSTICA (indicativos, no parte del
documento citado): la distribución exacta depende del alcance y madurez del
cliente.

| Fase | Foco | Esfuerzo (peso indicativo) |
|---|---|---|
| **GAP Analysis** | Levantar los procesos actuales, identificar la brecha entre lo que el negocio hace y lo que Odoo cubre por configuración; inventario de módulos OCA/core candidatos | 25% |
| **Kick-Off** | Alinear stakeholders, definir alcance, plan de fase, responsables (PL/SPoC/Developer), cronograma y criterios de aceptación | 5% |
| **Implementation** | Configuración primero + custom (solo gaps); desarrollo en ciclos con testing continuo (contrato make CDAD) | 55% |
| **Go-Live** | Migración/carga de datos, entrenamiento, corte, soporte post-implementación y acceptance final | 15% |

## Roles del proyecto

- **PL (Project Lead)** — responsable del plan, alcance, cronograma y la
  relación con el dueño del proceso; decide (con el SPoC) qué es configuración
  y qué es gap.
- **SPoC (Single Point of Contact)** — único canal entre el proyecto y el
  cliente/negocio; consolida requerimientos y valida que la solución responde
  al proceso real.
- **Developer** — implementa la configuración y el custom autorizado (solo
  gaps), manteniendo el contrato de tests (make) y los estándares OCA.

## Inventario de módulos ANTES de especificar

Antes de describir contraintos de una feature Odoo, completá el **inventario
de módulos**: qué apps *core* de Odoo y qué módulos **OCA** (Open Community
Association) cubren (parcial o totalmente) el proceso/movimiento que la
feature toca. La recomendación es reutilizar un módulo OCA/core existente
antes que especificar custom nuevo — documentá el descarte cuando aplique
(`VERIFICAR` si no podés confirmar el módulo exacto). El inventario va a la
sección "Contexto técnico" del spec.

## Formato de output de Discovery (mapeo proceso→módulo)

El Discovery de una feature Odoo entrega un mapeo **proceso→módulo**: qué
proceso de negocio (o flujo) la feature representa y qué módulos (core/OCA)
lo materializan, con su estado (ya existe / extender / crear custom por gap).

Formato de salida:

```markdown
## Mapeo proceso → módulo
- Proceso: <nombre del proceso/flujo>
  - Módulo core: <app.core / none>
  - Módulo OCA: <odoo/community-addons: nombre | none>
  - Módulo custom: <necesario solo si gap justificado | no>
  - Gap justificado: <sí, porque <razón> | no>
## Modelos/entidades tocadas
<...>
## Hooks/extensión disponibles
<...>
## Convenciones aplicables
<...>
## Verificaciones pendientes
<...>
```

## Marco de pregunta socrática (específico Odoo)

En el brainstorm, además de inputs/outputs/errores/permisos, preguntá:
- ¿El requerimiento se cubre con **configuración** (derechos, vistas, data
  demo, campos estándar) o exige **custom**?
- ¿Existe un módulo **OCA/core** que ya lo resuelva?
- ¿Cuál es el **SPoC** que valida la lógica de negocio? ¿Y el **PL** que
  define el alcance?
- ¿El gap está **justificado** por el dueño del proceso, o es un "custom por
  defecto"?

## Anti-patrones a evitar

- Especificar custom sin haber hecho el inventario OCA/core.
- Saltarse el juicio "configuración primero" e ir directo a desarrollo.
- Confundir roles: el PL define alcance, el SPoC valida negocio, el
  Developer implementa solo lo autorizado.