I'll start by reading the approved spec and the current test files involved.
Diagnosis confirmed. Now let me inspect which documents the selector currently picks and which ones would satisfy candidate discriminators (docs are data surfaces for this oracle; not implementation code).
The false positive is confirmed (a historical 005-004 planning/report block matched via "verifica"). Let me validate a precise discriminator before editing.
Now I'll implement the narrowing in the shared U3 test module.
Now the selectors themselves:
Now let me verify: the selector picks exactly the two preservation copies, and the full U3 + coupled modules pass on HEAD.
Discrimination evidence: mutation runs in a temp working copy (docs/ in the repo is untouched).
All mutations fail as AssertionError. Now the coupled + adjacent regression set:
The one failure is a pre-existing timing flake (passes 3/3 in isolation; no reference to the modified helpers). Let me review the final diff.
**Role: test-writer — substage `red` (TESTFIX acotado U3, paquete `test-writer-red-004`). Intake: validated packet** (`006-002-delegation-by-layer-test-writer-red-004`; canonical metadata presente y válido). No se cargaron skills de ciclo.

## Diagnóstico (confirmado antes de tocar nada)

`framed_evidence_documents()` devolvía **416** documentos de `docs/**` con marcador de evidencia. Sobre ese texto unido, el guard de `exit 2` de 005-004 T4 leía un informe histórico —`docs/specs/005-004-claude-code-roles/spec.md` PD-4: *«verifica las decisiones del guard, **no** que Claude Code honre `exit 2`»*— que matchea `honor`/`verific` y cuya ventana no declara alcance: `AssertionError` sobre el GREEN, por defecto del oráculo.

## Cambio (solo `tests/`, commit `20bb835`)

| Archivo | Cambio |
|---|---|
| `tests/test_006_002_u3_runtime_references.py` | +`preserved_reference_names()`, +`preservation_copy_documents(reference_name=None)`, +`SELF_PRESERVATION_RE`/`WITHDRAWAL_DECLARATION_RE`; `framed_evidence_documents()` re-documentada como superficie ANCHA (de 416 → 2 copias). Docstring: testfix + límites honestos |
| `tests/test_005_004_t4_cc_guard_decisions.py` | `evidence_text()` → `preservation_copy_documents("claude-code-delegation.md")`; docstrings de los dos guards de conservación |
| `tests/test_005_009_t3_spawn_reconciliation.py` | igual (copia CC) |
| `tests/test_005_010_t3_references.py` | igual (copia OpenCode) |

**Selección por contenido, sin fijar ruta:** un documento es la copia preservada si un **mismo bloque** (a) tiene como sujeto al propio documento (`this document / este documento … preserv\w*|conserv\w*`), (b) nombra la referencia retirada y (c) declara su retiro. Las **aserciones no cambian**: sobre la copia siguen exigiéndose alcance interactivo + `-p` + desconocido, la prohibición de spawn y el detalle de carga de OpenCode.

```
$ python3 -c "...preservation_copy_documents()..."
framed (ancha): 416
copias preservadas (todas): ['docs/evidence/runtime-delegation/claude-code-delegation.md',
                            'docs/evidence/runtime-delegation/opencode-delegation.md']
claude-code-delegation.md -> ['docs/evidence/runtime-delegation/claude-code-delegation.md']
opencode-delegation.md    -> ['docs/evidence/runtime-delegation/opencode-delegation.md']
inexistente -> []
```

```
$ python3 -m pytest tests/test_006_002_u3_runtime_references.py \
    tests/test_005_004_t4_cc_guard_decisions.py \
    tests/test_005_009_t3_spawn_reconciliation.py \
    tests/test_005_010_t3_references.py -q
36 passed in 4.46s      # (antes: 1 failed — el focal del diagnóstico)
```

## El oráculo sigue discriminando (mutaciones en copias temporales; `docs/` nunca editado)

```
control (copia sin mutar = HEAD): TestConsumerReference rc=0 2 passed | 005-009 rc=0 19 passed | 005-010 rc=0 5 passed
A copia preservada conserva la afirmación y pierde el alcance → rc=1 AssertionError 'interactiv' not found (1 failed, 1 passed)
B copia preservada DESAPARECE                                → rc=1 AssertionError (2 failed | 1 failed)
C copia OpenCode pierde el detalle (carga/identidad)         → rc=1 AssertionError (1 failed)
D copia CC pierde la prohibición de spawn                    → rc=1 AssertionError (1 failed)
```
Ningún fallo es Import/Syntax/ModuleNotFound. Mutación A reproducible con el texto: `pytest ... ::test_pd4_exit2_claim_stays_scoped_in_the_preserved_evidence → 1 failed in 0.47s`.

## Regresión ejecutada

`108 passed, 2 skipped, 1 failed in 105.59s` sobre U1+U2+U3, 005-004 T1–T4, 005-009 T1–T4, 005-010 T1–T4, 005-005 T2/T3. El único fallo es `test_005_010_t2...::test_pd4_default_argv_standalone_auto_without_server` — **flake de timing ajeno al cambio** (no referencia los helpers: `grep` vacío; `'destination opencode did not answer within 2.0 seconds'` bajo carga; **3/3 pases en aislamiento**, ~2.1 s). No se re-intentó el resto ni se sustitutó ninguna medición.

## Declaraciones honestas

- **Commit:** `20bb835` (4 archivos, +175/−41), sin `--no-verify`, sin `git stash`, sin push. `git status` post-commit: solo los 4 tests modificados.
- **Lectura fuera de `read_scope`:** leí documentos `docs/**` (superficies de datos del oráculo: la copia preservada y los informes históricos) — documentación no instalable, **no** código de implementación. No abrí `skills/**`, `sources/**`, `scripts/**`, `agents/**` (la contaminación de fase por parte del producto viene solo del propio test, que los lee por diseño).
- **Límite del oráculo (declarado en el módulo):** la copia se identifica por su DECLARACIÓN de preservación, no infalible: reconoce las formas listadas en `SELF_PRESERVATION_RE`/`WITHDRAWAL_DECLARATION_RE`; una copia que no se declare la copia (o no declare el retiro) hace fallar el guard por contrato («drift del oráculo»), nunca pasar en silencio.
- **No son míos:** `docs/planning/` y `findings/incremental-construction-...md` aparecen untracked (mtime 22:03) — no los creé ni los toqué; quedaron fuera del commit.
- No corrí la suite completa (política del paquete: la corre quien cierra). Sin commits de docs/state.
