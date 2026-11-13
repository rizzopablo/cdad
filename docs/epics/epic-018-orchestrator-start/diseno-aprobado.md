# Arranque CDAD directo y verificable

## Steps
- [x] Revisar independientemente y aprobar el diseño, incluida la enmienda de carga inicial.
- [ ] Corregir la entrada y preparación del encargo en las fuentes canónicas y regenerar agentes (T1).
- [ ] Hacer suficientes las ayudas y los diagnósticos de formatos del CLI (T2).
- [ ] Conectar ejemplos ejecutables y captura fiable de evidencia (T3).
- [ ] Revisar, ensayar en una sesión nueva y decidir la adopción voluntaria (T4).

## Borrador del arquitecto

> **Actualización posterior a revisión independiente:** el borrador original de abajo debe leerse junto con las precisiones obligatorias siguientes, que prevalecen donde difieran. Fueron propuestas por el arquitecto y revisadas independientemente; la enmienda específica de ADR-021 continúa pendiente de aprobación y materialización antes de T1.
>
> **Precedencia de entrada:** cuando el proyecto no está reconocido o se desconoce la procedencia efectiva de la skill, se mantienen las cargas y el reconocimiento existentes. En una sesión de orquestador generado, con su contrato presente, proyecto reconocido y procedencia efectiva conocida, se aplica `status` como entrada compacta incluso sin ejecución ni request preparado: esa ausencia, por sí sola, no activa la carga legacy. El legacy real del orquestador queda fuera de esa rama; no se cambian las cargas ni los límites de los roles. Ninguna de estas ramas autoriza abrir unidades ni omitir gates. Antes de T1 se requiere aprobación específica y materialización de la enmienda a ADR-021; no se difiere al cierre.
>
> **Recuperación de paquetes:** `--replace-packet` requiere paquete activo `prepared`, nunca despachado, obsolescencia demostrable del contrato o revisión de política ya admitida, motivo y autoridad vigente. Sin deriva no procede reemplazar; distinguir la retirada legítima de un preparado sin efectos de la reconciliación de un despacho. Verificar positivos y negativos sin efectos no autorizados.
>
> **Caso de aceptación y sensibilidad:** definir un encargo sintético protegido para architect/discovery sobre exportación CSV: objetivo y resultado explícitos; R1 columnas `id`, `fecha_utc`, `total` en UTF-8 y orden dado; R2 UTC y representación decimal del diccionario; R3 excluir nombres y correos; R4 orden estable por fecha e identificador; R5 informar datos inválidos sin descarte silencioso. Incluir exclusiones, fuentes con propósito, alcances y evidencia. El verificador debe aceptar el encargo completo y rechazar la variante que omita R3, con el oráculo intacto, sin autorización ni despacho real. Conservar `PIPESTATUS[0]` como alternativa documentada a la captura completa sin tubería.

**Pendiente de revisión y aprobación.** Este documento propone diseño y plan; no abre una feature, no reactiva autoridad histórica ni autoriza implementación o despliegue.

## 1. Objetivo y diagnóstico

**Objetivo:** que el orquestador llegue al primer encargo legítimo utilizando la orientación compacta y las interfaces existentes, sin reconstruir el CLI ni cargar documentación histórica por defecto.

La mejora no necesita otro sistema de arranque: necesita conectar y hacer coherente el existente.

### Qué ya está resuelto

- **005-003** ya contrató la vista compacta, la ampliación de contexto con motivo, los ejemplos ejecutables y la captura del retorno real. No corresponde volver a construirlos (`docs/specs/005-003-orientation-reduction/spec.md:140-203,326-345`).
- **007-001** ya identifica situación, siguiente operación, script y procedimiento. Esa operación es el **primer paso verificable**, no una macro ni autorización (`docs/specs/007-001-unambiguous-entry/spec.md:84-111`).
- Ya existe un asset con ejemplos de observaciones de despacho, actualización de continuidad, `status` y `open-unit` (`skills/cdad-cycle/assets/orientation-examples.json`).
- La ruta C ya es la preferida para nuevos despachos nativos; A sigue siendo válida donde corresponde (`skills/cdad-cycle/references/handoff-prompts.md:16-28`).

### Qué falta conectar o corregir

1. **Carga contradictoria.** El orquestador dice evitar el manual completo, pero su entrada de sesión exige cargarlo; además, su renderizado prescribe enviar stdout completo mientras otra sección establece C. No es solo desobediencia del modelo: hay instrucciones incompatibles (`sources/roles/orchestrator.md:85-120,169-224`).

