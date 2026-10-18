I'll start by reading the approved contract and plan, then the existing tests.
Now I'll write the U3 focal test module.
Now the coupled edits. Starting with the U2 module (removing the temporal U3 exclusions):
Now the coupled module #1:
Now update the map docstring of module #1 and its RED expectations:
Now coupled module #4 (spawn reconciliation):
Now the two parametrize lists in module #4 that include the withdrawn reference:
Now coupled module #5:
Now the OpenCode half of module #5:
Now coupled module #2 (CC guard decisions consumer):
Now update module #2's docstring map and RED notes:
RED U3 completo. Cierro con el informe de rol.

## Archivos modificados (solo `tests/`)

| Archivo | Cambio |
|---|---|
| `tests/test_006_002_u3_runtime_references.py` | **NUEVO** (+529) — focal RED de PD-9/PD-10 |
| `tests/test_006_002_u2_neutral_skill.py` | retiradas las exclusiones TEMPORALES de U3 (las dos referencias + `cli-delegation.md`): PD-1 corre sobre el árbol completo salvo `context-meter.md` (INV-8) y §2 (U4/PD-11) |
| `tests/test_005_004_t1_dispatch_tool_name.py` | #1: `CC_REF`/`OC_REF` (rutas retiradas) → capa de agente (`sources/agents/adapters/opencode.md` + `agents/cdad-orchestrator.md`) y adaptador fuente CC; 2 asserts reformulados |
| `tests/test_005_004_t4_cc_guard_decisions.py` | #2: `CONSUMER` (referencia retirada) → retiro + evidencia no instalable bajo `docs/**`; 2 tests reformulados |
| `tests/test_005_005_t3_provenance.py` | #3: PD-15 (documental) repuntado al nuevo dueño (`docs/**`) — sin test de comportamiento que tocar |
| `tests/test_005_009_t3_spawn_reconciliation.py` | #4: conservación de la referencia CC → evidencia no instalable; 2 listas `parametrize` podadas (superficie retirada) |
| `tests/test_005_010_t3_references.py` | #5: mitad OpenCode → evidencia no instalable; INV-7 queda sobre `cli-delegation.md` (instalable) |
| `tests/validate-consistency.sh` | F004 (tabla), F010 M6 y el control 005-004 PD-1 repuntados; helpers `assert_file_missing` / `assert_tree_not_has` |

## Mapa test → PD

| Test | PD | Estado RED |
|---|---|---|
| `…u3…::TestPd9…::test_pd9_runtime_references_are_withdrawn_from_the_installable_tree` | PD-9 | **FAIL** (ambas siguen instalables) |
| `…::test_pd9_history_is_preserved_as_non_installable_evidence_under_docs` | PD-9 | **FAIL** (ningún doc de `docs/**` conserva hoy el detalle retirado: 4/5 conceptos como máximo) |
| `…::test_pd9_reference_table_drops_the_two_runtime_rows` | PD-9 | **FAIL** (`SKILL.md:459-460`) |
| `…::test_pd9_no_installable_text_points_to_the_withdrawn_references` | PD-9 | **FAIL** (7 punteros: `SKILL.md:459-460,495`, `cli-delegation.md:271`, `runtime-adoption.md:53`, `sub-agent-strategies.md:55`) |
| `…::TestPd10…::test_pd10_adapter_contract_concepts_are_conserved` | PD-10 | PASS hoy (**GUARD pre-satisfecho** declarado) |
| `…::test_pd10_transport_choice_rule_is_gone` | PD-10 | **FAIL** — 1 ofensor exacto: `cli-delegation.md:269` «An orchestrator that already runs **inside OpenCode** delegates with `task`» (la regla de :267-276, identificada **por contenido**) |
| `test_005_004_t1::test_pd1_ii_opencode_side_keeps_its_tool_name` | PD-1/AC-1 + PD-9 | **FAIL** (retiro) |
| `test_005_004_t1::test_pd1_iii_adapter_and_derived_orchestrator_name_the_same_tool` | PD-1(iii) + PD-9 | **FAIL** (retiro) |
| `test_005_004_t4::test_pd4_withdrawn_consumer_preserves_the_guard_contract_claims` | PD-4/PD-9 | **FAIL** (retiro) |
| `test_005_004_t4::test_pd4_exit2_claim_stays_scoped_in_the_preserved_evidence` | PD-8/VERIFY-1 + PD-9 | **FAIL** (retiro; guard se activa sobre la evidencia) |
| `test_005_009_t3::test_pd9_spawn_guard_conservation_survives_the_reference_withdrawal` | PD-9 | **FAIL** (retiro) |
| `test_005_010_t3::test_pd10_opencode_load_mode_and_durable_identity_survive_withdrawal` | 005-010 PD-10 + 006-002 PD-9 | **FAIL** (retiro) |
| `test_005_010_t3::test_pd10_opencode_model_pointer_survives_the_withdrawal` | ídem | **FAIL** (retiro) |
| `test_006_002_u2::test_pd1_no_dispatch_tool_form_in_installable_skill_text` | PD-1/INV-1 | **FAIL** (30 offenders, todos en las 2 referencias + `cli-delegation.md:270`) |
| `validate-consistency.sh` F004 / F010 M6 / 005-004 PD-1 | PD-9 (+PD-1/AC-1) | **4 FAIL** nuevos |

