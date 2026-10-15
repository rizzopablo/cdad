# Decisión del orquestador — `record` también en el body de `begin` (003-007 T2)

**Problema.** D5 de la spec dice que el body de `begin` queda "byte-idéntico al actual
(compatibilidad del no-op de `begin`)". Esa compatibilidad ya no existe desde T1 (`b1e56e9`):
el body estampa `class` en cada referencia, así que un `begin` de antes de 003-007
re-ejecutado con el CLI nuevo produce otro body de todos modos. Mantener el `begin` sin
`record` solo debilita el discriminador de legado de O-1 (`review-t1-decision.md`): un body
de `begin` nuevo sin `record` sería indistinguible de uno legado.

**Decisión.** Todo body escrito por el CLI nuevo lleva `record`: `"begin"` o `"checkpoint"`,
según el comando que lo escribió.
- Legado = body **sin** `record`. Solo ahí rige la resolución por comparación (P7).
- Una referencia sin `class` en un body con `record` se trata como `contract` (P3).
- La detección de split-brain no cambia: ≥2 bodies con `record != "checkpoint"` bajo la
  misma clave (begins nuevos, legados, huérfanos).
- El no-op de `begin` sigue valiendo para un `begin` repetido con el mismo body.

El RED de T2 (`1d43ac7`) no fija el body de `begin`, así que no hay que tocar tests. Se
rectifica D5 de la spec en lo que T1 ya hizo obsoleto. P5, P6 y P7 no cambian de sentido.

**Enmienda (review T2, R-1).** El no-op de `begin` vale cuando el head vigente es ese mismo
`begin`. Si el head ya avanzó por un checkpoint de la misma clave, re-ejecutar el `begin`
falla cerrado sin escribir. Ese caso no ocurre en el flujo sancionado; queda como deuda
`T2-R1` (`review-t2-decision.md`).
