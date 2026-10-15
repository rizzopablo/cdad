# Decisión del orquestador — sonda de descubrimiento 1 (003-007)

**Resultado: parcial.** La sesión nueva encontró el checkpoint (`head.json` + body),
reconstruyó objetivo, decisiones, paquete activo y próxima acción correctamente, y
verificó a mano los digests de las referencias. **No invocó `resume`**: dijo que no
ejecutó el CLI de continuidad "porque pediste modo lectura estricta". `resume` es de
solo lectura (`continuity.md`), así que la omisión viene de que el cableado del
orquestador no lo dice. Tampoco cargó la skill `cdad-cycle`.

**Consecuencia:** el descubrimiento espontáneo de `resume` sigue sin demostrarse.
La sesión rehízo a mano lo que `resume` hace (lectura y verificación de digests), con más
lecturas y sin la proyección acotada por rol.

**Decisión:** se incorpora al alcance de T4 (mismo bloque "Continuity wiring" de
`sources/roles/orchestrator.md` que T4 ya modifica por BL-1), sin cambiar la spec:
- (d) el cableado dice que `resume`, `reconcile` y `trigger` son de **solo lectura** y
  que `resume` es el **primer paso** de toda sesión nueva que retoma trabajo, antes de
  leer el state a mano.
El RED de T4 lo verifica en el agente regenerado. Tras T4 se repite la sonda con el mismo
prompt (sonda 2) como observable de cierre.
