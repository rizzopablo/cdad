# Cierre del gate GREEN T4 — 010-004

**Fecha:** 2026-10-30
**Autor:** orquestador CDAD (mandato HITL vigente: `docs/epics/epic-010-documentary-specialization/execution.md`; `owner-mandate-hitl-2026-10-30.md`)
**Contrato:** `spec.md` SHA-256 `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`
**Plan:** `plan.md` v2 SHA-256 `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685`

## 1. Entrega registrada

| Dato | Valor |
|---|---|
| Paquete | `010-004-packet-dispatch-ergonomics-implementer-green-007` |
| Intento de continuidad | 27 (`begin` seq 54, `d74e2b87…`; cierre `checkpoint` seq 55, `58b96ba1…`) |
| Sesión nativa | `<session>` (`cdad-implementer`, opencode-go/deepseek-v4.1-flash) |
| FINAL TEXT | `.cdad/inbox/010-004-implementer-green-007-attempt27-role-report.md`, 7290 bytes, sha256 `e3eb10ef7ceab36bbb28f88a382f0aac63918fc3a56ba9dcd182e5e953b6ccd5` |
| Recibo durable | `.cdad/runtime/results/exec-010-004-packet-dispatch-ergonomics-001/010-004-packet-dispatch-ergonomics-implementer-green-007/receipt.json`, sha256 `bc43797741a87fdc295261c3ca2badb30fcd5158b5a6a941c6a8cdb65eae878c`, `semantic_status: pending` |
| Materialización | `docs/specs/010-004-packet-dispatch-ergonomics/green-t4.md`, byte-idéntico al FINAL TEXT (`e3eb10ef…`) |
| Commit de la entrega | `8958c366e701f784df84b3c68317c04d63c33d94` — `feat(010-004): GREEN T4 - despacho por ruta C en las cuatro superficies y derivados regenerados` |

## 2. Verificación propia del orquestador

### 2.1 Ámbito del commit

`git show --name-status` de `8958c366` devuelve exactamente 6 rutas, todas dentro del write scope del paquete (`sources`, `skills/cdad-cycle/references`, `agents`, `build/staging`):

| Archivo | +/− |
|---|---|
| `sources/roles/orchestrator.md` | 12 / 0 |
| `sources/agents/adapters/opencode.md` | 11 / 0 |
| `sources/agents/adapters/claude-code.md` | 11 / 0 |
| `skills/cdad-cycle/references/handoff-prompts.md` | 21 / 13 |
| `agents/cdad-orchestrator.md` (derivado) | 23 / 0 |
| `agents/claude-code/cdad-orchestrator.md` (derivado) | 23 / 0 |

`git diff --stat 8958c366~1 8958c366 -- tests docs scripts install.sh skills/cdad-cycle/scripts skills/cdad-cycle/SKILL.md` → vacío. Los derivados de `build/staging` son gitignored; su prueba es el hash agregado de §2.3.

### 2.2 Pruebas

```
python3 -m pytest tests/test_010_004_t4_red.py -q                      → 2 passed in 0.44s, rc=0
python3 -m pytest tests/test_cdad_generate.py tests/test_005_006_t6_owner_reviewfix.py -q
                                                                       → 15 passed in 2.73s, rc=0
```

### 2.3 Determinismo de la regeneración

`make staging` y `make agents` ejecutados dos veces consecutivas por el orquestador; hash agregado de `build/staging` (`find … | sort | xargs sha256sum | sha256sum`):

- antes: `c394a0c7d9584c4202c99c2a7147be13297549a8f17ad1102b5e8655ee7d3d7f`
- corrida 1: `c394a0c7d9584c4202c99c2a7147be13297549a8f17ad1102b5e8655ee7d3d7f`
- corrida 2: `c394a0c7d9584c4202c99c2a7147be13297549a8f17ad1102b5e8655ee7d3d7f`

`git status --porcelain -- build/staging agents` → vacío (staging es gitignored: el hash agregado es la prueba real). `make staging` y `make agents` rc=0 en ambas corridas.

### 2.4 Gate transversal: suite completa

Evidencia conservada en `.cdad/evidence/t4-full-suite/`:

| Intento | Comando | Resultado |
|---|---|---|
| `attempt-20261030T233338118253Z-1859495-e7d718fd` | `python3 scripts/cdad-suite.py close --all --evidence-root .cdad/evidence/t4-full-suite` | **1864 passed, 5 skipped**, `rc: 0` (`attempt.json`), `canary_delta_lines: 0` |
| `attempt-20261030T223309058329Z-1195400-a2422c4e` (conservado) | idem | `1 failed, 1863 passed, 5 skipped`, `rc: 1` |

