# Discovery — 010-004-packet-dispatch-ergonomics

**Resultado:** el repositorio ya verifica mecánicamente el paquete publicado y dispone de transporte externo sin retranscripción. El hueco está en el transporte nativo, su observabilidad y las instrucciones de intake. No hace falta inventar otro protocolo de paquetes, ledger o recibos.

Este informe es Discovery, **no una spec ni una aprobación**.

## 1. Incidentes y causas verificadas

| Incidente | Hallazgo |
|---|---|
| **I-1: pérdida de backticks** | El incidente está registrado en `observations-packet-dispatch.md:7-15`. El despacho nativo exige trasladar stdout sin cambios, pero esa exigencia es una **instrucción al orquestador**, no una conexión mecánica renderer→herramienta nativa (`sources/roles/orchestrator.md:63-76`). No encontré en las superficies examinadas una entrada nativa por archivo que evite trasladar el cuerpo como argumento textual. |
| **I-2: cierre JSON confundido con fin del paquete** | El renderer termina la cabecera y continúa inmediatamente con `# CDAD task`, instrucciones y cuerpo (`skills/cdad-cycle/scripts/cdad_packet.py:1853-1871`). El extractor conserva desde el marcador inicial hasta el final, no sólo hasta el cierre JSON (`:1885-1932`). La implementación distingue correctamente ambos; la confusión observada es del intake del rol. |
| **I-3: contexto inferido** | La cabecera incluye `execution_id` y el objeto `execution`, pero no la ruta utilizable del contexto (`:1825-1839`). Los comandos `render`, `validate-request` y `validate-packet` requieren `--execution-context` (`:9485-9491`). Ya existe un resolvedor v2 por identidad (`:2945-2955`); no corresponde duplicarlo. |
| **I-4: comparación de entrega no observable** | El original del scribe declara `cmp` render↔archivo, pero cotejo del prompt «campo por campo» (`docs/specs/010-000-continuity-relative-root/scribe-memory-002-original.md:1-6`). Eso no demuestra igualdad byte a byte de la entrega. Tampoco demuestra corrupción. El cierre preserva expresamente esa distinción (`closure.md:20-27`). |

Los detalles históricos de I-1 e I-2 están documentados por el orquestador; **no reproduje aquellos despachos originales**.

En este propio intake apareció otra manifestación de I-3: utilicé inicialmente `execution.authority_ref` como `--execution-context`; el CLI rechazó el Markdown como JSON. Con la ruta v2 correcta, la validación pasó. **Fuente de autoridad y contexto de ejecución son entidades diferentes.**

## 2. Superficie técnica real

### Producción y admisión

- **`validate_request`** comprueba identidad, contrato/digest, aprobación, scopes y binding con el paquete activo (`cdad_packet.py:1582-1788`).
- **`render_packet`** compone cabecera y cuerpo desde request, contexto y fuentes de instrucciones (`:1795-1871`).
- **`verify_published_packet`** resuelve el request publicado, valida y compara el archivo completo desde el marcador contra el render canónico (`:1935-1993`).
- **`validate-packet`** compara literalmente el archivo suministrado; su diagnóstico de divergencia es genérico (`:9905-9915`). A diferencia del verificador publicado, no elimina un preámbulo.

Estos son puntos de extensión existentes. Agregar un segundo verificador sería innecesario.

### Transporte nativo

El orquestador usa la herramienta nativa y después registra el intento; esa herramienta no realiza el registro CDAD (`sources/roles/orchestrator.md:45-61`).

Los adaptadores OpenCode y Claude Code ordenan pasar los bytes exactos, pero **no implementan una interceptación del prompt**:

- `sources/agents/adapters/opencode.md:66-100`.
- `sources/agents/adapters/claude-code.md:80-114`.

Además, ambos prohíben sustituir el transporte nativo por el adaptador CLI dentro del mismo runtime. Por tanto, **usar el CLI externo como atajo no es una solución compatible**.

