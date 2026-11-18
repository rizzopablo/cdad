**T1 RED (PC-5) hecho y commiteado: 91835a6b.** Los 4 tests nuevos fallan hoy por aserción sobre el comportamiento pendiente. El rc distinto de 0 es el esperado en RED.

## Intake (ruta C)
- `cdad_packet.py render --request …/REQUEST.json` dio rc=0 y su salida es **idéntica byte a byte** a `PACKET.md`.
- El sha256 del spec coincide con el del paquete (`5cca6fa6…eb0`).
- Leí solo spec, `test-audit.md`, `audit-decision.md` y tests. No leí código de implementación. Solo ejecuté los CLI públicos.

## Archivos modificados
1. **Nuevo:** `tests/test_019_002_discovery_delivery.py`.
2. **Extendido (deliberado):** `tests/test_006_005_u7_scribe_role_report.py`. Quité solo la tupla `("architect","brainstorm")` de `cases`. Las otras cuatro combinaciones siguen protegidas. Dejé el motivo como comentario en el código: la obligación anterior era rechazar `role-report` en brainstorm, y la nueva es admitirlo (019-002 PC-5).

## Tests nuevos
Son cuatro tests con tres clases de fixture. Los tests de PC-5 usan fixtures descartables, con HOME/XDG en el tempdir. Reutilizan las clases base `U1bEntryCase`, `U2ModuleCase` y `ScribeRowCase` de tests existentes.

| Test | Qué protege | Falla hoy con |
|---|---|---|
| `TestPc5NativeDerivation::test_pc5_native_brainstorm_delivery_kind_is_role_report` | Derivación nativa: `record` escenifica `role-report` | `rc=1: the closed role/subphase table does not determine a single artifact kind … ['architect-plan-draft','architect-spec-draft']` |
| `TestPc5OpenCodeDerivation::test_pc5_opencode_brainstorm_delivery_materializes` | Derivación del adaptador OpenCode, más materialización con sha idéntico | `'blocked' != 'completed'`, por el mismo motivo de kind no único |
| `TestPc5BrainstormMaterialization::test_pc5_brainstorm_role_report_materializes_with_identical_sha` | `materialize` acepta `role-report` en brainstorm, con state y receipt intactos | `rc=2 … artifact_kind 'role-report' is not permitted for role 'architect'/substage 'brainstorm'` |
| `TestPc5BrainstormMaterialization::test_pc5_brainstorm_draft_kinds_are_rejected` | `architect-spec-draft` y `architect-plan-draft` se rechazan en brainstorm, sin escribir target | `0 == 0` en ambos kinds: hoy se aceptan |

Consecuencia sin estos tests: una consulta técnica legítima se rechaza antes de registrar su informe.

## Comandos y resultado
```
cd <repo>
PYTHONPATH=.:tests python3 -m unittest -v tests/test_019_002_discovery_delivery.py
→ Ran 4 tests … FAILED (failures=5)   # 5 = 4 tests + 1 subTest, todas AssertionError, ninguna por import/setup

PYTHONPATH=.:tests python3 -m unittest tests/test_006_005_u7_scribe_role_report.py \
  tests/test_005_007_t4_architect_report_materialization.py
→ Ran 13 tests … OK

python3 scripts/cdad-suite.py validate
→ integridad insuficiente (esperado: el módulo y los 4 nodeids nuevos no están inventariados)
```
La corrida debe hacerse con `PYTHONPATH=.:tests`, que es lo que necesitan los imports de los tests existentes.

## Delta de inventario para que el orquestador materialice
**`suite-inventory.json`**, entrada de módulo nueva:
```json
{"assignments":[{"capability":"delivery-evidence","contract":"docs/specs/019-002-effective-discovery-instructions/spec.md","scope":"module"}],
 "confidence":"alta","decision":"mantener",
 "helper_dependencies":["test_006_005_u1b_dispatch_entry","test_006_005_u2_opencode_module","test_006_005_u7_scribe_role_report"],
 "kind":"test","path":"tests/test_019_002_discovery_delivery.py",
 "product_surfaces":["scripts/cdad_dispatch.py","scripts/cdad_packet.py","scripts/cdad_result.py","skills/cdad-cycle/scripts/cdad_delegate_opencode.py"],
 "provenance":"019-002 T1 RED, test-writer; PC-5, test-audit N1",
 "rationale":"consulta técnica del architect en brainstorm: kind único role-report, derivación nativa/OpenCode y materialización",
 "static_test_nodeids":4,"targets":[]}
```
Los nodeids son:
- `tests/test_019_002_discovery_delivery.py::TestPc5NativeDerivation::test_pc5_native_brainstorm_delivery_kind_is_role_report`
- `…::TestPc5OpenCodeDerivation::test_pc5_opencode_brainstorm_delivery_materializes`
- `…::TestPc5BrainstormMaterialization::test_pc5_brainstorm_role_report_materializes_with_identical_sha`
- `…::TestPc5BrainstormMaterialization::test_pc5_brainstorm_draft_kinds_are_rejected`

Los nodeids van con capacidad `delivery-evidence` y contrato `…019-002…/spec.md`.

El módulo u7 conserva sus 6 nodeids estáticos. No cambió ningún origen ni destino de mapeo, y el módulo no aparece en `pc-map.json`, así que no hay delta de mapa.

Los campos `product_surfaces` y `provenance` los infirió el test-writer por analogía con módulos vecinos. El orquestador debe ajustarlos si el esquema real lo exige.

## Sensibilidad y límites
- **Sensibilidad:** cada test discrimina un defecto concreto. Con el `_allowed_kinds` actual, la derivación falla por kind no único, `role-report` es rechazado, y los kinds de borrador se aceptan.
- **Controles de architect/draft:** no los dupliqué. Ya los protegen `test_005_007_t4`, `u1b::TestPd23NativeDescriptorKind` y `u2::TestPd23DerivedArtifactKind`, y t4 sigue en verde. Los demás rechazos por eje rol siguen en u7.
- **No ejecutado:** las regresiones restantes del plan (`test_015_001`, `006_006_u3/u5`, `test_cdad_generate`, `role_packet_*`) y la suite completa. No corresponden a RED y quedan como suite completa no realizada.
- **Fuera de alcance:** N2 (PC-7, closure→status→open-unit) no estaba en este paquete, solo en T1/PC-5.
- `docs/.cdad-state.json` sigue modificado y no es mío. No lo incluí en el commit.
- Los tests de PC-5 validan el kind, el rechazo y la materialización por transporte. No prueban que el architect redacte bien la consulta.