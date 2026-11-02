# Memory Bank drafts — 011 y 012

Drafts entregados por el scribe (sin commit; aprobacion del dueno, materializacion del orquestador).

## Draft 1 — docs/activeContext.md
Dos entries nuevas (2026-11-01): 012-installer-ignore-pycache y 011-begin-unpublished-packet-wedge. Texto completo en la sesion del scribe; resume:
- 012: install.sh +29/-1 (935328d8), is_cache_artifact_path() por forma de ruta aplicado en sync_skill_to, check_skill_tree y count_tree_files, mas poda de registros stale. 4 tests (887c057c), PC-4 endurecido (4241e337). Review 1 B cerrado por mutacion; 41 passed. Deuda F2/F3/suite.
- 011: cdad_continuity.py +17/-2 (87a16432), discriminador schema_version==2, rechazo previo a escritura con diagnostico accionable. 2 tests (fb743245). Review 0 B, 116 passed focal + 194 barrido. Deuda F1/F2/seguimientos 2-5.

## Draft 2 — docs/progress.md
- Nuevo bullet de Despliegue: 011 y 012 NO desplegadas; lo instalado es del epic 010 (a42f2a20). Redesplegar es decision del dueno. VERIFICADO por el orquestador: ./install.sh --check -> DRIFT en cdad_continuity.py en los tres runtimes.
- Linea en In progress y dos entries nuevas al tope de Done.

## Draft 3 — ADR
Ninguno. 011 aplica ADR-038; 012 aplica ADR-002. Confianza media: el reviewer de 011 no contrasto formalmente contra docs/adr/.

## Carry-forward (R6)
Suite completa no corrida (ambas); F1 y F2 de 011; F2 y F3 de 012; limpieza retroactiva; seguimientos 2-5. Ninguno toca una promesa comprometida.
