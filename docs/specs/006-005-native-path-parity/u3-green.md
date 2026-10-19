# Informe del rol — implementer GREEN, 006-005 U3

## 1. Archivos modificados

Un solo archivo, dentro del `write_scope` (`skills`):

`skills/cdad-cycle/scripts/cdad_packet.py` — +169/−11 (`git diff --stat`)

Cuatro zonas, como fija la ficha U3:

1. **Vocabulario y validador de scopes.** `SCOPE_CLASSES` suma `temporary`; `_validate_scope` ramifica `temporary` dentro del camino genérico de selector (mismas comprobaciones de forma/ruta) y exige contención en un `temporary_roots` declarado por la política aceptada, con diagnóstico que nombra `docs/cdad-policy.json` y el campo. El piso de escritura del test-writer pasa a `{tests, colocated-tests, temporary}` (los otros roles no ganan nada: implementer queda en `{implementation, docs}`, el resto sin escritura). `_scope_contains` trata el temporal como **no-producto**: contiene sólo lo que `classify_path` deja `None` y no es ruta privada, así el manifiesto (PD-17/INV-3) nunca acredita un cambio de producto bajo un temporal.
2. **Propuesta y `git check-ignore`.** `propose_policy` emite `temporary_roots: [".cdad/tmp"]` como **propuesta** (constante `DEFAULT_TEMPORARY_ROOT`, D-5 C1/C2); la política vigente del repo no se toca (`docs/cdad-policy.json` sigue con `[]`, verificado). `_require_ignored_temporary_scope` corre en `_publish_generation` antes de escenificar nada: `git check-ignore -q -- <selector>` read-only, rc 0 acepta, rc 1 (no ignorado) y cualquier otro rc (no es árbol Git / git ausente) fallan cerrado nombrando `.gitignore` y la salida de no pedir el temporal.
3. **Permiso del derivado (PD-24).** `_derived_maps` recibe `temporary_roots` y, para el test-writer, emite las raíces como `allow` (literal + `<raíz>/**`, misma convención que la barrera privada P-1) **después** de los allow de tests/co-ubicados y **antes** del `deny` de política, del `deny` de derivados y de las rutas privadas ⇒ findLast conserva esas barreras (O-4 a/b probados por los dos fixtures de colisión). Con lista vacía no se emite nada: derivado byte-idéntico.
4. **Fuente de las raíces.** `_accepted_temporary_roots`: en contexto v2 lee `policy.snapshot` y **verifica el sha** contra `policy.sha256` antes de parsear (si no coincide, falla cerrado); en v1 plano lee el archivo de política. Ambos pasan por `_validate_policy_document`, así PD-18 sigue vigente. La misma función alimenta `validate_request`, `_validate_corrections` (`--replace-packet`) y `_build_derived_payloads`, de modo que el paquete y el derivado leen la misma fuente.

## 2. Tabla test → resultado

