## Dictamen final (4a ronda) — 008-004

Los dos bloqueantes de la 3a ronda quedan cerrados por lectura. Sin nuevo hallazgo bloqueante dentro del alcance de esta ronda. No constituye aprobacion ni sustituye la suite de cierre.

- Ruta A (`sources/roles/architect.md:20-34`): compara todos los bytes desde el marcador hasta el final del paquete recibido con el render canonico COMPLETO del request validado, sin normalizacion; el limite coincide con `cdad_packet.py:1840-1858` y `:1966-1971`.
- Ruta C (`architect.md:35-43,49-57`): rechazos separados de A; admite cuerpo inline ausente, rechaza el parcial, exige bloque de identificacion, identidad coincidente y validacion completa de REQUEST.json y PACKET.md; conserva el limite de lectura de control-plane.
- Copias generadas: las 10 genericas reproducen el bloque; las 10 Odoo difieren solo en la frase de skills de dominio del generador y el reflujo adyacente.

### Estado de postcondiciones
| PC | Dictamen |
|---|---|
| 01 | Acreditada (codigo + pruebas durables de la 2a ronda) |
| 02 | Acreditada por lectura (preambulo transparente y no autorizante) |
| 03 | Acreditada por lectura del limite corregido y del verificador publicado |
| 04 | Acreditada textualmente; no se verifico una ejecucion nativa real de C |
| 05 | **Excepcion**: compatibilidad legacy/capabilities/migrate revisada parcialmente; regresiones no reejecutadas en esta ronda |
| 06 | Acreditada para los casos y controles de la 2a ronda |
| 07 | Acreditada para replays y preservacion inspeccionados |
| 08 | Acreditada por lectura para fuente y 20 copias. **Excepcion**: no se inspecciono una instalacion soportada nueva |

### Deuda diferible
Fuzzing, carga y matriz de runtimes (ya en spec). Validar el archivo en disco no acredita los bytes recibidos por una sesion nativa (spec 44-47). La suite completa corresponde al cierre.

### Evidencia
Commit revisado `d7cbb1f`; spec sha256 `48c553e7...e6df96`; 10 copias genericas EXACT, 10 Odoo con las diferencias descritas. Sin tests en esta ronda (3a ronda: 13 passed, 14 deselected).
