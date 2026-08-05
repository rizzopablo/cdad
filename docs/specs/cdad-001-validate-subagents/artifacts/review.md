# Review — cdad-001-validate-subagents

Reviewer model: bailian/qwen3.7-plus

Evalué el `impl.diff` (commit `6a5cf9a`, `scripts/validate-subagents.sh`, 96 líneas) contra la postcondición, formato mínimo de artefactos (§3), criterios de aceptación T1–T5 (§4), anti-scope (§5) y riesgos (§6) de la spec. También contrasté contra `install.sh` (fuente de verdad del cross-check) y confirmé que no existe `AGENTS.md` en el repo — las convenciones de estilo se contrastan contra `install.sh` (script hermano).

**Veredicto de las 5 postcondiciones:** todas implementadas (exit 0/≠0 con FAIL flag, lectura runtime con fallback documentado, cross-check reusando `install.sh --check`, artefactos por etapa, resumen `[etapa] artefacto -> OK/FAIL`). Sin violaciones de boundaries: el script es read-only e idempotente (todas las operaciones de verificación: `git apply --check`, `--dry-run`, `install.sh --check`). Sin hallazgos de seguridad con ≥80% de confianza (nombres de archivo son constantes fijas, sin interpolación de input de usuario, script de repo confiable).

## Hallazgos

### 1. Divergencia del spec — verificación de `impl.diff` usa `git apply`, no `patch -p1 --dry-run`
- **Ubicación:** `scripts/validate-subagents.sh:95-101` (impl.diff)
- **Problema:** La spec §3.3 define el formato mínimo de `impl.diff` como "aplicable: `patch -p1 --dry-run` exit 0", y el test de aceptación T4 (§4) aseserta exactamente eso (`patch -p1 --dry-run`). La implementación en cambio usa `git apply --check --reverse` OR `git apply --check`. No valida la misma condición que el criterio de aceptación.
- **Contexto que reduce severidad:** El comentario documenta que `patch --dry-run` falla con diffs de creación ya aplicados (archivo ya existe), y `git apply --check --reverse` es más robusto porque distingue "ya aplicado" de "aún aplicable". Justificación razonable y referenciada a `review.md`.
- **Sugerencia:** Aceptable como está, pero señalizar la divergencia en la spec o alinear T4 con este criterio; hoy el validator y la suite de aceptación miden cosas distintas.
- **Severidad:** Opcional

### 2. Inconsistencia de estilo — `set -u` (sin `-e` ni `-o pipefail`) vs. `install.sh`
- **Ubicación:** `scripts/validate-subagents.sh:39` y `:78`
- **Problema:** El script hermano `install.sh:12` usa `set -euo pipefail`. El validator usa solo `set -u`. En particular el pipeline `echo "$CHECK_OUT" | tail -3` (línea 78) corre sin `pipefail`; aunque aquí el exit code se captura de `install.sh` (no del pipeline), la falta de protección consistente es una divergencia de convención del repo.
- **Sugerencia:** Alinear a `set -euo pipefail` (o justificar por qué se omite `-e`/`pipefail` intencionalmente, dado el manejo manual de errores con `FAIL`).
- **Severidad:** Opcional

### 3. Sugerencia de simplificación — condición redundante `! -x`
- **Ubicación:** `scripts/validate-subagents.sh:73` (`if [ ! -x "$INSTALL_SH" ] && [ ! -f "$INSTALL_SH" ]`)
- **Problema:** El `! -x` es redundante. La rama `else` invoca `bash "$INSTALL_SH" --check`, y `bash` ejecuta el archivo sin necesidad del bit de ejecución. La condición real que importa es solo la existencia (`-f`).
- **Sugerencia:** Simplificar a `if [ ! -f "$INSTALL_SH" ]`.
- **Severidad:** Opcional

### 4. Inconsistencia de estilo — mensajes de error a stdout, no a stderr
- **Ubicación:** `scripts/validate-subagents.sh:50` (`fail() { echo "❌ $1"; ... }`)
- **Problema:** Los diagnósticos de falla (`❌ ...`) van a stdout. Convencionalmente los errores/diagnósticos van a stderr para no contaminar la salida verificable. (Nota: T2 depende de que `cdad-reviewer` esté en stdout, así que cambiarlo requiere ajustar el test.)
- **Sugerencia:** `fail()` debería escribir a `>&2`; ajustar T2 si se adopta.
- **Severidad:** Opcional

### 5. Divergencia del spec — §6 menciona "frontmatter + byte-compare", Etapa 1 solo verifica existencia
- **Ubicación:** `scripts/validate-subagents.sh:64-68` (Etapa 1)
- **Problema:** La tabla de riesgos (§6) dice que el validator hace "config estática (frontmatter + byte-compare)". La Etapa 1 solo corrobora que el archivo `cdad-*.md` *existe* en el runtime; no valida frontmatter ni contenido. El byte-compare se delega correctamente a `install.sh --check` (Etapa 2, conforme a postcond. #3), pero la validación de *frontmatter* no se ejecuta en ningún lado.
- **Sugerencia:** O agregar una validación mínima de frontmatter (p.ej. `name:` presente) en Etapa 1, o corregir la narrativa de §6 para reflejar que el frontmatter se cubre indirectamente por el byte-compare de `install.sh --check`.
- **Severidad:** Opcional

---

## Veredicto: PASS

La implementación satisface las cinco postcondiciones, respeta boundaries (read-only, idempotente, no duplica lógica de `install.sh`), no introduce riesgos de seguridad identificables y todos los hallazgos son opcionales de estilo/robustez. Ningún hallazgo bloquea el merge.

LISTO. Resumen: 0 bloqueantes, 5 opcionales.
