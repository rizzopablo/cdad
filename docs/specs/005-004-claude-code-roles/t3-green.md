# GREEN report — 005-004-claude-code-roles, T3 (pata Claude Code del chequeo de versión)

**Rol:** implementer · **Subetapa:** implementer-green · **Feature:** 005-004-claude-code-roles (epic-005-real-operation) · **Task:** T3
**Paquete:** `.cdad/packets/005-004-claude-code-roles-implementer-green-003/PACKET.md`
**Contrato:** `docs/specs/005-004-claude-code-roles/spec.md` (sha256 79d57e0a…) — PD-3 (a)-(d), AC-3, INV-3/INV-4/INV-7.
**Commit:** `b05c5c1114cf0590305bd368a51509cab71c4ec9` (`feat: pata Claude Code aditiva en cdad-version-check.py (005-004 PD-3/AC-3)`)

## 1. Cambio (mínimo, aditivo y declarado)

### `skills/cdad-cycle/scripts/cdad-version-check.py`
- `:15-22` (docstring): declara la pata **Claude Code** (aditiva) y su participación condicionada.
- `:66-71` (constantes): `CLAUDE_AGENTS_SUBDIR = (".claude", "agents")` y `ACTIVATION_REGISTRY_REL = Path(".cdad") / "activation.json"`.
- `:124-147` (nuevo `_claude_code_installation_root`): resuelve la raíz de instalación detrás de los agentes CC — desde el registro de activación (`<project-root>/.cdad/activation.json` → `adopted_root`, cuando esa raíz declara `.claude/agents`) y, si no, desde el directorio global de agentes CC del runtime (`<home>/.claude/agents` → `<home>`). Detectable ⇔ el directorio de agentes CC existe; sin él retorna `None`. Nunca asciende cruzando una frontera de instalación (F2) y no lee el manifiesto derivado de OpenCode.
- `:150-157` (nuevo `_claude_code_version`): lee el marcador en la raíz de instalación y, si falta, la copia junto a los agentes (patrón del propio archivo).
- `:192-194` (`main`): computa `cc_root`/`cc_version` (antes de imprimir).
- `:207-215` (`main`): imprime la línea declarada de la pata (`claude-code: <versión>` o `claude-code: (no version.txt found)` o `claude-code: (not detected: no Claude Code agents installation)`).
- `:222-233` (`main`): participación en el veredicto — con instalación CC detectable y marca presente, la versión entra en la comparación (`COHERENT`/`DRIFT`); con instalación CC detectable y marca faltante → `UNKNOWN` con causa; sin instalación CC detectable → **los cuatro veredictos y su `rc` no cambian**.

### `skills/cdad-cycle/references/project-start.md`
- `:213-221` (§10): actualiza la referencia **por referencia** (fuente única): nombra la pata CC, delega sus reglas y su formato al contrato 005-004 (PD-3), sin duplicar la regla ni el formato de salida y sin introducir una segunda forma de comando.

No se tocó `tests/` (verificado: `git diff --name-only -- tests/` vacío). No se tocaron las patas existentes (project/agents/CLI).

## 2. Tabla test → resultado

| Test del focal `tests/test_005_004_t3_version_check_cc.py` | Contrato | Resultado |
|---|---|---|
| `test_pd3_cc_leg_reports_version_when_coherent` | PD-3(a)(i)/AC-3 | PASS |
| `test_pd3_cc_leg_participates_in_verdict_drift` | PD-3(a)(c)/AC-3/INV-7 | PASS |
| `test_pd3_no_cc_installation_declares_absence_and_keeps_verdict` | PD-3(b)/INV-4(2) | PASS |
| `test_pd3_missing_cc_marker_is_unknown_with_cause_not_borrowed` | PD-3(d)/INV-3/INV-7 | PASS |
| `test_pd3_existing_verdicts_unchanged_without_cc[drift-DRIFT-1]` | PD-3(b)/INV-4(4) | PASS |
| `test_pd3_existing_verdicts_unchanged_without_cc[unknown-UNKNOWN-3]` | PD-3(b)/INV-4(4) | PASS |
| `test_pd3_existing_verdicts_unchanged_without_cc[no-project-agents-NO-PROJECT-AGENTS-4]` | PD-3(b)/INV-4(4) | PASS |
| `test_pd3_checkout_without_marker_stays_unknown_f2` | PD-3(c)/INV-4(F2) | PASS |

Focal: **8/8 GREEN** (era 8 RED por aserción).

