## Auditoría de tests — 019-003

**Resultado:** los verificadores existentes aportan protección de distribución, integridad y separación, pero no prueban por sí solos la suficiencia semántica de la estrategia ni la coherencia de las instrucciones modificadas. Esas obligaciones requieren la revisión independiente contextual prevista en la especificación.

Esta es una **auditoría parcial para decisión del orquestador**: el alcance de lectura del paquete autoriza la especificación 019-003 y `tests/`, pero no `systemPatterns`, el inventario vivo ni la guía documental citada en el propio paquete. No se leyeron esos archivos ni implementación. Tampoco se ejecutaron tests: los nombres y cuerpos identificados son verificadores existentes, no evidencia de una corrida verde.

### Mapa por promesa

**A. El dueño puede aprobar una estrategia suficiente — PC-1 y PC-2**

- **Evidencia existente identificada:** `tests/test_010_001_documentary_contracts.py::test_the_norm_separates_structural_control_from_semantic_review` y `::test_the_norm_requires_contrast_with_sources_and_owner_acceptance` protegen distinciones relacionadas. No establecen que las instrucciones candidatas permitan valorar cada promesa, método, criterio, evidencia y límite, ni que preserven correctamente la exención de revisión.
- **Disposición:** **Mantener**, sujeto a confirmar su aplicabilidad a los cambios efectivos.
- **Brecha y consecuencia:** sin revisión contextual de la guía, plantilla y consumidores de revisión, el dueño podría aprobar una estrategia insuficiente aunque un test encuentre las palabras esperadas.
- **Selección propuesta:** revisión independiente atribuible de PC-1 y PC-2; no añadir un test de coincidencia textual como prueba de suficiencia.

**B. La producción sigue el compromiso aprobado sin controlar la aceptación — PC-3 y PC-4**

- **Evidencia existente identificada:** `tests/test_010_002_documentary_role_integration.py::test_six_role_boundaries_and_no_documentary_variant` y `::test_explicit_editable_scope_and_stop_on_protected_overlap`; además, `tests/test_role_packet_render.py::test_p3_forbidden_role_scopes_are_rejected`.
- **Disposición:** **Mantener**. Los controles existentes cubren partes distintas de las fronteras; no se identifica todavía una protección faltante que justifique duplicarlos.
- **Brecha y consecuencia:** sin examinar las instrucciones candidatas de enrutamiento, handoffs y flujo ligero, podría dirigirse trabajo semántico a un RED fabricado, omitirse una de las verificaciones mixtas o permitirse cambiar criterios protegidos.
- **Selección propuesta:** revisión contextual de las tres rutas de PC-3 y de la protección de PC-4. Reutilizar controles de separación aplicables según las superficies efectivamente modificadas; no inventar un test ejecutable para fidelidad semántica.

**C. La aceptación refleja la evidencia y la entrega coherente — PC-5 y PC-6**

- **Evidencia existente identificada:**
  - `tests/test_role_packet_render.py::test_p1_p3_each_pair_matches_public_instruction_sources_byte_for_byte` y `::test_p2_validate_packet_rejects_tampered_body_metadata_and_hash`: composición e integridad de paquetes.
  - `tests/test_cdad_generate.py::test_postcondition_2_identical_runs_are_byte_identical`: determinismo de generación.
  - `tests/test_010_001_documentary_contracts.py::test_generated_and_promoted_agents_of_both_runtimes_carry_the_obligations` y `::test_isolated_install_distributes_the_reference_with_source_bytes`: protección de distribución relacionada.
  - `tests/test_010_003_documentary_pilot.py::test_semantically_defective_candidate_is_structurally_accepted`: contraejemplo explícito del límite de un control estructural.
- **Disposición:** **Mantener** cada verificador citado. Igualdad de bytes y distribución son protección de entrega, no prueba del significado ni de que la evidencia requerida exista.
- **Brecha y consecuencia:** sin revisar las instrucciones efectivas y contrastar los insumos históricos protegidos, podría acreditarse una aceptación con evidencia ausente o contradictoria, o distribuirse coherentemente una instrucción semánticamente incorrecta.
- **Selección propuesta:** revisión independiente de PC-5 y PC-6; ejecutar una selección proporcional de generación, paquetes y distribución una vez conocidas las superficies modificadas. Comparar candidato y salidas pertinentes, y contrastar los insumos históricos autorizados.

### Mantenimiento, RED e inventario

No se propone **Añadir**, **Extender**, **Sustituir**, **Consolidar** ni **Retirar** tests en este momento: no se identificó una promesa ejecutable pendiente con una diferencia de protección demostrada frente a los verificadores existentes. Si la implementación modifica un mecanismo de entrega y revela una brecha observable concreta, corresponde completar la auditoría antes de decidir su test; un sustituto de comportamiento vigente pertenecería a POST-AUDIT, no a RED.

No puedo determinar adiciones necesarias al inventario —nodeid, capacidad, contrato y procedencia— sin leerlo. El objetivo menciona `docs/suite-maintenance.md` y el inventario, pero ambos quedan fuera del `read_scope` explícito. También queda pendiente la lectura de la guía documental que el paquete ordena leer fuera de ese alcance. **Solicito al orquestador resolver esa contradicción y autorizar los insumos necesarios**, en lugar de ampliar el alcance silenciosamente.

### Evidencia de esta tarea

- **Archivos modificados:** ninguno.
- **Comandos:** `cdad_packet.py validate-request`, `validate-packet` y `render --route C`, con las rutas declaradas en la identificación. Ambas validaciones finalizaron correctamente; el render coincidió con la identificación recibida.
- **Tests ejecutados:** ninguno. **Suite completa no realizada**; la tarea es AUDIT y no la autoriza.
- **Commit:** ninguno.
- **Separación:** no se leyó código de implementación. La búsqueda de archivos de tests quedó truncada, por lo que el inventario de verificadores no se presenta como exhaustivo.