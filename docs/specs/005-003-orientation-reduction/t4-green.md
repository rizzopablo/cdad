GREEN de T4 completado.

## 1. Archivo creado y diff resumido

**Creado:** `skills/cdad-cycle/references/capabilities.md` (nuevo, 114 líneas). Único archivo del commit.

Estructura del documento (`capabilities-inventory-v1`):
- **§1 Cuatro clases + criterio** — tabla `observed` / `documented` / `not available` / `unknown` con el **criterio** que asigna cada clase (evidencia disponible ahora, nunca expectativa).
- **§2 Capacidades para planes, archivos, previews y diffs** — agrupadas por clase: observadas (archivos por ruta/enlace, diff por la herramienta de control de versiones, plan como archivo, preview por archivo/enlace), documentadas (disposición de versión y superficies del CLI por referencia; subcomandos de OpenChamber por su propio help), no disponibles (dashboard/scheduler/segunda fuente de estado; preview dedicada), desconocidas (contrato estable agente↔superficie de OpenChamber).
- **§3 Ligado a versión/configuración por referencia** — un párrafo que nombra a la vez versión y configuración; cita `orientation.md` §4; declara sin valores de este VPS.
- **§4 Fallback portable + cadena** — `agent → artifact → review` por archivos o enlaces; OpenChamber como **consumidor verificado** de su instalación y mecanismo de acceso, con su contrato estable agente↔superficie **NO verificado** (desconocido, propuesta posterior, no comprometido).
- **§5 Fronteras** — inventario, no manual; no redefine arranque; no promete el contrato agente↔superficie; no crea dashboard/scheduler/fuente de estado.

## 2. Comandos y salidas

RED (antes): `python3 -m pytest tests/test_005_003_t4_capabilities_inventory.py -q` → **6 failed** (por `AssertionError` de contrato, documento ausente).

GREEN (focal T4):
```
$ python3 -m pytest tests/test_005_003_t4_capabilities_inventory.py -q
......                                                                   [100%]
6 passed in 0.04s
```

Regresión proporcional (focales T1/T2/T3):
```
$ python3 -m pytest tests/test_005_003_t1_compact_view.py tests/test_005_003_t2_examples_execute.py tests/test_005_003_t3_set_summary.py -q
..............................                                           [100%]
30 passed in 9.88s
```

`git show --stat HEAD`:
```
 skills/cdad-cycle/references/capabilities.md | 114 +++++++++++++++++++++++++++
 1 file changed, 114 insertions(+)
```

## 3. Hash del commit

`b6e567b80c1ca532511765a309a0d518e668a6b7` — `feat(005-003): T4 - inventario de capacidades efectivas y fallback portable`

## 4. Desviaciones declaradas

- Ninguna sobre el contrato. `tests/**` intacto (nunca editado).
- `docs/.cdad-state.json` aparece modificado en el árbol de trabajo, pero es la preparación del paquete GREEN que hizo el orquestador (`active_packet` → implementer-green); está **fuera de mi write scope** y **no lo commiteé** (el commit contiene solo mi producto).
- Suite completa **no** corrida (según el encargo). Sin push, sin despliegue, sin tocar HOME.