| Test | Antes (RED 0b38f07) | Ahora |
|---|---|---|
| `test_006_005_u3_temporary_scope.py::TestPd15TemporaryScopeAuthorized::test_pd15_empty_policy_rejects_naming_file_and_field` | FAIL (AssertionError) | **PASS** |
| `…::TestPd15DeclaredRootAccepts::test_pd15_declared_root_accepts_and_packet_declares_scope` | FAIL | **PASS** |
| `…::TestPd16SelectorNotIgnored::test_pd16_selector_not_ignored_is_rejected_naming_both_exits` | FAIL | **PASS** |
| `…::TestPd16NonGitTree::test_pd16_non_git_tree_is_rejected_naming_both_exits` | FAIL | **PASS** |
| `…::TestPd16IgnoredSelector::test_pd16_ignored_selector_is_accepted` | FAIL | **PASS** |
| `…::TestPd17ReceiptWithTemporaryScope::test_pd17_real_test_plus_ignored_probe_is_received_pending` | FAIL | **PASS** |
| `…::TestPd17ReceiptWithTemporaryScope::test_pd17_change_outside_every_declared_scope_is_still_rejected` | FAIL | **PASS** |
| `…::TestPd18TemporaryRootIsNotProduct::test_pd18_temporary_root_overlapping_product_is_rejected` | PASS (ancla) | **PASS** |
| `test_006_005_u3b_…::TestPd24DeclaredRootIsEditable::test_pd24_declared_temporary_root_is_allow_in_edit_map` | FAIL (`deny` != `allow`) | **PASS** |
| `…::TestPd24DeclaredRootIsEditable::test_pd24_no_other_path_gains_permission` | PASS (ancla) | **PASS** |
| `…::TestPd24DeclaredRootIsEditable::test_pd24_publication_path_and_manifest_are_unchanged` | PASS (ancla) | **PASS** |
| `…::TestPd24EmptyTemporaryRootsIsByteIdentical::test_pd24_empty_list_keeps_todays_edit_map` | PASS (ancla) | **PASS** |
| `…::TestPd24PrivatePathOverTemporaryRoot::test_pd24_private_path_overlapping_temporary_root_wins` | FAIL (`deny` != `allow`) | **PASS** |
| `…::TestPd24DerivedDirOverTemporaryRoot::test_pd24_derived_directory_overlapping_temporary_root_wins` | PASS (ancla) | **PASS** |

**Focales: 14/14 verdes** (antes 9 failed / 5 passed).

## 3. Comandos exactos y salida

```
$ python3 -m pytest tests/test_006_005_u3_temporary_scope.py \
    tests/test_006_005_u3b_derived_temporary_permission.py -q
14 passed in 6.49s          # 3 corridas, idéntico

$ python3 -m pytest tests/test_004_002_t1_policy.py tests/test_004_002_t1_reviewfix.py \
    tests/test_004_002_t2_bootstrap.py tests/test_004_002_t6_landing.py \
    tests/test_004_002_t7_acceptance.py tests/test_004_002_t7_private_paths.py \
    tests/test_004_002_t7_limits_rule.py tests/test_004_002_t5_runtime.py \
    tests/test_004_002_t5_reviewfix.py tests/test_003_002_t1_receive.py \
    tests/test_003_002_t2_materialize.py tests/test_packet_prepare.py \
    tests/test_005_005_t2_docs_policy.py -q
147 passed in 210.94s       # las 13 regresiones de la ficha U3

# re-corrida tras el último ajuste del validador (subconjunto con más superficie de riesgo)
$ python3 -m pytest tests/test_packet_prepare.py tests/test_004_002_t1_policy.py \
    tests/test_004_002_t1_reviewfix.py tests/test_005_005_t2_docs_policy.py \
    tests/test_004_002_t5_runtime.py tests/test_004_002_t7_private_paths.py -q
86 passed in 49.02s
$ python3 -m pytest tests/test_004_002_t2_bootstrap.py tests/test_004_002_t6_landing.py \
    tests/test_004_002_t7_acceptance.py tests/test_004_002_t7_limits_rule.py \
    tests/test_004_002_t5_reviewfix.py tests/test_003_002_t1_receive.py \
    tests/test_003_002_t2_materialize.py -q
61 passed in 108.98s

# focales de U1a/U1b/U1c/U2
$ python3 -m pytest tests/test_006_005_u1a_runtime_config.py tests/test_006_005_u1b_dispatch_entry.py \
    tests/test_006_005_u1c_packet_agent.py tests/test_006_005_u2_opencode_module.py -q
56 passed in 73.76s

# ampliación proporcional (derivados, propuesta de política, contexto v2, proyección, preflight)
$ python3 -m pytest tests/test_004_002_t7_w2.py tests/test_004_002_t7_l1_derived.py \
    tests/test_005_008_t1_nested_tests.py tests/test_005_008_t2_language_commands.py \
    tests/test_004_002_t34_reviewfix3.py tests/test_005_013_t1_unit_projection.py \
    tests/test_005_006_t5_acceptance.py tests/test_003_003_t2_preflight.py \
    tests/test_005_001_tcorr.py tests/test_role_packet_render.py \
    tests/test_004_002_t3_durable.py tests/test_004_002_t3_reviewfix.py \
    tests/test_004_002_t2_reviewfix.py tests/test_003_004_t4_real_context.py \
    tests/test_003_006_t4_ru2_refused_write.py tests/test_005_005_t3_provenance.py -q
123 passed in 158.05s
$ python3 -m pytest tests/test_004_001_t7_capacity.py tests/test_006_002_u1_delegation_section.py \
    tests/test_006_002_u2_neutral_skill.py tests/test_006_002_u3_runtime_references.py \
    tests/test_006_002_u6_context_discipline.py \
    tests/test_005_007_t4_architect_report_materialization.py \
    tests/test_003_002_t2_reviewfix.py tests/test_005_001_t1_role_approval.py \
    tests/test_005_001_t2_replace_packet.py tests/test_005_012_t1_register_transition_base.py -q
87 passed in 111.68s

$ make validate
Assert PASS: 168
Assert FAIL: 1        # F011 — condición ambiental preexistente, ver §4
```

