# RED correctivo 2 — 003-001-role-packets

Fecha: 2026-09-17  
Rol: test-writer RED independiente  
Branch: `codex/epic-003-context-efficiency`  
Base exacta observada: `6cd2f303093c7cf2bbe6d24bc8f5562801232478`

## Alcance y aislamiento

- Se leyeron el handoff, `cdad-cycle/SKILL.md`, su contrato de rol, el spec aprobado, `post-audit-2.md`, los tres tests focales y las fuentes públicas bajo `skills/cdad-cycle/packets/`.
- No se leyó implementación bajo `skills/cdad-cycle/scripts/` ni schemas bajo `assets/`.
- Sólo se modificaron `tests/test_role_packets.py` y `tests/test_role_packet_render.py`.
- `tests/test_role_packet_consumers.py` quedó intacto. No se modificaron docs, state, skills, assets, consumidores, instalación ni git; no hubo commit.

## Tests agregados o reforzados

### PA-1 / P1-P3

- Para las 13 parejas rol/subfase, el test lee las tres fuentes públicas esperadas en orden: `common.md`, rol y subfase.
- Recalcula SHA-256 sobre los bytes exactos y compara la lista completa `instruction_sources`, incluidos orden y digests.
- Construye el bloque esperado mediante concatenación de los bytes crudos con un LF separador y lo compara byte a byte con el bloque estático delimitado.
- Comprueba exclusiones cruzadas representativas para `test-writer/red` e `implementer/green`, tanto de otro rol como de otra subfase.

### PA-5 / P5

- Matriz de `active_packet`: cuatro status válidos, ausencia individual de cada campo, enums/valores inválidos, versión, kind, hash y pareja `reviewer/green` inválida.
- Matriz de mismatch entre `active_packet` y request: id, rol, subfase, contract kind y contract hash.
- Rechazo de `ended_at` RFC3339 válido anterior a `started_at`.
- Aceptación de `prepared`, `dispatched`, `completed` y `failed`.

## Evidencia de ejecución

La suite focal integrada se ejecutó exactamente una vez:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_role_packets \
  tests.test_role_packet_render \
  tests.test_role_packet_consumers

Ran 25 tests in 115.785s
FAILED (failures=14)
```

Esa corrida confirmó un fallo de producto y expuso una normalización incorrecta del oráculo nuevo: el test quitaba los LF terminales de las fuentes antes de concatenarlas. Se corrigió el test para concatenar los bytes públicos crudos. Sin repetir la suite integrada, se verificó únicamente ese método corregido:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_role_packet_render.TestPublicTask2Surface.test_p1_p3_each_pair_matches_public_instruction_sources_byte_for_byte

Ran 1 test in 4.479s
OK
```

Con la corrección del oráculo, los 13 subfallos PA-1 quedan resueltos por evidencia focal. El RED contractual restante es único:

```text
FAIL: test_p5_active_packet_validates_every_field_enum_and_role_substage_pair
      (invalid_pair='reviewer/green')
AssertionError: 0 == 0 : invalid state binding was accepted
```

El fallo es una assertion por comportamiento faltante: `validate-state` acepta una pareja rol/subfase no autorizada. No hubo errores de importación, sintaxis, interfaz ni entorno.

## No regresión

- PA-2, PA-3, PA-4 y PA-6 permanecieron verdes en la corrida integrada.
- Los nuevos casos de fields/enums/mismatches, orden temporal y cuatro outcomes pasaron; sólo falló la pareja inválida.
- Cero `skip`, `skipTest` y `BLOCKED` en los tres archivos focales.
- `git diff --check` pasó.

## Resultado

RED válido para GREEN: implementar en `validate-state` el rechazo de parejas `active_packet.role` / `active_packet.substage` fuera de la matriz autorizada. No se requiere cambiar tests.
