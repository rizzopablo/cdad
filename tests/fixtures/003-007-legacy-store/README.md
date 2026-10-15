# Store legado pre-003-007 (fixture versionado) — 003-007 T1

Store de continuity **sintético, creado UNA VEZ** con el CLI del repo
**antes del GREEN de 003-007** (2026-10-08). En ese momento
`scripts/cdad_continuity.py` es exactamente un escritor pre-003-007:
`begin` con referencias de la forma string congela entradas
`{"path","sha256"}` SIN `class`/`fields` — la forma que 003-007 (P7/D6)
resuelve **por comparación** en lectura.

## Comando de generación exacto (fuera del test, no reproducible
post-GREEN con este shape: el GREEN estampa la clase resuelta)

```sh
GEN_ROOT=<tmp>/cdad-003-007-legacy-gen
# 1) proyecto sintético (archivos de abajo, rutas relativas):
#    fixture/exec.json            — contexto plano de 001 (forma T1 003-004)
#    docs/cdad-policy.json        — path_policy (forma 002/004)
#    fixture/legacy-note.md       — "Nota sin clase declarada (compat legada).\n"
#    fixture/update.json          — D11 con references=["fixture/legacy-note.md"]
# 2) congelar el store:
env -u TMPDIR python3 scripts/cdad_continuity.py begin \
    --project-root "$GEN_ROOT/proj" \
    --execution-context "$GEN_ROOT/proj/fixture/exec.json" \
    --update "$GEN_ROOT/proj/fixture/update.json" \
    --json < /dev/null
```

Salida: rc 0, `seq 1`, `body_sha256 =
9038f7ee24d09e59e63d94039008328470e8d8dbe0291771227f4668eb055b7c`,
`references = [{"path": "fixture/legacy-note.md",
"sha256": "82992b324a36ab6e4cb18b41a1b7b8d83cbf631704f862fd59057744e64a313d"}]`
(sin `class` — pre-003-007). Identidad: `execution_id =
exec-003-007-t1-red-001` (misma constante que
`tests/test_003_007_t1_reference_classes.py`).

## Consumo

Los tests P7 de `tests/test_003_007_t1_reference_classes.py` copian ESTE
directorio a un tmp (`shutil.copytree`) y corren `resume` sobre la copia:

- intacto → verificado como `contract` (state `unchanged`);
- editando/borrando `fixture/legacy-note.md` en la copia → `changed`/
  `missing` con `legacy: true`, rc 0 (no bloquea).

Prohibido como fuente: los stores reales de `.cdad/` del repo
(autocontención, nota del orquestador del paquete
`003-007-living-continuity-test-writer-red-001`).
