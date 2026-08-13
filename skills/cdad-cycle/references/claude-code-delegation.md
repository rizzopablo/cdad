# Claude Code Delegation — Mapeo de roles a sub-agentes

**Documento complementario a `SKILL.md` §4 (Regla de decisión de delegación).**

Cuando ejecutás CDAD en Claude Code y disponés de sub-agentes `cdad-*` nativos instalados en `~/.claude/agents/`, este documento detalla cómo delegarlos.

## Mecanismo: herramienta `Agent`

Claude Code expone la herramienta `Agent` para spawnear subagentes. El orquestador carga el skill y usa:

```python
from Agent import agent

# Ej: delegar test-writer RED
result = agent(
    subagent_type="cdad-test-writer",
    prompt="<handoff packet con contexto completo>"
)
```

O en markdown/prosa para que Claude Code lo interprete:

```
Invocá la herramienta Agent con subagent_type: cdad-test-writer
```

## Mapeo rol → subagent_type

| Rol | subagent_type | Tool | Modelo | Notas |
|-----|---|---|---|---|
| architect | `cdad-architect` | Agent | sonnet (optimus) | read-only; no requiere hooks |
| test-writer | `cdad-test-writer` | Agent | sonnet (optimus) | write-capable; hooks de path-scoping |
| implementer | `cdad-implementer` | Agent | haiku (optimus) | write-capable; hook bloquea `tests/**` |
| reviewer | `cdad-reviewer` | Agent | opus (optimus, distinto a implementer) | read-only; no requiere hooks |
| scribe | `cdad-scribe` | Agent | sonnet (optimus) | read-only; no requiere hooks |
| refactorer | `cdad-implementer` + `tdd_substage: refactor` | Agent | haiku (optimus) | Sub-modo del implementer; mismo subagent_type con contexto modificado |

## State-passing (sesiones frescas)

Los sub-agentes Claude Code arrancan **sin contexto del orquestador**, igual que en OpenCode. El handoff packet debe contener TODO lo necesario:

- **Tarea atómica** (una postcondición, un test, un diff — no agrupes)
- **Spec inline o ruta** (`docs/specs/<id>/spec.md`)
- **Interface/firma** si aplica
- **Reglas estrictas del rol** (tabla §2 del Contrato de roles en SKILL.md)
- **Output esperado y formato**
- **Campo `tdd_substage`** del state file si el rol lo usa (test-writer AUDIT/POST-AUDIT/RED, implementer GREEN/REFACTOR)

El subagente puede leer `docs/.cdad-state.json` y `docs/specs/<id>/` por sí mismo; no asumas que recuerda nada de la sesión anterior.

## Path-scoping en Claude Code (importante)

Claude Code no tiene soporte declarativo para restricciones de path (como `permission.edit: {"tests/**": deny}` en OpenCode). En cambio, los sub-agentes `cdad-*` usan **hooks PreToolUse**:

### cdad-implementer

- Hook `PreToolUse` matcher `Edit|Write` → invoca `~/.claude/cdad-scripts/path-guard.sh implementer`
- Comportamiento: bloquea `Edit`/`Write` a `tests/**` (exit code 2)
- Equivalente a OpenCode: `permission.edit/write: {"tests/**": deny}`

### cdad-test-writer

- Hook `PreToolUse` matcher `Read|Grep|Glob` → invoca `~/.claude/cdad-scripts/path-guard.sh test-writer-read`
- Comportamiento: bloquea `Read`/`Grep`/`Glob` a `src/**` y `lib/**` (invariante anti-trampa, no-negociable)
- Hook `PreToolUse` matcher `Edit|Write` → invoca `~/.claude/cdad-scripts/path-guard.sh test-writer-write`
- Comportamiento: bloquea `Edit`/`Write` a todo excepto `tests/**`
- Equivalente a OpenCode: `permission.read/grep: {"src/**": deny, "lib/**": deny}` + `permission.edit/write: {"*": deny, "tests/**": allow}`

**Caveat:** los hooks preToolUse son ejecutados ANTES de la llamada a la herramienta, pero No son tan fuertes como el enforcement OpenCode. Un subagente que logre **leer el JSON del hook antes de ejecutarlo** teóricamente podría adivinar la ruta bloqueada. En la práctica, el guard script bloquea la llamada misma (exit 2 previene la ejecución), pero la garantía es **conductual**, no **structural** (como en OpenCode con `permission` a nivel de runtime).

**Implicación:** el invariante "test-writer nunca ve `src/`" es **crítico** (AP-7, anti-trampa); se preserve vía hook, pero requiere confianza en que el runtime respecta el exit code 2 (lo hace, verificado empiricamente en validation-cdad-002.md).

## Re-delegación (NO permitida)

CDAD prohíbe explícitamente que un sub-agente delegue a otro sub-agente (GUARDIA DE SPAWN, SKILL.md §4, incidente 05 Ago 2026).

Claude Code refuerza esto: la herramienta `Agent` tiene un **límite de profundidad** (default 3 capas bajo la sesión principal). Un subagente spawnado por el orquestador que intente spawnear otro subagente lo va a encontrar rechazado después de ~3 capas.

**Regla CDAD en Claude Code:** si un subagente necesita delegar a otro, devuelve el control al orquestador con un handoff packet (prosa abierta, sin herramientas de delegación) y que ÉL decida el spawn. La guardia anti-spawn (SKILL.md) lo explica; en Claude Code se refuerza con el límite de profundidad de la plataforma.

## Handoff packet (fallback si no hay Agent tool)

Si por alguna razón Claude Code no expone la herramienta `Agent` (ej: usuario opt-out de subagentes), usa el handoff packet (prosa pegable a chat nuevo):

- Copiar el contenido de `references/handoff-prompts.md` para el rol
- Pegar en un chat **nuevo** (sesión separada, manual)
- El rol arranca en ese chat con reglas estrictas aplicadas conductualmente (sin hooks)

## Verificación (ADR-008)

La validación end-to-end de esta delegación vive en spike `cdad-002-validate-claude-code-subagents` (similar a `cdad-001` para OpenCode). Probes por rol incluyen:

1. **Creación y naming**: cada agente instalado en `~/.claude/agents/` existe y tiene el nombre correcto.
2. **Frontmatter**: tools correctos, model correcto (by profile), hooks presentes (implementer/test-writer).
3. **Hook execution**: path-guard.sh se ejecuta y bloquea según lo esperado (probes con tries intentadas a paths bloqueados).
4. **End-to-end**: mini-feature real corrida con los 5 subagentes, artefactos producidos por etapa, ningún re-spawn ilegal.

Resultado documentado en `findings/validation-cdad-002.md`.
