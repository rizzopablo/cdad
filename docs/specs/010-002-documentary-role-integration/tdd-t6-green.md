# Informe GREEN — T6 de `010-002-documentary-role-integration`

## 0. Intake (ruta C) y validez del paquete

| Verificación | Comando | Resultado |
|---|---|---|
| Identificación ruta C | `render --route C --request …/REQUEST.json` | idéntica byte a byte al bloque recibido |
| Request/packet | `validate-packet --request … --packet …` | `rc=0` |
| Render canónico completo | `render --request …` + `diff` contra `PACKET.md` | `PACKET_MATCHES_RENDER` (`diff` rc=0) |
| Contrato | `sha256sum docs/specs/010-002-documentary-role-integration/spec.md` | `0d630c49…81abc` (coincide con REQUEST/PACKET) |
| Cuerpo inline | — | ausente (ruta C correcta); sin mezcla de rutas |

Sin discrepancias bloqueantes. `docs/.cdad-state.json` (`M`) y `docs/specs/010-000-continuity-relative-root/discovery.md` (`??`) son preexistentes y **no** se tocaron ni commitearon. `red-t5.md` (`??`, del test-writer) tampoco se commitea: mi write scope es implementación.

## 1. Archivos modificados (solo implementación)

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/scripts/cdad_packet.py` | +127/−12: derivación canónica única (`_packet_agent` + `_generic_agent`), contraste estático agente↔rol, regla de presencia, contraste contextual compartido, rederivación del sucesor, contraste en intento nuevo de despacho |
| `skills/cdad-cycle/assets/packet-request.schema.json` | +13: propiedades opcionales `agent` y `execution_context` (tipo, `minLength`, descripción con la ubicación canónica) y `dependentRequired` (`execution_context` → `agent`); conjunto cerrado intacto |

`tests/**`: **0 líneas modificadas** (`git diff HEAD -- tests/` vacío).

## 2. Implementación frente al objetivo (derivada del contrato, no de los tests)

1. **Una sola derivación canónica**: `_packet_agent(role, state)` es la única resolución rol+stack (genérico para stack ausente/`null`/vacío; `cdad-<rol>-<stack>` para cualquier stack no vacío). La reutilizan preparación ordinaria, reemplazo, contraste contextual y registro. La forma genérica vive en `_generic_agent` (una sola definición); ningún consumidor resuelve por su cuenta (los consumidores leen `REQUEST.json.agent`, que es leer el valor declarado, no un resolutor).
2. **Contraste ESTÁTICO** en `validate_request` (`_validate_declared_agent`), compartido por `validate-request`, `render`, `validate-packet`, `receive`, `prepare` y reemplazo: acepta el genérico exacto o su prefijo completo con sufijo no vacío; un prefijo parcial o un agente de otro rol se rechazan. **No consulta el stack** y el diagnóstico nombra rol, agente recibido, familia esperada y declara que no evalúa stack.
3. **Contraste CONTEXTUAL** (`_require_current_agent`), aplicado solo a: publicación ordinaria, `--replace-packet` y registro de intento **nuevo** con agente declarado. **No** se aplica a repetición idéntica, finalización válida del write-ahead ni recepción/lectura. Diagnóstico con rol, stack vigente y agente esperado.
4. **Presencia**: `execution_context` sin `agent` se rechaza en la validación compartida (y por tanto en la publicación y el registro); el histórico sin ambos sigue admitido, registra intento nuevo sin contraste ni derivación silenciosa, y `agent` sigue fuera del render.
5. **Reemplazo**: el sucesor **rederiva** `new_request["agent"] = _packet_agent(role, state)`; nunca copia el del predecesor. Cubre predecesor histórico sin agente y predecesor con stack cambiado; bytes del predecesor intactos.
6. **Variante no publicada**: no se añadió ninguna guarda de existencia en el módulo (ni flag ni selector).
7. **Esquema**: solo se declararon las dos propiedades ya admitidas + dependencia estructural; `additionalProperties: false` y el resto del asset sin cambios de alcance.

## 3. Comandos y salidas (medidos)

**Módulo focalizado completo (obligatorio):**

```
$ python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py
...........................                                              [100%]
27 passed in 40.86s   (rc=0)
```
(El módulo mide 27 tests: los 13 de T3 + 14 de T5; el objetivo decía «21» por aritmética 13+14−6. Los 27, incluidos los 6 controles ya verdes, pasan.)

**Regresiones declaradas por el plan (T6):**

| Archivo | Resultado |
|---|---|
| `tests/test_packet_prepare.py` | `19 passed` (22.63s) |
| `tests/test_006_005_u1c_packet_agent.py` | `5 passed` (7.06s) |
| `tests/test_role_packet_consumers.py` | `5 passed` (9.77s) |
| `tests/test_role_packet_render.py` | `17 passed` (117.65s) |
| `tests/test_008_004_packet_enforcement.py` | `25 passed` (23.99s) |
| `tests/test_006_005_u2_opencode_module.py` | `19 passed` (30.55s) |
| `tests/test_006_005_u1b_dispatch_entry.py` | `17 passed` (28.03s) |
| `tests/test_007_002_dispatch_recovery.py` | `18 passed` (65.78s) |
| `tests/test_010_004_t2_red.py` | `6 passed` (8.99s) |
| `tests/test_010_001_documentary_contracts.py` | `11 passed` (8.97s) |

**Ampliación por superficie compartida (el cambio sale del focal):**

| Archivo | Resultado |
|---|---|
| `tests/test_003_002_t1_receive.py` (recepción) | `7 passed` |
| `tests/test_005_001_t2_replace_packet.py` | `8 passed` |
| `tests/test_005_005_t1_replace_conserved.py` | `6 passed` |
| `tests/test_005_003_t6_packet_contract.py` | `7 passed` |
| `tests/test_004_002_t4_dispatch.py` | `15 passed` |
| `tests/test_005_012_t1_register_transition_base.py` | `21 passed` |
| `tests/test_006_006_w1_replace_draft_packet.py` | `5 passed` |
| `tests/test_007_001_unambiguous_entry.py` | `49 passed` |
| `tests/test_006_004_u1_decisions_field.py` | `8 passed` |
| `tests/test_006_005_reviewfix.py` | `9 passed` |
| `tests/test_006_005_u6fix4_native_selection.py` | `9 passed` |
| `tests/test_006_005_u6fix5_write_ahead.py` | `11 passed` |

**PC-12.b (evidencia medida, instalación aislada temporal):** `install rc=0`; en `.config/opencode/skills`, `.agents/skills` y `.claude/skills`: `cli=True cli_bytes_equal=True schema=True schema_bytes_equal=True`.

## 4. Diff de comportamiento observable (antes → después)

1. **Publicación ordinaria** — `stack` null/vacío/ausente → `agent='cdad-test-writer'`; `stack=odoo` → `'cdad-test-writer-odoo'`; `execution_context='.cdad/executions/…/execution.json'` en los cuatro casos (sin cambio respecto del control ya verde: sigue garantía por construcción).
2. **Reemplazo tras cambio de stack** — antes: `'cdad-test-writer-odoo'` → `'cdad-test-writer-odoo'` (copia); después: predecesor `'cdad-test-writer-odoo'` → sucesor `'cdad-test-writer'`, `execution_context` declarado y bytes del predecesor intactos (`True`).
3. **Contraste estático** — antes: `validate-request` aceptaba `agent='cdad-reviewer'` (rc=0); después: `rc=2`, `request.agent 'cdad-reviewer' does not belong to the declared role 'test-writer': expected the generic agent 'cdad-test-writer' or that complete prefix with a non-empty suffix (cdad-test-writer-<suffix>); this static contrast does not evaluate the stack…`; mismo rol con otro stack tras cambiar el dominio sigue en `rc=0` (no se evalúa stack en lectura).
4. **Contraste contextual / presencia** — antes: intento nuevo con `cdad-test-writer` y stack `odoo` aceptado; después: `rc=2`, `record-dispatch: request.agent 'cdad-test-writer' is not the destination of the current stack: role 'test-writer', stack 'odoo', expected agent 'cdad-test-writer-odoo'…`, sin efectos (ni registro ni estado). `execution_context` sin `agent`: antes `rc=0`, después `rc=2` (`…must declare the agent that receives it…`). Histórico sin ambos campos tras cambiar el stack: `rc=0`, registro durable **sin** clave `agent` y request intacto (`True`). Repetición idéntica y finalización del write-ahead: conservan rc=0/bytes/estado (medido por los controles del módulo).

## 5. Commit

```
a09f830a  feat: implement recipient coherence and the published request schema (010-002 T6)
  skills/cdad-cycle/assets/packet-request.schema.json | 13 +++
  skills/cdad-cycle/scripts/cdad_packet.py            | 127 +++++++++++++++++++--
  2 files changed, 128 insertions(+), 12 deletions(-)
```
Staged/committed solo esos dos archivos; `tests/` intacto; estado y artefactos preexistentes fuera del commit.

## 6. Límites honestos

- La suite completa **no** la corrió el implementer (política del paquete: la corre una vez el cierre). Se ejecutó el módulo focal completo, las diez regresiones exigidas y doce módulos adicionales de las superficies compartidas (validación, reemplazo, despacho, write-ahead, recepción), todos verdes.
- No se tocó el HOME real ni la instalación del host; la evidencia PC-12.b se midió en una instalación aislada temporal (`CDAD_INSTALL_ROOT`). T7 repite el recorrido integrado final.
- No se añadieron guardas de existencia de agente ni permisos por defecto; el esquema describe forma y no sustituye las comprobaciones del CLI.
