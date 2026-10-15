# Tercer POST-AUDIT independiente — 003-001-role-packets

Fecha: 2026-09-17  
Rol: auditor POST-AUDIT final independiente  
Branch auditada: `codex/epic-003-context-efficiency`  
HEAD auditado: `c65bb7a04d077ca2c13b186e16c8d88c3d3a572a`  
Producto auditado: `10b0f9ba13f168094e94e9bcc477b93f7f889e45`  
Modo: sólo lectura del repositorio; no se repitió la suite focal.

## Veredicto

**APROBADO.**

PA-1 y PA-5 están cerrados con tests black-box que verifican el contrato
observable y con implementación coherente. PA-2, PA-3, PA-4 y PA-6 no presentan
regresión. La evidencia canónica del GREEN final registra 25/25 PASS, cero skips
y cero `BLOCKED` (`auditfix2-green.md:28-48`); el commit documental posterior no
cambia producto ni tests.

## PA-1 — cerrado

El oráculo ya no depende de `validate-packet` ni de una segunda invocación del
renderer:

- Para las 13 parejas rol/subfase, el test construye por contrato las rutas
  `common.md`, `roles/<role>.md` y `substages/<role>-<substage>.md`, lee sus bytes
  públicos, recalcula cada SHA-256 y compara la lista completa y ordenada de
  `instruction_sources` (`tests/test_role_packet_render.py:267-290`).
- El mismo test concatena los bytes crudos con un LF separador y compara byte a
  byte el bloque delimitado del paquete (`tests/test_role_packet_render.py:79-83`,
  `291-292`). Esto cubre procedencia, hashes, orden y cuerpo estático exacto.
- Se ejercen exclusiones cruzadas representativas en ambos ejes: para
  `test-writer/red` se excluyen el rol implementer y la subfase properties; para
  `implementer/green` se excluyen el rol test-writer y la subfase refactor
  (`tests/test_role_packet_render.py:296-314`).
- Las restricciones críticas se comprueban para cada paquete mediante semántica
  observable por rol (`tests/test_role_packet_render.py:44-53`, `293-294`).

La implementación observada coincide con el contrato: selecciona exactamente
las tres fuentes, calcula los hashes sobre esos mismos bytes y usa la misma
concatenación para el bloque estático (`skills/cdad-cycle/scripts/cdad_packet.py:376-397`).
El test calcula sus expectativas desde los archivos públicos y no importa ni
invoca helpers internos de producción, por lo que un digest inventado, un orden
distinto o un cuerpo discordante falla independientemente del renderer.

## PA-5 — cerrado

La matriz pendiente quedó completa respecto de los huecos enumerados por el
segundo POST-AUDIT:

- `active_packet=null` sigue aceptado y un objeto incompleto se rechaza
  (`tests/test_role_packets.py:271-279`).
- El snapshot completo ejercita los cuatro estados válidos, ausencia individual
  de cada uno de sus siete campos, valores/enums inválidos, versión, kind, hash y
  la pareja inválida `reviewer/green` (`tests/test_role_packets.py:281-332`).
- La implementación valida la pareja como unidad contra `ROLE_SUBSTAGES`, no como
  dos enums independientes (`skills/cdad-cycle/scripts/cdad_packet.py:40-46`,
  `156-185`). El diff GREEN es una sola sustitución en esa condición.
- `render` rechaza separadamente mismatches de id, rol, subfase, contract kind y
  contract hash entre request y paquete activo (`tests/test_role_packet_render.py:454-472`),
  en correspondencia con el binding de producción (`cdad_packet.py:360-368`).
- Un `ended_at` RFC3339 válido pero anterior a `started_at` se rechaza
  (`tests/test_role_packet_render.py:523-532`); producción parsea ambos offsets y
  compara instantes (`cdad_packet.py:438-442`).
- `prepared`, `dispatched`, `completed` y `failed` se aceptan explícitamente
  (`tests/test_role_packet_render.py:534-544`) y constituyen el conjunto cerrado
  de producción (`cdad_packet.py:33`, `443-444`).

## No regresión de PA-2, PA-3, PA-4 y PA-6

