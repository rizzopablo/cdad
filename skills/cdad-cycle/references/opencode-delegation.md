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

## ⚠️ task vs delegate — distinción por permisos del sub-agente

opencode distingue DOS herramientas de delegación, según los permisos del
sub-agente (verificado 05 Ago 2026, opencode 1.18.4):

| Herramienta | Para sub-agentes | Detalle |
|-------------|------------------|---------|
| `task` | con `write` habilitado (edit/write permitidos) | El sub-agente puede mutar archivos y devuelve resultado síncrono |
| `delegate` | read-only (`write: deny`, `edit: deny`, bash restringido) | Ejecución ASYNC en background; el orquestador debe esperar el evento de completado; el resultado puede venir como texto O como efecto (archivo escrito por el propio orquestador)

**Regla:** Si el rol CDAD es read-only por diseño (reviewer, scribe), NO usar
`task` — opencode lo rechaza con: `Agent 'X' is read-only... Use delegate for
read-only sub-agents. Use task for write-capable sub-agents.`

**Consecuencia para artefactos de roles read-only** (ej: review.md): el
delegate NO puede escribir el artefacto (write deny). Opciones:
a. ~~Scoped write~~ **verificado NO-FUNCIONAL en opencode 1.18.18 (2026-08-24)**:
   cualquier `deny` en edit/write/bash (aunque sea scoped a `docs/specs/<feat>/review.md`)
   hace que opencode colapse el agente a "read-only" y **fuerce `delegate`** igual.
   No habilita `task`. Descartado por evidencia empírica (test de routing con agente
   write-scoped a `log/**`: "Agent is read-only... use delegate").
b. El orquestador materializa el artefacto desde el output del delegate.

**Riesgo real del delegate: abort de turno (MessageAbortedError), no pérdida de
persistencia.** El output async SÍ se persiste completo en disco
(`~/.local/share/opencode/delegations/<hash>/<session>/<id>.md`); la causa de una
review truncada es que el sub-agente delegado **cierra el turno sobre una tool_call
sin emitir el texto final** (verificado 2026-08-24: truncado salió del loop en step 4
tras la última leída vs. completos con 6+ steps). El runtime entonces marca el mensaje
`MessageAbortedError` y solo persiste el trace (step-start + reasoning), no el informe.
Mitigación: el prompt del rol read-only (ej. cdad-reviewer.md "Formato de output") debe
incluir la **regla de cierre** — nunca cerrar sobre una tool_call, siempre volcar el
texto final en el mismo turno tras la última herramienta.

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
