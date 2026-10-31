# Informe RED — 010-002 T8 (B1 y B2)

## Intake (ruta C) — validado antes de trabajar

| Comprobación | Resultado |
|---|---|
| Bloque de identificación único y sin mezcla con paquete inline | OK |
| `packet_id`, `contract.path`, `contract.sha256`, `execution_id` contra `REQUEST.json` y `PACKET.md` | Coinciden |
| `execution.json` | `schema_version: 2` (v2, ruta C admisible) |
| `cdad_packet.py validate-request` sobre `REQUEST.json` | `rc=0` |
| `cdad_packet.py render` vs `PACKET.md` | Byte a byte idéntico (`diff -u` vacío) |
| `render --route C` vs bloque de identificación del dispatch | Byte a byte idéntico |
| SHA-256 del contrato `docs/specs/010-002-documentary-role-integration/spec.md` | `0d630c49…81abc` — coincide |

No se cargaron skills de ciclo completo ni se leyó producto para derivar el oráculo.

## Archivos modificados

- `tests/test_010_002_documentary_role_integration.py` — **único archivo tocado**. 593 inserciones, 11 eliminaciones.
- Ningún archivo bajo `sources/`, `agents/`, `scripts/`, `skills/` ni `docs/` fue modificado.
- Los cambios preexistentes en `docs/.cdad-state.json`, la desviación I-10 y los evidencia untracked de tareas anteriores quedaron intactos y fuera del commit.

## Controles añadidos

### B1 — la vía nativa no promete rechazo mecánico

**Ubicación:** `tests/test_010_002_documentary_role_integration.py::TestDispatchDoctrine::test_native_adapters_do_not_claim_a_mechanical_guard` (línea 2209), con self-check en `_native_guard_detector_self_check` (línea 2123).

**Superficies observadas** (`ADAPTER_NATIVE_SURFACES`, línea 222):
- `sources/agents/adapters/opencode.md`
- `sources/agents/adapters/claude-code.md`
- `agents/cdad-orchestrator.md`
- `agents/claude-code/cdad-orchestrator.md`

**Extensión del detector existente:** `claims_new_mechanical_guard` (línea 1061) ahora resuelve la polaridad sobre la **cláusula que formula el rechazo**, no sobre cualquier negación de la ventana de 300 caracteres. Incorpora:
- `native_mechanism_region` (línea 966): localiza el ítem `- **Mechanism (native).**` de los adaptadores, y también encabezados/etiquetas equivalentes.
- `mechanical_guard_negated` (línea 1026): una negación de la guarda o del rechazo mecánico absuelve; una negación de la **sustitución silenciosa** no.
- `_is_external_only`: la descripción correcta del adaptador externo no se imputa a la vía nativa.

**Causa del RED hoy:** las cuatro superficies contienen la cláusula literal:

> `a required variant that is not published is rejected mechanically before launching the role work: fail closed, never substitute it silently by the generic agent.`

El `never` de la sustitución silenciosa ya no absuelve la promesa mecánica. El fallo lista las cuatro superficies, incluidas las dos generadas, de modo que una corrección solo en la fuente no pasa.

**Self-check (pasa):** positivo literal; positivo con `never substitute it silently`; negativos `no new mechanical guard is promised`, `is not rejected mechanically`, `is not dispatched mechanically`, `the mechanical guard is absent`; descripción del adaptador externo; selección estructural de la región nativa.

**Conservación:** después de la aserción de la promesa mecánica se exige la obligación procedimental de D4 (variante ausente + detención + obligación procedimental) y la prohibición de sustitución silenciosa.

### B2 — los deltas Odoo de rol están condicionados al producto o al diff

**Ubicación:** `tests/test_010_002_documentary_role_integration.py::TestOdooApplicability::test_odoo_role_deltas_are_conditioned_on_product_or_diff` (línea 1895), con self-check en `_odoo_delta_detector_self_check` (línea 1831).

**Superficies observadas (9):**
- `sources/roles/reviewer.md`, `sources/roles/implementer.md`, `sources/roles/test-writer.md` — bloque `<!-- cdad-section:odoo --> … <!-- /cdad-section -->`.
- `agents/cdad-{reviewer,implementer,test-writer}-odoo.md` y `agents/claude-code/cdad-{reviewer,implementer,test-writer}-odoo.md` — bloque `## Odoo stack delta (declared)`.

**Detección:** `odoo_section` / `odoo_stack_delta_region` (líneas 675 y 686), `unconditional_addon_battery` (línea 726) y `_has_applicability_condition` (línea 710), con `ROLE_BATTERY` (línea 650). Una condición vale solo si está en la **misma sección** y reúne marcador condicional + producto/diff/cambio/encargo + addon + relación de aplicación (verbo, cópula o acción). La mera cercanía de «documentary» sin regla no condiciona.

**Causa del RED hoy:** las nueve superficies declaran la batería de addon y ninguna cláusula de su sección la subordina al producto o al diff. La matriz de aplicabilidad vive en otra sección y no cuenta. El fallo lista las nueve superficies con un extracto cada una.

**Self-check (pasa):**
- «documentary» + batería sin regla → reporta.
- `only when the product or the diff touches addon code` → no reporta.
- `when the product is an addon` (cópula) → no reporta.
- `solo si el encargo modifica o verifica un addon` → no reporta.
- condición en otra sección → reporta («la tabla de aplicabilidad no es coherencia»).

