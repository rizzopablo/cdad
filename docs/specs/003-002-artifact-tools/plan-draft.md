---
feature_id: 003-002-artifact-tools
created_at: 2026-09-17
status: draft
---

# Plan — 003-002 Artifact tools

## Restricciones globales

- Depender sólo de validadores públicos estables de 001.
- Python 3 stdlib; implementación instalable junto al helper de 001.
- Store operacional `.cdad/runtime`, gitignored.
- UTF-8 no vacío, máximo agregado 1 MiB por packet.
- Una finalización por execution/packet.
- Receipt mecánico, estado y aprobación semántica separados.
- Fixtures offline; sin fetch OpenCode/Codex.

## Tarea 1 — Receive atómico e idempotente

**Postcondiciones:** P1, P2 y base de P3/P6.

**Archivos**

- Create: `skills/cdad-cycle/scripts/cdad_result.py`.
- Create: wrapper fino `scripts/cdad_result.py`.
- Create: schemas result/bundle/receipt bajo assets de la skill.
- Modify: `.gitignore` para `.cdad/runtime` y temporales operacionales.
- Test: fixtures staged-file, bundle y concurrencia.

**Consume**

```text
execution context validado por 001
packet validado por 001
RESULT.json
staged UTF-8 parts
manifest observado opcional
```

**Produce**

```text
receive -> immutable bundle + receipt
validate-receipt -> status/diagnostic
```

**TDD**

1. RED: bytes/digests, 1 MiB, UTF-8, identidad, status dispatched y scope.
2. GREEN: write/fsync/rename mínimo y receipt inmutable.
3. RED/GREEN: retry, interrupción y dos procesos; identidad igual converge,
   contenido distinto conflictúa.

## Tarea 2 — Materialización por política de artefactos

**Dependencia:** Tarea 1 verde.

**Postcondiciones:** P3, P4 y parte de P6.

**Archivos**

- Modify: helper/schema de 002.
- Create: schema de autorización y tabla cerrada artifact kind/target.
- Test: fixtures architect bundle, audit, reviewer y scribe.

**Consume**

```text
receipt durable válido
MATERIALIZE.json
authority binding vigente
artifact policy
```

**Produce**

```text
materialize -> copia exacta o conflicto
```

**TDD**

1. RED: target permitido/prohibido, receipt/authority mismatch, traversal,
   target igual y target divergente.
2. GREEN: temp + rename exacto, sin approval effect ni state mutation.
3. Verificar que read-only target policy no amplía source write scope.

## Tarea 3 — Evidencia Python unittest

**Dependencias:** identidad y receipt de Tarea 1.

**Postcondición:** P5.

**Archivos**

- Modify: helper/schema de 002.
- Test: mini proyectos unittest offline con resultados green/red/empty/stale.

**Consume**

```text
RUN.json
python3 -m unittest argv
source/test/contract snapshots
```

**Produce**

```text
run-python-unittest -> log + immutable evidence
validate-run-evidence -> valid-current | invalid | stale
```

**TDD**

1. RED: argv no permitido, exit no cero, cero tests, snapshot cambiado y digest
   desconocido.
2. GREEN: ejecución sin shell, conteo > 0, captura exacta y comparación de
   equivalencia.
3. No añadir otro runner ni cache genérica.

## Tarea 4 — Integración con re-entry e instalación

**Dependencias:** Tareas 1-3 verdes.

**Postcondiciones:** integración P1-P6.

**Archivos**

- Modify: `skills/cdad-cycle/references/re-entry.md`.
- Modify: instrucciones de salida/materialización aplicables.
- Modify: instalación/README para entrypoint y store.
- Modify: state schema sólo con referencia de receipt/status; payload fuera del
  state.
- Test: recorrido offline receive → root reconciliation → materialize.

**Consume**

```text
receipt mecánico
validaciones específicas del rol
decisión/autoridad del orquestador
```

**Produce**

```text
flujo que recibe antes de validar semánticamente
root aplica state transition una sola vez
materialización desde stored original
installed CLI smoke
```

**TDD**

1. RED: retry con state ya reconciliado no repite efecto.
2. GREEN: referencia pequeña en state y re-entry desde original durable.
3. Suite P1-P6 y smoke instalado desde proyecto consumidor.

## Integración final

1. Ejecutar fixtures offline de recepción simple y architect bundle.
2. Ejecutar matriz interruption/concurrency/conflict.
3. Ejecutar artifact policy completa y verificar bytes/digests.
4. Ejecutar unittest green, red, empty, stale y unknown.
5. Ejecutar recorrido receive/retry/reconcile/materialize sin doble efecto.
6. Ejecutar suites estables de 001 y checks del repo aplicables.
7. Confirmar store gitignored y ausencia de cambios en instalación real.
8. Exigir cero skips/bloqueados para el gate de 002.

## Auto-revisión

- Tarea 1 → P1/P2/P3/P6.
- Tarea 2 → P3/P4/P6.
- Tarea 3 → P5.
- Tarea 4 → integración P1-P6.
- No hay task sin postcondición ni postcondición sin task.
- No se incluye fetch SDK, workflow engine, cache general ni continuidad.

---

Status: Pending approval together with spec.md
