# Decisión del dueño — Calibración de la revisión (proporcionalidad vs. detalle infinito)

Fecha: 2026-10-05. Registrada por el orquestador (HITL delegada). Origen: instrucción
del usuario en sesión durante el ciclo de 003-002.

## Texto de la instrucción

> «El reviewer no debería ser infinitamente detallista, porque siempre podría encontrar
> un detalle más para criticar, pero no debe perder el objetivo de usabilidad del
> sistema.»

## Contexto que la motivó

En el review-fix de T3 de 003-002, el reviewer encontró de forma sucesiva variantes del
mismo defecto (la ligadura entre `argv` y las selecciones declaradas de una corrida de
evidencia):

1. `R1` — la forma `discover -s X` con `test_selection` sesgada.
2. `F1` — la forma `python3 -m unittest <módulo>` (sin `discover`).
3. `R-F1a` / `R-F1b` — `-v <módulo>` con la opción antes del módulo; paquete de un
   solo segmento.
4. `R-F1c` — una opción estándar no invariante (`-k`) incluso con la selección
   correcta.

Cada ronda era correcta en su hallazgo y, a la vez, **no cerraba la familia**: siempre
quedaba una forma de `argv` más por enumerar. El costo era rondas sucesivas de
RED/GREEN/re-review sobre el mismo eje, sin mejorar la utilidad del sistema.

## Decisión

**La revisión es proporcional al objetivo del sistema, no a la exhaustividad
adversarial.** Reglas operativas:

1. **Peso por efecto real, no por posibilidad lógica.** Un hallazgo es **BLOCKING**
   cuando afecta el propósito declarado del sistema o su usabilidad en un uso
   realista (incluido el uso descuidado o de buena fe). Un hallazgo que solo se
   dispara con una construcción **deliberadamente adversarial** —que exige, por
   ejemplo, declarar a la vez selecciones sesgadas y una forma de invocación
   exótica— y que **no tiene camino realista**, es **OPTIONAL / deuda**, aunque sea
   formalmente cierto.
2. **Un defecto de CLASE se corrige como clase, en una ronda.** Si un hallazgo revela
   una familia (no un caso), el remedio es estructural y **fail-closed** (lo que no
   puede demostrarse, degrada), no la enumeración de variantes. El reviewer debe
   dictaminar la clase y su remedio, no producir la variante siguiente.
3. **La re-review cierra sobre la clase y la no-regresión.** Una re-review de cierre
   verifica: (a) el remedio de clase aplicado, (b) que no hay regresión en los locks,
   (c) que el caso bueno canónico sigue verde. **No abre una nueva caza de variantes**
   sobre el mismo eje; si encuentra una variante nueva de una clase ya cerrada, la
   registra como deuda con su razón de no-realismo y no bloquea.
4. **La usabilidad es un criterio de aceptación, no un adorno.** Un mecanismo que se
   vuelve inusable por perseguir rigor formal (invocaciones legítimas rechazadas,
   rondas infinitas, complejidad que nadie puede mantener) **falla** su objetivo
   aunque sus aserciones sean correctas.

## Consecuencia inmediata

Se aplicó el remedio de clase en **una** ronda (`5c76fee`: whitelist explícita de
opciones invariantes a la selección + única forma plenamente ligable + degradación por
defecto a `unknown`), cerrando `R-F1a`, `R-F1b` y `R-F1c` juntos, en lugar de seguir
enumerando formas de `argv`.

## Alcance

- Aplica a **toda** revisión de CDAD (cualquier feature, cualquier epic), no solo a
  003-002.
- No relaja los invariantes ni la severidad de los defectos **observables en uso
  real**: un escape alcanzable por un uso normal sigue siendo bloqueante.
- No autoriza al reviewer a abstenerse de buscar; autoriza a **ponderar** y a
  **cerrar por clase**.

## Registro de aplicación

| Fecha | Ciclo | Aplicación |
|---|---|---|
| 2026-10-05 | 003-002 T3 | Remedio de clase fail-closed en una ronda tras la instrucción; `R-F1a/b/c` cerrados juntos. |
