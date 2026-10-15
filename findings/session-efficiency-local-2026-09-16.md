# CDAD: ampliación del relevamiento con sesiones locales

Fecha: 2026-09-16. Revisión documental: `b4a1bef`. Investigación retrospectiva de solo lectura; no implementa optimizaciones, no certifica gates y no activa el epic 003.

## Resultado principal

La muestra ampliada refuerza la prioridad de detectar bucles sin progreso y limitar la acumulación de contexto del orquestador. La repetición de cargas de `cdad-cycle` dentro de una sesión existe, pero es infrecuente. La fricción de permisos también merece medición y recuperación explícita.

Se observaron estos casos adicionales:

- Un subagente genérico de una familia con delegaciones CDAD hizo **1.800 llamadas de compilación con dos variantes de comando**, ambas con la misma salida de éxito. La secuencia consecutiva más larga de argumentos y resultado idénticos contiene **896 llamadas durante 101,35 minutos**.
- Un agente `cdad-implementer` repitió **78 veces una llamada denegada**, distribuida en 43,67 minutos.
- Un subagente repitió **224 consultas idénticas de estado Git durante 41,13 minutos**, sin otras llamadas de herramientas en esa sesión.
- Se registraron **954 invocaciones de `cdad-cycle` en 939 sesiones**; solamente **7 sesiones** la invocaron más de una vez.

Estos resultados amplían el [primer relevamiento](session-efficiency-2026-09-16.md). No se suman ambas muestras: no se verificó su disjunción ni equivalencia de selección, runtime o período.

## Fuente, selección y privacidad

Base SQLite local de OpenCode, consultada mediante `mode=ro`, `query_only=ON` y una transacción de lectura para el agregado principal. Inventario: 2.923 sesiones, 70.005 mensajes y 303.133 partes; 63.532 mensajes de asistente en el conjunto de la base. El corte del agregado terminó aproximadamente a las 22:16 UTC. Las verificaciones puntuales posteriores usan los mismos eventos históricos identificados.

Dos selecciones, publicadas por separado:

1. **Sesiones con evidencia explícita de CDAD:** al menos un mensaje con agente/modo cuyo nombre empieza por `cdad-`, o una llamada `skill` cuyo nombre empieza por `cdad`. Hay 1.351 sesiones por la primera condición y 11 adicionales por la segunda: **1.362 sesiones**. Se cuentan todos los mensajes de asistente y herramientas de esas sesiones, incluso si cambiaron de agente.
2. **Familias vinculadas:** subir por `parent_id` hasta la raíz disponible de cada sesión seleccionada y tomar todos sus descendientes registrados. Resultado: **1.943 sesiones en 666 familias**. Incluye agentes genéricos y actividad que no necesariamente corresponde a un ciclo CDAD. Una familia no equivale a una feature ni necesariamente a un proyecto. No se reconstruyeron vínculos de delegación ausentes de `parent_id`.

Los alias `Sxxxx` se asignan por orden de creación e ID en esta extracción. La correspondencia con IDs reales, los eventos de respaldo, el extractor y los resultados intermedios permanecen en un directorio temporal privado, fuera del repositorio. Son alias de este estudio, no identificadores globales ni estables frente a otra extracción. Se omiten rutas, proyectos, identidades, cuentas, prompts, código y salidas privadas.

La muestra explícita cubre actividad desde el 31 de julio hasta el 16 de septiembre. Las versiones registradas de sesión son 1.18.4, 1.18.10, 1.18.16, 1.18.18 y 1.18.29. Ese campo no demuestra la versión exacta del ejecutable durante cada evento de una sesión reanudada.

## Agregado medido

| Métrica | Sesiones con evidencia explícita | Familias vinculadas |
|---|---:|---:|
| Sesiones | 1.362 | 1.943 |
| Mensajes de asistente | 30.407 | 43.582 |
| Llamadas de herramientas | 38.445 | 56.356 |
| Herramientas con estado `error` | 3.750 | 4.364 |
| Errores clasificados por texto como permisos | 3.287 | 3.685 |
| Tokens `input`, acumulados | 692.777.983 | 1.113.676.958 |
| Tokens `cache.read`, acumulados | 5.954.785.566 | 6.471.045.566 |
| Tokens `output`, acumulados | 16.612.249 | 23.726.927 |
| Tokens `reasoning`, acumulados | 8.003.468 | 9.266.590 |
| Partes `compaction` | 22 | 22 |
| Unión de intervalos de mensajes de asistente | 247,99 h | 250,36 h |

Los tokens se suman una vez por mensaje de asistente, sin volver a sumar `step-finish` ni totales de sesión. Son contadores reportados; no son costo monetario ni tamaño simultáneo del contexto. Las categorías de tokens pueden tener semántica específica del proveedor: se mantienen separadas, sin construir un total facturable.