**Episodio registrado honestamente (no se borra):** la primera corrida falló por redacción propia del rol implementer — su texto usaba `cdad_packet.py render --route C` sin el marcador `<skill-dir>` que exige el oráculo `tests/test_005_006_t6_owner_reviewfix.py:157` (HALLAZGO A2). El rol corrigió la redacción en la misma sesión, regeneró y re-corrió; el intento fallido queda en el directorio de evidencia y no se eliminó. La corrida de cierre es la posterior a la corrección.

Matiz de auditoría: ambos `attempt.json` registran `commit: 0d015234…` y `dirty: 7` porque la suite corrió sobre el árbol de trabajo (6 archivos modificados + el untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md`) antes de crear el commit `8958c366`; el árbol medido es el que produjo ese commit.

### 2.5 `make validate`

```
Assert PASS: 182
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile)
make: *** [Makefile:22: validate] Error 1     rc=2
```

F011 es **preexistente y ambiental**: `validate-subagents.sh` → `install.sh --check` compara el repo contra la instalación global (`~/.config/opencode`, `~/.agents`, `~/.claude`), que está desactualizada. El drift incluye archivos que este cambio no tocó (`skills/cdad-cycle/packets/substages/test-writer-post-audit.md`). Verificado por el orquestador en un worktree temporal sobre `0d015234` (commit base) con `make staging` generado: **el mismo F011 falla igual** (`Check: FAIL`, skills globales divergentes). No se actualizó ni debilitó la instalación global; todas las demás aserciones repo-internas pasan.

### 2.6 Pins

| Pin | Valor actual | Estado |
|---|---|---|
| `docs/specs/010-004-packet-dispatch-ergonomics/spec.md` | `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64` | intacto (declarado en `REQUEST.json`) |
| `docs/specs/010-004-packet-dispatch-ergonomics/plan.md` (v2) | `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685` | intacto |
| `docs/epics/epic-010-documentary-specialization/plan.md` | `b9375189b674dce8197f1cd69e79f5eba2934a92688d612607361db2edd5c698` | intacto |
| `docs/cdad-policy.json` | `f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711` | intacto |

`reconcile` reporta las cinco referencias de clase `contract` como `unchanged`.

## 3. Postcondiciones declaradas green en este gate

La alineación se verificó por lectura del texto vigente (no se reescribió prosa que ya cumplía). El reviewer independiente de T6 conserva la revisión semántica (designada por `decision-t4-mechanical-guard.md` §7 y `spec.md:466`); este gate no la sustituye.

| PC | Evidencia (archivo:línea resumen) |
|---|---|
| **PC-03** (`spec.md:402`) | `sources/roles/orchestrator.md:63-73` (bloque de despacho: `render --route C` sobre el request publicado, stdout solo, nunca recompuesto/retranscrito/con cuerpo, A+C rechazado aun coincidente, inline divergente no rescatado, rechazo reportado); `sources/agents/adapters/opencode.md:79-88`; `sources/agents/adapters/claude-code.md:93-102`; `skills/cdad-cycle/references/handoff-prompts.md:17-27`; guarda mecánica verde `tests/test_010_004_t4_red.py` (2 passed) |
| **PC-07b** (`spec.md:414`) | `skills/cdad-cycle/references/handoff-prompts.md:34-39` (v1 histórico, no entrada universal, nunca adoptado, bootstrap v2 en `project-execution.md` §3); `project-execution.md:110-119` (`--new-execution`, v1 nunca adoptado, diagnóstico que no reescribe); `project-execution.md:122-127` (`--resume-packet` replay byte-idéntico, condiciones v2); `sources/roles/orchestrator.md:103-108` (salida bloqueada: causa, quién decide/dónde volver, sin fabricar autoridad ni cambiar versión); `sources/roles/orchestrator.md:30` (diagnóstico: nada se prepara ni despacha) |
| **PC-08b** (`spec.md:420`) | `sources/roles/architect.md:19-30` (intake compartido: comparación desde el marcador **hasta el fin del paquete recibido** contra el render canónico completo, no solo la cabecera; toda diferencia —objetivo, línea de instrucción, contrato, scope o evidencia bajo cabecera intacta— bloquea y se reporta); `:48-55` (metadatos canónicos/cierre); derivados 10/10 por árbol en `agents/`, `agents/claude-code/`, `build/staging/agents/{opencode,claude-code}` con el literal de intake |
| **PC-10** (`spec.md:426`) | `skills/cdad-cycle/references/re-entry.md:24-54` (estados de llegada; staging es transporte, no autoridad; recibo mecánico que nunca aprueba, `semantic_status` siempre `pending`); `re-entry.md:121-128` (`rc=0`, `termination=completed` y `delivery=received` no son aprobación); `sources/roles/orchestrator.md:52-60` (el `delivery` del sobre —no `rc` ni `termination`— decide la ruta; el recibo es durable y se valida); `skills/cdad-cycle/references/cli-delegation.md:252,405-407` (stdin byte-idéntico; una corrida exitosa es observación empírica, no prueba) |
| **PC-11** (`spec.md:428`) | `re-entry.md:57` (reconciliar antes de repetir; no repetir un efecto ya aplicado); `re-entry.md:159` (no repetir la suite tres veces cuando el árbol/policy/entorno es equivalente); `re-entry.md:169-175` (reintento solo con hipótesis/información nueva; repetición idéntica → revisión de estrategia); `handoff-prompts.md:25-27` (un inline divergente no se rescata cambiando a C; el rechazo se reporta); `sources/roles/orchestrator.md:158` (no auto-reparación: re-despachar nombrando el defecto) |
| **PC-12** (`spec.md:432`) | Las cuatro superficies de despacho y ambos adaptadores concuerdan con §4.6 (commit `8958c366`, §2.1); derivados regenerados solo por `make staging`/`make agents` con determinismo medido (§2.3); 4/4 `cdad-orchestrator.md` nombran `--route C` (2 ocurrencias cada uno: bloque del rol + bloque del adaptador); 10/10 agentes de rol por árbol conservan la declaración de intake. **El recorrido del consumidor instalado aislado (preparar v2 → emitir C → resolver/validar contexto) es la verificación de T5 y no se acredita aquí** |

### 3.1 Corrección posterior — revisión T6 (2026-10-30)

La revisión independiente de Stage 4 (`review.md`, recibo `3c9a73d7…`) comprobó que **cuatro filas de la tabla anterior no quedaron acreditadas por las líneas que citan**. El texto original se conserva como registro histórico; esta corrección lo fecha y lo corrige:

| Fila | Estado real | Motivo |
|---|---|---|
| **PC-03** | **No acreditada en el intake** (B1) | La fila cita solo la capa de despacho (orquestador, adaptadores, handoff) y una guarda de token. El bloque `intake-core` de `sources/roles/architect.md:15-57` —superficie que `spec.md:402` incluye— no contiene el rechazo de mezcla A+C ni la exigencia de contexto v2 para C: el único «A+C» de `sources/roles/` vive en `orchestrator.md:70`, y los agentes derivados de rol no lo tienen. |
| **PC-07b** | **Contradicha por la conducta medida** (B2) | Con un paquete v1 activo en `prepared`, `prepare` remite a `prepare --new-execution` y `--new-execution` responde «complete or fail it before preparing a new packet (PD-4)»: el resultado observable no es el único que `spec.md:205,222,352` exigen, y ofrece la instrucción prohibida. Además `project-execution.md:122-127` no enuncia las «condiciones v2» que la fila le atribuye. |
| **PC-10** | **No acreditada por las líneas citadas** (B3) | `skills/cdad-cycle/references/cli-delegation.md:405-407` trata de la contención de locks del store (una corrida concurrente exitosa es observación, no prueba) y `re-entry.md:24-54,121-128` de que el recibo no aprueba (INV-09). Ninguna de esas líneas distingue integridad publicada, observabilidad de entrega y fidelidad del resultado, ni dice que archivo, stdin, literal reconstruido o recibo no prueban el prompt recibido. |
| **PC-11** | **No acreditada por las líneas citadas** (B3) | `re-entry.md:159` es la regla de equivalencia de una corrida registrada (no repetir la suite tres veces), no la conservación de I-4 e I-5: no dice que la falta de observabilidad por sí sola no obliga a repetir, ni regula el rescate de un inline alterado mediante C. |

Límite del propio gate: la guarda mecánica `tests/test_010_004_t4_red.py` comprueba **un token** (`--route C`) y su supervivencia en derivados. Verifica que el camino esté nombrado, **no** que la instrucción se obedezca ni que la semántica de la promesa se cumpla (`spec.md:466`); por eso estas cuatro filas podían estar en verde sin estarlo. La corrección de B1–B4 se sigue en `review.md` y en `closure-conditions.md`.

## 4. Límites declarados

- **Las guardas documentales no acreditan obediencia.** Verifican tokens estables y su presencia en las superficies y derivados; la semántica de la instrucción queda bajo la revisión independiente (R3, `closure-conditions.md:§3`).
- El recibo mantiene `semantic_status: pending`: recibir y materializar no aprueban nada; el gate lo decide el orquestador bajo el mandato HITL y la revisión independiente queda para T6.
- No se instaló nada globalmente, no se tocó `~/.config/opencode`, `~/.agents` ni `~/.claude`, y no hubo push.
- F011 se declara como drift ambiental preexistente; no se corrige debilitando la aserción ni actualizando la instalación global.