## 3. Comandos exactos y salida

### CMD1 — focal (RED → GREEN)
```
$ python3 -m pytest tests/test_005_004_t3_version_check_cc.py -q
........                                                                 [100%]
8 passed in 1.01s
```

### CMD2 — focal + regresiones declaradas por el paquete
```
$ python3 -m pytest tests/test_005_004_t3_version_check_cc.py tests/test_005_006_t6_owner_reviewfix.py tests/test_005_003_t2_examples_execute.py -q
.......................                                                  [100%]
23 passed in 2.92s
```

### CMD3 — lint del archivo (ruff, presente en el entorno; no hay objetivo lint declarado en el Makefile)
```
$ ruff check skills/cdad-cycle/scripts/cdad-version-check.py
All checks passed!
```

### CMD4 — regresión proporcional de los consumidores de `project-start.md` (el cambio sale del focal: toca una referencia compartida)
```
$ python3 -m pytest tests/test_005_006_t1_start_procedure.py tests/test_005_006_t2_intake.py \
    tests/test_005_006_t3_epic_features.py tests/test_005_006_t4_readme.py \
    tests/test_005_006_t5_acceptance.py tests/test_005_003_t1_compact_view.py \
    tests/test_005_007_t3_open_unit.py -q
................................................                         [100%]
48 passed in 13.54s
```

### CMD5 — verificación manual de la ruta del registro de activación (evidencia fuera del focal congelado)
Fixture `/tmp/opencode/ccprobe`: proyecto con `.cdad/activation.json` (`adopted_root` = raíz adoptada CC con `.claude/agents` y `version.txt` = `d4d4d4d4`), lado OpenCode coherente en `a1a1a1a1`, HOME sin instalación CC global.
```
$ HOME=<fixture-home> python3 <checker> --project-root <fixture-proj>
CDAD version check — project / agents / CLI / Claude Code
  project: a1a1a1a1
  agents:  a1a1a1a1
  CLI:     a1a1a1a1
  claude-code: d4d4d4d4
verdict: DRIFT (project, agents, CLI and Claude Code are NOT the same version)
rc=1
```
Muestra que la raíz CC se resuelve **desde el registro de activación** y no se presta la versión del lado OpenCode (no cruza la frontera).

## 4. `git diff --stat` acotado (commit)

```
$ git show --stat --format="%h %s" HEAD
b05c5c1 feat: pata Claude Code aditiva en cdad-version-check.py (005-004 PD-3/AC-3)

 skills/cdad-cycle/references/project-start.md   | 10 ++++
 skills/cdad-cycle/scripts/cdad-version-check.py | 75 +++++++++++++++++++++++--
 2 files changed, 81 insertions(+), 4 deletions(-)
```

Sólo los dos artefactos declarados por la feature; `tests/` intacto.

## 5. Invariantes

- **INV-4 (compatibilidad):** sin instalación CC detectable la pata CC no aporta veredicto; los cuatro veredictos/`rc` (COHERENT/0, DRIFT/1, UNKNOWN/3, NO-PROJECT-AGENTS/4) se conservan (focal parametrizado + `no_cc` + F2).
- **INV-3 (ausencia ≠ coherencia):** sin instalación CC, la pata imprime ausencia declarada y **no** aporta un veredicto favorable; marca faltante ⇒ `unknown` con causa, nunca `0`.
- **INV-7 (sin versión prestada):** la pata lee sólo la raíz de su propia frontera; nunca el manifiesto derivado de OpenCode (`OC_VERSION not in cc` en el focal de marcador faltante y en el de drift).
- **Anti-gaming:** no se editó ningún test; focal congelado intacto.

## 6. Límites honestos / evidencia no corrida

- **Suite completa:** NO ejecutada (política de suite completa del paquete: la corre una vez quien cierra). Se corrió el focal + regresiones declaradas + regresión proporcional de consumidores de `project-start.md`.
- La ruta del **registro de activación** no está cubierta por el focal congelado (sus fixtures usan el directorio global de agentes CC). Se verificó manualmente (CMD5); el focal cubre los caminos global/ausente/F2.
- No hay objetivo lint declarado en `Makefile`; se corrió `ruff check` sobre el archivo modificado (verde). `python3 -m py_compile` OK.
- No se tocó HOME, no se desplegó, no se hizo `git push`. El cambio en `docs/.cdad-state.json` es previo a esta sesión y **no** fue incluido en el commit (queda para el coordinador/escritor único del state).
