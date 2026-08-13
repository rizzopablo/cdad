# Sub-agent strategies — cómo materializar sesiones aisladas según entorno

CDAD requiere que test-writer, implementer, reviewer, refactorer y scribe corran en sesiones que **no compartan contexto**. Cómo se materializa esto depende del entorno.

## Por qué importa

Si un mismo agente escribe el test y la implementación en la misma sesión, va a alinear ambos: ajusta el código para que el test pase, o mentalmente ajusta el test para lo que su código va a satisfacer. La separación garantiza que el test sea oráculo independiente.

## Estrategia por entorno

### OpenCode

**Soporte nativo completo**. Los agentes CDAD viven versionados en el repo en `agents/` (formato OpenCode, runtime de referencia) y se instalan a `~/.config/opencode/agents/` vía `install.sh` — el repo es la fuente única de verdad y la copia instalada se regenera desde ahí, no se edita a mano. Definición de ejemplo de un sub-agente:

```yaml
---
description: Test-writer estricto en CDAD. Solo escribe tests.
mode: subagent
permission:
  edit:
    "*": deny
    "tests/**": allow
  read:
    "src/**": deny       # NO ve código de implementación
    "docs/specs/**": allow
    "docs/systemPatterns.md": allow
---
Sos un test-writer en CDAD. Escribís un test que verifica una postcondición específica del spec...
```

Sub-agentes mínimos a crear (uno por archivo):

- `architect` — read-only, descubrimiento y brainstorm.
- `test-writer` — edit en `tests/`, NO ve `src/` ni código de implementación.
- `implementer` — edit en código de implementación, NO en tests.
- `refactorer` — edit en código, NO en tests; suite debe seguir verde.
- `reviewer` — read-only, modelo distinto al implementer si es posible.
- `scribe` — read-only, drafta Memory Bank update.

Modelo distinto por sub-agente con clave `model: provider/model-id`.

Invocación: `@nombre-agente` o desde un comando slash con `subtask: true`.

### Claude Code

**Soporte nativo via sub-agents** (desde ADR-008, 2026-08-13). Definilos en `.claude/agents/<name>.md` con frontmatter Claude Code (NO OpenCode — las sintaxis son diferentes).

**Diferencias clave con OpenCode:**
- Claude Code frontmatter NO tiene `permission` con globs (ej: `edit: {"tests/**": deny}`). En cambio, usa `tools:` como allowlist plano (nombres de herramientas: `Read`, `Grep`, `Edit`, `Write`, `Bash`, `Skill`, etc.).
- Path-scoping se reconstruye vía `hooks.PreToolUse` que corre un script guard (`~/.claude/cdad-scripts/path-guard.sh <rol>`) antes de cada `Edit`/`Write`/`Read`/`Grep`.
- Modelo: `model:` acepta alias (`haiku`, `sonnet`, `opus`, `fable`) o model ID completo — no hay gateway `mofgw`.

Invocación desde el orquestador con la herramienta `Agent` (equivalente a OpenCode's `task`/`delegate`). La sub-sesión NO ve el contexto del agente padre.

**Detalle completo:** ver `references/claude-code-delegation.md`.

### Zed

**Soporte parcial via Agent Panel**. Zed tiene Agent Panel que permite múltiples threads y perfiles. La estrategia:

1. Crear **perfiles** (Profile) en Zed con instrucciones específicas para cada rol CDAD.
2. Para cada fase, abrir un **thread nuevo** con el perfil correspondiente.
3. Pasar manualmente solo el contexto relevante (spec + interface para test-writer; spec + test para implementer; etc.).

Zed no enforza permisos por glob como OpenCode/Claude Code, así que la disciplina es del operador (vos como orquestador): le das al implementer solo los archivos que tiene que ver.

Si Zed evolucionó y ya soporta permisos granulares cuando leas esto, usá la versión nativa.

### Cualquier LLM en chat (fallback single-session)

Si el entorno no soporta sub-agentes (chat web común, terminal pura), **simulás aislamiento con disciplina explícita**:

#### Opción 1 — Conversaciones separadas

El usuario abre una nueva conversación para cada fase. Cada conversación arranca con:

> *"Sos `<rol>` en CDAD. Tu única tarea es `<tarea>`. Te paso el contexto necesario y nada más:*
>
> *<contexto pegado por el usuario, curado>"*

Esto es lo más cercano al ideal sin sub-agentes nativos. La fricción es real (cambiar de chat) pero la calidad lo justifica.

#### Opción 2 — Modos en una sola conversación (último recurso)

Si el usuario insiste en single-session, declarás cambios de modo explícitos:

> *"Cambio a modo **test-writer**. Para esta fase, NO voy a mirar código de implementación; solo trabajo con el spec y la interface. Si me preguntás sobre el código, te recuerdo que estoy en este modo."*

> *"Cambio a modo **implementer**. Ahora veo el test y la interface. NO voy a modificar el test."*

Esto es **menos efectivo** que sesiones reales aisladas porque el LLM mantiene memoria del contexto previo, pero al menos formaliza la separación. La fricción del cambio de modo señala al usuario que estamos en una excepción.

Avisale al usuario:

> *"Estamos en single-session por entorno. Es el modo de menor garantía de aislamiento. Si en algún momento podés migrar a un entorno con sub-agentes (OpenCode, Claude Code), el rendimiento del proceso mejora notablemente."*

## Cuál estrategia recomendar

| Entorno | Estrategia recomendada |
|---------|------------------------|
| OpenCode | Sub-agentes nativos `.opencode/agent/*.md` |
| Claude Code | Sub-agents nativos en `.claude/agents/` |
| Zed | Threads con perfiles |
| ChatGPT, Claude.ai chat, etc. | Conversaciones separadas (opción 1) |
| Forced single-session | Modos explícitos (opción 2), con warning |

## Cómo arrancar cada sesión aislada

Plantilla genérica del prompt inicial para una sesión aislada:

```
Sos un sub-agente <rol> en CDAD. 

Tu tarea es: <tarea específica de esta fase>

Reglas estrictas:
- <regla 1: ej. NO mires el código de implementación>
- <regla 2: ej. solo editás archivos en tests/>
- <regla 3>

Contexto que recibís:
1. Spec aprobado: <contenido o ruta>
2. Interface: <contenido o ruta>
3. <otros artefactos según rol>

Output esperado: <qué entregás al cerrar la sesión>
```

Adaptá las reglas y el contexto según el rol. Las reglas son negociables solo si el spec del proyecto autoriza una excepción específica.

## Permisos por rol — cheatsheet

| Rol | Edit | Read | Notas |
|-----|------|------|-------|
| architect | nada (plan-only) | todo | descubrimiento + brainstorm |
| test-writer | `tests/**` | spec, interface, systemPatterns | NO `src/**` |
| implementer | código de implementación | spec, tests, interface | NO `tests/**` |
| refactorer | código de implementación | suite completa | NO `tests/**`, suite verde siempre |
| reviewer | nada | todo | idealmente modelo distinto al implementer |
| scribe | nada | spec, diff, review, Memory Bank | drafta updates de Memory Bank |

Si el entorno enforza estos permisos por glob, perfecto. Si no, vos como orquestador respetás estos roles al dirigir cada fase.
