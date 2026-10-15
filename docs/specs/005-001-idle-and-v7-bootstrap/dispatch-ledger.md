# Dispatch ledger — 005-001-idle-and-v7-bootstrap

Versión operativa: v7 `ce09ed0` (activada por el dueño el 2026-10-08; ver
`docs/runtime-adopted-version.md`). Raíz aislada de la adopción:
`<adopted-root>` = `$HOME/.cache/cdad-adopted-ce09ed0`. Los scripts de esa raíz y
los del repo son **byte a byte iguales** (sha256 verificado de
`cdad_packet.py`, `cdad_continuity.py`, `cdad_result.py`, `cdad_guard.py` y
`SKILL.md`): una sola versión del CLI, sin MIX-V6V7.

Gate de tests: focales + módulos tocados por despacho; suite completa al cierre
o si la tarea toca instalador, staging o renderer.

| # | Fecha | Rol | Modelo | Sesión / título | Resultado |
|---|---|---|---|---|---|
| — | 2026-10-08 | orquestador | — | transición del state (commit `c78a0e4`) | Activación de `epic-005-real-operation` (`epic_stage: features-loop`, `epic_features` con las 4 features, `005-001` `in-progress`) y de la feature (`active_feature: 005-001-idle-and-v7-bootstrap`, `current_stage: discovery`); `hitl_delegation` registrada con alcance/vencimiento/fuente de `execution.md`; cita de aprobación del plan en `epic_history`. Se cerró el `active_packet` stale de 003-007 (`scribe-memory-001` → `completed`; su `receive` existe y el Memory Bank está materializado en `docs/activeContext.md`), requisito PD-4. |
| 1 | 2026-10-08 | architect | `mofgw/deepseek-v4.1-flash` (según plan §Operación) | `005-001-idle-and-v7-bootstrap-architect-discovery-001` — **preparado, pendiente de despacho** en una sesión nueva del orquestador (los agentes v7 se cargan al abrirla) | **Primer `prepare` del epic** (`rc=0`), con `CDAD_OPENCODE_AGENTS_DIR="<adopted-root>/.config/opencode/agents"` en la misma invocación: publica los **agentes de proyecto v7**. Verificación (detalle abajo): `source_dir` de la raíz v7 y los 11 derivados coinciden con los hashes del manifiesto. `validate-state` → `VALID`; `validate-request` y `validate-packet` → `rc=0`. La sesión del orquestador termina aquí: el dueño abre una sesión nueva y se retoma con `resume` como primer paso. |
| — | 2026-10-08 | orquestador | — | **Retiro del paquete `005-001-idle-and-v7-bootstrap-architect-discovery-001`** (`contract_sha256` `db04ea70509ae294ba714e5871467503a377d4ec1fa4b17196c599cb536bac86`, `contract_kind` `approved-epic-plan`) | **Retirado sin haberse despachado nunca.** Motivo: el plan del epic se editó después de prepararlo (apartado «Cambios al plan», 2026-10-08), de modo que el contrato cambió y `prepare --resume-packet` devuelve `contract sha256 does not match exact content` (rechazo correcto). No se marcó `completed` ni `failed`; `active_packet` → `null`. El directorio `.cdad/packets/005-001-idle-and-v7-bootstrap-architect-discovery-001/` (REQUEST.json + PACKET.md) se conserva como evidencia. |
| — | 2026-10-08 | orquestador | — | **Rectificación de `stage_history[161]`** (entrada creada para el primer `prepare`) | La entrada pasa de `stage: specification` / `approved_by: Pablo` a `stage: discovery-authorization` / `authorized_by: Pablo`, con `rectified_at: 2026-10-08`; se conserva la nota original. No es una aprobación de spec (la spec no existe todavía). Consecuencia verificada: `validate-state` → `rc=2`, `ERROR: contract approval record missing … (I2)`; es el comportamiento correcto hasta que exista la aprobación real de `spec.md` (paso siguiente). |
| 2 | 2026-10-08 | architect | `mofgw/deepseek-v4.1-flash` (plan §Operación) | `docs/specs/005-001-idle-and-v7-bootstrap/handoff-architect-001.md` — **camino temporal fuera del CLI por I2 circular** | Despacho del discovery + borrador de spec/plan de 005-001 (puntos b–e del plan, prueba decisiva y qué hace una entrada rectificada). Autoridad: plan del epic aprobado + `execution.md`. **No es una aprobación de spec.** Reemplaza al paquete retirado de la fila 1. Resultado: `architect-draft-001.md` (sesión `<ses-62>`); hallazgos verificados por el orquestador (I2 en `_approved_stage_entry` rola-agnóstico; contrato pineado en `validate_request`; bloqueo PD-4; `--resume-packet` con I11). |
| — | 2026-10-08 | orquestador | — | **Materialización y aprobación de spec/plan** (ADR-003 + HITL delegada epic-005) | Materializados `architect-draft-001.md` (verbatim), `spec.md` (PD-1..PD-17, invariantes, criterios) y `plan.md` (T1..T4 + `plan-tasks`). Resueltas D1–D6 en `spec.md` §7 (D1 `epic_history` epic-plan; D2 sin pin del plan, pin de la spec; D3 pin obligatorio + migración; D4 `--replace-packet` sin flags ordinarios; D5 reposo `idle` ⟺ `active_feature` null; D6 aprobación por rol en `prepare`/`validate-request`). Aprobación real registrada en `stage_history` (entrada `specification`, `approved_by`: orquestador OpenCode HITL, `contract_sha256` `a793522a…3125f2`). `validate-state` → `VALID` rc=0; el ciclo sigue por el CLI. |
| 3 | 2026-10-08 | test-writer | `mofgw/glm-5.3-flash` | `...-test-writer-red-001` (sesión `<ses-63>`) | **T1 RED** (`tdd-red-t1`): `tests/test_005_001_t1_role_approval.py` (PD-1..PD-6 + slice PD-12); 5 fallos por AssertionError + PD-5/PD-6 controles verdes; migración D3 (pin) en 9 fixtures; suite 5 failed/601 passed. Commit `e49a1ce`. Recepción `received → completed`. |
| 4 | 2026-10-08 | implementer | `mofgw/deepseek-v4.1-flash` | `...-implementer-green-001` (sesión `<ses-64>`) | **T1 GREEN** (`tdd-green-t1`): `_contract_approval_for` rol-aware en `validate_request`; marcador `approval pending`. Focal 7/7; suite 606 passed; `make validate` 2 F011 preexistentes. Commit `c885f02`. Nota: 1er turno devolvió control sin suite/commit → se continuó la misma sesión. Recepción `received → completed`. |
| 5 | 2026-10-08 | test-writer | `mofgw/glm-5.3-flash` | `...-test-writer-red-002` (sesión `<ses-65>`) | **T2 RED** (`tdd-red-t2`): `tests/test_005_001_t2_replace_packet.py` (PD-7..PD-11, PD-16 + slice PD-12); 8 tests/10 fallos por AssertionError (superficie `--replace-packet` inexistente). Commit `7941007`. Recepción `received → completed`. |
| — | 2026-10-08 | implementer | `mofgw/deepseek-v4.1-flash` | `...-implementer-green-002` (sesión `<ses-66>`) **BLOCKED** | **T2 GREEN bloqueado** (`tdd-green-t2` outcome `blocked`; paquete `failed`): implementación completa en el árbol sin commitear, pero el test RED aprobado tenía un defecto — `state_pre` (l.420) se tomaba ANTES del re-pin legítimo del fixture (l.423), de modo que la aserción INV-2 (l.543) exigía al CLI revertir el re-pin (violando INV-2). Verificado por el orquestador. 7/8 focales; suite 1 failed/613 passed. Deriva al test-writer. |
| 6 | 2026-10-08 | test-writer | `mofgw/glm-5.3-flash` | `...-test-writer-red-003` (sesión `<ses-67>`) | **T2 RED-FIX** (`tdd-red-t2-fix`): `state_pre` movido tras el re-pin del fixture; ninguna aserción cambiada; RED preservado. Focal T2 8/8 (con la implementación en el árbol). Commit `66b880a`. Recepción `received → completed`. |
| 7 | 2026-10-08 | implementer | `mofgw/deepseek-v4.1-flash` | `...-implementer-green-003` (sesión `<ses-66>`, reanudada) | **T2 GREEN cerrado** (`tdd-green-t2` outcome `ok`): implementación del intento bloqueado, sin reescritura. Focal T2 8/8; suite completa **614 passed**; `make validate` 2 F011 preexistentes (independientes del diff). Commit `0e77e49`. Recepción `received → completed`. |
| — | 2026-10-08 | orquestador | — | **Cierre de T1 y T2** | Todos los paquetes con `record-dispatch` (I8) + `receive` (receipt durable) + `validate-receipt` VALID + transición `received → completed` del orquestador. `validate-state` → `VALID`. Próximo: **T3 RED/GREEN** (reposo/idle, PD-13..PD-15), luego **T4** (prueba decisiva PD-17), review (stage 4) y Memory Bank/cierre (stage 5). |