Los intervalos usan `time.created` y `time.completed` válidos. La unión evita sumar simultaneidad entre padres e hijos, pero no mide inferencia pura ni horas humanas. Incluye esperas de herramientas y excluye mensajes sin intervalo completo. No mide tiempo hasta feature aceptada. No se suman duraciones de `task` a esa unión.

## Casos contrastados

| Alias | Rol registrado | Fecha UTC | Observación | Interpretación |
|---|---|---|---|---|
| S2512 | `general`, en familia con roles CDAD | 11 de septiembre | Dos grupos de 1.178 y 622 llamadas de compilación, cada grupo con argumentos idénticos y la misma respuesta de éxito de 25 bytes; 896 llamadas consecutivas idénticas en 101,35 min. | Bucle de verificación exitoso sin progreso observable en la secuencia. |
| S0962 | `coder`, en familia con roles CDAD | 3 de agosto | 224 llamadas consecutivas de estado Git, respuesta idéntica, 41,13 min. Toda la sesión contiene esas 224 llamadas `bash`. | Repetición sostenida sin avance observable; sin mensajes nuevos de usuario durante el intervalo. |
| S1353 | `cdad-implementer` | 9 de agosto | 78 repeticiones de una llamada de inspección denegada, 43,67 min entre primera y última; la racha consecutiva mayor tiene 30 llamadas. | Bucle ante un rechazo de permisos. No es un fallo funcional de tests. |
| S2832 | `cdad-reviewer` | 14 de septiembre | 12 llamadas idénticas; 11 consecutivas. La herramienta figura `completed`, pero responde que el wrapper no soporta la operación solicitada. | El estado `completed` por sí solo no prueba éxito ni progreso. |
| S0974 | `coder`, en familia con roles CDAD | 3 de agosto | 242 lecturas consecutivas del mismo final de log, salida idéntica durante 53,47 min; dos mensajes de usuario en el intervalo. | Posible polling. Requiere revisar la condición esperada y las instrucciones antes de considerarlo desperdicio. |

La repetición exacta se obtiene con hashes de herramienta, argumentos JSON canónicos y tupla de salida/error/estado. «Consecutiva» significa sin otra llamada de herramienta intercalada en esa sesión, ordenada por timestamp; no significa ausencia de razonamiento o texto entre llamadas.

En S2512, el grupo de 1.178 repeticiones abarca 128,18 minutos y contiene solo llamadas `bash` en su intervalo; no aparecen herramientas de edición. El otro grupo abarca 51,49 minutos. Se inspeccionaron los comandos: son dos envoltorios de la misma compilación. La respuesta informa éxito, pero no se volvió a ejecutar ni se certificó el build. No se descartan cambios externos del árbol y no se presenta el intervalo completo como ahorro recuperable.

La raíz de esa familia registra delegaciones a architect, test-writer, implementer, reviewer, scribe y agentes genéricos. S2512 no cargó explícitamente `cdad-cycle`: atribuir su bucle directamente al prompt del implementer CDAD sería incorrecto. El detector debe cubrir también los agentes auxiliares del flujo.

Los casos abarcan etiquetas de modelos GLM y DeepSeek; no se demuestra que el problema sea exclusivo de un modelo, ni cuál fue su causa raíz. No se deduce un abandono o una aceptación final a partir de un mensaje incompleto o de la ausencia de veredicto estructurado.

## Contexto reportado por rol

Proxy por mensaje: `input + cache.read + cache.write`, tomando solo valores positivos y mensajes etiquetados con el rol indicado. No es una medición independiente de texto ni una prueba de capacidad efectiva del modelo.

| Rol | Mensajes con proxy positivo | Mediana | Máximo |
|---|---:|---:|---:|
| Orquestador | 16.404 | 252.762,5 | 1.013.174 |
| Implementer | 4.355 | 86.614 | 1.013.668 |
| Reviewer | 1.365 | 62.131 | 140.308 |
| Architect | 1.241 | 61.446 | 181.139 |
| Test-writer | 1.366 | 52.452,5 | 211.591 |
| Scribe | 371 | 57.626 | 109.240 |

Se separó la variante histórica `cdad-test-writer-local`: 668 mensajes positivos, mediana 80.522,5 y máximo 182.792. Las variantes Odoo explícitas tienen una muestra mínima y no permiten comparación representativa. No se mezclan roles personalizados con los de la tabla.

El orquestador supera 500.000 tokens reportados en 3.145 mensajes positivos, aproximadamente el 19,2 %. El máximo global de 1.013.668 pertenece al implementer S1353: `input=804`, `cache.read=1.012.864`. Su único `step-finish` coincide con los contadores del mensaje. Esto descarta doble suma de pasos en ese máximo; no valida independientemente el contador del proveedor.

