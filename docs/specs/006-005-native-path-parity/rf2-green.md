All gates are met and the commit is in place. Here is the role report.

---

# Role report — implementer, GREEN review-fix 2 (006-005-native-path-parity, B-3 + B-4)

**Packet:** `006-005-native-path-parity-implementer-green-019` · **Contract:** `docs/specs/006-005-native-path-parity/spec.md` (sha256 `3a824be…20df01`, sin enmienda) · **Substage:** green · **Commit:** `88491b2`

## Archivos modificados (2, ambos en write scope)

| Archivo | Hallazgo | Cambio |
|---|---|---|
| `skills/cdad-cycle/scripts/cdad_dispatch.py` | **B-4** | `_key_states()`: la llave que la fila **expone** sin declaración vuelve a ser `unknown` (se retira la omisión introducida por B-2) |
| `skills/cdad-cycle/references/re-entry.md` | **B-3** | «Orchestrator materialization protocol»: tabla de los **tres estados de llegada** con su ruta; se retira el párrafo que conservaba la escenificación manual para el despacho externo; «Transport equivalence» deja de presentar `receive` como primer paso de la ruta del adaptador CLI |

**NO tocado:** `tests/**` (0 líneas de diff en `tests/`), `agents/**`, `sources/**` (no hizo falta: el generado ya declara las dos rutas correctamente según `rereview.md`; la contradicción estaba en el procedimiento remitido, luego `make agents` no era necesario), `docs/planning/`, `findings/`, `docs/.cdad-state.json` (cambio del orquestador, sin commitear, ajeno) y la instalación/config/store/runtime en `HOME` (ni leídos ni escritos por mí).

### B-4 — la llave expuesta sin declaración queda `unknown` (contrato conservado, sin enmienda)
La **selección** de la fila (`--session`/`--parent`) y la **suficiencia** de la evidencia quedan separadas: la fila seleccionada puede exponer `parent_id` y, sin `--parent` declarado, esa llave es `unknown` — se nombra en el diagnóstico y no acredita sesión (`session: null`, procedencia que declara lo no verificado, entrega persistida bajo PD-6). Un `--parent` **declarado** que coincide acredita; uno **contradictorio** sigue siendo rechazo (`blocked`, sin entrega). La normalización de B-2 (instante + modelo, `cdad_delegate_opencode.py`) queda intacta.

### B-3 — el protocolo distingue por estado de llegada
| Estado de llegada | Ruta declarada |
|---|---|
| FINAL TEXT pendiente de escenificar | escenificar los bytes exactos + `RESULT.json` ⇒ `receive` |
| descriptor ya escenificado (nativa) | `record` ya escribió texto y descriptor ⇒ `receive` (sin escenificar de nuevo) |
| recibo ya durable (externa) | `delivery_ref` = recibo durable ⇒ validar recibo (`validate-receipt`) ⇒ `materialize` / `register-transition` — **sin escenificar y sin recibir otra vez** |

## Test → resultado

| Selección | Comando | Resultado |
|---|---|---|
| RED en HEAD (línea base, antes del cambio) | `pytest -q tests/test_006_005_reviewfix2.py tests/test_006_005_reviewfix.py` | **4 failed**, 12 passed (los 4 RED declarados) |
| RED + A-1 (después) | ídem | **16 passed** (13.52 s) |
| focal del paquete | `pytest -q tests/test_006_005_u1b_dispatch_entry.py` | **17 passed** (18.31 s) |
| focales de la feature | `pytest -q tests/test_006_005_*.py` | **155 passed** (164.34 s; re-corrida final tras el re-wrap: **155 passed**, 187.53 s) |
| regresiones declaradas (006-002/006-003/006-001/packet_prepare) | `pytest -q tests/test_006_002_u5_transport_equivalence.py tests/test_006_001_t1_selection.py tests/test_006_003_u4_delegation_config.py tests/test_006_003_u6_server_credential.py tests/test_006_003_u8_acceptance.py tests/test_packet_prepare.py` | **62 passed** (203.38 s) |
| regresiones declaradas (005-009/005-010/005-007 t5/004-002 t4) | `pytest -q tests/test_005_009_t1_interface.py … tests/test_004_002_t4_dispatch.py` | **56 passed, 2 skipped** (83.40 s) |
| `test_cdad_generate`, `test_role_packet_consumers`, tests de re-entry | `pytest -q tests/test_cdad_generate.py tests/test_role_packet_consumers.py tests/test_004_003_t5_reentry_equivalence.py tests/test_003_006_t3_receive_wiring.py tests/test_005_007_t7_unit_size_and_retries.py` | **42 passed** (13.82 s) |
| re-verificación tras el re-wrap del texto | `pytest -q tests/test_006_005_reviewfix2.py tests/test_006_005_reviewfix.py tests/test_006_002_u5_transport_equivalence.py tests/test_004_003_t5_reentry_equivalence.py tests/test_003_006_t3_receive_wiring.py tests/test_005_007_t7_unit_size_and_retries.py` | **49 passed** (19.89 s) |
| `make validate` | `make validate` | **Assert PASS: 168 · Assert FAIL: 1** → F011, ambiental (ver abajo) |
| suite completa | — | **no ejecutada** (PD-21: la corre quien cierra) |