## Ejecución y evidencia

### Comando 1

```sh
python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py \
  -k 'mechanical or odoo_applicability or delta'
```

**rc=1**

```text
2 failed, 1 passed, 26 deselected in 1.26s

FAILED ...::TestOdooApplicability::test_odoo_role_deltas_are_conditioned_on_product_or_diff
FAILED ...::TestDispatchDoctrine::test_native_adapters_do_not_claim_a_mechanical_guard
```

Selección: 3/29 tests (`--collect-only`: el control B2, el control B1 y el control previo `test_absent_variant_is_mechanical_external_and_procedural_native`, que sigue verde).

### Comando 2

```sh
python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py
```

**rc=1**

```text
2 failed, 27 passed in 39.20s

FAILED ...::TestOdooApplicability::test_odoo_role_deltas_are_conditioned_on_product_or_diff
FAILED ...::TestDispatchDoctrine::test_native_adapters_do_not_claim_a_mechanical_guard
```

Logs completos: `/tmp/opencode/red-k-final.log` y `/tmp/opencode/red-full-final.log`.

## Controles previos que siguen verdes (27)

**TestEngagement**
1. `test_documentary_procedure_uses_the_existing_fields_without_a_new_selector`
2. `test_explicit_editable_scope_and_stop_on_protected_overlap`
3. `test_six_role_boundaries_and_no_documentary_variant`

**TestOdooApplicability**
4. `test_addon_boundary_and_module_documentation`
5. `test_distributed_artifacts_carry_the_matrix`
6. `test_documentary_verifier_is_not_an_addon_test`
7. `test_producer_roles_matrix`
8. `test_review_coordination_memory_matrix_and_diff_prevalence`

**TestDispatchDoctrine**
9. `test_absent_variant_is_mechanical_external_and_procedural_native`
10. `test_every_selection_surface_derives_a_suffix_and_keeps_no_other_value_fallback`

**TestDistribution**
11. `test_documentary_odoo_journey_keeps_domain_and_write_frontier`
12. `test_generation_is_reproducible_and_promoted_matches_staging`
13. `test_isolated_install_distributes_corrected_surfaces_and_the_generic_journey`

**TestAgentBinding**
14. `test_agent_is_excluded_from_render_between_valid_requests`
15. `test_context_without_agent_is_rejected_on_validation_and_publication`
16. `test_contextual_contrast_rejects_a_new_intent_with_wrong_stack_agent`
17. `test_historical_without_both_fields_records_a_new_intent_without_destination_contrast`
18. `test_identical_repetition_after_stack_change_stays_idempotent`
19. `test_ordinary_publication_publishes_derived_agent_and_context`
20. `test_replacement_after_stack_change_rederives_current_stack`
21. `test_replacement_of_historical_successor_without_agent_rederives`
22. `test_static_role_contrast_rejects_foreign_agent_and_does_not_evaluate_stack`

**TestAgentBindingReception**
23. `test_reception_after_stack_change_keeps_the_static_contrast_only`

**TestAgentBindingWriteAheadFinalization**
24. `test_write_ahead_finalization_after_stack_change_completes_once`

**TestRequestSchema**
25. `test_schema_accepts_valid_current_and_historical_requests`
26. `test_schema_rejects_invalid_shape_unknown_keys_and_context_without_agent`
27. `test_schema_shape_is_distinct_from_cli_role_and_dispatch_contrast`

## Commit

- **Commit:** `58b0bcd7e589b08e46514dd4bfe04e00d73d7c01`
- **Mensaje:** `test(010-002): RED de B1 y B2 (guarda mecanica nativa y deltas Odoo condicionados)`
- **Alcance:** solo `tests/test_010_002_documentary_role_integration.py` (`git show --stat`: 1 file, 593 insertions, 11 deletions).
- `git status --porcelain -- tests/test_010_002_documentary_role_integration.py` → vacío (HEAD contiene la versión final).

## Límites y notas honestas

- **Oráculo:** derivado del contrato (D4/PC-09 para B1; PC-04/PC-05 para B2), del plan T8, del dictamen T8 (B1/B2) y del objective del paquete. No se derivó del texto bajo prueba.
- **Lectura estructural:** para localizar la región nativa y la sección Odoo generada se inspeccionaron únicamente marcadores estructurales — `- **Mechanism (native).**` en los adaptadores y `## Odoo stack delta (declared)` en los agentes generados—, no la prosa del producto.
- **Sin cambio de producto:** el RED exige corregir `sources/agents/adapters/opencode.md`, `sources/agents/adapters/claude-code.md`, `sources/roles/{reviewer,implementer,test-writer}.md` y regenerar con `make agents`. No se corrigió producto; según las condiciones del paquete, se reporta y se detiene.
- **Suite completa:** no ejecutada (política del paquete: la ejecuta quien cierra). Solo se ejecutó el módulo focalizado y la selección pedida.
- **Alcance B2:** además de las tres fuentes, el control observa los seis agentes `-odoo` promovidos, para no aceptar una corrección que deje los agentes generados con el texto viejo.
- **Límite del detector:** la polaridad es una regla estructural (negación que gobierna la guarda/rechazo mecánico), no análisis semántico general. No acredita fidelidad semántica ni conducta de modelos (PC-13).
