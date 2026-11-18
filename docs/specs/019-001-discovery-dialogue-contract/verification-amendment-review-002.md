# Revisión del borrador de enmienda

**Objeto:** `docs/specs/019-001-discovery-dialogue-contract/verification-amendment-draft-002.md`  
**SHA-256:** `dcf87fc1d3eb21f33c929bc2bb6c7702aefbe8da6b25c35cf20869fa9b4cb305`

**Dictamen:** la propuesta merece un intento acotado, pero **todavía no demuestra una vía ejecutable para un RED conductual válido**. El fallo de un lector frente a instrucciones vigentes puede revelar el problema que motiva el diseño; no demuestra por sí solo que falle el producto documental pendiente. GREEN debe permanecer bloqueado hasta resolver esa relación y acreditar el procedimiento concreto. Esta revisión no aprueba la enmienda ni autoriza implementación.

## Hallazgos

### 1. La comparación cambia el objeto observado sin demostrar todavía que ejercite el producto pendiente

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

El borrador propone aplicar el mismo oráculo a una lectura de las instrucciones actuales y luego a una lectura del diseño (`verification-amendment-draft-002.md:58–84, 100–112`). Reconoce que son objetos distintos, pero deja para una aprobación posterior la definición de las bases y su relación (`:29–33, 110`).

El compromiso aprobado de Promise A exige que **el producto** asigne responsabilidades y describa los cambios de límites necesarios (`spec.md:135–139`). Las instrucciones actuales siguen teniendo poderes efectivos y no son ese producto (`spec.md:11–15, 29`). Por tanto, una respuesta basal que refleje correctamente las instrucciones actuales, pero contradiga la decisión futura D1, no es automáticamente una falla del producto pendiente. Aprobar la comparación por adelantado evita cambiarla oportunistamente; no demuestra por sí mismo su relevancia contractual.

**Consecuencia:** podría etiquetarse como RED una diferencia entre dos regímenes documentales, en vez de una aserción fallida sobre el comportamiento pendiente que GREEN debe satisfacer.

**Cierre verificable:** antes de aceptar ese RED, identificar las dos bases exactas y sus versiones, el objeto común sometido al verificador y una demostración trazable de por qué el fallo basal representa la ausencia o incumplimiento de PC-1/PC-2, sin tratar como defectuosas instrucciones que todavía gobiernan legítimamente. Si no puede demostrarse bajo la norma vigente, mantener el bloqueo y elevar la alternativa metodológica a la autoridad competente.

### 2. El procedimiento ejecutable y la procedencia de las respuestas siguen indeterminados

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

El borrador exige una respuesta real, recuperable y atribuible, un oráculo inalterado y una comparación ejecutable (`:70–74, 84–94, 108–116`). Sin embargo, delega al test-writer la concreción de captura y consumo de la observación (`:90–94`) y no identifica cómo se generará, recuperará y vinculará cada respuesta con sus entradas, ni cómo una ejecución posterior utilizará la nueva observación sin sustituir manualmente el resultado.

Esto no demuestra que la solución sea imposible. Sí impide verificar ahora que exista una ejecución reproducible que distinga una respuesta auténtica de un registro preparado para producir el resultado deseado. Además, el test-writer no debe leer el documento producido para derivar el oráculo; un reviewer independiente sí puede leerlo dentro de un alcance explícito (`documentary-contracts.md:133–146`). La separación propuesta es compatible **en principio**, pero sus handoffs y permisos concretos aún no están especificados.

**Consecuencia:** el proceso podría terminar comprobando un expediente editado o una respuesta no atribuible, en lugar de observar la lectura de la revisión documental identificada; alternativamente, podría requerir que el test-writer acceda al producto y perder independencia.

**Cierre verificable:** obtener del test-writer un procedimiento y verificador concretos, revisados independientemente, que identifiquen: productor y alcance de cada lectura; entradas y versiones; captura íntegra de la respuesta; forma de entrega al test sin alterar caso ni oráculo; comando y salida de la aserción; y tratamiento de respuestas ausentes o ambiguas. Debe demostrarse con evidencia real, sin fabricar respuestas ni exigir una interfaz nueva al producto. Hasta entonces, es una ruta propuesta, no un RED acreditado.

### 3. ADR-040 continúa fuera del índice de decisiones vigentes

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

El borrador identifica y propone tramitar este problema por separado (`:137–149`); no lo resuelve por sí mismo. El índice se declara exhaustivo para las decisiones vigentes (`docs/systemPatterns.md:5–9`) y omite ADR-040, cuyo encabezado declara estado **Accepted** y alcance a los seis roles (`docs/adr/ADR-040-especializacion-documental-por-contrato-casa-unica-y-dos-registros.md:3–9`). Su sección de confianza conserva, además, una frase incompatible con ese estado (`:124–132`).

**Consecuencia:** los paquetes que se apoyan en el índice pueden omitir una decisión documental aplicable, incluida la separación entre verificación y revisión semántica.

**Cierre verificable:** reconciliar mediante la autoridad y mantenimiento correspondientes el índice y la redacción residual del ADR, o registrar una decisión autorizada diferente sobre su estado; luego comprobar la distribución pertinente mediante `current_decisions`. No corresponde declarar el ADR obsoleto por inferencia.

## Abstentions

- No puedo afirmar que el test-writer vaya a poder construir el verificador propuesto bajo las reglas actuales: no existe aún una ejecución concreta que contrastar.
- No puedo acreditar que un fallo frente a las instrucciones actuales constituya RED del producto futuro sin la identificación y justificación de ambas bases.
- No revisé un `operating-design/` ni evalué el cumplimiento final de PC-1–PC-12. Tampoco se observó una sesión real de lectura.

## Evidencia y límites de esta revisión

- **Intake:** Route C; `validate-request` y `validate-packet` terminaron sin salida y con éxito. El render de identificación Route C coincidió con el recibido.
- **Comandos principales:** `python3 ~/.agents/skills/cdad-cycle/scripts/cdad_packet.py validate-request …`, `validate-packet …`, `render … --route C`; `sha256sum docs/specs/019-001-discovery-dialogue-contract/verification-amendment-draft-002.md`; consultas puntuales con `rg` y `sed`; `git status --short`; `git rev-parse HEAD`.
- **Revisión examinada:** `b66439aa06a6d4aae798d63527ce07bba69d324d`.
- **Archivos modificados:** ninguno. **Commit creado:** ninguno.
- **Tests:** no ejecutados; se revisó un borrador, no una implementación ni un verificador existente. Suite completa no realizada.