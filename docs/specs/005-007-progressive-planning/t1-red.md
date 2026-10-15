# Informe RED — T1 / 005-007-progressive-planning (test-writer)

Packet: `005-007-progressive-planning-test-writer-red-001` · role: test-writer · substage: red
Contrato: `docs/specs/005-007-progressive-planning/spec.md` (sha256 `54877103d622ca75994b503ee4be016bf39682c2c6a6f89962a8436d8d309a4a` — verificado contra el archivo antes de leerlo).
Plan: `docs/specs/005-007-progressive-planning/plan.md` (sha256 `1f636260c81bd74cbeb7c2778fa9902b2e517c902b061e9fe2dba721861d3430` — verificado).

## 1. Archivo escrito (única modificación; dentro del write scope `tests/`)

- `tests/test_005_007_t1_progressive_detail_rule.py` (nuevo, 342 líneas).
- Oráculo de consistencia ESTRUCTURAL caja negra (clase ya usada en este repo,
  p. ej. `tests/test_005_006_t4_readme.py`); los archivos de producto se leen
  AL EJECUTARSE (archivo faltante = estado conductual → `pytest.fail`).
- Ningún oráculo derivado de implementación: el test-writer NO leyó
  `skills/**`, `scripts/**`, `sources/**`, `agents/**`, `build/**` ni
  `install.sh` (raíces declaradas de implementación en la path policy).

## 2. Propiedades → postcondiciones (docstring enumera el mismo mapeo)

| Test | Postcondición | Qué fija (estructural) |
|---|---|---|
| `test_p1_pd1_canonical_home_declares_detail_marker_and_closed_values` | **PD-1** (§6 D1/D2) | El hogar canónico `skills/cdad-cycle/references/stage-2-specification.md` declara el token `detail` y los valores `"next"` y `"planned"` co-occurrentes con el marcador en una ventana de ≤4 líneas. |
| `test_p2_pd1_pd2_planned_fields_and_validation_plan_scoping` | **PD-1 + PD-2** | En la sección por heading que contiene `detail` + `"planned"`: los cinco campos exigidos a la tarea planificada (`objective`, `depends_on`, `uncertainty`, `owner`, `resolves_when`) aparecen; el plan de validación por tarea (`focal_tests`/`observable_checks`/`regressions`/`integration_gate`) queda declarado **exigido a `"next"`/sin marcador** (co-ocurrencia ≤3 líneas con el ámbito «next/sin marcador») y **no** en la misma línea de una tarea `"planned"`. |
| `test_p3_pd12_format_section_41_declares_field_by_reference` | **PD-12** (§6 D1) | `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` tiene una sección 4.1; ahí el token `detail` aparece y hay una REFERENCIA a la regla o su hogar (`stage-2-specification.md` / «regla de detalle progresivo» / `progressive-detail`). Se afirman token y referencia, no prosa. |
| `test_p4_pd12_reviewer_plan_review_consumes_marker_by_reference` | **PD-12** | `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` menciona `detail` y referencia la regla/su hogar. |
| `test_p5_pd12_single_source_no_second_copy_of_closed_value_set` | **PD-12** (fuente única) | El par de valores cerrados está en el hogar canónico; y, para CUALQUIER otro `.md` bajo `skills/cdad-cycle/references/**` y `skills/cdad-cycle/packets/**`, si re-enuncia el conjunto cerrado, ese archivo referencia la regla/su hogar. Comprobación explícita y estructural. |

Sin asserts de prosa completa, de estilo ni de número de líneas; sin skip.

## 3. Comando exacto ejecutado (RED)

```
python3 -m pytest tests/test_005_007_t1_progressive_detail_rule.py -q
```

(también `-v` y `--tb=no` para el detalle de abajo; mismo resultado)

## 4. Salida — resumen final de pytest (la prueba del RED)

```
FAILED tests/test_005_007_t1_progressive_detail_rule.py::test_p1_pd1_canonical_home_declares_detail_marker_and_closed_values
FAILED tests/test_005_007_t1_progressive_detail_rule.py::test_p2_pd1_pd2_planned_fields_and_validation_plan_scoping
FAILED tests/test_005_007_t1_progressive_detail_rule.py::test_p3_pd12_format_section_41_declares_field_by_reference
FAILED tests/test_005_007_t1_progressive_detail_rule.py::test_p4_pd12_reviewer_plan_review_consumes_marker_by_reference
FAILED tests/test_005_007_t1_progressive_detail_rule.py::test_p5_pd12_single_source_no_second_copy_of_closed_value_set
5 failed in 0.04s
```

**5 collected, 5 failed, 0 passed.** Razones exactas (todas `AssertionError` de comportamiento, ninguna por ImportError/SyntaxError/NameError/fixture; una colección previa con `re.PatternError` fue un bug del oráculo del propio test, corregido ANTES del RED efectivo):

- P1 (línea ~166): `PD-1/D1: el hogar canónico skills/cdad-cycle/references/stage-2-specification.md no declara el marcador por tarea \`detail\`.`
- P2 (línea ~203): `PD-1/D2: el hogar canónico no declara la tarea planificada-no-detallada (ninguna sección contiene \`detail\` con el valor "planned").`
- P3 (línea ~282): `PD-12/D1: la sección 4.1 del formato no menciona el marcador por tarea \`detail\` (el campo del bloque plan-tasks quedará sin declarar).`
- P4 (línea ~301): `PD-12: la subfase skills/cdad-cycle/packets/substages/reviewer-plan-review.md no menciona el marcador \`detail\` que debe consumir.`
- P5 (línea ~322): `PD-12: el conjunto cerrado de valores del marcador ("next"|"planned") no está declarado en el hogar canónico.`

El RED es correcto: cada fallo afirma el AUSENTE de la postcondición (la regla
no vive aún en su hogar canónico; el formato y el reviewer no la referencian),
que es lo que la tarea GREEN de T1 escribirá.

## 5. Alcance y commit

- `git status` tras el trabajo: sólo `tests/test_005_007_t1_progressive_detail_rule.py` (nuevo, mío) + `docs/.cdad-state.json` (MODIFICADO POR EL ORQUESTADOR: es el `active_packet` del despacho de este paquete — escritor único del CLI; no fue editado ni commiteado por mí).
- `git diff` acotado al archivo de test. Nada fuera de `tests/` fue modificado por esta sesión.
- Commit: **`16a89ad`** (`16a89ad410d76e8cbe324816d63a152375b6e0b0`), rama `codex/epic-005-real-operation`, mensaje con prefijo `test:` — "test: 005-007 T1 RED — regla de detalle progresivo y su hogar canonico (PD-1, PD-12)". Sin `--no-verify`; pre-commit corrió.

## 6. Nota para el GREEN de T1

El paquete T1 escribe la regla en el hogar canónico, el campo en la sección 4.1
del formato (por referencia) y el marcador en `reviewer-plan-review.md` (por
referencia). Ninguna de las cinco propiedades exige prosa específica: sólo el
hogar canónico ya declarado. Los oráculos son compatibles con
`detail: "next"` | `"planned"`, con backticks o comillas, y con tantas
secciones de la regla como el GREEN declare (acepta cualquiera que cumpla).
