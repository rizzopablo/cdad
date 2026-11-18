Corrección hecha y commiteada. Cambié una sola referencia, la plantilla de borrador de spec, y no toqué tests ni otros archivos.

**Packet:** la validación de la ruta C con `cdad_packet.py validate-packet` dio rc=0.

**Commit:** `54b40d76`, que modifica solo `skills/cdad-cycle/references/handoff-prompts.md` (2 inserciones, 2 borrados).

```diff
-Task: produce the spec draft for "<feature-name>" based on the brainstorm.
+Task: produce the spec draft for "<feature-name>" based on the owner's recoverable dialogue decisions and, only if one was consulted, the consultation summary.
 
 Context:
-1. Brainstorm summary: <paste summary>
+1. Owner dialogue decisions (recoverable from the discovery dialogue): <paste decisions>; consultation summary (only if the architect was consulted): <paste summary or "none">; do not require a brainstorm summary that does not exist
```

**Pruebas:**
- `pytest` sobre los tests que referencian el handoff dio 76 passed: `test_006_002_u6_context_discipline`, `test_packet_prepare`, `test_010_002_documentary_role_integration`, `test_005_005_t2_docs_policy`, `test_006_006_u3_review_route_and_gate` y `test_014_001_suite_evidence_defaults`.
- `tests/validate-consistency.sh` da 182 aciertos y 1 fallo: «F011: scripts/validate-subagents.sh (active profile) → FAIL». Con la versión anterior del archivo (`HEAD~1`) falla igual, así que no viene de este cambio. No investigué por qué falla `validate-subagents.sh`.
- No corrí la suite completa. La selección fue focal más `validate-consistency.sh`.

En el árbol quedan sin trackear tres archivos que ya estaban: `docs/specs/019-002-effective-discovery-instructions/recovery-contextual-review-001.md`, `recovery-contextual-review-002.md` y `recovery-semantic-fix-001.md`.