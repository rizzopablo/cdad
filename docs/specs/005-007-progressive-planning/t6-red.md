# Informe RED — 005-007 T6 (plantillas alineadas) · rol test-writer, subfase red

Packet: `005-007-progressive-planning-test-writer-red-008`
Contrato: `docs/specs/005-007-progressive-planning/spec.md` (sha256 `54877103…a4a`, APROBADA 2026-10-13). Postcondiciones aplicables: **PD-5**, **PD-6** (+ PD-10 como receta referenciada, PD-12 como fuente única). Plan: `docs/specs/005-007-progressive-planning/plan.md` (ficha T6, `:111-121`).

## Qué se escribió

**Archivo modificado (write scope = `tests/`):** `tests/test_005_007_t6_templates.py` (nuevo, 428 líneas; commit `95516ef`). Patrón: RED estructural de T1 de esta misma feature (lectura de producto al ejecutarse, archivo faltante = `pytest.fail` de estado conductual, tokens por familias de presencia — sin prosa pineada) + fixture `prepare` de T2/T3-de-004-003 (proyecto temporal, CLI invocado como subprocess, cero lecturas de implementación para derivar oráculos; los archivos de producto se leen solo al EJECUTAR los tests).

Cuatro tests, uno por caso exigido, cada uno trazado a su postcondición:

| Test | Postcondición | Oráculo (derivado solo del contrato) |
|---|---|---|
| `test_case1_pd5_spec_template_opens_from_user_journey` | PD-5 / AC-5-1ª | `assets/spec-template/spec.md` abre con las cuatro piezas del recorrido (actor, objetivo, punto de partida legítimo, primer resultado útil) en la apertura (título + preámbulo + 1ª sección nivel ≤2; los `###` quedan dentro); la firma no es el primer bloque; la sección de aceptación se ancla a comportamiento y el literal de cobertura **no** está en todo el archivo |
| `test_case2_pd6_feature_plan_template_block_validates_with_product` | PD-6 / AC-5-2ª | `assets/feature-plan-template.md` con ficha + EXACTAMENTE UN bloque `plan-tasks`; el bloque se EXTRAe tal cual, se arma un fixture mínimo (proyecto temporal, ficha `draft-plan` verde de 004-003/T1) con ese bloque en `plan.md`, y `prepare` lo ACEPTA (rc=0) curación del validador del producto |
| `test_case3_pd6_pd10_stage2_references_template_and_use_acceptance_recipe` | PD-6/PD-10 | `stage-2-specification.md` menciona la plantilla por su nombre de asset y ancla la receta mínima de aceptación de uso; la referencia no re-enuncia la regla (ventana corta alrededor de la mención) |
| `test_case4_pd12_single_source_format_and_rule` | PD-12 | el formato sigue declarado UNA VEZ en `planning-contract-draft.md` §4.1 (sección + token `plan-tasks` presentes); la plantilla REFERENCIA §4.1 y, si re-enuncia el conjunto cerrado del marcador, referencía la regla/su hogar; ni plantilla ni la referencia del caso 3 re-enuncian la regla |

## Comandos ejecutados

```
python3 -m pytest tests/test_005_007_t6_templates.py -q
python3 -m pytest tests/test_005_007_t1_progressive_detail_rule.py tests/test_005_007_t2_progressive_plan_validator.py -q
git add tests/test_005_007_t6_templates.py
git commit -m "test: 005-007 T6 RED — plantillas alineadas (recorrido de uso + plantilla de plan de feature)" tests/test_005_007_t6_templates.py
```

## Salida RED (exacta, resumida)

```
4 failed in 0.57s
FAILED test_case1_pd5_... — AssertionError: la apertura no deriva de un recorrido de uso: faltan las piezas ['actor', 'objetivo', 'punto de partida legitimo', 'primer resultado util']
FAILED test_case2_pd6_... — Failed: archivo requerido no existe: skills/cdad-cycle/assets/feature-plan-template.md   (estado conductual, convención del RED de T1)
FAILED test_case3_pd6_... — AssertionError: stage-2-specification.md no referencia la plantilla de plan de feature (assets/feature-plan-template.md)
FAILED test_case4_pd12... — Failed: archivo requerido no existe: skills/cdad-cycle/assets/feature-plan-template.md
```

Estatus RED: **4/4 fallan HOY**, cada uno por la aserción esperada (comportamiento faltante / archivo requerido ausente como estado conductual) — **ninguno** por ImportError/SyntaxError/NameError o error de fixture. Coherente con el contrato: hoy la plantilla de spec abre por `Signature` y pide cobertura (`spec-template/spec.md:17-21,41`), no existe plantilla de plan de feature (`discovery.md:176-179`) y stage-2 no la referencia.

Regresión focal: los vecinos de la misma fuente siguen verdes:

```
python3 -m pytest tests/test_005_007_t1_progressive_detail_rule.py tests/test_005_007_t2_progressive_plan_validator.py -q
→ 11 passed in 4.88s
```

(No se corre la suite completa: política declarada en el packet — la corre una vez quien cierra.)

## Commit

```
95516ef5c2f93003696264517dd7c64b4f75d40f test: 005-007 T6 RED — plantillas alineadas (recorrido de uso + plantilla de plan de feature)
 tests/test_005_007_t6_templates.py | 428 +++++++++++++++++++++++++++++++++++++
 1 file changed, 428 insertions(+)
```

Rama: `codex/epic-005-real-operation`. Diff acotado a `tests/` (write scope respetado; ni `src`/`skills`/`docs` tocados). Sin `--no-verify`, sin push.

## Decisiones de oráculo declaradas (resumen)

- Tokens de las cuatro piezas del recorrido en familias bilingual ES/EN (`actor|usuario|…`, `objetivo|goal|…`, `punto de partida|starting point|…`, `primer resultado|first result|…`): PRESENCIA, no rotulado exacto — como pide el encargo.
- «Acertura» definida estructuralmente (hasta la 2ª sección de nivel ≤2); «sección de aceptación» = primer título nivel ≤3 que hable de aceptación/criterios.
- Cobertura retirada: literal `Line coverage ...` / `cobertura de líneas` prohibido en TODO el archivo.
- Bloque de la plantilla: datos `plan-tasks` con fence normalizado `^[ \t]{0,3}` y exactamente **un** bloque; parseo JSON fail-loud (`fail` de unittest = AssertionError, nunca excepción de fixture) y `tasks` lista no vacía; el resto del formato lo juzga el validador del producto al correr `prepare`.
- `pytest.fail` por archivo requerido ausente = convención de estado conductual del RED de T1 de esta misma feature (el archivo faltante ES el comportamiento faltante de PD-6, no un error del oráculo).