## Verificación de publicación de agentes v7 (criterio 2 del plan)

Manifiesto `.opencode/agents/.cdad-derived.json`:

- `source_dir` = `<adopted-root>/.config/opencode/agents` → **raíz v7** (antes:
  raíz v6 `…/cdad-adopted-abcd4d3/…`).
- `policy_sha256` = `f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711`
  (la política aceptada por la ejecución).
- Los 11 derivados publicados (`cdad-architect{,-odoo}`, `cdad-test-writer{,-odoo}`,
  `cdad-implementer{,-odoo}`, `cdad-reviewer{,-odoo}`, `cdad-scribe{,-odoo}`,
  `cdad-orchestrator`): `sha256(archivo publicado) == agents[].derived_sha256` y
  `sha256(fuente v7) == agents[].source_sha256`. Conjunto publicado exactamente
  igual al del manifiesto. Todo en **true**.

Verificación reproducible (raíz del repo):

```sh
python3 - <<'PY'
import json,hashlib; from pathlib import Path
r=Path("."); m=json.load(open(".opencode/agents/.cdad-derived.json"))
assert m["source_dir"]==str(Path.home()/".cache/cdad-adopted-ce09ed0/.config/opencode/agents")
for n,h in m["agents"].items():
    assert hashlib.sha256((r/".opencode/agents"/n).read_bytes()).hexdigest()==h["derived_sha256"]
    assert hashlib.sha256((Path(m["source_dir"])/n).read_bytes()).hexdigest()==h["source_sha256"]
print("v7 agents OK")
PY
```

