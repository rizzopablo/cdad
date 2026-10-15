# Informe GREEN — 005-007 T6 (plantillas alineadas) · rol implementer, subfase green

Packet: `005-007-progressive-planning-implementer-green-008`.
Contrato: `docs/specs/005-007-progressive-planning/spec.md` (sha256 `54877103…a4a`). Postcondiciones: **PD-5**, **PD-6** (+ PD-10 y PD-12 por referencia). Plan: `docs/specs/005-007-progressive-planning/plan.md` (ficha T6).
Oraculo CONGELADO: `tests/test_005_007_t6_templates.py` (commit `95516ef`) — **no editado**.

## Archivos modificados (write scope: `skills/`; exactamente 3 archivos)

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/assets/spec-template/spec.md` | Modify |
| `skills/cdad-cycle/assets/feature-plan-template.md` | Create (nuevo) |
| `skills/cdad-cycle/references/stage-2-specification.md` | Modify |

## Que se implemento

1. **PD-5 — la plantilla de spec abre por el recorrido de uso.** La apertura (titulo + preambulo, antes de la primera seccion `##`) declara el recorrido en etiquetas explicitas: `Actor`, `Goal`, `Legitimate starting point`, `First useful result`, mas una linea funcional derivada de ese recorrido. La **firma dejo de ser el primer bloque**: no queda ningun token de firma/codigo en la apertura; el contrato (postcondiciones numeradas + invariantes) se conserva, con la firma como detalle de soporte dentro de `## Contract`. La seccion de aceptacion es **comportamiento observable sobre el recorrido** (titulo `## Acceptance criteria (observable behavior over the journey)` y bullets observables, incluido un camino de recuperacion); el item «Line coverage … X%» se **retiro del archivo completo** (no aparece el literal ni su variante en español). El resto del esqueleto (out of scope, notas, contexto tecnico, status) se mantiene integrado.
2. **PD-6 — plantilla de plan de feature (nueva).** `assets/feature-plan-template.md` lleva la **ficha** de la feature (`Feature ID` + plan version, resultado observable, postcondiciones cubiertas, alcance in/out, consume/produce, contexto global) y **exactamente un** bloque canonico `plan-tasks` con `validation_strategy` y dos tareas de ejemplo que declaran `id`, `objective`, `produce`, `consume`, `depends_on`, `parallel`, `files`, `focal_tests` (tarea con codigo) u `observable_checks` (tarea sin codigo), `regressions`, `integration_gate` y `owner`. Es **consumidor** del formato: lo referencia por su unica declaracion (`docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4.1) y no la re-enuncia. El bloque extraido tal cual es ACEPTADO por `prepare` del producto (el propio oraculo lo prueba con un fixture temporal).
3. **PD-6/PD-10 — stage-2 referencia, no duplica.** `references/stage-2-specification.md` gana la subseccion `### Feature plan template`: referencia la plantilla por su nombre de asset (`assets/feature-plan-template.md`) y **ancla por nombre** la «minimum acceptance-of-use recipe» (contract / integration / use, cada capa con su productor, actor evaluador y evidencia), dejando su detalle por referencia. No agrega una segunda copia del formato: la mencion de `planning-contract-draft.md` sigue siendo **una sola** en el archivo, no hay fence `plan-tasks` y no hay re-enunciado del conjunto cerrado del marcador `detail` en la ventana de la referencia.

## Comandos y salidas (exactas)

### RED de partida (verificado antes de tocar producto)

```
$ python3 -m pytest tests/test_005_007_t6_templates.py -q
4 failed in 0.56s
FAILED test_case1_pd5_... FAILED test_case2_pd6_... FAILED test_case3_pd6_... FAILED test_case4_pd12_...
```

### Oraculo congelado (despues del GREEN)

```
$ python3 -m pytest tests/test_005_007_t6_templates.py -q
....                                                                     [100%]
4 passed in 0.72s
```

### Regresion proporcional (declarada)

Tests existentes que tocan los assets/references modificados:

- `skills/cdad-cycle/references/stage-2-specification.md` (modificado): lo leen `tests/test_005_007_t1_progressive_detail_rule.py` (P1/P2: hogar canonico del marcador `detail`; P5: fuente unica de la skill) y `tests/test_004_003_t4_validation_fields.py` (`TestFA`: el consumidor referencia el hogar canonico §4.1 **exactamente una vez** y no re-declara el formato); `tests/validate-consistency.sh` tambien lo inspecciona (redaccion AP-10/B11).
- `skills/cdad-cycle/assets/spec-template/spec.md` (modificado): solo lo lee `tests/test_005_007_t6_templates.py` (verificado: `grep -rn "spec-template" tests/*.py tests/*.sh Makefile scripts/*.sh skills/cdad-cycle/scripts/*.py`).
- `skills/cdad-cycle/assets/feature-plan-template.md` (nuevo): solo lo lee el oraculo de T6.

Ademas del area de plantillas/documentacion se corrieron los tests de plan/paquetes ya usados en T2 (el bloque de la plantilla es consumido por el validador del producto):

```
$ python3 -m pytest tests/test_005_007_t1_progressive_detail_rule.py tests/test_005_007_t2_progressive_plan_validator.py tests/test_004_003_t1_draft_contract.py tests/test_004_003_t3_plan_checks.py tests/test_004_003_t4_validation_fields.py tests/test_packet_prepare.py -q
................................................                         [100%]
48 passed in 30.01s
```

Chequeo de consistencia del repo (documental, proporcional; no es la suite):

```
$ bash tests/validate-consistency.sh
Assert PASS: 141
Assert FAIL: 2
FAIL: 2 assert(s) failed.
```

Las dos fallas son **pre-existentes y ajenas a este cambio**: (a) `F011: scripts/validate-subagents.sh` compara el arbol contra las copias instaladas (`~/.claude/...`) y ya reporta drift en archivos que NO toque — `~/.claude/skills/cdad-cycle/assets/artifact-policy.json` y los 11 agentes (`diff -q` confirma que difieren); (b) `tests/validate-odoo-specialization.sh` falla en A3 por patrones sensibles en `docs/specs/005-010-*/…`, `docs/.cdad-state.json` y `tests/__pycache__/*.pyc`, tambien ajenos. Mis tres archivos no aparecen entre los offenders (salvo el natural drift de la copia instalada de `spec-template/spec.md`, que es consecuencia esperada de instalar/actualizar, no un assert del repo).

**Politica de suite completa:** no se corrio la suite completa (la corre una vez quien cierra, por la politica declarada en el packet).

## `git diff --stat` y commit

```
$ git show --stat --format="%h %s" HEAD
594da73 feat: 005-007 T6 GREEN — plantillas alineadas con el resultado (PD-5, PD-6)

 skills/cdad-cycle/assets/feature-plan-template.md     | 79 ++++++++++++++++++++++
 skills/cdad-cycle/assets/spec-template/spec.md        | 42 +++++++-----
 skills/cdad-cycle/references/stage-2-specification.md |  6 ++
 3 files changed, 110 insertions(+), 17 deletions(-)
```

Hash completo: `594da73acad9eac4c79accc432079734faa6e79d` (rama `codex/epic-005-real-operation`). Sin `--no-verify`, sin push. `docs/.cdad-state.json` sigue modificado (lo mantiene el orquestador) y **no** entro en el commit: el diff esta acotado a los tres archivos declarados.

## Restricciones e invariantes respetadas

- **No edite `tests/`** (AP-4): el unico commit toca los tres archivos de producto; el oraculo congelado quedo intacto en `95516ef`.
- **No cambie el comportamiento del validador ni el render de paquetes**: no toque `skills/cdad-cycle/scripts/cdad_packet.py`; el bloque de la plantilla es aceptado por el validador **sin cambio alguno** (probado por el propio oraculo: `prepare` rc=0 y `PACKET.md` publicado).
- **Fuente unica (PD-12)**: el formato sigue declarado solo en `planning-contract-draft.md` §4.1; la regla de detalle progresivo sigue en `stage-2-specification.md` («Progressive detail», seccion P1/P2 verde); la plantilla no re-enuncia el conjunto cerrado del marcador `detail`; stage-2 conserva una sola mencion del hogar del formato y ningun fence `plan-tasks`.
- **Minimalidad**: solo los tres archivos exigidos; sin features extra.

## Estado del gate GREEN

- Oraculo congelado: **4 passed**.
- Regresion proporcional declarada: **48 passed** (+ consistencia del repo: 141 PASS / 2 FAIL pre-existentes ajenos).
- Commit: `594da73` (`feat:`), diff acotado a 3 archivos.
- Pendiente para el cierre (no es de este rol): la suite completa la corre quien cierra.
