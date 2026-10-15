# Review — 004-003 T2 (plan-review subphase & packet), diff `821d50b..019eee6`

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-10>`.
> Paquete: `004-003-planning-procedures-reviewer-review-003`.
> **Dictamen: changes-required (3 bloqueantes, 2 opcionales, 2 FYI).**

**Contrato:** `spec.md` sha256 verificado `ba395f…` ✓ · **Diff:** GREEN `019eee6` (5 archivos) · **Tests:** byte-idénticos en GREEN (`git diff 821d50b..019eee6 -- tests/` vacío) · Sesión independiente del implementer ✓.

## Verificación realizada (comandos exactos)

1. `sha256sum docs/specs/004-003-planning-procedures/spec.md` → `ba395fedf46b…` = contract sha. OK.
2. `python3 -m pytest tests/test_004_003_t2_plan_review.py tests/test_004_003_t1_draft_contract.py tests/test_004_003_t1_reviewfix.py -q` → **9 passed in 8.35s**.
3. `pytest tests/test_packet_prepare.py tests/test_role_packets.py tests/test_role_packet_render.py tests/test_role_packet_consumers.py tests/test_role_packet_review_regressions.py tests/test_install_ownership.py tests/test_004_002_t7_l1_derived.py -q` → **71 passed in 208s**.
4. `bash tests/validate-consistency.sh` → 141 PASS / **2 FAIL**, idénticos en el baseline `821d50b` → **preexistentes**.
5. `bash scripts/validate-subagents.sh` → FAIL con drift, también en baseline; T2 agrega 2 archivos driftados (ver FYI-2).
6. Sondas CLI en vivo (fixtures en /tmp; repo real intacto):
   - **Sonda A** — `prepare --role reviewer --substage review` + `--contract-kind draft-plan …` → **rc=0, ACEPTADO**; composición = `substages/reviewer-review.md` (procedimiento de diff).
   - **Sonda B** — `prepare --role reviewer --substage plan-review` con `approved-feature-spec` por defecto → **rc=0, ACEPTADO**.
   - **Inspección del render**: línea 003 = "…assess the complete diff against the approved contract…" (de `packets/roles/reviewer.md`), línea 005 = "Review a PLAN DRAFT…" (de `substages/reviewer-plan-review.md`) — ambas presentes en todo paquete plan-review.

## Bloqueantes

### B1 — Un contrato `draft-plan` sigue siendo aceptado por la subfase `review` (escape de PD-2)

**Ubicación:** `cdad_packet.py:56` (`ROLE_SUBSTAGES["reviewer"]`), `:700-741` (la validación liga `draft-plan`→rol reviewer pero **nunca** `draft-plan`↔`plan-review`). Bucket h.

El review-fix de T1 restringió `draft-plan` al rol reviewer (F1), pero el reviewer puede recibirlo por la subfase `review`, que compone `reviewer-review.md` ("assess the complete diff against the approved contract") para un objeto borrador. El paquete emitido es internamente contradictorio. Reproducido: Sonda A rc=0. El suite no cubre el par (el negativo solo probó `test-writer/red`, `tests/test_004_003_t2_plan_review.py:213`).

**Remedio:** en el mismo bloque de validación PD-1, rechazar `draft-plan` cuando `substage != "plan-review"`; agregar el negativo black-box.

### B2 — `plan-review` es aceptado sobre un contrato `approved-*` (el procedimiento de borrador compone para una spec aprobada)

**Ubicación:** `cdad_packet.py:56`, `:705-741` (sin chequeo substage↔contract-kind). Bucket m.

§2 define `plan-review` para un objeto borrador; el criterio de aceptación 1 exige negativos donde "no se produce paquete para un contrato no soportado". Sonda B: un paquete plan-review se renderiza sobre `approved-feature-spec`. No se fabrica aprobación (PD-3 se sostiene por el kind), pero el misroute es un defecto observable del mismo agujero de pairing, por la otra puerta.

**Remedio:** pairing bidireccional en un solo lugar (`draft-plan` ⇔ `plan-review` para el rol reviewer); cubrir ambas direcciones con negativos.

### B3 — `packets/roles/reviewer.md` no fue reconciliado según G4 (todo paquete plan-review abre con la instrucción de diff-review)

**Ubicación:** `skills/cdad-cycle/packets/roles/reviewer.md:1` — compuesta en todo paquete plan-review (línea 003 del render). Bucket h.

La spec §5 G4 nombra explícitamente `packets/roles/reviewer.md` entre los "consumidores derivados a reconciliar (sin copia nueva)"; la nota de GREEN del orquestador declaró solo **dos** reconciliaciones (los dos enums de esquema + `handoff-prompts.md`). Resultado: un paquete plan-review cuya primera instrucción de rol dirige una diff-review contra un contrato aprobado para una revisión de borrador — enunciado competidor de la regla "qué revisar" (PD-12) y error de encuadre semántico (PD-2). El test de composición fija este archivo byte a byte, así que la contradicción está consagrada en el oráculo.

**Remedio:** generalizar la frase una vez, en la fuente editable única: "assess the object the contract declares: the complete diff for approved contracts, the plan draft for `draft-plan`". El test calcula el sha dinámicamente (líneas 149-155) → la edición no rompe el oráculo.

## Opcionales

- **O1** — Falta el newline final en `packets/substages/reviewer-plan-review.md` (único archivo de `packets/substages/` sin él). Bucket l. Formato; el render no se afecta.
- **O2** — `handoff-prompts.md:542-547`: el template invoca `plan-review` sin las tres flags obligatorias (`--contract-kind/--contract-path/--plan-version`); una copia literal falla. Bucket l.

## FYI (visible al dueño, no de este diff)

1. **A3 sensitive-pattern hit, preexistente:** `validate-odoo-specialization.sh` A3 marca `tests/test_role_packets.py` (1 match del patrón local #0); presente también en el baseline `821d50b`; introducido por la línea T6 de 004-002 (`c50f521`, `f50c3d8`), fuera de este diff.
2. **Los installs de HOME ahora driftean:** `validate-subagents.sh` reporta los dos JSON de esquema cambiados entre el drift (p. ej. `~/.claude/skills/cdad-cycle/assets/*.schema.json`), porque los assets publicados cambiaron sin reinstalar. El check ya fallaba en baseline (drift de agentes); T2 agrega dos entradas. Remedio: reinstalar al cerrar T2; la paridad de instalación fresca la prueba el test P5 de T2 (render byte-idéntico).

## Correcto y verificado

Par válido (reviewer, plan-review)+draft-plan (PD-2), oráculo de composición fijado byte a byte y nunca el substage review (PD-2), sin marca de aprobación y kind `draft-plan` (PD-3), exclusividad de rol con garantías de no-escritura (PD-4), encargo completo (PD-9), paridad de producto instalado (PD-12) — los 5 focales re-corridos verdes. El substage source lleva correctamente el encuadre semántico, confianza ≥80%, verdict-tuple y Abstentions.

## Abstenciones

1. **No repitió la suite completa:** la afirmación del implementer (338 passed / 628 s) no se re-verifica; corrió focal (9) + regresiones de paquete (71). No la disputa.
2. **Semántica de despacho en vivo del procedimiento** (independencia de sesión del autor, ≥80% en una review real, T7 end-to-end): no juzgable desde el diff.
3. **Si las sesiones de despacho RED/GREEN fueron realmente independientes:** el registro es consistente, pero la aislación al momento del despacho no es verificable desde los artefactos.

**Resumen:** 3 bloqueantes, 2 opcionales, 2 FYI, 3 abstenciones. Los bloqueantes son un tema con tres caras: el pairing `draft-plan`↔`plan-review` no se enforce en ninguna dirección (B1/B2) y la fuente de rol compartida aún encuadra la review como diff-vs-aprobado (B3, la reconciliación G4 que este diff omitió). Los tres se cierran en un cambio coherente a `cdad_packet.py:705-741` + `packets/roles/reviewer.md` + negativos en el test.
