# CDAD: eficiencia de contexto, tokens y ejecución

Fecha: 2026-09-16. Ampliado el mismo día con una segunda revisión del repositorio. Estado: análisis y propuestas para discutir; no es un spec aprobado ni modifica el proceso vigente.

## Objetivo y alcance

Analizar cómo acelerar CDAD y reducir su consumo de contexto y tokens conservando los contratos, el aislamiento de roles y la evidencia de los gates. Este documento permite continuar la discusión desde la web sin depender del historial de una conversación.

Se revisaron secciones relevantes de la metodología, agentes, skills, handoffs, re-entry y el protocolo de presupuesto de tests. Es una revisión estática y dirigida, no una auditoría exhaustiva ni un benchmark de sesiones reales. Los tamaños son bytes medidos en archivos de la revisión base `f2b9611`; no equivalen a tokens ni al contenido que efectivamente inyecta cada runtime.

La ampliación contrasta agentes, skill central, handoffs, etapas TDD/review/merge, detección de estado y validadores en la revisión `eb3a511181c3d76d0306dd149176b90ebe8b617c` de `translation-en`. Las referencias relativas permiten navegar el repositorio; esa revisión fija la evidencia de los hallazgos aunque los archivos cambien después.

Privacidad: se omiten identidades de usuarios, rutas absolutas, cuentas, remotos, datos de clientes y detalles del entorno de ejecución. Las referencias internas son relativas al repositorio. Se conservan enlaces a publicaciones públicas como fuentes bibliográficas.

## Opinión principal

CDAD tiene una arquitectura compatible con contextos acotados: roles separados, artefactos persistidos y referencias bajo demanda. Sin embargo, las instrucciones actuales hacen cargar y repetir información que muchos roles no necesitan.

La sobrecarga no depende solamente de la longitud de los prompts. El modelo también debe interpretar mecánica del proceso: resolver instrucciones divergentes, reconstruir contexto, preparar transferencias y volver a verificar hechos. La hipótesis central es que cada modelo debería comprender su contrato y su tarea, mientras un componente determinista ejecuta la administración del procedimiento.

La primera oportunidad es mejorar la distribución del contexto y eliminar trabajo repetido. La migración a modelos pequeños o locales debería evaluarse después, con una base medida. Reducir el tamaño de los prompts no garantiza por sí solo menor costo por feature si aumenta los errores y las correcciones.

## Relación con el artículo