## 4. `make validate` — F011, condición ambiental declarada (preexistente)

```
$ make validate | grep '^FAIL'
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL

$ bash scripts/validate-subagents.sh | grep DRIFT
DRIFT: differs ~/.claude/skills/cdad-cycle/scripts/__pycache__/cdad_delegate_opencode.cpython-313.pyc
DRIFT: differs ~/.claude/skills/cdad-cycle/references/cli-delegation.md
```

Idéntico al fallo ya declarado en el informe del RED (§5) y en el HEAD del paquete: **drift de las copias instaladas en HOME**, no del árbol. Mi diff es de un solo archivo de `skills/`, ninguno de esos dos; no toqué `~/.claude` ni `~/.config/opencode` (prohibido por el encargo). Queda reportado para que el orquestador decida (reinstalar o registrar la condición).

## 5. Conflictos entre oráculos

Ninguno. No edité tests. No hay test que fije el valor de la propuesta ni el mapa `edit` completo del test-writer derivado (coincide con V-8/A-1 del RED): `test_004_002_t5_runtime.py` usa el evaluador findLast con sondas y `test_004_002_t1_policy.py` sólo comprueba determinismo y que la propuesta materializada valide.

## 6. Commit

```
$ git commit -F -   # "feat: 006-005 U3 GREEN — temporal del test-writer autorizado y escribible"
[a7f1bea] skills/cdad-cycle/scripts/cdad_packet.py | 180 +++++++++++++++++++++--
 1 file changed, 169 insertions(+), 11 deletions(-)
```

Sin `--no-verify`, sin `git stash`, sin push. `git status` posterior: sólo los untracked preexistentes ajenos (`docs/planning/`, `findings/incremental-construction-…-2026-10-17.md`), intactos.

## 7. Límites declarados

- **La escritura real no se prueba aquí.** `scope_validation: passed` (PD-17) sigue siendo compatible con que el auxiliar no se haya podido escribir: lo ignorado nunca entra al manifiesto (INV-3). PD-24 prueba que el mapa `edit` del derivado **autoriza** la raíz y que las barreras conservan findLast; la escritura con la herramienta del rol es U6 (E2/V-14), y qué copia del agente carga el hijo nativo sigue siendo el desconocido declarado en la spec §9.
- **`git check-ignore` es una verificación de prepare, no un sandbox**: un `.gitignore` cambiado después de publicar el paquete no se re-verifica en `receive`.
- La contención del temporal en el manifiesto se apoya en `classify_path` (producto) + `_is_private_path` (privadas). Un cambio en una ruta que la política no clasifique ni declare privada, dentro de la raíz temporal, se consideraría contenido — es exactamente lo que D-5 C2/C5 acota: la raíz es disjunta de producto por `_validate_temporary_roots` y el `deny` privado gana por findLast.