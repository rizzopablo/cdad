## AUDIT 019-003 — informe parcial para el orquestador

**Estado: bloqueado para completar el AUDIT.** El paquete es válido, pero la referencia normativa documental `skills/cdad-cycle/references/documentary-contracts.md` queda fuera de su `read_scope`, limitado a `docs/` y `tests/`. El encargo indica detener esa porción si ocurre esta contradicción. No leí la referencia ni busqué una copia alternativa.

Solicito un paquete corregido que autorice expresamente esa referencia. Hasta entonces, las selecciones siguientes son **provisionales**, no un AUDIT final listo para aprobación.

### Mapa provisional por promesa

**A — Estrategia suficiente para aprobación (PC-1 y PC-2).** Mantener:

- `tests/test_010_001_documentary_contracts.py::TestPromiseC::test_the_norm_separates_structural_control_from_semantic_review`
- `tests/test_010_001_documentary_contracts.py::TestPromiseC::test_the_norm_requires_contrast_with_sources_and_owner_acceptance`

Aportan controles relacionados con la separación entre estructura y revisión semántica y con el contraste de fuentes. No prueban que la guía candidata permita decidir la suficiencia de cada estrategia ni que preserve la exención de revisión. **Sin revisión contextual independiente**, el dueño podría aprobar una estrategia insuficiente aunque aparezcan las palabras esperadas. Selección provisional: revisión independiente de guía, plantilla y consumidores de revisión.

**B — Producción sin control de su propia aceptación (PC-3 y PC-4).** Mantener:

- `tests/test_010_002_documentary_role_integration.py::TestEngagement::test_six_role_boundaries_and_no_documentary_variant`
- `tests/test_010_002_documentary_role_integration.py::TestEngagement::test_explicit_editable_scope_and_stop_on_protected_overlap`
- `tests/test_role_packet_render.py::TestRoleScopes::test_p3_forbidden_role_scopes_are_rejected`

Protegen partes distintas de las fronteras. **Sin revisar las instrucciones candidatas**, podría fabricarse un RED para trabajo semántico, omitirse una verificación mixta o permitirse cambiar criterios protegidos. Selección provisional: revisión contextual de las tres rutas y de los criterios protegidos; reutilizar controles aplicables según las superficies modificadas.

**C — Aceptación según evidencia y entrega coherente (PC-5 y PC-6).** Mantener:

- `tests/test_role_packet_render.py::TestPublicTask2Surface::test_p1_p3_each_pair_matches_public_instruction_sources_byte_for_byte`
- `tests/test_role_packet_render.py::TestPacketIntegrity::test_p2_validate_packet_rejects_tampered_body_metadata_and_hash`
- `tests/test_cdad_generate.py::TestDeterministicGenerator::test_postcondition_2_identical_runs_are_byte_identical`
- `tests/test_010_001_documentary_contracts.py::TestPromiseD::test_generated_and_promoted_agents_of_both_runtimes_carry_the_obligations`
- `tests/test_010_001_documentary_contracts.py::TestPromiseD::test_isolated_install_distributes_the_reference_with_source_bytes`
- `tests/test_010_003_documentary_pilot.py::test_semantically_defective_candidate_is_structurally_accepted`

Son protección de integridad, distribución o del límite de los controles estructurales; no acreditan fidelidad semántica. **Sin revisión de las instrucciones efectivas y los insumos históricos protegidos**, podría acreditarse evidencia ausente o distribuirse fielmente una instrucción incorrecta. Selección provisional: revisión independiente, comparación de candidato y salidas pertinentes, contraste histórico y controles de entrega proporcionales al diff.

Cada verificador listado tiene una única disposición provisional: **Mantener**. No se propone alta, extensión, sustitución, consolidación ni retiro: aún no se identificó una diferencia de protección ejecutable que lo justifique. Cualquier sustituto de comportamiento vigente correspondería a POST-AUDIT con sus evidencias, no a RED.

### Inventario y límites

`docs/suite-maintenance.md` declara el comando `python3 scripts/cdad-suite.py validate`, el inventario y el mapa indicados en el encargo. Las asignaciones existentes de los módulos citados apuntan a contratos anteriores: 010-001, 010-002, 010-003, 003-001 y 004-001, según el módulo. Son asignaciones principalmente a nivel de módulo; **no acreditan por sí solas protección semántica de 019-003**.

El mapa consultado conserva su piloto histórico y registros `VERIFY`; no encontré en lo leído una genealogía aplicable a una sustitución de los verificadores propuestos aquí. No hay cambios de tests ni delta de inventario que materializar. No se ejecutó `validate`: el mantenimiento con delta vacío asigna esa medición a otros responsables cuando corresponda.

### Evidencia de la sesión

- `cdad_packet.py validate-packet` terminó sin salida ni error; `render --route C` reprodujo la identificación recibida.
- Se consultaron la especificación, el informe parcial, `systemPatterns`, el mantenimiento de suite, el inventario, el mapa y referencias de tests autorizados.
- No se ejecutaron tests ni la suite completa; los verificadores identificados **no son evidencia de una corrida verde**.
- Archivos modificados: ninguno. Commit: ninguno.
- No se leyó código de implementación.