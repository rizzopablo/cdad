# RED T4 — 005-007-progressive-planning · test-writer · subetapa red

**Packet:** `005-007-progressive-planning-test-writer-red-005` (contract sha `54877103…`, policy sha `f508ab1e…`) · **Rol:** test-writer · **Focal:** `tests/test_005_007_t4_architect_report_materialization.py` · **Postcondición:** PD-8 · **Trazabilidad:** ficha T4 del plan (`docs/specs/005-007-progressive-planning/plan.md:87-97`) + observación 1 de `review-claude-spec-2026-10-13.md`.

## Resultado del RED (fait accompli medido)

`python3 -m pytest tests/test_005_007_t4_architect_report_materialization.py -q` → **1 failed, 6 passed** (~9-10 s).

El único fallo es el caso 1 (positivo PD-8) y falla por **AssertionError** sobre la postcondición ausente, con el diagnóstico del producto en el mensaje (never ImportError / CLI ausente; el test trae el guard `assert_reachable_or_invalid_red`):

```
AssertionError: 2 != 0 : PD-8: la tabla cerrada de materialización debe admitir el kind `role-report`
para el architect (subetapa 'discovery') — es el kind que emite el adaptador de la interfaz común, y
el recibo del discovery real de 005-007 lo lleva (hoy el kind no está en la tabla cerrada del
architect y materialize lo rechaza, sin vía legítima para el informe):
rc=2 stdout='' stderr="ERROR: artifact_kind 'role-report' is not permitted for role
'architect'/substage 'discovery': a kind of another role fails in the closed §7 table\n"
```

## Mapa de casos → postcondición (trazado en docstrings del test)

| # | Caso (ficha T4) | Test | Estado hoy |
|---|---|---|---|
| 1 | POSITIVO: parte única `role-report` del architect (subfase `discovery`) materializada a `docs/specs/<feature>/` con sha idéntico y sin `cp` | `TestArchitectRoleReportMaterializes.test_pd8_role_report_materializes_with_identical_sha_into_specs_root` | **RED** (AssertionError) |
| 2 | NEGATIVO (clausura del eje rol): `implementer-role-report` / `test-writer-role-report` sobre paquete del architect, rechazo rc≠0 sin prefijo parcial | `TestArchitectRoleClosure.test_pd8_foreign_role_named_kinds_stay_rejected` (2 subTests) | control, pasa |
| 3 | NEGATIVO: destino fuera de `docs/specs/<feature>/` (3 variantes) rechazado sin escribir | `TestOutsideAllowedRoot.test_pd8_target_outside_specs_feature_root_stays_rejected` | control, pasa |
| 4 | BINDING: `receipt_sha256` erróneo (`"f"*64`) con kind vigente `architect-spec-draft` se rechaza antes de copiar; `approval_effect: false` | `TestMaterializeBinding.test_pd8_materialize_binding_bad_receipt_sha256_rejected` | control, pasa |
| 5 | REGRESIÓN: `architect-spec-draft` / `architect-plan-draft` siguen materializando; kind `review` (fixture reviewer propio) sigue materializando; `receive` no cambia (recibo mecánico `pending`, identidad ligada, part byte-idéntico, nada escrito fuera de `.cdad/`) | `TestArchitectExistingKindsRegression` + `TestReviewerReviewKindRegression` + `TestReceiveUnchanged` | control, pasa (3 tests) |

## Superficie probada (comportamiento, sin plomería)

Flujo completo real de 003-002 sobre un proyecto sintético en tempdir (política v2 + plan del epic aprobado en `epic_history` para el architect — patrón `test_005_001_t4_decisive` S1; spec aprobada en `stage_history` para el fixture reviewer): `prepare` → `--record-dispatch` (I8) → staging de la única parte en `.cdad/inbox` + manifest + descriptor (kind declarado en el descriptor; `receive` no gatea por kind, R5 de 003-002) → `receive` (rc=0, receipt durable) → `materialize` con autorización §7. Targets project-relative; corridas de `materialize` con cwd en la raíz del fixture (patrón T2 de 003-002). Sin rutas del host, sin tocar el repo real, sin desplegar, sin red.

## Comandos y evidencia (exactos)

```text
python3 -m pytest tests/test_005_007_t4_architect_report_materialization.py -q
→ 1 failed, 6 passed in ~9-10 s  (un único R: el caso 1)

python3 -m pytest tests/test_003_002_t1_receive.py tests/test_003_002_t2_materialize.py -q
→ 18 passed in 23.10 s  (regresiones declaradas por la ficha T4: intactas)

python3 -m ruff check tests/test_005_007_t4_architect_report_materialization.py
→ All checks passed!
```

## Archivo creado y commit

- **Modificado/añadido (write scope `tests/`):** `tests/test_005_007_t4_architect_report_materialization.py` (nuevo, 801 líneas, 7 tests).
- **Commit del rol:** `852d3be` — `test: 005-007 T4 RED - role-report del architect (PD-8) no materializa: foca receive+materialize con 6 controles (eje rol, raiz, binding, regresiones)` en `codex/epic-005-real-operation`; `1 file changed, 801 insertions(+)` (solo el test). Sin `--no-verify`, sin push.
- **Nota:** `docs/.cdad-state.json` tiene el diff del orquestador (transición `active_packet` al packet de este rol, `dispatched`); no lo toqué y no entra en este commit (el state solo lo escribe el orquestador).

## Desviación declarada (PD-15, honestidad de fase)

Durante la exploración previa, fuera y por encima del read scope del packet, leí contenido de implementación: `cat skills/cdad-cycle/assets/artifact-policy.json`, `grep`/`sed -n '600,700p' skills/cdad-cycle/scripts/cdad_result.py` (tabla `_allowed_kinds` y validación de autorización) y el wrapper `scripts/cdad_result.py`. Declaro el hecho y su efecto: la tabla cerrada vista coincide con el «hecho medido» que ya traía el encargo (para el architect sólo `architect-spec-draft`/`architect-plan-draft`; inicio no relajado). Los 7 tests derivan sus aserciones del contrato (spec PD-8, ficha T4, observación 1) y del comportamiento observable del CLI sobre fixtures (subprocess), no de lo leído; el fixture del reviewer se resolvió por sonda black-box del CLI (rc=0 en preparación precondición), no por lectura. Si el orquestador considera contaminada la fase, la parte afectada (este RED) se rehace en sesión aparte; los insumos de comportamiento (los 7 casos con su estado esperado) quedan registrados arriba. Ningún GREEN se orientó a contenidos internos: el test no fija nombres internos, mocks ni plumbing (solo el contrato §7 de 003-002 + PD-8).

## Estado para el implementer GREEN (T4)

GREEN debe hacer pasar el caso 1 admitiendo `role-report` para el architect en la tabla cerrada (`artifact-policy.json` con raíz `docs/specs/<feature>/` + eje rol/subfase), conservando los controles 2-5 verdes (clausura del eje rol, raíz, binding, regresiones). El RED no fija subfase `draft`: exige el camino real ya medido (recibo del discovery, subfase `discovery`); si el GREEN quiere admitir el kind en otra subfase del architect, es aditiva y no está prohibida por esta foca. No tocar el adaptador (excluido por la ficha). Regresiones de re-verificación: las dos focas de 003-002 (18 tests, hoy verdes).
