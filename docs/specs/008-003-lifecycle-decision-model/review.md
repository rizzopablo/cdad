## Dictamen: BLOCKING

### 1. La escritura programática de continuidad omite la guarda compartida

**Required — Verdict: BLOCKING — Bucket: h**
`skills/cdad-cycle/scripts/cdad_continuity.py:1012-1027, 2951-3005`

`plan_write()` carga el contexto y llama directamente a `_plan_write()`. La comparación de identidad y propietario con el estado y el registro de suspensiones está en `_require_unit_operable()`, pero esa función se invoca desde `main()`, no desde `plan_write()`.

Por tanto, una llamada programática puede planificar una escritura para una unidad suspendida o con propietario contradictorio sin pasar por la guarda que sí aplica el CLI. La spec incluye expresamente los bordes invocables directamente (PC-01, PC-02 y PC-06).

**Cierre verificable:** aplicar la resolución y guarda compartidas en el borde programático, sin duplicarlas, y demostrar con llamadas directas que las contradicciones y la suspensión se rechazan antes de producir un plan publicable.

### 2. La elegibilidad se comprueba antes de reconocer replays acreditados

**Required — Verdict: BLOCKING — Bucket: h**
`skills/cdad-cycle/scripts/cdad_continuity.py:1035-1037, 1062-1098, 2999-3005`
`skills/cdad-cycle/scripts/cdad_result.py:635-650`

En continuidad, `_require_current_authority()` precede a la búsqueda del enlace publicado; además, el CLI comprueba suspensión antes de entrar en la operación. En recepción, la suspensión se comprueba antes de buscar el recibo durable. Así, una repetición íntegramente acreditada puede rechazarse por autoridad revocada o suspensión posterior, aunque no requiera ningún efecto nuevo.

Esto contradice el orden obligatorio de §4.4: identidad y evidencia, luego replay/conflicto y, únicamente para efectos nuevos, elegibilidad. El test existente de autoridad revocada verifica `checkpoint-receipt`, pero no cubre el replay de escritura ni el de recepción bajo suspensión.

**Cierre verificable:** reconocer primero el replay íntegro en cada dominio; comprobar después autoridad y suspensión sólo si resta un efecto nuevo. Añadir guardas que repitan escritura y recepción acreditadas tras revocación o suspensión, verificando éxito y ausencia de cambios.

### 3. El núcleo no es dueño de las decisiones migradas de replay y conflicto

**Required — Verdict: BLOCKING — Bucket: h**
`skills/cdad-cycle/scripts/cdad_lifecycle.py:396-411`
`skills/cdad-cycle/scripts/cdad_continuity.py:1062-1098`
`skills/cdad-cycle/scripts/cdad_packet.py:7735-7786, 7953-7980`
`skills/cdad-cycle/scripts/cdad_result.py:643-650`

`converge()` recibe `replay` ya decidido y un diagnóstico de conflicto ya construido por el consumidor. Continuidad conserva la clasificación local de replay y conflicto; packet conserva ramas propias para el replay de cierre y transición; result conserva su rama propia de recibo durable sin llamar al decisor. No es sólo adaptación de hechos físicos: los consumidores siguen determinando el resultado de política.

La spec prohíbe precisamente una fachada que devuelva la decisión a los consumidores y exige retirar las ramas migradas (PC-06). Esto también limita la evidencia para declarar un único criterio de elegibilidad.

**Cierre verificable:** mover al núcleo las decisiones migradas sobre hechos ya verificados —conservando separados sus dominios— y entregar el inventario antes/después con trazabilidad de cada rama y borde, incluidos los programáticos.

## Deuda

- **SUSP-IDENTITY:** la evidencia de este cambio **no alcanza para cerrarla**: PC-06 y la cobertura del borde programático siguen pendientes.
- **SUSP-GUARD:** tampoco alcanza para declarar el cierre parcial previsto: la guarda no se aplica en el borde programático señalado. El límite de evidencia eliminada seguiría abierto incluso tras corregirlo.
- **SUSP-LOCK y SUSP-APPROVAL:** permanecen abiertas, conforme a §6 de la spec.

## Evidencia de revisión

- Los cinco tests de `tests/test_008_003_lifecycle_decisions.py` ejercen CLIs y observan rechazos, artefactos, replay y rutas; no son meras autodeclaraciones. No cubren los escapes indicados arriba.
- Comando ejecutado: `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_008_003_lifecycle_decisions.py` → **`5 passed in 39.68s`**.
- No ejecuté la suite completa: el paquete la reserva para quien cierre la tarea. No verifiqué independientemente el resultado histórico de 1778 pasados y un fallo.
- Revisé `06ab12f` y `cb2dc98`; el SHA-256 de la spec coincide con el paquete: `3c2aa400fe7e1cec52b7412ef4c7c546bca09f61e1571cedc6eafbfd3df52031`.
- El núcleo inspeccionado no realiza I/O ni consulta el reloj, y no importa consumidores.
- **Archivos modificados por esta revisión:** ninguno. `git status --short` mostraba una modificación preexistente en `docs/.cdad-state.json`; no la alteré.
- **Commit de revisión:** ninguno.

## Abstentions

- No pude acreditar las **15 ramas** una por una: el inventario específico del implementador no figuraba entre los insumos proporcionados. Los hallazgos estructurales anteriores se basan en ramas concretas observadas.
- No concluyo la ausencia de regresiones en todas las variantes de `resume_unit` y clasificación de retiro: no ejecuté una verificación exhaustiva de esas ramas.
- No completo la comparación entre la tabla de decisiones actuales y todos los ADR aplicables; queda pendiente para el cierre.
