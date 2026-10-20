GREEN de U3 completo. Informe de rol:

## Archivos modificados (4 — exactamente los declarados en el paquete)

| Fichero | +/− | Qué cambia |
|---|---|---|
| `skills/cdad-cycle/references/stage-2-specification.md` | +34/−3 | Subfase de revisión del borrador (despacho → recepción del dictamen → ruteo de bloqueantes → re-review focal → recién entonces aprobación), exit gate con `plan-review.md` + condición de bloqueantes, forma declarada de la exención (los cuatro campos) |
| `skills/cdad-cycle/SKILL.md` | +3/−1 | Criterio en el gate 2→3 (espejo del 4→5) + flecha del mapa del ciclo rotulada `draft reviewed — plan-review.md` |
| `skills/cdad-cycle/references/re-entry.md` | +24/−0 | Re-entry del dictamen de borrador (bloqueantes / re-review focal / exención) + sección propia con la política de compatibilidad entre revisiones y sus dos salidas |
| `skills/cdad-cycle/references/handoff-prompts.md` | +13/−6 | La plantilla `plan-review` declara `--object-kind`, `--spec-path`, `--spec-version`; no re-enuncia el procedimiento (sigue referenciando el substage pineado) |

**No tocaré:** `tests/` (0 líneas en el commit), `skills/cdad-cycle/scripts/` (el CLI no cambia; el gate sigue supervisado), `docs/.cdad-state.json` y los untracked de `docs/planning/` y `findings/` (ajenos, del orquestador). Nunca leí ni escribí el HOME.

## Tabla test → resultado

| Comando | Tests | Resultado |
|---|---|---|
| `pytest tests/test_006_006_u3_review_route_and_gate.py` | 12 (focal) | **12 passed** — los 9 RED + los 3 controles |
| regresiones de la ficha (intake 005-006 T2, render/paquetes de rol, `cdad-generate`, detalle progresivo 005-007 T1, informe del architect 005-007 T4, materializar 003-002 T2) | 59 | **59 passed** |
| regresión proporcional extra (13 ficheros que leen estas 4 superficies: T6/T7 de 005-007, 006-005 reviewfix2, 006-002 u2/u3/u4/u5/u6, 006-003 u3/u5p, 005-009 T3, 005-006 T6, static-block ceiling) | 86 | **86 passed** |
| `test_packet_prepare.py` + `test_role_packet_consumers.py` | 24 | **24 passed** |
| hermanas 006-006 (U1, U2, U5) | 42 | **42 passed** |
| `make validate` | 168 asserts | **168 PASS / 1 FAIL — idéntico a la línea base previa a mi cambio** |

## Comandos con salida

```
$ python3 -m pytest tests/test_006_006_u3_review_route_and_gate.py -v
12 passed in 5.20s

$ python3 -m pytest tests/test_005_006_t2_intake.py tests/test_role_packet_render.py \
    tests/test_role_packets.py tests/test_cdad_generate.py \
    tests/test_005_007_t1_progressive_detail_rule.py \
    tests/test_005_007_t4_architect_report_materialization.py tests/test_003_002_t2_materialize.py -q
59 passed in 139.35s (0:02:19)

$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
```

**F011 es ambiental y preexistente** (mismo assert, mismo conteo antes y después de mi cambio). Causa medida con `bash scripts/validate-subagents.sh`: (a) `install.sh --check` da DRIFT de la copia instalada `~/.claude/skills/cdad-cycle/{references/stage-2-specification.md, SKILL.md}` — la instalación se refresca por el flujo del owner, yo no toco HOME; (b) el agente instalado `~/.config/opencode/agents/cdad-reviewer.md` declara `model:` (artefacto del HOME, preexistente); (c) `build/staging` ausente. No hay ningún assert verde que se haya vuelto rojo.

**Regeneración:** `make staging` produce salidas **byte-idénticas** a los `agents/` trackeados (0 diferencias) ⇒ ningún artefacto generado deriva de estos cuatro ficheros ⇒ **no queda diff pendiente**. `build/` está en `.gitignore`.

## Decisiones que declaro

1. **Sin renumerar las subfases de la etapa 2.** La subfase nueva va **sin número** (`## Draft review sub-phase (plan-review) — …`), entre la 2.2 y la 2.3, para que «Sub-phase 2.3 — Approval» conserve su número y las dos referencias externas `§2.3/Layer 2` (`SKILL.md:365`, `stage-4-review.md:169`) sigan siendo válidas. Renumerar habría obligado a tocar un **quinto** fichero fuera de la lista declarada de la ficha. El orden del procedimiento (revisión **antes** de la aprobación) queda respetado.
2. **La política de compatibilidad es declaración, no cambio del renderer** (D-12): sección propia en `re-entry.md` junto a la re-entry del dictamen; el CLI no distingue la causa del rechazo y no lo he tocado.
3. Los dos controles negativos de PD-10 siguen verdes: el gate 2→3 permanece **supervisado** (con aprobación vigente y sin dictamen, `prepare` rc=0; sin aprobación, rc≠0 con `approval pending`).

## Commit

```
06f76bb feat: 006-006 U3 — revision del borrador en el recorrido y el gate 2->3
 skills/cdad-cycle/SKILL.md                         |  4 ++-
 skills/cdad-cycle/references/handoff-prompts.md    | 19 ++++++----
 skills/cdad-cycle/references/re-entry.md           | 24 ++++++++++++++
 skills/cdad-cycle/references/stage-2-specification.md | 37 ++++++++++++++++++++--
 4 files changed, 74 insertions(+), 10 deletions(-)
```

Sin `--no-verify`, sin `git stash` (0 entradas), sin push. **La suite completa no se corrió** (política del paquete: la corre una vez quien cierra).