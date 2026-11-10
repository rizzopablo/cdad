# Condiciones de la corrida base (T4) — 017-001-suite-performance

Fijadas antes de ejecutar, segun spec §4.4 y plan T4.

- Fecha de arranque: 2026-11-07T15:55:20Z (UTC)
- Revision efectiva: `7426438bdbace78d55f3ea97f1a74e2d000a7310` (registrada por `attempt.json`, `dirty=0`)
- Arbol: sin cambios pendientes al fijar (git status limpio)
- Seleccion: `--all` (2034 nodeids coleccionados, suite completa)
- Comando: `python3 scripts/cdad-suite.py close --all --evidence-root <repo-parent>/evidence/017-001-baseline`
- Registro de alcance aplicado: `performance/operation-scope.json` (calibrated=true)
- Instrumentacion: la del commit fijado (T1/T2/T3); sin variables de entorno adicionales
- Staging/caches: `build/staging/manifest.json` presente en el checkout; cache de producto y de staging del suite en estado inicial de la corrida (ninguna precarga)
- Recursos: 8 nucleos; RAM 31 GB (20 GB libres al fijar); carga `3.43 3.92 4.64 4/3257 3645080`; disco libre 30 GB
- Evidencia cruda: `<repo-parent>/evidence/017-001-baseline` (fuera del repo, ruta estable del workspace)
- Alcance declarado vs observado: se contrasta al cerrar la corrida con `reconcile` y `entry-check`
- Suite completa: esta corrida **es** la corrida completa autorizada por el dueno para la base

## Intento previo descartado

El primer intento (`attempt-20261107T155542924336Z-668613-be25e07e`, 4443.5 s)
termino con 7 fallos **ambientales** en
`tests/test_005_002_t3_application_privacy.py`: `setUp` preferia
`/tmp/opencode` sin comprobar escritura y ese directorio pertenece a otro
usuario en este host. Los siete fallos son `PermissionError`, no fallos del
producto, y ocurren en el 26 % de la corrida. Se corrigio la causa (commit
`c73e96e5`, mismo patron que `27ac3a88`) y se rehizo la base sobre revision
sana; el intento descartado se conserva como evidencia del diagnostico.

## Intento efectivo

`attempt-20261107T171212569537Z-1474770-69bdbdcf`: 4994.27 s de pytest,
2029 passed / 0 failed / 5 skipped, canary delta 0, `rc=0`. Artefactos:
`performance/baseline.json`, `performance/baseline.md`, y la reconciliacion en
`evidence/017-001-baseline2/reconciliation/`.
