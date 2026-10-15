# Segundo POST-AUDIT independiente — 003-001-role-packets

Fecha: 2026-09-17  
Rol: auditor POST-AUDIT independiente  
Branch auditada: `codex/epic-003-context-efficiency`  
Base exacta: `044d175` (`96972c1` GREEN correctivo + handoff documental)  
Modo: sólo lectura del repositorio; no se repitió la suite focal.

## Veredicto

**CAMBIOS REQUERIDOS.**

La corrección cierra PA-2, PA-3, PA-4 y PA-6, y cierra una parte sustancial de
PA-1 y PA-5. El gate de TDD todavía no puede aprobarse porque persiste el núcleo
de PA-1: la suite no tiene un oráculo independiente que pruebe que los bytes del
bloque estático son exactamente `common + rol + subfase` y que los hashes
publicados corresponden a esas fuentes. PA-5 también conserva huecos de matriz
y una combinación rol/subfase inválida es aceptada por `validate-state`.

La evidencia canónica `auditfix-green.md` registra 20/20, cero skips y cero
`BLOCKED` en 76.830 s. La auditoría usa esa corrida como evidencia empírica y
no la repite, conforme al handoff.

## Hallazgos por severidad

### ALTO — PA-1 persiste: `instruction_sources` todavía no es un oráculo independiente

El contrato exige que cada digest sea el SHA-256 de los bytes exactos de su
archivo, que el orden sea `common.md`, rol y subfase, y que el bloque delimitado
sea la concatenación exacta de esas fuentes con un LF entre ellas
(`spec.md:313-328`). P1 también exige ausencia de instrucciones exclusivas de
otro rol o subfase (`spec.md:572-577`).

El test agregado en `tests/test_role_packet_render.py:257-278` sólo:

- compara los tres nombres de path esperados;
- comprueba que cada supuesto hash tenga 64 caracteres hexadecimales;
- busca una o dos expresiones regulares de restricción por rol en el cuerpo.

No lee las tres fuentes canónicas, no recalcula sus SHA-256, no extrae y compara
el bloque delimitado con sus bytes concatenados, y no comprueba ausencia de
instrucciones exclusivas de otro rol/subfase. Un renderer que publique hashes
inventados con forma válida o que omita/reemplace `common.md` o el delta de
subfase puede satisfacer este test. `validate-packet` tampoco independiza el
oráculo: vuelve a llamar al mismo `render_packet` y compara igualdad con ese
resultado (`skills/cdad-cycle/scripts/cdad_packet.py:497-509`).

La implementación actual parece construir correctamente las tres fuentes y sus
digests (`cdad_packet.py:376-412`), pero el gate CDAD exige que la postcondición
quede verificada por tests de comportamiento. El mismo defecto introducido en
renderer y validator seguiría pasando. Para cerrar PA-1, el test black-box debe
calcular desde los archivos públicos los tres hashes esperados, comparar el
bloque estático byte a byte y ejercer al menos una exclusión cruzada observable
por rol/subfase.

### MEDIO — PA-5 persiste parcialmente: matriz de estado/métrica incompleta

El contrato exige validar todos los campos y enums de `active_packet`
(`spec.md:473-480`) y que un `ended_at` existente no preceda a `started_at`
(`spec.md:564-568`). La suite sólo cubre `active_packet=null`, un objeto
incompleto y el objeto válido usado por los renders
(`tests/test_role_packets.py:258-266`). No prueba status, versión, kind, hash,
rol, subfase ni parejas rol/subfase inválidas, ni los mismatches individuales
de id/rol/subfase/kind/hash contra request.

Hay además un defecto observable por inspección: `_validate_active_packet`
comprueba que `role` pertenezca a `VALID_ROLES` y `substage` a
`VALID_SUBSTAGES`, pero no valida la pareja contra `ROLE_SUBSTAGES`
(`cdad_packet.py:156-185`). Por ello, un snapshot como `role=reviewer` y
`substage=green` es aceptado por `validate-state`, aunque la misma pareja sea
inválida para una request.

En métricas se cubren identidad, tipos numéricos, `null`, modelos distintos,
outcome inválido y strings no RFC3339 (`tests/test_role_packet_render.py:419-464`).
Falta probar un timestamp RFC3339 válido pero anterior al inicio, y la aceptación
de los cuatro outcomes cerrados. La implementación incluye el control temporal,
pero fue agregado sin un RED que lo verifique.

## Estado explícito de PA-1..PA-6