## Notas de registro (transparencia)

- **Entrada I2 del primer `prepare`.** El primer `prepare` de una feature exige
  `stage_history` con `{feature, stage: "specification", approved_by}` (I2,
  `cdad_packet.py::_approved_stage_entry`) y **el architect lo necesita ya en
  discovery** (su tipo de contrato es `approved-epic-plan`,
  `cdad_packet.py::_contract_for`). El handoff del epic pide registrar el state
  «con la cita de aprobación del plan» y que ese primer `prepare` publique los
  agentes v7; por eso la transición registra una entrada `specification` para
  `005-001` cuyo `evidence` es el **plan del epic aprobado por el dueño** y cuya
  nota aclara que la spec de la feature aún no existe (la redacta el architect).
  Es la autorización de contrato (I2) de este despacho, no la aprobación de una
  spec inexistente.
- Sin push (regla del epic). Sin `--no-verify`. No se leyó
  `tests/.sensitive-patterns.local`. No se instaló CDAD en HOME.
| 8 | 2026-10-09 | test-writer | `mofgw/glm-5.3-flash` (plan §Operación) | `...-test-writer-red-004` (sesión `<ses-68>`) | **T3 RED** (`tdd-red-t3`): `tests/test_005_001_t3_idle.py` (505 líneas; PD-13/PD-14/PD-15 + slice PD-12). 4 tests / 12 fallas, todas `AssertionError` de comportamiento (0 errores). Verificado por el orquestador. Commit `d7355b7` (solo `tests/`). Recepción: `record-dispatch` (I8) + transición `received→completed`. |
| 9 | 2026-10-09 | implementer | `mofgw/deepseek-v4.1-flash` | `...-implementer-green-004` (sesión `<ses-69>`) | **T3 GREEN** (`tdd-green-t3`): `IDLE_STAGE` + `_validate_idle_coherence` + rama `validate-state`; reposo → `VALID: idle` (rc=0), incoherencia/paquete en vuelo → `state incoherent` (rc=2). Focal 4/4; regresiones 69/69. Desviación declarada: `references/state-detection.md` sin cambios (ya documentaba la invariante). Commit `11e1454` (+45; 0 en `tests/`). |
| — | 2026-10-09 | orquestador | — | **Enmienda del plan del epic** (commit `9c32e5d`) | 005-001 suma las dos correcciones acotadas de T1/T2 instruidas por el dueño (ruta de la aprobación; conservación del reemplazo), como tarea **T-CORR** antes de T4, con gate focales + módulos tocados. |
| 10 | 2026-10-09 | architect | `mofgw/deepseek-v4.1-flash` | `...-architect-draft-001` (sesión `<ses-316>`) | **Enmienda T-CORR de spec/plan** (PD-3/PD-5 ajustadas; PD-18..PD-24 nuevas; INV-7/INV-8; D4 enmendada; D7 nueva; T-CORR en `plan-tasks`). Entregó el TEXTO FINAL completo como archivos de transporte (`/tmp/opencode/arch-005-001-corr-{spec,plan}.md`). Materializado con el flujo: `receive` rc=0 (spec 26741 B sha `86accc0a…`, plan 12339 B sha `c7e5b5b9…`) + `materialize` CAS rc=0 contra el sha previo `a793522a…`; el orquestador aplicó la marca de aprobación (acto de aprobación, no contenido) y re-registró el pin en `stage_history` (commit `d1b36c2`). |
| 11 | 2026-10-09 | test-writer | `mofgw/glm-5.3-flash` | `...-test-writer-red-005` (sesión `<ses-70>`) | **T-CORR RED** (`tdd-red-tcorr`): `tests/test_005_001_tcorr.py` (987 líneas). 10 tests / 13 fallas, todas `AssertionError` (0 errores), con control positivo y el subtest del centinela de lista vacía (D7). Verificado por el orquestador; focales T1/T2/T3 19/19 verdes. Commit `3b5c5ec` (solo `tests/`). |
| 12 | 2026-10-09 | implementer | `mofgw/deepseek-v4.1-flash` | `...-implementer-green-005` (sesión `<ses-71>`) | **T-CORR GREEN** (`tdd-green-tcorr`): C1 el pin de spec autoriza solo si NOMBRA el contrato (`contract_path` + `contract_sha256`); C2 `--replace-packet` conserva campo a campo el encargo anterior, admite las 6 opciones de corrección solo en replace (centinela `-`, pisos obligatorios), mismas validaciones con diagnóstico campo/motivo/opción, argv mezclado rechazado, `.superseded.json` con `conserved_fields`/`changed_fields`. Focal 10/10; regresiones 72/72; suite completa del rol 628 passed. Verificado por el orquestador (focales 29/29 y lectura del arreglo de C1). Commit `bfe8edb` (+180/-20; 0 en `tests/`). |
| 13 | 2026-10-09 | test-writer | `mofgw/glm-5.3-flash` | `...-test-writer-red-006` (sesión `<ses-72>`) | **T4 RED** (`tdd-red-t4`): `tests/test_005_001_t4_decisive.py` (942 líneas), escenario PD-17 **ajustado** (S2: recepción real del paquete del architect antes de preparar al test-writer; S5: reemplazo sobre un paquete todavía `prepared` y no despachado). **Destapó un defecto real**: sin el archivo de la spec y sin aprobación, `prepare` daba el error genérico «cannot read contract» en vez de `approval pending` (PD-3/PD-12/PD-17 paso 2). Commit `bd65cd6` (solo `tests/`). |
| — | 2026-10-09 | implementer | `mofgw/deepseek-v4.1-flash` | `...-implementer-green-006` (sesión `<ses-73>`) **BLOCKED** | **T4 GREEN bloqueado** (`tdd-green-t4` outcome `blocked`; paquete `failed`): aplicó el fix mínimo del producto (SIN commitear) y S3 pasó, pero el escenario murió en S6a: `assert_no_effects` exigía la ausencia ABSOLUTA de `.superseded.json`, en contradicción con S5c3 (que exige el registro legítimo de P1). Verificado por el orquestador por lectura del test: aserciones mutuamente excluyentes. Deriva al test-writer. |
| 14 | 2026-10-09 | test-writer | `mofgw/glm-5.3-flash` | `...-test-writer-red-007` (sesión `<ses-74>`) | **T4 RED-FIX**: `assert_no_effects` acota la comprobación de `.superseded.json` al snapshot `before` (rechaza solo registros NUEVOS); ninguna otra aserción cambia. Verificado por el orquestador: con el fix de producto el focal pasa; con `git stash` del archivo de producto vuelve a fallar en S3 (RED preservado). Focales de la feature 30/30. Commit `ec8bd48` (solo `tests/`). |
| 15 | 2026-10-09 | implementer | `mofgw/deepseek-v4.1-flash` | `...-implementer-green-007` (sesión `<ses-75>`) | **T4 GREEN** (`tdd-green-t4` outcome `ok`): commit del fix del intento bloqueado. Helper `_reject_absent_contract_without_approval` + guard en `prepare`: contrato ausente sin entrada `specification` que lo nombre → `approval pending` con tokens y ruta, sin efectos. **Prueba decisiva PD-17 verde end-to-end**. Focales de la feature 30/30; regresiones 51/51. Commit `70df141` (+42/-1; 0 en `tests/`). |
| — | 2026-10-09 | orquestador | — | **Estado: T1–T4 y T-CORR técnicamente completas** | Próximo: la **única review formal** de la feature (stage 4, cubre también las correcciones), luego stage 5 (suite completa + `make validate` + Memory Bank/cierre). |

