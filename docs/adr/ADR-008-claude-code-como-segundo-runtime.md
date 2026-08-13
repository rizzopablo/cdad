# ADR-008 — Claude Code como segundo runtime objetivo para CDAD

**Fecha:** 2026-08-13  
**Status:** Approved (Fase 1 implementación 13 Aug 2026, pending validation spike `cdad-002`)  
**Contexto:** Expansión de CDAD más allá de OpenCode (runtime de referencia desde ADR-002) para incluir Claude Code como runtime con soporte completo de sub-agentes.

---

## Problema

CDAD hoy está documentado como soportable "de forma nativa" en Claude Code (referencias imprecisas en `SKILL.md` §"Compatibilidad multi-entorno" línea 427 y `sub-agent-strategies.md` línea 46), pero **ninguno de los 5 sub-agentes existe en formato Claude Code**, y las referencias documentan explícitamente que ese entorno es fallback genérico sin soporte nativo.

Discrepancia: la metodología CDAD es **agnóstica del arnés**, pero la implementación no. El usuario quiere el mismo flujo CDAD (5 roles, aislamiento de sesión, routing de modelo por rol) disponible en Claude Code.

## Opciones consideradas

### Opción A: Mantener estado quo (fallback handoff packet)

- Dejar CDAD como OpenCode-only, documentar Claude Code como fallback manual (handoff packet).
- Ventaja: cero ingeniería, SKILL.md ya lo cubre.
- Desventaja: frena adopción, fricción manual, pierde aislamiento de sub-agentes nativos.

### Opción B: Portar 1:1 cada agente OpenCode → Claude Code

- Traducir directamente 5 archivos `cdad/agents/*.md` → formato Claude Code.
- Desventaja: Claude Code no tiene soporto para path-scoping declarativo (`permission.edit: {"tests/**": deny}` no existe).
- Resultado: dos de los 5 agentes (implementer, test-writer) pierden garantías críticas (test-writer never sees `src/` es AP-7, no-negociable).

### Opción C: Reconstruir path-scoping vía hooks + duplicar frontmatter (ELEGIDA)

- Crear 5 agentes nuevos en `cdad/agents/claude-code/cdad-*.md` (nuevos archivos, no comparten con OpenCode).
- Los 3 read-only (architect, reviewer, scribe) son triviales: `tools:` omite `Edit`/`Write`.
- Los 2 write-capable (implementer, test-writer) usan `hooks.PreToolUse` que invoca un guard script `~/.claude/cdad-scripts/path-guard.sh <rol>`.
- Guard script Lee JSON del hook (`tool_name`, `tool_input.file_path`), bloquea según la regla del rol (exit 2).
- Documentar explícitamente que la garantía es **conductual** (hook bloquea la llamada), no **structural** (como OpenCode con `permission` a nivel de runtime).
- Aceptar duplicación de frontmatter por ahora; queda marcada como deuda técnica si divergen en mantenimiento.

Ventaja: soporte completo de subagentes nativos en Claude Code; único trade-off documentado es que path-scoping es más débil (pero verificable empíricamente).  
Desventaja: ingeniería de hooks + guard script; validación requiere probes reales (no simulación).

## Decisión

**Opción C.** CDAD expande a Claude Code con:

1. **5 agentes nuevos** en `cdad/agents/claude-code/cdad-*.md` (formato Claude Code, frontmatter nativo).
2. **Guard script** `cdad/scripts/claude-code-path-guard.sh` que reconstruye path-scoping vía PreToolUse hooks.
3. **Extensión de `cdad-models.sh`** con función `cdad_model_claude <perfil> <rol>` que mapea a alias Anthropic (haiku/sonnet/opus/fable).
4. **Actualización de `install.sh`** para instalar también targets Claude Code sin tocar lógica OpenCode.
5. **Correcciones documentales**: SKILL.md §4 y §"Compatibilidad", nuevo `references/claude-code-delegation.md`, corrección de `references/sub-agent-strategies.md`.
6. **Validación spike** `cdad-002-validate-claude-code-subagents` (end-to-end con 5 subagentes reales, probes por rol).

## Razones

### Path-scoping via hooks (no declarativo)

Claude Code no expone un mecanismo de `permission.edit: {"tests/**": deny}` a nivel de frontmatter. El único mecanismo de reconstrucción es un hook `PreToolUse` que:
1. Corre ANTES de cada llamada a `Edit`/`Write`/`Read`/`Grep`/etc.
2. Recibe JSON con `tool_name` e `tool_input.file_path`.
3. Puede bloquear (exit 2) la ejecución.

Esto es verificable (encontrado en ~30 agentes reales instalados + doc oficial vía `claude-code-guide` agent) y soportado desde Claude Code 1.0.

Garantía: **conductual**. El hook bloquea la llamada antes de que se ejecute. No es tan fuerte como el enforcement de OpenCode (que opera a nivel de runtime), pero es suficiente si el runtime respeta el exit code (verificado en validation spike).

### Invariante anti-trampa (AP-7)

El test-writer nunca debe ver `src/` o código de implementación. Es el corazón del aislamiento test-writer ↔ implementer. En Claude Code se reconstruye con:

