# Directiva del owner — test por contrato, no por cobertura (provisional)

**Vigente desde:** 2026-10-27, por decisión del dueño (Pablo).
**Alcance:** todo el epic 008, a partir de su aplicación en 008-002 y hasta que 008-006 la formalice en las fuentes de los roles.
**Estado:** provisional — se prueba en uso antes de convertirla en doctrina del producto.

## Texto de la regla

> **REGLA DE TRABAJO VIGENTE EN ESTA UNIDAD — DIRECTIVA DEL OWNER (obligatoria, manda sobre cualquier criterio de cobertura)**
>
> **DESTINATARIOS:** el principal es el ARCHITECT (la spec es donde nace el goldplating: postcondiciones por promesa de usuario, prohibido pedir "N variantes" de algo con el mismo resultado observable, sección `deferred-hardening` obligatoria). Le siguen test-writer (un test por promesa), reviewer (cláusula 7) y scribe (`deferred-hardening` al closure). El IMPLEMENTER queda FUERA de esta regla: es disciplina de TESTS, no de código. El implementer puede y debe agregar la robustez que considere necesaria (validaciones, guardas, manejo de casos límite razonables) aunque ningún test la exija; no se lo limita a "lo mínimo para que pase el test", porque eso produce código frágil.
>
> 1. Un test existe SOLO si su ausencia deja que un comportamiento VISIBLE PARA EL USUARIO FINAL se rompa en silencio.
> 2. Variantes internas con el mismo resultado observable son UN test. Dos implementaciones funcionalmente equivalentes que pasan por caminos distintos NO generan dos tests.
> 3. Un test por PROMESA al usuario, no por postcondición. Si dos postcondiciones protegen la misma promesa, va un solo test.
> 4. Cada test declara en una línea qué se rompe para el usuario sin él ("sin este test, el usuario...").
> 5. Lo que se decide NO probar en esta unidad va a la sección `deferred-hardening` de la spec (y del closure al cerrar). No se disfraza de deuda oculta ni se omite.
> 6. Prohibido: objetivos de cobertura, tests por simetría, escenarios que sólo protegen contra un integrador hipotético o contra transiciones internas del framework que el usuario no puede observar.
> 7. Reviewer: todo hallazgo por "falta este test" debe nombrar la consecuencia de usuario. Si no puede nombrarla, el hallazgo se registra como diferido en `deferred-hardening` y NO bloquea.
> 8. Gate del orquestador antes de aprobar RED: una sola pregunta — «¿qué se rompe para el usuario sin este test?». Si la respuesta no existe, el test no entra (o entra como diferido declarado).
> 9. FACULTAD DEL ORQUESTADOR: la regla es un piso, no un techo. Un hallazgo no bloqueante puede promoverse a test por decisión del orquestador cuando toque (a) seguridad, (b) integridad o pérdida silenciosa de datos, o (c) una regresión cuya falla sería evidente y cara de descubrir tarde aunque no nombre una promesa directa. La decisión se registra con su motivo en el gate, no se aplica en silencio.

## Cómo se aplica mientras es provisional

- **Spec (architect):** cada postcondición se escribe como promesa observable; se prohíben las "N variantes" que producen el mismo resultado; toda spec incluye `deferred-hardening`.
- **RED (test-writer):** un test por promesa, con la línea «sin este test, el usuario…».
- **Review (reviewer):** cláusula 7; un hallazgo sin consecuencia de usuario va a `deferred-hardening`.
- **Gate (orquestador):** la pregunta de la cláusula 8, registrada en la transición.
- **Implementer:** fuera de la regla; la robustez razonable no se limita al mínimo que pasa el test.
- **Cierre (scribe):** `deferred-hardening` pasa al `closure.md`.

Esta directiva **no** relaja ninguna garantía de seguridad, integridad ni conservación de datos: esos casos entran por la cláusula 9.

## Camino a 008-006

008-006-contract-not-coverage convierte esta directiva en doctrina de las fuentes de los roles
(`sources/roles/architect.md`, `test-writer.md`, `reviewer.md`, `orchestrator.md`, `scribe.md`) y en el
detalle de `skills/cdad-cycle/references/stage-3-tdd.md`, con sus tests y su gate. Hasta entonces, esta
directiva es la referencia citada por las specs del epic.
