# Revisión del borrador 017-001

**Dictamen:** recomiendo corregir los bloqueantes antes de presentar el borrador para aprobación. La decisión corresponde al dueño; esta revisión no aprueba la spec ni autoriza su implementación.

Objeto principal: `docs/specs/017-001-suite-performance/spec.md`, SHA256 `1cff418c36c6392645c5d66b524104681198a021f8d57caab5445b61ad9de273`. También revisé `plan.md`, con el límite de identidad indicado abajo.

## Hallazgos

### 1. La línea base no garantiza medir las operaciones necesarias para elegir la optimización

**Severidad:** BLOCKING · **Verdict: BLOCKING** · **Bucket: m**

**Ubicación:** `spec.md:164-167,250-259,313-315`; `plan.md:37-44,54-60,73-74`.

El perfil admite una lista de operaciones, pero la calibración anterior a la base exige comprobar nodeids, fases, XML y tiempo exterior, sin exigir que se hayan instrumentado y calibrado operaciones concretas de preparación dentro de `call`. El plan sitúa la medición de preparación interna, copias y generación en la tarea de optimización, **después** de capturar la única base autorizada.

Esto es material porque el discovery identifica precisamente preparación mezclada dentro de `call` como hipótesis aún no medida (`discovery.md:69-75`). Una base con fases completas pero `operations` vacío podría satisfacer formalmente parte de la instrumentación sin aportar el dato necesario para elegir una optimización por costo observado. Una medición posterior no reconstruye retroactivamente esos intervalos en la base.

**Corrección y cierre verificable:** antes de la base, identificar las operaciones candidatas y su mecanismo de observación; calibrar al menos los recorridos relevantes que puedan medirse sin alterar las transiciones, o declarar expresamente cuáles permanecerán desconocidos y cómo se decidirá sin ellos. La condición de entrada a la base debe comprobar que el perfil contiene y atribuye correctamente los intervalos comprometidos en una selección focal conocida.

### 2. El plan no deja una primera tarea despachable con validación definida

**Severidad:** BLOCKING · **Verdict: BLOCKING** · **Bucket: m**

**Ubicación:** `plan.md:14-29,31-46`; regla aplicable: `skills/cdad-cycle/references/stage-2-specification.md:143-167`.

Las tareas no tienen el marcador `detail`, por lo que se revisan como tareas inmediatas. La primera pide una auditoría de doce postcondiciones, helpers, consumidores, copias, selecciones y fronteras de medición; enumera evidencia genérica, pero no define comprobaciones observables concretas ni la regresión y el gate de integración de esa unidad. La segunda agrupa instrumentación, compatibilidad, preservación del runner, calibración y gate bajo un único RED/GREEN genérico.

El riesgo no es la ausencia de un formato por sí misma: el siguiente despacho no tiene una frontera verificable que permita saber qué resultado recibe su consumidor ni rechazar una parte sin arrastrar el resto. Tampoco queda determinado cómo cerrar la auditoría antes de gastar la corrida base.

**Corrección y cierre verificable:** delimitar la siguiente unidad con resultado consumible, responsable y comprobaciones concretas —incluidos regresión y gate cuando correspondan—; dividir la instrumentación si sus resultados pueden rechazarse independientemente. Las tareas posteriores cuyo detalle dependa de la base pueden quedar explícitamente planificadas, con incertidumbre, responsable y condición de resolución.

### 3. La revisión conjunta no fija la identidad del plan en el contrato recibido

**Severidad:** BLOCKING · **Verdict: BLOCKING** · **Bucket: m**

**Ubicación:** `.cdad/packets/017-001-suite-performance-reviewer-plan-review-001/REQUEST.json:10-17,27-30`; `skills/cdad-cycle/references/stage-2-specification.md:52-55`.

El encargo solicita revisar spec y plan, pero el contrato fija por SHA256 únicamente la spec; el plan figura como input sin digest. Calculé el hash del plan que efectivamente leí: `fe082bcd6ec7e01cd9b48bc5da77118fbe1cc6bc9201e8026c1b4b091e41416a`. Eso identifica mi lectura, pero no demuestra que sean los bytes que el despacho quiso someter a revisión.

La consecuencia es que el resultado conjunto no queda ligado de forma verificable a ambas piezas que se presentarían juntas para aprobación.

**Corrección y cierre verificable:** el orquestador debe fijar la identidad de ambos documentos mediante el mecanismo contractual aplicable y obtener una revisión que nombre esos dos digests. No hace falta repetir la revisión completa si el mecanismo permite una comprobación focal de identidad y de cualquier cambio introducido.

### 4. ADR aceptado ausente del índice de decisiones vigentes

**Severidad:** OPTIONAL · **Verdict: OPTIONAL** · **Bucket: m**

**Ubicación:** `docs/systemPatterns.md:5-40`; `docs/adr/ADR-040-especializacion-documental-por-contrato-casa-unica-y-dos-registros.md:3-8`.

El ADR-040 declara estado **Accepted** y alcanza al reviewer, pero no aparece en la tabla de decisiones vigentes. No observé que esta omisión haya alterado el contenido del borrador revisado: el contrato recibido ya remite a la norma documental. Sin embargo, el índice queda incompleto para futuros despachos.

**Corrección propuesta:** reconciliar el índice con el estado del ADR mediante el responsable de mantenimiento; comprobar que la fila apunta al archivo existente y declara los roles pertinentes.

## Límites y evidencia

- Ruta C validada: `validate-request` y `validate-packet` terminaron sin errores; el render de identificación coincidió con el recibido y el contexto declara `schema_version: 2`.
- Revisé la spec, el plan, el plan del epic, discovery, decisiones del dueño, política de CI, mantenimiento de suite, el runner y los tests y helpers citados. No ejecuté tests ni suite completa: se trata de una revisión de borrador, no de evidencia de rendimiento.
- Comandos de control principales: `python3 scripts/cdad_packet.py validate-request`, `validate-packet` y `render --route C` con las rutas del paquete; `sha256sum` sobre spec y plan; `git rev-parse HEAD`; `git status --short`; `git diff --name-only`; inspección de `docs/adr/`.
- `HEAD` observado: `041988bae05219c507c5c2d00835669d672dac53`. El estado mostraba `docs/.cdad-state.json` modificado antes de mi intervención.
- **Archivos modificados por esta revisión:** ninguno. **Commit creado:** ninguno.

## Abstentions

- No puedo determinar todavía si la preparación será el costo dominante, si el objetivo futuro será alcanzable ni si el paralelismo será útil o seguro: faltan las mediciones y la decisión posterior del dueño.
- El plan leído queda identificado por el hash calculado arriba, pero su identidad no estaba fijada en el contrato de despacho; el hallazgo 3 limita la acreditación de la revisión conjunta.
