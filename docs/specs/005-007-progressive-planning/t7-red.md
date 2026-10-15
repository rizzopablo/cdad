# RED de T7 — 005-007-progressive-planning (test-writer, substage `red`)

**Packet:** `005-007-progressive-planning-test-writer-red-009` · **Contrato:** `docs/specs/005-007-progressive-planning/spec.md` (sha256 `54877103…`) · **Postcondiciones:** PD-3, PD-4, PD-13 (+ PD-12 estructural) · **Ficha:** T7 del plan (sha256 `1f636260…`).

## Qué se escribió

`tests/test_005_007_t7_unit_size_and_retries.py` (nuevo, 356 líneas) — test estructural caja-negra, convención de la feature (helpers de `test_005_007_t1_progressive_detail_rule.py`: `_load`/`_lines`/`_near`/`_sections`). Los archivos de producto (`stage-2-specification.md`, `re-entry.md`) se leen **al ejecutar**, no por el test-writer: **no leí implementación** (ninguna lectura de `skills/`, `scripts/`, `sources/`, `agents/`). Oráculos derivados solo de la spec aprobada y la ficha T7; aserciones de presencia por familias de tokens (rotulos variables), nunca prosa completa.

Un caso por postcondición:

| Caso | Postcondición | Oráculo (derivado del contrato) |
|---|---|---|
| CASE 1 | PD-3 | La sección de tamaño de unidad de `stage-2-specification.md` declara las 4 condiciones cualitativas del criterio por costo total — (a) reviewer no podría rechazarla sin rechazar su vecina; (b) cierra su propio resultado verificable con su consumidor nombrado; (c) costos fijos (planeación + apertura de sesión + revisión independiente + integración) superan el avance marginal; (d) no mueve la feature hacia un resultado verificable (fragmentación) — referencia el criterio de «costo de coordinación» (`planning-contract-draft.md:155`) y **no** declara umbrales numéricos (`%`, mínimos, `≥ N`, conteos de tareas/archivos/líneas). |
| CASE 2 | PD-4 | `re-entry.md` declara el disparador a nivel de unidad: reintento **sin información nueva** sobre una unidad → **revisión de estrategia** → **replanteo de la unidad** (tamaño/frontera/detalle), con el número de intentos como **señal, no criterio**. |
| CASE 3 | PD-12 | La sección de tamaño de `stage-2-specification.md` **referencia** la regla de reintentos / su hogar (`re-entry.md`) y **no** re-enuncia el conteo (guard: ninguna segunda declaración de «dos intentos»/conteo en esa sección). |
| CASE 4 | PD-13 | La cláusula de replanteo declara la trazabilidad: conserva **objetivo, dependencias y razones** (no borra/reescribe) y **no reescribe un contrato despachado sin reconciliación declarada**. |

## Comando ejecutado (RED focal, segundos — no la suite)

```
python3 -m pytest tests/test_005_007_t7_unit_size_and_retries.py -v
```

## Resultado: 4 failed, 0 passed (exit 1), en 0.09s — todos `AssertionError`

| Caso | Falla hoy en | Salida (causa de la aserción) |
|---|---|---|
| CASE 1 (PD-3) | `:228` | `AssertionError: PD-3: la regla de tamaño de unidad no declara el criterio por costo total como condiciones verificables: falta al menos una de las cuatro condiciones cualitativas en toda sección de tamaño — (a)…(d). Secciones candidatas examinadas: 2.` — hoy la regla de tamaño no es por costo total (VERIFY 4 sin resolver según el contrato). |
| CASE 2 (PD-4) | `:280` | `AssertionError: PD-4: la cláusula de replanteo no declara el disparador completo: reintento SIN información nueva sobre una unidad -> revisión de estrategia -> replanteo de la unidad (tamaño/frontera/detalle), con el número de intentos como señal y NO como criterio.` — consistente con el contrato: la revisión de estrategia genérica ya existe en re-entry.md, falta el **vínculo a nivel de unidad**. |
| CASE 3 (PD-12) | `:301` | `AssertionError: PD-12: la sección de tamaño de unidad de stage-2-specification.md no REFERENCIA la regla de reintentos ni su hogar (re-entry.md); el vínculo se consume por referencia, no como segunda regla.` — el guard de segunda declaración del conteo es preventivo (pasa hoy; protege después del GREEN). |
| CASE 4 (PD-13) | `:336` | `AssertionError: PD-13: la cláusula de replanteo no declara la trazabilidad: replantear una unidad conserva el OBJETIVO, las DEPENDENCIAS y las RAZONES (no borra ni reescribe el rastro de la unidad).` |

Ningún `ImportError`/`SyntaxError`/`NameError` ni error de fixture en el estado final (un `re.PatternError` transitorio durante la edición — `(?i)` a mitad de patrón en Python 3.13 — se corrigió antes del RED válido; el RED registrado es el de arriba). Nada de skip.

## Evidencia

- **Archivos modificados:** `tests/test_005_007_t7_unit_size_and_retries.py` (nuevo). Nada fuera de `tests/`.
- **Nota de alcance:** `docs/.cdad-state.json` aparece modificado en el worktree por el seguimiento del ciclo (no fue tocado por esta tarea; fuera del write scope del rol — se deja intacto).
- **Commit:** `4462a9a9711ac0d8719d192213ade56ecb828257` — `test: 005-007 T7 RED — tamaño de unidad por costo total (PD-3) y vinculo reintentos↔unidad (PD-4/PD-12/PD-13)` — rama `codex/epic-005-real-operation`, 1 archivo, +356.
- **Suite completa:** no corrida (política de suite: la corre una vez quien cierra).
