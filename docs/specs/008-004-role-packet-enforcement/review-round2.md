## Dictamen (2a ronda): BLOCKING

Los tres escapes del review anterior cierran por lectura. El intake compartido, sin embargo, no exige las comprobaciones completas del contrato antes de trabajar: PC-03, PC-04 y PC-08 quedan parcialmente sin acreditar.

### 1. BLOCKING — Ruta A acepta metadatos validos sin exigir igualdad del paquete completo
- Ubicacion: `sources/roles/architect.md:19-27`; copias generadas (p. ej. `agents/cdad-reviewer.md`, bloque "Validated packet path").
- Evidencia: con marcador, cierre y metadatos validos el intake manda seguir el paquete; no instruye resolver/validar el `REQUEST.json`, generar el render canonico ni comparar TODOS los bytes recibidos desde el marcador hasta el final, como exige `spec.md:65-80` y `:159-164`. El verificador de disco (`cdad_packet.py:1961-1978`) no acredita los bytes recibidos por una sesion nativa (`spec.md:44-47`).
- Consecuencia: un prompt con encabezado valido y objetivo/instrucciones alterados satisface el intake textual.
- Cierre verificable: instruir la validacion del request y la comparacion integra del paquete recibido con su render canonico antes de trabajar; regenerar y comprobar por lectura.

### 2. BLOCKING — Ruta C no vincula la identidad recibida ni delimita su lectura de control-plane
- Ubicacion: `sources/roles/architect.md:28-30`; `spec.md:82-97` y `:166-172`.
- Evidencia: el intake no exige comparar los metadatos del bloque recibido con los del paquete validado, ni declara que las lecturas minimas de control-plane no amplian el scope de producto.
- Cierre verificable: exigir un unico bloque de identificacion, comparar sus metadatos con el request y paquete validados, y limitar la excepcion de lectura al control-plane necesario.

### Comprobaciones
- PC-02 texto: preambulo transparente y no autorizante (`sources/roles/architect.md:16-18`).
- PC-08 seleccion textual: las 20 copias tienen "at any position" y "Route C"; ninguna conserva "first line" (script de inspeccion: `first-line=False`, `route-C=True`, `marker-any=True`). No cierra PC-08 en su totalidad por las omisiones de A y C.
- Tres bloqueantes previos: `cdad_delegate.py:574-602` admite antes de leer bytes; `cdad_dispatch.py:1073-1103` antes de observar/staging; `cdad_continuity.py:1235-1251` rechaza request ausente con rastro de publicacion y conserva legacy sin rastro. Pruebas durables en `tests/test_008_004_packet_enforcement.py:590-760`.
- PC-05 lectura parcial: `capabilities`/`migrate` con ramas separadas (`cdad_dispatch.py:1324-1340`).

### Limites
No ejecute tests ni la suite; no acredite la distribucion instalada; no verifique empiricamente todas las operaciones legacy.
