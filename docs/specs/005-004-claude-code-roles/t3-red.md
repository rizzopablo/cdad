# Informe de RED — 005-004-claude-code-roles, T3

**Rol:** test-writer (etapa 3, subetapa RED) · **Paquete:** `005-004-claude-code-roles-test-writer-red-003`
**Feature:** `005-004-claude-code-roles` · **Execution:** `exec-005-004-claude-code-roles-001`
**Contrato:** `docs/specs/005-004-claude-code-roles/spec.md` (sha256 `79d57e0a…2ec945`), PD-3 / AC-3 / INV-3 / INV-4 / INV-7
**Focal:** `tests/test_005_004_t3_version_check_cc.py` (nuevo) · **Commit:** `4828c0c885665bbe2ab9e3b7b7b5c8128a3b9b3f`

## Método (oráculo independiente)

No se leyó el código del comprobador ni ningún otro archivo de implementación. El oráculo es
`cdad-version-check.py` **como programa**: se invoca como subproceso y sólo se lee su salida
observable y su `rc`, alimentándolo con *fixtures de raíces de instalación* construidos en
`tmp_path` (HOME aislado, nunca HOME real ni el repo, con `CDAD_*` esterilizados en el env):

- **raíz OpenCode de fixture**: `<root>/.config/opencode/agents/` + `<root>/version.txt`, con el
  manifiesto del proyecto `<project>/.opencode/agents/.cdad-derived.json`
  (`source_version`, `source_dir` → raíz de agentes) que alimenta las patas `project`/`agents`;
- **pata `CLI`**: el comprobador se copia (bytes, sin abrirlo) dentro de
  `<root>/.config/opencode/skills/cdad-cycle/scripts/`, layout de instalación que hoy resuelve esa pata;
- **instalación de Claude Code detectable**: `<home>/.claude/agents/cdad-*.md` presentes y el
  marcador de su raíz `<home>/version.txt` (y `<home>/.claude/agents/version.txt`, por el patrón
  "junto a los agentes" de PD-14).

Versiones sintéticas: `a1a1a1a1` (lado OpenCode), `b2b2b2b2` (raíz CC distinta), `c3c3c3c3` (drift).

## Mapa test → postcondición/criterio

| Test | Afirmación observable | Contrato |
|---|---|---|
| `test_pd3_cc_leg_reports_version_when_coherent` | Con instalación CC detectable y valores coherentes, informa la versión de la pata CC y el veredicto sigue COHERENT (rc 0) | PD-3(a)(i) / AC-3 |
| `test_pd3_cc_leg_participates_in_verdict_drift` | Con instalación CC detectable de **otra** raíz, la pata participa y el veredicto pasa a DRIFT (rc 1); la pata reporta **su** versión (`b2b2b2b2`) y **no** la del lado OpenCode (`a1a1a1a1`) | PD-3(a)(c) / AC-3 / INV-7 |
| `test_pd3_no_cc_installation_declares_absence_and_keeps_verdict` | **Sin** instalación CC detectable: veredicto y `rc` idénticos a hoy (COHERENT/0) **y** línea declarada de ausencia | PD-3(b) / INV-4 (ítem 2) |
| `test_pd3_missing_cc_marker_is_unknown_with_cause_not_borrowed` | Marcador faltante ⇒ `unknown` **con causa**, nunca `0` ni la versión del manifiesto derivado de OpenCode | PD-3(d) / INV-3 / INV-7 |
| `test_pd3_existing_verdicts_unchanged_without_cc[drift\|unknown\|no-project-agents]` | Sin CC detectable, DRIFT/1, UNKNOWN/3 y NO-PROJECT-AGENTS/4 siguen como hoy, con la ausencia declarada (COHERENT/0 queda en el test anterior) | PD-3(b) / INV-4 (ítem 4) |
| `test_pd3_checkout_without_marker_stays_unknown_f2` | Invocación desde el checkout sin marcador: sigue UNKNOWN (rc 3) y declara la ausencia de la pata CC | PD-3(c) / INV-4 (F2) |

## Comandos exactos y salida

```
$ python3 -m pytest tests/test_005_004_t3_version_check_cc.py -q --tb=line
FFFFFFFF                                                                 [100%]
<repo>/tests/test_005_004_t3_version_check_cc.py:201: AssertionError: PD-3(a)/AC-3: con una instalacion de Claude Code detectable el comprobador no informa la version de esa pata:
<repo>/tests/test_005_004_t3_version_check_cc.py:237: AssertionError: PD-3(a)/AC-3: con una instalacion de Claude Code detectable el comprobador no informa la version de esa pata:
<repo>/tests/test_005_004_t3_version_check_cc.py:276: AssertionError: PD-3(b)/INV-4: sin instalacion CC detectable no aparece la linea declarada de ausencia de la pata:
<repo>/tests/test_005_004_t3_version_check_cc.py:304: AssertionError: PD-3(d)/INV-3: con agentes CC detectables y marcador faltante el comprobador no declara la pata CC:
<repo>/tests/test_005_004_t3_version_check_cc.py:366: AssertionError: PD-3(b)/INV-4: sin instalacion CC detectable no aparece la linea declarada de ausencia de la pata (caso drift):
<repo>/tests/test_005_004_t3_version_check_cc.py:366: AssertionError: PD-3(b)/INV-4: sin instalacion CC detectable no aparece la linea declarada de ausencia de la pata (caso unknown):
<repo>/tests/test_005_004_t3_version_check_cc.py:366: AssertionError: PD-3(b)/INV-4: sin instalacion CC detectable no aparece la linea declarada de ausencia de la pata (caso no-project-agents):
<repo>/tests/test_005_004_t3_version_check_cc.py:398: AssertionError: PD-3(b)/INV-4: sin instalacion CC detectable no aparece la linea declarada de ausencia de la pata:
=========================== short test summary info ============================
FAILED tests/test_005_004_t3_version_check_cc.py::test_pd3_cc_leg_reports_version_when_coherent
FAILED tests/test_005_004_t3_version_check_cc.py::test_pd3_cc_leg_participates_in_verdict_drift
FAILED tests/test_005_004_t3_version_check_cc.py::test_pd3_no_cc_installation_declares_absence_and_keeps_verdict
FAILED tests/test_005_004_t3_version_check_cc.py::test_pd3_missing_cc_marker_is_unknown_with_cause_not_borrowed
FAILED tests/test_005_004_t3_version_check_cc.py::test_pd3_existing_verdicts_unchanged_without_cc[drift-DRIFT-1]
FAILED tests/test_005_004_t3_version_check_cc.py::test_pd3_existing_verdicts_unchanged_without_cc[unknown-UNKNOWN-3]
FAILED tests/test_005_004_t3_version_check_cc.py::test_pd3_existing_verdicts_unchanged_without_cc[no-project-agents-NO-PROJECT-AGENTS-4]
FAILED tests/test_005_004_t3_version_check_cc.py::test_pd3_checkout_without_marker_stays_unknown_f2
8 failed in 1.02s
```

