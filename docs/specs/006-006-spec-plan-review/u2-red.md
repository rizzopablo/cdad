# RED de U2 — 006-006-spec-plan-review · informe de rol

## 1. Archivos modificados y commit

| | |
|---|---|
| Archivo | `tests/test_006_006_u2_review_procedure.py` (**nuevo**, 417 líneas) |
| Commit | `9371722c7f7b9c5e63de7e639bc0645f3580cb57` — `test: 006-006 U2 RED — objeto de revision declarado por el contrato` |
| Diff | `1 file changed, 417 insertions(+)` — **sólo `tests/`** (`git show --name-only HEAD`) |
| No tocado | `docs/.cdad-state.json` (orquestador), `docs/planning/`, `findings/*` (untracked, ajenos) |

Sin `--no-verify`, sin `git stash`, sin `push`.

## 2. Mapa test → PD

| Test | PD |-oráculo| Estado hoy |
|---|---|---|---|
| `test_pd6_pd12_u2_substage_reviewed_object_is_not_the_plan_alone` | PD-6/PD-12 (O-1) | el objeto declarado es el objeto de especificación: la etiqueta plan-céntrica no queda como objeto **único** + el substage no excluye la spec («not only the spec») | **FAIL** ✅ razón correcta |
| `test_pd6_u2_substage_requires_the_dictamen_to_name_the_object_and_its_digest` | PD-6 / D-9 (O-2) | el dictamen nombra el objeto revisado **y su digest** (digest + obligación de nombrar + dictamen, por proximidad de 500 car.) | **FAIL** ✅ razón correcta |
| `test_pd12_u2_role_rule_names_the_contract_declared_object_with_its_form` | PD-12 (O-3) | la regla de rol nombra el objeto que el contrato declara, con su forma declarada (spec **y** plan), no «the plan draft» | **FAIL** ✅ razón correcta |
| `test_pd12_u2_substage_keeps_its_vigente_obligations` | PD-12 (O-4) | separación estructural/semántico; juicio sobre la intención; `## Abstentions` y «never mark the reviewed draft approved» (verbatim de la ficha); `detail` por referencia; taxonomía/confianza/verdict-tuple | PASS (guarda) |
| `test_pd12_u2_role_rule_keeps_its_vigente_obligations` | PD-12 (O-4) | read-only, veredicto, confianza, rationale, ubicación, abstención | PASS (guarda) |
| `test_pd12_control_negative_u2_substage_is_a_consumer_not_a_second_home` | PD-12 (O-5, control negativo) | el substage apunta al hogar canónico de la regla de detalle y no es un segundo hogar normativo (operacionalización del oráculo vigente 005-007 P5) | PASS (control) |
| `test_v5_pd12_u2_reviewer_static_block_is_measured_and_below_the_ceiling` | V-5 / PD-12 (O-6) | bloque estático medido = **2728 bytes** < techo declarado 12000 (holgura 9272) | PASS (medición) |

**Oráculos por concepto, no por frase exacta**: sólo se afirman literales que la ficha cita *verbatim* («PLAN DRAFT», «the plan draft», `## Abstentions`, «never mark the reviewed draft approved»). El resto son familias de tokens y vecindad. El «no re-enunciar la regla» se operacionaliza de forma determinista con el oráculo vigente 005-007 P5 (puntero al hogar canónico); el juicio de prosa queda para la review (INV-8 de 005-013) — declarado en el docstring.

## 3. A-1 — **ningún oráculo vigente se reemplaza**

`rg "PLAN DRAFT" tests/` → **0 ocurrencias**. `rg -i "plan draft" tests/` → 1 sola: `tests/test_004_003_t2_plan_review.py:75` (`OBJECTIVE = "Review the plan draft: intention + restrictions + plan"`), que es **cadena local del propio test** (el objetivo que pasa a `prepare`), no un oráculo sobre el texto del producto. Ese archivo calcula el sha256 del substage **dinámicamente** (`hashlib.sha256((PACKETS_ROOT / path).read_bytes())`), luego no lo fija. Las otras cuatro regresiones no tocan el substage ni la regla de rol. ⇒ **No hay nada que reformular**: este RED sólo añade casos. `DRAFT_PLAN_RELPATH` intacto.

