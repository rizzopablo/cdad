# Decisión sobre review-draft-001 — 003-006 (orquestador, delegación HITL)

Veredicto del reviewer: aprobable con cambios. Se aceptan todos los puntos:

- **BL-1 (aceptado):** la re-adopción entra en el plan como **primer paso de T4**:
  `install.sh` hacia una raíz aislada nueva del commit de cierre de T1–T3, fila v5 en
  `docs/runtime-adopted-version.md`, verificación de consumidor y repunte de la raíz
  en la activación. El límite se declara: escribe bajo `~/.cache` (raíz aislada
  versionada), nunca en `~/.claude`, `~/.agents` ni `~/.config/opencode`.
- **BL-2 (aceptado):** se quita `.claude/settings.json` del contrato. Los hooks viven en
  el frontmatter de los agentes. Si V1 lo exigiera, pasa a deuda.
- **R-1 (aceptado):** la activación reescribe de forma determinista
  `command: ~/.claude/cdad-scripts/path-guard.sh <rol>` → `command: <A>/.claude/cdad-scripts/path-guard.sh <rol>`.
  El test de T2 afirma que ningún `command:` emitido contiene `~/.claude`. No se toca
  `cdad-generate.py` (parametrizar en origen → deuda).
- **R-2 (aceptado):** el guion de T4 especifica `claude -p` / `codex exec` no interactivos
  y declara que los runtimes escriben sus propios logs/sesiones bajo HOME (no es instalar CDAD).
  Para T4 el orquestador ejecuta los runtimes con un HOME temporal cuando sea viable
  (`HOME=<raíz desechable>`), y si la autenticación lo impide lo declara en el ledger.
- **R-3 (aceptado):** T3 parte de staging limpio; el commit lista solo los archivos tocados.
- **R-4 (aceptado):** la identidad de versión se comprueba contra el `.cdad-install-manifest.json`
  existente; sin herramienta nueva.
- **R-5 (aceptado):** si un archivo destino existe y difiere de lo que se emitiría, el
  generador falla con error (dry-run lo muestra); nunca sobreescribe en silencio.
- **R-6 (aceptado):** I1 se reescribe según la recomendación.
- **R-7 (aceptado):** en T4 las reglas nuevas se aplican desde una sesión nueva de
  orquestador tras la re-adopción (o leídas del repo), y queda en el ledger.
- **R-8 (aceptado):** ledger y docs nuevos sin rutas absolutas locales (marcadores `<adopted-root>`, `<project-root>`).
  La ruta absoluta preexistente en `runtime-adopted-version.md` va a deuda de anonimización.
- **N-1..N-3 (aceptados):** quitar V6; `depends_on` coherente con `consume`; la cláusula
  "hook ausente no bloquea" de P5 se evidencia solo en T4.

Siguiente paso: el architect produce spec.md y plan.md finales con estos cambios.
