**Ruta C validada; bloqueo al completar el plan.** No modifiqué archivos ni la spec.

La exigencia de conservar T1–T8 y que **cada tarea sea despachable con un solo rol/subfase** contradice la organización actual:

- **T1** corresponde al orquestador y a la autoridad aprobadora (`plan.md:16–30`).
- **T8** combina coordinación del orquestador, aceptación y borradores del scribe (`plan.md:182–206`).
- El orquestador **no es un rol despachable**: el catálogo solo admite architect, test-writer, implementer, reviewer y scribe; además lo declara expresamente (`skills/cdad-cycle/scripts/cdad_packet.py:62–93,103–105`).
- **T2** agrupa AUDIT y POST-AUDIT; **T7**, corrección y re-verificación independiente (`plan.md:32–58,166–180`). No pueden presentarse como un único despacho que ejecute ambas responsabilidades.

Añadir campos completos podría superar la validación estructural, pero no resolvería esta incompatibilidad. No devuelvo un plan completo afirmando una condición que no cumple.

**Reencauce recomendado:** autorizar que T1–T8 se conserven como hitos del plan, mientras **cada encargo dentro de ellos** mantiene un único rol/subfase. T1/T8 serían coordinación; T2 y T7 conservarían sus despachos independientes. Esto no requiere cambiar las promesas de la spec. Si se mantiene literalmente «una tarea = un despacho», hace falta autorizar otra descomposición.

### Evidencia

Ejecutados con salida correcta:
- `python3 scripts/cdad_packet.py validate-request --project-root . --execution-context .cdad/executions/exec-010-003-documentary-pilot-001/execution.json --request .cdad/packets/010-003-documentary-pilot-architect-draft-002/REQUEST.json`
- `python3 scripts/cdad_packet.py validate-packet --project-root . --execution-context .cdad/executions/exec-010-003-documentary-pilot-001/execution.json --request .cdad/packets/010-003-documentary-pilot-architect-draft-002/REQUEST.json --packet .cdad/packets/010-003-documentary-pilot-architect-draft-002/PACKET.md`
- El render `--route C` reprodujo la identificación recibida.

`python3 -B -m pytest --version` → `pytest 8.3.5`. El comando propuesto de T3 tiene runner disponible; no se ejecutaron sus pruebas ni la suite completa.

**Archivos modificados por esta sesión:** ninguno. **Commit:** ninguno.
