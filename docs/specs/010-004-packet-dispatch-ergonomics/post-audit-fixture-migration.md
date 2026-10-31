# FINAL TEXT — test-writer POST-AUDIT correctivo T2 (010-004, packet `-post-audit-004`)

## 0. Validación de entrada (Route C)

- Scripts de **repositorio** (`skills/cdad-cycle/scripts/cdad_packet.py --project-root .`); no se usó ni modificó la copia global (drift D-1 respetado; nada instalado/reinstalado).
- `validate-request` → exit 0 · `validate-packet` → exit 0 · `render` vs `PACKET.md` → **byte-idéntico** (14.834 bytes) · sha256 PACKET `e31b7c4f…` ✓ · pins spec/plan verificados por `validate-packet` (exit 0).
- Implementación no leída: ningún archivo de `skills/`, `scripts/`, `sources/`, `agents/`, `build/`; el CLI solo se ejecutó black-box (probe de medición). Edición restringida a `tests/**`.

## 1. Traza por archivo modificado

**C1 — migración de convención (PC-04/§4.1: preparación nueva recibe el MISMO documento v2 en `.cdad/executions/<execution_id>/execution.json`).**

| Archivo | Convención anterior | Convención nueva | Clase | Decisión/PC | Tests afectados |
|---|---|---|---|---|---|
| `tests/test_packet_prepare.py` | `PrepareProject.execution_path` (:152-153) devolvía `ROOT/EXECUTION.json`; `args()` (:155-164) lo pasaba a `prepare` | El getter (`execution_path`) materializa al primer acceso el mismo documento (mismo `EXECUTION_ID` `exec-003-001-role-packets-001`) en `.cdad/executions/<id>/execution.json` y `args()` hereda la ruta canónica sin tocar líneas | C1 | §4.1 + PC-04 | los 19 del archivo (8 C1 → 绿 excepto residuales §5) |
| `tests/test_006_006_u1_draft_object_form.py` | factory `project()` sin materializado | materializa el contexto canónico en la construcción | C1 | PC-04 | 16 C1 → 21/21 |
| `tests/test_004_003_t4_validation_fields.py` | ídem | ídem | C1 | PC-04 | 8 → 11/11 |
| `tests/test_005_007_t2_progressive_plan_validator.py` | ídem | ídem | C1 | PC-04 | 6 → 6/6 |
| `tests/test_004_003_t3_plan_checks.py` | ídem | ídem | C1 | PC-04 | 5 → 5/5 |
| `tests/test_004_003_t2_plan_review.py` | ídem + sitio inline :299 (test instalado) | ídem (factory + inline) | C1 | PC-04 | 5 → 5/5 |
| `tests/test_004_003_t1_draft_contract.py` | ídem | ídem | C1 | PC-04 | 2 → 2/2 |
| `tests/test_004_003_t2_reviewfix.py` | ídem | ídem | C1 | PC-04 | 2 → 2/2 |
| `tests/test_004_003_t1_reviewfix.py` | ídem | ídem | C1 | PC-04 | 2 → 2/2 |
| `tests/test_005_007_reviewfix_blockings.py` | ídem | ídem | C1 | PC-04 | 1 → 2/2 |
| `tests/test_006_005_u1c_packet_agent.py` | consumidor central (sin tocarlo) | convención central en `PrepareProject` | C1 | PC-04 | 4 → 5/5 |
| `tests/test_006_006_u3_review_route_and_gate.py` | ídem | ídem | C1 | PC-04 | 2 → 12/12 |
| `tests/test_005_007_t6_templates.py` | ídem | ídem | C1 | PC-04 | 1 → 4/4 |

**C2 — expectativa sustituida (única aserción cambiada, trazada):**

| Archivo | Anterior → nueva | Clase | Traza completa |
|---|---|---|---|
| `tests/test_004_002_t7_acceptance.py` `_cell_legacy` (:430-473) | esperaba rc=0 + `stdout.startswith(PACKET_BEGIN)` (intake implícito v1 sin policy publicando paquete) → espera **rc≠0, stdout vacío, `published_packets=={}`, v1 byte-idéntico, sin contexto v2 fabricado, state sin binding v2 ni `active_packet` (INV-11)**; espeja el patrón verde de `test_004_002_t6_landing.py::TestPd12LegacyIntake`. Celdas restantes de la matriz: sin cambio. | C2 | `test_004_002_t7_acceptance.py:430-473` (exp. PD-12) → `docs/specs/004-002-project-execution-bootstrap/spec.md:112-115` (PD-12) → `docs/specs/010-004-packet-dispatch-ergonomics/owner-decision-v2-new-assignments.md:3-13` → `010-004/spec.md` §7 **N-3** (:453) + **PC-04** (:406) + **INV-11** (:446) |

**Desviación declarada (punto central 1 del packet):** `tests/test_role_packets.py::StateFixture` (:247) quedó **byte-idéntico**. Razón medida (probe black-box): toda escritura canónica eager en la capa `StateFixture`/`PacketFixture`/`PrepareProject.__init__` deja `.cdad` pre-existente y el test protegido byte-idéntico `test_p2_default_execution_context_and_out_dir_under_project_cdad` hace `cdad_dir.mkdir()` **plano** (:416) → `FileExistsError`. El migrado se realiza en el punto 2 (`PrepareProject.execution_path` con materializado — provado: `prepare` rc=0 solo con contexto canónico y no altera el documento canónico; `changed` del árbol = solo `docs/.cdad-state.json`).

