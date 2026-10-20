GREEN de U2 completado. Aquí va el informe de rol con la evidencia.

## 1. Archivos modificados

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` | El objeto pasa de «un PLAN DRAFT» al **objeto de especificación** (intención declarada, restricciones y decisiones aplicables, spec, plan cuando existe, contratos y capacidades para ejecutar y obtener evidencia); se generalizan las dos frases plan-céntricas del juicio; **se suma** la obligación de que el dictamen nombre el objeto revisado y su digest (D-9/PD-6). |
| `skills/cdad-cycle/packets/roles/reviewer.md` | La regla «qué revisar» pasa a «el objeto **que el contrato declara, con su forma declarada** (spec o plan)»; desaparece la etiqueta «the plan draft». |

`git show --stat HEAD` → **2 files changed, 2 insertions(+), 2 deletions(-)**. Nada más tocado: `docs/.cdad-state.json` (orquestador) y los untracked `docs/planning/`, `findings/*` quedan intactos y sin commitear. No hay manifiesto generado que fije el sha de estos dos archivos (el manifiesto de `build/staging` sólo pinea los 22 agentes generados; `rg` de los digests viejos → 0 coincidencias) ⇒ **no hay nada que regenerar**.

## 2. Tabla test → resultado

| Test | Oráculo | Resultado |
|---|---|---|
| `test_pd6_pd12_u2_substage_reviewed_object_is_not_the_plan_alone` | PD-6/PD-12 (O-1) | **PASS** (7/7 del focal) |
| `test_pd6_u2_substage_requires_the_dictamen_to_name_the_object_and_its_digest` | PD-6 / D-9 (O-2) | **PASS** |
| `test_pd12_u2_role_rule_names_the_contract_declared_object_with_its_form` | PD-12 (O-3) | **PASS** |
| `test_pd12_u2_substage_keeps_its_vigente_obligations` | PD-12 (O-4, guarda) | **PASS** |
| `test_pd12_u2_role_rule_keeps_its_vigente_obligations` | PD-12 (O-4, guarda) | **PASS** |
| `test_pd12_control_negative_u2_substage_is_a_consumer_not_a_second_home` | PD-12 (O-5, control negativo) | **PASS** |
| `test_v5_pd12_u2_reviewer_static_block_is_measured_and_below_the_ceiling` | V-5 / PD-12 (O-6) | **PASS** (3033 ≤ 12000) |
| `tests/test_005_007_t1_progressive_detail_rule.py` (P4/P5) | regresión 005-007 PD-12 | **PASS** (oráculo intacto) |
| `tests/test_005_007_t6_templates.py` | regresión | **PASS** |
| `tests/test_004_003_t2_plan_review.py` | regresión (sha-pinning dinámico) | **PASS** |
| `tests/test_role_packet_render.py` | regresión | **PASS** |
| `tests/test_role_packets.py` | regresión | **PASS** |
| `tests/test_006_006_u1/u2/u5_*.py` | focales de la feature | **PASS** (42) |

Ningún oráculo vigente se reemplazó (A-1 de la ficha): no hubo contradicción entre oráculos que tuviera que detener el trabajo.

## 3. Comandos y salidas

```
$ python3 -m pytest tests/test_006_006_u2_review_procedure.py -v
7 passed in 0.17s

$ python3 -m pytest tests/test_006_006_u1_draft_object_form.py \
      tests/test_006_006_u2_review_procedure.py tests/test_006_006_u5_exemption_record.py -q
42 passed in 56.06s

$ python3 -m pytest tests/test_005_007_t1_progressive_detail_rule.py \
      tests/test_005_007_t6_templates.py tests/test_004_003_t2_plan_review.py \
      tests/test_role_packet_render.py tests/test_role_packets.py -q
34 passed in 168.22s (0:02:48)     # misma cuenta que la línea base del RED

$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
make: *** [Makefile:22: validate] Error 1
```

**Medición V-5** (misma convención que el test: bytes unidos por `b"\n"`): `common.md` 901 + `roles/reviewer.md` 363 + `substages/reviewer-plan-review.md` 1767 = **3033 bytes** ≤ techo **12000** (holgura 8967; antes 2728, delta +305).

## 4. `make validate` — F011 declarado (ambiental)

`make validate` queda **rojo en el mismo único assert que la línea base del RED** (168 PASS / 1 FAIL). El `install.sh --check` que corre el validador reporta tres causas **independientes**:

| Causa | Drift | ¿Mía? |
|---|---|---|
| `scripts/cdad_packet.py` (+2 `.pyc`) en las 3 raíces | instalado = revisión anterior (documentado en `u2-red.md` §5) | **No** — no toqué el CLI |
| `MISSING (staged but not installed)`: `build/staging/agents/opencode/cdad-orchestrator.md`, `cdad-reviewer.md` | agentes staged nunca instalados | **No** — independiente de mi diff |
| `packets/substages/reviewer-plan-review.md` y `packets/roles/reviewer.md` en las 3 raíces | la copia instalada conserva los bytes previos | **Sí, y es estructural**: la copia instalada de un archivo del repo se refresca sólo con `install.sh`, que **escribe en la instalación de HOME** — prohibido por el encargo («Nunca leas ni escribas la instalacion de HOME») y fuera de mi write scope |

**Acción para el orquestador**: `install.sh` (camino declarado del repo) y después `make validate` ⇒ verde. Es la misma acción que el informe del RED ya sugería.

## 5. Commit

```
95d9e11  feat: 006-006 U2 — objeto de revision declarado por el contrato
 skills/cdad-cycle/packets/roles/reviewer.md                 | 2 +-
 skills/cdad-cycle/packets/substages/reviewer-plan-review.md | 2 +-
```
Sin `--no-verify` (el repo no tiene hooks: `.git/hooks` sólo tiene samples), sin `git stash`, sin `push`.

## 6. Limitaciones honestas (PD-15)

- **No leí la instalación de HOME.** Las líneas `DRIFT:` son la salida del propio validador del repo (`install.sh --check` ejecutado por `scripts/validate-subagents.sh`); no abrí ningún archivo instalado. No corrí el instalador.
- El diagnóstico de F011 se apoya en esa salida y en el digest de los blobs **del repo** (`git show HEAD:…` vs copia instalada registrada en `u2-red.md`), no en una lectura mía de `~/.claude`/`~/.config`.
- Intenté una comparación desde una exportación temporal de HEAD (`git archive` a `/tmp/opencode`) para aislar el estado previo: abortó pronto por falta del manifiesto de staging y **se descartó**; no conclusion resting on it.
- **No corrí la suite completa** (política del paquete: la corre una vez quien cierra).
- La medición V-5 usa la convención congelada del propio oráculo (bytes unidos por `b"\n"`), no una suma de caracteres.