# Re-review focal T2 — 004-003-planning-procedures

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-13>`.
> Paquete: `004-003-planning-procedures-reviewer-review-004`. Alcance focal
> (PD-5). **Dictamen: 3/3 bloqueantes cerrados, enmienda de oráculo sin pérdida
> de garantías, 0 bloqueantes nuevos, 1 Nit.**

## Verificación realizada

1. `sha256sum …/spec.md` → `ba395fed…bf766` = contract sha ✓
2. `git show 1cb2732` leído íntegro: 3 hunks, 2 archivos, `3 insertions(+), 3 deletions(-)`. **Solo cambian valores de substage** (`"review"` → `"plan-review"` en los defaults de `project()` de `test_004_003_t1_draft_contract.py:53` y `test_004_003_t1_reviewfix.py:45`, y en el control honesto de `TestF1DraftPlanIsReviewerOnly:84`). Ninguna aserción, fixture ni timeout cambia.
3. `grep -n '"review"' <los 3 archivos de test>` → **0 matches**: no queda ningún uso de `reviewer/review` + draft-plan en los oráculos.
4. Lectura de `cdad_packet.py:696-745` y `:2298-2333`: el pairing se enforce en **un solo lugar** (`validate_request`, 729-739), después de la validez de kind (719) y antes de cualquier publicación (750+). El B2 para otros roles lo cubre `ROLE_SUBSTAGES` (696); el B1 para otros roles, la restricción F1 preexistente (2324).
5. `cat packets/roles/reviewer.md` → frase generalizada en la fuente editable única, una línea, sin copia nueva.
6. `pytest tests/test_004_003_t2_reviewfix.py tests/test_004_003_t2_plan_review.py tests/test_004_003_t1_draft_contract.py tests/test_004_003_t1_reviewfix.py -q` → **11 passed in 8.75s**.
7. `pytest tests/test_role_packets.py tests/test_role_packet_render.py tests/test_role_packet_consumers.py tests/test_packet_prepare.py -q` → **44 passed in 83.82s**.

## Cierres

- **B1 — CLOSED.** `cdad_packet.py:729-734` (`is_draft and substage != "plan-review"` → `PolicyError`). Negativo black-box con control honesto y garantías de no-publicación: `tests/test_004_003_t2_reviewfix.py:53-90`. Bucket h.
- **B2 — CLOSED.** `cdad_packet.py:735-739` (`not is_draft and substage == "plan-review"` → `PolicyError`), más `ROLE_SUBSTAGES:696`. Negativo: `tests/test_004_003_t2_reviewfix.py:94-149`. Chequeo bidireccional en una sola pieza, tal como pedía el remedio. Bucket m.
- **B3 — CLOSED.** `packets/roles/reviewer.md:1` — la regla "qué revisar" declara el objeto según el contrato. Única copia; la contradicción previa desaparece del render. Regresión de composición verde. Bucket h.
- **Enmienda de oráculo `1cb2732` — SIN DEBILITAMIENTO.** Único delta observable: el substage de los controles honestos. Los controles F1/F2 de T1 son independientes del substage (`_default_scopes` no lo recibe); ningún oráculo T1 fijaba composición de `reviewer-review.md` (grep vacío). La enmienda es consecuencia lógica del cierre B1: mantener `reviewer/review` como control honesto habría sido un oráculo que testifica un escape. **Fortalece** la coherencia. Los negativos T1 (implementer/green, test-writer/red) no cambiaron.

## Hallazgo nuevo

- **O3 — Nit · OPTIONAL · bucket l.** `packets/roles/reviewer.md:1`: "the complete diff against the approved contract **for approved contracts**" repite "approved"; el remedio original decía "the complete diff for approved contracts". Semánticamente correcto; ruido de lectura. Una línea; el sha dinámico del oráculo la tolera. A deuda.

## Abstenciones

1. **Suite completa no re-corrida:** focal (11) + regresiones de composición/paquete (44). La declaración de GREEN (340 passed) no se re-verifica; no se disputa.
2. **Live dispatch del procedimiento enmendado:** juzgable solo desde artefactos; los oráculos pasan y el registro es consistente.

## Resumen

**Modificados por este rol:** ninguno (read-only, write scope vacío). **Commits leídos:** `f12b478` (review-fix B1/B2/B3), `1cb2732` (enmienda de oráculo), `7f7f322` (HEAD, GREEN verificado). **Dictamen:** los tres cierres proceden y la enmienda preserva todas las garantías T1/T2. **T2 cerrada.**
