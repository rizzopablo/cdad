T6 (producción semántica de instrucciones, sin RED inventado) está hecha y commiteada como `d415cc1b8b65f5280dffe0bb839207f906aace72`. No hubo nada que reportar de README: no lo toqué y no apareció ningún fallo base de sus tests.

**Qué cambió, por promesa**
- **PC-1/PC-2 (orquestador):** en `sources/roles/orchestrator.md` agregué la regla "Discovery dialogue".
  - El orquestador es el único interlocutor: puede leer código, ejecutar el producto e investigar.
  - Consulta al arquitecto cuando la incertidumbre lo justifica, sin esperar a la preparación para redactar.
  - Los hallazgos técnicos que fundan una decisión se registran con atribución.
  - Respuestas parciales, silencio y defaults no aceptados no son consentimiento. La preparación para redactar no es aprobación.
- **PC-3:** la regla de "no auto-reparar" ahora admite una corrección formal trivial en una presentación corregida aparte, con atribución. El original, su recibo y la copia del diario quedan intactos. La única prohibición dura es escribir o corregir producto y tests.
- **Arquitecto:** `sources/roles/architect.md` y el packet `architect-brainstorm.md` pasan de "preguntar al usuario" a entregar un `role-report` de consulta. El borrador de la especificación se hace solo con decisiones realmente tomadas, y las dudas sin resolver quedan listadas como abiertas o bloqueantes. La descripción en `scripts/cdad-generate.py` quedó alineada.
- **PC-6 (referencias):**
  - **`stage-1-discovery.md`:** quité "YOU do not do the discovery".
  - **`stage-2-specification.md` y `re-entry.md`:** el brainstorm re-entra con criterios sobre el informe y las decisiones. La re-entrada del borrador apunta a la revisión independiente o exención que ya existen, sin rediseñarlas.
  - **`handoff-prompts.md`:** el prompt de consulta devuelve `DONE. <role-report>` en lugar de `READY FOR DRAFT`.
  - **`SKILL.md`:** una línea nueva sobre el diálogo.
  - **`odoo-architect/SKILL.md`:** solo el enrutamiento de preguntas.
  - **`CDAD_metodologia.md`:** §6.2 actualizado.
- **PC-5 (cierre):** `stage-5-merge.md` y `feature-handoff.md` describen el reposo legítimo (`idle`/`null`). `done`/`null` se diagnostica antes de abrir la siguiente unidad.

Quedaron intactos el enrutamiento por método de verificación, los bytes de los packets congelados y la separación entre metodología instalada y producto.

**Comandos y resultados**
- `make agents`: 12 archivos por runtime, sin errores. El delta generado son solo las 6 salidas de `agents/` (architect, architect-odoo y orchestrator, en opencode y claude-code): +40/−10 líneas. `build/staging` no aparece en el estado de git.
- Generación, render y recepción congelada: `pytest -q tests/test_cdad_generate.py tests/test_role_packet_render.py tests/test_role_packet_consumers.py tests/test_015_001_frozen_reception.py tests/test_006_006_u3_review_route_and_gate.py tests/test_006_006_u5_exemption_record.py` dio 67 passed.
- Consumidores de los archivos tocados: `tests/test_005_005_t2_docs_policy.py`, `test_006_002_u2/u4/u6`, `test_006_003_u5p`, `test_006_004_u4`, `test_010_002`, `test_010_004_t4_red`, `test_014_001`, `test_packet_prepare` dieron 92 passed.
- Suite completa: **no realizada**. Corresponde al cierre del epic. Corrí selección focal más consumidores, y la conformidad semántica queda para la revisión independiente T7.

**Alcance del commit:** 19 archivos, +74/−34, todos dentro del alcance de producción de instrucciones más `agents/**` regenerado y `CDAD_metodologia.md`. No edité tests, README ni registros en `docs/`.

Quedan sin commitear los archivos que ya estaban modificados o sin seguimiento antes de empezar, ninguno mío:
- `docs/.cdad-state.json`
- `docs/specs/008-002-suite-by-capability/suite-inventory.json`
- `docs/specs/019-002-effective-discovery-instructions/recovery-delivery-green.md`
- `docs/specs/019-002-effective-discovery-instructions/recovery-orientation-green.md`
- `docs/specs/019-002-effective-discovery-instructions/recovery-orientation-red.md`

**Límite:** la coherencia semántica real (PC-1 a PC-3 y PC-6) la establece la revisión contextual independiente T7, no estos tests mecánicos.