2. **Formatos poco visibles.** Las ayudas actuales muestran `--input INPUT` y `--update UPDATE`, sin explicar sus formatos. Los validadores sí conocen `PATH=PURPOSE`, el documento JSON de continuidad y los submodos incompatibles.

3. **Recetas desactualizadas entre sí.** El arranque y el flujo mínimo de continuidad no muestran toda la secuencia vigente de transporte nativo: `begin` → `verify-begin` → herramienta nativa → registro con el mismo entero. Esa secuencia sí aparece en el mandato canónico (`sources/roles/orchestrator.md:192-209`).

4. **Ejemplos correctos pero desconectados.** Faltan conexiones ejecutables para preparar un encargo completo, distinguir los usos de `--input`, recuperar continuidad y reemplazar sin mezclar opciones.

5. **Entrada de sesión confundida con transición interna.** La distinción existe conceptualmente, pero no queda suficientemente explícito que terminar `open-unit` no inicia otra sesión ni obliga a reconstruirla.

6. **Captura fiable enseñada como alternativa, no como recorrido principal.** El patrón actual reconoce el riesgo de las tuberías; conviene priorizar captura completa sin tubería y presentación posterior (`references/orientation.md:54-72`).

El diagnóstico recibido aporta una observación privada: aproximadamente **299 s**, **49 llamadas a herramientas** y **49 turnos de asistente** hasta la primera delegación; las herramientas terminadas acumularon aproximadamente **16,1 s**. También reportó un primer input de **46.187 tokens** y un último `input + cache.read` de **132.424 tokens**. Son datos aportados, no reproducidos aquí: no constituyen benchmark universal ni permiten atribuir el tiempo restante exclusivamente al razonamiento.

El desajuste visual del directorio mostrado por OpenChamber **no se considera causa**.

## 2. Diseño elegido

### A. Una entrada corta que compone lo existente

Mantener `orientation.md` como dueño de la orientación y `project-start.md` como dueño del arranque desde reposo. No crear un tercer manual.

El orquestador generado, que ya recibe su contrato de rol, seguirá este criterio:

- Resolver la raíz y la ubicación efectiva del producto instalado.
- Consultar `status`.
- Seguir `situation` y `next.operation` hacia la sección pertinente.
- Ampliar lecturas por una duda o bloqueo concreto, no para reconstruir por defecto el estado o el CLI.
- No interpretar `next-unit/open-unit` como permiso para abrir trabajo ante una consulta o un pedido exclusivamente de diseño.

**Cambio doctrinal explícito:** retirar la obligación de cargar íntegramente `cdad-cycle` en cada entrada del orquestador generado. Conservar esa carga para el flujo legacy y cuando falte el contrato operativo necesario. Esto requiere una enmienda acotada a la prescripción de carga de ADR-021; no se presenta como una regla ya vigente.

Para localizar `<skill-dir>`, los adaptadores documentarán las ubicaciones convencionales que ya instala `install.sh`, sin confundirlas con la instalación efectiva. Ante instalaciones personalizadas, debe confirmarse su procedencia; si solo puede conocerse cargando la skill, esa carga será una excepción justificada. No se inventa una variable de runtime ni se busca globalmente.

**Resuelve:** carga completa redundante, volcado histórico y exploración del CLI para operaciones ordinarias.

### B. Continuar una transición no equivale a reingresar

La entrada de sesión se aplica al comienzo real de una sesión:

- Si hay ejecución activa, reconstruir la continuidad correspondiente y reconciliar trabajo despachado antes de repetir efectos.
- Desde reposo, no ejecutar `resume`.
- Después de un `open-unit` realizado en esta sesión, continuar desde su resultado hacia el encargo autorizado. No repetir intake/resume solo porque cambió el estado.
- Volver a consultar orientación si aparece una contradicción, una interrupción o evidencia de cambios concurrentes.

Esto es una regla de procedimiento, **sin marcador nuevo de sesión ni estado adicional**.

### C. Ayudas suficientes sobre los comandos actuales

Mejorar las ayudas de `cdad_packet.py` y `cdad_continuity.py`, sin añadir comandos ni formatos:

- `prepare` ordinario: `--input PATH=PURPOSE`, repetible.
- Registro de despacho: el mismo `--input` recibe un **archivo JSON de observaciones**, no una entrada documental.
- `begin`/`checkpoint`: `--update` recibe la **ruta a un archivo JSON cuyo contenido es un objeto**, no texto literal ni Markdown.
- `resume`: requiere `--execution-context`; no asumir la resolución implícita disponible en otras superficies.
- `--replace-packet`: explicar las correcciones admitidas y la incompatibilidad con `--role`, `--substage` y `--objective`.

