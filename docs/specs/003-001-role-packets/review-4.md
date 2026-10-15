# Review focal 4 — B4 symlink (cdad-reviewer, Claude)

Veredicto: **APROBADO-COMENTARIOS** — 0 bloqueantes, 2 opcionales, 1 abstención.

- Symlink de directorio al repo con `CDAD_INSTALL_ROOT=REPO`: install, `--check` y
  uninstall dry-run abortan con `ERROR: Managed install destination overlaps the source repository`.
- Symlink al archivo `install.sh`: falla antes del guard (`Model profiles script missing`),
  fail-safe; mismo comportamiento que antes del fix, no es una regresión.
  Opcional (bucket hardening): resolver `BASH_SOURCE[0]` con `readlink -f` y agregar
  un test para este caso.
- Opcional: comentar que la canonicalización de `SCRIPT_DIR` es un requisito de seguridad.
  **Aplicado** en install.sh:19-20.
- Sin regresión en otros usos de SCRIPT_DIR (models, allowlist, path-guard, skills, agents).
- `tests/test_role_packet_review_regressions.py`: 8 passed.
- Abstención: no se verificó en macOS/BSD.
