# GREEN residual B4 — 003-001-role-packets

Fecha: 2026-09-18  
Rol: implementer (`gpt-5.6-sol`)  
Base: `c3425fe`

`guard_source_overlap` incorpora ahora cada destino efectivo
`<extra-dir>/<skill>` producido por `extra_skills_dirs`. Todos se canonicalizan,
incluidos componentes symlink, antes de compararlos con el repositorio fuente.
El guard corre antes de install, check, uninstall y sus modos dry-run. Los extras
aislados conservan su funcionamiento.

El método focal B4 pasó en 12,003 s y `bash -n install.sh` pasó. La suite focal
ampliada se ejecutó después de integrar el cambio:

```text
Ran 33 tests in 107.105s

OK
```

Resultado: 33/33, cero errores, skips o `BLOCKED`. El implementer sólo modificó
`install.sh` y no tocó tests.

