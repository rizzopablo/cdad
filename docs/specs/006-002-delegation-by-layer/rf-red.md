I have the contract, the review finding B-1, and the existing U2/U4 oracles. I'll create the focal review-fix RED that extends the PD-1/INV-2 oracle for the class B-1 identified (bare runtime model aliases + concrete deployment gateway), reusing U2's single-definition surface helpers.
RED confirmed: 5 content offenders — all four bare aliases plus the gateway, all at `sub-agent-strategies.md:51` — and zero false positives elsewhere in the installable tree. Now capturing the evidence explicitly.
RED completo. Reporte:

## Cambios
- **Nuevo:** `tests/test_006_002_reviewfix.py` (focal review-fix B-1, 239 líneas, commit `5c85d68`).
- **Sin tocar:** `skills/`, `sources/`, `scripts/`, `agents/`, `docs/` (diff vacío). No edité `tests/test_006_002_u2_neutral_skill.py` — el objetivo permitía focal nuevo, y así U2/U4 conservan su superficie y el oráculo extendido queda aislado y auditable. Los untracked `docs/planning/` y `findings/…` no son míos (quedan sin trackear).

## Mapa test → postcondición
| Test | Postcondición | Esperado hoy |
|---|---|---|
| `TestB1OracleSelfCheck::test_b1_oracle_flags_bare_alias_in_model_context` | PD-1/INV-2 (B-1) — guarda del oráculo | PASA |
| `TestB1OracleSelfCheck::test_b1_oracle_ignores_alias_outside_model_context` | PD-1/INV-2 (B-1) — anti-falso-positivo | PASA |
| `TestB1OracleSelfCheck::test_b1_oracle_flags_deployment_gateway_token` | PD-1/INV-2 (B-1) — guarda del oráculo | PASA |
| `TestPd1Inv2B1NoRuntimeModelDetail::test_pd1_inv2_no_bare_runtime_model_alias_or_concrete_gateway_in_installable_skill_text` | PD-1/INV-2 (B-1) — ausencia en `skills/**` | **FALLA (AssertionError)** |

Diseño: reusa la superficie y el oráculo base de U2 (`scanned_documents`, `model_offences`, `TOOL_FORM_EXCLUSIONS` — una sola definición, sin copiar patrones) y **extiende** con: (a) alias de runtime `haiku|sonnet|opus|fable` **solo si la misma línea tiene contexto de modelo/delegación** (`model:`, «modelo», delegat*, sub-agent*) — cubre la frontera exacta de PD-1 «a concrete model in a delegation context» y evita la acepción «magnum opus»; (b) gateway de despliegue `mofgw`. `context-meter.md` sigue excluido (INV-8).

## Comandos y salida
1. `python3 -m pytest -q tests/test_006_002_reviewfix.py tests/test_006_002_u2_neutral_skill.py tests/test_006_002_u4_skill_without_models.py`
   → `1 failed, 12 passed`. La falla es **AssertionError de contenido** (no ImportError/SyntaxError), con los 5 ofensores:
   ```
   sub-agent-strategies.md — alias … 'haiku' (línea 51)
   sub-agent-strategies.md — alias … 'sonnet' (línea 51)
   sub-agent-strategies.md — alias … 'opus' (línea 51)
   sub-agent-strategies.md — alias … 'fable' (línea 51)
   sub-agent-strategies.md — gateway de despliegue concreto: 'mofgw' (línea 51)
   ```
   **0 falsos positivos** en el resto del árbol instalable.
2. `python3 -m pytest -q tests/test_006_002_u2_neutral_skill.py tests/test_006_002_u4_skill_without_models.py` → **9 passed** (U2 y U4 verdes con el oráculo sin perturbar).
3. `python3 -m pytest tests/test_006_002_reviewfix.py -v` → los 3 self-checks `PASSED`; el de ausencia `FAILED` (único rojo).
4. `ruff check tests/test_006_002_reviewfix.py` → `All checks passed!`
5. Condición de cierre de B-1: `grep -RniE '\bhaiku\b|\bsonnet\b|\bopus\b|\bfable\b|mofgw' skills/` → 1 sola línea (`sub-agent-strategies.md:51`), coherente con el review.

## Commit
`5c85d68` — `test: 006-002 review-fix RED B-1 alias de modelo de runtime y gateway de despliegue en texto instalable`; `git diff --cached --name-only` = `tests/test_006_002_reviewfix.py` (1 file, +239). Sin `--no-verify`, sin `git stash`, sin push.

## Notas honestas
- Leí solo el contrato (`docs/specs/006-002-delegation-by-layer/spec.md` y `review.md`) y `tests/**`; no abrí `skills/**` a mano. La línea ofensora llega desde la cita del review B-1 y la confirma la salida del oráculo en runtime.
- El oráculo se acota a contexto de modelo por línea; si un alias apareciera en prosa legítima sin marcador de modelo, no es ofensor (el contrato pide exactamente esa frontera). El self-check (2) fija ese comportamiento para que no se degrade a un grep ingenuo.