| Hallazgo | Estado | Evidencia |
|---|---|---|
| PA-2 — matriz P4 | Cerrado, sin regresión | La matriz de bindings, autoridad, expiración/revocación, feature done/cancelled/fuera del epic, pares runtime/scope, herencia, excepción inválida antes de `basic` y `basic` ordinario permanece en `tests/test_role_packets.py:207-269`. |
| PA-3 — paridad source/installed | Cerrado, sin regresión | El caso válido exige código 0, paquete real y paridad de bytes/resultados; el inválido exige fallo real, stdout vacío y diagnóstico, en `tests/test_role_packet_consumers.py:70-168`. |
| PA-4 — matriz negativa P2 | Cerrado, sin regresión | Canonicalidad, tampering/hash, traversal, symlink, input fuera de scope, pareja inválida, kind/path, relabel, selectores y test colocado permanecen en `tests/test_role_packet_render.py:318-420`; scopes de rol en `424-451`. |
| PA-6 — bloqueos y portabilidad | Cerrado, sin regresión | Install root aislado, entrypoint instalado, consumo portable, permisos y dependencia Python permanecen en `tests/test_role_packets.py:141-201` y `tests/test_role_packet_consumers.py:61-225`. No hay retornos de éxito `BLOCKED` ni skips ejecutables. |

El commit RED final `56bc846` modifica sólo los dos tests que cerraban PA-1/PA-5,
la evidencia y el state. El commit GREEN `10b0f9b` modifica sólo
`skills/cdad-cycle/scripts/cdad_packet.py`, evidencia y state. Entre RED y HEAD
no hay cambios en `tests/**`; entre producto y HEAD sólo existe el handoff
documental. El cambio de producción está limitado al defecto de pareja
rol/subfase, por lo que no introduce una ruta nueva sobre PA-2/3/4/6.

## Mapeo test ↔ postcondición y calidad de suite

Los 25 métodos focales se distribuyen sin tests ajenos al contrato:

- P1: 5 métodos de parejas, determinismo, límite/boundary, bytes/fuentes y
  exclusiones, más el método property determinista de 100 casos.
- P2: 3 métodos de metadata, alteración/hash y paths/scopes, compartiendo el
  property determinista.
- P3: semántica de las 13 parejas, 2 métodos de scopes y 2 métodos de
  consumidores/permisos.
- P4: 1 método matricial con subcasos positivos y negativos completos.
- P5: 8 métodos para estado, paquete activo, binding y métricas.
- P6: 5 métodos de instalación, consumo, dependencia y confinamiento de la
  instalación de Tarea 1.

El conteo estático es 25 métodos: 3 en `test_role_packets.py`, 17 en
`test_role_packet_render.py` y 5 en `test_role_packet_consumers.py`. Todos usan
CLI, instalador, archivos instalados o superficies documentales públicas. No
hay imports de la implementación canónica, mocks de plumbing, assertions sobre
nombres/orden de helpers internos, tests triviales de constantes privadas ni
casos de cobertura ajenos a P1-P6.

La búsqueda estática no encuentra `skipTest`, `pytest.skip`, decoradores skip ni
ramas que emitan `BLOCKED`. La única aparición textual relacionada es el nombre
histórico `test_p4_p5_state_binding_matrix_or_report_interface_blocked`; su
cuerpo exige que la CLI exista y falla si falta (`tests/test_role_packets.py:207-208`),
por lo que no salta ni bloquea ejecución.

## Independencia TDD y evidencia empírica

- El test-writer documenta sesión RED independiente, lectura limitada a spec,
  auditoría, tests y fuentes públicas, sin leer implementación ni schemas; sólo
  modificó tests (`auditfix2-red.md:8-13`).
- El RED integrado produjo un fallo contractual por assertion para
  `reviewer/green`; tras corregir la normalización del oráculo de bytes se
  verificó focalmente PA-1 y quedó ese único defecto de producto
  (`auditfix2-red.md:31-69`).
- El implementer documenta un único cambio de producción y ninguna edición de
  tests (`auditfix2-green.md:8-17`). El historial y los diffs confirman el orden
  RED `56bc846` → handoff → GREEN `10b0f9b` y scopes de archivos disjuntos.
- El mapeo test↔postcondición de este informe lo realiza una tercera sesión
  distinta de la que escribió tests e implementación.

No existe telemetría mecánica de lecturas de sesiones, limitación ya declarada
por el proyecto. Dentro de la evidencia auditable disponible, la separación
temporal, los artefactos de rol y los diffs sostienen la independencia requerida.

No se repitió la suite: `auditfix2-green.md:28-42` aporta la salida de la corrida
integrada exacta sobre el producto `10b0f9b`:

```text
Ran 25 tests in 109.655s

OK
```

No hay cambio posterior de producto o tests que invalide esa evidencia.

Status: Approved.
