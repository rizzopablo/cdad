## Role report — implementer · GREEN (enmienda 001 de 006-002)

**Packet:** `006-002-delegation-by-layer-implementer-green-008` · `exec-006-002-delegation-by-layer-001`
**Contract:** `docs/specs/006-002-delegation-by-layer/spec.md` (sha256 `c4fc5584…`) — «Enmienda 001 — regla 4 de contexto» (spec.md:227‑231), PD‑6(4)/INV‑4.
**RED reformulado:** `tests/test_006_002_u6_context_discipline.py` (commit `b9d9455`) — **no fue tocado**.

### 1. Cambios (4 archivos, todos dentro del write scope)

| Archivo | Cambio |
|---|---|
| `sources/roles/orchestrator.md:108` | Regla 4 reescrita de «**Never `/tmp` as channel or workspace**» (prohibición absoluta) a **una sola línea relativizada**: `/tmp` admitido para borradores efímeros de un mismo proceso; lo durable/evidencia/lo que lee otro proceso o rol → rutas estables del workspace (`.cdad/inbox` para el recibo, workspace declarado para el resto) porque `/tmp` se limpia y no deja evidencia |
| `skills/cdad-cycle/SKILL.md:174` | El puntero «Context discipline» repetía «never `/tmp` as channel or workspace»; ahora enuncia la regla relativizada. `orientation.md` **no** contiene ninguna mención de `/tmp` (verificado: `grep -n tmp skills/cdad-cycle/references/orientation.md` → vacío), no se tocó |
| `agents/cdad-orchestrator.md:102` y `agents/claude-code/cdad-orchestrator.md:107` | Regenerados con `make agents` (salidas declaradas; nunca a mano) |

```
$ git show --stat --format="%H %s" HEAD
4c068ea3aa29da3fdb336b46bfc74a6ddbad2b67 feat: 006-002 enmienda 001 GREEN — regla 4 de contexto relativizada (/tmp)
 agents/cdad-orchestrator.md             | 2 +-
 agents/claude-code/cdad-orchestrator.md | 2 +-
 skills/cdad-cycle/SKILL.md              | 2 +-
 sources/roles/orchestrator.md           | 2 +-
 4 files changed, 4 insertions(+), 4 deletions(-)
```

`tests/**` no aparece en el diff (invariante «Do not edit tests» respetada). `install.sh`, `cdad-models.sh`, el adaptador y ADR‑007 intactos. `docs/planning/` y `findings/…` siguen **sin trackear** (no son míos): `git status --short` solo los lista como `??`.

### 2. Tabla test → resultado

| Test / módulo | Resultado |
|---|---|
| `tests/test_006_002_u6_context_discipline.py` (focal, 7 tests) | **7 passed** |
| `test_006_002_u1..u6` (módulos acoplados de la feature) | **38 passed** |
| 33 módulos que leen orquestadores / `SKILL.md` / `orientation.md` (`test_005_009_t3_spawn_reconciliation.py`, `test_005_004_*`, `test_cdad_generate.py`, `test_package_prepare`, `test_role_packet_*`, `test_install_review5_regressions.py`, `test_opencode_read_map_and_steps.py`, …) | **272 passed, 2 skipped** |
| `make agents` (idempotencia) | **OK** (2ª corrida: `sha256sum -c` sin cambios) |
| `make validate` | **161 Assert PASS / 1 Assert FAIL** = `F011` (DT‑8) |

### 3. Comandos y salidas

```text
$ python3 -m pytest tests/test_006_002_u6_context_discipline.py -q
.......                                                                  [100%]
7 passed in 1.49s

$ python3 -m pytest tests/test_006_002_u1..u6 -q          # 6 módulos
......................................                    [100%]
38 passed in 4.86s

$ python3 -m pytest <33 módulos que leen orquestadores/SKILL.md/orientation.md> -q
272 passed, 2 skipped in 216.03s (0:03:36)

$ sha256sum agents/cdad-orchestrator.md agents/claude-code/cdad-orchestrator.md \
    build/staging/agents/opencode/cdad-orchestrator.md build/staging/agents/claude-code/cdad-orchestrator.md > before.txt
$ make agents >/dev/null && sha256sum -c before.txt
agents/cdad-orchestrator.md: OK
agents/claude-code/cdad-orchestrator.md: OK
build/staging/agents/opencode/cdad-orchestrator.md: OK
build/staging/agents/claude-code/cdad-orchestrator.md: OK
IDEMPOTENT: OK

$ make validate
Assert PASS: 161
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
PASS: F011 (B8): validate-subagents.sh no longer requires impl.diff to still apply against the tree
PASS: F011 (B8): validate-subagents.sh still verifies impl.diff's format
PASS: F011: tests/validate-odoo-specialization.sh → PASS (zero regression over cdad-003/004)
```

**F011 = DT‑8 (preexistente, ajeno a este diff) — probado, no supuesto.** El fallo es drift de las **copias instaladas en HOME** (`install.sh --check`). Extraje el árbol HEAD *sin* mi cambio y falla idéntico:

```text
$ rm -rf /tmp/opencode/cdad-head && mkdir -p /tmp/opencode/cdad-head
$ git archive HEAD | tar -x -C /tmp/opencode/cdad-head && cd /tmp/opencode/cdad-head
$ bash scripts/validate-subagents.sh | tail -3
[models] basic profile: no fixed models — agents inherit the runtime's model; …
== RESULT: FAIL (see the ❌ messages above) ==
```

El drift alcanza archivos que no toqué (p. ej. `~/.config/opencode/agents/cdad-architect.md` difiere solo por `model: …`), confirmando que F011 no es causado por U‑enmienda‑001.

### 4. Crítica constructiva

- **Gates formales verde.** Oráculos de conceptos co‑ubicados (unidad/ventana) satisfechos por la fuente y por ambos orquestadores generados; el oráculo de ausencia relativizado recorre `skills/**` + `agents/**` sin offenders.
- **Pendiente revisado y reportado sin tocar** (no lo exige ningún test): `skills/cdad-cycle/references/handoff-prompts.md:628` — `Run logs named under ~/tmp/ (never /tmp/) so the evidence is referenceable.` Usa `/tmp` como lugar de un artefacto (log de corrida) y conserva un «never /tmp» absoluto local. El oráculo de ausencia de U6 lo **salta** porque su bloque contiene «Never» (línea 623‑624 `Never re-run without a change`), y `grep -rn "/tmp" tests/` confirma que ningún test lo exige. Si el dueño quiere consistencia plena con la enmienda, es una línea a reformular en otra unidad (no la cambio: «si no lo exige, reportalo sin cambiarlo»).
- **`orientation.md` sin menciones de `/tmp`** → no requería cambios; sigue siendo el dueño de «vista primero» citado, sin duplicación introducida por mí.
- **`make agents` con `PROFILE=optimus`** regenera `build/staging` (ignorado por git); el fixture de los tests usa su propia copia con `PROFILE=basic`, por lo que el perfil no afecta las aserciones (regla de contexto independiente de perfil).

### 5. Evidencia del commit

- **Commit:** `4c068ea3aa29da3fdb336b46bfc74a6ddbad2b67` — `feat: 006-002 enmienda 001 GREEN — regla 4 de contexto relativizada (/tmp)`
- Sin `--no-verify`, sin `git stash`, **sin push**. Solo los 4 archivos del scope entraron al commit.

**Límite honesto (PD‑6):** el test prueba que la regla *existe y está relativizada*, no que se *obedezca*; la única evidencia de comportamiento es el transcript de la corrida de aceptación (U8) y es una muestra. La redacción fina la verifica el review de stage 4.