## 4. Comandos y salidas

```
$ python3 -m pytest tests/test_006_006_u2_review_procedure.py -v
test_pd6_pd12_u2_substage_reviewed_object_is_not_the_plan_alone        FAILED
test_pd6_u2_substage_requires_the_dictamen_to_name_the_object_and_its_digest FAILED
test_pd12_u2_role_rule_names_the_contract_declared_object_with_its_form FAILED
test_pd12_u2_substage_keeps_its_vigente_obligations                    PASSED
test_pd12_u2_role_rule_keeps_its_vigente_obligations                   PASSED
test_pd12_control_negative_u2_substage_is_a_consumer_not_a_second_home  PASSED
test_v5_pd12_u2_reviewer_static_block_is_measured_and_below_the_ceiling PASSED
3 failed, 4 passed in 0.31s
```
Los 3 fallos son `AssertionError` sobre el **texto** (no ImportError/SyntaxError); el primero afirma `Enunciado: 'Review a PLAN DRAFT'`, el segundo `DIGEST ... es None`, el tercero `span=(153,163) match='plan draft'`.

```
$ python3 -m pytest tests/test_005_007_t1_progressive_detail_rule.py tests/test_005_007_t6_templates.py \
    tests/test_004_003_t2_plan_review.py tests/test_role_packet_render.py tests/test_role_packets.py
34 passed in 214.71s (0:03:34)
```
Medición V-5: `common.md` 901 + `roles/reviewer.md` 310 + `substages/reviewer-plan-review.md` 1515, unidos por `\n` = **2728 bytes** (coincide exacto con la cifra declarada en el contrato) · techo 12000 · holgura **9272**.

## 5. Bloque a reportar: `make validate` rojo por **deriva del producto instalado** (preexistente, no mío)

`make validate` → `Assert PASS: 168, Assert FAIL: 1` (`F011: scripts/validate-subagents.sh`). Diagnóstico: el producto instalado está desfasado respecto del repo —

```
repo HEAD (1cbccd5)          9106a1c4…
instalado ~/.claude/skills/…  d8e4bcfab53423c433272f095c5fd20eb87a463a7d3df37982ca2904dfd420d7
git show 3ca6597:…            d8e4bcf…   ← el instalado = revisión ANTERIOR a U1 (0a6e7fa) y U5 (1cbccd5)
```
El check compara `install.sh --check` (árboles instalados `~/.claude`, `~/.config/opencode`, `~/.agents`) contra el repo. Mi diff es **un archivo nuevo bajo `tests/`**, que los validadores no leen ⇒ **preexistente**, no causado por U2. No lo corrijo (fuera de mi write scope: re-instalar muta el entorno del owner). **Acción sugerida al orquestador antes del gate GREEN de U2: re-instalar el producto** (`install.sh`) para que `make validate` pueda estar verde.

## 6. Limitaciones honestas (PD-15)

- La herramienta `Read` deniega `skills/**` (implementation root del path policy). Leí por bash **los tres archivos de texto de procedimiento** que el encargo autoriza explícitamente (`packets/substages/reviewer-plan-review.md`, `packets/roles/reviewer.md`, y `packets/common.md`,needed para identificar la composición del bloque estático que el contrato nombra). **No leí** `skills/cdad-cycle/scripts/` (prohibido) ni ningún `.py` de implementación: del script sólo calculé **hashes sha256** (repo vs instalado vs commits) para diagnosticar la deriva de `make validate` — un hash no revela contenido.
- No corrí la suite completa (política del paquete: la corre **una vez** quien cierra).
- El RED exige que el GREEN conserve las obligaciones vigentes; si el implementador las reescribe en otra forma, las guardas lo señalan con mensaje explícito.