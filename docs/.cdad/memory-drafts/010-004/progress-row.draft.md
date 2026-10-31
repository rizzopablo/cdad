# Fila propuesta para `docs/progress.md` — 010-004 (BORRADOR, NO APLICADA)

Estado propuesto: **`done`** · Fecha: **2026-10-31** · Sección destino: `## Done` (primera fila,
por encima de `- **010-000-continuity-relative-root**`).

Material del **orquestador**, no del rol (el paquete del scribe no incluía `progress.md`; el
scribe lo dejó constancia en sus Observaciones 1). Requiere aprobación del dueño igual que el
resto del Memory Bank; hasta entonces la unidad sigue `in-progress` en
`docs/.cdad-state.json`. **No se aplicó** a `docs/progress.md`.

Procedencia: derivada de `docs/specs/010-004-packet-dispatch-ergonomics/closure.md`
(§2 suite, §4 tests, §5 incidentes, §7 R1), `review.md` y `review-verification.md`.
Cifras citadas, no re-medidas por el orquestador.

## Fila (contenido aplicable, copiar tal cual)

- **010-004-packet-dispatch-ergonomics** (2026-10-31, epic 010 — **2/5**) — cierre local declarado; a la espera de aprobación del dueño y NO publicado. El encargo dejó de depender de retranscribir su cuerpo (`render --route C` emite solo declaración + identificación de 8 campos, sin instrucciones, objetivo, entradas, scopes ni cuerpo) y el rol dejó de inferir su contexto de ejecución (toda publicación nueva usa v2 y declara `.cdad/executions/<execution_id>/execution.json` en request y cabecera; la vía implícita v1 sin policy quedó cerrada). PC-01..PC-12; review independiente con 4 bloqueantes y reverificación T6 que los declara **B1–B4 cerrados**. Suite completa en un intento: `--all` 1876 nodeids sobre `daace667`, **rc=0**, `1871 passed, 5 skipped in 3668.03s`, `dirty 1`, `canary_delta_lines=0`; los 5 skips son integraciones preexistentes por variables de entorno. Tests del feature: 7 archivos, **22 tests**. `make validate` sigue 182 PASS / 1 FAIL (F011 preexistente y ambiental): la condición es «declarado», no PASS. Cuatro deudas conservadas: D-1/publicación (R1: cerrada en el repositorio, **no vigente en la instalación**; publicar es decisión del dueño), R-A (`--replace-packet`/`--resume-packet` no dan el diagnóstico de PC-07b), I-8 (el test-writer no puede leer sus `instruction_sources`) y R2 (clase I-6 abierta). Sin ADR nuevo. Detalle en `docs/specs/010-004-packet-dispatch-ergonomics/closure.md`.
