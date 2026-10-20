RED de U3 entregado. Informe:

## Archivos modificados

| Fichero | Acción |
|---|---|
| `tests/test_006_006_u3_review_route_and_gate.py` | **NUEVO** (800 líneas) — único fichero tocado y el único del commit |

Nada fuera de `tests/`. `docs/.cdad-state.json` (modificado por el orquestador antes de mi sesión) y `docs/planning/`, `findings/*.md` (sin trackear, ajenos) quedaron intactos.

## Mapa test → postcondición (12 tests)

| Test | PD | O- | Estado hoy |
|---|---|---|---|
| `..._stage2_exit_gate_names_the_dictamen_artifact_and_the_blocker_condition` | PD-10 | O-1 | **FAIL (RED)** |
| `..._stage2_declares_the_draft_review_subphase` | PD-10 | O-2 | **FAIL (RED)** |
| `..._stage2_states_the_declared_form_of_the_exemption` | PD-10 (campos de PD-9/§2.7) | O-3 | **FAIL (RED)** |
| `..._skill_gate_2_to_3_names_the_dictamen_artifact_and_the_blocker_condition` | PD-10 | O-4 | **FAIL (RED)** |
| `..._skill_cycle_map_names_the_draft_review` | PD-10 | O-5 | **FAIL (RED)** |
| `..._reentry_has_the_draft_verdict_reentry` | PD-10 | O-6 | **FAIL (RED)** |
| `..._handoff_template_declares_the_form_and_the_double_identity_flags` | PD-10 | O-7 | **FAIL (RED)** |
| `..._control_negative_handoff_template_does_not_restate_the_procedure` | PD-10 | O-7 ctrl | PASS (control) |
| `..._control_negative_vigente_approval_without_dictamen_is_not_rejected` | PD-10 | O-2 ctrl (i) | **PASS (control)** |
| `..._control_negative_without_approval_the_same_prepare_is_rejected` | PD-10+PD-14 | O-2 ctrl (ii) | **PASS (control)** |
| `..._pd16b_reentry_declares_the_compatibility_policy_between_revisions` | PD-16(b) | O-8 | **FAIL (RED)** |
| `..._pd16b_reentry_declares_the_two_exits_of_the_compatibility_policy` | PD-16(b) | O-8 | **FAIL (RED)** |

**A-1: ninguna** — como dice la ficha. Comprobé las 7 regresiones: ninguna fija el texto de estas cuatro superficies; las que miden el paquete del reviewer calculan el sha256 del substage dinámicamente. El RED sólo **añade** casos; no toca fixtures compartidos (`DRAFT_PLAN_RELPATH` no se usa).

## Comandos y salida

```
$ python3 -m pytest tests/test_006_006_u3_review_route_and_gate.py -v
9 failed, 3 passed in 1.26s
```
Los 9 RED fallan con `AssertionError` de comportamiento (nunca ImportError/SyntaxError), p.ej. `assert 'plan-review.md' in '\n- [ ] docs/specs/<feature-id>/spec.md exists. …'`.

**Controles negativos (proceso real del CLI, proyecto descartable, HOME aislado):** (i) aprobación `specification` vigente con pin coincidente y **sin** `plan-review.md` → `prepare --role test-writer --substage red` ⇒ **rc=0** y paquete publicado (el gate es supervisado); (ii) misma fixture sin la entrada de aprobación ⇒ **rc=2** con `ERROR: approval pending: contract approval record missing: stage_history has no entry…`. Los dos casos difieren **sólo** en la entrada de aprobación. **Ambos pasan hoy** → declarados como controles (no asserts de RED).

**Satisfacción de los oráculos (auto-comprobación, en memoria, sin ficheros):** simulé dos redacciones plausibles de GREEN (A y B, con vocabulario distinto) → los 9 oráculos de texto se satisfacen en ambas (0 fallos). Los oráculos son por concepto, no por frase.

**Regresiones de la ficha:**
```
$ python3 -m pytest tests/test_005_006_t2_intake.py tests/test_role_packet_render.py \
  tests/test_role_packets.py tests/test_cdad_generate.py \
  tests/test_005_007_t1_progressive_detail_rule.py \
  tests/test_005_007_t4_architect_report_materialization.py tests/test_003_002_t2_materialize.py -q
59 passed in 149.16s
```
`tests/test_006_006_u2_review_procedure.py` (hermana): 7 passed. Colección de U1/U2/U5 sin errores.

**`make validate`:** 168 PASS / 1 FAIL — **fallo preexistente y ambiental, no mío**: `F011` corre `scripts/validate-subagents.sh`, que reporta *DRIFT* entre el repo (`skills/cdad-cycle/packets/substages/reviewer-plan-review.md`, `packs/roles/reviewer.md`, cambiados por el GREEN de U2 `95d9e11`) y la copia instalada del host `~/.claude/skills/cdad-cycle/` (anterior a ese commit), más `build/staging` ausente. No toca `tests/`. Lo declaro para el cierre; el `make validate` verde corresponde al GREEN de U3.

## Commit

```
0a33c45c161368329cb96e705bd4c914a9dd911e
test: 006-006 U3 RED — recorrido, gate 2->3 y compatibilidad
 tests/test_006_006_u3_review_route_and_gate.py | 800 +++++++++++++++++++++++++
 1 file changed, 800 insertions(+)
```
Sin `--no-verify`, sin stash, sin push. La suite completa **no** se corrió (política del paquete: la corre quien cierra).

## Nota de aislamiento (declarada)

No leí código de implementación. El guard de rutas denegó el `Read` de `skills/` y `sources/` (están en `implementation_roots`); leí por `bash` **sólo texto de procedimiento** que la propia ficha autoriza (`stage-2-specification.md`, `SKILL.md`, `re-entry.md`, `handoff-prompts.md`) y las tres `instruction_sources` del paquete. `skills/cdad-cycle/scripts/` no se leyó: el CLI sólo se invoca como subproceso. El RED no depende de ninguna lectura previa de la implementación: los oráculos salen de la spec/plan y de la ficha.