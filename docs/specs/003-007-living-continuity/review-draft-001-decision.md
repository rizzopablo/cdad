# Decisión del orquestador sobre review-draft-001 (003-007)

Bajo la delegación HITL de epic-003. Todos los bloqueantes se aceptan.

| Hallazgo | Decisión | Cómo entra |
|---|---|---|
| BL-1 cableado sin clases | **Aceptado** | T4 amplía alcance: el bloque "Continuity wiring" de `sources/roles/orchestrator.md` dice explícitamente qué se declara `living` (ledgers, `debt.md`, Memory Bank, borradores de cierre/enmienda) y qué `contract` (spec/plan aprobados, `docs/cdad-policy.json`, state con `fields` de autoridad). Postcondición nueva en P10. Además T1 pone el ejemplo con clases en `continuity.md`. |
| BL-2 test RU-2 cambia por diseño | **Aceptado** | T2 declara la modificación de la faceta `checkpoint` de `tests/test_003_006_t4_ru2_refused_write.py` (la hace el test-writer en el RED de T2, con trazabilidad a P5); la faceta `begin` divergente queda intacta. T2 escribe qué sigue detectando `_detect_split_brain`. |
| BL-3 modos de fallo de `fields` | **Aceptado** | P4 extendida: `fields` sobre archivo no JSON → `rc≠0` al escribir; proyección vacía (ninguna clave presente) → `rc≠0` al escribir. Fijado en el RED de T1. |
| R-1 puente legado por comparación | **Aceptado** (reemplaza D6/D7 blanket) | Cuerpo legado sin `class`: digest igual → se verifica como `contract`; distinto → se informa `changed` con `legacy: true` (no bloquea). Resuelve el punto 4 hoy y protege specs cerradas que sigan intactas. Excepción documentada: la clase de legado no está congelada. |
| R-2 integridad de `stage_history` | **Aceptado como deuda** | D1 declara el residuo; entra en `debt.md`. |
| R-3 fixtures autocontenidos | **Aceptado** | P7 se prueba con copias de stores en tmp; la verificación sobre los stores reales queda como observable de T3. |
| R-4 ambigüedad D9 | **Aceptado** | El texto incluye el ejemplo: una tarea del plan cuyo RED y GREEN son despachos separados cumple la regla. |
| R-5 quitar `--optimus` | **Rechazado** | `optimus` es el perfil del proyecto y la instalación va a una raíz aislada (`CDAD_INSTALL_ROOT`); no toca el perfil del dueño. Todas las adopciones v1–v6 usaron `--optimus`. |
| Abstención: `reconcile` tras append | **Aceptado** | El RED de T2 cubre `reconcile` de un paquete cuya clave ya no es el head. |