## Hallazgo de gate — MIX-V6V7 en los agentes de proyecto (2026-10-09, orquestador)

Al retomar, el manifiesto `.opencode/agents/.cdad-derived.json` tenía
`source_dir = <home>/.config/opencode/agents` (la instalación de HOME, una
versión **distinta** de la v7: sin el bloque `limits-core` y con los modelos
comentados), no la raíz v7 adoptada (`$HOME/.cache/cdad-adopted-ce09ed0`).
Algún `prepare` posterior al primero se ejecutó sin `CDAD_OPENCODE_AGENTS_DIR` y
re-derivó los agentes de proyecto desde esa fuente → **agentes de proyecto de una
versión distinta a la CLI/skills v7**, contra el criterio 2 del epic.

Disposición: **todos los `prepare` de esta sesión** se ejecutaron con
`CDAD_OPENCODE_AGENTS_DIR="$HOME/.cache/cdad-adopted-ce09ed0/.config/opencode/agents"`;
el primer `prepare` de la sesión (T3 RED) re-derivó los 11 agentes desde la raíz
v7 y el manifiesto volvió a declararla. Queda como **observación abierta** para
la review de cierre: el CLI no fuerza la raíz adoptada (registrada en
`.cdad/activation.json`) y un orquestador que omita la variable publica agentes
de otra versión **sin avisar** (defecto de usabilidad/detección, no del flujo de
esta feature).

## Nota de registro — re-entry de los roles de escritura (2026-10-09)

Para los roles de **escritura** (test-writer, implementer) el artefacto es el
**commit** (durable en git) y no hay materialización: el orquestador registra el
despacho (I8 `record-dispatch`) y la transición en `state`, y verifica el commit
(alcance + corrida propia). `receive`/`materialize` se reservan para los
artefactos de los roles de **solo lectura** que sí se materializan (architect →
spec/plan; reviewer → review; scribe → Memory Bank), que es el alcance de la
sección «Orchestrator materialization protocol (read-only roles)» de
`references/re-entry.md`. (T1/T2 de esta feature también habían recibido el
reporte de los roles de escritura; no se repite ese paso por no aportar al
gate y por costo de transcripción, según lo autorizado por el dueño.)
