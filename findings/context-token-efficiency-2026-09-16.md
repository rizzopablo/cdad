# CDAD: eficiencia de contexto, tokens y ejecución

Fecha: 2026-09-16. Estado: análisis y propuestas para discutir; no es un spec aprobado ni modifica el proceso vigente.

## Objetivo y alcance

Analizar cómo acelerar CDAD y reducir su consumo de contexto y tokens conservando los contratos, el aislamiento de roles y la evidencia de los gates. Este documento permite continuar la discusión desde la web sin depender del historial de una conversación.

Se revisaron secciones relevantes de la metodología, agentes, skills, handoffs, re-entry y el protocolo de presupuesto de tests. Es una revisión estática y dirigida, no una auditoría exhaustiva ni un benchmark de sesiones reales. Los tamaños son bytes medidos en archivos de la revisión base `f2b9611`; no equivalen a tokens ni al contenido que efectivamente inyecta cada runtime.

Privacidad: se omiten identidades de usuarios, rutas absolutas, cuentas, remotos, datos de clientes y detalles del entorno de ejecución. Las referencias internas son relativas al repositorio. Se conservan enlaces a publicaciones públicas como fuentes bibliográficas.

## Opinión principal

CDAD tiene una arquitectura compatible con contextos acotados: roles separados, artefactos persistidos y referencias bajo demanda. Sin embargo, las instrucciones actuales hacen cargar y repetir información que muchos roles no necesitan.

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

### Tensiones entre instrucciones

- **Contexto mínimo frente a skill completa:** la metodología recomienda cargar solo archivos necesarios, pero los ejecutores y handoffs solicitan `cdad-cycle` completo.
- **Lectura bajo demanda frente a acumulación:** leer referencias una por vez evita cargas iniciales excesivas, pero no elimina del historial las referencias ya leídas.
- **Properties genéricas frente a presupuesto Odoo:** [re-entry](../skills/cdad-cycle/references/re-entry.md) pide al menos 100 entradas, mientras el [protocolo Odoo](../skills/odoo-make-env/references/run-budget-protocol.md) propone 8–10 como presupuesto inicial. Se necesita una precedencia explícita y consistente entre política general y especialización.
- **Granularidad frente a costo de arranque:** tareas de un test o postcondición por sesión pueden multiplicar lecturas, handoffs y ejecuciones. La separación entre roles sigue siendo necesaria; la granularidad dentro de un mismo rol admite evaluación.

## Propuestas priorizadas

### 1. Separar instrucciones de orquestación y ejecución

Mantener `cdad-cycle` como entrada breve para detectar estado, elegir procedimiento y validar gates. Cada ejecutor recibe su contrato de rol, subfase y referencias aplicables, sin procedimientos de bootstrap, otros roles o runtimes ajenos.

Conservar visibles las restricciones críticas, como la prohibición de editar tests para el implementer. Mover explicaciones, incidentes históricos y ejemplos extensos a documentación de consulta. Separar las plantillas de handoff por rol/subfase.

Presupuesto experimental inicial: 1–2 mil tokens de instrucciones estables por ejecutor, excluyendo spec, código, herramientas y contexto propio de la tarea. Es una hipótesis para medir, no un óptimo demostrado ni una razón para omitir restricciones necesarias.

### 2. Cargar una vez y recuperar según necesidad

Sustituir la recarga en cada turno por carga al iniciar sesión y recuperación cuando cambie la versión, cambie el objetivo o se pierda contexto relevante. Una caché de archivos leídos no implica que el modelo todavía conserve su contenido: el runtime debe distinguir ambas situaciones.

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

La selección debe respetar permisos de lectura y no filtrar implementación al test-writer. Acotar contexto no justifica ocultar dependencias necesarias para cumplir el contrato.

### 4. Separar memoria activa, conocimiento estable e historial

- `activeContext`: objetivo vigente, bloqueos y próxima acción.
- `systemPatterns`: convenciones vigentes organizadas por tema.
- Historial y decisiones: archivos consultables mediante un índice.