**Motivo de cada RED (todos `AssertionError`, ningún error de import/sintaxis/entorno):**

1. `cc_leg_reports_version_when_coherent` — el comprobador no declara la pata CC (no hay línea que
   nombre Claude Code): falta la observación de PD-3(a) (los controles `project/agents/CLI` = `a1a1a1a1`
   pasan).
2. `cc_leg_participates_in_verdict_drift` — falta la pata CC; además, con la instalación CC detectable
   en `b2b2b2b2` el veredicto de hoy es COHERENT/0 y el contrato exige DRIFT/1. Reproducción manual
   del fixture (mismos bytes de fixture, subproceso directo):

```
$ HOME=<fixture-home-CC-b2b2b2b2> python3 <fixture-root>/.config/opencode/skills/cdad-cycle/scripts/cdad-version-check.py --project-root <fixture-project>
CDAD version check — project / agents / CLI
  project: a1a1a1a1
  agents:  a1a1a1a1
  CLI:     a1a1a1a1
verdict: COHERENT (project, agents and CLI are the same version)
rc=0
```

3. `no_cc_installation_declares_absence_and_keeps_verdict` — veredicto/`rc` de hoy se conservan
   (COHERENT/0, control verde), pero no aparece la línea declarada de ausencia de la pata (ítem 2).
4. `missing_cc_marker_is_unknown_with_cause_not_borrowed` — no se declara la pata CC con marcador
   faltante (PD-3(d)); sin hueco para `0` ni versión prestada.
5-7. `existing_verdicts_unchanged_without_cc[drift|unknown|no-project-agents]` — controles de
   veredicto/`rc` verdes (DRIFT/1, UNKNOWN/3, NO-PROJECT-AGENTS/4); falla la línea de ausencia.
8. `checkout_without_marker_stays_unknown_f2` — F2 conservado (UNKNOWN/3 verde); falla la línea de
   ausencia.

**Controles de no-regresión declarados por el plan (verdes):**

```
$ python3 -m pytest tests/test_005_006_t6_owner_reviewfix.py tests/test_005_003_t2_examples_execute.py -q
...............                                                          [100%]
15 passed in 1.92s
```

## Diff y commit

```
$ git show --stat --oneline 4828c0c
4828c0c test: RED 005-004 T3 — pata Claude Code del chequeo de version (PD-3/AC-3)
 tests/test_005_004_t3_version_check_cc.py | 404 ++++++++++++++++++++++++++++++
 1 file changed, 404 insertions(+)
```

- **Commit:** `4828c0c885665bbe2ab9e3b7b7b5c8128a3b9b3f` (prefijo `test:`, sólo `tests/`; 0 archivos
  fuera del alcance de escritura). `docs/.cdad-state.json` quedó modificado **preexistente**, no
  tocado por este rol.

## Límites honestos y decisiones de contrato

- **Interfaz de fixture declarada por este focal** (el implementer la satisface o el GREEN no es
  legítimo): la instalación CC es detectable por `<home>/.claude/agents/` y su versión se lee en la
  raíz de instalación detrás de esos agentes (`<home>/version.txt`; se acepta también
  `<home>/.claude/agents/version.txt` por el patrón "junto a los agentes"). La resolución desde el
  **registro de activación** (`.cdad/activation.json`) que PD-3 nombra *no* se usó en el fixture:
  el focal consigue la raíz CC distinta de la del CLI sin él, y no se quiso fijar una clave de
  registro no verificada. El registro queda para el GREEN como camino declarado, no asertado aquí.
- La etiqueta de la línea CC se acepta con cualquier forma razonable (`claude-code:`, `Claude Code:`,
  `cc:`) y también embebida en otra línea; lo exigido es que **nombre la pata y su valor**.
- En `missing_cc_marker…` **no** se asertó el veredicto global: PD-3 fija que una marca faltante es
  `unknown` **con causa** y prohibe `0`/versión prestada, pero no fija si el veredicto global debe
  pasar a UNKNOWN cuando la instalación CC es detectable y le falta el marcador; no se inventó esa
  decisión (el veredicto/`rc` sí quedan asertados en los casos ya cubiertos de no-regresión).
- Este rol no vio la implementación (aislamiento de fase conservado); los bytes del comprobador sólo
  se copiaron para el fixture, nunca se abrieron. La suite completa **no** se corrió (política del
  paquete: la corre una vez quien cierra).
