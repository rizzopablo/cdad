# ADR-038: La admisión de una encomienda ocurre en cada frontera invocable y compara bytes con el render canónico

- **Status**: Proposed (pendiente de ratificación del dueño; epic-008, `008-004-role-packet-enforcement`).
- **Date**: 2026-10-28
- **Confidence**: **Alta** (25 tests que discriminan contra el código previo, cuatro rondas de review,
  distribución instalada verificada).
- **Origen**: `docs/specs/008-004-role-packet-enforcement/spec.md` (D1–D3, PC-01..PC-08) y su `closure.md`.

## Contexto

Una encomienda CDAD se despacha a una sesión de rol y se acredita después con su registro. El paquete que la
identifica se publica en disco y viaja al rol como texto. El hueco medido: una encomienda podía despacharse
por la vía nativa —o por una CLI invocada directamente— y **acreditarse sin que nadie hubiera comparado el
`PACKET.md` publicado con el render canónico de su request**.

Tres hechos concretos, no hipótesis: (i) el runtime antepone una línea a todo prompt de subagente y el intake
exigía el marcador en la primera línea; (ii) la review reprodujo que un encabezado válido con objetivo
alterado pasaba la comprobación textual; (iii) la review reprodujo que `cdad_delegate` lanzaba un worker con
el paquete alterado **después** de un `begin` válido, porque la única comprobación vivía en `dispatch`.

## Decisión

1. **Cada frontera invocable verifica su propia precondición antes de producir efectos**: `begin`,
   `prepare --record-dispatch`, `cdad_dispatch dispatch` y `record`, y `cdad_delegate` — antes de publicar
   continuidad, observar el modelo, preparar staging, transmitir bytes o cambiar estado.
2. **Un solo criterio de integridad y un solo verificador**: el del productor, importado (ADR-036); la
   frontera no reimplementa ni acepta un subconjunto del paquete.
3. **La identidad la da el marcador canónico**, identificado **exactamente una vez en cualquier posición**.
   El preámbulo es **transparente y no autoriza** nada.
4. **La ruta principal compara bytes completos**: todo lo recibido desde el marcador hasta el final contra el
   **render canónico completo**, sin normalizar. Objetivo, instrucciones, contrato, entradas, scopes,
   invariantes y evidencia son parte de la comparación.
5. **La ruta de respaldo (identificación sin cuerpo)** exige un bloque único cuyos metadatos coincidan con el
   paquete validado, y su lectura mínima de control-plane **no amplía el scope de producto**.
6. **Cero marcadores es consulta legacy sin acreditación CDAD; toda anomalía rechaza** —más de uno, bloque sin
   cierre, identidad discordante, ausencia de paquete— **sin fallback silencioso**.
7. **`begin` rechaza una referencia `contract` cubierta por el `write_scope` del propio paquete**, que por
   diseño produciría P1 en el `record`.

## Alternativas rechazadas

- **Confiar en el preflight del orquestador.** Es obligatorio y no suficiente: un consumidor programático o
  una CLI invocada directamente lo saltan.
- **Exigirle al runtime que suprima el preámbulo.** Depende de un tercero y de una versión.
- **Validar sólo el encabezado o un hash del archivo.** El encabezado válido con objetivo alterado pasó; y
  validar el archivo en disco no acredita los bytes que recibió una sesión nativa.
- **Un segundo verificador en las fronteras.** Dos definiciones de la misma identidad, condenadas a divergir
  (ADR-036).
- **Reclasificar automáticamente una referencia `living` como `contract`.** Cambiaría la semántica declarada
  por el escritor (ADR-018) para tapar un error de encargo.

## Consecuencias

**Positivas.** Una encomienda sin paquete verificable no produce efectos en ninguna frontera administrada; el
rechazo nombra la ruta y la causa. La identidad no depende de las palabras del objetivo ni del nombre del rol.
El rechazo temprano de PC-06 evitó registros condenados por diseño.

**Negativas / límites.** La garantía es de **admisión, no de intercepción**: no impide que un agente ignore
sus instrucciones ni media herramientas nativas. Validar el paquete en disco **no** acredita los bytes
recibidos por una sesión nativa. Hay doble comprobación en el camino normal. La regla vive en la fuente del
rol y en 20 copias generadas: hay que verificar que ninguna conserve la condición vieja.

## Cumplimiento

`tests/test_008_004_packet_enforcement.py` — **25 casos** que discriminan contra el código previo, más 664
regresiones focales de continuidad, despacho, recepción y paquetes; `003-004`/`003-007` intactos.
Distribución: `./install.sh --check` **PASS (414 grupos)**, 11 agentes por runtime con el intake corregido y
sin `model:`; `make validate` **68/68**.
