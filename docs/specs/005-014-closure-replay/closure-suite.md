# Suite de cierre — 005-014-closure-replay

La corrió una sola vez el orquestador OpenCode (HITL delegada del epic-005) el 2026-10-14, en un **worktree aparte**.

- **Versión:** worktree `--detach` en `2de9747`, que incluye el código de T1 (`a4028af`) y toda la documentación de la unidad (RED, GREEN, aceptación, review). Se armó con `make staging` en el perfil por defecto (el instalador despliega el set staged: sin `build/staging/manifest.json` el propio arnés de P4 falla su precondición). El código de producto del worktree es **byte a byte** el del commit de cierre de la unidad: `git diff --name-only a4028af..2de9747 -- skills/ scripts/ agents/ sources/ build/ install.sh` → vacío.
- **Suite:** `python3 -m pytest tests -q -p no:cacheprovider` → **1028 passed y 4 skipped, sin fallos** (19 min 42 s). Los 1028 incluyen los 4 focales nuevos de T1.
- **`make validate`:** **155 PASS y 1 FAIL**. El fallo es **F011** (`scripts/validate-subagents.sh`, drift de copia instalada), **preexistente y declarado** (D-6 de 005-011); es el mismo resultado que la suite de cierre de 005-012.
- **Equivalencia:** entre `a4028af` y este registro solo cambia documentación (`docs/**` y el state); ningún archivo de producto. No se re-corrió nada más.
- **Aceptación:** el escenario de T2 (`docs/specs/005-014-closure-replay/acceptance.md`) se corrió sobre el CLI del repo con proyecto descartable y da AC-1/AC-2/AC-3 en verde; el reviewer lo reprodujo por su cuenta sobre su propio proyecto descartable.