```bash
cdad/scripts/claude-code-path-guard.sh test-writer-read
# bloquea Read/Grep/Glob a src/** y lib/**
```

Documentado como **crítico** en ADR-008 y probes explícitos en `validation-cdad-002.md`.

### Invariante reviewer ≠ implementer (ADR-001)

"Reviewer en familia de modelo distinta al implementer" es no-negociable (anti-confirmation-bias). En OpenCode se cumple con cross-provider (`mofgw/qwen3.7-plus` vs `mofgw/deepseek-v4-flash`). En Claude Code se degrada a **distinto dentro de Anthropic**: `opus` vs `haiku` (optimus profile).

Esto es **más débil** (ambos son Anthropic, no cross-provider), pero sigue ofreciendo diversity (distintos modelos = distintas heurísticas). Se documenta explícitamente en `references/claude-code-delegation.md` como trade-off.

### Bash: permiso completo (sin granularidad por comando)

Claude Code no soporta `permission.bash: {"go test*": allow, "*": deny}`. Se otorga `Bash` completo en `tools:`, igual que se simplificó OpenCode en 2026-08-10 (`.worker/permissions-fix/`). Precedente ya sentado en el proyecto.

### Modelo: Anthropic-only, extensible vía env

Claude Code no expone custom gateways (tipo `mofgw`). Se usa `model: <alias>` (`haiku`/`sonnet`/`opus`/`fable`) o model ID completo.

Para premium profile, se podría extender (p.ej. `CDAD_PREMIUM_MODEL_REVIEWER=claude-opus-5`) pero es future work. Hoy: alias puro.

## Consecuencias

### Positivas

- CDAD disponible en Claude Code con aislamiento real de sub-agentes.
- Mismo flujo que OpenCode (5 etapas, gates, roles, Memory Bank).
- Validable empiricamente (validation spike con probes reales).
- Documentación clara del trade-off (path-scoping vía hook, no declarativo).

### Negativas

- Ingeniería adicional: guard script + hooks + validación.
- Duplicación de frontmatter (5 nuevos .md files) vs. código compartido.
- Path-scoping más débil (conductual, no structural) — requiere confianza en runtime.
- Setup: usuario debe instalar agentes + guard script con `install.sh` antes de usar.

## Trade-offs Explícitos

| Aspecto | OpenCode | Claude Code | Documentado |
|---------|----------|------------|---|
| Sub-agentes nativos | ✓ | ✓ | Sí |
| Path-scoping | Declarativo (`permission`) | Via hook (`PreToolUse`) | Sí, en ADR-008 + claude-code-delegation.md |
| Reviewer ≠ implementer | Cross-provider (`mofgw/*`) | Anthropic-only (`opus` vs `haiku`) | Sí, explícito trade-off |
| Bash granularidad | Por comando (`go test*`) | Completo (`Bash`) | Sí, precedente en .worker/permissions-fix/ |
| Garantía path-scoping | Structural (runtime) | Conductual (hook) | Sí, crítico en validation |

## Verificación

**Validation spike `cdad-002-validate-claude-code-subagents`** (similar a `cdad-001`):

1. **Instalación**: `install.sh --optimus` (Claude Code target).
2. **5 agentes instalados**: verificar en `~/.claude/agents/cdad-*.md`.
3. **Guard script presente**: `~/.claude/cdad-scripts/path-guard.sh`.
4. **Probes por rol** (tabla en `claude-code-delegation.md`):
   - architect: Read-only (no Edit/Write).
   - test-writer-read: bloquea `src/**` y `lib/**`.
   - test-writer-write: bloquea fuera de `tests/**`.
   - implementer: bloquea `tests/**`.
   - reviewer: Read-only (no Edit/Write).
   - scribe: Read-only (no Edit/Write).
5. **End-to-end**: mini-feature (3-4 postcondiciones) corrida vía `Agent` tool, 5 etapas, artefactos producidos.
6. **Resultado**: `findings/validation-cdad-002.md` documentando fricciones, timeouts, bloqueos reales vs. esperados.

**Criterio de aceptación**: 5/5 etapas PASS (igual que `cdad-001`, 5/5 stages + artefactos).

## Próximos Pasos

1. Implementar Fase 1-5 (agentes, guard script, modelo mapping, install.sh, skill updates).
2. Validación spike `cdad-002`.
3. Documentar en `findings/validation-cdad-002.md` fricciones reales descubiertas.
4. Fase 6 (futuro): extender `install.sh` para preguntar perfil de instalación (OpenCode-only, Claude Code-only, both).

---

## Referencias

- `cdad/agents/claude-code/cdad-*.md` (5 agentes nuevos)
- `cdad/scripts/claude-code-path-guard.sh` (guard script)
- `cdad/scripts/cdad-models.sh` — extensión con `cdad_model_claude`
- `cdad/skills/cdad-cycle/SKILL.md` — §4 y §"Compatibilidad multi-entorno"
- `cdad/skills/cdad-cycle/references/claude-code-delegation.md` (nuevo)
- `cdad/skills/cdad-cycle/references/sub-agent-strategies.md` — corrección Claude Code
- `findings/validation-cdad-002.md` (spike result, futuro)
