# Review — T3 (004-003): checks mecánicos de plan en `prepare`

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-16>`.
> Paquete: `004-003-planning-procedures-reviewer-review-005`.
> **Dictamen: APPROVED — 0 bloqueantes**, con 2 hallazgos de deuda obligatoria
> antes de T4 (F1, F2) y opcionales/nits F3–F7.

**Contrato:** `spec.md` sha256 verificado `ba395fed…bf766` ✓ · **Diff:** `9f43d65..6257431`.

## Evidencia

- `tests/test_004_003_t3_plan_checks.py` (362 líneas, `9f43d65`) **intactos en el rango** (`git diff 9f43d65..6257431 --name-only`: el implementer no tocó tests ✓).
- `python3 -m unittest tests.test_004_003_t3_plan_checks -v` → `Ran 5 tests — OK`.
- Focal completo re-verificado por el reviewer: `Ran 35 tests in 22.069s — OK` (T1/T2/T3 + packet_prepare).
- 10 sondas adversariales propias vía `run_prepare` sobre fixtures temporales.
- **Suite completa 345 passed / 470 s: evidencia CITADA del implementer, no verificada por el reviewer** (árbol de código idéntico; la corrida del reviewer murió con la sesión — PD-5, declarado en abstenciones).

## Sostenido (verificado)

- **Orden de enforcement correcto:** los checks corren en `cdad_packet.py:2490-2493`, después de leer/hashear el contrato y **antes** de `out_dir`/`packet_id`/`validate_request`/publicación. En todo rechazo `out_dir` queda vacío y el state intacto.
- **Separación estructural/semántica (PD-2, AC-3):** los checks solo miran tokens estructurales (ids, artifacts, versiones, archivos, dependencias). Ninguna regla juzga calidad. **¿Deciden calidad semántica? No.**
- **Una fuente, sin copias competidoras:** `scripts/cdad_packet.py` es un wrapper `runpy` de 11 líneas; la fuente canónica es `skills/cdad-cycle/scripts/cdad_packet.py`.
- **`prepare` sigue siendo el único productor** (invariante 1).
- **Detección de ciclos correcta:** un probe inicial sugirió un "ciclo perdido"; al inspeccionar, el grafo era acíclico (arista hacia un ancestro que no depende del visitado). DFS 3-colores detecta todo ciclo real. No es hallazgo.
- **Decisión de oráculo ACEPTADA con condiciones:** el bloque cercado `plan-tasks` JSON dentro del plan es coherente con §4 del planning contract ("una tabla o sección en el plan existente") y con PD-2 (solo hechos estructurales). La leniencia (sin bloque → no se rechaza en T3) está declarada en oráculo, state y código.

## Hallazgos

- **F1 — Required · bucket m · `cdad_packet.py:2253-2267`.** El docstring declara "Malformed declarations fail loud" y el código no lo cumple: variantes de fence (indentado, sin cierre, con tag, `\r\n`, segundo bloque) caen en el camino "bloque ausente" → **rc=0, publicado, checks saltados**. Dentro del alcance estricto de T3 no rompe la observabilidad (sin bloque es legal), pero es una trampa para T4 (cuando el bloque sea obligatorio, un fence indentado = agujero silencioso). **Remedio:** detectar toda línea ```plan-tasks que no matchee el open canónico y fallar ruidoso; o normalizar antes de matchear.
- **F2 — Required · bucket m · `tests/test_004_003_t3_plan_checks.py:38-41` + `cdad_packet.py:2262-2264`.** El formato del bloque no tiene hogar canónico editable (ni `planning-contract-draft.md` §4, dueño de los campos del plan-file según G5, ni el plan del epic). Además ambos docstrings dicen que exigir el bloque "es postcondición de T4", pero el schema del bloque T3 **omite los campos de G5** (pruebas focales, regresiones, gate de integración, responsable): dos declaraciones de estructura solapadas sin relación escrita. Violación latente de PD-12/invariante 6. **Remedio:** registrar el formato (y su relación con la ficha §4) **una vez** en el dueño canónico y referenciarlo desde código/tests.
- **F3 — Optional/Consider · bucket m · `cdad_packet.py:2296-2312`.** Doble productor del mismo artefacto aceptado (dos tareas producen `contract-a` con versiones distintas → rc=0). §5 exige contratos compatibles y el epic se llama *single-source planning*. Plegar también P6 (produce duplicado dentro de una tarea, last-wins silencioso).
- **F4 — Optional/Consider · bucket m · `cdad_packet.py:2382-2405`.** Paralelismo: declaración unilateral con colisión de archivo → aceptado; tareas mutuamente `parallel` **y** con dependencia entre ellas → aceptado (contradicción estructural). Rechazarlas o declararlas fuera de alcance en el oráculo.
- **F5 — Nit · bucket h · `cdad_packet.py:2374-2375`.** Cadena de 1500 tareas con ciclo → `RecursionError`, rc=1 con traceback en vez de `ERROR:` rc=2. Nada se publica (hold transaccional verificado). **Remedio:** DFS iterativo o `except RecursionError → PolicyError`.
- **F6 — Nit · bucket l · `cdad_packet.py:2329-2331`.** El diagnóstico de entrada sin productor dice "has no producer" también cuando el artifact tiene otro productor declarado (falso en ese caso).
- **F7 — Nit · bucket l · `cdad_packet.py:2329→2332→2350→2382`.** Comentarios numerados fuera de orden; entradas `consume` escaneadas dos veces; `files` no valida tipo/no-vacío de sus entries.
- **F8 — FYI.** `--no-verify` en el commit RED (prohibido por el handoff): repo sin hooks → sin efecto material. No determinable post-hoc para `6257431`.

## Abstenciones

1. Suite completa: citada del implementer, no verificada; focal completo (35/35) sí verificado.
2. `--no-verify` en `6257431`: no determinable post-hoc; sin hooks, sin efecto.
3. Legitimidad del doble productor por artefacto (F3): §5/§6 no lo prohíben explícitamente; preferencia de organización sin consecuencia demostrada no se vuelve bloqueante.
4. Modelos configurados/reportados: observaciones, nunca amplían permisos.

## Dictamen

**APPROVED — 0 bloqueantes.** AC-3 y PD-2 satisfechos; anti-gaming intacto. **Deuda obligatoria antes de T4:** F1 (fail-loud en variantes de fence) y F2 (hogar canónico del formato + des-confusión T3/G5). Opcionales a deuda priorizada: F3, F4. Nits: F5–F7.
