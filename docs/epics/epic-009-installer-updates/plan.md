# Plan — epic-009-installer-updates

Épica **light** (decisión del dueño, 2026-10-28): una sola feature, sin fases de descubrimiento
multi-feature. Existe porque el estado de CDAD no admite features huérfanas (`validate-state` exige que
`active_feature` pertenezca a `epic_features`), no porque haga falta ceremonia de épica.

## Objetivo

> Instalar una actualización de CDAD no debe costarle al usuario la configuración que ya hizo: hoy un
> `model:` por agente deja el archivo en conflicto, lo congela en la versión vieja y hace fallar
> `--check`; el remedio operativo (borrar y reinstalar) borra el modelo.

## Features

| Feature | Promesa | Plan |
|---|---|---|
| `009-001-installer-agent-overlay` | Las claves de usuario del frontmatter (`model:`) sobreviven a la actualización, el resto del agente se actualiza, el archivo sigue owned y `--check` pasa | `docs/specs/009-001-installer-agent-overlay/plan.md` |

## Criterios de aceptación del epic

1. La feature cierra con su `closure.md` y evidencia de PC-1..PC-7.
2. `make validate` sin fallos y `./install.sh --check` PASS.
3. Ningún texto instalable (repo/staging/generado) fija un modelo: INV-3 (006-003) intacto.
4. Sin mecanismos duplicados: una sola definición de «clave de usuario», consumida por install, `--check` y
   el validador.
5. Sin push: la publicación sigue reservada al dueño.

## Alcance

Entra: el overlay de claves de usuario en las copias instaladas de agentes (`.config/opencode/agents/` y
`.claude/agents/`), el mensaje de `--check` que hoy nombra la ruta de staging, y el re-scope del validador.
No entra: elegir modelos, preservar personalizaciones libres (siguen siendo conflicto D4), ni tocar
`opencode.json`.

## Autoridad

HITL delegada por el dueño al orquestador para esta épica (spec, gates, review y Memory Bank con evidencia);
severidad de defectos sin relajar; publicación reservada al dueño. Fuente: instrucción del dueño del
2026-10-28 en la sesión de orquestación («ciclo CDAD light»).