Los errores conservarán códigos y validaciones existentes. Solo donde falte orientación añadirán **argumento/campo, causa y recuperación legítima**, remitiendo al ejemplo canónico. No habrá otro esquema paralelo ni generador de documentación.

**Resuelve:** los intentos fallidos de formatos y mezclas de submodos.

### D. Preparar el encargo íntegro antes de publicarlo

Añadir al procedimiento una comprobación breve usando el encargo existente, no un formulario nuevo:

- objetivo y resultado esperado;
- requisitos y exclusiones ya recibidos;
- fuentes, alcances e invariantes;
- evidencia solicitada;
- vehículo de entrega.

Transmitirlos mediante los campos actuales y revisar el paquete resultante antes del transporte. La integridad semántica sigue siendo responsabilidad del orquestador: el validador no puede demostrar que entendió todas las condiciones del usuario.

Si hay paquete válido, usar C para nuevos despachos nativos y A cuando el transporte lo requiera, siempre con los bytes del renderer. Si no existe la autoridad o el contrato necesario para preparar —como en este diseño preliminar— utilizar la consulta legacy permitida, sin fabricar aprobación.

**Resuelve:** omisiones que provocan retirada/republicación y deliberaciones innecesarias entre A/C.

### E. Evidencia completa antes de mostrar extractos

El recorrido recomendado capturará stdout y stderr completos en rutas autorizadas del workspace, guardará inmediatamente el retorno del proceso y después mostrará extractos.

Debe funcionar también con `set -e`: ejecutar el comando dentro de una condición explícita, conservar su código y devolverlo al llamador. No usar el resultado de `head`, `tail` o un `printf` final como retorno del CLI.

Para payloads de despacho, preservar los bytes directamente: **no usar sustitución de comandos que elimine saltos de línea finales**, ni mezclar metadatos con el render.

**Resuelve:** falsos éxitos de tuberías y evidencia incompleta.

### Alternativas descartadas

- **Solo añadir recomendaciones:** deja intactas las contradicciones y ayudas insuficientes.
- **Comando nuevo `start` o macro de ejecución:** duplicaría procedimientos y acercaría orientación a autorización/despacho automático.
- **Generador de manuales o framework de ejemplos:** costo innecesario; bastan el asset y los tests existentes.
- **Límites de llamadas, bloqueo de lecturas o reducción forzada de contexto:** no resuelven la causa y restringen exploraciones legítimas.
- **Actualizar globalmente para probar:** innecesario; la adopción debe ser voluntaria y localizada.

## 3. Alcance por fuentes

**Modificar:**

- `sources/roles/orchestrator.md`: entrada, carga condicional, continuidad interna y preparación íntegra.
- `sources/agents/adapters/opencode.md`
- `sources/agents/adapters/claude-code.md`: localización del producto y redacción coherente de transporte.
- `skills/cdad-cycle/SKILL.md`: eliminar contradicciones de carga y alinear sus punteros.
- `skills/cdad-cycle/references/orientation.md`: conexión con operaciones, ejemplos y captura.
- `skills/cdad-cycle/references/project-start.md`: continuidad del arranque y receta vigente.
- `skills/cdad-cycle/references/continuity.md`: entrada de sesión y orden vigente.
- `skills/cdad-cycle/references/project-execution.md`: únicamente conexiones y aclaraciones pertinentes.
- `skills/cdad-cycle/references/handoff-prompts.md`: preparación íntegra y coherencia de vehículos.
- `skills/cdad-cycle/assets/orientation-examples.json`: ampliar los ejemplos existentes.
- `skills/cdad-cycle/scripts/cdad_packet.py`
- `skills/cdad-cycle/scripts/cdad_continuity.py`: ayudas y diagnósticos de los bordes descritos.

**Pruebas:** ampliar cobertura por promesa en un módulo nuevo propuesto, `tests/test_orchestrator_startup_usability.py`, reutilizando fixtures y pruebas existentes. El AUDIT decidirá cualquier modificación necesaria de tests vigentes.

**Salidas derivadas:** regenerar mediante `make agents`; nunca editar `agents/**` manualmente. No se prevén cambios a `Makefile` ni a la lógica de `scripts/cdad-generate.py`.

**Documentación de cierre:** el scribe propondrá la actualización de `docs/systemPatterns.md` y la enmienda de ADR-021. El orquestador materializará también los deltas del inventario vivo correspondientes.

No se modifican contratos históricos aprobados, configuración de modelos, políticas de proyecto ni estado para realizar este diseño.

## 4. Postcondiciones propuestas

