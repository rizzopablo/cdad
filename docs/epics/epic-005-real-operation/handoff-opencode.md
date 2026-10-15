# Encargo para el orquestador OpenCode — epic-005

> **Reemplazado** el 2026-10-08 por [handoff-opencode-2.md](handoff-opencode-2.md). Se conserva como historia.

Fecha: 2026-10-08. Rama: `codex/epic-005-real-operation`. Sin push automático.

## Antes de empezar

1. Leé [plan.md](plan.md). Solo avanzás si su estado dice «Aprobado por Pablo»
   y existe [execution.md](execution.md) con la delegación. Si falta alguno,
   detenete e informá.
2. Versión vigente: v7 `ce09ed0` (ver `docs/runtime-adopted-version.md`). Las
   skills y la config ya apuntan a v7. Los agentes de proyecto
   (`.opencode/agents/`) todavía son v6.
3. Una sola versión del CLI por ejecución: usá los scripts de la raíz activada
   (`.cdad/activation.json`). Nunca mezcles v6 y v7 (MIX-V6V7).

## Transición del state

Registrá en `docs/.cdad-state.json`, con la cita de aprobación del plan:
- epic-003 sigue en `epic_history` tal como está; `active_epic` pasa a
  `epic-005-real-operation`, `epic_stage: features-loop`, `epic_features` con
  las cuatro features del plan (005-001 `in-progress`, el resto `queued`).
- `hitl_delegation` con el alcance, vencimiento y fuente de `execution.md`.
- Commit del state y árbol limpio antes de cualquier despacho.

## Primer `prepare` (005-001): publicación de agentes v7

En la misma invocación del primer `prepare`, definí la variable de entorno:

```
CDAD_OPENCODE_AGENTS_DIR="<raíz adoptada>/.config/opencode/agents" python3 scripts/cdad_packet.py prepare ...
```

No asumas que quedó persistida por un comando anterior; un `export` previo no
cuenta. Después:
1. Verificá que `.opencode/agents/.cdad-derived.json` tenga `source_dir` en esa
   raíz v7 y que los agentes publicados coincidan con los hashes del manifiesto.
2. Registrá la verificación en el dispatch-ledger de 005-001.
3. Terminá tu sesión: el dueño abre una sesión nueva del orquestador para que
   cargue los agentes v7. Retomá con `resume` como primer paso.

Repetí la variable en cada `prepare` del epic y verificá `source_dir` cada vez
(criterio 2 del plan).

## 005-001

Ciclo completo de `cdad-cycle`, empezando por el architect (discovery + spec).
Insumos: deuda VALIDATE-IDLE en `docs/specs/003-007-living-continuity/debt.md`
y la causa confirmada por Codex: `validate-state` rechaza `active_feature`
nulo mientras sigue el bloque `execution` de la feature anterior. La spec
decide si el reposo acepta ese bloque o exige archivarlo; el validador debe
seguir rechazando un state incoherente.

## Checkpoints de legado

Si retomás un checkpoint sin `record` (anterior a 003-007), «se pudo leer» no
significa «sigue aprobado»: evaluá los cambios que informa antes de actuar y
después escribí un checkpoint nuevo con clases explícitas.

## Límites

- No instales CDAD en HOME (`~/.claude`, `~/.agents`, `~/.config/opencode`);
  solo raíces aisladas. No actives versiones en el repo real: es del dueño.
- No uses `--no-verify` ni push. No leas `tests/.sensitive-patterns.local`.
- Gates de tests según el plan. La suite completa de cierre se corre en un
  worktree fijado al commit de cierre, en primer plano, esperando `EXIT=`.
- Ante un obstáculo fuera de tu ámbito, entregá el diagnóstico; no alteres
  cambios ajenos ni el estado compartido del repo para esquivarlo.
