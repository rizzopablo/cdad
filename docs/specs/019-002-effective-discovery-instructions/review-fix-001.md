Los cuatro hallazgos bloqueantes de `review-001.md` están corregidos y los 86 tests de la selección pasan. El commit es `974d55d5`. No toqué tests ni desplegué nada. Validé el paquete por la ruta C y su render canónico coincide byte a byte con el recibido.

## Qué cambié
1. **Contexto atribuido (hallazgo 1):**
   - **Architect:** en `stage-2-specification.md`, `handoff-prompts.md` y `re-entry.md` ahora recibe el contexto completo y cualificado del diálogo, no un resumen. Incluye las entradas superadas marcadas como tales, con su autoridad y sus vínculos de supersesión.
   - **Reviewer:** recibe el mismo registro completo. En la ruta por paquete va como `--input docs/specs/<feature>/discovery.md=Dialogue context`; en la ruta legacy se pega en el prompt.
2. **Procedencia de las correcciones (hallazgo 2):** añadí la sección «Dialogue record convention» en `stage-2-specification.md`. Cada entrada lleva:
   - identificador recuperable de la fuente o del mensaje;
   - autoridad de quien habla;
   - fragmento afectado;
   - siguiente acción.
   Una corrección es una entrada nueva con `supersedes`, la entrada reemplazada recibe `superseded-by` y nunca se borra ni se reescribe. Una corrección sin autoridad se registra como declaraciones en conflicto. `re-entry.md` y `sources/roles/orchestrator.md` remiten a esa sección.
3. **Ruta sin consulta (hallazgo 3):** si el diálogo ya resolvió las decisiones y no hay incertidumbre consecuente, se omite la consulta pero no la comprobación R1–R5. Se registra con R4 como «no consultation: no consequential uncertainty» y sigue el mismo handoff. Lo reflejé en `stage-2-specification.md`, `re-entry.md` y el orchestrator.
4. **Inferencia de cierre (hallazgo 4):** en `state-detection.md`, la fila «Memory Bank updated, feature merged» ahora dice que es solo una inferencia de trabajo terminado. El estado `idle/null` existe únicamente como resultado de una transición de cierre registrada en state, y hay que verificarlo ahí.

También reconcilié `skills/cdad-cycle/SKILL.md:69`: «Socratic brainstorm» pasó a «targeted technical consultation».

## Comandos y resultados
- `python3 -I scripts/cdad_packet.py render --request <REQUEST.json>` seguido de `cmp` con `PACKET.md`: rc 0 y `SAME`.
- `make agents`: regeneró `agents/cdad-orchestrator.md` y `agents/claude-code/cdad-orchestrator.md`.
- `pytest` sobre `test_019_002_discovery_delivery`, `test_019_002_resting_orientation`, `test_006_005_u7_scribe_role_report`, `test_005_007_t4_architect_report_materialization`, `test_015_001_frozen_reception`, `test_cdad_generate`, `test_role_packet_render` y `test_role_packet_consumers`: 60 passed en 198.92 s.
- `pytest` sobre `test_006_006_u3_review_route_and_gate` y `test_006_006_u5_exemption_record`: 26 passed en 31.88 s.

## Límites
- No ejecuté la suite completa ni `make validate`.
- PC-4 y PC-11 (ejercicio observado) y la evidencia de publicación congelada siguen pendientes para T3. No los doy por cubiertos.
- `docs/.cdad-state.json` ya estaba modificado antes de empezar y quedó fuera del commit.

Archivos en el commit: `skills/cdad-cycle/SKILL.md`, `skills/cdad-cycle/references/handoff-prompts.md`, `skills/cdad-cycle/references/re-entry.md`, `skills/cdad-cycle/references/stage-2-specification.md`, `skills/cdad-cycle/references/state-detection.md`, `sources/roles/orchestrator.md`, `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`.