## 2. Diff completo

Mostrado hunk por hunk arriba en la sesión y contenido byte-exacto en el commit `db8aa9c6` (`git show db8aa9c6`): 11 archivos de `tests/**`, `100 insertions(+), 21 deletions(-)`. Los 3 verfiles editados: (i) getter de `PrepareProject.execution_path` (test_packet_prepare.py :151-173); (ii) celda C2 `_cell_legacy` (t7 :430-473); (iii) 9 materializados-en-construcción (8 factories + 1 sitio inline en t2_plan_review).

## 3. Evidencia real (comandos + líneas resumen)

**(a) 14 archivos migrados — antes → después** (`python3 -m pytest tests/<f>.py -q --tb=line -rf -p no:cacheprovider`):

```
baseline (evidencia obligatoria): 63 FAILED = 62 C1 + 1 C2
test_packet_prepare 8→3 · u1_draft_object_form 16→0 · t4_validation_fields 8→0
t5_t2_progressive_plan_validator 6→0 · 004_003_t3_plan_checks 5→0 · t2_plan_review 5→0
u1c_packet_agent 4→0 · u3_review_route_and_gate 2→0 · 004_003_t2_reviewfix 2→0
t1_reviewfix 2→0 · t1_draft_contract 2→0 · t6_templates 1→0 · reviewfix_blockings 1→0
t7_acceptance (C2) 1→0      TOTAL: 63 → 3
```

**(b) Tests protegidos — 14 pasan pró todos, sin tocarlos:**

```
python3 -m pytest tests/test_010_004_t2_red.py <2 POST-AUDIT> <4 PC-08a render> <PC-08a CRLF> <C3 f6> -q
14 passed in 46.36s   (6 RED T2 ✓ · 2 POST-AUDIT ✓ · 5 PC-08a ✓ · C3 f6 ✓)
```

`test_p5_installed_cli_prepare_matches_repo_prepare`: **pasó** (16 passed del archivo) — sin deriva D-1 observable en esa superficie: preparación aprobada en ambos CLI (instalado atrasado aun admite ruta canónica con el mismo output).

## 4. Declaración de no-debilitamiento

- **Fuera de la celda C2: NINGUNA aserción agregada, quitada ni relajada.** Los 9 mint hunks de fixture contienen cero aserciones (materializado en construcción + comentarios).
- **Dentro de C2 (sustitución N-3, autorizada por spec §7)**: `assertEqual(rc,0)`→`assertNotEqual(rc,0)`; `assertTrue(stdout startswith(PACKET_BEGIN))`→ sustituido por `assertEqual(stdout,"")` + `published_packets(root)=={}` (más fuerte: nada publicado); se **agregan** `assertIsNone(state["execution"])` y `assertIsNone(state["active_packet"])` (INV-11); docstring actualizado con la traza N-3. Se conservan el escenario y las aserciones vigentes (v1 intacto, no fabricar v2).
- `git status --porcelain`: solo los 11 `tests/**` (ya committeados) + el untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md` tal cual. Sin suite completa, sin push.

## 5. Fallos residuales (los 3 de `test_packet_prepare`, causa exacta; NO absorbidos)

1. `test_p1_prepare_writes_three_files_and_stdout_equals_packet_and_render` (oráculo de conjunto `added`, línea 242-248): el literal incluye `".cdad"` como creación de `prepare`; bajo la convención migrada el_material_context puede existir `pre-prepare;` y las entradas `.cdad/executions/<id>*/` y `already` no declaradas en el esperado. Causa distinta — hyphen del oráculo — atribolución en emienda del mismo (la factory no puede materializar sin romper el `mkdir()` plano del protegido p2).
2. `test_p4_unserializable_state_fails_without_effects` (igualdad de árbol, línea 710): el_material_context existe antes… — `args()` evaúla el getter entre el `before` y el `after` → el árbol "cambia" por la fixture, no por prepare (prepare falla limpio, exit 2 con estado intacto).
3. `test_p2_default_request_derivations_per_role` (`:377`): el request de GREEN T2 ahora declara `execution_context=".cdad/executions/<execution_id>/execution.json"` (PC‑04‑c positivo, spec :406) y el dict esperado del conjunto cerrado no tiene el campo. Es una expectativa que la spec §7 ordena actualizar "con trazabilidad al requisito (PC‑04)… lista no exhaustiva", PERO el packet de esta subfase limita cambios de aserción a la celda C2 → **se escala al orquestador** (actualización trazada a PC‑04‑c en un dispatch propio; no se corrigió aquí).

Ninguno exige decisión de producto; los tres son oráculos de expectativaFixture/conjunto cerrado que el producto PC‑04 exige evolucionar. La C3 de t2_bootstrap fue resuelva por producto en `3eda073a` ✓ (14/14 verdes confirma).

## 6. Commit

```
db8aa9c6d6f4d2e01c02d02634dc9a5c165a2a13
test: migrar fixtures al contexto v2 canonico (010-004 T2, POST-AUDIT correctivo)
11 files changed, 100 insertions(+), 21 deletions(-)
```

Fin de la subfase: POST-AUDIT correctivo entregado. No escribí tests nuevos, no inicié RED, no implementé producto ni corrí la suite completa — los residuales §5 quedan escalados al orquestador con su causa exacta.