### Transporte externo

Aquí sí existe una cadena programática:

1. Verificación del paquete publicado.
2. Lectura de `PACKET.md`.
3. Paso de sus bytes al adaptador.
4. Envío por stdin al cliente destino.

Fuentes: `skills/cdad-cycle/scripts/cdad_delegate.py:540-598` y `cdad_delegate_opencode.py:593-625`.

Esto elimina la retranscripción del cuerpo en ese recorrido. **No acredita por sí solo qué mensaje persistió o recibió finalmente el runtime.** Tampoco debe describirse como una transacción indivisible: la verificación y la lectura para transmitir son operaciones separadas.

### Registro y recepción del resultado

- El registro I8 contiene observaciones de runtime, modelo, sesión, momento y procedencia; **no contiene una prueba de igualdad del prompt recibido** (`cdad_packet.py:3760-3767,3810-3845`).
- Las capacidades del adaptador observan correlación de sesión, no integridad del prompt (`cdad_delegate_opencode.py:2257-2315`).
- El lector examinado extrae el último texto de assistant; no expone allí una comparación del mensaje user con el paquete (`:815-854`).
- `receive` verifica paquete, identidad y scopes y persiste el resultado con `semantic_status: pending` (`cdad_result.py:664-750`).

**Un recibo del resultado no es un recibo de integridad del prompt ni una aprobación semántica.**

## 3. Tres evidencias que deben permanecer separadas

| Evidencia | Qué puede acreditarse hoy |
|---|---|
| **Integridad del paquete publicado** | Mecánicamente: request validado y comparación completa con el render. |
| **Integridad de la entrega al rol** | Transporte programático hasta stdin en la vía externa. En la vía nativa examinada, la igualdad del prompt no queda acreditada por el verificador del archivo ni por I8. |
| **Fidelidad del resultado al encargo** | Contraste del contenido con contrato y fuentes, seguido del gate correspondiente. No se deduce de las dos anteriores. |

Esta limitación ya figura en el contrato anterior: `docs/specs/008-004-role-packet-enforcement/spec.md:44-47`. ADR-038 también la explica, pero **su estado es Proposed**, no ratificado (`docs/adr/ADR-038-admision-en-cada-frontera-invocable-y-comparacion-por-bytes.md:3,58-61`).

**VERIFY:** si cada runtime soportado permite recuperar el mensaje de entrada original, con correlación inequívoca y preservación suficiente para la comparación exigida. No se consultaron stores reales ni código externo al repositorio; no afirmo que esa capacidad sea imposible o esté ausente en todos los runtimes.

## 4. Opciones y criterio recomendado

### A. Explicitar el contexto y mejorar el diagnóstico común

Preferible a corregir únicamente los ejemplos que fallaron:

- Declarar el contexto utilizable sin confundirlo con `authority_ref`.
- Reutilizar la resolución existente.
- Distinguir rechazo por identificación, contexto, contrato y divergencia del cuerpo.
- Indicar causa y siguiente acción sin imprimir contenido sensible.

Debe conservarse la compatibilidad deliberada con contextos v1; `.cdad/execution.json` no es universalmente incorrecto. También hay documentación que todavía lo presenta como entrada principal (`skills/cdad-cycle/references/handoff-prompts.md:5-30`).

### B. Emitir la ruta C existente, no crear otra

La ruta C ya está definida: identificación explícita de un paquete único, validación de request y archivo completo, sin ampliar el scope de producto (`sources/roles/architect.md:35-43`; spec anterior `:82-97`).

**Ventaja:** evita volver a transportar el cuerpo largo como texto reconstruido por el modelo.

**Límite:** una identificación corta trasladada por el modelo no convierte automáticamente la llamada nativa en transporte mecánico. Reduce la superficie de retranscripción, pero no prueba los bytes que recibió el runtime.