Fuente: [Notes on migrating 35kb prompts away from Anthropic/OpenAI to Self-Hosted Ollama+opencode](https://patrickmccanna.net/notes-on-migrating-large-prompts-away-from-anthropic-openai-to-self-hosted-llms/).

El autor describe llamadas repetidas, relecturas y trabajo rehecho al saturar el contexto. Propone objetivos acotados, estado persistido y cargar solo la información necesaria para cada tarea. Son observaciones prácticas útiles para CDAD, pero no un experimento que demuestre que esos fallos se deban exclusivamente al contexto. Sus afirmaciones sobre proveedores no son necesarias para este análisis ni se adoptan como hallazgos.

Tampoco conviene asumir que ejecución local implica siempre contexto pequeño. El modelo, la memoria y la configuración importan. [Ollama documenta](https://docs.ollama.com/context-length) cómo configurar el contexto y que ampliarlo requiere más memoria. La capacidad configurada y la calidad efectiva sobre contextos largos deben medirse por separado.

## Hallazgos del repositorio

| Hallazgo | Evidencia | Implicación a comprobar |
|---|---|---|
| Skill central de 34.700 bytes | [cdad-cycle](../skills/cdad-cycle/SKILL.md) | Los ejecutores cargan procedimientos de otras etapas. |
| Orquestador de 12.881 bytes, con contrato de roles también presente en la skill | [Agente orquestador](../agents/cdad-orchestrator.md) | Duplicación de instrucciones dentro de una sesión. |
| Handoffs de todos los roles reunidos en 25.324 bytes | [Handoff prompts](../skills/cdad-cycle/references/handoff-prompts.md) | Leer el archivo entero para un solo rol incorpora contenido innecesario. |
| Recarga explícita de la skill en cada turno | [Orquestador](../agents/cdad-orchestrator.md), [implementer Claude Code](../agents/claude-code/cdad-implementer.md), otros agentes de ese runtime | Lecturas redundantes; el efecto real depende del tratamiento del runtime. |
| Memoria activa acumulativa de 8.851 bytes | [activeContext](../docs/activeContext.md) | El historial de features cerradas se convierte en carga de arranque. |
| Metodología de 151.764 bytes | [Metodología](../CDAD_metodologia.md) | Debe funcionar como documentación consultable; no se encontró una obligación general de cargarla entera. |

No corresponde sumar todo el repositorio como si se cargara en cada sesión. Tampoco todos los bytes de un agente, incluido su frontmatter, necesariamente llegan al modelo como texto.

### Tensiones entre instrucciones y hallazgos adicionales

Los siguientes son hallazgos estáticos; su impacto efectivo sobre reintentos, tokens y latencia requiere trazas de ejecución.

| Tema | Evidencia en la revisión ampliada | Propuesta |
|---|---|---|
| Identidad del ejecutor | El [implementer](../agents/cdad-implementer.md) carga `cdad-cycle`; la [skill](../skills/cdad-cycle/SKILL.md) comienza con «You are the orchestrator» y prohíbe implementar, aunque después explica el modo por rol. | Entregar directamente el contrato del ejecutor, evitando que deba reconciliar instrucciones de identidad. |
| Granularidad | El contrato de estado del [orquestador](../agents/cdad-orchestrator.md) pide una postcondición/test por tarea. [TDD, Parallel dispatch](../skills/cdad-cycle/references/stage-3-tdd.md) declara predeterminado un paquete de postcondiciones ortogonales, con una sesión RED y un handoff GREEN. | Unificar la regla que ya permite agrupar; distinguirla de una futura ampliación a postcondiciones acopladas. |
| Alcance de properties | El orquestador excluye conjuntamente «Exhaustive coverage, property tests, load/perf, and edge cases». La skill y TDD sí incluyen properties derivadas de invariantes explícitos del spec. | Una política canónica proyectada en todas las instrucciones aplicables. |
| Volumen de properties | [Re-entry](../skills/cdad-cycle/references/re-entry.md) y TDD piden ≥100 entradas; [handoffs](../skills/cdad-cycle/references/handoff-prompts.md) propone 100–1000; el [protocolo Odoo](../skills/odoo-make-env/references/run-budget-protocol.md) propone 8–10. | Presupuesto por proyecto y propósito de validación, con precedencia explícita. |
| Continuación automática/manual | La skill y el orquestador ordenan terminar el turno después de delegar; las referencias describen esperar a que el usuario traiga resultados, incluso junto a instrucciones para subagentes nativos. | Separar modos de ejecución; en modo automático, reanudar al recibir el resultado, respetando las aprobaciones estratégicas. |
| Reutilización de evidencia | [Review](../skills/cdad-cycle/references/stage-4-review.md) permite citar evidencia vigente; [detección](../skills/cdad-cycle/references/state-detection.md) y [merge](../skills/cdad-cycle/references/stage-5-merge.md) vuelven a pedir ejecuciones. | Resolver vigencia de evidencia de forma común; no deducir que toda nueva ejecución es redundante, especialmente entre entornos. |
| Materialización de documentos | Los roles de solo lectura devuelven documentos como texto y el orquestador los escribe y commitea (contrato §5). | Persistir exactamente la salida mediante una herramienta determinista, sin requerir que otro modelo vuelva a generar el documento. |
| Acumulación | La tabla de referencias pide cargar detección en cada turno y handoffs al preparar paquetes; `activeContext` se define como historial acumulativo. | Cargar por necesidad y versión; separar estado vigente e historial. Leer bajo demanda no elimina lo ya leído del contexto. |

### Limitación concreta del validador de consistencia

En [tests/validate-consistency.sh, bloque F006](../tests/validate-consistency.sh), la corrección de la exclusión de property tests se verifica en `skills/cdad-cycle/SKILL.md` y `references/stage-3-tdd.md`, pero no en `agents/cdad-orchestrator.md`, donde permanece la frase contradictoria. Esto no afirma que se haya ejecutado el validador en esta revisión: es una observación sobre su alcance.

La propuesta es verificar que todas las proyecciones de una política provengan de la fuente canónica y probar el comportamiento relevante. Las comprobaciones de texto pueden ayudar a detectar divergencias, pero por sí solas no demuestran consistencia semántica ni cumplimiento del rol.

## Propuestas priorizadas

### 1. Separar instrucciones de orquestación y ejecución

Mantener `cdad-cycle` como entrada breve para detectar estado, elegir procedimiento y validar gates. Cada ejecutor recibe su contrato de rol, subfase y referencias aplicables, sin procedimientos de bootstrap, otros roles o runtimes ajenos.

Definir una fuente canónica por política y generar sus proyecciones por rol, stack y runtime. Los adaptadores conservan las restricciones específicas de cada entorno. Un criterio práctico: ningún ejecutor necesita cargar procedimientos del orquestador para saber qué puede hacer.

Conservar visibles las restricciones críticas, como la prohibición de editar tests para el implementer. Mover explicaciones, incidentes históricos y ejemplos extensos a documentación de consulta. Separar las plantillas de handoff por rol/subfase.

Presupuesto experimental inicial: 1–2 mil tokens de instrucciones estables por ejecutor, excluyendo spec, código, herramientas y contexto propio de la tarea. Es una hipótesis para medir, no un óptimo demostrado ni una razón para omitir restricciones necesarias.

### 2. Cargar una vez y recuperar según necesidad

Sustituir la recarga en cada turno por carga al iniciar sesión y recuperación cuando cambie la versión, cambie el objetivo o se pierda contexto relevante. Una caché de archivos leídos no implica que el modelo todavía conserve su contenido: el runtime debe distinguir ambas situaciones.

El contrato crítico debe permanecer disponible tras compactación o reinicio. Cargar una vez no significa confiar indefinidamente en un archivo que el modelo leyó pero ya no tiene en contexto.

Medir las cargas reales, incluyendo instrucciones globales, esquemas de herramientas, skills, archivos y resultados. El tamaño de una skill aislada no describe todo el contexto de arranque.

### 3. Handoff pequeño y verificable

Interpretar «contexto completo» como suficiente para ejecutar correctamente. Usar referencias versionadas y una selección explícita de archivos, sin copiar conversaciones ni razonamientos de otros roles.

Ejemplo de estructura propuesta:

```text
Rol/subfase: implementer / GREEN
Objetivo: satisfacer P3
Spec: ruta + versión
Lecturas: interfaz, tests relevantes, convenciones aplicables
Dependencias: invariantes y postcondiciones relacionadas
Edición: archivos permitidos
Evidencia RED: log + revisión correspondiente
Finalización: evidencia GREEN + archivos cambiados + bloqueos
```

La selección debe respetar permisos de lectura y no filtrar implementación al test-writer. Acotar contexto no justifica ocultar dependencias necesarias para cumplir el contrato. Una ruta disponible no equivale a información comprendida: incluir directamente las dependencias críticas y permitir ampliación de contexto dentro de los permisos del rol.

El paquete de retorno debe identificar resultado, artefactos, revisiones, evidencias, bloqueos y siguiente acción necesaria, sin volcar toda la conversación. Los hallazgos de review aplicables conservan su texto original y procedencia; optimizar la transferencia no autoriza suavizar ni alterar el feedback.

### 4. Separar memoria activa, conocimiento estable e historial

- `activeContext`: objetivo vigente, bloqueos y próxima acción.
- `systemPatterns`: convenciones vigentes organizadas por tema.
- Historial y decisiones: archivos consultables mediante un índice.

El scribe debería consolidar y reemplazar información obsoleta, además de agregar entradas. Los roles recibirían los temas aplicables, no todo el historial. Un checkpoint debe conservar decisiones, pendientes y referencias a evidencia para permitir una sesión nueva sin reconstrucción extensa. Debe permitir reconstruir el siguiente paquete desde archivos, sin depender de la conversación anterior. Reiniciar en un límite natural de trabajo es una opción a medir, manteniendo el aislamiento entre roles.

### 5. Generalizar el presupuesto de ejecuciones

El [run-budget-protocol](../skills/odoo-make-env/references/run-budget-protocol.md) ya aporta una base útil: tests focalizados al diagnosticar, suite completa al cerrar el gate y reutilización de evidencia válida. Extender el patrón a otros stacks y unificar instrucciones contradictorias.

La reutilización exige identidad de código, tests, dependencias, configuración y entorno relevante. Un commit por sí solo no garantiza equivalencia: puede haber cambios sin commit, fixtures externos o variaciones del entorno.

Propuesta de registro mínimo por ejecución:

- Identificador del gate/paquete y versión del spec cuando corresponda.
- Identidad del código y tests realmente ejecutados, incluyendo cambios sin commit.
- Dependencias, configuración, fixtures y entorno relevantes.
- Comando, selección de tests y semilla/parámetros si aplican.
- Código de salida, conteos de tests ejecutados/fallidos/omitidos y contraste con la selección esperada.
- Referencia al log completo y a los artefactos de la ejecución.

El gate consulta este registro y valida su vigencia. Un cambio documental no invalida automáticamente la evidencia; un cambio relevante en código, tests, configuración o fixtures puede invalidarla. Si no se puede establecer equivalencia, no reutilizarla. CI sigue ejecutándose cuando sea una condición requerida o verifique otro entorno. La suficiencia semántica de los tests sigue requiriendo evaluación independiente.

Separar **presupuesto de diagnóstico** de **suficiencia de validación**. Reducir properties de 100 casos a 10 conserva el invariante escrito, pero reduce la búsqueda de contraejemplos: no es un ahorro sin contrapartida. Definir explícitamente qué cubre el gate y qué se pospone a hardening.

Guardar logs completos como artefactos y devolver al modelo un resumen verificable con comando, resultado, cantidad de tests, revisión y ubicación de la evidencia. Conservar acceso al fallo completo cuando sea necesario para diagnosticar; no comprimir hasta ocultar errores o suites vacías.

### 6. Automatizar comprobaciones mecánicas

Validar con scripts presencia de artefactos, esquema del estado, alcance de archivos modificados y asociación entre evidencia y revisión. Reservar al modelo la interpretación semántica: si los tests verifican el contrato y si el cambio es correcto.

Un componente pequeño, por ejemplo en Go, podría ofrecer estas responsabilidades:

| Operación determinista | Juicio que permanece en el modelo o dueño del proceso |
|---|---|
| Validar esquema, transiciones y aprobaciones registradas. | Evaluar la claridad y suficiencia del contrato; emitir las aprobaciones que correspondan. |
| Preparar el contexto autorizado para un rol. | Identificar dependencias relevantes y solicitar ampliaciones. |
| Comprobar archivos modificados contra permisos. | Evaluar la corrección y alcance semántico del cambio. |
| Ejecutar comandos y registrar evidencia. | Determinar si los tests verifican realmente la postcondición. |
| Persistir exactamente el artefacto devuelto por un rol. | Redactar specs, reviews y decisiones. |

La persistencia no equivale a aprobación: la herramienta valida destino y alcance y guarda la salida sin otorgar al rol permisos generales de escritura ni autoaprobar sus documentos. No exige construir un framework completo; comenzar por preparación de contexto, evidencia y validación del estado.

Generar variantes de agentes desde fuentes comunes por rol, stack y runtime reduciría divergencias. El ahorro de mantenimiento es directo; el de tokens solo aparece si el contenido generado y cargado es menor. Preservar permisos específicos y sus verificaciones empíricas.

### 7. Evaluar granularidad y paralelismo

La agrupación ortogonal ya existe en TDD y en una excepción del handoff RED. Primero hacer consistente esa regla en todas las instrucciones. Agrupar postcondiciones acopladas sería una ampliación posterior de la política, con evaluación propia.

Cada paquete debe tener objetivo verificable, postcondiciones y dependencias identificadas, alcance de archivos explícito y tamaño compatible con el contexto disponible. Mantener RED y GREEN separados y la auditoría independiente. La evidencia debe permitir distinguir el resultado de cada postcondición.

Ejemplo hipotético, no benchmark: seis postcondiciones independientes tratadas individualmente requieren doce sesiones RED/GREEN. Agrupadas en dos paquetes requieren cuatro. Se evitan ocho arranques y sus transferencias, pero no desaparece el trabajo de implementación ni se demuestra una reducción de dos tercios del costo total.

Paralelizar tareas independientes cuando reduzca el camino crítico sin conflictos de archivos o estado. Más agentes pueden bajar la latencia y aumentar simultáneamente los tokens totales. No adoptar paralelismo como sinónimo de eficiencia.

### 8. Separar ejecución automática y handoff manual

- **Automática:** el resultado del subagente dispara re-entry, validación y siguiente transición autorizada. No añadir una espera humana a cada resultado mecánico.
- **Manual:** entregar el paquete y esperar que el usuario traiga el resultado del otro entorno.
- **En ambos modos:** conservar las aprobaciones estratégicas y cualquier delegación explícita ya registrada; no inferir autorización para eludirlas.

La selección de modo debe ser explícita y depender de las capacidades reales del runtime. Eliminar pausas innecesarias puede reducir tiempo transcurrido aunque no reduzca mucho los tokens; medir ambos efectos por separado.

### 9. Distinguir caché, contexto y generación

La caché de prefijos puede reducir costo y latencia cuando el proveedor/runtime la soporta, pero no sustituye la reducción del contexto lógico ni evita volver a generar documentos. Mantener instrucciones estables antes del contexto variable cuando el runtime lo permita; medir lecturas/escrituras de caché y costo efectivo, sin asumir comportamiento idéntico entre proveedores.

Referencias complementarias consultadas para esta ampliación:

- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): recuperación selectiva, memoria externa y compactación; no demuestra un ahorro específico para CDAD.
- [Claude Platform: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching): prefijos estables y distinción entre reutilización de entrada y generación de salida.

## Garantías que se conservan

- Spec aprobado y postcondiciones verificables.
- Aislamiento de test-writer e implementer y restricciones de edición por rol.
- Review independiente y política vigente de diversidad de modelos.
- Evidencia real para cerrar gates y trazabilidad de sus artefactos.
- Auditoría independiente del mapeo entre tests y postcondiciones.

Las propuestas son cambios de distribución y ejecución. Cualquier modificación de gates o granularidad debe especificarse y validarse antes de convertirse en política.

## Plan de evaluación

Comparar la versión actual y una variante aligerada sobre tareas equivalentes: cambio pequeño, cambio con varias postcondiciones y caso Odoo con instalación costosa. Mantener comparables modelo, runtime y entorno; repetir lo necesario para distinguir variación de una mejora consistente.

| Dimensión | Métricas |
|---|---|
| Consumo | Tokens de entrada, salida y caché cuando estén disponibles; costo total de todos los agentes. |
| Latencia | Tiempo hasta feature aceptada; separar ejecución de agentes, arranque de roles, tests y espera humana. |
| Trabajo redundante | Relecturas sin cambios, cargas de skills, handoffs, reintentos sin nueva hipótesis. |
| Calidad | Correcciones de review, incumplimientos de rol, gates inválidos, regresiones y defectos conocidos que los controles detectan o dejan pasar. |
| Contexto | Carga inicial real, máximo por sesión, crecimiento por herramientas y frecuencia de checkpoints o compactación. |

Indicador principal: **costo y tiempo por feature aceptada manteniendo calidad y garantías**. No se atribuye todavía ningún porcentaje de ahorro: falta instrumentación de ejecución.

Incluir casos controlados con defectos introducidos deliberadamente para comprobar que la variante conserva capacidad de detección: edición de tests por el implementer, suite vacía con salida exitosa, evidencia obsoleta y test que no verifica su postcondición. Ejecutarlos en un entorno de evaluación aislado. Un piloto pequeño aporta indicios, no una garantía estadística de calidad equivalente.

Las llamadas repetidas son señales para investigar, no prueba automática de agotamiento de contexto. Hay relecturas legítimas tras cambios y ejecuciones repetidas necesarias para investigar no determinismo.

## Plan incremental propuesto

| Iteración | Alcance | Cómo evaluar |
|---|---|---|
| 0 — Línea base | Elegir runtime, perfil/modelos y tareas representativas. Registrar cargas, llamadas, tokens, tiempos y reintentos de todos los roles. | Establecer costo y tiempo por feature aceptada; identificar qué parte corresponde a tests y espera humana. |
| 1 — Instrucciones y continuidad | Corregir contradicciones; separar contratos por rol; eliminar recargas por turno; distinguir ejecución automática/manual. | Mantener gates y modelos comparables; comprobar qué carga recibe cada rol y si disminuyen relecturas/pausas sin perder controles. |
| 2 — Paquetes y evidencia | Aplicar agrupación ortogonal coherente; registrar vigencia de evidencia; separar memoria activa e historial. | Comparar arranques, tamaño máximo de contexto y ejecuciones repetidas, además de calidad. |
| 3 — Operaciones deterministas | Incorporar gradualmente preparación de contexto, validación de estado/evidencia y persistencia exacta de artefactos. | Verificar que disminuye administración realizada por el modelo y que permisos/aprobaciones se conservan. |
| 4 — Modelos y otras variantes | Evaluar modelos menores por rol; después, si corresponde, granularidad acoplada o paralelismo adicional. | Costo total y tiempo hasta aceptación, incluyendo escalamiento, correcciones y fallos; no solo precio por token. |

Descomponer cada iteración en cambios comparables cuando sea necesario para atribuir las mejoras. No introducir simultáneamente cambios de modelo y de procedimiento en el primer piloto.

## Punto de continuación para otro entorno

### Estado de este trabajo

Archivo de destino: `findings/context-token-efficiency-2026-09-16.md`, rama `translation-en`. Esta versión ampliada se entrega como archivo para incorporarla desde otro entorno: el intento de actualización mediante la integración de GitHub fue rechazado con `403 Resource not accessible by integration`, por lo que no se creó un commit. El blob de partida es `985f9768d2445cc475511fe51ea4335089c7ebcb`; si el documento remoto cambió, integrar los cambios en vez de sobrescribirlos. Una vez incorporada esta versión, actualizar esta nota con el resultado.

- El problema informado es exceso de tiempo por feature, tokens y necesidad de contextos grandes; la metodología se considera efectiva para sus objetivos.
- Se completaron dos revisiones estáticas, con las revisiones base registradas arriba.
- Se autorizó documentar las propuestas para retomar la discusión. Eso no constituye aprobación de un spec ni autorización de una transición del ciclo.
- Este cambio actualiza exclusivamente este informe: no modifica agentes, skills operativas, tests, estado CDAD ni política vigente.
- No se ejecutaron benchmarks ni se implementaron las optimizaciones. No hay porcentajes de ahorro demostrados.

### Próxima acción recomendada

Convertir la iteración 1 en un spec acotado, junto con la instrumentación mínima de la iteración 0. Antes de diseñarlo, comprobar si los archivos citados cambiaron desde `eb3a511181c3d76d0306dd149176b90ebe8b617c`; no asumir que todas las contradicciones siguen presentes.

### Decisiones pendientes

1. Runtime y perfil/modelos usados en el piloto; no presuponerlos a partir de los ejemplos.
2. Tareas representativas y disponibilidad de trazas reales, incluyendo un caso con tests costosos.
3. Ubicación y formato de la fuente canónica de políticas y generación de variantes.
4. Esquema del paquete de contexto, resultado del rol, checkpoint y evidencia reutilizable.
5. Regla de invalidación por cambios de archivos, dependencias, configuración y entorno.
6. Umbrales medibles de aceptación de costo/latencia/contexto y controles de calidad.
7. Alcance inicial de las herramientas deterministas; Go es una opción propuesta, no una decisión tomada.
8. Precedencia del presupuesto de properties y justificación de su suficiencia.

### Criterios propuestos para el primer spec

- Un ejecutor recibe su contrato sin cargar instrucciones que le asignen el rol de orquestador.
- Cada política aplicable tiene una fuente identificada y no existen divergencias entre sus proyecciones.
- Las restricciones críticas se conservan tras compactación/reinicio.
- El modo automático continúa ante resultados mecánicos autorizados y el manual espera el handoff; ambos respetan aprobaciones.
- Una sesión nueva puede reconstruir la próxima tarea desde estado y artefactos persistidos.
- Se conserva el aislamiento, la evidencia real de gates y la auditoría independiente.
- Las comparaciones incluyen todos los agentes y el retrabajo. Las metas numéricas se fijan después de obtener la línea base.

Este documento permite retomar el análisis sin acceder a la conversación original. El siguiente paso es definir y aprobar el alcance experimental, no aplicar todas las propuestas como una reforma única.