### Promesa 1 — La entrada indica cómo avanzar sin reconstruir el sistema

**PC-1.** Fuente del orquestador, ambos generados y skill dejan de exigir y prohibir simultáneamente la carga completa. La entrada compacta y las excepciones están expresamente diferenciadas.

**PC-2.** El procedimiento distingue sesión nueva, reposo y continuación tras `open-unit`; no prescribe `resume` por una transición interna ni apertura de trabajo por una mera consulta.

### Promesa 2 — Las interfaces ordinarias se pueden usar sin leer implementación

**PC-3.** Las ayudas explican los dos formatos de `--input`, el archivo JSON de `--update`, el contexto requerido de `resume` y las opciones incompatibles de reemplazo.

**PC-4.** Los negativos comprometidos —entrada sin propósito, contexto omitido, actualización literal/Markdown y reemplazo mezclado— fallan con el código aplicable, diagnóstico accionable y sin publicar efectos nuevos.

### Promesa 3 — Los ejemplos llevan a un encargo válido

**PC-5.** Los ejemplos del asset se ejecutan sobre fixtures autocontenidos, con sustituciones limitadas de rutas e identidades. Cubren los formatos anteriores y la secuencia nativa vigente, incluido `verify-begin` y la conservación del entero de continuidad.

**PC-6.** El procedimiento transmite todos los requisitos del caso de aceptación mediante campos existentes. C y A mantienen sus contratos y no se mezclan; la ausencia de autoridad no se resuelve inventándola.

### Promesa 4 — La evidencia permite confiar en el resultado observado

**PC-7.** El patrón de captura conserva salida completa y retorno del CLI, incluso ante fallo con `set -e`; el payload renderizado mantiene sus bytes.

**PC-8.** La generación es determinista y coincide con las salidas publicadas; las verificaciones doctrinales conservan los límites de roles, autoridad y orientación.

**PC-9.** El ensayo real entrega un registro comparable de llamadas, lecturas, contexto y tiempos, con cobertura y limitaciones explícitas, sin presentar observaciones desconocidas como medidas.

### Invariantes

No nuevos estados, gates, aprobaciones, macros ni executor. `status.next.operation` no concede autoridad. Se conservan ADR-003, ADR-011, ADR-032 y ADR-033: separación de roles, materialización, límites proporcionales, delegación por runtime y modelos por configuración.

La documentación orienta al LLM; **no controla mecánicamente sus lecturas ni garantiza latencia**.

## 5. Plan propuesto

Cada tarea separará AUDIT, mantenimiento autorizado, RED y GREEN en los despachos que correspondan. Nunca se encargarán varias subfases TDD en una sola invocación.

### T1 — Entrada y encargo coherentes

**Dependencias:** aprobación del diseño y revisión independiente del borrador.

**Roles:** test-writer para AUDIT/verificadores; implementer para fuentes y documentación.

**Consume:** PC-1, PC-2 y PC-6.
**Produce:** entrada compacta coherente, reglas de continuación y preparación íntegra; agentes regenerados.

**Verificación:** checks documentales por conceptos, contraste doctrinal independiente y regresiones:

- `test_005_006_t1_start_procedure.py`
- `test_006_002_u6_context_discipline.py`
- `test_006_005_u4_single_entry.py`
- `test_007_001_unambiguous_entry.py`

**Criterio:** no queda una ruta ordinaria que ordene simultáneamente cargar y evitar el manual, repetir resume tras apertura o tomar orientación como autoridad.

### T2 — Formatos y ayudas accionables

**Dependencias:** T1, para consumir su terminología y referencias.

**Roles:** test-writer RED; implementer GREEN, separados.

**Consume:** PC-3 y PC-4.
**Produce:** ayudas suficientes, diagnósticos y ejemplos canónicos de los formatos comprometidos.

**Verificación:** subprocess de `--help` sin configuración de proyecto; positivos y negativos en fixtures válidos; comparación del árbol antes/después de rechazos. Preservar códigos existentes y ejecutar regresiones de preparación, reemplazo y continuidad afectadas.

**Criterio:** las operaciones comprometidas se pueden formular desde ayuda y ejemplos, sin inspeccionar fuentes del CLI.

### T3 — Recorrido ejecutable y captura fiable

**Dependencias:** T1 y T2.

**Roles:** test-writer RED/integración; implementer GREEN, separados.

**Consume:** PC-5 y PC-7.
**Produce:** asset conectado al procedimiento y verificación del recorrido completo hasta la frontera de transporte.

