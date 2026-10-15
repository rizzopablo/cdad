Committed as `5316650`. Report follows.

## 1. Archivos tocados (diff resumido)

**`skills/cdad-cycle/references/project-start.md`** (§11, el ofensor nombrado por el oráculo A2):
```
-`cdad_packet.py status` (`orientation.md` §1), the single bounded projection
+`<skill-dir>/scripts/cdad_packet.py status` (`orientation.md` §1), the single bounded projection
```
El bloque `sh` de esa sección ya usaba el marcador; no se tocó.

**`skills/cdad-cycle/references/orientation.md`** (misma clase):
- §1, primera acción: `The first orientation action is the compact operational view of `cdad_packet.py`` → `` `<skill-dir>/scripts/cdad_packet.py` ``.
- §3, tabla de operaciones frecuentes (5 filas): `validate-state`, `validate-request`/`validate-packet`, `prepare`, `prepare --record-dispatch` y `cdad_continuity.py begin` reescritas como `` `<skill-dir>/scripts/cdad_*.py …` ``.

Total: 2 archivos, +8/−7. No se tocaron tests, assets ni ningún otro archivo.

## 2. Comandos y salidas

```
$ python3 -m pytest tests/test_005_006_t6_owner_reviewfix.py -q
.....                                                                    [100%]
5 passed in 0.06s

$ python3 -m pytest tests/test_005_006_t1_start_procedure.py -q
...............                                                          [100%]
15 passed in 0.06s

$ python3 -m pytest tests/test_005_003_t2_examples_execute.py tests/test_005_003_t1_compact_view.py -q
.....................                                                    [100%]
21 passed in 7.98s
```

(Antes del cambio, `test_hallazgo_a2_cli_invocations_derived_from_skill_dir` fallaba con `project-start.md:196` como único ofensor; confirmado con la corrida de reproducción.)

Búsqueda de la misma clase en los archivos de cableado (grep de `cdad_*.py` sin `<skill-dir>`): sin ofensores restantes en los 7 archivos que escanea el oráculo A2.

## 3. Hash del commit

`5316650fabacb2d714ab27bcf3975fe92e1871cf` — `fix(005-003): invocaciones del cableado con el marcador <skill-dir> (A2 de 005-006)` (solo los 2 archivos, verificado con `git show --stat`).

## 4. Otros ofensores de la misma clase (declarados, SIN tocar)

`orientation.md` líneas **69** y **71** (sección «Root-relative asymmetry»): `` `cdad_packet.py` requires an absolute `--project-root` `` y `` `cdad_continuity.py resume --project-root .` resolves the relative root `` — referencias/forma de comando del CLI sin el marcador. El oráculo A2 **no escanea** `orientation.md` y el encargo acotó la edición de ese archivo a la frase de la primera acción (línea ~16) y a la tabla de operaciones; por eso las dejé intactas (`No cambies nada mas`). No verifiqué si son de esta feature; se reportan para decisión del orquestador.

Nota: `docs/` y el ADR-025 aparecen modificados en el working tree por el trabajo del orquestador; **no** los toqué ni los incluí en el commit (write scope: `skills/`). La suite completa no se corrió (política del encargo).