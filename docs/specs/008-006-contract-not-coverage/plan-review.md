# Revisión del borrador 008-006

**Contrato revisado:** `docs/specs/008-006-contract-not-coverage/spec.md`, SHA-256 `be0e64e359d253248dbd2826e81981eef231a39676ed19ee5e1ee0d93544f188`. Es un borrador pendiente de aprobación; esta revisión no lo aprueba.

## Hallazgos

### 1. BLOCKING — La especificación deja una cuota contradictoria en el generador

**Verdict: BLOCKING · Bucket: h**

La PC-6 exige que los agentes generados reciban la doctrina coherente (`spec.md:82-85`), pero el generador incorpora otro fragmento editable que exige literalmente “one test per numbered postcondition” (`scripts/cdad-generate.py:523-531`). La especificación identifica siete hogares y exige eliminar esa cuota de la **tabla compuesta**, pero no identifica ni exige alinear este fragmento RED.

**Consecuencia:** se pueden actualizar las fuentes de roles y la tabla, ejecutar `make agents` y seguir distribuyendo al test-writer instrucciones incompatibles: un test por promesa y uno por postcondición. Las comprobaciones limitadas a la tabla no detectarían el conflicto.

**Cierre verificable:** incluir el fragmento del generador entre los consumidores que deben alinearse o sustituirse por un puntero al hogar canónico; comprobar en los agentes de ambos runtimes que no conserva la cuota contradictoria.

### 2. IMPORTANT — “Un test por promesa” se formula como techo pese a las promociones

**Verdict: BLOCKING · Bucket: m**

PC-2 y R2 dicen “un test por promesa” (`spec.md:43-48,98`), mientras R4 permite promover tests adicionales por seguridad, integridad o regresiones costosas (`spec.md:54-58,100`). R7 exige verificar cada promesa (`spec.md:73-78`), pero no aclara si esa fórmula es una cuota máxima, una unidad ordinaria de selección o cómo convive con varios comportamientos observables distintos y las promociones.

**Consecuencia:** un lector puede rechazar un test necesario porque ya existe uno para esa promesa, aunque proteja una falla observable diferente. El contrapeso impide diferir garantías en términos generales, pero deja instrucciones operativas en tensión.

**Cierre verificable:** precisar en R2 y sus consumidores que no se multiplican tests para resultados equivalentes, sin prohibir los necesarios para verificar comportamientos comprometidos distintos ni los promovidos por R4. Mantener trazabilidad y motivo por test.

### 3. IMPORTANT — El diferimiento obligatorio no cubre claramente lo que se decide no probar

**Verdict: BLOCKING · Bucket: m**

La directiva del owner, cláusula 5, requiere registrar **lo que se decide no probar en esta unidad**. La spec obliga a que exista la sección (`spec.md:34-37,97`) y a trasladar sus disposiciones al cierre (`:67-69,102`), pero no exige que la selección y el gate registren allí cada diferimiento y su motivo. La sección de la propia spec enumera categorías (`:135-142`), no establece esa obligación operativa para features futuras.

**Consecuencia:** una feature puede tener `deferred-hardening: None` y descartar escenarios sin dejar constancia, cumpliendo formalmente la existencia de la sección y vaciando la garantía de transparencia de la directiva.

**Cierre verificable:** asignar explícitamente a la selección/gate el registro de lo decidido no probar y su motivo, con `None` únicamente cuando no haya diferimientos; conservar el traslado al closure.

## Comprobaciones y límites

- **PC-1 a PC-5:** son instrucciones documentales revisables por lectura. Los tests estáticos pueden comprobar marcadores y formulaciones identificadas, pero no demostrar por sí solos que una consecuencia sea verdadera o suficiente; el límite declarado en `spec.md:110-121` lo reconoce.
- **PC-6:** `Makefile:10-18` genera y promueve ambos runtimes sin instalar agentes en destinos reales. La comprobación de ausencia de `model:` es verificable; no ejecuté la regeneración por el alcance de solo lectura. El hallazgo 1 impide considerar suficiente la composición prevista.
- **Tabla de decisiones y ADR:** no completé la comparación sistemática de `docs/systemPatterns.md` con `docs/adr/`.
- No ejecuté tests ni generación; tampoco verifiqué independientemente una ejecución previa del autor.

## Abstenciones

- Me abstengo de dictaminar la conformidad completa con las decisiones vigentes y ADR, por no haber terminado su contraste sistemático.
- Me abstengo de afirmar que la suite focal pasa o falla: no fue ejecutada.

## Evidencia de ejecución

- **Archivos modificados por este rol:** ninguno. `git status --short` mostró únicamente `M docs/.cdad-state.json`, preexistente y no atribuido a esta revisión.
- **HEAD observado:** `84b8324d88557b81886f51abe0e051bc2667b274`.
- **Commit creado:** ninguno.
- **Comandos:** `sha256sum` y `nl -ba` sobre la spec; `git status --short`; `git rev-parse HEAD`; búsquedas `rg` acotadas a roles, generador, tests, discovery y epic; lectura de la directiva y discovery con `cat`; inspección de líneas del generador y Makefile con `nl -ba ... | sed -n ...`; listado de ADR con `ls docs/adr`. Los resultados relevantes se citan en los hallazgos.