### Flakiness conocida del margen del waiter (declarada, con corrida aislada)
`tests/test_006_001_t1_selection.py` — corrida del archivo completo ×3: `18 passed` / `18 passed` / **1 failed** (`TestPd4SameErrandInServerMode::test_pd4_same_errand_in_server_mode` → `'timeout' != 'completed'`). Corrida **aislada** del mismo test ×5: **5 passed** (≈2 s cada uno). Es el flake preexistente de la espera acotada (~0,18 s) bajo carga, ya documentado en `rf2-red.md`; ese archivo no referencia `cdad_dispatch` y mi cambio no toca el margen del waiter → **no es regresión**.

### `make validate` — F011 ambiental (declarado)
Único fallo: `F011: scripts/validate-subagents.sh (active profile) → FAIL`. Su cadena es `install.sh --check`, que compara el árbol instalable del repo contra el **árbol instalado en `$HOME`** (`<home>/.claude/skills/cdad-cycle`, `<home>/.config/opencode/agents`, …) y reporta drift en la copia instalada de `re-entry.md` (el repo cambió con este GREEN; la copia instalada queda obsoleta por diseño hasta que corra `install.sh`, y la instalación en `HOME` está fuera de mi alcance de escritura) y, **independientemente de este cambio**, agentes instalados ausentes (`cdad-orchestrator.md`, `cdad-reviewer.md`). Los validadores del propio repo (F001–F010, F012, 005-004) pasan: 168/169 asserts. La cadena incluye la lectura interna de `tests/.sensitive-patterns.local` por `tests/validate-odoo-specialization.sh`: la hizo el validador declarado; yo no abrí, copié ni modifiqué ese archivo privado.

## Commit
```
88491b2 fix: 006-005 review-fix 2 — B-3 B-4
 skills/cdad-cycle/references/re-entry.md   | 44 ++++++++++++++++++------------
 skills/cdad-cycle/scripts/cdad_dispatch.py | 28 ++++++++++++----------
 2 files changed, 43 insertions(+), 29 deletions(-)
```
Sin `--no-verify`, sin `git stash`, sin `push`. El árbol de trabajo conserva intactos los cambios ajenos (`docs/.cdad-state.json` modificado; `docs/planning/` y `findings/` sin trackear).

## Límites y honestidad
- No edité tests; el único cambio de oráculo (A-1) venía declarado en el RED (`5306a28`) y no lo toqué.
- No amplié el contrato: la Conservación de spec §2.3 (PD-5/PD-6) es la del contrato aprobado.
- No ejecuté la suite completa (PD-21) ni repetí despachos reales; la evidencia es de fixtures, como en el RED.
- `make agents` no se ejecutó: las fuentes de los agentes y los dos orquestadores generados ya declaraban las dos rutas (transporte externo con `delivery_ref` = recibo durable, prohibitions de recibir otra vez); el defecto B-3 estaba en el procedimiento al que remiten. El oráculo de `test_006_005_reviewfix2.py::TestB3ReentryProtocol` sobre los dos generados pasa sin tocar ellos.
- No declaro independencia de familia de modelo respecto del implementer.