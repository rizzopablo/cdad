# Resolución del AUDIT — 010-002-documentary-role-integration — 2026-10-31

Resolución del gate de AUDIT y de las cuatro decisiones que el informe
(`docs/specs/010-002-documentary-role-integration/test-audit.md`, SHA-256
`03027b0ec7da74e4549c94cf241c7a6dbf8ed556083363be80f415699a66acc4`) dejó
abiertas antes de autorizar el RED. Ejercida por el orquestador bajo el mandato
HITL del 2026-10-30 (§1 y §3).

## Veredicto del AUDIT

- Mapa PC-01..PC-13 → verificación **suficiente**, con clase explícita y
  consecuencia de usuario por postcondición.
- Presencia textual y suficiencia semántica **separadas**; PC-13 reservada al
  dictamen independiente de T8, sin proxy estructural.
- Matrices Odoo de PC-04/PC-05 cubiertas por rol y por artefacto distribuido, sin
  usar el `write_scope` del architect ni del reviewer como descripción del
  producto.
- Tres vías de PC-07 clasificadas; publicación ordinaria y reemplazo como
  **garantía por construcción**, no como ramas de rechazo alcanzables.
- Medición de fixtures completa, con ubicaciones: **4 simulaciones de histórico
  que quitan solo `agent`**, **1 discordancia estática por rol ajeno**, **0
  discordancias contextuales** y **0 oráculos de reemplazo que fijen la copia del
  agente**.
- Aislamiento (`HOME`/XDG/temporales + `CDAD_INSTALL_ROOT` explícito) y techo
  estático suficientes; el techo se reejecuta en T4 y **no se eleva**.

**Ninguna postcondición quedó no verificable.** No hay bloqueante de contrato.

## A1 — Extensión de alcance a `tests/test_010_004_t2_red.py` (adoptada)

El AUDIT encontró que el helper `locator_project` de
`tests/test_010_004_t2_red.py` construye requests con `execution_context` y sin
`agent` en cinco tests hoy verdes. Con la regla de presencia de PC-08 esos cinco
tests pasarían a rojo por un motivo ajeno a su propia promesa (localizador del
contexto, 010-004).

**Decisión.** Se extiende el `write_scope` de T5 para incluir ese archivo, con la
edición mínima: agregar el `agent` derivado al request sintético del helper (una
línea de fixture). **No se debilita ninguna aserción** de 010-004 y no se toca
ninguna de sus obligaciones; la obligación nueva (presencia de `agent` cuando hay
contexto) se cumple en el fixture. La tabla de `plan-tasks` y la prosa de T5
quedan ampliadas con ese archivo y su razón.

## A2 — Fixture de variante no publicada (adoptada, con rebase)

El test `test_pd14_unpublished_packet_agent_fails_closed_before_dispatch`
(`tests/test_006_005_u2_opencode_module.py`) inyecta un agente de **rol ajeno**.
Con el contraste estático de PC-07(b), ese rechazo ocurriría antes y el test
podría quedar verde sin probar la publicación de la variante.

**Decisión.** Se rebasa el fixture a una variante del **mismo rol**,
contextualmente coherente y **no publicada** (un `stack` sin agente derivado
publicado), y se assertea que la causa del rechazo es «variante no publicada».
La promesa de PC-08 («rechazo mecánico en el adaptador externo, sin fallback») se
mantiene atribuible al adaptador y no preemptada por el contraste estático.

## A3 — Ubicación del test de finalización write-ahead (adoptada, opción a)

**Decisión.** El test de finalización tras cambio de `stack` se implementa en el
módulo nuevo `tests/test_010_002_documentary_role_integration.py`, reutilizando
el patrón público del adaptador con runtime falso. **No** se edita
`tests/test_006_005_u6fix5_write_ahead.py` y no se amplía el alcance por esa vía:
el comportamiento es de esta unidad y su verificación vive en el módulo de esta
unidad.

## A4 — Aclaraciones recomendadas (tres adoptadas como registro, una diferida)

1. **Write-ahead de un intento histórico sin `agent`.** Se registra en el RED como
   caso comprometido: la finalización de un intento histórico sin `agent` tampoco
   aplica contraste contextual. Se deduce de D3 y se verifica explícitamente; no
   requiere cambio de contrato.
2. **Alcance de «validar un request publicado».** Se registra que la regla de
   presencia se aplica en `validate-request` y `validate-packet`, además de
   `render`, como ya implica D3.
3. **PC-03 es obligación procedimental.** Se registra que no hay rechazo mecánico
   de un encargo documental sin alcance declarado; un enforcement mecánico sería
   cambio de contrato fuera de esta unidad. El test verifica el procedimiento y
   la igualdad de scopes ya verde, no un rechazo inexistente.
4. **Atribución del rechazo de variante no publicada.** Queda resuelta por A2; no
   se difiere.

## A5 — Staging y snapshot (declarado)

El AUDIT observó `HEAD` `0279a9d0` frente al snapshot `3bea7a8d` que cita la spec,
y un `build/staging` previo. El contrato está pineado por SHA-256 y coincide; la
diferencia de `HEAD` es la materialización de los documentos de esta misma unidad
y no altera el contrato. T4 regenera `build/staging` antes de comparar; un test de
distribución que lea staging del checkout como oráculo del contenido corregido
queda expresamente prohibido (riesgo R8 del AUDIT).

## Autorización

Con A1..A5 resueltas, **se aprueba el gate de AUDIT** y se autoriza el RED de T3
con los trece tests de instrucciones y distribución listados en el informe, el
`write_scope` de T5 ampliado con `tests/test_010_004_t2_red.py`, y las
adaptaciones de fixture de A2 y A3 previstas para T5.
