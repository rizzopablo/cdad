I'll start by reading the contract and the review findings, then the existing test module.
RED de la segunda ronda completado. Reporte:

## Archivos

- **Creado/commiteado:** `tests/test_006_003_rf2_review_fixes.py` (566 líneas, módulo nuevo). Nada fuera de `tests/`. `docs/planning/` y `findings/…` (sin trackear, ajenos) intactos.

## Mapa test → hallazgo

| Test | Hallazgo / condición de cierre | Resultado hoy |
|---|---|---|
| `test_b1_a_empty_digest_without_source_is_preserved_and_disclosed` | B-1 · cláusulas 1 y 4: sha `""` + source `""` y sha `""` + source ausente → se conserva, CONFLICT, sigue registrado. Control **in-run**: hermano con digest correcto se retira (no-vacuidad) | **RED** — el archivo se borra (`rm -f`, «Obsolete prune: 3 retired») |
| `test_b1_a2_uninstall_does_not_remove_an_empty_digest_record` | B-1 · cláusula 1 en la otra superficie: `--uninstall` no lo borra sin resolución explícita | **RED** — `372 of 372 removed, 0 preserved` |
| `test_b1_b_empty_digest_with_present_source_publishes_a_coherent_record` | B-1 · cláusula 2: preservado **y** registro coherente (source en su slot; nunca «registered \<source\>») | **RED** — registro `{"sha256": "rf2-…-sentinel", "source": ""}` (columnas permutadas) |
| `test_b1_c_null_digest_publishes_a_coherent_record` | B-1 · cláusula 2 con digest `null`: slot del digest ≠ token `None`; sin «registered None» | **RED** — `{"sha256": "None", …}` |
| `test_b1_control_correct_digest_still_retires_the_obsolete_own_file` | B-1 · control positivo (declarado) | **PASA** (declarado) |
| `test_opt1_wrong_env_credential_diagnosis_also_names_the_default_file` | OPT-1 · §2.3 (`spec.md:48`): con 401 y valor de entorno, el diagnóstico nombra también la ruta del archivo por defecto; valor nunca (INV-1) | **RED** — «no credential file was consulted», sin ruta |

Mecanismo/detalle declarado en el docstring del módulo (colapso del TSV de 4 columnas leído con `IFS=$'\t' read`), derivado de B-1 + sondas black-box en `/tmp/opencode` (el shape `{"sha256","source"}` del manifiesto publicado se observó ejecutando `install.sh`, **no** leyendo implementación).

## Comandos y salida

```
$ python3 -m pytest tests/test_006_003_rf2_review_fixes.py -q
FFFF.F                                              [100%]
5 failed, 1 passed in 66.60s          # 2ª corrida: 5 failed, 1 passed in 65.00s

$ ... --tb=line
unittest/case.py:732 AssertionError: Lists differ: [] != ['.agents/skills/…ADR.md', '.claude/…', '.config/opencode/…']
 B-1/INV-2: `--uninstall` borró archivos cuyos registros no tienen digest …
unittest/case.py:744 AssertionError: … tiene un registro con sha256 VACÍO … el instalador lo borró (rc=0)
unittest/case.py:732 AssertionError: '' != 'rf2-hand-edit-source-sentinel'   # slot source permutado
unittest/case.py:732 AssertionError: 'none' unexpectedly found … {'sha256': 'None', 'source': …}
unittest/case.py:744 AssertionError: OPT-1/§2.3: el diagnóstico no nombra la ruta (['…/rf2-opt1-xdg/cdad/opencode-server.env'])
```
Cada fallo es un `AssertionError` sobre comportamiento ausente (sin ImportError/syntax/fixture error). Estable en dos corridas.

## Commit

```
26667b5 test: 006-003 review-fix 2 RED (B-1 sha-less manifest records + OPT-1)
 tests/test_006_003_rf2_review_fixes.py | 566 ++++++++++++++
 1 file changed, 566 insertions(+)
```
Sin `--no-verify`, sin `git stash`, sin push.

## Límites / honestidad

- No leí `install.sh` ni ningún archivo de implementación; los oráculos salen de spec §2.3 + INV-2 + B-1/OPT-1.
- Alcance de escritura respetado: solo `tests/`. `HOME` real intacto: `stat ~/.config/cdad` → mtime `2026-10-17 19:48` (anterior a esta sesión); todo instala en raíz redirigida + HOME tempdir (INV-6).
- No leí `tests/.sensitive-patterns.local`. REUSE declarado: `InstallerHarness` (U4), `ServerCredentialCase` (U6) y funciones/constantes de U7 (ninguna clase con tests importada → sin tests ajenos duplicados).
- La coherencia del registro se ancla a lo que pide B-1 (fuente en su slot, digest sin token `None`/texto de fuente); es un oráculo de superficie publicada, no de plumbing.
