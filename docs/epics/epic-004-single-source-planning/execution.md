# Registro de autoridad — ejecución de epic-004-single-source-planning

Fecha: 2026-09-24. Este documento es la **fuente de la delegación HITL de
epic 004** referenciada por `docs/.cdad-state.json` (`hitl_delegation.source`).

## Alcance de la autoridad

Ejecutar el epic `epic-004-single-source-planning` (tres features:
`004-001-canonical-runtime-artifacts`, `004-002-project-execution-bootstrap`,
`004-003-planning-procedures`) bajo la metodología CDAD con la política de
[ADR-011](../../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md)
(autonomía supervisada y límites proporcionales), conforme al
[handoff de continuación](../../handoffs/2026-09-23-glm-continuation.md),
la [enmienda C0 vigente](c0-amendment-supervised-autonomy-2026-09-24.md) y la
spec aprobada de
[004-001](../../specs/004-001-canonical-runtime-artifacts/spec.md).

| Campo | Valor |
|---|---|
| delegated_to | GLM (orquestador y construcción del epic 004) |
| requested_by | usuario (Pablo) |
| requested_at | 2026-09-24 |
| scope | epic-004-single-source-planning: alcance del epic, specs, decisiones dentro de contratos aprobados, priorización de reviews, aprobaciones de Memory Bank y gates para sus tres features e integración |
| expires | cierre, cancelación o revocación del epic |
| publication | sin push automático |
| decisores de análisis/review | GPT o Claude, en sesión distinta del autor/implementer; un dictamen técnico no concede por sí solo autoridad de aprobación |

## Cadena de autoridad (evidencia)

1. **Elección de GLM para desarrollo** (GPT/Claude análisis/review): decisión
   del usuario documentada en el handoff de continuación (§4), re-confirmada
   en las revisiones C0 de GPT y Claude ("esa selección no necesita otra
   confirmación").
2. **Política de autonomía supervisada (ADR-011)**: aceptada por instrucción
   del usuario (2026-09-24).
3. **Dictamen C0 conforme con corrección**: revisión focal de Claude
   (2026-09-24) sobre el delta + spec/plan de 004-001; corrección requerida y
   tres observaciones resueltas por el architect en
   [correction-004-001-architect-2026-09-24.md](correction-004-001-architect-2026-09-24.md)
   (base del dictamen: `21238de`).
4. **Aprobación de la spec 004-001 con postcondiciones**: registrada en la
   marca de aprobación de
   [spec.md](../../specs/004-001-canonical-runtime-artifacts/spec.md) —
   instrucción del usuario en sesión ("Adelante, toma en cuenta estas
   observaciones de claude y continúa") tras conocer la conclusión del
   dictamen ("listo para que Pablo apruebe y se active 004 según §6").
5. **Procedimiento de activación**: §6 del informe del architect
   (corrección-004-001-architect-2026-09-24.md), con snapshot de suspensión de
   epic 003 y un único write del state.

## Límites expresos

- No hereda la delegación HITL de Codex/epic-003 (se archiva con estado
  `suspended`, no se borra).
- No concede autoridad de publicación (sin push automático) ni permisos
  adicionales sobre código fuera del alcance del epic.
- La aprobación estratégica residual (nuevos alcances no previstos, cambios de
  frontera de epic, cierre del epic) sigue siendo del usuario.

## Enmienda 2026-09-29/30 — orquestación por Claude (decisión del usuario)

La orquestación de epic 004 pasa a **Claude** (sesión de Claude Code), con
construcción delegada a los roles CDAD. Instrucciones del usuario en sesión:
- 2026-09-29, "Tal vez vos mismo podrías orquestar pero delegarle... a
  opencode+glm como subagentes";
- "continúa orquestando los agentes opencode con mofgw/glm-5.3-flash (puedes
  usar mofgw/deepseek-v4.1-flash...)";
- "Adelante, continúa orquestando los subagentes y tomando las mejores
  decisiones como dueño del proceso y hitl hasta completar un desarrollo
  excelente".

| Campo | Valor vigente |
|---|---|
| delegated_to | Claude (orquestador del epic 004, dueño del proceso con criterio HITL) |
| construcción | test-writer e implementer en OpenCode con modelos económicos (glm-5.3-flash, deepseek-v4.1-flash) |
| review y architect | gpt-6-astra vía Codex; suplente: subagentes Claude Opus si Codex se queda sin crédito (2026-09-30) |
| se conserva | scope, expires, publication y límites expresos de la delegación original |

Las decisiones de aprobación estratégica residual siguen siendo del usuario;
en 004-002 las tomó en sesión (D1–D6, aprobación de la spec con C1–C2).

## Enmienda 2026-10-01 — selección de modelos por crédito (decisión del usuario)

El usuario adjuntó el ADR "Arnés multi-modelo para los roles CDAD" (de otro
proyecto; en este repo el número ADR-007 ya está ocupado) y decidió usar su
selección "porque si no nos quedamos sin tokens demasiado rápido". Vigente
desde 2026-10-01 para epic 004:

| Rol | Runtime y modelo |
|---|---|
| architect, implementer, scribe | OpenCode `--standalone --auto`, `mofgw/deepseek-v4.1-flash` |
| test-writer, reviewer de rutina | OpenCode `--standalone --auto`, `mofgw/glm-5.3-flash` |
| segunda mirada (solo riesgo alto) | Codex `exec -s read-only < /dev/null`; sin crédito, subagente Claude Opus |

- Solo variantes flash.
- Implementer y reviewer de familias distintas (DeepSeek frente a GLM).
- El orquestador valida cada spec contra el código, porque architect e
  implementer comparten familia.
- Se audita `--no-verify` en los commits de los roles con escritura.
- Para 004-002, que toca la integridad del estado (lock y publicación
  transaccional), la segunda mirada se reserva para el cierre de la
  feature, en una sola pasada.
- Limitación declarada: test-writer y reviewer comparten familia (GLM).