| Hallazgo original | Estado | Evidencia |
|---|---|---|
| PA-1 — composición semántica P1/P3 sin oráculo independiente | **PERSISTE (alto)** | Hay procedencia pública y regex de restricciones, pero no se contrastan hashes ni bytes de las fuentes; tampoco exclusiones cruzadas. |
| PA-2 — matriz P4 incompleta | **CERRADO** | `tests/test_role_packets.py:197-256` cubre pares autorizados/no autorizados, bindings, autoridad ausente, delegación revocada/expirada, feature done/cancelled/fuera del epic, herencia, excepción inválida antes de `basic` y `basic` ordinario. |
| PA-3 — paridad source/installed admitía dos fallos iguales | **CERRADO** | `tests/test_role_packet_consumers.py:70-168` exige source render y source validate en código 0, paquete real no vacío y paridad; también exige fallo real, stdout vacío y diagnóstico en el caso inválido. |
| PA-4 — matriz negativa P2 incompleta | **CERRADO** | `tests/test_role_packet_render.py:299-415` cubre tampering, hash de contrato, traversal, symlink, input fuera de scope, pareja inválida, kind/path, relabel, root amplio, selector archivo/directorio, test colocado y scopes prohibidos. |
| PA-5 — estado/métricas incompletos | **PERSISTE PARCIALMENTE (medio)** | Se ampliaron identidad, modelos, nulls, números, sintaxis RFC3339 y outcome inválido; faltan matriz de `active_packet`, pareja rol/subfase, orden temporal en tests y outcomes válidos completos. |
| PA-6 — guards `BLOCKED` retornaban éxito | **CERRADO** | El commit RED reemplaza retornos por assertions; no hay `skip`, `skipTest` ni `BLOCKED` ejecutable en los tres archivos focales. Evidencia GREEN: 20/20, cero skips/BLOCKED. |

## Mapeo test ↔ postcondición y relevancia

Los 20 métodos focales mapean a postcondiciones del spec:

- P1: matriz de 13 parejas, determinismo, límite/boundary, procedencia/semántica y 100 casos deterministas.
- P2: metadata canónica, tampering/hash, paths/scopes y propiedad de canonicalidad.
- P3: semántica por rol, scopes exactos/prohibidos, permisos instalados y consumidores.
- P4: matriz de estado/autoridad/runtime/scope/basic.
- P5: active packet parcial, identidad/números/null/modelos/timestamps/outcomes parcial.
- P6: install root aislado, entrypoint instalado, paridad source/installed, consumo Task/chat y dependencia Python 3 pública.

No se identifican tests ajenos al contrato. Tampoco se observan tests triviales
que sólo afirmen constantes internas ni mocks sobre plumbing. Los tests usan las
interfaces públicas CLI/installer, salidas, archivos instalados y superficies
documentales públicas. El test de procedencia es relevante, pero insuficiente
como oráculo; el problema es cobertura contractual, no irrelevancia.

## Independencia TDD e historial

- Los tests correctivos entraron primero en `0bc4e4d`; la evidencia RED registra
  20 métodos, 16 fallos y una sesión test-writer nueva que no leyó implementación.
- El handoff al implementer quedó en `ce04804`; el GREEN correctivo es
  `96972c1`.
- `git diff --name-status 96972c1^..96972c1` no contiene `tests/**`. El
  implementer modificó únicamente estado/evidencia, el renderer canónico y los
  dos schemas. **Se confirma que el implementer no modificó tests.**
- El historial de los tres archivos focales contiene sólo commits RED
  (`631b1b3`, `c5c89a1`, `eb7e6ce`, `0bc4e4d`); los GREEN
  (`413cb0d`, `e06089f`, `ddc5f4a`, `96972c1`) no los tocaron.
- La independencia de sesión test-writer/implementer está documentada en
  `auditfix-red.md`, `auditfix-green.md` y el handoff, y es coherente con la
  separación temporal y de archivos del historial. No existe traza mecánica de
  lecturas del test-writer, por lo que esa parte se confirma hasta el límite de
  la evidencia auditable disponible.
- Este segundo mapeo test↔postcondición fue realizado por una sesión auditor
  distinta de la que escribió los tests.

## Ausencia de skips y bloqueos

La búsqueda estática en los tres tests focales no encuentra decoradores de
skip, `skipTest`, `pytest.skip` ni ramas `BLOCKED`. Las menciones restantes de
`BLOCKED` están sólo en documentos históricos/evidencia de RED anterior. La
evidencia canónica del GREEN correctivo registra explícitamente 20/20, cero
skips y cero `BLOCKED`.

## Corrección mínima requerida

1. Fortalecer el test P1/P3 para usar un oráculo independiente: leer las tres
   fuentes públicas esperadas, calcular hashes, comparar orden y digests, y
   comparar byte a byte el bloque estático; agregar exclusiones cruzadas
   representativas de rol y subfase.
2. Completar la matriz P5 de `active_packet`, incluyendo parejas rol/subfase, y
   corregir `_validate_active_packet` para validarlas.
3. Agregar RED de orden temporal (`ended_at` anterior, ambos RFC3339 válidos) y
   aceptación de los cuatro outcomes definidos.
4. Ejecutar la suite focal integrada y registrar salida completa con cero
   skips/BLOCKED. El implementer del fix no debe modificar `tests/**`.

Status: Changes required.
