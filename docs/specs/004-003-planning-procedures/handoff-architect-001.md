# Handoff legacy identificado: architect 001 (004-003)

Adenda 2026-10-05 para el próximo despacho o re-entry (no altera retrospectivamente
el encargo ya ejecutado): incorporar `efficient-orchestration-requirements.md`
de este directorio al discovery/spec/plan. Es una decisión de alcance del usuario;
requiere armonizar los procedimientos y gates mediante la spec. Si ya existen
borradores, presentar solo el delta necesario y conservar el trabajo válido.

Discovery y borrador de spec y plan para 004-003-planning-procedures (epic-004-single-source-planning). Sos el architect: solo lectura. Entregá los borradores en tu respuesta final; el orquestador los materializa y el dueño los aprueba.
Fuentes obligatorias:
 - docs/epics/epic-004-single-source-planning/plan.md: la sección de 004-003 y los requisitos R12, D8 y los asignados a 004-003;
 - planning-contract-draft.md, el procedimiento a incorporar;
 - c0-architect-report-2026-09-24.md: D8, la revisión de borradores de plan con un contract-kind nuevo, y la fuente canónica de orquestación;
 - c0-amendment-supervised-autonomy-2026-09-24.md;
 - execution.md;
 - docs/specs/004-002-project-execution-bootstrap/: spec.md, debt-second-look.md, supervision-record.md (lecciones de T7);
 - docs/adr/ADR-011 y ADR-012;
 - docs/activeContext.md y docs/progress.md;
 - skills/cdad-cycle/references/ y skills/cdad-epic/ si existe.
Contexto vigente, decisiones del dueño:
 - CDAD debe servir más allá de Python: Go con tests junto al código, y ciclos que no producen código (documentos, configuración, multimedia).
 - Los límites mecánicos son moderados; la disciplina es instrucción más auditoría.
 - Se prefiere un MVP con camino feliz viable: lo que no lo rompe va a deuda priorizada.
 - La deuda de 004-002 está en debt-second-look.md. F4 (scopes del test-writer con tests co-ubicados o exactos) es de prioridad alta: evaluá si 004-003 la necesita para su camino feliz.
 - Pendientes heredados: el principio de generalidad y la decisión de modelos de los agentes de proyecto.
Entregables:
 (1) Discovery breve: problema, usuarios, qué falta hoy (citá archivo:línea) y qué NO entra.
 (2) Borrador de spec en el formato de docs/specs/004-002-project-execution-bootstrap/spec.md: postcondiciones PD-n verificables y criterios de aceptación, alcance MVP explícito y lo diferido como deuda.
 (3) Borrador de plan por tareas T1..Tn, cada una con su RED verificable y su dependencia.
 (4) Decisiones que tiene que tomar el dueño, con tu recomendación.
 (5) Riesgos.
Sé concreto y proporcional: el MVP mínimo que cierra el objetivo de la epic, no un diseño exhaustivo. Como máximo unas 250 líneas. Si algo te es denegado, detenete y reportalo. No leas tests/.sensitive-patterns.local.
