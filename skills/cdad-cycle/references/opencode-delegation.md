# OpenCode delegation — materializar sesiones aisladas con sub-agentes nativos

Cuando el entorno es OpenCode y existen sub-agentes `cdad-*` instalados
(`~/.config/opencode/agents/cdad-*.md`, instalados via `install.sh` del repo),
el orquestador puede delegar el rol vía la herramienta `task` con
`subagent_type: cdad-<rol>` en lugar de entregar un handoff packet al usuario.

## Regla de decisión

1. ¿El entorno expone sub-agentes `cdad-*` como `subagent_type` disponibles en `task`?
   - SÍ → delegá via Task (flujo de abajo).
   - NO / dudás → handoff packet (portable a cualquier runtime).
2. ¿El rol es de Etapa 3 con sub-fases (AUDIT / RED / properties / E2E)?
   - Cada invocación Task es UNA tarea atómica (una postcondición, un test,
     un diff). NO agrupes sub-fases en una sola invocación, salvo que el spec
     marque postcondiciones ortogonales explícitas.

## Mapeo rol → subagent_type

| Rol CDAD | subagent_type | Modelo (mofgw) | Etapa |
|----------|---------------|-------------------|-------|
| architect | `cdad-architect` | deepseek-v4-pro | 1, 2 |
| test-writer (AUDIT/RED/properties/E2E) | `cdad-test-writer` | glm-5.2 | 3 |
| implementer (GREEN, refactor sub-modo) | `cdad-implementer` | deepseek-v4-flash | 3 |
| reviewer | `cdad-reviewer` | qwen3.7-plus | 4 |
| scribe | `cdad-scribe` | deepseek-v4-pro | 5 |

El `subagent_type` es el rol. El modelo lo define la config del sub-agente
(no se pasa como argumento). Reviewer usa familia distinta al implementer
(regla CDAD no-negociable contra confirmation bias).

La tabla muestra el perfil **optimus** (diseño del repo). El deploy puede usar
otro perfil (`install.sh --economical|--premium`, ver `scripts/cdad-models.sh`
y ADR-007): verificá el perfil activo antes de asumir el modelo de la tabla
(marker `~/.config/opencode/agents/.cdad-models-profile`). La regla
reviewer-familia-distinta se mantiene en los 3 perfiles.

## Mecanismo de state passing

Los sub-agentes Task reciben contexto FRESCO (no ven el contexto del
orquestador). Por eso:

1. El orquestador construye el prompt del Task con el contenido del handoff
   packet: tarea atómica, contexto relevante (spec inline o ruta, interface,
   reglas estrictas del rol, output esperado).
2. El sub-agente además LEE por sí mismo `docs/.cdad-state.json` (para
   `tdd_substage` y estado) y `docs/specs/<feature-id>/` según el rol.
3. El orquestador NO asume que el sub-agente recuerda nada de la sesión
   anterior. Todo el contexto necesario va en el prompt del Task.

## ⚠️ task vs delegate — clasificación por permisos del plugin

opencode distingue DOS herramientas de delegación, pero la clasificación
**NO la decide el rol CDAD**: la decide el **PLUGIN**, a partir de los
permisos del bloque `permission:` anidado del frontmatter del sub-agente:

- El sub-agente es **task-able (write-capable)** cuando AL MENOS UNO de los
  permisos `edit`, `write` o `bash` del bloque `permission:` anidado NO es
  catch-all deny (ej. la palanca `write: ask` de cdad-010: `write` no es
  deny, así que el agente no colapsa a read-only).
- El sub-agente es **read-only** solo si `edit`, `write` y `bash` del bloque
  anidado son TODOS catch-all deny.

| Herramienta | Para sub-agentes | Detalle |
|-------------|------------------|---------|
| `task` | task-ables (plugin: al menos un permiso anidado no-deny) | El sub-agente puede mutar archivos y devuelve resultado síncrono |
| `delegate` | read-only puros (los tres anidados catch-all deny) | Ejecución ASYNC en background; el orquestador debe esperar el evento de completado |

**Con la palanca `write: ask` (cdad-010, 2026-09-12), los 10 sub-agentes
`cdad-*` son task-ables → TODO el routing CDAD en OpenCode va por `task`.**

### `delegate` — fallback NO-VIABLE en este deploy

**`delegate` es fallback no-viable en este deploy (canal muerto):** el
`session.prompt` que el plugin usa para inyectar la tarea NO pasa modelo, el
sub-agente delegado cae al default global (sin crédito) y muere con timeout
y 0 mensajes. Evidencia: findings `delegation-timeouts-2026-09-08` del
workspace. NO usar `delegate` para routing CDAD.

**Referencia histórica del canal (cuando estuvo vivo) — riesgo
MessageAbortedError.** El riesgo real del delegate nunca fue la pérdida de
persistencia: el output async SÍ se persiste completo en disco
(`~/.local/share/opencode/delegations/<hash>/<session>/<id>.md`); la causa de
una review truncada era que el sub-agente delegado **cerraba el turno sobre
una tool_call sin emitir el texto final** (verificado 2026-08-24: truncado
salió del loop en step 4 tras la última leída vs. completos con 6+ steps). El
runtime entonces marcaba el mensaje `MessageAbortedError` y solo persistía el
trace (step-start + reasoning), no el informe. La **regla de cierre** que lo
mitigaba — nunca cerrar sobre una tool_call, siempre volcar el texto final en
el mismo turno tras la última herramienta — sigue siendo buena práctica de
prompt para cualquier rol read-only, hoy vía `task`.

Nota histórica sobre scoped write: cualquier `deny` en edit/write/bash (aunque
sea scoped a un path) hace que opencode colapse el agente a "read-only" y
fuerce `delegate` (verificado NO-FUNCIONAL como mecanismo para habilitar
`task` en opencode 1.18.18, 2026-08-24). Desde cdad-010 la palanca es
`write: ask`: no es deny, no colapsa a read-only, y no genera prompts (el
runtime no evalúa `write`; detalle y vigilancia en `docs/systemPatterns.md`).

## Fallback ante rate limit (429)

Si el Task falla con error de rate limit (429) o provisión:

1. Reintentá 1 vez con backoff corto.
2. Si persiste, SURFACE al usuario: decile qué rol quedó bloqueado y por qué.
3. Ofrecé re-invocar el mismo Task apuntando el modelo del sub-agente a la
   vía el gateway local (proxy router) aceptando el trade-off de determinismo
   (rotación de modelos), o esperar a que el límite se resetee.

## Cuándo Task vs handoff packet

| Criterio | Task (OpenCode) | Handoff packet |
|----------|-----------------|----------------|
| Aislamiento de sesión | Sí (sub-agente fresco) | Sí (chat nuevo) |
| Modelo distinto por rol | Sí (config por agente) | Manual (el usuario elige chat/modelo) |
| Automatización | Total (sin copiar/pegar) | Manual |
| Portabilidad | Solo OpenCode | Cualquier runtime |
| Overhead de contexto | Bajo (prompt acotado) | Alto (pegado manual) |
| Fallback | Gateway local (proxy router) | Ninguno necesario |

Preferencia: Task cuando el entorno lo soporta; handoff packet como fallback
universal. El skill sigue siendo portable.