El criterio recomendado es reutilizar esta ruta común antes que añadir conectores específicos por runtime. Si se exige evidencia independiente de la entrega, esos conectores necesitarían capacidad real demostrada; no basta agregar otro hash declarado.

### C. Tratar honestamente lo no observable

Recomiendo distinguir en la futura spec:

- Divergencia real o autoridad inválida: rechazo.
- Evidencia de entrega insuficiente: limitación explícita, **no prueba automática de corrupción**.
- Resultado infiel al contrato: hallazgo sobre el resultado, independientemente del transporte.

Esto requiere aprobación contractual; **Discovery no cambia las reglas vigentes ni autoriza rescatar un inline alterado mediante C**.

## 5. Convenciones y regresiones existentes

- El intake compartido pertenece a `sources/roles/architect.md:15-58`; el generador lo compone para los demás roles (`scripts/cdad-generate.py:70,633`).
- Los agentes son salidas generadas: se cambian fuentes y se regeneran, no se parchean copias (`Makefile:1-18`).
- Las pruebas actuales cubren alteración del paquete publicado y rechazo antes de efectos, no igualdad del mensaje nativo recibido (`tests/test_008_004_packet_enforcement.py:17-44`).
- Hay regresión de diferencias CRLF (`tests/test_role_packet_review_regressions.py:468`).
- Parte de las pruebas de consumidores comprueba instrucciones textuales sobre stdout sin cambios; eso no demuestra transporte real (`tests/test_role_packet_consumers.py:179-196`).

## 6. Preguntas para el usuario

1. **¿Qué significa exactamente eliminar la retranscripción manual?**  
   ¿Basta que el cuerpo se cargue desde el paquete publicado mediante una identificación C generada, o se exige una conexión mecánica renderer→herramienta nativa? La segunda todavía necesita verificar capacidades del runtime.

2. **¿La emisión de C es una decisión ya fijada o una opción?**  
   El historial aprobado menciona «emisión de ruta C por el renderer» (`plan.md:123-130`), mientras las observaciones piden no fijar mecanismo antes de Discovery (`observations-packet-dispatch.md:36-46`). Recomiendo reutilizar C, pero conviene resolver expresamente esta diferencia.

3. **¿Se aprueba que la futura spec distinga entrega no observable de entrega corrupta**, sin repetir automáticamente trabajo contrastable, manteniendo rechazo ante divergencias reales y los gates de fidelidad y aprobación?

## 7. Evidencia de esta ejecución

**Intake:** request validado. Comparación completa mediante literal explícito del texto recibido: **5.243 bytes, igualdad `True`**. Ese literal fue introducido por el modelo: **no es una exportación independiente del mensaje del runtime y no lo presento como prueba mecánica de entrega**.

**Paquete publicado:** verificación mecánica satisfactoria; igualdad con render. SHA-256:

```text
79237dd5ceff04d87c4559178aa2954e25927b4e6c41c039cff8b1c937c9aa7e
```

Sondas exclusivamente en memoria: preámbulo + paquete completo aceptado; cabecera sola y objetivo alterado distintos del canónico; marcador duplicado y cierre ausente rechazados. Python **3.13.5**, `CDAD_STATIC_BLOCK_LIMIT` sin configurar.

**Comandos exactos y salidas:** constan íntegros en las llamadas de herramientas de esta sesión, incluidos los dos here-docs de comparación y sondas. Los comandos CLI de validación/render con el contexto v2 terminaron `rc=0`; el intento inicial con `execution.md` terminó `rc=2`, con error de lectura JSON. No ejecuté tests, suite, generación ni instalación.

**Cambios:** ninguno. `git diff --exit-code` y `git diff --cached --exit-code`: `rc=0`. El único untracked, igual al inicio y al final, es `docs/specs/010-000-continuity-relative-root/discovery.md`; no lo modifiqué.

**HEAD:** `922db1a6e8ab822ba1aa7b50668f5321d83d0a7e`. **Commit creado:** ninguno.
