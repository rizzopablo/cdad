I'll start by loading the domain context and examining the contract and failing tests.
Now let me run the focal test and the related tests to see the current state.
Now let me examine the other reformulated oracles and validation scripts.
Now I have the full picture. Let me make the edits, starting with `SKILL.md` §2.
Now `sources/roles/reviewer.md`:
Now the adapters. OpenCode first:
Now Claude Code adapter:
Now regenerate the agents:
Now let me run the full gate: all 006_002/006_003 tests plus the tests that read the affected surfaces.
All gates green. Committing:
Let me re-verify idempotency on the final committed state:
## Role report — implementer (GREEN) · `006-003` U5' (enmienda A-5)

**Estado: DONE.** Focal y regresión proporcional verdes; commit creado sin `--no-verify`, sin stash, sin push.

---

### 1. Qué cambié (mínimo, A-5)

Retiro del requisito de familia/modelo del reviewer, con reemplazo declarado («el modelo de cada rol es el que configura el runtime; o `delegation.json` en la delegación externa; CDAD no lo elige»).

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/SKILL.md` | §2 «Models.» y «Anti-bias invariants» sin familia; **Role invariants** (§4) sin `reviewer's model family`; fila de anti-patrón «inline vs delegate» (conserva el aislamiento de sesión); se conservan los otros invariantes anti-sesgo |
| `sources/roles/reviewer.md` | Invariantes del rol: read-only + sesión independiente; sin verificación de familia |
| `sources/roles/orchestrator.md` | Anti-bias sin familia; párrafo «Model:» sin celdas por runtime; limitación honesta reescrita (ver §4) |
| `sources/agents/adapters/opencode.md` | Bullet **Family verification (D-3/INV-5)** → **Model provenance (I8)**; sin «no profiles» en frontmatter |
| `sources/agents/adapters/claude-code.md` | Ídem + retiro de la redacción bajo `basic`/«under this profile» (se conserva I8, «does not choose», «environment configuration» y la referencia a `scripts/validate-subagents.sh`/`ADR-007`) |
| `scripts/cdad-generate.py` | `model_note()` sin el requisito de familia («configuration verification» / «invariant not guaranteed») |
| `agents/**` (6) | Regenerados con `make agents` (idempotente) |

Conservados: observación **I8** (`model_configured`/`model_reported`) y `references/verdict-tuple.md`. No toqué `stage-4-review.md` («A failure family is fixed as a family»), ni `tests/`, ni `install.sh`, ni los scripts de delegación.

### 2. Commands + output

```
$ make agents            # (x3, idempotente)
cdad-generate: 12 files -> build/staging/agents/opencode (+ manifest.json)
cdad-generate: 12 files -> build/staging/agents/claude-code (+ manifest.json)
$ git status --short -- agents/        # tras dos make agents
(vacío = sin diff: idempotente)
```

### 3. Tabla test → resultado

| Test | Resultado |
|---|---|
| `test_006_003_u5p_no_family_requirement.py` (focal, 7) | ✅ |
| `test_006_003_u3_texts_without_profiles.py` (10) | ✅ |
| `test_006_002_u1_delegation_section.py` / `_u2_` / `_u4_` | ✅ |
| `test_005_004_t2_installer_claims.py` (8, incl. `test_pd5_adapter_does_not_declare_the_retired_reviewer_family_invariant` y `..._references_the_exemption_source...`) | ✅ |
| `tests/test_006_002_*.py` + `tests/test_006_003_*.py` (conjunto del gate) | ✅ **80 passed** |
| Tests que leen SKILL.md / `sources/` / orquestadores (`grep -l … tests/*.py`, 54 archivos) | ✅ **382 passed, 2 skipped** |
| `bash tests/validate-consistency.sh` — F001 (A-5/PD-7b) | ✅ PASS (168 asserts) |
| `bash tests/validate-consistency.sh` — F011 | ❌ **declarada** (drift de HOME: `~/.claude`, `~/.config/opencode`, `~/.agents` con instalación previa — preexistente, no causada por el diff) |
| `bash tests/validate-odoo-specialization.sh` | ✅ PASS (68 asserts, P1 rev retiro de familia) |

```
$ python3 -m pytest tests/test_006_003_u5p_no_family_requirement.py \
    tests/test_006_003_u3_texts_without_profiles.py tests/test_006_002_u1_delegation_section.py \
    tests/test_006_002_u2_neutral_skill.py tests/test_006_002_u4_skill_without_models.py \
    tests/test_005_004_t2_installer_claims.py -q
45 passed in 10.15s
```

### 4. Desviación declarada (sin conflicto de oráculos)

`tests/validate-consistency.sh` F001 greps el **archivo completo** del orquestador por `model famil`. La limitación honesta heredada (`sources/roles/orchestrator.md:102`, compuesta al agente) decía «does not guarantee isolation nor another model family» y disparaba ese patrón. La reescribí a «**nor any particular model**» (mismo sentido, alineado con A-5: el modelo es el que configura el runtime). El oráculo `u5p` declara esa línea como **no-ofensiva** (no exige conservarla), así que no hay oposición entre oráculos: F001 queda satisfacible sin tocar texto que `u5p` exija.

### 5. Residual fuera de alcance declarado (para el orquestador, no lo toqué)

Siguen conteniendo la formulación retirada, por estar fuera del alcance del packet (`scripts` de delegación / limitaciones honestas no barridas por los focales):
- `scripts/validate-subagents.sh:25,181-183,199` («reviewer!=implementer family invariant … configuration verification») — packet: **NO TOCAR scripts de delegación**.
- `skills/cdad-cycle/references/cli-delegation.md:334-335` y `SKILL.md:146` («does not attest isolation nor another model family») — declaradas limitaciones honestas **no-ofensoras** por `test_006_003_u5p_*` y fuera de las secciones que el packet manda retirar.

### 6. Commit

```
0230156 feat: 006-003 U5' GREEN — retiro del requisito de familia/modelo del reviewer
 12 files changed, 107 insertions(+), 141 deletions(-)
```

Solo archivos dentro del `write_scope` (`agents/`, `scripts/`, `skills/`, `sources/`); `docs/planning/` y `findings/…` (sin trackear, ajenos) quedaron intactos.