## Comandos y salida

```
python3 -m pytest tests/test_006_002_u3_runtime_references.py -q
→ 5 failed, 1 passed in 0.45s      (los 5: AssertionError de contrato; 0 ImportError/SyntaxError/NameError)

python3 -m pytest <8 módulos tocados + test_006_002_u1_delegation_section.py + test_005_010_reviewfix.py + test_005_009_t2_opencode_adapter.py> -q
→ 13 failed, 64 passed in 39.32s        # los 13 son exactamente los RED listados arriba

bash tests/validate-consistency.sh
→ Assert PASS: 155 / Assert FAIL: 5
  4 nuevos por PD-9 (F004 ×2, F010 M6 ×1, control 005-004 PD-1 ×1) + F011 preexistente y ambiental
  (drift de la instalación en HOME, ajeno a tests/; ya reportado en U1/U2)
```
`make validate` no agrega linters; no corrí la suite completa (política del packet: la cierra el closer).

## Commit

`2665d55  test: 006-002 U3 RED — retiro de las referencias por runtime y cli-delegation.md como contrato del adaptador` — 8 archivos, todos bajo `tests/` (+958/−236); sin `--no-verify`, sin `git stash`, sin push; árbol limpio tras el commit.

## Justificación de cada cambio acoplado (por PD)

- **#1** — PD-9: el dueño del nombre de la herramienta es la capa del agente (D-1); la referencia retirada deja de ser superficie del oráculo, y el retiro es el assert que falla hoy. Cobertura conservada (adaptador fuente + derivado para CC; adaptador fuente + orquestador para OpenCode).
- **#2** — PD-9: el consumidor instalable sale del árbol y sus afirmaciones (clasificador, fail-closed, búsquedas acotadas, alcance de `exit 2`) se verifican sobre la **evidencia no instalable** que las preserva; el guard de `exit 2` se activa sobre el texto preservado (precedente INV-8 de 005-009).
- **#3** — PD-15 era documental (sin test): se repunta el dueño declarado a `docs/**`.
- **#4** — PD-9: la conservación del spawn guard sigue cubierta por SKILL.md + fuente + ambos generados (parametrizados) y el detalle retirado (prohibición + incidente) se verifica en la evidencia; las dos listas `parametrize` pierden solo la superficie retirada.
- **#5** — PD-9: la mitad OpenCode (modo de carga, identidad durable, puntero a la tabla única) se repunta a la evidencia; INV-7 queda sobre el texto **instalable** (`cli-delegation.md`, PD-10 lo mantiene), porque la evidencia no instalable está fuera de su alcance por diseño.
- **U2** — instrucción del packet: PD-1 sin las exclusiones temporales de U3.
- **validate-consistency.sh** — PD-9: la tabla ya no indexa las dos referencias (puntero colgante) y el retiro es assert por ausencia; M6 y el control PD-1 de 005-004 se reformulan **conservando** la preocupación sobre el árbol instalable y la capa de agente. Todo reformulado en este RED, nunca en el GREEN (enmienda A-1).

## Límites y riesgos declarados (honestos)

1. **Sin lecturas de implementación para derivar aserciones**: no abrí `skills/`, `sources/`, `scripts/` ni `agents/`. Los ofensores que cito salen de los **mensajes de falla de mis propios tests** (el test lee el producto por diseño). Sí ejecuté `grep -rl` (solo **nombres de archivo**) sobre `skills/` para comprobar que el GREEN era alcanzable: confirmé que los punteros viven en 4 archivos de `skills/cdad-cycle/references` + `SKILL.md` (todos dentro de la superficie de U3) y que ningún texto de `agents/**` apunta a las rutas retiradas.
2. **Único riesgo real de bloqueo del GREEN**: las aserciones de evidencia (#2, #4, #5 y PD-9-2) exigen que el detalle retirado se preserve en `docs/**` **incluyendo** el contrato del guard y la prohibición/incidente del CC. Si la intención de U3 fuese preservar solo los cuatro ítems enumerados por la spec (recarga/versión, `delegate`, 429, procedencia), esos asserts bloquearían: lo declaro para que el orquestador adjudique (conservar la cobertura vs. recortar la preservación) — no lo resolví por mi cuenta.
3. **Alcance del retiro de punteros** (PD-9-4): exige limpiar los 7 punteros de los 4 archivos instalables, no solo la tabla que nombra la ficha; es el oráculo textual de PD-9 («ningún texto instalable apunta a esas rutas») y está dentro de la superficie de `skills/`.
4. **Exclusión declarada del oráculo de evidencia**: se excluyen los documentos de planificación de esta feature (`spec/plan/discovery/u*-red/u*-green` en su directorio) porque **mandan** el movimiento y aceptarlos volvería vacuo el assert (mismo criterio con que U2 excluyó `context-meter.md`); la evidencia puede vivir en cualquier otro documento de `docs/**`, incluido uno nuevo en ese directorio.
5. **`test_pd10_adapter_contract_concepts_are_conserved` es un guard pre-satisfecho declarado**: mide que el contrato del adaptador sigue ahí (no que esta unidad agregue texto). Los casos `exit-2`/`INV-8` conservan su lógica de skip/retorno declarado cuando el texto no trata el concepto.