La concentración en el orquestador da fundamento a checkpoints y reconstrucción de tarea. Las medianas no aíslan causalidad: tareas, antigüedad de sesiones, modelos e instrucciones difieren.

## Skills, permisos y tests

**Skills.** Las 954 invocaciones de `cdad-cycle` se distribuyen en 939 sesiones. Siete sesiones tienen más de una, con máximo de cinco. Son 15 invocaciones por encima de una por sesión: no respalda recarga habitual por turno. Se cuentan intentos de herramienta, no necesariamente cargas exitosas; tampoco se capturan cargas por lectura de archivos o inyección automática. Las salidas asociadas suman 30.550.482 bytes entre todas las sesiones, no tokens ni contexto simultáneo.

**Permisos.** Los 3.287 errores identificados por texto representan el 87,7 % de los 3.750 errores de herramientas en la selección explícita. La clasificación busca expresiones de permiso/denegación en el campo de error; no es una certificación manual de todos los casos. El caso S1353 se verificó individualmente. Se deben distinguir permisos correctos frente a un intento fuera de rol, incompatibilidad de wrappers y configuración defectuosa. Abrir permisos globales no es una solución aceptable.

**Tests.** La heurística de comandos detecta 1.805 candidatos en la selección explícita, con 61,14 minutos acumulados en los intervalos registrados de herramienta. No equivalen a suites completas ni miden todo el costo de tests: puede incluir menciones o rechazos, omitir wrappers, scripts, ejecución remota y procesos en background. Esta cifra no permite concluir que tests sean baratos ni compararla directamente con el caso Odoo del otro informe.

## Versiones y reproducibilidad

La skill del repositorio y la instalada actualmente en dos ubicaciones locales no coinciden:

- Repositorio: SHA-256 `a75990c8639592eaea7d2236f2531875c1de43cc8e05f40dcf7a62b056664e5f`.
- Instalaciones consultadas: SHA-256 `48e44a6873b438a50e97ed755abf6acc41b7259d7e4ba9a93a0c4640b98e7854`.

La diferencia no prueba un defecto ni identifica qué revisión estaba cargada en cada evento. No se reinstalaron skills, no se reanudaron sesiones y no se ejecutaron builds o tests de los proyectos analizados.

Procedimiento para reproducir el agregado en una copia equivalente de la base:

1. Abrir SQLite en lectura y fijar una transacción. Inventariar `session`, `message` y `part`.
2. Seleccionar sesiones por agente/modo CDAD o invocación de skill CDAD, sin seleccionar por título de proyecto.
3. Formar familias exclusivamente con `parent_id`, conservando separadas ambas cohortes.
4. Sumar contadores de mensajes de asistente; contar herramientas desde partes de tipo `tool` y compactaciones desde `compaction`.
5. Agrupar repeticiones por sesión/herramienta/argumentos/resultado; separar rachas consecutivas de repeticiones distribuidas.
6. Calcular unión de intervalos y proxies positivos por mensaje. Conservar las limitaciones del proveedor y valores desconocidos.
7. Inspeccionar ejemplos concretos con comandos y resultados, manteniéndolos privados; publicar únicamente alias y descripciones depuradas.

El extractor y el mapa privado son temporales, no un artefacto versionado del epic. Para una línea base mantenible falta convertir este procedimiento en una extracción parametrizada y validada, guardar un corte reproducible con política de retención y fijar versiones efectivas. Los agregados de este documento no permiten por sí solos reconstruir la base ni acceder a conversaciones.

## Consecuencias para el epic 003

Orden recomendado de investigación, sin aprobar ni cambiar todavía la descomposición:

1. **Detección y recuperación de falta de progreso**, incluyendo éxito repetido, permiso denegado y error semántico con estado `completed`. Considerar tanto roles CDAD como auxiliares. Usar polling legítimo como control negativo y distinguir racha, resultado, objetivo y cambios relevantes.
2. **Compatibilidad de permisos y herramientas**, con una comprobación previa por rol y un retorno de bloqueo tras rechazos repetidos, conservando el aislamiento.
3. **Checkpoints del orquestador**, con decisiones, aprobaciones, tarea vigente y referencias a evidencia; evaluar además el implementer atípico de contexto extremo.
4. **Proyecciones de instrucciones por rol**, para reducir carga de arranque y contradicciones. La motivación empírica es carga distribuida y consistencia, no recarga habitual por turno.
5. **Clasificación por feature y propósito de los tests**, antes de prometer ahorro por evidencia reutilizada o modificar el presupuesto.

Pendientes: enlazar aceptación y retrabajo con features, separar esperas e inferencia cuando existan datos suficientes, auditar diversidad de modelos por pareja implementación/review y comparar variantes controladas. No se calcula costo por feature ni porcentaje de ahorro. El plan continúa en `draft` y los gates E1/E2 siguen abiertos.
