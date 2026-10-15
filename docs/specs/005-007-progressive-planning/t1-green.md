# Informe GREEN — T1 / 005-007-progressive-planning (implementer)

Packet: `005-007-progressive-planning-implementer-green-001` · role: implementer · substage: green
Contrato: `docs/specs/005-007-progressive-planning/spec.md` (sha256 `54877103d622ca75994b503ee4be016bf39682c2c6a6f89962a8436d8d309a4a`).
Oraculo congelado (contrato del GREEN, NO editado): `tests/test_005_007_t1_progressive_detail_rule.py` (commit `16a89ad`).
Plan: `docs/specs/005-007-progressive-planning/plan.md` (sha256 `1f636260c81bd74cbeb7c2778fa9902b2e517c902b061e9fe2dba721861d3430`).

## 1. Que escribi (una sola vez cada cosa; solo los tres archivos declarados)

**a) Hogar canonico de la regla — `skills/cdad-cycle/references/stage-2-specification.md` (+20).**
Nueva subseccion `### Progressive detail (canonical rule)`, insertada entre
`### Task structure` y `### The central rule`. Enuncia, UNA vez: para TODAS las
unidades, objetivo y dependencias completos; el detalle (contrato, firmas y
pruebas) solo de la tanda proxima; el marcador por tarea `detail` con conjunto
cerrado `"next"` (default) y `"planned"`; una tarea `"planned"` declara
`objective`, `depends_on`, `uncertainty`, `owner` y `resolves_when` y NO declara
el plan de validacion por tarea, mientras que una tarea `"next"` o sin marcador
sigue declarando el plan de validacion por tarea
(`focal_tests`/`observable_checks`, `regressions`, `integration_gate`). Cierra
declarando que los consumidores la referencian y nunca la copian.

**b) Formato del bloque (una sola declaracion) — `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4.1 (+12/-3).**
Agregue el campo `detail` a la lista de nombres de campo por tarea y una frase
que declara sus dos valores (`"next"` default / `"planned"`) y REFERENCIA la
regla por archivo/seccion (`skills/cdad-cycle/references/stage-2-specification.md`,
seccion «Progressive detail»), sin re-enunciar la regla ni el detalle del plan
de validacion por tarea. No agregue un segundo fence `plan-tasks` (el conteo
literal del documento sigue en 1, exigido por la regresion de 004-003 T4).

**c) Consumidor de la subfase — `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` (1 linea, +1/-1).**
La revision de plan ahora consume el marcador `detail` POR REFERENCIA
(`skills/cdad-cycle/references/stage-2-specification.md`, seccion "Progressive
detail"): revisa la tarea `"planned"` por objetivo/dependencias/incertidumbre/
dueño/condicion y la `"next"`/sin marcador por su plan de validacion por tarea;
sin copiar la regla.

No agregue una segunda copia normativa de la regla ni de su conjunto cerrado; no
toque el validador (eso es T2), ni el render de paquetes, ni `tests/`.

## 2. Comando exacto del oraculo congelado y salida

```
python3 -m pytest tests/test_005_007_t1_progressive_detail_rule.py -q
```

Salida (resumen final de pytest):

```
.....                                                                    [100%]
5 passed in 0.05s
```

(Los cinco pasan: P1 hogar canonico declara marcador + conjunto cerrado; P2
campos de `"planned"` + plan de validacion anclado a `"next"`/sin marcador; P3
formato §4.1 declara el campo por referencia; P4 el reviewer consume por
referencia; P5 fuente unica.)

## 3. Regresion proporcional del area tocada

Tests que cubren la skill y los paquetes (focales existentes del area: formato
`plan-tasks`, subfase de review de plan, contrato del encargo):

```
python3 -m pytest tests/test_004_003_t1_draft_contract.py \
  tests/test_004_003_t2_plan_review.py \
  tests/test_004_003_t3_plan_checks.py \
  tests/test_004_003_t4_validation_fields.py \
  tests/test_005_003_t6_packet_contract.py -q
```

Salida:

```
..............................                                           [100%]
30 passed in 19.13s
```

Validador de consistencia del repo (`bash tests/validate-consistency.sh`):
`Assert PASS: 141`, `Assert FAIL: 2`. Los 2 FAIL son **preexistentes y ajenos**
a este cambio (`F011: scripts/validate-subagents.sh`, `F011:
tests/validate-odoo-specialization.sh`): verificado con `git stash` de los tres
archivos — el baseline ya daba exactamente los mismos 2 FAIL. El segundo es por
patrones sensibles en `docs/specs/**` ajenos a este cambio; el primero compara
el repo contra las instalaciones de HOME (`.claude/skills`, `.config/opencode/
skills`, `.agents/skills`) sin sincronizar, y la instalacion en HOME esta fuera
del alcance de este paquete (INV-6: sin desplegar, sin tocar HOME).

## 4. Diff (solo los tres archivos declarados)

```
git show --stat --oneline HEAD
 .../planning-contract-draft.md                       | 12 +++++++++---
 .../packets/substages/reviewer-plan-review.md        |  2 +-
 .../cdad-cycle/references/stage-2-specification.md   | 20 ++++++++++++++++++++
 3 files changed, 30 insertions(+), 4 deletions(-)
```

`git status --short`: solo ` M docs/.cdad-state.json` (modificado por el
orquestador — `active_packet` del despacho; escritor unico del CLI; no lo
commitee). Ningun archivo de `tests/` fue tocado.

## 5. Commit

`7ff19c17da7b7607468fe8aa01b51e75af91c3fd` (`7ff19c1`), rama
`codex/epic-005-real-operation`:

```
feat: 005-007 T1 GREEN — regla de detalle progresivo en su hogar canonico (PD-1, PD-12)
```

## 6. Limites honestos

- La suite completa **no** la corri (politica de suite: la corre una vez quien
  cierra). Corri el oraculo congelado + la regresion focal del area (5 archivos,
  30 tests) + `validate-consistency.sh`.
- Los 2 FAIL de `validate-consistency.sh` son de baseline (comprobado con
  stash); mi cambio no agrega fallos, pero el check estaba rojo antes.
- No verifique comportamiento del validador (cambio de `detail` fuera del
  conjunto cerrado, rechazo fail-closed): eso es alcance de T2 y su oraculo.
- La frase "el marcador vive en un solo lugar" se verifico por el oraculo P5
  (globs `skills/cdad-cycle/references/**` y `skills/cdad-cycle/packets/**`), no
  por revision humana de todo el repo.
