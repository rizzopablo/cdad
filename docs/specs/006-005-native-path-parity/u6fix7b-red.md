## Report — test-writer RED, 006-005 U6-7b

### 1. Intake path y límites respetados

Validated packet path (`---cdad-packet-json`, `packet_id: 006-005-native-path-parity-test-writer-red-020`). No cargué las skills completas del ciclo. Leí solo: el contrato aprobado, `execution.md` (hallazgo U6-7), `tests/**` y los **artefactos** `agents/cdad-*.md` / derivados publicados. **No leí implementación**: `scripts/cdad_packet.py` y `scripts/cdad-generate.py` solo se invocaron como procesos. No toqué `tests/.sensitive-patterns.local` ni la copia instalada real del HOME.

### 2. Archivos modificados (solo `tests/`)

| Archivo | Cambio |
|---|---|
| `tests/test_006_005_u6fix7b_derived_strips_write.py` | **Nuevo** (401 líneas). RED U6-7b: derivados construidos por `prepare` desde una copia instalada de fixture que lleva `  write: ask`. |
| `tests/test_004_002_t5_runtime.py` | **A-1**: `without_maps` reformulado — `write` pasa a la región de permisos reemplazada por la derivación (declarado en el helper y en el docstring del test byte-a-byte). |

Commit: `14c2b3c0520461d56580a559cc7d3d12ee0abdee` — `test: 006-005 U6-7b RED — los derivados no heredan la palanca write` (2 files, +437/−20).

### 3. Oráculo y mapa test → PD

El fixture copia `agents/cdad-*.md` de HEAD a un directorio temporal de “instalación” y **reinserta `  write: ask` dentro del bloque `permission`, después del mapa `edit`** (los agentes sin bloque `permission`, como el orchestrator, quedan intactos). `prepare` corre como proceso con `CDAD_OPENCODE_AGENTS_DIR` apuntando a esa copia. Los veredictos se evalúan reutilizando `write_rule_list`/`write_verdict` y `edit_verdict` de `tests/test_006_005_u6fix7_write_lever.py` (findLast sobre `edit`+`write` en orden de archivo).

Docstrings «E2/PD-24 (U6-7b)»:

| Test | Postcondición |
|---|---|
| `test_u6_7b_every_derived_agent_ignores_the_installed_write_lever` | E2/PD-24: para cada rol publicado y su `-odoo`, en 7 sondas, `write_verdict == edit_verdict` y nunca `ask`. |
| `test_u6_7b_derived_test_writer_keeps_tests_docs_and_temporary` | PD-24: `tests/x.py` allow, `docs/x.md` deny, `.cdad/tmp/x` allow (raíz temporal declarada); `-odoo`: tests allow/models deny. |
| `test_u6_7b_derived_implementer_and_readers_keep_their_maps` | PD-24: implementer tests deny/código allow; architect/reviewer/scribe (+`-odoo`) toda ruta deny. |
| `test_u6_7b_derived_orchestrator_control_stays_allow` | Control: `permission: allow`, nunca llevó la palanca; escritura allow, nunca `ask`. |
| `test_u6_7b_second_prepare_does_not_claim_hand_edits` | Deriva: un `prepare` siguiente rc=0 (no reclama edición a mano) y regenera bytes idénticos. |

Precondiciones verificadas por test: `prepare` rc=0, el set publicado espeja la copia instalada y **cada rol instalado lleva `  write: ask`** (el fixture no pasa vacío).

### 4. A-1 — test existente reformulado (declarado)

`tests/test_004_002_t5_runtime.py::without_maps` (usado por `test_pd8_i9_derived_body_is_byte_identical_to_source` y `test_pd8_i9_reconciled_policy_regenerates_deriveds`) fijaba que la derivación conserva byte a byte **todo** el frontmatter salvo `read/grep/glob/edit` + cabecera `permission:`, es decir, fijaba la conservación de `write`. U6-7b exige retirar/reemplazar esa clave (v2.0.27 la evalúa para la escritura), así que **`write` entra a la región reemplazada**; el resto sigue byte a byte. El reemplazo quedó declarado en el docstring del helper y en el del test. No hay otro test que fije esa conservación.

### 5. Comandos y salida

```
$ python3 -m pytest tests/test_006_005_u6fix7b_derived_strips_write.py -q --tb=line
F.FF.                                                                    [100%]
...
AssertionError: 'ask' != 'deny'
AssertionError: 'ask' != 'allow'
AssertionError: 'ask' != 'deny'
3 failed, 2 passed in 1.69s
```
Fallan por **aserción de comportamiento** (`'ask' != 'deny'/'allow'`), sin ImportError ni error de fixture. Pasan hoy: el control del orchestrator y el chequeo de deriva (invariante de conservación).

```
$ python3 -m pytest tests/test_006_005_*.py -q
3 failed, 130 passed in 153.79s (0:02:33)
```
Las 3 fallas son exactamente las nuevas de U6-7b; los 130 restantes (incluidos los focales U3 del bloque de validación) verdes.

```
$ python3 -m pytest tests/test_004_002_t7_l1_derived.py \
    tests/test_004_002_t5_runtime.py tests/test_004_002_t5_reviewfix.py \
    tests/test_004_002_t7_w2.py -q
45 passed in 20.94s
```
La reformulación A-1 no rompió ningún test de derivados.

### 6. Notas y límites

- El bloque «Task validation plan» del task nombra focales de **U3**, mientras el objetivo y la subfase del packet son **U6-7b RED**. Seguí el objetivo (contrato de ejecución) y corrí el set que pide; los focales U3 quedaron cubiertos verdes dentro de `tests/test_006_005_*.py`.
- `docs/specs/006-005-native-path-parity/u6-acceptance.md` aparece modificado en el working tree por otra sesión (A1b/A3); **no es mío y no fue incluido en el commit**. Los untracked `docs/planning/` y `findings/*` quedaron intactos.
- Suite completa no ejecutada (política de cierre PD-21). Sin `--no-verify`, sin `git stash`, sin push.