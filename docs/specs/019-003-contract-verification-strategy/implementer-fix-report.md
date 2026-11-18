## Informe del implementer: review-fix 019-003 (route C)

**Commit:** `cc4465d0` · `refactor: align stage 2/3 gates and lightweight route with review-001 (019-003)`. Local, sin publicar. Lo amendé una vez para usar el prefijo literal `refactor:` que exige `re-entry.md` para la subfase review-fix.

**Archivos modificados (4, solo producto):**
- `skills/cdad-cycle/references/stage-3-tdd.md`: tabla de GREEN, paso 7, loop y gate. Las promesas semánticas llegan a Stage 4 con revisión pendiente y sin RED fabricado. Las mixtas exigen ambas familias. La aceptación sigue siendo posterior a la revisión independiente.
- `skills/cdad-cycle/references/stage-2-specification.md`: gate de especificación con dos alternativas: revisión realizada (`plan-review.md`, bloqueantes resueltos o descartados) o exención registrada con sus cuatro campos. La exención no cuenta como revisión ejecutada ni como evidencia de suficiencia.
- `skills/cdad-cycle/SKILL.md`: diagrama de etapas y gates 2→3 y 3→4 alineados con las tres rutas.
- `skills/cdad-spec-and-test/SKILL.md` (flujo ligero): reglas 2 y 4, diagrama, cierre y tabla de gates. Las mixtas requieren tests para la parte ejecutable y revisión contextual independiente para la semántica.

**Decisiones mías:**
- No toqué `sources/`, `packets/`, `scripts/` ni tests. Por eso no regeneré `agents/`: los agentes se componen desde `sources/`, y esas fuentes ya eran coherentes con el enrutamiento.
- Dejé `handoff-prompts.md:438` («paste output with all tests green») sin cambios. Es una plantilla de evidencia de un contexto ejecutable.

**Validación del paquete:** `validate-request` rc=0, `validate-packet` rc=0, el PACKET.md en disco es idéntico al render canónico, `render --route C` coincide con el bloque de identificación y `validate-state` dice VALID. El hash del contrato coincide.

**Pruebas (comandos exactos y resultados):**
1. `python3 -m pytest -q` sobre 15 archivos (006_006 u2–u5, 004_003 t2/t5, 013_001, 005_005 t2/t4, cdad_generate, role_packet_render/consumers, 010_001–003): **155 passed**.
2. Segunda tanda sobre 29 archivos que leen los textos editados: **217 passed, 2 failed**. Los fallos son `test_005_006_t6_owner_reviewfix.py::test_hallazgo_a1_no_install_root_in_wiring` y `…a2…`, por `README.md:89` y `:125`. Reproducen **igual en el HEAD 4a1dc07c** (worktree desechable), y `README.md` no tiene cambios míos. Son preexistentes.
3. `bash tests/validate-consistency.sh`: 182 PASS, 1 FAIL (`F011`). `scripts/validate-subagents.sh` falla por `install.sh --check` (drift de la instalación desplegada). **También falla en el HEAD.**
4. `bash tests/validate-odoo-specialization.sh`: **68 PASS, 0 FAIL**.
5. Tras el amend: `test_006_006_u3`, `test_cdad_generate`, `test_role_packet_render`, `test_005_006_t2_intake`: **45 passed**.

**Suite completa no realizada.** Corrí la selección focal: todos los tests que leen los archivos editados, más los dos scripts de validación. No corrí la suite completa. Esto es proporcional a un cambio que solo toca textos canónicos; la suite completa queda como deuda explícita de cierre de epic.

**Sin tocar:** `install.sh` y despliegue. `docs/.cdad-state.json` sigue modificado sin commitear: lo escribió la preparación del paquete, no yo.