El scribe debería consolidar y reemplazar información obsoleta, además de agregar entradas. Los roles recibirían los temas aplicables, no todo el historial. Un checkpoint debe conservar decisiones, pendientes y referencias a evidencia para permitir una sesión nueva sin reconstrucción extensa.

### 5. Generalizar el presupuesto de ejecuciones

El [run-budget-protocol](../skills/odoo-make-env/references/run-budget-protocol.md) ya aporta una base útil: tests focalizados al diagnosticar, suite completa al cerrar el gate y reutilización de evidencia válida. Extender el patrón a otros stacks y unificar instrucciones contradictorias.

La reutilización exige identidad de código, tests, dependencias, configuración y entorno relevante. Un commit por sí solo no garantiza equivalencia: puede haber cambios sin commit, fixtures externos o variaciones del entorno.

Guardar logs completos como artefactos y devolver al modelo un resumen verificable con comando, resultado, cantidad de tests, revisión y ubicación de la evidencia. Conservar acceso al fallo completo cuando sea necesario para diagnosticar; no comprimir hasta ocultar errores o suites vacías.

### 6. Automatizar comprobaciones mecánicas

Validar con scripts presencia de artefactos, esquema del estado, alcance de archivos modificados y asociación entre evidencia y revisión. Reservar al modelo la interpretación semántica: si los tests verifican el contrato y si el cambio es correcto.

Generar variantes de agentes desde fuentes comunes por rol, stack y runtime reduciría divergencias. El ahorro de mantenimiento es directo; el de tokens solo aparece si el contenido generado y cargado es menor. Preservar permisos específicos y sus verificaciones empíricas.

### 7. Evaluar granularidad y paralelismo

Probar agrupación de postcondiciones relacionadas dentro del mismo rol y subfase, con dependencias explícitas y contexto acotado. Mantener RED y GREEN separados y la auditoría independiente. El objetivo verificable puede abarcar más de un test.

Paralelizar tareas independientes cuando reduzca el camino crítico sin conflictos de archivos o estado. Más agentes pueden bajar la latencia y aumentar simultáneamente los tokens totales. No adoptar paralelismo como sinónimo de eficiencia.

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
| Latencia | Tiempo hasta feature aceptada, arranque de roles y tiempo de tests. |
| Trabajo redundante | Relecturas sin cambios, cargas de skills, handoffs, reintentos sin nueva hipótesis. |
| Calidad | Correcciones de review, incumplimientos de rol, gates inválidos y regresiones detectadas. |
| Contexto | Carga inicial real, crecimiento por herramientas y frecuencia de checkpoints o compactación. |

Indicador principal: **costo y tiempo por feature aceptada manteniendo calidad y garantías**. No se atribuye todavía ningún porcentaje de ahorro: falta instrumentación de ejecución.

Las llamadas repetidas son señales para investigar, no prueba automática de agotamiento de contexto. Hay relecturas legítimas tras cambios y ejecuciones repetidas necesarias para investigar no determinismo.

## Punto de continuación

Primera iteración recomendada:

1. Instrumentar una línea base de cargas, tokens, llamadas y tiempos.
2. Eliminar recargas por turno y separar instrucciones por rol/subfase.
3. Unificar precedencia y presupuesto de tests entre instrucciones generales y Odoo.
4. Comparar resultados y recién después ajustar granularidad, paralelismo o modelos.

Pendientes para convertir el análisis en un spec:

- Elegir runtime y tareas representativas del piloto.
- Definir fuente canónica de contratos y generación de variantes.
- Precisar esquema del handoff y de evidencia reutilizable.
- Establecer presupuestos medibles y criterios de aceptación sin debilitar gates.
- Resolver cómo invalidar contexto y evidencia cuando cambian archivos o entorno.

No se implementaron estas propuestas ni se inició una transición del ciclo CDAD como parte de este análisis.