**Verificación:** ampliar `test_005_003_t2_examples_execute.py` o cubrir su delta en el módulo nuevo; ejecutar ejemplos realmente, comprobar negativos y códigos, preservar evidencia y contrastar bytes del render. No simular una aprobación ni invocar un worker real desde tests deterministas.

**Criterio:** el recorrido documentado es ejecutable y sus fallos no quedan ocultos por la presentación de salida.

### T4 — Revisión, ensayo y adopción voluntaria

**Dependencias:** T1–T3.

**Roles:** reviewer independiente; orquestador para evidencia y ensayo; scribe para borradores de cierre.

**Consume:** PC-8 y PC-9 y evidencia de las tareas anteriores.
**Produce:** revisión, informe de uso y propuesta de adopción/rollback.

**Verificación:** generación determinista/paridad mediante los tests existentes; `make validate`; regresión proporcional; integridad del inventario mediante `python3 scripts/cdad-suite.py validate`, conforme al momento contractual.

**Criterio:** promesas verificadas, hallazgos resueltos o tratados por la autoridad pertinente, límites del ensayo declarados. Ningún despliegue global implícito.

## 6. Ensayo real y medición

Realizarlo en una **sesión nueva**, con la versión propuesta instalada en un ámbito aislado y un encargo autorizado. No reutilizar autoridad vencida ni repetir efectos sobre trabajo real.

Para una comparación defendible, registrar versión, configuración efectiva —sin cambiarla—, estado inicial, tarea, permisos y condiciones de caché observables. Preferir control y propuesta sobre copias desechables equivalentes, con autorización para cada ejecución. Si no puede reconstruirse la línea base original, declararla **referencia histórica no equivalente**.

Medir hasta la primera delegación legítima, o hasta el bloqueo correctamente declarado:

- llamadas y turnos, incluyendo el despacho;
- lecturas iniciales, repetidas y ampliaciones con motivo;
- bytes efectivamente devueltos, cuando sean observables;
- métricas de contexto con sus campos y cobertura, sin convertir bytes en tokens;
- tiempo total y duración de herramientas terminadas por separado;
- errores de invocación, republicaciones y motivo.

No restar duraciones para bautizar el residuo como “razonamiento”. No sumar contadores de contexto de semántica distinta.

**Aceptación de uso:** recorrido legítimo, encargo íntegro y registro recuperable. La reducción de costo se juzga con los datos obtenidos; no mediante cuotas arbitrarias de llamadas ni una garantía de segundos. Si persiste una fricción diagnosticada, se registra: no se declara resuelta por tener tests verdes.

## 7. Riesgos, despliegue y exclusiones

**Riesgos principales:** perder conocimiento al abreviar la carga; confundir una ubicación convencional con la efectiva; duplicar recetas; y comprobar presencia de instrucciones sin comprobar su uso. Se mitigan con referencias por necesidad, procedencia confirmada, un dueño por procedimiento, ejemplos ejecutados y ensayo real.

**Adopción:** primero revisión e instalación aislada; después actualización voluntaria del ámbito elegido por el dueño. Un `DRIFT` limitado al proyecto no obliga a actualizar globalmente ni demuestra qué cargó una sesión abierta.

**Rollback:** volver a la revisión anterior mediante el mecanismo de instalación existente, conservando evidencia y respetando cambios locales. No requiere migración de estado ni eliminación de historiales.

### deferred-hardening

- Control automático de lecturas o cumplimiento del modelo: fuera de alcance; exigiría otro mecanismo.
- Benchmarks estadísticos y atribución causal: diferidos; la evidencia disponible no los sostiene.
- Ayudas exhaustivas para todo el CLI: se limita a las operaciones implicadas en el diagnóstico.
- Rediseño del historial, medidor o instalación: no es necesario para esta mejora.
- Transporte externo completo: se conserva por regresión; el ensayo principal corresponde al arranque nativo observado.

## 8. Fuentes y límites de este borrador

Se contrastaron las fuentes locales indicadas, las ayudas públicas de ambos CLI y una proyección selectiva del estado, en la revisión `17bbd0257bb0`. No se leyó el historial completo, no se ejecutaron tests ni se modificaron archivos; el repositorio permaneció limpio.

Las métricas de la sesión original proceden del diagnóstico recibido. La verificación documental demuestra coherencia de instrucciones; los tests demostrarán comportamiento mecánico; el ensayo aportará evidencia de uso, no obediencia universal del modelo.

**Pendiente:** revisión independiente y aprobación del alcance, incluida la enmienda de carga inicial. Después, autorización del ámbito de ensayo y eventual adopción. No hacen falta más decisiones funcionales para continuar con este borrador.
